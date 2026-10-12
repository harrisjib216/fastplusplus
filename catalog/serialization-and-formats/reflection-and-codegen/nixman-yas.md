# YAS (Yet Another Serialization)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Reflection and code generation](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSL-1.0` · 🟡 stale

> Header-only C++11 serializer with a Boost.Serialization-style API; its binary archive ran 3.5-7.2x faster than Boost.Serialization and cereal.

| | |
|---|---|
| **Beats** | Boost.Serialization and cereal |
| **Claimed result** | thekvs suite: yas 302.7ms total vs boost 1195.04ms (\~3.9x) and cereal 1052.46ms (\~3.5x); fraillt suite (GCC 11): yas 2286ms ser/1770ms des vs boost 15126ms/12724ms (\~6.6x/\~7.2x) and cereal 10777ms/9088ms (\~4.7x/\~5.1x) |
| **Workload** | thekvs/cpp-serializers: serialize/deserialize a mixed object 1,000,000 times, averaged over 50 runs; fraillt/cpp_serializers_benchmark: serialize/deserialize a nested 'Monster' struct 300,000 times |
| **Metric** | throughput |
| **Hardware** | thekvs: unspecified 'Intel Core i7' desktop, Ubuntu 16.04; fraillt: Ubuntu 20.04 x64, exact CPU model not stated |
| **Compiler and flags** | thekvs suite: C++14, cmake -DCMAKE_BUILD_TYPE=Release; the compiler for the published table is not stated (the README only says it was 'tested with Clang and GCC'). fraillt suite: GCC 11 and Clang 12.0.1; CMakeLists.txt appends -O2 and defines NDEBUG with CMAKE_CXX_STANDARD 20 (the README/CI cmake call passes no CMAKE_BUILD_TYPE). |
| **Adoption** | 799 stars |
| **Last commit** | 2025-02-18 |
| **Links** | [repository](https://github.com/niXman/yas) · [benchmark](https://github.com/thekvs/cpp-serializers#readme) |

## Verdict

thekvs/cpp-serializers ran 1,000,000 serialize+deserialize round trips of a 17,416-byte record (1,000 int64 values plus 100 strings of 86 chars), averaged over 50 runs, on an unnamed Intel Core i7 with Ubuntu 16.04 and an unstated compiler. YAS 7.0.2 (binary, no header, its own memory streams) took 302.7 ms, against 1,195 ms for Boost 1.69 and 1,052 ms for cereal 1.2.2. Boost and cereal went through std::stringstream plus a copy into std::string, so part of that gap is the stream layer. The fraillt suite (GCC 11, Ubuntu 20.04 x64, 300,000 passes over 50 random 'Monster' structs) measured YAS 7.1.0 at 2,286 ms serialize / 1,770 ms deserialize, against 15,126/12,724 ms for Boost 1.77 and 10,777/9,088 ms for cereal 1.3.0.

## Use it when

- Hot-path binary serialization of structs built from arithmetic fields, std::string and std containers into memory buffers (IPC, network messages, caches), when both ends run YAS.
- Payloads dominated by std::vector or std::array of ints or floats: default binary mode copies each of these arrays with a single memcpy (the thekvs record holds 1,000 int64 values).
- Moving off cereal or Boost.Serialization code that serializes plain members, not pointers. The `serialize(Ar&)` hook and the `ar & x` / `ar(x, y)` syntax carry over with small edits.
- One serialize() definition that has to produce fast binary in production and readable JSON or text for debugging.
- Dependency-free C++11 builds across GCC 4.8.5+, Clang 3.5+, MinGW, MSVC 2017 and Emscripten.

## Skip it when

- Object graphs with raw or smart pointers, shared references or polymorphic base pointers. These are unsupported, and issue #33 asking for them has been open since 2018.
- Formats that must evolve over time. There is no object versioning (README TODO). The author says only member order and types define the layout (#143). Header-carrying archives are rejected if the header's archive version differs.
- Untrusted input. The string and container loaders call resize() with the stored 64-bit length before reading any data. `mem_istream::getch/peekch` do not check bounds. A malformed buffer can therefore force huge allocations or out-of-bounds reads.
- Compact output. Default binary writes lengths as 8-byte integers: 10,463 B vs bitsery's 6,913 B in the fraillt suite. `compacted` shrinks output, but in thekvs it was slower than Boost and cereal (2,063 ms), and it has an open uninitialized-bytes bug (#163).
- std::iostream I/O, strict JSON or big-endian targets. YAS over std::stringstream (fraillt, 10,871/11,182 ms) was no faster than cereal. JSON loading fails on scientific-notation or inf doubles (#160). base64.hpp does not compile on PowerPC big-endian (#44).

## How it is fast

Archives and streams are templates parameterized on a compile-time flags word (binary, compacted, endianness, header). Format branches resolve at compile time, and each field write reduces to a bounds check plus memcpy into a raw char buffer. `mem_ostream` starts at 20 KB and roughly doubles when full. In the default binary, non-compacted, host-endian mode, contiguous containers of arithmetic types are written and read with one memcpy of the whole element array (`can_be_processed_as_byte_array`). The library keeps no per-object state: there is no pointer tracking, and versioning is still a README TODO. The optional `compacted` varint encoding turns off the bulk-memcpy path.

## Compared with alternatives

Pick YAS over bitsery when you want Boost/cereal-style serialize() code that can also emit JSON or text. In the fraillt GCC 11 run, bitsery was faster (1,470/1,524 ms vs 2,286/1,770 ms) and 34% smaller; under Clang 12 the two were close (YAS 2,114/1,558 ms vs bitsery 2,128/1,832 ms). Pick Cista++ when deserialize latency dominates (0.16 ms vs cereal's 111 ms in its catalogued result). Pick struct_pack or FBE when the incumbent you are replacing is protobuf.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (Boost, Qt and Abseil are needed only for their optional type adapters) |
| **Minimum toolchain** | C++11 (README: GCC 4.8.5+, Clang 3.5+, MSVC 2017 in C++14 mode; config.hpp rejects MSVC older than VS2015); C++17 for std::optional/variant/string_view support |
| **Platforms** | little-endian x86/ARM-class targets, 32- and 64-bit, on GCC, Clang, MinGW and MSVC; Emscripten and wasi-sdk builds; CI covers Linux, macOS and Windows. Big-endian is untested and #44 reports a compile failure on PowerPC. |
| **Thread safety** | Not thread-safe per the author (#34). The library is stateless apart from its streams, so each thread needs its own archive and stream objects. |
| **Drop-in for the baseline** | partial — the serialize(Ar&) hook and the `ar & x` / `ar(x, y)` syntax match cereal. Boost.Serialization's hook differs only in that YAS takes no version argument. Archive classes and the wire format differ, and pointers, polymorphism and versioning are not supported. |

## Gotchas

- In `compacted` mode, unsigned reads copy only the stored low bytes into the destination and do not zero it first. A non-zero or uninitialized target keeps garbage in its upper bytes (#163, open). The author suggests wrapping it in yas::init().
- `mem_ostream(void* ptr, size)` over a caller-owned buffer does not grow safely. On overflow, realloc switches to a new heap buffer and memcpy's the old contents from the empty internal shared_buffer (a null pointer). Size fixed buffers with `yas::saved_size<F>()` first.
- YAS_OBJECT\* macros accept at most 20 members by default, and variant support is capped at 20 alternatives. Raise YAS_OBJECT_MAX_MEMBERS / YAS_VARIANT_MAX_VARIANTS if you need more (#36, #148).
- Use fixed-width types such as std::uint32_t, not std::size_t or long, for data shared between 32- and 64-bit builds (author, #100). Errors throw yas exception types; under -fno-exceptions they call std::abort().

## Caveats and trade-offs

The yas README says yas was created 'as a replacement of boost.serialization because of its insufficient speed' and cites both suites. Both suites are third-party with respect to yas: thekvs, and fraillt, who is the author of the competing library bitsery. Neither names an exact CPU model and thekvs does not name the compiler, so the evidence is not tier A. The win belongs to yas's default binary archive. In thekvs, 'yas-compact' (2063.34 ms) is slower than boost (1195.04) and cereal (1052.46). In fraillt, the std::stringstream-backed 'yas stream' case (GCC 10871/11182 ms) is no faster than cereal (10777/9088). Both runs are old: thekvs used yas 7.0.2 and boost 1.69 (repo last touched 2019); fraillt used yas 7.1.0, boost 1.77 and cereal 1.3.0. The repo has no LICENSE file and GitHub reports no license, but every sampled header under include/yas carries the Boost Software License 1.0 text.

No LICENSE file in the repository, so there is no explicit permission to reuse/modify the code despite it being publicly readable; project has had low commit activity in the last \~1.5 years.

## Maintenance

The last commit was 2025-02-18 and the last tagged release is 7.1.0 (2021-08), although master reports 7.2.0. Two bug reports filed in 2026-09 (#163, #164) are still open. The code is BSL-1.0 per every header and the author (#158), despite having no LICENSE file, and is header-only and easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification B, tier now B.
- **Tier reason:** The thekvs/cpp-serializers README results table, produced by benchmark.cpp and yas/record.cpp, is a widely cited third-party shootout. It shows yas at 302.7 ms against boost at 1195.04 ms and cereal at 1052.46 ms. It gives only 'Intel Core i7', Ubuntu 16.04 and a CMake Release build, with no compiler, so it is not A. The fraillt suite is third-party with respect to yas and states the compiler and -O2 but no CPU model.
- **Verifier notes:** All claimed numbers appear verbatim: the thekvs table and the GCC 11 table in fraillt. The ratios check out (6.6x/7.2x vs boost, 4.7x/5.1x vs cereal). License fixed: all 13 sampled headers, including include/yas/serialize.hpp, carry the BSL-1.0 notice, so usability changes to copyable. The last commit (2025-02-18) is confirmed, so the status stays stale.
- **Fields the verifier corrected:** `license`, `usability`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/thekvs/cpp-serializers#readme>
  - <https://github.com/thekvs/cpp-serializers/blob/master/CMakeLists.txt>
  - <https://github.com/thekvs/cpp-serializers/blob/master/benchmark.cpp>
  - <https://github.com/fraillt/cpp_serializers_benchmark#readme>
  - <https://github.com/fraillt/cpp_serializers_benchmark/blob/master/CMakeLists.txt>
  - <https://github.com/fraillt/cpp_serializers_benchmark/blob/master/.github/workflows/actions.yml>
  - <https://github.com/niXman/yas>
  - <https://github.com/niXman/yas/blob/master/include/yas/serialize.hpp>
- **Sources the enricher read:**
  - <https://github.com/niXman/yas>
  - <https://github.com/niXman/yas/blob/master/include/yas/serialize.hpp>
  - <https://github.com/niXman/yas/blob/master/include/yas/binary_oarchive.hpp>
  - <https://github.com/niXman/yas/blob/master/include/yas/binary_iarchive.hpp>
  - <https://github.com/niXman/yas/blob/master/include/yas/detail/io/binary_streams.hpp>
  - <https://github.com/niXman/yas/blob/master/include/yas/detail/io/header.hpp>
  - <https://github.com/niXman/yas/blob/master/include/yas/detail/io/endian_conv.hpp>
  - <https://github.com/niXman/yas/blob/master/include/yas/detail/io/exception_base.hpp>
  - <https://github.com/niXman/yas/blob/master/include/yas/mem_streams.hpp>
  - <https://github.com/niXman/yas/blob/master/include/yas/std_streams.hpp>
  - <https://github.com/niXman/yas/blob/master/include/yas/file_streams.hpp>
  - <https://github.com/niXman/yas/blob/master/include/yas/buffers.hpp>
  - <https://github.com/niXman/yas/blob/master/include/yas/object.hpp>
  - <https://github.com/niXman/yas/blob/master/include/yas/version.hpp>
  - <https://github.com/niXman/yas/blob/master/include/yas/detail/type_traits/flags.hpp>
  - <https://github.com/niXman/yas/blob/master/include/yas/detail/type_traits/type_traits.hpp>
  - <https://github.com/niXman/yas/blob/master/include/yas/detail/type_traits/serializer.hpp>
  - <https://github.com/niXman/yas/blob/master/include/yas/detail/config/config.hpp>
  - <https://github.com/niXman/yas/blob/master/include/yas/detail/tools/limit.hpp>
  - <https://github.com/niXman/yas/blob/master/include/yas/detail/tools/base_object.hpp>
  - <https://github.com/niXman/yas/blob/master/include/yas/detail/tools/save_load_string.hpp>
  - <https://github.com/niXman/yas/blob/master/include/yas/types/concepts/array.hpp>
  - <https://github.com/niXman/yas/blob/master/include/yas/types/concepts/keyval.hpp>
  - <https://github.com/niXman/yas/blob/master/include/yas/types/std/vector.hpp>
  - <https://github.com/niXman/yas/blob/master/include/yas/types/std/string.hpp>
  - <https://github.com/niXman/yas/blob/master/include/yas/types/std/optional.hpp>
  - <https://github.com/niXman/yas/blob/master/include/yas/types/utility/fundamental.hpp>
  - <https://github.com/niXman/yas/blob/master/include/yas/types/utility/usertype.hpp>
  - <https://github.com/niXman/yas/blob/master/include/yas/types/utility/value.hpp>
  - <https://github.com/niXman/yas/blob/master/.github/workflows/ci.yml>
  - <https://github.com/niXman/yas/blob/master/tests/speed/main.cpp>
  - <https://github.com/niXman/yas/issues?q=is%3Aissue>
  - <https://github.com/niXman/yas/issues/163>
  - <https://github.com/niXman/yas/issues/164>
  - <https://github.com/niXman/yas/issues/160>
  - <https://github.com/niXman/yas/issues/44>
  - <https://github.com/niXman/yas/issues/33>
  - <https://github.com/niXman/yas/issues/34>
  - <https://github.com/niXman/yas/issues/143>
  - <https://github.com/niXman/yas/issues/105>
  - <https://github.com/niXman/yas/issues/100>
  - <https://github.com/niXman/yas/issues/122>
  - <https://github.com/niXman/yas/issues/162>
  - <https://github.com/niXman/yas/issues/158>
  - <https://github.com/niXman/yas/issues/148>
  - <https://github.com/niXman/yas/issues/36>
  - <https://github.com/niXman/yas/issues/62>
  - <https://github.com/niXman/yas/commits/master>
  - <https://github.com/niXman/yas/releases>
  - <https://github.com/thekvs/cpp-serializers#readme>
  - <https://github.com/thekvs/cpp-serializers/blob/master/benchmark.cpp>
  - <https://github.com/thekvs/cpp-serializers/blob/master/data.hpp>
  - <https://github.com/thekvs/cpp-serializers/blob/master/yas/record.hpp>
  - <https://github.com/thekvs/cpp-serializers/blob/master/yas/record.cpp>
  - <https://github.com/thekvs/cpp-serializers/blob/master/boost/record.hpp>
  - <https://github.com/thekvs/cpp-serializers/blob/master/boost/record.cpp>
  - <https://github.com/thekvs/cpp-serializers/blob/master/cereal/record.hpp>
  - <https://github.com/thekvs/cpp-serializers/blob/master/cereal/record.cpp>
  - <https://github.com/fraillt/cpp_serializers_benchmark#readme>
  - <https://github.com/fraillt/cpp_serializers_benchmark/blob/master/yas/yas.cpp>
  - <https://github.com/fraillt/cpp_serializers_benchmark/blob/master/yas/yas_compression.cpp>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/nixman/yas`) · [data/wave4/enrich/raw/github_com_nixman_yas.json](../../../data/wave4/enrich/raw/github_com_nixman_yas.json) (enrichment confidence 0.85)

</details>
