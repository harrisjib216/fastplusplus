# Malachite

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `LGPL-3.0-only` · 🟢 active

> Pure-Rust port of GMP/FLINT integer algorithms; beats GMP (via rug) on sub-64-bit values and string parsing, not on large operands.

| | |
|---|---|
| **Beats** | GNU GMP (mpz, via the Rust rug 1.30.0 crate) |
| **Claimed result** | Tiny operands and parsing only, on an Apple M2 Max against rug 1.30.0 (GMP). At 10 bits: ubig_add malachite 2.1 ns vs rug 17.7 ns, ubig_mul 3.0 ns vs 18.0 ns, ubig_gcd 8.5 ns vs 20.9 ns, ubig_gcd_ext 25.8 ns vs 53.7 ns, ubig_pow 5.1 ns vs 41.6 ns, ubig_to_dec 10.1 ns vs 37.5 ns. Decimal and hex parsing beat rug at every size: ubig_from_dec at 10^4 bits 8.37 us vs 11.51 us, ubig_from_hex at 10^4 bits 3.13 us vs 6.60 us; string_round_trip 1.80 ms vs 1.97 ms. From about 100 to 1000 bits up, rug wins: ubig_mul at 10^4 bits malachite 8.28 us vs rug 4.52 us, ubig_gcd_ext at 1000 bits 3.40 us vs 3.18 us, ubig_modulo_pow at 10^4 bits 250.90 ms vs 143.02 ms. |
| **Workload** | Criterion microbenchmarks of unsigned big-integer add, sub, mul, div, gcd, extended gcd and conversions for 10 to 10^4 bits, malachite-nz 0.9.1 versus dashu, ibig, num-bigint and rug (GMP). |
| **Metric** | latency |
| **Hardware** | Apple M2 Max, macOS (Darwin 25.5.0, arm64) |
| **Compiler and flags** | rustc 1.92.0 (ded5c06cf 2025-12-08); cargo bench --features gmp with Cargo's default bench profile (opt-level=3; no [profile] override, no .cargo/config); criterion 0.5.1, 1 s warm-up, 2 s measurement, 100 samples; malachite-nz 0.9.1, rug 1.30.0 via gmp-mpfr-sys 1.7.1 (Cargo.lock); the GMP build (bundled or system) is not stated |
| **Adoption** | 586 stars |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/mhogrefe/malachite) · [benchmark](https://github.com/DRMacIver/rust-bigint-benchmarks/blob/main/benchmark-report.md) |

## Verdict

In DRMacIver's public Criterion suite (rustc 1.92.0, Cargo default bench profile, Apple M2 Max), malachite-nz 0.9.1 beat rug 1.30.0 (GMP) on 10-bit operations (add, mul, gcd, extended gcd, pow, to_dec) and on hex/decimal parsing at all sizes up to 10^4 bits, but rug won add, sub, mul, div, pow and modular arithmetic from about 100-1,000 bits upward. The small-value wins come from avoiding rug's per-result heap allocation rather than from faster limb kernels.

## Use it when

- Rust code dominated by values under 64 bits that must not overflow (interpreters, exact counters, property-test shrinkers): 10-bit add 2.1 ns vs rug 17.7 ns, gcd 8.5 ns vs 20.9 ns, pow 5.1 ns vs 41.6 ns
- Parsing many decimal or hex strings: from_dec and from_hex beat rug at every size up to 10^4 bits (from_dec 8.37 us vs 11.51 us at 10^4 bits)
- Pure-Rust, no_std or wasm targets that need GMP-class asymptotics (Toom, FFT, half-GCD) without a C toolchain or GMP build
- Projects that want rationals and big integers with the same API family, or a num-bigint replacement via malachite-bigint (as RustPython does)

## Skip it when

- Operands above about 1,000 bits where raw speed matters: rug/GMP is faster on mul (8.28 us vs 4.52 us at 10^4 bits), div, pow and modular pow (250.90 ms vs 143.02 ms at 10^4 bits), and on every task in tczajka's suite (e to 10M digits 3.689 s vs 2.788 s)
- Values of 65-128 bits: they already allocate (ubig_add at 100 bits 18.7 ns vs dashu 3.7 ns), so dashu is faster there
- C or C++ codebases: there is no C API; call GMP directly
- Closed-source distribution without accepting LGPL-3.0-only terms; Rust links crates statically by default, so the LGPL relinking obligations apply (issue #52 asked for a permissive license; it remains LGPL-3.0-only)
- Arbitrary-precision floats in production: the README says malachite-float is not yet feature-complete

## How it is fast

A Natural is an enum of Small(Limb) or Large(Vec&lt;Limb&gt;), so any value below 2^64 lives inline without a heap allocation, which is where it beats rug/mpz. For large operands it ports GMP's machinery: schoolbook, Toom-22/33/44/6h/8h and unbalanced Toom variants with GMP-style tuned thresholds (Toom-22 from 16 limbs on 64-bit), a small-prime FFT derived from Daniel Schultz's FLINT code plus Schonhage-Strassen from William Hart's FLINT code, GMP's divide-and-conquer and mu division with Newton inversion, and a subquadratic half-GCD. By-value operator overloads reuse the operand's buffer to avoid allocations in chains like &x + &y + &z.

## Compared with alternatives

Pick malachite over ibig and dashu when operands grow past a few thousand bits or you need gcd, modular and rational arithmetic with GMP-derived algorithms (the report finds it usually second to rug at 1,000-10^4 bits); pick dashu instead for 65-128-bit values or a permissive license, and FLINT or GMP itself from C/C++.

## Integration

| | |
|---|---|
| **Form** | crate (use the malachite meta-crate; malachite-nz holds the integer code) |
| **Dependencies** | malachite-base, itertools, libm, wide; optional serde, pyo3 (enable_pyo3), rand-based 'random' feature |
| **Minimum toolchain** | Rust 1.90 (rust-version for 0.9.x-0.12.0), edition 2024 |
| **Platforms** | any Rust target; 64-bit limbs by default, 32_bit_limbs feature for u32 limbs; no_std supported (closed issue #97 reported std leaking in through wide under no-default-features) |
| **Thread safety** | not documented explicitly; the crate is forbid(unsafe_code) unless enable_pyo3 is on, so Natural/Integer are ordinary owned values whose Send/Sync follow Rust's auto-trait rules |
| **Drop-in for the baseline** | partial: malachite-bigint is a drop-in for Rust's num-bigint; there is no rug- or GMP-compatible API (issue #91 'Rug API compatibility?' is open) |

## Gotchas

- Fast versions move quickly (0.9.1 in February 2026 to 0.12.0 in September 2026, minor-version bumps with API changes, e.g. issue #58 export incompatibility in 0.4.19+); pin versions
- Issue #90 reported e to 1M digits at about 7000 ms on 0.7.0 and newer vs 800 ms on 0.6.1; it was closed 2026-06-18, the day before 0.9.2, so the benchmarked 0.9.1 may carry that regression (fix version not documented)
- Past panics on valid inputs, all closed: extended_gcd 'mid &gt; len' (#73), Natural::factorial assertion (#86), squaring 2^(2^25) (#55)
- Mixed operations with primitives are deliberately not implemented (no Natural + u64); convert with Natural::from, which is cheap below 2^64

## Known shortcomings

- Beats rug/GMP only at tiny operands and parsing; rug is faster from about 1000 bits; Rust only, no C++ API; license now LGPL-3.0-only.
- Benchmarked 0.9.1 may include a regression: issue #90 reports e to 1M digits at \~7000 ms on 0.7.0+ vs 800 ms on 0.6.1, closed 2026-06-18 (the day before 0.9.2) with the fix version undocumented; past panics on valid inputs (#55, #73, #86) closed; LGPL-3.0-only with static linking by default; no C API.

## Caveats and trade-offs

Malachite beats GMP only on one- and two-word integers, where GMP's per-value allocation dominates, and on decimal/hex parsing. The same report counts malachite fastest in 27 of 205 cases and rug in 52, with rug ahead on add, sub, mul, div, gcd, pow and modular arithmetic from about 100 to 1000 bits up. The second suite (github.com/tczajka/bigint-benchmark-rs, malachite 0.4.14 vs rug 1.24.1) has rug faster on every task: digits of e at 10M, rug 2.788 s vs malachite 3.689 s; Fibonacci at 100M, rug 2.937 s vs malachite 5.192 s. The report calls itself 'quick, machine-specific local numbers, not authoritative' and uses a short criterion measurement time. It benchmarks malachite-nz 0.9.1, while the repo is now at 0.12.0. Malachite's own site (malachite.rs) is blocked from this container, so no first-party claim was recorded. The library is pure Rust with no C/C++ API.

Pure Rust, no_std; LGPL-3.0 (GitHub page lists LGPL-3.0 and GPL-3.0; -only/-or-later variant not confirmed). Parts derived from GMP, FLINT and MPFR. No C API, so C++ use needs FFI.

## Maintenance

Very active (commits to 2026-09-30, 0.12.0 released 2026-09-20, about 2.8 million recent crates.io downloads for malachite-nz) and copyable as LGPL-3.0-only safe Rust; floats are still incomplete.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded B to A. DRMacIver/rust-bigint-benchmarks is a third-party suite (written for dashu) with public criterion code in benches/primitive.rs, small_int.rs, workload.rs and shrinker.rs, run against rug/GMP with --features gmp. The report states rustc 1.92.0 and an Apple M2 Max. The flags are Cargo's default bench profile (opt-level=3): Cargo.toml has no [profile] override, and the repo has no .cargo/config or rust-toolchain file. Cargo.lock pins malachite-nz 0.9.1, rug 1.30.0 and gmp-mpfr-sys 1.7.1.
- **Verifier notes:** Numbers match the report exactly. The baseline is rug (the Rust wrapper of GMP), so the tiny-operand wins partly reflect rug/mpz allocation overhead rather than GMP's kernels. Repo is active (last commit 2026-09-30) with 586 stars; malachite-nz/Cargo.toml declares LGPL-3.0-only, and the workspace is now at 0.12.0.
- **Fields the verifier corrected:** `license`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/DRMacIver/rust-bigint-benchmarks/HEAD/benchmark-report.md>
  - <https://github.com/DRMacIver/rust-bigint-benchmarks/blob/main/benchmark-report.md>
  - <https://github.com/DRMacIver/rust-bigint-benchmarks>
  - <https://raw.githubusercontent.com/DRMacIver/rust-bigint-benchmarks/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/DRMacIver/rust-bigint-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/DRMacIver/rust-bigint-benchmarks/HEAD/benches/primitive.rs>
  - <https://raw.githubusercontent.com/DRMacIver/rust-bigint-benchmarks/HEAD/Cargo.lock>
  - <https://raw.githubusercontent.com/tczajka/bigint-benchmark-rs/HEAD/README.md>
  - <https://github.com/mhogrefe/malachite>
  - <https://github.com/mhogrefe/malachite/commits>
  - <https://raw.githubusercontent.com/mhogrefe/malachite/HEAD/README.md>
  - <https://raw.githubusercontent.com/mhogrefe/malachite/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/mhogrefe/malachite/HEAD/malachite-nz/Cargo.toml>
- **Sources the enricher read:**
  - <https://github.com/mhogrefe/malachite>
  - <https://github.com/mhogrefe/malachite/tree/master/malachite-nz/src/natural/arithmetic>
  - <https://github.com/mhogrefe/malachite/issues?q=is%3Aissue>
  - <https://github.com/mhogrefe/malachite/issues/90>
  - <https://github.com/mhogrefe/malachite/issues/55>
  - <https://raw.githubusercontent.com/mhogrefe/malachite/HEAD/README.md>
  - <https://raw.githubusercontent.com/mhogrefe/malachite/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/mhogrefe/malachite/HEAD/malachite/Cargo.toml>
  - <https://raw.githubusercontent.com/mhogrefe/malachite/HEAD/malachite-nz/Cargo.toml>
  - <https://raw.githubusercontent.com/mhogrefe/malachite/HEAD/malachite-nz/README.md>
  - <https://raw.githubusercontent.com/mhogrefe/malachite/HEAD/malachite-nz/src/lib.rs>
  - <https://raw.githubusercontent.com/mhogrefe/malachite/HEAD/malachite-nz/src/natural/mod.rs>
  - <https://raw.githubusercontent.com/mhogrefe/malachite/HEAD/malachite-nz/src/natural/arithmetic/mul/mod.rs>
  - <https://raw.githubusercontent.com/mhogrefe/malachite/HEAD/malachite-nz/src/natural/arithmetic/mul/fft.rs>
  - <https://raw.githubusercontent.com/mhogrefe/malachite/HEAD/malachite-nz/src/natural/arithmetic/gcd/mod.rs>
  - <https://raw.githubusercontent.com/mhogrefe/malachite/HEAD/malachite-nz/src/natural/arithmetic/div_mod.rs>
  - <https://raw.githubusercontent.com/mhogrefe/malachite/HEAD/malachite-nz/src/platform_64.rs>
  - <https://raw.githubusercontent.com/mhogrefe/malachite/HEAD/malachite-bigint/README.md>
  - <https://crates.io/api/v1/crates/malachite>
  - <https://crates.io/api/v1/crates/malachite-nz>
  - <https://raw.githubusercontent.com/DRMacIver/rust-bigint-benchmarks/main/benchmark-report.md>
  - <https://raw.githubusercontent.com/tczajka/bigint-benchmark-rs/HEAD/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/mhogrefe/malachite`) · [data/wave8/enrich/raw/github_com_mhogrefe_malachite.json](../../../data/wave8/enrich/raw/github_com_mhogrefe_malachite.json) (enrichment confidence 0.8)

</details>
