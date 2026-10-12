# TupleMarkup (TML)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [YAML, TOML and XML](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🔴 abandoned

> Tiny C parser for TML, a bracket-based nested-list markup format; author claims \~5x libxml2's parse speed on equivalent data.

| | |
|---|---|
| **Beats** | libxml2 |
| **Claimed result** | "about 5x faster than Libxml2 when parsing the same data", with dramatically less memory use (per tml-c/README; no numeric table or workload description given) |
| **Workload** | Parsing unspecified sample data with the bundled C89 in-place TML parser (tml-c), informally compared to libxml2 parsing 'the same data'. |
| **Metric** | throughput |
| **Adoption** | 32 stars |
| **Last commit** | 2013-03-10 |
| **Links** | [repository](https://github.com/judnich/TupleMarkup) · [benchmark](https://github.com/judnich/TupleMarkup/blob/master/tml-c/README) |

## Verdict

The only figure is one unqualified sentence in tml-c/README (about 5x faster than libxml2 on the same data, with much less memory); no input file, libxml2 version, compiler, hardware or result table is published. Its likely source is an undocumented --benchmark flag in tools/tml-convert/tml-convert.c that times one xmlReadFile()+xmlFreeDoc()+xmlCleanupParser() against one tml_parse_file()+tml_free_doc() with clock() (file I/O included, no warm-up or repeats, gcc -std=c99 -O3), which pits a libxml2 DOM build of an XML file against parsing that file's TML conversion, which has no closing tag names.

## Use it when

- You control both the producer and the consumer and want a small, hand-editable nested-list format for configs or scene and asset descriptions (the README's OpenGL model example) instead of XML.
- Memory-tight loaders: the whole tree sits in one buffer with 1 byte of overhead per short leaf and 10 bytes per list, and the README notes it is often smaller than the source text because indentation is discarded.
- Load-once, forward-walk reads: first-child and next-sibling steps are O(1), and numeric lists such as vertex data go straight into arrays with tml_node_to_float_array/_int_array.
- Selecting subtrees by shape, for example [position | \? \? \?] or [bold | \\*], with the built-in wildcard matcher instead of hand-written tree walks.
- Small C or C++ projects built with GCC or Clang that want four source files, only libc, and no build system.

## Skip it when

- You must read or write XML or talk to anything that does: it parses TML only, so every document has to be converted first (tml-convert does that with libxml2), and namespaces, DTDs, entities, XPath and validation have no TML equivalent.
- Untrusted input: parsing, string conversion and pattern matching recurse once per nesting level with no depth limit; a word that runs to the end of the buffer (for example the truncated '[hello' from the tests) reads one byte past it; a failed realloc leaks the old arena. The code has had no fuzzing and no maintenance since 2013.
- Random access or editing: tml_child_count and tml_child_at_index are O(n), nodes have no parent link, and there is no API to modify the tree; the only way to write it out is tml_node_to_markup_string into a fixed-size buffer.
- Streaming or very large inputs: the whole file is read into memory, the arena starts at twice the input size, and 32-bit offsets cap parsed data at 4 GB.
- Prose markup where line breaks matter, or files that start with a UTF-8 BOM: the BOM bytes are read as a word before the root '[' and parsing fails with 'Expecting opening bracket at start of file'.

## How it is fast

The tokenizer works in place: each token is a pointer and length into the input buffer, and words are scanned with a hand-unrolled 8-way byte-compare loop that switches to a slower in-place escape-collapsing path only when it hits a backslash. The recursive-descent parser appends every node to one contiguous, doubling byte buffer (an arena) in a variable-length packed layout: a leaf shorter than 255 bytes gets a single header byte (its length, which is also the relative offset to its next sibling) plus its NUL-terminated string, and lists and long leaves get a 9-byte header (0xFF plus 32-bit first-child and next-sibling offsets). Parsing a document therefore takes a handful of allocations (input copy, doc struct, arena growth and shrink) instead of one per node, with no SIMD, encoding conversion, entity or namespace work. The format also has less to check, since it has only four reserved symbols and no closing tag names or attribute syntax.

## Compared with alternatives

Every XML sibling (RapidXml, SpeedyXml, LightningXML, libleptris, frxml) parses real XML, and RapidXml alone shows 1084.9 vs 278.8 MB/s against libxml2 in bemayer/xml-benchmark's 10 MB bucket, so if you need faster XML, pick one of those. Pick TML only if you can drop XML entirely and want a four-file C parser with a compact packed tree for your own data files.

## Integration

| | |
|---|---|
| **Form** | source-drop (tml_parser.c/.h and tml_tokenizer.c/.h; optional C++ wrapper tml-cpp/source/tml.hpp) |
| **Dependencies** | none beyond libc; the optional tools/tml-convert converter and benchmark need libxml2 |
| **Minimum toolchain** | GCC or Clang. The README says any C89 compiler and the tests build with gcc -std=c89 -Wall, but tml_parser.c relies on GNU extensions (the old 'value: ""' initializer syntax and bare __inline__) and on C99 &lt;stdbool.h&gt;/&lt;stdint.h&gt;. tml-convert builds with gcc -std=c99 -O3. MSVC support is partial: a TML_INLINE macro exists, but tml_parser.c still needs patching. |
| **Platforms** | any hosted C platform in principle (scalar code, no SIMD or OS calls); offsets are read and written through unaligned uint32_t\* casts, which works on x86-64 and aarch64 but is undefined behavior and can trap on strict-alignment CPUs |
| **Thread safety** | Not documented. There is no global mutable state (TML_NODE_NULL is const), so separate docs can be parsed on separate threads, and the read API never modifies a finished doc. There is no locking. |
| **Drop-in for the baseline** | no |

## Gotchas

- The C word scanner stops at space, tab, brackets, '|' and backslash but not at CR or LF. The 2012-12-27 'Performance optimization' commit replaced isspace() with ' '/'\t' checks, so a word followed directly by a line break keeps it: 'test.' in the README's own markup example parses as "test.\n". atoi/atof don't mind, but string compares and pattern matches fail. Put a space before line ends or trim values.
- tml_parse_in_memory rewrites your buffer while collapsing escape codes, so treat it as scratch; the other entry points copy the input first. Node strings live in the doc's arena and are freed by tml_free_doc. Peak heap is about 3x the input (a copy plus the 2x arena) until the final shrink.
- A parse error still returns a doc: check doc-&gt;error_message, a static string with no line or column. NULL means only an allocation or file-open failure. The C++ wrapper throws bare const char\* only on NULL, not on parse errors.
- tml.hpp defines several TmlNode member functions outside the class without 'inline', so including it in more than one translation unit causes duplicate-symbol link errors. Its toString()/toMarkupString() silently truncate at MAX_TML_STRING_SIZE (4096), and the std::string pattern overloads re-parse the pattern on every call.

## Known shortcomings

- Its own format, not an XML parser: the libxml2 comparison times parsing an XML file against parsing its smaller TML conversion, once, with clock() and file I/O included, and no results are published. The README's C89 claim is false (GNU and C99 features). Words followed by CR/LF keep those bytes (commit 395ed74). Unbounded recursion, a one-byte over-read on truncated input, and the C++ header breaks the link when included in two files.

## Caveats and trade-offs

No benchmark methodology, workload size, compiler, or hardware stated anywhere -- a bare first-party numeric claim; project untouched since 2013 (abandoned); the comparison is between a custom markup format's parser and an XML parser, so treat the 'faster than libxml2' claim as weak/indirect evidence.

TML is a distinct minimalist markup language (bracket-minimized nested lists) rather than XML itself, so adopting it means replacing XML documents wholesale, not a drop-in libxml2 substitute; in-place parsing needs no malloc and targets no-heap embedded use; C89-compatible.

## Maintenance

Abandoned since 2013-03-10 (no tags or releases; the one open issue is a 2013 offer to write a Java port), but it is MIT-licensed and about 1,270 lines in four C files, so it is easy to vendor as long as you fix bugs like the line-break word bug yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The only number is one sentence in tml-c/README: 'about 5x faster than Libxml2 when parsing the same data'. The repo has no benchmark code (only unit tests in tml-c/tests), no workload, no compiler and no hardware, so this is a first-party number without methodology and stays C.
- **Verifier notes:** The claim is quoted accurately. Metadata checks out: MIT, not archived, not a fork, 32 stars, last commit 2013-03-10, so abandoned. The comparison is TML-format data against the equivalent XML (the repo's tml-convert tool uses libxml2), so the evidence is indirect, as the caveats already say.
- **Pages the verifier opened:**
  - <https://github.com/judnich/TupleMarkup>
  - <https://github.com/judnich/TupleMarkup/blob/master/tml-c/README>
  - <https://github.com/judnich/TupleMarkup/blob/master/README.md>
  - <https://github.com/judnich/TupleMarkup/blob/master/tml-c/tests/test_parser.c>
  - <https://github.com/judnich/TupleMarkup/blob/master/tml-c/tests/makefile>
  - <https://github.com/judnich/TupleMarkup/blob/master/tools/tml-convert/README>
  - <https://github.com/judnich/TupleMarkup/blob/master/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/judnich/TupleMarkup>
  - <https://github.com/judnich/TupleMarkup/blob/master/README.md>
  - <https://github.com/judnich/TupleMarkup/blob/master/SPEC.md>
  - <https://github.com/judnich/TupleMarkup/blob/master/EXAMPLES.md>
  - <https://github.com/judnich/TupleMarkup/blob/master/LICENSE>
  - <https://github.com/judnich/TupleMarkup/blob/master/tml-c/README>
  - <https://github.com/judnich/TupleMarkup/blob/master/tml-c/source/tml_parser.h>
  - <https://github.com/judnich/TupleMarkup/blob/master/tml-c/source/tml_parser.c>
  - <https://github.com/judnich/TupleMarkup/blob/master/tml-c/source/tml_tokenizer.h>
  - <https://github.com/judnich/TupleMarkup/blob/master/tml-c/source/tml_tokenizer.c>
  - <https://github.com/judnich/TupleMarkup/blob/master/tml-c/tests/makefile>
  - <https://github.com/judnich/TupleMarkup/blob/master/tml-c/tests/test_parser.c>
  - <https://github.com/judnich/TupleMarkup/blob/master/tml-c/tests/test_tokenizer.c>
  - <https://github.com/judnich/TupleMarkup/blob/master/tml-cpp/README>
  - <https://github.com/judnich/TupleMarkup/blob/master/tml-cpp/source/tml.hpp>
  - <https://github.com/judnich/TupleMarkup/blob/master/tools/README>
  - <https://github.com/judnich/TupleMarkup/blob/master/tools/tml-convert/README>
  - <https://github.com/judnich/TupleMarkup/blob/master/tools/tml-convert/makefile>
  - <https://github.com/judnich/TupleMarkup/blob/master/tools/tml-convert/tml-convert.c>
  - <https://github.com/judnich/TupleMarkup/issues?q=is%3Aissue>
  - <https://github.com/judnich/TupleMarkup/pulls?q=is%3Apr>
  - <https://github.com/judnich/TupleMarkup/commits/master>
  - <https://github.com/judnich/TupleMarkup/commit/395ed740a996f3a0e5292acb5c56c2d6c95f1a97>
  - <https://github.com/judnich/TupleMarkup/tags>
  - <https://github.com/judnich/TupleMarkup/releases>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/judnich/tuplemarkup`) · [data/wave4/enrich/raw/github_com_judnich_tuplemarkup.json](../../../data/wave4/enrich/raw/github_com_judnich_tuplemarkup.json) (enrichment confidence 0.72)

</details>
