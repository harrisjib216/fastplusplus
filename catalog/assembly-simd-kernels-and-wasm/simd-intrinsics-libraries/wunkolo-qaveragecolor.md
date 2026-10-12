# qAverageColor

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 slow

> SIMD (psadbw, AVX2, AVX-512) mean colour of an RGBA8 pixel buffer; AVX2 path 2.6-5.4x faster than a scalar loop.

| | |
|---|---|
| **Beats** | serial (scalar C++) average-colour routine in the same repo |
| **Claimed result** | Speedup over the serial version, AVX2: 4.41x (i7-7500U), 4.24x (i3-6100), 2.65x (i5-8600K), 2.61x (i9-7900X), 4.62x (i7-1065G7), 5.35x (i9-11900K). SSE4.2: 2.07x to 4.24x (column not rebuildable from the public CMake). The README's AVX-512 rows (4.27x i9-7900X, 5.47x i7-1065G7, 6.09x i9-11900K) are struck: both AVX-512 paths sum the wrong pixels (see caveats). |
| **Workload** | Average colour of RGBA8 pixels: tests/BigBench.cpp times one call each of the serial AverageColorRGBA8 and qAverageColorRGBA8 over 10,000,000 pixels all set to 0xBEEFFEEB (table); tests/AverageColor.cpp does the same on a loaded 3840x2160 image (write-up). Paths: psadbw byte sums (SSE4.2, AVX2, AVX-512F) and vpdpbusd (AVX-512 VNNI). |
| **Metric** | throughput |
| **Hardware** | Intel i7-7500U, i3-6100, i5-8600K, i9-7900X, i7-1065G7, i9-11900K (README table) |
| **Compiler and flags** | GCC 8.2.1 (README footnote, one footnote for rows added 2019-2021); CMakeLists.txt: CMAKE_BUILD_TYPE Release (CMake default -O3 -DNDEBUG) with -march=native -Wall -Wextra, C++17 with GNU extensions; the serial baseline and SIMD paths are compiled with the same flags |
| **Adoption** | 50 stars |
| **Last commit** | 2021-04-17 |
| **Links** | [repository](https://github.com/Wunkolo/qAverageColor) · [benchmark](https://github.com/Wunkolo/qAverageColor) |

## Verdict

README table: one timed call each of the scalar loop and the SIMD routine over 10,000,000 identical 0xBEEFFEEB pixels, GCC 8.2.1 with -O3 -march=native, on six Intel CPUs (rows added 2019-2021): AVX2 2.61x (i9-7900X) to 5.35x (i9-11900K), SSE4.2 2.07x to 4.24x, AVX-512 4.27x to 6.09x. The README's real-image runs (3840x2160 on an i7-7500U) give 2.63x (SSE) and 4.13x (AVX2) with output identical to the scalar result; AVX-512 was measured only on the uniform image, which masks the AVX-512 shuffle bug.

## Use it when

- Mean colour of large RGBA8 buffers (dominant-colour placeholders, thumbnails, auto-exposure statistics) on x86-64 with AVX2, where a scalar loop is the hot spot.
- Contiguous, tightly packed 32-bit pixels: whole images or whole tiles, not strided sub-rectangles.
- As a copyable reference for the psadbw byte-sum technique when writing RG8, R8 or RGB8 variants (the README sketches the RGB8 shuffle cases).
- Deployments built for the target machine, where -march=native or a fixed AVX2 target is acceptable.

## Skip it when

- Any AVX-512 build without patching: both AVX-512 paths (AVX512F and VNNI) feed full-register byte indices to the in-lane _mm512_shuffle_epi8, so the result is correct only for uniform images. Build with -mno-avx512f (AVX2 path) or replace the shuffle (for example vpermb on AVX512_VBMI).
- main branch with MSVC: the VNNI path is compiled whenever _MSC_VER is defined while CMake sets /arch:AVX2, so the binary executes vpdpbusd zmm on every CPU (illegal instruction without AVX512_VNNI); the dev branch disabled this on 2024-08-27.
- main branch on buffers that are not 16-byte aligned: the SSE tail loop uses _mm_stream_load_si128 (movntdqa), which faults on a misaligned address when Count % 8 &gt;= 4; dev replaced it with unaligned loads in 2024.
- Count == 0 divides by zero (so does the baseline); means are truncated, not rounded; no premultiplied-alpha, linear-light or padded-row handling.
- Portable binaries that need runtime CPU dispatch, or non-x86 targets on main (the dev branch adds AArch64 UDOT/UADDW and optional Apple AMX paths, with no published numbers).

## How it is fast

pshufb groups each channel's bytes into 64-bit lanes, then psadbw against zero (Wojciech Mula's sum-of-bytes trick) adds eight bytes per lane straight into 64-bit accumulators, so there is no per-pixel unpack or widening. The AVX2 loop takes 8 pixels per iteration with an in-lane vpshufb plus a cross-lane vpermd; the AVX-512F path takes 16 with vpsadbw, and the AVX-512 VNNI path uses vpdpbusd against a vector of ones into 32-bit accumulators that are flushed to 64-bit every 0x404040 iterations. The path is picked at compile time from -march=native macros; there is no runtime dispatch.

