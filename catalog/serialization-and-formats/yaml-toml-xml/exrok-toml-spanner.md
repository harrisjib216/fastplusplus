# toml-spanner

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [YAML, TOML and XML](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Arena-backed, span-preserving Rust TOML 1.1 library; parses \~9x and parse+deserializes \~3x faster than the `toml` crate.

| | |
|---|---|
| **Beats** | toml (toml-rs/toml, the de facto standard Rust TOML crate) |
| **Claimed result** | Parse-only zed/Cargo.toml: 24.5 us vs 228.5 us for toml 1.0.7+spec-1.1.0 (\~9.3x, derived from page data); extask.toml 8.9 vs 78.5 us and devsm.toml 3.7 vs 35.8 us (\~8.8x and \~9.7x, derived from page data). Parse+deserialize zed/Cargo.lock: 1023.5 us vs 2977.4 us (\~2.9x, derived from page data); zed/Cargo.toml: 92.5 vs 309.4 us (\~3.3x, derived from page data). README text: '2-3x faster than `toml` on end-2-end benchmarks'. toml_edit and toml-span are also slower in the same tables. |
| **Workload** | Parsing, and parse+deserialize, of real-world TOML files (zed/Cargo.toml, zed/Cargo.lock, extask.toml, devsm.toml) using the project's own micro-benchmark harness with cycle/instruction counters |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 5950X, 64GB RAM, Linux 6.18 |
| **Compiler and flags** | rustc 1.94.1 (stated in the README). The repo benchmark runner (devsm.toml action.benchmark) builds crates/benchmark with `cargo +nightly run --release`, using the default Cargo release profile (no LTO/opt-level override), plus rustflags `--cfg fuzzing` from crates/benchmark/.cargo/config.toml. |
| **Adoption** | 33 stars |
| **Last commit** | 2026-06-17 |
| **Links** | [repository](https://github.com/exrok/toml-spanner) · [benchmark](https://github.com/exrok/toml-spanner#benchmarks) |

## Verdict

These are the author's own cycle/instruction-counter benchmarks on an AMD Ryzen 9 5950X (Linux 6.18). The README states rustc 1.94.1, but the repo's benchmark action runs `cargo +nightly run --release` with the default release profile and no LTO. toml-spanner 1.0.0 parsed zed/Cargo.toml in 24.5 us vs 228.5 us for toml 1.0.7 parsing into `toml::Table` with `fast_hash` on (\~9.3x), and was 8.8-9.7x faster on two smaller configs. With deserialization into cargo's own lockfile/manifest types included, the lead shrinks to 2.9x (Cargo.lock, 1023.5 vs 2977.4 us) and 3.3x (Cargo.toml, 92.5 vs 309.4 us); none of this has been independently reproduced.

## Use it when

- Rust tools that load TOML configs or manifests on a startup or hot path (CLIs, build tools, dev servers), where `toml` parse time is visible. On real Cargo.toml and tool config files the README shows \~9x faster parsing.
- Linters, language servers and config validators that need exact source locations. Every parsed value keeps a byte span, and errors carry spans plus TOML paths and render through annotate-snippets or codespan-reporting.
- Reporting every config mistake in one pass. Conversion errors accumulate in the `Document` context, and `parse_recoverable` continues past syntax errors (up to 25) instead of failing on the first.
- Rewriting user-edited TOML while keeping comments and layout (`Formatting::preserved_from`), as a lighter option than toml_edit, which took \~12x longer to parse zed/Cargo.toml in the same table (306.6 vs 24.5 us).
- Crates that care about build time or binary size. For a simplified Cargo.toml model, the author's separate build benchmark reports a 52 ms warm `cargo check` vs 169 ms for toml, and a 204 KB vs 500 KB stripped release binary.

## Skip it when

- Codebases built on serde `Deserialize`: `toml::from_str` call sites and serde-derived types must be ported to `#[derive(Toml)]` or hand-written `FromToml`. The `serde` feature only adds `Serialize` impls for `Item`/`Spanned`.
- Workloads dominated by deserialization. The author calls the deserialization gains 'marginal', and the end-to-end lead over toml falls to 2.9x (Cargo.lock) and 3.3x (Cargo.toml).
- Documents of 256 MiB or more. They are rejected with `FileTooLarge` because spans are 28-bit.
- Dependency policies that forbid or strictly audit `unsafe`. The arena, packed items and tables rely heavily on unsafe code, and its safety rests on the author's Miri runs and fuzzing.
- Risk-averse production use: the project is young (first release January 2026, 1.0 in March 2026) and has a small user base (33 stars, \~38.6k crates.io downloads, 6 reverse dependencies). `toml` is the ecosystem standard.

## How it is fast

All tree nodes are allocated in a bump arena, and strings without escapes are borrowed zero-copy from the input, so parsing makes very few individual heap allocations. `Item` is 24 bytes: the type tag, container flags and span are bit-packed into two u32s. Tables are flat vectors kept in insertion order and searched linearly; once a table reaches 6 entries, one foldhash index for the whole parse, keyed on (the table's first-key offset, key), takes over, and `TableHelper` deserialization reuses that index and tracks consumed fields in a bitset. String bodies are scanned 8 bytes at a time with SWAR (SIMD-within-a-register) bit tricks to find delimiters, backslashes and control bytes; the changelog also credits pointer traversal, batched string reads and reduced LLVM IR.

## Compared with alternatives

It is the only Rust library among the catalogued TOML parsers, so pick it for Rust code. teptris (C, vs toml++), TOMLDecoder (Swift) and go-toml v2 (Go) serve other languages and were measured against different baselines, so their speedups cannot be compared with this one.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | foldhash (required); optional: serde (Serialize impls), zmij (float formatting, enabled by `to-toml`), toml-spanner-macros (`derive` feature; the macro crate itself has no dependencies) |
| **Minimum toolchain** | Rust 1.90 (edition 2024); the derive macro crate declares 1.84 |
| **Platforms** | any: pure Rust with portable u64 SWAR and no arch-specific SIMD; 32-bit (i686) is tested under Miri |
| **Thread safety** | Parsed `Item`/`Table`/`Array` and `OwnedItem`/`OwnedTable` are Send + Sync (since 1.0.2). `Arena` is Send but not Sync because its bump pointers are `Cell`s, so allocate from one thread at a time (one arena per parse or thread). |
| **Drop-in for the baseline** | partial: the API is different. `parse(&str, &Arena)` returns a `Document` that borrows from the arena, and typed deserialization goes through `FromToml`/`#[derive(Toml)]` rather than serde `Deserialize`. A `toml_spanner::from_str` exists but requires `T: FromToml`. Tables keep insertion order by default, unlike `toml` without `preserve_order`. |

## Gotchas

- The `Document` borrows both the input `&str` and the `Arena`. To keep parsed data past their lifetimes, convert it to your own types or use `OwnedItem`/`OwnedTable` (added in 1.0.2).
- `Table::get` and `doc["key"]` scan linearly. The foldhash index speeds up only parsing and `TableHelper` extraction, so ad-hoc lookups on very wide tables are O(n).
- `parse` rejects inputs of 1&lt;&lt;28 bytes (256 MiB) or more, but the `ErrorKind::FileTooLarge` docs and error message say 512 MiB.
- Integers are stored as i128, so values outside the i64 range, which `toml` rejects, are accepted. The project's fuzz comparison against toml skips these as a known divergence; check with `as_i64` if you need 64-bit range.

## Known shortcomings

- Not a drop-in for serde users: typed deserialization uses its own FromToml trait. The 9x is parse-only; parse plus deserialize is 2.9-3.3x. Accepts integers beyond i64 that toml rejects; table lookups are linear; the 256 MiB input limit contradicts its 512 MiB docs. Heavy unsafe, validated by the author's Miri and fuzz runs. Young (1.0 in 2026-03, 33 stars).

## Caveats and trade-offs

These are the project's own README numbers, not independently reproduced. The README states rustc 1.94.1, but the repo's devsm.toml benchmark action invokes `cargo +nightly`. All crates use the default Cargo release profile (no LTO). The numbers are for toml-spanner 1.0.0 (the current release is 1.0.3). The \~9x parse-only gap shrinks to \~2.9-3.3x once deserialization is included; the README says deserialization gains are 'marginal'. The library uses extensive unsafe code, mitigated by Miri and fuzzing. It started as a fork of toml-span but is not a GitHub fork, and the author says it has been 'pretty much completely rewritten'.

Uses extensive unsafe code for its compact Value/TableEntry layout (24/48 bytes vs toml's 32/56), mitigated by Miri and fuzzing per the author; end-to-end deserialization gains are smaller than pure parse-time gains; never compared against toml++ or any C/C++ library

## Maintenance

Actively maintained (1.0.3 released 2026-06-17, one open issue), dual MIT/Apache-2.0, pure Rust with a single required dependency, so it is easy to adopt, but it is young and lightly used.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now A.
- **Tier reason:** The README Benchmarks section compares toml-spanner against toml 1.0.7+spec-1.1.0 (the named baseline) and states rustc 1.94.1 and an AMD Ryzen 9 5950X. The harness is public in crates/benchmark/src/main.rs, with crates/benchmark/src/cargo.rs for parse+deserialize and a Cargo.lock that pins toml 1.0.7. The flags are in the repo: the devsm.toml action.benchmark runs `cargo +nightly run --release` in crates/benchmark (default release profile, no override), and crates/benchmark/.cargo/config.toml adds rustflags `--cfg fuzzing`. I upgraded C to A, following the earlier rkyv and sonic-rs precedent that flags in public build config count as stated.
- **Verifier notes:** The license 'MIT OR Apache-2.0' is correct: Cargo.toml says so and both LICENSE-MIT and LICENSE-APACHE exist, although the GitHub API reports only Apache-2.0. I verified 33 stars, the 2026-06-17 last commit (release 1.0.3), not archived. is_fork_of was kept as recorded because the README says it started as a toml-span fork, even though GitHub fork=false. A depends on accepting repo-config flags (`--release` via devsm.toml) as stated; if the orchestrator wants flags on the numbers page itself, this falls back to C.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/exrok/toml-spanner#benchmarks>
  - <https://github.com/exrok/toml-spanner>
  - <https://github.com/exrok/toml-spanner/commits>
  - <https://github.com/exrok/toml-spanner/blob/main/README.md>
  - <https://github.com/exrok/toml-spanner/blob/main/Cargo.toml>
  - <https://github.com/exrok/toml-spanner/blob/main/devsm.toml>
  - <https://github.com/exrok/toml-spanner/tree/main/crates/benchmark>
  - <https://github.com/exrok/toml-spanner/blob/main/crates/benchmark/Cargo.toml>
  - <https://github.com/exrok/toml-spanner/blob/main/crates/benchmark/Cargo.lock>
  - <https://github.com/exrok/toml-spanner/blob/main/crates/benchmark/.cargo/config.toml>
  - <https://github.com/exrok/toml-spanner/blob/main/crates/benchmark/src/main.rs>
  - <https://github.com/EmbarkStudios/toml-span>
- **Sources the enricher read:**
  - <https://github.com/exrok/toml-spanner>
  - <https://github.com/exrok/toml-spanner#benchmarks>
  - <https://github.com/exrok/toml-spanner/blob/main/README.md>
  - <https://github.com/exrok/toml-spanner/blob/main/Cargo.toml>
  - <https://github.com/exrok/toml-spanner/blob/main/CHANGELOG.md>
  - <https://github.com/exrok/toml-spanner/blob/main/devsm.toml>
  - <https://github.com/exrok/toml-spanner/blob/main/src/lib.rs>
  - <https://github.com/exrok/toml-spanner/blob/main/src/arena.rs>
  - <https://github.com/exrok/toml-spanner/blob/main/src/parser.rs>
  - <https://github.com/exrok/toml-spanner/blob/main/src/item.rs>
  - <https://github.com/exrok/toml-spanner/blob/main/src/item/table.rs>
  - <https://github.com/exrok/toml-spanner/blob/main/src/de.rs>
  - <https://github.com/exrok/toml-spanner/blob/main/src/error.rs>
  - <https://github.com/exrok/toml-spanner/blob/main/src/impl_serde.rs>
  - <https://github.com/exrok/toml-spanner/blob/main/crates/benchmark/Cargo.toml>
  - <https://github.com/exrok/toml-spanner/blob/main/crates/benchmark/.cargo/config.toml>
  - <https://github.com/exrok/toml-spanner/blob/main/crates/benchmark/src/main.rs>
  - <https://github.com/exrok/toml-spanner/blob/main/crates/benchmark/src/cargo.rs>
  - <https://github.com/exrok/toml-spanner/blob/main/crates/toml-spanner-macros/Cargo.toml>
  - <https://github.com/exrok/toml-spanner/blob/main/crates/fuzz/src/parse_compare.rs>
  - <https://github.com/exrok/toml-spanner/issues>
  - <https://github.com/exrok/toml-spanner/issues/1>
  - <https://github.com/exrok/toml-spanner/issues/2>
  - <https://github.com/exrok/toml-spanner/issues/4>
  - <https://github.com/exrok/toml-spanner/pulls>
  - <https://crates.io/api/v1/crates/toml-spanner>
  - <https://crates.io/api/v1/crates/toml-spanner/reverse_dependencies>
  - <https://github.com/exrok/rust-serialization-build-time-benchmarks>
  - <https://github.com/exrok/rust-serialization-build-time-benchmarks/blob/main/report/BENCH-cargo-toml.md>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/exrok/toml-spanner`) · [data/wave4/enrich/raw/github_com_exrok_toml_spanner.json](../../../data/wave4/enrich/raw/github_com_exrok_toml_spanner.json) (enrichment confidence 0.82)

</details>
