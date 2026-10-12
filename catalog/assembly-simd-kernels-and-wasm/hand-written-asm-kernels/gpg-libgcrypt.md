# libgcrypt (assembly for x86, ARM, PowerPC)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C with assembly (cipher/ directory)` · `LGPL-2.1 (library, COPYING.LIB); GPL-2.0 for helper programs and documentation (COPYING)` · 🟢 active

> GnuPG's crypto library with runtime-dispatched x86, ARM, PowerPC, s390x and RISC-V assembly; each new kernel beats libgcrypt's previous path.

| | |
|---|---|
| **Beats** | libgcrypt's own previous implementation of the same primitive, which differs per row: earlier assembly paths for several rows (VAES/AVX512 AES is measured against libgcrypt's VAES/AVX2 assembly; AES-NI XTS against earlier AES-NI code; SHA-NI SHA-1 against the previous SHA-1 path), generic C for others; NEWS does not say which |
| **Claimed result** | NEWS 1.9.0 (2021-01-19): Intel SHA extension for SHA-1 and SHA-256 '(4.0/3.7 times faster)'; AES-NI AES-XTS '(6 times faster)'; ARMv8/CE AES-XTS '(2.5 times faster)'; AVX/AVX2 Blake-2 '(1.3/1.4 times faster)'; i386/SSSE3 SHA-512 '(4.5 times faster on Ryzen 7)'; ARMv8/CE PMULL CRC '(7 times faster)'; ARMv7/NEON GCM '(3 times faster)'; CAST5 40-70% and Blowfish 60-80% faster. NEWS 1.12.0 (2026-01-29): VAES/AVX512 AES 'boosts OCB performance by about 2 times on AMD Zen5'. Commit 9e3af928ee: Ryzen 9 9950X3D OCB enc 0.030 to 0.016 ns/B (32298 to 61035 MiB/s) against the VAES/AVX2 path, no change on Zen4. Commit d02958bd30: SHA-1 on Celeron J3455 4.50 to 1.11 ns/B (211.7 to 858.1 MiB/s, '4.0x faster'). |
| **Workload** | symmetric crypto, hashing and checksum kernels listed in the NEWS 'Performance' bullets |
| **Metric** | throughput |
| **Hardware** | NEWS: Ryzen 7 (SHA-512 row) and AMD Zen5 (OCB row); commit messages: Intel Celeron J3455 1500 MHz no turbo (SHA-1 SHA-NI, d02958bd30), AMD Ryzen 9 9950X3D, Ryzen 9 7900X and Intel Core i3-1115G4 (VAES/AVX512, 9e3af928ee); other rows not checked |
| **Adoption** | 281 stars (GitHub mirror; maintainers do not track it) |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/gpg/libgcrypt) · [benchmark](https://github.com/gpg/libgcrypt/blob/master/NEWS) |

## Verdict

Every figure is a first-party before/after table in the ns/B, MiB/s, c/B format of libgcrypt's tests/bench-slope (which takes the median of 64 runs per buffer size and reports the linear-regression slope over 16 to 4112-byte buffers; the commits do not name the tool) comparing a new kernel with the library's previous code path on one CPU, compiler and flags unstated: SHA-1 SHA-NI 4.50 to 1.11 ns/B against the previous SHA-1 assembly on a Celeron J3455 at 1.5 GHz; AES-XTS 1.66 to 0.270 ns/B on an i7-4790K at 4.0 GHz against the generic XTS mode code; i386 SSSE3 SHA-512 12.58 to 2.78 ns/B on a Ryzen 7 3700X; ARMv8 CE PMULL CRC32 2.89 to 0.341 ns/B on a Cortex-A53 at 1104 MHz; VAES/AVX512 AES OCB 0.030 to 0.016 ns/B on a Ryzen 9 9950X3D against the VAES/AVX2 assembly, with no gain on Zen4 or Tiger Lake. None of this compares against OpenSSL or another library.

## Use it when

- You already link libgcrypt (GnuPG, systemd, cryptsetup-style stacks) and want the vector paths: upgrade to 1.12.x to get VAES/AVX512 AES (about 2x OCB/ECB/CBC-decrypt on Zen5) and AVX2/AVX512 CRC and GHASH.
- Bulk symmetric work on large buffers (disk encryption with AES-XTS, OCB/GCM/GCM-SIV streams, Camellia or SM4) where parallel modes can use the 4-to-16-block kernels.
- SHA-1/SHA-256 on x86 CPUs with the SHA extensions (SHA-NI): the SHA-NI path measured 4.0x over libgcrypt's previous SHA-1 assembly on a Celeron J3455 (sha1.c otherwise dispatches SSSE3, AVX, AVX-BMI2 or AVX2-BMI2 assembly; the commit does not name which ran before).
- Non-x86 targets that other libraries cover thinly: ARMv8 CE AES/GHASH/SHA/SM3/SM4/CRC, POWER8-10 vector crypto, s390x CPACF, RISC-V Zbb/Zbc and vector crypto.
- You need an LGPL C library with a FIPS 140-3 mode and service indicator.

## Skip it when

- Small messages and per-call latency: the commit tables use bench-slope-style ns/B slopes, which by construction exclude fixed per-call cost (key setup, handle open, finalization).
- Serial modes (CBC encrypt, CFB encrypt) and CPUs where the wide paths do not help: the VAES/AVX512 commit shows no gain for CBC/CFB encryption on Zen5 and roughly no change on Zen4 and Tiger Lake.
- Projects that cannot accept LGPL-2.1 linking terms or that want a small vendorable kernel; the library pulls in libgpg-error (1.56 or newer for current master) and an autotools build.
- Deployments that need the newest vector code to be battle-tested: the AVX-512 Poly1305 path (added in 1.11.0, 2024) and the POWER10 Poly1305 path produced wrong tags for crafted inputs until fixes on 2026-10-11, not yet in a release.
- If you want a C++ API or header-only use; libgcrypt is a C shared/static library with opaque handles.

## How it is fast

Per-architecture hand-written assembly (.S files such as rijndael-vaes-avx512-amd64.S, crc-armv8-aarch64-ce.S) and C files with inline asm (sha1-intel-shaext.c) for each primitive, selected at runtime from CPUID/hwcap feature bits (src/hwf-x86.c). Much of the mode speedup comes from 'bulk' functions that process 4 to 16 blocks per call so independent AES rounds pipeline (the AES-NI XTS 6x came from adding a 4-block bulk XTS path where XTS previously went through the generic mode code), plus carry-less multiply (PCLMUL/PMULL/VPMSUMD) folding for GHASH, POLYVAL and CRC. CPU-specific tuning flags steer around slow units, for example Zen5 is marked as having integer vector latency 2, so Blake2 drops its AVX/AVX2/AVX512 paths there.

## Compared with alternatives

Pick libgcrypt over Nettle when you need its wider mode and algorithm coverage with runtime-dispatched VAES/AVX512, SHA-NI and ARMv8 CE paths behind one library API; pick CRYPTOGAMS when you want individual perlasm kernels to embed without a library, or crc32-vpmsum when you only need a POWER8 CRC.

## Integration

| | |
|---|---|
| **Form** | shared lib (static also buildable) |
| **Dependencies** | libgpg-error (configure.ac requires 1.56 on master) |
| **Minimum toolchain** | Autoconf 2.69 / Automake 1.14 to build from git; a C compiler with GNU-style inline asm and an assembler that accepts the AVX512/VAES/SHA-NI mnemonics for those paths (configure probes each, e.g. HAVE_GCC_INLINE_ASM_AVX512) |
| **Platforms** | Generic C everywhere; assembly for x86-64 and i386 (SSSE3/AVX/AVX2/AVX512, AES-NI, VAES, SHA-NI, PCLMUL, GFNI), AArch64 and ARMv7 (NEON, ARMv8 CE, SVE), PowerPC (vector crypto, P10 LE), s390x, RISC-V (Zbb, Zbc, vector crypto); Windows via mingw cross build |
| **Thread safety** | Documented as thread-safe except functions that modify a shared handle (callers serialize those); gcry_check_version must run before other calls; fork without exec in pthread programs is warned against. |
| **Drop-in for the baseline** | partial: within libgcrypt the faster kernels are picked automatically with no API change; there is no drop-in for OpenSSL or other library APIs |

## Gotchas

- Correctness bugs in fast paths after release: commit 87714ba (2026-10-11) fixed a lost carry and dropped bit 130 in cipher/poly1305-amd64-avx512.S that gave wrong Poly1305 tags (ChaCha20-Poly1305 and Poly1305 MAC) for crafted inputs on CPUs with the HWF_INTEL_AVX512 feature set (Ice Lake class and later, Zen4/Zen5), shipped since 1.11.0; 3a7a156 the same day fixed a lost carry in poly1305-p10le.s. Neither fix is in a release yet (1.12.4 unreleased).
- The 1.9.0 release that carries most of the claimed speedups also shipped CVE-2021-3345, a heap overflow in _gcry_md_block_write introduced by e76617cb 'Reduce overhead on generic hash write function' (a performance change), fixed in 1.9.1; 1.9.2 fixed an input over-read in sha256-avx2-bmi2-amd64.S found by Guido Vranken.
- Speedups depend on the CPU: Blake2 AVX/AVX2/AVX512 (the 1.3/1.4x row) is now disabled on Zen5, ChaCha20 avoids vector code for single blocks on Zen5, and until b333d8a (2026-10-11) the Zen5 check used the wrong CPUID leaf so Zen6 would also get Zen5 tuning.
- Paths can be switched off per process with gcry_control(GCRYCTL_DISABLE_HWF, ...) before gcry_check_version, or system-wide in /etc/gcrypt/hwf.deny; --disable-asm drops all assembly, so check which features are active before comparing numbers.

## Known shortcomings

- NEWS figures only; many rows are measured against libgcrypt's own earlier assembly (the Zen 5 OCB 2x is AVX-512 against VAES/AVX2), not generic C; commit messages give CPU models (Celeron J3455, Ryzen 9 9950X3D) but no compiler or flags; the Poly1305 AVX-512 wrong-tag fix landed 2026-10-11. Licence LGPL-2.1 (tools GPL-2.0).
- Fast paths shipped correctness bugs: commit 87714ba (2026-10-11) fixed a lost carry and dropped bit 130 in cipher/poly1305-amd64-avx512.S that produced wrong Poly1305 tags on AVX-512 CPUs since 1.11.0 (3a7a156 fixed the same carry bug in poly1305-p10le.s); neither fix is released. The 1.9.0 release that carries most claimed rows also shipped CVE-2021-3345 from the perf commit e76617cb. Commit numbers are bench-slope ns/B (no per-call overhead), the baseline is libgcrypt's previous code (often already assembly), and the Blake2 AVX paths are now disabled on Zen5.

## Caveats and trade-offs

Release-note claims; the commit messages behind them give bench-slope before/after numbers and CPU models but never compiler or flags. The baseline is libgcrypt's previous code for the same primitive, often already assembly (the Zen5 OCB 2x is VAES/AVX512 against libgcrypt's own VAES/AVX2 assembly, and Zen4/Tigerlake see no gain), not a plain compiler build. Several rows are C with inline assembly or intrinsics (sha1-intel-shaext.c) rather than .S files. The i3-1115G4 table in commit 9e3af928ee has its before/after labels reversed. A correctness fix landed on 2026-10-11 in cipher/poly1305-amd64-avx512.S (lost carry and bit 130 in base 2^44 conversions gave wrong Poly1305 tags), not one of the claimed rows. GitHub repo is a mirror of dev.gnupg.org; maintainers do not track it. [retier] Release-note and commit-message claims with bench-slope ns/B numbers (per-call overhead excluded) and CPU models but no compiler or flags; the baseline is libgcrypt's previous code for the same primitive, often already assembly (Zen5 OCB 2x is VAES/AVX512 against libgcrypt's own VAES/AVX2 assembly; Zen4 and Tigerlake see no gain), not a plain compiler build. AES-XTS 6x was measured on an i7-4790K against generic XTS mode code. The i3-1115G4 table in commit 9e3af928ee has its before/after labels reversed. Blake2 AVX/AVX2/AVX512 paths (the 1.3/1.4x row) are now disabled on Zen5. Correctness: commit 87714ba (2026-10-11) fixed a lost carry and dropped bit 130 in cipher/poly1305-amd64-avx512.S that gave wrong Poly1305 tags on HWF_INTEL_AVX512 CPUs since 1.11.0, and 3a7a156 fixed the same carry bug in poly1305-p10le.s; neither fix is released (1.12.4 pending). The 1.9.0 release carrying most claimed rows shipped CVE-2021-3345 (heap overflow from perf commit e76617cb, fixed in 1.9.1) and 1.9.2 fixed an over-read in sha256-avx2-bmi2-amd64.S. The GitHub repo is an untracked mirror of dev.gnupg.org; paths can be disabled with GCRYCTL_DISABLE_HWF or /etc/gcrypt/hwf.deny.

