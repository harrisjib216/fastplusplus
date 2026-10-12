# Cista++

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Reflection and code generation](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++17 zero-copy serializer for native structs; beats cereal \~48x serializing and \~670x deserializing flat index-linked graphs.

| | |
|---|---|
| **Beats** | cereal |
| **Claimed result** | Cista++ `offset` (slim variant) vs cereal: serialize 4 ms vs 216 ms, deserialize 0.16 ms vs 111.00 ms, deserialize & traverse 66 ms vs 174 ms (derived from page data: \~54x, \~690x, \~2.6x); serialized size 25.3M vs 37.8M. Traverse alone is 67 ms for both. Compile time (clang-7 on Mac OS X): Cista++ `raw` 1.351 s vs cereal 1.827 s |
| **Workload** | Serialize/deserialize/traverse a graph of nodes and edges (object-oriented graph with pointers/indices) using the 'offset' and 'raw' variants of Cista++, compared to cereal, Cap'n Proto, and FlatBuffers |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 9 5900X, Ubuntu 20.04 |
| **Compiler and flags** | GCC 11, CMAKE_BUILD_TYPE=Release from the README build steps (CMakeLists.txt adds no other optimization flags; C++20); compile-time table uses clang-7 on Mac OS X |
| **Adoption** | 2.3k stars |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/felixguendling/cista) · [benchmark](https://github.com/felixguendling/cpp-serialization-benchmark#readme) |

## Verdict

The author's cpp-serialization-benchmark (Google Benchmark, GCC 11, Release, C++20, AMD Ryzen 9 5900X, Ubuntu 20.04, run 2021-12-18 with a CPU-scaling warning) used a 1,870-node graph stored as index-linked Cista offset 'slim' structs. It serialized in 4.5 ms vs cereal's 216 ms, checked-deserialized in 0.165 ms vs 111 ms, and did unchecked deserialize plus traverse in 66 ms vs 174 ms; traversal alone was about 67 ms for both because a std::set dominates it. The slim layout packs each edge into a 32-bit bitfield while cereal's graph uses three uint16 fields, so the 25.3 MB vs 37.8 MB size gap and the serialize time reflect the benchmark's data layout as well as the library.

## Use it when

- Large read-mostly C++ datasets (routing graphs, GIS data, game assets, lookup tables) that you want to mmap and query straight away with no parse step. Checked deserialize of a 25 MB graph took 0.165 ms, against 111 ms for cereal.
- Data already laid out as flat arrays that reference each other by index, like the benchmark's 'slim' graph. Here serialize is mostly block copies (4.5 ms vs cereal's 216 ms).
- Shared memory, or moving data between C++ processes built for the same pointer width, where the receiver should read fields in place.
- You want a hash_map/hash_set (Swiss-table style, 8-byte SWAR control groups) that can be serialized, plus a type-hash version stamp and optional checksum, without writing a schema or adding macros.

## Skip it when

