# dashu (dashu-int)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Pure-Rust, no_std big-integer crate (an ibig fork) that beats GMP via rug on one- and two-word values.

| | |
|---|---|
| **Beats** | GNU GMP (mpz, via the Rust rug 1.30.0 crate; gmp-mpfr-sys 1.7.1 pinned in Cargo.lock) |
| **Claimed result** | Small operands: ubig_add at 100 bits dashu 3.7 ns vs rug 21.9 ns; ubig_div at 100 bits 5.7 ns vs 32.4 ns; ubig_mul at 100 bits 22.6 ns vs 25.1 ns; ubig_gcd at 1000 bits 2.87 us vs 3.05 us; ubig_from_hex at 10^4 bits 2.56 us vs 6.60 us. Report summary: dashu faster than rug in 98 of 153 small-value cases and in 123 of 205 head-to-head cases overall; the page says rug/GMP is typically 2-6x slower on tiny values because of a fixed per-value heap allocation. rug/GMP is faster from about 1000 bits (ubig_mul at 10^4 bits: rug 4.52 us vs dashu 12.76 us). |
| **Workload** | Criterion microbenchmarks of unsigned big-integer add/sub/mul/div/gcd/pow/modular ops swept over 10 to 10^4 bits, plus small-value (&lt;=128 bit) workloads and string round-trips, dashu-int 0.4.2 vs rug (GMP), ibig, num-bigint and malachite. |
| **Metric** | latency |
| **Hardware** | Apple M2 Max, macOS (arm64) |
| **Compiler and flags** | rustc 1.92.0 (ded5c06cf 2025-12-08); cargo bench --features gmp with the default bench profile (Cargo.toml sets no [profile] overrides, so opt-level 3, inherits release); criterion 0.5.1 run with --warm-up-time 1 --measurement-time 2 --sample-size 100; dashu-int 0.4.2, rug 1.30.0 with gmp-mpfr-sys 1.7.1 (Cargo.lock) |
| **Adoption** | 142 stars, 20 forks; dashu-int 3,894,865 crates.io downloads (1,662,908 recent) as of 2026-10-01 |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/cmpute/dashu) · [benchmark](https://github.com/DRMacIver/rust-bigint-benchmarks/blob/main/benchmark-report.md) |

## Verdict

DRMacIver/rust-bigint-benchmarks ran Criterion microbenchmarks (rustc 1.92.0, default bench profile, 2 s measurements) on an Apple M2 Max comparing dashu-int 0.4.2 with rug 1.30.0 (GMP via gmp-mpfr-sys 1.7.1) and other Rust crates: dashu was faster than rug in 98 of 153 small-value cases (e.g. 100-bit add 3.7 vs 21.9 ns), but rug won most cases from about 1000 bits upward. The report calls its numbers quick, machine-specific and not authoritative.

## Use it when

- Rust code where most integers fit in 128 bits but must not overflow (checked accumulators, parsers, symbolic or property-testing workloads): at 100 bits the report shows add 3.7 vs 21.9 ns and div 5.7 vs 32.4 ns against rug/GMP.
- no_std or WebAssembly targets, or projects that cannot link LGPL GMP: it is pure Rust under MIT OR Apache-2.0.
- Hex parsing and gcd around 1000 bits, where dashu matched or beat rug in the report (gcd 2.87 vs 3.05 us; from_hex at 10^4 bits 2.56 vs 6.60 us).
- When you need integers, rationals, decimals and binary floats from one consistent pure-Rust family.

## Skip it when

- Operands of about 1000 bits and up: rug/GMP wins add, sub, mul, div, pow and modular arithmetic there (mul at 10^4 bits 4.52 vs 12.76 us; modular pow at 1000 bits 305 vs 771 us).
- Large-number workloads such as computing many digits of a constant: in tczajka/bigint-benchmark-rs, 10M digits of e take 19.9 s with dashu 0.4.2 vs 2.8 s with rug, and Fibonacci(100M) 26.2 s vs 2.9 s.
- C++ projects: there is no C API, so using it from C++ means writing and maintaining Rust FFI shims; a C++ small-value library such as mp++ or Boost.Multiprecision cpp_int is simpler.
- Constant-time cryptography: no constant-time guarantees are documented (an optional zeroize feature exists, but that only clears memory).

## How it is fast

The internal Repr is a union that stores one- or two-word magnitudes inline (up to 128 bits on 64-bit targets) and only spills to the heap above that, so small values never allocate, while GMP via rug pays a heap allocation per value; 0.6.1 also copies inline values directly on clone and compares them as single words. Larger operands use schoolbook multiplication with a double-word addmul kernel (BMI2 mulx on x86-64 with std), Karatsuba, Toom-3 from 96 words and, since 0.4.3, Proth-prime NTT with Garner CRT above about 4,000 words; division is schoolbook plus divide-and-conquer, and gcd is Lehmer's algorithm.

## Compared with alternatives

Pick dashu over ibig (its ancestor) because it keeps two words inline and has a much faster gcd (10^4 bits: 64 us vs 851 us), and over Malachite when you need a permissive license instead of LGPL or want the float, decimal and rational crates; pick Malachite for better large-operand speed, and blip_mp or ctbignum only outside Rust.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | dashu-base, cfg-if, static_assertions, num-modular; optional num-order (default), num-traits, num-integer, rand, serde, zeroize, rkyv |
| **Minimum toolchain** | Rust 1.68 (MSRV for the default build; some optional features such as rkyv_v08 need Rust 1.81+) |
| **Platforms** | any Rust target (16-, 32- and 64-bit words); BMI2 mulx kernel on x86-64 with std; NTT multiplication compiled out on smaller-word targets |
| **Thread safety** | not documented; UBig and IBig are owned value types with no shared internal state |
| **Drop-in for the baseline** | no |

## Gotchas

- The benchmark measured dashu-int 0.4.2, but the current release is 0.6.1; 0.4.3 added NTT multiplication, Montgomery arithmetic and lower Toom-3 thresholds, so large-operand gaps to GMP may now be smaller, and the small-value numbers have not been re-measured.
- Versions before 0.4.3 could exhaust the scratch allocator in modular exponentiation for Karatsuba-sized moduli and panic in gcd_ext when one operand divides the other; before 0.5.1, gcd of two large similar-sized integers could abort with 'not enough memory allocated'. Use 0.5.1 or later.
- 0.5.0 changed IBig's serde binary format to two's-complement little-endian bytes, so data serialized by earlier versions does not deserialize.
- The small-value win is mostly about allocation: each benchmarked op returns a new value, so rug pays a heap allocation while dashu stays inline; the 100-bit div bench divides operands of equal bit length, so it measures overhead rather than long division.

## Known shortcomings

- Wins only on small operands (rug pays a heap allocation per result); benchmarked 0.4.2 while crates.io is at 0.6.1; hard fork of ibig (is_fork_of set); Rust only.
- Benchmarked 0.4.2 had crash bugs fixed later (modpow scratch under-allocation and gcd_ext panic fixed in 0.4.3, large gcd abort in 0.5.1); 0.4.3 added NTT and Montgomery, so large-operand numbers are stale against 0.6.1; issue #54 asks for a GMP comparison, no reply.

## Caveats and trade-offs

The report calls itself 'quick, machine-specific local numbers, not authoritative' (one laptop, 2 s measurement). It benchmarks dashu-int 0.4.2, while crates.io's current release is 0.6.1 (2026-09-25). Each bench op returns a new value, so rug pays a heap allocation per result while dashu stores up to two words inline; the small-value win is about allocation and inline storage, not GMP's mpn kernels. The ubig_div bench divides two operands of the same bit length (b = random + a), so the quotient is tiny and it measures overhead, not long division. The suite was written for (but not merged into) the dashu repo and generalises dashu's own primitive.rs bench, so it is not fully arm's-length. The bit-width sweep stops at 10^4 bits. A second suite by ibig's author (github.com/tczajka/bigint-benchmark-rs, rug 1.24.1, dashu 0.4.2) shows GMP-backed rug far ahead on large workloads: digits of e at 10M rug 2.788 s vs dashu 19.943 s; Fibonacci at 100M rug 2.937 s vs dashu 26.224 s. The win is limited to small operands (about two words) and gcd near 1000 bits.

Pure Rust, no_std, inline storage for values up to two words, so no heap allocation for small integers. Slower than GMP from about 1000 bits upward (GMP has tuned assembly and asymptotically faster algorithms). Rust API, so usable from C++ only through FFI. Not an mpz-compatible API.

## Maintenance

Actively maintained (last commit 2026-09-30, 0.6.1 released 2026-09-25, about 3.9 million crates.io downloads), dual MIT/Apache-2.0, pre-1.0 with occasional breaking changes between minor versions.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** Upgraded from B. The report's numbers come from public Criterion code in DRMacIver/rust-bigint-benchmarks (benches/primitive.rs, small_int.rs, workload.rs, shrinker.rs; tables generated by scripts/gen_report.py), which runs dashu-int 0.4.2 and rug 1.30.0 (gmp-mpfr-sys 1.7.1, pinned in Cargo.lock) in one process. The page states rustc 1.92.0 and an Apple M2 Max, and Cargo.toml has no [profile] overrides, so `cargo bench` uses the default bench profile (opt-level 3); code, compiler, flags and CPU are all public, as in earlier default-release-build precedents.
- **Verifier notes:** All claimed numbers are on the page in dashu's and rug's rows, and the second-suite numbers in the caveats match tczajka/bigint-benchmark-rs. Metadata checked: MIT OR Apache-2.0, not archived, not a GitHub fork, last commit 2026-09-30, 142 stars. Worth recording that the win is small-operand only and the measured version (0.4.2) is behind the current 0.6.1.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `claimed_speedup`, `is_fork_of`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/DRMacIver/rust-bigint-benchmarks/blob/main/benchmark-report.md>
  - <https://github.com/DRMacIver/rust-bigint-benchmarks>
  - <https://raw.githubusercontent.com/DRMacIver/rust-bigint-benchmarks/main/Cargo.toml>
  - <https://raw.githubusercontent.com/DRMacIver/rust-bigint-benchmarks/main/Cargo.lock>
  - <https://raw.githubusercontent.com/DRMacIver/rust-bigint-benchmarks/main/README.md>
  - <https://raw.githubusercontent.com/DRMacIver/rust-bigint-benchmarks/main/benches/primitive.rs>
  - <https://github.com/cmpute/dashu>
  - <https://github.com/cmpute/dashu/commits>
  - <https://raw.githubusercontent.com/tczajka/bigint-benchmark-rs/HEAD/README.md>
  - <https://crates.io/api/v1/crates/dashu-int>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/cmpute/dashu/HEAD/README.md>
  - <https://raw.githubusercontent.com/cmpute/dashu/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/cmpute/dashu/HEAD/integer/README.md>
  - <https://raw.githubusercontent.com/cmpute/dashu/HEAD/integer/Cargo.toml>
  - <https://raw.githubusercontent.com/cmpute/dashu/HEAD/integer/CHANGELOG.md>
  - <https://raw.githubusercontent.com/cmpute/dashu/HEAD/benchmark/README.md>
  - <https://raw.githubusercontent.com/cmpute/dashu/HEAD/integer/src/lib.rs>
  - <https://raw.githubusercontent.com/cmpute/dashu/HEAD/integer/src/repr.rs>
  - <https://raw.githubusercontent.com/cmpute/dashu/HEAD/integer/src/mul/mod.rs>
  - <https://raw.githubusercontent.com/cmpute/dashu/HEAD/integer/src/gcd/mod.rs>
  - <https://raw.githubusercontent.com/cmpute/dashu/HEAD/integer/src/div/mod.rs>
  - <https://github.com/cmpute/dashu/tree/master/integer/src>
  - <https://github.com/cmpute/dashu/issues>
  - <https://github.com/cmpute/dashu/issues/54>
  - <https://raw.githubusercontent.com/DRMacIver/rust-bigint-benchmarks/main/benchmark-report.md>
  - <https://raw.githubusercontent.com/tczajka/bigint-benchmark-rs/HEAD/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/cmpute/dashu`) · [data/wave8/enrich/raw/github_com_cmpute_dashu.json](../../../data/wave8/enrich/raw/github_com_cmpute_dashu.json) (enrichment confidence 0.8)

</details>
