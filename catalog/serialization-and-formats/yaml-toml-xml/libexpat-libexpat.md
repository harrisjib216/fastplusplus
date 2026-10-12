# Expat

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [YAML, TOML and XML](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Long-lived C99 streaming (SAX-style) XML parser; beats libxml2 only when libxml2 builds a DOM, not against libxml2's own SAX.

| | |
|---|---|
| **Beats** | libxml2 (DOM parse; Expat measured in SAX mode) |
| **Claimed result** | 1 MB: Expat (SAX) 11.525 ms, 86.9 MB/s vs libxml2 (DOM) 26.507 ms, 37.8 MB/s (2.3x faster, derived from page data); 10 MB: 121.381 ms, 82.4 MB/s vs 263.196 ms, 38.0 MB/s (2.2x, derived); peak RSS 7.38 vs 24.81 MiB at 1 MB and 25.44 vs 197.37 MiB at 10 MB. Earlier run of the same file, 1 MB: Expat (SAX) 15.495 ms, 64.6 MB/s vs libxml2 (DOM) 35.168 ms, 28.5 MB/s (2.3x, derived). |
| **Workload** | Wall-clock parse (median of 3 repetitions) of a generated synthetic XML file (sample_1mb.xml and sample_10mb.xml; the 1 MB file has 16,824 elements, nesting up to 22, attributes, entities, CDATA, comments and processing instructions), Expat as SAX events versus libxml2 building a DOM tree. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-4850HQ (Haswell, 2013 laptop). The cross-language table (expat 15.495 ms vs libxml2 35.168 ms) ran at the 2.3 GHz base clock with no turbo; the wall/CPU/memory table (11.525 vs 26.507 ms, 121.381 vs 263.196 ms) is the 24.09.2026 run ab_quick_20260924_001320 at about 3.3 GHz (schedutil governor, turbo on, scaling_max_freq 3.5 GHz, load about 2.0 at start). |
| **Adoption** | 1.4k stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/libexpat/libexpat) · [benchmark](https://github.com/KrzysztofKowalski/libsimdxml) |

## Verdict

Third-party run from the README of a competing project (KrzysztofKowalski/libsimdxml; harness not published, Expat and libxml2 versions, compiler and flags unstated) on an Intel i7-4850HQ at about 3.3 GHz with turbo: Expat with SAX callbacks parsed a synthetic 1 MB file in 11.525 ms (86.9 MB/s) vs 26.507 ms (37.8 MB/s) for libxml2 building a DOM, about 2.3x, and the 10 MB file in 121.381 vs 263.196 ms, with peak RSS 7.38 vs 24.81 MiB and 25.44 vs 197.37 MiB. This measures streaming against tree construction, not one parser's speed against the other's; an earlier base-clock run gave 15.495 vs 35.168 ms.

## Use it when

- Streaming large or unbounded XML (feeds, logs, OpenStreetMap-style dumps, network streams) where memory must stay near the buffer size: in libsimdxml's run its peak RSS was 25.44 MiB on a 10 MB file vs 197.37 MiB for libxml2's DOM.
- Parsing untrusted XML in C or C++ where you want a mature, OSS-Fuzz-tested, distro-packaged library with built-in billion-laughs and allocation-amplification limits.
- Push parsing of data that arrives in chunks (sockets, decompression output), filling Expat's own buffer via XML_GetBuffer to avoid an extra copy.
- Replacing a libxml2 DOM parse in code that only walks the document once and throws the tree away.

## Skip it when

- Raw throughput: in the same libsimdxml table pugixml (DOM) ran at 271.1 MB/s vs Expat's 86.9 MB/s at 1 MB, and quick-xml at 195.2 vs 64.6 MB/s in the base-clock table, both about 3x (derived from page data).
- You already use libxml2's SAX or xmlReader API: no like-for-like data shows Expat faster, and bemayer/xml-benchmark has libxml2 SAX ahead even in the groups its depth limit cannot affect (1KB 0.028 vs 0.046 ms; DBLP and OSM extracts 104.8 vs 234.5 ms).
- You need a DOM, XPath, DTD or schema validation, or HTML parsing; Expat does none of these (it does not even check namespace URIs).
- Tiny documents parsed one per parser: per-parser setup dominates, and bemayer's 1KB row has Expat slower than both libxml2 SAX and quick-xml.
- Environments that cannot follow frequent security releases: 2.8.1, 2.8.4, 2.8.5 and 2.9.0 all shipped CVE fixes between May and October 2026.

## How it is fast

The tokenizer is table-driven: each encoding has a 256-entry byte-class table (asciitab.h, utf8tab.h, latin1tab), and xmltok_impl.c is included three times with different macros to stamp out specialised scanners for 8-bit, UTF-16LE and UTF-16BE input. Input is scanned in place with no tree or node allocations; element and attribute names and values are copied into string pools so callbacks get NUL-terminated strings. It is plain scalar C with no SIMD, which is why DOM parsers such as pugixml still beat it on throughput.

## Compared with alternatives

Pick Expat over yxml, quick-xml, pugixml, LightningXML or Parshred when you must stream chunked or very large XML from C or C++ with bounded memory and want a parser developed since 1997 and fuzzed by OSS-Fuzz, with entity handling, namespaces and UTF-8/UTF-16/ISO-8859-1/US-ASCII input; if the document fits in memory and speed matters, pugixml or another DOM sibling is about 3x faster, and yxml is the faster minimal streaming option.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (Autotools or CMake build; CMake FetchContent supported with SOURCE_SUBDIR expat/) |
| **Dependencies** | none beyond the C library (uses getentropy, arc4random or similar entropy sources for the hash salt) |
| **Minimum toolchain** | C99: GCC 4.5+ (GCC 4.8.1+ when used from C++), Clang 3.5+, MSVC 17.0/2022+; the test suite needs C++11 |
| **Platforms** | any; Linux, macOS, Windows (prebuilt win32 binaries), FreeBSD and MinGW in CI |
| **Thread safety** | not documented in doc/reference.html beyond the rule that parsing and cleanup functions must not be called from a handler on the parser that invoked it; use one XML_Parser per thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Open security tracker: the README banner and issue #1160 (open since 2026-03-06) say Expat has unfixed security issues, about 28 non-public reports (DoS loops, NULL dereferences, out-of-bounds access, parser re-entry); releases through 2.9.0 (2026-10-05) keep shipping CVE fixes, so pin to release tags and update promptly.
- DoS protections can reject legitimate input: billion-laughs protection rejects entity amplification above 100x once 8 MiB of output is reached (XML_ERROR_AMPLIFICATION_LIMIT_BREACH), and since 2.7.2 an allocation tracker enforces 100x amplification past a 64 MiB threshold and fails with an out-of-memory error; tune with XML_SetBillionLaughsAttackProtection\* and XML_SetAllocTrackerMaximumAmplification/ActivationThreshold.
- Chunked feeding: XML_Parse returning OK does not mean all input was parsed, tokens split across buffers wait for more data, and since 2.6.0 reparse deferral delays retries of large tokens (XML_SetReparseDeferralEnabled turns it off); XML_Parse copies input, so XML_GetBuffer plus XML_ParseBuffer is the documented fast path. 2.9.0 also removed XML_GetAttributeInfo/XML_ATTR_INFO and XML_MIN_SIZE (now build errors) and deprecated the 32-bit location functions and XML_LARGE_SIZE.
- Harness flaw in the like-for-like counter-evidence: bemayer/xml-benchmark's report_generator.py averages a 'wide' and a 'deep' file under each size label, and generate_data.py's deep files for the 100KB to 100MB labels nest 1,706 to 5,000 levels (5.6 to 100 MiB, not the labelled size). libxml2's parser (parser.c v2.9.14 read; the Dockerfile installs Debian bookworm's package) halts with 'Excessive depth in document: 256' unless XML_PARSE_HUGE is set, which bench.cpp does not set, and neither the Expat nor the libxml2 bench.cpp checks the parse return value. So libxml2's SAX and DOM times in those groups may come from aborted parses; only the 1KB and real-world groups are clean, and they still favour libxml2 SAX.

