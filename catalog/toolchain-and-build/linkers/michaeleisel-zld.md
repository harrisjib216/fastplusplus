# zld

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Linkers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Drop-in fork of Apple's ld64 that speeds up incremental Xcode debug linking; archived, maintainer now recommends lld instead.

| | |
|---|---|
| **Beats** | Apple ld (ld64) |
| **Claimed result** | Maintainer claims 'at least 40% faster' generally; measured numbers on a 'high-end Mac desktop': Signal 390ms-&gt;250ms (\~1.6x), Mozilla XUL 5.2s-&gt;2.20s (\~2.4x), Mozilla storage.framework 495ms-&gt;340ms (\~1.5x) (all derived from page data); similar percentage speedups reported on a 2014 MacBook Pro (Signal 790ms-&gt;540ms, XUL 10.3s-&gt;5.4s, storage.framework 940ms-&gt;625ms). |
| **Workload** | Incremental debug-build linking of three real Apple-platform binaries: the Signal iOS app's main binary, Mozilla's XUL framework (macOS Firefox), and Mozilla's Storage.framework (iOS Firefox), comparing stock Apple ld vs. zld link time, captured with the exact ld invocation command lines used. |
| **Metric** | build-time |
| **Hardware** | Described only as 'a high-end mac desktop' and 'a 2014 macbook pro' - no specific CPU model given. |
| **Compiler and flags** | Captured ld invocations show Xcode toolchain clang runtime libs (e.g. clang/11.0.0, clang/9.0.1) embedded in the linker command lines; no explicit statement of exact Xcode/clang version or optimization flags used for the benchmark run itself. |
| **Adoption** | 1.19k stars |
| **Last commit** | 2023-02-15 |
| **Links** | [repository](https://github.com/michaeleisel/zld) · [benchmark](https://github.com/michaeleisel/zld/blob/master/misc/benchmarks.md) |

## Verdict

First-party misc/benchmarks.md (with the full captured ld command lines) shows zld beating stock Apple ld64 on three real Xcode/Mach-O debug links on a 'high-end Mac desktop': Signal's iOS app binary 390ms-&gt;250ms (\~1.6x), Firefox macOS's XUL framework 5.2s-&gt;2.20s (\~2.4x), and Firefox iOS's Storage.framework 495ms-&gt;340ms (\~1.5x), with similar percentage gains reported on a 2014 MacBook Pro. No specific CPU model, run count, or variance is given, and the exact Xcode/clang version used for the benchmark itself isn't stated (the captured ld invocations reference clang 11.0.0 and 9.0.1 runtime libs).

## Use it when

- Xcode, Bazel, or Cargo debug builds on macOS/iOS where a single ld64 link already takes &gt;=500ms and faster edit-build-run loops matter
- Projects that must stay on Apple's own ld64 codebase for behavioral/stability reasons rather than switching linker families entirely
- Debug-only linking (not release, not App Store archive builds) where a small correctness/regression risk is acceptable
- Teams that can pin to a matching Xcode/ld64 vintage (repo's last activity is 2023, roughly Xcode 13-14 era) and won't chase newer toolchains
- x86_64 or arm64 Xcode debug targets where the arm64_32/Mac Catalyst fallback gap (see gotchas) doesn't apply

## Skip it when

- Any release, App Store, or otherwise correctness-critical build -- the README states it is untested/unintended for that
- Newer Xcode/ld64 versions past 2023: repo is archived (last commit 2023-02-15), so toolchain drift bugs like the Xcode 14 undefined `_objc_msgSend$...` selector-stub issue (#113, #125) won't be fixed
- Apple Silicon (M1) hosts, where users reported SIGKILL crashes and codesigning issues with certain Rust/Cargo link setups (#110, referencing #85)
- arm64_32 or Mac Catalyst link targets: zld knows it has issues there and silently falls back to the real ld unless you also pass `-zld_original_ld_path`
- New projects generally: the maintainer's own 2022 RFC (#112) says lld is faster and more reproducible and is what they'd pick today; the README's top line now tells readers to use lld instead

## How it is fast

Replaces ld64's STL hash maps/sets with Abseil's Swiss Tables (open-addressing, SIMD-probed hash containers) for the linker's internal symbol/string tables. Parallelizes stages that ld64 runs serially, including library parsing, output-file writing, and sorting. Also caches and speeds up string hashing (hash caching plus a faster hash function) and persists some object/library-name metadata under /tmp/zld-... between runs to warm later links.

## Compared with alternatives

mold and Wild are ELF/Linux linkers competing with lld; neither links Mach-O/Xcode debug builds, so they aren't substitutes for zld's use case. Pick zld over them only when the job is specifically Xcode/Bazel/Cargo debug-linking on macOS/iOS -- and even then, the maintainer's own RFC and the archived README both point to lld as the better current choice for that same job.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | cmake (build-time); vendors Abseil (for Swiss Tables) and Apple's ld64/corecrypto sources in-tree; requires the full Xcode.app (not just Command Line Tools) to build and run |
| **Minimum toolchain** | macOS with a full Xcode install; built via `make`/cmake; benchmark and issue history point to an Xcode 13-14 / clang 11.0.0 / ld64 vintage, unmaintained since 2023-02-15 |
| **Platforms** | macOS hosts only (Intel and Apple Silicon), producing Mach-O output for macOS/iOS/watchOS/tvOS targets; not applicable to Linux/Windows/GNU/MSVC toolchains |
| **Thread safety** | not documented (it's a single-shot CLI linker invocation, not an embeddable library API) |
| **Drop-in for the baseline** | partial -- explain: drop-in via -fuse-ld=&lt;path&gt; for debug configurations, but it silently falls back to the real ld64 for known-broken cases (arm64_32, Mac Catalyst) unless -zld_original_ld_path is also set, and it's explicitly not validated for release builds |

## Gotchas

- Without also passing -Wl,-zld_original_ld_path,&lt;real ld&gt;, zld silently falls back to Apple's stock linker for cases it knows are broken (arm64_32, Mac Catalyst) with no warning
- Needs the full Xcode.app installed, not just Xcode Command Line Tools, or builds/runs fail (#106, #109)
- Caches metadata under /tmp/zld-...; README says to run a link twice before judging speedup because the first run pays cold-cache cost
- Reported SIGKILL/codesigning crashes on Apple Silicon with some Rust+Cargo configurations (#110, #85), and an Xcode 14 undefined-symbol bug with ObjC selector stubs (#113, #125)

## Caveats and trade-offs

Repo is archived; the README's own top line now says 'zld is now archived, consider using lld instead.' Benchmark hardware is described only in vague terms ('high-end mac desktop', '2014 macbook pro'), not a specific CPU model, and only single-shot-looking numbers for 3 sample projects with no stated run count/variance, so capped at tier C rather than B/A. Baseline is Apple's ld64, not one of the four listed baselines (GNU ld, gold, lld, MSVC link.exe), so baseline_in_list=false. zld is a fork of Apple's open-source ld64 sources (not tracked by GitHub as a fork relationship since Apple's ld64 isn't hosted as a forkable GitHub repo).

Archived/unmaintained; intended only for debug builds, not verified for release correctness; mixes Apple's linker source with a newer Xcode toolchain, which the author calls 'not ideal'; macOS/Xcode-only, no Linux/Windows relevance.

## Maintenance

Archived since 2023-02-15 (MIT license, 1,191 stars); the README's own top line now says to use lld instead, echoing the maintainer's 2022 'Future of zld' RFC (#112) that lld is faster, more reproducible, and what they'd choose for a new project today.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party misc/benchmarks.md gives stock ld vs zld times for Signal, XUL and Storage.framework, with the full ld command lines. The hardware is vague ('high-end mac desktop', '2014 macbook pro'), and there is no run count, variance or benchmark harness, so these are first-party numbers short of A.
- **Verifier notes:** All numbers match benchmarks.md exactly: 390-&gt;250ms, 5.2s-&gt;2.20s, 495-&gt;340ms; 2014 MBP 790-&gt;540, 10.3s-&gt;5.4s, 940-&gt;625. The '40% faster' is the README's 'file an issue if ... not at least 40% faster'. Repo is archived (MIT, 1,191 stars, last commit 2023-02-15), so the abandoned status is correct. The only change is is_fork_of, because the README calls zld a fork of Apple's ld.
- **Fields the verifier corrected:** `is_fork_of`
- **Pages the verifier opened:**
  - <https://github.com/michaeleisel/zld/blob/master/misc/benchmarks.md>
  - <https://github.com/michaeleisel/zld>
- **Sources the enricher read:**
  - <https://github.com/michaeleisel/zld>
  - <https://github.com/michaeleisel/zld/blob/master/README.md>
  - <https://github.com/michaeleisel/zld/blob/master/misc/benchmarks.md>
  - <https://github.com/michaeleisel/zld/issues/112>
  - <https://github.com/michaeleisel/zld/issues/124>
  - <https://github.com/michaeleisel/zld/issues/125>
  - <https://github.com/michaeleisel/zld/issues/110>
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/michaeleisel/zld`) · [data/wave2/enrich/raw/github_com_michaeleisel_zld.json](../../../data/wave2/enrich/raw/github_com_michaeleisel_zld.json) (enrichment confidence 0.75)

</details>
