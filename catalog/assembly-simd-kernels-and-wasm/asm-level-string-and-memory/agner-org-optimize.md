# asmlib (Agner Fog): assembly memcpy, memmove, memset, strlen, strcpy and related replacements

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Assembly` · `GPL-3.0-or-later (commercial licences available on request from the author)` · ⚪ unknown

> Agner Fog's CPU-dispatched x86 assembly memcpy, memset, strlen and string routines; beat 2008-era glibc, MSVC and Intel CRTs.

| | |
|---|---|
| **Beats** | glibc 2.7/2.8 memcpy and strlen (32-bit and 64-bit builds), plus MSVC 2008, CodeGear, Intel C++ 10.1 and Mac Darwin8 libraries |
| **Claimed result** | asmlib-instructions.pdf section 1.5 (core clock cycles per byte, lower is better; asmlib v2.10 vs glibc 2.7/2.8): - memcpy 16 kB unaligned, Core 2: asmlib 0.12 vs Gnu 64-bit -fno-builtin 0.44 (3.7x), Gnu 32-bit -fno-builtin 0.57 (4.75x) and Gnu 32-bit builtin 1.21 (10x). - memcpy 16 kB aligned, Core 2: 0.11 vs 0.18 (1.6x). - strlen of 128 bytes, Core 2: 0.27 vs Gnu 64-bit 0.59 (2.2x). - Opteron K8: memcpy aligned 0.22 vs 0.28 (1.27x), unaligned 0.28 vs 0.29 (a tie), and strlen 1.19 vs Gnu 64-bit 0.6 (asmlib about 2x slower). All ratios are derived from page data. Fog's 2008 gcc and libc-help posts (search snippets only) state the matching 'factor 4-5 for unaligned data on a Core 2' and '3-4 times slower' for 64-bit libc. |
| **Workload** | Fog's comparison table in the asmlib manual: memcpy of 16 kB with aligned and unaligned operands, and strlen of 128-byte strings, measured in core clock cycles per byte. The libraries compared are MSVC 2008 (9.0), CodeGear bcc 5.5, Intel C++ 10.1.020 (_intel_fast_memcpy, __intel_new_strlen), Mac Darwin8 g++ 4.0.1, glibc 2.7/2.8 (32-bit with and without -fno-builtin, 64-bit with -fno-builtin) and asmlib 2.10. |
| **Metric** | throughput |
| **Hardware** | Intel Core 2 and AMD Opteron K8 (exact models not stated) |
| **Adoption** | classic reference library for CPU-dispatched x86 string routines, cited in mailing-list threads and forums |
| **Links** | [repository](https://www.agner.org/optimize/) · [benchmark](https://github.com/tpn/agner/blob/master/asmlib/asmlib-instructions.pdf) |

## Verdict

Fog's manual table compares asmlib 2.10 with glibc 2.7/2.8 and 2008-era MSVC 9.0, CodeGear 5.5, Intel C++ 10.1 and Darwin8 libraries, in cycles per byte on unnamed Core 2 and Opteron K8 CPUs. On Core 2, unaligned 16 kB memcpy runs 0.12 vs 0.44 cycles/byte for 64-bit glibc with -fno-builtin (3.7x) and 128-byte strlen 0.27 vs 0.59 (2.2x). On K8, memcpy gains shrink to 0.22 vs 0.28 aligned and a tie unaligned, and asmlib's strlen is about 2x slower (1.19 vs 0.6; ratios derived from page data). No harness, compiler flags or exact CPU models are published; the shipped testmem.cpp only checks correctness.

## Use it when

- x86 programs built with older toolchains whose C runtime has no dispatched string routines (MSVC 2008-era, Borland/CodeGear, Watcom, Digital Mars OMF, glibc 2.7/2.8). These are the libraries the manual's table beat.
- 32-bit GCC builds where the compiler's inline builtin memcpy and strlen are used. The table shows 1.21 vs 0.12 cycles/byte for unaligned 16 kB memcpy and 4.5 vs 0.27 for 128-byte strlen on Core 2.
- Large copies or fills where you want explicit control of the cache-bypass (non-temporal store) cutoff through SetMemcpyCacheLimit and SetMemsetCacheLimit.
- Mixed Windows, Linux, BSD and Intel-macOS code bases that want one string and memory library with the same API across all object formats.
- As a readable reference for per-microarchitecture CPU dispatch in assembly.

## Skip it when

- Current glibc on x86-64. It already selects SSE2, AVX2 and EVEX variants through ifunc, asmlib's strlen64.asm is an SSE2 loop last modified in 2008, and no published measurement shows asmlib ahead of a modern libc.
- AMD K8-class CPUs for strlen. The author's own table has asmlib at 1.19 cycles/byte against 0.6 for 64-bit glibc, and the unaligned memcpy result is a tie (0.28 vs 0.29).
- Any non-x86 target (ARM, RISC-V, POWER), or 32-bit shared objects on Linux, BSD or macOS. Position-independent 32-bit builds were dropped in v2.50.
- Closed-source products without a commercial licence. The library is GPL-3.0-or-later.
- Code where you need vendor support or catchable faults. The manual says 'for experts only ... If you have problems using it, then don't', and the library has no structured exception handling.

## How it is fast

Every function sets a function pointer on its first call, and later calls go straight through it. memcpy chooses an SSE2, SSSE3 (PALIGNR shift per source alignment), unaligned-load, 256-bit, AVX512F or AVX512BW path based on CPUID and on vendor, family and model tables. Copies and fills above half the last-level cache size use non-temporal (movnt) stores, and that cutoff can be changed with SetMemcpyCacheLimit and SetMemsetCacheLimit. strlen does aligned 16-byte SSE2 pcmpeqb and pmovmskb loads, masking off the misaligned head. strstr, strcmp and strspn use SSE4.2 string instructions.

## Compared with alternatives

Pick asmlib when you need one package covering memcpy, memmove, memset, memcmp, strlen, strcpy and strcat across Windows, Linux, BSD and Intel macOS object formats with a link-time override. For current x86-64 Linux, AOCL-LibMem (maintained, Zen-tuned, benchmarked against the host glibc) or a single-function sibling with recent glibc numbers such as fancy-memset or nadavrot/memset_benchmark is the better-evidenced choice.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none at run time; NASM to rebuild from asmlibSrc.zip (YASM for the dropped 32-bit PIC builds) |
| **Minimum toolchain** | Any C/C++ compiler that links ELF, COFF, OMF or Mach-O objects, or a Windows DLL (GCC, Clang, Intel C++, MSVC, Borland, Watcom, Digital Mars per the manual); NASM 2.x syntax since asmlib 2.20 |
| **Platforms** | x86 and x86-64 only (Windows, Linux, BSD, Intel macOS); runtime paths from SSE2 up to AVX512BW |
| **Thread safety** | Not documented for the memory and string functions. They keep no per-call state, but the first call writes a global dispatch pointer, and SetMemcpyCacheLimit changes a process-wide global. The random generators come in separate single-threaded and thread-safe variants. |
| **Drop-in for the baseline** | partial — the 'o' libraries replace memcpy, memmove, memset, memcmp, strlen, strcpy and strcat at link time. This only works if they are linked before libc and built with -fno-builtin (/Oi- on MSVC), and the link can fail with duplicate symbols when libc keeps two functions in one module. strstr, strcmp, strspn and strcspn have no override build because they read past the string end. |

## Gotchas

- The table does not show asmlib winning everywhere. On Core 2 the Mac Darwin8 library ties it on aligned memcpy (0.11 vs 0.11) and beats it on unaligned memcpy (0.11 vs 0.12). The large gaps are against 32-bit glibc with GCC builtins and against MSVC and CodeGear.
- Possible crash on some AVX-512 systems: InstructionSet in instrset64.asm (v2.51) only checks XCR0 bits 1-2 (SSE/AVX state) with XGETBV. It reports AVX512F and AVX512BW from CPUID leaf 7 alone, without checking that the OS has enabled the opmask and ZMM state (XCR0 bits 5-7). The memcpy, memset, memmove and memcmp dispatchers then jump to paths that use zmm16 and k1, which would fault with an illegal instruction on a kernel or hypervisor that leaves AVX-512 state disabled. This is a latent bug from reading the code; it does not affect the 2008 numbers, which used v2.10.
- Dispatch heuristics are hard-coded by vendor, family and model, last edited 2013 (UnalignedIsFaster, Store256BitIsFaster). For any AMD family above 15h the code 'assumes future AMD families are faster', so paths on newer CPUs are assumed rather than measured.
- strlen reads aligned 16-byte blocks before the start and after the end of the string, never past a 16-byte boundary. strstr, strcmp, strspn, strcspn, strtolower, strtoupper, strcount_UTF8 and strCountInSet can read up to 15 bytes past the end, and the manual's workaround is padding .bss and heap allocations. Expect sanitizer and debugger-watch hits. Copies above half the last-level cache bypass the cache, which slows a destination that is read right away.

## Known shortcomings

- 2008-era first-party numbers (asmlib-instructions.pdf section 1.5, tpn/agner mirror): Core 2 against glibc 2.7/2.8 64-bit, unaligned 16 kB memcpy 3.7x and strlen 2.2x, but about 2x slower on K8 strlen; no harness published; maintenance unknown. GPL-3.0-or-later.
- Enricher: the manual's own table has the Mac Darwin8 library tying asmlib on Core 2 aligned memcpy (0.11 vs 0.11) and beating it unaligned (0.11 vs 0.12), with the large gaps against 32-bit glibc, MSVC and CodeGear; the numbers are from v2.10 (2008) while strlen64.asm is SSE2-only and last modified 2008; latent bug in instrset64.asm v2.51: AVX-512 is reported from CPUID leaf 7 alone without checking XCR0 bits 5-7, so the zmm/k1 memcpy/memset paths can SIGILL where the OS leaves AVX-512 state disabled; testmem.cpp checks correctness only (no timing harness); agner.org unreachable, read from the tpn/agner mirror.

## Caveats and trade-offs

First-party numbers from 2008-era libraries; the manual itself calls them 'not up to date'. No benchmark code was published for the table, and the CPUs are named only by family (Core 2, Opteron K8). The tests are memcpy at one size (16 kB) and strlen at one size (128 bytes). On Opteron K8, asmlib's strlen (1.19 c/B) is about 2x slower than 64-bit glibc (0.6 c/B), and unaligned memcpy is a tie (0.28 vs 0.29). The largest Core 2 gaps are against 32-bit glibc with GCC's builtin inline string code; against 64-bit glibc the unaligned memcpy gain is 3.7x and the aligned one 1.6x. The numbers predate glibc's SSE2/SSSE3/AVX2/EVEX ifunc string routines, and no current asmlib-vs-glibc benchmark was found. A glibc-side reply in the 2008 gcc thread said glibc 2.6.1 x86-64 routines were already much faster (search snippet only). www.agner.org, gcc.gnu.org and sourceware.org all fail with getaddrinfo ENOTFOUND here. The manual was read from the third-party mirror github.com/tpn/agner (asmlib v2.51, 2016-11-16, mirrored 2018-04-11), so the latest release on agner.org could not be checked. The licence is GPL-3.0-or-later per the manual's section 9 and license.txt (copyleft).

x86 and x86-64 only; functions carry an A_ prefix (for example A_memcpy, A_memmove per a PureBasic forum snippet) and the library dispatches on instruction-set level (SSE2 and later), so it is linked or wrapped rather than a transparent libc replacement. Search snippets describe the licence as GPL; the licence file in the zip was not read, so usability is left as reference.

## Maintenance

Maintenance unknown: agner.org failed DNS resolution from this session, and the newest copy read (v2.51, 2016-11-16, from the third-party tpn/agner mirror) has strlen code last modified in 2008. The library is GPL-3.0-or-later with commercial licences on request, and ships as prebuilt libraries plus NASM source, so it can be linked or vendored under copyleft terms but comes with no support.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Fog's own asmlib manual (asmlib-instructions.pdf v2.51, section 1.5, read from the tpn/agner GitHub mirror) has a cycles-per-byte table comparing asmlib 2.10 with glibc 2.7/2.8 and other libraries on Intel Core 2 and AMD Opteron K8. These are first-party numbers: no benchmark code is published, CPUs are named only by family and the gcc version is not given, so the entry stays at C. The 2008 mailing-list claims could only be read as search snippets.
- **Verifier notes:** This is a real, widely cited reference library. The manual's own table gives glibc comparisons (3.7x on unaligned 16 kB memcpy and 2.2x on strlen on Core 2 versus 64-bit glibc 2.7/2.8), but asmlib loses on K8 strlen. Tier C, with all shortcomings tied to age: 2008 glibc, no published harness and no modern measurement. Maintenance stays 'unknown' because agner.org is unreachable; the mirror's newest asmlib is 2.51 from 2016.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `hardware`, `license`, `usability`, `baseline`, `caveats`
- **Shortcomings recorded by:** verifier batch-92 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/tpn/agner>
  - <https://github.com/tpn/agner/tree/master/asmlib>
  - <https://github.com/tpn/agner/commits/master>
  - <https://raw.githubusercontent.com/tpn/agner/master/asmlib/asmlib-instructions.pdf>
  - <https://raw.githubusercontent.com/tpn/agner/master/asmlib/license.txt>
- **Sources the enricher read:**
  - <https://github.com/tpn/agner>
  - <https://github.com/tpn/agner/tree/master/asmlib>
  - <https://raw.githubusercontent.com/tpn/agner/master/asmlib/asmlib-instructions.pdf>
  - <https://raw.githubusercontent.com/tpn/agner/master/asmlib/license.txt>
  - <https://raw.githubusercontent.com/tpn/agner/master/asmlib/asmlib.h>
  - <https://raw.githubusercontent.com/tpn/agner/master/asmlib/asmlibSrc/strlen64.asm>
  - <https://raw.githubusercontent.com/tpn/agner/master/asmlib/asmlibSrc/memcpy64.asm>
  - <https://raw.githubusercontent.com/tpn/agner/master/asmlib/asmlibSrc/memset64.asm>
  - <https://raw.githubusercontent.com/tpn/agner/master/asmlib/asmlibSrc/unalignedisfaster64.asm>
  - <https://raw.githubusercontent.com/tpn/agner/master/asmlib/asmlibSrc/instrset64.asm>
  - <https://raw.githubusercontent.com/tpn/agner/master/asmlib/asmlibSrc/testmem.cpp>
  - <https://raw.githubusercontent.com/tpn/agner/master/vectorclass/instrset_detect.cpp>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://agner.org/optimize`) · [data/wave13/enrich/raw/agner_org_optimize.json](../../../data/wave13/enrich/raw/agner_org_optimize.json) (enrichment confidence 0.6)

</details>
