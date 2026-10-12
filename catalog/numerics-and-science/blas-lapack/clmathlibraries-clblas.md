# clBLAS

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C/C++ (OpenCL kernels)` · `Apache-2.0` · 🔴 abandoned

> AMD's OpenCL BLAS (levels 1-3) with AutoGemm kernels; on a FirePro S9150 it out-ran cuBLAS 7.5 on a K40 at large GEMMs.

| | |
|---|---|
| **Beats** | NVIDIA cuBLAS 7.5 (Tesla K40) |
| **Claimed result** | The Perf wiki page gives charts only and states no ratio. Values read off the chart PNGs at the largest sizes (about 5750; approximate, derived from page data): SGEMM clBLAS on S9150 in two bands of about 3600 and about 4000-4100 GFlop/s vs cuBLAS on K40 about 3050-3200 (about 1.15x-1.3x); DGEMM about 1880-1900 vs about 1250 (about 1.5x); CGEMM about 4500-4550 vs about 3050-3100 (about 1.45x); ZGEMM about 1940 vs about 1200 (about 1.6x); DTRSM about 1200 vs about 1220 (parity, the K40 is ahead at several sizes). cuBLAS leads or ties below roughly 1000 (CGEMM, ZGEMM) to 1200 (DGEMM) and up to about 2500-3000 (SGEMM, main band) matrix size. |
| **Workload** | Square GEMM sweeps (SGEMM, DGEMM, CGEMM, ZGEMM; M=N=K from small up to about 5750) and square DTRSM, clBLAS 2.8.0 on an AMD S9150 (driver 14.50.2) plotted against cuBLAS 7.5 on an NVIDIA K40, GPU clocks set to max on both devices. |
| **Metric** | throughput |
| **Hardware** | AMD S9150 GPU (driver 14.50.2) vs NVIDIA K40 GPU; host CPU not stated |
| **Adoption** | 866 stars, 236 forks |
| **Last commit** | 2017-03-23 |
| **Links** | [repository](https://github.com/clMathLibraries/clBLAS) · [benchmark](https://github.com/clMathLibraries/clBLAS/wiki/Perf) |

## Verdict

AMD's wiki charts (2015) plot clBLAS 2.8.0 on a FirePro S9150 (driver 14.50.2) against cuBLAS 7.5 on a Tesla K40, with both GPUs at max clocks and the host CPU and compiler flags unstated. At sizes near 5750, clBLAS is ahead by about 1.15x-1.3x on SGEMM, 1.45x on CGEMM and 1.5x-1.6x on DGEMM and ZGEMM, and roughly level on DTRSM; cuBLAS leads below about 1000-3000 depending on precision. These are two different GPUs, the double-precision gaps match the DP peak ratio, and the cuBLAS numbers come from a harness not in the repo.

## Use it when

- Legacy code already written against the clBLAS API on AMD GCN GPUs of the Hawaii or Fiji generation, the only devices AutoGemm has selection tables for.
- Large square single- or complex-precision GEMM (sizes above about 3000) on those AMD GPUs, where the 2015 charts show 3600-4100 GFlop/s SGEMM and about 4500 GFlop/s CGEMM on an S9150.
- Portable OpenCL 1.2 code that needs the complete BLAS routine list, including level 1 and 2 routines and a CPU OpenCL device path for debugging.

## Skip it when

- Any new project: the repository has had no commits since 2017-03-23 (v2.12 bugfix roll-up), with 89 open issues including test failures on RX 5700 XT (gfx1010, #351) and ROCm (#341), a runtime error with Intel OpenCL 18.1 (#339) and an abort on OpenCL 1.1 (#343).
- Choosing a GPU BLAS by these charts: they compare different GPUs (AMD S9150 vs NVIDIA K40), so they say nothing about clBLAS vs cuBLAS on the same card; on NVIDIA hardware use cuBLAS, and for OpenCL on non-AMD devices the catalogued CLBlast beats clBLAS 2.12 in its IWOCL '18 paper.
- Small and mid-size GEMMs: cuBLAS on the K40 leads or ties up to about 1000 (CGEMM, ZGEMM), 1200 (DGEMM) and 2500-3000 (SGEMM), partly because of first-call kernel compilation and small-tile kernels.
- DTRSM-heavy work: clBLAS reaches about 1200 GFlop/s, only about 47% of the S9150's 2530 GFlop/s DP peak drawn on its own chart, while cuBLAS reaches about 73% of the K40's 1660 (derived from page data).
- Workloads needing batched, FP16 or mixed-precision GEMM, which clBLAS does not provide.

## How it is fast

Level-3 GEMM uses AutoGemm: Python scripts generate tiled OpenCL GEMM kernels at build time (16x16 work-groups with 1x1 to 6x6 register micro-tiles, so up to 96x96 macro-tiles), and a per-precision size table picks the tile for each problem size (for example, SGEMM at size 4000 and above uses only the 16x16 6x6 kernel). The tables were tuned for AMD Hawaii (the default, the S9150's GPU family) and Fiji only. Other routines come from a kernel generator, and kernels are compiled at run time on first call and cached.

## Compared with alternatives

Pick clBLAS over CLBlast only when you maintain existing clBLAS-API code on Hawaii- or Fiji-class AMD GPUs; CLBlast is maintained, auto-tuned for many more devices and beats clBLAS 2.12 in its paper. Neither replaces cuBLAS on NVIDIA hardware or rocBLAS (the base of the catalogued emugemm-cdna) on current AMD GPUs.

## Integration

| | |
|---|---|
| **Form** | shared lib by default (BUILD_SHARED_LIBS ON); static possible |
| **Dependencies** | an OpenCL SDK/ICD (OpenCL 1.2 by default, configurable 1.1 to 2.0) and a Python interpreter at build time for AutoGemm; Boost program_options plus Netlib CBLAS for the client; Google Test, Boost and Netlib CBLAS or ACML for tests |
| **Minimum toolchain** | GCC 4.6+ on Linux or Visual Studio 2010 SP1/2012 on Windows (README); CMake 2.8+ |
| **Platforms** | Windows, Linux and macOS hosts; any OpenCL device in principle, but GEMM tile tables exist only for AMD Hawaii and Fiji; newer AMD (gfx1010, ROCm) and Intel runtimes have open failure reports |
| **Thread safety** | clBLAS.h states the library is thread-safe except clblasSetup and clblasTeardown, which must be called once, outside concurrent use |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: the cuBLAS curves cannot be reproduced from this repository. measurePerformance.py accepts only --library clamdblas and the client (src/client) only calls clBLAS, so the K40 numbers came from an unpublished tool whose timing method is unknown; the clBLAS side times host wall-clock around enqueue plus clWaitForEvents, averaging 20 calls after one warm-up call and pruning 3-sigma outliers.
- The comparison crosses hardware, and the result depends on precision. DGEMM and ZGEMM reach 72-77% of each card's DP peak on both cards (DGEMM 1880-1900 of 2530 vs about 1250 of 1660; ZGEMM about 1940 vs about 1200), so the 1.5x-1.6x gaps mostly track the 1.52x DP-peak ratio. Single precision is closer to a library comparison: the S9150's 5.07 TFLOPS SP peak is about the K40's at the boost clock implied by the chart's 1660 DP line (search snippets give a 3:1 SP:DP ratio, 4.29/1.43). There clBLAS SGEMM (71-81%) and CGEMM (about 89%) are ahead of cuBLAS (about 60-64%). All ratios are derived from page data and snippets.
- The S9150 SGEMM points split into separate performance bands at the same size (about 3600 vs about 4100 GFlop/s near 5750), probably from AutoGemm's fixed 96x96 tile and edge handling, so performance depends on whether your sizes are tile multiples. The Perf page also says better SGEMM and DGEMM need NDA-only compiler flags and a proprietary clock-stabilization tool.
- The top-level CMake defaults CMAKE_BUILD_TYPE to Debug when unset, and BUILD_CLIENT is off by default; pass -DCMAKE_BUILD_TYPE=Release for host-side overhead comparable to the charts.

## Known shortcomings

- First-party wiki charts: clBLAS 2.8.0 on S9150 vs cuBLAS 7.5 on K40 (different hardware), DGEMM efficiency equal at about 75%, SGEMM crossover about 2500-3000, NDA-only flags and clock tool, no host CPU or flags. Abandoned since 2017-03-23; CLBlast (wave 8, B) beats it.
- Enricher: the cuBLAS curves cannot be reproduced from the repo (measurePerformance.py takes only clamdblas, the client only calls clBLAS); the DGEMM/ZGEMM gaps track the two GPUs' double-precision peaks (S9150 2530 vs K40 1660 GFLOPS) while the SGEMM/CGEMM edge is on near-equal single-precision peaks; DTRSM reaches only 47% of peak vs cuBLAS's 73%; AutoGemm tables cover Hawaii and Fiji only; CMake defaults to Debug.

## Caveats and trade-offs

First-party wiki charts with no numbers in the page text; values above are read from the images and are approximate. The comparison crosses hardware: clBLAS runs on an AMD S9150 and cuBLAS on an NVIDIA K40, so the difference mostly tracks the GPUs (the DTRSM chart draws peak lines at about 2530 GFLOPS for the S9150 and about 1660 for the K40; DGEMM efficiency is about 75 percent of peak on both, derived from page data). It is not a comparison against CPU BLAS (MKL, OpenBLAS, ACML). The page says optimized compiler flags and a proprietary clock-stabilization tool exist for AMD NDA customers and improve SGEMM and DGEMM, so the public build may not reproduce the charts. Versions are 2015 era (clBLAS 2.8.0, cuBLAS 7.5, 2015-era driver). The measurement client (src/client, measurePerformance.py) is public but compiler flags and host CPU are missing, hence tier C. [retier] S9150 vs K40 cross-GPU charts; DGEMM/ZGEMM gaps track DP peaks (2530 vs 1660 GFLOPS); DTRSM 47% of peak vs cuBLAS 73%; AutoGemm tables Hawaii/Fiji only; CMake defaults to Debug; CLBlast (wave 8, B) beats it.

OpenCL BLAS levels 1-3 for GPUs, with a CPU-device path for debugging; GEMM kernels come from the AutoGemm generator and are tuned for AMD GPUs. Repository inactive since March 2017 (v2.12 bugfix roll-up), so newer devices and OpenCL versions are untuned. The CLBlast paper (snippet only, paper not opened) benchmarks CLBlast 1.3.0 against clBLAS 2.12 and notes the bundled clBLAS tuner did not complete on some devices.

## Maintenance

Abandoned since 2017-03-23 (v2.12) but Apache-2.0 and buildable with CMake and Python. Its value now is legacy AMD OpenCL support, not speed: the evidence is a first-party cross-GPU chart whose cuBLAS side is unreproducible from the repo, so tier C is the ceiling, and D is defensible because the DGEMM and ZGEMM wins track the hardware's DP peaks.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party wiki page (Perf) with five charts (AutoGemm SGEMM/DGEMM/CGEMM/ZGEMM and DTRSM, clBLAS 2.8.0 on S9150 driver 14.50.2 vs cuBLAS 7.5 on K40); the measurement client (src/client, measurePerformance.py) is public but no host CPU, OpenCL compiler flags or build options are stated, and the page says faster SGEMM/DGEMM needs NDA-only compiler flags and a proprietary clock tool, so it cannot reach A; no independent measurement found, so not B.
- **Retiered** C to D: Lowered C to D: the cuBLAS baseline curves cannot be reproduced from the repo (the harness only drives clBLAS), the comparison is across different GPUs whose peak rates explain the double-precision gaps, and the project is abandoned since 2017; directional only.
- **Verifier notes:** Chart readings in the record match the PNGs (Perf.img/\*_s9150_k40.png); only the SGEMM crossover was understated (main S9150 band catches the K40 near 2500-3000, not 1000-2500). Shortcomings: cross-hardware comparison (AMD S9150 vs NVIDIA K40, equal DGEMM efficiency of about 75 percent of the chart's peak lines, so the DGEMM gap tracks the GPUs), not compared on the same device, 2015-era versions, NDA-only compiler flags and clock tool mentioned on the same page, repo abandoned since 2017-03-23; CLBlast (already verified in wave 8, tier B) reports beating clBLAS 2.12. Metadata checked: Apache-2.0, 866 stars, 236 forks, last commit 2017-03-23, no archived banner.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-173 (wave 8); enricher w8 pair-026
- **Pages the verifier opened:**
  - <https://github.com/clMathLibraries/clBLAS/wiki/Perf>
  - <https://raw.githubusercontent.com/wiki/clMathLibraries/clBLAS/Perf.md>
  - <https://raw.githubusercontent.com/wiki/clMathLibraries/clBLAS/Perf.img/sgemm_s9150_k40.png>
  - <https://raw.githubusercontent.com/wiki/clMathLibraries/clBLAS/Perf.img/dgemm_s9150_k40.png>
  - <https://raw.githubusercontent.com/wiki/clMathLibraries/clBLAS/Perf.img/cgemm_s9150_k40.png>
  - <https://raw.githubusercontent.com/wiki/clMathLibraries/clBLAS/Perf.img/zgemm_s9150_k40.png>
  - <https://raw.githubusercontent.com/wiki/clMathLibraries/clBLAS/Perf.img/dtrsm_s9150_k40.png>
  - <https://github.com/clMathLibraries/clBLAS>
  - <https://github.com/clMathLibraries/clBLAS/commits>
- **Sources the enricher read:**
  - <https://github.com/clMathLibraries/clBLAS>
  - <https://github.com/clMathLibraries/clBLAS/issues>
  - <https://github.com/clMathLibraries/clBLAS/tree/master/src/client>
  - <https://raw.githubusercontent.com/clMathLibraries/clBLAS/HEAD/README.md>
  - <https://raw.githubusercontent.com/clMathLibraries/clBLAS/HEAD/CHANGELOG>
  - <https://raw.githubusercontent.com/clMathLibraries/clBLAS/HEAD/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/clMathLibraries/clBLAS/HEAD/src/library/CMakeLists.txt>
  - <https://raw.githubusercontent.com/clMathLibraries/clBLAS/HEAD/src/clBLAS.h>
  - <https://raw.githubusercontent.com/clMathLibraries/clBLAS/HEAD/src/library/blas/AutoGemm/AutoGemmParameters.py>
  - <https://raw.githubusercontent.com/clMathLibraries/clBLAS/HEAD/src/client/client.cpp>
  - <https://raw.githubusercontent.com/clMathLibraries/clBLAS/HEAD/src/client/clfunc_xgemm.hpp>
  - <https://raw.githubusercontent.com/clMathLibraries/clBLAS/HEAD/src/client/clfunc_common.hpp>
  - <https://raw.githubusercontent.com/clMathLibraries/clBLAS/HEAD/src/client/clfunc_xtrsm.hpp>
  - <https://raw.githubusercontent.com/clMathLibraries/clBLAS/HEAD/src/client/statisticalTimer.cpp>
  - <https://raw.githubusercontent.com/wiki/clMathLibraries/clBLAS/Perf.md>
  - <https://raw.githubusercontent.com/wiki/clMathLibraries/clBLAS/Perf.img/sgemm_s9150_k40.png>
  - <https://raw.githubusercontent.com/wiki/clMathLibraries/clBLAS/Perf.img/dgemm_s9150_k40.png>
  - <https://raw.githubusercontent.com/wiki/clMathLibraries/clBLAS/Perf.img/cgemm_s9150_k40.png>
  - <https://raw.githubusercontent.com/wiki/clMathLibraries/clBLAS/Perf.img/zgemm_s9150_k40.png>
  - <https://raw.githubusercontent.com/wiki/clMathLibraries/clBLAS/Perf.img/dtrsm_s9150_k40.png>
  - WebSearch: FirePro S9150 peak single precision TFLOPS vs Tesla K40 (snippets: AMD press release 5.07 TFLOPS SP / 2.53 DP; K40 4.29 SP / 1.43 DP)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/clmathlibraries/clblas`) · [data/wave8/enrich/raw/github_com_clmathlibraries_clblas.json](../../../data/wave8/enrich/raw/github_com_clmathlibraries_clblas.json) (enrichment confidence 0.7)

</details>
