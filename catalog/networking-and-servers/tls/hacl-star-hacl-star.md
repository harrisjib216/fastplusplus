# EverCrypt (HACL\*) Curve25519 (Vale-optimized)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [TLS](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `Apache-2.0` · 🟢 active

> Formally verified C/asm crypto library; its ADX X25519 took about 4% fewer cycles than OpenSSL's ADX assembly.

| | |
|---|---|
| **Beats** | OpenSSL |
| **Claimed result** | EverCrypt's targeted Curve25519 (Low\* C plus Vale Intel ADX asm) takes 113,614 CPU cycles per scalar multiplication. OpenSSL's ADX asm takes 118,604. That is about 4.2% fewer cycles, or about 1.04x (derived from page data, Figure 9 of 'EverCrypt: A Fast, Verified, Cross-Platform Cryptographic Provider', IEEE S&P 2020). The paper's text says EverCrypt beats Oliveira et al. (115,122 cycles) by about 1%, and that Oliveira et al. 'in turn exceeds that of OpenSSL by 3%'. It also says EverCrypt beats Erbsen et al./fiat-crypto (145,248 cycles) by 22%. |
| **Workload** | Curve25519 scalar multiplication (the X25519 ECDH used in TLS 1.3), average CPU cycles per operation. The other implementations were measured in-kernel with Donenfeld's kbench9000 cycle counter. OpenSSL was measured 'using the same script, but in user space', because it cannot be called from the kernel. |
| **Metric** | throughput |
| **Hardware** | Intel Kaby Lake i7-7560 (the paper's wording; the record's i7-7560U suffix is not in the paper) |
| **Compiler and flags** | GCC 7.3, -O3 -march=native -mtune=native |
| **Adoption** | 1,837 stars. hacl-star.github.io says code from HACL\*, ValeCrypt and EverCrypt is deployed in Mozilla Firefox's NSS, the Linux kernel, mbedTLS, the Tezos blockchain, the ElectionGuard SDK and the WireGuard VPN. |
| **Last commit** | 2026-04-10 |
| **Links** | [repository](https://github.com/hacl-star/hacl-star) · [benchmark](https://project-everest.github.io/assets/evercrypt.pdf) |

## Verdict

Figure 9 of the IEEE S&P 2020 EverCrypt paper was measured on an Intel Kaby Lake i7-7560 with GCC 7.3 -O3 -march=native, with Hyper-Threading and Turbo off. EverCrypt's Low\*+Vale X25519 took 113,614 cycles per scalar multiplication against 118,604 for OpenSSL's ADX assembly (commit e8fb288): about 4.2% fewer cycles, and about 1% fewer than Oliveira et al. (115,122). The other implementations ran in-kernel under kbench9000, but OpenSSL ran the 'same script' in user space, and the public kbench9000 x25519 branch has no OpenSSL harness.

## Use it when

- X25519 key exchange (TLS 1.3, WireGuard/Noise, HPKE) on x86-64 CPUs with both BMI2 and ADX, when you want machine-checked memory safety, functional correctness and secret-independent timing without losing speed to hand-written ADX assembly.
- C projects that can vendor a few generated .c/.S files (EverCrypt_Curve25519, Hacl_Curve25519_51/64, AutoConfig2, Vale cpuid and curve25519 asm, karamel headers) instead of linking all of libcrypto.
- Mixed fleets that ship one binary: EverCrypt_Curve25519 checks CPUID at run time and uses the ADX path only where it is supported.
- Kernel or other freestanding-style code: Linux carries a derivative (lib/crypto/x86/curve25519.h, copyright INRIA, CMU and Microsoft). When it replaced the previous ADX code, Donenfeld measured it within about 1.6% either way of that code on 10 Intel CPUs.

## Skip it when

- Raw speed is your only reason to switch. The measured gain over OpenSSL is about 4% on one Kaby Lake CPU against a 2018-19 OpenSSL build, and in the kernel tests it roughly ties the fastest unverified ADX code.
- CPUs without ADX (for example Haswell, which has BMI2 only) and non-x86 targets. These fall back to portable radix-51 C, which Figure 9 puts at 135,636 cycles, about 14% slower than OpenSSL's ADX assembly (118,604). configure excludes Hacl_Curve25519_64.c on anything other than x64.
- You need a TLS stack, the EVP interface, PEM/DER key handling or certificates. This repo provides primitives only.
- Assuming the other primitives also beat OpenSSL. The paper says only that AES-GCM and ChaCha-Poly 'meet or exceed' OpenSSL. In its picoquic test, EverCrypt's ChaCha20-Poly1305 was slower (84.3 vs 90.9 MB/s).
- You want versioned, supported C releases. The README calls this the research home and points production users to cryspen/hacl-packages, which was last pushed in April 2025. Changing the code itself needs F\*, Z3, KaRaMeL and Vale.

## How it is fast

The fast back-end does field arithmetic mod 2^255-19 in radix-2^64 (four limbs) with Vale-verified x86-64 assembly. The assembly uses MULX (BMI2) and the two independent carry chains ADCX/ADOX (ADX), following Oliveira et al.'s ADX Curve25519. It adds fused fmul2/fsqr2 routines that multiply or square two field elements in one call. The Low\* Montgomery ladder is specialised for clamped scalars: it starts with bit 254 set, runs 251 steps over bits 253..3 and ends with three doublings, which reduces conditional swaps. The paper credits these changes with beating Oliveira et al. by about 1%.

## Compared with alternatives

Pick it over msotoodeh/curve25519 when you want proven correctness and constant-time guarantees for X25519, not just an unverified speed-tuned implementation. Pick AWS-LC or wolfSSL instead when you need a full TLS library with an OpenSSL-style API rather than a vendored primitive.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | No F\*/Z3 needed to use dist/. You need the KaRaMeL runtime headers (dist/karamel) and Hacl_Krmllib. EverCrypt dispatch also needs EverCrypt_AutoConfig2.c and the Vale cpuid-x86_64-\*.S. The fast path needs curve25519-x86_64-\*.S or the GCC inline-asm header curve25519-inline.h. config.h is generated by dist/configure. The dist Makefile can build libevercrypt.a/.so. |
| **Minimum toolchain** | C11 GCC/Clang for gcc-compatible (it uses VLAs; the Makefile passes -std=gnu11). MSVC needs the msvc-compatible dist, which uses external .asm instead of inline asm. configure disables addcarry intrinsics on GCC &lt; 5.5 (bug 81300) and inline asm on one broken Apple clang build. The paper benchmarked with GCC 7.3. |
| **Platforms** | Fast path: x86-64 with BMI2+ADX, with Linux, macOS, MinGW and MSVC assembly variants. Everywhere else, portable radix-51 C (best with 64-bit __int128; 32-bit uses emulated 128-bit arithmetic). configure also handles aarch64, ARMv7, s390x, ppc64le and x86. |
| **Thread safety** | Not documented. From the code: the Curve25519 functions keep all state in stack buffers, so they should be reentrant. EverCrypt_AutoConfig2_init writes unsynchronized global CPU-feature flags, so call it once before starting threads. |
| **Drop-in for the baseline** | partial — it replaces OpenSSL only at the raw X25519 primitive (scalarmult/ecdh on 32-byte buffers); there is no EVP_PKEY, BIO or libssl-compatible interface |

## Gotchas

- Call EverCrypt_AutoConfig2_init() before anything else. Otherwise the BMI2/ADX flags stay false and EverCrypt_Curve25519_\* silently runs the slow portable path; the docs say skipping init means always getting the fallback.
- Dispatch requires both BMI2 and ADX. A BMI2-only CPU such as Haswell gets the portable code; the Linux commit notes that 'haswell no longer benefits'.
- ecdh returns false when the shared secret is all zeros (low-order peer key), so check the result; scalarmult does no such check. Clamping is implicit: the ladder reads only bits 3-253 and treats bit 254 as set. Open issue #1071, an unreviewed LLM audit, notes that the F\* spec never calls decodeScalar.
- The proofs trust F\*, Z3, KaRaMeL, the C compiler and the inline-asm constraint strings. In 2021, imprecise clobber annotations in the Vale Curve25519 inline asm caused trouble with old GCC in the kernel (PR #501). NULL arguments are unchecked preconditions, not defensive checks (issue #327).

## Known shortcomings

- Only about 4% fewer cycles than OpenSSL for Curve25519 (113,614 vs 118,604); the paper's '3% over OpenSSL' refers to Oliveira et al. The public benchmark code has no OpenSSL run, and OpenSSL ran in user space while the others ran in the kernel. Its value is formal verification at near-OpenSSL speed.
- Small gain: \~4.2% fewer cycles than OpenSSL (113,614 vs 118,604) on one Kaby Lake i7-7560 against 2018-19 OpenSSL run in user space while the others ran in-kernel; the public kbench9000 harness has no OpenSSL and uses a median of 5,000 trials, not the paper's average of 1,000. Without ADX (including Haswell) or on non-x86 it falls back to portable radix-51 C, \~14% slower than OpenSSL. Forgetting EverCrypt_AutoConfig2_init() silently leaves the slow fallback on. In the paper's picoquic test EverCrypt's ChaCha20-Poly1305 was slower than OpenSSL's. No versioned C releases (hacl-packages last pushed 2025-04); changing code needs F\*, Z3, KaRaMeL and Vale. Raw X25519 functions only, no EVP/TLS layer. Proofs trust the toolchain and inline-asm constraints (clobber issue with old GCC in the kernel, PR #501); NULL arguments unchecked (#327). Positive: Linux replaced its ADX Curve25519 with this code, measured within \~1.6% of the previous fastest ADX code.

## Caveats and trade-offs

The gain over OpenSSL is only about 4% in cycles (derived). The record's '\~3% over OpenSSL' misreads the paper: that 3% is Oliveira et al. over OpenSSL. The result is from one 2017-era Kaby Lake CPU, against an OpenSSL build from 2018-19 (commit e8fb288). OpenSSL ran in user space while the other implementations ran in-kernel via kbench9000, so the environments differ. The public kbench9000 kb/x25519 branch holds the EverCrypt/Vale code and the other contenders but no OpenSSL harness, so the OpenSSL comparison cannot be fully reproduced from public code. The paper's AES-GCM and ChaCha20-Poly1305 figures (Figures 7-8, i9-9900K) say only that EverCrypt 'meets or exceeds' OpenSSL, so do not extrapolate to other primitives. The README calls hacl-star the research home and points production users to https://github.com/cryspen/hacl-packages. The repo is Apache-2.0, and the generated C code is also MIT.

Source is written in F\*/Low\*/Vale and compiled via KaRaMeL to C/assembly rather than hand-written C; gains formal proofs of memory safety, functional correctness and secret-independence (constant-time) at the cost of a heavy build toolchain (F\*, KaRaMeL, Vale) compared to a plain C/asm library.

## Maintenance

The research repo is actively maintained (last main commit 2026-04-10; Apache-2.0, with the generated C also MIT) and dist/ is easy to copy, but there are no versioned C releases, and the README sends production users to cryspen/hacl-packages, itself last pushed in April 2025.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now B.
- **Tier reason:** Peer-reviewed IEEE S&P 2020 paper (confirmed on IACR ePrint 2019/757). Figure 9 gives cycle counts vs OpenSSL, with GCC 7.3, -O3 -march=native -mtune=native and a Kaby Lake i7-7560 stated. It is not tier A because the public harness (kbench9000, branch kb/x25519, main.c) benchmarks EverCrypt, Vale, precomp/Oliveira, fiat, donna, sandy2x and others but has no OpenSSL. The paper says OpenSSL was run 'using the same script, but in user space', and that user-space run is not in the public code.
- **Verifier notes:** The record's '\~3% faster than OpenSSL' comes from misreading the paper's chained sentence. The Figure 9 cycle counts show about 4.2% (EverCrypt 113,614 vs OpenSSL 118,604 cycles), and claimed_speedup is corrected to that. Downgraded A to B because the public benchmark harness has no OpenSSL. Metadata checked with gh: Apache-2.0, not a fork, not archived, 1,837 stars, last commit 2026-04-10, so 'active' holds.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `hardware`, `workload`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://project-everest.github.io/assets/evercrypt.pdf>
  - <https://github.com/hacl-star/hacl-star>
  - <https://eprint.iacr.org/2019/757>
  - <https://hacl-star.github.io/>
  - <https://git.zx2c4.com/kbench9000/about/>
  - <https://git.zx2c4.com/kbench9000/refs/>
  - <https://git.zx2c4.com/kbench9000/tree/?h=kb/x25519>
  - <https://git.zx2c4.com/kbench9000/tree/?h=jd/curve-comparison>
  - <https://git.zx2c4.com/kbench9000/tree/main.c?h=kb/x25519>
- **Sources the enricher read:**
  - <https://github.com/hacl-star/hacl-star>
  - <https://github.com/hacl-star/hacl-star/tree/main/dist>
  - <https://github.com/hacl-star/hacl-star/blob/main/dist/gcc-compatible/EverCrypt_Curve25519.c>
  - <https://github.com/hacl-star/hacl-star/blob/main/dist/gcc-compatible/EverCrypt_Curve25519.h>
  - <https://github.com/hacl-star/hacl-star/blob/main/dist/gcc-compatible/EverCrypt_AutoConfig2.c>
  - <https://github.com/hacl-star/hacl-star/blob/main/dist/gcc-compatible/EverCrypt_AutoConfig2.h>
  - <https://github.com/hacl-star/hacl-star/blob/main/dist/gcc-compatible/Hacl_Curve25519_64.c>
  - <https://github.com/hacl-star/hacl-star/blob/main/dist/gcc-compatible/Hacl_Curve25519_64.h>
  - <https://github.com/hacl-star/hacl-star/blob/main/dist/gcc-compatible/Hacl_Curve25519_51.h>
  - <https://github.com/hacl-star/hacl-star/blob/main/dist/gcc-compatible/curve25519-inline.h>
  - <https://github.com/hacl-star/hacl-star/blob/main/dist/gcc-compatible/Makefile>
  - <https://github.com/hacl-star/hacl-star/blob/main/dist/gcc-compatible/Makefile.basic>
  - <https://github.com/hacl-star/hacl-star/blob/main/dist/configure>
  - <https://github.com/hacl-star/hacl-star/commits/main>
  - <https://github.com/hacl-star/hacl-star/issues/1071>
  - <https://github.com/hacl-star/hacl-star/issues/744>
  - <https://github.com/hacl-star/hacl-star/issues/327>
  - <https://github.com/hacl-star/hacl-star/pull/501>
  - <https://project-everest.github.io/assets/evercrypt.pdf>
  - <https://hacl-star.github.io/>
  - <https://hacl-star.github.io/HaclValeEverCrypt.html>
  - <https://hacl-star.github.io/HaclECDH.html>
  - <https://hacl-star.github.io/EverCryptAutoConfig.html>
  - <https://hacl-star.github.io/EverCryptNonAgile.html>
  - <https://hacl-star.github.io/Obtaining.html>
  - <https://hacl-star.github.io/API.html>
  - <https://github.com/cryspen/hacl-packages>
  - <https://github.com/torvalds/linux/blob/master/lib/crypto/x86/curve25519.h>
  - <https://github.com/torvalds/linux/commit/07b586fe0662>
  - <https://github.com/torvalds/linux/commit/acd93f8a4ca7>
  - <https://github.com/torvalds/linux/commit/dc7fc3a53ae1>
  - <https://git.zx2c4.com/kbench9000/plain/main.c?h=kb/x25519>
  - <https://hn.algolia.com/api/v1/search?query=EverCrypt&tags=story>
  - <https://hn.algolia.com/api/v1/items/19563073>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/hacl-star/hacl-star`) · [data/wave5/enrich/raw/github_com_hacl_star_hacl_star.json](../../../data/wave5/enrich/raw/github_com_hacl_star_hacl_star.json) (enrichment confidence 0.8)

</details>
