# xoshiro_cpp (david-cortes)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Random numbers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `CC0-1.0` · 🔴 abandoned

> Header-only xoshiro256++/128++ wrapper that drop-in replaces std::mt19937(_64) for &lt;random&gt; distributions.

| | |
|---|---|
| **Beats** | std::mt19937_64 |
| **Claimed result** | xoshiro256++: 946.70M gen/s vs std::mt19937_64: 294.26M gen/s (\~3.22x, derived from page data) |
| **Workload** | Raw 64-bit integer generation (xoshiro256++ variant), mean time per generation over 100 repetitions. |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-3570 @ 3.40GHz |
| **Compiler and flags** | clang, -O3 -DNDEBUG, no architecture-specific optimization flags |
| **Adoption** | 1 star |
| **Last commit** | 2021-09-08 |
| **Links** | [repository](https://github.com/david-cortes/xoshiro_cpp) · [benchmark](https://github.com/zeFresk/cpp-random-benchmarks) |

## Verdict

On zeFresk/cpp-random-benchmarks (Google Benchmark, 100 repetitions, clang -O3 -DNDEBUG, no architecture-specific flags, Intel i5-3570 @ 3.40GHz), xoshiro256++ generated 946.70M 64-bit values/s vs std::mt19937_64's 294.26M/s, about 3.2x, with both the benchmark source (src/xoshiro.cpp comparing directly against src/std.cpp) and the results table publicly readable.

## Use it when

- Need higher raw 64-bit generation throughput than std::mt19937_64 for simulations, statistical/ML model initialization, or Monte Carlo work while keeping &lt;random&gt;-engine compatibility (distributions, std::shuffle)
- Want a much smaller generator state (32 bytes vs \~2.5KB for MT19937), e.g. per-thread or per-object RNG instances, or many concurrent generator states
- Need independent parallel streams: jump()/long_jump() advance the state by the canonical 2^128/2^192-draw offsets to split into non-overlapping subsequences (both methods and the correct jump-polynomial tables are present in xoshiro.h, confirmed by reading the source this session)
- Willing to vendor a single \~400-line public-domain header with no build step and no dependencies beyond the STL
- Non-cryptographic use where BigCrush-class statistical quality is enough

## Skip it when

- Need cryptographic-strength randomness: xoshiro256++ is explicitly not a CSPRNG
- Need output bit-for-bit reproducible with the reference prng.di.unimi.it implementation for a given integer seed: this wrapper's seed(uint64_t) path deliberately differs from the canonical seeding recipe (stated in the README)
- Rely on generator equality comparisons: operator== in both classes is implemented as a bare `return std::memcmp(...)` without comparing to 0, so it reports mismatched states as equal and identical states as unequal (verified by reading xoshiro.h this session) — do not use it
- Need an actively maintained or widely-adopted dependency: single-star, single-file personal project, no commits since 2021-09-08, no LICENSE file (CC0 notice only in source/README)
- Need runtime-selectable, arbitrary-count independent streams the way PCG offers (per-instance odd increment); xoshiro here only offers the two fixed jump offsets

## How it is fast

Uses the xoshiro256++/128++ algorithm (Blackman & Vigna, 2019): a 256-bit (or 128-bit) state advanced with a few XORs, shifts and rotates per step, with a rotate-add-rotate output scrambler, no division and no large lookup tables, and a state small enough to sit in registers/L1 versus MT19937's \~2.5KB table and its tempering step. On the linked benchmark this measured 946.7M gen/s vs std::mt19937_64's 294.3M gen/s on the same hardware/compiler.

## Compared with alternatives

Pick this over PCG (pcg-cpp / wjakob pcg32) when you specifically want the xoshiro256++ statistical profile with built-in jump()/long_jump() streams in one dependency-free header; on the same benchmark PCG's pcg64_fast is slower (763.5M/s) while pcg32_fast is faster but 32-bit only (1072M/s). If raw throughput matters more than the specific algorithm, AESRand (27-34 GB/s, requires AES-NI) or biski64 (\~2.5x std::mt19937_64) beat xoshiro256++ by a wide margin on their own benchmarks.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (STL only: &lt;iostream&gt;, &lt;cstring&gt;, &lt;cstdint&gt;) |
| **Minimum toolchain** | C++11 (per README); code compiles conditionally for C++20 to drop the explicit operator!= |
| **Platforms** | any — portable C++ using bit rotations and memcpy, no SIMD or architecture-specific intrinsics; benchmark itself ran on x86-64 |
| **Thread safety** | not documented; all state is per-instance member data with no static/global mutable state observed in xoshiro.h, so separate instances per thread should be independent, but the author makes no explicit thread-safety claim |
| **Drop-in for the baseline** | true — same operator(), seed(), discard(), min()/max(), and stream insertion/extraction methods as std::mt19937_64, usable directly with &lt;random&gt; distributions and std::shuffle |

## Gotchas

- operator== is `return std::memcmp(...)` without `== 0`, so it evaluates backwards (identical states compare unequal, differing states compare equal) — confirmed in xoshiro.h this session; don't use it for equality checks
- Default-constructed instances start from a fixed hardcoded state (not randomly seeded), the same gotcha as std::mt19937's default constructor — call seed() explicitly for non-deterministic output
- Seeding logic is intentionally different from the canonical prng.di.unimi.it recipe (README: 'small change in the seeding logic'), so output won't match the reference C implementation for the same integer seed
- No LICENSE file in the repo, only a CC0 dedication noted in the README and the source header comment — a compliance process that requires an actual LICENSE file will flag this

## Caveats and trade-offs

Single-file, single-star personal wrapper repo with no dedicated LICENSE file (only a source-header notice that the underlying algorithm, by Blackman and Vigna, is public-domain/CC0); the algorithm's own canonical site (prng.di.unimi.it) is already in the excluded/known list, but this specific C++ wrapper repo is a distinct URL. Very low notability/adoption. [policy] CC0/public-domain dedication: copyable, but no patent grant.

xoshiro256++ has a much smaller period (2^256-1) than MT19937 (2^19937-1) but with far smaller state (32 bytes vs \~2.5KB); lacks jump/long-jump functions for parallel stream generation that canonical xoshiro implementations provide; not cryptographically secure.

## Maintenance

Abandoned since its last commit on 2021-09-08 (1 star, 1 fork, 0 open issues, no PRs) but it's a single \~400-line CC0/public-domain header with no LICENSE file — trivial to vendor and audit, so the lack of maintenance is low-risk beyond the license-file gap.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** The shootout's README table has xoshiro256++ (david-cortes/xoshiro_cpp) at 946.704M/s against std::mt19937_64 at 294.261M/s. The benchmark code is public: zeFresk/cpp-random-benchmarks src/xoshiro.cpp and src/std.cpp, with xoshiro_cpp pinned at d2c7ba4. The README states clang with -O3 -DNDEBUG and an Intel i5-3570.
- **Verifier notes:** The README and header declare CC0 (public-domain dedication), which is not OSI-approved. Under the strict rule usability becomes 'reference'; the orchestrator may choose to treat public-domain dedications as copyable. The header says its code was 'taken from' prng.di.unimi.it (a seed known-list entry) and wrapped as a &lt;random&gt;-compatible C++ engine. I kept the record because it is a distinct C++ port by a different author, but it may be worth folding into the xoshiro seed record. The metadata checked out: 1 star, last commit 2021-09-08, abandoned.
- **Fields the verifier corrected:** `usability`
- **Pages the verifier opened:**
  - <https://github.com/zeFresk/cpp-random-benchmarks>
  - <https://github.com/zeFresk/cpp-random-benchmarks/blob/main/src/xoshiro.cpp>
  - <https://github.com/zeFresk/cpp-random-benchmarks/blob/main/src/std.cpp>
  - <https://github.com/david-cortes/xoshiro_cpp>
  - <https://github.com/david-cortes/xoshiro_cpp/blob/master/xoshiro.h>
- **Sources the enricher read:**
  - <https://github.com/david-cortes/xoshiro_cpp>
  - <https://github.com/david-cortes/xoshiro_cpp/blob/master/README.md>
  - <https://github.com/david-cortes/xoshiro_cpp/blob/master/xoshiro.h>
  - <https://github.com/david-cortes/xoshiro_cpp/issues>
  - <https://github.com/david-cortes/xoshiro_cpp/pulls>
  - <https://github.com/zeFresk/cpp-random-benchmarks>
  - <https://github.com/zeFresk/cpp-random-benchmarks/blob/main/src/xoshiro.cpp>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/david-cortes/xoshiro_cpp`) · [data/wave1/enrich/raw/github_com_david_cortes_xoshiro_cpp.json](../../../data/wave1/enrich/raw/github_com_david_cortes_xoshiro_cpp.json) (enrichment confidence 0.6)

</details>
