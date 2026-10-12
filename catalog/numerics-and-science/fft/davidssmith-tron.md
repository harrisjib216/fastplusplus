# TRON (TRajectory Optimized NUFFT)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `CUDA` · `MIT` · 🟢 active

> CUDA NUFFT gridding/degridding hard-wired for 2D radial MRI trajectories; paper reports 6-30x over gpuNUFFT, BART and IRT.

| | |
|---|---|
| **Beats** | gpuNUFFT (GPU NUFFT gridding library), Fessler's Image Reconstruction Toolbox (IRT, MATLAB) and BART (the reproduction steps also build BART) |
| **Claimed result** | README: 'TRON is 30x faster than gpuNUFFT (a fast GPU code) and 75x faster than the image reconstruction toolbox (IRT) of Fessler (a ubiquitous CPU-based Matlab code)', with '50% less code than the minimal subset of IRT tested'. The paper abstract, seen only through a WebSearch summary, gives a range: '6-30x faster than the closest competitor, depending on test data set', and over 25x faster than gpuNUFFT; the README's 30x is the top of that range. |
| **Workload** | Non-Cartesian MRI gridding and degridding for radial (linear and golden-angle) trajectories on an Nvidia GPU, the repository for the paper 'Trajectory Optimized Nufft: Faster Non-Cartesian MRI Reconstruction through Prior Knowledge and Parallel Architectures'. |
| **Metric** | throughput |
| **Hardware** | Nvidia CUDA GPU (model not stated on the page) |
| **Compiler and flags** | src/Makefile: nvcc -ccbin gcc-6, -O3 -Wno-deprecated-gpu-targets --use_fast_math -D_FORCE_INLINES -DCUDA_HOST_MALLOC; links cuFFT and cuBLAS. CUDA and gcc versions beyond gcc-6 not stated. |
| **Adoption** | 32 stars |
| **Last commit** | 2026-01-12 |
| **Links** | [repository](https://github.com/davidssmith/TRON) · [benchmark](https://github.com/davidssmith/TRON) |

## Verdict

The README claims 30x over gpuNUFFT and 75x over Fessler's CPU MATLAB IRT for radial gridding; the peer-reviewed MRM 2019 abstract (seen only via search summaries) gives 6-30x over the closest competitor depending on data set and calls TRON the most accurate code tested. Built with nvcc -O3 --use_fast_math against cuFFT; the GPU model and CUDA version are not stated on any page opened.

## Use it when

- Offline or real-time reconstruction of 2D radial MRI (uniform-angle or golden-angle), including stack-of-stars and sliding-window golden-angle series on one Nvidia GPU.
- As a reference design for trajectory-specialised gridding: the 995-line tron.cu shows the gather-with-analytic-trajectory approach that beat general GPU gridders in the MRM 2019 paper.
- Reproducing or extending the MRM 2019 comparison against gpuNUFFT, BART and Fessler's IRT (scripts RUNME1-4 plus git-lfs data).
- Square-image adjoint NUFFT where single precision and a fixed Kaiser-Bessel kernel are acceptable.

## Skip it when

- Arbitrary, spiral or 3D trajectories: only 2D radial is implemented (a -3 'koosh' flag exists but the kernels are 2D); issue #7 asking how to add other trajectories is unanswered since Nov 2024. Use a general NUFFT (cuFINUFFT, gpuNUFFT, BART) instead.
- More than 6 coil channels times repetitions: per-thread accumulators are float2 utmp[MAXCHAN] with MAXCHAN hard-coded to 6, and nothing checks nc\*nt against it.
- Iterative reconstruction: the CGNR path (-i) is commented 'NOT WORKING CORRECTLY YET' in tron.cu.
- Non-square images, double precision, multi-GPU (MULTI_GPU is compiled to 0) or use as an in-process library with several concurrent plans (global static state).
- Production builds on current toolchains without porting: the Makefile pins nvcc -ccbin gcc-6 and the CUDA code dates from 2018-2021.

## How it is fast

The trajectory is computed analytically inside the kernels (angle = pe\*pi/npe or the golden-angle increment), so no trajectory array, presorting or atomic scatter is needed: in gridding each thread owns one Cartesian point (4x4 tiled thread mapping) and gathers, over every spoke, only the radial samples inside a circular band of +/- kernel width around its radius. Density compensation is an analytic ramp (precompensate kernel) instead of an iterative DCF, the Kaiser-Bessel kernel is evaluated on the fly with a polynomial I0 approximation, and float32 math is built with --use_fast_math; cuFFT does the oversampled (2x default) FFT.

## Compared with alternatives

FINUFFT/cuFINUFFT is the general-purpose choice (any trajectory, 1-3D, double precision, maintained library API); pick TRON only when data are strictly 2D radial on an Nvidia GPU and you want the trajectory-specialised, presort-free gather approach, noting that TRON's paper (2019) predates cuFINUFFT and never compared against it. The other FFT siblings (cuFFT alternatives such as VkFFT, tcFFT, TurboFFT) are uniform FFTs and do not address non-Cartesian gridding.

## Integration

| | |
|---|---|
| **Form** | source-drop (CUDA command-line program built with a Makefile) |
| **Dependencies** | CUDA toolkit with cuFFT and cuBLAS; reproduction also needs MATLAB, gpuNUFFT, BART and git-lfs data |
| **Minimum toolchain** | nvcc with gcc-6 host compiler as written in src/Makefile; minimum CUDA version not documented |
| **Platforms** | Linux/Unix with an Nvidia CUDA GPU (single GPU); POSIX headers (unistd.h, err.h) used |
| **Thread safety** | Not thread-safe: plans, streams, device buffers and recon parameters are file-scope static globals; not documented otherwise |
| **Drop-in for the baseline** | no |

## Gotchas

- Channel count is capped silently: gridradial2d accumulates into a fixed 6-element per-thread array while looping over nc\*nt channels, so larger coil arrays overflow it; compress coils to &lt;=6 first.
- The built-in 'Elapsed time' uses clock() (process CPU time) around the whole recon including cuFFT plan creation, allocation and host transfers, not CUDA events; do not compare it directly with kernel-only timings.
- Image size is derived from the readout (nx = ny = nro/2) and images must be square; the pad kernel's '&gt; 0' bounds test drops source row/column 0 in the forward (degridding) path.
- cudaFreeHost(&h_outdata) passes the address of the pointer instead of the pointer at exit, so the pinned buffer is not freed correctly (harmless for the CLI, wrong if reused as library code).

## Known shortcomings

- Paper abstract says 6-30x by data set, so the README's 30x is the best case; GPU model unknown.
- Correctness: only 6 channels fit (MAXCHAN 6) and nothing checks nc\*nt against it, so more coils overflow a per-thread array; the iterative CGNR path (-i) is marked 'NOT WORKING CORRECTLY YET'; cudaFreeHost(&ptr) is wrong; the built-in timer is clock() (CPU time) and includes plan creation; square 2D radial only; never compared against cuFINUFFT; dormant since 2021.

## Caveats and trade-offs

Tier B rests on the Magnetic Resonance in Medicine paper (2019), which could not be opened here (onlinelibrary.wiley.com is blocked); its abstract, seen through WebSearch, gives 6-30x depending on data set, so the README's 30x is the best case. GPU model and CUDA version are not on any page opened, so not tier A. The speedups are for radial-trajectory gridding against gpuNUFFT, BART and IRT, not against FFTW/MKL/KissFFT, and the repository description ('radial Fast Fourier Transform') overstates it as an FFT. The 75x is against CPU MATLAB code. Latest commits (Jan 2026) only zip MATLAB files; the CUDA code dates from 2018-2021. Reproduction needs MATLAB and git-lfs data.

Specialised to radial trajectories and CUDA (needs cuFFT, nvcc); gridding code only, not a general uniform FFT or arbitrary-trajectory NUFFT; reproducing the paper needs MATLAB, BART and gpuNUFFT.

## Maintenance

Effectively dormant: the CUDA code was last changed 2018-2021 and the January 2026 commits only zip MATLAB files; MIT-licensed and small (one \~1000-line .cu file), so it is easy to vendor or study but expect to port the build.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The README quotes 30x vs gpuNUFFT and 75x vs IRT from a peer-reviewed Magnetic Resonance in Medicine paper (2019, doi 10.1002/mrm.27497), and the repository holds the paper's reproduction scripts (src/RUNME1_tron_degrid_phantom.sh, src/RUNME3_tron_grid_all.sh, MATLAB parts in src/matlab_files.tar.gz) with nvcc flags in src/Makefile. No GPU or CPU model is stated on any page opened, so not A.
- **Verifier notes:** README numbers verified verbatim; Makefile and run script opened. Paper unreachable (EGRESS_BLOCKED); range 6-30x taken from a WebSearch summary of the abstract. Metadata matches: MIT (LICENSE opened), 32 stars, 10 forks, 19 commits, last 2026-01-12. Category 'fft' is a stretch (NUFFT gridding), but NUFFT fits the FFT family.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `baseline`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/davidssmith/TRON>
  - <https://raw.githubusercontent.com/davidssmith/TRON/HEAD/README.md>
  - <https://github.com/davidssmith/TRON/commits>
  - <https://github.com/davidssmith/TRON/tree/master/src>
  - <https://raw.githubusercontent.com/davidssmith/TRON/HEAD/src/Makefile>
  - <https://raw.githubusercontent.com/davidssmith/TRON/HEAD/src/RUNME3_tron_grid_all.sh>
  - <https://raw.githubusercontent.com/davidssmith/TRON/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/davidssmith/TRON>
  - <https://raw.githubusercontent.com/davidssmith/TRON/HEAD/README.md>
  - <https://raw.githubusercontent.com/davidssmith/TRON/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/davidssmith/TRON/HEAD/src/Makefile>
  - <https://raw.githubusercontent.com/davidssmith/TRON/HEAD/src/RUNME1_tron_degrid_phantom.sh>
  - <https://raw.githubusercontent.com/davidssmith/TRON/HEAD/src/RUNME3_tron_grid_all.sh>
  - <https://raw.githubusercontent.com/davidssmith/TRON/HEAD/src/tron.cu>
  - <https://raw.githubusercontent.com/davidssmith/TRON/HEAD/src/tron.h>
  - <https://raw.githubusercontent.com/davidssmith/TRON/HEAD/src/ra.h>
  - <https://raw.githubusercontent.com/davidssmith/TRON/HEAD/src/float16.h>
  - <https://github.com/davidssmith/TRON/tree/master/src>
  - <https://github.com/davidssmith/TRON/commits>
  - <https://github.com/davidssmith/TRON/issues?q=is%3Aissue>
  - <https://github.com/davidssmith/TRON/issues/7>
  - WebSearch: 'Trajectory Optimized NUFFT' TRON Smith (summaries of onlinelibrary.wiley.com/doi/full/10.1002/mrm.27497 and researchgate.net/publication/328349262)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/davidssmith/tron`) · [data/wave8/enrich/raw/github_com_davidssmith_tron.json](../../../data/wave8/enrich/raw/github_com_davidssmith_tron.json) (enrichment confidence 0.7)

</details>
