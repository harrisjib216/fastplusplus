# GEMM_AVX2_FMA3

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `GPL-3.0` · 🔴 abandoned

> Archived 2019 AVX2/FMA3 OpenMP sgemm_/dgemm_ for very large matrices, 2-6% faster than MKL 2019u4 on an i9-9900K.

| | |
|---|---|
| **Beats** | Intel MKL 2019 update 4 |
| **Claimed result** | README: SGEMM 963-976 GFLOPS (MKL2019: 944-951), DGEMM 477-481 GFLOPS (MKL2019: 466-469) at M=N=K=20000, 8 threads, i.e. about 2-3% faster (derived from page data). Bench screenshots: DGEMM 20000 NN MKL 467.1-468.0 vs library 478.9-480.5 GFLOPS; SGEMM 45000 NN MKL 942.5-942.7 vs library 996.0-997.5 GFLOPS (about 5.8% faster, derived from page data). |
| **Workload** | Large square SGEMM/DGEMM, M=N=K=20000, 8 threads. |
| **Metric** | throughput |
| **Hardware** | Intel Core i9-9900K with AVX-offset = 6, OMP_NUM_THREADS=8 |
| **Compiler and flags** | Library: gcc -fopenmp --shared -fPIC -march=haswell -O2 (Makefile); bench harness: gcc -fopenmp with static MKL (mkl_intel_lp64, mkl_gnu_thread, mkl_core) per the comment in bench/dgemmtest.c; compiler version not stated |
| **Adoption** | 1 star (archived) |
| **Last commit** | 2019-08-27 |
| **Links** | [repository](https://github.com/wjc404/GEMM_AVX2_FMA3) · [benchmark](https://raw.githubusercontent.com/wjc404/GEMM_AVX2_FMA3/HEAD/README.md) |

## Verdict

The author ran the bundled tester on an Intel Core i9-9900K (AVX offset 6, OMP_NUM_THREADS=8). The library was built with gcc -fopenmp -march=haswell -O2 (compiler version not stated) and timed against MKL 2019 update 4 linked statically with the GNU OpenMP layer, one call each per iteration with MKL first. At M=N=K=20000 it reached SGEMM 963-976 vs 944-951 GFLOPS and DGEMM 477-481 vs 466-469 GFLOPS (about 2-3%), and SGEMM at 45000 reached about 996 vs 943 GFLOPS (about 6%, derived from page data). Results matched MKL to about 1e-11 max absolute difference.

## Use it when

- Very large single- or double-precision GEMMs (the author recommends dimensions above 2000; numbers are given for 20000 and 45000) on an AVX2/FMA3 x86-64 Linux machine, run with all physical cores
- Studying or reusing a compact (about 1,100 lines) Haswell-class GEMM with a full transpose-case driver and an assembly micro-kernel, under GPL-3.0
- Benchmarking another dgemm_/sgemm_ shared library against MKL: the bench harness dlopens any library that exports those symbols

## Skip it when

- Small or medium matrices, or tall-skinny shapes: every call does aligned_alloc of an M x 256 A panel, packs it on one thread, and splits N statically across threads, so overhead and load imbalance dominate below the large-square regime
- Code that must stay under a permissive license: it is GPL-3.0
- AVX-512 machines, AMD Zen, or anything that is not Linux/ELF: block sizes are tuned for a Coffee Lake i9-9900K, and the kernel is ELF-only AT&T assembly built with -march=haswell
- When you need the rest of BLAS, CBLAS, ILP64, complex types or input validation: use OpenBLAS, BLIS or MKL
- Production use: archived since 2019-08-27, 1 star, no tests beyond the MKL-comparison bench

## How it is fast

It is a Goto-style blocked GEMM. For each 256-deep K slice, the master thread packs the full-height panel of A into a shared 4096-byte-aligned buffer. Each thread packs its own alpha-scaled 256x256 block of B and runs a hand-written AT&T-syntax assembly micro-kernel. The kernel holds a 12x4 (double) or 24x4 (float) tile of C in 12 ymm accumulators, broadcasts B, does 3 aligned A loads per k step, issues explicit prefetcht0/prefetcht1 for upcoming A, B and C, and handles edges with vmaskmov. N is split statically across OpenMP threads, and a hand-rolled spin barrier (synproc with a \~3 us delay loop) replaces OpenMP barriers around each shared A-panel refill.

## Compared with alternatives

Pick it over cpu_gemm_opt or sgemm.c (salykova) when you need double precision and a standard Fortran dgemm_/sgemm_ entry point covering every transpose case for multi-threaded large matrices. Those two are sgemm teaching kernels measured against OpenBLAS. The author's successor GEMM_AVX2 adds per-CPU tuning headers (dgemm_tune.h, sgemm_tune.h) and claims to outperform MKL 2019u4 after tuning.

## Integration

| | |
|---|---|
| **Form** | shared lib (DGEMM.so / SGEMM.so via the Makefile) |
| **Dependencies** | OpenMP (libgomp); the bench programs need Intel MKL (VSL RNG and dgemm as reference) |
| **Minimum toolchain** | GCC with -fopenmp and C11 aligned_alloc; compiler version not documented |
| **Platforms** | x86-64 Linux with AVX2 and FMA3 (Haswell or later); tuned only on an Intel i9-9900K |
| **Thread safety** | not documented; each call allocates its own buffers, but the driver assumes the OpenMP team equals omp_get_max_threads() (see gotchas) |
| **Drop-in for the baseline** | partial: exports the Fortran LP64 sgemm_/dgemm_ symbols that MKL also exports, so code calling dgemm_ directly can link it first; there is no cblas_dgemm and no other BLAS routine |

## Gotchas

- From reading gemm_driver.c (not tested): the driver splits N into omp_get_max_threads() chunks and spin-waits in synproc until that many threads check in. If the actual team is smaller (called from inside another parallel region with nesting off, OMP_DYNAMIC=true, or a thread limit), part of C is never computed and the call would spin forever. The barrier also uses plain non-atomic int reads, which works on x86 in practice but is a data race in C11 terms.
- Pointer offsets such as LDC\*cchunks[tid] are computed in 32-bit int, so matrices with more than about 2^31 elements (beyond \~46000 x 46000) overflow. aligned_alloc results are not checked for NULL.
- No argument validation (no xerbla). With alpha=0 and beta=0, C is multiplied by 0 rather than zeroed, so NaN/Inf already in C survive, unlike reference BLAS.
- Prebuilt test binaries (sgemmtest, dgemmtest, \*_new) ship in bench/ and must be chmod +x to run; per the README the older pair links MKL 2018 and the \*_new pair MKL 2019. Build your own from bench/\*.c rather than running opaque binaries.

## Known shortcomings

- Margin only 2-6% (bench/dgemmtest.c, gcc -O2 -march=haswell, i9-9900K).
- Correctness (code read): the driver splits N by omp_get_max_threads() and spin-waits for that many threads, so a smaller OpenMP team (nested call, OMP_DYNAMIC) hangs and leaves part of C uncomputed; int offsets overflow past \~2^31 elements; alpha=0,beta=0 scales C instead of zeroing (NaN survives).

## Caveats and trade-offs

Margin is small (2-3% at n=20000, about 6% for SGEMM at n=45000 in a screenshot) and measured on one overclocked desktop CPU (i9-9900K, AVX offset 6); MKL is the GNU-threaded build (libgomp), not Intel OpenMP; compiler version not stated; prebuilt test binaries are shipped beside the sources. The bench program checks the result against MKL (max abs difference about 1e-11 for DGEMM). Repo archived on 2019-08-27. Successor repo wjc404/GEMM_AVX2 says it can 'outperform Intel MKL (2019 update 4) after tuning', and wjc404/GEMM_AVX512F says '99% MKL 1-thread performance after tuning' (not faster).

AVX2/FMA3 only, large matrices only (author recommends dims &gt; 2000), Fortran-style 32-bit-integer interface callable from C++ via sgemm_/dgemm_ symbols. Tuning headers must be edited per CPU. GPL-3.0.

## Maintenance

Archived on 2019-08-27 and GPL-3.0. It is small enough to vendor as a reference kernel, but it is a parity-plus result on one desktop CPU with known driver hazards; the author's later GEMM_AVX2 (updated 2020-03-23) and GEMM_AVX512F repos supersede it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded: benchmark source is public (bench/dgemmtest.c and bench/sgemmtest.c, which dlopen the user library and time it against statically linked MKL 2019u4, with an example gcc compile command), the library Makefile states gcc -fopenmp -march=haswell -O2, and the CPU is named (i9-9900K, AVX offset 6, 8 threads).
- **Verifier notes:** Tier raised C to A because bench source, Makefile flags and CPU model are all public; margin is only a few percent, so treat as parity-plus. Metadata verified: GPL-3.0, 1 star, archived 2019-08-27, last commit 2019-08-27; successor-repo statements in caveats were not re-checked.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/wjc404/GEMM_AVX2_FMA3>
  - <https://github.com/wjc404/GEMM_AVX2_FMA3/commits>
  - <https://github.com/wjc404/GEMM_AVX2_FMA3/tree/master/bench>
  - <https://raw.githubusercontent.com/wjc404/GEMM_AVX2_FMA3/HEAD/README.md>
  - <https://raw.githubusercontent.com/wjc404/GEMM_AVX2_FMA3/HEAD/Makefile>
  - <https://raw.githubusercontent.com/wjc404/GEMM_AVX2_FMA3/HEAD/bench/dgemmtest.c>
  - <https://raw.githubusercontent.com/wjc404/GEMM_AVX2_FMA3/HEAD/bench/dim45000_nn.png>
  - <https://raw.githubusercontent.com/wjc404/GEMM_AVX2_FMA3/HEAD/bench/example%20usage%20of%20dgemmtest_new.png>
- **Sources the enricher read:**
  - <https://github.com/wjc404/GEMM_AVX2_FMA3>
  - <https://raw.githubusercontent.com/wjc404/GEMM_AVX2_FMA3/HEAD/README.md>
  - <https://raw.githubusercontent.com/wjc404/GEMM_AVX2_FMA3/HEAD/Makefile>
  - <https://raw.githubusercontent.com/wjc404/GEMM_AVX2_FMA3/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/wjc404/GEMM_AVX2_FMA3/HEAD/bench/dgemmtest.c>
  - <https://raw.githubusercontent.com/wjc404/GEMM_AVX2_FMA3/HEAD/bench/sgemmtest.c>
  - <https://raw.githubusercontent.com/wjc404/GEMM_AVX2_FMA3/HEAD/src/gemm_driver.c>
  - <https://raw.githubusercontent.com/wjc404/GEMM_AVX2_FMA3/HEAD/src/gemm_kernel.S>
  - <https://raw.githubusercontent.com/wjc404/GEMM_AVX2_FMA3/HEAD/src/gemm_copy.c>
  - <https://raw.githubusercontent.com/wjc404/GEMM_AVX2_FMA3/HEAD/src/gemm_kernel_irreg.c>
  - <https://github.com/wjc404?tab=repositories>
  - <https://raw.githubusercontent.com/wjc404/GEMM_AVX2/HEAD/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/wjc404/gemm_avx2_fma3`) · [data/wave8/enrich/raw/github_com_wjc404_gemm_avx2_fma3.json](../../../data/wave8/enrich/raw/github_com_wjc404_gemm_avx2_fma3.json) (enrichment confidence 0.75)

</details>
