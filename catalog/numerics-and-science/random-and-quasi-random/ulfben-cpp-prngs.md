# cpp_prngs (QuarkBurst64, RomuDuoJr, Konadare192 engines)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only constexpr C++17 small-state PRNG engines (RomuDuoJr, QuarkBurst64, Konadare192 and others) with a game-oriented Random&lt;E&gt; API, faster than std::mt19937.

| | |
|---|---|
| **Beats** | std::mt19937 (also std::minstd_rand, std::default_random_engine and C rand()) |
| **Claimed result** | README: 'All of the included engines substantially outperform the standard-library generators in this benchmark.' Engine-throughput chart (CPU time / no-op time, lower is faster; values read off the bar chart, approximate): std::mt19937 about 13,000; PCG32 about 5,000; Xoshiro256SS about 4,000; QuarkBurst64 and RomuDuoJr about 2,500 (roughly 5x faster than std::mt19937, derived from chart). |
| **Workload** | Quick Bench runs of raw engine next() throughput, bounded integers and bounded floats comparing the library's engines (PCG32, Xoshiro256SS, RomuDuoJr, QuarkBurst64, Konadare192, SmallFast\*) against standard-library generators. |
| **Metric** | throughput |
| **Adoption** | 1 star |
| **Last commit** | 2026-08-20 |
| **Links** | [repository](https://github.com/ulfben/cpp_prngs) · [benchmark](https://github.com/ulfben/cpp_prngs) |

## Verdict

The author's Quick Bench charts (August 2026) put raw next() at about 13,300 for std::mt19937 versus about 2,700 for RomuDuoJr and 2,600 for QuarkBurst64, in units of CPU time / no-op time, values read by eye. That is roughly 5x per call, but it compares 64-bit-output engines with the 32-bit-output std::mt19937. Compiler, flags, standard library and CPU are not stated (the Quick Bench links were unreachable). The harness is public (benchmarks/engine_comparison.cpp, Google Benchmark, 1024 values summed per iteration).

## Use it when

- Games and procedural generation that need fast, reproducible, cross-platform integer streams and replay checkpoints from a tiny state
- Many independent generator instances (per entity, per thread, per job) where std::mt19937's 2.5 KiB state is a cache cost
- Compile-time generation of tables or test data (engines and most of Random&lt;E&gt; are constexpr)
- Bounded integers and weighted picks in hot loops: Lemire's multiply-and-reject avoids most divisions (the README's bounded-integer chart compares it with std::uniform_int_distribution and rand() % n)
- 8/16-bit microcontrollers (AVR Arduino built as C++17) via the SmallFast8/16 and XorShift32Star8 engines

## Skip it when

- Security or anything adversarial: none of the engines is cryptographic, as the README states
- Scientific Monte Carlo that needs proven period, jump-ahead or guaranteed non-overlapping parallel streams: RomuDuoJr has no proven period (its seeding comment cites only empirical cycle checks), and child() explicitly 'does not promise independent or non-overlapping streams'
- Code that must reproduce std::mt19937 sequences or the exact output of std distributions
- Projects that need high-precision floats by default: normalized()/between() default to float with 23 random mantissa bits, and normal_approx() is an Irwin-Hall approximation clipped at about six standard deviations
- When you need audited statistical quality for QuarkBurst64: the repo has known-answer tests against an archived reference but no PractRand/TestU01 results, and the upstream eightomic/quarkburst repo returns 404

## How it is fast

The gain comes from replacing the 624-word Mersenne Twister with register-sized nonlinear generators. RomuDuoJr is one multiply plus a rotate-subtract on two 64-bit words. QuarkBurst64 is rotate/XOR/add with a Weyl counter and no multiply. Konadare192 is add/rotate with a Weyl increment. The wrapper uses Lemire's nearly divisionless multiply-and-reject for bounded integers (division-free when the bound is a compile-time constant). Floats are built by writing random bits into the mantissa field (the 'IQ float hack') instead of dividing.

## Compared with alternatives

Pick cpp_prngs over libchaos or the bare Romu entry when you want ready-to-copy constexpr C++17 engines plus a convenience layer (bounded ints, weighted picks, snapshots) with portable, deterministic output, including on AVR. For SIMD bulk throughput (simdrng, SHISHUA) or scientific-grade streams with jump-ahead (Randen, xoshiro reference code, OpenRAND), look at those entries instead.

## Integration

| | |
|---|---|
| **Form** | header-only (copy include/ or link the CMake INTERFACE target cpp_prngs::cpp_prngs) |
| **Dependencies** | none (GoogleTest is fetched only for the test build) |
| **Minimum toolchain** | C++17 (CMake 3.21+ for the provided target); C++20 adds constexpr std::bit_cast floats and the rnd::RandomBitEngine concept; AVR needs -std=gnu++17 (CI uses Arduino AVR core 1.8.8) |
| **Platforms** | any C++17 target (desktop, MSVC project included, AVR Arduino validated in CI) |
| **Thread safety** | not documented; engines and Random&lt;E&gt; are plain value types with no global state, so use one instance per thread |
| **Drop-in for the baseline** | partial: the engines satisfy UniformRandomBitGenerator and can replace std::mt19937 as the engine for std::shuffle or std distributions, but the sequences differ, seeding takes a single uint64_t rather than a seed_seq, and the Random&lt;E&gt; API is its own interface |

## Gotchas

