# CNTK

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Microsoft's archived C++ deep-learning toolkit; as a 2017 Keras backend it trained LSTMs about 2.6-3.3x faster than TensorFlow 1.2.

| | |
|---|---|
| **Beats** | TensorFlow (tensorflow-gpu 1.2.1 as a Keras 2.0.6 backend) |
| **Claimed result** | szilard benchm-dl keras_backend.md (GTX 1080 Ti, 2017): text-generation LSTM 3.3x faster than the TensorFlow backend; bidirectional LSTM 2.6x on a later-fixed buggy go_backwards path (Keras 2.0.5/2.0.6); slower than TensorFlow on CNNs (up to 1.7x). |
| **Workload** | Keras backend comparison (Keras 2.0.6, cntk 2.0 versus tensorflow-gpu 1.2.1, Theano 0.9.0) on one GTX 1080 Ti: average training seconds per epoch for bidirectional LSTM on IMDb, text-generation LSTM, MLP and CNN on MNIST, FastText on IMDb and CNN on CIFAR-10. |
| **Metric** | throughput |
| **Hardware** | Local machine with a GeForce GTX 1080 Ti Founder's Edition (CPU model not stated); the page also has M60 (Azure NV6), Titan X (Maxwell) and K80 columns, the K80 numbers copied from Max Woolf's blog. |
| **Compiler and flags** | No compile flags (Python stack): Ubuntu 16.04, CUDA 8.0 + cuDNN 5.1, Keras 2.0.6, tensorflow-gpu 1.2.1, cntk 2.0 (szilard/benchm-dl versions.txt). |
| **Adoption** | 17.6k stars |
| **Last commit** | 2022-09-23 |
| **Links** | [repository](https://github.com/microsoft/CNTK) · [benchmark](https://github.com/szilard/benchm-dl/blob/master/keras_backend.md) |

## Verdict

szilard/benchm-dl keras_backend.md timed Keras 2.0.6 models on CNTK 2.0 against tensorflow-gpu 1.2.1 on one GTX 1080 Ti (Ubuntu 16.04, CUDA 8.0, cuDNN 5.1, CPU unstated): seconds per epoch for a text-generation LSTM 32.7 vs 107.6 (3.3x), a bidirectional LSTM on IMDb 94.3 vs 245.5 (2.6x, measured on the CNTK backend's later-fixed go_backwards path), an MNIST MLP 1.3 vs 1.9 and FastText 2.7 vs 4.5, while both CNN tests favoured TensorFlow (up to 1.7x). Accuracy was similar across backends, and the K80 column was copied from Max Woolf's 2017 blog.

## Use it when

- You maintain an existing CNTK or BrainScript model and need to keep training or evaluating it on its original stack (CUDA 10, Python 3.6 or older).
- You need to convert a legacy CNTK model: CNTK 2.7 exports ONNX 1.4.1, including recurrent loops as ONNX Scan, for serving in ONNX Runtime.
- You are reproducing 2016-2019 results (speech recognition, the Keras-backend benchmarks) that were produced with CNTK.
- Historical reference for how per-frame recurrent loops can be separated from batched non-recurrent work in a static graph.

## Skip it when

- Any new project: Microsoft archived the repository on 2026-02-17, 2.7 (2019-03-29) was the last main release, and the README directs users to ONNX and ONNX Runtime.
- Modern Python or GPUs: PyPI wheels (cntk and cntk-gpu 2.7.post2, uploaded 2020-12-09) exist only for CPython 2.7, 3.5 and 3.6 on x86-64 Linux and Windows, built for CUDA 10; there is no macOS build, and issue #3835 (Dec 2020) asks whether anyone has built it with CUDA 11.1.
- CNN-heavy training: in the same 1080 Ti table TensorFlow 1.2.1 was faster on MNIST CNN (4.7 vs 5.0 s per epoch) and CIFAR-10 CNN (14.2 vs 24.2 s, about 1.7x).
- Keras users: multi-backend Keras dropped CNTK after 2.3.1 (the 2.4.0 README says multi-backend Keras is discontinued and the cntk_backend.py file is gone), so the measured integration path is closed for current Keras.
- Expecting the LSTM gap today: neither backend in the benchmark used cuDNN's fused LSTM (Keras's CuDNNLSTM arrived in 2.0.9), so the result says nothing about CNTK against TensorFlow or PyTorch with cuDNN RNNs.

## How it is fast

CNTK compiles the graph, runs every node outside a recurrent loop once over all frames of all sequences in the minibatch (PAR mode, one large GEMM), and runs only the nodes inside a PastValue/FutureValue loop frame by frame in its C++ engine (SEQTraversalFlowControlNode in ComputationNetworkEvaluation.cpp). Keras 2.0.6's CNTK backend maps K.rnn onto exactly such a CNTK sequence recurrence, while its TensorFlow 1.2 backend runs K.rnn as a tf.while_loop over TensorArrays (parallel_iterations=32, swap_memory=True), which pays control-flow overhead on every time step; with small LSTMs (64 or 128 units, batch 32 or 128) that per-step overhead dominates, which explains the LSTM gap and why the CNN rows, where cuDNN convolution does the work in both, favour TensorFlow. Natively CNTK also offers a cuDNN-backed OptimizedRNNStack and 1-bit-quantized and Block Momentum (BMUF) distributed learners, none of which the benchmark exercised.

## Compared with alternatives

Do not pick it over TensorFlow, PyTorch or MXNet for new work; choose it only to keep legacy CNTK models running, and prefer exporting them to ONNX and serving them with ONNX Runtime (Microsoft's stated successor). For small RNN training today, PyTorch or TensorFlow with cuDNN LSTMs replaces the overhead advantage CNTK had over Keras's 2017 while_loop path.

## Integration

| | |
|---|---|
| **Form** | shared lib (C++ CNTKLibrary, .NET Standard NuGet, Java) or Python wheel (cntk, cntk-gpu) |
| **Dependencies** | CUDA 10 and cuDNN 7 for GPU builds, MKL for CPU kernels (README); building from source needs Visual Studio 2017 15.9 on Windows or the Ubuntu 16.04 Dockerfiles in Tools/docker on Linux |
| **Minimum toolchain** | Python 2.7, 3.5 or 3.6 for the published wheels; Visual Studio 2017 15.9 to build on Windows |
| **Platforms** | x86-64 Linux and Windows; NVIDIA GPUs via CUDA 10; no macOS or ARM builds |
| **Thread safety** | not documented in the files read; CNTKLibrary.h only exposes a process-wide SetMaxNumCPUThreads for intra-op threads |
| **Drop-in for the baseline** | partial: as a Keras 2.0.5-2.3.1 backend it is a one-variable switch for model code that uses only Keras layers (masked RNNs excepted); native CNTK code is a different API from TensorFlow |

## Gotchas

- Harness flaw in the Bidirectional-LSTM row: Keras 2.0.5 and 2.0.6 (the version used for the 1080 Ti, Titan X and M60 columns) implemented go_backwards in the CNTK backend with C.sequence.future_value plus C.sequence.last, so the backward LSTM returned its state after only the last time step; Keras PR #7593 'cntk backend: fix the reversed rnn bug' (merged 2017-08-11, in 2.0.7) replaced it with reversing the input and using past_value. CNTK's SEQ traversal still runs the loop over every frame, so the time is probably representative, but the two backends did not train the same model. The forward-only text-generation LSTM row (3.3x) is unaffected.
- The Keras 2.0.6 CNTK backend raises 'RNN with mask is not support in CNTK currently' for masked recurrent layers (Embedding mask_zero or variable-length input); the IMDb test pads to 100 tokens without masking.
- The benchmark page publishes no scripts of its own; the tasks match minimaxir/keras-cntk-benchmark (batch 32, LSTM(64) for IMDb; batch 128, LSTM(128, implementation=2) for text generation), and timings are averages of 4-20 epochs with one run per backend, no variance, CPU model unstated, on CUDA 8 + cuDNN 5.1.
- Repository is archived and read-only since 2026-02-17 (755 open issues and 84 open pull requests remain); bug reports will not be fixed.

## Known shortcomings

- szilard benchm-dl keras_backend.md numbers (bidirectional LSTM 2.6x to 3.3x faster than TensorFlow on a GTX 1080 Ti) are 2017 software; CNTK is slower than TensorFlow on CNNs (up to 1.7x), scripts and CPU unstated. Repo archived 2026-02-17.
- Enricher: Keras 2.0.5/2.0.6's CNTK backend implemented go_backwards with future_value plus sequence.last, so the backward LSTM returned state after the last token only (fixed by keras PR #7593, 2017-08-11, Keras 2.0.7); the bidirectional-LSTM 2.6x row therefore measured a later-fixed buggy path (timing probably representative since the CNTK SEQ loop still ran every frame), while the text-generation LSTM 3.3x, MLP and FastText rows are clean. Neither backend used cuDNN LSTM (CuDNNLSTM arrived in Keras 2.0.9); the TF path used tf.while_loop swap_memory=True; masked RNNs unsupported; wheels only cp27/35/36 with CUDA 10; Keras dropped CNTK after 2.3.1.

## Caveats and trade-offs

Third-party 2017-era numbers on old software (TensorFlow 1.2.1, CUDA 8, cuDNN 5.1, CNTK 2.0), one GPU model per column, no variance reported, CPU not stated; the page says only that it was inspired by Max Woolf's benchmark, and its K80 column is copied from Max Woolf's blog; minimaxir/keras-cntk-benchmark (MIT, 26 stars) holds keras_cntk_benchmark.py but its README states no CPU model or versions, and benchm-dl (70 stars) itself holds no Keras-backend scripts (only cnn-mnist/). The win is confined to LSTM/RNN and small dense models; TensorFlow is faster on both CNN tests (MNIST CNN 4.7 versus 5.0 s per epoch, CIFAR-10 CNN 14.2 versus 24.2 s on the 1080 Ti), and on the K80 column FastText also favours TensorFlow (58.3 versus 69.5 s); the Keras Python layer sits between the benchmark and both engines. Accuracy is comparable across backends. The repository was archived by Microsoft on 2026-02-17 (read-only); the last code commit is 2020-03-31 and the README calls 2.7 (2019) the last main release. The HKBU dlbench study (arXiv 1608.07249, claims 5-10x over Torch and TensorFlow on CPU LSTMs) was seen only as a search snippet because arxiv.org and dlbench.comp.hkbu.edu.hk are blocked here, so its numbers are not recorded; the hclhkbu/dlbench repo README (MIT, 170 stars) has the harness but no results. CNTK's own README makes no speed claim against other frameworks. [retier] Keras 2.0.7 fixed the CNTK go_backwards bug behind the bidirectional row; neither backend used cuDNN LSTM; TF path ran tf.while_loop swap_memory=True; scripts and CPU unstated; repo archived 2026-02-17; Keras dropped CNTK after 2.3.1.

Deep-learning toolkit with C++ core, Python, C# and BrainScript front ends; the repository was archived by Microsoft on 2026-02-17, the last main release is 2.7 and the README says there are no plans for new features and points users to ONNX and ONNX Runtime. The measured path is the Keras CNTK backend, not native CNTK scripts.

## Maintenance

Abandoned: last main release 2.7 in 2019, last wheels 2020-12-09, repository archived by Microsoft on 2026-02-17; MIT-licensed, but only usable on Python 3.6 or older with CUDA 10, so treat it as a legacy and reference entry rather than something to adopt.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party measurement (szilard/benchm-dl keras_backend.md, environment in versions.txt) times CNTK 2.0 against TensorFlow 1.2.1 as Keras 2.0.6 backends on four GPUs; every quoted 1080 Ti figure and the 'about 2 to 4 times' LSTM summary are on the page. Not A: the page does not name its scripts (the inspiring minimaxir/keras-cntk-benchmark keras_cntk_benchmark.py is public, MIT, but its README states no CPU or versions) and no CPU model is given for any column.
- **Verifier notes:** All claimed numbers match the 1080 Ti column of keras_backend.md; tier B kept as an independent measurement. Shortcomings to record: 2017 software, CNN workloads slower than TensorFlow (up to 1.7x), CPU model and exact scripts unstated, repo archived 2026-02-17. The category (autodiff-and-ml-kernels) is a wave 8 category filed here by the seed backfill; the baseline TensorFlow is itself a record in this same batch.
- **Fields the verifier corrected:** `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-99 (wave 12); enricher w12 pair-006
- **Pages the verifier opened:**
  - <https://github.com/szilard/benchm-dl/blob/master/keras_backend.md>
  - <https://raw.githubusercontent.com/szilard/benchm-dl/master/keras_backend.md>
  - <https://raw.githubusercontent.com/szilard/benchm-dl/master/versions.txt>
  - <https://raw.githubusercontent.com/szilard/benchm-dl/master/README.md>
  - <https://github.com/szilard/benchm-dl>
  - <https://github.com/minimaxir/keras-cntk-benchmark>
  - <https://github.com/microsoft/CNTK>
  - <https://github.com/microsoft/CNTK/commits/master>
  - <https://raw.githubusercontent.com/microsoft/CNTK/master/LICENSE.md>
- **Sources the enricher read:**
  - <https://github.com/microsoft/CNTK>
  - <https://raw.githubusercontent.com/microsoft/CNTK/master/README.md>
  - <https://raw.githubusercontent.com/microsoft/CNTK/master/Source/CNTKv2LibraryDll/API/CNTKLibrary.h>
  - <https://raw.githubusercontent.com/microsoft/CNTK/master/Source/ComputationNetworkLib/ComputationNetworkEvaluation.cpp>
  - <https://raw.githubusercontent.com/microsoft/CNTK/master/Source/ComputationNetworkLib/RecurrentNodes.h>
  - <https://raw.githubusercontent.com/microsoft/CNTK/master/Source/Math/CuDnnRNN.cpp>
  - <https://raw.githubusercontent.com/microsoft/CNTK/master/Source/SGDLib/DataReaderHelpers.h>
  - <https://github.com/microsoft/CNTK/issues?q=is%3Aissue+3090+OR+ampere+OR+%22CUDA+11%22>
  - <https://pypi.org/pypi/cntk/json>
  - <https://pypi.org/pypi/cntk-gpu/json>
  - <https://raw.githubusercontent.com/szilard/benchm-dl/master/keras_backend.md>
  - <https://raw.githubusercontent.com/szilard/benchm-dl/master/versions.txt>
  - <https://raw.githubusercontent.com/szilard/benchm-dl/master/README.md>
  - <https://raw.githubusercontent.com/minimaxir/keras-cntk-benchmark/master/README.md>
  - <https://raw.githubusercontent.com/minimaxir/keras-cntk-benchmark/master/keras_cntk_benchmark.py>
  - <https://raw.githubusercontent.com/minimaxir/keras-cntk-benchmark/master/test_files/imdb_bidirectional_lstm.py>
  - <https://raw.githubusercontent.com/minimaxir/keras-cntk-benchmark/master/test_files/text_generator_keras.py>
  - <https://raw.githubusercontent.com/minimaxir/keras-cntk-benchmark/master/test_files/imdb_fasttext.py>
  - <https://raw.githubusercontent.com/minimaxir/keras-cntk-benchmark/master/test_files/mnist_mlp.py>
  - <https://raw.githubusercontent.com/minimaxir/keras-cntk-benchmark/master/test_files/cifar10_cnn.py>
  - <https://raw.githubusercontent.com/keras-team/keras/2.0.5/keras/backend/cntk_backend.py>
  - <https://raw.githubusercontent.com/keras-team/keras/2.0.6/keras/backend/cntk_backend.py>
  - <https://raw.githubusercontent.com/keras-team/keras/2.0.6/keras/backend/tensorflow_backend.py>
  - <https://raw.githubusercontent.com/keras-team/keras/2.0.6/keras/layers/recurrent.py>
  - <https://raw.githubusercontent.com/keras-team/keras/2.0.7/keras/backend/cntk_backend.py>
  - <https://raw.githubusercontent.com/keras-team/keras/2.0.9/keras/layers/cudnn_recurrent.py>
  - <https://raw.githubusercontent.com/keras-team/keras/2.3.1/keras/backend/cntk_backend.py>
  - <https://raw.githubusercontent.com/keras-team/keras/2.4.0/README.md>
  - <https://github.com/keras-team/keras/commits/2.0.7/keras/backend/cntk_backend.py>
  - <https://github.com/keras-team/keras/pull/7593>
  - WebSearch: minimaxir Benchmarking CNTK on Keras (slideshare snippet: CNTK faster on LSTMs/MLPs, TensorFlow on CNNs/embeddings)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/microsoft/cntk`) · [data/wave12/enrich/raw/github_com_microsoft_cntk.json](../../../data/wave12/enrich/raw/github_com_microsoft_cntk.json) (enrichment confidence 0.7)

</details>
