# MPL / FastParse (kurotakazuki/mpl)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Parser generators and combinators](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> One-rule TDPL/PEG grammar crate whose static-codegen backend (FastParse) beats nom, pest, peg, winnow, chumsky on recognition benchmarks.

| | |
|---|---|
| **Beats** | nom (also benchmarked against pest, peg, winnow, chumsky, serde_json) |
| **Claimed result** | README: static-codegen backend (FastParse) 'beats pest, peg, nom, winnow, chumsky, and even serde_json on equal-work recognition benchmarks.' Criterion numbers: nested-parens depth 1024, MPL 2.26us vs nom 7.50us (\~3.3x, derived from page data); depth 4096, MPL 9.23us vs nom 20.8us (\~2.25x, derived from page data); flat-1024, MPL 2.11us vs nom 4.92us (\~2.3x, derived from page data). |
| **Workload** | Micro-benchmarks, mostly recognition-only (bool result, no AST): nested/flat parenthesis matching (depth 1024/4096, flat-1024) vs nom/peg/winnow/pest/chumsky; JSON-subset recognition on json/canada/twitter/citm shapes vs peg (plus a token-queue tier vs pest and a reference tier vs serde_json Value); left-recursive-sum (lsum-64/256/1024) vs peg cache_left_rec. |
| **Metric** | latency |
| **Compiler and flags** | cargo/rustc with RUSTFLAGS="-C target-cpu=native"; criterion 0.8.2, sample size 100; dependency versions pinned (pest 2.8.6, peg 0.8.6, winnow 1.0.3, nom 8.0.0, chumsky 0.13.0), re-run 2026-05-30. |
| **Adoption** | 6 stars |
| **Last commit** | 2026-05-30 |
| **Links** | [repository](https://github.com/kurotakazuki/mpl) · [benchmark](https://github.com/kurotakazuki/mpl#readme) |

## Verdict

First-party Criterion benchmarks (sample size 100, RUSTFLAGS="-C target-cpu=native", pinned crate versions: pest 2.8.6/peg 0.8.6/winnow 1.0.3/nom 8.0.0/chumsky 0.13.0, re-run 2026-05-30, no CPU model or rustc version stated) show MPL's recognition-only FastParse backend parsing nested/flat parenthesis strings 2.25x-3.3x faster than nom (e.g. depth-1024 nested: 2.26us vs nom 7.50us) and 1.8x-2.5x faster than peg on JSON-subset recognition; these numbers measure recognition only and do not capture the cost of building an actual parse tree, which is what most nom users need.

## Use it when

- Recognition-only or validation-style workloads (need a bool or a walkable token stream, not necessarily a typed AST) where nom/peg/pest parsing overhead is the bottleneck
- Grammars expressible in the single-rule TDPL/PEG form (sequence, choice, recursion, repetition, negative predicates), including left-recursive rules like `LSum = LSum N / N`
- Rust projects that can accept a build-time grammar file plus proc-macro dependencies (bumpalo, syn, quote), not just inline combinator code
- High-throughput repeated parsing where an externally supplied, resettable `Bump` arena (`fast_recognize_in`) amortizes allocation
- Willing to depend on a young, single-maintainer, 6-star crate for a non-critical or experimental parsing path

## Skip it when

- You need a typed AST/`Value` tree directly (e.g. JSON deserialization) — MPL's fast tier only emits a flat token buffer, a token-to-Value walker isn't shipped, and MPL's token tier is already slower than serde_json for that shape
- Your data has deeply nested coordinate-array shapes like canada.json — pest's coarser token queue beat MPL's per-variable Start/End emission by 1.68x in the token tier there
- You need nom's combinator ecosystem (streaming/incremental input, existing combinator libraries) — MPL has no equivalent
- Production systems needing a mature, widely-audited parser: 6 GitHub stars, first-party unreproduced benchmarks, and zero GitHub issues on record (nothing to check known-failure-mode history against)
- Deployments that don't set `RUSTFLAGS="-C target-cpu=native"` — the headline 2-3x numbers were measured with it; default release builds will be slower than reported

## How it is fast

Compile-time analysis picks a fast path per rule: char-class cascades become `[bool; 256]` lookup tables, multi-branch first-symbol choices become a single first-byte `match` dispatch, and tail-recursive repetition (`R = X R / ()`) compiles to an explicit `loop {}` instead of relying on LLVM tail-call optimization. Mizushima cut analysis restricts memoization to only the rules whose FIRST sets actually overlap; everything else (most rules in their 99-rule test grammar) skips the memo table entirely. Left recursion uses Squirrel-style position-only seed-growing memoization, the same family as peg's `#[cache_left_rec]`. Recognition-only calls run through a thin `CheckState` (input + furthest position, no token buffer).

## Compared with alternatives

Among the nom-beating siblings (winnow, chumsky), pick MPL only if you can restrict the workload to recognition-only or flat-token output and accept a single-rule grammar DSL from a single-maintainer, 6-star crate; winnow and chumsky are both far more established combinator libraries that were benchmarked against nom on equal-work full parsing, which is closer to what most nom users actually need.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | mpl: bumpalo 3.20 (arena allocator); mpl-macro (proc-macro crate): proc-macro2, quote, syn, plus mpl itself |
| **Minimum toolchain** | not documented — Cargo.toml declares edition 2021 with no MSRV pin; CI only builds against the stable toolchain |
| **Platforms** | not documented beyond CI, which runs only on ubuntu-latest; source is pure Rust with a single `unsafe fn push_unchecked` in fast.rs (capacity-checked buffer push), no target-specific/SIMD code observed |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — explain: grammar must be written in the .mplg DSL and derived onto a struct rather than composed from nom combinator functions in Rust, so migration is a rewrite, not a swap |

## Gotchas

- fast_recognize still builds a token buffer internally to match pest's semantics; use fast_recognize_only for the buffer-free fast path
- One unsafe block (push_unchecked in packages/mpl/src/fast.rs) relies on the caller having already checked capacity
- README's 'beats every comparator' claim is contradicted by its own canada-1024 token-tier row, where pest wins
- The serde_json row in the README is not equal-work (different output shapes) — don't read it as a parser-vs-parser result

## Caveats and trade-offs

First-party benchmark written and run by the sole maintainer, not independently reproduced; no CPU model or rustc version is stated (only RUSTFLAGS and crate versions). nom is compared only on the parenthesis benchmark. The serde_json comparison is not equal-work: the README itself says a fair direct comparison needs a Token-to-Value walker that is not yet shipped, and MPL's token-producing tier is slower than serde_json. pest beats MPL by 1.68x on canada-1024 in the token tier. Adoption is minimal (6 GitHub stars).

Very new, minimally-adopted grammar formalism (single-rule TDPL/GTDPL, `.mplg` DSL + macro), far less battle-tested than nom; benchmarks are recognition-only (returns bool), so they do not measure the cost of building an actual parse tree/AST, which is what most real nom users need; single maintainer.

## Maintenance

Active as of the 2026-05-30 last commit with green CI, but effectively unadopted (6 GitHub stars, single maintainer, zero GitHub issues on record); dual MIT/Apache-2.0 licensed and small enough to vendor, but pre-1.0 (0.3.1) and should be treated as research-grade rather than a production nom replacement.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The README's Performance section gives Criterion numbers against nom, peg, winnow, pest and chumsky. The harness is public (examples/paren_bench/benches/paren.rs) and the RUSTFLAGS and crate versions are stated. No CPU model or rustc version is given, so this is first-party evidence with partial methodology.
- **Verifier notes:** The numbers match the README tables. The default branch's last commit is 2026-05-30; pushed_at 2026-07-25 comes from dependabot branches. The README's 'beats every comparator' claim is contradicted by its own canada-1024 token-tier row.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/kurotakazuki/mpl#readme>
  - <https://github.com/kurotakazuki/mpl>
  - <https://github.com/kurotakazuki/mpl/tree/main/examples/paren_bench>
- **Sources the enricher read:**
  - <https://github.com/kurotakazuki/mpl>
  - <https://github.com/kurotakazuki/mpl#readme>
  - <https://github.com/kurotakazuki/mpl/tree/main>
  - <https://github.com/kurotakazuki/mpl/blob/main/packages/mpl/Cargo.toml>
  - <https://github.com/kurotakazuki/mpl/blob/main/packages/mpl-macro/Cargo.toml>
  - <https://github.com/kurotakazuki/mpl/blob/main/Cargo.toml>
  - <https://github.com/kurotakazuki/mpl/blob/main/examples/paren_bench/Cargo.toml>
  - <https://github.com/kurotakazuki/mpl/blob/main/.github/workflows/ci.yml>
  - <https://github.com/kurotakazuki/mpl/blob/main/packages/mpl/src/fast.rs>
  - <https://github.com/kurotakazuki/mpl/issues>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/kurotakazuki/mpl`) · [data/wave3/enrich/raw/github_com_kurotakazuki_mpl.json](../../../data/wave3/enrich/raw/github_com_kurotakazuki_mpl.json) (enrichment confidence 0.4)

</details>
