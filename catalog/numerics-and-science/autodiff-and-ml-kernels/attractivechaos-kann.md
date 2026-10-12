# KANN

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟡 stale

> Four-file C library for training small MLPs, CNNs and RNNs on CPU; beat 2017 Theano+Keras and tiny-dnn in its own runs.

| | |
|---|---|
| **Beats** | Theano 0.8.2 + Keras 1.2.2 (CPU, MKL); also TensorFlow 1.0.0 (CPU) and tiny-dnn |
| **Claimed result** | README Benchmarks table (first-party, 2017). mnist-mlp, Linux 1 CPU: KANN+SSE 31.3 s, KANN+BLAS 18.8 s versus Theano+Keras 33.7 s (KANN+BLAS about 1.8x, KANN+SSE about 1.08x, derived from page data), Tiny-dnn 2m19s (KANN+SSE about 4.4x, derived) and Tiny-dnn+AVX 1m34s (about 3.0x, derived). Mac 1 CPU: KANN 27.1 s versus TensorFlow 33.4 s and Theano+Keras 37.2 s. mul100-rnn, Linux 4 CPUs: KANN+SSE 12m13s and KANN+BLAS 8m18s versus Theano+Keras 19m52s (about 1.6x and 2.4x, derived); 1 CPU: KANN+SSE 40m05s is slower than Theano+Keras 27m30s, KANN+BLAS 22m58s is about 1.2x faster (derived). mnist-cnn, 4 CPUs: KANN 19m09s versus Theano+Keras 24m24s (about 1.27x, derived); 1 CPU: KANN 57m57s versus Tiny-dnn+AVX 300m40s (about 5.2x, derived) but slower than Theano+Keras 37m12s. |
| **Workload** | Training time on CPU for small networks: mnist-mlp (one hidden layer of 64 neurons), mnist-cnn (two 3x3x32 conv layers, max pool, 128-neuron dense), mul100-rnn (two GRU layers of size 160, 30000 samples), each run for a fixed number of epochs. |
| **Metric** | throughput |
| **Hardware** | Linux: 48 cores on two Xeon E5-2697 CPUs at 2.7GHz (plus a Tesla K40c used only for the Keras GPU row); Mac: Core i7-3667U 2GHz, 4 cores |
| **Compiler and flags** | Not stated for the README runs; the repo Makefile defaults to 'gcc -g -Wall -Wextra -Wc++-compat -O2'; KANN+BLAS used OpenBLAS-0.2.19 |
| **Adoption** | 761 stars |
| **Last commit** | 2025-06-06 |
| **Links** | [repository](https://github.com/attractivechaos/kann) · [benchmark](https://github.com/attractivechaos/kann) |

## Verdict

First-party 2017 README table, one run per row on 2x Xeon E5-2697 2.7GHz (Linux) and a Core i7-3667U (Mac), compiler and flags unstated (the Makefile defaults to gcc -O2): mnist-mlp, 20 epochs, 1 thread, took 31.3 s for KANN with SSE and 18.8 s with OpenBLAS 0.2.19 versus 33.7 s for Theano 0.8.2 + Keras 1.2.2 with MKL and 2m19s for tiny-dnn, and with 4 threads KANN beat Theano+Keras on mnist-cnn (19m09s vs 24m24s) and mul100-rnn (12m13s, or 8m18s with OpenBLAS, vs 19m52s). Single-threaded without BLAS it lost to Theano+Keras on mnist-cnn (57m57s vs 37m12s) and mul100-rnn (40m05s vs 27m30s), and the baselines are 2017 releases, so the result is about framework overhead and threading on tiny models, not about KANN's kernels beating MKL.

## Use it when

- Training or running small to medium networks (an MLP with tens to hundreds of hidden units, a small CNN, a two-layer GRU of 160 units) inside a C or C++ program without Python, CUDA or a framework dependency.
- Embedding a trainable model in a tool where the four source files (kann.c, kann.h, kautodiff.c, kautodiff.h, about 3,900 lines) can be vendored, for example bioinformatics or command-line utilities.
- CPU-only multi-core training of tiny models where per-step framework overhead dominates and intra-batch threading across 4 cores helps (the README's 4-thread rows beat Theano+Keras by about 1.3x to 2.4x, derived from page data).
- Building non-standard graphs (shared weights, multiple inputs, outputs or costs, VAEs, recurrent nodes) in C when tiny-dnn's layer stack is too rigid.
- Learning how a reverse-mode autodiff engine and RNN unrolling work; the code and doc/02dev.md are short enough to read in an afternoon.

## Skip it when

- Anything that needs GPUs, large networks or modern operators: no GPU backend, no batch normalization, no attention or transformer layers, float32 only.
- Single-threaded convolution or RNN training without BLAS: KANN's own kernels lost to MKL-backed Theano+Keras in the README (mnist-cnn 57m57s vs 37m12s, mul100-rnn 40m05s vs 27m30s), and doc/02dev.md says its direct convolution is about twice as slow as Theano's GEMM-based one.
- When you need a maintained project: the only commits after April 2021 are two in June 2025 (NEON support and an mt-mode API), and issues such as #33 (mnist-cnn assert failure, 2019) and #34 (kann_class_error returns 0 for KANN_C_CEB, 2020) are still open.
- Interchange with other frameworks: no ONNX or Keras import/export, only kann_save/kann_load in its own format.
- Wide-SIMD x86 targets where you expect AVX2/AVX-512 or FMA: the built-in kernels are 128-bit SSE intrinsics; link OpenBLAS (make CBLAS=...) to get faster dense layers.

## How it is fast

There is little framework overhead: one C graph evaluated in topological order with float32 buffers, no interpreter or Python layer. Matrix products use a cache-tiled sgemm built on hand-written 4-wide SSE (or, since June 2025, NEON) sdot/saxpy kernels, or cblas_sgemm when compiled with HAVE_CBLAS (OpenBLAS gave the README's fastest rows). Convolution is direct computation with an optimized inner loop and an NCHW-to-NHWC reshuffle, not im2col, so it needs little working memory but does not benefit from BLAS. Multi-threading (kann_mt) splits each mini-batch across cloned networks on pthreads and averages their gradients, which scaled better than the 2017 Theano+Keras setup.

## Compared with alternatives

Pick KANN over tiny-ml-runtime when you need training and RNNs rather than inference of a fixed tiny MLP, and over PyTorch, MXNet or Caffe when a dependency-free C source drop matters more than speed on big models or GPUs. Adept-2, XAD and CoDiPack are scalar operator-overloading AD for C++ numerical code, not neural-network training, so they rarely compete with KANN.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond libc and libm; optional pthreads (HAVE_PTHREAD, on in the Makefile) and an optional CBLAS such as OpenBLAS (HAVE_CBLAS); the examples' kann_extra/kann_data.c uses zlib |
| **Minimum toolchain** | ANSI C / C89-compatible compiler (README; the Makefile builds with gcc -O2 and also checks -Wc++-compat); kann.h has extern "C" guards for C++ |
| **Platforms** | any C target; SSE fast path on x86-64, NEON fast path on aarch64 since June 2025, scalar fallback elsewhere |
| **Thread safety** | Not documented as thread-safe. One kann_t must not be used from several threads; kann_mt() runs its own worker threads that main-thread code busy-waits on, and the default random number state (kad_rand(0), kann_srand) and kann_verbose are unsynchronized globals. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness differences behind the README table (none invalidates it, but the rows are not like-for-like): KANN's mnist-cnn adds two dropout(0.2) layers that the Keras (-C without -d) and tiny-dnn models lack; the TensorFlow script trains with Adam and tiny-dnn with plain SGD and softmax cross-entropy, while KANN and Keras use RMSprop with sigmoid binary cross-entropy; the Python scripts print their own timers (Keras rnn-bit.py includes model build and Theano compilation, mlp.py excludes it) while the KANN examples have no internal timer, and the README does not say which timer produced each row; the scripts leave theano.config.openmp commented out, so Theano's 4-CPU rows thread only MKL GEMM.
- examples/rnn-bit.c trains with 'for (j = 0; j &lt; d-&gt;n - mini_size; j += mini_size)', so each epoch skips the tail of the data (468 batches, 29,952 of the 30,000 mul100 samples); the extra work this saves is under 0.2%, so it does not explain the RNN speedups.
- kann_mt() synchronizes by spinning on a volatile int counter rather than atomics or a condition variable on the main thread: one core is burned while workers run, and the pattern relies on x86 memory ordering, a concern for the new aarch64 NEON build. The NEON kernels carry a source comment saying they were 'translated from SSE to NEON by LLM' and have no published benchmarks.
- Issue #44 (Apple M1) reports the Getting Started rnn-bit example printing 1924146487037 instead of 1138429; the low 21 bits match and only bits 38-40 are wrong (derived from issue data), because rnn-bit's apply mode decodes 64 steps while the model was trained on the data's bit length, so untrained steps can emit spurious 1s. Also, the examples call kad_trap_fe(), which unmasks SSE invalid and divide-by-zero exceptions, so an invalid operation (a NaN-producing step) or a division by zero makes them crash with SIGFPE.

## Known shortcomings

- Tier C: README numbers from 2017 against Theano 0.8.2 and TensorFlow 1.0.0 with the build unstated; without BLAS KANN loses single-thread to Theano+Keras on mnist-cnn (57m57s vs 37m12s) and mul100-rnn (40m05s vs 27m30s). Stale (last commit 2025-06-06).
- Enricher: README rows are not like for like (numbers not invalidated): KANN's mnist-cnn adds two dropout(0.2) layers that Keras and tiny-dnn lack; TF uses Adam, tiny-dnn SGD with softmax cross-entropy, KANN and Keras RMSprop with sigmoid cross-entropy; timers are asymmetric (Keras rnn-bit.py times build plus Theano compile, mlp.py excludes it, KANN examples have no internal timer and the README does not say which timer each row used); theano.config.openmp is commented out; the rnn-bit.c loop skips the tail (29,952 of 30,000 samples). kann_mt's main thread spins on a volatile int and relies on x86 ordering; NEON kernels were 'translated from SSE to NEON by LLM' with no benchmarks; open bugs #33 (mnist-cnn assert), #34 (kann_class_error 0 for CEB), #44 (M1 wrong sum beyond trained length). Stale since 2021 except two commits in June 2025.

## Caveats and trade-offs

First-party numbers from 2017 (Theano 0.8.2, Keras 1.2.2, TensorFlow 1.0.0, Tiny-dnn pulled March 1 2017), long before current frameworks; compiler version and flags used for the README runs are not stated, so tier C although the competitor scripts are in the repo (examples/keras, examples/tensorflow, examples/tiny-dnn). The README itself says not to read too much into the table, that Theano is about 50% faster than KANN single-threaded because of MKL sgemm, and that MKL/OpenBLAS matmul can be twice as fast as KANN's own. Without BLAS, KANN loses single-threaded to Theano+Keras on both mnist-cnn (57m57s vs 37m12s) and mul100-rnn (40m05s vs 27m30s); its wins are against Tiny-dnn, on multi-threaded rows (better intra-batch threading than Theano+Keras), and on the KANN+BLAS rows that add OpenBLAS-0.2.19, so the claim is not that KANN's own kernels beat MKL. TensorFlow was measured only on the Mac. None of the baselines are in the category's incumbent list (oneDNN, cuDNN, XNNPACK, Eigen tensor). Last commit 2025-06-06 (NEON support); no commits between April 2021 and June 2025.

Four source files (kautodiff, kann), under 4000 lines, only the C library by default, optional OpenBLAS and pthreads. CPU only, no batch normalization or other common operators, verbose RNN training API, not meant for large networks. Benchmarks cover small networks only.

## Maintenance

Stale: commits stopped in April 2021 apart from two in June 2025 (NEON support, an mt-mode API), with 2019-2021 bug reports unanswered, but it is MIT-licensed, about 3,900 lines in four C files with no required dependencies, and easy to vendor and patch.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README Benchmarks table (2017) with CPU models stated (2x Xeon E5-2697 2.7GHz; Core i7-3667U) and competitor scripts in examples/keras, examples/tensorflow, examples/tiny-dnn, but the compiler, its version and the flags used for the runs are not stated (the Makefile only defaults to gcc -O2), so not A; no independent measurement, so not B.
- **Verifier notes:** README numbers and hardware match the record; added the Tiny-dnn+AVX and 1-CPU mul100-rnn rows, which show KANN without BLAS losing single-threaded to Theano+Keras. Metadata checked on github.com: MIT (LICENSE.txt, Dana-Farber/Broad), 761 stars, not archived, last commit 2025-06-06 (stale). Shortcomings: 2017-era baselines, unstated build, single-thread losses to MKL-backed Theano.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-58 (wave 1); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://github.com/attractivechaos/kann>
  - <https://github.com/attractivechaos/kann/commits>
  - <https://github.com/attractivechaos/kann/tree/master/examples>
  - <https://raw.githubusercontent.com/attractivechaos/kann/HEAD/README.md>
  - <https://raw.githubusercontent.com/attractivechaos/kann/HEAD/Makefile>
  - <https://raw.githubusercontent.com/attractivechaos/kann/HEAD/LICENSE.txt>
- **Sources the enricher read:**
  - <https://github.com/attractivechaos/kann>
  - <https://github.com/attractivechaos/kann/tree/master/examples>
  - <https://github.com/attractivechaos/kann/commits>
  - <https://github.com/attractivechaos/kann/issues?q=is%3Aissue>
  - <https://github.com/attractivechaos/kann/issues/33>
  - <https://github.com/attractivechaos/kann/issues/34>
  - <https://github.com/attractivechaos/kann/issues/44>
  - <https://raw.githubusercontent.com/attractivechaos/kann/HEAD/README.md>
  - <https://raw.githubusercontent.com/attractivechaos/kann/HEAD/Makefile>
  - <https://raw.githubusercontent.com/attractivechaos/kann/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/attractivechaos/kann/HEAD/kann.h>
  - <https://raw.githubusercontent.com/attractivechaos/kann/HEAD/kann.c>
  - <https://raw.githubusercontent.com/attractivechaos/kann/HEAD/kautodiff.h>
  - <https://raw.githubusercontent.com/attractivechaos/kann/HEAD/kautodiff.c>
  - <https://raw.githubusercontent.com/attractivechaos/kann/HEAD/examples/mlp.c>
  - <https://raw.githubusercontent.com/attractivechaos/kann/HEAD/examples/mnist-cnn.c>
  - <https://raw.githubusercontent.com/attractivechaos/kann/HEAD/examples/rnn-bit.c>
  - <https://raw.githubusercontent.com/attractivechaos/kann/HEAD/examples/keras/mlp.py>
  - <https://raw.githubusercontent.com/attractivechaos/kann/HEAD/examples/keras/rnn-bit.py>
  - <https://raw.githubusercontent.com/attractivechaos/kann/HEAD/examples/tensorflow/mlp.py>
  - <https://raw.githubusercontent.com/attractivechaos/kann/HEAD/examples/tiny-dnn/mlp.cpp>
  - <https://raw.githubusercontent.com/attractivechaos/kann/HEAD/doc/01user.md>
  - <https://raw.githubusercontent.com/attractivechaos/kann/HEAD/doc/02dev.md>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/attractivechaos/kann`) · [data/wave1/enrich/raw/github_com_attractivechaos_kann.json](../../../data/wave1/enrich/raw/github_com_attractivechaos_kann.json) (enrichment confidence 0.8)

</details>
