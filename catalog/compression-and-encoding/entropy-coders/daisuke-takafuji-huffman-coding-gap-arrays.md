# Huffman_coding_Gap_arrays (gap-array GPU Huffman)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Entropy coders](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `CUDA/C` · `no license` · 🔴 abandoned

> Research CUDA Huffman encoder/decoder (ICPP 2020) whose gap array lets every GPU thread start decoding at a known bit offset.

| | |
|---|---|
| **Beats** | Previously published GPU Huffman decoders (unnamed in the abstract summaries; the IPDPS 2022 artifact codyjrivera/ipdps22-opthuffdec benchmarks this decoder alongside CUHD's self-synchronization decoder), an unnamed CPU Huffman implementation, and the same GPU decoder without a gap array |
| **Claimed result** | Snippet only (WebSearch summaries of the ICPP 2020 abstract): GPU Huffman decoding 1.26x-2.63x faster (encoding 2.87x-7.70x faster) than previously presented GPU Huffman decoding (encoding); GPU decoding 35.2x-43.3x faster than CPU implementations; with a gap array attached, decoding is a further 1.67x-6450x faster than without one. |
| **Workload** | CUDA encoder and decoder implementing Huffman coding with gap arrays for GPU acceleration (ICPP 2020, DOI 10.1145/3404397.3404429). |
| **Metric** | throughput |
| **Adoption** | 8 stars |
| **Last commit** | 2020-10-09 |
| **Links** | [repository](https://github.com/daisuke-takafuji/Huffman_coding_Gap_arrays) |

## Verdict

Per WebSearch summaries of the ICPP 2020 abstract (paper, slides and ACM PDF not opened), on a Tesla V100 with 10 files, GPU encoding was 2.87x-7.70x and decoding 1.26x-2.63x faster than previously published GPU Huffman code, and attaching a gap array sped decoding a further 1.67x-6450x over the same decoder without one. CPU speedups are quoted as 35.2x-43.3x in the record and as 35.2x-52.3x for decoding (18.7x-39.2x for encoding) in a later summary; the CPU implementation, compiler flags and CPU model are not named in what could be read.

## Use it when

- Studying or porting the gap-array idea into your own GPU codec where you control both encoder and decoder format.
- Byte-alphabet (256-symbol) data already resident on an NVIDIA GPU, where decode throughput matters more than about 3% extra compressed size.
- As a baseline when benchmarking newer GPU Huffman decoders (the IPDPS 2022 opthuffdec artifact already wires it in for that purpose).

## Skip it when

- Decoding standard Huffman streams (Deflate, JPEG, zstd huff0): the format needs the gap array, so it cannot read them.
- Anything needing a license: the repository has no license file, so the code is all-rights-reserved by default and only usable as reference.
- Production use: no tests, no error handling beyond fatal exits, no API, no maintenance since October 2020, and the CLI always runs 200 timed loops.
- Inputs of 2 GiB or more (the decoder reads sizes as int) or alphabets wider than bytes (MAX_CODE_NUM 256).
- Non-NVIDIA or non-Linux targets: CUDA only, Makefile hard-codes sm_70 and /usr/local/cuda, and the encoder uses fsync/fdatasync on glibc FILE internals.

## How it is fast

The encoder splits the compressed bit stream into 128-bit segments and stores, per segment, a 4-bit 'gap' (the offset of the first codeword starting in it), packed 8 per 32-bit word; the decoder then gives each thread one segment and starts decoding immediately, with no self-synchronization pass. Output positions come from a single-kernel decoupled look-back prefix sum (blocks take ids from an atomic counter and publish aggregate/prefix flags, which the paper calls Single Kernel Soft Synchronization). Decoding uses a two-level lookup table (10-bit first-level prefix) copied into shared memory, 32-bit word-wise global loads and atomicOr word writes; codes are length-limited to 16 bits by a CPU boundary package-merge, and the histogram runs on the GPU.

## Compared with alternatives

Pick it over CUHD/gpuhd when you can change the encoder: the gap array replaces CUHD's self-synchronization pass, which the paper reports as 1.26x-2.63x faster decoding. Pick ipdps22-opthuffdec instead if you want the newer, faster decoders (it includes an optimized gap-array decoder plus cuSZ integration); for CPU decoding, FiniteStateEntropy's huff0 or PIVCO-Huffman are the relevant choices.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | CUDA toolkit (nvcc, CUDA runtime); GNU Make |
| **Minimum toolchain** | not documented; Makefile builds with nvcc -O2 -arch=sm_70 (Volta) and needs a C++ compiler for the .cpp files |
| **Platforms** | NVIDIA GPU (default sm_70, edit ARCH for others), Linux |
| **Thread safety** | not documented; single-process CLI tools with global timing state |
| **Drop-in for the baseline** | no |

## Gotchas

- The decoder ignores its second argument and always writes ./decodedfile (huff.cpp opens "decodedfile" and never reads argv[2]; it also does not check argc).
- decoder.cu clears gpu_output with cudaMemset sized by the compressed input words, not the output buffer, before atomicOr writes: for compressible data part of the output is never zeroed (correct only if cudaMalloc returned zeroed memory), and for incompressible data the memset runs past the buffer. It also frees gpu_input twice and leaks gpu_output.
- Gap entries are 4 bits per 128-bit segment, so the gap array adds about 3.1% to the compressed size (derived from constants.hpp and the encoder's sizing).
- Printed decode time covers the kernel only; host-to-device and device-to-host copies are reported as separate columns.

## Known shortcomings

- Tier B on paper abstract snippets: 1.26x-2.63x vs earlier GPU decoders and 35.2x-43.3x vs unnamed CPU code; the 6450x figure is against its own decoder without the gap array. No license, so reference.
- No license; standalone CLI demos only with no API. The decoder ignores its output argument and always writes ./decodedfile; decoder.cu clears the output buffer with a memset sized by the input before the atomicOr writes, so output is under-zeroed when data compresses and the memset overruns the buffer when it does not; double cudaFree(gpu_input), gpu_output leaked, sizes stored as int (under 2 GiB). The bugs do not touch the timed kernel. The CPU speedup reads 35.2x-43.3x in the record but 35.2x-52.3x in a newer snippet, unresolved.

## Caveats and trade-offs

Repo README gives no numbers, compiler or hardware; no LICENSE, LICENSE.txt, LICENSE.md or COPYING at the root and none shown on the repo page (subdirectories not checked), so reference only. All numbers come from WebSearch summaries of the abstract; the paper, the github.io slides and the ACM PDF are blocked here. The CPU baseline is not named in the summaries. The 6450x upper bound compares against decoding without a gap array, i.e. the decoder's own fallback. Gap arrays change the encoded format, so it is not a drop-in decoder for plain Huffman streams. 9 commits, all between 2020-10-06 and 2020-10-09.

Requires encoding with the gap array (extra stored data, not compatible with plain Huffman streams).

## Maintenance

Abandoned research code (9 commits, 2020-10-06 to 2020-10-09) with no license, so reference only; the Makefile targets CUDA sm_70 with nvcc -O2.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed ICPP 2020 paper (doi 10.1145/3404397.3404429) whose abstract, per two WebSearch summaries, reports GPU decoding 1.26x-2.63x faster than previously presented GPU Huffman decoding and 35.2x-43.3x faster than CPU implementations; the paper, slides (github.io) and ACM PDF are blocked here and the repo has no numbers, flags or CPU model, so not A. The 6450x figure is relative to the same decoder without a gap array, not to an incumbent, so the &gt;50x cap was not applied to the incumbent comparisons.
- **Verifier notes:** Record's speedup was accurate but framed only against the no-gap-array self-comparison; corrected to lead with the incumbent comparisons from the same abstract. Metadata matches (8 stars, not a fork, last commit 2020-10-09, abandoned, no license).
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/daisuke-takafuji/Huffman_coding_Gap_arrays>
  - <https://github.com/daisuke-takafuji/Huffman_coding_Gap_arrays/commits>
  - <https://raw.githubusercontent.com/daisuke-takafuji/Huffman_coding_Gap_arrays/HEAD/README.md>
  - <https://github.com/codyjrivera/ipdps22-opthuffdec>
- **Sources the enricher read:**
  - <https://github.com/daisuke-takafuji/Huffman_coding_Gap_arrays>
  - <https://raw.githubusercontent.com/daisuke-takafuji/Huffman_coding_Gap_arrays/HEAD/README.md>
  - <https://github.com/daisuke-takafuji/Huffman_coding_Gap_arrays/tree/master/decoder>
  - <https://github.com/daisuke-takafuji/Huffman_coding_Gap_arrays/tree/master/encoder>
  - <https://github.com/daisuke-takafuji/Huffman_coding_Gap_arrays/tree/main/decoder/src>
  - <https://github.com/daisuke-takafuji/Huffman_coding_Gap_arrays/tree/main/decoder/include>
  - <https://github.com/daisuke-takafuji/Huffman_coding_Gap_arrays/tree/main/encoder/src>
  - <https://raw.githubusercontent.com/daisuke-takafuji/Huffman_coding_Gap_arrays/HEAD/decoder/Makefile>
  - <https://raw.githubusercontent.com/daisuke-takafuji/Huffman_coding_Gap_arrays/HEAD/decoder/README.md>
  - <https://raw.githubusercontent.com/daisuke-takafuji/Huffman_coding_Gap_arrays/HEAD/decoder/src/decoder.cu>
  - <https://raw.githubusercontent.com/daisuke-takafuji/Huffman_coding_Gap_arrays/HEAD/decoder/src/huff.cpp>
  - <https://raw.githubusercontent.com/daisuke-takafuji/Huffman_coding_Gap_arrays/HEAD/decoder/src/get_table.cpp>
  - <https://raw.githubusercontent.com/daisuke-takafuji/Huffman_coding_Gap_arrays/HEAD/decoder/include/constants.hpp>
  - <https://raw.githubusercontent.com/daisuke-takafuji/Huffman_coding_Gap_arrays/HEAD/decoder/include/decoder.cuh>
  - <https://raw.githubusercontent.com/daisuke-takafuji/Huffman_coding_Gap_arrays/HEAD/encoder/Makefile>
  - <https://raw.githubusercontent.com/daisuke-takafuji/Huffman_coding_Gap_arrays/HEAD/encoder/README.md>
  - <https://raw.githubusercontent.com/daisuke-takafuji/Huffman_coding_Gap_arrays/HEAD/encoder/src/huff.cpp>
  - <https://raw.githubusercontent.com/daisuke-takafuji/Huffman_coding_Gap_arrays/HEAD/encoder/src/encoder.cu>
  - <https://raw.githubusercontent.com/daisuke-takafuji/Huffman_coding_Gap_arrays/HEAD/encoder/src/package_merge.cpp>
  - <https://raw.githubusercontent.com/daisuke-takafuji/Huffman_coding_Gap_arrays/HEAD/encoder/src/symbols.cpp>
  - WebSearch: "Huffman Coding with Gap Arrays for GPU Acceleration" ICPP 2020 Tesla V100 decoding throughput (snippets only)
  - https://raw.githubusercontent.com/jnamaral/icpp20/HEAD/slides/Yamamoto_Huffman.pdf (404)
  - https://raw.githubusercontent.com/jnamaral/jnamaral.github.io/HEAD/icpp20/slides/Yamamoto_Huffman.pdf (404)
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/daisuke-takafuji/huffman_coding_gap_arrays`) · [data/wave9/enrich/raw/github_com_daisuke_takafuji_huffman_coding_gap_arrays.json](../../../data/wave9/enrich/raw/github_com_daisuke_takafuji_huffman_coding_gap_arrays.json) (enrichment confidence 0.6)

</details>
