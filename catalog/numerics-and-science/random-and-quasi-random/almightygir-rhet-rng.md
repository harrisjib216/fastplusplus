# rhet_RNG (xromu2jr, winner of the PRNG Battle Royale)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier D** (directional, no numbers) · Study only · `C++` · `no license` · 🔴 abandoned

> 2.8 KB public-domain header wrapping Overton's RomuDuoJr with seeding, range and float helpers; claimed fastest of 47 PRNGs for games, no published numbers.

| | |
|---|---|
| **Beats** | xoshiro256++ / xoshiro256\*\* / xoroshiro128 variants and PCG (pcg64) among the 47 PRNGs benchmarked; std::mt19937 is not among the generators listed in the README |
| **Claimed result** | No benchmark numbers appear in the repo. The README states that Romu2jr (RomuDuoJr with a NASAM-based seeding wrapper, xromu2jr.h) wins overall for game development, that the fixed-point (Lemire) range mapping beats biased modulo and unbiased masking, and that results are charts of relative speed per console (for example '2.2 implies the test was 2.2 faster than the slowest test that ran in this game console'). The charts themselves are images that are not in the repo. |
| **Workload** | Per the README: 47 non-cryptographic PRNGs on 9 game consoles (Nintendo Switch, PlayStation 4/4 Pro/5, Xbox One/One X/Series X, Stadia 1080p/4K), throughput and latency tests with at least 256 GB of random data per test, using three range-mapping methods (biased modulo, unbiased masking with discard, Lemire fixed-point fastrange) over ranges 2 to 2^16. |
| **Metric** | throughput |
| **Hardware** | Nine game consoles (CPU models unstated) |
| **Compiler and flags** | README: all tests built with 'top tier configuration presets' using the latest platform SDKs and Visual Studio 2019; exact flags unstated. |
| **Adoption** | 3 stars, 0 forks (re-host of the rhet.dev post by account Almightygir, three commits on 2023-06-25); the original post is cited by the ulfben/cpp_prngs README ('Winner of Rhet Butler's RNG Battle Royale (2020) and second fastest engine in the lineup') |
| **Last commit** | 2023-06-25 |
| **Links** | [repository](https://github.com/Almightygir/rhet_RNG) · [benchmark](https://github.com/Almightygir/rhet_RNG) |

## Verdict

The README describes relative-speed charts for latency and throughput tests (raw 64-bit, biased modulo, unbiased masking and Lemire fixed-point range mapping over ranges 2 to 2^16, at least 256 GB of data per test) across nine consoles built with Visual Studio 2019 and platform SDKs, normalised per console to the slowest test; no numbers, CPU models or flags are given, the charts are absent, and the code is private, so the claim that RomuDuoJr beats xoshiro256++/PCG64 and others rests on the author's word and his own weighting of speed and PractRand results.

## Use it when

- Game or interactive code that rolls many small ranges (loot tables, AI choices, particle jitter) and can accept the tiny bias of multiply-shift range mapping.
- You want a 16-byte generator you can vendor as one file with no dependencies and a public-domain wrapper.
- You seed many short-lived generators from a counter (entity IDs, frame numbers): the NASAM-based constructor mixes the seed so sequential uint32_t seeds are meant to give independent sequences, and it replaces discarding the low-quality first rolls typical of chaotic generators.
- Single-threaded hot loops where per-call latency matters more than vectorized throughput.

## Skip it when

- You need a guaranteed period: RomuDuoJr is chaotic, so some seed can fall into a short cycle; the author only brute-forced that 32-bit seeds have no cycle within the first 2^24 bytes (about 2 million 64-bit outputs) and 16-bit seeds within 2^36 bytes, and himself points people who cannot accept the risk to xoshiro256++ or sfc64.
- You need unbiased bounded integers: ru32(N)/ru64(N) are plain multiply-shift without the rejection step, so ranges that are not powers of two are slightly biased.
- You need std::-compatible engines, jump-ahead or independent streams: none are provided (no jump function, streams only by seeding).
- You need evidence: the repo has no numbers, the charts are not included, and the benchmark code was kept private for console NDA reasons, so the 'winner' claim cannot be reproduced.
- Any security-sensitive use; it is a non-cryptographic generator.

## How it is fast

RomuDuoJr keeps 128 bits of state and spends one 64-bit multiply, one subtract and one rotate per output, and it returns the previous x before the update, so the output has no dependency on the current step's multiply (the README notes Romu uses this 'return the previous roll' trick for latency). Bounded integers use Lemire's multiply-shift fastrange (high half of N times a random word) instead of modulo or rejection, which the README reports beat both alternatives in its charts, and floats are made by OR-ing random bits into the mantissa of 1.0 and subtracting 1 (Quilez's trick), avoiding an int-to-float conversion.

## Compared with alternatives

Pick ulfben/cpp_prngs instead if you want the same RomuDuoJr algorithm behind a std-compatible engine that works with std::shuffle and std::sample; pick xoshiro256++, sfc64 or PCG siblings when a guaranteed period matters, SHISHUA or the SIMD xoshiro siblings for bulk throughput, and lemire/FastShuffleExperiments for unbiased bounded integers. Choose this header only for its tiny public-domain wrapper and counter-friendly seeding.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none, but the header has no #include lines: include &lt;cstdint&gt; first (and the MSVC intrinsics header where __umulh is used) |
| **Minimum toolchain** | not documented; the code uses only C++11-era features, plus either unsigned __int128 (__SIZEOF_INT128__) or MSVC's __umulh for ru64(N) |
| **Platforms** | README tests covered Nintendo Switch, PlayStation 4/4 Pro/5, Xbox One/One X/Series X and Stadia built with the platform SDKs and Visual Studio 2019; any 64-bit target whose compiler offers __int128 or __umulh |
| **Thread safety** | not documented; a plain struct with mutable public state x, y and no locking, so use one instance per thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Seeds 0 and UINT64_MAX produce the same sequence: the constructor sets y = !s - s, which is 1 for both.
- as&lt;&gt;() type-puns through reinterpret_cast, which violates C++ strict aliasing; it usually works, but std::bit_cast or memcpy is the defined way if you modify the header.
- ri32(f, c) and similar return values in [f, c), and c - f is computed in the signed type, so very wide signed spans overflow.
- Compilers that have neither __int128 nor MSVC's __umulh cannot compile ru64(N).

## Known shortcomings

- Tier D: the repo holds only a README copy and the header; no numbers, no charts, and the benchmark code is private. It is a re-host by a non-author (3 stars, abandoned), cited by ulfben/cpp_prngs's README. Usability mixed.
- Seeds 0 and UINT64_MAX give the same sequence (the constructor sets y = !s - s); the cycle check covers only the first 2^24 bytes for 32-bit seeds; the range functions are biased (multiply-shift with no rejection); as&lt;&gt;() violates strict aliasing; the header has no #include lines; not a std::uniform_random_bit_generator. rhet.dev no longer resolves, so the original post is gone.

## Caveats and trade-offs

Tier D: the repo is an archive of a single 2.8 KB header (xromu2jr.h) plus a copy of the 2020 blog text; there are no benchmark numbers, charts or code in it, and the author says the benchmark code is kept private for console NDA reasons, so nothing is reproducible. The rhet.dev post and the Wayback copy were not fetched (blocked hosts). Licensing: the header says the wrapper is released into the public domain by its author, there is no LICENSE file in the repo, and the Romu algorithm by Mark Overton is not covered by that statement, so usability is marked mixed (no patent grant implied). The repo owner appears to be a different account from the original author (README says the header was created by RomuDuoJr at rhet.dev). Relative results are per console and mix PRNG quality and worst-case criteria chosen by the author; the 'winner' conclusion is his weighting.

RomuDuoJr has a 128-bit state and no guaranteed minimum period, so some seeds can end in short cycles; the README mitigates this with a NASAM-based initializer and brute-force checks (no cycles for 32-bit seeds within 2^24 bytes, 16-bit seeds within 2^36 bytes) but it is not a proof. Chaotic generators give low-quality first outputs unless seeded through a mixer. The README charts report some PractRand failures, and the author himself suggests xoshiro256++ or sfc64 when a guaranteed period matters. The header uses reinterpret_cast type punning in as&lt;&gt;() and either __uint128_t or __umulh for 64-bit ranges.

## Maintenance

Abandoned re-host (3 commits on 2023-06-25, 3 stars, no LICENSE file; the header states the wrapper is public domain, while the RomuDuoJr algorithm is Mark Overton's and its terms are not stated here); the original rhet.dev post no longer resolves (DNS failure in this session), so this repo is the reachable copy.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): reject; tier before verification D, tier now D.
- **Tier reason:** The repo holds only README.md (a copy of the 2020 rhet.dev post) and the 2.8 KB xromu2jr.h; the README describes relative-speed charts but contains no numbers, the chart images are not in the repo, and the author keeps the benchmark code private for console NDA reasons, so D. std::mt19937 is mentioned only as what games still use, not as a benchmarked generator.
- **Verifier notes:** Tier D, 3 stars, and the repo is a third-party re-host rather than the author's own; the original post has some citations (ulfben/cpp_prngs) but is not widely referenced, so rejected as not-notable-tier-d. If the keep-and-document rule applies, keep at D with usability mixed (header says the wrapper is public domain by NWDD; RomuDuoJr core by Mark Overton not covered) and maintenance abandoned (last commit 2023-06-25).
- **Fields the verifier corrected:** `stars_or_usage`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/Almightygir/rhet_RNG>
  - <https://github.com/Almightygir/rhet_RNG/commits/main>
  - <https://raw.githubusercontent.com/Almightygir/rhet_RNG/HEAD/README.md>
  - <https://raw.githubusercontent.com/Almightygir/rhet_RNG/HEAD/xromu2jr.h>
  - <https://github.com/ulfben/cpp_prngs>
- **Sources the enricher read:**
  - <https://github.com/Almightygir/rhet_RNG>
  - <https://raw.githubusercontent.com/Almightygir/rhet_RNG/HEAD/README.md>
  - <https://raw.githubusercontent.com/Almightygir/rhet_RNG/HEAD/xromu2jr.h>
  - <https://github.com/ulfben/cpp_prngs>
  - https://rhet.dev/wheel/rng-battle-royale-47-prngs-9-consoles/ (fetch failed: getaddrinfo ENOTFOUND rhet.dev; WebSearch snippet only)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/almightygir/rhet_rng`) · [data/wave8/enrich/raw/github_com_almightygir_rhet_rng.json](../../../data/wave8/enrich/raw/github_com_almightygir_rhet_rng.json) (enrichment confidence 0.75)

</details>
