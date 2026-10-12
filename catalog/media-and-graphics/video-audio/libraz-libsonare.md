# libsonare

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Dependency-free C++17 audio analysis and DSP engine with librosa-matching features; 1.25-27x faster than librosa per feature.

| | |
|---|---|
| **Beats** | librosa 0.11.0 (Python) |
| **Claimed result** | ms librosa vs libsonare: STFT 12.63 vs 6.81 (1.85x); Mel 19.89 vs 15.87 (1.25x); HPSS 1715.77 vs 64.41 (26.64x); Chroma 42.9 vs 8.46 (5.07x); pYIN 5745.04 vs 364.38 (15.77x); MFCC 21.29 vs 16.91 (1.26x); onset strength 20.98 vs 16.76 (1.25x); spectral centroid 24.67 vs 12.1 (2.04x); beat tracking 34.69 vs 44.44 (0.78x, slower). Full analyze 541.45 ms vs bpm-detector 38949.54 ms (71.94x). |
| **Workload** | Per-feature timing from raw audio (every call rebuilds STFT/Mel from samples) on a deterministic synthetic 73 s 44.1 kHz stereo fixture, downmixed and resampled to 22.05 kHz outside the timed region (librosa.load on the Python side, sonare::resample on the C++ side); median of 3 runs per case, no warmup; C++ timed with chrono::steady_clock inside sonare_bench, librosa with time.perf_counter around each call using librosa defaults (n_fft 2048, hop 512). Plus the full analyze() pipeline versus the same author's librosa-based bpm-detector 1.1.0 --comprehensive run as a subprocess. |
| **Metric** | throughput |
| **Hardware** | Apple M5 Max (benchmarks/README.md: 'M5 Max numbers are the published reference'); results record 18 hardware threads; load average 2.29/2.43 during the C++ run (results_cpp.json) and 2.49/3.09 during the librosa run (results.json) |
| **Compiler and flags** | CMake Release build (cmake -B build-bench -DCMAKE_BUILD_TYPE=Release -DBUILD_BENCH=ON -DBUILD_TESTING=OFF -DBUILD_CLI=OFF); the root CMakeLists.txt adds no optimization or -march flags beyond the Release defaults; PFFFT SIMD FFT backend on by default; compiler and version not stated |
| **Adoption** | 26 stars |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/libraz/libsonare) · [benchmark](https://raw.githubusercontent.com/libraz/libsonare/HEAD/benchmarks/results.json) |

## Verdict

Author-run: on an 18-thread Apple M5 Max (compiler not stated, CMake Release, PFFFT on) libsonare beat librosa 0.11.0 on a synthetic 73 s clip resampled to 22.05 kHz, median of 3 runs: STFT 1.85x, Mel 1.25x, MFCC 1.26x, onset 1.25x, centroid 2.04x, Chroma 5.07x, pYIN 15.77x (single-threaded C++), HPSS 26.64x (multithreaded C++ against single-threaded scipy), beat tracking 0.78x (slower). The Chroma ratio is inflated: run_bench.py calls librosa.feature.chroma_stft without tuning, so librosa also runs an estimate_tuning (piptrack) pass that libsonare's default skips; the 71.94x full-pipeline figure is against bpm-detector run as a subprocess (Python start-up, imports, decoding and resampling inside its timing, none of them inside libsonare's).

## Use it when

- C++ or Python services that run librosa-style analysis (BPM, key, chords, pitch) on many tracks and want to drop the Python/NumPy/numba stack.
- pYIN pitch tracking at scale: the measured 15.77x over librosa comes from a single-threaded C++ path, so it should hold per core.
- HPSS on multi-core servers, where the threaded median filters gave 26.64x over librosa on an 18-thread Apple M5 Max.
- Browser or Node.js audio analysis that has to match librosa defaults (WASM build, single-threaded).
- Pipelines that compute several features from one STFT: the cached path drops onset strength to 0.47 ms and MFCC to 0.89 ms once the spectrogram exists.

## Skip it when

