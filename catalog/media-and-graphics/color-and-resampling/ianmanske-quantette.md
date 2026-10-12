# quantette

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Rust palette quantizer (Wu and Oklab k-means); author's 4-thread runs show 3-14x faster than libimagequant on large opaque photos.

| | |
|---|---|
| **Beats** | libimagequant (imagequant crate 4.4.1, the engine behind pngquant); also color_quant 1.1.0 (NeuQuant) and exoquant 0.2.0 |
| **Claimed result** | Own harness, 256 colours, 4 threads for quantette and imagequant, no dithering: quantette k-means (quality comparable to imagequant by the doc's DSSIM table) is 3.3x to 14.1x faster than imagequant 4.4.1 at default settings on the eleven 5-6.7k-wide photos (median about 7.6x; Akihabara 97 ms versus 1044 ms, about 10.8x) and 2.9x to 8.6x on the 1920-wide versions (median about 4.9x), all derived from page data. With dithering the gap is 1.13x to 5.1x on the large photos (Futuristic 318 ms versus 360 ms; median about 2.6x) and 3.3x to 8.4x at 1920 wide (derived). Wu sRGB (25 ms on Akihabara, 8x to 46x faster than imagequant) produces clearly worse output (DSSIM 0.0072 versus 0.0044 on Akihabara), so its ratio is not a like-for-like speedup. In the imazen/zenquant README (50 images, 2026-03-04, default dithering, approximate timing) quantette 0.5 k-means takes about 265 ms versus imagequant 315 ms at speed 4 and 546 ms at speed 1, about 1.2x and 2.1x (derived), and color_quant is faster than both at 180 ms. |
| **Workload** | 256-colour image quantization plus remapping of 11 Unsplash photos at about 5500 to 6700 px wide and at 1920 px wide, with and without dithering, total ms per image averaged over 30 trials; Wu, k-means and imagequant columns on 4 threads, color_quant and exoquant single-threaded. |
| **Metric** | latency |
| **Hardware** | not stated |
| **Compiler and flags** | rustc with -C target-feature=+avx2 |
| **Adoption** | 38 stars; crates.io about 1.41M downloads (about 1.03M recent) |
| **Last commit** | 2026-08-02 |
| **Links** | [repository](https://github.com/IanManske/quantette) · [benchmark](https://github.com/IanManske/quantette) |

## Verdict

Author's harness (examples/cli.rs, 30 runs averaged, quantize+remap timed, rustc -C target-feature=+avx2, CPU and rustc version unstated), 256 colours, 4 threads for quantette and imagequant 4.4.1 at defaults. Without dithering, k-means took 53-97 ms vs 253-1044 ms on eleven 17-30 MP photos (3.3-14.1x) and 28-32 vs 93-266 ms at 1920 px wide (2.9-8.6x) with DSSIM close to imagequant's (worse on some 1920 px images, e.g. Futuristic 0.000846 vs 0.000545); with dithering 1.13-5.1x and 3.3-8.4x, with lower DSSIM than imagequant in 21 of 22 rows (derived from page data). imazen/zenquant's approximate, competitor-run table puts quantette at about 1.2x imagequant speed 4.

## Use it when

- Rust services or tools making PNG8/GIF palettes from large opaque photos: no-dither k-means took 53-97 ms against imagequant's 253-1044 ms on 17-30 MP photos (4 threads) at similar DSSIM.
- Palette extraction only (output_srgb8_palette), e.g. theme or LUT generation and terminal image display; crates.io reverse dependencies include okolors, lutgen-cli, icy_sixel and yazi-adapter.
- Projects that cannot take libimagequant's GPL-3.0-or-later or commercial terms: quantette is MIT OR Apache-2.0.
- no_std (alloc) or wasm32 builds: with the threads and image features off the crate is no_std, and CI runs clippy for wasm32-unknown-unknown.
- Quick previews where palette quality matters less: Wu in sRGB took 21-34 ms on the large photos, but its DSSIM was 1.6-3.1x imagequant's (derived from page data).

## Skip it when

- Images with transparency: there is no alpha support (README benchmark doc; issue #28, opened 2025-12-18, still open without a reply).
- C or C++ codebases without Rust in the build: there is no C API or header, so you would write your own FFI shim; libimagequant ships a C API.
- Dithered output on images where imagequant is already quick: with dithering, auto-dedup is off and the gap falls to 1.13x on Futuristic (318 vs 360 ms).
- When you need dithered output that is identical across machines: parallel Floyd-Steinberg splits the image into min(rayon threads, ceil(height/256)) bands, so results depend on thread count.
- When perceived quality or file size matters more than DSSIM: zenquant's README finds quantette best on DSSIM and SSIMULACRA2 but says imagequant 'consistently looks best to the human eye', and its own PNG/GIF outputs are smaller.

## How it is fast

Pixels are converted to Oklab with wide-crate f32x8 SIMD. Wu's greedy orthogonal bipartitioning builds the palette, optionally refined by k-means: online (MacQueen) k-means when serial and mini-batch k-means (batch 4096) on rayon when parallel, sampling at most 262,144 pixels by default, so k-means cost is nearly flat in image size. For images of 2048x2048 pixels or more with dithering off, the pipeline automatically radix-deduplicates pixels into an indexed image with counts, so colour conversion, Wu and nearest-palette mapping run on unique colours only. That explains why the gap to imagequant is largest on the 17-30 MP photos and smallest with dithering.

## Compared with alternatives

Against pngquant/libimagequant, the only quantizer among the siblings: pick quantette for opaque RGB images in Rust when you want MIT/Apache licensing instead of GPL-3.0-or-later/commercial and k-means quality in a fraction of imagequant's default-speed time on large photos. Keep libimagequant for alpha, a C API or its speed and quality knobs. The other siblings (fast_image_resize, libvips, moxcms, libyuv) are resizers and colour converters, not quantizers.

## Integration

| | |
|---|---|
| **Form** | crate (quantette on crates.io, v0.6.0) |
| **Dependencies** | palette, wide, bytemuck, bitvec, num-traits, libm, ordered-float, ref-cast; optional (all on by default) rayon for threads, image 0.25 for image integration, rand + rand_xoshiro for kmeans |
| **Minimum toolchain** | Rust 1.90 (rust-version), edition 2024 |
| **Platforms** | any Rust target; no_std with alloc when threads and image are disabled; SIMD through the wide crate, with AVX2 used only when enabled at compile time |
| **Thread safety** | Safe Rust API (unsafe confined to the dedup module); parallel paths run on the current rayon pool, so install a ThreadPool to bound threads; k-means RNG is seeded (default seed 0) |
| **Drop-in for the baseline** | no |

## Gotchas

- The published times used rustc -C target-feature=+avx2. The code relies on wide's f32x8 and has cfg(target_feature = "avx2") branches (for example the dedup threshold for custom palettes), so a default x86-64 build without AVX2 is a different, unbenchmarked configuration.
- Pipeline::new() defaults to Wu (not k-means), Floyd-Steinberg dithering on (7/8 error diffusion) and parallel off. To get the benchmarked k-means no-dither numbers you must set quantize_method(QuantizeMethod::kmeans()), ditherer(None) and parallel(true) yourself.
- The speedups depend on two size-dependent shortcuts: auto-dedup only at 2048x2048 pixels or more and only without dithering, and k-means sampling capped at 262,144 pixels (max_samples). Smaller images, dithered runs or dedup(false) lose part of the advantage.
- The benchmark doc was last edited 2025-12-23, before v0.6.0 (2026-05-15). The harness times one quantize+remap per process with Instant::elapsed().as_millis(), which truncates to whole milliseconds, so the 3 ms Wu figures at 1920 px are coarse. Its imagequant runs use only the library defaults (speed 4, quality target 100) because the harness has no speed option.

## Known shortcomings

- Doc numbers match examples/cli.rs (+avx2, no CPU or rustc): k-means is 3.3-14.1x faster than imagequant without dither and 1.13-5.1x with dither on large photos, but the Wu sRGB ratio is quality-mismatched (DSSIM 0.0072 against 0.0044) and imagequant runs on RGBA while quantette runs RGB; the zenquant competitor run (about 1.2-2.1x) marks its own timings approximate, so it does not lift the tier.
- Enricher (e108, 2026-10-05): no bug behind the numbers. The large-photo gap comes from automatic radix deduplication (only at 2048x2048 pixels and above, dither off) plus the k-means sample cap of 262,144; the pipeline defaults (Wu, dither on, serial) differ from the benchmarked configuration; AVX2 is compile-time only (wide crate with cfg(target_feature)); the timer's as_millis truncates; the harness lacks imagequant's speed option. Parallel dither bands depend on thread count; no alpha support (#28 unanswered); no C API; the benchmark document predates v0.6.0. Tier C holds.

## Caveats and trade-offs

Numbers are in quantette/docs/Benchmarks and Accuracy.md (file last edited 2025-12-23, so they predate quantette 0.6.0); CPU model and rustc version are not stated. Harness quantette/examples/cli.rs times one quantize+remap per process (30 runs averaged) with --verbose; image decode and imagequant's new_image setup are outside the timed region. Workloads differ: imagequant quantizes RGBA with alpha handling while quantette only supports RGB; imagequant ran at its library defaults (speed 4, quality target 100, dither level 0.0 in the no-dither runs); quantette k-means uses default KmeansOptions (sampled mini-batch k-means, iteration count not stated in the doc). The headline single-image ratio (about 10.8x on Akihabara) is near the top of a 3.3x to 14.1x range, and the gap shrinks to 1.13x on Futuristic with dithering. In imazen/zenquant's comparison (a competitor's harness, quantette 0.5, default dithering) the gap is only about 1.2x to 2.1x, and that doc marks its \~ms column as approximate (multi-threaded across images) and not for timing claims. The author notes each library has options that change results.

Rust crate (no C API verified); no alpha channel support while imagequant has it; Wu sRGB mode is the fastest but has visibly worse DSSIM (for example 0.007178 versus imagequant 0.004436 on Akihabara full size); k-means mode in Oklab matches imagequant DSSIM on most images. Category fit is colour quantization and palette generation rather than resampling.

## Maintenance

Active single-maintainer crate (v0.6.0 on 2026-05-15; since then dependency and lint maintenance, last commit 2026-08-02), MIT OR Apache-2.0, about 1.42M crates.io downloads and 16 reverse dependencies.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party tables in quantette/docs/Benchmarks and Accuracy.md, produced by the public harness quantette/examples/cli.rs with -C target-feature=+avx2, but no CPU model or rustc version is stated, so not A. The only third-party timing (imazen/zenquant README) is a competitor's approximate multi-threaded run whose own methodology doc says its \~ms column is not for timing claims, so it does not lift the entry to B.
- **Verifier notes:** Numbers in the record match the benchmark doc and the comparison is against the named incumbent (imagequant), but the headline picked a near-best-case image and a quality-mismatched Wu ratio; claim restated as ranges with the dithering and zenquant results, tier stays C. License (MIT OR Apache-2.0), 38 stars, 1.41M crates.io downloads and last commit 2026-08-02 confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** first-party harness vs imagequant
- **Pages the verifier opened:**
  - <https://github.com/IanManske/quantette>
  - <https://raw.githubusercontent.com/IanManske/quantette/HEAD/README.md>
  - <https://github.com/IanManske/quantette/tree/main/quantette>
  - <https://github.com/IanManske/quantette/tree/main/quantette/examples>
  - <https://raw.githubusercontent.com/IanManske/quantette/HEAD/quantette/docs/Benchmarks%20and%20Accuracy.md>
  - <https://raw.githubusercontent.com/IanManske/quantette/HEAD/quantette/examples/cli.rs>
  - <https://raw.githubusercontent.com/IanManske/quantette/HEAD/quantette/Cargo.toml>
  - <https://raw.githubusercontent.com/IanManske/quantette/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/IanManske/quantette/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/IanManske/quantette/HEAD/justfile>
  - <https://github.com/IanManske/quantette/commits/main>
  - <https://github.com/IanManske/quantette/commits/main/quantette/docs/Benchmarks%20and%20Accuracy.md>
  - <https://crates.io/api/v1/crates/quantette>
  - <https://raw.githubusercontent.com/imazen/zenquant/HEAD/README.md>
  - <https://raw.githubusercontent.com/imazen/zenquant/HEAD/benchmarks/README.md>
- **Sources the enricher read:**
  - <https://github.com/IanManske/quantette>
  - <https://raw.githubusercontent.com/IanManske/quantette/HEAD/README.md>
  - <https://raw.githubusercontent.com/IanManske/quantette/HEAD/quantette/docs/Benchmarks%20and%20Accuracy.md>
  - <https://raw.githubusercontent.com/IanManske/quantette/HEAD/quantette/examples/cli.rs>
  - <https://raw.githubusercontent.com/IanManske/quantette/HEAD/quantette/Cargo.toml>
  - <https://raw.githubusercontent.com/IanManske/quantette/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/IanManske/quantette/HEAD/justfile>
  - <https://github.com/IanManske/quantette/tree/main/quantette/src>
  - <https://github.com/IanManske/quantette/tree/main/quantette/src/quantize>
  - <https://github.com/IanManske/quantette/tree/main/quantette/src/api>
  - <https://raw.githubusercontent.com/IanManske/quantette/HEAD/quantette/src/lib.rs>
  - <https://raw.githubusercontent.com/IanManske/quantette/HEAD/quantette/src/dither.rs>
  - <https://raw.githubusercontent.com/IanManske/quantette/HEAD/quantette/src/color_space.rs>
  - <https://raw.githubusercontent.com/IanManske/quantette/HEAD/quantette/src/deps.rs>
  - <https://raw.githubusercontent.com/IanManske/quantette/HEAD/quantette/src/quantize/kmeans.rs>
  - <https://raw.githubusercontent.com/IanManske/quantette/HEAD/quantette/src/quantize/dedup.rs>
  - <https://raw.githubusercontent.com/IanManske/quantette/HEAD/quantette/src/quantize/mod.rs>
  - <https://raw.githubusercontent.com/IanManske/quantette/HEAD/quantette/src/api/pipeline.rs>
  - <https://raw.githubusercontent.com/IanManske/quantette/HEAD/quantette/src/api/quantize_method.rs>
  - <https://github.com/IanManske/quantette/commits/main>
  - <https://github.com/IanManske/quantette/issues?q=is%3Aissue>
  - <https://github.com/IanManske/quantette/issues/28>
  - <https://crates.io/api/v1/crates/quantette>
  - <https://crates.io/api/v1/crates/quantette/reverse_dependencies?per_page=20>
  - <https://raw.githubusercontent.com/imazen/zenquant/HEAD/README.md>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/ianmanske/quantette`) · [data/wave10/enrich/raw/github_com_ianmanske_quantette.json](../../../data/wave10/enrich/raw/github_com_ianmanske_quantette.json) (enrichment confidence 0.75)

</details>
