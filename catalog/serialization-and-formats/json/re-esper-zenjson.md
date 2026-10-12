# zenjson

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Single-header, in-situ C++ JSON DOM parser/serializer in the gason style; parses 1.8-3.6x faster than RapidJSON.

| | |
|---|---|
| **Beats** | RapidJSON |
| **Claimed result** | Parsing (derived from page data): 1.81x-3.57x faster than RapidJSON (twitter.json 2034.7 vs 570.3 MB/s = 3.57x; canada.json 3.048 vs 5.509 ms = 1.81x; citm_catalog.json 0.715 vs 1.869 ms = 2.61x). 13.8x-26.7x faster than nlohmann/json. Slightly slower than simdjson on twitter and citm (by 1-3%), and simdjson is 1.46x faster on canada. Stringifying (derived from page data): 2.64x-4.25x faster than RapidJSON (0.712 vs 1.877 ms, 8.723 vs 24.125 ms, 0.777 vs 3.299 ms) and 7.8x-15.3x faster than nlohmann/json. |
| **Workload** | Parsing and stringifying the nativejson-benchmark corpus (twitter.json, canada.json, citm_catalog.json). |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-7700K |
| **Compiler and flags** | Visual Studio 2017 (MSVC toolset v141), 64-bit. The committed benchmark/jsonbenchmark.vcxproj Release\|x64 uses MaxSpeed (/O2), IntrinsicFunctions (/Oi), WholeProgramOptimization and NDEBUG. RapidJSON uses RAPIDJSON_SSE2 and ParseInsitu. simdjson is compiled with /std:c++17 and allocate_capacity pre-allocation. The others use default settings. |
| **Adoption** | 8 stars |
| **Last commit** | 2019-09-16 |
| **Links** | [repository](https://github.com/re-esper/zenjson) · [benchmark](https://github.com/re-esper/zenjson/blob/master/README.md) |

## Verdict

The test machine was the author's Core i7-7700K with Visual Studio 2017 x64 (Release /O2 per the committed .vcxproj), timing 1,000 iterations with clock(). zenjson parsed twitter, canada and citm_catalog 3.57x, 1.81x and 2.61x faster than RapidJSON's SSE2 ParseInsitu, ran within 1-3% of 2019-era simdjson on twitter and citm, and was 1.46x slower than simdjson on canada.json. The 2.64-4.25x stringify lead over RapidJSON is inflated, because the harness never clears RapidJSON's output buffer between iterations. No library versions and no Linux, GCC or Clang results are given.

## Use it when

- Trusted, well-formed input (your own config, assets or service payloads) where you want a DOM that parses 1.8-3.6x faster than RapidJSON's insitu mode and 14-27x faster than nlohmann/json, in one vendored header.
- Parse-then-read workloads where you own the input buffer, can let the parser overwrite it, and can keep it alive as long as the DOM.
- Parsing many documents in sequence into one reused Document. The arena is reset and its blocks are recycled, so steady-state parses do little malloc work.
- String- and small-integer-heavy documents like twitter.json or citm_catalog.json, where the author's table shows it within 1-3% of simdjson.
- Builds where SIMD code paths are unwanted: the parser is plain scalar C++ with no intrinsics.

## Skip it when

- Untrusted input or input that must meet the standard. The parser is lenient: it accepts trailing commas, // comments, raw control characters in strings, lone '-' or '.', leading zeros and unknown escapes. It does not validate UTF-8, it does not combine \u surrogate pairs (it writes each half as a 3-byte sequence), and it ignores any bytes after the root. It also rejects scalar roots (ERROR_BAD_ROOT).
- Exact numbers. Integers longer than 9 digits are stored as doubles, so 64-bit IDs above 2^53 lose precision. Decimal parsing is not correctly rounded. Exponents above 308 become infinity, which the serializer does not handle (it only asserts).
- Documents nested deeper than 32 levels: the fixed parse stack returns ERROR_STACK_OVERFLOW.
- Large objects or indexed access: members and elements are linked lists, so key lookup, getLength() and operator[](index) are O(n), and an index loop over an array is O(n^2).
- Anything that needs a maintained dependency. The project has 8 commits made over 2019-09-15/16, no test suite in the tree, no issues or PRs, and only one Visual Studio benchmark.

## How it is fast

It parses in situ: strings and keys are pointers into the input buffer, which is unescaped in place and NUL-terminated, so no strings are copied. Following gason's design, each value is a NaN-boxed 8-byte word (type tag plus a 47-bit pointer in the NaN payload), and arrays and objects are singly linked node lists bump-allocated from an 8 KB-block arena that Document::parse resets and reuses. The parser is a single non-recursive loop with a fixed 32-entry explicit stack, a 256-entry character-class table, 4x-unrolled whitespace and string scans, an int32 fast path for integers up to 9 digits and a cheap, not correctly rounded float path (digits accumulated in a double, then multiplied by a tabulated power of ten); it uses no SIMD. Serialization uses Milo Yip's Grisu2 dtoa and a digit-pair lookup-table i32toa.

## Compared with alternatives

Pick it over gason, its credited inspiration with the same NaN-boxed, linked-list, in-situ design, when you also want a built-in serializer and nlohmann-style mutable syntax in one header. On parse speed alone, simdjson matched it on twitter/citm and was 1.46x faster on canada.json in zenjson's own table, and simdjson is strict and maintained. So choose zenjson only when you want a tiny vendored header for trusted input.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (bundles Milo Yip's dtoa_milo Grisu2 code) |
| **Minimum toolchain** | C++11 by inspection (initializer_list, enable_if, noexcept); only Visual Studio 2017 (v141) is documented or tested |
| **Platforms** | Not documented; benchmarked only on Windows x64. The code is scalar and portable in principle, but NaN-boxing needs heap pointers that fit in 47 bits, and this is only asserted in debug builds. |
| **Thread safety** | Not documented. Separate Documents parse independently, but the serializer writes numbers through function-static scratch buffers, so concurrent dump() calls race even on different documents. |
| **Drop-in for the baseline** | no |

