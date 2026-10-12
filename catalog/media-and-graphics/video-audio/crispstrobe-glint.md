# glint

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Clean-room MIT C++17 AAC-LC/MP3/Opus encoder suite; AAC encode about 2-10x faster than FFmpeg's native AAC encoder.

| | |
|---|---|
| **Beats** | FFmpeg native AAC encoder (libavcodec aac); the same league also times Fraunhofer FDK AAC, Apple afconvert, vo-aacenc and LAME 3.100 -q 2 (MP3) |
| **Claimed result** | README: fastest encoder in the AAC league at every quality tier, about 272x / 168x realtime at -q speed / -q best on an M1 (MP3 about 260x / 34x). League log rows for ffmpeg native AAC vs glint -q normal: speech 128 kbps 56x vs 169x, electronic 128 kbps 46x vs 214x, electronic 256 kbps 25x vs 246x, quartet 128 kbps 89x vs 196x, industrial 128 kbps 84x vs 175x (about 2.1x to 9.8x faster across the 12 league rows, derived from page data). In the same log FDK reaches 105x-175x and Apple 80x-181x. |
| **Workload** | Encoding 6 audio clips (speech, electronic, quartet, industrial, piano, castanets) to AAC-LC at 128 and 256 kbps with the project's tests/compare_encoders.py league; speed reported as multiples of real time. |
| **Metric** | throughput |
| **Hardware** | README says Apple M1 for the headline speed numbers; the league log itself does not state a CPU |
| **Compiler and flags** | README build instructions use CMake -DCMAKE_BUILD_TYPE=Release; the compiler and the flags used for the league run are not stated |
| **Adoption** | 2 stars |
| **Last commit** | 2026-08-19 |
| **Links** | [repository](https://github.com/CrispStrobe/glint) · [benchmark](https://raw.githubusercontent.com/CrispStrobe/glint/HEAD/tests/aac_league_v0.8.txt) |

## Verdict

The author's tests/compare_encoders.py encoded six local clips (speech, electronic, quartet, industrial, piano, castanets; the script's defaults are 60 s files apart from castanets) to 128 and 256 kbps ADTS. Each encode is one subprocess timed by wall clock, including process start-up and file I/O, on an unstated machine (the README names an M1, and PLAN.md places FFmpeg 8.1 on the same box). glint -q normal ran 2.1x-9.8x faster than ffmpeg's default native AAC encoder, 1.2x-2.5x faster than FDK and 1.0x-3.0x faster than Apple afconvert (derived from page data). Two noise signals stand out. glint-normal and glint-best produce identical output at these rates, yet their timings differ by up to 21% (quartet 128 kbps: 196x vs 238x). ffmpeg alone spans 25x-89x on clips of the same length. The Release flags (-O3 -march=native -ffast-math, LTO) are public in CMakeLists.txt; the compiler version and exact CPU are not. No correctness bug was found behind the numbers. The latest commit (2026-08-19) fixes glint's AAC decoder for foreign streams, which the league does not use, since ffmpeg decodes every stream for scoring.

## Use it when

- You need an AAC-LC encoder under a plain permissive licence: ffmpeg's native AAC is LGPL, FDK's licence is not OSI-approved, and vo-aacenc is unmaintained and ranks last on quality in the same league.
- Batch or server transcoding to 128-256 kbps stereo AAC where FFmpeg's native encoder is the incumbent. In the v0.8 league glint -q normal ran 175x-273x realtime against ffmpeg's 25x-89x, with better mean NMR on all 6 clips at 128 kbps.
- Embedded or no-FPU targets: GLINT_MODE=fixed fits the AAC encoder in 47.4 KB of RAM (plus about 30 KB of transient stack) with integer per-coefficient paths at -q speed. There are ready-made benchmark projects for Raspberry Pi Pico and ESP32, but no on-silicon throughput has been published.
- One small library that must both encode and decode MP3/AAC/Opus and decode Vorbis/FLAC, from C, C++, Python, Rust, Dart or the web.

## Skip it when

- Best quality at 128 kbps on speech or electronic music: Apple (afconvert) and FDK lead on noise-to-mask there (speech NMR -6.9/-5.4 dB vs glint -3.6; electronic -9.9/-11.4 vs -4.3).
- HE-AAC, HE-AACv2, multichannel (more than 2 channels) or MP4/M4A output: the AAC encoder is AAC-LC only, 1-2 channels, and emits ADTS frames.
- Opus encoding of speech at low rates: the Opus encoder is CELT-only (no SILK or hybrid modes), so libopus remains the choice there.
- Production use that needs an outside track record: the first commits date from mid-2026, there are 2 stars and one author, the crate has 98 downloads, and every quality and speed number is first-party.

