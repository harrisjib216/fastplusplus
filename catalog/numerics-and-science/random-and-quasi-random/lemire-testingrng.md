# testingRNG (aesctr, lehmer64 winners)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Benchmark-plus-quality shootout of C/C++ PRNGs; its winners (aesctr, lehmer64) beat MT19937, PCG and xoroshiro128+ on throughput.

| | |
|---|---|
| **Beats** | mersennetwister (reference Nishimura/Matsumoto MT19937 C code adapted in source/mersennetwister.h, not std::mt19937), C library rand(), pcg32, pcg64, xoroshiro128+ |
| **Claimed result** | aesctr 5.35 GB/s (0.19 ns/byte), lehmer64 3.10 GB/s vs mersennetwister 1.68 GB/s, pcg32 1.55 GB/s, pcg64 2.53 GB/s, xoroshiro128plus 2.50 GB/s; wyrand 4.22 GB/s, splitmix64 4.35 GB/s |
| **Workload** | Shootout of C/C++ non-cryptographic generators with TestU01 BigCrush and PractRand 512 GB; speed via ./build/speed/rng |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Gold 6548N (2.8 GHz, turbo 3.5 GHz) |
| **Compiler and flags** | GCC 14, CMake Release (-O3 -DNDEBUG) plus -march=native (speed/CMakeLists.txt) |
| **Adoption** | 205 stars |
| **Last commit** | 2026-09-21 |
| **Links** | [repository](https://github.com/lemire/testingRNG) · [benchmark](https://github.com/lemire/testingRNG) |

## Verdict

On an Intel Xeon Gold 6548N with GCC 14 (CMake Release -O3 plus -march=native), filling a 4 KB buffer, aesctr produced 5.35 GB/s and lehmer64 3.10 GB/s, versus 1.68 GB/s for reference MT19937 C code, 1.55 GB/s pcg32, 2.53 GB/s pcg64, 2.50 GB/s xoroshiro128+ and 0.28 GB/s glibc rand(); splitmix64 (4.35) and wyrand (4.22) also beat lehmer64.

## Use it when

- Choosing a fast non-cryptographic 64-bit generator for simulation, sampling or randomized algorithms, with statistical-test results to back the choice
- Bulk generation on x86-64 with AES-NI where aesctr's \~5.35 GB/s (vs \~1.68 GB/s for MT19937) matters
- Portable fast 64-bit output on GCC/Clang targets with __uint128_t: lehmer64 is \~10 lines and passes BigCrush and PractRand
- Replacing MT19937 or rand() in hot loops: MT fails PractRand (BRank) in this repo and is \~1.8x slower than lehmer64
- Benchmarking your own generator: the harness gives a ready speed + TestU01 + PractRand pipeline

## Skip it when

- Cryptographic or adversarial settings: these are non-cryptographic generators; aesctr uses the seed as the AES key with a zero high half, and the repo makes no security claim
- Multithreaded code using the headers as-is: every generator keeps static global state (aesctr has a reentrant aesctr_r(state\*) variant; lehmer64 does not)
- MSVC or 32-bit targets: lehmer64 needs __uint128_t; aesctr compiles to nothing unless __AES__ is defined
- Latency-bound single-draw code: the README says the benchmark stresses throughput, and aesctr's 64-byte refill makes per-call cost uneven
- Where you need a std::uniform_random_bit_generator class with distributions, jump-ahead or streams: the headers are bare C functions

## How it is fast

lehmer64 is a 128-bit multiplicative LCG (one 64x64-&gt;128 multiply per output, returning the high 64 bits; about 1.75 instructions per byte). aesctr runs AES-128 rounds (AES-NI _mm_aesenc_si128) in counter mode over 4 interleaved counters, buffering 64 bytes per refill so the AES latency is hidden by instruction-level parallelism. Both pass BigCrush and PractRand 512 GB in the repo's runs, unlike the faster-looking xorshift/xoroshiro variants.

## Compared with alternatives

Pick testingRNG's headers when you want a scalar generator with published BigCrush and PractRand results side by side with speed; SHISHUA and xoshiro8x256pp are much faster for bulk SIMD fills, and Randen is the choice if you need attack-resistant output, while simdpcg/SIMDxorshift only accelerate a single family.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the generator headers (each includes splitmix64.h for seeding); the harness needs CMake 3.20+, C++20, lemire/counters via CPM, TestU01 (bundled zip) and PractRand |
| **Minimum toolchain** | Headers: C99 with GCC/Clang extensions (__uint128_t, __builtin_expect, immintrin.h); harness: C++20, GCC 14+ or Clang 17+ recommended |
| **Platforms** | lehmer64: any 64-bit GCC/Clang target; aesctr: x86-64 with AES-NI only; README assumes Linux or macOS on x64 |
| **Thread safety** | Not thread-safe: static global state per generator; aesctr_r/aesctr_seed_r take an explicit state struct |
| **Drop-in for the baseline** | partial — same call shape as rand()/genrand_int32 (seed then next) but different output sequences, 64-bit outputs, and no C++ URBG class |

## Gotchas

- The 'mersennetwister' baseline is the reference Nishimura/Matsumoto C code, not libstdc++ std::mt19937; no std:: generator is timed. The only C library baseline is rand() (0.28 GB/s)
- The speed binary is built with -march=native and fills a 4 KB buffer through a function pointer, so numbers measure in-cache throughput and may not carry to other CPUs or ARM (README warns)
- aesctr.h is wrapped in #ifdef __AES__; without -maes/-march=native it silently defines nothing
- lehmer64 is an LCG: low bits of the 128-bit state are weak, which is why it returns only the high 64 bits; do not change it to return the low half

## Known shortcomings

- 'mersennetwister' baseline is the reference MT19937 C code, not std::mt19937; only C-library baseline is rand().
- No std:: generator timed; speed run fills only a 4 KB buffer through a function pointer with -march=native (in-cache throughput); headers keep static global state, not thread-safe (aesctr has aesctr_r); lehmer64 needs __uint128_t; aesctr compiles to nothing without __AES__.

## Caveats and trade-offs

'mersennetwister' is the reference MT19937 C code adapted in source/mersennetwister.h, not libstdc++'s std::mt19937; the only C-library baseline is rand() (0.28 GB/s). Built with -march=native. Benchmark stresses throughput, not latency; ARM results may differ. Other winners (wyrand, splitmix64, aesdragontamer) overlap known entries.

aesctr needs AES-NI; lehmer64 uses 128-bit multiply; aesctr is a stream cipher, not a classic PRNG.

## Maintenance

Actively maintained (speed table refreshed 2026-09-21), Apache-2.0, and each generator is a small standalone header that is easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** README 'Speed results' table from speed/src/rng.cpp (./build/speed/rng) on an Intel Xeon Gold 6548N with GCC 14; flags are public in CMakeLists.txt (default Release, i.e. -O3 -DNDEBUG) plus -march=native in speed/CMakeLists.txt. Code, compiler, flags and CPU model are all public.
- **Verifier notes:** All claimed numbers match the README table exactly (aesctr 5.35 GB/s/0.19 ns/byte, lehmer64 3.10, mersennetwister 1.68, pcg32 1.55, pcg64 2.53, xoroshiro128plus 2.50, wyrand 4.22, splitmix64 4.35). The README table was refreshed on 2026-09-21 (Xeon Gold 6548N run).
- **Fields the verifier corrected:** `baseline`, `baseline_stdlib`, `compiler_and_flags`, `last_commit`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/lemire/testingRNG>
  - <https://raw.githubusercontent.com/lemire/testingRNG/HEAD/README.md>
  - <https://raw.githubusercontent.com/lemire/testingRNG/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/lemire/testingRNG/HEAD/speed/CMakeLists.txt>
  - <https://raw.githubusercontent.com/lemire/testingRNG/HEAD/source/mersennetwister.h>
  - <https://raw.githubusercontent.com/lemire/testingRNG/HEAD/LICENSE>
  - <https://github.com/lemire/testingRNG/commits>
- **Sources the enricher read:**
  - <https://github.com/lemire/testingRNG>
  - <https://raw.githubusercontent.com/lemire/testingRNG/HEAD/README.md>
  - <https://raw.githubusercontent.com/lemire/testingRNG/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/lemire/testingRNG/HEAD/speed/CMakeLists.txt>
  - <https://raw.githubusercontent.com/lemire/testingRNG/HEAD/speed/src/rng.cpp>
  - <https://raw.githubusercontent.com/lemire/testingRNG/HEAD/source/aesctr.h>
  - <https://raw.githubusercontent.com/lemire/testingRNG/HEAD/source/lehmer64.h>
  - <https://raw.githubusercontent.com/lemire/testingRNG/HEAD/source/mersennetwister.h>
  - <https://raw.githubusercontent.com/lemire/testingRNG/HEAD/LICENSE>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/lemire/testingrng`) · [data/wave8/enrich/raw/github_com_lemire_testingrng.json](../../../data/wave8/enrich/raw/github_com_lemire_testingrng.json) (enrichment confidence 0.85)

</details>
