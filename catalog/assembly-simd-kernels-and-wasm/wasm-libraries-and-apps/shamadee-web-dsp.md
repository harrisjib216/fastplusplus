# WebDSP

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MIT` · 🔴 abandoned

> 2017 C++-to-WebAssembly image/video filter set (Sobel, 3x3 convolutions, colour tweaks) with a pure-JS fallback; faster only on the heavy filters.

| | |
|---|---|
| **Beats** | its own JavaScript fallback implementations of the same image and video filters (in-browser) |
| **Claimed result** | No numbers. README states that without WebAssembly support 'the more intensive convolution and edge detection filters will run very slowly or hang the browser completely'. |
| **Workload** | Client-side image and video filters (grayscale, invert, Sobel edge detection, convolution, blur, sharpen) on RGBA canvas pixel data, WebAssembly build versus the JavaScript fallback shipped in the same package. |
| **Metric** | latency |
| **Compiler and flags** | Emscripten emcc (version not stated), cpp/compileWASM.sh: -lm -O3 -s WASM=1 -s BINARYEN_IMPRECISE=1 -s ALLOW_MEMORY_GROWTH=1 |
| **Adoption** | 1.5k stars, 112 forks |
| **Last commit** | 2017-06-05 |
| **Links** | [repository](https://github.com/shamadee/web-dsp) · [benchmark](https://github.com/shamadee/web-dsp) |

## Verdict

The repository has no benchmark; the README only says convolution and edge filters 'will run very slowly or hang the browser' without WebAssembly. The companion web-dsp-demo page times one video frame per path with performance.now() (WASM time includes malloc and both copies, the JS path filters in place, and both are given canvas.clientWidth as the image width), and independent users in issue #25 (2017-2018, Chrome 61-63, Firefox Nightly on an i7-6600U, a Pixel phone, a 2014 MacBook Air) found WASM 10-99% slower on most filters but 10-20x faster on Super Edge (Sobel) and 50-100% faster on Gaussian Blur; no maintainer replied.

## Use it when

- Learning or teaching how a 2017-style Emscripten module is wrapped for canvas pixel processing; the C++ file is under 150 lines.
- Prototyping edge detection (sobelFilter) or repeated 3x3 convolutions (blur with count=3) on small video frames, the only filters users reported as clearly faster than the JS path.
- Vendoring a single filter loop into your own, modern WASM build after reviewing it, since the code is MIT-licensed and tiny.

## Skip it when

- Simple per-pixel filters (grayscale, invert, brighten, colour presets): users in issue #25 measured the WASM path 10-99% slower than the JS fallback in Chrome 61-63 and Firefox because of the copy in and out of the WASM heap.
- Frames above about 1.3 megapixels with sobelFilter: it puts an int[width\*height] variable-length array on a 5 MB stack (see gotchas), so 1080p input runs past the stack into the heap.
- Anything production-facing: abandoned since 2017-06-05, the shipped .wasm does not match the source, there is no worker or OffscreenCanvas support, and the demo link in the README (tiny.cc/webdsp) now redirects to an affiliate spam page (issue #29).
- Pipelines that need exact or portable results: brighten does not saturate, grayScale only copies the red channel, multiFilter wraps in C++ but clamps in JS, and convFilter ignores its bias argument in the WASM path.

## How it is fast

There is no special algorithm: the C++ loops (scalar Sobel with a separate grayscale buffer, direct non-separable 3x3 convolution in float, per-byte colour arithmetic) are compiled with emcc -O3 through asm2wasm, so the gain comes only from running typed integer/float loops in WebAssembly instead of the JIT-compiled JS of the same loops. Each call mallocs a buffer in the WASM heap, copies the frame in (as bytes, or as Float32 for convFilter and noise, which quadruples the copy), runs the loop and hands back a view; that copy overhead is why simple per-pixel filters do not win.

## Compared with alternatives

Only when you want a small, readable example of canvas filtering in WASM; for measured wins on pixel work BlazeDiff core-wasm (about 10x over pixelmatch at 4K) or the TensorFlow.js WASM backend are maintained and benchmarked, and iswasmfast is the better reference for when WASM actually beats JS.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime (Emscripten glue and prebuilt .wasm are in lib/); rebuilding needs an emsdk checkout at ../emsdk with the 2017 asm2wasm toolchain |
| **Minimum toolchain** | Browser with WebAssembly (binary version 1) and fetch, served over HTTP; rebuild script targets 2017 Emscripten (BINARYEN_IMPRECISE, asm2wasm) and BSD sed (macOS) |
| **Platforms** | Desktop browsers; the demo page states WebAssembly was not yet supported on mobile at the time |
| **Thread safety** | not documented; one global Emscripten Module and heap on the main thread, wrappers use the global _malloc/HEAPU8 |
| **Drop-in for the baseline** | partial: the WASM object and jsFallback() expose the same function names, but outputs differ for the multiFilter family (wrap vs clamp), convFilter (bias ignored, clamping), Sobel borders and the eight filters listed in the README TODO |

## Gotchas

- Shipped binary does not match the source: lib/webdsp_c.wasm was last rebuilt 2017-03-29, before the 2017-04-02 brighten fix (commit 691a996), and exports _multiFilterFloat, which cpp/webdsp.cpp and compileWASM.sh no longer contain; rebuilding from source breaks the eight wrappers that call it (forest, romance, hippo, longhorn, moss, tingle, swamp, robbery), and the shipped brighten likely still has the doubled overflow check.
- sobelFilter declares int grayData[width\*height] on the stack; the shipped glue sets TOTAL_STACK to 5,242,880 bytes with an upward-growing fastcomp stack directly below the malloc heap and the binary imports no stack-overflow abort, so frames over about 1.31 M pixels (1920x1080 needs 8.3 MB) silently overwrite the heap that holds the input frame.
- Every wrapper calls _free(mem) and then returns HEAPU8/HEAPF32.subarray(mem, ...), a view of freed memory; it is only safe if the caller copies it before any other allocation, and multiFilter reads data[i + width\*4] past the end of the buffer on the last row.
- The global 'var Module = {}', fixed './lib/' fetch paths and a sed patch of the glue's 'else{doRun()}' string mean it clashes with any other Emscripten module on the page and cannot be rebuilt with a current Emscripten without rework.

## Known shortcomings

- No numbers in the repo (tier D); the baseline is its own JavaScript fallback with 8 fallback filters not matched to the C++ code; built with BINARYEN_IMPRECISE; the InfoWorld 2017 "at least 200 percent" quote is a snippet only; LICENSE says MIT, package.json ISC. Last commit 2017-06-05.
- Issue #25: users measured WASM 10-99% slower than the JS fallback on most filters (Chrome 61-63, Firefox); only Sobel (10-20x) and blur (50-100%) were faster; no maintainer reply. Correctness bugs: lib/webdsp_c.wasm was last built 2017-03-29, predates the brighten fix 691a996 and exports _multiFilterFloat, which cpp/webdsp.cpp no longer contains, so a rebuild from source breaks 8 filters; sobelFilter's int[w\*h] VLA on a 5 MB TOTAL_STACK has no overflow check, so a 1080p frame overruns the heap; wrappers return HEAP views after _free; the demo harness passes canvas.clientWidth as the image width; the README demo link tiny.cc/webdsp is now affiliate spam (#29).

## Caveats and trade-offs

Tier D: no benchmark, no numbers, no hardware in the repository. Only the qualitative README statement above. A WebSearch snippet (snippet only; infoworld.com was unreachable) of an InfoWorld article by Paul Krill dated 2017-04-04 quotes co-developer Deep Pulusani: 'In our performance tests, which you can demo here, we were able to surpass JavaScript performance by at least 200 percent', with no workload, browser, hardware or method. The baseline is the package's own JS fallback, not an independent JS library and not a native build, and the README's TODO says the JS fallbacks for underground, rooster, mist, kaleidoscope, bacteria, hulk edge, ghost and twisted are not yet matched to their C++ counterparts, so those filters would not compute the same result. Built with -s BINARYEN_IMPRECISE=1 (imprecise float-to-int conversions). LICENSE file is MIT while package.json says ISC (both OSI). Last commit 2017-06-05, so abandoned; it targets the 2017 Emscripten/Binaryen toolchain. 1.5k stars, 112 forks.

Early (2018 era) WebAssembly module loaded by fetch, so it needs an HTTP server; image data must be copied between JS and WASM memory on each call. README TODO notes that several JS fallback filters (underground, rooster, mist, kaleidoscope, bacteria, hulk edge, ghost, twisted) are not yet matched with their C++ versions, so the two paths are not equivalent for those filters.

## Maintenance

Abandoned since 2017-06-05 (open PR #23 and issues #24-#29 unanswered); MIT LICENSE file versus ISC in package.json, small enough to read in minutes, but treat it as a historical example rather than a library, and do not follow the README demo link.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now D.
- **Tier reason:** The repository has no benchmark code or numbers; the README has only the qualitative statement that convolution and edge-detection filters 'will run very slowly or hang the browser completely without WebAssembly support', and test/test.js is a page-load smoke test. A press snippet quotes a developer figure (see notes) but the article could not be opened, so D stays.
- **Verifier notes:** Confirmed as a notable D entry (1.5k stars); repository has no measurement. Possible lift to C only if the InfoWorld 2017-04-04 article can be opened to confirm the developer's 'at least 200 percent' claim (seen as a search snippet only). Shortcomings to record: no numbers, self-baseline JS fallback with 8 filters not matched to the C++ code, BINARYEN_IMPRECISE build, abandoned since 2017, MIT vs ISC licence mismatch in package.json.
- **Fields the verifier corrected:** `compiler_and_flags`, `last_commit`, `maintenance_status`, `caveats`
- **Shortcomings recorded by:** verifier batch-98 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/shamadee/web-dsp>
  - <https://github.com/shamadee/web-dsp/commits/master>
  - <https://github.com/shamadee/web-dsp/tree/master/test>
  - <https://github.com/shamadee/web-dsp-demo>
  - <https://raw.githubusercontent.com/shamadee/web-dsp/HEAD/README.md>
  - <https://raw.githubusercontent.com/shamadee/web-dsp/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/shamadee/web-dsp/HEAD/test/test.js>
  - <https://raw.githubusercontent.com/shamadee/web-dsp/HEAD/compile.js>
  - <https://raw.githubusercontent.com/shamadee/web-dsp/HEAD/package.json>
  - <https://raw.githubusercontent.com/shamadee/web-dsp/HEAD/cpp/compileWASM.sh>
- **Sources the enricher read:**
  - <https://github.com/shamadee/web-dsp>
  - <https://raw.githubusercontent.com/shamadee/web-dsp/HEAD/README.md>
  - <https://raw.githubusercontent.com/shamadee/web-dsp/HEAD/package.json>
  - <https://raw.githubusercontent.com/shamadee/web-dsp/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/shamadee/web-dsp/HEAD/cpp/webdsp.cpp>
  - <https://raw.githubusercontent.com/shamadee/web-dsp/HEAD/cpp/compileWASM.sh>
  - <https://raw.githubusercontent.com/shamadee/web-dsp/HEAD/cpp/compileWASM.bat>
  - <https://raw.githubusercontent.com/shamadee/web-dsp/HEAD/compile.js>
  - <https://raw.githubusercontent.com/shamadee/web-dsp/HEAD/lib/webdsp.js>
  - <https://raw.githubusercontent.com/shamadee/web-dsp/HEAD/lib/webdsp_polyfill.js>
  - <https://raw.githubusercontent.com/shamadee/web-dsp/HEAD/lib/webdsp_c.js>
  - <https://raw.githubusercontent.com/shamadee/web-dsp/HEAD/lib/webdsp_c.wasm>
  - <https://raw.githubusercontent.com/shamadee/web-dsp/HEAD/test/test.js>
  - <https://raw.githubusercontent.com/shamadee/web-dsp/HEAD/test/test.cpp>
  - <https://raw.githubusercontent.com/shamadee/web-dsp/HEAD/bin/get-dsp.js>
  - <https://github.com/shamadee/web-dsp/issues?q=is%3Aissue>
  - <https://github.com/shamadee/web-dsp/issues/25>
  - <https://github.com/shamadee/web-dsp/issues/28>
  - <https://github.com/shamadee/web-dsp/issues/29>
  - <https://github.com/shamadee/web-dsp/pulls?q=is%3Apr>
  - <https://github.com/shamadee/web-dsp/commits/master>
  - <https://github.com/shamadee/web-dsp/commits/master/cpp/webdsp.cpp>
  - <https://github.com/shamadee/web-dsp/commits/master/lib/webdsp_c.wasm>
  - <https://github.com/shamadee/web-dsp/commit/691a996>
  - <https://github.com/shamadee/web-dsp-demo>
  - <https://raw.githubusercontent.com/shamadee/web-dsp-demo/HEAD/demo.js>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/shamadee/web-dsp`) · [data/wave13/enrich/raw/github_com_shamadee_web_dsp.json](../../../data/wave13/enrich/raw/github_com_shamadee_web_dsp.json) (enrichment confidence 0.75)

</details>
