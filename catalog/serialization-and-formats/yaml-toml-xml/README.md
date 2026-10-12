# YAML, TOML and XML

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md)</sub>

**What these beat:** libyaml, yaml-cpp, toml++, libxml2, pugixml  
**33 entries:** 9 tier A · 2 tier B · 22 tier C · 0 tier D · 32 copyable, 1 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**libfyaml**](pantoniou-libfyaml.md) | Full-spec YAML 1.2/JSON parser and emitter in C, with 3.0-3.6x yaml-cpp's parse throughput in fkYAML's benchmark. | **A** | C | MIT | 🟢 active |
| 2 | [**fkYAML**](fktn-k-fkyaml.md) | Header-only C++11 YAML 1.2 DOM parser/emitter that parses 7.3-7.7x faster than yaml-cpp in the project's benchmark. | **A** | C++ | MIT | 🟢 active |
| 3 | [**toml-spanner**](exrok-toml-spanner.md) | Arena-backed, span-preserving Rust TOML 1.1 library; parses \~9x and parse+deserializes \~3x faster than the `toml` crate. | **A** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 4 | [**noyalib**](sebastienrousseau-noyalib.md) | Pure-Rust, zero-unsafe YAML 1.2 serde library that parses config-sized documents to a Value 1.11-1.36x faster than yaml-rust2. | **A** | Rust | Apache-2.0 OR MIT | 🟢 active |
| 5 | [**chyaml**](jiannanya-chyaml.md) | C++20 YAML 1.2.2 parser/emitter whose 8-byte event tape builds about 2x faster than rapidyaml's arena tree on config-shaped YAML. | **A** | C++ | MIT | 🟢 active |
| 6 | [**LightningXML**](nemye-lightningxml.md) | Header-only C++20 pull deserializer binding XML straight into structs; beats pugixml, RapidXML and libxml2 on every author benchmark. | **A** | C++ | MIT | 🟢 active |
| 7 | [**Parshred**](gregghy-parshred.md) | C++20 SIMD XML parser with a flat 32-byte-node DOM; 1.6-3.3x pugixml's read-only parse throughput on synthetic XML. | **A** | C++ | AGPL-3.0-or-later | 🟢 active |
| 8 | [**yam**](trans-yam.md) | Zero-copy C11 YAML 1.2 event parser and emitter with an SSE4.2 scanner; parses 1.6-13x faster than libyaml. | **A** | C | MIT | 🟢 active |
| 9 | [**yxml**](g-blicky-net-yxml.md) | Tiny (6 KB) malloc-free C streaming XML parser; about 2.2-2.4x faster than a stripped-down libxml2 on large dumps. | **A** | C | MIT | 🔴 abandoned |
| 10 | [**toml++**](marzer-tomlplusplus.md) | Header-only C++17 TOML 1.0 parser and serializer; parses 18x to 430x faster than toml11 v4.2.0 in a third-party matrix. | **B** | C++ | MIT | 🟢 active |
| 11 | [**LibYAML**](yaml-libyaml.md) | Portable C89 YAML 1.1 parser/emitter (the engine under PyYAML's C loaders); about 6-7x yaml-cpp's YAML::Load throughput. | **B** | C | MIT | 🟢 active |
| 12 | [**TinyXML2**](leethomason-tinyxml2.md) | Small zlib-licensed C++ DOM XML parser; about 1.7x faster than MSXML 6.0 in one vendor test, slower than pugixml/RapidXML. | **C** | C++ | Zlib | 🟢 active |
| 13 | [**go-toml v2**](pelletier-go-toml.md) | Pure-Go TOML 1.1 library with an encoding/json-style API; project benchmarks show 2.4-6.4x faster than BurntSushi/toml. | **C** | Go | MIT | 🟢 active |
| 14 | [**libucl**](vstakhov-libucl.md) | C parser and emitter for UCL, an nginx-style JSON superset; README shows it parsing JSON about 2x faster than jansson. | **C** | C | BSD-2-Clause | 🟢 active |
| 15 | [**quick-xml**](tafia-quick-xml.md) | Rust StAX-style XML pull reader/writer; streams real-world XML 1.84x faster than libxml2 SAX, serializes 1.22x faster than pugixml. | **C** | Rust | MIT | 🟢 active |
| 16 | [**Expat**](libexpat-libexpat.md) | Long-lived C99 streaming (SAX-style) XML parser; beats libxml2 only when libxml2 builds a DOM, not against libxml2's own SAX. | **C** | C | MIT | 🟢 active |
| 17 | [**rapidyaml (ryml)**](biojppm-rapidyaml.md) | C++11 YAML 1.2/JSON parser and emitter that builds a zero-copy flat tree; \~25-30x yaml-cpp parse, \~140x emit. | **C** | C++ | MIT | 🟢 active |
| 18 | [**TOMLDecoder**](dduan-tomldecoder.md) | Swift TOML 1.1 parser and Codable decoder. In its author's harness, its lazy parse ran about 5x faster than toml++. | **C** | Swift | MIT | 🟢 active |
| 19 | [**xmloxide**](jonwiggins-xmloxide.md) | Pure-Rust libxml2 reimplementation: parsing at libxml2 parity, self-reported 1.5-2.4x faster serialization and 1.1-2.7x faster XPath. | **C** | Rust | MIT | 🟢 active |
| 20 | [**simdxml**](simdxml-simdxml.md) | Rust SIMD XML parser and XPath 1.0 engine using a flat structural index; beats pugixml on large, attribute-dense files. | **C** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 21 | [**RapidXml**](externpro-rapidxml.md) | Single-header in-situ C++ XML DOM parser from 2009; about 4x libxml2's DOM parse throughput on 10-100 MB inputs. | **C** | C++ | BSL-1.0 OR MIT | 🟢 active |
| 22 | [**libleptris**](leptris-leptris.md) | C11 XML library (DOM, SAX, XPath 1.0, DTD, XSLT, C14N) that beats libxml2 on small-document parse and XPath latency. | **C** | C | BSD-2-Clause | 🟢 active |
| 23 | [**libsimdxml**](krzysztofkowalski-libsimdxml.md) | C++23 port of Rust simdxml: SIMD structural XML indexer with XPath 1.0, claiming 1.04-1.24x pugixml parse throughput. | **C** | C++ | MIT | 🟢 active |
| 24 | [**PipeYAML**](zhaoliangcn-pipeyaml.md) | C++17 YAML parser/emitter with a yaml-cpp-style API; author reports \~10x faster Load, \~5x faster Dump on sub-1 KB configs. | **C** | C++ | MIT | 🟢 active |
| 25 | [**rusty_xml (Remade-With-Rust)**](remade-with-rust-rusty-xml.md) | Pure safe-Rust rewrite of libxml2 (parse, DOM, SAX, XPath, DTD, C14N) whose CLI parses faster than xmllint as shipped. | **C** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 26 | [**SpeedyXml (SpeedyXml-cpp)**](tcshadowwalker-speedyxml-cpp.md) | C++20 streaming SAX-style XML push parser with zero-copy callbacks; author-measured 4.4x faster than libxml2's SAX2 streaming parser. | **C** | C++ | BSD-3-Clause | 🟢 active |
| 27 | [**teptris**](leptris-teptris.md) | C99 TOML parser/emitter with a zero-copy arena DOM; its own benchmarks show 5-8x toml++ parse throughput. | **C** | C | MIT | 🟢 active |
| 28 | [**yeptris**](leptris-yeptris.md) | C11 YAML 1.2 parser, DOM and emitter that parses 2-4x faster than libyaml on medium and large documents. | **C** | C | BSD-2-Clause | 🟢 active |
| 29 | [**zxml**](smallthingz-zxml.md) | Zig DOM/streaming XML parser whose default permissive mode beats pugixml and rapidxml by 1.5-5.4x on real-world files. | **C** | Zig | MIT | 🟢 active |
| 30 | [**VTD-XML**](sourceforge-net-projects-vtd-xml.md) | Java XML parser building a compact offset/length token index, not a tree; beats libxml2 DOM parse, loses XPath. | **C** | Java | GPL-2.0-or-later | 🔴 abandoned |
| 31 | [**TupleMarkup (TML)**](judnich-tuplemarkup.md) | Tiny C parser for TML, a bracket-based nested-list markup format; author claims \~5x libxml2's parse speed on equivalent data. | **C** | C | MIT | 🔴 abandoned |
| 32 | [**frxml**](sharp0802-frxml.md) | Archived zero-copy C++17 XML parser; its old chart shows \~1.8-9x faster than libxml2 DOM but slower than pugixml and RapidXML. | **C** | C++ | MIT | 🔴 abandoned |
| 33 | [**SupXML (sup-xml)**](supsoorg-sup-xml.md) | Source-available Rust XML stack with a libxml2-compatible C ABI; the vendor reports \~2.1x median DOM-parse throughput over libxml2. | **C** | Rust | Proprietary… (study only) | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
