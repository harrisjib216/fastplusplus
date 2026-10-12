# superfasthash (SuperFastHash in JavaScript and AssemblyScript WebAssembly)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `AssemblyScript` · `ISC` · 🔴 abandoned

> Paul Hsieh's SuperFastHash as a tiny npm module in JS and AssemblyScript Wasm; Wasm about 1.2x the JS port on Node.

| | |
|---|---|
| **Beats** | JavaScript implementation of SuperFastHash in the same module (and Node.js native crypto MD5, SHA-1, SHA-256, RIPEMD-160) |
| **Claimed result** | SuperFastHash (wasm) 369.101 ms vs SuperFastHash (js) 447.736 ms per 1,000,000 hashes (about 1.21x, derived from page data); native Node crypto: MD5 4437.191 ms, SHA-1 4436.841 ms, SHA-256 5154.750 ms, RIPEMD-160 6644.826 ms. |
| **Workload** | 1,000,000 random messages of 1-1000 bytes (crypto.randomBytes) generated once and hashed once each per implementation by benchmarks/benchmark.js (console.time around Array.forEach, one pass, no warm-up); the README shows the output only as a macOS terminal screenshot (benchmark.png). |
| **Metric** | throughput |
| **Compiler and flags** | AssemblyScript compiler (asc from the GitHub master branch, 2019) with -O3 --validate via buildwasm.js; Node.js version not stated (package.json engines: node &gt;=10.10.0) |
| **Adoption** | 19 stars |
| **Last commit** | 2019-04-06 |
| **Links** | [repository](https://github.com/mjethani/superfasthash) · [benchmark](https://github.com/mjethani/superfasthash) |

## Verdict

One first-party run on an unnamed Mac (Node and V8 versions not stated; the author used Node v10.10.0 in issue #1 a week earlier) hashed 1,000,000 random 1-1000 byte messages once each: the AssemblyScript Wasm build took 369.1 ms against 447.7 ms for the module's own JS port (about 1.21x, derived from page data), including the per-message copy into Wasm memory. Other published runs of the same benchmark range from Wasm 1.1x slower (pre-optimisation build) to 1.51x faster, so the gain is real but small and run-dependent.

## Use it when

- You need SuperFastHash values inside a JS/Node codebase (for example to bucket or dedupe byte strings) and want a dependency-free, ISC-licensed file you can vendor.
- Long-running processes that hash many small-to-medium messages (hundreds of bytes), where V8 has tiered up and the Wasm path's roughly 1.1-1.5x edge over the JS port is worth an async init.
- Environments without Wasm: the pure-JS hash() has the same API and output, so you can fall back to it.

## Skip it when

- When you need hashes that match C/C++ SuperFastHash (Hsieh's hash.c, Chromium's base/third_party copy): both ports read the tail bytes as unsigned where the reference casts them to signed char, so about a quarter of random binary inputs hash differently (see gotchas).
- Messages larger than 64 KiB on the Wasm path with default options: the module exports a 0-page memory that initialize() grows by one page, so wasmMemory.set() throws a RangeError unless you call initialize({ memory: N }) with enough 64 KiB pages.
- Anything adversarial or security-relevant: it is a weak 32-bit non-cryptographic hash, and the repo's own tests assert collisions ('s11000' vs 's10018', 's99999' vs 's98981').
- If you want a maintained, faster Wasm hash: the project has 9 commits, the last on 2019-04-06, it is not published on npm (the registry returns 404 for 'superfasthash'; install is from GitHub), and the build depends on AssemblyScript's 2019 master branch.

## How it is fast

The Wasm build copies the message into linear memory at offset 0 (Uint8ClampedArray.set) and runs the hash loop as native i32 arithmetic with one 4-byte i32.load per round. The JS port instead reads bytes one at a time and coerces every intermediate with &gt;&gt;&gt; 0. The algorithm is SuperFastHash (16-bit add/shift/xor rounds plus a final avalanche); there is no SIMD and no batching. Each call still pays a JS-to-Wasm transition and a memcpy, so the gain is small.

## Compared with alternatives

Pick it only when you specifically need SuperFastHash in JS and accept its unsigned-tail deviation; for a general fast non-cryptographic hash in JS, the catalogued hash-wasm (XXHash64 about 16 GB/s vs xxhashjs) and xxhash-wasm entries are faster, maintained and published on npm. Among small AssemblyScript ports in this category it is similar in scale to xoroshiro128starstar (about 1.10x over Math.random): a modest, single-run gain.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime (prebuilt dist/wasm/superfasthash.js embeds the Wasm bytes); rebuilding needs assemblyscript from GitHub master and uglify-js |
| **Minimum toolchain** | Node.js &gt;= 10.10.0 (package.json engines); WebAssembly support for the wasm entry point |
| **Platforms** | any JS engine with WebAssembly (Node, browsers); pure-JS fallback everywhere |
| **Thread safety** | not documented; the Wasm build keeps one module-level memory buffer and writes each message to offset 0, so each instance is single-threaded by construction (per JS realm) |
| **Drop-in for the baseline** | partial — same hash(message) signature and output as the module's JS version, but the Wasm entry point needs an awaited initialize() first, and the input must be a typed array or array of byte values |

## Gotchas

- Output differs from Paul Hsieh's reference C code: the reference (and Chromium's copy) does `hash += (signed char)*data` for a 1-byte tail and `(signed char)data[2] << 18` for a 3-byte tail, while both the JS and the AssemblyScript ports use the unsigned byte. A Python re-implementation of both, checked against the repo's ASCII test vectors, found 24.5% of 20,000 random 1-1000 byte messages hash differently from the reference (single byte 0xFF: reference 0, port -1444309403). The repo's fixed vectors are all ASCII, so its tests cannot catch this; JS and Wasm agree with each other.
- The Wasm memory is 64 KiB by default (exported memory starts at 0 pages, initialize() grows it by options.memory = 1), so a longer message throws RangeError from wasmMemory.set; pass initialize({ memory: pages }) up front.
- Benchmark harness (benchmarks/benchmark.js): one console.time pass per implementation over the same 1,000,000 crypto.randomBytes messages (about 500 MB in total), with no warm-up or repetition and the JS pass first. Issue #1 shows how much this moves the ratio: an earlier build measured JS 619 ms vs Wasm 683 ms (Wasm slower), the author later measured 440 vs 387 ms, the README screenshot shows 447.7 vs 369.1 ms (1.21x), and MaxGraey's PR #2 run shows 510.6 vs 338.3 ms (1.51x, derived from page data). At 1-1,000 hashes the author's table is dominated by JS warm-up (0.366 ms vs 0.080 ms for one hash).
- The 'native' MD5/SHA-1/SHA-256/RIPEMD-160 rows call crypto.Hash(algo).update(msg).digest() per message, so they measure Node's per-object binding overhead plus a cryptographic hash, not a like-for-like baseline; the 10-12x gap over SuperFastHash says little about either.

## Known shortcomings

- Small gain (about 1.21x, derived from page data) from a single unwarmed run in which JavaScript is timed first, so JIT warm-up favours the Wasm side; no CPU or Node version.
- The 1.21x is one unwarmed run with the JS pass first; other published runs of the same benchmark range from Wasm 1.1x slower (issue #1) to 1.51x faster (PR #2). Both ports read tail bytes unsigned where Hsieh's and Chromium's reference casts to signed char, so 24.5% of random messages hash differently from the C reference (Python model; the ASCII-only test vectors miss it). Default Wasm memory is 64 KiB, so larger messages throw RangeError. Not on npm (registry 404).

## Caveats and trade-offs

Numbers exist only in a terminal screenshot in the repo; no CPU, Node version or V8 version stated. Single run per implementation with no warm-up: the JS implementation runs first in the same process, so its timed pass includes JIT tier-up, which favours the Wasm pass that runs second. Wasm timings include copying every message into Wasm linear memory (wasmMemory.set) and the JS-to-Wasm call, so the \~1.21x gain is end-to-end but small enough that run order could account for part of it. The native crypto rows (MD5, SHA-1, SHA-256, RIPEMD-160) build a Hash object per message and are cryptographic hashes, so they are not like for like. Last commit 2019-04-06.

Non-cryptographic hash only; Wasm path needs an async initialize() call.

## Maintenance

Abandoned since 2019-04-06 (9 commits, 19 stars, never published to npm), but ISC-licensed and only about 60 lines per implementation, so it is easy to vendor; fix the tail bytes to signed char first if you need reference-compatible hashes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party benchmark code is public (benchmarks/benchmark.js, run via npm run benchmark) and the README screenshot (benchmark.png, refreshed in the last commit on 2019-04-06) shows SuperFastHash (js) 447.736 ms vs (wasm) 369.101 ms per 1,000,000 hashes, but no CPU model, Node version or V8 version is given, so it cannot reach A.
- **Verifier notes:** Numbers match the screenshot exactly; ISC licence, 19 stars, 9 commits, last commit 2019-04-06 (abandoned) all confirmed. Main shortcomings: tiny \~1.21x margin (derived from page data) from a single unwarmed run with JS first, and no hardware or runtime version. The 'listed as unmaintained on awesome-assemblyscript' caveat was not checked (that list's raw README did not resolve).
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-55 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/mjethani/superfasthash>
  - <https://github.com/mjethani/superfasthash/commits>
  - <https://github.com/mjethani/superfasthash/commits/master/benchmark.png>
  - <https://raw.githubusercontent.com/mjethani/superfasthash/HEAD/README.md>
  - <https://raw.githubusercontent.com/mjethani/superfasthash/HEAD/benchmark.png>
  - <https://raw.githubusercontent.com/mjethani/superfasthash/HEAD/benchmarks/benchmark.js>
  - <https://raw.githubusercontent.com/mjethani/superfasthash/HEAD/buildwasm.js>
  - <https://raw.githubusercontent.com/mjethani/superfasthash/HEAD/wasm.js>
  - <https://raw.githubusercontent.com/mjethani/superfasthash/HEAD/package.json>
  - <https://raw.githubusercontent.com/mjethani/superfasthash/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/mjethani/superfasthash>
  - <https://github.com/mjethani/superfasthash/commits>
  - <https://github.com/mjethani/superfasthash/issues?q=is%3Aissue>
  - <https://github.com/mjethani/superfasthash/issues/1>
  - <https://github.com/mjethani/superfasthash/pull/2>
  - <https://raw.githubusercontent.com/mjethani/superfasthash/HEAD/README.md>
  - <https://raw.githubusercontent.com/mjethani/superfasthash/HEAD/benchmark.png>
  - <https://raw.githubusercontent.com/mjethani/superfasthash/HEAD/benchmarks/benchmark.js>
  - <https://raw.githubusercontent.com/mjethani/superfasthash/HEAD/buildwasm.js>
  - <https://raw.githubusercontent.com/mjethani/superfasthash/HEAD/wasm.js>
  - <https://raw.githubusercontent.com/mjethani/superfasthash/HEAD/index.js>
  - <https://raw.githubusercontent.com/mjethani/superfasthash/HEAD/package.json>
  - <https://raw.githubusercontent.com/mjethani/superfasthash/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/mjethani/superfasthash/HEAD/.gitignore>
  - <https://raw.githubusercontent.com/mjethani/superfasthash/HEAD/src/js/superfasthash.js>
  - <https://raw.githubusercontent.com/mjethani/superfasthash/HEAD/src/wasm/superfasthash.ts>
  - <https://raw.githubusercontent.com/mjethani/superfasthash/HEAD/src/wasm/tsconfig.json>
  - <https://raw.githubusercontent.com/mjethani/superfasthash/HEAD/dist/wasm/superfasthash.wat>
  - <https://raw.githubusercontent.com/mjethani/superfasthash/HEAD/dist/wasm/superfasthash.js>
  - <https://raw.githubusercontent.com/mjethani/superfasthash/HEAD/tests/superfasthash.js>
  - <https://raw.githubusercontent.com/chromium/chromium/main/base/third_party/superfasthash/superfasthash.c>
  - <https://registry.npmjs.org/superfasthash>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/mjethani/superfasthash`) · [data/wave13/enrich/raw/github_com_mjethani_superfasthash.json](../../../data/wave13/enrich/raw/github_com_mjethani_superfasthash.json) (enrichment confidence 0.7)

</details>
