# Fortran (Intel ifort) in floatingspeed lap3dkernel: direct 1/r kernel sum

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Fortran` · `Apache-2.0` · 🟢 active

> Naive OpenMP Fortran 1/r direct-sum loop built with ifort 2019 runs 1.88x faster than the same plain loop in C++ (g++ 9 or icpc 2019).

| | |
|---|---|
| **Beats** | Plain OpenMP C++ version of the same 1/r kernel direct summation in the same repo (c++SIMD/lap3dkernel.cpp without VCL), built with g++ 9 and icpc 2019 |
| **Claimed result** | No claim by the source. lap3dkernel/README results on an Intel Xeon Gold 6128 (12 OMP threads): C++ (GCC 9) + omp 4.1 Gpair/s, C++ (icpc 2019) + omp 4.1, Fortran (GCC 9) + omp 4.0, Fortran (ifort 2019) + omp 7.7 Gpair/s, i.e. ifort Fortran is 1.88x the plain C++ (derived from page data). Hand-SIMD C++ with the VCL library gets 6.1 (g++) and 4.0 (icpc), and with a custom double rsqrt 18.3 (g++) and 12.8 (icpc), which beat the Fortran. On the i7-7700HQ laptop gfortran 7 is 1.3 vs C++ 1.1 Gpair/s. |
| **Workload** | Dense direct N-body sum of the 3D 1/r kernel from 10,000 sources to 10,000 targets in double precision, 12 OpenMP threads, throughput in Gpair/s. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Gold 6128 (2019 workstation, 3.4 GHz, AVX-512, 12 cores, 12 OMP threads) |
| **Compiler and flags** | Intel rows: icpc 2019 -fPIC -O3 -march=native -funroll-loops -mkl -qopenmp -std=c++17 and ifort 2019 -qopenmp -fPIC -O3 -march=native -funroll-loops -mkl (commented lines in lap3dkernel/run_all_tests.sh, added in commit b1c14d2 in the same change as the Xeon Gold 6128 results). GNU rows: g++ (9) -fPIC -O3 -march=native -funroll-loops -fopenmp -std=c++17 and gfortran (9) -O3 -fopenmp -funroll-loops -march=native from the same script. No -ffast-math on the GNU side; the Intel compilers use their default -fp-model fast=1. Exact Intel compiler update numbers are not given ('2019'). |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | no |
| **Adoption** | 8 stars; main author Alex Barnett; copyright Simons Foundation, Inc. |
| **Last commit** | 2026-02-03 |
| **Links** | [repository](https://github.com/ahbarnett/floatingspeed) · [benchmark](https://github.com/ahbarnett/floatingspeed/blob/master/lap3dkernel/README) |

## Verdict

lap3dkernel/README, with flags tied to the rows by commit b1c14d2: on an Intel Xeon Gold 6128 (12 cores, AVX-512, 12 OpenMP threads), the naive OpenMP Fortran lap3dpot built with ifort 2019 (-qopenmp -fPIC -O3 -march=native -funroll-loops -mkl) summed 10,000 x 10,000 double-precision 1/r pairs at 7.7 Gpair/s. The plain C++ kernel reached 4.1 Gpair/s with both g++ 9 and icpc 2019 at matching flags, so ifort is 1.88x (derived from page data). gfortran 9 reached 4.0, and hand-SIMD C++ with VCL reached 6.1 Gpair/s, or 18.3 with a custom rsqrt (both g++).

## Use it when

- You keep naive Fortran direct-summation kernels (N-body, boundary-integral or near-field FMM sums) and have the Intel Fortran toolchain: the plain triple loop with only OpenMP got 7.7 Gpair/s on a 12-core AVX-512 Xeon, above g++ with VCL hand-SIMD (6.1).
- Choosing a compiler for 1/r kernel sums: the single file is a ready-made A/B test across gfortran, ifort, g++ and icpc at identical -O3 -march=native -funroll-loops flags.
- On gfortran, the 2026 SoA plus `!$omp simd reduction(+:accum)` variant (lap3dpot_soa_simd) reached 8.1 Gpair/s on a Ryzen 5700U, matching C++ with VCL (8.1), without intrinsics.
- As a reference implementation when porting a direct-sum kernel: one short subroutine, Apache-2.0.

## Skip it when

- When you want the fastest kernel: hand-vectorised C++ with VCL and a custom double rsqrt reached 18.3 Gpair/s with g++ on the same Xeon, 2.4x the ifort Fortran.
- With gfortran on the naive kernel: no win (4.0 against 4.1 Gpair/s on the Xeon, 1.3 against 1.1 on the i7-7700HQ laptop). The 1.88x needs ifort 2019, the Classic compiler, which the verified record says Intel has discontinued. Its successor, ifx, was not measured.
- When bit-for-bit reproducible sums matter: ifort's default fp-model fast=1 is value-unsafe and allows reordering (Intel docs, search snippet only), and the README prints no accuracy check for the ifort row.
- As a reason to move a C++ code base to Fortran: the plain C++ kernel was not tuned. A local accumulator, __restrict or `#pragma omp simd reduction` is the C++ counterpart of the Fortran changes that gave 2.5x to 3.5x in the 2026 variants (that change was not measured in C++).
- On CPUs other than the three tested x86 machines; the ifort comparison exists only for the AVX-512 Xeon Gold 6128.

