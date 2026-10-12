# clownresampler

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `0BSD` · 🟢 active

> Single-header C89 Lanczos-windowed-sinc resampler for 16-bit PCM, 0BSD; no speed claim or measurement against libsamplerate or anything else.

| | |
|---|---|
| **Beats** | libsamplerate (nearest incumbent; no baseline is named or timed by the project) |
| **Claimed result** | None. The README is three sentences (single-file library, C89, 0BSD, windowed-sinc with Lanczos window) and the header comments make no speed claim and name no other library. |
| **Workload** | None measured. Single-header C89 audio resampler using integer 16.16 fixed-point positions and a Lanczos-windowed sinc kernel (1024 samples per lobe table), low-level and streaming high-level APIs. |
| **Metric** | throughput |
| **Adoption** | 37 stars, 3 forks |
| **Last commit** | 2026-06-27 |
| **Links** | [repository](https://github.com/Clownacy/clownresampler) |

## Verdict

Nothing was measured: the README (three sentences), the header comments and the two FLAC-to-raw functional tests contain no timing code, no speed claim and no named baseline; libsamplerate is only the nearest incumbent assumed by the catalogue.

## Use it when

- C89 or freestanding-ish targets (consoles, emulators, retro ports) that need a resampler with no dependencies and a public-domain-equivalent licence.
- Streaming 16-bit integer PCM at ordinary ratios (for example 32 or 44.1 kHz to 48 kHz) where a short Lanczos-3 kernel is acceptable quality.
- Code bases without an FPU in the audio path: after the one-time table build (which uses double sin()), resampling is integer-only.
- Projects that want to vendor one header and read all of the resampler (about 1,400 lines, most of it comments, examples and integer typedefs).

## Skip it when

- When speed matters and must be shown: no benchmark, no comparison with libsamplerate, libsoxr, speexdsp or r8brain exists, and the scalar per-frame loop with a division and an indirect callback per output frame is not built for throughput.
- Float or 24/32-bit input, or high-fidelity mastering: input is cc_s16l only and the default kernel is 3-lobe Lanczos with nearest-entry table lookup; no frequency-response or SNR figures are published.
- Extreme downsampling or low-pass ratios with many channels in the high-level API (see gotchas: the fixed 0x1000-sample input buffer is not checked at init).
- More than 16 channels (CLOWNRESAMPLER_MAXIMUM_CHANNELS) or callers that need variable-ratio downsampling wider than the ratio given at HighLevel_Init.

## How it is fast

Nothing in the repository measures speed; the design simply keeps the per-sample work small and integer. Read positions advance in 16.16 fixed point, the Lanczos kernel is precomputed once into a 3-lobe table of 1024 entries per lobe (nearest-entry lookup, no interpolation), and each output frame is a scalar multiply-accumulate over 2 x 3 x stretch taps followed by one integer division to normalise by the summed kernel weights (a source TODO says 'divisions are slow'). There is no SIMD, no polyphase decomposition and no block processing: the output callback is invoked once per output frame.

## Compared with alternatives

Pick it over libsoxr, r8brain-free-src or SampleRateTap only when a single C89 0BSD header for 16-bit PCM matters more than measured speed and quality; those siblings carry third-party or first-party throughput tables against libsamplerate and this one carries none. LibFResample and the sst-basic-blocks LanczosResampler are the closer small-footprint alternatives, the former with published numbers.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (C standard library: assert, fabs, sin, memset, memmove; all overridable by macros) |
| **Minimum toolchain** | C89 for the C API; the C++ wrapper is gated on C++11 but declares an inline variable, which is a C++17 feature |
| **Platforms** | any (portable scalar C, no SIMD) |
| **Thread safety** | Not documented; each resampler keeps its own state struct and one const ClownResampler_Precomputed table may be shared by several resamplers, with no global mutable state in the C API |
| **Drop-in for the baseline** | no |

## Gotchas

- From the code: ClownResampler_HighLevel_Init never checks that twice the stretched kernel radius fits the fixed cc_s16l input_buffer[0x1000], while ClownResampler_HighLevel_Adjust does. When 2 x ceil(3 x input_rate / min(input, output, low-pass rate)) x channels exceeds 4096 samples (for example 8 channels at about 86:1, or 16 channels at about 43:1), the leading-padding read and the memmove in HighLevel_Resample run past the buffer and the refill size (0x1000 - 2R x channels) / channels wraps as size_t; at exactly 4096 the refill asks for 0 frames and resampling stops silently.
- With the default C89 typedefs cc_s32l is 'signed long', so on LP64 Linux/macOS the 6,144-entry kernel table is 48 KB instead of 24 KB; define CC_USE_C99_INTEGERS to get 32-bit int_least32_t entries.
- The 'C++11 interface' (added 2026-06-27) uses an inline variable for its shared Precomputed table, so strict C++11/14 builds warn or fail; its Init and Adjust wrappers also discard the cc_bool result, so an unsupported channel count or ratio goes unnoticed. The low-level API documents but does not check the 16-channel limit (its stack accumulator array is sized 16).
- Output frames are unclamped 32-bit values; the caller must clamp to 16 bits, as the examples do. Hissing on long runs of a constant non-zero sample was fixed only in April 2025 (after one reverted attempt).

## Known shortcomings

- No benchmark, speed claim or baseline anywhere in the repo; tests decode FLAC only with no timing; 16-bit PCM input only. Kept at D under the keep-and-document rule. 0BSD, 37 stars.
- Enricher: nothing is measured; scalar 3-lobe Lanczos with one division and one callback per output frame. Bug found by code reading: HighLevel_Init lacks the buffer-fit check that HighLevel_Adjust has, so when 2 x ceil(3 x in/min(in,out,lowpass)) x channels exceeds 4096 the fixed input_buffer[0x1000] overflows and the refill size wraps as size_t, and at exactly 4096 resampling stops silently (edge-case ratios only, e.g. 8 channels at about 86:1). C89 long typedefs make the kernel table 48 KB on LP64 (define CC_USE_C99_INTEGERS); the 'C++11 interface' uses a C++17 inline variable and drops Init/Adjust errors; the low-level API does not check the 16-channel limit.

## Caveats and trade-offs

No numbers and no comparison against libsamplerate, soxr or speexdsp anywhere: the repo has only functional tests (tests/test-high-level.c and tests/test-low-level.c decode a FLAC file with dr_flac and resample it, no timing code; the MP3 decoding is in the header's commented-out examples), no benchmark directory, and no commit message about speed (recent commits add a C++11 interface and fix hissing). One web search found no third-party benchmark. The faster-than claim rests on nothing; the lead's libsamplerate, soxr and speexdsp baselines are untested, and the design (scalar integer inner loop on 16-bit PCM input only, a Lanczos kernel table built with doubles at init, fixed 0x1000-sample high-level input buffer with a TODO to size it by kernel radius) is aimed at portability (C89) rather than speed. Notability is low (37 stars, 3 forks). 0BSD licence (public-domain-equivalent, no patent grant).

Zero-Clause BSD, single header, no dependencies, written in C89; integer 16.16 fixed-point positions and 17.15 fixed-point normalisation (the repo description says integer-only). In the high-level API the downsampling ratio must not be wider than the one given at init. Only a Lanczos kernel, not the quality ladder of libsamplerate or soxr. The source has a TODO about a remaining per-output-frame division ('divisions are slow').

## Maintenance

Lightly maintained by its single author (104 commits, last 2026-06-27 adding a C++ interface and a flush function; two closed issues), 0BSD and small enough to vendor, but treat it as a portable convenience resampler rather than a proven fast one.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now D.
- **Tier reason:** benchmark_url is null and none exists: the README (7 lines) and the 1376-line clownresampler.h make no speed claim and name no other resampler, tests/test-high-level.c and tests/test-low-level.c contain no timing code, no commit message mentions speed, and one web search found no third-party benchmark; no numbers anywhere, so D.
- **Verifier notes:** No-baseline, no-numbers entry kept at D per the keep-and-document rule (the prompt's not-notable-tier-d reject would apply otherwise). Shortcomings: no benchmark or speed claim anywhere, no baseline timed, 16-bit integer input only, 37 stars.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** any comparison against libsamplerate or soxr; any measurement against libsamplerate or soxr
- **Pages the verifier opened:**
  - <https://github.com/Clownacy/clownresampler>
  - <https://github.com/Clownacy/clownresampler/commits>
  - <https://github.com/Clownacy/clownresampler/tree/master/tests>
  - <https://raw.githubusercontent.com/Clownacy/clownresampler/HEAD/README.md>
  - <https://raw.githubusercontent.com/Clownacy/clownresampler/HEAD/clownresampler.h>
  - <https://raw.githubusercontent.com/Clownacy/clownresampler/HEAD/clownresampler.c>
  - <https://raw.githubusercontent.com/Clownacy/clownresampler/HEAD/LICENCE.txt>
  - <https://raw.githubusercontent.com/Clownacy/clownresampler/HEAD/tests/test-high-level.c>
  - <https://raw.githubusercontent.com/Clownacy/clownresampler/HEAD/tests/test-low-level.c>
- **Sources the enricher read:**
  - <https://github.com/Clownacy/clownresampler>
  - <https://github.com/Clownacy/clownresampler/commits>
  - <https://github.com/Clownacy/clownresampler/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/Clownacy/clownresampler/HEAD/README.md>
  - <https://raw.githubusercontent.com/Clownacy/clownresampler/HEAD/clownresampler.h>
  - <https://raw.githubusercontent.com/Clownacy/clownresampler/HEAD/clownresampler.c>
  - <https://raw.githubusercontent.com/Clownacy/clownresampler/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Clownacy/clownresampler/HEAD/LICENCE.txt>
  - <https://raw.githubusercontent.com/Clownacy/clownresampler/HEAD/tests/test-high-level.c>
  - <https://raw.githubusercontent.com/Clownacy/clownresampler/HEAD/tests/test-low-level.c>
  - <https://github.com/Clownacy/clownmdemu-frontend>
  - <https://raw.githubusercontent.com/Clownacy/clownmdemu-frontend/HEAD/.gitmodules>
  - <https://github.com/Clownacy/clownmdemu-frontend-common>
  - <https://raw.githubusercontent.com/Clownacy/clownmdemu-frontend-common/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/Clownacy/clownmdemu-frontend-common/HEAD/mixer.h>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/clownacy/clownresampler`) · [data/wave10/enrich/raw/github_com_clownacy_clownresampler.json](../../../data/wave10/enrich/raw/github_com_clownacy_clownresampler.json) (enrichment confidence 0.75)

</details>