- Beat tracking alone: libsonare's detect_beats was slower than librosa.beat.beat_track (44.44 vs 34.69 ms).
- Windows: the README says it is not supported (use WSL2); PyPI 1.8.1 ships wheels only for macOS arm64 and manylinux x86-64/aarch64, Python 3.11+.
- Codec work (decode/encode, resampling for playback): it is an analysis/DSP engine, not a replacement for FFmpeg, libopus or a dedicated resampler.
- Workloads that need librosa's exact output everywhere: chroma uses a fixed A440 tuning by default instead of librosa's auto-estimated tuning, and the HPSS median filter shrinks its window at the edges rather than reflect-padding.
- Single-core or WASM deployments expecting the headline HPSS and full-pipeline ratios: those come partly from multithreading, and the WASM build is single-threaded.

## How it is fast

Native float32 code with a vendored SIMD FFT (PFFFT, falling back to KissFFT for lengths PFFFT cannot factor) and Eigen array expressions for masks and filterbanks. HPSS uses a sorted-array sliding median (binary search plus memmove) instead of scipy's per-window selection, and splits the horizontal and vertical median filters across up to hardware_concurrency std::async workers. pYIN is single-threaded but computes the YIN difference by FFT cross-correlation with reused per-frame buffers and runs the Viterbi decode over log transition weights precomputed once. analyze() runs its spectrogram/mel/onset group and its HPSS+chroma group concurrently and shares one spectrogram across features.

## Compared with alternatives

Pick libsonare over audioFlux when you need the higher-level music-information pipeline (pYIN, HPSS, beats, key, chords) with librosa-matching defaults in C++, Python or the browser; audioFlux is the broader transform toolkit with OpenMP and pedalboard is the choice for audio I/O and effects rather than analysis.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake package find_package(sonare); shared optional via BUILD_SHARED) plus Python wheel, npm WASM package and an unpublished Node native addon |
| **Dependencies** | Eigen 3.3+ headers at build time (system or fetched 3.4.x via FetchContent); vendored dr_libs, minimp3, KissFFT, PFFFT and r8brain; optional FFmpeg for more input formats; Python binding needs NumPy |
| **Minimum toolchain** | C++17, CMake; compiler versions not documented |
| **Platforms** | Linux and macOS (x86-64, aarch64), WebAssembly; Windows unsupported (WSL2) |
| **Thread safety** | not documented; HPSS and analyze() spawn their own std::async workers internally |
| **Drop-in for the baseline** | partial — defaults mirror librosa (n_fft 2048, hop 512, 128 Slaney mels, HPSS kernels 31, pYIN constants) and CI checks reference values, but the API is new C++/Python/JS and chroma tuning is not auto-estimated |

## Gotchas

- Chroma::compute defaults to tuning 0 (A440); librosa.feature.chroma_stft estimates tuning when none is given, so pass an estimate_tuning() result for detuned material.
- HPSS and analyze() take every core they can get; the benchmark README warns that a busy machine inflates these timings several-fold, and the library offers no thread-count knob in the HPSS config.
- Very broad scope (92 mastering processors, synths, DAW runtime) in one library; turn off BUILD_MASTERING/BUILD_MIXING/BUILD_FX and friends if only analysis is needed.
- The Python, Node and WASM bindings are hand-written and not identical; check the repository's binding parity matrix before porting code between runtimes.

## Known shortcomings

- Off-baseline (librosa, Python). The HPSS and pYIN gains come from multi-core runs against a mostly single-threaded librosa, and the 71.94x figure is against bpm-detector rather than librosa; benchmarks/README.md names an Apple M5 Max but no compiler.
- Enricher (e113, 2026-10-05): the Chroma 5.07x row is inflated: run_bench.py calls librosa.feature.chroma_stft without a tuning argument, so librosa also times estimate_tuning (piptrack), while libsonare's ChromaConfig fixes tuning at 0 (documented in its header); the real ratio is unmeasured. The full-pipeline 71.94x times bpm-detector including Python startup, imports, decode and resample while libsonare receives pre-resampled samples. Caveat fix: pYIN is single-threaded (pitch.cpp has no threads), so the 15.77x is per core; HPSS (std::async median filters, up to 18 workers) and analyze() are threaded. Beat tracking is 0.78x. C stands.

