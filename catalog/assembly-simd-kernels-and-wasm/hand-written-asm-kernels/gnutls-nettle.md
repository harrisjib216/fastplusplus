# Nettle (assembly for x86_64, arm64, powerpc64, s390x)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C with assembly (arm, arm64, powerpc64, s390x, sparc64, x86, x86_64 directories)` · `LGPL-3.0-or-later OR GPL-2.0-or-later` · 🟢 active

> Nettle's runtime-dispatched assembly for AES, GCM, ChaCha and SHA, using CPU crypto instructions; beats Nettle's own table C up to 13x on POWER9.

| | |
|---|---|
| **Beats** | Nettle's own previous code: the generic C implementations for the PowerPC64 AES, GCM and Chacha figures (Nettle had no PowerPC64 assembly before 3.7), and Nettle's earlier plain x86_64 assembly for the sha_ni SHA-1/SHA-256 figure (x86_64 SHA1 assembly since Nettle 2.0, SHA256 since 2.7) |
| **Claimed result** | NEWS 3.7: new PowerPC64 assembly, 'Benchmarked on a Power9 machine, speedup was 13 times for AES256-CTR and AES256-GCM, and 3.5 times for Chacha'; NEWS 3.5: x86_64 sha1/sha256 using sha_ni, 'Speedup of 3-5 times on affected processors'; NEWS 3.8: new ARM64 implementation of AES, GCM, Chacha, SHA1 and SHA256 'Great speedups' (no numbers) |
| **Workload** | symmetric crypto kernels in the NEWS file: AES-256-CTR and AES-256-GCM, Chacha on Power9; SHA-1 and SHA-256 with sha_ni on x86_64 |
| **Metric** | throughput |
| **Hardware** | Power9 for the 13x and 3.5x figures; x86_64 with sha_ni for the 3-5x figure (CPU models not stated) |
| **Adoption** | 76 stars (GitHub mirror of the upstream repository) |
| **Last commit** | 2026-10-07 |
| **Links** | [repository](https://github.com/gnutls/nettle) · [benchmark](https://github.com/gnutls/nettle/blob/master/NEWS) |

## Verdict

NEWS 3.7 says the new PowerPC64 assembly ran 13x faster for AES256-CTR and AES256-GCM and 3.5x faster for ChaCha on a Power9 machine, against Nettle's generic C (table AES, C GHASH, one-block C ChaCha). The contributor's 2020 patch posts (nettle-bugs list, blocked here, seen as search snippets only) gave about 13.5x for GCM-AES encrypt and decrypt and about 26x for GHASH on POWER9, and about 17.5x and 30x on POWER8. A 2021 thread reported the stitched-GCM idea at 2.35 vs 1.30 cycles/byte for gcm_aes128 on a 3.5 GHz POWER9. NEWS 3.5 claims 3-5x for SHA-NI SHA-1/SHA-256 over Nettle's earlier x86_64 assembly. No CPU model, compiler, flags or raw output is published for any of these.

## Use it when

- POWER8, POWER9 or POWER10 Linux or AIX hosts doing AES-CTR, AES-GCM or ChaCha in GnuTLS or directly through Nettle. This is where the 13x (AES256-CTR/GCM) and 3.5x (ChaCha) Power9 figures come from.
- s390x and arm64 servers or Android/Apple/BSD arm64 devices with crypto extensions, where a fat build picks hardware AES, GHASH (PMULL), SHA-1 and SHA-256 at run time.
- x86_64 code hashing large volumes with SHA-1 or SHA-256 on CPUs with SHA-NI (NEWS 3.5: 3-5x over Nettle's earlier x86_64 assembly).
- Projects that need a small LGPL-3.0+/GPL-2.0+ crypto core with caller-owned contexts, no malloc and constant-time GHASH on all platforms (rewritten in 3.9), and that accept library-level speed rather than the fastest x86 numbers.

## Skip it when

- Throughput-critical AES-GCM or ChaCha20 on modern x86_64. The x86_64 directory has AES-NI with only two blocks in flight, separate AES and PCLMUL GHASH passes (no stitched GCM), a one-block SSE2 chacha-core-internal.asm, and no VAES, AVX2 or AVX-512 paths. libgcrypt (sibling) ships VAES/AVX512 AES.
- CPUs without carry-less multiply (no PCLMULQDQ, PMULL or vpmsumd). The 3.9 side-channel-silent GHASH rewrite made the C GHASH about 3x slower on x86_64 (NEWS 3.9), so GCM there is slow.
- POWER8 with Nettle 3.10 or 3.10.1. The new p8 stitched GCM-AES files used ISA 3.0 lxv, stxv and lxvb16x instructions while being selected on POWER8 crypto_ext, which was fixed in 3.10.2 (commits d891462, 2dffb58). Before 3.10.2 any ppc64 assembly could also be used without VSX.
- Closed-source static linking where LGPL-3.0 relinking terms are a problem (dual LGPL-3.0-or-later / GPL-2.0-or-later).
- Cases where you need published, reproducible numbers. The speedups exist only as release-note sentences, with no CPU model, compiler, flags or raw nettle-benchmark output.

## How it is fast

Mostly by calling the CPU's crypto instructions instead of Nettle's table-driven C. On POWER8 and later it uses vcipher and vpmsumd (vector crypto), with a stitched GCM-AES loop since 3.10. On x86_64 it uses AES-NI with two blocks interleaved per loop, SHA-NI and PCLMULQDQ. On arm64 it uses the AES, PMULL, SHA1 and SHA2 extensions, and on s390x the MSA facilities. Elsewhere it uses SIMD: ChaCha on POWER runs four blocks in parallel in AltiVec (_nettle_chacha_crypt_4core) against a one-block C core. The fat-\*.c files read CPUID, getauxval(AT_HWCAP/AT_HWCAP2), elf_aux_info, sysctl or AIX _system_configuration, and NETTLE_FAT_OVERRIDE can force a variant.

## Compared with alternatives

Pick Nettle over libgcrypt or CRYPTOGAMS when you want a compact, allocation-free library with stable APIs and automatic hardware dispatch on POWER8+, s390x and arm64, for example under GnuTLS. Pick libgcrypt for wider x86 SIMD (VAES/AVX512, SHA-NI, AES-XTS paths), and CRYPTOGAMS to vendor individual perlasm kernels with per-core cycle tables.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | none for libnettle; libhogweed (public key) needs GMP 6.1.0+ or the bundled mini-gmp (not binary compatible, slower); OpenSSL libcrypto optional, only for comparison rows in nettle-benchmark |
| **Minimum toolchain** | C99 compiler with alignof/alignas (Nettle 4.0), GNU make, m4 for the .asm files; autoconf 2.69 and ./.bootstrap for git checkouts; ppc64 assembly needs VSX (ISA 2.06) since 3.10.2 |
| **Platforms** | assembly for x86, x86_64, arm (v6, Neon), arm64, powerpc64 (p7/p8/p9), s390x, sparc64; fat runtime dispatch on x86_64, arm, arm64, powerpc64 and s390x (Linux, BSD, Android, Apple, AIX); generic C everywhere else |
| **Thread safety** | Contexts are caller-allocated, so use one per thread. The only shared state is the fat dispatch pointers set by a constructor. fat-x86_64.c says the init is idempotent and pointer writes are atomic on x86; the manual's wording was not read. |
| **Drop-in for the baseline** | yes |

## Gotchas

- The headline ratios measure hardware crypto instructions against Nettle's own C or older assembly, not against another library. On x86_64 Nettle's AES-NI interleaves only two blocks, and ChaCha is a one-block SSE2 core, so do not expect parity with libraries that keep 4-8 AES blocks in flight or use AVX2/AVX-512.
- Correctness bugs in the measured POWER code: the 3.7 AltiVec ChaCha that produced the 3.5x figure had a counter-update bug that broke GnuTLS tests on ppc64 (fixed 3.7.1). 3.9 fixed a Power7 ChaCha path that used a later-ISA instruction. 3.10.1 fixed a buffer overread and a stack alignment issue in the new ppc64 SHA-256 assembly. 3.10.2 removed ISA 3.0 instructions from the POWER8 GCM-AES files. Pin 3.10.2 or later on POWER. None of these fixes is described as changing speed.
- Packaging slip: the 3.5 tarball omitted x86_64/sha_ni. That broke x86_64 --enable-fat builds and gave 'worse performance than promised' with --enable-x86-sha-ni until 3.5.1. Also, the x86_64 fat self-test override list in configure.ac covers only vendor:intel and vendor:amd, not aesni or sha_ni, so those paths are tested only on hosts that have the instructions.
- Harness limits (examples/nettle-benchmark.c): it times one warm 10,240-byte buffer in a single run, extended until it lasts over 0.1 s, with no repetitions or median. The 'Mbyte/s' column divides by 1,048,576 (MiB/s). Cycle columns appear only when -f &lt;clock&gt; is passed, and the rdtsc micro-benchmarks run on uninitialised state. Small-message and per-call overhead are not measured.

## Known shortcomings

- NEWS prose only with no methodology; the sha_ni 3-5x baseline is Nettle's older x86_64 assembly, not C, and the Power9 13x is mostly hardware crypto instructions against table-driven C; the GitHub repo is a mirror. Licence LGPL-3.0-or-later OR GPL-2.0-or-later.
- Enricher: the gains are hardware crypto instructions against Nettle's own C (the 13x figure); the x86_64 AES-NI path keeps only 2 blocks in flight with no VAES/AVX2/AVX-512 and a single-block SSE2 ChaCha; the POWER assembly had fixes after measurement (ChaCha counter bug in the 3.5x code fixed in 3.7.1, ppc64 SHA-256 overread in 3.10.1, ISA 3.0 instructions in the POWER8 GCM-AES files in 3.10.2); the 3.5 tarball shipped without x86_64/sha_ni; nettle-benchmark uses one warm 10 KiB buffer in a single run; the patch-post figures (13.5x GCM, 26x GHASH on POWER9) are search snippets only.

## Caveats and trade-offs

Release-note claims by the maintainer and contributors, with no compiler, flags or CPU model beyond 'Power9' and 'affected processors'. Most of the gain comes from hardware crypto instructions (POWER8+ AES/GCM vector crypto, Intel/AMD SHA-NI) rather than from hand-scheduling: the 13x compares hardware AES against Nettle's table-based C, and the 3-5x sha_ni figure compares against Nettle's older x86_64 assembly, not compiler -O3 output. The NEWS 3.8 ARM64 and s390x entries say 'Great speedups' with no numbers, and NEWS 3.0's x86_64 GCM/MD5 assembly claims only 'Modest speedups on the order of 10%-20%'. The benchmark tool examples/nettle-benchmark.c is in the repo, but no results are published alongside it. The GitHub repository is a mirror (description: 'A mirror of the nettle repository'); upstream git instructions are at lysator.liu.se. The licence is a dual LGPL-3.0-or-later / GPL-2.0-or-later choice (GitHub shows only LGPL-3.0).

Fat builds (default since 3.7) select assembly at runtime by CPU feature; per-architecture assembly to maintain; copyleft licence (GitHub shows LGPL-3.0 and the repo carries COPYINGv2, COPYINGv3 and COPYING.LESSERv3).

## Maintenance

Actively maintained by Niels Möller (last commit on the GitHub mirror 2026-10-07, 4,905 commits, NEWS already describing 4.1 after the ABI-breaking 4.0). Copyable under LGPL-3.0-or-later or GPL-2.0-or-later; the GitHub repo is a mirror and upstream lives at lysator.liu.se, whose list and git hosts did not resolve from this session.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Maintainer release notes in NEWS give the 13x (AES256-CTR, AES256-GCM) and 3.5x (Chacha) Power9 figures and the 3-5x sha_ni figure, with no compiler, flags, CPU model or published results; first-party numbers without methodology are tier C.
- **Verifier notes:** All three NEWS quotes are verbatim (3.7: 13x AES256-CTR/GCM and 3.5x Chacha on Power9; 3.5: sha_ni 3-5x; 3.8: ARM64 'Great speedups'). The sha_ni baseline was earlier x86_64 assembly, not generic C, and the PowerPC gains are mainly hardware crypto instructions versus table C. Mirror metadata: 76 stars, 37 forks, last commit 2026-10-07, licence headers dual LGPL-3.0-or-later OR GPL-2.0-or-later.
- **Fields the verifier corrected:** `baseline`, `license`, `caveats`
- **Shortcomings recorded by:** verifier batch-72 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/gnutls/nettle>
  - <https://github.com/gnutls/nettle/commits>
  - <https://raw.githubusercontent.com/gnutls/nettle/HEAD/NEWS>
  - <https://raw.githubusercontent.com/gnutls/nettle/HEAD/README>
  - <https://raw.githubusercontent.com/gnutls/nettle/HEAD/sha256.c>
- **Sources the enricher read:**
  - <https://github.com/gnutls/nettle>
  - <https://raw.githubusercontent.com/gnutls/nettle/HEAD/NEWS>
  - <https://raw.githubusercontent.com/gnutls/nettle/HEAD/README>
  - <https://raw.githubusercontent.com/gnutls/nettle/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/gnutls/nettle/HEAD/fat-x86_64.c>
  - <https://raw.githubusercontent.com/gnutls/nettle/HEAD/fat-ppc.c>
  - <https://raw.githubusercontent.com/gnutls/nettle/HEAD/fat-arm64.c>
  - <https://raw.githubusercontent.com/gnutls/nettle/HEAD/fat-setup.h>
  - <https://raw.githubusercontent.com/gnutls/nettle/HEAD/examples/nettle-benchmark.c>
  - <https://raw.githubusercontent.com/gnutls/nettle/HEAD/x86_64/README>
  - <https://raw.githubusercontent.com/gnutls/nettle/HEAD/powerpc64/README>
  - <https://raw.githubusercontent.com/gnutls/nettle/HEAD/x86_64/aesni/aes128-encrypt.asm>
  - <https://raw.githubusercontent.com/gnutls/nettle/HEAD/x86_64/chacha-core-internal.asm>
  - <https://raw.githubusercontent.com/gnutls/nettle/HEAD/x86_64/sha_ni/sha256-compress-n.asm>
  - <https://github.com/gnutls/nettle/tree/master/x86_64>
  - <https://github.com/gnutls/nettle/tree/master/powerpc64>
  - <https://github.com/gnutls/nettle/tree/master/powerpc64/p8>
  - <https://github.com/gnutls/nettle/commits/master/powerpc64/p8>
  - <https://github.com/gnutls/nettle/commit/d891462ba3f6e39e3696b657dcb69e9869ad9762>
  - https://lists.lysator.liu.se/mailman/hyperkitty/list/nettle-bugs@lists.lysator.liu.se/thread/7GW3XBDM7ZVS6OZEEQ3ZY23WEWSCDJUA (DNS failure; content from WebSearch snippets only)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/gnutls/nettle`) · [data/wave13/enrich/raw/github_com_gnutls_nettle.json](../../../data/wave13/enrich/raw/github_com_gnutls_nettle.json) (enrichment confidence 0.6)

</details>