## Gotchas

- operator[] inserts on a miss: reading json["missing"] adds a null member (and index == length appends). Converting a missing string to std::string builds it from a null char\*, which is undefined behavior; use getString(default) instead.
- The DOM borrows the input buffer and the Document's arena. The buffer must outlive the DOM, and the next parse() on the same Document invalidates every earlier Json view. Document does not delete its copy constructor, so copying one frees the allocator twice.
- The header defines jsonParse and freeCrtAllocatedValue without 'inline' (and, on GCC/Clang, parseStringInternal too), so including it from more than one .cpp should cause duplicate-symbol link errors. It also uses std::numeric_limits and std::string without including &lt;limits&gt; or &lt;string&gt;.
- dump() pretty-prints by default (formatted = true, tab indents); pass false for compact output. The buffer overload returns false and reports the needed size when the buffer is too small. writeInt's static 10-byte buffer is one byte short for int32 values of -1,000,000,000 or less set through the API.

## Known shortcomings

- The RapidJSON stringify loop never clears its StringBuffer, so the baseline's time includes an ever-growing buffer and inflates the 2.64-4.25x stringify ratio. Parse is 1.81-3.57x over RapidJSON. MSVC 2017 only, third-party library versions unstated. Abandoned since 2019-09; 8 stars.
- Lenient, non-validating parser (trailing commas, comments, raw control characters, no UTF-8 validation, no surrogate pairing); integers over 9 digits stored as doubles and decimals not correctly rounded; hard nesting limit of 32. The header likely breaks in multi-file builds (non-inline definitions) and the serializer is not thread-safe (function-static buffers). operator[] inserts on missing keys; copying a Document double-frees. 8 commits, no tests.

## Caveats and trade-offs

No commits since 2019-09-16 (abandoned) and only 8 stars. The benchmark ran on a single 2017-era Windows/MSVC machine, with no Linux/GCC/Clang numbers. Library versions are not stated, and the RapidJSON/simdjson/nlohmann headers are not in the repo; the simdjson row uses the 2019 ParsedJson/json_parse API. In the stringify loop, RapidJSON's StringBuffer and PrettyWriter are never cleared between the 1000 iterations, so its stringify time includes appending and regrowing an ever-larger buffer; zenjson overwrites a fixed 4 MB buffer. zenjson and RapidJSON pretty-print, while nlohmann's dump() is compact. zenjson parses in situ, mutating the input. The README does not say Release explicitly; the Release|x64 settings come from the committed .vcxproj.

