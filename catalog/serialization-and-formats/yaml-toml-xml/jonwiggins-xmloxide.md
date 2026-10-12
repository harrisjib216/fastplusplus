# xmloxide

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [YAML, TOML and XML](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Pure-Rust libxml2 reimplementation: parsing at libxml2 parity, self-reported 1.5-2.4x faster serialization and 1.1-2.7x faster XPath.

| | |
|---|---|
| **Beats** | libxml2 |
| **Claimed result** | Parsing roughly parity to slightly slower than libxml2 (176 vs 184 MiB/s on Atom feed, \~4% slower; 103 vs 92 MiB/s on SVG, 12% faster; 142 vs 148 MiB/s on Maven POM, \~4% slower; 139 vs 157 MiB/s on XHTML, \~13% slower; 169 vs 175 MiB/s on 374KB doc, \~3% slower); serialization 1.5-2.4x faster; XPath evaluation 1.1-2.7x faster (attribute predicates up to 2.7x) |
| **Workload** | Criterion benchmarks (benches/comparison_bench.rs) against libxml2 through the Rust `libxml` 0.3 bindings. Parsing covers Atom feed 4.9 KB, SVG 6.3 KB, Maven POM 11.5 KB, XHTML 10.2 KB and a runtime-generated \~374 KB 2000-record document. Serialization covers Atom, Maven POM and the large document. XPath covers four expressions on the Atom and Maven POM fixtures. |
| **Metric** | throughput |
| **Compiler and flags** | rustc version unstated; Cargo.toml [profile.bench] lto="thin", codegen-units=1 |
| **Adoption** | 86 stars; 56,833 crates.io downloads (26,714 recent; xmloxide 0.5.0) |
| **Last commit** | 2026-08-08 |
| **Links** | [repository](https://github.com/jonwiggins/xmloxide) · [benchmark](https://github.com/jonwiggins/xmloxide/blob/main/README.md) |

## Verdict

The project's own Criterion benchmarks compare against libxml2 through the Rust libxml crate (0.3.8 in Cargo.lock), built with thin LTO and codegen-units=1; CPU, rustc and libxml2 versions are not stated, and the README numbers date from 2026-02-28, before 0.1.0, and were not re-run for 0.5.0. They show parsing at 0.89-1.12x libxml2 on five 4.9-374 KB documents, serialization 1.5-2.4x faster, and XPath 1.08-2.7x faster. The libxml2 side of the serialization benchmark adds xmlSaveToBuffer plus a CStr-to-String lossy copy. The XPath queries are unprefixed names on default-namespaced Atom and POM fixtures, so under XPath 1.0 rules libxml2 matches nothing while xmloxide matches by local name; the benchmark never checks that both sides return the same results.

## Use it when

- Rust (or C via the FFI) code that needs libxml2's breadth — validation, XPath, C14N, XInclude, catalogs, HTML — without linking the C library, which the README says has been unmaintained since December 2025.
- Serialization-heavy pipelines (parse or build a DOM, then emit XML), where the README shows 1.5-2.4x faster output than libxml2 on 4.9-374 KB documents.
- Parsing many independent documents across threads: there is no global init or state, and Document is Send + Sync.
- Parsing XML and WHATWG HTML5 (100% of html5lib-tests) through one crate and one tree API; libxml2 has no HTML5 parser.
- Workloads where parse speed only needs to match libxml2: parsing is 0.89-1.12x libxml2's speed on the project's own fixtures.

## Skip it when

- When raw parse throughput is the goal: 4 of 5 README parse benchmarks are 3-13% slower than libxml2, and faster Rust parsers exist.
- Truly incremental parsing of large inputs: PushParser buffers all pushed data and parses only on finish(). Use SAX instead.
- Evaluating untrusted XPath expressions: open issue #51 reports that a few thousand nested parentheses overflow the stack and abort the process in 0.5.0.
- RelaxNG-heavy validation: issues #52-#57 are open (&lt;div&gt; not traversed, combine= ignored for same-named defines, prefixed-name shorthand not resolved, attributes behind &lt;ref&gt; in interleave never matched, no compact syntax).
- XML 1.1, XSLT, custom entity loaders, custom error handlers, or code that dereferences libxml2 node structs: none of these are supported.

## How it is fast

The DOM is an arena: one Vec&lt;NodeData&gt; indexed by NonZeroU32 NodeIds with parent, first/last-child and sibling links. Serialization is a single pre-order walk that pushes into one String with a char-by-char escaper. The parser is hand-written recursive descent over UTF-8 bytes, with scalar bulk scans for text and attribute values, ASCII fast paths for names and built-in entities, and a byte pre-check for invalid characters; it uses no SIMD and no memchr. XPath fuses a `//` step and the child step after it into one descendant step, inlines name tests on the child and descendant axes, and short-circuits literal positional predicates. The README also claims string interning, but the tree does not use it: element names, prefixes and namespace URIs are owned Strings, and the Dict/SymbolId interner is referenced only in src/util/dict.rs.

## Compared with alternatives

Pick xmloxide over quick-xml or SupXML when you need libxml2's whole feature set (validation, XPath, C14N, XInclude, HTML4/HTML5, SAX/reader/push, C FFI) in safe Rust rather than raw speed: SupXML reports \~2.1x libxml2's DOM parse speed and quick-xml leads the bemayer benchmark, while xmloxide only matches libxml2 at parsing. Compared with rusty_xml, the other Rust libxml2 remake (1.55-2.31x on xmllint parse-noout), xmloxide's speed case rests on serialization and XPath, not parsing.

## Integration

| | |
|---|---|
| **Form** | crate (also a cdylib/staticlib through the Makefile with the `ffi` feature; the repo also has Python (PyO3) and WASM subcrates) |
| **Dependencies** | encoding_rs only for the library. The default `cli` feature pulls in clap, so library users should set default-features = false. Optional: serde, tokio (async), libxml (benchmarks only). |
| **Minimum toolchain** | Rust 1.81 (MSRV, edition 2021) |
| **Platforms** | Any Rust target as far as documented. The code is pure Rust and the parser scanner has no architecture-specific or SIMD paths; a WASM bindings subcrate exists. |
| **Thread safety** | No global state; Document is Send + Sync and mutation needs &mut Document. The FFI keeps its last-error state in thread-local storage. MIGRATION.md says a document shared across threads needs a mutex. |
| **Drop-in for the baseline** | partial — the C FFI plus libxml2_compat.h maps common libxml2 names (xmlReadMemory, xmlDocGetRootElement, xmlXPathEval, ...). Nodes are opaque (doc, id) handles, so there is no node-&gt;name or node-&gt;children access. Every handle and returned string must be freed, and there are no parser contexts, error handlers or entity loaders. The Rust API is not libxml2-shaped. |

## Gotchas

- XPath name tests ignore namespaces unless you register prefixes. An unprefixed test like //entry matches on local name only (the matches_element_name fallback), so it finds Atom-namespaced &lt;entry&gt; elements where libxml2 and XPath 1.0 return an empty set. Namespace-sensitive queries ported from libxml2 can return different results.
- Inferred from reading src/xpath/eval.rs, not run: try_fuse_descendant_child rewrites descendant-or-self::node()/child::X[pred] into descendant::X[pred] and copies the predicates unconditionally. //b[1] therefore looks like it returns only the first b in the document, not the first b child of each parent; XPath 1.0 §2.5 notes that //para[1] is not /descendant::para[1].
- Default ParseOptions limits: nesting depth 256, 256 attributes per element, 10 MB per text node or attribute value, and 10,000 entity expansions. Large or unusual documents need these raised explicitly.
- The API is pre-1.0 and changing. In 0.5.0 XPathValue::NodeSet switched to XPathNode entries, attribute paths stopped collapsing to String, and a new Expr::FilterPath variant was added. Use ≥0.5.0 anyway: 0.4.4 fixed CVE-2026-61727 (stack overflow from nested DTD content models), and 0.5.0 fixed an exponential-time entity recursion check.

## Known shortcomings

- Parsing is not a win (faster on only 1 of 5 documents); the wins are serialization (1.5-2.4x) and XPath (1.1-2.7x), and libxml2 is called through the Rust libxml wrapper, which adds overhead on its side. The README's 2.7x XPath row is labelled with a different query than the code runs. No CPU, rustc or libxml2 version.
- The XPath comparison likely compares different outputs: the Atom and POM fixtures declare a default namespace, so under XPath 1.0 libxml2 should match nothing for the unprefixed queries while xmloxide matches on local name, and the bench never checks results (source reading). Serialization baseline includes libxml-crate copy overhead. README tables predate 0.3-0.5 parser and XPath changes. //X[pred] is likely rewritten to descendant::X[pred], wrong for positional predicates. Deeply nested XPath parentheses abort the process (#51). Enrichment confidence 0.5.

## Caveats and trade-offs

No CPU model, rustc version or libxml2 version disclosed. Self-reported by the project. libxml2 is driven through the Rust `libxml` crate wrapper, so serialization (libxml_doc.to_string()) and XPath (Context::evaluate) include wrapper and conversion overhead on the libxml2 side. The README labels the 2.7x XPath row 'Attribute predicate (//book[@id])', but comparison_bench.rs actually runs //dependency[scope='test'] on the Maven POM. Parsing is not a win: 4 of 5 documents parse at or below libxml2 speed (only SVG is 12% faster), so the speed claim rests on serialization (1.5-2.4x) and XPath (1.08-2.7x). The 'Large' document is synthetic (make_large_xml).

Pure Rust reimplementation described by its author as 'agent-made' (AI-assisted); not a full libxml2 API-compatible drop-in (has its own MIGRATION.md); benchmark code exists (benches/comparison_bench.rs) but results are mixed, with parsing sometimes slower than libxml2 despite faster serialization and XPath

## Maintenance

Actively released: more than a dozen crates.io versions from 0.1.x (2026-03-01) to 0.5.0 (2026-08-08), about 57k downloads and 4 reverse dependencies. It is MIT-licensed, maintained by a single author with an AI coding agent (the repo carries CLAUDE.md and .claude/skills), and still pre-1.0 with recent breaking XPath changes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** README Performance section has Criterion tables against libxml2 from public bench code (benches/comparison_bench.rs, run with cargo bench --features bench-libxml2), with a bench profile of lto=thin and codegen-units=1 in Cargo.toml. It gives no CPU model, rustc version or libxml2 version, so it is first-party C, not A.
- **Verifier notes:** Every number in claimed_speedup matches the README tables exactly. XPath 'simple path' is only 8% faster (1.51 vs 1.63 us), which the README rounds into '1.1-2.7x'. Metadata checked via gh is correct (MIT, 86 stars, last commit 2026-08-08, active, not a fork). SupXML's head_to_head.rs also benchmarks against xmloxide, but that does not change this record.
- **Fields the verifier corrected:** `workload`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/jonwiggins/xmloxide/blob/main/README.md>
  - <https://github.com/jonwiggins/xmloxide>
  - <https://github.com/jonwiggins/xmloxide/blob/main/benches/comparison_bench.rs>
  - <https://github.com/jonwiggins/xmloxide/blob/main/Cargo.toml>
  - <https://crates.io/api/v1/crates/xmloxide>
- **Sources the enricher read:**
  - <https://github.com/jonwiggins/xmloxide>
  - <https://github.com/jonwiggins/xmloxide/blob/main/README.md>
  - <https://github.com/jonwiggins/xmloxide/blob/main/Cargo.toml>
  - <https://github.com/jonwiggins/xmloxide/blob/main/Cargo.lock>
  - <https://github.com/jonwiggins/xmloxide/blob/main/benches/comparison_bench.rs>
  - <https://github.com/jonwiggins/xmloxide/blob/main/benches/fixtures/atom_feed.xml>
  - <https://github.com/jonwiggins/xmloxide/blob/main/benches/fixtures/maven_pom.xml>
  - <https://github.com/jonwiggins/xmloxide/blob/main/benches/fixtures/svg_drawing.xml>
  - <https://github.com/jonwiggins/xmloxide/blob/main/benches/fixtures/xhtml_page.xml>
  - <https://github.com/jonwiggins/xmloxide/blob/main/MIGRATION.md>
  - <https://github.com/jonwiggins/xmloxide/blob/main/CHANGELOG.md>
  - <https://github.com/jonwiggins/xmloxide/blob/main/CLAUDE.md>
  - <https://github.com/jonwiggins/xmloxide/blob/main/Makefile>
  - <https://github.com/jonwiggins/xmloxide/blob/main/include/libxml2_compat.h>
  - <https://github.com/jonwiggins/xmloxide/blob/main/src/lib.rs>
  - <https://github.com/jonwiggins/xmloxide/blob/main/src/tree/mod.rs>
  - <https://github.com/jonwiggins/xmloxide/blob/main/src/tree/node.rs>
  - <https://github.com/jonwiggins/xmloxide/blob/main/src/parser/mod.rs>
  - <https://github.com/jonwiggins/xmloxide/blob/main/src/parser/input.rs>
  - <https://github.com/jonwiggins/xmloxide/blob/main/src/parser/xml.rs>
  - <https://github.com/jonwiggins/xmloxide/blob/main/src/util/dict.rs>
  - <https://github.com/jonwiggins/xmloxide/blob/main/src/serial/xml.rs>
  - <https://github.com/jonwiggins/xmloxide/blob/main/src/xpath/eval.rs>
  - <https://github.com/jonwiggins/xmloxide/blob/main/src/xpath/parser.rs>
  - <https://github.com/jonwiggins/xmloxide/blob/main/src/ffi/mod.rs>
  - <https://github.com/jonwiggins/xmloxide/blob/main/tests/libxml2-compat/BASELINE.md>
  - <https://github.com/jonwiggins/xmloxide/commits/main>
  - <https://github.com/jonwiggins/xmloxide/commits/main/README.md>
  - <https://github.com/jonwiggins/xmloxide/commit/75f6ed2>
  - <https://github.com/jonwiggins/xmloxide/issues>
  - <https://github.com/jonwiggins/xmloxide/issues/50>
  - <https://github.com/jonwiggins/xmloxide/issues/51>
  - <https://api.github.com/search/code?q=SymbolId+repo:jonwiggins/xmloxide>
  - <https://crates.io/api/v1/crates/xmloxide>
  - <https://crates.io/api/v1/crates/xmloxide/reverse_dependencies>
  - <https://github.com/KWARC/rust-libxml/blob/0.3.8/src/tree/document.rs>
  - <https://github.com/KWARC/rust-libxml/blob/0.3.8/src/parser.rs>
  - <https://github.com/KWARC/rust-libxml/blob/v0.3.16/src/tree/document.rs>
  - <https://github.com/KWARC/rust-libxml/blob/v0.3.16/src/parser.rs>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/jonwiggins/xmloxide`) · [data/wave4/enrich/raw/github_com_jonwiggins_xmloxide.json](../../../data/wave4/enrich/raw/github_com_jonwiggins_xmloxide.json) (enrichment confidence 0.5)

</details>
