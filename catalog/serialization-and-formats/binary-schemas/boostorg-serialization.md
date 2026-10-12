# Boost.Serialization

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> Boost's C++ object-graph serializer; its native binary archive round-tripped a \~17 KB record \~1.9x faster than Protobuf.

| | |
|---|---|
| **Beats** | Protobuf |
| **Claimed result** | 1195.04 ms vs Protobuf 2312.78 ms and Msgpack 2560.6 ms (derived from page data, \~1.9x faster than Protobuf, \~2.1x faster than Msgpack) |
| **Workload** | Round trip (serialize then deserialize) of one in-memory record holding a vector of 1,000 int64 values and 100 copies of an 86-char string (\~17 KB serialized), Boost via binary_oarchive/binary_iarchive over std::ostringstream/std::stringstream, constructed fresh each iteration; the README says each run is 1,000,000 operations, averaged over 50 runs, and reports average total time in ms (thekvs/cpp-serializers benchmark.cpp). |
| **Metric** | throughput |
| **Hardware** | Intel Core i7, Ubuntu 16.04 |
| **Compiler and flags** | Not stated for the published table on the current README, which says only 'Project was tested with Clang and GCC compilers'. Build: C++14, cmake -DCMAKE_BUILD_TYPE=Release (CMake's default -O3 -DNDEBUG for GCC/Clang) plus -W -Wall -Wextra from CMakeLists.txt. The README revision that published this table (commit 3015690c, 2019-03-13) said 'Project was tested with clang 5.0.0 (Ubuntu 16.04)'. |
| **Adoption** | part of Boost; boostorg/serialization repo has 135 stars (mirror; usage vastly larger via Boost distribution) |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/boostorg/serialization) · [benchmark](https://github.com/thekvs/cpp-serializers) |

## Verdict

Source: the third-party thekvs/cpp-serializers shootout, 2019 README table (boost 1.69.0 vs protobuf 3.7.0 and msgpack 3.1.1; Intel Core i7, Ubuntu 16.04; CMake Release build, clang 5.0.0 per the commit that published the table; standard library not stated). One record of 1,000 int64 plus 100 copies of an 86-char string (\~17 KB) was round-tripped through a fresh binary_oarchive/binary_iarchive over stringstreams each iteration. Boost took 1195.04 ms total against 2312.78 ms for Protobuf (\~1.9x) and 2560.6 ms for msgpack (\~2.1x); nothing was compared against a std facility, and the '1,000,000 operations' label looks too large for these totals, though the ratios are unaffected.

## Use it when

- C++-only persistence or checkpointing of existing class hierarchies that hold raw pointers, shared_ptr graphs or polymorphic base pointers, where mapping everything onto .proto messages would be a rewrite.
- Records dominated by std::vector of arithmetic types (int64, double) written to binary_oarchive: the bulk save_binary path writes them as a single raw copy.
- Many objects, or a few large ones, per archive (files, snapshots, bulk IPC), so the per-archive setup cost is amortized.
- Codebases already built against Boost that need non-intrusive serialization of third-party types, or per-class versioning so old files still load.
- Writer and reader on the same platform and ABI, which the native binary archive assumes.

## Skip it when

- Cross-language interchange, or wire contracts shared with other teams: there is no schema or IDL and no non-C++ reader. Stay on Protobuf, or see Thrift/hpp-proto.
- Deserializing untrusted input such as network data from clients. Issue #331 (insecure deserialization leading to type and ownership confusion, reported against 1.89.0 and below) is still open with details withheld, and a negative-class-id check was only added in August 2026 (#332).
- Small messages with one archive each. The maintainer measured 14.2 us per \~70-byte message with a fresh stream and archive per message versus 0.21 us with one shared archive (MSVC x64, issue #347), so setup dominates.
- When wire size or top C++ speed matters. It had the largest payload in the benchmark's main table (17,470 B vs Protobuf 16,116 and msgpack 13,402), and in the same run cereal (1052 ms) and yas (302.7 ms) were faster.
- Binary archives that must move across architectures. The native binary archive refuses to load when int/long/float/double sizes or endianness differ, and the portable binary archive lives only in the examples directory, without portable floating point.

## How it is fast

Nothing in the library targets speed. It won this benchmark because the native binary archive does almost no encoding. basic_binary_oprimitive::save writes each primitive as sizeof(T) raw native bytes with a single streambuf sputn, with no varint or zigzag step. std::vector of arithmetic types takes the 'array optimization' path: use_array_optimization is keyed on is_bitwise_serializable, which defaults to is_arithmetic, so the whole buffer goes out in one save_binary call. The benchmark's Protobuf schema declares the ids as proto3 repeated int64, which Protobuf varint-encodes (negative values take all 10 bytes), so on this int-heavy record a fixed-width bulk copy beats encoding and decoding each value.

## Compared with alternatives

cereal ran the same benchmark slightly faster (1052 vs 1195 ms) and is header-only with no dependencies, but its docs say it does not serialize raw pointers or references. Pick Boost.Serialization when you need raw-pointer object graphs with address tracking or must read existing Boost archives; otherwise take cereal. Choose Apache Thrift binary (1190 ms, a tie here) or hpp-proto if you need an IDL or cross-language wire format.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (compiled boost_serialization, plus boost_wserialization for wide-char archives), usually taken from a Boost distribution |
| **Dependencies** | Boost: array, assert, config, core, detail, integer, io, iterator, move, mpl, optional, predef, preprocessor, smart_ptr, spirit, type_traits, unordered, utility, variant (public); function (private) |
| **Minimum toolchain** | C++11 (meta/libraries.json cxxstd 11); CI covers GCC 7-16, Clang 6-22, MSVC 14.3/14.5 and Apple Clang |
| **Platforms** | Linux, macOS and Windows (MSVC, clang-win, MinGW GCC) in CI; the code is architecture-neutral, but native binary archives only load on a matching platform (sizes and endianness are checked in the header) |
| **Thread safety** | Documented: never share one archive instance between threads; separate archives in separate threads are fine, because the shared type tables are lock-free singletons initialized at module load. Do not load or unload DLLs/shared objects while any archive is open. |
| **Drop-in for the baseline** | no |

## Gotchas

- Objects are tracked by memory address. Saving successive copies from the same stack variable silently writes only the first one (a const-reference static assert catches the common case, but not inside name-value pairs), and after loading into a temporary and moving it into a container you must call reset_object_address or pointer restoration breaks.
- Polymorphic pointers must be registered or exported. BOOST_CLASS_EXPORT has to come after the archive headers are included, and each type needs exactly one BOOST_CLASS_EXPORT_IMPLEMENT. Getting this wrong fails at run time with unregistered_class, or with duplicate symbols at link time.
- Binary archives need streams opened with std::ios::binary. Otherwise CRLF translation corrupts the archive, and the library cannot detect it until load (debug builds assert). By default each archive also writes a header and swaps in a codecvt facet; the no_header and no_codecvt flags turn these off.
- Lengths read from the archive are trusted. The binary load of std::string reads a size_t and calls s.resize(l) with no bound, so a malformed or hostile archive can force a huge allocation.

## Known shortcomings

- Incidental win in one suite (thekvs/cpp-serializers): its lead over protobuf was only about 1.14x in the README's pre-2019 table. The suite's stated iteration count looks inconsistent with its totals (ratios unaffected). No compiler named for the published table.
- The win over protobuf comes from raw fixed-width copying of vector&lt;int64&gt; against protobuf's varint encoding of negative values; largest payload in the table (17,470 B). Maintainer measured 14.2 us per \~70-byte message with a fresh archive vs 0.21 us shared (#347). Open insecure-deserialization report (#331); binary string load resizes to an unbounded length; native binary archives are not portable across platforms.

## Caveats and trade-offs

This is the third-party thekvs/cpp-serializers shootout from 2019 (boost 1.69.0, protobuf 3.7.0, msgpack 3.1.1, 'Intel Core i7', Ubuntu 16.04); the current README names no compiler or exact CPU. Boost.Serialization is not marketed as fast, so this is an incidental win in a third-party shootout, not a first-party claim. In the same table it has the largest serialized size in the main table (17470 bytes), is \~1.1x slower than cereal (1052.46 ms) and \~4x slower than yas (302.7 ms) (derived from page data). In the README's pre-2019 table (boost 1.62, protobuf 3.1.0) its lead over protobuf was only \~1.14x (21760 vs 24717 ms). The implied \~1.2 us per \~17 KB round trip looks too fast for the stated 1,000,000 iterations, and the README's pre-2019 table (Core i5, Ubuntu 14.04, older library versions) showed \~11x larger totals, so the iteration label may be off; the ratios are unaffected.

General-purpose C++ object graph serialization (pointers, polymorphism, versioning) rather than a schema/IDL binary format; no cross-language interchange; heavier compile-time cost than lightweight header-only competitors.

## Maintenance

Actively maintained (commits through 2026-09-25; Gennaro Prota took over maintenance in 2026 and has been closing old issues) and shipped in every Boost release under BSL-1.0. Easy to get from system Boost packages or the Boost CMake superproject, but it is a compiled library with about 20 Boost dependencies, not a single header you can vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification B, tier now B.
- **Tier reason:** thekvs/cpp-serializers is a widely cited independent third-party shootout. Its public code (benchmark.cpp boost_serialization_test, boost/record.cpp) runs Boost.Serialization against protobuf and msgpack. The README gives only 'Intel Core i7', Ubuntu 16.04 and a CMake Release build, with no compiler named for the published table, so it falls short of A.
- **Verifier notes:** All numbers appear verbatim in the thekvs README table: boost 1195.04, protobuf 2312.78, msgpack 2560.6. The ratios check out (1.94x vs protobuf, 2.14x vs msgpack). gh confirms BSL-1.0, 135 stars, last commit 2026-09-25, not archived and not a fork. The fixes set compared_against_cpp_std_directly to false, fill in compiler/flags, make the workload more precise, and make the caveats self-contained. The repo entered known_list.txt only through this wave's merge (6ded485).
- **Fields the verifier corrected:** `compared_against_cpp_std_directly`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/thekvs/cpp-serializers>
  - <https://github.com/thekvs/cpp-serializers/blob/master/README.md>
  - <https://github.com/thekvs/cpp-serializers/commits/master/README.md>
  - <https://github.com/thekvs/cpp-serializers/commit/3015690c2c4bb477b25dec30086bca98a2d896a4>
  - <https://github.com/thekvs/cpp-serializers/blob/master/CMakeLists.txt>
  - <https://github.com/thekvs/cpp-serializers/blob/master/benchmark.cpp>
  - <https://github.com/thekvs/cpp-serializers/blob/master/data.hpp>
  - <https://github.com/thekvs/cpp-serializers/blob/master/boost/record.hpp>
  - <https://github.com/thekvs/cpp-serializers/blob/master/boost/record.cpp>
  - <https://github.com/boostorg/serialization>
  - <https://github.com/boostorg/serialization/commits>
- **Sources the enricher read:**
  - <https://github.com/boostorg/serialization>
  - <https://github.com/boostorg/serialization/commits>
  - <https://github.com/boostorg/serialization/blob/develop/CMakeLists.txt>
  - <https://github.com/boostorg/serialization/blob/develop/meta/libraries.json>
  - <https://github.com/boostorg/serialization/blob/develop/.github/workflows/ci.yml>
  - <https://github.com/boostorg/serialization/blob/develop/doc/index.html>
  - <https://github.com/boostorg/serialization/blob/develop/doc/overview.html>
  - <https://github.com/boostorg/serialization/blob/develop/doc/archives.html>
  - <https://github.com/boostorg/serialization/blob/develop/doc/special.html>
  - <https://github.com/boostorg/serialization/blob/develop/doc/traits.html>
  - <https://github.com/boostorg/serialization/blob/develop/doc/rationale.html>
  - <https://github.com/boostorg/serialization/blob/develop/doc/todo.html>
  - <https://github.com/boostorg/serialization/blob/develop/doc/exception_safety.html>
  - <https://github.com/boostorg/serialization/blob/develop/doc/release.html>
  - <https://github.com/boostorg/serialization/blob/develop/doc/performance_status.html>
  - <https://github.com/boostorg/serialization/blob/develop/include/boost/archive/basic_binary_oprimitive.hpp>
  - <https://github.com/boostorg/serialization/blob/develop/include/boost/archive/impl/basic_binary_iprimitive.ipp>
  - <https://github.com/boostorg/serialization/blob/develop/include/boost/serialization/vector.hpp>
  - <https://github.com/boostorg/serialization/issues/331>
  - <https://github.com/boostorg/serialization/issues/347>
  - <https://github.com/boostorg/serialization/issues/305>
  - <https://github.com/boostorg/serialization/issues/247>
  - <https://github.com/boostorg/serialization/issues/255>
  - <https://github.com/boostorg/serialization/issues/243>
  - <https://github.com/thekvs/cpp-serializers>
  - <https://github.com/thekvs/cpp-serializers/blob/master/README.md>
  - <https://github.com/thekvs/cpp-serializers/commits/master>
  - <https://github.com/thekvs/cpp-serializers/commit/3015690c2c4bb477b25dec30086bca98a2d896a4>
  - <https://github.com/thekvs/cpp-serializers/blob/master/benchmark.cpp>
  - <https://github.com/thekvs/cpp-serializers/blob/master/data.hpp>
  - <https://github.com/thekvs/cpp-serializers/blob/master/test.proto>
  - <https://github.com/thekvs/cpp-serializers/blob/master/boost/record.hpp>
  - <https://github.com/thekvs/cpp-serializers/blob/master/boost/record.cpp>
  - <https://github.com/USCiLab/cereal>
  - <https://uscilab.github.io/cereal/pointers.html>
  - <https://protobuf.dev/programming-guides/encoding/>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/boostorg/serialization`) · [data/wave4/enrich/raw/github_com_boostorg_serialization.json](../../../data/wave4/enrich/raw/github_com_boostorg_serialization.json) (enrichment confidence 0.6)

</details>
