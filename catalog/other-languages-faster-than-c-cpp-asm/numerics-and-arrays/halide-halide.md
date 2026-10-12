# Halide

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> C++-embedded DSL compiling image/array pipelines via LLVM; team's 2013 results beat expert C++, NEON and CUDA 1.1-4.4x.

| | |
|---|---|
| **Beats** | Expert hand-tuned C++ (OpenMP + Intel IPP), ARM NEON intrinsics/assembly and CUDA implementations of the same image-processing pipelines used as baselines in the PLDI 2013 paper (local Laplacian filters, bilateral grid, camera pipe, etc.) |
| **Claimed result** | PLDI 2013 table as reproduced in the team's CVPR 2015 tutorial slides (halide/halide.github.com, assets/lectures/Halide_CVPR_intro.pdf), Halide over hand-tuned expert implementations: x86 blur 1.2x, bilateral grid 4.4x, camera pipeline 3.4x, healing brush 1.7x, local Laplacian 1.7x; ARM camera pipeline 1.1x; GPU bilateral grid 2.3x, and GPU healing brush 5.9x and local Laplacian 9x against CPU expert code (asterisked, GPU-vs-CPU). Abstract: up to 5x faster than hand-tuned C, intrinsics and CUDA. |
| **Workload** | Image-processing pipelines written once as an algorithm plus a separate schedule (tiling, fusion, vectorization, parallelism): local Laplacian filters (99 stages) and bilateral grid on quad-core x86, plus camera raw pipe and others on ARM/CUDA, versus the hand-tuned expert code for the same pipelines. |
| **Metric** | throughput |
| **Hardware** | Quad-core x86 desktop, ARM and CUDA GPU platforms (exact CPU models not confirmed; paper PDF could not be opened) |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | Decouples the algorithm from its schedule: the programmer or autoscheduler explores loop tiling, producer-consumer fusion, recomputation vs storage, vectorization and parallelism without rewriting the algorithm, which finds locality/parallelism trade-offs that were too laborious to hand-code in C++. |
| **Adoption** | 6.6k stars |
| **Last commit** | 2026-10-09 |
| **Links** | [repository](https://github.com/halide/Halide) · [benchmark](https://people.csail.mit.edu/jrk/halide-pldi13.pdf) |

## Verdict

Per the Halide team's 2015 tutorial slides reproducing the PLDI 2013 results (paper PDF itself blocked here), Halide schedules ran 1.2-4.4x faster than expert multi-threaded SSE C++ on a quad-core x86 (bilateral grid 4.4x, camera pipe 3.4x, local Laplacian 1.7x, blur 1.2x), 1.1x faster than the hand-tuned camera pipe on ARM, and 2.3x faster than hand-written CUDA for the bilateral grid; the 5.9x and 9x GPU rows are measured against CPU expert code. CPU models, compilers and flags are not stated in what could be read.

## Use it when

- Multi-stage stencil or image pipelines (blurs, pyramids, demosaic, local Laplacian, bilateral grid, resampling) where intermediate buffers kill cache locality in straightforward C++
- You need one algorithm to run well on x86 SIMD, ARM NEON, Hexagon HVX and a GPU without maintaining a separate intrinsics or CUDA version per target
- Throughput-bound batch or camera processing on multi-megapixel frames where a few ms per frame matters (the team's 2015 slides cite Google HDR+, Photos auto-enhance and Android use)
- Teams that can afford an AOT build step (generators) and want a C-ABI static library with no LLVM at runtime

## Skip it when

- General code with data-dependent control flow, pointer-chasing or irregular data structures; Halide covers rectangular array pipelines only
- Small one-off kernels where a library call (IPP, OpenCV, BLAS, FFTW) already exists: the project's own slides show BLAS only at parity with Eigen (1x) and the bundled FFT only 1.5x over FFTW
- Projects that cannot take an LLVM dependency at build time (the compiler needs LLVM 21-23 at the time of writing; JIT also needs it at runtime)
- When nobody will tune schedules: parallelism, vectorization and fusion come only from the schedule (apps/blur spells out .parallel and .vectorize per target), autoscheduler quality varies by pipeline, and its GPU support is labelled experimental (issue #8640)
- Latency-critical GPU use measured with the bundled halide_benchmark.h, which its header and issue #2278 warn is misleading for GPU code

## How it is fast

The schedule language makes locality and parallelism trade-offs cheap to explore: compute_at/store_at give producer-consumer fusion, sliding windows and recompute-versus-store choices, split/vectorize/parallel give tiling, SIMD and threading, and gpu_tile maps the same algorithm to CUDA, OpenCL, Metal, Vulkan or D3D12. The compiler infers bounds, lowers to LLVM IR and emits SIMD for SSE/AVX, NEON, HVX and others. Schedules come from an expert or an autoscheduler (Mullapudi2016, Adams2019, Li2018); the wins over hand code come from fused, tiled loop organizations that are too laborious to hand-write, not from better codegen of the same loop nest.

## Compared with alternatives

Pick Halide over Futhark when the workload is a stencil or image pipeline that must be called from C++ and run well on CPU SIMD, mobile DSPs and GPUs from one source; pick Futhark for general nested data-parallel GPU programs. For a single small FFT or BLAS call, a tuned library (or FFTA.jl in Julia) is simpler, since Halide's own figures show only 1.5x over FFTW and parity with Eigen.

## Integration

| | |
|---|---|
| **Form** | static lib (AOT generator output: .a/.o plus C-ABI header) or shared lib (libHalide for JIT); pip wheels halide / halide-bin / halide-runtime |
| **Dependencies** | LLVM (21, 22 or 23, plus clang and lld) to build the compiler; CMake 3.28+; optional Python 3.9+ and pybind11 for bindings; generated AOT pipelines need only the small Halide runtime |
| **Minimum toolchain** | C++17; tested hosts GCC 9.5/11.4, MSVC 2022, AppleClang 14-15 |
| **Platforms** | Targets x86 (SSE/AVX), ARM/AArch64 (NEON), Hexagon HVX, PowerPC, RISC-V, WebAssembly; GPUs via CUDA, OpenCL, Metal, Vulkan, Direct3D 12; hosts Linux, Windows, macOS, Android, iOS, QuRT |
| **Thread safety** | Not documented in the README; generated pipelines use a shared runtime thread pool sized by HL_NUM_THREADS (default: host core count, max 256) |
| **Drop-in for the baseline** | no |

## Gotchas

- Paper table now attributable from the team's first-party CVPR 2015 tutorial slides (halide/halide.github.com, assets/lectures/Halide_CVPR_intro.pdf): x86 blur 1.2x, bilateral grid 4.4x, camera pipeline 3.4x, 'healing brush' 1.7x, local Laplacian 1.7x; ARM camera pipeline 1.1x; GPU bilateral grid 2.3x, healing brush 5.9x\*, local Laplacian 9x\*. The record's pairing of 5.9x with bilateral grid is wrong: 5.9x is the asterisked GPU 'healing brush' row, and the asterisked GPU rows compare Halide on a GPU against the CPU expert code (the local Laplacian slide spells out 'GPU: 9x faster (vs. Adobe)', Adobe's code being multi-threaded SSE C++), which is why 5.9x exceeds the abstract's 'up to 5x'.
- First-party figures disagree with each other: the same slide deck gives local Laplacian as 1.7x in the results table but '2x faster (vs. Adobe)' (and 20x vs a 300-line reference C++) in the narrative slide; the 2.1x in the record's snippet could not be matched to either.
- Harness flaw in the repo's only C++-baseline image app, apps/blur/test.cpp: the 'naive' baseline is a single-threaded scalar loop, and the hand-written SSE/NEON blur_fast uses '#pragma omp parallel for' but the Makefile adds -fopenmp only when \$(CXX) is not clang, so on clang/macOS builds the intrinsics baseline runs single-threaded against Halide's .parallel(y) schedule; the program prints three unlabelled times and the output check skips a 64-pixel border.
- The paper's expert baselines (hand-tuned camera pipe, Adobe's local Laplacian, IPP-based C++) are not in the repo; apps/local_laplacian, bilateral_grid and camera_pipe now time only manual versus autoscheduled Halide, so no current number against C++ can be reproduced from the repo except apps/fft (single-threaded FFTW_EXHAUSTIVE, 16x16 and 32x32) and cuda_mat_mul (cuBLAS).

## Known shortcomings

- PLDI 2013 numbers seen only in search snippets; the 2.1x/5.9x rows are not tied to specific apps, the local Laplacian baseline uses Intel IPP, and the win comes from scheduling and autotuning rather than codegen; no harness in the repo (apps/blur/test.cpp times naive C++, SSE intrinsics and Halide but publishes no numbers).
- The paper table is attributable from the team's CVPR 2015 slides (halide/halide.github.com, assets/lectures/Halide_CVPR_intro.pdf): x86 blur 1.2x, bilateral grid 4.4x, camera pipeline 3.4x, healing brush 1.7x, local Laplacian 1.7x; ARM camera pipeline 1.1x; GPU bilateral grid 2.3x, healing brush 5.9x and local Laplacian 9x, where the asterisked rows put Halide's GPU schedule against CPU expert code (GPU-vs-CPU asymmetry). The record's 5.9x was mis-attributed to bilateral grid and its 2.1x is unmatched (the slides say 1.7x in the table and '2x vs Adobe' in the narrative). Repo harness flaw: apps/blur/test.cpp's naive baseline is single-threaded and the Makefile adds -fopenmp only for non-clang, so on clang the SSE baseline is single-threaded against Halide's .parallel(y); the paper baselines are absent from the repo.

## Caveats and trade-offs

Numbers come only from WebSearch snippets of the PLDI 2013 paper (Ragan-Kelley et al.; the PDF hosts are blocked here, so the table was never opened); the snippet tool said the table text was garbled, so the row attributions (2.1x local Laplacian, 5.9x bilateral grid) are inferred, and the 5.9x row exceeds the abstract's 'up to 5x' without explanation. The baselines are the authors' 2012-13 expert implementations on 2012 hardware with CPU models, compilers and flags unconfirmed. The local Laplacian baseline calls Intel IPP library routines, so part of that comparison is Halide against a vendor library rather than against hand-written C++. The algorithm is the same mathematical pipeline on both sides, but the win comes from a different loop organization (fusion, tiling, recomputation, vectorization and parallelism chosen by the schedule and an autotuner), not from better code generation for the same loop nest. The repo does not carry the paper's baselines or harness; apps/blur/test.cpp does time naive C++, hand-written SSE intrinsics (blur_fast) and Halide side by side but publishes no numbers (enrichment lead). Halide is a C++-embedded DSL compiled through LLVM, so pipelines are callable directly from C++. License is MIT for the core; apps/bgu is Apache-2.0 (both OSI). [retier] The record's earlier 5.9x was mis-attributed to bilateral grid (it is GPU healing brush, against CPU expert code) and its 2.1x is unmatched (the slides say 1.7x in the table and '2x vs Adobe' in the narrative). The asterisked GPU rows compare Halide's GPU schedule with CPU expert code (GPU-vs-CPU asymmetry). Repo harness flaw: apps/blur/test.cpp's naive baseline is single-threaded and the Makefile adds -fopenmp only for non-clang, so on clang the SSE baseline is single-threaded against Halide's .parallel(y); the paper baselines are absent from the repo.

Embedded DSL: requires writing a Halide pipeline and a schedule (C++17 API or Python bindings), ahead-of-time or JIT compiled through LLVM; schedule quality depends on the expert or autoscheduler; image/array pipelines only, not general code. LICENSE.txt is MIT with apps/bgu under Apache-2.0.

## Maintenance

Very active (last commit 2026-10-09 per the verifier; PyPI release 21.0.0 on 2025-09-16, nightly wheels on pypi.halide-lang.org), MIT-licensed core with apps/bgu under Apache-2.0, used in Google imaging products per the team's slides; evidence remains first-party 2013-2015 figures with the expert baselines absent from the repo.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now C.
- **Tier reason:** The PLDI 2013 paper is peer reviewed, but every host carrying it (people.csail.mit.edu, commit.csail.mit.edu, courses.cs.washington.edu, web.eecs.umich.edu, dspace.mit.edu) is blocked here, so its numbers were seen only in WebSearch snippets; under the wave-14 rule snippet-only paper numbers stay tier C. The repository carries neither the expert baselines nor the paper harness.
- **Verifier notes:** Downgrade B to C: paper numbers seen only through search snippets and rows not attributable; the record's caveats already admitted this. Shortcomings: snippet-only paper numbers, 2012-era baselines with unknown flags and CPUs, IPP library calls in the local Laplacian baseline, win comes from schedule (loop organization plus autotuning) rather than codegen, no reproducible harness in the repo. Not a duplicate: Halide is not otherwise listed (halidecx/\* entries in wave 10 are unrelated). Metadata checked: MIT, 6.6k stars, last commit 2026-10-09, active.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-03 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/halide/Halide>
  - <https://github.com/halide/Halide/commits>
  - <https://raw.githubusercontent.com/halide/Halide/HEAD/README.md>
  - <https://raw.githubusercontent.com/halide/Halide/main/LICENSE.txt>
  - <https://raw.githubusercontent.com/halide/Halide/main/apps/blur/test.cpp>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/halide/Halide/main/README.md>
  - <https://raw.githubusercontent.com/halide/Halide/main/LICENSE.txt>
  - <https://raw.githubusercontent.com/halide/Halide/main/apps/blur/test.cpp>
  - <https://raw.githubusercontent.com/halide/Halide/main/apps/blur/halide_blur_generator.cpp>
  - <https://raw.githubusercontent.com/halide/Halide/main/apps/blur/Makefile>
  - <https://raw.githubusercontent.com/halide/Halide/main/apps/local_laplacian/process.cpp>
  - <https://raw.githubusercontent.com/halide/Halide/main/apps/local_laplacian/Makefile>
  - <https://raw.githubusercontent.com/halide/Halide/main/apps/local_laplacian/local_laplacian_generator.cpp>
  - <https://raw.githubusercontent.com/halide/Halide/main/apps/bilateral_grid/filter.cpp>
  - <https://raw.githubusercontent.com/halide/Halide/main/apps/bilateral_grid/Makefile>
  - <https://raw.githubusercontent.com/halide/Halide/main/apps/camera_pipe/process.cpp>
  - <https://raw.githubusercontent.com/halide/Halide/main/apps/fft/main.cpp>
  - <https://raw.githubusercontent.com/halide/Halide/main/apps/fft/fft.cpp>
  - <https://raw.githubusercontent.com/halide/Halide/main/apps/fft/fft.h>
  - <https://raw.githubusercontent.com/halide/Halide/main/apps/fft/Makefile>
  - <https://raw.githubusercontent.com/halide/Halide/main/apps/cuda_mat_mul/runner.cpp>
  - <https://raw.githubusercontent.com/halide/Halide/main/tools/halide_benchmark.h>
  - <https://github.com/halide/Halide/tree/main/apps>
  - <https://github.com/halide/Halide>
  - <https://github.com/halide/Halide/issues?q=is%3Aissue+is%3Aopen+performance+regression>
  - <https://github.com/orgs/halide/repositories>
  - <https://github.com/halide/halide.github.com/tree/master/assets/lectures>
  - <https://raw.githubusercontent.com/halide/halide.github.com/master/assets/lectures/Halide_CVPR_intro.pdf>
  - <https://pypi.org/pypi/halide/json>
  - https://people.csail.mit.edu/jrk/halide-pldi13.pdf (EGRESS_BLOCKED)
  - https://commit.csail.mit.edu/papers/2018/p106-ragan-kelley.pdf (EGRESS_BLOCKED)
  - https://halide-lang.org/assets/lectures/Halide_CVPR_intro.pdf (blocked; same file read via raw.githubusercontent.com)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/halide/halide`) · [data/wave14/enrich/raw/github_com_halide_halide.json](../../../data/wave14/enrich/raw/github_com_halide_halide.json) (enrichment confidence 0.7)

</details>
