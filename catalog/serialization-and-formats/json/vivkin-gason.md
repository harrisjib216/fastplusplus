# gason

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🔴 abandoned

> \~450-line in-situ C++11 JSON DOM parser, 1.2-1.5x faster than default RapidJSON on kostya's number-heavy JSON test.

| | |
|---|---|
| **Beats** | RapidJSON |
| **Claimed result** | kostya/benchmarks JSON test (README update 2026-07-19): gason 0.127 s vs RapidJSON 0.154 s with g++ (1.21x, derived from page data), and 0.133 s vs 0.194 s with clang++ (1.46x, derived). RapidJSON Precise with g++ takes 0.212 s. gason trails simdjson On-Demand (0.060 s), DAW JSON Link (0.089 s) and simdjson DOM (0.107 s), and roughly ties yyjson (0.131 s). The first-party README shootout (2013-14, i7 2.3 GHz, clang-500.2.79) gives gason 924 us vs RapidJSON 2210 us parse on monster.json (2.4x, derived) and 75 vs 91 us on data.json (1.2x, derived), but RapidJSON is faster on big.json (18093 vs 20092 us). |
| **Workload** | kostya/benchmarks JSON test: parse a large generated JSON file of 3D coordinates and average the x/y/z values, using idiomatic library code, reported as the median of runs with data loading not timed. The README shootout parses and sums the numbers in big.json, monster.json and data.json. |
| **Metric** | latency |
| **Hardware** | kostya/benchmarks: Intel Xeon E-2324G (Debian forky/sid Docker image). README shootout: Intel Core i7 2.3 GHz (OSX 10.9) and Samsung Galaxy Note II GT-N7100 (Android 4.3). |
| **Compiler and flags** | kostya/benchmarks: g++ 16.1.0 and clang++ 22.1.8 (-stdlib=libc++), -O3 -march=native -flto=auto -std=c++23. README shootout: clang-500.2.79 (OSX) and gcc 4.8.2 (Android). The page states no flags; the May-2014 CMakeLists (commit add97a2) sets -O3. |
| **Adoption** | 339 stars |
| **Last commit** | 2021-10-18 |
| **Links** | [repository](https://github.com/vivkin/gason) · [benchmark](https://github.com/kostya/benchmarks#json) |

## Verdict

kostya/benchmarks (README update 2026-07-19; Intel Xeon E-2324G, Debian Docker, -O3 -march=native -flto=auto -std=c++23) parsed a generated file of 524,288 coordinate objects and averaged x/y/z. gason took 0.127 s vs 0.154 s for RapidJSON's default DOM Parse() with g++ 16.1 (1.21x), and 0.133 s vs 0.194 s with clang++ 22.1.8/libc++ (1.46x); gason parses in place, while the RapidJSON test copies strings and no ParseInsitu variant was run. The author's 2013-14 shootout against 2013 RapidJSON trunk (i7, clang-500) is mixed: gason is 2.4x faster on monster.json (924 vs 2210 us) but slower on big.json (20092 vs 18093 us).

## Use it when

- Parsing trusted JSON once when it already sits in a writable buffer you can give up, and a sequential walk of the tree is enough (for example, pulling fields or sums from a large data dump or config).
- Number-heavy documents where approximate doubles are acceptable. kostya's generated file of 524,288 coordinate objects is this shape, and gason took 0.127 s there vs 0.154 s for RapidJSON (g++).
- Memory-constrained parsing. In the same test, gason's RSS grew by 96.75 MiB, vs 123.44 MiB for RapidJSON, 175.86 MiB for simdjson DOM and 229.38 MiB for yyjson (g++/gcc).
- Projects that want a tiny vendored parser: two files, about 450 lines, no dependencies, builds with -fno-exceptions -fno-rtti, on x86-64 or 32-bit targets.

## Skip it when

- Untrusted or validation-critical input. It accepts invalid JSON (trailing commas, {"a" null}, leading zeros, 0e, ["x"]]) and passes only 25 of 34 nativejson-benchmark validation cases. Open issue #43 (2026) reports reads past the terminating NUL when whitespace comes right before it, and the source confirms that path.
- When numbers must be exact. Conversion is not correctly rounded: it passes 26 of 66 nativejson-benchmark double tests, 5e-324 parses as 0 and 1.7976931348623157e308 as inf. There is no integer type, so integers above 2^53 lose precision.
- Platforms with tagged or wide pointers, such as Android on aarch64 with tagged heap pointers. NaN-boxing keeps only 47 pointer bits, so the type tag gets corrupted (open issue #36, seen on a Pixel 5). The guarding assert is compiled out in release builds, so the failure is silent.
- Documents nested more than 32 levels deep: the stack size is fixed and the parse returns JSON_STACK_OVERFLOW. Also skip it when you need keyed or indexed access, DOM editing or JSON output; none of these exist, and objects are linear lists.
- When peak speed matters most: simdjson On-Demand (0.060 s), DAW JSON Link (0.089 s) and simdjson DOM (0.107 s) all beat gason's 0.127 s in the same kostya test.

## How it is fast

It parses destructively in place. Strings are unescaped and NUL-terminated inside the source buffer and referenced by pointer, so string data is never copied. Every value is an 8-byte NaN-boxed double: numbers are stored as raw doubles, and every other type is a 4-bit tag plus a 47-bit pointer. Array and object members are singly-linked nodes of 16 or 24 bytes, taken from a bump-pointer zone allocator (4 KiB malloc'd blocks) and freed all at once. The parser is one non-recursive switch loop with a fixed 32-entry container stack. It converts numbers with a hand-rolled digit accumulator instead of strtod, which is fast but not correctly rounded.

## Compared with alternatives

In kostya's test, simdjson is faster (On-Demand 0.060 s, DOM 0.107 s) and yyjson roughly ties gason (0.131 s vs 0.127 s). kostya flags gason's number parsing as inaccurate but not theirs, so choose gason only when a two-file, \~450-line vendorable parser with a smaller tree (96.75 MiB RSS growth vs 175-229 MiB) matters more than exact numbers, strict validation and maintenance.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none |
| **Minimum toolchain** | C++11. VS2012 fails to compile it (open issue #22); VS2013 and later are reported to work. kostya builds it with g++ 16.1 and clang++ 22.1.8 at -std=c++23. |
| **Platforms** | 64-bit targets whose pointers fit in 47 bits (typical x86-64) and 32-bit targets (fixed in 2015). Broken on aarch64 with tagged heap pointers, e.g. Android (issue #36). |
| **Thread safety** | Not documented. In the source, jsonParse keeps no global state: all parser state lives on the stack or in the caller's JsonAllocator. Concurrent parses with separate buffers and allocators should therefore be safe, but that is inferred, not stated. |
| **Drop-in for the baseline** | no |

## Gotchas

- The source buffer is overwritten, and every string points into it. Keep the buffer and the JsonAllocator alive for as long as you use any JsonValue; destroying the allocator invalidates the whole tree.
- Array nodes are allocated without the key field, so reading node-&gt;key while iterating an array reads garbage. The README says only next and value are valid for arrays, and issue #38 hit this.
- Strings are C strings: \u0000 truncates them, and a surrogate pair such as \uD834\uDD1E becomes two 3-byte sequences, which is invalid UTF-8. Raw non-ASCII bytes are not validated.
- There is no length parameter, so the input must be NUL-terminated. Parsing stops after the first complete value and endptr points at the rest, so trailing data is not an error unless you check endptr yourself.

## Known shortcomings

- Unequal comparison: gason parses in place while kostya's RapidJSON harness uses the copying Parse() (no ParseInsitu row), and gason's number conversion is not correctly rounded. Fails many nativejson-benchmark conformance cases (25/34 validation, 26/66 double parsing). Open safety bugs: out-of-bounds read past the terminating NUL (#43, unsafe on untrusted input) and NaN-boxing that silently breaks with aarch64 tagged pointers (#36). Depth capped at 32, no integer type, no writer. Unmaintained since 2016.

## Caveats and trade-offs

The independent win over RapidJSON is modest (1.21x with g++, 1.46x with clang++). gason loses to simdjson and DAW JSON Link. kostya notes that gason mutates its input and has number-parsing inaccuracies (vivkin/gason#35); default RapidJSON has the same caveat. The README shootout is from 2013-14 against 2013 RapidJSON svn trunk and gives mixed results, with RapidJSON winning big.json on OSX. Its harness (parser-shootout.cpp, clone-enemy-parsers.sh) was removed from HEAD in Nov 2014 and survives only in git history, and the README build steps reference files that no longer exist. Last commit was 2021-10-18.

Destructive/in-situ parser that mutates the source buffer; objects/arrays are singly-linked lists (no random access); uses NaN-boxing for values; not a strict parser (accepts trailing commas)

## Maintenance

Abandoned: the last code fix was in 2016 and the last commit, in 2021, merged a typo fix, while 11 issues stay open, including tagged-pointer breakage, inexact numbers and an out-of-bounds read; it is MIT-licensed and small enough to vendor and patch yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded from stronger evidence: the independent kostya/benchmarks suite (\~2.9k stars) runs gason against RapidJSON. Its code is json/test_gason.cpp, json/test_rapid.cpp and common/commands.mk. It states g++ 16.1.0 and clang++ 22.1.8, flags -O3 -march=native -flto=auto, and CPU Intel Xeon E-2324G. gason measured 0.127 s vs 0.154 s for RapidJSON. The first-party README shootout alone would only be C.
- **Verifier notes:** The tier is upgraded from B to A on the independent kostya/benchmarks suite, and benchmark_url now points there. The README numbers match the record, but on their own they are first-party and would be C. Metadata checks out: MIT, 339 stars, last commit 2021-10-18, abandoned.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** kostya/benchmarks memory growth: gason 96.75 MiB vs RapidJSON 123.44, simdjson DOM 175.86, yyjson 229.38.
- **Pages the verifier opened:**
  - <https://github.com/vivkin/gason>
  - <https://github.com/vivkin/gason#performance>
  - <https://github.com/vivkin/gason/blob/master/CMakeLists.txt>
  - <https://github.com/vivkin/gason/blob/master/src/benchmark.cpp>
  - <https://github.com/vivkin/gason/blob/master/LICENSE>
  - <https://github.com/vivkin/gason/blob/master/data/download.sh>
  - <https://github.com/vivkin/gason/blob/add97a2/CMakeLists.txt>
  - <https://github.com/vivkin/gason/blob/add97a2/parser-shootout.cpp>
  - <https://github.com/vivkin/gason/blob/add97a2/clone-enemy-parsers.sh>
  - <https://github.com/kostya/benchmarks>
  - <https://github.com/kostya/benchmarks#json>
  - <https://github.com/kostya/benchmarks/blob/master/json/Makefile>
  - <https://github.com/kostya/benchmarks/blob/master/common/commands.mk>
  - <https://github.com/kostya/benchmarks/blob/master/json/test_gason.cpp>
- **Sources the enricher read:**
  - <https://github.com/vivkin/gason>
  - <https://github.com/vivkin/gason/blob/master/src/gason.h>
  - <https://github.com/vivkin/gason/blob/master/src/gason.cpp>
  - <https://github.com/vivkin/gason/blob/master/CMakeLists.txt>
  - <https://github.com/vivkin/gason/blob/master/src/benchmark.cpp>
  - <https://github.com/vivkin/gason/blob/master/src/test-suite.cpp>
  - <https://github.com/vivkin/gason/blob/master/src/pretty-print.cpp>
  - <https://github.com/vivkin/gason/issues>
  - <https://github.com/vivkin/gason/pulls>
  - <https://github.com/vivkin/gason/issues/43>
  - <https://github.com/vivkin/gason/issues/40>
  - <https://github.com/vivkin/gason/issues/38>
  - <https://github.com/vivkin/gason/issues/36>
  - <https://github.com/vivkin/gason/issues/35>
  - <https://github.com/vivkin/gason/issues/34>
  - <https://github.com/vivkin/gason/issues/33>
  - <https://github.com/vivkin/gason/issues/32>
  - <https://github.com/vivkin/gason/issues/29>
  - <https://github.com/vivkin/gason/issues/25>
  - <https://github.com/vivkin/gason/issues/22>
  - <https://github.com/vivkin/gason/issues/20>
  - <https://github.com/vivkin/gason/issues/19>
  - <https://github.com/vivkin/gason/issues/15>
  - <https://github.com/vivkin/gason/issues/12>
  - <https://github.com/vivkin/gason/pull/39>
  - <https://github.com/vivkin/gason/commits/master>
  - <https://github.com/vivkin/jzon>
  - <https://github.com/kostya/benchmarks>
  - <https://github.com/kostya/benchmarks#json>
  - <https://github.com/kostya/benchmarks/blob/master/json/test_gason.cpp>
  - <https://github.com/kostya/benchmarks/blob/master/json/test_rapid.cpp>
  - <https://github.com/kostya/benchmarks/blob/master/json/Makefile>
  - <https://github.com/kostya/benchmarks/blob/master/json/generate_json.rb>
  - <https://github.com/kostya/benchmarks/blob/master/common/commands.mk>
  - <https://github.com/miloyip/nativejson-benchmark>
  - https://github.com/miloyip/nativejson-benchmark/blob/master/sample/conformance_gason%20(C%2B%2B11).md
  - https://github.com/miloyip/nativejson-benchmark/blob/master/sample/conformance_RapidJSON%20(C%2B%2B).md
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/vivkin/gason`) · [data/wave4/enrich/raw/github_com_vivkin_gason.json](../../../data/wave4/enrich/raw/github_com_vivkin_gason.json) (enrichment confidence 0.8)

</details>
