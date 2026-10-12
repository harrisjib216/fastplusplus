# Biome

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Formatters, linters and language servers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Rust toolchain combining a formatter (97% Prettier-compatible) and linter (500+ rules) that replace ESLint and Prettier/dprint.

| | |
|---|---|
| **Beats** | ESLint (linting); Prettier and dprint (formatting) |
| **Claimed result** | Formatting: \~25x faster than Prettier, \~20x faster than parallel-prettier and than xargs -P prettier, 1.5 to 2x faster than dprint, single-threaded \~7x faster than Prettier; '100 times faster than Prettier on an M1 Max with 10 cores'. Linting: \~15x faster than ESLint (without plugins), single-threaded \~4x. These were measured on Rome, Biome's predecessor, in Nov 2022. |
| **Workload** | Wall time of formatting (Prettier, dprint) and linting (ESLint, only rules both tools support, no type-aware rules) on real JS/TS repos cloned by benchmark/bench.js (webpack, prettier and eslint sources). Formatting runs on already-formatted files after 2 hyperfine warmups. The published numbers come from the 2022 Rome-era run on target/webpack. |
| **Metric** | throughput |
| **Hardware** | MacBook Pro 13-inch, M1, 2020 (also notes an M1 Max 10-core run for the 100x figure) |
| **Adoption** | 25.9k stars |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/biomejs/biome) · [benchmark](https://github.com/biomejs/biome/blob/fdf8555f57dbb763f5dfcbe27be89814b2d0df0c/benchmark/README.md) |

## Verdict

The only public numbers are Nov 2022 hyperfine runs on a MacBook Pro 13-inch M1 (2020) comparing Biome's Rome-era predecessor against Prettier, parallel-prettier/xargs -P prettier, and dprint for formatting (\~25x, \~20x, \~20x, and 1.5-2x faster respectively, single-threaded \~7x), and against ESLint for linting (\~15x faster, rules both tools support, no type-aware rules, single-threaded \~4x), plus a separate M1 Max 10-core run cited for a '100x faster than Prettier' figure. No compiler flags, tool versions, or raw output are given, and the benchmark/ directory that produced these numbers was deleted from main in commit 8e4ada5 (2026-05-13).

## Use it when

- You already run Prettier (or dprint) + ESLint on JS/TS/JSON/CSS/GraphQL and want one faster CLI/LSP, bootstrapped from existing configs via `biome migrate`.
- Editor-in-the-loop formatting/linting on medium-large monorepos where ESLint's per-keystroke latency is the pain point — Biome's LSP targets interactive use.
- CI wants a fast cold full-repo check across JS/TS/CSS/GraphQL without needing type-aware rules.
- You want a self-contained native binary with no Node.js dependency for the CLI itself (the npm package just wraps a platform binary).
- You want broad out-of-the-box rule coverage (500+ rules pulled from ESLint/typescript-eslint/jsx-a11y/unicorn) without assembling an ESLint plugin stack.

## Skip it when

- You depend on ESLint plugins or custom rules with no Biome equivalent — `biome migrate eslint` only maps recognized rules (eslint, typescript, jsx-a11y, unicorn, jest), not arbitrary plugins.
- You need full type-aware lint parity with typescript-eslint: Biome's type-aware 'project domain' rules (noFloatingPromises, noUnresolvedImports, noImportCycles) are new in v2, opt-in, and docs cite performance dropping from \~800ms to \~2s per 2,000 files when enabled.
- You rely on incremental/cached formatting for large repos with few changed files — Biome has no incremental formatting like Prettier/dprint; every run is a cold run.
- You want to cite the headline speedup numbers as current: the published \~25x/\~15x figures are Nov 2022 Rome-era hyperfine runs, never re-measured, and the benchmark/ code that produced them was deleted from main in May 2026.
- Your codebase has deeply parenthesized object expressions in arrow functions (`() => ({...})`) — a real regression made formatting 'dramatically slower' on that shape between 2.5.10 and 2.5.11 (GH #11747), a sign perf isn't uniformly stable release-to-release.

## How it is fast

It's compiled Rust, avoiding Node.js/V8 startup and interpreter overhead. Formatting and linting run against one shared lossless CST (biome_rowan, a rowan-style Green/Red tree that preserves full trivia) instead of each tool doing its own parse. Biome's own benchmark notes say the linter batches rule matching against one semantic model and control-flow graph rather than running each rule as an independent AST visitor, and the CLI parallelizes file processing across threads (tunable via the BIOME_THREADS env var). The scanner also skips filesystem traversal into folders irrelevant to the current run when project-wide type rules are disabled.

## Compared with alternatives

Pick Biome over Oxlint when you need one tool for both formatting and linting plus LSP/editor support and a Prettier-config migrator; Oxlint's README claims \~2x faster linting than Biome and 50-100x vs ESLint but is lint-only with no formatter. Ruff is the closest analog outside JS (Rust linter+formatter replacing Flake8+Black) if you're evaluating the pattern rather than a JS-specific tool.

## Integration

| | |
|---|---|
| **Form** | crate (Rust workspace of 100+ biome_\* crates), distributed as a prebuilt native CLI binary via the @biomejs/biome npm package |
| **Dependencies** | none to run (self-contained native binary; npm install only adds one platform-specific optionalDependency binary, no JS deps). Building from source needs the Rust toolchain. |
| **Minimum toolchain** | Rust edition 2024 (\~1.85+) to build from source; via npm, Node.js &gt;=14.21.3 is only the install mechanism, not required to run the binary |
| **Platforms** | linux-x64/arm64 (glibc + musl), darwin-x64/arm64, win32-x64/arm64 (per npm optionalDependencies); also compiles to WASM for the online playground |
| **Thread safety** | not documented in detail — the architecture docs' parallelism/daemon sections are marked 'work in progress'; the CLI exposes a BIOME_THREADS env var to control worker threads, implying multi-threaded file processing |
| **Drop-in for the baseline** | partial — explain: formatting claims 97% Prettier compatibility and ships `biome migrate prettier`, so it's close to drop-in for Prettier; linting is not drop-in for ESLint — different config format/rule engine, no ESLint plugin support, and `biome migrate eslint` only best-effort converts recognized rules |

## Gotchas

- Type-aware lint rules (project domain: noFloatingPromises, noUnresolvedImports, noImportCycles) are opt-in and materially slower — docs cite \~800ms to \~2s per 2,000 files when enabled, plus higher memory use.
- No incremental/cached formatting: every `biome format`/`check` run reformats cold, unlike Prettier/dprint — confirmed in Biome's own benchmark notes.
- Formatter hit a real perf cliff on large parenthesized object expressions in arrow functions, reported as 'dramatically slower' between 2.5.10 and 2.5.13 (GH #11747).
- Dual-licensed MIT OR Apache-2.0 per Cargo.toml/package.json, though GitHub's repo-level license detection reports just Apache-2.0.

## Caveats and trade-offs

The benchmark/ directory was removed from main in 8e4ada5 ('chore: remove benchmark from repository', #10355, 2026-05-13). fdf8555f (2026-04-27, a dprint bump) is the last commit that touched benchmark/, and its README matches the removal commit's parent. The numbers are Nov 2022 Rome measurements, rounded and never re-run. At the cited commit, bench.js has parallel-prettier commented out ('crashing on Node 22') and pins eslint 9.39.4, prettier 3.8.3 and dprint 0.54.0, so the code does not reproduce the stated setup. The biomejs.dev homepage now claims '\~35x faster than Prettier when formatting 171,127 lines of code in 2,104 files with an Intel Core i7 1270P', but it links to tree/main/benchmark, which no longer exists.

Linting comparison only enables rules both tools support and excludes type-aware rules (favors Biome, which lacks type-aware linting); Biome does not support incremental/cached formatting the way Prettier and dprint do, so the cold-format comparison is the favorable case for Biome.

## Maintenance

Actively maintained (pushed 2026-09-24, 25.9k stars, not archived); dual MIT/Apache-2.0, published as compiled binaries for every major OS/arch, so it's safe to adopt for day-to-day formatting/linting today — just don't cite the 2022 speedup numbers as current without re-benchmarking.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): downgrade; tier before verification A, tier now C.
- **Tier reason:** The README at fdf8555f gives only rounded figures (\~25x Prettier, \~15x ESLint on an M1 MacBook Pro), with no raw output and no tool versions. History shows these figures are the Nov 2022 Rome-era results (commit ec1feb472a, text renamed Rome-&gt;Biome) and were never re-measured. The cited commit's benchmark/bench.js is a 2024 rewrite with 2026 dependency pins that disables parallel-prettier, so the public code does not reproduce the stated numbers. That makes them first-party numbers with partial methodology: C, not A.
- **Verifier notes:** Downgraded from A to C because the published numbers are stale, rounded Rome-era (2022) figures not produced by the cited code. The homepage's \~35x (i7-1270P) claim may have its own source worth tracking down in enrichment. Metadata checked: Apache-2.0 (spdx; benchmark package.json says MIT OR Apache-2.0), 25853 stars, last commit 2026-09-24.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/biomejs/biome>
  - <https://github.com/biomejs/biome/blob/fdf8555f57dbb763f5dfcbe27be89814b2d0df0c/benchmark/README.md>
  - <https://github.com/biomejs/biome/blob/fdf8555f57dbb763f5dfcbe27be89814b2d0df0c/benchmark/bench.js>
  - <https://github.com/biomejs/biome/blob/fdf8555f57dbb763f5dfcbe27be89814b2d0df0c/benchmark/package.json>
  - <https://github.com/biomejs/biome/commit/8e4ada5163fa8124d5e8fbc6a3aefa5a3ed32496>
  - <https://github.com/biomejs/biome/commit/fdf8555f57dbb763f5dfcbe27be89814b2d0df0c>
  - <https://github.com/biomejs/biome/commit/b03b8dcf12cb8bcf65df0b3d0758ae2b7050e9fe>
  - <https://github.com/biomejs/biome/commit/ec1feb472a77828479ba2027010ce0ae32484d74>
  - <https://biomejs.dev/>
- **Sources the enricher read:**
  - <https://github.com/biomejs/biome>
  - <https://github.com/biomejs/biome/blob/HEAD/Cargo.toml>
  - <https://github.com/biomejs/biome/blob/HEAD/packages/%40biomejs/biome/package.json>
  - <https://github.com/biomejs/biome/blob/HEAD/crates/biome_rowan/README.md>
  - <https://github.com/biomejs/biome/blob/fdf8555f57dbb763f5dfcbe27be89814b2d0df0c/benchmark/README.md>
  - <https://github.com/biomejs/biome/issues/11747>
  - <https://biomejs.dev/linter/>
  - <https://biomejs.dev/internals/architecture/>
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/biomejs/biome`) · [data/wave2/enrich/raw/github_com_biomejs_biome.json](../../../data/wave2/enrich/raw/github_com_biomejs_biome.json) (enrichment confidence 0.75)

</details>
