# DAW JSON Link

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [JSON serialization](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> Header-only C++ JSON library that parses straight into your typed structs, beating RapidJSON, simdjson DOM, Boost.JSON and nlohmann.

| | |
|---|---|
| **Beats** | RapidJSON (same suite also includes simdjson, yyjson, Boost.JSON, Boost.PropertyTree, nlohmann::json) |
| **Claimed result** | kostya/benchmarks Json test, current README (derived from page data, seconds): g++ DAW JSON Link 0.089s vs RapidJSON 0.154s (1.73x), vs simdjson DOM 0.107s (1.20x), vs Boost.JSON 0.374s (4.2x), vs Nlohmann 1.266s (14.2x). clang++: DAW 0.085s vs RapidJSON 0.194s (2.28x). simdjson On-Demand is faster than DAW (0.060s g++). The originally cited docs/kostya_benchmark_results.md holds older author-run tables: 0.19s vs RapidJSON 0.53s (i5-5350U) and 0.11s vs 0.26s (i7-7500U, gcc 9.2.1). Those numbers are verified. |
| **Workload** | kostya/benchmarks Json test: parse a big generated JSON file of coordinates and compute simple values from it, timed end-to-end. |
| **Metric** | latency |
| **Hardware** | Intel Xeon E-2324G (kostya/benchmarks environment, Debian forky/sid Docker image) |
| **Compiler and flags** | gcc/g++ 16.1.0 and clang/clang++ 22.1.8 (libc++); kostya common/commands.mk: -O3 -march=native -flto=auto -Wa,-mbranches-within-32B-boundaries, -std=c++23 |
| **Adoption** | 512 stars, 36 forks |
| **Last commit** | 2026-09-09 |
| **Links** | [repository](https://github.com/beached/daw_json_link) · [benchmark](https://github.com/kostya/benchmarks/blob/master/README.md) |

## Verdict

kostya/benchmarks Json test (parse + sum values from a generated coordinates JSON file) run on gcc 16.1.0 / clang 22.1.8 (libc++), -O3 -march=native -flto=auto -std=c++23, Intel Xeon E-2324G: DAW JSON Link 0.089s (g++) / 0.085s (clang++) beats RapidJSON 0.154s/0.194s (1.73x/2.28x), simdjson DOM 0.107s (1.20x), Boost.JSON 0.374s (4.2x) and nlohmann 1.266s (14.2x); simdjson On-Demand (0.060s) is faster than DAW. Memory column shows +0.00 MiB over baseline for DAW versus +175 MiB (simdjson DOM) and +96 MiB (gason), evidencing the no-parser-allocation claim. Older author-run tables (2015-2017 CPUs, gcc 9.2.1) showed 0.19s vs RapidJSON's 0.53s and 0.11s vs 0.26s, both independently confirmed.

## Use it when

- JSON schema is fixed and known at compile time, and you want to build typed C++ objects without an intermediate DOM
- You need to construct immutable or non-default-constructible types straight from JSON via their constructors
- You want strictly bounded/zero parser-side allocation (embedded, latency-sensitive, or `-fno-exceptions` builds via `DAW_JSON_DONT_USE_EXCEPTIONS`)
- You're streaming large arrays or NDJSON/JSON-Lines files and want a thread-partitioning iterator built in
- You also need SAX-style minification, JSON Path lookups, or JSON Schema generation from the same mapping

## Skip it when

- You want a drop-in mutable DOM you can edit and reserialize with zero setup (nlohmann::json-style) rather than declaring a mapping per type
- Compile-time budget is tight: heavy template metaprogramming for the mapping machinery adds to build times
- Raw parse throughput is the only goal and DOM/typed structure doesn't matter: simdjson On-Demand beats it in the same kostya table (0.060s vs 0.089s g++)
- You need certified-accurate float parsing on adversarial inputs: kostya's README flags DAW JSON Link (checked variant) among libraries with known number-parsing inaccuracies (issue #226, still open as a research note citing Clinger's accurate-parsing paper, not confirmed fixed)
- Your team wants minimal per-type boilerplate and doesn't already use C++26 reflection or Boost.PFR/Describe for automatic mapping

## How it is fast

No allocation inside the parser itself (memory shown in kostya's table is +0.00 MiB over baseline, versus +175 MiB for simdjson DOM and +96 MiB for gason); allocation, if any, happens only in the resulting user types. It skips DOM/tree construction entirely, parsing directly to constructor args in declaration order, and backtracks only if struct member order doesn't match JSON key order. Numeric parsing uses the Eisel-Lemire fast path for doubles and the Dragonbox algorithm for float-to-string; optional SSE4.2/AVX2/NEON paths exist for member-skip scanning, though the README says the constexpr non-SIMD path is often faster.

## Compared with alternatives

Pick this over cjson.cpp/json.cpp/Tachyon.JSON/utl::json when you want direct-to-typed-struct parsing (no DOM, constructor-arg based) plus SAX/lazy-pull/NDJSON modes from one mapping, not just a faster nlohmann-shaped DOM. If raw throughput against simdjson On-Demand is the only metric, that (or Tachyon.JSON, which also beats simdjson On-Demand in its own table) is faster than DAW JSON Link here.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | daw::header_libraries and daw::utf_range (both header-only, same author, pulled automatically via CMake FetchContent from extern/CMakeLists.txt) |
| **Minimum toolchain** | C++17 minimum (tested GCC 9-12, Clang 8-14, MSVC 19.29); C++20 enables inline NTTP member names; C++26 static reflection (or Boost.PFR/Boost.Describe adapters) enables automatic mapping without a manual json_data_contract |
| **Platforms** | any C++17 target; optional SIMD member-skip paths for x86 SSE4.2/AVX2 and arm NEON, but README says the default constexpr (non-SIMD) path is generally faster |
| **Thread safety** | Parsing has no shared mutable state across calls; the custom error-handler function pointer (`daw_json_error_handler`) is thread_local, so it must be installed per thread rather than once globally |
| **Drop-in for the baseline** | partial — from_json/to_json call shape resembles RapidJSON's, but every mapped type needs a json_data_contract specialization (or a reflection-based adapter); it is not a header swap |

## Gotchas

- Struct member order should match JSON key order; mismatches force backtracking and slow parsing
- Missing/optional members slow parsing more than explicit nulls do, per the README's performance notes
- Exceptions are on by default (throws daw::json::json_exception); disabling them (or building with -fno-exceptions) falls back to std::terminate unless a custom thread_local handler is installed
- Duplicate JSON member names resolve to an unspecified one unless you explicitly use json_key_value to preserve or order all of them

## Caveats and trade-offs

kostya's README notes that DAW JSON Link (and gason, default RapidJSON) have some number-parsing inaccuracies (daw_json_link issue #226). The 'NoCheck' variant skips structure checks; the cited figures use the checked variant. simdjson On-Demand beats DAW JSON Link in the same table. 'C++ Boost' in the old archived docs tables is Boost.PropertyTree (kostya test_boost.cpp included property_tree before its 2020 rename). The old tables were run on 2015-2017 CPUs, each machine on a different dataset. Win is vs third-party JSON libraries, not the C++ standard library.

Requires describing the JSON schema at compile time via reflection/data-member mapping rather than a drop-in mutable DOM like nlohmann::json; heavy template metaprogramming increases compile times; header-only.

## Maintenance

Actively maintained: last commit on default branch 'release' is 2026-09-09, with pushes as recent as 2026-09-18 on another branch. BSL-1.0 licensed and header-only (two small header-only same-author dependencies), so it is easy to vendor despite the heavier template metaprogramming and per-type mapping cost.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded from B with stronger evidence: the independent kostya/benchmarks README (Json section, updated 2026-07-19) runs json/test_dawjsonlink.cpp. That run states gcc 16.1.0 / clang 22.1.8, the Xeon E-2324G CPU and flags from common/commands.mk (-O3 -march=native -flto=auto -std=c++23; clang uses libc++). DAW JSON Link beats RapidJSON, simdjson DOM, Boost.JSON and nlohmann there.
- **Verifier notes:** Old doc numbers verified exactly. The current independent kostya README gives reproducible A-tier evidence, so I switched benchmark_url and refreshed the numbers. The last commit on default branch 'release' is 2026-09-09; 2026-09-18 is pushed_at from another branch. Stars 512 and BSL-1.0 confirmed.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/beached/daw_json_link>
  - <https://github.com/beached/daw_json_link/blob/release/docs/kostya_benchmark_results.md>
  - <https://github.com/kostya/benchmarks>
  - <https://github.com/kostya/benchmarks/blob/master/README.md>
  - <https://github.com/kostya/benchmarks/blob/master/json/Makefile>
  - <https://github.com/kostya/benchmarks/blob/master/common/commands.mk>
- **Sources the enricher read:**
  - <https://github.com/beached/daw_json_link>
  - <https://github.com/beached/daw_json_link/blob/release/readme.md>
  - <https://github.com/beached/daw_json_link/blob/release/docs/kostya_benchmark_results.md>
  - <https://github.com/beached/daw_json_link/blob/release/extern/CMakeLists.txt>
  - <https://github.com/beached/daw_json_link/blob/release/docs/cookbook/reflection.md>
  - <https://github.com/beached/daw_json_link/issues/226>
  - <https://github.com/beached/daw_json_link/issues?q=performance>
  - <https://github.com/kostya/benchmarks/blob/master/README.md>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/beached/daw_json_link`) · [data/wave1/enrich/raw/github_com_beached_daw_json_link.json](../../../data/wave1/enrich/raw/github_com_beached_daw_json_link.json) (enrichment confidence 0.8)

</details>
