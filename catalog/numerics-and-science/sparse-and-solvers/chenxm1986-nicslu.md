# NICSLU

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C (prebuilt libraries only)` · `Proprietary prebuilt binaries with no source: use is gated by a license key file (nicslu202110/license/nicslu.lic), and license/readme.txt says 'License for research/trial purpose only. Long-term license key file is now provided.' The README says the license has been extended to 9999-99-99.` · 🔵 finished

> Retired binary-only parallel sparse LU for SPICE circuit matrices; first-party 1.87x over KLU, 2.15x over MKL PARDISO.

| | |
|---|---|
| **Beats** | KLU (SuiteSparse) and Intel MKL PARDISO |
| **Claimed result** | NICSLU achieves 2.15X speedup over Intel MKL PARDISO and 1.87X speedup over KLU, both on geometric mean over the 182 matrices; faster than KLU on 149 of 182 cases (82%) and faster than MKL PARDISO on 134 of 182 (74%). Fewer fill-ins: KLU generates 29.6% more and PARDISO 46.1% more than NICSLU (geometric mean). Pre-analysis is slower: KLU spends 61% less pre-analysis time than NICSLU, while NICSLU spends 54% less than PARDISO. |
| **Workload** | Sparse LU solving of 182 circuit matrices (136 from real circuits, 46 from SuiteSparse); the page's performance chart is labelled normalized refactor+solving time (NICSLU = 1), with companion charts for fill-ins and pre-analysis time; all solvers use 'best configurations'. |
| **Metric** | latency |
| **Hardware** | Intel Gold 6132 CPU (core/thread count not stated); NICSLU version 201905B |
| **Compiler and flags** | Not stated in results.pdf. Prebuilt libraries in the repo are named lib_centos6_x64_gcc482_fma / _no_fma (gcc 4.8.2, CentOS 6); flags unknown. |
| **Adoption** | 52 stars |
| **Last commit** | 2026-03-22 |
| **Links** | [repository](https://github.com/chenxm1986/nicslu) · [benchmark](https://raw.githubusercontent.com/chenxm1986/nicslu/HEAD/results.pdf) |

## Verdict

The author's 2019 results.pdf compares NICSLU 201905B with KLU and Intel MKL PARDISO on an Intel Xeon Gold 6132, using refactorization plus solve time on 182 circuit matrices (136 unpublished real circuits, 46 SuiteSparse) with 'best configurations'; thread counts, versions and compilers are not stated. It reports geomean speedups of 1.87x over KLU (faster on 149 of 182) and 2.15x over PARDISO (faster on 134). The chart shows many matrices near 1x and a few huge outliers (one KLU case at 15691x) lifting the mean; the peer-reviewed TCAD 2013 paper (2.08x to 8.57x over KLU with 1-12 threads, per a search snippet) was not opened.

## Use it when

- An existing SPICE-style simulator that already integrates NICSLU, for example Dolphin Design SMASH (the README gives a special build for SMASH 7.5.x and nicslu202110 for 7.6.0, enabled with .OPTION SOLVER=NICSLU).
- Highly sparse circuit matrices refactorized thousands of times with a fixed pattern, where KLU occasionally blows up: the results chart shows KLU more than 10x slower on roughly 15 of 182 matrices (read off the chart), mostly where its fill-in is far larger.
- Older x86-64 CPUs without FMA or AVX2: NICSLU ships non-FMA builds, while its successor CKTSO refuses to run without AVX2 and FMA.
- Academic work that needs a frozen solver with a non-expiring key: the README says the license now runs to 9999-99-99, and use is free for academic purposes.
- Studying the algorithm: an older NICSLU 3.0.1 source tree (2011-2013, LGPL-2.1) is mirrored at github.com/wibraun/NICSLU, though the author's FAQ calls that version old and buggy.

## Skip it when

- New projects: the author says NICSLU is no longer updated or maintained and points to CKTSO, whose IEEE TCAD 2025 paper reports it 5.9x faster than NICSLU at 16 threads in the no-re-pivot best case (1.21x to 4.69x when both use CKTSO's ordering).
- Commercial products without a deal with the authors: it is copyrighted by NICS Lab (Tsinghua) and Xiaoming Chen, covered by three Chinese patents, free only for academic use, and needs a research/trial license key file to run.
- Solve-dominated or many-right-hand-side workloads: the user guide says only serial forward/backward solving is supported.
- Scaling to many cores: the CKTSO paper says NICSLU's factorization with pivoting gets only about 2x on 8-16 threads, and the auto-selector may run small or very sparse matrices on one thread regardless of the thread count.
- Non-circuit matrices (FEM, CFD) or non-x86 targets: orderings are minimum-degree family only (ColAMD and METIS were removed in 201905A), pre-analysis takes about 2.6x KLU's time, and the macOS/PowerPC request (issue #2, 2023) has no reply.

## How it is fast

It is a Gilbert-Peierls left-looking LU in the KLU lineage with several additions: static pivoting and scaling at analysis (Duff-Koster style permutation of large entries to the diagonal) to cut off-diagonal pivots, and six fill-reducing orderings (AMD, approximate minimum Markowitz, three approximate-minimum-operation variants and approximate minimum deficiency) run in parallel, keeping the one with the fewest predicted flops. Factorization adaptively picks a row-row, partial-supernode or full-supernode kernel by sparsity, and parallelizes over an elimination-tree dependency graph, running wide levels in parallel and narrow levels in a pipelined schedule; it also decides automatically whether a matrix is worth factorizing in parallel at all. Repeated Factorize calls use a pivoting-reduction technique, and ReFactorize reuses the previous pivot order with no pivoting, which is the fast path in converging Newton iterations.

## Compared with alternatives

Pick NICSLU over CKTSO only when you are tied to an existing NICSLU integration, need non-FMA x86-64 builds, or want the non-expiring key; otherwise CKTSO (same author, same API style) is faster and maintained. Choose Basker (open source in Trilinos, measured against KLU and PARDISO) when you need source, and GLU or CKTSO-GPU for GPU refactorization.

## Integration

| | |
|---|---|
| **Form** | shared lib (prebuilt .so / .dll; FMA and non-FMA; int32 and int64 builds) plus C headers with a C++ interface; no source for this version |
| **Dependencies** | license key file nicslu.lic beside the executable or library, or pointed to by the NICSLU_LICENSE environment variable; Linux links need -lpthread -lm -ldl (-lrt on old glibc); no OpenMP or BLAS |
| **Minimum toolchain** | C or C++ caller; Linux binaries built with gcc 4.8.2 on CentOS 6 and need a gcc-compatible compiler; x64 Windows needs Visual C++ 2005 or later |
| **Platforms** | x86-64 Linux and Windows only; FMA builds need Intel Haswell or AMD Piledriver or newer (NicsLU_Initialize returns -15 otherwise), non-FMA builds run on older x86-64 |
| **Thread safety** | The user guide says one handle cannot be used by several threads simultaneously; each handle owns a pthread / Win32 thread pool created by NicsLU_CreateThreads; concurrent use of separate handles is not documented |
| **Drop-in for the baseline** | partial — same analyze / factor / refactor / solve flow as KLU, but a different API, CSR rather than KLU's CSC by default, and a license key file to deploy |

## Gotchas

- NICSLU expects CSR; passing KLU-style CSC without MATRIX_COLUMN_\* gives wrong answers (the FAQ's 'completely wrong for any test case'), and duplicate entries are rejected with -7.
- The __NICS_INT64 macro must match the int32 or int64 library you link, or the integer argument types silently disagree.
- NicsLU_ReFactorize does no pivoting and can go unstable when values change a lot; call NicsLU_Factorize until Newton is converging. The FactorizeMatrix heuristic can misjudge extreme cases, and the guide recommends the low-level calls for DC analysis.
- Passing ax=NULL to NicsLU_Analyze disables static pivoting. The first factorization or refactorization carries one-time setup, so benchmark the second call, as the FAQ advises.

## Known shortcomings

- Tier C: results.pdf numbers (geomean 2.15x vs MKL PARDISO, 1.87x vs KLU over 182 matrices) are first-party; the license is a proprietary research/trial key file (nicslu202110/license/nicslu.lic). The TCAD 2013 paper (2.08x-8.57x vs KLU, 1-12 threads) was blocked and seen only as a snippet; retier candidate to B.
- Unmaintained; the author points to CKTSO. Serial solve only; the pivoting factorization scales only about 2x at 8-16 threads (CKTSO TCAD paper); the results.pdf geomean is lifted by a few huge KLU outliers (one at 15691x); thread counts and versions unstated; 136 of 182 matrices are private; patent-covered, academic use only. wibraun/NICSLU (LGPL-2.1, NICSLU 3.0.1 from 2011-2013) is the only copyable source, which the author's FAQ calls old and buggy with the closed version up to 3x faster.
- An LGPL-2.1-or-later source of NICSLU 3.0.1 (2011-2013) exists at wibraun/NICSLU (folded here as a duplicate); it bundles restricted HSL MC64 files and the author's FAQ calls it old and buggy, with the closed version up to 3x faster.

## Caveats and trade-offs

First-party 2019 results.pdf (NICSLU 201905B; the PDF is dated 2019-06-11). The newer nicslu202110 libraries were published afterwards and were not benchmarked there. No benchmark code and no source, so it cannot be rerun; 136 of the 182 matrices are 'real circuit cases' that the PDF does not identify as public. Compiler, flags and thread counts for every solver are unstated, and 'best configurations' is not defined. KLU is a sequential solver, so the 1.87X is likely multithreaded NICSLU against one-thread KLU. The README says NICSLU 'will no longer be updated or maintained' and points users to its successor CKTSO (already on the known list), which 'provides better performance and scalability'. The binaries need a research/trial license key file (nicslu202110/license), so this is reference only. Peer-reviewed support exists but was not opened: IEEE TCAD 2013 vol. 32 no. 2 pp. 261-274 ('NICSLU: An Adaptive Sparse Matrix Solver for Parallel Circuit Simulation'), whose abstract, seen only as a search-engine snippet (dl.acm.org, ieeexplore, researchgate and the Tsinghua lab site are egress-blocked), reports 2.08x to 8.57x geometric-mean speedups over KLU with 1-12 threads on the matrices (of 35) suited to the parallel algorithm. Linux libraries ship as lib_centos6_x64_gcc482_fma and _no_fma (gcc 4.8.2). Last commit 2026-03-22 ('Final update'), from the GitHub commits page. [retier] 2026-10-03 retier attempt: the TCAD 2013 paper (Tsinghua PDF at nicsefc.ee.tsinghua.edu.cn/nics_file/pdf/publications/2013/IEEE TCAD_64.pdf) is still egress-blocked here. A search snippet of the abstract again gives 2.08x to 8.57x geometric-mean speedups over KLU with 1-12 threads on the subset of 35 matrices suited to the parallel algorithm; machine, compiler and the exact matrix subset remain unverified.

Proprietary and binary-only: nicslu202110 holds Linux and Windows libraries (FMA and non-FMA builds), a license key file nicslu.lic, demos and docs, but no solver source. Per ug202110.pdf it is copyrighted by NICS Laboratory (Tsinghua) and Xiaoming Chen, protected by three Chinese patents, free for academic use and 'distributed for customization or research'; commercial use requires contacting the authors. The license key file is readme-marked for research/trial use and the key was extended to 9999-99-99. Author states it is no longer maintained and points to the successor CKTSO. Shared-memory multicore only.

## Maintenance

Finished: the 'Final update' commit is dated 2026-03-22, the code is unmaintained and replaced by CKTSO, and it is a proprietary, patent-covered, license-keyed binary, so treat it as a reference to call, not code to copy.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** results.pdf (first-party, NICSLU 201905B, Intel Gold 6132) states the 2.15X vs MKL PARDISO and 1.87X vs KLU geometric-mean speedups, the 149/182 and 134/182 win counts, the 29.6%/46.1% fill-in and the 61%/54% pre-analysis figures exactly as recorded. There is no benchmark code, compiler, flags or thread count, so C; the peer-reviewed IEEE TCAD 2013 paper could support B but I could not open it.
- **Verifier notes:** Every number in the record matches results.pdf. I filled in the license, which is a proprietary research/trial key-file license, so reference is right. The TCAD 2013 abstract (2.08x-8.57x geomean vs KLU, 1-12 threads, seen only as a search snippet) makes this a retier candidate to B for a session that can open IEEE/ACM.
- **Fields the verifier corrected:** `license`, `caveats`
- **Shortcomings recorded by:** verifier; same author's CKTSO doc/tcad.pdf: CKTSO 5.9x over NICSLU at 16 threads, 1.21x-4.69x with the same ordering, implying NICSLU about 2x over PARDISO there (derived from page data)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/chenxm1986/nicslu/HEAD/results.pdf>
  - <https://raw.githubusercontent.com/chenxm1986/nicslu/HEAD/README.md>
  - <https://github.com/chenxm1986/nicslu>
  - <https://github.com/chenxm1986/nicslu/commits>
  - <https://github.com/chenxm1986/nicslu/tree/master/nicslu202110>
  - <https://github.com/chenxm1986/nicslu/tree/master/nicslu202110/linux>
  - <https://github.com/chenxm1986/nicslu/tree/master/nicslu202110/license>
- **Sources the enricher read:**
  - <https://github.com/chenxm1986/nicslu>
  - <https://github.com/chenxm1986/nicslu/commits/master>
  - <https://github.com/chenxm1986/nicslu/issues?q=is%3Aissue>
  - <https://github.com/chenxm1986/nicslu/tree/master/nicslu202110>
  - <https://github.com/chenxm1986/nicslu/tree/master/nicslu202110/doc>
  - <https://github.com/chenxm1986/nicslu/tree/master/nicslu202110/include>
  - <https://github.com/chenxm1986/nicslu/tree/master/nicslu202110/demo>
  - <https://github.com/chenxm1986/nicslu/tree/master/nicslu202110/linux>
  - <https://github.com/chenxm1986/nicslu/tree/master/nicslu202110/linux/lib_centos6_x64_gcc482_fma>
  - <https://github.com/chenxm1986/nicslu/tree/master/nicslu202110/windows>
  - <https://raw.githubusercontent.com/chenxm1986/nicslu/HEAD/README.md>
  - <https://raw.githubusercontent.com/chenxm1986/nicslu/HEAD/results.pdf>
  - <https://raw.githubusercontent.com/chenxm1986/nicslu/HEAD/nicslu202110/license/readme.txt>
  - <https://raw.githubusercontent.com/chenxm1986/nicslu/HEAD/nicslu202110/doc/changelog.txt>
  - <https://raw.githubusercontent.com/chenxm1986/nicslu/HEAD/nicslu202110/doc/faq.pdf>
  - <https://raw.githubusercontent.com/chenxm1986/nicslu/HEAD/nicslu202110/doc/ug202110.pdf>
  - <https://raw.githubusercontent.com/chenxm1986/nicslu/HEAD/nicslu202110/include/nicslu.h>
  - <https://raw.githubusercontent.com/chenxm1986/nicslu/HEAD/nicslu202110/include/nics_common.h>
  - <https://raw.githubusercontent.com/chenxm1986/nicslu/HEAD/nicslu202110/include/nicslu_cpp.inl>
  - <https://raw.githubusercontent.com/chenxm1986/nicslu/HEAD/nicslu202110/demo/Makefile>
  - <https://raw.githubusercontent.com/chenxm1986/nicslu/HEAD/nicslu202110/demo/readme.txt>
  - <https://raw.githubusercontent.com/chenxm1986/cktso/master/doc/tcad.pdf>
  - <https://github.com/wibraun/NICSLU>
  - <https://github.com/wibraun/NICSLU/commits/master>
  - <https://raw.githubusercontent.com/wibraun/NICSLU/HEAD/README.md>
  - <https://raw.githubusercontent.com/wibraun/NICSLU/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/wibraun/NICSLU/HEAD/make.inc>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/chenxm1986/nicslu`) · [data/wave8/enrich/raw/github_com_chenxm1986_nicslu.json](../../../data/wave8/enrich/raw/github_com_chenxm1986_nicslu.json) (enrichment confidence 0.8)

</details>
