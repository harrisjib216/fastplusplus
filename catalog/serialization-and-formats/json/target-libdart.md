# libdart

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> C++14 JSON library whose finalized flat binary packets parse 9.2x faster than nlohmann/json and read with zero parsing.

| | |
|---|---|
| **Beats** | nlohmann/json (version not stated); the same run also has RapidJSON, sajson, YAJL and Jansson |
| **Claimed result** | Single-run table, ns per pass over the input: Dart finalized parse 27682 vs nlohmann 254695 (9.2x), Dart dynamic parse 158967 vs nlohmann 254695 (1.6x), Dart key lookups 3803 vs 8471 (2.2x), Dart finalized serialize 36241 vs nlohmann 68175 (1.9x), Dart dynamic serialize 43105 vs 68175 (1.6x) (ratios derived from page data). sajson parses faster than Dart (14360 ns) and RapidJSON in-situ is close (34035 ns). PARSING.md: Dart runs 'within about 50% of RapidJSON' on parse. |
| **Workload** | Google Benchmark run (benchmark/configurable.cc) over the repo's benchmark/input.json (newline-separated JSON packets): parse each packet to a DOM (Dart from_json, which in this build tokenizes with sajson and then lowers into Dart's sorted finalized buffer or dynamic heap), key lookups on pre-parsed results, and serialize back to a string. |
| **Metric** | throughput |
| **Hardware** | 'middle-end 2018 MacBook Pro'; Google Benchmark header reports 8 X 2300 MHz CPUs, L3 6291K; exact CPU model not named |
| **Compiler and flags** | -O3 -DNDEBUG plus dart_default_compile_options (benchmark/CMakeLists.txt); the benchmark CMake defines DART_USE_SAJSON when sajson.h is found, which switches Dart's parser to sajson; compiler and version not stated |
| **Adoption** | 80 stars |
| **Last commit** | 2021-09-11 |
| **Links** | [repository](https://github.com/target/libdart) · [benchmark](https://raw.githubusercontent.com/target/libdart/HEAD/PARSING.md) |

## Verdict

One single-run Google Benchmark on a 2018 MacBook Pro (8 x 2.3 GHz, -O3, compiler and nlohmann version not stated) over 10 generated JSON packets of about 1 KB: Dart's sajson-backed finalized parse took 27682 ns per pass vs 254695 ns for nlohmann/json (9.2x), dynamic parse 158967 ns (1.6x), top-level key lookups 3803 vs 8471 ns (2.2x) and finalized serialization 36241 vs 68175 ns (1.9x); sajson alone took 14360 ns and RapidJSON 45588 ns, so the parse win is mostly sajson versus nlohmann.

## Use it when

- Pipelines that parse a message once and fan it out to other processes, machines or shared-memory queues: a finalized dart::buffer is a contiguous, little-endian, architecture-independent byte block readers can use without reparsing.
- Read-heavy access to objects with many keys: top-level key lookups took 3803 ns vs 8471 ns for nlohmann/json and 6180 ns for RapidJSON per pass over 10 packets with 22 keys each.
- Streams of small (about 1 KB) documents where a sajson-backed finalized parse (27682 ns per 10.7 KB pass, about 386 MB/s, derived from page data) is enough and an STL-like API matters more than peak tokenizer speed.
- C++14 code that wants idiomatic construction from STL types plus a stable C89 ABI for bindings.

## Skip it when

- Raw parse-and-discard throughput: sajson alone parsed the same input in 14360 ns (1.9x faster than Dart, which wraps it), and simdjson or yyjson are faster still.
- Mutation-heavy work: the dynamic dart::heap parse took 158967 ns, 3.5x slower than RapidJSON's DOM (45588 ns) and only 1.6x faster than nlohmann; going from mutable to finalized needs an explicit lowering step.
- Anything that needs insertion-ordered keys, exact 64-bit integers or correctly rounded doubles while using the sajson-backed fast path (see gotchas).
- Projects that need a maintained dependency: the repository was archived on 2024-07-16 with the last commit on 2021-09-11, and it also requires GSL plus RapidJSON or sajson.
- Memory-tight services: every finalized parse allocates eight times the JSON text size.

## How it is fast

The finalized path tokenizes with sajson (when built with DART_USE_SAJSON) and then lowers the tree in one pass into a single aligned allocation laid out as sorted object vtables, so a document costs a few large allocations instead of one per node and std::string key. Key lookup is a binary search over a lexicographically sorted vtable whose 8-byte entries cache a 2-byte key prefix, so the search stays inside the small vtable until a likely match (described in IMPLEMENTATION.md). Numbers are stored at the narrowest exact width (int16/int32/int64, float only when the double round-trips), and finalized reads never allocate.

## Compared with alternatives

Pick libdart over sajson, simdjson or yyjson only when you want the parsed result as a relocatable zero-copy binary buffer with fast sorted-key lookup and an STL-like C++ API; for parse-and-read-once workloads sajson (which Dart wraps), simdjson or yyjson are faster, and simdjson and yyjson are still maintained.

## Integration

| | |
|---|---|
| **Form** | header-only (optional static/shared dart_abi library for the C89 interface) |
| **Dependencies** | Microsoft GSL (or gsl-lite); RapidJSON or sajson for JSON conversion; libyaml optional for YAML; Google Benchmark only for the benchmarks |
| **Minimum toolchain** | C++14; clang 3.8+, gcc 5.0+, Apple clang 8.3+, MSVC about 19.22 |
| **Platforms** | Linux and macOS primarily; Windows experimental; a 32-bit build option exists; the wire format is little-endian regardless of host |
| **Thread safety** | Default refcounting is std::shared_ptr (atomic) with copy-on-write, so packets can be shared across threads; dart::unsafe_ptr instantiations and view types are not thread-safe |
| **Drop-in for the baseline** | no |

## Gotchas

- The measured fast path is not the default build: the library option use_sajson is OFF, but benchmark/CMakeLists.txt defines DART_USE_SAJSON whenever sajson.h is found. In that path sajson keeps only 32-bit integers (larger ones become doubles, so Dart types them as decimals and loses precision above 2^53) and parses doubles by accumulating digits and multiplying by a power-of-ten table, which is not correctly rounded; the 2016 sajson in nativejson-benchmark failed 28 of 66 double tests. The benchmark input (10 packets, 150 integers all below 2^31, no floating-point values) never exercises either case, while nlohmann converts with full int64/correctly rounded semantics.
- Harness details: every Dart row uses dart::unsafe_ptr (non-atomic refcount) rather than the default std::shared_ptr; the key-lookup counter adds the packet count per packet instead of the key count, so its 'parsed key lookups/s' label is mis-scaled (the ns column is unaffected); the YAJL generator emits false for true values.
- basic_buffer::from_json allocates json.size() \* 8 bytes for every finalized parse (marked FIXME in the source) and keeps that block as the packet storage.
- Network constructors only check for null and 8-byte alignment; call dart::is_valid() on bytes from an untrusted source before wrapping them. Subscript returns a temporary, so obj["nested"].pop_back() silently mutates a copy and obj["k"] = v does not compile.

## Known shortcomings

- PARSING.md numbers: commit 3d45bc0 (2019-06-01) made sajson the finalized parser, so the 27682 ns figure is sajson plus lowering, not RapidJSON (the RapidJSON-backed figure was 66174 ns), and the 9.2x over an unversioned nlohmann is mostly sajson's win. Compiler and CPU model unstated. Archived 2024-07-16; Apache-2.0.
- Enricher: the measured fast path is the sajson build (use_sajson OFF by default; the benchmark CMake turns it on when sajson.h is found); sajson keeps only int32 integers (larger ones become doubles, precision lost above 2^53) and its doubles are not correctly rounded (28/66 double tests failed in 2016), while the bench input (10 packets of about 1 KB, 150 small ints, no doubles) exercises neither case. Dart rows use unsafe_ptr; the key-lookup counter is mis-scaled; the YAJL generator writes false for true; the finalized parse allocates json.size()\*8.

## Caveats and trade-offs

First-party numbers from a single run on a 2018 laptop (the doc itself calls single-run output noisy and says the graphs use 16 repetitions, which are images not text). nlohmann version (found as a system install by find_path) and compiler are not stated, so tier A is not met. Dart is not a tokenizer of its own here: the table was regenerated in commit 3d45bc0 ('Added a new, stupid-fast, sajson based parser', 2019-06-01), where Dart's from_json parses with sajson (include/dart/connector/json.tcc under DART_USE_SAJSON) and then lowers into the Dart buffer; that commit replaced the RapidJSON-backed finalized-parse figure of 66174 ns with 27682 ns. A default library build without the use_sajson option parses through RapidJSON and is slower than the quoted figure, so the 9.2x win over nlohmann mostly reflects sajson versus nlohmann; sajson alone parses in 14360 ns and the project's text says sajson is the choice for raw parse speed. The 'within about 50% of RapidJSON' sentence predates the sajson path. The key-lookup row measures lookups in Dart's sorted flat buffer on pre-parsed packets, not parse work. Dart requires lexicographically sorted object keys. The repo's LICENSE file is Apache-2.0 although the list tag said MIT. The repo was archived by the owner on Jul 16, 2024 and the last commit is 2021-09-11. [retier] First-party PARSING.md numbers; since commit 3d45bc0 (2019-06-01) the finalized parser is sajson, so the 27682 ns figure is sajson plus lowering (the RapidJSON-backed figure was 66174 ns) and the 9.2x over an unversioned nlohmann is mostly sajson's win. use_sajson is OFF by default; the benchmark CMake enables it when sajson.h is found. sajson keeps only int32 integers (larger become doubles, precision lost above 2^53) and its doubles are not correctly rounded (28/66 double tests failed in 2016); the bench input (10 packets of about 1 KB, 150 small ints, no doubles) exercises neither. Dart rows use unsafe_ptr; the key-lookup counter is mis-scaled (ns column fine); the YAJL generator writes false for true; the finalized parse allocates json.size()\*8. Compiler and CPU model unstated. Archived 2024-07-16; Apache-2.0.

Object keys are stored lexicographically sorted (iteration order is stable but not insertion order); no incremental parsing; finalized packets are immutable flat buffers, mutation needs a dynamic heap form and an expensive lowering step; copy-on-write reference counting (thread-unsafe pointer used in the benchmark). Header-only C++14 interface plus an ABI-stable C89 interface. JSON parsing itself is delegated to RapidJSON or sajson, YAML to libyaml.

## Maintenance

Abandoned (archived 2024-07-16, last commit 2021-09-11) but Apache-2.0 and header-only, so vendorable; the headline 9.2x depends on building with sajson, whose 32-bit integer cap and non-correctly-rounded double parsing change number fidelity relative to the default RapidJSON path and to nlohmann.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party single-run Google Benchmark output in PARSING.md from public code (benchmark/configurable.cc, -O3 -DNDEBUG in benchmark/CMakeLists.txt), but compiler, compiler version, nlohmann version and the exact CPU model are not stated, so it falls short of A and is not independent.
- **Verifier notes:** All quoted ns figures match the PARSING.md table and the derived ratios are correct; confirmed at tier C. Main correction: the finalized-parse figure comes from the sajson-backed parser (commit 3d45bc0), not RapidJSON, so the headline 9.2x over nlohmann is sajson plus lowering versus an unversioned nlohmann. Metadata confirmed: Apache-2.0, 80 stars, not a fork, archived 2024-07-16, last commit 2021-09-11 (abandoned).
- **Fields the verifier corrected:** `workload`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** first-party PARSING.md (verifier); enricher harness reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/target/libdart/HEAD/PARSING.md>
  - <https://github.com/target/libdart>
  - <https://github.com/target/libdart/tree/master/benchmark>
  - <https://raw.githubusercontent.com/target/libdart/HEAD/benchmark/configurable.cc>
  - <https://raw.githubusercontent.com/target/libdart/HEAD/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/target/libdart/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/target/libdart/HEAD/include/dart/connector/json.tcc>
  - <https://github.com/target/libdart/commits/master>
  - <https://github.com/target/libdart/commits/master/PARSING.md>
  - <https://github.com/target/libdart/commits/master/benchmark/CMakeLists.txt>
  - <https://github.com/target/libdart/commit/3d45bc0>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/target/libdart/HEAD/README.md>
  - <https://raw.githubusercontent.com/target/libdart/HEAD/PARSING.md>
  - <https://raw.githubusercontent.com/target/libdart/HEAD/PERFORMANCE.md>
  - <https://raw.githubusercontent.com/target/libdart/HEAD/IMPLEMENTATION.md>
  - <https://raw.githubusercontent.com/target/libdart/HEAD/ADVANCED.md>
  - <https://raw.githubusercontent.com/target/libdart/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/target/libdart/HEAD/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/target/libdart/HEAD/benchmark/configurable.cc>
  - <https://raw.githubusercontent.com/target/libdart/HEAD/benchmark/input.json>
  - <https://raw.githubusercontent.com/target/libdart/HEAD/include/dart.h>
  - <https://raw.githubusercontent.com/target/libdart/HEAD/include/dart/common.h>
  - <https://raw.githubusercontent.com/target/libdart/HEAD/include/dart/common.tcc>
  - <https://raw.githubusercontent.com/target/libdart/HEAD/include/dart/connector/json.tcc>
  - <https://raw.githubusercontent.com/target/libdart/HEAD/include/dart/buffer/buffer.h>
  - <https://raw.githubusercontent.com/target/libdart/HEAD/include/dart/buffer/api.tcc>
  - <https://raw.githubusercontent.com/target/libdart/HEAD/include/dart/buffer/detail.tcc>
  - <https://github.com/target/libdart/tree/master/include/dart>
  - <https://github.com/target/libdart/tree/master/include/dart/buffer>
  - <https://github.com/target/libdart/issues?q=is%3Aissue>
  - <https://github.com/target/libdart/issues/3>
  - <https://raw.githubusercontent.com/chadaustin/sajson/master/include/sajson.h>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/sample/conformance.csv>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/target/libdart`) · [data/wave4/enrich/raw/github_com_target_libdart.json](../../../data/wave4/enrich/raw/github_com_target_libdart.json) (enrichment confidence 0.75)

</details>
