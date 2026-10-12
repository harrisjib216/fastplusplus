# LunaSVG

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Small C++17 SVG 1.1/Tiny 1.2 renderer on the plutovg rasterizer; converts icons to PNG about 2x faster than cairosvg through Python.

| | |
|---|---|
| **Beats** | cairosvg 2.9.1 (Python, renders through Cairo 1.18.4) and resvg-py 0.5.0 |
| **Claimed result** | Median ms per file, SVG bytes to PNG bytes (benchmarks/results.md): simple-icons at 256 px pillow-lunasvg 1.00 vs cairosvg 2.17 and resvg-py 2.84 (README: 2.2x and 2.8x faster); at 1024 px 12.56 vs 23.63 and 34.85 (README: 1.9x and 2.8x). Render only, without PNG encode: 0.11 ms at 256 px and 0.88 ms at 1024 px. resvg feature tests (filters and text not timed): 256 px 0.45 vs 1.47 cairosvg and 2.17 resvg-py; 1024 px 5.26 vs 19.16 cairosvg and 27.22 resvg-py, over 943, 884 and 941 files respectively because files a renderer rejected are dropped from its median. |
| **Workload** | Median time per icon, SVG bytes to PNG bytes, for 3,460 simple-icons SVGs (24x24 viewBox) scaled to 256 px and 1024 px, plus 943 resvg feature-test SVGs (filters and text excluded), through the pillow-lunasvg Python binding of LunaSVG 3.5.0. |
| **Metric** | latency |
| **Hardware** | Apple M4, macOS 26.5.1 |
| **Compiler and flags** | pillow-lunasvg 0.1.0 built locally from commit 653c187 (LunaSVG 3.5.0) via pip with scikit-build-core and CMake; CMakeLists.txt sets only C++17, static lunasvg/plutovg and LUNASVG_DISABLE_EXTERNAL_RESOURCES, with no CMAKE_BUILD_TYPE or optimization flags, so the build tool's default applies; compiler and version not stated (macOS host). Python 3.13.15, Pillow 12.3.0, resvg-py 0.5.0, cairosvg 2.9.1 with cairo 1.18.4 from Homebrew. Exact commands are in results.md. |
| **Adoption** | 1.2k stars; embedded in many apps, pillow-lunasvg wheels on PyPI |
| **Last commit** | 2026-09-17 |
| **Links** | [repository](https://github.com/sammycage/lunasvg) · [benchmark](https://github.com/Maksim-Burtsev/pillow-lunasvg/blob/main/benchmarks/results.md) |

## Verdict

On an Apple M4 (macOS 26.5.1), pillow-lunasvg 0.1.0 (LunaSVG 3.5.0; built by scikit-build-core, whose default CMake build type is Release, compiler not stated) converted 3,460 simple-icons SVGs to PNG at a median 1.00 ms versus 2.17 ms for cairosvg 2.9.1 (Cairo 1.18.4) and 2.84 ms for resvg-py 0.5.0 at 256 px, and 12.56 versus 23.63 and 34.85 ms at 1024 px. LunaSVG's own parse plus render was only 0.11 ms and 0.88 ms of those times (about 89% and 93% of the pillow-lunasvg time is Pillow PNG encoding and Python overhead, derived from page data), and no render-only time is given for the baselines, so this is an end-to-end SVG-to-PNG comparison dominated by Python front-ends and PNG encoders, not a rasterizer comparison.

## Use it when

- Rendering SVG icons, UI assets or emoji glyphs to bitmaps inside a C++ application or game (it is used by Dear ImGui, RmlUi, OpenSiv3D and node-canvas) where pulling in Cairo, librsvg or Skia is too heavy.
- Python thumbnail or icon pipelines that currently call cairosvg: pillow-lunasvg ships self-contained wheels (259-467 KB, no system cairo) and was measured at about half cairosvg's per-file time.
- Static SVG content that sticks to SVG 1.1 basics: paths, shapes, gradients, patterns, clip paths, masks, markers, &lt;use&gt;, &lt;text&gt; with registered fonts.
- Applications that need to restyle or hit-test a loaded document (applyStyleSheet, setAttribute, elementFromPoint) and re-render without reparsing.

## Skip it when

- SVGs with filters (blur, drop shadows, lighting), mix-blend-mode, CSS transform properties, transform-origin, context-fill, or SVG/WebP inside &lt;image&gt;: none are implemented, and only 59% of resvg's feature tests match resvg's output at loose tolerance.
- Untrusted input without hardening: CVE-2024-33763 and CVE-2024-33764 (lunasvg 2.3.9) and CVE-2024-57720, -57721 and -57722 (lunasvg 3.0.0) are stack, segfault and allocation bugs, a fuzzer is still only requested (issue #223), and the pillow-lunasvg author had to add his own guards against deep-nesting stack overflow, exponential &lt;use&gt; expansion and a plutovg dashing loop that never terminates.
- Throughput-critical rendering of large scenes on many cores: plutovg's compositing is scalar, and engines such as Blend2D or ThorVG are built for that workload.
- Animated content (no SMIL; LunaSVG says animation is unlikely ever to be supported) or Lottie, where ThorVG is the fit.
- Patterns in documents with large user-space coordinates: open issue #248 reports the pattern tile canvas being allocated at user-space size (16,000 x 16,000 px in the report) before downscaling.

## How it is fast

Rendering goes through plutovg, a small C library whose scan converter is FreeType's ftgrays (exact-area coverage per pixel cell, emitted as coverage spans) and whose strokes come from the FreeType stroker; spans are composited with Qt-style per-span blend functions on premultiplied 32-bit pixels (scalar code; SSE2 is used only for the 32-bit fill helper). LunaSVG itself is a compact C++ DOM and layout tree with no Cairo context, no external XML or CSS library and no Python in the loop, which is where most of the measured advantage over cairosvg (a Python SVG parser driving Cairo) comes from.

## Compared with alternatives

Pick LunaSVG over NanoSVG2 when you need real SVG documents (clipping, masks, patterns, CSS, &lt;use&gt;, text) rather than flat fills, and over ThorVG when you only need static SVG to bitmap with a smaller codebase and a DOM API; pick ThorVG for Lottie or animation, and Blend2D when you are drawing your own vector content at high throughput rather than rendering SVG files.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | plutovg (C, bundled as a git submodule or found as plutovg &gt;= 1.3.0 via USE_SYSTEM_PLUTOVG), which itself bundles FreeType's ftgrays/stroker (FTL license) and stb_image/stb_truetype |
| **Minimum toolchain** | C++17, CMake 3.15 or Meson |
| **Platforms** | any (portable C/C++; SSE2 used only for a fill helper when available) |
| **Thread safety** | not documented; LunaSVG keeps a process-wide font cache, and pillow-lunasvg's code notes that plutovg's mutex is a no-op without &lt;threads.h&gt; (e.g. macOS), so that binding serializes every LunaSVG call with one global lock |
| **Drop-in for the baseline** | partial: in Python, pillow-lunasvg replaces cairosvg.svg2png calls with Image.open plus load(scale=) and save; in C/C++ it has its own API with nothing in common with Cairo or librsvg |

## Gotchas

- Bitmaps are ARGB32 premultiplied (BGRA bytes on little-endian); call Bitmap::convertToRGBA() in place before handing pixels to code that expects straight RGBA.
- By default &lt;image href="/path"&gt; may load local files; build with LUNASVG_DISABLE_EXTERNAL_RESOURCES=ON (as pillow-lunasvg does) when rendering untrusted SVGs, and consider LUNASVG_DISABLE_LOAD_SYSTEM_FONTS for reproducible text.
- &lt;use&gt; is expanded by deep copy, so a short chain of nested &lt;use&gt; grows exponentially in memory and time; cap input size or element counts yourself.
- Text needs fonts registered through lunasvg_add_font_face_from_file/_data or system font loading, so the same file can render differently on different machines.

## Known shortcomings

- Tier B on pillow-lunasvg results.md (public bench.py, Apple M4, no compiler or flags) against cairosvg and resvg-py, neither a listed baseline. The measurer is the Python wrapper's author (README PR #273), so a strict vendor reading gives C. Much of the gap is the Python front-end and PNG encoders, not the rasterizer.
- The comparison is end to end rather than rasteriser speed: render-only time is 0.11 of 1.00 ms at 256 px and 0.88 of 12.56 ms at 1024 px, so 89-93% of LunaSVG's measured time is Pillow PNG encoding plus Python, and the baselines have no render-only rows. The wheel was an optimised Release build (scikit-build-core default), correcting the verifier, but the compiler is still unstated. CVEs 2024-33763 and 33764 (2.3.9) and 2024-57720, 57721 and 57722 (3.0.0) per search snippets; fuzzer issue #223 open; open #248 (pattern canvas allocating 16,000x16,000); the wrapper guards deep nesting, exponential use elements and a plutovg dash infinite loop; external file loading is on by default.
- Enricher (e113, 2026-10-05, via resvg): the pillow-lunasvg benchmark's resvg baseline is resvg-py 0.5.0, whose Cargo.toml builds resvg 0.48.0 with opt-level 'z' (size-optimised), so the 2.8x over resvg-py measures a handicapped build; cairosvg parses SVG in Python. Retiered B to C (retier-34).

## Caveats and trade-offs

Measured by the author of the pillow-lunasvg wrapper (independent of LunaSVG's author, but promoting his own wrapper; he added pillow-lunasvg to LunaSVG's README via PR #273, merged 2026-09-17). The benchmark repo has 0 stars and 15 commits. The pipeline is timed through Python: about 89% of pillow-lunasvg's 1.00 ms is Pillow load plus PNG encode (render only 0.11 ms), and the three tools use different PNG encoders (Pillow zlib, cairo's PNG writer, resvg's encoder), while cairosvg parses SVG in Python, so the gap over cairosvg reflects front-end and encoder overhead more than Cairo's rasterizer versus plutovg. On the resvg test corpus LunaSVG does less work: it lacks filters, the CSS transform property, transform-origin, mix-blend-mode, context-fill and SVG/WebP inside &lt;image&gt; (59% loose fidelity match against resvg), and per-renderer medians cover different file subsets. Filter tests are not timed. On simple-icons fidelity is comparable (99.0% vs cairosvg 99.4% strict). The machine was not idle during the run (another development session), which is why min-of-3 was used. Baselines are Python packages (cairosvg, resvg-py), not the category's C/C++ incumbents. [retier] Measured by the author of the pillow-lunasvg wrapper (independent of LunaSVG's author, but promoting his own wrapper; added to LunaSVG's README via PR #273, merged 2026-09-17). The resvg baseline is resvg-py 0.5.0, whose Cargo.toml (baseplate-admin/resvg-py) builds resvg 0.48.0 with opt-level 'z', a size-optimised profile, so the 2.8x over resvg-py does not measure resvg's release performance; cairosvg parses SVG in Python. The pipeline is timed through Python: about 89% of pillow-lunasvg's 1.00 ms is Pillow load plus PNG encode (render only 0.11 ms), and the three tools use different PNG encoders. On the resvg test corpus LunaSVG does less work (no filters, CSS transform property, transform-origin, mix-blend-mode, context-fill or SVG/WebP inside &lt;image&gt;; 59% loose fidelity match against resvg) and per-renderer medians cover different file subsets; filter tests are not timed. The machine was not idle during the run (min-of-3 used). Baselines are Python packages, not the category's C/C++ incumbents.

Lightweight SVG 1.1/Tiny 1.2 renderer on top of the plutovg rasterizer. No filters, no SVG inside &lt;image&gt;, no WebP images, no CSS transform property, no transform-origin, no mix-blend-mode, no context-fill. Only 59% of resvg's feature tests match resvg output at 1% pixel tolerance (cairosvg 53%).

## Maintenance

Actively maintained (last commit 2026-09-17, release 3.5.0), MIT-licensed, 1.2k stars and embedded in Dear ImGui, RmlUi, node-canvas and others; safe to adopt for trusted static SVG, but harden it before rendering untrusted files.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now C.
- **Tier reason:** Independent run (by the pillow-lunasvg author, not LunaSVG's author sammycage) with a public harness (benchmarks/bench.py: min of 3 interleaved runs per file, median over pinned corpora), stated hardware (Apple M4), library versions and corpus commits; every number in the record matches benchmarks/results.md. Not A: no compiler or flags are stated and the repo's CMakeLists.txt/pyproject.toml set no build type or optimization flags.
- **Retiered** B to C: Lowered B to C. Enricher e113 (2026-10-05, while enriching resvg) found that the resvg-py 0.5.0 baseline used by the pillow-lunasvg benchmark builds resvg 0.48.0 with opt-level 'z' (baseplate-admin/resvg-py Cargo.toml, size-optimised), so the 2.8x over resvg-py measures a handicapped resvg build, not resvg; the other baseline, cairosvg, parses SVG in Python. The run is independent of LunaSVG's author but its baselines do not represent the compared libraries, so first-party-grade evidence only.
- **Verifier notes:** Numbers verified line by line against results.md and the timing code in bench.py. Keep at B as independent measurement, but the measurer has an interest in the wrapper, so the orchestrator may prefer C under the vendor-evidence precedent. LunaSVG metadata checked: MIT, 1.2k stars, last commit 2026-09-17, not archived.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** pillow-lunasvg benchmark (handicapped baselines)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Maksim-Burtsev/pillow-lunasvg/HEAD/benchmarks/results.md>
  - <https://raw.githubusercontent.com/Maksim-Burtsev/pillow-lunasvg/HEAD/benchmarks/bench.py>
  - <https://raw.githubusercontent.com/Maksim-Burtsev/pillow-lunasvg/HEAD/README.md>
  - <https://raw.githubusercontent.com/Maksim-Burtsev/pillow-lunasvg/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/Maksim-Burtsev/pillow-lunasvg/HEAD/CMakeLists.txt>
  - <https://github.com/Maksim-Burtsev/pillow-lunasvg>
  - <https://github.com/sammycage/lunasvg>
  - <https://github.com/sammycage/lunasvg/commits>
- **Sources the enricher read:**
  - <https://github.com/sammycage/lunasvg>
  - <https://raw.githubusercontent.com/sammycage/lunasvg/HEAD/README.md>
  - <https://raw.githubusercontent.com/sammycage/lunasvg/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/sammycage/lunasvg/HEAD/meson.build>
  - <https://raw.githubusercontent.com/sammycage/lunasvg/HEAD/include/lunasvg.h>
  - <https://github.com/sammycage/lunasvg/issues?q=is%3Aissue+crash+OR+overflow+OR+slow+OR+performance>
  - <https://github.com/sammycage/lunasvg/issues/150>
  - <https://github.com/sammycage/lunasvg/issues/248>
  - <https://github.com/sammycage/plutovg/tree/main/source>
  - <https://raw.githubusercontent.com/sammycage/plutovg/HEAD/README.md>
  - <https://raw.githubusercontent.com/sammycage/plutovg/HEAD/source/plutovg-blend.c>
  - <https://raw.githubusercontent.com/sammycage/plutovg/HEAD/source/plutovg-ft-raster.c>
  - <https://raw.githubusercontent.com/sammycage/plutovg/HEAD/source/plutovg-rasterize.c>
  - <https://github.com/Maksim-Burtsev/pillow-lunasvg>
  - <https://raw.githubusercontent.com/Maksim-Burtsev/pillow-lunasvg/HEAD/README.md>
  - <https://raw.githubusercontent.com/Maksim-Burtsev/pillow-lunasvg/HEAD/benchmarks/results.md>
  - <https://raw.githubusercontent.com/Maksim-Burtsev/pillow-lunasvg/HEAD/benchmarks/bench.py>
  - <https://raw.githubusercontent.com/Maksim-Burtsev/pillow-lunasvg/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Maksim-Burtsev/pillow-lunasvg/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/Maksim-Burtsev/pillow-lunasvg/HEAD/src/_lunasvg.cpp>
  - <https://raw.githubusercontent.com/Maksim-Burtsev/pillow-lunasvg/HEAD/src/pillow_lunasvg/__init__.py>
  - <https://raw.githubusercontent.com/scikit-build/scikit-build-core/HEAD/README.md>
  - https://www.strix.ai/cve/CVE-2024-33763 (search snippet only)
  - https://www.strix.ai/cve/CVE-2024-33764 (search snippet only)
  - https://vulners.com/cve/CVE-2024-57721 (search snippet only)
  - https://osv.dev/vulnerability/CVE-2024-57722 (search snippet only)
  - https://cyberstrike.io/cve/CVE-2024-57720/ (search snippet only)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/sammycage/lunasvg`) · [data/wave10/enrich/raw/github_com_sammycage_lunasvg.json](../../../data/wave10/enrich/raw/github_com_sammycage_lunasvg.json) (enrichment confidence 0.7)

</details>
