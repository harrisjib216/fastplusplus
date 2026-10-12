# dumac (Rust parallel du -sh for macOS)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Rust` · `no license` · 🟡 stale

> macOS-only Rust du -sh clone: parallel getattrlistbulk walk, about 5.7x faster than BSD du on a warm synthetic tree.

| | |
|---|---|
| **Beats** | macOS du -sh (BSD du, C); diskus is also compared |
| **Claimed result** | README hyperfine output: dumac 563.1 ms +- 22.6 vs du -sh 3.186 s +- 0.198 (5.66 +- 0.42 times faster) vs diskus 1.834 s +- 0.157 (3.26 +- 0.31 times faster). |
| **Workload** | Computing the total size of a synthetic tree built by setup_benchmark.py: 12 levels with branching factor two (4095 directories), 100 files of 70 bytes in every directory (409,500 files), warm disk cache. The README calls it '100 small files per level', but the script writes 100 files into each directory. |
| **Metric** | latency |
| **Hardware** | Apple Silicon Mac, model not stated ('modern Apple hardware') |
| **Compiler and flags** | cargo build --release; rustc version not stated; hyperfine --warmup 3 --min-runs 5; setup_benchmark.py builds the tree. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Why it wins** | README: parallel directory traversal using the macOS getattrlistbulk bulk-attribute syscall. |
| **Adoption** | 65 stars |
| **Last commit** | 2025-08-07 |
| **Links** | [repository](https://github.com/healeycodes/dumac) · [benchmark](https://raw.githubusercontent.com/healeycodes/dumac/HEAD/README.md) |

## Verdict

First-party hyperfine (warmup 3, 5 runs, warm cache) on a synthetic 12-level binary tree (4,095 directories, 100 files of 70 bytes each, 409,500 files) on the author's Apple M1 Pro (named in his blog post, not the README): dumac 563.1 ms vs macOS BSD du -sh 3.186 s (5.66x) and diskus 1.834 s (3.26x). The win comes from batched metadata syscalls plus multithreading, not from Rust: the author's own Go plus cgo build of the same getattrlistbulk loop ran 564.6 ms in the first blog run.

## Use it when

- Interactive or scripted total-size queries on large local APFS trees (node_modules, build caches, home folders) on a multi-core Apple Silicon Mac, where wall-clock time matters more than CPU time.
- Trees with many small files per directory, where per-file lstat dominates BSD du's runtime and batching metadata reads pays off most.
- As a reference implementation of correct getattrlistbulk parsing in Rust (RETURNED_ATTRS bitmap, attrreference_t name offsets, read_unaligned field walk) to copy the technique into your own scanner, keeping in mind the code has no license.

## Skip it when

- Anything that must match du byte for byte: directories' own blocks are not added (Apple du adds them in its FTS_DP case), every symlink is charged one 512-byte block although APFS keeps short targets inline at 0 blocks (open PR #7 measured 255.1M vs du 253.3M on /usr/share, 3,556 symlinks), and the human-readable rounding differs (870.8G vs du's 1.4T style).
- Linux, BSD or Windows: it calls getattrlistbulk and libc::__error, so it only builds on macOS (10.10 or later for the syscall).
- Trees that span volumes (scans of /, /Volumes, mounted images): inode dedup ignores the device id and applies to every file, while Apple du only dedups files with st_nlink &gt; 1 keyed by (st_dev, st_ino), so files on different volumes with colliding inode numbers can be silently dropped.
- Scripts that rely on exit status or deep paths: errors below the root (EACCES, EMFILE, ENAMETOOLONG once a joined path passes PATH_MAX because it calls open() on full path strings rather than openat) are printed to stderr, the subtree counts as 0, and the process still exits 0; du sets exit status 1.
- Battery- or CPU-constrained use: it trades total CPU for wall time (user+system 2.27 s vs du 1.43 s in the README run).

## How it is fast

Each directory is read with getattrlistbulk(2) into a 128 KiB buffer, which returns name, object type, inode (ATTR_CMN_FILEID) and ATTR_FILE_ALLOCSIZE for a batch of entries per syscall, so there is no lstat per file as in fts-based du. Subdirectories are recursed with a rayon work-stealing pool (available_parallelism threads, capped at 224) with 16 MiB stacks. Hard-link dedup uses 128 parking_lot-mutex-sharded HashSets keyed by inode &gt;&gt; 8, so runs of sequentially allocated APFS inodes from one directory land in one shard (the author measured lock collisions dropping from 176.66 to 4.66 per run).

## Compared with alternatives

