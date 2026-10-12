# JSON

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md)</sub>

**What these beat:** RapidJSON, nlohmann/json, simdjson, serde_json, encoding/json  
**69 entries:** 29 tier A · 5 tier B · 32 tier C · 3 tier D · 67 copyable, 2 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**simdjson**](simdjson-simdjson.md) | SIMD-accelerated JSON parser with full UTF-8 validation; \~4x faster than RapidJSON, \~25x than nlohmann. | **A** | C++ | Apache-2.0 OR MIT | 🟢 active |
| 2 | [**gjson**](tidwall-gjson.md) | Go library that reads single values from JSON by dot-path without unmarshalling; 3.2-5.7x lower latency than encoding/json structs. | **A** | Go | MIT | 🟢 active |
| 3 | [**cJSON**](davegamble-cjson.md) | Two-file ANSI C DOM JSON parser/printer; parsed 13 of 14 paper benchmark files faster than nlohmann/json (2019). | **A** | C | MIT | 🟢 active |
| 4 | [**Sonic**](bytedance-sonic.md) | ByteDance's JIT- and SIMD-accelerated Go JSON library; about 1.9-3.4x the throughput of encoding/json on amd64. | **A** | Go | Apache-2.0 | 🟢 active |
| 5 | [**jsonparser (buger)**](buger-jsonparser.md) | Zero-allocation, path-based JSON field extractor for Go; 3-6.5x faster than encoding/json struct unmarshal on the project's benchmarks. | **A** | Go | MIT | 🟢 active |
| 6 | [**yyjson**](ibireme-yyjson.md) | ANSI C JSON DOM library beating RapidJSON via single-file design, in-situ parsing, and low-allocation strategy. | **A** | C | MIT | 🟢 active |
| 7 | [**jaq**](01mf02-jaq.md) | Rust reimplementation of the jq language and CLI; faster than jq 1.8.1 on 23 of 30 author filter benchmarks. | **A** | Rust | MIT | 🟢 active |
| 8 | [**Jansson**](akheron-jansson.md) | Dependency-free C library for a mutable, reference-counted JSON tree; stringified 1.35x faster than JsonCpp 1.0.0 in a 2016 independent run. | **A** | C | MIT | 🟢 active |
| 9 | [**json-c**](json-c-json-c.md) | Long-standing reference-counted C JSON DOM; in a 2016 independent run it stringified a parsed canada.json 4x faster than Jansson, losing elsewhere. | **A** | C | MIT | 🟢 active |
| 10 | [**Parson**](kgabis-parson.md) | Two-file C89 JSON DOM with dot-path access; parsed 1.85x faster than JsonCpp 1.0.0 in a 2016 run, mostly on number-heavy canada.json. | **A** | C | MIT | 🟢 active |
| 11 | [**simd-json (Rust)**](simd-lite-simd-json.md) | Rust port of simdjson with serde support; 1.2-2.7x faster DOM parsing than serde_json in json-benchmark. | **A** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 12 | [**json-parser (udp/json-parser)**](udp-json-parser.md) | Two-file, non-recursive C89 DOM parser; parsed 1.5x faster than nlohmann/json 2.0.3 in a 2016 run, entirely on number-heavy input. | **A** | C | BSD-2-Clause | 🟢 active |
| 13 | [**segmentio/encoding (encoding/json replacement)**](segmentio-encoding.md) | Drop-in encoding/json replacement for Go that swaps reflection for unsafe-pointer codecs; \~1.7x marshal, \~5x unmarshal on typed structs. | **A** | Go | MIT | 🟢 active |
| 14 | [**jsoniter-scala**](plokhotnyuk-jsoniter-scala.md) | Scala macro-generated JSON codecs; decoding straight into case classes edged out RapidJSON's DOM (0.147 vs 0.154 s) in kostya/benchmarks. | **A** | Scala | MIT | 🟢 active |
| 15 | [**taoJSON**](taocpp-json.md) | Header-only C++17 JSON/CBOR/MsgPack/UBJSON value-and-events library; beat nlohmann 2.0.3 in a 2016 run, mainly on number-heavy JSON. | **A** | C++ | MIT | 🟢 active |
| 16 | [**Boost.JSON**](boostorg-json.md) | Mutable C++11 JSON DOM with an SSE2-assisted streaming parser; median \~2.6x faster parsing than nlohmann/json, roughly ties RapidJSON. | **A** | C++ | BSL-1.0 | 🟢 active |
| 17 | [**Jsonifier**](nihilai-collective-jsonifier.md) | Header-only C++20 JSON library that binds to registered structs; 1.1-1.8x simdjson ondemand read throughput on most whole documents. | **A** | C++ | MIT | 🟢 active |
| 18 | [**cpp-yyjson**](yosh-matsuda-cpp-yyjson.md) | C++20 JSON DOM library: header-only API over a bundled SIMD-patched yyjson fork; reads 1.4-4.6x, writes 2.6-8.1x faster than RapidJSON. | **A** | C++ | MIT | 🟢 active |
| 19 | [**LJSON**](lengjingzju-json.md) | Pure-C JSON5 DOM/SAX library; its arena/in-situ modes parse up to 2.5x and print \~3x faster than RapidJSON. | **A** | C | MIT | 🟢 active |
| 20 | [**asdf (Mir/D)**](libmir-asdf.md) | D JSON library: parses to compact binary ASDF, binds typed structs; 1.16-1.46x faster than RapidJSON on kostya's JSON test. | **A** | D | BSL-1.0 | 🟢 active |
| 21 | [**simdjson-oxcaml (simdjson-ox)**](artempyanykh-simdjson-oxcaml.md) | Native OxCaml simdjson port: reusable tape mode 1.18x RapidJSON geomean; DOM mode 0.69x RapidJSON, 4.9x Yojson. | **A** | OCaml | MIT | 🟢 active |
| 22 | [**sajson**](chadaustin-sajson.md) | Single-header, in-situ C++11 JSON DOM parser; 1.1-1.8x faster than RapidJSON insitu in the simdjson paper. | **A** | C++ | MIT | 🟡 stale |
| 23 | [**jsmn**](zserge-jsmn.md) | C89 zero-allocation JSON tokenizer; beat nlohmann/json on 8 of 14 benchmark files but trails RapidJSON. | **A** | C | MIT | 🔴 abandoned |
| 24 | [**YAJL**](lloyd-yajl.md) | Tiny ISC-licensed C streaming (SAX) JSON parser and generator; its DOM layer parsed 1.3x faster than json-c in nativejson-benchmark. | **A** | C | ISC | 🔴 abandoned |
| 25 | [**PicoJSON**](kazuho-picojson.md) | Single-header C++03-compatible JSON DOM on std::map/std::vector; stringified 1.09x faster than nlohmann/json 2.0.3 in a 2016 run, parses 1.9x slower. | **A** | C++ | BSD-2-Clause | 🔴 abandoned |
| 26 | [**gason**](vivkin-gason.md) | \~450-line in-situ C++11 JSON DOM parser, 1.2-1.5x faster than default RapidJSON on kostya's number-heavy JSON test. | **A** | C++ | MIT | 🔴 abandoned |
| 27 | [**ujson4c**](esnme-ujson4c.md) | Small C decode-only JSON DOM (UltraJSON decoder plus arena allocator); 4-10% faster than RapidJSON on citm/twitter, slower on canada. | **A** | C | BSD-3-Clause | 🔴 abandoned |
| 28 | [**zzzJSON**](dacez-zzzjson.md) | Single-header C JSON DOM with lazy number parsing and arena allocation; \~1.3x faster parse+stringify than RapidJSON in its own benchmark. | **A** | C | Public Domain (custom… | 🔴 abandoned |
| 29 | [**zenjson**](re-esper-zenjson.md) | Single-header, in-situ C++ JSON DOM parser/serializer in the gason style; parses 1.8-3.6x faster than RapidJSON. | **A** | C++ | MIT | 🔴 abandoned |
| 30 | [**UltraJSON**](ultrajson-ultrajson.md) | Maintenance-only CPython C extension for JSON; up to 2.5x faster than stdlib json on standard fixtures; Python-only. | **B** | C | BSD-3-Clause AND TCL | 🟢 active |
| 31 | [**JSONSki**](automatalab-jsonski.md) | Streaming JSONPath engine that skips irrelevant JSON with bit-parallel fast-forwarding; \~4.8x faster than simdjson parse+query (ASPLOS'22). | **B** | C++ | MIT | 🟡 stale |
| 32 | [**Pison**](automatalab-pison.md) | Multithreaded SIMD structural-index builder and path iterator for single huge JSON records; beats simdjson/RapidJSON end-to-end using 8 threads. | **B** | C++ | MIT | 🟡 stale |
| 33 | [**json_struct**](jorgen-json-struct.md) | Single-header C++11 JSON-to-struct binder; about 2.6x faster roundtrip than nlohmann/json on a third-party M1 benchmark. | **B** | C++ | HPND-sell-variant (study only) | 🟢 active |
| 34 | [**Mison (speculative structural-index JSON parser)**](paper-mison-speculative-structural-index-json-parser.md) | VLDB 2017 JSON parser (no public code) that jumps straight to queried fields; reports 5.5-9.1x over best of RapidJSON/Jackson/Gson. | **B** | C++ | no license (study only) | ⚪ unknown |
| 35 | [**orjson**](ijl-orjson.md) | CPython JSON extension in Rust (yyjson-backed parser) that serializes \~11-14x and parses \~2-6x faster than stdlib json. | **C** | Rust | MPL-2.0 AND (Apache-2.0 OR… | 🟢 active |
| 36 | [**easyjson**](mailru-easyjson.md) | Go codegen tool producing reflection-free struct JSON marshalers; README (2016) shows \~2.8x marshal, \~5.7x unmarshal vs encoding/json. | **C** | Go | MIT | 🟢 active |
| 37 | [**Coost co/json**](idealvin-coost-json.md) | JSON DOM module of the coost C++ base library; first-party numbers claim 1.4-3.6x faster parse/stringify than RapidJSON 1.1.0. | **C** | C++ | MIT | 🟢 active |
| 38 | [**go-json**](goccy-go-json.md) | Import-swap replacement for Go's encoding/json; unmarshalled typed structs \~2x faster than encoding/json in one third-party benchmark. | **C** | Go | MIT | 🟢 active |
| 39 | [**glaze**](stephenberry-glaze.md) | Header-only, C++23 reflection-based JSON (plus BEVE/CBOR/MessagePack/TOML/YAML/CSV) library; beats RapidJSON in first-party benchmarks. | **C** | C++ | MIT | 🟢 active |
| 40 | [**fastjson (valyala)**](valyala-fastjson.md) | Pure-Go schemaless JSON parser/validator with a reusable zero-allocation value tree; \~4-15x faster than encoding/json (2019 numbers). | **C** | Go | MIT | 🟢 active |
| 41 | [**reflect-cpp**](getml-reflect-cpp.md) | C++20 reflection serializer that reads JSON into structs through embedded yyjson; claims \~2x hand-written RapidJSON, \~10x nlohmann/json. | **C** | C++ | MIT | 🟢 active |
| 42 | [**sonic-rs**](cloudwego-sonic-rs.md) | Serde-compatible Rust JSON library using SIMD; about 1.7-2.8x faster than serde_json at typed parsing on x86_64. | **C** | Rust | Apache-2.0 | 🟢 active |
| 43 | [**jsoncons**](danielaparker-jsoncons.md) | Header-only C++ JSON/CBOR/MessagePack/BSON library whose DOM reads \~2x and writes \~2-4x faster than nlohmann/json in the author's benchmark. | **C** | C++ | BSL-1.0 | 🟢 active |
| 44 | [**fastgron**](adamritter-fastgron.md) | C++20 simdjson-based CLI that flattens JSON into greppable gron assignments and back; \~50-80x faster than gron. | **C** | C++ | MIT | 🟢 active |
| 45 | [**jiter**](pydantic-jiter.md) | Rust JSON parser from Pydantic: borrowed-string DOM, pull iterator and Python parser; \~2x serde_json::Value DOM throughput. | **C** | Rust | MIT | 🟢 active |
| 46 | [**libjson (vincenthz)**](vincenthz-libjson.md) | Tiny interruptible SAX-style (callback) JSON parser and printer in C; its suite wins over nlohmann/json come from harness code. | **C** | C | LGPL-2.1-only OR… | 🟢 active |
| 47 | [**NetJSON**](rpgmaker-netjson.md) | C# JSON serializer that emits per-type IL at runtime; \~3.4x faster serialization than Json.NET in a 2014 benchmark. | **C** | C# | MIT | 🟢 active |
| 48 | [**ssrJSON**](antares0982-ssrjson.md) | SIMD C extension replacing CPython's json.dumps/loads; README claims 4-31x faster dumps and 2-8x faster loads. | **C** | C | MIT | 🟢 active |
| 49 | [**metal-json**](brooooooklyn-metal-json.md) | Rust crate that parses JSON to a simdjson-format tape on Apple Silicon GPUs (Metal); beats C++ simdjson above \~4-5 MiB. | **C** | Rust | MIT | 🟢 active |
| 50 | [**JsonFusion**](tucher-jsonfusion.md) | Header-only C++23 reflection-based JSON parser that parses, validates and fills your structs in one pass, beating RapidJSON plus hand-written mapping. | **C** | C++ | MIT | 🟢 active |
| 51 | [**libjson (xnacly)**](xnacly-libjson.md) | Minimal pure-Go JSON parser with dot-path queries; parses about 2x faster than encoding/json into any by mutating input. | **C** | Go | MIT | 🟢 active |
| 52 | [**libJSON (IgnacioPomar)**](ignaciopomar-libjson.md) | Learning-project C++17 JSON DOM (shared_ptr nodes) that parses and walks 1.25-1.42x faster than nlohmann/json in its author's benchmark. | **C** | C++ | Unlicense | 🟢 active |
| 53 | [**simdjson-go**](minio-simdjson-go.md) | Go port of simdjson's SIMD parser for AVX2 amd64; builds a navigable tape 2.3-16.5x faster than encoding/json's interface{} decode. | **C** | Go | Apache-2.0 | 🟡 stale |
| 54 | [**sonnet**](sugawarayuuta-sonnet.md) | Pure-Go rewrite of encoding/json with the same API; decodes typed structs about 4x faster than the stdlib in author benchmarks. | **C** | Go | BSD-3-Clause | 🟡 stale |
| 55 | [**zimdjson**](ezequielramis-zimdjson.md) | Zig port of simdjson with streaming and reflection decoding; its On-Demand parser beats simdjson on 3 of 5 author benchmarks. | **C** | Zig | MIT | 🟡 stale |
| 56 | [**jist**](adelamodwala-jist.md) | Rust CLI that pulls one value by exact key/index path from multi-GB JSON files, far faster than jq. | **C** | Rust | GPL-3.0 | 🟡 stale |
| 57 | [**Tachyon JSON (Rust, TachyonConcepts)**](tachyonconcepts-tachyonjson.md) | Tiny unsafe Rust JSON writer for compile-time-constant objects into a fixed stack buffer; claims 8 ns vs serde_json's 23 ns. | **C** | Rust | MIT | 🟡 stale |
| 58 | [**jsoniter (json-iterator/go)**](json-iterator-go.md) | Pure-Go encoding/json replacement with cached per-type codecs; \~1.8x faster typed-struct Unmarshal than encoding/json. Archived. | **C** | Go | MIT | 🔴 abandoned |
| 59 | [**ffjson**](pquerna-ffjson.md) | Go code generator that emits static per-struct MarshalJSON/UnmarshalJSON methods to replace encoding/json's reflection-based codec. | **C** | Go | Apache-2.0 | 🔴 abandoned |
| 60 | [**pikkr**](pikkr-pikkr.md) | Rust implementation of the Mison speculative JSON field extractor; pulls named fields 2-4x faster than serde_json in its benchmark. | **C** | Rust | MIT | 🔴 abandoned |
| 61 | [**simdjson_nodejs**](luizperes-simdjson-nodejs.md) | Node.js N-API binding to C++ simdjson 0.9; lazyParse beats JSON.parse up to 2.3x by never building JS objects. | **C** | JavaScript | Apache-2.0 | 🔴 abandoned |
| 62 | [**libdart**](target-libdart.md) | C++14 JSON library whose finalized flat binary packets parse 9.2x faster than nlohmann/json and read with zero parsing. | **C** | C++ | Apache-2.0 | 🔴 abandoned |
| 63 | [**metajson (iod::metajson)**](iodcpp-metajson.md) | Header-only C++17 JSON codec for structs with compile-time-known shape; README claims up to 9x nlohmann/json, 2x RapidJSON. | **C** | C++ | MIT | 🔴 abandoned |
| 64 | [**jbson**](chrismanning-jbson.md) | Header-only C++14 JSON-to-BSON parser; author's 2015 runs: 1.46x faster than JsonCpp on canada.json, 9x slower than RapidJSON. | **C** | C++ | BSL-1.0 | 🔴 abandoned |
| 65 | [**libjson (SourceForge)**](sourceforge-net-projects-libjson.md) | Configurable C/C++ JSON DOM library with lazy parsing; about 1.09x faster than JsonCpp in one 2013 MSVC run. | **C** | C++ | BSD-2-Clause | 🔴 abandoned |
| 66 | [**ujson (µjson)**](bitbucket-org-awangk-ujson.md) | Small C++11 UTF-8 JSON DOM library with an re2c scanner; parses about 2x and prints 3.5-4.5x faster than nlohmann/json 2.0.3. | **C** | C++ | MIT | 🔴 abandoned |
| 67 | [**Sonic-Cpp**](bytedance-sonic-cpp.md) | Header-only SIMD JSON DOM parser and serializer for C++ with a RapidJSON-style API, about 2x RapidJSON on nativejson-benchmark files. | **D** | C++ | Apache-2.0 | 🟢 active |
| 68 | [**json.h**](sheredom-json-h.md) | Public-domain single-header C/C++ JSON parser into one read-only allocation; out-parsed nlohmann/json v2.0.3 in a 2016 shootout. | **D** | C | Unlicense | 🟢 active |
| 69 | [**qajson4c**](dehecht-qajson4c.md) | C99 JSON DOM parser building the whole tree in one caller-supplied buffer; claims lower parse memory than RapidJSON (unpublished). | **D** | C | MIT | 🔴 abandoned |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
