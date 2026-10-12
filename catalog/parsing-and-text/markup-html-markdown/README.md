# HTML, Markdown and markup

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md)</sub>

**What these beat:** libxml2, gumbo, cmark, html5ever  
**11 entries:** 1 tier A · 2 tier B · 8 tier C · 0 tier D · 11 copyable, 0 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**lexbor**](lexbor-lexbor.md) | Standards-compliant C99 HTML5/CSS/DOM/URL engine; beats libxml2-based bindings on HTML parsing and CSS selector throughput. | **A** | C | Apache-2.0 | 🟢 active |
| 2 | [**Discount**](orc-discount.md) | C Markdown-to-HTML library and CLI implementing original Markdown.pl syntax; converts orders of magnitude faster than Markdown.pl. | **B** | C | BSD-3-Clause | 🟢 active |
| 3 | [**Hoedown**](hoedown-hoedown.md) | Callback-driven C Markdown-to-HTML library (Sundown fork); edged out cmark 0.21 s vs 0.29 s in cmark's own 2015-era benchmark. | **B** | C | ISC | 🔴 abandoned |
| 4 | [**pugixml**](zeux-pugixml.md) | In-place, allocation-light C++ XML DOM parser with XPath 1.0, beating libxml2 on parse throughput. | **C** | C++ | MIT | 🟢 active |
| 5 | [**selectolax**](rushter-selectolax.md) | Cython bindings to the Lexbor/Modest C HTML5 engines, giving CSS-selector DOM parsing faster than lxml/libxml2. | **C** | Python | MIT | 🟢 active |
| 6 | [**MD4C**](mity-md4c.md) | SAX-style CommonMark parser in C, no AST, beats cmark on speed and memory when you don't need a DOM. | **C** | C | MIT | 🟢 active |
| 7 | [**html5-parser**](kovidgoyal-html5-parser.md) | C extension pairing a gumbo-derived HTML5 tokenizer with a direct-to-libxml2 tree build; far faster than pure-Python html5lib. | **C** | C | Apache-2.0 | 🟢 active |
| 8 | [**roxmltree**](razrfalcon-roxmltree.md) | Read-only, zero-copy Rust XML DOM parser; 2-3.5x faster than libxml2, no mutation or writing. | **C** | Rust | Apache-2.0 OR MIT | 🟢 active |
| 9 | [**MarkupEver**](awolverp-markupever.md) | Rust HTML/XML parser with CSS selection for Python; faster than BeautifulSoup4 and html5lib, slower than lxml-based Parsel. | **C** | Rust | MPL-2.0 | 🟢 active |
| 10 | [**stb_xml**](ferki-git-creator-stb-xml.md) | Single-header, zero-allocation XML tokenizer for C; beats libxml2's DOM parser on raw throughput. | **C** | C | BSD-3-Clause | 🟢 active |
| 11 | [**MyHTML**](lexborisov-myhtml.md) | Pure C99 HTML5 parser using a thread-pool tokenizer/tree-builder; beats Gumbo and html5ever on parse throughput. | **C** | C | LGPL-2.1 | 🟡 stale |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
