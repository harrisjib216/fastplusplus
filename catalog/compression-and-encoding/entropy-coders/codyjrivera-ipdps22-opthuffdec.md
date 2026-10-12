# ipdps22-opthuffdec (optimized GPU Huffman decoders)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Entropy coders](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `CUDA/C++` · `no license` · 🔴 abandoned

> IPDPS 2022 artifact: optimized CUDA self-synchronizing and gap-array Huffman decoders, reported 3.64x faster than cuSZ's GPU Huffman decoder.

| | |
|---|---|
| **Beats** | cuSZ's native GPU Huffman decoder (plus the original self-sync and gap-array decoders) |
| **Claimed result** | Snippet only (paper abstract via WebSearch; arXiv 2201.09118 and the IEEE/NSF pages are blocked here): average 3.64x speedup over cuSZ's Huffman decoder and 2.43x average improvement of cuSZ's overall decompression, on an Nvidia V100 with eight scientific datasets. The 'above 100 GB/s' throughput figure could not be confirmed from any reachable source and is dropped. |
| **Workload** | Optimised self-synchronising and gap-array Huffman decoders for error-bounded lossy compression (IPDPS 2022), evaluated on Tesla V100 with cuSZ datasets. |
| **Metric** | throughput |
| **Hardware** | x86_64 CPU with Nvidia Tesla V100 32 GB (README) |
| **Compiler and flags** | GCC 8.3.1 and NVCC 11.1 (README); Makefiles in opt-self-sync/ and opt-gap-array/ use CFLAGS -std=c++17 -g -O3 -march=native and NVCC_FLAGS --std=c++14 -O3 with -gencode arch=compute_70,code=sm_70 |
| **Adoption** | 3 stars |
| **Last commit** | 2022-03-01 |
| **Links** | [repository](https://github.com/codyjrivera/ipdps22-opthuffdec) · [benchmark](https://github.com/codyjrivera/ipdps22-opthuffdec/blob/main/runcusz.sh) |

## Verdict

Per WebSearch snippets of the IPDPS 2022 abstract (paper not opened; arXiv, IEEE and NSF pages blocked), on an NVIDIA Tesla V100 32 GB with an unnamed x86_64 host, GCC 8.3.1 and NVCC 11.1 (-O3, sm_70), the optimized decoders averaged 3.64x faster Huffman decoding than cuSZ's native GPU decoder and 2.43x faster overall cuSZ decompression across eight scientific datasets (the repo's scripts run five: HACC, EXAALT, CESM, Nyx, Isabel, error bound 1e-3). A further snippet says shared-memory sizing alone moves throughput between 158 and 233 GB/s; the repo itself publishes no numbers.

## Use it when

- GPU decompression in cuSZ-style error-bounded lossy compressors, where the Huffman stage decodes 16-bit quantization codes (1,024-symbol alphabet) on an NVIDIA GPU.
- Building or benchmarking a GPU Huffman decoder: the repo puts both original decoders and both optimized ones behind the same harness on the same datasets.
- When you control the encoder and can store an extra gap byte per 128 bits of compressed data (opt-gap-array), or need plain Huffman streams decoded on the GPU without format changes (opt-self-sync).
- Large, mostly compressible inputs on Volta-class or newer GPUs, where decoding throughput rather than per-call latency matters.

## Skip it when

