# SampleRateTap (async engine)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++20 near-unity ASRC for clock-drift bridging; its datapath beats libsamplerate MEDIUM/BEST at near-unity ratios.

| | |
|---|---|
| **Beats** | libsamplerate 0.2.2 (Secret Rabbit Code, MEDIUM and BEST converters) |
| **Claimed result** | COMPARISON.md (host x86, 2026-09-25, million output frames/s, median of 5) reports SampleRateTap 3.1-3.9x faster than libsamplerate 0.2.2 (stereo/mono; 1.5x at 8 channels) at the \~120 dB tier and 6.1x at the \~140 dB tier, with about 2-3.6x less latency. Table rows: balanced vs libsamplerate MEDIUM: mono 20.3 vs 5.2, stereo 14.6 vs 4.8, 8-ch 3.0 vs 1.9; transparent vs libsamplerate BEST: stereo 9.6 vs 1.6. Latency is 24 vs 46 frames (MEDIUM) and 40 vs 143 frames (BEST). The tiers are paired by vendor-stated stopband depth only. On the same page SampleRateTap is SLOWER than soxr HQ (114.3 mono, 52.9 stereo, 12.9 8-ch) and r8brain-free-src 120 dB (35.4 mono, 16.5 stereo, 4.1 8-ch). In embedded steady-state instruction counts (QEMU, stereo, 32-frame blocks), libsamplerate MEDIUM executes 2.7x (Cortex-M55), 3.2x (Cortex-M33) and 3.3x (Hexagon) more instructions per output frame than SampleRateTap balanced float, and BEST executes 7.8-9.8x more. |
| **Workload** | A fixed, known near-unity ratio (48000 to 48009.6 Hz, 1 + 200 ppm) applied to a 997 Hz float sine streamed in 128-frame blocks, for mono, stereo and 8-channel streams, measured in million output frames per second. SampleRateTap runs only its fractional_resampler datapath with a constant rate deviation; the servo is quiescent and clock recovery is not timed. libsamplerate gets the ratio through src_process. Algorithmic latency is also reported. The embedded rows count QEMU executed instructions per stereo output frame (32-frame blocks; 2 s and 4 s runs separate steady-state from construction cost). |
| **Metric** | throughput |
| **Hardware** | Host: shared Xeon @ 2.10 GHz (exact model not stated), run 2026-09-25. Embedded: QEMU TCG instruction counting on Cortex-M55 (mps3-an547), Cortex-M33 (mps2-an505) and Hexagon (qemu-hexagon 8.2.2) via the manually triggered compare.yml workflow. |
| **Compiler and flags** | GCC 13.3 -O3 (CMake Release; the bench target adds only warning flags, no -march). libsamplerate 0.2.2 and soxr 0.1.3 are the Ubuntu 24.04 distro packages, so their build flags are the distro's. r8brain-free-src is at pinned commit 7.5 with Ooura FFT. Embedded counts: arm-none-eabi-gcc 13.2.1 and hexagon-clang 19.1.5 at -O3 (CMake Release). |
| **Adoption** | 5 stars |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/tap/SampleRateTap) · [benchmark](https://github.com/tap/SampleRateTap/blob/main/async/docs/COMPARISON.md) |

## Verdict

The author's Google Benchmark harness (bench_compare.cpp; GCC 13.3 -O3 for SampleRateTap, Ubuntu 24.04 distro builds of libsamplerate 0.2.2 and soxr 0.1.3, on an unnamed shared Xeon @ 2.10 GHz) times only SampleRateTap's fractional_resampler at a fixed known ratio of 1 + 200 ppm in 128-frame blocks: 14.6 vs 4.8 M stereo frames/s against libsamplerate MEDIUM (3.04x, derived from page data), 20.3 vs 5.2 mono, 3.0 vs 1.9 at 8 channels, and 9.6 vs 1.6 stereo against BEST. Deterministic QEMU instruction counts on Cortex-M55, Cortex-M33 and Hexagon (arm-none-eabi-gcc 13.2.1, hexagon-clang 19.1.5, -O3) show libsamplerate MEDIUM executing 2.7-3.3x the steady-state instructions per stereo frame; the speedup is real for the timed code but partly comes from a shorter filter with a narrower passband, and neither the servo nor the FIFO is timed.

## Use it when

- Bridging two independently clocked devices at the same nominal rate (USB or network audio into a local DAC, AVB, ALSA device pairs) where you also need the clock recovery that libsamplerate, soxr and r8brain leave to the caller.
- Live monitoring or duplex paths with a 1-2 ms latency budget: 24-frame (0.5 ms) filter group delay for balanced, about 1.5 ms end to end with the default 48-frame FIFO setpoint.
- FPU-less or FP64-less embedded targets (Cortex-M33/RP2350 class, Hexagon, HiFi-style DSPs) via the Q15/Q31 datapaths, where the author's QEMU counts put the Q15 steady state at 879 (M33) and 457 (Hexagon) instructions per stereo frame.
- Multichannel streams that must stay phase-coherent: every channel of one instance is resampled at the same fractional position each frame.
- Fixed near-unity ratios where you would otherwise run libsamplerate MEDIUM/BEST block by block and can accept a 20 kHz passband instead of libsamplerate's wider one.

## Skip it when

- General sample-rate conversion (44.1 to 48 kHz, 2x, arbitrary ratios): the async engine only handles small deviations around a common nominal rate; use soxr, r8brain or libsamplerate (or this repo's separate bridge/rational engines).
- Maximum host throughput or offline/batch work: on the author's own x86 table soxr HQ (52.9 M stereo frames/s) and r8brain 120 dB (16.5) beat SampleRateTap balanced (14.6) when latency does not matter.
- When you need libsamplerate-equivalent filtering: balanced is 48 taps with a 20 kHz passband and a 28 kHz stopband edge above the 24 kHz Nyquist, so 20-24 kHz content can alias into 20-24 kHz, while libsamplerate MEDIUM/BEST use roughly 2x and 3.5x the taps with wider passbands; at the 24-bit interface it measures -133.9 dB THD+N against about -143.5 dB for the oracle-fed libraries.
- Devices that construct converters at boot on FP64-less cores: filter design runs in double at construction and costs about 870-884 M QEMU instructions on Cortex-M33 (seconds on a 150 MHz part), against 20.9 M for libsamplerate MEDIUM.
- Projects that need a stable, packaged dependency: pre-1.0 (v0.5.0 family version), API may still change, no install/package rules, 5 stars, single main author.

## How it is fast

At near-unity the conversion degenerates into a creeping fractional delay, so each output frame needs only one short polyphase FIR: a Kaiser-windowed sinc prototype split into L phase rows of T taps (balanced: 256 x 48), with coefficients linearly interpolated between the two rows adjacent to the fractional position. The position is an unsigned Q0.64 accumulator that adds only the rate deviation per sample, so whole-sample slips are detected by integer wraparound and the per-sample path has no double arithmetic. For multichannel streams the blended coefficient row is computed once per frame and shared by all channels, and from 4 channels up on hosts the history is stored frame-major so the dot product vectorizes across channels (the float path keeps strict per-channel double accumulation, so mono and stereo float dots are scalar by design).

## Compared with alternatives

Pick it over libsoxr and r8brain-free-src when you need drift correction with clock recovery inside a 1-2 ms budget or a fixed-point embedded path; those two are faster on x86 but carry 8.8-37 ms of latency in the same table and have no servo. Pick zita-resampler with zita-ajbridge instead if you are on Linux/JACK and GPL is acceptable, and LibFResample or r8brain for genuine rate conversion.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | DspTap (tap::dsp, MIT, header-only C++20, standard library only; pulled as a git submodule, so clone with --recurse-submodules). GoogleTest for tests; Google Benchmark, libsamplerate, soxr and r8brain-free-src only for the optional comparison benchmarks. |
| **Minimum toolchain** | C++20, CMake 3.24+, GCC 11+ / Clang 14+ / MSVC 19.30+ |
| **Platforms** | any; CI covers Linux (GCC, Clang, ASan/UBSan, TSan), macOS, Windows MSVC, arm64, and Cortex-M33, Cortex-M55 and Hexagon under QEMU. Tensilica HiFi4/5 only as a commented self-hosted CI template. |
| **Thread safety** | Single producer and single consumer: one thread calls push() at the input clock and one calls pull() at the output clock; both are noexcept, lock-free and allocation-free; status() is safe from any thread. The constructor allocates, designs the filter and may throw. |
| **Drop-in for the baseline** | partial — not a src_process replacement: different push/pull interface with built-in clock recovery, and only near-unity ratios (default +-1000 ppm). The lower-level fractional_resampler can be driven at a fixed known ratio as the benchmark does, but it is an internal-style API with priming and reset preconditions. |

## Gotchas

- The filter presets' band edges and servo bandwidths are absolute Hz for about 48 kHz; at other rates construct through config::for_sample_rate() or quality drops silently (the README measures about 32 dB lost at 16 kHz with unscaled defaults).
- The FIFO setpoint must exceed the pull block size; the converter raises it automatically and latency follows, and callbacks above about 340 frames also need fifo_frames set explicitly. With coarse blocks (32 frames and up) the servo stays in its Track stage and the README documents cent-scale low-rate FM (about 62 dB wideband at 32-frame blocks, 54 dB at 5 ms blocks).
- Q15 is format-limited to about 77 dB SNR; use float or Q31 when quality matters, Q15 when cycles do.
- polyphase_filter.h exposes a blend_row(bank, row, mu) helper that calls bank.numPhases(), which polyphase_filter_bank does not have (its accessor is num_phases()); it compiles only because the template is never instantiated, so calling it fails to build. The shipped datapath uses blend_row_phase and is unaffected.

## Known shortcomings

- First-party shootout (async/bench/compare/bench_compare.cpp, GCC 13.3 -O3, 'shared Xeon @ 2.10 GHz' with no CPU model): tiers were matched on stop-band dB only, not equal work (Balanced: 48 taps with a 20-28 kHz transition whose edge sits above the 24 kHz Nyquist; libsamplerate MEDIUM: 120.61 dB, about 91 taps, 90% bandwidth; Transparent 80 taps vs BEST 154.67 dB, about 286 taps; tap counts derived from source data), and no THD+N is given for libsamplerate MEDIUM (Balanced -133.9 dB vs sinc_best -143.5 dB). The timed path is the fixed-ratio datapath with the servo quiescent, so clock recovery is not timed; the engine handles near-unity ratios only (+/-1000 ppm) against libsamplerate's general 1/256 to 256, a different problem. Slower than libsoxr HQ and r8brain on x86; embedded rows are QEMU instruction counts, not time.
- bench_compare.cpp times only the fractional_resampler (servo and FIFO untimed); the mono and stereo float dot products are scalar double, so the speedup comes mostly from 48 taps against about 91 (the filter-pairing caveat stands); flags are not matched (SampleRateTap at -O3 against distro builds of libsamplerate and soxr). The README's full-pipeline table (2026-06-12, Xeon 2.80 GHz) gives 107.8 ns per stereo frame, slower than the datapath-only 14.6 M frames/s. Latent API bug: polyphase_filter.h blend_row() calls bank.numPhases(), which does not exist, and compiles only because it is never instantiated.

## Caveats and trade-offs

First-party: the harness and doc are by the project's author. On x86 host throughput, SampleRateTap beats only libsamplerate; soxr HQ and r8brain-free-src are faster (the author says so openly) but carry 8-33x more latency. The host CPU model is not stated (shared Xeon), and no raw result file is committed; the numbers exist only in COMPARISON.md. The libsamplerate latency rows date from 2026-06-12. The tiers are matched on stopband depth only, so the engines do not do equal filtering work. SampleRateTap balanced is 48 taps with a 20 kHz passband and a 28 kHz stopband edge, above the 24 kHz Nyquist (async/include/tap/sr/async/polyphase_filter.h). libsamplerate MEDIUM is 120.61 dB with a 90% -3 dB bandwidth and about 91 taps per output at this ratio (half length 22437, increment 491 in src/mid_qual_coeffs.h; tap count derived from source data). At the \~140 dB tier, SampleRateTap transparent is 80 taps (20-26 kHz transition, 140 dB), while libsamplerate BEST's table is 154.67 dB at about 286 taps (derived from source data). Part of the speedup therefore comes from a shorter filter with a wider transition band, which lets 20-24 kHz content alias above 20 kHz. No THD+N was measured for libsamplerate MEDIUM. The THD+N table pairs SampleRateTap balanced (-133.9 dB at 24-bit I/O, servo recovering the clock) with libsamplerate sinc_best (-143.5 dB, fed the exact ratio), about 10 dB better. The products solve different problems: the async engine is an ASRC limited to near-unity ratios (default +/-1000 ppm), while libsamplerate is a general fixed-ratio converter (1/256 to 256). The benchmark times only the fixed-ratio datapath, so the clock recovery the libraries lack is not timed, and SampleRateTap cannot replace libsamplerate outside drift correction. On embedded targets, construction costs far more than libsamplerate (870 M vs 20.9 M instructions on Cortex-M33 for balanced vs MEDIUM). The benchmarks are behind TAP_SR_BUILD_COMPARE_BENCH (requires TAP_SR_BUILD_BENCHMARKS), off by default. The repo is young (5 stars, 225 commits, measurements back to June 2026, no issues filed); no correctness bug behind the numbers was found.

Specialised: near-unity asynchronous ratio (+-1000 ppm default) for clock-domain bridging, not a general-ratio resampler. Header-only C++20. Fixed-point Q15/Q31 paths for FPU-less DSPs. Very low latency (0.5 ms filter, 1.5 ms default).

## Maintenance

Active (225 commits, last activity 2026-10-03, v0.5.0 family version, 1 open PR, no issues filed) and MIT-licensed, but young, pre-1.0 and consumable only via add_subdirectory/FetchContent; the benchmarks are first-party.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** COMPARISON.md and its public harness (async/bench/compare/bench_compare.cpp, Google Benchmark, enabled with -DTAP_SR_BUILD_COMPARE_BENCH=ON) state GCC 13.3 -O3 (CMake Release, no -march), but the host CPU is only a 'shared Xeon @ 2.10 GHz' with no model, so the timed numbers miss tier A; they are the project author's own measurements (first-party), hence C. The embedded rows are reproducible QEMU instruction counts (.github/workflows/compare.yml, async/bench/icount/cmp_main.cpp, pinned arm-none-eabi-gcc 13.2.1 and hexagon-clang 19.1.5 at -O3), but they count instructions rather than time, and the same author ran them.
- **Verifier notes:** The page numbers match the record. The doc's ratios agree with its tables to within rounding of the displayed values: 14.6/4.8 = 3.04 and 3.0/1.9 = 1.58 (derived from page data), against the stated 3.1x and 1.5x. The main shortcoming is the quality pairing: the tiers are matched by stopband dB, while libsamplerate's filters keep the transition band below Nyquist with roughly 2x (MEDIUM) and 3.5x (BEST) the taps. The ASRC also solves only the near-unity drift problem, not general rate conversion.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/tap/SampleRateTap/blob/main/async/docs/COMPARISON.md>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/docs/COMPARISON.md>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/bench/compare/bench_compare.cpp>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/bench/compare/CMakeLists.txt>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/bench/icount/cmp_main.cpp>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/.github/workflows/compare.yml>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/include/tap/sr/async/polyphase_filter.h>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/README.md>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/CMakeLists.txt>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/README.md>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/LICENSE>
  - <https://github.com/tap/SampleRateTap>
  - <https://github.com/tap/SampleRateTap/commits/main>
  - <https://github.com/tap/SampleRateTap/tree/main/async/bench/compare>
  - <https://github.com/tap/SampleRateTap/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/libsndfile/libsamplerate/master/docs/api_misc.md>
  - <https://raw.githubusercontent.com/libsndfile/libsamplerate/master/src/mid_qual_coeffs.h>
  - <https://raw.githubusercontent.com/libsndfile/libsamplerate/master/src/high_qual_coeffs.h>
- **Sources the enricher read:**
  - <https://github.com/tap/SampleRateTap>
  - <https://github.com/tap/SampleRateTap/pulls?q=is%3Apr>
  - <https://github.com/tap/SampleRateTap/tree/main/async/include/tap/sr/async>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/README.md>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/README.md>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/docs/COMPARISON.md>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/docs/PERFORMANCE.md>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/bench/compare/bench_compare.cpp>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/bench/compare/CMakeLists.txt>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/bench/icount/cmp_main.cpp>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/.github/workflows/compare.yml>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/include/tap/sr/async/polyphase_filter.h>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/include/tap/sr/async/converter.h>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/include/tap/sr/async/sample_traits.h>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/include/tap/sr/async/async.h>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/include/tap/sr/async/spsc_ring.h>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/CMakeLists.txt>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/tap/dsptap/HEAD/include/tap/dsp/fir_kernels.h>
  - <https://raw.githubusercontent.com/tap/dsptap/HEAD/include/tap/dsp/sample_traits.h>
  - <https://raw.githubusercontent.com/tap/dsptap/HEAD/README.md>
  - <https://raw.githubusercontent.com/tap/dsptap/HEAD/LICENSE>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/tap/sampleratetap`) · [data/wave10/enrich/raw/github_com_tap_sampleratetap.json](../../../data/wave10/enrich/raw/github_com_tap_sampleratetap.json) (enrichment confidence 0.75)

</details>
