# fclones

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟡 stale

> Parallel, device-aware Rust duplicate file finder; 4-10x shorter wall time than jdupes, fdupes and rdfind on a 316 GB SSD scan.

| | |
|---|---|
| **Beats** | jdupes / fdupes / rdfind (duplicate finders built on POSIX read) |
| **Claimed result** | SSD: fclones 0:34.59 vs rmlint 2:28.43, jdupes 5:01.91, fdupes 5:46.19, rdfind 5:53.07, yadf 0:59.32 |
| **Workload** | Find duplicates among 1,460,720 paths (316 GB) on NVMe SSD, page cache dropped before each run; second HDD benchmark of 51,370 paths. |
| **Metric** | throughput |
| **Hardware** | SSD: Dell Precision 5520, Intel Xeon E3-1505M v6 3.00GHz, 32GB RAM, NVMe, Ubuntu 20.10 kernel 5.8.0-53; HDD: Dell Precision M4600, Intel Core i7-2760QM 2.40GHz, 24GB RAM, Seagate Momentus 7200 RPM SATA, EXT4, Mint 19.3 |
| **Compiler and flags** | not stated; commands run with /usr/bin/time -v |
| **Adoption** | 3.0k stars |
| **Last commit** | 2025-03-03 |
| **Links** | [repository](https://github.com/pkolaczk/fclones) · [benchmark](https://github.com/pkolaczk/fclones/blob/HEAD/fclones/README.md) |

## Verdict

Author-run, page-cache-dropped scans of 1,460,720 paths (316 GB) on a Xeon E3-1505M v6 laptop with NVMe: fclones 0.12.1 34.59 s vs yadf 59.32 s, czkawka 2:09.00, rmlint 2:28.43, jdupes 1.18.2 5:01.91, fdupes 5:46.19, rdfind 5:53.07 (about 8.7x faster than jdupes and 10.2x than rdfind, derived from page data); SSD-run commands and build flags are not given, and jdupes' author has noted (blog post, search snippet only) that jdupes was run without -Q, so it did byte-for-byte confirmation that fclones skips. The older HDD table (fclones 0.9.1 vs jdupes 1.9 -Q, i7-2760QM, 7200 RPM disk) shows 19.45 s vs 1:18.47.

## Use it when

- Deduplicating large trees (hundreds of thousands to millions of files) on NVMe/SSD where a multi-threaded scan pays off.
- Spinning disks on Linux, where physical-offset ordering of reads helps (README HDD run: 19.45 s vs rdfind 33.70 s and jdupes 1:18.47).
- Repeated scans of the same data set: `--cache` persists file hashes keyed by inode and metadata.
- Pipelines that want a reviewable JSON/CSV report before any file is deleted, or reflink dedupe on Btrfs/XFS-style copy-on-write file systems.

## Skip it when

- When you need byte-for-byte confirmation before deletion: fclones never compares bytes and relies on a 128-bit (or wider) hash match; jdupes and fdupes confirm by default.
- As a component inside a C++ program: it is a Rust CLI/crate with no C API.
- Non-Linux platforms if you want the full speed: physical-placement ordering and page-cache drop-behind are Linux-only, and reflink is not supported on Windows.
- Data that changes under open file handles (databases) when using `--cache`, since cache validity depends on mtime and length.
- Projects that need an actively maintained tool: last commit 2025-03-03 (0.35.0 version bump), 89 open issues.

## How it is fast

A staged filter: group by size, drop same-inode hard links, then hash a small prefix (4 KiB on SSD, up to 16 KiB on HDD), then a suffix, and only then the full contents, so most non-duplicates are discarded after a few KiB of I/O. Directory walking runs in parallel on rayon scopes, and each block device gets its own random-I/O and sequential-I/O thread pools sized by detected disk type (HDD forced to 1 thread). On Linux it orders HDD reads by physical extent (FIEMAP), uses posix_fadvise RANDOM/SEQUENTIAL hints and DONTNEED drop-behind, hashes with 128-bit MetroHash by default, and keeps paths prefix-compressed to cut memory.

## Compared with alternatives

No sibling is a duplicate finder; fclones uses the same parallel-walk idea as gdu, diskus and pdu (disk usage) or bfs (traversal) but adds hashing and dedupe actions, so pick it when the job is finding identical file contents rather than sizing or listing trees.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | rayon, crossbeam, dashmap, sled, metrohash, blake3/xxhash-rust/sha2/sha3 (optional features), ignore, nix, fiemap (Linux), sysinfo and about 40 other crates |
| **Minimum toolchain** | Rust 1.74 (edition 2021) |
| **Platforms** | Linux (best, tested on Ubuntu), macOS and Windows reported to work; packaged for Snap, Homebrew, AUR, Alpine, NixOS |
| **Thread safety** | Internally multi-threaded; library-level thread-safety guarantees not documented |
| **Drop-in for the baseline** | partial — `-o fdupes` output format mimics fdupes, but the CLI and the two-step group/remove workflow differ from jdupes, fdupes and rdfind |

## Gotchas

- No byte-by-byte verification: duplicates are decided by hash equality alone (default metro 128-bit, non-cryptographic); choose `--hash-fn blake3` or sha256 if adversarial collisions matter.
- Hidden files and paths in .gitignore/.fdignore are skipped by default; pass `--no-ignore --hidden` for a full scan.
- Hard and soft links are not counted as duplicates unless `--isolate` or `--match-links`; `--match-links` with `--symbolic-links` can delete the only real copy (README warning).
- Open bug #275: an Em Space (U+2003) character is dropped from paths in the group phase; past bugs #148 (--unique listed non-unique files) and #99/#97 (--isolate counts) were fixed.

## Known shortcomings

- Fairness gap in the SSD benchmark: jdupes ran without -Q (per the jdupes author's blog, snippet only, blog blocked), so jdupes did a byte-for-byte confirm while fclones never byte-compares (hash only, metro128 by default); the SSD commands are not published. Open bug 275 (U+2003 dropped from paths). Rust, not C++.

## Caveats and trade-offs

First-party benchmark with no script or dataset published, so tier C. Version numbers date from 2021 (fclones 0.12.1). Baseline is other duplicate finders, not raw POSIX read. Not a C++ library.

Rust, not directly callable from C++; end-user tool; parallel scan and physical-offset ordering for HDD.

## Maintenance

Stale (last commit 2025-03-03, version 0.35.0) but MIT-licensed, about 3.0k stars and widely packaged; usable as an end-user tool or Rust crate, not as copyable C++ code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The fclones/README.md Benchmarks section gives first-party SSD timings (fclones 0:34.59, yadf 0:59.32, rmlint 2:28.43, jdupes 5:01.91, fdupes 5:46.19, rdfind 5:53.07) with CPU and commands stated, but no published dataset or script and no build flags, so C.
- **Verifier notes:** Numbers verified in the README table. MIT license, about 3k stars, last commit 2025-03-03 (version bump to 0.35.0), so stale is correct.
- **Fields the verifier corrected:** `hardware`
- **Shortcomings recorded by:** first-party README
- **Pages the verifier opened:**
  - <https://github.com/pkolaczk/fclones>
  - <https://github.com/pkolaczk/fclones/commits/main>
  - <https://raw.githubusercontent.com/pkolaczk/fclones/HEAD/fclones/README.md>
  - <https://raw.githubusercontent.com/pkolaczk/fclones/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/pkolaczk/fclones>
  - <https://raw.githubusercontent.com/pkolaczk/fclones/HEAD/fclones/README.md>
  - <https://raw.githubusercontent.com/pkolaczk/fclones/HEAD/fclones/Cargo.toml>
  - <https://raw.githubusercontent.com/pkolaczk/fclones/HEAD/fclones/src/device.rs>
  - <https://raw.githubusercontent.com/pkolaczk/fclones/HEAD/fclones/src/hasher.rs>
  - <https://raw.githubusercontent.com/pkolaczk/fclones/HEAD/fclones/src/file.rs>
  - <https://raw.githubusercontent.com/pkolaczk/fclones/HEAD/fclones/src/walk.rs>
  - <https://github.com/pkolaczk/fclones/tree/main/fclones/src>
  - <https://github.com/pkolaczk/fclones/issues?q=is%3Aissue+label%3Abug>
  - https://www.jodybruchon.com/2020/07/11/a-challenger-appears-fclones-fastest-duplicate-scanner-ever-its-complicated/ (EGRESS_BLOCKED; WebSearch snippet only)
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/pkolaczk/fclones`) · [data/wave11/enrich/raw/github_com_pkolaczk_fclones.json](../../../data/wave11/enrich/raw/github_com_pkolaczk_fclones.json) (enrichment confidence 0.7)

</details>