- Byte-oriented general-purpose compression or standard formats (Deflate, zstd, JPEG): symbols are 16-bit, codewords are capped at 14 bits, and the encoder is CUHD's own length-limited format.
- Production pipelines: research artifact, 5 commits ending 2022-03-01, editor lock and backup files committed (.#cuhd_gpu_decoder.cu, #cuhd_gather.h#), no tests beyond the demo's equality check, and cuSZ integration is left to the user.
- Small inputs or latency-sensitive calls: each decode() call allocates and frees its scratch buffers, runs a CUB sort and creates and destroys 9 CUDA streams.
- Non-NVIDIA or non-Linux targets: CUDA with CUB/Thrust only, Makefiles hard-code sm_70 and /usr/local/cuda, and the host code uses -march=native.
- If you need the orig-gap-array code under a license: that directory is the unlicensed Hiroshima University code and has no LICENSE file.

## How it is fast

Per the paper abstract (WebSearch snippet) and the code: decoded symbols are staged in shared memory and written to global memory from there, the shared-memory size is tuned online, memory access patterns are improved, and warp divergence is reduced. In opt-gap-array, an 8-bit gap per 4-unit (128-bit) subsequence removes the inter-block synchronization phase (phase 2 is empty); after an exclusive scan of per-subsequence symbol counts (Thrust), blocks are bucketed by compression ratio with a CUB radix sort and the final decode/write kernel is launched on 9 CUDA streams with shared buffers of 1,024 to 8,192 (or 3,584) 16-bit symbols per bucket. Lookup uses a 2^9-entry table cached in shared memory (cache_len 9).

## Compared with alternatives

Pick it over CUHD/gpuhd and Huffman_coding_Gap_arrays when you want the fastest of these GPU Huffman decoders for 16-bit quantization codes: it contains both and reports beating them as well as cuSZ. Pick FiniteStateEntropy's huff0 or PIVCO-Huffman for CPU byte-stream decoding, and multians or Recoil if you can switch from Huffman to ANS.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | CUDA toolkit with Thrust and CUB; cuSZ (separate build) and the SDRBench datasets (getdata.sh, via wget from a Globus endpoint) only for the paper's benchmark |
| **Minimum toolchain** | Tested with GCC 8.3.1 and NVCC 11.1 (README); Makefiles use -std=c++17 for host code and --std=c++14 for CUDA, arch sm_70 by default |
| **Platforms** | NVIDIA GPU (built for sm_70 by default; inherited CUHD README says compute capability 3.0+), Linux |
| **Thread safety** | not documented; decode() keeps global timing arrays and an invocation counter, so concurrent calls are not safe |
| **Drop-in for the baseline** | partial: it decodes the same cuSZ quantization codes, but the stream is encoded by its own CPU llhuff encoder (with a gap array for opt-gap-array), so cuSZ's Huffman format and code would have to be replaced, not linked against |

## Gotchas

- License is per directory: opt-self-sync, opt-gap-array and orig-self-sync carry LGPL-3.0 LICENSE files and CUHD headers ('released under LGPL-3.0'); the repo root and orig-gap-array have none.
- The demo maps any input symbol above 1024 to 0 before encoding and then checks the decoded output against that altered buffer, so arbitrary 16-bit files are silently changed (fine for cuSZ codes, not for general data).
- The demo's first 'throughput' line divides by wall time of the whole decode() call including allocations; the second sums per-phase times; both use 1024^3, so 'GB/s' is GiB/s.
- opt-self-sync/run.sh and opt-gap-array/run.sh are identical (both print 'best solution + self-synchronization'), CUSZ_DIR and DATA_DIR are empty and must be filled in, and \$shared_size is never set, so tuning is always online.

## Known shortcomings

- Tier B on the IPDPS 2022 paper, but the 3.64x vs the cuSZ Huffman decoder and 2.43x overall decompression figures are confirmed only from abstract snippets (hgpu.org, par.nsf.gov blocked); the '100 GB/s' claim is unconfirmed and dropped. No license, so reference; abandoned.
- License is not null: opt-self-sync, opt-gap-array and orig-self-sync carry LGPL-3.0 LICENSE files from CUHD while the root and orig-gap-array have none, so usability could be copyable with a copyleft note. The demo maps symbols above 1024 to 0 before encoding and checks against the altered buffer; decode() allocates and frees per call and builds 9 streams; the demo's 'GB/s' is GiB/s; the opt run.sh scripts are identical; editor backup files are committed. Snippet only: shared-memory sizing gives 158 vs 233 GB/s.

## Caveats and trade-offs

No LICENSE or COPYING file in the repo, so reference only. Numbers come from WebSearch snippets of the paper abstract; the repo README has no numbers and the paper PDF was unreachable (arXiv, IEEE, par.nsf.gov, hgpu.org blocked). Hardware is stated only as 'x86_64 CPU' plus a Tesla V100 32 GB. Baseline is cuSZ's GPU Huffman decoder, not a CPU library. Running the benchmark needs a separate cuSZ build and dataset download (getdata.sh). Last commit 2022-03-01.

Artifact repo for the paper; requires building cuSZ and downloading datasets via getdata.sh; run.sh scripts need local paths.

## Maintenance

Abandoned research artifact (last commit 2022-03-01, 3 stars); the optimized decoders are LGPL-3.0 per their directory LICENSE files, so they can be reused under copyleft terms, while orig-gap-array is unlicensed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed IPDPS 2022 paper (DOI 10.1109/IPDPS53621.2022.00075); two independent WebSearch snippets of its abstract state an average 3.64x speedup over cuSZ's Huffman decoder and 2.43x overall decompression. The artifact repo has the decoders, run.sh scripts and runcusz.sh baseline script with -O3 Makefiles, but no CPU model and no numbers, so not A.
- **Verifier notes:** Repo exists, 3 stars, 5 commits, last 2022-03-01, no license, not a fork. Metadata in record correct. runcusz.sh times cuSZ's own decompression on HACC, EXAALT, CESM, Nyx and Isabel at error bound 1e-3; benchmark_url set to that script since the record had none.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `benchmark_url`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/codyjrivera/ipdps22-opthuffdec>
  - <https://github.com/codyjrivera/ipdps22-opthuffdec/commits>
  - <https://raw.githubusercontent.com/codyjrivera/ipdps22-opthuffdec/HEAD/README.md>
  - <https://raw.githubusercontent.com/codyjrivera/ipdps22-opthuffdec/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/codyjrivera/ipdps22-opthuffdec/HEAD/opt-self-sync/Makefile>
  - <https://raw.githubusercontent.com/codyjrivera/ipdps22-opthuffdec/HEAD/opt-gap-array/Makefile>
  - <https://raw.githubusercontent.com/codyjrivera/ipdps22-opthuffdec/HEAD/runcusz.sh>
- **Sources the enricher read:**
  - <https://github.com/codyjrivera/ipdps22-opthuffdec>
  - <https://raw.githubusercontent.com/codyjrivera/ipdps22-opthuffdec/HEAD/README.md>
  - <https://raw.githubusercontent.com/codyjrivera/ipdps22-opthuffdec/HEAD/getdata.sh>
  - <https://github.com/codyjrivera/ipdps22-opthuffdec/tree/main/opt-gap-array>
  - <https://github.com/codyjrivera/ipdps22-opthuffdec/tree/main/opt-self-sync>
  - <https://github.com/codyjrivera/ipdps22-opthuffdec/tree/main/opt-gap-array/src>
  - <https://github.com/codyjrivera/ipdps22-opthuffdec/tree/main/opt-gap-array/include>
  - <https://raw.githubusercontent.com/codyjrivera/ipdps22-opthuffdec/HEAD/opt-gap-array/LICENSE>
  - <https://raw.githubusercontent.com/codyjrivera/ipdps22-opthuffdec/HEAD/opt-gap-array/README.md>
  - <https://raw.githubusercontent.com/codyjrivera/ipdps22-opthuffdec/HEAD/opt-gap-array/Makefile>
  - <https://raw.githubusercontent.com/codyjrivera/ipdps22-opthuffdec/HEAD/opt-gap-array/run.sh>
  - <https://raw.githubusercontent.com/codyjrivera/ipdps22-opthuffdec/HEAD/opt-gap-array/src/cuhd_gpu_decoder.cu>
  - <https://raw.githubusercontent.com/codyjrivera/ipdps22-opthuffdec/HEAD/opt-gap-array/src/demo.cc>
  - <https://raw.githubusercontent.com/codyjrivera/ipdps22-opthuffdec/HEAD/opt-gap-array/include/cuhd_constants.h>
  - <https://raw.githubusercontent.com/codyjrivera/ipdps22-opthuffdec/HEAD/opt-gap-array/include/cuhd_gpu_decoder.h>
  - <https://raw.githubusercontent.com/codyjrivera/ipdps22-opthuffdec/HEAD/opt-gap-array/include/cuhd_definitions.h>
  - <https://raw.githubusercontent.com/codyjrivera/ipdps22-opthuffdec/HEAD/opt-self-sync/LICENSE>
  - <https://raw.githubusercontent.com/codyjrivera/ipdps22-opthuffdec/HEAD/opt-self-sync/README.md>
  - <https://raw.githubusercontent.com/codyjrivera/ipdps22-opthuffdec/HEAD/opt-self-sync/Makefile>
  - <https://raw.githubusercontent.com/codyjrivera/ipdps22-opthuffdec/HEAD/opt-self-sync/run.sh>
  - <https://raw.githubusercontent.com/codyjrivera/ipdps22-opthuffdec/HEAD/opt-self-sync/src/cuhd_gpu_decoder.cu>
  - <https://raw.githubusercontent.com/codyjrivera/ipdps22-opthuffdec/HEAD/opt-self-sync/src/demo.cc>
  - <https://raw.githubusercontent.com/codyjrivera/ipdps22-opthuffdec/HEAD/orig-self-sync/LICENSE>
  - <https://raw.githubusercontent.com/codyjrivera/ipdps22-opthuffdec/HEAD/orig-self-sync/README.md>
  - <https://raw.githubusercontent.com/codyjrivera/ipdps22-opthuffdec/HEAD/orig-self-sync/Makefile>
  - <https://raw.githubusercontent.com/codyjrivera/ipdps22-opthuffdec/HEAD/orig-self-sync/run.sh>
  - <https://raw.githubusercontent.com/codyjrivera/ipdps22-opthuffdec/HEAD/orig-gap-array/README.md>
  - <https://raw.githubusercontent.com/codyjrivera/ipdps22-opthuffdec/HEAD/orig-gap-array/Makefile>
  - <https://raw.githubusercontent.com/codyjrivera/ipdps22-opthuffdec/HEAD/orig-gap-array/run.sh>
  - https://raw.githubusercontent.com/codyjrivera/ipdps22-opthuffdec/HEAD/orig-gap-array/LICENSE (404)
  - WebSearch: "Optimizing Huffman Decoding for Error-Bounded Lossy Compression on GPUs" shared memory compression ratio gap array self-synchronization GB/s V100 (snippets only)
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/codyjrivera/ipdps22-opthuffdec`) · [data/wave9/enrich/raw/github_com_codyjrivera_ipdps22_opthuffdec.json](../../../data/wave9/enrich/raw/github_com_codyjrivera_ipdps22_opthuffdec.json) (enrichment confidence 0.65)

</details>
