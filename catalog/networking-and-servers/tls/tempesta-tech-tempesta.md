# Tempesta FW (Tempesta TLS)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [TLS](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `GPL-2.0` · 🟢 active

> Linux-kernel TLS 1.2 server stack in the Tempesta FW proxy; 6-83% more handshakes/s than Nginx+OpenSSL in vendor tests.

| | |
|---|---|
| **Beats** | OpenSSL |
| **Claimed result** | 40-80% more TLS connections/sec than Nginx/OpenSSL and up to 4x lower latency in some tests; concretely: 1-CPU VM new-session RPS 2,180 vs 1,545 (+41%), avg latency 307ms vs 1,340ms (-77%); 2-CPU bare-metal session-resumption 35,263 vs 19,203 conn/s (+83%); 2-CPU bare-metal new-session RPS only 7,921 vs 7,426 (+6%). Raw crypto op/s were slower than OpenSSL: ECDSA 27,261 vs OpenSSL's 36,472 op/s, ECDHE 6,690 vs OpenSSL's 16,619 op/s -- the throughput win comes from avoiding user/kernel context switches and heap allocation, not from faster math. |
| **Workload** | Server-side full and abbreviated TLS 1.2 handshakes (ECDHE+ECDSA over NIST P-256) measured with the project's own tls-perf tool and wrk, comparing Nginx 1.19.1/OpenSSL 1.1.1d against Tempesta FW's in-Linux-kernel TLS handshake implementation, on a 1-vCPU KVM VM and on 2-node bare-metal servers |
| **Metric** | throughput |
| **Hardware** | 1 vCPU KVM VM on Intel Core i7-6500U host (no vAPIC), virtio_net; 2-node bare-metal cluster with Intel Xeon E3-1240v5 CPUs and Mellanox ConnectX-2 10GbE, Linux kernel 5.7 (also compared to 4.14) |
| **Adoption** | 722 stars |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/tempesta-tech/tempesta) · [benchmark](https://netdevconf.info/0x14/pub/papers/35/0x14-paper35-talk-paper.pdf) |

## Verdict

The authors' NetDev 0x14 (2020) paper ran TLS 1.2 ECDHE-ECDSA P-256 handshakes against Tempesta FW on Linux 5.7 and Nginx 1.19.1 + OpenSSL 1.1.1d, using tls-perf and wrk; on a 1-vCPU KVM guest (i7-6500U host, no vAPIC), Tempesta reached 2,180 vs 1,545 handshakes/s with 307 vs 1,340 ms average latency. On bare-metal Xeon E3-1240v5 limited to one physical core (2 hyperthreads) with 10GbE, it gained 83% on resumption but only 6% on new sessions (7,921 vs 7,426), with worse average, p95 and max latency; compiler and build flags are not given.

## Use it when

- Dedicated x86-64 Linux edge servers where full or resumed TLS handshakes/s is the bottleneck, for example short-lived HTTPS connections or TLS handshake floods (DDoS), and you can replace Nginx/HAProxy with Tempesta FW
- Traffic dominated by session resumption through RFC 5077 session tickets: the paper measured 35,263 vs 19,203 conn/s (+83%) against Nginx/OpenSSL on bare metal
- Small VMs without virtual APIC, where fewer VM exits matter: on a 1-vCPU KVM guest, the paper measured +41% handshakes/s and 77% lower average latency
- ECDSA P-256 certificates with ECDHE P-256 and AES-GCM suites, serving HTTP/1.1 or HTTP/2 (the only ALPN protocols supported)
- Deployments that want private and session keys held in non-swappable kernel memory, away from the application's address space

## Skip it when

- You need TLS 1.3, X25519, ChaCha20-Poly1305, P-384 or client-side TLS: only TLS 1.2 server-side with AES-GCM/CCM on secp256r1 is supported, and TLS 1.3 (issue #1031) is still open
- You need a library to link into your own application or into Nginx/HAProxy: there is no OpenSSL-compatible API, and the kernel TLS socket API (issue #1433) is only a proposal
- Bare-metal services that care about tail latency: in the paper, Nginx/OpenSSL had 50-170% lower average and p95 latency for new sessions, and Tempesta's max latency was up to 30x worse (28,262 vs 925 ms) under load
- Non-x86-64 hardware (ARM/Graviton), CPUs without BMI2/ADX, or managed kernels: the product needs a patched kernel (linux-6.12.12-tfw for 0.9/master, 5.10.35-tfw for 0.8), at least 8 GB RAM, 2 MB huge pages and an RSS-capable NIC
- RSA-certificate workloads (the docs say RSA isn't performance-optimized), or teams that cannot accept a Beta, GPLv2 in-kernel TLS stack that enlarges the kernel TCB

## How it is fast

The handshake runs in SoftIRQ right after the TCP handshake, with a zero-copy state machine on skbs, so there are no user/kernel context switches, socket syscalls or extra copies. Hot paths make no heap allocations: each cipher suite has a precomputed 'MPI profile' that is copied in one shot, and temporary big integers come from per-CPU page pools. P-256 uses hand-written x86-64 BMI2/ADX Montgomery arithmetic (after Gueron-Krasnov) in Jacobian coordinates, with fixed-base comb tables (window 7) for m\*G, RDRAND randomization in place of full constant-time table scans, and the Linux crypto API for AES-GCM/CCM. The paper reports 40x the original mbed TLS port's rate (2,180 vs 51 handshakes/s), but raw ECDSA/ECDHE op/s stay below OpenSSL's, so the gain over Nginx comes from where the code runs, not from faster math.

## Compared with alternatives

AWS-LC and wolfSSL are user-space libraries that link into HAProxy or Nginx, support TLS 1.3 and ARM, and scale across many cores (their benchmarks use a 64-core Graviton4). Pick Tempesta only when you can replace the whole HTTPS proxy on dedicated x86-64 Linux and TLS 1.2 ECDSA-P-256 handshake cost per core is your limit, since its gain comes from kernel placement and its own crypto is slower than OpenSSL's.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Patched Linux kernel (tempesta-tech/linux-6.12.12-tfw for 0.9/master, linux-5.10.35-tfw for release-0.8); Linux crypto API for symmetric ciphers and hashes; build packages listed in the install docs include gcc, g++, libboost-all-dev, libssl-dev, libelf-dev, flex, bison and dwarves |
| **Minimum toolchain** | not documented (no GCC version given); Ubuntu 24.04 is the preferred build and run environment; needs kernel headers and 35-40 GB of disk for the kernel build |
| **Platforms** | x86-64 Linux only; SSE4.2, BMI2 and ADX are required by the Makefile. AVX2 is listed as required in the docs, and the Makefile warns not to use builds without it in production. Needs RDRAND and huge-page support. |
| **Thread safety** | Kernel-internal: handshake steps run in non-preemptible SoftIRQ on per-CPU MPI pools, and each connection's TLS context is guarded by a spinlock (tls-&gt;lock). There is no public user-space API. |
| **Drop-in for the baseline** | no |

## Gotchas

- Side-channel protection mixes constant-time code with non-constant-time code plus RDRAND randomization (as in mbed TLS) rather than OpenSSL's constant-time-everywhere approach. A CRYPTO_CONST_TIME build flag exists. On SRBDS-affected Intel CPUs, the microcode mitigation cuts RDRAND to about 3% of its original speed, and the requirements page says the mitigation is needed in public clouds.
- Curve25519 source (tls/ec_25519.c) is present but marked 'slow and incomplete' and is not in the supported-curve list; secp256r1 is the only ECDHE curve offered.
- Heavy public-key math runs in SoftIRQ with kernel_fpu_begin/end. The paper links this to tail-latency spikes and packet drops under heavy load on bare metal.
- The master branch is a development (unstable) branch. The README says to use release-0.8 for a stable version, and the project calls itself Beta.

## Known shortcomings

- First-party NetDev paper; on bare metal Nginx/OpenSSL had lower average and 95th-percentile latency, and Tempesta showed tail-latency spikes up to +3000%. In-kernel TLS tied to Tempesta FW, not a drop-in library. No compiler or flags stated.
- Not a drop-in for OpenSSL: an out-of-tree kernel module inside the Tempesta FW reverse proxy with no OpenSSL-compatible API. TLS 1.2 server-side only (TLS 1.3 open, #1031), secp256r1 and AES-GCM/CCM only (no ChaCha20). Needs a patched kernel, x86-64 with SSE4.2/BMI2/ADX, 8 GB RAM and huge pages. Mixes constant-time and non-constant-time code with RDRAND randomization. Self-described Beta.

## Caveats and trade-offs

This is a first-party paper/benchmark by the Tempesta Technologies team (NetDev 0x14 conference paper, July 2020), not independent peer review, so it is capped at tier C despite the public benchmark tool (tls-perf) and stated hardware; compiler and build flags are not given. The headline 40-80% figure applies mainly to the 1-vCPU VM and to session resumption; the bare-metal new-session gain was only +6%. On bare metal Nginx/OpenSSL had lower average and 95th-percentile latency (the paper says 50-170% lower for new sessions and 4-9% for resumption), and Tempesta showed large tail-latency spikes (max latency up to +3000%, 28,262 vs 925 ms on resumption). The raw ECDSA/ECDHE op/s were lower than OpenSSL even though Tempesta's figures include ephemeral key generation, so that comparison is not like-for-like. Only x86-64 with AVX/BMI/ADX is supported, and the design relies on RDRAND randomization, which SRBDS microcode mitigations slow. Test hardware and kernel (5.7, 2020) are dated, and the code has changed since.

Linux-kernel-only (x86-64 with AVX/BMI/ADX required, no generic C fallback for the crypto routines), puts TLS handshake code in kernel space (larger attack surface / TCB), GPLv2 licensing, and the paper itself reports tail-latency spikes up to 30x worse in the worst case on bare metal under SoftIRQ load

## Maintenance

Actively developed (last commit 2026-09-25; Ubuntu 24 package release 0.8.2 in October 2025) but still self-described Beta; GPL-2.0 kernel module deployed as a complete reverse proxy, not a TLS library you can vendor into another program.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party NetDev 0x14 (2020) paper by Tempesta Technologies authors. NetDev is a Linux community conference that selects sessions through a call for sessions, not an academic peer-reviewed venue. The paper compares against Nginx 1.19.1/OpenSSL 1.1.1d using public tools (github.com/tempesta-tech/tls-perf, wrk) and names the CPUs (i7-6500U host VM; Xeon E3-1240v5), but compiler, build flags and exact test configs are absent, so it stays at C.
- **Verifier notes:** All numbers in claimed_speedup match the paper's tables (2,180 vs 1,545 RPS, 307 vs 1,340 ms, 35,263 vs 19,203, 7,921 vs 7,426, ECDSA 27,261 vs 36,472, ECDHE 6,690 vs 16,619), as do the hardware and baseline versions. The only correction is caveats, which now include the bare-metal latency and tail-latency regressions. The README cites the same 40-80% / x4 claim; the tempesta-tech.com HTTPS-performance KB page has no newer Tempesta numbers (marked TODO). Metadata checks out (GPL-2.0, 722 stars, last commit 2026-09-25 by committer date, not a GitHub fork, though Tempesta TLS began as a fork of mbed TLS 2.8.0).
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://netdevconf.info/0x14/pub/papers/35/0x14-paper35-talk-paper.pdf>
  - <https://netdevconf.info/0x14/>
  - <https://netdevconf.info/0x14/session.html?talk-performance-study-of-kernel-TLS-handshakes>
  - <https://github.com/tempesta-tech/tempesta>
  - <https://github.com/tempesta-tech/tempesta/blob/master/README.md>
  - <https://github.com/tempesta-tech/tls-perf>
  - <https://tempesta-tech.com/knowledge-base/Performance/>
  - <https://tempesta-tech.com/knowledge-base/HTTPS-performance/>
  - <https://tempesta-tech.com/knowledge-base/Tempesta-TLS/>
- **Sources the enricher read:**
  - <https://github.com/tempesta-tech/tempesta>
  - <https://github.com/tempesta-tech/tempesta/blob/master/README.md>
  - <https://github.com/tempesta-tech/tempesta/blob/master/tls/README.md>
  - <https://github.com/tempesta-tech/tempesta/blob/master/Makefile>
  - <https://github.com/tempesta-tech/tempesta/blob/master/tls/Makefile>
  - <https://github.com/tempesta-tech/tempesta/blob/master/tls/ciphersuites.c>
  - <https://github.com/tempesta-tech/tempesta/blob/master/tls/ttls.h>
  - <https://github.com/tempesta-tech/tempesta/blob/master/tls/mpool.c>
  - <https://github.com/tempesta-tech/tempesta/blob/master/tls/ec_p256.c>
  - <https://github.com/tempesta-tech/tempesta/blob/master/tls/ec_25519.c>
  - <https://github.com/tempesta-tech/tempesta/blob/master/tls/ecp.c>
  - <https://github.com/tempesta-tech/tempesta/blob/master/tls/tls_srv.c>
  - <https://github.com/tempesta-tech/tempesta/blob/master/fw/tls.c>
  - <https://github.com/tempesta-tech/tempesta/releases>
  - <https://github.com/tempesta-tech/tempesta/issues?q=TLS+1.3>
  - <https://github.com/tempesta-tech/tempesta/issues/1031>
  - <https://github.com/tempesta-tech/tempesta/issues/1335>
  - <https://github.com/tempesta-tech/tempesta/issues/1433>
  - <https://github.com/orgs/tempesta-tech/repositories>
  - <https://github.com/tempesta-tech/linux-tls>
  - <https://github.com/tempesta-tech/linux-6.12.12-tfw>
  - <https://netdevconf.info/0x14/pub/papers/35/0x14-paper35-talk-paper.pdf>
  - <https://tempesta-tech.com/knowledge-base/Requirements/>
  - <https://tempesta-tech.com/knowledge-base/Tempesta-TLS/>
  - <https://tempesta-tech.com/knowledge-base/Install-from-Sources/>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/tempesta-tech/tempesta`) · [data/wave5/enrich/raw/github_com_tempesta_tech_tempesta.json](../../../data/wave5/enrich/raw/github_com_tempesta_tech_tempesta.json) (enrichment confidence 0.8)

</details>
