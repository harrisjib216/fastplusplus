# FINUFFT (with cuFINUFFT)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> CPU (and CUDA) nonuniform FFT library, types 1-3 in 1-3 dimensions, several times faster than NFFT3 and CMCL NUFFT.

| | |
|---|---|
| **Beats** | NFFT3 (Chemnitz NUFFT library, built on FFTW); docs also name CMCL NUFFT |
| **Claimed result** | docs/related.rst: NFFT 'significantly slower and/or more memory-intensive than FINUFFT'; CMCL NUFFT 'much (up to 50x even for one thread) slower'; MIRT 'slower than FINUFFT for all tolerances smaller than 10^-1'; DUCC 'in some regimes is faster than ours'; NonuniformFFTs.jl 'close to our CPU performance, and can beat it in the case of real data'. Paper abstract (SIAM J. Sci. Comput. 2019): favorable speed and memory footprint against several popular CPU libraries, especially in three dimensions. Legacy cuFINUFFT README (flatironinstitute/cufinufft): acceleration over FINUFFT of up to 10x and up to 100x faster than other established GPU NUFFT codes. |
| **Workload** | 2D type-1 (adjoint) nonuniform FFT, the example from NFFT3's simple test migrated to FINUFFT, single thread, same output to all shown digits. |
| **Metric** | throughput |
| **Hardware** | AMD 5700U laptop, single thread |
| **Adoption** | 445 stars; PyPI packages finufft and cufinufft; Python/Julia/MATLAB/Fortran bindings |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/flatironinstitute/finufft) · [benchmark](https://github.com/flatironinstitute/finufft/blob/master/docs/nfft_migr.rst) |

## Verdict

docs/nfft_migr.rst times a 2-D type-1 transform of 500,000 random points to 300 x 200 modes at tol 1e-13, single thread on an AMD 5700U laptop: NFFT3 3.5.4alpha 0.589 s versus FINUFFT 0.0787 s (7.5x), with the same output to all printed digits (compiler and flags not stated; the timing uses clock()). The peer-reviewed 2019 SIAM J. Sci. Comput. paper, seen only through a WebSearch summary because arxiv.org is blocked here, reports NFFT 3.3.2 as 3-5x slower without precomputation and 2-4x slower with it, FINUFFT at least 2x faster than every other code tested on random points except MIRT at 1-digit accuracy, and CMCL NUFFT up to 50x slower even on one thread (docs/related.rst).

## Use it when

- MRI, cryo-EM, radio-astronomy imaging, spectral analysis of unevenly sampled data or PDE solvers that need sums of exponentials at nonuniform points, where a direct O(NM) sum or NFFT3 is too slow.
- 2-D and 3-D problems with up to millions of points at tolerances from about 1e-2 to 1e-12 in double precision (about 1e-5 in single), on multicore CPUs.
- Repeated transforms with the same points: the guru or 'many' interface reuses the bin-sort and FFT plan, which the troubleshooting page says can be 10-100x faster than repeated simple calls on small problems.
- NVIDIA GPU workloads through cuFINUFFT in the same repository, whose legacy README claims up to 10x over CPU FINUFFT and up to 100x over other established GPU NUFFT codes.
- Projects that need one library with C, C++, Python, MATLAB/Octave, Fortran and Julia front ends under Apache-2.0.

## Skip it when

- Data on a regular grid: a plain FFT is faster and exact, and type 1 and type 2 are adjoints, not inverses, so you cannot undo one with the other; NFFT3 has inverse NUFFTs, sphere and rotation-group transforms that FINUFFT lacks.
- Very many tiny transforms through the simple interface, or very high thread counts: FFTW wisdom lookup costs about 0.1 ms per thread, and open issue #869 reports a 3-D grid running 50-80x slower at 96 threads than at 64 or fewer on a dual EPYC 9474F.
- Tolerances near machine precision or large 1-D N in single precision: errors cannot beat roughly N_max times machine epsilon, and requests the library judges unreachable return error 26 unless opts.allow_eps_too_small is set.
- Every regime against DUCC's own NUFFT: the project's docs say DUCC 'in some regimes is faster than ours', and NonuniformFFTs.jl is close on CPU and faster for real-valued data.
- Bitwise reproducibility across thread counts: results vary at rounding level, by up to about 1e-11 relative in double with upsampfac=1.25 at tol 1e-7 to 1e-9.

## How it is fast

Standard spread / FFT / deconvolve NUFFT, but with a cheap compactly supported kernel evaluated on the fly by Horner piecewise polynomials and SIMD (xsimd) instead of precomputed kernel tables, so no point-dependent precomputation or large RAM is needed. Points are bin-sorted for cache locality and type-1 spreading is split into load-balanced subproblems across OpenMP threads; the inner FFT is FFTW (default) or DUCC0, which exploits the block sparsity of the upsampled 2D/3D grids. The 2019 paper introduced the 'exponential of semicircle' kernel; since v2.5.0 the default is a PSWF (prolate) kernel, and upsampfac=0 picks the oversampling factor (for example 2 or 1.25) from a density-aware cost model.

## Compared with alternatives

It is the general-purpose NUFFT among the catalogued FFT entries: pick it over TRON when you need all three transform types, CPU support and arbitrary sampling rather than a GPU MRI gridding pipeline compared against gpuNUFFT. Uniform-grid FFT entries (Admiral, PocketFFT, VkFFT) and FFTW++'s padded convolutions solve a different problem and are only relevant as its inner FFT or for regularly sampled data.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | FFTW3 &gt;= 3.3.6 single and double (default) or DUCC0 (fetched and bundled by CMake), xsimd and POET header-only (fetched), OpenMP (optional, ON by default); CUDA 11.8+ for cuFINUFFT |
| **Minimum toolchain** | C++17, CMake 3.25; GCC 9+ recommended on x86-64 (GCC 8.5 can fail in xsimd with AVX-512); MSVC works on Windows |
| **Platforms** | Linux, macOS (Intel and Apple Silicon), Windows (MSVC or MinGW; Windows CI builds DUCC0 only), PowerPC64/64le cross-builds; NVIDIA GPUs via cuFINUFFT; builds default to -march=native |
| **Thread safety** | Documented: safe with DUCC0; with FFTW, safe as long as no other thread creates or destroys FFTW plans outside FINUFFT (call fftw_make_planner_thread_safe() or pass opts.fftw_lock_fun/fftw_unlock_fun); set opts.nthreads=1 when calling from inside your own parallel region. |
| **Drop-in for the baseline** | partial — the NFFT3 migration guide maps type-1 calls one to one, but coordinates must be rescaled by 2\*pi and x/y swapped (row-major vs column-major), and NFFT3's inverse and special-geometry transforms have no equivalent |

## Gotchas

- setpts keeps pointers to your nonuniform point arrays rather than copying them, so they must stay unchanged until the last execute that uses them.
- The default FFTW plan mode is FFTW_ESTIMATE; FFTW_MEASURE gives faster repeated transforms but can spend many seconds planning on the first call.
- v2.5.0 switched the default kernel to PSWF, which changes results at the tolerance level, and its kernel setup was not thread safe when plans are created concurrently (fixed in v2.5.1, #835/#838); open issue #839 reports a rare heap-corruption abort in that code path during parallel plan creation, not yet diagnosed.
- Unreleased master (v2.6.0-dev) fixes a Windows fine-grid size wraparound that silently ran transforms on a tiny grid, a clang -fassociative-math build that folded points wrongly and segfaulted, and an icpx bin-sort miscompile; build from master or a later release if you hit these configurations.

## Known shortcomings

- Tier B rests on the paper abstract seen via search (arXiv blocked here).
- v2.5.0 had a thread-safety bug in parallel plan creation (fixed 2.5.1); open #839 (rare heap corruption during parallel plan creation) and #869 (50-80x slower at 96 threads); NUFFT, a loose fit for the fft category.

## Caveats and trade-offs

The tier B rests on the peer-reviewed 2019 paper; its full text could not be opened here (arXiv and Semantic Scholar blocked), only its abstract via a search result. ahbarnett/nufft-bench says MIRT's apply step beats all others in 1-D and 2-D, while MIRT precomputation is very expensive. DUCC is faster in some regimes, and NonuniformFFTs.jl is close on CPU, beats it on real data and claims its GPU type 1 beats cuFINUFFT v2.4.1. Library comparisons date from 2018-2019; docs/performance.rst only tracks FINUFFT against its own releases. Baselines are other NUFFT codes, not FFTW, MKL or KissFFT, and the fit with the FFT category is loose.

Computes nonuniform FFTs (types 1-3, 1-3 dimensions) to a user-set tolerance, not a plain uniform FFT; uses FFTW or DUCC for the inner FFT (CMake builds); GPU library cuFINUFFT in the same repository; NFFT3 offers more transform kinds (inverse NUFFT, sphere, rotation group) that FINUFFT lacks.

## Maintenance

Very active (3,747 commits, last commit 2026-09-30, release v2.5.1 of 2026-04-08 with v2.6.0 in preparation, CI across GCC, Clang, MSVC and CUDA 11.8-13.0) and Apache-2.0, maintained by the Flatiron Institute.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** docs/related.rst compares FINUFFT against NFFT3, CMCL and MIRT and points to the peer-reviewed SIAM J. Sci. Comput. 41(5) C479-C504 (2019) paper, whose abstract (seen via a search result; arXiv itself is blocked here) reports favorable speed and memory against several popular CPU NUFFT libraries, especially in 3-D. The nufft-bench harness is public, but FINUFFT flags and CPU are not stated there, so B, not A.
- **Verifier notes:** Quotes on related.rst, the nufft-bench compiler notes and the cuFINUFFT 10x/100x line all verified; Apache-2.0, 445 stars, last commit 2026-09-30 confirmed. Mixed picture against DUCC (already filed in wave 8) and NonuniformFFTs.jl is worth recording.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** nfft_migr: 7.5x over NFFT3 3.5.4alpha (0.589 s vs 0.0787 s, 1 thread, AMD 5700U, flags unstated).
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/flatironinstitute/finufft/master/docs/related.rst>
  - <https://raw.githubusercontent.com/flatironinstitute/finufft/master/README.md>
  - <https://raw.githubusercontent.com/flatironinstitute/finufft/master/docs/performance.rst>
  - <https://raw.githubusercontent.com/flatironinstitute/cufinufft/HEAD/README.md>
  - <https://raw.githubusercontent.com/ahbarnett/nufft-bench/HEAD/README.md>
  - <https://github.com/flatironinstitute/finufft>
  - <https://github.com/flatironinstitute/finufft/commits/master>
- **Sources the enricher read:**
  - <https://github.com/flatironinstitute/finufft>
  - <https://raw.githubusercontent.com/flatironinstitute/finufft/master/README.md>
  - <https://raw.githubusercontent.com/flatironinstitute/finufft/master/docs/related.rst>
  - <https://raw.githubusercontent.com/flatironinstitute/finufft/master/docs/nfft_migr.rst>
  - <https://raw.githubusercontent.com/flatironinstitute/finufft/master/docs/performance.rst>
  - <https://raw.githubusercontent.com/flatironinstitute/finufft/master/docs/trouble.rst>
  - <https://raw.githubusercontent.com/flatironinstitute/finufft/master/docs/opts.rst>
  - <https://raw.githubusercontent.com/flatironinstitute/finufft/master/docs/install.rst>
  - <https://raw.githubusercontent.com/flatironinstitute/finufft/master/docs/c.rst>
  - <https://raw.githubusercontent.com/flatironinstitute/finufft/master/include/finufft.h>
  - <https://raw.githubusercontent.com/flatironinstitute/finufft/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/flatironinstitute/finufft/master/CHANGELOG>
  - <https://raw.githubusercontent.com/flatironinstitute/finufft/master/tutorial/migrate2d1_test.c>
  - <https://raw.githubusercontent.com/ahbarnett/nufft-bench/HEAD/README.md>
  - <https://github.com/flatironinstitute/finufft/issues>
  - <https://github.com/flatironinstitute/finufft/issues?q=is%3Aissue+is%3Aopen+label%3Abug>
  - <https://github.com/flatironinstitute/finufft/issues/839>
  - <https://github.com/flatironinstitute/finufft/issues/869>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/flatironinstitute/finufft`) · [data/wave8/enrich/raw/github_com_flatironinstitute_finufft.json](../../../data/wave8/enrich/raw/github_com_flatironinstitute_finufft.json) (enrichment confidence 0.8)

</details>
