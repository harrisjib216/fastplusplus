# CPath

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [I/O and filesystem](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🔴 abandoned

> Single-header C directory traversal library; faster than `find`, TinyDir, Cute Files, and Python os.walk on recursive walks.

| | |
|---|---|
| **Beats** | find (GNU findutils), TinyDir, Cute Files, Python os.walk |
| **Claimed result** | Wall time 0.082-0.083s for CPath (recursion/emplace, C and C++) vs 0.147s for `find`, 0.237s for Python os.walk, 0.284s for Cute Files, 0.294s for TinyDir, 0.626s for `tree`. That is roughly 1.8x faster than `find` and \~3.4-3.6x faster than Cute Files/TinyDir (derived from page data). The project says CPath 'is often around 3x faster than other libraries and even faster than `find`'. |
| **Workload** | Recursive vs. explicit-stack directory traversal over a large synthetic directory tree (C API and C++ bindings), averaged over 100 runs, measuring user/system/wall time, compared against `find`, Python os.walk, Cute Files, and TinyDir. |
| **Metric** | latency |
| **Hardware** | MacBook Air7,2, Intel Core i5 @ 1.6GHz, 2 cores, 256KB L2 cache/core, 3MB L3, 8GB RAM |
| **Compiler and flags** | -O3 (project states -O1/-O2 give the same result; -O0 is \~5% slower); compiler name not stated |
| **Adoption** | 24 stars |
| **Last commit** | 2019-09-28 |
| **Links** | [repository](https://github.com/BraedonWooding/cpath) · [benchmark](https://github.com/BraedonWooding/cpath#benchmarks) |

## Verdict

Averaged over 100 runs of a recursive traversal over a large synthetic directory tree (MacBook Air7,2, dual-core Intel i5 @ 1.6GHz, -O3, compiler unnamed), CPath (C or C++, recursion or emplace) measured 0.082-0.083s wall time versus 0.147s for GNU find, 0.237s for Python os.walk, 0.284s for Cute Files, and 0.294s for TinyDir — about 1.8x faster than find and roughly 3.4-3.6x faster than Cute Files/TinyDir (derived from the reported wall times). It was not benchmarked against std::filesystem.

## Use it when

- Cross-platform (Windows + POSIX) recursive directory listing from C or pre-C++17 C++ without pulling in std::filesystem or Boost.Filesystem
- You only need file names/types during traversal and want to skip stat() calls unless you actually need size/time
- A small, vendorable single-header dependency (\~2.5k lines, MIT) is acceptable in the build
- Latency-sensitive walks over large trees where syscall count, not CPU work, dominates wall time
- You're willing to pin to and self-patch an abandoned header if bugs surface

## Skip it when

- You need std::filesystem/Boost.Filesystem feature parity (symlink handling, watching, permissions, atomic ops) — the author explicitly states CPath is not a std::filesystem replacement
- Windows-heavy usage: `cpathCanonicalise` has an open, unfixed length bug on Windows (issue #6), and CI never runs on Windows at all
- You need active maintenance: master's last commit is 2019-09-28, and 7 issues opened in 2023 (including a real init bug) remain untouched
- You need performance validated beyond one machine/toolchain: the only benchmark is first-party, single 2015 MacBook Air (dual-core i5 @ 1.6GHz), compiler unnamed, never independently reproduced
- You need paths longer than a fixed stack buffer: paths are stored in fixed-size `CPATH_MAX_PATH_LEN` buffers, not dynamically sized (open issue #7 acknowledges this)

## How it is fast

It does not eagerly call stat() on each entry; size/time info is loaded only on demand via `cpathGetFileInfo`, cutting per-entry syscalls versus TinyDir/Cute Files which stat every entry unconditionally. Its 'open file' (get file info from a path) needs a single syscall, versus TinyDir's approach of reopening and rescanning the parent directory (up to O(n) syscalls). The benchmark shows CPath and `find` have near-identical user time but CPath has much lower system time, consistent with the syscall-count reduction being the source of the win rather than faster CPU-bound logic.

## Compared with alternatives

The siblings (FastReader, reckless) beat std::ifstream/fstream and stdio for reading/writing file contents and logging, a different problem than directory enumeration — there's no real overlap. Pick CPath only when the bottleneck is recursive directory listing itself; use FastReader for fast file reads or reckless for high-throughput logging.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none beyond the C standard library (dirent.h/windows.h, sys/stat.h, stdlib.h, string.h, etc.) |
| **Minimum toolchain** | C89/C99-era C; C++ bindings target pre-C++17 compilers (no C++17 required); CI builds with gcc on Ubuntu 16.04/latest and macOS 10.14/latest |
| **Platforms** | POSIX (Linux, macOS) and Windows in source (windows.h/tchar.h path exists), but CI only exercises Linux and macOS — Windows has an open, unresolved bug (issue #6) and is untested by CI |
| **Thread safety** | not documented; no internal global mutable state was found in cpath.h, but the project makes no explicit thread-safety guarantee |
| **Drop-in for the baseline** | false — requires rewriting traversal against cpathGetNextFile()/cpath_dir (C) or cpath::Dir/File with Opt&lt;File, Error::Type&gt; (C++), not a drop-in for find, os.walk, TinyDir, Cute Files, or std::filesystem |

## Gotchas

- cpathGetNextFile does not stat() automatically — call cpathGetFileInfo (File::GetFileInfo in C++) explicitly or size/time fields stay unpopulated
- Open issue #1: the `file` output parameter isn't zero-initialized before a NULL check inside cpathGetNextFile — worth reading the source before relying on that check
- Paths live in fixed CPATH_MAX_PATH_LEN stack buffers rather than growing dynamically; very long paths can fail rather than resize (open issue #7)
- Windows cpathCanonicalise has a known, unfixed length-calculation bug (issue #6)

## Caveats and trade-offs

The published benchmark compares against `find`, TinyDir, Cute Files, Python os.walk and `tree`, not against std::filesystem, and the README says it is NOT a std::filesystem replacement. So this is evidence against a related but different incumbent (baseline_in_list=false). The benchmark is first-party, on one machine, and names no compiler. The benchmark sources are in tests/ (tests.c, cbench.h, benchmark_recursive.py). The last commit on the default branch (master) is 2019-09-28. The 2023-09-24 date is an unmerged side-branch commit (BraedonWooding-remove-unnecessary-check).

C89/C99-era API by design for broad pre-C++17 compiler support; larger codebase (\~2.5k lines) than minimal alternatives like TinyDir/Cute Files; does not eagerly load stat() info (opt-in), trading a feature for speed; author explicitly states CPath is 'NOT a replacement for a more heavy duty library like std::filesystem.'

## Maintenance

Abandoned: master's last commit is 2019-09-28 (the raw repo pushed_at of 2023-09-24 reflects an unmerged side branch, not master); MIT-licensed and small enough (\~2.5k-line single header) to vendor and patch yourself if needed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** README Benchmarks table shows the exact wall times (CPath 0.082-0.083s vs find 0.147s, os.walk 0.237s, Cute Files 0.284s, TinyDir 0.294s) with CPU (MacBookAir7,2, Intel Core i5 1.6GHz) and -O3 stated. Benchmark sources are in tests/ (tests.c, cbench.h, benchmark_recursive.py), but no compiler is named, so it is first-party with partial methodology: C.
- **Verifier notes:** The numbers and hardware check out. The record's last_commit came from the repo's pushed_at, which reflects an unmerged side branch; master was last touched in 2019-09, so it is now abandoned. The ratios were not marked as derived, so claimed_speedup was reworded to add that marker.
- **Fields the verifier corrected:** `claimed_speedup`, `last_commit`, `maintenance_status`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/BraedonWooding/cpath>
  - <https://github.com/BraedonWooding/cpath#benchmarks>
  - <https://github.com/BraedonWooding/cpath/blob/master/tests/benchmark_recursive.py>
- **Sources the enricher read:**
  - <https://github.com/BraedonWooding/cpath>
  - <https://github.com/BraedonWooding/cpath#benchmarks>
  - <https://github.com/BraedonWooding/cpath/blob/master/cpath.h>
  - <https://github.com/BraedonWooding/cpath/blob/master/.github/workflows/main.yml>
  - <https://github.com/BraedonWooding/cpath/blob/master/tests/benchmark_recursive.py>
  - <https://github.com/BraedonWooding/cpath/blob/master/example.c>
  - <https://github.com/BraedonWooding/cpath/blob/master/example.cpp>
  - <https://github.com/BraedonWooding/cpath/issues>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/braedonwooding/cpath`) · [data/wave1/enrich/raw/github_com_braedonwooding_cpath.json](../../../data/wave1/enrich/raw/github_com_braedonwooding_cpath.json) (enrichment confidence 0.32)

</details>
