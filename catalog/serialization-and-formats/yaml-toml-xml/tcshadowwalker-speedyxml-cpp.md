# SpeedyXml (SpeedyXml-cpp)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [YAML, TOML and XML](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> C++20 streaming SAX-style XML push parser with zero-copy callbacks; author-measured 4.4x faster than libxml2's SAX2 streaming parser.

| | |
|---|---|
| **Beats** | libxml2 |
| **Claimed result** | README table, 235 MiB real-world document, single core: SpeedyXml 0.34 s vs libxml2 (streaming SAX2) 1.53 s (4.4x), pugixml DOM 1.00 s (2.9x), RapidXml DOM in-situ 1.29 s (3.7x), Expat 4.38 s (12.7x); 'That is \~680 MiB/s'. README chart over 8 public datasets ('no other parser reaches half of SpeedyXml's throughput on any document') puts libxml2 at 6-29% of SpeedyXml's throughput, i.e. roughly 3.4x-17x slower (derived from page data). |
| **Workload** | Single-core, streaming SAX-style push parse of a 235 MiB real-world XML document, comparing wall-clock time against pugixml (DOM), RapidXml (in-situ DOM), libxml2 (SAX2 streaming), and Expat (streaming); repeated across 8 additional public XML datasets via a bundled script |
| **Metric** | throughput |
| **Hardware** | Not stated |
| **Compiler and flags** | Not stated for the published results; tools/public_bench.sh builds the bench tool with CMAKE_BUILD_TYPE=Release and the system default compiler. |
| **Adoption** | 1 star |
| **Last commit** | 2026-07-29 |
| **Links** | [repository](https://github.com/tcShadowWalker/SpeedyXml-cpp) · [benchmark](https://github.com/tcShadowWalker/SpeedyXml-cpp#benchmark) |

## Verdict

The author's own bench tool times each parser once, by wall clock, on a 235 MiB document that is neither named nor published: SpeedyXml 0.34 s vs 1.53 s (4.4x) for libxml2's SAX2 push parser, both fed 1 MiB chunks with no-op element callbacks, plus pugixml DOM 1.00 s, RapidXml 1.29 s and Expat 4.38 s. An 8-dataset chart puts libxml2 at 6-29% of SpeedyXml's throughput (about 3.4x slower on treebank, up to 17x on text-heavy Wikipedia). Compiler, flags, CPU and libxml2 version are not stated. The timings include file reads, SpeedyXml always runs last, and it does less work than libxml2 (no text decoding, namespaces, DTDs or tag matching).

## Use it when

- Single-pass extraction from very large or unbounded UTF-8 XML dumps (Wikipedia, OpenStreetMap, StackExchange, dblp-style exports) that are too big to hold as a DOM
- Single-core ETL where libxml2 SAX2 or Expat is the bottleneck: the author's 8-dataset chart shows libxml2 at 6-29% and Expat at 2-11% of SpeedyXml's throughput
- Input arriving in arbitrary chunks from sockets or files: feedInput accepts any slice boundary (tests feed 1-byte slices, the fuzz harness 1-97 bytes), and \~1 MiB slices are recommended for speed
- Documents with a known schema where you want callbacks only on specific paths: the Dispatcher skips unlisted subtrees by depth counting and switches text events off outside collectText/onText nodes
- Codebases that want a BSD-3-Clause, dependency-free parser they can vendor as one header plus one .cpp

## Skip it when

- You need a tree, XPath or random access: it is push-only, so a DOM parser (pugixml, RapidXml, libsimdxml) fits better
- UTF-16 or Latin-1 input, documents with an internal DTD subset or custom entities (rejected), or anything needing namespace resolution: none of these are supported, and libxml2 handles them
- Untrusted input that must be well-formed: it is not a validating parser, and without enableValidation_TagNesting it accepts mismatched and unclosed tags
- Big-endian targets (a static_assert rejects them), or teams that need a proven dependency: it went public 2026-07-27 with one release (v1.0.0), has 1 star and no third-party users, and CI runs only on Ubuntu with GCC and Clang
- Workloads that need decoded text for every node: the published timings use no-op callbacks that never decode text, so the cost of calling decodeXmlChars or collectText yourself is not included in them

## How it is fast

Nearly all scanning goes through memchr: '&lt;' ends a text run, then '&gt;' ends the tag, then '=', the quote character and '&' are found inside attributes. Tag-name ends are found with an 8-bytes-per-step SWAR bit trick instead of SIMD intrinsics. Callbacks get std::string_view slices of the caller's buffer, so the parser copies only tags that straddle a slice boundary. It also skips work a conforming parser does: no text entity decoding, no namespace or DTD processing, no encoding handling, and no start/end-tag matching unless the optional validation layer is on. Predefined entities in attributes are matched with 32-bit word compares, and setEnableTextEvent(false), which the dispatcher toggles automatically, turns off text callbacks for elements you ignore.

## Compared with alternatives

RapidXml, libsimdxml and Parshred's headline numbers are for DOM/index parsers that need the whole document in memory. Pick SpeedyXml for constant-memory, single-pass streaming of multi-hundred-MiB or unbounded input, with a BSD-3-Clause license and no ISA requirements; pick Parshred (AGPL-3.0, with SAX/pull/streaming APIs, namespaces, DTD validation and XPath) or libsimdxml (XPath) when you need standards coverage or queries.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake target SpeedyXml) or source-drop of include/SpeedyXml/SpeedyXml.h + src/SpeedyXml.cpp (add SpeedyXmlDispatcher.h/.cpp for the schema layer) |
| **Dependencies** | none (C++ standard library only); expat, pugixml, libxml2 and RapidXml are used only by the optional bench tool |
| **Minimum toolchain** | C++20 (uses std::span and &lt;bit&gt;); CMake 3.20 for the CMake build; minimum GCC/Clang versions not documented (CI uses the current Ubuntu GCC and Clang) |
| **Platforms** | any little-endian target (enforced by static_assert); no SIMD intrinsics (portable SWAR + memchr); CI runs only on GitHub ubuntu-latest, and macOS, Windows and MSVC are untested |
| **Thread safety** | not documented for XmlStreamParser, and each instance holds mutable buffers, so use one per stream/thread; the dispatcher docs say a compiled XmlSchema is immutable and can drive any number of parsers concurrently |
| **Drop-in for the baseline** | no |

## Gotchas

- Every string_view (tag name, attribute, text) is valid only inside the callback, so copy what you keep. rawTextData can fire several times per text node, including whitespace-only pieces, and unlike attributes its text is not entity-decoded.
- isValidEndOfDocument() checks only the parser state and trailing text, so `<a></b>` or an unclosed root passes unless you call enableValidation_TagNesting(). That layer reports errors by throwing XmlValidationException (default maxDepth 64), while syntax errors are reported by feedInput returning false plus getError().
- The encoding declaration is ignored, so non-UTF-8 bytes are passed through, not rejected. Per the source, a leading UTF-8 BOM reaches you as a text event. Unknown named entities such as &auml; (declared in external DTDs) stay undecoded, and processing instructions are skipped silently.
- feedInput takes an int length, so slices must be under 2 GiB. readStream reads through a fixed 64 KiB stack buffer, but the README says \~1 MiB slices give the best performance (the bench uses 1 MiB), so on hot paths call feedInput with your own large buffer. Tags that straddle slices are buffered up to setMaxBufferSize (default 1 MiB), then the parse fails.

## Caveats and trade-offs

No CPU model, compiler, or flags are given for the README numbers, and the 235 MiB document is unnamed and not published (the 8 public datasets in the chart are reproducible via tools/public_bench.sh). The bench tool times each parser once per run with gettimeofday wall clock, in a fixed order with SpeedyXml last. The pugixml/RapidXml rows are DOM vs streaming, as the author notes. The libxml2 comparison is streaming vs streaming, but SpeedyXml does less work: UTF-8 only, no namespace resolution, no DTD entities, not validating, text entities not decoded. Very new (created 2026-07-27), 1-star project with no third-party corroboration.

Streaming SAX-like push model only, not a DOM (caller must build any tree themselves); does not support XML entity declarations with internal DTD subsets, no namespace resolution, UTF-8-only, requires a little-endian machine

## Maintenance

Active but brand-new: the code history goes back to Feb 2025, it went public 2026-07-27 as v1.0.0, and the last commit is 2026-07-29. It is BSD-3-Clause and dependency-free, easy to vendor (two core files), fuzzed with libFuzzer and tested in CI under ASan/UBSan.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** README benchmark table (SpeedyXml 0.34 s vs libxml2 SAX2 1.53 s, 4.4x) comes from public benchmark code (tools/CmpOtherParsers.cpp via tools/benchmark.cmake, tools/public_bench.sh), but no compiler, flags, or CPU model are stated for the published results, so the tier is first-party C.
- **Verifier notes:** Numbers match the README exactly, and the benchmark code is public. Public-dataset ratios were read from the README SVG chart (bar order SpeedyXml, PugiXml, RapidXml, Expat, LibXml2 per tools/gen_bench_chart.py). Metadata (BSD-3-Clause, not fork, 1 star, last commit 2026-07-29, active) is confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp#benchmark>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp/blob/master/tools/CmpOtherParsers.cpp>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp/blob/master/tools/benchmark.cmake>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp/blob/master/tools/public_bench.sh>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp/blob/master/tools/gen_bench_chart.py>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp/blob/master/assets/bench-datasets-light.svg>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp/blob/master/CMakeLists.txt>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp/blob/master/ci.sh>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp/blob/master/.github/workflows/ci.yml>
- **Sources the enricher read:**
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp#benchmark>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp/blob/master/include/SpeedyXml/SpeedyXml.h>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp/blob/master/src/SpeedyXml.cpp>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp/blob/master/include/SpeedyXml/SpeedyXmlDispatcher.h>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp/blob/master/src/SpeedyXmlDispatcher.cpp>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp/blob/master/CMakeLists.txt>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp/blob/master/tools/CmpOtherParsers.cpp>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp/blob/master/tools/benchmark.cmake>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp/blob/master/tools/public_bench.sh>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp/blob/master/tools/gen_bench_chart.py>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp/blob/master/assets/bench-datasets-light.svg>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp/blob/master/ci.sh>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp/blob/master/.github/workflows/ci.yml>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp/blob/master/tests/CMakeLists.txt>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp/blob/master/tests/TestSpeedyXml.cpp>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp/blob/master/tests/FuzzSpeedyXml.cpp>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp/blob/master/tools/fuzz.sh>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp/blob/master/tools/CMakeLists.txt>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp/blob/master/tools/XmlParser_Stream_Fast.cpp>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp/blob/master/examples/DblpStats.cpp>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp/blob/master/.gitignore>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp/commits/master>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp/issues?q=is%3Aissue>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp/releases>
  - <https://github.com/tcShadowWalker/SpeedyXml-cpp/tags>
  - <https://github.com/gregghy/parshred>
  - <https://github.com/KrzysztofKowalski/libsimdxml>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/tcshadowwalker/speedyxml-cpp`) · [data/wave4/enrich/raw/github_com_tcshadowwalker_speedyxml_cpp.json](../../../data/wave4/enrich/raw/github_com_tcshadowwalker_speedyxml_cpp.json) (enrichment confidence 0.8)

</details>
