# fast_image_resize

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Rust SIMD image-resize crate (SSE4.1/AVX2/NEON/wasm); with AVX2 it is 1.3-1.6x faster than libvips and about 10x faster than the image/resize crates.

| | |
|---|---|
| **Beats** | libvips 8.15.1 (single-threaded); also the Rust image 0.25.6 and resize 0.8.9 crates |
| **Claimed result** | RGB8 Lanczos3: 13.52 ms (AVX2) vs libvips 17.31 ms (about 1.28x, derived from page data), image 176.09 ms, resize 137.70 ms. RGB8 Bilinear: 3.55 ms vs libvips 5.58 ms (about 1.57x). RGBA8 Lanczos3: 24.08 ms vs libvips 332.42 ms (libvips resampling in float after premultiply) and resize 218.65 ms. The RGB8 Box row (2.65 ms vs 61.51 ms) is not like-for-like: libvips vips_shrink with a non-integer factor runs a box pre-shrink plus a Lanczos3 reduce. The large margins are against the pure-Rust crates; on SSE4.1-only x86 and on arm64 Neoverse-N1 libvips wins the Bilinear and Bicubic RGB8 rows and the NEON Lanczos3 lead is 1.10x. |
| **Workload** | Single-threaded resize of a 4928x3279 image to 852x567 (RGB8, RGBA8 with alpha multiply/divide, L8) with Nearest, Box, Bilinear, Bicubic and Lanczos3 filters, criterion timings. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 5950X, DDR4 4000 MHz, Ubuntu 24.04 |
| **Compiler and flags** | Rust 1.97.1, cargo bench with criterion 0.7.0; Cargo.toml [profile.release] opt-level = 3, incremental = true, lto and codegen-units commented out (the image and resize crates get codegen-units = 1); no target-cpu flag; the fir rows force each CPU extension (none, SSE4.1, AVX2) through Resizer::set_cpu_extensions. libvips 8.15.1 is the Ubuntu 24.04 system library called through the libvips 1.7 Rust binding, so its build flags are the distro's. |
| **Adoption** | 463 stars, 42 forks; crates.io: 20,443,908 total downloads, 4,728,314 recent (crates.io API, 2026-10-03) |
| **Last commit** | 2026-08-20 |
| **Links** | [repository](https://github.com/Cykooz/fast_image_resize) · [benchmark](https://github.com/Cykooz/fast_image_resize/blob/main/benchmarks-x86_64.md) |

## Verdict

The author's criterion benches (mean point estimate, single thread, release profile opt-level 3, no LTO, no target-cpu, Rust 1.97.1, Ryzen 9 5950X, Ubuntu 24.04) resize a 4928x3279 photo to 852x567. RGB8 Lanczos3 takes 13.52 ms with AVX2, against 17.31 ms for libvips 8.15.1 (Ubuntu package, concurrency 1, cache off), 176.09 ms for image 0.25.6 and 137.70 ms for resize 0.8.9: 1.28x, 13x and 10x (derived from page data). The RGBA8 and Box margins over libvips are not like for like: libvips premultiplies into float for alpha, and its Box row is not a box filter. No correctness bug was found behind the numbers.

## Use it when

- Rust services that make thumbnails or previews: downscaling large 8-bit RGB/RGBA photos on x86-64 with AVX2, where it beats the image crate by about 13x and the resize crate by about 10x at Lanczos3.
- Replacing a single-threaded libvips reduce in a Rust pipeline on AVX2 machines: RGB8 Lanczos3 13.52 vs 17.31 ms, Bilinear 3.55 vs 5.58 ms, L8 Lanczos3 4.26 vs 12.54 ms on a Ryzen 9 5950X.
- 16-bit, f32 or alpha formats (RGBA16, LA8, RGBA32F) where the integer and float SIMD kernels have a larger lead over libvips (RGBA16 Lanczos3 53.51 vs 345.06 ms), with the caveat that libvips' alpha path in this harness runs in float.
- WebAssembly or no_std targets that need SIMD resizing without a C dependency (wasm32 SIMD128 paths; the 'no_std' feature since 6.0.0).

## Skip it when

- C or C++ codebases: there is no C API, and the margin over libvips (C, with C++ bindings) on RGB8 is only 1.3-1.6x with AVX2.
- CPUs without AVX2: with only SSE4.1, libvips is faster on RGB8 Bilinear (5.58 vs 5.83 ms) and Bicubic (9.92 vs 10.34 ms). On an ARM Neoverse-N1, libvips wins RGB8 Bilinear (26.85 vs 29.21 ms) and fir's NEON Lanczos3 lead is about 1.1x (79.72 vs 87.42 ms).
- Targets with no SIMD path: the portable 'fir rust' path is about 2x slower than libvips on RGB8 (Lanczos3 37.26 vs 17.31 ms), and f32 has no NEON or wasm path in the released 6.1.0.
- Gamma-correct resizing out of the box: it filters stored values (for example sRGB) directly; linearize with PixelComponentMapper (create_srgb_mapper) first and pay for the extra passes.
- Full image pipelines (decode, colour management, sharpen, encode): this crate only resamples.

## How it is fast

It uses the Pillow-SIMD approach (the source says so): weights for each output pixel are precomputed once per resize as an adaptive-size kernel and quantized to i16 fixed point, with the precision chosen per filter so sums fit in i32. Separable passes then run as multiply-add kernels (_mm256_madd_epi16 plus byte shuffles on AVX2, with equivalent SSE4.1, NEON and wasm SIMD128 paths). For u8 images the vertical pass runs first over only the source columns the horizontal kernel will touch. 4-row blocking is used in the horizontal pass. The CPU extension is detected at run time and can be forced with an unsafe setter. Alpha premultiply and divide are separate SIMD passes, and an optional rayon feature splits the work across threads.

## Compared with alternatives

Pick it over Pillow-SIMD (whose C convolution design it ports) and libvips when you are in Rust or wasm and want a dependency-free crate with AVX2, NEON and SIMD128 kernels for 8-bit, 16-bit and f32 pixels. In C or C++, stb-image-resize-opt, Skia or libvips avoid an FFI shim, and tir (tinyexr) is the closer fit for f32 HDR resizing.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | cfg-if, num-traits, thiserror (plus document-features under std); optional image, bytemuck, rayon, and cpufeatures for no_std |
| **Minimum toolchain** | Rust 1.87 (rust-version in Cargo.toml); avoid Rust 1.95-1.96 for wasm32 SIMD128 builds (an LLVM regression breaks U8x4 alpha division, per the README) |
| **Platforms** | x86-64 (SSE4.1 and AVX2 detected at run time), aarch64 (NEON), wasm32 (SIMD128), portable Rust fallback elsewhere; std or no_std |
| **Thread safety** | Resizer::resize takes &mut self and keeps internal scratch buffers, so use one Resizer per thread; the 'rayon' feature parallelizes a single resize internally. |
| **Drop-in for the baseline** | no |

## Gotchas

- ResizeOptions defaults to premultiplying and dividing by alpha for alpha formats, which nearly doubles RGBA8 Lanczos3 time (24.08 vs 13.52 ms for RGB8); call use_alpha(false) for opaque or already-premultiplied data.
- Resizer::set_cpu_extensions is unsafe: forcing AVX2 or NEON on a CPU without it is undefined behaviour.
- Version 6.0.0 made 'std' a default feature (5.6.0 was yanked for the same break), so default-features = false users must add 'std' or 'no_std' explicitly. Before 6.1.0, a one-thread rayon pool could deadlock on ResizeAlg::Nearest.
- Past SIMD alpha-division bugs (NEON U8x2 multiply in 5.1.3, SSE4.1/AVX2/NEON U16x2 and NEON U16x4 divide in 5.1.4) were fixed in point releases; pin a recent version if you resize LA/LA16 images.

## Known shortcomings

- Rust crate (language-filter mismatch; C++ use needs FFI). Tier A on public criterion benches (benches/bench_compare_rgb.rs, benches/utils/resize_functions.rs; Rust 1.97.1, opt-level 3, Ryzen 9 5950X), but it beats libvips only 1.28x on Lanczos3 RGB8 and was never tested against ImageMagick or stb_image_resize. Harness work differs: libvips Box uses shrink, libvips's alpha path runs in float, and libvips timings include the output copy. The page cites crate 6.0.1, a version not on crates.io.
- The RGB8 Box row (2.65 ms versus libvips 61.51 ms) is a harness artefact: libvips 8.15.1 vips_shrink with a non-integer factor does a box pre-shrink plus a Lanczos3 reduce, so it exceeds libvips' own Lanczos3 17.31 ms (retier-06 drops the row). The lead depends on AVX2: the SSE4.1 path loses RGB8 Bilinear and Bicubic to libvips (5.83 vs 5.58 ms, 10.34 vs 9.92 ms), and on arm64 Neoverse-N1 libvips wins Bilinear (26.85 vs 29.21 ms) with the NEON Lanczos3 lead only 1.10x. dev.md's RESULTS_LIFETIME can reuse stale competitor rows. Rust only, no C ABI.

## Caveats and trade-offs

Rust crate, not C++ or C: it is outside the default C++ language filter for this category and would need an FFI wrapper for C++ use. It does not compare against ImageMagick or stb_image_resize, the category's named baselines; the closest incumbent measured is libvips 8.15.1, and the RGB8 lead over it is modest (Lanczos3 13.52 ms vs 17.31 ms, about 1.28x; Bilinear 3.55 ms vs 5.58 ms, about 1.57x; derived from page data). The large margins are against the pure-Rust image and resize crates. The harness does not make libvips do identical work: libvips Box uses vips_shrink instead of a box-filter convolution; the alpha rows run libvips premultiply/unpremultiply, which produce float images (the harness casts back to the band format), so libvips resamples RGBA/LA in float while fir works in integers, which accounts for much of the RGBA8 Lanczos3 gap (332.42 ms vs 24.08 ms); and each libvips iteration builds a new pipeline and copies the result out with image_write_to_memory, while fir writes into a preallocated image with a reused Resizer, an overhead that dominates the Nearest rows. libvips runs with concurrency 1 and its cache disabled. The benchmarks are the author's own, on the author's machine. The page header says fast_image_resize 6.0.1, which is not a published crates.io version (6.0.0 and 6.1.0 are); the page was last updated on 2026-07-21 with the 6.1.0 release. The README's copy of the RGB8 table comes from an older run (libvips Lanczos3 16.07 ms vs fir AVX2 13.26 ms). The ARM64 and WASM32 benchmark pages were not opened.

Rust crate, not callable from C++ without writing a C shim (a Python binding cykooz.resizer exists). Supports u8/u16/f32 pixel types, SSE4.1, AVX2, NEON and WASM SIMD, and multithreading. Convolution (Box/Bilinear/Bicubic/Lanczos3) plus Nearest.

## Maintenance

Actively maintained by one author (6.1.0 on 2026-07-21, last commit 2026-08-20, with wasm f32 SIMD unreleased), dual MIT/Apache-2.0, 463 stars, about 20.4 million crates.io downloads and 128 reverse dependencies, 2 open issues and every bug-labelled issue closed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** benchmarks-x86_64.md is generated by public criterion benches (benches/bench_compare_rgb.rs, bench_compare_rgba.rs, benches/utils/resize_functions.rs) that time fir against libvips 8.15.1, image and resize in one harness, and the page states Rust 1.97.1, the AMD Ryzen 9 5950X and the crate versions while Cargo.toml fixes the release profile (opt-level 3, LTO off). Every claimed number matches the page; the measurements are first-party but fully reproducible, so A stands.
- **Verifier notes:** Numbers verified against benchmarks-x86_64.md and the harness source. The language field already reads Rust, which is correct; verify.py apply ignores the language key in corrections, so a decisions.json override is needed only if another stage set it differently. Flag the language-filter mismatch: this is a Rust entry in a C++-first category, and the libvips comparison is not like for like on the Box and alpha rows.
- **Fields the verifier corrected:** `compiler_and_flags`, `stars_or_usage`, `caveats`, `claimed_speedup`
- **Pages the verifier opened:**
  - <https://github.com/Cykooz/fast_image_resize>
  - <https://github.com/Cykooz/fast_image_resize/commits/main>
  - <https://github.com/Cykooz/fast_image_resize/commits/main/benchmarks-x86_64.md>
  - <https://github.com/Cykooz/fast_image_resize/tree/main/benches/utils>
  - <https://raw.githubusercontent.com/Cykooz/fast_image_resize/main/benchmarks-x86_64.md>
  - <https://raw.githubusercontent.com/Cykooz/fast_image_resize/main/Cargo.toml>
  - <https://raw.githubusercontent.com/Cykooz/fast_image_resize/main/README.md>
  - <https://raw.githubusercontent.com/Cykooz/fast_image_resize/main/CHANGELOG.md>
  - <https://raw.githubusercontent.com/Cykooz/fast_image_resize/main/benches/bench_compare_rgb.rs>
  - <https://raw.githubusercontent.com/Cykooz/fast_image_resize/main/benches/utils/resize_functions.rs>
  - <https://raw.githubusercontent.com/Cykooz/fast_image_resize/main/benches/utils/bencher.rs>
  - <https://crates.io/api/v1/crates/fast_image_resize>
- **Sources the enricher read:**
  - <https://github.com/Cykooz/fast_image_resize>
  - <https://github.com/Cykooz/fast_image_resize/tree/main/src/convolution>
  - <https://github.com/Cykooz/fast_image_resize/issues>
  - <https://github.com/Cykooz/fast_image_resize/issues?q=is%3Aissue>
  - <https://github.com/Cykooz/fast_image_resize/issues?q=is%3Aissue+label%3Abug>
  - <https://github.com/Cykooz/fast_image_resize/issues/12>
  - <https://github.com/Cykooz/fast_image_resize/issues/39>
  - <https://github.com/Cykooz/fast_image_resize/issues/60>
  - <https://raw.githubusercontent.com/Cykooz/fast_image_resize/main/README.md>
  - <https://raw.githubusercontent.com/Cykooz/fast_image_resize/main/benchmarks-x86_64.md>
  - <https://raw.githubusercontent.com/Cykooz/fast_image_resize/main/benchmarks-arm64.md>
  - <https://raw.githubusercontent.com/Cykooz/fast_image_resize/main/benchmarks-wasm32.md>
  - <https://raw.githubusercontent.com/Cykooz/fast_image_resize/main/Cargo.toml>
  - <https://raw.githubusercontent.com/Cykooz/fast_image_resize/main/CHANGELOG.md>
  - <https://raw.githubusercontent.com/Cykooz/fast_image_resize/main/dev.md>
  - <https://raw.githubusercontent.com/Cykooz/fast_image_resize/main/resizer/Cargo.toml>
  - <https://raw.githubusercontent.com/Cykooz/fast_image_resize/main/benches/bench_compare_rgb.rs>
  - <https://raw.githubusercontent.com/Cykooz/fast_image_resize/main/benches/bench_compare_rgba.rs>
  - <https://raw.githubusercontent.com/Cykooz/fast_image_resize/main/benches/utils/resize_functions.rs>
  - <https://raw.githubusercontent.com/Cykooz/fast_image_resize/main/benches/utils/bencher.rs>
  - <https://raw.githubusercontent.com/Cykooz/fast_image_resize/main/benches/utils/mod.rs>
  - <https://raw.githubusercontent.com/Cykooz/fast_image_resize/main/benches/utils/results.rs>
  - <https://raw.githubusercontent.com/Cykooz/fast_image_resize/main/src/lib.rs>
  - <https://raw.githubusercontent.com/Cykooz/fast_image_resize/main/src/resizer.rs>
  - <https://raw.githubusercontent.com/Cykooz/fast_image_resize/main/src/cpu_extensions.rs>
  - <https://raw.githubusercontent.com/Cykooz/fast_image_resize/main/src/convolution/mod.rs>
  - <https://raw.githubusercontent.com/Cykooz/fast_image_resize/main/src/convolution/filters.rs>
  - <https://raw.githubusercontent.com/Cykooz/fast_image_resize/main/src/convolution/optimisations.rs>
  - <https://raw.githubusercontent.com/Cykooz/fast_image_resize/main/src/convolution/u8x3/avx2.rs>
  - <https://raw.githubusercontent.com/libvips/libvips/v8.15.1/libvips/resample/shrink.c>
  - <https://raw.githubusercontent.com/libvips/libvips/v8.15.1/libvips/resample/reduceh.cpp>
  - <https://crates.io/api/v1/crates/fast_image_resize/reverse_dependencies?per_page=1>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/cykooz/fast_image_resize`) · [data/wave10/enrich/raw/github_com_cykooz_fast_image_resize.json](../../../data/wave10/enrich/raw/github_com_cykooz_fast_image_resize.json) (enrichment confidence 0.85)

</details>
