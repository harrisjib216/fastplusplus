# bzip2gpu (weissenberger)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `CUDA C++` · `MIT` · 🟡 stale

> Research CUDA decompressor for standard .bz2 streams that runs every stage except parsing on the GPU; reported faster than multicore CPU bzip2.

| | |
|---|---|
| **Beats** | multicore CPU bzip2 decompressor (exact program not named in the search snippet; candidates bzip2, pbzip2, lbzip2) |
| **Claimed result** | Snippet only: up to 6.1x over a multicore CPU implementation for the inverse BWT stage; up to 2400 MB/s combined inverse BWT and inverse MTF on an A100; over 11.62 GB/s bzip2 archive decompression on a DGX H100. The README itself states no numbers. No whole-archive CPU baseline figure was seen. |
| **Workload** | bzip2 decompression on a GPU: Huffman decoding, RLE2, inverse MTF, inverse BWT and RLE1 all on the device, output kept in device memory (README). The paper (ICPP 2024, 'Massively Parallel Inverse Block-sorting Transforms for bzip2 Decompression on GPUs', DOI 10.1145/3673038.3673067 per the README) evaluates on an A100 GPU and a DGX H100 server. |
| **Metric** | throughput |
| **Hardware** | Per the paper snippet: NVIDIA A100 and a DGX H100 server; CPU model for the baseline not seen. README: CUDA GPU with compute capability 7.0 or higher. |
| **Compiler and flags** | Makefile (opened): nvcc -std=c++17 -O3 -arch=native -Xcompiler "-Wall -std=c++17 -O3 -march=native -fopenmp"; README requires GNU compiler 11.4.1+ and CUDA SDK 12.4.1+. Flags used for the paper's numbers are not seen. |
| **Adoption** | 6 stars |
| **Last commit** | 2024-07-16 |
| **Links** | [repository](https://github.com/weissenberger/bzip2gpu) · [benchmark](https://doi.org/10.1145/3673038.3673067) |

## Verdict

The repo has no benchmark or timing code (the timer macros in include/helpers.h are unused). All figures come from an unreproduced search snippet of the ICPP 2024 paper: up to 6.1x over an unnamed multicore CPU implementation for the inverse-BWT stage alone, up to 2400 MB/s for inverse BWT plus inverse MTF on an A100, and over 11.62 GB/s bzip2 decompression on a DGX H100. A DGX H100 is an 8-GPU server and the demo uses one GPU. Not documented: whether that figure is aggregate, whether it includes host transfers and the CPU parser, and the CPU model, baseline program or compiler flags behind any of the numbers.

## Use it when

- Bulk decompression of large existing .bz2 archives written by reference bzip2 (single stream, up to 2 GiB uncompressed each) when the next processing step runs on the GPU and can read the output from device memory.
- Data-centre NVIDIA GPUs (compute capability 7.0+, A100/H100 class) with more than about 11 GB of free device memory, on Linux with CUDA 12.4.1+.
- Studying or reproducing GPU inverse BWT and inverse MTF techniques (list ranking, permutation scan) from the ICPP 2024 paper.
- Trusted, text-like inputs whose decompressed output you check yourself (for example against a stored hash), since the tool does not.

## Skip it when

- Untrusted or possibly corrupt archives. Block and stream CRC32s are parsed but never checked, and the parser and decoder do no bounds checks, so bad input can give silent garbage or memory corruption.
- Archives from lbzip2 or pbzip2, concatenated .bz2 files, or data with runs of small byte values. The RLE1 stage can mis-decode these (see gotchas).
- Streams over 2^31 - 1 uncompressed bytes (no batching). Small archives: Huffman decoding uses one GPU thread per 900 kB block, so few blocks leave the GPU mostly idle, and the inverse-BWT buffers are a fixed \~10 GB allocation whatever the input size.
- GPUs with less than \~12 GB of memory, non-NVIDIA hardware, Windows or macOS.
- Any need for compression, streaming, a stable library API or production support. The README says it 'is not suitable for production use'; the repo has 2 commits and no tests.

## How it is fast

A CPU parser finds block headers by testing every bit offset for the 48-bit block magic in parallel with OpenMP. It then builds two-level Huffman lookup tables for each block. On the GPU, Huffman and RLE2 decoding uses one thread per bzip2 block with the tables in shared memory, and zero runs become skipped writes into a pre-zeroed buffer. Inverse MTF cuts each block into 10,000-byte pieces, computes each piece's MTF permutation in parallel and joins them with a Blelloch scan over permutation composition. Inverse BWT stable-sorts the last column with CUB segmented sort to get the LF permutation, then walks it with Helman-JaJa parallel list ranking (sublist heads every 32 positions). RLE1 is undone with a parallel run-detection predicate plus a Thrust scan/scatter/gather 'expand'.

## Compared with alternatives

Pick it over lbzip2 (the catalogued multi-threaded bzip2: 62.7 vs 41.1 MB/s single-thread decompression in lzbench 2.4) only to decompress large reference-bzip2 archives on a data-centre GPU, keep the output on the device, and check the output yourself. lbzip2 verifies CRCs, has no size limit and handles multi-stream files. For new data, zstd or libbsc (both catalogued) are better format choices than any bzip2 decoder.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | CUDA Toolkit 12.4.1+ (CUB and Thrust from the toolkit; src/rle.cu and include/thrust_custom_alloc.cuh hold modified Thrust code under Apache-2.0 with LLVM exceptions), OpenMP (libgomp), std::filesystem (-lstdc++fs) |
| **Minimum toolchain** | C++17; GCC 11.4.1+; CUDA SDK 12.4.1+; GPU compute capability 7.0+ (README). The Makefile builds with -O3 -arch=native -march=native. |
| **Platforms** | NVIDIA GPUs (cc 7.0+) on GNU/Linux. The host side is built with -march=native for the build machine. Other host architectures are not documented. |
| **Thread safety** | Not documented. decode_stream takes a caller-supplied cudaStream_t, but the parser calls omp_set_num_threads() process-wide, and any CUDA error (including out-of-memory) calls exit(1) through the CUERR macro. |
| **Drop-in for the baseline** | partial: reads the standard .bz2 format but is not a bzip2/libbz2 replacement. It has a different C++ API and a demo CLI (input, output, GPU id), decompresses only, offers no streaming, and does not verify checksums. |

## Gotchas

- Likely RLE1 correctness bug, found from a Python port and not run on a GPU. is_run in src/rle.cu decides whether a byte is a run-length count from the 9 bytes before it only (preceded_by_run plus a backward parity chain), not from decoder state. The port gets 'a'x101 + 'b'x102 + 'c' wrong: 'c' is read as a count and becomes 99 extra 'b's. It also fails on 0x01x5 + 0x00x4 + 0x03 and on any run of 511 or more 0xFB bytes. It produced 18 and 50 false count bytes per MB on synthetic 8-bit low-value image and label-map data, but none on ELF binaries (ls, bash, libc), small-int64 arrays or JSON text. Because CRCs are never checked, the wrong output goes unreported.
- RLE1 runs on all blocks concatenated, so a run split across a block boundary is decoded as one run. Reference bzip2 never splits a run across blocks within one stream: its pending run carries into the next block. lbzip2 does split runs: its encode.c collect() ends a full block mid-run. pbzip2 and cat'd .bz2 files are multi-stream, and the parser's block-magic scan accepts them silently. In the port, a 4-space indent split 2+2 across two streams turned the following 'r' into 114 spaces, and 89 of 2000 random cut points in a Python source file decoded wrong.
- Memory: batch_iBWT allocates buffers for 800 blocks whatever the input size. At -9 (900 kB blocks) that is 2 x 720 MB of keys plus 3 x 2.88 GB of uint32 arrays, about 10.3 GB, even for the 10 MB test file. RLE1 then adds about 2 GB of Thrust buffers. The compressed input and the full output must also fit on the device.
- No bitstream validation. A selector MTF index at or above the tree count writes past a host std::vector in parse_selectors. A tree count of 7 overflows the 6-table code_lengths slot, and decode_block never bounds out_idx. Randomised blocks (bzip2 0.9.0) are not handled (the flag is skipped). The block size is read once from the first stream header. The block finder reads one uint64 past the input buffer, and the API input size is in 64-bit words, not bytes.

## Known shortcomings

- Numbers exist only as a search snippet of the ICPP 2024 abstract (iBWT up to 6.1x vs a multicore CPU, 11.62 GB/s on a DGX H100); the paper is blocked here (doi.org, dl.acm.org, uni-mainz). No timing code in the repo, the CPU baseline is unnamed, the 6.1x covers the inverse BWT stage only, and the block CRC32 is parsed but never verified in any of the 7 source files. 2 commits, last 2024-07-16. Paper-access retier candidate (B).
- Enricher: likely correctness bug in RLE1 (src/rle.cu is_run decides count bytes from the previous 9 bytes only, with no decoder state): a Python port mis-decodes 'a'x101+'b'x102+'c', 0x01x5+0x00x4+0x03 and any run of 511 or more 0xFB bytes, giving 18-50 false count bytes per MB on synthetic low-value 8-bit data (none on ELF binaries, int64 arrays or JSON); the CRC is never checked so wrong output goes unreported. RLE1 also runs across block boundaries, so lbzip2 (which ends blocks mid-run), pbzip2 and concatenated .bz2 streams can mis-decode (89 of 2000 random cut points wrong in the port); reference single-stream bzip2 is safe. The inverse BWT allocates a fixed about 10.3 GB on the device (800 blocks x 900 kB) whatever the input size; Huffman decode is one GPU thread per block; no bitstream validation (host heap overflow in parse_selectors on a bad selector, unbounded out_idx in decode_block); errors exit(1); the DGX H100 has 8 GPUs and the demo uses 1.

## Caveats and trade-offs

The paper (ICPP '24, 'Massively Parallel Inverse Block-sorting Transforms for bzip2 Decompression on GPUs', pp. 856-865, DOI 10.1145/3673038.3673067 cited by the README) is behind blocked hosts (doi.org, dl.acm.org, researchgate and the JGU HPC group site returned EGRESS_BLOCKED; no PDF mirror in github.com/weissenberger, whose four public repos are gpuhd, multians, bzip2gpu and HIPSW4). The numbers come from a WebSearch snippet seen by the search agent only; the verifier's three queries did not reproduce it, so they are snippet-only and the tier is capped at C until someone reads the paper (likely B; fix the baseline name then). The snippet's 6.1x is for one stage (iBWT) against an unnamed multicore CPU implementation, and the 11.62 GB/s DGX H100 figure carries no baseline, so a win over bzip2, pbzip2 or lbzip2 on whole-archive decompression is not confirmed. The repo has no timing or benchmark code: src/main.cc only loads the file, calls bz2gpu::decode_stream, copies the output to the host and writes it, so the paper's throughput numbers cannot be reproduced from the repo as published; whether the GB/s figures include the host-to-device input copy, the CPU-side parser (parser::parse and build_tables run on the host with OpenMP) or the device-to-host output copy is unknown, and the README notes that uncompressed output is kept in device memory. Repo is explicitly 'auxiliary material for our publication and is not suitable for production use'. Block and stream CRC32s are never verified: a grep of all seven src files (bz2gpu.cc, decoder.cu, ibwt.cu, imtf.cu, main.cc, parser.cc, rle.cu) finds the checksum only parsed into block_checksums (parser.cc lines 220-243), matching the README TODO 'stream error detection (parsing, checksums,...)', so corrupt input is not detected. main.cc reads argv[1] and argv[2] without checking argc. Streams are limited to 2^31 - 1 uncompressed bytes (no batched execution yet). Only 2 commits (2024-07-15, 2024-07-16), no unit tests (TODO), only a 10 MB test file (test/lichess_puzzles_10M.bz2). src/rle.cu and include/thrust_custom_alloc.cuh carry modified Thrust code under Apache-2.0 with LLVM exceptions; the rest is MIT. [retier] Numbers are from the ICPP 2024 abstract via search snippets (iBWT up to 6.1x over an unnamed multicore CPU, 11.62 GB/s on a DGX H100 using 1 of 8 GPUs); no benchmark code in the repo. The RLE1 stage decides count bytes from the previous 9 bytes with no decoder state and runs across block boundaries, so some inputs and lbzip2, pbzip2 or concatenated streams mis-decode, and the block CRC is never checked. Fixed about 10.3 GB device allocation, no bitstream validation, 2 commits, last 2024-07-16. Paper-access retier candidate.

Needs a CUDA GPU (compute capability 7.0+), proprietary drivers and GNU/Linux. Streams limited to 2^31 - 1 uncompressed bytes (no batching yet). The parser still runs on the CPU. Output stays in device memory, so throughput numbers exclude the copy back to host. Decompress only; no compressor. src/rle.cu and include/thrust_custom_alloc.cuh contain modified Thrust code under Apache-2.0 with LLVM exceptions (also OSI-approved); the rest is MIT.

## Maintenance

Stale research artifact (2 commits, 2024-07-15 and 2024-07-16; 6 stars, 0 forks, no issues, no tests); MIT with Apache-2.0 Thrust-derived files, so copyable for study, but it should not be used as a production decompressor: it skips CRC checks and the RLE1 stage likely mis-decodes some inputs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The only numbers are from the ICPP 2024 paper (DOI 10.1145/3673038.3673067, cited by the README; ICPP '24 proceedings pp. 856-865 confirmed by search), which is behind blocked hosts (doi.org, dl.acm.org, hpc.informatik.uni-mainz.de all EGRESS_BLOCKED); three WebSearch queries did not reproduce the searcher's abstract snippet, so the figures are snippet-only and capped at C under the cloud-harness rule. The repo itself contains no benchmark or timing code, so A is impossible from the repo; B is likely once the peer-reviewed paper can be read.
- **Verifier notes:** Real peer-reviewed project (ICPP 2024) but every number is from a search snippet I could not reproduce, and the repo has no benchmark harness; kept at C with benchmark_url set to the README-cited DOI. Shortcomings to record: snippet-only numbers, unnamed CPU baseline and stage-only 6.1x, no timing code in the repo, CRC32 never checked (confirmed across all seven source files including the .cu kernels), research prototype limited to 2^31-1 bytes. Paper-access retier candidate (likely B).
- **Fields the verifier corrected:** `benchmark_url`, `caveats`
- **Shortcomings recorded by:** paper access and a CRC-checked end-to-end comparison; CRC-checked decode of lbzip2 and pbzip2 streams
- **Pages the verifier opened:**
  - <https://github.com/weissenberger/bzip2gpu>
  - <https://github.com/weissenberger/bzip2gpu/commits>
  - <https://github.com/weissenberger/bzip2gpu/tree/main/src>
  - <https://github.com/weissenberger>
  - <https://raw.githubusercontent.com/weissenberger/bzip2gpu/HEAD/README.md>
  - <https://raw.githubusercontent.com/weissenberger/bzip2gpu/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/weissenberger/bzip2gpu/HEAD/Makefile>
  - <https://raw.githubusercontent.com/weissenberger/bzip2gpu/HEAD/src/main.cc>
  - <https://raw.githubusercontent.com/weissenberger/bzip2gpu/HEAD/src/bz2gpu.cc>
  - <https://raw.githubusercontent.com/weissenberger/bzip2gpu/HEAD/src/parser.cc>
  - <https://raw.githubusercontent.com/weissenberger/bzip2gpu/HEAD/src/decoder.cu>
  - <https://raw.githubusercontent.com/weissenberger/bzip2gpu/HEAD/src/ibwt.cu>
  - <https://raw.githubusercontent.com/weissenberger/bzip2gpu/HEAD/src/imtf.cu>
  - <https://raw.githubusercontent.com/weissenberger/bzip2gpu/HEAD/src/rle.cu>
- **Sources the enricher read:**
  - <https://github.com/weissenberger/bzip2gpu>
  - <https://github.com/weissenberger/bzip2gpu/tree/main/include>
  - <https://github.com/weissenberger/bzip2gpu/issues>
  - <https://raw.githubusercontent.com/weissenberger/bzip2gpu/HEAD/README.md>
  - <https://raw.githubusercontent.com/weissenberger/bzip2gpu/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/weissenberger/bzip2gpu/HEAD/Makefile>
  - <https://raw.githubusercontent.com/weissenberger/bzip2gpu/HEAD/src/main.cc>
  - <https://raw.githubusercontent.com/weissenberger/bzip2gpu/HEAD/src/bz2gpu.cc>
  - <https://raw.githubusercontent.com/weissenberger/bzip2gpu/HEAD/src/parser.cc>
  - <https://raw.githubusercontent.com/weissenberger/bzip2gpu/HEAD/src/decoder.cu>
  - <https://raw.githubusercontent.com/weissenberger/bzip2gpu/HEAD/src/ibwt.cu>
  - <https://raw.githubusercontent.com/weissenberger/bzip2gpu/HEAD/src/imtf.cu>
  - <https://raw.githubusercontent.com/weissenberger/bzip2gpu/HEAD/src/rle.cu>
  - <https://raw.githubusercontent.com/weissenberger/bzip2gpu/HEAD/include/bz2gpu.h>
  - <https://raw.githubusercontent.com/weissenberger/bzip2gpu/HEAD/include/parser.h>
  - <https://raw.githubusercontent.com/weissenberger/bzip2gpu/HEAD/include/decoder.h>
  - <https://raw.githubusercontent.com/weissenberger/bzip2gpu/HEAD/include/helpers.h>
  - <https://raw.githubusercontent.com/weissenberger/bzip2gpu/HEAD/include/cuda_helpers.h>
  - <https://raw.githubusercontent.com/weissenberger/bzip2gpu/HEAD/include/stream.cuh>
  - <https://raw.githubusercontent.com/weissenberger/bzip2gpu/HEAD/include/thrust_custom_alloc.cuh>
  - <https://raw.githubusercontent.com/kjn/lbzip2/master/src/encode.c>
  - <https://github.com/dingwentao/GPU-lossless-compression>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/weissenberger/bzip2gpu`) · [data/wave9/enrich/raw/github_com_weissenberger_bzip2gpu.json](../../../data/wave9/enrich/raw/github_com_weissenberger_bzip2gpu.json) (enrichment confidence 0.6)

</details>
