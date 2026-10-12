# FFT

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md)</sub>

**What these beat:** FFTW, MKL FFT, KissFFT  
**49 entries:** 13 tier A · 9 tier B · 21 tier C · 6 tier D · 44 copyable, 5 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**MatX**](nvidia-matx.md) | NumPy-style C++20 GPU array library whose JIT fusion of a cuFFT pipeline ran 1.61x faster than handwritten CUDA + cuFFT. | **A** | C++ | BSD-3-Clause | 🟢 active |
| 2 | [**PFFFT (marton78 fork)**](marton78-pffft.md) | Small BSD-licensed SIMD 1D FFT (float/double) plus fast convolution, about 5x faster than KissFFT, about half FFTW's speed. | **A** | C | FFTPACK/NCAR (UCAR)… | 🟢 active |
| 3 | [**PocketFFT (C++ branch)**](mreineck-pocketfft.md) | Header-only C++11 FFT (multi-D, any length, DCT/DST) behind NumPy and SciPy; about 4.5x faster than KissFFT on 3D transforms. | **A** | C++ | BSD-3-Clause | 🟢 active |
| 4 | [**VectorFFT**](tugbars-vectorfft.md) | Double-precision x86 AVX2/AVX-512 FFT library in C, with generated codelets and a wisdom planner; median 1.29x Intel MKL on 1D c2c. | **A** | C | MIT | 🟢 active |
| 5 | [**go-fft**](go-fft-fft.md) | Pure-Go (no cgo) float64 FFT for any length; fastest pure-Go option, behind FFTW on most single-core 1-D sizes. | **A** | Go | BSD-3-Clause | 🟢 active |
| 6 | [**Notorious-FFT**](notoriouslob-notorious-fft.md) | Header-only C FFT with an FFTW-shaped API and minfft-style split-radix core; 8-13% faster than minfft on ARM, far behind FFTW. | **A** | C | MIT | 🟢 active |
| 7 | [**meow_fft**](jodithetigger-meow-fft.md) | Single-header C99 float FFT (0BSD), scalar radix-8 mixed-radix, 1.1-1.5x faster than KissFFT on power-of-two sizes. | **A** | C | 0BSD | 🟡 stale |
| 8 | [**TurboFFT**](shixun404-turbofft.md) | Code-generated batched 1D FP32/FP64 GPU FFT kernels with fused ABFT fault tolerance; matches or beats cuFFT, beats VkFFT. | **A** | CUDA/C++ | Apache-2.0 | 🟡 stale |
| 9 | [**SFFT3 (3-D FFT built from FFTW 1-D transforms)**](elgw-sfft3.md) | 500-line OpenMP 3-D real FFT over FFTW 1-D plans; 1.2-1.3x faster than FFTW 3-D plans on large float volumes. | **A** | C | GPL-3.0 | 🟡 stale |
| 10 | [**muFFT**](themaister-mufft.md) | Small MIT C99 single-precision power-of-two FFT with runtime SSE/SSE3/AVX dispatch; 5-9x faster than KissFFT, near FFTW. | **A** | C | MIT | 🔴 abandoned |
| 11 | [**Admiral**](diamondinoia-admiral.md) | Compiled C++20 SIMD FFT library (any size, 1-D/N-D, c2c/r2c/DCT); the author's sweep has it 1.34-1.43x faster than single-thread FFTW_MEASURE. | **A** | C++ | BSD-3-Clause-Attribution (study only) | 🟢 active |
| 12 | [**cuSpFFT**](darkviper7-cuspfft.md) | Course-project CUDA 2-D R2C FFT for binary (0/1) sparse matrices; beats dense cuFFT on mid-size non-power-of-2 inputs. | **A** | CUDA | no license (study only) | 🟢 active |
| 13 | [**MPSFT (Matrix Pencil Sparse Fourier Transform)**](jiaweichiu-mpsft.md) | Research sparse Fourier transform (C++11) that recovers S dominant modes of a huge noisy spectrum faster than a full FFTW transform. | **A** | C++ | no license (study only) | 🔴 abandoned |
| 14 | [**KFR**](kfrlib-kfr.md) | C++20 SIMD DSP framework whose any-length FFT tracks or beats FFTW in vendor and LIGO/KAGRA benchmarks; GPL or paid license. | **B** | C++ | GPL-2.0-or-later (dual… | 🟢 active |
| 15 | [**VkFFT**](dtolm-vkfft.md) | Header-only, cross-vendor GPU FFT library; matches cuFFT on smooth lengths and is \~1.5-3x faster on prime/Bluestein lengths. | **B** | C | MIT | 🟢 active |
| 16 | [**FINUFFT (with cuFINUFFT)**](flatironinstitute-finufft.md) | CPU (and CUDA) nonuniform FFT library, types 1-3 in 1-3 dimensions, several times faster than NFFT3 and CMCL NUFFT. | **B** | C++ | Apache-2.0 | 🟢 active |
| 17 | [**FFTW++ (implicit dealiased convolutions on FFTW3)**](dealias-fftwpp.md) | C++ layer over FFTW3 whose implicitly/hybrid-dealiased convolutions beat explicit zero-padded FFT convolutions in 2D and 3D. | **B** | C++ | LGPL-3.0-or-later | 🟢 active |
| 18 | [**heFFTe (Highly Efficient FFT for Exascale)**](icl-utk-edu-heffte.md) | MPI-distributed 2-D/3-D FFT layer over FFTW, MKL, cuFFT and rocFFT; on GPUs about 2x fftMPI and SWFFT, at parity on CPU. | **B** | C++ | BSD-3-Clause | 🟢 active |
| 19 | [**TRON (TRajectory Optimized NUFFT)**](davidssmith-tron.md) | CUDA NUFFT gridding/degridding hard-wired for 2D radial MRI trajectories; paper reports 6-30x over gpuNUFFT, BART and IRT. | **B** | CUDA | MIT | 🟢 active |
| 20 | [**FlashFFTConv**](hazyresearch-flash-fft-conv.md) | CUDA tensor-core FFT convolution for PyTorch; 1.3x to 7.9x faster than torch.fft (cuFFT) convolution on H100. | **B** | CUDA/C++ | Apache-2.0 | 🟡 stale |
| 21 | [**PFT (Partial Fourier Transform)**](snudatalab-pft.md) | Research C++ code computing only M of N Fourier coefficients with polynomial-approximated twiddles; up to 19x over FFTW/MKL. | **B** | C++ | Apache-2.0 | 🟡 stale |
| 22 | [**Auto-MPFT**](snudatalab-auto-mpft.md) | Research code (KDD 2024) computing only a low-frequency block of 2-D Fourier coefficients faster than a full FFTW/MKL FFT. | **B** | C++ | Apache-2.0 | 🟡 stale |
| 23 | [**RustFFT**](ejmahler-rustfft.md) | Pure-Rust SIMD FFT for any length, including primes; beats a scalar, per-call-planned FFTW 3.3.8 at tiny and huge sizes. | **C** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 24 | [**wavelib**](rafat-wavelib.md) | Plain C wavelet library (DWT, SWT, MODWT, packets, CWT); its WebAssembly build beats pure-JS discrete-wavelets by 82-154x on wavedec. | **C** | C | BSD-3-Clause | 🟢 active |
| 25 | [**JTransforms**](wendykierp-jtransforms.md) | Pure-Java multithreaded FFT/DCT/DST/DHT library; beat a per-call-planned FFTW (via JNI) on smooth 2-D/3-D sizes, lost on primes. | **C** | Java | BSD-2-Clause | 🟢 active |
| 26 | [**PhastFT**](qustate-phastft.md) | Safe-Rust, in-place, power-of-two FFT with low memory and optional threads; beats RustFFT at mid sizes and a scalar FFTW build. | **C** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 27 | [**dft_simd (vertical-SIMD FFTW codelets)**](sfegan-dft-simd.md) | Recipe and test code that runs FFTW genfft codelets on AVX2/AVX-512 vectors, 8 or 16 short DFTs per call; beats FFTW on bulk short transforms. | **C** | C++ | GPL-2.0-or-later | 🟢 active |
| 28 | [**AppleSiliconFFT**](aminems-applesiliconfft.md) | Research Metal GPU and SME2 FFT kernels for Apple Silicon; M1 GPU N=4096 batch beats one-thread vDSP by 29%. | **C** | Metal Shading Language | MIT | 🟢 active |
| 29 | [**juFFTe**](fzj-jsc-juffte.md) | Fortran FFTE rewrite with Spiral-generated RISC-V Vector kernels; its authors report beating FFTW3 on RVV 1.0 chips, but the FFTW comparison is weak. | **C** | Fortran | Apache-2.0 | 🟢 active |
| 30 | [**FastAndFourier (FAF, JIT-compiled DSP/FFT library)**](notoriouslob-fastandfourier.md) | C11 DSP library (FFT, DCT/DST, DWT, CWT, STFT) with IR interpreter plus runtime gcc JIT; beats KissFFT only at some sizes. | **C** | C | MIT | 🟢 active |
| 31 | [**matchedfilter (formerly peak-fft)**](ahnitz-matchedfilter.md) | Fused batched matched filter (spectral product, inverse FFT, peak scan) for data x template banks; peak-only mode beats FFTW's inverse-only time. | **C** | C core | MIT | 🟢 active |
| 32 | [**pocketfft-tuned (benchmark-driven PocketFFT fork)**](dimandragon-pocketfft-tuned.md) | Header-only PocketFFT fork with AVX float 1-D codelets: 2.4x upstream, 1.35x FFTW_ESTIMATE on 1-D c2c; loses to FFTW_MEASURE. | **C** | C++ | BSD-3-Clause | 🟢 active |
| 33 | [**FFTS (The Fastest Fourier Transform in the South)**](anthonix-ffts.md) | BSD-3 C library for single-precision FFTs that JIT-compiles a machine-code plan; beat FFTW on pre-AVX SSE CPUs, loses on AVX. | **C** | C | BSD-3-Clause | 🟡 stale |
| 34 | [**minfft**](aimukhin-minfft.md) | Two-file C89 power-of-two FFT/DCT/DST library, about 2x KissFFT's speed; still slower than PocketFFT and FFTW. | **C** | C | MIT | 🟡 stale |
| 35 | [**OFFT**](christian-volmer-offt.md) | Scalar, BSL-licensed C++11 mixed-radix FFT for arbitrary lengths; beats FFTW_ESTIMATE at some awkward sizes, loses elsewhere. | **C** | C++ | BSL-1.0 | 🟡 stale |
| 36 | [**GPU_FFT (Raspberry Pi VideoCore IV, hello_fft in…**](raspberrypi-userland.md) | Andrew Holme's GPU_FFT: power-of-two complex FFTs on the Raspberry Pi VideoCore IV GPU, about 10x FFTW on the Pi 1 ARM. | **C** | C | BSD-3-Clause | 🔴 abandoned |
| 37 | [**Ne10 (NEON FFT)**](projectne10-ne10.md) | ARM's NEON-optimized C library whose FFTs (float, Q31, Q15) beat FFmpeg's assembly FFT on an Android phone. | **C** | C | BSD-3-Clause | 🔴 abandoned |
| 38 | [**fbcuda / fbfft (archived)**](facebookarchive-fbcuda.md) | Archived Facebook CUDA headers whose fbfft kernels batch tiny power-of-two FFTs; authors claim \~1.5x over cuFFT at CNN sizes. | **C** | CUDA C++ | BSD-3-Clause | 🔴 abandoned |
| 39 | [**gpuNUFFT**](andyschwarzl-gpunufft.md) | CUDA gridding/NUFFT library for 2D/3D non-Cartesian MRI with MATLAB and Python front ends; GPU alternative to CPU NUFFTs. | **C** | CUDA C++ | MIT | 🔴 abandoned |
| 40 | [**gpu_fftw**](gpu-fftw-gpu-fftw.md) | LD_PRELOAD shim that reroutes FFTW3 1-D power-of-two complex float FFTs to the original Raspberry Pi's VideoCore IV GPU. | **C** | C/C++ | MIT | 🔴 abandoned |
| 41 | [**tcFFT**](rox906-tcfft.md) | Research FP16 FFT kernels that run radix-16 butterflies on NVIDIA tensor cores; beats cuFFT half precision on V100/A100. | **C** | CUDA/C++ | GPL-3.0 | 🔴 abandoned |
| 42 | [**fCWT**](fastlib-fcwt.md) | Single-precision Morlet continuous wavelet transform on FFTW, OpenMP and AVX; README times it 10-120x faster than other CWT libraries. | **C** | C++ | Apache-2.0 (study only) | 🟡 stale |
| 43 | [**SYLT-FFT (fixed-point FFT for Cortex-M4)**](sylt-collab-sylt-fft.md) | Header-only 32-bit fixed-point radix-2 (I)FFT for Cortex-M4; 15-26% faster than CMSIS-DSP arm_cfft_radix2_q31 on a 256-point inverse. | **C** | C | MHG (Moral High Ground)… (study only) | 🔴 abandoned |
| 44 | [**AOCL-FFTW (AMD-optimized FFTW)**](amd-amd-fftw.md) | AMD's AOCL build of FFTW 3.3.10 with Zen-tuned kernels, copies, transposes and planners; vendor claims beating stock FFTW, no published numbers. | **D** | C | GPL-2.0-or-later | 🟢 active |
| 45 | [**eFFT (event-based FFT)**](raultapia-efft.md) | Header-only C++17/Eigen incremental 2D FFT for event cameras; updates an exact spectrum per event instead of rerunning FFTW. | **D** | C++ | GPL-3.0 | 🟢 active |
| 46 | [**SpFFT (sparse-input 3D FFT)**](eth-cscs-spfft.md) | 3D FFT layer for sparse (spherical-cutoff) frequency data that skips empty columns before calling FFTW/MKL/cuFFT/rocFFT; no published speedup. | **D** | C++ | BSD-3-Clause | 🟡 stale |
| 47 | [**SFFT library (ETH Zurich optimized sparse FFT, versions 1-3)**](davidediger-sfft.md) | ETH Zurich's SSE-optimized C++ build of MIT's sparse FFT (sFFT v1-v3) for k-sparse spectra; no published win over FFTW. | **D** | C++ | GPL-2.0-or-later | 🔴 abandoned |
| 48 | [**OTFFT (OK Ojisan's Template FFT)**](dewetron-otfft.md) | MIT double-precision Stockham FFT library for x86 (SSE2/AVX/AVX2) whose upstream author claims it beats FFTW at 2^1 to 2^24. | **D** | C++ | MIT | 🔴 abandoned |
| 49 | [**tinyfft**](ryuhei-mori-tinyfft.md) | Two tiny C files for power-of-two complex FFT and real convolution; author says the AVX version beats FFTW_MEASURE at 2^17-2^20. | **D** | C | BSD-2-Clause | 🔴 abandoned |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
