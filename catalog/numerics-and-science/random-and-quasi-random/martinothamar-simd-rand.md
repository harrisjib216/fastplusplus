# simd-rand (SIMD Xoshiro256+ / Xoshiro256++ and frand generators for Rust)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust crate of 4- and 8-lane SIMD Xoshiro256+/++, frand and biski64 generators; about 4.5x scalar rand_xoshiro Xoshiro256+ on AVX-512.

| | |
|---|---|
| **Beats** | Scalar Xoshiro256+ (benchmark label 'rand/Xoshiro256+', from the rand crate ecosystem) |
| **Claimed result** | Scalar rand_xoshiro Xoshiro256+ 33.10 ns per batch of 64 u64 (1.93 Gelem/s) versus portable Xoshiro256+X8 7.51 ns (8.52 Gelem/s) and AVX-512 Xoshiro256+X8 7.08 ns (9.04 Gelem/s): about 4.4x and 4.7x (derived from page data). For the author's frand generator, the scalar upstream frand crate (autovectorised by the compiler) runs 3.18 ns and FrandX8 2.53 ns, only about 1.26x (derived from page data). The 13x figure in the earlier record compared FrandX8 with scalar Xoshiro256+, which is a different generator. README text: vectorised PRNGs 'may perform anywhere from 4-6 times faster'. |
| **Workload** | Criterion benchmark that generates and accumulates batches of u64x8 values (64 u64 values per iteration according to the page's Gelem/s figures) with scalar versus portable-SIMD and AVX-512 vectorised generators. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 9950X3D 16-core desktop |
| **Compiler and flags** | cargo +nightly (rustc version not stated; MSRV 1.89). .cargo/config.toml sets -C target-cpu=native; bench-top adds RUSTFLAGS -C target-feature=+avx2,+avx512f,+avx512dq,+avx512vl; release profile opt-level 3, lto = true, codegen-units = 1; pinned to one SMT pair with taskset and the performance governor |
| **Adoption** | 7 stars |
| **Last commit** | 2026-03-15 |
| **Links** | [repository](https://github.com/martinothamar/simd-rand) · [benchmark](https://raw.githubusercontent.com/martinothamar/simd-rand/HEAD/README.md) |

## Verdict

The author's Criterion run on an AMD Ryzen 9 9950X3D (unpinned cargo nightly, target-cpu=native plus AVX-512 RUSTFLAGS, LTO, one pinned SMT pair) took 33.1 ns to generate and sum 64 u64 values with scalar rand_xoshiro Xoshiro256+, versus 7.51 ns for the portable Xoshiro256+X8 and 7.08 ns for the AVX-512 version (about 4.4x and 4.7x, derived from page data). For frand the gain over the compiler-autovectorized scalar crate is only about 1.26x (3.18 ns vs 2.53 ns).

## Use it when

- Rust Monte Carlo or simulation kernels already written with std::simd or AVX2/AVX-512 intrinsics that consume random u64 or f64 vectors
- Bulk generation on x86-64 CPUs with AVX-512 (avx512f+avx512dq) or AVX2 where 8 independent streams are acceptable
- Throughput-bound code where the scalar rand_xoshiro Xoshiro256+ is a measured bottleneck
- Projects on nightly Rust that want a portable SIMD RNG that also compiles on non-x86 targets

## Skip it when

- C or C++ projects: it is a Rust crate with no C API, so it needs FFI work; use a C++ SIMD xoshiro sibling instead
- Code that needs the same sequence as a scalar generator, reproducible jump-ahead between lanes, or lane splitting (lane jumps are a README TODO)
- Stable Rust without x86 SIMD: the portable module needs nightly; the specific modules compile only with the matching target features
- Statistically critical work: the author says he is no expert and has only run PractRand; no TestU01 results are published
- Production use expecting a mature crate: one crates.io release (0.1.0, February 2026, 64 downloads), 7 stars

## How it is fast

Each lane holds an independent copy of the generator state (multi-stream), so one vector step of xoshiro256+ (add, shift by 17, four XORs, rotate by 45) produces 4 or 8 outputs at once; the scalar xoshiro256+ has a serial state dependency that the compiler does not vectorize. frand (a Weyl increment followed by a multiply-xor-shift mix) is simple enough that the compiler already autovectorizes the scalar crate, so FrandX8 gains only from keeping eight lane states resident instead of broadcasting one state each call.

## Compared with alternatives

Pick it when you are writing Rust and want SIMD xoshiro or frand vectors directly; for C++ the closest siblings are xoshiro8x256pp (8-way xoshiro256++ gist), Xoshiro256PlusSIMD and simdrng, and SHISHUA is faster still if you can switch generator. Romu and Squares are scalar designs, so they suit code that cannot batch.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | rand_core 0.9 |
| **Minimum toolchain** | Rust 1.89 (MSRV, edition 2024); nightly for the portable feature |
| **Platforms** | portable: any target with nightly std::simd; specific::avx2: x86-64 with AVX2 (extra paths with avx512dq/avx512vl); specific::avx512: x86-64 with avx512f and avx512dq |
| **Thread safety** | not documented; generators are plain owned state with no shared globals, so use one instance per thread |
| **Drop-in for the baseline** | no |

## Gotchas

- FrandX8::seed_from_u64 (portable and AVX-512 versions, and FrandX4) copies one seed into every lane, so all lanes emit the same stream; the README's own benchmark rows use it. Seed with distinct from_seed bytes when you need independent lanes
- The crates.io 0.1.0 release (2026-02-01) predates the 2026-03-15 'fix frand implementation (#34)' commit that made FrandX8 match the upstream frand crate; use the git main branch for upstream-identical frand output
- The crate uses a fair amount of unsafe for the intrinsics paths, and the specific modules silently vanish if the target features are not enabled at compile time (.cargo/config.toml in the repo sets target-cpu=native)
- Results are vectors, not single values; consuming them one element at a time through a scalar API gives back much of the speedup

## Known shortcomings

- rustc nightly unpinned; the 13x frand figure compares different generators (real FrandX8 vs scalar frand \~1.26x); correctness bug: FrandX8::seed_from_u64 gives 8 identical lanes (Xoshiro256+X8 and FrandX8 otherwise compute correct generators); Rust.
- FrandX8/FrandX4::seed_from_u64 gives identical lanes. crates.io 0.1.0 (2026-02-01, 64 downloads) predates the frand fix PR #34 (2026-03-15). Rust only; nightly needed for the portable module.

## Caveats and trade-offs

The speedup compares the same algorithm scalar versus lane-parallel, so it measures vectorisation, not a better algorithm. Checked: the portable and AVX-512 Xoshiro256+X8 lanes run the standard xoshiro256+ step (s0+s3 output, s1&lt;&lt;17, rotl 45), and FrandX8 lanes match the upstream frand crate (the crate's tests assert this), so the SIMD paths compute the named generators as 8 independent streams. FrandX8::seed_from_u64 copies one seed into all 8 lanes, so the lanes emit identical streams. Seed with distinct from_seed bytes for independent lanes; the timed FrandX8 rows used seed_from_u64. Benchmarks accumulate batches into u64x8 to keep the work observable, which favours wide registers. frand is the author's choice of a small generator, and the README says he is no expert in statistical testing (PractRand only). The latest commit is 'fix frand implementation (#34)'. README warns that older AVX-512 CPUs may throttle.

Rust crate (not callable from C++ without FFI work); the 8-lane generators produce eight independent streams per call, so the sequence differs from the scalar generator; lane jumps are not implemented (TODO in README); AVX-512 specific paths need avx512f and avx512dq, and the portable module needs nightly Rust.

## Maintenance

Active (last commit 2026-03-15) but young and lightly used: MIT, 7 stars, one 0.1.0 crates.io release that predates the frand fix; Rust-only, so C++ users would need to port the small generator kernels.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now C.
- **Tier reason:** The README Criterion output compares rand_xoshiro::Xoshiro256Plus (33.10 ns per 64 u64) with the portable and AVX-512 Xoshiro256+X8 (7.51 / 7.08 ns) on a stated Ryzen 9 9950X3D. The code is public (benches/top/mod.rs, run by 'make bench-top'), and the flags are stated (.cargo/config.toml target-cpu=native, Makefile AVX-512 RUSTFLAGS, release profile opt-level 3, LTO, codegen-units 1). But the toolchain is an unpinned 'cargo +nightly' with no rustc version, which earlier waves held to C (e.g. Criterion benches with no rustc version).
- **Verifier notes:** All README numbers match the record. The tier drops only because the rustc nightly version is unstated; everything else needed for A is present. The RNG same-generator check passed for Xoshiro256+X8 against rand_xoshiro::Xoshiro256Plus.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/martinothamar/simd-rand/HEAD/README.md>
  - <https://raw.githubusercontent.com/martinothamar/simd-rand/HEAD/Makefile>
  - <https://raw.githubusercontent.com/martinothamar/simd-rand/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/martinothamar/simd-rand/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/martinothamar/simd-rand/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/martinothamar/simd-rand/HEAD/benches/top/mod.rs>
  - <https://raw.githubusercontent.com/martinothamar/simd-rand/HEAD/src/portable/xoshiro256plusx8.rs>
  - <https://raw.githubusercontent.com/martinothamar/simd-rand/HEAD/src/specific/avx512/xoshiro256plus.rs>
  - <https://raw.githubusercontent.com/martinothamar/simd-rand/HEAD/src/portable/frandx8.rs>
  - <https://raw.githubusercontent.com/martinothamar/simd-rand/HEAD/src/frand.rs>
  - <https://github.com/martinothamar/simd-rand>
  - <https://github.com/martinothamar/simd-rand/tree/main/benches>
  - <https://github.com/martinothamar/simd-rand/tree/main/src/portable>
  - <https://github.com/martinothamar/simd-rand/commits/main>
- **Sources the enricher read:**
  - <https://github.com/martinothamar/simd-rand>
  - <https://github.com/martinothamar/simd-rand/pull/34>
  - <https://github.com/martinothamar/simd-rand/issues>
  - <https://raw.githubusercontent.com/martinothamar/simd-rand/HEAD/README.md>
  - <https://raw.githubusercontent.com/martinothamar/simd-rand/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/martinothamar/simd-rand/HEAD/Makefile>
  - <https://raw.githubusercontent.com/martinothamar/simd-rand/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/martinothamar/simd-rand/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/martinothamar/simd-rand/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/martinothamar/simd-rand/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/martinothamar/simd-rand/HEAD/src/frand.rs>
  - <https://raw.githubusercontent.com/martinothamar/simd-rand/HEAD/src/portable/mod.rs>
  - <https://raw.githubusercontent.com/martinothamar/simd-rand/HEAD/src/portable/simdrand.rs>
  - <https://raw.githubusercontent.com/martinothamar/simd-rand/HEAD/src/portable/xoshiro256plusx8.rs>
  - <https://raw.githubusercontent.com/martinothamar/simd-rand/HEAD/src/portable/frandx8.rs>
  - <https://raw.githubusercontent.com/martinothamar/simd-rand/HEAD/src/specific/mod.rs>
  - <https://raw.githubusercontent.com/martinothamar/simd-rand/HEAD/src/specific/avx512/mod.rs>
  - <https://raw.githubusercontent.com/martinothamar/simd-rand/HEAD/src/specific/avx512/xoshiro256plus.rs>
  - <https://raw.githubusercontent.com/martinothamar/simd-rand/HEAD/benches/top/mod.rs>
  - <https://crates.io/api/v1/crates/simd_rand>
  - <https://raw.githubusercontent.com/martinothamar/simd-rand/HEAD/src/portable/frandx4.rs>
  - <https://raw.githubusercontent.com/martinothamar/simd-rand/HEAD/src/specific/avx512/frand.rs>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/martinothamar/simd-rand`) · [data/wave8/enrich/raw/github_com_martinothamar_simd_rand.json](../../../data/wave8/enrich/raw/github_com_martinothamar_simd_rand.json) (enrichment confidence 0.8)

</details>
