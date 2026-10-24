# tup

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Build systems](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `GPL-2.0` · 🟢 active

> File-based build tool that beats Make's incremental-rebuild scanning via a persistent Linux-only file monitor and per-command sandboxing.

| | |
|---|---|
| **Beats** | Make |
| **Claimed result** | At 100k files: no-op check \~0s (tup) vs \~30 minutes (make); single C-file change rebuild \~0.1s (tup) vs \~30 minutes (make). Cold/initial build: tup is 5-30% SLOWER than make across sizes. |
| **Workload** | Synthetic C project generator (logarithmic directory tree, up to 100,000 C files / \~200,000 total files with headers): cold build, single-file-change rebuild, and no-op ('nothing changed') dependency check, tup vs make. |
| **Metric** | build-time |
| **Adoption** | 1.3k stars |
| **Last commit** | 2026-07-30 |
| **Links** | [repository](https://github.com/gittup/tup) · [benchmark](http://gittup.org/tup/make_vs_tup.html) |

## Verdict

On tup's own synthetic C-project generator (log-scale graphs, N up to 100k files / \~200k with headers, make run as `make -rR`, no CPU/OS/compiler flags stated), tup reports \~0s no-op checks and \~0.1s single-file rebuilds versus make's figures of roughly 20-30 minutes at 100k files; tup's cold/initial build is itself 5-30% slower than make, and tup's own file monitor took up to 2min:30s to cold-start at 200k files.

## Use it when

- Large Linux C/C++ trees (tens of thousands of files) where make's per-invocation directory scan/stat dominates the edit-compile-test loop.
- Teams willing to run a persistent `tup monitor` daemon in the background and keep it warm.
- Projects that want undeclared-dependency errors caught automatically via file-access tracing instead of hand-maintained header dependency lists.
- GPL-2.0-compatible projects that can vendor the tool as-is (it already bundles Lua, PCRE2 and SQLite3, no external runtime deps).

## Skip it when

- Clean/cold builds: tup measured 5-30% slower than make across sizes on the vendor's own benchmark.
- macOS/Windows, or Linux without FUSE: the fast-path monitor is inotify/Linux-specific, the OSX shim has an open unresolved issue since 2014, and FUSE-based sandboxing broke on libfuse3 3.17.1 as recently as 2025 (issue #518).
- Teams needing Makefile compatibility, mainstream IDE integration, or a large plugin ecosystem -- 1.3k stars versus make's ubiquity.
- Build outputs generated dynamically/implicitly -- tup requires every output declared up front; undeclared writes are errors, which is a real migration cost.
- One-off or CI-only cold builds where the monitor never warms up -- most of the claimed win depends on a hot monitor and hot OS cache.

## How it is fast

Speed comes from a persistent background 'monitor' process (inotify on Linux) that watches the filesystem so tup never has to stat/walk the whole tree like make does on every invocation; state lives in an embedded SQLite database rather than being recomputed each run. Per-command FUSE sandboxing produces an exact dependency graph (not user-declared globs), so a change dirties only the affected graph nodes -- turning no-op and single-file rebuild checks into near O(changed files) instead of O(all files).

## Compared with alternatives

Pick tup over xmake/Mill/Buck2/ccache when the specific pain is make's linear directory-scan overhead on a huge Linux C/C++ tree during interactive edit-rebuild, and you can run a persistent monitor daemon and rewrite the build in Tup's DAG syntax; xmake is the closer choice for a faster Make-compatible generator without changing build files, and ccache if the bottleneck is recompilation itself rather than dependency scanning.

## Integration

| | |
|---|---|
| **Form** | source-drop (build tup itself from source via bootstrap.sh; not header-only) |
| **Dependencies** | none required to vendor -- bundles Lua, PCRE2, SQLite3 in-tree; needs libfuse on Linux for command sandboxing |
| **Minimum toolchain** | not documented precisely -- plain C, built via its own bootstrap.sh/tup; Windows build via build-win32.sh (MinGW) |
| **Platforms** | Linux (full speed: inotify monitor + FUSE sandbox), macOS (dllinject/ldpreload shim, no monitor -- open issue since 2014), Windows (dllinject-based tracing) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | false -- different Tupfile syntax (Lua-based), explicit output declarations required, no implicit globbing |

## Gotchas

- Near-zero no-op/rebuild times require `tup monitor` already running; without it tup falls back to scanning, and a third-party benchmark (issue #268) found it slower than make/ninja.
- libfuse3 ABI changes have broken tup's build-command file sandboxing before (3.17.1, reported 2025).
- Monitor cold-start took 2min:30s at 200k files in the vendor's own benchmark (2.5s once cache is hot).
- All build outputs must be declared explicitly; undeclared writes are treated as errors, not warnings.

## Caveats and trade-offs

First-party page with no CPU model, OS or compiler flags stated, and the generator script is not published. The ratio (about 30 min vs 0.1 s) looks implausible, so it is capped at tier C under the &gt;50x rule. The page footer shows a 2008-2024 copyright, so the hardware is likely old. At 100k files the log-scale graphs appear to put make at a little over 1,000 s (about 20 min), which is below the text's 'half an hour'. The near-zero no-op and update times rely on tup's file monitor, which took 9.7 s to start the first time at 200k files and 2 min 30 s with a cold cache (2.5 s hot). The 100k-file case is a stress test, and tup's cold build is 5-30% slower than make.

Requires all build outputs declared explicitly (no implicit globbing) for correctness; runs a persistent filesystem-watching 'monitor' process; much smaller ecosystem/IDE support than Make/CMake.

## Maintenance

Actively maintained (last commit 2026-07-30, closed a race-condition crash as recently as July 2026) but niche -- 1,262 stars, 168 open issues; GPL-2.0 and copyable/vendorable, though its FUSE-based build sandboxing has broken on newer libfuse3 as recently as 2025.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification C, tier now C.
- **Tier reason:** A first-party page describes the synthetic generator setup ('make -rR', N = 1 to 100k) and shows log-log graphs. It states no CPU, OS or compiler flags, and the generator script is not published. The gain is also implausible-looking (about 30 min vs 0.1 s), so tier C.
- **Verifier notes:** The text states make takes 'a half an hour' vs tup 'a tenth of a second' for a single C-file change at 100k files, tup takes '0 seconds' for nothing-changed, and tup is 5-30% slower on the initial build. The make no-op value comes from the graph and the general '30 minutes per update for make' remark. GPL-2.0 (COPYING), 1,262 stars and last commit 2026-07-30 are confirmed.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <http://gittup.org/tup/make_vs_tup.html>
  - <http://gittup.org/tup/make_vs_tup-nothing.png>
  - <http://gittup.org/tup/make_vs_tup-c_file.png>
  - <https://github.com/gittup/tup>
  - <https://github.com/gittup/tup/blob/master/COPYING>
- **Sources the enricher read:**
  - <https://github.com/gittup/tup>
  - <https://github.com/gittup/tup/blob/master/README.md>
  - <https://github.com/gittup/tup/blob/master/CONTRIBUTING.md>
  - <https://github.com/gittup/tup/issues/268>
  - <https://github.com/gittup/tup/issues/518>
  - <http://gittup.org/tup/make_vs_tup.html>
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/gittup/tup`) · [data/wave2/enrich/raw/github_com_gittup_tup.json](../../../data/wave2/enrich/raw/github_com_gittup_tup.json) (enrichment confidence 0.4)

</details>
