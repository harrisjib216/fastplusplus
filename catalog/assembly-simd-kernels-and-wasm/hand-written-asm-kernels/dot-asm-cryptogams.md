# CRYPTOGAMS (dot-asm/cryptogams, perlasm crypto kernels for x86_64, ARM, RISC-V, PPC, MIPS, s390x)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Perl-generated assembly (x86_64, ARMv4/v8, RISC-V, PPC, MIPS, SPARC, s390x, IA64, webasm)` · `BSD-3-Clause OR GPL-2.0-or-later (CRYPTOGAMS licence text with GPL alternative)` · 🟢 active

> Andy Polyakov's perlasm generators for ChaCha20, Poly1305, Keccak, SHA, AES and X25519 on a dozen ISAs; integer paths 1.4-3x faster than gcc output.

| | |
|---|---|
| **Beats** | gcc 4.8 compiled C (integer 'IALU' column) for the same ChaCha20 and Poly1305 algorithm; for Poly1305 the footnote says the comparison is against __int128 C code and gains over clang are about 50% |
| **Claimed result** | poly1305-armv4.pl header, 'IALU(\*)/gcc-4.4' column: IALU assembly 7.78 / 6.35 / 6.25 / 5.10 / 3.85 / 5.70 cycles per byte with '+100% / +130% / +115% / +95% / +85% / +100%' improvement over gcc-4.4 output (ARM11xx, Cortex-A5, A8, A9, A15, Snapdragon S4); NEON 3.00 / 2.36 / 2.55 / 1.25 / 1.48 cycles per byte on A5 / A8 / A9 / A15 / S4. sha1-x86_64.pl header ('Performance improvement is summarized in the following table'): +45% over gcc 3.4 on Opteron and +65% on Xeon (EM64T) at 6.8 / 9.9 cycles per byte. Newer headers in the same repo: poly1305-riscv.pl 1.8 cycles per byte on SiFive U74, '&gt;100% faster than compiler-generated code', 1.9 on C910 (\~75%), 3.3 on SpacemiT X60 (\~69%); keccak1600-riscv.pl SHA3-256 22 cycles per byte on U74, '\~60% faster than compiler-generated code'; chacha-x86_64.pl IALU column +39% to +99% over gcc 4.8 (5.87 cycles per byte on Skylake, +39%) with SSSE3/AVX paths down to 0.58 cycles per byte on Rocket Lake. |
| **Workload** | cycles per byte out of large buffers for ChaCha20 (x86_64/chacha-x86_64.pl) and Poly1305 blocks (x86_64/poly1305-x86_64.pl) across Intel, AMD, VIA and Atom-class cores, with scalar integer, SSSE3, AVX, AVX2 and AVX-512 code paths |
| **Metric** | throughput |
| **Hardware** | Per-row CPUs in the header table: P4, Core2, Westmere, Sandy Bridge, Ivy Bridge, Haswell, Skylake-X, Cannon Lake, Rocket Lake, Silvermont, Knights Landing, Goldmont, Bulldozer, Ryzen, VIA Nano; timings measured with rdtsc at fixed clock |
| **Compiler and flags** | gcc-4.4 (ARM Poly1305, integer path for -march=armv6), gcc 3.4 (x86_64 SHA-1), gcc 4.8 (x86_64 ChaCha); RISC-V headers say only 'compiler-generated code' without naming the compiler; no other flags stated |
| **Adoption** | 70 stars; the same generators feed OpenSSL's x86_64 and ARM assembly |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/dot-asm/cryptogams) · [benchmark](https://raw.githubusercontent.com/dot-asm/cryptogams/HEAD/x86_64/chacha-x86_64.pl) |

## Verdict

All numbers are first-party comment tables in each perlasm file, in cycles per byte, mostly measured with rdtsc at fixed clock. Each integer path is compared with gcc output for C code that is not in the repo. Examples: x86_64 ChaCha20 at 5.87 cpb on Skylake (+39% over gcc 4.8), x86_64 Poly1305 +90-200% over gcc-4.8 __int128 code (about 50% over clang), ARMv4 Poly1305 +85-130% over gcc-4.4, and RISC-V Poly1305 at 1.8 cpb on U74 (over 100% versus an unnamed compiler). SIMD paths reach 0.58 cpb for ChaCha20 (Rocket Lake) and 0.24 cpb for Poly1305 with IFMA. No harness, C reference or compiler flags are published.

## Use it when

