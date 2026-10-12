# zipir (Zig streaming DEFLATE-family compression library and CLI)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig` · `MIT` · 🟢 active

> Pure-Zig streaming gzip/zlib/raw-DEFLATE/BGZF codec in fixed memory; decodes zlib and raw DEFLATE about 1.24x faster than zlib-ng.

| | |
|---|---|
| **Beats** | zlib-ng 2.3.3 (zlib and raw DEFLATE), ISA-L igzip, and bgzip with libdeflate 1.26 or zlib-ng (htslib 1.24) |
| **Claimed result** | Whole-command single-threaded times on one Ryzen 9 3950X, geometric means over files (peer time / zipir time). Decompression: on zlib and raw DEFLATE zipir is the fastest of the timed streaming tools, zlib-ng takes 1.24x its time (zlib 1.17-1.27x, raw 1.18-1.28x); only zlib-ng and the Zig std library were timed on those formats, libdeflate and ISA-L were not. gzip decompression is level with ISA-L igzip (1.01x, per file 0.81-1.25x) and zlib-ng takes 1.10-1.26x. BGZF decompression: bgzip + libdeflate is 1.07x faster than zipir, bgzip + zlib-ng takes 1.06-1.24x. Compression against zlib-ng at the same nominal level (zlib and raw DEFLATE): level 1 1.35x with 34% larger zlib-ng output, level 5 1.08x (0.93-1.23x) with 2% larger output, level 9 2.01x (1.20-3.87x) with 2% larger output. Losses: ISA-L igzip is faster on gzip compression in all three lanes (0.83x, 0.28x and 0.13x of zipir's time) with 15-22% larger output; bgzip + libdeflate is 1.04x and 1.02x faster at no larger output on BGZF compression levels 1 and 5. Presets table: zipir fast 332.8 MB/s at ratio 3.183 against zlib-ng level 2 at 148 MB/s and ratio 3.257 and ISA-L igzip level 2 at 371 MB/s and ratio 3.205, so ISA-L is about 1.1x faster than zipir fast at a matched ratio (derived from page data). Peak RSS: zipir 0.55-0.62 MiB, the C tools 1.6-5.0 MiB. |
| **Workload** | Single-threaded whole-command compression at each tool's fast, balanced and dense level (zipir 1/5/9, zlib-ng 1/5/9, ISA-L igzip 0/1/2, bgzip 1/5/9) and decompression of gzip, zlib, raw DEFLATE and BGZF: FASTQ (57.2 MB and 20.2 MB), PRIDE XML (48.0 MB), mzIdentML (1.2 MB) and Canterbury tar (2.8 MB); BGZF compression uses a BAM (76.2 MB) and a VCF (11.5 MB) in place of the FASTQ files; decompression adds Silesia tar (211.9 MB). 3 warmups and 25 interleaved rounds per batch, medians; output size reported beside compression speed; process start-up and file I/O included. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 3950X (Zen 2, AVX2, no AVX-512), Linux 7.2.7-200.fc44 (Fedora 44), schedutil governor, every batch pinned to CPU 4, machine in normal use (1-minute load average 1.1-6.6), one host, measured 2026-09-27. |
| **Compiler and flags** | zipir 0.1.2 (compression rows commit 5f25547 with uncommitted changes, decompression rows commit ff8e9e8) through Zig adapters built with Zig 0.16.0 -Doptimize=ReleaseFast -Dstrip=true -Dcpu=native, single-threaded. Peers built by tools/install.sh with GCC 16.2.1: zlib-ng 2.3.3 static via CMake CMAKE_BUILD_TYPE=Release with WITH_NATIVE_INSTRUCTIONS=ON (minigzip CLI for gzip; a C adapter over the native API compiled cc -O3 -DNDEBUG -march=native for zlib and raw DEFLATE); ISA-L igzip 2.32.1 static, CMAKE_C_FLAGS_RELEASE -O3 -DNDEBUG -march=native with nasm; libdeflate 1.26 static at -O3 -DNDEBUG -march=native; htslib 1.24 bgzip -@1 with htslib's default compiler flags, linked statically to libdeflate or to zlib-ng in compat mode. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Adoption** | 0 stars (128 commits) |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/eneskemalergin/zipir) · [benchmark](https://raw.githubusercontent.com/eneskemalergin/zipir/HEAD/bench/linux-x86-avx2/README.md) |

## Verdict

On one Ryzen 9 3950X (Zen 2, AVX2), whole-command single-threaded runs (25 interleaved rounds, medians) of zipir built with Zig 0.16.0 ReleaseFast -Dcpu=native decoded zlib and raw DEFLATE about 1.24x faster than zlib-ng 2.3.3 (GCC 16.2.1, -O3 -march=native, native-API C adapter), tied ISA-L igzip 2.32.1 on gzip decode, and lost to bgzip + libdeflate 1.26 on BGZF decode by about 1.07x. Compression against zlib-ng at the same nominal level was 1.35x (level 1, zlib-ng output 34% larger), 1.08x (level 5) and 2.01x (level 9) faster with smaller output, but ISA-L igzip was faster at every gzip lane.

## Use it when

- Zig projects that read or write gzip, zlib or raw DEFLATE and want to drop a C zlib/zlib-ng dependency without losing speed: zlib and raw DEFLATE decode measured 1.17-1.28x faster than zlib-ng 2.3.3 on 1.2-212 MB files.
- Many concurrent streams under a tight memory budget: whole-process peak RSS 0.55-0.62 MiB versus 1.6-5.0 MiB for the C tools, with one fixed workspace per stream and no hidden allocation.
- Bioinformatics pipelines that need BGZF with line-aligned blocks matching bgzip 1.24, .gzi indexes and virtual-offset seeking from Zig, at roughly bgzip + libdeflate speed (within about 7% on decode, 2-4% on levels 1 and 5 compression).
- Decoding many small zlib or raw DEFLATE arrays held in memory (mzML-style) through `SliceDecoder`, which writes straight into your buffer with a 7.7 KB workspace.
- When you want zlib-level-9-class output size at about twice zlib-ng level 9's speed (zipir dense was 1.20-3.87x faster than zlib-ng 9 with 2% smaller output in the report).

## Skip it when

- Maximum gzip compression throughput: ISA-L igzip beat zipir at every gzip lane (0.83x, 0.28x and 0.13x of zipir's time, with 15-22% larger output), and at a matched ratio ISA-L level 2 is about 1.1x faster than zipir fast.
- Whole buffers in memory where libdeflate's one-shot API is an option: libdeflate was not timed against zipir's streaming decoders, bgzip + libdeflate decodes BGZF about 1.07x faster, and libdeflate level 7 compresses faster than zipir dense at the same ratio (54 vs 37.5 MB/s, from a separate run).
- Windows targets (unsupported), or ARM64 where speed matters: only the CRC-32 kernel is accelerated there and no ARM64 or macOS speed was measured.
- Code that needs the zlib C API, levels 0-9, preset dictionaries, multithreaded compression, or tar extraction; none of these exist.
- Projects that need a mature, widely used codec: 0 stars, first public release 0.2.0 on 2026-09-28, one author, pre-1.0 API that changed between 0.1.2 and 0.2.0.

## How it is fast

Decoding uses libdeflate-style tricks: a 64-bit bit buffer refilled branchlessly from an 8-byte little-endian load (`count |= 56`), a 10-bit (literal/length) and 9-bit (distance) first-level Huffman table with pre-decoded base and extra-bit fields and small overflow tables, and match copies done in 32-byte vector chunks for distances of 32 or more with a 289-byte output margin so the hot loop never bounds-checks per byte. Encoding uses hash chains over a 64K-entry head table with a 5-byte hash for `even`, a capped chain budget (12 probes for even, 160 for dense) with lazy matching, 32-byte SIMD match-length comparison, an entropy check that skips match search on incompressible windows, and dynamic Huffman blocks even at the fast preset. CRC-32 uses a PCLMUL fold and Adler-32 an AVX2 kernel, both chosen at run time.

## Compared with alternatives

Among catalogued compression siblings, crabz is a multithreaded pigz-style Rust gzip CLI and libbzip2-rs, bzip2z, snap and Supersnappy cover other formats; pick zipir when you need single-threaded DEFLATE-family streaming (including BGZF) inside a Zig program with fixed, small memory and no C dependency, and pick crabz or ISA-L when raw gzip compression throughput on many cores matters more.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none |
| **Minimum toolchain** | Zig 0.16.0 (minimum_zig_version in build.zig.zon) |
| **Platforms** | Linux and macOS on x86-64 and ARM64 (CI on all four); x86-64 picks PCLMUL CRC-32 and AVX2 Adler-32 at run time; Windows unsupported |
| **Thread safety** | No shared state and no threads; one workspace per stream, each usable on its own thread; a workspace must not move while in use |
| **Drop-in for the baseline** | partial — produces and reads standard gzip, zlib, raw DEFLATE and BGZF bytes interchangeably with zlib-ng, libdeflate and bgzip, but the API is Zig std.Io readers and writers, not the zlib C API, and compressed bytes differ from zlib-ng at the same nominal level |

## Gotchas

- The report says every batch ran pinned to CPU 4, but that sentence is hard-coded in bench/report.py; its own Method section says zipir's compression rows came from separate zipir-only runs on CPU 13 at a working tree with uncommitted changes, spliced against peer rows timed on CPU 4 (bench/splice.py). Different Zen 2 cores boost differently under schedutil, so the compression ratios are cross-run and cross-core; a later 10-round control batch agreed within -2.1% to -0.7%. The decompression rows are matched (same batch, same core).
- The 'Presets against every peer level' table, which gives the matched-ratio comparison (zipir fast 332.8 MB/s vs ISA-L level 2 371 MB/s), is also cross-run: peer levels come from separate all-level runs, zipir from the report run.
- Published numbers are -Dcpu=native (AVX2) builds; release binaries are built with -Dcpu=baseline, where only the checksum kernels are dispatched at run time and the engine's 32-byte vector copies and match-length compares compile to baseline SSE2, so release-binary speed is not measured.
- gzip, zlib and raw DEFLATE hand out decoded bytes before the trailer check; treat them as unverified until the reader reports end of stream (BGZF withholds a block until its CRC passes). Decoder fix b16996a (2026-09-30, stored-block and slow-path output-full handling) postdates the benchmark.

## Known shortcomings

- Decompression rows carry the A (commit ff8e9e8, same batches as peers) but the compression rows were timed on the uncommitted tree 5f25547 and spliced from separate runs; ranks streaming tools only (libdeflate full-buffer never timed); libdeflate wins BGZF decode 1.07x, ISA-L wins gzip compression and ties gzip decode; the level-1 win produces 34% larger output than zlib-ng; library design, not language; 0 stars.
- Harness flaw: the report's 'every batch ran pinned to CPU 4' is hard-coded in bench/report.py:959, while its Method section says zipir's compression rows came from zipir-only runs on CPU 13 at uncommitted tree 5f25547, spliced by bench/splice.py against peer rows timed on CPU 4, so the compression ratios (and the matched-ratio presets table, where ISA-L is about 1.1x faster) are cross-run and cross-core; a control batch agreed within -2.1% to -0.7%. Decompression rows are matched (same batch, same core) and stand. Published numbers are -Dcpu=native builds; release binaries are -Dcpu=baseline and unmeasured. Zebrac sends every tool's stdout to /dev/null, so no pipe asymmetry.

## Caveats and trade-offs

First-party report, one host, machine in normal use (matched interleaved rounds pinned to one CPU keep ratios fair). Compression rows were timed in zipir-only runs at commit 5f25547 with uncommitted changes and spliced against peer rows from a different run (zipir ff8e9e8); a later control batch agreed within -2.1% to -0.7%. The report predates release 0.2.1; the author says the release code decompresses faster and compresses a few percent slower on the small files. Times are whole processes including start-up and file I/O, not library cores. Rankings cover streaming tools only: libdeflate's full-buffer decoders, GNU gzip, host zlib, pigz and Rust flate2 passed qualification but were not timed, and libdeflate beats zipir on BGZF decompression. Nominal levels differ in effort (zlib-ng level 1 is its quick strategy with 34-41% larger output), so the level-1 compression win is not like-for-like; ISA-L igzip beats zipir on gzip compression. Decoder fix b16996a (2026-09-30, stored-block and slow-path output-full handling in src/engine/decode.zig) postdates the measurement; the benchmarked outputs were verified against reference decoders and the fast path only had its 289-byte margin turned into a named constant. A Zig library against different C implementations, not a language-level claim. 0 stars, very new repository. [retier] The report's 'every batch ran pinned to CPU 4' is hard-coded in bench/report.py; its Method section says zipir's compression rows came from zipir-only runs on CPU 13 at uncommitted tree 5f25547, spliced by bench/splice.py against peer rows timed on CPU 4, so the compression ratios and the matched-ratio presets table (ISA-L about 1.1x faster at matched ratio) are cross-run and cross-core (a control batch agreed within -2.1% to -0.7%). Decompression rows are matched (same batch, same core). Published numbers are -Dcpu=native builds; release binaries are -Dcpu=baseline and unmeasured. Every tool's stdout went to /dev/null (no pipe asymmetry).

Streaming library with fixed caller-owned memory (peak 0.55-0.62 MiB versus 1.6-5.0 MiB for the C tools); no dependencies; compression levels are zipir's own, so output sizes differ from zlib-ng at the same numeric level.

## Maintenance

Active single-author project (128 commits, last commit 2026-09-30, release 0.2.1), MIT-licensed, no dependencies and small enough to vendor, but 0 stars, no issues filed yet and a pre-1.0 API; the benchmark report predates 0.2.1, whose author-measured compression is a few percent slower and decompression faster.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now C.
- **Tier reason:** Public harness (tools/bench.sh with Zebrac matched rounds, tools/install.sh peer builds, bench/report.py) times zipir against zlib-ng 2.3.3, ISA-L igzip 2.32.1 and htslib 1.24 bgzip with libdeflate 1.26 or zlib-ng; compiler (Zig 0.16.0, GCC 16.2.1), flags (zipir ReleaseFast -Dcpu=native; zlib-ng CMake Release with WITH_NATIVE_INSTRUCTIONS, C adapters cc -O3 -DNDEBUG -march=native) and CPU (Ryzen 9 3950X) are all stated. The decompression rows (committed ff8e9e8, same batches as the peers) carry the A; the compression rows are weaker (uncommitted working tree, spliced runs).
- **Retiered** A to C: Enricher: the compression rows and the matched-ratio presets table were spliced from zipir-only runs on another core at an uncommitted working tree (the report's 'pinned to CPU 4' sentence is hard-coded), and the benchmarked -Dcpu=native build is not the release binary, so the compression side is cross-run and unreproducible; the decompression rows stand. First-party report with cross-run rows: A to C.
- **Verifier notes:** Numbers in the record match the report's summary table. Main shortcomings: compression rows from an uncommitted working tree timed in separate runs from the peers, rankings limited to streaming tools (libdeflate full-buffer not timed; libdeflate wins BGZF decode; ISA-L wins gzip compression and ties gzip decode), level-1 compression win comes with 34% larger zlib-ng output, single first-party host, 0 stars. Flags are matched (ReleaseFast -Dcpu=native against -O3/Release -march=native), so same_opt_level is true; same_algorithm stays false.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-73 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/eneskemalergin/zipir/HEAD/bench/linux-x86-avx2/README.md>
  - <https://raw.githubusercontent.com/eneskemalergin/zipir/HEAD/README.md>
  - <https://raw.githubusercontent.com/eneskemalergin/zipir/HEAD/tools/README.md>
  - <https://raw.githubusercontent.com/eneskemalergin/zipir/HEAD/tools/install.sh>
  - <https://raw.githubusercontent.com/eneskemalergin/zipir/HEAD/tools/bench.sh>
  - <https://github.com/eneskemalergin/zipir>
  - <https://github.com/eneskemalergin/zipir/commits/main>
  - <https://github.com/eneskemalergin/zipir/commit/5f25547>
  - <https://github.com/eneskemalergin/zipir/commit/ff8e9e8>
  - <https://github.com/eneskemalergin/zipir/commit/b16996a>
  - <https://github.com/eneskemalergin/zipir/commit/b16996a.diff>
- **Sources the enricher read:**
  - <https://github.com/eneskemalergin/zipir>
  - <https://github.com/eneskemalergin/zipir/commits/main>
  - <https://github.com/eneskemalergin/zipir/issues?q=is%3Aissue>
  - <https://github.com/eneskemalergin/zipir/tree/main/src>
  - <https://github.com/eneskemalergin/zipir/tree/main/src/engine>
  - <https://raw.githubusercontent.com/eneskemalergin/zipir/HEAD/README.md>
  - <https://raw.githubusercontent.com/eneskemalergin/zipir/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/eneskemalergin/zipir/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/eneskemalergin/zipir/HEAD/bench/linux-x86-avx2/README.md>
  - <https://raw.githubusercontent.com/eneskemalergin/zipir/HEAD/bench/report.py>
  - <https://raw.githubusercontent.com/eneskemalergin/zipir/HEAD/bench/splice.py>
  - <https://raw.githubusercontent.com/eneskemalergin/zipir/HEAD/tools/README.md>
  - <https://raw.githubusercontent.com/eneskemalergin/zipir/HEAD/tools/bench.sh>
  - <https://raw.githubusercontent.com/eneskemalergin/zipir/HEAD/tools/install.sh>
  - <https://raw.githubusercontent.com/eneskemalergin/zipir/HEAD/tools/common.sh>
  - <https://raw.githubusercontent.com/eneskemalergin/zipir/HEAD/tools/peers.tsv>
  - <https://raw.githubusercontent.com/eneskemalergin/zipir/HEAD/tools/c/zlib_adapter.c>
  - <https://raw.githubusercontent.com/eneskemalergin/zipir/HEAD/tools/zig/zipir.zig>
  - <https://raw.githubusercontent.com/eneskemalergin/zipir/HEAD/src/root.zig>
  - <https://raw.githubusercontent.com/eneskemalergin/zipir/HEAD/src/engine/decode.zig>
  - <https://raw.githubusercontent.com/eneskemalergin/zipir/HEAD/src/engine/encode.zig>
  - <https://raw.githubusercontent.com/eneskemalergin/zipir/HEAD/wiki/Library-Guide.md>
  - <https://raw.githubusercontent.com/eneskemalergin/zipir/HEAD/wiki/Formats-and-Limits.md>
  - <https://raw.githubusercontent.com/eneskemalergin/zipir/HEAD/wiki/Platforms-and-Acceleration.md>
  - <https://github.com/eneskemalergin/zebrac>
  - <https://raw.githubusercontent.com/eneskemalergin/zebrac/HEAD/README.md>
  - <https://raw.githubusercontent.com/eneskemalergin/zebrac/HEAD/src/main.zig>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/eneskemalergin/zipir`) · [data/wave14/enrich/raw/github_com_eneskemalergin_zipir.json](../../../data/wave14/enrich/raw/github_com_eneskemalergin_zipir.json) (enrichment confidence 0.72)

</details>