In-situ parsing modifies and depends on the input buffer (like RapidJSON's insitu mode), so callers lose the original string; single-header and small (&lt;2k LOC) but unmaintained since 2019, so it lacks fixes for JSON edge cases found in the years since.

## Maintenance

Abandoned since September 2019 (8 commits in two days, 8 stars, no tests), but MIT-licensed and small enough (\~1,650-line single header) to vendor if you accept owning its conformance and correctness fixes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification A, tier now A.
- **Tier reason:** The README Performance tables compare zenjson directly with RapidJSON (and simdjson and nlohmann/json) on the nativejson-benchmark files. The code is public: benchmark/jsonbenchmark.cpp (one TARGET macro per library, clock() over N=1000) and benchmark/jsonbenchmark.vcxproj (toolset v141; Release|x64 = MaxSpeed /O2, IntrinsicFunctions, WholeProgramOptimization, NDEBUG). The README states the compiler (Visual Studio 2017, 64-bit), the per-library flags (RAPIDJSON_SSE2/ParseInsitu, simdjson /std:c++17) and the CPU (i7-7700K), so it meets A. It is borderline: the README never says 'Release' explicitly (the committed project file supplies it), and the third-party library versions are neither stated nor vendored.
- **Verifier notes:** Every raw number in the record's examples appears in the README, but none of the ratios is on the page, and the paraphrased ranges were wrong. The parse lower bound was overstated ('\~2x'; canada.json is really 1.81x). The stringify ranges were understated (4.25x vs RapidJSON and 15.3x vs nlohmann on citm_catalog). Tier A is kept, so this is a claim-only downgrade. The stringify comparison against RapidJSON is biased by a harness flaw (the output buffer is never cleared), so the orchestrator should lead with the parse numbers. Metadata checks out: MIT, 8 stars, not a fork, last commit 2019-09-16.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/re-esper/zenjson>
  - <https://github.com/re-esper/zenjson/blob/master/README.md>
  - <https://github.com/re-esper/zenjson/blob/master/benchmark/jsonbenchmark.cpp>
  - <https://github.com/re-esper/zenjson/blob/master/benchmark/jsonbenchmark.vcxproj>
  - <https://github.com/re-esper/zenjson/blob/master/zenjson/wrapper.h>
  - <https://github.com/re-esper/zenjson/blob/master/zenjson/serialize.h>
- **Sources the enricher read:**
  - <https://github.com/re-esper/zenjson>
  - <https://github.com/re-esper/zenjson/blob/master/README.md>
  - <https://github.com/re-esper/zenjson/blob/master/benchmark/jsonbenchmark.cpp>
  - <https://github.com/re-esper/zenjson/blob/master/benchmark/jsonbenchmark.vcxproj>
  - <https://github.com/re-esper/zenjson/blob/master/zenjson/zenjson.h>
  - <https://github.com/re-esper/zenjson/blob/master/zenjson/base.h>
  - <https://github.com/re-esper/zenjson/blob/master/zenjson/value.h>
  - <https://github.com/re-esper/zenjson/blob/master/zenjson/allocator.h>
  - <https://github.com/re-esper/zenjson/blob/master/zenjson/deserialize.h>
  - <https://github.com/re-esper/zenjson/blob/master/zenjson/serialize.h>
  - <https://github.com/re-esper/zenjson/blob/master/zenjson/wrapper.h>
  - <https://github.com/re-esper/zenjson/blob/master/zenjson/dtoa_milo.h>
  - <https://github.com/re-esper/zenjson/blob/master/singleheader/zenjson.h>
  - <https://github.com/re-esper/zenjson/issues>
  - <https://github.com/re-esper/zenjson/pulls>
  - <https://github.com/re-esper/zenjson/commits/master>
  - <https://github.com/re-esper/zenjson/network/members>
  - <https://github.com/vivkin/gason/blob/master/README.md>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/re-esper/zenjson`) · [data/wave4/enrich/raw/github_com_re_esper_zenjson.json](../../../data/wave4/enrich/raw/github_com_re_esper_zenjson.json) (enrichment confidence 0.8)

</details>
