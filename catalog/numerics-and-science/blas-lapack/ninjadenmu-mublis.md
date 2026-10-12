# MuBLIS

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Small BLIS-style C framework for real L3 BLAS with NEON/AVX2 kernels; matches single-threaded OpenBLAS on Apple M4.

| | |
|---|---|
| **Beats** | OpenBLAS (single-threaded, built for Apple Silicon) |
| **Claimed result** | README chart (Apple M4, f32, single thread): GEMM 111.0 vs OpenBLAS 109.9 GFLOP/s (1.01x, derived from page data), SYMM 109.7 vs 109.5, SYRK 109.4 vs 108.8, SYR2K 109.4 vs 109.0, TRSM 100.9 vs 100.2, TRMM 95.8 vs 110.3 (0.87x, slower). README text: matches single-threaded OpenBLAS on 5 of 6 L3 operations and 'slightly outperforms OpenBLAS', \~80% of peak for single-threaded GEMM; generic cache-tiled baseline 6.0-6.3 GFLOP/s (about 17-18x below MuBLIS, derived from page data; README says '\~20x'). |
| **Workload** | Level-3 real BLAS operations (GEMM and others) generated from a BLIS-style framework with NEON and AVX2 micro-kernels, single thread, f32, Apple M4. |
| **Metric** | throughput |
| **Hardware** | Apple M4 (also tested on Xeon Gold 6248R, Ryzen 7 7700X, i5-7500 per README) |
| **Adoption** | 2 stars |
| **Last commit** | 2026-09-01 |
| **Links** | [repository](https://github.com/NinjadenMu/MuBLIS) · [benchmark](https://github.com/NinjadenMu/MuBLIS) |

## Verdict

The README chart for an Apple M4, single thread, f32, shows MuBLIS against an OpenBLAS built for that machine: GEMM 111.0 vs 109.9 GFLOP/s, SYMM 109.7 vs 109.5, SYRK 109.4 vs 108.8, SYR2K 109.4 vs 109.0, TRSM 100.9 vs 100.2, and TRMM 95.8 vs 110.3. That is parity on five routines and a loss on TRMM; matrix sizes, compiler, flags and OpenBLAS version are not given, and the AVX2 results on Xeon Gold 6248R, Ryzen 7 7700X and i5-7500 are described without numbers.

## Use it when

- You are bringing up a CBLAS Level-3 library on new or unusual hardware and want the packing and tiling framework done, so that you only write micro-kernels and block sizes.
- Single-threaded real f32/f64 GEMM, SYMM, SYRK, SYR2K or TRSM on Apple M-series or other NEON CPUs, where its README chart shows it within about 1% of single-threaded OpenBLAS.
- Multithreaded applications that call BLAS concurrently from many threads, each on its own small or medium problem: the library is reentrant and pools its pack buffers.
- Teaching or studying a compact, readable BLIS-style implementation in plain C with intrinsics rather than assembly.

## Skip it when

- You want more speed than OpenBLAS: the published gains are 0.2-1% (within noise), and TRMM is about 13% slower (95.8 vs 110.3 GFLOP/s on M4).
- Large matrices that should use every core: there is no internal multithreading, and all published numbers are single-threaded.
- Complex types, Level 1/2 routines, or Fortran BLAS symbols (dgemm_): none are implemented, so it cannot back LAPACK on its own.
- Apple Silicon throughput work: its kernels are NEON only; the catalogued Apple siblings (sme-gemm, MTGEMM-A) report Accelerate's SME/AMX path at about 2 TFLOP/s f32, against MuBLIS's 111 GFLOP/s on one core.
- Production use that needs maturity: the project started in July 2026, has 2 stars, and its own README calls its correctness tests non-comprehensive.

## How it is fast

It uses the BLIS/Goto layered loop nest: B is packed into kc x nc panels, A into mc x kc blocks, and a register-blocked micro-kernel computes one mr x nr tile of C (12x8 for f32 and 6x8 for f64 on the Apple 'firestorm' target) with NEON FMA intrinsics, full unrolling and a software prefetch of the next C tile. The out-of-place routines (GEMM, SYMM, SYRK, SYR2K) are thin shims over one L3 driver that skips or restricts blocks according to matrix structure; TRSM uses fused GEMM-TRSM micro-kernels, and TRMM sizes its triangular blocks from the cache block and the matrix size. Pack buffers are recycled from a pool rather than allocated on every call.

## Compared with alternatives

Pick MuBLIS over GEMMFIP (the BLIS fork) or OxiBLAS when you need a small, readable C framework to port Level-3 BLAS to new hardware, or a reentrant single-threaded CBLAS on NEON. For raw speed, OpenBLAS itself, Accelerate, or the SME-based siblings sme-gemm and MTGEMM-A on Apple Silicon are faster or equal.

## Integration

| | |
|---|---|
| **Form** | static lib and shared lib (make CONFIG=&lt;config&gt; builds build/&lt;config&gt;/lib/libmublis.a and libmublis.so/.dylib) |
| **Dependencies** | none beyond libc and pthreads |
| **Minimum toolchain** | C17 compiler (CSTD=c17) and GNU make; clang gets a --target triple from the config, while GCC is used without one |
| **Platforms** | Apple Silicon (firestorm NEON target, -mcpu=apple-m1), Linux aarch64 (NEON), Linux and macOS x86-64 with AVX2+FMA, plus a portable reference config |
| **Thread safety** | Reentrant: the target context is chosen once under pthread_once, and pack buffers come from a mutex-guarded pool that grows when more threads call at once; each call runs on the calling thread only. |
| **Drop-in for the baseline** | partial: it covers the real single- and double-precision Level-3 CBLAS routines (gemm, symm, syrk, syr2k, trmm, trsm) with the standard signatures, but not complex, Level 1/2 or Fortran-ABI BLAS |

## Gotchas

- Every bundled micro-kernel target is compiled with -ffast-math, so IEEE NaN/Inf and signed-zero behaviour inside GEMM is not guaranteed to match OpenBLAS or reference BLAS.
- The bundled configs do not detect the CPU at runtime: linux_avx2's dispatch.c always returns the AVX2 context although the reference target is also linked in, so that build will fault on x86 CPUs without AVX2/FMA. The 'fat binary' support means you write your own dispatch function.
- test/performance/benchmark_cblas.py times only one library per run (switch with MUBLIS_LIB) on all-ones and identity inputs; there is no committed OpenBLAS harness, and the README's matrix sizes, compiler and OpenBLAS version are not stated.
- Cache block sizes are fixed constants per target, not read from the CPU, so a CPU with different cache sizes needs retuning in the target's context.c.

## Known shortcomings

- Parity with OpenBLAS, not faster: GEMM 111.0 vs 109.9 GFLOP/s, TRMM 95.8 vs 110.3 (slower).
- Parity only (TRMM 13% slower). linux_avx2 dispatch always returns the AVX2 context with no CPU check, so it faults on non-AVX2 x86. Kernels built with -ffast-math (NaN/Inf semantics). No complex types, no Level 1/2, no Fortran ABI, no internal threading.

## Caveats and trade-offs

Margins over OpenBLAS are 0.2-1% (within run-to-run noise) and TRMM is 13% slower, so this is parity rather than a speedup; numbers appear only in a chart image; matrix sizes, compiler, flags and OpenBLAS version are not stated; the bundled benchmark_cblas.py uses all-ones inputs and has no OpenBLAS harness (it can load another library via MUBLIS_LIB). x86 AVX2 results on Xeon Gold 6248R, Ryzen 7 7700X and i5-7500 are described as 'strong performance' without numbers. The same author's fast_matmul repo reportedly calls its kernel 'comparable' to OpenBLAS (not re-checked in this run).

Framework in which per-microarchitecture micro-kernels are about 200 lines each; ships NEON and AVX2 kernels; L3 BLAS only; single-threaded numbers in the README.

## Maintenance

Active (first commit July 2026, last 2026-09-01) and MIT-licensed, small enough to vendor, but a 2-star single-author project with limited tests.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README chart (images/gflops_apple_m4.png) with per-operation GFLOP/s on a named CPU (Apple M4), but no matrix sizes, compiler flags or OpenBLAS version for the run, and the repo's test/performance/benchmark_cblas.py only times whichever library it loads, so not A.
- **Verifier notes:** Chart numbers read directly from the image; the win is about 1% on GEMM and absent on TRMM, so record as parity with OpenBLAS (shortcoming: not meaningfully faster). Metadata verified: MIT, 2 stars, last commit 2026-09-01.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/NinjadenMu/MuBLIS>
  - <https://github.com/NinjadenMu/MuBLIS/commits/main>
  - <https://github.com/NinjadenMu/MuBLIS/tree/main/test/performance>
  - <https://github.com/NinjadenMu/MuBLIS/tree/main/targets>
  - <https://raw.githubusercontent.com/NinjadenMu/MuBLIS/HEAD/README.md>
  - <https://raw.githubusercontent.com/NinjadenMu/MuBLIS/HEAD/images/gflops_apple_m4.png>
  - <https://raw.githubusercontent.com/NinjadenMu/MuBLIS/HEAD/test/performance/benchmark_cblas.py>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/NinjadenMu/MuBLIS/HEAD/README.md>
  - <https://raw.githubusercontent.com/NinjadenMu/MuBLIS/HEAD/Makefile>
  - <https://raw.githubusercontent.com/NinjadenMu/MuBLIS/HEAD/make/configure.mk>
  - <https://raw.githubusercontent.com/NinjadenMu/MuBLIS/HEAD/make/rules.mk>
  - <https://raw.githubusercontent.com/NinjadenMu/MuBLIS/HEAD/make/sources.mk>
  - <https://raw.githubusercontent.com/NinjadenMu/MuBLIS/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/NinjadenMu/MuBLIS/HEAD/test/performance/benchmark_cblas.py>
  - <https://raw.githubusercontent.com/NinjadenMu/MuBLIS/HEAD/targets/README.md>
  - <https://raw.githubusercontent.com/NinjadenMu/MuBLIS/HEAD/targets/firestorm/target.mk>
  - <https://raw.githubusercontent.com/NinjadenMu/MuBLIS/HEAD/targets/firestorm/context.c>
  - <https://raw.githubusercontent.com/NinjadenMu/MuBLIS/HEAD/targets/firestorm/firestorm.h>
  - <https://raw.githubusercontent.com/NinjadenMu/MuBLIS/HEAD/targets/firestorm/gemm_ukr.inc>
  - <https://raw.githubusercontent.com/NinjadenMu/MuBLIS/HEAD/targets/avx2/target.mk>
  - <https://raw.githubusercontent.com/NinjadenMu/MuBLIS/HEAD/targets/aarch64/target.mk>
  - <https://raw.githubusercontent.com/NinjadenMu/MuBLIS/HEAD/config/README.md>
  - <https://raw.githubusercontent.com/NinjadenMu/MuBLIS/HEAD/config/apple_silicon/config.mk>
  - <https://raw.githubusercontent.com/NinjadenMu/MuBLIS/HEAD/config/apple_silicon/dispatch.c>
  - <https://raw.githubusercontent.com/NinjadenMu/MuBLIS/HEAD/config/linux_avx2/config.mk>
  - <https://raw.githubusercontent.com/NinjadenMu/MuBLIS/HEAD/config/linux_avx2/dispatch.c>
  - <https://raw.githubusercontent.com/NinjadenMu/MuBLIS/HEAD/include/mublis.h>
  - <https://raw.githubusercontent.com/NinjadenMu/MuBLIS/HEAD/include/cblas.h>
  - <https://raw.githubusercontent.com/NinjadenMu/MuBLIS/HEAD/include/mublis_instantiate.h>
  - <https://raw.githubusercontent.com/NinjadenMu/MuBLIS/HEAD/frame/base/pool.c>
  - <https://raw.githubusercontent.com/NinjadenMu/MuBLIS/HEAD/frame/base/safe_dispatch.c>
  - <https://github.com/NinjadenMu/MuBLIS>
  - <https://github.com/NinjadenMu/MuBLIS/commits/main>
  - <https://github.com/NinjadenMu/MuBLIS/tree/main/config>
  - <https://github.com/NinjadenMu/MuBLIS/tree/main/targets>
  - <https://github.com/NinjadenMu/MuBLIS/tree/main/frame/base>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/ninjadenmu/mublis`) · [data/wave8/enrich/raw/github_com_ninjadenmu_mublis.json](../../../data/wave8/enrich/raw/github_com_ninjadenmu_mublis.json) (enrichment confidence 0.75)

</details>
