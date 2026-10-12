# noyalib

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [YAML, TOML and XML](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Pure-Rust, zero-unsafe YAML 1.2 serde library that parses config-sized documents to a Value 1.11-1.36x faster than yaml-rust2.

| | |
|---|---|
| **Beats** | yaml-rust2 |
| **Claimed result** | Headline table (Apple M4, Rust 1.95, LTO=fat): deserialize to Value is 1.11x-1.36x faster than yaml-rust2 across 5 fixtures (k8s multi-doc 85.1 us at 1.11x, simple 1.40 us at 1.36x). Against the other Rust crates it is 1.38x-2.00x faster (serde_yaml_ng 1.42-1.84x, serde_yml 1.48-1.96x, yaml-spanned 1.38-1.74x, serde-saphyr 1.69-2.00x). Serialize is 3.00x-4.34x faster than serde_yaml_ng. The serde-saphyr head-to-head table (Apple A18 Pro, rustc 1.98.0, default bench profile) shows 1.21x-3.31x over yaml-rust2 and 2.55x-3.26x over serde-saphyr 1.2.0. The SIMD StructuralIter scan on 1 MiB is 4.2x (stable) / 9.2x (nightly-simd) faster than a memchr find_any_of loop. |
| **Workload** | Criterion deserialize-to-Value-AST benchmarks on 5 fixtures (simple 3-field, nested 20-field, large_list 500 items, github_actions config, k8s multi-document) plus a SIMD structural-delimiter-scan microbenchmark on a 1MiB document |
| **Metric** | latency |
| **Hardware** | Apple M4, aarch64-apple-darwin (headline table); Apple A18 Pro (serde-saphyr head-to-head table) |
| **Compiler and flags** | Headline table: Rust 1.95 stable, criterion --release (LTO=fat, codegen-units=1, panic=abort), --warm-up-time 2 --measurement-time 4. serde-saphyr head-to-head table: rustc 1.98.0 (88d9e12ae 2026-08-18), default bench profile with no LTO tuning. |
| **Adoption** | 10 stars |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/sebastienrousseau/noyalib) · [benchmark](https://github.com/sebastienrousseau/noyalib/blob/main/docs/BENCHMARKS.md) |

## Verdict

The project's own criterion suite ran on an Apple M4 with Rust 1.95 stable (fat LTO, codegen-units=1, panic=abort) and parsed five fixtures (3-field doc to 29 KB 500-item list, plus a 4.4 KB k8s multi-doc) into a Value 1.11-1.36x faster than yaml-rust2's YamlLoader and 1.38-2.00x faster than serde_yaml_ng, yaml-spanned and serde-saphyr. A second dated run on an Apple A18 Pro with rustc 1.98 shows 1.21-3.31x over yaml-rust2 and 2.55-3.26x over serde-saphyr 1.2.0; neither run covers x86 or libyaml.

## Use it when

- Rust services that load config-sized YAML (a few KB to about 30 KB: Kubernetes manifests, GitHub Actions workflows, app config) into serde structs or a dynamic Value, where parse latency is worth 1.1-1.4x over yaml-rust2 or about 1.4-2.0x over serde_yaml_ng and serde-saphyr.
- Workloads that emit a lot of YAML: serializing a Value measured 3.00-4.34x faster than serde_yaml_ng on 3-field and 20-field documents.
- Moving off archived serde_yaml or deprecated serde_yml to a pure-Rust, `#![forbid(unsafe_code)]` crate. The compat shim and the per-crate migration guides make this cheaper.
- Parsing untrusted YAML. `ParserConfig::strict()` and `ParserLimits` cap depth, aliases, nodes, document size and more, and the docs report that billion-laughs input is rejected in under 3 us.
- no_std + alloc (with atomic pointers) or wasm32 targets, or tools that need fast parsing plus comment-preserving CST edits from one crate.

## Skip it when

- You need to beat libyaml, yaml-cpp or rapidyaml. None of them was measured. Derived from the page data, the parse-to-Value rate is about 32-64 MB/s on an M4, and the project's POLICIES.md gives about 36 MB/s for Value and 50-80 MB/s for typed parsing.
- You already use yaml-rust2 and parsing is not a bottleneck. The 1.11-1.36x (M4) gain means an API rewrite: there is no drop-in layer and no yaml-rust2 migration guide.
- Large documents. The comparison fixtures top out at 29 KB, and no MB-scale comparison against other crates is published.
- Code that relies on typed mapping keys. `Value::Mapping` is `IndexMap<String, Value>`, so integer, bool and complex keys are converted to strings unless you use `MappingAny`.
- Risk-averse production use. The crate has one main maintainer (OpenSSF Code-Review 0 per its own ECOSYSTEM.md), uses 0.0.x versions where a patch bump may break, and dozens of serializer and CST round-trip bugs were filed between 2026-08-30 and 2026-09-10 (all closed by 2026-09-16).

## How it is fast

The scanner hands out scalars as `Cow::Borrowed` when no escape forces a copy, and it finds delimiters with memchr's SSE2/NEON `memchr2`/`memchr3` plus a SWAR (8-byte `u64` stride) byte-set search for 4 or more needles. Integers are parsed by an 8-digits-per-`u64` SWAR decimal parser (measured 2.2-2.5x over `i64::from_str`), and the default `from_str` records no spans (docs: 34% less overhead). Typed `from_str::<T>` feeds parser events straight into the serde Visitor without building a Value AST (docs claim about 30% faster). The serializer's 3-4x lead over serde_yaml_ng comes from `itoa`/`ryu` direct-write buffers and fast detection of strings that need quotes.

## Compared with alternatives

It is the only Rust YAML library among the catalogued siblings, so pick it over rapidyaml, libfyaml, fkYAML or yeptris when you are in Rust and want serde binding and safe code without a C/C++ build. Those C/C++ siblings publish MB/s results against yaml-cpp or libyaml, and noyalib has never been measured against them.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | Always: serde_core, indexmap, rustc-hash, hashbrown, libm, memchr, smallvec. On by default and removable: itoa, ryu, serde_ignored. Opt-in: rayon, tokio, miette, schemars/jsonschema, figment, garde, validator, sval and others. |
| **Minimum toolchain** | Rust 1.86.0 (edition 2024). The `nightly-simd` feature needs nightly `portable_simd`; the `compare-saphyr` bench needs 1.88+. |
| **Platforms** | any Rust target with no hand-written intrinsics (memchr SSE2/NEON plus portable SWAR). CI runs x86-64 Linux/macOS/Windows and aarch64 macOS/Linux; no_std builds for thumbv7em and riscv32imac; wasm32. Targets without atomic CAS (thumbv6m, AVR, MSP430) are unsupported. |
| **Thread safety** | Documented: top-level functions are pure and can be called concurrently. Value, Mapping, Number, Spanned&lt;T&gt; and Error are Send + Sync. Spanned&lt;T&gt; deserialization uses a thread-local span context. The Rc-backed anchor registries are single-thread; the Arc variants are multi-thread. |
| **Drop-in for the baseline** | partial — not source-compatible with yaml-rust2 (`YamlLoader::load_from_str` / `Yaml`). A serde_yaml 0.9 name-for-name shim exists (`compat-serde-yaml` feature or the `noyalib-serde-yaml` crate). |

## Gotchas

- `from_str` rejects multi-document input with a 'more than one document' error (since v0.0.29). Use `load_all_as` or `from_str_multi` where yaml-rust2's `load_from_str` returned every document.
- The 4.2x / 9.2x `StructuralIter` result is a microbenchmark of a public primitive. `StructuralIter` does not appear in the scanner, scalar scanner or loader, so it does not contribute to the parse numbers, and the `simd` feature is a documented no-op.
- YAML 1.2 semantics are the default: `yes`/`no`/`on`/`off` stay strings and bare `0644` is not octal. `ParserConfig::version(YamlVersion::V1_1)` or the `legacy_*` flags opt back in.
- In the 0.0.x series the patch number is the breaking-change axis, including changes to Value shape or scalar resolution. Pin exact versions: three releases shipped on 2026-09-22 alone.

## Known shortcomings

- The headline Apple M4 table is likely older than the current code (it still has a serde_yml column and credits FxHasher, both since changed); the dated A18 Pro table is the current evidence. The 4.2x/9.2x SIMD StructuralIter figure is a standalone microbenchmark that does not feed parsing. No x86 numbers, no libyaml or yaml-cpp comparison, fixtures stop at 29 KB (Value parse about 32-64 MB/s). Mapping keys are strings. 0.0.x with one main maintainer and about 40 round-trip bugs filed and fixed in 2026-08/09.

## Caveats and trade-offs

baseline_in_list=false: yaml-rust2 is a widely-used pure-Rust YAML crate but not one of the five named incumbents (libyaml, yaml-cpp, toml++, libxml2, pugixml), and libyaml itself was never tested here. Numbers are entirely first-party (project's own criterion suite), though host/toolchain/flags are fully documented, meeting the Tier-A methodology bar on that basis. Results differ noticeably between the two disclosed hardware hosts (Apple M4 vs Apple A18 Pro), so treat exact ratios as approximate.

Never benchmarked against libyaml or yaml-cpp (this task's named baselines) -- only against other pure-Rust YAML crates; the margin over its closest competitor (yaml-rust2) is modest (1.11x-1.36x) versus the larger headline figures shown against weaker competitors; zero-unsafe pure-Rust design trades some of that narrower yaml-rust2 gap for safety plus Spanned&lt;T&gt;/Cow&lt;'a,str&gt;/Value::Tagged features yaml-rust2 lacks; very new/low-adoption project.

## Maintenance

Actively developed (v0.0.51 on 2026-09-22), installs as an ordinary crate, and is dual MIT/Apache-2.0 per the README and Cargo.toml (the GitHub API lists only Apache-2.0), with 10 stars but about 541k crates.io downloads over the last 90 days.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** docs/BENCHMARKS.md compares noyalib directly against yaml-rust2 (and serde_yaml_ng, serde_yml, yaml-spanned, serde-saphyr). It states Apple M4, Rust 1.95 stable and --release with LTO=fat, codegen-units=1, panic=abort. The benchmark code is public at crates/noyalib/benches/comparison.rs (SIMD scan: benches/structural_bitmask.rs). First-party, but it meets the A bar.
- **Verifier notes:** The numbers match the page, except that the lower end of the range against the other crates is 1.38x (yaml-spanned, large_list), not 1.42x. The README says the crate is dual-licensed Apache-2.0 OR MIT (LICENSE-APACHE and LICENSE-MIT), but the GitHub API reports only Apache-2.0. The only baselines are pure-Rust YAML crates, and libyaml/yaml-cpp are never tested; the existing caveat already says so. Metadata checked with gh: 10 stars, not a fork, last commit 2026-09-22.
- **Fields the verifier corrected:** `claimed_speedup`, `license`, `compiler_and_flags`
- **Pages the verifier opened:**
  - <https://github.com/sebastienrousseau/noyalib/blob/main/docs/BENCHMARKS.md>
  - <https://github.com/sebastienrousseau/noyalib>
  - <https://github.com/sebastienrousseau/noyalib/blob/main/README.md>
  - <https://github.com/sebastienrousseau/noyalib/tree/main/crates/noyalib/benches>
  - <https://github.com/sebastienrousseau/noyalib/blob/main/Cargo.toml>
- **Sources the enricher read:**
  - <https://github.com/sebastienrousseau/noyalib>
  - <https://github.com/sebastienrousseau/noyalib/blob/main/README.md>
  - <https://github.com/sebastienrousseau/noyalib/blob/main/docs/BENCHMARKS.md>
  - <https://github.com/sebastienrousseau/noyalib/blob/main/crates/noyalib/benches/comparison.rs>
  - <https://github.com/sebastienrousseau/noyalib/blob/main/crates/noyalib/benches/structural_bitmask.rs>
  - <https://github.com/sebastienrousseau/noyalib/tree/main/crates/noyalib/benches/fixtures>
  - <https://github.com/sebastienrousseau/noyalib/blob/main/Cargo.toml>
  - <https://github.com/sebastienrousseau/noyalib/blob/main/crates/noyalib/Cargo.toml>
  - <https://github.com/sebastienrousseau/noyalib/blob/main/crates/noyalib/src/lib.rs>
  - <https://github.com/sebastienrousseau/noyalib/blob/main/crates/noyalib/src/simd.rs>
  - <https://github.com/sebastienrousseau/noyalib/blob/main/crates/noyalib/src/parser/scanner.rs>
  - <https://github.com/sebastienrousseau/noyalib/blob/main/crates/noyalib/src/parser/scanner/scalars.rs>
  - <https://github.com/sebastienrousseau/noyalib/blob/main/crates/noyalib/src/parser/loader.rs>
  - <https://github.com/sebastienrousseau/noyalib/blob/main/crates/noyalib/src/value/mapping.rs>
  - <https://github.com/sebastienrousseau/noyalib/blob/main/docs/ARCHITECTURE.md>
  - <https://github.com/sebastienrousseau/noyalib/blob/main/docs/COMPARISON.md>
  - <https://github.com/sebastienrousseau/noyalib/blob/main/docs/ECOSYSTEM.md>
  - <https://github.com/sebastienrousseau/noyalib/blob/main/docs/POLICIES.md>
  - <https://github.com/sebastienrousseau/noyalib/blob/main/docs/README-REFERENCE.md>
  - <https://github.com/sebastienrousseau/noyalib/blob/main/CHANGELOG.md>
  - <https://github.com/sebastienrousseau/noyalib/issues>
  - <https://github.com/sebastienrousseau/noyalib/issues/351>
  - <https://github.com/sebastienrousseau/noyalib/releases>
  - <https://crates.io/api/v1/crates/noyalib>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/sebastienrousseau/noyalib`) · [data/wave4/enrich/raw/github_com_sebastienrousseau_noyalib.json](../../../data/wave4/enrich/raw/github_com_sebastienrousseau_noyalib.json) (enrichment confidence 0.72)

</details>
