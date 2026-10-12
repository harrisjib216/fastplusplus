# wasm-fun (hand-written WebAssembly text algorithms)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `WebAssembly text format (WAT)` · `Unlicense` · 🔴 abandoned

> Hand-written WebAssembly text (WAT) image and utility algorithms; claims skeleton tracing beats an Emscripten build and vanilla JS.

| | |
|---|---|
| **Beats** | LingDong-/skeleton-tracing's C++ version compiled to WebAssembly with Emscripten (wasm/compile.sh: emcc -O3 --closure 1, WebIDL glue, SINGLE_FILE=1, ALLOW_MEMORY_GROWTH=1) and its vanilla JavaScript implementation |
| **Claimed result** | README, traceskeleton.wat only: '\~300% faster than the version complied with emscripten (and \~10x smaller), \~500% faster than vanilla Javascript' (approximate, no figures, no harness; no claims for the other modules) |
| **Workload** | traceskeleton: topological skeleton of a binary image returned as polylines (includes its own malloc and linked list); other modules are thinning, distance transform, contour finding, maze generation |
| **Metric** | throughput |
| **Adoption** | 83 stars |
| **Last commit** | 2020-08-26 |
| **Links** | [repository](https://github.com/LingDong-/wasm-fun) · [benchmark](https://github.com/LingDong-/wasm-fun) |

## Verdict

The README says traceskeleton.wat is '\~300% faster than the version complied with emscripten (and \~10x smaller), \~500% faster than vanilla Javascript', with no engine, hardware, Emscripten version, input or harness; the comparator is skeleton-tracing's -O3, closure-compiled, WebIDL-glued Emscripten build and its vanilla JS port. Nothing was re-measured, and the repo's only timing code covers the WAT version alone and excludes thinning and I/O that the Emscripten path includes.

## Use it when

- A browser or Node page that needs binary-image skeleton tracing to polylines and wants a sub-kilobyte-class module (README: average binary about 900 bytes) instead of a SINGLE_FILE Emscripten bundle.
- Small images where per-call overhead of the Emscripten build (string-encoded input, text-serialised polylines and rects parsed back with split/parseInt) would dominate.
- Hosts with no build toolchain: the prebuilt .wasm files have no imports and can be instantiated directly.
- Learning or teaching hand-written WAT: the sources are heavily commented and cite the papers they implement.

## Skip it when

- When you need a measured speedup: the only claim is one approximate README sentence with no harness, engine, hardware or input, and the repo times nothing but its own version.
- Large images or skeletons with many points: every malloc scans the heap from address 0 (first-fit implicit free list) to place 12-byte point and 20-byte polyline nodes, so allocation cost grows with live nodes, unlike Emscripten's default allocator.
- Native code: skeleton-tracing's C99 version (pthreads) is the reference implementation and its README puts it at 0.76 ms per run on a 300x149 image.
- Concurrent use or several images per instance: all state (W, H, image pointer, heap) is module-global.
- Projects that need maintenance or tests: 9 commits, last on 2020-08-26, only demo pages under tests/.

## How it is fast

The module carries no Emscripten runtime, WebIDL glue or string marshalling: the image lives as a byte array in linear memory and results stay as a linked list that JS walks through accessor exports. Tracing is the skeleton-tracing algorithm (recursive split of the image along the row or column of least resistance into 10-pixel chunks, a border walk of each chunk, then fragment merging) hand-translated to WAT with an inline implicit-free-list first-fit malloc. No benchmark isolates which of these choices produces the claimed gain.

## Compared with alternatives

No sibling in hand-written-asm-kernels targets WebAssembly: FastMemcpy, FP-ASM, cespare/xxhash and the rest are native x86, Arm or Go assembly with published harnesses. Pick wasm-fun only when the code must run in a WebAssembly host and binary size matters; for native targets those siblings carry far better evidence.

## Integration

| | |
|---|---|
| **Form** | source-drop (.wat sources plus prebuilt .wasm modules) |
| **Dependencies** | none at runtime; wabt wat2wasm to reassemble (compile.py calls ./wat2wasm) |
| **Minimum toolchain** | any WebAssembly 1.0 engine (traceskeleton exports mutable globals MAX_ITER and CHUNK_SIZE); wabt to rebuild |
| **Platforms** | any WebAssembly host (browsers, Node.js); wasm32 linear memory starting at one 64 KiB page and grown on demand |
| **Thread safety** | not documented; module-global state and a single heap make one instance usable by one caller at a time |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind the 300% claim: skeleton-tracing's Emscripten build exposes only trace(DOMString img, w, h), which in one call runs Zhang-Suen thinning, tracing with SAVE_RECTS=1, std::to_string serialisation of polylines and rects, while its fromImageData/fromCanvas wrappers build the input string pixel by pixel and parse the output with split/parseInt; the only WAT timing in this repo (tests/traceskeleton.html) runs thinning_zs() and the im_set fill before starting a single Date() timer around trace_skeleton() and reads results after stopping it. A comparison through the public Emscripten API therefore timed thinning and marshalling on one side only; the method was never published. The vanilla JS library does expose traceSkeleton separately, but skeleton-tracing's own table puts vanilla JS (Node v12.10) at 38% of native C -O3, so a 5-6x win over it would make the WAT about twice as fast as native C, which points to non-comparable runs (one cold run, 1 ms Date() resolution, different input: horse.png is 400x328).
- Licence mismatch: the repo LICENSE is the Unlicense and most .wat headers say Public Domain, but traceskeleton.wat is headed 'MIT License' and ends with the full MIT text (it ports MIT-licensed skeleton-tracing), so keep that notice when copying it.
- setup() mallocs a new W\*H image on every call without freeing the old one and does not zero it, so every pixel must be written with im_set; extend() drops the memory.grow result, so a failed grow traps on an out-of-bounds store instead of returning NULL.
- thinning_zs stops as soon as either Zhang-Suen sub-iteration changes nothing (diff &= ...), not when a full pass changes nothing; the quirk is inherited from skeleton-tracing's C, C++ and JS versions, so output matches upstream but thinning can end early.

## Known shortcomings

- A single README sentence with no harness; the Emscripten comparator is a skeleton-tracing -O3 build called through WebIDL glue. Unlicense. Abandoned 2020-08-26.
- Harness flaw likely behind the 300% claim: skeleton-tracing's Emscripten build exposes only trace(DOMString), which runs Zhang-Suen thinning, rect saving (SAVE_RECTS=1) and std::to_string serialisation in one call, and its JS wrappers parse the output with split/parseInt, while the only WAT timing (tests/traceskeleton.html) is one Date() run of trace_skeleton after thinning and the im_set fill; a 5-6x win over vanilla JS would put the WAT about 2x ahead of native C -O3 by upstream's 38% table, so the runs are probably not comparable. traceskeleton.wat carries an MIT notice under an Unlicense repo; the first-fit malloc scans the whole heap per allocation; setup() leaks the old image; the memory.grow result is dropped; thinning stops when either sub-iteration makes no change (inherited from upstream).

## Caveats and trade-offs

Single README sentence with no benchmark script, browser or engine, hardware, Emscripten version or input size. tests/traceskeleton.html only logs one Date()-based millisecond timing of trace_skeleton on assets/horse.png (thinning excluded), with no Emscripten or JS comparison in this repo. The Emscripten comparator in LingDong-/skeleton-tracing (wasm/compile.sh) is built at -O3 but goes through WebIDL-binder glue and closure-compiled JS, so the 300% may include JS marshalling overhead rather than kernel speed. skeleton-tracing's own Node v12.10 table puts its vanilla JS at 38% of native C -O3; taken at face value a 5-6x win over vanilla JS would put the WAT ahead of native C, so the runs behind the two claims are probably not comparable (different engine or input). '300% faster' is ambiguous (3x or 4x). Hand-written WAT may fit wasm-libraries-and-apps better than hand-written-asm-kernels. Unlicense (OSI-approved public-domain dedication) carries no patent grant. Last commit 2020-08-26. [retier] Single README sentence with no benchmark script, browser or engine, hardware, Emscripten version or input size. The Emscripten comparator in LingDong-/skeleton-tracing exposes only trace(DOMString img, w, h), which in one call runs Zhang-Suen thinning, tracing with SAVE_RECTS=1 and std::to_string serialisation of polylines and rects, while its fromImageData/fromCanvas wrappers build the input string pixel by pixel and parse the output with split/parseInt; the only WAT timing in this repo (tests/traceskeleton.html) runs thinning_zs() and the im_set fill before a single Date() timer around trace_skeleton() on assets/horse.png, with no Emscripten or JS comparison. skeleton-tracing's own Node v12.10 table puts its vanilla JS at 38% of native C -O3, so a 5-6x win over vanilla JS would put the WAT about 2x ahead of native C, which suggests the runs timed different work. Licence mismatch: the repo is Unlicense but traceskeleton.wat carries the MIT notice of the skeleton-tracing port. The first-fit malloc scans the whole heap per allocation; setup() mallocs a new image per call without freeing the old one; extend() drops the memory.grow result; thinning_zs stops when either sub-iteration changes nothing (inherited from upstream).

Algorithms must be written directly in WAT (assembled with wabt); binaries average about 900 bytes; manual memory management with a small malloc; no toolchain dependency.

## Maintenance

Abandoned since 2020-08-26 (9 commits, no issues filed); the small, dependency-free sources are easy to vendor under the Unlicense, except traceskeleton.wat, which carries an MIT notice.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** Only a first-party README sentence ('\~300% faster than the version complied with emscripten ... \~500% faster than vanilla Javascript') with no harness, engine, hardware, input or Emscripten version; the repo's tests/traceskeleton.html times only the WAT version once with Date(), so this is first-party numbers without methodology (C).
- **Retiered** C to D: Enricher: the '\~300% faster than Emscripten, \~500% faster than vanilla JS' sentence has no harness; the Emscripten comparator's only entry point runs thinning, rect saving and string serialisation in one call with JS-side parsing, while the repo's only WAT timing is one Date() run of trace_skeleton after thinning, so the runs were not comparable (a 5-6x win over vanilla JS would put the WAT about 2x ahead of native C -O3 by upstream's own table). Directional claim without a valid measurement: C to D.
- **Verifier notes:** Claim text matches the README; tier C stands but evidence is a single unmeasured sentence with no harness. Metadata (Unlicense, 83 stars, last commit 2020-08-26, abandoned) is correct. Baseline corrected to name the -O3 Emscripten build in skeleton-tracing, which routes through WebIDL glue.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `caveats`
- **Shortcomings recorded by:** verifier batch-73 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/LingDong-/wasm-fun>
  - <https://github.com/LingDong-/wasm-fun/commits>
  - <https://github.com/LingDong-/wasm-fun/tree/master/tests>
  - <https://raw.githubusercontent.com/LingDong-/wasm-fun/HEAD/README.md>
  - <https://raw.githubusercontent.com/LingDong-/wasm-fun/HEAD/compile.py>
  - <https://raw.githubusercontent.com/LingDong-/wasm-fun/HEAD/tests/traceskeleton.html>
  - <https://raw.githubusercontent.com/LingDong-/skeleton-tracing/HEAD/README.md>
  - <https://github.com/LingDong-/skeleton-tracing/tree/master/wasm>
  - <https://raw.githubusercontent.com/LingDong-/skeleton-tracing/HEAD/wasm/compile.sh>
- **Sources the enricher read:**
  - <https://github.com/LingDong-/wasm-fun>
  - <https://github.com/LingDong-/wasm-fun/commits>
  - <https://github.com/LingDong-/wasm-fun/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/LingDong-/wasm-fun/HEAD/README.md>
  - <https://raw.githubusercontent.com/LingDong-/wasm-fun/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/LingDong-/wasm-fun/HEAD/compile.py>
  - <https://raw.githubusercontent.com/LingDong-/wasm-fun/HEAD/tests/traceskeleton.html>
  - <https://raw.githubusercontent.com/LingDong-/wasm-fun/HEAD/tests/assets/horse.png>
  - <https://raw.githubusercontent.com/LingDong-/wasm-fun/HEAD/wat/traceskeleton.wat>
  - <https://raw.githubusercontent.com/LingDong-/wasm-fun/HEAD/wat/malloc.wat>
  - <https://raw.githubusercontent.com/LingDong-/wasm-fun/HEAD/wat/thinning.wat>
  - <https://raw.githubusercontent.com/LingDong-/wasm-fun/HEAD/wat/disttransform.wat>
  - <https://raw.githubusercontent.com/LingDong-/wasm-fun/HEAD/wat/findcontours.wat>
  - <https://raw.githubusercontent.com/LingDong-/wasm-fun/HEAD/wat/mazegen.wat>
  - <https://raw.githubusercontent.com/LingDong-/wasm-fun/HEAD/wat/containers.wat>
  - <https://raw.githubusercontent.com/LingDong-/wasm-fun/HEAD/wat/random.wat>
  - <https://raw.githubusercontent.com/LingDong-/wasm-fun/HEAD/wat/browniantree.wat>
  - <https://raw.githubusercontent.com/LingDong-/skeleton-tracing/HEAD/README.md>
  - <https://raw.githubusercontent.com/LingDong-/skeleton-tracing/HEAD/LICENSE>
  - <https://github.com/LingDong-/skeleton-tracing/tree/master/wasm>
  - <https://raw.githubusercontent.com/LingDong-/skeleton-tracing/HEAD/wasm/compile.sh>
  - <https://raw.githubusercontent.com/LingDong-/skeleton-tracing/HEAD/wasm/glue_wrapper.cpp>
  - <https://raw.githubusercontent.com/LingDong-/skeleton-tracing/HEAD/wasm/wrapper.js>
  - <https://raw.githubusercontent.com/LingDong-/skeleton-tracing/HEAD/wasm/trace_skeleton.idl>
  - <https://raw.githubusercontent.com/LingDong-/skeleton-tracing/HEAD/cpp/trace_skeleton.cpp>
  - <https://raw.githubusercontent.com/LingDong-/skeleton-tracing/HEAD/c/trace_skeleton.c>
  - <https://raw.githubusercontent.com/LingDong-/skeleton-tracing/HEAD/js/trace_skeleton.vanilla.js>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/lingdong-/wasm-fun`) · [data/wave13/enrich/raw/github_com_lingdong_wasm_fun.json](../../../data/wave13/enrich/raw/github_com_lingdong_wasm_fun.json) (enrichment confidence 0.55)

</details>