Copyleft library (LGPL-2.1; helper programs and docs GPL); assembly per architecture selected at runtime; accelerated paths depend on CPU extensions (SHA-NI, AES-NI, VAES, ARMv8 CE).

## Maintenance

Very actively maintained (commits on 2026-10-11, releases through 1.12.3 in August 2026) on git.gnupg.org with the GitHub repository as an untracked mirror; LGPL-2.1 library that is copyable as a whole but hard to vendor kernel by kernel, and the newest AVX-512 and POWER10 Poly1305 paths carried wrong-tag bugs until 2026-10-11.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party release notes (NEWS 1.9.0 and 1.12.0) carry every quoted ratio; the linked commit messages add before/after bench-slope figures with CPU models (Celeron J3455 for SHA-NI SHA-1, Ryzen 9 9950X3D for VAES/AVX512 AES) but no compiler or flags, so first-party with partial methodology: C.
- **Verifier notes:** All quoted NEWS figures verified verbatim in NEWS 1.9.0 and 1.12.0; two commit messages checked for underlying numbers. Baseline corrected: several rows compare against libgcrypt's own earlier assembly, not generic C, so baseline_in_list is doubtful for those rows (left unchanged). Note the Poly1305 AVX-512 wrong-tag fix of 2026-10-11 as a quality shortcoming.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `hardware`, `license`, `last_commit`, `caveats`
- **Shortcomings recorded by:** verifier batch-71 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/gpg/libgcrypt>
  - <https://github.com/gpg/libgcrypt/commits/master>
  - <https://raw.githubusercontent.com/gpg/libgcrypt/HEAD/NEWS>
  - <https://raw.githubusercontent.com/gpg/libgcrypt/HEAD/README>
  - <https://github.com/gpg/libgcrypt/commit/9e3af928ee>
  - <https://github.com/gpg/libgcrypt/commit/d02958bd30>
  - <https://github.com/gpg/libgcrypt/commit/87714ba>
