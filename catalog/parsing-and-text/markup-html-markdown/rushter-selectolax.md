# selectolax

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [HTML, Markdown and markup](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python (Cython bindings to C engines)` · `MIT` · 🟢 active

> Cython bindings to the Lexbor/Modest C HTML5 engines, giving CSS-selector DOM parsing faster than lxml/libxml2.

| | |
|---|---|
| **Beats** | libxml2 (via lxml.html.fromstring used directly) |
| **Claimed result** | BeautifulSoup(html.parser) 61.02s; lxml 9.09s; html5_parser 16.10s; selectolax(Modest) 2.94s; selectolax(Lexbor) 2.39s. selectolax(Lexbor) is \~3.8x faster than lxml (libxml2) and \~25x faster than BeautifulSoup(html.parser); Modest is \~3.1x faster than lxml (derived from page data). |
| **Workload** | Extract title, link hrefs, script-tag count, and meta description from the homepages of the top 754 domains (324MB of HTML per examples/benchmark.py); total wall-clock time (time.time()) per parser over the corpus. |
| **Metric** | throughput |
| **Adoption** | 1.68k stars; widely used in Python web-scraping stacks |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/rushter/selectolax) · [benchmark](https://github.com/rushter/selectolax#simple-benchmark) |

## Verdict

On a 324MB corpus of 754 top-domain homepages (extracting title, `a[href]`s, script-tag count, and meta description), selectolax(Lexbor) ran in 2.39s and selectolax(Modest) in 2.94s versus lxml.html.fromstring+XPath used directly at 9.09s (\~3.8x and \~3.1x faster respectively) and BeautifulSoup(html.parser) at 61.02s. This is a single wall-clock run with no CPU, compiler, or flags stated, and the corpus itself is unpublished due to copyright.

## Use it when

- Scraping/extraction pipelines that are CPU-bound on parsing large volumes of HTML and only need to read specific fields, not mutate the tree heavily
- You're fine writing to selectolax's own CSS-selector API instead of XPath or BeautifulSoup's find/find_all
- You want HTML5-spec error recovery (like a browser) without a full browser or html5lib
- CPython 3.9–3.14 environments (per pyproject `requires-python`), Linux/macOS/Windows
- You explicitly use the Lexbor backend (`LexborHTMLParser`) rather than the legacy Modest one

## Skip it when

- You need a free-threaded (no-GIL) Python build — support is requested but still open (issue #215, opened 2026-03-18)
- Workload is XPath-driven or needs heavy DOM mutation/serialization — the verified benchmark only covers read-only field extraction
- You want the Modest backend for new code — the project itself says the underlying Modest C library is unmaintained and steers users to Lexbor
- You can't tolerate native-extension crash risk — past segfault under sustained load with `strip_tags()`+`text()` (#217) and memory corruption when deleting attributes (#172), both since fixed but indicative of the risk class
- You need XPath support at all — selectolax is CSS-selectors only, with a nonstandard `:lexbor-contains()` pseudo-class as its one extension

## How it is fast

The speedup comes from parsing in native, purpose-built HTML5 engines (Modest, and its successor Lexbor) rather than through libxml2's more general-purpose parser/tree machinery that lxml wraps, or Python-level parsing in BeautifulSoup's html.parser backend. Cython binds directly to the C node structures for traversal and CSS matching instead of materializing a heavier Python object per node. The published benchmark exercises light extraction (title, `a[href]`, script count, one meta tag) over 754 pages, not full tree mutation or serialization, so the win is concentrated in parse + shallow query, not general DOM editing.

## Compared with alternatives

Pick selectolax over raw lexbor when you want a maintained, widely-used (1.68k stars) Python package instead of hand-rolling FFI bindings to the C library yourself. Pick it over html5-parser when you don't need the output as an lxml tree — html5-parser deliberately produces an lxml-compatible tree so you can keep using XPath, which selectolax does not support. MarkupEver's published numbers are on microsecond-scale document sizes versus this benchmark's multi-second, 324MB corpus, so the two aren't directly comparable without testing on your own data.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime; Cython + setuptools&gt;=62.4 needed only to build from source (wheels ship prebuilt) |
| **Minimum toolchain** | Python &gt;=3.9,&lt;3.15 (CPython); Cython for source builds |
| **Platforms** | Linux, macOS, Windows (per PyPI classifiers); no free-threaded/no-GIL build yet |
| **Thread safety** | not documented in README; free-threaded Python support is an open, unresolved issue (#215) |
| **Drop-in for the baseline** | partial — explain: same job as lxml.html.fromstring (parse + query HTML), but different classes (HTMLParser/LexborHTMLParser) and CSS-selector-only API instead of XPath, so call sites must be rewritten |

## Gotchas

- Two backends (Modest, Lexbor) with overlapping but not identical features; Lexbor is the recommended one since 2024 but isn't used by every example/class by default — check which parser you import
- Backend licenses differ from the package license: Modest is LGPL-2.1 and Lexbor is Apache-2.0, even though selectolax itself is MIT
- Native-extension bugs have caused a SIGSEGV under sustained load (`strip_tags()`+`text()`, v0.4.8, issue #217) and memory corruption when deleting attributes (issue #172) — both closed/fixed, but crashes bypass normal Python exception handling
- No XPath; only CSS selectors plus the Lexbor-specific `:lexbor-contains()` pseudo-class for text matching

## Caveats and trade-offs

The 'lxml' row is lxml.html.fromstring plus XPath used directly, not BeautifulSoup(lxml), which makes it a direct libxml2 comparison. No CPU, compiler, or flags are stated. It is a single wall-clock run, not averaged trials. The corpus is unpublished because of copyright (per the comment in benchmark.py), so it cannot be reproduced exactly. The bundled Modest engine is LGPL-2.1 and lexbor is Apache-2.0.

Python/Cython call overhead remains vs raw C; default Modest backend engine is itself unmaintained (project now recommends the Lexbor backend); benchmark task is light DOM extraction, not full traversal or mutation.

## Maintenance

Actively maintained (last commit 2026-09-24, CI passing, Python 3.9-3.14 support) and MIT-licensed, but the bundled Modest engine is itself unmaintained upstream, so new code should target the Lexbor backend; free-threaded-Python support remains an open request.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The README table comes from the public examples/benchmark.py, but the 754-page corpus is unpublished and no CPU, compiler, or flags are stated, so C.
- **Verifier notes:** Numbers match the README. I checked examples/benchmark.py: the 9.09s row is lxml used directly, so the record's claim is stronger than it stated. Metadata checks out: MIT, 1,680 stars, last commit 2026-09-24.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/rushter/selectolax#simple-benchmark>
  - <https://github.com/rushter/selectolax>
  - <https://github.com/rushter/selectolax/blob/master/examples/benchmark.py>
- **Sources the enricher read:**
  - <https://github.com/rushter/selectolax>
  - <https://github.com/rushter/selectolax#simple-benchmark>
  - <https://github.com/rushter/selectolax/blob/master/examples/benchmark.py>
  - <https://github.com/rushter/selectolax/blob/master/pyproject.toml>
  - <https://github.com/rushter/selectolax/issues/215>
  - <https://github.com/rushter/selectolax/issues/194>
  - <https://github.com/rushter/selectolax/issues/217>
  - <https://github.com/rushter/selectolax/issues/172>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/rushter/selectolax`) · [data/wave3/enrich/raw/github_com_rushter_selectolax.json](../../../data/wave3/enrich/raw/github_com_rushter_selectolax.json) (enrichment confidence 0.6)

</details>