## How it is fast

The source documents no mechanism; what follows comes from reading the code. Both plain kernels add each source's contribution straight into the output element (pot(i) in Fortran, pot[t] in C++), which makes a loop-carried floating-point sum through memory. Fortran's rule that dummy arguments do not alias lets the compiler keep that sum in a register. ifort's default value-unsafe fp-model fast=1 also lets it reorder the sum, so the source loop can be vectorised. g++ and gfortran at -O3 without -ffast-math must add in order, and the C++ pot pointer has no __restrict. Supporting evidence: gfortran ties g++ (4.0 against 4.1 Gpair/s), and a 2026 variant that only moves the sum into a local scalar (lap3dpot_accum) takes gfortran from 2.3 to 5.9 Gpair/s on a Ryzen 5700U (comment in lap3dpottest.f90).

## Compared with alternatives

Use this entry when the question is which compiler to use for a multithreaded direct-sum kernel. It is the only Fortran sibling where the win comes from one vendor compiler (ifort) beating both g++ and icpc at identical flags, and the same table shows the hand-SIMD C++ ceiling. For gfortran-only evidence of Fortran beating C, the plb2 matmul (about 6% on M1) and fortran-lang poisson2d siblings are the better references.

## Integration

| | |
|---|---|
| **Form** | source-drop (single Fortran 90 file; the kernel is the subroutine lap3dpot) |
| **Dependencies** | OpenMP. At HEAD the test program also calls rsqrtps_nr4 and rsqrtps_block1024 from lap3dkernel/fortran/rsqrtps.c (x86 SSE/AVX intrinsics), which must be compiled and linked; lap3dpot itself needs nothing else. |
| **Minimum toolchain** | Fortran 90 compiler with OpenMP for lap3dpot. The HEAD test program uses iso_c_binding/bind(C) (Fortran 2003) and `!$omp simd` (OpenMP 4.0). Measured with ifort 2019, gfortran 9, g++ 9 and icpc 2019 (update numbers not given). |
| **Platforms** | Measured on x86-64 only: Xeon Gold 6128 (AVX-512), i7-7700HQ and Ryzen 5700U (AVX2). lap3dpot is portable Fortran; rsqrtps.c needs x86 intrinsics. |
| **Thread safety** | lap3dpot is an OpenMP-parallel loop over targets that writes only pot(i). Its pi variable is initialised in its declaration, which implies SAVE, but it is never modified. Calling it from several threads at once with distinct pot arrays should be safe, but this is not documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- Reproduction trap at HEAD: since the January-February 2026 commits (b179191, 3219b82), lap3dpottest.f90 calls rsqrtps_nr4 and rsqrtps_block1024, which are defined only in rsqrtps.c. Neither run_all_tests.sh nor fortran/compileandtest.sh compiles or links rsqrtps.o, so the scripted Fortran build should fail to link (read from the code; not compiled here). Build as the header of lap3dpottest.f90 says (gcc -O3 -march=native -c rsqrtps.c; gfortran ... rsqrtps.o), or check out commit b1c14d2, whose single-kernel lap3dpottest.f90 produced the 2020 Xeon rows.
- The two sides were not run identically. At the measured commit b1c14d2 the C++ main used ntest = 5 and the Fortran ntest = 20, although both normalise to pairs per second. The Fortran timer includes start-up of the program's first OpenMP region, while the C++ plain kernels run after four VCL tests have warmed the thread pool. The inputs come from different generators (drand48 against random_number), and the Fortran adds a 1/(4 pi) factor, so the printed checksums cannot be compared across languages. The README does not say which plain C++ kernel the '4.1' row is. In issue #2, target-outer (1.18-1.68 Gpair/s) beats source-outer (0.70-0.84), so the row is probably target-outer.
- Each row is one figure, and the timings are noisy. In issue #2, four runs on a Dell Precision 7530 gave 2.64-4.13 Gpair/s for the same C++ VCL kernel, and the 2020 Fortran header asks 'why is run time so variable, compared to other language versions??'. The 1.88x gap is larger than that spread, but the 4.0 against 4.1 tie is not a meaningful difference.
- The 2026 soa+rsqrt Fortran variants are only accurate to single precision. r2 is rounded to float before _mm_rsqrt_ps, and the double Newton steps converge to 1/sqrt(float(r2)); the program prints the relative difference. They are also slower than soa+simd (3.39 and 7.25 against 8.10 Gpair/s, file comments).

