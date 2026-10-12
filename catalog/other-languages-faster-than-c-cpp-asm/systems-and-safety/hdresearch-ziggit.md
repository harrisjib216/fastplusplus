# ziggit (Zig git reimplementation)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Zig` · `GPL-2.0` · 🟢 active

> Pure-Zig git CLI and embeddable library; first-party numbers beat Apple git on tiny macOS commands, not large Linux repos.

| | |
|---|---|
| **Beats** | git (C) CLI: status, log -20, branch -a, blame |
| **Claimed result** | BENCHMARKS.md (2026-03-31, commit 9b2c398). On macOS arm64 the small repo (51 commits) is 4.9x faster on average (status 8.1 vs 1.0 ms, 8.1x; log -20 5.0x; branch -a 5.6x; blame 1.3x) and the large repo (2,367 commits) 4.4x on average (status 2.1x, show --stat 1.2x, log --oneline all 1.4x, blame 36.0 vs 2.8 ms, 12.6x). On Linux x86_64 the small repo averages 1.2x (log -20 0.8x). On the large Linux repo ziggit is slower on 8 of 10 commands (status 0.7x, diff --stat 0.3x, show --stat 0.3x) and wins only blame (87.9 vs 7.9 ms, 11.1x). Library calls versus spawning git: findCommit 85.4x macOS and 6.3x Linux, cloneBare 7.3x and 34.3x, full workflow 9.6x (all 5 repos) and 32.4x. End-to-end bun install with the ziggit integration: 0.93-1.39x cold, parity warm. The README's '4-10x' headline mixes small-repo rows with the large-repo blame row and omits the Linux CLI results. |
| **Workload** | hyperfine (100 runs, 5 warmups) of small git commands in a test repository on macOS arm64, plus in-process library calls versus spawning git as a subprocess for a bun-style workflow. |
| **Metric** | latency |
| **Hardware** | Apple M-series arm64, macOS 15.6 (exact chip not stated); Linux x86_64 'vers VM' with 8 GB RAM (CPU model not stated). |
| **Compiler and flags** | ziggit: Zig 0.15.2, ReleaseFast. git: Apple Git 2.50.1 (macOS) and git 2.43.0 (Linux), build flags not stated. macOS CLI: hyperfine --warmup 5 --runs 100 (small repo) or --runs 50 (large repo). Linux CLI: shell loop with date +%s%N, 50 iterations. Library: a custom lib_bench.zig (not in the repo), 20 iterations. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Adoption** | 255 stars (2,495 commits) |
| **Last commit** | 2026-05-06 |
| **Links** | [repository](https://github.com/hdresearch/ziggit) · [benchmark](https://raw.githubusercontent.com/hdresearch/ziggit/9b2c398/BENCHMARKS.md) |

## Verdict

First-party BENCHMARKS.md (2026-03-31, removed from master later): on an unnamed Apple M-series Mac, hyperfine timings of ziggit (Zig 0.15.2, ReleaseFast) against Apple Git 2.50.1 averaged 4.9x on a 51-commit repo and 4.4x on a 2,367-commit repo, while on a Linux x86_64 VM against git 2.43.0 it averaged 1.2x on a small repo and was slower on 8 of 10 large-repo commands, winning only blame (11.1x, without rename following). Library rows compare in-process calls with fork+exec of git (85.4x/6.3x findCommit, 7.3x/34.3x cloneBare on macOS/Linux), and end-to-end bun install moved only 0.93-1.39x cold across different bun versions.

## Use it when

- A Zig program or bun-like package manager that resolves refs and extracts trees from git dependencies many times per run, where spawning git per call (2-8 ms per spawn in BENCHMARKS.md) dominates
- Browser or WASI environments that need git object storage and clone in a 142 KB (55 KB gzipped) WASM module
- LLM coding-agent loops issuing many small read commands (status, log -20, branch -a) on small repositories on macOS, where succinct output also cuts tokens
- Experiments with a self-contained pure-Zig git server or with git internals in Zig

## Skip it when

- Large repositories on Linux: the project's own table shows it slower than git 2.43.0 on 8 of 10 commands (status 0.7x, diff --stat and show --stat 0.3x)
- Library dirty-tree checks: statusPorcelain() and isClean() report a freshly opened repository as clean without reading the worktree
- Anything that needs git's exact output or semantics: succinct output is on by default, blame does not follow renames, and parity is tracked through partial runs of git's test suite
- Repositories with concurrent or multi-process writers: HEAD and branch refs are rewritten in place with truncate, without git's lock-file-and-rename protocol
- Projects that cannot link GPL-2.0 code into their own binary (the library form makes the whole program a derived work)

## How it is fast

Most of the CLI gain is per-invocation startup: a small static Zig binary starts in about 1-1.5 ms where the measured Apple Git took 7-8 ms, and the library mode removes the process spawn entirely. On top of that it uses stat-based (mtime and size) clean checks, a packed-refs hash map for ref lookups, hardlinked local clones on Linux and per-invocation memoisation of commits and blobs in blame. Several library 'fast paths' are cached assumptions rather than faster algorithms (see gotchas).

## Compared with alternatives

No sibling reimplements git; compared with fd, minifind or the FUC tools, which win on parallel I/O over large trees, ziggit's real advantage is avoiding process startup in many tiny calls, so pick it only for embedding git reads in a Zig or bun-style tool or for a WASM git, not for raw CLI throughput on large repositories.

## Integration

| | |
|---|---|
| **Form** | static binary (CLI, release builds for macOS and Linux incl. musl) or Zig module via build.zig addModule("ziggit"); WASM freestanding and WASI builds |
| **Dependencies** | none beyond libc on native targets (no build.zig.zon dependencies); optional git-fallback build option (default off) shells out to git |
| **Minimum toolchain** | Zig 0.15.2 (minimum_zig_version in build.zig.zon) |
| **Platforms** | macOS arm64 and x86_64, Linux x86_64 and arm64 (glibc and musl), wasm32 (freestanding, WASI); hardlinked clones only on Linux |
| **Thread safety** | not documented; Repository carries mutable per-instance caches (_cached_head_hash, _cached_is_clean, _cached_index_mtime), so share one instance across threads only with external locking |
| **Drop-in for the baseline** | partial — same .git format and the common flags, but output differs unless --no-succinct or GIT_SUCCINCT=0 is set, blame skips rename following, and some commands are incomplete (closed issues report failed clones, pull and SSH URLs) |

## Gotchas

- Library status is a benchmark shortcut, not a check: isLightningFastClean() marks any freshly opened repository with an index as clean without touching the worktree (source comment: 'BENCHMARK OPTIMIZATION: For test repos, aggressively assume clean ... benchmarks typically use clean repos'), and later statusPorcelain()/isClean() calls return the cached clean result while the index mtime is unchanged, so edited tracked files and new untracked files go unreported; the repo's own untracked-file test sets `_cached_is_clean = false; // Override aggressive caching` to pass. revParseHead() caches HEAD for the Repository's lifetime and never re-reads it after outside changes (comment: 'Skip mtime checking for benchmark scenarios where HEAD doesn't change'). benchmarks/lib_benchmark.zig times exactly these two calls against git subprocesses, so its status row measures a no-op (MQF-style); the published library table uses findCommit, cloneBare and checkout instead.
- Local cloneBare on Linux hardlinks every file under the source .git, including the mutable HEAD, config, packed-refs, refs and index files, so the clone keeps the source's config verbatim; ziggit's updateHead() and updateHeadForCheckout() then rewrite HEAD and branch refs in place (createFile with truncate), so a commit or checkout through the library in such a clone also moves the source repository's refs. That shared-inode copy is what the Linux cloneBare rows (174-394 us, 34.3x) time; on macOS the same path falls back to a full copy (1.5-6.0 ms).
- BENCHMARKS.md attributes git's 7-8 ms macOS floor to fork()+exec(), but ziggit, launched as a process by the same hyperfine, finishes in 1.0-1.4 ms on that machine, so the floor is the startup of the git binary used (Apple Git 2.50.1, path unstated; /usr/bin/git on macOS is an xcode-select stub). The 4-8x small-command rows and the 85x macOS findCommit row mostly measure that startup; on Linux the small-repo CLI average is 1.2x and findCommit 6.3x.
- CLI status (cmd_status.zig) treats a tracked file as unchanged when its whole-second mtime and size match the index entry; no racy-timestamp check was found, so a same-size edit within the same second can be missed. Much of the code is agent-generated (file headers read 'Agents: this file is yours to edit'), 2,495 commits on master.

## Known shortcomings

- The README's 4-10x is cherry-picked from a removed BENCHMARKS.md (commit 9b2c398): on Linux 1.2x on a small repo and slower on 8 of 10 large-repo commands; the macOS gain is mostly git startup; blame lacks rename detection; library rows run in-process against fork+exec and the E2E rows compare different bun versions; benchmark scripts are not in the repo.
- Library benchmark shortcut: isLightningFastClean() marks a freshly opened repo clean without reading the worktree ('BENCHMARK OPTIMIZATION ... aggressively assume clean'), statusPorcelain()/isClean() miss edits and its own test forces _cached_is_clean=false, so the lib_benchmark.zig status row times a no-op (MQF-style); the published findCommit, cloneBare and workflow rows are unaffected by that, but on Linux cloneBare hardlinks all .git files (HEAD, refs, config) and updateHead rewrites refs in place with truncate, so a library commit or checkout in the clone moves the source's refs, which explains the 34.3x. The macOS 7-8 ms git floor is not fork+exec: the ziggit process itself runs in 1.0-1.4 ms under the same hyperfine.

## Caveats and trade-offs

First-party. The README headline cherry-picks: on Linux x86_64 the CLI averages 1.2x on a small repo, and on a large repo ziggit is slower on 8 of 10 commands (diff --stat and show --stat at 0.3x). The macOS gains are mostly git process launch, about 7-8 ms per invocation according to BENCHMARKS.md itself; the git binary path is not stated. Blame's 11-12.6x comes from in-process memoisation, and src/git/blame_cmd.zig has no rename detection, while git blame follows whole-file renames by default, so the work differs; output equivalence was not shown. The library rows time an in-process call against fork+exec of git; that is overhead, not implementation speed, and libgit2 would be the fair in-process baseline. The end-to-end bun install rows compare a ziggit-integrated bun 1.3.11-canary with stock bun 1.2.10 (different bun versions) and show only 0.93-1.39x. Succinct output is on by default in ziggit, so status/log print less than git. BENCHMARKS.md was removed from master (commit b82fa0c), and the benchmarks/\*.zig in the repo do not reproduce the published tables. [retier] Library benchmark shortcut: isLightningFastClean() marks a freshly opened repo clean without reading the worktree ('BENCHMARK OPTIMIZATION ... aggressively assume clean'), so the lib_benchmark.zig status row times a no-op and statusPorcelain()/isClean() miss edits. On Linux cloneBare hardlinks all .git files (HEAD, refs, config) and updateHead rewrites refs in place with truncate, so a library commit or checkout in the clone moves the source's refs, which explains the 34.3x. The macOS 7-8 ms git floor is not fork+exec: the ziggit process itself runs in 1.0-1.4 ms under the same hyperfine.

Drop-in git CLI plus Zig library, WASM build (142 KB), built-in git server and a succinct output mode for LLM use; GPL-2.0; feature parity with git tracked through git's own test suite results.

## Maintenance

Active (v0.3.0 bumped 2026-04-23, last commit 2026-05-06), GPL-2.0, 255 stars and 10 forks, all six filed issues closed; usable as a CLI experiment or WASM git, but the library's cached status and HEAD shortcuts and in-place ref writes over hardlinked clones make it risky as an embedded git for anything that mutates repositories.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now D.
- **Tier reason:** The README numbers come from BENCHMARKS.md, which commit b82fa0c removed from master. It was read at commit 9b2c398 and is first-party. It names Apple Git 2.50.1 and git 2.43.0 but no exact CPU ("Apple M-series", "vers VM") or git build flags. The hyperfine scripts and the lib_bench.zig it cites are not in the repo: benchmarks/cli_benchmark.zig times different commands with its own timer and hard-codes /root/ziggit. So it is C, and the README claim is overstated.
- **Retiered** C to D: Enricher: the library status row times a no-op (isLightningFastClean marks a fresh repo clean without reading the worktree, MQF precedent) and cloneBare hardlinks the source's HEAD, refs and config so the 34.3x 'clone' shares and mutates the source repository, while the macOS CLI gains are git's process start-up; no valid like-for-like row remains: C to D.
- **Verifier notes:** README CLI numbers match BENCHMARKS.md, which is now removed from master and was read at commit 9b2c398. The README hides the Linux results, where ziggit is mostly at parity or slower, so the claim is downgraded as overstated, though the tier stays C. Shortcomings to record: startup-dominated microcommands, a cherry-picked headline, blame doing less work (no rename following), library rows that compare in-process calls with subprocess calls, E2E rows across different bun versions, and benchmark scripts missing from the repo. Metadata checked: GPL-2.0, 255 stars, last commit 2026-05-06, active.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-69 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/hdresearch/ziggit/HEAD/README.md>
  - <https://raw.githubusercontent.com/hdresearch/ziggit/HEAD/BENCHMARKS.md>
  - <https://github.com/hdresearch/ziggit>
  - <https://github.com/hdresearch/ziggit/commits>
  - <https://github.com/hdresearch/ziggit/tree/master/benchmarks>
  - <https://raw.githubusercontent.com/hdresearch/ziggit/master/benchmarks/cli_benchmark.zig>
  - <https://raw.githubusercontent.com/hdresearch/ziggit/master/benchmarks/lib_benchmark.zig>
  - <https://raw.githubusercontent.com/hdresearch/ziggit/master/benchmarks/bun_scenario_bench.zig>
  - <https://github.com/hdresearch/ziggit/commits/master/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/hdresearch/ziggit/9b2c398/BENCHMARKS.md>
  - <https://github.com/hdresearch/ziggit/tree/master/src>
  - <https://raw.githubusercontent.com/hdresearch/ziggit/master/src/main_common.zig>
  - <https://raw.githubusercontent.com/hdresearch/ziggit/master/src/cmd_misc.zig>
  - <https://raw.githubusercontent.com/hdresearch/ziggit/master/src/git/blame_cmd.zig>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/hdresearch/ziggit/HEAD/README.md>
  - <https://raw.githubusercontent.com/hdresearch/ziggit/9b2c398/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/hdresearch/ziggit/HEAD/build.zig>
  - <https://raw.githubusercontent.com/hdresearch/ziggit/HEAD/build.zig.zon>
  - <https://github.com/hdresearch/ziggit>
  - <https://github.com/hdresearch/ziggit/commits/master>
  - <https://github.com/hdresearch/ziggit/issues?q=is%3Aissue>
  - <https://github.com/hdresearch/ziggit/tree/master/benchmarks>
  - <https://github.com/hdresearch/ziggit/tree/master/src>
  - <https://github.com/hdresearch/ziggit/tree/master/test>
  - <https://raw.githubusercontent.com/hdresearch/ziggit/master/benchmarks/lib_benchmark.zig>
  - <https://raw.githubusercontent.com/hdresearch/ziggit/master/benchmarks/bun_scenario_bench.zig>
  - <https://raw.githubusercontent.com/hdresearch/ziggit/master/benchmarks/cli_benchmark.zig>
  - <https://raw.githubusercontent.com/hdresearch/ziggit/master/src/ziggit.zig>
  - <https://raw.githubusercontent.com/hdresearch/ziggit/master/src/cmd_status.zig>
  - <https://raw.githubusercontent.com/hdresearch/ziggit/master/src/cmd_rev_parse.zig>
  - <https://raw.githubusercontent.com/hdresearch/ziggit/master/src/git/blame_cmd.zig>
  - <https://raw.githubusercontent.com/hdresearch/ziggit/master/test/dirty_detection_test.zig>
  - <https://raw.githubusercontent.com/hdresearch/ziggit/master/test/cache_and_status_correctness_test.zig>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/hdresearch/ziggit`) · [data/wave14/enrich/raw/github_com_hdresearch_ziggit.json](../../../data/wave14/enrich/raw/github_com_hdresearch_ziggit.json) (enrichment confidence 0.75)

</details>
