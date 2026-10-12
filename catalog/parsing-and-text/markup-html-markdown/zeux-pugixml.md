# pugixml

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [HTML, Markdown and markup](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> In-place, allocation-light C++ XML DOM parser with XPath 1.0, beating libxml2 on parse throughput.

| | |
|---|---|
| **Beats** | libxml2 |
| **Claimed result** | Faster than libxml2 on all nine test files (derived from page data, benchmark-data.js). On x86: vs libxml2 DOM, 4.5x (house.dae 0.556 vs 2.501) to 23.4x (cathedral.xml); vs libxml2 SAX, 2.7x (house.dae 0.556 vs 1.500) to 19.1x (Russian.sml); e.g. English.sml 0.771 vs 6.412 (DOM, 8.3x) and 3.218 (SAX, 4.2x). x64 is similar: DOM 4.1x-24.1x, SAX 2.6x-19.7x. |
| **Workload** | Parse nine XML test files (1-20MB, including a 10MB XMark file and files with varying markup/content ratios) into a DOM, comparing pugixml against libxml2 (DOM and SAX modes), expat, and several other C/C++ XML parsers, on x86 and x64 builds. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7 @ 2.67 GHz |
| **Compiler and flags** | Microsoft Visual Studio 2015, "with all optimizations on"; exact flags not itemized |
| **Adoption** | 4.65k stars; widely embedded in game engines and other C++ projects needing a lightweight XML+XPath parser |
| **Last commit** | 2026-06-16 |
| **Links** | [repository](https://github.com/zeux/pugixml) · [benchmark](https://pugixml.org/benchmark-data.js) |

## Verdict

On an Intel Core i7 @ 2.67GHz with MSVC 2015 ('all optimizations on'), pugixml parsed nine 1-20MB XML test files (including a 10MB XMark file) into a DOM 4.5x-23.4x faster than libxml2's DOM mode and 2.7x-19.1x faster than libxml2's SAX mode on x86 builds, with similar 4.1x-24.1x / 2.6x-19.7x ratios on x64; the figures come from pugixml.org's benchmark-data.js chart data rather than a public, runnable benchmark harness.

## Use it when

- Parsing well-formed XML (config files, save formats, scene/asset descriptors) in the 1-20MB range where DOM parse throughput matters and libxml2's generality is overhead you don't need
- Embedding in game engines or tools that want a small, dependency-free, MIT-licensed C++ XML library (two source files, or header-only via PUGIXML_HEADER_ONLY)
- Need XPath 1.0 queries and in-place tree editing without pulling in libxml2's full XPath/validation stack
- Memory-constrained targets where compact mode's 2.5x-5x smaller tree is worth a 10-50% parse-time cost
- Codebases spanning C++98 through C++20 that want one parser across that range (move semantics and range-for activate automatically under C++11, string_view under C++17)

## Skip it when

- Need DTD or XML Schema validation, or custom (non-predefined) entity expansion — pugixml explicitly does not do this
- Documents too large to fit fully in memory — pugixml is DOM-only, no incremental/SAX streaming mode
- Want a drop-in libxml2 replacement — the API surface, error model, and node types are different, so this is a rewrite, not a swap
- Need the benchmarked numbers to be independently reproducible: the comparison lives in a chart-rendering script (benchmark-data.js) on pugixml.org, not a runnable harness in the repo or a public benchmark repo under the author's account
- Targeting strict-alignment architectures with very old pugixml versions — a misaligned-access UB bug in UTF-16/32 decoding was reported and fixed (issue #698, closed 2026-04-14); make sure you're on a version at or after that fix

## How it is fast

Node and attribute names/values are pointers into a single large parsed character buffer rather than individually heap-allocated strings; the fastest load path (load_buffer_inplace/_own) parses the caller's buffer directly ('in-situ' parsing), avoiding the extra copy libxml2's DOM path makes. Tree storage uses its own page-based allocator (one big allocation) instead of many small node allocations, and the recursive-descent parser uses lookup-table character classification rather than generic, more DTD/encoding-aware machinery. An optional compact mode trades \~10-50% more CPU time for 2.5x-5x smaller tree memory via relative-offset node/attribute encoding.

## Compared with alternatives

Pick pugixml over roxmltree when the codebase is C++ (roxmltree is Rust) and you need in-tree mutation plus XPath 1.0, not just read-only access; pick it over stb_xml when you need XPath, Unicode encoding conversion, or DOM editing rather than a minimal single-header reader. The HTML-focused siblings (lexbor, html5-parser, MyHTML, selectolax, MarkupEver) target malformed/HTML5 markup, not well-formed XML, so they solve a different problem.

## Integration

| | |
|---|---|
| **Form** | source-drop (src/pugixml.hpp + src/pugixml.cpp, \~2 files); header-only build available via PUGIXML_HEADER_ONLY |
| **Dependencies** | none required; STL usage is optional and can be disabled with PUGIXML_NO_STL |
| **Minimum toolchain** | C++98 minimum; C++11 unlocks move semantics/range-based for; C++17 unlocks std::string_view overloads and optional charconv float formatting (PUGIXML_CHARCONV_FLOAT) |
| **Platforms** | any (portable standard C++, no SIMD/arch-specific code path) |
| **Thread safety** | Free (non-member) functions are safe to call from multiple threads; concurrent read/write is safe as long as each tree is only accessed from one thread at a time; concurrent access to the same tree from multiple threads needs external synchronization; set_memory_management_functions is not thread-safe (per docs/manual.adoc, 'Thread-safety guarantees'). |
| **Drop-in for the baseline** | false — different API (xml_document/xml_node vs libxml2's xmlDoc/xmlNode) and different error-handling model; no compatibility shim |

## Gotchas

- load_buffer_inplace/_own parse by modifying the caller's buffer in place; the buffer must outlive the document tree, and load_buffer_inplace does not take ownership (you must free it yourself)
- The non-inplace load_buffer copies the input into a private buffer first, which costs more time and memory than the inplace variants — use inplace when performance is critical
- No DTD/XML Schema validation and no custom entity resolution; only the five predefined XML entities are expanded, unresolvable references are left as-is
- Whole document must fit in memory — there is no streaming/SAX-style incremental parse mode

## Known shortcomings

- w4-mine-d re-found pugixml (already listed in wave 3 under markup-html-markdown) with bemayer/xml-benchmark numbers: libxml2 DOM parse 5.8x-7.6x on three of five buckets, size labels mismatching real file sizes, parse success unchecked, CPU model unknown. pugixml is also the yaml-toml-xml incumbent baseline.

## Caveats and trade-offs

The pugixml.org benchmark page states the compiler (MSVC 2015, 'all optimizations on') and the CPU (Intel Core i7 @ 2.67 GHz, no exact model), but the benchmark harness source is not public (no benchmark repo under the zeux GitHub account), so it falls short of Tier A. There is no run date, and the current release (1.16) postdates the benchmarked version. benchmark-data.js labels values 'us/byte', but the accompanying MB/s figures (e.g. 0.556 -&gt; 1714 Mb/s) match ns/byte. The unit label is wrong; ratios are unaffected.

In-memory DOM with compact-storage option, full XPath 1.0 support, header-light API; benchmark numbers come from a chart-rendering script (benchmark-data.js) rather than a runnable, versioned benchmark harness in the main repo, so the comparison cannot be independently re-run from the pugixml GitHub repository alone.

## Maintenance

Actively maintained (last commit 2026-06-16, current release 1.16, CI on GitHub Actions/AppVeyor, MIT-licensed, not a fork or archived); small enough (two source files) to vendor directly into a project.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party benchmark page (pugixml.org/benchmark.html + benchmark-data.js). It states the compiler (MSVC 2015 'all optimizations on') and the CPU (Core i7 @ 2.67GHz, no exact model), but the benchmark harness source is not public: there is no benchmark repo among zeux's repos and none in pugixml's tree. That makes it C.
- **Verifier notes:** The record's cited numbers match benchmark-data.js exactly. The two files it cited are the lowest-ratio ones, so the claim was understated, and claimed_speedup is widened to the full range. MIT, 4,651 stars, last commit 2026-06-16, not a fork, not archived.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** bemayer/xml-benchmark (search agent, unverified)
- **Pages the verifier opened:**
  - <https://pugixml.org/benchmark-data.js>
  - <https://pugixml.org/benchmark.html>
  - <https://github.com/zeux/pugixml>
  - <https://github.com/zeux?tab=repositories>
- **Sources the enricher read:**
  - <https://github.com/zeux/pugixml>
  - <https://github.com/zeux/pugixml/blob/master/README.md>
  - <https://github.com/zeux/pugixml/blob/master/readme.txt>
  - <https://github.com/zeux/pugixml/blob/master/src/pugiconfig.hpp>
  - <https://github.com/zeux/pugixml/blob/master/CMakeLists.txt>
  - <https://github.com/zeux/pugixml/blob/master/docs/manual.adoc>
  - <https://github.com/zeux/pugixml/issues?q=performance>
  - <https://pugixml.org/benchmark.html>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/zeux/pugixml`) · [data/wave3/enrich/raw/github_com_zeux_pugixml.json](../../../data/wave3/enrich/raw/github_com_zeux_pugixml.json) (enrichment confidence 0.55)

</details>
