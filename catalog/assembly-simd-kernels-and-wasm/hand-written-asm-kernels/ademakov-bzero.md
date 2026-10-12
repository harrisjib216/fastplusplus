# ademakov/bzero

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Assembly (x86 SSE/AVX, GNU as) with C test harness` · `Unlicense` · 🔴 abandoned

> Public-domain x86-64 SSE and AVX assembly zero-fill routines that beat 2017-era libc memset on small buffers.

| | |
|---|---|
| **Beats** | libc memset (bzero_0 in the harness) and the author's trivial and unrolled C versions compiled with gcc -O2 |
| **Claimed result** | Core i7-4850HQ (total microseconds for 10,000 calls): 32 B bzero_6 26 / bzero_7 23 vs memset 86 (3.3x / 3.7x, derived from page data); 64 B 26 vs 70 (2.7x, derived from page data); 256 B 51 vs 82 (1.6x, derived from page data); 1024 B 189 vs 149 and 2048 B 393 vs 241 (memset faster). Xeon E5520 (no AVX): 64 B 47 vs 71, 256 B 79 vs 127, 1024 B 265 vs 317, 2048 B bzero_6 655 / bzero_7 552 vs memset 664. The README Update says newer AVX versions (bzero_9..bzero_H, added 2019) are 'faster than memset() for any memory size', but no tables or numbers are given for them. |
| **Workload** | Time to clear buffers of 0 to 2048+ bytes by size, comparing libc memset, trivial/unrolled C, SSE intrinsics, rep stosb, and hand-written SSE/AVX assembly versions. |
| **Metric** | latency |
| **Hardware** | Intel Xeon E5520 @ 2.27 GHz (no AVX) and Intel Core i7-4850HQ @ 2.30 GHz (AVX) |
| **Compiler and flags** | gcc at default -O0 (Makefile sets CC=gcc, no CFLAGS) for the C baselines and the bzero_0 memset wrapper; GNU as for the assembly variants |
| **Adoption** | 1 star |
| **Last commit** | 2019-05-04 |
| **Links** | [repository](https://github.com/ademakov/bzero) · [benchmark](https://raw.githubusercontent.com/ademakov/bzero/HEAD/README.md) |

## Verdict

In 2017 single-run hot-cache loops of 10,000 calls (totals in microseconds, harness built with no -O flag), the SSE assembly bzero_7 took 23 us at 32 B against 86 us for libc memset (about 3.7x, derived) and 26 vs 70 us at 64 B on an i7-4850HQ, but memset won from 1 KiB up there (2048 B: 241 vs 392 us); on a Xeon E5520 without AVX the assembly led by smaller margins at most sizes (single-run outliers such as bzero_7 at 15 B, 149 vs 75 us, go the other way; 2048 B: bzero_7 552 and bzero_6 655 vs memset 664). Libc version and OS were not stated, and the 2019 AVX variants that the README calls faster than memset at every size have no published numbers.

## Use it when

- Hot paths that zero many small buffers (roughly 8 to 512 bytes) whose size is only known at run time, on x86-64 with SSE2 or AVX.
- Projects that want a tiny, public-domain zeroing routine to read, vendor and benchmark on their own CPU and libc rather than a full mem\* library.
- Studying small-size memset techniques (bit-ladder tails versus overlapping stores) side by side with a ready harness that checks every byte and the padding around it.

## Skip it when

- Buffers of about 1 KiB and up on the AVX laptop: libc memset won at 1024 B (149 vs 189 us) and 2048 B (241 vs 392 us), and nothing above 8 KiB was ever measured; there are no non-temporal stores, no rep stosb path and no destination alignment for large clears.
- Constant small sizes: compilers already inline memset(p, 0, N) for fixed N into a few stores, which an out-of-line assembly call cannot beat, and the compiler can no longer elide or merge the clear.
- Windows x64, 32-bit x86, ARM or any non-System-V ABI: the code takes its arguments in rdi and rsi and uses AT&T syntax for GNU as; only the Apple symbol prefix is handled.
- Any setting that needs a modern baseline: the only tables are from 2017 on 2009 and 2013 CPUs with an unstated libc; current glibc memset (AVX2 and EVEX paths with overlapping small-size stores) uses the same tricks, and the 2019 AVX variants have no published numbers at all.
- Code that needs a maintained, tested library: 1 star, no tests beyond the harness, inactive since May 2019.

## How it is fast

The SSE versions clear 64 bytes per loop iteration with four unaligned 16-byte movdqu stores, then finish the tail with a test-and-branch ladder on the size bits (32, 16, 8, 4, 2, 1) instead of a byte loop. The 2019 AVX versions (bzero_G, bzero_H) use 32-byte vmovdqu stores and the overlapping-store trick for small sizes and tails: two stores, one at the start and one ending exactly at s + n, cover any length in a size class (0-3, 4-7, 8-15, 16-31, 32-63) without a loop. Because the value is always zero, no byte broadcast is needed, and nothing aligns the destination.

## Compared with alternatives

Pick it over asmlib (abiiranathan), which measures its memset against glibc 2.44 on a current CPU, only when you want a single public-domain zeroing routine of a few dozen lines to vendor and re-benchmark; FastMemcpy covers copies, not clears, and the Pico SDK pico_mem_ops and rt_memcpy_cm target Cortex-M rather than x86-64.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (GNU as through the gcc or clang driver, C preprocessor for the .S files) |
| **Minimum toolchain** | GNU as compatible assembler (gcc or clang driver for .S files); the harness needs a C99 compiler; not documented beyond that |
| **Platforms** | x86-64 System V ABI (Linux, BSD, macOS); bzero6.S to bzero8.S need SSE2, bzero9.S to bzeroH.S need AVX |
| **Thread safety** | Reentrant by construction: each function touches only the destination buffer and caller-saved registers (rax, rdx, rsi, rdi, xmm0/ymm0) and keeps no global state; not documented by the author. |
| **Drop-in for the baseline** | partial - zero-fill only, with no fill value and no return value, so it replaces bzero(p, n) or memset(p, 0, n) calls but not memset in general, and the compiler no longer treats the call as memset |

## Gotchas

- Harness flaws behind the 2017 tables (main.c at commit 1db9138 produced them): the Makefile sets CC=gcc with no CFLAGS, so make builds at gcc's default -O0, and the trivial C loop's 2048 B time (49,821 us per 10,000 calls on the 2.27 GHz Xeon, about 5.5 cycles per byte, derived) is the speed of an unoptimised byte loop; at -O0 memset is also reached through an unoptimised bzero_0 wrapper plus a PLT jump that the assembly versions, called directly through the function pointer, do not pay, which inflates memset's small-size totals (23-86 us) where a few cycles per call matter. There is no warm-up: the first size of each series (0 B) is inflated (memset 112 vs 78 us at 1 B; bzero_5 230 on the Xeon), and the run is single-shot with gettimeofday (1 us resolution).
- The destination is always data + 32 in a static array (at least 16-byte aligned), the same size is repeated 10,000 times (perfectly predicted branches) and the buffer is hot in L1, so misaligned destinations, mixed sizes and cold memory, where unaligned 32-byte stores split cache lines and libc's alignment and rep stosb paths pay off, were never measured.
- The .S files have no .note.GNU-stack section, so GNU ld 2.39+ warns 'missing .note.GNU-stack section implies executable stack' and marks the stack executable unless you link with -z noexecstack or assemble with -Wa,--noexecstack; they also carry no CFI or .type/.size directives, so profilers and debuggers see bare symbols.
- The AVX variants (bzero9.S to bzeroH.S) return after 256-bit vmovdqu stores without vzeroupper, which compilers and glibc's AVX2 memset emit to avoid AVX-SSE transition costs in following legacy-SSE code; the harness calls them back to back with no SSE code in between, so any such cost to the caller would not show. The i7-4850HQ is a MacBook Pro part and the files carry __APPLE__ guards, so the laptop table may be macOS libc memset and Apple clang invoked as gcc rather than glibc; the README does not say.

## Known shortcomings

- Downgraded A to C: README numbers match but the 2017 runs' flags are unstated (the 2017 Makefile has no CFLAGS, so gcc default -O0; the README only implies -O2), no gcc or glibc version, single-run microsecond totals over 10,000 calls; memset is faster at 1024 B and up on the i7-4850HQ; the 2019 AVX versions have no numbers.
- Enricher: the README tables (commit 1db9138) come from a Makefile with CC=gcc and no CFLAGS, so the C baselines ran at -O0 (about 5.5 cycles per byte for the trivial loop, derived) and memset went through an unoptimised bzero_0 wrapper plus a PLT jump while the assembly versions were called directly; no warm-up (the first 0 B size is inflated), a single gettimeofday run, aligned hot-L1 buffers and nothing above 8 KiB; the AVX variants return without vzeroupper and the .S files lack .note.GNU-stack; the laptop rows (i7-4850HQ) may have used macOS libc. Caveat corrections recorded in retier-03; tier C stays.

## Caveats and trade-offs

Units derived from main.c: each figure is the total gettimeofday time in microseconds for 10,000 calls on the same buffer (so 23 vs 26 is within 1 us timer noise; about 2.3-2.6 ns per call); one run per size, hot cache, same size every call (branch-friendly). Published tables come from the 2017 harness (the current main.c prints a different size list) on 2009/2013 CPUs with an unstated glibc; author notes stock memset is 'sometimes unreasonably bad for small buffer sizes' there, which modern glibc ERMS/AVX2/EVEX memset paths likely fixed. Memset wins at 1024 B and 2048 B on the AVX laptop. The 2019 AVX versions have no published numbers; AVX-512 untested. Unlicense (public-domain dedication, no patent grant). [retier] C baselines built at -O0; memset reached through an unoptimised wrapper plus PLT while the assembly routines are called directly; single run, no warm-up, aligned hot-L1 buffers up to 8 KiB only; AVX variants lack vzeroupper; .S files lack .note.GNU-stack; laptop rows may have used macOS libc

Strong only for small sizes and the SSE versions; the author concludes stock memset is better for large buffers when it can use AVX/AVX2. Public-domain dedication gives no patent grant.

## Maintenance

Inactive since May 2019 (1 star) but Unlicense public domain and each routine is one short file, so it is easy to vendor; re-benchmark against your current libc before adopting, and add a .note.GNU-stack section when linking with modern GNU ld.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** README tables compare hand-written SSE assembly (bzero6.S, bzero7.S) against libc memset (bzero_0 in bzero.c) using the public harness main.c on named CPUs (Xeon E5520, i7-4850HQ), and every number in claimed_speedup matches. Not A: the build flags for the published 2017 runs are not stated (the 2017 Makefile at e807b1d sets no CFLAGS, i.e. gcc's default -O0; the current Makefile adds only -march=native; the README merely says only 'gcc -O2' works as expected), and the gcc and glibc versions are not given.
- **Verifier notes:** Numbers verified exactly; downgraded A to C because the flags and compiler/glibc versions behind the 2017 tables are not stated (2017 Makefile builds at gcc default -O0 while the README implies -O2). Shortcomings: tiny single-run microsecond totals, old CPUs and glibc, memset faster at 1 KiB and up on AVX, newest AVX variants unmeasured; 1 star.
- **Fields the verifier corrected:** `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-29 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ademakov/bzero/HEAD/README.md>
  - <https://raw.githubusercontent.com/ademakov/bzero/HEAD/Makefile>
  - <https://raw.githubusercontent.com/ademakov/bzero/HEAD/main.c>
  - <https://raw.githubusercontent.com/ademakov/bzero/HEAD/bzero.c>
  - <https://raw.githubusercontent.com/ademakov/bzero/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ademakov/bzero/e807b1d/main.c>
  - <https://github.com/ademakov/bzero>
  - <https://github.com/ademakov/bzero/commits>
  - <https://github.com/ademakov/bzero/commits/master/Makefile>
  - <https://github.com/ademakov/bzero/blob/e807b1d/Makefile>
