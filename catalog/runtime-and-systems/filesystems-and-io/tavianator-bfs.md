# bfs

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `0BSD` · 🟢 active

> Breadth-first, find-compatible directory search tool with parallel async I/O; about 3x faster than GNU find on full traversals.

| | |
|---|---|
| **Beats** | GNU find 4.6.0 / fd |
| **Claimed result** | Per WebSearch snippets of the bfs 3.0 blog post (snippet only): in one test bfs took 8.5s vs GNU find 47.5s for the same 2930 files (about 5.6x, derived from snippet data); bfs-3.0.1 up to 248x faster than fd in some scenarios. The record's '3x faster than GNU find, 2.2x faster than previous bfs' could not be confirmed; older post figure (15-25% faster than GNU find 4.6.0) also unverified here. |
| **Workload** | Complete directory-tree traversal (expression -false) and early-quit/print searches; bfs 3.0 uses an asynchronous I/O queue served by up to 8 background threads (io_uring for getdents came later). Public harness bench/bench.sh runs bfs, find and fd on Linux, Rust and Chromium repo checkouts. |
| **Metric** | latency |
| **Adoption** | 1.3k stars |
| **Last commit** | 2026-08-24 |
| **Links** | [repository](https://github.com/tavianator/bfs) · [benchmark](https://tavianator.com/2023/bfs_3.0.html) |

## Verdict

Per WebSearch snippets of the author's bfs 3.0 blog post (page itself blocked): a full traversal of a \~7.6M-file home directory with -false took bfs 3.0.1 2.416 s vs GNU find 7.021 s (2.9x), bfs 2.6.3 5.307 s (2.2x) and fd 8.209 s; an early-quit search (-name kd-forest.mkv -quit) ran 427.6x faster than find and 248.7 +/- 159.3x faster than fd, a breadth-first-order effect with very high variance. CPU, compiler and flags were not visible in the snippets; the repo's bench/bench.sh (hyperfine -w2 -M20, Linux v6.5, Rust and Chromium 119 corpora) reproduces the setup but publishes no results.

## Use it when

- Shell scripts or tools that shell out to find and walk large trees (home directories, monorepos, kernel or Chromium checkouts)
- Searches for a file you expect to be near the top of a deep tree, with -print -quit
- Queries needing per-file metadata (-size, -newer, -links, colorized output), which benefit from parallel stat
- Linux boxes with liburing available, or macOS/BSD where the threaded path still applies
- When you need exact find semantics (the author reports no other find passes even the POSIX subset of its test suite)

## Skip it when

- You need a C or C++ library API for directory walking; bfs is only a binary (bftw.c is internal, not a supported library)
- You want gitignore-aware, regex-first search with friendly defaults; fd covers that interface (bfs needs -nohidden/-exclude)
- Output order must match GNU find's depth-first order exactly, e.g. diffing against existing find output
- Machines with very low open-file limits or many concurrent instances; 4.1.1 only recently started respecting system-wide limits
- Workloads dominated by -exec of a child process, where traversal speed is not the bottleneck

## How it is fast

Since 3.0 directories are opened and read asynchronously by background worker threads (default: number of CPUs, capped at 8, set with -jN) fed through a lock-free MPMC ring queue (src/ioq.c) that uses unconditional fetch-and-add instead of compare-and-swap. Since 3.1, on Linux with liburing, each worker also drives an io_uring for openat, close and statx, and stat() calls run in parallel on all platforms. Breadth-first order means -quit searches for shallow targets stop before descending into deep unrelated subtrees.

## Compared with alternatives

Pick bfs over al-dente (dent) when you need full find expression compatibility and a mature, packaged tool rather than a narrower listing utility; pick it over fd when the script already speaks find syntax or targets are shallow. For disk-usage totals, diskus, gdu or pdu are more direct.

## Integration

| | |
|---|---|
| **Form** | CLI binary (built with ./configure && make; packaged in most Linux distros, Homebrew, MacPorts, FreeBSD, OpenBSD) |
| **Dependencies** | none required beyond a C compiler, GNU make and Bash; optional libacl, libcap, libselinux, liburing, oniguruma |
| **Minimum toolchain** | C23 by default since 4.1; C17 fallback if the compiler supports common extensions; needs &lt;stdatomic.h&gt; and pthreads |
| **Platforms** | Linux, macOS, FreeBSD, OpenBSD, NetBSD, DragonFly BSD, Illumos, Android, WASIX; io_uring path Linux-only with feature probing |
| **Thread safety** | not applicable (standalone process; internally multi-threaded, -j1 disables background threads' parallelism) |
| **Drop-in for the baseline** | partial — accepts find's syntax and passes find's semantics tests, but output order is breadth-first, not depth-first, and -mount follows POSIX 2024 (excludes mount points) |

## Gotchas

- Default ./configure is a debug build; benchmark or package with ./configure --enable-release or results will be slower
- io_uring is used for openat/close/statx only; reading directory entries (getdents) still goes through readdir in worker threads (ioq.c carries a TODO for io_uring_prep_getdents)
- Several long-lived optimizer bugs were fixed recently: 4.0.8 fixed '-user a -or -user b' being rewritten to '-user a' (since 2.0), and 4.1.4 fixed -size units being ignored by the optimizer (since 1.3.3), which could return no results
- 3.1.2/3.1.3 fixed io_uring feature probing on older 5.x kernels; very old liburing builds were fixed in 4.0.5

## Known shortcomings

- io_uring covers openat, close and statx only; getdents still uses readdir in worker threads (a TODO in ioq.c). Optimizer bugs were fixed in 4.0.8 and 4.1.4. Numbers are blog snippets: about 7.6M files, bfs 3.0.1 at 2.416 s against GNU find 7.021 s (2.9x) and fd 8.209 s; early quit 427.6x against find and 248.7 +/- 159.3x against fd.

## Caveats and trade-offs

Numbers come only from the author's blog (tavianator.com, EGRESS_BLOCKED here), seen via WebSearch snippets; the repo's bench/ directory has a reproducible harness but no published results. bfs 3.0's async queue is thread-based, not io_uring as the record said. First-party. Hardware and flags not confirmed. 0BSD has no patent grant clause.

find-compatible CLI, not a library; Linux io_uring path needs a recent kernel, falls back to threads/readdir.

## Maintenance

Actively maintained (4.1.4 released June 29, 2026; CI and coverage), 0BSD-licensed and widely packaged, so it can be installed rather than vendored.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** Repo ships a public harness (bench/bench.sh, hyperfine via tailfin, Linux/Rust/Chromium corpora, --find and --fd comparisons) but publishes no results with CPU, compiler or flags; the numbers live only in the author's blog, which is egress-blocked here and was seen through WebSearch snippets. First-party, partial methodology: C.
- **Verifier notes:** Real, notable project (1.3k stars, 0BSD, not archived). Specific speedups in the record were not confirmed; claim rewritten from snippets. last_commit not checked (gh blocked).
- **Fields the verifier corrected:** `benchmark_url`, `workload`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** snippet only
- **Pages the verifier opened:**
  - <https://github.com/tavianator/bfs>
  - <https://raw.githubusercontent.com/tavianator/bfs/HEAD/README.md>
  - <https://raw.githubusercontent.com/tavianator/bfs/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/tavianator/bfs/HEAD/bench/bench.sh>
  - <https://raw.githubusercontent.com/tavianator/bfs/HEAD/bench/README.md>
- **Sources the enricher read:**
  - <https://github.com/tavianator/bfs>
  - <https://raw.githubusercontent.com/tavianator/bfs/HEAD/README.md>
  - <https://raw.githubusercontent.com/tavianator/bfs/HEAD/docs/BUILDING.md>
  - <https://raw.githubusercontent.com/tavianator/bfs/HEAD/docs/USAGE.md>
  - <https://raw.githubusercontent.com/tavianator/bfs/HEAD/docs/CHANGELOG.md>
  - <https://raw.githubusercontent.com/tavianator/bfs/HEAD/docs/bfs.1>
  - <https://raw.githubusercontent.com/tavianator/bfs/HEAD/bench/bench.sh>
  - <https://raw.githubusercontent.com/tavianator/bfs/HEAD/src/ioq.c>
  - <https://raw.githubusercontent.com/tavianator/bfs/HEAD/src/bftw.c>
  - <https://raw.githubusercontent.com/tavianator/bfs/HEAD/src/parse.c>
  - <https://github.com/sharkdp/fd/issues/1614>
  - WebSearch snippets of https://tavianator.com/2023/bfs_3.0.html (blocked)
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/tavianator/bfs`) · [data/wave11/enrich/raw/github_com_tavianator_bfs.json](../../../data/wave11/enrich/raw/github_com_tavianator_bfs.json) (enrichment confidence 0.75)

</details>
