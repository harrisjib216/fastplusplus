# Preprocessors and code generators

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md)</sub>

**What these beat:** cpp, protoc, m4  
**5 entries:** 0 tier A · 1 tier B · 4 tier C · 0 tier D · 5 copyable, 0 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**asp (algebraic, staged parsing)**](yallop-ocaml-asp.md) | Staged, typed OCaml parser combinators (MetaOCaml) that beat ocamlyacc/ocamllex throughput on 4 of 5 grammars. | **B** | OCaml | MIT | 🟡 stale |
| 2 | [**FlatBuffers**](google-flatbuffers.md) | Zero-copy binary serialization with schema-generated accessors; reads fields in place without unpacking, unlike protoc. | **C** | C++ | Apache-2.0 | 🟢 active |
| 3 | [**vtprotobuf (protoc-gen-go-vtproto)**](planetscale-vtprotobuf.md) | protoc plugin generating reflection-free Marshal/Unmarshal/Size/Equal/Clone helpers for Go protobuf APIv2; \~1.7x faster unmarshal than stock protoc-gen-go. | **C** | Go | BSD-3-Clause | 🟢 active |
| 4 | [**Zserio**](ndsev-zserio.md) | Own-IDL C++/Java/Python serialization framework; bit-packed decode 1.2x-2.6x faster than protoc. | **C** | C++ | BSD-3-Clause | 🟢 active |
| 5 | [**RapidProto**](veaac-rapidproto.md) | Header-only codegen protobuf decoder for C++: arena and streaming models beating protoc's Arena decode and protozero. | **C** | C++ | Apache-2.0 | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
