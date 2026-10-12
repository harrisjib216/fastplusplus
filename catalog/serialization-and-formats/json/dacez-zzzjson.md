# zzzJSON

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `Public Domain (custom dedication in LICENSE: 'zzzjson is public domain. Do whatever you want with it.'; not a formal OSI/SPDX license)` · 🔴 abandoned

> Single-header C JSON DOM with lazy number parsing and arena allocation; \~1.3x faster parse+stringify than RapidJSON in its own benchmark.

| | |
|---|---|
| **Beats** | RapidJSON |
| **Claimed result** | 'All JSON Above' total time 166ms (zzzjson) vs 220ms (RapidJSON) (\~1.33x); Random Short JSON 38ms vs 56ms (\~1.47x); Random Long JSON 29ms vs 45ms (\~1.55x); No-Number JSON 149ms vs 224ms (\~1.50x); JSON From Taobao 23ms vs 28ms (\~1.22x); JSON From nativejson-benchmark 22ms vs 23ms (\~1.05x, parity; parse alone 18ms vs 11ms, slower) (derived from page data) |
| **Workload** | Parse, stringify and parse+stringify ('All') wall time (ms) in memory over no-number JSON (nonum\*.json), nativejson-benchmark files (canada, citm_catalog, twitter), Taobao JSON (cart, trade), all of these plus json-iterator large-file.json, and random short/long JSON, run via build.sh all |
| **Metric** | latency |
| **Hardware** | Intel i7-6700 @ 3.40GHz, Ubuntu 18.04 (WSL) |
| **Compiler and flags** | G++-7.3, -O3 -std=c++11 -g (build.sh CompilePerformance) |
| **Adoption** | 155 stars; described in README as used at scale inside Tencent |
| **Last commit** | 2020-12-26 |
| **Links** | [repository](https://github.com/dacez/zzzjson) · [benchmark](https://github.com/dacez/zzzjson/blob/master/README.md) |

## Verdict

In the author's harness (build.sh all; G++ 7.3 -O3, i7-6700, Ubuntu 18.04 under WSL) against a 2018-07-25 RapidJSON snapshot built with RAPIDJSON_SSE2 and kParseDefaultFlags, zzzJSON took 166 ms for parse plus stringify on six files (the nativejson-benchmark trio, two Taobao files, json-iterator's large-file.json) vs 220 ms for RapidJSON (240 ms with its numbers-as-strings flag), with most of the gap in stringify (59 vs 119 ms) while parsing was even (95 vs 97 ms) and slower on the nativejson files (18 vs 11 ms). Each file was timed once per process with a millisecond clock, and the 2019 adapter set a 512 KB arena and an 8 KB output buffer even though the Chinese README says default settings were used.

## Use it when

- Edit-and-forward jobs: parse, read or change a few fields, and serialize again. On the README's six-file set, stringify took 59 ms vs RapidJSON's 119 ms because it copies the original text.
- Payloads that are mostly strings and keys. On the no-number files it parsed in 86 vs 128 ms and took 149 vs 224 ms for parse plus stringify.
- Cases where numbers must come back out exactly as they went in: they stay as their original text, so there is no double conversion, and GetNumFast hands you the raw digits to feed your own big-number parser.
- Pure-C code bases that want one header with no dependency beyond libc, and one arena per document that is freed in a single call (the 'Random Short JSON' set of 10,000 small documents took 38 vs 56 ms for parse plus stringify).
- Deeply nested input: parse, stringify and copy are all loops, so deep nesting cannot overflow the call stack.

## Skip it when

- Untrusted input combined with the numeric getters: GetInt/GetLong/GetLongLong/GetDouble copy the number's text into a 128-byte stack buffer without checking its length, so a valid number longer than 127 characters overflows the stack.
- Heavy random access or long-lived documents. ObjGet scans the keys one by one (no hash) and ArrayGet walks a linked list, so both are O(n). Every ObjGet/ArrayGet/Begin/Next/GetDouble call also takes a new block from the arena that is only reclaimed at ReleaseAllocator. Each node is a 72-byte struct on 64-bit.
- Number-heavy data where you need every value as a double. Parsing was slower than RapidJSON on the nativejson-benchmark trio (18 vs 11 ms), every GetDouble is a libc atof call plus an arena allocation, and SetDouble formats with snprintf("%.17g"), so 0.1 is written as 0.10000000000000001.
- Peak throughput. There is no SIMD, and the comparison covers only 2018-era DOM libraries (the vendored RapidJSON snapshot is from 2018-07-25), not simdjson or yyjson.
- Projects that need a maintained dependency with a formal license. There have been no commits since 2020-12, the README's API docs no longer match the header, issue #5 has been open without reply since 2022, and the LICENSE is an informal public-domain note with no SPDX id and no patent grant.

