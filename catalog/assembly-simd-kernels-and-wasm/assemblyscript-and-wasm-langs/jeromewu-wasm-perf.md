# wasm-perf (Emscripten Wasm SIMD intrinsics vs JavaScript matrix multiply)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🔴 abandoned

> Blog demo: 64x64 int32 matrix multiply in C compiled to Wasm SIMD128 by Emscripten, timed against a plain JavaScript loop.

| | |
|---|---|
| **Beats** | JavaScript (mul_mats.js) running in Node.js v16.16.0 (V8) |
| **Claimed result** | README table (first-party, Node.js v16.16.0): mul_mats_intrin-wasm-simd-O3 0.245s vs mul_mats.js 5.768s (-95.8%, about 23.5x, derived from page data); -O3 -msimd128 auto-vectorised 0.278s (-95.2%); -O3 without SIMD 2.012s (-65%); Wasm built without -O3 (emcc default -O0) is slower than JS (6.865s, +19%). The JS baseline computes NaN on uninitialised arrays; in a verifier rerun on Node 22.22.0 (different machine, Intel Xeon @ 2.10GHz) the repo's JS took 10.342s while an Int32Array version with a local accumulator and Math.imul took 4.583s (2.26x faster), so against idiomatic JS the headline would be roughly 10x, not 23.5x (estimate, cross-machine). |
| **Workload** | Time to complete 10,000 multiplications of two 64 x 64 matrices, JavaScript vs C compiled to WebAssembly by Emscripten with and without -O3 and -msimd128 and with SIMD intrinsics, plus native GCC rows. |
| **Metric** | throughput |
| **Hardware** | 11th Gen Intel Core i5-1135G7 @ 2.40GHz, 16 GB RAM, Manjaro Linux kernel 5.19.1 |
| **Compiler and flags** | Emscripten 3.1.18 with -O3 and -msimd128 (hand-written SIMD intrinsics in mul_mats_intrin.c); GCC 12.2.0 for the native rows (-O3, -O3 -mavx2); Node.js v16.16.0 |
| **Adoption** | 13 stars |
| **Last commit** | 2022-09-01 |
| **Links** | [repository](https://github.com/jeromewu/wasm-perf) · [benchmark](https://github.com/jeromewu/wasm-perf) |

## Verdict

On an i5-1135G7 with Node.js 16.16.0 and Emscripten 3.1.18, 10,000 64x64 int32 multiplies took 0.245 s with the -O3 -msimd128 intrinsics kernel, 0.278 s auto-vectorised and 2.012 s at -O3 without SIMD, against 5.768 s for a JavaScript loop that computes NaN on unfilled arrays. Re-run here (Node 22.22.0, Xeon @ 2.10GHz, kernel rebuilt with clang 18.1.3, best of 7): intrinsics 0.332-0.344 s, auto-vectorised 0.288 s, no-SIMD -O3 1.435-1.464 s, repo JS 10.03-11.21 s, Int32Array JS with Math.imul 4.29-4.66 s, so Wasm SIMD is about 13-15x faster than idiomatic JS (derived, different toolchain and machine).

## Use it when

- As a short, MIT-licensed starting point for writing wasm_simd128.h intrinsics in C with Emscripten (load, i32x4 mul/add, shuffle-based horizontal sum).
- To show a team the size of the gap between unoptimised emcc output (-O0, slower than JS) and emcc -O3 -msimd128 for a compute-bound integer loop.
- Small dense int32 dot-product or matrix kernels where the dimension is a multiple of 4 and wraparound int32 arithmetic is acceptable.
- Checking whether your own runtime (Node, a browser, a standalone Wasm VM) has working SIMD128 and how it compares with scalar Wasm.

## Skip it when

- As evidence of how much faster Wasm is than JavaScript: the JS baseline never fills its inputs (it multiplies undefined by undefined and produces NaN) and uses generic double arrays with a store on every inner iteration; an Int32Array plus Math.imul version is about 2.3x faster than the repo's JS, so the honest gap is roughly 10-15x (verifier estimate about 10x, 13-15x in a re-run here), not 23.5x.
- As evidence that hand-written intrinsics beat auto-vectorisation: rebuilt here with clang 18 -O3 -msimd128 on Node 22.22.0, the auto-vectorised scalar loop (best 0.288 s) was faster than the intrinsics kernel (best 0.332-0.344 s).
- Floating-point or non-multiple-of-4 matrices: the intrinsics loop steps k by 4 with no tail and only does int32 multiplies.
- Real matrix multiplication work: there is no blocking, packing, threading or float support; use a BLAS or a Wasm-targeted linear-algebra library instead.
- Anything that needs maintenance: 13 commits, all between 2022-08-26 and 2022-09-01, no issues, no releases.

## How it is fast

Most of the gain comes from compiling with -O3 (no-SIMD Wasm -O3 is 2.9x faster than the repo's JS) and enabling -msimd128 so LLVM auto-vectorises the dot-product loop into i32x4.mul/i32x4.add (a further 7x). The intrinsics kernel writes that dot product by hand: a v128 accumulator over four int32 lanes, loads from row i of A and row j of pre-transposed B, and a two-shuffle horizontal reduction at the end of each output element. B is stored transposed so both operands are read with unit stride.

## Compared with alternatives

Pick it for a minimal C/Emscripten intrinsics example; for a fairer JS-vs-Wasm matrix comparison (typed-array JS baseline, per-size sweep, 1.0-1.8x) see JavaScript-vs-WebAssembly-Comparative-Analysis, and for production Wasm SIMD code with real baselines see tape-sha256 or sha2-wasm.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Build: Docker 19.03+ with buildx, using the emscripten/emsdk:3.1.18 and gcc:12.2.0 images; run: Node.js. The kernel itself needs only wasm_simd128.h. |
| **Minimum toolchain** | Emscripten 3.1.18 as tested (any clang with -msimd128 and wasm_simd128.h; clang 18.1.3 compiled the kernel unchanged here); Node.js 16.16.0 as tested |
| **Platforms** | Any WebAssembly runtime with the SIMD128 feature (measured only in Node.js); the Docker build and make run-all target Linux, and the README warns some runs may fail elsewhere; native rows are x86-64, one built with -mavx2 |
| **Thread safety** | Single-threaded demo; the kernel keeps no global state but this is not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- The result check is blind to indexing bugs: inputs are all ones and the program only prints a message if the sum differs from 64^3 (exit code stays 0). The pre-fix kernel (before commit fa08bf6, 2022-09-01) loaded &in_a[i] and &in_b[j] instead of &in_a[i\*n+k] and &in_b[j\*n+k], still passed this check, and was published as 0.062 s (-99%). Re-run here: on all-ones data the pre-fix kernel gives 262144 like the fixed one, on varied data it gives -16 against the correct 584, and it runs in 0.062-0.106 s, matching the withdrawn figure.
- mul_mats.js is not the C algorithm in JavaScript: in_a.arr and in_b.arr are never filled, the transpose loop writes to the wrapper objects instead of .arr, every product is NaN and the output is never checked. It also does double arithmetic, while the C/Wasm side does wrapping int32.
- The README row labelled mul_mats_intrin-wasm-simd-O3.js is built as dist/mul_mats_intrin-wasm-O3-simd.js (make run-wasm-O3-simd-intrin). The non-O3 intrinsics row (4.718 s) was measured on the pre-fix kernel and never re-run. Rows without -O3 are emcc -O0 debug builds, so 'Wasm slower than JS' there is a build-flag artifact.
- Native GCC rows: -O3 targets baseline x86-64 (SSE2, no pmulld), so the blog's 'Wasm SIMD is faster than C' line compares against crippled native code; gcc -O3 -mavx2 (0.119 s) is about 2x faster than the best Wasm row. Each row is one run with no repetition, timed by clock() in C and console.time in JS.

## Known shortcomings

- The JavaScript baseline mul_mats.js never initialises its inputs (NaN math on holey arrays, result unchecked, doubles vs int32); the verifier's rerun on Node 22.22.0 shows an Int32Array version 2.26x faster than the repo JS, so the 23.5x headline is roughly 10x against idiomatic JavaScript; the non-O3 intrinsics row predates fix fa08bf6.
- The result check uses all-ones inputs and cannot catch indexing bugs: the pre-fix kernel (before fa08bf6) loaded &in_a[i] and &in_b[j], passed the check and was published as 0.062 s; reproduced here (varied data gives -16 vs the correct 584, all-ones gives 262144 like the fixed kernel). Enricher rerun (clang 18 -O3 -msimd128, Node 22.22.0, Xeon 2.10 GHz, best of 7): intrinsics 0.332-0.344 s vs auto-vectorised 0.288 s, so the intrinsics advantage is not reproduced; repo JS 10.03 s (NaN), Int32Array JS 4.29 s, so the real gap is about 13-15x, not 23.5x. Each README row is one run with no repetition; native -O3 rows target baseline x86-64 without -mavx2.

## Caveats and trade-offs

Baseline defect: mul_mats.js allocates in_a.arr and in_b.arr with new Array(size) and never fills them (its transpose loop writes to the wrapper objects, not .arr), so the timed loop multiplies undefined\*undefined = NaN in holey arrays and the output is never checked; the C/Wasm versions fill inputs with 1 and verify the sum. JS uses doubles while C/Wasm use int32 (wasm_i32x4_mul). Verifier rerun on Node 22.22.0: original 10.342s (sum NaN), filled plain arrays 9.876s, Int32Array 6.660s, Int32Array with local accumulator 4.583s; the uninitialised arrays cost little, but the untyped, store-every-iteration JS understates JS by about 2.3x. The intrinsics kernel had an indexing bug fixed on 2022-09-01 (fa08bf6, loads from &in_a[i] instead of &in_a[i\*n+k]); that commit re-measured the two -O3 SIMD rows (0.062s became 0.245s) but not the non-O3 intrinsics row (4.718s), which predates the fix. Non-O3 Wasm rows are emcc -O0 debug builds. Native GCC -O3 is baseline x86-64 (SSE2, no pmulld), so Wasm SIMD beating it is a flags artifact; native -O3 -mavx2 (0.119s) is about 2x faster than the best Wasm row. Single 64x64 int32 matrix-multiply microbenchmark from a 2022 Node 16 / Emscripten 3.1.18 setup; demo repo for a blog post, not a library. [retier] Baseline defect: mul_mats.js allocates in_a.arr and in_b.arr with new Array(size) and never fills them, so the timed loop multiplies undefined\*undefined = NaN in holey arrays and the output is never checked; JS uses doubles while C/Wasm use int32. Reruns on Node 22.22.0 (Intel Xeon @ 2.10GHz, different machine): repo JS 10.03-10.34 s (sum NaN), Int32Array with local accumulator 4.29-4.58 s, so the untyped, store-every-iteration JS understates JS by about 2.3x and the real gap is about 13-15x, not 23.5x. The result check uses all-ones inputs and only prints a message if the sum differs from 64^3: the pre-fix kernel (before fa08bf6, 2022-09-01, loads from &in_a[i] and &in_b[j]) passed it and was published as 0.062 s; on varied data it returns -16 against the correct 584 (reproduced). The fix re-measured the two -O3 SIMD rows (0.062 s became 0.245 s) but not the non-O3 intrinsics row (4.718 s). Enricher rerun (clang 18 -O3 -msimd128, best of 7): intrinsics 0.332-0.344 s vs auto-vectorised 0.288 s, so the intrinsics advantage over -O3 -msimd128 auto-vectorisation is not reproduced. Non-O3 Wasm rows are emcc -O0 debug builds; native GCC -O3 rows target baseline x86-64 (SSE2, no pmulld) and gcc -O3 -mavx2 (0.119 s) is about 2x faster than the best Wasm row; each row is one run with no repetition. Single 64x64 int32 matrix-multiply microbenchmark from a 2022 Node 16 / Emscripten 3.1.18 blog demo, abandoned since 2022-09-01.

Needs the WebAssembly SIMD proposal (browser or Node support) and an Emscripten toolchain. The win comes from -O3 plus SIMD, not from Wasm alone.

## Maintenance

Abandoned since 2022-09-01 (13 commits over one week, 13 stars, no issues); MIT-licensed blog demo whose only reusable piece is a 20-line int32 kernel, and whose headline numbers rest on a broken JS baseline and an all-ones result check that missed a published indexing bug.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** Code (mul_mats.js, mul_mats.c, mul_mats_intrin.c, Dockerfile), compilers, flags and CPU (i5-1135G7) are all public, but the JavaScript baseline is broken: mul_mats.js never initialises its input arrays, so every product is undefined\*undefined = NaN on holey generic arrays with no result check, and it does double arithmetic while the C/Wasm side does int32. A baseline with an unfixed correctness bug that also understates idiomatic JS caps the claim at C.
- **Verifier notes:** Numbers match the README, but the JS baseline never initialises its inputs (computes NaN, unchecked) and is untyped double code vs int32 Wasm; verifier rerun shows idiomatic typed JS 2.26x faster than the repo's JS, so the 23.5x headline is overstated (roughly 10x). Not invalid enough to reject (the Wasm side does the real work and is verified by its sum check). Metadata: MIT, 13 stars, 0 forks, last commit 2022-09-01 (abandoned), not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-52 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/jeromewu/wasm-perf>
  - <https://github.com/jeromewu/wasm-perf/commits>
  - <https://github.com/jeromewu/wasm-perf/commits/main>
  - <https://github.com/jeromewu/wasm-perf/commit/fa08bf608c5b6e3264faba63de268bb8617c33d0>
  - <https://github.com/jeromewu/wasm-perf/commit/edf01fe0f06b8b5f73281b03d338b731fff4af82>
  - <https://raw.githubusercontent.com/jeromewu/wasm-perf/HEAD/README.md>
  - <https://raw.githubusercontent.com/jeromewu/wasm-perf/HEAD/mul_mats.js>
  - <https://raw.githubusercontent.com/jeromewu/wasm-perf/HEAD/mul_mats.c>
  - <https://raw.githubusercontent.com/jeromewu/wasm-perf/HEAD/mul_mats_intrin.c>
  - <https://raw.githubusercontent.com/jeromewu/wasm-perf/HEAD/Makefile>
  - <https://raw.githubusercontent.com/jeromewu/wasm-perf/HEAD/Dockerfile>
  - <https://raw.githubusercontent.com/jeromewu/wasm-perf/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/jeromewu/wasm-perf>
  - <https://github.com/jeromewu/wasm-perf/commits/main>
  - <https://github.com/jeromewu/wasm-perf/commit/fa08bf608c5b6e3264faba63de268bb8617c33d0>
  - <https://github.com/jeromewu/wasm-perf/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/jeromewu/wasm-perf/HEAD/README.md>
  - <https://raw.githubusercontent.com/jeromewu/wasm-perf/HEAD/mul_mats.js>
  - <https://raw.githubusercontent.com/jeromewu/wasm-perf/HEAD/mul_mats.c>
  - <https://raw.githubusercontent.com/jeromewu/wasm-perf/HEAD/mul_mats_intrin.c>
  - <https://raw.githubusercontent.com/jeromewu/wasm-perf/HEAD/Makefile>
  - <https://raw.githubusercontent.com/jeromewu/wasm-perf/HEAD/Dockerfile>
  - <https://raw.githubusercontent.com/jeromewu/wasm-perf/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/jeromewu/wasm-perf/edf01fe0f06b8b5f73281b03d338b731fff4af82/mul_mats_intrin.c>
  - <https://github.com/jeromewu/jeromewu.github.io>
  - <https://github.com/jeromewu/jeromewu.github.io/tree/master/content/blog>
  - <https://raw.githubusercontent.com/jeromewu/jeromewu.github.io/master/content/blog/improving-performance-using-webassembly-simd-intrinsics/index.md>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/jeromewu/wasm-perf`) · [data/wave13/enrich/raw/github_com_jeromewu_wasm_perf.json](../../../data/wave13/enrich/raw/github_com_jeromewu_wasm_perf.json) (enrichment confidence 0.85)

</details>
