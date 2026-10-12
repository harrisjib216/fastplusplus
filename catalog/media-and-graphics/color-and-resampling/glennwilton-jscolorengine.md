# jsColorEngine

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `JavaScript (optional WebAssembly SIMD kernels)` · `MPL-2.0` · 🟢 active

> Pure-JavaScript ICC colour engine with WebAssembly SIMD CLUT kernels; 3.1-3.6x faster than lcms-wasm on 8-bit LUT image transforms.

| | |
|---|---|
| **Beats** | Little CMS 2 (lcms2 2.18 native built with gcc at -O2 and -O3; lcms-wasm = LittleCMS 2.16 compiled to WebAssembly) |
| **Claimed result** | README 'Current figures' table (Ryzen 7 7700X, one thread, Node 24, 1 MPx photographs), int-wasm-simd MPx/s with ratios vs lcms-wasm and vs native C lcms2: RGB to Lab 120.3 (3.6x, 1.8x), RGB to CMYK 119.3 (3.4x, 1.9x), CMYK to RGB 78.6 (3.1x, 2.0x), CMYK to CMYK 80.8 (3.5x, 2.2x), RGB to RGB soft-proof 115.9 (3.4x, 2.1x), RGB to RGB matrix 117.6 (1.8x vs lcms-wasm, 0.71x vs native C). docs/LcmsComparison.md (2026-08-19, jsCE 1.5.0) gives the absolute native lcms2 figures: 65.6, 61.9, 40.0, 35.6, 56.9 and 164.5 MPx/s (matrix). The 1.5.5 fused matrix-shaper kernel reaches 328 MPx/s against 119 for jsColorEngine's own CLUT path (README); that is an internal comparison, and LcmsComparison.md says the matrix head-to-head against lcms has not been re-run. |
| **Workload** | ICC-profile image transforms (RGB to Lab, RGB to CMYK, CMYK to RGB, CMYK to CMYK, RGB soft-proof through CMYK, matrix-shaper RGB to RGB), 1 megapixel real photographs, GRACoL2006 and AdobeRGB1998 profiles, single thread, each measurement in its own process. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 7700X (8 cores / 16 threads), 31 GB RAM, Windows 10 x64 |
| **Compiler and flags** | Native baseline: lcms2 2.18 (MIT core, no plugins) built with gcc 9.3.0 (Ubuntu 9.3.0-17ubuntu1\~20.04) under WSL2 Ubuntu 20.04, best of -O2 (RGB-source workflows) and -O3 (CMYK-source and soft-proof) after a seven-set CFLAGS sweep, pinned with taskset -c 0. jsColorEngine runs on Node v24.16.0 under Windows 10 x64 (V8 JIT, no compiler flags). lcms-wasm 1.0.5 (LittleCMS 2.16 compiled to wasm32 with Emscripten) is the prebuilt npm package; its build flags are not stated. |
| **Adoption** | 41 stars |
| **Last commit** | 2026-09-09 |
| **Links** | [repository](https://github.com/glennwilton/jsColorEngine) · [benchmark](https://github.com/glennwilton/jsColorEngine/blob/main/README.md) |

## Verdict

The README 'Current figures' table (Ryzen 7 7700X, one thread, Node v24.16.0 on Windows 10, 1 MPx from a 5-photo corpus, GRACoL2006 and AdobeRGB1998, relative colorimetric, 8-bit) gives int-wasm-simd at 78.6-120.3 MPx/s. That is 3.1-3.6x lcms-wasm 1.0.5 (LittleCMS 2.16 built with Emscripten, flags not stated) and 1.8-2.2x native lcms2 2.18 (gcc 9.3.0 -O2/-O3 under WSL2, taskset -c 0). None of these README rows appears in any generated table. The frozen same-run snapshot bench/history/1.6.0 (2026-08-22: BenchResults.md plus native-content-O2/O3.txt) gives jsCE SIMD 112.2/113/81.2/81/110.6 MPx/s against best cached native lcms at 66.4/61.5/39.7/35.8/57.1, which is 1.69/1.84/2.05/2.26/1.94x (derived from page data). On photos lcms's cmsFLAGS_NOCACHE build is faster (72.8/65.6/40.1/35.8/61.5), so against lcms's best configuration the margin is 1.54-2.26x (derived from page data). The README's RGB-to-Lab 3.6x over lcms-wasm does not follow from any published lcms-wasm figure (120.3/35.9 = 3.35x; the 1.6.0 table says 3.2x).

## Use it when

- JavaScript or TypeScript code (Node, browsers, Electron, web workers, Adobe CEP panels) that converts images between ICC profiles and would otherwise install lcms-wasm.
- 8-bit photographic content of about 1 MPx or more, where one core sustains roughly 80-120 MPx/s on RGB/CMYK LUT workflows (Ryzen 7 7700X, Node 24).
- Soft-proofing or prepress previews in the browser or on a headless server where WebGL/WebGPU shaders are not an option.
- Folders of images on a multicore Node host: transformImages() peaked at 787 MPx/s on 8 workers (noise content, int kernel) with output byte-identical to the sequential path.
- Shipping a baked, content-signed LUT JSON (Transform.fromJSON) instead of the ICC profiles themselves.

## Skip it when

- C or C++ code bases: there is no native API. Use lcms2 (with the GPL3 fast_float plugin for matrix-shaper RGB) or moxcms from Rust.
- Work that needs bit-identical output to LittleCMS: the image path is within 1 LSB of lcms on 100% of samples but only 96.8-99.2% bit-exact. The f64 path (buildLut: false) is an order of magnitude slower.
- Matrix-shaper RGB-to-RGB at peak speed: lcms2 with fast_float reaches about 455 MPx/s (SSE2) against jsCE's 328-331 MPx/s fused kernel. WebAssembly SIMD is fixed at 128 bits, so AVX2/AVX-512 native code can always go wider.
- Memory-constrained parallel use: each worker holds its own copy of every LUT (about 1.4 MB for a 33-point CMYK LUT, about 11.5 MB across 8 workers, plus a WASM copy per worker), where lcms's threaded plugin shares one.
- Named-colour (ncl2), abstract or ColorSpace-class profiles and MPE-only profiles are unsupported. N-channel input is slow: 5CLR and 6CLR got only WASM-scalar LUT kernels in 1.6.0 (16.4 and 7.66 MPx/s), and 7-15CLR input has no LUT path at all, so it runs per pixel on the accuracy pipeline.

## How it is fast

When the transform is created, the whole profile chain is sampled into a u16 CLUT (33^3 for RGB input, 17^4 for CMYK input, the same grid sizes lcms2's _cmsReasonableGridpointsByColorspace picks by default). Each pixel is then evaluated with tetrahedral interpolation and Q0.16 weights, in hand-written WebAssembly (.wat). The SIMD is channel-parallel: the 3-4 output channels at each tetrahedron corner are loaded into one i32x4 vector (v128.load64_zero + i32x4.extend_low_i16x8_u), so all channels of a pixel are interpolated at once. There is one monomorphic kernel per (input dims x output channels x data format), picked at create(). Stock lcms2 interpolates with scalar code behind a general stage walker, so the project's own analysis puts the \~2x over native C down to 128-bit width, not a better algorithm. Since 1.5.5, RGB-to-RGB matrix-shaper pairs skip the CLUT and run a fused curve-3x3-curve kernel (328-331 MPx/s at int8 on photos).

## Compared with alternatives

Pick jsColorEngine when the code has to run inside a JavaScript or WebAssembly host. In C or C++, stay with Little CMS 2 plus the fast_float plugin, and in Rust use moxcms. babl is GEGL/GIMP's pixel-format converter rather than a general ICC CMYK engine.

## Integration

| | |
|---|---|
| **Form** | module (npm package jscolorengine; CommonJS source, or a UMD bundle of about 115 KB gzip with the WASM inlined) |
| **Dependencies** | none at runtime (canvas, esbuild, jest, utif and wabt are dev-only) |
| **Minimum toolchain** | not documented (no engines field); the top tier needs a WebAssembly engine with 128-bit SIMD, and the dispatcher falls back to WASM scalar and then pure JS |
| **Platforms** | any JavaScript host: Node, browsers, Electron, web workers, React Native, Adobe CEP; results quoted for x86-64 Windows and Apple M4 |
| **Thread safety** | Single-threaded per JS realm. Parallelism comes only from the transformImages() worker pool: worker_threads on Node, and a separate worker bundle URL in browsers; without that URL it runs sequentially. |
| **Drop-in for the baseline** | no |

## Gotchas

- lutMode 'auto' picks int-wasm-simd only for int8/int16 data with buildLut: true; every other combination resolves to the slow 'float' path. Check xform.lutMode after create().
- pixelCache defaults to 'auto' since 1.6.0. The in-kernel last-pixel memo gains up to 3.94x on flat colour, costs about 4% on noisy photos and runs 5-channel photos at 0.84x; set pixelCache: 0 for grainy input.
- Throughput depends on CLUT coverage. Buffers under about 1x the CLUT cell count (for example 64K px against a 17^4 CMYK grid) or synthetic gradients read up to 1.8x high. The project withdrew its pre-1.5 figures (about 210-216 MPx/s) because its noise generator produced only 256 distinct colours.
- Premultiplied-alpha pixels must be unpremultiplied first (alpha.unpremultiply). Before 1.6.1 (issue #9), profiles loaded from a Uint8Array view with a non-zero byteOffset, as embedded in TIFF or JPEG, were silently mis-parsed.

## Known shortcomings

- JavaScript library with optional WebAssembly SIMD kernels (language-filter mismatch); neither ImageMagick nor stb_image_resize was tested. The native-C comparison (bench/lcms_c, gcc 9.3.0, -O2/-O3, Ryzen 7700X) is still being re-measured after issue #6, where the Little-CMS author pointed out wrong API calls; README figures differ from docs/BenchResults.md and LcmsComparison.md, and the 328 vs 119 MPx/s row compares the jsCE kernel with its own CLUT path, not with lcms.
- The README table (120.3/119.3/78.6/80.8/115.9) matches no generated file; the frozen same-run snapshot bench/history/1.6.0/win32-x64-amd-ryzen-7-7700x-8-core (native-content-O2/O3.txt plus BenchResults.md, 2026-08-22) is the reproducible source and its native harness already runs flags=0 / NOCACHE. The README ratio against native uses cached lcms2 although NOCACHE is faster on photos: derived 1.6.0 ratios are 1.69-2.26x against cached and 1.54-2.26x against NOCACHE (README says 1.8-2.2x); the RGB to Lab 3.6x against lcms-wasm is not derivable (120.3/35.9 = 3.35x; the 1.6.0 table says 3.2x). The lcms_c README's fast_float '3-4x' claim is stale (old 256-colour generator); the pixelCache 'auto' default since 1.6.0 lifts flat-content figures.

## Caveats and trade-offs

Issue #6 (opened 2026-05-17 by mm2, the LittleCMS author, now closed) says the native benchmark used incorrect lcms API calls and that lcms plugins give 'an easy 10x improvement, sometimes more'. The README still says the native-C numbers are being re-measured with corrected API calls before they are quoted further, yet the same README shows them in its current table, so treat the vs-native-C column as provisional (the vs lcms-wasm ratios are stated to be unaffected). The README table does not match the current generated docs/BenchResults.md or docs/LcmsComparison.md exactly. Host asymmetry: the JS runs on Windows, native lcms under WSL2 on the same CPU. Different work: jsColorEngine bakes the transform into an 8-bit 33^3 or 17^4 CLUT and interpolates it with 128-bit WASM SIMD, while lcms2 (flags = 0) builds its own precalculated device link and interpolates it with scalar code; outputs agree within 1 LSB (96.8-99.2% bit-exact), not bit-identical. lcms with the GPL fast_float plugin reaches about 455 MPx/s on matrix RGB to RGB (LcmsComparison.md) and is not in the head-to-head. Single machine, first-party. Language filter mismatch: the library is JavaScript plus inline WebAssembly, not C or C++, and is usable from C++ only by embedding a JS/WASM runtime. The baseline (Little CMS) is not on the color-and-resampling list (ImageMagick, stb_image_resize), and neither of those is measured.

Pure JavaScript, no native bindings; image path uses a baked CLUT so it is slightly less accurate than lcms2 (README: 100% of samples within 1 LSB of the LittleCMS oracle on the four tested workflows). JS/WASM only, not callable from C++.

## Maintenance

Active, single maintainer: 1.6.1 shipped on 2026-09-10, the last commit is 2026-09-09 (195 commits) and no issues are open. MPL-2.0 is file-level copyleft and fine to vendor into JS applications, but the library is not usable from C++ without embedding a JS/WASM runtime.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README 'Current figures' table matches the record exactly, and the native-C side has every A ingredient on paper (bench/lcms_c/bench_content_matrix.c driven by bench/reproduce.js, gcc 9.3.0 in WSL2, -O2/-O3 per workflow, Ryzen 7 7700X). It stays C because the project itself says the native lcms numbers are being re-measured with corrected lcms API calls after the LittleCMS author's issue #6 and should not be quoted further, and the README figures do not match the current generated docs/BenchResults.md (jsCE 1.6.0 photo row: 112.2/113/81.2/81/110.6 MPx/s) or docs/LcmsComparison.md (jsCE 1.5.0: 119.6/121.5/82.0/81.3/118.9); the lcms-wasm baseline is a prebuilt npm package whose Emscripten flags are not stated.
- **Verifier notes:** Numbers match the README; the project's own docs contradict each other on whether the native-C column is final, so C stands. The language correction is outside verify.py's CORRECTABLE set; record it as a decision override if wanted.
- **Fields the verifier corrected:** `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/glennwilton/jsColorEngine/HEAD/README.md>
  - <https://raw.githubusercontent.com/glennwilton/jsColorEngine/HEAD/docs/LcmsComparison.md>
  - <https://raw.githubusercontent.com/glennwilton/jsColorEngine/HEAD/docs/BenchResults.md>
  - <https://raw.githubusercontent.com/glennwilton/jsColorEngine/HEAD/bench/lcms_c/bench_content_matrix.c>
  - <https://raw.githubusercontent.com/glennwilton/jsColorEngine/HEAD/bench/lcms_c/Makefile>
  - <https://raw.githubusercontent.com/glennwilton/jsColorEngine/HEAD/bench/lcms_c/bench_marti.c>
  - <https://github.com/glennwilton/jsColorEngine/issues/6>
  - <https://github.com/glennwilton/jsColorEngine/tree/main/bench/lcms_c>
  - <https://github.com/glennwilton/jsColorEngine>
  - <https://github.com/glennwilton/jsColorEngine/commits/main>
  - <https://github.com/glennwilton/jsColorEngine/tree/main/src>
  - <https://github.com/glennwilton/jsColorEngine/tree/main/src/wasm>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/glennwilton/jsColorEngine/HEAD/README.md>
  - <https://raw.githubusercontent.com/glennwilton/jsColorEngine/HEAD/docs/LcmsComparison.md>
  - <https://raw.githubusercontent.com/glennwilton/jsColorEngine/HEAD/docs/BenchResults.md>
  - <https://raw.githubusercontent.com/glennwilton/jsColorEngine/HEAD/docs/deepdive/WasmKernels.md>
  - <https://raw.githubusercontent.com/glennwilton/jsColorEngine/HEAD/docs/deepdive/Architecture.md>
  - <https://raw.githubusercontent.com/glennwilton/jsColorEngine/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/glennwilton/jsColorEngine/HEAD/package.json>
  - <https://raw.githubusercontent.com/glennwilton/jsColorEngine/HEAD/bench/reproduce.js>
  - <https://raw.githubusercontent.com/glennwilton/jsColorEngine/HEAD/bench/release_matrix/run.js>
  - <https://raw.githubusercontent.com/glennwilton/jsColorEngine/HEAD/bench/release_matrix/README.md>
  - <https://raw.githubusercontent.com/glennwilton/jsColorEngine/HEAD/bench/lcms_c/bench_content_matrix.c>
  - <https://raw.githubusercontent.com/glennwilton/jsColorEngine/HEAD/bench/lcms_c/bench_lcms.c>
  - <https://raw.githubusercontent.com/glennwilton/jsColorEngine/HEAD/bench/lcms_c/bench_marti.c>
  - <https://raw.githubusercontent.com/glennwilton/jsColorEngine/HEAD/bench/lcms_c/Makefile>
  - <https://raw.githubusercontent.com/glennwilton/jsColorEngine/HEAD/bench/lcms_c/README.md>
  - <https://github.com/glennwilton/jsColorEngine/tree/main/bench/history/1.6.0>
  - <https://github.com/glennwilton/jsColorEngine/tree/main/bench/history/1.6.0/win32-x64-amd-ryzen-7-7700x-8-core>
  - <https://raw.githubusercontent.com/glennwilton/jsColorEngine/HEAD/bench/history/1.6.0/win32-x64-amd-ryzen-7-7700x-8-core/summary.txt>
  - <https://raw.githubusercontent.com/glennwilton/jsColorEngine/HEAD/bench/history/1.6.0/win32-x64-amd-ryzen-7-7700x-8-core/conditions.md>
  - <https://raw.githubusercontent.com/glennwilton/jsColorEngine/HEAD/bench/history/1.6.0/win32-x64-amd-ryzen-7-7700x-8-core/native-content-O2.txt>
  - <https://raw.githubusercontent.com/glennwilton/jsColorEngine/HEAD/bench/history/1.6.0/win32-x64-amd-ryzen-7-7700x-8-core/native-content-O3.txt>
  - <https://raw.githubusercontent.com/glennwilton/jsColorEngine/HEAD/bench/history/1.6.0/win32-x64-amd-ryzen-7-7700x-8-core/SNAPSHOT.json>
  - <https://github.com/glennwilton/jsColorEngine>
  - <https://github.com/glennwilton/jsColorEngine/commits/main>
  - <https://github.com/glennwilton/jsColorEngine/issues?q=is%3Aissue>
  - <https://github.com/glennwilton/jsColorEngine/issues/6>
  - <https://raw.githubusercontent.com/mm2/Little-CMS/master/src/cmspcs.c>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/glennwilton/jscolorengine`) · [data/wave10/enrich/raw/github_com_glennwilton_jscolorengine.json](../../../data/wave10/enrich/raw/github_com_glennwilton_jscolorengine.json) (enrichment confidence 0.8)

</details>
