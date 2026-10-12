# multians (massively parallel ANS decoding on GPUs)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Entropy coders](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `CUDA/C++` · `LGPL-3.0` · 🔴 abandoned

> CUDA research decoder for a single unpartitioned tANS bitstream; paper claims up to 17x over 64 CPU threads.

| | |
|---|---|
| **Beats** | 64-thread multicore CPU tANS decoder, a SIMD-based decoder and Zstandard's entropy codec |
| **Claimed result** | Snippet only (paper abstract via WebSearch): speedups of up to 17 over 64 CPU threads, up to 31 over a high-performance SIMD-based solution, and up to 39 over Zstandard's entropy codec. |
| **Workload** | GPU decoding of raw (unpartitioned) tANS-encoded streams using a self-synchronising overflow pattern; demo generates random 256-symbol data and compares GPU against multicore CPU decoding (ICPP 2019 paper, DOI 10.1145/3337821.3337888). |
| **Metric** | throughput |
| **Compiler and flags** | CUDA SDK 9+ (README); Makefile NVCC_FLAGS --std=c++14 -O3 -arch=sm_70 -Xcompiler=-pthread -D CUDA -D MULTI with ARCH = 61 gencode; paper's compiler versions not verified |
| **Adoption** | 30 stars |
| **Last commit** | 2019-07-26 |
| **Links** | [repository](https://github.com/weissenberger/multians) |

## Verdict

The ICPP 2019 paper's abstract, seen only as a search snippet, reports up to 17x over a 64-thread CPU decoder, up to 31x over a SIMD decoder and up to 39x over Zstandard's entropy codec. The GPU, CPU and compiler behind those numbers were not readable here because ACM DL is blocked. The repo prints only raw microsecond timings of GPU kernels against its own std::thread decoder on synthetic data and contains no zstd comparison.

## Use it when

- Research or prototyping on GPU entropy decoding, especially as the baseline that later work such as Recoil compares against
- You already have large single-stream tANS data (radix 2, one table, up to 256 symbols) and an NVIDIA GPU, and you cannot change the encoder to add partitions
- Data already resident in GPU memory: the demo times only the decode kernels, not the PCIe copies
- Studying self-synchronising speculative decoding; the same author's CUHD/gpuhd applies the idea to Huffman

## Skip it when

- Decoding zstd or FSE frames: the bit layout comes from the repo's own toy encoder and has no zstd format compatibility
- Anything that needs multiple tables, adaptive models, more than 256 symbols, rANS or byte-wise renormalisation (README: single table, b = 2 only)
- Production code: 5 commits, no tests beyond the demo's equality check, untouched since 2019-07-26, and an open build-failure issue (#1, 2020) left unanswered
- CPU-only or non-NVIDIA targets: only a CUDA implementation exists (the README says an OpenCL port 'should be straightforward' but none exists)
- Small inputs or latency-bound paths: kernel launches, a host-side sync loop and the prefix scan dominate short streams

## How it is fast

It decodes speculatively and relies on self-synchronisation. Each GPU thread starts decoding a small subsequence of input units (SUBSEQUENCE_SIZE 4) at a guessed state and bit offset and records a sync point (unit, bit, state, symbol count). Phase 1 synchronises subsequences within a thread block and phase 2 repeats a cross-block kernel until every block's start matches the previous block's end state. A thrust::exclusive_scan over per-subsequence symbol counts then gives output offsets, and phase 4 decodes again and writes the output in parallel.

## Compared with alternatives

Pick multians over the CPU coders (FiniteStateEntropy, hypersonic-rANS, htscodecs) only when the data is a single unpartitioned tANS stream that must be decoded on a GPU. For new GPU ANS work, Recoil (rANS, CPU and GPU, decoder-adaptive splits) is newer, maintained and reports higher throughput than multians. CUHD/gpuhd is the Huffman equivalent from the same author.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | CUDA toolkit 9+ (nvcc, thrust), pthreads; GNU/Linux per README |
| **Minimum toolchain** | C++14 (nvcc --std=c++14), CUDA SDK 9+, GPU compute capability 3.0+ |
| **Platforms** | Linux x86-64 with an NVIDIA GPU; the Makefile hard-codes ARCH = 61 plus -arch=sm_70 and must be edited |
| **Thread safety** | not documented; the decoder uses caller-allocated device buffers and auxiliary memory per call, so concurrent calls need separate buffers |
| **Drop-in for the baseline** | no |

## Gotchas

- Open issue #1 (Nov 2020): build fails with 'src/multians_output_buffer.cc:28:49: error: invalid use of array with unspecified bounds' on newer compilers; no fix in the repo
- Phase 2 is a do/while loop on the host that relaunches the kernel until all blocks report synchronised. It has no iteration cap, so a stream that synchronises slowly costs extra kernel launches and host round trips
- main.cc passes a hard-coded maximum codeword length of 11 to decode() and decodes output in reverse order (output_buffer-&gt;reverse() afterwards), matching the demo encoder only
- The demo's GPU timing covers decode kernels only: host-to-device copies of input and table, and the device-to-host copy of output, are outside TIMER_START/TIMER_STOP

## Known shortcomings

- Tier B on the ICPP 2019 paper (abstract snippet: up to 17x vs 64 CPU threads, 31x vs SIMD, 39x vs Zstandard's entropy codec); the repo demo compares only against its own multicore CPU decoder. LGPL-3.0, last commit 2019-07-26.
- Open issue #1 (Nov 2020, unanswered): the build fails with 'src/multians_output_buffer.cc:28:49: error: invalid use of array with unspecified bounds'. Demo GPU timing leaves out H2D/D2H copies; the phase-2 sync loop has no iteration cap; max codeword length 11 is hard-coded in main.cc; no zstd comparison in the repo; the paper hardware is unreadable (ACM blocked).

## Caveats and trade-offs

Paper (ACM DL) and its hardware tables were not reachable; speedups are from an abstract snippet and are 'up to' figures, so typical gains are lower and the CPU/GPU models behind them are unknown. The repo demo compares only against its own multicore CPU decoder on synthetic exponentially distributed 256-symbol data, not against Zstandard, so the Zstandard comparison cannot be reproduced from the repo. Decoder supports a single table, radix 2, up to 256 symbols. Makefile sets both ARCH = 61 gencode and -arch=sm_70. Last commit 2019-07-26.

Requires CUDA GPU with compute capability 3.0+; the README demo is a synthetic uniform 256-symbol test, not the paper's datasets.

## Maintenance

Abandoned since 2019-07-26 with an open, unanswered build issue; LGPL-3.0, and the five main source files total about 1.7k lines, so vendoring is feasible, but expect to patch it for current CUDA/GCC.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed ICPP 2019 paper (DOI 10.1145/3337821.3337888); WebSearch snippet of its abstract confirms up to 17x over 64 CPU threads, 31x over a SIMD decoder and 39x over Zstandard's entropy codec. The repo's demo only compares GPU against its own multicore CPU decoder, has no numbers and no stated hardware, so not A.
- **Verifier notes:** Repo exists, 30 stars, 4 forks, 5 commits, LGPL-3.0 confirmed from LICENSE, last commit 2019-07-26. Record metadata correct; only flags and caveats tightened.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/weissenberger/multians>
  - <https://github.com/weissenberger/multians/commits>
  - <https://raw.githubusercontent.com/weissenberger/multians/HEAD/README.md>
  - <https://raw.githubusercontent.com/weissenberger/multians/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/weissenberger/multians/HEAD/Makefile>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/weissenberger/multians/HEAD/README.md>
  - <https://raw.githubusercontent.com/weissenberger/multians/HEAD/Makefile>
  - <https://raw.githubusercontent.com/weissenberger/multians/HEAD/LICENSE>
  - <https://github.com/weissenberger/multians/tree/master/src>
  - <https://raw.githubusercontent.com/weissenberger/multians/HEAD/src/main.cc>
  - <https://raw.githubusercontent.com/weissenberger/multians/HEAD/src/multians_gpu_decoder.cu>
  - <https://raw.githubusercontent.com/weissenberger/multians/HEAD/src/multicore_decoder.cc>
  - <https://raw.githubusercontent.com/weissenberger/multians/HEAD/src/ans_encoder.cc>
  - <https://raw.githubusercontent.com/weissenberger/multians/HEAD/src/ans_table_generator.cc>
  - <https://github.com/weissenberger/multians/issues>
  - <https://github.com/weissenberger/multians/issues/1>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/weissenberger/multians`) · [data/wave9/enrich/raw/github_com_weissenberger_multians.json](../../../data/wave9/enrich/raw/github_com_weissenberger_multians.json) (enrichment confidence 0.7)

</details>
