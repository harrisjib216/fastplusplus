# Binary schemas

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md)</sub>

**What these beat:** Protobuf, FlatBuffers, Cap'n Proto, MessagePack  
**53 entries:** 16 tier A · 11 tier B · 25 tier C · 1 tier D · 50 copyable, 3 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**rkyv**](rkyv-rkyv.md) | Rust zero-copy serialization crate; faster serialize and in-place reads than Rust FlatBuffers, Cap'n Proto, prost and rmp-serde. | **A** | Rust | MIT | 🟢 active |
| 2 | [**Bebop**](6over3-bebop.md) | Schema-first binary serializer with C#, TypeScript, Rust and C++ codegen; its C# decoder beat Google.Protobuf and MessagePack 4-9x. | **A** | C# | Apache-2.0 | 🟢 active |
| 3 | [**postcard**](jamesmunns-postcard.md) | no_std serde binary format for Rust; serializes \~2x faster than prost/flatbuffers, \~3.6x faster than rmp-serde on log records. | **A** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 4 | [**nanoserde**](not-fl3-nanoserde.md) | Zero-dependency Rust derive serializer whose schemaless binary format encodes \~3.8x and decodes \~1.6x faster than prost on logs. | **A** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 5 | [**bitcode**](softbearstudios-bitcode.md) | Rust-only columnar, bit-packed serializer; on string-heavy logs it encodes 5-14x faster than prost, FlatBuffers, Cap'n Proto, rmp-serde. | **A** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 6 | [**Nino**](jasonxudeveloper-nino.md) | C# source-generated binary serializer for .NET and Unity; beats MessagePack-CSharp and edges MemoryPack on its own microbenchmarks. | **A** | C# | MIT | 🟢 active |
| 7 | [**YaFF (Yet another Flat Format)**](yandex-yaff.md) | Zero-copy wire format for existing .proto schemas. In-place field reads beat Protobuf parse-then-read \~25-50x and FlatBuffers \~2x. | **A** | C++ | Apache-2.0 | 🟢 active |
| 8 | [**wincode**](anza-xyz-wincode.md) | Bincode-1.x-compatible Rust serializer with in-place encoding; serializes 3.5-9.6x faster than the prost, FlatBuffers, capnp and rmp-serde crates on log data. | **A** | Rust | Apache-2.0 | 🟢 active |
| 9 | [**s2s (ziglibs)**](ziglibs-s2s.md) | Single-file Zig binary serializer driven by comptime type reflection; 1.1-2x faster round trips than zig-protobuf in one benchmark. | **A** | Zig | MIT | 🟢 active |
| 10 | [**minicbor**](twittner-minicbor.md) | no_std Rust CBOR codec whose derived encoders serialize 2.6-6.9x faster than rmp-serde (MessagePack); decoding is only on par. | **A** | Rust | BlueOak-1.0.0 | 🟢 active |
| 11 | [**savefile**](avl-savefile.md) | Rust derive-based, versioned binary format for saving structs to disk; serializes 4.7-41x faster than prost. | **A** | Rust | MIT | 🟢 active |
| 12 | [**bilrost**](mumbleskates-bilrost.md) | Rust derive-based, protobuf-like binary encoding (a rewritten prost fork) that encodes and decodes faster than prost. | **A** | Rust | Apache-2.0 | 🟢 active |
| 13 | [**qdf (Quick Data Format)**](alex60217101990-qdf.md) | Go-only schemaless binary format: record batches 29-68% smaller than Protobuf, \~7x faster decode than encoding/json. | **A** | Go | MIT | 🟢 active |
| 14 | [**Quarry**](ip332-quarry.md) | Schema compiler emitting no-heap C99, C++20 and Python BRF codecs; its C decoder beats Protobuf C++ on large/nested payloads. | **A** | C++ | Apache-2.0 | 🟢 active |
| 15 | [**serde-zap**](xangelix-serde-zap.md) | Serde-trait binary serializer for Rust; serializes string-heavy logs \~5.4x faster than prost, \~9.7x faster than rmp-serde. | **A** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 16 | [**libbson**](mongodb-libbson.md) | MongoDB's C library for building and iterating BSON; in one third-party C shootout it round-trips faster than cJSON on 4 of 5 payloads. | **A** | C | Apache-2.0 | 🔴 abandoned |
| 17 | [**Apache Thrift (binary protocol)**](apache-thrift.md) | Apache Thrift's C++ binary protocol: IDL-generated structs, fixed-width encoding; \~2.2x faster than msgpack-c in one round-trip test. | **B** | C++ | Apache-2.0 | 🟢 active |
| 18 | [**cereal**](uscilab-cereal.md) | Header-only C++11 serialization library whose binary archive round-tripped a 17 KB record \~2.2x faster than Protobuf in 2019. | **B** | C++ | BSD-3-Clause | 🟢 active |
| 19 | [**msgp**](tinylib-msgp.md) | Go code generator for MessagePack; about 6-7x lower marshal/unmarshal latency than reflection-based vmihailenco/msgpack on the same wire format. | **B** | Go | MIT | 🟢 active |
| 20 | [**colfer**](pascaldekloe-colfer.md) | Schema-compiled binary format with generated C11, Go, Java and JavaScript code; beats protobuf-go and protobuf C++ 2-3x on small records. | **B** | Go | CC0-1.0 | 🟢 active |
| 21 | [**mus-go**](mus-format-mus-go.md) | Go serialization primitives for the tagless MUS binary format; \~3x faster than protobuf-go on small structs, \~6x in unsafe mode. | **B** | Go | MIT | 🟢 active |
| 22 | [**Boost.Serialization**](boostorg-serialization.md) | Boost's C++ object-graph serializer; its native binary archive round-tripped a \~17 KB record \~1.9x faster than Protobuf. | **B** | C++ | BSL-1.0 | 🟢 active |
| 23 | [**200sc/bebop (Go)**](200sc-bebop.md) | Go code generator and runtime for the Bebop binary format; \~3x faster marshal/unmarshal than protobuf-go on a small struct. | **B** | Go | Apache-2.0 | 🟢 active |
| 24 | [**protostuff**](protostuff-protostuff.md) | Java serializer using a protobuf-style tagged binary format; serializes about 1.4x faster than protobuf-java but deserializes slower. | **B** | Java | Apache-2.0 | 🟡 stale |
| 25 | [**benc**](deneonet-benc.md) | Pure-Go raw binary serializer with optional schema codegen; hand-written benc code runs \~3.5x faster than protobuf-go on small structs. | **B** | Go | MIT | 🟡 stale |
| 26 | [**gencode**](andyleap-gencode.md) | Go code generator for a compact schema-driven binary format; marshals \~2.3x and unmarshals \~2.7x faster than protobuf-go. | **B** | Go | GPL-2.0 | 🔴 abandoned |
| 27 | [**Cornflakes**](deeptir18-cornflakes.md) | Rust research serialization library and kernel-bypass UDP stack that sends large fields zero-copy via NIC scatter-gather, beating Protobuf/FlatBuffers/Cap'n Proto. | **B** | Rust | no license (study only) | 🔴 abandoned |
| 28 | [**MemoryPack**](cysharp-memorypack.md) | C# source-generated binary serializer that copies unmanaged data raw; \~1.7x faster than MessagePack-CSharp on objects, 40x+ on struct arrays. | **C** | C# | MIT | 🟢 active |
| 29 | [**Apache Fory (C++)**](apache-fory.md) | Apache Fory's C++ serializer for plain annotated structs, cross-language binary format; 1.3-11x Protobuf's throughput in its benchmarks. | **C** | C++ | Apache-2.0 | 🟢 active |
| 30 | [**msgspec**](msgspec-msgspec.md) | Python C-extension MessagePack/JSON codec with typed Struct decoding; \~2-2.6x faster round-trip than msgpack-python. | **C** | Python | BSD-3-Clause | 🟢 active |
| 31 | [**Simple Binary Encoding (SBE)**](aeron-io-simple-binary-encoding.md) | Code generator for FIX SBE fixed-layout binary messages; C++ flyweight codecs beat Protobuf \~9x encode, \~7x decode (one small-message test). | **C** | C++ | Apache-2.0 | 🟢 active |
| 32 | [**fbthrift**](facebook-fbthrift.md) | Meta's C++ Thrift serialization and RPC framework; its Binary/Compact protocols encode and decode about 2-3x faster than libprotobuf in Meta's own microbenchmark. | **C** | C++ | Apache-2.0 | 🟢 active |
| 33 | [**Lite³ (lite3)**](fastserial-lite3.md) | Schemaless, JSON-compatible zero-copy C format: a B-tree in one mutable buffer; author runs beat FlatBuffers and simdjson. | **C** | C | MIT | 🟢 active |
| 34 | [**flatcc**](dvidelabs-flatcc.md) | FlatBuffers schema compiler and runtime for pure C. Wire-compatible with Google's flatc, and roughly as fast as its C++ code. | **C** | C | Apache-2.0 | 🟢 active |
| 35 | [**libcbor**](pjk-libcbor.md) | Full RFC 8949 CBOR library in C99; its low-level encoder writes CBOR 1.2x to 1.6x faster than Intel tinycbor in one third-party C shootout. | **C** | C | MIT | 🟢 active |
| 36 | [**Nerdbank.MessagePack**](aarnott-nerdbank-messagepack.md) | NativeAOT-ready .NET MessagePack serializer; \~1.2x faster than MessagePack-CSharp on array-encoded small objects, \~5% slower on maps. | **C** | C# | MIT | 🟢 active |
| 37 | [**JSON BinPack**](sourcemeta-jsonbinpack.md) | JSON Schema-driven binary JSON format; its prototype matched or beat Protobuf, Avro, MessagePack on encoded size across 27 documents. | **C** | C++ | AGPL-3.0-or-later | 🟢 active |
| 38 | [**greenpack**](glycerine-greenpack.md) | Go msgpack2 code generator with versioned, typed field names; \~15% faster writes than gogo/protobuf in author's 2017 benchmark. | **C** | Go | MIT | 🟢 active |
| 39 | [**flatty**](treeform-flatty.md) | Binary serializer for plain Nim types; \~38x faster serialize, \~36x faster deserialize than JSON-based std/marshal. | **C** | Nim | MIT | 🟢 active |
| 40 | [**HyperSerializer**](adam-dot-cohen-hyperserializer.md) | Contract-less .NET binary serializer built on runtime-compiled Span/MemoryMarshal proxies; \~16x faster than protobuf-net and MessagePack-CSharp in its author's benchmark. | **C** | C# | Apache-2.0 | 🟢 active |
| 41 | [**ProtoCache**](peterrk-protocache.md) | Zero-copy flat binary format for Protobuf schemas; reads messages in place \~20x faster than Protobuf parse-and-traverse. | **C** | C++ | BSD-3-Clause | 🟢 active |
| 42 | [**hpp-proto**](huangminghuang-hpp-proto.md) | Wire-compatible C++23 Protobuf implementation; non-owning mode decodes and builds+serializes 1.5-1.9x faster than libprotobuf arenas. | **C** | C++ | MIT | 🟢 active |
| 43 | [**JSBT (@cheprasov/jsbt)**](cheprasov-ts-jsbt.md) | Schemaless JS-to-JS binary serializer that keeps object graphs and deduplicates repeated subtrees; much smaller than Protobuf on repetitive data. | **C** | TypeScript | MIT | 🟢 active |
| 44 | [**fernBuffer**](escartem-fernbuffer.md) | Prototype bit-packed JSON encoder (C API over a C++17 core) that beats MessagePack on size for string- and key-heavy JSON. | **C** | C | MIT | 🟢 active |
| 45 | [**msgspec-serde**](ebrevdo-msgspec-serde.md) | Rust-backed Python FlatBuffers codegen producing msgspec Structs; \~19-22x faster encode, \~11-12x faster decode than official Python FlatBuffers. | **C** | Python | Apache-2.0 | 🟢 active |
| 46 | [**Imprint**](agavra-imprint.md) | Rust row format with a sorted field-offset directory, so records merge or project without decoding; \~4x faster than prost merges. | **C** | Rust | MIT | 🟡 stale |
| 47 | [**xlsx_drone**](damian-m-g-xlsx-drone.md) | Small read-only C11 .xlsx cell reader; through its Ruby FFI binding it read a 600k-cell sheet about 1.9x faster than roo. | **C** | C | MIT | 🟡 stale |
| 48 | [**Microsoft Bond (Compact Binary v1)**](microsoft-bond.md) | Discontinued Microsoft schema-based serializer whose Compact Binary wire format is smaller than FlatBuffers and unpacked Cap'n Proto. | **C** | C++ | MIT | 🔴 abandoned |
| 49 | [**Karmem**](inkeliz-karmem.md) | Zero-copy, schema-compiled binary format for Go/TinyGo and WASM; own benchmark: 5-18x faster than FlatBuffers' Go implementation. | **C** | Go | BSD-3-Clause | 🔴 abandoned |
| 50 | [**ZebraPack**](glycerine-zebrapack.md) | Go code generator for a msgpack2 format with integer field keys; marshals \~1.3-4x faster than Go protobuf libraries | **C** | Go | MIT | 🔴 abandoned |
| 51 | [**psio / pSSZ (successor to fracpack)**](gofractally-psio.md) | C++23 reflection-driven, SSZ-derived binary format with zero-copy views; author benchmarks show faster encode/decode than libprotobuf, capnp, FlatBuffers, msgpack. | **C** | C++ | no license (study only) | 🟢 active |
| 52 | [**MTS-1 (Lightweight Delta-Encoded Telemetry Format)**](paper-mts-1-lightweight-delta-encoded-telemetry-format.md) | Rust per-packet binary telemetry format (MTS-1/MWire) reporting \~5% smaller payloads than MessagePack on synthetic host metrics. | **C** | Rust | CC-BY-4.0 (study only) | ⚪ unknown |
| 53 | [**iguana (struct_pb)**](qicosmos-iguana.md) | Header-only C++17/20 reflection serializer whose struct_pb mode writes protobuf proto3 wire format from plain structs; claims 2.4x/3.4x over protobuf. | **D** | C++ | Apache-2.0 | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
