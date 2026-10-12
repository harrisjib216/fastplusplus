# fancy-memset (fm): SSE2 and AVX2 memset in x86-64 assembly

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `x86-64 assembly (GNU as) with a C benchmark harness` · `BSD-2-Clause (headers in each memset .S file, Copyright 2021 Elijah Stone, commit ee040ef; no root LICENSE file; vendored competitor files keep their own Intel BSD and CDDL terms)` · 🔴 abandoned

> Three tiny x86-64 assembly memsets (GPR, SSE2, AVX2) after Microsoft's 2021 CRT design; claims 10-370% over glibc memset.

| | |
|---|---|
| **Beats** | glibc memset (the harness's 'sys' row calls the system libc memset; glibc version not stated); the harness also times FreeBSD, Bionic and Solaris memset, a naive rep stos and a naive -O3 loop |
| **Claimed result** | AVX2 version: '10-370% faster than glibc memset', '300-400% faster than a naive loop compiled with -O3 by gcc/icc/clang', '50-470% faster than freebsd memset, for sizes larger than 64 bytes'. SSE2 version: '20-150% faster than freebsd memset', '5-100% faster than bionic memset'; no glibc figure for SSE2 ('don't know about glibc, idk how to force it to use sse2'). README says numbers 'are variable and depend heavily on sizes'. |
| **Workload** | bench.c: for each size, 16 warm-up calls, then 100000 calls at each of 64 destination offsets (base malloc+1 plus 0-63), timed with rdtsc/rdtscp around cpuid, fill value 0. main() calls test(64..4100) and bench() subtracts 63, so the measured lengths run from 1 to 4037 bytes, all cache-resident. The output prints each column's time as a ratio to the SSE2 version; no results are committed. |
| **Metric** | throughput |
| **Hardware** | CPU model not stated; x86-64 only (SSE2 or AVX2 versions); README discusses Intel CPUs with ERMS and AMD CPUs without ERMS |
| **Compiler and flags** | bench.c built with CFLAGS -O3 -g -fno-builtin (makefile); compiler name and version not stated; assembly files assembled with as or cc -x assembler-with-cpp; 'make erms=' builds the variant for CPUs without ERMS |
| **Adoption** | 13 stars |
| **Last commit** | 2022-04-05 |
| **Links** | [repository](https://github.com/moon-chilled/fancy-memset) · [benchmark](https://github.com/moon-chilled/fancy-memset) |

## Verdict

First-party README ranges only: the AVX2 version is 10-370% faster than the system glibc memset and the SSE2 version 20-150% faster than FreeBSD's and 5-100% faster than bionic's, on an unnamed CPU, compiler and glibc version, from a 2021 harness that timed one destination address. The committed bench times warm, zero-fill memsets of 1-4037 bytes at 64 destination offsets (rdtsc, 100000 calls each) and prints ratios to fm SSE2, so any AVX2-versus-glibc figure has to be derived and no results are published.

## Use it when

- A freestanding kernel, bootloader or custom libc on x86-64 that needs a small, readable memset: fancy_memset_basic uses only general-purpose registers, and each file is about 140 lines.
- A static binary on known AVX2 hardware where memset is a measured hotspot for cache-resident, variable-length fills of roughly 1 byte to 4 KiB (the only range the committed bench covers).
- Replacing an older generic memset (a rep stos one-liner, an old FreeBSD or bionic SSE2 routine) where the README's 20-150% and 5-100% gains apply.
- As a compact reference for the overlapping-store memset design before writing your own for another ISA.

## Skip it when

- As a blanket replacement for glibc memset: the 10-370% glibc figure has no per-size table, CPU, compiler or glibc version, so whether it wins on your machine is unknown until you run bench.c.
- Large or uncached fills: no non-temporal stores, and the author says the bench never touches uncached memory and that rep stos and bionic should do better there (issue #1).
- Streams of mixed sizes: every timing repeats one size 100000 times with a trained branch predictor; the author lists variable-size runs as a todo.
- Small constant-size memsets in ordinary code: calling a fancy_memset_\* symbol stops the compiler from inlining or eliding them, which it does for memset (the README says so).
- Non-x86-64 targets, the Windows x64 calling convention (the code reads rdi/rsi/rdx), or CPUs without AVX2 for the AVX2 variant (no runtime dispatch, so it faults with an illegal instruction).

## How it is fast

Size classes chosen with a few compares: lengths below one vector are written with two to four overlapping unaligned stores (4-byte, 16-byte or 32-byte), so there is no byte loop and no tail loop. Larger fills store one unaligned head vector, then run a 4x-unrolled loop of aligned stores (64 bytes per iteration for SSE2, 128 for AVX2) and finish with three aligned stores plus one overlapping unaligned store at the end. In the default build (erms) very large fills hand off to rep stosb after aligning the destination to 64 bytes (from 800 bytes in the SSE2 and basic versions, from 256 KiB in the AVX2 version); an ermsq build of the SSE2 version uses rep stosq from 2600 bytes.

## Compared with alternatives

Pick fm over nadavrot/memset_benchmark or Agner Fog's asmlib when you want a tiny, permissively licensed source-drop with a non-SIMD kernel variant and you can fix the ISA at build time; pick asmlib or AOCL-LibMem when you need runtime CPU dispatch or a whole set of string functions, and nadavrot's harness when you need glibc compared with and without PLT indirection.

## Integration

| | |
|---|---|
| **Form** | source-drop (three standalone .S files; the makefile's memset target also builds memset-basic.so, memset-sse2.so and memset-avx2.so) |
| **Dependencies** | none (bench and test use only libc; the optfetch submodule is not used by the makefile) |
| **Minimum toolchain** | GNU as with .intel_syntax noprefix, driven through cc -x assembler-with-cpp (GCC or Clang); System V AMD64 ABI and ELF symbols (no underscore prefix) |
| **Platforms** | x86-64 only: basic needs no SIMD, SSE2 version needs SSE2, AVX2 version needs AVX2; Linux and FreeBSD mentioned (README notes AS=/usr/local/bin/as on FreeBSD); Windows x64 ABI and macOS not supported or documented |
| **Thread safety** | stateless and reentrant (no globals, only argument registers and scratch registers) |
| **Drop-in for the baseline** | partial: same signature and return value, but exported as fancy_memset_basic/_sse2/_avx2 unless you assemble with -DMEMSET=memset, the variant must be chosen at link time to match the CPU, and ERMS use is fixed at build time |

## Gotchas

- Harness flaw in the published claims: the printout says 'higher is better' but each number is that column's cycles divided by fm SSE2's cycles, so above 1 means fm SSE2 won and the avx2 column below 1 means AVX2 beat SSE2 (issues #1 and #2; the author confirmed the inversion). The README figures were last edited in August 2021, before commit 13e5b4d (February 2022) rewrote bench.c from 5 x 1,000,000 calls on one destination (malloc+1) to 64 offsets x 100,000 calls over 1-4037 bytes, and no output from either harness is committed, so the claims cannot be tied to the current code.
- ERMS is chosen when assembling: plain 'make' defines erms, so the SSE2 and basic versions switch to rep stosb at 800 bytes and AVX2 at 256 KiB; 'make erms=' removes it and 'make erms=q' gives SSE2 a rep stosq path from 2600 bytes. In the default bench the SSE2 reference column is therefore rep stosb for every length from 800 to 4037 bytes. The 'naive' column is a C loop built with gcc -O3 -fno-builtin; GCC's loop distribution can still turn such a loop into a memset call (inference, not built here).
- Test coverage gap: test.c passes length l-2, so its largest case is 262143 bytes and the AVX2 rep stosb path (262144 bytes and up) is never executed; only fill values 0-3 are tested. By reading the code the path looks correct, but it is untested.
- The .S files carry no .note.GNU-stack section, no .type/.size and no endbr64 or GNU property notes: linking them with GNU ld marks the stack executable (binutils 2.39 and later warn) and drops IBT/shadow-stack enforcement for the whole binary unless you add the notes or pass -Wa,--noexecstack.

## Known shortcomings

- README AVX2 10-370% over glibc with no CPU, compiler or glibc version and no committed results; bench.c covers only 1-4037 bytes with a warm cache and fill 0; no licence (reference); 13 stars, last commit 2022-04-05.
- Harness flaw: the bench printout labels its ratios 'higher is better' but each number is that column's cycles divided by fm SSE2's, so above 1 means SSE2 won (issues #1 and #2, author confirmed). The README numbers date from August 2021 on an older harness (5 x 1,000,000 calls on one malloc+1 destination); commit 13e5b4d (February 2022) rewrote bench.c and no results are committed. The default erms build makes the SSE2 reference column rep stosb from 800 to 4037 bytes. test.c passes l-2, so the AVX2 rep stosb path (262144 bytes and up) is never tested and only fill values 0-3 are tried; the .S files lack .note.GNU-stack and CET notes. Licence correction: the .S files carry BSD-2-Clause headers (Copyright 2021 Elijah Stone, commit ee040ef), so the routines are copyable.

## Caveats and trade-offs

Public benchmark code and flags, but no CPU model, compiler version or glibc version, so it falls short of tier A. The 'sys' row is the libc memset reached through -fno-builtin; on glibc the ifunc picks a different variant per CPU, so 'glibc' means different code on different machines. The glibc figure (10-370% for AVX2) has no per-size table, and the author could not force glibc onto its SSE2 path, so the SSE2 version has no glibc figure. The committed bench covers lengths of 1-4037 bytes only, so the README's large-size claims (erms, up to 2x over bionic) are not exercised by it. Ratios are printed relative to the SSE2 version, so AVX2-vs-glibc must be derived. Fill value is always 0, buffers are warm and the same region is hit 100000 times. The README notes that the compiler inlines small constant memsets in real code. The repo describes itself as 'based on microsoft's design'. The competition/ folder vendors bionic, FreeBSD and Solaris memsets. No license file. Last commit 2022-04-05. [retier] Public benchmark code and flags, but no CPU model, compiler version or glibc version. Harness flaw: the bench printout says 'higher is better' but each number is that column's cycles divided by fm SSE2's cycles, so above 1 means fm SSE2 won and the avx2 column below 1 means AVX2 beat SSE2 (issues #1 and #2, author confirmed). The README figures were last edited in August 2021 on the older harness (5 x 1,000,000 calls on one malloc+1 destination); commit 13e5b4d (February 2022) rewrote bench.c to 64 offsets x 100,000 calls over 1-4037 bytes and no output from either harness is committed, so the claims cannot be tied to the current code. ERMS is chosen when assembling: plain 'make' defines erms, so the SSE2 reference column is rep stosb for every length from 800 to 4037 bytes in the default bench; the 'naive' column is a C loop built with -O3 -fno-builtin that GCC's loop distribution may still turn into a memset call (inference). The 'sys' row is the libc memset reached through -fno-builtin (glibc ifunc picks a different variant per CPU); the glibc figure has no per-size table and the SSE2 version has no glibc figure. The committed bench covers 1-4037 bytes only, so the README's large-size claims are not exercised; test.c passes l-2, so the AVX2 rep stosb path (262144 bytes and up) is never tested and only fill values 0-3 are tried. Fill value is always 0, buffers are warm and the same region is hit repeatedly. The .S files have no .note.GNU-stack, .type/.size, endbr64 or GNU property notes (executable stack warning, no IBT/shadow-stack). Abandoned since 2022-04-05.

x86-64 only. The AVX2 version needs AVX2 and the SSE2 version SSE2; selection is by which object you link (no runtime dispatch seen in the makefile). ERMS use is chosen at assembly time (makefile --defsym erms), so the build must match the CPU. Author notes that very small and constant-size memsets are better inlined by the compiler, so the benchmark does not cover them. No LICENSE file in the repo root, so the code cannot be assumed copyable.

## Maintenance

Abandoned since 2022-04-05 with one open, unanswered issue about the benchmark's inverted ratios; despite no root LICENSE file, the three memset .S files each carry a BSD-2-Clause header (Copyright 2021 Elijah Stone; commit ee040ef moved the licence into the source), so the routines are copyable, while the vendored competition files keep their own Intel BSD and CDDL terms; the README claims rest on an older harness than the committed one.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README gives first-party percentage ranges against glibc and other libc memsets, and the benchmark code (bench.c, makefile with -O3 -g -fno-builtin) is public, but no CPU model, compiler version, glibc version or results table is committed, so it stays first-party C.
- **Verifier notes:** README numbers match the record (AVX2 10-370% faster than glibc; SSE2 20-150% vs FreeBSD and 5-100% vs bionic). Shortcomings to record: no CPU, compiler or glibc version, no committed results, the bench covers only 1-4037 bytes with warm cache and fill 0, and no license (reference). Metadata verified: 13 stars, 1 fork, last commit 2022-04-05 (abandoned).
- **Fields the verifier corrected:** `workload`, `caveats`, `usability`, `license`
- **Shortcomings recorded by:** verifier batch-108 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/moon-chilled/fancy-memset>
  - <https://github.com/moon-chilled/fancy-memset/commits/master>
  - <https://raw.githubusercontent.com/moon-chilled/fancy-memset/HEAD/readme>
  - <https://raw.githubusercontent.com/moon-chilled/fancy-memset/HEAD/bench.c>
  - <https://raw.githubusercontent.com/moon-chilled/fancy-memset/HEAD/makefile>
- **Sources the enricher read:**
  - <https://github.com/moon-chilled/fancy-memset>
  - <https://github.com/moon-chilled/fancy-memset/tree/master/competition>
  - <https://github.com/moon-chilled/fancy-memset/commits/master>
  - <https://github.com/moon-chilled/fancy-memset/commits/master/readme>
  - <https://github.com/moon-chilled/fancy-memset/commit/13e5b4d>
  - <https://github.com/moon-chilled/fancy-memset/issues?q=is%3Aissue>
  - <https://github.com/moon-chilled/fancy-memset/issues/1>
  - <https://github.com/moon-chilled/fancy-memset/issues/2>
  - <https://raw.githubusercontent.com/moon-chilled/fancy-memset/HEAD/readme>
  - <https://raw.githubusercontent.com/moon-chilled/fancy-memset/HEAD/bench.c>
  - <https://raw.githubusercontent.com/moon-chilled/fancy-memset/HEAD/makefile>
  - <https://raw.githubusercontent.com/moon-chilled/fancy-memset/HEAD/test.c>
  - <https://raw.githubusercontent.com/moon-chilled/fancy-memset/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/moon-chilled/fancy-memset/HEAD/memset-avx2.S>
  - <https://raw.githubusercontent.com/moon-chilled/fancy-memset/HEAD/memset-sse2.S>
  - <https://raw.githubusercontent.com/moon-chilled/fancy-memset/HEAD/memset-basic.S>
  - <https://raw.githubusercontent.com/moon-chilled/fancy-memset/HEAD/competition/naive-memset.c>
  - <https://raw.githubusercontent.com/moon-chilled/fancy-memset/HEAD/competition/stos.s>
  - <https://raw.githubusercontent.com/moon-chilled/fancy-memset/HEAD/competition/bionic-memset.S>
  - <https://raw.githubusercontent.com/moon-chilled/fancy-memset/HEAD/competition/freebsd-memset.S>
  - <https://raw.githubusercontent.com/moon-chilled/fancy-memset/HEAD/competition/solaris-memset.S>
  - https://msrc-blog.microsoft.com/2021/01/11/building-faster-amd64-memset-routines/ (DNS failure, not read)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/moon-chilled/fancy-memset`) · [data/wave13/enrich/raw/github_com_moon_chilled_fancy_memset.json](../../../data/wave13/enrich/raw/github_com_moon_chilled_fancy_memset.json) (enrichment confidence 0.75)

</details>
