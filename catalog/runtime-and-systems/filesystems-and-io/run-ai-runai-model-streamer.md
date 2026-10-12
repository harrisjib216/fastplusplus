# Run:ai Model Streamer

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Concurrent C++ safetensors reader with a Python API that loads model weights to GPU faster than Hugging Face's safetensors loader.

| | |
|---|---|
| **Beats** | Hugging Face safetensors loader (mmap/read) and Tensorizer |
| **Claimed result** | GP3 SSD: 14.34 s at concurrency 16 vs 47.99 s for the safetensors loader (3.3x, derived from page data); concurrency 1 matches safetensors at 47.56 s. IO2 SSD: 7.53 s at concurrency 8 vs 47 s for safetensors (6.2x, derived from page data). S3: 4.88 s at concurrency 32 vs Tensorizer 37.36 s. vLLM ready time GP3 35.08 s vs 66.13 s, IO2 28.28 s vs 62.69 s. |
| **Workload** | Load Meta-Llama-3-8B (15 GB, single safetensors file) to one A10G GPU from cold start on AWS GP3 SSD, IO2 SSD and S3 with concurrent reads. |
| **Metric** | throughput |
| **Hardware** | AWS g5.12xlarge (4x A10G, one used); GP3 750 GB 1000 MiB/s, IO2 500 GB 4000 MiB/s |
| **Adoption** | 383 stars |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/dsx-ai-factory/model-streamer) · [benchmark](https://github.com/run-ai/runai-model-streamer/blob/master/docs/src/benchmarks.md) |

## Verdict

First-party benchmarks.md (Model Streamer 0.6.0, vLLM 0.5.5, CUDA 12.4, AWS g5.12xlarge with one A10G, cold cache) loaded the 15 GB Meta-Llama-3-8B safetensors file in 14.34 s at concurrency 16 versus 47.99 s for the HF safetensors loader on GP3 (3.3x, derived from page data; about 1.05 GB/s versus 0.31 GB/s, derived from page data), 7.53 s versus 47 s on IO2 (6.2x, derived from page data), and 4.88 s versus Tensorizer's 37.36 s from S3; vLLM time-to-ready fell from 66.13 s to 35.08 s on GP3. These numbers predate the io_uring/libaio engines in current code, and no benchmark scripts, CPU model or build flags are published.

## Use it when

- Cold-start loading of large single-file or sharded safetensors checkpoints from cloud block storage (EBS GP3/IO2-class) where one reader cannot saturate the volume.
- Loading weights directly from S3, GCS or Azure Blob without first copying to local disk, especially with multiple GPUs on NVLink using distributed streaming.
- vLLM or PyTorch inference servers that autoscale and need short time-to-ready on x86-64 Linux.
- Network file systems or virtiofs where per-filesystem queue depth tuning (RUNAI_STREAMER_FS_QUEUE_DEPTH="512,nfs=64") helps.

## Skip it when

- Mixture-of-experts checkpoints with tens of thousands of small tensors: issue #225 reports Qwen3-Next-80B (75,944 tensors, 162.7 GB) loading in 125.7 s versus 43.6 s with vLLM's default safetensors loader (2.9x slower) on a B200, from forced tensor clones and out-of-order delivery.
- Warm page cache or very fast local NVMe/tmpfs: the published wins are against throttled cold EBS volumes, and InstantTensor's table shows this streamer at 9.29 s versus 1.77 s for InstantTensor on 50 GB/s storage.
- Single-reader setups: at concurrency 1 it matched safetensors on GP3 (47.56 s vs 47.99 s), so the gain comes only from parallel reads.
- Non-PyTorch frameworks or non-safetensors formats (docs say PyTorch only), and aarch64 via pip (pip install is documented for x86_64).

## How it is fast

Reads are split into chunks (2 MiB default on file systems, 8 MiB on object stores) and issued concurrently, overlapping storage reads with host-to-GPU copies instead of mmap page faults or a serial read. Current versions pick a file-system strategy per host from io_uring_direct, io_uring_buffered, libaio_direct and a sync_buffered thread pool (default queue depth 512 for the async engines, 16 threads for the pool), with O_DIRECT where the mount supports it. Object storage uses many parallel ranged GETs (AWS CRT client, about 10 Gbit/s per client), and distributed mode has each rank read a slice and broadcast it over NCCL.

## Compared with alternatives

Pick it over fastsafetensors when weights sit in S3, GCS or Azure Blob or on throttled cloud block volumes and you want vLLM's built-in integration; prefer InstantTensor or fastsafetensors (GDS) for fast local NVMe or many-tensor MoE checkpoints, where this streamer was measured slower.

## Integration

| | |
|---|---|
| **Form** | module (pip wheel runai-model-streamer with a bundled C++ shared library; optional [s3], [gcs], [azure] backend packages) |
| **Dependencies** | PyTorch; libcurl4 and libssl for the C++ core; object-storage extras ship libstreamers3.so statically linked to libssl, libcrypto and libcurl; backend packages must match the core version exactly |
| **Minimum toolchain** | C++17, built with Bazel in -c opt (-O2) inside the project devcontainer; prebuilt wheels for x86_64 Linux |
| **Platforms** | Linux x86-64 (pip); aarch64 build config exists (-march=armv8-a+crc+crypto); io_uring and libaio engines probed at runtime with sync_buffered fallback |
| **Thread safety** | not documented for sharing one SafetensorsStreamer across threads; each streamer owns its OS reader threads, which close with the context manager |
| **Drop-in for the baseline** | partial: works as a vLLM load format, but direct users replace safe_open/load_file with a streaming iterator and must clone tensors they keep |

## Gotchas

- Yielded tensors live in a reused CPU (or, in distributed mode, device staging) buffer and may be overwritten under RUNAI_STREAMER_MEMORY_LIMIT or freed when the streamer closes; clone them if you keep them (issue #230 tracks owned tensors).
- Default CPU buffer cap is 40 GB in non-distributed mode; distributed streaming needs staging buffers of twice the largest tensor per device.
- Concurrency must be tuned per storage: the GP3 result plateaued at concurrency 4-16 (14.43-14.34 s) because the volume's 1 GiB/s limit was hit, while S3 kept improving up to 32.
- Distributed streaming is on by default for object storage to CUDA, and every rank must pass identical tensor_names; mixing S3 and file paths in one stream_files call is not allowed.

## Known shortcomings

- The repo moved to dsx-ai-factory/model-streamer. Current code has io_uring_direct, io_uring_buffered, libaio_direct and sync_buffered strategies; the benchmarks predate them (v0.6.0). Issue 225: Qwen3-Next-80B MoE (75,944 tensors) loads in 125.7 s against vLLM's default 43.6 s (2.9x slower) on a B200, from forced clones and out-of-order delivery.
- Repository renamed and moved to dsx-ai-factory/model-streamer on 2026-09-13; the old URL redirects. Benchmark has no public script and no CPU model, numbers from the 0.6.0 and vLLM 0.5.5 era (w11-seed-a, 2026-10-07).

## Caveats and trade-offs

First-party benchmark from 2024 versions (Model Streamer 0.6.0, vLLM 0.5.5, CUDA 12.4), CPU model and flags not stated, no benchmark scripts linked. The GP3 result hit the volume's 1 GiB/s cap, so it measures concurrency against a throttled disk. The InstantTensor-table figure (9.29 s vs 57.4 s) in the search record is not on this page and was dropped. The repository moved in September 2026 to dsx-ai-factory/model-streamer (the run-ai URL resolves there). The package is a Python SDK over a C++ core. Tier C.

C++ core with Python bindings; concurrency parameter must be tuned; also reads from S3.

## Maintenance

Actively maintained (commits through 2026-10-05, 383 stars, Apache-2.0), installable from PyPI as runai-model-streamer; the repo moved to dsx-ai-factory/model-streamer in September 2026 with the old URL redirecting.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party benchmarks.md compares Model Streamer with the HF safetensors loader and Tensorizer on GP3, IO2 and S3 with versions and AWS instance stated, but no benchmark code path, CPU model or build flags; first-party with partial methodology is C.
- **Verifier notes:** All GP3/IO2/S3/vLLM numbers verified in the Appendix tables of docs/src/benchmarks.md. Repo moved to github.com/dsx-ai-factory/model-streamer; orchestrator may want to update repo_url/id. Stars 383, Apache-2.0, last commit 2026-10-05 confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** public benchmark code; public benchmark script with hardware
- **Pages the verifier opened:**
  - <https://github.com/run-ai/runai-model-streamer/blob/master/docs/src/benchmarks.md>
  - <https://github.com/run-ai/runai-model-streamer>
  - <https://github.com/run-ai/runai-model-streamer/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/run-ai/runai-model-streamer/HEAD/README.md>
  - <https://raw.githubusercontent.com/dsx-ai-factory/model-streamer/HEAD/README.md>
  - <https://raw.githubusercontent.com/dsx-ai-factory/model-streamer/HEAD/docs/src/benchmarks.md>
  - <https://raw.githubusercontent.com/dsx-ai-factory/model-streamer/HEAD/docs/README.md>
  - <https://raw.githubusercontent.com/dsx-ai-factory/model-streamer/HEAD/docs/src/env-vars.md>
  - <https://raw.githubusercontent.com/dsx-ai-factory/model-streamer/HEAD/docs/src/installation.md>
  - <https://raw.githubusercontent.com/dsx-ai-factory/model-streamer/HEAD/docs/src/usage.md>
  - <https://raw.githubusercontent.com/dsx-ai-factory/model-streamer/HEAD/cpp/README.md>
  - <https://raw.githubusercontent.com/dsx-ai-factory/model-streamer/HEAD/cpp/.bazelrc>
  - <https://raw.githubusercontent.com/dsx-ai-factory/model-streamer/HEAD/cpp/posix_io/strategy/strategy.h>
  - <https://raw.githubusercontent.com/dsx-ai-factory/model-streamer/HEAD/cpp/posix_io/strategy/strategy.cc>
  - <https://raw.githubusercontent.com/dsx-ai-factory/model-streamer/HEAD/cpp/posix_io/engine_factory/engine_factory.cc>
  - <https://github.com/dsx-ai-factory/model-streamer>
  - <https://github.com/dsx-ai-factory/model-streamer/tree/master/cpp>
  - <https://github.com/dsx-ai-factory/model-streamer/tree/master/cpp/posix_io>
  - <https://github.com/dsx-ai-factory/model-streamer/tree/master/cpp/posix_io/strategy>
  - <https://github.com/dsx-ai-factory/model-streamer/issues>
  - <https://github.com/dsx-ai-factory/model-streamer/issues/225>
  - <https://github.com/dsx-ai-factory/model-streamer/releases>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/run-ai/runai-model-streamer`) · [data/wave11/enrich/raw/github_com_run_ai_runai_model_streamer.json](../../../data/wave11/enrich/raw/github_com_run_ai_runai_model_streamer.json) (enrichment confidence 0.75)

</details>
