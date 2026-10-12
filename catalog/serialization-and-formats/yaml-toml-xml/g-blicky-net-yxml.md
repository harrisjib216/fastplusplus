# yxml

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [YAML, TOML and XML](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🔴 abandoned

> Tiny (6 KB) malloc-free C streaming XML parser; about 2.2-2.4x faster than a stripped-down libxml2 on large dumps.

| | |
|---|---|
| **Beats** | libxml2 |
| **Claimed result** | \~2.2-2.4x faster than libxml2 (1.15s vs 2.53s on the Wikipedia dump, 0.74s vs 1.75s on the Discogs dump, both gcc 4.8.1 -O2) (derived from page data); \~1.3-1.5x faster than Expat (1.15s vs 1.47s, 0.74s vs 1.09s) on the same runs |
| **Workload** | Parsing two real-world XML dumps end-to-end (162 MiB Wikipedia XML dump and 94 MiB Discogs XML dump), measuring wall-clock parse time; also benchmarked against Expat and Mini-XML (mxml) on the same files. |
| **Metric** | throughput |
| **Hardware** | Linux 3.10.7, 3 GHz Intel E8400 (the page says 'Core Duo'; the E8400 is a Core 2 Duo part), 4GB RAM |
| **Compiler and flags** | gcc 4.8.1 (musl-cross x86_64-linux-musl 0.9.13 toolchain, static linking), -static -O2; a second table uses -Os |
| **Adoption** | Self-hosted cgit, so no star count. The project page lists users including FreeBSD pkg, getdns, Fuchsia (SVG parsing), ncdc, BTstack, RetroArch, radare2 and Crank Storyboard. Unofficial GitHub copies exist (e.g. JulStrat/yxml, 13 stars; getdnsapi/yxml). |
| **Last commit** | 2020-11-08 |
| **Links** | [repository](https://g.blicky.net/yxml.git) · [benchmark](https://dev.yorhel.nl/yxml) |

## Verdict

This is the author's own 2013-era benchmark. Each program is statically linked against musl 0.9.13 with gcc 4.8.1 -O2, reads the whole file into memory, parses it, and is timed with `time` on a 3 GHz Core 2 Duo E8400 running Linux 3.10.7. yxml took 1.15 s vs 2.53 s for libxml2 2.9.1 (xmlTextReader, with most features configured out) on a 162 MiB Wikipedia abstract dump, and 0.74 s vs 1.75 s on a 94 MiB Discogs dump (about 2.2-2.4x); Expat 2.1.0 with no callbacks took 1.47 s and 1.09 s. At -Os, yxml falls behind Expat on the Wikipedia file (1.67 s vs 1.58 s).

## Use it when

- Embedded or memory-constrained C targets that need to read XML with no heap use: about 6 KB of object code, and a 4-8 KiB name stack is enough for deep nesting according to the manual.
- Incremental, event-driven parsing, such as bytes arriving on a socket or file chunks read in a loop. The parser keeps all state in yxml_t, so it can stop and resume at any byte boundary.
- Pulling a few fields out of multi-hundred-MiB XML dumps in constant memory, where the caller buffers only the attributes or elements it needs.
- C projects that currently link libxml2 or Expat only to check well-formedness and tokenize, and that would rather vendor two MIT-licensed files than depend on a library.
- Untrusted input where DTD entity expansion is unwanted. yxml does not expand custom entities at all, so billion-laughs-style expansion cannot occur. The author says it is extensively fuzzed.

## Skip it when

- You need anything beyond tokenizing: DOM or tree access, XPath, XSLT, namespace resolution, or DTD or XML Schema validation. The page lists all of these as non-features.
- Documents that define or use custom entities (&lt;!ENTITY&gt;), or that contain conditional sections in &lt;!DOCTYPE&gt;. These cause YXML_EREF or a parse error rather than being handled.
- UTF-16 or other non-ASCII-compatible encodings. You must transcode to UTF-8 first, and yxml does not validate the encoding (garbage in, garbage out).
- Maximum throughput on large in-memory documents. The per-byte call API and plain switch DFA work out to about 130-140 MiB/s on the author's 2008-era E8400 (derived from 162 MiB/1.15 s and 94 MiB/0.74 s). The benchmark never compared it against pugixml or RapidXML, and SIMD/DOM siblings report GB/s-class numbers on modern hardware (not directly comparable).
- You need strict conformance or active upstream support. It does not check that attribute names are unique or that non-ASCII characters in names fall in the allowed Unicode ranges. There have been no commits since 2020, no tarball releases and no ABI stability promise.

## How it is fast

The grammar is written as a hand-specified DFA in a small table file (yxml-states). A Perl script (yxml-gen.pl) compiles that table into a single switch statement inside yxml_parse(), which handles one byte per call with no lookahead, no input buffering, no tree building and no malloc. Open element, attribute and PI names are pushed onto a NUL-separated stack in a fixed buffer the caller supplies. Character data comes back through an 8-byte field rather than being copied into strings, and the five predefined entity names are matched by packing up to five chars into a uint64 and comparing integers. Much of the speedup comes from doing less work than libxml2: no DTD processing, no custom entities, no namespace handling and no duplicate-attribute check. There is no SIMD.

## Compared with alternatives

Among the libxml2 challengers (SpeedyXml-cpp 4.4x, libleptris 2.5-3.6x SAX, RapidXml DOM), pick yxml when footprint, zero allocation and byte-at-a-time incremental input matter more than peak throughput, for example on embedded targets or in socket-driven C code. When you need raw speed on big in-memory files or a DOM, the siblings report far higher numbers on newer hardware.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (libc only: stdint.h, stddef.h, string.h). Perl is needed only to regenerate yxml.c from yxml-states and yxml.c.in, and the generated yxml.c is committed. An optional Makefile builds libyxml.a. |
| **Minimum toolchain** | C99 compiler: uses stdint.h and inline. yxml.h maps inline to __inline on MSVC, but strict C89 builds need a header tweak (open issue #6). The header has extern "C" guards for C++. |
| **Platforms** | any: pure, byte-oriented portable C with no SIMD or architecture-specific code. The benchmark ran on x86-64 Linux with musl. |
| **Thread safety** | Not documented. All parse state lives in the caller-owned yxml_t and its stack buffer, and the source has no mutable globals, so separate instances should be independent. Never share one instance across threads. |
| **Drop-in for the baseline** | no |

## Gotchas

- x-&gt;elem is valid only until the attribute list ends, not on YXML_ELEMEND. On &lt;n/&gt; inside &lt;foo&gt;, ELEMEND shows elem as 'foo'. The author confirmed in 2024 (issue #7) that this is a documented quirk, so keep your own stack of element names if you need the closing tag's name.
- The name stack buffer has a fixed size and cannot grow. A deep nesting or a long element/attribute/PI name returns YXML_ESTACK. Budget 1 + depth\*(max_name+1) + max_attr_or_pi_name+1 bytes.
- Text arrives in tiny chunks, usually one byte per CONTENT/ATTRVAL token (up to a few bytes for '?x', ']]x' or UTF-8 from &#N;). Multibyte UTF-8 characters are split across calls, so the caller must concatenate them and should cap buffer growth.
- Errors cannot be recovered from; you must re-init to parse a new document. A NUL byte is a syntax error. yxml_parse() cannot detect a missing or unclosed root element or an unterminated comment or PI, so always call yxml_eof() at the end. Duplicate attributes are silently allowed.

## Known shortcomings

- Not like-for-like: yxml does no validation and has no DTD support, libxml2 runs through xmlTextReader with most features off, and Expat runs with no callbacks. Each timing is one whole-process run on an old E8400 with gcc 4.8.1. In the -Os table yxml is slower than Expat on the Wiki file (1.67 vs 1.58 s). Abandoned since 2020-11.
- About 130-140 MiB/s on a 2008 E8400, well below the GB/s-class XML parsers in this category; pick it for size and simplicity. runbench.sh times each binary twice and the page does not say which run it shows. 'Extensively fuzzed' is unverifiable (no OSS-Fuzz). x-&gt;elem is not valid on YXML_ELEMEND (#7). Dormant rather than abandoned; issues are on code.blicky.net.

## Caveats and trade-offs

The benchmark dates from about 2013-2014 and ran on a 2008-era CPU (E8400) with 2013 library versions (libxml2 2.9.1, Expat 2.1.0). It is not compared against pugixml or RapidXML; the only rivals are Expat, libxml2 and Mini-XML. The numbers are the author's own, from his project page, and nobody has reproduced them independently. The comparison is not like-for-like: libxml2 runs through the xmlTextReader pull API with most features configured out (--without-push/sax1/tree/valid...), and Expat runs with no callbacks. yxml is non-validating, with no DTD or custom-entity support, so it does less work. Each timing is a single `time` of the whole process, including loading a pre-cached file. At -Os yxml is slower than Expat on the Wiki file (1.67s vs 1.58s) and faster on Discogs (1.02s vs 1.20s), though it still beats libxml2 (3.01s/2.08s). The repo is self-hosted cgit (unofficial GitHub copies exist) and has had no commits since 2020-11-08.

Minimal 3-function pull-style/streaming API, no malloc(), only 6 KiB object code; non-validating beyond well-formedness checks; no DTD, namespaces, XSLT, or XPath support; cannot parse non-ASCII-compatible encodings directly.

## Maintenance

Dormant: there have been no commits since 2020-11-08 and no tarball releases, though the author still answered an issue in March 2024. It is MIT-licensed, designed to be vendored as two files, and ships inside FreeBSD pkg, getdns, Fuchsia (SVG) and RetroArch.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** The page's -O2 table shows yxml at 1.15s (Wiki) and 0.74s (Discogs), against libxml2 2.9.1 at 2.53s/1.75s and Expat 2.1.0 at 1.47s/1.09s. The benchmark code is public in bench/ of g.blicky.net/yxml.git (Makefile, bench.c, runbench.sh), and it builds and runs libxml2, Expat and Mini-XML. The page states gcc 4.8.1 -O2, and the Makefile sets CFLAGS=-static -O2 with the musl-cross 0.9.13 toolchain. The page also states the CPU (3 GHz Intel E8400) and the OS (Linux 3.10.7).
- **Verifier notes:** The claimed numbers and the derived ratios (about 2.2x and 2.36x over libxml2, about 1.28x and 1.47x over Expat at -O2) match the page exactly. The license is MIT per the COPYING file, the last commit is 2020-11-08 per the cgit log, and the project is abandoned (more than 3 years old). The corrections only refine the toolchain and hardware wording, add usage details, and extend the caveats with how the benchmark was run and the -Os result.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://dev.yorhel.nl/yxml>
  - <https://g.blicky.net/yxml.git/>
  - <https://g.blicky.net/yxml.git/log/>
  - <https://g.blicky.net/yxml.git/tree/bench>
  - <https://g.blicky.net/yxml.git/tree/COPYING>
  - <https://g.blicky.net/yxml.git/plain/bench/Makefile>
  - <https://g.blicky.net/yxml.git/plain/bench/bench.c>
  - <https://g.blicky.net/yxml.git/plain/bench/runbench.sh>
  - <https://github.com/yorhel/yxml>
  - <https://github.com/JulStrat/yxml>
  - <https://github.com/getdnsapi/yxml>
- **Sources the enricher read:**
  - <https://dev.yorhel.nl/yxml>
  - <https://dev.yorhel.nl/yxml/man>
  - <https://g.blicky.net/yxml.git/log/>
  - <https://g.blicky.net/yxml.git/plain/yxml.h>
  - <https://g.blicky.net/yxml.git/plain/yxml.c.in>
  - <https://g.blicky.net/yxml.git/plain/yxml-gen.pl>
  - <https://g.blicky.net/yxml.git/plain/yxml-states>
  - <https://g.blicky.net/yxml.git/plain/bench/Makefile>
  - <https://g.blicky.net/yxml.git/plain/COPYING>
  - <https://code.blicky.net/yorhel/yxml>
  - <https://code.blicky.net/yorhel/yxml/issues>
  - <https://code.blicky.net/yorhel/yxml/issues/6>
  - <https://code.blicky.net/yorhel/yxml/issues/7>
  - <https://github.com/JulStrat/yxml>
  - <https://github.com/JulStrat/yxml/blob/master/bench/bench.c>
  - <https://github.com/JulStrat/yxml/blob/master/bench/runbench.sh>
  - <https://github.com/JulStrat/yxml/blob/master/Makefile>
  - <https://github.com/JulStrat/yxml/blob/master/.github/README.md>
  - <https://github.com/JulStrat/yxml/issues/3>
  - <https://github.com/JulStrat/yxml/pull/2>
  - <https://github.com/getdnsapi/yxml>
  - <https://github.com/yorhel/yxml>
  - <https://github.com/google/oss-fuzz/pull/12620>
  - <https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=yxml>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://g.blicky.net/yxml`) · [data/wave4/enrich/raw/g_blicky_net_yxml.json](../../../data/wave4/enrich/raw/g_blicky_net_yxml.json) (enrichment confidence 0.85)

</details>
