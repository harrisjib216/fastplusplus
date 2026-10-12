# KmStrSearch (Windows kernel UTF-8 and UTF-16 substring search)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MIT` · 🟢 active

> Windows kernel-mode UTF-8/UTF-16 substring search (last-character SIMD scan plus BMH/SWAR fallback) beating kernel CRT strstr/wcsstr on buffers above 6 KB.

| | |
|---|---|
| **Beats** | Windows kernel CRT strstr and wcsstr (MSVC runtime; not glibc or musl) |
| **Claimed result** | i7-1165G7, 8-bit, GB/s (CRT baseline vs Smart Auto): 10 KB 22.38 vs 45.71, 1 MB 22.66 vs 85.93; 16-bit 20 KB 26.67 vs 68.43. Worse on small buffers: 40 B 3.61 vs 1.95, 256 B 15.03 vs 4.88. README: on mismatched dense text CRT collapses to 0.21-0.37 GB/s while the hybrid delivers 49-81 GB/s, 'up to 385x faster'. |
| **Workload** | Three throughput inputs whose pattern's last character ('k', 'b', 'K') never occurs in the text, so each search degenerates to a one-byte memchr; alternate calls shifted by 32 characters but credited the full buffer; one 2 s run per cell |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-1165G7 (bare-metal Windows 11, AVX-512BW) and Intel Core i7-8086K (VMware guest Windows 11, AVX2 only) |
| **Compiler and flags** | Visual Studio 2026 with WDK (WindowsKernelModeDriver10.0 toolset), MSVC version not stated. TestKm/KmStrSearchDrv.vcxproj Release\|x64 sets /std:c++20 (stdcpp20), InlineFunctionExpansion AnySuitable, IntrinsicFunctions true, FavorSizeOrSpeed Speed on top of toolset defaults; the README does not say whether the numbers came from the Release or Debug configuration. |
| **Adoption** | 0 stars; first commit 2026-08-25 |
| **Last commit** | 2026-09-07 |
| **Links** | [repository](https://github.com/adanil-code/KmStrSearch) · [benchmark](https://github.com/adanil-code/KmStrSearch/blob/main/Readme.md) |

## Verdict

A single-thread kernel-driver loop (2 s per cell, Windows 11, MSVC version and Release/Debug unstated) measured 8-bit Smart Auto at 45.71 GB/s versus kernel CRT strstr 22.38 GB/s at 10 KB and 85.93 vs 22.66 GB/s at 1 MB on a bare-metal i7-1165G7 (about 2.0x and 3.8x, derived from page data), with a pattern whose last character never appears in the text; on that input and the log input CRT wins at 40 B and 256 B. The 'up to 385x' figure is 'aaaaaaaaab' over all-'a' text, where CRT strstr falls to 0.21 GB/s while the hybrid runs a vector scan for 'b'.

## Use it when

- Inside a Windows kernel driver at PASSIVE_LEVEL or APC_LEVEL, searching buffers larger than about 6 KB (8-bit) for a fixed pattern that is set up once and reused.
- Length-delimited kernel buffers (UNICODE_STRING-style, not NUL-terminated, possibly with embedded NULs), which strstr/wcsstr cannot take directly.
- Repetitive text where kernel CRT strstr goes quadratic on partial matches of the pattern's first character ('aaaaaaaaab' in all-'a' text: 0.21 GB/s CRT versus 81.67 GB/s Smart Auto on the i7-1165G7).
- AVX-512BW hosts scanning buffers of 20 KB or more, where the README shows the ZMM path ahead of AVX2 (1 MB: 80.92 vs 65.46 GB/s for 8-bit).

## Skip it when

- Buffers under about 6 KB on bare metal: Auto runs the scalar path, which measured 2-3x slower than CRT strstr (8-bit 256 B: 4.88 vs 15.03 GB/s; 40 B: 1.95 vs 3.61 GB/s).
- Text in which the pattern's last character is common: every occurrence becomes a candidate with a first-character check and a forward middle verification, so a pattern like 'aaaaaaaaba' over runs of 'a' does O(N\*M) work in the vector path (inferred from FindAVX2/FindAVX512, not measured by the repo).
- DISPATCH_LEVEL or higher: Find is PAGED_CODE and reads a paged-pool skip table, despite a header comment about calling it at DISPATCH_LEVEL.
- User-mode code: the classes include ntddk.h and use kernel pool and XSTATE APIs, and the README says TestUm timings cannot be trusted; use a user-mode searcher instead.
- Production code that needs maturity: 4 commits, 0 stars, single author, no CI, and texts longer than INT_MAX characters are not rejected although Find returns int.

## How it is fast

For patterns under 128 (AVX2/NEON) or 256 (AVX-512) characters, the vector engines broadcast the pattern's last character and compare 128 or 256 bytes per iteration (4x unrolled cmpeq, OR-reduced, then bit-scan), checking the first character and the middle only at candidate positions; longer patterns add a BMH jump after each 64- or 128-character block. Below 6 KB (1 KB on ARM64) Auto stays in general-purpose registers (scalar BMH with a SWAR memchr fast-forward when the skip is 2 or less) to avoid the KeSaveExtendedProcessorState/XSAVE cost of using YMM/ZMM in ring 0, and AVX-512 is used only from 20 KB. The UTF-16 skip table is folded to 2,048 entries (8 KB) with a golden-ratio multiplicative hash, keeping the smallest shift on collisions.

## Compared with alternatives

The catalogued substring searchers (MSVC STL's vectorized std::search, sliceslice, strstr.c, AOCL-LibMem) are user-mode; pick KmStrSearch only inside a Windows kernel driver scanning buffers above about 6 KB, and use MSVC STL std::search or a user-mode library everywhere else.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Windows Driver Kit (ntddk.h, ExAllocatePool2, KeSaveExtendedProcessorState/KeSaveFloatingPointState, ExIsProcessorFeaturePresent); intrin.h/immintrin.h or arm64_neon.h |
| **Minimum toolchain** | C++20 (/std:c++20, [[likely]]/[[unlikely]]), MSVC with the WindowsKernelModeDriver10.0 toolset; README names Visual Studio 2026 and the latest WDK |
| **Platforms** | Windows kernel on x64 (SWAR, AVX2, AVX-512F+BW detected via CPUID) and ARM64 (NEON); the project has only x64 and ARM64 configurations |
| **Thread safety** | not documented; Find is a const method that only reads the pattern and the skip table, so concurrent Find calls on one initialized object look safe by inspection; Initialize is not re-entrant and a second call leaks the first table |
| **Drop-in for the baseline** | partial — replaces strstr/wcsstr only after rewriting the call: a two-step object API (Initialize then Find) that takes an explicit text length and returns an int index rather than a pointer, and the pattern buffer must outlive the object (shallow copy) |

## Gotchas

- All three throughput inputs are memchr-degenerate for the hybrid: the last pattern character ('k' of 'Needle In The Haystack', 'b' of 'aaaaaaaaab', 'K' of 'CRITICAL: USE_AFTER_FREE BUGCHECK') never occurs in the text except at the planted match, and every pattern is below the 128/256-character bifurcation, so the vector engines never verify a candidate or use the skip table; the 45-105 GB/s figures are single-byte vector scans. The 'realistic log corpus' line contains no 'K' and no uppercase 'C', so it exercises neither skip-table entropy nor CRT candidate checks.
- Harness accounting: every second call searches from offset 32 with length minus 32 but is credited with the full buffer; at 40 B that leaves 8 characters, shorter than the 22- or 33-character pattern, so Find returns -1 without searching, which inflates every engine's tiny-buffer GB/s (about 6% at 256 B). Each cell is one 2 s single-thread run (the README's 'multi-threaded' claim does not match StartThreads(pMgr, 1, ...)); identical code paths differ by up to 40% in the VMware tables (8-bit 10 KB Smart Auto 18.61 vs AVX2 Explicit 31.17 GB/s, both FindAVX2) and by about 6% on bare metal (1 MB 85.93 vs 80.92, both FindAVX512).
- The correctness suite never reaches the 8-bit AVX2/AVX-512 loops or the 16-bit AVX-512 loop: its texts are 104 characters or fewer, below the 128/256-character minimums, so those engines fall back to FindScalar; the long-pattern BMH-plus-vector branch is untested, and the throughput loop does not check returned indices. Reading the loops found no off-by-one, but there is no test evidence for them.
- The header says a forced AVX512 engine falls back to scalar below 20 KB, but the code only falls back below 256 characters, so explicit AVX512 pays the ZMM state save on small buffers; with 16-bit text exactly at the 20 KB threshold the harness's 32-character shift makes Auto alternate between AVX-512 and AVX2 on successive calls.

## Known shortcomings

- Baseline is the naive Windows kernel CRT strstr; the harness calls StartThreads(pMgr, 1, ...) so it is single-threaded, not the multi-thread setup the README claims; best-case BMH input, and the 385x comes from a pattern whose last character never occurs (pathological for naive strstr); MSVC version and build config unstated; loses under about 6 KB.
- Enricher: all three throughput inputs reduce to a one-byte memchr because the pattern's last character ('k', 'b', 'K') never occurs in the text, so candidate verification and the skip table never run; every second call is shifted 32 characters but credited the full buffer, and at 40 B the remainder is shorter than the pattern so Find returns -1 without searching; one 2 s run per cell with up to 40% variance on the same path (VMware 10 KB 18.61 vs 31.17 GB/s); the correctness suite never reaches the 8-bit AVX2/AVX-512 or 16-bit AVX-512 loops (texts of at most 104 characters); an O(N\*M) vector path when the last character is frequent is inferred, not measured; PAGED_CODE in Find, so no DISPATCH_LEVEL. Retiered to D (degenerate workload).

## Caveats and trade-offs

Very new, single-author exploration with 0 stars and 4 commits ('not strictly benchmark-driven during its design'); no repetition counts or variance; MSVC version and build configuration unstated. The README calls the harness multi-threaded and memory-bus saturating, but RunPerformanceSuiteT calls StartThreads(pMgr, 1, ...), so each figure is single-thread throughput. Throughput counts the whole buffer per call even though BMH skips most bytes, so the 80-105 GB/s figures at 1 MB are not memory bandwidth; the 'standard' input is the best case for BMH (text all 'A', pattern contains no 'A'). The 'up to 385x' dense-text figure comes from a pattern whose last character never occurs in the text, so the hybrid reduces to a vectorized memchr while the CRT's naive strstr does O(N\*M) work; glibc's two-way strstr would not collapse this way. The baseline is the Windows kernel CRT strstr/wcsstr, not glibc or musl; on the VMware guest it measures only 1.35-1.67 GB/s on 256 B to 1 MB inputs (about 15x below the same CRT on bare metal). Loses to CRT on tiny and small buffers on bare metal (40 B 3.61 vs 1.95 GB/s, 256 B 15.03 vs 4.88 GB/s for 8-bit Smart Auto). User-mode build is declared untrustworthy for timing. Kernel driver telemetry only; no independent reproduction.

Windows kernel-mode (WDK driver) code: routes small buffers to a SWAR path to avoid the KeSaveExtendedProcessorState cost of entering vector mode, and uses AVX2/AVX-512BW or ARM64 NEON for larger buffers. Uses 8 KB (UTF-16) skip tables allocated from paged pool. Not a user-mode library; the README says user-mode (TestUm) timings cannot be trusted.

## Maintenance

Active (four commits from 2026-08-25 to 2026-09-07, 0 stars) and MIT-licensed; a small two-class source drop for Windows kernel drivers, best treated as research code that needs your own large-buffer correctness tests before production use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party README tables against the kernel CRT strstr/wcsstr with public harness code (Shared/KmStrSearchShared.h) and stated CPUs, but the MSVC version (only 'Visual Studio 2026') and the build configuration that produced the numbers are not stated, and the README's description of the harness (multi-threaded, bus-saturating) does not match the code, which starts one worker thread.
- **Retiered** C to D: Enricher (2026-10-12): degenerate workload. All three throughput inputs reduce to a one-byte memchr because the pattern's last character never occurs in the text, so the candidate-verification and skip-table paths that define the algorithm never execute; every second call is shifted 32 characters but credited the full buffer, and the 40 B cell returns -1 without searching. ThreadPool degenerate-benchmark precedent.
- **Verifier notes:** Numbers in claimed_speedup match the README tables (i7-1165G7 8-bit and 16-bit rows; 385x is the README's own figure, about 389x derived from page data 81.67/0.21). Record shortcomings: weak naive kernel-CRT baseline, best-case and pathological inputs chosen for BMH, single-thread harness despite README's multi-thread claim, loses below about 6 KB, unstated build configuration. No invalid evidence found: the CRT and hybrid run the same buffers and the hybrid has correctness tests.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-34 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/adanil-code/KmStrSearch/blob/main/Readme.md>
  - <https://raw.githubusercontent.com/adanil-code/KmStrSearch/main/Readme.md>
  - <https://github.com/adanil-code/KmStrSearch>
  - <https://github.com/adanil-code/KmStrSearch/commits/main>
  - <https://github.com/adanil-code/KmStrSearch/tree/main/TestKm>
  - <https://raw.githubusercontent.com/adanil-code/KmStrSearch/main/Shared/KmStrSearchShared.h>
  - <https://raw.githubusercontent.com/adanil-code/KmStrSearch/main/TestKm/KmStrSearchDrv.vcxproj>
- **Sources the enricher read:**
  - <https://github.com/adanil-code/KmStrSearch>
  - <https://raw.githubusercontent.com/adanil-code/KmStrSearch/main/Readme.md>
  - <https://raw.githubusercontent.com/adanil-code/KmStrSearch/main/LICENSE>
  - <https://raw.githubusercontent.com/adanil-code/KmStrSearch/main/StrSearch/KmStrSearch8.h>
  - <https://raw.githubusercontent.com/adanil-code/KmStrSearch/main/StrSearch/KmStrSearch8.cpp>
  - <https://raw.githubusercontent.com/adanil-code/KmStrSearch/main/StrSearch/KmStrSearch16.h>
  - <https://raw.githubusercontent.com/adanil-code/KmStrSearch/main/StrSearch/KmStrSearch16.cpp>
  - <https://raw.githubusercontent.com/adanil-code/KmStrSearch/main/Shared/KmStrSearchShared.h>
  - <https://raw.githubusercontent.com/adanil-code/KmStrSearch/main/TestKm/KmStrSearchDrv.cpp>
  - <https://raw.githubusercontent.com/adanil-code/KmStrSearch/main/TestKm/KmStrSearchDrv.vcxproj>
  - <https://raw.githubusercontent.com/adanil-code/KmStrSearch/main/TestUm/KmStrSearchUm.cpp>
  - <https://github.com/adanil-code/KmStrSearch/commits/main>
  - <https://github.com/adanil-code/KmStrSearch/commit/361f942>
  - <https://github.com/adanil-code/KmStrSearch/commit/0ed4a2e>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/adanil-code/kmstrsearch`) · [data/wave13/enrich/raw/github_com_adanil_code_kmstrsearch.json](../../../data/wave13/enrich/raw/github_com_adanil_code_kmstrsearch.json) (enrichment confidence 0.8)

</details>
