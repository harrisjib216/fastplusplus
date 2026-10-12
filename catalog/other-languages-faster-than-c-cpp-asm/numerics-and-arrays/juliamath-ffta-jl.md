# FFTA.jl (pure Julia FFT) vs FFTW.jl on small static vectors

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Julia` · `MIT` · 🟢 active

> Generic pure-Julia FFT for any element type; its only speed claim over FFTW is a 2021 one-shot N=64 snippet that no longer reproduces.

| | |
|---|---|
| **Beats** | FFTW (C library) through FFTW.jl fft(x) |
| **Claimed result** | N=64 SVector: FFTA.fft 698.611 ns (8 allocations, 2.11 KiB) vs FFTW.fft 5.433 us (34 allocations, 4.70 KiB), about 7.8x (derived from page data); the README itself calls the example cherry-picked. |
| **Workload** | One @btime of fft on a 64-element StaticArrays SVector of Float64, FFTA.fft vs FFTW.fft, as shown in the FFTA.jl README. |
| **Metric** | latency |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | README: carrying Julia's type specialisation (generic code that works on small StaticArrays without heap workspace) into the FFT; no further mechanism given. |
| **Adoption** | 76 stars |
| **Last commit** | 2026-09-01 |
| **Links** | [repository](https://github.com/JuliaMath/FFTA.jl) · [benchmark](https://github.com/JuliaMath/FFTA.jl) |

## Verdict

The README shows one BenchmarkTools pair from FFTA v0.2.2 (2021): fft on a 64-element StaticArrays SVector of Float64 took 698.611 ns in FFTA and 5.433 us in FFTW.jl, both as one-shot calls that plan on every invocation, with no CPU, Julia version or FFTW build stated. A 2026 rerun on current versions (issue #119) found both at about 4.9 us, probably FFTW in both calls, and planned FFTW at 422 ns; a contributor's planned comparison (issue #130) has FFTA 2.2x to 11.8x slower than FFTW by geomean across size classes.

## Use it when

- FFTs over element types FFTW cannot handle: Complex{BigFloat} for high precision, Symbolics variables to derive a symbolic transform, or SizedArray/SVector containers that should keep their type.
- Small transforms where a pure-Julia, MIT-licensed dependency with no binary library matters more than speed.
- Code that must stay generic over the number type (the README asks only that one(T) and the relevant convert methods exist).
- Power-of-two sizes when calling the internal FFTA.fft_pow2_radix4! with preallocated MVector output and SVector input, which the maintainer suggested in issue #119 as the fastest route for small sizes.

## Skip it when

- Anywhere FFTW applies with a reused plan: issue #130 measured planned FFTA at a geomean 2.6x slower for powers of two, 7.3x for smooth sizes, 5.8x for primes, 5.2x for 2D and up to 11.8x for 2D rfft (aarch64 Neoverse-N1, Julia 1.12.6, FFTW 3.3.11 single-threaded); the README itself says to use FFTW.jl for performance.
- In a session that also loads FFTW: FFTA.plan_fft and FFTA.fft dispatch to FFTW's more specific methods for ordinary ComplexF64 arrays and return FFTW plans (open issue #66), so you may not be running FFTA at all.
- Large prime or prime-heavy sizes: Bluestein scratch and the chirp are rebuilt on every execution (n = 1009 costs about 23 us of setup per call in issue #130).
- Float32 work at large n where accuracy matters: issue #118 (open, reported by stevengj) found error growing nearly O(n) because of the twiddle recurrence; the June 2026 Singleton-recurrence change targets this, but the issue is still open.
- 3D or higher real-input transforms (plan_rfft throws 'only supports 1D and 2D FFTs') and multithreaded transforms (no threading).

## How it is fast

Planning builds a call graph that factors N: radix-4/radix-2 recursion for powers of two, radix-3 for powers of three, mixed-radix Cooley-Tukey with N1 chosen near sqrt(N) for composites, an O(N^2) DFT for primes below 73 and Bluestein's chirp-z convolution above that. Twiddles are generated on the fly with Singleton's trigonometric recurrence instead of stored tables, and the code is generic Julia that specialises on the element and array type. The README attributes its one speed win to that specialisation carrying into small StaticArrays; with planned execution a contributor measured FFTA as slower than FFTW in every size class (issue #130).

## Compared with alternatives

No catalogued sibling is an FFT; other pure-Julia entries such as Bessels.jl, Gaius.jl and TriangularSolve.jl cover special functions and dense linear algebra. Choose FFTA over its FFTW baseline only for generic element types (BigFloat, symbolic) or a binary-free MIT dependency, not for speed.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | AbstractFFTs, Reexport, Primes, MuladdMacro, DocStringExtensions, plus the LinearAlgebra and Random standard libraries |
| **Minimum toolchain** | Julia 1.6.7 per Project.toml (issue #110 warns some FFTs may fail on older Julia versions) |
| **Platforms** | any platform Julia runs on (pure Julia, no binary artifacts) |
| **Thread safety** | not documented; from the source, a plan's CallGraph holds mutable workspace vectors that composite-size kernels write into, so one plan should not be executed from several threads at once |
| **Drop-in for the baseline** | partial — same AbstractFFTs API (fft, bfft, rfft, plan_fft) as FFTW.jl, but no FFTW flags or wisdom, no multithreading, real transforms only up to 2D, and loading both packages makes FFTW's methods win dispatch |

## Gotchas

- The catalogued benchmark is stale and the README snippet now times FFTW against itself. The 698.611 ns vs 5.433 us lines first appear in the v0.2.2 README (September 2021), when FFTA exported its own fft that ran directly on the SVector. Since v0.2.3 FFTA.fft is AbstractFFTs.fft, and with FFTW loaded in the same session (as in the snippet's `import FFTA, FFTW`) FFTW's plan_fft method wins for the converted ComplexF64 vector (issue #66). Issue #119 (April 2026, Julia 1.12.4, FFTA 0.3.1, FFTW 1.10.0) reproduced 4.922 us for FFTA.fft and 4.945 us for FFTW.fft, against 422 ns for a reused FFTW plan on a plain Vector; the maintainer agreed the README result is from 'a now-really-old version of FFTA' and that the comparison may be FFTW against itself. No valid current measurement shows FFTA faster than FFTW.
- Even the original 2021 numbers compared one-shot calls: fft(x) builds a plan on every call, so the 7.8x mostly measured FFTW planning plus SVector-to-Array conversion (34 allocations), not transform speed.
- The repo's benchmark suite runs FFTA and FFTW in separate Julia processes to avoid the dispatch clash, but it times fft(\$x) and rfft(\$x) with a fresh plan per call, and its results exist only as CI artifacts and a github.io report, not in the repo.
- Twiddle factors come from a recurrence whose inner step is wrapped in @fastmath, and the README's 'N in {1,2}' limit is out of date for complex transforms (any set of dimensions now) but still true for rfft.

## Known shortcomings

- One cherry-picked README timing at N=64; FFTW plans per call through the AbstractFFTs one-shot path, so it times planning rather than the transform; no reused-plan run, no CPU or versions.
- Claim invalid and not faster: the README's 698.611 ns vs 5.433 us snippet dates from v0.2.2 (2021); since v0.2.3 FFTA.fft is AbstractFFTs.fft, and with FFTW loaded FFTW's plan_fft wins dispatch (#66 open), so the snippet now times FFTW against itself. Issue #119's rerun: 4.922 vs 4.945 us, planned FFTW 422 ns, and the maintainer concedes the snippet is obsolete. Issue #130 planned runs: FFTA is 2.2-11.8x slower than FFTW (geomean; Neoverse-N1, Julia 1.12.6, FFTW 3.3.11). Also #118 Float32 twiddle error about O(n), and Bluestein setup on every call.

## Caveats and trade-offs

Single cherry-picked README snippet (the author says so), no CPU, Julia version, FFTW_jll build or flags. Both calls go through AbstractFFTs' one-shot path, fft(x, region) = (y = to1(x); plan_fft(y, region) \* y), so a plan is built on every call; for FFTW that means the FFTW planner runs per call on a copy of the SVector (complexfloat copies it into a ComplexF64 Array), so the 7.8x mostly measures planning and conversion overhead, not transform speed. FFTW with a reused plan is not compared, and the README itself sends users wanting performance to FFTW.jl. The repo's benchmark/ suite (separate Julia environments, fft(\$x) with a fresh plan per call, sizes up to 32768 and primes to 20000) commits no results; reports are CI artifacts kept 30 days and a docs page on github.io. Not a general speedup claim and not a Julia-versus-C codegen result. [retier] The 698.611 ns vs 5.433 us snippet dates from v0.2.2 (2021); since v0.2.3 FFTA.fft is AbstractFFTs.fft and with FFTW loaded FFTW's plan_fft wins dispatch (#66 open), so the snippet now times FFTW against itself. Issue #119's rerun: 4.922 vs 4.945 us with planned FFTW at 422 ns, and the maintainer concedes the snippet is obsolete. Issue #130 planned runs: FFTA 2.2-11.8x slower than FFTW (geomean; Neoverse-N1, Julia 1.12.6, FFTW 3.3.11). #118: Float32 twiddle error about O(n); Bluestein setup on every call.

Pure Julia and generic over element types (BigFloat, symbolic, StaticArrays), only 1D and 2D; the README itself says to use FFTW.jl for more performance.

## Maintenance

Maintained by the JuliaMath org (recent commits are the Singleton-recurrence accuracy work and CI bumps; v0.3.1 is the latest registered release) and MIT-licensed, but its only speed claim is a 2021 one-shot snippet the maintainer concedes is obsolete; current measurements show it slower than FFTW, so treat it as a generic-type FFT, not a faster one.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** The only numbers are one first-party @btime pair in the README (698.611 ns vs 5.433 us for N=64 SVector), with no CPU, Julia version or FFTW build stated; the repo's benchmark/ suite has no committed results (its report lives in 30-day CI artifacts and the github.io docs, not reachable here), so C.
- **Retiered** C to D: Enricher: the README snippet dates from v0.2.2 and now times FFTW against itself (FFTA.fft dispatches to FFTW's plan_fft when FFTW is loaded, #66), the maintainer concedes it is obsolete, and planned runs in issue #130 put FFTA 2.2-11.8x slower than FFTW; claim invalid and not faster: C to D.
- **Verifier notes:** Keep at C with shortcoming 'single cherry-picked one-shot timing at N=64 where FFTW's per-call planning dominates; no reused-plan comparison, no methodology'. Numbers match the README exactly; metadata checked (76 stars, MIT, last commit 2026-09-01, JuliaMath org, not a fork). Close to the crippled-baseline line (FFTW used without plan reuse), but both sides use the same one-shot API, so C rather than D.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-100 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/JuliaMath/FFTA.jl>
  - <https://raw.githubusercontent.com/JuliaMath/FFTA.jl/HEAD/README.md>
  - <https://github.com/JuliaMath/FFTA.jl/tree/main/benchmark>
  - <https://github.com/JuliaMath/FFTA.jl/commits/main>
  - <https://github.com/JuliaMath/FFTA.jl/tree/main/docs/src>
  - <https://raw.githubusercontent.com/JuliaMath/FFTA.jl/HEAD/docs/src/benchmarks.md>
  - <https://raw.githubusercontent.com/JuliaMath/FFTA.jl/HEAD/benchmark/fftw_env/bench_fftw.jl>
  - <https://raw.githubusercontent.com/JuliaMath/FFTA.jl/HEAD/src/FFTA.jl>
  - <https://raw.githubusercontent.com/JuliaMath/AbstractFFTs.jl/HEAD/src/definitions.jl>
- **Sources the enricher read:**
  - <https://github.com/JuliaMath/FFTA.jl>
  - <https://raw.githubusercontent.com/JuliaMath/FFTA.jl/HEAD/README.md>
  - <https://raw.githubusercontent.com/JuliaMath/FFTA.jl/HEAD/Project.toml>
  - <https://raw.githubusercontent.com/JuliaMath/FFTA.jl/HEAD/src/FFTA.jl>
  - <https://raw.githubusercontent.com/JuliaMath/FFTA.jl/HEAD/src/plan.jl>
  - <https://raw.githubusercontent.com/JuliaMath/FFTA.jl/HEAD/src/algos.jl>
  - <https://raw.githubusercontent.com/JuliaMath/FFTA.jl/HEAD/src/callgraph.jl>
  - <https://raw.githubusercontent.com/JuliaMath/FFTA.jl/HEAD/src/singleton_twiddle.jl>
  - <https://raw.githubusercontent.com/JuliaMath/FFTA.jl/HEAD/docs/src/benchmarks.md>
  - <https://raw.githubusercontent.com/JuliaMath/FFTA.jl/HEAD/benchmark/fftw_env/bench_fftw.jl>
  - <https://raw.githubusercontent.com/JuliaMath/FFTA.jl/v0.1.0/README.md>
  - <https://raw.githubusercontent.com/JuliaMath/FFTA.jl/v0.2.0/README.md>
  - <https://raw.githubusercontent.com/JuliaMath/FFTA.jl/v0.2.0/Project.toml>
  - <https://raw.githubusercontent.com/JuliaMath/FFTA.jl/v0.2.1/README.md>
  - <https://raw.githubusercontent.com/JuliaMath/FFTA.jl/v0.2.2/README.md>
  - <https://raw.githubusercontent.com/JuliaMath/FFTA.jl/v0.2.2/src/FFTA.jl>
  - <https://raw.githubusercontent.com/JuliaMath/FFTA.jl/v0.2.3/README.md>
  - <https://github.com/JuliaMath/FFTA.jl/issues?q=is%3Aissue>
  - <https://github.com/JuliaMath/FFTA.jl/issues/119>
  - <https://github.com/JuliaMath/FFTA.jl/issues/118>
  - <https://github.com/JuliaMath/FFTA.jl/issues/130>
  - <https://github.com/JuliaMath/FFTA.jl/issues/66>
  - <https://github.com/JuliaMath/FFTA.jl/commits/main>
  - <https://github.com/JuliaMath/FFTA.jl/commits/main/README.md>
  - <https://raw.githubusercontent.com/JuliaRegistries/General/master/F/FFTA/Versions.toml>
  - <https://raw.githubusercontent.com/JuliaRegistries/General/master/F/FFTA/Compat.toml>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/juliamath/ffta.jl`) · [data/wave14/enrich/raw/github_com_juliamath_ffta_jl.json](../../../data/wave14/enrich/raw/github_com_juliamath_ffta_jl.json) (enrichment confidence 0.8)

</details>
