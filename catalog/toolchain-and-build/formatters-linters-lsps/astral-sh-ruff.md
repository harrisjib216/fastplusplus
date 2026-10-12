# Ruff

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Formatters, linters and language servers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust linter and formatter replacing Flake8, Black, isort, pyupgrade, and more with one fast CLI.

| | |
|---|---|
| **Beats** | Flake8 (linting); Black (formatting); also compared to pycodestyle, pyflakes, pylint |
| **Claimed result** | README headline: '10-100x faster than existing linters (like Flake8) and formatters (like Black)'. Founder's blog post (2022-08-30): '\~150x faster than Flake8 on macOS (\~25x faster if you hack Flake8 to enable multiprocessing)', '\~75x faster than pycodestyle', '\~50x faster than pyflakes and pylint', and a single-file re-lint of CPython in '\~60ms total'. The blog gives no numbers against Black or any formatter. |
| **Workload** | Linting the CPython codebase from scratch with no cache, plus incremental single-file re-lint. The formatting speed claim against Black appears only in the README headline, not on the benchmark page. |
| **Metric** | throughput |
| **Adoption** | 49.8k stars; used in Apache Airflow, Apache Superset, FastAPI, Hugging Face Transformers, Pandas, SciPy |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/astral-sh/ruff) · [benchmark](https://notes.crmarsh.com/python-tooling-could-be-much-much-faster) |

## Verdict

CONTRIBUTING.md's reproducible hyperfine benchmark (Ruff release build vs. the CPython 3.10 tree, pinned tool versions, Python 3.11) shows Ruff at 294ms cold vs Flake8 12.26s (41.66x), pyflakes 15.79s (53.64x), pycodestyle 46.92s (159.43x), and autoflake 6.18s (20.98x) — but states no CPU model. The larger headline figures (\~150x vs Flake8, \~60ms incremental re-lint) come from the founder's 2022 blog post on unspecified macOS hardware, not this repo benchmark; the Black formatting-speed claim appears only in the README, with no benchmark numbers given anywhere.

## Use it when

- Python 3 codebase already on Flake8 with few/no exotic plugins, run alongside a formatter
- Want one tool for both linting and Black-style formatting instead of two separate ones
- Large codebases or monorepos where whole-repo lint/format time matters in CI or pre-commit
- Need editor/LSP integration (VS Code and others via ruff_server) with fast on-save checks
- Want built-in autofix for import sorting, unused imports, and pyupgrade-style modernization in one pass

## Skip it when

- Team depends on specific Flake8 plugins Ruff hasn't re-implemented natively
- Need output byte-identical to Black on code that wasn't already Black-formatted (FAQ notes more deviation there)
- Need full Pylint parity; coverage is partial and some Pylint-style rule requests are still open
- Using `--extend-per-file-ignores` together with leading recursive glob patterns — open issue reports an extreme performance penalty (#8626)
- Autofixes for PERF401/PERF403 rules have open bug reports of making code slower in some cases (#21890, #21891) — review fixes before accepting

## How it is fast

Written in Rust and shipped as a single native binary, it avoids the per-file Python interpreter and plugin-subprocess overhead that Flake8's plugin architecture incurs; rules are natively re-implemented in Rust rather than shelled out to separate Python checkers. It also has built-in result caching so unchanged files are skipped on incremental runs. CONTRIBUTING.md's own benchmark shows most of the incremental win comes from that cache: a cold lint of CPython takes \~294ms, a cached rerun \~48ms.

## Compared with alternatives

No catalogued sibling targets Python lint/format specifically: Biome and Oxlint are the JS/TS equivalents (ESLint/Prettier), Pyrefly and ty are Python type-checkers (a different job than linting/formatting), and clangd-tidy is the C/C++ equivalent. Pick Ruff whenever the baseline being replaced is Flake8, Black, isort, or pylint on a Python codebase.

## Integration

| | |
|---|---|
| **Form** | CLI binary (installed via pip/pipx/uv/cargo); source is a Rust crate workspace (crates/\*) |
| **Dependencies** | none for the prebuilt binary (self-contained, no Python runtime required to run it) |
| **Minimum toolchain** | Rust 1.96 (edition 2024) to build from source; prebuilt wheels declare Python &gt;=3.7 as the package requirement |
| **Platforms** | PyPI classifier lists 'OS Independent'; wheels are published for common platforms but no explicit CPU-architecture list was found this session |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — linter is drop-in for Flake8 only with few/no plugins, used alongside a formatter, on Python 3 code; formatter is drop-in for Black with near-identical output on already-Black-formatted code, more deviation otherwise |

## Gotchas

- Formatting non-Black-formatted code produces more diffs than the near-100% match figure implies (FAQ)
- `--extend-per-file-ignores` combined with leading recursive glob patterns triggers an 'extreme performance penalty' (issue #8626, open)
- PERF401/PERF403 autofix suggestions have open bug reports of producing slower code in some cases (#21890, #21891)
- Ruff's linter and Black/ruff-format treat line-length enforcement differently, so E501 can still fire even with the formatter enabled

## Caveats and trade-offs

No CPU model is stated for any headline number: the blog says only 'macOS'. The blog post (pre-Astral, by the original creator) is a first-party account with no harness. CONTRIBUTING.md ('CPython Benchmark' section) does give a reproducible head-to-head. It uses hyperfine on the CPython 3.10 branch with ruff built via cargo --release, tool versions from scripts/benchmarks/pyproject.toml, and Python 3.11. Results: Ruff 294ms vs flake8 12.26s (41.66x), pyflakes 15.79s (53.64x), pycodestyle 46.92s (159.43x), autoflake 6.18s (20.98x). It still states no hardware, so the entry stays Tier C. crates/ruff_benchmark contains microbenchmarks of Ruff internals only.

Not 100% rule-for-rule identical to Flake8/Black in every edge case (docs claim near-total parity); newer/smaller plugin ecosystem than the tools it replaces.

## Maintenance

Actively maintained (last commit 2026-09-24, 49,764 stars, MIT license); copyable either as a pip-installed prebuilt binary or as a vendorable Rust crate workspace, so there's little build/toolchain risk for adopters.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification C, tier now C.
- **Tier reason:** The founder's 2022-08-30 blog post gives \~150x vs Flake8, \~75x vs pycodestyle, \~50x vs pyflakes/pylint, and \~60ms incremental re-lint on CPython, stating only 'macOS' with no CPU model or methodology. The repo's CONTRIBUTING.md has reproducible hyperfine head-to-head commands but also no CPU model, so Tier C.
- **Verifier notes:** The blog numbers are verified. The record wrongly said no head-to-head harness exists in the repo; CONTRIBUTING.md has one, but it lacks a CPU model, so the tier stays C. The Black claim is README-only. Metadata verified: MIT, 49764 stars, last commit 2026-09-24.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://notes.crmarsh.com/python-tooling-could-be-much-much-faster>
  - <https://github.com/astral-sh/ruff>
  - <https://github.com/astral-sh/ruff/blob/main/CONTRIBUTING.md>
- **Sources the enricher read:**
  - <https://github.com/astral-sh/ruff>
  - <https://github.com/astral-sh/ruff/blob/main/Cargo.toml>
  - <https://github.com/astral-sh/ruff/blob/main/docs/faq.md>
  - <https://github.com/astral-sh/ruff/blob/main/pyproject.toml>
  - <https://github.com/astral-sh/ruff/blob/main/CONTRIBUTING.md>
  - <https://github.com/astral-sh/ruff/issues/8626>
  - <https://github.com/astral-sh/ruff/issues/21890>
  - <https://github.com/astral-sh/ruff/issues/21891>
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/astral-sh/ruff`) · [data/wave2/enrich/raw/github_com_astral_sh_ruff.json](../../../data/wave2/enrich/raw/github_com_astral_sh_ruff.json) (enrichment confidence 0.6)

</details>