## Compared with alternatives

Pick it when the job is specifically per-channel means of packed RGBA8 pixels; ParallelReductionsBenchmark covers float sums and simd-adler32 uses the same byte-sum idea for checksums, while bilinear_filter_simd and ARM NEON Compositor are other image kernels, not reductions.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the library (one .cpp plus one header); stb_image only for the AverageColor test; the dev branch's unit tests use Catch2 v3 |
| **Minimum toolchain** | main: C++17 with GNU extensions, CMake 3.2.2, GCC 8.2.1 used for the README numbers; dev: C++20, CMake 3.7 |
| **Platforms** | main: x86-64 only, AVX2 required at compile time (the main source has no SSE-only path) plus BMI1 for _bextr_u64; dev branch: SSE4.1+ x86-64 fallback and AArch64 NEON |
| **Thread safety** | not documented; a pure function over a read-only buffer with no shared state, so reentrant by construction |
| **Drop-in for the baseline** | partial — same signature as the repo's serial AverageColorRGBA8, but only for packed RGBA8 with Count &gt; 0, 16-byte-aligned buffers on main, and non-AVX-512 builds (AVX-512 builds return wrong means on non-uniform images) |

## Gotchas

- Correctness bug hidden by the benchmark input: _mm512_shuffle_epi8 (vpshufb) uses only the low 4 bits of each index inside its own 128-bit lane, but both AVX-512 paths pass indices 0x00-0x3F as if it were a full-width byte permute. Red and green are therefore summed from pixels 0-3 and 8-11 of every 16-pixel block and blue and alpha from pixels 4-7 and 12-15, each counted twice. A Python emulation of the documented intrinsic semantics (this session) gives R,G,B = 127,127,0 instead of 63,63,63 for a 4-white/12-black pattern, and 126,124,127,125 instead of 128,123,125,129 for random pixels. BigBench fills all 10,000,000 pixels with 0xBEEFFEEB and the dev branch's unit tests use only constant colours, so neither can catch it; the README's AVX-512 column (4.27x, 5.47x, 6.09x) times this code. Still present on dev as of 2025-10-04.
- VNNI path on main also drops pixels: the outer loop runs its own j++, i += 16 after the inner loop, so the last Count % 16 pixels (5 of 37, for example) and one 16-pixel block per 4,210,752 iterations are skipped while the sums are still divided by Count. Both benchmark sizes (10,000,000 and 8,294,400) are multiples of 16, so the timings are unaffected; fixed on dev in 2024.
- Not all table columns can be rebuilt from public files: main's source compiles the AVX2 loop unconditionally (an SSE4.2-only build fails to compile) and CMakeLists.txt only offers -march=native, so the edits or flags behind the SSE4.2 column and the AVX2 column on AVX-512 CPUs are unpublished. Each routine is timed once (serial first, same buffer, std::chrono::high_resolution_clock, no repetition); the author's Todo.md left 'Disable turbo for benchmarks' and 'List compiler version' undone, and dev later switched BigBench to a separate buffer per routine.
- _mm512_shuffle_epi8 and _mm512_sad_epu8 need AVX512BW, but the path is gated on __AVX512F__ alone; harmless on the listed CPUs, a build error on AVX512F-only parts such as Knights Landing.

## Known shortcomings

