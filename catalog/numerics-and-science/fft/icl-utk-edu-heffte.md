# heFFTe (Highly Efficient FFT for Exascale)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> MPI-distributed 2-D/3-D FFT layer over FFTW, MKL, cuFFT and rocFFT; on GPUs about 2x fftMPI and SWFFT, at parity on CPU.

| | |
|---|---|
| **Beats** | Distributed 3-D FFT libraries fftMPI, SWFFT, AccFFT and P3DFFT (FFTW-MPI-class); FFTW is heFFTe's own CPU backend |
| **Claimed result** | Repo: no competitor numbers; benchmarks/speed3d.h prints only heFFTe's own 'Performance: &lt;x&gt; GFlops/s' for the chosen backend (stock, FFTW, MKL, cuFFT, rocFFT, oneMKL). Peer-reviewed ICCS 2020 paper (seen only through search-result summaries; every copy was EGRESS_BLOCKED): GPU local kernels more than 40x faster than CPU state-of-the-art local kernels and over 2x for the whole FFT; heFFTe GPU about 2x faster than fftMPI and SWFFT; heFFTe beats FFTE by more than a factor of 2 with better scalability; about 90% of roofline peak for a 1024^3 FFT on Summit (6 MPI ranks per node, one V100 per rank). The heFFTe CPU path is built on improved fftMPI/SWFFT kernels and is described as 'at least as good as' them, i.e. parity on CPU. The '1.65x on two nodes' figure in the search record did not appear in any summary I saw. |
| **Workload** | Distributed-memory 2-D/3-D complex FFTs (e.g. 1024^3 on Summit nodes) with pencil or slab decomposition; the repo's speed3d benchmark reports heFFTe's own GFlops/s per backend. |
| **Metric** | throughput |
| **Hardware** | Summit (ORNL): IBM POWER9 CPUs and NVIDIA V100 GPUs, up to 24,576 POWER9 cores and 6,144 V100 GPUs, per the ICCS 2020 paper as summarized in search results; no hardware is stated in the repo. |
| **Adoption** | 59 stars; DOE Exascale Computing Project library (ICL UTK / ORNL) |
| **Last commit** | 2025-11-19 |
| **Links** | [repository](https://github.com/icl-utk-edu/heffte) · [benchmark](https://link.springer.com/chapter/10.1007/978-3-030-50371-0_19) |

## Verdict

Per search-result summaries of the peer-reviewed ICCS 2020 paper (the paper itself was not opened), on Summit (POWER9 plus V100, 6 ranks per node, one GPU per rank) heFFTe on GPUs is about 2x faster than the CPU-only fftMPI and SWFFT, more than 2x faster than FFTE with better scaling, and reaches about 90% of roofline peak for a 1024^3 FFT; its GPU local kernels are more than 40x faster than CPU kernels. Compiler, flags and competitor configurations were not seen. The repo's speed3d benchmark only prints heFFTe's own GFlops/s (5 N log2 N per run) for one backend, while the separate ICL hpfft harness wraps heFFTe, fftMPI, AccFFT, P3DFFT, FFTE, SWFFT, 2DECOMP&FFT, nb3dFFT, FFTW and FFTW++ without publishing results in its README.

## Use it when

- 3-D (or 2-D) FFTs too large for one node or one GPU, e.g. 512^3 to 1024^3+ grids in spectral/pseudo-spectral PDE, MD (PME/P3M) or cosmology codes on multi-GPU clusters
- Codes that must run on NVIDIA (cuFFT), AMD (rocFFT) and Intel (oneMKL) GPUs and on CPUs (FFTW, MKL, built-in stock) from one templated API
- Distributed jobs whose input layout (bricks) differs from the output layout (pencils or slabs): arbitrary non-overlapping per-rank boxes are reshaped for you
- Many same-shaped transforms per step: the batch overloads merge communication buffers to cut latency
- Applications that need distributed DCT/DST (types I and II) next to the FFT, available since 2.4

## Skip it when

- Single-process or single-GPU FFTs: heFFTe is only a communication and decomposition layer, so call FFTW, MKL, cuFFT or VkFFT directly
- CPU-only clusters where you expect a speedup over fftMPI, SWFFT or FFTW-MPI: the paper only claims its CPU path is 'at least as good' as those (parity); the 2x headline compares heFFTe on V100s with CPU-only libraries
- Long-running jobs with repeated r2c/c2r calls on the FFTW backend: open issue #88 shows FFTW plans made on nullptr arrays (in-place) but run out of place, allocating a hidden buffer on every call (+65.9 MB at 200^3, +217.4 MB at 300^3) that size_workspace() does not report; open issue #90 reports MaxRSS growing per forward/backward call in 2.4.1
- Builds without MPI, or a distributed 1-D FFT: MPI is mandatory, and the transforms are 2-D and 3-D only (2-D is a 3-D box of size 1 in one direction)
- One build that targets several GPU vendors: only one of CUDA, ROCm or oneAPI can be enabled per build, and the rocFFT backend has open issues (#82, #78; titles only seen)

## How it is fast

A 3-D FFT is split into batches of local 1-D FFTs (or 2-D FFTs in slab mode), run by a backend (stock, FFTW, MKL, oneMKL, cuFFT or rocFFT), with global reshapes between pencil orientations. Reshapes pack, exchange and unpack with MPI_Alltoallv (the default), padded MPI_Alltoall or pipelined point-to-point Isend/Irecv. use_reorder transposes during unpacking so 1-D FFTs run on contiguous data, use_pencils switches between pencil and slab decomposition, and use_num_subranks/use_subcomm limit how many ranks take part in the reshapes. On GPUs, packing runs on the device and GPU-aware MPI sends device buffers directly, so data stays on the GPU. Batched calls merge communication buffers to cut latency for small signals. Since GPU local FFTs are reported &gt;40x faster than CPU kernels, the remaining cost is mostly communication, which the paper puts at about 90% of roofline peak for 1024^3 on Summit.

## Compared with alternatives

heFFTe is the only catalogued FFT sibling built for distributed-memory 3-D FFTs across many GPUs and nodes; use it when the grid does not fit one device. Use VkFFT, TurboFFT or tcFFT for single-GPU transforms, and FFTW++ for dealiased convolutions on CPU clusters.

## Integration

| | |
|---|---|
| **Form** | shared lib (or static; CMake BUILD_SHARED_LIBS) with a header API (heffte.h) and CMake target Heffte::Heffte |
| **Dependencies** | MPI plus at least one backend: the built-in stock backend, FFTW3 (both fftw3 and fftw3f needed), MKL, oneMKL, cuFFT or rocFFT; optional MAGMA, SWIG/Fortran, Python |
| **Minimum toolchain** | C++11 (cxx_std_11), CMake 3.19+; CI-tested with GCC 11-13, Clang 14-18, dpcpp 2024.2, OpenMPI 4.1.6, FFTW 3.3.7-3.3.10, MKL/oneMKL 2024.2, CUDA 11-12.6, ROCm 5.6-6.2 |
| **Platforms** | Linux HPC systems: x86-64 and POWER9 CPUs (stock backend with optional AVX/AVX512), NVIDIA, AMD and Intel GPUs; one GPU backend per build |
| **Thread safety** | not documented; forward() and backward() are MPI-collective over the plan's communicator, so every rank must call them in the same order |
| **Drop-in for the baseline** | no |

## Gotchas

- The FFTW backend plans every local transform with FFTW_ESTIMATE on nullptr arrays (heffte_backend_fftw.h), so local kernels are untuned and r2c/c2r break FFTW's new-array execute contract (issue #88)
- No scaling by default (scale::none, like FFTW): pass scale::full to backward() (or scale::symmetric to both) to get the input back
- With a GPU backend, GPU-aware MPI is assumed ON at build time (Heffte_ENABLE_GPU_AWARE_MPI); on an MPI without GPU support, turn it off at build time or with plan_options::use_gpu_aware
- The stock backend has no vectorization unless built with -DHeffte_ENABLE_AVX or AVX512 (docs: up to an order of magnitude faster with them), and prime factors below HEFFTE_STOCK_RADER_MIN (100000) fall back to a direct O(p^2) DFT

## Known shortcomings

- The 2x over fftMPI/SWFFT compares GPU heFFTe against CPU-only libraries, so it is mostly a hardware gain; the CPU path is at parity. ICCS 2020 paper known from snippets only (publisher blocked here).
- Open #88: the FFTW backend plans with FFTW_ESTIMATE on nullptr arrays, and r2c/c2r allocate a hidden buffer on each call (+65.9 MB at 200^3, +217 MB at 300^3). Open #90: MaxRSS grows per call in 2.4.1, no maintainer reply. ICL's harness github.com/icl-utk-edu/hpfft has no published results.

## Caveats and trade-offs

The paper (Springer, iccs-meeting.org, icl.utk.edu, netlib.org copies) was EGRESS_BLOCKED, so all figures come from search-result summaries, not from the paper text; compiler, flags and the exact competitor configurations are unverified. The headline 2x over fftMPI and SWFFT compares heFFTe on V100 GPUs with CPU-only libraries (fftMPI and SWFFT have no GPU path), and the 40x compares GPU with CPU kernels, so both are mostly hardware gains; on CPU heFFTe reuses improved fftMPI/SWFFT kernels and is described only as at least as good as them. The FFTE comparison (&gt;2x) is the cleanest software claim but its configuration is unverified. The repo's own benchmarks time heFFTe alone (no head-to-head harness). AccFFT GPU runs reportedly failed correctness on Summit (search-record claim, not re-checked). Docs site (icl-utk-edu.github.io/heffte) is blocked. README 'Getting Help' links to the SLATE issue tracker rather than heFFTe's.

MPI-based distributed FFT; local 1-D/2-D kernels are delegated to FFTW, MKL, oneMKL, cuFFT or rocFFT backends, so heFFTe is a communication/decomposition layer and does not beat FFTW on a single core. Needs MPI and a backend library; also Fortran and Python bindings. Optional GPU-aware MPI.

## Maintenance

Maintained (DOE ECP, ICL UTK/ORNL): last commit 2025-11-19, CMake project version 2.4.1, BSD-3-Clause and copyable; 7 open issues include memory growth (#90) and the FFTW nullptr-plan problem (#88), and the README's 'Getting Help' link points to the SLATE issue tracker rather than heFFTe's.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C: the repo's benchmarks (benchmarks/speed3d.h, speed3d_c2c/r2c/r2r.cpp, convolution.cpp) time only heFFTe with one backend and print its own GFlops/s, but the peer-reviewed ICCS 2020 paper (Springer LNCS, 'heFFTe: Highly Efficient FFT for Exascale') reports, per search-result summaries, heFFTe GPU about 2x faster than fftMPI and SWFFT and more than 2x faster than FFTE on Summit. Not A: the paper could not be opened, and no comparison harness, compiler or flags were seen.
- **Verifier notes:** Kept the search record's metadata (BSD-3-Clause, 59 stars, 28 forks, 967 commits, last commit 2025-11-19, active) after checking the repo and commits pages. Upgrade to B follows the wave's precedent of accepting a peer-reviewed paper seen only through search snippets (ALP, Sputnik, ProxSuite); flag that the fftMPI/SWFFT win is GPU vs CPU. benchmark_url now points to the paper's Springer chapter (URL from search results; blocked here, not opened).
- **Fields the verifier corrected:** `claimed_speedup`, `benchmark_url`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://github.com/icl-utk-edu/heffte>
  - <https://github.com/icl-utk-edu/heffte/commits>
  - <https://github.com/icl-utk-edu/heffte/tree/master/benchmarks>
  - <https://raw.githubusercontent.com/icl-utk-edu/heffte/HEAD/README.md>
  - <https://raw.githubusercontent.com/icl-utk-edu/heffte/HEAD/benchmarks/speed3d.h>
  - <https://raw.githubusercontent.com/icl-utk-edu/heffte/HEAD/benchmarks/speed3d_c2c.cpp>
- **Sources the enricher read:**
  - <https://github.com/icl-utk-edu/heffte>
  - <https://github.com/icl-utk-edu/heffte/commits>
  - <https://github.com/icl-utk-edu/heffte/releases>
  - <https://github.com/icl-utk-edu/heffte/issues?q=is%3Aissue>
  - <https://github.com/icl-utk-edu/heffte/issues/88>
  - <https://github.com/icl-utk-edu/heffte/issues/90>
  - <https://github.com/icl-utk-edu/heffte/tree/master/include/stock_fft>
  - <https://raw.githubusercontent.com/icl-utk-edu/heffte/HEAD/README.md>
  - <https://raw.githubusercontent.com/icl-utk-edu/heffte/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/icl-utk-edu/heffte/HEAD/doxygen/installation.md>
  - <https://raw.githubusercontent.com/icl-utk-edu/heffte/HEAD/doxygen/basic_usage.md>
  - <https://raw.githubusercontent.com/icl-utk-edu/heffte/HEAD/include/heffte.h>
  - <https://raw.githubusercontent.com/icl-utk-edu/heffte/HEAD/include/heffte_fft3d.h>
  - <https://raw.githubusercontent.com/icl-utk-edu/heffte/HEAD/include/heffte_fft3d_r2c.h>
  - <https://raw.githubusercontent.com/icl-utk-edu/heffte/HEAD/include/heffte_plan_logic.h>
  - <https://raw.githubusercontent.com/icl-utk-edu/heffte/HEAD/include/heffte_reshape3d.h>
  - <https://raw.githubusercontent.com/icl-utk-edu/heffte/HEAD/include/heffte_backends.h>
  - <https://raw.githubusercontent.com/icl-utk-edu/heffte/HEAD/include/heffte_backend_stock.h>
  - <https://raw.githubusercontent.com/icl-utk-edu/heffte/HEAD/include/heffte_backend_fftw.h>
  - <https://raw.githubusercontent.com/icl-utk-edu/heffte/HEAD/include/stock_fft/heffte_stock_algos.h>
  - <https://raw.githubusercontent.com/icl-utk-edu/heffte/HEAD/include/stock_fft/heffte_stock_tree.h>
  - <https://raw.githubusercontent.com/icl-utk-edu/heffte/HEAD/benchmarks/speed3d.h>
  - <https://raw.githubusercontent.com/icl-utk-edu/hpfft/HEAD/README.md>
  - https://link.springer.com/chapter/10.1007/978-3-030-50371-0_19 (not opened; WebSearch snippets only)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/icl-utk-edu/heffte`) · [data/wave8/enrich/raw/github_com_icl_utk_edu_heffte.json](../../../data/wave8/enrich/raw/github_com_icl_utk_edu_heffte.json) (enrichment confidence 0.7)

</details>
