# SSE2 itoa (Muła algorithm, via miloyip/itoa-benchmark)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Number parsing and formatting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> SSE2-vectorized itoa for uint32/int32/uint64/int64 in Milo Yip's benchmark repo; 25.51x faster than sprintf on 9-10 digit values.

| | |
|---|---|
| **Beats** | sprintf (C stdio); std::ostringstream/std::to_string also tested but disabled by default with no numbers published on this page |
| **Claimed result** | 25.51x faster than sprintf() (verbatim, page's own Speedup column: sse2 7.614ns vs sprintf 194.225ns) -- the fastest contender in this shootout, ahead of branchlut (23.04x) and countlut (19.57x) |
| **Workload** | Sequential case: convert consecutive uint32_t values across 1-10 decimal-digit groups to ASCII, 100,000 reps per group, min of 10 trials. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7 920 @ 2.67GHz |
| **Compiler and flags** | Visual C++ 2013, Win64; release config via premake5 flags {"Optimize"} + NDEBUG (build/premake5.lua); literal compiler flags not stated |
| **Adoption** | 341 stars (benchmark repo hosting the implementation, at src/sse2.cpp) |
| **Last commit** | 2025-02-10 |
| **Links** | [repository](https://github.com/miloyip/itoa-benchmark) · [benchmark](https://github.com/miloyip/itoa-benchmark) |

## Verdict

On the repo's own README table (Core i7 920 @2.67GHz, Visual C++ 2013, Win64 release build), the SSE2 u32toa implementation averages 7.614 ns per call vs sprintf's 194.225 ns across the sequential 1-10 digit benchmark (100,000 reps/group, min of 10 trials) -- a 25.51x speedup, ahead of branchlut (23.04x) and countlut (19.57x) in the same table; std::ostringstream/std::to_string are compiled out by default (RUN_CPPITOA macro) and have no published numbers on this page.

## Use it when

- Hot-path serialization of high-volume 32-bit or especially 64-bit integers to decimal ASCII (logging, JSON/CSV writers, wire protocols) where sprintf's format-string parsing is the bottleneck.
- Your integers are frequently large (9-10 digit uint32_t, or most uint64_t/int64_t values) -- the only range where this file's SIMD path actually runs instead of falling back to scalar/LUT code.
- x86 or x86-64 targets that guarantee SSE2 (default on effectively all x86-64 CPUs); no ARM or other-arch support needed.
- You're willing to hand-extract two files (sse2.cpp + digitslut.h) from a benchmark harness, strip the REGISTER_TEST macro/test.h dependency, and own buffer-size correctness yourself since there is no bounds checking.

## Skip it when

- You need a maintained, versioned library rather than one file inside a 10+-implementation benchmark shootout with issues and PRs open since 2016 and no formal releases.
- Non-x86 targets: the file compiles to nothing outside `#if defined(i386) || __amd64 || _M_IX86 || _M_X64`, with no portable fallback provided.
- Values are mostly 1-8 decimal digits -- the SIMD kernel is dead code there by the author's own admission, so you get the same LUT-pair scalar performance as branchlut/countlut without SSE2's added complexity.
- You need std::to_chars-style safety (returned end pointer, error reporting, no overflow) -- this API just writes to a raw buffer with zero bounds checking.
- You want the speedup verified independently or on current hardware -- the only published numbers are first-party, from a Core i7 920 (2010-era) with Visual C++ 2013, and the std:: baselines (ostringstream/to_string) were never enabled for this table.

## How it is fast

For short values (&lt;10^8 for u32, &lt;10^16 for u64) the code falls back to the same digit-pair lookup table (gDigitsLut) used by the repo's lut/countlut/branchlut entries -- the SIMD path there is wrapped in #if 0 because, per the author's own comment, experiments found SSE2 slower in that range. For 9-10 digit u32 values and all u64 conversions it runs Wojciech Mula's SSE2 algorithm (Convert8DigitsSSE2): a chain of SIMD multiply-high/shift operations divides 8 decimal digits by powers of ten in parallel in a 128-bit register, packs the results into ASCII bytes with _mm_packus_epi16, then uses a movemask/ctz trick to trim leading zeros.

## Compared with alternatives

Most siblings in this category target floating-point/general charconv (Boost.Charconv, c4core, fast_double_parser, fpconv, double-conversion, milo Grisu2) or a broader iostream replacement (rigtorp CharConv, fast_io, stb_sprintf); pick this one specifically when you want a SIMD kernel for many-digit unsigned/signed 32- or 64-bit integers on x86 and are fine hand-extracting it from a benchmark harness -- jeaiii/itoa is the closer apples-to-apples sibling (also integer-only, from a similar shootout) but is header-only, scalar, and easier to vendor without SSE2 intrinsics.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | digitslut.h (200-byte const lookup table, in-repo); test.h is only needed for the REGISTER_TEST self-registration macro used by the benchmark harness and must be stripped/replaced to vendor standalone |
| **Minimum toolchain** | not documented; source uses &lt;cassert&gt;, &lt;stdint.h&gt;, and &lt;emmintrin.h&gt; SSE2 intrinsics with no C++11-only syntax, so most C++ toolchains with SSE2 intrinsic support should compile it (published results used Visual C++ 2013) |
| **Platforms** | x86/x86-64 only, guarded by #if defined(i386) \|\| defined(__amd64) \|\| defined(_M_IX86) \|\| defined(_M_X64); requires SSE2 (baseline on all x86-64; needs explicit enabling on some 32-bit x86 toolchains); no fallback for other architectures in this file |
| **Thread safety** | not documented; by inspection the functions are stateless, writing only to the caller-supplied buffer and reading only from const static tables, so concurrent calls on distinct buffers should be safe |
| **Drop-in for the baseline** | partial — explain: different call shape than sprintf (writes null-terminated ASCII into a caller buffer, no format string, no returned length, no bounds checking), so it's a manual per-call-site swap rather than a signature-compatible replacement |

## Gotchas

- Issue #8 (closed) flagged that i32toa_sse2/i64toa_sse2 previously computed `value = -value` on the most-negative int, which is signed-overflow UB and reportedly segfaulted on g++ 4.9.1; the code read this session already uses the recommended two's-complement fix (`u = ~u + 1`).
- No bounds checking: caller must size the buffer correctly (worst case \~11 bytes incl. sign/null for i32, \~21 for i64) or risk a buffer overflow.
- The vectorized 8-digit SSE2 kernel (Convert8DigitsSSE2) is dead code for u32toa values under 100,000,000 -- that branch is behind #if 0 with a comment that SSE2 measured slower there, so most 1-8-digit conversions actually run the same scalar/LUT-pair code as the branchlut/countlut entries, not SIMD.
- Uses 16-byte-aligned static constant tables (ALIGN_PRE/ALIGN_SUF macros); if copy-pasting only part of the file, bring the matching aligned constants along.

## Caveats and trade-offs

First-party numbers: the SSE2 code lives in and is benchmarked by the author's own repo. The README says the C++ std implementations (ostringstream, ostrstream, std::to_string) are 'turned off by default', and none of the committed result CSVs (including corei7-6700K linux gcc5.3) contain std numbers, so sprintf is the only baseline. Per the README, SSE2 helps mainly for values of 9 or more digits. Hardware and compiler are old (Core i7 920, VC++2013).

SIMD (SSE2) implementation only handles unsigned 32-bit integers in this benchmark; not packaged as a standalone library, lives at src/sse2.cpp inside the benchmark repo and would need extraction/generalization (signed, 64-bit) to vendor; requires x86 SSE2.

## Maintenance

Not a maintained library in its own right: it's one implementation file inside a community benchmark repo that still gets sporadic commits/PRs (last push 2025-02-10) but has open issues and PRs dating back to 2016 and no versioned releases; MIT-licensed and small (\~250 lines plus a header), so it's cheap to vendor and re-audit yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now C.
- **Tier reason:** The README table has sse2 at 7.614 ns (25.51x) vs sprintf at 194.225 ns, and branchlut at 23.04x and countlut at 19.57x, all verbatim. The cataloged project is the benchmark repo itself (src/sse2.cpp, Milo Yip's implementation of Muła's algorithm), so these are first-party numbers. Literal flags are not stated (build/premake5.lua has flags {"Optimize"} for release), so not A; C.
- **Verifier notes:** Metadata checks out: MIT, 341 stars, last commit 2025-02-10 (stale), not a fork, not archived. Downgraded from B to C because the benchmark is the project's own; the numbers themselves are accurate.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/miloyip/itoa-benchmark>
  - <https://github.com/miloyip/itoa-benchmark/blob/master/build/premake5.lua>
  - <https://github.com/miloyip/itoa-benchmark/tree/master/result>
- **Sources the enricher read:**
  - <https://github.com/miloyip/itoa-benchmark>
  - <https://github.com/miloyip/itoa-benchmark/blob/master/readme.md>
  - <https://github.com/miloyip/itoa-benchmark/blob/master/src/sse2.cpp>
  - <https://github.com/miloyip/itoa-benchmark/blob/master/src/test.h>
  - <https://github.com/miloyip/itoa-benchmark/blob/master/src/digitslut.h>
  - <https://github.com/miloyip/itoa-benchmark/blob/master/license.txt>
  - <https://github.com/miloyip/itoa-benchmark/issues/8>
  - <https://github.com/miloyip/itoa-benchmark/issues>
  - <https://github.com/miloyip/itoa-benchmark/pulls>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/miloyip/itoa-benchmark`) · [data/wave1/enrich/raw/github_com_miloyip_itoa_benchmark.json](../../../data/wave1/enrich/raw/github_com_miloyip_itoa_benchmark.json) (enrichment confidence 0.6)

</details>
