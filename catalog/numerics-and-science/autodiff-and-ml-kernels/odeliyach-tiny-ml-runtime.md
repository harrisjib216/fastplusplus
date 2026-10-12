# tiny-ml-runtime

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Educational pure-C MLP inference loop; beats per-call Python PyTorch only on tiny nets, loses 5x on MNIST.

| | |
|---|---|
| **Beats** | PyTorch 2.x (Python, batch size 1) |
| **Claimed result** | README: Iris (4-8-3), batch 1, 1M iterations: pure C 2,732,240 predictions/s (0.366 s) vs PyTorch from a single-threaded Python loop 10,596 predictions/s (94.374 s), stated as 258x; the README warns this measures Python plus PyTorch dispatch overhead, not compute throughput. MNIST (784-128-10), 100K iterations: pure C 4,244 predictions/s (23.563 s) vs PyTorch 22,502 (0.444 s), i.e. PyTorch about 5.3x faster (derived from page data). |
| **Workload** | Single-sample inference of a 4-8-3 Iris MLP and a 784-128-10 MNIST MLP, pure C engine versus PyTorch called from a single-threaded Python loop. |
| **Metric** | throughput |
| **Hardware** | Apple M1 (ARM64) |
| **Compiler and flags** | gcc -Wall -Wextra -O2 (Makefile); compiler version not stated |
| **Adoption** | 0 stars |
| **Last commit** | 2026-03-25 |
| **Links** | [repository](https://github.com/odeliyach/tiny-ml-runtime) · [benchmark](https://github.com/odeliyach/tiny-ml-runtime/blob/main/README.md) |

## Verdict

On an Apple M1 with gcc -O2 (version unstated), the C engine ran a 4-8-3 Iris MLP at 2,732,240 single-sample predictions/s versus 10,596/s for PyTorch 2.x driven from a single-threaded Python 3.11 loop (258x), but on a 784-128-10 MNIST MLP it managed 4,244/s versus PyTorch's 22,502/s, so PyTorch was about 5.3x faster. The timers differ between sides (CPU time vs wall clock) and no C/C++ runtime such as libtorch was compared.

## Use it when

- Reading or teaching how a dense forward pass, numerically stable softmax and a weight loader work in about 300 lines of C.
- Seeing the overhead-vs-compute crossover: tiny networks (tens of weights) called one sample at a time from code that would otherwise go through Python.
- A starting point you intend to rewrite (preallocated buffers, SIMD GEMV) for a microcontroller-style dense classifier, under MIT terms.

## Skip it when

- Any compute-bound network: on the 784-128-10 MNIST MLP the author's own numbers show PyTorch about 5.3x faster (22,502 vs 4,244 predictions/s).
- Production or untrusted model files: the standalone engine's load_weights() reads num_layers and the input width from the file without bounds checks into fixed arrays (layer_sizes[10], scaler_mean/std[784]), so a malformed file overflows the Network struct; malloc results in predict() are unchecked.
- Real-time or allocation-free contexts: predict() calls malloc/free twice per sample.
- Anything beyond dense + ReLU + softmax with at most 10 layers and 784 inputs (MAX_LAYERS, MAX_FEATURES): no convolutions, recurrent layers, other activations or batching.
- Through the Python binding: tinymlinference.predict() reopens and reparses the weight file on every call.

## How it is fast

It does not have a fast kernel: linear() is a naive row-major double loop with no SIMD, tiling, threading or restrict qualifiers, compiled with gcc -O2. The Iris win comes purely from skipping the Python interpreter and PyTorch's per-op dispatch on a 4-8-3 network (about 56 multiply-adds), which the README states itself. Each predict() still mallocs and frees two scratch buffers, so even the overhead-bound path is not minimal.

## Compared with alternatives

Pick it only to learn; for real per-sample CPU inference of small networks RTNeural does the same job with compile-time-sized, allocation-free SIMD layers plus recurrent layers, and faster-enhancer.c is the catalogued example of a single-model C engine that beats ONNX Runtime on the same weights.

## Integration

| | |
|---|---|
| **Form** | source-drop (src/c/inference.c + inference.h; Makefile builds a demo executable) or CPython extension via pip install . |
| **Dependencies** | none for the C core (libc, libm); PyTorch and NumPy only for training/export and the Python benchmark |
| **Minimum toolchain** | C11 per README; built with gcc -Wall -Wextra -O2 |
| **Platforms** | any C11 target; benchmarked only on Apple M1 (ARM64); weight file is raw native-endian int32/float32 |
| **Thread safety** | Author's notes: safe for concurrent read-only inference with no global state, since predict() uses per-call heap buffers; one Network per loader. |
| **Drop-in for the baseline** | no |

## Gotchas

- The 258x figure compares C CPU time (clock()) with wall-clock time (time.time()) of a Python loop that calls .item() per prediction; it measures interpreter plus dispatch overhead, not PyTorch kernels.
- The README's MNIST table header says 100K iterations, but src/python/benchmark_mnist.py runs 10,000 PyTorch iterations (10,000 / 0.444 s matches the 22,502/s shown); only the C side ran 100K.
- The CPython extension carries its own copy of the loader (with bounds checks) that leaks earlier layer buffers on a mid-file read failure; the two copies can drift.
- The weight format has no magic number, version or endianness marker.

## Known shortcomings

- The 258x is Python dispatch overhead; PyTorch is 5.3x faster on MNIST; C side timed with clock() and Python with time.time(); 0-star toy, flagged only.
- Security bug: the standalone C load_weights() reads num_layers and the input size from the weight file with no bounds check into fixed arrays (layer_sizes[10], scaler_mean/std[784]), so a malformed file overflows the struct; malloc results in predict() are never checked; the Python binding rereads the weight file on every predict() and leaks memory on a failed load; README says the MNIST PyTorch row used 100K iterations but benchmark_mnist.py runs 10,000.

## Caveats and trade-offs

Educational project with 0 stars. The 258x win is Python-interpreter and PyTorch dispatch overhead on a 4-feature input (the README says so), not a like-for-like library comparison: the PyTorch side is a Python loop that calls .item() on every prediction and is timed with time.time() (wall clock), while the C side is timed with clock() (CPU time) and is not compared against libtorch or any C/C++ inference engine. The C predict() mallocs and frees two buffers per call and uses naive loops with no SIMD, so on the compute-bound MNIST case PyTorch wins by about 5x. Single Apple M1 run, compiler version unstated.

Naive C loops with no SIMD, tiling or threading; dense layers, ReLU and softmax only; weights exported from PyTorch to a binary file.

## Maintenance

A 0-star student portfolio project (MIT, 47 commits, last commit 2026-03-25) with CI and tests; small enough to read and copy, but its own docs say it is not production-ready.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table with public benchmark code (src/c/inference.c benchmark(), src/python/benchmark.py), Makefile flags (gcc -O2) and the hardware (Apple M1) named, but no compiler version, and the C and Python sides use different timers. The gain is over 50x against a Python-dispatch baseline, so it is capped at C.
- **Verifier notes:** README numbers match the record exactly. Metadata confirmed (MIT, 0 stars, last commit 2026-03-25, active). Keep only as a flagged toy: its single win is overhead-bound and it loses on the compute-bound workload.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/odeliyach/tiny-ml-runtime/HEAD/README.md>
  - <https://raw.githubusercontent.com/odeliyach/tiny-ml-runtime/HEAD/Makefile>
  - <https://raw.githubusercontent.com/odeliyach/tiny-ml-runtime/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/odeliyach/tiny-ml-runtime/HEAD/src/python/benchmark.py>
  - <https://raw.githubusercontent.com/odeliyach/tiny-ml-runtime/HEAD/src/c/inference.c>
  - <https://github.com/odeliyach/tiny-ml-runtime>
  - <https://github.com/odeliyach/tiny-ml-runtime/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/odeliyach/tiny-ml-runtime/HEAD/README.md>
  - <https://raw.githubusercontent.com/odeliyach/tiny-ml-runtime/HEAD/Makefile>
  - <https://raw.githubusercontent.com/odeliyach/tiny-ml-runtime/HEAD/src/c/inference.c>
  - <https://raw.githubusercontent.com/odeliyach/tiny-ml-runtime/HEAD/src/c/inference.h>
  - <https://raw.githubusercontent.com/odeliyach/tiny-ml-runtime/HEAD/src/c/inference_module.c>
  - <https://raw.githubusercontent.com/odeliyach/tiny-ml-runtime/HEAD/src/python/benchmark.py>
  - <https://raw.githubusercontent.com/odeliyach/tiny-ml-runtime/HEAD/src/python/benchmark_mnist.py>
  - <https://raw.githubusercontent.com/odeliyach/tiny-ml-runtime/HEAD/docs/TECHNICAL_ANALYSIS.md>
  - <https://github.com/odeliyach/tiny-ml-runtime>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/odeliyach/tiny-ml-runtime`) · [data/wave8/enrich/raw/github_com_odeliyach_tiny_ml_runtime.json](../../../data/wave8/enrich/raw/github_com_odeliyach_tiny_ml_runtime.json) (enrichment confidence 0.85)

</details>
