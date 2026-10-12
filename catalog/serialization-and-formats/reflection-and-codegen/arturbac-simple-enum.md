# simple_enum

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Reflection and code generation](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> Header-only C++20 enum-to-string and string-to-enum for bounded enums, with 16-183x less instantiation time than magic_enum's default-range enum_name.

| | |
|---|---|
| **Beats** | magic_enum v0.9.5 enum_name (also reflect::enum_name main of 2024-02-02) |
| **Claimed result** | README table, instantiation time simple_enum vs magic_enum: lorem_ipsum_long (104 enumerators) 12.235 ms vs 199.867 ms (about 16x, derived from page data); lorem_ipsum_short (40) 5.286 vs 178.864 ms (34x); E (15) 2.607 vs 86.089 ms (33x); strong_untyped (3) 0.830 vs 151.590 ms (183x). reflect: 19.282 ms instantiation plus 36.470 ms code generation (55.752 ms total) for the 104-enumerator enum, and 69.216 ms total for strong_untyped. |
| **Workload** | Template instantiation time of one enum_name call per enum, measured with clang -ftime-trace, for four bounded enums (3, 15, 40 and 104 enumerators) built from time_trace/enum_definitions.h. |
| **Metric** | compile-time |
| **Hardware** | AMD Ryzen 9 5900X, Linux desktop, kernel 6.6.11-gentoo-dist |
| **Compiler and flags** | clang 17 with -ftime-trace (README); the time_trace/CMakeLists.txt sets no optimization or language-standard options of its own. |
| **Adoption** | 44 stars |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/arturbac/simple_enum) · [benchmark](https://raw.githubusercontent.com/arturbac/simple_enum/HEAD/README.md) |

## Verdict

First-party README table for simple_enum v0.2.0 (2024), measured with clang 17 -ftime-trace on an AMD Ryzen 9 5900X running Gentoo Linux. It reports the template instantiation time of one enum_name call per enum: 12.2 vs 199.9 ms against magic_enum 0.9.5 for 104 enumerators, 5.3 vs 178.9 ms for 40, 2.6 vs 86.1 ms for 16 (labelled 15), and 0.83 vs 151.6 ms for 3. reflect (main of 2024-02-02) totals 46 to 69 ms including code generation. These are compile-time figures only, magic_enum ran at its default range, and there is no runtime benchmark.

## Use it when

- Codebases with many enums where magic_enum's compile time is a measurable cost and you can annotate each enum with first/last or an adl_enum_bounds function.
- Dense, contiguous enums of any size: the README measures a 104-enumerator enum at about 12 ms of instantiation time, against about 200 ms for magic_enum at its default range.
- Enums whose values lie far outside [-128, 127], for example the README's adl_enum_bounds example starting at -15345953: only the width of the range matters, not where it starts.
- Third-party enums you cannot modify (the info&lt;&gt; specialization, e.g. std::memory_order).
- Projects that already use glaze JSON, std::format or fmt and want enum names in serialization and formatting without hand-written tables.

## Skip it when

- Sparse enums with a wide range: each value between first and last instantiates one se::f&lt;value&gt;(), so an enum spanning 0 to 1,000,000 is impractical. Holes cost compile time and come back as empty names.
- Enums you will not annotate: the unbounded default covers only 0 to 10, values outside it silently give an empty string_view, and issue #34 reports conversion warnings for an 8-value enum because the library casts 8 and 9 into it.
- Flag/bitmask enums: the README still lists 'enum bitmasks support' as planned, unlike magic_enum's flags mode.
- C++17 projects, or builds with CMAKE_CXX_STANDARD below 23: the headers need C++20, and the top-level CMakeLists.txt stops with a FATAL_ERROR 'Minimum required standard is C++23'.
- Toolchains with C++26 static reflection: magic_enum's current docs say it switches to standard reflection automatically there, so the 2024 comparison against magic_enum's __PRETTY_FUNCTION__ scan may no longer hold.

## How it is fast

It uses the same __PRETTY_FUNCTION__/__FUNCSIG__ trick as magic_enum: it instantiates se::f&lt;value&gt;() and parses the enumerator name out of the signature string. It does this only for the values in the declared [first, last] range, so the work grows with the range width. magic_enum 0.9.5's default scan covers [-128, 127], clamped to 0-127 for a uint8_t enum. Only the first value scans for the qualified-name prefix (first_pass). Every later value starts at that saved offset and only searches for the closing ']' (cont_pass). Hard-coded per-compiler offsets and a one-letter namespace (se) keep the strings short. The result is a constexpr array of (pointer, length) pairs, so a runtime enum_name is a range check plus an array index. enum_cast runs a lower-bound search over an index array that is sorted at compile time, using a binary/linear hybrid tuned for about 256 entries.

## Compared with alternatives

