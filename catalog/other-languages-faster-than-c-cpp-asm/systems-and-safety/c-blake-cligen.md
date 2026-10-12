# cligen/dents (c-blake, Nim fast directory walker behind find, ls and du)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Nim` · `ISC` · 🟢 active

> Nim getdents64/openat tree walker (cligen/dents) whose find, ls -R and du demos claim 1.4-4.5x over GNU tools.

| | |
|---|---|
| **Beats** | GNU find, GNU ls -1AUR and GNU du (C); BSD find and fd are also named for find |
| **Claimed result** | Doc comments in dents.nim: find '2.75-4.5X faster than GNU find /usr; 1.7x faster than BSD find\|fd'; ls1AU '-r0 is 1.7-2.25x faster than GNU ls -1AUR --color=none /usr &gt;/dev/null'; lss1AU '1.45-2.0x faster than ls -s1AUR'; bu/doc/du.md: 'my 1.4-2x faster file tree walk' for a mostly compatible GNU du replacement. |
| **Workload** | Recursive tree walk of /usr printing paths (dents find vs GNU find, BSD find and fd), listing with ls -1AUR --color=none and ls -s1AUR --color=none to /dev/null (dents ls1AU -r0, lss1AU -r0), and du totalling st_blocks (bu du vs GNU du). |
| **Metric** | latency (wall time) |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | dents.nim header: raw getdents64 saves one fstat per directory compared with opendir or fdopendir, openat/fstatat remove most full-path handling, and an optimistic open after d_type avoids lstat; the author also notes GNU find's handling of arbitrary filesystem depth. |
| **Adoption** | 584 stars (cligen); used by the c-blake/bu tools |
| **Last commit** | 2026-08-26 |
| **Links** | [repository](https://github.com/c-blake/cligen) · [benchmark](https://raw.githubusercontent.com/c-blake/cligen/HEAD/cligen/dents.nim) |

## Verdict

Only one-line doc comments: find 2.75-4.5x faster than GNU find on /usr and 1.7x faster than FreeBSD find (fd added later to the same comment); ls1AU -r0 1.7-2.25x and lss1AU 1.45-2.0x faster than GNU ls -1AUR / ls -s1AUR --color=none to /dev/null; bu du '1.4-2x faster' walk than GNU du. No machine, kernel, file system, cache state, tool versions, Nim/C flags or script are given. The numbers date from 2020, cover the non-batch build with the unsafe-on-NFS early-EOF default, and the ls comparisons do not produce identical output.

## Use it when

- Nim programs that must walk large local trees (ext4/xfs/btrfs/tmpfs) and want per-entry, pre- and post-directory hooks with the open dir fd and statx data available for \*at() calls
- Replacing a simple 'find DIR' / 'find -print0' or 'du -s' in scripts that run often on hot-cache local trees, where per-syscall overhead dominates
- Tools that need post-order aggregation (du-like totals, rm -rf like bu/rr) without building path strings for every syscall
- Linux x86-64 or similar; it also builds on BSDs through the libc fdopendir/readdir path, but the getdents64 speedups are Linux-only

## Skip it when

- NFS, sshfs or other FUSE/network file systems with default settings: the early-EOF shortcut can stop reading a directory after a short getdents read and silently drop entries (the source says 'Sadly, fails on sshfs/NFS/etc.'). Pass --eof0 / eof0=true there; bu du hard-codes eof0=false, so it cannot be made safe
- Very deep trees: each level holds an open fd and EMFILE/ENFILE silently ends that subtree (recFailDefault discards them). It is depth-limited by ulimit -n, unlike GNU find's fts
- When you need find predicates (-name, -newer, -exec, -prune) or exact GNU ls/du output; the demos print fixed formats and du drops several options
- Cold-cache or many-core NVMe walks: it is single-threaded, while parallel walkers such as fd or minifind may win there; no cold-cache numbers exist
- Non-Linux targets that care about speed: the getdents64 path, batch mode and the statx timestamps are Linux-specific

## How it is fast

On Linux it calls getdents64 through syscall() into a 4066-byte buffer, which skips the fstat that opendir/fdopendir does per directory. It descends with openat/fstatat (statx) relative to the parent fd, so the kernel never sees full paths. It trusts d_type and opens directories optimistically with O_DIRECTORY instead of lstat-ing each entry. By default it treats a short getdents read as end-of-directory, which saves one getdents call per directory. An optional -d:batch build sends each directory's statx calls through the author's out-of-tree sys_batch kernel module; the author says this adds about 1.25x more.

## Compared with alternatives

Pick dents over fd or minifind when you are writing Nim, need a library hook (pre/post-order callbacks with the dir fd) rather than a CLI, and walk hot local trees single-threaded. Pick fd for find-style matching with ignore files and parallelism, and dumac for a parallel du on macOS; dents has no measured numbers on par with their hyperfine tables.

## Integration

| | |
|---|---|
| **Form** | module (Nim source, part of the cligen nimble package) |
| **Dependencies** | none beyond the Nim stdlib and libc; optional out-of-tree c-blake 'batch' kernel module and headers for -d:batch |
| **Minimum toolchain** | Nim &gt;= 1.4.0 per cligen.nimble (the nimble file warns that helper modules may need newer Nim); C backend |
| **Platforms** | Linux (getdents64 fast path; statx used only if the build host has /usr/include/bits/statx.h or the x86_64-linux-gnu copy, checked at compile time, else an fstatat fallback); other POSIX through libc fdopendir/readdir |
| **Thread safety** | not documented; forPath keeps its state in template-local variables and uses the process-wide errno, so treat it as single-threaded |
| **Drop-in for the baseline** | partial: find prints the same path set for a plain recursive print on local file systems but has no predicates; ls1AU/lss1AU emit a different output order; bu du is 'mostly compatible' with GNU du but drops time, max-depth and separate-dirs options and uses PCRE patterns |

## Gotchas

- Early EOF is on by default: eof0=false makes fdopendir set eeof=true, so any getdents read shorter than about 3.5 KB ends the directory. Commit 7559cff (2020-06-28) turned the earlier opt-in -d:dentsLocalFS build switch into this runtime default. The benchmarked find/ls runs therefore used a shortcut that is unsafe on NFS/sshfs.
- By code reading (not run): ls1AU and lss1AU buffer each directory's names and print them in the post-recursion hook, so subdirectories are listed before their parents, unlike GNU ls -R. lss1AU's showLong prints label.dirname (libc dirname), so each header names the parent directory. Their timed outputs went to /dev/null, which hides both differences from ls -1AUR / ls -s1AUR.
- bu du (by code reading): the binary -p/--peta scale returns 1 shl 40 (TiB) instead of 1 shl 50; --exclude only skips adding the matched path's size and does not prune the walk; eof0 is hard-wired false. cligen/statx's &lt; and &lt;= on StatxTs compare tv_nsec with the other side's tv_sec.
- The '1.7x faster than BSD find|fd' figure was first written as '1.7x faster than FreeBSD find'. Commit ebb78e9 (2020-10-28) only added '|fd' to that comment, with no new number for fd.

## Known shortcomings

- Ratios are source comments (dents.nim lines 342, 383 and 428, bu/doc/du.md) from 2020 with no methodology; the -d:batch mode is left out; 'fd' is the Rust fd (commit ebb78e9).
- Early-EOF shortcut is on by default (eof0=false sets eeof=true): a short getdents read ends the directory, which the source says fails on sshfs and NFS; commit 7559cff (2020-06-28) turned the old opt-in -d:dentsLocalFS into this default, so the benchmarked find and ls runs used it, and bu du hard-codes eof0=false. EMFILE/ENFILE silently ends a subtree (depth capped by ulimit -n). Commit ebb78e9 only added '|fd' to the old '1.7x faster than FreeBSD find' comment with no separate fd number. By code reading: ls1AU and lss1AU print in post-order and lss1AU headers show the parent directory via libc dirname (outputs went to /dev/null); bu du -p uses 1 shl 40, --exclude does not prune, and StatxTs &lt; and &lt;= compare tv_nsec with tv_sec.

## Caveats and trade-offs

The numbers are one-line source comments with no machine, kernel, file system, cache state, tool versions, Nim build flags or script; ranges are given without raw timings. The ratios date from 2020 and cover only the portable path: commit 2948a0d (2020-06-19) says the optional -d:batch mode (a custom sys_batch kernel module) adds about another 1.25x and that the help ratios were deliberately not updated for it. The '1.7x faster than BSD find|fd' comment means both BSD find and the Rust fd (commit ebb78e9, 2020-10-28: 'Also include slow Rust fd in comparison'). The walk is a different implementation from GNU find's fts traversal: bu/doc/newest.md says GNU find worries about arbitrary file-system depth while the author has never seen a non-artificial depth above 30, so the walker trades generality for speed. Workloads are print-only walks of /usr, not find with predicates. [retier] The numbers are one-line source comments with no machine, kernel, file system, cache state, tool versions, Nim flags or script; ranges without raw timings, dating from 2020 and covering only the portable path (the -d:batch mode adds about 1.25x per commit 2948a0d). Early-EOF shortcut is on by default (eof0=false sets eeof=true): a short getdents read ends the directory, which the source says fails on sshfs and NFS; commit 7559cff (2020-06-28) turned the old opt-in -d:dentsLocalFS into this default, so the benchmarked find and ls runs used it, and bu du hard-codes eof0=false. EMFILE/ENFILE silently ends a subtree (depth capped by ulimit -n). Commit ebb78e9 only added '|fd' to the old '1.7x faster than FreeBSD find' comment with no separate fd number. By code reading: ls1AU and lss1AU print in post-order and lss1AU headers show the parent directory via libc dirname (outputs went to /dev/null); bu du -p uses 1 shl 40, --exclude does not prune, and StatxTs &lt; and &lt;= compare tv_nsec with tv_sec.

Linux-oriented (raw getdents64, optional custom kernel batch-syscall module that is not mainline). Not a general find: no expression language; the du clone drops several options and uses PCRE patterns.

## Maintenance

Actively maintained (last commit 2026-08-26, ISC, 584 stars) and easy to vendor as one Nim module plus cligen helpers. The speed claims are unreproducible 2020 comments, and the default early-EOF shortcut, silent EMFILE bottoming-out and the output differences found in ls1AU/lss1AU and bu du (code reading, not run) mean you should pass eof0=true on network file systems and not treat the demos as exact GNU replacements.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The ratios are first-party one-line doc comments in cligen/dents.nim (find, ls1AU, lss1AU) and bu/doc/du.md, with no timings, machine, kernel, file system, cache state, tool versions, build flags or script, so C.
- **Verifier notes:** All quoted ratios are verbatim in cligen/dents.nim lines 342, 383 and 428 and bu/doc/du.md; ISC licence, 584 stars, last commit 2026-08-26 confirmed. Record shortcomings: no methodology at all, 2020-era ratios, batch-mode speedups excluded from the stated ratios, depth-limited design.
- **Fields the verifier corrected:** `caveats`, `workload`
- **Shortcomings recorded by:** verifier batch-97 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/c-blake/cligen/HEAD/cligen/dents.nim>
  - <https://raw.githubusercontent.com/c-blake/cligen/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/c-blake/bu/HEAD/doc/du.md>
  - <https://raw.githubusercontent.com/c-blake/bu/HEAD/doc/newest.md>
  - <https://raw.githubusercontent.com/c-blake/bu/HEAD/README.md>
  - <https://github.com/c-blake/cligen>
  - <https://github.com/c-blake/cligen/commits/master>
  - <https://github.com/c-blake/cligen/commits/master/cligen/dents.nim>
  - <https://github.com/c-blake/cligen/commit/2948a0d>
  - <https://github.com/c-blake/cligen/commit/ebb78e9>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/c-blake/cligen/HEAD/cligen/dents.nim>
  - <https://raw.githubusercontent.com/c-blake/cligen/HEAD/cligen/statx.nim>
  - <https://raw.githubusercontent.com/c-blake/cligen/HEAD/cligen/posixUt.nim>
  - <https://raw.githubusercontent.com/c-blake/cligen/HEAD/cligen/osUt.nim>
  - <https://raw.githubusercontent.com/c-blake/cligen/HEAD/README.md>
  - <https://raw.githubusercontent.com/c-blake/cligen/HEAD/RELEASE-NOTES.md>
  - <https://raw.githubusercontent.com/c-blake/cligen/HEAD/cligen.nimble>
  - <https://raw.githubusercontent.com/c-blake/cligen/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/c-blake/bu/HEAD/README.md>
  - <https://raw.githubusercontent.com/c-blake/bu/HEAD/doc/du.md>
  - <https://raw.githubusercontent.com/c-blake/bu/HEAD/doc/newest.md>
  - <https://raw.githubusercontent.com/c-blake/bu/HEAD/du.nim>
  - <https://raw.githubusercontent.com/c-blake/bu/HEAD/bu.nimble>
  - <https://github.com/c-blake/cligen>
  - <https://github.com/c-blake/cligen/commits/master/cligen/dents.nim>
  - <https://github.com/c-blake/cligen/commit/ebb78e9>
  - <https://github.com/c-blake/cligen/commit/2948a0d>
  - <https://github.com/c-blake/cligen/commit/7559cff>
  - <https://github.com/c-blake/cligen/commit/0781e36>
  - <https://github.com/c-blake/cligen/issues?q=dents>
  - <https://github.com/c-blake/cligen/issues/156>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/c-blake/cligen`) · [data/wave14/enrich/raw/github_com_c_blake_cligen.json](../../../data/wave14/enrich/raw/github_com_c_blake_cligen.json) (enrichment confidence 0.65)

</details>