- **Sources the enricher read:**
  - <https://github.com/gpg/libgcrypt>
  - <https://github.com/gpg/libgcrypt/commits/master>
  - <https://raw.githubusercontent.com/gpg/libgcrypt/HEAD/NEWS>
  - <https://raw.githubusercontent.com/gpg/libgcrypt/HEAD/README>
  - <https://raw.githubusercontent.com/gpg/libgcrypt/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/gpg/libgcrypt/HEAD/cipher/poly1305.c>
  - <https://raw.githubusercontent.com/gpg/libgcrypt/HEAD/cipher/blake2.c>
  - <https://raw.githubusercontent.com/gpg/libgcrypt/HEAD/cipher/rijndael.c>
  - <https://raw.githubusercontent.com/gpg/libgcrypt/HEAD/cipher/sha1.c>
  - <https://raw.githubusercontent.com/gpg/libgcrypt/HEAD/src/hwf-x86.c>
  - <https://raw.githubusercontent.com/gpg/libgcrypt/HEAD/tests/bench-slope.c>
  - <https://raw.githubusercontent.com/gpg/libgcrypt/HEAD/doc/gcrypt.texi>
  - <https://github.com/gpg/libgcrypt/commit/9e3af928ee>
  - <https://github.com/gpg/libgcrypt/commit/d02958bd30>
  - <https://github.com/gpg/libgcrypt/commit/a00c5b2988>
  - <https://github.com/gpg/libgcrypt/commit/b52dde8609>
  - <https://github.com/gpg/libgcrypt/commit/14c8a593ed>
  - <https://github.com/gpg/libgcrypt/commit/87714ba>
  - <https://github.com/gpg/libgcrypt/commit/3a7a156>
  - <https://github.com/gpg/libgcrypt/commit/b333d8a>
  - <https://github.com/gpg/libgcrypt/commit/24af2a55d8>
  - <https://github.com/gpg/libgcrypt/commit/e76617cbab018dd8f41fd6b4ec6740b5303f7e13>
  - <https://github.com/gpg/libgcrypt/commits/master/cipher/blake2b-amd64-avx2.S>
  - <https://github.com/gpg/libgcrypt/commit/b2f78ae>
  - https://security-tracker.debian.org/tracker/CVE-2021-3345 (WebSearch snippet only)
  - https://dev.gnupg.org/T8514 (fetch failed: ENOTFOUND)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/gpg/libgcrypt`) · [data/wave13/enrich/raw/github_com_gpg_libgcrypt.json](../../../data/wave13/enrich/raw/github_com_gpg_libgcrypt.json) (enrichment confidence 0.65)

</details>
