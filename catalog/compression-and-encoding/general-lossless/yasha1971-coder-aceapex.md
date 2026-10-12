# ACEAPEX

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Block-independent LZ77 with zstd-coded token streams; decodes in parallel on CPU/GPU and supports random-access reads, aimed at genomic archives.

| | |
|---|---|
| **Beats** | zstd (zstd -3); also zlib in lzbench |
| **Claimed result** | README: 'At ratio 3.98 versus zstd -3 at 3.96 on the same file, ACEAPEX -T8 decodes at 7,401 MB/s against zstd -3 at 2,026 MB/s: 3.65x faster at genuinely comparable ratio.' Single thread decode is 1,624 MB/s on that file. lzbench 2.4 (EPYC 9555P, silesia.tar) lists aceapex 1.0.1 -1 at 55.9 MB/s compress, 675 MB/s decompress, ratio 32.35 versus zlib 1.3.2 -9 at 11.3 MB/s, 318 MB/s, ratio 31.92. |
| **Workload** | Parallel decode of a 1 GB FASTQ file (ERR194147) with block-independent LZ77 and absolute offsets; also enwik9 and silesia, on CPU with 8 threads and on GPU. |
| **Metric** | throughput |
| **Hardware** | README says reproduce scripts were verified on an EPYC 4344P; the CPU for the FASTQ table is not stated there. GPU numbers on Tesla T4 to Blackwell. |
| **Compiler and flags** | g++ -O3 -march=native -funroll-loops -std=c++17 (CPU build); nvcc -O3 (GPU build); links libzstd for entropy |
| **Adoption** | 6 stars; included in lzbench 2.3/2.4 and TurboBench 2.2.1 |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/yasha1971-coder/aceapex) · [benchmark](https://github.com/yasha1971-coder/aceapex) |

## Verdict

The headline is first-party: on the 1 GB ERR194147 FASTQ (re-measured after an earlier sample with degenerate quality strings was withdrawn), 8-thread ACEAPEX decodes at 7,401 MB/s against zstd -3 at 2,026 MB/s at near-equal ratio (3.98 vs 3.96), where the zstd thread count is not stated and the CPU for that table is not named; single-thread ACEAPEX is 1,624 MB/s. The independent lzbench 2.4 table (EPYC 9555P, gcc 15.2.0, silesia, one thread) has the older 1.0.1 format at 675 MB/s decode, about half of zstd -1.

## Use it when

- Write-once, read-many archives of genomes (FASTA/FASTQ) where you need region reads by offset: the authors report 0.081 ms 16 KB seeks on chr1 against 0.140 ms for bgzip+fai, at 11.8% smaller size
- Multi-core full decode of large files where you can spend 8 or more threads on decompression
- GPU-resident data pipelines that decode compressed data on the device (open profile needs no nvCOMP)
- Batched random range reads (aceapex_decompress_ranges) where requests cluster in the same blocks

## Skip it when

- As a general zstd replacement on one thread: independent lzbench 2.4 (EPYC 9555P) shows aceapex 1.0.1 decoding silesia at about 675 MB/s against zstd -1 at 1351 MB/s, and the README's own single-thread FASTQ figure (1,624 MB/s) is below zstd -3's 2,026 MB/s
- When interoperability matters: ACEPX2 is a private container, the lzbench copy is the older format 1, and archive bytes depend on the libzstd version used to encode
- When ratio is the goal: the README says zstd -19 is 1.2-1.55x denser on FASTQ with a whole-file window
- Write-heavy workloads: the README calls encode slow (50 GB at about 340 MB/s) and the project 'research-grade'
- When you need a mature, long-fuzzed decoder for hostile input (see gotchas): the code changes daily and the 2.1.0 API returned wrong bytes under concurrent calls

## How it is fast

Confining matches to the block removes cross-block dependencies, so blocks decode in parallel across threads or GPU warps; inside a block the encoder redirects references to their earliest origin where it can verify the bytes, shortening dependency chains, and the GPU decoder resolves the rest by wavefront ordering and closed-form periodic fills. Entropy work is pushed into large zstd or AVX2 rANS chunks that decode independently of the match phase, and DNA literals get a 2-bit base packing with a case bitmask and exception list. Recent CPU gains come from literal tiles held in L2, transparent huge pages, and non-temporal output stores (CHANGELOG 2.3 draft).

## Compared with alternatives

Choose it over Zstandard or zlib-ng only when you need parallel or ranged decode of a large static file, especially genomic data or GPU-resident decode; Rapidgzip gives parallel decode while keeping the standard gzip format, and for plain single-thread speed LZ4, zstd and misa77 decode faster.

## Integration

| | |
|---|---|
| **Form** | static lib or CLI from one C++ translation unit (src/aceapex_api.cpp); standalone C99 decoder as source-drop or shared lib (c/aceapex_decode.c); Python package; optional CUDA shared lib |
| **Dependencies** | libzstd (1.4.8 or 1.5.x; the open profile's archives need no zstd frames), pthreads; GPU Mode 2 needs NVIDIA nvCOMP 5 (closed source) |
| **Minimum toolchain** | C++17 (g++ -O3 -march=native in the documented build), C99 for the decoder, nvcc with -std=c++17 for GPU (default target sm_75) |
| **Platforms** | x86-64, x86-32, ARM32, ARM64 and PPC64LE pass the release cross-matrix under qemu-user; MinGW builds the library but no Windows runner; CLI is POSIX (mmap); GPU on NVIDIA sm_75 and later (T4 to Blackwell tested) |
| **Thread safety** | Per-call state since 2.2.0 (globals made thread-local after concurrent calls returned wrong bytes in 2.1.0; the lzbench 1.0.1 copy is unaffected); aceapex_decompress uses every hardware thread unless aceapex_decompress_mt is given a budget |
| **Drop-in for the baseline** | no |

## Gotchas

- Possible integer overflow in header validation (from reading the code, not tested): both open_arc in c/aceapex_decode.c and ax_header_ok in src/aceapex_main.cpp check 68 + num_blocks\*64 + zlit_sz + zoff_sz + zlen_sz + zcmd_sz &lt;= src_size in unchecked uint64 arithmetic, so crafted 64-bit stream sizes can wrap the sum, pass the check and send stream pointers and cursor bounds outside the buffer in the in-memory API. The C decoder was fuzzed 2,400 runs and the C++ reader 3,000 runs under ASan/UBSan per the CHANGELOG, which random bytes would rarely hit.
- The 'random access' unit is the entropy chunk, not the 16 KiB block: a region read unpacks the zstd or rANS chunks of all four streams that cover it (512 KiB default for token streams, 64 KiB to 1 MiB for literals), so seek cost and ratio depend on LIT_CHUNK and related knobs.
- Tuning comes from environment variables (AX_PROFILE, ACEAPEX_BS, LIT_CHUNK and 13 more) only in builds with ACEAPEX_ENV_TUNING; the library inside lzbench, TurboBench or your program ignores them since 2.2.2, so CLI numbers may use settings your build does not.
- nvCOMP 5.3.0.16 hangs on some corrupt zstd frames (repro in the repo); the GPU library offers ACEAPEX_GPU_VALIDATE_ZSTD to check every frame through libzstd on the host first.

## Known shortcomings

- Tier C: the README's 3.65x is 8 threads against zstd -3 with the zstd thread count unstated; on lzbench's single-thread Silesia run it is slower than zstd -1.
- Possible uint64 overflow in the header check (open_arc in c/aceapex_decode.c, ax_header_ok in src/aceapex_main.cpp): the sum of four file-supplied stream sizes is unchecked, so a wrap could pass the check and the in-memory API then points outside the buffer (read from code, not tested; fuzzed 2400/3000 runs per CHANGELOG). The 2.1.0 API returned wrong bytes under concurrent calls (fixed in 2.2.0). The random-access unit is the entropy chunk (512 KiB tokens, 64 KiB to 1 MiB literals), not a 16 KiB block, and the 'equal 16 KB blocks' ratio table gives ACEAPEX cross-block entropy chunks. Single-thread slower than zstd (lzbench 2.4: 675 vs 1351 MB/s). The lzbench copy is format 1; ACEPX2 is private. Archive bytes depend on the libzstd version. Mode 2 needs closed nvCOMP, and nvCOMP 5.3.0.16 hangs on corrupt frames.

## Caveats and trade-offs

First-party claim, mostly genomic data. The 3.65x figure compares an 8-thread decoder with zstd -3 whose thread count is not stated; single thread (1,624 MB/s) is slower than zstd -3 on the same file. The README previously published higher figures from a sample with degenerate quality strings and re-measured them. Papers are on arXiv (not opened).

Encode is slow and research grade; the ratio is 1.2-1.55x worse than zstd -19 on FASTQ. Main CPU build depends on libzstd; one GPU mode needs the closed-source nvcomp library. Block independence enables random access and GPU decode.

## Maintenance

Very active (releases 2.1.0, 2.2.0 and 2.2.2 between 2026-09-29 and 2026-10-01, with a 2.3 draft open) and MIT-licensed with a written format spec and conformance fixtures, but self-described as research-grade; pin a release and validate untrusted archives before use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The repo README's lzbench 2.3 table gives FASTQ 1 GB 1,624 / 7,401 MB/s (1 thread / -T8), enwik9 655 / 5,109, silesia 803 / 5,594, and states ACEAPEX -T8 at 7,401 MB/s versus zstd -3 at 2,026 MB/s at ratio 3.98 versus 3.96; these are first-party runs with no CPU model for the headline table, so C. The independent lzbench 2.4 table (EPYC 9555P, gcc 15.2.0) shows aceapex 1.0.1 slower than zstd -1 on silesia (675-679 versus 1351 MB/s decode), which does not support a general-data win.
- **Verifier notes:** All numbers in claimed_speedup and the lzbench 2.4 caveat match the pages. The 3.65x headline is 8-thread ACEAPEX versus zstd -3 with no thread count stated for zstd; the README's own 1-thread silesia figure (803 MB/s) is higher than lzbench's 1.0.1 row (675 MB/s). Repo: MIT, 6 stars, 642 commits, latest commit 2026-10-03; lzbench master's codec list now names aceapex 2.2.2 while its results table still shows 1.0.1.
- **Shortcomings recorded by:** verifier; lzbench 2.4
- **Pages the verifier opened:**
  - <https://github.com/yasha1971-coder/aceapex>
  - <https://raw.githubusercontent.com/yasha1971-coder/aceapex/HEAD/README.md>
  - <https://github.com/yasha1971-coder/aceapex/commits>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/yasha1971-coder/aceapex/HEAD/README.md>
  - <https://raw.githubusercontent.com/yasha1971-coder/aceapex/HEAD/c/aceapex_decode.c>
  - <https://raw.githubusercontent.com/yasha1971-coder/aceapex/HEAD/src/aceapex.h>
  - <https://raw.githubusercontent.com/yasha1971-coder/aceapex/HEAD/src/aceapex_main.cpp>
  - <https://raw.githubusercontent.com/yasha1971-coder/aceapex/HEAD/CLAIMS.md>
  - <https://raw.githubusercontent.com/yasha1971-coder/aceapex/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/yasha1971-coder/aceapex/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/yasha1971-coder/aceapex/HEAD/Makefile>
  - <https://raw.githubusercontent.com/yasha1971-coder/aceapex/HEAD/docs/FORMAT_ACEPX2.md>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/yasha1971-coder/aceapex`) · [data/wave9/enrich/raw/github_com_yasha1971_coder_aceapex.json](../../../data/wave9/enrich/raw/github_com_yasha1971_coder_aceapex.json) (enrichment confidence 0.7)

</details>