Pick dumac on macOS for a single total; on Linux the catalogued walkers (c-blake's cligen/dents du replacement, minifind, fd for find-style searches) apply instead, and for copy or delete of large trees the FUC tools (cpz, rmz) are the analogues. diskus (already listed) is portable and closer to du's semantics, but on the author's benchmark it used about 10 s of system time to dumac's 2.2 s.

## Integration

| | |
|---|---|
| **Form** | source-drop (Rust binary crate, cargo build --release; not published on crates.io, no releases) |
| **Dependencies** | libc 0.2.174, rayon 1.10.0, parking_lot 0.12.4 (tempfile for tests) |
| **Minimum toolchain** | Rust 1.80 or later (uses std::sync::LazyLock), edition 2021; macOS 10.10+ for getattrlistbulk |
| **Platforms** | macOS only (Apple Silicon tested by the author on an M1 Pro; Intel Macs not documented) |
| **Thread safety** | Single-shot CLI; the global SEEN_INODES set is process-wide and never cleared, so calling calculate_size twice in one process (as the tests do, with clear_seen_inodes) undercounts unless cleared. |
| **Drop-in for the baseline** | partial — replaces only 'du -sh &lt;one dir&gt;'; totals differ from du (no directory blocks, symlinks charged 1 block, all-inode dedup without device), no options, exit status 0 on subtree errors |

## Gotchas

- Error-entry parsing bug: per getattrlistbulk(2) and xnu get_error_attributes(), an entry that failed is packed as RETURNED_ATTRS, ERROR, then NAME, but dumac reads NAME before ERROR. On such entries it builds the name from the error word and takes the name's attr_length as the error code, so the entry is still skipped but the message shows a garbled or missing name and a bogus error number. Successful entries are parsed correctly because the kernel omits ATTR_CMN_ERROR when RETURNED_ATTRS is requested.
- Earlier versions undercounted real trees by about 35 percent (issue #2: 870.8G vs du 1.4T on a \$HOME) because a per-directory semaphore let open file descriptors grow past ulimit -n; fixed 2025-08-05 (931ac28, cap 224 in 03846c1). The author's first blog post figures (6.4x vs du, 2.58x vs diskus) were measured on that pre-fix tokio build, and hyperfine discards stderr, so skipped subtrees would not have been visible. The README figures (5.66x, 3.26x) come from the later rayon build, which holds at most one directory fd per thread.
- Run-to-run swing is large and the headline ratio moves with the du run: README revisions show du -sh at 3.330 s (2025-07-31), 2.484 s (2025-08-05, 4.58x) and 3.186 s (2025-08-07, 5.66x), and the second blog post timed the rayon build at 711.9 and 731.6 ms on the same tree versus 563.1 ms in the README. Only the deep tree is reported; setup_benchmark.py also builds a 'wide' tree (500 directories x 500 files) whose results are not published.
- Unlike Apple du, it does not set vfs.nspace.prevent_materialization (rdar://44903941 in du.c), so walking dataless File Provider or iCloud directories may materialize them. It also has no hard-linked-directory check (du's dirlinkchk) and does not cross-check its totals against du in tests (the three tests only assert lower bounds and hard-link dedup).

## Known shortcomings

- No license, Mac model unstated, warm cache only; the win is rayon parallelism plus getattrlistbulk, not Rust; output not tested against du; diskus is listed (wave 11); the blog (unreachable) reports 6.4x for an earlier tokio version.
- Parser bug: when an entry errors, the kernel packs ATTR_CMN_ERROR before NAME (xnu get_error_attributes, getattrlistbulk(2)) but dumac reads NAME first, so the entry is skipped with a garbled name and bogus error code. Issue #2: the earlier tokio build undercounted \$HOME by 35% (870.8G vs du 1.4T) from fd exhaustion, fixed 2025-08-05; the blog's 6.4x/2.58x were measured on that pre-fix build while the README 5.66x is the post-fix rayon build; the du baseline swings 2.484-3.330 s across README revisions (4.58x-6.39x). Symlinks are charged one block (open PR #7: 255.1M vs du 253.3M); inode dedup ignores the device; exit 0 on subtree errors. The author's Go+cgo build of the same C loop ran 564.6 ms, so the speed is not from Rust.

## Caveats and trade-offs

Synthetic tree and warm cache only (author says he found no reliable way to clear the macOS disk cache). Mac model not named. No LICENSE file and no license field in Cargo.toml. Not a language win: dumac runs a rayon work-stealing traversal on up to available_parallelism threads and reads name, type, inode and allocated size for a batch of entries per getattrlistbulk call, while BSD du walks single-threaded with fts and one stat per entry; dumac spends more total CPU (user+system 2.27 s vs du 1.43 s) to cut wall time. dumac counts only regular files and symlinks (directories' own blocks are not added) and dedups every inode, and its tests do not compare its output with du's. The author's first blog post (healeycodes.com, blocked here; search snippet only) reported 6.4x vs du and 2.58x vs diskus for an earlier tokio-based version, while the README shows 5.66x and 3.26x. [retier] Issue #2: the earlier tokio build undercounted \$HOME by 35% from fd exhaustion (fixed 2025-08-05); the blog's 6.4x/2.58x were measured on that pre-fix build while the README 5.66x is the post-fix rayon build; the du baseline swings 2.484-3.330 s across README revisions (4.58x-6.39x). Parser bug: on an errored entry the kernel packs ATTR_CMN_ERROR before NAME but dumac reads NAME first (entry skipped with a garbled name). Symlinks charged one block (open PR #7); inode dedup ignores the device; exit 0 on subtree errors. The author's Go+cgo build of the same C loop ran 564.6 ms, so the speed is not from Rust.

macOS only. No license file or Cargo license field, so the code cannot be copied.

## Maintenance

Stale since 2025-08-07 (19 commits, 65 stars), an open symlink-sizing PR (#7, 2026-08-04) has no maintainer response, and there is no LICENSE file or Cargo license field, so it is reference-only: read it for the getattrlistbulk technique, do not vendor it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party hyperfine output in the README against macOS du -sh and diskus, with public source and tree generator (setup_benchmark.py), but no Mac model or CPU, no rustc version and no independent run, so C.
- **Verifier notes:** Numbers match the README (563.1 ms vs du 3.186 s, 5.66x; vs diskus 1.834 s, 3.26x). Shortcomings to record: no license (reference only), Mac model unstated, warm cache only, win is parallelism plus getattrlistbulk rather than Rust, output equivalence with du not tested, earlier blog numbers differ (snippet only). Metadata checked: 65 stars, 19 commits, last commit 2025-08-07 (stale). diskus is already listed (wave 11); dumac is a separate project, not a duplicate.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-107 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/healeycodes/dumac/HEAD/README.md>
  - <https://github.com/healeycodes/dumac>
  - <https://github.com/healeycodes/dumac/commits>
  - <https://raw.githubusercontent.com/healeycodes/dumac/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/healeycodes/dumac/HEAD/setup_benchmark.py>
  - <https://raw.githubusercontent.com/healeycodes/dumac/HEAD/src/main.rs>
  - <https://github.com/healeycodes/dumac/tree/main/tests>
  - <https://raw.githubusercontent.com/healeycodes/dumac/HEAD/tests/integration_tests.rs>
- **Sources the enricher read:**
  - <https://github.com/healeycodes/dumac>
  - <https://raw.githubusercontent.com/healeycodes/dumac/HEAD/README.md>
  - <https://raw.githubusercontent.com/healeycodes/dumac/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/healeycodes/dumac/HEAD/Cargo.lock>
  - <https://raw.githubusercontent.com/healeycodes/dumac/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/healeycodes/dumac/HEAD/setup_benchmark.py>
  - <https://raw.githubusercontent.com/healeycodes/dumac/HEAD/tests/integration_tests.rs>
  - <https://raw.githubusercontent.com/healeycodes/dumac/a2901c6867f194be73f92486826f33d3cf7658cb/README.md>
  - <https://raw.githubusercontent.com/healeycodes/dumac/a2901c6867f194be73f92486826f33d3cf7658cb/src/main.rs>
  - <https://raw.githubusercontent.com/healeycodes/dumac/152dad272ae3e1c73ecaead23341fb32392729ee/README.md>
  - <https://github.com/healeycodes/dumac/commits/main>
  - <https://github.com/healeycodes/dumac/issues?q=is%3Aissue>
  - <https://github.com/healeycodes/dumac/issues/2>
  - <https://github.com/healeycodes/dumac/pulls?q=is%3Apr>
  - <https://github.com/healeycodes/dumac/pull/7>
  - <https://raw.githubusercontent.com/healeycodes/healeycodes.com/main/posts/maybe-the-fastest-disk-usage-program-on-macos.md>
  - <https://raw.githubusercontent.com/healeycodes/healeycodes.com/main/posts/optimizing-my-disk-usage-program.md>
  - <https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/bsd/man/man2/getattrlistbulk.2>
  - <https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/bsd/man/man2/getattrlist.2>
  - <https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/bsd/vfs/vfs_attrlist.c>
  - <https://raw.githubusercontent.com/apple-oss-distributions/file_cmds/main/du/du.c>
  - <https://crates.io/api/v1/crates/dumac>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/healeycodes/dumac`) · [data/wave14/enrich/raw/github_com_healeycodes_dumac.json](../../../data/wave14/enrich/raw/github_com_healeycodes_dumac.json) (enrichment confidence 0.8)

</details>
