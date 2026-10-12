# lbzip2 (maintained fork)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `GPL-3.0-or-later` · 🟢 active

> Maintained fork of lbzip2, a parallel bzip2-compatible compressor; single-threaded it already beats bzip2 1.0.8 by about 1.3x to 1.8x.

| | |
|---|---|
| **Beats** | bzip2 (bzip2 1.0.8) |
| **Claimed result** | lzbench 2.4: lbzip2 2.6.5 -1 compresses at 22.0 MB/s and decompresses at 62.7 MB/s versus bzip2 1.0.8 -1 at 13.5 MB/s and 41.1 MB/s (1.6x and 1.5x, derived from page data); -9: 22.4 and 47.0 versus 12.7 and 35.5 MB/s with the same output size class (ratio 25.75 for both). Fork README: about 8% faster compression and 9% faster decompression than lbzip2 2.5 (2015) on 220 MB of mixed data on an Apple M5 Max, single thread. |
| **Workload** | Silesia tar through lzbench, lbzip2 run single-threaded in bzip2 format; the tool also has a multithreaded mode. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 9555P at 3.20 GHz, single thread, performance governor, turbo disabled, Ubuntu 26.04; silesia.tar (211,947,520 bytes) |
| **Compiler and flags** | gcc 15.2.0 (lzbench 2.4 release binary lzbench24_x86_64-linux-gnu-gcc15); lzbench v2.4 Makefile OPT_FLAGS_O3: -fomit-frame-pointer -fstrict-aliasing -O3 -DNDEBUG (a few codecs use the -O2 variant); run options -eALL -t8,8 -o1c4 |
| **Adoption** | 1 star (fork); upstream kjn/lbzip2 has 156 stars and is unmaintained |
| **Last commit** | 2026-08-19 |
| **Links** | [repository](https://github.com/caius72/lbzip2) · [benchmark](https://github.com/inikep/lzbench) |

## Verdict

lzbench 2.4 (gcc 15.2.0 release binary, single thread of an AMD EPYC 9555P at 3.2 GHz, turbo off, silesia.tar) measured lbzip2 2.6.5 -1 at 22.0 MB/s compress and 62.7 MB/s decompress versus bzip2 1.0.8 -1 at 13.5 and 41.1 MB/s, and -9 at 22.4 and 47.0 versus 12.7 and 35.5 MB/s at the same 25.75% ratio (1.6-1.8x compress, 1.3-1.5x decompress, derived from page data). The fork's own README adds about 8% faster compression and 9% faster decompression over lbzip2 2.5 on an Apple M5 Max (first-party); most of the gain over bzip2 comes from upstream lbzip2's design, and lzbench's multithreaded table does not include lbzip2.

## Use it when

- You must produce or consume .bz2 files (archives, distro packages, legacy pipelines) and want them faster without changing the format.
- Multicore machines: the fork's README reports 220 MB compressing in 0.32 s on 18 cores versus 4.68 s single-threaded (Apple M5 Max), about 14.6x (derived from page data).
- Replacing bzip2 in shell pipelines or tar (tar -I lbzip2) on Linux, macOS or MSYS2.
- High levels (-9, 900k blocks) where bzip2 is slowest: lbzip2 keeps about 22 MB/s single-threaded versus 12.7 MB/s for bzip2 -9 on Silesia.

## Skip it when

- If you are free to choose the format: zstd, bzip3 or libbsc give better ratio and speed than any bzip2 implementation (bzip3 -5 reaches 22.29% and bsc -m0 23.26% on Silesia versus 25.75% for lbzip2 -9).
- In-process compression from C/C++: there is no supported library API; use libbz2 or an embeddable codec instead.
- Projects that cannot accept GPL-3.0-or-later code in the build or distribution.
- Native Win32 builds: only the MSYS2 POSIX runtime (needs msys-2.0.dll) is supported.
- Where long-term maintenance matters: the fork is one person's work since August 2026 (1 star, 0 forks); upstream kjn/lbzip2 is unmaintained.

## How it is fast

The BWT is computed with divbwt, an induced-sorting suffix-array construction from Yuta Mori's libdivsufsort lineage, instead of bzip2's comparison-based block sort, so compression speed barely changes from -1 to -9 (22.0 vs 22.4 MB/s in lzbench 2.4) where bzip2 slows down. Huffman tables are built with length-limited minimum-redundancy coding (Larmore-Hirschberg, Moffat-Katajainen) and decoded table-driven (Liddell-Moffat). The fork adds a vectorised forward MTF (SSE2/NEON), an inverse MTF done with one byte shuffle (pshufb with SSSE3, vqtbl1q_u8 on AArch64), slice-by-8 CRC32 and four rotating frequency counters. On top of that, input blocks are compressed and decompressed in parallel across worker threads.

## Compared with alternatives

Pick lbzip2 over bzip3, libbsc or zstd only when the output must stay in bzip2 format; those siblings win on ratio and speed with their own formats. Compared with pigz or Rapidgzip it is the analogous parallel tool for the .bz2 rather than .gz ecosystem.

## Integration

| | |
|---|---|
| **Form** | command-line tool (built from source with CMake; Homebrew tap caius72/lbzip2) |
| **Dependencies** | POSIX threads and POSIX runtime (fork, sigaction, sysconf); no external libraries |
| **Minimum toolchain** | C99 compiler, CMake 3.15+ |
| **Platforms** | Linux (glibc, musl), macOS on Apple Silicon, Windows via MSYS2; SIMD paths for x86-64 (SSE2; SSSE3 only when enabled at compile time) and AArch64 NEON, scalar fallback elsewhere |
| **Thread safety** | not applicable (standalone multithreaded program; thread count set with -n, capped at 1024 or 4x online CPUs) |
| **Drop-in for the baseline** | partial: drop-in for the bzip2 command line and .bz2 format, not for the libbz2 C API |

## Gotchas

- Like bzip2, it deletes the input file after compressing unless -k or -c is given.
- The SSSE3 inverse-MTF path compiles in only when the build already targets SSSE3 (-march=native or x86-64-v2); a default x86-64 build uses the slower branchy path.
- --small is accepted but ignored (main.c: 'For now --small is ignored'), so memory use is not reduced.
- Open upstream issues not listed as fixed in the fork's CHANGES.md: #35 (changes file permissions on files the user does not own), #27 (-n not working with tar) and #29 (lbzcat slower when the output file already exists).

## Known shortcomings

- Tier B on lzbench 2.4 (the maintainer ran the table; the lzbench CHANGELOG credits the integration to caius72). A maintained fork of kjn/lbzip2, which is not otherwise listed, so it stands.
- CLI only with no library API (lzbench wraps the internal encode.h/decode.h); GPL-3.0-or-later; one maintainer, 1 star. The SSSE3 inverse-MTF path is used only when built with -march=native or x86-64-v2; --small is ignored; upstream issues #35 (permissions), #27 (-n with tar) and #29 (slow lbzcat) are not covered by the fork's changelog; lzbench's multithread table omits lbzip2.

## Caveats and trade-offs

Baseline bzip2 is not in this category's list. The fork was created on 2026-08-17 from upstream commit 724352c and is one person's work (1 star). The lzbench CHANGELOG credits the lbzip2 2.6.5 integration to @caius72 (the fork author), although the table itself was run by the lzbench maintainer. Gain in the lzbench table is a single-thread comparison; most of the gain over bzip2 comes from upstream lbzip2's BWT/MTF implementation, and the fork itself adds about 8-9% over lbzip2 2.5 (first-party, Apple M5 Max). GPL-3.0-or-later.

Command line tool, output stays bzip2 compatible; real gains come from multiple threads (not shown in the lzbench multithreaded table). Not a library API; GPL-3.0.

## Maintenance

Active since August 2026 (2.6.5, last commit 2026-08-19) as the de facto maintained lbzip2 after Homebrew dropped the unmaintained upstream; GPL-3.0-or-later, CI on four platforms with 1111 tests, but a single maintainer.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now A.
- **Tier reason:** The lzbench 2.4 table (public code, gcc 15.2.0 release binary, single thread of an AMD EPYC 9555P, silesia.tar), run by the lzbench maintainer, lists lbzip2 2.6.5 -1 at 22.0 / 62.7 MB/s vs bzip2 1.0.8 -1 at 13.5 / 41.1 MB/s and -9 at 22.4 / 47.0 vs 12.7 / 35.5 MB/s; flags not on the README, so B. The fork's own README table (M5 Max, -O3, vs lbzip2 2.5) is first-party.
- **Retiered** B to A: Raised B to A for tier consistency with FastLZ (batch verdict A on the same table): the evidence is the lzbench 2.4 README table, an independent public suite (inikep/lzbench, tag v2.4) whose release binary lzbench24_x86_64-linux-gnu-gcc15 is built with gcc 15.2.0 from the public Makefile (OPT_FLAGS_O3 = -fomit-frame-pointer -fstrict-aliasing -O3 -DNDEBUG, line 147; some codecs use the -O2 variant, line 146), run single-threaded on an AMD EPYC 9555P at 3.20 GHz with -eALL -t8,8 -o1c4 on silesia.tar. Compiler, flags, CPU model and harness are all public, so the run is reproducible and meets tier A; the earlier B verdicts counted the flags as unstated because they are not repeated on the results page.
- **Verifier notes:** Numbers match the lzbench 2.4 row. On folding: upstream kjn/lbzip2 (156 stars, GPL-3.0, not archived) is not on the known list, so this maintained fork does not fold into a listed project; it is effectively the lbzip2 entry, and the orchestrator could note kjn/lbzip2 as the original. GitHub marks it as a fork of kjn/lbzip2; last commit 2026-08-19.
- **Fields the verifier corrected:** `caveats`, `compiler_and_flags`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/caius72/lbzip2>
  - <https://github.com/inikep/lzbench>
  - <https://github.com/caius72/lbzip2/commits>
  - <https://github.com/kjn/lbzip2>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/CHANGELOG>
- **Sources the enricher read:**
  - <https://github.com/caius72/lbzip2>
  - <https://github.com/caius72/lbzip2/tree/master/src>
  - <https://raw.githubusercontent.com/caius72/lbzip2/HEAD/README.md>
  - <https://raw.githubusercontent.com/caius72/lbzip2/HEAD/CHANGES.md>
  - <https://raw.githubusercontent.com/caius72/lbzip2/HEAD/NEWS>
  - <https://raw.githubusercontent.com/caius72/lbzip2/HEAD/ChangeLog>
  - <https://raw.githubusercontent.com/caius72/lbzip2/HEAD/ALGORITHM>
  - <https://raw.githubusercontent.com/caius72/lbzip2/HEAD/AUTHORS>
  - <https://raw.githubusercontent.com/caius72/lbzip2/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/caius72/lbzip2/HEAD/src/encode.h>
  - <https://raw.githubusercontent.com/caius72/lbzip2/HEAD/src/decode.h>
  - <https://raw.githubusercontent.com/caius72/lbzip2/HEAD/src/main.c>
  - <https://github.com/kjn/lbzip2/issues?q=is%3Aissue>
  - <https://github.com/kjn/lbzip2/issues/29>
  - <https://github.com/kjn/lbzip2/issues/35>
  - <https://github.com/inikep/lzbench>
  - <https://github.com/inikep/lzbench/tree/master/bwt>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/CHANGELOG>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/caius72/lbzip2`) · [data/wave9/enrich/raw/github_com_caius72_lbzip2.json](../../../data/wave9/enrich/raw/github_com_caius72_lbzip2.json) (enrichment confidence 0.75)

</details>