## Known shortcomings

- Win with ifort only (gfortran 4.0 ties g++ 4.1); the hand-SIMD C++ row (18.3) beats Fortran; mechanism inferred (Fortran no-alias semantics plus Intel fp-model fast), not stated by the source; Xeon Gold 6128 rows and icpc/ifort lines added in commit b1c14d2 with the same flags.
- Both plain kernels sum into pot through memory and are untuned; a gfortran local-accumulator variant reaches 2.3 to 5.9 Gpair/s, so the equivalent C++ fix would likely close the gap (not measured in C++). At the measured commit b1c14d2 C++ used ntest=5 against Fortran's 20; issue #2 reports run-to-run noise of 2.64-4.13. HEAD's run_all_tests.sh and compileandtest.sh do not link rsqrtps.c, so the Fortran build should fail as checked in (not compiled); the 2026 soa plus rsqrt variants are only single-precision accurate.

## Caveats and trade-offs

The source makes no Fortran-beats-C++ claim. The 1.88x ratio (7.7 vs 4.1 Gpair/s) is derived from the README table. The README notes say 'Clearly C++ w/ VCL beats others by 2x, and nearly 4x w/ custom rsqrt' (laptop section). The gap appears only with ifort: gfortran (4.0) ties g++ (4.1). Hand-vectorised C++ with VCL beats the Fortran: 6.1 (g++) and 18.3 Gpair/s (g++ with custom double rsqrt). Compared with icpc at identical flags, ifort is still 1.88x faster (derived from page data). Intel compiler versions are given only as '2019', and Intel has since discontinued ifort, so reproducing the result needs a legacy toolchain. One machine, 12 OMP threads, one reported figure per row (20 repetitions inside each run). The C++ README row does not say which plain kernel it reports (target-outer or source-outer loop). The kernels differ slightly in work: the Fortran stores coordinates as an array of structs x(3,n) and multiplies by an extra 1/(4 pi) prefactor, while the C++ uses separate X/Y/Z arrays. Neither plain version is tuned. The plain C++ kernel accumulates into pot[t] through plain pointers with no __restrict, which a C++ programmer can add. The SoA/SIMD Fortran variants added in 2026 reach 8.1 Gpair/s on a Ryzen 5700U, the same as C++ with VCL (8.1). The README results section is unfinished ('... (to finish)'). [retier] Both plain kernels sum into pot through memory and are untuned; a gfortran local-accumulator variant reaches 2.3 to 5.9 Gpair/s, so the equivalent C++ fix would likely close the gap (not measured in C++). At the measured commit C++ used ntest=5 against Fortran's 20; issue #2 reports run-to-run noise of 2.64-4.13. HEAD's scripts do not link rsqrtps.c, so the Fortran build should fail as checked in; the 2026 soa plus rsqrt variants are only single-precision accurate.

The ifort row needs the proprietary Intel Fortran compiler (2019 version); gfortran matches plain C++.

## Maintenance