No enum-reflection library is catalogued in this category yet; the siblings (Cista++, struct_pack, YAS, bitsery, FBE and others) are serializers. Use simple_enum alongside them when you need enum/string conversion for those formats; it ships glaze integration, and compile time matters more than flag-enum support.

## Integration

| | |
|---|---|
| **Form** | header-only (an optional C++ module build produces a static library) |
| **Dependencies** | none for the core (standard library only); glaze, fmt optional for those integrations |
| **Minimum toolchain** | C++20 for the headers (README), GCC 10+ or Clang 13+ enforced by #error checks, MSVC tested; the repo's own CMake build requires C++23 and CMake 3.28 |
| **Platforms** | any target, but only on GCC, Clang or MSVC (relies on their __PRETTY_FUNCTION__/__FUNCSIG__ layouts; other compilers hit #error) |
| **Thread safety** | not documented; enum_name and enum_cast are noexcept and read only constexpr static tables |
| **Drop-in for the baseline** | partial: enum_name(value) has the same call shape as magic_enum::enum_name, but the namespace differs, enum_cast returns expected&lt;E, enum_cast_error&gt;, and enums outside 0-10 need declared bounds |

## Gotchas

- enum_name returns a string_view into the compiler's __PRETTY_FUNCTION__ string, ending before the ']' and not null-terminated, so do not pass .data() to C APIs. The tables point into one full signature string per value in the range.
- Bug fixes landed on 2026-10-01 after the v0.9.5 release commit (PR #39): before them, the first hole in a sparse range was named "0", enum_cast("0") or enum_cast("") could match an invalid entry, and an index-to-enum lookup narrowed the index before the range check (an int8 index of 200 became -56 and was accepted). Use master after that date or a later tag.
- Benchmark harness flaw: simple_enum runs with exact bounds, but magic_enum runs at its default range: 256 values for the int-based enums and 128 for the uint8_t enum E, which explains E's lower 86 ms. An equal-range magic_enum run (customize::enum_range) is not measured. Each library's four per-enum figures come from one translation unit with a different call order (simple_enum.cc calls lorem_ipsum_long first, magic_enum.cc calls E first), so shared one-time instantiation cost falls on different rows.
- The table cannot be reproduced from the repo at HEAD: time_trace/CMakeLists.txt links magic_enum::magic_enum and reflect::reflect, but no CMake file fetches them, no file adds -ftime-trace, and SIMPLE_ENUM_ENABLE_TIME_TRACE is not a declared option. The magic_enum_enum_cast_tt target links only simple_enum.

## Known shortcomings

- Measures compile time only (clang 17 -ftime-trace, Ryzen 9 5900X): bounded enums vs magic_enum's default untuned range, flags unstated for the 183x ratio; the README says enum E has 15 values while the source defines 16.
- Enricher: magic_enum ran at its default range (256 values; 128 for the uint8_t enum E, which explains its 86 ms) against exact bounds for simple_enum; the two translation units call the enums in different order, so shared instantiation cost lands on different rows; not reproducible at HEAD (time_trace targets link magic_enum and reflect but nothing fetches them and -ftime-trace is not set; the table is still from v0.2.0). PR #39 (2026-10-01) fixed enum_cast matching the hole named '0' and the empty string and out-of-range index narrowing. Lead: fix8mt/conjure_enum.

## Caveats and trade-offs

Measures compiler frontend cost only (template instantiation time from clang -ftime-trace), not runtime lookup speed; the README gives no runtime benchmark. Numbers are for simple_enum v0.2.0 against magic_enum v0.9.5 and reflect main of 2024-02-02 (README, 2024), all since changed, and the README notes an old screenshot is from v0.0.1. Benchmark source is public (time_trace/simple_enum.cc, magic_enum.cc, reflect.cc, enum_definitions.h, CMakeLists.txt) with compiler and CPU named, so it nearly meets tier A, but optimization and standard flags and the build preset are not stated. Only bounded enums are measured: every benchmarked enum declares first/last (or adl_enum_bounds), while magic_enum.cc uses magic_enum's default value range with no enum_range or MAGIC_ENUM_RANGE customization, so magic_enum's cost is roughly constant per enum (151.590 ms for a 3-value enum) and the comparison favours the bounded case; simple_enum's unbounded mode is not measured. The README labels enum E as 15 enumerators but enum_definitions.h defines _1 to _16 (16 values). The reflect row is not comparable per the README (part of its work moves to runtime). The lead's guessed baseline (std::string_view or manual conversion) is not what is measured.

C++20 (tested up to C++23); enum_name and enum_cast need enumeration bounds: first/last members, an adl_enum_bounds function, an info&lt;&gt; specialization, or a default unbounded upper range (default_unbounded_upper_range). Cost is proportional to the number of enumerators for bounded enums. Also ships enum_view, enum_index, std::format and glaze integration. Initial C++ module build mode.

## Maintenance

Active single-maintainer project (44 stars, v0.9.5, bug-fix and clang 23 CI commits on 2026-10-01), BSL-1.0 and header-only so easy to vendor, but the performance table dates from v0.2.0 and has not been regenerated.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table (simple_enum v0.2.0 vs magic_enum v0.9.5 and reflect) with clang 17 -ftime-trace and Ryzen 9 5900X stated and public sources in time_trace/ (simple_enum.cc, magic_enum.cc, reflect.cc, enum_definitions.h, CMakeLists.txt), but optimization/standard flags and build preset are not stated, and the largest ratio (183x) exceeds 50x with flags unstated, so it stays C.
- **Verifier notes:** All README numbers and derived ratios check out (16x, 34x, 33x, 183x); metadata (BSL-1.0, 44 stars, last commit 2026-10-01, not a fork) confirmed. Tier C stands. Shortcomings: compile-time only, bounded enums vs magic_enum's default range without range tuning, 2024 versions, flags unstated, E enumerator count mislabelled.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** first-party compile-time table (verifier); enricher harness reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/arturbac/simple_enum/HEAD/README.md>
  - <https://raw.githubusercontent.com/arturbac/simple_enum/HEAD/time_trace/CMakeLists.txt>
  - <https://raw.githubusercontent.com/arturbac/simple_enum/HEAD/time_trace/simple_enum.cc>
  - <https://raw.githubusercontent.com/arturbac/simple_enum/HEAD/time_trace/magic_enum.cc>
  - <https://raw.githubusercontent.com/arturbac/simple_enum/HEAD/time_trace/reflect.cc>
  - <https://raw.githubusercontent.com/arturbac/simple_enum/HEAD/time_trace/enum_definitions.h>
  - <https://github.com/arturbac/simple_enum>
  - <https://github.com/arturbac/simple_enum/commits>
- **Sources the enricher read:**
  - <https://github.com/arturbac/simple_enum>
  - <https://github.com/arturbac/simple_enum/commits>
  - <https://github.com/arturbac/simple_enum/tree/master/include/simple_enum>
  - <https://github.com/arturbac/simple_enum/issues?q=is%3Aissue>
  - <https://github.com/arturbac/simple_enum/issues/33>
  - <https://github.com/arturbac/simple_enum/issues/34>
  - <https://github.com/arturbac/simple_enum/pull/39>
  - <https://raw.githubusercontent.com/arturbac/simple_enum/HEAD/README.md>
  - <https://raw.githubusercontent.com/arturbac/simple_enum/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/arturbac/simple_enum/HEAD/CMakePresets.json>
  - <https://raw.githubusercontent.com/arturbac/simple_enum/HEAD/cmake/preset-workflow.json>
  - <https://raw.githubusercontent.com/arturbac/simple_enum/HEAD/cmake/unit_test_integration.cmake>
  - <https://raw.githubusercontent.com/arturbac/simple_enum/HEAD/tests/CMakeLists.txt>
  - <https://raw.githubusercontent.com/arturbac/simple_enum/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/arturbac/simple_enum/HEAD/include/simple_enum/simple_enum.hpp>
  - <https://raw.githubusercontent.com/arturbac/simple_enum/HEAD/include/simple_enum/core.hpp>
  - <https://raw.githubusercontent.com/arturbac/simple_enum/HEAD/include/simple_enum/enum_cast.hpp>
  - <https://raw.githubusercontent.com/arturbac/simple_enum/HEAD/time_trace/CMakeLists.txt>
  - <https://raw.githubusercontent.com/arturbac/simple_enum/HEAD/time_trace/simple_enum.cc>
  - <https://raw.githubusercontent.com/arturbac/simple_enum/HEAD/time_trace/magic_enum.cc>
  - <https://raw.githubusercontent.com/arturbac/simple_enum/HEAD/time_trace/reflect.cc>
  - <https://raw.githubusercontent.com/arturbac/simple_enum/HEAD/time_trace/enum_definitions.h>
  - <https://raw.githubusercontent.com/arturbac/simple_enum/HEAD/time_trace/enum_cast_tt.cc>
  - <https://raw.githubusercontent.com/Neargye/magic_enum/master/doc/limitations.md>
  - <https://raw.githubusercontent.com/Neargye/magic_enum/v0.9.5/include/magic_enum/magic_enum.hpp>
  - WebSearch: arturbac simple_enum magic_enum compile time enum_name benchmark
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/arturbac/simple_enum`) · [data/wave4/enrich/raw/github_com_arturbac_simple_enum.json](../../../data/wave4/enrich/raw/github_com_arturbac_simple_enum.json) (enrichment confidence 0.75)

</details>
