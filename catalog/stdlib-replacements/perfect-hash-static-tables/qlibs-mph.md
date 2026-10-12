# mph (qlibs)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Perfect hashing and static tables](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟡 stale

> C++20 compile-time perfect-hash lookup built on BMI2 pext; 2.4-10x lower latency than std::unordered_map on 5-100-key string sets.

| | |
|---|---|
| **Beats** | std::unordered_map (std::hash), std::map, boost::unordered_flat_map (Boost 1.85), frozen::unordered_map, gperf, if-else and switch-case chains |
| **Claimed result** | Perfect-hashing benchmark on an i7-12650H with -O3 -march=native. The page shows plots only, so all values below were read off the plot pixels (derived from page data, about ±1 px). Plotted time is the total for size×100,000 lookups. 1024 string keys of length 1-8, all hits: std::unordered_map \~2.14 s vs mph \~0.16 s ('clang++-19' panel), \~13.7x (\~21 ns vs \~1.5 ns per lookup); 'g++-13' panel \~2.07 s vs \~0.15 s, \~14x. In the same run gperf \~0.46 s (\~2.9x slower than mph), boost::unordered_flat_map \~0.91 s (\~5.9x) and frozen \~1.44 s (\~9.2x). 1024 string keys of length exactly 8, all hits: std::unordered_map \~1.58 s vs mph \~0.15 s, \~10x; gperf \~2.1x slower than mph. 1024 uint32 keys, all hits: std::unordered_map \~0.76 s vs mph \~0.13 s, \~5.8-6.1x; boost::unordered_flat_map \~1.15-1.3x; frozen \~2.1-2.3x. 32 string keys of length 1-8, all hits: std::unordered_map \~0.052 s vs mph \~0.0033 s, \~15x (low precision because mph sits near the axis floor). mph is not faster everywhere. All misses, 1024 string keys: gperf \~0.11 s beats mph \~0.13 s. All misses, 1024 int keys: boost::unordered_flat_map roughly ties mph (\~0.14 s each in the 'g++-13' panel). std::unordered_map is slower than mph in every plot. The README nanobench tables (no CPU stated) are unchanged: std::unordered_map 15.32 ns vs mph 1.58 ns at 100 keys of length 8 (\~9.7x). |
| **Workload** | Lookups in static maps whose keys are known at compile time. int_to_int: uint16-range keys with 1-32 entries, and uint32-range keys with 1-1024 entries. str_to_int: string_view keys of length 1-8 or exactly 8, with 1-32 and 1-1024 entries. Hit probability 1.0, 0.5 and 0.0. Each target is a separate binary that times size×100,000 lookups from a pre-generated vector (std::chrono total, median of 3 runs). Checksums are asserted equal across all targets. Baselines: std::map, std::unordered_map (std::hash), boost::unordered_flat_map, frozen::unordered_map, gperf (string keys only), and if_else/switch_case chains. Build time and stripped binary size are also plotted. Harness: https://github.com/qlibs/mph/tree/benchmark/perfect_hashing. The README nanobench tables (5-100 keys) remain as secondary first-party data. |
| **Metric** | latency |
| **Hardware** | 12th Gen Intel Core i7-12650H (from /proc/cpuinfo in the notebook). Pinned to logical CPU 1 (a P-core) with taskset. Turbo Boost was on and the intel_pstate governor was powersave: pyperf system tune failed with permission errors. |
| **Compiler and flags** | Page labels say clang++-19 and g++-13 with -std=c++20 -DNDEBUG -O3 -march=native. The Makefile also adds -DNTEST -fconstexpr-steps=1000000000 -ftemplate-depth=1024 and -I for Boost 1.85. Both columns were most likely built with clang++-18, because the committed Makefile hard-codes CXX=clang++-18, which overrides the notebook's CXX environment variable. The stripped binary sizes are identical in both panels. The Dockerfile also installs clang 18 and gcc 13. |
| **Adoption** | 265 stars |
| **Last commit** | 2025-07-20 |
| **Links** | [repository](https://github.com/qlibs/mph) · [benchmark](https://qlibs.github.io/mph/perfect_hashing) |

## Verdict

In the author's nanobench run, lookups were random hits drawn from sets of 5-100 strings of 1-8 bytes. It used clang++ and g++ with -O3 -mbmi2 and libstdc++ on the g++ run; no CPU model or compiler versions are given. mph measured 1.4-7.2 ns per lookup, against 5.3-25.4 ns for std::unordered_map (with boost::hash) and 7.7-13.1 ns for gperf. The lead over gperf shrinks to 1.3-2.2x on the variable-length sets. The harness calls the v2-era mph::hash/mph::fixed_string API, which the current header no longer has, so the tables predate the current lookup/find code.

## Use it when

- Hot-path mapping of a fixed set of short keys known at build time: keyword or command parsing, string_to_enum/enum_to_string, ticker-symbol or message-type dispatch (the README examples).
- Sets of a few keys up to about a thousand. The README latency tables cover 5-100 string keys; the author's plot-only benchmark goes to 1024 keys.
- Strings of 8 bytes or fewer, and ideally 4 or fewer (the FAQ says a smaller maximum length gives a smaller table and one fewer instruction), or integer keys as u32/u64.
- x86-64 with fast PEXT (Intel Haswell+ or AMD Zen3+ per the FAQ), built with -mbmi2 or -march=native.
- Inputs that are always in the set: mph::lookup (or find&lt;100&gt;) skips the key compare and, for tiny integer sets, compiles to 3-5 instructions (README asm).

## Skip it when

- Keys that are only known, or change, at run time. There is no insert, erase or iteration; the table is generated at compile time.
- Long keys. Keys must fit in 128 bits (16 bytes), or lookup/find are removed by SFINAE and you must write your own fallback policy (issues #5 and #6 are still open). The mask search also looks at only the low 64 bits (mask&lt;u64&gt;), so keys that share their first 8 bytes can fail (issue #3).
- MSVC or libc++. The requirements list only GCC 12+ and Clang 15+, and the header uses GCC/Clang builtins. Open PR #19 reports that main does not compile with libc++'s partial &lt;experimental/simd&gt;.
- Large sets. The FAQ says it handles thousands of keys, not millions; build time grows with size and can hit constexpr step limits.
- CPUs with slow PEXT (AMD Zen2 takes 18 cycles per the FAQ) or non-x86 targets. Both use the software pext fallback, and no run-time numbers are published for it.

## How it is fast

All table construction happens at compile time. For very small sets, lookup uses a PCG generator to search for a multiplier such that (key\*magic)&gt;&gt;shift picks a bit-field out of one 32/64-bit constant, so the lookup is a multiply, a shift and a mask with no memory access. Otherwise it greedily finds the smallest bit mask that keeps every key unique; at run time, BMI2 PEXT packs those bits into a dense index into a 2^popcount(mask) table, and find does one full-key compare (a cmov by default). Strings up to 16 bytes are loaded as one integer (memcpy plus BZHI to trim the length), so there is no per-character hashing or probe loop, and find on more than 64 entries does a single std::experimental::simd bucket compare.

## Compared with alternatives

Pick mph over frozen or gperf when your keys are integers, enums or strings of 8 bytes or fewer on x86-64 with BMI2 and per-lookup latency matters most. The author's plots put it below frozen, gperf and boost::unordered_flat_map up to 1024 keys, and there is no head-to-head with Kronuz constexpr-phf or ConstexprCore/perfect_hash. Pick frozen instead for C++14, MSVC, longer strings or a container API; pick gperf or triehash for long string keys or generated C code.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (optional &lt;experimental/simd&gt; from libstdc++, which find needs for sets of more than 64 entries) |
| **Minimum toolchain** | C++20; GCC 12+ or Clang 15+ (README). A C++20 module wrapper, mph.cppm, is also provided. |
| **Platforms** | x86-64 is the target (BMI2 optional but recommended; AVX2/AVX-512 used through std::experimental::simd); other targets, including arm-none-eabi since issue #14, use a software pext fallback; GCC/Clang only |
| **Thread safety** | not documented; lookup and find are noexcept and read only immutable constexpr tables |
| **Drop-in for the baseline** | no |

## Gotchas

- mph::lookup returns an arbitrary value for a key that is not in the set. Use mph::find for untrusted input. find&lt;100&gt; (probability = 100) also skips the compare, so it behaves the same way.
- The header runs its self-tests as static_asserts every time you include it; define -DNTEST to skip them. Large sets can hit 'constexpr evaluation hit maximum step limit'; raise -fconstexpr-ops-limit (GCC) or -fconstexpr-steps (Clang).
- Without &lt;experimental/simd&gt;, find only accepts sets of 64 entries or fewer (requires-clause). Sets above 64 entries use SIMD buckets sized to the native register width.
- Main has an untagged change made after the v5.0.5 tag (PR #18, July 2025), still in the v5_0_5 inline namespace. The change narrows the probe key to the 32/64-bit mask type before find compares it with the full stored key. From reading the code (not compiled), keys longer than 4 bytes whose mask fits in 32 bits may stop matching, and no self-test covers this case. Pin tag v5.0.5 or test your key set.

## Caveats and trade-offs

First-party benchmark. The harness is on the benchmark branch, last changed 2024-07-02, so the README numbers may predate the current main code. The README gives compiler names and flags but no compiler versions and no CPU model, so the tier is capped at C. The std::unordered_map baseline uses boost::hash, not std::hash. The largest key set is 100 keys, not 149. mph::hash assumes valid keys, while the map baselines call find() with miss handling. The random_uints_5 row has no baseline. The speedup vs std::unordered_map is about 2.4x-10x across rows (derived from page data), which is plausible for 5-100 key sets. [retier] First-party benchmark by the mph author, run 2024-07-02. Results are shown only as plots; every number was read off the plot pixels (derived from page data). The compiler labels are unreliable: the Makefile's hard-coded CXX=clang++-18 overrides the notebook's CXX, and the binary sizes in the 'clang++-19' and 'g++-13' panels are identical, so this is almost certainly one compiler (likely clang++-18), not a clang vs gcc comparison. baseline_stdlib libstdc++ is inferred: Linux/Ubuntu, and no -stdlib=libc++ appears anywhere. Reproducibility gaps: the benchmark branch does not vendor the mph header (-I.. points at a branch root with no 'mph' file), so the mph version must be supplied by hand (about v5.0.0 / main 2e9418c at run time). frozen and gperf versions are not stated. Key sets come from Python's unseeded random, and only the C++ lookup stream is seeded. Timing is noisy: turbo on, powersave governor, non-monotonic std::unordered_map curves. Plotted time includes streaming a size×100k-element lookup vector, so mph's \~1.5 ns per lookup at 1024 keys may be close to a memory-streaming floor. mph is not fastest in miss-heavy runs: gperf beats it on 1024 string keys at 0% hits, and boost::unordered_flat_map ties it on 1024 int keys at 0% hits. The README's std::unordered_map-with-boost::hash caveat applies only to the README tables, since this harness uses std::hash. Ratios of \~6-15x vs std::unordered_map are plausible for small static sets under -O3.

Requires C++20 (gcc-12+/clang-15+); keys/values must be fully known at compile time (constexpr array), not a general dynamic hash table; author states it targets thousands, not millions, of entries; optional bmi2/SIMD hardware acceleration

## Maintenance

Stale: the last tagged release is v5.0.5 (Jan 2025), the last commit is a July 2025 community PR, and a libc++ build fix (PR #19) has been unmerged since Sept 2025. It is MIT-licensed, a single header with no dependencies, and easy to vendor; pin v5.0.5.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now A.
- **Tier reason:** The README 'Benchmarks (run-time)' tables show mph against std::map, std::unordered_map and gperf. The benchmark code is public (benchmark/benchmark.cpp on the benchmark branch, using nanobench). Compiler names and flags are given (clang++/g++ -std=c++20 -O3 -DNDEBUG -mbmi2), but no compiler versions and no CPU model. That is first-party code with partial methodology, so Tier C.
- **Retiered** C to A: The second benchmark meets all four Tier A conditions. (1) The code is public. The page https://qlibs.github.io/mph/perfect_hashing is perfect_hashing/index.html on the qlibs/mph 'benchmark' branch, served by GitHub Pages from that branch root. It is the rendered export of perfect_hashing/benchmark.ipynb. The harness is in the same folder: Makefile, Dockerfile, benchmark.hpp, and one .cpp per target (mph.cpp, unordered_map.cpp, map.cpp, boost_unordered_flat_map.cpp, frozen.cpp, gperf.cpp, if_else.cpp, switch_case.cpp). The qlibs.github.io repo is only the org landing page and holds no benchmark code. (2) The CPU is stated: the notebook prints /proc/cpuinfo showing '12th Gen Intel(R) Core(TM) i7-12650H'. Runs are pinned to CPU 1 with taskset. (3) Flags are stated: CXXFLAGS='-std=c++20 -DNDEBUG -O3 -march=native' is set in the notebook and printed on every plot title. The Makefile adds -DNTEST and the constexpr/template-depth limits. (4) The compiler is stated: the page and plots say clang++-19 and g++-13. The committed Makefile sets CXX=clang++-18 unconditionally, and a makefile assignment overrides the CXX environment variable the notebook passes. So both columns were most likely built with clang++-18. The byte-identical stripped binary sizes in the 'clang++-19' and 'g++-13' panels (int_to_int and str_to_int) support this. The compiler actually used is still fixed by public code, so the run is reproducible and stays Tier A. The per-compiler labels are unreliable (see caveats). This supersedes the earlier Tier C, which rested on the README nanobench tables that give no compiler version and no CPU.
- **Verifier notes:** The claimed numbers match the clang++ table exactly: 5.56 vs 1.61 ns, 15.32 vs 1.58 ns, and gperf 8.04 ns. mph is fastest in every benchmark group under both compilers. Metadata checks out: MIT license (in .github/LICENSE and the header, so spdx is null), 265 stars, last commit 2025-07-20, stale. baseline_stdlib libstdc++ is inferred from the g++ run; the stdlib for the clang++ run is not stated.
- **Fields the verifier corrected:** `workload`, `baseline_stdlib`, `caveats`, `benchmark_url`, `claimed_speedup`, `baseline`, `compiler_and_flags`, `hardware`
- **Pages the verifier opened:**
  - <https://github.com/qlibs/mph>
  - <https://github.com/qlibs/mph#benchmarks>
  - <https://github.com/qlibs/mph/blob/main/.github/README.md>
  - <https://github.com/qlibs/mph/blob/main/.github/LICENSE>
  - <https://github.com/qlibs/mph/blob/main/mph>
  - <https://github.com/qlibs/mph/tree/benchmark>
  - <https://github.com/qlibs/mph/blob/benchmark/benchmark/benchmark.cpp>
  - <https://github.com/qlibs/mph/blob/benchmark/benchmark/data.hpp>
  - <https://github.com/qlibs/mph/blob/benchmark/benchmark/CMakeLists.txt>
  - <https://github.com/qlibs/mph/blob/benchmark/perfect_hashing/Makefile>
- **Sources the enricher read:**
  - <https://github.com/qlibs/mph>
  - <https://github.com/qlibs/mph#benchmarks>
  - <https://github.com/qlibs/mph/blob/main/.github/README.md>
  - <https://github.com/qlibs/mph/blob/main/mph>
  - <https://github.com/qlibs/mph/blob/main/mph.cppm>
  - <https://github.com/qlibs/mph/issues?q=is%3Aissue+is%3Apr>
  - <https://github.com/qlibs/mph/issues/1>
  - <https://github.com/qlibs/mph/issues/2>
  - <https://github.com/qlibs/mph/issues/3>
  - <https://github.com/qlibs/mph/issues/4>
  - <https://github.com/qlibs/mph/issues/5>
  - <https://github.com/qlibs/mph/issues/6>
  - <https://github.com/qlibs/mph/issues/8>
  - <https://github.com/qlibs/mph/issues/10>
  - <https://github.com/qlibs/mph/issues/12>
  - <https://github.com/qlibs/mph/issues/13>
  - <https://github.com/qlibs/mph/issues/14>
  - <https://github.com/qlibs/mph/issues/16>
  - <https://github.com/qlibs/mph/issues/17>
  - <https://github.com/qlibs/mph/pull/7>
  - <https://github.com/qlibs/mph/pull/9>
  - <https://github.com/qlibs/mph/pull/11>
  - <https://github.com/qlibs/mph/pull/15>
  - <https://github.com/qlibs/mph/pull/18/files>
  - <https://github.com/qlibs/mph/pull/19/files>
  - <https://github.com/qlibs/mph/releases>
  - <https://github.com/qlibs/mph/commits/main>
  - <https://github.com/qlibs/mph/blob/v2.2.0/mph>
  - <https://github.com/qlibs/mph/blob/v2.5.0/mph>
  - <https://github.com/qlibs/mph/blob/v3.0.1/mph>
  - <https://github.com/qlibs/mph/tree/benchmark>
  - <https://github.com/qlibs/mph/commits/benchmark>
  - <https://github.com/qlibs/mph/blob/benchmark/benchmark/benchmark.cpp>
  - <https://github.com/qlibs/mph/blob/benchmark/benchmark/CMakeLists.txt>
  - <https://github.com/qlibs/mph/blob/benchmark/benchmark/README.md>
  - <https://github.com/qlibs/mph/blob/benchmark/perfect_hashing/Makefile>
  - <https://github.com/qlibs/mph/blob/benchmark/perfect_hashing/benchmark.hpp>
  - <https://github.com/qlibs/mph/blob/benchmark/perfect_hashing/mph.cpp>
  - <https://github.com/qlibs/mph/blob/benchmark/perfect_hashing/frozen.cpp>
  - <https://github.com/qlibs/mph/blob/benchmark/perfect_hashing/Dockerfile>
  - <https://github.com/qlibs/mph/blob/benchmark/perfect_hashing/index.html>
  - <https://github.com/qlibs/mph/blob/benchmark/perfect_hashing/benchmark_int_to_int.png>
  - <https://github.com/qlibs/mph/blob/benchmark/perfect_hashing/benchmark_str_to_int.png>
  - <https://qlibs.github.io/mph/perfect_hashing>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/qlibs/mph`) · [data/wave1-phf/enrich/raw/github_com_qlibs_mph.json](../../../data/wave1-phf/enrich/raw/github_com_qlibs_mph.json) (enrichment confidence 0.8)

</details>
