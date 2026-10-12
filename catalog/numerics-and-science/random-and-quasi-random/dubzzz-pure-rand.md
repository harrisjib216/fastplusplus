# pure-rand (fast-check PRNG library for JavaScript/TypeScript)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `TypeScript` · `MIT` · 🟢 active

> Seeded JavaScript/TypeScript PRNGs (xoroshiro128+, Mersenne Twister, LCG) with unbiased ranges; author's shuffle benchmark beats Math.random 1.4x.

| | |
|---|---|
| **Beats** | JavaScript native Math.random() (Xorshift128+ in Node 16.19.1) and the seedrandom, random-js, chance and faker Mersenne Twister libraries |
| **Claimed result** | Non-uniform: pure-rand Xoroshiro128+ 24.5 ms versus native Math.random 33.3 ms (native 1.4x slower), seedrandom Xorshift128 28.8 ms (1.2x slower), seedrandom Alea 28.1 ms (1.1x slower), chance Mersenne Twister 142.9 ms (5.8x slower), faker Mersenne Twister 109.1 ms (4.5x slower). Uniform: pure-rand 53.5 ms versus random-js Mersenne Twister 119.6 ms (2.2x slower). |
| **Workload** | Shuffle of an array of 1,000,000 items; mean time in ms, with separate non-uniform and uniform (unbiased range) sections. |
| **Metric** | throughput |
| **Hardware** | 2 x x64 Intel Xeon Platinum 8272CL @ 2.60GHz on GitHub Actions default runners, Ubuntu 22.04 container, 5.88 GB RAM |
| **Compiler and flags** | Node 16.19.1 (V8 JIT, default flags), pure-rand 6.0.0; benchmark script perf/compare.cjs (permalinked from COMPARISON.md at commit 556ec331) uses tinybench with 1,000 iterations and about 50 warmup iterations |
| **Adoption** | 117 stars; the PRNG behind fast-check (usage claim not checked) |
| **Last commit** | 2026-07-10 |
| **Links** | [repository](https://github.com/dubzzz/pure-rand) · [benchmark](https://raw.githubusercontent.com/dubzzz/pure-rand/HEAD/COMPARISON.md) |

## Verdict

The author's COMPARISON.md times a Fisher-Yates shuffle of a 1,000,000-element array (tinybench, 1,000 iterations) on Node 16.19.1 on a 2-vCPU Xeon Platinum 8272CL GitHub Actions runner. With biased float scaling, pure-rand 6.0.0 xoroshiro128+ took 24.5 ms against 33.3 ms for Math.random (V8's xorshift128+), 28.1-33.5 ms for seedrandom and 109-143 ms for the faker and chance Mersenne Twisters. With unbiased ranges it took 53.5 ms against random-js MT19937 at 119.6 ms (2.2x). The figures are for pure-rand 6.0.0 (January 2023); 8.4.2 has not been re-measured in that document.

## Use it when

- JS/TS code that needs seeded, replayable randomness: property-based tests, simulations, procedural generation, games with replays.
- You need unbiased integer ranges (uniformInt) or 53-bit doubles (uniformFloat64) without writing your own rejection sampling, which Math.random-based Math.floor(r \* n) code gets wrong.
- You need independent parallel streams (jump() moves xoroshiro128plus 2^64 steps ahead) or need to serialize and restore generator state (getState / \*FromState).
- Functional or immutable codebases that want pure generator calls via purify() and accept a clone per call.
- You already depend on fast-check: fast-check 4.10.2 lists pure-rand ^8.0.0 as its only dependency, so it adds no extra package.

## Skip it when

- C or C++ projects: it is TypeScript compiled to JS and cannot be called from C++. Use a C++ generator from this category instead.
- Anything security-sensitive (tokens, keys, shuffles with money at stake): none of the four generators is a CSPRNG; use crypto.getRandomValues.
- Statistically demanding work that reads low bits: xoroshiro128plus next() returns the low 32 bits of the 64-bit s0+s1 sum, the bits the xoroshiro128+ literature reports as failing linearity tests.
- Seeding many independent runs from random seeds: the xoroshiro128plus(seed) factory takes a 32-bit seed, so only 2^32 of its 2^128 states are reachable that way (use jump() for streams).
- Bulk throughput: there is no typed-array fill; generateN returns a plain number[], and purify() allocates a clone on every call.

