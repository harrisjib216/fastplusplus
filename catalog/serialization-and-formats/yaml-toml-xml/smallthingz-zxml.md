# zxml

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [YAML, TOML and XML](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig` · `MIT` · 🟢 active

> Zig DOM/streaming XML parser whose default permissive mode beats pugixml and rapidxml by 1.5-5.4x on real-world files.

| | |
|---|---|
| **Beats** | pugixml |
| **Claimed result** | bench/README.md stable snapshot: ours-permissive DOM is 1.46x-9.73x faster than the best of {pugixml, rapidxml} on each of the 24 headline fixtures (24/24 PASS). On the 15 real-world and pugixml-corpus fixtures the range is 1.47x-5.41x; pugixml_large.xml runs at 2560.26 MiB/s vs pugixml 473.25 MiB/s (5.41x). The 8.88x and 9.73x top end comes from synthetic_tiny_empty ('&lt;x/&gt;' x220,000) and synthetic_tiny_text ('&lt;x&gt;a&lt;/x&gt;' x120,000). Those inputs hit special-case exact-repeat DOM paths in src/parser.zig (detectRepeatedSelfClosingDocument, detectRepeatedSimpleTextPlan). The README average is 3799.40 MiB/s vs pugixml 1312.83 MiB/s, about 2.9x (derived from page data). The validated DOM averages 2037.12 MiB/s, about 1.55x pugixml (derived from page data), and it is slower than pugixml on weekly_utf8.xml (1218.10 vs 2151.54) and synthetic_deep_tree.xml (1124.84 vs 1259.10). |
| **Workload** | DOM parse throughput (MiB/s) across 24 headline XML fixtures (real-world RSS/catalog/sitemap files plus the vendored pugixml test corpus and synthetic stress cases: deep trees, wide siblings, CDATA/attribute mixes), 5 samples x 40ms per fixture, 'stable' profile |
| **Metric** | throughput |
| **Hardware** | 12th Gen Intel(R) Core(TM) i5-12450H, Linux 7.2.2-zen1-1-zen, x86_64, CPU frequency scaling 47%, advertised MHz range 400.0-4400.0 |
| **Compiler and flags** | zxml: Zig 0.16.0, ReleaseFast -Dcpu=native. pugixml (pinned git revision) and rapidxml 1.13: the unnamed system 'c++' driver (GCC or Clang not identified, no version), -O3 -DNDEBUG -march=native. |
| **Adoption** | 0 stars; repo created 2026-04-03, about 290 commits |
| **Last commit** | 2026-09-09 |
| **Links** | [repository](https://github.com/SmallThingz/zxml) · [benchmark](https://github.com/SmallThingz/zxml/blob/main/bench/README.md) |

## Verdict

In the author's stable-profile run on an i5-12450H (Linux 7.2, x86_64), zxml's default permissive DOM (Zig 0.16.0, ReleaseFast -Dcpu=native) beat the faster of pugixml (pinned git revision) and rapidxml 1.13 on all 24 headline fixtures. The C++ parsers were built with an unidentified system c++ driver at -O3 -DNDEBUG -march=native. The margin was 1.47-5.41x on the 15 real-world and pugixml-corpus files and reached 9.73x on synthetic exact-repeat inputs, and the mean was 3799.40 MiB/s vs 1312.83 for pugixml. The harness has three imbalances: pugixml's load_buffer copies the input on every iteration, pugixml builds comment/PI/declaration/doctype nodes while zxml's default stores none, and the validated DOM averages only 2037.12 MiB/s (about 1.55x pugixml).

## Use it when

- Zig programs that parse many small-to-medium UTF-8 documents (RSS/Atom feeds, sitemaps, catalogs, config) into a read-only tree: 2.1-4.1x pugixml on the 0.2-23 KiB feed and catalog fixtures (derived from page data).
- Trusted or producer-controlled XML where lenient parsing is acceptable and you can give the parser a mutable buffer that outlives the Document.
- Read patterns that touch only a few attributes or text values: attribute scanning and entity decoding wait until you query them, so content you never read costs almost nothing.
- Chunked or event-driven ingestion in Zig: the streaming parser takes cumulative buffers with save/restore, and it runs at 0.79-1.23x the DOM's throughput on the real-world fixtures (derived from page data).

## Skip it when

- C or C++ codebases: there is no C ABI or binding (build.zig exposes only a Zig module), so replacing pugixml means writing and maintaining a wrapper.
- Untrusted input that must be well-formed: validate_well_formedness drops the mean to 2037.12 MiB/s. It then loses to pugixml on weekly_utf8.xml (0.57x) and synthetic_deep_tree.xml (0.89x), and to rapidxml on 5 of the 14 real or pugixml-corpus files that have a validated result (derived from page data).
- Workloads that need DOM editing, XPath or non-UTF-8 input. zxml has no mutation API and no XPath. The source handles only UTF-8 (plus a UTF-8 BOM), with no transcoding found, while pugixml converts UTF-16/32 and Latin-1.
- Very large documents: the largest real-world fixture is a \~2.1 MiB arXiv feed (3.2x pugixml), most real files are 0.2-23 KiB (sizes derived from latest.json), and default u32 indexes reject inputs over 4 GiB - 1 with InputTooLarge unless you build with -Dintlen=u64.
- Production code that needs a track record: v0.1.0 in build.zig.zon, no tags or releases, one contributor, 0 stars, no issues or PRs ever filed, and it requires exactly the Zig 0.16 toolchain generation.

## How it is fast

It builds a lazy, source-backed DOM. Each node stores only a parent index and one source span, and text nodes are marked by a reversed span instead of a kind field. Attributes are not tokenized during parsing; they are rescanned from the source when queried. Subtree and sibling bounds come from preorder parent links, so parsing writes little more than 12 bytes per node. In the default permissive mode, a start tag ends at the first '&gt;' found by a SIMD scan (portable Zig @Vector: 32 bytes with AVX2, 16 bytes elsewhere), with quote parity checked in bulk instead of running a per-attribute state machine. Text runs are also found with vector compare masks, and the common &lt;tag&gt;text&lt;/tag&gt; shape is special-cased with a u64 comparison of the first 8 name bytes. Node storage is pre-sized from a '&lt;'-density sample, small documents start in a 64-node on-stack buffer, and inputs of 64 KiB or more that repeat one exact token take dedicated repeated-document paths, which produce the 8.9-9.7x synthetic results. Well-formedness validation (UTF-8 and XML character checks, duplicate-attribute filter, tag matching, reference checks) is a separate code path chosen at compile time, which is why it roughly halves throughput.

## Compared with alternatives

Pick zxml when you are working in Zig and want both a lazy DOM and an incremental streaming parser without C interop. In C++, the catalogued LightningXML (3.82 GB/s vs pugixml 1.46 GB/s on its flat workload) and Parshred (1.6-3.3x pugixml) link directly. simdxml suits XPath-style queries over multi-GB files, which zxml neither supports nor has measured.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (Zig standard library only; the benchmarks use pugixml and rapidxml, fetched separately) |
| **Minimum toolchain** | Zig 0.16.0 (minimum_zig_version in build.zig.zon; CI pins 0.16.0) |
| **Platforms** | any Zig target. SIMD uses portable @Vector (32-byte with AVX2 on x86, 16-byte elsewhere). ReleaseSafe compile checks passed for x86_64/aarch64 Linux, Windows and macOS, RISC-V 64, PowerPC64, ARM and x86_64 FreeBSD. Benchmarks exist only for x86_64 (i5-12450H). |
| **Thread safety** | Not documented. In the default destructive mode the decoding accessors (getAttributeValue, value, innerText) rewrite the input buffer and node spans in place, so a Document shared across threads needs external locking. In non_destructive mode those accessors appear to be read-only (inferred from src/document.zig). |
| **Drop-in for the baseline** | no |

## Gotchas

- The default ParseOptions{} is destructive: parse takes a []u8, and decoded accessors compact entity-containing values in place, so the original bytes are gone. Set non_destructive = true to parse a []const u8.
- Permissive mode recovers silently. `<a><b></a>` and an unclosed `<a><b>` both parse without error, and unquoted attributes such as a=1 are accepted. A raw '&gt;' inside a quoted attribute value, however, may be rejected; use &gt; or enable validation.
- By default, whitespace-only text nodes are dropped, comments and PIs are not stored (include_misc_nodes = false), and DTD entities are not expanded (expand_dtd_entities = false, capped by max_entity_value_len when on). Decoded-value results may own memory and must be released with .free(allocator).
- Without store_prev_sibling or store_last_child, prevSibling and lastChild scan forward from the parent, and nextSibling walks the current node's whole subtree. Backward or last-child navigation over wide or deep trees can be much slower than pugixml's linked nodes.

## Known shortcomings

- The 8.9-9.7x top of the range comes from two synthetic single-token files that hit special fast paths; on real-world and pugixml-corpus files it is 1.47-5.41x over the best of pugixml/rapidxml. Headline numbers use the permissive parser, which can reject valid XML; full-grammar mode is slower than pugixml on 2 files. The pugixml runner copies input inside the timed loop. The C++ baselines were built with an unnamed system c++ driver. 0 stars; the project's own VALIDATION.md reports FAIL on its speed targets.
- Most real-world fixtures are 0.2-23 KiB (largest about 2.1 MiB), so there is no evidence for large documents. Validated mode also loses to rapidxml on 5 of 14 real/corpus files. '112/112 conformance' is an in-house suite, not the W3C test suite, and there is no schema validation. No C ABI, DOM mutation or XPath; UTF-8 only; 4 GiB input cap by default. Default mode rewrites the source buffer on decode, so documents are not safe to share across threads. v0.1.0, one contributor.

## Caveats and trade-offs

First-party benchmark. The C++ baseline compiler is not identified (only the system 'c++' driver). Headline numbers use the default permissive, destructive DOM, which may reject a literal '&gt;' inside a quoted attribute value; the full-grammar validated mode is much slower (mean 2037.12 MiB/s) and loses to pugixml on weekly_utf8.xml and synthetic_deep_tree.xml. The top of the range (8.9x-9.7x) comes from synthetic exact-repeat fixtures that trigger special-case repeated-token DOM fast paths. The pugixml runner uses load_buffer, which copies the input inside the timed loop, while rapidxml runs non-destructive. The project's VALIDATION.md says its own absolute throughput targets (&gt;5 GiB/s permissive, &gt;3 GiB/s validated) FAIL. The repo has 0 stars and is about 6 months old, so adoption is unproven.

Zig-only API, no C ABI documented; default parser is destructive (mutates the input buffer in place) and permissive (may accept malformed XML such as an unescaped '&gt;' inside a quoted attribute value); enabling validate_well_formedness roughly halves throughput (e.g. note.xml: ours-validated 1650.37 MiB/s vs ours-permissive 2802.99 MiB/s); no XPath support shown in README; extremely new and unproven with no external adoption yet.

## Maintenance

Actively developed by a single author (about 290 commits since April 2026, last commit 2026-09-09) but still unreleased at v0.1.0; it is MIT-licensed, pure Zig and easy to vendor as a module if you pin Zig 0.16.0.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification A, tier now C.
- **Tier reason:** The harness is public: bench/bench.zig, bench/runners/pugixml_runner.cpp, bench/runners/rapidxml_runner.cpp, bench/runners/run_parse.zig and tools/scripts.zig (pugixml pinned to a git revision, rapidxml 1.13). The page states Zig 0.16.0 ReleaseFast -Dcpu=native, C++ flags -O3 -DNDEBUG -march=native, and the i5-12450H CPU. It misses A only because the baseline C++ compiler is recorded as the unnamed system 'c++' driver: no GCC or Clang identity and no version, in the page, latest.md or latest.json. That matches how earlier batches treated a missing compiler identity, so first-party numbers with partial methodology are C.
- **Verifier notes:** Every number in the record matches bench/README.md; the 3799.40 and 1312.83 averages are in the root README and VALIDATION.md. The record's 'first commits \~2026-09 / &lt;2-week-old repo' is wrong: the repo was created 2026-04-03 and has about 290 commits. License MIT, not a fork, not archived, last commit 2026-09-09, active: all confirmed. If the orchestrator accepts a named project compiler plus flags without the C++ driver's identity, this entry would qualify as A. Every other part of the methodology (pinned baselines, CPU, kernel, source SHA-256s) is unusually rigorous.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/SmallThingz/zxml>
  - <https://github.com/SmallThingz/zxml/blob/main/bench/README.md>
  - <https://github.com/SmallThingz/zxml/blob/main/README.md>
  - <https://github.com/SmallThingz/zxml/blob/main/bench/VALIDATION.md>
  - <https://github.com/SmallThingz/zxml/blob/main/bench/runners/pugixml_runner.cpp>
  - <https://github.com/SmallThingz/zxml/blob/main/bench/runners/rapidxml_runner.cpp>
  - <https://github.com/SmallThingz/zxml/blob/main/bench/results/latest.md>
  - <https://github.com/SmallThingz/zxml/blob/main/bench/results/latest.json>
  - <https://github.com/SmallThingz/zxml/blob/main/tools/scripts.zig>
  - <https://github.com/SmallThingz/zxml/blob/main/src/parser.zig>
- **Sources the enricher read:**
  - <https://github.com/SmallThingz/zxml>
  - <https://github.com/SmallThingz/zxml/blob/main/README.md>
  - <https://github.com/SmallThingz/zxml/blob/main/bench/README.md>
  - <https://github.com/SmallThingz/zxml/blob/main/bench/VALIDATION.md>
  - <https://github.com/SmallThingz/zxml/blob/main/bench/results/latest.md>
  - <https://github.com/SmallThingz/zxml/blob/main/bench/results/latest.json>
  - <https://github.com/SmallThingz/zxml/blob/main/bench/runners/pugixml_runner.cpp>
  - <https://github.com/SmallThingz/zxml/blob/main/bench/runners/rapidxml_runner.cpp>
  - <https://github.com/SmallThingz/zxml/blob/main/bench/runners/run_parse.zig>
  - <https://github.com/SmallThingz/zxml/blob/main/bench/stream_bench.zig>
  - <https://github.com/SmallThingz/zxml/blob/main/bench/conformance/security_owasp_nist_core.json>
  - <https://github.com/SmallThingz/zxml/blob/main/bench/conformance/schema_validation_xsd_core.json>
  - <https://github.com/SmallThingz/zxml/blob/main/bench/conformance/well_formedness_w3c_core.json>
  - <https://github.com/SmallThingz/zxml/blob/main/tools/scripts.zig>
  - <https://github.com/SmallThingz/zxml/blob/main/src/root.zig>
  - <https://github.com/SmallThingz/zxml/blob/main/src/document.zig>
  - <https://github.com/SmallThingz/zxml/blob/main/src/parser.zig>
  - <https://github.com/SmallThingz/zxml/blob/main/src/scanner.zig>
  - <https://github.com/SmallThingz/zxml/blob/main/src/streaming.zig>
  - <https://github.com/SmallThingz/zxml/blob/main/src/common.zig>
  - <https://github.com/SmallThingz/zxml/blob/main/tests/public_api.zig>
  - <https://github.com/SmallThingz/zxml/blob/main/examples/basic_parse.zig>
  - <https://github.com/SmallThingz/zxml/blob/main/build.zig>
  - <https://github.com/SmallThingz/zxml/blob/main/build.zig.zon>
  - <https://github.com/SmallThingz/zxml/blob/main/.github/workflows/ci.yml>
  - <https://github.com/SmallThingz/zxml/blob/main/SECURITY.md>
  - <https://github.com/SmallThingz/zxml/blob/main/CONTRIBUTING.md>
  - <https://github.com/SmallThingz/zxml/issues>
  - <https://github.com/SmallThingz/zxml/pulls>
  - <https://github.com/SmallThingz/zxml/releases>
  - <https://github.com/SmallThingz/zxml/tags>
  - <https://github.com/SmallThingz/zxml/commits/main>
  - <https://github.com/SmallThingz/zxml/graphs/contributors>
  - <https://github.com/zeux/pugixml/blob/27b68329de32cf9c601ca8eb6c588fd639960c40/docs/manual.adoc>
  - <https://github.com/zeux/pugixml/blob/27b68329de32cf9c601ca8eb6c588fd639960c40/docs/samples/transitions.xml>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/smallthingz/zxml`) · [data/wave4/enrich/raw/github_com_smallthingz_zxml.json](../../../data/wave4/enrich/raw/github_com_smallthingz_zxml.json) (enrichment confidence 0.8)

</details>
