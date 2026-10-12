# FastShuffleExperiments (nearly divisionless bounded random integers)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🟡 stale

> Benchmark and reference code for Lemire's nearly divisionless bounded random integers; Fisher-Yates shuffles about 8-10x faster than std::shuffle.

| | |
|---|---|
| **Beats** | std::shuffle (same underlying PRNG), plus OpenBSD-style and Java-style bounded-integer generation |
| **Claimed result** | README sample output (arrays of 1000 elements, ns per element): nearly divisionless 1.88 (32-bit) and 1.86 (64-bit) vs std::shuffle 18.66 and 15.28, vs OpenBSD-like 5.40 and 14.36, vs Java-like 3.08 and 7.96 (about 10x and 8x faster than std::shuffle, derived from page data); the README notes 'the exact numbers will vary'. |
| **Workload** | Random shuffles of arrays of 5 to 10^9 elements, ns per element, with 32-bit and 64-bit random words, comparing Lemire's nearly divisionless bounded-integer method against OpenBSD-like, Java-like, floating-point and std::shuffle approaches. |
| **Metric** | throughput |
| **Compiler and flags** | g++ or clang++ with -std=c++11 -O3 (from cpp/Makefile) |
| **Adoption** | 41 stars; technique adopted by libstdc++ std::uniform_int_distribution, Abseil, Swift, Go, Julia, Zig, NumPy per README |
| **Last commit** | 2024-03-12 |
| **Links** | [repository](https://github.com/lemire/FastShuffleExperiments) · [benchmark](https://raw.githubusercontent.com/lemire/FastShuffleExperiments/master/TOMACS_RCR/README.md) |

## Verdict

On the repo's own sample run (g++/clang++ -std=c++11 -O3, CPU and compiler version not stated), shuffling 1000-element uint32_t arrays with lehmer64 took 1.88 ns/element (32-bit words) and 1.86 ns/element (64-bit) with the nearly divisionless method versus 18.66 and 15.28 ns/element for std::shuffle driven by the same generator, about 10x and 8x. A WebSearch summary of the paper (not opened) says its figures were measured on an Intel i7-6700 (Skylake, 3.4 GHz) with GCC 5.4 -O3 -march=native, where std::shuffle performed close to the OpenBSD-like method.

## Use it when

- You need unbiased random integers in [0, n) or a Fisher-Yates shuffle in a hot loop and your toolchain's std::uniform_int_distribution / std::shuffle still uses division-based rejection (MSVC STL, libc++ or an older libstdc++; check yours).
- Writing your own shuffle, reservoir sampler or random index picker in C/C++ and want a short Apache-2.0 reference for the correct multiply-and-reject code (32-bit and 64-bit variants).
- Arrays from a few elements up to about 10^6 that fit in cache, where range reduction dominates: the sample run shows 1.8-1.9 ns/element versus 15-19 ns for std::shuffle.
- Reproducing or extending the TOMACS paper's figures (make benchmark / make plot in TOMACS_RCR).

## Skip it when

- As a library dependency: it is experiment code with global generator state, uint32_t-only arrays and no packaging or tests beyond a permutation check; copy the bounded-integer function instead.
- When your standard library already uses this method: the README says GNU libstdc++ adopted it for std::uniform_int_distribution, so the gap against a current libstdc++ std::shuffle is smaller than the sample output shows.
- MSVC or 32-bit targets without __uint128_t: the 64-bit variants and the lehmer64 generator need 128-bit integer support.
- Very large arrays (10^7 to 10^9 elements), where cache misses dominate and every method slows to roughly 6-47 ns/element; the nearly divisionless shuffle is still fastest of the unbuffered methods but by a smaller factor (about 3.6-3.8x vs std::shuffle at 10^9 in the sample run).
- When you need batched or SIMD generation of many bounded integers: Lemire's later batched technique is a separate project.

## How it is fast

Instead of x % n, it multiplies the random word by n into a double-width product (64-bit for 32-bit words, __uint128_t for 64-bit words) and takes the high half as the result; the low half tells whether the draw falls in the biased region, and only then (probability below n/2^L) does it compute -n % n and possibly redraw. So almost every bounded integer costs one multiply and one compare instead of one or two hardware divisions, while staying exactly unbiased. The benchmark pairs it with lehmer64, a 128-bit multiplicative generator that is itself one multiply per output.

## Compared with alternatives

Pick this as the C++ reference for the range-reduction step (unbiased integers in [0, n) and shuffling), which fastrand ports to Python; generator siblings such as testingRNG (lehmer64, aesctr) or simdrng speed up the raw random bits instead, so they combine with this method rather than compete with it.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (C++ standard library only; gnuplot 5.2 only for the RCR figures) |
| **Minimum toolchain** | C++11 (-std=c++11 in the Makefile); GCC or Clang for __uint128_t; README assumes a Linux-like system |
| **Platforms** | 64-bit targets whose compiler provides __uint128_t (e.g. x86-64, aarch64 with GCC/Clang); not MSVC |
| **Thread safety** | Not thread-safe as written: lehmer64 and the other generators keep static global state (e.g. g_lehmer64_state) seeded by setseed(); the bounded-integer functions themselves are stateless. |
| **Drop-in for the baseline** | no |

## Gotchas

- The generator is passed as a template parameter that must be a function pointer to a global-state function; a std:: engine object cannot be plugged in without a wrapper, so std::shuffle's column uses a small URBG wrapper around the same lehmer64 function.
- The float/double-multiplication variants use only 24 or 53 random bits and are not exactly unbiased; use only the nearly divisionless variant if fairness matters.
- The 'precomputed random indexes' column (about 0.9 ns/element) excludes index generation from the timing, so it is a lower bound, not a usable shuffle.
- The RCR README's sample numbers carry no CPU or compiler and say 'the exact numbers will vary'; the RCR gnuplot script plots the 32-bit Figure 3a std::shuffle series from the 64-bit rows.

## Known shortcomings

- Sample output has no CPU or compiler version; current libstdc++ already uses this technique, so the gain over today's std::shuffle is smaller.
- Experiment code, not a library: global lehmer64 state, uint32_t arrays only, needs __uint128_t (no MSVC). Float variants are biased. The precomputed column leaves index generation out of the timing.

## Caveats and trade-offs

Peer-reviewed paper (ACM TOMACS 2019, 'Fast Random Integer Generation in an Interval') with a replication package, but the numbers on the page are an illustrative sample run ('the exact numbers will vary') with no CPU, compiler version or standard library stated. The std::shuffle baseline reflects libstdc++ before it adopted this very technique in std::uniform_int_distribution, so the gap against a current libstdc++ is smaller. The benchmark generator is lehmer64, not std::mt19937, so the std::shuffle column isolates the range-reduction and shuffle cost. In the RCR gnuplot script, Figure 3a (shuffle32.pdf) plots the std::shuffle series from the 64-bit rows ('every 2::1'), which understates std::shuffle's 32-bit cost in that figure. The repo Makefile uses -O3 without -march. Last commit 2024-03-12.

Needs 128-bit multiplication (__uint128_t) for 64-bit words; the buffered/precomputed variants trade memory for speed; unbiased, nearly divisionless rejection method.

## Maintenance

Stale research code (last commit 2024-03-12, no issues filed) under Apache-2.0; the technique matters more than the repo, which is small enough to copy from and is already absorbed into libstdc++, Abseil, Go, Swift, Julia, Zig and NumPy per the README.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** This is the replication package (TOMACS_RCR) of a peer-reviewed ACM TOMACS 29(1) 2019 paper, and cpp/shuffle.cpp times std::shuffle beside the OpenBSD-like, Java-like and nearly divisionless shuffles on the same lehmer64 generator. The repo states only g++/clang++ with -std=c++11 -O3; the sample output has no CPU or compiler version, and the paper itself could not be opened, so not A.
- **Verifier notes:** Sample numbers at size 10000 (32-bit: 1.80 / 5.32 / 2.98 / 18.57; 64-bit: 1.78 / 14.40 / 7.97 / 15.23) match TOMACS_RCR/README.md; INCLUDESTDSHUFFLE is defined, so the std::shuffle column is live. A WebSearch summary (paper not opened; arXiv, ACM DL and lemire.me are blocked) says the paper used an Intel i7-6700 with GCC 5.4 -O3 -march=native and found std::shuffle close to the OpenBSD-like method; if confirmed, this could be retiered to A with that paper as benchmark_url. Not a duplicate of cpp_batched_random (the later batched technique, already listed). Metadata: Apache-2.0, 41 stars, 5 forks, 56 commits; stale.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/lemire/FastShuffleExperiments/HEAD/TOMACS_RCR/README.md>
  - <https://raw.githubusercontent.com/lemire/FastShuffleExperiments/HEAD/README.md>
  - <https://raw.githubusercontent.com/lemire/FastShuffleExperiments/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/lemire/FastShuffleExperiments/HEAD/TOMACS_RCR/Makefile>
  - <https://raw.githubusercontent.com/lemire/FastShuffleExperiments/HEAD/cpp/shuffle.cpp>
  - <https://raw.githubusercontent.com/lemire/FastShuffleExperiments/HEAD/TOMACS_RCR/gnuplot/shuffle.gnuplot>
  - <https://raw.githubusercontent.com/lemire/FastShuffleExperiments/HEAD/LICENSE>
  - <https://github.com/lemire/FastShuffleExperiments>
  - <https://github.com/lemire/FastShuffleExperiments/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/lemire/FastShuffleExperiments/HEAD/README.md>
  - <https://raw.githubusercontent.com/lemire/FastShuffleExperiments/HEAD/TOMACS_RCR/README.md>
  - <https://raw.githubusercontent.com/lemire/FastShuffleExperiments/HEAD/TOMACS_RCR/Makefile>
  - <https://raw.githubusercontent.com/lemire/FastShuffleExperiments/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/lemire/FastShuffleExperiments/HEAD/cpp/shuffle.cpp>
  - <https://raw.githubusercontent.com/lemire/FastShuffleExperiments/HEAD/cpp/shuffle.h>
  - <https://raw.githubusercontent.com/lemire/FastShuffleExperiments/HEAD/cpp/rangedrand.h>
  - <https://raw.githubusercontent.com/lemire/FastShuffleExperiments/HEAD/cpp/lehmer64.h>
  - <https://raw.githubusercontent.com/lemire/FastShuffleExperiments/HEAD/LICENSE>
  - <https://github.com/lemire/FastShuffleExperiments/tree/master/cpp>
  - <https://github.com/lemire/FastShuffleExperiments/issues?q=is%3Aissue>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/lemire/fastshuffleexperiments`) · [data/wave8/enrich/raw/github_com_lemire_fastshuffleexperiments.json](../../../data/wave8/enrich/raw/github_com_lemire_fastshuffleexperiments.json) (enrichment confidence 0.8)

</details>
