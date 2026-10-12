# fast-vad

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust (Python bindings via maturin)` · `Apache-2.0 OR MIT` · 🟢 active

> Rust/Python voice activity detector using a logistic regression over 8 FFT bands; first-party chart puts it 2-11x past webrtcvad.

| | |
|---|---|
| **Beats** | webrtcvad (Google WebRTC voice activity detector, C) |
| **Claimed result** | Processing speed relative to Silero ONNX: fast_vad offline 721x, fast_vad streaming 129x, webrtcvad 63x; README says significantly faster than WebRTC VAD and the page says the streaming path is about 2x faster than WebRTC VAD (offline about 11.4x, derived from page data: 721/63). |
| **Workload** | Relative processing speed of voice activity detection on speech audio (AVA-Speech and LibriVAD are the accuracy sets; which audio the speed figure used is not stated), with Silero VAD ONNX as the 1x reference. fast_vad offline (VAD.detect, all frames in parallel with rayon on 16 threads) and streaming (VadStateful, one 32 ms frame at a time) against webrtcvad through its Python binding (webrtcvad-wheels in the dev dependencies). The detectors do different work: fast_vad scores 32 ms (512-sample at 16 kHz) Hann-windowed FFT frames with an 8-band log-energy logistic-regression model, while webrtcvad uses its own model on 10, 20 or 30 ms frames; the frame size used for webrtcvad is not stated. |
| **Metric** | throughput |
| **Hardware** | Ryzen 7700X (8 cores, 16 threads) |
| **Adoption** | 28 stars, 1 fork; crates.io fast-vad 0.2.1 (801 downloads); PyPI fast-vad 0.2.1 |
| **Last commit** | 2026-03-25 |
| **Links** | [repository](https://github.com/AtharvBhat/fast-vad) · [benchmark](https://raw.githubusercontent.com/AtharvBhat/fast-vad/HEAD/docs/README.md) |

## Verdict

One first-party bar chart (docs/assets/processing-speed.png, Ryzen 7700X, 8 cores and 16 threads) gives speed relative to Silero ONNX: fast_vad offline 721x, streaming 129x, webrtcvad 63x. That makes streaming about 2x webrtcvad and offline about 11.4x (derived from page data), but the offline figure uses all 16 threads against single-threaded webrtcvad. The Python harness that produced the chart is not in the repo (bench_py/ is absent and excluded from the sdist; notebooks/ is gitignored), so the webrtcvad frame size (10, 20 or 30 ms), whether the float-to-int16 PCM conversion webrtcvad needs was inside the timing, Silero's ONNX thread settings, the audio used, compiler and flags are all unknown. The public criterion benches (bench_rs) time fast_vad alone on synthetic noise.

## Use it when

- Batch pre-segmentation of large 16 kHz or 8 kHz speech corpora (ASR or diarisation pipelines) where throughput matters more than best-in-class F1 and all cores are free for the offline rayon path.
- Python pipelines that already hold float32 numpy audio and want segment boundaries without loading ONNX Runtime or a neural model (the Silero ONNX comparison in the docs is 721x slower than the offline path and 129x slower than streaming).
- Clean or read speech close to LibriVAD, where the docs report F1 about 0.93-0.94 from 0 to 20 dB SNR with precision steady near 0.908.
- Rust services that need a cheap, allocation-free per-frame streaming detector with 32 ms decision granularity.

## Skip it when

- C or C++ projects: it is a Rust crate plus a Python wheel with no C API, so it needs your own FFI layer. WebRTC VAD is C and easy to embed.
- Hard real-world audio where accuracy dominates: on AVA-Speech the docs report F1 0.680 against 0.738 for Silero (webrtcvad 0.669), and the presets were tuned on LibriVAD read speech.
- Sample rates other than 8 or 16 kHz (no 32/48 kHz as in WebRTC VAD), multichannel input, or decisions finer than 32 ms (WebRTC VAD takes 10, 20 or 30 ms frames).
- Latency-critical turn-taking: streaming onset needs min_speech frames (2 frames, 64 ms, in normal mode) on top of the 32 ms frame, and offset waits for min_silence plus hangover.
- Projects that need a stable or mature dependency: version 0.2.x, PyPI classifier 'Development Status :: 3 - Alpha', 28 stars, one breaking API change already (0.2.0 return types).

## How it is fast

The model is tiny: per frame a SIMD Hann window, one realfft real-to-complex FFT, power summed into 8 log-energy bands (about 94-4000 Hz), then a 32-weight logistic regression (raw, noise-normalised, first- and second-delta features, weights compiled in as f32x8 constants from the portable `wide` crate) and a threshold. In the offline path the window/FFT/band stage runs over all frames in parallel with rayon; the classifier is then a sequential scan, because the per-band noise floor (an EMA with alpha 0.01) only updates on frames judged silent. The streaming path reuses preallocated window, FFT output and scratch buffers, so a frame does no allocation.

## Compared with alternatives

No other voice activity detector is catalogued. The video-audio siblings are codecs, resamplers, RTP stacks and denoisers, so none competes with it. A VAD classifies audio rather than encoding it, so it sits in this category only as audio analysis; judge it against webrtcvad and Silero, not against libopus or FFmpeg.

## Integration

| | |
|---|---|
| **Form** | crate (fast-vad on crates.io, cdylib + lib) and Python abi3 wheel (fast-vad on PyPI) |
| **Dependencies** | rayon, realfft, wide, thiserror, plus pyo3 0.28 (extension-module, abi3-py311), numpy and ndarray, which are unconditional even for pure-Rust users; Python package needs numpy &gt;= 2.0 |
| **Minimum toolchain** | Rust edition 2024 (Rust 1.85+); Python &gt;= 3.11 |
| **Platforms** | Wheels for Linux x86_64 and aarch64 (manylinux_2_28), macOS x86_64 and arm64, Windows x64; CI runs Rust tests on Ubuntu x64/arm64, macOS Intel/arm64 and Windows. SIMD is portable through `wide`, so no specific ISA is required. |
| **Thread safety** | VAD methods take &self and fan out on rayon's global pool; VadStateful is one instance per stream (&mut self, reset_state() to reuse). The Python bindings release the GIL during detection. |
| **Drop-in for the baseline** | no |

## Gotchas

- The offline VAD and streaming VadStateful smooth labels differently: offline applies hangover and then drops short speech and silence runs over the whole label array, which looks ahead; streaming uses a causal state machine. The same audio can therefore get different labels from the two paths.
- The noise floor is seeded from the first frame's band energies, and afterwards only moves on frames classified as silence (alpha 0.01, roughly a 3.2 s time constant at 32 ms frames, derived from the code). A stream that starts mid-speech begins with a speech-level floor. Call reset_state() between streams.
- Python input must be a contiguous float32 numpy array: float64 (the default dtype of soundfile.read), int16 or int32 raise TypeError. Trailing samples that do not fill a frame are ignored by detect_frames, and detect() copies the last frame's label onto them.
- Secondary write-ups describe the result as '721x realtime', but the docs chart's axis is a speedup factor relative to Silero ONNX, not a real-time factor; no absolute timings are published.

## Known shortcomings

- Rust (language-filter mismatch). The 721x/129x/63x figures are against Silero (a neural VAD, a different model class) on a Ryzen 7700X with the comparison harness (bench_py/, notebooks/) gitignored; bench_rs/benches/vad_bench.rs times fast_vad alone on noise. Detectors differ (32 ms FFT plus logistic regression vs webrtcvad's own model on 10/20/30 ms frames) and the offline run uses 16 threads; the fair figure is streaming at about 2x webrtcvad. Baseline webrtcvad is not a listed incumbent.
- Weak category fit: a voice-activity detector is audio classification, not a codec. The 721x offline figure is 16 threads against single-threaded webrtcvad; the 2x streaming figure is Python per-frame calls with webrtcvad frame size and int16 conversion placement unknown; bench_py/ is uncommitted (sdist-excluded, not gitignored) and notebooks/ is gitignored, so the harness is absent. Offline (look-ahead) and streaming (causal) smoothing differ, so labels can differ; the noise floor is seeded from the first frame; pyo3 and numpy are unconditional dependencies for Rust users; no C API. The blog's '721x realtime' misreads the chart, which is speedup versus Silero ONNX.

## Caveats and trade-offs

The comparison harness is not published (pyproject.toml excludes bench_py/\*\* and notebooks/\*\*, and .gitignore ignores notebooks/), so how webrtcvad was driven (per-frame Python calls, frame size) cannot be checked; numbers are bar-chart multipliers only, with no absolute timings, compiler or flags. The public bench_rs criterion benches (vad_bench.rs, filterbank_bench.rs) time fast_vad alone on LCG-generated noise. The offline 721x figure uses rayon across all 16 threads of the Ryzen 7700X while webrtcvad is single-threaded, so the about 11.4x offline gap is not per-core; the streaming path (about 2x webrtcvad, derived from page data: 129/63) is the like-for-like single-stream figure. The detectors are different models with different frame sizes, so this is a task-level rather than same-algorithm comparison. On AVA-Speech fast_vad F1 is 0.680 against 0.738 (Silero) and 0.669 (webrtcvad); presets were tuned on LibriVAD. Baseline webrtcvad is not in the FFmpeg, x264, Opus list. Rust crate outside the search's C++ language filter.

Logistic-regression VAD on 8 log-energy bands (16 kHz and 8 kHz only, 32 ms frames); no C API (Rust and Python only); offline path uses rayon across cores. Accuracy is lower than Silero on hard audio.

## Maintenance

Active (0.2.1 released 2026-03-25 on crates.io and PyPI, 83 commits, CI on Linux, macOS and Windows) and dual MIT/Apache-2.0, so it is easy to adopt from Rust or Python; it is still alpha-labelled, has a single author and its speed evidence is first-party only.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** docs/README.md and docs/assets/processing-speed.png give first-party relative speeds (fast_vad offline 721x, streaming 129x, webrtcvad 63x, Silero ONNX 1x) on a Ryzen 7700X, but the harness that produced them (bench_py/ and notebooks/, gitignored and absent from the repo) is unpublished and no compiler, flags or absolute timings are given. The public bench_rs/benches/vad_bench.rs only times fast_vad itself on synthetic noise, with no webrtcvad or Silero arm.
- **Verifier notes:** Numbers on the page match the record (721x, 129x, 63x, about 2x streaming over WebRTC VAD). baseline_in_list stays false. Rust crate found on crates.io, which does not fit the C++ language filter; language field set.
- **Fields the verifier corrected:** `workload`, `caveats`, `stars_or_usage`
- **Pages the verifier opened:**
  - <https://github.com/AtharvBhat/fast-vad>
  - <https://github.com/AtharvBhat/fast-vad/commits>
  - <https://github.com/AtharvBhat/fast-vad/tree/main/bench_rs>
  - <https://github.com/AtharvBhat/fast-vad/tree/main/bench_rs/benches>
  - <https://github.com/AtharvBhat/fast-vad/tree/main/docs>
  - <https://github.com/AtharvBhat/fast-vad/tree/main/tests>
  - <https://raw.githubusercontent.com/AtharvBhat/fast-vad/HEAD/README.md>
  - <https://raw.githubusercontent.com/AtharvBhat/fast-vad/HEAD/docs/README.md>
  - <https://raw.githubusercontent.com/AtharvBhat/fast-vad/main/docs/assets/processing-speed.png>
  - <https://raw.githubusercontent.com/AtharvBhat/fast-vad/main/bench_rs/Cargo.toml>
  - <https://raw.githubusercontent.com/AtharvBhat/fast-vad/main/bench_rs/benches/vad_bench.rs>
  - <https://raw.githubusercontent.com/AtharvBhat/fast-vad/main/Cargo.toml>
  - <https://raw.githubusercontent.com/AtharvBhat/fast-vad/main/pyproject.toml>
  - <https://raw.githubusercontent.com/AtharvBhat/fast-vad/main/.gitignore>
  - <https://raw.githubusercontent.com/AtharvBhat/fast-vad/main/CHANGELOG.md>
  - <https://github.com/wiseman/py-webrtcvad>
  - <https://crates.io/api/v1/crates/fast-vad>
  - <https://pypi.org/pypi/fast-vad/json>
- **Sources the enricher read:**
  - <https://github.com/AtharvBhat/fast-vad>
  - <https://raw.githubusercontent.com/AtharvBhat/fast-vad/HEAD/README.md>
  - <https://raw.githubusercontent.com/AtharvBhat/fast-vad/HEAD/docs/README.md>
  - <https://raw.githubusercontent.com/AtharvBhat/fast-vad/main/docs/assets/processing-speed.png>
  - <https://raw.githubusercontent.com/AtharvBhat/fast-vad/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/AtharvBhat/fast-vad/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/AtharvBhat/fast-vad/HEAD/build.rs>
  - <https://raw.githubusercontent.com/AtharvBhat/fast-vad/HEAD/.gitignore>
  - <https://raw.githubusercontent.com/AtharvBhat/fast-vad/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/AtharvBhat/fast-vad/HEAD/fast_vad.pyi>
  - <https://raw.githubusercontent.com/AtharvBhat/fast-vad/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/AtharvBhat/fast-vad/HEAD/src/vad/mod.rs>
  - <https://raw.githubusercontent.com/AtharvBhat/fast-vad/HEAD/src/vad/detector.rs>
  - <https://raw.githubusercontent.com/AtharvBhat/fast-vad/HEAD/src/vad/filterbank.rs>
  - <https://raw.githubusercontent.com/AtharvBhat/fast-vad/HEAD/src/vad/simd.rs>
  - <https://raw.githubusercontent.com/AtharvBhat/fast-vad/HEAD/src/vad/constants.rs>
  - <https://raw.githubusercontent.com/AtharvBhat/fast-vad/HEAD/bench_rs/Cargo.toml>
  - <https://raw.githubusercontent.com/AtharvBhat/fast-vad/HEAD/bench_rs/benches/vad_bench.rs>
  - <https://raw.githubusercontent.com/AtharvBhat/fast-vad/HEAD/bench_rs/benches/filterbank_bench.rs>
  - <https://raw.githubusercontent.com/AtharvBhat/fast-vad/HEAD/tests/test_vad.py>
  - <https://raw.githubusercontent.com/AtharvBhat/fast-vad/HEAD/.github/workflows/ci.yml>
  - <https://github.com/AtharvBhat/fast-vad/tree/main/tests>
  - <https://github.com/AtharvBhat/fast-vad/tree/main/src/vad>
  - <https://github.com/AtharvBhat/fast-vad/tree/main/.github/workflows>
  - <https://pypi.org/pypi/fast-vad/json>
  - <https://raw.githubusercontent.com/wiseman/py-webrtcvad/master/README.rst>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/atharvbhat/fast-vad`) · [data/wave10/enrich/raw/github_com_atharvbhat_fast_vad.json](../../../data/wave10/enrich/raw/github_com_atharvbhat_fast_vad.json) (enrichment confidence 0.75)

</details>
