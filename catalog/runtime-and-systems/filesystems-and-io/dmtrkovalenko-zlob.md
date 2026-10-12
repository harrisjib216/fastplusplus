# zlob

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Zig (C API)` · `MIT` · 🟢 active

> Zig glob(3)-compatible globbing and parallel file walker with C/Rust APIs; about 2-3x faster than Rust glob crate and walkdir.

| | |
|---|---|
| **Beats** | Rust glob crate, globset+walkdir, walkdir and ignore crates; README also claims glibc glob() is 1.2-1.7x slower |
| **Claimed result** | Linux kernel checkout, median wall time: \*\*/\*.c (36,685 matches) 24.2 ms vs glob crate 49.2 ms (2.0x) and globset+walkdir 43.8 ms (1.8x); drivers/\*\*/\*.c 8.23 ms vs 16.4 ms (2.0x); fs/\*.c 9.84 us vs 31.9 us (3.2x); \*/Makefile 11.4 us vs 39.1 us (3.4x). Walk (185,737 entries, warm cache, best of 5): plain walk 27.4 ms vs walkdir 90.9 ms; gitignore walk 2.4 ms vs ignore 8.0 ms; parallel 0.64 ms vs 4.9 ms; walk+metadata 24.3 ms vs 226 ms. README also claims 1.2-1.7x (up to 10x) over glibc glob(), with no table. |
| **Workload** | Glob patterns and recursive directory walks over a Linux kernel checkout (93,638 files, 6,157 dirs). |
| **Metric** | latency |
| **Hardware** | Intel Core i7-14700K, 14 cores (28 vCPU), Linux x86_64 |
| **Compiler and flags** | Zig 0.16.0 ReleaseFast static build; cargo bench via criterion |
| **Adoption** | 230 stars |
| **Last commit** | 2026-08-30 |
| **Links** | [repository](https://github.com/dmtrKovalenko/zlob) · [benchmark](https://github.com/dmtrKovalenko/zlob) |

## Verdict

With the project's criterion harness over a Linux kernel checkout (93,638 files) on an Intel Core i7-14700K, zlob 1.x built ReleaseFast with zig 0.16.0 resolved \*\*/\*.c in 24.2 ms vs 49.2 ms for the Rust glob crate (2.0x) and shallow patterns like fs/\*.c in 9.84 us vs 31.9 us (3.2x); walker rows (27.4 ms vs walkdir 90.9 ms, 2.4 ms vs ignore 8.0 ms) come from a synthetic-tree harness whose sizes do not match the README's stated 185,737 entries. No glibc glob() or C++ std::filesystem comparison is published.

## Use it when

- Recursive extension globs (\*\*/\*.c, src/\*\*/\*.{rs,toml}) over large source trees, such as editor/file-finder indexing (it was built for the fff finder).
- Replacing walkdir or ignore in Rust tools that walk big trees with .gitignore rules, especially when only size/mtime metadata is needed.
- Filtering a large in-memory list of paths against glob patterns without touching the file system (zlob_match_paths / indices variants).
- C code that wants glob(3) semantics plus \*\* and braces, and can take a Zig-built static or shared library.

## Skip it when

- Build systems that cannot add the Zig toolchain: the C library builds only with zig 0.16.0.
- Programs relying on sorted glob output by default: ZLOB_RECOMMENDED omits sorting, so you must drop NOSORT and give up some of the measured speed.
- Code needing GLOB_ALTDIRFUNC-style custom directory callbacks; path-matching mode documents that some flags (NOMAGIC, TILDE with relative paths) may not behave as expected.
- Linux without statx (WSL1): open issue #30 says walker metadata comes back as size/mtime 0 with no error or fallback.
- If you need the glibc glob() speedup as evidence: the README claims 1.2-1.7x (up to 10x) over glibc but publishes no table or harness for it.

## How it is fast

The pattern is analysed first so literal prefixes prune traversal (drivers/\*\*/\*.c only opens drivers/), and common leaf shapes such as \*.c or \*.{c,h,zig} compile to masked 1-4 byte suffix compares done for several suffixes at once with Zig @Vector SIMD (src/suffix_match.zig). Directory listing calls getdents64 directly on Linux (with a SWAR dirent scan as of 1.6.5), getattrlistbulk on macOS and ntdll on Windows; metadata comes from statx with a requested-field mask. The walker runs one directory per task on a work-stealing pool, and results are unsorted by default (ZLOB_NOSORT in ZLOB_RECOMMENDED).

## Compared with alternatives

Pick zlob when the job is pattern-driven file discovery (glob or gitignore-aware walk) inside your own program; al-dente (dent) and bfs are find-style command-line tools, and ripgrep is a searcher that only uses a walker internally.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none at runtime; Zig 0.16.0 to build (Rust crate wraps the same Zig code) |
| **Minimum toolchain** | zig 0.16.0 exactly (build.zig.zon minimum_zig_version 0.16.0; README says only 0.16.0) |
| **Platforms** | Linux, macOS, Windows (platform-specific listing paths); no-libc targets also built (a parallel-worker segfault there was fixed 2026-08-17) |
| **Thread safety** | Walker is multithreaded (threads=0 means one per CPU; visitor callbacks run on workers, with a worker_id for lock-free sharding); thread safety of concurrent zlob() calls not documented |
| **Drop-in for the baseline** | partial: C API mirrors glob(3) with a zlob prefix and zlob_t struct, but it is not a symbol-level replacement for glibc glob() and the Rust API differs from the glob and walkdir crates |

## Gotchas

- Walk table in the README says 'real 185k-entry repository' run with the 'medium/' filter, but rust/benches/walk_comparison.rs builds synthetic temp trees and its 'medium' tree is about 8,034 entries; the 185,737-entry numbers cannot be reproduced from the published harness as written, and the README does not say which zlob variant (serial, parallel, collect) each row is.
- In the glob benchmark the zlob side runs with NOSORT while the glob crate yields sorted per-directory output and allocates a PathBuf per match, so part of the gap is semantics, not matching speed; the globset+walkdir 1,000x+ ratios come from walking the whole tree for shallow patterns.
- \*\* does not follow directory symlinks by default (ZLOB_FOLLOW_SYMLINKS opts in with a (dev, ino) visited set), unlike the glob crate, so match counts on trees with directory symlinks differ; a nushell user reported 1,748 vs 1,767 matches for \*\*/\*.rs (issue #18, closed with PR #19).
- README links LICENSE.md, which does not exist; the license file is LICENSE (MIT).

## Known shortcomings

- The walk table does not match the harness: the README says a real 185k-entry repo with a medium/ filter, but walk_comparison.rs builds synthetic temp trees (medium is about 8,034 entries), so the walker rows are not reproducible from the published harness and the zlob variant per row is unstated. zlob runs NOSORT against the sorted glob crate. Open issue 30 (statx ENOSYS on WSL1 gives size/mtime 0, no fallback); issue 18 reports a count mismatch (1,748 vs 1,767).

## Caveats and trade-offs

The published tables compare against Rust crates (glob, globset+walkdir, walkdir, ignore), not glibc glob(); the glibc speedup claim has no published table or harness output on the page. rustc version is not stated (zig 0.16.0 is). Large globset+walkdir ratios (up to \~4,100x) reflect globset having to walk the whole tree for shallow patterns. README links LICENSE.md, which 404s; the license file is LICENSE (MIT per GitHub). [retier] Walker rows cannot be reproduced from the published harness (README says a real 185k-entry repo with a medium/ filter; walk_comparison.rs builds synthetic temp trees, medium about 8,034 entries; zlob variant per row unstated); zlob runs NOSORT against the sorted glob crate; baselines are Rust crates, not glibc; issue 30 (statx ENOSYS on WSL1) and issue 18 (count mismatch 1,748 vs 1,767) are open.

Needs the Zig toolchain (0.16.0 only) to build the C library; glob semantics are POSIX/glibc compatible with some flags unsupported (ALTDIRFUNC, parts of NOMAGIC).

## Maintenance

Actively developed (v1.6.5, last commit 2026-08-30, 230 stars), MIT-licensed and usable from C, but tied to zig 0.16.0 for builds.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** README benchmark table comes from the public criterion harness rust/benches/glob_comparison.rs (plus rust/benches/walk_comparison.rs, driven by scripts/run-benchmarks.sh), with toolchain and flags stated (zig 0.16.0 ReleaseFast static build, cargo bench) and CPU named (Intel Core i7-14700K); baseline is the Rust glob crate and globset+walkdir, both opened and confirmed in the harness source.
- **Verifier notes:** Harness files exist (glob_comparison.rs, walk_comparison.rs, run-benchmarks.sh all fetched). Off the C++-std baseline: incumbent is the Rust glob crate; glibc claim unverified.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/dmtrKovalenko/zlob/HEAD/README.md>
  - <https://raw.githubusercontent.com/dmtrKovalenko/zlob/HEAD/rust/benches/glob_comparison.rs>
  - <https://raw.githubusercontent.com/dmtrKovalenko/zlob/HEAD/rust/benches/walk_comparison.rs>
  - <https://raw.githubusercontent.com/dmtrKovalenko/zlob/HEAD/scripts/run-benchmarks.sh>
  - <https://github.com/dmtrKovalenko/zlob>
  - <https://github.com/dmtrKovalenko/zlob/commits/main>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/dmtrKovalenko/zlob/HEAD/README.md>
  - <https://raw.githubusercontent.com/dmtrKovalenko/zlob/HEAD/include/zlob.h>
  - <https://raw.githubusercontent.com/dmtrKovalenko/zlob/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/dmtrKovalenko/zlob/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/dmtrKovalenko/zlob/HEAD/rust/benches/glob_comparison.rs>
  - <https://raw.githubusercontent.com/dmtrKovalenko/zlob/HEAD/rust/benches/walk_comparison.rs>
  - <https://raw.githubusercontent.com/dmtrKovalenko/zlob/HEAD/scripts/run-benchmarks.sh>
  - <https://raw.githubusercontent.com/dmtrKovalenko/zlob/HEAD/src/suffix_match.zig>
  - <https://github.com/dmtrKovalenko/zlob>
  - <https://github.com/dmtrKovalenko/zlob/issues?q=is%3Aissue>
  - <https://github.com/dmtrKovalenko/zlob/issues/18>
  - <https://github.com/dmtrKovalenko/zlob/issues/30>
  - <https://github.com/dmtrKovalenko/zlob/commits/main>
  - <https://github.com/dmtrKovalenko/zlob/tree/main/src>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/dmtrkovalenko/zlob`) · [data/wave11/enrich/raw/github_com_dmtrkovalenko_zlob.json](../../../data/wave11/enrich/raw/github_com_dmtrkovalenko_zlob.json) (enrichment confidence 0.75)

</details>
