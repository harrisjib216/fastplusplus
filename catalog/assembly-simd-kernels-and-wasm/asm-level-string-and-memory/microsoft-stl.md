# Vectorized std::search and std::find in the MSVC STL (SSE4.2/AVX2 runtime dispatch)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0 WITH LLVM-exception` · 🟢 active

> MSVC STL's built-in SIMD std::search and string::find (SSE4.2, AVX2, NEON), 2-12x faster than its former scalar loop.

| | |
|---|---|
| **Beats** | MSVC STL's own scalar std::search before vectorization (the same PR also times C strstr as an unchanged control) |
| **Claimed result** | PR #4745 (1- and 2-byte elements, SSE4.2 pcmpestri; Stephan T. Lavavej's run on an AMD Ryzen 9 5950X, merged 2024-09-09): classic_search&lt;uint8_t&gt;/0 1976 to 160 ns (12.35x) and /1 2153 to 175 ns (12.30x); classic_search&lt;uint16_t&gt;/0 and /1 4.62x and 4.53x; ranges_search&lt;uint8_t&gt;/0 9.76x; search_default_searcher&lt;uint8_t&gt; 10.38x and 10.32x. The unchanged C strstr control took 142-143 ns (/0) and 157-162 ns (/1), so strstr stayed faster than the vectorized 1-byte std::search (160 and 175 ns). In that PR 4- and 8-byte rows were unchanged (0.98x-1.04x) and search_default_searcher&lt;uint64_t&gt; moved to 0.74x though its code was not changed (loop alignment suspected). PR #5484 (32- and 64-bit elements plus reworked 8/16-bit paths; 5950X run posted 2025-05-16, merged 2025-05-17): classic_search&lt;uint32_t&gt; /0 to /3 6.95x, 6.23x, 7.61x, 4.23x (1967 to 283 ns for /0); classic_search&lt;uint64_t&gt; /0 to /3 2.91x, 2.88x, 3.03x, 2.37x; uint16_t 1.38x to 1.98x. Regressions in the same 5950X table: classic_search&lt;uint8_t&gt;/0 158 to 202 ns (0.78x), /1 173 to 229 ns (0.76x), /3 0.91x, the 'evil' uint8_t/4 case 1016 to 3058 ns (0.33x) and uint64_t/4 0.71x; uint8_t/5 improved 2.77x. In that table c_strstr took 138 and 155 ns on /0 and /1, against 202 and 229 ns for the vectorized 1-byte classic_search. |
| **Workload** | benchmarks/src/search.cpp: std::search, ranges::search and default_searcher over a lorem-ipsum haystack with small and large needles near the beginning and end, plus adversarial 'evil' patterns, for uint8_t, uint16_t, uint32_t and uint64_t elements, timed in ns per search. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 5950X (maintainer comment on PRs #4745 and #5484); 12th-gen Intel Core i5-1235U E-cores (contributor run in PR #5484) |
| **Compiler and flags** | Not stated in the PRs. benchmarks/CMakeLists.txt builds the benchmarks as Release (/O2 /Ob2, plus /Zi /W4 /utf-8 and others) with MSVC or clang-cl; which compiler and version produced the posted tables is not said. |
| **Adoption** | 11.2k stars; the standard library shipped with Visual Studio |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/microsoft/STL) · [benchmark](https://github.com/microsoft/STL/pull/4745) |

## Verdict

Maintainer before/after runs with Google Benchmark (benchmarks/src/search.cpp, Release /O2 /Ob2, compiler and version unstated, AMD Ryzen 9 5950X) against MSVC STL's own previous scalar std::search: 1-byte classic_search 1976 to 160 ns (12.35x) and 2-byte 4.5x-4.6x in PR #4745, then 4-byte 4.2x-7.6x and 8-byte 2.4x-3.0x in PR #5484. The UCRT strstr timed in the same binary stayed faster than the vectorized 1-byte search (142 vs 160 ns).

## Use it when

- You build with MSVC or clang-cl against the MSVC STL and search std::string, std::wstring, string_view or vector&lt;char&gt; for short substrings: 1-byte classic_search went from 1976 to 160 ns (12.35x) on a Ryzen 9 5950X with no code change.
- Sequence search over 4- or 8-byte elements (std::u32string, vector&lt;int&gt;, vector&lt;uint64_t&gt;, vectors of pointers), which no libc strstr/memmem covers: 4.2x-7.6x (uint32_t) and 2.4x-3.0x (uint64_t) on the 5950X in PR #5484.
- Windows on ARM builds with MSVC Build Tools 14.51 or later: the NEON path posted 4.1x-6.1x for 1-byte and 3.0x-4.7x for 2-byte classic_search on a Neoverse N2 (PR #6139).
- Haystacks of a few hundred to a few thousand elements where the first needle element is rare enough that candidate checks stay cheap.

## Skip it when

- You use libstdc++ or libc++: none of this applies; use a dedicated searcher (memmem, sliceslice-style first-and-last-byte filters) there.
- Plain NUL-terminated byte strings where C strstr is enough: the UCRT strstr control in the same benchmark binary beat the vectorized 1-byte std::search on the 5950X (142-143 vs 160-175 ns in PR #4745).
- Adversarial or highly repetitive data: the candidate-then-verify design has O(n\*m) worst case and some 'evil' rows got slower (uint32_t /4 0.49x MSVC and 0.54x Clang on Neoverse N2 in #6139; uint64_t /4 0.71x on the 5950X in #5484); for a linear-time bound use std::boyer_moore_horspool_searcher or a Two-Way memmem.
- Floating-point elements, custom predicates or projections, non-contiguous iterators, constant evaluation, /clr:pure or CHPE builds, or _USE_STD_VECTOR_ALGORITHMS=0: these all take the scalar path.
- You need the speedup on an older toolchain: 4- and 8-byte elements need VS 2026 18.0 and ARM64 needs VS 2026 18.6.

## How it is fast

For 1-byte elements (and 2-byte elements on CPUs without AVX2) it uses the SSE4.2 PCMPESTRC/PCMPESTRI string instructions in 'equal ordered' mode, which test every alignment of a needle of up to 16 bytes against a 16-byte haystack block in one instruction and also report a partial match running off the block end; longer needles match their first 16 bytes that way and memcmp the rest. For 2-, 4- and 8-byte elements on AVX2 (SSE4.2 or NEON otherwise) it broadcasts the first needle element, compares a whole vector of haystack with PCMPEQ to find candidates, and confirms each candidate by XOR-ing one vector load against the needle kept in a register (masked TESTZ), with an inline memcmp for needles longer than a vector. The instruction set is picked per call from the CRT's __isa_enabled / __check_arch_support flags.

## Compared with alternatives

Pick it when you are already on MSVC and want faster std::search, default_searcher or string::find with zero code change, including 2-, 4- and 8-byte element sequences that sliceslice, strstr.c, toys strstr and KmStrSearch do not cover. Pick sliceslice (Rust, AVX2) or KmStrSearch (Windows kernel strstr/wcsstr, 85.93 vs 22.66 GB/s at 1 MB) when you need a dedicated byte searcher outside the C++ standard library or more throughput on large buffers.

## Integration

| | |
|---|---|
| **Form** | part of the toolchain: header-side dispatch plus out-of-line kernels that are linked statically from the STL import/static library (the header notes they are not exported from msvcp140.dll) |
| **Dependencies** | none beyond the MSVC C runtime (CPU-feature flags __isa_enabled / __check_arch_support) |
| **Minimum toolchain** | MSVC STL from VS 2022 17.13 (1- and 2-byte elements), MSVC Build Tools 14.50 / VS 2026 18.0 (4- and 8-byte), 14.51 / VS 2026 18.6 (ARM64 and ARM64EC); std::search works from /std:c++14, ranges::search needs C++20 |
| **Platforms** | Windows; x86 and x64 (SSE4.2 or AVX2 chosen at run time, scalar below SSE4.2), ARM64 and ARM64EC (NEON) |
| **Thread safety** | Same as std::search: pure reads of caller memory; the only shared state is the CRT's read-only CPU-feature flags |
| **Drop-in for the baseline** | yes |

## Gotchas

- The 1-byte regressions quoted from PR #5484 (classic_search&lt;uint8_t&gt; 0.76x-0.78x and the 'evil' /4 case 0.33x on the 5950X) came from an AVX2 8-bit path that PR #5519 removed five days later (merged 2025-05-22, 'Exclude AVX2 search path for 8-bit elements'); current main has the comment 'The AVX2 path for 8-bit elements is not necessarily more efficient than the SSE4.2 cmpestri path' and sends 1-byte search back to the #4745 PCMPESTRI code. #5519 posted no benchmark, so the shipping 1-byte path has no fresh measurement.
- The record's 'x86 and x64 only' is out of date: _VECTORIZED_SEARCH is now on for x64, x86, ARM64 and ARM64EC, with NEON kernels from PR #6139 (merged 2026-03-10); that PR's tables give speedups only, with no baseline named and no absolute times, and its author noted an open MSVC ARM64 codegen problem (DevCom-11053447, stack spills reloaded every loop iteration).
- Every eligible call goes to an out-of-line function with no size threshold in the header; haystacks below 16 bytes (32 for the AVX2 path) fall to a scalar tail inside it, so very small searches pay a non-inlined call.
- The harness (benchmarks/src/search.cpp) repeats the same search on one lorem-ipsum haystack, so caches and branch predictors are warm, and the compiler version is never stated; the c_strstr control in the same binary stayed within 0.97x-1.05x across runs, which supports that the deltas are code changes, though search_default_searcher&lt;uint64_t&gt; moved to 0.74x in #4745 with unchanged code (attributed to loop alignment).

## Known shortcomings

- Baseline is the MSVC STL's own older scalar version with the compiler unstated; 1-byte searches regress (0.76x-0.78x, 0.33x on the evil case) and the strstr control beats the 1-byte search; the uint64 range is 2.37x-3.03x.
- Record corrections: the 1-byte regressions quoted from PR #5484 (0.76-0.78x, 'evil' 0.33x) came from an AVX2 8-bit path that PR #5519 (merged 2025-05-22) removed, sending 1-byte search back to the #4745 PCMPESTRI code; no benchmark was posted after #5519, so the shipping 1-byte path has no fresh measurement. 'x86 and x64 only' is also stale: ARM64 and ARM64EC NEON kernels landed in PR #6139 (14.51 / VS 2026 18.6), whose tables give speedups only with no baseline named (uint32_t 'evil' 0.49x). The C strstr control is still faster than the vectorized 1-byte std::search.

## Caveats and trade-offs

The baseline is the previous scalar MSVC STL std::search, not glibc, libc++/libstdc++ or a third-party searcher, so this is a before/after of one standard library and users get it only by upgrading MSVC. Compiler and version are not stated (the benchmark CMake supports both MSVC and clang-cl); numbers sit in PR comments rather than a standing results file. Single-byte results are mixed: PR #5484 regressed 1-byte classic_search on the 5950X (0.76x-0.78x on /0 and /1) and the adversarial 'evil' 1-byte case (0.33x), and the maintainer said he was 'somewhat concerned about perf regressions for 1-byte search'; the posted numbers may be from an interim revision of the PR, since the author then proposed keeping the SSE4.2 path for 8/16-bit elements. The bundled C strstr control beats the vectorized 1-byte std::search in both PRs (142-143 vs 160 ns in #4745; 138 vs 202 ns in #5484). uint64_t evil case regressed to 0.71x. Filed here because it is SIMD byte-sequence search in a standard library; benchmarks/src/search.cpp now also has member_find (basic_string::find) and classic_find_end, but the PR tables quoted here cover std::search, ranges::search and default_searcher. Merged search-related PRs seen by the search agent: #4654, #4745 (2024-09-09), #5352, #5484 (2025-05-17), #5544. [retier] The baseline is the previous scalar MSVC STL std::search, not glibc, libc++/libstdc++ or a third-party searcher, so this is a before/after of one standard library. Compiler and version are not stated and the numbers sit in PR comments rather than a standing results file. Single-byte status: PR #5484 regressed 1-byte classic_search on the 5950X (0.76x-0.78x, 'evil' case 0.33x) through an AVX2 8-bit path that PR #5519 (merged 2025-05-22, 'Exclude AVX2 search path for 8-bit elements') removed five days later, sending 1-byte search back to the #4745 PCMPESTRI code; #5519 posted no benchmark, so the shipping 1-byte path has no fresh measurement, and the C strstr control (142-162 ns) stays faster than the vectorized 1-byte std::search (160-175 ns). Platforms: _VECTORIZED_SEARCH is on for x64, x86, ARM64 and ARM64EC, with NEON kernels from PR #6139 (merged 2026-03-10, 14.51 / VS 2026 18.6) whose tables give speedups only with no baseline named or absolute times (uint32_t 'evil' 0.49x) and an open MSVC ARM64 codegen problem (DevCom-11053447). Every eligible call goes to an out-of-line function with no size threshold, so very small searches pay a non-inlined call. The harness repeats one search on a lorem-ipsum haystack (warm caches and predictors); search_default_searcher&lt;uint64_t&gt; moved to 0.74x in #4745 with unchanged code (loop alignment).

x86 and x64 only; SSE4.2 and AVX2 kernels are chosen at run time. Applies only to contiguous ranges of simple element types; per a search snippet of Microsoft's docs the vectorized path sits behind the _USE_STD_VECTOR_ALGORITHMS macro and is separately compiled. Specific to MSVC STL, so libstdc++ and libc++ do not benefit.

## Maintenance

Actively maintained (last commit 2026-10-06) and shipped with every Visual Studio; the kernels in stl/src/vector_algorithms.cpp are Apache-2.0 WITH LLVM-exception and could be lifted, but they are written against MSVC's intrin.h and isa_availability.h and are meant to be used through the MSVC STL.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** PR #4745 and PR #5484 carry maintainer before/after tables (Google Benchmark, benchmarks/src/search.cpp, AMD Ryzen 9 5950X) against the previous scalar MSVC STL std::search; the code and the Release flags (/O2 /Ob2 in benchmarks/CMakeLists.txt) are public, but the compiler and version used (MSVC or clang-cl, both supported by that CMake file) are not stated, so first-party with partial methodology stays C.
- **Verifier notes:** Numbers in the record match PR #4745 exactly; the PR #5484 uint64_t range was overstated (2.88x-3.03x omitted /3 at 2.37x and the 0.71x evil regression), now corrected. Shortcomings to record: self-baseline (old MSVC STL), compiler unstated, 1-byte regressions and strstr control faster than the vectorized 1-byte search. Metadata checked: Apache-2.0 WITH LLVM-exception, 11.2k stars, last commit 2026-10-06.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-93 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/microsoft/STL/pull/4745>
  - <https://github.com/microsoft/STL/pull/5484>
  - <https://github.com/microsoft/STL>
  - <https://github.com/microsoft/STL/commits/main>
  - <https://raw.githubusercontent.com/microsoft/STL/main/benchmarks/src/search.cpp>
  - <https://raw.githubusercontent.com/microsoft/STL/main/benchmarks/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/microsoft/STL/pull/4745>
  - <https://github.com/microsoft/STL/pull/5484>
  - <https://github.com/microsoft/STL/pull/5484/commits>
  - <https://github.com/microsoft/STL/pull/5519>
  - <https://github.com/microsoft/STL/pull/6139>
  - <https://github.com/microsoft/STL/pulls?q=is%3Apr+search+vectorization+in%3Atitle>
  - <https://github.com/microsoft/STL/issues?q=is%3Aissue+search+vectorized>
  - <https://github.com/microsoft/STL/wiki/Changelog>
  - <https://raw.githubusercontent.com/microsoft/STL/main/benchmarks/src/search.cpp>
  - <https://raw.githubusercontent.com/microsoft/STL/main/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/microsoft/STL/main/stl/src/vector_algorithms.cpp>
  - <https://raw.githubusercontent.com/microsoft/STL/main/stl/inc/xutility>
  - <https://raw.githubusercontent.com/microsoft/STL/main/stl/inc/algorithm>
  - <https://raw.githubusercontent.com/microsoft/STL/main/stl/inc/functional>
  - <https://raw.githubusercontent.com/microsoft/STL/main/stl/inc/__msvc_string_view.hpp>
  - <https://raw.githubusercontent.com/microsoft/STL/main/stl/inc/yvals_core.h>
  - <https://raw.githubusercontent.com/microsoft/STL/main/README.md>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/microsoft/stl`) · [data/wave13/enrich/raw/github_com_microsoft_stl.json](../../../data/wave13/enrich/raw/github_com_microsoft_stl.json) (enrichment confidence 0.8)

</details>
