# fast-base64 (mitschabaude)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Encoding (base64, hex, CRC)](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `JavaScript/WebAssembly` · `MIT` · 🔴 abandoned

> Hand-written WebAssembly SIMD base64 codec for JS (browser/Node/Deno); beats pure-JS base64 loops, not native Buffer.

| | |
|---|---|
| **Beats** | The package's own pure-JS port (fast-base64/js), which the README says is 'the fastest existing JS implementation', plus native atob()/btoa() through its own fast-base64/nano wrapper |
| **Claimed result** | "\~20x faster than the fastest JS implementation on the first 100kB of input" and "\~2-3x faster than the fastest JS on the first 100MB" (the 'fastest JS' being the package's own fast-base64/js). The README also lists relative slowdowns against the default Wasm+SIMD build: fast-base64/js is '2-30x slower' and the atob/btoa-based fast-base64/nano is '3-100x slower'. Its one absolute example is 10kB of base64 decoding in 0.06ms with fast-base64 vs 5ms with nano on the author's laptop. |
| **Workload** | Converting between base64 strings and Uint8Array of 100kB to 100MB, in-browser and in Node/Deno, hand-written WASM with SIMD |
| **Metric** | throughput |
| **Adoption** | 58 stars; npm fast-base64 had 6,003 downloads in the week of 2026-09-19 to 2026-09-25 (latest version 0.1.8) |
| **Last commit** | 2022-01-04 |
| **Links** | [repository](https://github.com/mitschabaude/fast-base64) · [benchmark](https://github.com/mitschabaude/fast-base64#readme) |

## Verdict

The README claims about 20x over its own pure-JS port on the first 100 kB and 2-3x on the first 100 MB, plus 0.06 ms vs 5 ms to decode 10 kB against the atob wrapper. It gives no hardware, runtime version or results table, and its harness times one cold call per variant with performance.now(). In our warm-loop re-run on Node 24.18 / Apple M1 Pro (100 kB-10 MB), the Wasm build beat the JS port by about 2.1x on decode (0.74-0.77 vs 0.35-0.37 GB/s) and 3.7-4.6x on encode (1.4-2.3 vs 0.38-0.52 GB/s), not 20x, and Node's Buffer beat both.

## Use it when

- Browser code that encodes or decodes 100 kB-100 MB base64 payloads on engines without native Uint8Array.fromBase64/toBase64, where the fallback would be atob/btoa plus char-code loops.
- Trusted, well-formed standard-alphabet base64 with no line breaks, such as data your own code produced, because the fast path does no validation.
- Cross-runtime ESM code (browser plus Deno) that wants one small API without depending on Node's Buffer.
- Bundle-size-sensitive pages: the default build is about 1.9 kB minzipped, and `/js` is about 600 bytes if you need a synchronous API.

## Skip it when

- Node.js. In our warm-loop run on Node 24.18 (Apple M1 Pro), Buffer.from(s, 'base64') decoded about 10x faster than the default Wasm build (7.4 vs 0.76 GB/s of output at 1 MB), and Buffer#toString('base64') encoded 2.5-7x faster.
- Runtimes with native Uint8Array.fromBase64/toBase64 (MDN: Baseline since September 2025). The native API also validates input, skips whitespace and supports base64url.
- Untrusted input. Invalid characters silently decode to garbage (issue #4, confirmed by the author): '@@@@' gave [16,65,4] with no error, and 'SGVs\nbG8=' gave 'Hel9±¼' instead of 'Hello'.
- Small payloads, or hot paths that need a synchronous call. The fast build is async-only, and the README itself says typical apps will not notice the gap versus the 147-byte atob wrapper.
- Projects that need a maintained dependency. The last commit and npm release (0.1.8) are from 2022-01-04, and the 2023-2024 issues on validation, ESM typings and maintenance are unanswered.

## How it is fast

The kernels are hand-written WebAssembly text using 128-bit Wasm SIMD. Each iteration loads 16 base64 characters and maps them to 6-bit values with a branchless piecewise-linear formula (lane compares turned into add/subtract masks, no lookup table). It packs the bits with i32x4 shifts and masks and uses i8x16.swizzle to compact 16 chars into 12 bytes; encoding runs the same steps in reverse. String/byte conversion goes through TextEncoder.encodeInto/TextDecoder, a cached compiled module plus one shared WebAssembly.Memory avoid re-instantiating per call, and it skips input validation entirely.

## Compared with alternatives

aklomp/base64, fastbase64, Turbo-Base64, base64-turbo, vb64 and simdutf are native C/C++/Rust codecs running at several to 100+ GB/s, and none ships as a drop-in JS package for a browser page. Pick fast-base64 only when you need a ready-made web JS/Wasm package for trusted data; if you control native code, simdutf (which validates) is the better choice.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none |
| **Minimum toolchain** | An ES module environment with WebAssembly and TextEncoder/TextDecoder. The fast path needs Wasm SIMD and falls back to scalar Wasm, with a console.warn, if instantiation fails. The package is ESM-only: package.json exports only an 'import' condition, so there is no CommonJS require. |
| **Platforms** | Browsers, Node and Deno (deno.land/x/fast_base64) for the default build. The README says `/small` and `/nano` have no Node support. |
| **Thread safety** | Single-threaded JS. All concurrent async calls in one realm share one module-level WebAssembly.Memory with a bump allocator (closed issue #2 was about concurrent calls overwriting each other's memory). Worker use is not documented beyond the author's comment in issue #3 that the main version should work in all JS environments. |
| **Drop-in for the baseline** | partial — all four variants export the same toBytes/toBase64 names, but the default returns Promises while the `/js` and `/nano` baselines are synchronous, so switching means adding await. |

## Gotchas

- Encoder overrun bug: the SIMD encoder stores whole 16-byte vectors without padding its output allocation, so it writes up to 12 bytes past it. In our run on Node 24.18, toBase64 of a 28,086-byte input on fresh module memory threw 'RuntimeError: memory access out of bounds', because the allocation exactly fills the 64 KiB Wasm page. By our reading of the code it can also overwrite an adjacent in-flight allocation.
- The variants disagree on base64url. `/js` decodes '-' and '_' as 62/63, but the default SIMD path turns them into garbage ('-_-_' gave [197,236,94] instead of [251,255,191]), so run fromUrl() first.
- Only '=' is stripped before decoding, so whitespace or newlines (for example MIME-wrapped base64) corrupt the output without raising an error.
- The TypeScript types are not wired into the package.json `exports` map (open issue #6), so ESM + TS type resolution can fail. The repo's correctness check (test-base64.js) never exercises the default SIMD toBase64.

## Known shortcomings

- JavaScript/WASM, not C++. 'Fastest JS' baseline is the project's own fast-base64/js; the nano (atob/btoa) comparison is 3-100x. First-party numbers only; \~6k npm downloads/week.
- Encoder overrun bug (reproduced on Node 24): toBase64 on a 28,086-byte input fails with 'memory access out of bounds'. No input validation (invalid characters, newlines and base64url produce silent garbage). The 20x claim was not reproduced: warm runs on M1 Pro show WASM \~2x decode / \~4x encode over its own JS, and Node's Buffer is 5-10x faster than both. Abandoned since 2022-01; ESM-only with broken types (#6); native Uint8Array.fromBase64 is Baseline since 2025-09.

## Caveats and trade-offs

The 'fastest JS implementation' baseline is the author's own pure-JS port shipped in the same package. The README says so, but it is not an independent library. Native atob()/btoa() only appears through the nano wrapper, which adds array/string conversion overhead. No hardware, browser/Node version or results table is given, and the harness (test-base64.js) prints timings without publishing them. It cannot be used directly from C++ (JS/Wasm only) and is included under the any-language allowance.

Async API for the fastest (SIMD Wasm) variant; smaller/sync variants trade 2-100x speed for size or synchronicity. Threaded variants were found to be no faster except for &gt;1MB payloads in pure JS.

## Maintenance

Abandoned (last commit and npm 0.1.8 on 2022-01-04; issues from 2023-2024 unanswered) yet still about 6,000 npm downloads a week; it is MIT-licensed and small enough to vendor, but you would need to patch the encoder overrun and add validation yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README gives first-party speed claims with no published results table, hardware, runtime version or methodology. A harness exists (test-base64.js, run with `npx chrodemon`) but its output is never published.
- **Verifier notes:** The README numbers match the record word for word. The README also clarifies that the 'fastest JS implementation' is the package's own fast-base64/js, so I corrected the baseline and caveats. Metadata checks out: MIT, 58 stars, not a fork, not archived, last commit 2022-01-04 (abandoned).
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/mitschabaude/fast-base64>
  - <https://github.com/mitschabaude/fast-base64#readme>
  - <https://github.com/mitschabaude/fast-base64/blob/main/test-base64.js>
  - <https://api.npmjs.org/downloads/point/last-week/fast-base64>
  - <https://registry.npmjs.org/fast-base64>
- **Sources the enricher read:**
  - <https://github.com/mitschabaude/fast-base64>
  - <https://github.com/mitschabaude/fast-base64/blob/main/README.md>
  - <https://github.com/mitschabaude/fast-base64/blob/main/wasm.js>
  - <https://github.com/mitschabaude/fast-base64/blob/main/wasm-tools.js>
  - <https://github.com/mitschabaude/fast-base64/blob/main/wat/base64-simd.wat>
  - <https://github.com/mitschabaude/fast-base64/blob/main/js.js>
  - <https://github.com/mitschabaude/fast-base64/blob/main/small.js>
  - <https://github.com/mitschabaude/fast-base64/blob/main/nano.js>
  - <https://github.com/mitschabaude/fast-base64/blob/main/url.js>
  - <https://github.com/mitschabaude/fast-base64/blob/main/util.js>
  - <https://github.com/mitschabaude/fast-base64/blob/main/mod.ts>
  - <https://github.com/mitschabaude/fast-base64/blob/main/wasm-inline.js>
  - <https://github.com/mitschabaude/fast-base64/blob/main/build-lib.js>
  - <https://github.com/mitschabaude/fast-base64/blob/main/dist/wasm.js>
  - <https://github.com/mitschabaude/fast-base64/blob/main/test-base64.js>
  - <https://github.com/mitschabaude/fast-base64/blob/main/types/index.d.ts>
  - <https://github.com/mitschabaude/fast-base64/blob/main/types/js.d.ts>
  - <https://github.com/mitschabaude/fast-base64/blob/main/package.json>
  - <https://github.com/mitschabaude/fast-base64/blob/main/LICENSE.md>
  - <https://github.com/mitschabaude/fast-base64/commits/main>
  - <https://github.com/mitschabaude/fast-base64/issues?q=is%3Aissue>
  - <https://github.com/mitschabaude/fast-base64/issues/2>
  - <https://github.com/mitschabaude/fast-base64/issues/3>
  - <https://github.com/mitschabaude/fast-base64/issues/4>
  - <https://github.com/mitschabaude/fast-base64/issues/5>
  - <https://github.com/mitschabaude/fast-base64/issues/6>
  - <https://registry.npmjs.org/fast-base64>
  - <https://api.npmjs.org/downloads/point/last-week/fast-base64>
  - <https://hn.algolia.com/api/v1/search?query=fast-base64&restrictSearchableAttributes=url>
  - <https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Uint8Array/fromBase64>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/mitschabaude/fast-base64`) · [data/wave7/enrich/raw/github_com_mitschabaude_fast_base64.json](../../../data/wave7/enrich/raw/github_com_mitschabaude_fast_base64.json) (enrichment confidence 0.8)

</details>