- Baseline is the author's own serial loop, single-shot timing with the serial run first; the VNNI-path loop drops the trailing Count%16 pixels (measured sizes unaffected).
- Correctness bug behind the AVX-512 column: both AVX-512 paths feed indices 0x00-0x3F to the in-lane _mm512_shuffle_epi8, so red and green are summed from pixels 0-3 and 8-11 of every 16-pixel block and blue and alpha from pixels 4-7 and 12-15, each twice (emulation of 4 white plus 12 black pixels gives 127,127,0 instead of 63,63,63); the benchmark's single repeated pixel value hides it, so the AVX-512 rows (4.27x, 5.47x, 6.09x) timed wrong code. SSE and AVX2 paths are correct. The SSE4.2 column cannot be rebuilt from the public CMake, MSVC builds always take the VNNI path, _mm_stream_load needs 16-byte alignment, and the VNNI path drops Count%16 pixels. The default branch is frozen since 2021 while a dev branch carries fixes through 2025-10-04 without new numbers.

## Caveats and trade-offs

The baseline is the author's own plain serial loop (shifts and uint8 casts into 64-bit sums; _bextr_u64 appears only in the SIMD routine's scalar tail, not in the baseline), not a library such as OpenCV. Each function is timed once with std::chrono::high_resolution_clock, serial first, with no warm-up or repetition, so run-order and frequency effects are not controlled. The 10-megapixel test image is one repeated pixel value (the work is data-independent, so this matters little). Write-up numbers on the i7-7500U (2.63x SSE, 4.13x AVX2 on 3840x2160) differ from the table (2.85x and 4.41x on 10 megapixels). The README credits all rows to GCC 8.2.1 although rows were added from 2019 to 2021 (i9-11900K row 2021-04-17). Code-reading finding: the AVX-512 VNNI path's outer loop increments i by 16 after the inner loop exits, so it drops the last Count%16 pixels (and skips a 16-pixel block each time the 4,210,752-iteration 32-bit span fills, about 67 megapixels) while still dividing by Count; both benchmark sizes (10,000,000 and 8,294,400 pixels) are multiples of 16 and below the span, so the measured numbers are unaffected. Speedup depends heavily on the CPU (AVX2 2.61x on i9-7900X to 5.35x on i9-11900K). Results 2019-2021. [retier] The baseline is the author's own plain serial loop, not a library such as OpenCV. Each function is timed once with std::chrono::high_resolution_clock, serial first, with no warm-up or repetition. The 10-megapixel test image is one repeated pixel value, which hides a correctness bug: both AVX-512 paths feed indices 0x00-0x3F to _mm512_shuffle_epi8, which permutes within 128-bit lanes, so red and green are summed from pixels 0-3 and 8-11 of each 16-pixel block and blue and alpha from pixels 4-7 and 12-15, each twice (4 white plus 12 black pixels give 127,127,0 instead of 63,63,63); the AVX-512 column therefore timed wrong code. SSE and AVX2 paths are correct. The public CMake cannot rebuild the SSE4.2 column, MSVC builds always take the VNNI path (which drops Count%16 pixels), and _mm_stream_load needs 16-byte alignment. The default branch is frozen since 2021-04-17; a dev branch carries alignment, MSVC, VNNI, AArch64 and Apple AMX work through 2025-10-04 without new numbers.

x86 only (SSE4.2, AVX2, AVX-512 paths plus serial fallback); RGBA8 input only; 64-bit accumulators so no overflow below about 69 billion megapixels; a snippet-sized library, not a general image toolkit.

## Maintenance

