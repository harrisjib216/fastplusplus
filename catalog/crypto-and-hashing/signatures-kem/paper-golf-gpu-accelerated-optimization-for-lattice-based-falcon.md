# GOLF: GPU-accelerated Optimization for Lattice-based FALCON

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Signatures and key exchange](README.md)</sub>

**Tier C** (first-party claim) · Study only · `CUDA` · `no license` · ⚪ unknown

> CUDA batch port of Falcon-512 signing and verification, one signature per GPU thread; 70x/369x the reference's published CPU throughput.

| | |
|---|---|
| **Beats** | Falcon reference implementation throughput as published on falcon-sign.info (Intel Core i5-8259U @ 2.3 GHz, TurboBoost off), cited as Fouque et al. (Ref) in Table II and not re-run by the authors; also prior CPU/GPU Falcon papers |
| **Claimed result** | Falcon on RTX 4090: 420.25 kops/s signing (Table II: 420,250.10 ops/s) and 10,311.04 kops/s verification. The '42.02 kops/s' in the ePrint web abstract is a typo; the PDF abstract and Table II both say 420.25. Against the reference Falcon figures from falcon-sign.info (i5-8259U) the gain is 70.65x signing / 369.13x verification (the paper's '70.65x to 369.13x', Sec. IV-E). The abstract's 58.05x/73.14x is actually against the fastest CPU implementation (Nguyen et al., Apple M1), as Sec. IV-E and the conclusion show. GOLF is also 7.17x/3.79x over the fastest prior GPU work (Lee et al., on an A100, so different hardware) and 2.69x/1.53x on the same A100. |
| **Workload** | Batch Falcon signature generation and verification throughput (ops/s) on an RTX 4090 (and an A100), compared with the Falcon reference implementation's published single-machine CPU throughput and with prior CPU/GPU Falcon implementations (Table II) |
| **Metric** | throughput |
| **Hardware** | NVIDIA GeForce RTX 4090 (24 GB) with an AMD Ryzen 7 5700G host; also tested on an NVIDIA A100. The reference baseline numbers come from the Falcon website on an Intel Core i5-8259U (the paper's text also says i5-8279U). |
| **Compiler and flags** | NVCC, CUDA 12.1, -rdc=true -arch sm_89 -maxrregcount=127 (GPU side); the reference baseline's compiler and flags are not stated (numbers copied from falcon-sign.info) |
| **Links** | [benchmark](https://eprint.iacr.org/2025/749) |

## Verdict

On an RTX 4090 (CUDA 12.1, sm_89, -maxrregcount=127, 128x512 threads), GOLF measures 420,250 sign/s and 10,311,039 verify/s for Falcon, with parameters implied to be 512 by the baseline. That baseline (5,948.1 sign/s, 27,933.0 verify/s) was copied from falcon-sign.info for the reference implementation on an i5-8259U at 2.3 GHz with TurboBoost off and compiler flags not given, so 70.65x/369.13x compares a GPU batch against one CPU. On an A100 GOLF reaches 157,995 sign/s and 4,180,879 verify/s, which is 2.69x/1.53x over Lee et al.'s published A100 figures (not re-run).

## Use it when

- Cloud or server backends that queue tens of thousands of Falcon-512 signatures at a time, where aggregate ops/s matters and roughly 156 ms of batch latency is acceptable (RTX 4090 figure).
- Bulk Falcon-512 verification, e.g. checking large signature sets. Verification shows the largest gain (10.3M verify/s on an RTX 4090, about 6.4 ms batch latency) and needs no secret material on the GPU.
- You are building your own GPU Falcon and want proven, simple tricks: one thread per signature, a stack-frame iterative ffSampling, and depth-first butterfly ordering for FFT/iFFT cache locality.
- You need published RTX 4090 and A100 throughput numbers to size GPU capacity for Falcon against Lee et al.'s earlier GPU work.

## Skip it when

- Single-signature or latency-bound signing. Each 65,536-signature batch takes about 156 ms on an RTX 4090 (415 ms on an A100), while the CPU reference produces one Falcon-512 signature in about 0.17 ms (5,948 sign/s on an i5-8259U).
- You need usable, licensed code. The paper links none. The candidate repo russdrh/FP-GOLF has no license, 0 stars and a single benchmark/KAT driver, and has per-thread indexing bugs (see gotchas).
- Falcon-1024 or FIPS 206 FN-DSA interoperability. The paper never names a parameter set (its baseline row is Falcon-512), cites the 2018 NIST submission, and FP-GOLF hard-codes logn=9 (Falcon-512).
- Shared or multi-tenant GPUs with side-channel concerns. The paper argues GPU global-memory side channels are 'not practical' rather than measuring leakage, and does not analyze the floating-point Gaussian sampler's timing on GPU.
- Tight GPU memory. The FP-GOLF tree mode allocates 7,169 doubles (about 56 KB) of expanded key per thread, about 3.8 GB for its 65,536-thread batch, plus a 36 KB per-thread scratch union.

## How it is fast

The main gain is coarse-grained parallelism: one thread per signature, 128 blocks x 512 threads (65,536 signatures per launch), with -maxrregcount=127 so that 512 threads fit in a block. A 2-threads-per-signature fine-grained variant that swaps data with __shfl_sync reached only 177,027 sig/s, against 361,726 for coarse-grained. Kernel fusion avoids repeated launches and global-memory round trips, and the recursive ffSampling is rewritten as an explicit stack-frame loop (Lee et al.'s method) so that NVCC will compile it. Finally, the FFT/iFFT butterfly units run in depth-first rather than layer-by-layer (breadth-first) order to shorten data reuse distance. This added 14.51% signing throughput (361,726 to 414,216 sig/s at 128x512) and, per Nsight, cut L2-to-DRAM traffic by 18%.

## Compared with alternatives

Pick GOLF over VecFalcon only when you have a CUDA GPU and large batches and need Falcon throughput far beyond a CPU core. VecFalcon (CPU SIMD, 1.13-1.59x faster signing, released code) is the practical choice for per-signature latency or deployable code. GRASP is the matching GPU batch design for SPHINCS+ and also ships no code; if you need working GPU Falcon code today, Lee et al.'s benlwk/Falcon-Mitaka (GPL-3.0, Falcon-512), the prior work GOLF benchmarks against, is released.

## Integration

| | |
|---|---|
| **Form** | source-drop (paper only; the unconfirmed candidate russdrh/FP-GOLF is a Makefile project that builds one KAT/benchmark executable, kat512double_gpu, not a library) |
| **Dependencies** | CUDA runtime (cudart). The FP-GOLF build also needs gcc for the CPU reference files and includes cufft.h in fft_gpu.cu. |
| **Minimum toolchain** | Paper: NVCC from CUDA 12.1 with -rdc=true -arch sm_89 -maxrregcount=127. FP-GOLF README: CUDA 12.x (12.8 default), GCC with C99, Ubuntu 20.04+. Its Makefile uses -rdc=true -arch sm_80 -use_fast_math, but the fpr arithmetic uses explicit __dadd_rn/__dmul_rn. |
| **Platforms** | NVIDIA GPUs only. The paper tested an RTX 4090 (sm_89, with a Ryzen 7 5700G host) and an A100. The FP-GOLF README lists sm_70/sm_80/sm_86 targets. Linux host. |
| **Thread safety** | Not documented. Each GPU thread works on its own key/message/output slot, and there is no host-side API, stream handling or batching layer. |
| **Drop-in for the baseline** | no |

## Gotchas

- Headline ratios are easy to misread. The abstract's 58.05x/73.14x is against Nguyen et al.'s Apple M1 NEON code, not the reference. Against the reference (falcon-sign.info) the gain is 70.65x/369.13x, though the introduction says 387.84x. The ePrint web abstract prints 42.02 kops/s where the PDF says 420.25 kops/s.
- Throughput depends heavily on batch size. Across nine grid/block configurations from 16,384 to 65,536 threads, the best signing throughput is 2.93x the worst (1.47x for verification). Keys are generated ahead of time and shipped to the GPU in bulk, and the paper does not say whether host-device copies are inside the timed region.
- In FP-GOLF, the sign kernels read the 40-byte nonce (salt) with no per-thread offset, so every thread in a batch hashes and emits the same host-supplied salt. They also memmove thread 0's message into every signed-message output. Falcon (the paper's Algorithm 1) needs a fresh uniform salt per signature.
- The FP-GOLF benchmark copies one key, one message, one seed and one nonce into all 65,536 slots, checks only thread 0's signature against the CPU result, and times kernel launch plus cudaDeviceSynchronize only. Its grid is 256x256, not the paper's 128x512.

## Known shortcomings

- No public code. GPU vs CPU comparison: the 58.05x/73.14x ratios are against Nguyen et al. on an Apple M1, and the 70.65x/369.13x ratios against the reference use numbers copied from falcon-sign.info (i5-8259U, flags unknown). The ePrint page shows signing as 42.02 kops/s; the PDF says 420.25.
- Paper never names the parameter set (baseline is falcon-sign.info's Falcon-512 row) and its ratios are inconsistent (abstract 58x/73x vs Apple M1; 70.65x/369.13x vs reference; intro 387.84x). Batch latency \~156 ms. Side channels argued away, not measured. The possibly related russdrh/FP-GOLF repo (no license) reuses one salt across threads and its benchmark clones one key/message 65,536 times and checks only thread 0.

## Caveats and trade-offs

Peer-reviewed as IEEE Transactions on Information Forensics and Security vol. 20, pp. 9441-9453 (2025), doi:10.1109/TIFS.2025.3599681; the ePrint copy is labelled Preprint. The reference baseline was copied from the Falcon website (different CPU, flags unstated), not re-run. GPU batch throughput against a single CPU is a cross-hardware comparison, and the 7.17x/3.79x GPU comparison is also cross-hardware (RTX 4090 vs A100). The abstract labels 58.05x/73.14x as 'over the reference', but it is really against Nguyen et al. on an Apple M1. No code is linked from the paper. The repo github.com/russdrh/FP-GOLF (on the first author's account; a CUDA Falcon port with no license, created 2026-05, 0 stars) may be related but is not confirmed as the GOLF artifact, and its Makefile flags differ (sm_80, -use_fast_math).

No public code repository located; batched GPU throughput number, not single-operation latency; needs large batches and a CUDA GPU to realize the claimed gains.

## Maintenance

This is a peer-reviewed reference design (IEEE TIFS vol. 20, pp. 9441-9453, 2025; ePrint revised 2025-08-15) with no linked code, license or maintenance. The first author's russdrh/FP-GOLF (3 commits on 2026-05-25, 0 stars, no license) contains the paper's depth-first FFT/iFFT loops (logm/loghm counters) and stack-based ffSampling, so it is probably related. It is unconfirmed as the paper's artifact and not usable as-is.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The paper was peer-reviewed (IEEE TIFS 2025), but its reference-Falcon baseline figures (5,948.1 sign/s, 27,933.0 verify/s) were copied from falcon-sign.info (i5-8259U, compiler flags not given) rather than re-run. The GPU-vs-single-core-CPU gains are 70.65x/369.13x, over 50x with the baseline flags unstated, so the implausible-ratio rule caps the tier at C. No code is linked from the paper.
- **Verifier notes:** The headline signing figure in the record (42.02 kops/s) is a 10x typo on the ePrint landing page; the PDF says 420.25 kops/s. The 58.05x/73.14x ratios are against the Apple M1 implementation, not the reference; against the reference the gain is larger (70.65x/369.13x). I kept the tier at C because of the copied, flag-less baseline and the &gt;50x ratio, even though the paper is peer-reviewed (TIFS). I did not treat the russdrh/FP-GOLF repo as the project's code.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `hardware`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** IEEE TIFS 2025: signing 420.25 kops/s; vs Nguyen et al. (M1) 58.05x/73.14x; vs reference 70.65x/369.13x.
- **Pages the verifier opened:**
  - <https://eprint.iacr.org/2025/749>
  - <https://eprint.iacr.org/2025/749.pdf>
  - <https://falcon-sign.info/>
  - <https://api.crossref.org/works/10.1109/tifs.2025.3599681>
  - <https://github.com/russdrh/FP-GOLF>
  - <https://raw.githubusercontent.com/russdrh/FP-GOLF/main/FP-GOLF/Makefile>
  - <https://raw.githubusercontent.com/russdrh/FP-GOLF/main/FP-GOLF/test/PQCgenKAT_sign_gpu.cu>
  - <https://raw.githubusercontent.com/russdrh/FP-GOLF/main/FP-GOLF/GPU/sign_gpu.cu>
- **Sources the enricher read:**
  - <https://eprint.iacr.org/2025/749>
  - <https://eprint.iacr.org/2025/749.pdf>
  - <https://api.crossref.org/works/10.1109/tifs.2025.3599681>
  - <https://falcon-sign.info/>
  - <https://github.com/russdrh/FP-GOLF>
  - <https://github.com/russdrh/FP-GOLF/blob/main/README.md>
  - <https://github.com/russdrh/FP-GOLF/commits/main>
  - <https://github.com/russdrh/FP-GOLF/blob/main/FP-GOLF/Makefile>
  - <https://github.com/russdrh/FP-GOLF/blob/main/FP-GOLF/test/PQCgenKAT_sign_gpu.cu>
  - <https://github.com/russdrh/FP-GOLF/blob/main/FP-GOLF/GPU/api_gpu.cuh>
  - <https://github.com/russdrh/FP-GOLF/blob/main/FP-GOLF/GPU/nist_gpu.cu>
  - <https://github.com/russdrh/FP-GOLF/blob/main/FP-GOLF/GPU/sign_gpu.cu>
  - <https://github.com/russdrh/FP-GOLF/blob/main/FP-GOLF/GPU/fft_gpu.cu>
  - <https://github.com/russdrh/FP-GOLF/blob/main/FP-GOLF/GPU/fpr_gpu.cuh>
  - <https://github.com/russdrh/FP-GOLF/blob/main/FP-GOLF/GPU/rng_gpu.cu>
  - <https://github.com/russdrh/FP-GOLF/blob/main/FP-GOLF/GPU/katrng_gpu.cu>
  - <https://github.com/benlwk/Falcon-Mitaka>
  - <https://github.com/search?q=falcon+gpu&type=repositories>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `paper:golf-gpu-accelerated-optimization-for-lattice-based-falcon`) · [data/wave7/enrich/raw/paper_golf_gpu_accelerated_optimization_for_lattice_based_falcon.json](../../../data/wave7/enrich/raw/paper_golf_gpu_accelerated_optimization_for_lattice_based_falcon.json) (enrichment confidence 0.7)

</details>
