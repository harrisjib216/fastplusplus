# Random numbers

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md)</sub>

**What these beat:** std::mt19937, std::uniform_\*_distribution, std::shuffle  
**9 entries:** 4 tier A · 2 tier B · 3 tier C · 0 tier D · 9 copyable, 0 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**cpp_batched_random**](lemire-cpp-batched-random.md) | Header-only drop-in std::shuffle replacement that batches multiple Fisher-Yates draws from one 64-bit random word. | **A** | C++ | MIT | 🟢 active |
| 2 | [**PCG (pcg-cpp)**](imneme-pcg-cpp.md) | Header-only C++11 PCG-family RNG beating std::mt19937/std::mt19937_64 raw-generation throughput by \~2.6-4x. | **A** | C++ | Apache-2.0 | 🔴 abandoned |
| 3 | [**wjakob/pcg32**](wjakob-pcg32.md) | Tiny two-header PCG32 RNG beating std::mt19937 on speed, with an optional AVX2 8-wide variant. | **A** | C++ | Apache-2.0 | 🔴 abandoned |
| 4 | [**xoshiro_cpp (david-cortes)**](david-cortes-xoshiro-cpp.md) | Header-only xoshiro256++/128++ wrapper that drop-in replaces std::mt19937(_64) for &lt;random&gt; distributions. | **A** | C++ | CC0-1.0 | 🔴 abandoned |
| 5 | [**xoshiro/xoroshiro generators**](prng-di-unimi-it.md) | Public-domain xoshiro/xoroshiro PRNG family, faster than std::mt19937_64, not cryptographically secure. | **B** | C | 0BSD (generator sources… | 🟢 active |
| 6 | [**Random123**](deshawresearch-random123.md) | Header-only counter-based CPU/GPU RNG family (Philox, Threefry, ARS); only AES-NI variants clearly beat std::mt19937_64. | **B** | C++ | BSD-3-Clause | 🔴 abandoned |
| 7 | [**nanobench::Rng (RomuDuoJr)**](martinus-nanobench.md) | nanobench's built-in RomuDuoJr generator: a drop-in &lt;random&gt;-style 64-bit PRNG, \~1.3-3.9x faster than std::mt19937_64. | **C** | C++ | MIT | 🟢 active |
| 8 | [**biski64**](danielcota-biski64.md) | Tiny 3-word Weyl+rotate PRNG beating std::mt19937_64 on raw throughput; not a drop-in, ships as Rust crate + C reference source. | **C** | C | MIT | 🟡 stale |
| 9 | [**AESRand**](dragontamer-aesrand.md) | AES-NI hardware-accelerated PRNG streaming 256 bits per iteration, far outpacing std::mt19937 in raw throughput. | **C** | C++ | MIT | 🔴 abandoned |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
