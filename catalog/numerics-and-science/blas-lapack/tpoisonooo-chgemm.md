# chgemm

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🔴 abandoned

> Symmetric int8 x int8 to int32 GEMM for ARMv8 (aarch64) NEON, hand-written assembly; reported above gemmlowp on RK3399.

| | |
|---|---|
| **Beats** | gemmlowp (int8 GEMM); also reported against the fp32 single-core peak of the same CPU |
| **Claimed result** | how-to-optimize-gemm README (Chinese): chgemm int8 reaches up to 18.6 GFLOPS on one RK3399 core, vs an fp32 single-core theoretical limit of 14.3 GFLOPS and 'gemmlowp大约 12-14gflops' (gemmlowp about 12-14 GFLOPS); roughly 1.3x to 1.55x vs gemmlowp (derived from page data). chgemm README: peak 18.6 GFLOPS on RK3399 single core (graph 0.png, sizes 100-2000, about 16.3-18.6 GFLOPS above size 200), and about 23 GFLOPS on one AWS A72 core, which it calls the limit of this method. |
| **Workload** | Single-core int8 x int8 to int32 symmetric-quantised GEMM on a Rockchip RK3399 (aarch64) core, row-major, built with -O3. |
| **Metric** | throughput |
| **Hardware** | Rockchip RK3399 single core; AWS Cortex-A72 single core (about 23 GFLOPS, per chgemm README) |
| **Compiler and flags** | gcc (version not stated) with -O3 -g -Wall per the repo makefile (README: 'Compiled on RK3399 with -O3 flag'); ARM NEON C plus aarch64 assembly int8 kernels (int8kernel_m4/m2/m1, kernel_m4n4k16.S). |
| **Adoption** | 68 stars; the how-to-optimize-gemm README says chgemm was merged into ncnn's INT8 convolution |
| **Last commit** | 2020-06-07 |
| **Links** | [repository](https://github.com/tpoisonooo/chgemm) · [benchmark](https://github.com/tpoisonooo/how-to-optimize-gemm) |

## Verdict

chgemm's README reports up to 18.6 GFLOPS (counting int8 multiply-adds) on one RK3399 core with gcc -O3, plotted against the 14.3 GFLOPS fp32 single-core peak rather than another library, and about 23 GFLOPS on one AWS Cortex-A72 core. The gemmlowp comparison is an approximate, unsourced 'about 12-14 GFLOPS' in the separate how-to-optimize-gemm README, so the roughly 1.3x-1.55x lead over gemmlowp is derived from page data, not from a measured gemmlowp run.

## Use it when

- Int8 inference GEMM or 1x1 convolution on ARMv8.0 aarch64 cores without dot-product instructions (RK3399-class boards, Cortex-A72 servers such as the AWS A72 the README mentions)
- Symmetric quantisation is already in use, so weights and activations are in [-127, 127] and an int32 (or requantised int8) output is wanted
- Single-threaded row-major workloads where you can pre-pack the weight matrix once, since the pack step is exposed as a separate call
- As a compact, readable reference for the SMULL/SMLAL/SADALP int8 micro-kernel when writing your own

## Skip it when

- Cores with SDOT/I8MM (ARMv8.2 and later): these kernels do not use them, so kernels that do will be faster
- Asymmetric uint8 quantisation with zero points (the gemmlowp/TFLite convention) or data that contains -128
- Anything that needs a BLAS-style interface: no alpha/beta, transposes, leading dimensions, column-major input or float output; multi-threading is not provided (issue #6, 'can it support multi-core', open since July 2022 with no reply)
- x86, 32-bit ARM, Windows or Apple aarch64: the .S kernels are wrapped in '#if __aarch64__' and '#ifndef __APPLE__', and the C driver stops with '#error only support arm neon' without NEON
- Projects that need a maintained dependency or a clear license file: abandoned since June 2020 (13 commits), and BSD-3-Clause is stated only by a README badge

## How it is fast

GotoBLAS-style packing: reorder_a (assembly) and reorder_b (a C header in MMult_4x8_22; MMult_4x8_21 transposes B and reuses reorder_a) copy A and B into panel order, then int8kernel_m4 computes 4-row by 4-column tiles with 16 int32 accumulator registers (v8-v23), with int8kernel_m2/m1 for leftover rows and K split into 8/4/2/1 remainders. The inner loop uses the SMULL/SMLAL/SADALP pattern: SMULL multiplies int8 pairs into int16, SMLAL adds a second int8 product into the same int16 lane, and SADALP pairwise-widens into the int32 accumulators, which halves the widening work. It uses no SDOT dot-product instructions (the m4 kernel has only smull/smlal/saddlp/sadalp/addp arithmetic), so it runs on ARMv8.0 cores like the RK3399's.

## Compared with alternatives

It is the only int8 CPU kernel among the catalogued blas-lapack entries (LibShalom, IAAT and BLASFEO target fp32/fp64 small GEMM, MuBLIS and MTGEMM-A target Apple fp32), so pick it only for symmetric int8 to int32 on pre-dot-product aarch64; for floating point use those siblings or OpenBLAS.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (C plus GNU-syntax aarch64 assembly); OpenMP only if you build MMult_4x8_22.c with -fopenmp |
| **Minimum toolchain** | not documented; the makefile uses gcc -O3 with C99-style declarations in for loops and .S files assembled by gcc; an Android Studio sample (android/MyApplication) is included |
| **Platforms** | aarch64 Linux and Android with NEON only; not Apple, not armv7, not x86 |
| **Thread safety** | not documented; from the source, MY_MMult keeps no global state and allocates its own pack buffers on every call |
| **Drop-in for the baseline** | no |

## Gotchas

- The [-127, 127] limit is a correctness requirement, not a recommendation: two int8 products are summed in an int16 lane before widening, and (-128)\*(-128)\*2 = 32768 overflows int16 silently.
- The test driver's random_int8_matrix fills inputs with val % 3 (only 0, 1, 2), so the bundled correctness check never exercises negative values, extremes or the int16 overflow edge.
- MY_MMult ignores lda and ldb (it packs as if A is m x k and B is k x n contiguous), passes n as the output stride, and mallocs, packs and frees both A and B on every call; the published timings include that packing.
- The makefile's default NEW is MMult_4x8_22, which carries '#pragma omp parallel for num_threads(3)', but CFLAGS has no -fopenmp, so it runs single-threaded; adding -fopenmp silently switches it to exactly 3 threads. parameters.h defaults to a single 77x77x77 run with NREPEATS 1, so reproducing the README graph means editing it.

## Known shortcomings

- The gemmlowp baseline ('about 12-14 GFLOPS') is an unsourced approximation; the repo's own graph shows only its fp32 peak. BSD-3 is declared by a README badge only (no LICENSE file). Built with gcc -O3 -g -Wall.
- Correctness: inputs must stay in [-127,127] because two int8 products are summed in one int16 lane, so -128 overflows silently; the bundled test only fills inputs with val%3 (0, 1, 2), so negatives and overflow are never tested. lda/ldb are ignored. The default build looks multithreaded (omp parallel for num_threads(3) in MMult_4x8_22) but runs on one thread because the makefile has no -fopenmp. README's ncnn link (gemm_symm_int8.h) is now 404.

## Caveats and trade-offs

The gemmlowp comparison is only an approximate, unsourced range in the README of a different repo (the GPLv3 tutorial how-to-optimize-gemm); chgemm's own graph has no gemmlowp line (it shows chgemm, labelled 'mystery', against a flat fp32-peak line), and the repo's test harness compares only against a naive reference (REF_MMult.c). Peak 18.6 GFLOPS is a best case at size 2000. GFLOPS count int8 operations, so comparison with fp32 libraries is not like-for-like. Baseline gemmlowp is not one of OpenBLAS, MKL, Eigen or BLIS. License: BSD-3-Clause is declared only by a README badge; there is no LICENSE file (raw LICENSE 404) and no copyright header in the sources checked, so keep the attribution question in mind when copying; the same code ships in ncnn (BSD-3-Clause) as src/layer/arm/gemm_symm_int8.h. Build badge points to defunct travis-ci.org. 13 commits, last commit 2020-06-07.

aarch64/ARM only, int8 inputs restricted to [-127, 127] (symmetric quantisation, -128 not allowed), int32 output, row-major, simplified C = A\*B without alpha/beta, open packAB interface for deep-learning use. It is not a general BLAS replacement.

## Maintenance

Abandoned since 2020-06-07 (13 commits; the README's ncnn file link, src/layer/arm/gemm_symm_int8.h, now returns 404 on ncnn master), but it is a dozen small C and assembly files that are easy to vendor once you settle the license question (badge says BSD-3-Clause, no LICENSE file).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party only: chgemm's own graph (0.png) plots chgemm against a constant fp32-peak line, not against gemmlowp, and the gemmlowp figure is an approximate, unsourced range ('gemmlowp大约 12-14gflops') in the how-to-optimize-gemm README with no gemmlowp benchmark code, version or shapes.
- **Verifier notes:** Record accurate; tier C stands (gemmlowp number is approximate and not measured by public code). Shortcomings worth recording: no measured gemmlowp baseline, and the BSD-3-Clause license is declared only by a README badge with no LICENSE file.
- **Fields the verifier corrected:** `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://github.com/tpoisonooo/chgemm>
  - <https://github.com/tpoisonooo/chgemm/commits/master>
  - <https://raw.githubusercontent.com/tpoisonooo/chgemm/HEAD/README.md>
  - <https://raw.githubusercontent.com/tpoisonooo/chgemm/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/tpoisonooo/chgemm/HEAD/0.png>
  - <https://raw.githubusercontent.com/tpoisonooo/chgemm/HEAD/makefile>
  - <https://raw.githubusercontent.com/tpoisonooo/chgemm/HEAD/MMult_4x8_21.c>
  - <https://raw.githubusercontent.com/tpoisonooo/how-to-optimize-gemm/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/tpoisonooo/chgemm>
  - <https://github.com/tpoisonooo/chgemm/commits/master>
  - <https://github.com/tpoisonooo/chgemm/issues?q=is%3Aissue>
  - <https://github.com/tpoisonooo/chgemm/issues/5>
  - <https://raw.githubusercontent.com/tpoisonooo/chgemm/HEAD/README.md>
  - <https://raw.githubusercontent.com/tpoisonooo/chgemm/HEAD/makefile>
  - <https://raw.githubusercontent.com/tpoisonooo/chgemm/HEAD/MMult_4x8_21.c>
  - <https://raw.githubusercontent.com/tpoisonooo/chgemm/HEAD/MMult_4x8_22.c>
  - <https://raw.githubusercontent.com/tpoisonooo/chgemm/HEAD/parameters.h>
  - <https://raw.githubusercontent.com/tpoisonooo/chgemm/HEAD/public.h>
  - <https://raw.githubusercontent.com/tpoisonooo/chgemm/HEAD/test_MMult.c>
  - <https://raw.githubusercontent.com/tpoisonooo/chgemm/HEAD/REF_MMult.c>
  - <https://raw.githubusercontent.com/tpoisonooo/chgemm/HEAD/random_matrix.c>
  - <https://raw.githubusercontent.com/tpoisonooo/chgemm/HEAD/reorder_b.h>
  - <https://raw.githubusercontent.com/tpoisonooo/chgemm/HEAD/.travis.yml>
  - <https://raw.githubusercontent.com/tpoisonooo/chgemm/HEAD/int8kernel_m4.S>
  - <https://raw.githubusercontent.com/tpoisonooo/chgemm/HEAD/kernel_m4n4k16.S>
  - <https://raw.githubusercontent.com/tpoisonooo/how-to-optimize-gemm/HEAD/README.md>
  - <https://raw.githubusercontent.com/Tencent/ncnn/master/src/layer/arm/gemm_symm_int8.h>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/tpoisonooo/chgemm`) · [data/wave8/enrich/raw/github_com_tpoisonooo_chgemm.json](../../../data/wave8/enrich/raw/github_com_tpoisonooo_chgemm.json) (enrichment confidence 0.75)

</details>
