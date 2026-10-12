# loudness (iver56)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++ (Python package)` · `MIT` · 🟢 active

> Python wheel over a C++20 BS.1770 meter (Nomono's libloudness) that computes integrated LUFS about 1.7x faster than pyebur128/libebur128.

| | |
|---|---|
| **Beats** | pyebur128 (Cython wrapper of libebur128), pyloudnorm, torchaudio, pyloudness |
| **Claimed result** | Execution time for 5 minutes of mono 48 kHz audio: loudness 0.1.0 0.056 s; pyebur128 0.1.1 0.096 s; torchaudio 2.8.0 0.282 s; pyloudnorm 0.1.1 0.293 s; pyloudness 1.1.2 0.581 s. About 1.7x over pyebur128 (libebur128 via Cython), 5.0x over torchaudio, 5.2x over pyloudnorm, 10.4x over pyloudness (derived from page data). README: 'significantly faster than the alternatives when running on CPU'. |
| **Workload** | Integrated loudness (LUFS) of 5 minutes of mono 48 kHz float32 uniform white noise (np.random.uniform, 14.4M samples) held in a NumPy array; one timed call per library with time.time(), no warmup or repetition. loudness uses Meter&lt;EBU_I\|Histogram&gt;.addFrames (single-threaded path); pyebur128 uses R128State MODE_I add_frames; the pyloudness timing includes writing and reading a temporary WAV file. |
| **Metric** | throughput |
| **Compiler and flags** | Not stated; built with scikit-build-core (default Release) and CMake, C++20, no extra optimization flags in CMakeLists.txt; published wheels come from cibuildwheel |
| **Adoption** | 33 stars |
| **Last commit** | 2025-12-26 |
| **Links** | [repository](https://github.com/iver56/loudness) · [benchmark](https://raw.githubusercontent.com/iver56/loudness/HEAD/scripts/performance_benchmark.py) |

## Verdict

scripts/performance_benchmark.py times one call per library with time.time() on 5 minutes of 48 kHz mono float32 uniform white noise: loudness 0.1.0 0.056 s, pyebur128 0.1.1 0.096 s (about 1.7x), torchaudio 2.8.0 0.282 s, pyloudnorm 0.1.1 0.293 s, pyloudness 1.1.2 0.581 s (which includes writing and reading a WAV file). No CPU, OS, compiler or flags are given, there is no warmup or repetition, and loudness runs in Histogram mode while pyebur128 runs in MODE_I block-list mode; that mismatch costs little here (about 3,000 blocks against 14.4 million filtered samples), and pyebur128 takes the float32 buffer without conversion (ebur128_add_frames_float), so the comparison is otherwise like for like.

## Use it when

- Batch LUFS measurement of many files or long recordings from Python (dataset normalization, podcast/broadcast QC) where the audio is already a float32 NumPy array; the README run puts 5 minutes of 48 kHz mono at 0.056 s, about 5,360x real time (derived from page data).
- Replacing pyloudnorm or torchaudio.functional.loudness on CPU, where the same run is about 5x faster (0.293 s and 0.282 s).
- C++20 projects that want an MIT-licensed libebur128-style meter with typed modes and planar or interleaved input: vendor src/loudness (or use upstream nomonosound/libloudness) instead of the Python wrapper.
- Multichannel programme loudness with the standard BS.1770 weights: the default map for 5 and 6 channels is L, R, C, (LFE unused), Ls, Rs with 1.41 surround weighting.

## Skip it when

- When you need more than integrated loudness from Python: momentary, short-term, LRA and true peak exist in the C++ core but are not bound (PR #1 adding loudness_per_window has been open since 2025-11-20), so pyebur128 or pyloudnorm stay necessary for those.
- When the result must match an exact block-list computation bit for bit: the binding always uses Histogram mode (0.1 LU bins, bin-centre energies), which is within the EBU 0.1 LU tolerance but not identical to libebur128 without EBUR128_MODE_HISTOGRAM.
- Streaming or chunked input from Python: each call builds a fresh meter and needs at least 400 ms of audio, so there is no incremental state across calls.
- Intel macOS, 32-bit or other platforms without published wheels (PyPI 0.2.0 ships macOS arm64, manylinux/musllinux x86-64 and aarch64, Windows amd64); a source build needs CMake 3.22, a C++20 compiler and the git submodules.
- When you expect large wins over libebur128 itself: the measured margin over pyebur128 is about 1.7x from a single run, and the per-sample IIR is identical.

## How it is fast

The K-weighting filter is the same 4th-order combined direct-form-II IIR in double precision as libebur128, so the per-sample recurrence is not faster; the gain comes from the block bookkeeping. libebur128's ebur128_calc_gating_block re-sums the whole 400 ms window of filtered samples at every 100 ms hop (each sample is read four times, strided through an interleaved buffer), while libloudness squares samples into planar per-channel buffers, sums each 100 ms subblock once and forms each gating block from four subblock sums. The input type is a std::variant dispatched once per call, so the integer scaling divisor is a consteval constant (1.0 for float, compiled away) instead of libebur128's runtime static double, and a scoped FTZ/DAZ guard (MXCSR on x86, FPCR on ARM) keeps denormals out of the filter. The Python binding uses Histogram mode, which drops each block's energy into 1000 bins of 0.1 LU instead of keeping a block list.

## Compared with alternatives

No other loudness meter is catalogued; the video-audio siblings are codecs, resamplers and analysis toolkits (audioFlux, libsonare, pedalboard), none of which computes BS.1770 integrated loudness. The real alternative is libebur128 itself (via pyebur128): pick this when you only need integrated LUFS from Python and want the faster single call.

## Integration

| | |
|---|---|
| **Form** | module (pybind11 Python extension, wheels on PyPI); the C++ core builds as a static library from src/loudness |
| **Dependencies** | numpy &gt;= 1.22 at runtime; build needs pybind11 &gt;= 2.12, scikit-build-core &gt;= 0.9.6, CMake &gt;= 3.22, plus vendored gcem and bshoshany/thread-pool (git submodules) |
| **Minimum toolchain** | C++20 compiler (concepts, ranges, consteval); Python &gt;= 3.10 |
| **Platforms** | Wheels for Linux x86-64 and aarch64 (glibc and musl), macOS arm64, Windows x86-64; core is portable C++ with FTZ code for SSE2 and ARM and a manual-FTZ fallback elsewhere |
| **Thread safety** | Each Python call builds its own meter, so calls are independent, but the binding does not release the GIL, so Python threads serialize. In C++ a Meter instance is not documented as thread-safe; addFramesMT runs true peak per channel and the loudness filter as separate tasks, so it does not parallelize integrated loudness alone. |
| **Drop-in for the baseline** | partial: same integrated LUFS quantity as pyebur128/pyloudnorm from one function call, but a different API and no M/S/LRA/true peak in Python |

## Gotchas

- The binding forcecasts to C-contiguous float32: float64 input (soundfile.read's default) is silently copied and rounded to float32, and transposed views are copied, even though the C++ core accepts double, int16 and int32 directly.
- Input must be (samples, channels). A channels-first (C, n) array always raises ValueError, because it reads as C frames, under the 400 ms minimum, so torch-style data must be transposed first, which the forcecast turns into a copy.
- The vendor/thread-pool submodule URL is SSH (git@github.com:bshoshany/thread-pool.git), so a recursive HTTPS clone without SSH keys fails to fetch it.
- Package tests cover only two fixture files at a 0.1 LU tolerance plus argument checks; the EBU Tech 3341/3342 conformance cases live in upstream nomonosound/libloudness, not in this repository.

## Known shortcomings

- Off-baseline (pyebur128 and pyloudnorm). One time.time() run per library on 5 minutes of mono 48 kHz white noise with no CPU or compiler stated; the gain over pyebur128 is 1.7x (derived from page data). The core is Nomono's libloudness, which is not catalogued.
- Enricher (e110, 2026-10-05): no correctness bug; C stands. The speedup is real and explained: libebur128's ebur128_calc_gating_block re-sums the 400 ms window on every 100 ms hop (each sample read four times) while libloudness sums each 100 ms subblock once; the K-filter is identical. Minor benchmark flaw: loudness runs Histogram mode (0.1 LU bins) while pyebur128 runs the MODE_I block list; gating cost is small against 14.4M samples, and pyebur128 takes float32 directly, so otherwise like for like. The binding exposes integrated LUFS only, holds the GIL, silently copies float64 to float32 (forcecast), has two fixtures at +/-0.1 LU (EBU 3341/3342 tests only upstream), the thread-pool submodule uses an SSH URL, and addFramesMT does not parallelize integrated loudness alone.

## Caveats and trade-offs

Numbers come from one run per library timed with time.time() on synthetic white noise, with no CPU, compiler or OS stated; the chart was made with loudness 0.1.0 (current release 0.2.0). The closest baseline, pyebur128 (a Cython wrapper of libebur128), is only about 1.7x slower; the larger ratios are against pure-Python or torch implementations, and the pyloudness time includes WAV file I/O. The C++ core is Nomono's libloudness (MIT, described upstream as a C++ port of libebur128 with optimizations), compiled into this Python package; use from C++ means vendoring src/loudness. Off the category's FFmpeg/x264/Opus baselines (audio loudness metering).

C++ core based on Nomono's libloudness (not libebur128) with Python bindings; follows ITU BS.1770 gating; Python-first API, so use from C++ means vendoring the core.

## Maintenance

Small (33 stars, 68 commits, 0 open issues, one open PR) but maintained, with release 0.2.0 on 2025-12-26 adding Python 3.14 wheels; MIT-licensed, with a C++ core that is easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party numbers from a public script, scripts/performance_benchmark.py, which produced images/execution_time_comparison.png (chart title 'Execution times for 5 minutes of mono 48 kHz audio'); the five timings match the README alt text. No CPU, compiler or flags are stated and each library is timed once with time.time(), so C.
- **Verifier notes:** The record said no audio length or script was given; both exist (scripts/performance_benchmark.py, chart title gives 5 min mono 48 kHz). Single-shot timings make the 1.7x over pyebur128 noisy but not invalid. Upstream nomonosound/libloudness (10 stars, MIT) carries no numbers of its own and is not in the catalog, so no duplicate.
- **Fields the verifier corrected:** `benchmark_url`, `workload`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** first-party benchmark vs pyebur128
- **Pages the verifier opened:**
  - <https://github.com/iver56/loudness>
  - <https://github.com/iver56/loudness/tree/main>
  - <https://github.com/iver56/loudness/commits/main>
  - <https://github.com/iver56/loudness/tree/main/scripts>
  - <https://github.com/iver56/loudness/tree/main/tests>
  - <https://github.com/iver56/loudness/tree/main/src/loudness>
  - <https://raw.githubusercontent.com/iver56/loudness/HEAD/README.md>
  - <https://raw.githubusercontent.com/iver56/loudness/main/images/execution_time_comparison.png>
  - <https://raw.githubusercontent.com/iver56/loudness/HEAD/scripts/performance_benchmark.py>
  - <https://raw.githubusercontent.com/iver56/loudness/HEAD/src/loudness.cpp>
  - <https://raw.githubusercontent.com/iver56/loudness/HEAD/src/loudness/meter.hpp>
  - <https://raw.githubusercontent.com/iver56/loudness/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/iver56/loudness/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/iver56/loudness/HEAD/LICENSE>
  - <https://github.com/nomonosound/libloudness>
- **Sources the enricher read:**
  - <https://github.com/iver56/loudness>
  - <https://github.com/iver56/loudness/tree/main/src/loudness>
  - <https://github.com/iver56/loudness/tree/main/tests>
  - <https://github.com/iver56/loudness/pulls>
  - <https://github.com/iver56/loudness/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/iver56/loudness/HEAD/README.md>
  - <https://raw.githubusercontent.com/iver56/loudness/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/iver56/loudness/HEAD/scripts/performance_benchmark.py>
  - <https://raw.githubusercontent.com/iver56/loudness/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/iver56/loudness/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/iver56/loudness/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/iver56/loudness/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/iver56/loudness/HEAD/src/loudness.cpp>
  - <https://raw.githubusercontent.com/iver56/loudness/HEAD/src/loudness/meter.hpp>
  - <https://raw.githubusercontent.com/iver56/loudness/HEAD/src/loudness/defines.hpp>
  - <https://raw.githubusercontent.com/iver56/loudness/HEAD/src/loudness/utils.hpp>
  - <https://raw.githubusercontent.com/iver56/loudness/HEAD/src/loudness/constants.hpp>
  - <https://raw.githubusercontent.com/iver56/loudness/HEAD/src/loudness/k-filter.hpp>
  - <https://raw.githubusercontent.com/iver56/loudness/HEAD/src/loudness/k-filter.cpp>
  - <https://raw.githubusercontent.com/iver56/loudness/HEAD/src/loudness/bs1770-calculator.hpp>
  - <https://raw.githubusercontent.com/iver56/loudness/HEAD/src/loudness/bs1770-calculator.cpp>
  - <https://raw.githubusercontent.com/iver56/loudness/HEAD/src/loudness/interpolator.hpp>
  - <https://raw.githubusercontent.com/iver56/loudness/HEAD/src/loudness/detail/meter-impl.hpp>
  - <https://raw.githubusercontent.com/iver56/loudness/HEAD/src/loudness/detail/meter-impl.cpp>
  - <https://raw.githubusercontent.com/iver56/loudness/HEAD/tests/test_integrated_loudness.py>
  - <https://pypi.org/pypi/loudness/json>
  - <https://raw.githubusercontent.com/jodhus/pyebur128/HEAD/src/pyebur128/pyebur128.pyx>
  - <https://raw.githubusercontent.com/jodhus/pyebur128/HEAD/setup.py>
  - <https://raw.githubusercontent.com/jiixyj/libebur128/HEAD/ebur128/ebur128.c>
  - <https://github.com/nomonosound/libloudness>
  - <https://github.com/nomonosound/libloudness/tree/main/test>
  - <https://raw.githubusercontent.com/nomonosound/libloudness/HEAD/README.md>
  - <https://raw.githubusercontent.com/nomonosound/libloudness/HEAD/test/test-ebur128.cpp>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/iver56/loudness`) · [data/wave10/enrich/raw/github_com_iver56_loudness.json](../../../data/wave10/enrich/raw/github_com_iver56_loudness.json) (enrichment confidence 0.8)

</details>
