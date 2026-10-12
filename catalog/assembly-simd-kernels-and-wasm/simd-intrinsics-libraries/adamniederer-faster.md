# faster (Rust SIMD iterators)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust` · `MPL-2.0` · 🔴 abandoned

> Rust iterator-style explicit SIMD (simd_iter/simd_map/simd_reduce) with scalar polyfills; author's 2017-18 runs beat scalar iterators 1.15-8x.

| | |
|---|---|
| **Beats** | scalar Rust iterators |
| **Claimed result** | README (author's 'extremely unscientific' cargo bench runs on an Ivy Bridge host): target-cpu=ivybridge (AVX): map_scalar 6,963 ns/iter vs map_simd 879 ns/iter (about 7.9x, derived from page data); reduce_scalar 6,905 vs reduce_simd 839 ns/iter (about 8.2x, derived from page data); target-cpu=x86-64 (SSE2): map 7,237 vs 1,879 ns/iter (about 3.9x, derived from page data); target-cpu=pentium (polyfills only): map 7,195 vs 6,271 ns/iter (about 1.15x, derived from page data). Some rows are slower with SIMD: zip_simd 1,128 vs zip_scalar 901 ns/iter on the AVX target; bench_determinant3_simd 593 vs 354 ns/iter and bench_nop_simd 69 vs 38 ns/iter on the pentium target. |
| **Workload** | cargo bench over a 1024-element f32 array filled with -123.456 (benches/usage.rs). map_scalar computes 9\*sqrt(ceil(recip(sqrt(sqrt(abs(v))))))-4-2 per element and collects into a Vec; map_simd computes 9\*sqrt(ceil(rsqrt(sqrt(abs(v)))))-4-2 with faster's rsqrt, which on x86 is the approximate _mm256_rsqrt_ps/_mm_rsqrt_ps instruction, then scalar_collect. Built for ivybridge (AVX), x86-64 (SSE2) and pentium (polyfill only) targets on an Ivy Bridge host. |
| **Metric** | throughput |
| **Hardware** | host is ivybridge (only stated in README comments); exact CPU model not given |
| **Compiler and flags** | cargo bench (Cargo.toml profile.release opt-level = 3) with RUSTFLAGS='-C target-cpu=ivybridge' / 'x86-64' / 'pentium'; requires a nightly rustc (src/lib.rs uses #![feature(stdsimd)] and #![feature(test)]), version not stated |
| **Adoption** | 1.6k stars |
| **Last commit** | 2021-03-25 |
| **Links** | [repository](https://github.com/AdamNiederer/faster) · [benchmark](https://github.com/AdamNiederer/faster) |

## Verdict

The author's cargo bench on an unnamed Ivy Bridge host (nightly rustc of late 2017 to early 2018, pre-0.5 code) timed a 1024-element constant f32 map at 6,963 ns scalar versus 879 ns SIMD for target-cpu=ivybridge (about 7.9x), 7,237 vs 1,879 ns for x86-64/SSE2 (about 3.9x) and 7,195 vs 6,271 ns for the pentium polyfill build (about 1.15x), with the SIMD closure using approximate rsqrt against an exact sqrt plus division; a third-party 2018 run on an i7-5557U found the SIMD map 3.4x slower than scalar.

## Use it when

- Reading or porting old (2017-2021) Rust code that already depends on faster's simd_iter/simd_map API.
- Studying how to design an iterator-shaped SIMD API with tail padding and strided zips (stride_two..stride_nine, tuplify!).
- A pinned old nightly toolchain (community report: nightly-2020-08-27 / Rust 1.46 still builds 0.5.2) for elementwise f32/i32/u8 maps and reductions on x86.
- Kernels where an approximate rsqrt (error up to about 1e-3) is acceptable, which is where the published 8x rows come from.

## Skip it when

- Any current toolchain: issue #68 (2021) reports 0.5.2 failing to build because vektor 0.2.2 calls the removed _mm_extract_pi16, with every nightly after 2020-08-27 failing; src/lib.rs also needs #![feature(stdsimd)].
- Stable Rust or C++ projects: nightly-only crate, and from C++ it would need an FFI layer.
- Wide float vectors on AVX-without-AVX2 CPUs (Sandy/Ivy Bridge): the current code maps f32s to f32x8 only when avx2 is enabled, so those CPUs get 128-bit f32x4.
- SSE2-only builds that use ceil/floor/round: without SSE4.1 these fall back to per-lane scalar calls (issue #44).
- Binaries that must adapt to the running CPU: there is no runtime feature detection (issue #2 open); width is fixed by -C target-cpu / target-feature at build time.

## How it is fast

Static dispatch on compile-time target features to packed_simd_2 vector types plus hand-mapped x86 intrinsics through the vektor crate (_mm_rsqrt_ps, _mm_ceil_ps, _mm256_\* on AVX2), with zero-allocation iteration and vector loads/stores. Much of the published map/reduce gain also comes from the kernel itself: the SIMD closure uses the approximate rsqrt instruction (2 exact sqrt + 1 rsqrt per element) where the scalar baseline does 3 exact sqrt plus a division.

## Compared with alternatives

Among Rust siblings, pick glam or ultraviolet for vector maths types, SIMDNoise, simd-adler32 or memchr for those specific kernels, and argminmax for min/max scans; faster only makes sense if you need its generic iterator-over-slices API on an old pinned nightly. C++ users should look at EVE or the Vector Class Library instead.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | vektor 0.2.1 (x86 intrinsic bindings), packed_simd_2 0.3.4 (renamed as packed_simd); optional std feature (default) and no_std mode |
| **Minimum toolchain** | nightly Rust only (#![feature(stdsimd)], edition 2018); last toolchain reported to build 0.5.2 is nightly-2020-08-27 (Rust 1.46.0), per issue #68 |
| **Platforms** | x86/x86-64 accelerated (SSE2 baseline, SSE4.1 for rounding, 256-bit float and integer vectors only with AVX2, AVX-512 types declared); other architectures use scalar polyfills; aarch64 and wasm build problems reported in issue #47 |
| **Thread safety** | not documented (iterators borrow slices; vector types are plain values) |
| **Drop-in for the baseline** | partial — the closure body maps almost one-to-one from scalar iterator code, but the API (simd_iter with a default vector, simd_map, scalar_collect) and the vector types differ, and results can depend on vector width for impure or length-dependent closures |

## Gotchas

- README numbers are stale: the bench output names a tests:: module and was last re-benched in Dec 2017 to Feb 2018 (README commits 'Re-bench', 'Update benches'), while benches/usage.rs was created on 2018-07-17 and the 0.5 releases moved to packed_simd; the maintainer said on 2018-01-28 (issue #16) that 256-bit float support had been dropped for AVX-only targets, so the ivybridge rows do not describe the current crate.
- Independent run, issue #51 (2018-07-16, i7-5557U, rustc 1.29.0-nightly 2018-07-07): map_scalar 2,022 ns/iter versus map_simd 6,898 ns/iter, SIMD about 3.4x slower, because v.abs() silently resolved to std::simd's slower inherent abs instead of faster's trait method; without abs the rows were 558 vs 144 ns. The name clash was never resolved in the thread.
- Unequal kernels in the headline map/reduce benchmarks: SIMD uses the approximate rsqrt (documented error past 1e-3) where scalar does sqrt().recip(), and the constant -123.456 input plus ceil() hides the approximation error.
- zip_simd and zip_scalar compute different things: SIMD upcasts i32 to i64 and saturating-downcasts back to i32, the scalar path converts through f64 and returns f32, so their timings are not like for like.

## Known shortcomings

- README numbers match (map 6,963 vs 879 ns/iter, 7.9x derived) but the kernels are unequal (the SIMD path uses the approximate _mm256_rsqrt_ps while the scalar baseline does exact sqrt().recip()); some SIMD rows are slower (zip on AVX, determinant3 and nop on Pentium); no CPU model or rustc version; nightly-only (#![feature(stdsimd)], packed_simd_2). Abandoned since 2021-03-25.
- Enricher: README numbers were last re-benched December 2017 to February 2018 (pre-0.5, tests:: module) and do not describe the current crate (f32x8 needs AVX2; AVX-only Ivy Bridge maps to f32x4); an independent run in issue #51 (i7-5557U, nightly 2018-07-07) has map_simd 6,898 vs map_scalar 2,022 ns per iteration, SIMD 3.4x slower because abs() resolved to std::simd's inherent method; issue #68: the build fails after nightly-2020-08-27 (vektor 0.2.2 calls the removed _mm_extract_pi16); the zip rows compare unequal outputs (i32 vs f32). Retiered to D.

## Caveats and trade-offs

The README calls its own benchmarks 'extremely unscientific'; single host named only as Ivy Bridge, rustc nightly version unstated. Unequal kernels: the SIMD map and reduce benchmarks call faster's rsqrt, which on x86 is the approximate _mm256_rsqrt_ps/_mm_rsqrt_ps (the trait documents significant error past 1e-3), while the scalar baseline does an exact sqrt().recip(), i.e. one extra sqrt and a division per element; the ceil() in the chain hides the approximation for the constant input -123.456, so results match, but part of the 7.9x comes from cheaper math rather than SIMD width alone. The input is a constant-filled 1024-element array. Some SIMD rows are slower than scalar (zip_simd on AVX, determinant3 and nop on the pentium polyfill target). The crate never built on stable Rust: it needs nightly with #![feature(stdsimd)] and packed_simd_2; the stdsimd feature gate was later removed from nightly, so it likely does not build on current toolchains (not built here). Last commit 2021-03-25; abandoned.

Iterator-style SIMD abstraction for Rust with polyfills for CPUs lacking the target feature; depends on packed_simd_2 (nightly-era API). Not usable from C++ without FFI.

## Maintenance

Abandoned since 2021-03-25 (0.5.2) and broken on toolchains after nightly-2020-08-27 per issue #68; MPL-2.0 and readable as a design reference, but not usable in new code without reviving vektor and the stdsimd-era APIs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** The README (README.org) shows the author's cargo bench output for scalar iterators versus faster's SIMD iterators; the benchmark code is public (benches/usage.rs, map_scalar and map_simd) and RUSTFLAGS target-cpu values are given, but the rustc nightly version is unstated and the host is named only as 'ivybridge' with no CPU model, so it falls short of A. First-party, so C.
- **Retiered** C to D: Enricher (2026-10-12): the README numbers are stale (last re-benched December 2017 to February 2018 against a pre-0.5 crate whose 256-bit float paths were since dropped for AVX-only targets), the only independent run (issue #51, i7-5557U, nightly 2018-07-07) found the SIMD map 3.4x slower than scalar, and the crate no longer builds on toolchains after nightly-2020-08-27 (issue #68), so no current measurement supports the claim.
- **Verifier notes:** All quoted numbers match the README exactly. Shortcomings to record: unequal kernels (approximate rsqrt intrinsic in the SIMD path versus exact sqrt plus reciprocal in the scalar baseline), self-described unscientific single-host runs without CPU model or rustc version, some SIMD rows slower than scalar, nightly-only crate on the removed stdsimd feature and packed_simd_2, abandoned since 2021. Metadata checked: MPL-2.0, 1.6k stars, not archived, last commit 2021-03-25.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-41 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/AdamNiederer/faster>
  - <https://github.com/AdamNiederer/faster/tree/master/benches>
  - <https://github.com/AdamNiederer/faster/commits/master>
  - <https://raw.githubusercontent.com/AdamNiederer/faster/master/README.org>
  - <https://raw.githubusercontent.com/AdamNiederer/faster/master/Cargo.toml>
  - <https://raw.githubusercontent.com/AdamNiederer/faster/master/LICENSE>
  - <https://raw.githubusercontent.com/AdamNiederer/faster/master/src/lib.rs>
  - <https://raw.githubusercontent.com/AdamNiederer/faster/master/benches/usage.rs>
  - <https://raw.githubusercontent.com/AdamNiederer/faster/master/src/intrin/rsqrt.rs>
  - <https://raw.githubusercontent.com/AdamNiederer/faster/master/src/arch/x86/intrin/rsqrt.rs>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/AdamNiederer/faster/master/README.org>
  - <https://raw.githubusercontent.com/AdamNiederer/faster/master/Cargo.toml>
  - <https://raw.githubusercontent.com/AdamNiederer/faster/master/src/lib.rs>
  - <https://raw.githubusercontent.com/AdamNiederer/faster/master/benches/usage.rs>
  - <https://raw.githubusercontent.com/AdamNiederer/faster/master/src/intrin/rsqrt.rs>
  - <https://raw.githubusercontent.com/AdamNiederer/faster/master/src/arch/x86/intrin/rsqrt.rs>
  - <https://raw.githubusercontent.com/AdamNiederer/faster/master/src/arch/x86/vecs.rs>
  - <https://raw.githubusercontent.com/AdamNiederer/faster/master/src/arch/x86/intrin/round.rs>
  - <https://raw.githubusercontent.com/AdamNiederer/faster/master/src/arch/x86/intrin/abs.rs>
  - <https://raw.githubusercontent.com/AdamNiederer/faster/master/src/arch/mod.rs>
  - <https://crates.io/api/v1/crates/faster>
  - <https://github.com/AdamNiederer/faster/commits/master/README.org>
  - <https://github.com/AdamNiederer/faster/commits/master/benches/usage.rs>
  - <https://github.com/AdamNiederer/faster/issues>
  - <https://github.com/AdamNiederer/faster/issues/51>
  - <https://github.com/AdamNiederer/faster/issues/68>
  - <https://github.com/AdamNiederer/faster/issues/44>
  - <https://github.com/AdamNiederer/faster/issues/16>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/adamniederer/faster`) · [data/wave13/enrich/raw/github_com_adamniederer_faster.json](../../../data/wave13/enrich/raw/github_com_adamniederer_faster.json) (enrichment confidence 0.8)

</details>
