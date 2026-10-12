# cereal

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Header-only C++11 serialization library whose binary archive round-tripped a 17 KB record \~2.2x faster than Protobuf in 2019.

| | |
|---|---|
| **Beats** | Protobuf |
| **Claimed result** | 1052.46 ms vs Protobuf 2312.78 ms and Msgpack 2560.6 ms (derived from page data, \~2.2x faster than Protobuf, \~2.4x faster than Msgpack) |
| **Workload** | Round trip (serialize then deserialize) of one in-memory record holding a vector of 1,000 int64 values and 100 copies of an 86-char string (\~17 KB serialized), cereal via BinaryOutputArchive/BinaryInputArchive over std::ostringstream/std::stringstream; the README says each run is 1,000,000 operations, averaged over 50 runs, and reports average total time in ms (thekvs/cpp-serializers benchmark.cpp). |
| **Metric** | throughput |
| **Hardware** | Intel Core i7, Ubuntu 16.04 |
| **Compiler and flags** | Not stated for the published table on the current README, which says only 'Project was tested with Clang and GCC compilers'. Build: C++14, cmake -DCMAKE_BUILD_TYPE=Release (CMake's default -O3 -DNDEBUG for GCC/Clang) plus -W -Wall -Wextra from CMakeLists.txt. The README revision that published this table (commit 3015690c, 2019-03-13) said 'Project was tested with clang 5.0.0 (Ubuntu 16.04)'. |
| **Adoption** | 4.7k stars |
| **Last commit** | 2026-03-11 |
| **Links** | [repository](https://github.com/USCiLab/cereal) · [benchmark](https://github.com/thekvs/cpp-serializers) |

## Verdict

In thekvs/cpp-serializers (2019; cereal 1.2.2, protobuf 3.7.0, msgpack 3.1.1; CMake Release build, with clang 5.0.0 named by the README revision that published the table; an unspecified 'Intel Core i7' on Ubuntu 16.04), round-tripping one record of 1,000 int64 and 100 strings of 86 chars through cereal's BinaryOutputArchive/BinaryInputArchive took 1052.46 ms in total vs 2312.78 ms for Protobuf (\~2.2x) and 2560.6 ms for msgpack (\~2.4x), with no std:: baseline involved. Each cereal iteration builds a fresh std::ostringstream and std::stringstream and copies the buffer while the Protobuf loop reuses its message and string, so the stream overhead is inside cereal's number.

## Use it when

- C++-to-C++ data where both ends are built from the same code: checkpoints, caches, save state, or IPC between builds of one codebase
- Records dominated by contiguous arithmetic vectors and strings, which take the single-memcpy path. The benchmark record was 1,000 int64 plus 100 strings of 86 chars.
- Serializing existing STL-heavy types (maps, shared_ptr/unique_ptr, optional, variant) without writing a .proto file or adding a codegen step
- Migrating off Boost.Serialization: the syntax is similar (CEREAL_CLASS_VERSION mirrors BOOST_CLASS_VERSION), there is no Boost dependency, and it ran slightly faster in the same shootout
- When one serialize() function should also produce human-readable JSON or XML for debugging

## Skip it when

- Cross-language interchange or schema evolution. The binary format is positional and untagged, so reordering or changing fields breaks old data unless you opt into versioning. The docs say cereal was not designed as a robust long-term storage format.
- Untrusted input (network peers, user files). Container sizes read from the stream go straight into resize(). The maintainer closed #103 saying cereal expects to produce its own data and will not add checks. #629 reports a null-pointer dereference loading untrusted XML (still open), and #870 reported a type-confusion bug in 1.3.2 and earlier (closed, details redacted).
- Size-sensitive wire formats. Integers and length tags are fixed-width (uint64 size tags), so the benchmark payload was 17,416 bytes vs 16,116 for Protobuf and 13,402 for msgpack.
- Chasing the fastest possible round trip. In the same table yas (302.7 ms) was \~3.5x faster than cereal. Cap'n Proto and FlatBuffers finished a build+serialize+deserialize cycle in 400.98 and 491.5 ms.
- Raw-pointer or reference object graphs, and shared_ptr aliasing constructors. None of these are supported; Boost.Serialization handles raw pointers.

## How it is fast

Dispatch happens at compile time: SFINAE traits pick each type's member or free serialize/save/load, and variadic ar(...) calls inline down to the archive's primitive writers. The binary archive writes each arithmetic value's native bytes with one streambuf sputn/sgetn call, and a contiguous arithmetic vector or string is a uint64 length tag plus one bulk binary_data copy, with no field tags, no varint/zigzag coding and no per-element framing (the benchmark payload is exactly 8 + 1000x8 + 8 + 100x(8+86) = 17,416 bytes). Only shared_ptr targets are tracked (an address-to-id hash map), and version numbers are written only for types that opt in, so plain structs carry no metadata. Protobuf varint-encodes each int64 and tags each string, which makes its payload smaller (16,116 bytes) but its round trip slower here.

## Compared with alternatives

Pick cereal over Boost.Serialization when you want the same member serialize() style without Boost and can do without raw pointers; it was \~1.14x faster in the same table (1052.46 vs 1195.04 ms). Pick hpp-proto if you must keep Protobuf schemas or wire data, and Apache Thrift's binary protocol (1190.22 ms in the same table) if you need a schema shared with non-C++ code.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none. The JSON and XML archives use bundled RapidJSON, RapidXML and base64 headers. Building the repo's own tests/sandbox needs Boost.Serialization unless SKIP_PERFORMANCE_COMPARISON or JUST_INSTALL_CEREAL is set. |
| **Minimum toolchain** | C++11. The docs name g++ 4.7.3, clang++ 3.3 and MSVC 2013 or newer. CI covers g++ 4.7 and up, Xcode 15/16 clang and VS2013-2022. std::optional/std::variant support needs C++17. The CMake minimum is 3.6. |
| **Platforms** | any with a conforming C++11 compiler (Linux, macOS, Windows in CI). BinaryArchive is native-endian, so use PortableBinaryArchive when data crosses endianness. |
| **Thread safety** | Never use one archive from several threads at once. Separate archives can run in parallel only if CEREAL_THREAD_SAFE=1 is defined before every cereal include (or via the CMake THREAD_SAFE option). That setting mutex-guards the global polymorphism and versioning registries; the default is no locking. |
| **Drop-in for the baseline** | no |

## Gotchas

- Versioning is opt-in and all-or-nothing per type. Loading data saved without a version through a versioned serialize function corrupts the load and will likely crash. Load with the same cereal version you saved with.
- Archives are only guaranteed to have flushed when destroyed, and XML/JSON write nothing until then, so scope archives with RAII. Open file streams with std::ios::binary for binary archives.
- Polymorphic pointers need CEREAL_REGISTER_TYPE and RTTI, and registration only binds to archives #included before it. Registering inside a Windows DLL needs CEREAL_REGISTER_DYNAMIC_INIT/CEREAL_FORCE_DYNAMIC_INIT. Errors throw cereal::Exception (a std::runtime_error), so exceptions must be enabled.
- Known bugs: CVE-2020-11105 (shared_ptr ids keyed by raw address) is fixed only in 1.3.1+. CVE-2020-11104 (#625, open): long double writes uninitialized padding bytes. #880 (open, 2026): the bundled RapidJSON misparses some doubles under MSVC /O1 /GL /LTCG.

## Known shortcomings

- Measured with the plain binary archive, which is not endian-portable. Last release v1.3.2 (2022). The suite's stated iteration count looks inconsistent with its totals (ratios unaffected).
- Unequal harness: each cereal iteration builds fresh string streams and copies the buffer while the protobuf loop reuses its message. Payload about 8% larger than protobuf; YAS is about 3.5x faster than cereal in the same table. Container sizes from the stream go straight to resize() by design (#103); open #629 (null dereference on untrusted XML) and CVE-2020-11104 (uninitialized padding). Master since 2024 is only compiler/CI fixes.

## Caveats and trade-offs

This is the third-party thekvs/cpp-serializers shootout from 2019 (cereal 1.2.2, protobuf 3.7.0, msgpack 3.1.1, 'Intel Core i7', Ubuntu 16.04), and cereal's latest release is v1.3.2 (2022). The current README names no compiler or exact CPU and says only that Clang and GCC were tested. The test uses cereal's plain binary archive, which is schema-less and not endian-portable (cereal ships a separate PortableBinaryArchive), so it is not like-for-like with Protobuf's wire format. yas is \~3.5x faster than cereal in the same table (302.7 ms, derived from page data). The ordering also held in the README's pre-2019 table (cereal 11031 vs protobuf 24717 and msgpack 33815 ms). The implied \~1.05 us per \~17 KB round trip looks too fast for the stated 1,000,000 iterations, and the README's pre-2019 table (Core i5, Ubuntu 14.04, older library versions) showed \~11x larger totals, so the iteration label may be off; the ratios are unaffected.

Header-only, macro-driven intrusive/non-intrusive serialize() methods; not a schema/IDL language like Protobuf so no cross-language codegen; text/binary/XML archives supported but binary archive is what was benchmarked.

## Maintenance

Lightly maintained (last release v1.3.2 in Feb 2022, master commits since 2024 are compiler and CI fixes with the latest on 2026-03-11, and an open issue asks for a new release), but it is BSD-3-Clause and header-only, so vendoring 1.3.2 or master is easy.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification B, tier now B.
- **Tier reason:** thekvs/cpp-serializers is a widely cited independent third-party shootout. Its public code (benchmark.cpp cereal_serialization_test, cereal/record.cpp) runs cereal against protobuf and msgpack. The README gives only 'Intel Core i7', Ubuntu 16.04 and a CMake Release build, with no compiler named for the published table, so it falls short of A.
- **Verifier notes:** All numbers appear verbatim in the thekvs README table: cereal 1052.46, protobuf 2312.78, msgpack 2560.6. The ratios check out (2.20x vs protobuf, 2.43x vs msgpack). gh confirms BSD-3-Clause, 4,707 stars, last commit 2026-03-11 (active), not archived and not a fork. The fixes set compared_against_cpp_std_directly to false, fill in compiler/flags, make the workload more precise, and make the caveats self-contained. The repo entered known_list.txt only through this wave's merge (6ded485).
- **Fields the verifier corrected:** `compared_against_cpp_std_directly`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/thekvs/cpp-serializers>
  - <https://github.com/thekvs/cpp-serializers/blob/master/README.md>
  - <https://github.com/thekvs/cpp-serializers/commits/master/README.md>
  - <https://github.com/thekvs/cpp-serializers/commit/3015690c2c4bb477b25dec30086bca98a2d896a4>
  - <https://github.com/thekvs/cpp-serializers/blob/master/CMakeLists.txt>
  - <https://github.com/thekvs/cpp-serializers/blob/master/benchmark.cpp>
  - <https://github.com/thekvs/cpp-serializers/blob/master/data.hpp>
  - <https://github.com/thekvs/cpp-serializers/blob/master/cereal/record.hpp>
  - <https://github.com/thekvs/cpp-serializers/blob/master/cereal/record.cpp>
  - <https://github.com/USCiLab/cereal>
  - <https://github.com/USCiLab/cereal/commits>
  - <https://github.com/USCiLab/cereal/releases/latest>
- **Sources the enricher read:**
  - <https://github.com/USCiLab/cereal>
  - <https://github.com/USCiLab/cereal/blob/master/README.md>
  - <https://github.com/USCiLab/cereal/blob/master/include/cereal/archives/binary.hpp>
  - <https://github.com/USCiLab/cereal/blob/master/include/cereal/archives/portable_binary.hpp>
  - <https://github.com/USCiLab/cereal/blob/master/include/cereal/cereal.hpp>
  - <https://github.com/USCiLab/cereal/blob/master/include/cereal/macros.hpp>
  - <https://github.com/USCiLab/cereal/blob/master/include/cereal/details/helpers.hpp>
  - <https://github.com/USCiLab/cereal/blob/master/include/cereal/types/vector.hpp>
  - <https://github.com/USCiLab/cereal/blob/master/include/cereal/types/string.hpp>
  - <https://github.com/USCiLab/cereal/blob/master/include/cereal/version.hpp>
  - <https://github.com/USCiLab/cereal/blob/master/CMakeLists.txt>
  - <https://github.com/USCiLab/cereal/blob/master/.github/workflows/ci.yml>
  - <https://github.com/USCiLab/cereal/blob/master/.github/workflows/ci-macos.yml>
  - <https://github.com/USCiLab/cereal/blob/master/appveyor.yml>
  - <https://github.com/USCiLab/cereal/blob/gh-pages/_includes/main.markdown>
  - <https://github.com/USCiLab/cereal/blob/gh-pages/_includes/serialization_archives.markdown>
  - <https://github.com/USCiLab/cereal/blob/gh-pages/_includes/thread_safety.markdown>
  - <https://github.com/USCiLab/cereal/blob/gh-pages/_includes/pointers.markdown>
  - <https://github.com/USCiLab/cereal/blob/gh-pages/_includes/transition_from_boost.markdown>
  - <https://github.com/USCiLab/cereal/blob/gh-pages/_includes/serialization_functions.markdown>
  - <https://github.com/USCiLab/cereal/blob/gh-pages/_includes/polymorphism.markdown>
  - <https://github.com/USCiLab/cereal/releases>
  - <https://github.com/USCiLab/cereal/releases/tag/v1.3.1>
  - <https://github.com/USCiLab/cereal/releases/tag/v1.3.2>
  - <https://github.com/USCiLab/cereal/commits/master>
  - <https://github.com/USCiLab/cereal/issues/103>
  - <https://github.com/USCiLab/cereal/issues/625>
  - <https://github.com/USCiLab/cereal/issues/629>
  - <https://github.com/USCiLab/cereal/issues/707>
  - <https://github.com/USCiLab/cereal/issues/870>
  - <https://github.com/USCiLab/cereal/issues/880>
  - <https://github.com/USCiLab/cereal/issues/882>
  - <https://github.com/USCiLab/cereal/issues?q=CVE>
  - <https://github.com/USCiLab/cereal/issues?q=untrusted>
  - <https://github.com/USCiLab/cereal/issues?q=release>
  - <https://github.com/USCiLab/cereal/issues?q=bad_alloc>
  - <https://nvd.nist.gov/vuln/detail/CVE-2020-11105>
  - <https://cveawg.mitre.org/api/cve/CVE-2020-11105>
  - <https://github.com/thekvs/cpp-serializers>
  - <https://github.com/thekvs/cpp-serializers/blob/master/README.md>
  - <https://github.com/thekvs/cpp-serializers/blob/3015690c2c4bb477b25dec30086bca98a2d896a4/README.md>
  - <https://github.com/thekvs/cpp-serializers/blob/master/benchmark.cpp>
  - <https://github.com/thekvs/cpp-serializers/blob/master/cereal/record.hpp>
  - <https://github.com/thekvs/cpp-serializers/blob/master/cereal/record.cpp>
  - <https://github.com/thekvs/cpp-serializers/blob/master/data.hpp>
  - <https://github.com/thekvs/cpp-serializers/blob/master/CMakeLists.txt>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/uscilab/cereal`) · [data/wave4/enrich/raw/github_com_uscilab_cereal.json](../../../data/wave4/enrich/raw/github_com_uscilab_cereal.json) (enrichment confidence 0.65)

</details>
