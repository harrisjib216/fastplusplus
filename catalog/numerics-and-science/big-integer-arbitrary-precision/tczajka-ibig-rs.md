# ibig

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Pure-Rust big integers that beat GMP (via rug) only on one-word (&lt;=64-bit) values and on string parsing.

| | |
|---|---|
| **Beats** | GNU GMP (mpz, via the Rust rug 1.30.0 crate; gmp-mpfr-sys 1.7.1 pinned in Cargo.lock) |
| **Claimed result** | At 10 bits: ubig_add ibig 1.8 ns vs rug 17.7 ns, ubig_sub 1.5 ns vs 18.0 ns, ubig_mul 2.1 ns vs 18.0 ns, ubig_div 1.5 ns vs 28.3 ns. Parsing beats rug at every size: ubig_from_hex at 10^4 bits 2.55 us vs 6.60 us, ubig_from_dec 10.17 us vs 11.51 us; ibig_from_str_small 34.1 ns vs 111.3 ns. Already at 100 bits rug wins add/sub/div (ubig_add 25.7 ns vs 21.9 ns), and at 10^4 bits GMP wins clearly: ubig_mul rug 4.52 us vs ibig 12.69 us. |
| **Workload** | Criterion microbenchmarks of unsigned big-integer add, sub, mul, div at 10 to 10^4 bits, ibig 0.3.6 versus dashu, num-bigint, malachite-nz and rug (GMP). |
| **Metric** | latency |
| **Hardware** | Apple M2 Max, macOS (Darwin 25.5.0, arm64) |
| **Compiler and flags** | rustc 1.92.0 (ded5c06cf 2025-12-08); cargo bench --features gmp with the default bench profile (Cargo.toml sets no [profile] overrides, so opt-level 3, inherits release); criterion 0.5.1 run with --warm-up-time 1 --measurement-time 2 --sample-size 100; ibig 0.3.6, rug 1.30.0 with gmp-mpfr-sys 1.7.1 (Cargo.lock) |
| **Adoption** | 107 stars; ibig crate 875,051 crates.io downloads (118,046 recent) as of 2026-10-01; last crates.io release 0.3.6 (2022-09-17) |
| **Last commit** | 2026-07-24 |
| **Links** | [repository](https://github.com/tczajka/ibig-rs) · [benchmark](https://github.com/DRMacIver/rust-bigint-benchmarks/blob/main/benchmark-report.md) |

## Verdict

In DRMacIver's third-party Criterion suite (rustc 1.92.0, default bench profile, Apple M2 Max), ibig 0.3.6 beat rug 1.30.0/GMP on 10-bit add/sub/mul/div (1.5-2.1 ns vs 17.7-28.3 ns) and on hex/decimal parsing at all sizes, but lost to rug from 100 bits up on add/sub/div and at 10^4 bits on mul, gcd, pow, modular ops and formatting. The small-value win comes from avoiding a per-result heap allocation, not from faster limb kernels.

## Use it when

- Rust code where most values fit in 64 bits but must not overflow (counters, exact rationals with small parts, property-test shrinkers): one-word add/sub/mul/div measured 1.5-2.1 ns vs 17.7-28.3 ns for rug
- Parsing many decimal or hex strings into big integers: ubig_from_hex and ubig_from_dec beat rug at every size up to 10^4 bits
- Targets where linking GMP is impractical or LGPL is unacceptable: pure Rust, no_std, MIT OR Apache-2.0
- Embedded or wasm builds that need big integers without a C toolchain

## Skip it when

- Operands of two words or more: rug/GMP is already ahead at 100 bits on add, sub and div, and about 2.8x faster on 10^4-bit multiplication (4.52 us vs 12.69 us)
- gcd-heavy or modular-inverse-heavy code: gcd is a binary (quadratic) algorithm, 16x slower than rug at 10^4 bits (850.52 us vs 53.05 us) and 111x slower on extended gcd (7.82 ms vs 70.31 us)
- Large computations (millions of digits): multiplication stops at Toom-3 with no FFT/NTT path in the released code; ibig's own suite has 10M digits of e at 20.673 s vs rug 2.788 s
- Converting big values to strings: ubig_to_hex at 10^4 bits is 7.34 us vs rug 2.47 us
- C or C++ projects: there is no C API; use dashu or malachite only if you are in Rust anyway, otherwise GMP itself

## How it is fast

UBig is an enum: Small(Word) holds a value that fits in one machine word inline, and only longer values allocate a Buffer, so one-word arithmetic avoids the heap allocation that rug/mpz pays per result. Multiplication switches from schoolbook (&lt;=24 words) to Karatsuba (&lt;=192 words) to Toom-3; division is schoolbook below 32 words and recursive divide-and-conquer above; non-power-of-two parsing works in 256-word chunks combined with precomputed radix powers. On x86-64 limb add/sub use the _addcarry_u64/_subborrow_u64 intrinsics; there is no hand-written assembly.

## Compared with alternatives

Prefer dashu (a hard fork of ibig) in almost every case: it also inlines two-word values, has a subquadratic gcd (13x faster than ibig at 10^4 bits) and is within a few percent of ibig on add, mul and parsing at 1,000-10^4 bits in the same report. Pick ibig only for its smaller, frozen, permissively licensed 0.3.6 codebase; pick malachite or rug when operands exceed about 1,000 bits, and Boost.Multiprecision fixed cpp_int or ctbignum from C++.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | ibig 0.3.6: cfg-if, static_assertions, num-traits (no_std); optional rand 0.8, serde 1.0 |
| **Minimum toolchain** | Rust 1.49 for the crates.io 0.3.6 release (crates.io rust_version); the repo's ibig-old copy now declares 1.93 and the unreleased 0.4.0 rewrite needs 1.95 (edition 2024) |
| **Platforms** | any Rust target; x86 and x86-64 get carry intrinsics, other targets use generic 16/32/64-bit word code |
| **Thread safety** | not documented; UBig/IBig are plain owned values and no global mutable state was seen in the source read |
| **Drop-in for the baseline** | no |

## Gotchas

- The repository's main code (ibig 0.4.0 on ibig-core) is a from-scratch rewrite its README calls 'in early development'; the benchmarked and published code is 0.3.6 (2022-09-17), kept in ibig-old/, so the GitHub HEAD and the crate differ
- Only one word is stored inline: 65-128-bit values (u128, i128) already allocate, e.g. ubig_from_u128 21.4 ns vs dashu 1.8 ns
- UBig is capped at UBig::MAX_BIT_LEN (close to usize::MAX bits) and panics if exceeded; gcd(0, 0) panics
- Issue #18 ('0 shouldn't have a modular inverse') was closed in November 2022, after the last release; whether 0.3.6 is affected is not documented

## Known shortcomings

- Wins only on 1-word values and parsing; rug is ahead from 100 bits; gcd 16x slower at 1e4 bits; last crate release 0.3.6 (2022); Rust only.
- GitHub HEAD is an unreleased 0.4.0 rewrite ('early development'); the benchmarked code is 0.3.6 (2022, kept in ibig-old/) with binary (quadratic) gcd and multiplication capped at Toom-3 (explains large-operand losses); issue #18 (modular inverse of 0) closed after the last release; dashu beats it nearly everywhere.

## Caveats and trade-offs

Win over GMP is confined to one-word integers (about 10 bits in the sweep) and to string parsing; from 100 bits rug is ahead on add/sub/div, and ibig's gcd is far slower than rug at every size from 100 bits (ubig_gcd at 10^4 bits 850.52 us vs 53.05 us). Each bench op returns a new value, so rug pays a heap allocation per result while ibig stores one word inline; the small-value win is about allocation, not GMP's kernels. The ubig_div bench divides equal-length operands (tiny quotient). The benchmarked crate is ibig 0.3.6, the last crates.io release (2022-09-17); the repository has since been restructured (ibig, ibig-core, ibig-old directories; rustc 1.95 MSRV), so current code may differ. In the second suite by ibig's own author (github.com/tczajka/bigint-benchmark-rs, rug 1.24.1) ibig is far behind rug on large workloads (digits of e at 10M: rug 2.788 s vs ibig 20.673 s). Dashu, a hard fork of ibig, is its own entry. The report calls itself non-authoritative (one laptop, 2 s measurement).

Pure Rust, no_std, inline small-integer representation; no subquadratic gcd (10-13x slower than dashu/malachite/rug at 10^4 bits), no C API.

## Maintenance

The repo is active (commits in July 2026) but on an unreleased rewrite; the crate has had no release since 0.3.6 in September 2022, still draws about 118k recent downloads, and is MIT OR Apache-2.0, small and pure Rust, so the old version is easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded from B. The same public Criterion suite (DRMacIver/rust-bigint-benchmarks benches/primitive.rs and small_int.rs; Ibig backend) runs ibig 0.3.6 and rug 1.30.0 (gmp-mpfr-sys 1.7.1, Cargo.lock) side by side. The page states rustc 1.92.0 and an Apple M2 Max, and Cargo.toml has no [profile] overrides (default bench profile, opt-level 3), so code, compiler, flags and CPU are all public.
- **Verifier notes:** Numbers verified in ibig's column of the shared report. Metadata checked: MIT OR Apache-2.0, not archived, not a fork, last commit 2026-07-24, 107 stars, MSRV 1.95 and ibig-old directory confirmed. The win is narrow (one-word values and parsing); the crate has had no release since 2022 even though the repo is active.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `claimed_speedup`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/DRMacIver/rust-bigint-benchmarks/blob/main/benchmark-report.md>
  - <https://github.com/DRMacIver/rust-bigint-benchmarks>
  - <https://raw.githubusercontent.com/DRMacIver/rust-bigint-benchmarks/main/Cargo.toml>
  - <https://raw.githubusercontent.com/DRMacIver/rust-bigint-benchmarks/main/Cargo.lock>
  - <https://raw.githubusercontent.com/DRMacIver/rust-bigint-benchmarks/main/benches/primitive.rs>
  - <https://github.com/tczajka/ibig-rs>
  - <https://github.com/tczajka/ibig-rs/commits>
  - <https://raw.githubusercontent.com/tczajka/bigint-benchmark-rs/HEAD/README.md>
  - <https://crates.io/api/v1/crates/ibig>
- **Sources the enricher read:**
  - <https://github.com/tczajka/ibig-rs>
  - <https://github.com/tczajka/ibig-rs/tree/master/ibig-old/src>
  - <https://github.com/tczajka/ibig-rs/issues?q=is%3Aissue>
  - <https://github.com/tczajka/ibig-rs/issues/18>
  - <https://github.com/tczajka/ibig-rs/issues/13>
  - <https://raw.githubusercontent.com/tczajka/ibig-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/tczajka/ibig-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/tczajka/ibig-rs/HEAD/ibig/Cargo.toml>
  - <https://raw.githubusercontent.com/tczajka/ibig-rs/HEAD/ibig/README.md>
  - <https://raw.githubusercontent.com/tczajka/ibig-rs/HEAD/ibig-old/Cargo.toml>
  - <https://raw.githubusercontent.com/tczajka/ibig-rs/HEAD/ibig-core/Cargo.toml>
  - <https://raw.githubusercontent.com/tczajka/ibig-rs/main/ibig-old/src/lib.rs>
  - <https://raw.githubusercontent.com/tczajka/ibig-rs/main/ibig-old/src/ubig.rs>
  - <https://raw.githubusercontent.com/tczajka/ibig-rs/main/ibig-old/src/mul/mod.rs>
  - <https://raw.githubusercontent.com/tczajka/ibig-rs/main/ibig-old/src/mul/ntt.rs>
  - <https://raw.githubusercontent.com/tczajka/ibig-rs/main/ibig-old/src/div/mod.rs>
  - <https://raw.githubusercontent.com/tczajka/ibig-rs/main/ibig-old/src/div/divide_conquer.rs>
  - <https://raw.githubusercontent.com/tczajka/ibig-rs/main/ibig-old/src/gcd.rs>
  - <https://raw.githubusercontent.com/tczajka/ibig-rs/main/ibig-old/src/parse/mod.rs>
  - <https://raw.githubusercontent.com/tczajka/ibig-rs/main/ibig-old/src/parse/non_power_two.rs>
  - <https://raw.githubusercontent.com/tczajka/ibig-rs/main/ibig-old/src/fmt/mod.rs>
  - <https://raw.githubusercontent.com/tczajka/ibig-rs/main/ibig-old/src/arch/mod.rs>
  - <https://raw.githubusercontent.com/tczajka/ibig-rs/main/ibig-old/src/arch/x86_64/mod.rs>
  - <https://raw.githubusercontent.com/tczajka/ibig-rs/main/ibig-old/src/arch/x86_64/add.rs>
  - <https://raw.githubusercontent.com/tczajka/ibig-rs/main/ibig-old/src/arch/generic_64_bit/ntt.rs>
  - <https://raw.githubusercontent.com/tczajka/ibig-rs/main/ibig-old/src/memory.rs>
  - <https://raw.githubusercontent.com/tczajka/ibig-rs/main/ibig-old/src/buffer.rs>
  - <https://raw.githubusercontent.com/tczajka/ibig-rs/main/ibig-old/src/pow.rs>
  - <https://raw.githubusercontent.com/tczajka/ibig-rs/main/ibig-old/src/modular/mod.rs>
  - <https://raw.githubusercontent.com/tczajka/ibig-rs/main/ibig-old/src/modular/div.rs>
  - <https://crates.io/api/v1/crates/ibig>
  - <https://raw.githubusercontent.com/DRMacIver/rust-bigint-benchmarks/main/benchmark-report.md>
  - <https://raw.githubusercontent.com/tczajka/bigint-benchmark-rs/HEAD/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/tczajka/ibig-rs`) · [data/wave8/enrich/raw/github_com_tczajka_ibig_rs.json](../../../data/wave8/enrich/raw/github_com_tczajka_ibig_rs.json) (enrichment confidence 0.8)

</details>
