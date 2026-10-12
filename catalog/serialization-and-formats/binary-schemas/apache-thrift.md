# Apache Thrift (binary protocol)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Apache Thrift's C++ binary protocol: IDL-generated structs, fixed-width encoding; \~2.2x faster than msgpack-c in one round-trip test.

| | |
|---|---|
| **Beats** | MessagePack |
| **Claimed result** | 1190.22 ms (Thrift-binary) vs Msgpack 2560.6 ms (derived from page data, \~2.2x faster than Msgpack); did not beat Protobuf's 2312.78ms by as wide a margin but still faster (\~1.9x) |
| **Workload** | Round trip (serialize then deserialize) of one in-memory record holding a vector of 1,000 int64 values and 100 copies of an 86-char string (\~17 KB serialized), Thrift via TBinaryProtocolT over TMemoryBuffer; the README says each run is 1,000,000 operations, averaged over 50 runs, and reports average total time in ms (thekvs/cpp-serializers benchmark.cpp). |
| **Metric** | throughput |
| **Hardware** | Intel Core i7, Ubuntu 16.04 |
| **Compiler and flags** | Not stated for the published table on the current README, which says only 'Project was tested with Clang and GCC compilers'. Build: C++14, cmake -DCMAKE_BUILD_TYPE=Release (CMake's default -O3 -DNDEBUG for GCC/Clang) plus -W -Wall -Wextra from CMakeLists.txt. The README revision that published this table (commit 3015690c, 2019-03-13) said 'Project was tested with clang 5.0.0 (Ubuntu 16.04)'. |
| **Adoption** | 11k stars |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/apache/thrift) · [benchmark](https://github.com/thekvs/cpp-serializers) |

## Verdict

In the third-party thekvs/cpp-serializers shootout (2019 README table: Thrift 0.12.0, msgpack-c 3.1.1, protobuf 3.7.0; C++14 CMake Release build, compiler unnamed in the current README; 'Intel Core i7', Ubuntu 16.04), round-tripping one \~17 KB record (1,000 int64 values plus 100 86-char strings) through TBinaryProtocolT&lt;TMemoryBuffer&gt; took 1190.22 ms in total, against 2560.6 ms for msgpack (\~2.15x) and 2312.78 ms for protobuf (\~1.94x). The Thrift loop even includes a copy of the output into a std::string each iteration. The stated 1,000,000 iterations would mean \~1.2 us per round trip, which looks too fast, so trust the ratios rather than the absolute times.

## Use it when

- You already have a Thrift IDL, or want one schema shared across C++ and other languages, and need fast round trips of C++ structs through in-memory buffers (cache blobs, queue payloads, stored records).
- Records dominated by int64 arrays and medium-length strings, where CPU time matters more than bytes on the wire.
- Hot loops that can reuse one TMemoryBuffer, one protocol object and one destination struct across calls, which is how the benchmark ran it.
- You may later want RPC on the same types: the generated code and protocols plug into Thrift's client/server stack.

## Skip it when

- Size-sensitive storage or network links: the binary encoding was 17,017 B against msgpack's 13,402 B (\~27% larger) in this test. TCompactProtocol is smaller (13,378 B) but took 3474 ms in the same run, slower than both msgpack and protobuf.
- Schemaless or dynamic data, or data that arbitrary tools must read without an IDL. MessagePack is self-describing; Thrift binary is not.
- Maximum raw C++ speed: in the same shootout cereal (1052 ms) and YAS (303 ms) were faster, and Cap'n Proto and FlatBuffers took 401 and 492 ms for a full build, serialize and deserialize cycle.
- Untrusted input on older releases: 0.24.0 fixes C++ issues including CVE-2026-55969 (integer overflow in container size prechecks) and CVE-2026-55970 (heap over-read in THeaderTransport). Stay on a current release.
- You want a small header-only dependency: this needs a built libthrift plus the thrift compiler in your build.

## How it is fast

The binary protocol writes every integer at fixed width in big-endian order (an i64 is a byte swap plus 8 bytes) and every string as a 4-byte length plus raw bytes, so encoding and decoding need no varint branches. TBinaryProtocolT is a template over the transport, so with TMemoryBuffer each field goes through TBufferBase's inline fast path: one bounds check and one memcpy. readStringBody() borrow()s the string straight from the buffer and assigns it, and the generated read() fills the typed struct directly, reusing the destination vectors' capacity. The msgpack-c path in the same harness unpacks into an intermediate msgpack::object tree and then convert()s it into the struct.

## Compared with alternatives

Pick Thrift over cereal or Boost.Serialization when the same schema must be read from other languages or later carried over RPC; those two are C++-only. For C++-only data in this same test, cereal was a bit faster (1052 vs 1190 ms), is header-only and needs no IDL, and Boost.Serialization was a tie (1195 ms).

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (libthrift, chosen with CMake BUILD_SHARED_LIBS) plus the thrift code generator at build time |
| **Dependencies** | thrift compiler for code generation; libthrift links pthreads and librt, with OpenSSL for the SSL sockets (the CMake build skips SSL if OpenSSL is absent or disabled); Boost headers to build (TUuid is implemented on boost::uuids; Boost is not a runtime link dependency); libevent only for libthriftnb (non-blocking server); zlib only for thriftz |
| **Minimum toolchain** | C++11 (CMake default CMAKE_CXX_STANDARD 11); C++03/C++98 dropped after 0.12.0. The benchmark built Thrift 0.12.0 with C++14. |
| **Platforms** | Linux and other POSIX systems, Windows 7 or later (XP/Vista dropped after 0.12.0); byte order is fixed by the protocol (TNetworkBigEndian default, TLEBinaryProtocol for little-endian), so no architecture requirement is documented |
| **Thread safety** | Not documented for protocol and buffer objects. TMemoryBuffer and TBinaryProtocolT hold mutable read/write cursors, so give each thread its own instances. |
| **Drop-in for the baseline** | no |

## Gotchas

- Generated code takes TProtocol\* by default, so each readI64/readString call is a virtual dispatch into the templated protocol. `thrift --gen cpp:templates` generates templatized reader/writer methods instead. The benchmark used the default, non-templated output.
- TBinaryProtocol's string and container size limits default to 0 (unlimited); only TConfiguration's max message size (100 MB default) bounds what a hostile length prefix can make it allocate. Call setStringSizeLimit/setContainerSizeLimit for untrusted data.
- TMemoryBuffer::resetBuffer(buf, sz) defaults to the OBSERVE policy: it reads your memory in place without copying, so that memory must outlive the parse.
- Fields marked `required` in the IDL make read() throw TProtocolException(INVALID_DATA) when absent, which limits later schema changes.

## Known shortcomings

- Only the binary protocol wins in thekvs/cpp-serializers; thrift-compact (3474 ms) is slower than both protobuf and msgpack. The suite's stated 1,000,000 iterations look inconsistent with the published totals (ratios unaffected).
- Only evidence is a 2019 run of Thrift 0.12.0 (current v0.24.0 unmeasured) with an uneven harness: the msgpack path rebuilds an object tree and converts each iteration while Thrift reuses buffers and the destination struct. Binary encoding is about 27% larger than msgpack. TBinaryProtocol string and container limits default to unlimited; v0.24.0 fixes two C++ CVEs (CVE-2026-55969, CVE-2026-55970). cereal and YAS beat it in the same suite.

## Caveats and trade-offs

This is the third-party thekvs/cpp-serializers shootout from 2019 (thrift 0.12.0, protobuf 3.7.0, msgpack 3.1.1, 'Intel Core i7', Ubuntu 16.04); the current README names no compiler or exact CPU. Only the binary protocol wins: thrift-compact (3474.32 ms) is slower than both protobuf (2312.78) and msgpack (2560.6). Thrift is itself a major incumbent RPC/serialization stack. The test is a single record round-tripped through in-memory buffers, so it says nothing about RPC cost. The pre-2019 table on the same README also had thrift-binary ahead (13335 vs protobuf 24717 and msgpack 33815 ms). The implied \~1.2 us per \~17 KB round trip looks too fast for the stated 1,000,000 iterations, and the README's pre-2019 table (Core i5, Ubuntu 14.04, older library versions) showed \~11x larger totals, so the iteration label may be off; the ratios are unaffected.

Requires IDL + code generation (thrift compiler) and an RPC framework dependency footprint; Thrift-compact variant was much slower (3474ms) than Thrift-binary in the same run, so only the binary protocol qualifies.

## Maintenance

Actively maintained Apache-2.0 project (v0.24.0 released 2026-07-11, commits through 2026-09-24), but the only speed evidence is for 0.12.0 from 2019, so the current release has not been measured.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification B, tier now B.
- **Tier reason:** thekvs/cpp-serializers is a widely cited independent third-party shootout. Its public code (benchmark.cpp thrift_serialization_test, CMakeLists.txt) runs thrift-binary against protobuf and msgpack. The README gives only 'Intel Core i7', Ubuntu 16.04 and a CMake Release build, with no compiler named for the published table, so it falls short of A.
- **Verifier notes:** All numbers appear verbatim in the thekvs README table: thrift-binary 1190.22, protobuf 2312.78, msgpack 2560.6. The ratios check out (1.94x vs protobuf, 2.15x vs msgpack). gh confirms Apache-2.0, 10,960 stars, last commit 2026-09-24, not archived and not a fork. The fixes set compared_against_cpp_std_directly to false (the C++ std library has no serializer), fill in compiler/flags, make the workload more precise, and make the caveats self-contained. The repo entered known_list.txt only through this wave's merge (6ded485), so it is not a duplicate.
- **Fields the verifier corrected:** `compared_against_cpp_std_directly`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/thekvs/cpp-serializers>
  - <https://github.com/thekvs/cpp-serializers/blob/master/README.md>
  - <https://github.com/thekvs/cpp-serializers/commits/master/README.md>
  - <https://github.com/thekvs/cpp-serializers/commit/3015690c2c4bb477b25dec30086bca98a2d896a4>
  - <https://github.com/thekvs/cpp-serializers/blob/master/CMakeLists.txt>
  - <https://github.com/thekvs/cpp-serializers/blob/master/benchmark.cpp>
  - <https://github.com/thekvs/cpp-serializers/blob/master/data.hpp>
  - <https://github.com/apache/thrift>
  - <https://github.com/apache/thrift/commits>
  - <https://github.com/apache/thrift/tags>
- **Sources the enricher read:**
  - <https://github.com/apache/thrift>
  - <https://github.com/apache/thrift/blob/master/README.md>
  - <https://github.com/apache/thrift/blob/master/lib/cpp/README.md>
  - <https://github.com/apache/thrift/blob/master/lib/cpp/src/thrift/protocol/TBinaryProtocol.tcc>
  - <https://github.com/apache/thrift/blob/master/lib/cpp/src/thrift/protocol/TBinaryProtocol.h>
  - <https://github.com/apache/thrift/blob/master/lib/cpp/src/thrift/protocol/TVirtualProtocol.h>
  - <https://github.com/apache/thrift/blob/master/lib/cpp/src/thrift/transport/TBufferTransports.h>
  - <https://github.com/apache/thrift/blob/master/lib/cpp/src/thrift/TConfiguration.h>
  - <https://github.com/apache/thrift/blob/master/lib/cpp/CMakeLists.txt>
  - <https://github.com/apache/thrift/blob/master/build/cmake/DefineCMakeDefaults.cmake>
  - <https://github.com/apache/thrift/blob/master/compiler/cpp/src/thrift/generate/t_cpp_generator.cc>
  - <https://github.com/apache/thrift/blob/master/lib/cpp/test/Benchmark.cpp>
  - <https://github.com/apache/thrift/blob/master/CHANGES.md>
  - <https://github.com/apache/thrift/releases>
  - <https://github.com/apache/thrift/tags>
  - <https://github.com/thekvs/cpp-serializers>
  - <https://github.com/thekvs/cpp-serializers/blob/master/README.md>
  - <https://github.com/thekvs/cpp-serializers/blob/master/benchmark.cpp>
  - <https://github.com/thekvs/cpp-serializers/blob/master/data.hpp>
  - <https://github.com/thekvs/cpp-serializers/blob/master/test.thrift>
  - <https://github.com/thekvs/cpp-serializers/blob/master/msgpack/record.hpp>
  - <https://github.com/thekvs/cpp-serializers/blob/master/thrift/gen-cpp/test_types.cpp>
  - <https://github.com/thekvs/cpp-serializers/blob/master/CMakeLists.txt>
  - <https://github.com/thekvs/cpp-serializers/commits/master>
  - <https://ratatoskr.run/openembedded-devel/2026/09/17524220/t>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/apache/thrift`) · [data/wave4/enrich/raw/github_com_apache_thrift.json](../../../data/wave4/enrich/raw/github_com_apache_thrift.json) (enrichment confidence 0.5)

</details>
