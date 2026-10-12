# mozjpeg-rs

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `BSD-3-Clause` · 🟢 active

> Safe-Rust port of the mozjpeg JPEG encoder; its trellis mode timed 6% faster than C mozjpeg on one synthetic image.

| | |
|---|---|
| **Beats** | mozjpeg (C encoder, libjpeg-turbo fork with trellis quantization) |
| **Claimed result** | README table at 2048x2048: Trellis (AC + DC) 197 ms vs C mozjpeg 210 ms ('6% faster'), but the Rust side runs TrellisMode::Optimized with adaptive candidate limiting against the C full trellis search, so it does less work rather than the same algorithm faster, and output sizes for the timed image are unchecked; Baseline (Huffman opt) 42 ms vs 9 ms for C mozjpeg ('4.6x slower'). README also claims 0.05-0.80% smaller files in trellis modes. |
| **Workload** | One synthetic 2048x2048 RGB image (gradient plus periodic noise, generated in tests/bench_2k.rs), quality 85, 4:2:0, sequential (non-progressive) JPEG, single-threaded, 3 warmups then 30 timed iterations per side; Rust vs C mozjpeg built from the vendored source in the mozjpeg-sys 2.2.3 crate. Two configs: no optimizations (TestEncoderConfig::baseline(), Huffman optimization off) and Huffman optimization + AC and DC trellis with deringing off on both sides. |
| **Metric** | throughput |
| **Compiler and flags** | cargo test --release --test bench_2k -- --nocapture; README says 'release mode with AVX2/NEON'; rustc version and RUSTFLAGS for the README numbers are not stated (crate MSRV 1.89; the separate Criterion Docker harness benchmark/Dockerfile.perf pins rust:1.92-bookworm and installs nasm for mozjpeg-sys). C mozjpeg is the vendored source compiled by mozjpeg-sys. |
| **Adoption** | 3 stars |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/imazen/mozjpeg-rs) · [benchmark](https://raw.githubusercontent.com/imazen/mozjpeg-rs/HEAD/README.md) |

## Verdict

tests/bench_2k.rs encodes one synthetic 2048x2048 gradient-plus-periodic-noise RGB image at Q85 4:2:0, sequential and single-threaded, 3 warmups then 30 timed runs per side, in the same process as C mozjpeg built by mozjpeg-sys 2.2.3 (default features include nasm_simd). The README reports 197 vs 210 ms with Huffman optimization plus AC/DC trellis and no deringing, and 42 vs 9 ms with no optimizations; CPU, rustc and RUSTFLAGS are not stated, and output sizes for the timed image are discarded. The trellis comparison sets the same encoder parameters on both sides but pits Rust's reduced trellis search (standard-table rates, adaptive lookback and candidate caps added in 0.6.0, when the changelog first claimed 7% faster) against C's full search with gather and requantize passes, so the gain is less work, not a faster implementation of the same search.

## Use it when

- Rust services that want mozjpeg-style trellis-quantized JPEGs without a C toolchain, cmake or nasm, and with forbid(unsafe_code) across the whole encoder
- Encoding untrusted images on a server: Limits rejects oversized dimensions, allocations and metadata before any pixel work, and \*_with_stop variants accept a cancellation or deadline token
- Replacing the C mozjpeg crate while keeping output bytes for non-trellis baseline and progressive configs (byte-exact parity on CID22 at Q75-95)
- Photo encoding at roughly Q75-95 with trellis on, where its measured speed is on par with or slightly ahead of C mozjpeg
- aarch64 or wasm32 targets: CI covers 15 platform configurations, including NEON and wasm32-wasip1 with SIMD128

## Skip it when

- Fast encoding without trellis: the no-optimization config timed 42 ms against 9 ms for C mozjpeg at 2048x2048 (4.6x slower), so for speed-first baseline JPEG use libjpeg-turbo or C mozjpeg
- You need decoding: it is encoder-only. The author recommends zenjpeg (encode and decode) for new projects
- Grayscale progressive output: open issue #9 (2026-08-29) reports an index-out-of-bounds panic in the SOS writer for Subsampling::Gray with ProgressiveBalanced or ProgressiveSmallest
- You need byte-identical trellis output to stock C mozjpeg: the default Optimized trellis gives different (usually slightly smaller) files, and TrellisMode::MozjpegExact is slower and is validated against imazen's patched mozjpeg fork
- Arithmetic coding, multipass trellis, a C ABI, or code that has had a human audit: the README says much of the code is AI-generated and not fully human-reviewed

## How it is fast

The trellis-mode win comes mainly from doing less trellis work than C mozjpeg. The default TrellisMode::Optimized runs trellis inline in the single forward-DCT pass and estimates rates from the standard Huffman tables. C mozjpeg instead gathers statistics, builds optimal tables and then runs extra trellis and Huffman passes per component. TrellisSpeedMode::Adaptive also caps the O(n^2) predecessor search at lookback 8 with 3 candidates for blocks with more than 55 nonzero AC coefficients, and at 16 with 4 above 48; upstream quantize_trellis in jcdctmgr.c searches every predecessor. DCT and colour conversion use safe SIMD (archmage, runtime AVX2/NEON dispatch, autovectorised fallback), but the non-trellis entropy coder is much slower than C's hand-tuned SIMD path.

## Compared with alternatives

Pick it over zenjpeg (same author, encoder and decoder, beats libjpeg-turbo) only when you need mozjpeg-compatible settings and output bytes rather than the best size/quality. Pick it over libjpeg-turbo or jpeg-rusturbo when smaller trellis-quantized files from memory-safe Rust matter more than raw baseline encode speed.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | archmage, safe_unaligned_simd, wide, bytemuck, enough; default features add zenyuv (fast-yuv), imgref and rgb; optional png, zencodec/zenpixels/garb, and mozjpeg-sys + libc (mozjpeg-sys-config, which lifts forbid(unsafe_code) and builds C) |
| **Minimum toolchain** | Rust 1.89 (edition 2024) |
| **Platforms** | x86-64 (AVX2 dispatched at runtime), aarch64 (NEON), wasm32 (SIMD128); other targets use an autovectorised fallback. CI also covers armv7 and i686 under QEMU |
| **Thread safety** | Each encode is single-threaded (no threading dependency); Send/Sync guarantees for Encoder are not documented; the almost-enough Stopper token is Send + Sync |
| **Drop-in for the baseline** | partial — a different Rust builder API with no libjpeg-compatible C interface; output matches C mozjpeg byte for byte only for non-trellis baseline/progressive with default colour conversion, and the mozjpeg-sys-config feature can configure a C encoder from the same settings |

## Gotchas

- Encoder::default() is Preset::ProgressiveBalanced (progressive, trellis, deringing), not a baseline JPEG; use Encoder::baseline_optimized() or Preset::BaselineBalanced for sequential output
- The README speed table does not use the shipped defaults: the 6% trellis row has deringing off and runs Adaptive search limiting, and the row labelled 'Baseline (huffman opt)' actually times TestEncoderConfig::baseline() with Huffman optimization off
- Hand-written SIMD intrinsics sit behind the non-default simd-intrinsics feature; default builds use autovectorised DCT/colour code, which Cargo.toml puts at about 87% of the intrinsics speed
- fast_color(true) (zenyuv) is about 40% faster at RGB to YCbCr but changes output bytes by ±1 rounding, so it breaks C parity

## Known shortcomings

- Single synthetic 2048x2048 image at Q85 4:2:0 (tests/bench_2k.rs), AC and DC trellis on, deringing off on both sides: trellis 197 ms versus mozjpeg 210 ms. The Rust side uses TrellisMode::Optimized, so output is not byte-identical and the bench reports no sizes; the README labels the 4.6x-slower row 'huffman opt' but the code runs it with Huffman optimisation off; no CPU or rustc version. The older Kodak CSV shows about 36% less time but files 0.9-3.9% larger.
- The '6% faster' trellis claim is not like-for-like (retier-28): Rust times TrellisMode::Optimized with the Adaptive limiter (lookback 8/16, 3/4 candidates, blocks over 48/55 non-zero coefficients) against the C full quantize_trellis search with no speed limiter, so it does less work, and the timed image's sizes were never checked; the adaptive limiting landed in 0.6.0, the same release that first claimed 7% faster. Open issue #9 (greyscale plus progressive preset panics); Encoder::default() is progressive; simd-intrinsics is off by default; crates.io latest 0.9.2 (0.10.0 unreleased).

## Caveats and trade-offs

Pure-Rust reimplementation (port) of the mozjpeg encoder with #![forbid(unsafe_code)], not a binding: C mozjpeg is used only as a dev-dependency for parity tests and benchmarks and as an optional config feature. The speed win exists only with trellis quantization (197 ms vs 210 ms, 6%) on one synthetic image; without trellis it is 4.6x slower (42 ms vs 9 ms). The README labels that row 'Baseline (huffman opt)', but the current tests/bench_2k.rs times TestEncoderConfig::baseline(), which has Huffman optimization off. The Rust trellis is TrellisMode::Optimized by default (adaptive search limiting, standard-table rate estimation), a different search from C mozjpeg's trellis, so outputs are not byte-identical; bench_2k discards the outputs and reports no file sizes, and the 0.05-0.80% smaller-file claim comes from a separate CID22 run (examples/cid22_bench). The bit-exact TrellisMode::MozjpegExact is described as slower and is not what was timed. No CPU model, rustc version or flags for the README table. An older checked-in benchmark/benchmark_results.csv (Kodak, 24 images x 21 qualities, progressive + trellis + deringing, from examples/pareto_benchmark built by a rust:1.83 Dockerfile from the project's earlier 'mozjpeg-oxide' name) sums to 6,850 ms Rust vs 10,658 ms C (about 36% less time, derived from page data) but with Rust files 0.9-3.9% larger at Q75-95, so it predates the current parity claims and states no CPU. README says much of the code is AI-generated and not fully human-reviewed; a 2026-07-28 note documents a NEON DCT bug that inverted blocks on aarch64 (fixed). The author recommends the sibling crate zenjpeg (already listed) for new projects. Baseline is C mozjpeg, not libjpeg-turbo or libpng.

Safe Rust (#![forbid(unsafe_code)]) using the archmage safe-SIMD layer; encoder only. Output is byte-identical to C mozjpeg for baseline and progressive modes; trellis output differs slightly (smaller) unless TrellisMode::MozjpegExact is chosen. Optional fast_color(true) gives about 40% faster RGB to YCbCr at the cost of exact parity.

## Maintenance

Actively maintained (last commit 2026-09-29; 0.10.0 prepared but unreleased, crates.io latest 0.9.2 from 2026-04-17 with about 120k downloads), BSD-3-Clause and easy to add with cargo, but a single-maintainer project with 3 stars whose author now steers new users to zenjpeg.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party numbers from public benchmark code (tests/bench_2k.rs, which times mozjpeg-rs against C mozjpeg built by mozjpeg-sys in the same process), but the README table states no CPU model, rustc version or RUSTFLAGS ('release mode with AVX2/NEON' only), so it falls short of A.
- **Verifier notes:** Port, not a binding, so not a duplicate; C mozjpeg (mozilla/mozjpeg) itself is not listed and could be a lead as the trellis-quantization incumbent. Trellis speed comparison is like-for-like in settings (Q85, 4:2:0, AC+DC trellis, Huffman opt, no deringing on both sides) but not in algorithm or output bytes. Metadata checked: BSD-3-Clause, 3 stars, not a fork, last commit 2026-09-29.
- **Fields the verifier corrected:** `workload`, `compiler_and_flags`, `caveats`, `claimed_speedup`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/imazen/mozjpeg-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/imazen/mozjpeg-rs/HEAD/tests/bench_2k.rs>
  - <https://raw.githubusercontent.com/imazen/mozjpeg-rs/HEAD/src/test_encoder.rs>
  - <https://raw.githubusercontent.com/imazen/mozjpeg-rs/HEAD/src/types.rs>
  - <https://raw.githubusercontent.com/imazen/mozjpeg-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/imazen/mozjpeg-rs/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/imazen/mozjpeg-rs/HEAD/benchmark/README.md>
  - <https://raw.githubusercontent.com/imazen/mozjpeg-rs/HEAD/benchmark/Dockerfile>
  - <https://raw.githubusercontent.com/imazen/mozjpeg-rs/HEAD/benchmark/Dockerfile.perf>
  - <https://raw.githubusercontent.com/imazen/mozjpeg-rs/HEAD/benchmark/benchmark_results.csv>
  - <https://raw.githubusercontent.com/imazen/mozjpeg-rs/HEAD/examples/pareto_benchmark.rs>
  - <https://raw.githubusercontent.com/imazen/mozjpeg-rs/HEAD/benchmarks/neon_tiers_aarch64_2026-07-28.md>
  - <https://github.com/imazen/mozjpeg-rs>
  - <https://github.com/imazen/mozjpeg-rs/commits>
  - <https://github.com/imazen/mozjpeg-rs/tree/main/src>
  - <https://github.com/imazen/mozjpeg-rs/tree/main/benchmark>
  - <https://github.com/imazen/mozjpeg-rs/tree/main/benchmarks>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/imazen/mozjpeg-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/imazen/mozjpeg-rs/HEAD/tests/bench_2k.rs>
  - <https://raw.githubusercontent.com/imazen/mozjpeg-rs/HEAD/src/test_encoder.rs>
  - <https://raw.githubusercontent.com/imazen/mozjpeg-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/imazen/mozjpeg-rs/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/imazen/mozjpeg-rs/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/imazen/mozjpeg-rs/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/imazen/mozjpeg-rs/HEAD/src/types.rs>
  - <https://raw.githubusercontent.com/imazen/mozjpeg-rs/HEAD/src/trellis.rs>
  - <https://raw.githubusercontent.com/imazen/mozjpeg-rs/HEAD/src/encode.rs>
  - <https://raw.githubusercontent.com/mozilla/mozjpeg/master/jcdctmgr.c>
  - <https://raw.githubusercontent.com/mozilla/mozjpeg/master/jcmaster.c>
  - <https://crates.io/api/v1/crates/mozjpeg-sys/2.2.3>
  - <https://crates.io/api/v1/crates/mozjpeg-rs>
  - <https://github.com/imazen/mozjpeg-rs>
  - <https://github.com/imazen/mozjpeg-rs/issues?q=is%3Aissue>
  - <https://github.com/imazen/mozjpeg-rs/issues/9>
  - <https://github.com/imazen/mozjpeg-rs/pulls?q=is%3Apr>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/imazen/mozjpeg-rs`) · [data/wave10/enrich/raw/github_com_imazen_mozjpeg_rs.json](../../../data/wave10/enrich/raw/github_com_imazen_mozjpeg_rs.json) (enrichment confidence 0.75)

</details>
