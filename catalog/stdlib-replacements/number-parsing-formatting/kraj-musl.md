# musl

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Number parsing and formatting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Small MIT Linux libc; in one zig-built run its atoi (2.3x) and sprintf %f (1.2x) beat glibc, strtod loses 4.3x.

| | |
|---|---|
| **Beats** | glibc (atoi, strtok/strtok_r, bsearch, strrchr, sprintf) |
| **Claimed result** | musl vs glibc ns/op (third-party table, mixed result): atoi_parse 3.96 vs 9.28; strtok_r_parse 4.94 vs 14.76; strtok_parse 5.71 vs 15.23; strrchr 157.31 vs 354.19; bsearch_int 10.52 vs 16.02; sprintf_float 136.34 vs 160.56. Derived from page data: 2.3x, 3.0x, 2.7x, 2.3x, 1.5x and 1.2x faster. glibc is faster in 20 of the 32 rows (e.g. qsort_int 2.8x, strtod 4.3x, strstr 2.9x, malloc_free_small 11x, strncmp 37x), 3 rows tie. |
| **Workload** | 32 libc micro-benchmarks (ns per operation) built with zig cc for x86_64-linux-gnu and x86_64-linux-musl: e.g. atoi over 512 short decimal strings, strtok and strtok_r CSV splitting, bsearch on ints, strrchr, sprintf('%.6f') over 128 doubles. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 PRO 5850U, Linux 6.8.0-87-generic (Ubuntu 22.04), run dated 2025-11-18 |
| **Compiler and flags** | zig 0.15.2 (clang 20.1.2) 'zig cc' with -std=c11 -O3 -march=native -mtune=native -flto=full -fomit-frame-pointer -funroll-loops -DNDEBUG -fno-math-errno -fno-trapping-math -g0 -s, targets x86_64-linux-gnu and x86_64-linux-musl (run.sh) |
| **Adoption** | 400 stars (kraj/musl, a downstream mirror of the official musl git); benchmark repo 7 stars |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/kraj/musl) · [benchmark](https://github.com/fereidani/musl-vs-glibc) |

## Verdict

fereidani/musl-vs-glibc built one C file with zig 0.15.2 (clang 20.1.2, -O3 -march=native -flto=full) for the host's dynamic glibc (Ubuntu 22.04, probably 2.35) and zig's bundled static musl and ran each row once on an AMD Ryzen 7 PRO 5850U (2025-11-18). In the number rows musl won atoi (3.96 vs 9.28 ns over 512 strings of 1-5 digits) and sprintf %.6f (136.34 vs 160.56 ns) but lost strtod (226.72 vs 52.40 ns), sprintf %d (44.83 vs 36.91 ns) and the snprintf mix (250.64 vs 174.18 ns); across all 32 rows musl was faster in 9, slower in 20 and tied in 3.

## Use it when

- Your build already targets musl (Alpine containers, zig cc -target x86_64-linux-musl, static Rust or Go binaries) and a hot path parses short decimal integers with atoi: 3.96 vs 9.28 ns per call on 1-5 digit strings.
- Tokenising with strtok or strtok_r on a single-character separator and short tokens (CSV-like lines): 4.94 vs 14.76 ns per token, even though each 185-token line also pays for a 985-byte strcpy, where musl is the slower libc.
- Fixed-precision %f formatting of small doubles where the libc choice is already musl: 136 vs 161 ns per sprintf("%.6f").
- You want readable, MIT-licensed reference code to copy for a single routine (atoi.c is 16 lines, floatscan.c about 500) rather than LGPL glibc code.

## Skip it when

- Parsing doubles: musl's strtod was 4.3x slower than glibc's (226.72 vs 52.40 ns); a dedicated parser such as fast_float is faster still.
- Integer and mixed printf formatting: sprintf("%d") 1.21x slower and a four-conversion snprintf 1.44x slower than glibc; use {fmt}, jeaiii/itoa or std::to_chars instead of switching libc.
- As a general speed upgrade: glibc won 20 of the 32 rows, including 32-byte malloc/free (11x), qsort (2.8x), regexec (5.9x) and strtod; musl+jemalloc closes the malloc gap only.
- Validating untrusted numeric input with atoi: musl computes in int with no overflow check or errno, so out-of-range strings hit signed overflow; use strtol and check errno and the end pointer.
- Code that depends on glibc behaviour (NSS modules, GNU extensions, locale data) or on glibc-tuned SIMD string routines.

## How it is fast

atoi is a 16-line loop (skip isspace, read a sign, accumulate 10\*n - digit as a negative int) with no errno, locale or range handling, while glibc 2.35's atoi is a call to strtol(nptr, NULL, 10). strtok/strtok_r have the same strspn-then-strcspn structure as glibc, but musl's strspn and strcspn special-case a one-character separator set (a byte loop, and __strchrnul's word-at-a-time HASZERO bit trick), which is cheap for the benchmark's 4-byte average tokens. printf %f goes through fmt_fp, which converts the value to x87 long double and expands it into base-1e9 uint32 limbs, emitting 9 digits per limb; why that edges glibc by 1.18x was not established from the sources read. The losses have visible causes: strtod's __floatscan returns early only for short integer-like inputs and otherwise rescales a base-1e9 big number in 2^29 steps (the benchmark's '123.123E-4' style inputs take that path), and every printf call runs printf_core twice (a validation pass with f=0, then the output pass).

## Compared with alternatives

Only when the libc choice is already musl for deployment reasons: for parsing doubles fast_float beats glibc's strtod 3-5x (and glibc beat musl 4.3x here), and {fmt}, Ryu or Dragonbox format doubles about 16-26x faster than sprintf, far beyond musl's 1.18x edge.

## Integration

| | |
|---|---|
| **Form** | static lib (libc.a; a shared libc.so that is also its own dynamic linker is built too) |
| **Dependencies** | none beyond the Linux syscall API; building needs GNU Make and a freestanding C99 compiler with gcc-style inline asm, weak aliases and hidden visibility (INSTALL) |
| **Minimum toolchain** | C99 compiler (GCC, clang, cparser and PCC have built it); use a musl-targeted toolchain, the musl-gcc wrapper, or zig cc -target \*-linux-musl (the benchmark used zig 0.15.2) |
| **Platforms** | Linux only: i386, x86_64 (x32 experimental), ARM, AArch64, MIPS, MIPS64, PowerPC, PowerPC64, S390X, SuperH, Microblaze, or1k, RISC-V 32/64, LoongArch64 (INSTALL) |
| **Thread safety** | strtok keeps a static pointer (use strtok_r); atoi, strtol, strtod and snprintf are reentrant; stdio FILE operations lock per stream |
| **Drop-in for the baseline** | partial: same ISO C/POSIX API as glibc, so number parsing and formatting calls compile unchanged, but switching means changing the whole libc target (allocator, locale, NSS and static-linking behaviour change with it) |

## Gotchas

- What was measured is zig 0.15.2's bundled musl, not this repository: a pre-1.2.6 copy (its fmt_fp still declares the long-double-sized stack buffer that upstream shrank in August 2024). Zig overrides strlen, strcmp, strncmp and strcasecmp (lib/c/string.zig) and memcpy, memmove, memset and memcmp (compiler_rt), but its lib/c/stdlib.zig exports only abs, labs and llabs, so the atoi, strtod, printf, bsearch, strtok and strrchr rows do run musl C code.
- Harness flaws: each row is one calibrated sample (the loop stops once a run exceeds 62.5 ms of the 250 ms target; no repetitions), the glibc build calls libc.so through the PLT while musl is linked statically, and under -O3 the glibc build's stdlib.h pulls in the extern-inline bsearch from bits/stdlib-bsearch.h (__USE_EXTERN_INLINES), so the 1.5x bsearch row probably compares a compiler-inlined copy against musl's library loop (inference, not disassembled). The strtok rows charge a 985-byte strcpy per 185 tokens to each libc.
- musl's atoi has no overflow handling: 10\*n - digit is computed in int, so inputs beyond the int range are undefined behaviour and differ from glibc's strtol-based result (C leaves both undefined).
- Upstream commit f96e47a (2025-07-02) introduced a buffer overflow in floating-point decimal formatting that 0ccaf05 fixed on 2025-09-19; the fix says no release carried it, but a git snapshot of master or kraj/master from that window does, so pin a tag such as v1.2.6 rather than an arbitrary mirror commit.

## Known shortcomings

- Same fereidani/musl-vs-glibc benchmark as the glibc entry (zig cc flags, Ryzen 7 PRO 5850U, single run): musl wins 9 of 32 rows and loses 20; the measured musl is the zig 0.15.2 bundle, whose strlen/strcmp/strncmp and mem\* are Zig's own code, not the kraj mirror's, so the memcpy row is Zig compiler_rt vs glibc BZ 30994 and the strrchr win depends on the workload (last match near the end); in its own number-parsing-formatting category musl loses strtod 4.3x, sprintf_int 1.21x and snprintf_mix 1.44x; static vs dynamic linking asymmetric; musl.libc.org blocked so the record points at the kraj mirror.
- Enricher (orphaned file, agent killed by the session limit): what was measured is zig 0.15.2's bundled pre-1.2.6 musl, not this mirror; Zig overrides strlen, strcmp, strncmp, strcasecmp (lib/c/string.zig) and memcpy, memmove, memset, memcmp (compiler_rt) while the atoi, strtod, printf, bsearch, strtok and strrchr rows do run musl C code. Each row is one calibrated sample with no repetitions; the glibc build calls libc.so through the PLT while musl is linked statically; under -O3 glibc's stdlib.h pulls in the extern-inline bsearch, so the 1.5x bsearch row probably compares a compiler-inlined copy against musl's library loop (inference). musl's atoi has no overflow handling (10\*n - digit in int). Upstream commit f96e47a (2025-07-02) introduced a floating-point formatting buffer overflow fixed by 0ccaf05 (2025-09-19) with no release in between, so pin a tag such as v1.2.6 rather than a mirror commit.

## Caveats and trade-offs

Weak, mixed claim: in the musl vs glibc column musl is faster in 9 of 32 rows, slower in 20 and tied in 3; within the record's own category (number parsing/formatting) musl wins atoi_parse (2.3x) and sprintf_float (1.18x) but loses strtod_parse (4.3x slower), sprintf_int (1.21x slower) and snprintf_mix (1.44x slower), all derived from page data. The benchmark is a one-person third-party repo (fereidani/musl-vs-glibc, 7 stars, no licence), one calibrated run per benchmark, one machine, results dated 2025-11-18, glibc version unstated. What was measured is not kraj/musl: it is the musl bundled with zig 0.15.2, built by zig and linked statically, against the host's dynamic glibc through the PLT. Zig 0.15.2 replaces several musl functions with its own code (lib/c/string.zig exports strlen, strcmp, strncmp, strcasecmp; compiler_rt exports memcpy, memmove, memset, memcmp), so those rows do not measure musl. musl's strrchr win depends on the workload and on Zig's strlen: musl implements strrchr as memrchr(s, c, strlen(s)+1), and the 10,000-byte test string has an 'X' every 101 bytes, so the backward scan stops within about 100 bytes while glibc 2.35's forward scan tracks many matches over the whole string. strtok/strtok_r per-token times include a strcpy of the whole input per iteration (glibc's strcpy is faster, so musl's win there is net of that). The memcpy row (glibc 4043.27 vs 154.19 ns for 16 KB) is not a musl result (Zig compiler_rt memcpy) and was tied by the glibc entry's verifier to glibc bug BZ 30994 (rep movsb page aliasing on AMD Zen 3/4; snippet only there, not re-checked here) rather than being a harness artifact. strlen, strcmp and memcmp rows are hoisted no-ops (about 0.1 ns). The earlier statement that -flto=full inlines statically linked musl code is an unverified inference. kraj/musl is Khem Raj's downstream GitHub mirror (default branch kraj/master carries Yocto-style patches; branch master tracks upstream git.musl-libc.org, last commit 2026-10-05); the musl project's own site and git host were not opened (egress blocked). The record is filed under 'musl' because the repo itself carries no benchmark; baseline glibc is not a C++ standard-library facility. [retier] fereidani/musl-vs-glibc (zig cc, Ryzen 7 PRO 5850U, one run): wins 9 of 32 rows, loses 20. Measured libc is zig 0.15.2's bundled musl, whose strlen/strcmp/strncmp/memcpy/memmove are Zig code (memcpy row is Zig compiler_rt vs glibc BZ 30994); strrchr win depends on last-match position. In number-parsing-formatting musl loses strtod 4.3x, sprintf_int 1.21x, snprintf_mix 1.44x. Static vs dynamic linking asymmetric; kraj/musl is a mirror (musl.libc.org blocked).

Repo description stresses efficient static and dynamic linking, lightweight code and low runtime overhead rather than peak throughput. In the same table musl's malloc (malloc_free_small 11x, malloc_free_medium 4x slower), qsort (2.8x), strtod (4.3x) and several str\* routines (strcpy 5.9x, strncmp 37x slower) lose badly to glibc; musl+jemalloc closes most of the malloc gap. Software relying on glibc-specific behaviour may need porting.

## Maintenance

Upstream musl is actively maintained (v1.2.6 tagged 2026-03-20, upstream fixes through September 2026) and kraj/master was last updated 2026-09-28, but kraj/musl is a downstream mirror and the only evidence is one unrepeated third-party run of zig's bundled musl with no musl-specific benchmark in the repo; MIT, so single files are easy to copy.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now C.
- **Tier reason:** fereidani/musl-vs-glibc publishes benchmark.c and run.sh with the full flag set, names the compiler (zig 0.15.2 using clang 20.1.2) and the CPU (AMD Ryzen 7 PRO 5850U), and its README table holds every claimed number, which meets A for a third-party run (same evidence and tier as the catalogued glibc entry, https://github.com/bminor/glibc). The glibc version is not printed (Ubuntu 22.04 host, probably 2.35).
- **Retiered** A to C: The public harness has flags and a CPU, but the measured 'musl' is zig 0.15.2's bundle with Zig replacements for strlen, strcmp, strncmp, memcpy and memmove, so the headline string rows do not measure musl's code (same finding as the glibc entry's retier); single run and the record points at a mirror. Capped at C.
- **Verifier notes:** All claimed numbers and the 9/20/3 row count match the README table. Caveats corrected: memcpy row is Zig compiler_rt vs glibc BZ 30994 (not an artifact), Zig 0.15.2 overrides strlen/strcmp/strncmp and mem\* so the 'musl' side is partly Zig code, strrchr win is workload-shaped (last match near the end), and in its own category musl loses strtod 4.3x, sprintf_int and snprintf_mix. Kept at A for consistency with the bminor/glibc entry that cites the same benchmark.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-69 (wave 1); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://github.com/fereidani/musl-vs-glibc>
  - <https://raw.githubusercontent.com/fereidani/musl-vs-glibc/HEAD/README.md>
  - <https://raw.githubusercontent.com/fereidani/musl-vs-glibc/HEAD/run.sh>
  - <https://raw.githubusercontent.com/fereidani/musl-vs-glibc/HEAD/benchmark.c>
  - <https://raw.githubusercontent.com/ziglang/zig/0.15.2/lib/c.zig>
  - <https://raw.githubusercontent.com/ziglang/zig/0.15.2/lib/c/string.zig>
  - <https://raw.githubusercontent.com/ziglang/zig/0.15.2/lib/c/stdlib.zig>
  - <https://raw.githubusercontent.com/ziglang/zig/0.15.2/lib/compiler_rt.zig>
  - <https://raw.githubusercontent.com/ziglang/zig/0.15.2/lib/compiler_rt/memcpy.zig>
  - <https://github.com/kraj/musl>
  - <https://github.com/kraj/musl/commits/kraj/master>
  - <https://github.com/kraj/musl/commits/master>
  - <https://github.com/kraj/musl/branches>
- **Sources the enricher read:**
  - <https://github.com/kraj/musl>
  - <https://github.com/kraj/musl/tags>
  - <https://github.com/kraj/musl/commits/kraj/master>
  - <https://github.com/kraj/musl/commits/master/src/stdio/vfprintf.c>
  - <https://github.com/kraj/musl/commit/0ccaf0572e9cccda2cced0f7ee659af4c1c6679a>
  - <https://raw.githubusercontent.com/kraj/musl/master/README>
  - <https://raw.githubusercontent.com/kraj/musl/master/INSTALL>
  - <https://raw.githubusercontent.com/kraj/musl/master/VERSION>
  - <https://raw.githubusercontent.com/kraj/musl/master/WHATSNEW>
  - <https://raw.githubusercontent.com/kraj/musl/master/src/stdlib/atoi.c>
  - <https://raw.githubusercontent.com/kraj/musl/master/src/stdlib/strtod.c>
  - <https://raw.githubusercontent.com/kraj/musl/master/src/stdlib/strtol.c>
  - <https://raw.githubusercontent.com/kraj/musl/master/src/stdlib/bsearch.c>
  - <https://raw.githubusercontent.com/kraj/musl/master/src/internal/floatscan.c>
  - <https://raw.githubusercontent.com/kraj/musl/master/src/internal/intscan.c>
  - <https://raw.githubusercontent.com/kraj/musl/master/src/stdio/vfprintf.c>
  - <https://raw.githubusercontent.com/kraj/musl/master/src/string/strtok.c>
  - <https://raw.githubusercontent.com/kraj/musl/master/src/string/strtok_r.c>
  - <https://raw.githubusercontent.com/kraj/musl/master/src/string/strspn.c>
  - <https://raw.githubusercontent.com/kraj/musl/master/src/string/strcspn.c>
  - <https://raw.githubusercontent.com/kraj/musl/master/src/string/strchrnul.c>
  - <https://raw.githubusercontent.com/kraj/musl/master/src/string/strrchr.c>
  - <https://raw.githubusercontent.com/kraj/musl/master/src/string/memrchr.c>
  - <https://raw.githubusercontent.com/fereidani/musl-vs-glibc/HEAD/README.md>
  - <https://raw.githubusercontent.com/fereidani/musl-vs-glibc/HEAD/run.sh>
  - <https://raw.githubusercontent.com/fereidani/musl-vs-glibc/HEAD/benchmark.c>
  - <https://raw.githubusercontent.com/ziglang/zig/0.15.2/lib/c.zig>
  - <https://raw.githubusercontent.com/ziglang/zig/0.15.2/lib/c/stdlib.zig>
  - <https://raw.githubusercontent.com/ziglang/zig/0.15.2/lib/c/string.zig>
  - <https://raw.githubusercontent.com/ziglang/zig/0.15.2/lib/libc/musl/src/stdio/vfprintf.c>
  - <https://raw.githubusercontent.com/ziglang/zig/0.15.2/lib/libc/include/generic-glibc/stdlib.h>
  - <https://raw.githubusercontent.com/ziglang/zig/0.15.2/lib/libc/include/generic-glibc/features.h>
  - <https://raw.githubusercontent.com/ziglang/zig/0.15.2/lib/libc/include/generic-glibc/sys/cdefs.h>
  - <https://raw.githubusercontent.com/bminor/glibc/glibc-2.35/stdlib/atoi.c>
  - <https://raw.githubusercontent.com/bminor/glibc/glibc-2.35/string/strtok_r.c>
  - <https://raw.githubusercontent.com/bminor/glibc/glibc-2.35/bits/stdlib-bsearch.h>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/kraj/musl`) · [data/wave1/enrich/raw/github_com_kraj_musl.json](../../../data/wave1/enrich/raw/github_com_kraj_musl.json) (enrichment confidence 0.6)

</details>
