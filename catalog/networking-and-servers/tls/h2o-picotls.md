# picotls "fusion" AES-GCM engine

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [TLS](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> x86-64 AES-GCM engine inside picotls, tuned for short QUIC packets; \~1.3x OpenSSL 1.1.1g throughput at 1440-byte records.

| | |
|---|---|
| **Beats** | OpenSSL |
| **Claimed result** | At 1440-byte AEAD blocks, fusion's throughput is 5.86e9 vs 4.43e9 B/s on Core i5 9400 (1.32x), 4.91e9 vs 3.61e9 on Ryzen 3 3200G (1.36x) and 3.07e9 vs 2.32e9 on Core m3 6Y30 (1.32x). The baseline is OpenSSL 1.1.1g in full-AEAD mode (derived from page data). At 16384-byte blocks the gap shrinks to 1.01-1.15x. The PR text itself says OpenSSL loses \~30% throughput at 1440 bytes compared with 16KB, while fusion cuts that overhead to \~10%. Against OpenSSL's AES-GCM-core-only numbers (no AAD, IV setup or finalization), fusion at 1440 bytes is 1.03-1.14x. |
| **Workload** | AES-GCM AEAD encryption throughput (bytes/s) for QUIC-sized 1440-byte blocks and 16KB blocks, with 13-byte AAD. fusionbench.c uses a 16-byte key, so this is AES-128-GCM; the chart does not label the key size, and AES-256 support was still a to-do in the PR. The chart also shows fusion with QUIC header protection computed in parallel. |
| **Metric** | throughput |
| **Hardware** | Intel Core i5 9400 @4GHz, AMD Ryzen 3 3200G @3.6GHz, Intel Core m3 6Y30 @2.2GHz (chart labels in the PR) |
| **Adoption** | 641 stars; used in the H2O HTTP server |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/h2o/picotls) · [benchmark](https://github.com/h2o/picotls/pull/310) |

## Verdict

In the author's PR #310 chart, fusion (fusionbench.c, AES-128-GCM, 13-byte AAD) beats `openssl speed -aead` from OpenSSL 1.1.1g by 1.32-1.36x at 1440-byte blocks on a Core i5 9400, Ryzen 3 3200G and Core m3 6Y30. At 16 KB the gap is 1.01-1.15x, and on the m3 fusion is slightly behind OpenSSL's AES-GCM core-only figure (3.36e9 vs 3.41e9 B/s). The two sides used different harnesses, and no compiler or flags were given.

## Use it when

- QUIC endpoints on x86-64 with AES-NI, PCLMULQDQ and AVX2 where packets are \~1200-1500 bytes and AES-GCM shows up in profiles; this is where the measured gain is 1.3x or more.
- You already use picotls (H2O, quicly, picoquic) and can swap the AES-GCM cipher suites for the fusion ones after ptls_fusion_is_supported_by_cpu() returns true, as H2O does for its QUIC listeners.
- QUIC stacks that want packet protection and header protection computed in one pass via the supplementary-encryption argument.
- TLS-over-TCP senders doing zero-copy send, especially on CPUs without DDIO or with VAES (Zen 3+), via ptls_non_temporal_aes\*gcm; this is H2O's ssl-zerocopy mode, which turns kTLS off.

## Skip it when

- Bulk TLS with 16 KB records: the gain over OpenSSL 1.1.1g shrinks to 1-15%, the non-temporal engine without VAES measured 84-102% of OpenSSL at 16 KB, and newer OpenSSL, BoringSSL or AWS-LC builds were never compared.
- As the AEAD of any picotls connection where picotls owns the record layer (TLS over TCP, no update_traffic_key callback): ptls_fusion_aes\*gcm leaves do_encrypt_v as an assert(!"FIXME") stub, and picotls calls it for every record. picoquic hit this in its QMux (QUIC over TLS/TCP) mode and turned fusion off.
- Non-x86 targets (aarch64, Apple Silicon): there is no fusion code path, and issue #379 asking for one has been open since 2022.
- Anything beyond AES-GCM: fusion has no ChaCha20-Poly1305, its AES-CTR cipher handles at most 16 bytes (header protection only), and its AES-ECB is encrypt-only.
- Processes that must survive allocation failure: context creation and capacity growth assert on out-of-memory (and dereference NULL when built with NDEBUG).

## How it is fast

It stitches AES-CTR and GHASH into a single loop written in C intrinsics (AES-NI + PCLMULQDQ): six AES blocks are in flight while AAD and ciphertext are multiplied into GHASH, so AAD processing and tag finalization overlap with payload encryption instead of running as separate phases. GHASH key powers are precomputed per context (sized for 1500-byte records, grown on demand), so each record needs only one GHASH reduction. When a record is short and an AES lane would sit idle, that lane computes the QUIC header-protection mask, which is why header protection is nearly free on the chart. The separate non-temporal TLS engine adds a 256-bit VAES/VPCLMULQDQ path and writes ciphertext with streaming stores, so data headed for the NIC does not pollute the cache.

## Compared with alternatives

Pick fusion over AWS-LC, wolfSSL or stock OpenSSL when you are already on picotls/quicly and the hot path is per-packet QUIC AES-GCM on x86-64. Pick AWS-LC, wolfSSL or ztls when you need a complete TLS-over-TCP library, and ChaChaCha when you need ChaCha20-Poly1305.

## Integration

| | |
|---|---|
| **Form** | static lib (picotls-fusion target, built by CMake next to picotls-core; shared-library builds added 2026-09-25) |
| **Dependencies** | picotls-core; a full TLS stack also needs a picotls crypto binding (OpenSSL libcrypto or minicrypto) for key exchange, hashing and certificates |
| **Minimum toolchain** | C99 compiler that accepts -mavx2 -maes -mpclmul -mvaes -mvpclmulqdq and compiles the 256-bit AES intrinsics (the CMake probe CC_HAS_AESNI256 turns WITH_FUSION off otherwise); MSVC via the picotlsvs projects |
| **Platforms** | x86-64 only; at runtime it needs AES-NI, PCLMULQDQ and AVX2 (ptls_fusion_is_supported_by_cpu), and the non-temporal encrypt path uses VAES/VPCLMULQDQ when present |
| **Thread safety** | not documented; each AEAD context is mutable per-connection state, and ptls_fusion_can_aesni256 is a process-wide global set during CPU detection |
| **Drop-in for the baseline** | partial — drop-in only as a picotls cipher-suite AEAD, and the QUIC variant only where do_encrypt_v is never called; there is no EVP/libssl interface, so OpenSSL users must adopt picotls |

## Gotchas

- ptls_fusion_aes128gcm/256gcm are QUIC-only. do_encrypt_v and the streaming init/update/final callbacks are assert(!"FIXME") stubs, and picotls.h says TLS-over-TCP ciphers MUST implement do_encrypt_v. With asserts on, any ptls_aead_encrypt_v call aborts; with NDEBUG it silently writes nothing. The picotls test suite skips multi-vector tests for these two algorithms, and picoquic master defaulted PTLS_WITH_FUSION to OFF on 2026-09-17 (commit 8b8c302).
- Call ptls_fusion_is_supported_by_cpu() first: lib/fusion.c is compiled with AVX2/VAES flags, so an unsupported CPU faults. The Windows CPUID check tests ECX bit 5 (VMX) where PCLMULQDQ is bit 1, and neither path checks OS AVX state through XGETBV.
- The QUIC engine never uses the 256-bit VAES path (the source says 'no support for aesni256 yet'), and non-temporal decryption is always 128-bit; only non-temporal encryption gets the VAES speedup.
- The code reads past buffer ends on purpose (loadn128/256 are marked NO_SANITIZE_ADDRESS), and the non-temporal engine does a read-modify-write of the whole 64-byte line at unaligned output edges, so other threads must not write adjacent bytes during encryption. Valgrind noise from CPU detection (#380) is still open; a 2022 heap over-read in set_capacity (#418) was fixed.

## Known shortcomings

- The fusion AES-128-GCM win is 1.32-1.36x OpenSSL 1.1.1g at 1440-byte blocks but only 1.01-1.15x at 16 KB, against an old OpenSSL. x86-64 AES-NI/AVX2 only. No compiler or flags stated. Bundled crypto includes CC0 code (no patent grant).
- The fusion AES-GCM engine leaves aead_do_encrypt_v and the streaming encrypt callbacks as assert(!"FIXME") stubs (silently writing nothing under NDEBUG), so it is unsafe whenever picotls owns the TLS-over-TCP record layer; picoquic turned PTLS_WITH_FUSION off on 2026-09-17 (8b8c302) after QMux hit it. H2O uses fusion only for QUIC and the separate non-temporal engine for TCP. The lead over OpenSSL shrinks to 1.01-1.15x at 16 KB and fusion is slightly slower on a Core m3; the non-temporal engine was 84-102% of OpenSSL 1.1.1f with 128-bit instructions (1.67-1.90x only with VAES on Zen 3), all against 2020 OpenSSL, with no compiler or flags. The QUIC engine never uses VAES-256. CPU detection bugs: Windows tests the VMX bit instead of PCLMULQDQ, no XGETBV check, leaf-7 accepts VAES or VPCLMULQDQ alone; Valgrind issue #380 open. x86-64 only (#379). Intentional over-reads; unaligned edges read-modify-write whole 64-byte lines. No EVP interface. AES-256 now exists (the record's 'to-do' is outdated).

## Caveats and trade-offs

The PR states no compiler or flags, and the chart gives no cycles/byte. The CPU models are on the chart, contrary to the original record. The baseline is OpenSSL 1.1.1g from 2020, now several major releases old, and OpenSSL was measured with `openssl speed -aead` rather than the same harness as fusion. The win is mainly at short (QUIC-sized) blocks, 1.3x or more; at 16KB it is 1-15%. Fusion is x86-64 only and needs AES-NI, PCLMUL and AVX2. The repo has no top-level LICENSE file. The README says MIT, and lib/fusion.c is under both Apache-2.0 and MIT because its transformH function is derived from OpenSSL. The minicrypto binding pulls in cifra (CC0; no patent grant) and micro-ecc (BSD-2-Clause). The repo's t/ptlsbench.c now benchmarks fusion and OpenSSL AEADs side by side, but no published results with methodology were found.

Fusion is x86-64-specific and written in plain C (not hand assembly) to keep pipelines full for short AEAD blocks; it's one of four interchangeable crypto backends in picotls (OpenSSL, minicrypto, fusion, libaegis), so using it is opt-in and the OpenSSL backend remains the default for portability.

## Maintenance

Active (lib/fusion.c last changed May 2026, repo pushed 2026-09-25) and MIT, with Apache-2.0 also covering one OpenSSL-derived function, but the QUIC AEAD still ships unimplemented callbacks, and picoquic disabled fusion by default because of them.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party PR chart comparing fusion with OpenSSL 1.1.1g, run both with `openssl speed -aead` and without it (AES-GCM core only). CPU models are on the chart. Benchmark code is public (fusionbench.c gist 1ba0bc3a447f5ab7008abdbf9bea9e6b, plus `openssl speed`), but no compiler or flags are given anywhere, so it cannot be A. It is not peer-reviewed or third-party, so it cannot be B.
- **Verifier notes:** Tier C holds. I corrected three things: the record said no CPU model was stated, but the chart names three CPUs; the workload is AES-128-GCM, not AES-256; and usability goes from 'mixed' to 'copyable', since every part is under an OSI or CC0 license (gh reports spdx null only because there is no LICENSE file). Metadata checked with gh: 641 stars, not a fork, not archived, last commit 2026-09-25.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `workload`, `usability`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/h2o/picotls/pull/310>
  - <https://user-images.githubusercontent.com/41567/84847975-3ab46680-b08d-11ea-85a4-7c75adf86147.png>
  - <https://gist.github.com/kazuho/1ba0bc3a447f5ab7008abdbf9bea9e6b>
  - <https://github.com/h2o/picotls>
  - <https://github.com/h2o/picotls/blob/master/README.md>
  - <https://github.com/h2o/picotls/blob/master/lib/fusion.c>
  - <https://github.com/h2o/picotls/blob/master/t/ptlsbench.c>
- **Sources the enricher read:**
  - <https://github.com/h2o/picotls>
  - <https://github.com/h2o/picotls/blob/master/README.md>
  - <https://github.com/h2o/picotls/blob/master/include/picotls/fusion.h>
  - <https://github.com/h2o/picotls/blob/master/lib/fusion.c>
  - <https://github.com/h2o/picotls/blob/master/cmake/fusion.cmake>
  - <https://github.com/h2o/picotls/blob/master/CMakeLists.txt>
  - <https://github.com/h2o/picotls/blob/master/include/picotls.h>
  - <https://github.com/h2o/picotls/blob/master/lib/picotls.c>
  - <https://github.com/h2o/picotls/blob/master/t/fusion.c>
  - <https://github.com/h2o/picotls/blob/master/t/ptlsbench.c>
  - <https://github.com/h2o/picotls/pull/310>
  - <https://user-images.githubusercontent.com/41567/84847975-3ab46680-b08d-11ea-85a4-7c75adf86147.png>
  - <https://github.com/h2o/picotls/pull/384>
  - <https://user-images.githubusercontent.com/41567/167744223-1beb2f0c-cd63-42a2-b804-df005d3acbcb.png>
  - <https://github.com/h2o/picotls/pull/492>
  - <https://github.com/h2o/picotls/pull/602>
  - <https://github.com/h2o/picotls/issues/379>
  - <https://github.com/h2o/picotls/issues/380>
  - <https://github.com/h2o/picotls/issues/418>
  - <https://github.com/h2o/picotls/issues/450>
  - <https://github.com/h2o/picotls/commits/master/lib/fusion.c>
  - <https://github.com/private-octopus/picoquic/commit/8b8c302e9737a53312b41cf644cfe36662e0c6e2>
  - <https://github.com/private-octopus/picoquic/blob/master/picoquic/picoquic_ptls_fusion.c>
  - <https://github.com/private-octopus/picoquic/blob/master/picoquic/qmux.c>
  - <https://github.com/h2o/h2o/blob/master/src/main.c>
  - <https://hn.algolia.com/api/v1/search?query=%22picotls%22>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/h2o/picotls`) · [data/wave5/enrich/raw/github_com_h2o_picotls.json](../../../data/wave5/enrich/raw/github_com_h2o_picotls.json) (enrichment confidence 0.75)

</details>
