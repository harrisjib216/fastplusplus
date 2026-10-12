# Coost co/json

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> JSON DOM module of the coost C++ base library; first-party numbers claim 1.4-3.6x faster parse/stringify than RapidJSON 1.1.0.

| | |
|---|---|
| **Beats** | RapidJSON |
| **Claimed result** | master readme.md table (us, co/json vs rapidjson, minified twitter.json): win stringify 569 vs 2089 (3.6x), parse 924 vs 2495 (2.7x); mac stringify 783 vs 1289 (1.6x), parse 1097 vs 1658 (1.5x); linux stringify 468 vs 1359 (2.9x), parse 764 vs 1070 (1.4x). The benchmark branch top-level readme.md also compares simdjson (parse / stringify / parse(minimal) / stringify(minimal), us): linux rapidjson 1233.701 / 2503 / 1057.799 / 2243, simdjson 385.3 / 1779 / 351.752 / 2298, co/json 666.979 / 1660 / 457.381 / 981; windows rapidjson 4197.339 / 3008 / 4078.067 / 2216, simdjson 843.06 / 2373 / 607.946 / 2119, co/json 717.444 / 1514 / 623.745 / 993. The benchmark branch benchmark/readme.md gives a third set without simdjson: linux rapidjson 1270 / 2106 / 1127 / 1358 vs co/json 1005 / 920 / 788 / 470; windows rapidjson 4260 / 2472 / 4098 / 2831 vs co/json 1071 / 881 / 943 / 700. |
| **Workload** | Parse and stringify of minified twitter.json (simdjson's jsonexamples/twitter.json), average microseconds per operation, co/json DOM versus RapidJSON Document/Writer. |
| **Metric** | throughput |
| **Hardware** | Not stated: only OS labels win, mac, linux (the log benchmark text in the same branch says its Linux numbers came from the Windows Subsystem for Linux); no CPU model. |
| **Compiler and flags** | Benchmark branch benchmark/xmake.lua builds json_bm with set_optimize("fastest") (per the top-level xmake.lua comments: -O3 on gcc/clang, -Ox on MSVC); libco itself is built by the top-level xmake.lua with set_optimize("fastest") and /MT on Windows but set_optimize("faster") (-O2) on Linux/macOS; C++11; RAPIDJSON_SSE42 defined only if CO_SSE42 is set. Compiler names and versions not stated. |
| **Adoption** | 4.2k stars |
| **Last commit** | 2026-09-28 |
| **Links** | [repository](https://github.com/idealvin/coost) · [benchmark](https://raw.githubusercontent.com/idealvin/coost/master/readme.md) |

## Verdict

First-party only, measured on minified twitter.json against RapidJSON 1.1.0 with default parse flags. The master README reports stringify at 468-783 us vs 1289-2089 us (1.6-3.6x) and parse at 764-1097 us vs 1070-2495 us (1.4-2.7x) across unnamed Windows, macOS and Linux machines, with no CPU or compiler version given. The figures come from pre-4.0 code whose harness exists only on the 2023 benchmark branch, and that harness also showed simdjson parsing faster than co/json on Linux.

## Use it when

- You already build coost (coroutines, flag, log, RPC) and want JSON on the same string and allocator types
- Config files and RPC payloads of small to medium size that you build or inspect through a fluent API
- Stringify-heavy code: serialization shows the largest first-party gains (1.6-3.6x over RapidJSON on minified twitter.json)
- One thread that repeatedly parses and discards documents, where the thread-local node free lists stay warm

## Skip it when

- Raw parse speed: in coost's own harness simdjson parsed faster than co/json on Linux (385 vs 667 us), and the yyjson and simdjson siblings publish numbers with hardware and compiler stated
- Untrusted or strictly conforming input: object keys with escape sequences are not handled, strings are not checked for UTF-8 or raw control characters, and errors return only a null value
- Number-heavy documents (canada.json-style): doubles go through libc strtod and were never benchmarked, since only twitter.json was measured
- Wide objects with many lookups: get() and operator[] do a linear strcmp scan over the members
- You want a standalone JSON dependency: this requires building libco (C++17 on master) rather than dropping in a header

## How it is fast

A non-recursive, goto-driven parser keeps an explicit value stack and builds each array or object at its closing bracket as one contiguous pointer array (objects are stored as flat key/value pairs). Strings are scanned with memchr for the closing quote and the backslash, and an escape-free string is copied once. Whitespace and output escapes use 8-way unrolled table scans. Each value is a 16-byte header allocated from thread-local size-class free lists (16/32/64/128 bytes) backed by coost's co::alloc, so repeated parse-and-free cycles reuse warm memory. Integers use a plain digit loop, doubles use libc strtod, and stringify formats doubles with milo::dtoa (Grisu2).

## Compared with alternatives

Choose co/json only if you already depend on coost and want its fluent json::any API. For speed, yyjson (about 2.3x RapidJSON parse on a stated EPYC 7R32 with gcc 9.3) and simdjson (faster than co/json even in coost's own harness) are the better-evidenced choices; Boost.JSON or glaze cover a standalone DOM or struct mapping.

## Integration

| | |
|---|---|
| **Form** | static lib (part of libco, built with xmake or CMake; shared build possible) |
| **Dependencies** | none external; the JSON module uses coost's own string type and allocator (co::string, co::alloc) |
| **Minimum toolchain** | C++17 on master (xmake set_languages c++17, CMake 3.15+); the benchmarked pre-4.0 code built as C++11. Default non-MSVC flags are -O2 -g; MSVC builds add /fp:fast |
| **Platforms** | Linux, macOS, Windows, FreeBSD; x86, x64, ARM, ARM64 (per README, with CI badges for each OS and for Windows-arm64) |
| **Thread safety** | not documented; parser scratch state and node free lists are thread-local (static __thread Cache\*), and a json::any has no internal locking |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaws behind the RapidJSON numbers (benchmark branch json_bm.cc). The baseline is a vendored RapidJSON 1.1.0 built without RAPIDJSON_SSE42, since CO_SSE42 is never defined in benchmark/xmake.lua. Stringify is timed as one call, not averaged. The largest ratios (Windows, 3.6x/2.7x) likely measure allocators rather than parsing: RapidJSON's parse time rises from about 1070-1270 us on Linux to 4197-4260 us on Windows in the benchmark-branch files (2495 us in the README row), while co/json stays between 667 and 1071 us on both. RapidJSON's per-Document MemoryPoolAllocator mallocs 64 KB chunks through the static MSVC CRT (/MT) on every loop iteration, whereas co/json reuses its thread-local free lists across all 1000 iterations.
- Object keys are found with memchr to the next quote and get no escape processing. A key containing an escaped quote fails to parse, and keys with escapes such as \n or \u00e9 keep the raw escape text. str() then writes keys verbatim, so a key set from code that contains a quote or a control character produces invalid JSON. String values are unescaped and escaped correctly, but the output escape table covers only \r \n \t \b \f, the quote and the backslash, so other control bytes are written raw.
- json::parse returns a null json::any on any error, with no position or message, so a malformed document looks the same as the literal null; use parse_from() and check its bool.
- Doubles are parsed with strtod, which depends on the C locale's decimal point and ignores strtod's end pointer. str(), dbg() and pretty() default to mdp = 16 maximum decimal places, so fixed-notation values with more decimals are rounded on output.

## Known shortcomings

- First-party README numbers vs RapidJSON (stringify 1.6x to 3.6x, parse 1.4x to 2.7x on minified twitter.json) with no CPU or compiler version; stringify timed as a single call; pre-4.0 code; the RapidJSON/simdjson harness lives only on a stale benchmark branch (2023-12-09) that builds a new simdjson parser every iteration, and simdjson is still faster on Linux there (385.3 vs 666.979 us); README and branch give three different number sets.
- Enricher: the baseline is vendored RapidJSON 1.1.0 without SSE4.2; the headline Windows ratios likely measure allocators rather than parsing (RapidJSON parse 4197-4260 us on Windows in the branch files vs 1070-1270 on Linux, co/json 667-1071: RapidJSON mallocs 64 KB chunks per document through the static MSVC runtime while co/json reuses thread-local free lists across all 1000 loops); object keys get no escape handling (an escaped quote in a key fails to parse, keys are written raw), parse errors return plain null, doubles use the locale-dependent strtod, only twitter.json measured.

## Caveats and trade-offs

First-party, partial methodology, so tier C. Table is identical to the v3.0.2 README (tag 2023-11-23), so it predates coost 4.0.0 (tag 2026-09-15) whose API changed (json::any, co::string); master test/jbm.cc now times only co/json, and the RapidJSON/simdjson comparison code is only on the old benchmark branch (last updated 2023-12-09; co::Json, fastring; its top-level readme.md still contains unresolved git merge-conflict markers). The README calls the figures averages, but in benchmark/json_bm.cc the stringify figure is a single timed call after one warm-up, while parse is the mean of 1000 loops. RapidJSON baseline is default Document::Parse with default flags (no in-situ, no SIMD unless CO_SSE42) and its stringify includes building a StringBuffer and copying into std::string. The harness also handicaps simdjson: it constructs a new simdjson::dom::parser inside every parse iteration (re-allocating its buffers each time, against simdjson's documented reuse pattern) and stringifies through std::ostringstream. Even so, simdjson parses faster than co/json on Linux (385.3 vs 666.979 us); co/json is faster only on the Windows run (717.444 vs 843.06 us), where RapidJSON is also about 3.4x slower than on Linux. README and benchmark-branch files give three different numbers for the same rows (e.g. linux parse 764 vs 1070 in the README, 1005 vs 1270 in benchmark/readme.md, 666.979 vs 1233.701 in the branch readme), and benchmark/readme.md says its Linux log numbers came from the Windows Linux subsystem. No CPU, compiler version or RAM stated.

Part of the coost library (co::Json/json::any, fluent API, own allocator and fastring/co::string types), not a standalone single header; DOM only. Benchmark code is public (benchmark branch: benchmark/json_bm.cc, rapidjson.h, simdjson folder, xmake.lua) but is not on master.

## Maintenance

Actively maintained (MIT, 4.2k stars, CMake project version 4.0.0, last commit 2026-09-28 per the verifier), but the JSON numbers are first-party, predate the 4.0 API, and the headline Windows ratios likely reflect RapidJSON's per-document malloc on the MSVC CRT heap rather than parse speed; escaped object keys are not handled.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party numbers only. The master readme.md table (win/mac/linux, co/json vs rapidjson) matches the record exactly; the benchmark code (benchmark branch benchmark/json_bm.cc with benchmark/rapidjson.h) is public, but no CPU model or compiler version is stated anywhere, and the README table itself does not appear in any benchmark-branch results file.
- **Verifier notes:** Record accurate; numbers verified on master readme.md and on both benchmark-branch readme files, harness verified in benchmark/json_bm.cc. Shortcomings: first-party, no CPU/compiler, single-shot stringify timing, simdjson handicapped by per-iteration parser construction yet still faster on Linux, numbers from pre-4.0 code that no longer has the comparison harness on master.
- **Fields the verifier corrected:** `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-71 (wave 1, stdlib decomposition); enricher (wave 1 stdlib seeds, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/idealvin/coost/master/readme.md>
  - <https://github.com/idealvin/coost>
  - <https://github.com/idealvin/coost/commits/master>
  - <https://github.com/idealvin/coost/tree/master/benchmark>
  - <https://github.com/idealvin/coost/branches/all>
  - <https://github.com/idealvin/coost/tree/benchmark>
  - <https://github.com/idealvin/coost/tree/benchmark/benchmark>
  - <https://raw.githubusercontent.com/idealvin/coost/benchmark/readme.md>
  - <https://raw.githubusercontent.com/idealvin/coost/benchmark/xmake.lua>
  - <https://raw.githubusercontent.com/idealvin/coost/benchmark/benchmark/json_bm.cc>
  - <https://raw.githubusercontent.com/idealvin/coost/benchmark/benchmark/readme.md>
  - <https://raw.githubusercontent.com/idealvin/coost/benchmark/benchmark/xmake.lua>
  - <https://raw.githubusercontent.com/idealvin/coost/benchmark/benchmark/rapidjson.h>
  - <https://raw.githubusercontent.com/idealvin/coost/master/LICENSE.md>
  - <https://raw.githubusercontent.com/idealvin/coost/master/test/jbm.cc>
  - <https://github.com/idealvin/coost/tags>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/idealvin/coost/master/readme.md>
  - <https://raw.githubusercontent.com/idealvin/coost/master/xmake.lua>
  - <https://raw.githubusercontent.com/idealvin/coost/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/idealvin/coost/master/LICENSE.md>
  - <https://raw.githubusercontent.com/idealvin/coost/master/include/co/json.h>
  - <https://raw.githubusercontent.com/idealvin/coost/master/include/co/string.h>
  - <https://raw.githubusercontent.com/idealvin/coost/master/src/json.cc>
  - <https://raw.githubusercontent.com/idealvin/coost/master/test/jbm.cc>
  - <https://raw.githubusercontent.com/idealvin/coost/benchmark/readme.md>
  - <https://raw.githubusercontent.com/idealvin/coost/benchmark/xmake.lua>
  - <https://raw.githubusercontent.com/idealvin/coost/benchmark/src/json.cc>
  - <https://raw.githubusercontent.com/idealvin/coost/benchmark/include/co/json.h>
  - <https://raw.githubusercontent.com/idealvin/coost/benchmark/benchmark/json_bm.cc>
  - <https://raw.githubusercontent.com/idealvin/coost/benchmark/benchmark/readme.md>
  - <https://raw.githubusercontent.com/idealvin/coost/benchmark/benchmark/xmake.lua>
  - <https://raw.githubusercontent.com/idealvin/coost/benchmark/benchmark/rapidjson.h>
  - <https://raw.githubusercontent.com/idealvin/coost/benchmark/benchmark/rapidjson/rapidjson.h>
  - <https://raw.githubusercontent.com/idealvin/coost/benchmark/benchmark/rapidjson/allocators.h>
  - <https://github.com/idealvin/coost/issues?q=is%3Aissue+json>
  - <https://github.com/idealvin/coost/issues/353>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/idealvin/coost#json`) · [data/wave1/enrich/raw/github_com_idealvin_coost_json.json](../../../data/wave1/enrich/raw/github_com_idealvin_coost_json.json) (enrichment confidence 0.7)

</details>
