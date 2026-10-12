# toml++

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [YAML, TOML and XML](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++17 TOML 1.0 parser and serializer; parses 18x to 430x faster than toml11 v4.2.0 in a third-party matrix.

| | |
|---|---|
| **Beats** | toml11 v4.2.0 (also cpptoml, tomlc99 in the same matrix) |
| **Claimed result** | Parse time in ms, toml++ vs toml11: array_heavy 12.0 vs 5168.8, cargo_like 7.3 vs 649.2, datetime_heavy 26.8 vs 584.9, deep_tables 5.4 vs 548.1, mixed 10.1 vs 503.3, scalar_float 65.2 vs 1159.3, scalar_int 37.1 vs 1156.1, scalar_string 25.2 vs 452.0, table_heavy 29.3 vs 2377.3; about 18x to 430x faster than toml11 across the nine shapes (derived from page data). Second data point: toml11 PR #320 (Intel i5-12600KF, 122-line config, 10000 parses) lists toml++ at 1178.6 ms and 1015.5 ms against 17850.4 ms and 18118.0 ms for toml11 before the PR (about 15x and 18x, derived from page data) and 4482.6 ms and 4859.9 ms after it (about 3.8x and 4.8x). |
| **Workload** | Parse of nine generated TOML corpus files (0.25-1.5 MB each: array_heavy, cargo_like, datetime_heavy, deep_tables, mixed, scalar_float, scalar_int, scalar_string, table_heavy) from memory, min of 10 runs after 1 warmup, toml++ v3.4.0 vs toml11 v4.2.0. |
| **Metric** | throughput |
| **Hardware** | Apple M1 Max, Darwin arm64 (run 3, 2026-09-13) |
| **Compiler and flags** | Release build per LEDGER.md: -O3 -DNDEBUG -flto=thin (top-level CMakeLists.txt turns on CMAKE_INTERPROCEDURAL_OPTIMIZATION for Release); benchmarks/CMakeLists.txt also adds target_compile_options(bench_parse PRIVATE -O2), so the header-only toml++ v3.4.0 and toml11 v4.2.0 adapters (bench_tomlplus.cpp, bench_toml11.cpp) most likely compile at -O2, equally for both; compiler binary not named (Darwin arm64 with thin LTO implies Apple clang). |
| **Adoption** | 2.2k stars |
| **Last commit** | 2026-07-21 |
| **Links** | [repository](https://github.com/marzer/tomlplusplus) · [benchmark](https://github.com/leptris/teptris/blob/main/benchmarks/LEDGER.md) |

## Verdict

In the teptris benchmark ledger (run 3, 2026-09-13, Apple M1 Max, Release -O3 -flto=thin with -O2 on the bench target, compiler unnamed, min of 10 after 1 warmup) toml++ v3.4.0 parsed nine generated 0.25-1.5 MB TOML files in 5.4-65.2 ms against 452-5,169 ms for toml11 v4.2.0, about 18x-430x faster (derived from page data). A separate open toml11 PR (#320, i5-12600KF, 10,000 parses of a 122-line file) shows toml++ about 15-18x faster than toml11 before that PR and about 3.8-4.8x after it.

## Use it when

- You use toml11 (v4.2 or earlier) or a comparable comment-preserving C++ parser and config loading time matters: the cited matrix shows 18x-430x shorter parse times on 0.25-1.5 MB files, and an open toml11 PR measures about 15-18x on a 122-line config (about 0.1-0.12 ms per parse for toml++).
- C++17 projects that want a maintained, toml-test-conformant TOML 1.0 reader with a typed DOM, path-style lookup and round-trip output to TOML, JSON or YAML.
- Builds without exceptions or RTTI (game engines, embedded-ish targets): TOML_EXCEPTIONS=0 switches to a parse_result return type.
- Teams that want a single header to vendor, or a compiled mode (TOML_HEADER_ONLY=0 plus TOML_IMPLEMENTATION in one TU) to cut compile time; meson, CMake, vcpkg and Conan packaging exist.

## Skip it when

- Throughput is the goal: in the same matrix cpptoml beats it on all 8 shapes it can parse, tomlc17 on 3 shapes, and teptris (the benchmark author's C library) by 3.2-7.5x; toml++ ran at 22-60 MB/s, which is a mid-pack speed, not a fast one.
- You need comments, whitespace or key order preserved for editing configs in place: toml++ drops comments (toml11 keeps them, and tables here are sorted std::map, so original key order is lost on re-emit).
- Projects on current toml11 (v4.4.0 or later): its release notes claim toml::parse got 2x faster after the measured v4.2.0, and an open PR (#320) cuts it another 4x, so the gap is far smaller than the 18x-430x headline.
- Inputs that need TOML 1.1 syntax by default: the library advertises full TOML v1.0.0 support; newer-spec items such as newlines in inline tables or \e escapes only work behind TOML_ENABLE_UNRELEASED_FEATURES.
- Compile-time-sensitive codebases using the header-only default: the single header is large (the parser implementation alone is about 116 KB) and is instantiated in every including TU unless compiled mode is used.

## How it is fast

A hand-written recursive-descent parser that pulls codepoints from a UTF-8 reader built on Bjoern Hoehrmann's DFA decoder, decoding in 32-codepoint blocks with a 128-codepoint history ring for short look-back, instead of the combinator-style scanner chain toml11 v4 uses. Each node stores only a source_region (line/column begin and end plus a shared path pointer); comments are discarded rather than attached to values. Tables are std::map&lt;key, unique_ptr&lt;node&gt;&gt; and every value is its own heap node, so it is a conventional allocating DOM, not an arena or zero-copy design; its lead comes from toml11 being slow (0.1-1.9 MB/s in the cited run), not from SIMD or arena tricks.

## Compared with alternatives

Pick toml++ over teptris when you want a mature, widely packaged C++17 API with a typed DOM and JSON/YAML output and can accept 3-8x slower parsing; pick teptris when parse throughput dominates and a young C API is acceptable. TOMLDecoder (Swift), toml-spanner (Rust) and go-toml (Go) beat toml++ or their own baselines but only matter if you are not in C++.

## Integration

| | |
|---|---|
| **Form** | header-only (optional compiled mode via TOML_HEADER_ONLY=0 and TOML_IMPLEMENTATION; C++20 module support) |
| **Dependencies** | none |
| **Minimum toolchain** | C++17; tested on Clang 8+, GCC 8+, MSVC VS2019 |
| **Platforms** | any; CI-tested on x64, x86 and ARM (Windows ARM64 added March 2026) |
| **Thread safety** | not documented; parse calls share no global state that the README mentions, but a parsed table is an ordinary mutable container with no internal locking |
| **Drop-in for the baseline** | no |

## Gotchas

- The last tagged release is v3.4.0; several parser fixes exist only on master: TOML_MAX_NESTED_VALUES lowered from 256 to 128 after a stack overflow on deeply nested arrays and inline tables (issue #292, March 2026), UB on the malformed input "[&" (#294) and a precondition violation on '[[[' headers (#301, May 2026). For untrusted input, pin a recent master commit rather than v3.4.0.
- Benchmark harness notes: the cited ledger compiles both header-only adapters inside bench_parse, whose CMakeLists appends -O2 after the Release -O3 (equal for toml++ and toml11), and the toml11 row also times a per-iteration copy into a std::vector; neither changes the size of the toml11 gap, but no compiler is named and only an Apple M1 Max run reports toml++ figures.
- The benchmark corpus is synthetic (seed 42) with 30,000-60,000 keys in a single table on the scalar shapes; toml++ inserts every key into a std::map and allocates every value separately, so those shapes measure allocator and tree-insert cost more than typical small config files do.
- With exceptions disabled toml::parse returns toml::parse_result, a table-or-error wrapper, instead of toml::table; code written for one mode does not compile unchanged in the other.

## Known shortcomings

- Tier B on leptris/teptris benchmarks/LEDGER.md (run 3, M1 Max, -O3 -DNDEBUG -flto=thin, compiler unnamed): wins only over toml11 v4.2.0, a slow baseline that keeps comments and was pinned before the 2x v4.4.0 speedup; cpptoml is faster on all 8 shapes it parses and tomlc17 on 3; bench_parse adds -O2 after Release -O3; the benchmark was written by a competitor's author.
- Enricher (orphaned file): the ledger's bench_parse appends -O2 after the Release -O3 (equal for both) and the toml11 row also times a per-iteration copy into a std::vector; no compiler named, only an Apple M1 Max run reports toml++ figures; the corpus is synthetic (seed 42, 30,000-60,000 keys in a single table on the scalar shapes) and toml++ inserts every key into a std::map and allocates every value separately, so those shapes measure allocator and tree-insert cost. The last tag v3.4.0 lacks master-only parser fixes (TOML_MAX_NESTED_VALUES lowered to 128 after a stack overflow, issue #292; UB on '[&', #294; precondition violation on '[[[' headers, #301), so pin a recent master commit for untrusted input; with exceptions disabled toml::parse returns toml::parse_result instead of toml::table.

## Caveats and trade-offs

The win is against toml11 only. In the same matrix cpptoml (v0.5-era, TOML 0.5 semantics, rejects heterogeneous arrays) parses faster than toml++ on all 8 shapes it can parse (for example cargo_like 4.0 ms vs 7.3 ms, scalar_float 24.3 ms vs 65.2 ms), tomlc17 is faster on array_heavy, deep_tables and mixed (6.8, 2.9 and 4.2 ms vs 12.0, 5.4 and 10.1 ms), tomlc99 is faster on deep_tables (2.9 ms), and teptris (the benchmark author's own C library) is 3.2-7.5x faster than toml++. The benchmark was written by the author of a competing TOML parser (teptris) and published in its own repository, so it is independent of toml++ and toml11 but not a neutral suite; it falls short of tier A because the compiler is not named (Darwin arm64 with -flto=thin implies Apple clang) and the toml++ and toml11 numbers come from a single machine. benchmarks/CMakeLists.txt adds target_compile_options(bench_parse PRIVATE -O2) after the Release -O3, so the header-only toml++ and toml11 adapters most likely compile at -O2 (equal for both). The toml++ row times toml::parse on a string_view; the toml11 row also times a copy into a std::vector (ledger says under 2% of parse). toml11 is pinned at v4.2.0 and its v4.4.0 release notes (2025-02-15) claim toml::parse is 2x faster, so the ratio is overstated against current toml11; toml11 per-token error-location metadata makes it a slow baseline (0.1-1.9 MB/s here), and the toml11 PR #320 author notes that toml11 parses and preserves comments while toml++ does not, so part of the gap is a feature difference. Run on generated corpora (seed 42), not real-world configs. toml++'s own repo has only examples/parse_benchmark.cpp (a timing loop, no comparison) and no published numbers; the PR #320 numbers (10,000 toml::try_parse calls, i5-12600KF) come from an open third-party PR with no compiler or flags stated. Linux x86_64 gcc CI numbers exist in the same ledger but give no toml++ figures.

Header-only C++17 (optional compiled mode); parser does not preserve comments, whereas toml11 keeps comments and per-token error-location metadata, which accounts for part of the gap; supports serialising to TOML, JSON and YAML; works with or without exceptions and RTTI.

## Maintenance

Actively maintained on master (last commit 2026-07-21, bug-fix PRs from many contributors), MIT-licensed, 2.2k stars; releases lag master, with v3.4.0 still the latest tag, so recent safety fixes require tracking master.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification B, tier now B.
- **Tier reason:** LEDGER.md run 3 (2026-09-13, Apple M1 Max, -O3 -DNDEBUG -flto=thin) lists every quoted toml++ and toml11 time, and the code is public (benchmarks/bench_tomlplus.cpp, bench_toml11.cpp, bench_main.cpp, scripts/run_benchmarks.sh: warmup 1, min of 10), but the compiler is never named, so not A; it is an independent third-party measurement by a competing parser's author, so B.
- **Verifier notes:** All nine toml++ vs toml11 times and the 18x-430x range (17.8x-431x derived) match LEDGER.md; PR #320 figures (1,178.6/1,015.5 vs 17,850.4/18,118.0 and 4,482.6/4,859.9 ms) match the open PR. Shortcomings: win only over toml11 (a slow, comment-preserving baseline pinned before its 2x v4.4.0 speedup); cpptoml faster on all 8 parsable shapes and tomlc17 on 3; benchmark by a competitor; compiler unnamed. Metadata confirmed (MIT, 2.2k stars, last commit 2026-07-21, active). Not a duplicate: teptris is listed separately with toml++ as its baseline.
- **Fields the verifier corrected:** `caveats`, `compiler_and_flags`
- **Shortcomings recorded by:** verifier batch-62 (wave 4); enricher (wave 4)
- **Pages the verifier opened:**
  - <https://github.com/leptris/teptris/blob/main/benchmarks/LEDGER.md>
  - <https://raw.githubusercontent.com/leptris/teptris/HEAD/benchmarks/LEDGER.md>
  - <https://raw.githubusercontent.com/leptris/teptris/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/leptris/teptris/HEAD/scripts/run_benchmarks.sh>
  - <https://raw.githubusercontent.com/leptris/teptris/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/leptris/teptris/HEAD/benchmarks/bench_tomlplus.cpp>
  - <https://raw.githubusercontent.com/leptris/teptris/HEAD/benchmarks/bench_toml11.cpp>
  - <https://raw.githubusercontent.com/leptris/teptris/HEAD/benchmarks/bench_main.cpp>
  - <https://github.com/ToruNiina/toml11/pull/320>
  - <https://github.com/ToruNiina/toml11/releases>
  - <https://github.com/marzer/tomlplusplus>
  - <https://github.com/marzer/tomlplusplus/commits/master>
- **Sources the enricher read:**
  - <https://github.com/marzer/tomlplusplus>
  - <https://github.com/marzer/tomlplusplus/commits/master>
  - <https://github.com/marzer/tomlplusplus/releases>
  - <https://github.com/marzer/tomlplusplus/issues?q=is%3Aissue+performance+OR+slow+OR+crash+OR+overflow>
  - <https://raw.githubusercontent.com/marzer/tomlplusplus/HEAD/README.md>
  - <https://raw.githubusercontent.com/marzer/tomlplusplus/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/marzer/tomlplusplus/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/marzer/tomlplusplus/HEAD/meson.build>
  - <https://raw.githubusercontent.com/marzer/tomlplusplus/HEAD/examples/parse_benchmark.cpp>
  - <https://raw.githubusercontent.com/marzer/tomlplusplus/HEAD/include/toml++/toml.hpp>
  - <https://raw.githubusercontent.com/marzer/tomlplusplus/HEAD/include/toml++/impl/preprocessor.hpp>
  - <https://raw.githubusercontent.com/marzer/tomlplusplus/HEAD/include/toml++/impl/parser.inl>
  - <https://raw.githubusercontent.com/marzer/tomlplusplus/HEAD/include/toml++/impl/table.hpp>
  - <https://raw.githubusercontent.com/marzer/tomlplusplus/HEAD/include/toml++/impl/node.hpp>
  - <https://raw.githubusercontent.com/marzer/tomlplusplus/HEAD/include/toml++/impl/array.hpp>
  - <https://raw.githubusercontent.com/marzer/tomlplusplus/HEAD/include/toml++/impl/parse_result.hpp>
  - <https://raw.githubusercontent.com/leptris/teptris/HEAD/benchmarks/LEDGER.md>
  - <https://raw.githubusercontent.com/leptris/teptris/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/leptris/teptris/HEAD/benchmarks/bench_tomlplus.cpp>
  - <https://raw.githubusercontent.com/leptris/teptris/HEAD/benchmarks/bench_toml11.cpp>
  - <https://raw.githubusercontent.com/leptris/teptris/HEAD/benchmarks/bench_main.cpp>
  - <https://raw.githubusercontent.com/leptris/teptris/HEAD/benchmarks/bench_common.hpp>
  - <https://raw.githubusercontent.com/leptris/teptris/HEAD/scripts/run_benchmarks.sh>
  - <https://raw.githubusercontent.com/leptris/teptris/HEAD/scripts/gen_bench_corpus.py>
  - <https://raw.githubusercontent.com/leptris/teptris/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/cktan/tomlc17/HEAD/README.md>
  - <https://github.com/ToruNiina/toml11/pull/320>
  - <https://github.com/ToruNiina/toml11/releases>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/marzer/tomlplusplus`) · [data/wave4/enrich/raw/github_com_marzer_tomlplusplus.json](../../../data/wave4/enrich/raw/github_com_marzer_tomlplusplus.json) (enrichment confidence 0.8)

</details>
