# pXart

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Header-only C++17 SSE/AVX2 MT19937, Xoroshiro128+ and MSWS; AVX2 MT19937 matches std::mt19937 output and generates it about 8x faster.

| | |
|---|---|
| **Beats** | std::mt19937 (libstdc++, GCC 9.2.0); also Boost.Random mt19937 |
| **Claimed result** | Thesis Table 9.1 (i7-7700K, 4.51 GHz, 16 GiB generated through a 16 KiB buffer): STL MT19937 9.29 s, Boost MT19937 5.79 s, pXart scalar MT19937 7.61 s, pXart SSE MT19937 2.11 s, pXart AVX MT19937 1.15 s (AVX about 8.1x faster than STL and 5.0x faster than Boost, derived from page data). Thesis text: scalar pXart beat the STL version but not Boost's; SSE/AVX are 'more than three times' / 'more than six times' faster than pXart scalar. Monte Carlo pi, 10^8 samples (Table 9.2): STL MT19937 with pXart's uniform function 0.53 s (0.72 s naive with std::uniform_real_distribution), Boost 0.33 s; pXart AVX MT19937 used as a drop-in through a cache ('AVX cache') 0.15 s, about 3.5x faster than STL (derived from page data); the 0.07 s 'AVX' figure also vectorizes the pi loop itself with AVX intrinsics in single precision, so it is not an RNG-only gain. |
| **Workload** | Bulk generation of 16 GiB of 32-bit random numbers through a 16 KiB cache buffer, plus a 10^8-sample Monte Carlo pi benchmark, comparing std::mt19937, Boost mt19937 and pXart scalar/SSE4.1/AVX2 MT19937 and Xoroshiro128+. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-7700K (Kaby Lake, 4.51 GHz measured); second machine Intel Core i5-8250U laptop |
| **Compiler and flags** | GCC 9.2.0, -O3 -march=native |
| **Adoption** | 3 stars; build2 package (cppget.org badge in README) |
| **Last commit** | 2021-01-18 |
| **Links** | [repository](https://github.com/lyrahgames/pxart) · [benchmark](https://raw.githubusercontent.com/lyrahgames/pxart/HEAD/docs/thesis/main.pdf) |

## Verdict

In the author's 2019 master's thesis (Jena), GCC 9.2.0 -O3 -march=native on a Core i7-7700K at 4.51 GHz, generating 16 GiB through a 16 KiB buffer took 9.29 s with libstdc++ std::mt19937, 5.79 s with Boost mt19937 and 1.15 s with pXart's AVX2 MT19937 (about 8.1x and 5.0x, derived from page data); scalar pXart MT19937 (7.61 s) beat STL but not Boost. In a 10^8-sample Monte Carlo pi run, using the AVX2 MT19937 through a buffer in scalar code took 0.15 s vs 0.53 s for STL with pXart's uniform conversion (about 3.5x, derived from page data).

## Use it when

- Code bound to the std::mt19937 sequence (reproducible simulations, saved seeds) that needs much higher throughput on x86 with AVX2 or SSE2
- Bulk fills of 32-bit randoms or floats, e.g. Monte Carlo inner loops where you can consume 8 values per call or buffer them
- SIMD kernels already written with AVX2 intrinsics that want random vectors directly in registers
- Projects that want a tiny MIT header-only dependency, usable via build2, CMake or by copying the pxart/ folder

## Skip it when

- Non-x86 targets: SIMD paths are SSE/AVX2 intrinsics only; ARM or other platforms fall back to the scalar engines
- When you need std &lt;random&gt; distributions on the vector engines: there are no normal, exponential or other non-uniform distributions
- When you are free to change the generator and want maximum speed: pXart's own AVX2 Xoroshiro128+ beats its AVX2 MT19937 (0.74 s vs 1.15 s for 16 GiB in the thesis), and other siblings are faster still
- Production code that needs maintenance or support: 3 stars, alpha build2 package, last commit January 2021
- Exact unbiased bounded integers: the multiply-shift range reduction has a small bias the code itself calls an approximation

## How it is fast

For MT19937 it vectorizes the state twist of a single generator (Agner Fog's technique): 8 consecutive state words are updated per AVX2 instruction, and a copy of the first new block stored past the end of the state array handles the wrap-around, so output order is unchanged. Xoroshiro128+ and MSWS instead run several independent instances side by side in the vector lanes (multi-stream), so their SIMD output differs from the scalar sequence. Uniform floats are made by OR-ing the top 23 (float) or 52 (double) random bits into the exponent of 1.0 and subtracting 1, and bounded integers use a multiply-shift instead of a division.

## Compared with alternatives

Pick pXart when you must keep the exact 32-bit std::mt19937 sequence and want a small C++17 header with AVX2/SSE paths; VMT19937 also covers mt19937_64 and AVX-512, and if the generator can change, SIMD xoshiro siblings (simdrng, Xoroshiro-style engines) or SHISHUA are faster.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (doctest for tests, perfevent for benchmarks) |
| **Minimum toolchain** | C++17; README lists GCC, Clang, Intel, MinGW and MSVC as tested; SIMD headers compile only when __AVX2__ / __SSE2__ are defined (e.g. -march=native) |
| **Platforms** | any for scalar engines; x86-64 with SSE2 (simd128 MT19937) or AVX2 (simd256) for the vectorized engines |
| **Thread safety** | not documented; engines are plain value types with no shared state, so use one instance per thread |
| **Drop-in for the baseline** | partial — scalar pxart::mt19937 and the SIMD versions reproduce the std::mt19937 sequence, but the SIMD engines return vectors, min()/max() are non-static, and the API (pxart::uniform, default_seeder) differs from std::mt19937 plus distributions |

## Gotchas

- pxart::simd256::xoroshiro128plus's default constructor leaves its state uninitialized, and its seeding constructor calls rng() eight times inside one _mm256_set_epi32 argument list, whose evaluation order is unspecified, so seeded streams can differ between compilers
- The templated RNG&& seeding constructor of pxart::mt19937 is a better match than the copy constructor for a non-const lvalue, so 'pxart::mt19937 b{a};' seeds b from a's outputs instead of copying a
- uniform&lt;double&gt; from a 32-bit engine only has 32 random bits (low mantissa bits are zero); uniform&lt;float&gt; uses 23 bits and returns [0,1)
- The SIMD headers silently define nothing if compiled without AVX2/SSE2 flags; check the PXART_SUPPORT_SIMD256_\* macros

## Known shortcomings

- The 0.07 s Monte Carlo figure vectorizes the whole pi loop; as an RNG-only drop-in ('AVX cache') it is 0.15 vs 0.53 s, \~3.5x.
- simd256::xoroshiro128plus default constructor leaves state uninitialized; its seeding constructor calls rng() 8 times inside one _mm256_set_epi32, so evaluation order is unspecified and seeds differ across compilers. Templated RNG&& constructor hijacks copies from non-const lvalues. AVX2 MT19937 is bit-identical to std::mt19937 (repo test checks 10M outputs).

## Caveats and trade-offs

Numbers come from a December 2019 master's thesis (Friedrich-Schiller-Universitat Jena) stored in the repo, not peer reviewed; results appear only in the thesis PDF, not in the README. GCC 9.2 / libstdc++ only, Kaby Lake hardware, single run per configuration with no variance reported. The 0.07 s Monte Carlo figure rewrites the whole pi loop in AVX intrinsics; the drop-in RNG gain ('AVX cache') is 0.15 s vs 0.53 s. The benchmark code at HEAD (2021) may differ slightly from the 2019 thesis version. Last commit 2021-01-18.

Needs an Intel CPU with SSE4.1/AVX2 for the vectorized engines. The SIMD engines interleave independent streams, so output differs from std::mt19937 and state is larger; own API (pxart::uniform, pxart::simd256::mt19937), not a drop-in std engine.

## Maintenance

Abandoned since January 2021 (3 stars, alpha cppget.org package), but MIT-licensed, header-only and small enough to vendor; the AVX2 MT19937 is tested bit-for-bit against std::mt19937.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** Thesis section 9 states GCC 9.2.0 with -O3 -march=native on an Intel Core i7-7700K (Table 9.1/9.2 at 4.51 GHz) and the benchmark code is public in the repo at benchmarks/basic/generate_cache.cpp and benchmarks/basic/monte_carlo_pi.cpp, which run std::mt19937 and boost::random::mt19937 next to pxart scalar/SSE/AVX MT19937.
- **Verifier notes:** All Table 9.1 and 9.2 numbers match the thesis PDF. The SIMD MT19937 vectorizes one MT19937 state (Fog's technique), so its output matches the scalar generator rather than being a different interleaved generator. Metadata confirmed on github.com: MIT, 3 stars, not fork/archived, last commit 2021-01-18.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/lyrahgames/pxart/HEAD/docs/thesis/main.pdf>
  - <https://raw.githubusercontent.com/lyrahgames/pxart/HEAD/README.md>
  - <https://github.com/lyrahgames/pxart>
  - <https://github.com/lyrahgames/pxart/commits>
  - <https://github.com/lyrahgames/pxart/tree/master/benchmarks>
  - <https://github.com/lyrahgames/pxart/tree/master/benchmarks/basic>
  - <https://raw.githubusercontent.com/lyrahgames/pxart/HEAD/benchmarks/basic/generate_cache.cpp>
  - <https://raw.githubusercontent.com/lyrahgames/pxart/HEAD/benchmarks/basic/monte_carlo_pi.cpp>
  - <https://raw.githubusercontent.com/lyrahgames/pxart/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/lyrahgames/pxart>
  - <https://github.com/lyrahgames/pxart/commits/master>
  - <https://github.com/lyrahgames/pxart/tree/master/pxart/pxart>
  - <https://github.com/lyrahgames/pxart/tree/master/tests>
  - <https://github.com/lyrahgames/pxart/tree/master/tests/basics>
  - <https://raw.githubusercontent.com/lyrahgames/pxart/HEAD/README.md>
  - <https://raw.githubusercontent.com/lyrahgames/pxart/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/lyrahgames/pxart/HEAD/docs/thesis/main.pdf>
  - <https://raw.githubusercontent.com/lyrahgames/pxart/HEAD/pxart/pxart/pxart.hpp>
  - <https://raw.githubusercontent.com/lyrahgames/pxart/HEAD/pxart/pxart/mt19937.hpp>
  - <https://raw.githubusercontent.com/lyrahgames/pxart/HEAD/pxart/pxart/uniform.hpp>
  - <https://raw.githubusercontent.com/lyrahgames/pxart/HEAD/pxart/pxart/algorithm.hpp>
  - <https://raw.githubusercontent.com/lyrahgames/pxart/HEAD/pxart/pxart/xoroshiro128plus.hpp>
  - <https://raw.githubusercontent.com/lyrahgames/pxart/HEAD/pxart/pxart/msws.hpp>
  - <https://raw.githubusercontent.com/lyrahgames/pxart/HEAD/pxart/pxart/simd256/mt19937.hpp>
  - <https://raw.githubusercontent.com/lyrahgames/pxart/HEAD/pxart/pxart/simd256/uniform.hpp>
  - <https://raw.githubusercontent.com/lyrahgames/pxart/HEAD/pxart/pxart/simd256/xoroshiro128plus.hpp>
  - <https://raw.githubusercontent.com/lyrahgames/pxart/HEAD/pxart/pxart/simd128/mt19937.hpp>
  - <https://raw.githubusercontent.com/lyrahgames/pxart/HEAD/benchmarks/basic/generate_cache.cpp>
  - <https://raw.githubusercontent.com/lyrahgames/pxart/HEAD/tests/basics/simd256/mt19937.cpp>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/lyrahgames/pxart`) · [data/wave8/enrich/raw/github_com_lyrahgames_pxart.json](../../../data/wave8/enrich/raw/github_com_lyrahgames_pxart.json) (enrichment confidence 0.85)

</details>
