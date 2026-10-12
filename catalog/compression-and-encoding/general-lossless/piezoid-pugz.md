# pugz

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Research prototype that decompresses one gzip stream of ASCII text on many threads; beats single-threaded GNU gunzip and libdeflate.

| | |
|---|---|
| **Beats** | GNU gunzip (gzip); libdeflate also compared in the paper |
| **Claimed result** | README, dual Xeon X5675: gunzip 55 MB/s vs pugz 147 MB/s with 1 thread and 251 MB/s full decompression with 24 threads (1052 MB/s when only counting lines); i7-4770: gunzip 63 MB/s vs pugz 172 MB/s (1 thread) and 376 MB/s (8 threads). Paper Table II (32 threads, FASTQ files preloaded in memory): gunzip 37 MB/s, libdeflate 118 MB/s, pugz 611 MB/s, stated as 16.5x faster than gunzip and 5.2x faster than libdeflate |
| **Workload** | Parallel decompression of gzip-compressed ASCII text files (FASTQ in the paper; 2.7 GB and 24 GB compressed files in the README), speed measured in compressed input bytes per second |
| **Metric** | throughput |
| **Hardware** | README: dual Xeon X5675 (2x 6C/12T, 32 GB) and i7-4770 (4C/8T, 16 GB); paper: 2x12-core 2.3 GHz Xeon E5-2670 v3, 512 GB RAM |
| **Compiler and flags** | Makefile: -std=c++11 -mssse3 -O3 -flto -march=native -mtune=native -g; 'make asserts=0' adds -DNDEBUG (README recommends it for maximal performance). Compiler (\$(CXX)) and version not stated. |
| **Adoption** | 124 stars; paper by Kerbiriou and Chikhi (copy in repo at paper/paper.pdf) |
| **Last commit** | 2019-08-20 |
| **Links** | [repository](https://github.com/Piezoid/pugz) · [benchmark](https://github.com/Piezoid/pugz#decompression-speed-benchmark) |

## Verdict

Peer-reviewed HiCOMB/IPDPSW 2019 paper, Table II: on three 3-7.5 GB FASTQ files preloaded into RAM on a 2x12-core Xeon E5-2670 v3, gunzip 37 MB/s, libdeflate 118 MB/s and pugz with 32 threads 611 MB/s of compressed input (16.5x and 5.2x), with output sent unordered to /dev/null and no CRC check in pugz. The README's own script runs give 55 MB/s gunzip versus 147 MB/s (1 thread) and 251 MB/s (24 threads, ordered output) on a dual Xeon X5675; compiler version not stated.

## Use it when

- Decompressing large (GB-scale) gzip FASTQ, CSV, TSV or log files that someone else produced with plain gzip, on a many-core box, when you cannot get an index or a block-parallel format.
- Order-insensitive consumers (read-level FASTQ processing, line counting): the unsynchronized path scaled to 1052 MB/s at 24 threads in the README versus 251 MB/s with ordered output.
- As a reference implementation or algorithm source for building speculative parallel inflate into your own C++ tool (MIT licence).

## Skip it when

- Any binary payload (.tar.gz, BAM, images) or text with bytes outside '\t'..'\~' (UTF-8 accents, Latin-1): unsupported by design.
- Multi-member or blocked gzip files (bgzip/BGZF, concatenated .gz members): unsupported; issue #5 open since 2019.
- Anything needing integrity: gzip CRC32 and ISIZE are never checked, so corrupted input can silently yield wrong text.
- Production pipelines: abandoned since 2019 with open crash reports (#11 'Got a context from invalid position' on Nanopore FASTQ, #13 races and mutex assertions with 64 threads on pigz-made files), and error handling is mostly assertions. rapidgzip covers the general case.
- Few cores or ordered output: with ordered stdout the README shows only 147 to 251 MB/s from 1 to 24 threads (Xeon X5675), and the library holds a section of decompressed output in memory per thread.

## How it is fast

Each thread jumps to an arbitrary bit offset and finds the next deflate block start by trying to decode at every bit position, failing fast with strict checks, then confirming by decoding five more blocks. Because the 32 KB history window before that point is unknown, the thread decodes with symbolic placeholders for unresolved back-references (16-bit symbols, compressed to 8 bits through a lookup table since text only uses bytes '\t'..'\~'); a quick sequential pass hands each chunk its predecessor's final window and a parallel pass substitutes the placeholders. The single-thread inflate loop is libdeflate's table-driven Huffman decoder, which is why one pugz thread is already about 2.7x gunzip; it also skips CRC32.

## Compared with alternatives

Pick rapidgzip over pugz for almost every use: it handles binary data, multi-member files, CRC checks and is maintained. pugz is only worth reading for the algorithm or for unordered ASCII FASTQ throughput; pigz decompresses on one thread, and libdeflate is the faster single-thread choice when the file fits in memory.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond pthreads and librt (Linux) |
| **Minimum toolchain** | C++11 compiler with SSSE3; Makefile uses -O3 -flto -march=native (compiler version not documented; issues #8-#10 were build failures fixed in 2019) |
| **Platforms** | Linux on recent x86-64 per README (SSSE3 required, -march=native binaries are not portable) |
| **Thread safety** | Internal threading only; one call decompresses one mmapped file. Issue #13 (open, 2022) reports sporadic races: assertion failures in DeflateThread::get_context(), pthread mutex owner assertion and std::system_error at 64 threads. |
| **Drop-in for the baseline** | partial — CLI resembles gunzip (writes to stdout, -t threads) but only for single-member ASCII-text gzip, with no CRC check and no library form |

## Gotchas

- Default is 1 thread; you must pass -t N, and the thread count is capped at 1 + compressed_size/2 MiB.
- Built with asserts on by default; `make asserts=0` is faster but the README warns unsupported files may then cause undefined behaviour, because most input validation is assert() (lib/input_stream.hpp, lib/deflate_decompress.hpp). libdeflate_gzip_decompress also ignores the return value of consume_header(), so a bad gzip header is not rejected there.
- The produced binary is called `gunzip`; installing it on PATH shadows GNU gunzip with a tool that lacks CRC checks and binary support.
- Input is mmapped from a regular file (no stdin streaming; source comment 'need a streaming-friendly solution').

## Known shortcomings

- Peer-reviewed numbers (HiCOMB/IPDPSW 2019, Table II: 37/118/611 MB/s) but compiler version unstated. Skips the CRC32 that gunzip computes, so not equal work. Text-only input, fork of ebiggers/libdeflate, abandoned.
- CRC32 and ISIZE are never checked. Open crash issues: #11 'Got a context from invalid position', #13 races and mutex assertions at 64 threads on pigz-made files; #12 INVALID_LITERAL core dump closed without a fix. Input checks rely on assert(), so asserts=0 gives undefined behaviour. gzip_decompress.hpp ignores the consume_header() return value. Binary is named gunzip (shadows GNU). Default 1 thread; input must be an mmapped file; x86-64 Linux with SSSE3 and -march=native only. Paper speeds use unordered output to /dev/null. Abandoned since 2019; rapidgzip supersedes it.

## Caveats and trade-offs

Prototype: may crash, or give undefined behaviour with asserts=0; blocked/multi-part gzip files and non-ASCII (binary) data are unsupported. pugz skips CRC32 verification while gunzip computes it (README: CRC would cost roughly 33%), so the comparison is not equal work. Paper speeds come from files preloaded in memory with output sent unsynchronized to /dev/null (order-insensitive, mimicking a FASTQ parser); the README 'full decompression' column keeps ordered output and scales far less (251 MB/s at 24 threads vs 1052 MB/s line counting). README speeds are compressed-input bytes per second from a wall-clock shell script (example/bigger_benchmark.sh, divides by 1024\*1024) on HIGGS.csv.gz and SRR6832872.fastq.gz. Compiler and version not stated. GitHub fork of ebiggers/libdeflate. The newer rapidgzip (already catalogued) covers the general case.

Only ASCII text files with bytes in ['\t','\~'] work (no binary, no .tar.gz); no CRC32 check (README says adding it would cost about 33%); no multi-member gzip support; standalone program, not a library; output synchronization limits the in-order speedup; needs many cores to win (1 thread: 147 vs 55 MB/s likely reflects its libdeflate-derived inflate code, per the README).

## Maintenance

Abandoned prototype (last commit 2019-08-20, open crash and race issues), MIT-licensed; usable as an algorithm reference or for unordered ASCII decompression, superseded for general use by rapidgzip.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded C to B: the README cites the peer-reviewed paper (Kerbiriou and Chikhi, HiCOMB 2019 workshop, IPDPSW 2019, pp. 209-217, doi 10.1109/IPDPSW.2019.00042), whose Table II shows gunzip 37, libdeflate 118 and pugz (32 threads) 611 MB/s on a 2x12-core Xeon E5-2670 v3. Not A: the README benchmark script (example/bigger_benchmark.sh), Makefile flags and CPU models are public, but the compiler and version are not stated (Makefile uses \$(CXX)).
- **Verifier notes:** All README and paper Table II numbers match the record; the paper does name its venue via the README citation (HiCOMB/IPDPSW 2019), so peer-review credit applies and the tier rises to B. Metadata checked: MIT, 124 stars, 11 forks, 88 commits, last commit 2019-08-20 (abandoned), GitHub fork of ebiggers/libdeflate.
- **Fields the verifier corrected:** `compiler_and_flags`, `is_fork_of`, `caveats`
- **Shortcomings recorded by:** peer-reviewed paper; peer-reviewed paper (HiCOMB/IPDPSW 2019)
- **Pages the verifier opened:**
  - <https://github.com/Piezoid/pugz>
  - <https://github.com/Piezoid/pugz/commits>
  - <https://raw.githubusercontent.com/Piezoid/pugz/HEAD/README.md>
  - <https://raw.githubusercontent.com/Piezoid/pugz/HEAD/Makefile>
  - <https://raw.githubusercontent.com/Piezoid/pugz/HEAD/example/bigger_benchmark.sh>
  - <https://raw.githubusercontent.com/Piezoid/pugz/HEAD/example/test.sh>
  - <https://raw.githubusercontent.com/Piezoid/pugz/HEAD/paper/paper.pdf>
- **Sources the enricher read:**
  - <https://github.com/Piezoid/pugz>
  - <https://raw.githubusercontent.com/Piezoid/pugz/HEAD/README.md>
  - <https://raw.githubusercontent.com/Piezoid/pugz/HEAD/Makefile>
  - <https://raw.githubusercontent.com/Piezoid/pugz/HEAD/lib/gzip_decompress.hpp>
  - <https://raw.githubusercontent.com/Piezoid/pugz/HEAD/lib/deflate_decompress.hpp>
  - <https://raw.githubusercontent.com/Piezoid/pugz/HEAD/lib/decompressor.hpp>
  - <https://raw.githubusercontent.com/Piezoid/pugz/HEAD/lib/input_stream.hpp>
  - <https://raw.githubusercontent.com/Piezoid/pugz/HEAD/lib/memory.hpp>
  - <https://raw.githubusercontent.com/Piezoid/pugz/HEAD/programs/gunzip.cpp>
  - <https://raw.githubusercontent.com/Piezoid/pugz/HEAD/paper/paper.pdf>
  - <https://github.com/Piezoid/pugz/tree/master/lib>
  - <https://github.com/Piezoid/pugz/issues?q=is%3Aissue>
  - <https://github.com/Piezoid/pugz/issues/11>
  - <https://github.com/Piezoid/pugz/issues/12>
  - <https://github.com/Piezoid/pugz/issues/13>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/piezoid/pugz`) · [data/wave9/enrich/raw/github_com_piezoid_pugz.json](../../../data/wave9/enrich/raw/github_com_piezoid_pugz.json) (enrichment confidence 0.8)

</details>
