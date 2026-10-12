# Reflection and code generation

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md)</sub>

**What these beat:** Boost.Serialization, cereal  
**13 entries:** 3 tier A · 1 tier B · 8 tier C · 1 tier D · 13 copyable, 0 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**Cista++**](felixguendling-cista.md) | Header-only C++17 zero-copy serializer for native structs; beats cereal \~48x serializing and \~670x deserializing flat index-linked graphs. | **A** | C++ | MIT | 🟢 active |
| 2 | [**struct_pack (yalantinglibs)**](alibaba-yalantinglibs.md) | Header-only C++ binary serializer that reflects plain structs at compile time, no .proto or macros; \~2-20x faster than protobuf. | **A** | C++ | Apache-2.0 | 🟢 active |
| 3 | [**simdjson experimental_json_builder (C++26 reflection-based…**](simdjson-experimental-json-builder.md) | Obsolete 2024 prototype of a C++26 reflection JSON serializer; about 20x nlohmann/json throughput. Now part of simdjson's builder. | **A** | C++ | Apache-2.0 | 🟢 active |
| 4 | [**YAS (Yet Another Serialization)**](nixman-yas.md) | Header-only C++11 serializer with a Boost.Serialization-style API; its binary archive ran 3.5-7.2x faster than Boost.Serialization and cereal. | **B** | C++ | BSL-1.0 | 🟡 stale |
| 5 | [**Magic Enum**](neargye-magic-enum.md) | Macro-free C++17 enum reflection (enum to string, string to enum, iteration); compiles faster than conjure_enum at scale. | **C** | C++ | MIT | 🟢 active |
| 6 | [**bitsery**](fraillt-bitsery.md) | Header-only C++11 binary serializer; 7-10x faster than Boost.Serialization and 4.7-7.3x faster than cereal in its author's benchmark. | **C** | C++ | MIT | 🟢 active |
| 7 | [**Fast Binary Encoding (FBE)**](chronoxor-fastbinaryencoding.md) | Schema-compiled binary serializer for C++ and eight other languages; about 4x lower serialize/deserialize latency than Protobuf on small messages. | **C** | C++ | MIT | 🟢 active |
| 8 | [**Enchantum**](zxshady-enchantum.md) | Header-only C++17 enum reflection (to_string, cast, iteration, bitflags); author-measured builds up to 6.4x faster than magic_enum with default settings. | **C** | C++ | MIT | 🟢 active |
| 9 | [**simple_enum**](arturbac-simple-enum.md) | Header-only C++20 enum-to-string and string-to-enum for bounded enums, with 16-183x less instantiation time than magic_enum's default-range enum_name. | **C** | C++ | BSL-1.0 | 🟢 active |
| 10 | [**SerialXML**](ejaindev-serialxml.md) | C++26 reflection-based struct-to-XML writer; author measures \~9.6x lower latency than Boost.Serialization/cereal XML archives. | **C** | C++ | MIT | 🟢 active |
| 11 | [**Djinni (Snapchat fork of dropbox/djinni)**](snapchat-djinni.md) | Snap's maintained Djinni IDL bridge generator (C++ to Java/JNI, Objective-C, WASM/TypeScript); claims 5-10x faster JNI string passing than Dropbox's original. | **C** | C++ | Apache-2.0 | 🟡 stale |
| 12 | [**ser20**](royjacobson-ser20.md) | C++20 fork of cereal with a buffered binary archive: 1.3-2.1x faster than cereal, 1.1-2.8x than Boost, on small-field data. | **C** | C++ | BSD-3-Clause | 🟡 stale |
| 13 | [**Easy Reflection**](chocolacula-easy-reflection-cpp.md) | C++17 reflection via Clang code generation; serializes structs to JSON, YAML and binary, charted 3.3x faster JSON writes than nlohmann/json. | **D** | C++ | Apache-2.0 | 🔴 abandoned |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
