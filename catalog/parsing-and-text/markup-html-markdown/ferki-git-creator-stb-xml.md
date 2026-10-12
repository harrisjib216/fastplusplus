# stb_xml

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [HTML, Markdown and markup](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> Single-header, zero-allocation XML tokenizer for C; beats libxml2's DOM parser on raw throughput.

| | |
|---|---|
| **Beats** | libxml2 |
| **Claimed result** | Small 72B XML: 188 MB/s vs libxml2 15 MB/s \~12.5x; medium \~1KB XML: 556 MB/s vs 36 MB/s \~15x (derived from page data). The 1MB figure (8707 MB/s vs 46 MB/s, \~189x; README claims 193x) is invalid: run_parser caps xml_parse at 10000 tokens, so stb_xml stops early (10000 tokens vs 87357 nodes libxml2 builds) while MB/s is computed over the full 1,048,653 bytes. |
| **Workload** | Parse synthetic small (72B), medium (\~1KB), and generated large (\~1MB) XML, timed with clock() over 10 to 100000 iterations. stb_xml is a tokenizer (test_stb_xml.c, 10000-token buffer); libxml2 uses xmlParseMemory plus xmlFreeDoc, building a full DOM (test_libxml.c). |
| **Metric** | throughput |
| **Compiler and flags** | gcc -O2 -std=c99 for stb_xml; gcc -lxml2 -O2 for libxml2 comparison |
| **Adoption** | 2 stars; brand-new single-developer proof-of-concept |
| **Last commit** | 2026-01-05 |
| **Links** | [repository](https://github.com/Ferki-git-creator/stb_xml) · [benchmark](https://github.com/Ferki-git-creator/stb_xml/blob/main/output_tests.txt) |

## Verdict

Console output from test_stb_xml.c (gcc -O2 -std=c99) and test_libxml.c (gcc -lxml2 -O2) on the author's machine (no CPU model given) shows stb_xml at 188 MB/s vs libxml2's 15 MB/s on a 72-byte document (\~12.5x) and 556 MB/s vs 36 MB/s on a \~1KB document (\~15x); the 1MB-file figure (8707 vs 46 MB/s, \~189x, matching the README's '193x' claim) is invalid because the benchmark's fixed 10000-token buffer caps stb_xml's work at roughly 11% of the document while libxml2 fully parses all \~87357 nodes and throughput is computed over the full byte count on both sides.

## Use it when

- Small, trusted, well-formed XML (config files, game/level data, small message payloads) where you just need tag/attribute offsets, not a DOM
- Embedded or memory-constrained targets where a \~1.5KB single header and zero heap allocation during parsing matter more than feature completeness
- You're willing to write your own tree/attribute-lookup layer on top of a flat token array
- Throughput-bound repeated parsing of the same small/medium shapes, e.g. request/response bodies a few hundred bytes to \~1KB, where the \~12-15x tokenizer-vs-DOM gap (small: 188 vs 15 MB/s; medium: 556 vs 36 MB/s) is real overhead you're paying today in libxml2
- You need only tokenization, not validation - malformed XML, external entities, or DTDs are not your concern

## Skip it when

- Any input over 10000 tokens: the reference benchmark harness passes a fixed `tokens[10000]` buffer, and `xml_parse` silently stops filling tokens once `max_tokens` is hit rather than erroring, so large documents are silently truncated unless you size the buffer yourself and check the return value
- You need namespaces, DTD/entity handling, XPath, XSLT, or XML Schema - none exist here
- Untrusted or possibly-malformed input: the parser does 'minimal error checking' per its own README/feature list and has no validation path
- You need a DOM, mutation, or serialization API - stb_xml only tokenizes; there is no tree, no write-back, no libxml2-compatible surface
- Production use generally: this is a single-developer, 2-commit, 2-star proof-of-concept with no tests beyond one manual sample and no CI, issue history, or track record

## How it is fast

It is a single-pass, branch-heavy state machine (4 states: default, in-tag, comment, CDATA) that never copies bytes or allocates memory; tokens just record start/end offsets into the caller-owned buffer. Each token is a packed 6-byte struct (two uint16 offsets, two uint8 fields) versus libxml2's 40+ byte DOM nodes, so far less memory is written per byte of input. libxml2, by contrast, builds a full DOM (xmlParseMemory + tree of xmlNode/xmlAttr) with allocation, validation-related bookkeeping, and pointer-linked structures.

## Compared with alternatives

Pick stb_xml over pugixml or roxmltree only if you specifically want a bare tokenizer with no tree at all and can tolerate its 10000-token/65535-byte-span limits and near-total lack of validation; pugixml and roxmltree both build real (if lightweight) trees, are far more mature, and their libxml2 comparisons (4.5x-23x and \~2.3x-2.5x respectively) are not artifacts of a token cap the way stb_xml's headline number is.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none |
| **Minimum toolchain** | C99 (repo builds with gcc -O2 -std=c99); uses stdint.h fixed-width types |
| **Platforms** | not documented (pure C99, no platform-specific code visible, but no explicit platform/arch statement in README) |
| **Thread safety** | not documented (function is reentrant/stateless aside from caller-provided buffers, but this is not stated anywhere in the repo) |
| **Drop-in for the baseline** | partial — explain: same input (raw XML text) but a completely different output shape (flat offset tokens vs a DOM tree), so callers must rewrite consumption code, not just relink |

## Gotchas

- max_tokens truncation is silent: xml_parse's own benchmark (test_stb_xml.c) caps a 1MB document at 10000 tokens out of \~87000 nodes libxml2 produces for the same file, and the reported 8707 MB/s and README's 193x figure are computed by dividing the full file size by the time to fill only those 10000 tokens - the actual per-byte-of-input throughput on large documents is far lower than advertised
- Attribute value end is not stored: xml_token_t.val_start marks where a quoted attribute value begins, but you must rescan for the closing quote yourself (test_stb_xml.c's print_token does this with a manual strlen scan) since there's no val_end field
- Self-closing tags (`<tag/>`) reuse val_start as a boolean flag (1 = self-closing) on TAG_OPEN tokens, which collides in meaning with its use as a value-offset on ATTR tokens - easy to misread if you don't check token.type first
- start/end offsets are uint16_t, capping any single tag name, text run, or attribute span at 65535 bytes even though input length itself is int32_t

## Known shortcomings

- 2 stars. The README's 1 MB figure (\~193x) comes from a harness bug that stops parsing at 10,000 tokens while dividing by the full file size; only the \~12-15x on small and medium files holds, and that compares a tokenizer against libxml2 building a full DOM.

## Caveats and trade-offs

In test_stb_xml.c, run_parser passes max_tokens=10000, and xml_parse stops at token_count &lt; max_tokens. On the 1MB file only about the first 10000 tokens are tokenized, yet throughput is computed over the whole file, so the 189x/193x claim is overstated by roughly an order of magnitude. The two sides do different work: tokenize-only, with minimal error checking, vs a full DOM build. The libxml2 side is a system shared library with its build flags unknown. No CPU model is given. The repo is 2 commits on 2026-01-05, with 2 stars.

stb_xml is a bare zero-allocation tokenizer emitting 6-byte tokens, not a validating parser or DOM builder: no namespaces, no DTD/entity handling, minimal error checking, so it does far less work per byte than libxml2's full tree build.

## Maintenance

Active per last-commit date (2026-01-05) but the entire history is 2 commits from a single developer with 2 stars and 0 issues - effectively a brand-new proof-of-concept, not a maintained project; BSD-3-Clause and small enough (\~1.5KB single header) to vendor and re-verify yourself if you still want it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party console output with public harnesses (test_stb_xml.c, test_libxml.c) and gcc -O2 flags, but no CPU model. The headline 1MB figure is a harness artifact, so the result is capped at C.
- **Verifier notes:** The 1MB throughput number is a measurement bug (token cap), not a real speedup. The only defensible numbers are the \~12-15x small and medium cases, which are still tokenizer vs DOM. The record said xmlReadMemory; the code uses xmlParseMemory. Metadata checks out: BSD-3-Clause, 2 stars, last commit 2026-01-05. The orchestrator may want to drop it as not notable.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Ferki-git-creator/stb_xml/blob/main/output_tests.txt>
  - <https://github.com/Ferki-git-creator/stb_xml>
  - <https://github.com/Ferki-git-creator/stb_xml/blob/main/test_stb_xml.c>
  - <https://github.com/Ferki-git-creator/stb_xml/blob/main/stb_xml.h>
  - <https://github.com/Ferki-git-creator/stb_xml/blob/main/test_libxml.c>
  - <https://github.com/Ferki-git-creator/stb_xml/blob/main/README.md>
- **Sources the enricher read:**
  - <https://github.com/Ferki-git-creator/stb_xml>
  - <https://github.com/Ferki-git-creator/stb_xml/blob/main/README.md>
  - <https://github.com/Ferki-git-creator/stb_xml/blob/main/stb_xml.h>
  - <https://github.com/Ferki-git-creator/stb_xml/blob/main/test_stb_xml.c>
  - <https://github.com/Ferki-git-creator/stb_xml/blob/main/test_libxml.c>
  - <https://github.com/Ferki-git-creator/stb_xml/blob/main/output_tests.txt>
  - <https://github.com/Ferki-git-creator/stb_xml/blob/main/LICENSE>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/ferki-git-creator/stb_xml`) · [data/wave3/enrich/raw/github_com_ferki_git_creator_stb_xml.json](../../../data/wave3/enrich/raw/github_com_ferki_git_creator_stb_xml.json) (enrichment confidence 0.3)

</details>