- Default construction uses a fixed seed, so Random&lt;E&gt;() gives the same sequence every run. Seeding helpers live in a separate gist (seeding.hpp), not in the repo.
- Floating between(lo, hi) is computed as lo + (hi - lo) \* normalized(), so rounding can return hi for some ranges despite the documented [lo, hi). In C++17 the float path is constexpr arithmetic unless RND_FAST_FLOAT is defined.
- from_state() bypasses seeding. All-zero states are invalid for most engines (PCG32's inc must be odd), and this is checked only by assert in debug builds.
- Third-party engine headers keep their own licenses (PCG32 and Konadare192 are Apache-2.0, QuarkBurst's upstream is BSD-3-Clause), so check the per-file headers when vendoring rather than assuming MIT throughout.

## Known shortcomings

- QuarkBurst64 has no PractRand/TestU01 evidence and upstream eightomic/quarkburst is 404 (KAT checked only against an archived reference). RomuDuoJr period unproven. float between(lo,hi) can round to hi; child() streams are not independent. Repo mostly curates third-party engines.

## Caveats and trade-offs

Numbers exist only as Quick Bench bar charts (ratio CPU time / no-op time) with no hardware, compiler, flags or standard library stated; values were read by eye from the PNGs and match the record (raw next(): std::mt19937 about 13,300 vs RomuDuoJr about 2,700, QuarkBurst64 about 2,600). The raw-engine chart compares 64-bit-output engines against the 32-bit-output std::mt19937 per call (std::mt19937_64 appears only in the bounded-integer chart, about 15,800). The harness sums outputs and calls DoNotOptimize only once after the loop. The fastest engines are ports of third-party generators (Romu, quarkburst/GhostScramble, konadare192px++, xoshiro256\*\*, PCG32), so the entry mainly curates and packages third-party winners; third-party engine headers keep their own licenses (public domain, Apache-2.0, MIT). The upstream eightomic/quarkburst page returned 404 in the search run, and the RNG Battle Royale (2020) page was not opened. The C rand() % bound baseline is biased and only a performance reference, as the benchmarks README says. 1 star, single author.

Header-only C++17 with constexpr engines; 4-32 bytes of state; deterministic across platforms; engines are ports of known algorithms (Bob Jenkins SmallFast, Romu, Pelle Evensen's konadare192px++, Eightomic quarkburst), wrapped in a game-oriented Random&lt;E&gt; API; the 8/16-bit engines target microcontrollers.

## Maintenance

Actively maintained by a single author (232 commits, last 2026-08-20, 1 star, CI on desktop and AVR). MIT for the wrappers, with third-party engines under their original permissive licenses; small enough to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party Quick Bench bar charts in the README (benchmarks/results/\*.png) compare the engines against std::mt19937, std::default_random_engine, std::minstd_rand, rand() and std::uniform_int_distribution; benchmark code is public (benchmarks/engine_comparison.cpp, random_bounded_integer.cpp, random_bounded_float.cpp) but compiler, flags, standard library and CPU are not stated (the Quick Bench links are not reachable here), so C.
- **Verifier notes:** Chart values and README text match the record. Metadata confirmed on github.com: MIT, 1 star, 232 commits, last commit 2026-08-20 (active). quick-bench.com is egress-blocked, so compiler settings stay unknown.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/ulfben/cpp_prngs>
  - <https://github.com/ulfben/cpp_prngs/commits/main>
  - <https://github.com/ulfben/cpp_prngs/tree/main/benchmarks>
  - <https://raw.githubusercontent.com/ulfben/cpp_prngs/HEAD/README.md>
  - <https://raw.githubusercontent.com/ulfben/cpp_prngs/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/ulfben/cpp_prngs/HEAD/benchmarks/engine_comparison.cpp>
  - <https://raw.githubusercontent.com/ulfben/cpp_prngs/HEAD/benchmarks/results/engine-comparison-2026-08.png>
  - <https://raw.githubusercontent.com/ulfben/cpp_prngs/HEAD/benchmarks/results/random-bounded-integer-2026-08.png>
  - <https://raw.githubusercontent.com/ulfben/cpp_prngs/HEAD/benchmarks/results/random-bounded-float-2026-08.png>
- **Sources the enricher read:**
  - <https://github.com/ulfben/cpp_prngs>
  - <https://github.com/ulfben/cpp_prngs/issues?q=is%3Aissue>
  - <https://github.com/ulfben/cpp_prngs/tree/main/tests>
  - <https://raw.githubusercontent.com/ulfben/cpp_prngs/HEAD/README.md>
  - <https://raw.githubusercontent.com/ulfben/cpp_prngs/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ulfben/cpp_prngs/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/ulfben/cpp_prngs/HEAD/include/rnd/random.hpp>
  - <https://raw.githubusercontent.com/ulfben/cpp_prngs/HEAD/include/rnd/concepts.hpp>
  - <https://raw.githubusercontent.com/ulfben/cpp_prngs/HEAD/include/rnd/engines/romuduojr.hpp>
  - <https://raw.githubusercontent.com/ulfben/cpp_prngs/HEAD/include/rnd/engines/quarkburst64.hpp>
  - <https://raw.githubusercontent.com/ulfben/cpp_prngs/HEAD/include/rnd/engines/konadare192.hpp>
  - <https://raw.githubusercontent.com/ulfben/cpp_prngs/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/ulfben/cpp_prngs/HEAD/benchmarks/engine_comparison.cpp>
  - <https://raw.githubusercontent.com/ulfben/cpp_prngs/HEAD/benchmarks/random_bounded_integer.cpp>
  - <https://raw.githubusercontent.com/ulfben/cpp_prngs/HEAD/benchmarks/random_bounded_float.cpp>
  - <https://raw.githubusercontent.com/ulfben/cpp_prngs/HEAD/tests/engine_reference_validation.hpp>
  - https://github.com/eightomic/quarkburst (404)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/ulfben/cpp_prngs`) · [data/wave8/enrich/raw/github_com_ulfben_cpp_prngs.json](../../../data/wave8/enrich/raw/github_com_ulfben_cpp_prngs.json) (enrichment confidence 0.75)

</details>
