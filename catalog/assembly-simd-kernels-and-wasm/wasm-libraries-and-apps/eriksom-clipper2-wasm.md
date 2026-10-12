# Clipper2-WASM (clipper2-wasm)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++ (Clipper2) compiled to WebAssembly, JavaScript/TypeScript API` · `BSL-1.0` · 🟢 active

> Emscripten/Embind build of Angus Johnson's Clipper2 2.0.1; boolean ops 1.15-1.69x faster than Clipper1 WASM (js-angusj-clipper).

| | |
|---|---|
| **Beats** | Clipper1 WASM (js-angusj-clipper) |
| **Claimed result** | README screenshot (Apple M2 Pro, 5,000 ops x 5,000 points): intersection 1962.1 ms (Clipper1) vs 1163.3 ms (Clipper2), shown as +40.71%; union 2434.2 vs 1817.4 ms (+25.34%); difference 2122.5 vs 1472.8 ms (+30.61%); xor 2609.0 vs 2278.4 ms (+12.67%). The percentages are time reductions relative to Clipper1, i.e. 1.69x, 1.34x, 1.44x and 1.15x faster (derived from page data). |
| **Workload** | Boolean operations (intersection, union, difference, xor) over two intersecting circle paths of 5,000 points each, repeated 5,000 times in the browser benchmark page. |
| **Metric** | throughput |
| **Hardware** | Apple M2 Pro (from the README heading); browser not stated |
| **Compiler and flags** | Emscripten em++ (version not stated) with -O3 -s DISABLE_EXCEPTION_CATCHING=1 --bind -s MODULARIZE=1 -s WASM_BIGINT -s ALLOW_MEMORY_GROWTH=1 -DUSINGZ (clipper2-wasm/compile-wasm.sh prod); Clipper2 static library built with emcmake cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS_RELEASE=-O3 -DCLIPPER2_HI_PRECISION=OFF (README.dev.md). Baseline js-angusj-clipper@1.3.1 loaded from jsdelivr as shipped (its build flags not stated). |
| **Adoption** | 112 stars; npm package clipper2-wasm |
| **Last commit** | 2026-05-18 |
| **Links** | [repository](https://github.com/ErikSom/Clipper2-WASM) · [benchmark](https://github.com/ErikSom/Clipper2-WASM) |

## Verdict

A single run of the repo's browser page (5,000 ops on two 5,000-point integer circles, EvenOdd fill) on an Apple M2 Pro, browser and Emscripten version unstated, measured Clipper2-WASM against js-angusj-clipper 1.3.1 (Clipper1 compiled to wasm, loaded from jsDelivr): intersection 1962.1 vs 1163.3 ms, union 2434.2 vs 1817.4, difference 2122.5 vs 1472.8 and xor 2609.0 vs 2278.4 ms, i.e. 1.69x, 1.34x, 1.44x and 1.15x (derived from page data), with Clipper1's per-call JS-to-wasm conversion inside its timer and Clipper2's outside.

## Use it when

- Browser, worker or Node code that runs many 2D polygon boolean operations (intersection, union, difference, xor) on the same or slowly changing geometry, where inputs can stay in Paths64 between calls.
- Projects on js-angusj-clipper or a pure-JS Clipper port that want Clipper2 features: PolyTree output with isHole, RectClip, Minkowski, SimplifyPaths, constrained Delaunay triangulation, Z values carried on points.
- Polygon offsetting (InflatePaths) and rectangle clipping of large path sets for CAD, CNC, mapping or game tooling in JavaScript.
- Apps that need exact integer (Paths64) or decimal-precision (PathsD) geometry from the reference Clipper2 implementation rather than a reimplementation.

## Skip it when

- One-off clips of small polygons coming from JavaScript objects: every call then pays MakePath64 (a BigInt per coordinate) and readback through view(), which the benchmark does not time; issue #3 'MakePath64 very slow' was closed as not planned.
- Code that cannot manage manual lifetimes: every Path64/Paths64/Clipper64 and every get(i) result needs delete(); a wasm memory leak in the bindings (issue #11) was only fixed in May 2026 (PR #13), and wasm memory grows (ALLOW_MEMORY_GROWTH) without shrinking.
- Code that expects catchable errors: the production build sets DISABLE_EXCEPTION_CATCHING=1, so a C++ exception (for example Path64.assign with a bad length) cannot be caught from JavaScript.
- Bundle-size-sensitive pages: clipper2z.wasm is 213,643 bytes plus a 54 KB glue file, and the utils module adds another 237 KB wasm.
- Teams wanting a measured speedup over native Clipper2 or a pure-JS library: neither is benchmarked; the only number is a single browser run against Clipper1 wasm.

## How it is fast

The gain is Clipper2's own: its boolean, offsetting and triangulation engine is the author's rewrite of Clipper1 (which js-angusj-clipper wraps), compiled at -O3 by Emscripten; nothing wasm-specific is added (no SIMD, threads or LTO flags in compile-wasm.sh or README.dev.md). The API lets callers keep geometry resident in wasm memory as Paths64 across many operations and reuse an output container, so repeated clips skip the per-call copy of JavaScript {x,y} objects into the heap and back that js-angusj-clipper's clipToPaths performs. Path construction and readback use typed-array views (one BigInt64Array or Float64Array set per path) rather than per-point binding calls.

## Compared with alternatives

No other 2D polygon-clipping library is catalogued in this category: brepkit does 3D B-rep booleans against OpenCASCADE wasm and contour-wasm computes isobands, so pick Clipper2-WASM whenever the job is 2D boolean operations, offsetting or triangulation in JavaScript.

## Integration

| | |
|---|---|
| **Form** | module (npm clipper2-wasm: Emscripten ES6 and UMD builds with .wasm files) |
| **Dependencies** | none at runtime (@types/emscripten is listed for typings); building needs Emscripten, CMake and the Clipper2 submodule |
| **Minimum toolchain** | JavaScript runtime with WebAssembly and BigInt64Array (WASM_BIGINT build); source build: Emscripten em++ (version not documented) with C++17 Clipper2 2.0.1 |
| **Platforms** | browsers, webviews, web workers and Node (ENVIRONMENT='web,webview,worker,node'); any CPU |
| **Thread safety** | not documented; single-threaded Emscripten build without pthreads, one module instance per realm or worker |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw (clipper1-vs-clipper2.html, testPolyOperation.js): the Clipper1 loop calls clipToPaths with JavaScript {x,y} arrays, which mallocs a Float64 heap buffer, writes 10,000 points, converts them to native paths and converts the result back to JS objects on every one of the 5,000 ops, while the Clipper2 inputs are built once with MakePath64 outside the timer and its output stays in a reused native Paths64 that is never read. The timed gap (about 160 us per op for intersection, derived from page data) therefore includes an unknown share of marshalling; the harness also never checks that the two libraries return the same polygons, runs each clip type once with no warm-up, and always runs Clipper1 first.
- The Clipper2 build is USINGZ-only (Point64 and PointD carry a z value, 24 bytes per point), and the view()/assign() helpers assume that layout; MakePath64 expects flat [x0, y0, x1, y1, ...] arrays and MakePathZ64 [x, y, z, ...].
- package.json 'types' points to dist/es/clipper2z.d.ts, which is not in the published 0.4.0 tarball; the declarations are at dist/clipper2z.d.ts, so import types from 'clipper2-wasm/dist/clipper2z' as the README example does. The README's 'Download lib' and 'Usage' links point to a CPP/clipper2-wasm path that returns 404.
- CreateClipper64(preserveCollinear) takes the flag that Clipper2 normally sets via a property; the benchmark passes false, matching js-angusj-clipper's default.

## Known shortcomings

- Compares against the Clipper1 wasm build, not the category baseline, with an asymmetric harness (Clipper1 marshals JavaScript points every operation, Clipper2 inputs are prebuilt); real gains 1.15-1.69x (derived); browser and emcc version unstated; numbers from a screenshot.
- Enricher: the Clipper1 timer covers malloc plus a 10,000-point write plus result conversion to JS on every op while Clipper2's MakePath64 (BigInt per coordinate; issue #3 'MakePath64 very slow' closed as not planned) runs outside the timer and its output is never read; no check that both libraries return the same polygons; single run with Clipper1 always first; USINGZ-only build (24-byte points), DISABLE_EXCEPTION_CATCHING=1 in production, package.json types path missing from the 0.4.0 tarball, README CPP/ links 404. Retiered to D.

## Caveats and trade-offs

Numbers exist only as a PNG screenshot in the README (checked; the four rows match). The comparison is Clipper2 against Clipper1, both as wasm, so the gain is mostly algorithmic, not wasm versus JS or native; the category's baselines (same library native, JS equivalent) are not measured, so the entry is off-baseline. Harness asymmetry in clipper1-vs-clipper2.html and testPolyOperation.js: the Clipper1 timed loop calls clipToPaths with plain JS {x,y} arrays, so every op marshals 2 x 5,000 input points into wasm and converts the result back to JS objects, while the Clipper2 inputs are converted to native Paths64 once before timing and the output stays in a native Paths64; part of the gap is therefore JS-wasm marshalling, not clipping. Single timed run per clip type, no warm-up, Clipper1 always runs first. Browser and Emscripten version not stated. Clipper2 itself (AngusJohnson/Clipper2, C++) is a separate project and is not listed.

Wasm module must be loaded and instantiated before use; objects created on the wasm side need explicit delete().

## Maintenance

Maintained in bursts (last commit and npm 0.4.0 on 2026-05-18 after a 2024-2026 gap; 112 stars, 15 forks, five closed issues) and BSL-1.0 licensed, so it is copyable and the reference way to run Clipper2 in JavaScript, but treat the speedup as first-party and measure your own marshalling cost.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party README screenshot (Apple M2 Pro) of the public harness clipper2-wasm/examples/benchmark/clipper1-vs-clipper2.html; the four rows match the record exactly. Emscripten version and browser are not stated, and the harness is asymmetric (below), so it stays C.
- **Retiered** C to D: Enricher (2026-10-12): asymmetric harness with no valid measurement. The Clipper1 timer includes malloc, a 10,000-point write and result conversion to JS on every operation while Clipper2's MakePath64 conversion (BigInt per coordinate) runs outside the timer and its output is never read; no check that both libraries return the same polygons; single run with Clipper1 always first.
- **Verifier notes:** Numbers verified against the screenshot (fetched via its signed asset URL) and the harness source read. Main shortcomings: off-baseline (Clipper1 wasm, no native or JS comparison) and an asymmetric harness that charges JS-to-wasm conversion to Clipper1 only; last commit 2026-05-18, BSL-1.0, 112 stars, npm clipper2-wasm 0.4.0.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-84 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/ErikSom/Clipper2-WASM>
  - <https://raw.githubusercontent.com/ErikSom/Clipper2-WASM/HEAD/README.md>
  - <https://github.com/user-attachments/assets/59543ebe-e501-46f6-b1cc-c2f9f32d5b18>
  - <https://github.com/ErikSom/Clipper2-WASM/tree/main/clipper2-wasm/examples/benchmark>
  - <https://raw.githubusercontent.com/ErikSom/Clipper2-WASM/main/clipper2-wasm/examples/benchmark/clipper1-vs-clipper2.html>
  - <https://raw.githubusercontent.com/ErikSom/Clipper2-WASM/main/clipper2-wasm/examples/benchmark/testPolyOperation.js>
  - <https://raw.githubusercontent.com/ErikSom/Clipper2-WASM/main/clipper2-wasm/examples/benchmark/circlePath.js>
  - <https://raw.githubusercontent.com/ErikSom/Clipper2-WASM/main/README.dev.md>
  - <https://raw.githubusercontent.com/ErikSom/Clipper2-WASM/main/clipper2-wasm/compile-wasm.sh>
  - <https://raw.githubusercontent.com/ErikSom/Clipper2-WASM/main/clipper2-wasm/package.json>
  - <https://github.com/ErikSom/Clipper2-WASM/commits>
  - <https://registry.npmjs.org/clipper2-wasm>
- **Sources the enricher read:**
  - <https://github.com/ErikSom/Clipper2-WASM>
  - <https://github.com/ErikSom/Clipper2-WASM/commits/main>
  - <https://github.com/ErikSom/Clipper2-WASM/issues?q=is%3Aissue>
  - <https://github.com/ErikSom/Clipper2-WASM/issues/3>
  - <https://github.com/ErikSom/Clipper2-WASM/issues/11>
  - <https://github.com/ErikSom/Clipper2-WASM/tree/main/clipper2-wasm/dist>
  - <https://raw.githubusercontent.com/ErikSom/Clipper2-WASM/main/README.md>
  - <https://raw.githubusercontent.com/ErikSom/Clipper2-WASM/main/README.dev.md>
  - <https://raw.githubusercontent.com/ErikSom/Clipper2-WASM/main/.gitmodules>
  - <https://raw.githubusercontent.com/ErikSom/Clipper2-WASM/main/LICENSE>
  - <https://raw.githubusercontent.com/ErikSom/Clipper2-WASM/main/clipper2-wasm/compile-wasm.sh>
  - <https://raw.githubusercontent.com/ErikSom/Clipper2-WASM/main/clipper2-wasm/package.json>
  - <https://raw.githubusercontent.com/ErikSom/Clipper2-WASM/main/clipper2-wasm/clipper.bindings.cpp>
  - <https://raw.githubusercontent.com/ErikSom/Clipper2-WASM/main/clipper2-wasm/glue-stub-z.js>
  - <https://raw.githubusercontent.com/ErikSom/Clipper2-WASM/main/clipper2-wasm/examples/benchmark/clipper1-vs-clipper2.html>
  - <https://raw.githubusercontent.com/ErikSom/Clipper2-WASM/main/clipper2-wasm/examples/benchmark/testPolyOperation.js>
  - <https://raw.githubusercontent.com/ErikSom/Clipper2-WASM/main/clipper2-wasm/examples/benchmark/circlePath.js>
  - <https://raw.githubusercontent.com/ErikSom/Clipper2-WASM/main/clipper2-wasm/dist/es/clipper2z.wasm>
  - <https://registry.npmjs.org/clipper2-wasm>
  - <https://registry.npmjs.org/clipper2-wasm/-/clipper2-wasm-0.4.0.tgz>
  - <https://raw.githubusercontent.com/xaviergonz/js-angusj-clipper/master/README.md>
  - <https://raw.githubusercontent.com/xaviergonz/js-angusj-clipper/master/src/clipFunctions.ts>
  - <https://raw.githubusercontent.com/xaviergonz/js-angusj-clipper/master/src/native/PathToNativePath.ts>
  - <https://raw.githubusercontent.com/AngusJohnson/Clipper2/main/README.md>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/eriksom/clipper2-wasm`) · [data/wave13/enrich/raw/github_com_eriksom_clipper2_wasm.json](../../../data/wave13/enrich/raw/github_com_eriksom_clipper2_wasm.json) (enrichment confidence 0.7)

</details>
