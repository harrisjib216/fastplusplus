# roxmltree

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [HTML, Markdown and markup](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Read-only, zero-copy Rust XML DOM parser; 2-3.5x faster than libxml2, no mutation or writing.

| | |
|---|---|
| **Beats** | libxml2 |
| **Claimed result** | roxmltree faster than libxml2 across all four sizes (derived from page data): huge 2,997,887 ns vs 6,850,666 ns (\~2.28x); large 1,494,886 ns vs 3,250,606 ns (\~2.17x); medium 421,137 ns vs 950,984 ns (\~2.26x); tiny 2,522 ns vs 8,931 ns (\~3.54x). |
| **Workload** | Parse XML documents of four sizes (tiny/medium/large/huge) into a read-only DOM tree using `cargo bench`, comparing roxmltree against libxml2, sxd-document, and xmltree. |
| **Metric** | throughput |
| **Compiler and flags** | `cargo bench --features=libxml` using the `bencher` crate (libtest-style ns/iter output, not criterion); libxml2 called via the rust `libxml` 0.3.1 bindings (Parser::default().parse_string). The rustc version, flags and libxml2 version/build are not stated. |
| **Adoption** | 537 stars |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/RazrFalcon/roxmltree) · [benchmark](https://github.com/RazrFalcon/roxmltree#performance) |

## Verdict

On an Apple M1 Pro, using `cargo bench` with the bencher/libtest harness, roxmltree parsed four synthetic XML sizes 2.2-2.3x faster than libxml2 (called via the rust-libxml FFI crate) for medium/large/huge files and \~3.5x faster for tiny files; no rustc version, compiler flags, or libxml2 version are stated.

## Use it when

- Read-only extraction/querying from well-formed, UTF-8 XML (config files, SVG, feeds, data interchange)
- Latency- or throughput-sensitive parsing of small-to-large (not multi-GB) documents where libxml2 FFI overhead matters
- Pure-Rust builds that must avoid a C dependency or unsafe code (no_std-compatible via memchr)
- Workloads needing exact source position tracking per node/attribute for diagnostics (positions feature)
- One-shot parse-then-read pipelines where no later edit/round-trip-serialize step is needed

## Skip it when

- Any workflow that mutates the tree or writes XML back out — not supported at all
- Documents needing DTD resolution/validation — DTD support is not complete
- Non-UTF-8 input — not supported (libxml2 handles this)
- Very large documents where memory is tight: peak RAM runs \~6-8x file size (author's own 1.1GB file measurement: 7.6GB peak)
- HTML or non-well-formed markup — no HTML mode, unlike libxml2

## How it is fast

Node/attribute names, text, comments, and processing instructions are kept as Range&lt;usize&gt; slices into the original input buffer instead of being allocated and copied, so the tree is largely zero-copy. The tree itself is a flat, vector-backed arena (a modified version of the ego-tree crate) rather than a pointer-chasing linked structure. Scanning uses the memchr crate for fast byte search, and the crate forbids unsafe code and supports no_std, avoiding both libxml2's own allocator/type-conversion layer and the FFI marshalling overhead the benchmark's rust-libxml bindings add on the libxml2 side.

## Compared with alternatives

Pick roxmltree over pugixml or lexbor/libxml2 when you need a pure-Rust, no-unsafe, no-C-dependency parser for read-only XML querying and don't need mutation, writing, DTD, or HTML support; pick pugixml or lexbor instead when you need in-place tree editing, serialization, or HTML parsing.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | memchr (sole dependency; the README's own alternatives table lists roxmltree as having 0 dependencies, which conflicts with Cargo.toml) |
| **Minimum toolchain** | Rust 1.60+ (edition 2021) |
| **Platforms** | any (pure Rust, no_std-compatible, no arch-specific requirements documented) |
| **Thread safety** | not documented explicitly; the parsed tree is read-only/immutable after Document::parse |
| **Drop-in for the baseline** | partial — same read-only DOM-query idea as libxml2 but a different, iterator-based Rust API, and it drops mutation, writing, DTD, and HTML support |

## Gotchas

- Disabling the `positions` feature saves 8 bytes/node and part of the attribute overhead but removes original-document position tracking
- README's benchmark tables are internally inconsistent: huge_roxmltree is 2,997,887 ns/iter in the libxml2 comparison table but 3,147,424 ns/iter in the streaming-parser table, where huge_quick_xml instead shows exactly 2,997,887 ns/iter — looks like a copy-paste slip in one of the two tables
- Project states any panic is a critical bug to report, i.e. panics are not expected/allowed even on malformed input
- libxml2 in this benchmark is driven through the `rust-libxml` FFI wrapper crate, not called natively, so its measured time includes binding overhead

## Caveats and trade-offs

Benchmark code is public (benches/xml.rs, not bench/xml.rs), but the README states no CPU model, rustc/libxml2 versions, build flags or date, so it falls short of Tier A. libxml2 is driven through Rust FFI bindings (rust-libxml), so its time includes binding overhead. The README is internally inconsistent: huge_roxmltree is 2,997,887 ns in the libxml2 table but 3,147,424 ns in the quick-xml table, where huge_quick_xml shows exactly 2,997,887 ns (likely a copy-paste slip). The huge-file ratio is \~2.2-2.3x either way.

Read-only tree (no mutation or writing support), no unsafe code, no DTD support, roughly 6-8x memory overhead relative to file size; mimics lxml's parsing behavior rather than being fully spec-complete like libxml2.

## Maintenance

Actively maintained (last commit 2026-09-22, 537 stars) and dual MIT/Apache-2.0 licensed, small pure-Rust crate that's easy to vendor or pin.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** Benchmark code is public (benches/xml.rs, benches/Cargo.toml; libxml2 via the feature-gated rust `libxml` crate), but the README gives no CPU model, rustc version or flags, or libxml2 version, so it is first-party with partial methodology: C.
- **Verifier notes:** All four libxml2-vs-roxmltree numbers match the README, and the derived ratios are correct. The license 'Apache-2.0 OR MIT' is confirmed by Cargo.toml ('MIT OR Apache-2.0') and the LICENSE-MIT/LICENSE-APACHE files, even though GitHub's API reports only Apache-2.0. 537 stars, last commit 2026-09-22.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/RazrFalcon/roxmltree#performance>
  - <https://github.com/RazrFalcon/roxmltree/tree/master/benches>
  - <https://github.com/RazrFalcon/roxmltree/blob/master/benches/xml.rs>
  - <https://github.com/RazrFalcon/roxmltree/blob/master/benches/Cargo.toml>
  - <https://github.com/RazrFalcon/roxmltree/blob/master/Cargo.toml>
- **Sources the enricher read:**
  - <https://github.com/RazrFalcon/roxmltree>
  - <https://github.com/RazrFalcon/roxmltree#performance>
  - <https://github.com/RazrFalcon/roxmltree/blob/master/Cargo.toml>
  - <https://github.com/RazrFalcon/roxmltree/blob/master/src/lib.rs>
  - https://github.com/RazrFalcon/roxmltree/tree/master (recursive file listing)
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/razrfalcon/roxmltree`) · [data/wave3/enrich/raw/github_com_razrfalcon_roxmltree.json](../../../data/wave3/enrich/raw/github_com_razrfalcon_roxmltree.json) (enrichment confidence 0.55)

</details>
