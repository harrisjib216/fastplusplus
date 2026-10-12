# RapidXml

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [YAML, TOML and XML](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSL-1.0 OR MIT` · 🟢 active

> Single-header in-situ C++ XML DOM parser from 2009; about 4x libxml2's DOM parse throughput on 10-100 MB inputs.

| | |
|---|---|
| **Beats** | libxml2 |
| **Claimed result** | bemayer/xml-benchmark DOM Parse, run of 2026-09-01 (the page regenerates monthly). RapidXML vs libxml2 throughput: 1084.9 vs 278.8 MB/s in the 10MB bucket (26.93 vs 104.783 ms, \~3.9x, derived from page data); 638.2 vs 161.2 MB/s in the 100MB bucket (163.388 vs 646.685 ms, \~4.0x, derived from page data); 989.0 vs 79.1 MB/s in the 1KB bucket (\~12.5x, derived from page data, but at 0.001 vs 0.013 ms, near timer resolution). libxml2 shows higher throughput in the 100KB bucket (3277.1 vs 2017.2 MB/s) and the 1MB bucket (2265.9 vs 1212.7 MB/s). Those buckets include deep files that libxml2 stops parsing partway through (see caveats). pugixml beats RapidXML in every bucket (e.g. 1575.1 vs 1084.9 MB/s at 10MB). |
| **Workload** | DOM parse (bemayer/xml-benchmark: 14 libraries across 7 languages, 12 with DOM rows). Each bucket averages a synthetic wide/shallow file and a deep/narrow file. Every library runs in its own debian:bookworm-slim Docker container on a GitHub Actions ubuntu-latest runner, with /usr/bin/time capturing RSS and CPU. The 1KB-100MB size labels are only nominal. Because generate_data.py indents every level, the deep files are about 5.6 MiB (100KB label), 47.9 MiB (1MB and 10MB labels) and 100 MiB (100MB label), with 1,706 to 5,000 nesting levels. Only averages across the two shapes are published. |
| **Metric** | throughput |
| **Hardware** | GitHub Actions ubuntu-latest runner, with each library in a debian:bookworm-slim Docker container (CPU model not published) |
| **Compiler and flags** | g++ from the debian:bookworm-slim image (bookworm's g++ is 12.2.0; the suite never prints the version). The Dockerfile runs cmake -DCMAKE_BUILD_TYPE=Release (CMake's default GCC Release flags are -O3 -DNDEBUG), and benchmarks/rapidxml/CMakeLists.txt adds CMAKE_CXX_STANDARD 17 and -fpermissive. RapidXml is the SourceForge rapidxml-1.13.zip. libxml2 is Debian's prebuilt package (bookworm: 2.9.14), built with the same Release setup. |
| **Adoption** | 2 stars on externpro/rapidxml, a CMake-packaged mirror. Upstream RapidXml's SourceForge page showed '3,065 This Week' downloads on 2026-09-25. bemayer/xml-benchmark uses the SourceForge rapidxml-1.13.zip as its RapidXML entry. The verifier did not check the SpeedyXml-cpp mention. |
| **Last commit** | 2026-08-31 |
| **Links** | [repository](https://github.com/externpro/rapidxml) · [benchmark](https://bemayer.github.io/xml-benchmark/) |

## Verdict

In bemayer/xml-benchmark's 2026-09-01 run (Debian bookworm g++ 12.2, CMake Release -O3, a GitHub Actions ubuntu-latest runner with no CPU model given), DOM parsing averaged over a wide and a deep synthetic file ran about 3.9x faster than Debian's libxml2 2.9.14 at the 10 MB bucket (26.9 vs 104.8 ms) and about 4.0x at 100 MB (163.4 vs 646.7 ms); RapidXml's time includes copying the buffer on every iteration. libxml2 wins the 100 KB and 1 MB buckets, probably because it stops at depth 256 on the deep files, and pugixml beat RapidXml in every bucket.

## Use it when

- Trusted, well-formed XML (configs, asset or scene files, data exports) that fits in memory, when you want a DOM and libxml2's parse plus xmlFreeDoc time dominates. The one measured run shows about 3.9-4.0x libxml2 at the 10 MB and 100 MB buckets.
- You can hand the parser a mutable buffer that outlives the document, such as a std::vector&lt;char&gt; with a trailing '\0'. For read-only data, use parse_non_destructive and read lengths with name_size()/value_size().
- You want one dependency-free header instead of linking libxml2: embedded targets, cross-compiles, Windows, or builds without exceptions (define RAPIDXML_NO_EXCEPTIONS and supply parse_error_handler).
- Many small or medium documents where you only need element structure and first-text values: parse_fastest skips data nodes and never writes to the buffer.

## Skip it when

- Untrusted input. Recursion depth is unbounded (parse_element -&gt; parse_node_contents -&gt; parse_node), and Boost.PropertyTree's embedded copy has an open fuzzer report of stack overflow on deep nesting (boostorg/property_tree#130). By default a mismatched closing tag like &lt;a&gt;&lt;/b&gt; is accepted.
- Anything that needs XPath, DTD or schema validation, namespaces, DTD-declared entities, or real UTF-16/UTF-32. The manual says wide-character support is partial, and SourceForge ticket #23 reports wchar_t parsing broken for code points above 255.
- Choosing a DOM parser on speed alone. pugixml beat RapidXml in every bucket of bemayer's run (1575 vs 1085 MB/s at 10 MB) and in SpeedyXml's README (1.00 s vs 1.29 s on 235 MiB). Parshred's README shows the opposite order, so benchmark on your own data.
- Very large files or tight memory. Throughput fell to 638 MB/s at the 100 MB bucket (1085 MB/s at 10 MB), and Parshred's README shows RapidXML falling from about 2.4 GB/s at 16 MB to about 0.9 GB/s at 64-128 MB. The whole input plus DOM must be resident: RSS was 424 MB at the 100 MB bucket, in a harness that also keeps a copy of the input.
- Projects that need a maintained parser. There has been no upstream release since 1.13 (2009), and the SourceForge tracker has open tickets going back to 2009.

## How it is fast

In-situ parsing: node names and values are pointers into the source buffer. Zero terminators, entity expansion and whitespace normalization are written into that buffer in place, so no strings are copied. Nodes and attributes are placement-new'd from a bump-pointer arena (memory_pool: a 64 KB block inside the document, then 64 KB heap blocks) that is freed all at once. Parse flags are a template parameter, so each flag combination compiles to its own parser with the unused branches removed; characters are classified with 256-entry lookup tables in scalar recursive-descent code (no SIMD).

## Compared with alternatives

Choose RapidXml over Parshred (needs C++20, GCC 12+) or SpeedyXml (a streaming push parser with no DOM) when you need a mutable in-memory DOM from one dependency-free header that builds on old or unusual toolchains. Parshred's own README puts it within about 5% of RapidXML up to 16 MB and 1.5-1.8x ahead at 64 MB+, so prefer Parshred for very large files on AVX2 hardware.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none beyond &lt;cassert&gt;, &lt;cstdlib&gt;, &lt;new&gt; and &lt;exception&gt; (or user-supplied equivalents with RAPIDXML_NO_STDLIB); rapidxml_utils.hpp adds &lt;vector&gt;, &lt;string&gt;, &lt;fstream&gt; |
| **Minimum toolchain** | C++98/03. Upstream was tested on VC++ 2003-2008, gcc 3/4 and Comeau 4.3.3; bemayer builds it with Debian bookworm g++ 12.2 in C++17 mode (with -fpermissive for the unpatched print header). externpro's CMakeLists requires CMake 4.3, but you can skip it and copy the header. |
| **Platforms** | any (portable scalar C++, no SIMD or OS calls); externpro publishes packages for Linux amd64/arm64, macOS arm64 and Windows amd64 |
| **Thread safety** | Not documented. The code has no global mutable state (lookup tables are const statics), so separate xml_document instances can run on separate threads; a single document and its pool are unsynchronized. |
| **Drop-in for the baseline** | no |

## Gotchas

- xml_document embeds a 64 KB static pool (RAPIDXML_STATIC_POOL_SIZE), so a document on the stack takes 64 KB+ of stack. Calling parse() again on the same document drops the old nodes but does not free the pool, so call clear() between parses.
- Input must be a mutable, zero-terminated Ch\* that outlives the document, and the default mode writes '\0's and expanded entities into it. parse_non_destructive stops the writes, but then names and values are unterminated and entities stay unexpanded. It still needs a terminating zero, so a raw mmap is not enough.
- It is lax by default. Closing-tag names are checked only with parse_validate_closing_tags. DOCTYPE is skipped, only the five built-in entities and &#...; references are expanded, and unrecognised &lt;!...&gt; constructs are silently dropped.
- Nodes do not own their strings: a name or value you set by hand must outlive the node (use doc.allocate_string()). The SourceForge 1.13 zip's rapidxml_print.hpp does not compile on GCC 4.7+ as shipped (bemayer uses -fpermissive), while externpro's copy carries the forward-declaration fix.

## Caveats and trade-offs

Only evidence is bemayer/xml-benchmark, a small third-party suite (1 star, no license, created 2026-04-06). It benchmarks the SourceForge rapidxml-1.13.zip, not this repo, though the parser code is the same 1.13. Its size buckets are misleading: deep-shape files are 5.6-100 MiB with up to 5,000 nesting levels. libxml2 2.9.14 (Debian bookworm) stops at depth 256 without XML_PARSE_HUGE (parser.c nodePush calls xmlHaltParser). The libxml2 bench calls xmlParseMemory without checking the result, so its deep-file times measure a halted partial parse. This favors libxml2, so the \~3.9-4.0x RapidXml win at 10MB/100MB is if anything conservative. The 'libxml2 faster at 100KB/1MB' result is probably this artifact. Per-shape numbers are not published. The run is a single monthly run on a CI runner with no CPU model. RapidXml loses to pugixml at every size, so cite only libxml2 as the beaten baseline. RapidXml is a non-validating in-situ parser, while libxml2 builds a full DOM. The upstream parser has had no release since 1.13 (header dated 2009; SourceForge last updated 2013-04-26). externpro's recent commits (last 2026-08-31) are CMake/CI packaging only, so 'active' reflects packaging, not parser development.

In-situ, destructive parser (mutates the source buffer); allocates DOM nodes from an internal per-instance pool, which becomes a scaling bottleneck at large file sizes versus newer arena/SoA designs (see libsimdxml and parshred entries, both of which cite this exact weakness); C++03-era single-header code with no active upstream maintainer since the 1.13 release (2009); canonical home is SourceForge (http://rapidxml.sourceforge.net/), this GitHub repo is a maintained third-party host of the original source

## Maintenance

The parser code has not changed since upstream 1.13 (2009; SourceForge last updated 2013), and externpro's 'active' commits are CMake/CI packaging only, but the dual BSL-1.0/MIT single header is small enough to vendor; take externpro's copy for the patched print header.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification B, tier now C.
- **Tier reason:** The benchmark code is public (bemayer/xml-benchmark benchmarks/rapidxml/bench.cpp and benchmarks/libxml2/bench.cpp; Debian bookworm g++, CMake Release, -fpermissive), but no CPU model is published (only 'ubuntu-latest / GitHub Actions'), so it is not A. The suite is a 1-star, unlicensed repo created 2026-04-06, not a well-known independent suite, so it is not B either (same call as earlier small third-party harnesses); C.
- **Verifier notes:** The numbers match the page's embedded BENCHMARK_DATA (gh-pages index.html, run 2026-09-01), but the page updates monthly. I downgraded B to C because the suite is not well-known and no CPU model is given. I also found a methodology flaw in the suite: libxml2 stops at its 256-depth limit on the deep files, which biases the results toward libxml2, not RapidXml. I set maintenance_status to active by the last-commit rule, and set is_fork_of to the SourceForge upstream, following the lrstar precedent.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `compared_against_cpp_std_directly`, `maintenance_status`, `is_fork_of`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://bemayer.github.io/xml-benchmark/>
  - <https://github.com/bemayer/xml-benchmark>
  - <https://github.com/bemayer/xml-benchmark/blob/gh-pages/index.html>
  - <https://github.com/bemayer/xml-benchmark/blob/main/README.md>
  - <https://github.com/bemayer/xml-benchmark/blob/main/benchmarks/rapidxml/bench.cpp>
  - <https://github.com/bemayer/xml-benchmark/blob/main/benchmarks/rapidxml/CMakeLists.txt>
  - <https://github.com/bemayer/xml-benchmark/blob/main/benchmarks/rapidxml/Dockerfile>
  - <https://github.com/bemayer/xml-benchmark/blob/main/benchmarks/libxml2/bench.cpp>
  - <https://github.com/bemayer/xml-benchmark/blob/main/benchmarks/libxml2/CMakeLists.txt>
  - <https://github.com/bemayer/xml-benchmark/blob/main/benchmarks/libxml2/Dockerfile>
  - <https://github.com/bemayer/xml-benchmark/blob/main/benchmarks/pugixml/CMakeLists.txt>
  - <https://github.com/bemayer/xml-benchmark/blob/main/benchmarks/runner.sh>
  - <https://github.com/bemayer/xml-benchmark/blob/main/.github/workflows/benchmark.yml>
  - <https://github.com/bemayer/xml-benchmark/blob/main/tools/orchestrator.py>
  - <https://github.com/bemayer/xml-benchmark/blob/main/tools/report_generator.py>
  - <https://github.com/bemayer/xml-benchmark/blob/main/tools/generate_data.py>
  - <https://github.com/bemayer/xml-benchmark/blob/main/tools/common.py>
  - <https://github.com/bemayer/xml-benchmark/blob/main/tools/download_data.py>
  - <https://github.com/externpro/rapidxml>
  - <https://github.com/externpro/rapidxml/blob/xpro/license.txt>
  - <https://github.com/externpro/rapidxml/blob/xpro/rapidxml.hpp>
  - <https://sourceforge.net/projects/rapidxml/>
  - <https://github.com/GNOME/libxml2/blob/v2.9.14/parser.c>
  - <https://packages.debian.org/bookworm/libxml2>
  - <https://packages.debian.org/bookworm/g++>
- **Sources the enricher read:**
  - <https://github.com/externpro/rapidxml>
  - <https://github.com/externpro/rapidxml/blob/xpro/rapidxml.hpp>
  - <https://github.com/externpro/rapidxml/blob/xpro/rapidxml_utils.hpp>
  - <https://github.com/externpro/rapidxml/blob/xpro/rapidxml_print.hpp>
  - <https://github.com/externpro/rapidxml/blob/xpro/manual.html>
  - <https://github.com/externpro/rapidxml/blob/xpro/CMakeLists.txt>
  - <https://github.com/externpro/rapidxml/blob/xpro/CMakePresetsBase.json>
  - <https://github.com/externpro/rapidxml/blob/xpro/license.txt>
  - <https://github.com/externpro/rapidxml/blob/xpro/.gitmodules>
  - <https://github.com/externpro/rapidxml/blob/xpro/.github/workflows/xpbuild.yml>
  - <https://github.com/externpro/rapidxml/commits/xpro>
  - <https://github.com/externpro/rapidxml/commit/a71cd03a>
  - <https://github.com/externpro/rapidxml/compare/v1.13...xpro>
  - <https://github.com/externpro/rapidxml/releases>
  - <https://sourceforge.net/p/rapidxml/bugs/>
  - <https://sourceforge.net/p/rapidxml/bugs/20/>
  - <https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=rapidxml>
  - <https://bemayer.github.io/xml-benchmark/>
  - <https://github.com/bemayer/xml-benchmark>
  - <https://github.com/bemayer/xml-benchmark/blob/gh-pages/index.html>
  - <https://github.com/bemayer/xml-benchmark/blob/main/benchmarks/rapidxml/bench.cpp>
  - <https://github.com/bemayer/xml-benchmark/blob/main/benchmarks/rapidxml/CMakeLists.txt>
  - <https://github.com/bemayer/xml-benchmark/blob/main/benchmarks/rapidxml/Dockerfile>
  - <https://github.com/bemayer/xml-benchmark/blob/main/benchmarks/libxml2/bench.cpp>
  - <https://github.com/bemayer/xml-benchmark/blob/main/tools/report_generator.py>
  - <https://github.com/bemayer/xml-benchmark/blob/main/tools/common.py>
  - <https://github.com/bemayer/xml-benchmark/blob/main/tools/download_data.py>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp>
  - <https://github.com/gregghy/parshred>
  - <https://github.com/KrzysztofKowalski/libsimdxml>
  - <https://github.com/boostorg/property_tree/issues/130>
  - <https://github.com/svgpp/svgpp/issues/84>
  - <https://github.com/search?q=rapidxml+overflow&type=issues>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/externpro/rapidxml`) · [data/wave4/enrich/raw/github_com_externpro_rapidxml.json](../../../data/wave4/enrich/raw/github_com_externpro_rapidxml.json) (enrichment confidence 0.8)

</details>
