# benchmark-rngs PhiloxSIMD (AVX Philox4x32-10)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Study only · `C++` · `no license` · 🔴 abandoned

> AVX2 8-lane Philox4x32-10 engine in a 2019 benchmark harness; 3.7x xoshiro256\*\* and 9x std::mt19937 single-thread.

| | |
|---|---|
| **Beats** | xoshiro256\*\*, PCG64 and std::mt19937 (also an at::mt19937 implementation shipped in the repo) |
| **Claimed result** | results/README.md, 1 thread, 134217728 numbers (best average): philox_simd (global) 0.176 s and philox_simd (thread local) 0.188 s vs xoshiro256\*\* 0.651 s, pcg64 0.659 s, std::mt19937 1.609 s, at::mt19937 0.393 s, scalar philox 0.439 s; about 3.7x vs xoshiro256\*\* and pcg64 and 9.1x vs std::mt19937 (derived from page data). |
| **Workload** | Wall time in seconds to generate 134,217,728 random numbers with 1 to 1024 threads (and 8 to 8.6e9 numbers on 1 thread), global vs thread-local generators. |
| **Metric** | throughput |
| **Hardware** | 16 x Intel Xeon E5-1660 v4 @ 3.20 GHz (1 socket), Ubuntu 18.04, turbo boost off, performance governor |
| **Compiler and flags** | GNU 7.4.0; CMakeLists.txt sets CMAKE_CXX_FLAGS '-std=c++11 -Wall -pthread -march=native -lm' and the README builds with -DCMAKE_BUILD_TYPE=Release (CMake's default Release flags for GCC add -O3 -DNDEBUG) |
| **Adoption** | 4 stars |
| **Last commit** | 2019-07-18 |
| **Links** | [repository](https://github.com/syed-ahmed/benchmark-rngs) · [benchmark](https://raw.githubusercontent.com/syed-ahmed/benchmark-rngs/master/results/README.md) |

## Verdict

On a Xeon E5-1660 v4 (turbo off, Ubuntu 18.04, GCC 7.4.0, -std=c++11 -march=native in a CMake Release build), one thread generating 134,217,728 32-bit values took 0.176 s with SIMD Philox (bulk vector consumption), 0.439 s with scalar Philox, 0.651 s with xoshiro256\*\*, 0.659 s with the 'pcg64' row (actually pcg32, half the bits), 0.393 s with at::mt19937 and 1.609 s with libstdc++ std::mt19937. That is about 3.7x faster than xoshiro256\*\* and 9.1x faster than std::mt19937 (derived from page data).

## Use it when

- You need bulk 32-bit random words on x86-64 with AVX2 and can consume them as __m256i vectors (e.g. filling buffers or vectorized distribution transforms).
- You want counter-based streams with PyTorch/CUDA Philox semantics (seed, subsequence, offset skip-ahead) so each thread gets an independent subsequence at no setup cost.
- Multithreaded generation with one engine per thread. Thread-local SIMD Philox reached about 0.03 s wall time for 134M values at 8 threads, against 0.188 s on one thread (derived from page data).
- As a reference for writing your own AVX2 Philox kernel. The core is about 150 lines.

## Skip it when

- You need a licensed dependency. The repo has no LICENSE file, so legally it is reference-only, even though the code says it was adapted from PyTorch (BSD-3-Clause).
- You need output identical to Random123, cuRAND or PyTorch Philox. That requires setting UNSHUFFLE to 1, which the published timings did not include.
- Non-x86 targets, MSVC, or CPUs without AVX2. It includes &lt;x86intrin.h&gt;, uses __builtin_expect and AVX2 integer intrinsics, and has no NEON or scalar fallback in this header.
- You draw a few values at a time through operator(). Only the bulk next32 path was benchmarked, and at 8 values xoshiro256\*\* was faster (1.58e-7 s vs 1.79e-7 s).
- You need a maintained library with tests. The last commit was in 2019, the harness's equality check against scalar Philox is commented out, and it has no CI.

## How it is fast

It runs 8 independent Philox counters at once in AVX2 lanes. Each round uses _mm256_mul_epu32 on even and odd lanes plus shuffle/unpack to form the 32x32-to-64 mulhi/lo pairs, and the 10 rounds are fully vectorized with broadcast keys. Counter increments are one vector add, with a scalar fallback only near 32-bit wrap. The default build (UNSHUFFLE 0) skips the 4x8 transpose, so the outputs come out word-major rather than in standard Philox order.

## Compared with alternatives

Pick it only to study a compact AVX2 Philox kernel compatible with PyTorch's (seed, subsequence, offset) API. For something you can ship, compare OpenRAND (counter-based Philox and Squares for CPU and GPU, with paper measurements), vphilox (vectorized Philox benchmarked on several CPUs) or simdrng/VMT19937 (vectorized xoshiro and Mersenne Twister against std engines), and check their licenses, since this repo has none.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Array.h (at::detail::Array) and splitmix64.h from the same repo; the harness also uses CLI11 and libfort (vendored) |
| **Minimum toolchain** | C++11 (CMakeLists sets -std=c++11 -march=native); GCC or Clang because of &lt;x86intrin.h&gt; and __builtin_expect; harness tested with GCC 7.4.0 |
| **Platforms** | x86-64 with AVX2 required |
| **Thread safety** | Not thread-safe per engine (mutable counter and output buffer). The harness either guards one global engine with a std::mutex held for the whole loop, or gives each thread its own engine with subsequence = thread index. |
| **Drop-in for the baseline** | partial: operator() yields uint32_t like std::mt19937, but it lacks the URBG members (result_type/min/max), seeding semantics and output stream differ, and the fast path is the vector next32() API |

## Gotchas

- With UNSHUFFLE 0 (the default), each 32-word block is a transposed reordering of standard Philox4x32-10 output. check_philox_vs_simd() in benchmark.cpp is commented out with a note that UNSHUFFLE must be 1 for the outputs to match.
- The 'pcg64' baseline in PCG.h is actually PCG32 (pcg32_random_r: 64-bit state, 32-bit XSH-RR output), but the harness counts each call as two 32-bit randoms. That row therefore produced only half the bits it claims.
- Baseline per-call costs derived from page data are high (about 9.7 ns per xoshiro256\*\* call and 12 ns per std::mt19937 output, while the repo's own at::mt19937 runs the same algorithm in 2.9 ns). Part of the 9x gap over std::mt19937 is likely harness or implementation overhead, not generator cost. Against at::mt19937 the gap is 2.2x.
- In the 'global' multithreaded runs, a mutex is held for each thread's entire loop, so those runs are serialized and their wall time stays flat as threads are added.

## Known shortcomings

- No license; PhiloxSIMD defaults to UNSHUFFLE 0, so its output is a block-reordered Philox stream (same values, different order) and the timings leave out the reorder cost.
- Benchmark flaws: the 'pcg64' baseline in PCG.h is really pcg32 (32-bit output) yet the harness counts each call as two 32-bit values; the 9.1x over std::mt19937 is partly harness overhead (std::mt19937 \~12 ns per output vs the repo's own at::mt19937 doing the same work in 2.9 ns; against at::mt19937 the gain is 2.2x, derived from page data). In the 'global' multithreaded runs a mutex is held for each thread's whole loop, so those runs are serialized. Equality check against scalar Philox is commented out because outputs match only with UNSHUFFLE=1.

## Caveats and trade-offs

No LICENSE file (none in the top-level listing, and the GitHub sidebar shows no license), so usability is reference; Philox.h and PhiloxSIMD.h say the engine was 'Originally implemented in PyTorch's fusion compiler' (PyTorch is BSD-3-Clause), but the repo itself grants nothing. PhiloxSIMD.h defaults to UNSHUFFLE 0, which skips the transpose ('set to 1 to match non-SIMD ordering'), so the benchmarked SIMD stream is a block-wise reordering of standard Philox4x32-10 output and the timings exclude the cost of restoring standard order. The SIMD variants consume outputs with vector adds while scalar engines are called one value at a time. Counts are in 32-bit units for every engine (64-bit engines count two per call), so the comparison is per bit. At tiny counts (8 numbers) xoshiro256\*\* is faster (1.58e-7 s vs 1.79e-7 s). 2019 results on GCC 7.4, single machine.

x86-only SIMD (x86intrin.h, built with -march=native); a counter-based Philox generator, so streams and statistical properties differ from xoshiro/PCG/MT; PhiloxSIMD.h has an UNSHUFFLE switch to match the non-SIMD output order. The repo is a benchmark harness with the headers inside, not a packaged library.

## Maintenance

Abandoned since 2019-07-18 (4 stars), with no license, so it is reference-only. The PhiloxSIMD.h technique is worth reading, but reimplement it or take PyTorch's BSD code rather than copying from here.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** results/README.md gives the timings with GNU 7.4.0, Ubuntu 18.04 and the CPU model (Xeon E5-1660 v4, turbo off, performance governor); the benchmark code is public (benchmark.cpp, functions.cpp) and CMakeLists.txt states the flags (-std=c++11 -Wall -pthread -march=native, CMake Release build).
- **Verifier notes:** All quoted 1-thread numbers match results/README.md exactly (philox_simd global 0.176079 s, thread local 0.187869 s, xoshiro256\*\* 0.650694 s, pcg64 0.65864 s, std::mt19937 1.60893 s, at::mt19937 0.392547 s, philox 0.438846 s). baseline_stdlib set to libstdc++ because the only compiler is GNU 7.4.0 on Ubuntu. 4 stars, last commit 2019-07-18, no license confirmed.
- **Fields the verifier corrected:** `compiler_and_flags`, `baseline_stdlib`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/syed-ahmed/benchmark-rngs/master/results/README.md>
  - <https://raw.githubusercontent.com/syed-ahmed/benchmark-rngs/master/README.md>
  - <https://raw.githubusercontent.com/syed-ahmed/benchmark-rngs/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/syed-ahmed/benchmark-rngs/master/functions.cpp>
  - <https://raw.githubusercontent.com/syed-ahmed/benchmark-rngs/master/benchmark.cpp>
  - <https://raw.githubusercontent.com/syed-ahmed/benchmark-rngs/master/PhiloxSIMD.h>
  - <https://raw.githubusercontent.com/syed-ahmed/benchmark-rngs/master/Philox.h>
  - <https://github.com/syed-ahmed/benchmark-rngs>
  - <https://github.com/syed-ahmed/benchmark-rngs/commits>
- **Sources the enricher read:**
  - <https://github.com/syed-ahmed/benchmark-rngs>
  - <https://raw.githubusercontent.com/syed-ahmed/benchmark-rngs/master/README.md>
  - <https://raw.githubusercontent.com/syed-ahmed/benchmark-rngs/master/results/README.md>
  - <https://raw.githubusercontent.com/syed-ahmed/benchmark-rngs/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/syed-ahmed/benchmark-rngs/master/PhiloxSIMD.h>
  - <https://raw.githubusercontent.com/syed-ahmed/benchmark-rngs/master/Philox.h>
  - <https://raw.githubusercontent.com/syed-ahmed/benchmark-rngs/master/benchmark.cpp>
  - <https://raw.githubusercontent.com/syed-ahmed/benchmark-rngs/master/functions.cpp>
  - <https://raw.githubusercontent.com/syed-ahmed/benchmark-rngs/master/xoshiro256starstar.h>
  - <https://raw.githubusercontent.com/syed-ahmed/benchmark-rngs/master/PCG.h>
  - <https://raw.githubusercontent.com/syed-ahmed/benchmark-rngs/master/MT19937.h>
  - <https://raw.githubusercontent.com/syed-ahmed/benchmark-rngs/master/splitmix64.h>
  - <https://raw.githubusercontent.com/syed-ahmed/benchmark-rngs/master/Array.h>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/syed-ahmed/benchmark-rngs`) · [data/wave8/enrich/raw/github_com_syed_ahmed_benchmark_rngs.json](../../../data/wave8/enrich/raw/github_com_syed_ahmed_benchmark_rngs.json) (enrichment confidence 0.8)

</details>
