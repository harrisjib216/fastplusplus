# clangd-tidy

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Formatters, linters and language servers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python` · `MIT` · 🟢 active

> CLI wrapper around clangd that reports clang-tidy diagnostics much faster than standalone clang-tidy.

| | |
|---|---|
| **Beats** | clang-tidy |
| **Claimed result** | "clangd-tidy is significantly faster than clang-tidy (over 10x in my experience)" |
| **Workload** | Running the same clang-tidy checks over a C/C++ codebase (for example in CI). clangd-tidy wraps clangd, which only builds an AST from included headers, instead of standalone clang-tidy, which checks code from all headers even though it suppresses warnings from them by default. |
| **Metric** | throughput |
| **Adoption** | 161 stars |
| **Last commit** | 2026-02-09 |
| **Links** | [repository](https://github.com/lljbash/clangd-tidy) · [benchmark](https://github.com/lljbash/clangd-tidy#comparison-with-clang-tidy) |

## Verdict

The README's 'Comparison with clang-tidy' section states clangd-tidy is 'significantly faster than clang-tidy (over 10x in my experience)' when running the same checks over a codebase, because clangd only builds an AST from included headers where clang-tidy checks all headers. No benchmark script, target codebase, compiler flags, or hardware are given — it's the author's stated personal experience, not a reproducible measurement.

## Use it when

- Running clang-tidy-style checks in CI on a C/C++ codebase where wall-clock time matters
- You already have clangd installed/configured and a working compile_commands.json
- You want per-file grouped diagnostics instead of clang-tidy's duplicated per-header warnings
- You want incremental linting of only changed lines via clangd-tidy-diff (e.g. gradual rollout of checks on a legacy codebase)
- You also want code-formatting checks (clang-format) folded into the same CI step (-f/--format)

## Skip it when

- You need --fix / automatic fixups; clangd-tidy has no fix-application support, only editor code actions
- You rely on clang-tidy checks that clangd's TidyProvider doesn't support; those are silently dropped, not reported as skipped
- Exact diagnostic parity with clang-tidy matters (there are open, acknowledged behavioral discrepancies, e.g. issues #7, #15, #16)
- You can't install/configure clangd in your CI image, or don't have a compile_commands.json
- You want a large, heavily-used, battle-tested tool; this is a small single-maintainer project (161 stars)

## How it is fast

Standalone clang-tidy parses and checks the full AST of every included header for every translation unit, even though it suppresses warnings from headers by default. clangd instead builds and caches an AST scoped to what a file actually needs, the same incremental analysis it uses for live editor diagnostics, so clangd-tidy inherits that lighter-weight AST construction instead of clang-tidy's from-scratch per-file header checking. No other technique (caching, parallel dispatch beyond clangd's own worker pool, etc.) is described in the README or source.

## Compared with alternatives

Not directly comparable to the other sibling entries (Biome, Oxlint, Pyrefly, ty, Ruff), which target JS/TS or Python; clangd-tidy is the only C/C++ formatter-linter-LSP entry in this category so far, so 'no siblings catalogued yet' for its actual competitor set (clang-tidy variants).

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | clangd (external binary); Python 3.8+; attrs, cattrs, typing-extensions (auto-installed via pip); tqdm optional for progress bar |
| **Minimum toolchain** | Python 3.8+; a clangd binary (version affects available .clangd diagnostics config, e.g. UnusedIncludes needs clangd-14+, MissingIncludes needs clangd-17+) |
| **Platforms** | POSIX (per PyPI classifiers: Operating System :: POSIX); no Windows classifier listed |
| **Thread safety** | not documented (single Python CLI process driving one clangd subprocess over LSP; -j controls clangd's internal async worker/background-index thread count, not multiple clangd-tidy processes) |
| **Drop-in for the baseline** | partial — explain: same CLI shape (pass filenames, -p for compile_commands.json dir) but no --fix, and it silently disables clang-tidy checks clangd doesn't support, so output isn't a strict superset/match of clang-tidy's |

## Gotchas

- Silently disables clang-tidy checks unsupported by clangd's TidyProvider (listed in LLVM's TidyProvider.cpp) rather than erroring or warning
- No --fix option; the README suggests using editor code actions instead since the tool targets CI, not local fix workflows
- Known behavioral discrepancies vs clang-tidy are tracked as open issues (#7, #15, #16), not resolved
- Default -j (clangd async workers) is 1, so out-of-the-box throughput depends on tuning -j for parallelism

## Caveats and trade-offs

'Over 10x' is the author's personal experience, with no benchmark script, codebase, compiler flags, or hardware given, so it is capped at Tier C despite the plausible-sounding number. The StackOverflow discussion linked in the README is anecdotal, not a reproducible benchmark. The comparison is not exactly like-for-like: clangd-tidy silently disables several clang-tidy checks that clangd does not support, and it lacks --fix.

No --fix support; silently disables checks clangd doesn't support; some diagnostic behavior differs from clang-tidy (tracked as known discrepancies in the project's issue tracker); requires clangd installed and configured, and a working compile_commands.json.

## Maintenance

Actively maintained (last commit 2026-02-09) and MIT-licensed, but a small, single-maintainer project (161 stars) — usability tagged 'copyable' rather than a heavyweight dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification C, tier now C.
- **Tier reason:** The README's 'Comparison with clang-tidy' section says 'significantly faster than clang-tidy (over 10x in my experience)'. This is a first-party number with no benchmark code, codebase, or hardware given, so it is Tier C.
- **Verifier notes:** The quote is verified. The record's claim that clangd 'reuses its background index' is not on the page, so it was removed from workload. Metadata verified: MIT, 161 stars, last commit 2026-02-09 (active). The project is small, but it stays because it is Tier C, not D.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/lljbash/clangd-tidy#comparison-with-clang-tidy>
  - <https://github.com/lljbash/clangd-tidy>
- **Sources the enricher read:**
  - <https://github.com/lljbash/clangd-tidy#comparison-with-clang-tidy>
  - <https://github.com/lljbash/clangd-tidy>
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/lljbash/clangd-tidy`) · [data/wave2/enrich/raw/github_com_lljbash_clangd_tidy.json](../../../data/wave2/enrich/raw/github_com_lljbash_clangd_tidy.json) (enrichment confidence 0.5)

</details>
