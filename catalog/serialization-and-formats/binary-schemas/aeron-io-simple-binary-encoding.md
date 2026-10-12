# Simple Binary Encoding (SBE)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Code generator for FIX SBE fixed-layout binary messages; C++ flyweight codecs beat Protobuf \~9x encode, \~7x decode (one small-message test).

| | |
|---|---|
| **Beats** | Protobuf |
| **Claimed result** | \~9.2x faster serialize (35 ns vs 322 ns) and \~6.75x faster deserialize (52 ns vs 351 ns) than Protobuf (ratios derived from page data) |
| **Workload** | Serialize/deserialize a small trading domain object (one Account with Wallet and 3 Orders, 128 bytes in memory) in chronoxor's CppBenchmark-based CppSerialization suite. SBE encodes it to 138 bytes and Protobuf to 120 bytes. Both timings include converting from/to the plain C++ domain model: Protobuf builds a fresh message per operation without an arena, while SBE encodes in place into a fixed 1 KB buffer. Also compared: Cap'n Proto, FastBinaryEncoding, FlatBuffers, zpp::bits and JSON (RapidJSON). |
| **Metric** | latency |
| **Hardware** | Apple M1 Pro (10 cores, reported 2.4 GHz), 32 GiB RAM, macOS (Darwin 24.5.0). All 15 CppBenchmark reports in the README come from this one machine, run on 2025-07-16 |
| **Compiler and flags** | chronoxor/CppSerialization suite at commit 8f6e4240 with sbe-all-1.35.6.jar; CMake sets C++23; compiler and optimization flags not stated. SBE_NO_BOUNDS_CHECK is never defined, so SBE bounds checks were likely on. |
| **Adoption** | 3.5k stars |
| **Last commit** | 2026-09-17 |
| **Links** | [repository](https://github.com/aeron-io/simple-binary-encoding) · [benchmark](https://github.com/chronoxor/CppSerialization) |

## Verdict

chronoxor/CppSerialization is a 167-star suite by the author of FastBinaryEncoding. In it, converting a 128-byte Account with 3 Orders from plain C++ structs and back took 35 ns to encode and 52 ns to decode with SBE, vs 322/351 ns for Protobuf (a fresh message with no arena, SerializeToString/ParseFromString). The run was on an Apple M1 Pro (macOS, 'release' configuration); the build scripts set C++23 but the compiler and flags are unstated, and Protobuf was an unpinned main-branch build. The reports are dated 2025-07-16, when the suite vendored sbe-all-1.35.6.jar; the 1.40.1 jar was only added on 2026-09-09. The suite does not define SBE_NO_BOUNDS_CHECK, so SBE's default bounds checks were presumably on.

## Use it when

- Low-latency trading or messaging paths (market data, order entry, Aeron transport) where messages are mostly fixed-width numbers, enums and short fixed char arrays, and both ends share one SBE schema, for example an exchange feed published as SBE XML.
- Hot paths that must not allocate: encoding straight into a preallocated send or ring buffer, and decoding in place from the receive buffer.
- Small messages (tens to a few hundred bytes), where Protobuf's per-message object construction and varint parsing dominate. The measured case was a 138-byte message with 3 repeating-group entries.
- Polyglot systems that need the same wire format from C++, C, Java, C#, Go and Rust, all generated from one schema.
- Consumers that read each message once, front to back (streaming decode), rather than looking fields up at random.

## Skip it when

- Schemas that change often or need fields removed, changed or reordered. Only adding fields at the end of a block (with sinceVersion, presence=optional) stays backward-compatible, and composites cannot gain fields without a new message template and schema version.
- Sparse or mostly-optional data. Optional fields still take their full fixed width and use in-band null sentinels, and fixed-length char arrays are padded. The cited test encoded to 138 bytes vs Protobuf's 120.
- Random access or partial reads of large nested documents. The FAQ says you cannot randomly access fields. Groups and var data must be walked, or explicitly skipped, in schema order to reach whatever follows them.
- Parsing untrusted input with only the built-in checks. Open issue #969 (since 2024-01) reports that a received group blockLength is not validated against the fields being read, so a crafted small blockLength lets field reads run past the buffer.
- Builds that cannot run a JVM at codegen time or must use -fno-exceptions. The generator is a Java 17 jar, and generated code throws std::runtime_error, e.g. for group index overrun or an unknown enum value, even with bounds checks off.

## How it is fast

Every field has a fixed offset inside its root or group block. A getter or setter therefore compiles to a memcpy of a native-width value at buffer + constant offset, plus a __builtin_bswap only when the schema byte order differs from the host. There is no varint coding, tag dispatch or presence bookkeeping. The flyweight pattern reads and writes the caller's buffer directly, with no intermediate message object, heap allocation or extra copy; the project's Design Principles call these 'copy-free', 'allocation-free' and 'native type mapping'. Access is strictly ascending and sequential, so the codec tracks one position cursor, and the only per-advance cost is a __builtin_expect-hinted bounds compare, which SBE_NO_BOUNDS_CHECK compiles out.

## Compared with alternatives

Pick SBE over YaFF, ProtoCache or Apache Fory when you need a standardized (FIX), cross-language, fixed-layout wire format that is written in place into your own buffer with no allocation, as in market-data and order gateways. The siblings report their wins over Protobuf mostly on read, decode-and-traverse or throughput benchmarks; prefer them when your data is nested or optional-heavy and not consumed strictly in order, where SBE's fixed layout and sequential-access rule fit poorly.

## Integration

| | |
|---|---|
| **Form** | header-only (headers generated per schema by the Java sbe-all jar; the optional on-the-fly (OTF) decoder is a header-only CMake INTERFACE target) |
| **Dependencies** | Generated C++ codecs: C++ standard library only. Code generation: Java 17+ runtime to run sbe-all (the 'all' jar bundles Agrona). Building this repo: CMake 3.30+ and Gradle. |
| **Minimum toolchain** | C++11 for generated codecs; C++17 adds std::string_view accessors and [[nodiscard]], and C++20 adds std::span overloads. DTOs require C++17. CI builds with GCC 11-14 and Clang 17-22 on Ubuntu 24.04, Xcode clang on macOS 15, and MSVC on windows-latest. |
| **Platforms** | Linux, macOS and Windows per the README. Any CPU where __BYTE_ORDER__ is defined (GCC/Clang) or WIN32 is set; the generated header #errors otherwise. Big- and little-endian hosts are both handled via byte swaps. The cited benchmark ran on aarch64 (Apple M1 Pro). |
| **Thread safety** | Not documented. Flyweights are mutable cursors (buffer pointer, offset, position) with no locking, so give each thread its own encoder/decoder instance. |
| **Drop-in for the baseline** | no |

## Gotchas

- Access order is a contract that is not checked by default. Groups and var data must be encoded and decoded in schema order and skipped explicitly, with next() called per group element. Violations silently produce invalid messages or misreads. Runtime checks need codegen with -Dsbe.generate.precedence.checks=true plus compiling with SBE_ENABLE_PRECEDENCE_CHECKS, and the wiki warns of significant overhead.
- Bounds checks are on by default and throw std::runtime_error (e.g. 'buffer too short [E100]'). SBE's own sbe-benchmarks define SBE_NO_BOUNDS_CHECK in Release builds, so compare numbers only at the same setting.
- Decoded values are views into the buffer; copy anything you keep after the buffer is reused. getXAsString() allocates a std::string, while getXAsStringView() (C++17) does not.
- Older-version reads return in-band null sentinels for fields past the acting block length, e.g. the minimum value for signed integers and the maximum for unsigned. Test xInActingVersion() rather than comparing values.

## Caveats and trade-offs

The numbers come from a small third-party shootout (chronoxor/CppSerialization, 167 stars) run by the author of a competing format (FastBinaryEncoding), not by SBE's team. SBE's own sbe-benchmarks (Car/MarketData, C++ and Java) do not compare against Protobuf. Compiler and flags are not stated, and everything ran on a single Apple M1 Pro on 2025-07-16 with SBE 1.40.1. The message is tiny (138 bytes), so the results may not generalize to larger or variable-length-heavy messages. zpp::bits was marginally faster in the same table (34/37 ns).

Requires an SBE XML schema and code generator; designed around FIX-derived low-latency financial messaging, less flexible than Protobuf for evolving/optional fields

## Maintenance

Actively maintained by Real Logic/Aeron (1.40.2 released and last commit on 2026-09-17, 3.5k stars) under Apache-2.0. The C++ side is just generated headers, so it is easy to adopt as long as you can run the Java generator in your build.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification B, tier now C.
- **Tier reason:** chronoxor/CppSerialization's README table and per-protocol CppBenchmark reports show SBE at 35/52 ns and Protobuf at 322/351 ns, and the benchmark code is public (performance/sbe_\*.cpp, protobuf_\*.cpp). The compiler and flags are not stated (only 'Process configuration: release'), so it is not A. It is also a small suite (167 stars) run by the author of a competing format (FastBinaryEncoding), not a well-known independent suite, so it is not B. This matches how the wave-1 verifier tiered Cap'n Proto and zpp::bits from the same suite.
- **Verifier notes:** The numbers match the SBE and Protobuf rows and their detailed reports exactly. I downgraded B to C because the suite is neither well-known nor fully neutral, and compiler and flags are missing. The record's claim that the repo logs 'several per-run hardware configs' is wrong: every report is the same M1 Pro. The metadata is correct (Apache-2.0, 3,511 stars, last commit 2026-09-17, active).
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/aeron-io/simple-binary-encoding>
  - <https://github.com/aeron-io/simple-binary-encoding/blob/master/README.md>
  - <https://github.com/aeron-io/simple-binary-encoding/tree/master/sbe-benchmarks>
  - <https://github.com/chronoxor/CppSerialization>
  - <https://github.com/chronoxor/CppSerialization/blob/main/README.md>
  - <https://github.com/chronoxor/CppSerialization/blob/main/CMakeLists.txt>
  - <https://github.com/chronoxor/CppSerialization/blob/main/.gitlinks>
  - <https://github.com/chronoxor/CppSerialization/blob/main/modules/protobuf.cmake>
  - <https://github.com/chronoxor/CppSerialization/tree/main/modules/sbe>
  - <https://github.com/chronoxor/CppSerialization/blob/main/performance/protobuf_serialize.cpp>
  - <https://github.com/chronoxor/CppSerialization/blob/main/performance/protobuf_deserialize.cpp>
  - <https://github.com/chronoxor/CppSerialization/blob/main/performance/sbe_serialize.cpp>
  - <https://github.com/chronoxor/CppSerialization/blob/main/performance/sbe_deserialize.cpp>
- **Sources the enricher read:**
  - <https://github.com/aeron-io/simple-binary-encoding>
  - <https://github.com/aeron-io/simple-binary-encoding/blob/master/README.md>
  - <https://github.com/aeron-io/simple-binary-encoding/blob/master/CMakeLists.txt>
  - <https://github.com/aeron-io/simple-binary-encoding/blob/master/build.gradle>
  - <https://github.com/aeron-io/simple-binary-encoding/blob/master/cppbuild/cppbuild>
  - <https://github.com/aeron-io/simple-binary-encoding/blob/master/.github/workflows/ci.yml>
  - <https://github.com/aeron-io/simple-binary-encoding/blob/master/.github/workflows/slow.yml>
  - <https://github.com/aeron-io/simple-binary-encoding/blob/master/sbe-tool/src/main/java/uk/co/real_logic/sbe/generation/cpp/CppGenerator.java>
  - <https://github.com/aeron-io/simple-binary-encoding/blob/master/sbe-tool/src/main/java/uk/co/real_logic/sbe/generation/cpp/CppDtoGenerator.java>
  - <https://github.com/aeron-io/simple-binary-encoding/blob/master/sbe-tool/src/main/java/uk/co/real_logic/sbe/SbeTool.java>
  - <https://github.com/aeron-io/simple-binary-encoding/blob/master/sbe-tool/src/main/cpp/CMakeLists.txt>
  - <https://github.com/aeron-io/simple-binary-encoding/blob/master/sbe-benchmarks/src/main/cpp/CMakeLists.txt>
  - <https://github.com/aeron-io/simple-binary-encoding/blob/master/sbe-benchmarks/src/main/cpp/SbeMarketDataCodecBench.h>
  - <https://github.com/aeron-io/simple-binary-encoding/releases>
  - <https://github.com/aeron-io/simple-binary-encoding/commits/master>
  - <https://github.com/aeron-io/simple-binary-encoding/wiki>
  - <https://github.com/aeron-io/simple-binary-encoding/wiki/Cpp-User-Guide>
  - <https://github.com/aeron-io/simple-binary-encoding/wiki/Frequently-Asked-Questions>
  - <https://github.com/aeron-io/simple-binary-encoding/wiki/Design-Principles>
  - <https://github.com/aeron-io/simple-binary-encoding/wiki/Message-Versioning>
  - <https://github.com/aeron-io/simple-binary-encoding/wiki/Sbe-Tool-Guide>
  - <https://github.com/aeron-io/simple-binary-encoding/wiki/Safe-Flyweight-Usage>
  - <https://github.com/aeron-io/simple-binary-encoding/issues?q=C%2B%2B>
  - <https://github.com/aeron-io/simple-binary-encoding/issues/969>
  - <https://github.com/aeron-io/simple-binary-encoding/issues/1076>
  - <https://github.com/aeron-io/simple-binary-encoding/issues/599>
  - <https://github.com/aeron-io/simple-binary-encoding/issues/1100>
  - <https://github.com/chronoxor/CppSerialization>
  - <https://github.com/chronoxor/CppSerialization/blob/main/README.md>
  - <https://github.com/chronoxor/CppSerialization/blob/main/CMakeLists.txt>
  - <https://github.com/chronoxor/CppSerialization/blob/main/.gitlinks>
  - <https://github.com/chronoxor/CppSerialization/blob/main/proto/trade.h>
  - <https://github.com/chronoxor/CppSerialization/blob/main/performance/sbe_serialize.cpp>
  - <https://github.com/chronoxor/CppSerialization/blob/main/performance/sbe_deserialize.cpp>
  - <https://github.com/chronoxor/CppSerialization/blob/main/performance/protobuf_serialize.cpp>
  - <https://github.com/chronoxor/CppSerialization/blob/main/performance/protobuf_deserialize.cpp>
  - <https://github.com/chronoxor/CppSerialization/tree/8f6e4240/modules/sbe>
  - <https://github.com/chronoxor/CppSerialization/commit/af39f3dc>
  - <https://github.com/chronoxor/CppSerialization/commit/20147706>
  - <https://github.com/chronoxor/CppSerialization/commit/9e135bb4>
  - <https://github.com/chronoxor/CppSerialization/commits/main/modules/sbe>
  - <https://github.com/chronoxor/CppSerialization/commits/main/README.md>
  - <https://github.com/search?q=SBE_NO_BOUNDS_CHECK+repo%3Achronoxor%2FCppSerialization&type=code>
  - <https://github.com/chronoxor/CppCMakeScripts/blob/main/SetCompilerFeatures.cmake>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/aeron-io/simple-binary-encoding`) · [data/wave4/enrich/raw/github_com_aeron_io_simple_binary_encoding.json](../../../data/wave4/enrich/raw/github_com_aeron_io_simple_binary_encoding.json) (enrichment confidence 0.82)

</details>
