# simdxml

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [YAML, TOML and XML](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Rust SIMD XML parser and XPath 1.0 engine using a flat structural index; beats pugixml on large, attribute-dense files.

| | |
|---|---|
| **Beats** | pugixml |
| **Claimed result** | vs pugixml: 2.6x on DBLP 5.1GB //article (3.2s vs 8.3s), 1.3x on PubMed 195MB //MeshHeading, 1.7x on 10MB attribute-heavy //record, 2.6x on the Ryzen 9 attribute-heavy case; vs xmllint: up to 17.5x; vs quick-xml (Rust): 1.1-4.0x depending on file shape |
| **Workload** | End-to-end XPath query benchmarks (sxq CLI vs pugixml vs xmllint) on real-world corpora - DBLP 5.1GB //article, PubMed 195MB //MeshHeading, 10MB attribute-heavy //record - plus library-level parse-only throughput vs Rust parsers (quick-xml, roxmltree) on PubMed 195MB, 1MB attribute-heavy XML, 1MB patent XML, and a 69KB SVG. |
| **Metric** | throughput |
| **Hardware** | Apple M4 Max (NEON) and AMD Ryzen 9 3950X (AVX2) |
| **Compiler and flags** | simdxml/sxq: cargo build --release, workspace [profile.release] lto=true, codegen-units=1, strip=true (rustc version not stated; MSRV 1.75). pugixml side: bench/pugixml-xpath.cpp shim built with `c++ -O2 -std=c++17` against the system libpugixml (bench/run-x86.sh; the author's blog says pugixml 1.14 at -O2). No C++ compiler version stated. CLI timing uses hyperfine (5 warmup/20 runs; DBLP 2 warmup/5 runs); library timing uses criterion. |
| **Adoption** | 14 stars |
| **Last commit** | 2026-03-27 |
| **Links** | [repository](https://github.com/simdxml/simdxml) · [benchmark](https://github.com/simdxml/simdxml/blob/main/README.md) |

## Verdict

All figures are the project's own hyperfine timings of whole processes: `sxq` (release build with LTO, rustc version unstated) against a small pugixml XPath shim built with `c++ -O2` against the system pugixml (1.14 per the author's blog). On an M4 Max that gave 3.2 s vs 8.3 s on 5.1 GB DBLP `//article` and 130 vs 174 ms on 195 MB PubMed, and on a Ryzen 9 3950X 14.7 vs 38.8 ms on a 10 MB attribute-heavy file. However, sxq used every core and, on DBLP and PubMed, printed only a match count, while the single-threaded pugixml shim printed every match's text, and pugixml wins PubMed `count()` and `contains()` outright.

## Use it when

- Read-only XPath extraction from large, record-oriented dumps (hundreds of MB to multi-GB, e.g. DBLP or PubMed) on a multi-core machine. The author's blog puts the DBLP index at \~3.6 GB against \~7.9 GB for pugixml's DOM.
- Attribute-dense XML such as SVG or flat attribute records. This is where the SIMD quote masking pays off: 1.7-2.6x over pugixml end-to-end and 4.0x over quick-xml parse-only on the project's 1 MB attribute-heavy file.
- Shell pipelines that currently use `xmllint --xpath`. `sxq` is a jq-style CLI with count, raw, JSON and NUL-separated output, and the README reports it 6.4-17.5x faster than xmllint.
- Querying the same big file repeatedly (a `.sxi` sidecar is reloaded by mmap, so there is no re-parse), or running one compiled query over thousands of small files (the batch API with a bloom-filter prescan).
- Rust services, or Python/Elixir through the simdxml org's bindings, that need XPath 1.0 over trusted, well-formed UTF-8 input.

## Skip it when

- You need a DOM to edit or save, or pugixml's tree-navigation API. simdxml is a query-only index, and C++ callers would have to write their own FFI layer.
- Untrusted, malformed or non-UTF-8 input. Upfront UTF-8 validation was removed for speed (commit 8a7fdd4), text is handed back through `from_utf8_unchecked`, and mismatched close tags are not detected (the `MismatchedCloseTag` error variant is never raised). DTDs are not processed, and only the five predefined entities and numeric entities are decoded.
- Workloads dominated by `count()` / `contains()`, or small files. pugixml wins those PubMed queries (117 vs 133 ms, 148 vs 162 ms), and under 1 MB the README says all native tools are within startup noise.
- XPath that depends on namespaces. `pfx:name` tests are matched against the literal tag text, with no prefix-to-URI resolution, so a document that uses a default namespace or a different prefix will not match.
- Anything needing a maintained dependency. It has 14 stars and one main author; v0.1.0 through v0.2.1 all shipped on 26-27 March 2026 with no main-branch commits since, and a third-party fix for index corruption (PR #4) was withdrawn unmerged.

## How it is fast

Parsing follows simdjson's stage-1 idea: 64-byte blocks are compared against `<`, `>`, `"` and `'` with AVX2, SSE4.2 or NEON and packed into u64 bitmaps, and quoted regions are masked with a prefix-XOR (PMULL carry-less multiply on ARM, a shift-XOR chain on x86). That classifier only runs when a 4 KB sample shows more than 5 quotes per tag; otherwise a memchr-based scanner jumps from `<` to `<`. The output is a struct-of-arrays index of about 16 bytes per tag, against about 35 bytes per DOM node. XPath then runs on CSR child arrays, pre/post-order numbering (O(1) ancestor tests), posting lists of interned tag names, and fused descendant scans; the CSR arrays are built lazily, only for multi-step paths. Files are mmap'd, and in the CLI anything of 1 MB or more is split at `>`...`<` boundaries, parsed on all cores, and merged in one sequential pass.

## Compared with alternatives

Parshred (C++20, AGPL-3.0: DOM/SAX/pull APIs, XPath, namespaces, DTD validation, W3C conformance in CI) and libsimdxml (a C++23 library with the same flat-index-plus-XPath-1.0 design, 1.15-1.24x pugixml on parse) are the native C++ options, and Parshred is the one to use for untrusted or namespace-heavy XML. Pick simdxml when you are in Rust or want a permissively licensed CLI for multi-core XPath extraction over multi-GB record dumps.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | nom 7, thiserror 2, memchr 2, memmap2 0.9, xxhash-rust 0.8 (xxh3); the sxq CLI adds only memmap2 |
| **Minimum toolchain** | Rust 1.75 (declared MSRV), edition 2021 |
| **Platforms** | x86-64 (AVX2 or SSE4.2 detected at runtime, scalar fallback); aarch64 NEON (selected at compile time, and uses PMULL without a feature check); other targets use a scalar/memchr path |
| **Thread safety** | Not documented. `XmlIndex` is plain Vecs over a borrowed `&[u8]`, so the compiler auto-derives Send + Sync for it. `xpath()` / `xpath_text()` take `&self`, but `eval()` takes `&mut self` because it builds the CSR indexes lazily, so call `ensure_indices()` before sharing an index across threads. The library spawns its own scoped threads for `parse_parallel`, the batch APIs and CSR builds above 10K tags. |
| **Drop-in for the baseline** | no |

## Gotchas

- Quote state in the SIMD two-stage path is tracked across the whole document, not per tag. A lone `"` or `'` in text content (e.g. `don't`) masks every later `<` and `>`, silently dropping the rest of the document from the index. This affects only files routed to that path (more than 5 quotes per tag in the first 4 KB). The fix, PR #4 from June 2026, was withdrawn unmerged; it also reports phantom tags from `<` inside comments or CDATA on that same path.
- On aarch64, `neon.rs` calls `vmull_p64` (PMULL) with no `target_feature` gate or runtime check. Per PR #4, this traps with an illegal instruction on ARMv8 cores that lack the crypto extension.
- Depth limits, from reading the source (not tested). The sequential scanner keeps parents in a fixed 32-entry stack, so tags nested deeper than 32 get no parent pointer and child/parent steps below that depth can miss. The parallel merge uses a 4096-entry stack with no bounds guard, so deeper nesting panics.
- `sxq` automatically switches to all-core parallel parsing for files of 1 MB or more; pass `-t 1` for a single-threaded comparison. Its parallel splitter accepts any `>` followed by `<`, which can fall inside a CDATA section that contains markup. `string-length()` counts bytes, not characters.

## Caveats and trade-offs

First-party numbers from the project's own README and bench scripts; not independently reproduced. The end-to-end CLI comparisons favor sxq. sxq parses files over 1 MB in parallel on all cores by default, while the pugixml shim is single-threaded. For DBLP, and for the PubMed //MeshHeading query in run-x86.sh, sxq runs with -c (prints only the match count) while the pugixml shim extracts and prints the text of every match. So the 2.6x DBLP and 1.3x PubMed figures compare multi-threaded count-only output against single-threaded full text output. The README and the author's blog say pugixml wins count() and contains() queries (blog: 0.88x and 0.91x). No rustc or C++ compiler version stated. The repo has no LICENSE file: MIT OR Apache-2.0 is declared only in Cargo.toml and the README, and GitHub reports no license. 14 stars; last main commit 2026-03-27.

Produces a flat structural-index array (no DOM tree, \~16 bytes/tag vs \~35 for a DOM node) rather than pugixml's tree API; pugixml still wins on scalar-aggregation (count()) and text-predicate (contains()) queries where its single-pass DOM build has lower overhead; it's a Rust crate, so C++ consumers need an FFI layer; no top-level LICENSE file is committed - the MIT OR Apache-2.0 grant lives only in Cargo.toml package metadata.

## Maintenance

Listed as active, but every commit landed on 26-27 March 2026 (crates.io v0.1.0 through v0.2.1, about 5.7k downloads) and main has had nothing since. MIT OR Apache-2.0 is declared only in Cargo.toml and the README, with no LICENSE file, and it installs with `cargo add simdxml` or `cargo install simdxml-cli`.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification A, tier now C.
- **Tier reason:** The README tables come from the project's own public harness (bench/run.sh, bench/run-x86.sh, bench/pugixml-xpath.cpp, crates/simdxml/benches/parse_bench.rs), and the CPU models are stated (M4 Max, Ryzen 9 3950X). But no rustc or C++ compiler version is given, and the pugixml version and build flags are not on the page (run-x86.sh uses system libpugixml with the shim at -O2; the author's blog says pugixml 1.14 at -O2). That misses A, and first-party numbers with partial methodology are C.
- **Verifier notes:** All README numbers match the record. Downgraded A to C under the no-compiler-version rule. The CLI method also favors sxq (all-core parallel parse plus count-only output against a single-threaded pugixml printing text). A web search turned up a C++23 port, KrzysztofKowalski/libsimdxml, which may be worth a separate look for the C++-first list; I did not evaluate it.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/simdxml/simdxml>
  - <https://github.com/simdxml/simdxml/blob/main/README.md>
  - <https://github.com/simdxml/simdxml/blob/main/Cargo.toml>
  - <https://github.com/simdxml/simdxml/blob/main/crates/simdxml/Cargo.toml>
  - <https://github.com/simdxml/simdxml/blob/main/bench/run.sh>
  - <https://github.com/simdxml/simdxml/blob/main/bench/run-x86.sh>
  - <https://github.com/simdxml/simdxml/blob/main/bench/pugixml-xpath.cpp>
  - <https://github.com/simdxml/simdxml/blob/main/bench/download-corpora.sh>
  - <https://github.com/simdxml/simdxml/blob/main/crates/simdxml/benches/parse_bench.rs>
  - <https://github.com/simdxml/simdxml/blob/main/crates/simdxml-cli/src/main.rs>
  - <https://cigrainger.com/blog/simdxml/>
- **Sources the enricher read:**
  - <https://github.com/simdxml/simdxml>
  - <https://github.com/simdxml/simdxml/blob/main/README.md>
  - <https://github.com/simdxml/simdxml/blob/main/Cargo.toml>
  - <https://github.com/simdxml/simdxml/blob/main/crates/simdxml/Cargo.toml>
  - <https://github.com/simdxml/simdxml/blob/main/crates/simdxml/README.md>
  - <https://github.com/simdxml/simdxml/blob/main/crates/simdxml-cli/Cargo.toml>
  - <https://github.com/simdxml/simdxml/blob/main/crates/simdxml-cli/README.md>
  - <https://github.com/simdxml/simdxml/blob/main/crates/simdxml-cli/src/main.rs>
  - <https://github.com/simdxml/simdxml/blob/main/crates/simdxml/src/lib.rs>
  - <https://github.com/simdxml/simdxml/blob/main/crates/simdxml/src/error.rs>
  - <https://github.com/simdxml/simdxml/blob/main/crates/simdxml/src/index/mod.rs>
  - <https://github.com/simdxml/simdxml/blob/main/crates/simdxml/src/index/structural.rs>
  - <https://github.com/simdxml/simdxml/blob/main/crates/simdxml/src/index/tags.rs>
  - <https://github.com/simdxml/simdxml/blob/main/crates/simdxml/src/index/lazy.rs>
  - <https://github.com/simdxml/simdxml/blob/main/crates/simdxml/src/simd/mod.rs>
  - <https://github.com/simdxml/simdxml/blob/main/crates/simdxml/src/simd/avx2.rs>
  - <https://github.com/simdxml/simdxml/blob/main/crates/simdxml/src/simd/neon.rs>
  - <https://github.com/simdxml/simdxml/blob/main/crates/simdxml/src/simd/sse42.rs>
  - <https://github.com/simdxml/simdxml/blob/main/crates/simdxml/src/parallel/mod.rs>
  - <https://github.com/simdxml/simdxml/blob/main/crates/simdxml/src/batch/mod.rs>
  - <https://github.com/simdxml/simdxml/blob/main/crates/simdxml/src/bloom.rs>
  - <https://github.com/simdxml/simdxml/blob/main/crates/simdxml/src/persist/mod.rs>
  - <https://github.com/simdxml/simdxml/blob/main/crates/simdxml/src/xpath/eval.rs>
  - <https://github.com/simdxml/simdxml/blob/main/crates/simdxml/tests/bug_regression.rs>
  - <https://github.com/simdxml/simdxml/blob/main/crates/simdxml/tests/pugixml_conformance.rs>
  - <https://github.com/simdxml/simdxml/blob/main/crates/simdxml/benches/parse_bench.rs>
  - <https://github.com/simdxml/simdxml/blob/main/bench/run.sh>
  - <https://github.com/simdxml/simdxml/blob/main/bench/run-x86.sh>
  - <https://github.com/simdxml/simdxml/blob/main/bench/pugixml-xpath.cpp>
  - <https://github.com/simdxml/simdxml/commits/main>
  - <https://github.com/simdxml/simdxml/commit/8a7fdd4>
  - <https://github.com/simdxml/simdxml/pull/4>
  - <https://github.com/simdxml/simdxml/issues>
  - <https://github.com/orgs/simdxml/repositories>
  - <https://crates.io/api/v1/crates/simdxml>
  - <https://cigrainger.com/blog/simdxml/>
  - <https://github.com/KrzysztofKowalski/libsimdxml>
  - <https://github.com/gregghy/parshred>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/simdxml/simdxml`) · [data/wave4/enrich/raw/github_com_simdxml_simdxml.json](../../../data/wave4/enrich/raw/github_com_simdxml_simdxml.json) (enrichment confidence 0.82)

</details>
