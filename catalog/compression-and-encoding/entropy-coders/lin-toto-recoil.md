# Recoil (parallel rANS decoding)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Entropy coders](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `GPL-3.0` · 🟢 active

> Header-only C++20 rANS library that splits one interleaved stream for parallel decode on AVX2/AVX-512 CPUs and CUDA GPUs.

| | |
|---|---|
| **Beats** | single-thread interleaved rANS, conventional fixed-partition parallel rANS, and the multians GPU ANS decoder (not zstd/lz4/zlib/brotli/xz) |
| **Claimed result** | Snippet only (ICPP 2023 paper, arXiv 2306.12141, not opened): decoding throughput comparable to conventional parallel rANS while cutting compression overhead by up to 14.12% vs fixed partitioning, over 90 GB/s on a Turing GPU, greatly outperforming other ANS-based codecs such as multians. No per-dataset numbers read. |
| **Workload** | Parallel interleaved rANS decoding with decoder-adaptive split counts on CPU and GPU, measuring decode throughput and extra bitstream overhead versus fixed partitioning (ICPP 2023, arXiv 2306.12141). |
| **Metric** | throughput |
| **Compiler and flags** | gcc-10 (g++-10) and CUDA 12.1 in the testscripts Dockerfile; CMake Release build with -DPROB_BITS=11/16 and optional -DAVX512 (from build.sh); exact optimization flags not checked |
| **Adoption** | 19 stars |
| **Last commit** | 2026-07-12 |
| **Links** | [repository](https://github.com/lin-toto/recoil) · [benchmark](https://github.com/lin-toto/recoil-testscripts) |

## Verdict

Per search snippets of the ICPP 2023 paper (arXiv 2306.12141, not opened), CPU runs on a 16-core Xeon W-3245 compared AVX2 and AVX-512 single-thread, conventional fixed-partition and Recoil decoders, and GPU runs on an RTX 2080 Ti compared multians, conventional and Recoil CUDA decoders. Recoil matched conventional throughput (over 90 GB/s on the GPU) with lower partition overhead. The public harness (recoil-testscripts: gcc-10, CUDA 12.1, CMake Release with -O3 -march=native, ProbBits 11/16, multians built with NUM_STATES 1024/32768 from the lin-toto/multians fork) has no recorded numbers.

## Use it when

- Static-model or per-symbol-CDF rANS payloads (8- or 16-bit symbols, ProbBits 11 or 16) that one encoder writes and decoders of very different widths read, e.g. a 16-thread CPU and a GPU
- Bandwidth-sensitive delivery where split metadata should match the decoder: encode with many splits once, then reduce the split count per client
- GPU-resident bulk decode: the paper snippet reports over 90 GB/s on a Turing GPU (RTX 2080 Ti)
- Learned-image-compression style workloads with per-symbol distributions (the LIC examples 20-28)

## Skip it when

- Adaptive-model or context-mixing coding: the decoders take precomputed CDF/LUT offsets, with no adaptive model updates
- Non-x86 CPUs or CPUs without AVX2: RansSplitDecoder hard-wires the AVX2 or AVX-512 32x32 decoder, and the testscripts build.sh exits without AVX2
- Projects that cannot accept GPL-3.0 (copyleft for a header-only library means your binary is covered)
- Small inputs or single-threaded decode: hypersonic-rANS or htscodecs are simpler and faster per core, and Recoil's win is parallel scalability, not per-thread speed
- Production use without your own testing: no releases, no tests, no docs, last code change 2023-06-26

## How it is fast

It uses interleaved rANS (32 lanes) with SIMD decoders (RansDecoder_AVX2_32x32, RansDecoder_AVX512_32x32) and a CUDA decoder in which each warp lane is one rANS state; lanes share the bitstream pointer through __ballot_sync/__popc. Parallelism comes from split points: the encoder stores the state of each interleaved coder near a cut, and a split decoder starts there and runs 'sync' decodes (syncRansOnce) until all 32 lanes are initialised. Unlike conventional fixed partitioning, it does not need fresh coder states and flushes per partition. A heuristic picks split points to balance symbol counts (HeuristicSymbolCount) or bitstream length (EqualBitstreamLength).

## Compared with alternatives

Choose Recoil over multians when you control the encoder and want rANS with static or per-symbol CDFs, decoding on both CPU and GPU, and newer CUDA. The paper compares against multians on GPU and reports much higher throughput. Choose hypersonic-rANS or htscodecs instead for single-core CPU rANS speed or a maintained, permissively licensed codec, and torch_ans for PyTorch-integrated GPU rANS.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for CPU (pthread used by examples); CUDA 12+ for the GPU decoder |
| **Minimum toolchain** | C++20 (concepts, std::span), gcc 10+ or clang 14+, CMake 3.24+ for examples, CUDA 12+ |
| **Platforms** | x86-64 with AVX2 (AVX-512 optional via -DAVX512) for the split CPU decoder; NVIDIA GPUs (CMake default CUDA arch 70) for CUDA |
| **Thread safety** | not documented; RansSplitDecoder::decodeSplit writes disjoint ranges of a shared result vector, so different splitIds can run on separate threads, but one decoder object is not otherwise synchronised |
| **Drop-in for the baseline** | no |

## Gotchas

- The CPU split decoder picks AVX2 or AVX-512 at compile time through the AVX512 macro; the CMake build also adds -march=native, so binaries are not portable across CPUs
- The CUDA decoder static_asserts NInterleaved == 32, and its grid is metadata.splits.size() / (NThreads / NInterleaved) with integer division, so split counts that are not multiples of the warps per block look like they leave trailing splits unlaunched (not documented)
- RansSplitDecoderCuda::decodeAll times only the kernel with CUDA events; bitstream and CDF pool are copied to the GPU in the constructor and the result is copied back afterwards, so lastDuration excludes PCIe transfers
- The encoder buffers all symbols and every intermediate state (symbolBuffer, intermediateStates) before flushSplits, so encode memory grows with input size; there is no streaming encode
- Decoding past the end throws DecodingReachesEndException, and buffer or offset mismatches throw std::runtime_error, so exceptions must be enabled on the CPU path

## Known shortcomings

- Tier C: the harness is public (recoil-testscripts: gcc-10, CUDA 12.1, CMake Release) but the results xlsx is an empty template and the paper numbers ('over 90 GB/s on a Turing GPU') are snippet-only (arXiv blocked); baseline is single-thread/conventional rANS plus multians. GPL-3.0. Could reach B with paper access.
- 'Active' is overstated: code dormant since 2023-06-26, the only later commit adds a LICENSE (2026-07-12, PR #3 by another contributor). The CPU split decoder is hard-wired to AVX2/AVX-512 with -march=native; the CUDA grid uses integer division splits/(NThreads/32) so trailing splits may go unlaunched (undocumented); kernel-only timing leaves out PCIe copies; the encoder buffers the whole input. Paper setup from snippets only: Xeon W-3245 and RTX 2080 Ti.

## Caveats and trade-offs

Benchmark harness is public (recoil-testscripts: Dockerfile, build.sh, runall.sh, datasets rand_\*, dickens, webster, enwik8/9, div2k) but Recoil_ExperimentData.xlsx is an empty paste-in template, so no numbers are in any repo; paper numbers seen only as search snippets since arXiv/ACM are blocked here. Recoil's CPU throughput is only comparable to conventional parallel rANS; its win is lower metadata overhead and decoder-adaptive scalability, and the clear speed win is over multians and single-thread decoding. Baseline is off the zlib/zstd/lz4/brotli/xz list. GPL-3.0: copyable only under GPL terms. A verifier with arXiv access could raise it to B.

C++20 header-only library with CUDA support; GPL-3.0 copyleft; documentation 'TODO'. Test scripts and dataset in separate repo lin-toto/recoil-testscripts (submodules multians and recoil).

## Maintenance

The code has been dormant since 2023-06-26; the only later commit is a GPL-3.0 LICENSE added 2026-07-12 through PR #3 by another contributor. Usable research code with no open issues, but 'active' maintenance overstates it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now C.
- **Tier reason:** Public benchmark harness in lin-toto/recoil-testscripts (Dockerfile with gcc-10/CUDA 12.1, build.sh with CMake Release builds, testscripts/main.py) compares Recoil against single-thread and conventional interleaved rANS and the multians GPU decoder, but its results spreadsheet is an empty template and the peer-reviewed ICPP 2023 paper (arXiv, ACM, ar5iv blocked) was seen only via snippets ("over 90 GB/s on a Turing GPU"). Without readable numbers or a CPU model it cannot reach B or A; C pending paper access.
- **Verifier notes:** Metadata checked on github.com: GPL-3.0, 19 stars, 2 forks, last commit 2026-07-12 (LICENSE added), active. Not rejected: peer-reviewed paper with a public harness, tier C not D.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/lin-toto/recoil>
  - <https://github.com/lin-toto/recoil/commits>
  - <https://github.com/lin-toto/recoil-testscripts>
  - <https://raw.githubusercontent.com/lin-toto/recoil-testscripts/HEAD/Dockerfile>
  - <https://raw.githubusercontent.com/lin-toto/recoil-testscripts/HEAD/build.sh>
  - <https://raw.githubusercontent.com/lin-toto/recoil-testscripts/HEAD/runall.sh>
  - <https://raw.githubusercontent.com/lin-toto/recoil-testscripts/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/lin-toto/recoil-testscripts/HEAD/Recoil_ExperimentData.xlsx>
- **Sources the enricher read:**
  - <https://github.com/lin-toto/recoil>
  - <https://raw.githubusercontent.com/lin-toto/recoil/HEAD/README.md>
  - <https://raw.githubusercontent.com/lin-toto/recoil/HEAD/CMakeLists.txt>
  - <https://github.com/lin-toto/recoil/issues>
  - <https://github.com/lin-toto/recoil/commits/main>
  - <https://github.com/lin-toto/recoil/tree/main/include/recoil>
  - <https://github.com/lin-toto/recoil/tree/main/include/recoil/simd>
  - <https://github.com/lin-toto/recoil/tree/main/include/recoil/split>
  - <https://github.com/lin-toto/recoil/tree/main/include/recoil/cuda>
  - <https://github.com/lin-toto/recoil/tree/main/examples>
  - <https://github.com/lin-toto/recoil/tree/main/examples/01_combine_encoded_splits>
  - <https://raw.githubusercontent.com/lin-toto/recoil/HEAD/include/recoil/rans.h>
  - <https://raw.githubusercontent.com/lin-toto/recoil/HEAD/include/recoil/rans_decoder.h>
  - <https://raw.githubusercontent.com/lin-toto/recoil/HEAD/include/recoil/rans_encoder.h>
  - <https://raw.githubusercontent.com/lin-toto/recoil/HEAD/include/recoil/rans_coded_data.h>
  - <https://raw.githubusercontent.com/lin-toto/recoil/HEAD/include/recoil/split/rans_split_decoder.h>
  - <https://raw.githubusercontent.com/lin-toto/recoil/HEAD/include/recoil/split/rans_split_encoder.h>
  - <https://raw.githubusercontent.com/lin-toto/recoil/HEAD/include/recoil/cuda/rans_split_decoder_cuda.cuh>
  - <https://raw.githubusercontent.com/lin-toto/recoil/HEAD/examples/01_combine_encoded_splits/combine_encoded_splits.cpp>
  - <https://raw.githubusercontent.com/lin-toto/recoil-testscripts/HEAD/build.sh>
  - <https://raw.githubusercontent.com/lin-toto/recoil-testscripts/HEAD/runall.sh>
  - <https://raw.githubusercontent.com/lin-toto/recoil-testscripts/HEAD/Dockerfile>
  - <https://raw.githubusercontent.com/lin-toto/recoil-testscripts/HEAD/.gitmodules>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/lin-toto/recoil`) · [data/wave9/enrich/raw/github_com_lin_toto_recoil.json](../../../data/wave9/enrich/raw/github_com_lin_toto_recoil.json) (enrichment confidence 0.72)

</details>
