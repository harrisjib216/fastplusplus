# ONNX Runtime (transformers GPU inference, BERT and GPT-2)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Microsoft's ONNX inference runtime; its fused transformer graphs ran BERT/GPT-2 1.2-5.7x faster than TorchScript 1.5.1 on V100.

| | |
|---|---|
| **Beats** | PyTorch 1.5.1 eager fp32 (GPT-2 rows) and TorchScript fp32 at batch 1 (BERT rows); PyTorch fp16 never measured |
| **Claimed result** | BERT-base, batch 1, fp32: onnxruntime 1.4.0 1.38 ms vs torchscript 1.5.1 7.92 ms at s=8 (5.7x, derived from page data), 3.11 vs 9.56 ms at s=128 (3.1x, derived from page data), 10.74 vs 12.83 ms at s=512 (1.2x, derived from page data); ORT fp16 1.45 ms at s=128 (6.6x vs the torchscript fp32 row, derived from page data). GPT-2, batch 1, fp32: 1.42 vs 5.80 ms at s=4 (4.1x, derived from page data). |
| **Workload** | Average per-inference latency in milliseconds of BERT-base (bert-base-uncased, BertModel, input_ids only) and GPT-2 (GPT2LMHeadModel with past state) on a Tesla V100, batch sizes 1 and 4 (BERT) and 1 to 128 (GPT-2), sequence lengths 8 to 512 (BERT) and 4 to 128 (GPT-2), ORT with graph optimizer script and IO binding. |
| **Metric** | latency |
| **Hardware** | Tesla V100-PCIE-16GB GPU, CPU Intel Xeon E5-2690 v4 |
| **Compiler and flags** | Not built from source: prebuilt onnxruntime-gpu 1.4.0 against PyTorch 1.5.1 TorchScript, so no compiler or flags; CUDA, cuDNN and driver versions are not stated. Stated settings: IO binding enabled, ORT transformer optimizer script (graph fusion), fp32 and fp16 ORT rows, run through run_benchmark.sh (benchmark.py) and the benchmark_gpt2.py commands printed in the README; the script commit behind the 2020 table is not pinned. |
| **Adoption** | 22.0k stars; Microsoft project |
| **Last commit** | 2026-10-10 |
| **Links** | [repository](https://github.com/microsoft/onnxruntime) · [benchmark](https://github.com/microsoft/onnxruntime/blob/main/onnxruntime/python/tools/transformers/README.md) |

## Verdict

Microsoft's 2020 README table: on a Tesla V100-PCIE-16GB with a Xeon E5-2690 v4, prebuilt ORT 1.4.0 with the transformer optimizer and IO binding averaged 1.38, 3.11 and 10.74 ms for BERT-base (input_ids only, batch 1) at s=8, 128 and 512 against TorchScript 1.5.1 fp32 at 7.92, 9.56 and 12.83 ms (5.7x, 3.1x, 1.2x), and 1.42 vs 5.80 ms for one GPT-2 decoding step with past length 4. No CUDA, cuDNN or driver versions or script commit are given, and both columns come from unsynchronized back-to-back loops.

## Use it when

- Serving exported BERT-family encoders (BERT, DistilBERT, RoBERTa, ALBERT) or GPT-2-style decoders on NVIDIA GPUs at small batch and short sequences, where framework dispatch dominates latency.
- Deploying one model to several back ends (CPU, CUDA, TensorRT, DirectML, OpenVINO, QNN) from a C or C++ application without a Python runtime.
- fp16 inference on Tensor Core GPUs (V100, T4) via the optimizer's float16 option, after checking accuracy on your data.
- Teams already exporting to ONNX who want graph fusion without writing custom CUDA kernels.

## Skip it when

- Long sequences or large batches that are GPU-compute bound: the published gap falls to 1.2x at s=512, batch 1, and no batch-4 TorchScript row exists.
- Architectures outside the tested list (BERT, DistilBERT, DistilGPT2, RoBERTa, ALBERT, GPT-2, TF BERT): fusions need an exact subgraph match, and the README warns such models may be only partly optimized or not at all.
- If you can use a modern PyTorch stack (torch.compile, CUDA graphs, SDPA attention): the table predates all of them, so the current gap is unmeasured.
- Environments that must not send usage data: docs/Privacy.md says telemetry is ON by default in official builds (1DS on Linux, macOS, Android, iOS; ETW on Windows).
- Workloads needing one session shared by many threads on the CUDA EP with 1.14.x: issue #15154 (memory pattern with multiple streams) broke this until PR #15426 (April 2023).

## How it is fast

Subgraph pattern-matching fusion: the optimizer replaces embedding + LayerNorm, the whole multi-head attention block, Add + LayerNorm and bias + GELU with single fused kernels (EmbedLayerNormalization, Attention, SkipLayerNormalization, BiasGelu/FastGelu), which cuts kernel count and per-op dispatch cost. The C++ executor dispatches the graph without Python or TorchScript interpreter overhead, IO binding removes host-device copies, and an optional fp16 conversion uses Tensor Cores. The flat TorchScript row (7.92 ms at s=8 to 9.56 ms at s=128) suggests most of the small-shape gain is dispatch overhead removed, not faster GPU math.

## Compared with alternatives

Pick ONNX Runtime when you need a vendor-neutral runtime for exported ONNX graphs with C/C++/C#/Java/JS bindings and several execution providers; FasterTransformer and ByteTransformer claim larger BERT gains from hand-fused NVIDIA kernels but cover fewer models and platforms, CTranslate2 fits Transformer translation and generation models better, and OpenVINO is the Intel-CPU choice.

## Integration

| | |
|---|---|
| **Form** | shared lib (prebuilt onnxruntime / onnxruntime-gpu packages, or a CMake build from source) |
| **Dependencies** | CUDA toolkit and cuDNN for the CUDA EP (versions not documented in the files read); the transformer optimizer and benchmarks need Python with onnx, transformers and PyTorch for export |
| **Minimum toolchain** | Building from source: C++20, GCC 11.1+, CMake 3.28+ (cmake/onnxruntime_language_standard_versions.cmake and CMakeLists.txt); applications can link through the C API |
| **Platforms** | Windows, Linux, macOS, Android, iOS and WebAssembly per docs/Privacy.md; the measured path here is x86-64 Linux with an NVIDIA GPU |
| **Thread safety** | Not stated in the files read; issue #15154 reports a CUDA EP data race when threads share one session in 1.14.x, fixed by PR #15426 (workaround: enable_mem_pattern=False) |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: neither engine's timing loop synchronizes the GPU. benchmark.py times TorchScript with timeit around inference(input_ids) and no torch.cuda.synchronize, and in ORT 1.4.0 run_with_iobinding with GPU-bound outputs returns without a stream sync (InferenceSession::Run(IOBinding) leaves SynchronizeInputs commented out; the CUDA EP's OnRunEnd only records an event). The 'average latency' columns are back-to-back pipelined time per call over 1000 calls, not single-request latency.
- GPT-2 baseline label: the README's printed benchmark_gpt2 commands do not pass --torchscript (default False; the v1.4.0 script had no TorchScript option and loaded the model with torchscript=False), so they time eager PyTorch, not the 'torchscript 1.5.1' the table names. The script never runs PyTorch in fp16 ('This script does not support float16 for PyTorch'), so the GPT-2 fp16 rows are ORT fp16 against PyTorch fp32.
- Selective rows: run_benchmark.sh (both at v1.4.0 and today) runs TorchScript in the GPU fp16 loop and at batch sizes 1 and 4, yet the README publishes only TorchScript fp32 batch 1, so the 6.6x fp16 figure is against fp32 while an fp16 TorchScript result would have been produced. The v1.4.0 script's model list (bert-base-cased, roberta-base, gpt2) also does not match the table's bert-base-uncased.
- fp16 conversion is lossy: the v1.4.0 validation accepted rtol 5e-2 and atol 1e-1 for fp16 against 1e-4 for fp32; fusions silently fall back to unfused ops when the exported graph layout differs.

## Known shortcomings

- Downgraded A to C: first-party Microsoft README table on prebuilt 1.4.0 and PyTorch 1.5.1 wheels, no CUDA, cuDNN or driver versions, benchmark script commit unpinned; TorchScript baseline only at batch 1; fp16 ORT compared with fp32 TorchScript although benchmark.py supports TorchScript fp16; 2020-era data.
- Enricher: neither timing loop syncs the GPU (benchmark.py times TorchScript via timeit without torch.cuda.synchronize; ORT 1.4.0 run_with_iobinding returns without stream sync, SynchronizeInputs commented out and the CUDA EP OnRunEnd only records an event), so the latency columns are pipelined time per call, and the TorchScript row is flat at 7.92-9.56 ms from s=8 to s=128 (host-dispatch bound). The GPT-2 'torchscript 1.5.1' row comes from README commands without --torchscript (default False; the v1.4.0 script had no TorchScript option), so eager PyTorch fp32 was measured; the script never runs PyTorch fp16, while run_benchmark.sh also produces unpublished TorchScript fp16 and batch-4 rows; the v1.4.0 model list does not match the table. Telemetry on by default in official builds (docs/Privacy.md); CUDA EP shared-session thread bug #15154 fixed by PR #15426.

## Caveats and trade-offs

Numbers are from ORT 1.4.0 and PyTorch 1.5.1 (2020 era); newer PyTorch (torch.compile, SDPA kernels) and newer ORT are not in the table, so the gap today is unknown. The baseline is TorchScript only (no TensorRT, no PyTorch eager row), and TorchScript appears only at batch 1; the batch 4 (BERT) and batch 8-128 (GPT-2) rows are ORT-only. The advantage shrinks to 1.2x at s=512 batch 1. The fp16 rows are ORT fp16 against the TorchScript fp32 row; the current benchmark.py can run TorchScript in fp16 (model.half(), '-e torchscript -g -p fp16') but the table shows no such row, so the 6.6x fp16 figure compares unequal precisions. The README table is for bert-base-uncased while the current run_benchmark.sh default model list is bert-base-cased, roberta-base and distilbert-base-uncased with sequence lengths up to 1024, so the exact script version behind the table is not pinned. First-party (Microsoft) measurement on prebuilt packages with no CUDA/cuDNN/driver versions. The README states the results were obtained with the optimizer and IO binding enabled. Weak independent corroboration (not used for the tier): ELS-RD/transformer-deploy (Apache-2.0, 1.7k stars) README reports ONNX Runtime FP32 below PyTorch FP32 latency on an RTX 3090 (MiniLM-L6 classification 1.57 vs 5.43 ms; gpt2 4.99 vs 9.43 ms) with no batch size or versions, and its question-answering block duplicates the token-classification numbers exactly. [retier] No GPU sync in either timing loop (ORT 1.4.0 run_with_iobinding, timeit for TorchScript); TorchScript row flat 7.92-9.56 ms across sequence lengths (host-dispatch bound); unpublished TorchScript fp16 and batch-4 rows; v1.4.0 model list does not match the table; telemetry on by default in official builds.

Needs a model export to ONNX and ORT's transformer optimizer (subgraph pattern matching: the README says layout changes or untested architectures may be only partly optimized). Supported list in the README: BERT, DistilBERT, DistilGPT2, RoBERTa, ALBERT, GPT-2 (PyTorch) and BERT (TensorFlow). Many execution providers and bindings (C, C++, Python, C#, Java, JS), larger binary than a plain PyTorch install.

## Maintenance

Actively maintained (VERSION_NUMBER 1.32.0, last commit 2026-10-10, 22.1k stars) and MIT-licensed, but the benchmark table is six years old (ORT 1.4.0 against PyTorch 1.5.1) and its harness flaws make the speedups historical and directional rather than a current measurement.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now C.
- **Tier reason:** First-party Microsoft README table (onnxruntime/python/tools/transformers/README.md) with public driver scripts (run_benchmark.sh, benchmark.py, models/gpt2/benchmark_gpt2.py) and stated GPU/CPU (Tesla V100-PCIE-16GB, Xeon E5-2690 v4), but both engines are prebuilt packages (onnxruntime-gpu 1.4.0, PyTorch 1.5.1) with no CUDA, cuDNN or driver version and no pinned script commit, so it is not A; same treatment as CTranslate2 and other prebuilt-wheel entries (C).
- **Verifier notes:** All quoted numbers and derived ratios match the README tables (5.7x, 3.1x, 1.2x, 6.6x fp16-vs-fp32, GPT-2 4.1x). Downgraded A to C: first-party run on prebuilt wheels without CUDA/cuDNN versions or a pinned script commit; shortcomings to record are the 2020-era versions, TorchScript-only batch-1 baseline, fp16 ORT compared against fp32 TorchScript, and the unpinned script version. Metadata (MIT, 22.0k stars, last commit 2026-10-10, active) checked and correct.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`, `baseline`
- **Shortcomings recorded by:** verifier batch-174 (wave 8); enricher w8 pair-034
- **Pages the verifier opened:**
  - <https://github.com/microsoft/onnxruntime/blob/main/onnxruntime/python/tools/transformers/README.md>
  - <https://github.com/microsoft/onnxruntime/blob/main/onnxruntime/python/tools/transformers/run_benchmark.sh>
  - <https://github.com/microsoft/onnxruntime/blob/main/onnxruntime/python/tools/transformers/benchmark.py>
  - <https://github.com/microsoft/onnxruntime>
  - <https://github.com/microsoft/onnxruntime/commits/main>
  - <https://github.com/ELS-RD/transformer-deploy>
- **Sources the enricher read:**
  - <https://github.com/microsoft/onnxruntime>
  - <https://raw.githubusercontent.com/microsoft/onnxruntime/HEAD/README.md>
  - <https://raw.githubusercontent.com/microsoft/onnxruntime/HEAD/onnxruntime/python/tools/transformers/README.md>
  - <https://raw.githubusercontent.com/microsoft/onnxruntime/HEAD/onnxruntime/python/tools/transformers/run_benchmark.sh>
  - <https://raw.githubusercontent.com/microsoft/onnxruntime/HEAD/onnxruntime/python/tools/transformers/benchmark.py>
  - <https://raw.githubusercontent.com/microsoft/onnxruntime/HEAD/onnxruntime/python/tools/transformers/benchmark_helper.py>
  - <https://raw.githubusercontent.com/microsoft/onnxruntime/HEAD/onnxruntime/python/tools/transformers/models/gpt2/benchmark_gpt2.py>
  - <https://raw.githubusercontent.com/microsoft/onnxruntime/HEAD/onnxruntime/python/tools/transformers/models/gpt2/gpt2_helper.py>
  - <https://raw.githubusercontent.com/microsoft/onnxruntime/HEAD/onnxruntime/python/tools/transformers/onnx_exporter.py>
  - <https://raw.githubusercontent.com/microsoft/onnxruntime/HEAD/onnxruntime/python/tools/transformers/onnx_model_bert.py>
  - <https://raw.githubusercontent.com/microsoft/onnxruntime/v1.4.0/onnxruntime/python/tools/transformers/README.md>
  - <https://raw.githubusercontent.com/microsoft/onnxruntime/v1.4.0/onnxruntime/python/tools/transformers/run_benchmark.sh>
  - <https://raw.githubusercontent.com/microsoft/onnxruntime/v1.4.0/onnxruntime/python/tools/transformers/benchmark.py>
  - <https://raw.githubusercontent.com/microsoft/onnxruntime/v1.4.0/onnxruntime/python/tools/transformers/benchmark_gpt2.py>
  - <https://raw.githubusercontent.com/microsoft/onnxruntime/v1.4.0/onnxruntime/core/providers/cuda/cuda_execution_provider.cc>
  - <https://raw.githubusercontent.com/microsoft/onnxruntime/v1.4.0/onnxruntime/core/session/inference_session.cc>
  - <https://raw.githubusercontent.com/microsoft/onnxruntime/v1.4.0/onnxruntime/core/session/IOBinding.cc>
  - <https://raw.githubusercontent.com/microsoft/onnxruntime/v1.4.0/onnxruntime/python/onnxruntime_pybind_state.cc>
  - <https://raw.githubusercontent.com/microsoft/onnxruntime/HEAD/cmake/CMakeLists.txt>
  - <https://raw.githubusercontent.com/microsoft/onnxruntime/HEAD/cmake/onnxruntime_language_standard_versions.cmake>
  - <https://raw.githubusercontent.com/microsoft/onnxruntime/HEAD/include/onnxruntime/core/session/onnxruntime_c_api.h>
  - <https://raw.githubusercontent.com/microsoft/onnxruntime/HEAD/docs/Privacy.md>
  - <https://raw.githubusercontent.com/microsoft/onnxruntime/HEAD/VERSION_NUMBER>
  - <https://raw.githubusercontent.com/microsoft/onnxruntime/HEAD/LICENSE>
  - <https://github.com/microsoft/onnxruntime/issues/15154>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/microsoft/onnxruntime`) · [data/wave8/enrich/raw/github_com_microsoft_onnxruntime.json](../../../data/wave8/enrich/raw/github_com_microsoft_onnxruntime.json) (enrichment confidence 0.75)

</details>
