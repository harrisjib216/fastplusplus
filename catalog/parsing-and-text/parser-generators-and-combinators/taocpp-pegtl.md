# PEGTL (JSON grammar)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Parser generators and combinators](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> Header-only C++ PEG parser-combinator library; its JSON grammar validates 1.7-5.5x faster than nlohmann::json::accept in lexy's benchmark.

| | |
|---|---|
| **Beats** | nlohmann/json (nlohmann::json::accept validation) |
| **Claimed result** | lexy JSON validation benchmark (M1 Mac Mini, compiler and flags unstated): PEGTL JSON grammar 1.7-5.5x faster than nlohmann::json::accept, with the PEGTL build of unknown pre-2023 version and the baseline converting floats; slower than rapidjson, lexy and glaze on the same page. |
| **Workload** | JSON well-formedness validation of canada.json, citm_catalog.json and twitter.json (nativejson-benchmark data) read into one in-memory buffer; PEGTL contrib json::text grammar over pegtl::memory_input versus nlohmann::json::accept on the same buffer, measured with nanobench. |
| **Metric** | throughput |
| **Hardware** | 2020 Mac Mini with M1 processor |
| **Compiler and flags** | Not stated on the page; harness nanobench v4.3.0 (fetched in lexy benchmarks/CMakeLists.txt); compiler, flags and CMake build type unstated |
| **Adoption** | 2.2k stars |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/taocpp/PEGTL) · [benchmark](https://raw.githubusercontent.com/foonathan/lexy/HEAD/docs/content/benchmark_json.adoc) |

## Verdict

In lexy's nanobench JSON validation benchmark on a 2020 M1 Mac Mini (compiler, flags and build type unstated, 11 samples per series), PEGTL's JSON grammar over an in-memory buffer took 3.65/2.37/1.41 ms on canada/citm_catalog/twitter.json versus 20.20/6.60/2.42 ms for nlohmann::json::accept (5.5x/2.8x/1.7x, derived from page data). The PEGTL version measured is unknown (pre-December-2023 main), and PEGTL itself publishes no benchmarks; the maintainers declined to provide performance data in issue #261.

## Use it when

- Writing a parser for a custom text format, DSL, config or protocol in C++ without a code-generation step (Bison/ANTLR) and without Boost.
- Syntax validation or event-style parsing where you attach actions only to the rules you care about and never build a DOM.
- Projects that want a long-lived, BSL-1.0 dependency with released versions, sanitizer and CodeQL CI, and coverage of Linux, macOS, Windows and Android.
- Reusing one grammar with different action sets (validate, extract, build a parse tree) through template specialization.

## Skip it when

- JSON specifically: on the same lexy benchmark page it is slower than rapidjson SAX, lexy and glaze on all three files (glaze 3.1-4.4x faster, derived from page data); use a dedicated JSON library.
- Grammars that backtrack heavily: there is no memoization (packrat request #35 closed wontfix), so worst-case cost depends entirely on how the grammar is written; the docs tell you to factor out common prefixes.
- Untrusted deeply nested input with the default setup: rules recurse on the C++ stack and depth is unbounded unless you opt into the depth limiter (limit_depth in 3.x, check_depth with input_with_depth on main).
- Debug or -O0 builds where parser speed matters, and MSVC builds that dislike large object files (the install guide warns /bigobj is often needed).
- Codebases that cannot absorb API churn: 4.0.0 (2026-06-07) replaced memory_input/string_input, made parse_error a template and dissolved contrib/, and main is already an unreleased 5.0 requiring C++20.

## How it is fast

Each grammar rule is a type with a static match() function, so a grammar compiles into a hand-written-style recursive-descent parser that the optimizer inlines; the docs say it relies on the compiler for performance and should always be built with inlining enabled. Rules declare a rewind mode so sub-rules can drop their backtracking guards when the caller does not need rewinding, and plain inputs skip line/column bookkeeping. There is deliberately no packrat memoization; the authors argue simple recursive descent usually beats it in practice.

## Compared with alternatives

Choose PEGTL over lexy when you value a 2007-era, widely used library with semver releases and a large rule, action and parse-tree toolkit over raw speed; lexy validated the same JSON files 1.6-2.2x faster on the same page. Against re2c, PEGTL is a full PEG parser rather than a lexer generator; winnow and chumsky are the Rust counterparts.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (ICU optional for Unicode property rules; RTTI used for demangling on compilers other than GCC, Clang and MSVC) |
| **Minimum toolchain** | main (5.0, unreleased): C++20, GCC 11, Clang 13, Visual Studio 2022; 4.x and 3.x branches: C++17; 2.x: C++11 |
| **Platforms** | Linux, macOS, Windows, Android; architecture-independent (no SIMD or intrinsics) |
| **Thread safety** | not documented; grammars are stateless types and per-run state lives in the input and the state objects you pass to parse() |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind the numbers: lexy's benchmarks/json/pegtl.cpp includes tao/pegtl/contrib/json.hpp, constructs pegtl::memory_input and catches the non-template pegtl::parse_error, but PEGTL main dropped memory_input in the input refactor (commit 71e1807, 2023-12-13) and had a templated parse_error by 7ab5fa0 (2025-08-04, the last main commit before the page's 2025-10-13 regeneration); the CMake fetches PEGTL main.zip, so the PEGTL column must come from a cached pre-December-2023 download, the measured version is unknown, and the harness no longer builds as published.
- Unequal work against the baseline: nlohmann::json::accept still converts every floating-point token to a double (and, in older versions, every integer), while PEGTL's json::text only checks number syntax, which plausibly explains much of the 5.5x gap on float-heavy canada.json; nlohmann's current develop lexer has since added accept-only shortcuts (discard_number_values, contiguous bulk number scanning), so the ratios are stale.
- Parse errors are exceptions by default (global failures from must&lt;&gt;, if_must&lt;&gt;, raise&lt;&gt; and the try_catch rules); -fno-exceptions is supported but those rules are unavailable and file I/O errors call std::perror and std::terminate, so validate-only code typically catches parse_error_base (4.x and later) or parse_error (3.x).
- Text inputs track line and column with selectable eol strategies (rule, scan or lazy tracking); plain view/file inputs do not, so choose the input type deliberately when error positions or speed matter.

## Known shortcomings

- lexy JSON validation benchmark run by a competitor (M1 Mac Mini, no compiler or flags, versions unpinned): off-baseline (no Bison, ANTLR, Spirit or nom row) and slower than rapidjson, lexy and glaze on the same page; the win is over nlohmann::json::accept only.
- Enricher: lexy's pegtl.cpp uses pegtl::memory_input, contrib/json.hpp and a non-template parse_error, which PEGTL main removed in 71e1807 (2023-12-13) and templated in 7ab5fa0 (2025-08-04), so the PEGTL column in the 2025-10-13 page came from a cached pre-Dec-2023 download of unknown version and the harness no longer builds against the main.zip it fetches; unequal work: nlohmann accept converts every float to double while PEGTL only checks number syntax, which likely drives the 5.5x on canada.json, and nlohmann develop has since added accept shortcuts. Unbounded recursion depth unless check_depth/limit_depth is enabled; no memoization (#35 wontfix); API churn in 4.0.0; main now C++20.

## Caveats and trade-offs

The benchmark is written and run by the author of lexy, a competing parser library (already catalogued in wave 3), and PEGTL is a comparison column, not the subject; no one claims PEGTL beats nlohmann/json, the ratios are derived from the page's embedded plot data. Off-baseline for its category: the spec's parser-generators-and-combinators baselines are Bison/Flex, ANTLR, Boost.Spirit and nom, and none of them is measured; nlohmann::json::accept is a JSON library's acceptor, not its fast path, and on the same page PEGTL is slower than rapidjson SAX (2.51, 1.44, 0.97 ms), lexy (2.29, 1.08, 0.75 ms) and glaze (1.16, 0.73, 0.32 ms) on all three files. Compiler, flags and build type are not stated, and the benchmark CMake fetches PEGTL main.zip and nlohmann/json develop.zip, so versions are unpinned (page last regenerated 2025-10-13, 'Update benchmarks to include glaze'). Single Apple M1 machine, 11 samples per series. PEGTL docs mention only an internal 5-10% gain of one rule at -O0 (Rules-and-Grammars.md), not a comparison against another library. A 2018 IPSJ study compared PEGTL with Boost.Spirit.X3, cpp-peglib and matcha2 (abstract via search snippet only; per-library numbers not seen). The original category guess 'filesystems-and-io' with stdio/fstream baselines does not fit: PEGTL's file inputs (mmap_input, read_input) have no published comparison against stdio or std::fstream. [retier] Harness pegtl.cpp uses memory_input and non-template parse_error removed from PEGTL main (71e1807, 7ab5fa0); nlohmann develop has since added accept shortcuts; off-baseline (no Bison, ANTLR, Spirit or nom); unbounded recursion depth by default; no memoization (#35).

Zero-dependency header-only PEG parser combinator library (main branch needs C++20, 3.x and 4.x branches C++17); PEGTL's own README makes no speed claim and publishes no benchmark. The result is for the contrib JSON grammar only (no DOM built), so it says nothing about a parse-to-tree workload. Parse errors are raised as exceptions (the benchmark catches pegtl::parse_error).

## Maintenance

Actively maintained (4.0.0 released 2026-06-07, 5.0 in progress on main, 2.2k stars, one open issue) under BSL-1.0 and safe to depend on, but pin a release tag since main breaks APIs and requires C++20.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now C.
- **Tier reason:** Independent measurement: lexy's benchmark (benchmarks/json/pegtl.cpp, nlohmann.cpp, main.cpp, CMakeLists.txt) is run by the author of a competing library, not by PEGTL, with public code and the CPU stated (Apple M1 Mac Mini), but no compiler, flags or build type on the page, so it cannot reach A.
- **Retiered** B to C: Lowered B to C: the independent lexy page's PEGTL column was built from a cached pre-December-2023 download of unknown version (the harness no longer compiles against the main it fetches), and the baseline does more work (nlohmann::json::accept converts floats to double while PEGTL's grammar only checks syntax), so the measurement is neither version-pinned nor like for like.
- **Verifier notes:** Means recomputed from the 11 embedded samples match the record (canada 3.649 vs 20.199 ms, citm 2.367 vs 6.598 ms, twitter 1.406 vs 2.420 ms); pegtl.cpp runs json::text plus eof over memory_input and nlohmann.cpp calls json::accept on the same buffer. Metadata checks out (BSL-1.0, 2.2k stars, last commit 2026-10-03, active). Shortcomings to record: off-baseline (no Bison/ANTLR/Spirit/nom comparison), slower than rapidjson, lexy and glaze on the same page, compiler and flags unstated, unpinned versions.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-61 (wave 11); enricher w11 pair-030
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/foonathan/lexy/HEAD/docs/content/benchmark_json.adoc>
  - <https://raw.githubusercontent.com/foonathan/lexy/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/foonathan/lexy/HEAD/benchmarks/json/CMakeLists.txt>
  - <https://raw.githubusercontent.com/foonathan/lexy/HEAD/benchmarks/json/pegtl.cpp>
  - <https://raw.githubusercontent.com/foonathan/lexy/HEAD/benchmarks/json/nlohmann.cpp>
  - <https://raw.githubusercontent.com/foonathan/lexy/HEAD/benchmarks/json/main.cpp>
  - <https://github.com/foonathan/lexy/commits/main/docs/content/benchmark_json.adoc>
  - <https://github.com/taocpp/PEGTL>
  - <https://github.com/taocpp/PEGTL/commits>
- **Sources the enricher read:**
  - <https://github.com/taocpp/PEGTL>
  - <https://raw.githubusercontent.com/taocpp/PEGTL/HEAD/README.md>
  - <https://raw.githubusercontent.com/taocpp/PEGTL/HEAD/doc/README.md>
  - <https://raw.githubusercontent.com/taocpp/PEGTL/HEAD/doc/Rules-and-Grammars.md>
  - <https://raw.githubusercontent.com/taocpp/PEGTL/HEAD/doc/Inputs-and-Parsing.md>
  - <https://raw.githubusercontent.com/taocpp/PEGTL/HEAD/doc/Changelog.md>
  - <https://raw.githubusercontent.com/taocpp/PEGTL/HEAD/doc/Migration-Guide.md>
  - <https://raw.githubusercontent.com/taocpp/PEGTL/HEAD/doc/Install-Guide.md>
  - <https://raw.githubusercontent.com/taocpp/PEGTL/HEAD/doc/Control-Reference.md>
  - <https://raw.githubusercontent.com/taocpp/PEGTL/HEAD/doc/Extra-Reference.md>
  - <https://raw.githubusercontent.com/taocpp/PEGTL/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/taocpp/PEGTL/main/include/tao/pegtl/example/json.hpp>
  - <https://raw.githubusercontent.com/taocpp/PEGTL/3.x/include/tao/pegtl/contrib/json.hpp>
  - <https://raw.githubusercontent.com/taocpp/PEGTL/3.x/include/tao/pegtl/contrib/limit_depth.hpp>
  - <https://raw.githubusercontent.com/taocpp/PEGTL/71e1807/include/tao/pegtl/inputs.hpp>
  - <https://raw.githubusercontent.com/taocpp/PEGTL/7ab5fa00104eae6c050b9b5c3852c797f6968921/include/tao/pegtl/inputs.hpp>
  - <https://raw.githubusercontent.com/taocpp/PEGTL/7ab5fa00104eae6c050b9b5c3852c797f6968921/include/tao/pegtl/internal/inputs.hpp>
  - <https://raw.githubusercontent.com/taocpp/PEGTL/7ab5fa00104eae6c050b9b5c3852c797f6968921/include/tao/pegtl/parse_error.hpp>
  - <https://raw.githubusercontent.com/taocpp/PEGTL/7ab5fa00104eae6c050b9b5c3852c797f6968921/include/tao/pegtl/contrib/json.hpp>
  - <https://github.com/taocpp/PEGTL/commits/main/include/tao/pegtl/contrib/json.hpp>
  - <https://github.com/taocpp/PEGTL/commits/main/include/tao/pegtl/memory_input.hpp>
  - <https://github.com/taocpp/PEGTL/commits/main/?until=2025-10-13>
  - <https://github.com/taocpp/PEGTL/issues?q=is%3Aissue+performance>
  - <https://github.com/taocpp/PEGTL/issues/261>
  - <https://github.com/taocpp/PEGTL/issues/35>
  - <https://raw.githubusercontent.com/foonathan/lexy/HEAD/docs/content/benchmark_json.adoc>
  - <https://raw.githubusercontent.com/foonathan/lexy/HEAD/benchmarks/json/pegtl.cpp>
  - <https://raw.githubusercontent.com/foonathan/lexy/HEAD/benchmarks/json/nlohmann.cpp>
  - <https://raw.githubusercontent.com/foonathan/lexy/HEAD/benchmarks/json/main.cpp>
  - <https://raw.githubusercontent.com/foonathan/lexy/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/foonathan/lexy/HEAD/benchmarks/json/CMakeLists.txt>
  - <https://github.com/foonathan/lexy/commits/main/benchmarks/json/pegtl.cpp>
  - <https://raw.githubusercontent.com/nlohmann/json/develop/include/nlohmann/detail/input/lexer.hpp>
  - <https://raw.githubusercontent.com/nlohmann/json/develop/include/nlohmann/detail/input/parser.hpp>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/taocpp/pegtl`) · [data/wave11/enrich/raw/github_com_taocpp_pegtl.json](../../../data/wave11/enrich/raw/github_com_taocpp_pegtl.json) (enrichment confidence 0.75)

</details>
