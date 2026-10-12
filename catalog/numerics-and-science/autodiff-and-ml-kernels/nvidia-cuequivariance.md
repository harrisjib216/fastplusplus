# cuEquivariance

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Python (frontends; CUDA kernels ship as separate pip packages)` · `Apache-2.0` · 🟢 active

> NVIDIA's CUDA kernels for equivariant tensor products (MACE, NequIP, Allegro); an independent study puts MACE inference about 3x faster than e3nn.

| | |
|---|---|
| **Beats** | e3nn (PyTorch equivariant tensor products for MACE, NequIP and similar models) |
| **Claimed result** | Independent study (arXiv 2510.23621, abstract seen via WebSearch snippets only, paper not opened): cuEquivariance 'reduces inference latency by about 3x' for MACE compared with the e3nn backend. Repo: no numbers. The MACE tutorial cell (docs/tutorials/pytorch/MACE.rst) prints 'Speedup: {e3nn_avg/cuet_avg}x' but stores no output; one WebSearch summary said the rendered docs.nvidia.com tutorial shows 5.6x for the channelwise tensor product, but a second targeted search did not confirm it and docs.nvidia.com is egress-blocked, so that figure is unverified. CHANGELOG '\~3x' (JAX v0.3.0 vs Torch v0.2.0) and 'up to 2x' (uniform 1d kernel) compare cuEquivariance with its own earlier releases. |
| **Workload** | The repo's PyTorch MACE tutorial (docs/tutorials/pytorch/MACE.rst) contains an executable timing cell comparing e3nn's channelwise tensor product plus scatter_add against cuEquivariance's fused uniform_1d kernel: multiplicity 128 (128x0e + 128x1o), 1000 nodes, 10000 edges, float32, CUDA, 10 throwaway and 1000 timed repetitions with torch.cuda.synchronize. |
| **Metric** | throughput |
| **Adoption** | 441 stars, 43 forks (github.com page, 2026-10-03); NVIDIA library named in the README as accelerating DiffDock, MACE, Allegro and NequIP; a backend option in MACE |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/NVIDIA/cuEquivariance) · [benchmark](https://arxiv.org/abs/2510.23621) |

## Verdict

An independent preprint (arXiv 2510.23621, 'Speeding Up MACE', read only as a search snippet) profiles MACE end to end and finds the cuEquivariance backend cuts inference latency by about 3x versus e3nn, with roughly 4x more from casting linear layers to BF16/FP16. GPU, compiler and exact model size were not visible. The repo's own tutorial times e3nn against cuEquivariance (1000 nodes, 10000 edges, multiplicity 128, FP32) but stores no output.

## Use it when

- Inference or training of MACE-style interatomic potentials on NVIDIA GPUs, where MACE already exposes cuEquivariance as a backend
- Large graphs (thousands of nodes, tens of thousands of edges) with multiplicities around 128, where the tutorial says the kernels do best
- Message-passing layers where you can fuse gather, channelwise tensor product and scatter into one uniform_1d call
- Symmetric contraction and per-species (indexed) linear layers in MACE's product basis and skip connections
- Protein-structure models (OpenFold3/Boltz-style) that need triangle attention or triangle multiplication on Ampere through Blackwell

## Skip it when

- You need AMD GPUs, CPUs or source-level control of the kernels: the kernel wheels are NVIDIA-only binaries under a proprietary license, and the open-source OpenEquivariance covers AMD and is BSD-3
- Plain equivariant linear layers or scalar-only irreps: the tutorial says it does 'not provide a large speedup' there, and issue #45 reported no gain over e3nn for a 3000x0e linear case
- Small inputs: the tutorial says the kernels do best on very large inputs, and triangle kernels fall back to PyTorch below sequence length 100 by default
- Code that must stay in e3nn's mul_ir layout end to end: each TransposeIrrepsLayout call costs time, which the tutorial calls 'quite expensive'
- Production code that cannot absorb API breaks: the README says Beta, and 0.4.0 and 0.9.0 removed or renamed public classes

## How it is fast

Every supported operation is lowered to one segmented-polynomial descriptor and run by a JIT-compiled 'uniform_1d' CUDA kernel (or fused_tp / indexed_linear kernels) instead of e3nn's chain of small PyTorch ops. The uniform_1d kernel fuses the gather of sender features and the scatter-add of messages into the tensor-product call, so the edge-sized intermediates of the e3nn message-passing path are not written to memory. It uses an ir_mul (component-major) layout so channels are contiguous, and indexed linear layers (per-species weights) run as one kernel instead of e3nn's FullyConnectedTensorProduct against a one-hot vector.

## Compared with alternatives

Pick cuEquivariance over OpenEquivariance when you run MACE or AlphaFold-style models on NVIDIA hardware and want the vendor-maintained backend with JAX bindings and triangle kernels. OpenEquivariance claims parity with it, is BSD-3 and runs on AMD. batmobile's 11.8x-20x e3nn numbers come from a much smaller single-author kernel set.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | cuequivariance (core), PyTorch (&gt;=2.11 for ops 0.12.0) or JAX, and the proprietary cuequivariance-ops-torch-cu12/-cu13 or cuequivariance-ops-jax-\* kernel wheels; Triton for the triangle kernels; optional ONNX/TensorRT extras for export |
| **Minimum toolchain** | Python 3.10+ (3.10-3.14 listed), CUDA 12 or 13 wheels (CUDA 11 dropped in 0.6.0); Blackwell triangle-attention kernels need cu13 builds |
| **Platforms** | Linux x86-64 and aarch64 (manylinux wheels) with NVIDIA GPUs; the 'naive' PyTorch method runs anywhere but is unoptimized |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — the descriptors reproduce e3nn operations (an O3_e3nn group exists for matching conventions) and MACE can switch backends, but modules, weight layouts and the default ir_mul data layout differ from e3nn, so direct e3nn code must be ported |

## Gotchas

- uniform_1d and fused_tp compute only in FP32 or FP64; FP16/BF16 inputs are upcast to FP32 math unless you choose another method.
- The triangle-multiplication Triton kernels can run ahead-of-time tuning that 'may take several hours'; the cache lives in \~/.cache/cuequivariance-triton and is lost on container restart unless it is persisted.
- Open issue #244 reports out-of-shared-memory failures on Blackwell at embedding size 128, and 0.9.1 fixed an index overflow in uniform_1d at large index values; 0.9.1 also turned parallel kernel compilation off by default after multi-GPU problems.
- Deprecated primitives (TensorProduct, EquivariantTensorProduct, SymmetricTensorProduct) raise ImportError since 0.9.0; use SegmentedPolynomial or the high-level modules.

## Known shortcomings

- Raised D to C on the abstract of an independent arXiv 2510.23621 (about 3x MACE inference latency vs e3nn), seen only as a snippet. The kernel pip package ships under NVIDIA's proprietary Math Libraries SDK license, so usability stays mixed.
- The kernel wheels are proprietary binaries (NVIDIA Math Libraries SDK license forbids reverse engineering and derivative works); the README says Beta and releases 0.4.0 and 0.9.0 broke the API. uniform_1d/fused_tp compute only in FP32/FP64; the tutorial says linear layers get no large speedup and issue #45 found no gain over e3nn for a 3000x0e linear; issue #244 open: out of shared memory on Blackwell at embedding size 128. The 3x MACE figure (arXiv 2510.23621) stays snippet-only, and the snippet attributes about 4x more to BF16/FP16 linear layers.

## Caveats and trade-offs

Numbers are snippet only: the independent arXiv 2510.23621 abstract (about 3x MACE inference latency versus e3nn) was read through WebSearch because arxiv.org is egress-blocked; methodology, GPU and precision were not visible. docs.nvidia.com was also egress-blocked, and the repo's MACE tutorial timing cell (1000 nodes, 10000 edges, multiplicity 128, float32, 1000 timed repetitions) stores no output. The tutorial itself notes 'our kernels tend to have best performance for very large input sizes'. The repo's Python frontends are Apache-2.0 ('All files hosted in this repository are subject to the Apache 2.0 license'), but the CUDA kernels ship as separate pip packages (cuequivariance-ops-torch-cu12/-cu13, cuequivariance-ops-jax-\*) under the proprietary 'NVIDIA Math Libraries SDK' license agreement (pypi.org metadata: 'Other/Proprietary License'), which forbids reverse engineering and derivative works, so usability is 'mixed'. Other independent measurements exist: OpenEquivariance's peer-reviewed ACDA25 paper and harness (tests/benchmark.py) time cuEquivariance against e3nn; per its abstract snippets, OpenEquivariance's fused kernels beat cuEquivariance by up to 4.5x forward. Vendor-only figures would cap at C.

Python library with PyTorch and JAX bindings. The repository files are Apache-2.0, but the CUDA kernels are installed from separate cuequivariance-ops-torch-cu12/cu13 and cuequivariance-ops-jax-cu12/cu13 pip packages; OpenEquivariance's README calls cuEquivariance's kernel package 'closed-source', and I did not find the kernel source or the ops-package license in the repo. NVIDIA-GPU only; beta status per README. Uses the transpose of e3nn's mul_ir data layout and the tutorial warns that layout transposes can be expensive. Triton-based triangle kernels have optional ahead-of-time tuning that can take hours.

## Maintenance

Actively developed by NVIDIA (0.12.0 on PyPI 2026-09-23, roughly monthly releases) and still labelled Beta; the Apache-2.0 Python frontends are usable, but the speed comes from closed binary kernel wheels under the NVIDIA Math Libraries SDK license, which forbids reverse engineering and derivative works, so usability is mixed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification D, tier now C.
- **Tier reason:** Upgraded from D to C. The independent preprint 'Speeding Up MACE: Low-Precision Tricks for Equivariant Force Fields' (arXiv 2510.23621) compares MACE's e3nn and cuEquivariance backends, and its abstract says cuEquivariance 'reduces inference latency by about 3x'. Two WebSearch snippets agree on this, but arXiv is egress-blocked, so methodology and hardware were not visible. The repo itself carries only an e3nn-vs-cuEquivariance timing cell with no stored output (docs/tutorials/pytorch/MACE.rst).
- **Verifier notes:** Upgraded D to C (verdict 'confirm' per the upgrade rule) because the independent arXiv 2510.23621 abstract gives about 3x MACE inference latency versus e3nn; seen as a WebSearch snippet only. Confirmed the proprietary license on the kernel pip package, so 'mixed' stands. A retier to B needs that paper (or the OpenEquivariance ACDA25 paper's cuE-vs-e3nn columns) to be opened.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/NVIDIA/cuEquivariance>
  - <https://github.com/NVIDIA/cuEquivariance/commits>
  - <https://raw.githubusercontent.com/NVIDIA/cuEquivariance/HEAD/README.md>
  - <https://raw.githubusercontent.com/NVIDIA/cuEquivariance/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/NVIDIA/cuEquivariance/HEAD/docs/tutorials/pytorch/MACE.rst>
  - <https://pypi.org/pypi/cuequivariance-ops-torch-cu12/json>
- **Sources the enricher read:**
  - <https://github.com/NVIDIA/cuEquivariance>
  - <https://raw.githubusercontent.com/NVIDIA/cuEquivariance/HEAD/README.md>
  - <https://raw.githubusercontent.com/NVIDIA/cuEquivariance/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/NVIDIA/cuEquivariance/HEAD/VERSION>
  - <https://raw.githubusercontent.com/NVIDIA/cuEquivariance/HEAD/docs/tutorials/pytorch/MACE.rst>
  - <https://raw.githubusercontent.com/NVIDIA/cuEquivariance/HEAD/cuequivariance_torch/cuequivariance_torch/__init__.py>
  - <https://raw.githubusercontent.com/NVIDIA/cuEquivariance/HEAD/cuequivariance_torch/cuequivariance_torch/primitives/segmented_polynomial.py>
  - <https://raw.githubusercontent.com/NVIDIA/cuEquivariance/HEAD/cuequivariance_torch/pyproject.toml>
  - <https://github.com/NVIDIA/cuEquivariance/issues?q=is%3Aissue+slow+OR+performance+OR+slower>
  - <https://github.com/NVIDIA/cuEquivariance/issues/45>
  - <https://github.com/NVIDIA/cuEquivariance/issues/39>
  - <https://pypi.org/pypi/cuequivariance-ops-torch-cu12/json>
  - <https://pypi.org/pypi/cuequivariance-torch/json>
  - <https://raw.githubusercontent.com/PASSIONLab/OpenEquivariance/HEAD/README.md>
  - <https://github.com/Cortex-Discovery/sobek>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/nvidia/cuequivariance`) · [data/wave8/enrich/raw/github_com_nvidia_cuequivariance.json](../../../data/wave8/enrich/raw/github_com_nvidia_cuequivariance.json) (enrichment confidence 0.6)

</details>
