# djvu-rs (Rust DjVu codec) vs DjVuLibre

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Pure-Rust, MIT DjVu reader, renderer and encoder; first-party runs show faster rendering and c44/cjb2-style encoding than DjVuLibre 3.5.29.

| | |
|---|---|
| **Beats** | DjVuLibre 3.5.29 (C++): ddjvu rendering and the c44 / cjb2 encoders |
| **Claimed result** | README table (Apple M1 Max) matching BENCHMARKS_RESULTS.md 'Comparison with DjVuLibre 3.5.29', 2026-10-03 run, djvu-rs warm Criterion render_pixmap vs libdjvulibre render-only on an already decoded page: boy.djvu @72 dpi 61.7 us vs 124 us (2.0x), watchmaker about 1.4x, cable about 1.6x as printed; the warm rows let djvu-rs reuse its cached RGB background and JB2 mask while DjVuLibre redoes IW44 reconstruction and the JB2 blit each call, so like-for-like estimates from page data are about 1.16-1.27x (watchmaker) and about 1.4x (cable), with the boy 2.0x mostly cache reuse. |
| **Workload** | Render: djvu-rs warm Criterion render_pixmap (RGBA, aa off) vs libdjvulibre ddjvu_page_render (RGB24) timed render-only over 10-50 repeats on a page already decoded, for boy @72 dpi, colorbook @150 dpi, watchmaker and cable @300 dpi; cold: Criterion parse plus first render vs one unrepeated libdjvulibre open+decode plus the render mean. Encode: examples/encoder_parity_scorecard.rs renders each corpus page to PPM/PBM with ddjvu, then times c44 or cjb2 against the djvu-rs PageEncoder (Photo or Lossless profile), both as subprocess workers writing a file, median of 5 runs, with ddjvu decode fidelity checks (PSNR/SSIM for IW44, pixel-exact for JB2). |
| **Metric** | throughput |
| **Hardware** | Apple M1 Max (10 cores), macOS arm64; the 2026-10-06 encode re-run ran under background load (load average about 10), each djvu-rs/DjVuLibre pair back to back. |
| **Compiler and flags** | djvu-rs: Rust 1.98 for the 2026-10-03/06 comparison runs (older tables Rust 1.92.0); Cargo.toml [profile.release] and [profile.bench] set lto = "fat", codegen-units = 1 (the BENCHMARKS_RESULTS.md header still says opt-level 3 with thin LTO, from the 2026-05-17 run). DjVuLibre 3.5.29: installed with 'brew install djvulibre' per scripts/bench_djvulibre.sh, library build flags not stated; render harness scripts/djvulibre_bench.c compiled with cc -O2 against ddjvuapi. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Adoption** | 11 stars; about 13k crates.io downloads of djvu-rs |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/matyushkin/djvu-rs) · [benchmark](https://github.com/matyushkin/djvu-rs/blob/main/BENCHMARKS_RESULTS.md) |

## Verdict

These are first-party runs on one Apple M1 Max against Homebrew DjVuLibre 3.5.29 (build flags not stated; the C harness was built with cc -O2), with djvu-rs on Rust 1.98, fat LTO and codegen-units 1. Warm Criterion render_pixmap beat libdjvulibre ddjvu_page_render render-only by 1.4-2.0x, but the djvu-rs side reuses cached RGB backgrounds and masks that DjVuLibre recomputes on every call. The encoder parity scorecard (subprocess medians of 5, under background load) has djvu-rs 3.1-3.5x faster than c44 and cjb2 on large pages, with ddjvu-checked fidelity and sizes of 0.952-1.040x.

## Use it when

- You need DjVu decode, render or export inside a Rust, Python or browser application and cannot link GPL-licensed DjVuLibre.
- Viewer-style workloads that re-render the same pages (zoom, tiles, page turns): the per-page caches make the second and later renders much cheaper than the first.
- Batch conversion of scans to DjVu: on large pages the IW44 Photo and JB2 Lossless profiles ran about 3.1-3.5x faster than c44 and cjb2, with files at 0.95-1.04x DjVuLibre's size.
- In-browser DjVu viewing: the WASM build was 6.5-15x faster than djvu.js in the project's own headless Chrome runs.
- DjVu-to-PDF, EPUB or TIFF pipelines that keep the text layer, bookmarks and hyperlinks.

## Skip it when

- You need pixel-identical output to DjVuLibre: no render-equality check is published, and downscales at subsample 4 or more skip later BG44 chunks and use a max-pooled mask.
- Cold, render-once workloads where the warm-render ratios would drive the decision: those ratios rely on caches DjVuLibre does not keep (see gotchas), and the cold comparison is not like-for-like.
- Smallest IW44 files at default settings: the Photo profile codes 100 slices against c44's default 74,89,99, so its files are 2.5-4% larger (parity at an equal slice count). Lossy JB2 and same-size refinement remain experimental.
- Editing legacy FORM:BM44/PM44 pages, which are read-only; the Python bindings also lack encoding and structural edits (merge, split, page insert).
- Projects that need a stable API or a large user base: the crate is at 0.42 (pre-1.0, breaking minor releases), with one maintainer and about 11 stars.

## How it is fast

Each page keeps OnceLock caches of its decoded IW44 image, its YCbCr-to-RGB background at subsample 1, 2 and 4, and its JB2 mask bitmap, so a repeat render only composites. Downscales at subsample 4 or more decode just the first BG44 chunk and read a max-pooled quarter-resolution mask. The ZP arithmetic decoder works in u32 registers (JB2 decode 3.36 ms to 423 us in #180), and YCbCr-to-RGBA and wavelet kernels have NEON, AVX2 and wasm simd128 paths. The compositor has specialised paths (nearest at 1:1, area averaging, popcount bilevel downscale), and an opt-in `parallel` feature splits rows across rayon. Encoder speed comes from inlining the ZP bit coder in the IW44 and BZZ passes (#937, #938) and from a NEON zigzag scatter of IW44 blocks (#939).

## Compared with alternatives

No other DjVu codec is catalogued. Among the catalogued Rust rewrites of C codecs (libbzip2-rs, snap, crabz), pick djvu-rs whenever the format is DjVu, especially when you need a permissive licence instead of GPL DjVuLibre.

## Integration

| | |
|---|---|
| **Form** | crate (also a `djvu` CLI binary, PyPI wheels and an npm WebAssembly package) |
| **Dependencies** | thiserror, wide and the workspace codec crates (djvu-zp, djvu-bzz, djvu-iff, djvu-bitmap, djvu-jb2, djvu-pixmap, djvu-iw44); the default `std` feature adds png and zune-jpeg. Optional: rayon (parallel), miniz_oxide and jpeg-encoder (pdf), zip and flate2 (epub, cbz), tiff, tokio (async), memmap2, Tesseract (ocr-tesseract). Without `std` the codec crates still build as no_std plus alloc. |
| **Minimum toolchain** | Rust 1.88 (edition 2024); the experimental ocr-onnx feature needs 1.91 |
| **Platforms** | any Rust target. CI gates cover x86-64 Linux, aarch64 Linux, Windows MSVC and wasm32. AVX2 is detected at runtime on x86-64, NEON is used on aarch64, and simd128 is a separate wasm build. |
| **Thread safety** | Document and DjVuDocument are Send + Sync (asserted at compile time in tests/send_sync_contract.rs). Page decode caches are filled through OnceLock. DjVuDocumentMut is Send and edits through an exclusive &mut PageMut borrow. |
| **Drop-in for the baseline** | partial: it reads and writes the same DjVu files, but it has a different Rust/Python/JS API (no ddjvuapi C ABI), different CLI commands (`djvu render` and `djvu encode`, not ddjvu, c44 and cjb2) and different render code, so output pixels are not guaranteed to match |

## Gotchas

- Harness flaw behind the warm render rows. render_pixmap on an already-loaded page reuses that page's cached RGB background (bg_rgb_s1/s2/s4) and cached JB2 mask bitmap (src/djvu_render/layers.rs). DjVuLibre's ddjvu_page_render calls bg44-&gt;get_pixmap and fgjb-&gt;get_bitmap on every call, so it rebuilds the IW44 wavelet image, converts colour and blits the JB2 shapes each time (libdjvu/ddjvuapi.cpp, DjVuImage.cpp). Adding back djvu-rs's own stage costs gives these estimates (derived from page data): watchmaker 3.04 ms background-to-RGB plus 2.79 ms mask decode, so 29.8-32.6 ms against 37.8 ms, about 1.16-1.27x rather than 1.4x; cable about 26 ms against 36.8 ms, about 1.4x rather than 1.6x. The 2.0x boy row is most likely cache reuse against recomputation.
- The cold row (13.7 ms against 41.6 ms) sets a Criterion mean of parse plus first render against one unrepeated libdjvulibre open+decode that includes context creation and message waits. The encode rows time the DjVuLibre tools through an extra process spawn (--external-worker), which dominates the 3.8x cable and 4.4x cookbook rows.
- Per-page caches keep decoded backgrounds and masks alive between renders, up to a process-wide budget of 256 MiB by default (render_cache::DEFAULT_BUDGET). Above it, a sweep evicts the least-recently-used layers across all pages. Use render_cache::set_budget to change the budget; set_budget(usize::MAX) removes it.
- SECURITY.md says the crate forbids `unsafe`, but the codec crates opt out with #[allow(unsafe_code)] for NEON, AVX2 and simd128 YCbCr and wavelet kernels; the top-level crate uses #![deny(unsafe_code)] with exceptions.

## Known shortcomings

- DjVuLibre is a Homebrew build with flags unstated; the cold 3.0x row is not like-for-like (the page says so); the 3.8x cable and 4.4x cookbook encode rows mostly measure start-up (cjb2 takes 20.8-28.4 ms even on a near-empty page); renders never checked for equal output.
- Harness flaw: the warm render rows let djvu-rs reuse its per-page cached RGB background (bg_rgb_s1/s2/s4) and cached JB2 mask (src/djvu_render/layers.rs) while DjVuLibre's ddjvu_page_render calls bg44-&gt;get_pixmap and fgjb-&gt;get_bitmap on every call (checked in the barak/djvulibre mirror), redoing IW44 reconstruction and the JB2 blit each time; estimates from page data put watchmaker at about 1.16-1.27x rather than 1.4x, cable at about 1.4x rather than 1.6x, and the boy 2.0x is mostly cache reuse against recomputation. SECURITY.md says the crate forbids unsafe, but djvu-iw44 has #[allow(unsafe_code)] NEON, AVX2 and simd128 kernels; the render cache budget is 256 MiB by default; whether the 2026-10-03 run enabled the parallel feature is unclear.

## Caveats and trade-offs

First-party numbers on one Apple M1 Max; DjVuLibre 3.5.29 is the Homebrew build (flags not stated) driven by a C harness built with cc -O2. Render rows compare a warm Criterion mean with a libdjvulibre render-only mean; there is no pixel or PSNR equality check for renders, and the djvu-rs colorbook 150 dpi path decodes only the first BG44 chunk and samples a cached max-pooled 1/4-resolution mask (BENCHMARKS_RESULTS.md notes), so the 1.4x colorbook row may compare different output quality; the native-resolution cable bilevel row (1.6x) is the cleanest. The 3.0x cold row adds a single unrepeated libdjvulibre open+decode (35.3 ms, including context creation and threaded decode with message waits) to the render mean and sets it against a Criterion mean, and the djvu-rs cold path also decodes only the first BG44 chunk. Encode rows time whole subprocesses on both sides, but the DjVuLibre side pays an extra spawn (the scorecard binary's --external-worker launches c44/cjb2) and DjVuLibre start-up: cjb2 takes 20.8-28.4 ms on both the cable page and the near-empty Chinese cookbook page (67-byte output) in every snapshot from 2026-07-13 to 2026-10-06, while djvu-rs now takes 4.4-7.4 ms on them (2026-10-05/06 runs) (derived from page data), so the README's 3.8x cable row and the 4.4x cookbook row mostly measure fixed start-up cost, not JB2 coding; the large-page encodes (watchmaker 3.1x, goody two-shoes 3.3x, map atlas 3.5x) are the meaningful encode rows. Encode timings moved sharply between snapshots (goody two-shoes djvu-rs 405.8 ms on 2026-10-03, 311.9 ms on 2026-10-05, 111.7 ms on 2026-10-06 after PRs #937-#939) and the latest run was under load. c44's default schedule codes one slice fewer than djvu-rs (74,89,99), so djvu-rs IW44 output is 1.025-1.040x larger at slightly higher PSNR (parity at an equal slice count); JB2 lossless outputs are pixel-exact at 0.952-1.011x cjb2 size. The 2026-07-13 scorecard rows that showed goody two-shoes slower and much larger came from two IW44 encoder bugs fixed on 2026-07-16 and are superseded. No DjVuLibre comparison numbers are published for x86; the github.io dashboard is blocked here. [retier] The warm render rows reuse djvu-rs's per-page cached RGB background (bg_rgb_s1/s2/s4) and cached JB2 mask while DjVuLibre's ddjvu_page_render calls bg44-&gt;get_pixmap and fgjb-&gt;get_bitmap on every call, so the render ratios compare cached reuse with recomputation. SECURITY.md says the crate forbids unsafe, but djvu-iw44 has #[allow(unsafe_code)] NEON, AVX2 and simd128 kernels; the render cache budget is 256 MiB by default; whether the 2026-10-03 run enabled the parallel feature is unclear.

Clean-room MIT implementation written from the public DjVu v3 specification (no GPL code); encoder output is not always smaller than DjVuLibre (README: 1.025 to 1.040x c44 for IW44 and 0.952 to 1.011x cjb2); legacy BM44/PM44 pages are read-only.

## Maintenance

Actively developed (last commit 2026-10-11, v0.42.0, no open issues), MIT-licensed and easy to adopt as a crate, wheel or npm package. Treat its DjVuLibre render ratios as optimistic: the warm rows compare cached pixels against per-call IW44 reconstruction and JB2 blitting in DjVuLibre, and the encode ratios on the large pages are the most like-for-like numbers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now C.
- **Tier reason:** Benchmark code is public (benches/render.rs, scripts/djvulibre_bench.c with scripts/bench_djvulibre.sh, examples/encoder_parity_scorecard.rs) and the djvu-rs toolchain and Apple M1 Max are stated, but DjVuLibre 3.5.29 is a Homebrew install whose build flags are never stated (only the C harness's cc -O2), so not A; first-party numbers, so C. Tier unchanged; the headline range is narrowed because two of its five rows are not like-for-like.
- **Verifier notes:** Real and active project (11 stars, MIT, last commit 2026-10-11, 13,395 crates.io downloads); README numbers are all on BENCHMARKS_RESULTS.md, and the record's caveats about a goody two-shoes loss and an in-process Rust encoder were wrong or stale and are replaced. Shortcomings to record: baseline build flags unstated; cold 3.0x row not like-for-like; 3.8x/4.4x small-page encode rows dominated by start-up cost; renders not checked for equal output; djvu-rs was slower than libdjvulibre as recently as 2026-06-18.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-68 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/BENCHMARKS_RESULTS.md>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/scripts/bench_djvulibre.sh>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/scripts/djvulibre_bench.c>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/scripts/djvulibre_compare.py>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/examples/encoder_parity_scorecard.rs>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/docs/encoder-parity.md>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/benches/render.rs>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/.github/workflows/bench.yml>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/Cargo.toml>
  - <https://github.com/matyushkin/djvu-rs>
  - <https://github.com/matyushkin/djvu-rs/commits/main>
  - <https://crates.io/api/v1/crates/djvu-rs>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/BENCHMARKS_RESULTS.md>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/scripts/djvulibre_bench.c>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/scripts/bench_djvulibre.sh>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/benches/render.rs>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/examples/encoder_parity_scorecard.rs>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/docs/encoder-parity.md>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/PERF_EXPERIMENTS.md>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/EXPERIMENTS_INDEX.md>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/docs/api-compatibility.md>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/docs/feature-matrix.md>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/.github/workflows/bench.yml>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/src/djvu_document/page.rs>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/src/djvu_render/pipeline.rs>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/src/djvu_render/layers.rs>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/src/djvu_render/cache.rs>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/src/djvu_render/mod.rs>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/src/djvu_render/composite.rs>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/src/render_cache.rs>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/src/iw44_encode.rs>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/src/jb2_encode.rs>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/src/iw44.rs>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/crates/djvu-iw44/Cargo.toml>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/crates/djvu-iw44/src/lib.rs>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/crates/djvu-iw44/src/image.rs>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/crates/djvu-iw44/src/wavelet.rs>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/crates/djvu-iw44/src/color.rs>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/crates/djvu-iw44/src/plane.rs>
  - <https://raw.githubusercontent.com/matyushkin/djvu-rs/HEAD/crates/djvu-iw44/src/encode/mod.rs>
  - <https://github.com/matyushkin/djvu-rs/tree/main/src>
  - <https://github.com/matyushkin/djvu-rs/tree/main/src/djvu_document>
  - <https://github.com/matyushkin/djvu-rs/tree/main/src/djvu_render>
  - <https://github.com/matyushkin/djvu-rs/tree/main/crates/djvu-iw44/src>
  - <https://github.com/matyushkin/djvu-rs/commit/3e64096>
  - <https://github.com/matyushkin/djvu-rs/issues?q=is%3Aissue+is%3Aopen+label%3Abug>
  - <https://github.com/matyushkin/djvu-rs/issues>
  - <https://raw.githubusercontent.com/barak/djvulibre/master/libdjvu/ddjvuapi.cpp>
  - <https://raw.githubusercontent.com/barak/djvulibre/master/libdjvu/DjVuImage.cpp>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/matyushkin/djvu-rs`) · [data/wave14/enrich/raw/github_com_matyushkin_djvu_rs.json](../../../data/wave14/enrich/raw/github_com_matyushkin_djvu_rs.json) (enrichment confidence 0.7)

</details>