- You need fast ChaCha20-Poly1305, Keccak/SHA-3 or SHA-512 kernels inside your own crypto or TLS code without linking OpenSSL; the Linux kernel's lib/crypto/x86/poly1305-x86_64-cryptogams.pl is derived from this code.
- RISC-V targets, where this is among the few tuned sources: Poly1305 runs at 1.8 cycles per byte on SiFive U74 (header: over 100% faster than compiler output) and 1.2 cpb vectorised on SpacemiT X60. ChaCha20 runs at 6.0 cpb with the 'vertical' vector code on X60. Zbb/Zvkb, Zknh and CHERI variants are included.
- ARMv8 ChaCha20 on big cores: 1.25-1.30 cpb with 6xNEON+2xIALU on Apple M1, Cortex-X925 and Snapdragon X, against 3.9-4.5 cpb for the integer path (header table).
- GPLv2 code bases that cannot take OpenSSL's Apache-2.0 copies: the CRYPTOGAMS licence offers BSD-3-style terms or the GPL.

## Skip it when

- You want a turnkey library. CPU-feature detection is missing (issue #4, open since 2019), and so are benchmark or test programs (#3), a build system and C headers. Nettle, libgcrypt, OpenSSL or libsodium ship the same class of assembly behind a real API.
- SHA-1 on modern x86: x86_64/sha1-x86_64.pl is the original integer-only file (6.8 / 9.9 cpb on Opteron / Xeon EM64T against gcc 3.4). OpenSSL's current copy adds SSSE3, AVX, AVX2 and SHA-NI paths: 3.54 cpb on Skylake, 1.93 on Ryzen with SHA extensions.
- If you need every OpenSSL-side fix and file: issue #7 (open since 2020) lists OpenSSL modules missing here. Some have since been added (aesni-gcm-x86_64, ghashv8-armx, sha512-armv8), but x86_64/ghash-x86_64.pl is still absent. Pull requests are ignored, and issues shared with OpenSSL are redirected there.
- ARMv8 ChaCha20 on little or older cores: inputs of 512 bytes or more take the 6xNEON+2xIALU path, which the header marks slower than 4+1 on Cortex-A53 (4.45 vs 4.06 cpb), A57, Denver, X-Gene, Mongoose and Kryo.
- When licence clarity matters: the GPL alternative names no version (issue #12, open since 2021), and headers mix 'GPL-1.0+ OR BSD-3-Clause' with the older 'OpenSSL or CRYPTOGAMS' wording.

## How it is fast

Each primitive is hand-scheduled per microarchitecture and dispatched at run time from capability bits. ChaCha20 runs 1x/2x/4x SSSE3, 4x XOP, 8x AVX2 and 16x AVX-512F block-parallel lanes. Poly1305 keeps the accumulator in base 2^26 limbs for AVX/AVX2/AVX-512. With AVX512-IFMA it uses base 2^44 and vpmadd52luq/huq, and it precomputes key powers r^1..r^4 so that 4 blocks are multiplied in parallel. The scalar paths use 64-bit limb arithmetic tuned for each core. x86_64-xlate.pl translates one source to ELF, Mach-O and Win64 (with SEH unwind tables); newer RISC-V files add vector, Zbb/Zvkb, Zknh, Zicfilp and CHERI variants.

## Compared with alternatives

Pick it over the Nettle or libgcrypt siblings when you want individual kernels (especially RISC-V, CHERI or a GPLv2-compatible licence) without adopting a whole library. Pick those libraries when you need a supported API with CPU detection and tests. For post-quantum RISC-V work, PQRV covers Kyber and Dilithium, which CRYPTOGAMS does not.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Perl at build time and an assembler (GNU as or clang; nasm or ml64 for Win64). The caller must define and fill OpenSSL's capability words: OPENSSL_ia32cap_P on x86 and OPENSSL_armcap_P on ARM. ARM files include arm/arm_arch.h. |
| **Minimum toolchain** | Perl 5. For x86_64 SIMD paths: GNU binutils 2.19 (AVX), 2.22 (AVX2), 2.25 (AVX-512) and 2.26 (IFMA, Poly1305), or clang above 3.0 (clang 7 or later for AVX-512); nasm 2.09+ or ml64 for Win64. |
| **Platforms** | x86_64 (ELF, Mach-O, mingw64, Win64 nasm/masm), x86, ARMv4-v8 (including a Linux-kernel flavour), RISC-V 32/64 with V/Zbb/Zvkb/Zknh/Zicfilp/CHERI, PPC, MIPS, SPARCv9, s390x, IA64, CIL; WebAssembly text for Poly1305 |
| **Thread safety** | Reentrant by code reading: pure functions on caller-owned contexts; the capability words are read-only after the caller sets them |
| **Drop-in for the baseline** | partial: the entry points and context layouts are OpenSSL's internal ones (ChaCha20_ctr32, poly1305_init/blocks/emit), so it can replace a C fallback behind that interface, but there is no C header, CPU detection or high-level AEAD API |

## Gotchas

- SIMD paths are chosen when the Perl script runs, not only at run time. Each x86_64 script probes `$CC -Wa,-v` or `$CC -v` (or nasm/ml64) for the assembler version. If the regex does not match, as with an unusual cross-compiler name, `$avx` stays undefined and the AVX/AVX2/AVX-512 code is left out without warning, leaving only SSSE3 and scalar code.
- Run-time dispatch reads OpenSSL's bit layout (`OPENSSL_ia32cap_P+4/+8`, `OPENSSL_armcap_P`), and nothing here fills it. The ChaCha20 and Poly1305 headers say AVX-512 is deliberately suppressed on Skylake-X because it slows the whole system. That suppression lives in OpenSSL's CPUID code, so an integrator who simply copies CPUID bits gets the AVX-512 paths the author avoids.
- poly1305_init selects the implementation and, outside the kernel flavour, returns the matching blocks/emit function pointers through its third argument. The IFMA path keeps the hash in base 2^44 (poly1305_init_base2_44, poly1305_emit_base2_44), so do not mix entry points of different implementations on one context.
- Divergence from OpenSSL on Win64 IFMA, from reading the code: OpenSSL now builds its AVX512-IFMA Poly1305 only when not Win64 (`$avx>3 && !$win64`, the area of its CVE-2023-4807 fix), and its 8-block IFMA routine uses ymm6-10 without saving them. Here IFMA stays enabled on Win64, but that 8-block routine is compiled out with `if (0)`, and the live 1x/4x IFMA routines use only ymm0-5 and ymm16-31. The header does not say which routine produced its 0.24 cpb AVX-512 IFMA figures for Cannon Lake and Rocket Lake.

## Known shortcomings

- First-party header tables with old compilers (gcc 3.4/4.4/4.8) or none named and no harness; RISC-V and ChaCha header figures added.
- Enricher: no harness or C reference behind the header tables; AVX paths are chosen when the Perl script probes \$CC and are silently dropped if the probe fails; dispatch reads OPENSSL_ia32cap_P/armcap_P but the repo has no CPU detection (#4 open since 2019); the ARMv8 ChaCha at 512 B and above uses the 6+2 path, slower on A53/A57 per its own header; unlike OpenSSL (which disables IFMA Poly1305 on Win64 around CVE-2023-4807) IFMA stays on here while the 8x routine using ymm6-10 is compiled out with if (0), and the header does not say which routine gave its 0.24 cpb IFMA figure; GPL version unstated (#12).

## Caveats and trade-offs

Performance data is a comment table in each .pl file, first-party and without a harness, C reference or compiler flags; the compilers named (gcc 3.4, 4.4, 4.8) are old, so modern compilers may close part of the gap, and the RISC-V headers do not name a compiler at all. The percentage column is the assembly's improvement over the compiler-generated code (the compiler output is that much slower). The repo README has no performance numbers, and pull requests are ignored (issues common with OpenSSL are redirected there). Some files are old revisions: x86_64/sha1-x86_64.pl is the original integer-only version with no SSSE3/AVX/SHA-NI paths, so OpenSSL's current perlasm is faster on modern x86. The same assembly ships in OpenSSL (and parts in the Linux kernel and XKCP); file headers carry 'GPL-1.0+ OR BSD-3-Clause' or the older 'OpenSSL or CRYPTOGAMS license' wording. Only five headers were read.

Per-architecture assembly generated by perl scripts and assembled with a 'flavour' argument; many code paths are specific to one ISA extension (AVX-512, IFMA), and the author says AVX-512 paths on Skylake-X are deliberately suppressed because they can slow the whole system. The README says pull requests are currently ignored and OpenSSL-common issues go through OpenSSL channels.

## Maintenance

Active and copyable as a source drop: last commit 2026-10-05; 2025-2026 work is mostly RISC-V vector and CHERI support plus new Cortex-X925 and Snapdragon X results. 70 stars, 8 open issues (#3 benchmarks and #4 CPU detection open since 2019); pull requests are ignored, and the README's background link is dead (#19).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party comment tables in the perlasm headers compare the assembly with compiler-generated code (gcc-4.4 for ARM Poly1305, gcc 3.4 for x86_64 SHA-1, gcc 4.8 for x86_64 ChaCha), but there is no benchmark harness or C reference in the repo and no flags beyond -march=armv6 for one column, so not A or B.
- **Verifier notes:** Numbers in the record match the poly1305-armv4.pl and sha1-x86_64.pl headers; added newer RISC-V and x86_64 ChaCha header figures. Metadata matches (70 stars, last commit 2026-10-05, LICENSE is BSD-3-style with GPL alternative). Not a duplicate of a listed entry: OpenSSL appears in the catalog only as a baseline. Shortcomings: first-party comment tables, old or unnamed compilers, no harness.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-37 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/dot-asm/cryptogams/HEAD/arm/poly1305-armv4.pl>
  - <https://raw.githubusercontent.com/dot-asm/cryptogams/HEAD/x86_64/sha1-x86_64.pl>
  - <https://raw.githubusercontent.com/dot-asm/cryptogams/HEAD/riscv/poly1305-riscv.pl>
  - <https://raw.githubusercontent.com/dot-asm/cryptogams/HEAD/riscv/keccak1600-riscv.pl>
  - <https://raw.githubusercontent.com/dot-asm/cryptogams/HEAD/x86_64/chacha-x86_64.pl>
  - <https://raw.githubusercontent.com/dot-asm/cryptogams/HEAD/LICENSE>
  - <https://github.com/dot-asm/cryptogams>
  - <https://github.com/dot-asm/cryptogams/commits>
  - <https://github.com/dot-asm/cryptogams/tree/master/riscv>
- **Sources the enricher read:**
  - <https://github.com/dot-asm/cryptogams>
  - <https://github.com/dot-asm/cryptogams/commits>
  - <https://github.com/dot-asm/cryptogams/issues>
  - <https://github.com/dot-asm/cryptogams/issues/4>
  - <https://github.com/dot-asm/cryptogams/issues/7>
  - <https://github.com/dot-asm/cryptogams/issues/12>
  - <https://github.com/dot-asm/cryptogams/issues/19>
  - <https://github.com/dot-asm/cryptogams/tree/master/x86_64>
  - <https://github.com/dot-asm/cryptogams/tree/master/arm>
  - <https://github.com/dot-asm/cryptogams/tree/master/c>
  - <https://github.com/dot-asm/cryptogams/tree/master/webasm>
  - <https://raw.githubusercontent.com/dot-asm/cryptogams/HEAD/README.md>
  - <https://raw.githubusercontent.com/dot-asm/cryptogams/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/dot-asm/cryptogams/HEAD/x86_64/chacha-x86_64.pl>
  - <https://raw.githubusercontent.com/dot-asm/cryptogams/HEAD/x86_64/poly1305-x86_64.pl>
  - <https://raw.githubusercontent.com/dot-asm/cryptogams/HEAD/x86_64/sha1-x86_64.pl>
  - <https://raw.githubusercontent.com/dot-asm/cryptogams/HEAD/x86_64/aesni-x86_64.pl>
  - <https://raw.githubusercontent.com/dot-asm/cryptogams/HEAD/x86_64/keccak1600-x86_64.pl>
  - <https://raw.githubusercontent.com/dot-asm/cryptogams/HEAD/x86_64/x86_64-xlate.pl>
  - <https://raw.githubusercontent.com/dot-asm/cryptogams/HEAD/arm/poly1305-armv4.pl>
  - <https://raw.githubusercontent.com/dot-asm/cryptogams/HEAD/arm/chacha-armv8.pl>
  - <https://raw.githubusercontent.com/dot-asm/cryptogams/HEAD/riscv/poly1305-riscv.pl>
  - <https://raw.githubusercontent.com/dot-asm/cryptogams/HEAD/riscv/chacha-riscv.pl>
  - <https://raw.githubusercontent.com/openssl/openssl/master/crypto/sha/asm/sha1-x86_64.pl>
  - <https://raw.githubusercontent.com/openssl/openssl/master/crypto/poly1305/asm/poly1305-x86_64.pl>
  - <https://raw.githubusercontent.com/torvalds/linux/master/lib/crypto/x86/poly1305-x86_64-cryptogams.pl>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/dot-asm/cryptogams`) · [data/wave13/enrich/raw/github_com_dot_asm_cryptogams.json](../../../data/wave13/enrich/raw/github_com_dot_asm_cryptogams.json) (enrichment confidence 0.8)

</details>
