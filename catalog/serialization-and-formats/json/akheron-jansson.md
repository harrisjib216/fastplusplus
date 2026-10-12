# Jansson

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟢 active

> Dependency-free C library for a mutable, reference-counted JSON tree; stringified 1.35x faster than JsonCpp 1.0.0 in a 2016 independent run.

| | |
|---|---|
| **Beats** | JsonCpp 1.0.0 (stringify also beats nlohmann/json 2.0.3) |
| **Claimed result** | No claim by the project; figures are from the independent suite's committed sample CSV (Jansson v2.7). Stringify total 69.9 ms vs JsonCpp 94.3 ms (1.35x) and Nlohmann 87.7 ms (1.25x), ratios derived from page data; Jansson is faster on each file (canada 64.2 vs JsonCpp 84.4 / Nlohmann 76.3 ms; citm 3.76 vs 5.68 / 7.18 ms; twitter 1.93 vs 4.14 / 4.24 ms). Parse total 112.1 ms vs JsonCpp 165.5 ms (1.48x derived) and json-c 134.6 ms (1.20x derived), but that rests on canada.json (78.5 vs JsonCpp 142.5 ms); Jansson is slower than JsonCpp on citm (22.7 vs 14.6 ms) and twitter (10.9 vs 8.5 ms) and slower than Nlohmann 2.0.3 on parse (72.5 ms total). |
| **Workload** | nativejson-benchmark: parse three JSON files (canada.json 2199 KB, citm_catalog.json 1737 KB, twitter.json 632 KB) into each library's DOM, and stringify the DOM back to JSON; total time over the three files. |
| **Metric** | throughput |
| **Hardware** | MacBook Pro (Retina, 15-inch, Mid 2015), Intel Core i7-4980HQ @ 2.80GHz |
| **Compiler and flags** | clang 7.0 64-bit on macOS (README sample results, updated 2016-9-9); premake5 gmake build (build/premake.sh) in release configuration: optimize Full, NDEBUG, -march=native (build/premake5.lua) |
| **Adoption** | 3.4k stars |
| **Last commit** | 2026-07-09 |
| **Links** | [repository](https://github.com/akheron/jansson) · [benchmark](https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv) |

## Verdict

In nativejson-benchmark's committed 2016 sample (clang 7.0, full optimization with -march=native, Core i7-4980HQ, macOS), Jansson 2.7 stringified canada, citm_catalog and twitter in 69.9 ms total against JsonCpp 1.0.0's 94.3 ms (1.35x) and nlohmann/json 2.0.3's 87.7 ms, winning on each file; its 112.1 vs 165.5 ms parse total rests on canada.json alone. The project itself makes no speed claim.

## Use it when

- C code that needs to build, edit and re-emit JSON documents (configs, RPC payloads in the KB to low-MB range) with a small, stable, well-documented C API and no dependencies.
- Replacing JsonCpp 1.0.x-era serialization of small and medium documents, where the 2016 run showed the largest stringify gaps (citm_catalog 3.76 vs 5.68 ms, twitter 1.93 vs 4.14 ms).
- Untrusted input where hash flooding and stack exhaustion matter: object hashing is seeded at runtime (CVE-2013-6401 fix in 2.6) and parse, dump, equal and deep copy are depth-limited (JSON_PARSER_MAX_DEPTH, default 2048).
- Programs that want precise parse-error reporting (line, column, byte offset, enum json_error_code) or json_pack/json_unpack for building and validating small structures.

## Skip it when

- Throughput-critical parsing: in the same 2016 CSV, RapidJSON parsed the three files in 7.9 ms total, cJSON in 24.7 ms and nlohmann/json 2.0.3 in 72.5 ms, against Jansson's 112.1 ms.
- Object- and string-heavy documents where JsonCpp is the incumbent: Jansson 2.7 parsed citm_catalog (22.7 vs 14.6 ms) and twitter (10.9 vs 8.5 ms) slower than JsonCpp 1.0.0; its parse-total win comes only from canada.json.
- Large files (100 MB and up): issue #280 measured json_load_file at about 13 s on a 181 MB file against about 8 s for Python's json module, and issue #332 reported 413.3 MB of memory and 19,975,350 allocations for a 76.3 MB file (5.4x the input).
- Number-heavy output: json-c stringified canada.json in 16.3 ms against Jansson's 64.2 ms in the same run.
- Data needing unsigned 64-bit integers, bignums or exact decimals: only json_int_t (long long) and double are supported, and bignum support (issue #69) is still open.

## How it is fast

It is not built for speed: the parser is a recursive-descent lexer that pulls one byte at a time through a function-pointer stream (stream_get in src/load.c), tracks line and column per byte, copies each token into a growable strbuffer and converts numbers with strtod. Objects are chained hash tables with a seeded lookup3 hashlittle hash plus a second linked list for insertion order, and every value, string and pair is a separate malloc. Its stringify edge over JsonCpp 1.0.0 comes from writing compact output through a single growing strbuffer: the benchmark CSV shows 18-21 allocations per stringify for Jansson against 12,197 (citm_catalog) and 7,727 (twitter) for JsonCpp.

## Compared with alternatives

Pick Jansson over cJSON when you want its documented thread-safety rules, seeded hash-table objects, depth limits on every recursive operation, json_pack/json_unpack and detailed error positions; pick cJSON (4.5x faster parse in the same 2016 run) or yyjson when parse speed is what you are optimizing.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (autotools or CMake); small enough to vendor as source |
| **Dependencies** | none |
| **Minimum toolchain** | Plain C compiler (headers adjusted for C89 in 2.13); CMake 3.10+ for the CMake build, or autotools (autoreconf -i for git checkouts) |
| **Platforms** | any; changelog covers Linux, macOS, BSDs, Solaris, MSVC and MinGW builds |
| **Thread safety** | Library has no mutable global state except the hash seed and allocator hooks. Read-only sharing of values across threads is safe and reference counting uses compiler atomics when JANSSON_THREAD_SAFE_REFCOUNT is defined (2.11+); mutating a shared value needs external locking. Call json_object_seed(0) and json_set_alloc_funcs before spawning threads. |
| **Drop-in for the baseline** | no |

## Gotchas

- The measured version is v2.7 (2014). Since 2.8 object keys always keep insertion order (an extra ordered list per pair) and a crash on deeply nested input was fixed; since 2.14.1 reals are printed with David Gay's dtoa (USE_DTOA defaults ON); 2.15.0 merged serialization optimizations (#658, #719) with no published numbers. Current speed relative to any baseline is unmeasured.
- Before 2.15.1, dump, json_equal and deep copy recursed without a depth limit, so a deeply nested value built in code (not parsed) could overflow the stack; upgrade to 2.15.1 or later.
- Strings containing NUL are rejected unless JSON_ALLOW_NUL is passed; integers that overflow json_int_t are a parse error unless JSON_DECODE_INT_AS_REAL is set.
- No harness flaw found: nativejson-benchmark's janssontest.cpp times json_loads(json, 0) and json_dumps(root, JSON_COMPACT), the normal API calls, and JsonCpp is timed through its standard reader and writer builders. The weakness is the baseline (JsonCpp 1.0.0, 2016), not the harness.

## Known shortcomings

- Only win in the 2016 nativejson-benchmark run (clang 7.0, i7-4980HQ, -O3 -march=native NDEBUG) is over JsonCpp 1.0.0 (and nlohmann on stringify); the parse lead rests on canada.json. Loses parse to nlohmann, cJSON and RapidJSON and stringify to json-c.
- Enricher: stale baseline (v2.7 of 2014 vs JsonCpp 1.0.0 in the 2016 run; since then insertion-order lists in 2.8, dtoa real printing in 2.14.1 and unbenchmarked dump optimizations #658/#719 in 2.15.0). The parser reads one byte at a time through a function-pointer stream with one malloc per node; issue #332 (76.3 MB file used 413.3 MB, 5.4x) and #280 (181 MB file took 13 s vs Python json 8 s). The stringify win over JsonCpp is an allocation-count story (18-21 vs 12,197 allocations on citm_catalog).

## Caveats and trade-offs

Jansson makes no speed claim; this is a derived win in an independent suite. Results are from 2016 with Jansson v2.7 and JsonCpp 1.0.0 (current releases are far newer), on one macOS machine. The same suite shows Jansson parse far behind RapidJSON (7.9 ms total), cJSON (24.7 ms), Nlohmann 2.0.3 (72.5 ms) and others, and json-c stringifies much faster (30.8 ms total vs Jansson 69.9 ms). The independent ludocode/schemaless-benchmarks (GCC 5.3.0, -O3 -flto, Jansson 2.7) puts Jansson last in nearly every speed test: tree parse 105.18 us vs YAJL 99.31 us and RapidJSON in-situ 10.58 us, encode 63.40 us vs YAJL 37.86 us; its author calls Jansson 'even slower than YAJL'. Treat Jansson as a feature-rich mutable-tree library, not a fast one.

Mutable, reference-counted tree: every node is individually allocated (224,392 allocations for canada.json, 111,230 for citm_catalog.json, 43,822 for twitter.json in the CSV), strings are copied and object entries are kept in a hashtable (ludocode benchmark reports key reordering); in return it supports editing and re-encoding documents, full UTF-8 handling, detailed error positions and a stable C API with no dependencies.

## Maintenance

Actively maintained (2.15.1 released 2026-06-30, commits into July 2026), MIT, mature and widely packaged; usable and copyable, but the speed entry rests on a 2016 run of a 2014 release against a 2015 JsonCpp.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** Independent nativejson-benchmark suite: public harness (src/tests/janssontest.cpp and src/tests/jsoncpptest.cpp, json_loads/json_dumps(JSON_COMPACT) vs Json::CharReaderBuilder/StreamWriterBuilder), build via build/premake.sh (premake5 gmake) with release optimize Full, NDEBUG and -march=native (build/premake5.lua), clang 7.0 64-bit, CPU Core i7-4980HQ stated in README and CSV name. All per-file numbers in the record match the committed sample CSV.
- **Verifier notes:** Every figure checks out against the CSV (parse totals Jansson 112.06, JsonCpp 165.52, json-c 134.55, Nlohmann 72.48 ms; stringify Jansson 69.91, JsonCpp 94.26, Nlohmann 87.73, json-c 30.80 ms), and the schemaless-benchmarks caveat numbers and quote are also verified. Weak entry to record as a shortcoming: the win is only over JsonCpp 1.0.0 (and Nlohmann 2.0.3 on stringify) in a 2016 run; the parse win rests on canada.json alone, Jansson loses parse to JsonCpp on citm and twitter, and loses to Nlohmann, cJSON, RapidJSON on parse and to json-c on stringify; no project speed claim.
- **Fields the verifier corrected:** `compiler_and_flags`
- **Shortcomings recorded by:** nativejson-benchmark CSV (verifier); enricher code reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/README.md>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/build/premake5.lua>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/build/premake.sh>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/src/tests/janssontest.cpp>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/src/tests/jsoncpptest.cpp>
  - <https://raw.githubusercontent.com/ludocode/schemaless-benchmarks/HEAD/README.md>
  - <https://github.com/akheron/jansson>
  - <https://github.com/akheron/jansson/commits/master>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/akheron/jansson/HEAD/README.rst>
  - <https://raw.githubusercontent.com/akheron/jansson/HEAD/CHANGES>
  - <https://raw.githubusercontent.com/akheron/jansson/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/akheron/jansson/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/akheron/jansson/HEAD/src/jansson.h>
  - <https://raw.githubusercontent.com/akheron/jansson/HEAD/src/load.c>
  - <https://raw.githubusercontent.com/akheron/jansson/HEAD/src/dump.c>
  - <https://raw.githubusercontent.com/akheron/jansson/HEAD/src/value.c>
  - <https://raw.githubusercontent.com/akheron/jansson/HEAD/src/hashtable.c>
  - <https://raw.githubusercontent.com/akheron/jansson/HEAD/src/hashtable.h>
  - <https://raw.githubusercontent.com/akheron/jansson/HEAD/src/strbuffer.c>
  - <https://raw.githubusercontent.com/akheron/jansson/HEAD/src/memory.c>
  - <https://raw.githubusercontent.com/akheron/jansson/HEAD/src/jansson_private.h>
  - <https://raw.githubusercontent.com/akheron/jansson/HEAD/src/utf.c>
  - <https://raw.githubusercontent.com/akheron/jansson/HEAD/src/hashtable_seed.c>
  - <https://raw.githubusercontent.com/akheron/jansson/HEAD/doc/apiref.rst>
  - <https://raw.githubusercontent.com/akheron/jansson/HEAD/doc/conformance.rst>
  - <https://raw.githubusercontent.com/akheron/jansson/HEAD/doc/threadsafety.rst>
  - <https://github.com/akheron/jansson/pull/658>
  - <https://github.com/akheron/jansson/pull/719>
  - <https://github.com/akheron/jansson/issues?q=is%3Aissue+slow+OR+performance+OR+speed>
  - <https://github.com/akheron/jansson/issues/280>
  - <https://github.com/akheron/jansson/issues/332>
  - <https://github.com/akheron/jansson/issues/751>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/src/tests/janssontest.cpp>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/README.md>
  - <https://github.com/ibireme/yyjson_benchmark>
  - <https://raw.githubusercontent.com/ibireme/yyjson_benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/ibireme/yyjson_benchmark/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ibireme/yyjson_benchmark/HEAD/docs/reports/Intel_NUC_8i5_gcc_9.html>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/akheron/jansson`) · [data/wave4/enrich/raw/github_com_akheron_jansson.json](../../../data/wave4/enrich/raw/github_com_akheron_jansson.json) (enrichment confidence 0.75)

</details>
