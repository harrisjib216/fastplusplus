# aubio

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `GPL-3.0-or-later` · 🟢 active

> GPL C audio-analysis library whose Python aubio.source loads compressed audio 1.5-2.3x faster than audioread's ffmpeg subprocess.

| | |
|---|---|
| **Beats** | audioread (FFmpegAudioFile for the load benchmark, audioread.audio_open with its auto-selected backend for the metadata benchmark; compressed formats decode through an ffmpeg subprocess) |
| **Claimed result** | Numbers derived from the benchmark's results/\*.pickle files (derived from page data; mean over the 16 durations). Load rows are the minimum of 3 timeit repeats of 3 loads of one file per duration. Load to numpy, aubio vs audioread+ffmpeg: wav 0.064 vs 0.657 s (about 10x; this wav row comes from bmcfee's Feb 2023 dev-machine run), mp4 0.044 vs 0.101 (about 2.3x), mp3 0.068 vs 0.103 (about 1.5x), flac 0.067 vs 0.071 (about 1.06x, a tie). Versus librosa: mp3 0.068 vs 0.131 (about 1.9x), mp4 0.044 vs 0.111 (about 2.5x), wav 0.064 vs 0.289 (about 4.5x). Versus soundfile on wav: 0.064 vs 0.103. Metadata rows are seconds per info call, and each call opens the file 4 times. Aubio vs audioread: mp3 0.0015 vs 0.098 (about 66x), flac 0.0015 vs 0.098 (about 66x), mp4 0.0030 vs 0.106 (about 35x), ogg 0.0046 vs 0.200 (about 44x), wav 0.040 vs 0.099 (about 2.5x). Aubio is slower in several rows. Flac load: 0.067 vs soundfile 0.045 and librosa 0.039. Wav load: 0.064 vs scipy 0.014. Metadata vs torchaudio: flac 0.0015 vs 0.000062, mp3 0.0015 vs 0.00054, ogg 0.0046 vs 0.00063, wav 0.040 vs 0.000039. Metadata vs soundfile: flac 0.0015 vs 0.00053, ogg 0.0046 vs 0.0041, wav 0.040 vs 0.0008. Aubio has no row in the ogg load pickle. |
| **Workload** | Python audio-loading benchmark: time to decode a mono noise file (1 to 151 s long, 16 durations, one file per duration) into a numpy array with aubio.source (hop_size 1024) versus audioread's FFmpegAudioFile, librosa, soundfile and others; a second benchmark times metadata queries (samplerate, channels, samples, duration). |
| **Metric** | latency |
| **Adoption** | 3.8k stars |
| **Last commit** | 2026-04-10 |
| **Links** | [repository](https://github.com/aubio/aubio) · [benchmark](https://github.com/faroit/python_audio_loading_benchmark) |

## Verdict

In the third-party faroit/python_audio_loading_benchmark, aubio 0.4.9's aubio.source (hop 1024) was timed against audioread 2.1.9's FFmpegAudioFile on mono 44.1 kHz white-noise files of 1-151 s, taking the minimum of 3 timeit repeats of 3 loads. Hardware and the aubio build are unstated. aubio loaded mp4 about 2.3x and mp3 about 1.5x faster and tied on flac; the 10x wav ratio comes from a separate 2023 rerun on a machine with slow ffmpeg startup. Metadata queries were 35-66x faster on compressed formats, mostly avoided process spawns. soundfile, librosa, scipy and torchaudio beat aubio on several rows.

## Use it when

- Python pipelines that load many short MP3 or AAC/MP4 files and currently use audioread's ffmpeg backend: mean load 0.068 vs 0.103 s (mp3) and 0.044 vs 0.101 s (mp4) over files of 1-151 s.
- Metadata scans (sample rate, channels, length) over compressed files where the alternative spawns ffmpeg: 0.0015 vs 0.098 s per info call on mp3 and flac.
- Block-wise streaming reads (hop-sized blocks, seek, URL sources) that feed aubio's own onset, pitch, tempo or MFCC analysis without a separate decoder dependency.
- C or C++ programs that want one source API over libav, libsndfile, CoreAudio or a dependency-free WAV reader, and can accept GPL-3.0-or-later.

## Skip it when

- WAV or FLAC loading: scipy loaded wav in 0.014 vs 0.064 s, and soundfile (0.045 s) and librosa (0.039 s) beat aubio's 0.067 s on flac.
- Metadata-only workloads where torchaudio or soundfile are available: torchaudio answered in 0.000062 s vs 0.0015 s on flac, and soundfile in 0.0008 s vs 0.040 s on wav.
- Closed-source or permissively licensed products: GPL-3.0-or-later applies to anything that links it.
- Projects that need a maintained wheel: PyPI has only the 0.4.9 sdist (2019-02-08), and fixes for Python 3.12 (issue #394, commit 885e316), NumPy 2 and GCC 14 exist only on unreleased master.
- Files longer than about 71.6 minutes read through the libav backend, if you rely on source.duration (see gotchas).

## How it is fast

Decoding runs in-process. When built with libav, the source opens the file with libavformat/libavcodec and converts to float with libswresample in C; other builds use CoreAudio, libsndfile or a built-in WAV reader. audioread's FFmpegAudioFile spawns an ffmpeg process per file and pipes raw int16 bytes back. The Python wrapper reuses one output vector per source object rather than allocating a new array for each block. Most of the measured advantage is avoided process spawn and pipe overhead, not a faster codec.

## Compared with alternatives

Pick aubio over pedalboard or Symphonia when you need onset, pitch or beat analysis in the same C library as an in-process libav reader. For pure file-reading speed, pedalboard (Python) or Symphonia (Rust decoders) are the catalogued options; for librosa-style feature extraction, compare libsonare and audioFlux.

## Integration

| | |
|---|---|
| **Form** | static/shared C library (waf, plus a Meson build merged on master) and a Python extension module (PyPI aubio 0.4.9, sdist only) |
| **Dependencies** | none required (built-in wavread/wavwrite and Ooura FFT); optional libavcodec/libavformat/libavutil/libswresample, libsndfile, libsamplerate, fftw3 or fftw3f, rubberband, libvorbis, libFLAC, JACK, Intel IPP, Apple Accelerate/CoreAudio; the Python module needs NumPy |
| **Minimum toolchain** | C compiler (the Python build assumes C99 variadic macros); Python 3 with NumPy, with Python 3.12 and NumPy 2 support only on unreleased master |
| **Platforms** | Linux, macOS, Windows, Cygwin and iOS per the README; no SIMD requirement |
| **Thread safety** | not documented; each source object owns its own libav context and a reused output buffer, so use one object per thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Correctness bug in the measured code path: aubio_source_avcodec_get_duration() casts libavformat's int64 microsecond duration to the 32-bit uint_t before dividing ((uint_t)duration / 1e6), so source.duration wraps for files longer than 4294.97 s (about 71.6 min). The value is also only a container estimate. The benchmark's load_aubio allocates np.zeros(f.duration) and slices blocks into it, so that loader is only safe for short files; the measured files were at most 151 s, so the published numbers are unaffected.
- source() returns the same reused vector on every call (Py_source_do hands back self-&gt;read_to), zero-padded beyond `read`. Copy the samples before the next call, or every block will alias one buffer.
- The harness is lopsided in small ways. load_ar_ffmpeg overwrites sig on each buffer and returns only the last one, so the audioread baseline never assembles the full array. Only the last file in each duration folder is timed. Every info call reopens the file four times, which charges audioread four ffmpeg spawns. aubio's libav source multiplies max_analyze_duration by 100 before avformat_find_stream_info, and its wav info call (0.040 s) was about 27x slower than its mp3 call (0.0015 s). All test audio is synthetic white noise.
- Which backend you get depends on the build: the PyPI sdist uses pkg-config to look for libav and sndfile and otherwise falls back to the built-in WAV reader (WAV only). Heap out-of-bounds reads (#409, #410) were fixed on master in 2025 but are not in 0.4.9; #435 (global OOB read in pitchyinfft) and #439 (source_avcodec leak) are open.

## Known shortcomings

- Independent faroit/python_audio_loading_benchmark pickles match, but the win is over audioread's per-file ffmpeg subprocess (process-spawn overhead, not faster codecs); two runs on different machines mixed (np_wav pickle from a 2023 dev machine, the rest from a 2021 server), README charts not regenerated, Docker setup broken, no CPU, OS or build info. Slower than torchaudio and soundfile on most metadata rows (torchaudio 2-1000x faster) and slower than soundfile, librosa and scipy on flac or wav loads; no ogg load row. GPL-3.0-or-later.
- Enricher: aubio_source_avcodec_get_duration casts the int64 microsecond duration to a 32-bit uint_t before dividing, so duration wraps past 4294.97 s (about 71.6 min); the benchmark's np.zeros(f.duration) depends on it but the test files max out at 151 s. Harness: load_ar_ffmpeg keeps only the last buffer (the baseline never assembles the array); only the last file per folder is timed; libav open uses max_analyze_duration x100 (wav info 0.040 vs mp3 0.0015 s); white-noise input; the win is mostly ffmpeg process spawn. PyPI has only the 0.4.9 sdist (2019); Python 3.12, NumPy 2 and OOB-read fixes (#409, #410) are only on master; #435 OOB and #439 leak open.

## Caveats and trade-offs

This is an independent community benchmark (faroit/python_audio_loading_benchmark, 152 stars, last commit 2023-12-19), not run by the aubio project. The README shows only bar charts on a log time axis; the exact numbers come from the repo's results/benchmark_np_&lt;ext&gt;.pickle and benchmark_metadata_&lt;ext&gt;.pickle files, read with a restricted unpickler that whitelists pandas and numpy classes and executes no code. The numbers mix two runs on different machines. PR #8 (merged 2021-09-06, faroit's 'server') produced every pickle except np_wav, with 2020-21 library versions (librosa 0.8 era). PR #26 (bmcfee's 'dev machine', merged 2023-12-19) replaced only results/benchmark_np_wav.pickle, with librosa 0.10, soundfile 0.12.1 and scipy 1.9. The README version table therefore describes only the wav load row, and the README charts were not regenerated after #26 ('create new plots later'). On that machine ffmpeg was slow to start: audioread took at least 0.28 s for 3 loads of a 1 s wav file, against 0.024 s for flac in the 2021 run, which inflates the 10x wav ratio. The repo states no hardware, CPU model, OS or compiler. The Dockerfile (python:3.6.8) cannot install the pinned tensorflow 2.11 and librosa 0.10, and bmcfee reported the docker instructions failing, so the environment is not reproducible as published. The aubio package's build configuration (whether its decoder backend is libav) is not stated; aubio 0.4.9 (2019-02-08, still the latest PyPI release) ships only as an sdist. Harness quirks: the load benchmark records the minimum of 3 timeit repeats with number=3 (seconds for 3 loads) and keeps only the last file of each duration folder. The metadata benchmark records the mean seconds per info call over every file and 3 rounds, and each info call opens the file 4 times. The audioread baseline spawns an ffmpeg process per file (FFmpegAudioFile for loads, audio_open's auto-selected backend for metadata), so aubio's win is largely process-spawn overhead rather than faster codecs; aubio itself decodes mp3/mp4 through libav (FFmpeg's libraries) when built with it. Aubio is a competitive loader, not the fastest one. libsndfile (soundfile), scipy and librosa beat it on wav or flac loads, and torchaudio and soundfile beat it on most metadata queries (torchaudio by 2-1000x). Aubio's own repo has only python/demos/demo_reading_speed.py with no published numbers, and its README makes no speed claim. The 'ffmpeg or standard codec' baseline was a Haiku guess; the rows compared here are audioread's ffmpeg wrapper, not the ffmpeg library called from C.

GPL-3.0-or-later, so copyleft for anything linking it. The fast decode path depends on the aubio build having libav (ffmpeg), libsndfile or CoreAudio enabled; the Python API streams hop-sized blocks (loop in Python), so very small hop sizes cost interpreter time. Python package is the code measured, not the C library alone.

## Maintenance

Master is active again (0.5.0-alpha, last commit 2026-04-10; fixes for Python 3.12, NumPy 2, GCC 14 and FFmpeg 7 issues), but the only PyPI release is the 2019 0.4.9 sdist, and maintainer replies in issue #422 give no release date. LedFx publishes a GPL fork with wheels (aubio-ledfx 0.4.12 on PyPI, cp311 and later), whose README lists libsndfile, libsamplerate and fftw3 as dependencies but not FFmpeg.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party harness, not by the aubio project (faroit/python_audio_loading_benchmark: benchmark_np.py, benchmark_metadata.py and loaders.py are public; its authors are faroit and hagenw, and librosa maintainer bmcfee re-ran the wav load). Its results/\*.pickle files hold numbers that rank aubio ahead of audioread's ffmpeg-subprocess reader and librosa. It falls short of A: there is no CPU model, OS or build configuration ('our server', 'my dev machine'), and aubio 0.4.9 is an sdist-only package whose decoder backend depends on the build. Tier B follows the pigzbench precedent.
- **Verifier notes:** All claimed numbers match the pickles; I re-derived them myself. Confirmed at B as an independent harness. Shortcomings: the win is over an ffmpeg-subprocess wrapper, so it is mostly spawn overhead. The data mixes a 2023 wav-only rerun on bmcfee's dev machine with 2021 server runs for the other formats. No hardware is stated and the Docker setup is broken. torchaudio and soundfile beat aubio on most metadata rows, and soundfile, librosa and scipy beat it on flac or wav loads. Metadata confirmed: GPL-3.0-or-later, 3.8k stars, last commit 2026-04-10, not a fork, not archived.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-112 (wave 10); enricher w10 pair-024
- **Pages the verifier opened:**
  - <https://github.com/faroit/python_audio_loading_benchmark>
  - <https://github.com/faroit/python_audio_loading_benchmark/tree/master/results>
  - <https://github.com/faroit/python_audio_loading_benchmark/commits/master>
  - <https://github.com/faroit/python_audio_loading_benchmark/pull/26>
  - <https://github.com/faroit/python_audio_loading_benchmark/pull/26/files>
  - <https://github.com/faroit/python_audio_loading_benchmark/pull/8/files>
  - <https://raw.githubusercontent.com/faroit/python_audio_loading_benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/faroit/python_audio_loading_benchmark/HEAD/benchmark_np.py>
  - <https://raw.githubusercontent.com/faroit/python_audio_loading_benchmark/HEAD/benchmark_metadata.py>
  - <https://raw.githubusercontent.com/faroit/python_audio_loading_benchmark/HEAD/loaders.py>
  - <https://raw.githubusercontent.com/faroit/python_audio_loading_benchmark/HEAD/generate_audio.sh>
  - <https://raw.githubusercontent.com/faroit/python_audio_loading_benchmark/HEAD/Dockerfile>
  - <https://raw.githubusercontent.com/faroit/python_audio_loading_benchmark/HEAD/requirements.txt>
  - <https://raw.githubusercontent.com/faroit/python_audio_loading_benchmark/HEAD/results/benchmark_np_wav.pickle>
  - <https://raw.githubusercontent.com/faroit/python_audio_loading_benchmark/HEAD/results/benchmark_np_mp3.pickle>
  - <https://raw.githubusercontent.com/faroit/python_audio_loading_benchmark/HEAD/results/benchmark_np_mp4.pickle>
  - <https://raw.githubusercontent.com/faroit/python_audio_loading_benchmark/HEAD/results/benchmark_np_flac.pickle>
  - <https://raw.githubusercontent.com/faroit/python_audio_loading_benchmark/HEAD/results/benchmark_np_ogg.pickle>
  - <https://raw.githubusercontent.com/faroit/python_audio_loading_benchmark/HEAD/results/benchmark_metadata_mp3.pickle>
  - <https://raw.githubusercontent.com/faroit/python_audio_loading_benchmark/HEAD/results/benchmark_metadata_wav.pickle>
  - <https://github.com/aubio/aubio>
  - <https://github.com/aubio/aubio/commits/master>
  - <https://raw.githubusercontent.com/aubio/aubio/HEAD/README.md>
  - <https://raw.githubusercontent.com/aubio/aubio/HEAD/python/demos/demo_reading_speed.py>
  - <https://pypi.org/pypi/aubio/json>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/aubio/aubio/HEAD/README.md>
  - <https://raw.githubusercontent.com/aubio/aubio/HEAD/src/io/source.c>
  - <https://raw.githubusercontent.com/aubio/aubio/HEAD/src/io/source_avcodec.c>
  - <https://raw.githubusercontent.com/aubio/aubio/HEAD/src/io/source_wavread.c>
  - <https://raw.githubusercontent.com/aubio/aubio/HEAD/src/io/source_sndfile.c>
  - <https://raw.githubusercontent.com/aubio/aubio/HEAD/src/types.h>
  - <https://raw.githubusercontent.com/aubio/aubio/HEAD/src/aubio_priv.h>
  - <https://raw.githubusercontent.com/aubio/aubio/HEAD/python/ext/py-source.c>
  - <https://raw.githubusercontent.com/aubio/aubio/HEAD/python/lib/moresetuptools.py>
  - <https://raw.githubusercontent.com/aubio/aubio/HEAD/python/lib/gen_external.py>
  - <https://raw.githubusercontent.com/aubio/aubio/HEAD/python/demos/demo_reading_speed.py>
  - <https://raw.githubusercontent.com/aubio/aubio/HEAD/setup.py>
  - <https://raw.githubusercontent.com/aubio/aubio/HEAD/wscript>
  - <https://raw.githubusercontent.com/aubio/aubio/HEAD/VERSION>
  - <https://raw.githubusercontent.com/aubio/aubio/HEAD/ChangeLog>
  - <https://raw.githubusercontent.com/aubio/aubio/HEAD/scripts/get_waf.sh>
  - <https://github.com/aubio/aubio/issues?q=is%3Aissue+ffmpeg+OR+numpy+OR+python+3.12+OR+build>
  - <https://github.com/aubio/aubio/issues/422>
  - <https://github.com/aubio/aubio/issues/394>
  - <https://pypi.org/pypi/aubio/json>
  - <https://pypi.org/pypi/aubio-ledfx/json>
  - <https://github.com/LedFx/aubio-ledfx>
  - <https://raw.githubusercontent.com/faroit/python_audio_loading_benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/faroit/python_audio_loading_benchmark/HEAD/loaders.py>
  - <https://raw.githubusercontent.com/faroit/python_audio_loading_benchmark/HEAD/benchmark_np.py>
  - <https://raw.githubusercontent.com/faroit/python_audio_loading_benchmark/HEAD/benchmark_metadata.py>
  - <https://raw.githubusercontent.com/faroit/python_audio_loading_benchmark/HEAD/generate_audio.sh>
  - <https://raw.githubusercontent.com/faroit/python_audio_loading_benchmark/HEAD/requirements.txt>
  - <https://raw.githubusercontent.com/faroit/python_audio_loading_benchmark/HEAD/Dockerfile>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/aubio/aubio`) · [data/wave10/enrich/raw/github_com_aubio_aubio.json](../../../data/wave10/enrich/raw/github_com_aubio_aubio.json) (enrichment confidence 0.75)

</details>
