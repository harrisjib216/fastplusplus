# nam-zig

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Zig` · `MIT` · 🟢 active

> Zig port of Neural Amp Modeler (play, train, export .nam) on Fucina; no timing against NeuralAmpModelerCore C++.

| | |
|---|---|
| **Beats** | NeuralAmpModelerCore (C++) at -O3: no timing comparison found in the README or repo |
| **Claimed result** | None against NeuralAmpModelerCore. README gives absolute numbers only: standard WaveNet (13,802 weights) 72 us per 64-frame block at 48 kHz on one core, '18x the 1333 us realtime budget'; 480 us per 512-frame block (22x); a 23-layer 8-channel Tone3000 profile (12,146 weights) 57 us per 64-frame block. Parity with upstream render: max \|diff\| 2.3e-6, RMS 6.5e-8. |
| **Workload** | Real-time inference of Neural Amp Modeler WaveNet profiles at 48 kHz on one core; the README reports per-block cost against the real-time budget and checks output parity with the upstream C++ renderer. |
| **Metric** | latency |
| **Hardware** | Apple M1 Max (single core), 2026-09-09 snapshot |
| **Compiler and flags** | ReleaseFast (Zig); upstream build in the test plan uses cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo -DNAM_ENABLE_A2_FAST=OFF for the parity render only. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Adoption** | 0 stars; 15 commits since 2026-09-09 |
| **Last commit** | 2026-09-19 |
| **Links** | [repository](https://github.com/matteo-grella/nam-zig) · [benchmark](https://github.com/matteo-grella/nam-zig) |

## Verdict

Only absolute costs are published: standard WaveNet (13,802 weights) 72 us per 64-frame block and 480 us per 512-frame block at 48 kHz, and a 23-layer 8-channel Tone3000 profile at 57 us per 64-frame block, ReleaseFast on an Apple M1 Max (2026-09-09 snapshot); no NeuralAmpModelerCore timing was taken, so there is no ratio, only output parity with upstream render (max |diff| 2.3e-6).

## Use it when

- Playing .nam profiles standalone on macOS, Linux or Windows without a DAW or plugin host, with cabinet IRs and multi-stage chains
- Training NAM profiles on a CPU without a PyTorch install, then using the exported .nam in any upstream-compatible player
- Small standard-size WaveNet profiles at 64-frame blocks, where the README reports 72 us per block on one M1 Max core (about 5% of the 1333 us budget)
- Zig projects that want a NAM inference engine with output matching upstream tools/render (max |diff| 2.3e-6, RMS 6.5e-8 on the standard example)

## Skip it when

- When you need evidence that it beats NeuralAmpModelerCore: no upstream timing is reported anywhere, only absolute per-block costs
- Inside a DAW: the README describes a standalone app and documents no VST3, AU or CLAP plugin
- Slimmable WaveNet submodels or non-WaveNet condition_dsp engines in the trainable path: they fail with a named error
- Older x86 CPUs with the prebuilt binaries: x86-64 releases are built with -Dcpu=x86_64_v3 (AVX2 required); the Linux aarch64 release is built for the baseline CPU and so lacks the tuned kernels
- Production rigs that need a track record: created 2026-09-09, 0 stars, one author, live audio on Linux and Windows exercised by users rather than CI

## How it is fast

Every WaveNet causal convolution is a Fucina groupedCausalConv1dStreaming over its own ring-buffer state, which in inference runs as one fused kernel call (conv, bias, state carry); the per-layer accumulations are done in place and the block path is allocation-free once Fucina's buffer pool is warm. Fucina selects NEON/dotprod or AVX2/AVX-VNNI kernels at compile time for the host CPU (as if -march=native), and macOS builds link Accelerate by default; whether the conv kernels actually call BLAS is not documented. Exact tanh is the default, with a fast-tanh option.

## Compared with alternatives

No audio-model siblings are catalogued in numerics-and-arrays; next to the Zig and Mojo LLM-inference entries (llama2.zig, llama2.mojo) it is the pick only for NAM guitar-amp profiles, and its Fucina engine is the same library whose llama.cpp comparison is catalogued separately.

## Integration

| | |
|---|---|
| **Form** | application binary (CLI plus window) built with zig build; no library API documented |
| **Dependencies** | Fucina v0.5.1 (fetched by the Zig package manager, pinned by tag and hash), vendored miniaudio; optional system BLAS (Accelerate on macOS by default, -Dblas=none to drop it); GTK 3 and WebKitGTK on Linux for the window, else the browser |
| **Minimum toolchain** | Zig 0.16.0 |
| **Platforms** | macOS arm64 and x86_64, Linux x86_64 and aarch64, Windows x86_64; developed and tested on Apple Silicon; prebuilt x86-64 binaries need x86-64-v3 (AVX2, FMA) |
| **Thread safety** | README says the audio callback is allocation-free and lock-free with chains preloaded and prewarmed; nothing documented for use as a library |
| **Drop-in for the baseline** | partial — reads and writes the same .nam files and matches upstream render output, but it is a separate program with no C++ API, so it cannot replace NeuralAmpModelerCore inside a plugin |

## Gotchas

- The bench command reports the mean per-block time over about 5 s of repeatedly processing one fixed 64-sample sine block after 64 warm-up blocks (src/main.zig); it gives no worst-case or percentile figure, so the 18x real-time headroom is an average, not a deadline guarantee, and 'bench standard' uses synthetic weights.
- Builds are tuned to the compiling host: a cross-compile without -Dcpu silently loses the fast kernels (Fucina README), and Debug builds are about 20x slower and will not keep up in real time.
- The README says the timing ran on one core, but Fucina has a bounded worker pool and macOS builds link Accelerate; the thread count used by bench is not stated, and no upstream benchmodel run on the same machine is given.
- The parity render builds upstream as RelWithDebInfo with NAM_ENABLE_A2_FAST=OFF; that build is for correctness only and says nothing about upstream speed.

## Known shortcomings

- Absolute per-block costs only (72 us per 64 frames on an M1 Max) with no NeuralAmpModelerCore timing; 0 stars and one month old.
- Enricher: still no NeuralAmpModelerCore timing; the bench is the mean over one repeated 64-sample block with no worst case or percentiles; x86 releases need x86-64-v3 while linux-aarch64 is built for the baseline CPU; the 'one core' claim is unverified (Fucina worker pool, Accelerate linked).

## Caveats and trade-offs

The speed claim from the Fucina enricher is unverified: the README names upstream's benchmodel tool as the performance oracle but reports no upstream timing, so there is no baseline number and no ratio. Repo was created 2026-09-09 (about a month old) with no stars or releases. Recorded at D per the seed-record instruction (not notable by stars).

A Zig port with trainer, live audio app, tuner and GGUF container, built on the author's Fucina tensor library; imports and exports upstream .nam files; WaveNet, LSTM, ConvNet and Linear architectures; slimmable WaveNet submodels are not supported in the trainable path.

## Maintenance

Active (v0.4.0 on 2026-09-19, 15 commits since 2026-09-09) and MIT-licensed with prebuilt releases, but a one-month-old single-author project with no baseline measurement, so it stays a usable NAM runtime rather than a demonstrated speedup over the C++ core.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now D.
- **Tier reason:** The README's Performance bullet gives only absolute per-block costs (72 us per 64-frame block, 480 us per 512-frame block, 57 us for the Tone3000 profile; ReleaseFast, Apple M1 Max) against the real-time budget; it names upstream's benchmodel tool as the performance oracle but reports no NeuralAmpModelerCore timing, so there is no comparison and the entry stays D.
- **Verifier notes:** All absolute numbers, parity figures (max |diff| 2.3e-6, RMS 6.5e-8) and metadata (0 stars, MIT, 15 commits, first commit 2026-09-09, last 2026-09-19 'release: 0.4.0') match the record. Shortcoming: no baseline measurement at all and not notable (0 stars, one month old); kept at D under the keep-and-document rule rather than rejected. The upstream build in the test plan (RelWithDebInfo) is for the parity render only.
- **Shortcomings recorded by:** verifier batch-111 (wave 14 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/matteo-grella/nam-zig/HEAD/README.md>
  - <https://github.com/matteo-grella/nam-zig>
  - <https://github.com/matteo-grella/nam-zig/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/matteo-grella/nam-zig/HEAD/README.md>
  - <https://github.com/matteo-grella/nam-zig>
  - <https://github.com/matteo-grella/nam-zig/tree/main/src>
  - <https://github.com/matteo-grella/nam-zig/commits>
  - <https://raw.githubusercontent.com/matteo-grella/nam-zig/HEAD/src/main.zig>
  - <https://raw.githubusercontent.com/matteo-grella/nam-zig/HEAD/src/wavenet.zig>
  - <https://raw.githubusercontent.com/matteo-grella/nam-zig/HEAD/src/engine.zig>
  - <https://raw.githubusercontent.com/matteo-grella/nam-zig/HEAD/build.zig>
  - <https://raw.githubusercontent.com/matteo-grella/nam-zig/HEAD/build.zig.zon>
  - <https://github.com/matteo-grella/nam-zig/tree/main/.github/workflows>
  - <https://raw.githubusercontent.com/matteo-grella/nam-zig/HEAD/.github/workflows/release.yml>
  - <https://raw.githubusercontent.com/matteo-grella/nam-zig/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/matteo-grella/fucina/v0.5.1/README.md>
  - <https://raw.githubusercontent.com/matteo-grella/fucina/v0.5.1/src/streamconv.zig>
  - <https://crates.io/api/v1/crates/NeuralAmpModeler-rs>
  - <https://raw.githubusercontent.com/fabiohl/NeuralAmpModeler-rs/HEAD/docs/benchmarks.md>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/matteo-grella/nam-zig`) · [data/wave14/enrich/raw/github_com_matteo_grella_nam_zig.json](../../../data/wave14/enrich/raw/github_com_matteo_grella_nam_zig.json) (enrichment confidence 0.8)

</details>
