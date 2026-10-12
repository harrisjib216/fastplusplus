# ML-KEM AVX-512 optimization for TLS 1.3 (Zheng et al., Fudan University)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Signatures and key exchange](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `C` · `no license` · ⚪ unknown

> Unreleased AVX-512 ML-KEM (ESORICS 2024) reporting 1.30-1.64x fewer cycles than pq-crystals AVX2 Kyber, but only 0.4-5.6% more TLS handshakes.

| | |
|---|---|
| **Beats** | pq-crystals Kyber 'standard' branch AVX2 implementation (FIPS 203 draft code, the paper's ref [5]) for ML-KEM cycle counts; liboqs 0.10.1 ML-KEM AVX2 via OQS-provider on OpenSSL 3.3.0-dev for TLS 1.3 handshakes/sec |
| **Claimed result** | AVX-512 ML-KEM is 1.30x-1.64x faster than the AVX2 implementation in median CPU cycles (max 1.64x for ML-KEM-1024 Encaps: 25,062 vs 41,162 cycles). Batched keygen (8 keys) gives 4.9x / 4.2x / 3.5x for ML-KEM-512/768/1024 per the paper. TLS 1.3 handshake gains are small, about 0.4-5.6% more connections/sec in most PQ-only and hybrid configurations (derived from page data), and the paper itself calls them 'subtle' / 'minimal'. |
| **Workload** | ML-KEM-512/768/1024 key generation, encapsulation, and decapsulation, plus a batch key-generation variant, integrated into liboqs and OQS-provider for OpenSSL/TLS 1.3 handshakes |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Platinum 8475B, 4 vCPUs, 8 GiB memory (Alibaba Cloud c8i compute-optimized instance, Sapphire Rapids) |
| **Compiler and flags** | GCC 9.4.0 (optimization flags not stated); AVX-512 disabled when benchmarking the AVX2 baseline; Turbo Boost and hyper-threading left on; median of 100,000 runs; TLS tests with OpenSSL 3.3.0-dev + OQS provider (openssl s_server / s_time) |
| **Links** | [benchmark](https://arxiv.org/abs/2404.13544) |

## Verdict

On a 4-vCPU Alibaba c8i VM (Xeon Platinum 8475B, GCC 9.4.0, flags unstated, Turbo and HT on), the median over 100,000 runs shows the AVX-512 code using 1.30-1.64x fewer cycles than the pq-crystals 'standard'-branch AVX2 Kyber built with AVX-512 disabled (for example, ML-KEM-1024 encaps at 25,062 vs 41,162 cycles). Through liboqs 0.10.1, the OQS provider and OpenSSL 3.3.0-dev, openssl s_time handshakes/sec rose only about 0.4-5.6% in PQ-only and hybrid modes.

## Use it when

- As a design blueprint if you maintain an ML-KEM backend for AVX-512 x86 servers such as Sapphire Rapids and want roughly 1.3-1.6x over the pq-crystals AVX2 kernels.
- TLS terminators or KEM key pools that can pre-generate ephemeral keys 8 at a time: batched keygen is reported at 2,804 / 4,866 / 7,394 cycles per key for ML-KEM-512/768/1024.
- Capacity planning: the paper's handshake data shows faster KEM code barely moves openssl s_time throughput, which is useful evidence before spending effort on KEM kernels.
- Research on IND-1-CCA KEMs for ephemeral TLS key exchange: TRH decaps is 5,666 vs 19,838 cycles for ML-KEM-512 (measured on the AVX2 code), with the same ciphertext size.

## Skip it when

- When you need something you can build or audit: the paper says 'we will later open source our code', and no repository was found as of 2026-09. The only public AVX-512 Kyber repo found (cccccosine/Kyber_AVX512_32w) is a different ISC 2024 multi-way paper.
- CPUs without AVX-512: the design depends on 32 zmm registers, mask registers, compress-store and vpermb, and has no fallback path.
- Hybrid-mode TLS (X25519/P-256 + ML-KEM) where you expect big handshake gains: Table 4 shows about 0.4-5.6% more connections/sec, because ECDH and signatures dominate.
- Deployments that need final-FIPS 203 or CMVP conformance: the code was built on FIPS 203 draft base code, final-standard conformance is not documented, and the faster TRH/TCH variants are not ML-KEM at all.
- One-off keygen latency: batching only pays off when the caller consumes 8 key pairs at once, which needs application or protocol changes.

## How it is fast

Each 512-bit zmm register holds 32 signed 16-bit coefficients, so one polynomial fits in 8 registers. All 7 NTT layers are merged: coefficients load once, and shuffle16/8/4/2/1 permutes pair them up at each butterfly distance. The butterflies use signed Montgomery reduction (vpmullw/vpmulhw with twiddles premultiplied by q^-1), Barrett reduction (vpmulhw plus a shift), and lazy reduction in the inverse NTT. Keccak-p[1600] runs 8 states in parallel instead of AVX2's 4. Rejection sampling and CBD sampling use AVX-512 mask registers and compress-store, and pk/sk decode and decompress use the byte permute vpermb.

## Compared with alternatives

It is the only catalogued AVX-512 ML-KEM result, so use it as a reference design; for runnable ML-KEM code, moduletto (NEON ML-KEM-512 on aarch64, benchmarked against liboqs 0.16.0) actually ships. The same group's Dilithium-AVX512 (the paper's ref [56]) has public code for the signature side, and ENG25519 (ref [55]) speeds up the X25519 half that this paper's own data shows dominates hybrid handshakes.

## Integration

| | |
|---|---|
| **Form** | not applicable: paper only. It describes a source patch to liboqs 0.10.1 (ml_kem directory) used via oqs-provider, and it was never released. |
| **Dependencies** | not documented (unreleased); the paper's integration used liboqs 0.10.1, oqs-provider and OpenSSL 3.3.0-dev |
| **Minimum toolchain** | GCC 9.4.0 in the paper's evaluation, optimization flags not stated; kernels are shown as GNU-as AT&T-syntax macros |
| **Platforms** | x86-64 with AVX-512 (including the vpermb byte permute), evaluated only on a 4-vCPU Alibaba Cloud ecs.c8i.xlarge (Xeon Platinum 8475B, Sapphire Rapids) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial: per the paper it slots into liboqs as alternate ML-KEM Keygen/Encaps/Decaps behind an OQS_ENABLE_KEM_ml_kem_512_avx512 config macro, so OQS-provider and OpenSSL callers do not change. But the code is unreleased, and batch keygen requires callers to take 8 keys at a time. |

## Gotchas

- Table 3 anomaly: the AVX2 ML-KEM-1024/Dilithium5 cell (3191.46 conn/s) duplicates the Falcon512 cell, so AVX-512 appears slower there (2451.08). It also contradicts the paper's own statement that handshakes/sec drop as the security level rises, so it is likely a copy error and that column is unreliable.
- The batch-keygen ratios printed in Table 2 (4.9x/4.2x/3.5x) are a bit higher than the same table's non-batched AVX-512 keygen implies (about 4.7x/4.0x/3.4x). Also, Algorithm 4 as printed batches only the final SHA3-256 over the 8 encapsulation keys while K-PKE.KeyGen runs in a loop, so the paper does not explain how per-key cost falls to 2,804 cycles.
- The printed assembly has errors: Algorithm 2 (Gentleman-Sande butterfly) repeats 'vpmulhw %zmm\zh' on two lines where a low-half product with the zeta\*q^-1 constant is needed, so do not transcribe the listings verbatim.
- Noisy measurement setup: Turbo Boost and hyper-threading were left on, the host was a 4-vCPU cloud VM, and TLS client and server ran on the same machine. Handshake deltas of about 1-5% are within what such setups can drift.

## Known shortcomings

- No public code. Real baseline is the pq-crystals Kyber AVX2 implementation (liboqs is used only for the TLS integration); gain 1.30-1.64x on the KEM, but only \~0.4-5.6% end-to-end in TLS 1.3 (derived), and one Table 3 cell is slower. Needs AVX-512.
- Code still unreleased (cccccosine/Kyber_AVX512_32w is a different paper). Table 3's ML-KEM-1024/Dilithium5 cell looks like a copy error; the 3.5-4.9x batch keygen is not explained by Algorithm 4 as printed (it batches only SHA3-256(ek)). Measured on a 4-vCPU VM with Turbo and HT on, flags unstated, against FIPS 203 draft code. liboqs has no AVX-512 ML-KEM (it now uses mlkem-native).

## Caveats and trade-offs

Published at ESORICS 2024 (LNCS), but the paper only says 'we will later open source our code' and no public repository was found (GitHub repo and code search), so has_code=false and the result cannot be reproduced. Table 3 has one cell where AVX-512 is slower (ML-KEM-1024/Dilithium5: 2451.08 vs 3191.46 conn/s, an AVX2 value that duplicates the Falcon512 cell, so possibly a copy error). The stated batch-keygen ratios are a little higher than the table implies against non-batched AVX-512 keygen (about 4.7x / 4.0x / 3.4x, derived from page data). Handshake gains are within about 6%.

Requires AVX-512; the paper's batch key-generation method requires protocol-level changes to how TLS 1.3 handshakes request/consume KEM keys, not just a drop-in library swap.

## Maintenance

Peer-reviewed (ESORICS 2024, LNCS pp. 123-143), but the promised code never appeared, liboqs has no AVX-512 ML-KEM from this work (it switched to mlkem-native in 2025), and there is no license or maintenance, so treat it as a paper-only reference design.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded C-&gt;B: the paper was peer-reviewed and published at ESORICS 2024 (LNCS, DOI 10.1007/978-3-031-70890-9_7, pp. 123-143), and its Table 2 shows 1.30-1.64x cycle-count wins over the pq-crystals Kyber AVX2 code (GCC 9.4.0, Xeon Platinum 8475B). It falls short of A because no code has been released (searched GitHub) and compiler flags are not stated.
- **Verifier notes:** Hardware and compiler claims check out; the baseline for the headline 1.64x is the pq-crystals standard-branch AVX2 code, not liboqs itself (liboqs 0.10.1 is only the integration target), so I corrected baseline to say so and left baseline_in_list=true because the TLS comparison runs through liboqs. The tier is upgraded to B on the confirmed ESORICS 2024 publication.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** ESORICS 2024: ML-KEM AVX-512 1.30-1.64x vs pq-crystals AVX2; TLS 1.3 handshake gain \~0.4-5.6%.
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2404.13544>
  - <https://arxiv.org/pdf/2404.13544>
  - <https://api.crossref.org/works/10.1007/978-3-031-70890-9_7>
  - <https://link.springer.com/chapter/10.1007/978-3-031-70890-9_7>
  - <https://github.com/cccccosine/Kyber_AVX512_32w>
- **Sources the enricher read:**
  - <https://arxiv.org/abs/2404.13544>
  - <https://arxiv.org/pdf/2404.13544>
  - <https://export.arxiv.org/api/query?id_list=2404.13544>
  - <https://api.crossref.org/works/10.1007/978-3-031-70890-9_7>
  - <https://api.crossref.org/works?query.bibliographic=Faster+Post-Quantum+TLS+1.3+Based+on+ML-KEM&rows=3>
  - <https://github.com/cccccosine/Kyber_AVX512_32w>
  - <https://github.com/cccccosine>
  - <https://github.com/search?q=kyber+avx512&type=repositories>
  - <https://github.com/search?q=ml-kem+avx512&type=repositories>
  - <https://github.com/open-quantum-safe/liboqs/pulls?q=avx512>
  - <https://github.com/open-quantum-safe/liboqs/pull/2041>
  - <https://github.com/open-quantum-safe/liboqs/pull/2167>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `paper:ml-kem-avx-512-optimization-for-tls-1-3-zheng-et-al-fudan-university`) · [data/wave7/enrich/raw/paper_ml_kem_avx_512_optimization_for_tls_1_3_zheng_et_al_fudan_university.json](../../../data/wave7/enrich/raw/paper_ml_kem_avx_512_optimization_for_tls_1_3_zheng_et_al_fudan_university.json) (enrichment confidence 0.7)

</details>
