# winnow

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Parser generators and combinators](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Zero-copy Rust parser-combinator crate, forked from nom, favoring API evolution and built-in features over strict compatibility.

| | |
|---|---|
| **Beats** | nom |
| **Claimed result** | winnow 178.91 us (627 MB/s) vs nom 526.52 us (213 MB/s) on chumsky's idiomatic JSON benchmark, which is \~2.9x higher throughput (derived from page data). Numbers come from the third-party table in the chumsky README, not from winnow's own docs. |
| **Workload** | Same idiomatic JSON parsing benchmark as the chumsky shootout (single document), single core |
| **Metric** | throughput |
| **Hardware** | single core of an AMD Ryzen 7 3700x |
| **Adoption** | 958 stars |
| **Last commit** | 2026-09-17 |
| **Links** | [repository](https://github.com/winnow-rs/winnow) · [benchmark](https://codeberg.org/zesterer/chumsky#performance) |

## Verdict

On chumsky's own idiomatic single-document JSON benchmark (single core, AMD Ryzen 7 3700x, cargo bench with debug=true, rustc version/flags unstated), winnow parsed at 178.91 us (627 MB/s) versus nom at 526.52 us (213 MB/s), about 2.9x the throughput. The table lives in chumsky's README (mirrored on Codeberg), not in winnow's own docs or benchmarks, and was not rerun independently this session.

## Use it when

- Already writing or migrating a nom-style combinator parser and want ongoing feature development rather than nom's stability-first churn policy
- Parsing bytes/binary formats where zero-copy slices and streaming (partial-input) parsing matter
- Willing to enable the `simd` feature (adds `memchr`) for token/substring-heavy grammars
- Want built-in extras (debug tracing, `dispatch`, bit-level parsing, error recovery groundwork) without pulling in separate nom-ecosystem crates
- no_std / no-alloc embedded targets, using the crate's `alloc`/`std` feature flags to scope in only what's needed

## Skip it when

- Need a drop-in nom replacement with zero migration cost — API is renamed and trait-based, not source-compatible
- Basing the choice purely on the winnow-vs-nom speed number: it comes from a competing project's (chumsky) README table, not winnow's own benchmark suite, and was not independently reproduced this session
- Need the single fastest option in this category — chumsky's own bench shows chumsky itself beating winnow (140.77 us / 797 MB/s check-only, 210.43 us / 533 MB/s full parse, vs winnow's 178.91 us / 627 MB/s) on the same workload
- Require documented thread-safety guarantees — none are stated in the README or docs pages read
- Need nom v8's GAT-based call-site specialization for squeezing out extra throughput in hot, tightly-controlled parsers

## How it is fast

The library is byte-oriented and zero-copy by default; its own performance docs recommend parsing as `u8` rather than `char` and using `dispatch` instead of `alt` when branches have unique prefixes, to cut per-token overhead. An optional `simd` feature pulls in `memchr` for accelerated byte/substring search. winnow deliberately avoids Rust GATs (which nom v8 uses for call-site specialization), trading a slice of peak throughput for more predictable performance and simpler generated code (smaller `impl Trait` return types, faster builds).

## Compared with alternatives

Pick winnow over chumsky when you want a nom-style imperative combinator API and an incremental migration path from an existing nom parser, not the top raw throughput — chumsky's own benchmark shows chumsky itself outrunning winnow on the same JSON workload. Pick it over MPL/FastParse when you need a mature, widely-used, actively maintained general-purpose crate rather than a newer project whose README leads with beating winnow specifically.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none required; optional memchr (simd feature), optional anstream/anstyle/is_terminal_polyfill/terminal_size (debug feature) |
| **Minimum toolchain** | Rust 1.65.0 (MSRV, per Cargo.toml) |
| **Platforms** | any (pure Rust; alloc/std feature-gated for no_std use) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — hard fork of nom's code and concepts, but combinators are renamed and parsers implement a `Parser` trait instead of nom's `FnMut(I) -> IResult` closures; migration guide and doc-aliases exist but source is not compatible |

## Gotchas

- Char-based parsing is measurably slower than byte-based per the project's own performance notes; parse `u8` and use `BStr` only for debug display
- Chained combinators can produce large inferred types that slow builds; the docs recommend wrapping chains in a closure or naming them to avoid `impl Trait` bloat
- `simd` feature must be opted into (`cargo add winnow -F simd`) to get memchr-accelerated search; it is not on by default
- GitHub's license badge shows NOASSERTION, but LICENSE-MIT, Cargo.toml, and the COPYRIGHT file all state MIT

## Caveats and trade-offs

Harvested from a competitor's shootout (the chumsky README), not a claim winnow makes itself; winnow's README makes no performance claims. winnow is a hard fork of nom (COPYRIGHT: 'Winnow is forked from nom'), so the baseline is its own parent. rustc version and flags are not stated; bench profile is cargo bench with debug=true. chumsky's bench (benches/json.rs, winnow 0.7 dev-dep) runs both nom 7.1 and nom 8 but the table shows a single unlabelled 'nom' row. Single JSON workload that may not generalize. GitHub reports the license as NOASSERTION, but LICENSE-MIT, Cargo.toml and COPYRIGHT all say MIT.

winnow is a nom-derived combinator library aimed at ergonomics as much as raw speed; the win here comes from a shootout run and published by a different project (chumsky), not from winnow's own benchmark suite, and was not independently re-run in this search; winnow's own 'Why winnow?' docs page makes no numeric speed claim over nom.

## Maintenance

Actively maintained (default-branch commit 2026-09-17, frequent releases per crates.io versioning in Cargo.toml); MIT-licensed and published as an ordinary crate, so it is easy to vendor or pin despite the GitHub license-detector showing NOASSERTION.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification B, tier now C.
- **Tier reason:** The numbers are in one JSON benchmark table in a competing library's (chumsky's) README. The code is public (chumsky benches/json.rs, criterion) and the CPU is stated (Ryzen 7 3700x), but the rustc version and flags are not, so it cannot be A. A single table maintained by a competitor is not a well-known independent suite, so it is C, not B (borderline call).
- **Verifier notes:** The numbers match the table exactly. Tier moved from B to C because the source is not a well-known independent suite. The GitHub default branch was last committed 2026-09-17; the record's 2026-09-24 was pushed_at, not a default-branch commit. The chumsky repo moved to Codeberg, so benchmark_url now points there (same table).
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `last_commit`, `is_fork_of`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/winnow-rs/winnow>
  - <https://github.com/winnow-rs/winnow/blob/main/LICENSE-MIT>
  - <https://github.com/winnow-rs/winnow/blob/main/COPYRIGHT>
  - <https://github.com/winnow-rs/winnow/blob/main/Cargo.toml>
  - <https://github.com/winnow-rs/winnow/blob/main/README.md>
  - <https://github.com/zesterer/chumsky/blob/master/README.md#performance>
  - <https://github.com/zesterer/chumsky/blob/main/benches/json.rs>
  - <https://github.com/zesterer/chumsky/blob/main/Cargo.toml>
  - <https://codeberg.org/zesterer/chumsky>
  - <https://codeberg.org/zesterer/chumsky/raw/branch/main/README.md>
- **Sources the enricher read:**
  - <https://github.com/winnow-rs/winnow>
  - <https://github.com/winnow-rs/winnow/blob/main/README.md>
  - <https://github.com/winnow-rs/winnow/blob/main/Cargo.toml>
  - <https://docs.rs/winnow/latest/winnow/_topic/why/index.html>
  - <https://codeberg.org/zesterer/chumsky/raw/branch/main/README.md>
  - <https://github.com/winnow-rs/winnow/issues?q=performance>
  - <https://github.com/winnow-rs/winnow/blob/main/src/_topic/performance.rs>
  - <https://github.com/winnow-rs/winnow/blob/main/src/_topic/nom.rs>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/winnow-rs/winnow`) · [data/wave3/enrich/raw/github_com_winnow_rs_winnow.json](../../../data/wave3/enrich/raw/github_com_winnow_rs_winnow.json) (enrichment confidence 0.55)

</details>
