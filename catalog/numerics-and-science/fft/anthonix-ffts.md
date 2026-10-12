# FFTS (The Fastest Fourier Transform in the South)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🟡 stale

> BSD-3 C library for single-precision FFTs that JIT-compiles a machine-code plan; beat FFTW on pre-AVX SSE CPUs, loses on AVX.

| | |
|---|---|
| **Beats** | FFTW |
| **Claimed result** | On Core i7-870 (SSE4.2, no AVX) FFTS 1.11x-1.88x faster than FFTW; on i5-3340M (AVX) FFTS wins at N&lt;=32 (1.17-1.81x) and loses at N&gt;=64 (0.64-0.91x) (issue #28 table) |
| **Workload** | Single-precision FFT of various sizes, SSE; user-posted comparison in GitHub issue |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-870 @2.93GHz; i5-3340M @2.70GHz; i5-3470 @3.2GHz |
| **Adoption** | \~560 stars, 215 forks |
| **Last commit** | 2024-05-15 |
| **Links** | [repository](https://github.com/anthonix/ffts) · [benchmark](https://github.com/anthonix/ffts/issues/28) |

## Verdict

A user-posted table in issue #28 (2014) compared FFTS with FFTW on power-of-two complex FFTs from N=4 to 262144. FFTS is single precision; the FFTW version, planner flags and compiler were not stated. On an i7-870 (SSE4.2, no AVX) FFTS was 1.11-1.88x faster at every size; on an i5-3340M (AVX) it won only for N &lt;= 32 (1.17-1.81x) and ran at 0.64-0.91x of FFTW's speed for N &gt;= 64. The issue page showed no comments this session, so the record's second-user report (i5-3470, VS2015, real N=2048, \~50% slower) could not be re-traced.

## Use it when

- Power-of-two single-precision FFTs on SSE-only x86-64 CPUs (Nehalem-class and older): on an i7-870 FFTS was 1.11-1.88x faster than FFTW at every N from 4 to 262144
- Very small transforms (N &lt;= 32): even on the AVX i5-3340M FFTS beat FFTW by 1.17-1.81x
- 32-bit ARMv7 targets (older Android/iOS) that want a BSD-licensed FFT with hand-written NEON or VFP assembly
- Replacing GPL FFTW with a permissively licensed library that has a similar plan/execute shape for 1D/2D/N-D real and complex transforms

## Skip it when

- AVX/AVX2/AVX-512 CPUs at N &gt;= 64: the only SIMD paths are SSE-SSE3 and NEON, and on the i5-3340M FFTW was \~1.1-1.56x faster (FFTS ran at 0.64-0.91x of FFTW's speed, derived from page data)
- Double precision: every kernel is float-only (_32f); only the linkotec fork added 'initial support for double precision' (2018)
- AArch64 (Apple Silicon, arm64 Android, ARM servers): no 64-bit ARM SIMD path, and the JIT falls through to the x86 SSE code generator, so dynamic code has to be disabled; open issues #73 and #75 ask about arm64/NDK builds
- Non-power-of-two lengths: they run Bluestein with a power-of-two FFT of size &gt;= 2N-1 plus three extra buffers, so they cost several power-of-two transforms; PocketFFT or VectorFFT handle them natively
- Projects that need a maintained dependency: the library code last changed in 2017, and issues #81 (segfault in forward 2D real transforms) and #66 (SIGILL in neon_transpose8 on 32-bit ARM) are still open

## How it is fast

Plan creation fixes size and direction, precomputes twiddle lookup tables and input-offset tables, and on x86-64 (SSE) or 32-bit ARM (NEON/VFP) emits specialised machine code into an mmap'd buffer that is then flipped to read+execute. The generated code runs SIMD size-8 leaf transforms over the permuted input, then radix-4/radix-8 butterfly passes. The authors' IEEE TSP 2013 paper (Blake, Witten, Cree) calls this a cache-oblivious algorithm with run-time specialisation, without FFTW's large codelet library or time-consuming machine-specific calibration. A static (no-JIT) build uses the same SSE/NEON kernels through C macros.

## Compared with alternatives

Pick FFTS only for power-of-two single-precision work on SSE-only x86-64 or 32-bit ARM NEON, where it has hand-tuned code and a permissive license. On current hardware muFFT (runtime AVX dispatch), PocketFFT (any length, double precision, ARM) or KFR (beats FFTW on modern CPUs, GPL/commercial) are better and maintained.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none (libm); GNU assembler for the ARM .s files |
| **Minimum toolchain** | C (standard not documented); CMake 2.8.12+ or autotools (./configure --enable-sse --enable-single); GCC, Clang or MSVC |
| **Platforms** | x86-64 with SSE/SSE2/SSE3 (runtime code generation x86-64 only; 32-bit x86 falls back to the static path); 32-bit ARMv7 NEON/VFP; other targets need --disable-dynamic-code and get the scalar static path; no AVX |
| **Thread safety** | Not documented. Real-input and non-power-of-two plans write to a per-plan scratch buffer (p-&gt;buf) during ffts_execute, so give each thread its own plan |
| **Drop-in for the baseline** | false — FFTW-like but separate API (ffts_init_\*/ffts_execute/ffts_free); interleaved float complex layout and -1 forward sign match FFTW, but there is no guru/many interface, no double precision and no wisdom |

## Gotchas

- Input and output buffers must be 16-byte aligned on SSE/NEON builds. ffts_execute only LOGs a warning on misalignment and then runs aligned SIMD code; issue #81 is a segfault from an internally misaligned row pointer in forward 2D real transforms
- The default build generates machine code at plan time and mprotects anonymous memory to read+execute. Where JIT memory is forbidden, build with --disable-dynamic-code (autotools) or DISABLE_DYNAMIC_CODE (CMake)
- On ARM the CMake build probes the host with -march=native and runs test programs to pick NEON hard/soft-float or VFP, so cross-compiles skip this detection
- ffts_chirp_z_init writes into its scratch buffer without checking the aligned malloc result, so an allocation failure on a large non-power-of-two plan dereferences NULL

## Known shortcomings

- Faster only on pre-AVX CPUs, FFTW wins on AVX CPUs (issue #28); another user measured \~50% slower for real N=2048; author points to linkotec and ValveSoftware forks; stale (2024-05-15).
- The record's 'second user (i5-3470, VS2015, real N=2048) \~50% slower' claim is untraceable: issue #28 has no comments. #28 table: on the AVX i5-3340M FFTS wins at N&lt;=32 (1.17-1.81x) and loses at N&gt;=64 (0.64-0.91x).
- Open segfault #81 (forward 2D real, misaligned row pointer); SIGILL #66 on ARM32; float-only, no AVX, no AArch64 SIMD (JIT falls through to x86 SSE codegen on non-ARM32); ffts_execute only logs on misaligned buffers; chirp_z_init skips a malloc NULL check; code frozen since 2017, forks idle since 2019.

## Caveats and trade-offs

Win is only on pre-AVX CPUs and reverses on AVX hardware; a second user measured FFTS \~50% slower than FFTW for real N=2048; author says not touched for many years and points to forks (linkotec/ffts, ValveSoftware/ffts); last commit (2024-05-15) is a README-only change; evidence is user comments. [retier] The earlier 'second user \~50% slower at real N=2048' note is untraceable (issue #28 has no comments); disregard it.

Runtime dynamic code generation (disable with --disable-dynamic-code); SSE/NEON; no AVX path

## Maintenance

Abandoned: the code last changed in June 2017 (a merge of linkotec's Bluestein support), and the only later commit (May 2024) is a README note from the author pointing to the linkotec and ValveSoftware forks. Those forks are themselves idle since March 2019. The library is BSD-3 and small enough to vendor, but treat it as frozen legacy code for SSE/ARMv7 single precision.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** GitHub issue #28 has user-posted FFTS vs FFTW numbers with CPU models but no compiler/flags or bench code for the first comparison; mixed results, so C.
- **Verifier notes:** License is BSD-3-Clause per the COPYRIGHT file. Last commit 2024-05-15 is \~2.4 years ago (stale by rule) but effectively unmaintained per the author; orchestrator may prefer a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `license`, `usability`, `maintenance_status`, `stars_or_usage`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/anthonix/ffts/issues/28>
  - <https://github.com/anthonix/ffts>
  - <https://github.com/anthonix/ffts/commits>
  - <https://raw.githubusercontent.com/anthonix/ffts/HEAD/COPYRIGHT>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/anthonix/ffts/HEAD/README.md>
  - <https://raw.githubusercontent.com/anthonix/ffts/HEAD/include/ffts.h>
  - <https://raw.githubusercontent.com/anthonix/ffts/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/anthonix/ffts/HEAD/COPYRIGHT>
  - <https://raw.githubusercontent.com/anthonix/ffts/HEAD/src/ffts.c>
  - <https://raw.githubusercontent.com/anthonix/ffts/HEAD/src/ffts_chirp_z.c>
  - <https://raw.githubusercontent.com/anthonix/ffts/HEAD/src/codegen.c>
  - <https://raw.githubusercontent.com/anthonix/ffts/HEAD/src/ffts_static.c>
  - <https://raw.githubusercontent.com/anthonix/ffts/HEAD/src/ffts_real.c>
  - <https://github.com/anthonix/ffts/issues/28>
  - <https://github.com/anthonix/ffts/issues>
  - <https://github.com/anthonix/ffts/issues/81>
  - <https://github.com/anthonix/ffts/commits>
  - <https://github.com/linkotec/ffts>
  - <https://github.com/linkotec/ffts/commits>
  - <https://github.com/ValveSoftware/ffts>
  - <https://raw.githubusercontent.com/project-gemmi/benchmarking-fft/HEAD/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/anthonix/ffts`) · [data/wave8/enrich/raw/github_com_anthonix_ffts.json](../../../data/wave8/enrich/raw/github_com_anthonix_ffts.json) (enrichment confidence 0.75)

</details>
