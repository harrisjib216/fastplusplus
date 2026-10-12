# json.h

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `Unlicense` · 🟢 active

> Public-domain single-header C/C++ JSON parser into one read-only allocation; out-parsed nlohmann/json v2.0.3 in a 2016 shootout.

| | |
|---|---|
| **Beats** | nlohmann/json (C++11, v2.0.3 as pinned by nativejson-benchmark); the same table also has JsonCpp 1.0.0, Jansson and cJSON |
| **Claimed result** | Parse time in ms, json.h vs nlohmann v2.0.3: canada.json 9.418 vs 55.591 (5.9x), citm_catalog.json 5.077 vs 9.875 (1.9x), twitter.json 2.351 vs 7.010 (3.0x); three-file total 16.846 vs 72.476 ms (4.3x) (ratios derived from page data). Also parses faster than JsonCpp (142.458 / 14.587 / 8.477 ms), Jansson (78.465 / 22.656 / 10.935 ms) and cJSON (15.574 / 5.580 / 3.517 ms). Stringify json.h vs nlohmann: canada.json 29.355 vs 76.315 ms (2.6x), citm_catalog.json 4.034 vs 7.178 ms (1.8x), twitter.json 0.978 vs 4.239 ms (4.3x) (ratios derived from page data). RapidJSON is still faster than json.h (4.755 / 1.950 / 1.227 ms parse). |
| **Workload** | Parse of canada.json, citm_catalog.json and twitter.json from an in-memory buffer into a DOM, time in ms. Because json.h keeps numbers as text, the harness (src/tests/sheredomjsonhtest.cpp) walks the tree after json_parse and calls atof() on every number with the result discarded; stringify times json_write_minified plus an emulation walk that sprintf's into a discarded local buffer. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-4980HQ @ 2.80GHz, MacBook Pro (Retina, 15-inch, Mid 2015), macOS 64-bit (README and result file name) |
| **Compiler and flags** | clang 7.0 64-bit (README: 'MacBook Pro (Retina, 15-inch, Mid 2015, Corei7-4980HQ@2.80GHz) with clang 7.0 64-bit', also in the result file name); build/premake5.lua release configuration uses optimize "Full" plus buildoptions -march=native |
| **Adoption** | 841 stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/sheredom/json.h) · [benchmark](https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv) |

## Verdict

In nativejson-benchmark's 2016 sample run (clang 7.0 at full optimization with -march=native, Core i7-4980HQ, macOS), json.h parsed canada/citm_catalog/twitter in 9.4/5.1/2.4 ms vs nlohmann/json v2.0.3 at 55.6/9.9/7.0 ms (4.3x on the three-file total) and stringified 1.8-4.3x faster, but RapidJSON beat it, the measured revision failed 16 conformance tests, and its number conversion was a discarded atof() the optimizer very likely removed, so the canada.json gap overstates the real difference.

## Use it when

- C or C++98-era code that wants a dependency-free, public-domain single header (tests build as gnu89, C99, C11 and C++98 through C++20 on gcc, clang and MSVC).
- Load-once, read-only documents such as config or asset files where one allocation freed with one free() (or carved from an arena via the alloc callback) is the main attraction.
- Inputs that need JSON5 or simplified-JSON leniency (comments, trailing commas, unquoted keys, hex, Infinity/NaN) or byte-offset/line locations for error reporting.
- Round-tripping documents where numbers must come back exactly as written: the suite records 27/27 roundtrip passes because number text is copied verbatim (nlohmann v2.0.3 failed roundtrip24-27).

## Skip it when

