# Intel(R) Multi-Buffer Crypto for IPsec (intel-ipsec-mb)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [AEAD and ciphers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> Intel's x86-64 assembly packet-crypto library; batches many packets per SIMD pass; beat OpenSSL AES-CBC+HMAC-SHA-256 once.

| | |
|---|---|
| **Beats** | OpenSSL (AES-256-CBC+HMAC-SHA-256 throughput) and FreeBSD OpenCrypto Framework (OCF) default kernel crypto (AES-GCM / ChaCha20-Poly1305 VPN throughput) |
| **Claimed result** | Netgate AsiaBSDCon 2023 paper: on an AVX2 test host, IPsec-MB did 18.1 Gbps AES-256-CBC+HMAC-SHA-256 on 1400-byte blocks vs OpenSSL's maximum of 10.4 Gbps on 16 kB blocks, about 1.7x (derived from page data). In pfSense/FreeBSD VPN tests, the IIMB engine was compared with FreeBSD's default OpenCrypto Framework (OCF) on Ryzen 5 5600 VMs: OpenVPN DCO AES-256-GCM async 10 vs 6.0 Gbps; ChaCha20-Poly1305 async 7.0 vs 4.10 Gbps; IPsec-ESP AES-128-GCM async 7.68 vs 4.46 Gbps. On the Netgate SG-8200 (Atom C3758), OpenVPN AES-256-GCM async was 2.50 vs 1.50 Gbps. |
| **Workload** | Raw AES-256-CBC+HMAC-SHA-256 throughput vs OpenSSL on an AVX2 host, plus end-to-end iperf3 VPN throughput (OpenVPN DCO, IPsec-ESP, WireGuard) in pfSense/FreeBSD with an IIMB-based engine replacing OCF as the in-kernel crypto provider |
| **Metric** | throughput |
| **Hardware** | OpenSSL comparison: unnamed 'test host with AVX2'. VPN tests: AMD Ryzen 5 5600 (KVM/QEMU VMs running FreeBSD-CURRENT) and Netgate SG-8200 (Intel Atom C3758). |
| **Adoption** | 339 stars; used as the software crypto backend in DPDK, Intel(R) QAT Engine, and FD.io |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/intel/intel-ipsec-mb) · [benchmark](https://2023.asiabsdcon.org/program/_p05b/paper.pdf) |

## Verdict

The only comparison against OpenSSL is one sentence in Netgate's AsiaBSDCon 2023 paper. On an unnamed AVX2 host, IPsec-MB ran AES-256-CBC+HMAC-SHA-256 at 18.1 Gbps on 1400-byte blocks, against OpenSSL's best of 10.4 Gbps on 16 kB blocks (about 1.7x), with no CPU model, compiler, OpenSSL version or benchmark code given. The other gains are end-to-end iperf3 VPN throughput in FreeBSD-CURRENT VMs on a Ryzen 5 5600 (plus an Atom C3758 SG-8200), where Netgate's batching engine plus this library replaced FreeBSD's OCF. Those numbers measure the engine and the library together, not the library against OpenSSL.

## Use it when

- IPsec gateways, VPN concentrators and DPDK/VPP data planes that always have many independent packets in flight and can keep the job queue full.
- Legacy AES-CBC + HMAC-SHA1/SHA2 suites, which gain the most from multi-lane batching. Netgate measured 18.1 Gbps on 1400-byte packets against OpenSSL's best of 10.4 Gbps on 16 kB buffers.
- 3GPP, DOCSIS or PON stacks that need ZUC-EEA3/EIA3, SNOW3G, KASUMI, the 5G NEA4/5/6 ciphers, DOCSIS AES/DES or PON CRC-BIP with SIMD multi-lane code. Few general crypto libraries ship these.
- Async crypto engines, in the kernel or in userspace, that batch standard AEADs (AES-GCM, ChaCha20-Poly1305). Netgate's FreeBSD engine moved OpenVPN DCO AES-256-GCM from 6.0 to 10 Gbps async and IPsec-ESP AES-128-GCM from 4.46 to 7.68 Gbps, compared with FreeBSD's OCF.
- Recent x86-64 servers with VAES, VPCLMULQDQ and AVX-512 or AVX10 (Ice Lake, Sapphire Rapids and later), where the by32 GCM and x16-lane paths are used. It is also a fit when you need a power-up self-test and ACVP harness for CAVP.

## Skip it when

- Any non-x86-64 target. INSTALL.md says compilation is 'x64 only', and the maintainers declined an Arm64 port (issue #145). Arm keeps a separate fork at gitlab.arm.com, and Netgate had to use ISA-L and OpenSSL code on ARM.
- Low-rate or latency-bound traffic where one message is usually outstanding. Intel's white paper warns that calling flush after every submit is correct but slower than good single-buffer code, and that the design assumes flushes are rare.
- Replacing OpenSSL EVP in a production application. The in-repo OpenSSL 3.x imb-provider is labeled 'evaluation, development, and benchmarking only'. The production route, QAT Engine's qat_sw, uses this library only for AES-GCM and requires AVX-512F, AVX512_IFMA, VAES and VPCLMULQDQ.
- Single large AES-GCM or ChaCha20-Poly1305 buffers where OpenSSL is already in use. These AEADs are single-buffer multi-block here, as they are in OpenSSL's assembly, and no published head-to-head against OpenSSL shows a gain for them.
- SM3/SM4 on CPUs without SM3NI/SM4NI. The maintainers say the base implementations are not optimized, and one VPP user saw about 200 Mbps (issue #152).

## How it is fast

The main technique is multi-buffer processing. Modes that are serial inside one message (AES-CBC encryption, HMAC-SHA, AES-XCBC/CMAC, ZUC, SNOW3G) are run across independent jobs held in SIMD lanes: x4 with SSE, x8 with AVX2 and x16 with AVX-512, so each packet's dependency chain overlaps with the others. Modes that parallelize within one message (GCM, CTR, CBC decryption) use single-buffer 'by8/by16/by32' kernels with VAES and VPCLMULQDQ. Cipher and hash work is also interleaved ('function stitching'). init_mb_mgr_auto picks the SSE, AVX2, AVX-512 or AVX10 code path at run time, and AES key schedules, HMAC ipad/opad states and GHASH key powers are computed once per session rather than per packet. In Netgate's measurement on an AVX2 host, serial AES-256-CBC+HMAC-SHA-256 ran at 5.4 Gbps and the multi-buffer path at 18 Gbps.

## Compared with alternatives

libaegis, HiAE, Rocca, SNOW-V-GCM and aegis-bitsliced are new AEAD algorithms, and both ends must implement them. Pick intel-ipsec-mb when you have to talk existing wire formats (AES-GCM, AES-CBC+HMAC, ChaCha20-Poly1305 or 3GPP ciphers) to standard IPsec, TLS or 5G peers on x86-64. If you control both endpoints and want raw per-byte AEAD speed, AEGIS or HiAE are faster designs.

## Integration

| | |
|---|---|
| **Form** | shared lib (default) or static lib built with CMake (libIPSec_MB). CPack can produce DEB/RPM packages. The OS packages are installed under /usr/local/lib. |
| **Dependencies** | Build time: NASM and Perl (Perl generates the vendored OpenSSL ML-DSA/Keccak assembly). Run time: only the C library. Optional: Valgrind headers for the constant-time validation build, and libacvp 2.0+ for the ACVP test app. |
| **Minimum toolchain** | CMake 3.16+. C11 (GCC and Clang build with -std=c11; MSVC and MinGW are supported). NASM 2.14+ is required; NASM 2.16 is needed for the AVX-IFMA paths and 2.16.02 for the SM3/SM4/SHA512-NI paths, otherwise those paths are skipped with a warning. |
| **Platforms** | x86-64 only, on Linux, FreeBSD and Windows. Code paths are chosen at run time among SSE types 1-3 (minimum SSE4.2 + AES-NI + PCLMULQDQ), AVX2 types 1-4, AVX-512 types 1-2 and AVX10. This repo has no AArch64 support. |
| **Thread safety** | One IMB_MGR per thread. The header says an IMB_MGR 'is owned by a single thread', and the 2012 white paper says the routines are not thread-safe, so any locking has to live above them. The process-wide fallback of imb_get_errno() is shared between threads. ML-KEM/ML-DSA contexts must not be shared between threads either. |
| **Drop-in for the baseline** | partial — the native job/burst manager API is nothing like OpenSSL EVP. It becomes swappable only through a framework plug-in: DPDK cryptodev PMDs, the FD.io/VPP ipsecmb engine, QAT Engine qat_sw (AES-GCM only, AVX-512+IFMA+VAES required), or a custom engine such as Netgate's FreeBSD OCF replacement. The in-repo OpenSSL 3.x provider is for testing only. |

## Gotchas

- Decryption never verifies the tag. For every AEAD and MAC, the decrypt/verify direction only writes the computed tag, and the caller must compare it in constant time. The library also does not enforce key/IV uniqueness and accepts GCM tags shorter than 96 bits.
- SAFE_DATA, SAFE_PARAM and SAFE_LOOKUP are on by default and cost speed. One user measured about 10% slower AES-CBC/CTR on Broadwell after upgrading from v0.52 (issue #90), and the maintainers suggested turning off SAFE_DATA and SAFE_PARAM. SECURITY.md says no general side-channel protection was added. The optional Valgrind constant-time check covers only the job API.
- The job pointer returned by submit or flush is valid only until the next get_next_job call. Jobs complete in submission order, so one slow lane holds back later jobs until you flush. Expanded keys and auth keys must be 16-byte aligned, and keys, HMAC pads and GHASH powers must be precomputed per session.
- Main is 3.0.0-dev and the README says code from main is not fit for production. The last tagged release is v2.0 (November 2024), and 3.0 removes the wireless and CRC direct APIs, the QUIC API, SNOW-V, ZUC-256 and bit-length support.

## Known shortcomings

- Only outside evidence is Netgate's AsiaBSDCon 2023 paper: 18.1 vs OpenSSL 10.4 Gbps for AES-CBC+HMAC with mismatched block sizes and no CPU model stated. x86-only (Intel/AMD with AES-NI/VAES).
- x86-64 only (Arm64 port declined, #145; a separate Arm fork exists). Job/burst API, not EVP; the in-repo OpenSSL provider is test-only, and QAT qat_sw uses it only for AES-GCM on AVX-512+IFMA CPUs. Decrypt jobs return the tag without checking it (caller must compare). SAFE_\* defaults cost \~10% (#90). Last release v2.0 (Nov 2024); main is 3.0-dev and drops APIs. The only OpenSSL head-to-head is one Netgate sentence with an unnamed CPU and mismatched sizes (1400 B vs 16 kB).

## Caveats and trade-offs

The only OpenSSL head-to-head is one sentence in a downstream user's (Netgate) paper. It covers AES-256-CBC+HMAC-SHA-256, not AES-GCM or ChaCha20-Poly1305, uses mismatched block sizes (1400 B for IPsec-MB vs 16 kB for OpenSSL), and names no CPU model or compiler. The AES-GCM and ChaCha20-Poly1305 gains are measured against FreeBSD's OCF framework, not OpenSSL, in end-to-end VPN throughput, so part of the gain comes from the new engine's job batching and async handling, not only the library's kernels. The paper's ARM (SG-1100) results use ISA-L AES and OpenSSL ChaCha20-Poly1305, not intel-ipsec-mb. Intel's own white paper (2012) and the DPDK 25.11 Intel crypto performance report give absolute throughput only, with no OpenSSL comparison. The vendored ML-DSA/ML-KEM code is Apache-2.0 (LICENSE.OpenSSL); the rest is BSD-3-Clause, and both are OSI-approved.

Job-based multi-buffer API is a different programming model than OpenSSL's EVP interface (best throughput requires batching many buffers together); x86-64/AArch64 specific, hand-written per-ISA assembly; targets IPsec/packet-processing workloads rather than general-purpose drop-in crypto.

## Maintenance

Intel develops it actively (commits up to 2026-09-25) under BSD-3-Clause, plus Apache-2.0 for the vendored OpenSSL PQC code. Ship a tagged release (v2.0 is the last one, from November 2024, and is what DPDK 24.11 uses) rather than main, and expect API removals in 3.0.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification D, tier now C.
- **Tier reason:** Upgraded from D. Netgate's AsiaBSDCon 2023 paper (linked from the project wiki's Links page) gives head-to-head numbers: IPsec-MB 18.1 Gbps vs OpenSSL 10.4 Gbps for AES-256-CBC+HMAC-SHA-256, plus VPN throughput vs FreeBSD's default OCF kernel crypto. The OpenSSL comparison names no CPU model, uses mismatched block sizes, and gives no compiler/flags or benchmark code, and it is not a well-known benchmark suite, so this is C.
- **Verifier notes:** I found a real numbers page via the project wiki's Links page, so I upgraded D to C (verdict confirm). If the orchestrator counts AsiaBSDCon as peer-reviewed it could argue B, but the OpenSSL comparison itself has almost no methodology. I changed usability from 'mixed' to 'copyable' because all code is under OSI licenses (BSD-3-Clause plus Apache-2.0 vendored parts). numbers_found_on_page refers to the corrected claimed_speedup; the original record claimed no numbers.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `baseline`, `workload`, `hardware`, `usability`, `caveats`
- **Shortcomings recorded by:** Netgate AsiaBSDCon 2023: AES-CBC+HMAC 18.1 vs OpenSSL 10.4 Gbps; VPN throughput wins over FreeBSD OCF.
- **Pages the verifier opened:**
  - <https://github.com/intel/intel-ipsec-mb>
  - <https://github.com/intel/intel-ipsec-mb/wiki>
  - <https://raw.githubusercontent.com/wiki/intel/intel-ipsec-mb/Publications.md>
  - <https://raw.githubusercontent.com/wiki/intel/intel-ipsec-mb/Links.md>
  - <https://github.com/intel/intel-ipsec-mb/wiki/doc/fast-multi-buffer-ipsec-implementations-ia-processors-paper.pdf>
  - <https://fast.dpdk.org/doc/perf/>
  - <https://fast.dpdk.org/doc/perf/DPDK_25_11_Intel_crypto_performance_report.pdf>
  - <https://2023.asiabsdcon.org/program/_p05b/paper.pdf>
  - <https://github.com/intel/QAT_Engine>
- **Sources the enricher read:**
  - <https://github.com/intel/intel-ipsec-mb>
  - <https://github.com/intel/intel-ipsec-mb/blob/main/README.md>
  - <https://github.com/intel/intel-ipsec-mb/blob/main/INSTALL.md>
  - <https://github.com/intel/intel-ipsec-mb/blob/main/SECURITY.md>
  - <https://github.com/intel/intel-ipsec-mb/blob/main/ReleaseNotes.md>
  - <https://github.com/intel/intel-ipsec-mb/blob/main/lib/intel-ipsec-mb.h>
  - <https://github.com/intel/intel-ipsec-mb/blob/main/lib/CMakeLists.txt>
  - <https://github.com/intel/intel-ipsec-mb/blob/main/lib/cmake/unix.cmake>
  - <https://github.com/intel/intel-ipsec-mb/blob/main/perf/README.md>
  - <https://github.com/intel/intel-ipsec-mb/blob/main/examples/burst-app/README.md>
  - <https://github.com/intel/intel-ipsec-mb/blob/main/test/imb-provider/README.md>
  - <https://github.com/intel/intel-ipsec-mb/releases>
  - <https://github.com/intel/intel-ipsec-mb/issues/90>
  - <https://github.com/intel/intel-ipsec-mb/issues/99>
  - <https://github.com/intel/intel-ipsec-mb/issues/112>
  - <https://github.com/intel/intel-ipsec-mb/issues/145>
  - <https://github.com/intel/intel-ipsec-mb/issues/152>
  - <https://github.com/intel/intel-ipsec-mb/issues/154>
  - <https://github.com/intel/intel-ipsec-mb/wiki/doc/fast-multi-buffer-ipsec-implementations-ia-processors-paper.pdf>
  - <https://2023.asiabsdcon.org/program/_p05b/paper.pdf>
  - <https://github.com/intel/QAT_Engine>
  - <https://github.com/intel/QAT_Engine/blob/master/docs/qat_sw.md>
  - <https://github.com/intel/QAT_Engine/blob/master/docs/features.md>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/intel/intel-ipsec-mb`) · [data/wave7/enrich/raw/github_com_intel_intel_ipsec_mb.json](../../../data/wave7/enrich/raw/github_com_intel_intel_ipsec_mb.json) (enrichment confidence 0.75)

</details>