- Pointer-heavy object graphs. In the same 2021 run, the pointer-based Cista offset graph (unique_ptr nodes, ptr edges) took 659 ms to serialize and 248 ms to checked-deserialize, vs cereal's 216 ms and 111 ms. Raw mode took 650 ms and 256 ms checked; its 24.8 ms is the unchecked path.
- You need other languages or schema evolution. Only C++ can read the data. The type hash detects layout changes but migrates nothing, and downward compatibility means hand-dispatching on your own version field.
- Readers and writers with different pointer widths (wasm32 vs x64, Win32 vs 64-bit macOS). offset_t is intptr_t, so this only works after patching it to int64_t (issues #212, #281).
- Compact wire messages. Every value takes sizeof(T) bytes, and a variant is always sized for its largest alternative (#121). The pointer-based graph came to 176 MB vs cereal's 37.8 MB. zpp_bits, in the same benchmark, matched Cista's serialize time (4.14 ms) using std containers.
- Untrusted input with cyclic pointers when you won't pay for mode::DEEP_CHECK. The default check does not prove that cyclic structures have no dangling pointers, and the wiki warns that modifying deserialized untrusted data is unsafe.

## How it is fast

It is zero-copy: serialize copies each struct and container buffer into the output, then rewrites pointer fields as self-relative offsets, using an address-to-offset hash map to resolve pointers. In offset mode, deserialize never parses or allocates: it is one pass that checks pointer bounds and alignment or, with UNCHECKED/CAST, a reinterpret_cast of the buffer. offset::ptr is a position-independent self-relative pointer (the Boost.Interprocess offset_ptr idea), so a read-only mmap works wherever the file lands, while raw mode rewrites offsets into absolute pointers in place on load. Reflection comes from C++17 aggregate-arity detection plus structured bindings (to_tuple), and byte-swapping compiles out when host and format byte order match.

## Compared with alternatives

Pick Cista over bitsery, YAS or struct_pack when the reader should use the data in place: mmap a big graph, hash map or asset file and query it with no decode or allocation, with every reader a C++ build of the same pointer width. The catalogued wins for those siblings (and FBE) are encode/decode round-trips of message-like objects, which fit better for compact network messages or types that must stay std::vector/std::string.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none required (a single amalgamated cista.h, or a CMake INTERFACE target). Optional: fmt when CISTA_FMT is defined, xxh3 or wyhash (bundled) via CISTA_HASH, mimalloc via CISTA_USE_MIMALLOC |
| **Minimum toolchain** | C++17. The maintainer says all features need GCC 9+ (GCC 7/8 have known issues). Users report Clang 10+ and MSVC 2017+ working. CI runs GCC 12, Clang 17 (libc++, ASan/UBSan) and current MSVC |
| **Platforms** | Any target whose byte order the header can detect (otherwise #error). CI covers Linux x86-64 and Windows amd64/x86. Reader and writer must share pointer width. Big-endian hosts byte-swap in place, so the buffer must be writable |
| **Thread safety** | not documented. The containers have no internal locking (none in the vector/hash_storage headers read). Raw-mode or byte-swapping deserialize writes into the buffer, so deserialize once before sharing it |
| **Drop-in for the baseline** | no |

## Gotchas

- deserialize returns a pointer into your buffer, so the buffer must outlive every use of it. The buffer must also be aligned: a misaligned one throws 'ptr alignment' (copy_from_potentially_unaligned handles that case), and cista_exception is thrown on any failed check.
- A raw pointer that doesn't point into serialized data (not owned by a unique_ptr or an indexed container) is written as null. The only sign is a printf 'warning: dangling pointer' to stdout; nothing is thrown.
- Structs are copied byte for byte, padding included. The benchmark adds explicit filler fields, and CISTA_ZERO_OUT exists to zero fresh memory. Plain aggregates also get a second per-field write pass (for endian conversion), while the 4.5 ms headline type skips it with empty serialize/deserialize overloads on its bitfield edges.
- The CMake option CISTA_FMT defaults to ON and pulls in fmt headers, so builds without fmt fail unless you pass -DCISTA_FMT=OFF (CI does this). The v0.16 amalgamated header had to be regenerated for fmt breakage (#226, #264).

## Caveats and trade-offs

Benchmark numbers come from felixguendling's own companion repo (cpp-serialization-benchmark), so they are first-party, but methodology (code, compiler, build type, CPU) is public, which is why it qualifies for tier A. The run is from 2021-12-18 (benchmark_result.txt) with Cista pinned as a submodule at d3492bf; the benchmark repo has not changed since 2021-12-31, and that run warns that CPU scaling was enabled. The 1.351 s compile time is for the `raw` variant, and `raw` serializes slower than cereal (650 ms vs 216 ms); the win is for the `offset` slim variant. The main cista README shows an older 2019 run (72 ms vs 239 ms serialize), which points the same direction. The very large deserialize speedup vs cereal is an architectural effect of zero-copy access (no parsing step), not a benchmarking artifact.

The zero-copy 'offset' variant requires reading/writing in a fixed pointer-offset layout (no relocation), so both ends must share pointer width/endianness; the 'raw' variant (native pointers, relocatable) is far slower to serialize (3555ms) because of the extra relocation pass. Not schema-evolution-friendly like protobuf/capnproto without opt-in versioning.

## Maintenance

Actively maintained: last commit 2026-09-25 (a bitvec fix), recent offset-container move and AMD GPU work, latest release v0.16 (2025-09-06). It is mostly one maintainer (547 commits by the author), MIT-licensed, and ships as a single header that is easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** cpp-serialization-benchmark README runs Cista++ against cereal on the same graph workload with public code (src/main.cc, src/cista.cc, src/cereal.cc, Google Benchmark). It states GCC 11, the Release build type (README build steps), and AMD Ryzen 9 5900X; the raw output is in benchmark_result.txt.
- **Verifier notes:** Numbers match the Cista++ `offset` row (= cista_offset_slim_bench in benchmark_result.txt); ratios were not marked as derived, now fixed. Compile-time figure belonged to the `raw` row. Metadata correct (MIT, 2,253 stars, last commit 2026-09-25, active).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/felixguendling/cista>
  - <https://github.com/felixguendling/cista/blob/master/README.md>
  - <https://github.com/felixguendling/cista/commits>
  - <https://github.com/felixguendling/cpp-serialization-benchmark#readme>
  - <https://github.com/felixguendling/cpp-serialization-benchmark>
  - <https://github.com/felixguendling/cpp-serialization-benchmark/blob/master/CMakeLists.txt>
  - <https://github.com/felixguendling/cpp-serialization-benchmark/blob/master/benchmark_result.txt>
  - <https://github.com/felixguendling/cpp-serialization-benchmark/tree/master/src>
  - <https://github.com/felixguendling/cpp-serialization-benchmark/tree/master/external_lib>
- **Sources the enricher read:**
  - <https://github.com/felixguendling/cista>
  - <https://github.com/felixguendling/cista/blob/master/README.md>
  - <https://github.com/felixguendling/cista/blob/master/include/cista/serialization.h>
  - <https://github.com/felixguendling/cista/blob/master/include/cista/mode.h>
  - <https://github.com/felixguendling/cista/blob/master/include/cista/verify.h>
  - <https://github.com/felixguendling/cista/blob/master/include/cista/exception.h>
  - <https://github.com/felixguendling/cista/blob/master/include/cista/cista_exception.h>
  - <https://github.com/felixguendling/cista/blob/master/include/cista/endian/conversion.h>
  - <https://github.com/felixguendling/cista/blob/master/include/cista/endian/detection.h>
  - <https://github.com/felixguendling/cista/blob/master/include/cista/offset_t.h>
  - <https://github.com/felixguendling/cista/blob/master/include/cista/reflection/arity.h>
  - <https://github.com/felixguendling/cista/blob/master/include/cista/reflection/to_tuple.h>
  - <https://github.com/felixguendling/cista/blob/master/include/cista/containers/offset_ptr.h>
  - <https://github.com/felixguendling/cista/blob/master/include/cista/containers/hash_storage.h>
  - <https://github.com/felixguendling/cista/blob/master/include/cista/containers/vector.h>
  - <https://github.com/felixguendling/cista/blob/master/include/cista/atomic.h>
  - <https://github.com/felixguendling/cista/blob/master/include/cista/mmap.h>
  - <https://github.com/felixguendling/cista/blob/master/include/cista/targets/buf.h>
  - <https://github.com/felixguendling/cista/blob/master/include/cista/type_hash/type_hash.h>
  - <https://github.com/felixguendling/cista/blob/master/include/cista/strong.h>
  - <https://github.com/felixguendling/cista/blob/master/CMakeLists.txt>
  - <https://github.com/felixguendling/cista/blob/master/.github/workflows/linux.yml>
  - <https://github.com/felixguendling/cista/blob/master/.github/workflows/windows.yml>
  - <https://github.com/felixguendling/cista/blob/master/test/std_vector_test.cc>
  - <https://github.com/felixguendling/cista/blob/master/test/downward_compat_test.cc>
  - <https://github.com/felixguendling/cista/wiki/Security>
  - <https://github.com/felixguendling/cista/wiki/Serialization-Reference>
  - <https://github.com/felixguendling/cista/wiki/Installation-and-Usage>
  - <https://github.com/felixguendling/cista/wiki/Data-Structure-Versioning>
  - <https://github.com/felixguendling/cista/issues>
  - <https://github.com/felixguendling/cista/issues/281>
  - <https://github.com/felixguendling/cista/issues/279>
  - <https://github.com/felixguendling/cista/issues/70>
  - <https://github.com/felixguendling/cista/issues/270>
  - <https://github.com/felixguendling/cista/issues/264>
  - <https://github.com/felixguendling/cista/issues/222>
  - <https://github.com/felixguendling/cista/issues/212>
  - <https://github.com/felixguendling/cista/issues/121>
  - <https://github.com/felixguendling/cista/issues/265>
  - <https://github.com/felixguendling/cista/pull/278>
  - <https://github.com/felixguendling/cista/releases>
  - <https://github.com/felixguendling/cista/commits>
  - <https://cista.rocks/>
  - <https://github.com/felixguendling/cpp-serialization-benchmark#readme>
  - <https://github.com/felixguendling/cpp-serialization-benchmark/blob/master/benchmark_result.txt>
  - <https://github.com/felixguendling/cpp-serialization-benchmark/blob/master/CMakeLists.txt>
  - <https://github.com/felixguendling/cpp-serialization-benchmark/blob/master/src/main.cc>
  - <https://github.com/felixguendling/cpp-serialization-benchmark/blob/master/src/cista.cc>
  - <https://github.com/felixguendling/cpp-serialization-benchmark/blob/master/src/cereal.cc>
  - <https://github.com/felixguendling/cpp-serialization-benchmark/blob/master/include/csb/benches/cista_offset_slim.h>
  - <https://github.com/felixguendling/cpp-serialization-benchmark/blob/master/include/csb/benches/cista_offset.h>
  - <https://github.com/felixguendling/cpp-serialization-benchmark/blob/master/include/csb/benches/cista_raw.h>
  - <https://github.com/felixguendling/cpp-serialization-benchmark/blob/master/include/csb/benches/cereal.h>
  - <https://github.com/felixguendling/cpp-serialization-benchmark/blob/master/include/csb/benches/zpp_bits.h>
  - <https://github.com/felixguendling/cpp-serialization-benchmark/blob/master/include/csb/cista_offset_graph.h>
  - <https://github.com/felixguendling/cpp-serialization-benchmark/blob/master/include/csb/graph_constants.h.in>
  - <https://github.com/felixguendling/cpp-serialization-benchmark/blob/master/include/csb/traverse_graph.h>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/felixguendling/cista`) · [data/wave4/enrich/raw/github_com_felixguendling_cista.json](../../../data/wave4/enrich/raw/github_com_felixguendling_cista.json) (enrichment confidence 0.87)

</details>
