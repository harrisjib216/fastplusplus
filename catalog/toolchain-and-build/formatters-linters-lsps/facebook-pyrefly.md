# Pyrefly

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Formatters, linters and language servers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust type checker and LSP for Python; faster than mypy and Pyright on cold, whole-project checks.

| | |
|---|---|
| **Beats** | mypy; Pyright |
| **Claimed result** | README: checks over 1.85M lines of code per second and type-checks projects like PyTorch 15x faster than mypy and Pyright (no methodology given). Astral's public ty_benchmark (blog dated 2025-12-16), cold CLI check of home-assistant on M4 with no cache: Pyrefly 5.32s vs Pyright 19.62s vs mypy 45.66s, so Pyrefly is \~3.7x faster than Pyright and \~8.6x faster than mypy (derived from page data). In the same post's LSP incremental re-check on pytorch, Pyrefly was the slowest of the three: 2.60s vs Pyright 370.5ms vs ty 4.5ms (chart values; the prose gives 2.38s / 386ms / 4.7ms). |
| **Workload** | First-party: type-checking PyTorch. Third-party reproducible check: cold CLI type-check of home-assistant/core on Apple M4 (astral ty_benchmark harness) |
| **Metric** | throughput |
| **Hardware** | Apple M4 (exact variant/RAM not specified) |
| **Adoption** | 7.0k stars; default type checker for Meta's Instagram codebase (\~20M LOC), adopted by PyTorch and JAX |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/facebook/pyrefly) · [benchmark](https://astral.sh/blog/ty) |

## Verdict

Astral's ty_benchmark harness (public, pinned revisions) ran a cold CLI type-check of home-assistant/core with no cache on an Apple M4: Pyrefly 5.32s vs Pyright 19.62s (\~3.7x faster) vs mypy 45.66s (\~8.6x faster). The same post's LSP incremental-recheck test on PyTorch showed Pyrefly was the slowest of the three, \~2.4-2.6s vs Pyright's \~370-386ms and ty's \~4.5-4.7ms; no compiler flags are relevant since these are prebuilt/uv-installed binaries, hardware is stated only as 'M4'.

## Use it when

- Cold or CI type-checks of large, multi-module Python codebases (millions of LOC) where batch throughput matters more than incremental recheck latency
- Migrating an existing mypy or Pyright project and wanting built-in tooling (`pyrefly init`, `pyrefly suppress`) to stage the rollout
- Codebases heavy on Pydantic, Django, or pytest patterns, where Pyrefly's built-in framework modeling reduces false positives
- Wanting one tool that is both the CLI checker and the editor LSP with consistent results (VS Code, Neovim, Zed)
- Multi-core CI machines, since checking parallelizes across modules with rayon

## Skip it when

- Editor-driven inner loop where every-keystroke/save recheck latency matters most: Astral's benchmark measured Pyrefly's incremental LSP recheck on PyTorch at \~2.4-2.6s, versus \~370ms for Pyright and \~4.5ms for ty
- Memory-constrained dev machines: multiple open issues report very high RSS, including one reporting the VS Code extension reaching up to 100GB on a large repo
- Older Linux hosts on glibc 2.17, where a memory-allocation crash has been reported
- Teams that need strict semver stability: Pyrefly's own version policy states monthly minor releases can introduce new type errors or other breaking changes
- Relying on the README's PyTorch '15x faster than mypy/Pyright' headline for capacity planning — no hardware or methodology is published for it

## How it is fast

The whole tool is a single Rust binary; type-checking is parallelized across modules with rayon, backed by concurrent data structures (dashmap, parking_lot) and jemalloc/mimalloc allocators. Per its own ARCHITECTURE.md, it deliberately favors module-level incrementality over fine-grained, binding-level incrementality (the Salsa/rust-analyzer or Roslyn/TypeScript approach): each module's bindings are solved sequentially and completely, betting that whole-module solving is fast enough that finer-grained caching isn't needed. That design gives fast cold/batch checks but is the likely reason its LSP incremental recheck lagged both Pyright and ty in Astral's benchmark.

## Compared with alternatives

