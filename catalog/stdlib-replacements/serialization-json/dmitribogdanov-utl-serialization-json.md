# utl::json (part of the UTL header-only library collection)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [JSON serialization](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++17 JSON library, 2-4x faster than nlohmann::json at parsing and serializing; RapidJSON still wins parsing.

| | |
|---|---|
| **Beats** | nlohmann::json (also PicoJSON; beats RapidJSON on serialization tasks only, loses to it on most parsing tasks) |
| **Claimed result** | Faster than nlohmann::json at parsing: 2.2x on twitter.json (402.89 vs 182.76 op/s), 2.4x on apache_builds.json (2,134.76 vs 881.03 op/s), and about 4x on strings.json and numbers.json (derived from page data). Faster than nlohmann at serializing by about 1.6-1.9x on twitter.json and apache_builds.json (e.g. twitter.json minimized: 834.42 vs 440.27 op/s), 1.5x on numbers.json, and 2.4x on strings.json (derived from page data). Vs RapidJSON, utl::json wins only strings.json parsing and most serialization runs. The author says that an experimental flat-map object type (not the shipped default) 'allowed utl::json to beat RapidJSON on all serializing tasks and significantly closed the gap of database.json parsing'. RapidJSON is still 1.30-1.40x faster at parsing database.json in that run. |
| **Workload** | Parsing and serializing minimized/prettified JSON test files (strings.json, numbers.json, twitter.json, apache_builds.json, database.json) with a benchmark harness comparing utl::json, nlohmann, PicoJSON, and RapidJSON |
| **Metric** | throughput |
| **Adoption** | 336 stars |
| **Last commit** | 2026-09-19 |
| **Links** | [repository](https://github.com/DmitriBogdanov/UTL) · [benchmark](https://github.com/DmitriBogdanov/UTL/blob/master/docs/module_json.md#benchmarks) |

## Verdict

First-party nanobench tables in docs/module_json.md (no compiler, flags, or CPU model given) show utl::json parsing 2.2x faster than nlohmann::json on twitter.json (402.89 vs 182.76 op/s) and 2.4x on apache_builds.json (2,134.76 vs 881.03 op/s), and serializing 1.6-1.9x faster on those same files. RapidJSON parses faster than utl::json on numbers.json (1.29-1.45x), twitter.json (2.07-2.22x), apache_builds.json (1.63-1.72x) and database.json (1.30-1.40x), and roughly ties it at serializing apache_builds.json.

## Use it when

- Already modeling data with std::map/std::vector/std::string and want JSON that interoperates with those containers directly, no custom container API to learn
- Want recursive struct&lt;-&gt;JSON reflection (UTL_JSON_REFLECT macro) without hand-writing serializers
- Currently on nlohmann::json and want a similarly-shaped, header-only replacement that's 2.2-4x faster parsing and 1.6-2.4x faster serializing, without needing RapidJSON/simdjson-class throughput
- Need a tiny dependency footprint: single header, under 1k lines, MIT, no third-party deps
- Workload looks like the benchmarked files (twitter.json/apache_builds.json/strings.json/numbers.json shape) rather than deeply object-keyed documents

## Skip it when

- Baseline to beat is RapidJSON, not nlohmann: RapidJSON parses faster on 3 of 4 benchmarked files (numbers.json, twitter.json, apache_builds.json), only strings.json parsing favors utl::json
- Object-heavy / heavily-keyed documents: object_type is std::map, so map insertion/iteration dominates runtime -- the author names this the library's main perf weak point
- Need SIMD-class throughput (simdjson, Glaze, yyjson): utl::json deliberately avoids intrinsics and compiler-specific code for portability, at the cost of top-end speed
- Need distinct integer vs float JSON numbers: number_type is a single double for every JSON number (open, unaddressed feature request #2), so integers beyond 2^53 lose precision
- Building with Clang + libc++ &lt; 20: falls back to a much slower locale-based istringstream number parser (check UTL_JSON_FROM_CHARS_FALLBACK), narrowing or erasing the published speedup on that toolchain (mostly a macOS issue)

## How it is fast

Single-pass recursive-descent parser with no separate tokenizing stage: node type is decided from the first character inside Parser::parse_node(), so the document is scanned once while the recursive Node tree is built. Numbers go through std::charconv's from_chars/to_chars, with a locale-based istringstream fallback only on libc++ &lt;20 (no floating-point from_chars there). The header's own dev docs state it uses no intrinsics or compiler-specific code anywhere, so the win over nlohmann comes from a leaner single-scan design and std::charconv, not vectorization -- which is also why hand-tuned RapidJSON still beats it on most parsing runs.

## Compared with alternatives

Pick utl::json over cjson.cpp / json.cpp / DAW JSON Link / Tachyon.JSON when the goal is STL-container-backed Node values plus macro-based recursive struct reflection in one sub-1k-line header; pick one of those siblings instead when the target baseline is RapidJSON or simdjson rather than nlohmann, since utl::json's wins are consistent only against nlohmann::json and PicoJSON.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (self-contained single header; nlohmann/PicoJSON/RapidJSON are only benchmark-harness comparisons, not runtime deps) |
| **Minimum toolchain** | C++17; MSVC needs /Zc:preprocessor for the UTL_JSON_REFLECT macro to expand correctly |
| **Platforms** | any -- CI covers Windows, Ubuntu, macOS, FreeBSD; no intrinsics or architecture-specific code in the parser |
| **Thread safety** | Not documented for Node/Parser directly. The header notes its libc++ from_chars fallback is specifically 'thread-safe locale-neutral' (avoiding stod/strtod's global-locale issues), implying the rest of the parser holds no shared mutable state, but no explicit thread-safety guarantee is given. |
| **Drop-in for the baseline** | partial — API shape mirrors nlohmann::json (Node vs json, from_string/to_string) but names and methods differ, so call sites need porting, not just a header swap |

## Gotchas

- object_type is std::map&lt;std::string, Node, std::less&lt;&gt;&gt; — object-heavy JSON pays std::map insertion/iteration cost; documented as the main performance weak point
- number_type is one double for every JSON number, no separate integer type; a feature request for int/float split is open and unresolved (issue #2)
- from_string()/from_file() default recursion_limit=100 to cap stack depth against maliciously deep nesting, throwing std::runtime_error past the limit — raise it if legitimate documents nest deeper
- Clang + libc++ &lt;20 silently swaps in a slower locale-based float parser (no std::from_chars); detect with #ifdef UTL_JSON_FROM_CHARS_FALLBACK before trusting benchmark numbers on that toolchain

## Caveats and trade-offs

No CPU model, compiler, or compiler flags appear on the benchmark page (nanobench tables showing relative %, ms/op, op/s, and err% only), so the methodology is self-reported and partial. The 'relative' column is relative to utl::json, and &gt;100% means faster. RapidJSON beats utl::json on parsing on every file except strings.json: numbers.json 1.29-1.45x, twitter.json 2.07-2.22x, apache_builds.json 1.63-1.72x, database.json 1.30-1.40x. It also roughly ties utl::json at serializing apache_builds.json (100.5%). The consistent win is only against nlohmann and PicoJSON. The database.json/flat-map result uses a configuration the author rejected, so it does not describe the shipped library. The page also warns that Clang/libc++ below version 20 falls back to a much slower number parser (no std::from_chars).

Uses std::map for JSON objects by default, which the author states is the main performance weak point on object-heavy documents; JSON values map onto standard containers (std::map/std::vector/std::string) for STL interoperability rather than a custom optimized container, trading some speed for simplicity.

## Maintenance

Actively developed (repo pushed 2026-09-19) but the published master branch — what a consumer actually pulls — last moved 2025-12-08; MIT-licensed, 336 stars, not a fork, small enough to vendor as one header.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party nanobench tables in docs/module_json.md; the benchmark code (benchmarks/module_json/parse_serialize.cpp) is public, but the page gives no compiler, flags, or CPU model, so it is C.
- **Verifier notes:** The numbers are on the page and belong to the utl::json rows. The serialization range was overstated: the record claimed 1.9-2.4x on twitter/apache, but the page gives 1.6-1.9x. 'Closed most of the parsing gap' was also overstated; the page says 'significantly closed', and RapidJSON is still about 1.3-1.4x faster. The caveat undercounted RapidJSON's parsing wins. Metadata checks out: MIT, 336 stars, not a fork, not archived. The record's last_commit 2026-09-19 is on the dev branch; the default master branch's last commit is 2025-12-08. The repo is active either way. The repo URL is on known_list.txt only because this record was already merged, not as a duplicate under another URL.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/DmitriBogdanov/UTL>
  - <https://github.com/DmitriBogdanov/UTL/blob/master/docs/module_json.md#benchmarks>
  - <https://github.com/DmitriBogdanov/UTL/tree/master/benchmarks/module_json/>
  - <https://github.com/DmitriBogdanov/UTL/blob/master/benchmarks/module_json/parse_serialize.cpp>
  - <https://github.com/DmitriBogdanov/UTL/blob/master/benchmarks/CMakeLists.txt>
  - <https://github.com/DmitriBogdanov/UTL/blob/master/benchmarks/common.hpp>
  - <https://github.com/DmitriBogdanov/UTL/blob/master/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/DmitriBogdanov/UTL>
  - <https://github.com/DmitriBogdanov/UTL/blob/master/README.md>
  - <https://github.com/DmitriBogdanov/UTL/blob/master/docs/module_json.md>
  - <https://github.com/DmitriBogdanov/UTL/blob/master/docs/module_json.md#benchmarks>
  - <https://github.com/DmitriBogdanov/UTL/blob/master/include/UTL/json.hpp>
  - <https://github.com/DmitriBogdanov/UTL/issues>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/dmitribogdanov/utl#serialization-json`) · [data/wave1/enrich/raw/github_com_dmitribogdanov_utl_serialization_json.json](../../../data/wave1/enrich/raw/github_com_dmitribogdanov_utl_serialization_json.json) (enrichment confidence 0.55)

</details>
