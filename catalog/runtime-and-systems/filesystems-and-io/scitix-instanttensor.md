# InstantTensor

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> C++/Python safetensors-to-GPU loader using O_DIRECT io_uring/AIO plus NCCL all-gather; beats the safetensors loader on cold loads.

| | |
|---|---|
| **Beats** | safetensors loader (mmap-based file read to GPU); also compared with fastsafetensors and Run:ai Model Streamer |
| **Claimed result** | 50GB/s storage: Qwen3-30B-A3B 1.77 s vs safetensors 57.4 s (32.4x), fastsafetensors 22.2 s, RMS 9.29 s; DeepSeek-R1 15.3 s vs 160 s (10.5x). tmpfs: 1.26 s vs 12.7 s (10.1x) and 12.1 s vs 22.6 s (1.87x) |
| **Workload** | Load Qwen3-30B-A3B (61 GB) on 1 H200 and DeepSeek-R1 (689 GB) on 8 H200 from 50 GB/s storage using direct I/O with tuned io_uring/AIO concurrency; also tmpfs. |
| **Metric** | throughput |
| **Hardware** | H200 GPUs, 50 GB/s storage; tmpfs testbed 2 NUMA nodes x 8 channels DDR5; CPU model not stated |
| **Adoption** | 83 stars |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/scitix/InstantTensor) · [benchmark](https://github.com/scitix/InstantTensor/blob/main/docs/benchmark.md) |

## Verdict

First-party docs/benchmark.md (instanttensor 0.1.4 vs safetensors 0.7.0, fastsafetensors 0.2.2, Run:ai Model Streamer 0.15.6) on H200 GPUs: from 50 GB/s storage, Qwen3-30B-A3B (61 GB, 1 GPU) loads in 1.77 s vs 57.4 s (32.4x) and DeepSeek-R1 (689 GB, 8 GPUs, TP=8/EP=8, time to slowest rank) in 15.3 s vs 160 s (10.5x); on tmpfs, 1.26 s vs 12.7 s (10.1x) and 12.1 s vs 22.6 s (1.87x). The CPU model, compiler flags and cache-drop procedure are not stated; tests/test.py is the harness.

## Use it when

- Cold-start loading of large LLM checkpoints (tens to hundreds of GB) onto GPUs from storage of 5 GB/s or more (README's own threshold)
- Multi-GPU tensor/expert-parallel serving (e.g. TP=8) where every rank would otherwise read the whole checkpoint
- Hosts whose RAM is reserved for KV-cache offload or that switch models often, so the page cache cannot hold the model
- Loading from tmpfs to GPU, where its mmap path measured 10.1x over safetensors for a 61 GB model on one H200
- vLLM deployments, via its documented InstantTensor loader integration

## Skip it when

- Warm page cache and repeated reloads of the same model: Direct I/O ignores cached pages; switch to BackendPolicy.BUFFERED or keep the default loader
- Slow storage (single SATA SSD, network disk under \~5 GB/s): the gap shrinks; issue #1 reported small gains for Qwen3-8B/32B on an H20
- CPU-only loading, Windows or macOS: GPU (CUDA/ROCm), Linux and PyTorch &gt;= 2.8 are required; io_uring backends need kernel 5.6+
- Code that needs random-access get_tensor(name) or collects tensors before use with copy=False
- Tight GPU memory: the device ring buffer may take up to INSTANTTENSOR_MAX_FREE_MEM_USAGE (default 0.5) of free GPU memory; issue #13 reports a draft-model load failing on allocation

## How it is fast

Reads bypass the page cache with Direct I/O (O_DIRECT) through io_uring (registered fixed files and fixed buffers, io_uring_prep_read_fixed) or libaio, with chunk size and queue depth tuned per backend, into a cudaHostRegister-pinned staging buffer. Chunks are pipelined: host read, cudaMemcpyAsync to the device on one stream, and on multi-GPU loads each rank reads only its 1/world_size slice of a chunk and ncclAllGather assembles the rest on a second stream, so 8 GPUs share the storage bandwidth instead of each reading the full model. tmpfs files use an mmap backend with worker threads.

## Compared with alternatives

Pick it over fastsafetensors or Run:ai Model Streamer when loading large checkpoints on 1-8 GPUs from very fast storage or tmpfs: its own table shows 1.77 s vs 22.2 s (fastsafetensors) and 9.29 s (Model Streamer) for Qwen3-30B-A3B. Model Streamer remains the choice for S3/object-storage sources, which InstantTensor does not support yet (issue #15).

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | PyTorch &gt;= 2.8, CUDA or ROCm runtime, NCCL (via torch.distributed); vendored static liburing, libaio, pybind11, dlpack and atomic_queue; optional cuFile (GPUDirect Storage) |
| **Minimum toolchain** | C++17 extension built by setuptools; Python &gt;= 3.9; Linux kernel 5.6+ for io_uring (5.15+ recommended) |
| **Platforms** | Linux x86-64 with NVIDIA (CUDA) or AMD (ROCm) GPUs |
| **Thread safety** | not documented; one safe_open context per process or process group, with internal loader threads |
| **Drop-in for the baseline** | partial — same safe_open(...) entry point and framework='pt' as safetensors, but streaming tensors() iteration instead of keys()/get_tensor(), and different lifetime rules |

## Gotchas

- With copy=False, tensors are views into a ring buffer: consume each before the next is yielded and do not keep references after the with block; list(f.tensors()) silently corrupts data when buffer_size &lt; total_tensor_size (issue #9, now warned about at runtime). The default is copy=True.
- Default backend order for disk files is [URING, AIO] with O_DIRECT; buffered mode must be requested explicitly with backend=BackendPolicy.BUFFERED or INSTANTTENSOR_BACKEND=BUFFERED.
- Pinned staging memory scales as round_up(chunk_size, page_size) \* io_depth \* world_size; INSTANTTENSOR_CACHE_BUFFER=1 keeps it pinned for the life of the process.
- In tests/test.py the safetensors baseline loads each tensor to CPU and copies it to the GPU, and every rank reads the full checkpoint; the harness does not drop the page cache itself, so cold-cache conditions depend on the operator.

## Known shortcomings

- The test.py safetensors baseline loads to CPU and then copies to the GPU, every rank reads the full model, and the harness does not drop caches. Issue 9: copy=False ring-buffer corruption (fixed with a warning; default copy=True); issue 1: small gains on H20.

## Caveats and trade-offs

First-party benchmark. CPU model and compiler flags are not given, so tier C; the README names tests/test.py as the full benchmark harness. The baseline is the safetensors Python loader, not a raw POSIX read loop. On tmpfs the DeepSeek-R1 gain shrinks to 1.87x, and fastsafetensors and RMS are slower than plain safetensors there. With copy=False, list(f.tensors()) silently corrupts data when buffer_size &lt; total_tensor_size (README warning). A repo (123123213weqw/siphon) republishes the identical table and is not reported separately.

C++ core with Python API aimed at PyTorch/GPU loading; direct I/O makes warm-cache loads slower than page-cache-based loaders; needs very fast storage to show the gain.

## Maintenance

Active (version 0.2.1 on PyPI, last commit 2026-10-05, 83 stars, used by vLLM), Apache-2.0 and copyable, though the package is marked Development Status Alpha and several closed issues were silent-corruption and lifetime bugs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** docs/benchmark.md has first-party tables against safetensors 0.7.0, fastsafetensors 0.2.2 and Run:ai Model Streamer 0.15.6; every claimed number matches. The README points to tests/test.py as the benchmark harness, but CPU model and compiler flags are not stated, so not A.
- **Verifier notes:** All 50 GB/s and tmpfs numbers match docs/benchmark.md exactly. Apache-2.0 LICENSE confirmed. I did not check the star count (83).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** public benchmark code
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/scitix/InstantTensor/HEAD/docs/benchmark.md>
  - <https://raw.githubusercontent.com/scitix/InstantTensor/HEAD/README.md>
  - <https://raw.githubusercontent.com/scitix/InstantTensor/HEAD/LICENSE>
  - <https://github.com/scitix/InstantTensor/commits>
- **Sources the enricher read:**
  - <https://github.com/scitix/InstantTensor>
  - <https://raw.githubusercontent.com/scitix/InstantTensor/HEAD/README.md>
  - <https://raw.githubusercontent.com/scitix/InstantTensor/HEAD/docs/benchmark.md>
  - <https://raw.githubusercontent.com/scitix/InstantTensor/HEAD/setup.py>
  - <https://raw.githubusercontent.com/scitix/InstantTensor/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/scitix/InstantTensor/HEAD/tests/test.py>
  - <https://raw.githubusercontent.com/scitix/InstantTensor/HEAD/csrc/loader_io_uring.cpp>
  - <https://raw.githubusercontent.com/scitix/InstantTensor/HEAD/csrc/loader_common.cpp>
  - <https://github.com/scitix/InstantTensor/issues?q=is%3Aissue>
  - <https://github.com/scitix/InstantTensor/issues/9>
  - <https://github.com/scitix/InstantTensor/issues/1>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/scitix/instanttensor`) · [data/wave11/enrich/raw/github_com_scitix_instanttensor.json](../../../data/wave11/enrich/raw/github_com_scitix_instanttensor.json) (enrichment confidence 0.8)

</details>
