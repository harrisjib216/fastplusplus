# sse4-strstr (SIMD-friendly algorithms for substring searching)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [String search and hashing](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSD-2-Clause` · 🔴 abandoned

> SIMD substring-search kernels (SSE2-AVX512, NEON) from a blog article; beats glibc strstr by \~1.3-1.8x on x86.

| | |
|---|---|
| **Beats** | std::strstr / libc strstr (same problem as std::string::find and the default std::search) |
| **Claimed result** | std::strstr: 0.662s vs AVX2 (generic) kernel: 0.364s -&gt; \~1.82x faster (derived from page data); SSE2 (generic): 0.489s -&gt; \~1.35x faster (derived from page data). Other machines in the results folder (Haswell, Cascade Lake, Knights Landing, ARMv7/ARMv8) show similar or larger gaps. |
| **Workload** | Scan a fixed text corpus (data/i386.txt) for a word list (data/words) with SWAR/SSE2/SSE4.1/SSE4.2/AVX2 substring-search kernels vs std::strstr, timed end-to-end, on an Intel Skylake i7-6700 with GCC 5.4.1. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-6700 (Skylake) for the cited number. results/ also covers ARMv7, ARMv8 (Clang 3.8.0), AMD Bulldozer FX-8510, Intel Haswell i7-4770, Knights Landing 7210, Skylake i9-7900, Cascade Lake Xeon Gold 5217, and Westmere M540. |
| **Compiler and flags** | g++ -std=c++11 -O3 -Wall -Wextra -pedantic -I. -DHAVE_SSE_INSTRUCTIONS -mavx2 -DHAVE_AVX2_INSTRUCTIONS -DNDEBUG (current Makefile speedup_avx2 target). GCC 5.4.1 for the cited result (from the result filename). results/ also has GCC 4.8.4-7.4.0 and Clang 3.8.0 runs on other CPUs. |
| **Adoption** | 266 stars |
| **Last commit** | 2022-01-04 |
| **Links** | [repository](https://github.com/WojciechMula/sse4-strstr) · [benchmark](https://github.com/WojciechMula/sse4-strstr/blob/master/results/skylake-i7-6700-gcc5.4.1-avx2.txt) |

## Verdict

On an Intel Skylake i7-6700 with GCC 5.4.1 (-O3 -mavx2), the repo's own speedup_avx2 benchmark scanning data/i386.txt for data/words shows glibc std::strstr at 0.662s vs the "AVX2 (generic)" kernel at 0.364s across three runs with identical checksums (\~1.82x faster); "SSE2 (generic)" is 0.489s (\~1.35x faster). std::string::find is not measured on this run -- the harness skips it on GCC/x86.

## Use it when

- Exact single fixed-needle search over large in-memory byte buffers (logs, text corpora) on x86-64 with SSE4.1/AVX2/AVX512, or ARMv7/AArch64 with NEON, where the scan itself is the bottleneck
- You want reference/teaching code for SIMD substring-search techniques (the vectorized Karp-Rabin-style first/last-byte filter) rather than a dependency
- You can vendor a handful of individual .cpp/.h files into your own build instead of linking a packaged library
- Needle length and target ISA are known ahead of time so you can pick/compile the matching kernel (SSE4, AVX2, AVX512BW, NEON) for your CPU
- You're willing to own and patch the code yourself going forward -- no upstream maintenance since Jan 2022

## Skip it when

- You need a drop-in for std::string::find/strstr with wide-char support, custom predicates, or a std::string_view-friendly API -- none of that exists here
- You need multi-needle or streaming search; only a single fixed needle against a fully-buffered haystack is implemented (open issue #18 asks for multithreading, #19 for combining with Raita's algorithm -- both unaddressed)
- You need a maintained, packaged dependency: no releases, no build-system package config, last commit 2022-01-04, and confirmed bugs (#11, #16) are unfixed
- Needle length 1 passed directly to the low-level avx2_strstr_anysize kernel (bypassing the dispatcher) hits a confirmed bug: k-2 underflows (issue #11)
- On current hardware/libc the maintainer himself says (issue #12, 2020) "AVX2 won't help much" over a decent modern strstr -- re-benchmark on your own CPU/libc before adopting

## How it is fast

SWAR and SIMD kernels (SSE2, SSE4.1 MPSADBW, SSE4.2 PCMPESTRM, AVX2, AVX512F/BW, NEON) scan 16-64 bytes per iteration instead of glibc strstr's byte-at-a-time loop. The fastest "generic" kernel behind the cited 1.82x number (avx2_strstr_v2 -&gt; avx2_strstr_anysize) broadcasts the needle's first and last byte across a 32-byte AVX2 vector, compares both in one pass to get a lane mask of candidate offsets, then verifies each candidate with a short memcmp -- a vectorized two-byte filter (0x80.pl's "SIMD-friendly Karp-Rabin" scheme), not a per-byte scan. Needles of length 2-12 get separate template-specialized SSE4.1/AVX2 kernels tuned per exact length.

## Compared with alternatives

Pick this over StringZilla or Boost.Algorithm's Boyer-Moore/Boyer-Moore-Horspool searchers only when you specifically want the raw, ISA-specific kernel source to vendor one function with zero dependencies (no Boost, no StringZilla) or to study the 0x80.pl vectorized Karp-Rabin technique; both siblings are actively packaged and maintained, and StringZilla in particular reports larger, more current speedups over std::string::find.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (uses &lt;immintrin.h&gt;/&lt;arm_neon.h&gt; intrinsics and the C++11 standard library only) |
| **Minimum toolchain** | C++11; GCC or Clang with the matching ISA flag per kernel (-msse4.2, -mavx2, -mavx512bw, -mfpu=neon) |
| **Platforms** | x86-64 (SSE2 baseline; SSE4.1/4.2, AVX2, AVX512F/AVX512BW variants gated by build flags), ARMv7 (NEON) and ARMv8/AArch64 |
| **Thread safety** | not documented -- kernels are pure functions with no shared mutable state, but there is no synchronization code anywhere in the repo, and issue #18 (open) requests multithreading support |
| **Drop-in for the baseline** | partial -- explain: the top-level function signature/return convention mirrors std::string::find (offset or npos) rather than strstr's null-terminated char\* return, and using it means vendoring specific kernel files plus manual dispatch by needle length and target ISA rather than including one header |

## Gotchas

- Raw per-length kernels (e.g. avx2_strstr_anysize, sse4_strstr_anysize) assert needle_size &gt; 4 or &gt; 0 depending on variant; only the top-level dispatchers (avx2_strstr, avx2_strstr_v2, sse4_strstr_anysize's callers) special-case short needles (0-4 bytes) via strchr/strstr/memcmp -- calling a raw kernel directly with a short needle is unsafe (issue #11, confirmed bug for k=1)
- The vectorized loops load fixed 16/32-byte windows (_mm256_loadu_si256 at s+i and s+i+k-1) per iteration, which can read past the logical end of the haystack near its tail; the README/code does not document a guaranteed-safe overread margin, so vendoring into a tightly-sized buffer needs care
- Open, unanswered GitHub issue (#16) questions whether the `next1` vector in avx2_strstr_eq (the 2-byte-needle path) is read before being fully initialized
- The repo's own speedup.cpp deliberately skips std::string::find on GCC/x86 builds ("proven to be utterly slow, don't waste our time"), so its own benchmark has no std::string::find numbers to compare against on x86

## Caveats and trade-offs

Companion sample code for a 2016-era article on SIMD substring search. Last commit January 2022 (abandoned). The \~1.8x figure is for one kernel/CPU pairing, and results vary widely by kernel and machine in results/. The 'std::strstr' row is the unqualified C strstr (glibc on the GCC/Linux runs), not the generic std::search. speedup.cpp deliberately skips std::string::find on GCC builds ('proven to be utterly slow'), so it has no numbers on x86.

Companion code for a blog article (0x80.pl), not a packaged library -- integrating it means vendoring individual .cpp/.h kernels rather than linking a target; only exact single-needle substring search is covered (no wide-char, no custom predicates, no std::string_view-style API).

## Maintenance

Abandoned: last commit 2022-01-04, not archived, two confirmed/unanswered bugs (#11, #16) unaddressed; BSD-2-Clause and small enough to vendor a single kernel file, but the maintainer himself notes (2020) that on modern CPUs/libc the AVX2 advantage over strstr is small.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** The results file shows std::strstr 0.662049 s vs AVX2 (generic) 0.363694 s (three runs, identical checksums). The code is public (src/speedup.cpp, Makefile speedup_avx2 target with -O3 -mavx2). The compiler (GCC 5.4.1) and CPU (i7-6700) are stated in the result filename.
- **Verifier notes:** Numbers match the result file exactly. libc++ is not evidenced: all x86 runs are GCC, and the baseline is glibc strstr. Metadata verified: BSD-2-Clause, 266 stars, last commit 2022-01-04, not archived.
- **Fields the verifier corrected:** `baseline_stdlib`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/WojciechMula/sse4-strstr/blob/master/results/skylake-i7-6700-gcc5.4.1-avx2.txt>
  - <https://github.com/WojciechMula/sse4-strstr>
  - <https://github.com/WojciechMula/sse4-strstr/blob/master/Makefile>
  - <https://github.com/WojciechMula/sse4-strstr/blob/master/src/speedup.cpp>
  - <https://github.com/WojciechMula/sse4-strstr/blob/master/README.rst>
  - <https://github.com/WojciechMula/sse4-strstr/tree/master/results>
- **Sources the enricher read:**
  - <https://github.com/WojciechMula/sse4-strstr>
  - <https://github.com/WojciechMula/sse4-strstr/blob/master/README.rst>
  - <https://github.com/WojciechMula/sse4-strstr/blob/master/Makefile>
  - <https://github.com/WojciechMula/sse4-strstr/blob/master/common.h>
  - <https://github.com/WojciechMula/sse4-strstr/blob/master/src/speedup.cpp>
  - <https://github.com/WojciechMula/sse4-strstr/blob/master/src/all_procedures.cpp>
  - <https://github.com/WojciechMula/sse4-strstr/blob/master/avx2-strstr.cpp>
  - <https://github.com/WojciechMula/sse4-strstr/blob/master/avx2-strstr-v2.cpp>
  - <https://github.com/WojciechMula/sse4-strstr/blob/master/sse4-strstr.cpp>
  - <https://github.com/WojciechMula/sse4-strstr/blob/master/results/skylake-i7-6700-gcc5.4.1-avx2.txt>
  - <https://github.com/WojciechMula/sse4-strstr/issues/11>
  - <https://github.com/WojciechMula/sse4-strstr/issues/12>
  - <https://github.com/WojciechMula/sse4-strstr/issues/15>
  - <https://github.com/WojciechMula/sse4-strstr/issues/16>
  - <https://github.com/WojciechMula/sse4-strstr/issues>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/wojciechmula/sse4-strstr`) · [data/wave1/enrich/raw/github_com_wojciechmula_sse4_strstr.json](../../../data/wave1/enrich/raw/github_com_wojciechmula_sse4_strstr.json) (enrichment confidence 0.82)

</details>
