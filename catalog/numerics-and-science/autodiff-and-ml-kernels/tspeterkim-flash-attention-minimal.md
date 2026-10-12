# flash-attention-minimal (forward-only FlashAttention in about 100 lines of CUDA)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `CUDA C++` · `Apache-2.0` · 🟡 stale

> Educational 100-line FP32 CUDA FlashAttention forward kernel; its 13x win over eager PyTorch attention is a cold-start profiling artifact.

| | |
|---|---|
| **Beats** | naive PyTorch attention (eager matmul + softmax + matmul) |
| **Claimed result** | README sample output on a T4: manual attention Self CUDA time total 52.545 ms vs minimal flash attention 3.908 ms (about 13x, derived from page data); Self CPU time total 52.389 ms vs 11.452 ms; the README says 'Speed-up achieved!'. |
| **Workload** | One profiled forward call of attention with batch 16, 12 heads, sequence length 64, head dimension 64, FP32, on a T4 (bench.py). |
| **Metric** | latency |
| **Hardware** | NVIDIA T4 (AWS g4 instance); host CPU model not stated. |
| **Compiler and flags** | nvcc -O2 (extra_cuda_cflags=['-O2'] in bench.py via torch.utils.cpp_extension.load); CUDA, PyTorch and compiler versions not stated. |
| **Adoption** | 1.2k stars, 118 forks |
| **Last commit** | 2024-12-30 |
| **Links** | [repository](https://github.com/tspeterkim/flash-attention-minimal) · [benchmark](https://github.com/tspeterkim/flash-attention-minimal) |

## Verdict

The README's sample output on an AWS T4 is a single profiled forward call at batch 16, 12 heads, seq_len 64, head_dim 64, FP32: manual attention 52.545 ms vs minimal flash attention 3.908 ms Self CUDA time (about 13x, derived from page data), built with nvcc -O2, with CUDA and PyTorch versions not stated. The verifier judged this a cold-start artifact of timing an unwarmed baseline; warmed or CUDA-event-timed runs reported in issues #11 and #13 show eager PyTorch attention is faster.

## Use it when

- Learning how FlashAttention's tiling and online-softmax rescaling work, by reading about 100 lines of CUDA next to the paper's Algorithm 1.
- A minimal starting point for your own attention-kernel experiments (many forks and open PRs add a backward pass, FA2 loop order, GQA or causal masking).
- Classroom or interview exercises at small shapes (for example seq_len 64, head_dim 64, FP32) where correctness against a manual reference matters more than speed.
- Checking a tensor-core rewrite step by step: the tensorcore branch keeps the naive kernel and a WMMA TF32 kernel side by side.

## Skip it when

- Any case where speed matters: measured with warm-up or CUDA events, eager PyTorch attention is faster (issues #11 and #13), and the README concedes it gets slower than the manual implementation for longer sequences and larger block sizes.
- As a substitute for PyTorch SDPA, flash-attn or cuDNN attention: it was never benchmarked against them and runs FP32 one-thread-per-row matmuls without tensor cores (main branch).
- Training, causal or masked attention, or FP16/BF16 models: forward only, no mask, FP32 inputs only (a BF16 request, issue #7, is open).
- Sequence lengths that are not a multiple of the block size (32 on main, 16 in the tensorcore branch) or head dimensions above about 117 on main (see gotchas).
- Code that relies on CUDA streams or multiple GPUs: kernels launch on the default stream, and the main branch queries shared memory on device 0 only.

## How it is fast

It applies FlashAttention-1 tiling with online softmax: K/V tiles of 32 rows and a Q tile go into shared memory, a running row max m and row sum l are kept, and partial outputs are rescaled, so the N x N score matrix is never written to global memory. The outer loop runs over K/V tiles and the inner loop over Q tiles (the FA1 order), so O, l and m are re-read and re-written in global memory for every K/V tile. There is one thread block of 32 threads per (batch, head), and each thread computes a whole query row's dot products serially on FP32 CUDA cores. That keeps the matmuls slow and occupancy low, so in practice it shows the I/O-aware idea rather than delivering speed. The tensorcore branch uses one warp per block with 16x16x8 TF32 WMMA fragments for QK^T and PV.

## Compared with alternatives

Pick it only to read the algorithm in its smallest form. For a from-scratch learning path that ends at competitive speed, use the catalogued learn-cuda attention (gau-nernst, beats the flash-attn package on SM120) or Mini-Attention (beats cuDNN SDPA at short sequences). For real workloads, use FlashAttention-3/4 or cuDNN through PyTorch SDPA.

## Integration

| | |
|---|---|
| **Form** | module (PyTorch C++/CUDA extension JIT-built from flash.cu and main.cpp by torch.utils.cpp_extension.load; the kernel can also be copied as a source-drop) |
| **Dependencies** | PyTorch with CUDA, Ninja, nvcc |
| **Minimum toolchain** | not documented (bench.py builds with nvcc -O2; the tensorcore branch sets TORCH_CUDA_ARCH_LIST=8.0 and -O3 -use_fast_math, and TF32 WMMA needs sm_80 or newer) |
| **Platforms** | NVIDIA GPUs with CUDA (README sample on a T4); the tensorcore branch targets Ampere (sm_80) or newer |
| **Thread safety** | not documented; launches on the legacy default stream rather than PyTorch's current stream, and has no CUDA error checks |
| **Drop-in for the baseline** | no |

## Gotchas

- The README speedup is not a speedup: bench.py profiles one cold call of each implementation (manual attention first) under torch.autograd.profiler with no warm-up, so the 52.5 ms baseline is mostly first-call initialisation; issue #16 adds that the old autograd profiler does not capture the custom op properly.
- No bounds checks on N (derived from code): tiles are read and written in full for ceil(N/Bc) iterations, so a seq_len that is not a multiple of the block size reads past the head's slice and writes O out of range. A Faial data-race analysis (issue #1) found the main kernel race-free only when Bc == Br == blockDim.x, Tr &lt;= blockDim.x and N &gt;= blockDim.x^2.
- Shared memory (derived from code, not tested): the main branch requests 3\*Bc\*d\*4 + Bc\*Br\*4 bytes per block (28 KB at head_dim 64, 52 KB at 128) without the cudaFuncSetAttribute opt-in above the 48 KB default, and the launch is not error-checked, so head_dim above about 117 can fail without an error at the call and return the zero-initialised O. It also printf's the shared-memory line on every call.
- The tensorcore branch cudaMallocs the l and m buffers on every call and never frees them (a leak of B\*nh\*N\*8 bytes per call), and computes in TF32, which has less precision than the FP32 main kernel.

## Known shortcomings

- Claim not reproducible: bench.py times one cold call with no warm-up, so the 52.5 ms 'manual' PyTorch figure is mostly initialisation; issues #11 and #13 report naive PyTorch is faster once warmed or timed with CUDA events. Educational code (\~100 lines, forward only, tiny sizes).
- The reported speedup is a cold-start profiler artifact (issues #11, #13, #16). No bounds check when N is not a multiple of 32 (16 on the tensorcore branch); on main head_dim above about 117 exceeds 48 KB shared memory with no opt-in and an unchecked launch; the tensorcore branch leaks cudaMalloc'd l/m every call; Faial race-freedom conditions are in issue #1. The leloykun fork's 94x over FA2 on an RTX 3060 (4.048 vs 377.542 ms) is likely the same artifact.

## Caveats and trade-offs

Invalid evidence: bench.py times a single cold call of each implementation under torch.autograd.profiler with no warm-up, and manual attention runs first, so its 52.5 ms CUDA time is dominated by one-time initialisation. Issue #11 (2025-09-04) reports that on a second run naive attention is 'drastically faster than the flash attention kernel'; issue #13 reports that timed with CUDA events 'the flash attention is consistently much slower than the manual attention'; issue #16 says the old autograd profiler does not capture the custom op correctly; issue #3 ('slow in for loop test') times both with a warm-up. The README itself concedes it gets slower than the manual implementation for longer sequences and larger block sizes (thread-per-row matmuls, FP32, fixed block size 32), and bench.py says 'Use small model params, otherwise slower than manual attention'. Educational code: forward only, no comparison with cuDNN, official flash-attention or PyTorch SDPA. The tensorcore branch has a 10-iteration wall-clock bench at GPT-2 sizes (seq 1024) but publishes no numbers. Repo identity inferred from the HN title (HN thread not opened).

Educational forward pass only (no backward); FP32 rather than FP16; block size fixed at 32 at compile time; one thread per output row, which makes the matmuls slow.

## Maintenance

Stale since 2024-12-30 (9 commits on main), and open PRs that add a backward pass, FA2 and GQA are unmerged; it is Apache-2.0 with 1.2k stars and is good teaching code, but not something to depend on for performance.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): reject; tier before verification C, tier now C.
- **Tier reason:** The README numbers (52.545 ms vs 3.908 ms Self CUDA time on a T4) come from bench.py, which profiles one cold call of each variant with no warm-up, manual attention first, so the manual figure carries first-call cuBLAS/kernel initialisation; at batch 16 x 12 heads x 64 x 64 FP32 a steady-state eager attention takes far less than 52 ms. The numbers exist but do not measure a speedup, so at most first-party C and in substance invalid.
- **Verifier notes:** Reject: the only speedup is a cold-start profiling artifact, and three issues (#11, #13, #16) report naive PyTorch attention is faster when measured properly; README admits slower at realistic sizes. If kept under keep-and-document, record shortcoming 'claimed speedup not reproducible: benchmark times an unwarmed baseline; slower than eager PyTorch attention when warmed (issues #11, #13)' and tier no higher than C. Metadata on github.com: Apache-2.0, 1.2k stars, 118 forks, not a fork or archived, 9 commits on main, last commit 2024-12-30 (stale is right).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/tspeterkim/flash-attention-minimal>
  - <https://github.com/tspeterkim/flash-attention-minimal/commits>
  - <https://github.com/tspeterkim/flash-attention-minimal/issues?q=is%3Aissue>
  - <https://github.com/tspeterkim/flash-attention-minimal/issues/3>
  - <https://github.com/tspeterkim/flash-attention-minimal/issues/11>
  - <https://github.com/tspeterkim/flash-attention-minimal/issues/13>
  - <https://github.com/tspeterkim/flash-attention-minimal/issues/16>
  - <https://raw.githubusercontent.com/tspeterkim/flash-attention-minimal/HEAD/README.md>
  - <https://raw.githubusercontent.com/tspeterkim/flash-attention-minimal/HEAD/bench.py>
  - <https://raw.githubusercontent.com/tspeterkim/flash-attention-minimal/tensorcore/README.md>
  - <https://raw.githubusercontent.com/tspeterkim/flash-attention-minimal/tensorcore/bench.py>
- **Sources the enricher read:**
  - <https://github.com/tspeterkim/flash-attention-minimal>
  - <https://github.com/tspeterkim/flash-attention-minimal/issues?q=is%3Aissue>
  - <https://github.com/tspeterkim/flash-attention-minimal/pulls?q=is%3Apr>
  - <https://github.com/tspeterkim/flash-attention-minimal/issues/1>
  - <https://github.com/tspeterkim/flash-attention-minimal/issues/3>
  - <https://github.com/tspeterkim/flash-attention-minimal/issues/11>
  - <https://github.com/tspeterkim/flash-attention-minimal/issues/13>
  - <https://github.com/tspeterkim/flash-attention-minimal/issues/16>
  - <https://raw.githubusercontent.com/tspeterkim/flash-attention-minimal/HEAD/README.md>
  - <https://raw.githubusercontent.com/tspeterkim/flash-attention-minimal/HEAD/bench.py>
  - <https://raw.githubusercontent.com/tspeterkim/flash-attention-minimal/HEAD/flash.cu>
  - <https://raw.githubusercontent.com/tspeterkim/flash-attention-minimal/HEAD/main.cpp>
  - <https://raw.githubusercontent.com/tspeterkim/flash-attention-minimal/tensorcore/README.md>
  - <https://raw.githubusercontent.com/tspeterkim/flash-attention-minimal/tensorcore/bench.py>
  - <https://raw.githubusercontent.com/tspeterkim/flash-attention-minimal/tensorcore/flash.cu>
  - <https://raw.githubusercontent.com/tspeterkim/flash-attention-minimal/tensorcore/main.cpp>
  - <https://github.com/leloykun/flash-attention-minimal>
  - <https://github.com/ishovkun/flash-attention>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/tspeterkim/flash-attention-minimal`) · [data/wave8/enrich/raw/github_com_tspeterkim_flash_attention_minimal.json](../../../data/wave8/enrich/raw/github_com_tspeterkim_flash_attention_minimal.json) (enrichment confidence 0.8)

</details>
