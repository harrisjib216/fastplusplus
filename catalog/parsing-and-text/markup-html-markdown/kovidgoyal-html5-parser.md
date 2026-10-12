# html5-parser

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [HTML, Markdown and markup](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C (Python extension)` · `Apache-2.0` · 🟢 active

> C extension pairing a gumbo-derived HTML5 tokenizer with a direct-to-libxml2 tree build; far faster than pure-Python html5lib.

| | |
|---|---|
| **Beats** | html5lib (pure-Python HTML5 parser); also BeautifulSoup with html5lib and lxml (libxml2) backends |
| **Claimed result** | 35x faster than html5lib (lxml tree, HTML5 support); 8x faster than BeautifulSoup+html5lib; 2x faster than BeautifulSoup+lxml; author states an overall \~37x speedup on his system. |
| **Workload** | Parsing a \~5.7MB real-world HTML document into a tree; 100 iterations for html5-parser vs 10 iterations for competing libraries, on the author's own machine with Python 3. |
| **Metric** | throughput |
| **Adoption** | 706 stars; used inside the calibre e-book application |
| **Last commit** | 2026-09-20 |
| **Links** | [repository](https://github.com/kovidgoyal/html5-parser) · [benchmark](https://html5-parser.readthedocs.io/en/latest/index.html) |

## Verdict

Author's own benchmark.py, a single run on his own machine with Python 3 (no CPU, OS, or compiler flags stated), parsed a 5.7MB HTML file 100x with html5-parser vs 10x for the others: 0.397s vs html5lib 13.906s (35x, the apples-to-apples lxml-tree/HTML5 comparison), BeautifulSoup+html5lib 12.683s (8x), and BeautifulSoup+lxml.html 3.826s (2x -- this margin reflects BeautifulSoup's own overhead, not libxml2 speed, since html5-parser was not benchmarked against lxml.html/libxml2 used directly).

## Use it when

- Already building on lxml/libxml2 in Python and need spec-correct HTML5 (not HTML4/XML) tokenization and tree construction
- Parsing large HTML documents or a high volume of pages where html5lib or BeautifulSoup+html5lib throughput is the bottleneck
- Need HTML5-correct namespace handling for embedded SVG/MathML, which html5lib handles poorly
- Parsing messy or slightly-XHTML-flavored markup, using maybe_xhtml to tolerate self-closed elements
- Desktop/batch app parsing lots of untrusted real-world HTML in bulk, e.g. an e-book/EPUB pipeline (its proving ground is calibre)

## Skip it when

- Already calling lxml.html.fromstring/libxml2 directly and don't need strict HTML5 algorithm compliance -- html5-parser is not shown to beat libxml2 itself; selectolax's benchmark measured it slower than lxml.html on real pages (16.10s vs 9.09s over 754 pages)
- Environment can't build/ship a C extension, or uses PyPI's binary lxml wheel (static libxml2) -- html5-parser raises a RuntimeError at import on a libxml2 version mismatch unless lxml is installed with --no-binary
- Need streaming or head-only parsing to skip a large &lt;body&gt; -- not supported (open feature request, issue #31)
- Parsing adversarial/untrusted fragments through non-HTML fragment_context -- a MathML-integration-point fragment case caused infinite looping (issue #29); confirm the fix is in your pinned version
- Non-lxml treebuilder output (etree/dom/soup) needed -- those re-walk the tree in Python and lose most of the C-vs-C speed advantage

## How it is fast

Tokenizes and builds a parse tree in C using a modified copy of Google's gumbo-parser (vendored under gumbo/), then walks that gumbo tree once and constructs a libxml2 document directly in C (src/as-libxml.c) via an explicit stack-based traversal, before handing the finished xmlDoc to lxml with etree.adopt_external_document. This skips the extra Python-object-construction pass that gumbo's own Python bindings and BeautifulSoup-based stacks require, and skips html5lib's pure-Python tokenizer/tree-builder entirely.

## Compared with alternatives

Pick html5-parser when you specifically need HTML5-spec-correct parsing into a real lxml/libxml2 tree from Python and can accept lxml's --no-binary build constraint. If the goal is raw throughput against libxml2 itself rather than against html5lib, selectolax (Lexbor backend, \~3.8x faster than lxml.html directly in its own benchmark) or lexbor beat it outright.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | lxml &gt;= 3.8.0 (must be installed with --no-binary so it links dynamic libxml2), chardet (encoding-detection fallback), optional BeautifulSoup4 for treebuilder='soup' |
| **Minimum toolchain** | C99 compiler; setup.py compiles with -std=c99 -O3 -Wall -Werror -pedantic-errors on Unix, /O2 on Windows (MSVC via a dedicated win-ci.py script) |
| **Platforms** | Linux, macOS, Windows -- CI runs three OSes and four compilers per the README; no documented CPU-architecture restriction |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial -- explain: the output is a standard lxml Element like lxml.html.fromstring would give, but html5-parser and lxml must share the exact same dynamically-loaded libxml2 build, so a plain `pip install html5-parser` next to a normal binary lxml wheel fails at import |

## Gotchas

- Binary lxml wheels bundle a static libxml2; you must `pip install --no-binary lxml lxml` first or you get a RuntimeError citing mismatched LIBXML_VERSION at import
- sanitize_names defaults to True, silently rewriting non-ASCII-safe tag/attribute names to keep the tree valid XML -- turn it off if strict HTML5 spec fidelity matters more than XML-safety
- Only the lxml/lxml_html treebuilders are fast; etree, dom, and soup treebuilders are implemented in Python on top of the same parse and are correspondingly slower
- A fragment-parsing edge case at MathML integration points could infinite-loop (issue #29, filed and since closed) -- worth confirming on your pinned version if you parse untrusted fragments

## Caveats and trade-offs

The docs never compare against lxml.html/libxml2 directly; the 2x row is html5-parser-to-soup (1.685s) vs BeautifulSoup+lxml (3.826s), so the margin is BeautifulSoup overhead, not libxml2. selectolax's third-party benchmark (examples/benchmark.py, 754 pages) shows html5_parser slower than lxml.html used directly (16.10s vs 9.09s). html5-parser itself builds a libxml2 tree via lxml. The 35x/37x figures are against pure-Python html5lib. No CPU, OS, or compiler flags are stated, and it is a single ad hoc run on the author's machine.

Uses gumbo internally then rebuilds a libxml2-compatible tree, so it needs a compiled C extension; not a pure drop-in for lxml's own HTML parser API.

## Maintenance

Actively maintained (last commit 2026-09-20) and used in production inside calibre despite a small following (706 stars); Apache-2.0 and a compact C codebase, but the requirement to build lxml against a matching dynamic libxml2 makes it harder to vendor cleanly than a header-only or wheel-friendly library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party benchmark.py output in the docs (5,956,815-byte file; html5-parser 0.397s vs html5lib 13.906s, BeautifulSoup+html5lib 12.683s, BeautifulSoup+lxml 3.826s; speedup table 35/8/2; '37x') with public script benchmark.py but no CPU, OS, or compiler flags, so C.
- **Verifier notes:** Numbers match the docs exactly. The real win is vs html5lib and BeautifulSoup, not vs libxml2. selectolax's README shows lxml (libxml2) beating html5_parser, so I moved the baseline to html5lib and set baseline_in_list=false. Metadata checks out: Apache-2.0, 706 stars, last commit 2026-09-20.
- **Fields the verifier corrected:** `baseline`, `baseline_in_list`, `caveats`
- **Pages the verifier opened:**
  - <https://html5-parser.readthedocs.io/en/latest/index.html>
  - <https://github.com/kovidgoyal/html5-parser>
  - <https://github.com/kovidgoyal/html5-parser/blob/master/docs/index.rst>
  - <https://github.com/kovidgoyal/html5-parser/blob/master/benchmark.py>
  - <https://github.com/rushter/selectolax#simple-benchmark>
  - <https://github.com/rushter/selectolax/blob/master/examples/benchmark.py>
- **Sources the enricher read:**
  - <https://github.com/kovidgoyal/html5-parser>
  - <https://github.com/kovidgoyal/html5-parser/blob/master/README.rst>
  - <https://github.com/kovidgoyal/html5-parser/blob/master/docs/index.rst>
  - <https://github.com/kovidgoyal/html5-parser/blob/master/src/html5_parser/__init__.py>
  - <https://github.com/kovidgoyal/html5-parser/blob/master/setup.py>
  - <https://github.com/kovidgoyal/html5-parser/blob/master/src/as-libxml.c>
  - <https://github.com/kovidgoyal/html5-parser/issues>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/kovidgoyal/html5-parser`) · [data/wave3/enrich/raw/github_com_kovidgoyal_html5_parser.json](../../../data/wave3/enrich/raw/github_com_kovidgoyal_html5_parser.json) (enrichment confidence 0.5)

</details>
