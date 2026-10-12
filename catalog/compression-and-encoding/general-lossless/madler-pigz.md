# pigz

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `Zlib` · 🔴 abandoned

> Multithreaded gzip/zlib/zip compressor by zlib's co-author; beats single-threaded GNU gzip on multicore machines.

| | |
|---|---|
| **Beats** | gzip |
| **Claimed result** | pigzbench README table, decompression speed (MB/s): pigz-Sys 306, pigz-CF 307, pigz-ng 361, gzip 189, pbzip2 448, zstd 528; pigz with system zlib is about 1.6x gzip (derived from page data). Compression appears only in graphs (approximate, read from silesia_speed_threads.png and silesia_speed_size.png): at 1 thread pigz with system zlib plots at about the same speed as gzip at each level; at 12 threads pigz-System level 3 reaches roughly 490 MB/s vs gzip level 3 at roughly 65 MB/s, and README text says 'All versions of pigz outperform the system's single threaded gzip'. |
| **Workload** | Third-party zlib-ng/pigzbench: Silesia corpus (and NIfTI brain imaging data), 12-core AMD Ryzen 3900X, comparing pigz built with system zlib, Cloudflare zlib and zlib-ng against gzip, pbzip2 and zstd. |
| **Metric** | throughput |
| **Hardware** | 12-core (24-thread) AMD Ryzen 3900X for the thread-scaling graph; the README does not say which machine produced the decompression table. |
| **Compiler and flags** | Not stated; a_compile.py builds pigz against madler/zlib, cloudflare/zlib and zlib-ng (develop, -DZLIB_COMPAT=ON) with CMake defaults. |
| **Adoption** | 3.0k stars; widely packaged parallel gzip |
| **Last commit** | 2023-08-20 |
| **Links** | [repository](https://github.com/madler/pigz) · [benchmark](https://github.com/zlib-ng/pigzbench) |

## Verdict

Third-party zlib-ng/pigzbench (Python scripts, CMake-default builds, compiler and flags not stated) on a 12-core AMD Ryzen 3900X over the Silesia corpus: decompression of identical .gz data at 306 MB/s for pigz with system zlib vs 189 MB/s for gzip (about 1.6x, derived from page data), 361 MB/s with zlib-ng. Compression results are in graphs only: at 1 thread pigz and gzip plot at about the same speed, and the multicore gain comes from threads (roughly 490 vs 65 MB/s at level 3 with 12 threads, read from the graph).

## Use it when

- Compressing large files or streams to .gz on a multicore box where the output must stay plain gzip for downstream tools (NIfTI .nii.gz, log archives, tarballs, initramfs).
- Shell pipelines (tar | pigz) where gzip -6 is the bottleneck and switching to zstd is not allowed.
- Building against a faster zlib (zlib-ng in compat mode or Cloudflare zlib) to stack a per-core speedup on top of the thread scaling.
- Rsync-friendly archives (-R) or random-access/damage-tolerant gzip (-i) produced at multicore speed.
- Maximum-ratio gzip output via -11 (bundled zopfli) where compression time does not matter.

## Skip it when

- Single-core or -p 1 runs: compression speed is then the same as gzip on the same zlib (pigzbench thread-scaling graph), so there is no gain.
- Decompression-heavy workloads: gzip inflate cannot be split, so pigz only reaches about 1.6x gzip (306 vs 189 MB/s); Rapidgzip or a zlib-ng/libdeflate-backed decoder goes much further.
- In-process use from C/C++: there is no library interface; link zlib-ng, libdeflate or ISA-L instead.
- Native Windows builds: the code targets Unix-style systems with pthreads (Windows/CMake support is the open issue #62 and a to-do in pigz.c).
- When the format is free to change: zstd (pzstd or zstd -T) beats it on both speed and ratio in the same pigzbench graphs.

## How it is fast

Input is cut into 128 KiB chunks (-b) that worker threads deflate in parallel, each primed with the previous chunk's last 32 KiB via deflateSetDictionary() so the ratio stays close to single-threaded deflate; chunks end on a byte boundary with Z_SYNC_FLUSH and a single writer thread concatenates them in order. Per-chunk CRC-32/Adler-32 values are computed in parallel and merged with crc32_combine()/adler32_combine(). Decompression stays single-threaded inflate, but separate read, write and check-value threads overlap I/O and checksumming with it.

## Compared with alternatives

Pick pigz when you need multithreaded compression that writes plain gzip from the command line; pigzpp claims about 2.1x over pigz 2.6 at the same level but is younger and less proven, Rapidgzip is the choice for fast parallel gzip decompression, and zlib-ng, libdeflate or ISA-L are the in-process library options (and zlib-ng can be linked under pigz).

## Integration

| | |
|---|---|
| **Form** | source-drop (single CLI executable built with make; widely packaged by distributions) |
| **Dependencies** | zlib 1.2.3+ (1.2.6+ recommended), POSIX pthreads, libm; bundled zopfli source for -11 |
| **Minimum toolchain** | not documented; the Makefile uses gcc -O3 (use gmake on Solaris) |
| **Platforms** | Unix-style systems with zlib and pthreads (README); no official Windows build |
| **Thread safety** | not applicable (a standalone program); internally uses its own yarn.c pthread wrapper |
| **Drop-in for the baseline** | partial: a CLI drop-in for gzip (same flags, standard .gz output, unpigz link), but output bytes differ from gzip's and level 3 and below are not identical between threaded and unthreaded runs |

## Gotchas

- Each 128 KiB chunk adds about 4-5 bytes (Z_SYNC_FLUSH marker), and -i (independent blocks) costs more ratio because the 32 KiB dictionary is dropped.
- Byte-identical output across thread counts needs zlib 1.2.4+ and level 4 or higher; levels 1-3 differ by thread count.
- Open issue #116 (Feb 2024): all threads hung on a futex in a 'cpio | pigz' dracut pipeline, with no maintainer response.
- README header says 'pigz 2.8 (19 Aug 2022)' while pigz.c says 19 Aug 2023; the 2023 date matches the commit history.

## Known shortcomings

- Raised C to B on zlib-ng's pigzbench (17 stars; C defensible): decompression pigz-System 306 vs gzip 189 MB/s comes from zlib inflate plus separate I/O and CRC threads, while 1-thread pigz-System compression plots the same as gzip, so the compression gain is multithreading only. Zlib license; last commit 2023-08-20.
- No gain at -p 1 (the only gain is multithreading) and decompression is single-thread inflate at about 1.6x gzip (306 vs 189 MB/s); no library API (issue #50); Unix-only (issue #62); open issue #116, all threads hang on a futex in 'cpio | pigz' (dracut), no reply. The README dates 2.8 to 2022 while pigz.c and the commits say 2023-08-19/20.

## Caveats and trade-offs

No own-code single-thread compression win: the compression gain over gzip comes from multithreading (at 1 thread pigz-System and gzip plot together), and the larger gains in the table come from the zlib backend (zlib-ng, Cloudflare), which the catalog lists separately. Decompression gain over gzip (306 vs 189 MB/s with the same system zlib) is real but comes from pigz's zlib inflate plus separate read/write/check threads, not a new algorithm. Compiler and flags not stated; compression numbers only in graphs. Maintenance 'abandoned' by the 3-year rule (last commit 2023-08-20, v2.8). pigzbench is a port of neurolabusc/pigz-bench-python (its graph links point there).

Parallel gzip using multiple cores; output is standard gzip but block boundaries cost a little ratio; decompression is only partly parallel; needs zlib 1.2.3+ and pthreads.

## Maintenance

No commits since v2.8 on 2023-08-20 (abandoned by the 3-year rule, though widely packaged and stable); zlib-licensed and a few C files, so easy to vendor or rebuild against zlib-ng.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C: zlib-ng/pigzbench is an independent third-party harness (public Python scripts a_compile.py, b_speed_threads.py, c_decompress.py, d_speed_size.py; not by the pigz author) on a named CPU (12-core AMD Ryzen 3900X) that compares pigz with system zlib against gzip; compiler and flags are not stated (CMake defaults in a_compile.py), so not A. It is a small repo (17 stars), so the 'independent measurement' reading of B is the generous one; C is defensible if B requires a well-known suite.
- **Verifier notes:** Per catalog rule: pigz judged on pigzbench; it carries a multithreading win only for compression (no own-code single-thread win) and a modest pipelining win for decompression; zlib-ng/libdeflate wins belong to those entries. Metadata OK: zlib license (SPDX Zlib), 3.0k stars, not archived, last commit 2023-08-20.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/madler/pigz>
  - <https://github.com/madler/pigz/commits>
  - <https://raw.githubusercontent.com/madler/pigz/HEAD/README>
  - <https://github.com/zlib-ng/pigzbench>
  - <https://raw.githubusercontent.com/zlib-ng/pigzbench/HEAD/README.MD>
  - <https://raw.githubusercontent.com/zlib-ng/pigzbench/HEAD/a_compile.py>
  - <https://raw.githubusercontent.com/zlib-ng/pigzbench/HEAD/silesia_speed_threads.png>
  - <https://raw.githubusercontent.com/zlib-ng/pigzbench/HEAD/silesia_speed_size.png>
- **Sources the enricher read:**
  - <https://github.com/madler/pigz>
  - <https://raw.githubusercontent.com/madler/pigz/HEAD/README>
  - <https://raw.githubusercontent.com/madler/pigz/HEAD/pigz.c>
  - <https://raw.githubusercontent.com/madler/pigz/HEAD/Makefile>
  - <https://github.com/madler/pigz/commits>
  - <https://github.com/madler/pigz/issues>
  - <https://github.com/madler/pigz/issues/116>
  - <https://raw.githubusercontent.com/zlib-ng/pigzbench/HEAD/README.MD>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/madler/pigz`) · [data/wave9/enrich/raw/github_com_madler_pigz.json](../../../data/wave9/enrich/raw/github_com_madler_pigz.json) (enrichment confidence 0.8)

</details>
