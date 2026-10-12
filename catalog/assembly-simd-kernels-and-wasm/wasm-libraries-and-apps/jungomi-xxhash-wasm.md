# xxhash-wasm

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `WebAssembly with JavaScript wrapper (implementation of xxHash 32-bit and 64-bit)` · `MIT` · 🟡 stale

> Hand-written WebAssembly XXH32/XXH64 for browsers and Node, tens to hundreds of times faster than pure-JS xxhashjs.

| | |
|---|---|
| **Beats** | xxhashjs (pure JavaScript xxHash, uses cuint for 64-bit math); also Node built-in crypto md5 and sha1 (different, cryptographic algorithms) |
| **Claimed result** | Third-party (haya32x64 docs/benchmarks.md, snapshot 2026-08-09, xxhash-wasm 1.1.0 vs xxhashjs 0.2.2, public API, medians of nine 150 ms samples): XXH64 one-shot 4-byte input 39.4 ns vs 1939.3 ns on C8a (AMD EPYC 9R45), about 49x (derived from page data), and 63.9 vs 2691.0 ns on C8g (Neoverse V2), about 42x (derived). 1 MiB bulk 15,973 vs 37 MB/s (about 432x, derived) on C8a and 10,738 vs 28 MB/s (about 384x, derived) on C8g. 8-char strings 59.2 vs 2437.8 ns (about 41x, derived). First-party README (Benchmark.js ops/sec): the prose says the 32-bit hash is up to 90x and the 64-bit up to 350x faster than xxhashjs. The table itself shows 32-bit from 11.2x at 1 byte (5,752,446 vs 513,517 ops/sec) up to 140.7x at 1,000,000 bytes, and 64-bit from 373x at 1 byte (4,438,501 vs 11,896 ops/sec) up to 677.8x at 100,000 bytes. At 100,000,000 bytes 64-bit is 34.56 vs 0.13 ops/sec (265.8x). All README ratios are derived from page data. |
| **Workload** | XXH64/XXH32 hashing via the public JS API. Third-party: byte-array one-shot (4 B, 8 B), 1 MiB bulk, streaming 1 MiB in 64 B-64 KiB chunks, and ASCII strings (8, 32 chars). First-party README: Benchmark.js ops/sec on random ASCII strings from 1 byte to 100,000,000 bytes, plus Node crypto md5/sha1 for comparison. |
| **Metric** | throughput |
| **Hardware** | Third-party: AWS EC2 c8a.2xlarge (AMD EPYC 9R45) and c8g.2xlarge (Arm Neoverse V2), Ubuntu 26.04, timed work pinned to CPU 2. First-party README: an x64 MacBook Pro (CPU model not stated) running Node 17.3; the xxhash-wasm 64-bit column is identical in the xxhashjs and Node-crypto tables, so both appear to come from the same run (inference). |
| **Compiler and flags** | Hand-written src/xxhash.wat built with wasm-opt --enable-bulk-memory -O4 (package.json build-wasm script; npm 1.1.0 artifact). Third-party run under Node.js 24.18.0 / V8 13.6.233.17-node.50 via node --expose-gc js.mjs (haya32x64 bench/, calibration plus warmup, then nine 150 ms samples, median). The first-party README table comes from bench/index.js (Benchmark.js, node --max-old-space-size=4096 index.js), with Node 17.3 stated for the Node-crypto table. |
| **Adoption** | 184 stars |
| **Last commit** | 2024-11-19 |
| **Links** | [repository](https://github.com/jungomi/xxhash-wasm) · [benchmark](https://github.com/thevilledev/haya32x64/blob/main/docs/benchmarks.md) |

## Verdict

The third-party thevilledev/haya32x64 harness (Node 24.18.0, V8 13.6, public APIs, median of nine 150 ms samples, EC2 c8a.2xlarge AMD EPYC 9R45 and c8g.2xlarge Neoverse V2, pinned to one CPU) timed xxhash-wasm 1.1.0 XXH64 against xxhashjs 0.2.2. One-shot 4-byte keys took 39.4 vs 1,939.3 ns (about 49x) on EPYC and 63.9 vs 2,691.0 ns on Neoverse; 1 MiB throughput was 15,973 vs 37 MB/s and 10,738 vs 28 MB/s; 8-character strings took 59.2 vs 2,437.8 ns (ratios derived from page data). The first-party Benchmark.js table (x64 MacBook Pro, Node 17.3, CPU not stated) shows the same order of magnitude, with no native-C baseline in either harness.

## Use it when

- You need a fast non-cryptographic 32- or 64-bit hash (cache keys, content fingerprints, dedup, ETags) in a browser, Node, Deno or Cloudflare Workers, and you control both producer and consumer of the hash.
- You must stay compatible with existing XXH32/XXH64 digests produced by native xxHash, for example matching hashes computed server-side in C, Go or Rust.
- You are replacing xxhashjs: one-shot 4-byte XXH64 drops from about 1.9 us to about 40 ns, and 1 MiB inputs run near 11-16 GB/s instead of 28-37 MB/s in the third-party harness.
- Bundle size matters: about 2.3 kB gzipped with the wasm embedded, against 10.3 kB for xxhashjs.
- You hash large inputs incrementally (file uploads, streams) with 4 KiB or larger chunks through `create64().update()`.

## Skip it when

- You need XXH3 or XXH128, the variants native xxHash recommends for speed: they are not implemented (issue #29, open since January 2022), whereas hash-wasm ships both.
- Your engine lacks BigInt-in-wasm, bulk memory or TextEncoder.encodeInto: Chrome before 85, Firefox before 79, Safari before 15, Node before 15, and some embedded WebViews (issue #34: 'references are not enabled' in an Excel-for-Mac WKWebView). The maintainer's advice is to pin 0.4.2, which is 3-4x slower.
- Your keys are tiny and per-call latency is critical: in the haya32x64 harness the pure-JS haya32x64 hashes 4-byte keys in 22.9 ns versus 39.4 ns, and hash-wasm's own Chrome benchmark puts hash-wasm about 2.1x ahead at 32 bytes (derived from page data).
- You stream in very small chunks: each `update` copies the state blob in and out of wasm memory, so 64-byte chunks reach only 1,130 MB/s on EPYC 9R45 versus 16,863 MB/s with 64 KiB chunks.
- You need a cryptographic or keyed hash: xxHash offers no collision resistance against adversarial input.

## How it is fast

The kernel is a hand-written WAT module (src/xxhash.wat, optimised with binaryen `wasm-opt -O4`) that uses native wasm `i64.mul`/`i64.rotl` for the four-lane xxHash stripe loop, where xxhashjs emulates 64-bit arithmetic with cuint objects. Strings are UTF-8 encoded straight into wasm linear memory with `TextEncoder.encodeInto`, and the 64-bit seed and result cross the JS/wasm boundary as BigInt through the wasm BigInt integration, so no hi/lo splitting or extra copies happen. The streaming state lives in a small JS-held blob that is copied into linear memory around each wasm call, and bulk-memory `memory.copy` handles the partial-stripe buffer. There is no SIMD.

## Compared with alternatives

Against hash-wasm (the only catalogued sibling hashing xxHash): pick xxhash-wasm when you want only XXH32/XXH64 with synchronous calls returning numbers/BigInt and the smallest bundle. Pick hash-wasm when you need XXH3/XXH128 or other algorithms, or the fastest small-input XXH64: its README shows 101.66 vs 47.58 MB/s at 32 bytes and a tie at 1 MB (Chrome v131, Ryzen 9 7900X).

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (the wasm binary is embedded in the ESM, CJS and UMD bundles; a separate .wasm file is used for the workerd build) |
| **Minimum toolchain** | Chrome 85, Edge 79, Firefox 79, Safari 15, Node 15 (needs BigInt-in-wasm, bulk memory and TextEncoder.encodeInto); rebuilding needs binaryen wasm-opt and rollup |
| **Platforms** | any JavaScript engine meeting those features; browsers, Node (ESM or CommonJS), Cloudflare Workers through the 'workerd' export condition |
| **Thread safety** | Each `await xxhash()` creates its own wasm instance; JavaScript runs one thread per realm, so use one instance per Worker. Streaming hashers on one instance save and restore their state around every call (src/xxhash.js), so interleaving several streams is safe. |
| **Drop-in for the baseline** | partial: same XXH32/XXH64 outputs as xxhashjs, but a different API (async instantiation, then synchronous calls returning number/BigInt instead of cuint objects; 64-bit seed is one BigInt, not two 32-bit halves) |

## Gotchas

- Wasm linear memory only grows: one-shot APIs copy the whole input into it (strings reserve 3x their length for encodeInto; Raw APIs `memory.set` the Uint8Array, with no zero-copy offset/length variant, issue #40), and the instance keeps that memory for its lifetime. Hashing one 100 M-character string leaves about 300 MB attached to the instance, so use streaming or a short-lived instance for large inputs.
- The 64-bit APIs take and return BigInt: `h64(str, 0)` with a Number seed throws a TypeError, and results need `.toString(16).padStart(16, '0')` or `h64ToString` for hex output. The README says the string conversion can cost up to 20% on small inputs.
- First-party harness flaw (minor): bench/index.js runs `.toString(16)` on every xxhashjs result but returns raw numbers/BigInt for xxhash-wasm, adding work to the baseline at small sizes; the README prose ('up to 90x/350x') also understates its own table (up to about 141x/678x, derived from page data). The third-party haya32x64 harness consumes both digests without string conversion, and its numbers stand.
- Multi-chunk streaming is barely tested: the known-answer vectors (inputs up to 74 bytes plus one 65,537-byte string) go through a single `update`, and the only split-input tests hash 'helloworld' (10 bytes), below one 16/32-byte stripe. So the buffered path that carries partial stripes across `update` calls has no known-answer test in the repo, and the haya32x64 benchmark does not check digests.

## Known shortcomings

- Raised C to A on the third-party haya32x64 harness (bench/js.mjs, Node 24.18.0/V8 13.6, EPYC 9R45 and Neoverse V2): 4 B 39.4 vs 1939.3 ns (about 49x derived), 1 MiB 15,973 vs 37 MB/s (about 432x derived) against xxhashjs, whose cuint emulation makes it a weak baseline; the first-party bench gives xxhashjs extra .toString(16) work; hash-wasm is faster at 32 B (2.1x derived). Filed under wasm-libraries-and-apps.
- The third-party haya32x64 harness is sound (digests consumed), so the numbers stand; the first-party bench/index.js runs .toString(16) only on xxhashjs results and the README prose understates its own table. Limits: XXH32 and XXH64 only, no XXH3 or XXH128 (issue #29 open); wasm memory never shrinks (strings reserve 3x their length); hash-wasm is 2.1x faster at 32 bytes; multi-update streaming has no known-answer tests.

## Caveats and trade-offs

The baseline xxhashjs is a slow pure-JS port that emulates 64-bit math with cuint, not a tuned JS hash. The Node crypto comparison uses cryptographic md5/sha1. There is no native xxHash C baseline. The README prose (up to 90x/350x) understates its own table (up to \~141x/\~678x, derived). In the first-party bench/index.js the xxhashjs calls also run .toString(16) on each result while xxhash-wasm returns raw numbers/BigInt, so the baseline does extra work (small at large inputs). Not the fastest wasm xxHash: hash-wasm 4.10.0's README shows XXHash64 at 101.66 MB/s vs xxhash-wasm 1.0.2's 47.58 MB/s at 32 bytes (2.1x, derived), with a tie at 1 MB (15,989 vs 15,929 MB/s). In haya32x64's harness, pure-JS haya32x64 (a different hash) beats xxhash-wasm XXH64 on 4-byte keys (22.9 vs 39.4 ns), and cyrb53 (53-bit) is faster still. The third-party measurer is a competing hash author's new repo (a wave-7 catalog entry), with one instance per host type. WebAssembly instantiation (\~1-2 ms) is excluded. Needs BigInt-in-wasm, bulk memory and TextEncoder.encodeInto (Chrome 85+, Safari 15+, Node 15+).

Needs BigInt in WASM, bulk memory and TextEncoder.encodeInto (Chrome &gt;= 85, Firefox &gt;= 79, Safari &gt;= 15, Node &gt;= 15); older xxhash-wasm 0.4.2 is 3-4x slower. WASM instantiation takes about 1 ms in the browser and a little over 2 ms in Node. Small bundle (11.4 kB minified, 2.3 kB gzipped) versus xxhashjs 41.5 kB.

## Maintenance

Stale since v1.1.0 (2024-11-19; the maintainer closed most open issues that day and declined a native-baseline benchmark), but MIT-licensed, dependency-free, about 2 kB, and implementing a frozen algorithm, so it is safe to vendor; no correctness bug was found behind the measured numbers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C. A third-party harness (thevilledev/haya32x64 bench/js.mjs, run as node --expose-gc js.mjs, with xxhash-wasm 1.1.0 and xxhashjs 0.2.2 pinned in bench/package.json) times xxhash-wasm XXH64 against xxhashjs XXH64. docs/benchmarks.md and the raw bench/results JSON state Node.js 24.18.0 / V8 13.6.233.17 and AMD EPYC 9R45 / Arm Neoverse V2 CPUs. The first-party README table (bench/index.js, Benchmark.js) alone would be C, since it gives no CPU model.
- **Verifier notes:** README numbers match the record exactly, but its prose ratios understate the table, and the first-party harness gives xxhashjs extra .toString(16) work. Tier upgraded C to A on the third-party haya32x64 harness, following the libspng-via-wuffs precedent. Metadata confirmed: MIT, 184 stars, 21 forks, not a fork, last commit 2024-11-19 (v1.1.0), stale. Category fit: a hand-written WAT library compared with the JS equivalent fits wasm-libraries-and-apps better than assemblyscript-and-wasm-langs; consider a category override. hash-wasm (already in wave 13 merged) is faster at small inputs.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-06 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/jungomi/xxhash-wasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/jungomi/xxhash-wasm/HEAD/package.json>
  - <https://raw.githubusercontent.com/jungomi/xxhash-wasm/HEAD/bench/index.js>
  - <https://raw.githubusercontent.com/jungomi/xxhash-wasm/HEAD/bench/package.json>
  - <https://raw.githubusercontent.com/jungomi/xxhash-wasm/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/jungomi/xxhash-wasm/v0.4.2/README.md>
  - <https://github.com/jungomi/xxhash-wasm>
  - <https://github.com/jungomi/xxhash-wasm/commits>
  - <https://github.com/jungomi/xxhash-wasm/tree/main/bench>
  - <https://raw.githubusercontent.com/thevilledev/haya32x64/main/docs/benchmarks.md>
  - <https://raw.githubusercontent.com/thevilledev/haya32x64/main/bench/js.mjs>
  - <https://raw.githubusercontent.com/thevilledev/haya32x64/main/bench/package.json>
  - <https://raw.githubusercontent.com/thevilledev/haya32x64/main/bench/results/c8a-node24-v2.json>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/jungomi/xxhash-wasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/jungomi/xxhash-wasm/HEAD/package.json>
  - <https://raw.githubusercontent.com/jungomi/xxhash-wasm/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/jungomi/xxhash-wasm/HEAD/src/index.js>
  - <https://raw.githubusercontent.com/jungomi/xxhash-wasm/HEAD/src/xxhash.js>
  - <https://raw.githubusercontent.com/jungomi/xxhash-wasm/HEAD/src/xxhash.wat>
  - <https://raw.githubusercontent.com/jungomi/xxhash-wasm/HEAD/src/index.workerd.js>
  - <https://raw.githubusercontent.com/jungomi/xxhash-wasm/HEAD/rollup.config.js>
  - <https://raw.githubusercontent.com/jungomi/xxhash-wasm/HEAD/types.d.ts>
  - <https://raw.githubusercontent.com/jungomi/xxhash-wasm/HEAD/test/index.test.js>
  - <https://raw.githubusercontent.com/jungomi/xxhash-wasm/HEAD/bench/index.js>
  - <https://raw.githubusercontent.com/jungomi/xxhash-wasm/HEAD/bench/package.json>
  - <https://github.com/jungomi/xxhash-wasm/issues?q=is%3Aissue>
  - <https://github.com/jungomi/xxhash-wasm/issues/27>
  - <https://github.com/jungomi/xxhash-wasm/issues/30>
  - <https://github.com/jungomi/xxhash-wasm/issues/31>
  - <https://github.com/jungomi/xxhash-wasm/issues/34>
  - <https://github.com/jungomi/xxhash-wasm/issues/40>
  - <https://registry.npmjs.org/xxhash-wasm/latest>
  - <https://raw.githubusercontent.com/thevilledev/haya32x64/main/docs/benchmarks.md>
  - <https://raw.githubusercontent.com/thevilledev/haya32x64/main/bench/js.mjs>
  - <https://raw.githubusercontent.com/thevilledev/haya32x64/main/bench/package.json>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/HEAD/README.md>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/jungomi/xxhash-wasm`) · [data/wave13/enrich/raw/github_com_jungomi_xxhash_wasm.json](../../../data/wave13/enrich/raw/github_com_jungomi_xxhash_wasm.json) (enrichment confidence 0.8)

</details>
