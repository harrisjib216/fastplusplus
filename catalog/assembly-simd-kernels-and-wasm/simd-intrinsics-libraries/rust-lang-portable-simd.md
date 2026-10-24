# Rust portable SIMD (std::simd / portable-simd)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Rust nightly's std::simd: one portable Simd&lt;T, N&gt; type that beat scalar and autovectorized Rust loops 5-13x in a byte count.

| | |
|---|---|
| **Beats** | scalar loops (Rust for-loop and Rust iterator version; also a C for-loop and NumPy as reference rows) |
| **Claimed result** | random_sp: portable_simd 19.874 GiB/s (589,654 ns/iter) vs Rust iter 3.978 GiB/s, Rust for_loop 1.482 GiB/s, C for_loop 1.482 GiB/s, C original 0.278 GiB/s, NumPy 5.711 GiB/s; about 5.0x over the Rust iterator and 13.4x over the Rust and C for-loops (derived from page data). random_printable: 19.870 vs 3.979 (Rust iter), 1.481 (Rust for_loop) and 1.478 GiB/s (C for_loop and C original). |
| **Workload** | Independent 'sp' benchmark from the 'six times faster than C' blog post: return the number of 's' bytes minus the number of 'p' bytes over 12 MiB of random 's'/'p' characters (random_sp) or 12 MiB of random printable ASCII (random_printable). The Rust portable_simd version compares 16 bytes at a time (u8x16) against scalar Rust (for-loop, iterator), C (original, while-loop, for-loop) and NumPy versions. |
| **Metric** | throughput |
| **Hardware** | Apple MacBook Pro M1 (2020), 8 GB RAM, up to 3.2 GHz, 12 MB L2 |
| **Compiler and flags** | rustc 1.68.0-nightly (61a415be5 2023-01-12), LLVM 15.0.6; Apple clang 14.0.0 (clang-1400.0.29.202) for the C rows. Run with cargo bench. Cargo.toml has no profile overrides, so the default bench profile applies (opt-level 3, no target-cpu flag). build.rs compiles the C sources through the cc crate with -mcpu=apple-m1 and the optimization level of the cargo profile. |
| **Adoption** | 1.1k stars; the std::simd implementation in Rust nightly |
| **Last commit** | 2026-09-16 |
| **Links** | [repository](https://github.com/rust-lang/portable-simd) · [benchmark](https://github.com/eddieantonio/fast-sp) |

## Verdict

A third-party demo (eddieantonio/fast-sp) counted 's' minus 'p' bytes over 12 MiB inputs with Rust's #[bench] harness on an Apple M1, using rustc 1.68.0-nightly (2023-01-12, LLVM 15.0.6) and Apple clang 14 with -mcpu=apple-m1 for C. The portable_simd version (u8x16) reached 19.87 GiB/s against 3.98 GiB/s for the autovectorized Rust iterator and about 1.48 GiB/s for the scalar Rust and C loops, with all versions asserted equal on both inputs.

## Use it when

- You already use nightly Rust and want one SIMD source that compiles for x86-64, aarch64 and other targets without per-architecture std::arch code.
- Byte scanning, counting, comparison and other lane-wise kernels where LLVM's autovectorizer gives up or picks a poor accumulator width, as in the fast-sp count (about 19.9 GiB/s against 4.0 GiB/s for the autovectorized iterator on an M1).
- Floating-point loops that do not autovectorize because float addition is not associative; an open issue (#297) shows SIMD f64 sums about 4x faster than a plain f64 loop, while integer sums gained nothing.
- Code that should behave identically on every target: the docs promise IEEE-consistent semantics (for example simd_min matching f32::min) except subnormal flushing on armv7 and powerpc.

## Skip it when

- Stable Rust: the API is behind #![feature(portable_simd)], and the 'critical issues before stabilization' thread (#364, opened 2023) was still waiting on two structural API changes (PRs #493 and #483) in August 2026.
- Kernels that need a specific instruction or non-IEEE semantics: the docs say std::arch can be slightly faster (for example _mm_min_ps against simd_min), and open issues report masks that do not optimize as well as hand-written x86 code (#472), bad codegen for OR/AND masks (#303) and functions that scalarize after inlining (#321).
- Integer reductions that LLVM already autovectorizes: issue #297 measured u64/i64 SIMD sums on AVX-512 no faster than a plain iterator loop.
- Vector transcendental math: StdFloat sin/cos/exp/ln lower to LLVM intrinsics that, per the crate's own docs, may fall back to the platform math.h; use a dedicated vector math library for those.
- Runtime CPU dispatch across feature levels: features are fixed at compile time, running a binary built for a feature the CPU lacks is undefined behaviour, and swizzle_dyn's implementation is chosen when std itself is built (-Zbuild-std may be needed).

## How it is fast

Simd&lt;T, N&gt; is a #[repr(simd)] type whose operations lower to LLVM's generic vector IR and simd_\* compiler intrinsics, so LLVM picks the target's instructions (SSE/AVX/AVX-512, NEON, wasm simd128 and others). In the fast-sp test the code compares 16 bytes per iteration against splatted 's' and 'p', turns the masks into 0/-1 lanes and reduces within narrow i8 lanes. The scalar baselines either stay scalar (branchless cinc/csel) or autovectorize into an isize-wide sum that fits only two lanes per 128-bit register.

## Compared with alternatives

Pick it over packed_simd for any new Rust code, because packed_simd is archived and superseded by this API. Pick glam or ultraviolet instead when you only need small linear-algebra types, and EVE or std::experimental::simd (marcelcases/simd) when the project is C++.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (ships in nightly core/std as core::simd and std::simd; std_float math trait needs std) |
| **Minimum toolchain** | Rust nightly with #![feature(portable_simd)]; the repository itself pins nightly-2026-04-28 and edition 2024 |
| **Platforms** | any Rust target (scalar fallback where SIMD is missing); tuned paths for x86/x86-64, aarch64 and armv7 NEON, wasm32, powerpc, loongarch64 and hexagon |
| **Thread safety** | not documented; Simd&lt;T, N&gt; is a plain value type with no shared state |
| **Drop-in for the baseline** | partial — scalar loops must be rewritten into vector chunks with explicit head and tail handling; there is no automatic vectorizing iterator |

## Gotchas

- Float reduce_sum and reduce_product use ordered (sequential) LLVM reductions, and float reduce_max/reduce_min fold over the array in scalar code; keep accumulators in vectors and reduce once at the end.
- Simd&lt;T, N&gt; is passed and returned through memory unless the call is inlined, so the docs recommend #[inline] on functions that take or return vectors.
- Integer operators wrap silently even in debug builds, integer division by zero still panics, N must be 1 to 64, and mask layout is unspecified.
- Simd&lt;T, N&gt; has a larger alignment than [T; N]: read and write through raw pointers with read_unaligned/write_unaligned or use as_simd; aligned read on a T-aligned slice is undefined behaviour.

## Known shortcomings

- Evidence is a 3-star demo (eddieantonio/fast-sp, Apple M1, rustc 1.68.0-nightly); tier A rests on flags read from the build files (default cargo bench profile, cc -mcpu=apple-m1) rather than stated in prose. The table was measured on 2023 code and not re-run after the 2026-07-30 switch to std::simd::prelude. The workload is a net count of 's' minus 'p'.
- Enricher: the rust_iter baseline sums into isize (2 lanes per 128-bit register) while the SIMD version reduces in i8 lanes, a same-task idiom difference that accounts for part of the 5.0x; README table from 2023 code; stabilisation still blocked (issue #364).

## Caveats and trade-offs

The measured repo (eddieantonio/fast-sp) is a third-party, single-author demo with 3 stars and AGPL-3.0 benchmark code; the library itself is Apache-2.0 OR MIT. It covers one microbenchmark (count of 's' minus count of 'p') on one Apple M1 machine (NEON, 16-byte vectors) with a 2023-01-12 nightly, so today's portable_simd may differ. The README table comes from the 2023 code. On 2026-07-30 the author moved rust_portable_simd.rs to std::simd::prelude and added a rust_portable_simd_v2 variant, but did not re-run the table. The baselines are scalar loops for the same task. The README says the Rust and C for-loops compile to branchless scalar code (cinc/csel) and the iterator version autovectorizes into messy code, so the win is explicit SIMD over scalar or weakly autovectorized code, not over another SIMD library. No comparison against std::arch intrinsics, C++ std::experimental::simd, xsimd or Highway was found. The portable-simd README has no benchmark numbers, and the book's roughly 41 percent matrix-multiply figure (first-party, measured on the author's machine) was not checked. Correctness is tested in the repo: all implementations are asserted equal on both 12 MiB inputs. Timing uses Rust's built-in nightly #[bench] harness with the input behind black_box. Portable-simd PR #548 (AVX2 swizzle_dyn) reports 33 percent less time on a 'Zen2 laptop', but it measures against the library's own previous code and states no CPU model, compiler or benchmark code. [retier] Enricher: the fast-sp rust_iter baseline sums into isize, so the autovectorised loop gets only 2 lanes per 128-bit register, while the SIMD version reduces in i8 lanes per 16 bytes; part of the 5.0x is that accumulator width. The README table comes from 2023 code and was not rerun after the 2026-07-30 changes. Gotchas: float reduce_sum is ordered (sequential) and float reduce_max/reduce_min are a scalar fold; Simd values pass through memory unless inlined; swizzle_dyn's fast path needs std rebuilt (-Zbuild-std); issue #297 finds u64/i64 SIMD sums no faster than an autovectorised loop; stabilisation is still blocked (issue #364, PRs #493 and #483, August 2026).

Nightly-only (#![feature(portable_simd)]), API unstable. One Simd&lt;T, N&gt; type for every architecture, lanes up to 64, aliases up to 512-bit; masks have unspecified layout. The std::simd docs say arch-specific intrinsics may sometimes be slightly faster, with slightly different semantics, for example min without strict IEEE handling.

## Maintenance

Actively developed (last commit 2026-09-16, 94 open issues) and dual MIT/Apache-2.0, but nightly-only with no stabilization date, so production use means pinning a nightly toolchain.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded from B: the fast-sp repo (a third-party demo, not a well-known suite, so B does not fit) publishes the benchmark code (src/lib.rs #[bench] harness, src/implementations/rust_portable_simd.rs, rust_for_loop.rs, rust_iter.rs, c/\*.c, build.rs) running portable_simd against scalar Rust and C loops. The README states rustc 1.68.0-nightly (2023-01-12) / LLVM 15.0.6, Apple clang 14.0.0 and the Apple M1 CPU, and the flags follow from the public build files: the default cargo bench profile, and cc with -mcpu=apple-m1 in build.rs.
- **Verifier notes:** Numbers match the fast-sp README exactly. The record's workload wrongly said 'count transitions'; it is a net count. Tier A rests on flags read from the public Cargo.toml and build.rs rather than stated in prose; B was wrong either way, because this is neither a paper nor a well-known suite. Metadata checked on github.com (gh CLI blocked): 1.1k stars, Apache-2.0 and MIT, not archived, last commit 2026-09-16 on main.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-129 (wave 13 book seed pass, 2026-10-24); enrichment (wave 13 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/eddieantonio/fast-sp>
  - <https://raw.githubusercontent.com/eddieantonio/fast-sp/HEAD/README.md>
  - <https://raw.githubusercontent.com/eddieantonio/fast-sp/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/eddieantonio/fast-sp/HEAD/build.rs>
  - <https://raw.githubusercontent.com/eddieantonio/fast-sp/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/eddieantonio/fast-sp/HEAD/src/implementations/rust_portable_simd.rs>
  - <https://raw.githubusercontent.com/eddieantonio/fast-sp/HEAD/src/implementations/rust_iter.rs>
  - <https://raw.githubusercontent.com/eddieantonio/fast-sp/HEAD/src/implementations/rust_for_loop.rs>
  - <https://raw.githubusercontent.com/eddieantonio/fast-sp/HEAD/c/with-explicit-size.c>
  - <https://github.com/eddieantonio/fast-sp/tree/main/src/implementations>
  - <https://github.com/eddieantonio/fast-sp/commits/main>
  - <https://github.com/rust-lang/portable-simd>
  - <https://raw.githubusercontent.com/rust-lang/portable-simd/HEAD/README.md>
  - <https://github.com/rust-lang/portable-simd/commits/main>
  - <https://github.com/rust-lang/portable-simd/pull/548>
- **Sources the enricher read:**
  - <https://github.com/rust-lang/portable-simd>
  - <https://raw.githubusercontent.com/rust-lang/portable-simd/HEAD/README.md>
  - <https://raw.githubusercontent.com/rust-lang/portable-simd/HEAD/beginners-guide.md>
  - <https://raw.githubusercontent.com/rust-lang/portable-simd/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/rust-lang/portable-simd/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/rust-lang/portable-simd/HEAD/crates/core_simd/Cargo.toml>
  - <https://raw.githubusercontent.com/rust-lang/portable-simd/HEAD/crates/core_simd/src/lib.rs>
  - <https://raw.githubusercontent.com/rust-lang/portable-simd/HEAD/crates/core_simd/src/mod.rs>
  - <https://raw.githubusercontent.com/rust-lang/portable-simd/HEAD/crates/core_simd/src/core_simd_docs.md>
  - <https://raw.githubusercontent.com/rust-lang/portable-simd/HEAD/crates/core_simd/src/vector.rs>
  - <https://raw.githubusercontent.com/rust-lang/portable-simd/HEAD/crates/core_simd/src/simd/num/float.rs>
  - <https://raw.githubusercontent.com/rust-lang/portable-simd/HEAD/crates/core_simd/src/swizzle_dyn.rs>
  - <https://raw.githubusercontent.com/rust-lang/portable-simd/HEAD/crates/std_float/src/lib.rs>
  - <https://github.com/rust-lang/portable-simd/issues?q=is%3Aissue%20state%3Aopen%20performance>
  - <https://github.com/rust-lang/portable-simd/labels>
  - <https://github.com/rust-lang/portable-simd/issues/364>
  - <https://github.com/rust-lang/portable-simd/issues/297>
  - <https://github.com/rust-lang/portable-simd/issues/472>
  - <https://github.com/eddieantonio/fast-sp/commits/main>
  - <https://raw.githubusercontent.com/eddieantonio/fast-sp/HEAD/README.md>
  - <https://raw.githubusercontent.com/eddieantonio/fast-sp/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/eddieantonio/fast-sp/HEAD/build.rs>
  - <https://raw.githubusercontent.com/eddieantonio/fast-sp/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/eddieantonio/fast-sp/HEAD/src/implementations/mod.rs>
  - <https://raw.githubusercontent.com/eddieantonio/fast-sp/HEAD/src/implementations/rust_portable_simd.rs>
  - <https://raw.githubusercontent.com/eddieantonio/fast-sp/HEAD/src/implementations/rust_portable_simd_v2.rs>
  - <https://raw.githubusercontent.com/eddieantonio/fast-sp/HEAD/src/implementations/rust_iter.rs>
  - <https://raw.githubusercontent.com/eddieantonio/fast-sp/HEAD/src/implementations/rust_for_loop.rs>
  - <https://raw.githubusercontent.com/eddieantonio/fast-sp/HEAD/c/with-explicit-size.c>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/rust-lang/portable-simd`) · [data/wave13/enrich/raw/github_com_rust_lang_portable_simd.json](../../../data/wave13/enrich/raw/github_com_rust_lang_portable_simd.json) (enrichment confidence 0.8)

</details>
