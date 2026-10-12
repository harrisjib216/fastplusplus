# md5-wasm (hand-written WebAssembly MD5)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `WebAssembly text format (.wat) with JavaScript wrapper` · `MIT` · 🟢 active

> Promise-based MD5 for Node and browsers with a hand-written WAT core; about 39x faster than md5 npm on 37 MB.

| | |
|---|---|
| **Beats** | md5 npm package (pure JavaScript MD5, 'the most popular md5 utility') |
| **Claimed result** | README: '30x faster than the most popular md5 utility' (md5 npm). Table (Node v10.18.1, Ubuntu): 37 MB 38,500 ms vs 990 ms (0.96 vs 37 MB/s), about 39x (derived from page data); 24 MB 23,600 vs 700 ms; 12 MB 12,400 vs 490 ms; 8 MB 7,600 vs 400 ms; 4 MB 4,000 vs 330 ms; 2 MB 2,000 vs 240 ms; 1 MB 1,000 vs 170 ms; 0.5 MB 520 vs 360 ms; 0.3 MB 390 vs 300 ms; 0.2 MB 260 vs 90 ms |
| **Workload** | MD5 of files from 0.2 MB to 37 MB on a low-powered Ubuntu production server with NodeJS v10.18.1, elapsed ms and MB/s per size |
| **Metric** | throughput |
| **Compiler and flags** | hand-written WAT (four-logics-syntax.wat) assembled to wasm; NodeJS v10.18.1 on Ubuntu; no benchmark script found in the visible file list |
| **Adoption** | 34 stars; npm package md5-wasm |
| **Last commit** | 2026-04-23 |
| **Links** | [repository](https://github.com/briantbutton/md5-wasm) · [benchmark](https://github.com/briantbutton/md5-wasm) |

## Verdict

First-party README table (Node v10.18.1, unnamed low-powered Ubuntu server, single runs, no script): MD5 of a 37 MB file takes 990 ms versus 38,500 ms with the md5 npm package (37 vs 0.96 MB/s, about 39x), falling to 1.3-2.9x on the 0.2-0.5 MB rows, where only JavaScript runs. An independent hash-wasm benchmark (Chrome 131, Ryzen 9 7900X) puts md5-wasm 2.0.0 at 131.77 MB/s versus 21.65 MB/s for md5 2.3.0 at 1 MiB, on its JavaScript fallback.

## Use it when

- MD5 checksums of multi-megabyte buffers (well above 4 MiB) in a browser, where Node's crypto module is not available, e.g. hashing a user-selected video before upload.
- Replacing the md5 npm package in legacy code that hashes large Buffers or Uint8Arrays and can accept a Promise-based call.
- When a single MIT-licensed file with no dependencies and no build step is preferred over a larger hashing library.

## Skip it when

- In Node.js: the built-in crypto.createHash('md5') (native OpenSSL) is the obvious incumbent and was never compared.
- Inputs up to about 4 MiB: no WebAssembly runs (see gotchas), and an independent run at 1 MiB measured md5-wasm's JS path at 131.77 MB/s versus 171.73 MB/s for pure-JS spark-md5 3.0.2 and 850.31 MB/s for hash-wasm 4.10.0 (Chrome 131, Ryzen 9 7900X).
- Streaming or chunked hashing of files larger than memory, or inputs over 255.9 MB: the whole input must be in one buffer and is copied into a fresh wasm memory.
- Latency-sensitive UI or server threads: the hash is computed synchronously on the calling thread despite the Promise API, and each WebAssembly call recompiles the module (about 150 ms on the author's server).
- Code that passes strings or needs a synchronous result (issue #3 asked for synchronous support; none was added).

## How it is fast

The core is a hand-written WebAssembly text module (four-logics-syntax.wat) whose loops() export runs the 64 MD5 steps over 61,440 consecutive 64-byte blocks (3.75 MiB) per call, reading message words straight from linear memory with i32.load and keeping the A-D state in wasm globals, so no JavaScript number conversions happen inside the loop (the README's explanation for the gap). Input bytes are packed into a Uint32Array view of the wasm memory, and whatever the wasm chunks do not cover is finished by a hand-unrolled JavaScript MD5 over that typed array. Much of the advantage over the md5 npm package comes from this better-written JavaScript as well: the rows where no WebAssembly runs are still 1.3-8.3x faster than md5 (derived from page data).

## Compared with alternatives

None of the sibling hashes (superfasthash, sha2-wasm, tape-sha256) computes MD5, so the real choice is against hash-wasm, which is already in this wave's merged records and measured 6.5x faster at 1 MiB, or spark-md5. Pick md5-wasm only for large in-memory buffers where a tiny dependency-free file matters more than peak speed.

## Integration

| | |
|---|---|
| **Form** | source-drop (single JS file with base64-embedded wasm; npm package md5-wasm 2.0.0) |
| **Dependencies** | none |
| **Minimum toolchain** | A JavaScript engine with WebAssembly and Promise (falls back to JavaScript with a console message if WebAssembly is missing); README numbers from Node v10.18.1 |
| **Platforms** | Node.js and browsers (any CPU) |
| **Thread safety** | Each call builds its own closures, WebAssembly.Memory and instance, so concurrent calls are independent (a multiple-simultaneous-calls bug was fixed in May 2020 per the commit log); hashing itself runs synchronously on the calling thread. |
| **Drop-in for the baseline** | no |

## Gotchas

- Unit mismatch behind the README table: md5WASM sends inputs larger than 1,048,576 bytes down the WebAssembly path, but md5WA only calls the wasm loops() while more than 1,048,576 32-bit words (4 MiB) remain, since len and i count words. Inputs from 1 MiB to about 4 MiB therefore compile the module, allocate wasm memory and copy the data, then hash entirely in JavaScript, and on larger inputs the last 0.25-4 MiB is always hashed in JavaScript. The README's 0.2-2 MB rows ran no WebAssembly at all; the same thresholds are in npm 1.0.2, 1.1.0 and the current file.
- 'Non-blocking' describes only the API shape: the JavaScript path hashes inside the Promise executor before md5WASM returns, and the WebAssembly path hashes synchronously in the instantiate callback. Every WebAssembly-path call recompiles the module from bytes and allocates at least 512 wasm pages (32 MiB) of memory, up to 4,096 pages (256 MiB) for the largest inputs.
- The README table is a set of single runs committed 2020-05-02, before the May 2020 WebAssembly optimisation and the v2.0.0 rewrite (Feb 2021). Its small rows are non-monotonic (0.2 MB 90 ms, 0.3 MB 300 ms, 0.5 MB 360 ms, 1 MB 170 ms), which points to cold-JIT noise, and it names no CPU and ships no benchmark script.
- The only independent numbers (hash-wasm README, via hash-wasm-benchmark's md5.worker.js) time md5-wasm at 32 B and exactly 1 MiB, both on its pure-JS path: 6.1x over md5 2.3.0 at 1 MiB (derived from page data), but slower than spark-md5 and 6.5x slower than hash-wasm's compiled-C WebAssembly MD5.

## Known shortcomings

- Weak baseline (the md5 npm package at about 1 MB/s; Node crypto not compared); no CPU or script, Node v10; inputs up to 1,048,576 bytes run the bundled JavaScript fallback, not WASM.
- Enricher: byte/word unit mismatch in the harness: the WASM path is entered above 1,048,576 bytes but the wasm loops() only runs while more than 1,048,576 words (4 MiB) remain, so the README 0.2-2 MB rows ran no WebAssembly (JS vs JS) and the last 0.25-4 MiB of every input is hashed in JS (same thresholds in npm 1.0.2, 1.1.0 and current); 'non-blocking' is false (synchronous, module recompiled each call); the independent hash-wasm benchmark (Chrome 131, Ryzen 9 7900X) shows the JS path at 131.77 MB/s vs md5 21.65 (6.1x) but below spark-md5 171.73 and hash-wasm 850.31. Retiered to D.

## Caveats and trade-offs

First-party table from an unnamed 'slow production server', Node v10.18.1 (2019-era V8), no CPU model and no public benchmark script. The baseline md5 npm package runs at about 1 MB/s and is not a tuned JavaScript MD5; Node's built-in crypto.createHash('md5') (native OpenSSL), the obvious server-side incumbent, is not compared. In the current md5-wasm.js only inputs larger than 1,048,576 bytes (bounder) go to WebAssembly; smaller inputs use the bundled pure-JS MD5, so the 0.2-1 MB rows compare two JavaScript implementations, and the WASM path instantiates a new module on every call (about 150 ms per the README) and finishes the tail in JS. The README itself expected 3-5x and attributes the larger gap to number-format conversions in the md5 package. Code dates from 2020-2021; the 2026-04-23 commit ('Fighting with git') is housekeeping. [retier] Byte/word threshold mismatch means the 0.2-2 MB rows ran no WebAssembly and larger inputs finish in JS; synchronous despite the 'non-blocking' claim; module recompiled per call

Asynchronous (Promise) API only, no synchronous version; about 150 ms WebAssembly instantiation cost on the author's server; takes bytes not strings, so strings must be converted first; wasm is used only above a size threshold.

## Maintenance

The code has been frozen since v2.0.0 (February 2021); later commits only touch the README or are housekeeping (the 2026-04-23 commit is 'Fighting with git'), and there are no tests (the npm test script is a stub). It is MIT-licensed and small enough to vendor, but the speedup is overstated for inputs under about 4 MiB because of the byte/word threshold mismatch.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party README table against the md5 npm package on an unnamed 'slow production server' with Node v10.18.1; no CPU model and no benchmark script in the repo, so C.
- **Retiered** C to D: Enricher (2026-10-12): the measured code never ran the WebAssembly path for the README's 0.2-2 MB rows (the WASM branch is taken above 1,048,576 bytes but the wasm loop only runs while more than 1,048,576 words remain) and hashes the last 0.25-4 MiB of every input in JS, so the published wasm-vs-JS table measures JS against JS; the only independent run (hash-wasm benchmark) shows it below spark-md5 and hash-wasm. No valid measurement of the wasm claim.
- **Verifier notes:** README table and 30x claim verified; derived 39x at 37 MB is correct. Metadata confirmed: MIT (LICENSE.md, package.json), 34 stars, 3 forks, 25 commits, last commit 2026-04-23, so active by the 12-month rule although the code is essentially from 2021. Main shortcomings for the record: weak baseline (slow md5 npm, Node crypto not compared), no hardware or script, small-file rows run the JS fallback.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-118 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/briantbutton/md5-wasm/HEAD/README.md>
  - <https://github.com/briantbutton/md5-wasm>
  - <https://github.com/briantbutton/md5-wasm/commits>
  - <https://raw.githubusercontent.com/briantbutton/md5-wasm/HEAD/md5-wasm.js>
  - <https://raw.githubusercontent.com/briantbutton/md5-wasm/HEAD/package.json>
  - <https://github.com/briantbutton/md5-wasm/issues?q=is%3Aissue>
  - <https://github.com/briantbutton/md5-wasm/issues/1>
- **Sources the enricher read:**
  - <https://github.com/briantbutton/md5-wasm/commits>
  - <https://github.com/briantbutton/md5-wasm/issues?q=is%3Aissue>
  - <https://github.com/briantbutton/md5-wasm/issues/1>
  - <https://raw.githubusercontent.com/briantbutton/md5-wasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/briantbutton/md5-wasm/HEAD/md5-wasm.js>
  - <https://raw.githubusercontent.com/briantbutton/md5-wasm/HEAD/package.json>
  - <https://raw.githubusercontent.com/briantbutton/md5-wasm/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/briantbutton/md5-wasm/HEAD/four-logics-syntax.wat>
  - <https://registry.npmjs.org/md5-wasm>
  - <https://registry.npmjs.org/md5-wasm/-/md5-wasm-1.0.2.tgz>
  - <https://registry.npmjs.org/md5-wasm/-/md5-wasm-1.1.0.tgz>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/HEAD/README.md>
  - <https://github.com/Daninet/hash-wasm-benchmark>
  - <https://github.com/Daninet/hash-wasm-benchmark/tree/master/src>
  - <https://github.com/Daninet/hash-wasm-benchmark/tree/master/src/benchmark>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm-benchmark/HEAD/src/benchmark/md5.worker.js>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm-benchmark/HEAD/src/benchmark/bench.js>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/briantbutton/md5-wasm`) · [data/wave13/enrich/raw/github_com_briantbutton_md5_wasm.json](../../../data/wave13/enrich/raw/github_com_briantbutton_md5_wasm.json) (enrichment confidence 0.8)

</details>
