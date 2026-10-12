# libchaos (KISS, Xoroshiro128Plus, Xorshf96 and other PRNGs)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-2-Clause` · 🔴 abandoned

> Abandoned C++11 grab-bag of small PRNGs (xorshift128+, xorshift1024\*, KISS, xorshf96) about 2.6x faster per call than std::mt19937.

| | |
|---|---|
| **Beats** | std::mt19937 and std::mt19937_64 (also std::minstd_rand, ranlux24/48, knuth_b) |
| **Claimed result** | README: CHAOS_PRNG_XOROSHIRO128PLUS 178.426M items/s, CHAOS_PRNG_XORSHF96 185.148M, CHAOS_PRNG_ABYSSINIAN 165.754M, CHAOS_PRNG_KISS 99.9175M vs STL mt19937 68.239M and mt19937_64 60.0674M items/s (Xoroshiro128Plus about 2.6x mt19937, derived from page data). |
| **Workload** | Google Benchmark items/s for 'Next' calls of libchaos PRNGs vs STL engines, run on Travis CI. |
| **Metric** | throughput |
| **Hardware** | Travis CI (CPU not stated) |
| **Compiler and flags** | g++-4.8 on Travis CI (.travis.yml; clang lines commented out) with -std=c++11 -O3 -flto -march=native -mtune=native, Release build (CMakeLists.txt). The flags come from the build files, not from the text next to the numbers. |
| **Adoption** | 1.6k stars |
| **Last commit** | 2017-01-01 |
| **Links** | [repository](https://github.com/maciejczyzewski/libchaos) · [benchmark](https://github.com/maciejczyzewski/libchaos) |

## Verdict

README Google Benchmark rows from a Travis CI VM (CPU not stated; g++-4.8, -O3 -flto -march=native per the build files) report the '128+' class at 178.4M items/s and xorshf96 at 185.1M, against std::mt19937 at 68.2M and mt19937_64 at 60.1M items/s (about 2.6x, derived from page data). The libchaos and STL rows are shown separately; the harness counts one item per four discarded next() calls and uses no DoNotOptimize, so the absolute rates are understated 4x and output tempering may be optimized away for every engine.

## Use it when

- Reading or reproducing the chaos-machine research (XORRING32/64 machines and the ePrint paper), which is the library's actual focus.
- Needing a copy of Marsaglia's KISS or xorshf96 with the exact sequences pinned by the repo's signature tests.
- Quick non-critical C++11 simulations or games where a small generator about 2-3x faster per call than std::mt19937 is enough and BSD-2-Clause is acceptable.
- Otherwise, take the reference xoshiro/PCG code or a maintained sibling instead; nothing here is faster than those originals.

## Skip it when

- When you need xoroshiro128+ or xoroshiro1024\*: the classes with those names implement the older xorshift128+ and xorshift1024\* algorithms, so the output and quality do not match the names.
- With &lt;random&gt; distributions or any template that expects a UniformRandomBitGenerator: chaos::prng&lt;&gt; has min(), max() and operator() but no result_type typedef, so std::uniform_int_distribution and similar should not compile against it (code reading, not compiled).
- Anything security-related: the README offers chaos::password&lt;CHAOS_MACHINE_XORRING64,...&gt; for password hashing and calls the machines suitable for cryptographic primitives, but the repo cites no third-party cryptanalysis, only the author's ePrint paper.
- MSVC or portable binaries: CMake stops on any compiler other than GCC or Clang, Clang is forced to -stdlib=libc++, and the installed library is built with -march=native.
- Production use in general: the code was last committed on 2017-01-01, the CHANGELOG still reads 'Release 0.0.1 (in development)', the README warns 'early stage of development', and a 2017 link-error issue (#11) is unanswered.

## How it is fast

There is no special technique: the speedup is what any small-state xorshift- or multiply-with-carry-family generator gets over MT19937's 624-word state and periodic twist. next() is an inline handful of shifts, xors and adds on 2-16 words of state (xorshift128+, xorshift1024\* with a final multiply, Marsaglia's xorshf96 and KISS, and an MWC pair called 'abyssinian'). The benchmark builds everything with -O3 -flto -march=native.

## Compared with alternatives

Rarely. For a fast modern engine, cpp_prngs (RomuDuoJr, QuarkBurst64) is benchmarked directly against std::mt19937 and the other std engines, and testingRNG benchmarks the original lehmer64, xoroshiro128+ and PCG code. Pick libchaos only for its chaos-machine experiments or for its KISS/xorshf96 implementations with pinned test signatures.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the PRNG headers; the chaos machines link libchaos (src/, built with CMake); tests and benchmarks use Google Test and Google Benchmark submodules |
| **Minimum toolchain** | C++11, g++ 4.7+ (CMake check); Travis CI used g++-4.8. Clang builds force libc++. MSVC is rejected by CMakeLists.txt. |
| **Platforms** | Linux/macOS with GCC or Clang (Travis used Ubuntu trusty); no architecture-specific code in the PRNG headers |
| **Thread safety** | not documented; generators are plain objects with mutable state, so use one per thread |
| **Drop-in for the baseline** | partial — exposes operator(), min() and max() like a std:: engine but no result_type, and seeding uses seed()/operator&lt;&lt; with generator-specific types rather than the std:: engine constructors |

## Gotchas

- Weak seeding: seed(n) on the '128+' and '1024\*' classes overwrites only the first state word and leaves the rest as fixed constants, so the first CHAOS_PRNG_XOROSHIRO128PLUS output after seed(n) is just n + 0x121fd2155c472f96, and streams from nearby seeds start correlated. KISS.seed(x) never reseeds its two MWC words, and seed(0) zeroes its xorshift component.
- Every generator object carries two std::string members (name and authors, from CHAOS_META_DEFINE), so construction can allocate and copies are heavier than the state alone.
- chaos.h #defines and then #undefs short macro names (M, R, KISS, MWC, SHR3, CONG, znew, wnew), which clobbers user macros with those names.
- chaos::truely&lt;&gt; reads current_position and current_checkpoint in its constructor (via reseed()) before they are initialized, which is undefined behaviour.

## Known shortcomings

- Mislabelled generators: XOROSHIRO128PLUS is actually xorshift128+ and XOROSHIRO1024STAR is xorshift1024\*; the bench discards outputs (no DoNotOptimize) and counts 4 calls as 1 item (ratios still valid).
- Misnamed generators: XOROSHIRO128PLUS is actually xorshift128+ and XOROSHIRO1024STAR is xorshift1024\*. prng&lt;&gt; has no result_type, so it is not a URBG and std distributions should fail. seed() overwrites one word only (first 128+ output = seed + 0x121fd2155c472f96). truely&lt;&gt; reads uninitialized members (UB). README pitches chaos::password for hashing with no third-party cryptanalysis. CMake rejects MSVC; library built with -march=native; bench discards outputs. Abandoned 2017.

## Caveats and trade-offs

The numbers are from 2016-2017 on a shared Travis VM whose CPU is not stated. The libchaos table and the STL block are listed separately in the README, and it does not say they came from the same run. The generator called CHAOS_PRNG_XOROSHIRO128PLUS is actually xorshift128+ (include/chaos/generators/xoroshiro.hh: s1 ^= s1 &lt;&lt; 23; s[1] = s1 ^ s0 ^ (s1 &gt;&gt; 18) ^ (s0 &gt;&gt; 5)), not xoroshiro128+, and CHAOS_PRNG_XOROSHIRO1024STAR is actually xorshift1024\* (shifts 31/11/30, multiplier 1181783497276652981). Both are mislabelled, and the README lists them as 'high' quality. Benchmark harness (tests/b_generators.cc): the return values of next()/operator() are discarded without DoNotOptimize, so output scrambling can be removed as dead code for every engine; each loop iteration makes 4 calls but counts 1 item, so all items/s figures are understated 4x (the ratios are unaffected). The speed edge is what any xorshift-family generator gives over MT19937. Most of the library (chaos machines, hashing, analysis) is not about speed.

Library built around 'chaos machines' (hashes and PRNGs) with its own push/pull API; the PRNG classes are listed with seed, output and period; whether they satisfy the C++ UniformRandomBitGenerator interface was not checked. Several generators (Xoroshiro128+, KISS, Xorshf96) are ports of existing algorithms.

## Maintenance

Abandoned since 2017-01-01 with 23 commits; BSD-2-Clause, and the PRNG headers are small enough to copy, but the mislabelled algorithms and missing result_type make it a poor dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party Google Benchmark items/s in the README for libchaos PRNGs and STL engines (std::mt19937 68.239M, mt19937_64 60.0674M items/s), with public benchmark code (tests/b_generators.cc) and build flags in CMakeLists.txt/.travis.yml, but the CPU is an unnamed Travis VM, so not A; no independent source, so C.
- **Verifier notes:** README numbers match exactly (Xoroshiro128Plus 178.426M vs mt19937 68.239M items/s, 2.6x derived). Metadata: BSD-2-Clause (FreeBSD variant), 1.6k stars, 158 forks, last commit 2017-01-01 (abandoned). Worth recording as a shortcoming: the generator named xoroshiro128+ is mislabelled (it implements xorshift128+).
- **Fields the verifier corrected:** `compiler_and_flags`, `baseline_stdlib`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/maciejczyzewski/libchaos>
  - <https://github.com/maciejczyzewski/libchaos/commits/master>
  - <https://github.com/maciejczyzewski/libchaos/tree/master/include/chaos>
  - <https://github.com/maciejczyzewski/libchaos/tree/master/include/chaos/generators>
  - <https://raw.githubusercontent.com/maciejczyzewski/libchaos/HEAD/README.md>
  - <https://raw.githubusercontent.com/maciejczyzewski/libchaos/HEAD/tests/b_generators.cc>
  - <https://raw.githubusercontent.com/maciejczyzewski/libchaos/HEAD/include/chaos/generators/xoroshiro.hh>
  - <https://raw.githubusercontent.com/maciejczyzewski/libchaos/HEAD/include/chaos/prng.hh>
  - <https://raw.githubusercontent.com/maciejczyzewski/libchaos/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/maciejczyzewski/libchaos/HEAD/.travis.yml>
  - <https://raw.githubusercontent.com/maciejczyzewski/libchaos/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/maciejczyzewski/libchaos/HEAD/README.md>
  - <https://raw.githubusercontent.com/maciejczyzewski/libchaos/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/maciejczyzewski/libchaos/HEAD/.travis.yml>
  - <https://raw.githubusercontent.com/maciejczyzewski/libchaos/HEAD/tests/b_generators.cc>
  - <https://raw.githubusercontent.com/maciejczyzewski/libchaos/HEAD/tests/t_generators.cc>
  - <https://raw.githubusercontent.com/maciejczyzewski/libchaos/HEAD/include/chaos.h>
  - <https://raw.githubusercontent.com/maciejczyzewski/libchaos/HEAD/include/chaos/prng.hh>
  - <https://raw.githubusercontent.com/maciejczyzewski/libchaos/HEAD/include/chaos/types.hh>
  - <https://raw.githubusercontent.com/maciejczyzewski/libchaos/HEAD/include/chaos/macros.hh>
  - <https://raw.githubusercontent.com/maciejczyzewski/libchaos/HEAD/include/chaos/seed.hh>
  - <https://raw.githubusercontent.com/maciejczyzewski/libchaos/HEAD/include/chaos/truely.hh>
  - <https://raw.githubusercontent.com/maciejczyzewski/libchaos/HEAD/include/chaos/generators/xoroshiro.hh>
  - <https://raw.githubusercontent.com/maciejczyzewski/libchaos/HEAD/include/chaos/generators/kiss.hh>
  - <https://raw.githubusercontent.com/maciejczyzewski/libchaos/HEAD/include/chaos/generators/abyssinian.hh>
  - <https://raw.githubusercontent.com/maciejczyzewski/libchaos/HEAD/include/chaos/generators/xorshf96.hh>
  - <https://raw.githubusercontent.com/maciejczyzewski/libchaos/HEAD/include/chaos/generators/xorshift.hh>
  - <https://raw.githubusercontent.com/maciejczyzewski/libchaos/HEAD/include/chaos/generators/linear.hh>
  - <https://raw.githubusercontent.com/maciejczyzewski/libchaos/HEAD/ALGORITHMS>
  - <https://raw.githubusercontent.com/maciejczyzewski/libchaos/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/maciejczyzewski/libchaos/HEAD/install.sh>
  - <https://raw.githubusercontent.com/maciejczyzewski/libchaos/HEAD/LICENSE>
  - <https://github.com/maciejczyzewski/libchaos>
  - <https://github.com/maciejczyzewski/libchaos/tree/master/src>
  - <https://github.com/maciejczyzewski/libchaos/issues?q=is%3Aissue>
  - <https://github.com/maciejczyzewski/libchaos/issues/11>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/maciejczyzewski/libchaos`) · [data/wave8/enrich/raw/github_com_maciejczyzewski_libchaos.json](../../../data/wave8/enrich/raw/github_com_maciejczyzewski_libchaos.json) (enrichment confidence 0.8)

</details>
