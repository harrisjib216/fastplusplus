# ptar

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🔴 abandoned

> Go CLI that archives a directory tree into N independent tar files in parallel, much faster than GNU tar on parallel filesystems.

| | |
|---|---|
| **Beats** | GNU tar |
| **Claimed result** | Linux kernel source (1.5 GB, 47K files, GPFS hot page pool, no compression): gnutar 6m4s vs 64 workers 9.4 s (about 38.7x, derived from page data), 128 workers 9.9 s, 1 worker 6m33s; 10 TB 500K-file dataset: gnutar 10hr20m vs 32 workers 44m39s (about 13.9x, derived from page data), 32 workers with gzip 8hr22m. |
| **Workload** | Archive the Linux kernel source (1.5 GB, 47K files) and a 10 TB, 500K-file dataset on GPFS with hot page pool, no compression, N parallel workers writing separate valid tar files. |
| **Metric** | throughput |
| **Hardware** | GPFS with hot page pool (no CPU model) |
| **Adoption** | 15 stars |
| **Last commit** | 2019-10-31 |
| **Links** | [repository](https://github.com/zgiles/ptar) · [benchmark](https://github.com/zgiles/ptar) |

## Verdict

First-party README tables only: on GPFS with a hot page pool, archiving the 1.5 GB, 47K-file Linux kernel source took 6m4s with GNU tar vs 9.4 s with 64 workers (about 38.7x, derived from page data), and a 10 TB, 500K-file dataset took 10hr20m vs 44m39s with 32 workers (about 13.9x). No CPU, Go or GNU tar version, node count or scripts are given; the 1-worker run was slower than GNU tar.

## Use it when

- Archiving large trees (tens of thousands to millions of files) from parallel or network filesystems (GPFS, Lustre-style) where per-file latency, not bandwidth, dominates
- HPC data migration or backup where splitting the output into many tar files is acceptable or even useful (partial recovery if one file is corrupted)
- Uncompressed or lz4 archives, where the README's 10 TB run took 44m39s at 32 workers vs 10hr20m for GNU tar
- Hosts with many cores and enough filesystem concurrency to feed 32-64 workers (the kernel-source run stopped improving past 64)

## Skip it when

- You need a single archive file or a pipe to stdout; output is always N separate tar files
- Single local SSD or small trees: the 1-worker run (6m33s) was slower than GNU tar (6m4s), and nothing shows gains on local disks
- Extraction speed matters: parallel decompression is listed as not done; you untar each piece yourself
- Archives needing hard-link detection, sparse files, xattrs or ACLs: the code builds headers with Go's tar.FileInfoHeader only and does none of this
- Production-critical jobs: abandoned since 2019, no tests, and any lstat/open/read error panics the whole process

## How it is fast

Scan and archive are decoupled: one godirwalk walker (unsorted readdir) feeds paths into a 1024-slot channel, and N goroutines each lstat, open, read and append files to their own archive/tar writer. On a parallel filesystem such as GPFS the gain comes from keeping many metadata and read requests in flight at once, which serial GNU tar cannot do; there is no special I/O technique (plain os.Read with a 4 KiB buffer).

## Compared with alternatives

No catalogued sibling creates archives; fcp, wcp and uring-sync parallelize copying instead, and hop speeds up reading single files from an archive. Pick ptar when the goal is getting a huge tree on a parallel filesystem into tar files fast and N output files are acceptable.

## Integration

| | |
|---|---|
| **Form** | module (Go command-line tool, static binary via Makefile) |
| **Dependencies** | gopkg.in/alecthomas/kingpin.v2, github.com/karrick/godirwalk, github.com/pierrec/lz4 |
| **Minimum toolchain** | Go (GOPATH-era layout, no go.mod; a modern Go toolchain needs go mod init first); version not documented |
| **Platforms** | Unix-like (static CGO_ENABLED=0 build); tested only on Linux with GPFS per README |
| **Thread safety** | not applicable (CLI); each worker owns its tar writer, shared state is channels only |
| **Drop-in for the baseline** | partial - output tar files are GNU-tar readable, but the CLI and one-archive-per-run model differ from tar |

## Gotchas

- The code accepts --compression gz, not gzip (the CLI hint says gzip, which panics 'Not implemented'), and names outputs prefix.N.targz or prefix.N.tarlz4 with no dot before the compression suffix
- Entry names are the paths as walked, so an absolute input path yields absolute names inside the tar (GNU tar would strip the leading /)
- A file that disappears or is unreadable between scan and archive panics and aborts the whole run, leaving partial tar files
- Files are dealt to workers in channel order with no size balancing (TarMaxSize is declared but unused), so output files can be very uneven

## Known shortcomings

- `--compression gzip` panics 'Not implemented' (the code wants 'gz'); output names are prefix.N.targz with no dot; any lstat or read error panics the whole run; absolute input paths are stored in the tar unchanged; no hard-link, sparse or xattr handling; TarMaxSize is unused; no go.mod. Go, not C++.

## Caveats and trade-offs

First-party numbers on a parallel file system with a hot page pool; 1 worker is slower than GNU tar (6m33s vs 6m4s); no flags, versions or CPU given. Output is many separate valid tar files, not one archive, so it is not a drop-in replacement; parallel decompression not done. Last commit 2019-10-31.

Produces N independent tar files rather than one archive; Go tool, not callable from C++.

## Maintenance

Abandoned since 2019-10-31 (15 stars, 0 open issues), MIT/Expat per the README; small enough (four packages) to vendor and modernize, but treat it as a sketch rather than a hardened archiver.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README 'Sample Performance' tables give first-party wall times versus GNU tar on GPFS with no benchmark script, CPU, versions or flags; C.
- **Verifier notes:** Numbers match the README. Metadata checked: MIT/Expat stated in the README (no LICENSE file at root), 15 stars, last commit 2019-10-31 (abandoned).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** first-party README
- **Pages the verifier opened:**
  - <https://github.com/zgiles/ptar>
  - <https://github.com/zgiles/ptar/commits/master>
  - <https://raw.githubusercontent.com/zgiles/ptar/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/zgiles/ptar/HEAD/README.md>
  - <https://github.com/zgiles/ptar>
  - <https://github.com/zgiles/ptar/tree/master/pkg>
  - <https://raw.githubusercontent.com/zgiles/ptar/HEAD/Makefile>
  - <https://raw.githubusercontent.com/zgiles/ptar/HEAD/cmd/ptar/main.go>
  - <https://raw.githubusercontent.com/zgiles/ptar/HEAD/pkg/ptar/ptar.go>
  - <https://raw.githubusercontent.com/zgiles/ptar/HEAD/pkg/scanner/scanner.go>
  - <https://raw.githubusercontent.com/zgiles/ptar/HEAD/pkg/index/index.go>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/zgiles/ptar`) · [data/wave11/enrich/raw/github_com_zgiles_ptar.json](../../../data/wave11/enrich/raw/github_com_zgiles_ptar.json) (enrichment confidence 0.7)

</details>
