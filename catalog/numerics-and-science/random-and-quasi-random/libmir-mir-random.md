# mir-random (libmir/mir-random, D random number generators)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `D` · `BSL-1.0` · 🟢 active

> D random library: Lemire bounded integers, a faster Mersenne Twister (since merged into Phobos), xoshiro/PCG engines, ndslice distributions.

| | |
|---|---|
| **Beats** | D Phobos std.random (Mt19937 generation and initialization, modulo-reduction bounded integers) |
| **Claimed result** | README: Mt19937 +100% initialization and +54% generation versus Phobos (merged to Phobos); randIndex with Lemire's method on x86-64 with LDC 1.6.0: 1.40x uint Mt19937_64, 1.73x uint Xoroshiro128Plus, 2.36x ulong Mt19937_64, 4.25x ulong Xoroshiro128Plus. bench/Mt19937_bench.d comment: mir 32-bit Mt19937 6.80851 Gb/s vs Phobos 32-bit 4.41989 Gb/s (1.54x), mir 64-bit Mt19937 12.5984 Gb/s (2.85x vs Phobos 32-bit; Phobos 64-bit noted as having wrong initialization and tempering). bench/randindex_bench.d sample results on i7-7920HQ: ulong Xoroshiro128Plus 4.40044 vs 1.0195 x 10^8 calls/s (4.32x, derived from page data), ulong Mt19937_64 1.87091 vs 0.796416 (2.35x, derived from page data). No benchmark found for the +100% initialization figure. |
| **Workload** | bench/Mt19937_bench.d: 100 million Mt19937 outputs summed in a loop, Gb/s, mir Mt19937_32/Mt19937_64 vs Phobos std.random.Mt19937 (32-bit). bench/randindex_bench.d: 800 million bounded-integer calls with moduli 6..105 per engine, modulo-with-rejection (randIndexV1) vs Lemire multiply-shift (randIndexV2), both implemented in the bench file. README 'Comparison with Phobos' bullets summarize both. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-7920HQ @ 3.10GHz for the randIndex sample results in bench/randindex_bench.d; not stated for bench/Mt19937_bench.d |
| **Compiler and flags** | LDC via ldmd2, dub --build=release-nobounds (bench file shebangs); README names LDC 1.6.0 for the randIndex figures |
| **Adoption** | 32 stars; dub package |
| **Last commit** | 2026-06-10 |
| **Links** | [repository](https://github.com/libmir/mir-random) · [benchmark](https://github.com/libmir/mir-random/tree/master/bench) |

## Verdict

bench/Mt19937_bench.d (100 million outputs, LDC via ldmd2 with dub release-nobounds, CPU not stated) shows mir's 32-bit Mt19937 at 6.81 Gb/s vs the Phobos Mt19937 of that time at 4.42 Gb/s (1.54x), with matching checksums. Phobos has since adopted this implementation (D 2.074.0 changelog per a search snippet; dlang.org is blocked here, but current Phobos std/random.d credits it). bench/randindex_bench.d on an Intel Core i7-7920HQ compares Lemire multiply-shift with modulo-with-rejection, both written in the bench file, over 800 million calls with moduli 6 to 105: ulong from Xoroshiro128Plus 4.40 vs 1.02 x10^8 calls/s, ulong from Mt19937_64 1.87 vs 0.80 x10^8. Current Phobos uniform and _uniformIndex still use modulo-with-rejection, so that gap should still hold against Phobos, but Phobos itself was not timed.

## Use it when

- D programs doing many bounded integer draws (shuffles, sampling, random indexing), where randIndex measured 1.4x to 4.3x more calls per second than modulo reduction on the same engine.
- D code that needs a faster default generator than Phobos's 32-bit Mt19937: switch to Xoroshiro128Plus or Xoshiro256StarStar, which the bench runs much faster than Mt19937_64 under randIndex.
- Filling ndslice arrays with normal, exponential, gamma or multivariate-normal variates for simulation or Monte Carlo in D.
- -betterC or @nogc nothrow code that cannot use DRuntime; the engines and rand functions are @nogc and do not need the GC.

## Skip it when

- C or C++ projects: generators are D templates with no C ABI; only the entropy functions (mir_random_genRandomNonBlocking and mir_random_genRandomBlocking) have C names. In C++ use the catalogued C++ entries instead.
- Mersenne Twister throughput alone: Phobos's MersenneTwisterEngine has used this implementation since it was merged (current std/random.d credits Ilya Yaroshenko and mir-random), so the +54% generation figure no longer applies to current Phobos.
- Cryptography, tokens or secrets: the README says not to use it for that.
- Projects that need an active upstream: only 2 commits since January 2022 (December 2024 and June 2026, both compiler fixes), and issue #133 (wrong signs in flex transformation unit-test expectations) has been open since 2021.
- Code built on Phobos's range-based RNG API: engines use opCall and forbid default construction and copying, so porting needs PhobosRandom or rewrites.

## How it is fast

randIndex replaces modulo-with-rejection by Daniel Lemire's multiply-shift reduction (a double-width multiply; the rejection threshold, and its division, is computed only when the low half falls below m), with a branch hint on the rare path. The Mersenne Twister updates one state word per call over a reversed state array and interleaves tempering of the previous output with the state update so values stay in registers, instead of regenerating all 624 words in a block. Floating-point rand!T fills every mantissa bit (saturated values; README: rand!real can produce more than 2^78 distinct values).

## Compared with alternatives

Pick mir-random only for D code; for C++ the same ideas are catalogued directly: FastShuffleExperiments for Lemire's nearly divisionless bounded integers, cslarsen/mersenne-twister or VMT19937 for a faster Mersenne Twister, and dqrng or simdrng for xoshiro/PCG engines with fast distributions.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | mir-core (&gt;=0.2.0 &lt;2.0.0); mir-linux-kernel on Linux; advapi32 on Windows; mir-algorithm optional ('default' configuration) or required ('extended') for ndslice and distribution features; the 'minimal' configuration omits it |
| **Minimum toolchain** | not documented; code branches for LDC, GDC and DMD, and README figures used LDC 1.6.0; last commit (2026-06-10) adapted to recent compilers |
| **Platforms** | Linux, Windows, macOS/iOS and the BSDs (seeding via getrandom, Windows APIs or arc4random); any architecture D compilers target |
| **Thread safety** | Engines are plain structs with no locking; rne / threadLocal!Engine give one auto-seeded instance per thread (needs TLS, so not available under -betterC), and the docs warn not to share threadLocalPtr pointers between threads. |
| **Drop-in for the baseline** | partial: Mt19937 output matches Phobos for the same seed (the bench prints identical checksums), but the API differs (opCall instead of front/popFront, randIndex instead of uniform); PhobosRandom!Engine adapts an engine to the Phobos interface. |

## Gotchas

- rand!float / rand!double / rand!real return values in (-1, 1), not [0, 1); apply fabs or use a uniform variable for [0, 1).
- The default Random is Mt19937_64 on 64-bit targets (Mt19937 on 32-bit), which is slower than the bundled xoshiro/xoroshiro engines; choose an engine explicitly when speed matters.
- Engines @disable default construction and postblit, so they must be passed by ref or pointer; seeding Mt19937 from a 64-bit unpredictableSeed requires masking to Mt19937.max (shown in the docs).
- Xoroshiro128Plus (xoroshiro128+) has weak low bits that fail binary-rank tests; the module docs recommend Xoshiro256StarStar as the all-purpose generator.

## Known shortcomings

- Tier C: bench/Mt19937_bench.d gives mir 6.81 vs Phobos 4.42 Gb/s (1.54x) with no CPU listed; randindex_bench.d (i7-7920HQ) compares modulo vs Lemire within the same file, not Phobos. No benchmark backs the +100% init claim. No root LICENSE file; BSL-1.0 per dub.sdl and file headers.
- The Mt19937 +54%/+100% claim no longer applies: current Phobos std/random.d credits Yaroshenko/mir-random for its Mersenne Twister (D 2.074.0 changelog, snippet only). randIndex 1.4-4.3x is measured against a modulo version written in the bench file, not Phobos, though Phobos uniform still uses modulo so that gap probably holds. 'Active' overstates it (2 compiler-fix commits since 2022-01); issue #133 (sign errors in flex unit-test expectations) open since 2021; rand!float returns (-1,1), not [0,1); the default Random is Mt19937_64.

## Caveats and trade-offs

D only, not callable from C++ without bindings. Benchmarks date from the LDC 1.6.0 era (about 2017-2018). The Mt19937 generation and initialization improvements were merged back into Phobos, so the gap against current Phobos has probably closed; the Mt19937 bench states no CPU or LDC version. The randIndex 1.40x-4.25x figures compare Lemire's reduction against a modulo reduction written in the same bench file on the same engine, not mir-random against Phobos's uniform. No benchmark source found for the +100% initialization claim. No root LICENSE file (LICENSE returns 404); license comes from dub.sdl ('BSL-1.0 (default), Apache License, Version 2.0 for PCG') and per-file Boost License 1.0 headers.

D language with a Better C mode and no DRuntime dependency; provides Mt19937, PCG (Apache-2.0), SplitMix, XorshiftStar, Xoroshiro128Plus and Xoshiro256\*\* engines plus ndslice-based random arrays and distributions; the new API uses opCall rather than a range interface. Not for cryptography.

## Maintenance

Maintenance-only rather than active (2 commits since January 2022, both compiler fixes; 32 stars; dub package), but Boost-licensed (Apache-2.0 for PCG) and usable from D; out of language scope for C++.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README bullets match the record, and public bench code exists: bench/Mt19937_bench.d times mir Mt19937 against Phobos std.random.Mt19937 (6.80851 vs 4.41989 Gb/s, built with dub --build=release-nobounds --compiler=ldmd2) but states no CPU; bench/randindex_bench.d states an Intel Core i7-7920HQ but compares two in-file reduction methods (modulo vs Lemire), not Phobos. Neither benchmark has code, compiler, flags and CPU against the named baseline together, so C.
- **Verifier notes:** Stars 32, last commit 2026-06-10 (fix ctfe for Random), active; numbers verified against README and bench files. Bench comment ratios differ slightly from README (4.32x vs 4.25x), likely separate runs. Out-of-language (D) entry for the random category.
- **Fields the verifier corrected:** `benchmark_url`, `compiler_and_flags`, `hardware`, `workload`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/libmir/mir-random>
  - <https://github.com/libmir/mir-random/commits>
  - <https://github.com/libmir/mir-random/tree/master>
  - <https://github.com/libmir/mir-random/tree/master/bench>
  - <https://raw.githubusercontent.com/libmir/mir-random/HEAD/README.md>
  - <https://raw.githubusercontent.com/libmir/mir-random/HEAD/dub.sdl>
  - <https://raw.githubusercontent.com/libmir/mir-random/HEAD/bench/Mt19937_bench.d>
  - <https://raw.githubusercontent.com/libmir/mir-random/HEAD/bench/randindex_bench.d>
  - <https://raw.githubusercontent.com/libmir/mir-random/HEAD/source/mir/random/package.d>
- **Sources the enricher read:**
  - <https://github.com/libmir/mir-random>
  - <https://github.com/libmir/mir-random/commits>
  - <https://github.com/libmir/mir-random/issues?q=is%3Aissue>
  - <https://github.com/libmir/mir-random/issues/133>
  - <https://github.com/libmir/mir-random/tree/master/source/mir/random>
  - <https://github.com/libmir/mir-random/tree/master/source/mir/random/engine>
  - <https://raw.githubusercontent.com/libmir/mir-random/HEAD/README.md>
  - <https://raw.githubusercontent.com/libmir/mir-random/HEAD/dub.sdl>
  - <https://raw.githubusercontent.com/libmir/mir-random/HEAD/bench/Mt19937_bench.d>
  - <https://raw.githubusercontent.com/libmir/mir-random/HEAD/bench/randindex_bench.d>
  - <https://raw.githubusercontent.com/libmir/mir-random/HEAD/source/mir/random/package.d>
  - <https://raw.githubusercontent.com/libmir/mir-random/HEAD/source/mir/random/engine/package.d>
  - <https://raw.githubusercontent.com/libmir/mir-random/HEAD/source/mir/random/engine/mersenne_twister.d>
  - <https://raw.githubusercontent.com/libmir/mir-random/HEAD/source/mir/random/engine/xoshiro.d>
  - <https://raw.githubusercontent.com/dlang/phobos/master/std/random.d>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/libmir/mir-random`) · [data/wave8/enrich/raw/github_com_libmir_mir_random.json](../../../data/wave8/enrich/raw/github_com_libmir_mir_random.json) (enrichment confidence 0.75)

</details>
