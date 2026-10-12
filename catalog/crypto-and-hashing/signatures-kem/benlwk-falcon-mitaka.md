# Falcon-Mitaka GPU (High Throughput Lattice-based Signatures on GPUs)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Signatures and key exchange](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `CUDA` · `GPL-3.0` · 🟡 stale

> Batched CUDA Falcon-512/Mitaka-512 sign and verify; the paper reports 8.8-18.5x sign and 105-149x verify throughput over CPU AVX2 Falcon.

| | |
|---|---|
| **Beats** | Falcon NIST-submission AVX2-optimized CPU implementation (Fouque et al. [4]); Mitaka is compared only against its FP64 reference C. liboqs was not benchmarked. |
| **Claimed result** | The paper's stated ratios do not match its own tables. '7.78x sign / 52.43x verify vs AVX2' (RTX 3080, Falcon-512) is actually vs the FP64 reference (27908/3587, 1913380/36491). 'Falcon-1024 20.56x/148.56x' equals A100 Falcon-512 throughput divided by AVX2 Falcon-1024 throughput. The abstract's '20.03x/29.51x' equals Mitaka-512 on A100 vs the Mitaka FP64 reference. Recomputed from Tables 5/6, Falcon GPU batch throughput (K=16384) vs AVX2 CPU (derived from page data): Falcon-512 RTX 3080 8.81x sign / 104.96x verify; Falcon-1024 RTX 3080 5.35x / 66.45x; Falcon-512 A100 18.50x / 149.29x; Falcon-1024 A100 13.18x / 114.24x. |
| **Workload** | Falcon-512/1024 batched signing and verification throughput on GPU (K up to 16,384 signatures per launch) vs the Falcon AVX2-optimized CPU implementation; Mitaka-512/1024 GPU vs the Mitaka FP64 reference C |
| **Metric** | throughput |
| **Hardware** | NVIDIA RTX 3080 (8704 CUDA cores; desktop host Intel i9-10900K @3.70GHz) plus A100/V100/T4 on the ARDC Nectar cloud (host Intel Xeon Gold 6150 @2.2GHz). The paper does not say which CPU or how many threads produced the AVX2/FP64 CPU baseline rates in Table 6. |
| **Compiler and flags** | GPU: CUDA 11 (paper Table 4); repo Makefile uses CUDA 11.7 nvcc -rdc=true -arch sm_86 with gcc as the host compiler. Compiler/flags for the CPU AVX2 baseline are not stated anywhere in the paper. |
| **Adoption** | 5 stars |
| **Last commit** | 2023-11-14 |
| **Links** | [repository](https://github.com/benlwk/Falcon-Mitaka) · [benchmark](https://eprint.iacr.org/2023/399.pdf) |

## Verdict

The TPDS 2024 paper (Tables 5-6, CUDA 11, averaged over 30 runs, batch K=16,384) reports Falcon-512 at 27,908 sign/s and 1,913,380 verify/s on an RTX 3080, and 58,595 and 2,721,562 on an A100. Against the Falcon AVX2 CPU rates of 3,167 sign/s and 18,230 verify/s, that is 8.8x/105x (RTX 3080) and 18.5x/149x (A100); Falcon-1024 comes out at 5.35x/66x and 13.2x/114x. The CPU model, thread count and compiler for the AVX2 baseline are never stated. The paper's own 'vs AVX2' ratios are really against the FP64 reference, and its AVX2 Falcon-512 sign rate (3,167/s) is oddly below the FP64 reference's (3,587/s).

## Use it when

- Server-side bulk Falcon-512 verification with thousands of pending signatures on an NVIDIA GPU: on the RTX 3080 the paper reports 1.07M verifies/s at K=1024 (0.95 ms per batch) and 1.91M/s at K=16,384, against 18,230/s for the AVX2 CPU code.
- Throughput-bound batch signing when latency of tens to hundreds of ms per batch is acceptable. On the A100, Falcon-512 reaches 58,595 signs/s at K=16,384 (280 ms per batch).
- Comparing Mitaka with Falcon for parallel hardware: Mitaka-512 signing is 2.7-2.8x faster than Falcon-512 at K=16,384 on the RTX 3080 and A100.
- Starting point for GPU FN-DSA/Falcon research (GPL-3.0): the iterative ffSampling, shared-memory FFT/NTT kernels and kernel-fusion patterns can be reused.

## Skip it when

- Latency-bound or small-batch signing. At K=32 on the RTX 3080, Falcon-512 signs only 2,000/s with 16 ms batch latency, below the paper's own CPU AVX2 figure of 3,167/s.
- Anything production-like. Keys, seeds and nonces are test vectors, there is no keygen or real API, failed norm checks are not retried, the Mitaka sampler keys come from libc rand(), and there are no CUDA error checks or cudaFree calls.
- Falcon-1024, Mitaka-1024 or FIPS 206 FN-DSA: only the 512 variants are in the repo, even though the paper benchmarks the 1024 variants.
- Consumer or inference GPUs with weak FP64. Falcon signing is FP64-bound, so the A100 signs about 2.1x faster than the RTX 3080 at K=16,384, and the paper notes FP64 runs at 1/32 of the int32 rate on the RTX 3080 and T4.
- Proprietary products that cannot accept GPL-3.0 copyleft, or settings that need side-channel review. The paper does not discuss constant-time or GPU timing leakage.

## How it is fast

The work is split coarse- then fine-grain. K signatures run as K CUDA blocks, and inside each block the polynomial work is spread over threads (N/4 threads for the shared-memory FFT, N/2 for the NTT mod 12289, N for coefficient-wise ops), with small kernels fused under COMB_KER. Falcon's recursive ffSampling is rewritten as an iterative loop over an explicit stack (ffSampling_fft_dyntree), which avoids CUDA dynamic parallelism. That loop still runs one thread per signature and dominates signing time (65.8% of Falcon-512 CPU signing time per the paper's Table 1). Mitaka's sampler is split into a bulk ChaCha20 random-byte phase (N threads per signature) and a per-coefficient discrete-Gaussian phase, so Mitaka signing is fully data-parallel. Falcon verification runs entirely on integer NTT kernels, which is why the verify gains are much larger than the sign gains.

