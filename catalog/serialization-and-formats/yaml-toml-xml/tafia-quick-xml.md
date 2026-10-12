# quick-xml

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [YAML, TOML and XML](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust StAX-style XML pull reader/writer; streams real-world XML 1.84x faster than libxml2 SAX, serializes 1.22x faster than pugixml.

| | |
|---|---|
| **Beats** | libxml2 and pugixml |
| **Claimed result** | bemayer/xml-benchmark, run of 2026-09-01 (the page regenerates monthly). Throughput in MB/s; all ratios derived from page data. Most representative is the real-world DBLP/OSM bucket ('other'): - DOM Parse: quick-xml 715.3 vs pugixml 597.5 (1.2x) and libxml2 49.2 (14.5x) - SAX/Stream: quick-xml 611.8 vs libxml2 331.8 (1.84x) - Serialize: quick-xml 865.7 vs pugixml 707.6 (1.22x) and libxml2 499.1 (1.73x) Synthetic buckets: - DOM Parse 10MB: 3721.3 vs pugixml 1575.1 (2.4x) and libxml2 278.8 (13.3x) - DOM Parse 100MB: 1619.1 vs 923.8 (1.75x) and 161.2 (10.0x) - SAX/Stream 100MB: 1467.9 vs libxml2 822.0 (1.79x) - Serialize 100MB: 1581.9 vs pugixml 1054.0 (1.5x) and libxml2 551.1 (2.87x) quick-xml's 'DOM Parse' row does not build a tree. Its harness runs the same read_event_into loop as its SAX row, so the DOM ratios compare a pull tokenizer against full DOM builders. quick-xml loses in three places. pugixml wins DOM Parse at 1KB (1977.9 vs 659.3; 0.001 vs 0.002 ms, at timer resolution). libxml2 shows higher Serialize throughput at 100KB (20100.9 vs 3748.3) and 1MB (15467.1 vs 2958.3), which is an artifact (see caveats). pugixml wins XPath Query, which quick-xml does not implement here. |
| **Workload** | bemayer/xml-benchmark cross-language shootout (14 libraries, 7 languages). Each library runs in its own Docker container on a GitHub Actions ubuntu-latest runner, and time is the mean of N auto-calibrated iterations. Each synthetic bucket (nominal 1KB-100MB) averages a wide/shallow file and a deep/narrow file. The deep files have 1,706-5,000 nesting levels and heavy indentation, so they are about 5.6 MiB (100KB label), 47.9 MiB (1MB and 10MB labels) and 100 MiB (100MB label). The 'other' bucket averages \~10MB DBLP and OpenStreetMap extracts. Operations: DOM parse, SAX/stream parse, XPath //\*[@id], and serialize. quick-xml's DOM and SAX rows both run a Reader::read_event_into loop that builds no tree and does not touch attributes or unescape text. Its Serialize writes pre-parsed owned events with quick_xml::Writer. |
| **Metric** | throughput |
| **Hardware** | GitHub Actions 'ubuntu-latest' hosted runner (exact CPU model not stated; results refresh monthly via a cron CI job) |
| **Compiler and flags** | quick-xml: benchmarks/quick-xml/Cargo.toml sets [profile.release] opt-level = 3 and lto = true. The Dockerfile builds it with `cargo build --release` in the rust:slim image, so it uses the latest stable rustc at build time. The dependency is quick-xml = "\*", so the crate version is whatever was newest and is not recorded. pugixml (master via CMake FetchContent) and both C++ harnesses are built with Debian bookworm g++ (12.2.0; the suite never prints it) via cmake -DCMAKE_BUILD_TYPE=Release (CMake default -O3 -DNDEBUG), C++17. libxml2 itself is Debian bookworm's prebuilt package (2.9.14+dfsg), not compiled by the suite. |
| **Adoption** | 1,570 GitHub stars; crates.io reports 431.8M total downloads, 117.1M recent downloads and 2,435 reverse dependencies (checked 2026-09-25) |
| **Last commit** | 2026-09-02 |
| **Links** | [repository](https://github.com/tafia/quick-xml) · [benchmark](https://bemayer.github.io/xml-benchmark/) |

## Verdict

bemayer/xml-benchmark, run of 2026-09-01 on a GitHub Actions ubuntu-latest runner (CPU model unstated). quick-xml (version unpinned `*`, likely 0.42.0; stable rustc, LTO) was measured against pugixml master and Debian libxml2 2.9.14, both built with g++ 12.2 at -O3. On the \~10 MB DBLP/OSM bucket its `read_event_into` loop hit 612 MB/s vs libxml2 SAX 332 (1.84x) and serialized at 866 vs pugixml 708 (1.22x). The harness never touches attributes or unescapes text, so its 715 MB/s 'DOM' figure against pugixml's 598 (1.2x) is not a like-for-like tree build.

## Use it when

- Rust code that streams large XML dumps (DBLP/OSM-style, 10-100 MB) and pulls out a subset of fields. On the \~10 MB real-world bucket the event loop ran 612 MB/s vs libxml2 SAX 332 and Expat 228.
- Read-modify-write pipelines that transform a document event by event with `Reader` + `Writer`. Serialize measured 866 MB/s vs pugixml 708 and libxml2 499 on real-world files.
- Memory-bound parsing. Peak RSS was 11.9 MB on the \~10 MB real-world bucket, vs 50.1 MB for pugixml DOM and 187 MB for libxml2 DOM.
- Mapping config or API payloads straight onto Rust structs with the `serialize` (serde) feature, or streaming XML from sockets with `async-tokio`.

## Skip it when

- You need a navigable tree or XPath. quick-xml builds neither, and pugixml wins every XPath Query bucket in the same suite. Its 'DOM Parse' wins are a bare event loop, not a tree.
- C/C++ codebases. There is no C API, so you would need FFI/cxx glue around a Rust crate.
- You need strict conformance: no DTD/schema validation, custom entities must be resolved by hand, and issue #848 lists well-formedness errors the reader does not report (multiple root elements, top-level text; `MissingEndTag` only from `read_to_end`). No W3C conformance suite runs in CI (#749).
- Tiny documents. pugixml beat it on 1 KB DOM parse (1978 vs 659 MB/s, though near timer resolution).
- You need a stable API across years. It is pre-1.0, with four breaking minor lines (0.39-0.42) in 2026 alone, and 0.42 moved the whole API from bytes to `&str` (see issue #782 on release churn).

## How it is fast

The reader is a small state machine (text, reference, markup). It uses `memchr`'s vectorized byte search (`memchr2` for `<`/`&` in text, `memchr3` for `>` and the two quote characters inside tags) to jump between delimiters instead of stepping through bytes one at a time. Events are `Cow<str>` slices of the input or of one caller-reused buffer, so no tree and no per-node allocations are built. `BytesStart` stores only the raw tag and name length, so attributes are split only when you iterate `attributes()`. Entity unescaping and EOL/attribute normalization happen only when you call `xml_content()`/`normalized_value()`, and costly checks such as comment `--` validation are off by default.

## Compared with alternatives

Pick quick-xml when you are in Rust and want a widely used (2,435 reverse dependencies), maintained streaming reader plus writer with serde support. For C++ streaming against libxml2 SAX, SpeedyXml avoids FFI. For C++ DOM trees, LightningXML or Parshred are the pugixml challengers, and simdxml targets XPath-style queries, which quick-xml does not do.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | memchr (required); optional: encoding_rs (`encoding`), serde (`serialize`/`serde-types`), tokio (`async-tokio`), document-features, arbitrary |
| **Minimum toolchain** | Rust 1.86 (edition 2024) for 0.42.0; 0.41.x needs 1.79; 0.39.x and older 1.56 |
| **Platforms** | any Rust target; `#![forbid(unsafe_code)]`, no platform-specific code in the crate itself (SIMD comes via memchr); CI runs Linux and Windows plus an i686 32-bit test subset |
| **Thread safety** | not documented; `Reader`/`Writer` are plain owned structs with no global state, so use one reader per stream/thread |
| **Drop-in for the baseline** | no |

## Gotchas

- 0.42.0 (2026-08-22) validates UTF-8 on every event. Non-UTF-8 input without the `DecodingReader` now returns `Error::Encoding`. The `encoding` feature handles only ASCII-compatible encodings, so UTF-16 needs `DecodingReader` or you get wrong events.
- Pin &gt;= 0.41.0. RUSTSEC-2026-0194 (O(N^2) duplicate-attribute check, 80k attributes about 6 s) and RUSTSEC-2026-0195 (unbounded `NsReader` namespace allocation, OOM demonstrated on Routinator) affect earlier versions.
- `trim_text` has documented bugs. It trims text next to comments/PIs/CDATA that is real content, and it emits empty `Text("")` events (#984). The reader also does no transparent EOL normalization (#1003). Trim or normalize per event instead.
- The serde `overlapped-lists` feature can buffer without bound and go quadratic on hostile input. Set `event_buffer_size` if you enable it.

## Known shortcomings

- In bemayer/xml-benchmark (1-star, unlicensed, no CPU model) quick-xml's 'DOM Parse' builds no tree: it runs the same event loop as its SAX row, so DOM ratios compare a tokenizer against full DOM builders. It loses 1 KB DOM parse to pugixml. Debian libxml2 2.9.14 stops at depth 256 on the deep files, which skews the libxml2 serialize rows. No XPath.
- The benchmark depends on quick-xml '\*', so the measured version is unknown (probably 0.42.0), and it times the buffered copying read_event_into path, not zero-copy read_event. Require &gt;= 0.41.0 for RUSTSEC-2026-0194 (O(N^2) duplicate-attribute check) and RUSTSEC-2026-0195 (unbounded NsReader allocation). Misses some well-formedness errors such as multiple roots (#848), no W3C conformance suite in CI, no line-ending normalization, no DTD or schema validation. Four breaking minor versions in 2026; MSRV 1.86.

## Caveats and trade-offs

Evidence problems:
- The only C/C++ head-to-head is bemayer/xml-benchmark, a small third-party suite (1 star, no license, created 2026-04-06). It is one run a month on a shared CI runner with no CPU model, and the numbers drift between runs.
- quick-xml's 'DOM Parse' row is not a DOM parse. Its harness is the same streaming event loop as its SAX row, with lazy attribute parsing and no text unescaping. Comparing that row with pugixml or libxml2 building a full tree is apples to oranges. The fair comparisons are SAX/Stream against libxml2 SAX, and Serialize.
- The synthetic buckets are dominated by whitespace-heavy deep files, which inflates throughput for every library.

The libxml2 artifact:
- Debian's libxml2 2.9.14 halts at nesting depth 256 without XML_PARSE_HUGE (parser.c xmlParseElementStart calls xmlHaltParser). xmlParseMemory then returns NULL.
- As a result, libxml2's deep-file DOM and SAX timings measure a truncated parse, and its deep-file Serialize dumps a NULL document (a no-op).
- This favors libxml2, so quick-xml's wins over libxml2 are if anything understated. It also explains libxml2's 'wins' in Serialize at 100KB and 1MB.

Other limits:
- pugixml beats quick-xml at 1KB DOM parse (near timer resolution) and owns XPath.
- quick-xml is a Rust crate, so C++ users need FFI.

Written in Rust, so using it from C++ requires FFI/cxx bindings rather than direct linking; primarily an event-based (SAX-like) reader rather than a DOM-first API, though the same benchmark still measured a DOM-parse mode; does not implement XPath querying (pugixml wins that category in the same suite); much of libxml2's loss is tied to its heavier per-node allocation model (peak RSS 933.7 MB vs quick-xml's 106.1 MB at 100MB), so part of the win reflects allocation strategy, not only raw scanning speed.

## Maintenance

Actively maintained (0.42.0 released 2026-08-22, last commit 2026-09-02) and MIT-licensed with about 434M crates.io downloads, but still pre-1.0 with frequent breaking API changes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification B, tier now C.
- **Tier reason:** The page's embedded BENCHMARK_DATA (run of 2026-09-01) has quick-xml, pugixml and libxml2 rows from one harness, and the code is public (bemayer/xml-benchmark benchmarks/quick-xml/src/main.rs, benchmarks/pugixml/bench.cpp, benchmarks/libxml2/bench.cpp). No CPU model is published (only 'ubuntu-latest / GitHub Actions'), so it is not A. The suite is a 1-star repo with no license, created 2026-04-06, so it is not a well-known independent suite and B does not apply. This is C, the same call as batch-08 made for RapidXML on this suite.
- **Verifier notes:** Every figure in the record matches the page's embedded BENCHMARK_DATA. I downgraded B to C because the suite is not well-known and lists no CPU model, the same call as batch-08 (RapidXML) made on this suite. Reading the harness source showed that quick-xml's 'DOM Parse' is its streaming loop. Real-world ratios are smaller (1.2x vs pugixml, 1.84x SAX vs libxml2) than the synthetic ones. RazrFalcon/roxmltree's README (537 stars, Apple M1 Pro) has cargo-bench numbers for quick-xml, but only against roxmltree and xml-rs, with libxml2 in a separate table and no flags, so it adds nothing stronger.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `compared_against_cpp_std_directly`, `workload`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://bemayer.github.io/xml-benchmark/>
  - <https://github.com/bemayer/xml-benchmark>
  - <https://github.com/bemayer/xml-benchmark/blob/main/README.md>
  - <https://github.com/bemayer/xml-benchmark/blob/main/benchmarks/quick-xml/src/main.rs>
  - <https://github.com/bemayer/xml-benchmark/blob/main/benchmarks/quick-xml/Cargo.toml>
  - <https://github.com/bemayer/xml-benchmark/blob/main/benchmarks/quick-xml/Dockerfile>
  - <https://github.com/bemayer/xml-benchmark/blob/main/benchmarks/libxml2/bench.cpp>
  - <https://github.com/bemayer/xml-benchmark/blob/main/benchmarks/libxml2/CMakeLists.txt>
  - <https://github.com/bemayer/xml-benchmark/blob/main/benchmarks/libxml2/Dockerfile>
  - <https://github.com/bemayer/xml-benchmark/blob/main/benchmarks/pugixml/bench.cpp>
  - <https://github.com/bemayer/xml-benchmark/blob/main/benchmarks/pugixml/CMakeLists.txt>
  - <https://github.com/bemayer/xml-benchmark/blob/main/benchmarks/pugixml/Dockerfile>
  - <https://github.com/bemayer/xml-benchmark/blob/main/benchmarks/runner.sh>
  - <https://github.com/bemayer/xml-benchmark/blob/main/.github/workflows/benchmark.yml>
  - <https://github.com/bemayer/xml-benchmark/blob/main/tools/orchestrator.py>
  - <https://github.com/bemayer/xml-benchmark/blob/main/tools/report_generator.py>
  - <https://github.com/bemayer/xml-benchmark/blob/main/tools/common.py>
  - <https://github.com/bemayer/xml-benchmark/blob/main/tools/generate_data.py>
  - <https://github.com/bemayer/xml-benchmark/blob/main/tools/download_data.py>
  - <https://github.com/tafia/quick-xml>
  - <https://github.com/tafia/quick-xml/blob/master/README.md>
  - <https://github.com/tafia/quick-xml/blob/master/Cargo.toml>
  - <https://crates.io/api/v1/crates/quick-xml>
  - <https://crates.io/api/v1/crates/quick-xml/reverse_dependencies?per_page=1>
  - <https://github.com/RazrFalcon/roxmltree>
  - <https://raw.githubusercontent.com/GNOME/libxml2/v2.9.14/parser.c>
  - <https://raw.githubusercontent.com/GNOME/libxml2/v2.9.14/xmlsave.c>
  - <https://packages.debian.org/bookworm/libxml2>
  - <https://packages.debian.org/bookworm/g++>
- **Sources the enricher read:**
  - <https://github.com/tafia/quick-xml>
  - <https://github.com/tafia/quick-xml/blob/master/README.md>
  - <https://github.com/tafia/quick-xml/blob/master/Cargo.toml>
  - <https://github.com/tafia/quick-xml/blob/master/Changelog.md>
  - <https://github.com/tafia/quick-xml/blob/master/src/lib.rs>
  - <https://github.com/tafia/quick-xml/blob/master/src/reader/mod.rs>
  - <https://github.com/tafia/quick-xml/blob/master/src/reader/slice_reader.rs>
  - <https://github.com/tafia/quick-xml/blob/master/src/reader/buffered_reader.rs>
  - <https://github.com/tafia/quick-xml/blob/master/src/reader/state.rs>
  - <https://github.com/tafia/quick-xml/blob/master/src/parser/mod.rs>
  - <https://github.com/tafia/quick-xml/blob/master/src/parser/element.rs>
  - <https://github.com/tafia/quick-xml/blob/master/src/events/mod.rs>
  - <https://github.com/tafia/quick-xml/blob/master/src/events/attributes.rs>
  - <https://github.com/tafia/quick-xml/blob/master/compare/README.md>
  - <https://github.com/tafia/quick-xml/blob/master/examples/README.md>
  - <https://github.com/tafia/quick-xml/blob/master/examples/custom_entities.rs>
  - <https://github.com/tafia/quick-xml/blob/master/.github/workflows/rust.yml>
  - <https://github.com/tafia/quick-xml/issues/848>
  - <https://github.com/tafia/quick-xml/issues/782>
  - <https://github.com/tafia/quick-xml/issues/1003>
  - <https://github.com/tafia/quick-xml/issues/749>
  - <https://github.com/tafia/quick-xml/issues?q=performance>
  - <https://github.com/tafia/quick-xml/issues?q=slow>
  - <https://bemayer.github.io/xml-benchmark/>
  - <https://github.com/bemayer/xml-benchmark/blob/main/benchmarks/quick-xml/src/main.rs>
  - <https://crates.io/api/v1/crates/quick-xml>
  - <https://github.com/rustsec/advisory-db/blob/main/crates/quick-xml/RUSTSEC-2026-0194.md>
  - <https://github.com/rustsec/advisory-db/blob/main/crates/quick-xml/RUSTSEC-2026-0195.md>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/tafia/quick-xml`) · [data/wave4/enrich/raw/github_com_tafia_quick_xml.json](../../../data/wave4/enrich/raw/github_com_tafia_quick_xml.json) (enrichment confidence 0.75)

</details>
