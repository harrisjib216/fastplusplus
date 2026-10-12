# Text search and indexing

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md)</sub>

**What these beat:** grep/ripgrep, Lucene, SQLite FTS  
**15 entries:** 3 tier A · 2 tier B · 10 tier C · 0 tier D · 14 copyable, 1 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**Tantivy**](quickwit-oss-tantivy.md) | Embeddable Rust full-text search library, architecturally close to Lucene, ahead on phrase/negated/count-heavy queries. | **A** | Rust | MIT | 🟢 active |
| 2 | [**SeekStorm**](seekstorm-seekstorm.md) | Rust in-process search engine with native lexical and vector indexes; claims sub-millisecond BM25 latency beating Lucene. | **A** | Rust | Apache-2.0 | 🟢 active |
| 3 | [**IResearch (SereneDB)**](serenedb-serenedb.md) | C++ inverted-index search library (ex-ArangoSearch) embedded in SereneDB; claims 5x over Lucene, real gains are 1.0x-1.7x. | **A** | C++ | Apache-2.0 | 🟢 active |
| 4 | [**libpostal**](openvenues-libpostal.md) | C library that parses and normalizes street addresses worldwide with a CRF; about 10-65x faster per address than Deepparse's neural parser. | **B** | C | MIT | 🟢 active |
| 5 | [**ucg (UniversalCodeGrep)**](gvansickle-ucg.md) | Ack-style recursive source-code grep using PCRE2 JIT and threaded traversal; about 3.7x faster than egrep -R on a kernel-tree search. | **B** | C++ | GPL-3.0-only | 🟢 active |
| 6 | [**Manticore Search**](manticoresoftware-manticoresearch.md) | SQL/HTTP full-text and analytics search database, C++ core, positioned as a faster Elasticsearch alternative. | **C** | C++ | GPL-3.0 | 🟢 active |
| 7 | [**Infinity**](infiniflow-infinity.md) | C++ AI-native search database for RAG; vendor run shows 10x Elasticsearch's full-text QPS on 33M Wikipedia documents. | **C** | C++ | Apache-2.0 | 🟢 active |
| 8 | [**ugrep (with ugrep-indexer)**](genivia-ugrep.md) | ugrep-indexer builds Bloom-filter file indexes so ugrep's cold recursive search skips non-matching files, beating ripgrep. | **C** | C++ | BSD-3-Clause | 🟢 active |
| 9 | [**GoAWK**](benhoyt-goawk.md) | POSIX AWK interpreter in Go with CSV mode and embedding API; faster than one-true-awk, slower than gawk and mawk. | **C** | Go | MIT | 🟢 active |
| 10 | [**PISA (Performant Indexes and Search for Academia)**](pisa-engine-pisa.md) | Research-grade in-memory C++ inverted-index search engine; trades blows with Lucene 10.4 on top-k ranked queries, loses on counting. | **C** | C++ | Apache-2.0 | 🟢 active |
| 11 | [**RapidFuzz**](rapidfuzz-rapidfuzz-cpp.md) | Header-only C++ FuzzyWuzzy-style string similarity scorers on bit-parallel LCS/Levenshtein; its Python package runs 13-28x more pairs/s than FuzzyWuzzy. | **C** | C++ | MIT | 🟢 active |
| 12 | [**ngi (N-gram Indexed Regex Search)**](erogol-ngi.md) | CLI that builds a trigram index of a codebase to pre-filter files before ripgrep does the actual regex match. | **C** | Rust | MIT | 🟢 active |
| 13 | [**frg (fastripgrep)**](qhkm-fastripgrep.md) | Rust CLI that indexes a codebase with sparse n-grams to search faster than ripgrep on every tested pattern. | **C** | Rust | MIT | 🟢 active |
| 14 | [**MeTA**](meta-toolkit-meta.md) | C++ text retrieval and analysis toolkit; its ACL 2016 demo paper reports faster indexing than Lucene and Indri and faster linear classification than LIBLINEAR. | **C** | C++ | MIT OR NCSA (repo carries… | 🔴 abandoned |
| 15 | [**trigrep**](pythonicninja-trigrep.md) | Rust CLI that pre-builds a disk-backed trigram index of a repo, then searches only candidate files, beating ripgrep in a first-party benchmark. | **C** | Rust | no license (study only) | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
