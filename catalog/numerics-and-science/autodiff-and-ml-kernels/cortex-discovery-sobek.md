# Sobek (streaming equivariant tensor-product convolutions)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python/CUDA (generated CUDA kernels, PyTorch extension)` · `Apache-2.0` · 🟢 active

> Generated-CUDA PyTorch backend for equivariant tensor-product graph convolutions; claims 1.2x-49.7x over OpenEquivariance with bounded memory.

| | |
|---|---|
| **Beats** | OpenEquivariance (primary), also cuEquivariance and e3nn |
| **Claimed result** | Search snippet of arXiv 2607.18074 abstract: faster in all 75 capacity-matched comparisons across two operator families and all three differentiation orders, 1.2x to 49.7x, peak allocated memory reduced by up to 99%; at the last degree point shared with OpenEquivariance, OpenEquivariance allocates 24.1-27.1 GiB vs Sobek 0.1-0.4 GiB; runs workloads up to two orders of magnitude beyond OpenEquivariance capacity. |
| **Workload** | Edge-conditioned equivariant tensor-product convolution (uvw and uvu operator families), forward, backward and double backward, on capacity-matched grids (16-profile UVW grid, 9-profile UVU grid); also peak memory. |
| **Metric** | throughput |
| **Compiler and flags** | CUDA Toolkit 13.3 recommended (CUDA 12.9 builds about 25% slower per README); PyTorch &gt;= 2.12 JIT extension builder; float32 with ieee or tf32 GEMMs; nvcc flags not stated |
| **Adoption** | 12 stars |
| **Last commit** | 2026-07-24 |
| **Links** | [repository](https://github.com/Cortex-Discovery/sobek) · [benchmark](https://arxiv.org/abs/2607.18074) |

## Verdict

The authors' preprint (arXiv 2607.18074, read only through search snippets) reports Sobek faster in all 75 OpenEquivariance-capacity-matched comparisons (UVW 16-profile and UVU 9-profile grids, forward, backward and double backward), 1.2x to 49.7x, with up to 99% lower peak allocated memory, on an NVIDIA RTX 5090 in fp32 per a search snippet. The repo's harness (sobek/benchmarks/measure.py, runners.py) times medians of CUDA-event samples after warmup, and by default times OpenEquivariance including the phi @ radial_linear weight expansion and receiver sort (an oe_preexpanded variant excludes the expansion); no result files are checked in and the nvcc flags are -O3 plus PyTorch arch flags.

## Use it when

- Training equivariant GNN potentials in PyTorch on NVIDIA GPUs where force training needs double backward and memory, not FLOPs, limits graph size.
- Large or dense graphs (many edges per node, wide irreps) where materializing [E, weight_numel] edge weights blows past GPU memory with OpenEquivariance or e3nn.
- Models whose last radial MLP layer can be handed to the convolution (phi plus projection weight), so the fusion boundary fits.
- Fixed-topology workloads (MD steps on one structure) that benefit from TPConvGraph reuse and CUDA Graph replay.
- Runs that need bitwise-deterministic results, since the kernels avoid atomics.

## Skip it when

- Anything other than float32: no fp64, fp16 or bf16 path (GEMMs can only switch between ieee and tf32).
- Problems that mix uvw and uvu paths in one instruction set, or uvu with unequal input/output multiplicities or spherical-harmonic multiplicity above one; only weighted fully connected uvw and homogeneous channel-wise uvu are supported.
- Non-NVIDIA hardware or environments without a CUDA toolkit for JIT compilation; every new problem shape pays a first-call nvcc compile.
- Production use that needs maturity: version 0.1.0, 5 commits (2026-07-20 to 2026-07-24), no releases, no issue history, single-company authorship.
- Pipelines already built around e3nn/OpenEquivariance's precomputed edge-weight interface and mul_ir layout; using mul_ir mode in Sobek adds transposes and emits an efficiency warning.

## How it is fast

It fuses the last radial linear layer into the convolution and reassociates the computation so edge-local products are reduced straight into bounded receiver-side state, so the per-edge weight tensor, per-edge messages and their adjoints are never materialized. Per-problem CUDA kernels are code-generated from the irreps/instruction spec and JIT-compiled with nvcc -O3 via torch.utils.cpp_extension.load_inline, combined with cuBLAS GEMMs; graph traversal is receiver-owned (CSR by receiver, with a source-ordered pass for gradients), deterministic and atomic-free. A receiver_scratch_bytes budget (default 128 MiB) drives node-chunking and a knapsack-style choice of which receiver aggregates to retain for the backward pass.

## Compared with alternatives

Pick Sobek over OpenEquivariance, cuEquivariance or FlashTP when the per-edge weight tensor is what runs you out of memory or you need double backward at scale and can fuse the final radial layer; pick cuEquivariance or OpenEquivariance for drop-in e3nn compatibility, other dtypes, or a mature dependency, and FlashTP for its published SevenNet end-to-end results (Sobek reports no FlashTP comparison).

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Python &gt;= 3.11, PyTorch &gt;= 2.12 with CUDA, cgen &gt;= 2025.1, a CUDA toolkit usable by PyTorch's JIT extension builder (13.3 recommended); benchmarks extra adds e3nn, OpenEquivariance, torch-geometric 2.8.0, numpy, matplotlib |
| **Minimum toolchain** | Python 3.11, PyTorch 2.12, CUDA Toolkit (13.3 recommended; 12.9 builds about 25% slower per README) |
| **Platforms** | NVIDIA CUDA GPUs only (kernels compiled for the local arch via PyTorch's arch flags) |
| **Thread safety** | not documented (generated CUDA dumps are written atomically; CUDA Graph replay returns session-owned storage overwritten by the next replay unless clone=True) |
| **Drop-in for the baseline** | partial — same mathematical operator and e3nn-style irreps/instruction tuples, but a different call signature (phi plus radial_linear instead of per-edge weights) and a different native feature layout (ir_mul) |

## Gotchas

- First call for each new tensor-product specification compiles CUDA; the extension is cached only when PyTorch, CUDA, GPU arch, problem and codegen settings all match.
- The CUDA toolkit is chosen from CUDA_HOME; the README reports identical kernels about 25% slower when built with CUDA 12.9 instead of 13.3.
- TPConvGraph tensors must not be modified in place, and a user-supplied sender_perm is only structurally checked, not validated as a permutation.
- phi_dim not divisible by four disables aligned float4 radial-embedding loads in receiver-side kernels.

## Known shortcomings

- Tier C: first-party arXiv 2607.18074 preprint (snippet only) with 1.2x-49.7x over OpenEquivariance across 75 comparisons; the repo has a benchmark CLI but no published results and the GPU is unknown. 12 stars.
- v0.1.0 with 5 commits; float32 only; not a drop-in replacement (different call signature and ir_mul layout); no FlashTP comparison. The harness times OpenEquivariance including its phi @ radial_linear expansion and receiver sort (the oe_preexpanded variant leaves the expansion out); paper hardware per snippet is an RTX 5090 in fp32; no result files are checked in.

## Caveats and trade-offs

The paper (arxiv.org abs/html/pdf, pith.science) was EGRESS_BLOCKED, so the numbers are from WebSearch snippets of the abstract and could not be checked against tables; GPU model and per-case numbers unknown. Repo ships a benchmark CLI (suites minimal, scaling, throughput, uvu-throughput; 'matched' command for OpenEquivariance-capacity-matched timing; peak-memory re-measurement with --memory-only) but no checked-in results and no paper PDF (tree: sobek/, tests/, LICENSE, NOTICE, pyproject.toml). Preprint, not peer reviewed; authors are the repo owners (Cortex Discovery GmbH). Speedups are over a partly different formulation (Sobek fuses the final radial projection while baselines take precomputed per-edge weights), and comparisons are capacity-matched against OpenEquivariance, so 1.2x-49.7x is a range over cases, not a typical figure. Float32 only. No evidence of a benchmark against FlashTP (README only lists FlashTP among related libraries). Very young repo: 5 commits between 2026-07-20 and 2026-07-24, 12 stars, 0 forks.

CUDA/PyTorch only, float32 only; requires CUDA toolkit for JIT compile (first call per problem compiles specialised kernels). Supports uvw and homogeneous uvu contractions, fused radial projection so the caller must pass the compact radial embedding plus final projection weight. Deterministic, no atomics, bounded scratch (receiver_scratch_bytes).

## Maintenance

Apache-2.0, version 0.1.0 published in July 2026 by Cortex Discovery GmbH with 12 stars and no activity since 2026-07-24; usable as a pip-installable PyTorch module but young enough to pin and validate against e3nn before trusting it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party arXiv preprint (2607.18074, authors are the repo owners) reports 1.2x-49.7x over OpenEquivariance across 75 capacity-matched comparisons; the repo ships the benchmark CLI (sobek.benchmarks.cli matched/run/curves) but no published results, GPU model or nvcc flags, and the preprint is not peer reviewed, so C.
- **Verifier notes:** Metadata checked on github.com: Apache-2.0, 12 stars, 0 forks, not a fork, not archived, last commit 2026-07-24 (active). Numbers in the record match the abstract snippets; benchmark_url set to the preprint the README links (not openable here).
- **Fields the verifier corrected:** `benchmark_url`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/Cortex-Discovery/sobek>
  - <https://github.com/Cortex-Discovery/sobek/commits>
  - <https://raw.githubusercontent.com/Cortex-Discovery/sobek/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/Cortex-Discovery/sobek>
  - <https://raw.githubusercontent.com/Cortex-Discovery/sobek/HEAD/README.md>
  - <https://raw.githubusercontent.com/Cortex-Discovery/sobek/HEAD/pyproject.toml>
  - <https://github.com/Cortex-Discovery/sobek/tree/main/sobek>
  - <https://github.com/Cortex-Discovery/sobek/tree/main/sobek/kernels>
  - <https://github.com/Cortex-Discovery/sobek/tree/main/sobek/kernels/uvw>
  - <https://github.com/Cortex-Discovery/sobek/tree/main/sobek/nn>
  - <https://github.com/Cortex-Discovery/sobek/tree/main/sobek/benchmarks>
  - <https://github.com/Cortex-Discovery/sobek/tree/main/tests>
  - <https://github.com/Cortex-Discovery/sobek/commits>
  - <https://github.com/Cortex-Discovery/sobek/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/Cortex-Discovery/sobek/HEAD/sobek/kernels/config.py>
  - <https://raw.githubusercontent.com/Cortex-Discovery/sobek/HEAD/sobek/kernels/forward.py>
  - <https://raw.githubusercontent.com/Cortex-Discovery/sobek/HEAD/sobek/kernels/_runtime.py>
  - <https://raw.githubusercontent.com/Cortex-Discovery/sobek/HEAD/sobek/kernels/uvw/forward.py>
  - <https://raw.githubusercontent.com/Cortex-Discovery/sobek/HEAD/sobek/kernels/uvw/scratch.py>
  - <https://raw.githubusercontent.com/Cortex-Discovery/sobek/HEAD/sobek/benchmarks/measure.py>
  - <https://raw.githubusercontent.com/Cortex-Discovery/sobek/HEAD/sobek/benchmarks/runners.py>
  - WebSearch snippets of https://arxiv.org/abs/2607.18074 (arXiv egress-blocked; not opened)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/cortex-discovery/sobek`) · [data/wave8/enrich/raw/github_com_cortex_discovery_sobek.json](../../../data/wave8/enrich/raw/github_com_cortex_discovery_sobek.json) (enrichment confidence 0.6)

</details>