Pick Pyrefly over ty (astral-sh/ty) when you value production-scale proof (Instagram's 20M-LOC codebase, PyTorch, JAX adoption) and built-in Pydantic/Django/pytest modeling over raw speed — in the same benchmark ty beat Pyrefly on both cold checks (2.19s vs 5.32s) and, by a wide margin, incremental LSP rechecks (4.5ms vs 2.6s).

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none to run (pip install pyrefly ships a prebuilt Rust binary); building from source pulls a Rust workspace (rayon, dashmap, parking_lot, lsp-server, ruff_python_parser/ruff_notebook, tokio, etc.) |
| **Minimum toolchain** | Rust stable, edition 2024 (Rust 1.85+) to build from source; rust-toolchain.toml pins channel=stable with no exact version |
| **Platforms** | Linux x86_64/i686/aarch64 (glibc and musl), macOS x86_64/arm64, Windows x86_64/i686/aarch64 — all built as prebuilt release binaries |
| **Thread safety** | not documented as an embeddable library API; internally parallelizes checking across modules via rayon/dashmap/parking_lot |
| **Drop-in for the baseline** | partial — separate CLI, config file, and error set from mypy/Pyright; provides `pyrefly init`/`suppress`/`infer` to ease migration and can read some existing Mypy/Pyright config values |

## Gotchas

- README claims IDE rechecks 'typically complete in under 10 milliseconds,' but Astral's independent benchmark measured 2.4-2.6s for Pyrefly's LSP recheck on PyTorch — a large, credible gap
- Multiple open GitHub issues report excessive memory use, including one titled 'Pyrefly consumes A LOT of memory' and another reporting the VS Code extension using up to 100GB
- Reported crash allocating memory on glibc 2.17 (older Linux distros)
- Does not follow strict semver: any minor version bump (monthly) may add new type errors or change behavior; `pyrefly suppress` exists specifically to manage that churn

## Caveats and trade-offs

The Tier A evidence comes from astral's ty_benchmark, run by a competing project (Astral/ty), not by Pyrefly's team or a neutral third party. The code is public and pins project revisions and tool versions (pyrefly&gt;=0.43.1 locked in uv.lock), and the machine is stated only as 'M4'. The run dates from December 2025, so it predates about 9 months of Pyrefly releases. The README claims 'rechecks typically complete in under 10 milliseconds', but the astral LSP benchmark measured 2.38-2.60s for Pyrefly on pytorch. The README's '15x on PyTorch' claim has no traceable methodology and would support only Tier C on its own.

Pyrefly's own PyTorch-based "15x faster" headline is unverified in this session (no hardware/methodology found); the corroborating cold-check numbers (\~3.7-8.6x vs Pyright/mypy) are smaller than that headline, and Pyrefly's LSP incremental re-check was the slowest of the three checkers in the same harness, so speedup is workload-dependent.

## Maintenance

Actively maintained — commits as of today (2026-09-24), monthly minor releases, 1.0 tagged as stable; MIT-licensed and installable as a prebuilt binary via pip, so adoption cost is low despite the non-semver upgrade churn.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification A, tier now A.
- **Tier reason:** astral.sh/blog/ty cold-CLI chart has a Pyrefly row next to mypy and Pyright (5.32s vs 45.66s vs 19.62s on home-assistant, M4). The harness is public at astral-sh/ruff scripts/ty_benchmark (commit 7f7485d): hyperfine, no cache, projects pinned to git revisions in src/benchmark/projects.py, tool versions locked in uv.lock/package-lock.json.
- **Verifier notes:** Numbers and ratios check out against the chart. The blog prose and chart disagree slightly on the LSP numbers, so both are recorded. Metadata verified: MIT, 7004 stars, last commit 2026-09-24, not a fork or archived.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://astral.sh/blog/ty>
  - <https://github.com/astral-sh/ruff/blob/7f7485d608d2da19a0632a1238f2d4be551f612f/scripts/ty_benchmark/README.md>
  - <https://github.com/astral-sh/ruff/tree/7f7485d608d2da19a0632a1238f2d4be551f612f/scripts/ty_benchmark>
  - <https://github.com/facebook/pyrefly>
- **Sources the enricher read:**
  - <https://github.com/facebook/pyrefly>
  - <https://github.com/facebook/pyrefly/blob/main/README.md>
  - <https://github.com/facebook/pyrefly/blob/main/ARCHITECTURE.md>
  - <https://github.com/facebook/pyrefly/blob/main/Cargo.toml>
  - <https://github.com/facebook/pyrefly/blob/main/pyrefly/Cargo.toml>
  - <https://github.com/facebook/pyrefly/blob/main/rust-toolchain.toml>
  - <https://github.com/facebook/pyrefly/blob/main/.github/workflows/release_binaries.yml>
  - <https://github.com/facebook/pyrefly/issues>
  - <https://github.com/facebook/pyrefly/releases>
  - <https://astral.sh/blog/ty>
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/facebook/pyrefly`) · [data/wave2/enrich/raw/github_com_facebook_pyrefly.json](../../../data/wave2/enrich/raw/github_com_facebook_pyrefly.json) (enrichment confidence 0.6)

</details>
