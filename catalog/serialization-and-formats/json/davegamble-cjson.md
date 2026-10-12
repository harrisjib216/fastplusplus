# cJSON

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟢 active

> Two-file ANSI C DOM JSON parser/printer; parsed 13 of 14 paper benchmark files faster than nlohmann/json (2019).

| | |
|---|---|
| **Beats** | nlohmann/json (JSON for Modern C++) |
| **Claimed result** | Table 10 (Skylake, GB/s): cJSON is faster than nlohmann/json ('JSON for Modern C++') on 13 of 14 files and ties on mesh (0.06 vs 0.06 GB/s), e.g. gsoc-2018 0.53 vs 0.12 GB/s (\~4.4x), twitter 0.33 vs 0.10 (\~3.3x), citm_catalog 0.36 vs 0.14 (\~2.6x); on number-heavy files the margin is small (canada 0.07 vs 0.05, marine_ik 0.07 vs 0.06, numbers 0.07 vs 0.06, mesh.pretty 0.13 vs 0.11) (derived from page data). cJSON also beats jsoncpp on all 14 files and jsmn on 11 of 14, losing github_events (0.28 vs 0.52), marine_ik (0.07 vs 0.18) and numbers (0.07 vs 0.65) (derived from page data). RapidJSON (default mode) beats cJSON on 13 of 14 files; cJSON is ahead only on gsoc-2018 (0.53 vs 0.51 GB/s); RapidJSON insitu beats cJSON on all 14 (derived from page data). |
| **Workload** | Table 10 of the simdjson VLDB 2019 paper parses 14 real-world JSON files (twitter, canada, citm_catalog, mesh, mesh.pretty, apache_builds, github_events, gsoc-2018, instruments, marine_ik, numbers, random, twitterescaped, update-center) in memory, single-threaded, hyperthreading disabled, on an Intel Core i7-6700 (Skylake), reporting parse throughput in GB/s for cJSON, RapidJSON, nlohmann/json and jsmn. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-6700 (Skylake), 3.4 GHz, single-threaded, hyperthreading disabled |
| **Compiler and flags** | GCC 9.1, -O3 -march=native, Linux |
| **Adoption** | 13k stars (13,011) |
| **Last commit** | 2026-09-16 |
| **Links** | [repository](https://github.com/DaveGamble/cJSON) · [benchmark](https://arxiv.org/abs/1902.08318) |

## Verdict

Table 10 of Langdale and Lemire's simdjson paper (VLDB Journal 2019, arXiv 1902.08318) measured in-memory, single-threaded DOM parsing of 14 files with GCC 9.1 -O3 -march=native on a Skylake i7-6700: cJSON (1.7.10, the pinned submodule) ran 0.06-0.53 GB/s against nlohmann/json's 0.05-0.14 GB/s, winning 13 files and tying on mesh, with the widest gaps on string-heavy gsoc-2018 (0.53 vs 0.12) and twitter (0.33 vs 0.10). The harness excludes cJSON_Delete from the timed region but includes nlohmann's destructor, and the numbers predate 1.7.19's per-number allocation.

## Use it when

- C or C89-only code bases (firmware, embedded, old toolchains) that need parse, modify and print in two vendorable files with swappable malloc/free hooks.
- C++ projects that currently parse string-heavy documents (tweets, API payloads, gsoc-2018-style records) with nlohmann/json and can live with a C API; the 2019 table shows 2.6-4.4x on those files.
- Small configuration or message documents (a few KB, objects with a handful of keys) where a simple mutable DOM matters more than GB/s.
- Output-constrained targets: cJSON_PrintPreallocated prints into a caller buffer with no heap allocation, and CJSON_NESTING_LIMIT caps recursion depth at compile time.

## Skip it when

- Number-heavy documents (canada, marine_ik, numbers, mesh): it roughly ties nlohmann/json at 0.06-0.07 GB/s, jsmn is about 9x faster on numbers, and since 1.7.19 parse_number mallocs a temporary buffer per number (PR #939), which the 2019 numbers (cJSON 1.7.10) do not reflect.
- Throughput-critical parsing: RapidJSON beats it on 13 of 14 files in the same table, and sajson, gason and simdjson are faster on every file.
- 64-bit integers or exact integer round-trips: every number is a double, and valueint is a 32-bit int that saturates at INT_MAX/INT_MIN.
- Large objects or arrays accessed by key or index: lookups walk a linked list (O(n) per key, O(n^2) for indexed array loops), and the maintainers declined a hash table (issue #436).
- Untrusted input where strict validation and prompt security fixes matter: the README says most invalid UTF-8 is passed through, the paper lists cJSON among parsers lacking validation, and CVE-2026-67215/67216 (cJSON_Utils patch recursion, cJSON_Compare CPU cost) are open with no fixed release.

## How it is fast

There is no SIMD and no structural-index pass: it is a byte-at-a-time recursive-descent parser that allocates nodes as it goes, storing arrays and objects as doubly linked lists (child/next/prev) with no key hashing or ordering. Strings are pre-scanned to the closing quote to size a single allocation and then unescaped in one copy; numbers are copied into a temporary buffer and converted with libc strtod, with the locale's decimal point substituted. The paper does not say why this beats nlohmann/json, and its harness times nlohmann's destructor but runs cJSON_Delete outside the timed region, which favors cJSON by an unmeasured amount.

## Compared with alternatives

Pick cJSON over jsmn when you need an owned tree with unescaped strings plus a printer, since jsmn only tokenizes (though jsmn wins on numbers and github_events). Pick it over yyjson, sajson or gason only for C89 portability, a two-file vendor drop, or because it is already in your dependency tree; sajson and gason were faster on every Table 10 file.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (C standard library only: string.h, stdio.h, math.h, stdlib.h, limits.h, ctype.h, float.h, locale.h) |
| **Minimum toolchain** | C89/ANSI C compiler (built with -std=c89); CMake 3.5+ for the CMake build; README says not to compile it as C++ |
| **Platforms** | any with IEEE 754 doubles; CI covers Linux and macOS (GCC and Clang) plus Visual Studio 2013/2015 on AppVeyor |
| **Thread safety** | Not thread safe in general; safe only if cJSON_GetErrorPtr is never used (use return_parse_end instead), cJSON_InitHooks is called before any threads use cJSON, and setlocale is not called while cJSON calls are running. |
| **Drop-in for the baseline** | false — it is a C library with manual ownership (cJSON_Delete, free printed strings) and linked-list nodes, whereas nlohmann/json is a C++ value type; porting means rewriting every access site. |

## Gotchas

- `type` is a bit field; test it with the cJSON_Is\* functions, not ==. Adding an item to an array or object transfers ownership, so deleting it yourself afterwards is a double free.
- cJSON_GetObjectItem is case-insensitive for legacy reasons; use the \*CaseSensitive variants for standard behavior. With duplicate keys only the first match is returned.
- cJSON_Parse ignores trailing data after the first value unless you call cJSON_ParseWithOpts with require_null_terminated=1. Number syntax is whatever strtod accepts from the run of [0-9+-.eE] characters, so non-RFC forms such as leading zeros pass.
- With ENABLE_LOCALES (default ON) parsing and printing read localeconv() for the decimal point. Strings cannot contain NUL or \u0000, and cJSON_PrintPreallocated needs 5 bytes more than the output length.

## Known shortcomings

- Beats nlohmann/json on 13 of 14 files (one tie) and jsmn on 11 of 14 in the simdjson VLDB 2019 paper, but loses to RapidJSON on 13 of 14 (ahead only on gsoc-2018, 0.53 vs 0.51 GB/s). Pick it for portability and simplicity, not speed.
- Maintenance is at risk: on 2026-09-16 a maintainer said there is no commitment to answer issues or security reports and recommended forks (#1080). CVE-2026-67215 and CVE-2026-67216 are open with no fixed release (#1073). In the paper's harness cJSON_Delete is outside the timed region while nlohmann's tree is freed inside it. The paper measured 1.7.10; 1.7.19 mallocs per number (CVE-2023-26819 fix), possibly slower on number-heavy files. Loose validation (strtod number syntax, invalid UTF-8 passed through).

## Caveats and trade-offs

Earlier versions of this record misread Table 10: nlohmann/json is 0.12 GB/s on gsoc-2018 (not 0.14) and 0.06 on mesh (a tie with cJSON, not 0.05), and cJSON beats jsmn on 11 of 14 files, so the seed lead's '11 of 14' was correct. cJSON only wins against RapidJSON on 1 of 14 files (gsoc-2018, 0.53 vs 0.51, a 4% gap), so nlohmann/json (13 wins, 1 tie) is the honest baseline for a 'beats' claim, not RapidJSON. Table 10 gives only two significant digits, so the number-heavy files (canada, marine_ik, mesh, mesh.pretty, numbers; margins 0-0.02 GB/s) are near-ties. Numbers are from 2019 ('latest available version' of each parser, cJSON version not stated); the artifact repo's March 2020 Skylake rerun (results/skylake/comparison, not the paper) has nlohmann slightly ahead on mesh (0.066 vs 0.061 GB/s) while cJSON still leads on the other 13 files. All libraries have changed many times since, so the gap may be different today. nativejson-benchmark (https://github.com/miloyip/nativejson-benchmark) lists cJSON 1.5.0 among its tested libraries, which supports cJSON being a recognized shootout entrant, but its per-library numbers were not extracted and it is cited only as corroboration.

cJSON is a simple DOM-only C parser with no SIMD and doubles for all numeric values (precision/int64 caveats); RapidJSON offers a stricter/faster SAX+DOM API and substantially outperforms cJSON on 13 of the 14 files in the same table, so cJSON should not be pitched as beating RapidJSON in general.

## Maintenance

The last release is 1.7.19 (2025-09-09) and a few fixes have landed since (latest 2026-09-16), but on 2026-09-16 a maintainer posted issue #1080 saying there is no response-time commitment and recommending forks; it is MIT and two files, so vendoring and patching locally is easy.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification A, tier now A.
- **Tier reason:** Table 10 of arXiv 1902.08318 (identical in v4-v7; VLDB Journal 2019) reports cJSON and nlohmann/json ('JSON for Modern C++') GB/s on 14 files with GCC 9.1 -O3 -march=native on an Intel i7-6700 Skylake, and footnote 4 publishes the code: github.com/simdjson/simdjson_experiments_vldb2019 experiments/comparison (Dockerfile FROM gcc:9.1, build.sh/run.sh) driving benchmark/parsingcompetition.cpp and allparsingcompetition in the pinned lemire/simdjson submodule, so tier A stands; the verdict is downgrade only because the claim misquotes the baseline numbers and overstates 'all 14'.
- **Verifier notes:** The tier (A) and the metadata (MIT, 13,011 stars, last commit 2026-09-16, active, not fork/archived) are correct. The verdict is downgrade because the claim was wrong, not the tier: the record quoted wrong nlohmann numbers (gsoc 0.14 should be 0.12; mesh 0.05 should be 0.06, a tie), overstated 'all 14' (it is 13 wins plus a tie), and wrongly said the jsmn count was 10/14 when it is 11/14. The artifact repo's 2019-06 raw results for cJSON, jsmn and RapidJSON match Table 10; nlohmann raw numbers for Table 10 were not in those 2019 files.
- **Fields the verifier corrected:** `claimed_speedup`, `compared_against_cpp_std_directly`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/1902.08318>
  - <https://arxiv.org/pdf/1902.08318>
  - <https://arxiv.org/pdf/1902.08318v3>
  - <https://arxiv.org/pdf/1902.08318v4>
  - <https://arxiv.org/pdf/1902.08318v5>
  - <https://arxiv.org/pdf/1902.08318v6>
  - <https://github.com/DaveGamble/cJSON>
  - <https://github.com/simdjson/simdjson_experiments_vldb2019>
  - <https://github.com/simdjson/simdjson_experiments_vldb2019/tree/master/experiments/comparison>
  - <https://github.com/simdjson/simdjson_experiments_vldb2019/tree/master/results/skylake/comparison>
  - <https://github.com/simdjson/simdjson/tree/ab0e22a3169a038333a3ca9ae922571dbb18f5b1/benchmark>
  - <https://github.com/miloyip/nativejson-benchmark>
- **Sources the enricher read:**
  - <https://github.com/DaveGamble/cJSON>
  - <https://github.com/DaveGamble/cJSON/blob/master/README.md>
  - <https://github.com/DaveGamble/cJSON/blob/master/cJSON.c>
  - <https://github.com/DaveGamble/cJSON/blob/master/cJSON.h>
  - <https://github.com/DaveGamble/cJSON/blob/master/cJSON_Utils.h>
  - <https://github.com/DaveGamble/cJSON/blob/master/CHANGELOG.md>
  - <https://github.com/DaveGamble/cJSON/blob/master/SECURITY.md>
  - <https://github.com/DaveGamble/cJSON/blob/master/CMakeLists.txt>
  - <https://github.com/DaveGamble/cJSON/blob/master/.github/workflows/CI.yml>
  - <https://github.com/DaveGamble/cJSON/blob/master/appveyor.yml>
  - <https://github.com/DaveGamble/cJSON/releases>
  - <https://github.com/DaveGamble/cJSON/compare/v1.7.19...master>
  - <https://github.com/DaveGamble/cJSON/pull/939>
  - <https://github.com/DaveGamble/cJSON/issues/1080>
  - <https://github.com/DaveGamble/cJSON/issues/1073>
  - <https://github.com/DaveGamble/cJSON/issues/436>
  - <https://github.com/DaveGamble/cJSON/issues/1054>
  - <https://github.com/DaveGamble/cJSON/issues/956>
  - <https://github.com/DaveGamble/cJSON/commit/c69134d01746dcf551dd7724b4edb12f922eb0d1>
  - <https://arxiv.org/abs/1902.08318>
  - <https://arxiv.org/pdf/1902.08318v6>
  - <https://github.com/simdjson/simdjson_experiments_vldb2019/tree/master/results/skylake/comparison>
  - <https://github.com/simdjson/simdjson/blob/ab0e22a3169a038333a3ca9ae922571dbb18f5b1/benchmark/parsingcompetition.cpp>
  - <https://github.com/simdjson/simdjson/blob/ab0e22a3169a038333a3ca9ae922571dbb18f5b1/benchmark/benchmark.h>
  - <https://github.com/simdjson/simdjson/tree/ab0e22a3169a038333a3ca9ae922571dbb18f5b1/dependencies>
  - <https://github.com/miloyip/nativejson-benchmark>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/davegamble/cjson`) · [data/wave4/enrich/raw/github_com_davegamble_cjson.json](../../../data/wave4/enrich/raw/github_com_davegamble_cjson.json) (enrichment confidence 0.85)

</details>
