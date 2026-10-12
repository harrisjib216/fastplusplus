# libarchive (bsdtar)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-2-Clause` · 🟢 active

> Multi-format streaming archive library behind bsdtar; matches or trails GNU tar on tar speed, wins only seek-based listing.

| | |
|---|---|
| **Beats** | GNU tar 1.19 (star 1.5a85 also run) |
| **Claimed result** | Mixed, mostly not faster. 64-bit Athlon 64 X2, tmpfs, Linux 2.6.23 tree (291 MB, best of 5): list 0.164 s versus GNU tar 0.218 s (bsdtar 1.33x faster, derived from page data); create 0.764 s versus 0.743 s (GNU tar 1.03x faster); extract 0.733 s versus 0.625 s (GNU tar 1.17x faster). 64-bit, disk, 3.2 GB in 7,447 files (best of 3): list 0.053 s versus 56.535 s (unexplained, since the script passes --seek to GNU tar); create 184.680 s versus 159.240 s (GNU tar 1.16x faster); extract 78.914 s versus 78.480 s (tie). 32-bit 1.5 GHz Athlon, drivers tree (119 MB, best of 3): list 0.167 s versus 0.161 s, create 1.329 s versus 1.223 s, extract 1.186 s versus 1.064 s (GNU tar faster in all three). 32-bit, disk, 2.1 GB (best of 3): list 0.214 s versus 0.210 s, create 182.171 s versus 174.999 s, extract 94.912 s versus 94.657 s (GNU tar marginally faster in all three). Tim Kientzle's note attributes bsdtar's list wins to lseek() skipping over entry bodies, which GNU tar also offers. The project itself only claims 'efficient'. |
| **Workload** | Jan Psota's TCP script (tcp.sh) timing bsdtar (libarchive 2.3.4), GNU tar 1.19 and star 1.5a85 creating, listing and extracting a pax-format archive; four data sets on two machines: Linux 2.6.23 source (291 MB, 23,867 files) on tmpfs, best of 5, and a 3.2 GB home directory on reiserfs disk on a 64-bit Athlon 64 X2; a 119 MB driver tree and a 2.1 GB home directory on a 32-bit Athlon, best of 3. |
| **Metric** | throughput |
| **Hardware** | AMD Athlon 64 X2 Dual Core 4200+ 2.2 GHz, 2012 MB RAM, Linux 2.6.22 (Gentoo); also a 1.5 GHz 32-bit AMD Athlon with 504 MB |
| **Compiler and flags** | gcc 4.2.2 (Gentoo), CFLAGS="-O2 -march=k8 -pipe" (64-bit machine); -march=athlon-xp -mfpmath=sse on the 32-bit machine |
| **Adoption** | 3.6k stars; ships as bsdtar, bsdcpio, bsdunzip on FreeBSD, macOS and Windows |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/libarchive/libarchive) · [benchmark](https://raw.githubusercontent.com/libarchive/libarchive/HEAD/contrib/psota-benchmark/results.txt) |

## Verdict

Jan Psota's 2007 Bug-tar post timed bsdtar 2.3.4 (libarchive 2.3.4) against GNU tar 1.19 and star 1.5a85 on pax archives (gcc 4.2.2, Athlon 64 X2 4200+ and a 1.5 GHz Athlon): GNU tar was faster or tied at create and extract on all four data sets, and bsdtar listed faster only on the two 64-bit sets (1.33x on tmpfs; the disk-set 1000x is a page-cache and seek artifact). It shows libarchive is not faster than GNU tar overall.

## Use it when

- A C or C++ program must read or write many archive and compression formats in-process through one API, with format detection on read.
- Listing or selectively extracting from large uncompressed tar files on seekable storage, where the lseek skip avoids reading entry bodies.
- Streaming archives to or from a socket, pipe or memory buffer through custom read/write callbacks, without temporary files.
- Cross-platform tooling (FreeBSD, macOS, Windows, Linux) that needs the same tar/zip behaviour everywhere; bsdtar is already the system tar on FreeBSD, macOS and Windows.

## Skip it when

- Choosing bsdtar over GNU tar for speed: in the only archived comparison GNU tar was faster or tied at create and extract on all four data sets.
- Random access into archives or in-place modification: the README says these are not directly supported and points such applications elsewhere.
- Multi-core decompression or compression of large archives: libarchive works serially (open issue #2848 asks for parallel processing; #2987 asks about parallel archive_read_data).
- Fast ZIP listing: open issue #889 reports bsdtar taking 1.843 s versus unzip 0.034 s to list a 250 MB CBZ, with a third of about 3k system calls stat'ing /etc/localtime.
- Untrusted input in a latency-sensitive service without sandboxing: parsers for many legacy formats keep producing memory-safety advisories, and open issue #1267 shows a crafted cpio file taking over 1,500 s on tmpfs.

## How it is fast

The one measured edge is listing: for regular files and disk-like block devices, archive_read_open_filename switches to an lseek()-based skip callback and power-of-two blocks of at least 64 KiB, so `bsdtar tf` on an uncompressed tar seeks past entry bodies and reads only headers. Otherwise the design is a single-pass stream through read/write callbacks, chosen for generality (tape, sockets, pipes) rather than speed; no parallel compression or decompression is built in.

## Compared with alternatives

Pick libarchive when the need is format coverage and an embeddable streaming API, not speed; for raw tar throughput on parallel file systems ptar's multi-worker creation is the measured win, and hop is the choice when fast reads of individual files from an archive matter more than tar compatibility.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (plus the bsdtar/bsdcpio/bsdcat/bsdunzip executables) |
| **Dependencies** | none required; optional zlib, bzip2, liblzma, lz4, zstd, libb2, OpenSSL or mbed TLS or Nettle (Windows CNG), libxml2 or expat (Windows XmlLite), iconv, ACL and xattr libraries, PCRE2POSIX; unused compressors are not linked into static binaries |
| **Minimum toolchain** | C compiler; CMake 3.17+ or autotools (configure); MSVC and MinGW on Windows |
| **Platforms** | Linux, FreeBSD, NetBSD, OpenBSD, DragonFly, macOS, Windows, other POSIX systems |
| **Thread safety** | No global state, but not thread-aware: an archive object needs caller locking; archive_write_disk_header() is not thread safe on POSIX (umask(0) window can create world-writable directories) and must be mutexed; the read_disk/write_disk modules use chdir(). |
| **Drop-in for the baseline** | partial: bsdtar accepts the common tar command line, but GNU-specific options differ (the 2007 run shows bsdtar 2.3.4 lacked --diff/compare), and the library is a new API rather than a replacement for GNU tar |

## Gotchas

- Harness flaw: tcp.sh runs only `sync` between repetitions and never drops the page cache, so best-of-n disk runs report warm-cache times; bsdtar's 0.053 s listing of a 3.2 GB archive (7,447 entries, about 7 microseconds per header on a 60 MB/s disk) can only come from seeking over header blocks already cached, while GNU tar's 56.5 s equals 58 MB/s, a full sequential read of an archive larger than the machine's 2,012 MB of RAM. The 1000x list gap measures caching plus whether the tool seeked, not parser speed (derived from page data).
- Harness flaw: use_times picks the 'best' repetition with plain `sort | head -1`, a string sort, so a 100.x s run beats a 9x.x s run whenever repetitions straddle 10 s or 100 s. The reported bsdtar and GNU tar rows are consistent with their minima, but star's 100.814 s extract on the 32-bit disk may not be its best run.
- Options were asymmetric: the script passes --seek to GNU tar and -no-fsync to star on every operation and nothing to bsdtar, and the 'compare' rows for bsdtar time an unsupported-option error (0.001 s) because the script does not stop on that failure.
- A FreeBSD 2006 note (WebSearch snippet only, list archive blocked) found gtar about 13% faster than bsdtar extracting /usr/ports and attributed it to bsdtar calling lchmod() on every extracted file while gtar skips no-op chmods; no newer measurement was found.

## Known shortcomings

- Kept as a not-faster entry: the 2007 script states compiler, flags and CPU (mechanically A) but bsdtar is slower than GNU tar 1.19 on create and extract for all 4 data sets and wins only list on 2 of 4; the compare row is a no-op; versions from 2007.
- Enricher: tcp.sh only runs sync and never drops the page cache, so the best-of-n disk runs are warm-cache and bsdtar's 0.053 s list of a 3.2 GB archive (about 7 us per header) comes from seeking over cached headers while GNU tar's 56.5 s is a full read at disk speed: the 1000x list gap measures caching plus seeking, not parser speed; use_times picks 'best' with a string sort, wrong when runs cross 10 s or 100 s; options are asymmetric (--seek for GNU tar, -no-fsync for star, nothing for bsdtar). Open issues: #889 (ZIP list 1.843 s vs unzip 0.034 s), #2848 (serial only), #1267 (crafted cpio over 1,500 s on tmpfs).

## Caveats and trade-offs

Not a speed claim by the project: the data is a 2007 mailing-list post by a third party (Jan Psota, Bug-tar list), archived in contrib/psota-benchmark with the TCP script (tcp.sh) beside it; the committed script sets n=3 while the first result set says best of 5. Versions are libarchive 2.3.4 and GNU tar 1.19, so the numbers are stale by almost twenty years. The 'compare' rows are invalid: Tim Kientzle's note says bsdtar does not support that operation (the script does not abort on its failure), so its 0.001 s is a no-op. bsdtar is slower than GNU tar for create and extract on all four data sets; its list win appears on the two 64-bit sets only and comes from lseek() skipping, a feature GNU tar has too; the script passes --seek to GNU tar, so the 1000x list gap on the 3.2 GB disk run is not explained by the file. Covers only uncompressed archives; compressed or tape cases are untested. Licence: COPYING is a 2-clause BSD notice for most sources, with a few files under 3-clause UC Regents, public domain or CC0/OpenSSL/Apache-2.0, all permissive. Filed so the shortcoming is recorded; libarchive is not shown to be faster than GNU tar overall.

Streaming multi-format reader and writer (tar, zip, 7z, rar, iso9660 and more), so the generality costs some create and extract speed relative to a tar-only tool. README notes thread safety depends on the platform (archive_write_disk_header needs an external mutex on POSIX).

## Maintenance

Actively maintained (3.8.x release line, 3.9.0dev on master, last commit 2026-10-06, 3.6k stars) and BSD-2-Clause, so it is safe to adopt for format coverage, but its only speed evidence is an archived 2007 third-party run on versions nearly twenty years old.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** contrib/psota-benchmark/results.txt with the public script contrib/psota-benchmark/tcp.sh states gcc 4.2.2, the Gentoo CFLAGS and the CPU models, so it is mechanically A-reproducible, but it shows libarchive not faster overall (slower create and extract on all four data sets, list faster on only two) with 2007 versions, so C is kept as a documentation entry rather than a speed win.
- **Verifier notes:** All quoted numbers match results.txt; I added the 32-bit machine sets (GNU tar faster or tied in every create, list and extract) and the 64-bit disk create/extract rows, so the list win holds on only two of four sets. Metadata verified: 3.6k stars, BSD-2-Clause COPYING, last commit 2026-10-06 (active). Keep as a documented not-faster entry: shortcomings are stale 2007 versions, slower create/extract, a no-op compare row, and a list-only win from lseek skipping.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** first-party 2007 script (verifier, not faster); enricher harness reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/libarchive/libarchive/HEAD/contrib/psota-benchmark/results.txt>
  - <https://raw.githubusercontent.com/libarchive/libarchive/HEAD/contrib/psota-benchmark/tcp.sh>
  - <https://raw.githubusercontent.com/libarchive/libarchive/HEAD/COPYING>
  - <https://github.com/libarchive/libarchive>
  - <https://github.com/libarchive/libarchive/commits/master>
  - <https://github.com/libarchive/libarchive/tree/master/contrib/psota-benchmark>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/libarchive/libarchive/HEAD/contrib/psota-benchmark/results.txt>
  - <https://raw.githubusercontent.com/libarchive/libarchive/HEAD/contrib/psota-benchmark/tcp.sh>
  - <https://raw.githubusercontent.com/libarchive/libarchive/HEAD/README.md>
  - <https://raw.githubusercontent.com/libarchive/libarchive/HEAD/COPYING>
  - <https://raw.githubusercontent.com/libarchive/libarchive/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/libarchive/libarchive/HEAD/NEWS>
  - <https://raw.githubusercontent.com/libarchive/libarchive/HEAD/libarchive/archive_read_open_filename.c>
  - <https://raw.githubusercontent.com/libarchive/libarchive/HEAD/libarchive/archive.h>
  - <https://raw.githubusercontent.com/libarchive/libarchive/HEAD/CMakeLists.txt>
  - <https://github.com/libarchive/libarchive>
  - <https://github.com/libarchive/libarchive/issues?q=is%3Aissue+performance+slow>
  - <https://github.com/libarchive/libarchive/issues/2848>
  - <https://github.com/libarchive/libarchive/issues/889>
  - <https://github.com/libarchive/libarchive/issues/1267>
  - <https://github.com/libarchive/libarchive/releases>
  - <https://github.com/libarchive/libarchive/releases/latest>
  - <https://github.com/libarchive/libarchive/security>
  - WebSearch: bsdtar vs GNU tar extraction speed benchmark libarchive slower (snippet of https://lists.freebsd.org/pipermail/cvs-all/2006-September/189494.html; page itself EGRESS_BLOCKED)
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/libarchive/libarchive`) · [data/wave1/enrich/raw/github_com_libarchive_libarchive.json](../../../data/wave1/enrich/raw/github_com_libarchive_libarchive.json) (enrichment confidence 0.75)

</details>
