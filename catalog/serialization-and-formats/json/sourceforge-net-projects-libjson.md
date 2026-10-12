# libjson (SourceForge)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-2-Clause` · 🔴 abandoned

> Configurable C/C++ JSON DOM library with lazy parsing; about 1.09x faster than JsonCpp in one 2013 MSVC run.

| | |
|---|---|
| **Beats** | JsonCpp |
| **Claimed result** | Visual C++ 11.0 32-bit: 1000 iterations of 500 parsings in 5.2787 to 5.29663 s for libjson vs 5.762 to 5.77978 s for JsonCpp (about 1.09x, derived from page data); libjson lazy-parsing mode 0.478065 to 0.486636 s (about 12x against JsonCpp's full parse, derived from page data, but lazy parsing defers work so it is not like-for-like). RapidJSON is faster than both at 0.961858 to 0.962361 s; large canada.json: libjson 240.289 s vs RapidJSON 7.97 s per 1000 parses (about 30x slower, derived). |
| **Workload** | mloskot/json_benchmark 'small' set: data/one-json-per-line.jsons, 500 sample JSON strings from sub-100 to 500 characters, each parsed into the library's DOM type, 1000 iterations, best and worst of 2 marks; libjson against JsonCpp, RapidJSON (DOM mode), casablanca and JSON Spirit on VC++ 11.0 32-bit. The libjson harness only calls libjson::parse and checks the top-level node type. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E5-2687W @ 3.10GHz, 16 GB RAM, Windows 7 64-bit |
| **Compiler and flags** | Visual C++ 11.0 (32-bit); benchmark programs built with Boost.Build 'b2 variant=release' (no explicit flags listed). libjson is not a target in the Jamroot, so how libjson was built and which JSONOptions.h options were set (JSON_PREPARSE on or off) is not stated. |
| **Adoption** | SourceForge rating 4.8/5 from 47 reviews; 176 downloads per week (SourceForge page, 2026-10-07) |
| **Last commit** | 2012-06-25 |
| **Links** | [repository](https://sourceforge.net/projects/libjson/) · [benchmark](https://github.com/mloskot/json_benchmark) |

## Verdict

On the mloskot/json_benchmark README (2013, Visual C++ 11.0 32-bit, Xeon E5-2687W, Windows 7), 1000 passes over 500 small objects (87,428 bytes per pass) took 5.2787 s for libjson against 5.762 s for JsonCpp (about 1.09x, roughly 16.6 vs 15.2 MB/s, derived from page data) and 0.962 s for RapidJSON, with libjson's build options unpublished. libjson was not run under GCC 4.7, and on canada.json it took 240.289 s per 1000 parses against RapidJSON's 7.97 s, with no JsonCpp row for that compiler.

## Use it when

- Keeping legacy code that already uses libjson (or R's RJSONIO, which vendors it) building, rather than choosing a parser for new work.
- Small ASCII-only messages where you read a few fields and ignore the rest: in lazy mode untouched subtrees cost only the whitespace-stripping copy.
- You want comment-preserving JSON (C and bash style), base64 binary nodes and a push-style stream callback in one BSD-2-Clause library with a plain C ABI.
- Builds that need compile-time feature stripping (read-only or write-only, no iterators, no exceptions) more than raw parse speed.

## Skip it when

- Throughput matters: on the same 2013 page RapidJSON parsed the small set 5.5x faster and canada.json 30x faster (240.289 s vs 7.97 s per 1000 parses, about 9.4 vs 282 MB/s, derived from page data); yyjson, simdjson or RapidJSON are the current choices.
- Non-ASCII text: with JSON_UNICODE off (the default) a \uXXXX escape keeps only its low byte, so \u4e2d silently becomes '-' and \u00e9 becomes a lone 0xE9 byte that is not UTF-8; turning JSON_UNICODE on switches the whole API to wide strings.
- 64-bit integers: every number is stored as a double via std::atof and as_int returns long, so values above 2^53 lose precision and on Windows (32-bit long) as_int truncates above 2^31 (open bug #67).
- Untrusted input or modern toolchains: the last release is from 2012, tickets for crashes on malformed input (#55, #61) and for overload ambiguity under -std=c++11 (#63) are still open, a 2022 forum post reports a GCC 9 std::map allocator static_assert failure, and there is no fuzzing or public VCS.
- Deeply nested or large documents: in lazy mode each level re-scans and copies its children's text on first access, and the eager build was the slowest library tested on canada.json.

## How it is fast

Every parse first copies the input while stripping whitespace and comments and rewriting escaped quotes to a sentinel byte, so later bracket- and quote-matching scans need no escape handling. In the default lazy mode (JSON_PREPARSE off) parse() only checks the outer brackets and wraps the compact copy in a root node; an object or array is split into child substrings (one bracket-matching scan plus one string copy per child) only when first accessed, and numbers go through std::atof only when read. With JSON_PREPARSE on, a recursive-descent validator (JSONPreparse) builds the whole tree up front. There is no SIMD scanning or in-situ parsing; an optional mempool++ pool (JSON_MEMORY_POOL) is the only allocator trick.

## Compared with alternatives

Only when you maintain code that already uses libjson or need its comment-preserving round trips behind a C ABI; for new code yyjson or RapidJSON parse far faster with correct UTF-8 handling, simdjson On-Demand gives validated lazy access, and Parson or json.h cover the small permissive C library niche.

## Integration

| | |
|---|---|
| **Form** | source-drop (compile _internal/Source/\*.cpp into your project and comment out JSON_LIBRARY to get the C++ API) or static/shared lib via the bundled makefile (C interface only) |
| **Dependencies** | none (C++ standard library; bundled mempool++ and libbase64++ headers are used only with optional switches) |
| **Minimum toolchain** | Written for pre-C++11 compilers; the makefile defaults to g++ -O3 -ffast-math -fexpensive-optimizations (-fast on macOS, which clang rejects per a 2015 user review); -std=c++11 breaks overload resolution in 7.6.1 (bug #63) |
| **Platforms** | Any hosted C++ platform; docs list gcc and llvm on OS X and gcc on Linux as fully tested, MinGW and Visual C++ as partially tested |
| **Thread safety** | Not thread-safe by default: JSON_REF_COUNT nodes are copy-on-write and the docs advise turning it off or using JSON_MUTEX_CALLBACKS for multi-threaded use; lazy Fetch mutates mutable members inside const accessors, so concurrent reads of one shared node race, and parsing writes a global used_ascii_one flag. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind the numbers: the published mloskot/json_benchmark benchmark_libjson.cpp cannot produce the README's libjson small-set row. It loads only canada.json (the small-set line is commented out), calls jb::get_json(), which no longer exists at HEAD, and uses libjson::parse, which the shipped JSONOptions.h hides by defining JSON_LIBRARY. The measured build therefore had at least that header edit, probably JSON_PREPARSE turned on as well (240 ms per canada.json parse fits only an eager build), and neither edit is published.
- The 12x 'lazy mode' line (0.478 s) is not a parse: the harness only checks the root node's type, which lazy mode sets from the first character, so it timed a whitespace-stripping copy plus one node allocation per string against JsonCpp's full DOM build.
- The 2013 rows predate commit dff5b86 (2013-06-04), which fixed set_mark: before it the reported lowest time was just the second of the two marks, so rows printed as 'X to X' (libjson.large 240.289 to 240.289) may hide a faster first mark; the libjson and JsonCpp small rows show both marks, so the 1.09x figure is unaffected.
- In lazy mode parse() only checks that the compacted text starts with { or [ and ends with the matching bracket; malformed content inside is not reported at parse time and later surfaces as silently nulled children (JSON_SAFE). Call libjson::is_valid first on untrusted input. Numbers use std::atof, which follows the C locale if the program calls setlocale.

## Known shortcomings

- mloskot/json_benchmark README (VC++ 11.0 32-bit only): 1.09x vs JsonCpp while RapidJSON is 5.5x faster on the same page; the libjson rows are not reproducible from public code (benchmark_libjson.cpp has one commit whose get_json() loaded only canada.json, HEAD calls a missing jb::get_json(), no libjson Jamroot target, JSONOptions.h settings unstated). BSD-2-Clause per libjson_7.6.1.zip License.txt (usability copyable). Last release 2012-06-25, abandoned; GCC 9 build failure reported.
- Enricher: the published benchmark_libjson.cpp cannot produce the README small row because the shipped JSONOptions.h defines JSON_LIBRARY, which hides libjson::parse, so the measured build had unpublished edits; the lazy 0.478 s line is not a parse (the harness checks only the root type, set from the first character, timing a whitespace-strip copy plus node allocation), so the 12x lazy claim is invalid; the 2013 rows predate the set_mark fix dff5b86. Default build keeps only the low byte of \uXXXX escapes, stores numbers as double via std::atof (bug #67), open crash tickets #55/#61, -std=c++11 break #63.

## Caveats and trade-offs

Only numbers are from an independent 2013 hobby benchmark (mloskot/json_benchmark, 39 stars) whose author says it is not maintained and was superseded by Native JSON Benchmark; Native JSON Benchmark itself does not include this libjson (only vincenthz/libjson). The libjson rows are not reproducible from the published code: benchmark_libjson.cpp was never updated after its first commit, its get_json() loaded only canada.json (the small-set line is commented out), it calls a function missing from the current header, and libjson has no Jamroot target, so the small-set libjson run needed an unpublished local edit and an unstated libjson build. libjson 7.6.1's default JSONOptions.h leaves JSON_PREPARSE off, so libjson::parse is lazy by default and the benchmark only inspects the top-level type; the README gives a separate lazy-mode line (0.478065 to 0.486636 s) but never says which build produced the 5.2787 s row. The win over JsonCpp is about 1.09x (derived from page data) on VC++ 11.0 32-bit only; libjson was not measured on GCC 4.7, and on the large canada.json set libjson took 240.289 s vs RapidJSON 7.97 s with no JsonCpp row. The SourceForge page's own claim ('usually runs circles around other JSON libraries') has no numbers. Licence is the 2-clause BSD text (FreeBSD variant with the 'views and conclusions' clause) in License.txt of libjson_7.6.1.zip, Copyright 2010 Jonathan Wallace. Last release libjson_7.6.1.zip was uploaded 2012-06-25 and there is no public VCS; the SourceForge 'Last Update' 2016-11-09 is project-page activity. A 5-year-old SourceForge discussion post reports a GCC 9 build failure (std::map allocator value_type static assertion). This is a different project from vincenthz/libjson. [retier] mloskot/json_benchmark README (VC++ 11.0 32-bit only): 1.09x vs JsonCpp while RapidJSON is 5.5x faster on the same page. The libjson rows are not reproducible from public code: the shipped JSONOptions.h defines JSON_LIBRARY, which hides libjson::parse, so the measured build had unpublished edits (likely JSON_PREPARSE; 240 ms per canada.json fits an eager build); benchmark_libjson.cpp has one commit whose get_json() loaded only canada.json and HEAD calls a missing jb::get_json(). The lazy 0.478 s line is not a parse: the harness checks only the root type, set from the first character, so it timed a whitespace-strip copy plus node allocation and the 12x lazy claim is invalid. The 2013 rows predate the set_mark fix dff5b86 (2013-06-04). Default build keeps only the low byte of \uXXXX escapes, stores numbers as double via std::atof (bug #67); open crash tickets #55/#61, -std=c++11 break #63. BSD-2-Clause per libjson_7.6.1.zip; last release 2012-06-25, abandoned.

C++ library with a C interface, lazy parsing, streaming and DOS protection options, many compile-time switches. Project page calls it 'super-effiecient and usually runs circles around other JSON libraries'.

## Maintenance

Abandoned: last release libjson_7.6.1.zip dates from 2012-06-25, there is no public VCS and about 34 bug tickets are still open (many of them spam); BSD-2-Clause and small enough to vendor (RJSONIO on CRAN still ships a copy), but treat it as legacy code, not as a fast parser.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification B, tier now C.
- **Tier reason:** The numbers are on the independent mloskot/json_benchmark README (VC++ 11.0 32-bit, Xeon E5-2687W, b2 variant=release), but the libjson rows cannot be reproduced from the public code: benchmark_libjson.cpp has a single commit (6593fd4, 2013-04-17) whose get_json() loads only canada.json, at HEAD it calls jb::get_json() which no longer exists in json_benchmark.hpp, and libjson has no Jamroot target, so the small-set harness and libjson's build options (JSONOptions.h, e.g. JSON_PREPARSE) are absent from public sources. That matches the rule that numbers built with flags absent from public sources are tier C; the win is also only 1.09x on one compiler.
- **Verifier notes:** Numbers in claimed_speedup match the README exactly, including the lazy-mode and large-set lines. Downgraded B to C because the libjson rows came from an unpublished harness edit and an unstated libjson build configuration, the margin over JsonCpp is 1.09x on one compiler, and RapidJSON beats libjson 5.5x on the same page. Licence verified from the release zip as BSD-2-Clause, so usability moves to copyable; last code release is 2012-06-25 (abandoned).
- **Fields the verifier corrected:** `license`, `usability`, `last_commit`, `stars_or_usage`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** mloskot/json_benchmark (verifier downgrade B to C); enricher harness reading
- **Pages the verifier opened:**
  - <https://github.com/mloskot/json_benchmark>
  - <https://raw.githubusercontent.com/mloskot/json_benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/mloskot/json_benchmark/HEAD/benchmark_libjson.cpp>
  - <https://raw.githubusercontent.com/mloskot/json_benchmark/HEAD/json_benchmark.hpp>
  - <https://raw.githubusercontent.com/mloskot/json_benchmark/HEAD/Jamroot>
  - <https://raw.githubusercontent.com/mloskot/json_benchmark/HEAD/benchmark_jsoncpp.cpp>
  - <https://raw.githubusercontent.com/mloskot/json_benchmark/HEAD/run_benchmark.bat>
  - <https://raw.githubusercontent.com/mloskot/json_benchmark/6593fd4/json_benchmark.hpp>
  - <https://github.com/mloskot/json_benchmark/commits/master>
  - <https://github.com/mloskot/json_benchmark/commits/master/benchmark_libjson.cpp>
  - <https://github.com/miloyip/nativejson-benchmark/tree/master/src/tests>
  - <https://sourceforge.net/projects/libjson/>
  - <https://sourceforge.net/projects/libjson/files/>
  - <https://sourceforge.net/projects/libjson/files/latest/download>
  - <https://sourceforge.net/p/libjson/activity/>
- **Sources the enricher read:**
  - <https://sourceforge.net/projects/libjson/>
  - <https://downloads.sourceforge.net/project/libjson/libjson_7.6.1.zip>
  - libjson_7.6.1.zip: libjson/JSONOptions.h, libjson/libjson.h, libjson/License.txt, libjson/Documentation.pdf, libjson/makefile, _internal/Source/JSONWorker.cpp, _internal/Source/internalJSONNode.cpp, _internal/Source/internalJSONNode.h, _internal/Source/JSONNode.h, _internal/Source/NumberToString.h, _internal/Source/JSONPreparse.cpp, _internal/Source/JSONDebug.h, _internal/Source/JSONDefs.h, _internal/Source/JSONGlobals.h, _internal/TestSuite/Benchmark/main.cpp, _internal/TestSuite/Benchmark/makefile
  - <https://sourceforge.net/p/libjson/bugs/>
  - <https://sourceforge.net/p/libjson/bugs/55/>
  - <https://sourceforge.net/p/libjson/bugs/61/>
  - <https://sourceforge.net/p/libjson/bugs/63/>
  - <https://sourceforge.net/p/libjson/bugs/65/>
  - <https://sourceforge.net/p/libjson/bugs/67/>
  - <https://sourceforge.net/p/libjson/discussion/>
  - <https://sourceforge.net/p/libjson/discussion/1119662/thread/da2a14760a/>
  - <https://sourceforge.net/p/libjson/files/>
  - <https://raw.githubusercontent.com/mloskot/json_benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/mloskot/json_benchmark/4d3d04b/README.md>
  - <https://raw.githubusercontent.com/mloskot/json_benchmark/c684c4a/README.md>
  - <https://raw.githubusercontent.com/mloskot/json_benchmark/HEAD/benchmark_libjson.cpp>
  - <https://raw.githubusercontent.com/mloskot/json_benchmark/HEAD/json_benchmark.hpp>
  - <https://raw.githubusercontent.com/mloskot/json_benchmark/6593fd4/json_benchmark.hpp>
  - <https://raw.githubusercontent.com/mloskot/json_benchmark/HEAD/Jamroot>
  - <https://raw.githubusercontent.com/mloskot/json_benchmark/HEAD/benchmark_jsoncpp.cpp>
  - <https://raw.githubusercontent.com/mloskot/json_benchmark/HEAD/benchmark_rapidjson.cpp>
  - <https://raw.githubusercontent.com/mloskot/json_benchmark/HEAD/run_benchmark.bat>
  - <https://raw.githubusercontent.com/mloskot/json_benchmark/HEAD/data/one-json-per-line.jsons>
  - <https://raw.githubusercontent.com/mloskot/json_benchmark/HEAD/data/canada.json>
  - <https://github.com/mloskot/json_benchmark/commits/master>
  - <https://github.com/mloskot/json_benchmark/commit/dff5b86>
  - <https://github.com/cran/RJSONIO/tree/master/src>
  - <https://raw.githubusercontent.com/cran/RJSONIO/master/DESCRIPTION>
  - <https://raw.githubusercontent.com/cran/RJSONIO/master/src/libjson/JSONOptions.h>
  - <https://github.com/YaoxiangLi/RJSONIO>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://sourceforge.net/projects/libjson`) · [data/wave4/enrich/raw/sourceforge_net_projects_libjson.json](../../../data/wave4/enrich/raw/sourceforge_net_projects_libjson.json) (enrichment confidence 0.8)

</details>