## How it is fast

Each 64-bit state word is kept as two 32-bit JavaScript numbers and advanced with |0, &gt;&gt;&gt; and ^ so V8 stays in int32 arithmetic with no BigInt or allocation per draw (xoroshiro128plus.ts). congruential32 advances three LCG steps in parallel with Math.imul using precomputed a^2 and a^3 constants (8.4.1), and the 8.x releases also trimmed Mersenne Twister twisting, initialisation and allocations. uniformInt uses rejection sampling on one 32-bit draw followed by a modulo for ranges up to 2^32, with module-level scratch objects for wider ranges; it does not use Lemire's nearly divisionless method.

## Compared with alternatives

Pick it when the code is JavaScript or TypeScript; the catalogued language-specific siblings fill the same role elsewhere (fastrand for Python, vpxyz/xorshift and pgregory.net/rand for Go, xrandom for Dart). For C++ use testingRNG's lehmer64 or aesctr, or SIMD generators such as simdrng or SHISHUA, plus FastShuffleExperiments for bounded integers, which use a nearly divisionless method where pure-rand uses a modulo.

## Integration

| | |
|---|---|
| **Form** | module (npm package pure-rand, CommonJS and ESM builds, subpath exports only since 8.0.0, TypeScript types included) |
| **Dependencies** | none (no runtime dependencies in package.json 8.4.2) |
| **Minimum toolchain** | No engines field; CI checks the bundle on Node 12.17.0 (test-legacy-bundle script). ES module subpath imports need a bundler or Node with exports-map support. |
| **Platforms** | any JavaScript runtime (Node, browsers, Deno/Bun not documented) |
| **Thread safety** | not documented; since 8.0.0 generators mutate in place, so give each worker or logical stream its own instance (clone() or jump()). |
| **Drop-in for the baseline** | no |

## Gotchas

- 8.0.0 is a breaking release: no main entry point (import from pure-rand/generator/... and pure-rand/distribution/...), rng moved to the first argument, mutation became the default, unsafeUniformIntDistribution became uniformInt, and fromState moved to xoroshiro128plusFromState and similar exports. The benchmark code (perf/compare.cjs at 556ec331) uses the 6.x names and will not run on 8.x.
- next() returns a signed int32 in [-2^31, 2^31 - 1]; use &gt;&gt;&gt; 0 for an unsigned value. uniformFloat64 consumes two next() calls per double.
- The README's 'non-uniform' recipe ((rng.next() &gt;&gt;&gt; 0) / 2^32 scaled by the range) is the variant that won the 1.4x benchmark and is biased; the README itself recommends against it.
- Historic issues #1 (infinite loop when the range exceeded the generator) and #63 (non-uniform for gaps beyond 32 bits) are closed; no open bug or quality issues were listed on 2026-10-03.

## Known shortcomings

- Tier A on COMPARISON.md (perf/compare.cjs, Node 16.19.1, Xeon Platinum 8272CL), but the non-uniform rows use the mutating unsafeNext() path, not the pure API the library is named for.
- The 'pure functional API' is stale: 8.0.0 (2026-03) made mutation the default, with pure semantics only via a purify() clone. The benchmark is pure-rand 6.0.0 on Node 16; perf/compare.cjs uses removed 6.x names and 8.4.2 was never re-measured. xoroshiro128plus next() returns the low 32 bits of the 64-bit sum (weak linear low bits per the xoroshiro128+ literature, snippet only); a 32-bit seed reaches only 2^32 states; uniformInt uses modulo rejection, not nearly-divisionless. fast-check 4.10.2 depends on pure-rand ^8.0.0.

## Caveats and trade-offs

JavaScript only, not usable from C++. Measured on shared GitHub Actions runners (noisy), with old versions (pure-rand 6.0.0, Node 16). The workload is a Fisher-Yates shuffle, so it measures range reduction as well as the generator. The non-uniform pure-rand rows call the mutating unsafeNext() API rather than the pure next() API the library is named for. The native Math.random baseline appears only in the non-uniform section; the uniform section compares only against random-js. COMPARISON.md's prose calls the non-uniform section 'known to be slower' (rejection resampling), which describes the uniform section; the tables themselves are consistent. Run by the project author. The 'Congruential' generator (congruential32 in the code) is listed as 1.1x faster than the recommended Xoroshiro128+ in the non-uniform table.

