# AESRand

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> AES-NI hardware-accelerated PRNG streaming 256 bits per iteration, far outpacing std::mt19937 in raw throughput.

| | |
|---|---|
| **Beats** | std::mt19937 |
| **Claimed result** | 27.45 GB/s (single-stream) / 34.35 GB/s (dual-stream) for AESRand vs 0.858 GB/s for std::mt19937 (\~32x / \~40x throughput; derived from page data in BenchmarkResults.md); on a cycles-per-iteration basis, 3.69 cycles/iter (32 bytes/iter) vs mt19937's 14.76 cycles/iter (4 bytes/iter), \~4x fewer cycles per call (derived from page data) |
| **Workload** | 5-10 billion-iteration tight loop generating random bytes summed into an anti-optimizer accumulator, timed with QueryPerformanceCounter, CPU clock locked to remove turbo-boost noise. |
| **Metric** | throughput |
| **Hardware** | AMD Threadripper 1950x, manually locked to 3.4 GHz (verified in Ryzen Master) |
| **Compiler and flags** | Visual Studio 2017 (toolset v141, Windows build); the build configuration used for the benchmark is not stated. The repo's Release\|x64 config sets MaxSpeed (/O2), intrinsics, whole-program optimization, and AVX2. |
| **Adoption** | 62 stars |
| **Last commit** | 2019-04-18 |
| **Links** | [repository](https://github.com/dragontamer/AESRand) · [benchmark](https://github.com/dragontamer/AESRand/blob/master/BenchmarkResults.md) |

## Verdict

On the author's own benchmark (5-10 billion iteration tight loop, Visual Studio 2017 x64 build, AMD Threadripper 1950x manually locked to 3.4GHz), AESRand measured 27.45 GB/s single-stream / 34.35 GB/s dual-stream versus 0.858 GB/s for std::mt19937 (MSVC STL) — about 32x/40x higher throughput, or 3.69 cycles per 32-byte iteration versus mt19937's 14.76 cycles per 4-byte iteration. The README itself flags that mt19937 was not inlined in this test, which may inflate the ratio.

## Use it when

- Bulk random-byte generation on x86-64 with AES-NI (Westmere/Bulldozer or newer) where throughput, not API compatibility, is the goal
- Workloads that can consume 256 bits per draw at once (buffer fill, Monte Carlo sampling, fuzz-input generation)
- You're willing to vendor a small source drop and manage RNG state explicitly per thread/stream yourself
- You need many verified-independent parallel streams (PractRand-clean to 4TB across the tested stream space) rather than a single sequential stream
- You're prototyping/researching AES-NI-based RNG design rather than shipping a supported dependency

## Skip it when

- Target hardware lacks AES-NI / ARMv8 crypto extension / Power9 crypto builtins (no software fallback exists)
- You need a std::mt19937-compatible engine you can plug into &lt;random&gt; distributions or std::shuffle without wrapper code
- You need cryptographic-strength randomness; this is a statistical PRNG only, with an author-documented weakness to single-bit counter changes
- You'd run the parallel-stream (dual-output) variant past 8TB of PractRand-equivalent output, where it's known to fail
- You need active maintenance, releases, CI, or community support (repo is a single-author research prototype, abandoned since 2019)

## How it is fast

The 'counter' portion (AESRand_increment) is a single SIMD add with 1-cycle latency, kept deliberately minimal since it bounds the loop's critical path. The 'mixer' chains 2-3 AESENC/AESDEC round instructions per iteration, which have 1-per-cycle (or 2-per-cycle on AMD Zen) throughput, so instruction-level parallelism across loop iterations hides most of the \~4-cycle AES latency. The dual-stream variant runs two independent counter/mixer chains to expose more ILP, measured at 2.95 cycles/iteration vs 3.69 for the single-stream version.

## Compared with alternatives

Pick AESRand over ALU-based siblings (PCG, xoshiro_cpp, wjakob/pcg32, biski64, nanobench::Rng) when you specifically want to saturate AES-NI throughput for bulk byte generation rather than a small, portable, dependency-free integer generator. Prefer Random123 (also AES-NI-based) instead if you want a similarly hardware-accelerated generator with more independent, peer-reviewed statistical validation — Random123's reported margin over std::mt19937_64 (\~1.8x) is far more conservative than AESRand's \~32-40x, partly reflecting AESRand's larger per-call output and its non-inlined mt19937 baseline.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond compiler intrinsics (immintrin.h on x86, arm_neon.h on aarch64, GCC PPC crypto builtins on Power9) |
| **Minimum toolchain** | C++11 (AESRand_Paper's ARM Makefile pins -std=c++11, built with g++-8.3; the x86 Makefile passes no -std flag, just -maes; the Windows benchmark used VS2017/v141) |
| **Platforms** | x86-64 with AES-NI required for the benchmarked path; AESRand_Paper additionally ships aarch64 (ARMv8 crypto ext, via Makefile.arm) and Power9/PPC64 (via Makefile.power9) implementations, but only the x86 path was benchmarked |
| **Thread safety** | not documented; the core RNG has no global mutable state (state is an explicit value passed/returned by the caller), so per-thread state should be safe in practice, but the author does not state this |
| **Drop-in for the baseline** | false — free-function API over an explicit SIMD state, not a std::mt19937-compatible engine class |

## Gotchas

- Author's own benchmark notes std::mt19937 was NOT inlined by MSVC, which may inflate the measured speedup vs. an inlined baseline
- 1-bit changes to the counter increment are a documented weak direction; the design compensates by changing the full 128-bit state every step
- The parallel-stream (dual-output) variant only varies the top 64 bits and fails PractRand beyond 8TB, so only \~2^35 verified-independent streams exist despite a 2^64 theoretical claim
- Three near-duplicate implementations exist in-tree (Windows/VS2017, AESRand_Linux, AESRand_Paper) with slightly different APIs (e.g. AESRand_rand vs AESRand_rand_uint32); pick one and expect to adapt it

## Caveats and trade-offs

Author's own benchmark notes explicitly that std::mt19937 'was NOT inlined' by MSVC in the test, which may inflate mt19937's measured cost and the resulting speedup ratio; first-party, single-machine result with no independent replication; exact compiler optimization flags not given.

Requires AES-NI hardware (x86 since Westmere/Bulldozer; author notes Power9/ARM would need adaptation); prototype/research quality rather than a packaged library; author flags a 1-bit-change statistical weakness and that the parallel-stream variant fails PractRand beyond 8TB.

## Maintenance

Abandoned since its last commit in April 2019; MIT-licensed and small enough to vendor as source, but it's a single-author research prototype with no releases, no CI, and only one (non-bug) closed issue — treat it as a design reference to adapt, not a supported dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** BenchmarkResults.md shows raw results (27.4534 / 34.3487 GBps AESRand vs 0.857752 GBps mt19937; 3.69 vs 14.76 cycles/iter) on a Threadripper 1950x locked to 3.4 GHz with public VS2017 code. The build configuration actually used is not stated, and mt19937 was not inlined, so this is first-party C, not A.
- **Verifier notes:** Numbers and derived ratios (\~32x/\~40x GB/s, \~4x cycles per call) check out against BenchmarkResults.md. The README confirms the 'mt19937 was NOT inlined' remark. Metadata confirmed: MIT, 62 stars, last commit 2019-04-18, abandoned.
- **Fields the verifier corrected:** `compiler_and_flags`
- **Pages the verifier opened:**
  - <https://github.com/dragontamer/AESRand>
  - <https://github.com/dragontamer/AESRand/blob/master/BenchmarkResults.md>
  - <https://github.com/dragontamer/AESRand/blob/master/README.md>
  - <https://github.com/dragontamer/AESRand/blob/master/AESRand/AESRand/AESRand.vcxproj>
- **Sources the enricher read:**
  - <https://github.com/dragontamer/AESRand>
  - <https://github.com/dragontamer/AESRand/blob/master/README.md>
  - <https://github.com/dragontamer/AESRand/blob/master/BenchmarkResults.md>
  - <https://github.com/dragontamer/AESRand/blob/master/AESRand_Linux/AESRand.cpp>
  - <https://github.com/dragontamer/AESRand/blob/master/AESRand_Paper/AESRand.hpp>
  - <https://github.com/dragontamer/AESRand/blob/master/AESRand_Paper/README.md>
  - <https://github.com/dragontamer/AESRand/blob/master/AESRand_Paper/UnitTest.cpp>
  - <https://github.com/dragontamer/AESRand/blob/master/AESRand_Paper/Makefile>
  - <https://github.com/dragontamer/AESRand/blob/master/AESRand_Paper/Makefile.arm>
  - https://github.com/dragontamer/AESRand/issues (search)
  - <https://github.com/dragontamer/AESRand/pulls>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/dragontamer/aesrand`) · [data/wave1/enrich/raw/github_com_dragontamer_aesrand.json](../../../data/wave1/enrich/raw/github_com_dragontamer_aesrand.json) (enrichment confidence 0.6)

</details>
