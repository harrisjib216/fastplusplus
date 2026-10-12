# pixz

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-2-Clause` · 🟡 stale

> Parallel, block-indexed xz compressor CLI; roughly ties multi-threaded xz on speed, adds random access into .tpxz tarballs.

| | |
|---|---|
| **Beats** | xz (XZ Utils), run multi-threaded by pRDS with the same core count as pixz (xz -zcT&lt;cores&gt; -6 to compress, xz -cdT&lt;cores&gt; to decompress) |
| **Claimed result** | pRDS README benchmark table: pixz write 443 s, read 63 s, size 805 MB versus multi-threaded xz write 469 s, read 64 s, size 795 MB (pixz about 1.06x faster to compress and about 1.02x faster to decompress, output about 1.3% larger, derived from page data). Other xz-format rows: 7z (-mmt) 580 s write, 83 s read, 741 MB; R native xzfile 2626 s write, 105 s read, 772 MB (pixz about 5.9x faster than R's built-in single-threaded xz, but multi-threaded xz itself is about 5.6x faster than R native, derived from page data, so that gap is threading, not pixz). R native uncompressed write and read take 99 s and 42 s, which bounds the read rows. |
| **Workload** | Write and read an R object holding a 3 GB CSV of about 17 million tweets through the R package pRDS, which pipes R's serialization stream into external compressors at default levels: pixz -tp&lt;cores&gt; -6 versus xz -zcT&lt;cores&gt; -6 for writing, pixz -dp&lt;cores&gt; versus xz -cdT&lt;cores&gt; for reading (cores = mc.cores option, or detectCores()/2 when unset), on a 4-core, 8-thread i7 Mac. Benchmark committed 2020-06-02. |
| **Metric** | throughput |
| **Hardware** | i7 Mac, 4 cores / 8 threads (exact CPU model not stated) |
| **Adoption** | 795 stars, 66 forks |
| **Last commit** | 2025-03-08 |
| **Links** | [repository](https://github.com/vasi/pixz) · [benchmark](https://github.com/retrography/pRDS) |

## Verdict

The only measurement is one informal third-party run in the pRDS R package's README (2020): writing and reading an R object of about 17 million tweets (3 GB CSV) on a 4-core/8-thread i7 Mac, pixz -tp&lt;cores&gt; -6 took 443 s to write and 63 s to read versus 469 s and 64 s for xz -zcT&lt;cores&gt; -6 at the same thread count, about 1.06x faster compression with 805 MB versus 795 MB output; reads go through R's deserializer from a pipe, so the read rows are R-bound, and no tool versions or repeats are given.

## Use it when

- Large tarballs (backups, datasets, build artifacts) that must stay in .xz format but where you later need to list members or pull out single files quickly
- Systems with XZ Utils older than 5.4, which cannot decompress with multiple threads, or older than 5.6, where xz is single-threaded unless given -T
- Pipelines that already use 'tar -I' and want multi-core LZMA2 at xz's ratio without changing the archive format readers expect
- Multi-gigabyte single files where parallel decompression of an .xz you produce yourself matters

## Skip it when

- You already run XZ Utils 5.4+ with -T: in the only third-party run found (pRDS, 3 GB tweet CSV, 4-core i7 Mac) pixz -6 was 443 s versus 469 s for xz -T at equal threads, with 1.3% larger output, a gap one informal run cannot separate from noise
- You need byte-exact round trips through plain 'xz -d' of tar input: in tar mode the file index is written as an extra LZMA2 block inside the same stream, so xz -d emits it as trailing bytes (consistent with open issue #65, where 'pixz -0 | xz -d' produced 3.9 MB more than the 4.38 GB input); use -t
- Speed matters more than the .xz format: catalogued siblings such as bzip3, libbsc, Kanzi or lrzip compress several times faster than xz in their own runs
- Memory-constrained hosts: about ceil(1.3N+1) blocks are in flight plus one LZMA2 coder per thread, and the out-of-memory issue #44 and 'Error creating block encoder' #97 are open
- You need an actively released tool: the last release is 1.0.7 (2020-07-26); later commits (to 2025-03-08) are unreleased and 33 issues are open, including an unresolved decompression deadlock (#35) and a 'stream footer' failure on a 3.1 TiB file (#102)

## How it is fast

A pthread pipeline: one reader thread cuts input into blocks of 2x the LZMA2 dictionary size (16 MiB at -6, 128 MiB at -9; tunable with -f), N worker threads run liblzma's block encoder or decoder on separate blocks, and the main thread writes them back in sequence order. Because every block header carries its sizes and the xz index lists them, decompression can also be split across threads, and the tar file index lets extraction seek straight to the needed blocks. The compression itself is plain liblzma at the chosen preset, so per-core speed is xz's.

## Compared with alternatives

Pick pixz when you must emit .xz and want random access to tarball members; for raw speed in the LZMA2 family Fast LZMA2 reports 20-100% faster encoding than 7-Zip's LZMA2 at high levels, and if the format is free, bzip3, libbsc, Kanzi or lrzip beat xz outright in their catalogued runs, while pigz is the analogous tool for gzip.

## Integration

| | |
|---|---|
| **Form** | command-line program (autotools build); no library API |
| **Dependencies** | liblzma 4.999.9beta-212 or later, libarchive 2.8 or later, pthreads, libm; AsciiDoc only for the man page (can be built without since 1.0.7) |
| **Minimum toolchain** | C99 compiler (AC_PROG_CC_STDC), autoconf 2.68+ and pkg-config when building from git |
| **Platforms** | Linux (glibc and musl), macOS, BSD-style endian headers handled; Windows build fixes (seekability, CPU count) are in unreleased 2023 commits |
| **Thread safety** | not applicable (standalone process); internally one reader, N coder threads (all cores via sched_getaffinity or sysconf, cap with -p) and one writer |
| **Drop-in for the baseline** | partial: output is a valid .xz stream that xz can decompress and 'tar -Ipixz' works, but CLI flags and default file naming differ from xz and tar-mode output carries an extra index block |

## Gotchas

- Source finding: when given an input file and an output path, src/pixz.c opens the output with open(opath, O_CREAT | O_WRONLY, mode) and no O_TRUNC (no ftruncate anywhere), so writing over an existing longer file leaves its old tail after the new data: a corrupt .xz on compression, silently extra bytes on 'pixz -d in.xz out' decompression. Shell redirection and stdin input (fopen 'w') are not affected; delete the target first.
- Tar detection is automatic and changes the payload: in tar mode an index block is appended and pixz -d verifies and filters it with a heuristic ('File index heuristic failed, use -t flag'); open issue #80 asks to document that payloads may be modified. Use -t for non-tar data.
- The README's two speed arguments are dated: xz 5.4.0 (2022-12-13) added a threaded decompressor for multi-block files with sizes in block headers, and xz 5.6.0 NEWS lists multithreaded mode as the default, so the remaining distinctive feature is the tarball index.
- Parallel decompression only helps on multi-block files: an .xz written by single-threaded xz is one block and decodes on one core; issue #71 reports idle cores during decompression of a 13 GB file on a 16-thread Ryzen.

## Known shortcomings

- pRDS README (0-star repo, one informal run): the baseline is multi-threaded xz (-zcT&lt;cores&gt;), not single-threaded as the record said, so pixz is only about 6% faster (443 vs 469 s); read rows are limited by R deserialization. Filed under compression-and-encoding/general-lossless.
- Enricher: src/pixz.c opens the named output with O_CREAT|O_WRONLY and no O_TRUNC, so overwriting a longer existing file leaves a stale tail (corrupt .xz, or silent extra bytes on -d); tar mode stores the file index as an extra LZMA2 block in the same stream, so plain xz -d emits trailing bytes (open #65). The README's speed arguments predate xz 5.4.0's threaded decoder and 5.6.0's multithreaded default; last release 1.0.7 (2020), open deadlock #35. Not clearly faster than xz -T; the main value is the tarball index.

## Caveats and trade-offs

Weak evidence: one loosely controlled run by a third party in an obscure R package (pRDS, GPL-2.0, 0 stars; the pRDS author says 'not in an entirely scientific manner', 'loosely controlled environment', and that four tools did not work as intended on the machine), no tool versions, no flags, no CPU model, no repeat runs. pRDS's command table (R/zzz.R) runs xz as 'xz -zcT# -%' and 'xz -cdT#' and pixz as 'pixz -tp# -%' and 'pixz -dp#' with the same core count, so the xz row is multi-threaded xz, not single-threaded: the result is pixz versus xz -T at equal threads, a 6% compression gap that a single run cannot separate from noise. Reads go through R's deserializer from a pipe (uncompressed read alone takes 42 s), so the 63 s versus 64 s read rows are R-bound and say little about pixz's parallel decompression; the benchmark predates xz 5.4's multi-threaded decompression. The pixz README makes no speed numbers; its claims are that it parallelizes decompression, indexes tarballs for random access, and defaults to all cores while xz defaults to one (modern xz has -T and -T0, so that is a default difference). No stronger public pixz-versus-xz measurement was found (two WebSearch queries returned only README mirrors). Not clearly faster than multi-threaded xz; its distinct value is the block index for random access to tarball members.

Splits input into independent xz blocks (loses some compression ratio versus one large block, 805 MB versus 795 MB in the table above), adds a tarball index for fast listing and single-file extraction, output is a normal .xz stream with an added index; needs libarchive and liblzma; flags differ from xz (-z, -c, -f, -l, -q, -t mean different things).

## Maintenance

Stale but not abandoned: last release 1.0.7 in 2020, sporadic unreleased commits through 2025-03-08, 33 open issues; BSD-2-Clause and packaged by distributions (Fedora and openSUSE packages appear in search results), so usable as a CLI, but treat it as an indexing tool rather than a speed upgrade over modern xz -T.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The only numbers are one informal third-party run in the pRDS README (i7 Mac, no CPU model, no tool versions, no repeats, author calls it 'not in an entirely scientific manner'); pRDS is not a well-known benchmark suite and pixz's own repo has no benchmark, so this is numbers without methodology, tier C.
- **Verifier notes:** Numbers match the pRDS README exactly and metadata checks out (BSD-2-Clause, 795 stars, 66 forks, not archived, last commit 2025-03-08, stale). The record's caveat that the xz row might be single-threaded was wrong: pRDS passes -T&lt;cores&gt; to xz, so record the shortcoming as 'about 6% faster than multi-threaded xz in one informal third-party run; not clearly faster; read rows bound by R deserialization'. Judged against general-lossless's xz baseline.
- **Fields the verifier corrected:** `baseline`, `workload`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** pRDS README (verifier); enricher code reading
- **Pages the verifier opened:**
  - <https://github.com/retrography/pRDS>
  - <https://raw.githubusercontent.com/retrography/pRDS/HEAD/README.md>
  - <https://github.com/retrography/pRDS/tree/master/R>
  - <https://raw.githubusercontent.com/retrography/pRDS/HEAD/R/parallelRDS.R>
  - <https://raw.githubusercontent.com/retrography/pRDS/HEAD/R/zzz.R>
  - <https://github.com/retrography/pRDS/commits>
  - <https://github.com/vasi/pixz>
  - <https://github.com/vasi/pixz/commits>
  - <https://raw.githubusercontent.com/vasi/pixz/HEAD/README.md>
  - <https://raw.githubusercontent.com/vasi/pixz/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/vasi/pixz>
  - <https://github.com/vasi/pixz/commits>
  - <https://github.com/vasi/pixz/issues>
  - <https://github.com/vasi/pixz/issues/35>
  - <https://github.com/vasi/pixz/issues/65>
  - <https://github.com/vasi/pixz/issues/71>
  - <https://github.com/vasi/pixz/issues/80>
  - <https://github.com/vasi/pixz/issues/102>
  - <https://github.com/vasi/pixz/issues?q=is%3Aissue+truncate+OR+O_TRUNC+OR+overwrite+OR+existing>
  - <https://raw.githubusercontent.com/vasi/pixz/HEAD/README.md>
  - <https://raw.githubusercontent.com/vasi/pixz/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/vasi/pixz/HEAD/NEWS>
  - <https://raw.githubusercontent.com/vasi/pixz/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/vasi/pixz/HEAD/src/pixz.h>
  - <https://raw.githubusercontent.com/vasi/pixz/HEAD/src/pixz.c>
  - <https://raw.githubusercontent.com/vasi/pixz/HEAD/src/common.c>
  - <https://raw.githubusercontent.com/vasi/pixz/HEAD/src/write.c>
  - <https://raw.githubusercontent.com/vasi/pixz/HEAD/src/read.c>
  - <https://raw.githubusercontent.com/vasi/pixz/HEAD/src/list.c>
  - <https://raw.githubusercontent.com/vasi/pixz/HEAD/src/cpu.c>
  - <https://raw.githubusercontent.com/vasi/pixz/HEAD/src/Makefile.am>
  - <https://raw.githubusercontent.com/retrography/pRDS/HEAD/README.md>
  - <https://raw.githubusercontent.com/retrography/pRDS/HEAD/R/zzz.R>
  - <https://raw.githubusercontent.com/retrography/pRDS/HEAD/R/parallelRDS.R>
  - <https://raw.githubusercontent.com/tukaani-project/xz/HEAD/NEWS>
  - https://www.linuxlinks.com/best-linux-multi-core-compression-tools/3/ (EGRESS_BLOCKED)
  - WebSearch: pixz vs "xz -T" benchmark decompression (results: README mirrors, bugzilla.redhat.com 1260911, build.openbuildservice.org pixz)
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/vasi/pixz`) · [data/wave1/enrich/raw/github_com_vasi_pixz.json](../../../data/wave1/enrich/raw/github_com_vasi_pixz.json) (enrichment confidence 0.6)

</details>
