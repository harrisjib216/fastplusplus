# pedalboard

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python (C++17/JUCE core)` · `GPL-3.0` · 🟢 active

> Spotify's Python audio-effects and audio-file library on a JUCE C++17 core; first-party claims of beating pySoX, SoxBindings and librosa.load.

| | |
|---|---|
| **Beats** | pySoX (Python wrapper that runs the SoX command-line program), SoxBindings (Python bindings to libsox) and librosa.load (audio file reading) |
| **Claimed result** | README, under 'Even when only using one thread': processes audio up to 300x faster than pySoX for single transforms and 2-5x faster than SoxBindings (via iCorv/pedalboard_with_tfdata), and reads audio files up to 4x faster than librosa.load 'in many cases'. The cited SoxBindings notebook times six single effects on LJ Speech at 22.05 kHz: SoxBindings 73.1/130.8/38.1/38.6/76.7/105.2 s against pedalboard 11.6/26.3/10.9/10.8/32.2/20.9 s (Compressor, Chorus, HighpassFilter, LowpassFilter, Phaser, Reverb), i.e. 2.4-6.3x (derived from page data). But pedalboard ran with tf.data num_parallel_calls=AUTOTUNE while SoxBindings ran serially, and a single Pedalboard effect chain was slower than the SoxBindings chain (357.2 s vs 305.2 s, 0.85x, derived from page data); only splitting the chain into parallel tf.data stages won (82.1 s). PR #85 first claimed 'up to 20x faster than librosa.load in certain cases', later tempered; no method given. |
| **Workload** | Python audio effect processing for single transforms and audio file reading, compared against pySoX, SoxBindings and librosa.load. |
| **Metric** | throughput |
| **Adoption** | 6.3k stars; on PyPI as pedalboard |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/spotify/pedalboard) · [benchmark](https://github.com/spotify/pedalboard) |

## Verdict

The README's 300x (vs pySoX) and 4x (vs librosa.load) figures have no published method, corpus or machine; PR #85 first claimed up to 20x versus librosa.load 'without resampling', and a later commit 'tempered' the claim. The only public numbers are a third-party notebook (iCorv/pedalboard_with_tfdata: Python 3.8.11, pedalboard version and hardware not recorded) on LJ Speech at 22.05 kHz with six default-parameter effects. There SoxBindings took 38.1-130.8 s and pedalboard 10.8-32.2 s (2.4-6.3x, derived from page data). However, pedalboard ran with tf.data num_parallel_calls=AUTOTUNE while SoxBindings ran serially (the notebook says soxbindings does not allow multi-threading). No single-thread, like-for-like measurement exists behind the README's 'even when only using one thread' wording.

## Use it when

- ML data augmentation in Python (tf.data, PyTorch DataLoader threads) that applies built-in effects to many clips. The GIL is released during processing, so threads scale across cores without multiprocessing, provided each thread owns its own plugin instances.
- Replacing pySoX code that runs the sox command line once per transform. Most of the claimed 300x is removed subprocess and temporary-file overhead, so short clips gain the most.
- Reading, transcoding or resampling large files from Python in constant memory: chunked AudioFile.read(), resampled_to() with O(1) memory, and WAV/FLAC/OGG/MP3 encoding without FFmpeg.
- Batch rendering through third-party VST3 or Audio Unit plugins from a Python script on macOS, Windows or Linux.

## Skip it when

- C++ projects. The core is a pybind11 extension (pedalboard_native) with no C++ API or standalone library, so use JUCE's dsp classes or Rubber Band directly.
- Closed-source or permissively licensed products. pedalboard is GPL-3.0 and statically bundles JUCE (GPLv3 or commercial), the VST3 SDK, Rubber Band and FFTW (GPLv2+), and LAME (relicensed to GPLv3 here).
- Pipelines that must match SoX output. The effects are JUCE algorithms, not SoX ports, and the SoxBindings comparison ran each library's own effect at default parameters, so the outputs differ.
- float64 processing. process() casts float64 input to float32 (astype) and always returns float32.
- x86-64 CPUs without AVX. Linux x86-64 wheels require AVX, and Linux wheels up to 0.9.21 were built with -march=native and could crash with SIGILL on import on older CPUs (issue #454, fixed by PR #511 in September 2026).

## How it is fast

The work runs in compiled C++ inside one process. pySoX instead launches the SoX program per transform, and most of the 300x figure is that overhead. process.h copies the array once into a juce::AudioBuffer&lt;float&gt;. It then runs every plugin in place over 8192-sample blocks (DEFAULT_BUFFER_SIZE) with the GIL released (py::gil_scoped_release), so several Python threads can use separate cores. The DSP is JUCE's dsp module (for example juce::dsp::Reverb, a Freeverb-style design) plus Rubber Band for pitch and time stretching. Rubber Band's FFTs use vendored FFTW with AVX codelets on Linux and vDSP on macOS. The extension builds as a CMake Release with -O3 and interprocedural optimisation, and Linux x86 wheels target -mavx. File reads decode through JUCE readers, including a patched MP3 decoder, straight into the output buffer with the GIL released.

## Compared with alternatives

No catalogued sibling offers a Python effect chain or plugin host, so pick pedalboard for effects and for file I/O and encoding from Python. audioFlux is the catalogued choice for spectral feature extraction against librosa. libsoxr or r8brain-free-src are the C/C++ choices when the job is resampling throughput and quality rather than effects.

## Integration

| | |
|---|---|
| **Form** | module (Python C++ extension, platform wheels on PyPI; vendored C/C++ dependencies compiled in statically) |
| **Dependencies** | numpy at runtime. Bundled and statically linked: JUCE 6, VST3 SDK, Rubber Band, FFTW 3 (Linux only), LAME/mpglib, libgsm, dr_wav, pybind11. A Linux source build also needs freetype and ALSA development packages. |
| **Minimum toolchain** | Python 3.10+ (requires-python &gt;=3.10; tested 3.10-3.15). Building from source needs C++17, CMake 3.18+, scikit-build-core &gt;=0.5 and pybind11 &gt;=2.9. |
| **Platforms** | Linux x86-64 (AVX required) and aarch64 (manylinux and musllinux wheels); macOS x86-64, arm64 and universal2; Windows amd64 |
| **Thread safety** | The GIL is released while plugins process and while files are read. Each Plugin holds a std::mutex, and process() locks every plugin in a chain in pointer order, so threads sharing one plugin instance run one at a time. Using the same instance twice in one chain raises an error. Concurrent reads from one AudioFile object raise 'Another thread is currently reading from this AudioFile'. |
| **Drop-in for the baseline** | no |

## Gotchas

- A Pedalboard or plugin shared across threads serializes on its mutex. Build one chain per worker. The iCorv notebook's 'Pedalboard Chain' row shared one board across tf.data AUTOTUNE workers, and it is the only row where pedalboard lost to SoxBindings (357.2 s vs 305.2 s).
- reset=True is the default, so each call clears delay lines and reverb tails. Chunked or streaming processing needs reset=False (README quick start). Plugins with latency get compensated output that is padded and then trimmed.
- Every call copies the input array into a JUCE buffer and copies the result back, and float64 input costs an extra conversion. For very short clips the copies and Python call overhead are a large share of the time.
- MP3 frames and duration are estimates until the file has been read through (exact_duration_known is False), so the length can change during reading.

## Known shortcomings

- Python with a C++17/JUCE core via pybind11 (language-filter mismatch); weak category fit (audio effects, no resampling). README compares only pySoX (which spawns a SoX subprocess), SoxBindings and librosa.load, with no FFmpeg and no machine; the 300x and 4x are first-party. The cited SoxBindings notebook (iCorv) ran Pedalboard in parallel (tf.data AUTOTUNE) against serial SoxBindings, contradicting the README's 'one thread', and a single Pedalboard chain was slower there (357.2 s vs 305.2 s).
- The iCorv chain row shares one Pedalboard across tf.data AUTOTUNE workers and the per-plugin std::mutex in process.h serialises it, which is the only row lost to SoxBindings (357.2 against 305.2 s); float64 input is cast to float32. Linux wheels up to 0.9.21 were built -march=native and SIGILL on old CPUs (#454, PR #511); AVX is now required. No C++ API; GPL-3.0.

## Caveats and trade-offs

First-party claims without benchmark code, corpus, machine or compiler in the repo; no FFmpeg, libsamplerate or resampling comparison anywhere in the README, so the video-audio category fit is weak (the baselines are Python audio-effect and file-loading wrappers, not FFmpeg, x264/x265 or Opus). The 300x figure against pySoX includes pySoX launching a SoX subprocess and file I/O per transform, so it mostly measures process overhead. The only public numbers behind the SoxBindings claim (iCorv/pedalboard_with_tfdata notebook) ran pedalboard multi-threaded via tf.data AUTOTUNE against serial SoxBindings, contradicting the README's 'even when only using one thread', compared SoX and JUCE effects at default parameters (different algorithms), and showed a single Pedalboard chain slower than SoxBindings (357.2 s vs 305.2 s). The librosa figure traces to PR #85 ('up to 20x... in certain cases', later tempered to 4x) with no method. The C++ core is a pybind11 extension module (C++17, -O3 release builds) and is not shipped as a standalone C++ library; C++ users would use JUCE directly. GPL-3.0, with JUCE, Rubber Band and LAME linked in under GPL terms.

Python-first API on a JUCE C++ core; GPL-3.0 (copyleft, commercial licensing through JUCE terms may apply); releases the GIL so multiple cores can be used; wheels cover macOS, Windows and Linux.

## Maintenance

Actively maintained by Spotify: v0.9.25 released 2026-09-09, last commit 2026-09-23, 6.3k stars, 85 open issues and 58 open PRs. It is easy for Python users (pip wheels), but GPL-3.0 and not reusable as a C++ library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification C, tier now C.
- **Tier reason:** The README gives first-party headline figures (300x vs pySoX, 4x vs librosa.load) with no benchmark code, corpus, machine or flags in the repo; the 2-5x SoxBindings figure comes from a third-party notebook (iCorv/pedalboard_with_tfdata, 6 stars) with no hardware stated, which is not a well-known independent suite. Tier stays C; the verdict is a downgrade because the README's 'even when only using one thread' framing is overstated.
- **Verifier notes:** The README compares pedalboard against pySoX, SoxBindings and librosa.load only, with no machine stated; the 300x and 4x figures are first-party, and the 2-5x figure is a small third-party notebook whose method contradicts the README's one-thread framing. Kept at C with the measured-work mismatch documented; the category fit to video-audio is loose. verify.py does not apply 'language' from corrections, so record it as a decision override.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/spotify/pedalboard>
  - <https://github.com/spotify/pedalboard/commits>
  - <https://github.com/spotify/pedalboard/tree/master/scripts>
  - <https://github.com/spotify/pedalboard/issues?q=librosa%20faster>
  - <https://github.com/spotify/pedalboard/pull/85>
  - <https://raw.githubusercontent.com/spotify/pedalboard/HEAD/README.md>
  - <https://raw.githubusercontent.com/spotify/pedalboard/HEAD/setup.py>
  - <https://github.com/iCorv/pedalboard_with_tfdata>
  - <https://raw.githubusercontent.com/iCorv/pedalboard_with_tfdata/HEAD/README.md>
  - <https://raw.githubusercontent.com/iCorv/pedalboard_with_tfdata/HEAD/pedalboard_with_tfdata.ipynb>
  - <https://raw.githubusercontent.com/iCorv/pedalboard_with_tfdata/HEAD/plots/transform_effect_duration.png>
  - <https://raw.githubusercontent.com/iCorv/pedalboard_with_tfdata/HEAD/plots/effect_chain.png>
- **Sources the enricher read:**
  - <https://github.com/spotify/pedalboard>
  - <https://github.com/spotify/pedalboard/commits/master>
  - <https://github.com/spotify/pedalboard/tree/master/pedalboard>
  - <https://github.com/spotify/pedalboard/tree/master/pedalboard/io>
  - <https://github.com/spotify/pedalboard/issues>
  - <https://github.com/spotify/pedalboard/issues?q=is%3Aissue+benchmark+OR+slow+OR+performance>
  - <https://github.com/spotify/pedalboard/issues/212>
  - <https://github.com/spotify/pedalboard/issues/416>
  - <https://github.com/spotify/pedalboard/issues/454>
  - <https://github.com/spotify/pedalboard/pull/85>
  - <https://github.com/spotify/pedalboard/pull/511>
  - <https://raw.githubusercontent.com/spotify/pedalboard/HEAD/README.md>
  - <https://raw.githubusercontent.com/spotify/pedalboard/HEAD/setup.py>
  - <https://raw.githubusercontent.com/spotify/pedalboard/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/spotify/pedalboard/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/spotify/pedalboard/HEAD/pedalboard/process.h>
  - <https://raw.githubusercontent.com/spotify/pedalboard/HEAD/pedalboard/Plugin.h>
  - <https://raw.githubusercontent.com/spotify/pedalboard/HEAD/pedalboard/JucePlugin.h>
  - <https://raw.githubusercontent.com/spotify/pedalboard/HEAD/pedalboard/BufferUtils.h>
  - <https://raw.githubusercontent.com/spotify/pedalboard/HEAD/pedalboard/plugins/Reverb.h>
  - <https://raw.githubusercontent.com/spotify/pedalboard/HEAD/pedalboard/version.py>
  - <https://raw.githubusercontent.com/spotify/pedalboard/HEAD/pedalboard/io/AudioFileInit.h>
  - <https://raw.githubusercontent.com/spotify/pedalboard/HEAD/pedalboard/io/ReadableAudioFile.h>
  - <https://raw.githubusercontent.com/spotify/pedalboard/HEAD/pedalboard/io/StreamResampler.h>
  - <https://raw.githubusercontent.com/iCorv/pedalboard_with_tfdata/HEAD/pedalboard_with_tfdata.ipynb>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/spotify/pedalboard`) · [data/wave10/enrich/raw/github_com_spotify_pedalboard.json](../../../data/wave10/enrich/raw/github_com_spotify_pedalboard.json) (enrichment confidence 0.75)

</details>
