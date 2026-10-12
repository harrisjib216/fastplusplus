# LibShalom

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🟡 stale

> ARMv8 assembly GEMM library for small and irregular-shaped SGEMM/DGEMM; beats OpenBLAS, BLIS, ARMPL, LIBXSMM and BLASFEO there.

| | |
|---|---|
| **Beats** | OpenBLAS, BLIS, ARMPL, LIBXSMM, BLASFEO |
| **Claimed result** | 2x higher throughput than BLASFEO at M=N=K=8 single-thread on Phytium 2000+; 2.6x higher GFLOPS than BLIS at M=32,N=50176,K=5000 on Phytium 2000+; 1.05-2x higher throughput than competing libraries overall; average 1.8x over the second-best (BLIS) on irregular shapes |
| **Workload** | Small (8..128) and irregular-shaped SGEMM/DGEMM on ARMv8 multi-cores |
| **Metric** | throughput |
| **Hardware** | Phytium 2000+, Kunpeng 920, ThunderX2 |
| **Compiler and flags** | gcc 8.2.1 -O3 |
| **Adoption** | 18 stars |
| **Last commit** | 2022-04-08 |
| **Links** | [repository](https://github.com/AnonymousYWL/LibShalom) · [benchmark](https://zwang4.github.io/publications/tpds21-1.pdf) |

## Verdict

The LibShalom paper (ACM, 2021) measured with GCC 8.2.1 -O3 on Phytium 2000+, Kunpeng 920 and ThunderX2: single-thread small GEMM reaches 2x BLASFEO at 8x8x8 and 5-10% over the best other library at 32-128, and multithreaded irregular GEMM with M=32 reaches 2.6x BLIS on Phytium 2000+ (averages 1.8x over BLIS on Kunpeng 920, 1.4x on ThunderX2). The repo's own benchmark times LibShalom only, so baseline numbers come from the paper.

## Use it when

- Many tiny GEMMs (8..128 per side) on ARMv8 servers such as Kunpeng 920, Phytium 2000+ or ThunderX2, single-threaded
- Skinny multithreaded GEMMs such as conv-layer-as-GEMM (M of 16-64, N in the tens of thousands, large K) on many-core ARM
- Row-major C = A\*B or C = A\*B^T where you control the call site and can adopt a non-BLAS API
- Research baselines for small/irregular GEMM on ARM

## Skip it when

- x86 or any non-ARMv8 target: kernels are AArch64 inline assembly
- Code that needs a BLAS/CBLAS drop-in, alpha/beta scaling, strided (leading-dimension) operands or column-major layout
- Large square GEMMs: the paper defers those to existing libraries
- DGEMM beyond the small NN path, or complex types: the API covers only SGEMM variants and one DGEMM entry point
- Production use needing maintenance: anonymous-account repo, last commit 2022-04-08, new issues restricted

## How it is fast

It skips packing when operands fit in L1 or are read sequentially, and where packing is needed it interleaves the pack loads/stores with the FMA stream of the micro-kernel instead of running it as a separate pass. Micro-kernel tile sizes (7x12 for FP32) come from an analytical model that maximizes the compute-to-memory ratio, and edge cases get dedicated scheduled kernels. Multithreading partitions both M and N, with the N split chosen as ceil(sqrt(T\*N/M)), so skinny shapes still feed all cores.

## Compared with alternatives

Pick it over BLASFEO when you need multithreaded skinny GEMMs on ARM (BLASFEO is single-threaded and was left out of that comparison), and over OpenBLAS/BLIS for tiny or irregular shapes on ARMv8; on x86 use BLASFEO or LIBXSMM-class code instead, and for Graviton 3 / medium sizes the GEMMFIP BLIS fork is the comparable option with a BLAS interface.

## Integration

| | |
|---|---|
| **Form** | static lib (libsmm.a) or shared lib (libsmm.so) built by a plain Makefile |
| **Dependencies** | OpenMP |
| **Minimum toolchain** | GCC 8.2+ (README); built as C++ with g++ because the header includes &lt;vector&gt; |
| **Platforms** | aarch64 (ARMv8 NEON) only; tested on Phytium 2000+, Kunpeng 920, ThunderX2 |
| **Thread safety** | not documented; thread counts and partitioning live in global variables (vec, Tm, Tn, T) set by LibShalom_set_thread_nums |
| **Drop-in for the baseline** | no |

## Gotchas

- Despite being listed as C, LibShalom.h includes &lt;vector&gt; and has 'using namespace std', so it compiles only as C++
- NN_LIB/Makefile compiles object files without -O flags (-O3 appears only on the link line); the inline-assembly kernels are unaffected but the C driver code builds at -O0 unless you edit it
- Row-major only; the README example passes B as transposed (NT), so check the transb convention before use
- Header hard-codes blocking constants (GEMM_K 320, GEMM_N 4096, GEMM_M 256) tuned for the tested CPUs

## Known shortcomings

- Record overstated: 2x is vs BLASFEO and 2.6x vs BLIS, not OpenBLAS; repo benchmarks time LibShalom only, not the baselines.
- Two repos by the same author carry identical LibShalom READMEs (MYLIB and LibShalom); repo_url set to the one named LibShalom.

## Caveats and trade-offs

Repo hosted under an anonymized account (AnonymousYWL/MYLIB); paper page itself redacted the URL, repo linked via search; ARM only

ARMv8 only, C with OpenMP and assembly kernels; GEMM only

## Maintenance

Stale since April 2022 with new issues restricted, but MIT-licensed and small enough to vendor as a source drop for AArch64 builds.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed SC'21-era ACM paper comparing against OpenBLAS, BLIS, ARMPL, LIBXSMM and BLASFEO with GCC 8.2.1 -O3 on named ARM CPUs. Not A because the repo's benchmark directory times LibShalom only, not the baselines. Downgraded because the record's claim was overstated: the 2x and 2.6x figures are against other baselines, not OpenBLAS.
- **Verifier notes:** The record attributed the 2x and 2.6x figures to OpenBLAS; on the page they are against BLASFEO and BLIS respectively. MIT license, 18 stars and last commit 2022-04-08 are confirmed; the README is titled LibShalom.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`
- **Pages the verifier opened:**
  - <https://zwang4.github.io/publications/tpds21-1.pdf>
  - <https://github.com/AnonymousYWL/MYLIB>
  - <https://github.com/AnonymousYWL/MYLIB/commits>
- **Sources the enricher read:**
  - <https://github.com/AnonymousYWL/MYLIB>
  - <https://raw.githubusercontent.com/AnonymousYWL/MYLIB/HEAD/README.md>
  - <https://raw.githubusercontent.com/AnonymousYWL/MYLIB/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/AnonymousYWL/MYLIB/HEAD/NN_LIB/Makefile>
  - <https://raw.githubusercontent.com/AnonymousYWL/MYLIB/HEAD/NN_LIB/LibShalom.h>
  - <https://raw.githubusercontent.com/AnonymousYWL/MYLIB/HEAD/NN_LIB/SMM_NT_thread.c>
  - <https://github.com/AnonymousYWL/MYLIB/issues>
  - <https://zwang4.github.io/publications/tpds21-1.pdf>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/anonymousywl/mylib`) · [data/wave8/enrich/raw/github_com_anonymousywl_mylib.json](../../../data/wave8/enrich/raw/github_com_anonymousywl_mylib.json) (enrichment confidence 0.75)

</details>
