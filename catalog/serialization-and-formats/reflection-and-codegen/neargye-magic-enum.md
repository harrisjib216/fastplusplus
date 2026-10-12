# Magic Enum

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Reflection and code generation](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Macro-free C++17 enum reflection (enum to string, string to enum, iteration); compiles faster than conjure_enum at scale.

| | |
|---|---|
| **Beats** | conjure_enum (fix8mt/conjure_enum), another macro-free C++ enum-reflection library |
| **Claimed result** | Compile time in seconds (lower is better), magic_enum vs conjure_enum, all ratios derived from page data: GCC Small 47 vs 97.1 (2.1x), Big 21 vs 81.7 (3.9x), Ideal 8.1 vs 46.8 (5.8x); Clang Small 47 vs 66.8 (1.4x), Big 18 vs 52.9 (2.9x), Ideal 8.7 vs 32 (3.7x); MSVC Big 37 vs 244.9 (6.6x), Ideal 17.9 vs 95.7 (5.3x), Small 80 vs ERROR (conjure_enum hit C1060 compiler out of heap space). Clang object size KB: Small 732 vs 779, Big 1307 vs 1400, Ideal 1051 vs 1123; Clang executable size KB: Small 95 vs 243, Big 168 vs 357, Ideal 134 vs 305. The Large Range case (-1024..1024) timed out (&gt;20 min) for magic_enum on all three compilers (GCC, Clang and MSVC); conjure_enum was Unknown on GCC and timed out on Clang and MSVC. |
| **Workload** | Compile time of one generated translation unit per library and case, each calling the library's to_string once per enum: 200 small enums (16 members, reflection range -128..128), 32 big enums (200 members, -256..256), 200 enums with a large range (16 members, -1024..1024) and 100 enums with an ideal range (50 members, 0..50); each averaged over 10 runs. Object-file and executable sizes measured on Clang only. |
| **Metric** | compile-time |
| **Compiler and flags** | -O3 for GCC and Clang, /Ox for MSVC; the README says the library was tested locally on Windows 10 with Visual Studio 2022 (19.44), GCC 14.2.0 and Clang 20.1.2 but does not tie these versions to the benchmark runs; conjure_enum built with FIX8_CONJURE_ENUM_MINIMAL; magic_enum range set through MAGIC_ENUM_RANGE_MIN/MAX. Source generator: benchmarks/gen.py in ZXShady/enchantum (the timing driver is not published). |
| **Adoption** | 6.2k stars |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/Neargye/magic_enum) · [benchmark](https://github.com/ZXShady/enchantum) |

## Verdict

A rival library's README (ZXShady/enchantum) compiled generated translation units that call enum_name once per enum (200 enums of 16 members, 32 of 200, 100 of 50) at -O3 or /Ox with GCC, Clang and MSVC, averaging 10 runs: magic_enum took 47 s vs conjure_enum 97.1 s on GCC Small, 18 s vs 52.9 s on Clang Big and 37 s vs 244.9 s on MSVC Big, with conjure_enum running out of heap on MSVC Small; magic_enum itself timed out at range -1024..1024 everywhere and lost every row to enchantum. No CPU is stated, the timing script is unpublished and the baseline's own small benchmark shows the two libraries at parity, so this is compile-time evidence only and nothing about run-time speed.

## Use it when

- You need enum to string and string to enum for third-party or legacy enums that you cannot annotate, on C++17 compilers (GCC 9+, Clang 5+, MSVC 2017 15.3+).
- Enums with values inside roughly -128..127, or ones you can give a tight per-enum enum_range, where the probe cost stays small (enchantum's ideal-range case 0..50: about 8-18 s for 100 enums of 50 members).
- You already depend on conjure_enum or a hand-rolled __PRETTY_FUNCTION__ scheme and want shorter builds and smaller binaries: in the enchantum table magic_enum compiles 1.4x to 6.6x faster than conjure_enum and its Clang executables are 2.1x to 2.6x smaller (derived from page data).
- You need breadth: flags, wide-char names, case-insensitive casts, std::format/{fmt} formatters, enum containers, C++20 module target and packaging in vcpkg, Conan, Meson, Bazel and ROS.

## Skip it when

- Compile time matters most: enchantum compiles the same generated files 2.7x to 8.1x faster with its out-of-bounds check disabled (1.1x to 6.4x with its default ENCHANTUM_CHECK_OUT_OF_BOUNDS_BY=2, derived from page data) and produces smaller objects, and simple_enum is faster in most rows (enchantum README).
- Enums with large or scattered values: with a -1024..1024 range magic_enum timed out (&gt;20 min) on GCC, Clang and MSVC for 200 enums in the enchantum benchmark, and values outside the range silently produce empty names.
- Forward-declared enums, enums inside templates (Clang problems per issues #164 and #65), or aliased enumerators (aliases share one name; ShapeKind::Box comes back as ConvexBegin).
- Hot-path parsing of strings into enums with many members unless you define MAGIC_ENUM_ENABLE_HASH: the default enum_cast(string) is a linear compare over all names.
- Large translation units in IDEs: issue #207 reports very slow MSVC IntelliSense after including the header.

## How it is fast

Without C++26 reflection it probes every value in [MAGIC_ENUM_RANGE_MIN, MAGIC_ENUM_RANGE_MAX] (default -128..127) by instantiating a function template and parsing __PRETTY_FUNCTION__/__FUNCSIG__, in 256-wide macro-unrolled blocks (MAGIC_ENUM_FOR_EACH_256) that set a validity bitset, then builds compact static arrays of values and bare enumerator names. Storing only the short identifier, not the namespace-qualified string, is what the enchantum README credits for magic_enum's smaller binaries and faster builds than conjure_enum. At run time, enum_name on a contiguous enum is an O(1) offset index (value minus min); sparse and flag enums fall back to a linear scan, and string-to-enum is a linear name compare unless MAGIC_ENUM_ENABLE_HASH turns both into a constexpr hash switch. Master (since 2026-08-31, unreleased) selects a C++26 std::meta::enumerators_of backend automatically, which removes the range scan where the compiler supports P2996 and expansion statements.

## Compared with alternatives

Pick Magic Enum over Enchantum or simple_enum when you want the most widely packaged and feature-complete option (flags, wide strings, formatters, containers, modules) and your enums fit a small range; pick Enchantum when build time and binary size dominate, and simple_enum when you can add first/last markers to your own enums.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (optional {fmt} for magic_enum_format.hpp) |
| **Minimum toolchain** | C++17; GCC 9+, Clang 5+, MSVC 15.3+ (VS 2017), Xcode 10+; C++20 module target needs CMake 3.28+ |
| **Platforms** | any platform those compilers target (compiler-specific __PRETTY_FUNCTION__/__FUNCSIG__ parsing; unsupported compilers fail to compile unless MAGIC_ENUM_NO_CHECK_SUPPORT is defined) |
| **Thread safety** | not documented; the API is stateless constexpr noexcept functions returning string_views into static tables |
| **Drop-in for the baseline** | partial: same idea and similar operations as conjure_enum, but a different namespace and call names (magic_enum::enum_name vs FIX8::conjure_enum&lt;T&gt;::enum_to_string) and range macros (MAGIC_ENUM_RANGE_MIN/MAX vs FIX8_CONJURE_ENUM_MIN_VALUE/MAX_VALUE) |

## Gotchas

- Harness and baseline caveat: the baseline's own README (fix8mt/conjure_enum, section 9) measures a one-enum, 64-member translation unit and finds parity, Clang 0.3 s vs 0.3 s and MSVC 0.376 s vs 0.343 s (magic_enum about 9% faster), so the 1.4x to 6.6x gaps in the enchantum table only appear with hundreds of enums per TU; that harness also built conjure_enum with FIX8_CONJURE_ENUM_ALL_OPTIMIZATIONS while enchantum used FIX8_CONJURE_ENUM_MINIMAL only.
- The enchantum tables were last edited May to July 2025 (README commits) and do not state the magic_enum version, so at best v0.9.7 or v0.9.8 was measured; the timing driver is not published (benchmarks/gen.py only writes the sources) and the runs were at -O3 or /Ox on the author's Windows 10 machine with no CPU given.
- Range edges: values outside [MAGIC_ENUM_RANGE_MIN, MAGIC_ENUM_RANGE_MAX] return an empty name or nullopt with no warning; (max - min) must stay below UINT16_MAX; flag enums ignore the range macros and never reflect zero.
- Big ranges can hit constexpr step limits ('constexpr evaluation hit maximum step limit'); the docs tell you to raise -fconstexpr-steps, -fconstexpr-ops-limit or /constexpr:steps. Do not mix #include and import magic_enum in one program, and keep the reflection backend setting consistent across TUs.

## Known shortcomings

- Tier C: the only evidence is the compile-time table in the rival enchantum README (beats conjure_enum 1.4x-6.6x; loses to enchantum and simple_enum except MSVC Small where simple_enum takes 186 vs 80 s; Large Range times out on all three compilers); gen.py only generates sources, the timing driver, CPU and versions are not tied to the runs; executable sizes smaller than conjure_enum; no runtime benchmark; niche baseline.
- Enricher (orphaned file): the baseline's own README (fix8mt/conjure_enum section 9) finds parity on a one-enum 64-member translation unit (Clang 0.3 vs 0.3 s, MSVC 0.376 vs 0.343 s), so the 1.4x-6.6x gaps appear only with hundreds of enums per TU, and that harness built conjure_enum with FIX8_CONJURE_ENUM_ALL_OPTIMIZATIONS while enchantum used FIX8_CONJURE_ENUM_MINIMAL; the enchantum tables (May-July 2025) do not state the magic_enum version, the timing driver is unpublished (gen.py writes sources only) and the runs were at -O3 or /Ox on the author's Windows 10 machine with no CPU. Values outside [MAGIC_ENUM_RANGE_MIN, MAGIC_ENUM_RANGE_MAX] return an empty name silently; (max - min) must stay below UINT16_MAX; flag enums ignore the range macros; big ranges hit constexpr step limits. C++26 reflection backend on master since 2026-08-31 with an open g++-16 segfault (#467).

## Caveats and trade-offs

The only numbers found are in a competitor's README (enchantum). Its purpose is to show enchantum beats magic_enum: enchantum compiles 2.7x to 8.1x faster than magic_enum in the same table (for example GCC Small 6.0 s vs 47 s), simple_enum compiles faster than magic_enum in every row except MSVC Small (186 s vs 80 s) and the Large Range rows where magic_enum timed out (GCC Small 21.5 s vs 47 s), and magic_enum's own object and executable sizes are 2.4x to 15.6x larger than enchantum's. magic_enum timed out (&gt;20 min) on the Large Range case with every compiler. The win over conjure_enum is implicit (the README lists conjure_enum as slow to compile with bigger binaries and attributes this to storing namespace-qualified names, although conjure_enum is based on magic_enum's implementation); conjure_enum is a niche baseline, and magic_enum is better read as the incumbent that others beat. benchmarks/gen.py only generates the sources; the timing script, exact command lines, library versions and CPU are not published, and the compiler versions are given only as the author's local test setup, so this is first-party-to-a-rival, tier C. No runtime benchmark exists for magic_enum against std::string_view tables, switch statements or hand-written conversions: the repo has no benchmark directory and Magic Enum's own README claims no speed numbers.

Header-only C++17 (GCC 9+, Clang 5+, MSVC 15.3+). Uses __PRETTY_FUNCTION__ probing over a bounded value range (MAGIC_ENUM_RANGE_MIN/MAX, default -128..128), so enums with larger values need per-enum customization; compile time grows with the range. Not a runtime-speed claim.

## Maintenance

Actively maintained (last commit 2026-10-05, latest release v0.9.8, C++26 reflection backend on master since 2026-08-31 with one open g++-16 segfault report, #467) and MIT-licensed header-only, so it is easy to adopt; treat the speed claim as a build-time comparison against a niche rival, not a reason to prefer it over Enchantum.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The only numbers are a compile-time table in a rival library's README (ZXShady/enchantum); the source generator benchmarks/gen.py is public but the timing driver, exact command lines, library versions and CPU model are not, and the compiler versions are listed only as the author's local test setup, so it cannot be A, and a rival's README is not a well-known independent suite, so not B.
- **Verifier notes:** Numbers match the enchantum README exactly; corrected the Large Range timeout (magic_enum timed out on Clang too, not only GCC and MSVC), the caveat that simple_enum beats magic_enum in every row (MSVC Small is 186 s vs 80 s), and added the executable sizes where magic_enum is also smaller than conjure_enum. enchantum and simple_enum are already verified wave-4 entries that beat magic_enum in this same table; magic_enum itself is a 6.2k-star incumbent with no first-party speed claim. Metadata checked: MIT, 6.2k stars, not a fork, last commit 2026-10-05.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-63 (wave 4); enricher (wave 4)
- **Pages the verifier opened:**
  - <https://github.com/ZXShady/enchantum>
  - <https://raw.githubusercontent.com/ZXShady/enchantum/HEAD/README.md>
  - <https://github.com/ZXShady/enchantum/tree/main/benchmarks>
  - <https://raw.githubusercontent.com/ZXShady/enchantum/HEAD/benchmarks/gen.py>
  - <https://github.com/Neargye/magic_enum>
  - <https://raw.githubusercontent.com/Neargye/magic_enum/HEAD/README.md>
  - <https://github.com/Neargye/magic_enum/commits/master>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Neargye/magic_enum/HEAD/README.md>
  - <https://raw.githubusercontent.com/Neargye/magic_enum/HEAD/doc/limitations.md>
  - <https://raw.githubusercontent.com/Neargye/magic_enum/HEAD/include/magic_enum/magic_enum.hpp>
  - <https://github.com/Neargye/magic_enum>
  - <https://github.com/Neargye/magic_enum/commits/master>
  - <https://github.com/Neargye/magic_enum/releases>
  - <https://github.com/Neargye/magic_enum/issues>
  - <https://github.com/Neargye/magic_enum/issues?q=is%3Aissue+compile+time>
  - <https://raw.githubusercontent.com/ZXShady/enchantum/HEAD/README.md>
  - <https://raw.githubusercontent.com/ZXShady/enchantum/HEAD/benchmarks/gen.py>
  - <https://github.com/ZXShady/enchantum/commits/main/README.md>
  - <https://github.com/fix8mt/conjure_enum>
  - <https://raw.githubusercontent.com/fix8mt/conjure_enum/HEAD/README.md>
  - <https://raw.githubusercontent.com/fix8mt/conjure_enum/HEAD/examples/cbenchmark.cpp>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/neargye/magic_enum`) · [data/wave4/enrich/raw/github_com_neargye_magic_enum.json](../../../data/wave4/enrich/raw/github_com_neargye_magic_enum.json) (enrichment confidence 0.75)

</details>
