# CUHD / gpuhd (massively parallel Huffman decoding on GPUs)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Entropy coders](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `CUDA/C++` · `LGPL-3.0` · 🔴 abandoned

> CUDA Huffman decoder (CUHD) that splits one unpartitioned bitstream across GPU threads by self-synchronization; reported 10x+ over zstd's CPU huff0.

| | |
|---|---|
| **Beats** | Zstandard's CPU Huffman decoder (huff0) |
| **Claimed result** | Snippet only (WebSearch summary of the paper): speedups of over one order of magnitude compared to the state-of-the-art CPU-based Zstandard Huffman decoder. |
| **Workload** | GPU Huffman decoding of raw unpartitioned Huffman streams using self-synchronisation, evaluated on TITAN V, TITAN Xp and GTX 1080 (ICPP 2018, DOI 10.1145/3225058.3225076). |
| **Metric** | throughput |
| **Hardware** | TITAN V, TITAN Xp, GTX 1080 (from search snippet) |
| **Compiler and flags** | README: GNU compiler 5.4.0+ and CUDA SDK 8+; flags not verified |
| **Adoption** | 50 stars |
| **Last commit** | 2019-02-02 |
| **Links** | [repository](https://github.com/weissenberger/gpuhd) · [benchmark](https://doi.org/10.1145/3225058.3225076) |

## Verdict

Per WebSearch summaries of the peer-reviewed ICPP 2018 paper (not opened; ACM blocked here), GPU decoding on TITAN V, TITAN Xp and GTX 1080 was over an order of magnitude faster than Zstandard's CPU Huffman decoder, and one citing-work snippet puts CUHD at about 10 GB/s; no CPU model, compiler flags or dataset are known, and the comparison pits a GPU against a CPU.

## Use it when

- You control both encoder and decoder and need to decode large (tens of MB and up) byte-symbol Huffman streams that already live on, or are headed to, an NVIDIA GPU.
- You cannot afford to add partition metadata (gap arrays, chunk offsets) to the stream format but still want GPU-wide parallel decode.
- Research or baseline use: it is the reference self-synchronization GPU Huffman decoder (ICPP 2018) that later work such as ipdps22-opthuffdec builds on and compares against.
- Throughput-bound pipelines where amortizing host-to-device transfers and kernel launches over a big buffer is acceptable.

## Skip it when

- Decoding standard formats (deflate, zstd/huff0, JPEG): codeword length is capped at MAX_CODEWORD_LENGTH = 11 (compile-time) and the bit layout is CUHD's own 32-bit-unit format from its llhuff encoder.
- Alphabets larger than 256 symbols: SYMBOL_TYPE is std::uint8_t.
- Small inputs or latency-sensitive calls: the decode runs four kernel phases, a host round-trip per phase-2 iteration and a Thrust scan, plus PCIe copies.
- Codes or data that synchronize slowly: phase 2 is relaunched in a host loop until all sequences synchronize, so the number of passes is data-dependent and unbounded in the code.
- Production use that needs a maintained library, AMD/Intel GPUs, Windows or macOS: the README targets GNU/Linux and CUDA only, and there are no commits since 2019-02-02.

## How it is fast

Uses the self-synchronization property of Huffman codes: each thread starts decoding a small subsequence (4 x 32-bit units in the demo) at an arbitrary bit offset, and decoding from a wrong offset usually falls back into codeword alignment within a few codewords. Phase 1 synchronizes subsequences within a thread block, phase 2 is relaunched until every block boundary has synchronized, phase 3 is a Thrust exclusive scan over per-subsequence symbol counts to get output offsets, and phase 4 re-decodes and writes symbols in parallel. Each symbol is decoded by a single direct lookup in a 2^11-entry table using a two-word sliding window.

## Compared with alternatives

Pick it over Huffman_coding_Gap_arrays when the stream format cannot carry a gap array, but prefer the optimized self-sync and gap-array variants in ipdps22-opthuffdec, which report faster decoding with CUHD as their baseline. For CPU decoding of standard Huffman, PIVCO-Huffman or FSE's Huff0 are the practical choices; for GPU entropy decoding with a newer design, the same author's multians (tANS) is the sibling.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | CUDA runtime and driver (libcudart, libcuda), Thrust (bundled with the CUDA toolkit); the bundled encoder/ subdirectory for encoding |
| **Minimum toolchain** | README: GCC 5.4.0+ and CUDA SDK 8+; the Makefile compiles host code with -std=c++17 -O3 -march=native -Wall -Werror and device code with nvcc --std=c++11 -O3, so a GCC with C++17 support is needed in practice |
| **Platforms** | GNU/Linux with an NVIDIA GPU of compute capability 3.0+; ARCH in the Makefile defaults to 70 (Volta) and must be edited per GPU |
| **Thread safety** | not documented; decode() launches on the default stream and reuses a caller-supplied CUHDGPUDecoderMemory, so concurrent decodes need separate buffers and serialize on the default stream |
| **Drop-in for the baseline** | no |

## Gotchas

- Build is configured by hand-editing CUDA_INCLUDE, CUDA_LIB and ARCH in the Makefile (defaults point at /usr/local/cuda-9.1 and sm_70); there is no CMake or install target.
- The caller must know the exact uncompressed size up front to size CUHDOutputBuffer; the stream carries no length or table header.
- Auxiliary memory scales with input: one uint4 sync point (16 bytes) plus a 32-bit output count per subsequence, which is 16 bytes of input in the demo configuration (SUBSEQ_SIZE 4, 128 threads), so aux memory is roughly the size of the compressed input.
- The repository has no benchmark results; the demo only prints per-phase microsecond timings and checks the round trip on random binomially distributed bytes.

## Known shortcomings

- Tier B on the ICPP 2018 paper, known only from abstract snippets ('over one order of magnitude' vs zstd's CPU Huffman, no multiplier); the DOI page is unopened.
- MAX_CODEWORD_LENGTH 11 is compile-time, symbols are uint8 and the stream format is its own llhuff (not huff0 or deflate compatible); the phase-2 sync loop relaunches until done (data-dependent pass count); auxiliary memory is about the size of the compressed input; the Makefile is hand-edited (cuda-9.1, sm_70); the repo has no results and the speedup is known only from snippets ('over one order of magnitude' vs zstd huff0, about 10 GB/s per a citing snippet).

## Caveats and trade-offs

Paper not reachable (ACM/doi blocked); README has no numbers; speedup known only from WebSearch summaries of the abstract ('over one order of magnitude' vs zstd's CPU Huffman decoder, no multiplier or GB/s figure given). GPU vs CPU comparison, so the gain includes the hardware difference. 8 commits, May 2018 to February 2019; no activity since. The IPDPS 2022 artifact codyjrivera/ipdps22-opthuffdec uses CUHD as its 'orig-self-sync' baseline and ships optimized variants of it (GCC 8.3.1, NVCC 11.1, V100), so faster derivatives exist.

Needs a CUDA GPU with compute capability 3.0+; basic sequential encoder only; decoding is compatible with ordinary Huffman streams (no gap array needed).

## Maintenance

Abandoned since 2019-02-02 (8 commits, 50 stars, no issues filed); LGPL-3.0, so static linking into closed-source code carries relinking obligations, and the code targets CUDA 8/9-era toolchains.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** The README links the peer-reviewed ICPP 2018 paper (doi 10.1145/3225058.3225076); two WebSearch summaries of its abstract say it evaluates on TITAN V, TITAN Xp and GTX 1080 and shows speedups of over one order of magnitude vs the state-of-the-art CPU Zstandard Huffman decoder. The paper itself (ACM, ResearchGate) is blocked here, the repo has no results, and no flags or CPU model are known, so not A; held at B on the peer-reviewed abstract as in earlier snippet-only paper verdicts.
- **Verifier notes:** Metadata matches (LGPL-3.0 LICENSE file, 50 stars, not a fork, last commit 2019-02-02, abandoned). benchmark_url set to the paper DOI the README links; it was not opened (blocked).
- **Fields the verifier corrected:** `benchmark_url`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/weissenberger/gpuhd>
  - <https://github.com/weissenberger/gpuhd/commits>
  - <https://raw.githubusercontent.com/weissenberger/gpuhd/HEAD/README.md>
  - <https://raw.githubusercontent.com/weissenberger/gpuhd/HEAD/LICENSE>
  - <https://github.com/codyjrivera/ipdps22-opthuffdec>
- **Sources the enricher read:**
  - <https://github.com/weissenberger/gpuhd>
  - <https://raw.githubusercontent.com/weissenberger/gpuhd/HEAD/README.md>
  - <https://raw.githubusercontent.com/weissenberger/gpuhd/HEAD/Makefile>
  - <https://github.com/weissenberger/gpuhd/tree/master/src>
  - <https://github.com/weissenberger/gpuhd/tree/master/include>
  - <https://raw.githubusercontent.com/weissenberger/gpuhd/HEAD/include/cuhd_constants.h>
  - <https://raw.githubusercontent.com/weissenberger/gpuhd/HEAD/include/cuhd_definitions.h>
  - <https://raw.githubusercontent.com/weissenberger/gpuhd/HEAD/include/cuhd_gpu_decoder.h>
  - <https://raw.githubusercontent.com/weissenberger/gpuhd/HEAD/include/cuhd_subsequence_sync_point.h>
  - <https://raw.githubusercontent.com/weissenberger/gpuhd/HEAD/src/cuhd_gpu_decoder.cu>
  - <https://raw.githubusercontent.com/weissenberger/gpuhd/HEAD/src/demo.cc>
  - <https://github.com/weissenberger/gpuhd/issues?q=is%3Aissue>
  - <https://github.com/codyjrivera/ipdps22-opthuffdec>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/weissenberger/gpuhd`) · [data/wave9/enrich/raw/github_com_weissenberger_gpuhd.json](../../../data/wave9/enrich/raw/github_com_weissenberger_gpuhd.json) (enrichment confidence 0.7)

</details>
