# WojciechMula/toys avx512-string (AVX512F strlen, strchr, strrchr, strcmp)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-2-Clause` · 🔴 abandoned

> 2016 AVX512F SWAR versions of strlen, strchr, strrchr and strcmp; 4-16x over a 2016 glibc on Knights Landing.

| | |
|---|---|
| **Beats** | libc strlen/strchr/strrchr/strcmp via &lt;cstring&gt; (labelled 'std' in the harness; libc version not stated) |
| **Claimed result** | strlen 4.96x (0.0829 s vs 0.0167 s), strchr 4.44x (0.1000 s vs 0.0225 s), strrchr 16.03x (0.7211 s vs 0.0450 s), strcmp 3.94x (0.1171 s vs 0.0297 s) |
| **Workload** | strlen/strchr/strrchr/strcmp over 10 kB strings on a Knights Landing CPU, AVX512F kernels (SWAR tricks since AVX512F has no byte ops) versus the stdlib routine. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Phi Knights Landing 7210 |
| **Compiler and flags** | GCC 5.4.3 (README); Makefile flags: -std=c++14 -mavx512f -O3 -Wall -Wextra -pedantic |
| **Adoption** | 373 stars (toys repo) |
| **Last commit** | 2020-04-06 |
| **Links** | [repository](https://github.com/WojciechMula/toys) · [benchmark](https://github.com/WojciechMula/toys/blob/master/avx512-string/README.rst) |

## Verdict

In the author's single October 2016 run on a Xeon Phi 7210 (Knights Landing) with GCC 5.4.3 and -O3 -mavx512f, 5 passes over a 10 KiB buffer took 0.0829 s with libc strlen vs 0.0167 s (4.96x), strchr 0.1000 vs 0.0225 s (4.44x), strrchr 0.7211 vs 0.0450 s (16.03x) and strcmp 0.1171 vs 0.0297 s (3.94x); about 0.7-3.2 GB/s for libc vs 9-16 GB/s for AVX512F (derived from the harness's byte counts). The glibc version and which variant it picked on KNL are not stated; a 2016 glibc probably ran an SSE2 path (inference).

## Use it when

- As a reference or starting point for SWAR-in-SIMD string scanning on AVX-512F-only targets (Knights Landing/Knights Mill) where byte compares (AVX-512BW) are missing.
- Long ASCII strings (kilobytes) held in buffers you control and pad with at least 64 readable bytes past the terminator, where a 4-16x scan speedup over an old SSE2-era libc matters.
- Teaching material: each kernel is 30-100 lines and shows mask-based early exit, dword-to-byte refinement and the last-match trick for strrchr.

## Skip it when

- As a general libc replacement: the kernels read up to 63 bytes past the terminator (and past the first difference in strcmp) with no page-boundary handling, so a string ending near the end of a mapped page can fault.
- Non-ASCII data or a NUL search character: strchr/strrchr miss matches for characters 0x80-0xFF, strchr(s, 0) and strrchr(s, 0) return NULL, and strcmp orders bytes 0x80-0xFF as negative (see gotchas).
- CPUs with AVX-512BW/VL (Skylake-SP and later, Zen 4): byte compares make the SWAR detour unnecessary, and current glibc already selects EVEX string variants there; nothing here was measured on such hardware.
- Short strings (tens of bytes), which dominate real strlen/strcmp calls: the benchmark measured only average lengths of about 5-10 KB, and per-call overhead and the scalar tail were not studied.
- Projects needing maintenance or a build system: the code dates from October 2016, the README calls the tests 'not very good', and there is no packaging beyond a Makefile.

## How it is fast

Each loop iteration loads 64 bytes with an unaligned _mm512_loadu_si512 and applies the classic SWAR zero-byte test ((v - 0x01010101) & \~v & 0x80808080, fused into one vpternlogd) to 16 dwords at once, giving a 16-bit dword mask; strchr/strrchr run the same test on v XOR a broadcast of the character, and strcmp combines s1's zero mask with a dword-inequality mask (vpcmpneqd). Once a mask bit fires, a short scalar check of the 4 bytes of that dword finds the exact position, and strrchr uses clz on the mask to find the last match per block. The loop body has no per-byte work, so long strings run at about 12-16 GB/s versus 0.7-3 GB/s for the libc baseline in the author's run.

## Compared with alternatives

Pick it only to study or adapt the AVX-512F SWAR technique (Knights Landing-class hardware); for a production x86 replacement use AOCL-LibMem or Agner Fog's asmlib, which dispatch by CPU and cover many more functions, and for Arm use Arm Optimized Routines.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (immintrin.h, cassert) |
| **Minimum toolchain** | C++14 as the Makefile builds it (-std=c++14 -mavx512f -O3); GCC or Clang for __builtin_ctz/__builtin_clz and __attribute__((always_inline)); measured with GCC 5.4.3 |
| **Platforms** | x86-64 with AVX-512F only (Knights Landing used for the numbers; Intel SDE suggested for emulation) |
| **Thread safety** | stateless pure functions, safe to call concurrently |
| **Drop-in for the baseline** | partial — libc-like names and results only for ASCII strings, non-NUL search characters and buffers padded by 64 bytes; strchr/strrchr take char rather than int |

