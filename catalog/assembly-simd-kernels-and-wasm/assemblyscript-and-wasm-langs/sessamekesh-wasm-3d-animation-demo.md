# WebAssembly vs JavaScript Animation Demo (sessamekesh/wasm-3d-animation-demo)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MIT` · 🔴 abandoned

> 2017 WebGL demo running one naive skeletal-animation system in TypeScript and in Emscripten-compiled C++/Wasm; Wasm hit 60 FPS where JS managed 5-10.

| | |
|---|---|
| **Beats** | TypeScript skeletal-animation implementation running in the browser JavaScript engine |
| **Claimed result** | JavaScript around 5-10 FPS vs WebAssembly an easy 60 FPS with 15 characters. |
| **Workload** | CPU-bound skeletal animation of 15 characters on screen, nearly identical logic in TypeScript and C++ compiled to WebAssembly with Emscripten, WebGL rendering. |
| **Metric** | throughput |
| **Hardware** | third-generation Intel i3 CPU, GTX 980 Ti GPU |
| **Compiler and flags** | emcc ./cc/naivewasmanimationmanager.cc -O3 -s SIDE_MODULE=1 -s WASM=1 (makefile), Emscripten sdk-incoming-64bit with binaryen-master (2017); TypeScript ^2.2 bundled with webpack 2; browser and engine version not stated |
| **Adoption** | 226 stars |
| **Last commit** | 2017-04-25 |
| **Links** | [repository](https://github.com/sessamekesh/wasm-3d-animation-demo) · [benchmark](https://github.com/sessamekesh/wasm-3d-animation-demo) |

## Verdict

The author watched the demo on one PC (third-generation Intel i3, GTX 980 Ti, browser and version not named, spring 2017): with 15 characters the TypeScript manager gave about 5-10 FPS and the emcc -O3 Wasm manager an easy 60 FPS, at least 6-12x per frame (derived from page data). 60 FPS is the requestAnimationFrame vsync cap and the frame time also includes WebGL rendering, so the true animation-only ratio is unknown, and no timing log exists in the repo.

## Use it when

- As a reading example of moving a whole CPU-bound per-frame subsystem into Wasm: serialize data into the Wasm heap once, make one export call per mesh per frame, read results through a zero-copy typed-array view
- Teaching or presenting JS vs Wasm, since the same naive algorithm sits side by side in ts/model/naivejsanimationmanager.ts and cc/naivewasmanimationmanager.cc
- As a starting skeleton for keyframe sampling, quaternion slerp and bone-hierarchy evaluation in C++ for the browser, after fixing the keyframe search noted under gotchas

## Skip it when

- As a production animation runtime: no asset pipeline, character assets are not in the repo (no redistribution rights), and every bone recomputes its full parent chain each call (bones x depth work, no cached hierarchy)
- As evidence of today's JS-vs-Wasm gap: the numbers are 2017 browsers, unnamed engine, frames per second capped at 60 by requestAnimationFrame, and no recorded timings
- When the fair baseline is optimized JavaScript: package.json and the URL parser name 'speedyjs'/'speedywasm' and an 'optimized JavaScript' system, but none was ever implemented, so pre-allocated typed-array JS was never measured
- With a current Emscripten without rewriting the hand-built loader (see gotchas)

## How it is fast

Nothing algorithmic: both managers sample keyframes by binary search, slerp/lerp position, rotation and scale, and recompute every bone's whole parent chain recursively. The Wasm gain comes from AOT-compiled C++ (emcc -O3) working on packed float32 structs and stack temporaries with no garbage collection, against TypeScript that allocates new Mat4/Vec3/Float32Array objects per bone per call and looks bones up by string in Maps. Model and animation data stay resident in the Wasm heap, so no per-frame copy is needed.

## Compared with alternatives

Pick it over wasm-perf (Emscripten SIMD matrix multiply vs Node, timed table) or Speedy.js (TypeScript subset compiled to Wasm, Chrome 58 charts) when you want an end-to-end browser app that keeps a whole subsystem's data in the Wasm heap; for actual numbers those siblings are better evidence.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Emscripten (2017 'incoming' branch with binaryen-master, SIDE_MODULE build), TypeScript ^2.2, webpack 2 with ts-loader, stats.js and dat.gui served from webroot; character model and animation files you must supply yourself |
| **Minimum toolchain** | Emscripten 2017 incoming/fastcomp (side-module ABI before 1.38.18), TypeScript 2.2 targeting ES6, a browser with WebAssembly MVP and WebGL 1 |
| **Platforms** | web browsers with WebAssembly and WebGL |
| **Thread safety** | not documented; single-threaded main-thread demo, and the Wasm manager reuses one result buffer for every call |
| **Drop-in for the baseline** | no |

## Gotchas

- The keyframe binary search (the same code in TypeScript and C++) returns a stale index when the loop ends on low == high: with keyframe times 0..7 and a sample at 2.5 it interpolates keyframes 1 and 2 with ratio 1.5, extrapolating the pose. The C++ copy also does `high = idx - 1u` on uint32, so when the search probes index 0 with the sample at the first keyframe time (for example a two-keyframe channel sampled at its start) it wraps to 0xFFFFFFFF and keeps searching out of bounds, while the TypeScript copy exits at -1. Both sides do the same work, so the speed comparison stays like-for-like, but some poses are wrong.
- The data structures differ in both directions, not only in Wasm's favour: TypeScript allocates per bone and uses string-keyed Map lookups, while C++ finds each static and animated bone by a linear scan over all bones and copies the StaticBone (with its Mat4) by value. The Wasm module also imports sinf, acosf and fmodf from JavaScript (Math.sin, Math.acos, a % b), so every slerp and keyframe wrap crosses the Wasm-JS boundary.
- The loader hand-builds the 2017 side-module imports (memoryBase, tableBase, underscore-prefixed _sinf/_acosf/_fmodf), uses a bump allocator from 1 MB with a guessed 1 MB 'stack' (the code says it will not fail gracefully on overflow) and fixes memory at 512 pages (32 MB) with no growth. Emscripten 1.38.18 (Nov 2018) renamed memoryBase/tableBase to __memory_base/__table_base.
- Every Wasm result is a Float32Array view at the same heap address, so it is valid only until the next call; the demo renders each one immediately, so this holds there. The page's Stats.js 'Anim' panel times getAnimationData with performance.now() each frame, but the README reports only the FPS observation.

## Known shortcomings

- Anecdotal frames-per-second on one machine with a 60 FPS vsync cap hiding the real ratio; the JavaScript side allocates objects per frame and uses string-keyed Map lookups.
- Correctness bug in both the TypeScript and C++ managers: the keyframe binary search returns a stale index, so some poses extrapolate (ratio 1.5 at sample 2.5 over keyframes 0..7); the C++ copy also wraps high = idx - 1u to 0xFFFFFFFF and reads out of bounds when it probes index 0 at the first keyframe time; the same work runs on both sides, so the comparison stays like-for-like but the poses are wrong. The asymmetry cuts both ways: C++ finds bones by linear scan and calls JS Math.sin/acos/fmod through imports. The promised 'speedyjs' optimized-JS baseline was never written; the loader is tied to pre-1.38.18 Emscripten (memoryBase); the hosted demo returned HTTP 503.

## Caveats and trade-offs

Informal one-machine observation from a 2017 browser/engine generation with no timing harness or FPS log in the repo; 60 FPS is probably vsync-capped so the true gap is unknown. Both managers use the same naive algorithm (per-bone recursive recomputation of the parent chain, binary keyframe search; the Apr 2017 linear-to-binary search fix was applied to both), but the TypeScript side looks bones up by string name in Maps and allocates new Mat4/Vec3/Float32Array objects per bone per frame, while the C++ side uses integer bone IDs and stack temporaries, so part of the gap is data layout and GC pressure rather than the engine. The author calls the logic only 'nearly' identical. MIT licence is in license.md. Listed on awesome-wasm. [retier] Informal one-machine observation from a 2017 browser and engine generation with no timing harness or FPS log in the repo; 60 FPS is probably vsync-capped, so the true gap is unknown (the page's Stats.js 'Anim' panel times getAnimationData per frame but the README reports only FPS). Both managers use the same naive algorithm, and both share a correctness bug: the keyframe binary search returns a stale index when the loop ends on low == high (keyframe times 0..7 sampled at 2.5 interpolate keyframes 1 and 2 with ratio 1.5, extrapolating the pose), and the C++ copy also wraps high = idx - 1u to 0xFFFFFFFF and keeps searching out of bounds when it probes index 0 at the first keyframe time; the same work runs on both sides, so the poses are wrong rather than the comparison skewed. Data layouts differ in both directions: TypeScript allocates per bone per frame and uses string-keyed Map lookups, while C++ finds each bone by a linear scan, copies StaticBone by value, and imports sinf, acosf and fmodf from JavaScript, so every slerp and keyframe wrap crosses the Wasm-JS boundary. The promised 'speedyjs' optimized-JS baseline was never written. The loader is tied to pre-1.38.18 Emscripten (memoryBase/tableBase), uses a bump allocator with a guessed 1 MB stack and fixed 32 MB memory; every Wasm result is a Float32Array view valid only until the next call. The hosted demo returned HTTP 503.

Needs an Emscripten toolchain and a Wasm-capable browser; assets are not included in the repo.

## Maintenance

Abandoned since April 2017 (26 commits; only 2 issues, both closed); MIT-licensed, but it cannot run as shipped (no assets, 2017 Emscripten glue), and the hosted S3 demo returned HTTP 503 when fetched on 2026-10-12, so it is useful only as code to read.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party informal observation in the README (15 characters: about 5-10 FPS with the TypeScript manager vs an easy 60 FPS with the C++/Wasm manager on a third-gen i3); the code and emcc flags are public but there is no timing harness, no exact CPU model and no browser version, so C.
- **Retiered** C to D: Enricher: the only evidence is a 2017 FPS observation with no harness or log, the 60 FPS side is probably vsync-capped, both animation managers share a stale-index keyframe bug (the C++ copy also reads out of bounds), and the data layouts differ in both directions. Directional claim with no valid measurement: C to D.
- **Verifier notes:** README sentence confirmed; 226 stars, 23 forks, MIT (license.md), 26 commits, last commit 2017-04-25 (abandoned). Main shortcomings: anecdotal FPS from one machine, vsync cap hides the real ratio, JS side allocates per frame and uses string-keyed Map lookups.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-55 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/sessamekesh/wasm-3d-animation-demo>
  - <https://github.com/sessamekesh/wasm-3d-animation-demo/commits>
  - <https://github.com/sessamekesh/wasm-3d-animation-demo/tree/master/ts>
  - <https://github.com/sessamekesh/wasm-3d-animation-demo/tree/master/ts/model>
  - <https://github.com/sessamekesh/wasm-3d-animation-demo/tree/master/cc>
  - <https://raw.githubusercontent.com/sessamekesh/wasm-3d-animation-demo/HEAD/README.md>
  - <https://raw.githubusercontent.com/sessamekesh/wasm-3d-animation-demo/HEAD/license.md>
  - <https://raw.githubusercontent.com/sessamekesh/wasm-3d-animation-demo/HEAD/makefile>
  - <https://raw.githubusercontent.com/sessamekesh/wasm-3d-animation-demo/HEAD/package.json>
  - <https://raw.githubusercontent.com/sessamekesh/wasm-3d-animation-demo/HEAD/cc/naivewasmanimationmanager.cc>
  - <https://raw.githubusercontent.com/sessamekesh/wasm-3d-animation-demo/HEAD/ts/model/naivejsanimationmanager.ts>
  - <https://raw.githubusercontent.com/mbasso/awesome-wasm/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/sessamekesh/wasm-3d-animation-demo>
  - <https://github.com/sessamekesh/wasm-3d-animation-demo/commits/master>
  - <https://github.com/sessamekesh/wasm-3d-animation-demo/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/sessamekesh/wasm-3d-animation-demo/HEAD/README.md>
  - <https://raw.githubusercontent.com/sessamekesh/wasm-3d-animation-demo/HEAD/license.md>
  - <https://raw.githubusercontent.com/sessamekesh/wasm-3d-animation-demo/HEAD/makefile>
  - <https://raw.githubusercontent.com/sessamekesh/wasm-3d-animation-demo/HEAD/package.json>
  - <https://raw.githubusercontent.com/sessamekesh/wasm-3d-animation-demo/HEAD/tsconfig.json>
  - <https://raw.githubusercontent.com/sessamekesh/wasm-3d-animation-demo/HEAD/cc/naivewasmanimationmanager.cc>
  - <https://raw.githubusercontent.com/sessamekesh/wasm-3d-animation-demo/HEAD/cc/include/math.h>
  - <https://raw.githubusercontent.com/sessamekesh/wasm-3d-animation-demo/HEAD/ts/model/naivejsanimationmanager.ts>
  - <https://raw.githubusercontent.com/sessamekesh/wasm-3d-animation-demo/HEAD/ts/model/naivewasmanimationmanager.ts>
  - <https://raw.githubusercontent.com/sessamekesh/wasm-3d-animation-demo/HEAD/ts/model/animation.ts>
  - <https://raw.githubusercontent.com/sessamekesh/wasm-3d-animation-demo/HEAD/ts/model/animationmanager.ts>
  - <https://raw.githubusercontent.com/sessamekesh/wasm-3d-animation-demo/HEAD/ts/model/dancingentity.ts>
  - <https://raw.githubusercontent.com/sessamekesh/wasm-3d-animation-demo/HEAD/ts/math/mat4.ts>
  - <https://raw.githubusercontent.com/sessamekesh/wasm-3d-animation-demo/HEAD/ts/demoapp.ts>
  - <https://raw.githubusercontent.com/sessamekesh/wasm-3d-animation-demo/HEAD/webroot/index.html>
  - <https://raw.githubusercontent.com/emscripten-core/emscripten/main/ChangeLog.md>
  - <http://aws-website-webassemblyskeletalanimation-ffaza.s3-website-us-east-1.amazonaws.com/>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/sessamekesh/wasm-3d-animation-demo`) · [data/wave13/enrich/raw/github_com_sessamekesh_wasm_3d_animation_demo.json](../../../data/wave13/enrich/raw/github_com_sessamekesh_wasm_3d_animation_demo.json) (enrichment confidence 0.75)

</details>