## How it is fast

The AAC rate loop computes each band's scalefactor in closed form from the psychoacoustic mask (noise target proportional to mask^0.6, with a 10 dB minimum-SNR cap), then bisects one integer offset to fit the bit budget, followed by a single measure-and-correct pass. FFmpeg's default two-loop search iterates quantization and scalefactors band by band. Each bisection step counts bits exactly but cheaply: band_costs() scores all 11 Huffman codebooks in two passes over a band, zero bands cost O(1), and optimal sectioning is a dynamic program over (band, book) with closed-form side-info counts, so no count-only emission is needed. PLAN.md A3 credits that change with a 52-54% cut in encode time at identical output. The MDCT is a radix-2 N/4-point complex FFT with pre- and post-twiddles; |x|^0.75 is cached per frame. Release builds use -O3 -march=native -ffast-math with LTO.

## Compared with alternatives

Pick glint over remade_ffmpeg_rs (also faster than FFmpeg's native AAC encoder, but a Rust crate) when you want a C/C++ library with a C ABI and an AAC quality league against Apple and FDK. For MP3, pick it over Shine when you need a psychoacoustic model: it is ahead of LAME 3.100 on PEAQ ODG on 8 of 10 clips at 128 kbps, and its fixed build needs about 64 KB against Shine's 96 KB, both per glint's README. Shine and SuperLAME remain the MP3-only incumbents in this catalog.

## Integration

| | |
|---|---|
| **Form** | static lib and shared lib (CMake), plus a CLI; Rust crate glint-audio builds the C++ from source; vcpkg port, ESP-IDF component |
| **Dependencies** | none for the library (C++17 standard library; std::thread pool only for MP3 scalefactor search, GLINT_NO_THREADS for bare metal); Python, numpy and ffmpeg only for the test and league scripts |
| **Minimum toolchain** | C++17, CMake 3.16; the Rust crate declares rust-version 1.70 |
| **Platforms** | any C++17 target; README says CI builds release libraries for 9 platforms and shows Android NDK, iOS and aarch64 Linux cross builds; fixed-point builds for Cortex-M0+/M3, RP2040 and ESP32; wasm via Emscripten |
| **Thread safety** | Not documented for the AAC encoder; contexts are independent handles. glint_set_threads is process-wide and affects only the MP3 scalefactor search (byte-identical output at any thread count). |
| **Drop-in for the baseline** | no |

## Gotchas

- A zero-initialized glint_aac_config selects GLINT_QUALITY_SPEED (no psychoacoustic shaping), and the current CLI also defaults to -q speed, although the README's usage text says the default is normal. Set quality explicitly.
- Encoder behaviour can change through process environment variables read once into function statics (GLINT_AAC_NO_TNS, GLINT_AAC_SNRMIN, GLINT_AAC_ALPHA, GLINT_AAC_ALPHA_S), so the same binary can produce different streams on different hosts.
- glint_aac_flush is required and returns the tail frames; the README gives the encoder delay as 2048 samples. Gapless playback needs that trim, since ADTS carries no delay metadata.
- At 128-256 kbps stereo, -q best and -q normal gave identical quality metrics on all 12 league rows: above 56 kbps per channel, best differs only in extra walk iterations on frames just after a transient. Do not pay for best expecting better output at these rates.

## Known shortcomings

- First-party AAC league (tests/aac_league_v0.8.txt, 2.1x-9.8x over ffmpeg-aac at matched or better NMR) timed by tests/compare_encoders.py as one subprocess wall clock per run with start-up included; compiler, flags and CPU are missing. The README's '168x at -q best' is not in the v0.8 log (which shows 164-283x).
- The league log is a single wall-clock run under what PLAN.md calls moderate load: glint-normal and glint-best produce identical output at 128 and 256 kbps yet their times differ by up to 21% (quartet 128 kbps: 196x versus 238x), so the ratios carry about plus or minus 20% noise. The README 272x/168x comes from PLAN A3 (300 s speech, min of 5, glint and Apple only, no ffmpeg). The ffmpeg baseline is the default coder (probably 8.1 twoloop); FFmpeg master switched its default to the NMR trellis coder on 2026-07-01 and -aac_coder fast was never timed. Versus FDK 1.2-2.5x and Apple 1.0-3.0x (derived from page data). Release flags are public (-O3 -march=native -ffast-math, LTO) but compiler version and CPU are missing; a zeroed glint_aac_config and the CLI both default to -q speed although the README says normal.

## Caveats and trade-offs

Very new project (first commits July 2026, 322 commits, 2 stars) with first-party measurements only; compiler and flags not stated, CPU only named as M1 in README prose (the league includes afconvert, so it ran on macOS). The harness (tests/compare_encoders.py) times one subprocess.run per encoder and clip with time.time(), so each 'enc x' figure is a single wall-clock run that includes process start-up, WAV parsing and file output; ffmpeg's heavier start-up weighs more on short clips, and clip lengths are not published (the clips are local files). The README's '\~272x/168x realtime at -q speed/-q best' does not match the v0.8 log, where glint-best ranges 164x-283x (mean about 228x, derived from page data), so the prose figure comes from another run. Quality is not traded for the win over ffmpeg: glint -q normal beats ffmpeg-aac on mean NMR on all 6 clips at 128 kbps, but trails Apple and FDK on speech and electronic. vo-aacenc is about as fast as glint -q normal on some rows (castanets 256 kbps 260x vs 241x) at much worse quality. MP3 comparison against LAME is quality-first, not speed.

Clean-room MP3, AAC-LC and Opus encoders plus Opus, Vorbis, FLAC, MP3 and AAC decoders; C ABI with Python, Rust and Dart bindings; fixed-point builds for MCUs. Opus encoder is CELT-only. AAC quality at 128 kbps trails Apple and FDK on speech and electronic clips (noise-to-mask), beats FFmpeg native AAC.

## Maintenance

Active (322 commits, last 2026-08-19, GitHub releases up to v0.9.0, crate glint-audio 0.11.0 with 98 downloads), MIT, 0 issues and 0 PRs ever filed. Small and self-contained enough to vendor, but it is a mid-2026 one-author project with no outside users yet.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party league log (tests/aac_league_v0.8.txt) produced by the project's own public harness tests/compare_encoders.py, with ffmpeg native AAC in every table; no compiler, flags or CPU model in the log (the README prose names only 'an M1'), so it cannot reach A and is not independent.
- **Verifier notes:** Every quoted ffmpeg-aac vs glint-normal row matches the log, and the 2.1x-9.8x range checks out across all 12 rows (lowest industrial 128 kbps 175/84, highest electronic 256 kbps 246/25). Speed is wall-clock of whole CLI runs, single sample, so treat the ratios as indicative. Metadata (MIT, 2 stars, last commit 2026-08-19, not a fork) confirmed.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/CrispStrobe/glint/HEAD/tests/aac_league_v0.8.txt>
  - <https://raw.githubusercontent.com/CrispStrobe/glint/HEAD/README.md>
  - <https://raw.githubusercontent.com/CrispStrobe/glint/HEAD/tests/compare_encoders.py>
  - <https://github.com/CrispStrobe/glint>
  - <https://github.com/CrispStrobe/glint/commits>
- **Sources the enricher read:**
  - <https://github.com/CrispStrobe/glint>
  - <https://github.com/CrispStrobe/glint/commits/main>
  - <https://github.com/CrispStrobe/glint/releases>
  - <https://github.com/CrispStrobe/glint/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/CrispStrobe/glint/HEAD/README.md>
  - <https://raw.githubusercontent.com/CrispStrobe/glint/HEAD/tests/aac_league_v0.8.txt>
  - <https://raw.githubusercontent.com/CrispStrobe/glint/HEAD/tests/compare_encoders.py>
  - <https://raw.githubusercontent.com/CrispStrobe/glint/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/CrispStrobe/glint/HEAD/PLAN.md>
  - <https://raw.githubusercontent.com/CrispStrobe/glint/HEAD/cli/main.cpp>
  - <https://raw.githubusercontent.com/CrispStrobe/glint/HEAD/include/glint/glint.h>
  - <https://raw.githubusercontent.com/CrispStrobe/glint/HEAD/src/aac_encoder.cpp>
  - <https://raw.githubusercontent.com/CrispStrobe/glint/HEAD/src/aac_coder.cpp>
  - <https://raw.githubusercontent.com/CrispStrobe/glint/HEAD/src/aac_mdct.cpp>
  - <https://crates.io/api/v1/crates/glint-audio>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libavcodec/aacenc.c>
  - <https://github.com/FFmpeg/FFmpeg/commits/master/libavcodec/aacenc.c>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/crispstrobe/glint`) · [data/wave10/enrich/raw/github_com_crispstrobe_glint.json](../../../data/wave10/enrich/raw/github_com_crispstrobe_glint.json) (enrichment confidence 0.75)

</details>
