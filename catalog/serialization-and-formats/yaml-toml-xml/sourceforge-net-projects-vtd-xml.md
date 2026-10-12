# VTD-XML

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [YAML, TOML and XML](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Java` · `GPL-2.0-or-later` · 🔴 abandoned

> Java XML parser building a compact offset/length token index, not a tree; beats libxml2 DOM parse, loses XPath.

| | |
|---|---|
| **Beats** | libxml2 |
| **Claimed result** | bemayer/xml-benchmark DOM Parse, run of 2026-09-01 (the page regenerates monthly). Mean times in ms, VTD-XML vs libxml2; all ratios derived from page data: - 100KB: 0.542 vs 0.871 (1.6x) - 1MB: 3.439 vs 10.788 (3.1x) - 10MB: 21.45 vs 104.783 (4.9x) - 100MB: 238.903 vs 646.685 (2.7x) - 1KB: 0.036 vs 0.013 (VTD-XML is 2.8x slower) These ratios are not like-for-like above 1KB. VTD-XML's rows at 100KB-100MB cover only the wide file. VTD-XML's MAX_DEPTH is 254, so it rejects the deep files (1,706-5,000 levels). Throughput x time on the page equals the wide-file size exactly. libxml2's rows average the wide file with a deep file that libxml2 2.9.14 halts at depth 256. Per-shape times are not published, so a same-file ratio cannot be derived. VTD-XML's 'DOM Parse' builds a VTD token index, not a node tree. libxml2 builds and frees a full xmlDoc. XPath //\*[@id] runs on the same wide-only files for both libraries, and VTD-XML loses at every size: - 1KB: 0.086 vs 0.005 ms (17x slower) - 100KB: 0.907 vs 0.126 ms (7.2x slower) - 1MB: 36.943 vs 2.509 ms (14.7x slower) - 10MB: 392.963 vs 42.573 ms (9.2x slower) - 100MB: 3837.515 vs 565.64 ms (6.8x slower) The page's aggregate score ranks libxml2 (32.5) above VTD-XML (30.5). |
| **Workload** | bemayer/xml-benchmark cross-language shootout (14 libraries, 7 languages). Each library runs in its own Docker container on a GitHub Actions ubuntu-latest runner. Time is the mean of N auto-calibrated iterations (the page says 'median', but the harness divides total time by iterations). Each synthetic bucket (nominal 1KB-100MB) averages a wide/shallow file and a deep/narrow file. The deep files are about 5.6 MiB (100KB label), 47.9 MiB (1MB and 10MB labels) and 100 MiB (100MB label), with 1,706-5,000 nesting levels. VTD-XML's DOM Parse is VTDGen.setDoc(xml.clone()) + parse(false), which is namespace-unaware and builds no tree. It has no rows for deep files above 1KB. |
| **Metric** | latency |
| **Hardware** | GitHub Actions ubuntu-latest runner, with each library in its own Docker container (CPU model not published) |
| **Compiler and flags** | VTD-XML: com.ximpleware:vtd-xml resolved from the Maven range [2.0,), which gives 2.13.4 (Maven Central metadata lastUpdated 2017-08-10). The harness is built with maven:3-eclipse-temurin-21 and runs on eclipse-temurin:21-jre as a plain `java -jar` with no JVM flags. It does min(5, iterations) warm-up parses, and only 1 measured iteration on files over 50 MB. libxml2: Debian bookworm's prebuilt package (2.9.14). Its harness is built with bookworm g++ via cmake -DCMAKE_BUILD_TYPE=Release (CMake default -O3 -DNDEBUG), C++17. The harness calls xmlParseMemory + xmlFreeDoc with no options (no XML_PARSE_HUGE). |
| **Adoption** | 35 stars and 11 forks on jzhang2004/vtd-xml, a full source copy of the SourceForge repo pushed by SourceForge project member jzhang2004 (last commit 2018-06-28). SourceForge: registered 2004-05-28, Last Update 2017-10-08, 74 downloads this week (checked 2026-09-25), latest file ximpleware-2.13-4-java.zip. Maven Central com.ximpleware:vtd-xml latest is 2.13.4. |
| **Last commit** | 2018-06-28 |
| **Links** | [repository](https://sourceforge.net/projects/vtd-xml/) · [benchmark](https://bemayer.github.io/xml-benchmark/) |

## Verdict

On bemayer/xml-benchmark's 2026-09-01 run (GitHub Actions ubuntu-latest, Docker, CPU not published), VTD-XML 2.13.4 on Temurin 21 (no JVM flags, parse(false), input array cloned inside the timed loop) built its token index 1.6x-4.9x faster than Debian libxml2 2.9.14's xmlParseMemory + xmlFreeDoc (C++ harness, -O3) at 100KB-100MB. VTD-XML's rows cover only the wide file because it rejects the deep files, while libxml2's rows also average in a deep file it halts at depth 256; VTD-XML also loses at 1KB (2.8x) and on XPath //\*[@id] at every size (6.8x-17x).

## Use it when

- JVM services that parse many shallow (&lt;255 levels) 100 KB-100 MB documents and read a few fields by navigation, where building DOM objects and the GC they cause is the cost. On bemayer/xml-benchmark its index build posted 0.54-239 ms vs libxml2's 0.87-647 ms, with the caveat that the file sets differ.
- Replacing Xerces or JDK DOM in Java code that only reads. On the same page, VTD-XML's DOM Parse time is lower than Xerces's at every size (0.036 vs 0.232 ms at 1KB; 238.9 vs 489.0 ms at 100MB). Again the file sets differ.
- Parse once, use many times: save the index with writeIndex() and reload it with loadIndex() so you do not re-tokenize the same large file.
- Small edits or fragment cut/paste on large documents (XMLModifier, getElementFragment), which avoids a full DOM round trip and re-serialization.
- Files larger than RAM, up to 256 GB, using the extended edition (VTDGenHuge in MEM_MAPPED mode), provided nesting stays at 30 levels or fewer.

## Skip it when

- XPath-heavy workloads. On //\*[@id] it was 6.8x-17x slower than libxml2 at every size (3837.5 vs 565.6 ms at 100MB), and slower than Xerces from 1MB up.
- Deeply nested XML. The standard edition throws 'Depth exceeds MAX_DEPTH' past 254 levels, and the 256 GB extended edition allows only 30. The standard edition also caps documents at 2 GB, or 1 GB with namespaces on.
- Tiny documents or short-lived processes. At 1KB it is 2.8x slower than libxml2, and its peak RSS on the page is 57 MB vs 5.4 MB (JVM baseline).
- Anything that needs DTD-declared or external entities, schema validation or a W3C DOM API. The FAQ calls DTD and external entities effectively deprecated, VTDGen parses a DTD but does not resolve declared entities, and a DOM interface is ruled out.
- Projects that cannot take GPLv2 plus patent notices and an unmaintained codebase. The last release was 2017, and bugs such as namespace shadowing in getElementFragmentNs (#13) are still open.

## How it is fast

It uses non-extractive tokenization, which the project calls Virtual Token Descriptor (VTD). The raw bytes stay in memory undecoded, and each token becomes one 64-bit long: 4-bit type, 8-bit depth, 20-bit length and a 30/32-bit offset. These longs are appended to pooled long[] buffers, so parsing creates no node objects, no strings and almost no GC work. Random access comes from 'location caches': per-depth arrays whose entries pair an element's record index with the index of its first child. The FAQ puts these at about 10% of parse cost and total memory at 1.3-1.5x the document size. End tags are not stored, and setDoc_BR() reuses the buffers across parses.

## Compared with alternatives

Pick it only when you must stay on the JVM and want random access, a saved index or in-place byte edits. Every catalogued sibling is native: on the same bemayer page quick-xml's DOM Parse is faster than VTD-XML at every size, and RapidXml beats it at 1KB and 100MB. For XPath, prefer simdxml or libxml2 itself.

## Integration

| | |
|---|---|
| **Form** | module (Java jar, Maven Central com.ximpleware:vtd-xml 2.13.4); C, C++ and C# ports are source-drop from the repo |
| **Dependencies** | none (the 2.13.4 POM declares no dependencies) |
| **Minimum toolchain** | Java; the FAQ lists Java 1.2 through 8 as tested, and the benchmark ran 2.13.4 on Temurin 21 JRE. The C port builds with a makefile, or with Visual Studio set to 'Compile as C'. |
| **Platforms** | any JVM; the C, C++ and C# ports cover Linux, Windows and .NET/Mono per the FAQ |
| **Thread safety** | Not thread-safe per instance. VTDNav has exactly one cursor, and AutoPilot moves it. For parallel reads, give each thread its own navigator from duplicateNav() or cloneNav(), which share the read-only XML, VTD and location-cache buffers (the javadoc says this 'may be useful for parallel XPath evaluation'). VTDGen is per-parse state. |
| **Drop-in for the baseline** | no |

## Gotchas

- parseFile(), parseGZIPFile() and similar catch IOException and ParseException, print them to System.out and return false. Use setDoc() + parse() if you need the exception.
- Hard limits in VTDGen throw ParseException: depth 254, prefix 511 bytes, qualified name 2047 bytes, and 2 GB file size (1 GB with namespaces). Text tokens longer than 1M-1 bytes are split across several records.
- The byte[] passed to setDoc() is the document. Records only point into it, so it must stay alive and unmodified for as long as the VTDNav is used.
- toNormalizedString() collapses whitespace by design (issue #9); use toString(), or toRawString() to keep entities. Issue #6 reports toString() mishandling multibyte characters, with a fix promised for '2.13_2'.

## Known shortcomings

- Rows do not compare the same files: VTD-XML refuses documents deeper than 254 levels, so its 100KB-100MB rows cover only the wide file, while libxml2's rows average in a deep file it truncates at depth 256. 6.8-17x slower than libxml2 on XPath at every size, and the suite's overall score ranks libxml2 above it. GPL-2.0-or-later with patent notices and a litigation-termination clause. Abandoned: last release 2.13.4 (2017), last commit 2018-06.
- JVM only; on the same page quick-xml's DOM parse is faster at every size and RapidXml wins at 1 KB and 100 MB, so pick VTD-XML only if you must stay on the JVM. The 256 GB memory-mapped edition (VTDGenHuge) caps depth at 30. parseFile() swallows exceptions and returns false. Open bugs in the GitHub copy (#6, #8, #13, #15) with no release after 2.13.4.

## Caveats and trade-offs

Evidence problems:
- The only head-to-head against libxml2 is bemayer/xml-benchmark, a small third-party suite (1 star, no license, created 2026-04-06). It runs once a month on a shared CI runner with no CPU model.
- Its DOM Parse buckets are not like-for-like. VTD-XML's MAX_DEPTH = 254 (VTDGen.java throws 'Depth exceeds MAX_DEPTH'), so VTD-XML fails on the 1,706-5,000-level deep files, and its 100KB-100MB rows cover only the wide file. libxml2's rows average the wide file with a deep file that libxml2 2.9.14 halts at depth 256. The displayed 1.6x-4.9x ratios therefore compare different file sets.
- VTD-XML's 'DOM Parse' builds a non-extractive token index, not a node tree.

Where VTD-XML loses:
- It is slower than libxml2 on XPath //\*[@id] at every size (6.8x-17x).
- It loses DOM Parse at 1KB.
- pugixml beats it at 1KB, 10MB and 100MB.
- The page's aggregate score ranks libxml2 above VTD-XML.

Project limits:
- VTD-XML cannot parse documents deeper than 254 levels in standard mode.
- There has been no release since 2.13.4 (2017). The last GitHub commit is from 2018-06-28.
- The source headers are GPL-2.0-or-later but also cite US patents 7133857, 7260652 and 7761459. They add a clause that terminates the licenses of parties in litigation with XimpleWare, so check before copying.

Requires a JVM; VTD's lazy/index-based model gives a fast DOM build but XPath queries afterward are then much slower than libxml2 (e.g. 3837.5ms vs 565.6ms at 100MB, derived from page data), so the win is DOM-parse-specific, not end-to-end; the project also ships native C/C++/C# ports per its site, but only the Java build was benchmarked here; dual GPLv2/commercial licensing, and the project homepage carries a notice terminating licenses for parties in litigation with XimpleWare.

## Maintenance

Abandoned: the last release is 2.13.4 (Maven Central, 2017) and the last commit on the maintainer's GitHub copy is 2018-06-28. The jar has no dependencies and is easy to adopt, but GPLv2 (commercial license on request), the listed US patents and a license-termination clause for parties in litigation with XimpleWare make it a legal-review item.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification B, tier now C.
- **Tier reason:** The page's embedded BENCHMARK_DATA (run of 2026-09-01) has VTD-XML and libxml2 rows from one harness, and the code is public (bemayer/xml-benchmark benchmarks/vtd-xml/src/main/java/bench/Bench.java, benchmarks/libxml2/bench.cpp). No CPU model is published (only 'ubuntu-latest / GitHub Actions'), so it is not A. The suite is a 1-star repo with no license, created 2026-04-06, so it is not a well-known independent suite and B does not apply. This is C, the same call batch-08 (RapidXML) and batch-35 (quick-xml) made on this suite.
- **Verifier notes:** Numbers on the page match the record exactly. Throughput x time shows that VTD-XML's DOM rows cover only the wide file, because VTD-XML rejects deep files. libxml2's rows include halted deep-file parses, so the per-size ratios are not same-file comparisons, and claimed_speedup was rewritten to say so. Other fixes: the GitHub copy is by SourceForge project member jzhang2004 (the record called it unofficial), the latest release is 2.13.4 (not 2.12), the license is GPL-2.0-or-later per the headers, and maintenance_status is abandoned (last commit 2018-06-28).
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `compared_against_cpp_std_directly`, `license`, `last_commit`, `maintenance_status`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://bemayer.github.io/xml-benchmark/>
  - <https://github.com/bemayer/xml-benchmark>
  - <https://sourceforge.net/projects/vtd-xml/>
  - <https://sourceforge.net/projects/vtd-xml/files/>
  - <https://github.com/jzhang2004/vtd-xml>
  - <https://repo1.maven.org/maven2/com/ximpleware/vtd-xml/maven-metadata.xml>
- **Sources the enricher read:**
  - <https://sourceforge.net/projects/vtd-xml/>
  - <https://vtd-xml.sourceforge.io/>
  - <https://vtd-xml.sourceforge.io/VTD.html>
  - <https://vtd-xml.sourceforge.io/faq.html>
  - <https://vtd-xml.sourceforge.io/benchmark1.html>
  - <https://vtd-xml.sourceforge.io/technical/0.html>
  - <https://github.com/jzhang2004/vtd-xml>
  - <https://github.com/jzhang2004/vtd-xml/blob/master/ximple-dev/com/ximpleware/VTDGen.java>
  - <https://github.com/jzhang2004/vtd-xml/blob/master/ximple-dev/com/ximpleware/VTDNav.java>
  - <https://github.com/jzhang2004/vtd-xml/blob/master/ximple-dev/com/ximpleware/extended/VTDGenHuge.java>
  - <https://github.com/jzhang2004/vtd-xml/blob/master/ximple-dev_c/vtd-xml/ReadMe.txt>
  - <https://github.com/jzhang2004/vtd-xml/issues?q=is%3Aissue>
  - <https://github.com/jzhang2004/vtd-xml/issues/3>
  - <https://github.com/jzhang2004/vtd-xml/issues/5>
  - <https://github.com/jzhang2004/vtd-xml/issues/6>
  - <https://github.com/jzhang2004/vtd-xml/issues/8>
  - <https://github.com/jzhang2004/vtd-xml/issues/9>
  - <https://github.com/jzhang2004/vtd-xml/issues/10>
  - <https://github.com/jzhang2004/vtd-xml/issues/12>
  - <https://github.com/jzhang2004/vtd-xml/issues/13>
  - <https://github.com/jzhang2004/vtd-xml/issues/15>
  - <https://bemayer.github.io/xml-benchmark/>
  - <https://github.com/bemayer/xml-benchmark/blob/main/benchmarks/vtd-xml/src/main/java/bench/Bench.java>
  - <https://github.com/bemayer/xml-benchmark/blob/main/benchmarks/vtd-xml/pom.xml>
  - <https://github.com/bemayer/xml-benchmark/blob/main/benchmarks/vtd-xml/Dockerfile>
  - <https://github.com/bemayer/xml-benchmark/blob/main/benchmarks/libxml2/bench.cpp>
  - <https://repo1.maven.org/maven2/com/ximpleware/vtd-xml/maven-metadata.xml>
  - <https://repo1.maven.org/maven2/com/ximpleware/vtd-xml/2.13.4/vtd-xml-2.13.4.pom>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://sourceforge.net/projects/vtd-xml`) · [data/wave4/enrich/raw/sourceforge_net_projects_vtd_xml.json](../../../data/wave4/enrich/raw/sourceforge_net_projects_vtd_xml.json) (enrichment confidence 0.7)

</details>
