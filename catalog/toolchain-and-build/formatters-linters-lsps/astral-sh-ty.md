# ty

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Formatters, linters and language servers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust-based Python type checker and language server from Astral; 10-100x faster cold checks than mypy and Pyright.

| | |
|---|---|
| **Beats** | mypy; Pyright |
| **Claimed result** | Cold CLI check on home-assistant (no cache, M4): ty 2.19s vs Pyrefly 5.32s vs Pyright 19.62s vs mypy 45.66s, so ty is \~9x faster than Pyright and \~21x faster than mypy (derived from page data). Blog prose: 'without caching, ty is consistently between 10x and 60x faster than mypy and Pyright'. LSP incremental re-check after editing a file in pytorch, chart values: ty 4.5ms vs Pyright 370.5ms vs Pyrefly 2.60s, so ty is \~82x faster than Pyright and \~578x faster than Pyrefly (derived from page data). The prose gives 4.7ms, 'ty is 80x faster than Pyright (386ms) and 500x faster than Pyrefly (2.38 seconds)'. README headline: '10x - 100x faster than mypy and Pyright'. |
| **Workload** | Cold CLI type-check of home-assistant/core (no cache); incremental re-check latency in the language server after editing one file in pytorch/pytorch |
| **Metric** | latency |
| **Hardware** | Apple M4 (exact variant/RAM not specified) |
| **Adoption** | 19.7k stars |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/astral-sh/ty) · [benchmark](https://astral.sh/blog/ty) |

## Verdict

Astral's own blog (astral.sh/blog/ty, dated 2025-12-16) reports, on an Apple M4: cold no-cache CLI type-check of home-assistant/core at ty 2.19s vs Pyrefly 5.32s vs Pyright 19.62s vs mypy 45.66s (\~9x over Pyright, \~21x over mypy), and LSP incremental re-check after editing a file in pytorch/pytorch at ty 4.5ms vs Pyright 370.5ms vs Pyrefly 2.60s (\~82x over Pyright, \~578x over Pyrefly; prose cites slightly different 4.7ms/386ms/2.38s). No tool versions or exact M4 variant/RAM are stated on the page; the harness (astral-sh/ruff scripts/ty_benchmark) is public with pinned lockfiles. The repo's own BENCHMARKS.md, run separately on an Apple M3 Max (128GB) with pinned versions (ty 0.0.55, Pyright 1.1.410, mypy 2.1.0, Pyrefly 1.1.1), corroborates the same ranking on other projects (e.g. Black: ty 69.5ms vs Pyrefly 128.3ms vs mypy 1.316s vs Pyright 1.420s) though with different magnitudes than the blog.

## Use it when

- Large monorepos where cold, no-cache CLI type-check latency matters (CI, pre-commit)
- IDE/language-server usage where sub-second incremental re-check after each keystroke/save matters
- Projects already on the Astral toolchain (uv, Ruff) wanting one vendor for lint/format/type-check
- Teams willing to tolerate a beta, fast-moving type checker in exchange for speed
- Python 3.10+ targeted codebases (earlier versions type-check with more false positives/negatives)

## Skip it when

- Projects needing a stable, versioned API/behavior contract — ty is 0.0.x with no stable-API guarantee and diagnostics can change between any two releases
- Codebases relying on mypy/pyright-specific strict-mode flags or plugins with no ty equivalent yet (see docs/coming-from-mypy-or-pyright.md rule-mapping gaps)
- Code with very complex/deeply nested expressions where bidirectional type inference has known 'dismal performance' and regression reports (astral-sh/ty#3180, #3505)
- Warm/cached CLI re-check comparisons — the headline benchmark is a no-cache scenario; only mypy supports warm cached re-checks in that comparison, so it doesn't show ty's cache-hit CLI behavior
- Teams that need mature third-party plugin ecosystems (e.g. mypy plugins) that ty doesn't support

## How it is fast

Written in Rust and built on the `salsa` incremental-computation framework (the same query/memoization engine used by rust-analyzer), giving fine-grained incremental re-analysis so editing one file only recomputes affected queries instead of re-checking the project. It parallelizes work with `rayon`, and on Linux/other non-macOS/Windows targets swaps in `tikv-jemallocator` for allocation-heavy workloads. Cold/no-cache runs are fast because the whole pipeline (parsing, semantic indexing, inference) is Rust-native rather than Python, unlike mypy.

## Compared with alternatives

Versus Pyrefly (the only true sibling here — same baseline of mypy/Pyright): pick ty when incremental LSP re-check latency matters most (Astral's benchmark shows ty beating Pyrefly by \~500x on that metric) and you want a public, pinned, reproducible benchmark harness rather than Pyrefly's README claim with no stated methodology; pick Pyrefly if you need functionality ty doesn't yet have. Biome/Oxlint/clangd-tidy/Ruff aren't real alternatives here — different languages or different tool category (linting/formatting, not type checking).

## Integration

| | |
|---|---|
| **Form** | source-drop (prebuilt standalone binary / PyPI wheel built via maturin from a Rust binary crate in the astral-sh/ruff monorepo) |
| **Dependencies** | none (Python package pyproject.toml declares zero deps; the Rust binary statically bundles its own dependencies) |
| **Minimum toolchain** | none required to use it (install via uvx/pipx/pip/standalone installer/Docker); building from source requires Rust 1.96+ per astral-sh/ruff's workspace Cargo.toml |
| **Platforms** | macOS, Linux, Windows (prebuilt binaries via GitHub Releases, PyPI wheels, standalone installer script, Docker image ghcr.io/astral-sh/ty) |
| **Thread safety** | not documented as an embeddable library (it's used as a CLI/LSP binary, not linked as a crate); internally parallelizes with rayon and uses salsa's incremental scheduler |
| **Drop-in for the baseline** | partial — CLI shape (`ty check`) and pyproject.toml config resemble mypy/pyright, but suppression syntax (`# ty: ignore[rule]`), rule names, and strict-mode behavior differ; docs/coming-from-mypy-or-pyright.md documents the rule mapping and gaps |

## Gotchas

- 0.0.x versioning: no stable API yet, diagnostics/behavior can change between any two releases (README 'Version policy')
- Default checking mode is stricter than mypy/pyright defaults in several ways (e.g. always checks unannotated function bodies) with no flag to relax it, which can surface new errors when migrating
- Complex/deeply nested expressions can trigger severe slowdowns from bidirectional type inference cost (open issues: 'Dismal performance when some complex expressions exist', a sympy performance regression)
- The astral-sh/ty GitHub repo is mostly packaging/docs; the actual Rust type-checker source lives in the astral-sh/ruff repo's crates/ty\* via a git submodule

## Caveats and trade-offs

The ty team designed and ran this benchmark on its own project. It compares ty favorably against competitors, including Pyrefly from this same batch, so it is not an independent third party. The harness (astral-sh/ruff/scripts/ty_benchmark) is public and reproducible. The blog does not state tool versions: they are pinned only through the harness lockfiles, and the only hardware given is 'M4' (variant and RAM not stated). The blog post is dated 2025-12-16. The astral-sh/ty repo is mostly packaging and docs (GitHub reports Python), and the Rust type-checker source lives in astral-sh/ruff.

ty is still in beta with an unstable API and incomplete type-system coverage vs. mature mypy/Pyright; only mypy supports warm/cached re-checks in this benchmark, so the cold-check comparison favors checkers with fast cold starts.

## Maintenance

Actively developed beta from Astral (same team as Ruff/uv), with commits as recent as today; MIT licensed and usable now via uvx/pipx/pip, but the 0.0.x version policy means no stable API and diagnostics can change release to release.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification A, tier now A.
- **Tier reason:** The blog charts compare ty against mypy and Pyright: cold CLI on home-assistant (2.19s vs 45.66s / 19.62s) and LSP re-check on pytorch, with machine stated as M4. The harness is public at astral-sh/ruff scripts/ty_benchmark (commit 7f7485d), with pinned project revisions (projects.py), locked tool versions (uv.lock, package-lock.json), and hyperfine cold/no-cache configuration.
- **Verifier notes:** The prose and chart disagree slightly on the LSP numbers (4.7ms/386ms/2.38s vs 4.5ms/370.5ms/2.60s), so both are now in claimed_speedup. The record's caveat said the page states tool versions ('latest of each'), which the page does not show, so the caveat was corrected. Metadata verified: MIT, 19740 stars, last commit 2026-09-24.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://astral.sh/blog/ty>
  - <https://github.com/astral-sh/ruff/blob/7f7485d608d2da19a0632a1238f2d4be551f612f/scripts/ty_benchmark/README.md>
  - <https://github.com/astral-sh/ruff/tree/7f7485d608d2da19a0632a1238f2d4be551f612f/scripts/ty_benchmark>
  - <https://github.com/astral-sh/ty>
- **Sources the enricher read:**
  - <https://github.com/astral-sh/ty>
  - https://github.com/astral-sh/ty (README)
  - https://github.com/astral-sh/ty (repo file tree)
  - <https://github.com/astral-sh/ty/blob/main/BENCHMARKS.md>
  - <https://github.com/astral-sh/ty/blob/main/pyproject.toml>
  - <https://github.com/astral-sh/ty/blob/main/docs/installation.md>
  - <https://github.com/astral-sh/ty/blob/main/.gitmodules>
  - <https://github.com/astral-sh/ty/blob/main/docs/coming-from-mypy-or-pyright.md>
  - <https://github.com/astral-sh/ty/blob/main/docs/features/language-server.md>
  - https://github.com/astral-sh/ty/issues (search: performance)
  - https://github.com/astral-sh/ty/issues (search: memory/slow/hang/timeout)
  - <https://github.com/astral-sh/ruff/blob/main/crates/ty/Cargo.toml>
  - <https://github.com/astral-sh/ruff/blob/main/Cargo.toml>
  - <https://astral.sh/blog/ty>
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/astral-sh/ty`) · [data/wave2/enrich/raw/github_com_astral_sh_ty.json](../../../data/wave2/enrich/raw/github_com_astral_sh_ty.json) (enrichment confidence 0.82)

</details>
