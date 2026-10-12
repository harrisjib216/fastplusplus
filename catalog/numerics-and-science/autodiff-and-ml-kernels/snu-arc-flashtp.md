# FlashTP (SNU-ARC)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++/CUDA (PyTorch extension)` · `MIT` · 🟢 active

> Fused, sparsity-aware CUDA kernels for e3nn's channelwise (uvu) tensor product; paper reports up to 41.6x over e3nn.

| | |
|---|---|
| **Beats** | e3nn o3.TensorProduct (uvu, with torch_scatter) and NVIDIA cuEquivariance |
| **Claimed result** | Search snippets of the ICML 2025 abstract: up to 41.6x and 60.8x kernel speedups over e3nn and NVIDIA cuEquivariance; SevenNet-l3i5 4.2x and 3.5x speedup with 6.3x and 6.2x peak-memory reduction for inference and training. |
| **Workload** | Channelwise (uvu) tensor-product layer of equivariant MLIPs (NequIP, SevenNet-type irreps configs in ir_config/), kernel microbenchmarks and end-to-end SevenNet-l3i5 inference and training. |
| **Metric** | throughput |
| **Adoption** | 62 stars; integrated in SevenNet 'flash' branch |
| **Last commit** | 2026-05-27 |
| **Links** | [repository](https://github.com/SNU-ARC/flashTP) · [benchmark](https://openreview.net/pdf?id=wiQe95BPaB) |

## Verdict

The ICML 2025 paper (read here only through search-result snippets of its abstract) reports up to 41.6x and 60.8x kernel speedups over e3nn and NVIDIA cuEquivariance on the uvu tensor product, and 4.2x inference and 3.5x training speedups with 6.3x and 6.2x lower peak memory for SevenNet-l3i5; snippets mention an A100, but GPU model, precision and the configurations behind the maxima were not confirmed from the paper itself. SevenNet's own docs say FlashTP gives 'up to \~4x' speedup and lose to cuEquivariance above about 10^3 atoms.

## Use it when

- Training or running an equivariant MLIP (NequIP, SevenNet-style) on NVIDIA A100/H100 where the uvu tensor product dominates step time or GPU memory limits system size (the paper reports 28,000 atoms on one A100).
- Force training that needs double-backward through the tensor product, which FlashTP implements natively in fp32 and fp64.
- SevenNet users: it is wired in via --enable_flash, and SevenNet's docs say FlashTP with LAMMPS: Torch beats cuEquivariance with LAMMPS: ML-IAP for small systems (below about 10^3 atoms).
- Irreps whose input-1 multiplicities are all multiples of 32 (e.g. 32x0e, 64x1o) with e3nn's default component/element normalization and per-edge (non-shared, non-internal) weights.

## Skip it when

- Multiplicities that are not multiples of 32 (e.g. 10x1o, 40x0e): the module asserts mul % 32 == 0 and fails; issue #4 asking for a workaround was closed without an answer.
- Large systems: SevenNet's accelerator docs (citing the SevenNet-Omni paper) report a crossover around 10^3 atoms beyond which cuEquivariance is more efficient.
- Tensor products other than channelwise uvu (fully connected uvw, shared or internal weights), fp16/bf16, or non-NVIDIA GPUs: none are supported.
- GPUs other than A100/H100 without manual tuning: the shared-memory budget is chosen by matching 'A100' or 'H100' in the device name, and any other GPU drops to a 48 KiB 'safe mode' unless you pass smem_size.
- Projects that need a pip wheel or a version policy: install is from source with a CUDA build of up to 10 minutes (issue #5 asking for a pip release is open), version 0.1.1.

## How it is fast

It fuses gather, tensor product, per-edge weighting and scatter-add into one kernel per pass, so the large per-edge intermediate tensor that e3nn materializes is never written to memory; that is where the reported 6x peak-memory reduction comes from. The Clebsch-Gordan coefficients are stored sparsely (only nonzero 'fibers', with values deduplicated into a uint8-indexed table of up to 256 unique values, or an extended-CG kernel above that), skipping the zero entries a dense e3nn contraction multiplies. Paths are grouped per input irrep and per 32-channel warp, inputs are staged in shared memory sized to the GPU (163 KiB on A100, 227 KiB on H100), and outputs are accumulated with atomicAdd.

## Compared with alternatives

Pick FlashTP over cuEquivariance for uvu-based models on small-to-medium systems (below about 10^3 atoms per SevenNet's docs) or when peak memory is the limit; pick cuEquivariance or OpenEquivariance for larger systems, multiplicities not divisible by 32, or non-uvu products, and Sobek if you want streaming convolutions that its authors report beat OpenEquivariance.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | PyTorch &gt;= 2.4.1, e3nn, CUDA toolkit 12+, ninja; torch_scatter only for the e3nn reference benchmark |
| **Minimum toolchain** | Python &gt;= 3.10 (setup.py), CUDA 12, PyTorch 2.4.1; nvcc built with -O2 |
| **Platforms** | NVIDIA GPUs only; built for the detected compute capability, or sm_80 and sm_90 with PTX fallback when no GPU is present at build time (Blackwell runs via PTX JIT) |
| **Thread safety** | not documented; a DDP multi-GPU illegal-memory-access report (issue #1) was closed with no fix visible on the issue page |
| **Drop-in for the baseline** | partial — same irreps and instruction arguments as e3nn.o3.TensorProduct uvu, but the call takes node features plus edge_src/edge_dst and returns scatter-summed node outputs, so the surrounding gather/scatter code must be removed |

## Gotchas

- Output accumulation uses atomicAdd in the scatter step, so results are not bitwise deterministic run to run; the bundled correctness check compares against e3nn with a 1e-4 absolute tolerance.
- Unique Clebsch-Gordan values are deduplicated after rounding through fp32 even in fp64 mode, which picks the kernel variant (uint8-indexed vs extended CG above 256 unique values).
- The example/test.sh 'microbenchmark' runs one forward, backward and double-backward pass and checks correctness; it has no timing code, so reproducing the paper's speedups needs an external profiler (e.g. Nsight).
- Building can be killed by out-of-memory in ninja (exit 137); SevenNet's docs recommend MAX_JOBS=1.

## Known shortcomings

- Tier B on the ICML 2025 paper, whose 41.6x/60.8x kernel and SevenNet 4.2x/3.5x figures were seen only in abstract snippets (openreview, mlanthology, arXiv blocked); GPU and flags unverified. OpenEquivariance issue #171 confirms FlashTP did not benchmark against OpenEquivariance.
- Input-1 multiplicities must be multiples of 32 (asserted; issue #4 closed without answer). SevenNet's own accelerator docs say cuEquivariance is faster above about 10^3 atoms. Shared memory is chosen by matching 'A100' or 'H100' in the GPU name, with a 48 KiB fallback for anything else; scatter uses atomicAdd, so results are not bitwise deterministic; example/test.sh checks correctness only with no timing code; no pip release (issue #5 open); DDP illegal-memory-access issue #1 closed with no visible fix.

## Caveats and trade-offs

Paper (openreview, proceedings.mlr.press, mlanthology) EGRESS_BLOCKED; numbers are from WebSearch snippets of the ICML 2025 abstract only, so GPU model, precision and the configuration on which the 41.6x/60.8x maxima occur are unverified. The 'up to' figures are maxima, and the per-phase figures (forward/backward/double-backward) were not confirmed. Repo README gives no numbers; it ships microbenchmarks (example/test.sh runs example/flashTP_test.py over ir_config/) that a user can rerun; the build auto-detects GPU compute capability and falls back to sm_80/sm_90 with PTX. Scope is the channelwise 'uvu' tensor product only (drop-in for e3nn.o3.TensorProduct uvu). Baselines are Python/PyTorch e3nn (with torch_scatter) and cuEquivariance, not a C++ default. No head-to-head against OpenEquivariance in the paper per the OpenEquivariance issue #171 remark; Sobek lists FlashTP only as a related library.

Drop-in only for channelwise 'uvu' e3nn TensorProduct; CUDA 12+ and PyTorch &gt;= 2.4.1; kernels compiled at install (up to 10 minutes), per-architecture (auto-detect, A100/H100 fallback with PTX); README TODO lists performance work and a JIT implementation.

## Maintenance

Active (last commit 2026-05-27, adding GPU auto-detection and PTX fallback), MIT-licensed, 23 commits and integrated into SevenNet main via --enable_flash, but still a 0.1.1 source-only research release with a TODO for further performance work and a JIT path.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed ICML 2025 paper (linked from the repo README) reports kernel speedups over e3nn and NVIDIA cuEquivariance; the abstract numbers (up to 41.6x and 60.8x; SevenNet-l3i5 4.2x/3.5x speed, 6.3x/6.2x memory) appear identically in WebSearch snippets of openreview and proceedings.mlr.press. The paper itself was EGRESS_BLOCKED, so GPU model and flags could not be checked and the repo README carries no numbers, which rules out A.
- **Verifier notes:** Metadata checked on github.com: MIT, 62 stars, 8 forks, not a fork, not archived, 23 commits, last commit 2026-05-27 (active). benchmark_url set to the paper PDF the README links; it could not be opened here (blocked). Keep at B on peer review.
- **Fields the verifier corrected:** `benchmark_url`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/SNU-ARC/flashTP>
  - <https://github.com/SNU-ARC/flashTP/commits>
  - <https://raw.githubusercontent.com/SNU-ARC/flashTP/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/SNU-ARC/flashTP/HEAD/README.md>
  - <https://github.com/SNU-ARC/flashTP>
  - <https://github.com/SNU-ARC/flashTP/commits>
  - <https://github.com/SNU-ARC/flashTP/issues?q=is%3Aissue>
  - <https://github.com/SNU-ARC/flashTP/issues/1>
  - <https://github.com/SNU-ARC/flashTP/issues/4>
  - <https://github.com/SNU-ARC/flashTP/issues/6>
  - <https://github.com/SNU-ARC/flashTP/tree/main/flashTP_e3nn>
  - <https://raw.githubusercontent.com/SNU-ARC/flashTP/HEAD/flashTP_e3nn/flashTP.py>
  - <https://raw.githubusercontent.com/SNU-ARC/flashTP/HEAD/flashTP_e3nn/utils.py>
  - <https://raw.githubusercontent.com/SNU-ARC/flashTP/HEAD/flashTP_e3nn/sptp_exp_opt_large/fused_e3nn_exp_opt_large.py>
  - <https://raw.githubusercontent.com/SNU-ARC/flashTP/HEAD/flashTP_e3nn/sptp_exp_opt_large/fwd_sptp_linear_v2_shared_exp.cu>
  - <https://raw.githubusercontent.com/SNU-ARC/flashTP/HEAD/setup.py>
  - <https://raw.githubusercontent.com/SNU-ARC/flashTP/HEAD/requirements.txt>
  - <https://raw.githubusercontent.com/SNU-ARC/flashTP/HEAD/example/flashTP_test.py>
  - <https://raw.githubusercontent.com/SNU-ARC/flashTP/HEAD/example/test.sh>
  - <https://raw.githubusercontent.com/MDIL-SNU/SevenNet/main/README.md>
  - <https://raw.githubusercontent.com/MDIL-SNU/SevenNet/main/docs/source/user_guide/accelerator.md>
  - WebSearch: FlashTP ICML 2025 abstract snippets (openreview.net/forum?id=wiQe95BPaB, proceedings.mlr.press/v267/lee25l.html)
  - https://lacuna.tiptreesystems.com/work/flashtp-fused-sparsity-aware-tensor-product-for-machine-learning-interatomic/wrk_8c0e4dad648c9343030816fd545ae078 (EGRESS_BLOCKED)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/snu-arc/flashtp`) · [data/wave8/enrich/raw/github_com_snu_arc_flashtp.json](../../../data/wave8/enrich/raw/github_com_snu_arc_flashtp.json) (enrichment confidence 0.75)

</details>
