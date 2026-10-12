# Parsing and text

<sub>[fastpp](../../README.md) › [Catalog](../README.md)</sub>

Regex engines, tokenizers, CSV and markup parsers, Unicode transcoders and text search measured against PCRE2, ICU, grep and their peers.

**102 entries in 7 categories:** 22 tier A · 8 tier B · 66 tier C · 6 tier D

| Category | Entries | A | B | C | D | What they beat |
|---|--:|--:|--:|--:|--:|---|
| [CSV and tabular data](csv-tabular/README.md) | 18 | 4 | 0 | 12 | 2 | pandas read_csv, csv-parser libs the benchmark names |
| [HTML, Markdown and markup](markup-html-markdown/README.md) | 11 | 1 | 2 | 8 | 0 | libxml2, gumbo, cmark, html5ever |
| [Lexers and tokenizers](lexers-tokenizers/README.md) | 11 | 1 | 1 | 8 | 1 | re2c, hand-written baselines the benchmark names |
| [Parser generators and combinators](parser-generators-and-combinators/README.md) | 12 | 4 | 0 | 7 | 1 | Bison/Flex, ANTLR, Boost.Spirit, nom |
| [Regex engines](regex-engines/README.md) | 12 | 2 | 3 | 7 | 0 | PCRE2, RE2, std::regex, Rust regex |
| [Text search and indexing](text-search-and-indexing/README.md) | 15 | 3 | 2 | 10 | 0 | grep/ripgrep, Lucene, SQLite FTS |
| [Unicode and UTF-8](unicode-utf8/README.md) | 23 | 7 | 0 | 14 | 2 | ICU, std::codecvt, simdutf as incumbent-fast |

## Most-adopted tier A picks

Tier A, copyable and actively maintained, ordered by GitHub stars.

| # | Project | What it is | Category | Tier | Language | License | Status |
|--:|---|---|---|:-:|---|---|---|
| 1 | [**utf8_range (SIMD Range-based UTF-8 validator)**](unicode-utf8/protocolbuffers-protobuf.md) | SIMD range-based UTF-8 validator bundled in protobuf; edges out Lemire's SSE/NEON validator, mostly on ARM. | [Unicode and UTF-8](unicode-utf8/README.md) | **A** | C | MIT | 🟢 active |
| 2 | [**Tantivy**](text-search-and-indexing/quickwit-oss-tantivy.md) | Embeddable Rust full-text search library, architecturally close to Lucene, ahead on phrase/negated/count-heavy queries. | [Text search and indexing](text-search-and-indexing/README.md) | **A** | Rust | MIT | 🟢 active |
| 3 | [**lexbor**](markup-html-markdown/lexbor-lexbor.md) | Standards-compliant C99 HTML5/CSS/DOM/URL engine; beats libxml2-based bindings on HTML parsing and CSS selector throughput. | [HTML, Markdown and markup](markup-html-markdown/README.md) | **A** | C | Apache-2.0 | 🟢 active |
| 4 | [**SeekStorm**](text-search-and-indexing/seekstorm-seekstorm.md) | Rust in-process search engine with native lexical and vector indexes; claims sub-millisecond BM25 latency beating Lucene. | [Text search and indexing](text-search-and-indexing/README.md) | **A** | Rust | Apache-2.0 | 🟢 active |
| 5 | [**libpg_query**](parser-generators-and-combinators/pganalyze-libpg-query.md) | PostgreSQL's own Bison parser as a standalone C library; raw parse about 5-7x faster than sqlparser-rs in a rival's harness. | [Parser generators and combinators](parser-generators-and-combinators/README.md) | **A** | C | BSD-3-Clause | 🟢 active |
| 6 | [**Sep**](csv-tabular/nietras-sep.md) | Zero-allocation, SIMD-vectorized .NET CSV/TSV parser built to beat CsvHelper on throughput. | [CSV and tabular data](csv-tabular/README.md) | **A** | C# | MIT | 🟢 active |
| 7 | [**re2c**](parser-generators-and-combinators/skvadrik-re2c.md) | Lexer generator emitting inline jump-based state machines for 12 languages; beats Ragel on real-world grammars, loses on synthetic repetition. | [Parser generators and combinators](parser-generators-and-combinators/README.md) | **A** | C | Public Domain (dedication… | 🟢 active |
| 8 | [**Vince's CSV Parser**](csv-tabular/vincentlaucsb-csv-parser.md) | RFC 4180 C++ CSV reader/writer with mmap, SIMD and speculative parallel parsing; beats fast-cpp-csv-parser and rapidcsv on large-file ETL. | [CSV and tabular data](csv-tabular/README.md) | **A** | C++ | MIT | 🟢 active |
| 9 | [**IResearch (SereneDB)**](text-search-and-indexing/serenedb-serenedb.md) | C++ inverted-index search library (ex-ArangoSearch) embedded in SereneDB; claims 5x over Lucene, real gains are 1.0x-1.7x. | [Text search and indexing](text-search-and-indexing/README.md) | **A** | C++ | Apache-2.0 | 🟢 active |
| 10 | [**simdutf8**](unicode-utf8/rusticstuff-simdutf8.md) | SIMD-accelerated UTF-8 validator for Rust, a drop-in replacement for std::str::from_utf8, up to 23x faster. | [Unicode and UTF-8](unicode-utf8/README.md) | **A** | Rust | MIT OR Apache-2.0 | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