The default branch main has not changed since 2021-04-17, but the non-default dev branch received alignment, MSVC and VNNI fixes, AArch64 and Apple AMX paths and Catch2 tests through 2025-10-04 without new README numbers; MIT and one file to vendor, but use the AVX2 path and patch or disable the AVX-512 paths before relying on the output.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now C.
- **Tier reason:** README table gives SSE4.2/AVX2/AVX-512 speedups over the serial routine on six named Intel CPUs (GCC 8.2.1, synthetic 10-megapixel image); the benchmark code is public (tests/BigBench.cpp with tests/Bench.hpp; tests/AverageColor.cpp for the 3840x2160 write-up) and the flags are in CMakeLists.txt (CMAKE_BUILD_TYPE Release, -march=native, C++17), with serial and SIMD paths built by the same flags.
- **Retiered** A to C: Enricher: both AVX-512 paths misuse the in-lane _mm512_shuffle_epi8 and sum the wrong pixels twice (hidden by the benchmark's single repeated pixel value), so the AVX-512 column timed incorrect code; the SSE4.2 column cannot be rebuilt from the public CMake. Public code, flags and CPUs remain for the correct AVX2 path, but with one column invalid and one unreproducible the table is first-party C.
- **Verifier notes:** Table numbers match the record; MIT, 50 stars, default branch main, last commit 2021-04-17 (Add i9-11900k benchmarks), abandoned. Shortcomings to record: single-shot serial-first timing, self-written scalar baseline, and an unfixed VNNI-path bug that drops trailing pixels when the count is not a multiple of 16 (does not affect the measured sizes).
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `caveats`, `claimed_speedup`, `maintenance_status`
- **Shortcomings recorded by:** verifier batch-75 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/Wunkolo/qAverageColor>
  - <https://github.com/Wunkolo/qAverageColor/commits/main>
  - <https://github.com/Wunkolo/qAverageColor/commits/master>
  - <https://raw.githubusercontent.com/Wunkolo/qAverageColor/HEAD/README.md>
  - <https://raw.githubusercontent.com/Wunkolo/qAverageColor/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Wunkolo/qAverageColor/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Wunkolo/qAverageColor/HEAD/source/qAverageColor.cpp>
  - <https://raw.githubusercontent.com/Wunkolo/qAverageColor/HEAD/tests/BigBench.cpp>
  - <https://raw.githubusercontent.com/Wunkolo/qAverageColor/HEAD/tests/AverageColor.cpp>
  - <https://raw.githubusercontent.com/Wunkolo/qAverageColor/HEAD/tests/Bench.hpp>
- **Sources the enricher read:**
  - <https://github.com/Wunkolo/qAverageColor>
  - <https://github.com/Wunkolo/qAverageColor/commits/main>
  - <https://github.com/Wunkolo/qAverageColor/commits/dev>
  - <https://github.com/Wunkolo/qAverageColor/branches/all>
  - <https://github.com/Wunkolo/qAverageColor/pulls>
  - <https://github.com/Wunkolo/qAverageColor/pulls?q=is%3Apr+is%3Aclosed>
  - <https://github.com/Wunkolo/qAverageColor/pull/5>
  - <https://github.com/Wunkolo/qAverageColor/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/Wunkolo/qAverageColor/HEAD/README.md>
  - <https://raw.githubusercontent.com/Wunkolo/qAverageColor/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Wunkolo/qAverageColor/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Wunkolo/qAverageColor/HEAD/Todo.md>
  - <https://raw.githubusercontent.com/Wunkolo/qAverageColor/HEAD/source/qAverageColor.cpp>
  - <https://raw.githubusercontent.com/Wunkolo/qAverageColor/HEAD/include/qAverageColor.hpp>
  - <https://raw.githubusercontent.com/Wunkolo/qAverageColor/HEAD/tests/BigBench.cpp>
  - <https://raw.githubusercontent.com/Wunkolo/qAverageColor/HEAD/tests/AverageColor.cpp>
  - <https://raw.githubusercontent.com/Wunkolo/qAverageColor/HEAD/tests/Bench.hpp>
  - <https://raw.githubusercontent.com/Wunkolo/qAverageColor/dev/source/qAverageColor.cpp>
  - <https://raw.githubusercontent.com/Wunkolo/qAverageColor/dev/source/qAverageColor-x64.cpp>
  - <https://raw.githubusercontent.com/Wunkolo/qAverageColor/dev/source/qAverageColor-a64.cpp>
  - <https://raw.githubusercontent.com/Wunkolo/qAverageColor/dev/tests/UnitTests.cpp>
  - <https://raw.githubusercontent.com/Wunkolo/qAverageColor/dev/tests/BigBench.cpp>
  - <https://raw.githubusercontent.com/Wunkolo/qAverageColor/dev/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Wunkolo/qAverageColor/dev/README.md>
  - <https://raw.githubusercontent.com/Wunkolo/qAverageColor/amx/source/qAverageColor.cpp>
  - <https://raw.githubusercontent.com/Wunkolo/qAverageColor/amx/README.md>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/wunkolo/qaveragecolor`) · [data/wave13/enrich/raw/github_com_wunkolo_qaveragecolor.json](../../../data/wave13/enrich/raw/github_com_wunkolo_qaveragecolor.json) (enrichment confidence 0.85)

</details>
