# alpaka (alpaka3 BabelStream)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MPL-2.0` · 🟢 active

> Header-only C++20 single-source kernel layer (CUDA, HIP, SYCL, OpenMP, TBB) matching native BabelStream bandwidth on GH200 and Grace.

| | |
|---|---|
| **Beats** | NVIDIA reference BabelStream implementation (native OpenMP on Grace CPU, native CUDA on GH200 GPU) |
| **Claimed result** | On NVIDIA Grace CPU (OpenMP, 72 threads, GNU 14.3, -ftree-vectorize -mcpu=neoverse-v2): alpaka3 reaches 107% of the NVIDIA reference throughput on average over Copy/Mult/Add/Triad (alpaka3 Copy 469, Mult 469, Add 453, Triad 456 GB/s; reference bars about 455, 458, 408, 408 GB/s and mainline alpaka about 450, 452, 428, 423 GB/s, derived from page data: bar heights in the SVG scaled by the labelled alpaka3 values). Dot 447 GB/s for alpaka3 versus 40 GB/s for mainline alpaka; no Dot reference. On NVIDIA GH200 GPU (CUDA 13.3): 99% of the NVIDIA reference on average (alpaka3 Copy 3,636, Mult 3,634, Add 3,665, Triad 3,667 GB/s; reference bars about 3,663, 3,664, 3,735, 3,731 GB/s, derived from page data), i.e. parity, not a win; Dot 3,731 GB/s versus 3,678 GB/s for mainline alpaka. |
| **Workload** | BabelStream Copy/Mult/Add/Triad/Dot memory-bandwidth kernels, double precision, 1.073742 billion elements, run through alpaka3's portable kernel API versus native reference code and mainline alpaka. |
| **Metric** | throughput |
| **Hardware** | JUPITER at the Juelich Supercomputing Centre: NVIDIA Grace CPU (72 OpenMP threads) and NVIDIA GH200 GPU |
| **Compiler and flags** | CPU run: GNU 14.3, -ftree-vectorize -mcpu=neoverse-v2 (from chart footer); GPU run: CUDA 13.3, flags not stated |
| **Adoption** | 428 stars (alpaka-group/alpaka, default branch dev_v3.x) |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/alpaka-group/alpaka) · [benchmark](https://github.com/alpaka-group/alpaka) |

## Verdict

First-party README charts from JUPITER (Juelich): on a Grace CPU (OpenMP, 72 threads, GNU 14.3, -ftree-vectorize -mcpu=neoverse-v2) alpaka3's BabelStream port reaches 469/469/453/456 GB/s on Copy/Mult/Add/Triad, 107% of an unnamed NVIDIA reference on average (reference bars about 455/458/408/408 GB/s, derived from page data); on a GH200 GPU (CUDA 13.3, flags not stated) it reaches 3,636 to 3,667 GB/s, 99% of the reference, i.e. parity. Dot has no reference; versus mainline alpaka it is 447 vs 40 GB/s on the CPU and 3,731 vs 3,678 GB/s on the GPU, all double precision at 2^30 elements.

## Use it when

- You maintain a C++ code that must run on NVIDIA, AMD and Intel GPUs plus multi-core CPUs and want one kernel source instead of CUDA, HIP, SYCL and OpenMP variants.
- Memory-bound streaming kernels (copy, scale, add, triad, dot style) where the target is native-code bandwidth: the project shows 99% of the NVIDIA reference on a GH200 GPU and 107% on a Grace CPU with 72 OpenMP threads.
- HPC codes already built around alpaka (the group's particle-in-cell work is cited in CITATION.cff) that want the alpaka3 SIMD/frame API and its CPU dot-product fix (447 GB/s vs 40 GB/s for mainline alpaka on Grace).
- Teams that want to unit-test GPU kernels on a CPU-only CI machine with the serial or OpenMP backend.

## Skip it when

- You need dense linear algebra (GEMM, LU, QR): alpaka provides no BLAS routines; use a vendor BLAS, OpenBLAS, BLIS or CLBlast.
- You need a stable, released API today: alpaka3 has no release tag (CITATION.cff says 3.0.0, the latest tag is mainline 2.2.0 from 2026-10-08), and its install docs still point to alpaka-group/alpaka3 branch dev.
- Compute-bound kernels that depend on vendor-specific features (tensor cores, warp intrinsics, cooperative groups): BabelStream only shows bandwidth parity, and explicit shared-memory caching is left to the kernel author.
- Windows or macOS builds: the README badge lists Linux only.
- Codes that need bitwise-reproducible reductions: the docs say thread reordering makes deterministic results impossible to guarantee, and issue #2434 (open) notes dot-product verification drift on single-threaded backends.

## How it is fast

Kernels are compiled straight to the native model of each backend, so there is no runtime dispatch layer in the hot loop. alpaka3's index domain is split into equally sized frames, and onAcc::SimdAlgo::concurrent walks each frame with explicit SIMD packs (load, fill, vector arithmetic) per worker thread, which lets compilers emit wide loads and stores on CPUs where mainline alpaka's one-element-per-thread mapping did not. The BabelStream port uses 512 threads per block and a per-device elements-per-thread factor; reductions go through the library's transformReduce.

## Compared with alternatives

None of the blas-lapack siblings is a kernel-portability layer: pick alpaka when you write your own kernels and need one source for CUDA, HIP, SYCL and OpenMP; pick CLBlast or a vendor BLAS (OpenBLAS, MKL, cuBLAS) when what you need is GEMM-class routines.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the core; CMake 3.25+ (alpaka_finalize target helper); the CUDA Toolkit, ROCm/HIP, oneAPI, OpenMP or TBB for the chosen backend; Catch2 for tests and benchmarks |
| **Minimum toolchain** | C++20 (g++, clang++, nvcc or icpx); CMake 3.25; the GPU chart used CUDA 13.3 and the CPU chart GNU 14.3 |
| **Platforms** | Linux; x86, ARM, RISC-V and Power8+ CPUs; NVIDIA, AMD and Intel GPUs |
| **Thread safety** | not documented beyond the queue/event model (work is ordered within a queue; separate queues may run concurrently); recent commits fix deadlocks in blocking host queues |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness asymmetry: the alpaka3 BabelStream port (benchmark/babelstream/src/babelStreamCommon.hpp) computes bandwidth from the minimum time over runs 2..N, while the GPU chart says the NVIDIA reference values are 'the mean of supplied runs'; neither chart names the reference code, its flags or its run count, so the 107%/99% ratios compare best-of-N against figures of unknown aggregation that the project did not re-run.
- The Grace CPU reference bars (about 408 GB/s for Add and Triad) sit at or below the low end of NVIDIA's own expected STREAM Triad range for a GH200 Grace with 72 threads (410 to 486 GB/s, from a search snippet of NVIDIA's Grace tuning guide; the page itself was unreachable), while alpaka3's 456 GB/s sits inside it, so the 7% CPU win may reflect a weak reference run rather than a better kernel.
- In the same harness the NStream kernel (a += b + scalar\*c touches four arrays) is credited with only two arrays of traffic, so its reported bandwidth is half the true figure; the README charts do not use NStream.
- The benchmark sources carry BabelStream's licence, whose clause 3b requires results from modified code to be labelled as a BabelStream variant; the README charts are titled 'BabelStream performance' without that label.

## Known shortcomings

- alpaka is a portability layer, not a thread pool; its alpaka3 BabelStream numbers (GPU at parity, 99% of the NVIDIA reference on GH200; CPU about 7% faster on Grace) were read from README SVG bar heights, the NVIDIA reference results were supplied rather than re-run, and the reference code and flags are unstated. Filed under blas-lapack (STREAM-style vector kernels).
- Enricher: BabelStream bandwidth is the minimum over runs 2..N (babelStreamCommon.hpp) while the GPU native reference is the 'mean of supplied runs', not re-run, with code and flags unnamed; the Grace reference Add/Triad about 408 GB/s sits at the low end of NVIDIA's own STREAM Triad range (410-486 GB/s, snippet only) and alpaka3's 456 is inside it, so the 7% CPU win may be a weak baseline; NStream credits 2 arrays instead of 4 (bandwidth reported at half, not charted); alpaka3 is unreleased (no tag, latest 2.2.0 is mainline); open issue #2434 (dot verification).
- Domain set to numerics-and-science to match its blas-lapack category.

## Caveats and trade-offs

The numbers exist only as two matplotlib SVG charts embedded in the README (labels are rendered as glyph paths; the labelled values are readable from the SVG's text comments, unlabelled reference bars only from bar geometry). The GPU chart says 'Native results are the mean of supplied runs', so the NVIDIA reference was not re-run by the project, and neither chart names the reference code, its build or its flags. The GPU run states no flags. Benchmark source is public in benchmark/babelstream (with run commands in benchmark/babelstream/src/README.md, carrying BabelStream's own licence with publication restrictions), but the JUPITER run configuration is not given. The GPU result is parity (99%), only the CPU run is faster (107%, i.e. about 7%, mostly on Add and Triad), and Dot has no reference. The old listed repo ComputationalRadiationPhysics/alpaka now only redirects to alpaka-group/alpaka, and the listed LGPLv3+ licence is outdated (now MPL-2.0). Only memory-bandwidth kernels are measured, no thread-pool or scheduling workload; alpaka is a performance-portability kernel abstraction library, so thread-pools-work-stealing is the wrong category.

Single-source performance-portability layer (CUDA, HIP, SYCL, OpenMP, serial backends) that has to match hand-written native kernels; alpaka3 on the default branch is a redesign with a different API from mainline alpaka. Explicit shared-memory caching is left to the kernel author.

## Maintenance

Actively developed (dev_v3.x commits on 2026-10-01, 214 open issues, 428 stars) and MPL-2.0, but alpaka3 is unreleased and its API differs from the released 2.x line, so pin a commit if you adopt it now.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README charts (docs/images/babelstream-grace-cpu.svg and babelstream-gh200-gpu.svg) compare alpaka3 against NVIDIA reference results; the alpaka benchmark code is public (benchmark/babelstream/src) and the CPU chart names GNU 14.3 and its flags, but the reference bars were not run from public code with stated flags ('Native results are the mean of supplied runs' on the GPU chart), so the baseline comparison is not reproducible and stays C.
- **Verifier notes:** Labelled values in both SVGs match the record exactly (text comments in the matplotlib SVGs); I derived the unlabelled reference and mainline bars from bar geometry. Shortcomings: wrong category (portability layer, not a thread pool; consider a category override); GPU is parity, CPU win about 7%; baseline numbers supplied rather than re-run, reference code and flags unstated. Metadata: MPL-2.0, 428 stars, branch dev_v3.x, last commit 2026-10-01, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-56 (wave 11); enricher w11 pair-018; orchestrator domain fix 2026-10-11
- **Pages the verifier opened:**
  - <https://github.com/alpaka-group/alpaka>
  - <https://github.com/alpaka-group/alpaka/commits/dev_v3.x>
  - <https://raw.githubusercontent.com/alpaka-group/alpaka/dev_v3.x/docs/images/babelstream-grace-cpu.svg>
  - <https://raw.githubusercontent.com/alpaka-group/alpaka/dev_v3.x/docs/images/babelstream-gh200-gpu.svg>
  - <https://github.com/alpaka-group/alpaka/tree/dev_v3.x/benchmark/babelstream>
  - <https://github.com/alpaka-group/alpaka/tree/dev_v3.x/benchmark/babelstream/src>
  - <https://raw.githubusercontent.com/alpaka-group/alpaka/dev_v3.x/benchmark/babelstream/CMakeLists.txt>
  - <https://raw.githubusercontent.com/alpaka-group/alpaka/dev_v3.x/benchmark/babelstream/src/README.md>
  - <https://raw.githubusercontent.com/alpaka-group/alpaka/dev_v3.x/benchmark/babelstream/src/LICENSE>
  - <https://raw.githubusercontent.com/alpaka-group/alpaka/dev_v3.x/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/alpaka-group/alpaka>
  - <https://raw.githubusercontent.com/alpaka-group/alpaka/dev_v3.x/README.md>
  - <https://raw.githubusercontent.com/alpaka-group/alpaka/dev_v3.x/LICENSE>
  - <https://raw.githubusercontent.com/alpaka-group/alpaka/dev_v3.x/CMakeLists.txt>
  - <https://raw.githubusercontent.com/alpaka-group/alpaka/dev_v3.x/CITATION.cff>
  - <https://github.com/alpaka-group/alpaka/tree/dev_v3.x/benchmark/babelstream/src>
  - <https://raw.githubusercontent.com/alpaka-group/alpaka/dev_v3.x/benchmark/babelstream/CMakeLists.txt>
  - <https://raw.githubusercontent.com/alpaka-group/alpaka/dev_v3.x/benchmark/babelstream/src/README.md>
  - <https://raw.githubusercontent.com/alpaka-group/alpaka/dev_v3.x/benchmark/babelstream/src/LICENSE>
  - <https://raw.githubusercontent.com/alpaka-group/alpaka/dev_v3.x/benchmark/babelstream/src/babelStreamCommon.hpp>
  - <https://raw.githubusercontent.com/alpaka-group/alpaka/dev_v3.x/benchmark/babelstream/src/babelStreamMainTest.cpp>
  - <https://raw.githubusercontent.com/alpaka-group/alpaka/dev_v3.x/docs/images/babelstream-grace-cpu.svg>
  - <https://raw.githubusercontent.com/alpaka-group/alpaka/dev_v3.x/docs/images/babelstream-gh200-gpu.svg>
  - <https://github.com/alpaka-group/alpaka/tree/dev_v3.x/docs>
  - <https://github.com/alpaka-group/alpaka/tree/dev_v3.x/docs/source>
  - <https://github.com/alpaka-group/alpaka/tree/dev_v3.x/docs/source/basic>
  - <https://raw.githubusercontent.com/alpaka-group/alpaka/dev_v3.x/docs/source/basic/install.rst>
  - <https://raw.githubusercontent.com/alpaka-group/alpaka/dev_v3.x/docs/source/basic/intro.rst>
  - <https://raw.githubusercontent.com/alpaka-group/alpaka/dev_v3.x/docs/source/basic/library.rst>
  - <https://raw.githubusercontent.com/alpaka-group/alpaka/dev_v3.x/docs/source/basic/cheatsheet.rst>
  - <https://raw.githubusercontent.com/alpaka-group/alpaka/dev_v3.x/docs/source/basic/abstraction.rst>
  - <https://github.com/alpaka-group/alpaka/tags>
  - <https://github.com/alpaka-group/alpaka/commits/dev_v3.x>
  - <https://github.com/alpaka-group/alpaka/issues?q=is%3Aissue%20babelstream>
  - <https://github.com/alpaka-group/alpaka/issues/2434>
  - <https://github.com/alpaka-group/alpaka/issues/1875>
  - <https://github.com/alpaka-group/alpaka3>
  - WebSearch: NVIDIA Grace CPU BabelStream OpenMP results (snippets of docs.nvidia.com/grace-perf-tuning-guide/health-checks.html; the page itself returned ENOTFOUND)
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/alpaka-group/alpaka`) · [data/wave11/enrich/raw/github_com_alpaka_group_alpaka.json](../../../data/wave11/enrich/raw/github_com_alpaka_group_alpaka.json) (enrichment confidence 0.6)

</details>
