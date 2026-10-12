# fastsafetensors

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python` · `Apache-2.0` · 🟢 active

> Python safetensors loader with a C++17 pybind11 core that replaces mmap with parallel pread/GDS reads into GPU memory.

| | |
|---|---|
| **Beats** | safetensors loader using mmap |
| **Claimed result** | ROCm nogds: 6.02 GB/s vs mmap 1.28 GB/s (4.7x) for GPT-2 Medium; 2.62 GB/s vs 1.01 GB/s (2.6x) for GPT-2; README: 4.8x-7.5x faster than default safetensors, 26.4 GB/s on Llama-70B with GDS |
| **Workload** | Load GPT-2 and larger models on AMD MI300X (ROCm, no GDS) with parallel threads and fixed buffers versus mmap; paper also reports Llama/Falcon/Bloom loads. |
| **Metric** | throughput |
| **Hardware** | 8x AMD Instinct MI300X |
| **Adoption** | 167 stars |
| **Last commit** | 2026-10-04 |
| **Links** | [repository](https://github.com/foundation-model-stack/fastsafetensors) · [benchmark](https://github.com/foundation-model-stack/fastsafetensors/blob/main/docs/amd-perf.md) |

## Verdict

On 8x AMD MI300X (ROCm, fastsafetensors 0.1.15, single-GPU loads, perf/fastsafetensors_perf/perf.py), the tuned nogds path loaded GPT-2 Medium (1.4 GB) at 6.02 GB/s vs 1.28 GB/s for safetensors mmap plus .to(device), and GPT-2 (523 MB) at 2.62 GB/s vs 1.01 GB/s; a cold-cache nogds run reached only 1.24 GB/s and mmap was not run cold. The 4.8x-7.5x and 26.4 GB/s (Llama-70B, 4 GPUs, GDS) figures come from the CLOUD 2025 paper, which was not opened.

## Use it when

- Cold-starting LLM inference servers (vLLM, SGLang) where weight loading from NVMe dominates startup time
- Multi-GPU tensor-parallel loads where CPU-side slicing of mmapped tensors is the bottleneck
- Nodes with GPUDirect Storage or hipFile (ROCm 7.2+) and fast NVMe or parallel file systems (3FS has a dedicated reader)
- AMD MI300X / ROCm without GDS: the nogds bounce-buffer path still beat mmap 2.6x-4.7x on the project's GPT-2 runs

## Skip it when

- Weights already in page cache or tmpfs: InstantTensor's sibling table shows fastsafetensors at 0.76x of plain safetensors there
- C++ applications that want a library to link: the C++ code is a pybind11 extension with no standalone C++ API
- Memory-constrained or unified-memory hosts that load checkpoints in a loop: issue #94 reports about 2x file size retained after close()
- Small models on CPU-only hosts, where thread and pinned-buffer setup costs are not repaid (not benchmarked by the project)
- When you need byte-identical, battle-tested loading on new hardware without validation: issue #38 reported corrupted gpt-oss-120b weights on DGX Spark through GdsFileCopier's alignment path (workaround noalign=True or nogds=True)

## How it is fast

It avoids mmap and demand paging: a fixed pool of std::thread workers issues large pread calls (O_DIRECT where available) into pinned bounce buffers, alternating two buffers and GPU streams per worker so disk reads overlap host-to-device copies. With GPU Direct Storage (cuFile on CUDA, hipFile on ROCm 7.2+, DirectStorage on Windows) data goes NVMe to GPU without host staging. Tensors are instantiated lazily via DLPack, and sharding (torch.distributed broadcast/scatter) and dtype conversion run on the GPU instead of the CPU.

## Compared with alternatives

Pick it over Run:ai Model Streamer when you want the loader already integrated into vLLM/SGLang with GDS and ROCm/hipFile support; pick InstantTensor instead if its 50 GB/s storage numbers (Qwen3-30B-A3B 1.77 s vs fastsafetensors 22.2 s) hold for your setup, and plain safetensors if weights are already cached.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Python 3.10-3.14, typer; build needs setuptools and pybind11; runtime PyTorch or Paddle; optional CUDA cuFile, ROCm hipFile, libnuma, DirectStorage DLLs, fastsafetensor-3fs-reader |
| **Minimum toolchain** | C++17 compiler (C++20 /std:c++20 on Windows MSVC), Python 3.10 |
| **Platforms** | Linux x86-64 with CUDA or ROCm; Windows (DirectStorage via CUDA interop); unified-memory systems such as DGX Spark; aarch64 wheels were missing per issue #82 |
| **Thread safety** | not documented; loader owns a fixed worker pool and must be closed after its buffers/iterators |
| **Drop-in for the baseline** | partial — vLLM/SGLang switch via a flag, but direct users must replace safe_open calls with the SafeTensorsFileLoader or fastsafe_open API |

## Gotchas

- Default owning tensors keep the whole file or chunk allocation alive: a small view can pin a large buffer; borrowed_tensors=True avoids that but tensors become invalid after close()
- Close the buffer or exhaust the ParallelLoader/AutoLoader iterator before loader.close(); loader.close() does not close an active iterator
- GDS registration failure silently falls back to the nogds bounce-buffer path with only a warning, so performance can drop without an error
- Bandwidth in perf.py is output tensor bytes over wall time, so F16 conversion runs report fewer bytes (0.77 GB/s) than the file size read

## Known shortcomings

- Issue 38: the GdsFileCopier alignment path broke gpt-oss-120b weights on DGX Spark (does not touch the nogds benchmark). Issue 94: about 2x file size stays in memory after close(). The F16 bandwidth in perf.py counts output bytes, so 0.77 GB/s understates the read rate. CLOUD 2025 paper not opened.

## Caveats and trade-offs

Peer-reviewed IEEE CLOUD 2025 paper (arXiv 2505.23072) was not opened (arXiv blocked); the README's 4.8x-7.5x and 26.4 GB/s figures are quoted from that paper. The ROCm table compares a tuned 'optimal' nogds config against default mmap on small GPT-2 models (523MB and 1.4GB, single GPU); the cold-cache nogds run reached only 1.24 GB/s and the F16 run 0.77 GB/s, and mmap was not tested cold. Host CPU model not stated. The DeepSeek-R1 vLLM result is an image only. Python package, not a C++ library.

Python library with native extension (not usable from C++ directly); avoids mmap and the page cache; advantage vanishes when the model is already cached (InstantTensor's table shows 0.76x vs safetensors on tmpfs).

## Maintenance

Actively maintained (version 0.4.0, Apache-2.0, 167 stars, commits into October 2026) and pip-installable, but it is a Python package for PyTorch/Paddle loaders rather than a C++ library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** docs/amd-perf.md has first-party tables from perf/fastsafetensors_perf/perf.py: GPT-2 Medium nogds 6.02 GB/s vs mmap 1.28 GB/s, GPT-2 best config 2.62 GB/s vs mmap 1.01 GB/s on 8x MI300X; no host CPU model or build flags, and the CLOUD 2025 paper could not be opened, so C.
- **Verifier notes:** Numbers match docs/amd-perf.md and README lines 11-13. If the paper becomes reachable it could support tier B.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/foundation-model-stack/fastsafetensors>
  - <https://github.com/foundation-model-stack/fastsafetensors/commits/main>
  - <https://raw.githubusercontent.com/foundation-model-stack/fastsafetensors/HEAD/docs/amd-perf.md>
  - <https://raw.githubusercontent.com/foundation-model-stack/fastsafetensors/HEAD/README.md>
  - <https://raw.githubusercontent.com/foundation-model-stack/fastsafetensors/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/foundation-model-stack/fastsafetensors>
  - <https://raw.githubusercontent.com/foundation-model-stack/fastsafetensors/HEAD/README.md>
  - <https://raw.githubusercontent.com/foundation-model-stack/fastsafetensors/HEAD/docs/amd-perf.md>
  - <https://raw.githubusercontent.com/foundation-model-stack/fastsafetensors/HEAD/docs/overview.md>
  - <https://raw.githubusercontent.com/foundation-model-stack/fastsafetensors/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/foundation-model-stack/fastsafetensors/HEAD/setup.py>
  - <https://raw.githubusercontent.com/foundation-model-stack/fastsafetensors/HEAD/perf/fastsafetensors_perf/perf.py>
  - <https://raw.githubusercontent.com/foundation-model-stack/fastsafetensors/HEAD/fastsafetensors/cpp/ext.cpp>
  - <https://raw.githubusercontent.com/foundation-model-stack/fastsafetensors/HEAD/fastsafetensors/cpp/ext.hpp>
  - <https://raw.githubusercontent.com/foundation-model-stack/fastsafetensors/HEAD/fastsafetensors/loader.py>
  - <https://github.com/foundation-model-stack/fastsafetensors/issues?q=is%3Aissue>
  - <https://github.com/foundation-model-stack/fastsafetensors/issues/38>
  - <https://github.com/foundation-model-stack/fastsafetensors/issues/94>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/foundation-model-stack/fastsafetensors`) · [data/wave11/enrich/raw/github_com_foundation_model_stack_fastsafetensors.json](../../../data/wave11/enrich/raw/github_com_foundation_model_stack_fastsafetensors.json) (enrichment confidence 0.7)

</details>
