# GRASP: GPU-based paRallel Accelerated SPHINCS+

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Signatures and key exchange](README.md)</sub>

**Tier C** (first-party claim) · Study only · `CUDA` · `no license` · ⚪ unknown

> Single-kernel CUDA SPHINCS+-SHA256-f-simple batch signer/verifier; 1.37-3.45x over Kim et al.'s GPU code, 1,820-3,659x the single-core reference.

| | |
|---|---|
| **Beats** | NIST PQC SPHINCS+ reference C code (version 3.0), SHA-256 simple fast parameter sets, run by the authors on a single core of an AMD Ryzen 5 5600G; also the open-source GPU SPHINCS+ of Kim et al. (re-run on the same GPU) plus prior GPU/FPGA works |
| **Claimed result** | SPHINCS+-SHA256-f-simple on RTX 4090, kernel time only (memcpy excluded). Signing: 146,363 / 82,621 / 40,489 ops/s at levels 1/3/5, which is 3659.08x / 3177.73x / 3114.54x over the single-core NIST reference (40/26/13 ops/s). Verification: 1,499,590 / 933,696 / 886,362 ops/s, which is 2029.22x / 1897.76x / 1820.05x over the reference (Table VI). Against Kim et al. (open-source, re-run on the same RTX 4090): signing 1.37x/1.79x/1.58x (1.36x/1.65x/1.49x with memcpy) and verification 1.53x/1.80x/3.45x. |
| **Workload** | SPHINCS+-SHA256-128f/192f/256f-simple signing and verification throughput (ops/s) on an RTX 4090, compared with the NIST reference C code on one Ryzen 5 5600G core and with prior GPU/FPGA SPHINCS+ implementations; headline GPU numbers exclude host-device memcpy time |
| **Metric** | throughput |
| **Hardware** | NVIDIA GeForce RTX 4090 (also RTX 3090 and GTX 1080); CPU baseline on an AMD Ryzen 5 5600G (single core); Linux |
| **Compiler and flags** | NVCC on Linux (version and flags not stated); the CPU reference build's compiler and flags are not stated |
| **Links** | [benchmark](https://eprint.iacr.org/2024/1030) |

## Verdict

On an RTX 4090, timing kernels only (host-device copies excluded, averaged over 1,000 runs, NVCC version and flags unstated), GRASP signs 146,363 / 82,621 / 40,489 and verifies 1,499,590 / 933,696 / 886,362 SPHINCS+-SHA256-128f/192f/256f-simple signatures per second. That is 3,114-3,659x (signing) and 1,820-2,029x (verification) the NIST reference C code v3.0 on one Ryzen 5 5600G core. The like-for-like result is 1.37-1.79x signing and 1.53-3.45x verification over Kim et al.'s open-source GPU code re-run on the same RTX 4090.

## Use it when

- High-volume SPHINCS+ signing on a data-center GPU (e.g. a code- or firmware-signing farm) that accepts SHA-256 fast-simple parameters: 146,363 / 82,621 / 40,489 signatures/s at levels 1/3/5 on an RTX 4090.
- Mass verification of SPHINCS+-SHA256-f signatures: 1.5M/s at level 1 on an RTX 4090, one thread per signature.
- A GPU signer that needs per-signature latency: the low-latency mode signs in 0.512 ms at level 1 (25 ms for the CPU reference, 4.8 ms for Kim et al.), at the cost of dropping to 19,521 ops/s.
- Reference techniques for your own GPU or CPU hash-based signer. Kernel fusion, gcd-sized thread teams and merging WOTS+ signing into leaf keygen are all described in enough detail to reimplement, and the paper says the WOTS+ merge also helps CPU code.

## Skip it when

- You need code. None was released and there is no license. The only open GPU SPHINCS+ code found is Kim et al.'s kindongsy/TCAS-SPHINCSp_GPU, which is unlicensed and consists of per-security-level Visual Studio projects.
- You need SHAKE, Haraka, 'robust' or small (s) parameter sets. Only SHA-256 fast-simple was measured; the claim that it is 'equally effective in all modes' is asserted, not benchmarked.
- You need FIPS 205 SLH-DSA compliance. The work targets SPHINCS+ round 3 (reference code v3.0), and compatibility with the final SLH-DSA standard is not documented.
- Small batches in the throughput mode. The peak needs a 128x512 grid; at 128x64, level-1 signing drops to 66.4 kops/s, 45% of the peak.
- Sizing end-to-end PCIe throughput from the headline. It excludes host-device copies: with memcpy, RTX 4090 level-1 signing falls from 146,363 to 117,723 ops/s, and with-memcpy verification numbers are not reported.

## How it is fast

Kernel fusion runs FORS, WOTS+ and the MSS hypertree in a single CUDA kernel. This avoids the global-memory hand-offs of Kim et al.'s multi-kernel design. The thread-team size is chosen so that both the hypertree layer count d and the FORS tree count k divide evenly (gcd(22,33)=11), with one thread per layer or subtree, so no threads sit idle during node merging. When the root of the layer below is already known, WOTS+ signing is folded into that leaf's public-key chain computation, which removes about 33% of the hash calls for those leaves and cuts separate WOTS+ signings from d to t per thread. The n-byte hash blocks move with 16-byte int4 loads and stores at levels 1 and 5, and with int2 at level 3, where 24-byte blocks would misalign.

## Compared with alternatives

Pick GRASP when you are committed to hash-based SPHINCS+ signatures and need GPU batch throughput. GOLF is the same group's GPU design for Falcon; it reaches 420k sign/s on the same RTX 4090 with 666-byte Falcon-512 signatures versus 17,088 bytes for SPHINCS+-128f, and it also ships no code. The CPU siblings (VecFalcon, ENG25519, UltrafastSecp256k1) release code and suit per-signature latency on CPUs.

## Integration

| | |
|---|---|
| **Form** | not released (paper only; described as one fused CUDA kernel for signing and one for verification) |
| **Dependencies** | not documented (unreleased); CUDA runtime implied |
| **Minimum toolchain** | not documented: the paper says only 'NVCC compiler' on Linux, with no CUDA version or flags |
| **Platforms** | NVIDIA GPUs: measured on RTX 4090, RTX 3090 and GTX 1080 under Linux |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Level-3 verification is reported inconsistently: the text says 1,408,846 ops/s, while Table VI and Fig. 13 say 933,696 (933.7 kops/s). The table value drives the 1897.76x and 1.80x ratios.
- The 1,820-3,659x ratios are against the portable reference C code on one Ryzen 5 5600G core with unstated flags (40/26/13 sign/s, 739/492/487 verify/s). No optimized CPU SPHINCS+ implementation was compared.
- The gap over Kim et al. shrinks with apples-to-apples conditions: 1.37/1.79/1.58x kernel-only on an RTX 4090 (Kim's open-source code re-run), 1.36/1.65/1.49x with memcpy, and 1.22/1.25/1.30x on an RTX 3090 against Kim's published with-memcpy figures.
- The low-latency and high-throughput modes are separate thread configurations. Low-latency gives 5.5x lower throughput than Kim et al. on the RTX 4090, so pick one per deployment.

## Known shortcomings

- No public code. The &gt;1000x ratios compare an RTX 4090 against one Ryzen 5 5600G core running the NIST SPHINCS+ reference; the headline numbers exclude memcpy, and NVCC/CPU flags are not given. Against other GPU code (Kim et al., re-run on the same RTX 4090) the gain is 1.37-3.45x.
- Only SHA256-f-simple is measured; including memcpy, level-1 signing drops from 146k to 118k/s. Needs a 128x512 launch grid (128x64 reaches 45% of peak). Level-3 verify figure differs between text (1,408,846) and table (933,696). Baseline is the portable reference v3.0 on one core, with no optimized CPU build compared. SLH-DSA (FIPS 205) compatibility not documented.

## Caveats and trade-offs

Peer-reviewed as IEEE Transactions on Computers vol. 75, no. 4, pp. 1579-1592 (2026), doi:10.1109/TC.2026.3654650; the ePrint copy is labelled Preprint and has a different title ('GRASP: Accelerating Hash-based PQC Performance on GPU Parallel Architecture'). The &gt;1000x figure is GPU batch throughput against a single CPU core, with compiler flags unstated on both sides. The headline GPU numbers exclude memcpy. The level-3 verification figure in the text (1,408,846 ops/s) conflicts with Table VI (933,696 ops/s). No code release was found.

No public code repository located; GPU batch throughput vs single-thread reference, not representative of single-signature latency; SPHINCS+ is already the slowest NIST signature scheme so large multiples over its reference implementation are expected.

## Maintenance

This is unreleased research code from a peer-reviewed paper (IEEE TC vol. 75 no. 4, pp. 1579-1592, 2026; ePrint revised 2025-01-16) with no repo, license or maintenance, so treat it as a technique reference only. Both the ePrint and the journal version are titled 'GRASP: Accelerating Hash-based PQC Performance on GPU Parallel Architecture'; the catalog name is the expanded acronym.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The paper was peer-reviewed (IEEE Transactions on Computers 2026) and re-ran the NIST SPHINCS+ reference C code v3.0 on one core of a Ryzen 5 5600G. However, neither the NVCC nor the CPU compiler flags/version are stated, and the gains are 1820x-3659x, so the implausible-ratio rule caps the tier at C. No code was released.
- **Verifier notes:** The record's claim matches the abstract. I added the concrete per-level numbers and the peer-reviewed venue (IEEE TC 2026). Tier stays C because of the &gt;1000x cross-hardware ratio with unstated flags. The more meaningful result is 1.37x-3.45x against Kim et al.'s open-source GPU code, re-run on the same RTX 4090.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `hardware`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** IEEE TC 2026: signing 3659x/3178x/3115x, verifying 2029x/1898x/1820x vs SPHINCS+ ref v3.0 (1 core); 1.37-3.45x vs Kim et al. GPU.
- **Pages the verifier opened:**
  - <https://eprint.iacr.org/2024/1030>
  - <https://eprint.iacr.org/2024/1030.pdf>
  - <https://api.crossref.org/works/10.1109/tc.2026.3654650>
- **Sources the enricher read:**
  - <https://eprint.iacr.org/2024/1030>
  - <https://eprint.iacr.org/2024/1030.pdf>
  - <https://api.crossref.org/works/10.1109/tc.2026.3654650>
  - <https://github.com/search?q=sphincs+gpu&type=repositories>
  - <https://github.com/search?q=sphincs+language%3Acuda&type=repositories>
  - <https://github.com/search?q=GRASP+SPHINCS&type=repositories>
  - <https://github.com/kindongsy/TCAS-SPHINCSp_GPU>
  - <https://github.com/choileta/NIST_PQC_SPHINCSp_throughput>
  - <https://hn.algolia.com/api/v1/search?query=GRASP%20SPHINCS&tags=story>
  - <https://eprint.iacr.org/2025/749.pdf>
  - <https://falcon-sign.info/>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `paper:grasp-gpu-based-parallel-accelerated-sphincs`) · [data/wave7/enrich/raw/paper_grasp_gpu_based_parallel_accelerated_sphincs.json](../../../data/wave7/enrich/raw/paper_grasp_gpu_based_parallel_accelerated_sphincs.json) (enrichment confidence 0.75)

</details>
