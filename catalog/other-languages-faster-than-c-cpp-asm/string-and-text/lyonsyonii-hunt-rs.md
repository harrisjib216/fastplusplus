# hunt (hunt-rs)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟡 stale

> Multithreaded Rust file-name finder (CLI); the author's warm-cache README runs show it 5.5-12x faster than GNU find.

| | |
|---|---|
| **Beats** | GNU find (C) |
| **Claimed result** | First match under \~/: hunt --hidden --first --exact SomeFile \~/ 180.2 ms +/- 7.4 vs find \~/ -name SomeFile -print -quit 2.219 s +/- 0.071, 12.31 +/- 0.64 times faster. All matches from /: hunt -H SomeFile / 633.6 ms +/- 25.1 vs find / -name "\*SomeFile\*" 3.473 s +/- 0.144, 5.48 +/- 0.31 times faster. (fd, Rust sibling: 913.6 ms and 1.452 s.) |
| **Workload** | File-name search over a home directory and the whole filesystem of one machine (about 2,762,223 files, including a network drive and an external drive): first match of a deeply nested hidden file, and all names containing 'SomeFile' from /. |
| **Metric** | latency |
| **Compiler and flags** | Cargo release profile lto=true, codegen-units=1, panic=abort, strip, with rayon, crossbeam-channel, mimalloc and memchr (Cargo.toml, version 3.0.0); GNU find version and build flags not stated; the README does not say which hunt version produced the numbers. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | Multithreaded parallel directory traversal (rayon work stealing, crossbeam channels) plus mimalloc and memchr substring search, per the README ('find did not perform any parallelism at all') and the Cargo.toml dependency comments. |
| **Adoption** | 104 stars |
| **Last commit** | 2025-07-06 |
| **Links** | [repository](https://github.com/LyonSyonII/hunt-rs) · [benchmark](https://github.com/LyonSyonII/hunt-rs) |

## Verdict

The author's own hyperfine runs on one undescribed machine (about 2.76 million files including a network and an external drive; CPU, kernel, filesystem, GNU find version and cache state not stated, and the script warms up once): finding a deeply nested hidden file under \~/ took 180.2 ms with the hunt build of May 2023 against 2.219 s for `find ~/ -name SomeFile -print -quit` (12.3x), and listing every name containing 'SomeFile' from / took 633.6 ms with the January 2022 build against 3.473 s for `find / -name "*SomeFile*"` (5.5x). In the second case hunt used about 1.9x find's total CPU time, so the speedup comes from running the walk on many cores.

## Use it when

- Interactive 'where did I put that file' lookups by name fragment over a large home directory or whole disk on a many-core machine with a warm dentry and inode cache.
- Quick substring or exact-name searches where grouped, sorted output (exact matches listed separately) is more useful than find's stream.
- Finding the first copy of a uniquely named file deep in a tree, where a parallel walk reaches deep branches sooner than find's depth-first order.
- Picking a result interactively (--select, --multiselect) in a shell session.

## Skip it when

- Scripts that need find semantics: no -mtime/-size/-perm/-exec/-prune, no regex or glob patterns, different option syntax, and output is buffered, grouped and sorted unless -ss is passed.
- Paths that must be piped safely: there is no -print0 option, paths are converted with to_string_lossy (non-UTF-8 names come out with U+FFFD), and the README's own `hunt -s -e SomeFile | xargs rm -r` example splits names containing spaces.
- Machines with few cores, cold caches, spinning disks or network filesystems: hunt spent equal or more total CPU than find in the README runs, so the margin rests on idle cores and on concurrent metadata I/O being fast; no cold-cache or low-core numbers exist.
- Reproducible first-match results: with several matching files the parallel walk returns whichever is found first, which can differ between runs.
- Long-lived tooling: last commit 2025-07-06, last release 3.0.0 (2024-11-13), single maintainer.

## How it is fast

Parallel directory traversal. search_dir() opens a rayon scope per directory and spawns every subdirectory as a work-stealing task with no depth limit by default (the HUNT_MAX_DEPTH environment variable switches deeper levels to serial recursion), so readdir calls for many directories run on all cores at once while GNU find walks one directory at a time. Per entry it takes the file type from the directory entry, does the substring test with a prebuilt memchr::memmem::Finder, allocates through mimalloc (the author reports about 15% from mimalloc in issue #8) and sends hits over a bounded crossbeam channel; --first calls process::exit on the first received hit. The README's own CPU columns show the win is wall-clock parallelism, not less work: about 1.54 s of user+system CPU for hunt against 1.58 s for find in the first-match case, and 5.38 s against 2.84 s in the all-matches case (derived from page data).

## Compared with alternatives

Pick hunt over fd (catalogued under systems-and-safety) only for plain name-fragment lookups where its grouped exact/contains output helps. fd has regex and glob patterns, .gitignore handling and -x/-X exec, and hunt's README win over fd (5.07x first match, 2.29x all matches) was measured on 2022-2023 builds. Use the walkdir or ignore crates (bench_walk) to embed a directory walker in Rust code, and uutils findutils when you need find-compatible syntax.

## Integration

| | |
|---|---|
| **Form** | binary crate (CLI; cargo install hunt, cargo binstall, or prebuilt release binaries) |
| **Dependencies** | clap, colored, rayon, crossbeam-channel, mimalloc (C allocator built from source), thin_str, memchr, inquire, profi; rustix on Linux, winapi-util on Windows |
| **Minimum toolchain** | crates.io 3.0.0 declares rust-version 1.74.1; the HEAD Cargo.toml uses edition 2024 (Rust 1.85 or newer) |
| **Platforms** | prebuilt for x86_64 Linux, x86_64 and aarch64 macOS, x86_64 Windows (cargo-dist targets); Unix and Windows code paths in source |
| **Thread safety** | not applicable (CLI); uses rayon's global pool on all cores and offers no thread-count option |
| **Drop-in for the baseline** | no |

## Gotchas

- The README numbers describe old builds, measured 16 months apart: the all-matches-from-/ rows (633.6 ms vs 3.473 s) were added in commit 060b8f4 on 2022-01-15, the hunt 1.5.x era when it still used jetscii and aho-corasick, and the first-match rows (180.2 ms vs 2.219 s) in commit aab3011 with the 2.0.0 release on 2023-05-26. Neither covers 3.0.0 or HEAD. The two cases also name different home directories (/home/user and /home/lyon). The shipped benchmarks/run script cannot regenerate them: it has no find row for the / case, passes fd --unrestricted instead of the README's fd flags, and runs hyperfine with --warmup 1 --ignore-failure, so every timing is warm-cache. The README points to a benchmarks.sh file that does not exist.
- The README says --first searches [current_dir, home_dir, root] and that `hunt -f -e SomeFile` searches the whole system. At HEAD, search.rs walks only '.' when no directory is given.
- Passing --ignore makes is_result() call canonicalize() (a realpath walk) on every entry visited, a large per-entry cost, and an entry whose canonicalize fails, such as a dangling symlink, is silently dropped from the results.
- Case-insensitive mode lowercases file names with to_ascii_lowercase while the automatic case-sensitivity switch checks Unicode uppercase, so non-ASCII letters match only in the same case. Directories given twice (one nested in another) are walked twice (documented; dedup request #6 is open). Read errors are skipped silently unless -v is set.

## Known shortcomings

- Multithreaded hunt against single-threaded GNU find: total CPU 1.54 s vs 1.58 s and 5.38 s vs 2.84 s (derived from page data), so the 12.31x and 5.48x are wall-clock parallelism; warm cache (--warmup 1); no hardware stated; the script is benchmarks/run; stale since 2025-07-06.
- Enricher: the README numbers predate 3.0.0 and come from two builds 16 months apart (the '/' rows from commit 060b8f4, 2022-01-15, and the first-match rows from aab3011, 2023-05-26); benchmarks/run cannot reproduce them (no find row for '/', different fd flags, warm cache, --ignore-failure). Docs drift (--first and 'whole system' wrong; HEAD searches only '.' by default); --ignore canonicalises every entry and silently drops dangling symlinks; the README's xargs rm -r example splits paths with spaces; output is lossy for non-UTF-8 names.

## Caveats and trade-offs

README numbers only, measured with hyperfine on one unspecified machine (no CPU, kernel, filesystem, cache state, GNU find version or hunt version) over a tree that includes a network drive and an external drive. hunt is multithreaded while GNU find is single-threaded, and the tools do different work (hunt --first searches [current_dir, home_dir, root] in its own order, sorts and groups output, matches exact or substring names; find -name uses glob matching in depth-first order), so the first-match latency depends on where the file sits in each tool's traversal order. The win is parallelism, not per-thread efficiency: user plus system CPU time is about 1.54 s for hunt against 1.58 s for find in the first-match case and about 5.38 s for hunt against 2.84 s for find in the all-matches case (derived from page data). benchmarks/run runs hyperfine -N --warmup 1, so the timings use a warm dentry and inode cache. The benchmark script is benchmarks/run (for the 'run' task runner), not benchmarks.sh as the README says (benchmarks.sh returns 404), and it compares hunt, a previous hunt 2.3.0 binary, fd and find (no locate). Last commit 2025-07-06 (about 15 months before the check). The locate row was omitted for the second case and quoted as 486.8 ms in the README text. [retier] Enricher: the '/' rows come from commit 060b8f4 (2022-01-15) and the first-match rows from aab3011 (2023-05-26), both before 3.0.0; benchmarks/run cannot reproduce them; --ignore silently drops dangling symlinks.

Simplified find: case-insensitive name match by default, results grouped and sorted, no regex or other find predicates, skips hidden directories unless --hidden, optional --ignore list; an opinionated tool rather than a find replacement.

## Maintenance

Stale: last commit 2025-07-06 (dependency, edition and flake updates) and last release 3.0.0 on 2024-11-13; MIT-licensed, about 42k crates.io downloads and 104 stars; installable from crates.io or prebuilt binaries, but the published speed numbers predate 3.0.0.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** README hyperfine output shows hunt 180.2 ms vs find 2.219 s (12.31x) and 633.6 ms vs 3.473 s (5.48x); the bench script benchmarks/run is public but no CPU model, GNU find version or hunt version is given, so first-party C.
- **Verifier notes:** README numbers match the record. Shortcomings to record: multithreaded tool against single-threaded GNU find (hunt spends equal or more total CPU time), different matching semantics and traversal order, warm-cache timings on one undescribed machine, stale since 2025-07-06.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-114 (wave 14 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/LyonSyonII/hunt-rs>
  - <https://raw.githubusercontent.com/LyonSyonII/hunt-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/LyonSyonII/hunt-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/LyonSyonII/hunt-rs/HEAD/benchmarks/run>
  - <https://github.com/LyonSyonII/hunt-rs/commits>
- **Sources the enricher read:**
  - <https://github.com/LyonSyonII/hunt-rs>
  - <https://raw.githubusercontent.com/LyonSyonII/hunt-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/LyonSyonII/hunt-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/LyonSyonII/hunt-rs/HEAD/benchmarks/run>
  - <https://github.com/LyonSyonII/hunt-rs/tree/main/src>
  - <https://raw.githubusercontent.com/LyonSyonII/hunt-rs/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/LyonSyonII/hunt-rs/HEAD/src/search.rs>
  - <https://raw.githubusercontent.com/LyonSyonII/hunt-rs/HEAD/src/structs.rs>
  - <https://raw.githubusercontent.com/LyonSyonII/hunt-rs/HEAD/src/print.rs>
  - <https://raw.githubusercontent.com/LyonSyonII/hunt-rs/HEAD/src/searchresult.rs>
  - <https://github.com/LyonSyonII/hunt-rs/commits/main/README.md>
  - <https://github.com/LyonSyonII/hunt-rs/commit/aab3011>
  - <https://github.com/LyonSyonII/hunt-rs/commit/060b8f4>
  - <https://github.com/LyonSyonII/hunt-rs/commits/main>
  - <https://github.com/LyonSyonII/hunt-rs/issues?q=is%3Aissue>
  - <https://github.com/LyonSyonII/hunt-rs/issues/8>
  - <https://crates.io/api/v1/crates/hunt>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/lyonsyonii/hunt-rs`) · [data/wave14/enrich/raw/github_com_lyonsyonii_hunt_rs.json](../../../data/wave14/enrich/raw/github_com_lyonsyonii_hunt_rs.json) (enrichment confidence 0.75)

</details>
