# al-dente (dent)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟡 stale

> Small multithreaded C directory walker on raw getdents64 that prints every path; beats GNU find and fd on a synthetic tree.

| | |
|---|---|
| **Beats** | GNU find (readdir/fts directory traversal); also fd |
| **Claimed result** | Listing 765,200 entries: find 3.178 s, fdfind -HI 1.633 s, dent 563.9 ms (5.64x faster than find, 2.90x faster than fdfind); with grep for a regex: 6.01x faster than find -iregex, 1.60x faster than fdfind |
| **Workload** | Listing a synthetic tree of 765,200 entries with a multithreaded getdents64 walker, timed with hyperfine (3 warmups, 10 runs). |
| **Metric** | latency |
| **Compiler and flags** | gcc -Wall -pthread -O3 (Makefile) |
| **Adoption** | 18 stars |
| **Last commit** | 2024-10-03 |
| **Links** | [repository](https://github.com/royreznik/al-dente) · [benchmark](https://github.com/royreznik/al-dente) |

## Verdict

First-party hyperfine (3 warmups, 10 runs) on a synthetic tree the README says holds 765,200 entries, with warm caches implied: dent 563.9 ms vs GNU find 3.178 s (5.64x) and fdfind -HI 1.633 s (2.90x); piping to grep for one name was 6.01x faster than find -iregex and 1.60x faster than fd. Built with gcc -O3 per the Makefile; CPU, core count, filesystem and kernel are not stated, and dent and fd ran multithreaded while find is single-threaded.

## Use it when

- Dumping the full path list of a large tree (hundreds of thousands to millions of entries) on Linux, on a local filesystem that fills in d_type
- Feeding a path list to grep or another tool when you do not need find's predicates, ordering or metadata
- As a short, readable reference for a parallel getdents64 walker you can adapt into your own C/C++ code (MIT license)

## Skip it when

- Filesystems that return DT_UNKNOWN in d_type (some NFS, older XFS, reiserfs and FUSE setups): dent never stats, so it silently does not descend into those directories
- Any use that needs find/fd features: name or type filters, depth limits, ignore files, -exec, stat-based predicates, stable output order
- Pipelines that expect clean text paths: entry names are printed with up to 7 trailing NUL padding bytes (see gotchas), which is why the README's grep example needs -a
- Non-Linux systems (raw getdents64 syscall)
- Long-lived production use: single burst of commits in October 2024, no tests of output correctness against find, code written with ChatGPT per the README

## How it is fast

Worker threads (pthreads) pop directory paths from a mutex/condvar work queue, read each directory with the raw getdents64 syscall into a 256 KiB thread-local buffer, and recurse into children whose d_type is DT_DIR without ever calling stat. Output is built in a 256 KiB thread-local buffer and written with one fwrite per flush. The speedup over GNU find comes mostly from parallelism (dent's system time, 1.82 s, is over 3x its 0.56 s wall time) plus skipping per-entry libc/fts overhead.

## Compared with alternatives

Pick dent only when you want the smallest possible parallel getdents64 walker to copy and you control the filesystem; bfs is the catalogued choice for a find-compatible, maintained traversal tool, and lsr covers single-directory ls -l listing rather than recursive walks.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond libc and pthreads |
| **Minimum toolchain** | C with GNU extensions (gcc; _GNU_SOURCE, __thread, __builtin_prefetch) |
| **Platforms** | Linux only |
| **Thread safety** | not applicable as a program; list_directory uses static thread-local buffers, so it is not reentrant within one thread |
| **Drop-in for the baseline** | partial — equivalent to a bare 'find DIR' listing (same set of paths, unordered, with NUL padding bytes), nothing more |

## Gotchas

- Name length is computed as d_reclen - offsetof(d_name) - 1, but d_reclen is padded to 8 bytes, so each printed name carries 0-7 trailing NUL bytes before the newline. Directory recursion still works (strdup stops at the first NUL), but the output is not byte-identical to find's and needs grep -a; the benchmarked output was this padded form (read from dent.c).
- The committed benchmark_scenario.c (DEPTH 4, BREADTH 32) does not produce the README's 765,200-entry tree: it creates 1,082,400 directories and 1,082,400 unique files (the file loop sits inside the directory loop, rewriting the same 32 files 32 times), and its printed counter would read 35,719,200. The tree that was timed is therefore not reproducible from the repo as-is (computed from the source).
- README says MAX_CONCURRENT_THREADS in dirlist.h defaults to 1000, but no such file or macro exists; the actual default is 10 threads from main.c, and the README's 'executable named dirlist' is really dent.
- README says the project is 'provided as-is without any warranty' but the repo root has an MIT LICENSE (Copyright 2024 roy reznik); open() failures (permissions) are printed with perror and skipped.

## Known shortcomings

- The name length is taken from the padded d_reclen, so printed names carry 0-7 trailing NUL bytes (hence grep -a in the README) and the output is not byte-identical to find. The committed benchmark_scenario.c (DEPTH 4, BREADTH 32) builds 2,164,800 unique entries, not the claimed 765,200, so the timed tree is not reproducible from the repo. README thread docs are wrong: the real default is 10 threads, not 1000, and dirlist.h does not exist.

## Caveats and trade-offs

No hardware or filesystem stated; single synthetic scenario (benchmark_scenario.c); warm cache implied; fd and dent are both multithreaded (system time exceeds wall time), find is single-threaded. README says the multithreading was written with ChatGPT. Default MAX_CONCURRENT_THREADS is 1000.

Linux only (getdents64); lists names only, no stat; README says AI-assisted derivation of a coworker's code.

## Maintenance

Stale since 2024-10-03 (ten commits over two days, 18 stars, one closed issue), MIT-licensed and small enough to vendor, but fix the NUL-padding name length before relying on its output.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party hyperfine run against GNU find and fdfind in the README; benchmark generator (benchmark_scenario.c) and Makefile flags (gcc -Wall -pthread -O3) are public, but no CPU model or filesystem is stated, so not A.
- **Verifier notes:** A LICENSE file exists at the repo root and is MIT (Copyright 2024 roy reznik), so usability moves from reference to copyable. Numbers match the README exactly.
- **Fields the verifier corrected:** `license`, `usability`, `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/royreznik/al-dente>
  - <https://github.com/royreznik/al-dente/commits>
  - <https://raw.githubusercontent.com/royreznik/al-dente/HEAD/README.md>
  - <https://raw.githubusercontent.com/royreznik/al-dente/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/royreznik/al-dente/HEAD/Makefile>
- **Sources the enricher read:**
  - <https://github.com/royreznik/al-dente>
  - <https://raw.githubusercontent.com/royreznik/al-dente/HEAD/README.md>
  - <https://raw.githubusercontent.com/royreznik/al-dente/HEAD/Makefile>
  - <https://raw.githubusercontent.com/royreznik/al-dente/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/royreznik/al-dente/HEAD/dent.c>
  - <https://raw.githubusercontent.com/royreznik/al-dente/HEAD/dent.h>
  - <https://raw.githubusercontent.com/royreznik/al-dente/HEAD/main.c>
  - <https://raw.githubusercontent.com/royreznik/al-dente/HEAD/benchmark_scenario.c>
  - <https://github.com/royreznik/al-dente/commits>
  - <https://github.com/royreznik/al-dente/issues?q=is%3Aissue>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/royreznik/al-dente`) · [data/wave11/enrich/raw/github_com_royreznik_al_dente.json](../../../data/wave11/enrich/raw/github_com_royreznik_al_dente.json) (enrichment confidence 0.75)

</details>
