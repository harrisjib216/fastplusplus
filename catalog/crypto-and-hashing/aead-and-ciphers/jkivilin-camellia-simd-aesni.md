# camellia-simd-aesni

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [AEAD and ciphers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟢 active

> Byte-sliced Camellia kernels computing S-boxes with AES-NI/VAES/GFNI; 3-19x faster than NTT's table-based reference C.

| | |
|---|---|
| **Beats** | Camellia reference implementation (NTT camellia-BSD-1.2.0 camellia.c, table-based scalar C, built at -O2 in the same harness) |
| **Claimed result** | README bullets, versus the table-based reference camellia.c in the same harness: SIMD256 32-block intrinsics, AVX512+GFNI \~18.7x on Ryzen 9 7900X, \~17.8x on Core i3-1115G4 (gcc-14), \~14.1x on Ryzen 9 9950X3D (gcc-15); AVX512+VAES 7.4x to 8.9x; AVX2+AES-NI \~5.4x on Core i5-6500. SIMD256 assembly: AVX2+GFNI \~18.2x on 7900X (\~0.92 cycles/byte), \~14.1x on 9950X3D; AES-NI AVX2 \~5.8x on i5-6500. SIMD128 16-block: \~3.1x to 4.5x on x86, \~2.2x to 3.0x on ARM (ThunderX2, Cortex-A53) and \~2.4x on POWER9. The 1-block SIMD128 (constant-time) variants are 1.2x to 2.9x slower than the reference except AVX512+GFNI on the i3-1115G4 (\~1.2x faster). README sample outputs on the 7900X: test_simd256_asm_x86_64 reference 372.041 MiB/s vs SIMD256 5159.460 MiB/s (about 13.9x, derived from page data); test_simd256_intrinsics_x86_64_gfni_avx512 reference 313.426 vs SIMD256 5977.907 MiB/s (about 19.1x, derived). Cortex-A53 sample: 29.027 vs 36.700 MiB/s for 16 blocks (about 1.26x, derived), below the \~2.2x bullet. |
| **Workload** | Camellia-128 encryption/decryption throughput in MiB/s from the repo's own test harness main.c, SIMD implementations processing 16 or 32 blocks in parallel versus the reference doing one block at a time. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 7900X (Zen 4), Ryzen 9 9950X3D (Zen 5), Intel Core i3-1115G4, Core i5-6500, ARM ThunderX2, Cortex-A53 (648 MHz), POWER9 |
| **Compiler and flags** | GCC -O2 with per-target -march flags given in the README build log (sandybridge/haswell/znver4 plus -maes -mvaes -mgfni -mavx512\*); individual rows cite gcc-13, gcc-14 or gcc-15; harness is main.c and the reference is camellia-BSD-1.2.0/camellia.c in the repo |
| **Adoption** | 20 stars |
| **Last commit** | 2026-01-01 |
| **Links** | [repository](https://github.com/jkivilin/camellia-simd-aesni) · [benchmark](https://github.com/jkivilin/camellia-simd-aesni) |

## Verdict

The author's main.c times NTT's camellia-BSD-1.2.0 table-based C (gcc -O2, no -march) against the SIMD kernels, Camellia-128, 8 KiB in place, 1 s per variant: 32-block AVX2/AVX-512+GFNI builds come out about 14-19x faster on Ryzen 9 7900X, Ryzen 9 9950X3D and Core i3-1115G4, AES-NI-only AVX2 builds about 5.4-5.8x on Core i5-6500, and 16-block builds 2.2-4.5x on x86, ARM and POWER9; the README samples I re-derived give 13.9x and 19.1x on the 7900X, but they were run on older code than the bullets.

## Use it when

- A protocol or policy requires Camellia and your mode is parallel: CTR, CBC/CFB decryption, XTS or OCB over at least 16 blocks (256 B) per call.
- x86-64 with GFNI (Ice Lake/Tiger Lake and later, Zen 4/Zen 5): SIMD256 GFNI builds reach about 14-19x the table-based C (about 0.92 cycles/byte on Ryzen 9 7900X per the README).
- You need a cache-timing-safe Camellia: the vector paths use no secret-indexed tables, unlike the reference's four 1 KiB SP tables; the 1-block SIMD128 variants exist for CBC encryption and single blocks.
- AArch64 with Crypto Extensions or POWER8+ where only table-based Camellia exists: 2.2-3.0x in 16-block mode on Cortex-A53/ThunderX2 and about 2.4x on POWER9 per the README.

## Skip it when

- Serial workloads (CBC encryption, single blocks): the constant-time 1-block variants are 1.2x-2.9x slower than the table-based C on most listed CPUs (only AVX-512+GFNI on Tiger Lake is about 1.2x faster).
- You want a library rather than kernels: libgcrypt ships the same author's code (cipher/camellia-simd128.h says it is from this repository) with modes, runtime dispatch and an extra GFNI/AVX-512 64-way path, under LGPL-2.1.
- You are free to pick the cipher: the best GFNI Camellia figure is about 0.92 cycles/byte on Zen 4, while catalogue entries on other machines show AEGIS-128L near 0.18 and SUPERCOP AES-256-GCM near 0.70 cycles/byte, with authentication included.
- RISC-V: the RVA23+Zvkb+Zvkned path was added 2025-12-25 with no published performance numbers and builds with -mstrict-align.

## How it is fast

Camellia's S-boxes share AES's GF(2^8) inversion, so with affine pre- and post-filters (vpshufb nibble lookups, or a single GFNI affine instruction) the S-box layer runs on AES SubBytes via AESENCLAST, with 16 or 32 independent blocks byte-sliced across vector registers to fill the pipelines. GFNI replaces the filter-plus-AES sequence with vgf2p8affineinvqb/vgf2p8affineqb, which is why GFNI builds roughly double VAES builds. The technique is from the author's master's thesis 'Block Ciphers: Fast Implementations on x86-64 Architecture' (pp. 42-50).

## Compared with alternatives

None of the catalogued aead-and-ciphers siblings (libaegis, HiAE, Rocca, intel-ipsec-mb, Crypto++, Botan, Mbed TLS) is a Camellia kernel; pick this only when Camellia is mandated, and pick libaegis or an AES-GCM library whenever the cipher is your choice.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (libc only); GNU make and GCC cross compilers for the provided test binaries |
| **Minimum toolchain** | GCC with the relevant ISA flags (-maes, -mvaes, -mgfni, AVX-512 for the intrinsics builds); README rows cite gcc-13, gcc-14 and gcc-15; Ubuntu 22.04 cross-compilers listed as prerequisites |
| **Platforms** | x86-64 and i386 (AES-NI with SSE4.1/AVX, AVX2, optional VAES/GFNI/AVX-512), AArch64 with Neon+AES CE, ppc64le POWER8+ with VSX and crypto, riscv64 RVA23 with Zvkb+Zvkned |
| **Thread safety** | not documented; all key material lives in the caller-owned struct camellia_simd_ctx and no global mutable state is declared in camellia_simd.h |
| **Drop-in for the baseline** | no |

## Gotchas

- Benchmark noise sets the ratios: main.c times each variant once for 1 s (CLOCK_MONOTONIC, 8 KiB in-place buffer, no repetitions, CPU pinning only in the ThunderX2 sample), and the same camellia_ref_x86-64.o reference reads 372.0 MiB/s in one README sample and 313.4 MiB/s in the other on the same Ryzen 9 7900X (19% apart), so a ratio swings by that much depending on which run it is divided by (the AES-NI SIMD256 sample is 13.9x against 372 but 16.5x against 313).
- README sample outputs are older than the code and the bullets: the current intrinsics code always prints a 1-block line (have_camellia_1blk_simd128() returns 1 since the 2025-12-14 commit), yet the test_simd256_intrinsics_x86_64_gfni_avx512 sample has none; the 16-block asm sample gives 3.6x on the 7900X against a \~4.5x bullet, and the Cortex-A53 sample gives 1.26x against a \~2.2x gcc-15 bullet.
- Throughput is raw ECB-style block processing on an L1-resident 8 KiB buffer; counter generation, XOR and chaining costs of a real mode are not included.
- Argument order is (ctx, out, in), the reverse of the reference's (src, dst), and the 16/32-block functions take no length, so callers must always supply exactly 16 or 32 blocks.

## Known shortcomings

- Baseline is the table-based reference camellia.c, not OpenSSL assembly or libgcrypt; the 1-block variants are slower; README samples disagree with the bullets (13.9x sample vs 9.2x VAES bullet on a 7900X; Cortex-A53 1.26x vs 2.2x). Filed under aead-and-ciphers.
- Harness flaw: main.c times each variant once for 1 s with no repeats on an L1-resident 8 KiB buffer, and the same reference object reads 372.0 vs 313.4 MiB/s in two README samples on the same Ryzen 9 7900X (19% apart), so ratios swing (AES-NI SIMD256 13.9x vs 16.5x). README samples predate the code and the bullets: current intrinsics always print a 1-block line but the gfni_avx512 sample has none; the 16-block asm sample shows 3.6x against a \~4.5x bullet. Throughput is raw block processing with no mode cost. libgcrypt ships the same code plus a GFNI/AVX-512 64-way path.

## Caveats and trade-offs

First-party numbers. The baseline is the NTT table-based reference camellia.c (which the README calls the OpenSSL reference) compiled at -O2 without -march, one block at a time; OpenSSL's Camellia x86-64 assembly, libgcrypt and the Linux kernel's AES-NI/AVX2 Camellia were not measured, so the gain over an optimised incumbent is unknown. Best-case ratios (14-19x) need GFNI on AVX-512 hardware; the 1-block SIMD128 variants are 1.2x to 2.9x slower than the reference on most listed CPUs (one 1.2x faster case), as the README admits. The README sample outputs do not match its own bullets: the plain AES-NI AVX2 assembly sample shows 13.9x on the 7900X while the bullet for the faster VAES build on the same CPU says \~9.2x, the reference itself reads 372 vs 313 MiB/s in two samples on the same machine, and the Cortex-A53 sample shows 1.26x against a \~2.2x bullet, so the samples come from older builds or compilers than the bullets. Only a 16-32 block parallel workload benefits (CTR, CBC/CFB decryption, XTS, OCB). Better filed under a cipher category than simd-intrinsics-libraries. Last commit date taken from the commits page.

Only pays when 16 or 32 blocks are available in parallel (CTR, CBC decrypt, CFB decrypt, XTS, OCB); not useful for CBC encryption or single blocks. Needs AES-NI/VAES/GFNI with AVX2 or AVX-512 on x86, ARMv8 Crypto Extension on AArch64, VSX plus AES on POWER, or RVA23 Zvkb+Zvkned on RISC-V. Hand-written GAS assembly files and C intrinsics; targets one cipher, not a general SIMD library. The README presents a constant-time alternative to table lookups.

## Maintenance

Active (last commit 2026-01-01, ARMv8 1-block work merged from a contributor), MIT-licensed and small enough to vendor, but it is a kernel collection with 0 issues filed and 20 stars; libgcrypt's LGPL copy is the maintained production route.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Benchmark code is public (main.c do_speedtest, clock_gettime loop over an in-place buffer, with test-vector self-tests) and the README gives the exact GCC command lines (-O2 plus per-target -march/-maes/-mvaes/-mgfni/-mavx512\*) and the CPU models; several rows also name gcc-13/14/15. The reference is compiled in the same harness (camellia-BSD-1.2.0/camellia.c at -O2).
- **Verifier notes:** Numbers in the record match the README; tier A stands on main.c plus exact GCC flags and CPU models. Main shortcomings: baseline is the table-based reference C code rather than OpenSSL's Camellia assembly or libgcrypt, 1-block variants slower than the reference, README sample outputs disagree with its bullets (13.9x sample vs 9.2x VAES bullet on the 7900X; 1.26x vs 2.2x on Cortex-A53), only 20 stars. Category would fit a crypto/cipher category better.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-74 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/jkivilin/camellia-simd-aesni>
  - <https://raw.githubusercontent.com/jkivilin/camellia-simd-aesni/HEAD/README.md>
  - <https://github.com/jkivilin/camellia-simd-aesni/commits>
  - <https://raw.githubusercontent.com/jkivilin/camellia-simd-aesni/HEAD/main.c>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/jkivilin/camellia-simd-aesni/HEAD/README.md>
  - <https://raw.githubusercontent.com/jkivilin/camellia-simd-aesni/HEAD/main.c>
  - <https://raw.githubusercontent.com/jkivilin/camellia-simd-aesni/HEAD/camellia_simd.h>
  - <https://raw.githubusercontent.com/jkivilin/camellia-simd-aesni/HEAD/camellia_simd256_x86-64_aesni_avx2.S>
  - <https://raw.githubusercontent.com/jkivilin/camellia-simd-aesni/HEAD/camellia_simd128_with_aes_instruction_set.c>
  - <https://raw.githubusercontent.com/jkivilin/camellia-simd-aesni/HEAD/Makefile>
  - <https://raw.githubusercontent.com/jkivilin/camellia-simd-aesni/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/jkivilin/camellia-simd-aesni/HEAD/camellia-BSD-1.2.0/camellia.c>
  - <https://github.com/jkivilin/camellia-simd-aesni/commits>
  - <https://github.com/jkivilin/camellia-simd-aesni/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/gpg/libgcrypt/master/cipher/camellia-simd128.h>
  - <https://raw.githubusercontent.com/gpg/libgcrypt/master/cipher/camellia-gfni-avx512-amd64.S>
  - <https://raw.githubusercontent.com/gpg/libgcrypt/master/cipher/camellia-aesni-avx2-amd64.h>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/jkivilin/camellia-simd-aesni`) · [data/wave13/enrich/raw/github_com_jkivilin_camellia_simd_aesni.json](../../../data/wave13/enrich/raw/github_com_jkivilin_camellia_simd_aesni.json) (enrichment confidence 0.8)

</details>
