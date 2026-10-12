# OpenSSLNTRU (libsntrup761 + engntru OpenSSL ENGINE)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [TLS](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `C` · `no license` · 🔴 abandoned

> Batched sntrup761/857 post-quantum key exchange for OpenSSL 1.1.1 TLS 1.3; more LAN handshakes/sec than OpenSSL's asm X25519/P-256.

| | |
|---|---|
| **Beats** | OpenSSL TLS 1.3 key exchange (ASM-optimized X25519 and P-256) |
| **Claimed result** | USENIX Security '22 paper, Section 4.4 and Figure 5: over 100 samples of 8192 sequential TLS 1.3 handshakes each, sntrup761 and sntrup857 'consistently achieve more connections per second' than OpenSSL 1.1.1k's ASM-optimized X25519 and P-256. The results are shown only as CDF curves on a 440-620 connections/sec axis, with no tabulated numbers. Key generation: sntrup761 batch keygen (batch size 32) costs 156317 amortized Haswell cycles per key, versus 814608 for the previous best sntrup761 software and 269191 for CECPQ2's ntruhrss701 (\~1.72x versus ntruhrss701, derived from page data). The ntruhrss701 comparison is against the CECPQ2 KEM, not against OpenSSL. |
| **Workload** | Custom \~300-line tls_timer client performs 8,192 sequential TLS 1.3 handshakes between an Intel Core i7-6700 client and an AMD Ryzen 7 2700X server over Gigabit Ethernet, measuring average connections/sec; separately, cycle-counted key generation on a Haswell CPU. |
| **Metric** | throughput |
| **Hardware** | Client: Intel Core i7-6700; Server: AMD Ryzen 7 2700X; key-generation cycle counts measured on Haswell |
| **Last commit** | 2021-12-14 |
| **Links** | [repository](https://opensslntru.cr.yp.to) · [benchmark](https://opensslntru.cr.yp.to/opensslntru-20211006.pdf) |

## Verdict

In the USENIX Security '22 paper (Section 4.4, Figure 5), tls_timer ran 100 samples of 8,192 sequential full TLS 1.3 handshakes (RSA-2048 certificate) from an i7-6700 client to a stunnel server on a Ryzen 7 2700X over a Gigabit LAN with Turbo off. The sntrup761 and sntrup857 CDFs sit above OpenSSL 1.1.1k's asm X25519 and P-256 on a 440-620 conn/s axis with no tabulated numbers (the demo page's example run gives about 522 vs 462 vs 449 conn/s), and the paper states no compiler, while the build scripts use gcc/clang -O3 -march=haswell or native; keygen is 156,317 amortized cycles per key at batch size 32 on a Haswell Xeon E3-1275 v3, vs 819,332 unbatched in the same library and 269,191 for CECPQ2's ntruhrss701.

## Use it when

- Reproducing or extending post-quantum TLS 1.3 handshake measurements on an OpenSSL 1.1.1 stack. The USENIX Security '22 artifact earned the Available, Functional and Reproduced badges, and tls_timer is included.
- Lab or internal testbeds where you control both endpoints and want sntrup761/857 key exchange in unmodified, dynamically linked OpenSSL apps (stunnel, nginx, Apache httpd, GNOME Web).
- Workloads dominated by many fresh full handshakes from long-lived processes on x86-64 Linux with AVX2, where ephemeral keygen CPU is the cost you care about.
- As reference code for batch sntrup761 key generation to port into another library. libntruprime lists this batch-inversion work as faster than its own code and not yet included.

## Skip it when

- Production TLS. OpenSSL 1.1.1 reached end of life on 2023-09-11, the ENGINE API was deprecated in OpenSSL 3.0 and removed in 4.0, and OpenSSL 3.5+ already offers the standardized X25519MLKEM768 hybrid by default.
- Talking to anything that isn't another OpenSSLNTRU peer. The codepoints are private-use (0xFE00/0xFE01), key exchange is PQ-only with no ECC hybrid, and authentication stays classical (RSA/ECDSA certificates).
- Bandwidth-bound or high-latency links. Each handshake carries 2,197 bytes of key plus ciphertext, and the authors warn that their unloaded Gigabit LAN hides this, so sntrup should not be read as cheaper than ECC overall.
- Pre-fork servers or other processes that fork after the key pool has been filled (README caveat: key reuse), statically linked applications, and non-AVX2, non-Linux or OpenSSL 3.x setups (not supported or not documented).
- When you need clear licensing: the speed-critical libsntrup761 tarball has no license file or statement.

## How it is fast

Key generation is batched: for 32 keys, Montgomery's batch-inversion trick replaces 32 inversions in R/3 and in R/q with one inversion plus 3n-3 multiplications each, which brings amortized sntrup761 keygen from about 819k to 156k Haswell cycles. Batching needs big×big multiplication in (Z/4591)[x], so the authors use Schönhage's and Nussbaumer's tricks to get radix-2 NTTs over an NTT-unfriendly modulus, run on AVX2 16-bit lanes after 16x16 transposes; the R/3 side uses Karatsuba, a 5-way split with vpshufb reductions, and a Barrett-based invertibility check. engntru keeps batching invisible to TLS: each parameter set has a lock-protected per-process pool of 32 precomputed keypairs that is refilled when it runs empty.

## Compared with alternatives

The siblings (EverCrypt and Mehdi Sotoodeh's curve25519, AWS-LC, wolfSSL, Tempesta TLS) speed up classical ECC or whole TLS stacks. OpenSSLNTRU is the only catalogued entry that adds post-quantum key exchange, so pick it only to study what batched sntrup KEM handshakes cost on OpenSSL 1.1.1, not to make classical handshakes faster.

## Integration

| | |
|---|---|
| **Form** | shared lib: libsntrup761batch.so plus the dynamically loaded engntru ENGINE .so, on top of an OpenSSL 1.1.1 you rebuild from patched source |
| **Dependencies** | OpenSSL 1.1.1f-1.1.1m patched with openssl-1.1.1x-ntru.patch (libsntrup761 also links libcrypto for SHA-512); libsntrup857 for sntrup857; CMake 3.10+, pkg-config and Python 3 for the build scripts |
| **Minimum toolchain** | GCC or Clang building with -O3 and -march=haswell or -march=native (AVX2); exact compiler versions not documented (demo tested on Debian 10/11) |
| **Platforms** | x86-64 Linux with an AVX2 CPU is the only documented and tested setup (the optimized crypto_kem/sntrup761/avx code is tagged amd64/x86); other OSes and architectures are not documented |
| **Thread safety** | engntru's batch_lib key pools are guarded by OpenSSL CRYPTO_RWLOCKs, so it is thread-safe within a process. It is not fork-safe: a pool inherited across fork() can reuse keys. libsntrup761 functions are stateless; their thread safety is not documented. |
| **Drop-in for the baseline** | partial: it keeps OpenSSL 1.1.1 API/ABI compatibility, so dynamically linked apps need no code changes, but you must rebuild OpenSSL from patched 1.1.1f-m source, load the ENGINE via config, and both peers must run OpenSSLNTRU to negotiate the private groups |

## Gotchas

- The README warns that if a process loads engntru, fills a batch and then forks without erasing the heap, keys can be reused. There is no pthread_atfork handling.
- The request that finds the pool empty pays for the whole 32-key batch synchronously. That is about 5.0M Haswell cycles, which the paper puts at about 2.5 ms on a 2 GHz Haswell, with roughly a 143 KB footprint per batch. The async_batch_lib build option moves the refill onto a filler thread.
- The patch appends sntrup761/sntrup857 to OpenSSL's default supported_groups list. To actually send a PQ key share you still set Groups (for example SNTRUP761:SNTRUP857:X25519:P-256), and debug builds of engntru log per operation (ENGNTRU_DEBUG), which skews timing.
- In libsntrup761's batch keygen, the malloc of the scratch buffer holding secret polynomials is unchecked, and the buffer is freed without being zeroed. engntru does OPENSSL_cleanse each keypair it takes out of its pool.

## Known shortcomings

- The headline handshake comparison is CDF plots only; the only numbers are the demo page's example run (sntrup761 \~522 conn/s vs X25519 \~462, P-256 \~449), and the authors say the unloaded LAN hides the 2,197 extra bytes per handshake, so sntrup should not be read as cheaper than ECC overall. No compiler stated in the paper (build scripts use -O3 -march=haswell/native). Dead platform: patches cover OpenSSL 1.1.1f-1.1.1m (EOL 2023-09); ENGINE deprecated in 3.0 and removed in 4.0; OpenSSL 3.5+ ships X25519MLKEM768 instead. Private codepoints, post-quantum only (no ECC hybrid), dynamically linked apps only. A process that forks after filling the key pool can reuse keys (no atfork handling). The handshake that empties the pool pays the whole 32-key refill (\~2.5 ms on 2 GHz Haswell) unless async_batch_lib is used. Batch keygen doesn't check malloc and frees secret polynomials without zeroing. Mixed licences; libsntrup761 has none. The maintained successor libntruprime (public domain, in Debian/Ubuntu) lacks the batch speedup (949,559 vs 156,317 amortized cycles). x86-64 Linux with AVX2 only.

## Caveats and trade-offs

The paper was published at USENIX Security 2022 (confirmed on the usenix.org presentation page, with Available, Functional and Reproduced artifact badges). The headline 'more handshakes/sec' result is shown only as a CDF plot, not a tabulated number. The authors warn that 'one should not conclude that sntrup761 and sntrup857 cost less than ECC overall', because the unloaded Gigabit LAN hides the larger lattice communication costs. The 156317-cycle figure is the amortized cost of batch key generation (batch of 32); unbatched sntrup761 keygen is 819332 cycles (Table 3). Licensing is mixed: engntru is LGPL-3.0-or-later (COPYING and COPYING.LESSER), tls_timer is Apache-2.0 (LICENSE), and the speed-critical libsntrup761 tarball has no license file or statement (only build and test harness files say 'Public domain'). The OpenSSL patches modify OpenSSL 1.1.1 code. The demo page was last updated 2021.12.14 (OpenSSL 1.1.1m patch); the library tarballs are dated 2021-06-08.

Requires patching OpenSSL (1.1.1f-1.1.1m only, not tested against 3.x); post-quantum-only KEM, not a general TLS library; experimental/demo-quality integration; no formal security audit of engntru/libsntrup761.

## Maintenance

This is an abandoned research artifact (tarballs dated 2021-06-08, last patch for OpenSSL 1.1.1m in Dec 2021) that depends on an OpenSSL line that reached end of life in 2023 and an ENGINE API that OpenSSL 4.0 removed; with mixed licensing (engntru LGPL-3.0+, tls_timer Apache-2.0, libsntrup761 without a license statement) it is only usable as reference code, and maintained sntrup761 now lives in the public-domain libntruprime, which does not include the batch keygen.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** The paper appeared at USENIX Security '22 (peer-reviewed; artifact badges Available, Functional and Reproduced). Its Section 4.4 and Figure 5 show sntrup761 and sntrup857 completing more TLS 1.3 connections/sec than OpenSSL 1.1.1k's ASM-optimized X25519 and P-256, with tls_timer code public and CPUs named. Compiler and flags are not stated, so not A. This upgrades the record from C to B.
- **Verifier notes:** The given demo.html only carries the 156317-cycle keygen figure. The X25519/P-256 handshake comparison is in the paper, and the 269191 ntruhrss701 figure is on the intro page and in paper Table 1, so I repointed benchmark_url to the paper PDF. The venue is confirmed as USENIX Security '22, which moves the tier from C to B. The record's claim that no license exists in the tarballs is wrong for engntru (LGPL-3.0+) and tls_timer (Apache-2.0). I kept usability 'reference' because the core libsntrup761 is unlicensed, and set status to abandoned because the last update was more than 3 years ago and the authors do not say the work is complete.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `last_commit`, `maintenance_status`, `caveats`
- **Pages the verifier opened:**
  - <https://opensslntru.cr.yp.to/demo.html>
  - <https://opensslntru.cr.yp.to/>
  - <https://opensslntru.cr.yp.to/papers.html>
  - <https://opensslntru.cr.yp.to/opensslntru-20211006.pdf>
  - <https://www.usenix.org/conference/usenixsecurity22/presentation/bernstein>
  - <https://opensslntru.cr.yp.to/libsntrup761-20210608.tar.gz>
  - <https://opensslntru.cr.yp.to/engntru-20210608.tar.gz>
  - <https://opensslntru.cr.yp.to/tls_timer-20210608.tar.gz>
- **Sources the enricher read:**
  - <https://opensslntru.cr.yp.to/>
  - <https://opensslntru.cr.yp.to/demo.html>
  - <https://opensslntru.cr.yp.to/papers.html>
  - <https://opensslntru.cr.yp.to/opensslntru-20211006.pdf>
  - <https://opensslntru.cr.yp.to/libsntrup761-20210608.tar.gz>
  - <https://opensslntru.cr.yp.to/engntru-20210608.tar.gz>
  - <https://opensslntru.cr.yp.to/tls_timer-20210608.tar.gz>
  - <https://opensslntru.cr.yp.to/openssl-1.1.1m-ntru.patch>
  - <https://www.usenix.org/conference/usenixsecurity22/presentation/bernstein>
  - <https://libntruprime.cr.yp.to/>
  - <https://libntruprime.cr.yp.to/speed.html>
  - <https://libntruprime.cr.yp.to/license.html>
  - <https://libntruprime.cr.yp.to/internals.html>
  - <https://raw.githubusercontent.com/openssl/openssl/master/NEWS.md>
  - <https://openssl-library.org/post/2023-09-11-eol-111/>
  - <https://hn.algolia.com/api/v1/search?query=OpenSSLNTRU&tags=story>
  - <https://hn.algolia.com/api/v1/search?query=opensslntru.cr.yp.to>
  - <https://hn.algolia.com/api/v1/search?query=sntrup761%20batch%20TLS>
  - <https://test761.cr.yp.to/>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://opensslntru.cr.yp.to`) · [data/wave5/enrich/raw/opensslntru_cr_yp_to.json](../../../data/wave5/enrich/raw/opensslntru_cr_yp_to.json) (enrichment confidence 0.8)

</details>
