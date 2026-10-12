# hop

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier D** (directional, no numbers) · Study only · `Zig` · `no license` · 🔴 abandoned

> Uncompressed, read-only archive format and CLI in Zig with an indexed footer, for pulling single files faster than tar or unzip.

| | |
|---|---|
| **Beats** | unzip and tar (reading individual files) |
| **Claimed result** | 25x faster than unzip and 10x faster than tar at reading individual files (uncompressed). |
| **Workload** | Reading individual files out of an uncompressed archive of the tigerbeetle repository. |
| **Metric** | latency |
| **Hardware** | macOS 12 (M1X) and an Ubuntu AMD64 server (CPU model not stated) |
| **Adoption** | 359 stars |
| **Last commit** | 2021-11-10 |
| **Links** | [repository](https://github.com/Jarred-Sumner/hop) · [benchmark](https://github.com/Jarred-Sumner/hop) |

## Verdict

The author's README screenshots (macOS 12 on an M1-class Mac, plus an unnamed Ubuntu AMD64 server) show hop printing one file from an uncompressed archive of the tigerbeetle repo about 25x faster than unzip and 10x faster than tar; build flags (Makefile uses -Drelease-fast) and the exact commands are not published beyond the images. Open issue #3 points out that these runs take a few milliseconds each, so they mainly measure startup, not archive access.

## Use it when

- Reading a handful of files out of a big bundle of many small files (node_modules-style trees) where tar's sequential scan dominates.
- Studying a minimal indexed-archive layout (content first, hash-indexed footer, zero-copy decode, sendfile/copy_file_range) before designing your own.
- Trusted, locally produced archives under 4 GB where compression, checksums and symlinks are not needed.

## Skip it when

- Any production or redistribution use: the repo has no license file, so treat it as read-only reference code.
- Untrusted archives: no checksums, no bounds or path validation on entry names (extract passes stored names straight to createFile/makePath, so '../' names can write outside the target directory), and footer structs are cast without alignment checks (open issue #1).
- Archives over 4 GB, or trees that rely on symlinks, empty directories, permissions or mtimes (stored but not restored on extract).
- When you need compression, appends or a maintained tool: indexed formats such as asar, or zip with stored entries, are the fairer comparisons; the code targets a 2021 pre-0.9 Zig and has had no commits since 2021-11-10.

## How it is fast

The footer holds a table of packed File structs plus an array of 32-bit Wyhash hashes of each path, so a lookup reads the header, preads the footer, scans the hash array and sends the file's byte range to stdout with sendfile; tar has to walk entries sequentially. The footer is decoded with almost no work: packed-struct arrays are cast straight from the read buffer (std.mem.bytesAsSlice). Extraction and archiving copy data with copy_file_range. The source does not support the README's 'sorted, so faster lookup' line: the hash array is searched linearly (std.mem.indexOfScalar), not by binary search.

## Compared with alternatives

None of the siblings is an archive format; ptar is the one closest in spirit (it parallelizes creating plain tar archives). Pick hop only to study an indexed single-file read path; for faster tar creation use ptar, and for copying whole trees fcp or wcp.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | libc (build.zig links it); Zig standard library |
| **Minimum toolchain** | Zig of late 2021 (pre-0.9 std API: \*std.mem.Allocator, std.build.Builder, standardReleaseOptions); does not build on current Zig without porting |
| **Platforms** | Linux x86-64 and macOS x86-64/aarch64 (Makefile release targets); Windows not documented |
| **Thread safety** | not applicable (single-threaded CLI) |
| **Drop-in for the baseline** | no |

## Gotchas

- Single-file lookup matches only the 32-bit Wyhash of the path and never compares the name, so two paths with the same hash return the wrong file's bytes.
- Archiving calls copy_file_range once per file and records whatever count it returns, without looping on short copies, and never closes the input files (it raises RLIMIT_NOFILE to the hard limit to cope).
- Extraction does not close output files and does not restore the stored chmod or mtime; the .hop file itself is chmodded 0777 and starts with a '#!/usr/bin/env hop' shebang.
- Open issue #3 says the README benchmarks run in the single-millisecond range, where hyperfine warns 'Command took less than 5 milliseconds, results may be inaccurate', so the 25x/10x figures mostly measure process startup.

## Known shortcomings

- Measurement flaw: open issue 3 says the README runs take single-digit milliseconds and hyperfine warns '&lt;5 ms, results may be inaccurate', so the 25x and 10x figures are mostly process startup. Code issues: lookup matches a 32-bit Wyhash only with no name compare (a collision returns the wrong file); one copy_file_range call per file with no short-copy loop; no '../' path check on extract; the README's 'sorted' lookup is really a linear indexOfScalar. No license; all 21 commits are from 2021-11-10 on pre-0.9 Zig.

## Caveats and trade-offs

No license file (LICENSE, LICENSE.md, LICENSE.txt all 404), so reference only. Benchmarks are screenshots only, with no script, flags or server CPU model. The author says it was written in about 3 hours with no tests and no checksums (unsafe for untrusted data), ignores symlinks, and is limited to 4 GB. HN commenters say the right baseline is an indexed archive such as asar, not tar or unzip. It is an archive format, which sits at the edge of filesystems-and-io. [retier] README runs take single-digit milliseconds (hyperfine warns '&lt;5 ms, results may be inaccurate'), so the 25x/10x figures are mostly startup (issue 3); lookup matches a 32-bit Wyhash only with no name compare; one copy_file_range per file with no short-copy loop; no '../' path check on extract; 'sorted' lookup is really linear; no license; pre-0.9 Zig, all commits from 2021-11-10.

Archive format with no compression, no checksums, 4 GB limit, read-only, single-threaded.

## Maintenance

Abandoned: all 21 commits are dated 2021-11-10, three issues remain open and there is no license, so it is reference-only and needs porting to current Zig.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now D.
- **Tier reason:** README states '25x faster than unzip and 10x faster than tar at reading individual files (uncompressed)' and shows first-party benchmark screenshots (M1X macOS, unnamed Ubuntu AMD64 server); no benchmark script, compiler flags or server CPU model, so C.
- **Retiered** C to D: Downgraded from C. The README runs take single-digit milliseconds and hyperfine warns '&lt;5 ms, results may be inaccurate' (open issue 3), so the 25x and 10x figures are mostly process startup; the lookup also matches a 32-bit Wyhash only. Kept and documented.
- **Verifier notes:** The 25x/10x headline is in the README text; the per-benchmark numbers are only in images, which I did not read. I could not see the last commit date (2021-11-10) on the page, so I left it unchanged. 359 stars confirmed; not a fork.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/Jarred-Sumner/hop>
  - <https://raw.githubusercontent.com/Jarred-Sumner/hop/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/Jarred-Sumner/hop>
  - <https://raw.githubusercontent.com/Jarred-Sumner/hop/HEAD/README.md>
  - <https://raw.githubusercontent.com/Jarred-Sumner/hop/HEAD/src/main.zig>
  - <https://raw.githubusercontent.com/Jarred-Sumner/hop/HEAD/src/schema.zig>
  - <https://raw.githubusercontent.com/Jarred-Sumner/hop/HEAD/build.zig>
  - <https://raw.githubusercontent.com/Jarred-Sumner/hop/HEAD/Makefile>
  - <https://github.com/Jarred-Sumner/hop/commits>
  - <https://github.com/Jarred-Sumner/hop/issues?q=is%3Aissue>
  - <https://github.com/Jarred-Sumner/hop/issues/3>
  - <https://github.com/Jarred-Sumner/hop/issues/1>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/jarred-sumner/hop`) · [data/wave11/enrich/raw/github_com_jarred_sumner_hop.json](../../../data/wave11/enrich/raw/github_com_jarred_sumner_hop.json) (enrichment confidence 0.7)

</details>
