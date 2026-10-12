# Randen

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> AES-based backtracking-resistant PRNG (C++11 URBG) at roughly std::mt19937_64 speed; reference code for absl::BitGen's engine.

| | |
|---|---|
| **Beats** | std::mt19937_64 / pcg64_c32 (also Philox, ISAAC, ChaCha8) |
| **Claimed result** | README x86: microbenchmark 1.54 cpb vs mt19937_64 1.79 and pcg64_c32 0.78 (PCG faster); reservoir sampling 2.60 cpb vs mt19937_64 2.82 and pcg64_c32 3.03. Paper: geometric mean over applied tasks about 1.1x faster than Mersenne Twister on x86 and PPC; PCG fastest on x86 (paper's shuffle and reservoir tables show PCG \~1.2x faster than Randen) |
| **Workload** | Microbenchmark and applied tasks (Fisher-Yates shuffle, reservoir sampling, Monte Carlo) for an AES-NI based backtracking-resistant generator |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E5-2690 v3 (x86); also POWER8e |
| **Compiler and flags** | Paper: Clang r331746 -O3 -std=gnu++11; repo Makefile: clang++ -std=c++11 -O3 -fno-pic -mavx2 -maes (README: GCC 7.3 up to 1.6x and Clang 4.0.1 up to 1.3x more cycles/byte) |
| **Adoption** | 338 stars; archived 2023-06-12 (used by Abseil) |
| **Last commit** | 2018-10-05 |
| **Links** | [repository](https://github.com/google/randen) · [benchmark](https://arxiv.org/abs/1810.02227) |

## Verdict

On an Intel Xeon E5-2690 v3 (Haswell) with Clang -O3, Google's paper reports Randen about 1.1x faster than std::mt19937_64 (geomean over shuffle, reservoir sampling and Monte Carlo, also on POWER8), while pcg64_c32 is fastest on x86; the README's tight-loop microbenchmark shows 1.54 cpb vs 1.79 for mt19937_64 and 0.78 for pcg64_c32. The standard library implementation for mt19937_64 is not named.

## Use it when

- You want a default generator that is safe if outputs or state might be attacker-observable (shuffles, sampling, randomized algorithms in services) without paying CTR-DRBG or /dev/urandom costs (\~10x slower in the README table).
- Applied workloads (shuffle, reservoir sampling, Monte Carlo) on x86 with AES-NI where std::mt19937_64 is the incumbent: about 1.1x faster geomean per the paper, with 256 bytes of state versus mt19937_64's \~2.5 KB.
- Already on Abseil: use absl::BitGen, which is this algorithm with runtime AES dispatch and a portable fallback.
- x86-64 with AES-NI, POWER8+ with VSX, or ARMv8 with crypto extensions.

## Skip it when

- Raw throughput is the goal: pcg64_c32 is \~2x faster in the tight-loop microbenchmark (0.78 vs 1.54 cpb) and the paper's shuffle tables show PCG ahead; non-crypto generators like Romu or xoshiro are faster still.
- Targets without hardware AES: the standalone repo has no software fallback (vector128.h hits #error "Port"); only Abseil ships a slow portable path.
- You need a vetted CSPRNG for keys/tokens: the README says the algorithm is 'still under review and subject to change' and the paper is not peer reviewed.
- You need a maintained standalone library: archived 2023-06-12, last commit 2018-10-05, no versioned releases or build system beyond a Makefile.
- Performance depends heavily on compiler unrolling: README reports up to 1.6x more cycles/byte with GCC 7.3 and 1.3x with Clang 4.0.1.

## How it is fast

It plugs a 2048-bit Simpira-v2-style permutation (a 16-branch generalized Feistel network with improved block shuffle, 17 rounds of 2-round AES-128 functions) into the Reverie sponge construction, so one permutation call refills a 240-byte output buffer while keeping a 128-bit hidden capacity for backtracking resistance. The AES rounds run on hardware AES instructions (AES-NI, POWER8 VSX crypto, ARMv8 crypto), and operator() is just a buffer read with a rare refill branch.

## Compared with alternatives

Pick Randen when you need attack resistance (indistinguishability plus backtracking resistance) at near-Mersenne-Twister cost; Romu, SIMDxorshift and Randompack are faster but non-cryptographic, and Squares/Philox-style counter-based RNGs suit parallel stream splitting rather than state-compromise resistance.

## Integration

| | |
|---|---|
| **Form** | source-drop (randen.h, randen.cc, vector128.h) |
| **Dependencies** | none (compiler intrinsics only) |
| **Minimum toolchain** | C++11; Makefile uses clang++ -O3 -mavx2 -maes; Clang recommended for loop unrolling |
| **Platforms** | x86 with SSE2+AES-NI, POWER8 with VSX, ARMv8 with NEON+crypto; build fails elsewhere |
| **Thread safety** | not documented; engine is a plain mutable object with no synchronization (Abseil states its BitGen is not thread safe, like std engines) |
| **Drop-in for the baseline** | yes |

## Gotchas

- Must be compiled with AES enabled (-maes or equivalent); there is no runtime CPU dispatch in this repo.
- Object is alignas(32) with 256 bytes of state; heap allocation of the engine relies on aligned new (C++17) or a custom allocator under C++11.
- Backtracking resistance only covers outputs before the last Generate call; prediction resistance needs periodic reseed() with fresh entropy.
- Output stream may change if the algorithm is revised (README: 'subject to change'); Abseil's absl::BitGen deliberately offers no seed stability across runs.

## Known shortcomings

- Google preprint, not peer reviewed; only \~1.1x faster than mt19937 (geomean) and slower than PCG in the microbenchmark and most paper tasks; README and paper reservoir-sampling tables disagree; standard library not stated; archived (last commit 2018-10-05).
- No software fallback: will not compile without hardware AES (vector128.h #error "Port"); README says algorithm 'still under review and subject to change'; speed depends on loop unrolling (GCC 7.3 up to 1.6x more cycles/byte); maintained version is Abseil's absl::BitGen.

## Caveats and trade-offs

Modest win over std::mt19937_64 (\~1.1x geomean, \~1.16x in microbenchmark derived from page data); slower than PCG in microbenchmark and most paper tasks; README reservoir table disagrees with paper's (README has Randen ahead of PCG); standard library used for mt19937_64 not stated; repo archived 2023-06-12, last commit 2018-10-05; algorithm lives on in Abseil's absl::random

Requires AES-NI (Intel/AMD/POWER); 2048-bit state; main selling point is cryptographic-strength backtracking resistance at near-PCG speed, not raw speed

## Maintenance

Archived since 2023-06-12 (last commit 2018-10-05) but Apache-2.0 and small enough to vendor; for production prefer the maintained Abseil absl::BitGen implementation.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded from B: the arXiv paper is a Google preprint (not peer reviewed) but states CPU (Xeon E5-2690 v3), compiler (Clang r331746) and flags (-O3 -std=gnu++11), and the benchmark code is public in the repo (randen_benchmark.cc, built by Makefile with clang++ -O3 -mavx2 -maes) and runs against std &lt;random&gt; mt19937_64 and pcg64.
- **Verifier notes:** Paper is self-published (Google), so B was not justified on peer review, but full methodology plus public bench code earns A. Stdlib implementation not stated, baseline_stdlib left empty.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `compared_against_cpp_std_directly`, `last_commit`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/1810.02227>
  - <https://arxiv.org/pdf/1810.02227>
  - <https://github.com/google/randen>
  - <https://github.com/google/randen/commits>
  - <https://raw.githubusercontent.com/google/randen/HEAD/README.md>
  - <https://raw.githubusercontent.com/google/randen/HEAD/Makefile>
  - <https://raw.githubusercontent.com/google/randen/HEAD/randen_benchmark.cc>
  - <https://raw.githubusercontent.com/google/randen/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/google/randen/HEAD/README.md>
  - <https://raw.githubusercontent.com/google/randen/HEAD/randen.h>
  - <https://raw.githubusercontent.com/google/randen/HEAD/randen.cc>
  - <https://raw.githubusercontent.com/google/randen/HEAD/vector128.h>
  - <https://raw.githubusercontent.com/google/randen/HEAD/Makefile>
  - <https://github.com/google/randen/issues>
  - <https://github.com/google/randen/issues/4>
  - <https://abseil.io/docs/cpp/guides/random>
  - <https://github.com/abseil/abseil-cpp/blob/master/absl/random/internal/randen.h>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/google/randen`) · [data/wave8/enrich/raw/github_com_google_randen.json](../../../data/wave8/enrich/raw/github_com_google_randen.json) (enrichment confidence 0.8)

</details>
