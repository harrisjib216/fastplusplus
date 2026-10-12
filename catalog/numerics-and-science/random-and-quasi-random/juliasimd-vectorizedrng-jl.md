# VectorizedRNG.jl (SIMD Xoshiro256++ for Julia)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Julia` · `MIT` · 🟢 active

> Julia SIMD xoshiro-style RNG with vectorized Box-Muller; about 2x Julia's old dSFMT MersenneTwister for randn! (1.5-3.4x for rand!).

| | |
|---|---|
| **Beats** | Julia Base default RNG of the time (dSFMT-based MersenneTwister, a SIMD-oriented Mersenne Twister variant) |
| **Claimed result** | Haswell AVX2 randn!: 7.235 us versus 3.744 us (about 1.9x, derived from page data); rand!: 791 ns versus 513 ns (about 1.5x, derived). AVX-512 (i7-1165G7) randn!: 1.676 us versus 854 ns (about 2.0x, derived); rand!: 549.9 ns versus 159.9 ns (about 3.4x, derived). |
| **Workload** | BenchmarkTools minimum time to fill a Vector{Float64} of 1024 elements with randn! and rand! using the default Base RNG versus local_rng() from VectorizedRNG, on an old Haswell AVX2 machine and on an AVX-512 laptop. |
| **Metric** | throughput |
| **Hardware** | 11th Gen Intel Core i7-1165G7 @ 2.80GHz (the versioninfo() printed after the AVX-512 run); the AVX2 run is only described as an 'old haswell machine' |
| **Compiler and flags** | Julia 1.6.0-DEV.1581 (2020-11-26), LLVM 11.0.0 (ORCJIT, tigerlake); JIT, no flags; benchmark snippets are in the README |
| **Adoption** | 36 stars |
| **Last commit** | 2026-05-27 |
| **Links** | [repository](https://github.com/JuliaSIMD/VectorizedRNG.jl) · [benchmark](https://raw.githubusercontent.com/JuliaSIMD/VectorizedRNG.jl/HEAD/README.md) |

## Verdict

The README's BenchmarkTools minimum times for filling a 1024-element Vector{Float64} compare Base's then-default dSFMT MersenneTwister with local_rng(): randn! 7.235 us vs 3.744 us and rand! 791 ns vs 513 ns on an unspecified AVX2 Haswell, and randn! 1.676 us vs 854 ns and rand! 549.9 ns vs 159.9 ns on an Intel i7-1165G7 (AVX-512) under Julia 1.6.0-DEV.1581 with LLVM 11. No C++ std:: baseline is involved, and Julia's current Xoshiro-based default was not measured.

## Use it when

- Julia code filling medium Float64 arrays (around 1024 elements, the size benchmarked) with normals, where the README shows 7.235 us to 3.744 us on AVX2 Haswell and 1.676 us to 854 ns on an AVX-512 i7-1165G7
- AVX-512 x86 machines, where uniform rand! went from 549.9 ns to 159.9 ns (about 3.4x, derived from page data)
- Monte Carlo kernels that need in-place scaled noise via randn!(rng, x, StaticInt(0), β, γ), i.e. x = γ·z + β without a temporary
- Statistical work where per-thread streams are enough and bit reproducibility across machines is not needed

## Skip it when

- Anything that needs a C or C++ library: this is a Julia package built on VectorizationBase.jl and SLEEFPirates.jl
- Code that relies on the documented xoshiro256++ algorithm, its period or its 2^128 stream spacing: src/xoshiro.jl drops the '+ s0' output term and rotates s3 right by 45 (a left rotation by 19, not 45), so it is a nonstandard variant and the reused xoshiro256 jump constants do not establish stream separation
- Current Julia (1.7+): the README's baseline is the old dSFMT MersenneTwister; Julia's default RNG is now a per-task Xoshiro256++ with its own SIMD bulk path (Julia Random docs, seen only via search snippets), and no comparison against it is published
- Apple M1/NEON: open issue #20 reports randn! at about 2.85 us vs 1.69 us for the default RNG (about 69% slower) and no faster rand!
- Large arrays that spill out of cache, or long-term maintenance: issue #4 argues the gain fades beyond about 2048 elements, and VectorizationBase.jl's README says it is 'looking for new maintainers, otherwise deprecated in Julia 1.11'

## How it is fast

Each thread owns XREGISTERS = 2 SIMD registers of independent xoshiro-style states, so 8 streams on AVX2 or 16 on AVX-512, spaced by the xoshiro256 2^128 jump polynomial. A bulk fill advances all lanes at once with integer shift/xor/rotate vector ops, converts bits to floats with mask tricks (vpternlog on AVX-512), and writes two vectors per loop iteration with masked tail stores. Normals come from a SIMD Box-Muller transform using Remez-fitted polynomial sin/cos and log approximations, whereas Julia's MersenneTwister randn uses a scalar ziggurat; the README credits most of the randn! gain to this.

## Compared with alternatives

Pick this only inside Julia, where it is the ready-made SIMD normal and uniform filler. From C++, simdrng gives verified lane-correct xoshiro256++ with SIMD bulk fill, and EigenRand or the normaldist-benchmark Box-Muller code cover vectorized normals; simd-rand is the Rust equivalent.

## Integration

| | |
|---|---|
| **Form** | module (Julia package, registered; version 0.2.26) |
| **Dependencies** | VectorizationBase.jl (0.19.38, 0.20.1 or 0.21), SLEEFPirates.jl 0.6.29+, UnPack.jl, Random, Distributed, Requires; optional StaticArraysCore extension |
| **Minimum toolchain** | Julia 1.6 (Project.toml compat) |
| **Platforms** | x86-64 best (AVX2, AVX-512 where it shines); aarch64 NEON runs but is slower than Base for randn! per issue #20; vector width picked by VectorizationBase at load |
| **Thread safety** | One generator per thread via local_rng(), indexed by Threads.threadid() into a block allocated for Threads.nthreads() when the package loads; a single generator must not be shared between threads, and task migration or threads added after load are not documented |
| **Drop-in for the baseline** | partial: implements Random.AbstractRNG so rand!/randn!/rand work, but you must pass local_rng() explicitly, Random.seed! does not seed it (use VectorizedRNG.seed!), and the output stream differs from Base |

## Gotchas

- Bug in the scaled in-place path: when α is passed as an ordinary number (anything other than StaticInt(0)), the main loop of samplevector! in src/api.jl line 266 uses z₁ for the second vector, so each pair of adjacent W-element chunks gets identical random draws; only the tail block uses z₂. The default rand!/randn! (α = StaticInt(0)) path is correct, and the test only checks the mean, so it does not catch this.
- Seeding is separate from Base: the generator is seeded from Base's global RNG at load time, Random.seed! has no effect, and VectorizedRNG.seed!(n) reseeds every thread's streams at once.
- Results depend on SIMD width and thread count: streams are interleaved across 8 (AVX2) or 16 (AVX-512) lanes per thread, so the same seed gives different sequences on different machines.
- The README itself reports that its BigCrush run on a 10980XE was slower than MersenneTwister's (511.5 s vs 481.8 s) and warns 'Watch out when mixing vectorized and non-vectorized code' (AVX-512 downclocking).

## Known shortcomings

- Correctness bug: not true Xoshiro256++ (output rotr23 missing +s0; state rotr45 = rotl19), so the standard jump constants are invalid and stream separation/period are unproven; claim kept because the baseline is MT, not xoshiro; Julia.
- Correctness bug (src/api.jl line 266): in samplevector!, when alpha is an ordinary number (anything except StaticInt(0)), the main loop reuses z1 for the second W-chunk, so adjacent chunks get identical draws; tests check only the mean. Nonstandard xoshiro; NEON randn! 69% slower (#20); dependency VectorizationBase deprecated for Julia 1.11 unless maintained; baseline is old dSFMT, never compared with current Julia Xoshiro. Julia, not callable from C++.

## Caveats and trade-offs

Numbers are from 2020 on a Julia 1.6 dev build. The README says Base Julia used dSFMT only up to 1.7, so the baseline no longer describes current Julia (Base now uses its own Xoshiro256++). The README itself says dSFMT 'in a few tests appears to outperform this library on AVX2 systems' for uniform numbers, and that the normal-distribution win comes mainly from a SIMD Box-Muller versus a scalar ziggurat. The AVX2 machine's CPU model is not given. Correctness: despite the 'vectorized Xoshiro256++' label, src/xoshiro.jl outputs rotate_right(s0+s3, 23) without the '+ s0' term (left commented out), and it updates s3 with rotate_right(s3, 45), which equals a left rotation by 19, not xoshiro's left rotation by 45. VectorizationBase defines rotate_right as a true right funnel shift. So the engine is a nonstandard xoshiro-like variant, and the standard xoshiro256 jump constants it uses to space streams 2^128 apart are not valid for that engine; full period and stream separation are not established. It passes SmallCrush in CI and BigCrush per the README. Baseline is not std::mt19937.

Julia-only (not usable from C++); 8 or 16 parallel xoshiro streams per thread depending on vector width, jump-ahead of 2^128 per stream; seeding is separate from Random.seed!; mixing vectorised and non-vectorised code can hurt performance.

## Maintenance

MIT-licensed and registered, but effectively in maintenance mode: the only 2026 commits (May 27) fix compat entries, the previous code change was October 2023, 8 issues are open, and its VectorizationBase.jl dependency is seeking maintainers; 36 stars.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** The README prints the full BenchmarkTools code and output for Base randn!/rand! against local_rng(). The AVX-512 run is followed by versioninfo(): Julia 1.6.0-DEV.1581, LLVM 11.0.0 ORCJIT tigerlake (default JIT optimisation) on an Intel Core i7-1165G7. That meets A, as with Octavian.jl in this wave. The Haswell AVX2 numbers lack a CPU model and are C-level on their own.
- **Verifier notes:** All eight timings match the README. The same-generator rule does not void the claim, because the baseline is a different generator (Base MersenneTwister) by design. The mislabelled generator is still a shortcoming worth recording.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/JuliaSIMD/VectorizedRNG.jl/HEAD/README.md>
  - <https://raw.githubusercontent.com/JuliaSIMD/VectorizedRNG.jl/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/JuliaSIMD/VectorizedRNG.jl/HEAD/src/xoshiro.jl>
  - <https://raw.githubusercontent.com/JuliaSIMD/VectorizedRNG.jl/HEAD/src/VectorizedRNG.jl>
  - <https://raw.githubusercontent.com/JuliaSIMD/VectorizedRNG.jl/HEAD/test/runtests.jl>
  - <https://raw.githubusercontent.com/JuliaSIMD/VectorizationBase.jl/HEAD/src/llvm_intrin/intrin_funcs.jl>
  - <https://github.com/JuliaSIMD/VectorizedRNG.jl>
  - <https://github.com/JuliaSIMD/VectorizedRNG.jl/commits/master>
- **Sources the enricher read:**
  - <https://github.com/JuliaSIMD/VectorizedRNG.jl>
  - <https://github.com/JuliaSIMD/VectorizedRNG.jl/commits/master>
  - <https://github.com/JuliaSIMD/VectorizedRNG.jl/issues?q=is%3Aissue>
  - <https://github.com/JuliaSIMD/VectorizedRNG.jl/issues/20>
  - <https://github.com/JuliaSIMD/VectorizedRNG.jl/issues/4>
  - <https://raw.githubusercontent.com/JuliaSIMD/VectorizedRNG.jl/HEAD/README.md>
  - <https://raw.githubusercontent.com/JuliaSIMD/VectorizedRNG.jl/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/JuliaSIMD/VectorizedRNG.jl/HEAD/Project.toml>
  - <https://raw.githubusercontent.com/JuliaSIMD/VectorizedRNG.jl/HEAD/src/VectorizedRNG.jl>
  - <https://raw.githubusercontent.com/JuliaSIMD/VectorizedRNG.jl/HEAD/src/xoshiro.jl>
  - <https://raw.githubusercontent.com/JuliaSIMD/VectorizedRNG.jl/HEAD/src/api.jl>
  - <https://raw.githubusercontent.com/JuliaSIMD/VectorizedRNG.jl/HEAD/src/special_approximations.jl>
  - <https://raw.githubusercontent.com/JuliaSIMD/VectorizedRNG.jl/HEAD/src/masks.jl>
  - <https://raw.githubusercontent.com/JuliaSIMD/VectorizedRNG.jl/HEAD/test/runtests.jl>
  - <https://raw.githubusercontent.com/JuliaSIMD/VectorizationBase.jl/HEAD/README.md>
  - <https://raw.githubusercontent.com/JuliaSIMD/VectorizationBase.jl/HEAD/src/llvm_intrin/intrin_funcs.jl>
  - https://github.com/JuliaLang/julia/pull/40546 (WebSearch snippet only)
  - https://docs.julialang.org/en/v1/stdlib/Random/ (WebSearch snippet only)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/juliasimd/vectorizedrng.jl`) · [data/wave8/enrich/raw/github_com_juliasimd_vectorizedrng_jl.json](../../../data/wave8/enrich/raw/github_com_juliasimd_vectorizedrng_jl.json) (enrichment confidence 0.8)

</details>
