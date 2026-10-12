# audioFlux

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C (with Python bindings)` · `MIT` · 🟢 active

> C audio feature-extraction library (mel, MFCC, CQT, CWT, pitch) with Python bindings; mel spectrograms faster than librosa, mostly torchaudio-competitive.

| | |
|---|---|
| **Beats** | librosa 0.10.0 and torchaudio 0.11.0 (mel spectrogram); essentia 2.0.1 listed as a compared library |
| **Claimed result** | Against torchaudio (the like-for-like baseline; Linux AMD Threadripper 3970X, audioFlux on 32 OpenMP threads): 1.2-7.1x across time steps, but 0.92x (slower) at 100 steps; on a Linux Intel i7-6850K audioFlux is slower than torchaudio at 10 steps and above (13.07378 s vs 12.14323 s at 3000); on macOS Intel and Apple M1 torchaudio is faster for short inputs while audioFlux is faster for long ones. The librosa ratios (about 56x at 1 step and 10.5x at 3000 steps, derived from page data) are inflated: librosa rebuilt its mel filter bank inside the timed call (filters.mel cache off) at a 22050 Hz default sample rate. Off the category's C baselines in every case. |
| **Workload** | Time to compute the mel spectrogram of 1000 sample signals at time steps of 1 to 3000 frames (fft_len 2048, slide_len 512, sampling rate 32000) on Linux and macOS with AMD, Intel and M1 CPUs, warm-up and initialisation excluded. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen Threadripper 3970X (Ubuntu 20.04.4), Intel Core i7-6850K 3.60 GHz (Ubuntu 20.04.4), 3.8 GHz 8-core Intel Core i7 on macOS 12.6.1, Apple M1 |
| **Compiler and flags** | Not stated; README says libraries use the latest release or source built with high-performance support, with OpenBLAS or MKL; run_benchmark.py scripts are in the benchmark folder |
| **Adoption** | 3.4k stars, 150 forks, 168 commits; PyPI audioflux 0.1.9 (2024-05-24), also on Anaconda |
| **Last commit** | 2026-03-06 |
| **Links** | [repository](https://github.com/libAudioFlux/audioFlux) · [benchmark](https://raw.githubusercontent.com/libAudioFlux/audioFlux/master/benchmark/README.md) |

## Verdict

First-party benchmark (audioFlux 0.1.5, librosa 0.10.0, torchaudio 0.11.0; 2048-point FFT, hop 512, 128 mels, average per call reported as seconds per 1000 calls) on a Threadripper 3970X, i7-6850K, macOS Intel i7 and Apple M1, with build flags, BLAS backend and thread counts not recorded: against torchaudio audioFlux is 1.2x to 7.1x faster on the 3970X except at 100 frames (0.92x), slower on the i7-6850K from 10 frames up, and faster on the Macs only for long inputs. The 10x to 56x librosa ratios overstate the core's advantage: run_librosa.py times librosa.feature.melspectrogram, which in librosa 0.10.0 rebuilds the 128-band mel filter bank on every call (filters.mel cache is off unless LIBROSA_CACHE_DIR is set) and is called without sr (22050 Hz default instead of 32000), while audioFlux's and torchaudio's filter banks are built at object creation outside the timer; audioFlux also runs up to 32 OpenMP threads with no thread limits set for any library.

## Use it when

- Batch extraction of mel, MFCC, CQT or chroma features from long clips in Python on x86-64 Linux or macOS, where the C core's multi-threaded STFT pays off (500 to 3000 frames per call)
- Replacing librosa.feature.melspectrogram in a data pipeline that calls it many times, since audioFlux builds the filter bank once and keeps it in the object
- Mobile or embedded feature extraction from C (iOS Accelerate, Android FFTW3f builds) where pulling in PyTorch is not an option; the README reports 0.25 to 0.89 ms per 4096-sample mel frame on phones
- Research that needs less common transforms (NSGT, S-transform, synchrosqueezed CWT, reassigned STFT) in one library

## Skip it when

- You already depend on PyTorch: torchaudio was as fast or faster on the Intel i7-6850K Linux box at 10 frames and above, at 100 frames on the Threadripper, and for short inputs on both Macs
- You need outputs that match librosa or torchaudio numerically: the benchmark never compares outputs, defaults differ (Slaney scale without filter normalisation here), and open issue #35 reports different mel values when torch is imported in the same process
- Linux ARM64 or other platforms without a prebuilt library: issue #44 (arm64 Docker) is unanswered, and the PyPI package is a single 70.8 MB py3-none-any wheel carrying prebuilt binaries
- Very long inputs on memory-constrained devices: issue #27 reports 1.4 GB allocated for a 3-minute track (15 M samples, hop 512) on Android; the STFT stores full fftLength complex frames, not just the fftLength/2+1 non-redundant bins
- Projects that need a responsive upstream: most issues since 2023 have no maintainer reply, including #46, an unreported vulnerability (the reporter could not file it because GitHub security reporting is off)

## How it is fast

Per-frame FFTs go to a vendor FFT chosen at build time: Intel MKL DFTI on Linux, Apple Accelerate vDSP on macOS/iOS, FFTW3f on Android/Windows, or a built-in cached-twiddle radix-2 FFT. The STFT splits frames across omp_get_max_threads()/2 OpenMP worker FFT objects (32 threads on the 64-thread Threadripper 3970X used for the headline chart). The mel filter bank is built once when the object is created and applied as a matrix product, so repeated calls only pay for FFT, power and the dot product.

## Compared with alternatives

No catalogued sibling does audio feature extraction: pedalboard covers effects and file I/O against pySoX and librosa.load, and libsoxr/r8brain cover resampling, so pick audioFlux when the job is mel/MFCC/CQT features and you cannot or do not want to depend on PyTorch.

## Integration

| | |
|---|---|
| **Form** | shared lib (C core built with CMake) plus Python package (ctypes wrapper); static lib on iOS |
| **Dependencies** | Linux: optional Intel MKL (MKL_INCLUDE_PATH/MKL_LIB_PATH) and LLVM libomp; macOS: Accelerate and libomp (Homebrew llvm); Android/Windows/OHOS: FFTW3f; Python: numpy, scipy&gt;=1.2.0, soundfile&gt;=0.12.1, matplotlib |
| **Minimum toolchain** | CMake 3.5; Linux CMakeLists hard-codes /usr/bin/clang with -O3 -fopenmp=libomp; macOS needs Homebrew llvm (C_COMPILER_PATH); Python &gt;=3.6; setup.py refuses to build on Windows (cross-built from macOS/Linux) |
| **Platforms** | Linux and macOS (x86-64, Apple M1), Windows, iOS, Android, OpenHarmony per the build scripts; Linux arm64 not documented |
| **Thread safety** | not documented; objects cache per-call buffers internally, so use one object per thread; the STFT itself runs OpenMP threads |
| **Drop-in for the baseline** | partial — same features as librosa and torchaudio but a different object API, power-of-two FFT sizes only, and different mel defaults, so outputs are not identical |

## Gotchas

- The STFT calls omp_set_num_threads() on each call (timeLength threads for short inputs, omp_get_max_threads()/2 otherwise), changing the OpenMP thread count other code in the same runtime then inherits; the benchmark README also warns that mixing its libomp with MKL/PyTorch OpenMP runtimes can fail or slow down
- On Apple platforms the real-input FFT goes through the complex vDSP_fft_zop path because, per a source comment, 'real to complex fft has problem', so it does twice the FFT work there
- The PyPI release is still 0.1.9 (2024-05-24); the TuneTrack features (README 'v0.1.10', commits of 2026-02/03) are only in the source tree
- benchmark/run_benchmark.py treats -r as the number of subprocess launches and -er as calls per launch, the reverse of what benchmark/README.md says; the per-call average it prints is still correct

## Known shortcomings

- Off-baseline: compared only with librosa and torchaudio (Python), never with a C baseline; scripts are public but compiler, flags, BLAS and thread counts are unstated. Torchaudio is faster on Linux Intel at 10 or more steps and on macOS for short inputs.
- The librosa ratios are inflated (retier-28): run_librosa.py times librosa.feature.melspectrogram, which in librosa 0.10.0 rebuilds the mel filter bank every call (cache off without LIBROSA_CACHE_DIR) at the 22050 Hz default (sr omitted), while audioFlux and torchaudio build banks at init outside the timer; audioFlux's STFT runs 32 OpenMP threads on the 3970X with no thread limits anywhere. Open issues #35 (mel output changes after importing torch), #46 (unreported vulnerability), #27 (1.4 GB allocation for a 3-minute track), #44 (arm64 unanswered); PyPI stuck at 0.1.9; run_benchmark.py's -r and -er are swapped against the README.

## Caveats and trade-offs

Off-baseline: compared only against Python libraries (librosa, torchaudio), not against a C/C++ codec or DSP baseline from the FFmpeg, x264, Opus list; essentia is listed but has no numbers. First-party benchmark on 2022-2023 versions (audioFlux 0.1.5, librosa 0.10.0, torchaudio 0.11.0); compiler, flags, BLAS backend and thread counts are not stated, and torchaudio/MKL threading is not controlled. Inputs are random noise (np.random.randn) timed with time.time() around one call, summed over 1000 runs. Settings are close but not identical: audioFlux uses Slaney mel scale with no filter normalisation, librosa defaults to Slaney normalisation, torchaudio uses its default HTK mel scale; outputs are not compared. torchaudio is faster than audioFlux on Linux Intel at 10 steps and above and on macOS for short inputs. The README also shows the results as chart images. [retier] Off-baseline (librosa and torchaudio, Python). librosa rows inflated by per-call filter-bank construction and a mismatched sample rate; audioFlux runs 32 OpenMP threads unthrottled. Build flags live in src/CMakeLists.txt (Linux clang -O3 with MKL and libomp) but the measured build is not recorded. Open issues #35 (mel output changes after importing torch), #46 (unreported vulnerability), #27 (1.4 GB allocation for a 3-minute track), #44 (arm64, unanswered); PyPI stuck at 0.1.9 (2024-05-24); run_benchmark.py's -r and -er flags are swapped against the README.

Audio and music analysis library: mel spectrogram, MFCC, CQT, CWT and more; C core with a Python wrapper, optional OpenBLAS, MKL or Accelerate backends. Adjacent to the video-audio category (feature extraction, not codecs).

## Maintenance

MIT-licensed and usable from Python today, but maintenance is sporadic: no PyPI release since 0.1.9 (2024-05-24), a commit gap from May 2024 to February 2026, and most open issues (including an unreported vulnerability) without a maintainer reply.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party benchmark/README.md with public scripts (benchmark/run_audioflux.py, run_librosa.py, run_torchaudio.py, run_benchmark.py, utils.py) and CPU models, but no compiler, flags or BLAS build of the audioFlux C core is stated, so not A; the &gt;50x librosa ratio also caps it at C.
- **Verifier notes:** Numbers match benchmark/README.md exactly; scripts are public and roughly matched (n_fft 2048, hop 512, 128 mels, center=False). Kept as off-baseline C entry per batch note; last commit 2026-03-06 (TuneTrack fixes), MIT.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/libAudioFlux/audioFlux/master/benchmark/README.md>
  - <https://raw.githubusercontent.com/libAudioFlux/audioFlux/master/benchmark/run_audioflux.py>
  - <https://raw.githubusercontent.com/libAudioFlux/audioFlux/master/benchmark/run_librosa.py>
  - <https://raw.githubusercontent.com/libAudioFlux/audioFlux/master/benchmark/run_torchaudio.py>
  - <https://raw.githubusercontent.com/libAudioFlux/audioFlux/master/benchmark/run_benchmark.py>
  - <https://raw.githubusercontent.com/libAudioFlux/audioFlux/master/benchmark/utils.py>
  - <https://github.com/libAudioFlux/audioFlux>
  - <https://github.com/libAudioFlux/audioFlux/tree/master/benchmark>
  - <https://github.com/libAudioFlux/audioFlux/commits/master>
  - <https://pypi.org/pypi/audioflux/json>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/libAudioFlux/audioFlux/master/README.md>
  - <https://raw.githubusercontent.com/libAudioFlux/audioFlux/master/benchmark/README.md>
  - <https://raw.githubusercontent.com/libAudioFlux/audioFlux/master/benchmark/run_audioflux.py>
  - <https://raw.githubusercontent.com/libAudioFlux/audioFlux/master/benchmark/run_librosa.py>
  - <https://raw.githubusercontent.com/libAudioFlux/audioFlux/master/benchmark/run_torchaudio.py>
  - <https://raw.githubusercontent.com/libAudioFlux/audioFlux/master/benchmark/run_benchmark.py>
  - <https://raw.githubusercontent.com/libAudioFlux/audioFlux/master/benchmark/utils.py>
  - <https://raw.githubusercontent.com/libAudioFlux/audioFlux/master/setup.py>
  - <https://raw.githubusercontent.com/libAudioFlux/audioFlux/master/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/libAudioFlux/audioFlux/master/scripts/build_linux.sh>
  - <https://raw.githubusercontent.com/libAudioFlux/audioFlux/master/scripts/build_macOS.sh>
  - <https://raw.githubusercontent.com/libAudioFlux/audioFlux/master/src/bft_algorithm.c>
  - <https://raw.githubusercontent.com/libAudioFlux/audioFlux/master/src/dsp/fft_algorithm.c>
  - <https://raw.githubusercontent.com/libAudioFlux/audioFlux/master/src/stft_algorithm.c>
  - <https://raw.githubusercontent.com/libAudioFlux/audioFlux/master/src/spectrogram_algorithm.c>
  - <https://raw.githubusercontent.com/libAudioFlux/audioFlux/master/src/reassign_algorithm.c>
  - <https://raw.githubusercontent.com/libAudioFlux/audioFlux/master/src/vector/flux_vectorOp.c>
  - <https://raw.githubusercontent.com/libAudioFlux/audioFlux/master/docs/installing.md>
  - <https://raw.githubusercontent.com/libAudioFlux/audioFlux/master/python/audioflux/__version__.py>
  - <https://raw.githubusercontent.com/libAudioFlux/audioFlux/master/python/audioflux/__init__.py>
  - <https://raw.githubusercontent.com/libAudioFlux/audioFlux/master/python/audioflux/spectrogram.py>
  - <https://raw.githubusercontent.com/libAudioFlux/audioFlux/master/python/audioflux/bft.py>
  - <https://raw.githubusercontent.com/libAudioFlux/audioFlux/master/python/audioflux/fftlib.py>
  - <https://raw.githubusercontent.com/librosa/librosa/0.10.0/librosa/feature/spectral.py>
  - <https://raw.githubusercontent.com/librosa/librosa/0.10.0/librosa/filters.py>
  - <https://raw.githubusercontent.com/librosa/librosa/0.10.0/librosa/_cache.py>
  - <https://github.com/libAudioFlux/audioFlux/tree/master/src>
  - <https://github.com/libAudioFlux/audioFlux/tree/master/scripts>
  - <https://github.com/libAudioFlux/audioFlux/issues?q=is%3Aissue>
  - <https://github.com/libAudioFlux/audioFlux/issues/35>
  - <https://github.com/libAudioFlux/audioFlux/issues/18>
  - <https://github.com/libAudioFlux/audioFlux/issues/22>
  - <https://github.com/libAudioFlux/audioFlux/issues/27>
  - <https://github.com/libAudioFlux/audioFlux/issues/44>
  - <https://github.com/libAudioFlux/audioFlux/issues/46>
  - <https://github.com/libAudioFlux/audioFlux/commits/master>
  - <https://pypi.org/pypi/audioflux/json>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/libaudioflux/audioflux`) · [data/wave10/enrich/raw/github_com_libaudioflux_audioflux.json](../../../data/wave10/enrich/raw/github_com_libaudioflux_audioflux.json) (enrichment confidence 0.75)

</details>