## How it is fast

It uses what the README calls 'parse on use': numbers and strings are checked for well-formedness but kept as pointer-plus-length slices of the input (ParseFast does not even copy the input), so parsing never calls strtod or unescapes a string. The tree is a linked structure (first-child, next, prev, father and end pointers), built in a loop rather than by recursion, whose nodes are bump-allocated from a per-document arena that grows by a factor of zj_DELTA (default 2) and is freed in one call. Stringify walks the tree and memcpy's the original text slices, with no re-escaping and no double-to-text conversion, which is where most of its lead over RapidJSON's Writer comes from. The only other tricks are __builtin_expect branch hints and 4-byte word compares for true/false/null; there is no SIMD.

## Compared with alternatives

Against LJSON (the other C entry that claims to beat RapidJSON) and Jsonifier (measured against simdjson), choose zzzJSON only when you want a public-domain single C header whose lazy numbers round-trip exactly and whose stringify is a plain copy, as in edit-and-forward workloads. The Go (go-json, jsoniter, Sonic, easyjson) and Rust (jiter, simd-json) siblings are for other languages.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (libc only: stdlib, string, stdio, stdint, stdbool) |
| **Minimum toolchain** | C99-level C (stdbool.h, stdint.h, static inline) or C++; the Chinese README says zzzJSON has no compiler requirement; the published numbers used G++ 7.3 with -O3 -std=c++11. Not verified by building. |
| **Platforms** | Only x86-64 Linux (Ubuntu 18.04 under WSL) was tested. The code is plain C apart from unaligned, type-punned uint32_t loads when matching true/false/null (fine on x86-64/aarch64, undefined behavior on strict-alignment targets). It uses __builtin_expect on GCC/Clang and plain branches on other compilers such as MSVC. Document size is capped at 4 GiB because zj_Size defaults to uint32_t (it can be changed with zj_SIZE_TYPE). |
| **Thread safety** | Not documented. From reading the code: Parse and Stringify touch only the Allocator you pass in, so one Allocator per thread works. The Set\*Len\* validators (SetStrLen, SetStrLenFast, SetKeyLen, SetKeyLenFast, SetNumStrLen, SetNumStrLenFast) share a file-static string cache, which makes them unsafe to call from more than one thread. |
| **Drop-in for the baseline** | no |

## Gotchas

