# MarkupEver

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [HTML, Markdown and markup](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust (Python bindings)` · `MPL-2.0` · 🟢 active

> Rust HTML/XML parser with CSS selection for Python; faster than BeautifulSoup4 and html5lib, slower than lxml-based Parsel.

| | |
|---|---|
| **Beats** | BeautifulSoup4 (html.parser and lxml backends) and html5lib |
| **Claimed result** | vs BeautifulSoup4(lxml): parse 4,927us vs 22,809us \~4.6x; CSS select 310us vs 2,995us \~9.7x; serialize 1,952us vs 14,900us \~7.6x (all derived from page data). On the same page, Parsel (which uses lxml/libxml2 directly) beats MarkupEver in all three: parse 4,072us vs 4,927us, select 161us vs 310us, serialize 1,276us vs 1,952us. |
| **Workload** | Parse, CSS-select, and serialize a test HTML document; average microseconds per operation measured for BeautifulSoup(html.parser), BeautifulSoup(lxml), Parsel, html5lib, and MarkupEver. |
| **Metric** | latency |
| **Hardware** | Manjaro Linux x86_64, 8GB RAM, Intel Core i3-1115G4 |
| **Adoption** | 37 stars; small/early-stage project |
| **Last commit** | 2026-07-21 |
| **Links** | [repository](https://github.com/awolverp/markupever) · [benchmark](https://awolverp.github.io/markupever/#performance) |

## Verdict

On the maintainer's own micro-benchmark (Manjaro Linux x86_64, 8GB RAM, Intel i3-1115G4; Python version and compiler flags unstated), MarkupEver parsed a test HTML page in 4,927us avg vs BeautifulSoup4(lxml)'s 22,809us (\~4.6x) and html5lib's 63,489us; CSS-selected in 310us vs BeautifulSoup4's 2,995us (\~9.7x); and serialized in 1,952us vs BeautifulSoup4's 14,900us (\~7.6x). On the same table, Parsel (using lxml/libxml2 directly) beat MarkupEver on all three operations (4,072us parse, 161us select, 1,276us serialize).

## Use it when

- Parsing/selecting/serializing many small-to-medium HTML or XML documents from Python where BeautifulSoup4 or html5lib is the measured bottleneck
- Need CSS-selector querying (soupsieve-style syntax) without switching to XPath
- Building a DOM from scratch and serializing it (e.g. generating HTML), not just parsing existing markup
- Large or streamed input where incremental parsing via Parser.process() avoids buffering the whole document
- Deploying to Linux, Windows, or macOS with a prebuilt PyPI wheel - no local Rust toolchain needed

## Skip it when

- You already call lxml/Parsel directly - on the project's own benchmark table, Parsel beats MarkupEver on every measured operation (parse, select, serialize)
- You need the CSS :has() pseudo-class - an open issue says it does not work
- You need a BeautifulSoup-compatible API (Tag, NavigableString, .find()) - MarkupEver's dom/select API is different, so adopting it is a rewrite, not a swap
- You need airtight cross-thread sharing of parser objects - an unsound `impl Sync` on Tendril-based parser/matching types was reported (issue #10) and fixed later, but the exact fixed version is not documented
- You want independently reproduced numbers - only the maintainer's own benchmark exists, with no published benchmark code, no stated Python version, and no stated build flags

## How it is fast

Tokenizing and tree-building run through html5ever (Rust's spec-compliant HTML5 parser) and CSS matching uses servo's `selectors` crate, both compiled natively instead of going through Python's html.parser or the tree BeautifulSoup builds on top. The DOM is a single Vec-backed Rust tree (treedom crate), avoiding per-node Python object churn until a node is touched, and the release build uses fat LTO, one codegen unit, and panic=abort.

## Compared with alternatives

Pick MarkupEver over html5-parser when you also want CSS selection and DOM construction/serialization in the same library, not just fast HTML5-to-lxml-tree parsing; pick selectolax or Parsel/lxml directly instead when you don't need MarkupEver's DOM-building API, since both outperform MarkupEver on this same class of parse/select/serialize benchmark.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Rust build deps only (pyo3 0.29, parking_lot 0.12, hashbrown 0.17, plus html5ever/selectors pulled in via the treedom and matching workspace crates); Python runtime has no extra dependencies |
| **Minimum toolchain** | Rust edition 2021 (build-time only, via maturin); Python &gt;=3.8, with wheels published for CPython 3.9-3.14 and PyPy - no Rust toolchain needed to install from PyPI |
| **Platforms** | Linux, Windows, macOS per PyPI classifiers; benchmarked on x86-64 (Manjaro), no documented architecture restriction |
| **Thread safety** | README claims 'completely thread-safe', but issue #10 found the `impl Sync` on Tendril-based parser/matching types unsound (non-atomic refcount under concurrent access); addressed by later 'remove unsafe blocks' PRs, exact fixed version not documented |
| **Drop-in for the baseline** | partial — explain: same parse -&gt; select -&gt; serialize workflow as BeautifulSoup4, but a different, non-object-compatible API (TreeDom/dom.Document, select()/select_one()) |

## Gotchas

- CSS :has() pseudo-class does not work (open issue, unresolved as of this session)
- Historical unsound Sync impl on parser/matching types tied to html5ever's Tendril type (issue #10) - fixed later, but pin a recent version if you share parser objects across threads
- A separate 'attaching a node to itself causes crash' bug was reported and closed - confirm you're past that fix
- pyproject.toml's PyPI classifier lists the license as MIT while the actual LICENSE file and Cargo.toml both say MPL-2.0 - a metadata inconsistency, not an alternate license grant

## Caveats and trade-offs

On its own benchmark table MarkupEver is slower than Parsel, which the page says directly uses lxml (libxml2), in parsing, selecting, and serializing. The win is only over BeautifulSoup4's Python tree layer and html5lib, not over libxml2. The benchmark code is not published, the test document is not described, and Python version and build flags are not stated. Only the project's own numbers exist, with no independent reproduction.

Built on html5ever + servo's selectors crate internally, so the measured gap is Rust-native-code vs Python-wrapped-libxml2, not a new parsing algorithm; requires a compiled Rust extension for Python users.

## Maintenance

Actively maintained (last commit 2026-07-21, CI running on push) and MPL-2.0 licensed, but it's a compiled PyO3/maturin extension rather than a source-drop, and it's a small, largely single-author project (37 stars) with an unresolved CSS-selector gap and a past thread-safety soundness bug, so treat it as promising but young.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party min/max/avg table on the docs page (CPU stated: Intel i3-1115G4, Manjaro), but no benchmark code in the repo (the only match in the tree is docs/docs/index.md), no Python version, and no build flags, so C.
- **Verifier notes:** Numbers match the page. The libxml2 baseline is wrong: the libxml2-direct wrapper (Parsel) on the same page is faster, so I re-pointed the baseline to BeautifulSoup4/html5lib. The orchestrator may want to decide whether a 'faster than BeautifulSoup' entry is in scope. Metadata checks out: MPL-2.0, 37 stars, last commit 2026-07-21.
- **Fields the verifier corrected:** `baseline`, `baseline_in_list`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://awolverp.github.io/markupever/#performance>
  - <https://github.com/awolverp/markupever>
  - <https://github.com/awolverp/markupever/blob/master/docs/docs/index.md>
- **Sources the enricher read:**
  - <https://github.com/awolverp/markupever>
  - https://github.com/awolverp/markupever (README, via gh api repos/.../readme)
  - <https://github.com/awolverp/markupever/blob/master/Cargo.toml>
  - <https://github.com/awolverp/markupever/blob/master/pyproject.toml>
  - <https://github.com/awolverp/markupever/blob/master/docs/docs/index.md>
  - <https://awolverp.github.io/markupever/#performance>
  - <https://github.com/awolverp/markupever/blob/master/docs/docs/querying.md>
  - <https://github.com/awolverp/markupever/issues>
  - <https://github.com/awolverp/markupever/issues/10>
  - <https://github.com/awolverp/markupever/blob/master/LICENSE>
  - https://github.com/awolverp/markupever/git/trees/HEAD (file tree)
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/awolverp/markupever`) · [data/wave3/enrich/raw/github_com_awolverp_markupever.json](../../../data/wave3/enrich/raw/github_com_awolverp_markupever.json) (enrichment confidence 0.55)

</details>
