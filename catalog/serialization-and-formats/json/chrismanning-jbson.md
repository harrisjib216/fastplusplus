# jbson

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSL-1.0` · 🔴 abandoned

> Header-only C++14 JSON-to-BSON parser; author's 2015 runs: 1.46x faster than JsonCpp on canada.json, 9x slower than RapidJSON.

| | |
|---|---|
| **Beats** | JsonCpp (also QJsonDocument and jsoncons) |
| **Claimed result** | json_benchmark, README figures: large 43.0072 to 43.0377 s vs jsoncpp 62.7781 to 62.7823 s (1.46x), QJsonDocument 58.1027 to 58.1235 s (1.35x), jsoncons 243.634 to 243.796 s (5.7x); small 1.24328 to 1.27775 s vs jsoncpp 2.4124 to 2.45696 s (about 1.9x) and jsoncons 10.2386 to 10.2747 s (8x), ratios derived from page data. sanSS benchmark: medium 64,800 us vs jsoncpp 121,035 us and QJsonDocument 82,839 us; large 190,883 us vs jsoncpp 438,745 us (QJsonDocument did not finish); memory 24,708 K vs jsoncpp 44,224 K on medium objects and 1,132 K vs 4,084 K on small. README: 'it's 2nd only to rapidjson (or 3rd to QJsonDocument with small input)'. |
| **Workload** | JSON text parsing: mloskot/json_benchmark (1000 iterations of 500 small documents, and 1000 iterations of canada.json as one large document) and sanSS/json-bechmarks (small, medium and large objects, average time per parse and memory), jbson parsing JSON into its BSON document. |
| **Metric** | throughput |
| **Adoption** | 38 stars |
| **Last commit** | 2015-12-20 |
| **Links** | [repository](https://github.com/chrismanning/jbson) · [benchmark](https://github.com/chrismanning/jbson) |

## Verdict

The author ran mloskot/json_benchmark (1000 parses of canada.json, 2,251,060 bytes) and reports jbson 43.0 s vs JsonCpp 62.8 s (1.46x), QJsonDocument 58.1 s (1.35x), jsoncons 243.6 s and RapidJSON 4.86 s, i.e. about 52 MB/s vs 36 MB/s for JsonCpp and 463 MB/s for RapidJSON (derived from page data), plus about 1.9x over JsonCpp on 500 small documents; sanSS json-bechmarks gives 64.8 ms vs 121.0 ms on medium objects. No compiler, flags, CPU or library versions are given, and the jbson adapter used in both suites is not published; the repo's own test/perf_test.cpp only self-times 1000 parses of a sample file with no baseline.

## Use it when

- You need JSON converted to BSON bytes (for example to hand to MongoDB-style storage or a BSON wire format) and want one header-only, BSL-licensed C++ library that does both.
- Parse once, iterate sequentially: config or message documents that are walked front to back rather than randomly indexed.
- Memory matters more than speed and the alternative is a node-per-value DOM such as JsonCpp: the author's sanSS runs show 24,708 K vs 44,224 K on medium objects.
- Legacy code that already depends on Boost and a 2015-era libc++ toolchain, where the library is known to build.

## Skip it when

- Raw parse speed is the goal: by the author's own numbers RapidJSON parses canada.json about 9x faster (4.86 s vs 43.0 s per 1000 parses), and yyjson and simdjson are faster still.
- Random access into large documents or arrays: find() is a linear scan, and array index lookup does std::to_string(idx) and then a linear name comparison, so indexed loops over a large array are quadratic.
- Input you do not control: there is no fuzzing, and the literal, \u-escape and post-whitespace checks dereference the iterator without testing for end of input (see gotchas).
- Strict JSON round-tripping: the BSON model cannot hold NUL in names, \u0000 is stored as the six characters \u0000, integers beyond int64 throw instead of becoming doubles, and number validation rejects valid 0e5 while accepting invalid -01.
- Any maintained or modern-toolchain project: the last commit was 2015-12-20 and the headers depend on Library Fundamentals TS headers and std::wstring_convert.

## How it is fast

The reader reserves one std::vector&lt;char&gt; the size of the input and appends type bytes, names, length-prefixed strings and little-endian numbers into it in a single recursive-descent pass, so there is no per-node heap allocation, std::map or Value object as in JsonCpp. Numbers go through Boost.Spirit Qi's int and real parsers; integers that fit int32 are stored as 4 bytes. Reading is lazy: elements are decoded from the buffer only when iterated. Nothing is SIMD or table-driven, and every character passes through a Boost.Spirit line_pos_iterator that tracks line numbers for error messages, which is one reason it stays far behind RapidJSON.

## Compared with alternatives

Pick jbson over yyjson, simdjson or the C parsers Jansson and json-c only when BSON output itself is the requirement and a header-only Boost-based C++ library fits; for plain JSON parsing every one of those siblings is the better choice, and jsoncons (5.7x slower than jbson in the 2015 README) is catalogued separately with newer numbers.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | Boost 1.55 or newer (headers only: Range, Spirit Qi, Exception, Predef, lexical_cast, ios_state); the optional test build fetches googletest r660 from googletest.googlecode.com SVN |
| **Minimum toolchain** | C++14 (-std=c++1y) with &lt;codecvt&gt;, &lt;experimental/optional&gt; and &lt;experimental/string_view&gt;; README says it is known to work only with an up-to-date (2015) libc++ and fails on gcc 4.8/4.9 libstdc++ |
| **Platforms** | any (portable scalar C++); BSON numbers are written little-endian via native_to_little_endian |
| **Thread safety** | not documented; json_reader keeps per-parse state, so use one reader per thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Extended-JSON handling is broken for everything except \$oid: parse_extended_value compares basic_document::size(), which returns the BSON size in bytes (at least 5), against 1 or 2 for \$date, \$timestamp, \$undefined, \$minkey, \$maxkey, \$binary/\$type, \$regex/\$options and \$ref/\$id, so any object whose first key is one of those always throws json_parse_error. This includes ordinary JSON such as JSON Schema subschemas of the form {"\$ref": "#/definitions/x"}; the tests cover only \$oid and a \$binary case that is expected to throw.
- Bounds checks are missing on malformed or truncated input: true/false/null are matched with std::next(first, 4 or 5) past the end, \u escapes read four characters without an end check, and parse_document/parse_array test \*first for ':' , ',' or '}' right after skip_space without checking first == last. With std::string input this usually hits the terminating NUL; with other ranges it is an out-of-range read.
- Number edge cases: integers outside int64 fail Spirit's extract_int and throw; 0e5 and 0E-3 (valid JSON) are rejected by the leading-zero check, while -01 (invalid JSON) is accepted; \u0000 is kept as the literal text \u0000.
- Element names are always copied, and elements obtained from a document hold iterator ranges into its buffer, so they must not outlive the document unless copied into jbson::element (README).

## Known shortcomings

- First-party README numbers with no compiler, flags or hardware; the adapter code behind the table is not published. About 9x slower than RapidJSON on large inputs. Parses to a BSON buffer, a different data model from DOM JSON libraries.
- Enricher: parse_extended_value compares the document byte size (at least 5) against 1 or 2, so any JSON object whose first key is \$date, \$timestamp, \$regex, \$ref, \$id, \$binary, \$undefined, \$minkey or \$maxkey always throws json_parse_error (JSON Schema {"\$ref": ...} included; only \$oid works); no end-of-input checks on true/false/null, \u escapes or after skip_space; rejects valid 0e5 and accepts -01. test/perf_test.cpp is self-timing only with no baseline; derived from page data about 52 MB/s on canada.json vs RapidJSON 463 MB/s.

## Caveats and trade-offs

First-party run: the README gives the author's own timings with no compiler, flags, hardware or library versions, so tier C even though mloskot/json_benchmark is public (its own README lists no jbson or jsoncons row and shows different absolute times on other hardware); the jbson benchmark adapters are not published anywhere found (no bench directory in the repo). It is slower than RapidJSON (small 0.454 to 0.486 s, large 4.857 to 4.863 s, so about 9x on large) and, on small input, slower than QJsonDocument (1.046 to 1.056 s). json_reader parses straight into a BSON byte buffer that is then read through iterators, a different data model from the DOMs it is compared with. README's large-object memory figure is garbled ('70,7748 K'). README says the library is known to work only with an up-to-date libc++. 2015 numbers, repository last changed 2015-12-20. Both benchmark repos are unmaintained or superseded by nativejson-benchmark, which has no jbson row.

Header-only C++14 library whose JSON parser emits a BSON-style byte document that is read lazily through iterators and constant wrappers, not an in-memory DOM; BSON names cannot hold NUL so JSON compliance is partial; the README says it needs a current libc++ (codecvt and C++14 aliases missing from older libstdc++).

## Maintenance

Abandoned since 2015-12-20 (261 commits, 38 stars, 2 open issues including an unimplemented binary element type, #7); BSL-1.0 and header-only so it can be vendored, but expect to patch it for a current compiler and standard library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README Performance section only: author's own json_benchmark and sanSS json-bechmarks runs with no compiler, flags, hardware or library versions; the jbson adapter code is not public (repo has only doc/, include/, test/, and mloskot/json_benchmark lists neither jbson nor jsoncons).
- **Verifier notes:** All README numbers and derived ratios check out (large 43.0 vs jsoncpp 62.8 s = 1.46x, QJsonDocument 1.35x, jsoncons 5.7x; small about 1.9x vs jsoncpp; sanSS medium 64,800 vs 121,035 us). Metadata verified: BSL-1.0, 38 stars, not archived, last commit 2015-12-20 (abandoned). Shortcomings: first-party, unpublished adapter, no methodology, slower than RapidJSON and (small input) QJsonDocument, different data model (BSON buffer).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** first-party README (verifier); enricher code reading
- **Pages the verifier opened:**
  - <https://github.com/chrismanning/jbson>
  - <https://github.com/chrismanning/jbson/commits/master>
  - <https://github.com/chrismanning/jbson/tree/master>
  - <https://raw.githubusercontent.com/chrismanning/jbson/HEAD/README.md>
  - <https://raw.githubusercontent.com/chrismanning/jbson/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/mloskot/json_benchmark/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/chrismanning/jbson>
  - <https://github.com/chrismanning/jbson/tree/master/include/jbson>
  - <https://github.com/chrismanning/jbson/tree/master/test>
  - <https://github.com/chrismanning/jbson/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/chrismanning/jbson/HEAD/README.md>
  - <https://raw.githubusercontent.com/chrismanning/jbson/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/chrismanning/jbson/HEAD/include/jbson/json_reader.hpp>
  - <https://raw.githubusercontent.com/chrismanning/jbson/HEAD/include/jbson/document.hpp>
  - <https://raw.githubusercontent.com/chrismanning/jbson/HEAD/include/jbson/element.hpp>
  - <https://raw.githubusercontent.com/chrismanning/jbson/HEAD/include/jbson/json_writer.hpp>
  - <https://raw.githubusercontent.com/chrismanning/jbson/HEAD/include/jbson/detail/config.hpp>
  - <https://raw.githubusercontent.com/chrismanning/jbson/HEAD/test/json_reader_test.cpp>
  - <https://raw.githubusercontent.com/chrismanning/jbson/HEAD/test/perf_test.cpp>
  - <https://raw.githubusercontent.com/chrismanning/jbson/HEAD/test/CMakeLists.txt>
  - <https://raw.githubusercontent.com/mloskot/json_benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/mloskot/json_benchmark/HEAD/data/canada.json>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/chrismanning/jbson`) · [data/wave4/enrich/raw/github_com_chrismanning_jbson.json](../../../data/wave4/enrich/raw/github_com_chrismanning_jbson.json) (enrichment confidence 0.6)

</details>
