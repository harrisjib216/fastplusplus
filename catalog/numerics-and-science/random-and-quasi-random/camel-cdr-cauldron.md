# cauldron random.h (ziggurat normal distribution)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟡 stale

> Single-header C (C++-compatible) RNG library whose ziggurat standard-normal sampler measured 2.2x (float) and 4.2x (double) faster than std::normal_distribution.

| | |
|---|---|
| **Beats** | std::normal_distribution (driven by std::minstd_rand in the benchmark's cpp11random entry) |
| **Claimed result** | Issue #3 in miloyip/normaldist-benchmark (author camel-cdr), ns per sample, float: ziggurat_new 4.018, cpp11random (std::normal_distribution) 8.852, existing ziggurat 7.289, marsagliapolar 6.133, inverse 6.017, boxmuller 7.484; double: ziggurat_new 4.081, cpp11random 17.009, existing ziggurat 7.817, marsagliapolar 8.711, inverse 7.222, boxmuller 16.546. Derived from page data: 2.2x faster than std::normal_distribution for float and 4.2x for double; 1.8x and 1.9x faster than the benchmark's existing ziggurat. The issue says its implementation is 60% faster than the existing ziggurat. |
| **Workload** | Generating 1,000,000 standard-normal float or double samples per trial (minimum over 10 trials) in miloyip/normaldist-benchmark, camel-cdr's 128-block ziggurat with a single condensed lookup table and an LCG as the uniform source versus the benchmark's other implementations. |
| **Metric** | throughput |
| **Adoption** | 143 stars |
| **Last commit** | 2025-02-01 |
| **Links** | [repository](https://github.com/camel-cdr/cauldron) · [benchmark](https://github.com/miloyip/normaldist-benchmark/issues/3) |

## Verdict

In camel-cdr's issue #3 on miloyip/normaldist-benchmark (2020-12-19; 1M samples, minimum of 10 trials; CPU and compiler not stated), a template ziggurat that is the precursor of random.h's code took 4.018 ns per float and 4.081 ns per double, against 8.852 and 17.009 ns for std::normal_distribution driven by std::minstd_rand and 7.289 and 7.817 ns for the benchmark's existing ziggurat. That code fed the ziggurat from the Numerical Recipes 32-bit LCG, taking the box index from its low 7 bits, and built the double version's 64-bit draw from two identically seeded copies of that LCG, so both halves are equal; no output-quality result was reported, and the repo's own tools/random/bench.c times dist_normal(f)_zig but publishes no numbers.

## Use it when

- C or C++ simulation and Monte Carlo code that draws many scalar standard normals and where std::normal_distribution shows up in profiles (about 9-17 ns per sample in the cited run versus about 4 ns).
- Projects that want a vendorable MIT single header with no dependency beyond libm that builds as C89 and as C++ (both are exercised by the repo's test script).
- Code that already controls its own fast PRNG (Romu, PCG, xoshiro\*\*) and wants to plug it in per thread through the function-pointer interface.
- Float sampling where a small (516-byte, 129 floats) read-only table that stays in L1 is acceptable.

## Skip it when

- Bulk or SIMD fills of large arrays: the routine is scalar, one sample per call; vectorized siblings such as EigenRand target that case.
- Code that needs the &lt;random&gt; distribution-object interface (URBG, param_type, mean/stddev) or other distributions such as gamma or Student t.
- Results that must be bit-identical to std::normal_distribution or another library: the sequence differs.
- Pairing it with a generator whose low bits are weak (the + and \* scramblers, plain power-of-two LCGs): the sign and box index come from the lowest bits of each draw, while random.h's own notes say the xoshiro/xoroshiro + variants' lower bits fail linear tests yet recommend those variants for floating point.
- Decisions that need hard numbers: the only published comparison is a first-party 2020 run of precursor code with no CPU, compiler or flags; re-measure on your target.

## How it is fast

It is the Marsaglia-Tsang ziggurat in Doornik's formulation, but with a single table of box x-coordinates (129 floats for the default 128 boxes, 257 doubles for the default 256); the source comment says dropping the second bound table halves memory and allows bigger tables. Each sample usually costs one RNG call, one multiply and one compare, because one 32- or 64-bit draw is split into the sign (bit 0), the box index (the next 7 or 8 bits) and the uniform (the top 24 or 53 bits). Only rejected draws reach the wedge test (two expf/exp calls) or Marsaglia's 1964 log-based tail method.

## Compared with alternatives

Pick cauldron when you want plain C (even C89) and a scalar standard-normal function driven by your own PRNG; its precursor ran about 1.8x faster than the existing ziggurat in miloyip's normaldist-benchmark. Pick EigenRand for vectorized bulk fills on Eigen arrays, Zest for a C++ distribution-object API covering gamma, Student t and other ziggurat-able distributions, and cxx-ziggurat or zigg if you prefer a C++ class or R integration.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | libm (logf/expf/sqrtf and the double versions); the TRNG section uses OS APIs (getrandom, arc4random, RtlGenRandom or /dev/urandom), not needed by the ziggurat |
| **Minimum toolchain** | C89 (test script builds with -std=c89 -Dinline=) or C++ via g++ -xc++; requires uint32_t/uint64_t and float/double formats with at least 7 spare bits beyond the mantissa (checked by #error) |
| **Platforms** | any (portable C, no intrinsics in the ziggurat path); the test script also runs a big-endian MIPS build under qemu when that toolchain is installed |
| **Thread safety** | not documented; the table is read-only after init and taken as a const pointer, and RNG state is caller-owned, so one shared table plus one RNG state per thread works by construction |
| **Drop-in for the baseline** | no |

## Gotchas

- You must call dist_normalf_zig_init / dist_normal_zig_init before sampling. Table size is a compile-time macro: DIST_NORMALF_ZIG_COUNT defaults to 128 and cannot exceed 128; DIST_NORMAL_ZIG_COUNT defaults to 256 (power of two, at most 1024). The matching _R and _AREA constants are only defined when you leave COUNT at its default, so a custom COUNT needs its own constants from tools/random/ziggurat-constants.c.
- Because the sign and box index use the low bits of each draw, a generator with poor low bits biases the output; a related issue (#2, closed 2024-11-22) showed dist_uniform\*_dense returning only 1.0 with the odd-only randu LCG.
- The repo's CI runs test/random/dist_normal.c (Jochen Voss's GPL-2 testgauss checks of mean and tail probabilities, with Romu generators) under gcc, sanitizers and g++, but test.sh ends with 'exit 0' and has no 'set -e', so a failing test would not fail CI. The GPL applies to that test file only; random.h itself is MIT.
- dist_normalf_fast is an approximation (sum of popcounts plus a linear nudge), not an exact normal sampler; do not confuse it with the ziggurat functions.

## Known shortcomings

- Tier C: the numbers come from the author's own issue #3 table; the baseline 'cpp11random' is std::normal_distribution driven by std::minstd_rand, and clt4 ties with it (4.064 vs 4.088 ns). The current random.h double default is 256 blocks, not the configuration timed in the issue.
- The issue #3 benchmark took the box index from the low 7 bits of a 32-bit NR LCG (period 128), and the double draw concatenates two identically seeded LCGs so both halves are equal; no statistical quality result is reported. Sign and box index come from low bits although random.h recommends the +/\* variants (weak low bits) for floats. test.sh ends with 'exit 0', so CI never fails. A custom ZIG_COUNT needs your own _R/_AREA tables.

## Caveats and trade-offs

First-party claim in a GitHub issue comment with no CPU model, compiler or flags, so tier C. The std::normal_distribution baseline is driven by std::minstd_rand, not std::mt19937 (confirmed in the benchmark's src/cpp11random.cpp), and the standard library implementation is not stated; the ziggurat uses a cheap LCG, so the gap partly reflects RNG cost (the benchmark's null entry is 1.049 ns float, 1.149 ns double). In the same tables the benchmark's clt4 entry (sum of 4 uniforms, an approximation) runs at 4.064 ns float and 4.088 ns double, essentially tied with ziggurat_new. The code in the issue is the author's proposed template, not literally the current cauldron function: random.h's dist_normal(f)_zig is described as based on Doornik's implementation with a single lookup table, and in the current random.h the float version defaults to 128 blocks while the double version defaults to 256 blocks (DIST_NORMAL_ZIG_COUNT), so the link is by author and design, not identical code. The double version builds a 64-bit value from two 32-bit LCG outputs per the issue. The cauldron repo has tools/random/bench.c (referenced from random.h) but publishes no results. Issue dated 2020-12-19; last repo commit 2025-02-01. The lead's '4.0 ns versus 7.3-7.8 ns' compares against the benchmark's existing ziggurat, while the std::normal_distribution figures are 8.852 ns and 17.009 ns.

Single-file C header (usable from C++) with the ziggurat entry points dist_normalf_zig and dist_normal_zig that need an init call and a lookup table (128 entries, float or double) and a caller-supplied RNG function; the slow path uses log and exp. The library also offers a lower-accuracy dist_normalf_fast that was not part of this evidence. Output quality of the issue's code was not verified here (the benchmark harness has a correctness check, but the issue does not report its result).

## Maintenance

Stale (random.h last changed 2025-02-01, 'small changes'; 0 open issues, 143 stars) but MIT-licensed, self-contained and easy to vendor; the ziggurat section can be copied on its own per the header's design notes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** Issue #3 (camel-cdr, 2020-12-19) posts ns-per-sample tables for float and double that include cpp11random (std::normal_distribution with std::minstd_rand, per the benchmark's src/cpp11random.cpp and readme); every number in claimed_speedup matches. First-party numbers with no CPU model, compiler or flags, so C.
- **Verifier notes:** All numbers verified on the issue page; license MIT, 143 stars, last commit 2025-02-01 ('small changes') confirmed, so stale is right. Only the caveats were extended (clt4 tie, 256-block double default in current random.h).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/miloyip/normaldist-benchmark/issues/3>
  - <https://github.com/camel-cdr/cauldron>
  - <https://github.com/camel-cdr/cauldron/commits/main>
  - <https://raw.githubusercontent.com/camel-cdr/cauldron/HEAD/cauldron/random.h>
  - <https://raw.githubusercontent.com/miloyip/normaldist-benchmark/HEAD/src/cpp11random.cpp>
  - <https://raw.githubusercontent.com/miloyip/normaldist-benchmark/HEAD/readme.md>
- **Sources the enricher read:**
  - <https://github.com/camel-cdr/cauldron>
  - <https://github.com/camel-cdr/cauldron/issues?q=is%3Aissue>
  - <https://github.com/camel-cdr/cauldron/issues/2>
  - <https://github.com/camel-cdr/cauldron/commits/main/cauldron/random.h>
  - <https://github.com/camel-cdr/cauldron/tree/main/.github/workflows>
  - <https://raw.githubusercontent.com/camel-cdr/cauldron/HEAD/README.md>
  - <https://raw.githubusercontent.com/camel-cdr/cauldron/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/camel-cdr/cauldron/HEAD/cauldron/random.h>
  - <https://raw.githubusercontent.com/camel-cdr/cauldron/HEAD/tools/random/bench.c>
  - <https://raw.githubusercontent.com/camel-cdr/cauldron/HEAD/Makefile>
  - <https://raw.githubusercontent.com/camel-cdr/cauldron/HEAD/test/random/dist_normal.c>
  - <https://raw.githubusercontent.com/camel-cdr/cauldron/HEAD/test/Makefile>
  - <https://raw.githubusercontent.com/camel-cdr/cauldron/HEAD/test/test.sh>
  - <https://raw.githubusercontent.com/camel-cdr/cauldron/HEAD/.github/workflows/tests.yml>
  - <https://github.com/miloyip/normaldist-benchmark/issues/3>
  - <https://raw.githubusercontent.com/miloyip/normaldist-benchmark/HEAD/src/lcg.h>
  - <https://raw.githubusercontent.com/miloyip/normaldist-benchmark/HEAD/src/cpp11random.cpp>
  - <https://github.com/cd-mcfarland/fast_prng>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/camel-cdr/cauldron`) · [data/wave8/enrich/raw/github_com_camel_cdr_cauldron.json](../../../data/wave8/enrich/raw/github_com_camel_cdr_cauldron.json) (enrichment confidence 0.75)

</details>
