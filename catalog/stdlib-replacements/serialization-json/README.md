# JSON serialization

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md)</sub>

**What these beat:** iostreams + std::string, std::format (record actual baseline)  
**17 entries:** 7 tier A · 0 tier B · 9 tier C · 1 tier D · 16 copyable, 1 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**scnlib**](eliaskosunen-scnlib.md) | Type-safe scanf/istream replacement; \~3-5x faster than std::stringstream and sscanf at parsing ints, floats, and words. | **A** | C++ | Apache-2.0 | 🟢 active |
| 2 | [**json.cpp**](jart-json-cpp.md) | Lean C++11 JSON parser/serializer beating nlohmann::json 2-3x on parse/round-trip latency and compile time. | **A** | C++ | Apache-2.0 | 🟢 active |
| 3 | [**mpack**](ludocode-mpack.md) | Embeddable C MessagePack codec; beat msgpack-c 1.1-3x in its author's 2016 suite; independent 2026 run: encode only. | **A** | C | MIT | 🟢 active |
| 4 | [**DAW JSON Link**](beached-daw-json-link.md) | Header-only C++ JSON library that parses straight into your typed structs, beating RapidJSON, simdjson DOM, Boost.JSON and nlohmann. | **A** | C++ | BSL-1.0 | 🟢 active |
| 5 | [**cjson.cpp**](rfgplk-cjson-cpp.md) | Header-only SIMD index/tape JSON parser for C++26 on the micron runtime, \~9-31x faster than nlohmann::json. | **A** | C++ | MIT | 🟢 active |
| 6 | [**HPS (High Performance Serialization)**](jl2922-hps.md) | Header-only C++11 serializer for STL/user types; faster and smaller than Boost.Serialization, no schema needed. | **A** | C++ | MIT | 🔴 abandoned |
| 7 | [**pbtools**](eerimoq-pbtools.md) | Python-generated C11 proto3 encoder/decoder with arena workspaces; beat libprotobuf C++ and protobuf-c on small messages at -O2. | **A** | C | MIT | 🔴 abandoned |
| 8 | [**Cap'n Proto**](capnproto-capnproto.md) | Zero-copy binary serialization/RPC system: wire format equals in-memory layout, beating RapidJSON-based JSON serialize/deserialize by \~2.8x/1.6x. | **C** | C++ | MIT | 🟢 active |
| 9 | [**protobuf-c**](protobuf-c-protobuf-c.md) | Wire-compatible Protocol Buffers runtime and protoc plugin for C; about 5x nanopb's encode+decode throughput on host CPUs. | **C** | C | BSD-2-Clause | 🟢 active |
| 10 | [**mrpt-serialization**](mrpt-mrpt.md) | MRPT's portable, versioned binary archive (CArchive); via the gtsam2mrpt_serial bridge it serializes GTSAM factor graphs about 2x faster than Boost. | **C** | C++ | BSD-3-Clause | 🟢 active |
| 11 | [**zpp::bits**](eyalz800-zpp-bits.md) | Header-only C++20 binary serializer using compile-time aggregate reflection; no schema, no codegen, faster than JSON via RapidJSON in third-party benchmarks. | **C** | C++ | MIT | 🟢 active |
| 12 | [**utl::json (part of the UTL header-only library collection)**](dmitribogdanov-utl-serialization-json.md) | Header-only C++17 JSON library, 2-4x faster than nlohmann::json at parsing and serializing; RapidJSON still wins parsing. | **C** | C++ | MIT | 🟢 active |
| 13 | [**Protocol Puffers (protopuf)**](pragmatwice-protopuf.md) | Header-only C++20 protobuf-wire-compatible codec with messages as template types; encodes a tiny message 2-4x faster than libprotobuf. | **C** | C++ | Apache-2.0 | 🟢 active |
| 14 | [**BitSerializer**](pavelkisliak-bitserializer.md) | C++17 multi-format struct serializer whose built-in MsgPack archive saves about 33x and loads about 22x faster than nlohmann::json's MsgPack path. | **C** | C++ | MIT | 🟢 active |
| 15 | [**blazingio**](purplesyringa-blazingio.md) | Header-only mmap+SIMD std::cin/cout replacement, \~5x faster than libstdc++ iostream for competitive-programming I/O. | **C** | C++ | MIT | 🟡 stale |
| 16 | [**Tachyon.JSON v6**](mrcodechef-tachyon-json.md) | Single-header AVX2 JSON parser under a proprietary license; benchmarks nlohmann/simdjson but times only its structural-bitmask build, not full parsing. | **C** | C++ | Proprietary (TACHYON… (study only) | 🟢 active |
| 17 | [**cmp**](camgunz-cmp.md) | Tiny allocation-free C89 MessagePack reader/writer; smaller than msgpack-c but 13-30% slower on write in the only shootout. | **D** | C | MIT | 🟡 stale |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