- ParseFast copies nothing. Nodes point into your buffer, so it must stay alive and unchanged until ReleaseAllocator; Parse and ParseLen copy the input into the arena first. Strings and keys stay in their escaped form: GetStr/GetStrFast return the escaped text (use GetUnEscapeStr/GetUnEscapeKey to decode), ObjGet compares against the escaped key bytes, and Stringify writes escapes and number spellings back out exactly as they were in the input.
- The number getters are thin wrappers over atoi/atol/atoll/atof, which report no errors or overflow (GetInt on 1.5 quietly returns 1). zj_strToLong/LongLong/Double copy the text into a temporary buffer and then pass the original pointer to libc anyway (issue #5, open). Every one of them does an unchecked memcpy into a char[128].
- zj_stringCache is a file-static pointer. It is allocated from whichever Allocator first calls a Set\*Len\* function and is never reset, so after that Allocator is released, later Set\*Len\* calls write to freed memory.
- The README has drifted from zzzjson.h. Its API list and example use BOOL, True, JSONTYPEARRAY, Size() and zj_SHORT_API, none of which exist in the current header, which uses bool, true, JSONTypeArray, SizeOf and zj_API_MODE. In C, short names such as Value, Parse, Set, Type, Next, Copy and Move are global by default and can collide with your own; in C++ they live in namespace zj. The bench adapter's tuning macro (zj_ALLOCATORINITMEMSIZE) no longer matches the header's zj_ALLOCATOR_INIT_MEMSIZE and is silently ignored.

## Known shortcomings

- The 2019 benchmark adapter used a tuned 512 KB arena rather than defaults. From reading the code: numeric getters memcpy into a fixed char[128] stack buffer without a length check, and a file-static string cache used by Set\*Len\* dangles once its Allocator is freed.

## Caveats and trade-offs

The numbers are 2018-2019 era (the README tables were last touched 2019-04-18) and come from GCC 7.3 on Ubuntu 18.04 under WSL. The repository has had no commits since 2020-12-26. Most of the win is in stringify: parse alone is at parity (95 vs 97ms on All JSON) or slower (18 vs 11ms on the nativejson-benchmark files). zzzJSON's 'parse on use' keeps numbers as text and does not convert them, while RapidJSON (kParseDefaultFlags) converts numbers, so the comparison is not like-for-like on number-heavy data. The 'All' column is timed separately and does not always equal parse plus stringify. Newer leaders (yyjson, simdjson) are not in the comparison. The LICENSE is an informal public-domain dedication with no SPDX id and grants no patent rights.

Pure C, single header, 'parse on use' lazy number handling; no SIMD, so it does not compete with simdjson/yyjson-class parsers, only with DOM libraries like RapidJSON/nlohmann/cJSON

## Maintenance

Abandoned: the last commit (2020-12-26) was a community PR renaming zzz_ to zj_ and the benchmark tables date from 2019-04, but the public-domain-style license and single 2,761-line header make it easy to vendor once you have audited the numeric getters and the Set\*Len\* functions.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** The README tables compare zzzjson with RapidJSON (plus rapidjsonfp and rapidjsonstr) and 8 other C/C++ libraries, and state the CPU (i7-6700 3.40GHz), compiler (G++-7.3) and optimization (O3). The public harness is test/performance/c++/performance_test.cpp with zzzjson_test.h and rapidjson_test.h, built and run by build.sh all (-O3 -std=c++11). This first-party run meets A.
- **Verifier notes:** All four claimed ratios match the README; I added the Taobao and nativejson-benchmark rows so the claim is not cherry-picked. The license was identified from the LICENSE file as a public-domain dedication (usability stays copyable, with 'no patent grant' in caveats). Metadata checks out: 155 stars, last commit 2020-12-26, abandoned, not archived, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `license`, `compared_against_cpp_std_directly`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/dacez/zzzjson>
  - <https://github.com/dacez/zzzjson/blob/master/README.md>
  - <https://github.com/dacez/zzzjson/blob/master/LICENSE>
  - <https://github.com/dacez/zzzjson/blob/master/build.sh>
  - <https://github.com/dacez/zzzjson/blob/master/test/performance/c++/performance_test.cpp>
  - <https://github.com/dacez/zzzjson/blob/master/test/performance/c++/zzzjson_test.h>
  - <https://github.com/dacez/zzzjson/blob/master/test/performance/c++/rapidjson_test.h>
  - <https://github.com/dacez/zzzjson/blob/master/zzzjson.h>
- **Sources the enricher read:**
  - <https://github.com/dacez/zzzjson>
  - <https://github.com/dacez/zzzjson/blob/master/README.md>
  - <https://github.com/dacez/zzzjson/blob/master/READMECHN.md>
  - <https://github.com/dacez/zzzjson/blob/master/zzzjson.h>
  - <https://github.com/dacez/zzzjson/blob/master/zzzjson.hpp>
  - <https://github.com/dacez/zzzjson/blob/master/zzzjson.go>
  - <https://github.com/dacez/zzzjson/blob/master/LICENSE>
  - <https://github.com/dacez/zzzjson/blob/master/build.sh>
  - <https://github.com/dacez/zzzjson/blob/master/test/test.h>
  - <https://github.com/dacez/zzzjson/blob/master/test/performance/c++/performance_test.cpp>
  - <https://github.com/dacez/zzzjson/blob/master/test/performance/c++/zzzjson_test.h>
  - <https://github.com/dacez/zzzjson/blob/master/test/performance/c++/zzzjsonbeta_test.h>
  - <https://github.com/dacez/zzzjson/blob/master/test/performance/c++/rapidjson_test.h>
  - <https://github.com/dacez/zzzjson/blob/master/test/performance/c++/rapidjsonfp_test.h>
  - <https://github.com/dacez/zzzjson/blob/master/test/performance/c++/rapidjsonstr_test.h>
  - <https://github.com/dacez/zzzjson/blob/master/test/conformance/conformance_test.cpp>
  - <https://github.com/dacez/zzzjson/blob/master/sample/c/sample.c>
  - <https://github.com/dacez/zzzjson/blob/master/sample/c++/sample.cpp>
  - <https://github.com/dacez/zzzjson/blob/51201ab/zzzjson.h>
  - <https://github.com/dacez/zzzjson/blob/51201ab/test/performance/c++/zzzjson_test.h>
  - <https://github.com/dacez/zzzjson/issues?q=is%3Aissue+is%3Apr>
  - <https://github.com/dacez/zzzjson/issues/2>
  - <https://github.com/dacez/zzzjson/issues/3>
  - <https://github.com/dacez/zzzjson/issues/5>
  - <https://github.com/dacez/zzzjson/pull/4>
  - <https://github.com/dacez/zzzjson/commits/master>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/dacez/zzzjson`) · [data/wave4/enrich/raw/github_com_dacez_zzzjson.json](../../../data/wave4/enrich/raw/github_com_dacez_zzzjson.json) (enrichment confidence 0.8)

</details>
