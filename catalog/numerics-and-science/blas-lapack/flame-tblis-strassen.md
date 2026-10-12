# tblis-strassen (Strassen's Algorithm for Tensor Contraction)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `BSD-3-Clause` · 🔴 abandoned

> Research code on 2016-era TBLIS: tensor contractions via one- or two-level Strassen, up to 1.3x over regular TBLIS.

| | |
|---|---|
| **Beats** | TBLIS regular tensor-contraction routine (Strassen level L=0 in the same code); TBLIS is itself the state-of-the-art non-BLAS contraction library |
| **Claimed result** | README: 'achieving up to 1.3x speedup'. |
| **Workload** | Synthetic tensor contractions and the Tensor Contraction Benchmark (TCCG 'tcb' set) on single-core, multicore and distributed-memory systems, using Strassen's algorithm inside a transposition-free contraction. |
| **Metric** | throughput |
| **Hardware** | Maverick supercomputer at TACC (artifact.pdf; CPU model not stated on any opened page) |
| **Compiler and flags** | icc/icpc 15.0.3 with the GCC 4.9.3 standard library for single-node runs, mpicc/mpicxx from mvapich2 2.1 for distributed runs; configure --disable-shared --enable-config=sandybridge (artifact.pdf, README); other compiler flags not stated |
| **Adoption** | 15 stars |
| **Last commit** | 2017-07-07 |
| **Links** | [repository](https://github.com/flame/tblis-strassen) · [benchmark](https://github.com/flame/tblis-strassen) |

## Verdict

The authors' peer-reviewed SISC 2018 paper (README abstract) reports up to 1.3x effective GFLOPS over the same code's regular TBLIS contraction (L=0), measured on synthetic contractions and the TCCG benchmark on single-core, multicore and distributed runs. Those runs used icc 15.0.3, the Sandy Bridge AVX double-precision kernels and TACC Maverick (CPU model not stated). Per-case numbers are in the paper, which was not opened, so only the 'up to' figure is confirmed.

## Use it when

- Research or reproduction of the SISC 2018 Strassen-for-tensor-contraction results on an x86 machine with AVX.
- Very large double-precision contractions with big free and contracted dimensions (the square sweep runs 256 to 20480), where 1-2 Strassen levels can beat a conventional GEMM-based contraction.
- As a reference implementation of the Block-Scatter-Matrix plus fused-Strassen-packing technique for porting into a modern TBLIS or BLIS build.
- Distributed-memory contraction experiments on a SLURM cluster, using the bundled dist/ scripts as a starting point.

## Skip it when

- Production code: no commits since 2017-07-07, and it fails to compile with GCC 10.3 (open issue #1, 'B is not a constant expression' in stra_matrify.hpp).
- Single precision or complex data: optimized Strassen micro-kernels exist only for double (bli_dstra_asm_8x4 and its two- and four-output variants) in the sandybridge config. The float and complex Strassen slots are left empty.
- Modern CPUs with AVX2/AVX-512: the documented build is --enable-config=sandybridge (AVX, 8x4 double kernel), so FMA hardware is not used by the Strassen path.
- Small or skinny contractions: Strassen's extra additions only pay off at large sizes. The paper reports gains of at most 1.3x.
- Code that needs bit-for-bit agreement with a conventional contraction: Strassen reorders the floating-point arithmetic, and the driver reports a norm-2 error against the regular TBLIS result.

## How it is fast

It uses the Block-Scatter-Matrix layout to treat a tensor contraction as a GEMM on general-stride storage, so Strassen's 7-multiply recursion runs on the tensors in place, with no explicit permutation and no extra workspace (README). It adapts the authors' earlier BLIS-based Strassen-for-GEMM implementation (linked in the README): operand sums are folded into packing, and the default 'ABC' variant uses dedicated AVX micro-kernels (bli_dstra_asm_8x4 plus 'two' and 'four' variants) that write several C sub-blocks in one pass. 'AB' and 'Naive' variants are included for comparison. Each Strassen level does 7 block multiplies instead of 8, which is where the up-to-1.3x gain at large sizes comes from.

## Compared with alternatives

Pick it over TBLIS (MatthewsResearchGroup/tblis) only when you are studying or porting Strassen for tensor contraction: TBLIS is the maintained, multi-architecture code base but has no Strassen path. For plain matrices, fmm-gen (also from the FLAME group) and fast-matmul (Benson and Ballard) cover a wider family of fast algorithms against a conventional GEMM or MKL.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | A 2016-era TBLIS with BLIS-derived kernels in the tree, and TCI threading (tci.h). Build needs autotools (autoreconf). OpenMP runtime for the driver (omp_get_wtime, OMP_NUM_THREADS/KMP_AFFINITY). Optional BLAS, hwloc and memkind are detected by configure. mvapich2 2.1 and SLURM for the distributed experiments. |
| **Minimum toolchain** | C99 and C++11. Authors used icc/icpc 15.0.3 with the GCC 4.9.3 standard library. GCC 10.3 is reported to fail (issue #1). |
| **Platforms** | x86-64 with AVX (artifact: 'x86-64 processor that supports AVX instructions'), Linux or macOS. Strassen kernels only in the sandybridge config. |
| **Thread safety** | not documented. The Strassen variant (ABC/AB/Naive) is picked through the process-global tblis::internal::impl, so concurrent callers cannot use different variants safely. Parallelism comes from TCI with BLIS_\*_NT and OpenMP environment variables. |
| **Drop-in for the baseline** | partial — stra_mult has the same signature as the bundled TBLIS mult, but that is the 2016 TBLIS API, not current MatthewsResearchGroup/tblis, so moving to this code base means replacing TBLIS. |

## Gotchas

- Only 1 or 2 Strassen levels: stra_mult and stra_mult_2level. The driver prints 'More than 2-level is not supported' for L&gt;2.
- Variant selection is a global setting (tblis::internal::impl = BLIS_BASED / STRA_AB / STRA_NAIVE), not a function argument.
- The bin/\*_run_\*.sh scripts write results with plain 'tee', not 'tee -a', so each line overwrites the .m result file. Capture stdout instead.
- The timing harness allocates two 100M-double cache-flush buffers (about 1.7 GB) on every timed call and reports best-of-niter (default 3) effective GFLOPS = 2mnk/time.

## Known shortcomings

- 'Up to 1.3x' is vs TBLIS L=0 (its own base); built on a 2016-era TBLIS snapshot with a Sandy Bridge config only; abandoned 2017.
- Does not build on GCC 10.3 (issue #1 open since 2023-11); optimized Strassen micro-kernels exist only for double on Sandy Bridge AVX; bench scripts use tee without -a, so result files get overwritten.

## Caveats and trade-offs

The 1.3x is a best case ('up to') from the authors' own runs, measured against the same code with Strassen turned off (L=0 runs the regular TBLIS contraction). Per-case numbers, the CPU model and the speedups on the Tensor Contraction Benchmark are in the SISC paper, which could not be opened (arxiv.org 1704.03092 and the publisher are egress-blocked). The code appears to be built on a 2016-era TBLIS code base: the LICENSE is TBLIS's BSD-3-Clause, copyright Devin Matthews 2015-2016. Build instructions configure only the Sandy Bridge AVX kernels, and the distributed scripts assume TACC Maverick SLURM queues. There have been no commits since 2017-07-07. This is a research artifact, not a maintained library; for production use the current TBLIS (MatthewsResearchGroup/tblis) is the maintained code base, but it has no Strassen path.

Research code built on a copy of TBLIS and BLIS; test_strassen driver and tcb_run_\*.sh scripts; build and run steps are described in artifact.pdf in the repo. Strassen adds extra additions and workspace use, and only pays off for large enough contractions.

## Maintenance

Abandoned research artifact (last commit 2017-07-07, one open build-failure issue). BSD-3-Clause (TBLIS's license, copyright Devin Matthews), so copyable, but expect to patch it for modern compilers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C. The README abstract's 'up to 1.3x speedup' over the regular TBLIS contraction is the paper's claim, and the paper is confirmed as peer-reviewed: SIAM J. Sci. Comput. 40(3) C305-C326, 2018, DOI 10.1137/17M1135578, cited on the tblis-rs README. Not A: artifact.pdf names icc 15.0.3 and 'Maverick supercomputer at TACC' but no CPU model and no compiler flags beyond --enable-config=sandybridge, although the benchmark scripts (bin/\*_run_1core.sh, tcb.txt) are public.
- **Verifier notes:** The claim matches the README verbatim. Peer review was confirmed through the full SISC citation on the restgroup/tblis-rs README (not the publisher page), so the tier was raised from C to B. Metadata was checked on github.com: BSD-3-Clause, 15 stars, 6 forks, not a fork, last commit 2017-07-07 (abandoned).
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/flame/tblis-strassen>
  - <https://github.com/flame/tblis-strassen/commits>
  - <https://raw.githubusercontent.com/flame/tblis-strassen/HEAD/README.md>
  - <https://raw.githubusercontent.com/flame/tblis-strassen/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/flame/tblis-strassen/HEAD/artifact.pdf>
  - <https://github.com/restgroup/tblis-rs>
  - <https://raw.githubusercontent.com/restgroup/tblis-rs/HEAD/readme.md>
- **Sources the enricher read:**
  - <https://github.com/flame/tblis-strassen>
  - <https://github.com/flame/tblis-strassen/issues?q=is%3Aissue>
  - <https://github.com/flame/tblis-strassen/issues/1>
  - <https://github.com/flame/tblis-strassen/tree/master/src>
  - <https://github.com/flame/tblis-strassen/tree/master/src/stra_iface>
  - <https://github.com/flame/tblis-strassen/tree/master/src/stra_iface/3t>
  - <https://raw.githubusercontent.com/flame/tblis-strassen/HEAD/README.md>
  - <https://raw.githubusercontent.com/flame/tblis-strassen/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/flame/tblis-strassen/HEAD/artifact.pdf>
  - <https://raw.githubusercontent.com/flame/tblis-strassen/HEAD/version>
  - <https://raw.githubusercontent.com/flame/tblis-strassen/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/flame/tblis-strassen/HEAD/Makefile.am>
  - <https://raw.githubusercontent.com/flame/tblis-strassen/HEAD/src/tblis.h>
  - <https://raw.githubusercontent.com/flame/tblis-strassen/HEAD/src/stra_iface/3t/stra_mult.h>
  - <https://raw.githubusercontent.com/flame/tblis-strassen/HEAD/src/stra_iface/3t/stra_mult_2level.h>
  - <https://raw.githubusercontent.com/flame/tblis-strassen/HEAD/src/stra_iface/3m/stra_mult.h>
  - <https://raw.githubusercontent.com/flame/tblis-strassen/HEAD/src/configs/sandybridge/config.hpp>
  - <https://raw.githubusercontent.com/flame/tblis-strassen/HEAD/src/util/thread.h>
  - <https://raw.githubusercontent.com/flame/tblis-strassen/HEAD/test/test_strassen.cxx>
  - <https://raw.githubusercontent.com/flame/tblis-strassen/HEAD/bin/square_run_1core.sh>
  - <https://raw.githubusercontent.com/flame/tblis-strassen/HEAD/bin/tcb_run_1core.sh>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/flame/tblis-strassen`) · [data/wave8/enrich/raw/github_com_flame_tblis_strassen.json](../../../data/wave8/enrich/raw/github_com_flame_tblis_strassen.json) (enrichment confidence 0.75)

</details>
