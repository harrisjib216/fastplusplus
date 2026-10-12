# Lite³ (lite3)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Schemaless, JSON-compatible zero-copy C format: a B-tree in one mutable buffer; author runs beat FlatBuffers and simdjson.

| | |
|---|---|
| **Beats** | FlatBuffers |
| **Claimed result** | Cista++ cpp-serialization-benchmark fork, graph with 1870 nodes: serialize+deserialize takes 7.79 ms for the Lite³ Buffer API vs 1887.49 ms for FlatBuffers (242x, derived from page data; this is the project's '242x'). Serialize is 3.02 vs 1845.8 ms (611x, derived), deserialize/verify 4.77 vs 41.69 ms (8.7x, derived) and traverse 79.39 vs 90.53 ms (1.14x, derived). Message size is 38.069 MB vs 62.998 MB. zpp::bits (4.66 ms) and Cista++ offset slim (3.96 ms) beat Lite³ on serialize+deserialize. The 'up to 120x' claim is simdjson On-Demand find_tweet at 53937 ns vs 448 ns for the Lite³ Buffer API (120x, derived) on twitter.json. In that test Lite³ queries data pre-converted to its binary format while the other libraries parse JSON. |
| **Workload** | Three external suites, forked and run by the Lite³ author and linked from the README. (1) Cista++ cpp-serialization-benchmark: serialize, deserialize and traverse a node/edge graph, vs FlatBuffers, Cap'n Proto, cereal, zpp::bits and Cista++. (2) simdjson bench_ondemand queries on twitter.json (\~632 kB): top_tweet, partial_tweets, find_tweet and distinct_user_id, vs simdjson, yyjson and RapidJSON, with Lite³ on pre-converted binary data. (3) kostya/benchmarks JSON coordinate sum (\~115 MB). The lite3 repo has no harness of its own. |
| **Metric** | throughput |
| **Compiler and flags** | Cista++ fork: g++-11 with CMake Release for the benchmark; liblite3 is built by its Makefile default (-O2 -DNDEBUG). The simdjson and kostya forks state no compiler or flags. |
| **Adoption** | 807 stars |
| **Last commit** | 2026-08-06 |
| **Links** | [repository](https://github.com/fastserial/lite3) · [benchmark](https://github.com/fastserial/lite3#benchmarks) |

## Verdict

In the author's fork of the Cista++ graph benchmark (1,870 nodes; g++-11 CMake Release with liblite3 at -O2; CPU not stated), Lite³ serialize+deserialize takes 7.79 ms against 1887.49 ms for FlatBuffers. Nearly all of that gap is FlatBuffers serialize (1845.8 vs 3.02 ms), where its adapter builds per-edge tables through a std::map while the Lite³ adapter memcpys uint16 edge arrays as opaque byte blobs; deserialize (Lite³ copying out to std::vector against the FlatBuffers verifier) is 8.7x faster and traverse is about equal (79.4 vs 90.5 ms). The '120x' is find_tweet in the author's simdjson fork (448 ns vs 53,937 ns for simdjson On-Demand) on twitter.json already converted to Lite³, run on an x86-64 machine where simdjson picked its AVX-512 'icelake' kernel at \~3.8 GHz; model and conversion cost are not reported.

## Use it when

- C or C++ services that receive a message, read or change a few fields and forward it: gets and sets run on the received buffer, and sending is a memcpy with no re-serialize.
- JSON-shaped data with no fixed schema, stored or sent in Lite³ form and queried selectively. The author's find_tweet run takes 448 ns against 53,937 ns for simdjson On-Demand on twitter.json (\~632 kB), because the query reads only the nodes on its path.
- Both ends are your own C/C++ code and CPU cost matters more than bytes on the wire, with JSON conversion still available for debugging and for existing JSON APIs.
- Embedded or no-malloc code on little-endian 64-bit targets: the Buffer API never allocates, the core is 9.3 kB, and `make LITE3_JSON_LIBRARIES=0` leaves out yyjson and base64.
- Cases where FlatBuffers' IDL, codegen and lock-step schema upgrades are the real pain, and O(log n) field access is acceptable.

## Skip it when

- Bandwidth- or storage-bound links. Every message carries its keys, the design page reports \~40% more bytes than JSON on the Twitter data, and the README says to pick Protocol Buffers if you are bandwidth-constrained. In the author's graph run it is 38.1 MB, against 25.3 MB for Cista++ offset slim and 37.8 MB for zpp::bits (FlatBuffers: 63.0 MB).
- Data that arrives as JSON on every request. lite3_json_dec does a full yyjson parse and then rebuilds the tree as Lite³, so that path cannot beat yyjson, and the 120x query numbers leave out the conversion.
- Fixed-schema hot paths that need O(1) field access or the lowest encode+decode time. FlatBuffers, Cap'n Proto and SBE offer O(1) reads, and in the author's own graph run zpp::bits (4.66 ms) and Cista++ offset slim (3.96 ms) beat Lite³ (7.79 ms) on serialize+deserialize.
- Untrusted input in production today. A fuzz-found misaligned-access/undefined-behavior report (#20, April 2026) is still open, the repo has no fuzz harness, and there is no formal spec. The README calls the API unstable, and the author plans to replace the DJB2 hash, which would change the wire format.
- Big-endian or 32-bit targets (big-endian is a compile error; 32-bit support is future work), messages over 4 GiB, objects or arrays over 2^26 entries, and non-C languages: the Python bindings are an open PR, and the C++ (1 star) and C# ports are third-party.

## How it is fast

Each object or array is a B-tree laid out inside one contiguous buffer with 32-bit relative offsets. A 96-byte node (1.5 cache lines) holds up to 7 sorted 32-bit DJB2 key hashes, 7 key-value offsets and 8 child offsets, so a lookup walks at most 9 nodes comparing integers, and macros compute the hashes of string-literal keys at compile time. Values carry a 1-byte type tag and store i64/f64 natively in little-endian, so reads return pointers into the buffer, fixed-size overwrites happen in place, and iterators issue __builtin_prefetch for the next nodes and entries. The benchmark wins come from skipping work rather than from SIMD: in the simdjson fork, find_tweet on the converted data runs about 4.9k instructions, against 764k for simdjson On-Demand parsing the JSON.

## Compared with alternatives

Pick Lite³ over schema-based siblings such as YaFF, ProtoCache or SBE only when a schema/IDL is unacceptable, when you must mutate a received buffer in place and send it on, or when you need a lossless JSON round trip. With a known schema, those siblings give O(1) or near-O(1) reads and smaller messages, and rkyv covers the same zero-copy niche in Rust.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none for the core. JSON conversion uses vendored yyjson and nibble_base64 (in lib/, MIT), on by default and removable with LITE3_JSON_LIBRARIES=0. The Makefile uses GNU nm/objcopy to prefix the vendored symbols with lite3_internal_ and installs a pkg-config file. |
| **Minimum toolchain** | C11 with GNU extensions; the README requires GCC or Clang because of builtins. A C23-only label/declaration construct that broke GCC 9.4 and Clang 10 was fixed in PR #18. The headers have extern "C" guards, and the author's benchmark includes them from C++20 built with g++-11. |
| **Platforms** | Little-endian only (big-endian fails with #error); needs int64_t and 8-byte doubles; 32-bit CPUs are listed as future work. The README says it has not been tested on ARM, and the header warns that the default LITE3_PREFETCHING can crash on non-x86 platforms near unmapped pages or on messages with invalid offsets. Published runs were on x86-64. |
| **Thread safety** | Read-only calls (get, iterators, JSON encode) are documented as thread-safe on a shared buffer. Any mutation, including JSON decode into a buffer, needs external locking, and mixing reads with writes is not safe. |
| **Drop-in for the baseline** | no |

## Gotchas

- Object keys are ordered by their 32-bit DJB2 hash, so iteration and JSON output do not keep insertion order (the README's own example prints "method" before "event"). The hash is unseeded (fixed start value 5381), and quadratic probing is capped at LITE3_HASH_PROBE_MAX = 128 attempts.
- String and bytes results are generation-stamped references. Read them only through LITE3_STR()/LITE3_BYTES(), which return NULL after any mutation of the buffer; dereferencing .ptr directly is unsafe. PR #23 (merged Aug 2026) made mutations of nested objects invalidate these references too, and the message start must be 4-byte aligned.
- A failed set can still write to the buffer and increase buflen. Overwriting a string or bytes value with a larger one appends it and never reclaims the old space. lite3.h has no key-delete call, and the only way to compact is to rewrite the message into a new buffer. The Context API grows by 4x via realloc, and its docs advise against it for latency-sensitive code unless you preallocate.
- JSON conversion: unsigned integers above INT64_MAX silently become f64, nesting is capped at 32 levels, and bytes become base64 strings. Library error messages are off by default (LITE3_ERROR_MESSAGES), so failures show only as -1 plus errno.

## Known shortcomings

- The 242x headline is serialize+deserialize against a FlatBuffers adapter that builds through std::map while Lite3 copies pre-flattened arrays; deserialize alone is 8.7x, traverse is about even, and zpp::bits beats Lite3 overall. The 120x figure compares simdjson parsing JSON against Lite3 querying already-converted binary data. No CPU model stated.
- The 120x omits conversion: lite3_json_dec does a full yyjson parse first, so any JSON-ingest path cannot beat yyjson. Open fuzz-found misaligned-access report (#20) and no fuzz harness despite the untrusted-input claim. No releases or spec, API unstable, and a planned hash change will alter the wire format.

## Caveats and trade-offs

All numbers are author-run on forks of external suites, with no CPU model stated. The 242x figure is serialize-dominated: the upstream FlatBuffers adapter builds per-edge tables through a std::map lookup, while the Lite³ adapter memcpys pre-flattened index-based edge arrays as opaque byte blobs. Deserialize is only 8.7x faster and traverse is about equal. zpp::bits and Cista++ offset slim beat Lite³ on serialize+deserialize. The 120x JSON comparisons pit JSON parsing against queries on data already converted to Lite³, so they are not like-for-like. The upstream Cista suite (felixguendling, 37 stars) does not include Lite³.

Core library is C, not C++ (a separate C++ port, jasoncoposky/lite3-cpp, exists but has only 1 star and is unverified for the same performance); schemaless self-describing design costs \~40% extra size vs raw JSON on the cited Twitter dataset; O(log n) rather than O(1) field access

## Maintenance

Active (last commit 2026-08-06, created Nov 2025, 807 stars) and MIT, with a \~9.3 kB dependency-free C core that is easy to vendor. But there are no tagged releases or formal spec, only third-party ports exist outside C, and the API and wire format are declared unstable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The numbers come from author-run forks of external suites (fastserial/cpp-serialization-benchmark, fastserial/simdjson, fastserial/kostya-benchmark). Each fork has public code, but the Lite³ author wrote the adapters, and no upstream suite includes Lite³. Only the Cista++ fork names a compiler (g++-11, CMake Release). No CPU model is stated anywhere, and the 242x figure exceeds 50x, so this stays at C.
- **Verifier notes:** The record said there was no reproducible harness, but the README links three public benchmark forks with raw output files, so benchmark_url now points at the README Benchmarks section. The tier stays C. The headline 242x and 120x ratios are real on the pages but are derived from uneven comparisons, and claimed_speedup now spells that out. Metadata checks out: MIT, 807 stars, last commit 2026-08-06, active.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/fastserial/lite3>
  - <https://github.com/fastserial/lite3/blob/main/README.md>
  - <https://github.com/fastserial/lite3/blob/main/LICENSE>
  - <https://github.com/fastserial/lite3/blob/main/Makefile>
  - <https://lite3.io/design_and_limitations.html>
  - <https://lite3.io/>
  - <https://github.com/fastserial/cpp-serialization-benchmark>
  - <https://github.com/fastserial/cpp-serialization-benchmark/blob/master/README.md>
  - <https://github.com/fastserial/cpp-serialization-benchmark/blob/master/cpp_serialization_benchmark_output.txt>
  - <https://github.com/fastserial/cpp-serialization-benchmark/blob/master/cpp_serialization.csv>
  - <https://github.com/fastserial/cpp-serialization-benchmark/blob/master/CMakeLists.txt>
  - <https://github.com/fastserial/cpp-serialization-benchmark/blob/master/include/csb/benches/lite3.h>
  - <https://github.com/fastserial/cpp-serialization-benchmark/blob/master/include/csb/benches/fbs.h>
  - <https://github.com/fastserial/cpp-serialization-benchmark/blob/master/definitions/graph.fbs>
  - <https://github.com/fastserial/simdjson>
  - <https://github.com/fastserial/simdjson/blob/master/README.md>
  - <https://github.com/fastserial/simdjson/blob/master/simdjson_output.txt>
  - <https://github.com/fastserial/kostya-benchmark>
  - <https://github.com/fastserial/kostya-benchmark/blob/master/README.md>
  - <https://github.com/fastserial/kostya-benchmark/blob/master/kostya_benchmark_output.txt>
  - <https://github.com/felixguendling/cpp-serialization-benchmark>
- **Sources the enricher read:**
  - <https://github.com/fastserial/lite3>
  - <https://github.com/fastserial/lite3/blob/main/README.md>
  - <https://github.com/fastserial/lite3/blob/main/include/lite3.h>
  - <https://github.com/fastserial/lite3/blob/main/include/lite3_context_api.h>
  - <https://github.com/fastserial/lite3/blob/main/src/lite3.c>
  - <https://github.com/fastserial/lite3/blob/main/src/json_dec.c>
  - <https://github.com/fastserial/lite3/blob/main/Makefile>
  - <https://github.com/fastserial/lite3/blob/main/lite3.pc>
  - <https://github.com/fastserial/lite3/commits/main>
  - <https://github.com/fastserial/lite3/releases>
  - <https://github.com/fastserial/lite3/tags>
  - <https://github.com/fastserial/lite3/issues>
  - <https://github.com/fastserial/lite3/issues/20>
  - <https://github.com/fastserial/lite3/issues/17>
  - <https://github.com/fastserial/lite3/issues/19>
  - <https://github.com/fastserial/lite3/issues/16>
  - <https://github.com/fastserial/lite3/issues/3>
  - <https://github.com/fastserial/lite3/pulls>
  - <https://github.com/fastserial/lite3/pull/21>
  - <https://lite3.io/design_and_limitations.html>
  - <https://github.com/fastserial/cpp-serialization-benchmark/blob/master/include/csb/benches/lite3.h>
  - <https://github.com/fastserial/cpp-serialization-benchmark/blob/master/include/csb/benches/fbs.h>
  - <https://github.com/fastserial/cpp-serialization-benchmark/blob/master/include/csb/lite3_graph.h>
  - <https://github.com/fastserial/cpp-serialization-benchmark/blob/master/CMakeLists.txt>
  - <https://github.com/fastserial/cpp-serialization-benchmark/blob/master/cpp_serialization_benchmark_output.txt>
  - <https://github.com/fastserial/simdjson>
  - <https://github.com/fastserial/simdjson/blob/master/README.md>
  - <https://github.com/fastserial/simdjson/blob/master/simdjson_output.txt>
  - <https://github.com/fastserial/simdjson/blob/master/benchmark/find_tweet/lite3.h>
  - <https://github.com/fastserial/kostya-benchmark/blob/master/README.md>
  - <https://github.com/jasoncoposky/lite3-cpp>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/fastserial/lite3`) · [data/wave4/enrich/raw/github_com_fastserial_lite3.json](../../../data/wave4/enrich/raw/github_com_fastserial_lite3.json) (enrichment confidence 0.8)

</details>
