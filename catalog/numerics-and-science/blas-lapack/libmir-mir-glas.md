# Mir GLAS

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `D` · `BSL-1.0` · 🔴 abandoned

> D-written single-threaded BLAS GEMM that beat OpenBLAS 0.2.18 by 10-15% in 2016; abandoned since 2018.

| | |
|---|---|
| **Beats** | OpenBLAS (also Eigen, Apple Accelerate; equal to Intel MKL on average) |
| **Claimed result** | Blog conclusion: 'Mir GLAS is significantly faster than OpenBLAS and Apple Accelerate for virtually all benchmarks and parameters, two times faster than Eigen and Apple Accelerate for complex matrix multiplication. Mir GLAS average performance equals to Intel MKL.' From the chart data (_includes/bench_charts_1.html, GFLOPS for m=n=k from 10 to 2000, single thread), median Mir/OpenBLAS ratios are 1.15x sgemm, 1.13x dgemm, 1.12x cgemm, 1.10x zgemm, with Mir ahead at 22-23 of 23 sizes; at N=2000 sgemm 85.9 vs 75.8 GFLOPS (1.13x) and dgemm 42.0 vs 40.3 (1.04x). Versus Eigen the medians are 1.06-1.07x for real and 1.91-1.96x for complex types; versus Accelerate 1.12x real and 3.3x complex; versus MKL about 1.00-1.01x (MKL slightly ahead on dgemm at N&gt;=500, 0.97x median). All ratios derived from page data. |
| **Workload** | GEMM (single-threaded) on a 2.2 GHz Core i7-4770HQ, Mir GLAS 0.18.0 vs OpenBLAS 0.2.18, as described in the author's 2016 blog post. |
| **Metric** | throughput |
| **Hardware** | 2.2 GHz Core i7 (i7-4770HQ, Haswell), 6 MB L3, 16 GB DDR3L-1600, MacBookPro11,2, OS X 10.11.6, single thread |
| **Compiler and flags** | LDC (version not stated in the post; README requires LDC &gt;= 1.1.0 beta 6); GLAS build flags not stated in the post (README manual build uses dub --build=target-native --compiler=ldmd2); Eigen built with CMake Release -DEIGEN_TEST_AVX=ON -DEIGEN_TEST_FMA=ON; OPENBLAS_NUM_THREADS=1, VECLIB_MAXIMUM_THREADS=1, MKL_NUM_THREADS=1 |
| **Adoption** | 102 stars, 8 forks, 190 commits |
| **Last commit** | 2022-08-19 |
| **Links** | [repository](https://github.com/libmir/mir-glas) · [benchmark](https://raw.githubusercontent.com/libmir/blog/HEAD/_posts/2016-09-23-glas-gemm-benchmark.md) |

## Verdict

The author's 2016 single-thread benchmark on a 2.2 GHz i7-4770HQ MacBook Pro (Mir GLAS 0.18.0 built with LDC, version and flags unstated) against OpenBLAS 0.2.18, Eigen 3.3-rc1, MKL 2017.0.098 and Accelerate for m=n=k from 10 to 2000 gives median Mir/OpenBLAS ratios of 1.15x sgemm, 1.13x dgemm, 1.12x cgemm and 1.10x zgemm; the margin is largest at n &lt;= 100 (median about 1.4x for real types) and shrinks to about 1.03x for dgemm at n &gt;= 500, and MKL is roughly equal (ratios derived from page data). The benchmark source (libmir/mir benchmarks/glas/gemm_report.d) is gone, and the numbers predate the LLVM 4 slowdown reported in issue #18.

## Use it when

- Reading or porting a compact, assembler-free generic GEMM design (one kernel for real and complex types, a per-ISA register-blocking table) as a reference.
- Single-threaded GEMM on small square matrices (n &lt;= 100) on an Intel Haswell-class CPU, where the 2016 data show the largest margin over OpenBLAS 0.2.18 (median about 1.4x for sgemm and dgemm).
- Single-threaded complex GEMM where the alternative is Eigen 3.3 or Apple Accelerate: the 2016 data show about 1.9x over Eigen and about 3.3x over Accelerate for cgemm and zgemm.
- D projects already pinned to an old LDC and mir-algorithm 0.x that want a dependency-light BLAS with an ndslice interface.

## Skip it when

- Any multithreaded workload: multithreading is an unchecked item in the README, while OpenBLAS and MKL scale across cores.
- Current toolchains: the README warns of open issue #18, a 2x GEMM slowdown when built with LLVM 4.x-5.x versus 3.9.1, and the build prints a 'PERFORMANCE NOTE: LLVM &gt;=4.0 has a bug in register renaming' and falls back to a smaller kernel. Issue #29 (open since June 2018) says a release is needed for mir-algorithm &gt; 0.9.0, and issue #22 reports dub failing to build it with its dependencies.
- AMD CPUs: open issue #20 (April 2017) reports it slower than OpenBLAS and ACML for DGEMM on an AMD machine, with no maintainer reply.
- Large double-precision GEMM where Intel MKL is available: in the author's own data MKL is ahead on dgemm and zgemm at every size from about 500 to 2000.
- Code needing a full BLAS: TRSM, TRMM, SYRK, SYR2K, HERK and all Level 2 routines are missing, so LAPACK cannot sit on top of it alone.

## How it is fast

It is a Goto-style packed GEMM: A and B are packed into contiguous panels, and a register-blocked micro-kernel accumulates an mr x nr tile of C using LLVM vector types, without assembler. One generic kernel serves float, double and both complex types; the register-blocking shape comes from a small per-ISA configuration (x87, SSE2, AVX/AVX2, AVX-512F) chosen at compile time with __traits(targetHasFeature). Block sizes kc and mc are computed at runtime from the L1 and last-level cache sizes reported by mir-cpuid. The author also argues that the kernels are not unrolled, so they put less pressure on the instruction cache.

## Compared with alternatives

Rarely: Laser is the closest sibling (same era, also stale, but multithreaded and at parity with modern OpenBLAS), and BLASFEO is the maintained choice for small matrices. Pick Mir GLAS only to study a generic, assembler-free GEMM kernel design or for single-threaded complex GEMM in an old D toolchain.

## Integration

| | |
|---|---|
| **Form** | static lib (built with dub and LDC; a dynamic configuration exists in dub.json but the README lists shared-library support as unfinished) |
| **Dependencies** | mir-cpuid (link order -lmir-glas -lmir-cpuid); mir-algorithm for the D headers; Netlib CBLAS if you want the CBLAS interface |
| **Minimum toolchain** | LDC &gt;= 1.1.0 beta 6 (README); built with ldmd2, -betterC and -mcpu=native for the target-native build; works with C99 callers via include/glas/\*.h. Builds with current LDC releases are not documented. |
| **Platforms** | x86 and x86-64 (register configurations for x87, SSE2, AVX/AVX2, AVX-512F); POSIX and Windows memory back-ends; other targets need a mir-cpuid port and a new configuration |
| **Thread safety** | Not documented, and not safe from code reading: glas_init and the GEMM blocking routine use process-global __gshared state, including one shared pack buffer that each call reuses or reallocates, so concurrent calls from several threads race on it. |
| **Drop-in for the baseline** | partial: it exports the Fortran BLAS symbols for gemm, symm, hemm and Level 1 only; CBLAS needs Netlib's CBLAS wrapper, and every other BLAS routine is absent |

## Gotchas

- The ISA kernel is fixed at compile time (__traits(targetHasFeature), -mcpu=native in the target-native build), so a library built on an AVX-512 machine is not safe to ship to older CPUs, and there is no runtime dispatch.
- The C header include/glas/ndslice.h declares glas_zaxpy and _glas_zaxpy with a float _Complex alpha, while the D implementation takes cdouble; C or C++ callers of zaxpy through that header pass alpha with the wrong type.
- The README ticks 'CI testing with Netlib's BLAS test suite', but in .travis.yml the test.sh step that runs the Netlib CBLAS tests is commented out; CI only builds the gemm and hemm examples.
- Call glas_release() to free the shared pack buffer; otherwise it stays allocated at its largest size for the life of the process.

## Known shortcomings

- Claim not reproducible: open issue #18 reports about 2x slower with LLVM 4+; benchmark source 404; blog ratios derived from its chart data; D language.
- Thread-safety bug: the pack buffer is a process-global __gshared buffer reused by every call, so concurrent GEMM calls race. C header bug: include/glas/ndslice.h declares glas_zaxpy alpha as float _Complex while the D code takes cdouble (ABI mismatch, wrong results for C callers). README ticks Netlib test CI but test.sh is commented out in .travis.yml. ISA fixed at compile time (-mcpu=native); build breakage in #22, #29. Gain over OpenBLAS 0.2.18 is mostly at n&lt;=100 (\~1.4x), only \~1.03x for dgemm at n&gt;=500 (derived from page data).

## Caveats and trade-offs

Numbers are first-party, from 2016, single-threaded only (GLAS has no multithreading), against OpenBLAS 0.2.18 and Eigen 3.3-rc1 on one Haswell laptop. The linked benchmark source is gone (404), and the LDC version and flags are not stated. Claim likely not reproducible with current compilers: the README points to open issue #18 ('2 x slower with LLVM 4.X - 5.X', opened by the author 2017-03-30), which reports the GEMM micro-kernel running about twice as slow when built with LLVM 4.0 than with LLVM 3.9.1. GitHub issue #20 ('[AMD] mir-glas is slower than OpenBLAS for DGEMM', 2017-04-01, no maintainer reply) reports it slower than OpenBLAS on an AMD machine. Only GEMM, SYMM, HEMM and Level 1 are implemented. Last real code commits are from 2018, README-only edit in 2022. The rendered post is at blog.mir.dlang.io (blocked from this container); its Jekyll source and chart data are in github.com/libmir/blog.

C library written in D with BLAS API (CBLAS via Netlib CBLAS) and a GLAS API based on mir-algorithm ndslice; links against mir-cpuid; usable from C++ as a C library. Only Level 3 gemm was completed.

## Maintenance

Abandoned: the last code change was in mid-2018 and the last commit a README edit in August 2022; Boost-licensed and small, but it needs an old LDC/LLVM to reproduce the published speed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party 2016 blog post (read from its source in the libmir/blog repo) gives per-size single-threaded GFLOPS for Mir GLAS 0.18.0, OpenBLAS 0.2.18, Eigen 3.3-rc1, MKL 2017.0.098 and Accelerate on an i7-4770HQ, but the LDC version and build flags are not stated and the linked benchmark source (libmir/mir benchmarks/glas/gemm_report.d) now returns 404, so C.
- **Verifier notes:** The blog page itself was blocked, but its source and chart data in the libmir/blog repo were read first-hand, replacing the search-snippet-based claim; quoted conclusions and hardware match the record. Boost license (LICENSE_1_0.txt), 102 stars, last commit 2022-08-19 confirmed (abandoned).
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/libmir/mir-glas/HEAD/README.md>
  - <https://raw.githubusercontent.com/libmir/mir-glas/HEAD/LICENSE_1_0.txt>
  - <https://raw.githubusercontent.com/libmir/blog/HEAD/_posts/2016-09-23-glas-gemm-benchmark.md>
  - <https://raw.githubusercontent.com/libmir/blog/HEAD/_includes/bench_charts_1.html>
  - <https://github.com/libmir/mir-glas>
  - <https://github.com/libmir/mir-glas/commits>
  - <https://github.com/libmir/mir-glas/issues/20>
  - <https://github.com/libmir/mir-glas/issues/18>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/libmir/mir-glas/HEAD/README.md>
  - <https://raw.githubusercontent.com/libmir/mir-glas/HEAD/dub.json>
  - <https://raw.githubusercontent.com/libmir/mir-glas/HEAD/.travis.yml>
  - <https://raw.githubusercontent.com/libmir/mir-glas/HEAD/test.sh>
  - <https://raw.githubusercontent.com/libmir/mir-glas/HEAD/LICENSE_1_0.txt>
  - <https://raw.githubusercontent.com/libmir/mir-glas/HEAD/source/glas/internal/config.d>
  - <https://raw.githubusercontent.com/libmir/mir-glas/HEAD/source/glas/internal/gemm.d>
  - <https://raw.githubusercontent.com/libmir/mir-glas/HEAD/source/glas/internal/blocking.d>
  - <https://raw.githubusercontent.com/libmir/mir-glas/HEAD/source/glas/internal/memory.d>
  - <https://raw.githubusercontent.com/libmir/mir-glas/HEAD/source/glas/precompiled/context.d>
  - <https://raw.githubusercontent.com/libmir/mir-glas/HEAD/source/glas/ndslice.d>
  - <https://raw.githubusercontent.com/libmir/mir-glas/HEAD/include/glas/ndslice.h>
  - <https://raw.githubusercontent.com/libmir/mir-glas/HEAD/include/glas/fortran.h>
  - <https://raw.githubusercontent.com/libmir/mir-glas/HEAD/bench/gemm_report.d>
  - <https://raw.githubusercontent.com/libmir/blog/HEAD/_posts/2016-09-23-glas-gemm-benchmark.md>
  - <https://raw.githubusercontent.com/libmir/blog/HEAD/_includes/bench_charts_1.html>
  - <https://github.com/libmir/mir-glas>
  - <https://github.com/libmir/mir-glas/commits/master>
  - <https://github.com/libmir/mir-glas/issues?q=is%3Aissue>
  - <https://github.com/libmir/mir-glas/issues/18>
  - <https://github.com/libmir/mir-glas/issues/20>
  - <https://github.com/libmir/mir-glas/issues/31>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/libmir/mir-glas`) · [data/wave8/enrich/raw/github_com_libmir_mir_glas.json](../../../data/wave8/enrich/raw/github_com_libmir_mir_glas.json) (enrichment confidence 0.75)

</details>