## Compared with alternatives

Pick it over GOLF when you need GPU Falcon code you can actually read and run. GOLF reports far higher Falcon throughput (420k sign/s on an RTX 4090), but no repository is catalogued for it. Pick VecFalcon instead when you care about per-signature latency on a CPU (SSE2/AVX2/AVX-512/NEON/RVV, 1.1-1.6x over c-fn-dsa); pick this one only for large GPU batches or to evaluate Mitaka.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | CUDA runtime (cudart) only |
| **Minimum toolchain** | nvcc from CUDA 11.7 (Falcon Makefile) or CUDA 12.1 (Mitaka Makefile) with gcc as the host compiler; the paper lists CUDA 11 |
| **Platforms** | NVIDIA GPUs. Both Makefiles hard-code -arch sm_86, and the README says it is tested on the RTX 3080 and A100; the paper also ran it on V100 and T4. No CPU fallback. |
| **Thread safety** | Not documented. Each crypto_sign/crypto_ver call allocates its own pinned-host and device buffers and never frees them, and there is no stream or concurrency handling. |
| **Drop-in for the baseline** | no |

## Gotchas

- ffSampling_fft_dyntree loads the sampler SHAKE state from scA[0..24] (batch slot 0) in every block instead of scA[bid\*25+i]. With real per-signature seeds, every signature in a batch would draw the same sampler randomness; the harness hides this because all slots use the same seed.
- A signature that fails the norm bound is not regenerated. is_short_half_gpu/check_norm only set a flag or printf 'short half detected', whereas the reference implementation restarts sampling.
- The repo's Mitaka verify defaults to an integer NTT path added in November 2023 (FLOAT_VER is off), while the paper's Mitaka verify numbers used FP64 FFT, so re-runs will not match Table 5. Mitaka also allocates a BATCH×512×512-byte PRNG buffer, 256 MiB at BATCH=1024 and 4 GiB at 16,384.
- Reported throughput includes host-device copies. Falcon rebuilds the full basis (complete_private) and the LDL tree for every signature, with no expanded-key fast path.

## Known shortcomings

- GPU vs CPU: the AVX2 baseline's compiler, flags, CPU and thread count are unstated. The paper's ratios do not match its own tables (7.78x/52.43x are vs the FP64 reference; 20.03x/29.51x are Mitaka vs FP64). Real Falcon-512 RTX 3080 vs AVX2 is 8.81x/104.96x (derived).
- Benchmark harness only: hard-coded keys/seeds/nonces, no keygen or API, no cudaFree or error checks. ffSampling seeds every block from slot 0, so real per-signature seeds would share sampler randomness; norm-failed signatures are not retried; Mitaka PRNG keys come from rand(). Small batches lose: K=32 on an RTX 3080 gives 2,000 signs/s (16 ms), below the CPU AVX2 3,167/s. Repo's Mitaka verify now uses an integer NTT (Nov 2023) while the paper measured FP64. Falcon-512 only, sm_86, GPL-3.0.

## Caveats and trade-offs

