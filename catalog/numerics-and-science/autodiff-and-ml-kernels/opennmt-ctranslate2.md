# CTranslate2

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> C++ inference runtime for converted Transformer models; about 2.4-3.6x the CPU throughput of PyTorch-based translation.

| | |
|---|---|
| **Beats** | PyTorch 1.13.1 (OpenNMT-py, Hugging Face Transformers), TensorFlow 2.11.0 (OpenNMT-tf), Marian 1.11.0, FasterTransformer 5.3 (GPU) |
| **Claimed result** | CPU, OpenNMT-py WMT14 model: CTranslate2 3.6.0 658.8 tokens/s vs OpenNMT-py/PyTorch 275.8 (about 2.4x, derived from page data); int8 860.2 vs PyTorch int8 323.3. CPU, OPUS-MT model: CTranslate2 525.0 vs Transformers/PyTorch 147.3 (about 3.6x, derived) and vs Marian 344.5 (about 1.5x, derived). GPU, OPUS-MT model: 5876.4 vs Marian 3241.0 and Transformers/PyTorch 1022.9 tokens/s. GPU, OpenNMT-py model: fp32 CTranslate2 6634.7 vs FasterTransformer 5.3 at 6979.0 (CTranslate2 slower), but CTranslate2 float16 10990.7 vs FasterTransformer float16 8592.5. Max memory also lower (CPU OPUS-MT 721MB vs Marian 7605MB). |
| **Workload** | Translating the En-De newstest2014 test set with Transformer base models (OpenNMT-tf WMT14, OpenNMT-py WMT14, OPUS-MT/Marian); target tokens generated per second, aggregated over several runs, CPU with 4 threads and GPU. |
| **Metric** | throughput |
| **Hardware** | CPU: 4 threads on an AWS c5.2xlarge instance, Intel Xeon Platinum 8275CL. GPU: AWS g5.xlarge, NVIDIA A10G, driver 510.47.03, CUDA 11. |
| **Adoption** | 4.7k stars; on PyPI as ctranslate2 4.8.2 (2026-08-31); backend of faster-whisper |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/OpenNMT/CTranslate2) · [benchmark](https://github.com/OpenNMT/CTranslate2/blob/master/README.md) |

## Verdict

First-party README tables (CTranslate2 3.6.0, newstest2014 En-De, tokens/s excluding tokenization and model load) show 658.8 vs 275.8 tok/s against OpenNMT-py on PyTorch 1.13.1 and 525.0 vs 147.3 (Transformers) and 344.5 (Marian 1.11.0) on 4 threads of an AWS c5.2xlarge Xeon Platinum 8275CL; on an A10G (CUDA 11) float16 reaches 10990.7 vs FasterTransformer 5.3 float16 at 8592.5, while fp32 trails FasterTransformer. Docker-based scripts in tools/benchmark reproduce it, but no compiler flags are given and the table predates the current 4.8.x release.

## Use it when

- Serving a supported Transformer (MT models, Whisper speech recognition, small and mid-size LLMs) where PyTorch or TensorFlow inference is the incumbent and you want 2-4x more tokens/s on CPU.
- CPU-only translation on x86-64 or AArch64 with int8 weights: the README shows 860 tok/s int8 vs 324 tok/s for OpenNMT-py int8 on 4 Xeon threads.
- Embedding an inference engine in a C++ application without pulling in PyTorch (the project FAQ names this case), with control over intra/inter-op threads and memory.
- Batch or streaming jobs that can feed many batches concurrently: multiple replicas share weights on one device, and calls release the Python GIL.
- Memory-constrained deployments where int8/float16 quantization (4x smaller on disk) matters more than bit-exact output.

## Skip it when

- Training, fine-tuning or architectures not in the supported list: the FAQ says it only exports weights and re-implements the graph, so unsupported models cannot run.
- When you need a kernel-level win over oneDNN, cuBLAS or cuDNN: it calls those libraries, and the benchmarks compare whole frameworks, not kernels.
- GPU fp32 versus FasterTransformer: the README shows FasterTransformer 5.3 faster (6979 vs 6635 tok/s); open issues report Whisper encode about 4x slower than the OpenAI PyTorch reference (#1699) and bfloat16 GEMM slower than float16 (#2033).
- Large-scale LLM serving with paged KV cache and continuous batching: its features are batch reordering, async queues and tensor parallelism via MPI, not a serving scheduler.
- Loading untrusted model files on releases before 4.8.1/4.8.2, which fixed a model-load heap overflow and out-of-bounds reads.

## How it is fast

A hand-written graph per architecture with layer fusion, padding removal, batch reordering (sorting inputs by length within max_batch_size), in-place ops and caching allocators on CPU and GPU. Weights can be stored and computed in int8 (per-row scale, Wu et al. 2016), int16, float16, bfloat16 or AWQ int4, which also cuts memory (721MB vs Marian's 7605MB on the CPU OPUS-MT run). Matrix math is delegated late to Intel MKL (packed GEMM on Intel by default since 4.8.0), oneDNN, OpenBLAS, Ruy, Apple Accelerate or cuBLAS, with runtime ISA dispatch (AVX/AVX2/AVX512); dynamic vocabulary reduction (vmap) shrinks the output softmax for translation.

## Compared with alternatives

Pick it over FasterTransformer or LightSeq when you need CPU inference, an actively maintained engine, or a single C++/Python API across MT, Whisper and LLMs; pick FasterTransformer or ByteTransformer only for NVIDIA-GPU BERT/GPT pipelines already tuned around them. Kernel libraries such as LIBXSMM or FBGEMM sit below it and do not replace it.

## Integration

| | |
|---|---|
| **Form** | shared lib (static optional via BUILD_SHARED_LIBS=OFF); pip wheels and Docker images |
| **Dependencies** | One CPU BLAS backend: Intel MKL (default, &gt;= 2019.5), oneDNN &gt;= 3.0, OpenBLAS, Ruy or Apple Accelerate; optional CUDA &gt;= 11.0 (wheels need CUDA 12.x), cuDNN &gt;= 8 for convolutional models, ROCm/HIP, NCCL + MPI for tensor parallelism; pybind11 for the Python module |
| **Minimum toolchain** | C++17, CMake 3.15+ (per the install docs); Python &gt;= 3.9 for wheels |
| **Platforms** | x86-64 with SSE4.1 or newer, AArch64/ARM64; Linux, macOS, Windows; NVIDIA GPUs with compute capability &gt;= 3.5 (tensor cores need &gt;= 7.0); AMD ROCm wheels on the releases page |
| **Thread safety** | Translator/Generator are replica pools: concurrent translate/generate calls from multiple threads are supported and run on separate workers; load/unload/clear-cache methods on the pool are documented as not thread-safe |
| **Drop-in for the baseline** | partial — models must be converted to the CTranslate2 format and called through its own Translator/Generator API, but converters cover OpenNMT, Fairseq, Marian and Transformers checkpoints |

## Gotchas

- The runtime silently falls back to another compute type when the requested one is not optimized on the device (e.g. int16 runs as float16 on GPU, float16 runs as float32 on CPU); query get_supported_compute_types or set CT2_VERBOSE=1.
- Quantized outputs differ slightly from the original model (BLEU 26.77 to 26.64-26.85 in the README tables); int8 + vmap is the fastest CPU row but also the lowest BLEU.
- Keep inter_threads x intra_threads at or below the physical core count; the default intra_threads is 4 and async queues block once max_queued_batches is full.
- Open bug #1181: importing numpy after ctranslate2 can segfault; tensor-parallel Flan-T5 XXL gave unexpected output in #1691.

## Known shortcomings

- Table measured on 3.6.0 while the current release is 4.8.x; int8-vs-int8 gains are smaller; FasterTransformer fp32 beats CTranslate2 fp32 on GPU; baselines are frameworks, not kernels.
- Security: 4.8.1 fixed a model-load heap overflow (#2068) and 4.8.2 fixed StorageView out-of-bounds reads (#2073) plus allocation size checks (#2091, #2094), so untrusted models are unsafe before 4.8.2; open: Whisper encode \~4x slower than OpenAI PyTorch (#1699), numpy-import segfault (#1181).

## Caveats and trade-offs

First-party README numbers measured with CTranslate2 3.6.0 (the current release is 4.8.x, so the published table is stale) against PyTorch 1.13.1, TensorFlow 2.11.0, Transformers 4.26.1, Marian 1.11.0 and FasterTransformer 5.3; public Docker-based benchmark scripts in tools/benchmark, but no compiler or flags and prebuilt packages. Baselines are whole frameworks, not oneDNN, cuDNN, XNNPACK or Eigen kernels, so this does not show a kernel-level win over them. Like-for-like quantized comparisons are smaller than the headline: CPU int8 CTranslate2 860.2 vs OpenNMT-py int8 323.3 tok/s, and CTranslate2 int8 696.1 vs Marian int8 355.8 tok/s. FasterTransformer fp32 was faster than CTranslate2 fp32 on the GPU (6979.0 vs 6634.7 tok/s). The README itself warns relative performance changes with settings. Tokenization, detokenization and model loading are excluded from the timed region.

Supports a fixed list of Transformer architectures only (encoder-decoder, decoder-only LLM, encoder-only); models must first be converted to its own format; int8/int16/float16 quantization changes outputs slightly (BLEU 26.64 to 26.82 in the table); CPU backends are third-party (Intel MKL, oneDNN, OpenBLAS, Ruy); C++ and Python APIs.

## Maintenance

Actively maintained (4.8.2 released 2026-08-31 on PyPI, MIT-licensed, 4.7k stars, backend of faster-whisper); security fixes go to the latest release series only, so stay current.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README benchmark tables (CPU on c5.2xlarge Xeon Platinum 8275CL, GPU on g5.xlarge A10G) with public Docker-based scripts in tools/benchmark, but no compiler or flags (prebuilt packages), so not A; no independent or peer-reviewed source.
- **Verifier notes:** All claimed numbers match the README Benchmarks section. Metadata checked: MIT, 4.7k stars, not archived, last commit 2026-09-26.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/OpenNMT/CTranslate2/HEAD/README.md>
  - <https://github.com/OpenNMT/CTranslate2/tree/master/tools/benchmark>
  - <https://github.com/OpenNMT/CTranslate2>
  - <https://github.com/OpenNMT/CTranslate2/commits>
- **Sources the enricher read:**
  - <https://github.com/OpenNMT/CTranslate2>
  - <https://raw.githubusercontent.com/OpenNMT/CTranslate2/HEAD/README.md>
  - <https://raw.githubusercontent.com/OpenNMT/CTranslate2/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/OpenNMT/CTranslate2/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/OpenNMT/CTranslate2/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/OpenNMT/CTranslate2/HEAD/docs/installation.md>
  - <https://raw.githubusercontent.com/OpenNMT/CTranslate2/HEAD/docs/hardware_support.md>
  - <https://raw.githubusercontent.com/OpenNMT/CTranslate2/HEAD/docs/parallel.md>
  - <https://raw.githubusercontent.com/OpenNMT/CTranslate2/HEAD/docs/quantization.md>
  - <https://raw.githubusercontent.com/OpenNMT/CTranslate2/HEAD/docs/faq.md>
  - <https://raw.githubusercontent.com/OpenNMT/CTranslate2/HEAD/docs/performance.md>
  - <https://raw.githubusercontent.com/OpenNMT/CTranslate2/HEAD/docs/translation.md>
  - <https://raw.githubusercontent.com/OpenNMT/CTranslate2/HEAD/tools/benchmark/README.md>
  - <https://raw.githubusercontent.com/OpenNMT/CTranslate2/HEAD/include/ctranslate2/translator.h>
  - <https://raw.githubusercontent.com/OpenNMT/CTranslate2/HEAD/include/ctranslate2/replica_pool.h>
  - <https://pypi.org/pypi/ctranslate2/json>
  - <https://github.com/OpenNMT/CTranslate2/issues?q=is%3Aissue+is%3Aopen+label%3Abug>
  - <https://github.com/OpenNMT/CTranslate2/issues?q=is%3Aissue+slower>
  - <https://github.com/OpenNMT/CTranslate2/issues/1699>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/opennmt/ctranslate2`) · [data/wave8/enrich/raw/github_com_opennmt_ctranslate2.json](../../../data/wave8/enrich/raw/github_com_opennmt_ctranslate2.json) (enrichment confidence 0.85)

</details>