## Known shortcomings

- Not faster like for like: the only win is Expat SAX against libxml2 DOM in the 0-star libsimdxml README (SAX 11.525 vs libxml2 DOM 26.507 ms; 15.495 vs 35.168 ms), whose harness tmp/benchmark/orchestrator.sh is not public (404), with versions and flags unstated and the two tables run at different clocks (2.3 GHz no turbo vs about 3.3 GHz turbo); bemayer/xml-benchmark has libxml2 SAX ahead of Expat at all 5 sizes (1 MB: 39.606 vs 70.714 ms). Open issue #1160 and about 30 unfixed non-public security reports.
- Enricher: the only win is SAX vs libxml2 DOM in the libsimdxml README. The counter-evidence harness bemayer/xml-benchmark averages wide and deep files per size label; its deep files nest 1,706-5,000 levels and libxml2 2.9.14 halts at depth 256 without XML_PARSE_HUGE while bench.cpp sets no options and checks no return values, so some libxml2 times there come from aborted parses; the clean groups (1KB; DBLP+OSM 104.8 vs 234.5 ms) still favour libxml2 SAX. Issue #1160 open (28 non-public reports); CVE fixes in every release May-Oct 2026.
- Re-found by the wave 4 seed backfill (w4-mine-h) with the 2004 xmlbench sample.results (SAX with no-op handlers: Expat 1.08-1.47x faster than libxml2 SAX, 2.3-3.3x faster than Xerces-C++ SAX; flags and versions unstated), but the 2026 bemayer run has libxml2 faster than Expat at every size, so the SAX-vs-SAX advantage does not hold today; the verified record's 2.2-2.3x compares Expat SAX against libxml2 DOM.

