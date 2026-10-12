# opuspp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Header-only C++23 port of the libopus 1.6.1 decoder for one CELT stream type, bit-exact and 1.27-1.48x faster.

| | |
|---|---|
| **Beats** | libopus 1.6.1 decoder (opus_decode_float), built with identical compiler and flags |
| **Claimed result** | Like for like (same compiler and flags) opuspp is 1.27x to 1.48x faster than libopus at 320 kb/s (GCC Size 1.27x, GCC Balanced 1.48x, GCC Fast 1.43x, Clang Size 1.42x, Clang Balanced 1.46x, Clang Fast 1.42x); 1.09x to 1.50x across other bit rates, packet loss and encoder complexities. Five of six opuspp builds beat the fastest libopus build (GCC Fast) by 1.33x to 1.43x; GCC Size opuspp is slower than that build (0.88x). |
| **Workload** | Decoding a 60 s mixed-audio stream (tones, noise, transients, orchestral music) encoded by libopus as 48 kHz fullband stereo, 10 ms CELT frames at 320 kb/s and encoder complexity 4; best of 7 passes pinned to one core, packet buffer flushed from cache before each pass. Other streams: 128 and 510 kb/s, 10% packet loss, complexity 0 and 2. |
| **Metric** | throughput |
| **Hardware** | One core of an AMD Ryzen 5 9600X |
| **Compiler and flags** | GCC 16.2 and Clang 22.1; Size: -Os, Balanced: -O2, Fast: -O3 -march=native -ffast-math -falign-loops=32 (libopus with OPUS_FLOAT_APPROX=ON and OPUS_FAST_MATH=ON, opuspp with OPUSPP_FLOAT_APPROX); all with -DNDEBUG -ffunction-sections -fdata-sections and -Wl,--gc-sections |
| **Adoption** | 0 stars (repository created 2026-10-02, one commit) |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/mhaugstrup/opuspp-ai-port) · [benchmark](https://raw.githubusercontent.com/mhaugstrup/opuspp-ai-port/HEAD/docs/performance.md) |

## Verdict

tests/bench.cpp decodes the same libopus-encoded packets (60 s of tones, noise, transients and orchestral music; 320 kb/s, complexity 4, 10 ms fullband stereo) with opus_decode_float and with opuspp, best of 7 passes on one pinned Ryzen 5 9600X core with the packet arena clflushed before each pass; libopus 1.6.1 is built statically with the same GCC 16.2 or Clang 22.1 flags per profile (-Os, -O2, or -O3 -march=native -ffast-math with FLOAT_APPROX in both) and keeps its run-time AVX2 dispatch. opuspp is 1.27-1.48x faster like for like and 1.09-1.50x across 128/510 kb/s, 10% loss and complexities 0 and 2; libopus is not built with -flto, so part of the gain is the header-only inlining the project argues for, and only the rendered tables (not results.json) are committed.

## Use it when

- You control both ends of a low-latency link (wireless or LAN audio streaming) and can pin the encoder to RESTRICTED_CELT, fullband, 10 ms frames, complexity 0-4 and OPUS_SET_PREDICTION_DISABLED(1).
- High-bitrate stereo music streams (128-510 kb/s) where decode CPU per stream matters; the largest measured gain is at 320 kb/s.
- Freestanding or embedded C++ builds that need no heap, no libm, no exceptions or RTTI, and a fixed 18.1 KB decoder object the caller places.
- Systems that must stay bit-identical to a reference libopus build (SSE baseline, strict IEEE) for conformance testing via final_range().

## Skip it when

- General Opus playback: SILK, hybrid, 20/40/60 ms frames, narrower bandwidths, multi-frame packets and packets that enable the pitch post-filter are rejected, so VoIP/WebRTC or file playback needs libopus.
- Streams whose encoder you do not control: a sender switching to complexity 5+ or prediction enabled produces packets opuspp refuses, so keep a libopus fallback.
- Needs beyond the CELT PLC: no FEC, DRED, OSCE or deep PLC, no multistream, no int16 output or other sample rates.
- Non-x86 targets where speed matters: everything was built and measured on x86-64 Linux (one Ryzen 5 9600X core); NEON and RVV come only through the generic vector-extension backend and are unmeasured.
- Production code that needs a track record: one commit (2026-10-02), 0 stars, no outside users, written by Claude Code; fuzzed and sanitizer-checked by the author but not externally reviewed.

## How it is fast

Specialisation alone was not enough (0.68x of libopus with GCC -O2 per the project's notes); the speed comes from an explicit portable SIMD layer, simd&lt;T,N&gt; on GCC/Clang vector extensions, that ports libopus's SSE xcorr/inner-product kernels lane for lane and vectorises code libopus runs scalar (radix-3/4/5 FFT butterflies with compile-time twiddles, IMDCT rotation and TDAC windowing, noise fill with a 4-lane LCG using jump-ahead constants, Hadamard/Haar steps, de-emphasis loads). Every buffer and table is alignas(64) and sliding windows are built from aligned blocks with compile-time shuffles. Serial integer code was rewritten exactly: a 6 KB constexpr bits2pulses lookup table instead of a binary search, a hardware-sqrt-plus-correction isqrt in theta decoding, and a branch-free counting search in cwrsi (PVQ index decoding). Being header-only, all of it inlines into the caller, whereas libopus is a separately compiled library.

## Compared with alternatives

Pick opuspp over libopus or full-codec ports such as opus-pure, ruopus or ropus only when the stream is pinned to fullband 10 ms CELT with prediction off and you want header-only freestanding C++ with libopus-bit-exact output; the full ports and libopus handle SILK, hybrid and every frame size, and gopus/ruopus/ropus are the choices for Go or Rust.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the library (only &lt;cstddef&gt;, &lt;cstdint&gt;, &lt;bit&gt;); libopus 1.6.1 sources, CMake 3.21+, ffmpeg and a music clip only for tests and benchmarks |
| **Minimum toolchain** | C++23; GCC 16.2 and Clang 22.1 tested; other compilers fall back to an untested plain-array SIMD backend |
| **Platforms** | any C++23 target in principle (GCC/Clang vector extensions lower to SSE, AVX, NEON, RVV); verified and measured only on x86-64 Linux (baseline, v2, v3, v4 builds) |
| **Thread safety** | Not documented; all mutable state is inside each Decoder object and the tables are constexpr, so one decoder per thread is safe (inference from the code). |
| **Drop-in for the baseline** | partial: replaces opus_decode_float only for CELT-only fullband 10 ms single-frame packets from a prediction-disabled encoder, through a different C++ API |

## Gotchas

- Bit-exactness needs strict IEEE: with FMA enabled (e.g. -march=native) normal frames differ at about 135 dB SNR unless you add -ffp-contract=off, and -ffast-math is only accepted together with -DOPUSPP_FLOAT_APPROX (#error otherwise).
- A stock x86 libopus picks an AVX2+FMA pitch kernel at run time, so its concealment differs from opuspp (about 86 dB SNR at 10% loss); the project's bit-exact reference is libopus built with OPUS_X86_MAY_HAVE_AVX2=OFF.
- Concealment peaks at 9.6-12.1 KB of stack (3.8-6.5 KB for normal decoding), which matters for small embedded thread stacks.
- GCC -Os builds gain least: 1.27x like for like and 0.88x of a GCC -O3 -march=native libopus, so build it at -O2 or higher with GCC.

## Known shortcomings

- Tier A on its own bench.cpp and profile_report.py (GCC 16.2 and Clang 22.1, same flags, Ryzen 5 9600X) against libopus 1.6.1 with the same packets, bitrate, complexity and frame size. Output is bit-exact only in the Size and Balanced profiles; the Fast profile is about 137 dB SNR against the reference, not bit-exact. The raw results.json is not committed.
- The static libopus baseline is built without -flto while opuspp inlines header-only by design; only an x86-64 Ryzen 5 9600X is measured (NEON unmeasured); results.json is not committed; the bench sinks one sample per call (bit-exactness is checked separately across 47 configurations and 300k fuzz cases); a GCC -Os build runs at 0.88x of the fastest libopus.

## Caveats and trade-offs

Code was written by Claude Code (the README says so); the repository has one commit (2026-10-02), 0 stars and no users yet. Decoder only, and only for one stream configuration: OPUS_APPLICATION_RESTRICTED_CELT, fullband, 10 ms frames, 48 kHz stereo float output, prediction disabled, encoder complexity 0-4, no SILK/hybrid/FEC/pitch post-filter; other packets are rejected. The comparison is like for like: both decoders decode the identical packet buffer, built with identical flags per profile (libopus with its default CMake options apart from hardening off, so its intrinsics/run-time CPU dispatch stay enabled), best of 7 passes with the packet buffer clflushed before each pass. Output is bit-identical to libopus in the Size (-Os) and Balanced (-O2) builds (47 encoder configurations and a 300k-packet fuzz test per docs/verification.md); the Fast builds (-ffast-math, FLOAT_APPROX) are not bit-exact in either decoder (about 137 dB SNR on normal frames and 62 dB in concealment against libopus FLOAT_APPROX), so the fastest-build comparison is perceptually, not bit-exactly, equivalent. Only rendered tables are committed; the raw results.json that profile_report.py writes is not in the repository, and the numbers were not re-run. libopus is linked statically; docs/performance-shared-library.md reports 1.24x to 1.48x against a shared libopus. The GCC -Os opuspp build is 0.88x of the fastest libopus build (GCC Fast).

Header-only freestanding C++23 decoder specialised to one stream type: CELT-only, fullband, 48 kHz stereo float output, 10 ms frames, prediction disabled, no pitch post-filter, no SILK, hybrid, FEC or DNN extensions. Bit-identical to libopus in strict-IEEE builds (47 encoder configurations, 300k-packet fuzz); the Fast profile is not bit-exact in either decoder. Smaller code (71-198 KB vs 98-236 KB static libopus) and decoder state (18.1 KB vs 26.6 KB), no heap or libm.

## Maintenance

Brand-new single-commit AI-written experiment (active, 0 stars) under BSD-3-Clause as a libopus derivative; the code, tests and benchmark are complete and reproducible, but nobody else is using it yet.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** docs/performance.md compares opuspp against the reference libopus 1.6.1 decoder (opus_decode_float) on the same packets (same 320 kb/s bitrate, encoder complexity, 10 ms frame size, fullband stereo, 48 kHz float output); the harness opuspp/tests/bench.cpp and the build/run driver opuspp/tools/profile_report.py are public, and the page states compilers (GCC 16.2, Clang 22.1), identical flags per profile for both decoders, and the CPU (Ryzen 5 9600X, one pinned core). Every number in claimed_speedup matches the tables in docs/performance.md and docs/performance-additional.md.
- **Verifier notes:** Checked the orchestrator's points: harness, compilers, flags and CPU are all public; comparison is against reference libopus 1.6.1 at the same bitrate, complexity and frame size on the same packets; bit-exact only in the strict-IEEE (Size, Balanced) profiles, not in Fast. Metadata (BSD-3-Clause derivative of libopus, 0 stars, 1 commit on 2026-10-02, not a fork) confirmed on the GitHub page.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/mhaugstrup/opuspp-ai-port/HEAD/docs/performance.md>
  - <https://raw.githubusercontent.com/mhaugstrup/opuspp-ai-port/HEAD/README.md>
  - <https://raw.githubusercontent.com/mhaugstrup/opuspp-ai-port/HEAD/opuspp/tests/bench.cpp>
  - <https://raw.githubusercontent.com/mhaugstrup/opuspp-ai-port/HEAD/opuspp/tools/profile_report.py>
  - <https://raw.githubusercontent.com/mhaugstrup/opuspp-ai-port/HEAD/docs/performance-additional.md>
  - <https://raw.githubusercontent.com/mhaugstrup/opuspp-ai-port/HEAD/docs/verification.md>
  - <https://raw.githubusercontent.com/mhaugstrup/opuspp-ai-port/HEAD/docs/performance-shared-library.md>
  - <https://raw.githubusercontent.com/mhaugstrup/opuspp-ai-port/HEAD/docs/performance-build-profiles.md>
  - <https://raw.githubusercontent.com/mhaugstrup/opuspp-ai-port/HEAD/opuspp/README.md>
  - <https://raw.githubusercontent.com/mhaugstrup/opuspp-ai-port/HEAD/LICENSE>
  - <https://github.com/mhaugstrup/opuspp-ai-port>
  - <https://github.com/mhaugstrup/opuspp-ai-port/commits>
- **Sources the enricher read:**
  - <https://github.com/mhaugstrup/opuspp-ai-port>
  - <https://raw.githubusercontent.com/mhaugstrup/opuspp-ai-port/HEAD/README.md>
  - <https://raw.githubusercontent.com/mhaugstrup/opuspp-ai-port/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/mhaugstrup/opuspp-ai-port/HEAD/docs/performance.md>
  - <https://raw.githubusercontent.com/mhaugstrup/opuspp-ai-port/HEAD/docs/performance-additional.md>
  - <https://raw.githubusercontent.com/mhaugstrup/opuspp-ai-port/HEAD/docs/performance-shared-library.md>
  - <https://raw.githubusercontent.com/mhaugstrup/opuspp-ai-port/HEAD/docs/performance-build-profiles.md>
  - <https://raw.githubusercontent.com/mhaugstrup/opuspp-ai-port/HEAD/docs/verification.md>
  - <https://raw.githubusercontent.com/mhaugstrup/opuspp-ai-port/HEAD/docs/how-claude-made-it.md>
  - <https://raw.githubusercontent.com/mhaugstrup/opuspp-ai-port/HEAD/docs/code-size.md>
  - <https://raw.githubusercontent.com/mhaugstrup/opuspp-ai-port/HEAD/docs/memory.md>
  - <https://raw.githubusercontent.com/mhaugstrup/opuspp-ai-port/HEAD/opuspp/README.md>
  - <https://raw.githubusercontent.com/mhaugstrup/opuspp-ai-port/HEAD/opuspp/CMakeLists.txt>
  - <https://raw.githubusercontent.com/mhaugstrup/opuspp-ai-port/HEAD/opuspp/include/opuspp/opuspp.hpp>
  - <https://raw.githubusercontent.com/mhaugstrup/opuspp-ai-port/HEAD/opuspp/tests/bench.cpp>
  - <https://raw.githubusercontent.com/mhaugstrup/opuspp-ai-port/HEAD/opuspp/tests/bench_signal.hpp>
  - <https://raw.githubusercontent.com/mhaugstrup/opuspp-ai-port/HEAD/opuspp/tests/bench_stream.hpp>
  - <https://raw.githubusercontent.com/mhaugstrup/opuspp-ai-port/HEAD/opuspp/tests/data/README.md>
  - <https://raw.githubusercontent.com/mhaugstrup/opuspp-ai-port/HEAD/opuspp/tools/profile_report.py>
  - <https://raw.githubusercontent.com/mhaugstrup/opuspp-ai-port/HEAD/opuspp/tools/fetch_deps.sh>
  - <https://raw.githubusercontent.com/mhaugstrup/opuspp-ai-port/HEAD/opuspp/tools/verify.sh>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/mhaugstrup/opuspp-ai-port`) · [data/wave10/enrich/raw/github_com_mhaugstrup_opuspp_ai_port.json](../../../data/wave10/enrich/raw/github_com_mhaugstrup_opuspp_ai_port.json) (enrichment confidence 0.85)

</details>
