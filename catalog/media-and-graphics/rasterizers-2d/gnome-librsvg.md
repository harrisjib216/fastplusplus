# libRSVG

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `LGPL-2.1-or-later` · 🟢 active

> GNOME's Rust SVG renderer onto Cairo; beat resvg 0.8.0 on blur- and clip-heavy icons, lost on simple ones.

| | |
|---|---|
| **Beats** | resvg 0.8.0 (cairo, Qt, raqote and Skia backends) and QtSvg 5.12.3 |
| **Claimed result** | Oxygen 4.12: librsvg 2.45.5 163 s versus resvg 0.8.0 cairo 195 s, qt 191 s, raqote 205 s, skia 175 s (about 1.2x faster than resvg-cairo, derived from page data); QtSvg 5.12.3 160 s. Elementary 5.0: librsvg 24 s versus resvg qt 35 s and QtSvg 30 s, but resvg cairo, raqote and skia need only 19 s (librsvg is slower there). A third-party user report on current versions (linebender/resvg issue #1146, 2026-10-01, clip-path-heavy Illustrator-style SVG): rsvg 42 ms versus upstream resvg 960 ms at 1000 px wide and 537 ms versus 31.7 s at 4000 px (about 23x and 59x, derived from page data); a patched resvg in the same report took 18 ms and 437 ms, faster than rsvg. |
| **Workload** | Wall time to render every SVG file of two icon themes (Oxygen 4.12, 4947 files with heavy blur, clipping and masking; Elementary OS 5.0, 3417 simple files) with librsvg 2.45.5 versus resvg 0.8.0 backends and QtSvg 5.12.3. |
| **Metric** | throughput |
| **Adoption** | GNOME's SVG renderer; 410 stars on the read-only GitHub mirror |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/GNOME/librsvg) · [benchmark](https://raw.githubusercontent.com/RazrFalcon/resvg/v0.8.0/.github/perf-oxygen.svg) |

## Verdict

Only a competitor's numbers exist: the resvg 0.8.0 README (2019, no CPU, threads, compiler or build flags stated) rendered the Oxygen icon theme (4,947 blur- and clip-heavy files) in 163 s with librsvg 2.45.5 against 175-205 s for resvg's four backends and 160 s for feature-poor QtSvg, but Elementary (3,417 simple files) in 24 s against 19 s for resvg. A 2026 third-party resvg issue (#1146, one clip-path-heavy file, no versions, hardware or timing method, LLM-assisted analysis) has rsvg 23-59x faster than upstream resvg, while a proposed resvg patch then beats rsvg.

## Use it when

- Programs already on the GNOME/GTK stack (cairo, pango, glib) that need SVG icons, thumbnails or gdk-pixbuf loading with no extra rendering engine.
- Illustrator-style SVGs with many clip paths at large output sizes, where current resvg allocates a layer per clip (resvg issue #1146: rsvg 42 ms vs 960 ms at 1000 px, 537 ms vs 31.7 s at 4000 px).
- Filter-heavy (Gaussian blur, lighting) batch rasterization on multi-core machines, since those filters run in parallel.
- Vector output: rendering SVG into PDF or PostScript through Cairo surfaces, which pixel-only renderers cannot do.
- Text-bearing SVGs that should use the system's fonts through fontconfig and Pango shaping.

## Skip it when

- Small or simple icons: resvg 0.8.0's own chart had librsvg slower on the Elementary set (24 s vs 19 s for 3,417 files).
- When exact clipPath semantics matter: Cairo can only intersect clips, so unions of clip paths are approximated (the source comment says 'not completely correct'; resvg's README calls it incorrect but faster).
- Static, dependency-free or WASM builds: it needs cairo 1.18+, pango 1.50+, glib 2.50+, harfbuzz, freetype and libxml2 at build time.
- Untrusted input without your own sandbox or limits: there is no built-in cap on memory or CPU time, and an open report (#952, search snippet only) has one SVG taking 17 minutes that resvg, Firefox and Chrome render normally.
- Animated, scripted or SVG 1.2/Tiny content: not supported.

## How it is fast

Clip paths go straight to Cairo's native path clipping (cr.clip() in drawing_ctx.rs) instead of rendering each clip into a mask layer, which is cheap on files with many clip paths. feGaussianBlur uses the spec-sanctioned three-box-blur approximation for stdDeviation of 2 or more (an explicit convolution below that, kernel capped at 500 taps), and the box-blur and lighting loops are split per row or column across all cores with Rayon (since 2.43.4). Path filling and compositing are Cairo/pixman's.

## Compared with alternatives

Pick librsvg over resvg when your SVGs are clip-path or blur heavy, you already ship cairo and pango, or you need PDF/PS output; pick resvg for simple icons, pure-Rust static builds, untrusted input and exact clip semantics. LunaSVG and ThorVG are smaller dependency-light C++ options that have not been benchmarked against librsvg in any source read here.

## Integration

| | |
|---|---|
| **Form** | shared lib (librsvg-2 C/GObject API, built with meson and cargo-c) or crate (librsvg); rsvg-convert CLI |
| **Dependencies** | cairo &gt;= 1.18.0, pango &gt;= 1.50, glib/gio &gt;= 2.50, harfbuzz &gt;= 2.0, freetype2, libxml2 &gt;= 2.9; optional gdk-pixbuf &gt;= 2.20, dav1d &gt;= 1.3 for AVIF, gobject-introspection and Vala for bindings |
| **Minimum toolchain** | Rust 1.92.0 (MSRV in Cargo.toml and meson.build), meson &gt;= 1.3.0, cargo-c &gt;= 0.10.10 |
| **Platforms** | Linux and other Unix-likes, macOS/iOS and Windows (meson.build has darwin/ios and windows branches); anywhere cairo and pango build |
| **Thread safety** | Not documented as a general guarantee; rendering can be cancelled from another thread with a GCancellable (2.58.92 and later), and filters use a process-wide Rayon pool on all cores. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind the headline: librsvg 2.43.4 and later run Gaussian blur and lighting filters on all available cores with Rayon (NEWS; rayon::scope in shared_surface.rs box_blur_loop), and the resvg 0.8.0 README states no thread count or CPU, while resvg rendered single-threaded. The 'faster blur' it credits for librsvg 2.45.5's Oxygen win (163 s vs 175-205 s) may be multi-core versus single-core blur rather than a per-core advantage; the 'single thread' note appears only in v0.9.0, whose charts drop librsvg.
- Clip paths use Cairo's native clipping, which intersects but cannot union; apply_clip_path's own comment calls this not completely correct, so part of the speed comes from approximate clip semantics.
- Only 2.62.x and 2.63.x are supported; 2.63.2 (2026-10-01) fixes a use-after-free with duplicated XML entities in nested XInclude documents (RUSTSEC-2026-0305), and Cairo older than 1.17.0 crashes on out-of-range coordinates.
- There is no in-tree performance tracking (devel-docs/performance_tracking.rst, 2022) and rsvg-bench only loops parse/render into a fixed 100x100 surface, so the project publishes no numbers of its own.

## Known shortcomings

- Tier C, mixed: in the resvg v0.8.0 charts librsvg 2.45.5 wins Oxygen (163 s vs 175-205 s) and loses Elementary (24 vs 19 s); the resvg README says part of the Oxygen lead comes from incorrect native cairo clipping; no CPU, harness or flags; 2019 versions. resvg issue #1146 shows rsvg 23-59x faster on a clip-path file until resvg was patched. The same charts serve as the wave 10 resvg evidence read in reverse.
- Enricher: librsvg 2.43.4+ runs Gaussian blur and lighting on all cores with Rayon (rayon::scope in shared_surface.rs box_blur_loop; lighting.rs par_chunks_mut) while resvg v0.8.0 is single-threaded and its README gives no thread count, so the Oxygen 163 s vs 175-205 s 'faster blur' is likely multi-core vs one core; clipping uses native cairo cr.clip() with intersect only (source comment: 'not completely correct'). No in-tree performance numbers (rsvg-bench renders to 100x100 only); RUSTSEC-2026-0305 use-after-free fixed in 2.63.2; issue #952 one SVG takes 17 minutes (snippet only); no memory or CPU caps.

## Caveats and trade-offs

Numbers are bar-chart labels in two SVG images (perf-oxygen.svg, perf-elementary.svg) in the resvg 0.8.0 repository, measured by the resvg author (a competitor, independent of librsvg). The same README says all tested applications have different SVG support, which impacts the performance, that Chrome, Firefox, Inkscape and Batik were left out for startup time, and that librsvg wins on Oxygen because it has a faster Gaussian blur and uses native cairo clipping, which the resvg author calls incorrect but faster, so part of the win comes from a less correct clip implementation. v0.8.0 states no CPU, compiler flags or librsvg build configuration and links no script (the v0.9.0 and v0.9.1 READMEs name an AMD 3700X, single thread, tmpfs, script in resvg-test-suite/tools/perf, but those charts dropped librsvg), so the tier is capped at C. librsvg 2.45.5 dates from 2019 and the resvg cairo, qt and raqote backends no longer exist. librsvg loses to resvg on the simple Elementary set (24 s versus 19 s) and QtSvg is as fast on Oxygen (160 s) only because it skips filters, clipPath, mask and pattern. The only current comparison reached is linebender/resvg issue #1146 (open, 2026-10-01, one pathological clip-path file, no hardware, versions or flags, AI-assisted analysis) where resvg's per-clip layer allocation makes it 23-59x slower than rsvg; a proposed resvg patch beats rsvg there. These are the same v0.8.0 charts already used as the evidence for resvg (wave 10, which lists librsvg as its baseline), read in the opposite direction. A WebSearch snippet (page not opened, blocked) mentions a later table with rsvg 2.42.2 at 242 s versus Inkscape 0.92.4 at 1610 s and Batik 1.12 at 3686 s on the W3C suite; not used in the record. The GNOME wiki, gitlab.gnome.org and librsvg's own rsvg-bench were not reached; the repo_url is the read-only GitHub mirror (canonical home is gitlab.gnome.org/GNOME/librsvg). Same chart README: https://raw.githubusercontent.com/RazrFalcon/resvg/v0.8.0/README.md and https://raw.githubusercontent.com/RazrFalcon/resvg/v0.8.0/.github/perf-elementary.svg [retier] resvg v0.8.0 charts (2019, no CPU, harness or flags): librsvg 2.45.5 wins Oxygen (163 s vs 175-205 s) and loses Elementary (24 vs 19 s). librsvg runs blur and lighting on all cores with Rayon while resvg is single-threaded (thread count unstated), and part of the Oxygen lead comes from incorrect native cairo clipping (intersect-only cr.clip()). resvg issue #1146: rsvg 23-59x faster on a clip-path file until resvg was patched. No in-tree perf numbers; RUSTSEC-2026-0305 fixed in 2.63.2; #952 pathological 17-minute SVG.

LGPL-2.1-or-later (Rust core with a C ABI, renders to Cairo surfaces). The resvg author attributes the Oxygen win to a faster blur implementation and native cairo clipping, which he says is incorrect for some inputs (resvg-test-suite clipPath row) but faster; librsvg therefore trades some SVG correctness for speed in that comparison.

## Maintenance

Actively maintained by GNOME (2.63.2 security release on 2026-10-01; about 193k crates.io downloads) under LGPL-2.1-or-later; the GitHub repo is a read-only mirror, development and issues are on gitlab.gnome.org.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Bar labels in resvg v0.8.0's perf-oxygen.svg and perf-elementary.svg match the record exactly; the v0.8.0 README states no CPU, compiler, flags or librsvg build and links no script (the AMD 3700X, tmpfs and resvg-test-suite tools/perf script appear only from v0.9.0, whose charts drop librsvg). A competitor's README chart, and a later third-party issue report without hardware or versions, so C.
- **Verifier notes:** Chart numbers verified exactly; tier C stands. Shortcomings to record: mixed result (faster than resvg only on blur and clip-heavy Oxygen, slower on Elementary, tied with feature-poor QtSvg), resvg's README attributes part of librsvg's Oxygen lead to incorrect native cairo clipping, 2019 versions with no hardware or harness, and the same charts are resvg's (wave 10) evidence in reverse. Added the current third-party resvg issue #1146 numbers (rsvg 23-59x faster on a clip-path file) to claimed_speedup. Metadata checked: LGPL-2.1-or-later (workspace Cargo.toml), 410 stars on the mirror, last commit 2026-10-01.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-66 (wave 1); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/RazrFalcon/resvg/v0.8.0/.github/perf-oxygen.svg>
  - <https://raw.githubusercontent.com/RazrFalcon/resvg/v0.8.0/.github/perf-elementary.svg>
  - <https://raw.githubusercontent.com/RazrFalcon/resvg/v0.8.0/README.md>
  - <https://raw.githubusercontent.com/RazrFalcon/resvg/v0.9.0/README.md>
  - <https://raw.githubusercontent.com/RazrFalcon/resvg/v0.9.1/README.md>
  - <https://raw.githubusercontent.com/RazrFalcon/resvg/v0.10.0/README.md>
  - <https://raw.githubusercontent.com/RazrFalcon/resvg/v0.11.0/README.md>
  - <https://github.com/linebender/resvg/issues/1146>
  - <https://github.com/GNOME/librsvg>
  - <https://github.com/GNOME/librsvg/commits>
  - <https://raw.githubusercontent.com/GNOME/librsvg/HEAD/Cargo.toml>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/GNOME/librsvg/HEAD/README.md>
  - <https://raw.githubusercontent.com/GNOME/librsvg/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/GNOME/librsvg/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/GNOME/librsvg/HEAD/NEWS>
  - <https://raw.githubusercontent.com/GNOME/librsvg/HEAD/meson.build>
  - <https://raw.githubusercontent.com/GNOME/librsvg/HEAD/meson_options.txt>
  - <https://raw.githubusercontent.com/GNOME/librsvg/HEAD/rsvg/Cargo.toml>
  - <https://raw.githubusercontent.com/GNOME/librsvg/HEAD/rsvg/src/lib.rs>
  - <https://raw.githubusercontent.com/GNOME/librsvg/HEAD/rsvg/src/api.rs>
  - <https://raw.githubusercontent.com/GNOME/librsvg/HEAD/rsvg/src/drawing_ctx.rs>
  - <https://raw.githubusercontent.com/GNOME/librsvg/HEAD/rsvg/src/filters/gaussian_blur.rs>
  - <https://raw.githubusercontent.com/GNOME/librsvg/HEAD/rsvg/src/surface_utils/shared_surface.rs>
  - <https://raw.githubusercontent.com/GNOME/librsvg/HEAD/rsvg/src/filters/lighting.rs>
  - <https://raw.githubusercontent.com/GNOME/librsvg/HEAD/rsvg-bench/Cargo.toml>
  - <https://raw.githubusercontent.com/GNOME/librsvg/HEAD/rsvg-bench/src/main.rs>
  - <https://raw.githubusercontent.com/GNOME/librsvg/HEAD/librsvg-c/Cargo.toml>
  - <https://raw.githubusercontent.com/GNOME/librsvg/HEAD/librsvg-c/src/handle.rs>
  - <https://raw.githubusercontent.com/GNOME/librsvg/HEAD/devel-docs/security.rst>
  - <https://raw.githubusercontent.com/GNOME/librsvg/HEAD/devel-docs/features.rst>
  - <https://raw.githubusercontent.com/GNOME/librsvg/HEAD/devel-docs/architecture.rst>
  - <https://raw.githubusercontent.com/GNOME/librsvg/HEAD/devel-docs/performance_tracking.rst>
  - <https://raw.githubusercontent.com/GNOME/librsvg/HEAD/devel-docs/compiling.rst>
  - <https://raw.githubusercontent.com/GNOME/librsvg/HEAD/devel-docs/supported_versions.rst>
  - <https://crates.io/api/v1/crates/librsvg>
  - <https://raw.githubusercontent.com/RazrFalcon/resvg/v0.8.0/README.md>
  - <https://raw.githubusercontent.com/RazrFalcon/resvg/v0.9.0/README.md>
  - <https://github.com/RazrFalcon/resvg-test-suite>
  - <https://github.com/RazrFalcon/resvg-test-suite/tree/master/tools>
  - https://github.com/RazrFalcon/resvg-test-suite/tree/master/tools/perf (404, perf script removed)
  - <https://github.com/linebender/resvg/issues/1146>
  - https://gitlab.gnome.org/GNOME/librsvg/-/issues/952 (search snippet only; gitlab.gnome.org egress-blocked)
  - https://gitlab.gnome.org/GNOME/librsvg/issues/188 (search snippet only)
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/gnome/librsvg`) · [data/wave1/enrich/raw/github_com_gnome_librsvg.json](../../../data/wave1/enrich/raw/github_com_gnome_librsvg.json) (enrichment confidence 0.7)

</details>
