# SHA-Intrinsics (noloader)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Cryptographic hashes](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `LicenseRef-Public-Domain` · 🟢 active

> Public-domain SHA-1/SHA-256 block functions on Intel SHA-NI and ARMv8 crypto intrinsics, plus POWER8 SHA-256/512; no measured baseline.

| | |
|---|---|
| **Beats** | portable C SHA-256 (the repo's own sha256.c reference) and OpenSSL SHA-256: neither is measured in the README |
| **Claimed result** | No speedup stated; the README says 'The speedups can be tricky to measure' and lists only absolute Botan numbers. Intel SHA on Celeron J3455: SHA-256 445.747 MiB/sec at 3.64 cycles/byte (GCC 7.3.1) and 447.657 MiB/sec at 3.62 cycles/byte (Clang 5.0.1); SHA-1 889.903 MiB/sec at 1.82 cycles/byte (GCC 7.3.1). ARMv8 (Kirin 620, Cortex-A53 1.2 GHz, GCC 4.9.2): SHA-256 599.463 MiB/sec. The same Intel run shows SHA-512 (no SHA-512 hardware) at 121.721 MiB/sec and 13.32 cycles/byte, but that is a different algorithm so no ratio is derived. Power8 built-ins: SHA-256 250.424 MiB/sec at 12.95 cycles/byte, which the README calls 'not that impressive'. |
| **Workload** | README reports Botan 'speed --msec=3000' hashing of 1024-byte buffers (SHA-1, SHA-224, SHA-256, SHA-384, SHA-512) with Botan using these SHA-NI / ARMv8 / Power8 compression functions; there is no baseline column. |
| **Metric** | throughput |
| **Hardware** | Intel Celeron J3455 1.5 GHz (burst 2.2 GHz), ASUS J3455M-E; Kirin 620 SoC, octa-core Cortex-A53 1.2 GHz (the README names the ARM machine an ARMv8 LeMaker HiKey, the board that carries this SoC); ppc64le POWER8 at 3.4 GHz (GCC112, GCC compile farm) |
| **Compiler and flags** | GCC 7.3.1 and Clang 5.0.1 (x86); GCC 4.9.2 (ARM); GCC 7.2.0 (POWER8). README build flags: -msse4 -msha (x86), -march=armv8-a+crc+crypto (ARM), -mcpu=power8 (POWER8). Botan's own build flags are not stated. |
| **Adoption** | 232 stars; README benchmarks are Botan runs that use this code |
| **Last commit** | 2026-01-08 |
| **Links** | [repository](https://github.com/noloader/SHA-Intrinsics) · [benchmark](https://github.com/noloader/SHA-Intrinsics) |

## Verdict

The README only quotes Botan 'speed --msec=3000' runs on 1024-byte buffers with Botan using these code paths: SHA-256 at 445.7 MiB/s (3.64 cycles/byte, GCC 7.3.1) and 447.7 MiB/s (Clang 5.0.1) on a Celeron J3455 (Goldmont), 599.5 MiB/s on a Kirin 620 Cortex-A53 at 1.2 GHz (GCC 4.9.2), and 250.4 MiB/s (12.95 cycles/byte) on POWER8 at 3.4 GHz (GCC 7.2.0). No portable-C, OpenSSL or software-Botan row was measured, so no speedup can be stated.

## Use it when

- You maintain your own SHA-1 or SHA-256 (hashing loop, padding, API) and want to swap in a hardware block function for CPUs with SHA-NI (AMD Zen, Intel Goldmont and later Atoms, newer Intel Core) or ARMv8 crypto extensions.
- You need public-domain code that can be vendored without a licence notice and without a build system: one .c file per algorithm and architecture.
- Embedded or bootloader code on AArch64 (Cortex-A53 class) where pulling in OpenSSL or Botan is too heavy; the README's Botan run on a Cortex-A53 at 1.2 GHz reports about 599 MiB/s for SHA-256 on 1 KiB buffers.
- As a readable reference for how SHA-NI and ARMv8 SHA intrinsics are sequenced when writing or reviewing your own implementation.

## Skip it when

- You want a complete hash API: OpenSSL, Botan, Crypto++ or libsodium already ship these same code paths with runtime CPU dispatch, padding and test vectors.
- SHA-384/SHA-512 on x86 or ARM: there is no hardware path here (only sha512.c in portable C and sha512-p8.cxx for POWER8); the x86 and ARM SHA-384/512 rows in the README are Botan's software code.
- POWER8: the README calls its own numbers 'not that impressive' (SHA-256 250 MiB/s at 12.95 cycles/byte) and issue #5 on load/store overhead is still open.
- Many messages at once (Merkle trees, proof-of-work, batch verification): multi-buffer AVX2/AVX-512 hashers process several independent messages in parallel and are not covered here.
- Any CPU without the extension: the code has no fallback and executes illegal instructions there; issue #9 shows an Intel i7-10510U lacking SHA-NI.

## How it is fast

The x86 files drive the Intel SHA extensions (_mm_sha256rnds2_epu32 and _mm_sha256msg1/msg2, two rounds per instruction) with the state kept in ABEF/CDGH register order, following Intel's and Sean Gulley's miTLS layout. The ARM files use the ARMv8 crypto instructions (vsha256hq_u32 and friends, four rounds per instruction) after a vrev32q_u8 byte swap. The POWER8 files only accelerate the sigma functions with __builtin_crypto_vshasigmaw/d and still run the rounds in vector code, which is why the README calls the POWER8 result flat.

## Compared with alternatives

Pick it over sha2-with-c-intrinsic (AWS) when you want public-domain single files with an ARMv8 path and no build system; pick AWS's code when you need measured numbers against OpenSSL or AVX/AVX2 SHA-512. For many independent messages, Intel ISA-L Crypto multi-buffer or hashtree are the better fit.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (compiler intrinsic headers only: x86intrin.h/immintrin.h, arm_neon.h/arm_acle.h, altivec.h) |
| **Minimum toolchain** | Not documented as a minimum; README results use GCC 7.3.1 and Clang 5.0.1 (x86), GCC 4.9.2 (ARM), GCC 7.2.0 (POWER8); source comments mention Visual Studio 2015 for the x86 SHA intrinsics, IBM XL C/C++ for POWER8, and g++ being needed for the ARM intrinsics with GCC 4.8.5. Flags: -msse4.1 -msha (x86), -march=armv8-a+crc+crypto (ARM), -mcpu=power8 (POWER8). |
| **Platforms** | x86 / x86-64 with SHA extensions (SHA-1, SHA-224, SHA-256); ARMv8 AArch32/AArch64 with crypto extensions, little-endian (SHA-1, SHA-224, SHA-256); POWER8 or later (SHA-256, SHA-512); portable C reference for SHA-256 and SHA-512. |
| **Thread safety** | Not documented; the functions touch only the caller's state and input plus constant round tables (from reading the code), so separate states can be hashed concurrently. |
| **Drop-in for the baseline** | partial — it replaces only the block function inside an existing SHA implementation; padding, length encoding, the IV, output serialization and CPU feature detection are the caller's job. |

## Gotchas

- Only whole 64-byte blocks are processed: a trailing partial block is silently ignored, and length is a uint32_t, so inputs over 4 GiB must be chunked by the caller.
- No runtime dispatch: cpuid.c is a stand-alone sample that tests CPUID leaf 7 EBX bit 29; you must wire the check in yourself or the binary faults on CPUs without SHA-NI.
- The built-in tests are thin: the sha256-x86.c test main hashes one padded empty block and checks only the first 8 bytes of the digest (e3b0c44298fc1c14); there are no multi-block or NIST known-answer vectors, and issue #12 asked whether SHA-1 padding is missing (closed without an answer).
- The ARM code always byte-swaps with vrev32q_u8 ('Reverse for little endian'), so big-endian AArch64 is not handled; the README numbers come from Botan's adaptations (Botan's sha2_32_armv8.cpp is 'Contributed by Jeffrey Walton', its x86 file credits Sean Gulley's code), not from timing these files directly.

## Known shortcomings

- README numbers have no baseline row (no portable C, OpenSSL or software Botan) and the README never says Botan ran this repo's code. No LICENSE file, only public-domain headers with no patent grant; code effectively unchanged since 2018 (PR #14 merged 2026-01-07 and reverted the next day).
- Enricher: the README numbers time Botan's copies (Botan's ARMv8 SHA-256 file is contributed by the same author; its x86 file credits Gulley's code), not these files. No SHA-512 hardware path on x86 or ARM (the SHA-384/512 rows are Botan software), a trailing partial block is silently dropped, the length is uint32_t, there is no runtime dispatch, ARM always byte-swaps (big-endian broken), and the test checks only the first 8 bytes of the empty-message digest.

## Caveats and trade-offs

No baseline measured: the README gives no portable-C, OpenSSL or software-only Botan row, and the numbers come from Botan ('concrete numbers are available from Jack Lloyd's Botan'); the README does not say which code path Botan was built with, so the link between these numbers and this repo's files is implied, not stated. The README itself says 'The speedups can be tricky to measure' and calls the Power8 numbers 'not that impressive'. No LICENSE file (raw LICENSE returns 404, GitHub shows no license); each source file header says 'Written and placed in public domain by Jeffrey Walton' (sha256-x86.c: 'Written and place in public domain'), with no patent grant. The x86 files are 'based on code from Intel, and by Sean Gulley for the miTLS project' and the ARM files on ARM and mbedTLS code, so the public-domain dedication of derived code is unverified. Maintenance: the 2026-01-08 commit reverts the 2026-01-07 merge of PR #14 (mikowals, opened 2024-02-24, a rename of ARM SHA-256 state variables that changes no calculation), so master's code is unchanged in substance since at least April 2018 (the commits before PR #14 are April 2018 .travis.yml tweaks); PR #16 with the same rename is still open. The x86 source header's own build line uses -msse4.1 -msha while the README says -msse4 -msha. Clang 3.7 ARM results are 'To be determined'.

Only the SHA-1, SHA-224, SHA-256 and SHA-512 compression functions on full blocks: the caller sets the initial state and pads the final block, and the sample main hashes an empty message only. Needs SHA-NI (x86 -msha), ARMv8 crypto extensions or POWER8; Power8 gain is flat. No runtime CPU dispatch in the code (cpuid.c is a sample).

## Maintenance

Effectively frozen since April 2018 (the January 2026 commits merged and then reverted a variable rename), with 2 open issues and 1 open PR; it is small, dependency-free and public domain by file-header dedication (no LICENSE file, no patent grant, derived from Intel, miTLS, ARM and mbedTLS code), so it is easy to vendor but you own the testing.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification D, tier now D.
- **Tier reason:** The README's Benchmarks section lists only absolute Botan 'speed --msec=3000' throughputs (SHA-256 445.747 MiB/sec at 3.64 cycles/byte with GCC 7.3.1 on a Celeron J3455, 599.463 MiB/sec on the Kirin 620, 250.424 MiB/sec on POWER8) with no portable-C, OpenSSL or software-Botan row, so there is no measured speedup over any baseline; D.
- **Verifier notes:** Numbers in claimed_speedup match the README exactly, but there is no baseline row anywhere, so the entry stays at D (keep with shortcoming 'no baseline measured'; the sha256.c reference implementation is never timed). The 2024 'ARM: fix incorrect variable names' change was merged 2026-01-07 and reverted 2026-01-08, so the code is effectively unchanged since 2018 even though the last-commit date reads active; 232 stars, 47 forks, not archived, not a fork.
- **Fields the verifier corrected:** `caveats`, `hardware`
- **Shortcomings recorded by:** verifier batch-57 (wave 7 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/noloader/SHA-Intrinsics>
  - <https://github.com/noloader/SHA-Intrinsics/commits>
  - <https://github.com/noloader/SHA-Intrinsics/pull/14>
  - <https://raw.githubusercontent.com/noloader/SHA-Intrinsics/HEAD/README.md>
  - <https://raw.githubusercontent.com/noloader/SHA-Intrinsics/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/noloader/SHA-Intrinsics/HEAD/sha256-x86.c>
  - <https://raw.githubusercontent.com/noloader/SHA-Intrinsics/HEAD/sha256-arm.c>
  - <https://raw.githubusercontent.com/noloader/SHA-Intrinsics/HEAD/sha256.c>
  - <https://raw.githubusercontent.com/noloader/SHA-Intrinsics/HEAD/sha256-p8.cxx>
- **Sources the enricher read:**
  - <https://github.com/noloader/SHA-Intrinsics>
  - <https://raw.githubusercontent.com/noloader/SHA-Intrinsics/HEAD/README.md>
  - <https://raw.githubusercontent.com/noloader/SHA-Intrinsics/HEAD/sha256-x86.c>
  - <https://raw.githubusercontent.com/noloader/SHA-Intrinsics/HEAD/sha256-arm.c>
  - <https://raw.githubusercontent.com/noloader/SHA-Intrinsics/HEAD/sha256.c>
  - <https://raw.githubusercontent.com/noloader/SHA-Intrinsics/HEAD/sha256-p8.cxx>
  - <https://raw.githubusercontent.com/noloader/SHA-Intrinsics/HEAD/sha1-x86.c>
  - <https://raw.githubusercontent.com/noloader/SHA-Intrinsics/HEAD/sha1-arm.c>
  - <https://raw.githubusercontent.com/noloader/SHA-Intrinsics/HEAD/cpuid.c>
  - <https://raw.githubusercontent.com/noloader/SHA-Intrinsics/HEAD/sha512-x86.c>
  - <https://raw.githubusercontent.com/noloader/SHA-Intrinsics/HEAD/sha512-arm.c>
  - <https://github.com/noloader/SHA-Intrinsics/issues?q=is%3Aissue>
  - <https://github.com/noloader/SHA-Intrinsics/issues/5>
  - <https://github.com/noloader/SHA-Intrinsics/issues/6>
  - <https://github.com/noloader/SHA-Intrinsics/issues/9>
  - <https://github.com/noloader/SHA-Intrinsics/issues/12>
  - <https://raw.githubusercontent.com/randombit/botan/release-2/src/lib/hash/sha2_32/sha2_32_x86/sha2_32_x86.cpp>
  - <https://raw.githubusercontent.com/randombit/botan/release-2/src/lib/hash/sha2_32/sha2_32_armv8/sha2_32_armv8.cpp>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/noloader/sha-intrinsics`) · [data/wave7/enrich/raw/github_com_noloader_sha_intrinsics.json](../../../data/wave7/enrich/raw/github_com_noloader_sha_intrinsics.json) (enrichment confidence 0.75)

</details>
