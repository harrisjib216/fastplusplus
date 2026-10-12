# gpuNUFFT

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `CUDA C++` · `MIT` · 🔴 abandoned

> CUDA gridding/NUFFT library for 2D/3D non-Cartesian MRI with MATLAB and Python front ends; GPU alternative to CPU NUFFTs.

| | |
|---|---|
| **Beats** | cuFINUFFT (3D, single-coil and 32-coil MRI data, as measured in cufinufft issue #126, Jan 2022); CPU NUFFT libraries only directionally via the MRI-NUFFT benchmark statement |
| **Claimed result** | cufinufft issue #126 (paquiteau, Jan 28 2022), 3D 128x128x160: forward 73.42 +/- 1.119 ms vs cufinufft 279.36 +/- 0.552 ms (3.8x), adjoint 62.73 +/- 0.640 vs 132.27 +/- 0.697 ms (2.1x); 32 coils (32x128x128x160): forward 1582.74 +/- 3.853 vs 8952.54 +/- 2.771 ms (5.65x), adjoint 1739.30 +/- 10.767 vs 4159.96 +/- 5.939 ms (2.39x). The ratios are the reporter's own. The reporter adds that 'cufiNUFFT remains faster for 2D data' and gives no 2D numbers. |
| **Workload** | GPU gridding / NUFFT of arbitrary 2D and 3D non-Cartesian MRI k-space data (MATLAB mex and Python bindings). No benchmark workload found. |
| **Metric** | throughput |
| **Hardware** | Not stated in issue #126 (results produced in a Google Colab notebook, https://colab.research.google.com/drive/1IuOgwshEG04GVaZoinZNdbRkPmG-Kadp, not opened). The cuFINUFFT paper's harness (MelodyShih/cuFINUFFT-bench) builds with CUDA 10.0.130 and gcc 7.4.0 and runs gpuNUFFT through its MATLAB interface in single precision; per a WebSearch snippet, the paper's measurements were on a V100. |
| **Compiler and flags** | CUDA Toolkit, CMake 2.8+; README notes it was tested with CUDA 5.0 and gcc 4.6; a later commit adds CUDA 11 support |
| **Adoption** | 85 stars, 37 forks; a gpuNUFFT backend of MRI-NUFFT (JOSS) and pysap-mri; the actively maintained fork chaithyagr/gpuNUFFT is what PyPI gpuNUFFT ships (0.10.8, released 2026-07-08) |
| **Last commit** | 2022-02-06 |
| **Links** | [repository](https://github.com/andyschwarzl/gpuNUFFT) · [benchmark](https://github.com/flatironinstitute/cufinufft/issues/126) |

## Verdict

The repo publishes no speed numbers, and the MRI-NUFFT JOSS paper only says cufinufft and gpuNUFFT performed best in its benchmark, which commits no results; a gpuNUFFT Python-binding author co-wrote that paper. One concrete measurement is in cufinufft issue #126 (Jan 2022, GPU and tolerances unstated, gpuNUFFT timings include host-device copies): forward 73.42 ms vs 279.36 ms and adjoint 62.73 vs 132.27 ms on single-coil 128x128x160, and 1582.74 vs 8952.54 ms and 1739.30 vs 4159.96 ms with 32 coils, while the cuFINUFFT paper reports the opposite direction for general-purpose benchmarks.

## Use it when

- Iterative 3D non-Cartesian MRI reconstruction (CG-SENSE, compressed sensing) with a fixed trajectory, where the one-time sector precomputation is amortized over many forward/adjoint calls.
- Multi-coil 3D data with sensitivity maps and density compensation built into the operator; in a 2022 cufinufft issue (#126) gpuNUFFT ran 2.1x to 5.65x faster than cufinufft on 3D 128x128x160 data with 1 and 32 coils (tolerances not matched, GPU not stated).
- MATLAB-based MRI pipelines that want a drop-in GPU NUFFT operator object.
- Python MRI work through MRI-NUFFT or pysap-mri, installed from PyPI (the gpuNUFFT package built from the chaithyagr fork).

## Skip it when

- General-purpose or 2D NUFFTs with a target accuracy: cuFINUFFT takes an explicit tolerance and, per its paper (seen only as a search snippet), averages 78x faster than gpuNUFFT on type 1 and 5x faster on type 2; the issue #126 reporter also found cufinufft faster in 2D.
- Upstream on current CUDA: the code uses the legacy texture-reference API (texture&lt;&gt; globals, cudaBindTextureToArray), which NVIDIA removed in CUDA 12 (removal known from CUDA release notes, not opened here). Its gencode list stops at sm_75, and CUDA 10/11 build issues (#89, #91) are open. Use the chaithyagr fork, which drops that API and adds sm_80 to sm_120.
- Multi-GPU or concurrent use: one GPU per process (issue #72, open), and the operator state lives in device-global __constant__ symbols (GI, KERNEL[10000]) and global textures.
- Very large 3D problems: indices are 32-bit unsigned int; an overflow on large trajectories (#81) was fixed, while a crash on large 3D matrices (#84) and an out-of-memory report (#68) are still open.
- Codebases without CUDA: there is no CPU fallback; the CPU-side code covers only precomputation.

## How it is fast

Kaiser-Bessel gridding with Beatty et al.'s minimal-oversampling kernel, read from a precomputed radial lookup table held in constant memory or in GPU textures with linear interpolation. Samples are pre-sorted into fixed-size grid sectors (e.g. 8^3) so each thread block caches its sector's data in shared memory and scatters with atomicAdd. A 'balanced' operator precomputes a sector processing order to even out load on clustered trajectories such as radial or spiral centers, and cuFFT does the oversampled FFT.

## Compared with alternatives

Pick gpuNUFFT (preferably the chaithyagr fork) for 3D multi-coil MRI operators with coil sensitivities and density compensation built in, where the one reported head-to-head (cufinufft issue #126) favours it. Pick cuFINUFFT (FINUFFT) for general or 2D NUFFTs with a guaranteed tolerance. TRON's README claims 30x over gpuNUFFT, but only for its own trajectory-optimized radial/spiral use.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | CUDA Toolkit with cuFFT; MATLAB for the default mex build (GEN_MEX_FILES=ON); optional pybind11 Python bindings (GEN_PYTHON_FILES) and Google Test |
| **Minimum toolchain** | C++11, CMake 3.12 (FindCUDA), CUDA 8 to 11 for upstream (README says it was tested with CUDA 5.0 and gcc 4.6); CUDA 12 needs the chaithyagr fork |
| **Platforms** | NVIDIA GPUs only; upstream gencode sm_50 to sm_75 plus compute_52/compute_61 PTX for JIT on newer cards; Linux (gcc) and Windows (Visual Studio 2013 Win64) documented |
| **Thread safety** | not documented; the code keeps per-device global state (__constant__ GI and KERNEL, global texture references), so run one operator at a time per device/process |
| **Drop-in for the baseline** | partial: it replaces a CPU NUFFT operator in MATLAB or MRI-NUFFT pipelines, but it has its own operator API (kernel width, sector width and oversampling, no tolerance), so outputs differ in accuracy and scaling from FINUFFT/NFFT |

## Gotchas

- Accuracy is set indirectly by kernel width and oversampling factor, not by a tolerance, so speed comparisons against FINUFFT or cuFINUFFT must match error levels; issue #101 ('How to determine the scaling?') is open.
- Single precision by default; double precision requires rebuilding with GPU_DOUBLE_PREC=ON.
- Operator construction sorts samples into sectors (CPU or GPU) and must be redone when the trajectory changes; loadPrecomputedGpuNUFFTOperator reuses saved mappings.
- Host-array calls copy data to and from the device each time and return arrays that must be freed manually; for iterative loops use the GpuArray overloads that keep data on the GPU.

## Known shortcomings

- No numbers; the MRI-NUFFT JOSS paper only says it ranks among the fastest. Upstream abandoned; the chaithyagr/gpuNUFFT fork is active and is what PyPI ships (0.10.8, 2026-07-08).
- Uses the legacy texture-reference API that CUDA 12 removed; gencode stops at sm_75; device-global __constant__ state; single GPU only (#72); open crash/OOM issues #84, #68 and CUDA 10/11 build issues #89, #91. Double precision exists via the GPU_DOUBLE_PREC CMake option (the record said single only). The chaithyagr fork drops texture references and adds sm_80 to sm_120. The cuFINUFFT paper (arXiv 2102.08463, snippet only) reports cuFINUFFT 78x faster for type 1 and 5x for type 2.
- Raised D to C (retier-14) on cufinufft issue #126 (closed, no replies): 3D single coil 3.8x forward / 2.1x adjoint and 32 coils 5.65x / 2.39x over cuFINUFFT, with GPU, eps and gpuNUFFT parameters unstated and host-device copies counted only on the gpuNUFFT side. The cuFINUFFT paper (arXiv 2102.08463, blocked) claims the opposite (78x type 1, 5x type 2; harness MelodyShih/cuFINUFFT-bench, CUDA 10.0, gcc 7.4.0).

## Caveats and trade-offs

Tier D: no speed numbers anywhere I could open. README gives install steps only (tested with CUDA 5.0 and gcc 4.6; a 2022 merge adds CUDA 11 support). matlab/demo/run_demo.m and cgsense_phantom_recon_cpu.m time gpuNUFFT forward/adjoint against a CPU NUFFT operator with tic/toc, but no results are committed. The LICENSE cites Knoll et al., Proc ISMRM 2014 p4297 (conference abstract, not opened) and README points to Dropbox 'Supporting material' (not opened). mind-inria/mri-nufft-benchmark commits no results; the MRI-NUFFT JOSS paper source (docs/paper-joss/paper.md in mind-inria/mri-nufft, opened via raw.githubusercontent.com) states only that cufinufft and gpuNUFFT give the best performance in that benchmark, with no numbers; its authors include the gpuNUFFT Python-binding author (Chaithya G R), so it is not fully independent. Published third-party comparisons (for example the cuFINUFFT paper) were not checked; the direction against cuFINUFFT is unknown to me. The upstream repo's last commit is 2022-02-06 (abandoned), but MRI-NUFFT docs name chaithyagr/gpuNUFFT (a GitHub fork, 2 stars, 1,356 commits) as the active fork and PyPI gpuNUFFT 0.10.8 was released 2026-07-08. LICENSE is MIT plus a request to credit the authors and cite the ISMRM abstract in academic work. Baselines FFTW, MKL FFT and KissFFT in the assignment are not what gpuNUFFT is compared with; the relevant incumbents are CPU NUFFTs. [retier] Two sources conflict. (1) cufinufft issue #126 (Jan 2022, user paquiteau, who is not a gpuNUFFT author but works on MRI tooling that later wrapped gpuNUFFT in MRI-NUFFT) measured gpuNUFFT 2.1x to 5.65x faster than cufinufft in 3D. The GPU, the cufinufft eps and the gpuNUFFT kernel width, oversampling and sector width are not stated, so accuracy was probably not matched. Copy accounting is unequal: cufinufft times cover computation and D2H only, while gpuNUFFT times also include H2D, which biases against gpuNUFFT. The reporter says the result contradicts Figure 4 of arXiv 2102.08463 and that cufinufft is still faster in 2D. The issue was closed with no maintainer reply. (2) The peer-reviewed cuFINUFFT paper (Shih et al., PDSEC 2021, arXiv 2102.08463; PDF blocked here, figures from WebSearch snippets only) reports cuFINUFFT about 78x faster than gpuNUFFT on type 1 and 5x faster on type 2 at matched accuracy, with its harness in MelodyShih/cuFINUFFT-bench (gpuNUFFT run via MATLAB, CUDA 10.0, gcc 7.4.0; no results committed). The two may both hold: gpuNUFFT can win on fixed MRI trajectories with its precomputed sector operator and low-accuracy gridding, and lose at higher requested accuracy or on clustered points. Upstream gpuNUFFT is unmaintained since 2022-02; the maintained fork is chaithyagr/gpuNUFFT.

Needs an NVIDIA GPU and CUDA; built primarily around MATLAB mex files (MATLAB required unless the Python bindings are used); NUFFT only (gridding with Kaiser-Bessel style kernels), not a general FFT replacement; single precision.

## Maintenance

Upstream has been abandoned since 2022-02-06, with many open build and crash issues; it is MIT-licensed (with a request to cite Knoll et al., ISMRM 2014), and the maintained chaithyagr fork (PyPI gpuNUFFT, recommended by MRI-NUFFT) is the version to adopt.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification D, tier now C.
- **Tier reason:** No speed numbers on any opened page. The only comparative statement is directional: the MRI-NUFFT JOSS paper source (docs/paper-joss/paper.md) says that, per its benchmark, cufinufft and gpuNUFFT provide the best performances by leveraging CUDA acceleration. matlab/demo/run_demo.m times gpuNUFFT against a CPU NUFFT operator but publishes no results.
- **Retiered** D to C: I opened flatironinstitute/cufinufft issue #126 ('gpuNUFFT is faster than cufiNUFFT in 3D', closed with no comments). There a non-author user (paquiteau, Jan 28 2022) reports mean plus/minus std timings with a shared Colab notebook, showing gpuNUFFT 2.1x to 5.65x faster than cufinufft on 3D MRI data. The GPU, the cufinufft tolerance and the gpuNUFFT parameters are unstated, and the copy accounting is unequal, so this is partial methodology and supports C rather than B. The conflicting peer-reviewed cuFINUFFT paper (arXiv 2102.08463) stayed blocked, so its 78x and 5x figures are snippet-only and cannot set the tier.
- **Verifier notes:** Confirmed D; not rejected because it is a used, cited MRI backend (MRI-NUFFT, pysap-mri, ISMRM 2014) with an independent-ish directional claim in the MRI-NUFFT JOSS paper. Consider pointing the entry, or a note, at the active fork chaithyagr/gpuNUFFT that PyPI ships.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `stars_or_usage`, `caveats`, `hardware`
- **Shortcomings recorded by:** verifier; semi-independent: flatironinstitute/cufinufft issue #126 (Jan 2022, GPU and tolerance unstated) has gpuNUFFT 3D 128x128x160 forward 73.42 vs cuFINUFFT 279.36 ms and adjoint 62.73 vs 132.27 ms (32 coils: 1582.74 vs 8952.54 ms, 1739.30 vs 4159.96 ms), with the gpuNUFFT side including host-device copies and the reporter saying cuFINUFFT is faster in 2D; semi-independent: cufinufft issue #126 (user paquiteau), 2022
- **Pages the verifier opened:**
  - <https://github.com/andyschwarzl/gpuNUFFT>
  - <https://raw.githubusercontent.com/andyschwarzl/gpuNUFFT/HEAD/README.md>
  - <https://raw.githubusercontent.com/andyschwarzl/gpuNUFFT/HEAD/LICENSE>
  - <https://github.com/andyschwarzl/gpuNUFFT/commits/master>
  - <https://github.com/andyschwarzl/gpuNUFFT/tree/master/matlab/demo>
  - <https://raw.githubusercontent.com/andyschwarzl/gpuNUFFT/master/matlab/demo/run_demo.m>
  - <https://raw.githubusercontent.com/andyschwarzl/gpuNUFFT/master/matlab/demo/cgsense_phantom_recon_cpu.m>
  - <https://raw.githubusercontent.com/andyschwarzl/gpuNUFFT/master/matlab/demo/cgsense_phantom_recon.m>
  - <https://github.com/chaithyagr/gpuNUFFT>
  - <https://pypi.org/pypi/gpuNUFFT/json>
  - <https://github.com/mind-inria/mri-nufft>
  - <https://github.com/mind-inria/mri-nufft/tree/master/docs>
  - <https://raw.githubusercontent.com/mind-inria/mri-nufft/master/docs/paper-joss/paper.md>
  - <https://raw.githubusercontent.com/mind-inria/mri-nufft/master/docs/backend.rst>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/andyschwarzl/gpuNUFFT/HEAD/README.md>
  - <https://raw.githubusercontent.com/andyschwarzl/gpuNUFFT/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/andyschwarzl/gpuNUFFT/HEAD/CUDA/CMakeLists.txt>
  - <https://raw.githubusercontent.com/andyschwarzl/gpuNUFFT/HEAD/CUDA/inc/gpuNUFFT_operator.hpp>
  - <https://raw.githubusercontent.com/andyschwarzl/gpuNUFFT/HEAD/CUDA/inc/gpuNUFFT_operator_factory.hpp>
  - <https://raw.githubusercontent.com/andyschwarzl/gpuNUFFT/HEAD/CUDA/inc/config.hpp.cmake>
  - <https://raw.githubusercontent.com/andyschwarzl/gpuNUFFT/HEAD/CUDA/inc/gpuNUFFT_types.hpp>
  - <https://raw.githubusercontent.com/andyschwarzl/gpuNUFFT/master/CUDA/inc/cuda_utils.cuh>
  - <https://raw.githubusercontent.com/andyschwarzl/gpuNUFFT/master/CUDA/inc/gpuNUFFT_kernels.hpp>
  - <https://raw.githubusercontent.com/andyschwarzl/gpuNUFFT/master/CUDA/inc/gpuNUFFT_utils.hpp>
  - <https://raw.githubusercontent.com/andyschwarzl/gpuNUFFT/master/CUDA/src/gpu/std_gpuNUFFT_kernels.cu>
  - <https://raw.githubusercontent.com/andyschwarzl/gpuNUFFT/master/CUDA/src/gpu/atomic/atomic_gpuNUFFT_kernels.cu>
  - <https://github.com/andyschwarzl/gpuNUFFT/tree/master/CUDA/src/gpu>
  - <https://github.com/andyschwarzl/gpuNUFFT/issues?q=is%3Aissue>
  - <https://github.com/andyschwarzl/gpuNUFFT/issues/80>
  - <https://github.com/andyschwarzl/gpuNUFFT/issues/72>
  - <https://raw.githubusercontent.com/chaithyagr/gpuNUFFT/HEAD/README.md>
  - <https://raw.githubusercontent.com/chaithyagr/gpuNUFFT/HEAD/CUDA/CMakeLists.txt>
  - <https://raw.githubusercontent.com/chaithyagr/gpuNUFFT/HEAD/CUDA/src/gpu/std_gpuNUFFT_kernels.cu>
  - <https://github.com/flatironinstitute/cufinufft/issues/126>
  - <https://raw.githubusercontent.com/flatironinstitute/finufft/master/docs/related.rst>
  - <https://raw.githubusercontent.com/flatironinstitute/finufft/master/docs/refs.rst>
  - <https://raw.githubusercontent.com/flatironinstitute/finufft/master/docs/c_gpu.rst>
  - <https://raw.githubusercontent.com/mind-inria/mri-nufft/master/docs/backend.rst>
  - <https://raw.githubusercontent.com/mind-inria/mri-nufft/master/docs/paper-joss/paper.md>
  - <https://github.com/mind-inria/mri-nufft-benchmark>
  - WebSearch snippet: cuFINUFFT paper arXiv 2102.08463 abstract/summary (page not opened; arxiv.org blocked)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/andyschwarzl/gpunufft`) · [data/wave8/enrich/raw/github_com_andyschwarzl_gpunufft.json](../../../data/wave8/enrich/raw/github_com_andyschwarzl_gpunufft.json) (enrichment confidence 0.7)

</details>
