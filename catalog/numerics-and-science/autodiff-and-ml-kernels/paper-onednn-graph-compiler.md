# oneDNN Graph Compiler

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · ⚪ unknown

> Intel's tensor compiler backend for oneDNN Graph API that fuses MLP/MHA subgraphs; beat oneDNN post-op fusion and TVM. Removed in oneDNN 3.8.

| | |
|---|---|
| **Beats** | oneDNN primitives with post-op fusion; TVM auto-scheduler |
| **Claimed result** | BERT Large 1.12x and DLRM 1.15x over oneDNN post-op fusion; MHA total time 2.3x (FP32) and 2.4x (Int8) lower than post-op fusion; 2.4x (MLP) and 6.2x (MHA) average over TVM, 3.8x on Int8 matmul total time; MLP total time 4% worse than primitives on FP32, 6% better on Int8 |
| **Workload** | Tensor compiler fusing MLP and MHA subgraphs, BERT-Large and DLRM end to end. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Platinum 8358, 32 cores |
| **Links** | [repository](https://github.com/uxlfoundation/oneDNN/tree/v3.7/src/graph/backend/graph_compiler) · [benchmark](https://arxiv.org/pdf/2301.01333) |

## Verdict

Intel's own arXiv paper (2301.01333) measured on a 32-core Xeon Platinum 8358: BERT-Large 1.12x and DLRM 1.15x end to end over oneDNN post-op fusion, MHA 2.3x (FP32) / 2.4x (Int8) lower time than post-op fusion, and 2.4x (MLP) / 6.2x (MHA) average over TVM with auto-scheduler; FP32 MLP was 4% slower than oneDNN primitives and Int8 MLP 6% faster. No compiler, flags or benchmark scripts are given.

## Use it when

- Only if you are pinned to oneDNN 3.0-3.7 on Intel Xeon and run Int8 or FP32 BERT-style MHA blocks through the Graph API (the paper reports 2.3-2.4x lower MHA time than post-op fusion).
- As a reference design for template-plus-fusion tensor compilers, if you are building your own fused MLP/attention codegen for CPUs.
- Reproducing the paper's BERT-Large / DLRM numbers on a Xeon Platinum 8358-class machine with a matching oneDNN 3.x build.

## Skip it when

- New projects: oneDNN 3.7 deprecated the backend and 3.8 removed it; current oneDNN covers SDPA and gated MLP through its regular Graph API backend.
- FP32 MLP: the paper measured it 4% slower than plain oneDNN primitives.
- Non-Intel or non-x86 targets: the paper only measured a Xeon Platinum 8358 and the docs list no other supported platforms.
- Builds with the DPC++/SYCL CPU runtime: its CMake fails with an unsupported CPU runtime error for DPCPP.
- Anything that needs stability: the backend was always labelled experimental.

## How it is fast

It lowers through two IRs: a Graph IR that keeps op semantics for graph-level passes (layout propagation, constant-weight preprocessing, FP32-to-Int8 conversion with quantization-parameter folding) and a C-like Tensor IR for code generation. Compute-heavy ops are expanded from expert-written templates around tuned microkernels instead of being searched by an auto-scheduler. Fine-grain fusion inserts neighbouring ops at anchor points inside the template loops, and coarse-grain fusion merges the parallel outer loops of several fused ops, with buffer reuse by liveness analysis.

## Compared with alternatives

LIBXSMM and Optimizing-DGEMM are kernel libraries you call directly, while this was a graph-level fuser behind the oneDNN Graph API; pick it only for whole-subgraph MHA/MLP fusion on an old oneDNN, since it is no longer maintained.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | part of oneDNN (static or shared per DNNL_LIBRARY_TYPE); optional LLVM &gt;= 10 if the llvm JIT is selected, otherwise the builtin JIT needs nothing extra |
| **Minimum toolchain** | not documented beyond oneDNN 3.x's own requirements |
| **Platforms** | x86-64 Intel Xeon as measured; other platforms not documented; OMP/TBB CPU runtimes only (DPCPP rejected) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — same oneDNN Graph API, chosen at build time; frameworks needed no code change, but only oneDNN &lt;= 3.7 ships it |

## Gotchas

- Off by default; it had to be enabled at CMake time, and runtime env vars ONEDNN_EXPERIMENTAL_GRAPH_COMPILER_CPU_JIT (llvm/c/builtin) and _OPT_LEVEL change codegen.
- Removed in oneDNN v3.8, so upgrading oneDNN silently drops back to the regular dnnl backend's fusions.
- The 'c' JIT mode is unavailable on Windows and macOS per its CMake file.

## Known shortcomings

- Intel's own arXiv paper, no venue, compiler or flags; code lives inside the oneDNN repo (itself a baseline), no subdirectory named.
- Discontinued: deprecated in oneDNN v3.7 and removed in v3.8; code (Apache-2.0) only in v3.7 tree; always experimental; build refuses the DPCPP CPU runtime.

## Caveats and trade-offs

Paper only for this entry: the paper points to the oneDNN repo (a baseline itself) but no dedicated repo was opened, so repo_url is null and license is unconfirmed. Compiler flags not stated; FP32 matmul is slower than primitives.

Embedded as a component of oneDNN; fusion gains only for graph-level patterns.

## Maintenance

Discontinued: deprecated in oneDNN 3.7 and removed in 3.8 (2025); the code remains readable at the v3.7 tag under Apache-2.0, but it is a reference, not something to adopt.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** Intel's own arXiv paper (no venue stated) reports 2.4x/6.2x over TVM, 1.12x BERT-Large and 1.15x DLRM over oneDNN post-op fusion, FP32 4% worse / Int8 6% better than primitives on a Xeon Platinum 8358; no compiler, flags or benchmark code given, so first-party C.
- **Verifier notes:** Paper says the graph compiler is open source and embedded in oneDNN (cites github.com/oneapi-src/oneDNN) but names no subdirectory; repo_url left null and has_code unchanged since I did not open the oneDNN tree. Vendor (Intel) paper, so first-party.
- **Fields the verifier corrected:** `claimed_speedup`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2301.01333>
  - <https://arxiv.org/pdf/2301.01333>
- **Sources the enricher read:**
  - <https://arxiv.org/abs/2301.01333>
  - <https://arxiv.org/pdf/2301.01333>
  - <https://uxlfoundation.github.io/oneDNN/v3.6/dev_guide_graph_compiler.html>
  - <https://github.com/uxlfoundation/oneDNN/releases/tag/v3.7>
  - <https://github.com/uxlfoundation/oneDNN/releases/tag/v3.8>
  - <https://github.com/uxlfoundation/oneDNN>
  - <https://raw.githubusercontent.com/uxlfoundation/oneDNN/v3.7/src/graph/backend/graph_compiler/CMakeLists.txt>
  - <https://raw.githubusercontent.com/uxlfoundation/oneDNN/v3.7/src/graph/backend/CMakeLists.txt>
  - <https://raw.githubusercontent.com/uxlfoundation/oneDNN/v3.7/cmake/options.cmake>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `paper:onednn-graph-compiler`) · [data/wave8/enrich/raw/paper_onednn_graph_compiler.json](../../../data/wave8/enrich/raw/paper_onednn_graph_compiler.json) (enrichment confidence 0.75)

</details>
