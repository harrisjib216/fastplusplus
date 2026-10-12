# zenquant (imazen)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `AGPL-3.0-only OR LicenseRef-Imazen-Commercial` · 🟢 active

> Pure-Rust 256-colour palette quantizer in OKLab with perceptual masking; smaller PNG/GIF than libimagequant, not faster.

| | |
|---|---|
| **Beats** | libimagequant (imagequant crate 4, presets s1 d50, s1 d100, s4 d100); also quantette 0.5 k-means, quantizr, color_quant |
| **Claimed result** | Not a speed claim; zenquant's pitch is smaller files and better butteraugli at similar time. README table: zenquant Best butteraugli 3.17, SSIMULACRA2 82.9, DSSIM 0.00058, PNG 586 KB, GIF 764 KB, \~542 ms; imagequant s1 d100 4.10, 82.2, 0.00056, 637 KB, 848 KB, \~546 ms; imagequant s4 d100 4.39, 81.9, 0.00057, 640 KB, 854 KB, \~315 ms; quantette k-means 3.86, 83.9, 0.00050, 616 KB, 799 KB, \~265 ms; zenquant Fast 3.29, 82.6, 0.00069, 582 KB, 749 KB, \~321 ms. Derived from page data: Best PNG is 8% smaller than imagequant s1 d100 at the same \~ms; Fast is 1.7x faster than imagequant s1 d100 (321 vs 546) but no faster than imagequant s4 (315) or quantette (265). |
| **Workload** | 256-colour quantization of 50 images from three corpora (CID22, CLIC 2025, screenshots) with default dithering; scored by butteraugli, SSIMULACRA2, DSSIM, PNG size (zenpng aggressive deflate), GIF size and approximate per-image milliseconds from the multi-threaded default run. |
| **Metric** | other |
| **Compiler and flags** | cargo run --example quantizer_comparison --release; runtime SIMD dispatch (AVX2+FMA, NEON, WASM128), no -C target-cpu=native; rustc version not stated |
| **Adoption** | 2 GitHub stars; crates.io zenquant 0.1.3 (8,680 downloads, 4,077 recent); default quantizer in zenpng, zengif, zenwebp (all imazen's own crates) |
| **Last commit** | 2026-09-27 |
| **Links** | [repository](https://github.com/imazen/zenquant) · [benchmark](https://github.com/imazen/zenquant) |

## Verdict

First-party README table (2026-03-04 run of examples/quantizer_comparison.rs, 50 images from CID22, CLIC 2025 and screenshots, 256 colours, rustc, CPU and OS unrecorded): zenquant Best has butteraugli 3.17 vs 4.10 and a PNG of 586 KB vs 637 KB (about 8% smaller, derived from page data) against imagequant 4 at speed 1 with full dithering, at \~542 vs \~546 ms. Those times come from the approximate multi-threaded, cached mode, so the record supports a size and butteraugli advantage, not a speed one.

## Use it when

- Producing palette PNG, APNG or GIF where file size at a given butteraugli score matters more than encode time (README: Best 586 KB PNG vs imagequant s1 d100 637 KB at about the same \~542 vs \~546 ms).
- Pure-Rust, no_std + alloc or WASM builds that require #![forbid(unsafe_code)] and no C dependency.
- Animation encoders that need one shared palette across frames and a per-frame quality floor (with_min_ssim2 returns QualityNotMet so the encoder can fall back to truecolor).
- Server pipelines that need cooperative cancellation of slow Best-preset runs (quantize_with_stop) and a pixel-count cap (default 120 MP).
- Projects already on imazen's zenpng, zengif or zenwebp, where zenquant is the default quantizer.

## Skip it when

- When speed is the goal: in the README table zenquant Fast (\~321 ms) only ties imagequant s4 (\~315 ms) and loses to quantette k-means (\~265 ms), and Best costs the same as imagequant s1 d100.
- When per-pixel fidelity or looks matter most: the README itself says quantette k-means leads SSIMULACRA2 (83.9 vs 82.9) and DSSIM (0.00050 vs 0.00058) and that imagequant looks best to the eye.
- Closed-source network services without a licence purchase: AGPL-3.0-only network copyleft unless you buy the commercial licence (\$1 startup tier for under \$1M revenue and fewer than 5 employees).
- Untrusted input on the released crate: 0.1.3 caps pixel count only in quantize/quantize_rgba; extending the cap to remap/build_palette is still in the unreleased 0.1.4 changelog and issue #4 ('Server hardening') was open in June 2026.
- Risk-averse production use: 2 stars, two dependents (zenpng, zengif, both imazen's), first release 2026-03-05, and a README notice that the code was developed with Claude and 'Not all code manually reviewed'.

## How it is fast

It is tuned for size and perceptual quality rather than speed: an OKLab histogram is split by median cut, then refined by k-means weighted with butteraugli-inspired adaptive-quantization masks so palette entries go to smooth gradients and skin tones instead of noisy texture. A format-aware palette sort, adaptive Floyd-Steinberg dithering and an optional Viterbi dynamic program that lengthens index runs help deflate and LZW compress the output. Hot loops (sRGB to OKLab, nearest-palette search, k-means) use archmage runtime SIMD dispatch (AVX2+FMA, NEON, WASM SIMD128) with a scalar fallback.

## Compared with alternatives

Pick zenquant over pngquant/libimagequant or quantette when the smallest palette PNG or GIF at a good butteraugli score, a pure-Rust forbid(unsafe) no_std build, shared animation palettes or a quality floor matter more than speed; pick quantette for the fastest run and best per-pixel metrics, and libimagequant for the best-looking output and the longest track record.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | rgb, imgref, num-traits (libm), thiserror, linear-srgb, archmage, magetypes, enough |
| **Minimum toolchain** | Rust 1.92 (edition 2024) |
| **Platforms** | any Rust target; SIMD paths for x86-64 AVX2+FMA, aarch64 NEON and wasm32 SIMD128 with scalar fallback |
| **Thread safety** | not documented; each call is single-threaded with no thread-pool dependency, so parallelize across images in the caller |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: the README's \~ms column comes from the default mode, which quantizes 8 images at once in scoped threads, times a single unwarmed run per quantizer per image, lets imagequant 4 (default features, rayon threads) spawn its own pool on top, and reuses cached per-image results and their old timings from cache.json unless --recalc is passed; benchmarks/README.md calls these numbers 'fine for the quality columns, not for timing claims', and no --benchmark (single-thread, min-of-4-after-warm-up) result or CPU/rustc record is committed.
- Harness flaw: every zenquant row runs in OutputFormat::Png mode, so the GIF column never exercises its GIF tuning, and the PNG column re-encodes the reconstructed RGB pixels through zenpng's auto-indexing, so each quantizer's own palette order (zenquant's luminance sort) does not reach the measured PNG size. benchmarks/README.md says all contenders use 'same default dithering', but the code gives color_quant no dithering, quantizr 0.5, imagequant 0.5 or 1.0, quantette Floyd-Steinberg and zenquant its adaptive dither.
- with_target_ssim2, with_min_ssim2, ssimulacra2_estimate() and butteraugli_estimate() use an internal MPE estimator, not real SSIMULACRA2 or butteraugli, so the quality floor is approximate.
- Version and licence drift: crates.io serves 0.1.3 (2026-04-10) while main is 0.1.4 (the manifest had regressed to 0.1.2 after the 0.1.3 release, per CHANGELOG), the build_palette/remap \*_with_stop APIs are unreleased, and the licence changed from AGPL-3.0-or-later (0.1.0, 0.1.1) to AGPL-3.0-only OR LicenseRef-Imazen-Commercial from 0.1.2.

## Known shortcomings

- Not faster: best about 542 ms, the same as imagequant s1 d100 (546 ms); the fast 321 ms mode only ties imagequant s4 (315 ms) and loses to quantette (265 ms); the win is file size and butteraugli score. The ms column comes from an approximate 8-thread run with cached timings, imagequant kept its default rayon threads while zenquant ran single-threaded, no CPU or rustc recorded; 2 stars, AI-generated-code notice.
- Enricher: the README ms column comes from an 8-thread default run with one unwarmed run per image, imagequant's rayon pool on top, and cache.json reusing old timings unless --recalc; no --benchmark result, CPU or rustc recorded. Every zenquant row runs OutputFormat::Png, so its GIF mode is never measured, and the PNG column re-encodes RGB through zenpng auto-indexing so its own palette sort is never measured; dithering is not equal (color_quant none, quantizr 0.5); the 'SSIM2 target/floor' uses an internal MPE estimate. crates.io 0.1.3 vs main 0.1.4, pixel cap on remap/build_palette unreleased, issue #4 open.

## Caveats and trade-offs

Not faster than the incumbents in the README table: zenquant Best takes the same \~542 ms as imagequant s1 d100 and the Fast preset (321 ms) only ties imagequant s4 (315 ms) and loses to quantette k-means (265 ms); the win is file size and butteraugli, while quantette leads SSIMULACRA2/DSSIM. The \~ms column comes from the default run, which times a single run per image while 8 images are quantized in parallel threads, reuses cached per-image results (and their timings) unless --recalc is passed, and is described by the repo's own benchmarks/README.md as 'fine for the quality columns, not for timing claims'; the single-thread --benchmark mode has no committed result. Even in --benchmark mode the comparison is not single-core for every contender: imagequant 4 is a dev-dependency with default features, which enable its rayon 'threads' feature, while zenquant is no_std and single-threaded; imagequant's timed closure also includes an RGB-to-RGBA copy. No CPU, RAM, OS or rustc version is recorded for the 2026-03-04 run. Evidence is first-party, the README notes AI-generated code ('Not all code manually reviewed'), and the repo manifest is at 0.1.4 while crates.io still serves 0.1.3. Licence is dual (AGPL-3.0-only OR commercial; 0.1.0 and 0.1.1 were AGPL-3.0-or-later), so the AGPL branch is copyable but with network copyleft.

OKLab pipeline with butteraugli-inspired adaptive-quantization masking, median cut, k-means, format-aware palette sort, Floyd-Steinberg and optional Viterbi run optimization; no_std plus alloc, forbid(unsafe_code), SIMD dispatch. AGPL-3.0 network copyleft unless a commercial licence is bought (\$1 startup tier); the README says quantette leads on per-pixel metrics and imagequant looks best to the eye.

## Maintenance

Actively developed by Imazen (250 commits, last on 2026-09-27; 0.1.3 on crates.io with 8,680 downloads) and copyable under AGPL-3.0-only or a paid commercial licence, but it is six months old, has 2 stars, and is AI-assisted code that the README says is not fully reviewed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README table (2026-03-04 run of examples/quantizer_comparison.rs) compares zenquant with imagequant 4, quantette 0.5, quantizr and color_quant, and every number in claimed_speedup matches it; the harness code and competitor versions are public, but no CPU model, OS or rustc version is recorded for the run (benchmarks/README.md only asks future runs to record them), and the \~ms column comes from the approximate multi-threaded mode, so first-party tier C.
- **Verifier notes:** Record is accurate; this is a quality/size entry, not a speed win, so the orchestrator should file the not-faster shortcoming. Harness flaws to record: approximate multi-threaded timing with cached results, imagequant allowed its internal rayon threads, no hardware or rustc recorded, 2 stars.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** same-thread-count timing on stated hardware; warmed, single-threaded timing with equal dithering
- **Pages the verifier opened:**
  - <https://github.com/imazen/zenquant>
  - <https://github.com/imazen/zenquant/commits>
  - <https://raw.githubusercontent.com/imazen/zenquant/HEAD/README.md>
  - <https://raw.githubusercontent.com/imazen/zenquant/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/imazen/zenquant/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/imazen/zenquant/HEAD/examples/quantizer_comparison.rs>
  - <https://crates.io/api/v1/crates/zenquant>
  - <https://crates.io/api/v1/crates/imagequant>
- **Sources the enricher read:**
  - <https://github.com/imazen/zenquant>
  - <https://github.com/imazen/zenquant/commits>
  - <https://github.com/imazen/zenquant/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/imazen/zenquant/HEAD/README.md>
  - <https://raw.githubusercontent.com/imazen/zenquant/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/imazen/zenquant/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/imazen/zenquant/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/imazen/zenquant/HEAD/examples/quantizer_comparison.rs>
  - <https://raw.githubusercontent.com/imazen/zenquant/HEAD/src/lib.rs>
  - <https://crates.io/api/v1/crates/zenquant>
  - <https://crates.io/api/v1/crates/zenquant/reverse_dependencies?per_page=20>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/imazen/zenquant`) · [data/wave10/enrich/raw/github_com_imazen_zenquant.json](../../../data/wave10/enrich/raw/github_com_imazen_zenquant.json) (enrichment confidence 0.7)

</details>
