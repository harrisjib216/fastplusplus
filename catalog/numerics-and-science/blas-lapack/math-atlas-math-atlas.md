# ATLAS

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `BSD-3-Clause` · 🔴 abandoned

> Self-tuning C BLAS with part of LAPACK that times its own kernels on the build machine; about 6-8x faster than Netlib reference BLAS.

| | |
|---|---|
| **Beats** | Netlib reference BLAS (Debian blas 1.2.20110419, lapack 3.5.0) |
| **Claimed result** | Single-threaded ATLAS 3.10.2 (Debian package) vs Netlib reference BLAS, R-benchmark-25 mean of 10 runs (chart bar labels and 'Performance gain' column in the README images): Xeon E3-1275 v5 2800x2800 cross-product 1.50 s vs 11.41 s (x7.6), 2000x2000 linear regression 0.747 s vs 5.466 s (x7.3); Xeon E5-1620 v4 cross-product 1.58 s vs 9.45 s (x6.0). Multi-threaded ATLAS dev branch 3.11.38 reaches 0.14 s (x79.3) on the E3-1275 v5 cross-product. Against in-list baselines the multi-threaded ATLAS build roughly ties: i7-4790K cross-product ATLAS (mt) 0.13 s vs OpenBLAS 0.14 s, BLIS 0.15 s, MKL 0.17 s; i5-3570 OpenBLAS 0.27 s vs ATLAS (mt) 0.28 s, MKL 0.28 s, BLIS 0.28 s. |
| **Workload** | Wall-clock time of dense matrix kernels from R-benchmark-25 run in R 3.2.4 (Microsoft R Open) linked to each BLAS, 10 runs: 2800x2800 cross-product and 2000x2000 linear regression; single-threaded ATLAS 3.10.2 (Debian package) against the Netlib reference BLAS, on Intel Xeon E3-1275 v5 and Xeon E5-1620 v4. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E3-1275 v5 and Intel Xeon E5-1620 v4 (also ten other hosts in the same repo); Debian Jessie, kernel 4.4 |
| **Compiler and flags** | Not stated. ATLAS (st) 3.10.2 and Netlib (blas 1.2.20110419, lapack 3.5.0) are Debian Jessie binary packages (libatlas3-base, libblas3/liblapack3) installed from a snapshot.debian.org 20160411 jessie-backports mirror, so the ATLAS (st) library was not auto-tuned on the test host; ATLAS (mt) 3.11.38 was built from source with '../configure --shared --with-netlib-lapack-tarfile=lapack-3.6.0.tgz' (Debian build-essential gcc/gfortran, version not stated) after patching config.c (thrchk=0) and archinfo_x86.c (adds CPU model 0x5E); CPU governor set to performance. |
| **Adoption** | 192 stars, 37 forks (GitHub mirror); last SourceForge stable release 3.10.3 dated 2016-07-28, last developer release 3.11.41 dated 2018-10-05; shipped as a Debian package |
| **Last commit** | 2019-06-11 |
| **Links** | [repository](https://github.com/math-atlas/math-atlas) · [benchmark](https://github.com/andre-wojtowicz/blas-benchmarks) |

## Verdict

The independent andre-wojtowicz/blas-benchmarks suite ran R-benchmark-25 under Microsoft R Open 3.2.4 on Debian Jessie, swapping BLAS libraries with LD_PRELOAD and reporting the mean elapsed time of 10 runs. On a Xeon E3-1275 v5, Debian's single-threaded ATLAS 3.10.2 computed a 2800x2800 crossprod in 1.50 s against 11.41 s for the Debian Netlib reference BLAS/LAPACK (7.6x) and the 2000x2000 regression in 0.747 s against 5.466 s (7.3x); on a Xeon E5-1620 v4 the crossprod took 1.58 s against 9.45 s (6.0x). Compiler and flags are not stated because both are binary packages.

## Use it when

- Replacing the unoptimised Netlib reference BLAS through the standard F77 or CBLAS ABI on a machine where you can run the tuned build yourself: the benchmark shows 6-8x on 2800x2800 SYRK-type work even with an untuned generic Debian build.
- A new or unusual architecture with no vendor-tuned or hand-tuned BLAS: the FAQ says the fully automatic search is there to give 'an adequate library on a truely new architecture'.
- You want a BSD-3-Clause BLAS with a row-major C LAPACK interface (clapack.h) for LU, Cholesky and QR solves.
- Studying or reusing empirical autotuning: the search framework and the per-architecture defaults are the reusable part.

## Skip it when

- Mainstream x86-64 or AArch64 where OpenBLAS, BLIS or MKL are available. In the same suite, single-threaded Debian ATLAS 3.10.2 took 1.50 s for the cross-product test against 0.49 s for OpenBLAS 0.2.12 and 0.14 s for MKL (both multi-threaded) on a Xeon E3-1275 v5. Multi-threaded ATLAS 3.11.38 only ties OpenBLAS, BLIS and MKL, within about 10%, on the older i7-4790K and i5-3570 hosts.
- Prebuilt distribution binaries. Debian's libatlas3-base is built without processor extensions and Debian recommends a local rebuild (README.Debian, search snippet only). The ATLAS errata adds that stable 3.10's block-factor and storage constraints 'can cut performance by around half' on modern machines compared with the developer release.
- Builds you cannot babysit. Configure aborts if it detects CPU throttling, parallel make (-j) ruins the tuning, tuning can fail with 'unable to get timings in tolerance', and open issues report a 3.10.3 tuning segfault with glibc 2.27 (#44), a failed RISC-V build (#78) and Cortex-A53 build problems (#79).
- Applications that need a runtime-adjustable thread count or use OpenMP: the maximum thread count is fixed at compile time, and the errata calls an OpenMP build of ATLAS 'a bad idea' for speed.
- Anything that needs active maintenance: no commits since 2019-06-11, and release requests #77 and #89 have no maintainer reply.

## How it is fast

Automated Empirical Optimization of Software (AEOS): at install time ATLAS times candidate GEMM kernels and searches blocking factor, register blocking, unrolling and compiler flags with a relaxed 1-D line search. Where 'architectural defaults' from earlier searches exist for the detected CPU and compiler, it uses those instead. Contributed hand-written SIMD kernels (SSE, AltiVec, 3DNow! and others) are kept when they win, Level 3 BLAS is built on the tuned GEMM, and the LAPACK subset uses recursive LU and Cholesky and a hybrid recursive-panel QR. The threaded library uses pthreads with processor affinity.

## Compared with alternatives

Siblings such as BLASFEO (small matrices), FT-BLAS, the GEMMFIP BLIS fork and Eigen are measured against OpenBLAS or MKL, while ATLAS clearly beats only the Netlib reference. Pick ATLAS only when you need a self-tuning, BSD-licensed full BLAS on hardware those libraries do not target, or when an existing build already expects libsatlas/libtatlas.

## Integration

| | |
|---|---|
| **Form** | static lib (always built) plus optional shared libs libsatlas and libtatlas (--shared); built from source with ATLAS configure/make, or as distribution packages |
| **Dependencies** | none for the C BLAS; a Fortran 77 compiler (gfortran) for the F77 interface and for full LAPACK from netlib's LAPACK tarball (--with-netlib-lapack-tarfile); pthreads for the threaded library |
| **Minimum toolchain** | ANSI/ISO C 1990 compiler (gcc by default; clang on OS X from 3.10.3 with --force-clang); gfortran optional |
| **Platforms** | x86 32/64-bit, ARM (NEON on 32-bit), IBM POWER, SPARC; Linux, OS X, AIX, SunOS, Windows through Cygwin or MinGW; RISC-V does not build (open issue #78) |
| **Thread safety** | FAQ: 'completely safe to call any ATLAS routine from a threaded code'; there are no global variables. Link the serial interface if you do your own threading. The threaded library's maximum thread count is fixed at compile time. |
| **Drop-in for the baseline** | partial: link-level drop-in for the full reference BLAS (F77 and CBLAS ABI) and, when built with netlib's LAPACK, for LAPACK; ATLAS alone provides only the LU, QR and Cholesky-related LAPACK routines |

## Gotchas

- Harness note: the 'cross-product' row times R's crossprod(a), which R evaluates with BLAS DSYRK (symcrossprod in R's array.c), not DGEMM. The 'linear regression' row is solve(crossprod(a), crossprod(a, b)) on a 2000x2000 Matrix-package dgeMatrix, a SYRK plus a symmetric solve, although the script's printed label says 3000x3000. Each figure is the mean elapsed time of 10 runs.
- Harness note: 'ATLAS (st)' is the generic Debian 3.10.2 binary, so ATLAS's install-time tuning never ran on the test hosts and the number understates a locally tuned ATLAS. 'ATLAS (mt)' 3.11.38 was built after slave-cmds.sh inserted 'thrchk=0;' into config.c, which disables ATLAS's CPU-throttling abort, and 'case 0x5E:' into archinfo_x86.c, which forces Skylake detection into an existing case. Its tuning therefore ran under whatever frequency scaling the performance governor left, and it is compared against a 2014 OpenBLAS 0.2.12 package.
- Errata performance traps: serial performance can fall off a cliff for N &gt; 1500 when the install leaves CacheEdge unset, so tune CacheEdge. Small-problem speed suffers because glibc's mmap-backed malloc makes ATLAS's per-call GEMM workspace expensive; the errata suggests MALLOC_TRIM_THRESHOLD_=-1 and MALLOC_MMAP_MAX_=0 and then re-tuning. Hyperthreads thrash the caches, so disable SMT or pass --force-tids.
- Threaded builds pin threads with processor affinity and are tuned for the configured core count, so a generic threaded library must be built (-t X) for the smallest core count of any target machine.

## Known shortcomings

- The only clear win is over Netlib reference BLAS (off-list): 7.6x on E3-1275 v5, 6.0x on E5-1620 v4. Single-threaded ATLAS is slower than multi-threaded OpenBLAS, MKL and GotoBLAS2, and the 3.5x mt lead over OpenBLAS on Skylake/Broadwell is likely an artifact of Debian's 2014 OpenBLAS 0.2.12 predating both CPUs while ATLAS was patched for CPU model 0x5E; on i7-4790K and i5-3570 ATLAS mt, OpenBLAS, BLIS and MKL are within about 10%. Debian packages, compiler and flags unstated. Stable 3.10.3 dates from 2016-07-28; last commit 2019-06-11, abandoned.
- Enricher: the 'cross-product' row is R crossprod, so DSYRK rather than DGEMM, and the regression label says 3000x3000 while the code runs 2000x2000; ATLAS(st) is the generic untuned Debian binary (understates ATLAS) while ATLAS(mt) was built with the throttle check disabled (thrchk=0) and the Skylake 0x5E patch. The errata note that stable 3.10 can lose about half its speed vs the dev release on modern CPUs; open #44 (glibc 2.27 segfault); abandoned.

## Caveats and trade-offs

The headline win is over the unoptimised Netlib reference BLAS, which is not one of the category's listed baselines (OpenBLAS, MKL, Eigen, BLIS). In the same charts single-threaded ATLAS is slower than OpenBLAS 0.2.12 (0.49 s vs 1.50 s on the E3-1275 v5 cross-product), GotoBLAS2 (0.92 s) and Intel MKL (0.14 s), but those, BLIS and ATLAS (mt) are multi-threaded builds in this suite, so the single-threaded comparison is not like-for-like (single-threaded ATLAS does beat the multi-threaded BLIS dev build on the E3-1275 v5: 1.50 s vs 1.75 s). The multi-threaded ATLAS 3.11.38 lead over OpenBLAS on the E3-1275 v5 (0.14 s vs 0.49 s) and E5-1620 v4 (0.15 s vs 0.53 s) is probably not a fair in-list win: OpenBLAS was a 2014 Debian 0.2.12 package older than both CPUs, while the ATLAS (mt) build was patched to recognise CPU model 0x5E; on the older i7-4790K and i5-3570 hosts ATLAS (mt), OpenBLAS, BLIS and MKL are within about 10% of each other. Numbers are read from bar-chart images embedded in the README (the page has no text tables; bars are means of 10 runs); compiler and flags are not stated; ATLAS (st) is the Debian package, so ATLAS's install-time tuning was not run on the host; 2016-era hardware and library versions; the suite is a small third-party repo (33 stars, Zenodo DOI) rather than a famous shootout. ATLAS's own timing pages (math-atlas.sourceforge.net/timing/) give DGEMM percent-of-peak (e.g. 89% on a 2.4 GHz Core2) without any baseline. The ATLAS papers (Whaley and Dongarra) were not reachable here. Project inactive since 2019-06-11; the last stable release is 3.10.3 (2016-07-28) and the last developer release 3.11.41 (2018-10-05).

Tunes itself empirically to the build machine (project description: 'applying empirical techniques in order to provide portable performance'); provides the BLAS API through C and Fortran77 interfaces but only some LAPACK routines.

## Maintenance

Abandoned: the last commit is 2019-06-11, the last stable release 3.10.3 (2016-07-28) and the last developer release 3.11.41 (2018-10-05), and 15 open issues, including build crashes, have no maintainer replies. It stays BSD-3-Clause, still ships in distributions, and is worth building only where no better-tuned BLAS exists.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party suite (andre-wojtowicz/blas-benchmarks, not by the ATLAS authors) with public harness code (slave-cmds.sh installs each library and LD_PRELOADs it under Rscript; benchmark-urbanek.R is R-benchmark-25, mean of 10 runs) and stated CPU models; the chart images show ATLAS (st) at 1.50 s vs Netlib 11.41 s (x7.6) and 0.747 s vs 5.466 s (x7.3) on the Xeon E3-1275 v5 and 1.58 s vs 9.45 s (x6.0) on the Xeon E5-1620 v4. Not A because compiler and flags are never stated (ATLAS st and Netlib are Debian binary packages; ATLAS mt is built with ATLAS's own configure defaults on an unstated gcc).
- **Verifier notes:** Numbers match the README chart images exactly; ATLAS is a genuine, widely shipped auto-tuned BLAS but its only clear win is over Netlib reference BLAS (baseline_in_list corrected to false). Shortcomings to record: baseline off-list (Netlib reference); single-threaded ATLAS slower than multi-threaded OpenBLAS/MKL/GotoBLAS2 in the same charts; multi-threaded ATLAS only ties OpenBLAS/MKL/BLIS on CPUs the 2014 OpenBLAS 0.2.12 package supports; compiler and flags unstated; abandoned since 2019. The record's '3.10.3 dated 2018-10-05' was the developer release 3.11.41; stable 3.10.3 is 2016-07-28.
- **Fields the verifier corrected:** `baseline_in_list`, `compiler_and_flags`, `claimed_speedup`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** README charts (verifier); enricher harness reading
- **Pages the verifier opened:**
  - <https://github.com/andre-wojtowicz/blas-benchmarks>
  - <https://raw.githubusercontent.com/andre-wojtowicz/blas-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/andre-wojtowicz/blas-benchmarks/HEAD/gen/img/img_ph_h1_b1_t1.png>
  - <https://raw.githubusercontent.com/andre-wojtowicz/blas-benchmarks/HEAD/gen/img/img_ph_h1_b1_t2.png>
  - <https://raw.githubusercontent.com/andre-wojtowicz/blas-benchmarks/HEAD/gen/img/img_ph_h2_b1_t1.png>
  - <https://raw.githubusercontent.com/andre-wojtowicz/blas-benchmarks/HEAD/gen/img/img_ph_h3_b1_t1.png>
  - <https://raw.githubusercontent.com/andre-wojtowicz/blas-benchmarks/HEAD/gen/img/img_ph_h7_b1_t1.png>
  - <https://raw.githubusercontent.com/andre-wojtowicz/blas-benchmarks/HEAD/gen/img/img_ph_h1_b2_t1.png>
  - <https://raw.githubusercontent.com/andre-wojtowicz/blas-benchmarks/HEAD/slave-cmds.sh>
  - <https://raw.githubusercontent.com/andre-wojtowicz/blas-benchmarks/HEAD/benchmark-urbanek.R>
  - <https://raw.githubusercontent.com/andre-wojtowicz/blas-benchmarks/HEAD/results.Rmd>
  - <https://github.com/math-atlas/math-atlas>
  - <https://github.com/math-atlas/math-atlas/commits>
  - <https://raw.githubusercontent.com/math-atlas/math-atlas/HEAD/LICENSE.txt>
  - <https://sourceforge.net/projects/math-atlas/files/Stable/>
  - <https://sourceforge.net/projects/math-atlas/files/Stable/3.10.3/>
  - <https://sourceforge.net/projects/math-atlas/files/Developer%20%28unstable%29/>
  - <https://math-atlas.sourceforge.net/timing/>
- **Sources the enricher read:**
  - <https://github.com/math-atlas/math-atlas>
  - <https://raw.githubusercontent.com/math-atlas/math-atlas/master/README.rst>
  - <https://raw.githubusercontent.com/math-atlas/math-atlas/HEAD/LICENSE.txt>
  - <https://github.com/math-atlas/math-atlas/issues>
  - <https://github.com/math-atlas/math-atlas/issues/44>
  - <https://github.com/math-atlas/math-atlas/issues/66>
  - <https://github.com/math-atlas/math-atlas/issues/89>
  - <https://math-atlas.sourceforge.net/atlas_install/>
  - <https://math-atlas.sourceforge.net/atlas_install/node2.html>
  - <https://math-atlas.sourceforge.net/atlas_install/node4.html>
  - <https://math-atlas.sourceforge.net/atlas_install/node5.html>
  - <https://math-atlas.sourceforge.net/atlas_install/node21.html>
  - <https://math-atlas.sourceforge.net/atlas_install/node24.html>
  - <https://math-atlas.sourceforge.net/atlas_install/node36.html>
  - <https://math-atlas.sourceforge.net/atlas_install/node42.html>
  - <https://math-atlas.sourceforge.net/atlas_install/node46.html>
  - <https://math-atlas.sourceforge.net/atlas_install/node66.html>
  - <https://math-atlas.sourceforge.net/errata.html>
  - <https://math-atlas.sourceforge.net/faq.html>
  - <https://raw.githubusercontent.com/andre-wojtowicz/blas-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/andre-wojtowicz/blas-benchmarks/HEAD/slave-cmds.sh>
  - <https://raw.githubusercontent.com/andre-wojtowicz/blas-benchmarks/HEAD/benchmark-urbanek.R>
  - <https://raw.githubusercontent.com/andre-wojtowicz/blas-benchmarks/HEAD/results.Rmd>
  - <https://raw.githubusercontent.com/wch/r-source/trunk/src/main/array.c>
  - WebSearch: Debian atlas README.Debian libatlas3-base generic build (snippet of metadata-backend.ftp-master.debian.org stable_README.Debian; host blocked)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/math-atlas/math-atlas`) · [data/wave8/enrich/raw/github_com_math_atlas_math_atlas.json](../../../data/wave8/enrich/raw/github_com_math_atlas_math_atlas.json) (enrichment confidence 0.8)

</details>
