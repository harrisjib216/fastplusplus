# cpu_gemm_opt

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Single-core AVX2 SGEMM study (BLIS-style 6x16 asm kernel, per-size tuned blocking) about 4-9% ahead of OpenBLAS 0.3.4.

| | |
|---|---|
| **Beats** | OpenBLAS 0.3.4 sgemm (README: 'most of the size exceed openblas(0.3.4)'; the driver times cblas_sgemm from the OpenBLAS it links) |
| **Claimed result** | 78.31 GFLOPS (96.38% of peak) vs 75.11 for the OpenBLAS reference column at 960^3; 78.12 vs 73.65 at 1920^3; 78.20 vs 73.41 at 3264^3; 78.62 vs 72.70 at 9120^3; 75.79 vs 68.14 at 192^3; 60.13 vs 43.05 at 48^3. About 4-9% faster at every size from 960 up (derived from page data). Slower than the reference at 144^3 (55.85 vs 64.26). |
| **Workload** | Single-core row-major SGEMM, square sizes 48 to 9120, alpha=beta=1, hand-written AVX2 6x16 micro-kernel with per-size tuned block parameters, hyperthreading off; OpenBLAS also limited to one thread and the process pinned to one CPU. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Gold 6142, one core at 2600 MHz, hyperthreading off, theoretical 81.25 GFLOPS (AVX2 FMA) |
| **Compiler and flags** | clang++ 7.0.0, -pthread -std=c++11 -Wall -O3 -m64 -mfma -msse -msse2 (src/build.sh) |
| **Adoption** | 75 stars |
| **Last commit** | 2019-04-15 |
| **Links** | [repository](https://github.com/carlushuang/cpu_gemm_opt) · [benchmark](https://github.com/carlushuang/cpu_gemm_opt) |

## Verdict

On one 2.6 GHz core of an Intel Xeon Gold 6142 (hyperthreading off), built with clang++ 7.0.0 -O3 -mfma, the README's row-major SGEMM sweep shows the tuned 6x16 kernel at about 77-79 GFLOPS from 960^3 to 9120^3 against 72-75 GFLOPS for single-threaded OpenBLAS 0.3.4 cblas_sgemm (78.31 vs 75.11 at 960^3, 78.62 vs 72.70 at 9120^3), about 4-9% faster; it also leads at most small sizes (60.13 vs 43.05 at 48^3) but loses at 144^3. The OpenBLAS build target was not stated, and its column stays below the 81.25 AVX2 figure the driver uses as peak, so it was probably not running AVX-512 kernels (inference from page data).

## Use it when

- Learning how a cache- and TLB-aware SGEMM is built on AVX2/FMA, with the derivation of the blocking constraints written out in a PDF
- Single-threaded row-major SGEMM experiments on an Intel Skylake-SP-class core (the author used a Xeon Gold 6142 at 2.6 GHz with hyperthreading off) for square sizes from about 192 to 9120, where the README table shows it ahead of OpenBLAS 0.3.4
- A starting point for your own per-machine tuned micro-kernel, since the tuner and the parameter database format are included

## Skip it when

- Any general BLAS use: column-major input and every transpose combination are unimplemented stubs, and there is no DGEMM or complex type
- Matrices whose M is not a multiple of 6 or N not a multiple of 16: the 6x16 assembly kernel ignores the edge-tile sizes passed to it (its assert is commented out), so edge tiles read and write past the matrix
- Multi-threaded workloads: it is single-core only, and the README states it beats OpenBLAS with OpenBLAS also limited to one thread
- AVX-512 machines where peak matters: the kernel uses 256-bit AVX2 even on the AVX-512-capable Gold 6142, so a library with AVX-512 kernels can be faster
- Small sizes such as 144^3, where OpenBLAS was faster in the README table (55.85 vs 64.26 GFLOPS), or sizes not in the tuned database, which fall back to default blocking

## How it is fast

It follows the Goto/van de Geijn loop nest: A is packed into mr x kc column panels (with alpha folded in) and B into kc x nr row panels in page-aligned buffers, C is scaled by beta once, and a 6x16 AT&T inline-assembly micro-kernel keeps 12 YMM accumulators, broadcasts A with vbroadcastss, issues vfmadd231ps, unrolls k by 4 and prefetches the next A and B panels. Blocking sizes are chosen so the panels fit L1, L2, L3 and the L1D TLB (the driver prints these checks), and a tuner stores the best mc/nc/kc per problem size in sgemm_tuned.db, which the benchmark then loads.

## Compared with alternatives

Pick it over sgemm.c (salykova) or matmul-cpu when you want the blocking derivation (cache and TLB constraints) spelled out and a per-size tuner; GEMM_AVX2_FMA3 targets multi-threaded AVX2 and is measured against MKL, and BLASFEO is the better choice for small matrices.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | A CBLAS header (gemm_driver.h includes &lt;cblas.h&gt;); OpenBLAS for the reference and benchmark driver; pthreads; Linux CPU-affinity calls in util.cc |
| **Minimum toolchain** | C++11 with GCC-style AT&T inline assembly; the author built with clang++ 7.0.0 and -O3 -m64 -mfma -msse -msse2 via src/build.sh (paths are hard-coded to /opt) |
| **Platforms** | x86-64 with AVX2 and FMA3; Linux; tested only on an Intel Xeon Gold 6142 |
| **Thread safety** | not documented; each call allocates its own packing buffers, but there is no parallel path and the driver pins itself to one CPU |
| **Drop-in for the baseline** | partial — cblas_sgemm-like argument order but different enum types and an extra gemm_context_t argument; only CblasRowMajor/NoTrans/NoTrans works |

## Gotchas

- Non-row-major or transposed calls return silently with C unchanged, rather than failing
- The micro-kernel stores C with aligned vmovaps, so C must be 32-byte aligned with ldc a multiple of 8 floats, and M and N must be multiples of 6 and 16; the benchmark only uses multiples of 48, which hides this
- Packing buffers are malloc'd and freed on every call, which costs time at small sizes
- The % of peak column divides by 1024 instead of 1000 (81.25 rather than 83.2 GFLOPS at 2.6 GHz) and counts 2\*M\*N\*(K+1) flops, so the 96% figures overstate efficiency by a few points; the GFLOPS comparison with OpenBLAS uses the same formula and is unaffected

## Known shortcomings

- 4-9% over OpenBLAS 0.3.4 from 960 up but slower at 144; old OpenBLAS; abandoned 2019.
- Correctness traps: only RowMajor/NoTrans/NoTrans is implemented (the other 7 branches return with C untouched); the 6x16 asm kernel ignores edge tiles, so M%6 or N%16 != 0 reads/writes out of bounds; aligned stores need C 32B-aligned and ldc%8==0; % of peak inflated (divides by 1024); blocking autotuned per size against untuned OpenBLAS.

## Caveats and trade-offs

OpenBLAS is version 0.3.4 (2019) and its build TARGET is not stated, so it may not have been the best kernel for that CPU; the gflops_ref column is not labelled in the README (identified as OpenBLAS from the README sentence and src/gemm_driver.cc / src/build.sh); the win is small (4-9% at large sizes) and reverses at 144^3; build.sh also adds -g and the OpenBLAS path /opt/OpenBLAS is machine-specific; the README says tuning was unfinished; results are 7 years old; single-core only.

SGEMM only, single core, row-major driver; AVX2 kernel (the Xeon Gold 6142 also has AVX-512, which it does not use); needs a per-machine tuned parameter database (sgemm_tuned.db), hyperthreading off and ideally turbo off to reach peak.

## Maintenance

Abandoned since 2019-04-15 (31 commits, 75 stars, one unanswered issue asking for an MKL comparison) but MIT-licensed and small enough to vendor as a study kernel; it is unsafe as a general SGEMM because of the stubbed paths and unchecked edge tiles.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** README table gives gflops vs gflops_ref per size; src/gemm_driver.cc times cblas_sgemm_opt and the linked OpenBLAS cblas_sgemm (openblas_set_num_threads(1), pinned to one core), src/build.sh states clang++ 7.0.0 and -O3 -m64 -mfma -msse -msse2, and the CPU is Xeon Gold 6142 at 2600 MHz.
- **Verifier notes:** All quoted numbers match the README table; the table actually runs to 9120^3, not 3264^3. Metadata checked on github.com: MIT, 75 stars, 16 forks, not a fork, last commit 2019-04-15 (abandoned).
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/carlushuang/cpu_gemm_opt>
  - <https://github.com/carlushuang/cpu_gemm_opt/commits>
  - <https://raw.githubusercontent.com/carlushuang/cpu_gemm_opt/HEAD/README.md>
  - <https://raw.githubusercontent.com/carlushuang/cpu_gemm_opt/HEAD/src/build.sh>
  - <https://raw.githubusercontent.com/carlushuang/cpu_gemm_opt/HEAD/src/gemm_driver.cc>
  - <https://raw.githubusercontent.com/carlushuang/cpu_gemm_opt/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/carlushuang/cpu_gemm_opt>
  - <https://github.com/carlushuang/cpu_gemm_opt/tree/master/src>
  - <https://github.com/carlushuang/cpu_gemm_opt/issues?q=is%3Aissue>
  - <https://github.com/carlushuang/cpu_gemm_opt/issues/1>
  - <https://raw.githubusercontent.com/carlushuang/cpu_gemm_opt/HEAD/README.md>
  - <https://raw.githubusercontent.com/carlushuang/cpu_gemm_opt/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/carlushuang/cpu_gemm_opt/HEAD/src/build.sh>
  - <https://raw.githubusercontent.com/carlushuang/cpu_gemm_opt/HEAD/src/gemm_driver.cc>
  - <https://raw.githubusercontent.com/carlushuang/cpu_gemm_opt/master/src/gemm_driver.h>
  - <https://raw.githubusercontent.com/carlushuang/cpu_gemm_opt/master/src/gemm_config.h>
  - <https://raw.githubusercontent.com/carlushuang/cpu_gemm_opt/master/src/gemm_opt.cc>
  - <https://raw.githubusercontent.com/carlushuang/cpu_gemm_opt/master/src/sgemm_tuned.db>
  - <https://raw.githubusercontent.com/carlushuang/cpu_gemm_opt/master/src/util.h>
  - <https://raw.githubusercontent.com/carlushuang/cpu_gemm_opt/master/src/util.cc>
  - <https://raw.githubusercontent.com/carlushuang/cpu_gemm_opt/master/src/kernel/sgemm_asm_6x16.cc>
  - <https://raw.githubusercontent.com/carlushuang/cpu_gemm_opt/master/src/kernel/sgemm_pack.cc>
  - <https://raw.githubusercontent.com/carlushuang/cpu_gemm_opt/master/src/kernel/sgemm_c.cc>
  - <https://raw.githubusercontent.com/carlushuang/cpu_gemm_opt/master/src/kernel/sgemm_micro_kernel.h>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/carlushuang/cpu_gemm_opt`) · [data/wave8/enrich/raw/github_com_carlushuang_cpu_gemm_opt.json](../../../data/wave8/enrich/raw/github_com_carlushuang_cpu_gemm_opt.json) (enrichment confidence 0.85)

</details>
