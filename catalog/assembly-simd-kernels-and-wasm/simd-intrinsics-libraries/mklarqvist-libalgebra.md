# libalgebra

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0` · 🔴 abandoned

> Header-only x86 C library: SIMD popcount, positional popcount and AND/OR/XOR bitmap cardinalities, with CPUID dispatch.

| | |
|---|---|
| **Beats** | naive scalar code with auto-vectorization disabled (__attribute__((optimize("no-tree-vectorize")))): popcount_scalar_naive_nosimd and intersect/union/diff_scalar_naive_nosimd, which count bits with an 8-bit lookup table (STORM_popcnt_lookup8bit), not the POPCNT instruction |
| **Claimed result** | Popcount: 16.4x at 1024 64-bit words, 21x at 8192, 4.2x at 1048576 (1.0x at 4 words); set-algebra cardinality (AND/OR/XOR): 15.3x at 1024 word pairs, 13.7x at 8192, 2.8x at 1048576, 0.8x at 4; all in CPU cycles per 64-bit word versus an 8-bit lookup-table scalar loop compiled with vectorization disabled. The README also shows a positional-popcount table (up to 138.71x at 65536 values for pospopcnt_u16_avx512_harvey_seal), but those numbers are identical to the mklarqvist/positional-popcount README (measured there with gcc 7.3.1) and are not produced by libalgebra's benchmark.cpp. |
| **Workload** | Popcount, positional popcount and bitmap set-algebra cardinalities (AND/OR/XOR) over arrays of 4 to 1048576 64-bit words, in CPU cycles per word on an AVX512BW machine. |
| **Metric** | throughput |
| **Hardware** | Cannon Lake Core i3-8121U (AVX512BW) |
| **Compiler and flags** | gcc (GCC) 8.2.1 20180905 (Red Hat 8.2.1-3) per README; CMakeLists.txt forces CMAKE_BUILD_TYPE Release and sets CMAKE_CXX_FLAGS to -std=c++11 (CMake's GCC Release default adds -O3 -DNDEBUG); no -march flag, the SSE4.2/AVX2/AVX512BW kernels use __attribute__((target(...))) with CPUID dispatch; run as 'benchmark -p -r 10000' |
| **Adoption** | 45 stars |
| **Last commit** | 2019-12-16 |
| **Links** | [repository](https://github.com/mklarqvist/libalgebra) · [benchmark](https://github.com/mklarqvist/libalgebra) |

## Verdict

On a Cannon Lake Core i3-8121U with gcc 8.2.1 (CMake Release, -O3 -DNDEBUG, -std=c++11, kernels picked by CPUID), minimum user-space cycles per 64-bit word over 10000 runs. The dispatched popcount was 16.4x faster than an 8-bit-lookup scalar loop with vectorization disabled at 1024 words, 21x at 8192 and 4.2x at 1048576; AND/OR/XOR cardinality was 15.3x faster at 1024 word pairs and 2.8x at 1048576 (0.8x at 4). Against a hardware POPCNT loop the gain would be much smaller (catalogued libpopcnt and sse-popcount tables suggest roughly 2-4x; not measured here).

## Use it when

- Counting set bits, or AND/OR/XOR cardinalities, of large bitmaps (hundreds to millions of 64-bit words) on x86-64 with AVX2 or AVX-512BW. The README shows popcount 12-21x over a byte-lookup loop between 512 and 16384 words, falling to about 3-4x once data leaves cache.
- Similarity or overlap scores between dense bitsets (Jaccard or Hamming counts from intersect/union/diff) where you only need the count, not the result bitmap.
- Per-bit-position counts over uint16 flag arrays (for example SAM/BAM FLAG statistics) via STORM_pospopcnt_u16.
- A portable binary built without -march that should still use AVX2/AVX-512 where available, thanks to the target attributes and run-time dispatch.

## Skip it when

- Whenever exact counts matter on arbitrary lengths without your own tests: by reading the code, STORM_popcnt returns wrong counts for many lengths that are not powers of two (see gotchas). Modelling its index arithmetic in Python gave wrong results for 253 of 513 eight-byte-multiple sizes from 0 to 4096 bytes on an AVX-512BW CPU and 450 of 513 on an SSE4.2-only CPU.
- ARM/aarch64: despite the README's NEON claim, the header has no NEON code and includes &lt;x86intrin.h&gt; unconditionally for every non-MSVC compiler, so it does not compile there. Use libpopcnt or std::popcount instead.
- MSVC builds that want SIMD: the SSE/AVX2 kernels are compiled only under /arch:AVX2, where the STORM_TARGET macro expands to a stray `0` before each function (not compiled here). AppVeyor CI builds without /arch, so only the scalar POPCNT path is ever tested on Windows.
- Tiny inputs (under about 32 words): the README shows 0.8-1.4x, so there is nothing to gain.
- If you need a maintained dependency: last commit 2019-12-16, no releases, issues #1 and #5 (int loop counters against size_t lengths) still open.

## How it is fast

It runs the Harley-Seal carry-save-adder popcount from Lemire, Kurz and Mula (2016) with SSE4.2, AVX2 and AVX-512BW. AVX-512 uses vpternlogd for the adder, and AVX2 inputs shorter than 64 words use Mula's pshufb nibble-lookup kernel. Positional popcount uses the Klarqvist/Mula/Lemire blend-popcnt, adder-forest and Harley-Seal kernels. CPUID and XGETBV are read once at run time and the kernel is picked by length, so you need no -march flags.

## Compared with alternatives

Use it only for its one-header bundle of popcount plus AND/OR/XOR cardinalities with run-time dispatch, and only on power-of-two or self-tested lengths. Otherwise prefer the catalogued sources it repackages: libpopcnt for plain popcount, positional-popcount (same author, where the pospopcnt numbers come from) for positional counts, CRoaring for compressed bitmap set algebra, and sse-popcount as the reference kernels. sse-popcount's catalogued run puts AVX-512 Harley-Seal at about 3.6x over a 64-bit POPCNT loop, a fairer yardstick than libalgebra's byte-lookup baseline.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (benchmark.cpp needs Linux perf_event for -p mode) |
| **Minimum toolchain** | SIMD kernels need GCC 4.9+ (AVX-512BW GCC 5+) or Clang 3.8+; benchmark built with -std=c++11; C11 or C++ for the dispatch |
| **Platforms** | x86 / x86-64 only in practice (SSE4.2, AVX2, AVX-512BW chosen at run time); no NEON code despite the README |
| **Thread safety** | not documented; dispatch caches CPUID in a function-local static (C++11 magic static, or a __sync CAS in C) and the kernels are pure functions of read-only input, so concurrent calls look safe |
| **Drop-in for the baseline** | partial — no std:: equivalent; it replaces a hand-written popcount or AND+popcount loop, with byte lengths for STORM_popcnt, 16-bit-value counts for pospopcnt and 64-bit-word counts for set algebra |

## Gotchas

- Correctness bugs in STORM_popcnt's remainder handling (found by reading libalgebra.h at the 2019-12-16 head; not compiled, since the enrichment rules forbid building). (1) STORM_popcnt_csa_sse4 and the SSE intersect/union/diff CSA kernels end with `cnt64 = STORM_POPCOUNT_SSE(...)` instead of `+=`, so whenever the 128-bit vector count is not a multiple of 16 they return only the last vector's popcount; this path serves 256-511 byte inputs on every SSE4.2+ CPU. (2) STORM_popcnt_avx2 points its SSE tail at &data[n_cycles_sse\*4] instead of &data[n_cycles\*4], so it double-counts words 4-5 and drops the last two words when n_words % 4 is 2 or 3 (512-1023 bytes on AVX-512 CPUs, all sizes from 512 bytes on AVX2 CPUs). (3) STORM_popcnt_avx512 starts its scalar tail at 8\*n_cycles + 4\*n_cycles instead of 4\*n_cycles_avx2, so it drops the last word of any odd-word input of 1024 bytes or more. Example from the model: 272 bytes gives 67 instead of 1100 on AVX-512BW. On AVX2/AVX-512 machines the set-algebra kernels are correct; on SSE4.2-only CPUs intersect/union/diff are wrong for 1890 of 2017 lengths from 32 to 2048 words.
- The benchmark cannot catch these bugs: every tested size is a power of two (4 to 1048576 words), the popcount cross-check `assert(a == b)` is removed by the Release build's -DNDEBUG, and the set-algebra path has no check at all. The published speedups therefore come only from the bug-free power-of-two paths.
- The README overstates and misdocuments the API: it names STORM_get_intersection_count_func, but the header defines STORM_get_intersect_count_func. It says pospopcnt's size is in bytes, but the code loops over len uint16 values, so passing a byte count reads twice past the buffer. The pospopcnt speedup table is copied from mklarqvist/positional-popcount, and benchmark.cpp never runs pospopcnt.
- Harness details: cycles are user-space perf counters, minimum of 10000 single calls, with freshly generated (cache-hot) data before each call; at 4-32 words the ioctl fringe dominates. LinuxEvents never sizes its `ids` vector before ioctl(PERF_EVENT_IOC_ID, &ids[i]) (undefined behaviour; the return is unchecked) and closes only the last of six perf fds per call (about 760 leaked over a full run). The scalar set-algebra fallback uses inline-asm popcnt without a CPUID check.

## Known shortcomings

- Raised C to A: popcount and set-algebra rows reproducible (benchmark.cpp, CMake Release -std=c++11, gcc 8.2.1, i3-8121U), but the baseline is an 8-bit lookup-table loop with vectorization off rather than POPCNT, NDEBUG removes the correctness check, and the 138.71x pospopcnt table is copied from positional-popcount (same author, same kernels), not measured here. Abandoned since 2019.
- Correctness bugs found by reading libalgebra.h (not compiled): the SSE CSA remainder loops assign 'cnt64 =' instead of '+=', STORM_popcnt_avx2's SSE tail points at &data[n_cycles_sse\*4], and STORM_popcnt_avx512's tail starts at 4\*n_cycles instead of 4\*n_cycles_avx2; a Python model of the index math gives wrong STORM_popcnt results for 253 of 513 sizes between 0 and 4096 bytes on AVX-512 (272 B gives 67 vs 1100) and 450 of 513 on SSE4.2-only CPUs, and wrong SSE-only set algebra for 1890 of 2017 lengths. The benchmark tests only power-of-two sizes and NDEBUG removes the assert, so the published numbers are unaffected. No NEON code despite the README; unconditional x86intrin.h (no ARM build); README API name and pospopcnt size unit wrong; the perf harness has undefined behaviour in ids and leaks fds; the baseline is an 8-bit lookup loop.

## Caveats and trade-offs

Baseline is a deliberately naive 8-bit lookup-table loop with vectorization disabled (about 8.1 cycles per 64-bit word for popcount, 5.0 for set algebra), not the POPCNT instruction or __builtin_popcountll, so the speedups overstate the gain over a tuned scalar loop. The positional-popcount table in the README is copied from mklarqvist/positional-popcount (same numbers, measured there with gcc 7.3.1); libalgebra's benchmark.cpp does not benchmark pospopcnt. The library packages kernels from positional-popcount and the Lemire/Kurz/Mula AVX2 popcount work (sse-popcount), so it overlaps with those entries. Release build defines NDEBUG, so the assert(a == b) correctness check in the perf popcount path is compiled out and the set-algebra path has no check. Single machine; data freshly generated each iteration and cache-resident (README calls it a practical upper limit). No commits since 2019-12-16. [retier] Baseline is a deliberately naive 8-bit lookup-table loop with vectorization disabled (about 8.1 cycles per 64-bit word for popcount, 5.0 for set algebra), not the POPCNT instruction or __builtin_popcountll. Correctness bugs (found by reading libalgebra.h at the 2019-12-16 head, modelled in Python, not compiled): the SSE CSA remainder loops (STORM_popcnt_csa_sse4 and the SSE intersect/union/diff kernels) end with 'cnt64 = STORM_POPCOUNT_SSE(...)' instead of '+=', STORM_popcnt_avx2 points its SSE tail at &data[n_cycles_sse\*4], and STORM_popcnt_avx512's tail starts at 4\*n_cycles rather than 4\*n_cycles_avx2; STORM_popcnt therefore returns wrong counts for 253 of 513 sizes between 0 and 4096 bytes on AVX-512 (272 B gives 67 vs 1100) and 450 of 513 on SSE4.2-only CPUs, and the SSE-only set algebra is wrong for 1890 of 2017 lengths. The benchmark tests only power-of-two sizes (4 to 1048576 words), the popcount cross-check assert is removed by -DNDEBUG and the set-algebra path has no check, so the published speedups come only from the bug-free power-of-two paths. The positional-popcount table in the README is copied from mklarqvist/positional-popcount (benchmark.cpp never runs pospopcnt), the README misnames STORM_get_intersect_count_func and gives pospopcnt's size in bytes where the code loops over uint16 values, there is no NEON code despite the README and x86intrin.h is included unconditionally, the perf harness never sizes its ids vector before ioctl and leaks five of six perf fds per call, and the scalar set-algebra fallback uses inline-asm popcnt without a CPUID check. The library packages kernels from positional-popcount and the Lemire/Kurz/Mula AVX2 popcount work.

Header-only C/C++ library using POPCNT, SSE4.2, AVX2, AVX512BW and NEON; tested with GCC, Clang and MSVC per the README.

## Maintenance

Abandoned since 2019-12-16 (45 stars, no releases) and Apache-2.0, so it is easy to vendor as one header, but fix the three remainder bugs (cnt64 = vs +=, the AVX2 SSE-tail pointer, the AVX-512 tail index) and test non-power-of-two lengths before trusting its counts.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Upgraded C to A for the popcount and set-algebra rows: benchmark code is public (benchmark.cpp, run as 'benchmark -p -r 10000' with Linux perf counters against popcount_scalar_naive_nosimd and \*_scalar_naive_nosimd), the compiler (gcc 8.2.1 20180905) and CPU (Core i3-8121U Cannon Lake) are stated in the README, and the flags come from the public CMakeLists.txt (CMAKE_BUILD_TYPE Release, CMAKE_CXX_FLAGS -std=c++11, so CMake's GCC Release default -O3 -DNDEBUG; kernels picked at run time via target attributes, so no -march is needed). The README's pospopcnt table is not produced by this repo's benchmark: it is copied unchanged from mklarqvist/positional-popcount.
- **Retiered** A to C: Enricher: the remainder handling in libalgebra.h is wrong (SSE CSA loops assign instead of accumulate; AVX2 and AVX-512 tails index from the wrong offset), so STORM_popcnt returns wrong counts for 253 of 513 sizes between 0 and 4096 bytes on AVX-512 and 450 of 513 on SSE4.2-only CPUs, and SSE-only set algebra is wrong for most lengths; the published numbers come only from the bug-free power-of-two paths and the Release build removes the assert that would catch it. Correctness bug in the hot path on real input sizes (uniwidth precedent), still unfixed: A to C.
- **Verifier notes:** Numbers on the README match the record exactly. Upgraded to A because CMakeLists.txt pins the build (Release, -std=c++11) and benchmark.cpp runs the named naive baselines; the record wrongly said no build file existed. The pospopcnt claim belongs to positional-popcount (batch-10), so the orchestrator may want libalgebra listed on its popcount and set-algebra rows only, or folded as a near-duplicate; the weak lookup-table baseline should be recorded as a shortcoming.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-12 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/mklarqvist/libalgebra>
  - <https://github.com/mklarqvist/libalgebra/commits>
  - <https://raw.githubusercontent.com/mklarqvist/libalgebra/HEAD/README.md>
  - <https://raw.githubusercontent.com/mklarqvist/libalgebra/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/mklarqvist/libalgebra/HEAD/benchmark.cpp>
  - <https://raw.githubusercontent.com/mklarqvist/libalgebra/HEAD/.travis.yml>
  - <https://raw.githubusercontent.com/mklarqvist/libalgebra/HEAD/libalgebra.h>
  - <https://raw.githubusercontent.com/mklarqvist/positional-popcount/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/mklarqvist/libalgebra>
  - <https://github.com/mklarqvist/libalgebra/commits>
  - <https://github.com/mklarqvist/libalgebra/issues?q=is%3Aissue>
  - <https://github.com/mklarqvist/libalgebra/issues/1>
  - <https://github.com/mklarqvist/libalgebra/issues/5>
  - <https://raw.githubusercontent.com/mklarqvist/libalgebra/HEAD/README.md>
  - <https://raw.githubusercontent.com/mklarqvist/libalgebra/HEAD/libalgebra.h>
  - <https://raw.githubusercontent.com/mklarqvist/libalgebra/HEAD/benchmark.cpp>
  - <https://raw.githubusercontent.com/mklarqvist/libalgebra/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/mklarqvist/libalgebra/HEAD/.travis.yml>
  - <https://raw.githubusercontent.com/mklarqvist/libalgebra/HEAD/appveyor.yml>
  - <https://raw.githubusercontent.com/mklarqvist/libalgebra/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/mklarqvist/libalgebra/HEAD/.gitignore>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/mklarqvist/libalgebra`) · [data/wave13/enrich/raw/github_com_mklarqvist_libalgebra.json](../../../data/wave13/enrich/raw/github_com_mklarqvist_libalgebra.json) (enrichment confidence 0.75)

</details>
