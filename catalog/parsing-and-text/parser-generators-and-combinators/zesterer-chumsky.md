# chumsky

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Parser generators and combinators](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust parser-combinator library beating nom on JSON throughput, with error recovery and zero-copy output.

| | |
|---|---|
| **Beats** | nom |
| **Claimed result** | chumsky (check-only) 140.77 us (797 MB/s) and chumsky (full parse) 210.43 us (533 MB/s) vs nom 526.52 us (213 MB/s) on an idiomatic JSON benchmark, which is \~3.7x and \~2.5x higher throughput (derived from page data). winnow (178.91 us) beats full-parse chumsky in the same table. |
| **Workload** | Idiomatic JSON parsing benchmark (single document) compared across 8 Rust parsing libraries/hand-written parser, single core |
| **Metric** | throughput |
| **Hardware** | single core of an AMD Ryzen 7 3700x |
| **Adoption** | 4.5k stars on GitHub (archived mirror); 106 stars on Codeberg (active home) |
| **Last commit** | 2026-09-16 |
| **Links** | [repository](https://github.com/zesterer/chumsky) · [benchmark](https://codeberg.org/zesterer/chumsky#performance) |

## Verdict

In chumsky's own first-party criterion JSON-parsing benchmark, run on a single core of an AMD Ryzen 7 3700x, chumsky's check-only mode took 140.77 us (797 MB/s) and full parse took 210.43 us (533 MB/s), versus 526.52 us (213 MB/s) for nom (7.1/8 both used as dev-dependencies) — roughly 3.7x and 2.5x the throughput of nom on that one workload. rustc version and optimization flags are not stated in the benchmark writeup.

## Use it when

- Writing a compiler, interpreter, or DSL parser where you want structured error recovery and multiple diagnostics per parse instead of failing on the first error
- Parsing UTF-8 text or byte slices where zero-copy output (slices into the input) matters for throughput or memory
- Validation-only workloads where you just need to know if input is well-formed (chumsky's check-only mode is the fastest path in its own JSON benchmark)
- no_std/embedded targets that need a parser combinator library without the standard library
- Grammars needing context-sensitivity (semantic indentation, raw strings) beyond plain context-free/PEG combinators

## Skip it when

- You need nom's streaming/incremental parsing model for partial network buffers; chumsky's API is not drop-in compatible with nom and expects the input available as a slice
- You want the fastest full-AST parse in this exact benchmark family: winnow (178.91 us) beats chumsky's full-parse mode (210.43 us) on the same JSON workload
- You need a fully stable, 1.0-guaranteed API today; the crate is at 0.13.0 and an open tracking issue (#543, 'Tracking: Stable 1.0') shows the API surface is still settling
- You plan to share a single parser value across threads via `recursive()`: chumsky's source (src/lib.rs) imports `alloc::rc::Rc` and `core::cell::{Cell, RefCell}` for its recursive-parser machinery, and thread-safety is not documented, so Send/Sync should not be assumed without checking
- You're on the latest Windows MSVC toolchain: an open issue (#815) reports a linker error from just `use chumsky;`, unresolved as of this session

## How it is fast

Parsers are built as a typed combinator tree that chumsky's internal optimizer (built on GATs) specializes at compile time, avoiding much of the dynamic dispatch overhead of naive combinator libraries. A 'check-only' mode validates input without constructing an output/AST at all, which is the fastest configuration in its own benchmark. Zero-copy string/byte-slice handling avoids per-token allocation, and the optional `stacker` feature (on by default) spills recursion state to the heap only when the native stack is close to exhausted, rather than paying a cost up front.

## Compared with alternatives

Of the catalogued siblings, only winnow is a close substitute (also a Rust parser library beating nom on this exact JSON benchmark). Pick chumsky over winnow when you want combinator ergonomics, built-in error recovery, and rich diagnostics for a hand-rolled language/DSL grammar; pick winnow when raw full-parse throughput matters most, since it beats chumsky's full-parse mode (178.91 us vs 210.43 us) in chumsky's own table. The other siblings (flap, PAPAGENO, re2c, Pika Parser) target OCaml/C parser-generator or lexer-generator use cases, not Rust combinator parsing, so they aren't direct alternatives.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | always: hashbrown, unicode-ident, unicode-segmentation; optional (feature-gated): stacker (default-on), regex-automata, lexical, either, serde, bytes, railroad |
| **Minimum toolchain** | Rust 1.65, edition 2021 (per Cargo.toml `rust-version`) |
| **Platforms** | any — no_std-compatible (`#![cfg_attr(not(...), no_std)]`), no architecture-specific requirements found; Windows+MSVC has an open unresolved linker-error report (issue #815) |
| **Thread safety** | not documented; internal `recursive()` support is built on `Rc`/`RefCell` (seen in src/lib.rs imports), so recursive parsers are likely not Send/Sync without extra wrapping |
| **Drop-in for the baseline** | false — different combinator API from nom; a nom parser must be rewritten, not ported, to use chumsky |

## Gotchas

- The headline check-only number (140.77 us) validates input without building any output tree — don't compare it directly to other libraries' full-parse numbers, including chumsky's own 210.43 us full-parse figure
- recursive() parsers appear to rely on Rc&lt;RefCell&lt;_&gt;&gt; internally (inferred from src/lib.rs imports, not stated in the docs), a likely source of !Send/!Sync surprises
- Open issue #798: parsers wrapped in `.ignored()` currently skip `map_with()`, which the maintainers call out as unexpected behavior
- Open issue #159: error-recovery logic can affect how otherwise-valid input is parsed, i.e. enabling recovery is not purely additive

## Known shortcomings

- The GitHub repo linked here is archived because development moved to https://codeberg.org/zesterer/chumsky, which is active.

## Caveats and trade-offs

The GitHub repo is archived because the project moved to Codeberg (GitHub description: 'Chumsky has moved to Codeberg!'). Development continues at codeberg.org/zesterer/chumsky, last commit 2026-09-16. First-party benchmark; rustc version and flags are not stated, only the CPU. The table shows one unlabelled 'nom' row, but the bench defines both nom 7.1 and nom 8. The author says a single JSON benchmark should not be read as a general 'faster than X' claim. winnow beats full-parse chumsky in this table.

Single micro-benchmark (JSON); chumsky's own README warns results vary heavily with grammar shape and that 'chumsky is faster than X' is too strong a claim from one workload; check-only mode (the fastest number) does validation without building a parse tree.

## Maintenance

Actively maintained (last commit 2026-09-16) — the GitHub repo is now an archived mirror after the project's move to Codeberg (codeberg.org/zesterer/chumsky), where development continues. MIT-licensed and distributed as an ordinary crate, but still pre-1.0 (v0.13.0), so treat the combinator API as subject to change.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** This is the project's own benchmark. The code is public (benches/json.rs, criterion, with nom 7.1 and nom 8 as dev-deps) and the CPU is stated (single core of a Ryzen 7 3700x), but the rustc version and optimization flags are not. That is first-party with partial methodology, so C.
- **Verifier notes:** The numbers match exactly. The 'abandoned' status was wrong: GitHub is an archived mirror after a move to Codeberg, where the repo is active. The orchestrator should consider changing repo_url/id to https://codeberg.org/zesterer/chumsky, which is not a correctable field here.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `last_commit`, `maintenance_status`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/zesterer/chumsky>
  - <https://github.com/zesterer/chumsky/blob/master/README.md#performance>
  - <https://github.com/zesterer/chumsky/blob/main/benches/json.rs>
  - <https://github.com/zesterer/chumsky/blob/main/Cargo.toml>
  - <https://codeberg.org/zesterer/chumsky>
  - <https://codeberg.org/zesterer/chumsky/raw/branch/main/README.md>
  - <https://codeberg.org/api/v1/repos/zesterer/chumsky>
  - <https://codeberg.org/api/v1/repos/zesterer/chumsky/commits?limit=1&stat=false>
- **Sources the enricher read:**
  - <https://github.com/zesterer/chumsky>
  - <https://github.com/zesterer/chumsky/blob/main/README.md>
  - <https://github.com/zesterer/chumsky/blob/main/Cargo.toml>
  - <https://github.com/zesterer/chumsky/blob/main/benches/json.rs>
  - <https://github.com/zesterer/chumsky/blob/main/src/lib.rs>
  - https://github.com/zesterer/chumsky/issues (searched: "performance", label:bug)
  - <https://codeberg.org/zesterer/chumsky>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/zesterer/chumsky`) · [data/wave3/enrich/raw/github_com_zesterer_chumsky.json](../../../data/wave3/enrich/raw/github_com_zesterer_chumsky.json) (enrichment confidence 0.72)

</details>
