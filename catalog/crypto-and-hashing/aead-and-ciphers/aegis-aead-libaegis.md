# libaegis (AEGIS-128L, AEGIS-128X/256X)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [AEAD and ciphers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🟢 active

> Portable C library for the AEGIS AEAD family (RFC 10032), roughly 3x AES-GCM throughput on AES-NI/VAES CPUs.

| | |
|---|---|
| **Beats** | AES-256-GCM (SUPERCOP aes256gcmv1; on this host the fastest implementation is Romain Dolbeau's VAES code; the OpenSSL wrapper 'opensslnew' is also measured and is slower) |
| **Claimed result** | long+0 encrypt quartiles on hertz: aegis128l 0.18/0.19/0.19 cycles/byte vs aes256gcmv1 0.55/0.56/0.57 cycles/byte, about 2.9-3x faster (derived from page data). 1536+1536 encrypt: aegis128l 0.20-0.21 vs aes256gcmv1 0.55-0.56. The wider AEGIS-128X4 variant (also in libaegis) measures 0.07-0.08 cycles/byte long+0, about 7-8x (derived from page data). |
| **Workload** | eBACS/SUPERCOP AEAD 'long+0 encrypt' benchmark: cycles/byte for long messages with no associated data, computed as 1/1920 of the cycle-count difference between a 2048-byte and a 128-byte message (not 1536-byte messages) |
| **Metric** | throughput |
| **Hardware** | Intel Core i9-13900K (Raptor Lake); AMD EPYC 7543; AMD Ryzen 7 7700 (Zen4, AVX-512+VAES) — single core, 16 KB messages |
| **Compiler and flags** | From the eBACS web-impl pages (SUPERCOP 20260831, hertz). Fastest aegis128l implementation 'aesnib': clang -march=native -O2 -fwrapv -Qunused-arguments -fPIC -fPIE -gdwarf-4 -Wall. Fastest aes256gcmv1 implementation 'dolbeau/vaesenc-int': clang -march=native -Os -fwrapv -Qunused-arguments -fPIC -fPIE -gdwarf-4 -Wall. |
| **Adoption** | 146 stars; AEGIS is now published as RFC 10032 (linked from the libaegis README) and is also shipped inside libsodium |
| **Last commit** | 2026-09-21 |
| **Links** | [repository](https://github.com/aegis-aead/libaegis) · [benchmark](https://eprint.iacr.org/2023/523.pdf) |

## Verdict

On eBACS/SUPERCOP 20260831 (hertz, AMD Ryzen 7 7700 Zen 4, single core, clang -march=native -O2), long-message encryption with no AD costs 0.18/0.19/0.19 cycles/byte for SUPERCOP's aegis128l ('aesnib') vs 0.55/0.56/0.57 for the fastest aes256gcmv1 (Dolbeau's VAES code), about 2.9-3x, and aegis128x4 is about 0.07-0.08. That measures SUPERCOP's own AEGIS code, not libaegis. The author's ePrint 2023/523 (Zig reference code vs OpenSSL 3.1 AES-128-GCM, 16 KB, single core) reports 190 vs 81 Gbps on i9-13900K and 118 vs 37 on EPYC 7543. libaegis's own README chart (Zen 4, turbo off) shows aegis128l at 208 Gb/s vs 47.7 for BoringSSL AES-256-GCM.

## Use it when

- Bulk AEAD on x86-64 with AES-NI, or better VAES/AVX-512 (Zen 4, Ice Lake and later, Raptor Lake), where AES-GCM is the throughput bottleneck: disk/file encryption, backups, storage, high-rate tunnels.
- Medium-to-large messages (KB to MB). eBACS shows about 0.19 cycles/byte for aegis128l vs 0.56 for the best AES-256-GCM on Zen 4, and the X4 variant reaches about 0.07.
- Protocols you control on both ends, or TLS 1.3 stacks that already carry AEGIS suites (picotls, h2o, fizz are listed as users).
- When you want random nonces without GCM's 96-bit limits: 128-bit nonces for AEGIS-128L/X (about 2^48 messages per key per RFC 10032), and 256-bit nonces for AEGIS-256/X with no practical limit.
- Encrypted random-access files or databases: the RAF API gives chunked, authenticated, seekable read/write/truncate with caller-supplied I/O and RNG callbacks and no allocation.

## Skip it when

- When you need interoperability with existing AES-GCM peers, FIPS-validated modules, or standards that mandate GCM. AEGIS is an informational IRTF RFC, not a NIST mode.
- CPUs without AES instructions (many microcontrollers, RISC-V without crypto extensions). The default soft backend is bitsliced and constant-time but slow, and upstream recommends aegis-bitsliced for those targets.
- Picking an X variant blindly. Without VAES, AEGIS-128X2 was 25% slower than AEGIS-128L on an i3-7130U (issue #16), and on Apple M1 the README chart shows AEGIS-128X4 (97.68 Gb/s) below AEGIS-128L (114.61).
- Protocols that need full commitment when attackers control associated data: RFC 10032 says AEGIS is only key-committing in the receiver-binding game and fully committing only if the AD is not attacker-controlled (hash the AD first otherwise).
- Risk-averse deployments: AEGIS has a shorter cryptanalytic record than AES-GCM, and there have been recent memory-safety fixes (e.g. an out-of-bounds read in aegis256_stream() with a NULL nonce, fixed 2026-09).

## How it is fast

AEGIS is built from bare AES round functions (one AESENC per 128-bit state word per update, no key schedule), and AEGIS-128L absorbs 256 bits per update through 8 independent AES rounds that fill the AES pipelines. GCM needs a full 10/14-round AES block cipher plus a separate GHASH carry-less multiply. The X2/X4 modes run 2 or 4 AEGIS-128L/256 lanes side by side so VAES+AVX2 or AVX-512 can do 2-4 AES rounds per instruction. aegis_init() does runtime CPU detection and picks per-variant backends: AES-NI+AVX, VAES+AVX2, AVX-512 (with a narrow-AVX-512 path for AEGIS-256X4 on Zen 4), ARM NEON AES and FEAT_SHA3, POWER Altivec, WASM SIMD128, and a bitsliced constant-time software fallback.

## Compared with alternatives

Pick libaegis over HiAE or Rocca when you want an algorithm with a published RFC 10032, shipping TLS users, and an MIT C library that runs on x86, ARM, POWER and WASM, rather than a research cipher whose best numbers depend on AVX-512 or ARM tuning. Pick it over aegis-bitsliced whenever the target has AES-NI, ARMv8 crypto or VAES. aegis-bitsliced only wins on AES-less hardware.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (zig build or CMake); source-drop also supported by copying src/ |
| **Dependencies** | none (libc only; freestanding on wasm32) |
| **Minimum toolchain** | C99 via CMake 3.10+, or Zig 0.16.0+ for zig build. README says Zig or recent clang with -march=native produces faster code than gcc. MSVC and clang-cl have CI workflows. |
| **Platforms** | x86 and x86-64 (AES-NI+AVX, VAES+AVX2, AVX-512 dispatched at runtime), aarch64 (NEON AES, FEAT_SHA3), POWER with Altivec+crypto, wasm32-freestanding (SIMD128/relaxed SIMD on by default), plus a portable software fallback for anything else |
| **Thread safety** | aegis_init() is documented as not thread-safe (call it once before other use). It sets a global backend pointer per variant. After that, one-shot calls work on caller-owned buffers and states are caller-owned structs. Sharing one state across threads is not documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- Forgetting aegis_init() still works but can be 'much slower': the default backend is chosen at compile time and may be the software path.
- Incremental decryption returns plaintext from state_decrypt_update() before the tag is checked. The header says not to use it until state_decrypt_final() succeeds. The one-shot decrypt zeroes the output on tag failure.
- mac_final()/encrypt_final() consume the state by design (issue #28). Clone the MAC state with \*_mac_state_clone() before finalizing if you need to continue, and never reuse a (key, nonce) pair, even with a different tag length or AD.
- Static linking alongside libsodium 1.0.21 once caused duplicate symbols (issue #30, fixed upstream). -Dfavor-performance / -DFAVOR_PERFORMANCE swaps the constant-time bitsliced soft AES for table lookups on CPUs without AES hardware.

## Known shortcomings

- Independent eBACS numbers measure SUPERCOP's own AEGIS code, not libaegis (so tier B, not A). eBACS's fastest AES-GCM is Dolbeau's VAES code; OpenSSL's wrapper is slower, so ratios against 'OpenSSL AES-GCM' flatter it. eBACS 'long' figure is the 2048-vs-128-byte differential. AEGIS needs AES hardware instructions to be fast.
- X variants lose without VAES: AEGIS-128X2 is 25% slower on an i3-7130U (#16), and on M1 128X4 (97.68 Gb/s) trails 128L (114.61). aegis_init() is not thread-safe; incremental decryption releases plaintext before the tag is checked; NULL-nonce out-of-bounds read fixed only in 2026-09 (#35). Not interoperable with AES-GCM and not FIPS-approved. Paper 2023/523 measured Zig reference code vs OpenSSL 3.1, and the README chart baseline is BoringSSL.

## Caveats and trade-offs

eBACS measures SUPERCOP's own AEGIS implementations, not libaegis. The winning aegis128l code on hertz is 'aesnib' (no author credited); Frank Denis's sodium-aesni (libsodium) scores close behind, and the aegis128x2/x4 code in SUPERCOP is credited to Frank Denis. The aes256gcmv1 row is the best of several AES-GCM implementations. On hertz that is dolbeau/vaesenc-int. The OpenSSL wrapper (opensslnew) is slower in the web-impl selection-time column: about 5764 for opensslnew vs 3258 for dolbeau and 1241 for aegis128l aesnib, so the gap against OpenSSL itself is likely larger than 3x. Compiler and flags ARE disclosed on the per-machine web-impl pages. libaegis's own README chart (img/bench-encryption.png, first-party, 16 KB encryption) does state its CPUs. On AMD Zen 4 with turbo off: aegis128l 208.44 Gb/s vs aes256-gcm (BoringSSL) 47.68 Gb/s. On Apple M1: 114.61 vs 41.6 Gb/s. The chart's baseline is BoringSSL, not OpenSSL, and the libaegis benchmark.zig does not include AES-GCM.

The X2/X4 speedups require VAES/AVX-512 or equivalent wide vector-AES instructions; on CPUs without vector-AES, plain AEGIS-128L/256 is as fast or faster than the X-variants. AEGIS has a shorter cryptanalytic track record than AES-GCM (in active study since 2013).

## Maintenance

Actively maintained (v0.10.6 released 2026-09-21, many 2026 releases, few open issues), MIT-licensed, and easy to vendor by copying src/; pre-1.0 versioning, and the project refuses AI-written contributions.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now B.
- **Tier reason:** eBACS/SUPERCOP is a well-known independent suite. On the hertz page (Ryzen 7 7700) aegis128l runs at 0.18-0.19 cycles/byte and aes256gcmv1 at 0.55-0.57. The public harness and web-impl pages give compiler, flags and CPU, but the measured aegis128l code (the uncredited 'aesnib' implementation) is not shown to be libaegis. The fastest AES-GCM is also Dolbeau's VAES code, not OpenSSL, so this is B, not A.
- **Verifier notes:** The numbers are accurate and belong to the aegis128l and aes256gcmv1 rows. The workload wrongly said 1536-byte messages; 'long' is the 2048-vs-128-byte differential. The record's caveats wrongly said compiler flags were undisclosed and the README charts had no CPU, and both are corrected. Tier would be A for the AEGIS algorithm vs OpenSSL AES-GCM, but the measured code is not shown to be libaegis's.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `baseline`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** eBACS: aegis128l 0.18-0.19 vs aes256gcmv1 0.55-0.57 cycles/byte (\~3x). README (Zen 4): 208 vs BoringSSL AES-GCM 47.7 Gb/s.; eBACS hertz (Ryzen 7 7700): aegis128l 0.18/0.19/0.19 vs aes256gcmv1 0.55/0.56/0.57 cycles/byte.
- **Pages the verifier opened:**
  - <https://bench.cr.yp.to/results-aead/amd64-hertz.html>
  - <https://bench.cr.yp.to/impl-aead/aegis128l.html>
  - <https://bench.cr.yp.to/impl-aead/aes256gcmv1.html>
  - <https://bench.cr.yp.to/impl-aead/aegis128x4.html>
  - <https://bench.cr.yp.to/web-impl/amd64-hertz-crypto_aead-aegis128l.html>
  - <https://bench.cr.yp.to/web-impl/amd64-hertz-crypto_aead-aes256gcmv1.html>
  - <https://github.com/aegis-aead/libaegis>
  - <https://raw.githubusercontent.com/aegis-aead/libaegis/main/img/bench-encryption.png>
  - <https://raw.githubusercontent.com/aegis-aead/libaegis/main/src/test/benchmark.zig>
  - <https://www.rfc-editor.org/rfc/rfc10032.html>
- **Sources the enricher read:**
  - <https://github.com/aegis-aead/libaegis>
  - <https://github.com/aegis-aead/libaegis/blob/main/README.md>
  - <https://github.com/aegis-aead/libaegis/blob/main/src/include/aegis.h>
  - <https://github.com/aegis-aead/libaegis/blob/main/src/include/aegis128l.h>
  - <https://github.com/aegis-aead/libaegis/blob/main/src/aegis128l/aegis128l.c>
  - <https://github.com/aegis-aead/libaegis/blob/main/src/aegis128l/aegis128l_aesni.c>
  - <https://github.com/aegis-aead/libaegis/blob/main/src/aegis128l/aegis128l_common.h>
  - <https://github.com/aegis-aead/libaegis/blob/main/src/aegis128x4/aegis128x4.c>
  - <https://github.com/aegis-aead/libaegis/blob/main/src/common/common.h>
  - <https://github.com/aegis-aead/libaegis/blob/main/src/common/cpu.c>
  - <https://github.com/aegis-aead/libaegis/blob/main/src/common/cpu.h>
  - <https://github.com/aegis-aead/libaegis/blob/main/src/common/softaes.c>
  - <https://github.com/aegis-aead/libaegis/blob/main/src/common/softaes.h>
  - <https://github.com/aegis-aead/libaegis/blob/main/src/test/benchmark.zig>
  - <https://github.com/aegis-aead/libaegis/blob/main/CMakeLists.txt>
  - <https://github.com/aegis-aead/libaegis/blob/main/build.zig>
  - <https://github.com/aegis-aead/libaegis/blob/main/build.zig.zon>
  - <https://github.com/aegis-aead/libaegis/blob/main/AI-POLICY.md>
  - <https://github.com/aegis-aead/libaegis/blob/main/LICENSE>
  - <https://github.com/aegis-aead/libaegis/issues?q=is%3Aissue>
  - <https://github.com/aegis-aead/libaegis/issues/35>
  - <https://github.com/aegis-aead/libaegis/issues/30>
  - <https://github.com/aegis-aead/libaegis/issues/28>
  - <https://github.com/aegis-aead/libaegis/issues/16>
  - <https://github.com/aegis-aead/libaegis/issues/13>
  - <https://github.com/aegis-aead/libaegis/pulls?q=is%3Apr>
  - <https://github.com/aegis-aead/libaegis/releases>
  - <https://github.com/aegis-aead/libaegis/commits/main>
  - <https://raw.githubusercontent.com/aegis-aead/libaegis/main/img/bench-encryption.png>
  - <https://raw.githubusercontent.com/aegis-aead/libaegis/main/img/bench-mobile.png>
  - <https://eprint.iacr.org/2023/523.pdf>
  - <https://eprint.iacr.org/2023/523>
  - <https://bench.cr.yp.to/results-aead/amd64-hertz.html>
  - <https://bench.cr.yp.to/web-impl/amd64-hertz-crypto_aead-aegis128l.html>
  - <https://www.rfc-editor.org/rfc/rfc10032.txt>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/aegis-aead/libaegis`) · [data/wave7/enrich/raw/github_com_aegis_aead_libaegis.json](../../../data/wave7/enrich/raw/github_com_aegis_aead_libaegis.json) (enrichment confidence 0.88)

</details>
