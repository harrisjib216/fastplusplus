# batmobile (CUDA kernels for equivariant GNNs)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `CUDA C++ with PyTorch bindings` · `MIT` · 🟢 active

> Hand-unrolled FP32 CUDA kernels for L_max=3 spherical harmonics and Clebsch-Gordan tensor products, timed against generic e3nn.

| | |
|---|---|
| **Beats** | e3nn (PyTorch library for E(3)-equivariant neural networks; generic implementation) |
| **Claimed result** | README (RTX 3090, N_atoms=1000, C=32, \~20 neighbours/atom): spherical harmonics L=3 0.142 ms (e3nn) vs 0.012 ms (11.8x); tensor product 1.847 ms vs 0.089 ms (20.8x); TP backward 3.21 ms vs 0.156 ms (20.6x); fused SH+TP 0.574 ms vs 0.413 ms (1.39x), listed under an 'e3nn (baseline)' column, but the matching script benchmarks/benchmark_fused_sh_tp.py only compares fused against batmobile's own unfused SH+TP+scatter pipeline, so that row appears to be fused vs unfused batmobile rather than vs e3nn. At N_atoms=5000, C=64, \~30 neighbours: fused 5.935 ms vs unfused batmobile 8.604 ms (1.45x). |
| **Workload** | Spherical harmonics (L=3), tensor product with Clebsch-Gordan coefficients (forward and backward) and fused SH+TP for MACE/NequIP/Allegro style models, N_atoms=1000, C=32, about 20 neighbours per atom, on RTX 3090. |
| **Metric** | latency |
| **Hardware** | NVIDIA RTX 3090; host CPU not stated |
| **Compiler and flags** | CUDA 12.x and PyTorch 2.0+ (README); flags not stated |
| **Adoption** | 44 stars |
| **Last commit** | 2026-01-17 |
| **Links** | [repository](https://github.com/Infatoshi/batmobile) · [benchmark](https://github.com/Infatoshi/batmobile) |

## Verdict

Single-author timings on one RTX 3090 (CUDA 12.x, PyTorch 2.x, -O3 --use_fast_math, host CPU not stated) at 1,000 atoms, C=32, about 20 neighbours: SH 0.012 ms vs e3nn 0.142 ms (11.8x, CUDA-event timed), unweighted TP 20.8x and TP backward 20.6x over e3nn, while the 1.39x 'Fused SH+TP' row and the 1.45x at-scale row compare fused against batmobile's own unfused pipeline. The TP comparison does less work than e3nn's FullTensorProduct, and the scripts cannot run at HEAD without fixing the module name.

## Use it when

- Custom MACE/NequIP-style models on Ampere consumer GPUs (built for RTX 3090, sm_86) that use exactly L_max=3 irreps 0e+1o+2e+3o in FP32.
- Prototyping or studying how fused, unrolled CG kernels beat e3nn's generic einsum/codegen path on small irreps.
- Spherical harmonics alone for L_max 0-6 on unit vectors, where the SH kernel gave 11.8x over e3nn at 1,000 edges in the README.
- Workloads whose bottleneck is the unweighted SH x feature product per edge, where the fused kernel avoids materializing Y_lm.

## Skip it when

- Production MD runs: 3 commits, no releases, no CI, and the package does not import at HEAD (see gotchas).
- Any L_max other than 3 for tensor products; the binding checks that inputs have exactly 16 components.
- FP64 or mixed-precision simulations: every binding requires float32 (the README says FP32 only, no FP64).
- GPUs other than sm_86-compatible: setup.py builds SASS only for compute_86/sm_86 with no PTX, so A100 (sm_80) and Hopper/Blackwell need the flag edited.
- If you need a vetted fast equivariant backend: issues #1 and #3 point to OpenEquivariance and NVIDIA cuEquivariance, and batmobile has not been benchmarked against either.

## How it is fast

For L_max=3 all 34 CG paths and their 611 non-zero coefficients are generated as compile-time constants (scripts/gen_fused_tp.py, cg_coefficients_l3.cuh) and fully unrolled, so no sparse CG tables are read and no per-path kernel launches happen. The weighted kernel gives each (sample, output channel) pair a thread block that accumulates in shared memory. The fused SH+TP kernel computes the 16 harmonics in registers from closed-form polynomials and uses them right away, so Y_lm never goes to global memory.

## Compared with alternatives

No equivariant-GNN sibling is catalogued yet; the nearest siblings (tiny-cuda-nn's fully fused MLPs, Liger-Kernel's fused PyTorch ops) target other layers, so batmobile is only worth considering as a readable reference for fused L_max=3 SH/CG kernels, not as a replacement for them.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | PyTorch &gt;=2.0, NumPy &gt;=1.20, CUDA toolkit, pybind11 (via torch.utils.cpp_extension); e3nn, torch_scatter and torch_cluster for tests/benchmarks |
| **Minimum toolchain** | C++17 (g++ and nvcc -std=c++17); CUDA 12.x per README (LLMS.txt says 11.8+); Python &gt;=3.9 |
| **Platforms** | NVIDIA sm_86 as shipped (RTX 3090 / RTX 30xx); other archs need TORCH_CUDA_ARCH_LIST and the hard-coded -gencode flag in setup.py changed; Linux assumed, others not documented |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Broken import at HEAD: commit e4fa3a9 'Rename project from batteries to batmobile' renamed the built module to '_batmobile' (setup.py, bindings.cpp, autograd.py), but python/batmobile/__init__.py and every benchmark/test script still do 'import _batteries', so 'import batmobile' and the README benchmark commands fail until patched; benchmark_e2e_mace.py also imports a nonexistent 'python.autograd'.
- The README autograd example imports SphericalHarmonics and TensorProduct from batmobile.autograd, but that module defines SphericalHarmonicsFunction, TensorProductFunction and lowercase wrappers.
- The tensor-product speedup is not equal work: tests/benchmark_tensor_product.py times the unweighted tensor_product_simple, which sums paths into 16 outputs (l &lt;= 3), against e3nn o3.FullTensorProduct, which outputs every (l1, l2) -&gt; l path up to l=6; the weighted, channelled kernel has no e3nn timing ('too slow for direct comparison').
- spherical_harmonics expects already-normalized vectors (docstring: 'must be normalized'); the benchmark calls e3nn with normalize=False to match.

## Known shortcomings

- README 'Fused SH+TP 1.39x' sits under the e3nn column but its script compares fused vs batmobile's own unfused path; README-named benchmarks/benchmark_tensor_product.py is 404.
- Claim not reproducible at HEAD: rename commit e4fa3a9 left __init__.py and every bench/test importing `_batteries` while the build produces `_batmobile`, so `import batmobile` fails; the README autograd example imports names that do not exist; TP 20.8x is unequal work (unweighted 16-output TP vs e3nn FullTensorProduct with all paths up to l=6); setup.py builds sm_86 only.

## Caveats and trade-offs

Small project (44 stars, 3 commits, all dated 2026-01-17 and co-authored with Claude), first-party numbers from one GPU with no compiler flags or host CPU. Baseline is the generic e3nn, not an optimised library such as cuEquivariance or OpenEquivariance. Benchmark scripts do not back every README row: the README names benchmarks/benchmark_tensor_product.py, which does not exist (raw fetch 404); benchmarks/benchmark_tp_backward.py times only batmobile (no e3nn baseline; timing via time.perf_counter over 100 launches); benchmarks/benchmark_fused_sh_tp.py compares fused vs batmobile's unfused pipeline, not e3nn, although the README places its 1.39x row under the e3nn column. Only the spherical-harmonics script and the end-to-end MACE script time e3nn directly. Covers L_max=3 only.

Hand-written kernels for specific L_max and layouts; fused operators; PyTorch extension only.

## Maintenance

MIT-licensed, 44 stars, all 3 commits on 2026-01-17 (co-authored with an AI assistant), and three open issues with no maintainer replies; small enough to vendor and study, but it needs a one-line import fix and an arch-flag edit before it builds and runs anywhere but an RTX 30xx.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README Benchmarks table gives first-party RTX 3090 timings against e3nn, and public scripts exist (benchmarks/bench_spherical_harmonics.py times e3nn.o3.spherical_harmonics with CUDA events; benchmarks/benchmark_e2e_mace.py has an e3nn per-op breakdown). No compiler flags or host CPU are stated, and not every README row has a matching baseline script, so C, not A.
- **Verifier notes:** Metadata confirmed via github.com page: MIT (LICENSE 'Copyright (c) 2025 Batteries Authors'), 44 stars, 7 forks, not archived, not a fork, 3 commits all on 2026-01-17. Shortcoming to record: README row 'Fused SH+TP' attributed to e3nn is backed by a fused-vs-unfused batmobile script; README-named TP benchmark script is missing.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Infatoshi/batmobile>
  - <https://github.com/Infatoshi/batmobile/commits>
  - <https://github.com/Infatoshi/batmobile/tree/HEAD/benchmarks>
  - <https://raw.githubusercontent.com/Infatoshi/batmobile/HEAD/README.md>
  - <https://raw.githubusercontent.com/Infatoshi/batmobile/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Infatoshi/batmobile/HEAD/benchmarks/bench_spherical_harmonics.py>
  - <https://raw.githubusercontent.com/Infatoshi/batmobile/HEAD/benchmarks/benchmark_fused_sh_tp.py>
  - <https://raw.githubusercontent.com/Infatoshi/batmobile/HEAD/benchmarks/benchmark_tp_backward.py>
  - <https://raw.githubusercontent.com/Infatoshi/batmobile/HEAD/benchmarks/benchmark_e2e_mace.py>
  - <https://raw.githubusercontent.com/Infatoshi/batmobile/HEAD/benchmarks/benchmark_fused_mp.py>
- **Sources the enricher read:**
  - <https://github.com/Infatoshi/batmobile>
  - <https://github.com/Infatoshi/batmobile/commits/main>
  - <https://github.com/Infatoshi/batmobile/tree/main/tests>
  - <https://github.com/Infatoshi/batmobile/issues>
  - <https://github.com/Infatoshi/batmobile/issues/1>
  - <https://github.com/Infatoshi/batmobile/issues/3>
  - <https://raw.githubusercontent.com/Infatoshi/batmobile/HEAD/README.md>
  - <https://raw.githubusercontent.com/Infatoshi/batmobile/HEAD/LLMS.txt>
  - <https://raw.githubusercontent.com/Infatoshi/batmobile/HEAD/setup.py>
  - <https://raw.githubusercontent.com/Infatoshi/batmobile/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/Infatoshi/batmobile/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Infatoshi/batmobile/HEAD/python/batmobile/__init__.py>
  - <https://raw.githubusercontent.com/Infatoshi/batmobile/HEAD/python/batmobile/autograd.py>
  - <https://raw.githubusercontent.com/Infatoshi/batmobile/HEAD/python/bindings.cpp>
  - <https://raw.githubusercontent.com/Infatoshi/batmobile/HEAD/src/tensor_product/tensor_product.cu>
  - <https://raw.githubusercontent.com/Infatoshi/batmobile/HEAD/src/spherical_harmonics/spherical_harmonics.cu>
  - <https://raw.githubusercontent.com/Infatoshi/batmobile/HEAD/src/message_passing/fused_sh_tp.cu>
  - <https://raw.githubusercontent.com/Infatoshi/batmobile/HEAD/tests/benchmark_tensor_product.py>
  - <https://raw.githubusercontent.com/Infatoshi/batmobile/HEAD/tests/test_tensor_product.py>
  - <https://raw.githubusercontent.com/Infatoshi/batmobile/HEAD/benchmarks/bench_spherical_harmonics.py>
  - <https://raw.githubusercontent.com/Infatoshi/batmobile/HEAD/benchmarks/benchmark_fused_sh_tp.py>
  - <https://raw.githubusercontent.com/Infatoshi/batmobile/HEAD/benchmarks/benchmark_e2e_mace.py>
  - <https://raw.githubusercontent.com/Infatoshi/batmobile/HEAD/examples/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/infatoshi/batmobile`) · [data/wave8/enrich/raw/github_com_infatoshi_batmobile.json](../../../data/wave8/enrich/raw/github_com_infatoshi_batmobile.json) (enrichment confidence 0.8)

</details>
