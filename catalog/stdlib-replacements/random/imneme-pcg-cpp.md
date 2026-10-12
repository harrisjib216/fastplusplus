# PCG (pcg-cpp)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Random numbers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> Header-only C++11 PCG-family RNG beating std::mt19937/std::mt19937_64 raw-generation throughput by \~2.6-4x.

| | |
|---|---|
| **Beats** | std::mt19937 / std::mt19937_64 |
| **Claimed result** | pcg_cpp::pcg32_fast: 1071.97M gen/s vs std::mt19937: 270.65M gen/s (\~3.96x, derived from page data); pcg_cpp::pcg64_fast: 763.50M gen/s vs std::mt19937_64: 294.26M gen/s (\~2.59x, derived from page data) |
| **Workload** | Raw 32-bit/64-bit integer generation, mean time per generation over 100 repetitions, no downstream distribution. |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-3570 @ 3.40GHz |
| **Compiler and flags** | clang, -O3 -DNDEBUG, no architecture-specific optimization flags |
| **Adoption** | 854 stars |
| **Last commit** | 2022-04-08 |
| **Links** | [repository](https://github.com/imneme/pcg-cpp) · [benchmark](https://github.com/zeFresk/cpp-random-benchmarks) |

## Verdict

On zeFresk/cpp-random-benchmarks (Google Benchmark, pcg-cpp pinned at commit 428802d, clang -O3 -DNDEBUG, Intel Core i5-3570, no AVX2): pcg32_fast measured 1071.97M generations/s vs std::mt19937's 270.65M/s (\~3.96x), and pcg64_fast measured 763.50M/s vs std::mt19937_64's 294.26M/s (\~2.59x). Which C++ standard library (libstdc++ vs libc++) backed the std::mt19937 baseline is not stated in the benchmark.

## Use it when

- Raw uint32_t/uint64_t generation is the bottleneck (Monte Carlo inner loops, procedural generation, shuffling large arrays) and you don't need many independent streams.
- Code already consumes std::uniform_int_distribution or other &lt;random&gt; distributions -- PCG engines satisfy UniformRandomBitGenerator so distributions work unchanged.
- Non-cryptographic use where 64-bit (pcg32_fast) or 128-bit (pcg64_fast) internal state is acceptable.
- You can vendor a small, unmaintained header-only library (Apache-2.0/MIT dual-licensed) rather than depend on an actively-updated package.
- You want tunable stream separation later (setseq/oneseq/unique variants) without changing the surrounding API shape, if you outgrow the fast/MCG variant.

## Skip it when

- You need many statistically independent streams (e.g. one RNG per thread/worker) -- pcg32_fast/pcg64_fast are MCG-based with a single fixed stream; use the setseq variants (pcg32/pcg64) instead, at lower throughput.
- Cryptographic or security-sensitive randomness is needed -- PCG is not a CSPRNG and issue #27 ('Seed securely by default') is still open, so default seeding is not secure by default.
- Your code relies on seed()/set_stream() being independent -- issue #94 documents that calling seed() or seed(itype) on pcg32/pcg64 resets the stream to the default, silently discarding a previously-selected stream.
- You need an actively maintained upstream -- last commit 2022-04-08; issue #106 (Dec 2025) proposes a third-party fork (Total-Random/pcg-cpp) for Windows ARM64/MSVC/128-bit-fallback fixes that are unmerged upstream.
- You're touching custom seeding/streaming edge cases without testing -- several other open issues (#85, #91, #102) report surprising stream-selection/repeat behavior in specific variants; verify your exact typedef and seeding path.

## How it is fast

Each engine keeps a small 64-bit or 128-bit linear/multiplicative congruential generator (LCG/MCG) state, permuted through an output function (XSH-RR, XSL-RR, XSH-RS) on every call, instead of Mersenne Twister's \~20,000-bit state array and tempering step -- so a generated value costs one multiply-add plus a permute rather than a big-array update. The benchmarked '_fast' variants are MCG-based (pcg32_fast = mcg_xsh_rs_64_32, pcg64_fast = mcg_xsl_rr_128_64): they drop the increment/stream-selection add that the default setseq/oneseq engines perform every step, shortening the instruction path at the cost of a single fixed stream per type.

## Compared with alternatives

Pick imneme/pcg-cpp over wjakob/pcg32 when you need 64-bit generation or explicit stream-separation strategies (oneseq/setseq/unique/mcg, extended k-dimensional generators) -- wjakob/pcg32 is a smaller single-header 32-bit-only PCG (940M gen/s, \~3.47x) with less machinery. Pick it over xoshiro_cpp when you want PCG's settable-stream model (C++11 SeedSequence support, per-stream selection) rather than xoshiro256++'s larger 256-bit-state, no-stream-argument design, even though xoshiro256++ measured similarly (946M gen/s, \~3.22x) on the same benchmark suite.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (pcg_random.hpp includes pcg_extras.hpp and pcg_uint128.hpp from the same repo, no external deps) |
| **Minimum toolchain** | C++11 |
| **Platforms** | any; uses __SIZEOF_INT128__/compiler builtins where available and has MSVC-specific intrinsic paths for 128-bit ops in pcg_uint128.hpp, but community issue #106 reports unmerged fixes needed for Windows ARM64 and some MSVC/128-bit-fallback cases |
| **Thread safety** | not documented; no mutex/atomic usage found in pcg_random.hpp or pcg_extras.hpp -- treat a shared engine instance as unsynchronized, same caveat as std::mt19937 |
| **Drop-in for the baseline** | partial -- explain: satisfies UniformRandomBitGenerator like std::mt19937 so it works with std &lt;random&gt; distributions, but type names, constructors, and seed()/set_stream() semantics differ and are not interchangeable with std::mt19937 call sites |

## Gotchas

- pcg32_fast/pcg64_fast are MCG-based (mcg_xsh_rs_64_32 / mcg_xsl_rr_128_64): one fixed stream per instance, no per-object stream selection.
- seed() and seed(itype) on pcg32/pcg64 reinstall the default stream, discarding any stream previously set via set_stream() (issue #94, open).
- No secure-by-default seeding -- issue #27 (open) asks for default construction to seed from OS entropy; currently you must seed explicitly.
- Repository is a reference implementation with many similarly-named typedefs (pcg32 vs pcg32_oneseq vs pcg32_fast vs pcg32_k64 ...); picking the wrong one changes both speed and stream-independence guarantees.

## Caveats and trade-offs

Numbers come from a third-party shootout run on a 2012-era CPU (i5-3570, no AVX2); the README does not state whether libstdc++ or libc++ was linked for the std::mt19937 baseline. pcg-cpp's own site (pcg-random.org, docs pages) makes only statistical-quality benchmarking claims, not speed claims, on the pages checked this session.

128-bit internal state (vs MT19937's \~20,000-bit state) gives far fewer theoretically independent streams; fast variants (pcg32_fast/pcg64_fast) drop the increment-based stream selection used by the 'oneseq'/default variants for extra speed, trading some statistical/stream-separation guarantees; not cryptographically secure; API differs from a drop-in std::mt19937 substitute (template-heavy, many variant typedefs).

## Maintenance

Abandoned upstream -- last commit 2022-04-08, more than 3 years with no update; Apache-2.0/MIT dual-licensed and small enough to vendor as-is. A community fork (Total-Random/pcg-cpp, referenced in issue #106) exists for modern-platform fixes but is not merged upstream.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** The third-party shootout's README table has pcg_cpp::pcg32_fast at 1071.970M/s and pcg64_fast at 763.500M/s, against std::mt19937 at 270.652M/s and std::mt19937_64 at 294.261M/s. The benchmark code is public: zeFresk/cpp-random-benchmarks src/pcg.cpp and src/std.cpp, using Google Benchmark with pcg-cpp pinned at 428802d. The README states clang with -O3 -DNDEBUG and an Intel i5-3570.
- **Verifier notes:** The last commit on master (428802d) is 2022-04-08. The record's 2024-05-17 is only the repo's pushed_at timestamp, so the status is abandoned (more than 3 years). The ratios (\~3.96x and \~2.59x) recompute correctly. The standard library linked in the shootout is not stated, so baseline_stdlib stays empty.
- **Fields the verifier corrected:** `last_commit`, `maintenance_status`
- **Pages the verifier opened:**
  - <https://github.com/zeFresk/cpp-random-benchmarks>
  - <https://github.com/zeFresk/cpp-random-benchmarks/blob/main/src/pcg.cpp>
  - <https://github.com/zeFresk/cpp-random-benchmarks/blob/main/src/std.cpp>
  - <https://github.com/zeFresk/cpp-random-benchmarks/blob/main/CMakeLists.txt>
  - <https://github.com/imneme/pcg-cpp>
- **Sources the enricher read:**
  - <https://github.com/imneme/pcg-cpp>
  - <https://github.com/imneme/pcg-cpp/blob/master/README.md>
  - <https://github.com/imneme/pcg-cpp/blob/master/include/pcg_random.hpp>
  - <https://github.com/imneme/pcg-cpp/blob/master/include/pcg_extras.hpp>
  - <https://github.com/imneme/pcg-cpp/blob/master/include/pcg_uint128.hpp>
  - https://github.com/imneme/pcg-cpp/issues (search: bug, performance)
  - <https://github.com/imneme/pcg-cpp/issues/27>
  - <https://github.com/imneme/pcg-cpp/issues/94>
  - <https://github.com/imneme/pcg-cpp/issues/106>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/imneme/pcg-cpp`) · [data/wave1/enrich/raw/github_com_imneme_pcg_cpp.json](../../../data/wave1/enrich/raw/github_com_imneme_pcg_cpp.json) (enrichment confidence 0.85)

</details>