## Gotchas

- Correctness bug (found by exact emulation of the kernels' 32-bit lane arithmetic): avx512f_strchr and avx512f_strrchr build the broadcast pattern as 0x01010101u \* uint32_t(c) with c a signed char, so a character &gt;= 0x80 sign-extends (0xE9 becomes 0xE8E8E8E9). A match is then seen only in byte 0 of each dword: occurrences at byte offsets 1-3 are missed (NULL returned), and a byte equal to c-1 at offsets 1-3 trips assert(false), which aborts because the Makefile does not define NDEBUG. The benchmark searches only for 'X' (0x58), so the timing is unaffected.
- avx512f_strchr(s, '\0') and avx512f_strrchr(s, '\0') return NULL instead of a pointer to the terminator, and avx512f_strcmp compares bytes as signed char (int a = c1[i]), so "caf\xC3\xA9" vs "cafe" returns -162 where libc strcmp returns a positive value. test.cpp misses all of this: it uses only '?', 'X' and 0, compares strcmp results for exact equality, and its strchr test only places 'X' after the terminator, so the found path is never validated.
- Harness flaw in speed_strrchr.cpp: the loop writes 'X' at every index i and then restores '?', including i = size-1 where the only terminator sits, so after the first of the 5 iterations the 10 KiB buffer (plus its 64-byte '?' padding) has no NUL. Both std::strrchr and the AVX512F version then read past the heap allocation until they hit a stray zero byte (undefined behaviour). Both sides do it, so the ratio probably holds, but 4 of the 5 timed passes run on unterminated strings.
- Every call in all four harnesses starts at the same buffer start (plain new char[], not forced to 64-byte alignment), lengths are uniform over 0-10 KiB (strrchr always scans the full 10 KiB), the 10 KiB buffer stays cache-resident, and timing is a single gettimeofday interval per implementation with no repetitions.

## Known shortcomings

- README numbers exact (GCC 5.4.3, KNL 7210, Makefile flags, speed_str\*.cpp public) but one 10 KiB size only, glibc version unknown (baseline may be weak), unaligned 64 B loads with no page-crossing guard (the bench pads 64 B), and the strcmp code changed in 2020 after the numbers (perf-only).
- Correctness bugs confirmed by emulating the kernels' lane arithmetic: strchr and strrchr broadcast 0x01010101u \* uint32_t(signed char), so for characters &gt;= 0x80 matches at byte offsets 1-3 are missed and some inputs reach assert(false); strchr/strrchr(s, '\0') return NULL; strcmp compares signed char, giving the wrong sign for bytes &gt;= 0x80; test.cpp never checks strchr's found path. Harness flaw: speed_strrchr overwrites the only terminator at i=size-1, so 4 of 5 passes over-read the heap on both sides (UB). The benchmark uses 'X' only, so the ratios probably stand.

## Caveats and trade-offs

Author says the tests 'aren't very good' and do not cover a range of string lengths: one 10 KiB buffer filled with '?', the terminator (or target char) moved through every position, 5 iterations, gettimeofday timing, no repetitions or variance. Measured once in October 2016 on one old CPU with GCC 5.4.3 (not an official GCC release number; 5.4.0 and 5.5.0 exist); the glibc version and which of its ifunc variants ran on KNL are not stated, so the baseline may be a weak SSE2 path (the 16x strrchr gain points that way). The AVX512F kernels use unaligned 64-byte loads with no page-boundary handling (avx512f_strlen does _mm512_loadu_si512(s + len) in a loop), so they can read up to 63 bytes past the terminator and fault at the end of a mapped page; the benchmark pads every buffer by 64 bytes, so they are not drop-in libc replacements without aligned or masked loads. speed_strlen discards the strlen result (the other three harnesses accumulate into a volatile counter); the measured times look like real work. avx512f-strcmp.cpp was simplified by KWillets on 2020-04-06 (commit 8759381, removes a redundant zero2 mask, not a correctness fix), after the README numbers were taken. The README lists custom scalar versions too but reports only std vs AVX512F. Date shown is the last commit touching avx512-string; the toys repo itself was last pushed 2026-04-08. An SSE2 version of the same four functions lives in WojciechMula/sse2string, whose README gives no numbers. [retier] Author says the tests 'aren't very good': one 10 KiB buffer filled with '?', the terminator or target moved through every position, 5 iterations, gettimeofday timing, no repetitions or variance. Measured once in October 2016 on a Knights Landing with GCC 5.4.3 (not an official release number); the glibc version and which ifunc variants ran are not stated. Correctness bugs (emulated, not run): strchr and strrchr broadcast 0x01010101u \* uint32_t(signed char), so for characters &gt;= 0x80 matches at byte offsets 1-3 are missed and some inputs reach assert(false); strchr/strrchr(s, '\0') return NULL; strcmp compares signed char, wrong sign for bytes &gt;= 0x80; test.cpp never checks strchr's found path. Harness flaw: speed_strrchr overwrites the only terminator at i=size-1, so 4 of 5 passes over-read the heap on both sides (UB). The benchmark uses 'X' only, so the ratios probably stand, but they time buggy kernels.

Requires AVX512F (Xeon Phi KNL, Skylake-X and later). The strlen kernel uses unaligned 64-byte loads that can read past the terminator and across a page boundary, so it is only safe on padded buffers (the harness pads by 64 bytes). Only four functions (strlen, strchr, strrchr, strcmp); no memcpy/memchr.

## Maintenance

Untouched since a 2020 strcmp simplification (core code from October 2016) in a BSD-2-Clause snippet repository; small enough to copy, but fix the signed-char broadcast, NUL-character and strcmp sign bugs and add page-safe tail handling before using it on real data.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now C.
- **Tier reason:** README.rst table compares std (libc via &lt;cstring&gt;) against AVX512F with the exact times claimed; benchmark code is public (avx512-string/speed_strlen.cpp, speed_strchr.cpp, speed_strrchr.cpp, speed_strcmp.cpp), the compiler (GCC 5.4.3) and CPU (Knights Landing 7210) are stated in the README and the flags (-std=c++14 -mavx512f -O3) are in avx512-string/Makefile.
- **Retiered** A to C: Enricher: emulation of the kernels' lane arithmetic shows strchr and strrchr miss characters &gt;= 0x80 at byte offsets 1-3 (some inputs hit assert(false)), both return NULL for '\0', and strcmp gives the wrong sign for bytes &gt;= 0x80; the speed_strrchr harness also over-reads the heap on 4 of 5 passes. Numbers measured on code with hot-path correctness bugs: A to C (uniwidth precedent).
- **Verifier notes:** Numbers match README.rst exactly and the harness, Makefile flags, compiler and CPU are all public, so A holds on the letter of the rule; record shortcomings: single 10 KiB size, unstated glibc version (possibly weak baseline path on KNL), no page-crossing safety in the AVX512F kernels (bench pads buffers by 64 bytes), 2016-era one-off measurement. Not a duplicate: other WojciechMula entries (sse4-strstr, toys strstr-swar) are different code.
- **Fields the verifier corrected:** `compared_against_cpp_std_directly`, `caveats`
- **Shortcomings recorded by:** verifier batch-34 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/WojciechMula/toys/blob/master/avx512-string/README.rst>
  - <https://raw.githubusercontent.com/WojciechMula/toys/master/avx512-string/README.rst>
  - <https://raw.githubusercontent.com/WojciechMula/toys/master/avx512-string/Makefile>
  - <https://raw.githubusercontent.com/WojciechMula/toys/master/avx512-string/speed_strlen.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/toys/master/avx512-string/speed_strchr.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/toys/master/avx512-string/speed_strrchr.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/toys/master/avx512-string/speed_strcmp.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/toys/master/avx512-string/avx512f-strlen.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/toys/master/avx512-string/avx512f-strchr.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/toys/master/avx512-string/gettime.cpp>
  - <https://github.com/WojciechMula/toys>
  - <https://github.com/WojciechMula/toys/commits/master>
  - <https://github.com/WojciechMula/toys/commits/master/avx512-string>
  - <https://github.com/WojciechMula/toys/commit/8759381>
- **Sources the enricher read:**
  - <https://github.com/WojciechMula/toys>
  - <https://github.com/WojciechMula/toys/commits/master/avx512-string>
  - <https://github.com/WojciechMula/toys/issues?q=is%3Aissue+avx512>
  - <https://github.com/WojciechMula/toys/issues/5>
  - <https://raw.githubusercontent.com/WojciechMula/toys/master/avx512-string/README.rst>
  - <https://raw.githubusercontent.com/WojciechMula/toys/master/avx512-string/Makefile>
  - <https://raw.githubusercontent.com/WojciechMula/toys/master/avx512-string/common.h>
  - <https://raw.githubusercontent.com/WojciechMula/toys/master/avx512-string/test.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/toys/master/avx512-string/gettime.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/toys/master/avx512-string/speed_strlen.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/toys/master/avx512-string/speed_strchr.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/toys/master/avx512-string/speed_strrchr.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/toys/master/avx512-string/speed_strcmp.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/toys/master/avx512-string/avx512f-strlen.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/toys/master/avx512-string/avx512f-strchr.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/toys/master/avx512-string/avx512f-strrchr.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/toys/master/avx512-string/avx512f-strcmp.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/toys/master/avx512-string/scalar-strlen.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/toys/master/avx512-string/scalar-strchr.cpp>
  - WebSearch: glibc x86_64 multiarch strrchr-evex strlen-evex (snippets: EVEX variants selected on AVX512VL+AVX512BW CPUs)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `paper:wojciechmula-toys-avx512-string`) · [data/wave13/enrich/raw/paper_wojciechmula_toys_avx512_string.json](../../../data/wave13/enrich/raw/paper_wojciechmula_toys_avx512_string.json) (enrichment confidence 0.75)

</details>
