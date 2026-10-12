# upack (μpack)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Integer compression and bit-packing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Rust SIMD bitpacking of 128-integer u32/u16 blocks; beats the bitpacking crate's BitPacker4x on x86, loses on ARM.

| | |
|---|---|
| **Beats** | Rust bitpacking crate (port of simdcomp); also compared in README prose to StreamVByte |
| **Claimed result** | BENCHMARKS.md AVX512 Zen5 (AMD 9950x), x128 decompress: upack-base 10.07B int/s vs bitpacking-base 8.85B (1.14x, derived from page data); delta 8.81B vs 3.82B (2.3x, derived). AVX2 Zen3 (5900HX): 6.13B vs 5.88B base, 3.58B vs 3.26B delta. Hetzner CCX13 AVX2: 6.20B vs 5.87B base, 3.72B vs 2.85B delta. |
| **Workload** | Decompress/compress 128-integer blocks of u32 with AVX512/AVX2/NEON, plain, delta and delta-1 variants, in billions of ints per second. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 9950X (Zen5, AVX512); AMD Ryzen 9 5900HX laptop (Zen3, AVX2); Apple M4 (NEON); Hetzner CCX13 (AVX2); Hetzner CAX11 (NEON) |
| **Compiler and flags** | Rust (version not stated; crate rust-version 1.90.0, edition 2024); benchmark run via Justfile `bench` recipe: cargo run -p benchmark --release with features avx512,avx2,neon, no RUSTFLAGS/target-cpu set for the bench; profile.release has debug = true |
| **Adoption** | 11 stars |
| **Last commit** | 2026-06-23 |
| **Links** | [repository](https://github.com/lnx-search/upack) · [benchmark](https://raw.githubusercontent.com/lnx-search/upack/HEAD/BENCHMARKS.md) |

## Verdict

The author's benchmark crate (synthetic sorted blocks with random gap bit widths up to 26, 1 M samples, 15 s per routine) compares against the bitpacking 0.9 crate's BitPacker4x, which is its SSE3 128-bit format, not the AVX2 BitPacker8x. On Zen5 (Ryzen 9 9950X, AVX-512), x128 decompress was 10.07 vs 8.85 B int/s plain and 8.81 vs 3.82 delta; on AVX2 Zen3 and Hetzner CCX13 the plain gain was about 4-6%; on NEON (M4, CAX11) upack was slower. Rust compiler version is not stated and builds used plain cargo --release with no target-cpu flag.

## Use it when

- Rust search engines or columnar stores packing sorted docID or offset blocks of 128 u32 values on x86-64 with AVX2 or AVX-512.
- Workloads with many short lists or tail blocks under 128 values, where fixed-size SIMD bitpacking would pad or need a separate VByte fallback.
- Delta-coded decode-heavy paths on Zen5-class AVX-512 CPUs, where its delta decode measured 2.3x the bitpacking crate's BitPacker4x.
- Projects that want zero dependencies and no allocation in the codec.

## Skip it when

- ARM/NEON targets: on Apple M4 and Hetzner CAX11 it is slower than the bitpacking crate for both compress and decompress (M4 decompress 6.45 vs 7.01 B int/s, compress 4.12 vs 6.53).
- u64 values or blocks larger than 128 integers (not supported).
- Big-endian machines (compile_error in uint32/mod.rs).
- C or C++ codebases: Rust-only crate with no C API; simdcomp or FastPFor give the same technique natively.
- When you need a mature, widely deployed codec: 11 stars, about 95 total crates.io downloads, first release 2026-02-27.

## How it is fast

Hand-written AVX-512, AVX2 and NEON kernels (plus a scalar fallback) chosen at run time with is_x86_feature_detected or the aarch64 equivalent, and specialised per bit width. Each 128-value block is processed as two 64-value halves with separate full and partial pack/unpack kernels, so a short block costs only the bytes and work for its n values. Delta decoding is fused into the unpack kernels, which is where the largest gain over the baseline shows (8.81 vs 3.82 B int/s on Zen5).

## Compared with alternatives

Pick it over simdcomp or FastPFor when you are in Rust, on x86, and have many partial blocks; on ARM, or in C/C++, use simdcomp, FastPFor or TurboPFor, and for byte-oriented variable-length codes see Stream VByte or varint-simd.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none (features avx512, avx2, neon enabled by default) |
| **Minimum toolchain** | Rust 1.90.0, edition 2024 |
| **Platforms** | x86-64 (AVX-512 or AVX2 paths, runtime detected), aarch64 (NEON), scalar fallback elsewhere; little-endian only |
| **Thread safety** | Stateless free functions over caller-owned buffers; no shared state, so safe to call from many threads (not stated explicitly in the docs) |
| **Drop-in for the baseline** | partial — same job and 128-value block as bitpacking::BitPacker4x, but a different bit layout and API, so stored data is not interchangeable |

## Gotchas

- compress_delta and compress_delta1 take the input as &mut and overwrite it with the deltas.
- decompress asserts that the input slice is at least the full-block size for that bit width, so a truncated partial block must be re-padded (zero-filled) in memory before decoding; only the stored copy can be short.
- The block has no header: the caller must persist compressed_bit_length and n alongside the bytes.
- Its format differs from simdcomp and from BitPacker4x/8x even at n = 128, so it cannot read their output.

## Known shortcomings

- Tier C: every number reproduces from BENCHMARKS.md but the rustc version is unstated and the bench is a plain cargo --release; on CAX11 the delta variant loses (1.74B vs 1.88B). Rust; loses to the bitpacking crate on NEON.
- The bench baseline is bitpacking::BitPacker4x (the SSE3 128-bit format), not the AVX2 BitPacker8x, so the AVX2/AVX-512 wins are against narrower SIMD; NEON loses on compress (M4 4.12 vs 6.53 billion ints/s); synthetic data only (random gaps, max 26 bits); compress_delta mutates its input; about 95 crates.io downloads in total.

## Caveats and trade-offs

Loses to the bitpacking baseline on NEON: Apple M4 x128 decompress base 6.45B vs 7.01B int/s and delta 5.12B vs 5.70B; Hetzner CAX11 base 2.46B vs 3.05B and delta 1.74B vs 1.88B. Rust compiler version not stated (only minimum rust-version 1.90.0); bench built with plain cargo --release. First-party benchmark (benchmark/ crate). Does not compare against FastPFor, Simple-8b or varint, so baseline is off-list. Not a C++ library (Rust); no C API checked.

Variable-size output blocks (partial blocks can be truncated) for better ratio on short lists; u32/u16 only, u64 not supported; Rust crate with zero dependencies.

## Maintenance

Actively maintained (v1.1.1 on 2026-06-23, one open NEON tuning issue) and Apache-2.0, but young and lightly used; usable as a Rust dependency, not as C++ code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** BENCHMARKS.md compares upack against the Rust bitpacking 0.9 crate (simdcomp port) on five named CPUs with public benchmark code (benchmark/ crate, run by `just bench` = cargo run -p benchmark --release), and every claimed number matches; but the rustc version used is not stated (only the crate minimum rust-version 1.90.0) and the runs are first-party, so not A.
- **Verifier notes:** All Zen5, Zen3 and CCX13 x128 decompress numbers in the claim match BENCHMARKS.md; added the CAX11 delta loss to caveats. Metadata checked: Apache-2.0, 11 stars, not archived or a fork, last commit 2026-06-23 (active).
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/lnx-search/upack/HEAD/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/lnx-search/upack/HEAD/README.md>
  - <https://raw.githubusercontent.com/lnx-search/upack/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/lnx-search/upack/HEAD/Justfile>
  - <https://raw.githubusercontent.com/lnx-search/upack/HEAD/benchmark/Cargo.toml>
  - <https://raw.githubusercontent.com/lnx-search/upack/HEAD/LICENSE>
  - <https://github.com/lnx-search/upack>
  - <https://github.com/lnx-search/upack/commits>
- **Sources the enricher read:**
  - <https://github.com/lnx-search/upack>
  - <https://github.com/lnx-search/upack/issues?q=is%3Aissue>
  - <https://github.com/lnx-search/upack/tree/main/src>
  - <https://github.com/lnx-search/upack/tree/main/src/uint32>
  - <https://github.com/lnx-search/upack/tree/main/benchmark/src>
  - <https://github.com/lnx-search/upack/tree/main/benchmark/src/uint32>
  - <https://raw.githubusercontent.com/lnx-search/upack/HEAD/README.md>
  - <https://raw.githubusercontent.com/lnx-search/upack/HEAD/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/lnx-search/upack/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/lnx-search/upack/HEAD/Justfile>
  - <https://raw.githubusercontent.com/lnx-search/upack/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/lnx-search/upack/HEAD/src/core.rs>
  - <https://raw.githubusercontent.com/lnx-search/upack/HEAD/src/util.rs>
  - <https://raw.githubusercontent.com/lnx-search/upack/HEAD/src/uint32/mod.rs>
  - <https://raw.githubusercontent.com/lnx-search/upack/HEAD/src/uint32/avx2/mod.rs>
  - <https://raw.githubusercontent.com/lnx-search/upack/HEAD/benchmark/Cargo.toml>
  - <https://raw.githubusercontent.com/lnx-search/upack/HEAD/benchmark/src/main.rs>
  - <https://raw.githubusercontent.com/lnx-search/upack/HEAD/benchmark/src/uint32/mod.rs>
  - <https://raw.githubusercontent.com/lnx-search/upack/HEAD/benchmark/src/uint32/lib_bitpacking.rs>
  - <https://raw.githubusercontent.com/lnx-search/upack/HEAD/benchmark/src/uint32/generate.rs>
  - <https://raw.githubusercontent.com/lnx-search/upack/HEAD/benchmark/src/uint32/runner.rs>
  - <https://raw.githubusercontent.com/quickwit-oss/bitpacking/HEAD/README.md>
  - <https://crates.io/api/v1/crates/upack>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/lnx-search/upack`) · [data/wave9/enrich/raw/github_com_lnx_search_upack.json](../../../data/wave9/enrich/raw/github_com_lnx_search_upack.json) (enrichment confidence 0.75)

</details>