Pure functional API: generators are immutable and return a new generator on every call, which costs allocation but enables rollback and purity. Offers congruential32, Mersenne Twister, xorshift128+ and xoroshiro128+ with built-in unbiased uniform ranges and jump support.

## Maintenance

Active (8.4.2 released 2026-07-10, frequent performance commits), MIT, zero dependencies and the PRNG under fast-check, but JavaScript-only, so for this C++-first catalog it is a reference entry for JS projects.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** COMPARISON.md times pure-rand against native Math.random (Node 16.19.1, Xorshift128+) and the seedrandom, faker, chance and random-js generators. The benchmark code is public (perf/compare.cjs, pinned at commit 556ec331, tinybench, 1,000 iterations of a 1,000,000-item Fisher-Yates shuffle). The runtime version (Node 16.19.1, default flags) and the CPU (Intel Xeon Platinum 8272CL @ 2.60GHz, GitHub Actions runner) are stated, so A.
- **Verifier notes:** Every number in claimed_speedup matches COMPARISON.md exactly. Metadata confirmed on github.com: MIT, 117 stars, 5 forks, not a fork or archived, last commit 2026-07-10 (active). Scope flag: TypeScript/JavaScript library, kept as a non-C++ entry like other wave 8 non-C++ RNG entries.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/dubzzz/pure-rand/HEAD/COMPARISON.md>
  - <https://github.com/dubzzz/pure-rand>
  - <https://github.com/dubzzz/pure-rand/blob/556ec331c68091c5d56e9da1266112e8ea222b2e/perf/compare.cjs>
  - <https://github.com/dubzzz/pure-rand/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/dubzzz/pure-rand/HEAD/README.md>
  - <https://raw.githubusercontent.com/dubzzz/pure-rand/HEAD/COMPARISON.md>
  - <https://raw.githubusercontent.com/dubzzz/pure-rand/HEAD/package.json>
  - <https://raw.githubusercontent.com/dubzzz/pure-rand/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/dubzzz/pure-rand/HEAD/src/generator/xoroshiro128plus.ts>
  - <https://raw.githubusercontent.com/dubzzz/pure-rand/HEAD/src/generator/congruential32.ts>
  - <https://raw.githubusercontent.com/dubzzz/pure-rand/HEAD/src/types/RandomGenerator.ts>
  - <https://raw.githubusercontent.com/dubzzz/pure-rand/HEAD/src/types/JumpableRandomGenerator.ts>
  - <https://raw.githubusercontent.com/dubzzz/pure-rand/HEAD/src/distribution/uniformInt.ts>
  - <https://raw.githubusercontent.com/dubzzz/pure-rand/HEAD/src/distribution/internals/uniformIntInternal.ts>
  - <https://raw.githubusercontent.com/dubzzz/pure-rand/HEAD/src/distribution/uniformFloat64.ts>
  - <https://raw.githubusercontent.com/dubzzz/pure-rand/HEAD/src/distribution/uniformBigInt.ts>
  - <https://raw.githubusercontent.com/dubzzz/pure-rand/HEAD/src/utils/purify.ts>
  - <https://raw.githubusercontent.com/dubzzz/pure-rand/556ec331c68091c5d56e9da1266112e8ea222b2e/perf/compare.cjs>
  - <https://github.com/dubzzz/pure-rand>
  - <https://github.com/dubzzz/pure-rand/issues?q=is%3Aissue>
  - <https://github.com/dubzzz/pure-rand/tree/main/src>
  - <https://github.com/dubzzz/pure-rand/tree/main/src/__bench__>
  - <https://registry.npmjs.org/pure-rand>
  - <https://registry.npmjs.org/fast-check/latest>
  - WebSearch: xoroshiro128+ lowest bits linearity (result snippets from Wikipedia Xoroshiro128+ and arXiv 1810.05313; pages not opened, prng.di.unimi.it EGRESS_BLOCKED)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/dubzzz/pure-rand`) · [data/wave8/enrich/raw/github_com_dubzzz_pure_rand.json](../../../data/wave8/enrich/raw/github_com_dubzzz_pure_rand.json) (enrichment confidence 0.75)

</details>
