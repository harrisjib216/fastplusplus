# Photon (photon-rs)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Pure-Rust image-effects library that also ships as WebAssembly for browsers and Node; one mixed first-party result against the libvips CLI.

| | |
|---|---|
| **Beats** | libvips (vips CLI, Windows vips.exe) |
| **Claimed result** | Wiki Benchmarks page (2020-06-04, photon-rs 0.2.0): PNG invert and save, Photon criterion [238.46 ms 244.87 ms 254.62 ms] vs libvips vips.exe 915.1 ms +/- 36.0 ms (10 runs), about 3.7x faster (derived from page data). JPG invert and save, Photon [114.67 ms 117.26 ms 122.22 ms] vs libvips 84.2 ms +/- 12.0 ms (18 runs), so libvips is about 1.39x faster (derived from page data). Mixed result: one win (PNG), one loss (JPG). |
| **Workload** | Invert all pixels of one image and save it again, once for a PNG and once for a JPG; Photon timed with criterion (cargo bench), libvips timed with hyperfine on the vips.exe command line. |
| **Metric** | latency |
| **Adoption** | 3.9k stars |
| **Last commit** | 2026-09-18 |
| **Links** | [repository](https://github.com/silvia-odwyer/photon) · [benchmark](https://github.com/silvia-odwyer/photon/wiki/Benchmarks) |

## Verdict

One first-party wiki page (2020-06-04, photon-rs 0.2.0 with image 0.21.1) timed open, invert and save inside a criterion loop (10 samples) against libvips's Windows vips.exe under hyperfine, which includes process start-up. Photon won the PNG case (244.87 ms vs 915.1 ms) and lost the JPG case (117.26 ms vs 84.2 ms). No CPU, OS, image size or encoder settings are given, and the PNG bench code was never committed. Reading the code adds that the timed work is dominated by image-crate decode and encode: Photon's own step is a scalar invert loop, and save_image always writes RGBA8 with image-crate defaults, while vips used its own encoder defaults. So the PNG gap most likely reflects codecs, settings and process start-up rather than Photon's pixel code.

## Use it when

- Browser or Node.js apps that need client-side photo filters, tints, channel edits or simple resizes without a native addon (no libvips or sharp binary to install).
- Rust apps that want a large catalogue of ready-made Instagram-style effects and colour adjustments on 8-bit RGBA images, where the code to write matters more than raw throughput.
- Serverless or edge runtimes that accept WASM but not native modules (issue #138 discusses Cloudflare Workers).
- Single-image, interactive edits where per-call cost is tens to hundreds of milliseconds and a lazy streaming pipeline is not needed.

## Skip it when

- High-throughput server pipelines (thumbnails, batch conversion): libvips is threaded and streams; Photon decodes the whole image to RGBA8 in memory and runs one thread. Its own wiki shows libvips faster on the JPG case (84.2 ms vs 117.26 ms).
- Quality or speed-critical resampling: resize is the image crate's generic imageops::resize. fast_image_resize (catalogued) uses SIMD and beats libvips on Lanczos3.
- 16-bit, HDR, float or colour-managed work: everything is converted to 8-bit RGBA on load (issue #155 asks for 16-bit grayscale and is open), there is no ICC handling, and blend() treats sRGB bytes as linear (it calls LinSrgba::new(...).into_linear(), which is a no-op), so blending happens on gamma-encoded values.
- Code that must not panic on bad input: many public functions unwrap() decode and encode results (new_from_byteslice, get_bytes, get_bytes_jpeg), and in WASM a panic shows up as 'RuntimeError: unreachable' (issues #45, #134 and #175 are open).
- Projects that need fixes on a release: crates.io's latest is 0.3.3 (2025-05-10), and the 2026 adjustments module and memory-copy fixes are only on master.

## How it is fast

There is no special technique: the effects are scalar, single-threaded loops over the RGBA byte buffer (for example, invert is a step_by(4) loop computing 255 - v), with no SIMD intrinsics, no threading (no rayon) and no unsafe code. Decoding, encoding, resize (image::imageops::resize, a separable filter) and the 90-degree rotation steps come from the image crate 0.24.8, and gaussian_blur is a three-pass box-blur approximation. In the browser the gain is compiling these loops to WebAssembly rather than running them in JavaScript; the README says it 'run[s] at near-native speed' but publishes no WASM numbers.

## Compared with alternatives

Pick Photon when you need a ready-made effects catalogue that runs unchanged in the browser, Node and native Rust. For resizing, pick fast_image_resize (SIMD, measured faster than libvips). For OpenCV-style kernels, pick kornia-rs. For server throughput, use libvips itself.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | image 0.24.8 (gif, jpeg, png, tiff, webp, bmp and other codecs), palette 0.6.1, imageproc 0.23, rusttype 0.9.2, rand 0.7, base64 0.13, serde, thiserror, time, perlin2d, instant; the default enable_wasm feature also pulls in wasm-bindgen, web-sys, js-sys, node-sys and console_error_panic_hook (turn it off with default-features = false for native builds) |
| **Minimum toolchain** | Rust 2021 edition (Rust 1.56 or later); no rust-version is declared, and CI runs on stable |
| **Platforms** | any Rust target (pure Rust, scalar code), plus wasm32 builds for browsers and Node |
| **Thread safety** | not documented; PhotonImage is a plain owned struct (Vec&lt;u8&gt;, width, height) and functions take &mut or &, with no internal threads or shared state |
| **Drop-in for the baseline** | no |

## Gotchas

- The native get_raw_pixels_slice() (no copy) exists only when enable_wasm is off. With the default features you get get_raw_pixels(), which clones the whole buffer.
- blend() panics unless the first image is no larger than the second, but it then indexes the second image at the same linear byte offset. If the second image is wider, rows misalign and the wrong pixels are blended. It also lowercases the blend-mode string inside the per-pixel loop, which allocates once per pixel.
- Open issue #119: some filters skip the last pixel. The loop bound 'len() - 4' is still present in primary, inc_brightness and dec_brightness in effects.rs (monochrome.rs has been fixed). rotate() truncates the angle to an integer, and issues #170 and #198 report noise and bugs on rotation.
- In JavaScript, PhotonImage objects live in WASM linear memory. Issue #175 hit an out-of-memory error after about 174 new_from_base64 calls in Node 20. PR #227 (2026-09) reduced copies, but callers should still free images explicitly.

## Known shortcomings

- Mixed result: PNG invert 244.87 ms against vips.exe 915.1 ms (about 3.7x) but JPG 117.26 against 84.2 ms (libvips about 1.39x faster); an in-process criterion run against the vips CLI including process start-up, with no CPU, OS or versions; the committed bench (b802192, 2020-06-04, photon 0.2.0) covers only input.jpg and the PNG bench was never committed. The operation is invert, not resampling.
- Enricher (e121, 2026-10-05): no SIMD, threads or unsafe code; invert is a scalar step_by(4) loop. The wiki-timed work is mostly image-crate decode and encode (save_image always writes RGBA8 at image-crate defaults), so the PNG win is likely codecs plus vips.exe start-up rather than Photon pixel code. Stays C; no independent numbers found. Bugs not behind the numbers: blend() reads the second image by linear offset so rows misalign when it is wider; the blend-mode string is lowercased per pixel; LinSrgba into_linear is a no-op so blends operate on gamma values; open #119 last-pixel skip remains in primary, inc_brightness and dec_brightness. The current adjustments bench mutates one cloned image every iteration (unpublished numbers).

## Caveats and trade-offs

Mixed result: Photon wins the PNG invert-and-save case (about 3.7x, derived from page data) but libvips wins the JPG case (about 1.39x, derived from page data). First-party wiki numbers from 2020-06-04 (photon-rs 0.2.0 at that commit), never updated; no CPU, OS, compiler, rustc or libvips version, image dimensions or encoder settings (PNG compression level, JPEG quality) are given, so the PNG gap may reflect encoder settings rather than the pixel operation. The two sides are timed differently: Photon in an in-process criterion loop (10 samples) of open, invert and save; libvips through hyperfine on the Windows vips.exe command line, which includes process start-up. Hyperfine reports only 6.2 ms user and 13.1 ms system CPU for the 915 ms PNG run, so its CPU accounting does not cover the vips work. The bench at the matching commit b802192 (crate/benches/photon_benchmark.rs, 2020-06-04) opens examples/input_images/input.jpg and saves output.jpg; no PNG variant was ever committed and the PNG test image is an imgur link, so the PNG number (the only win) cannot be reproduced from the repo. The page introduction promises ImageMagick and PIL comparisons but only libvips numbers appear. Invert is a trivial per-pixel colour op and says nothing about resampling; the current bench (crate/benches/photon_benchmark.rs) adds resize_png/resize_jpg with Lanczos3 but no published numbers against any baseline. Baseline is neither ImageMagick nor stb_image_resize.

Rust crate that also compiles to WebAssembly for browser and Node.js; about 96 image functions (channel ops, filters, color effects, resize). Native Rust, not a C or C++ API.

## Maintenance

Actively maintained (Apache-2.0, 3.9k stars, last commit 2026-09-18, with community bug and memory fixes through 2026), but releases lag master and no benchmark has been published since 2020.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The wiki Benchmarks page (5 revisions, all by the author on 2020-06-04) shows hyperfine output for vips.exe and criterion output for Photon, matching the record exactly, but gives no CPU, OS, compiler, Rust/libvips versions or image sizes, and the PNG bench code was never committed. First-party numbers with partial methodology, so C.
- **Verifier notes:** Numbers verified verbatim on the wiki page and its revision history; the record's bench path benches/photon_benchmark.rs is really crate/benches/photon_benchmark.rs, and at the wiki's date it only benchmarked a JPG. Metadata checked: Apache-2.0 (LICENSE.md), 3.9k stars, 190 forks, not archived, not a fork, last commit 2026-09-18. Keep as a C entry with the mixed-result and category-fit shortcomings.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** first-party wiki timings
- **Pages the verifier opened:**
  - <https://github.com/silvia-odwyer/photon/wiki/Benchmarks>
  - <https://github.com/silvia-odwyer/photon/wiki/Benchmarks/_history>
  - <https://github.com/silvia-odwyer/photon>
  - <https://github.com/silvia-odwyer/photon/commits>
  - <https://github.com/silvia-odwyer/photon/commits/master/crate/benches/photon_benchmark.rs>
  - <https://raw.githubusercontent.com/silvia-odwyer/photon/HEAD/README.md>
  - <https://raw.githubusercontent.com/silvia-odwyer/photon/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/silvia-odwyer/photon/HEAD/crate/Cargo.toml>
  - <https://raw.githubusercontent.com/silvia-odwyer/photon/HEAD/crate/benches/photon_benchmark.rs>
  - <https://raw.githubusercontent.com/silvia-odwyer/photon/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/silvia-odwyer/photon/b802192/crate/benches/photon_benchmark.rs>
  - <https://raw.githubusercontent.com/silvia-odwyer/photon/b802192/crate/Cargo.toml>
- **Sources the enricher read:**
  - <https://github.com/silvia-odwyer/photon/wiki/Benchmarks>
  - <https://github.com/silvia-odwyer/photon/commits/master>
  - <https://github.com/silvia-odwyer/photon/issues?q=is%3Aissue+performance>
  - <https://github.com/silvia-odwyer/photon/issues?q=is%3Aissue+is%3Aopen>
  - <https://github.com/silvia-odwyer/photon/issues/13>
  - <https://github.com/silvia-odwyer/photon/issues/36>
  - <https://github.com/silvia-odwyer/photon/issues/119>
  - <https://github.com/silvia-odwyer/photon/issues/131>
  - <https://github.com/silvia-odwyer/photon/issues/144>
  - <https://github.com/silvia-odwyer/photon/issues/175>
  - <https://raw.githubusercontent.com/silvia-odwyer/photon/HEAD/README.md>
  - <https://raw.githubusercontent.com/silvia-odwyer/photon/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/silvia-odwyer/photon/HEAD/crate/Cargo.toml>
  - <https://raw.githubusercontent.com/silvia-odwyer/photon/HEAD/crate/benches/photon_benchmark.rs>
  - <https://raw.githubusercontent.com/silvia-odwyer/photon/HEAD/crate/src/lib.rs>
  - <https://raw.githubusercontent.com/silvia-odwyer/photon/HEAD/crate/src/native.rs>
  - <https://raw.githubusercontent.com/silvia-odwyer/photon/HEAD/crate/src/channels.rs>
  - <https://raw.githubusercontent.com/silvia-odwyer/photon/HEAD/crate/src/transform.rs>
  - <https://raw.githubusercontent.com/silvia-odwyer/photon/HEAD/crate/src/effects.rs>
  - <https://raw.githubusercontent.com/silvia-odwyer/photon/HEAD/crate/src/helpers.rs>
  - <https://raw.githubusercontent.com/silvia-odwyer/photon/HEAD/crate/src/multiple.rs>
  - <https://raw.githubusercontent.com/silvia-odwyer/photon/HEAD/crate/src/iter.rs>
  - <https://raw.githubusercontent.com/silvia-odwyer/photon/HEAD/crate/src/conv.rs>
  - <https://raw.githubusercontent.com/silvia-odwyer/photon/HEAD/crate/src/filters.rs>
  - <https://raw.githubusercontent.com/silvia-odwyer/photon/HEAD/crate/src/colour_spaces.rs>
  - <https://raw.githubusercontent.com/silvia-odwyer/photon/HEAD/crate/src/monochrome.rs>
  - <https://raw.githubusercontent.com/silvia-odwyer/photon/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/silvia-odwyer/photon/b802192/crate/benches/photon_benchmark.rs>
  - <https://raw.githubusercontent.com/silvia-odwyer/photon/b802192/crate/Cargo.toml>
  - <https://crates.io/api/v1/crates/photon-rs>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/silvia-odwyer/photon`) · [data/wave10/enrich/raw/github_com_silvia_odwyer_photon.json](../../../data/wave10/enrich/raw/github_com_silvia_odwyer_photon.json) (enrichment confidence 0.75)

</details>