- **Sources the enricher read:**
  - <https://github.com/ademakov/bzero>
  - <https://github.com/ademakov/bzero/commits/master>
  - <https://raw.githubusercontent.com/ademakov/bzero/HEAD/README.md>
  - <https://raw.githubusercontent.com/ademakov/bzero/HEAD/Makefile>
  - <https://raw.githubusercontent.com/ademakov/bzero/HEAD/main.c>
  - <https://raw.githubusercontent.com/ademakov/bzero/HEAD/bzero.c>
  - <https://raw.githubusercontent.com/ademakov/bzero/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ademakov/bzero/HEAD/bzero6.S>
  - <https://raw.githubusercontent.com/ademakov/bzero/HEAD/bzero7.S>
  - <https://raw.githubusercontent.com/ademakov/bzero/HEAD/bzero8.S>
  - <https://raw.githubusercontent.com/ademakov/bzero/HEAD/bzero9.S>
  - <https://raw.githubusercontent.com/ademakov/bzero/HEAD/bzeroA.S>
  - <https://raw.githubusercontent.com/ademakov/bzero/HEAD/bzeroB.S>
  - <https://raw.githubusercontent.com/ademakov/bzero/HEAD/bzeroC.S>
  - <https://raw.githubusercontent.com/ademakov/bzero/HEAD/bzeroD.S>
  - <https://raw.githubusercontent.com/ademakov/bzero/HEAD/bzeroE.S>
  - <https://raw.githubusercontent.com/ademakov/bzero/HEAD/bzeroF.S>
  - <https://raw.githubusercontent.com/ademakov/bzero/HEAD/bzeroG.S>
  - <https://raw.githubusercontent.com/ademakov/bzero/HEAD/bzeroH.S>
  - <https://raw.githubusercontent.com/ademakov/bzero/e807b1d/main.c>
  - <https://raw.githubusercontent.com/ademakov/bzero/e807b1d/Makefile>
  - <https://raw.githubusercontent.com/ademakov/bzero/e807b1d/bzero.c>
  - <https://raw.githubusercontent.com/ademakov/bzero/1db9138/main.c>
  - <https://raw.githubusercontent.com/ademakov/bzero/1db9138/Makefile>
  - <https://raw.githubusercontent.com/ademakov/bzero/1db9138/bzero.c>
  - <https://raw.githubusercontent.com/ademakov/bzero/1db9138/README.md>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/ademakov/bzero`) · [data/wave13/enrich/raw/github_com_ademakov_bzero.json](../../../data/wave13/enrich/raw/github_com_ademakov_bzero.json) (enrichment confidence 0.75)

</details>
