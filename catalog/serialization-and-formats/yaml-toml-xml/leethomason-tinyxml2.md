# TinyXML2

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [YAML, TOML and XML](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Zlib` · 🟢 active

> Small zlib-licensed C++ DOM XML parser; about 1.7x faster than MSXML 6.0 in one vendor test, slower than pugixml/RapidXML.

| | |
|---|---|
| **Beats** | MSXML 6.0 (6.30.18362.418, Microsoft IXMLDOMDocument) |
| **Claimed result** | Raw parse time, TinyXML-2 vs MSXML 6.0: 800 MB 7,424,695 vs 12,940,236 microseconds (about 1.7x faster, derived from page data); 1.5 GB 12,958,705 vs 22,529,768 microseconds (about 1.7x). Load-parse-unload warm: 800 MB 9,278,020 vs 16,457,514 (1.8x), 1.5 GB 16,493,514 vs 29,422,628 (1.8x); cold 1.5 GB 20,971,263 vs 31,736,102 (1.5x). Memory at 800 MB: TinyXML-2 5477.5 MB vs MSXML 3428.5 MB. In the same tables Rapid-XML (1,686,864 microseconds at 800 MB), pugiXml (1,243,289) and mdz_xml (830,137 to 965,468) are all faster than TinyXML-2. The project's own README claims only that TinyXML-2 is 'efficient' and, against TinyXML-1, 'uses less memory, is faster, and uses far fewer memory allocations', with no figures. |
| **Workload** | DOM parse of Wikimedia XML dumps (about 800 MB and about 1.5 GB) on Windows 10, measuring only the Parse() call for TinyXML-2, against MSXML 6.0 used through IXMLDOMDocument; part of a competitor's comparison of its own parser. |
| **Metric** | throughput |
| **Hardware** | Intel i5-6600 @ 3.30GHz (4 cores/4 threads), 16 GB RAM, Windows 10 64-bit |
| **Compiler and flags** | VC++ toolset v100 (64-bit); optimization flags not stated. |
| **Adoption** | 5.8k stars |
| **Last commit** | 2026-05-24 |
| **Links** | [repository](https://github.com/leethomason/tinyxml2) · [benchmark](https://raw.githubusercontent.com/maxdz-gmbh/mdz_xml/HEAD/README.md) |

## Verdict

A competing vendor's README (maxdz mdz_xml) timed a TinyXML-2 snapshot of 23.03.2021 (between tags 8.0.0 and 8.1.0) against MSXML 6.0 on March 2021 Wikidata stub dumps on an Intel i5-6600 under Windows 10 with VC++ toolset v100 x64, optimization flags unstated: TinyXML-2's Parse() took 7.42 s vs 12.94 s at 800 MB and 12.96 s vs 22.53 s at 1.5 GB (about 1.7x), and load-parse-unload was about 1.8x faster warm and 1.5x faster cold (derived from page data). The same tables show TinyXML-2 using about 1.6x MSXML's memory and crashing on the 2.0 GB and 2.7 GB files; no standard-library baseline applies and the project itself publishes no numbers.

## Use it when

- Config files, game assets, level data and service payloads up to tens of MB, where a simple editable DOM and round-trip writing matter more than raw parse throughput.
- Replacing MSXML (Windows-only COM) or TinyXML-1 in portable C++: one .h/.cpp pair, zlib licence, no exceptions, no RTTI, no standard-library containers.
- Parsing untrusted input where you want error line numbers on every node and a built-in nesting limit (TINYXML2_MAX_ELEMENT_DEPTH = 500) that returns XML_ELEMENT_DEPTH_EXCEEDED instead of overflowing the stack.
- Generating XML with XMLPrinter to a FILE\* or memory buffer, with or without a DOM.

## Skip it when

- Throughput-bound parsing: in the same maxdz tables RapidXML is about 4.4x and pugixml about 6.0x faster than TinyXML-2 at 800 MB, and in the siximapala CSV pugixml reads 10 MB in 18-20 ms vs 65-102 ms (derived from page data).
- Multi-GB documents: in the 2021 maxdz tables it used 5477.5 MB for an 800 MB file and 9601.6 MB for 1.5 GB (more than MSXML) and crashed on the 2.0 GB and 2.7 GB dumps that MSXML parsed; use a streaming parser such as Expat or yxml.
- Documents that need DTDs, external entities, XPath, XSLT, schema validation, namespaces or UTF-16 input.
- Concurrent reads of one shared XMLDocument from several threads without a lock: the first read of a string writes into the document buffer.
- Code that needs a stable API or ABI: the README says the major version changes fairly rapidly and API changes are common (the current tag is 11.0.0).

## How it is fast

The whole input is read (LoadFile) or memcpy'd (Parse) into one owned buffer and parsed in place by a recursive-descent parser: StrPair records start/end pointers into that buffer, and entity decoding and newline normalization run lazily and in place only when a string is first read (StrPair::GetStr). Nodes and attributes come from per-type fixed-size free-list pools carved from 4 KB blocks (MemPoolT) rather than one heap allocation per node, and the library uses no standard-library containers. The scanning loops are plain byte-at-a-time code (ctype isspace/isalpha, strncmp against end tags) that also counts line numbers for every node, with no SIMD or lookup tables, which is why pugixml and RapidXML outrun it.

## Compared with alternatives

Pick TinyXML-2 over RapidXml (externpro), LightningXML or zxml when you want an actively patched, easy-to-learn editable DOM with error line numbers and a nesting limit and parse speed is secondary; for throughput use RapidXml or a pugixml-class parser, and for multi-GB files use a streaming parser such as Expat or yxml, since TinyXML-2 was the slowest DOM parser in both third-party tables found and the most memory-hungry in the maxdz one.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (C runtime only); CMake and meson builds and a vcpkg port are provided, and it can be built as a static or shared library |
| **Minimum toolchain** | C++11 in practice (the header uses override unconditionally; the CMake build does not enforce a standard); MSVC, GCC and Clang |
| **Platforms** | any (portable C++, no SIMD or architecture-specific code); 64-bit file sizes through _fseeki64/fseeko since PR #787 (merged 2020-03-10) |
| **Thread safety** | Not documented. There is no locking; separate XMLDocument objects can be used on separate threads (the only mutable global is XMLUtil::SetBoolSerialization, which the header calls 'not thread safe'), but even const reads of one document mutate its buffer (mutable StrPair with lazy GetStr), so a shared document needs external locking. |
| **Drop-in for the baseline** | no |

## Gotchas

- Typed accessors (QueryDoubleText, DoubleAttribute, QueryIntAttribute and friends) go through sscanf and snprintf, so they are slow and depend on the C locale: under a comma-decimal locale a value like 1.5 can read back as 1 (issue #160, open since 2014).
- XMLDocument::Parse(const char\*, size_t) allocates and memcpy's the entire input before parsing, so peak memory is the caller's buffer plus TinyXML-2's copy plus the node pools; LoadFile reads straight into the owned buffer and avoids the duplicate. Assertions (TIXMLASSERT) compile to nothing outside debug builds.
- Each new attribute is checked for duplicates by scanning the element's attribute linked list, so an element with k attributes costs O(k^2) name compares while parsing; Attribute(name) and FirstChildElement(name) are linear scans, and XMLNode::DeepClone recursion is unbounded (issue #839, open).
- Harness notes for the numbers: the maxdz raw-parse column says only Parse() is timed for TinyXML-2, but that call includes allocating and copying the whole input, and the Task-Manager memory figure probably counts both the harness buffer and TinyXML-2's copy, while MSXML's timed scope is unstated, so the 1.7x ratio's bias cannot be signed. The project's own timer in xmltest.cpp prints 'milli-seconds' but on non-MSVC builds divides raw clock() ticks by the loop count without CLOCKS_PER_SEC, so on POSIX the printed figure is microseconds, 1000x too large.

## Known shortcomings

- Only numbers come from the competitor mdz_xml README (2021 TinyXML-2 snapshot, unpublished harness, flags unstated): beats only MSXML 6.0 (1.74x raw parse, 1.78x warm, 1.51x cold) and is the slowest open parser in that table (RapidXML 4.4x, pugixml 6.0x faster), uses more memory than MSXML and crashes on 2.0 GB and 2.7 GB files; the raw-parse timing covers Parse() only.
- Enricher: the maxdz 'Parse()-only' timing includes TinyXML-2's full-input allocation and memcpy and the memory column likely counts the input twice, while the MSXML timed scope is unstated; the project's own xmltest.cpp timer divides raw clock() ticks without CLOCKS_PER_SEC on non-MSVC builds (1000x too large, no published numbers depend on it). sscanf typed accessors are locale-dependent (#160 open); const reads write into the buffer, so a shared document is unsafe across threads; the duplicate-attribute check is O(k^2); CVE-2024-50615 fixed in 10.1.0; May 2026 security fixes (#1067) unreleased after 11.0.0.

## Caveats and trade-offs

Weak evidence of an unusual kind: the numbers come from a competing commercial vendor (maxdz mdz_xml, closed source, evaluation binaries only, benchmark harness not published, optimization flags not stated) whose tables use public Wikimedia dumps from March 2021 and a TinyXML-2 snapshot of 23.03.2021, so they predate several major TinyXML-2 releases. In those tables TinyXML-2 is the slowest of the open parsers (RapidXML about 4.4x and pugiXml about 6.0x faster in raw parse at 800 MB, derived from page data), uses more memory than MSXML (5477.5 vs 3428.5 MB at 800 MB, 9601.6 vs 6095.3 MB at 1.5 GB) and crashes on the 2.0 GB and 2.7 GB files that MSXML parses. In the raw-parse table only the Parse() call is timed for TinyXML-2, while MSXML is driven through IXMLDOMDocument with its timed scope unstated, so the 1.7x raw-parse ratio may flatter TinyXML-2; the load-parse-unload tables (1.8x warm, 1.5x cold) are the fairer comparison. MSXML 6.0 is Windows-only, not libxml2. Other third-party data points go against it: the siximapala/XML-plugins-exhibit README sample CSV (0 stars, hardware and flags unstated, Windows build) has pugixml read 10 MB in 18-20 ms vs TinyXML2 65-102 ms and RapidXML 42-55 ms, and 200 MB in 328-562 ms vs TinyXML2 1226-1272 ms. tinyxml2 issue #52 'Benchmark?' (opened 2012, now closed) asked for a comparison with pugixml and received no numbers. The lead's guessed baseline (libxml2) has no TinyXML-2 numbers anywhere reachable.

Small DOM parser (README: one header and one cpp file) with no dependency on the C++ standard library; UTF-8 only; its README says it was rewritten to suit use in a game (less memory, fewer allocations than TinyXML-1) and that if you need browser-level or more complete XML support 'TinyXML-2 is not the parser for you'. The README notes COLLAPSE_WHITESPACE essentially parses the document twice.

## Maintenance

Actively maintained (latest tag 11.0.0 from March 2025, which includes the CVE-2024-50615 fix from 10.1.0; master gained further GetCharacterRef hardening in #1067 and a destructor speedup in #1075 in May 2026 that are not yet released), and its zlib licence and two-file layout make it trivial to vendor, but the speed evidence is a single unreproducible 2021 vendor table in which it is slower than pugixml and RapidXML.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The only numbers against a recognizable incumbent (MSXML 6.0) come from a competing vendor's README (maxdz mdz_xml) with the CPU (i5-6600) and toolset (VC++ v100 64-bit) stated but no optimization flags and no published harness, so not A; a closed-source competitor's table is not a well-known independent suite, so not B. TinyXML-2's own README has no figures, only 'efficient' and faster than TinyXML-1.
- **Verifier notes:** All numbers in claimed_speedup appear in the mdz_xml README tables and the derived ratios check out (1.74x and 1.74x raw parse, 1.77x and 1.78x warm, 1.51x cold). Shortcomings to record: only faster than MSXML 6.0 (Windows-only) in a competitor's unreproducible 2021 table, slowest of the open parsers there, higher memory than MSXML, crashes on 2.0 GB and 2.7 GB inputs, and unequal timing scope (Parse() only) in the raw-parse table. Metadata confirmed (Zlib, 5.8k stars, not a fork, not archived, last commit 2026-05-24); the libsimdxml exclusion claim in caveats was not re-checked (repo not found in one search), and pugixml.org/benchmark.html, which might include TinyXML-2, is EGRESS_BLOCKED.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** competitor mdz_xml README (verifier); enricher harness reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/maxdz-gmbh/mdz_xml/HEAD/README.md>
  - <https://raw.githubusercontent.com/leethomason/tinyxml2/HEAD/readme.md>
  - <https://raw.githubusercontent.com/leethomason/tinyxml2/HEAD/LICENSE.txt>
  - <https://github.com/leethomason/tinyxml2>
  - <https://github.com/leethomason/tinyxml2/commits>
  - <https://github.com/leethomason/tinyxml2/issues/52>
  - <https://github.com/siximapala/XML-plugins-exhibit>
  - <https://raw.githubusercontent.com/siximapala/XML-plugins-exhibit/HEAD/README.md>
  - <https://github.com/zeux/pugixml/tree/master/docs>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/leethomason/tinyxml2/HEAD/readme.md>
  - <https://raw.githubusercontent.com/leethomason/tinyxml2/HEAD/tinyxml2.h>
  - <https://raw.githubusercontent.com/leethomason/tinyxml2/HEAD/tinyxml2.cpp>
  - <https://raw.githubusercontent.com/leethomason/tinyxml2/HEAD/xmltest.cpp>
  - <https://raw.githubusercontent.com/leethomason/tinyxml2/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/leethomason/tinyxml2/HEAD/meson.build>
  - <https://raw.githubusercontent.com/leethomason/tinyxml2/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/maxdz-gmbh/mdz_xml/HEAD/README.md>
  - <https://raw.githubusercontent.com/siximapala/XML-plugins-exhibit/HEAD/README.md>
  - <https://github.com/leethomason/tinyxml2/releases>
  - <https://github.com/leethomason/tinyxml2/tags>
  - <https://github.com/leethomason/tinyxml2/commits/master>
  - <https://github.com/leethomason/tinyxml2/issues?q=is%3Aissue+performance>
  - <https://github.com/leethomason/tinyxml2/issues?q=is%3Aissue+locale>
  - <https://github.com/leethomason/tinyxml2/issues?q=is%3Aissue+large+file>
  - <https://github.com/leethomason/tinyxml2/issues/749>
  - <https://github.com/leethomason/tinyxml2/issues/786>
  - <https://github.com/leethomason/tinyxml2/issues/872>
  - <https://github.com/leethomason/tinyxml2/issues/997>
  - <https://github.com/leethomason/tinyxml2/issues/1047>
  - <https://github.com/leethomason/tinyxml2/pull/787>
  - <https://github.com/leethomason/tinyxml2/pull/1067>
  - <https://github.com/leethomason/tinyxml2/pull/1075>
  - <https://github.com/bemayer/xml-benchmark>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/leethomason/tinyxml2`) · [data/wave4/enrich/raw/github_com_leethomason_tinyxml2.json](../../../data/wave4/enrich/raw/github_com_leethomason_tinyxml2.json) (enrichment confidence 0.6)

</details>
