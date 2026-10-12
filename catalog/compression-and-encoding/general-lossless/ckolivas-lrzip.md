# lrzip

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `GPL-2.0` · 🟢 active

> Command-line compressor that removes long-distance duplicates (rzip) before multithreaded LZMA; beats xz/7z on large redundant files.

| | |
|---|---|
| **Beats** | xz and 7z (LZMA), plus bzip2 and gzip |
| **Claimed result** | linux-2.6.37.tar: xz 63,291,156 bytes (14.7%), compress 4m02s, decompress 8.7s; 7z 63,636,839 (14.8%), 2m28s, 6.6s; lrzip default 64,561,485 (14.9%), 1m12s, 4.3s; lrzip -l (LZO) 137,515,997 (31.9%), 14s, 2.7s; gzip 94,512,561 (21.9%), 17s, 4.0s. Six kernel trees: 7z 344,088,002 (14.5%), 17m26s compress, 1m22s decompress; lrzip 104,874,109 (4.4%), 11m37s, 56s. 10GB VM image: xz 2,272,322,208 (21.2%), 50m58s; 7z 2,242,897,134 (20.9%), 26m36s; lrzip 1,372,218,189 (12.8%), 10m23s. |
| **Workload** | Compress a Linux 2.6.37 kernel tarball (430,612,480 bytes) with default options; also six consecutive kernel trees (2.37 GB). |
| **Metric** | throughput |
| **Hardware** | 3GHz quad-core Intel Core2, 8GB RAM, SSD, lrzip v0.612 (kernel tarball and 10GB VM image tables); 2.53GHz dual-core Core2, 4GB, 32-bit userspace, lrzip v0.5.1 (six-kernel-tree table); i7-3930K 3.2GHz, 32GB (10GB image vs gzip/pbzip2) |
| **Adoption** | 704 stars |
| **Last commit** | 2026-09-21 |
| **Links** | [repository](https://github.com/ckolivas/lrzip) · [benchmark](https://raw.githubusercontent.com/ckolivas/lrzip/HEAD/doc/README.benchmarks) |

## Verdict

Author's own 2012 tables, no compiler or flags, run on a 3 GHz quad-core Core2 with 8 GB, lrzip 0.612: on the 431 MB Linux 2.6.37 tarball the default mode compressed in 72 s versus 242 s for xz and 148 s for 7z at about the same size (14.9% versus 14.7-14.8%), and decompressed in 4.3 s versus 8.7 s for xz; on a 10 GB VM image it took 10m23s to reach 12.8% versus xz 50m58s at 21.2% (derived from page data). These compare multithreaded lrzip with the single-threaded xz of that era on old lrzip versions; the 2026 0.7.x releases with LZMA SDK 26.02 have no published benchmarks.

## Use it when

- Archiving large files (from about 100 MB up to many GB) with redundancy far apart: VM and disk images, tarballs of several source trees or versions, backups and database dumps.
- Multi-core machines with plenty of RAM where you want 7z/xz-class ratios in less wall time, or much better ratios when long-range duplication dominates (10 GB VM image: 12.8% versus 21.2% for xz in the author's table).
- Quick space savings on big files with -l (rzip plus LZO), which the author's tables show running at about gzip speed with better ratios on redundant data.
- As a preprocessor: -n writes rzip-reduced output that another compressor can then shrink faster.

## Skip it when

- Small or medium files (under about 10-50 MB per the README) or data without long-range repeats: the rzip pass adds little and plain xz -T0 or zstd is simpler.
- You need an embeddable library, streaming or random access, or a format other tools read: lrzip is a POSIX CLI with its own format, and the README says piped stdin/stdout loses window size and ratio on files larger than about 25% of RAM.
- Memory-constrained or shared production hosts: the README says it uses all available RAM by design, LZMA may request up to 25% of total RAM, and LZMA spawns its own threads on top of -p.
- Untrusted archives on older versions: CVEs on crafted .lrz files include heap overflows and use-after-free bugs (CVE-2017-8844, CVE-2017-8846, CVE-2018-5747, CVE-2022-26291, CVE-2023-39741 in libzpaq on 0.651); fixes continue in 2026 (heap overflow in clear_buffer() fixed 2026-09-21).
- 32-bit targets or native Windows: 32-bit support was removed in 0.7.0, and an open issue (#276) reports MSYS builds failing on PRIO_MIN.

## How it is fast

The rzip stage keeps a hash table of tags computed by a rolling XOR-of-random-values hash over 31-byte windows (MINIMUM_MATCH), thinning entries by tag bit pattern as the table fills, so matches hundreds of MB to GB apart are replaced by short references before the backend runs. Because that stage shrinks the data, the much slower LZMA or ZPAQ backend has less to do, and the backend works on independent chunks in a thread per CPU. Each block is first test-compressed with LZ4 and skipped if incompressible; a 'sliding mmap' lets the window exceed RAM, at a large speed cost.

## Compared with alternatives

Pick lrzip over xz-beating siblings such as bzip3, libbsc, Kanzi or fast-lzma2 when the input is a single multi-GB file with long-distance duplication, since their windows or blocks are far smaller than lrzip's RAM-sized rzip window. For library use, streaming, or general files, zstd (with --long for long-range matching) is the safer default.

## Integration

| | |
|---|---|
| **Form** | CLI tool (standalone program; liblrzip removed in 0.650) |
| **Dependencies** | pthreads, libm, zlib, libbz2, liblzo2, liblz4 (testing only); embeds LZMA SDK 26.02 and libzpaq 7.15 |
| **Minimum toolchain** | autoconf 2.71 or newer to bootstrap, a C and C++ compiler (gcc tested; README recommends -O2 -march=native, since an unoptimized build is about 3x slower) |
| **Platforms** | 64-bit POSIX (Linux, macOS 10.5+ noted, Android build fixes); hardware AES and PCLMUL paths for encryption where the compiler supports them |
| **Thread safety** | Not applicable (standalone multithreaded process; -p sets thread count, LZMA adds its own threads) |
| **Drop-in for the baseline** | partial: lrz and lrzip -d mimic gzip-style command-line semantics, but output is .lrz, which xz, 7z and gzip cannot read |

## Gotchas

- 0.7.0 introduced a new file format and AES-256-GCM encryption; archives encrypted with the new default cannot be read by lrzip 0.6.x (use --legacy-encrypt for that), and streamed large stdio archives are also incompatible.
- -U (unlimited window) can be much slower when the file is far larger than RAM; once a file is over about 5x the window, plain LZMA can compress smaller (README FAQ).
- -p 1 gives slightly better compression than the multithreaded default, so ratio and speed figures depend on thread count.
- ZPAQ mode (-z) decompresses as slowly as it compresses (2m08s versus 4.3s for the default on the kernel tarball).

## Known shortcomings

- Tier C: all numbers are in doc/README.benchmarks dated 2012-07-07 (i7-3930K), including the 10 GB VM-image table; GPL-2.0.
- CLI only (liblrzip removed in 0.650); GPL-2.0; CVEs on crafted .lrz input (CVE-2017-8844, CVE-2017-8846, CVE-2018-5747, CVE-2022-26291, CVE-2023-39741); the 2012 benchmarks compare multithreaded 0.612 against single-thread xz, and 0.7.x (2026, LZMA SDK 26.02) is unbenchmarked; 0.7.0 changed the format and its default encryption is unreadable by 0.6.x; 32-bit dropped.

## Caveats and trade-offs

Old (Core2-era, document dated 7 July 2012) numbers in one doc file, no compiler, flags or scripts. Wall-time comparison with lrzip using all cores against xz of that era (single-threaded) and 7z. Modern multithreaded xz (-T) and zstd --long would narrow or reverse the gap. Author's own benchmark. lrzip is a file-level CLI (rzip long-range pass plus LZMA/LZO/ZPAQ backends), 64-bit only, and wins mostly on large inputs with long-distance redundancy.

Needs large RAM for long-range dedup window; wins mainly on large files with distant redundancy (hundreds of MB apart). Multithreaded across blocks, so wall-clock gains come partly from using 4 cores against single-threaded xz.

## Maintenance

Actively maintained in 2026 (0.7.3 released 2026-09-14, security and performance commits to 2026-09-21, one open issue); GPL-2.0, so use it as an external tool rather than linking it into non-GPL code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** doc/README.benchmarks is the author's own table against 7z, xz, bzip2 and gzip with CPU named but no compiler, flags or benchmark scripts, so C.
- **Verifier notes:** All claimed numbers found in doc/README.benchmarks; added the 10GB image table and dates. Metadata: GPL-2.0, 704 stars, last commit 2026-09-21 (active).
- **Fields the verifier corrected:** `hardware`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/ckolivas/lrzip>
  - <https://github.com/ckolivas/lrzip/commits>
  - <https://raw.githubusercontent.com/ckolivas/lrzip/HEAD/doc/README.benchmarks>
  - <https://raw.githubusercontent.com/ckolivas/lrzip/HEAD/COPYING>
- **Sources the enricher read:**
  - <https://github.com/ckolivas/lrzip>
  - <https://github.com/ckolivas/lrzip/commits/master>
  - <https://github.com/ckolivas/lrzip/releases>
  - <https://github.com/ckolivas/lrzip/issues>
  - <https://raw.githubusercontent.com/ckolivas/lrzip/HEAD/README.md>
  - <https://raw.githubusercontent.com/ckolivas/lrzip/HEAD/doc/README.benchmarks>
  - <https://raw.githubusercontent.com/ckolivas/lrzip/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/ckolivas/lrzip/HEAD/BUGS>
  - <https://raw.githubusercontent.com/ckolivas/lrzip/HEAD/WHATS-NEW>
  - <https://raw.githubusercontent.com/ckolivas/lrzip/HEAD/ChangeLog>
  - <https://raw.githubusercontent.com/ckolivas/lrzip/HEAD/rzip.c>
  - WebSearch: lrzip CVE heap overflow use-after-free crafted lrz file (snippets from opencve.io, bugzilla.redhat.com, blogs.gentoo.org)
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/ckolivas/lrzip`) · [data/wave9/enrich/raw/github_com_ckolivas_lrzip.json](../../../data/wave9/enrich/raw/github_com_ckolivas_lrzip.json) (enrichment confidence 0.8)

</details>
