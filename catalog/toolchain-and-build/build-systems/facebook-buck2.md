# Buck2

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Build systems](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Meta's Rust rewrite of the Buck build system; up to 2x faster than Buck1 in Meta's internal monorepo usage.

| | |
|---|---|
| **Beats** | Buck1 (Meta's original Buck build system) |
| **Claimed result** | "up to 2x faster than Buck1 in practice" (informal internal figure) |
| **Workload** | Meta's internal production usage comparing Buck2 to Buck1 across their monorepo build workloads; no specific project, task, or methodology given. |
| **Metric** | build-time |
| **Adoption** | 4.4k stars; used in production at Meta |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/facebook/buck2) · [benchmark](https://github.com/facebook/buck2/blob/main/README.md) |

## Verdict

The only first-party number is the README's 'up to 2x faster than Buck1 in practice,' sourced from Meta's internal production usage comparing Buck2 to Buck1 across Meta's monorepo. No specific workload, project, methodology, compiler/stdlib, or hardware is given, and the README itself says comparisons against Bazel-class systems 'have yet to be performed.'

## Use it when

- Large, multi-language monorepos already paying the cost of Make/Bazel-style top-down builds and needing better incremental-rebuild accuracy
- Teams that can invest in Remote Execution infrastructure to get real hermetic, cacheable builds
- Projects wanting a single build/test/query tool across languages with cross-language dependencies (e.g. Rust crate &lt;- OCaml &lt;- Python)
- Teams willing to write/port BUCK/Starlark rule definitions instead of reusing existing CMake/Make/Cargo build files
- Users comfortable tracking a fast-moving HEAD with no stable release tag

## Skip it when

- Small or single-language projects where Make/CMake/Cargo already work fine — migration cost isn't justified
- Teams wanting hermetic guarantees without standing up Remote Execution: local-only build steps are not sandboxed/hermetic (README footnote)
- Projects needing precompiled-header support: open issue #368 says PCH 'don't seem to be working'
- Workloads sensitive to daemon startup latency: open issue #507 notes 'daemon startup is a bit slow'
- Anyone needing a stable, versioned release: no stable release tag exists, Meta itself tracks HEAD

## How it is fast

Core build graph runs on `dice`, Meta's own incremental computation engine, so only invalidated nodes recompute on a change. Remote Execution support (Bazel's REAPI, works with BuildBarn/BuildBuddy/EngFlow/NativeLink) enables distributed/cached builds and, when used, hermeticity: all rule inputs must be declared or the build fails. A persistent background daemon (buckd) plus filesystem watching avoids repeated startup/scan cost on ultra-large repos. Build files and rules are parsed/evaluated with `starlark-rust`, Meta's own fast Starlark interpreter.

## Compared with alternatives

Pick Buck2 over Mill/tup/xmake when you need true multi-language monorepo builds with Remote-Execution-backed hermeticity and are willing to adopt Starlark BUCK files; its 2x number is Meta-internal Buck1-vs-Buck2 only (evidence tier C, no workload/hardware given), so it is not a verified head-to-head against Make/CMake/Ninja/Bazel/Cargo the way tup's or Mill's numbers are.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (self-contained Rust workspace; Remote Execution backend optional and external, e.g. BuildBarn/BuildBuddy/EngFlow/NativeLink) |
| **Minimum toolchain** | prebuilt binaries via GitHub releases or dotslash; building from source uses a pinned Rust nightly (rust-toolchain.toml: nightly-2026-07-05) |
| **Platforms** | Linux, macOS, Windows (CI has setup_linux_env/setup_macos_env/setup_windows_env and a Cross.toml) |
| **Thread safety** | not documented (daemon architecture is designed for concurrent builds; no explicit thread-safety contract found in README/source skim) |
| **Drop-in for the baseline** | partial — explain: replaces Buck1 with much better incremental-dependency accuracy per README, but requires BUCK/Starlark build files, not a drop-in for CMake/Make/Cargo project files |

## Gotchas

- Local-only build steps are NOT sandboxed/hermetic; only Remote-Execution-backed builds get full hermeticity (README footnote)
- Open issue #340: buck2 recompiles \*all\* source files when a link-only dependency changes
- No stable release tag; Meta itself runs latest HEAD, so 'rough edges' are expected for outside users (README warning)
- Precompiled headers reportedly not working (issue #368)

## Caveats and trade-offs

The README footnote says the figure 'comes from internal usage of Buck1 versus Buck2 at Meta' and that 'appropriate comparisons with systems like Bazel have yet to be performed; Buck1 is the baseline because it's simply what existed and what had to be replaced.' Buck1 is not one of this run's named baselines (CMake+Ninja, Make, Bazel, Cargo), and the 2x figure has no stated workload, hardware or methodology.

Requires Buck-style BUCK/Starlark build files, not compatible with existing CMake/Make/Cargo project files without new rules; full hermeticity guarantee needs Remote Execution infra.

## Maintenance

Actively maintained (commits as of 2026-09-24, 4.4k stars, used in production at Meta), but usability is 'copyable' rather than a stable package: no stable release tag, dual MIT/Apache-2.0 licensed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification C, tier now C.
- **Tier reason:** The README gives one first-party number: 'up to 2x faster than Buck1 in practice', from internal Meta usage. It gives no workload, hardware, method or benchmark code. That is a number without methodology, so tier C.
- **Verifier notes:** The claim matches the README. The license is dual MIT and Apache-2.0 (LICENSE-MIT and LICENSE-APACHE), even though gh shows only Apache-2.0. Stars (4,438) and last commit (2026-09-24) are confirmed. The only correction completes the truncated verbatim quote in caveats.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/facebook/buck2/blob/main/README.md>
  - <https://github.com/facebook/buck2>
- **Sources the enricher read:**
  - <https://github.com/facebook/buck2/blob/main/README.md>
  - <https://github.com/facebook/buck2>
  - repos/facebook/buck2/readme (gh api)
  - repos/facebook/buck2/git/trees/HEAD?recursive=1 (gh api)
  - repos/facebook/buck2/contents/Cargo.toml (gh api)
  - repos/facebook/buck2/contents/rust-toolchain.toml (gh api)
  - gh search issues --repo facebook/buck2 "performance"
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/facebook/buck2`) · [data/wave2/enrich/raw/github_com_facebook_buck2.json](../../../data/wave2/enrich/raw/github_com_facebook_buck2.json) (enrichment confidence 0.35)

</details>