## Caveats and trade-offs

Authors' own benchmark: public scripts and a named CPU (Apple M5 Max) but no compiler, so tier C. Baseline is a Python library; the biggest gaps (HPSS 26.64x, pYIN 15.77x) come from libsonare's threaded paths using every core against mostly single-threaded librosa, and benchmarks/README.md says the WASM build is single-threaded and these speedups shrink there. The 71.94x full-pipeline figure compares against bpm-detector (the same author's earlier librosa-based program, timed as a subprocess including Python start-up and imports), not librosa itself. Beat tracking is slower than librosa (0.78x). Inputs are resampled by different resamplers on each side, so the two libraries do not see byte-identical samples. Synthetic fixture only. Audio analysis, not a codec, so it is off the FFmpeg/x264/Opus category baselines.

Dependency-free C++ core with Python, Node.js and WASM bindings; defaults match librosa where features overlap and CI checks against librosa reference values. Threaded paths use all cores.

## Maintenance

Very active (3,069 commits, v1.8.1 on PyPI, last commit 2026-10-03), Apache-2.0, single maintainer with 26 stars and no public issue history, so expect fast change and little outside review.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party numbers: benchmarks/results.json (merged from benchmarks/results_cpp.json) holds every per-feature figure and the 541.45 ms vs 38949.54 ms full-pipeline figure exactly as claimed, produced by public code (benchmarks/bench_cpp.cpp for the C++ side, benchmarks/run_bench.py for librosa 0.11.0 pinned in benchmarks/pyproject.toml). benchmarks/README.md names the Apple M5 Max as the published reference machine and gives the Release cmake line, but no compiler or compiler version is stated, so not A.
- **Verifier notes:** All claimed numbers match results.json exactly; harness reads like-for-like per feature (both sides standalone from raw audio, median of 3). Hardware is stated after all (M5 Max in benchmarks/README.md), but compiler is not, so C stands; keep with the off-baseline shortcoming.
- **Fields the verifier corrected:** `hardware`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** first-party harness vs librosa
- **Pages the verifier opened:**
  - <https://github.com/libraz/libsonare>
  - <https://github.com/libraz/libsonare/commits>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/README.md>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/benchmarks/results.json>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/benchmarks/results_cpp.json>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/benchmarks/bench_cpp.cpp>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/benchmarks/run_bench.py>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/benchmarks/pyproject.toml>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/libraz/libsonare>
  - <https://github.com/libraz/libsonare/commits>
  - <https://github.com/libraz/libsonare/issues?q=is%3Aissue>
  - <https://github.com/libraz/libsonare/pulls?q=is%3Apr>
  - <https://github.com/libraz/libsonare/tree/main/third_party>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/README.md>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/benchmarks/results.json>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/benchmarks/results_cpp.json>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/benchmarks/bench_cpp.cpp>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/benchmarks/run_bench.py>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/benchmarks/pyproject.toml>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/src/effects/hpss.h>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/src/effects/hpss.cpp>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/src/feature/pitch.h>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/src/feature/pitch.cpp>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/src/feature/mel_spectrogram.h>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/src/feature/mel_spectrogram.cpp>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/src/feature/onset.h>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/src/feature/chroma.h>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/src/core/spectrum.h>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/src/core/resample.h>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/src/core/fft.cpp>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/src/analysis/beat_analyzer.h>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/src/analysis/beat_analyzer.cpp>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/src/analysis/music_analyzer.cpp>
  - <https://raw.githubusercontent.com/libraz/libsonare/HEAD/src/quick.h>
  - <https://pypi.org/pypi/libsonare/json>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/libraz/libsonare`) · [data/wave10/enrich/raw/github_com_libraz_libsonare.json](../../../data/wave10/enrich/raw/github_com_libraz_libsonare.json) (enrichment confidence 0.75)

</details>
