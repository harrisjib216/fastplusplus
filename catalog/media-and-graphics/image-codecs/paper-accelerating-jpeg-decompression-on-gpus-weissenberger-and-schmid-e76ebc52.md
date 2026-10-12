# Accelerating JPEG Decompression on GPUs (Weissenberger and Schmidt, HiPC 2021)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Study only · `?` · `no license` · ⚪ unknown

> HiPC 2021 CUDA JPEG decoder design; claims up to 51x over libjpeg-turbo and 8x over nvJPEG on A100; no code.

| | |
|---|---|
| **Beats** | libjpeg-turbo (CPU) and NVIDIA nvJPEG (GPU) |
| **Claimed result** | From search-result snippet of the arXiv abstract (arXiv:2111.09219, paper page not opened): outperforms libjpeg-turbo (CPU) and nvJPEG (GPU) by up to 51x (34x) and 8.0x (5.7x) on A100 (V100), and up to 3.4x over nvJPEG with the dedicated hardware decoder on A100. |
| **Workload** | GPU JPEG decompression that locates codeword boundaries at arbitrary bitstream positions so independent chunks decode in parallel; compared on A100 and V100 GPUs against libjpeg-turbo and nvJPEG (also nvJPEG with the A100 hardware decoder). |
| **Metric** | throughput |
| **Hardware** | NVIDIA A100 and V100 GPUs (per snippet) |
| **Links** | [benchmark](https://arxiv.org/pdf/2111.09219) |

## Verdict

Two search-result snippets of the arXiv abstract (2111.09219; the paper itself is blocked here) report up to 51x over libjpeg-turbo and 8.0x over nvJPEG on an A100, 34x and 5.7x on a V100, and up to 3.4x over nvJPEG using the A100's hardware JPEG decoder. Neither snippet names the CPU model, thread count, CUDA or nvJPEG version, the images, or whether transfers are timed.

## Use it when

- As a design reference when building a GPU JPEG decoder that must parallelise baseline Huffman decoding of files without restart markers (camera, web or dataset JPEGs)
- Batch decoding of many large JPEGs on NVIDIA datacenter GPUs (A100, V100) where CPU libjpeg-turbo or nvJPEG's hybrid path is the bottleneck, for example ML data loading, provided you reimplement it
- Comparing against nvJPEG and the A100 hardware JPEG decoder: the abstract reports up to 3.4x over nvJPEG with that decoder
- Starting a prototype from the authors' gpuhd Huffman stage (LGPL-3.0, CUDA 8+, compute capability 3.0+)

## Skip it when

- You need something to link today: no code, binary or artifact was published with the paper
- Files that need features outside the paper's subset (the abstract says it implements 'an important subset of the JPEG standard'; which features are left out is not documented in any source readable here)
- Small images or low-latency single-image decode: PCIe transfers, kernel launches and gpuhd-style host round-trips for the sync loop are fixed costs, and whether the paper's timings include host-device transfers is not documented
- Non-NVIDIA GPUs or CPU-only deployments; use libjpeg-turbo or a multithreaded CPU decoder instead
- Pathological Huffman tables or streams that resynchronise slowly: gpuhd repeats its inter-block pass until all blocks agree, and no worst-case bound is documented

## How it is fast

It applies the authors' self-synchronising Huffman decoding (ICPP 2018, code in weissenberger/gpuhd) to the JPEG bitstream. Each thread starts decoding a fixed-size bit window at an arbitrary offset. Prefix codes tend to resynchronise, so a guessed start converges on the true codeword boundaries after a few codewords. In gpuhd this runs as an intra-block sync pass (phase1_decode_subseq), inter-block passes repeated from the host until every block agrees (phase2_synchronise_blocks), a thrust::exclusive_scan over per-chunk symbol counts that gives output offsets, and a final decode-and-write pass. The data-parallel stages after that (dequantisation, IDCT, colour conversion) map to the GPU directly. The JPEG-specific handling of DC/AC run-length symbols is described in the paper, which was not readable here.

## Compared with alternatives

The catalogued siblings (libjpeg-turbo, jpeg-nitro, zenjpeg, libjpeg-turbo-rs, MANGO) are all CPU decoders you can install; this is the only GPU JPEG decode design in the category, but with no code it is a reference for building a decoder, not a choice. For a working GPU path use nvJPEG (proprietary) or CESNET GPUJPEG (BSD-2-Clause, not catalogued, parallel Huffman only with restart markers); for CPU decoding use libjpeg-turbo or jpeg-nitro.

## Integration

| | |
|---|---|
| **Form** | none (paper only; no code released) |
| **Dependencies** | NVIDIA CUDA per the paper (A100 and V100 tested); the related gpuhd decoder needs CUDA SDK 8+, GCC 5.4+, GNU/Linux and Thrust |
| **Minimum toolchain** | not documented for the JPEG decoder (gpuhd: CUDA 8, GCC 5.4, compute capability 3.0) |
| **Platforms** | NVIDIA GPUs (A100 and V100 in the paper's evaluation) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- CPU baseline setup is unknown: if libjpeg-turbo ran on one thread, the 51x headline compares a whole A100 with one CPU core, and a multithreaded CPU decode of a batch would shrink the gap
- nvJPEG version, CUDA version, image set, chroma subsampling and whether transfers are timed are not documented in any readable source, so the 8.0x and 3.4x nvJPEG ratios cannot be checked
- The speedups are 'up to' figures; median or per-image results were not readable
- CESNET GPUJPEG, the common open-source alternative, decodes Huffman on the GPU only when the file has restart markers and otherwise falls back to the CPU (per its README). This paper's selling point is not needing restart markers.

## Known shortcomings

- Reference only: peer-reviewed HiPC 2021 paper (pp. 121-130) with no public code (the author's GitHub holds no JPEG repo). Numbers are snippet-only (A100 51x/8.0x; V100 figures unconfirmed) because arXiv 2111.09219 and every mirror are blocked here. GPU decoder, a different machine class from libjpeg-turbo on CPU.
- The paper remains blocked (arXiv, arxiv-vanity, paperswithcode, x-mol), so the V100 34x and 5.7x figures and the 3.4x over the A100 hardware decoder are confirmed only by search snippets; no code is published, and CPU thread count, nvJPEG version and transfer timing are unknown. The technique is documented from the authors' gpuhd cuhd_gpu_decoder.cu.

## Caveats and trade-offs

Snippet only: the paper could not be opened (arXiv, ar5iv, ADS, hgpu.org, encode.su, the Mainz HPC group page, Hugging Face and OpenAlex are all blocked here); benchmark_url is the arXiv PDF URL as it appears in search results, not opened. Its existence and venue are corroborated by several independent search results, including the GPULZ paper's reference list: 'André Weißenberger and Bertil Schmidt. Accelerating jpeg decompression on gpus. 2021 IEEE 28th International Conference on High Performance Computing, Data, and Analytics (HiPC), pages 121-130.' My own search snippets show only the A100 figures (up to 51x over libjpeg-turbo, 8.0x over nvJPEG); the V100 figures (34x, 5.7x) and the 3.4x over nvJPEG's A100 hardware decoder come from the search agent's snippet. Unknown: CPU model and thread count for libjpeg-turbo (a single-threaded CPU baseline would inflate the 51x), CUDA and nvJPEG versions, image set, and whether host-device transfers are timed. No code: the author's GitHub account (weissenberger) has exactly four repositories (HIPSW4, bzip2gpu, multians, gpuhd), none a JPEG decoder.

Needs an NVIDIA GPU and PCIe transfers; implements an important subset of the JPEG standard, not all of it. Presented at HiPC 2021 (peer reviewed). Related author repos on github.com/weissenberger (gpuhd, multians) cover GPU Huffman and ANS decoding, not a JPEG decoder.

## Maintenance

Peer-reviewed 2021 paper with no released code and nothing to maintain; it stays a research reference, and the authors' related gpuhd repository was last touched in February 2019 (8 commits, LGPL-3.0, no issues filed).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** Peer-reviewed HiPC 2021 paper that names libjpeg-turbo and nvJPEG as baselines, but every host carrying it (arXiv, ar5iv, ADS, hgpu.org, encode.su, Uni Mainz, Hugging Face, OpenAlex) is egress-blocked, so the numbers are snippet-only and no code exists; per the orchestrator's rule it stays a reference record at C.
- **Verifier notes:** Real paper, real named baselines, no code and no openable source in this environment; kept as reference at C. A retier needs an environment that reaches arXiv or IEEE to read the setup section.
- **Fields the verifier corrected:** `benchmark_url`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/weissenberger>
  - <https://github.com/weissenberger?tab=repositories>
  - <https://github.com/jndean/CUDAjpeg>
  - <https://raw.githubusercontent.com/dingwentao/GPU-lossless-compression/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/weissenberger/gpuhd>
  - <https://github.com/weissenberger/gpuhd/tree/master/src>
  - <https://github.com/weissenberger/gpuhd/issues?q=is%3Aissue>
  - <https://github.com/weissenberger/gpuhd/commits>
  - <https://raw.githubusercontent.com/weissenberger/gpuhd/HEAD/README.md>
  - <https://raw.githubusercontent.com/weissenberger/gpuhd/HEAD/src/cuhd_gpu_decoder.cu>
  - <https://raw.githubusercontent.com/weissenberger/multians/HEAD/README.md>
  - <https://raw.githubusercontent.com/weissenberger/bzip2gpu/HEAD/README.md>
  - <https://raw.githubusercontent.com/CESNET/GPUJPEG/HEAD/README.md>
  - <https://raw.githubusercontent.com/actcwlf/PIC/HEAD/README.md>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `paper:accelerating-jpeg-decompression-on-gpus-weissenberger-and-schmidt-hipc-2021`) · [data/wave10/enrich/raw/paper_accelerating_jpeg_decompression_on_gpus_weissenberger_and_schmidt_hipc_2021.json](../../../data/wave10/enrich/raw/paper_accelerating_jpeg_decompression_on_gpus_weissenberger_and_schmidt_hipc_2021.json) (enrichment confidence 0.45)

</details>