The repo is a small personal benchmark (Apache-2.0, Simons Foundation, 8 stars, 41 commits, last commit 2026-02-03, 3 open issues), not a maintained library. The kernel is trivially copyable, but the headline result needs the legacy ifort 2019 compiler. At HEAD the scripted Fortran build no longer links (rsqrtps.c is missing from the scripts), so reproduce from commit b1c14d2.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgrade C to A: benchmark code is public (lap3dkernel/c++SIMD/lap3dkernel.cpp and lap3dkernel/fortran/lap3dpottest.f90), compilers (GCC 9, icpc 2019, ifort 2019), flags and CPU model (Xeon Gold 6128) are all stated, and the flags are tied to the numbers: commit b1c14d2 (2020-03-12) added the Xeon Gold 6128 rows to lap3dkernel/README together with the icpc/ifort lines in run_all_tests.sh, which use identical -fPIC -O3 -march=native -funroll-loops -mkl -qopenmp flags. README rows 4.1 (g++ and icpc), 4.0 (gfortran) and 7.7 (ifort) Gpair/s match the record.
- **Verifier notes:** Real entry with accurate numbers. I upgraded the tier to A because commit b1c14d2 ties the Intel flags to the Xeon Gold 6128 rows. Main shortcomings for the decision record: the win appears only with ifort and not with gfortran (gfortran ties g++); hand-SIMD C++ (VCL, custom rsqrt) beats the Fortran by up to 2.4x; the source makes no claim and gives no mechanism (why_faster above is an inference); ifort is discontinued.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-61 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/ahbarnett/floatingspeed>
  - <https://github.com/ahbarnett/floatingspeed/blob/master/lap3dkernel/README>
  - <https://raw.githubusercontent.com/ahbarnett/floatingspeed/HEAD/lap3dkernel/README>
  - <https://raw.githubusercontent.com/ahbarnett/floatingspeed/HEAD/README.md>
  - <https://raw.githubusercontent.com/ahbarnett/floatingspeed/HEAD/lap3dkernel/run_all_tests.sh>
  - <https://raw.githubusercontent.com/ahbarnett/floatingspeed/HEAD/lap3dkernel/c++SIMD/lap3dkernel.cpp>
  - <https://raw.githubusercontent.com/ahbarnett/floatingspeed/HEAD/lap3dkernel/fortran/lap3dpottest.f90>
  - <https://raw.githubusercontent.com/ahbarnett/floatingspeed/HEAD/LICENSE>
  - <https://github.com/ahbarnett/floatingspeed/commits/master>
  - <https://github.com/ahbarnett/floatingspeed/commits/master/lap3dkernel/README>
  - <https://github.com/ahbarnett/floatingspeed/commits/master/lap3dkernel/run_all_tests.sh>
  - <https://github.com/ahbarnett/floatingspeed/commit/b1c14d2c59aaa4dc34c78fba658815677dadb8e2>
  - <https://github.com/ahbarnett/floatingspeed/commit/master>
- **Sources the enricher read:**
  - <https://github.com/ahbarnett/floatingspeed>
  - <https://github.com/ahbarnett/floatingspeed/issues>
  - <https://github.com/ahbarnett/floatingspeed/issues/2>
  - <https://github.com/ahbarnett/floatingspeed/tree/master/lap3dkernel/fortran>
  - <https://github.com/ahbarnett/floatingspeed/commits/master/lap3dkernel>
  - <https://raw.githubusercontent.com/ahbarnett/floatingspeed/HEAD/README.md>
  - <https://raw.githubusercontent.com/ahbarnett/floatingspeed/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ahbarnett/floatingspeed/HEAD/lap3dkernel/README>
  - <https://raw.githubusercontent.com/ahbarnett/floatingspeed/HEAD/lap3dkernel/run_all_tests.sh>
  - <https://raw.githubusercontent.com/ahbarnett/floatingspeed/HEAD/lap3dkernel/c++SIMD/lap3dkernel.cpp>
  - <https://raw.githubusercontent.com/ahbarnett/floatingspeed/HEAD/lap3dkernel/fortran/lap3dpottest.f90>
  - <https://raw.githubusercontent.com/ahbarnett/floatingspeed/HEAD/lap3dkernel/fortran/lap3dpottest_accum.f90>
  - <https://raw.githubusercontent.com/ahbarnett/floatingspeed/HEAD/lap3dkernel/fortran/compileandtest.sh>
  - <https://raw.githubusercontent.com/ahbarnett/floatingspeed/HEAD/lap3dkernel/fortran/rsqrtps.c>
  - <https://raw.githubusercontent.com/ahbarnett/floatingspeed/b1c14d2c59aaa4dc34c78fba658815677dadb8e2/lap3dkernel/fortran/lap3dpottest.f90>
  - <https://raw.githubusercontent.com/ahbarnett/floatingspeed/b1c14d2c59aaa4dc34c78fba658815677dadb8e2/lap3dkernel/c++SIMD/lap3dkernel.cpp>
  - <https://raw.githubusercontent.com/ahbarnett/floatingspeed/b1c14d2c59aaa4dc34c78fba658815677dadb8e2/lap3dkernel/run_all_tests.sh>
  - <https://raw.githubusercontent.com/ahbarnett/floatingspeed/b1c14d2c59aaa4dc34c78fba658815677dadb8e2/lap3dkernel/README>
  - https://www.intel.com/content/www/us/en/docs/fortran-compiler/developer-guide-reference/2024-1/floating-point-optimizations.html (blocked: DNS lookup failed; WebSearch snippet of Intel fp-model docs used instead)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:fortran/ahbarnett/floatingspeed#lap3dkernel`) · [data/wave14/enrich/raw/lang_fortran_ahbarnett_floatingspeed_lap3dkernel.json](../../../data/wave14/enrich/raw/lang_fortran_ahbarnett_floatingspeed_lap3dkernel.json) (enrichment confidence 0.75)

</details>
