# bitsery

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Reflection and code generation](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++11 binary serializer; 7-10x faster than Boost.Serialization and 4.7-7.3x faster than cereal in its author's benchmark.

| | |
|---|---|
| **Beats** | Boost.Serialization and cereal |
| **Claimed result** | fraillt/cpp_serializers_benchmark README, 'general' test case. GCC 11: bitsery 1470 ms ser / 1524 ms des vs boost 15126/12724 ms (\~10.3x/\~8.3x) and cereal 10777/9088 ms (\~7.3x/\~6.0x). Clang 12.0.1: bitsery 2128/1832 ms vs boost 16011/13017 ms (\~7.5x/\~7.1x) and cereal 9977/8565 ms (\~4.7x/\~4.7x). Ratios derived from page data. bitsery's own README shows an older GCC 10.3.0 run: bitsery 1119/1166 ms vs boost 15391/12912 ms and cereal 10518/10245 ms. |
| **Workload** | Serialize/deserialize a vector of 50 randomly generated nested 'Monster' structs (fixed seed; vectors, strings, enums, weapons) 300,000 times after 5 warmup rounds, on Ubuntu 20.04 x64 with GCC 11 and Clang 12.0.1 (fraillt/cpp_serializers_benchmark suite) |
| **Metric** | throughput |
| **Hardware** | Ubuntu 20.04 x64 (exact CPU model not stated) |
| **Compiler and flags** | GCC 11 and Clang 12.0.1. CMakeLists.txt appends -O2, defines NDEBUG, MONSTERS=50 and SAMPLES=300000, and sets CMAKE_CXX_STANDARD 20. The README/CI cmake call passes no CMAKE_BUILD_TYPE (the CI job names say 'Release'). |
| **Adoption** | 1.3k stars |
| **Last commit** | 2025-10-08 |
| **Links** | [repository](https://github.com/fraillt/bitsery) · [benchmark](https://github.com/fraillt/cpp_serializers_benchmark#readme) |

## Verdict

In the author's own cpp_serializers_benchmark (50 random nested Monster structs, 300,000 serialize/deserialize iterations, -O2, Ubuntu 20.04 x64, CPU not stated), bitsery took 1470/1524 ms on GCC 11 vs 15126/12724 ms for Boost and 10777/9088 ms for cereal (about 10.3x/8.3x and 7.3x/6.0x). On Clang 12.0.1 the gap shrinks to about 7.5x/7.1x vs Boost and 4.7x vs cereal. Part of the gap is I/O: the Boost and cereal harnesses build a new std::stringstream each call, while bitsery reuses a std::vector buffer.

## Use it when

- Real-time C++-to-C++ messaging (game netcode, RPC) where you control both ends and want small payloads: 6913 B vs 10413-11037 B for cereal/Boost on the benchmark's Monster set.
- Parsing untrusted network input into ordinary STL types: every dynamic container carries a maxSize, and bounds-checked reads report a ReaderError code instead of throwing (use v5.2.5 or later if you use the pointer extensions).
- Hot loops that serialize into a reused std::vector or a fixed byte array: the author's fixed-buffer run serializes in 927 ms vs 1470 ms for the default resizable buffer (GCC 11).
- Bandwidth-constrained links where you know value ranges: ValueRange/Entropy bit-packing cut the benchmark payload from 6913 B to 4213 B for about 30% more CPU on GCC 11.
- Cross-platform binary data (x86/x64, ARM, big-endian targets): byte widths are fixed in code and the endianness is a config option.

## Skip it when

- You need JSON/XML/text archives, or readers in other languages: bitsery is binary-only with no schema or IDL, so non-C++ consumers must decode the layout by hand.
- You want Boost.Serialization-style automatic class versioning and pointer tracking: bitsery has only append-only schema evolution (Growable, 4-byte size prefix per object), and pointers and polymorphism need explicit extensions, a PointerLinkingContext and registered class hierarchies.
- You need the absolute fastest C++ binary serializer: zpp_bits takes 733/693 ms vs bitsery's 1470/1524 ms on the same page (GCC 11), and under Clang 12 YAS ties on serialize and wins on deserialize (2114/1558 vs 2128/1832 ms).
- You serialize to files or streams and must detect write failure: the stream adapter ignores short sputn writes (issue #110, open), and stringstream deserialize runs at 6180 ms vs 1524 ms for the buffer adapter.
- A single container or string has 2^30 or more elements: the length prefix only asserts size &lt; 0x40000000 and encodes a wrong length in release builds.

## How it is fast

The Serializer and adapters are templates resolved at compile time (CRTP adapters with explicit value sizes). Each field compiles to a fixed-size copy into a contiguous byte buffer, with no virtual dispatch and no type or version metadata. Contiguous containers of fundamental types go out as one block copy when no endian swap is needed. The std::vector output adapter grows by 1.5x+128 bytes (rounded down to 64) on a noinline cold path and reuses existing capacity, so a reused buffer serializes without allocating. Lengths use a 1-, 2- or 4-byte varint prefix, which keeps the Monster payload at 6913 B, against 10413 B for cereal and 11037 B for Boost. Read-side checks are compile-time switches (CheckAdapterErrors, CheckDataErrors), and turning them off cut GCC 11 deserialize time from 1524 to 982 ms.

## Compared with alternatives

Over YAS: bitsery's payload is 34% smaller (6913 B vs 10463 B) and it is faster under GCC 11 (1470/1524 vs 2286/1770 ms), though YAS matches or beats it under Clang 12. Over Cista++, struct_pack and FBE: pick bitsery for hand-written serialize() functions with enforced max sizes and bit-level packing into ordinary STL types; those entries were measured against cereal or protobuf on different suites, so their numbers do not compare directly.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (GoogleTest only to build its tests) |
| **Minimum toolchain** | C++11 (tutorial names GCC 4.9.4, Clang 3.4, MSVC 2015); some extensions such as StdVariant need C++17; CMake 3.25 if you consume its CMake package; CI runs GCC 14, Clang 18, MSVC latest (C++17) and macOS |
| **Platforms** | any with 8-bit bytes; tested on Windows, Linux and macOS; little-endian default, big-endian configurable |
| **Thread safety** | not documented; Serializer/Deserializer objects hold per-instance adapter state, and the author says serialization is inherently sequential, so parallelism means splitting the data yourself (issue #97) |
| **Drop-in for the baseline** | partial — brief_syntax.h accepts cereal-style s(a, b, c) calls, so cereal serialize functions port mechanically, but the signature, adapters and wire format differ; bitsery is not source- or data-compatible with Boost.Serialization or cereal archives |

## Gotchas

- The std::vector output buffer is resized ahead of the write position (1.5x+128 bytes, at least current capacity), so buffer.size() exceeds the payload. Always use writtenBytesCount() or the value quickSerialization returns (issue #128).
- Serialization-side limits are assert-only: exceeding maxSize, overflowing a fixed-size output buffer, and lengths of 2^30 or more are not detected in NDEBUG builds (the author confirmed this is intended, issues #26 and #70). Size the buffer first with the MeasureSize adapter.
- On a read error the input adapter fills the remaining reads with zeros and sets a sticky ReaderError, so the object can be partly filled. Check both fields of quickDeserialization's {error, completedSuccessfully} result.
- Pointer extensions: in v5.2.4 and earlier, a crafted payload could make shared pointers alias objects of a different type (type confusion, vtable hijack); v5.2.5 fixes this. The default StandardRTTI uses typeid().hash_code(), which crashed on Apple ARM libc++ (issue #101, open; the workaround is a custom RTTI). ValueRange&lt;float&gt; can raise a false InvalidData (issue #130, open).

## Caveats and trade-offs

This is a first-party comparison: the benchmark repo belongs to bitsery's author (fraillt). The compiler and -O2 are stated but the CPU model is not, so the tier is C. The headline numbers in bitsery's README (1119/1166 ms, GCC 10.3.0) come from an older run than the GCC 11 / Clang 12 tables in the benchmark repo. bitsery's lead shrinks under Clang (\~4.7x vs cereal). zpp_bits beats bitsery on the same page (GCC 733/693 ms). The page itself notes that the protobuf and flatbuffers comparisons are not fully fair because of conversion to the custom types.

No implicit metadata/schema (compile-time only serialize() functions must be written per type); forward/backward compatibility and polymorphism require opting into specific extensions rather than being automatic like Boost.Serialization's archive system.

## Maintenance

Active but slow-moving: v5.2.5 (2025-10-09) is the latest release and commit, and the author still answers issues in 2026 (issue #129, August 2026); MIT-licensed, header-only and dependency-free, so vendoring is easy.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification C, tier now C.
- **Tier reason:** This is a first-party suite: fraillt/cpp_serializers_benchmark is by bitsery's author, with code in bitsery/bitsery.cpp, boost/boost.cpp, cereal/cereal.cpp and testing_core/. It states the compiler (GCC 11 / Clang 12.0.1) and flags (-O2 -DNDEBUG in CMakeLists.txt) but no CPU model. That rules out A, and being first-party rules out B.
- **Verifier notes:** The claim mixed two runs. The 1119/1166 ms figures come from bitsery's README (GCC 10.3.0, different boost/cereal numbers), and the 1524/1561 ms figures on the benchmark page are deserialize times, not serialize times. So '\~10-14x vs boost' and '\~7-9x vs cereal' overstated the benchmark_url data, which shows \~7.1-10.3x and \~4.7-7.3x for the 'general' case. last_commit corrected to 2025-10-08 (the push was 2025-10-09). The status stays 'active' but passes the 12-month mark in mid-October 2026. The page tables match the repo's GitHub Actions ubuntu-20.04 matrix, so they may come from CI runners, but I could not confirm that; hardware is left as is.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/fraillt/cpp_serializers_benchmark#readme>
  - <https://github.com/fraillt/cpp_serializers_benchmark/blob/master/CMakeLists.txt>
  - <https://github.com/fraillt/cpp_serializers_benchmark/blob/master/.github/workflows/actions.yml>
  - <https://github.com/fraillt/cpp_serializers_benchmark/blob/master/tools/index.js>
  - <https://github.com/fraillt/bitsery>
  - <https://github.com/fraillt/bitsery#readme>
- **Sources the enricher read:**
  - <https://github.com/fraillt/bitsery>
  - <https://github.com/fraillt/bitsery#readme>
  - <https://github.com/fraillt/bitsery/blob/master/doc/design/README.md>
  - <https://github.com/fraillt/bitsery/blob/master/doc/design/fundamental_types.md>
  - <https://github.com/fraillt/bitsery/blob/master/doc/design/errors.md>
  - <https://github.com/fraillt/bitsery/blob/master/doc/design/extensions.md>
  - <https://github.com/fraillt/bitsery/blob/master/doc/design/pointers.md>
  - <https://github.com/fraillt/bitsery/blob/master/doc/tutorial/hello_world.md>
  - <https://github.com/fraillt/bitsery/blob/master/include/bitsery/adapter/buffer.h>
  - <https://github.com/fraillt/bitsery/blob/master/include/bitsery/details/adapter_common.h>
  - <https://github.com/fraillt/bitsery/blob/master/include/bitsery/common.h>
  - <https://github.com/fraillt/bitsery/blob/master/include/bitsery/serializer.h>
  - <https://github.com/fraillt/bitsery/blob/master/include/bitsery/deserializer.h>
  - <https://github.com/fraillt/bitsery/blob/master/include/bitsery/traits/core/std_defaults.h>
  - <https://github.com/fraillt/bitsery/blob/master/include/bitsery/ext/growable.h>
  - <https://github.com/fraillt/bitsery/blob/master/include/bitsery/ext/utils/rtti_utils.h>
  - <https://github.com/fraillt/bitsery/blob/master/include/bitsery/ext/utils/polymorphism_utils.h>
  - <https://github.com/fraillt/bitsery/blob/master/CHANGELOG.md>
  - <https://github.com/fraillt/bitsery/blob/master/CMakeLists.txt>
  - <https://github.com/fraillt/bitsery/blob/master/.github/workflows/on_linux.yml>
  - <https://github.com/fraillt/bitsery/blob/master/.github/workflows/on_windows.yml>
  - <https://github.com/fraillt/bitsery/tags>
  - <https://github.com/fraillt/bitsery/issues>
  - <https://github.com/fraillt/bitsery/issues/26>
  - <https://github.com/fraillt/bitsery/issues/70>
  - <https://github.com/fraillt/bitsery/issues/97>
  - <https://github.com/fraillt/bitsery/issues/101>
  - <https://github.com/fraillt/bitsery/issues/110>
  - <https://github.com/fraillt/bitsery/issues/128>
  - <https://github.com/fraillt/bitsery/issues/129>
  - <https://github.com/fraillt/bitsery/issues/130>
  - <https://gist.github.com/TrebledJ/750abc64a826f19dd2d6774724629b71>
  - <https://github.com/fraillt/cpp_serializers_benchmark#readme>
  - <https://github.com/fraillt/cpp_serializers_benchmark/blob/master/bitsery/bitsery.cpp>
  - <https://github.com/fraillt/cpp_serializers_benchmark/blob/master/bitsery/bitsery_unsafe_read.cpp>
  - <https://github.com/fraillt/cpp_serializers_benchmark/blob/master/bitsery/bitsery_fixed_buffer.cpp>
  - <https://github.com/fraillt/cpp_serializers_benchmark/blob/master/boost/boost.cpp>
  - <https://github.com/fraillt/cpp_serializers_benchmark/blob/master/cereal/cereal.cpp>
  - <https://github.com/fraillt/cpp_serializers_benchmark/blob/master/testing_core/test.cpp>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/fraillt/bitsery`) · [data/wave4/enrich/raw/github_com_fraillt_bitsery.json](../../../data/wave4/enrich/raw/github_com_fraillt_bitsery.json) (enrichment confidence 0.85)

</details>
