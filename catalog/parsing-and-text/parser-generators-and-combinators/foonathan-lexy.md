# lexy

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Parser generators and combinators](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> C++17 parser combinator DSL that beats PEGTL on JSON validation by avoiding implicit backtracking.

| | |
|---|---|
| **Beats** | PEGTL (taocpp/PEGTL) |
| **Claimed result** | \~1.6x-2.2x lower validation time than PEGTL across the three test files (derived from page data: canada.json lexy median \~2.25ms vs pegtl \~3.65ms [1.62x]; citm_catalog.json lexy \~1.08ms vs pegtl \~2.37ms [2.19x]; twitter.json lexy \~0.75ms vs pegtl \~1.41ms [1.88x]) |
| **Workload** | JSON validation (accept/reject, no DOM construction) of three real-world files from the nativejson-benchmark corpus (canada.json, citm_catalog.json, twitter.json), timed with nanobench |
| **Metric** | latency |
| **Hardware** | 2020 Mac Mini, Apple M1 |
| **Adoption** | 1.3k stars |
| **Last commit** | 2025-10-18 |
| **Links** | [repository](https://github.com/foonathan/lexy) · [benchmark](https://lexy.foonathan.net/benchmark_json/) |

## Verdict

First-party nanobench benchmark (JSON accept/reject validation, no DOM construction) on a 2020 M1 Mac Mini shows lexy beating PEGTL (fetched from its main/develop/master branch at build time, not a pinned release) by \~1.6x-2.2x median latency across canada.json, citm_catalog.json, and twitter.json; compiler and optimization flags are not stated on the page.

## Use it when

- Validating or parsing well-defined text/binary grammars (JSON-like formats, IPv4/config/protocol grammars) where you control both grammar and target C++ types
- You want zero-copy parsing into existing structs/enums instead of building a generic DOM first
- You can require C++17 (ideally C++20) and are fine embedding the grammar as C++ rather than an external grammar file
- Compile-time (constexpr) parsing of literals/config baked into the binary is valuable
- You're already comparing PEG-style combinator libraries and want less implicit backtracking than PEGTL/Boost.Spirit

## Skip it when

- You need a ready-made JSON/XML DOM out of the box — lexy explicitly puts 'implement an efficient container' out of scope, and on the same benchmark page a DOM-oriented library (glaze) beats lexy by \~1.5-2.3x
- Pre-C++17 toolchains, or projects that want a small, familiar template-class grammar style (PEGTL) instead of operator-heavy DSL syntax
- Teams sensitive to compile-time cost of heavy constexpr/template metaprogramming (author states \~2s per JSON-parser TU in debug; isolate lexy into its own TU)
- You need a pinned, independently-run benchmark before adopting on performance grounds alone — this is a first-party nanobench result with no stated compiler/flags
- Full parsing into a data structure is the actual workload — the only public benchmark measures accept/reject validation, not construction cost

## How it is fast

The core idea is explicit, branch-condition-controlled backtracking: rules only backtrack or look ahead when the grammar author says so, unlike PEG engines (PEGTL included) that backtrack implicitly on every ordered choice, re-testing input the programmer didn't intend to re-test. Because output is delivered through callbacks straight into caller-owned types (zero-copy), there's no intermediate DOM allocation/copy step during validation. The library also uses SIMD-width ('SWAR') string/character-class scanning internally (the benchmark's 'lexy no SWAR' variant exists specifically to isolate that contribution).

## Compared with alternatives

No C++ siblings are catalogued in this category yet (its own baseline, PEGTL, isn't itself catalogued as an entry); relative to the Rust combinators here (winnow, chumsky), lexy targets the same 'combinator beats naive/PEG baseline' niche but the comparisons aren't cross-language-comparable — pick lexy specifically when you're in C++17+, want compile-time grammars, and want less implicit backtracking than PEGTL.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the core header-only library (only fundamental stdlib headers like &lt;type_traits&gt;/&lt;cstddef&gt;); a small optional compiled component (lexy_file, from src/input/file.cpp) backs lexy::read_file for file I/O |
| **Minimum toolchain** | C++17 (CMake option LEXY_FORCE_CPP17 pins this; uses C++20 automatically when available); CMake &gt;= 3.8 to configure, &gt;= 3.18 for the top-level build with tests/examples/benchmarks |
| **Platforms** | not documented beyond generic C++17/20 (CI badge present but CI matrix not inspected this session); benchmark hardware was Apple M1 (aarch64), not architecture-restricted |
| **Thread safety** | not documented explicitly; core parsing is constexpr/stateless and writes only into caller-provided objects via callbacks, so independent concurrent parses have no obvious shared mutable state, but the docs make no explicit thread-safety guarantee |
| **Drop-in for the baseline** | partial — explain: same category (PEG-style combinator) as PEGTL but a different DSL style (operator overloading vs templated grammar classes) and a different output model (callbacks into user types vs PEGTL actions), so porting a grammar is a rewrite, not a swap |

## Gotchas

- No generic DOM/tree type ships for JSON-like formats; you must define your own value types and callbacks or accept more manual work than nlohmann/rapidjson-style libraries
- Grammar rules only backtrack/lookahead where you explicitly write branch conditions — porting PEG intuition from PEGTL/Boost.Spirit (which backtrack implicitly) can silently change parsing behavior, not just performance
- Debug-mode compile times are noticeable per translation unit (author-reported \~2s for the example JSON parser); the docs recommend isolating the grammar in its own TU or using dsl::subgrammar to split it
- No open GitHub issues surfaced for 'stack overflow/crash/recursion/performance' in a limited search, so no widely-flagged pathological-input bug was found — absence of evidence, not confirmation of safety on adversarial input

## Caveats and trade-offs

First-party benchmark run by the lexy author, not an independent suite. The page states hardware (M1 Mac Mini) and harness (nanobench) but not the compiler or flags, which keeps it below A. PEGTL, nlohmann/json, rapidjson and glaze were fetched from moving branches (main/develop/master) at build time, not pinned releases. Boost.JSON is optional in CMake (find_package) and has no data series on the page. Same page, derived from its data: glaze validates \~1.5-2.3x faster than lexy on all three files; lexy is \~1.1-1.3x faster than rapidjson and \~3-9x faster than nlohmann/json.

lexy parses via callbacks straight into user-supplied types (zero-copy) rather than a generic DOM; its DSL is more verbose than PEGTL's template-class grammar; requires C++17; the benchmark measures pure validation, not full parsing into a data structure, so results may not generalize.

## Maintenance

Actively maintained (last commit 2025-10-18, \~1.3k stars) and BSL-1.0 licensed; header-only core makes it easy to vendor, though the DSL is more verbose than PEGTL's and requires C++17.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** This is a first-party nanobench benchmark. The code is public (benchmarks/json/ with pegtl.cpp, lexy.cpp and CMakeLists.txt) and the hardware is stated (M1 Mac Mini), but the compiler and flags are not stated on the page, so C.
- **Verifier notes:** I extracted the embedded plotly data (11 samples per series). Medians match the record: canada 2.251 vs 3.649 ms, citm 1.080 vs 2.367 ms, twitter 0.749 vs 1.406 ms, lexy vs PEGTL. Metadata checks out: BSL-1.0, 1257 stars, last commit 2025-10-18 (active, just under 12 months).
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://lexy.foonathan.net/benchmark_json/>
  - <https://github.com/foonathan/lexy>
  - <https://github.com/foonathan/lexy/tree/main/benchmarks/json>
  - <https://github.com/foonathan/lexy/blob/main/benchmarks/json/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/foonathan/lexy>
  - <https://github.com/foonathan/lexy/blob/main/README.adoc>
  - <https://lexy.foonathan.net/benchmark_json/>
  - <https://github.com/foonathan/lexy/blob/main/CMakeLists.txt>
  - <https://github.com/foonathan/lexy/tree/main/src>
  - <https://github.com/foonathan/lexy/tree/main/include/lexy>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/foonathan/lexy`) · [data/wave3/enrich/raw/github_com_foonathan_lexy.json](../../../data/wave3/enrich/raw/github_com_foonathan_lexy.json) (enrichment confidence 0.6)

</details>