This compares a GPU batch against a CPU implementation of unstated thread count, so the &gt;50x verify ratios are a hardware and batching effect. Per-batch latency is high (e.g. 587 ms for a 16,384-signature Falcon-512 sign batch on the RTX 3080). The paper's own speedup text misattributes baselines (see claimed_speedup). Released code covers only Falcon-512 and Mitaka-512, targets sm_86, and has no CPU baseline harness. It rebuilds the LDL tree on every signature. No commits since 2023-11-14.

Needs a CUDA GPU and large signature batches to amortize kernel-launch overhead; single-signature latency is not necessarily better than CPU; public repo only ships Falcon-512 and Mitaka-512, not the 1024 variants benchmarked in the paper.

## Maintenance

Stale: 9 commits, the last on 2023-11-14 (Mitaka integer verify), 5 stars and no issues. It is GPL-3.0 and small enough to copy as research code, but it needs a real API, key and nonce handling, and the RNG and retry bugs fixed before any real use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now B.
- **Tier reason:** The paper is peer-reviewed (IEEE TPDS 2024, DOI 10.1109/TPDS.2024.3367319) and its Table 6 compares GPU throughput against the Falcon AVX2 CPU implementation, so B. It is not A because the paper gives no compiler, flags, thread count or even which CPU ran the AVX2 baseline (Table 4 lists only 'CUDA 11'). The repo has no AVX2 baseline harness, and its released code covers only Falcon-512 and Mitaka-512.
- **Verifier notes:** The main fix is claimed_speedup: none of the record's three headline ratio pairs is actually Falcon-vs-AVX2 per the paper's own Tables 5/6, so I replaced them with ratios recomputed from the page data. Metadata (GPL-3.0, 5 stars, last commit 2023-11-14, stale, copyable) checks out.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Shortcomings recorded by:** TPDS 2024 tables: Falcon-512 on RTX 3080 vs AVX2 CPU 8.81x / 104.96x (derived).
- **Pages the verifier opened:**
  - <https://eprint.iacr.org/2023/399.pdf>
  - <https://github.com/benlwk/Falcon-Mitaka>
  - <https://api.crossref.org/works?query.title=High+Throughput+Lattice-based+Signatures+on+GPUs+Comparing+Falcon+and+Mitaka>
- **Sources the enricher read:**
  - <https://github.com/benlwk/Falcon-Mitaka>
  - <https://github.com/benlwk/Falcon-Mitaka/blob/main/README.md>
  - <https://github.com/benlwk/Falcon-Mitaka/blob/main/falcon-gpu-512/Makefile>
  - <https://github.com/benlwk/Falcon-Mitaka/blob/main/falcon-gpu-512/main.cu>
  - <https://github.com/benlwk/Falcon-Mitaka/blob/main/falcon-gpu-512/include/cuda_kernel.cuh>
  - <https://github.com/benlwk/Falcon-Mitaka/blob/main/falcon-gpu-512/src/cuda_kernel.cu>
  - <https://github.com/benlwk/Falcon-Mitaka/blob/main/falcon-gpu-512/src/ffSampling.cu>
  - <https://github.com/benlwk/Falcon-Mitaka/blob/main/falcon-gpu-512/src/fft.cu>
  - <https://github.com/benlwk/Falcon-Mitaka/blob/main/falcon-gpu-512/src/common.cu>
  - <https://github.com/benlwk/Falcon-Mitaka/blob/main/falcon-gpu-512/include/fpr.cuh>
  - <https://github.com/benlwk/Falcon-Mitaka/blob/main/mitaka-gpu-512/Makefile>
  - <https://github.com/benlwk/Falcon-Mitaka/blob/main/mitaka-gpu-512/main.cu>
  - <https://github.com/benlwk/Falcon-Mitaka/blob/main/mitaka-gpu-512/include/cuda_kernel.cuh>
  - <https://github.com/benlwk/Falcon-Mitaka/blob/main/mitaka-gpu-512/src/cuda_kernel.cu>
  - <https://github.com/benlwk/Falcon-Mitaka/blob/main/mitaka-gpu-512/src/samplerZ.cu>
  - <https://github.com/benlwk/Falcon-Mitaka/commit/0bacd49>
  - <https://eprint.iacr.org/2023/399.pdf>
  - <https://eprint.iacr.org/2023/399>
  - <https://api.crossref.org/works/10.1109/TPDS.2024.3367319>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/benlwk/falcon-mitaka`) · [data/wave7/enrich/raw/github_com_benlwk_falcon_mitaka.json](../../../data/wave7/enrich/raw/github_com_benlwk_falcon_mitaka.json) (enrichment confidence 0.8)

</details>
