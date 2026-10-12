# ujson (µjson)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Small C++11 UTF-8 JSON DOM library with an re2c scanner; parses about 2x and prints 3.5-4.5x faster than nlohmann/json 2.0.3.

| | |
|---|---|
| **Beats** | nlohmann/json v2.0.3 (as pinned by nativejson-benchmark) |
| **Claimed result** | Independent shootout rows, derived from page data (CSV times summed over the 3 files): parse 37.15 ms vs nlohmann 72.48 ms (1.95x faster; per file canada 25.19 vs 55.59 ms, citm 8.21 vs 9.88 ms, twitter 3.76 vs 7.01 ms); stringify 24.86 vs 87.73 ms (3.5x); prettify 29.28 vs 130.56 ms (4.5x). DOM traversal (Statistics) is slower: 3.02 vs 2.17 ms (1.4x slower). The project's own README makes only the unquantified claim 'Fast UTF-8 conformant parser'. |
| **Workload** | nativejson-benchmark DOM parse, stringify and prettify of canada.json (2199KB), citm_catalog.json (1737KB) and twitter.json (632KB), time summed over the three files, in memory. |
| **Metric** | throughput |
| **Hardware** | MacBook Pro (Retina, 15-inch, Mid 2015), Core i7-4980HQ @ 2.80 GHz |
| **Compiler and flags** | clang 7.0 64-bit on macOS as named in the README (in 2016 this must be Apple clang 7.x, since upstream clang 7.0 shipped in 2018; inference); build/premake5.lua at the sample's commit a4a9f10 (2016-09-09) sets release config -DNDEBUG, premake optimize "Full", and gmake buildoptions -march=native -Wall -Wextra, identical to the current file |
| **Adoption** | Bitbucket repo with no star count; listed in awesome-cpp (JSON) and one of 43 libraries in miloyip/nativejson-benchmark |
| **Last commit** | 2016-10-08 |
| **Links** | [repository](https://bitbucket.org/awangk/ujson) · [benchmark](https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv) |

## Verdict

In Milo Yip's nativejson-benchmark sample of 2016-09-09 (clang 7.0 64-bit on macOS, premake optimize Full with NDEBUG and -march=native, Core i7-4980HQ), ujson snapshot 0d6259e parsed canada, citm_catalog and twitter in 37.15 ms total against 72.48 ms for nlohmann/json 2.0.3 (1.95x), stringified in 24.86 vs 87.73 ms (3.5x) and prettified in 29.28 vs 130.56 ms (4.5x), while DOM traversal was 1.4x slower and parse memory up to 6.5x higher. The current code (65df934) has not been measured.

## Use it when

- Legacy C++11 code that wants a small, readable, MIT-licensed DOM parser and writer with strict UTF-8 validation, built with clang/libc++ or MSVC.
- Serialization-heavy jobs on moderate documents where stringify/prettify speed matters more than lookup speed (24.9 ms stringify vs 87.7 ms for nlohmann 2.0.3 on the three shootout files).
- Configuration or message data you treat as immutable values and pass by value between threads (shared_ptr payloads, no mutation).
- Read-once documents whose objects are small enough that sorted-vector binary search is fine.

## Skip it when

- Anything built with GCC/libstdc++ 5 or newer without first testing it: the header assumes libstdc++ strings are copy-on-write and relocates them with memcpy (see gotchas).
- Untrusted input: the parser is unbounded recursive descent (deep nesting can overflow the stack), and the library has had no fixes since 2016-10-08.
- Data with 64-bit integers or exact integer round-trips: every number is a double, so 1234567890123456789 comes back as 1.2345678901234568e18 and -0.0/0.0 print as -0/0 (nativejson-benchmark roundtrip 18/27).
- Large numeric arrays or memory-constrained parsing: the measured build used 34.4 MB for canada.json against nlohmann's 5.3 MB, and RapidJSON, yyjson or simdjson parse several times faster.
- Code that traverses or queries the DOM a lot: tree statistics were 1.4x slower than nlohmann (3.02 vs 2.17 ms) because every type test is a virtual call and string access uses dynamic_cast.

## How it is fast

The tokenizer is a re2c-generated DFA that validates UTF-8 (including \u escapes and surrogate pairs) while it scans, so strings are copied without a second validation pass; with SSE2 it skips whitespace and copies escape-free string runs 16 bytes at a time (_mm_cmpeq_epi8 + movemask). Numbers go through Google's double-conversion (StringToDouble / ToShortest) instead of strtod/printf. Values use a small-object buffer (null, bool, double and, on libc++/MSVC, strings up to 22/15 bytes stay inline) and arrays, objects and long strings sit behind std::shared_ptr, so copies only bump a reference count; the writer appends into one std::string.

## Compared with alternatives

Against taoJSON (41.2 ms parse) and udp/json-parser (47.3 ms) on the same shootout it parses a little faster (37.2 ms) and stringifies faster than both, but RapidJSON, json.h, yyjson and simdjson are far faster and still maintained; pick ujson only for its small immutable-value API and strict UTF-8 validation, and prefer taoJSON or Boost.JSON for new code.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | bundled double-conversion 1.1.5 (BSD-3-Clause amalgamation); re2c only if you edit ujson.re2c; Catch for the tests |
| **Minimum toolchain** | C++11 with RTTI (string_cast uses dynamic_cast); README tables list clang 3.4 (Xcode 5.1.1), gcc 4.8.3 and VS2013; the CMake script needs CMake 2.8 policies and downloads re2c 0.13.5 from SourceForge |
| **Platforms** | any for the scalar path; SSE2 fast paths on x86/x86-64 (GCC/Clang __SSE2__, MSVC x64 or /arch:SSE2); only libc++, MSVC STL and libstdc++ are recognised (other standard libraries hit #error) |
| **Thread safety** | README: values are immutable and arrays/objects/long strings are shared through std::shared_ptr, so passing a ujson::value by value to another thread is race-free; no other guarantees documented |
| **Drop-in for the baseline** | no |

## Gotchas

- find(object, name) and at(object, name) are a bare std::lower_bound with no equality check: for a missing key, find returns the next larger key instead of end(), and at only throws when the key would sort after every member, despite the README saying at 'behaves like std::map::at'. Compare it-&gt;first yourself.
- By code reading (not executed): with libstdc++ (__GLIBCXX__) the header picks its 'ref-counted string' path and stores a std::string inline, but moves, swaps and the stable_sort of object members relocate values with memcpy. GCC 5+ libstdc++ defaults to the SSO std::string, whose data pointer points into the object itself, so a moved short string keeps pointing at the old storage and its destructor can free a non-heap pointer. The independent benchmark only built it with clang/libc++ on macOS, where strings use ujson's own inline buffer.
- The measured snapshot (0d6259e, 2015-04-12) reserved 16 slots in every parsed array and object, which explains the 34.4 MB canada.json footprint (about 56k two-number arrays at 16 x 32-byte values, inferred from code and page data); the author removed the reserve in 65df934 on 2016-10-08 ('slight reduction in parse speed') and the benchmark's sample was never rerun. Escaped '/' was also unsupported in that snapshot (pass01 failure, fixed in 3d1852b).
- Objects are stable-sorted on construction, so output key order differs from input, duplicate keys are kept side by side, and every parsed object pays a sort plus a temporary buffer.

## Known shortcomings

- nativejson-benchmark 2016 CSV (parse 1.95x nlohmann v2.0.3; flags confirmed at sample commit a4a9f10) measured the 2015-04-12 snapshot 0d6259e; a later commit trades parse speed for memory. DOM traversal is slower, parse memory 34 MB, roundtrip 18/27. Abandoned.
- Code-reading bugs: find/at do a bare lower_bound with no equality check, so a missing key returns the next key and at() rarely throws; with libstdc++ on GCC 5+ the header assumes COW strings and moves values with memcpy, leaving SSO strings dangling (the benchmark built it only with clang/libc++). The measured snapshot 0d6259e reserved 16 slots in every array and object, which explains the 34.4 MB canada.json figure; removed in 65df934 and the benchmark was never rerun. The pass01 failure was missing '\/' support, fixed in 3d1852b. No depth limit; numbers are double only.

## Caveats and trade-offs

Numbers come from the single 2016-09-09 sample run of nativejson-benchmark (by Milo Yip, RapidJSON's author, independent of ujson). At that commit the ujson submodule was pinned to 0d6259e (2015-04-12); the author's later commits of 2016-09-10 (escaped slash fix, int printing) and 2016-10-08 'Greatly reduce memory usage at the cost of slight reduction in parse speed' were never measured, although the benchmark's master now pins 65df934, so the current ujson parses somewhat slower than the sample shows. Baseline nlohmann/json is v2.0.3 (submodule c8d01fa), many releases behind the current library. ujson trails cJSON (24.67 ms), RapidJSON (7.93 ms) and ujson4c (8.95 ms) on parse and is slower than nlohmann on DOM traversal (Statistics 3.02 vs 2.17 ms); its parse memory is high (34.4 MB after parsing canada.json against nlohmann's 5.3 MB). Conformance in the same suite: parse validation 33/34 (fails pass01), parse double 66/66, parse string 9/9, roundtrip 18/27, against nlohmann 34/34, 66/66, 9/9, 23/27. Not compared against libstdc++, libc++ or MSVC STL (no std JSON exists). Project has no benchmark of its own; Bitbucket repo with no star count. [retier] Measured snapshot 0d6259e pre-allocated 16 slots per container (removed in 65df934, not rerun); built only with clang/libc++ (libstdc++ COW assumption breaks SSO strings); find/at return the next key for a missing key; no depth limit; numbers are double only.

Much higher memory than nlohmann in the same run: parse result 34.37 MB vs 5.29 MB on canada.json (6.5x), 16.23 MB vs 3.05 MB on citm_catalog.json. Four-file amalgamation (ujson.hpp, ujson.cpp, double-conversion.h, double-conversion.cc); scanner generated by re2c; C++11; objects are sorted vectors with binary-search lookup; UTF-8 only; code size 126,996 bytes vs nlohmann 42,132 bytes in the benchmark's jsonstat executable.

## Maintenance

Abandoned since 2016-10-08 (12 commits, issue tracker no longer served by Bitbucket); MIT and only four source files, but treat the libstdc++ string path and the find/at lookup as bugs to fix before vendoring.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now C.
- **Tier reason:** Independent nativejson-benchmark suite: harness code public (src/tests/ujsontest.cpp against src/tests/nlohmanntest.cpp, build/premake5.lua), compiler stated (clang 7.0 64-bit on macOS), flags in premake5.lua at the sample's own commit a4a9f10 (2016-09-09: NDEBUG, optimize Full, -march=native) and CPU stated (Core i7-4980HQ); the CSV rows for 'ujson (C++)' and 'Nlohmann (C++11)' sum exactly to the record's 37.15 vs 72.48 ms parse, 24.86 vs 87.73 ms stringify, 29.28 vs 130.56 ms prettify and 3.02 vs 2.17 ms statistics.
- **Retiered** A to C: The nativejson-benchmark numbers were measured on snapshot 0d6259e, which reserved 16 slots in every array and object (explaining the 34.4 MB canada.json figure); that reservation was removed in 65df934 and the benchmark was never rerun, so the published numbers describe code that no longer exists (numbers-before-later-fix precedent). The library also has lookup bugs (find/at return the next key for a missing key) and a libstdc++ memcpy-move hazard outside the measured path.
- **Verifier notes:** Numbers verified row by row against the shared CSV (this project's 'ujson (C++)' row, not ujson4c). Flags confirmed at the sample commit, so the 'assumed to match' hedge is removed. Shortcomings: 2016 single run on a 2015 ujson snapshot that the author later slowed for memory, stale nlohmann v2.0.3 baseline, slower DOM traversal, high parse memory, 18/27 roundtrip conformance, abandoned since 2016-10-08.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** nativejson-benchmark CSV (verifier); enricher (wave 4)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/README.md>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/sample/conformance.csv>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/build/premake5.lua>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/a4a9f10f41c515d6abb0f019ab9f5d021ed4bb9e/build/premake5.lua>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/a4a9f10f41c515d6abb0f019ab9f5d021ed4bb9e/src/tests/ujsontest.cpp>
  - <https://github.com/miloyip/nativejson-benchmark/commits/master/sample/performance_Corei7-4980HQ@2.80GHz_mac64_clang7.0.csv>
  - <https://github.com/miloyip/nativejson-benchmark/commits/master/build/premake5.lua>
  - <https://github.com/miloyip/nativejson-benchmark/tree/master/thirdparty>
  - <https://github.com/miloyip/nativejson-benchmark/tree/a4a9f10f41c515d6abb0f019ab9f5d021ed4bb9e/thirdparty>
  - <https://api.bitbucket.org/2.0/repositories/awangk/ujson>
  - <https://api.bitbucket.org/2.0/repositories/awangk/ujson/commits?pagelen=5>
  - <https://api.bitbucket.org/2.0/repositories/awangk/ujson/src/master/LICENSE.md>
  - <https://api.bitbucket.org/2.0/repositories/awangk/ujson/src/master/README.md>
- **Sources the enricher read:**
  - <https://api.bitbucket.org/2.0/repositories/awangk/ujson>
  - <https://api.bitbucket.org/2.0/repositories/awangk/ujson/src/master/>
  - <https://api.bitbucket.org/2.0/repositories/awangk/ujson/src/master/README.md>
  - <https://api.bitbucket.org/2.0/repositories/awangk/ujson/src/master/CMakeLists.txt>
  - <https://api.bitbucket.org/2.0/repositories/awangk/ujson/src/master/LICENSE-3RD-PARTY.md>
  - <https://api.bitbucket.org/2.0/repositories/awangk/ujson/src/master/ujson/ujson.hpp>
  - <https://api.bitbucket.org/2.0/repositories/awangk/ujson/src/master/ujson/ujson.re2c>
  - <https://api.bitbucket.org/2.0/repositories/awangk/ujson/src/master/ujson/ujson.cpp>
  - <https://api.bitbucket.org/2.0/repositories/awangk/ujson/src/master/ujson/CMakeLists.txt>
  - <https://api.bitbucket.org/2.0/repositories/awangk/ujson/src/master/test/test.cpp>
  - <https://api.bitbucket.org/2.0/repositories/awangk/ujson/src/master/test/fuzz.cpp>
  - <https://api.bitbucket.org/2.0/repositories/awangk/ujson/commits?pagelen=50>
  - <https://api.bitbucket.org/2.0/repositories/awangk/ujson/diff/65df934>
  - <https://api.bitbucket.org/2.0/repositories/awangk/ujson/diff/dbdffc7>
  - <https://api.bitbucket.org/2.0/repositories/awangk/ujson/issues?pagelen=50>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/sample/conformance.csv>
  - https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/sample/conformance_ujson%20(C%2B%2B).md
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/src/tests/ujsontest.cpp>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/a4a9f10f41c515d6abb0f019ab9f5d021ed4bb9e/src/tests/ujsontest.cpp>
  - <https://github.com/miloyip/nativejson-benchmark/issues?q=ujson>
  - <https://github.com/miloyip/nativejson-benchmark/pull/69>
  - <https://github.com/miloyip/nativejson-benchmark/issues/102>
  - <https://github.com/miloyip/nativejson-benchmark/commits/master/sample/conformance.csv>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://bitbucket.org/awangk/ujson`) · [data/wave4/enrich/raw/bitbucket_org_awangk_ujson.json](../../../data/wave4/enrich/raw/bitbucket_org_awangk_ujson.json) (enrichment confidence 0.75)

</details>