- Raw throughput matters: RapidJSON beat it on every file in the same run (4.8/2.0/1.2 ms vs 9.4/5.1/2.4 ms parse), and the catalogued yyjson and simdjson are far faster still.
- Number-heavy input: canada.json used 18,010,128 bytes vs 5,293,488 for nlohmann (3.4x), and every numeric read still needs your own strtod.
- You need to build or mutate documents: the DOM is read-only and there is no construction API; cJSON or nlohmann fit better.
- Untrusted input on an old copy: more than 15 closed issues report heap overflows, out-of-bounds reads and a stack overflow (2022 to October 2026, most recently #132 on 2026-10-01); only vendor a current revision.
- Key lookup by name: objects are singly linked lists with no lookup helper (open feature request #79), so access is a linear walk.

## How it is fast

Two-pass design: a first scan (json_get_value_size) validates the input and sums the exact DOM and string-data sizes, then one malloc is made and a second pass (json_parse_value) fills it, so the whole document costs one allocation instead of one per node (2 allocations in the benchmark vs 170,254 for nlohmann on canada.json). Numbers are copied as their source text with no string-to-double conversion, and the writer copies that text back verbatim with no double formatting. The scanners are plain byte-at-a-time loops; there is no SIMD.

## Compared with alternatives

Pick it over cJSON or udp/json-parser when you want one public-domain header, a single-allocation read-only DOM, JSON5 flags and lossless number text; pick yyjson (MIT, also a compact read-only DOM, and much faster) whenever speed is the reason you are looking, and cJSON when you must build or edit documents.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (libc: stddef.h, string.h, stdlib.h, inttypes.h) |
| **Minimum toolchain** | C89 (gnu89) or C++98; gcc, clang, MSVC, TCC or Open Watcom (any other compiler hits an #error) |
| **Platforms** | any; README lists Windows, macOS and Linux |
| **Thread safety** | not documented; json.h has no global state, so separate parses on separate buffers do not share anything |
| **Drop-in for the baseline** | partial: it covers parse and write of standard JSON, but the API is C structs with linked lists, read-only, and numbers stay strings, so nlohmann/json call sites must be rewritten |

## Gotchas

- Harness flaw behind the numbers: nativejson-benchmark's sheredomjsonhtest.cpp 'emulates' number parsing with atof() whose result is discarded; LLVM 3.7 (the base of Apple clang 7.0) marks atof nounwind and readonly and deletes unused side-effect-free calls, so on canada.json the measured parse very likely did no number conversion at all, while nlohmann converted all of them (not confirmed by disassembly).
- Second harness flaw: the stringify/prettify emulation memcpy's the json_number_s struct's first field (the char\* to the number text) into a double and sprintf's that pointer bit pattern, so it formats garbage subnormals, not the document's numbers; json.h's own writer only copies number text.
- Every function is defined in the header with weak linkage (json_weak, __inline on MSVC), so there is no single-implementation macro; each translation unit compiles the full parser and the linker folds the copies.
- Free the DOM with whatever matches the allocator you passed (plain free() by default); there is no json_free and no realloc-style growth (issue #109), and writers only gained allocator callbacks (json_write_minified_ex, json_write_pretty_ex) on 2026-08-24.
- The 2016 revision that was measured accepted invalid JSON (raw tabs and newlines in strings, trailing content, malformed exponents) and did not decode \u escapes; current code fixes these, and nesting depth is capped by JSON_MAX_RECURSION (default 1000).

## Known shortcomings

- nativejson-benchmark 2016 run: the suite's conformance.csv shows the measured json.h failed 9 of 34 validation tests (raw tab and newline in strings, trailing content, bad exponents) and 7 of 9 string tests (\u escapes), fixed later (\u decoding added; raw control characters rejected 2026-10-02), so the later-fixed-bug rule applies; the harness discards the atof result and keeps numbers as text; nlohmann v2.0.3 baseline from 2016.
- Enricher: nativejson-benchmark's sheredomjsonhtest.cpp ParseNumbers calls atof() and discards the result, which LLVM 3.7 (Apple clang 7.0) marks nounwind+readonly and deletes, so the canada.json parse very likely did no number conversion while nlohmann did (not confirmed by disassembly); WriteNumbers memcpy's the char\* of json_number_s into a double, so the stringify rows formatted pointer bits, not document numbers. More than 15 closed issues report heap OOB, OOB reads and stack overflows (2022 to 2026-10-01, #132). Downgraded C to D.

## Caveats and trade-offs

Numbers are the independent nativejson-benchmark sample run (README 'Update on: 2016-9-9') on a 2014-era CPU with clang 7.0, a 2016-era json.h and nlohmann v2.0.3; nlohmann/json has been reworked since. The measured json.h did less work than the baselines: in the same suite's sample/conformance.csv it failed 9/34 parse-validation tests (pass01 rejected; fail02, fail07, fail08, fail10, fail25 raw tab, fail27 raw newline, fail29, fail30 accepted) and 7/9 string tests (string03-string09, consistent with not decoding \u escapes), while nlohmann passed all validation and string tests. Current json.h decodes \u escapes and gained fixes in 2026 (reject numbers with no digits after a sign, 2026-10-01; reject raw control characters in quoted strings, 2026-10-02; comment after a number, 2026-10-06), so the measured parser was more permissive and today's ratios may differ. json.h does not convert numbers to doubles; the harness's emulation calls atof() and discards the result, which the compiler may drop, so number conversion cost (large on canada.json) may not have been paid at all; the stringify emulation memcpy's the number payload pointer as a double and formats it into a discarded buffer, and json.h's writer copies number text verbatim with no double-to-string work. The json.h README makes no speed claim and links no benchmark; the win is a derived comparison between rows of a third-party shootout (the suite author also wrote RapidJSON, which beats json.h). Public-domain dedication (Unlicense), no patent grant. [retier] nativejson-benchmark 2016 run (clang 7.0, i7-4980HQ): the adapter sheredomjsonhtest.cpp calls atof() in ParseNumbers and discards the result, which LLVM 3.7 marks nounwind+readonly and deletes, so the canada.json parse very likely did no number conversion while nlohmann did (not confirmed by disassembly); WriteNumbers memcpy's the char\* of json_number_s into a double, so stringify rows formatted pointer bits rather than document numbers. The measured build failed 9 of 34 validation tests and 7 of 9 string tests (conformance.csv), fixed later (\u decoding added, raw control characters rejected 2026-10-02). nlohmann v2.0.3 baseline from 2016. More than 15 closed issues report heap OOB, OOB reads and stack overflows (2022 to 2026-10-01, #132).

Read-only DOM in one allocation (2 allocations in the benchmark), non-streaming, numbers kept as unparsed strings so callers convert them. Memory is large on number-heavy input: canada.json 18,010,128 bytes vs nlohmann 5,293,488 (3.4x, derived from page data). The same suite's conformance table records 9 failed parse-validation cases and 7 of 9 failed string-parse cases for json.h (nlohmann passes all of both), so it accepts some invalid JSON and does not decode some string escapes in that vendored version.

## Maintenance

Active (last commit 2026-10-06, with a burst of 2026 correctness and memory-safety fixes) and Unlicense public domain, so it is easy to vendor, but vendor a current revision and treat the 2016 benchmark ratios as stale and inflated.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification A, tier now D.
- **Tier reason:** The shootout itself would meet A (public harness miloyip/nativejson-benchmark src/tests/sheredomjsonhtest.cpp, clang 7.0, build/premake5.lua optimize "Full" with -march=native, Core i7-4980HQ), but the measured 2016-era json.h failed 9 of 34 parse-validation and 7 of 9 string tests in the same suite's sample/conformance.csv (accepted raw tab and newline inside strings, trailing content and malformed exponents; string03-string09 fail, consistent with no \u escape decoding), and those hot-path correctness gaps were fixed later (current json.h decodes \u escapes; raw control characters rejected in commit 5db3857 on 2026-10-02), so the later-fixed-bug rule caps it at C.
- **Retiered** C to D: Downgraded C to D: the nativejson-benchmark adapter discards atof()'s result, so the compiler very likely removed number conversion from the timed json.h parse (nlohmann converted numbers), and the stringify adapter formats pointer bits; the 2016 build also failed 16 conformance tests fixed later. Kept as directional (MQF-style no-op suspected but not confirmed by disassembly).
- **Verifier notes:** Numbers match the CSV rows exactly (Scheredom json.h (C) and Nlohmann (C++11) rows), so the evidence is real and the entry stays; downgraded A to C under the later-fixed-correctness rule because the shootout's own conformance results show the measured json.h skipped validation and \u decoding work that it now performs, and the number post-pass discards atof results. Shortcomings to record: measured 2016 build failed 16 conformance tests (raw control characters, trailing content, malformed exponents, \u escapes) later fixed; numbers kept as strings so parse and stringify skip float conversion; harness atof result discarded; stale 2016 run against nlohmann v2.0.3. Metadata confirmed: Unlicense, 841 stars, not a fork, not archived, last commit 2026-10-06 (main).
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** nativejson-benchmark CSV (verifier downgrade A to C); enricher harness reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv>
  - <https://github.com/miloyip/nativejson-benchmark>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/README.md>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/build/premake5.lua>
  - <https://github.com/miloyip/nativejson-benchmark/tree/master/src/tests>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/src/tests/sheredomjsonhtest.cpp>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/sample/conformance.csv>
  - <https://github.com/sheredom/json.h>
  - <https://github.com/sheredom/json.h/commits>
  - <https://raw.githubusercontent.com/sheredom/json.h/HEAD/json.h>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/sheredom/json.h/HEAD/README.md>
  - <https://raw.githubusercontent.com/sheredom/json.h/HEAD/json.h>
  - <https://raw.githubusercontent.com/sheredom/json.h/HEAD/test/CMakeLists.txt>
  - <https://github.com/sheredom/json.h/issues>
  - <https://github.com/sheredom/json.h/issues?q=is%3Aissue+is%3Aclosed>
  - <https://github.com/sheredom/json.h/issues/109>
  - <https://github.com/sheredom/json.h/commits>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/src/tests/sheredomjsonhtest.cpp>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/sample/conformance.csv>
  - <https://raw.githubusercontent.com/llvm/llvm-project/llvmorg-3.7.0/llvm/lib/Transforms/IPO/FunctionAttrs.cpp>
  - <https://raw.githubusercontent.com/llvm/llvm-project/llvmorg-3.7.0/llvm/lib/Transforms/Utils/Local.cpp>
  - <https://raw.githubusercontent.com/llvm/llvm-project/llvmorg-3.7.0/llvm/include/llvm/IR/Instruction.h>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/sheredom/json.h`) · [data/wave4/enrich/raw/github_com_sheredom_json_h.json](../../../data/wave4/enrich/raw/github_com_sheredom_json_h.json) (enrichment confidence 0.7)

</details>
