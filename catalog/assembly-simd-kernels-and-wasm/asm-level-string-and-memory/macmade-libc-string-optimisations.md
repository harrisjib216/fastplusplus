# LibC-String-Optimisations (XEOS x86 and x86-64 string functions)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Assembly (x86, x86-64) with C tests` · `XEOS Software License 1.0 (custom BSD-style licence with an advertising clause and a clause forbidding combination or linking with GPL/LGPL software; not OSI-approved)` · 🔴 abandoned

> Hand-written SSE2/SWAR x86 and x86-64 assembly strlen, memchr, memcpy, memset, strcat for Mach-O; mostly 1-15% over OS X 10.9 libc.

| | |
|---|---|
| **Beats** | OS X 10.9 libc strlen, memset, memchr, memcpy, strcat (the README notes it is also heavily optimised); not glibc or musl |
| **Claimed result** | 64-bit: strlen 0.527532 s vs 0.531318 s OS X (under 1%); memset 0.778556 s vs 0.906685 s; memchr 0.476380 s vs 0.516240 s; memcpy 0.858043 s vs 0.928405 s; strcat 1.269549 s vs 1.314561 s. 32-bit: memchr 0.532130 s vs 6.374186 s (about 12x against OS X's 32-bit memchr). The README's misaligned strcat rows (64-bit 1.423539 s vs 3.920867 s, 32-bit 1.515425 s vs 4.644904 s) are struck: strcat-test.c never resets t1 before the misaligned libc loop, so the libc figure also counts the aligned libc, aligned XEOS and xeos_strcat_c loops (a stub at README commit 7e40015); subtracting the aligned rows leaves at most 1.34 s for OS X misaligned in 64-bit against XEOS 1.42 s (XEOS about 6% slower) and 1.64 vs 1.52 s in 32-bit (about 8% faster) (derived from page data). Loses: misaligned memcpy 1.408296 s vs OS X 1.218205 s (64-bit) and 1.457572 s vs 1.446217 s (32-bit). |
| **Workload** | 10,000,000 calls per function: strlen on 1000 chars, memset 4096 B, memchr 1000 B searching last char, memcpy 4096 B (aligned and misaligned), strcat on 1000 chars; 32-bit and 64-bit builds. |
| **Metric** | throughput |
| **Compiler and flags** | Makefile: kernels are hand-written assembly assembled with yasm (-f macho64 / -f macho); test harnesses built with clang -Weverything -fpic -target x86_64-apple-darwin or i386-apple-darwin and no optimisation flag (harness loops at -O0). Compiler versions not stated. |
| **Adoption** | 7 stars |
| **Last commit** | 2017-01-11 |
| **Links** | [repository](https://github.com/macmade/LibC-String-Optimisations) · [benchmark](https://github.com/macmade/LibC-String-Optimisations/blob/master/README.md) |

## Verdict

The README is first-party: OS X 10.9 libc as the baseline, CPU and compiler versions not stated, one run per row, harness at -O0, 10M calls per row. In 64-bit, XEOS took 0.7% less time on strlen of 1,000 characters, 14% less on 4 KiB memset, 7.7% less on 1,000-byte memchr, 7.6% less on aligned 4 KiB memcpy and 3.4% less on aligned strcat, and 15.6% more on misaligned memcpy. The 12x 32-bit memchr gain is against OS X's slow 32-bit memchr. The 2.8x/3.1x misaligned strcat gains are a timing bug; corrected they are about 0.94x in 64-bit and 1.08x in 32-bit (derived from page data).

## Use it when

- As a short, heavily commented reference for classic SSE2 string scanning (aligned-down load, leading-byte mask, pcmpeqb/pmovmskb/bsf) and SWAR fallbacks, in both 32-bit and 64-bit NASM/yasm syntax.
- In freestanding x86 kernels or hobby OSes without a libc that need small, dependency-free memchr, strlen or memset on pre-AVX hardware, and only if the XEOS licence terms are acceptable.
- In 32-bit x86 code on old OS X, where the system memchr was the slow one: 0.53 s vs 6.37 s for 10M scans of 1,000 bytes in the README.

## Skip it when

- On any current libc target. The baseline is the 2013 OS X 10.9 libc, the aligned 64-bit wins are 0.7-14% less time, and the project has no AVX or ERMS paths.
- For misaligned memcpy: it is slower than OS X in both builds (1.408 vs 1.218 s in 64-bit, 1.458 vs 1.446 s in 32-bit).
- In GPL/LGPL projects or anywhere an OSI licence is required. Clause 3 of the XEOS Software License 1.0 (printed in the Makefile header) forbids combining or linking the code with GNU-licensed software, and clause 4 requires an advertising acknowledgement.
- On Linux/ELF or Windows: it is built with yasm -f macho/macho64, uses leading-underscore symbol names and the System V register convention, so it needs porting.
- In production code in general: the README badge says prototype, the last code commit is from 2014, and the tests only print pointers and strings without comparing them to libc.

## How it is fast

On the first call each function runs CPUID and caches SSE2 support in a global. The SSE2 path aligns the pointer down to 16 bytes, masks the leading bytes with a shifted all-ones mask, and then scans with pcmpeqb + pmovmskb + bsf. strlen checks one 16-byte block per iteration; memchr broadcasts the byte with punpcklbw/pshufd and unrolls 4x16 bytes. memcpy copies 128-, 64- and 16-byte blocks through eight xmm registers (movdqa when both pointers are aligned, movdqu loads otherwise), and memset stores 16-byte movdqa blocks. The non-SSE2 fallbacks use the SWAR has-zero-byte bit trick on 4- or 8-byte words. There is no AVX, no non-temporal store and no rep movsb/stosb.

## Compared with alternatives

Agner Fog's asmlib covers the same functions plus memmove and strcpy, for 32- and 64-bit, with published cycles-per-byte comparisons against glibc and Darwin libraries; fancy-memset and the Arm Optimized Routines cover modern memset and Arm targets. Pick XEOS only as a compact SSE2/SWAR teaching reference, or for a pre-AVX freestanding x86 project that can accept the anti-GPL licence clause.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none at run time; yasm to assemble (vendored under software-deps/yasm), clang for the test harnesses |
| **Minimum toolchain** | yasm with Mach-O output (-f macho / -f macho64); clang targeting x86_64-apple-darwin and i386-apple-darwin; versions not documented |
| **Platforms** | x86 (i386) and x86-64 macOS (Mach-O, System V AMD64 calling convention); the SSE2 path runs when CPUID reports SSE2, a scalar SWAR path otherwise |
| **Thread safety** | Not documented. The functions keep no state except the lazily written __SSE2Status flag, which the first call sets without synchronisation; every thread writes the same value. |
| **Drop-in for the baseline** | partial: the signatures match libc but the symbols are exported as xeos_\* and the code is Mach-O only. Every object file also defines its own global __SSE2Status, so linking two of them together gives a duplicate-symbol error unless edited. |

## Gotchas

- Harness flaw behind the headline strcat wins. strcat-test.c never resets t1 before the misaligned libc loop, so 'OS X strcat (misaligned)' = t2 - t1 also includes the aligned libc loop, the aligned XEOS loop and the xeos_strcat_c loop. In commit 7e40015, where these README numbers were added, xeos_strcat_c was a stub that returned at once. Subtracting the aligned rows leaves at most 3.920867 - 1.314561 - 1.269549 = 1.34 s for OS X misaligned in 64-bit, against XEOS 1.42 s (XEOS about 6% slower). In 32-bit it leaves 4.644904 - 1.653358 - 1.349833 = 1.64 s, against XEOS 1.52 s (about 8% faster). Both are derived from page data. So the 2.8x and 3.1x 'Best result (!!!)' rows are a timing artifact, and the bug is still on master.
- The README numbers do not come from today's harness. After they were taken, e1e9b3e (2013-08-19) changed the strcat strings from 1000 to 1024 characters and replaced the C reference with real code. Each harness runs twice (SSE2 pass, then the non-SSE2 path) and the README does not say which pass it quotes. Each row is one gettimeofday interval at -O0, and the libc loop always runs first with no warm-up. The libc calls go through dyld stubs while the xeos_\* calls are direct, so the 0.38 ns-per-call strlen margin is noise.
- xeos_memchr compares the remaining length with signed jumps (jle). Any n of 2^63 or more, including the memchr(p, c, SIZE_MAX) idiom, returns NULL even when the byte is present.
- The C fallback xeos_strcat_c on master handles only an aligned destination end: after the source-alignment bytes, its misaligned branch writes at most one word's worth of bytes and then NUL-terminates, which truncates the result (commit message: 'aligned pointers only for the moment'). The harnesses declare `extern int _SSE2Status` although the 64-bit objects define a quadword.

## Known shortcomings

- Harness built with no -O flag; OS X 10.9 baseline; gains mostly 1-15% with a 32-bit misaligned memcpy loss; no CPU stated. Licence is the XEOS Software License 1.0 (non-OSI, anti-GPL clause), reference only.
- Harness flaw: strcat-test.c never resets t1 before the misaligned libc loop, so the 'OS X strcat (misaligned)' row also counts the aligned libc, aligned XEOS and xeos_strcat_c loops (xeos_strcat_c was a stub at README commit 7e40015); corrected (derived from page data), 64-bit OS X misaligned is at most 1.34 s vs XEOS 1.42 s (XEOS about 6% slower) and 32-bit 1.64 vs 1.52 s (about 8% faster), so the 2.8x/3.1x strcat wins are artifacts. xeos_memchr compares the length with signed jumps, so n &gt;= 2^63 (the SIZE_MAX idiom) returns NULL; every .o defines a global __SSE2Status, so two objects linked together give a duplicate symbol; xeos_strcat_c truncates on a misaligned destination.

## Caveats and trade-offs

First-party numbers from the README only; the CPU, compiler versions and run count are not stated, and the baseline is the 2013-era OS X 10.9 libc rather than glibc. Each test harness runs the loop twice (SSE2 path, then the non-SSE2 path with _SSE2Status = 0) and the README does not say which pass it quotes. Harness C files are built without an -O flag, so loop overhead is unoptimised (it applies equally to both sides). Wins on most rows are 1-15%; the 12x memchr gain is against OS X's 32-bit memchr and the 2.8-3x strcat gains only on misaligned input. XEOS loses on misaligned memcpy in both 32-bit and 64-bit builds. The strlen margin is under 1% (0.527532 s vs 0.531318 s). README badge says status 'prototype'; macOS/Mach-O build only (yasm macho targets). Custom XEOS licence forbids linking with GPL/LGPL code, so it is reference only. [retier] First-party numbers from the README only; CPU, compiler versions and run count are not stated, and the baseline is the 2013-era OS X 10.9 libc rather than glibc. The misaligned strcat rows are artifacts of a timer never reset (struck from the claim). The README numbers do not come from today's harness: e1e9b3e (2013-08-19) changed the strcat strings from 1000 to 1024 characters and replaced the stub C reference with real code. Each harness runs the loop twice (SSE2 pass, then the non-SSE2 path) and the README does not say which pass it quotes; each row is one gettimeofday interval at -O0 with the libc loop always first and no warm-up; the libc calls go through dyld stubs while the xeos_\* calls are direct. Wins on the remaining rows are 1-15%, with the 12x memchr gain against OS X's 32-bit memchr; XEOS loses on misaligned memcpy in both builds. Code bugs: xeos_memchr compares the remaining length with signed jumps, so n &gt;= 2^63 (the memchr(p, c, SIZE_MAX) idiom) returns NULL even when the byte is present; every .o defines a global __SSE2Status, so linking two objects gives a duplicate symbol; the C fallback xeos_strcat_c truncates on a misaligned destination ('aligned pointers only for the moment').

x86 and x86-64 assembly only; SSE2 versions used when the CPU supports them, slower fallbacks otherwise. Developed for the XEOS operating system; README status badge says prototype. License is the XEOS Software License (README badge and text); no LICENSE file found at the repo root, and its terms were not verified, so treated as reference.

## Maintenance

Abandoned prototype: the last code commit is from 2014 (YASM build), the last README edit 2017-01-11, with 7 stars and one open feature request. It is usable only as a reference, because of the custom XEOS licence (anti-GPL and advertising clauses, no LICENSE file) and Mach-O-only builds, and its headline strcat numbers come from a timing bug.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README timings against the OS X 10.9 libc with public test harnesses (source/\*-test.c) and a Makefile, but no CPU model, no compiler version, and the harness is built without any -O flag; not A or B.
- **Verifier notes:** Numbers match the README; added the 32-bit misaligned memcpy loss and strcat rows. Record shortcomings: OS X 10.9 libc baseline, no hardware or compiler versions, mostly 1-15% gains, prototype status, non-OSI XEOS licence with an anti-GPL clause.
- **Fields the verifier corrected:** `license`, `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-34 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/macmade/LibC-String-Optimisations/blob/master/README.md>
  - <https://raw.githubusercontent.com/macmade/LibC-String-Optimisations/master/README.md>
  - <https://raw.githubusercontent.com/macmade/LibC-String-Optimisations/master/Makefile>
  - <https://raw.githubusercontent.com/macmade/LibC-String-Optimisations/master/source/memchr-test.c>
  - <https://raw.githubusercontent.com/macmade/LibC-String-Optimisations/master/source/strcat-test.c>
  - <https://github.com/macmade/LibC-String-Optimisations>
  - <https://github.com/macmade/LibC-String-Optimisations/commits>
- **Sources the enricher read:**
  - <https://github.com/macmade/LibC-String-Optimisations>
  - <https://github.com/macmade/LibC-String-Optimisations/tree/master/source>
  - <https://github.com/macmade/LibC-String-Optimisations/tree/master/software-deps>
  - <https://github.com/macmade/LibC-String-Optimisations/commits/main>
  - <https://github.com/macmade/LibC-String-Optimisations/commits/master>
  - <https://github.com/macmade/LibC-String-Optimisations/issues>
  - <https://raw.githubusercontent.com/macmade/LibC-String-Optimisations/master/README.md>
  - <https://raw.githubusercontent.com/macmade/LibC-String-Optimisations/master/Makefile>
  - <https://raw.githubusercontent.com/macmade/LibC-String-Optimisations/master/.travis.yml>
  - <https://raw.githubusercontent.com/macmade/LibC-String-Optimisations/master/software-deps/Makefile>
  - <https://raw.githubusercontent.com/macmade/LibC-String-Optimisations/master/source/strcat-test.c>
  - <https://raw.githubusercontent.com/macmade/LibC-String-Optimisations/master/source/strcat.c>
  - <https://raw.githubusercontent.com/macmade/LibC-String-Optimisations/master/source/strcat.64.s>
  - <https://raw.githubusercontent.com/macmade/LibC-String-Optimisations/master/source/memchr-test.c>
  - <https://raw.githubusercontent.com/macmade/LibC-String-Optimisations/master/source/memchr.64.s>
  - <https://raw.githubusercontent.com/macmade/LibC-String-Optimisations/master/source/memcpy-test.c>
  - <https://raw.githubusercontent.com/macmade/LibC-String-Optimisations/master/source/memcpy.64.s>
  - <https://raw.githubusercontent.com/macmade/LibC-String-Optimisations/master/source/memset-test.c>
  - <https://raw.githubusercontent.com/macmade/LibC-String-Optimisations/master/source/memset.64.s>
  - <https://raw.githubusercontent.com/macmade/LibC-String-Optimisations/master/source/strlen-test.c>
  - <https://raw.githubusercontent.com/macmade/LibC-String-Optimisations/master/source/strlen.64.s>
  - <https://raw.githubusercontent.com/macmade/LibC-String-Optimisations/master/source/strchr-test.c>
  - <https://raw.githubusercontent.com/macmade/LibC-String-Optimisations/master/source/strchr.64.s>
  - <https://raw.githubusercontent.com/macmade/LibC-String-Optimisations/master/source/memchr.32.s>
  - <https://raw.githubusercontent.com/macmade/LibC-String-Optimisations/7e40015/README.md>
  - <https://raw.githubusercontent.com/macmade/LibC-String-Optimisations/7e40015/source/strcat-test.c>
  - <https://raw.githubusercontent.com/macmade/LibC-String-Optimisations/7e40015/source/strcat.c>
  - <https://raw.githubusercontent.com/macmade/LibC-String-Optimisations/e1e9b3e/source/strcat-test.c>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/macmade/libc-string-optimisations`) · [data/wave13/enrich/raw/github_com_macmade_libc_string_optimisations.json](../../../data/wave13/enrich/raw/github_com_macmade_libc_string_optimisations.json) (enrichment confidence 0.85)

</details>
