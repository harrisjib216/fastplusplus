# rusty_xml (Remade-With-Rust)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [YAML, TOML and XML](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Pure safe-Rust rewrite of libxml2 (parse, DOM, SAX, XPath, DTD, C14N) whose CLI parses faster than xmllint as shipped.

| | |
|---|---|
| **Beats** | libxml2 |
| **Claimed result** | As shipped (rxmlint linked with rusty_alloc against xmllint on the system allocator), CLI parse-noout: 1.55x-2.31x faster (derived from page data). The us/C ratios are 0.447x on big-attr.xml (83.25 vs 37.18 MB/s), 0.644x on big-1m.xml (115.74 vs 74.56), 0.625x on big-300k.xml (125.56 vs 78.47) and 0.432x on slashdot.xml (118.05 vs 50.98). All four files show 20/20 paired wins at z=+4.47. The README headline is '1.6x to 2.2x faster'. With the same allocator on both sides (the parser alone, N=11), the page reports big-attr 0.80x (\~1.25x faster, derived) and big-300k 1.07x (rusty_xml \~7% slower). The author states that roughly half the margin is the allocator. |
| **Workload** | CLI-vs-CLI parse without output (xmllint --noout against rxmlint --noout, --repeat inner loop) on big-attr.xml (627KB), big-1m.xml (1.27MB), big-300k.xml (309KB) and slashdot.xml (3.7KB x 10000). The run is single core, CPU-time metric, ABBA-interleaved, with N=20 pairs and a C-vs-C null arm per row. |
| **Metric** | throughput |
| **Hardware** | CPU model not stated. The harness is Windows PowerShell (xmllint.exe/rxmlint.exe), pinned to core 4 at High priority, and measures CPU time. |
| **Compiler and flags** | rxmlint built with `cargo build -p rusty_xml-cli --release` (rustc version not stated) and linked with rusty_alloc. libxml2 is a pinned prebuilt v2.15.3 xmllint.exe on the system allocator. Parse options differ: C defaults to XML_PARSE_COMPACT \| XML_PARSE_BIG_LINES, and rxmlint forces NONET \| NO_XXE. |
| **Adoption** | 1 star |
| **Last commit** | 2026-09-20 |
| **Links** | [repository](https://github.com/Remade-With-Rust/rusty_xml) · [benchmark](https://github.com/Remade-With-Rust/rusty_xml/blob/main/bench/SIDE-BY-SIDE.md) |

## Verdict

This is an author-run, CLI-vs-CLI comparison on Windows: rxmlint 0.2.0 (release build, rustc not stated, linked with rusty_alloc) against a pinned MSVC build of libxml2 v2.15.3 xmllint on the system allocator. Both parsed with --noout --repeat, pinned to one core, measuring CPU time over 20 ABBA pairs; the CPU model is not stated. rusty_xml was 1.55x-2.31x faster on four files (83.25 vs 37.18 MB/s on big-attr), but with the same allocator on both sides it was only about 1.25x faster on big-attr and about 7% slower on big-300k. The slashdot row is inflated because xmllint re-reads the file on every repeat.

## Use it when

- You need libxml2's feature set (XPath 1.0, DTD validation, C14N/exclusive C14N, HTML parsing) in a Rust or wasm32 build with no C toolchain, no \*-sys crate and #![forbid(unsafe_code)] throughout.
- You parse untrusted XML and want no-network and no-XXE behaviour that cannot be switched off, plus bounded entity expansion.
- Your binary already uses rusty_alloc (or you are willing to set it as the global allocator). The as-shipped 1.55x-2.31x DOM-parse gain over xmllint depends on it.
- You parse attribute-heavy documents of hundreds of KB to MB into a DOM. big-attr.xml is the only large file that stays faster (about 1.25x) when both sides use the same allocator.
- You are porting libxml2-based code to Rust and want the same function names and option bits.

## Skip it when

- You need a parser that is faster on its own merits. With the same allocator the author measures 0.80x on big-attr and 1.07x (slower) on big-300k, and the board has not been re-run since rxmlint 0.2.0. The 0.3.0 through 0.8.1 conformance releases have landed since then.
- You need streaming or bounded memory. xml_reader_for_memory and rxmlint --stream build the whole tree and then walk it. Only the rusty_xml-specific XML_PARSE_NO_TREE flag with a SAX handler avoids building nodes.
- You need XML 1.1, external entity or DTD loading, gzip input (XML_PARSE_UNZIP is not wired), or Shift_JIS/EUC-JP/ISO-2022-JP encodings. None of these are supported.
- You need a C-ABI drop-in for libxml2 (the cdylib is a stub) or the full RelaxNG/XSD/Schematron validators (only working subsets exist).
- You need a mature dependency. The repo was created 2026-08-27, versions 0.1.0 to 0.8.1 all shipped within three days, it has 1 star and about 268 crates.io downloads, and every commit since 0.8.1 has been a README edit.

## How it is fast

About half of the published margin comes from the allocator. rxmlint uses rusty_alloc, a pure-Rust port of mimalloc, as its #[global_allocator], while xmllint runs on the system allocator. The rest comes from ordinary scanner work in the 0.2.0 performance release: character data and attribute values are copied in one pass per ASCII run instead of decoding each character, names are scanned in place as byte spans, UTF-8 decoding checks only the leading scalar (this fixed an O(n^2) re-validation), scratch attribute vectors are reused, and the arena DOM uses u32 NodeId handles. Allocations on the attribute-heavy file fell 72%. There is no SIMD and no string interning: every node and attribute still holds owned Strings, which explains why the allocator matters so much.

## Compared with alternatives

Pick rusty_xml when you need libxml2's breadth (XPath, DTD validation, C14N, HTML) in memory-safe pure Rust. If raw parse speed is the goal, the C/C++ siblings beat libxml2 by much more: RapidXml at 1084.9 vs 278.8 MB/s DOM, SpeedyXml at 4.4x streaming, and libleptris at 1.4-3.6x.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none outside its own workspace crates for the library. rxmlint alone pulls in rusty_alloc-api (plus libc/windows-sys) through rusty_xml-alloc. cargo-deny bans \*-sys crates and copyleft. |
| **Minimum toolchain** | Rust 1.85 (MSRV), edition 2021 |
| **Platforms** | Windows x86-64, Linux and macOS are built and tested in CI. The wasm32-unknown-unknown library passes cargo check in CI. No arch-specific code or SIMD. |
| **Thread safety** | not documented. XmlDoc is plain owned data (Vec/String/HashMap, no Rc/RefCell/unsafe) and xml_init_parser is a no-op with no global state, so separate documents on separate threads should be fine. |
| **Drop-in for the baseline** | partial — the Rust API mirrors libxml2 names and XML_PARSE_\* bits and rxmlint takes xmllint's flags, but there is no C ABI, the output diverges on entity-reference nodes and DTD-subset serialization, and NONET\|NO_XXE are always forced on |

## Gotchas

- The library never sets #[global_allocator]. Linked into your app on the system allocator, you get the same-allocator result (0.80x-1.07x of libxml2), not the headline 0.43x-0.64x.
- xml_ctxt_use_options ORs in XML_PARSE_NONET | XML_PARSE_NO_XXE on every call, so documents that depend on external entities or DTDs cannot be loaded, even when you pass other flags.
- Without NOENT, general entities are expanded where libxml2 keeps entity-reference nodes, and the internal DTD subset is serialized verbatim where C reorders it. Tree shape and byte output differ from xmllint in these two cases.
- Since 0.2.0 the pub `name` field of #text/#comment/#cdata-section/#document nodes is an empty String. Use XmlDoc::name() to get the canonical name.

## Known shortcomings

- About half the margin over libxml2 comes from its custom allocator (rusty_alloc), per the author: with the same allocator big-attr is 0.80x and big-300k is 1.07x of libxml2's time, so the parser alone is slower on big-300k. The comparison is CLI against CLI with different parse flags.
- The board measures 0.2.0; releases through 0.8.1 added conformance checks and were never re-benchmarked. Not reproducible from the repo (big-1m.xml missing, script covers other files), and the xmllint baseline differs about 1.86x between the author's two boards. The library sets no global allocator, so embedders get the same-allocator figures. '--stream' builds the full tree first. 1 star; all releases shipped within three days.

## Caveats and trade-offs

The headline ratio is 'as shipped' and includes rusty_alloc (a pure-Rust mimalloc port) against libxml2 on the system allocator. With the same allocator, the author measures only 0.80x on big-attr and 1.07x on big-300k, where rusty_xml is slower, and says quoting the as-shipped ratio as a parser result would be wrong. The slashdot.xml row is flattered because xmllint re-opens and re-reads the file on every --repeat. This is CLI-vs-CLI with different parse flags, not a kernel A/B. The repo is very new (created 2026-08-27, 1 star). The CPU model, OS details and rustc version are not stated. The numbers are the author's own and are not independently reproduced.

Author states roughly half the speed advantage comes from rusty_alloc (pure-Rust mimalloc) vs libxml2's system allocator, not the parsing algorithm itself; ground-up reimplementation of libxml2's algorithms (not a binding), so feature completeness (full XPath, validation) is still catching up

## Maintenance

The last code release was 0.8.1 on 2026-08-29, and every commit since has been a README edit (the 'active installs' count is self-reported). It is MIT OR Apache-2.0, 100% safe Rust and on crates.io, but the whole project was written in under a month by a single maintainer org.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification C, tier now C.
- **Tier reason:** bench/SIDE-BY-SIDE.md is a paired board: rxmlint against a pinned libxml2 v2.15.3 xmllint, with the harness public in bench/pinvs.ps1. No CPU model and no rustc version are stated, and the C side is a prebuilt oracle binary, so this is first-party partial methodology: C.
- **Verifier notes:** The numbers match SIDE-BY-SIDE.md and the README. The record left out the author's own same-allocator disclosure, which shows the parser alone is not uniformly faster (big-300k 1.07x, slower), so the claim was overstated. Tier C stays. License confirmed as MIT OR Apache-2.0 (LICENSE-MIT, LICENSE-APACHE and Cargo.toml; GitHub detects only Apache-2.0). Last commit 2026-09-20, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Remade-With-Rust/rusty_xml>
  - <https://github.com/Remade-With-Rust/rusty_xml/blob/main/bench/SIDE-BY-SIDE.md>
  - <https://github.com/Remade-With-Rust/rusty_xml/blob/main/bench/C-ONLY-BOARD.md>
  - <https://github.com/Remade-With-Rust/rusty_xml/blob/main/bench/pinvs.ps1>
  - <https://github.com/Remade-With-Rust/rusty_xml/blob/main/README.md>
  - <https://github.com/Remade-With-Rust/rusty_xml/blob/main/Cargo.toml>
- **Sources the enricher read:**
  - <https://github.com/Remade-With-Rust/rusty_xml>
  - <https://github.com/Remade-With-Rust/rusty_xml/blob/main/README.md>
  - <https://github.com/Remade-With-Rust/rusty_xml/blob/main/bench/SIDE-BY-SIDE.md>
  - <https://github.com/Remade-With-Rust/rusty_xml/blob/main/bench/C-ONLY-BOARD.md>
  - <https://github.com/Remade-With-Rust/rusty_xml/blob/main/bench/pinvs.ps1>
  - <https://github.com/Remade-With-Rust/rusty_xml/blob/main/oracle/PIN>
  - <https://github.com/Remade-With-Rust/rusty_xml/blob/main/NOTICE.md>
  - <https://github.com/Remade-With-Rust/rusty_xml/blob/main/Cargo.toml>
  - <https://github.com/Remade-With-Rust/rusty_xml/blob/main/Cargo.lock>
  - <https://github.com/Remade-With-Rust/rusty_xml/blob/main/CHANGELOG.md>
  - <https://github.com/Remade-With-Rust/rusty_xml/blob/main/.github/workflows/ci.yml>
  - <https://github.com/Remade-With-Rust/rusty_xml/blob/main/docs/plan/rusty_xml.md>
  - <https://github.com/Remade-With-Rust/rusty_xml/blob/main/docs/plan/API-CENSUS.md>
  - <https://github.com/Remade-With-Rust/rusty_xml/blob/main/crates/rusty_xml/Cargo.toml>
  - <https://github.com/Remade-With-Rust/rusty_xml/blob/main/crates/rusty_xml/src/lib.rs>
  - <https://github.com/Remade-With-Rust/rusty_xml/blob/main/crates/rusty_xml-alloc/Cargo.toml>
  - <https://github.com/Remade-With-Rust/rusty_xml/blob/main/crates/rusty_xml-alloc/src/lib.rs>
  - <https://github.com/Remade-With-Rust/rusty_xml/blob/main/crates/rusty_xml-parser/Cargo.toml>
  - <https://github.com/Remade-With-Rust/rusty_xml/blob/main/crates/rusty_xml-parser/src/lib.rs>
  - <https://github.com/Remade-With-Rust/rusty_xml/blob/main/crates/rusty_xml-parser/src/parse.rs>
  - <https://github.com/Remade-With-Rust/rusty_xml/blob/main/crates/rusty_xml-tree/src/lib.rs>
  - <https://github.com/Remade-With-Rust/rusty_xml/blob/main/crates/rusty_xml-reader/src/lib.rs>
  - <https://github.com/Remade-With-Rust/rusty_xml/blob/main/crates/rusty_xml-cli/Cargo.toml>
  - <https://github.com/Remade-With-Rust/rusty_xml/blob/main/crates/rusty_xml-cli/src/main.rs>
  - <https://github.com/Remade-With-Rust/rusty_xml/blob/main/crates/rusty_xml-c-abi/src/lib.rs>
  - <https://github.com/Remade-With-Rust/rusty_xml/issues>
  - <https://github.com/Remade-With-Rust/rusty_xml/pulls>
  - <https://github.com/Remade-With-Rust/rusty_xml/commits/main>
  - <https://crates.io/api/v1/crates/rusty_xml>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/remade-with-rust/rusty_xml`) · [data/wave4/enrich/raw/github_com_remade_with_rust_rusty_xml.json](../../../data/wave4/enrich/raw/github_com_remade_with_rust_rusty_xml.json) (enrichment confidence 0.55)

</details>
