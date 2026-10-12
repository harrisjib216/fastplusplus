# resvg

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Pure-Rust static-SVG renderer with a C API; benchmarks faster than librsvg on icon sets, much slower on clip-path-heavy files.

| | |
|---|---|
| **Beats** | librsvg (2.45.5 in the resvg 0.8.0 README charts; 2.50 in the MediaWiki snippet) and QtSvg 5.12.3; Inkscape 1.0 and Batik only in the snippet-only MediaWiki table |
| **Claimed result** | First-party (resvg 0.8.0 README, 2019): time to render the Elementary OS Icon Theme 5.0 (3417 files): resvg 0.8.0 19 s with the cairo, raqote or skia backend (35 s with qt), librsvg 2.45.5 24 s, QtSvg 5.12.3 30 s, so about 1.26x faster than librsvg (derived from page data). Oxygen Icon Theme 4.12 (4947 files): resvg 0.8.0 175 s (skia) to 205 s (raqote), librsvg 163 s, QtSvg 160 s, so resvg was about 7% to 26% slower than librsvg there (derived from page data); the README attributes this to librsvg's faster blur and its native but incorrect cairo clipping, and notes QtSvg skips filter, clipPath, mask and pattern. Snippet only (MediaWiki 'SVG benchmarks' page, blocked): resvg 0.14.0 1m04.490s CPU time vs librsvg 2.50 1m46.776s, Inkscape 1.0 7m57.465s, Batik 6m51.560s, about 1.66x faster than librsvg and 7.4x faster than Inkscape (derived from snippet data); a second table on that page, per a snippet, gives resvg 150 s, rsvg 2.42.2 242 s, Inkscape 1610 s, Batik 3686 s. |
| **Workload** | resvg 0.8.0 README: wall time to render every SVG of the Elementary OS 5.0 icon theme (3417 files) and the Oxygen 4.12 icon theme (4947 files, converted from .svgz) with each library. MediaWiki SVG benchmarks (snippet only): CPU time to render W3C SVG test files at 512 px with each renderer's command-line tool, resvg 0.14.0, 2021. |
| **Metric** | throughput |
| **Adoption** | 4.1k stars; the CLI and C API are used by other projects (resvg-js, Wikimedia evaluation) |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/linebender/resvg) · [benchmark](https://github.com/linebender/resvg/blob/v0.8.0/README.md) |

## Verdict

Only first-party numbers are reachable: the resvg 0.8.0 README (2019, no hardware, compiler or harness stated; that tag's testing-tools folder holds only regression and test-runner scripts) rendered the Elementary icon theme in 19 s against librsvg 2.45.5's 24 s (about 1.26x), but the Oxygen theme in 175-205 s against librsvg's 163 s (slower), using cairo, raqote, Skia and Qt backends that current resvg no longer has. The independent Wikimedia 2021 comparison (resvg 0.14.0 at 1m04s CPU time against librsvg 2.50 at 1m47s over W3C test files) is search-snippet only, and an open third-party issue (#1146) measures current resvg 23-59x slower than librsvg on a clip-path-heavy file.

## Use it when

- Batch SVG-to-PNG of icon sets, maps and other static artwork where you want one self-contained binary with no cairo, pango or GLib dependency.
- Rendering untrusted SVG: the resvg crate forbids unsafe code, and the project guards against endless loops and deep recursion.
- Output that must be pixel-identical across platforms (x86 Windows and ARM macOS give the same bytes per the README), e.g. golden-image tests or reproducible thumbnails.
- C or C++ programs that want an SVG renderer through a small C API with static linking.
- WASM or embedded targets where Rust compiles but system graphics libraries are unavailable.

## Skip it when

- Files with many clip paths, such as Illustrator exports: issue #1146 (2026-10-01, open) measured upstream resvg at 960 ms versus librsvg 42 ms at 1000 px and 31.7 s versus 537 ms at 4000 px; each clip path allocates and masks a full layer-sized pixmap.
- Documents that reuse large raster images through &lt;use&gt;: issue #1147 (open) shows the image decoded again for every use (30 uses of one 4000x3000 JPEG: 1374 ms, 257 ms with a proposed patch).
- Filter-heavy documents: issue #857 reports over 4 s for a document with 10 filters and was closed as not planned; the 0.8.0 README also notes librsvg's faster blur on the Oxygen theme.
- Animated or scripted SVG, SVG Tiny 1.2, or GPU rendering: none are supported.
- Text that must match the platform's native hinting: text is shaped and filled as paths, and needs fonts loaded explicitly.

## How it is fast

usvg resolves CSS, units, use/symbol references and shapes into plain paths and groups before rendering, so the renderer is a simple tree walk over pre-resolved paths. Rasterization goes through tiny-skia, a Rust port of a subset of Skia's CPU raster pipeline with SSE/AVX and AArch64 NEON paths. Since 0.33 each isolated group gets a layer sized to its computed bounding box instead of the whole canvas (the changelog reports paris-30k going from about 33.8 s to 0.29 s on an M1 Pro). Gaussian blur uses a 5-pass box blur for sigma of 2 or more and an Alvarez-Mazorra IIR cascade below that. Rendering is single-threaded.

## Compared with alternatives

Pick resvg over LunaSVG when SVG coverage and memory safety on untrusted input matter more than raw speed: LunaSVG wins the pillow-lunasvg end-to-end timing, but resvg-py in that harness builds resvg with opt-level 'z', and resvg passes more of the resvg test suite. Use ThorVG for Lottie or animation, and tiny-skia directly (resvg's backend) when you draw your own vector content rather than SVG files.

## Integration

| | |
|---|---|
| **Form** | crate (resvg, usvg) plus C API as shared or static library (resvg.h), and CLI |
| **Dependencies** | pure Rust crates only (tiny-skia, usvg, svgtypes; optional zune-jpeg, gif, image-webp, fontdb/skrifa/harfrust for text); no system libraries |
| **Minimum toolchain** | Rust 1.85 (MSRV of 0.48.1, edition 2024); any C/C++ compiler for the C API |
| **Platforms** | anywhere Rust compiles, including WASM; SIMD in tiny-skia on x86-64 and AArch64 |
| **Thread safety** | not documented in resvg.h; the renderer itself is single-threaded |
| **Drop-in for the baseline** | partial — the CLI does the same job as rsvg-convert with its own flags, but the C API is not librsvg's RsvgHandle/cairo interface |

## Gotchas

- resvg_render expects a width\*height\*4 buffer of premultiplied RGBA8888; convert before handing pixels to straight-alpha code.
- Text renders only if fonts are loaded (for example resvg_options_load_system_fonts or the system-fonts feature); 0.48 moved text to skrifa and harfrust, so glyph output can differ slightly from 0.47.
- Cost scales with layer and clip area, not with element count: large output sizes with clip paths, masks or filters can be tens of times slower than small ones.
- Release builds should use the repository's production profile (opt-level 3, LTO, one codegen unit); bindings built otherwise (resvg-py 0.5.0 builds resvg with opt-level 'z') will be slower.

## Known shortcomings

- Mixed result against librsvg in the reachable first-party v0.8.0 README charts: Elementary 19 s against librsvg 2.45.5's 24 s (1.26x) but Oxygen 175-205 s against 163 s (7-26% slower); the Wikimedia 1.66x and 7.4x figures are snippet-only (mediawiki, phabricator and gitlab.gnome.org blocked).
- Enricher (e113, 2026-10-05): the only first-party numbers are the 0.8.0 README figures against backends that no longer exist, with no harness. Open issue #1146 (2026-10-01): a clip-path-heavy file renders in 960 ms vs librsvg's 42 ms at 1000 px and 31.7 s vs 537 ms at 4000 px because each clip allocates a layer-sized pixmap; #1147: &lt;use&gt; re-decodes images; #857 (filters performance) closed as not planned. C stands, usability mixed. The pillow-lunasvg benchmark's resvg-py baseline builds resvg at opt-level 'z', so its resvg numbers are handicapped (recorded against LunaSVG).

## Caveats and trade-offs

The reachable numbers are first-party, from the resvg 0.8.0 README (2019), with no hardware, OS, compiler, flags or harness stated; resvg 0.8.0 rendered through cairo, Qt, raqote or Google Skia backends, whereas current resvg renders only through tiny-skia, so those timings do not describe today's code. They are mixed: faster than librsvg on simple icons (Elementary) and slower on the blur- and clip-heavy Oxygen theme. From 0.9 on the README compared only resvg's own backends, and since 0.10 it carries no numbers and says comparing SVG renderers is like comparing apples and oranges. The Wikimedia evaluation (independent, 2021, resvg 0.14.0) is snippet only: www.mediawiki.org, phabricator.wikimedia.org and the librsvg GitLab issue 729 are egress-blocked, so its hardware and command lines are unknown; times are whole-suite CLI runs that include process start-up, which also penalizes Batik's JVM. The baselines differ in SVG feature support (resvg-test-suite correctness per the snippet: resvg 0.831, Inkscape 0.745, librsvg 0.662), so faster and more complete are mixed in one figure. Written in Rust with a C API (crates/c-api); not C++. No benches/ directory exists in the current repo. Other resvg-based entries (resvg-js) are already recorded.

Static SVG only (no scripting or animation). Rust crate with a C API (crates/c-api) so it is callable from C++. Renders on the CPU through tiny-skia; no GPU path. Built with a production profile (opt-level 3, LTO, one codegen unit).

## Maintenance

Actively maintained by Linebender (0.48.1 released 2026-08-02, commits to 2026-10-03), Apache-2.0 OR MIT, about 28.4 million crates.io downloads, so safe to depend on; the C API is versioned with the crate and has no stable ABI promise documented.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** A reachable first-party page carries numbers: the resvg 0.8.0 README Performance section (charts .github/perf-elementary.svg and perf-oxygen.svg) times whole icon themes against librsvg 2.45.5 and QtSvg 5.12.3, with no hardware, compiler, flags or measurement script stated (the later-cited resvg-test-suite tools/perf script is gone from the current tree). The independent Wikimedia numbers in the record exist only in a snippet of the blocked MediaWiki page, so C.
- **Verifier notes:** Metadata checked on github.com: Apache-2.0 OR MIT, 4.1k stars, 354 forks, not archived, last commit 2026-10-03 (active), all as recorded. benchmark_url moved to the reachable v0.8.0 README; the MediaWiki SVG_benchmarks page holds the independent numbers and would support B if a later session can open it.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** first-party 0.8.0 README; issue #1146 user numbers
- **Pages the verifier opened:**
  - <https://github.com/linebender/resvg>
  - <https://raw.githubusercontent.com/linebender/resvg/HEAD/README.md>
  - <https://github.com/linebender/resvg/commits/main>
  - <https://github.com/linebender/resvg/tree/main/docs>
  - <https://github.com/linebender/resvg/tree/main/crates>
  - <https://github.com/linebender/resvg/tree/main/crates/resvg>
  - <https://github.com/linebender/resvg/tree/main/tools>
  - <https://raw.githubusercontent.com/linebender/resvg/HEAD/CHANGELOG.md>
  - <https://github.com/linebender/resvg/blob/v0.8.0/README.md>
  - <https://raw.githubusercontent.com/linebender/resvg/v0.8.0/README.md>
  - <https://raw.githubusercontent.com/linebender/resvg/v0.8.0/.github/perf-elementary.svg>
  - <https://raw.githubusercontent.com/linebender/resvg/v0.8.0/.github/perf-oxygen.svg>
  - <https://raw.githubusercontent.com/linebender/resvg/v0.9.1/README.md>
  - <https://raw.githubusercontent.com/linebender/resvg/v0.9.1/benches/README.md>
  - <https://raw.githubusercontent.com/linebender/resvg/v0.14.0/README.md>
  - <https://github.com/linebender/resvg-test-suite>
  - <https://github.com/linebender/resvg-test-suite/tree/master/tools>
- **Sources the enricher read:**
  - <https://github.com/linebender/resvg/tree/v0.8.0>
  - <https://github.com/linebender/resvg/tree/v0.8.0/testing-tools>
  - <https://github.com/linebender/resvg/issues?q=is%3Aissue+performance+OR+slow>
  - <https://github.com/linebender/resvg/issues/1146>
  - <https://github.com/linebender/resvg/issues/1147>
  - <https://github.com/linebender/resvg/issues/857>
  - <https://github.com/linebender/resvg/issues/765>
  - <https://raw.githubusercontent.com/linebender/resvg/HEAD/README.md>
  - <https://raw.githubusercontent.com/linebender/resvg/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/linebender/resvg/HEAD/crates/resvg/Cargo.toml>
  - <https://raw.githubusercontent.com/linebender/resvg/HEAD/crates/resvg/src/lib.rs>
  - <https://raw.githubusercontent.com/linebender/resvg/HEAD/crates/resvg/src/clip.rs>
  - <https://raw.githubusercontent.com/linebender/resvg/HEAD/crates/resvg/src/mask.rs>
  - <https://raw.githubusercontent.com/linebender/resvg/HEAD/crates/resvg/src/render.rs>
  - <https://raw.githubusercontent.com/linebender/resvg/HEAD/crates/resvg/src/filter/mod.rs>
  - <https://raw.githubusercontent.com/linebender/resvg/HEAD/crates/resvg/src/filter/box_blur.rs>
  - <https://raw.githubusercontent.com/linebender/resvg/HEAD/crates/resvg/src/filter/iir_blur.rs>
  - <https://raw.githubusercontent.com/linebender/resvg/HEAD/crates/c-api/Cargo.toml>
  - <https://raw.githubusercontent.com/linebender/resvg/HEAD/crates/c-api/resvg.h>
  - <https://raw.githubusercontent.com/linebender/resvg/HEAD/crates/c-api/README.md>
  - <https://raw.githubusercontent.com/linebender/resvg/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/linebender/resvg/HEAD/docs/unsupported.md>
  - <https://raw.githubusercontent.com/linebender/resvg/v0.8.0/README.md>
  - <https://raw.githubusercontent.com/linebender/resvg/v0.8.0/.github/perf-elementary.svg>
  - <https://raw.githubusercontent.com/linebender/resvg/v0.8.0/.github/perf-oxygen.svg>
  - <https://raw.githubusercontent.com/linebender/resvg/v0.9.1/benches/README.md>
  - <https://raw.githubusercontent.com/baseplate-admin/resvg-py/HEAD/Cargo.toml>
  - <https://crates.io/api/v1/crates/resvg>
  - <https://pypi.org/pypi/resvg-py/0.5.0/json>
  - https://www.mediawiki.org/wiki/SVG_benchmarks (search snippet only)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/linebender/resvg`) · [data/wave10/enrich/raw/github_com_linebender_resvg.json](../../../data/wave10/enrich/raw/github_com_linebender_resvg.json) (enrichment confidence 0.75)

</details>
