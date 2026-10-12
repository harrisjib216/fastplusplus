# frxml

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [YAML, TOML and XML](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Archived zero-copy C++17 XML parser; its old chart shows \~1.8-9x faster than libxml2 DOM but slower than pugixml and RapidXML.

| | |
|---|---|
| **Beats** | libxml2 |
| **Claimed result** | Chart plots parse time relative to frxml (lower = faster), values read from log-scale Figure_1.png: libxml2 is \~1.8-9x slower than frxml (largest at the smallest inputs) and tinyxml2 \~2.6-5x slower. pugixml (\~0.8-0.9x, dipping to \~0.4x at \~260-290 KiB) and RapidXML (\~0.8-0.95x, \~0.4x at \~260-290 KiB) are FASTER than frxml at nearly all sizes. Memory: frxml allocates less than pugixml, tinyxml2 and libxml2 throughout, but RapidXML allocates less than frxml below \~45 KiB. |
| **Workload** | Parses randomly generated XML documents: pugixml-built trees of 50-1000 nodes with random 5-char element names and one attribute each, max depth 300, about 0-330 KiB. Timed with google/benchmark at 3 iterations per size against pugixml, RapidXML, tinyxml2 and libxml2 (DOM parse). Legacy Oct-2024 harness test/src/main.cxx at commit 06b3b12; allocated bytes counted by wrapping malloc. |
| **Metric** | throughput |
| **Compiler and flags** | Compiler unstated; frxml library built with -O3 -march=native (frxml/CMakeLists.txt at commit 06b3b12); pugixml, tinyxml2 and libxml2 come from system packages via find_package, flags unknown |
| **Adoption** | 1 star |
| **Last commit** | 2025-09-02 |
| **Links** | [repository](https://github.com/Sharp0802/frxml) · [benchmark](https://github.com/Sharp0802/frxml/blob/master/docs/Figure_1.png) |

## Verdict

The only evidence is a first-party chart (docs/Figure_1.png, Oct 2024) of the now-deleted frxml::doc DOM. It was run on pugixml-generated documents of 50-1000 elements with one attribute each and no text (about 0-330 KiB), with 3 google/benchmark iterations per size. Relative to frxml, libxml2's xmlReadMemory DOM took \~3.5x as long mid-range (\~9x at the smallest sizes, \~1.8x at 260-290 KiB) and tinyxml2 \~2.6-5x, while pugixml (\~0.8-0.9x) and RapidXML beat it at nearly every size. At 260-290 KiB every competitor's ratio drops at once, so frxml itself slowed \~2x in that band. frxml was built with -O3 -march=native, against distro-packaged competitors with unknown flags, and no compiler or CPU is stated. The harness's `if (!doc)` check can never fire because operator! tests an offset that is always &gt;= 0. The legacy parser rejected character data outright (text between tags returns E_NO_BEGIN). By my reading, its tree index also left child elements out of each element's subtree size. So it did far less work than libxml2, and the result says nothing about XML that contains text.

## Use it when

- Machine-generated XML you control (elements, attributes, comments, PIs, plain text) where you only need to tokenize it once, and libxml2's full DOM, dictionary and well-formedness checks cost more than you need
- Allocation-free or arena-style code: parse&lt;callback&gt; never allocates, so you decide whether to keep records, copy them into your own buffer, or drop them
- Small documents where libxml2 setup cost dominates: the 2024 chart shows the widest gap over libxml2 (\~5-9x) below \~20 KiB, though that was the deleted frxml::doc API
- Vendoring a tiny MIT-licensed tokenizer (four headers, \~14 KB, no dependencies) that you will read, fix and extend yourself

## Skip it when

- Any case where speed is the goal and pugixml or RapidXML is an option: both were faster than frxml in its own chart (\~0.8-0.9x its time, \~0.4x at 260-290 KiB)
- Real-world XML with DOCTYPE/ENTITY declarations, entities (&lt; and &#x20; stay raw), namespaces, CDATA (mis-detected, see gotchas), or whitespace around '=' in attributes (a = "x" fails with EXPECTED_QUOTE)
- Untrusted or possibly malformed input: the 2025 parser does not check that end tags match (its comment says 'validation is for validator, not parser'), and the repo has no unit tests, fuzzing or CI, only a benchmark
- Projects that need a maintained dependency: the repo is archived, has 1 star and no releases or tags, and its README usage example calls the deleted frxml::doc API
- MSVC builds: the delimiter literals rely on a GNU string-literal operator template extension

## How it is fast

It makes a single zero-copy pass that does very little per byte: names, attribute values and text come back as std::string_view slices of the input, with no entity decoding, no DTD or namespace handling, and (in the 2025 code) no end-tag matching. Delimiters are compile-time char packs (a GNU string-literal operator template plus fold expressions) and the callback is a non-type template parameter, so the scalar byte-at-a-time scan loops and the per-node dispatch inline completely; there is no SIMD, SWAR or memchr. The benchmarked 2024 code appended every node in pre-order to one geometrically growing std::vector of std::variant, where libxml2 and tinyxml2 allocate per node, which is also why it allocated less memory in the chart.

## Compared with alternatives

Almost never for speed. Catalogued siblings that beat libxml2 by more are RapidXml (externpro), which was also faster than frxml in frxml's own chart, and LightningXML, which also leads pugixml and RapidXML. Pick frxml only if you want a \~14 KB, allocation-free event tokenizer to vendor and extend yourself for machine-generated XML.

## Integration

| | |
|---|---|
| **Form** | header-only (CMake INTERFACE target frxml; include frxml/frxml.h). The benchmarked 2024 version was a shared library. |
| **Dependencies** | none; google/benchmark, pugixml and tinyxml2 are git submodules used only by the benchmark |
| **Minimum toolchain** | C++17 plus the GNU string-literal operator template extension (the code suppresses -Wgnu-string-literal-operator-template), so GCC or Clang in practice; CMake 3.27 for the repo build; compiler versions not documented |
| **Platforms** | not documented; portable scalar code with no intrinsics; UTF-8 input only (no BOM); both harnesses assume a Unix-like host (run.sh, and -Wl,--wrap,malloc in the 2024 harness) |
| **Thread safety** | not documented; parse() has no global or static state (only a local view plus your context pointer), so parsing different inputs with separate contexts is reentrant by construction |
| **Drop-in for the baseline** | no |

## Gotchas

- The code the chart measured is gone. The README figure and usage example (frxml::doc, which also references an undefined `error`) are for the Oct 2024 DOM, deleted on 2025-08-27. The head is a different callback API, and the 2025 harness that tests it has no published results.
- The callback receives a pointer to a stack temporary, and each record's string_views point into your input. Copy node-&gt;size() bytes if you keep a record, and keep the input alive. Element::attrs() and children() are declared but never defined, so calling them fails to link.
- CDATA detection is broken: after '&lt;' the code matches "!CDATA[" instead of "![CDATA[", so a real &lt;![CDATA[...]]&gt; section becomes a bogus Element with no matching ETag. &lt;!DOCTYPE ...&gt; is likewise reported as an Element named "!DOCTYPE".
- Header hygiene: node.h includes only &lt;cstdint&gt; but uses std::string_view, std::ostream and std::is_same_v, so include those headers before frxml/frxml.h. string.h defines a global SPACE macro. The CMake target calls target_compile_definitions(cxx_std_17), which defines a macro rather than requiring C++17, so set the standard yourself.

## Known shortcomings

- Slower than pugixml and RapidXML (about 2.4x slower at 260-290 KiB inputs); it only beats libxml2 (\~1.8-9x) and tinyxml2 (\~2.6-5x). The published chart is from the October 2024 code; the 2025 rewrite has no published results.
- The measured code no longer exists: the chart is of the 2024 frxml::doc DOM (deleted 2025-08-27), and the current header-only callback API has no numbers. The 2024 parser could not read text between tags and its harness could not detect a failed parse; frxml was built with -O3 -march=native against distro-packaged competitors. Current code misdetects CDATA and never matches end tags. Repo archived.

## Caveats and trade-offs

The chart shows frxml SLOWER than pugixml and RapidXML, the fast incumbents in this category; it only beats libxml2 and tinyxml2. The numbers exist only as a chart image (Figure_1.png, Oct 2024) from the legacy implementation. The code was rewritten in Aug-Sep 2025 with a new harness (frxml-test/lib/main.cxx, vs pugixml/tinyxml2 on UW XML datasets) that has no published results, yet README still shows the old figure. No compiler or CPU stated; only 3 iterations per size. Limited XML 1.0 support: no DOCTYPE/ENTITY, no entity decoding. The repository is archived.

Zero-copy/single-pass design explicitly omits entity and DOCTYPE/ENTITY decoding to stay zero-copy, and only supports a limited XML 1.0 subset; goal of O(n) memory regardless of nesting depth.

## Maintenance

The author archived the repo after an Aug-Sep 2025 rewrite (last commit 2025-09-02; 1 star; no issues, releases, unit tests or CI). It is MIT-licensed and the head is four small headers that are easy to vendor, but the README's chart and example describe deleted code, and the current code has the parsing bugs listed above.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification C, tier now C.
- **Tier reason:** The only numbers are a first-party chart, docs/Figure_1.png, with values relative to frxml. The harness that produced it is public at commit 06b3b12 (test/src/main.cxx, test/script/main.py), but it states no compiler or CPU and uses only 3 iterations per size, so the tier is C.
- **Verifier notes:** The record inverted the chart. main.py divides each library's time by frxml's, so pugixml and RapidXML sitting below 1.0 means they beat frxml, and the claim to beat the named baseline pugixml is false. I kept the entry as a downgrade with libxml2 (in the yaml-toml-xml baseline list) as the beaten incumbent. The orchestrator may prefer reject/not-faster, since it loses to pugixml and RapidXML. Metadata is correct: MIT, archived, last commit 2025-09-02, 1 star.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Sharp0802/frxml>
  - <https://github.com/Sharp0802/frxml/blob/master/docs/Figure_1.png>
  - <https://github.com/Sharp0802/frxml/blob/master/docs/README.md>
  - <https://github.com/Sharp0802/frxml/blob/master/frxml-test/lib/main.cxx>
  - <https://github.com/Sharp0802/frxml/blob/master/frxml-test/CMakeLists.txt>
  - <https://github.com/Sharp0802/frxml/blob/master/run.sh>
  - <https://github.com/Sharp0802/frxml/blob/master/frxml-test/graph/main.py>
  - <https://github.com/Sharp0802/frxml/blob/master/frxml-test/samples/NOTICE>
  - <https://github.com/Sharp0802/frxml/commits/master>
  - <https://github.com/Sharp0802/frxml/blob/06b3b1276233b9d8818113df3ac6d5e1c577189c/test/src/main.cxx>
  - <https://github.com/Sharp0802/frxml/blob/06b3b1276233b9d8818113df3ac6d5e1c577189c/test/src/randomxml.cxx>
  - <https://github.com/Sharp0802/frxml/blob/06b3b1276233b9d8818113df3ac6d5e1c577189c/test/script/main.py>
  - <https://github.com/Sharp0802/frxml/blob/06b3b1276233b9d8818113df3ac6d5e1c577189c/test/CMakeLists.txt>
  - <https://github.com/Sharp0802/frxml/blob/06b3b1276233b9d8818113df3ac6d5e1c577189c/frxml/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/Sharp0802/frxml>
  - <https://github.com/Sharp0802/frxml/blob/master/docs/README.md>
  - <https://github.com/Sharp0802/frxml/blob/master/docs/Figure_1.png>
  - <https://github.com/Sharp0802/frxml/blob/master/CMakeLists.txt>
  - <https://github.com/Sharp0802/frxml/blob/master/.gitmodules>
  - <https://github.com/Sharp0802/frxml/blob/master/frxml/CMakeLists.txt>
  - <https://github.com/Sharp0802/frxml/blob/master/frxml/include/frxml/frxml.h>
  - <https://github.com/Sharp0802/frxml/blob/master/frxml/include/frxml/node.h>
  - <https://github.com/Sharp0802/frxml/blob/master/frxml/include/frxml/parse.inc>
  - <https://github.com/Sharp0802/frxml/blob/master/frxml/include/frxml/string.h>
  - <https://github.com/Sharp0802/frxml/blob/master/frxml-test/lib/main.cxx>
  - <https://github.com/Sharp0802/frxml/blob/master/frxml-test/CMakeLists.txt>
  - <https://github.com/Sharp0802/frxml/blob/master/frxml-test/graph/main.py>
  - <https://github.com/Sharp0802/frxml/blob/master/frxml-test/samples/NOTICE>
  - <https://github.com/Sharp0802/frxml/blob/master/run.sh>
  - <https://github.com/Sharp0802/frxml/commits/master>
  - <https://github.com/Sharp0802/frxml/issues?q=is%3Aissue>
  - <https://github.com/Sharp0802/frxml/releases>
  - <https://github.com/Sharp0802/frxml/tags>
  - <https://github.com/Sharp0802/frxml/commit/06b3b1276233b9d8818113df3ac6d5e1c577189c>
  - <https://github.com/Sharp0802/frxml/blob/06b3b1276233b9d8818113df3ac6d5e1c577189c/CMakeLists.txt>
  - <https://github.com/Sharp0802/frxml/blob/06b3b1276233b9d8818113df3ac6d5e1c577189c/docs/README.md>
  - <https://github.com/Sharp0802/frxml/blob/06b3b1276233b9d8818113df3ac6d5e1c577189c/frxml/CMakeLists.txt>
  - <https://github.com/Sharp0802/frxml/blob/06b3b1276233b9d8818113df3ac6d5e1c577189c/frxml/frxml.h>
  - <https://github.com/Sharp0802/frxml/blob/06b3b1276233b9d8818113df3ac6d5e1c577189c/frxml/src/frxml.cxx>
  - <https://github.com/Sharp0802/frxml/blob/06b3b1276233b9d8818113df3ac6d5e1c577189c/test/CMakeLists.txt>
  - <https://github.com/Sharp0802/frxml/blob/06b3b1276233b9d8818113df3ac6d5e1c577189c/test/randomxml.h>
  - <https://github.com/Sharp0802/frxml/blob/06b3b1276233b9d8818113df3ac6d5e1c577189c/test/src/randomxml.cxx>
  - <https://github.com/Sharp0802/frxml/blob/06b3b1276233b9d8818113df3ac6d5e1c577189c/test/src/main.cxx>
  - <https://github.com/Sharp0802/frxml/blob/06b3b1276233b9d8818113df3ac6d5e1c577189c/test/script/main.py>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/sharp0802/frxml`) · [data/wave4/enrich/raw/github_com_sharp0802_frxml.json](../../../data/wave4/enrich/raw/github_com_sharp0802_frxml.json) (enrichment confidence 0.8)

</details>
