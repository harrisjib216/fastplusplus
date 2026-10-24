# Serialization and formats

<sub>[fastpp](../../README.md) › [Catalog](../README.md)</sub>

JSON, YAML, TOML, XML and binary-schema libraries measured against RapidJSON, nlohmann/json, Protobuf and the other usual defaults.

**170 entries in 4 categories:** 57 tier A · 19 tier B · 89 tier C · 5 tier D

| Category | Entries | A | B | C | D | What they beat |
|---|--:|--:|--:|--:|--:|---|
| [Binary schemas](binary-schemas/README.md) | 53 | 16 | 11 | 25 | 1 | Protobuf, FlatBuffers, Cap'n Proto, MessagePack |
| [JSON](json/README.md) | 70 | 29 | 5 | 33 | 3 | RapidJSON, nlohmann/json, simdjson, serde_json, encoding/json |
| [Reflection and code generation](reflection-and-codegen/README.md) | 14 | 3 | 1 | 9 | 1 | Boost.Serialization, cereal |
| [YAML, TOML and XML](yaml-toml-xml/README.md) | 33 | 9 | 2 | 22 | 0 | libyaml, yaml-cpp, toml++, libxml2, pugixml |

## Most-adopted tier A picks

Tier A, copyable and actively maintained, ordered by GitHub stars.

| # | Project | What it is | Category | Tier | Language | License | Status |
|--:|---|---|---|:-:|---|---|---|
| 1 | [**simdjson**](json/simdjson-simdjson.md) | SIMD-accelerated JSON parser with full UTF-8 validation; \~4x faster than RapidJSON, \~25x than nlohmann. | [JSON](json/README.md) | **A** | C++ | Apache-2.0 OR MIT | 🟢 active |
| 2 | [**gjson**](json/tidwall-gjson.md) | Go library that reads single values from JSON by dot-path without unmarshalling; 3.2-5.7x lower latency than encoding/json structs. | [JSON](json/README.md) | **A** | Go | MIT | 🟢 active |
| 3 | [**cJSON**](json/davegamble-cjson.md) | Two-file ANSI C DOM JSON parser/printer; parsed 13 of 14 paper benchmark files faster than nlohmann/json (2019). | [JSON](json/README.md) | **A** | C | MIT | 🟢 active |
| 4 | [**Sonic**](json/bytedance-sonic.md) | ByteDance's JIT- and SIMD-accelerated Go JSON library; about 1.9-3.4x the throughput of encoding/json on amd64. | [JSON](json/README.md) | **A** | Go | Apache-2.0 | 🟢 active |
| 5 | [**jsonparser (buger)**](json/buger-jsonparser.md) | Zero-allocation, path-based JSON field extractor for Go; 3-6.5x faster than encoding/json struct unmarshal on the project's benchmarks. | [JSON](json/README.md) | **A** | Go | MIT | 🟢 active |
| 6 | [**rkyv**](binary-schemas/rkyv-rkyv.md) | Rust zero-copy serialization crate; faster serialize and in-place reads than Rust FlatBuffers, Cap'n Proto, prost and rmp-serde. | [Binary schemas](binary-schemas/README.md) | **A** | Rust | MIT | 🟢 active |
| 7 | [**yyjson**](json/ibireme-yyjson.md) | ANSI C JSON DOM library beating RapidJSON via single-file design, in-situ parsing, and low-allocation strategy. | [JSON](json/README.md) | **A** | C | MIT | 🟢 active |
| 8 | [**jaq**](json/01mf02-jaq.md) | Rust reimplementation of the jq language and CLI; faster than jq 1.8.1 on 23 of 30 author filter benchmarks. | [JSON](json/README.md) | **A** | Rust | MIT | 🟢 active |
| 9 | [**Jansson**](json/akheron-jansson.md) | Dependency-free C library for a mutable, reference-counted JSON tree; stringified 1.35x faster than JsonCpp 1.0.0 in a 2016 independent run. | [JSON](json/README.md) | **A** | C | MIT | 🟢 active |
| 10 | [**json-c**](json/json-c-json-c.md) | Long-standing reference-counted C JSON DOM; in a 2016 independent run it stringified a parsed canada.json 4x faster than Jansson, losing elsewhere. | [JSON](json/README.md) | **A** | C | MIT | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
