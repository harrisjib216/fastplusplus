# Oxlint (oxc-project/oxc)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Formatters, linters and language servers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust-based JavaScript/TypeScript linter and toolchain that replaces ESLint with 50-100x faster linting.

| | |
|---|---|
| **Beats** | ESLint |
| **Claimed result** | README summary: 'Oxlint is 50x - 100x faster than ESLint depending on the number of CPU cores' and '\~2x faster than Biome'. VS Code, standard rules, vs ESLint v9: 62.10x (M2 Max 12-core), 118.25x (M4 Max), 60.09x (M3 Air 8-core); single-threaded Oxlint is \~17x faster than ESLint on M2 Max (derived from page data: 31.025s / 1.824s). Vs Biome (VS Code; bench.sh uses a single no-debugger rule): 2.72x, 2.49x, 3.31x. Type-aware rules vs typescript-eslint (M2 Max): 8.22x on Vue core, 12.38x on Sentry. |
| **Workload** | Linting the VS Code src tree with standard rules (the Biome comparison uses only the no-debugger rule), plus Vue core and Sentry with type-aware rules vs typescript-eslint. Timed with hyperfine (1 warmup, non-zero exits ignored), with no ESLint cache. |
| **Metric** | throughput |
| **Hardware** | MacBook Pro M2 Max (12-core); MacBook Pro M4 Max 64GB; MacBook Air M3 24GB 8-core |
| **Compiler and flags** | hyperfine -w 1 -i; oxlint -c .oxlintrc.json (plus a --threads=1 run) vs eslint -c eslint.config.mjs (ESLint v9 per README); prebuilt npm binaries, exact versions pinned only in pnpm-lock |
| **Adoption** | 22.9k stars (oxc monorepo) |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/oxc-project/oxc) · [benchmark](https://github.com/oxc-project/bench-linter) |

## Verdict

Oxc's own bench-linter repo (hyperfine, 1 warmup, non-zero exits ignored, ESLint v9, no ESLint cache) measured Oxlint linting the VS Code source tree at 62.10x/118.25x/60.09x ESLint's speed on an M2 Max 12-core / M4 Max / M3 Air 8-core respectively, and \~17x single-threaded (31.025s vs 1.824s on M2 Max); vs Biome on the same tree with only the no-debugger rule enabled, 2.72x/2.49x/3.31x across the same three machines; vs typescript-eslint with type-aware rules on Vue core and Sentry (M2 Max), 8.22x and 12.38x respectively.

## Use it when

- Large JS/TS monorepos where ESLint's per-file startup and plugin dispatch overhead dominates CI time
- Standard-rule linting (no exotic plugin needs) where raw throughput matters more than full rule-set parity
- Multi-core CI runners or dev machines, since the speedup scales with thread count
- Teams migrating incrementally, running Oxlint alongside ESLint to cover the remaining rule gap
- Projects wanting near-instant `npx oxlint` feedback with zero required config

## Skip it when

- Codebases that depend on ESLint plugins with no Oxlint equivalent or JS-plugin bridge
- Projects needing full type-aware linting parity with typescript-eslint - gain drops to 8-12x and rule coverage is narrower, and it needs the separate oxlint-tsgolint/TypeScript 7 component
- Repos still on legacy ESLint v8 config - must convert to flat config via @eslint/migrate-config before the official migration tool works
- Setups with local/custom ESLint plugins - these do not migrate automatically
- Single-core or low-core environments, where the advantage shrinks toward the \~17x single-threaded figure

## How it is fast

Oxlint reuses oxc's own parser and semantic analyzer, built on an arena allocator (oxc_allocator), so most rules run in a single AST traversal instead of ESLint's per-rule/per-plugin dispatch. Files are linted in parallel across CPU cores via Rayon, with the `ignore` crate (SIMD-accelerated) walking the file tree, so throughput scales with core count. That parallelism is why the gap widens on more cores: \~17x single-threaded vs ESLint, up to \~62-118x multi-threaded on 8-12 core machines in the project's own benchmark.

## Compared with alternatives

Over Biome specifically: the same VS Code benchmark run by the Oxc project shows Oxlint 2.5-3.3x faster (though that test used only the no-debugger rule, so treat it as a floor, not a full-ruleset comparison). The other catalogued siblings (Ruff, Pyrefly, ty, clangd-tidy) target Python or C++, so within JS/TS linting Oxlint is the only ESLint-throughput entry here besides Biome.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | Rust workspace of internal oxc_\* crates (oxc_allocator, oxc_parser, oxc_linter, oxc_semantic, ...) plus rayon, bpaf, napi, tower-lsp-server; npm CLI package ships a prebuilt native binary with no user-facing JS deps |
| **Minimum toolchain** | Rust 1.96.0 (workspace MSRV, N-2 policy), edition 2024; no Rust toolchain needed to use the prebuilt npm binary |
| **Platforms** | Linux (glibc/musl; x86-64, arm/aarch64, riscv64, powerpc64le), macOS (x86-64, arm64), Windows (x86-64, i686, arm64), plus wasm and OpenHarmony targets per the npm package's optionalDependencies |
| **Thread safety** | not documented for the Rust crates as an embeddable library API; the CLI itself parallelizes file processing across threads via Rayon (thread count configurable, e.g. --threads=1 for single-threaded runs) |
| **Drop-in for the baseline** | partial — explain: reads ESLint's flat config format and reports similar diagnostics, but implements a subset of ESLint's rules with a different plugin architecture, and needs the separate oxlint-tsgolint component for type-aware TS rules |

## Gotchas

- Legacy ESLint v8 configs must be converted to flat config first (via @eslint/migrate-config) before the @oxlint/migrate tool works
- Local/custom ESLint plugins don't migrate automatically and need manual setup
- Type-aware rules require the separate oxlint-tsgolint binary, which depends on TypeScript 7
- The published Oxlint-vs-Biome benchmark enables only a single rule (no-debugger) on both linters, so the \~2x figure isn't representative of full rule-set performance

## Caveats and trade-offs

Run and published by the Oxc project itself. Oxlint and ESLint versions for the published runs are not stated beyond 'ESLint v9'. The repo's package.json now requires eslint ^10, and bench.sh adds an 'eslint --concurrency=auto' run that the README results do not show, so the published numbers predate the current config: VS Code results were last updated 2025-05/09, type-aware results 2025-12. The 50-100x headline applies only to standard rules; with type-aware rules the gain is 8-12x. The Biome comparison uses a single rule. The benchmark repo itself has no LICENSE file (its package.json says MIT).

Oxlint implements a subset of ESLint's rule set (no plugin ecosystem parity yet); type-aware linting benchmark excludes rules requiring full type info to keep comparison fair, which understates ESLint+typescript-eslint's real-world cost but also means Oxlint's rule coverage is narrower.

## Maintenance

Actively maintained (commits as recent as today, 22.9k stars across the oxc monorepo) with VoidZero backing; MIT licensed and directly usable via `npx oxlint`, though ESLint rule/plugin parity is still incomplete.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification A, tier now A.
- **Tier reason:** oxc-project/bench-linter publishes the harness (bench-vscode/bench.sh, bench-vue, bench-sentry: hyperfine -w 1 -i with the oxlint/eslint command lines and configs). The README shows raw hyperfine output against ESLint v9 with each machine named (M2 Max 12-core, M4 Max, M3 Air 8-core). Code, configuration and CPU are all stated, so A.
- **Verifier notes:** Tier A stands. The record's claim left out the much lower type-aware results (8.22x and 12.38x) even though its workload lists type-aware rule sets, so I added them to claimed_speedup. Metadata checked: MIT, 22871 stars, last commit 2026-09-24, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/oxc-project/oxc>
  - <https://github.com/oxc-project/bench-linter>
  - <https://github.com/oxc-project/bench-linter/blob/main/README.md>
  - <https://github.com/oxc-project/bench-linter/blob/main/bench-vscode/bench.sh>
  - <https://github.com/oxc-project/bench-linter/blob/main/package.json>
- **Sources the enricher read:**
  - <https://github.com/oxc-project/oxc>
  - <https://github.com/oxc-project/oxc/blob/main/README.md>
  - <https://github.com/oxc-project/oxc/blob/main/npm/oxlint/README.md>
  - <https://github.com/oxc-project/oxc/blob/main/apps/oxlint/Cargo.toml>
  - <https://github.com/oxc-project/oxc/blob/main/crates/oxc_linter/README.md>
  - <https://github.com/oxc-project/oxc/blob/main/Cargo.toml>
  - <https://github.com/oxc-project/oxc/blob/main/npm/oxlint/package.json>
  - <https://oxc.rs/docs/guide/usage/linter/migrate-from-eslint.html>
  - <https://github.com/oxc-project/bench-linter>
  - <https://github.com/oxc-project/bench-linter/blob/main/README.md>
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/oxc-project/oxc`) · [data/wave2/enrich/raw/github_com_oxc_project_oxc.json](../../../data/wave2/enrich/raw/github_com_oxc_project_oxc.json) (enrichment confidence 0.85)

</details>
