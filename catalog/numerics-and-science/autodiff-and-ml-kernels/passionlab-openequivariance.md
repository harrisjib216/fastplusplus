# OpenEquivariance

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python/C++ (JIT-generated CUDA, HIP and SYCL kernels)` · `BSD-3-Clause` · 🟢 active

> JIT GPU kernel generator for e3nn-style Clebsch-Gordan tensor products and fused graph convolutions; claims up to 10x over e3nn.

| | |
|---|---|
| **Beats** | e3nn (torch.compile max-autotune with CUDA graphs in the harness); also compared with NVIDIA cuEquivariance and FlashTP |
| **Claimed result** | README: 'We provide up to an order of magnitude acceleration over e3nn' and performance 'on par with the latest version of NVIDIA cuEquivariance'; docs/index.rst: 'up to an order of magnitude speedup over e3nn and competitive performance with NVIDIA's cuEquivariance'. Docs (tests_and_benchmarks.rst) and CHANGELOG v0.4.0: 'up to 2x speedup over FlashTP's fused kernels'. Paper abstract (SIAM ACDA25, arXiv 2501.13986; WebSearch snippet only, paper not opened): fused kernels give up to 4.5x forward and 3x (another snippet says 3.5x) backward speedup over cuEquivariance, &gt;10x over e3nn, and up to 5.3x (another snippet: 5.4x) MACE inference speedup over the original unoptimized version. One snippet also gives 5.3x over e3nn and 1.5x over cuEquivariance in FP32, and 6.6x and 1.43x in FP64. The snippet figures disagree between paper versions and need checking against the PDF. |
| **Workload** | Clebsch-Gordan tensor products and fused equivariant graph convolutions for MACE, NequIP, DiffDock and e3nn tetris-poly problems, forward and backward, float32 and float64, run by tests/benchmark.py (uvu, uvw, roofline and conv suites; 100 warmup and 100 timed iterations, PRNG seed 11111). |
| **Metric** | throughput |
| **Hardware** | Paper benchmarks: NVIDIA A100-SXM-80GB at Lawrence Berkeley National Laboratory (docs/tests_and_benchmarks.rst). The docs also list example invocations for an NVIDIA A5000 and note that the roofline slope and peak are only correct on an A100. |
| **Compiler and flags** | Not stated (kernels are JIT-compiled at runtime; README asks for PyTorch and GCC 9+). |
| **Adoption** | 170 stars, 17 forks (github.com page, 2026-10-03); pip package 'openequivariance'; works with MACE and NequIP |
| **Last commit** | 2026-09-27 |
| **Links** | [repository](https://github.com/PASSIONLab/OpenEquivariance) · [benchmark](https://github.com/PASSIONLab/OpenEquivariance/blob/main/docs/tests_and_benchmarks.rst) |

## Verdict

All headline claims are first-party. The README claims up to 10x over e3nn, with the harness's e3nn baseline compiled by torch.compile max-autotune with CUDA graphs, and parity with cuEquivariance; the docs claim up to 2x over FlashTP's fused kernels, measured on an A100-SXM-80GB at LBNL/NERSC Perlmutter with no compiler or flags stated. The paper abstract (SIAM ACDA25, seen only as search snippets whose figures vary by version) gives up to 4.5-4.8x forward and 3x backward over cuEquivariance, &gt;10x over e3nn and up to 5.3-5.4x MACE inference speedup. One outside data point: the Nequix maintainer reported 2.5x (1000 atoms) and 3.3x (1728 atoms) end-to-end gains from adding the oeq kernels to Nequix's PyTorch port, on an A100 per the thread.

## Use it when

- Training or running MACE, NequIP, Nequix or SevenNet-style models on NVIDIA or AMD GPUs where e3nn tensor products dominate step time; NequIP documents an OpenEquivariance acceleration path.
- Large molecular graphs where unfused e3nn message passing runs out of memory: the docs say the MACE carbon.xyz benchmark (158K edges) needs an 80GB GPU with e3nn, while the fused oeq convolution is expected to fit.
- You need an open-source alternative to NVIDIA cuEquivariance (closed-source kernel package), or you need AMD (HIP), JAX or Intel XPU (beta SYCL) support.
- Models that need float64 tensor products or higher-order derivatives (forces, force-matching training, Hessian-like terms).

## Skip it when

- Tensor products outside pure 'uvu'/'uvw': mixed instruction types, other connection modes and non-trainable instructions are unsupported. Per a NequIP docs snippet seen in search, Allegro models cannot use it.
- CPU-only systems, or nodes with mixed GPU generations: there is no CPU path, and kernels are compiled for the compute capability of the first visible GPU only.
- You need an independent head-to-head against FlashTP at high angular momentum: issue #171 asked for one and got no answer, and the '2x over FlashTP' claim is first-party.
- MACE symmetric contraction: it is beta, needs e3nn, is not exposed at the package top level, and the docs note user reports of weak backward-pass performance.
- AMD GPUs with versions before 0.7.0: a HIP warp-sync bug produced non-conservative forces (issue #211).

## How it is fast

It exploits the sparsity of the Clebsch-Gordan (Wigner 3j) coefficient tensor. At JIT time the generator enumerates the nonzeros and writes them as hex float literals into fully unrolled CUDA/HIP code from Jinja templates (ComputationSchedule.py, loop_unroll_tp.cuh), so no sparse indexing happens at run time. Each warp works out of its own shared-memory slice: the problem is split into segments whose irreps and weights fit per-warp shared memory, and 'uvw' paths use a warp-level, register-tiled matmul (wmm.cuh). The fused convolution never materializes per-edge messages; it reduces with atomics, or deterministically over receiver-sorted edges with a transpose permutation for the backward pass, with optional Kahan summation.

## Compared with alternatives

Pick it over cuEquivariance when you need open-source kernels, AMD/Intel GPUs, JAX, float64 or the memory-saving fused convolution. Pick cuEquivariance for NVIDIA-only, vendor-supported kernels that also cover Allegro. batmobile reports larger single-kernel gains over e3nn on an RTX 3090 but covers a much narrower set of operations and frameworks.

## Integration

| | |
|---|---|
| **Form** | module (pip package 'openequivariance' plus a C++ extension; kernels are JIT-compiled at first use, with NVRTC on CUDA per issue #162) |
| **Dependencies** | PyTorch &gt;= 2.4 (&gt;= 2.10 for the precompiled extension, AOTI, export and Intel XPU) or JAX &gt; 0.5.0 with the separate openequivariance_extjax package; CUDA or HIP toolkit, or oneAPI icpx for SYCL; e3nn only for tests, benchmarks and symmetric contraction |
| **Minimum toolchain** | GCC 9+ (c++ --version &gt;= 9.0), Linux, Python with PyTorch or JAX |
| **Platforms** | Linux GPUs only: NVIDIA (run-tested V100, A100-40/80GB, A5000, T4, H100), AMD (MI250x, MI300x), Intel Data Center GPU Max via beta SYCL; no CPU backend |
| **Thread safety** | Not documented; CUDA streams and multiple devices are supported since v0.2.0, and the non-deterministic (atomics) convolution gives run-to-run rounding differences. |
| **Drop-in for the baseline** | partial — TPProblem mirrors e3nn's o3.TensorProduct (internal_weights=False required) and matches e3nn up to rounding for 'uvu' with multiplicity-1 second inputs; other configurations, including all 'uvw', match only after reordering weights with reorder_weights_from_e3nn/to_e3nn; only 'uvu'/'uvw' are covered |

## Gotchas

- The first import builds a C++ extension, which can take minutes; issues #156 and #207 report import hangs on a stale build lock (PR #209 added a timeout), and #175 reports a compilation cache that did not persist on L40S/RTX 6000.
- Modules saved after torch.compile or torch.export load only on the same GPU architecture; uncompiled modules recompile kernels when loaded on another GPU.
- deterministic=True (the faster, atomics-free convolution) requires edges sorted by receiver, inputs permuted with receiver_perm, and a sender transpose permutation; deterministic=False accepts any order but uses atomics.
- Before v0.7.0 the HIP kernels used a block-level thread fence where CUDA used __syncwarp. On an MI300, NequIP-OAM-L (l_max = 3) gave non-conservative forces: 9.3-32.8 meV/A force differences and +79.7 eV/ns NVE energy drift (issue #211, OEQ 0.6.8). It was fixed in PR #217 on 2026-09-10, so upgrade on AMD.

## Known shortcomings

- Tier C: README gives order-of-magnitude over e3nn and docs 2x over FlashTP, first-party; the ACDA25 paper (arXiv 2501.13986: &gt;10x e3nn, up to 4.5x forward over cuEquivariance) was blocked and seen only as snippets. B candidate once the paper is opened.
- Issue #211: an AMD HIP warp-sync bug gave non-conservative forces on NequIP-OAM-L at l_max=3 (9.3-32.8 meV/A, +79.7 eV/ns NVE drift, OEQ 0.6.8), fixed in PR #217 on 2026-09-10 (v0.7.0). Paper abstract snippets give 4.5x or 4.8x forward over cuEquivariance depending on version; the paper is still unopened.
- The repo holds a harness (tests/benchmark.py, docs name an A100-SXM-80GB) but no committed numbers, and e3nn/cuEquivariance versions are unpinned; a newer paper snippet claims only 1.3x over cuEquivariance and 6.2x on MACE (older: 4.5x).

## Caveats and trade-offs

The headline figures are first-party README statements with no per-problem numbers on the pages I could open, so tier C is a floor. The paper (SIAM ACDA25) is peer reviewed and the benchmark code is public with A100-SXM-80GB stated and exact reproduction commands in docs/tests_and_benchmarks.rst, so a verifier with paper access may justify tier B, or A if the paper states compiler and flags. The README sentence is garbled ('up to an order of magnitude acceleration over e3nn perform on par with...'), which is quoted as is. The harness removes e3nn's torch-compile variant for float64 'benzene' because it runs out of memory, and for 'limited-memory' GPUs drops expensive tests. The 2x claim over FlashTP is against FlashTP's fused kernels only. Opened: README, LICENSE, CHANGELOG.md, docs/tests_and_benchmarks.rst and tests/benchmark.py via raw.githubusercontent.com, plus the repo tree and commit pages on github.com. [retier] Paper not opened (arXiv, author site, SIAM, researchgate and alphaxiv all blocked from this container); every paper figure is from WebSearch snippets only, and the snippets disagree across paper versions: earlier snippets give up to 4.5x forward and 3x or 3.5x backward over cuEquivariance, &gt;10x over e3nn and 5.3x or 5.4x MACE inference speedup, while a 2026-10-03 snippet gives up to 1.3x over cuEquivariance, &gt;10x over e3nn and up to 6.2x MACE inference speedup. The README itself claims only 'up to an order of magnitude acceleration over e3nn' and performance 'on par with' cuEquivariance, which is consistent with the smaller cuEquivariance figure. The harness is public (tests/benchmark.py; the e3nn baseline is the torch.compile max-autotune plus CUDA-graphs variant, with an uncompiled variant also available), but the bench extra in openequivariance/pyproject.toml leaves e3nn, cuequivariance, cuequivariance-torch and cuequivariance-ops-torch-cu12 unpinned, so a rerun compares against whatever versions are current, and no result tables are committed. Docs also claim up to 2x over FlashTP's fused kernels (first-party, no numbers in the repo); the FlashTP README does not mention OpenEquivariance.

Supports most 'uvu' and 'uvw' e3nn tensor products, not all of e3nn. Results equal e3nn up to rounding for many configurations; for 'uvw' connection modes the weights must be reordered (reorder_weights_from_e3nn/to_e3nn). Fused convolution has an atomics mode that is non-deterministic and a deterministic mode needing receiver-sorted indices plus a transpose permutation. JIT compile at first use; needs a CUDA, HIP or SYCL (beta) toolchain; PyTorch and JAX frontends.

## Maintenance

Actively maintained academic project (v0.7.0 on 2026-09-10, SYCL backend merged 2026-09-23), BSD-3-Clause (LBNL/UC Berkeley) and pip-installable; it ships frequent correctness fixes, so pin a recent version.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** On the pages I could open, the claims are first-party summaries: the README says 'up to an order of magnitude acceleration over e3nn', and docs/tests_and_benchmarks.rst and CHANGELOG v0.4.0 say 'up to 2x speedup over FlashTP'. The public harness tests/benchmark.py times e3nn, cue and oeq, and the docs state an A100-SXM-80GB, but no per-problem numbers, compiler or flags were visible, so the tier is C. The peer-reviewed SIAM ACDA25 paper (arXiv 2501.13986) would support B, but I saw its abstract only as WebSearch snippets because arXiv is egress-blocked.
- **Verifier notes:** Accurate record; only the star count and the claimed_speedup text changed (paper-abstract figures added and marked as snippet only). This is a B candidate: once arxiv.org/abs/2501.13986 (or the SIAM ACDA25 version, DOI 10.1137/1.9781611978759.3) can be opened, check the per-problem e3nn and cuEquivariance figures and retier.
- **Fields the verifier corrected:** `stars_or_usage`, `claimed_speedup`, `benchmark_url`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier; semi-independent: Nequix maintainer (discussion #5) measured oeq kernels 2.5x (1000 atoms) and 3.3x (1728 atoms) end-to-end on the Nequix PyTorch port, A100; he also contributed OEQ JAX lowerings; retier check 14
- **Pages the verifier opened:**
  - <https://github.com/PASSIONLab/OpenEquivariance>
  - <https://github.com/PASSIONLab/OpenEquivariance/commits>
  - <https://github.com/PASSIONLab/OpenEquivariance/tree/main/docs>
  - <https://raw.githubusercontent.com/PASSIONLab/OpenEquivariance/HEAD/README.md>
  - <https://raw.githubusercontent.com/PASSIONLab/OpenEquivariance/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/PASSIONLab/OpenEquivariance/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/PASSIONLab/OpenEquivariance/HEAD/docs/tests_and_benchmarks.rst>
  - <https://raw.githubusercontent.com/PASSIONLab/OpenEquivariance/HEAD/docs/index.rst>
  - <https://raw.githubusercontent.com/PASSIONLab/OpenEquivariance/HEAD/docs/models.rst>
  - <https://raw.githubusercontent.com/PASSIONLab/OpenEquivariance/HEAD/tests/benchmark.py>
- **Sources the enricher read:**
  - <https://github.com/PASSIONLab/OpenEquivariance/tree/main/openequivariance/openequivariance>
  - <https://github.com/PASSIONLab/OpenEquivariance/tree/main/openequivariance/openequivariance/templates>
  - <https://github.com/PASSIONLab/OpenEquivariance/tree/main/openequivariance/openequivariance/core>
  - <https://raw.githubusercontent.com/PASSIONLab/OpenEquivariance/HEAD/README.md>
  - <https://raw.githubusercontent.com/PASSIONLab/OpenEquivariance/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/PASSIONLab/OpenEquivariance/HEAD/docs/tests_and_benchmarks.rst>
  - <https://raw.githubusercontent.com/PASSIONLab/OpenEquivariance/HEAD/docs/supported_ops.rst>
  - <https://raw.githubusercontent.com/PASSIONLab/OpenEquivariance/HEAD/docs/installation.rst>
  - <https://raw.githubusercontent.com/PASSIONLab/OpenEquivariance/HEAD/docs/models.rst>
  - <https://raw.githubusercontent.com/PASSIONLab/OpenEquivariance/HEAD/docs/index.rst>
  - <https://raw.githubusercontent.com/PASSIONLab/OpenEquivariance/HEAD/tests/benchmark.py>
  - <https://raw.githubusercontent.com/PASSIONLab/OpenEquivariance/HEAD/openequivariance/openequivariance/core/ComputationSchedule.py>
  - <https://raw.githubusercontent.com/PASSIONLab/OpenEquivariance/HEAD/openequivariance/openequivariance/core/LoopUnrollTP.py>
  - <https://raw.githubusercontent.com/PASSIONLab/OpenEquivariance/HEAD/openequivariance/openequivariance/templates/loop_unroll_tp.cuh>
  - <https://raw.githubusercontent.com/PASSIONLab/OpenEquivariance/HEAD/openequivariance/openequivariance/templates/loop_unroll_conv_atomic.cuh>
  - <https://raw.githubusercontent.com/PASSIONLab/OpenEquivariance/HEAD/openequivariance/openequivariance/templates/wmm.cuh>
  - <https://github.com/PASSIONLab/OpenEquivariance/issues?q=is%3Aissue>
  - <https://github.com/PASSIONLab/OpenEquivariance/issues/211>
  - <https://github.com/PASSIONLab/OpenEquivariance/issues/171>
  - <https://github.com/PASSIONLab/OpenEquivariance/pull/217>
  - <https://github.com/PASSIONLab/OpenEquivariance/commits/main>
  - <https://github.com/atomicarchitects/nequix/discussions/5>
  - <https://github.com/SNU-ARC/flashTP>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/passionlab/openequivariance`) · [data/wave8/enrich/raw/github_com_passionlab_openequivariance.json](../../../data/wave8/enrich/raw/github_com_passionlab_openequivariance.json) (enrichment confidence 0.7)

</details>
