# LightningXML

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [YAML, TOML and XML](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++20 pull deserializer binding XML straight into structs; beats pugixml, RapidXML and libxml2 on every author benchmark.

| | |
|---|---|
| **Beats** | pugixml, RapidXML, libxml2 |
| **Claimed result** | Leads every workload in the README table. Default (non-normalizing, zero-copy) parser: Flat 3.82 GB/s vs pugixml 1.46 GB/s, RapidXML 199 MB/s (parse_default) / 1.58 GB/s (parse_fastest), libxml2 DOM 178 MB/s; Large (10K users) 3.31 GB/s vs pugixml 311 MB/s, RapidXML fast 340 MB/s, libxml2 DOM 60 MB/s; Attributes 1.91 GB/s vs libxml2 DOM 34 MB/s; Comment-heavy 13.22 GB/s vs pugixml 2.87 GB/s. The fully conforming StrictParser still leads, e.g. Flat 2.67 GB/s and Large 2.43 GB/s. |
| **Workload** | Deserializes matching-struct XML payloads across 9 synthetic shapes (flat, deep, attributes, small, large 10K-user, org/nested, tree depth-14, comment-heavy, catalog) into typed C++ records; measures source-bytes-per-second throughput, pinned to one core, median of 15 repetitions. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 7950X3D, Ubuntu 24.04, pinned to one core |
| **Compiler and flags** | Clang 19, -O3/Release |
| **Adoption** | 1 star |
| **Last commit** | 2026-08-14 |
| **Links** | [repository](https://github.com/nemye/LightningXML) · [benchmark](https://github.com/nemye/LightningXML/blob/main/README.md) |

## Verdict

The numbers come from the author's own Google Benchmark harness: AMD Ryzen 9 7950X3D, Ubuntu 24.04, Clang 19 -O3 with LTO on the bench binary, one pinned core, median of 15 runs. Each library fills the same records from the same \~0.1 KB-1 MB synthetic payloads. Per row, the conforming StrictParser beats the fastest competitor (pugixml v1.14, RapidXML from Boost 1.88 with parse_fastest, libxml2 v2.14.6) by 1.13x (Catalog, 1.74 vs 1.54 GB/s) up to \~7x (Large 10K users, 2.43 GB/s vs 340 MB/s), and the zero-copy default parser widens that to 1.6-9.7x. The Large-row gap is an unexplained outlier: pugixml drops from 1.46 GB/s on Flat to 311 MB/s there. No std-library baseline was measured and no independent reproduction exists.

## Use it when

- Loading XML whose shape you know at compile time (configs, feeds, API payloads, XSD-defined formats) into typed C++ records, where 'pugixml parse, then walk the DOM' is the hot spot. On the author's table the default parser runs at 1.7-3.8 GB/s against pugixml's 0.3-1.5 GB/s on the same record-filling task.
- Hot paths where the input buffer outlives the parsed objects, so std::string_view members give zero-copy extraction. Mix in std::string members only where you need owned copies.
- Documents carrying a lot of content you ignore (comments, unmapped subtrees, long text): these are skipped with memchr. The comment-heavy row runs at 13.2 GB/s (8.2 GB/s strict) against pugixml's 2.9 GB/s.
- Projects that already have an XSD: xsdgen emits the structs, enums, std::variant choices and XmlConstraints facet checks (enforced by xmlight::validate()), and the serializer round-trips the same types.
- Small, many-message workloads (the 1-element 'Small' row is \~2 GB/s against pugixml's 0.8 GB/s) where DOM setup costs dominate.

## Skip it when

- You need a DOM, XPath, in-place editing, or to explore XML whose schema you do not know. There is no tree API, so pugixml or libxml2 remain the right tools.
- Input that is not UTF-8 (UTF-16/32 and other declared encodings are rejected), namespace-aware processing (xmlns is never resolved and elements match on local name only), custom DTD entities (anything beyond the five predefined ones is ErrorCode::UndefinedEntity), or real XSD document validation (xs:union, xs:import, xs:any and complexContent restriction are unsupported by xsdgen).
- Untrusted input where you rely on the parser to reject malformed XML. The default Parser skips entity decoding and three well-formedness checks. Even StrictParser only scans unmapped subtrees and DOCTYPE structurally, and no tier validates UTF-8 byte sequences.
- Very large or streamed inputs. The parser takes the whole document as one std::string_view (no chunked or incremental feed is documented), and the published benchmarks use synthetic payloads of roughly 0.1 KB-1 MB that fit in cache.
- Risk-averse production use. The project is single-author, was created in June 2026 and has 1 star with no outside issue reports. CI builds only GCC and Clang on ubuntu-latest, so MSVC, macOS and Windows are untested.

## How it is fast

It never builds a tree. It is a pull parser specialized per target type at compile time. Field names are FNV-1a hashed at compile time. A cyclic 'next expected field' hint table lets schema-ordered documents match each open tag with a compile-time-length memcmp (folded to word compares) and read the value straight into the member. Only a miss falls back to hash lookup, and the name is confirmed after the lookup. By default string members are std::string_view slices of the source buffer, so there is no allocation and no entity decoding. For types with up to 32 attribute fields, attributes are captured in one streamed, typed pass. Comments, CDATA and unmapped subtrees are skipped with libc memchr scans instead of being tokenized. Normalization and strict checks are template policy flags (ParserOptions) that compile away when off. There are no hand-written SIMD intrinsics; the memchr calls are the only vectorized code.

## Compared with alternatives

Pick LightningXML over Parshred, libsimdxml, RapidXml or SpeedyXml when you want XML bound straight into typed C++ structs from a compile-time or XSD-generated mapping, with a matching serializer, rather than a faster general-purpose tree or event stream. Prefer simdxml for XPath-style queries over multi-GB files (its DBLP 5.1 GB runs); LightningXML's benchmarks stop around 1 MB.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (standard library only; the optional xsdgen tool, tests and benchmarks are built with CMake 3.16+ and fetch GTest / Google Benchmark / competitors) |
| **Minimum toolchain** | C++20 (uses concepts, &lt;span&gt;, &lt;format&gt;, &lt;chrono&gt; calendar types). The README says it was tested with Clang 19, and CI builds GCC and Clang on ubuntu-latest. A standard library with std::format is required. |
| **Platforms** | Portable C++ with no intrinsics (uses libc memchr). Only Linux x86-64 (Ubuntu CI, Ryzen 9 7950X3D bench) is exercised; other OS/compilers are not documented. |
| **Thread safety** | Not documented. Inferred from the source: a BasicParser is a stateful, non-copyable, movable cursor over one buffer, and the header has only constexpr/const tables, so use one parser per thread. |
| **Drop-in for the baseline** | no |

## Gotchas

- std::string_view members alias the source buffer and are always raw, under every parser tier: '&amp;' stays literal and line endings are not normalized. Only std::string members receive decoded text under NormalizingParser/StrictParser, and the buffer must outlive every string_view.
- Mixed content: when a comment, CDATA section, PI or unmapped child splits an element's text, a raw string member keeps only the last run. For example, '&lt;desc&gt;Price: &lt;![CDATA[\$5]]&gt; only&lt;/desc&gt;' yields " only". Use a normalizing parser with a std::string member if that matters.
- Namespace prefixes are ignored for matching, so same-local-name elements from different namespaces bind to the same field and '&lt;a:x&gt;...&lt;/b:x&gt;' is accepted. An std::optional attribute with an unparseable value is silently left empty instead of failing the parse.
- Errors are reported as a bool plus parser.errorCode(); the header has no throw statements (container allocation can still throw std::bad_alloc). Nesting is capped at MAX_DEPTH = 256 and attributes per tag at 65,536, and arrField always serializes all N slots of a std::array.

## Known shortcomings

- Not fully conforming despite the README: unmapped subtrees and DOCTYPE are only scanned structurally (end-tag names not matched), UTF-8 is never validated and namespaces are never resolved. Author's own benchmark on small synthetic in-cache payloads (about 0.1 KB-1 MB); the \~7x Large-row lead comes from pugixml and RapidXML slowing sharply there, unexplained. 1 star, Linux-only CI.

## Caveats and trade-offs

Single-project, first-party benchmark (not independent). The headline column is the default parser, which skips entity expansion, normalization and three well-formedness checks, while pugixml (load_buffer with default options) and libxml2 decode, normalize and copy. The StrictParser column is the like-for-like one and still leads, but by less. RapidXML's 199 MB/s Flat figure is parse_default; parse_fastest reaches 1.58 GB/s. The benchmark executable is built with LTO, but FetchContent dependencies (pugixml, libxml2) are not. The author flags the depth-14 Tree row as allocation-bound and high-variance for the DOM competitors. Very new, low-adoption project (1 star, created 2026-06-09).

Zero-copy/non-normalizing default parser trades entity decoding and validation for speed; requires compile-time field-mapping structs rather than a general DOM API; StrictParser tier restores well-formedness checks at reduced speed; C++20 required.

## Maintenance

Actively developed by a single author: v1.0.0 on 2026-07-01, then four releases through v1.3.0 on 2026-08-14, which fixed a long list of correctness and hostile-input issues and added a libFuzzer target. It is MIT-licensed and ships as a single header that is easy to vendor, but it has 1 star, no outside users or issue reports, and Linux-only CI.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** The README Performance table compares against pugixml, RapidXML and libxml2. The benchmark code is public (test/bench_LightningXML.cc, a Google Benchmark harness, with competitor versions pinned in CMakeLists: pugixml v1.14, Boost 1.88 RapidXML, libxml2 v2.14.6), and the compiler (Clang 19), flags (-O3/Release) and CPU (Ryzen 9 7950X3D) are stated. That meets A.
- **Verifier notes:** All numbers cited in the record appear on the README. I added the StrictParser and RapidXML parse_fastest figures so the claim is not read as like-for-like against normalizing parsers. Metadata matches: MIT, 1 star, not a fork, last default-branch commit 2026-08-14 (Release 1.3.0).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/nemye/LightningXML>
  - <https://github.com/nemye/LightningXML/blob/main/README.md>
  - <https://github.com/nemye/LightningXML/blob/main/test/bench_LightningXML.cc>
  - <https://github.com/nemye/LightningXML/blob/main/CMakeLists.txt>
  - <https://github.com/nemye/LightningXML/blob/main/build.sh>
  - <https://github.com/nemye/LightningXML/commits/main>
- **Sources the enricher read:**
  - <https://github.com/nemye/LightningXML>
  - <https://github.com/nemye/LightningXML/blob/main/README.md>
  - <https://github.com/nemye/LightningXML/blob/main/include/LightningXML.hh>
  - <https://github.com/nemye/LightningXML/blob/main/test/bench_LightningXML.cc>
  - <https://github.com/nemye/LightningXML/blob/main/test/test_Conformance.cc>
  - <https://github.com/nemye/LightningXML/blob/main/CMakeLists.txt>
  - <https://github.com/nemye/LightningXML/blob/main/ChangeLog.md>
  - <https://github.com/nemye/LightningXML/blob/main/.github/workflows/build-and-test.yml>
  - <https://github.com/nemye/LightningXML/commits/main>
  - <https://github.com/nemye/LightningXML/issues?q=is%3Aissue>
  - <https://github.com/nemye/LightningXML/releases>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/nemye/lightningxml`) · [data/wave4/enrich/raw/github_com_nemye_lightningxml.json](../../../data/wave4/enrich/raw/github_com_nemye_lightningxml.json) (enrichment confidence 0.8)

</details>