## Caveats and trade-offs

Weak and contested evidence. Expat's own README says only 'Fast streaming XML parser written in C99 with &gt;90% test coverage', with no numbers. The figures come from the README of a competing 2026 project (KrzysztofKowalski/libsimdxml, 0 stars, 18 commits, a C++23 port of the Rust simdxml) that lists expat and libxml2 only as references. The harness is not public: the README's tmp/benchmark/orchestrator.sh and tools/rss_sampler.py are not in the repository. Expat and libxml2 versions, compiler and flags are not stated. The two libsimdxml tables were taken at different clocks (2.3 GHz base without turbo for the 15.495/35.168 ms cross-language table; about 3.3 GHz with turbo for the 11.525/26.507 and 121.381/263.196 ms wall/CPU/memory table), so ratios hold only within a table. The compared modes differ (Expat streaming SAX events vs libxml2 building a full DOM tree, which also explains the 25.44 vs 197.37 MiB peak RSS at 10 MB), so this is not like-for-like; the win belongs to streaming, not to the parser. Like-for-like data points the other way: bemayer/xml-benchmark (report/index.html committed, run dated 2026-04-06T17:17:26Z, runner 'local', hardware, compiler and versions not stated, Docker images with latest versions) has libxml2 SAX/Stream faster than Expat at every size: 1KB 0.028 vs 0.046 ms, 100KB 2.104 vs 10.178 ms, 1MB 39.606 vs 70.714 ms, 10MB 110.529 vs 145.468 ms, 100MB 592.34 vs 933.022 ms, and 104.826 vs 234.468 ms in a group labelled 'other' (that report's time and throughput columns imply input sizes other than the group labels, e.g. the '1MB' group works out to about 24 MB, so its labels are unreliable, but each within-group comparison favours libxml2). Search snippets of older posts (pages not opened, snippet only) disagree: a 2011 OSM-dev post has Expat about 10% faster than libxml2 on OSM data, a 2006 GNOME xml-list post has libxml2 about 30% faster on most test data, and an OpenOffice wiki page calls libxml2 SAX the fastest. Security: the libexpat repo shows a caution banner 'Expat has unfixed security issues' pointing to issue #1160 (open since 2026-03-06), which tracks about 30 non-public reports (DoS loops, NULL function-pointer dereferences, out-of-bounds access, UTF-16 surrogate validation).

Non-validating, stream-oriented push parser in C with no tree, so memory stays near input size (7.38 MiB peak at 1 MB in the table above) but the caller must build any document structure; libxml2 additionally offers DOM, validation, XPath and HTML parsing.

## Maintenance

Actively maintained (release 2.9.0 on 2026-10-05, maintainer funded by Munich's Open Source Sabbatical from 2026-08-01 for up to six months), MIT-licensed and in every major distro, but issue #1160 lists unfixed non-public security reports; the only speed win on record is SAX vs libxml2's DOM, and the bemayer like-for-like comparison mixes in deep files where libxml2 may abort at depth 256.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The libsimdxml README does show expat (SAX) and libxml2 (DOM) rows with exactly the claimed numbers, but it is a 0-star competitor's README: the harness (tmp/benchmark/orchestrator.sh) is not in the repository (404 on raw.githubusercontent.com, no tmp/ directory), the expat and libxml2 versions, compiler and flags are unstated, and the modes differ (SAX vs DOM). That is third-party numbers with partial methodology and no public code, so C, not A or B.
- **Verifier notes:** Record is accurate: the claimed numbers match the libsimdxml README rows exactly, and license MIT (expat/COPYING), 1.4k stars (555 forks), last commit 2026-10-06 and active status all check out. Shortcomings to record: not faster than libxml2 in a like-for-like SAX comparison (bemayer/xml-benchmark has libxml2 SAX ahead at all five sizes), the only win is Expat SAX vs libxml2 DOM from a 0-star competitor's README whose harness is not public, and the two quoted tables ran at different clocks (hardware corrected). Also record the open issue #1160 (about 30 unfixed non-public security reports).
- **Fields the verifier corrected:** `hardware`, `caveats`
- **Shortcomings recorded by:** SAX-vs-SAX comparison with a public harness; enricher harness reading; backfill w4-mine-h
- **Pages the verifier opened:**
  - <https://github.com/KrzysztofKowalski/libsimdxml>
  - <https://raw.githubusercontent.com/KrzysztofKowalski/libsimdxml/HEAD/README.md>
  - <https://raw.githubusercontent.com/KrzysztofKowalski/libsimdxml/HEAD/.gitignore>
  - <https://raw.githubusercontent.com/KrzysztofKowalski/libsimdxml/HEAD/tmp/benchmark/orchestrator.sh>
  - <https://github.com/libexpat/libexpat>
  - <https://github.com/libexpat/libexpat/commits/master>
  - <https://raw.githubusercontent.com/libexpat/libexpat/HEAD/expat/README.md>
  - <https://raw.githubusercontent.com/libexpat/libexpat/HEAD/expat/COPYING>
  - <https://github.com/libexpat/libexpat/issues/1160>
  - <https://github.com/bemayer/xml-benchmark>
  - <https://raw.githubusercontent.com/bemayer/xml-benchmark/HEAD/report/index.html>
- **Sources the enricher read:**
  - <https://github.com/libexpat/libexpat>
  - <https://github.com/libexpat/libexpat/issues/1160>
  - <https://raw.githubusercontent.com/libexpat/libexpat/HEAD/expat/README.md>
  - <https://raw.githubusercontent.com/libexpat/libexpat/HEAD/expat/Changes>
  - <https://raw.githubusercontent.com/libexpat/libexpat/HEAD/expat/doc/reference.html>
  - <https://raw.githubusercontent.com/libexpat/libexpat/HEAD/expat/lib/xmltok.c>
  - <https://raw.githubusercontent.com/libexpat/libexpat/HEAD/expat/lib/xmltok_impl.c>
  - <https://raw.githubusercontent.com/libexpat/libexpat/HEAD/expat/lib/xmlparse.c>
  - <https://raw.githubusercontent.com/KrzysztofKowalski/libsimdxml/HEAD/README.md>
  - <https://raw.githubusercontent.com/bemayer/xml-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/bemayer/xml-benchmark/HEAD/report/index.html>
  - <https://github.com/bemayer/xml-benchmark/tree/main/benchmarks>
  - <https://github.com/bemayer/xml-benchmark/tree/main/benchmarks/expat>
  - <https://github.com/bemayer/xml-benchmark/tree/main/benchmarks/libxml2>
  - <https://raw.githubusercontent.com/bemayer/xml-benchmark/HEAD/benchmarks/expat/bench.cpp>
  - <https://raw.githubusercontent.com/bemayer/xml-benchmark/HEAD/benchmarks/expat/Dockerfile>
  - <https://raw.githubusercontent.com/bemayer/xml-benchmark/HEAD/benchmarks/expat/CMakeLists.txt>
  - <https://raw.githubusercontent.com/bemayer/xml-benchmark/HEAD/benchmarks/libxml2/bench.cpp>
  - <https://raw.githubusercontent.com/bemayer/xml-benchmark/HEAD/benchmarks/libxml2/Dockerfile>
  - <https://raw.githubusercontent.com/bemayer/xml-benchmark/HEAD/benchmarks/libxml2/CMakeLists.txt>
  - <https://raw.githubusercontent.com/bemayer/xml-benchmark/HEAD/benchmarks/runner.sh>
  - <https://raw.githubusercontent.com/bemayer/xml-benchmark/HEAD/tools/generate_data.py>
  - <https://raw.githubusercontent.com/bemayer/xml-benchmark/HEAD/tools/download_data.py>
  - <https://raw.githubusercontent.com/bemayer/xml-benchmark/HEAD/tools/common.py>
  - <https://raw.githubusercontent.com/bemayer/xml-benchmark/HEAD/tools/report_generator.py>
  - <https://raw.githubusercontent.com/bemayer/xml-benchmark/HEAD/results/results.jsonl>
  - <https://raw.githubusercontent.com/GNOME/libxml2/v2.9.14/parser.c>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/libexpat/libexpat`) · [data/wave4/enrich/raw/github_com_libexpat_libexpat.json](../../../data/wave4/enrich/raw/github_com_libexpat_libexpat.json) (enrichment confidence 0.65)

</details>
