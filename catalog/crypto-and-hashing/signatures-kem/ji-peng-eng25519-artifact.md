# ENG25519 (Curve25519_AVX512IFMA)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Signatures and key exchange](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `LGPL-3.0` · 🟡 stale

> AVX-512IFMA X25519/Ed25519 code plus an OpenSSL 1.1.1 ENGINE; beats OpenSSL's x86-64 Curve25519 code 3.3-12x on throughput.

| | |
|---|---|
| **Beats** | OpenSSL 1.1.1 X25519 (x86-64 assembly, crypto/ec/asm/x25519-x86_64.pl) and Ed25519 (C implementation, crypto/ec/curve25519.c), extracted from OpenSSL_1_1_1-stable and compiled into the paper's benchmark harness; the TLS-level experiments use OpenSSL 1.1.1q |
| **Claimed result** | X25519-KeyGen 12.01x, Ed25519-Sign 3.79x, Ed25519-Verify 3.33x, fixed-point scalar multiplication 8.06x higher throughput than OpenSSL (paper Tables 2-4) |
| **Workload** | Warm-start CPU-cycle cost (2,000 warm-up runs, average of 20,000 runs) of X25519-KeyGen, Ed25519-Sign/Verify and fixed-point scalar multiplication on an Intel Xeon Ice Lake server. Only X25519-KeyGen is batched (8x1-way: eight keypairs per call). Ed25519-Sign (1x8-way) and Ed25519-Verify (1x2-way) run one operation per call and use AVX-512IFMA lanes internally. OpenSSL runs one operation at a time on scalar x86-64 code |
| **Metric** | throughput |
| **Hardware** | Intel Xeon (Ice Lake) Platinum 8369B, 8 vCPUs, Alibaba Cloud ecs.c7.2xlarge (Turbo Boost left enabled) |
| **Compiler and flags** | GCC 9.2.0, -O2 (artifact CMake Release flags: -mavx512ifma -O2 -funroll-loops -m64 -march=native -mtune=native -fomit-frame-pointer -fwrapv); OpenSSL code extracted and built with the same options |
| **Adoption** | 14 stars; USENIX Security 2024 paper artifact |
| **Last commit** | 2024-06-12 |
| **Links** | [repository](https://github.com/Ji-Peng/eng25519_artifact) · [benchmark](https://ji-peng.com/uploads/usenix_security2024/paper.pdf) |

## Verdict

Warm-start cycle counts were measured with GCC 9.2.0 -O2 on an Alibaba Cloud Xeon Platinum 8369B (Ice Lake, Turbo on), against OpenSSL 1.1.1's X25519 assembly and Ed25519 C code extracted into the same harness. The results: batched X25519-KeyGen 60,479 cycles per 8 keys vs 90,809 per key (12.01x throughput); Ed25519 sign 24,723 vs 93,606 cycles (3.79x) and verify 81,506 vs 271,445 (3.33x); fixed-base scalar multiplication 8.06x. Against Faz-Hernandez's AVX2 code the margins shrink to 1.18x for sign and 1.33x for verify, and end-to-end TLS 1.3 handshakes improved only 25%.

## Use it when

- TLS 1.3 servers whose throughput is limited by handshakes, running OpenSSL 1.1.1 on Intel Xeons with AVX-512IFMA (Ice Lake or newer) and using X25519 key exchange with Ed25519 certificates. The paper measured 25% more handshakes per second than stock X25519 (1,707 vs 1,366) and 24-41% higher DoT peak throughput.
- Bulk generation of ephemeral X25519 keypairs, where eight keypairs per call fits naturally (key pools, precomputed keypairs for session setup).
- Services that sign a lot of Ed25519 on AVX-512IFMA servers: about 24.7k cycles per signature, versus 93.6k for OpenSSL 1.1.1's C code.
- A reference design for AVX-512IFMA Curve25519 arithmetic, with CryptoLine-verified field routines, or for handling the cold start of AVX-512 units in latency-sensitive code.

## Skip it when

- CPUs without AVX-512IFMA, which includes AVX2-only parts, Cascade Lake and Cooper Lake Xeons (per the paper) and ARM. There is no fallback path, and the build uses -march=native.
- OpenSSL 3.x or 4.x stacks. The ENGINE API was deprecated in OpenSSL 3.0, and OpenSSL 4.0.0 (April 2026) removed engine support, so ENG25519 would have to be ported to the provider API.
- Workloads dominated by X25519 shared-secret derivation. The authors did not beat prior work there: the ENGINE's derive is Hisil et al.'s code at 61,867 cycles, only 1.47x OpenSSL 1.1.1.
- Clients or lightly loaded servers. Cold AVX-512 units made the primitives 1.6-3.8x slower in the paper's DoT test, and the fix is a helper thread that keeps the vector unit awake.
- Production code that needs maintained, audited crypto. This is a research artifact, stale since June 2024, with no releases. Only the field arithmetic is formally verified, and the authors never benchmarked it against Intel's own AVX-512IFMA multi-buffer crypto_mb Curve25519 code (issue #1).

## How it is fast

Field elements mod 2^255-19 are stored in radix 2^51 (five limbs) to fit the 52-bit vpmadd52luq/vpmadd52huq multiply-add instructions, and field arithmetic runs 8x1-way: eight independent field elements across the eight 64-bit lanes of a zmm register. The paper's 'maximize transferable parallelism' idea carries that 8-way parallelism up the stack. KeyGen runs eight independent fixed-base scalar multiplications per call (8x1 -&gt; 8x1 -&gt; 8x1), Sign spreads one table-based fixed-base scalar multiplication over 8 lanes (8x1 -&gt; 8x1 -&gt; 1x8), and Verify uses a 2x4-way window-based double-point scalar multiplication (8x1 -&gt; 2x4 -&gt; 1x2, window width 5). The ENGINE's X25519-Derive is not the authors' code but a wrapper around Hisil et al.'s AVX-512F 4-way Montgomery ladder.

## Compared with alternatives

Pick it when you specifically need faster X25519/Ed25519 for TLS 1.3 on AVX-512IFMA servers. UltrafastSecp256k1 targets secp256k1 ECDSA (Bitcoin-style signing), fasthqc/hqc is a post-quantum code-based KEM, and VecFalcon (same first author) speeds up Falcon post-quantum signing, so none of them substitutes for Curve25519.

## Integration

| | |
|---|---|
| **Form** | shared lib (OpenSSL 1.1.1 ENGINE loaded via openssl.cnf); the raw primitives are a source-drop with no library target (their CMake builds only a benchmark executable) |
| **Dependencies** | OpenSSL 1.1.1 (1.1.1q recommended; needed for SHA-512 and the ENGINE API), CMake 3.10+; the DoT experiments also use unbound |
| **Minimum toolchain** | GCC 9.2.0 tested (C with inline AVX-512IFMA intrinsics plus GNU assembler files), built with -O2 -mavx512ifma -march=native |
| **Platforms** | x86-64 Linux with AVX-512IFMA required (Intel Cannon Lake/Ice Lake or later, not Cascade/Cooper Lake); tested on Ubuntu (20.04 recommended for the DoT experiments) |
| **Thread safety** | The ENGINE's keypair pool is protected by OpenSSL CRYPTO_RWLOCKs (one global lock and one per store). Thread safety of the raw primitives is not documented. One error path in batch.c (BATCH_CTX_new failing) returns while still holding the global lock. |
| **Drop-in for the baseline** | partial — transparent for OpenSSL 1.1.1 applications once openssl.cnf loads the eng25519 ENGINE (X25519 and Ed25519 EVP_PKEY methods), but not usable with OpenSSL 3.x providers or OpenSSL 4.0, and the raw primitives have a different, batch-oriented API |

## Gotchas

- X25519 keygen through the ENGINE does not compute a fresh key per call. It hands out keys from a pool held in OpenSSL secure heap: 128 X25519 keypairs refilled by 16 batch calls, and 8 for Ed25519. Each refill stalls roughly 0.22-0.33 ms, according to the paper.
- The ENGINE's X25519 derive never checks for an all-zero shared secret; its provider returns success unconditionally. The OpenSSL X25519() it replaces returns failure on an all-zero output.
- The published speedups are warm-start numbers (2,000 warm-up runs). Cold-start cost in real TLS traffic is 1.6-3.8x higher unless you run the authors' timer_warmup or heuristic_warmup helper pinned to the sibling hyperthread, which also works against the CPU's power saving.
- After the ENGINE's reference count drops to zero, the global lock is freed and never recreated, because the init is guarded by run_once. Re-initializing the ENGINE in the same process therefore fails.

## Known shortcomings

- Only X25519 key generation is 8-way batched; Ed25519 Sign (1x8) and Verify (1x2) are single-operation paths, and the Ed25519 baseline is OpenSSL's C code.
- Needs AVX-512 IFMA (built with -march=native, no fallback); speedups are warm-start, cold runs are 1.6-3.8x slower without a warm-up thread. Built as an OpenSSL 1.1.1 ENGINE: the ENGINE API was deprecated in 3.0 and removed in 4.0.0 (Apr 2026). X25519 derive is Hisil et al.'s code (only 1.47x) and lacks the all-zero shared-secret check OpenSSL does. Against Faz-H AVX2 it is only 1.18x sign / 1.33x verify; never compared with Intel crypto_mb (#1). Stale since 2024-06.

## Caveats and trade-offs

The 12.01x X25519-KeyGen ratio compares an 8-keypair batched call (60,479 cycles per 8 keys) with OpenSSL generating one keypair per call, so it measures throughput rather than single-operation latency. The Ed25519 ratios (3.79x and 3.33x) are per operation. The OpenSSL baseline is OpenSSL 1.1.1 code extracted and recompiled inside the authors' harness, not a stock or current OpenSSL build. Turbo Boost was left enabled (the authors argue it causes no significant jitter). The code needs an AVX-512IFMA CPU. End-to-end, the paper reports 25% and 35% more TLS 1.3 handshakes per second than the stock OpenSSL X25519 and P-256 configurations (1,707 vs 1,366 and 1,260 connections per second), far below the micro-benchmark ratios.

Speedups are for N-way batched operations (8x/2x parallel instances) vs OpenSSL's 1-way scalar calls, not single-call latency; requires AVX-512IFMA hardware (Ice Lake or newer); deployed via a custom OpenSSL ENGINE, not a drop-in library

## Maintenance

Stale research artifact (last commit June 2024, no releases, one open issue). It is LGPL-3.0, and the primitives are small enough to vendor, but the ENGINE is tied to an API that OpenSSL deprecated in 3.0 and removed in 4.0.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** USENIX Security 2024 paper Tables 2-4 compare directly against OpenSSL 1.1.1 X25519/Ed25519 with GCC 9.2.0, -O2 and Xeon Platinum 8369B stated; the benchmark code (Crypto/Curve25519_AVX512IFMA/test.c, with OpenSSL's x86-64 asm and C code vendored in src/openssl_curve25519.\*) is public in the artifact repo, so tier A stands.
- **Verifier notes:** All claimed ratios appear exactly in the paper: 12.01 (Table 2), 3.79 and 3.33 (Table 3), 8.06 (Table 4). The only fix needed was the workload: the record said Ed25519-Sign was 8-way batched, but it is a 1x8-way single-signature implementation. Metadata checks out: LGPL-3.0, 14 stars, last commit 2024-06-12 (stale), not archived, not a fork.
- **Fields the verifier corrected:** `baseline`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://ji-peng.com/uploads/usenix_security2024/paper.pdf>
  - <https://github.com/Ji-Peng/eng25519_artifact>
  - <https://raw.githubusercontent.com/Ji-Peng/eng25519_artifact/main/Crypto/Curve25519_AVX512IFMA/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Ji-Peng/eng25519_artifact/main/Crypto/Curve25519_AVX512IFMA/test.c>
- **Sources the enricher read:**
  - <https://github.com/Ji-Peng/eng25519_artifact>
  - <https://github.com/Ji-Peng/eng25519_artifact/blob/main/README.md>
  - <https://github.com/Ji-Peng/eng25519_artifact/blob/main/Crypto/Curve25519_AVX512IFMA/README.md>
  - <https://github.com/Ji-Peng/eng25519_artifact/blob/main/Crypto/Curve25519_AVX512IFMA/CMakeLists.txt>
  - <https://github.com/Ji-Peng/eng25519_artifact/blob/main/Crypto/Curve25519_AVX512IFMA/inc/curve25519.h>
  - <https://github.com/Ji-Peng/eng25519_artifact/blob/main/Crypto/Curve25519_AVX512IFMA/inc/intrin.h>
  - <https://github.com/Ji-Peng/eng25519_artifact/blob/main/Crypto/Curve25519_AVX512IFMA/inc/gfparith_8w.h>
  - <https://github.com/Ji-Peng/eng25519_artifact/blob/main/Crypto/Curve25519_AVX512IFMA/test.c>
  - <https://github.com/Ji-Peng/eng25519_artifact/blob/main/Crypto/Curve25519_AVX512IFMA/src/openssl_curve25519.c>
  - <https://github.com/Ji-Peng/eng25519_artifact/blob/main/ENG25519/eng25519/README.md>
  - <https://github.com/Ji-Peng/eng25519_artifact/blob/main/ENG25519/eng25519/CMakeLists.txt>
  - <https://github.com/Ji-Peng/eng25519_artifact/blob/main/ENG25519/eng25519/eng25519.c>
  - <https://github.com/Ji-Peng/eng25519_artifact/blob/main/ENG25519/eng25519/test/eng25519.cnf>
  - <https://github.com/Ji-Peng/eng25519_artifact/blob/main/ENG25519/eng25519/meths/eng25519_x25519_meth.c>
  - <https://github.com/Ji-Peng/eng25519_artifact/blob/main/ENG25519/eng25519/providers/api/curve25519.h>
  - <https://github.com/Ji-Peng/eng25519_artifact/blob/main/ENG25519/eng25519/providers/batch_fast_lib/batch.c>
  - <https://github.com/Ji-Peng/eng25519_artifact/blob/main/ENG25519/eng25519/providers/batch_fast_lib/batch.h>
  - <https://github.com/Ji-Peng/eng25519_artifact/blob/main/ENG25519/eng25519/providers/batch_fast_lib/curve25519.c>
  - <https://github.com/Ji-Peng/eng25519_artifact/blob/main/ENG25519/eng25519/providers/batch_fast_lib/CMakeLists.txt>
  - <https://github.com/Ji-Peng/eng25519_artifact/blob/main/ENG25519/eng25519/providers/batch_fast_lib/ed25519_fast_avx512ifma/ed255.h>
  - <https://github.com/Ji-Peng/eng25519_artifact/blob/main/ENG25519/eng25519/providers/batch_fast_lib/ed25519_fast_avx512ifma/ed255.c>
  - <https://github.com/Ji-Peng/eng25519_artifact/blob/main/ENG25519/eng25519/providers/batch_fast_lib/x25519_fast_avx512f/montgomery.c>
  - <https://github.com/Ji-Peng/eng25519_artifact/blob/main/Verify/README.md>
  - <https://github.com/Ji-Peng/eng25519_artifact/issues/1>
  - <https://ji-peng.com/uploads/usenix_security2024/paper.pdf>
  - <https://raw.githubusercontent.com/openssl/openssl/openssl-3.0/README-ENGINES.md>
  - <https://raw.githubusercontent.com/openssl/openssl/master/NEWS.md>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/ji-peng/eng25519_artifact`) · [data/wave7/enrich/raw/github_com_ji_peng_eng25519_artifact.json](../../../data/wave7/enrich/raw/github_com_ji_peng_eng25519_artifact.json) (enrichment confidence 0.85)

</details>
