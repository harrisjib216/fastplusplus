# CodeJeNN (Keras-to-C++ inference header generator)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++ (generated); generator in Python` · `NRL Open License Agreement (custom, non-OSI)` · 🟢 active

> Python tool that turns a trained Keras MLP/CNN into one dependency-free C++ header; snippet-reported 2-25x over Keras eager on one core.

| | |
|---|---|
| **Beats** | Keras eager-mode inference (TensorFlow backend for the MLP case, PyTorch backend for the CNN case) |
| **Claimed result** | Snippet only (arXiv 2607.02746 not opened; WebSearch summary): MLP, 10,000 samples in 0.48 s with generated C++ vs 12.01 s for Keras with the TensorFlow backend (about 25x) and 1.21 s for TensorFlow JIT (about 2.5x). CNN: 1.05 s vs 19.14 s eager (about 18x) and 2.17 s JIT (about 2.1x). The abstract-level summary says '2-38x faster inference than Keras backends'. The search agent's other summary (nearly 38x with the PyTorch backend, about 9x vs PyTorch JIT) was not confirmed by the snippet seen here. The repo itself publishes no numbers. |
| **Workload** | Single-thread, single-core inference of a small MLP and CNN, 10,000 loops each on fresh random samples, generated C++ vs Keras eager (and Keras JIT mode). |
| **Metric** | latency |
| **Hardware** | MacBook with M1 Pro chip, single thread on one core |
| **Compiler and flags** | g++-15 (Homebrew GCC, not Apple clang) with -O3 -march=native -ffast-math -fopenmp, OMP_NUM_THREADS=1, linked against conda HDF5 (tutorials/06_speed_test/mlp/run.sh and cnn/run.sh); llvm-openmp from conda-forge |
| **Adoption** | 1 star |
| **Last commit** | 2026-06-22 |
| **Links** | [repository](https://github.com/jarcities/codejenn) · [benchmark](https://raw.githubusercontent.com/jarcities/codejenn/HEAD/tutorials/06_speed_test/readme.md) |

## Verdict

The repo's speed test (tutorials/06_speed_test) times 10,000 single-sample calls of a small MLP and CNN in Keras eager or JIT mode against the generated C++ (g++-15 -O3 -march=native -ffast-math, one thread, MacBook M1 Pro) but publishes no numbers. The figures come only from search snippets of arXiv 2607.02746: MLP 0.48 s vs 12.01 s Keras/TensorFlow eager (about 25x) and 1.21 s with JIT (about 2.5x), CNN 1.05 s vs 19.14 s eager (about 18x) and 2.17 s JIT (about 2.1x). The C++ timing loop discards outputs, and the measured models hit the stale-output code path described above.

## Use it when

- Calling a small Keras-trained MLP or CNN once per cell or per sample inside a C++ physics or CFD code, where linking TensorFlow, libtorch or ONNX Runtime is unwanted
- Single-sample, single-thread latency on CPU with models small enough that the weight arrays stay in cache (the speed test uses a 1000-64-32-100 MLP and a 10x100 input CNN)
- Supported layer sets only: Dense, Conv1D/2D/3D and their transposes, separable and depthwise conv, pooling, Batch/Layer/Unit/Group normalization, Reshape/Flatten/Rescaling, common activations
- Research or government projects that can accept the NRL Open License Agreement

## Skip it when

- Calling the generated function more than once with a 1-D output and no output normalization file: the generator emits `static std::array<Scalar, N> model_output = layer_K_output;`, a static local initialized only on the first call, so every later call returns the first result (this is the configuration of both speed-test models)
- Multithreaded callers: every layer buffer and the output are function-local statics, so concurrent calls from OpenMP or MPI+threads code race
- Large models or batched throughput: Dense is an unvectorized scalar loop with strided weight access, the README warns large static arrays make it memory-bandwidth bound, and against Keras JIT the snippet-reported gain is only about 2-2.5x
- Recurrent, attention or multi-input/multi-output models: only single-input, single-output sequential or functional MLP/CNN graphs are supported (ConvLSTM2D is commented out)
- Projects needing an OSI license: the NRL agreement restricts redistribution to its own terms, takes an irrevocable grant-back of modifications to the US Government, and can be terminated by the Government

## How it is fast

It removes the framework entirely: no Python dispatch, no tensor allocation and no graph runtime per call, which is what dominates single-sample inference of small models in Keras eager mode. Weights are emitted as constexpr std::array literals, layers are small inline function templates (a plain scalar dot-product loop for Dense) with activations passed as lambdas so the compiler can inline everything, and intermediate buffers are preallocated function-local statics. The README says vectorization and threading are deliberately left out, on the assumption that the host solver is already parallel.

## Compared with alternatives

RTNeural is the catalogued alternative for small-model C++ inference, with measured comparisons against libtorch, ONNX Runtime and TensorFlow Lite; pick CodeJeNN only when you want a single dependency-free header generated straight from a Keras .h5/.keras file, including 3D and transposed convolutions, and can accept the NRL license and fix the static-buffer issues. Kaoken and tiny-ml-runtime take the same baked-weights approach for other model types.

## Integration

| | |
|---|---|
| **Form** | source-drop (generated single header per model; the generator is a Python script, src/api-core/main.py) |
| **Dependencies** | none for the generated header beyond the C++ standard library; the generator needs Keras plus a backend (TensorFlow, PyTorch or JAX), matplotlib, pandas, scikit-learn, sympy, spektral, pydot |
| **Minimum toolchain** | not documented; the generated code uses constexpr std::array and generic lambdas (C++17 is a safe assumption, not stated). The speed test used Homebrew g++-15 with -O3 -march=native -ffast-math |
| **Platforms** | any platform with a C++ compiler (portable scalar code, no intrinsics); tested by the author on an Apple M1 Pro |
| **Thread safety** | not thread-safe: generated functions keep layer outputs and the returned array in function-local static buffers |
| **Drop-in for the baseline** | no |

## Gotchas

- Stale-output bug: with a 1-D output and no output_\*.npy normalization files, the returned array is a static initialized once, so results after the first call are wrong; the --debug comparison calls the model once and does not catch it, and the speed test discards results
- Weights are non-static constexpr locals inside the inline function; for large models check stack use and code size, since the compiler may materialize them per call
- Custom activations need a hand-written C++ version pasted into the header; until then the header prints 'WARNING: CUSTOM ACTIVATION HAS NOT BEEN IMPLEMENTED' on every call
- Docs disagree with the scripts: the speed-test readme says the CNN used PyTorch and the MLP TensorFlow, but the checked-in test.py files set the opposite; src/generate.sh passes --double, which main.py's argparse does not define (it takes --bit=32|64), so the shipped default script should exit with an unrecognized-argument error

## Known shortcomings

- Numbers from an arXiv snippet only (MLP 0.48 s vs 12.01 s eager and 1.21 s JIT; CNN 1.05 s vs 19.14 s and 2.17 s JIT); the 38x CNN figure is not confirmed. README backend labels contradict test.py. NRL licence is non-OSI, so reference only.
- Correctness bug: code_generate.py emits `static std::array<Scalar,N> model_output = layer_K_output;` for 1-D outputs without output normalization; a static local initialises once, so every call after the first returns the first result. Both speed-test models (MLP 1000-&gt;100, CNN -&gt;100) take this path, and test.cpp discards results while --debug calls the model once, so neither catches it; whether the timed loop still does the work (or is optimised away) is unproven without a build. Every layer buffer is a function-local static (not thread-safe). src/generate.sh passes --double, which main.py's argparse lacks.

## Caveats and trade-offs

Speedup figures come only from search snippets of arXiv 2607.02746, which could not be opened. Two snippet summaries disagree on the CNN figures (about 18x vs about 38x). The repo's speed test reproduces the setup but publishes no numbers. The baseline is Keras eager mode on tiny models, single thread, which is dominated by Python dispatch overhead, so the comparison favors generated code; against JIT modes the gain is about 2-2.5x per the snippet. The generated C++ is built with -ffast-math and -march=native. The tutorial readme says the CNN uses the PyTorch backend and the MLP TensorFlow, but the checked-in test.py files set the opposite (mlp: KERAS_BACKEND=torch; cnn: tensorflow), and cnn/run.sh has the Python and training steps commented out. License is the NRL Open License Agreement: use and modify allowed, redistribution only under that agreement, irrevocable grant-back of modifications to the US Government, and the Government may terminate it. It is not OSI-approved, so the code is reference only. A single commit ('final draft for paper') makes up the history.

Emits a standalone C++ header with inlined static weights and no Lapack or Eigen dependency; large models can become memory-bandwidth bound because of big static arrays (noted in the repo); input must be a Keras HDF5 model with supported layers only.

## Maintenance

A single-commit code drop (2026-06-22, 'final draft for paper') from a US Naval Research Laboratory project with 1 star; the NRL Open License makes it reference-only for this catalog, and the generated header may count as a derivative work under that agreement.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The benchmark page (tutorials/06_speed_test/readme.md) describes a CodeJeNN-vs-Keras eager/JIT harness. The harness is public (mlp/ and cnn/ run.sh, test.py, test.cpp), the compiler and flags are in run.sh, and the hardware (M1 Pro, one core) is named. But the page publishes no numbers. The timings exist only in arXiv 2607.02746, which is blocked here and seen through search snippets, so per the snippet-only rule the tier stays C.
- **Verifier notes:** The benchmark page has no numbers. I confirmed the MLP/CNN timings through one WebSearch snippet. The arXiv html/abs and pith.science pages are egress-blocked, so the speedup stays snippet-level. Recordable shortcomings: the backend labels in the readme contradict test.py, the baseline is Keras eager (Python overhead) and the gain vs JIT is only about 2-2.5x, and the license is non-OSI. Metadata on github.com: license.txt (NRL Open License), 1 star, 0 forks, not a fork, 1 commit on 2026-06-22 (active).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/jarcities/codejenn/HEAD/tutorials/06_speed_test/readme.md>
  - <https://raw.githubusercontent.com/jarcities/codejenn/HEAD/readme.md>
  - <https://raw.githubusercontent.com/jarcities/codejenn/HEAD/license.txt>
  - <https://raw.githubusercontent.com/jarcities/codejenn/HEAD/tutorials/06_speed_test/mlp/run.sh>
  - <https://raw.githubusercontent.com/jarcities/codejenn/HEAD/tutorials/06_speed_test/cnn/run.sh>
  - <https://raw.githubusercontent.com/jarcities/codejenn/HEAD/tutorials/06_speed_test/mlp/test.py>
  - <https://raw.githubusercontent.com/jarcities/codejenn/HEAD/tutorials/06_speed_test/cnn/test.py>
  - <https://github.com/jarcities/codejenn>
  - <https://github.com/jarcities/codejenn/commits>
  - <https://github.com/jarcities/codejenn/tree/main/tutorials/06_speed_test>
- **Sources the enricher read:**
  - <https://github.com/jarcities/codejenn>
  - <https://raw.githubusercontent.com/jarcities/codejenn/HEAD/readme.md>
  - <https://raw.githubusercontent.com/jarcities/codejenn/HEAD/license.txt>
  - <https://raw.githubusercontent.com/jarcities/codejenn/HEAD/requirements.txt>
  - <https://raw.githubusercontent.com/jarcities/codejenn/HEAD/src/readme.md>
  - <https://raw.githubusercontent.com/jarcities/codejenn/HEAD/src/generate.sh>
  - <https://github.com/jarcities/codejenn/tree/main/src/api-core>
  - <https://raw.githubusercontent.com/jarcities/codejenn/HEAD/src/api-core/code_generate.py>
  - <https://raw.githubusercontent.com/jarcities/codejenn/HEAD/src/api-core/main.py>
  - <https://raw.githubusercontent.com/jarcities/codejenn/HEAD/src/api-core/build_model.py>
  - <https://raw.githubusercontent.com/jarcities/codejenn/HEAD/src/api-core/testing.py>
  - <https://raw.githubusercontent.com/jarcities/codejenn/HEAD/tutorials/supported_layers.md>
  - <https://github.com/jarcities/codejenn/tree/main/tutorials/01_simple_mlp>
  - <https://raw.githubusercontent.com/jarcities/codejenn/HEAD/tutorials/01_simple_mlp/simple_mlp.py>
  - <https://raw.githubusercontent.com/jarcities/codejenn/HEAD/tutorials/06_speed_test/readme.md>
  - <https://raw.githubusercontent.com/jarcities/codejenn/HEAD/tutorials/06_speed_test/mlp/run.sh>
  - <https://raw.githubusercontent.com/jarcities/codejenn/HEAD/tutorials/06_speed_test/mlp/test.py>
  - <https://raw.githubusercontent.com/jarcities/codejenn/HEAD/tutorials/06_speed_test/mlp/test.cpp>
  - <https://raw.githubusercontent.com/jarcities/codejenn/HEAD/tutorials/06_speed_test/mlp/train.py>
  - <https://raw.githubusercontent.com/jarcities/codejenn/HEAD/tutorials/06_speed_test/cnn/run.sh>
  - <https://raw.githubusercontent.com/jarcities/codejenn/HEAD/tutorials/06_speed_test/cnn/test.py>
  - <https://raw.githubusercontent.com/jarcities/codejenn/HEAD/tutorials/06_speed_test/cnn/train.py>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/jarcities/codejenn`) · [data/wave8/enrich/raw/github_com_jarcities_codejenn.json](../../../data/wave8/enrich/raw/github_com_jarcities_codejenn.json) (enrichment confidence 0.7)

</details>
