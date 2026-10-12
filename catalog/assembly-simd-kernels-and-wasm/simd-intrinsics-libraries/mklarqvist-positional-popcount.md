# positional-popcount

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `Apache-2.0` · 🔴 abandoned

> C99 SIMD kernels counting set bits per bit position over 16-bit arrays; up to 16x faster than GCC-vectorized scalar code.

| | |
|---|---|
| **Beats** | pospopcnt_u16_scalar_naive (portable scalar C, auto-vectorized by GCC) and pospopcnt_u16_scalar_naive_nosimd |
| **Claimed result** | pospopcnt_u16_avx512_harley_seal is 16.28x faster than the auto-vectorized scalar naive version at 65536 values (6.43x at 4096, 9.41x at 8192) and 138.71x faster than the no-SIMD naive version at 65536 values; AVX-512 adder forest 4.96x at 2048; at 128 values the Harley-Seal version is 0.52x (slower). README also states about 50 GB/s (about 0.120 cycles per 16-bit integer) with AVX-512. |
| **Workload** | Positional population count (set-bit counts at each of 16 bit positions) over arrays of 16-bit values; the speedup tables cover arrays of 128 to 65536 values on one core, while the cycles-per-integer and MB/s tables use 1 million uniformly random simulated FLAG fields over 1,000 repetitions. |
| **Metric** | throughput |
| **Hardware** | Cannon Lake Core i3-8121U for the speedup table; cycles and MB/s tables also give Sky Lake Xeon W-2104 and Haswell Xeon E5-2697 v3 |
| **Compiler and flags** | gcc (GCC) 7.3.1 20180303 (Red Hat 7.3.1-5); Makefile OPTFLAGS -O3 -march=native, CFLAGS -std=c99, bench built with -std=c++11 |
| **Adoption** | 57 stars; code of the paper 'Efficient Computation of Positional Population Counts Using SIMD Instructions' (Klarqvist, Muła, Lemire), Concurrency and Computation: Practice and Experience 33(17), 2021, DOI 10.1002/cpe.6304 (venue from search snippet; arXiv 1911.02696); README points production users to libalgebra |
| **Last commit** | 2020-01-23 |
| **Links** | [repository](https://github.com/mklarqvist/positional-popcount) · [benchmark](https://github.com/mklarqvist/positional-popcount) |

## Verdict

On a Cannon Lake Core i3-8121U with GCC 7.3.1 at -O3 -march=native, single core, the AVX-512BW Harley-Seal kernel was 16.28x faster than GCC's auto-vectorized naive loop at 65,536 16-bit values (6.43x at 4,096, 0.52x at 128). Against the same loop with vectorization disabled it was 138.71x faster. A separate 1M-value table (README, also from Sky Lake and Haswell) gives 0.121 cycles per value and 48,906 MB/s for the AVX-512 CSA kernel against 2.049 cycles and 2,953 MB/s for the auto-vectorized loop, about 17x (derived from page data). The data was cache-warm: the reference function had just read it.

## Use it when

- Per-bit-position tallies over arrays of thousands to millions of 16-bit flags, e.g. SAM/BAM FLAG fields, one-hot or bitmap feature columns, or bit-sliced statistics.
- x86-64 with AVX-512BW (Skylake-X, Cannon Lake, Ice Lake or later), where the Harley-Seal kernel reached 0.12 cycles per value on warm data.
- AVX2-only x86 machines: the AVX2 CSA kernel still measured 0.199 cycles per value against 2.049 for the auto-vectorized scalar loop on Cannon Lake (about 10x), and 0.308 against 3.778 on Haswell (about 12x), derived from the README cycle table.
- Arrays of about 1,024 values or more; the auto-dispatch switches to the CSA kernels at 512 (AVX-512) or 1,024 (AVX2) values.
- You can vendor two C99 files and build them for a known target CPU.

## Skip it when

- Arrays under about 512 values: in the README speedup table the AVX-512 Harley-Seal kernel is 0.52x at 128 values and 0.74x at 256, and the gain over the scalar loop is 2-3x at best.
- Portable binaries: dispatch happens only at compile time (POSPOPCNT_SIMD_VERSION from __AVX512F__, __AVX2__ or __SSE4_2__). A -march=native build will not run on older CPUs, and a default x86-64 build (SSE2 only) falls back to a scalar umul128 kernel.
- Non-x86 targets: the header includes arm_neon.h but there are no NEON or ASIMD kernels; ARM gets scalar code only. The later Clausecker, Lemire and Schintke work covers AVX2, AVX-512 and ASIMD.
- Production use: the README sends production users to libalgebra.h. The repo has had no commits since January 2020, and its open MinGW build failure (issue #30, 'invalid register for .seh_savexmm') was never fixed.
- 8-bit or 32-bit input through the auto path: get_pospopcnt_u8_method(PPOPCNT_U8_AUTO) and the u32 AUTO both return the scalar naive loop (a TODO in pospopcnt.c), so you must pick a named kernel.

## How it is fast

The fastest kernels use a Harley-Seal carry-save adder (CSA) network: 16 vectors of 32 words are compressed into bit-plane accumulators (ones, twos, fours, eights, sixteens). Only the sixteens plane is expanded into per-position 16-bit lane counters, by shift-and-mask, once every 16 vectors. On AVX-512 each CSA is two vpternlogd instructions. The lane counters are flushed into the 32-bit totals every 65,535 vectors so they cannot overflow. Mid-size inputs use an 'adder forest' (a shallower CSA tree) or Mula's blend-and-popcnt kernel, and arrays under 32 values use an SSE2 psadbw kernel.

## Compared with alternatives

Choose it over sse-popcount when you need a count per bit position rather than one total popcount; sse-popcount solves the plain total-popcount problem. Against libalgebra (same author), choose this repo only to study or benchmark the individual pospopcnt kernels; its own README says libalgebra.h is the production-ready packaging.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (pospopcnt.h + pospopcnt.c; the benchmarks need C++11, and the instrumented benchmark needs Linux perf events) |
| **Minimum toolchain** | C99; GCC or Clang in practice (the kernels use the & operator on __m128i, __restrict__, __attribute__ and unsigned __int128). Travis CI ran GCC 5-8 and Clang; the README numbers came from GCC 7.3.1. |
| **Platforms** | x86 / x86-64 with SSE4.2, AVX2 or AVX-512BW (or AVX-512VBMI) enabled at compile time; scalar fallback elsewhere |
| **Thread safety** | Not documented. By inspection the kernels keep no global or static state and write only the caller's counter array, so concurrent calls with separate counter arrays are safe. |
| **Drop-in for the baseline** | partial: it replaces a hand-written per-bit counting loop with one call that adds into 16 uint32_t counters, but there is no std or libc equivalent to drop it into, and some kernels overwrite the counters instead of adding to them (see gotchas). |

## Gotchas

- Silent wrong answers on AVX-512F CPUs without AVX-512BW (Knights Landing/Mill): __AVX512F__ selects the AVX-512 dispatch path, but the BW kernels it calls for len &gt;= 256 compile to stubs that return 0 without counting, and pospopcnt_u16_avx512_harley_seal returns 0 when neither BW nor VBMI is enabled. The counters stay unchanged and no error is reported.
- Harness flaw in benchmark.cpp: assert_truth() prints FAILURE on a mismatch but always returns true, and it returns early when all counters are zero, so ./bench (and the CI run './bench 100000 10') never fails on wrong counts and silently times no-op stubs. The Linux instrumented_benchmark does check: it runs with its test flag always on and prints 'Problem detected' for a kernel that returns all zeros or wrong counts.
- Harness bug introduced on 2019-12-05 (commit 2c941c7, 'Refactor statistics calculations'): StatisticsBuilder::calculate divides an uninitialized time.mean, so the MB/s figure is garbage. It also sums cycles with std::accumulate(..., 0), an int accumulator that truncates totals above 2^31. At the defaults (1M values, 500 iterations) the no-SIMD baseline's total of about 8.8e9 cycles wraps, so the current ./bench badly under-reports that baseline. The README tables date from March to August 2019 and predate the bug, so they cannot be reproduced with today's ./bench, which also no longer prints MB/s.
- API inconsistency: most kernels add into flags, but pospopcnt_u16_avx512_masked_ops stores its 16 counters with _mm512_storeu_si512, and the 8-bit wrappers built by make_pospopcnt_u8_from_u16 assign flags[i] = ... instead of adding. Zero the counters before every call when mixing kernels.

## Known shortcomings

- README numbers backed by benchmark.cpp checking every method against scalar_naive and a CCPE 33(17) 2021 paper (DOI 10.1002/cpe.6304, snippet only); single Cannon Lake CPU; README tables use method names no longer in pospopcnt.c; abandoned since 2020-01-23; overlaps libalgebra (same kernels).
- Harness bugs in the current benchmark.cpp since commit 2c941c7 (2019-12-05): MB/s is computed from an uninitialised time.mean, the cycle total is summed into an int via std::accumulate(..., 0) so the no-SIMD baseline wraps at the default 1M x 500, and assert_truth always returns true and passes all-zero stubs; the README tables (March-August 2019) predate these bugs, so A holds but the current ./bench cannot reproduce them. Correctness bug: AVX-512F without BW (Knights Landing) makes pospopcnt_u16() call stubs for len &gt;= 256 and leaves the counters at zero. The 50 GB/s headline is cache-warm; no runtime dispatch; u8/u32 AUTO is scalar.

## Caveats and trade-offs

Speedup-table baseline is the compiler auto-vectorized scalar version at -O3 -march=native, a fair baseline; the 138.71x figure is against a deliberately non-vectorized baseline. Speedup table comes from one 2019-era laptop-class Cannon Lake CPU; the AVX-512 paths do not run on most AMD or client Intel parts of that era. The README tables predate the final code: the cycles and MB/s tables list methods (pospopcnt_u16_avx512_csa, avx2_csa, mula3) that no longer exist under those names in pospopcnt.c, and the speedup table's avx512_adder_forest/blend names are now avx512bw_\*. Timing uses CPUID/RDTSC serialization per call and the input is regenerated and pre-touched by the reference function before each timed call, so small-array (128-512 values) ratios include fixed overhead and warm-cache effects. Peer-reviewed in CCPE 2021 (venue from search snippet only; arXiv not reachable). libalgebra (same author) reuses these kernels, so the two entries overlap; a follow-up paper (arXiv 2412.16370, Clausecker, Lemire, Schintke) extends the method to AVX2, AVX-512 and ASIMD. [retier] Speedup-table baseline is the compiler auto-vectorized scalar version at -O3 -march=native (fair); the 138.71x figure is against a deliberately non-vectorized baseline. One 2019-era Cannon Lake laptop CPU; the 50 GB/s headline is cache-warm. The README tables predate the final code (method names such as avx512_csa and mula3 no longer exist) and predate the harness bugs introduced by commit 2c941c7 (2019-12-05): StatisticsBuilder::calculate divides an uninitialised time.mean (garbage MB/s), the cycle total is summed with std::accumulate(..., 0) into an int that wraps at the default 1M values x 500 iterations (the no-SIMD baseline's about 8.8e9 cycles), and assert_truth() always returns true and returns early on all-zero counters, so the current ./bench cannot reproduce the tables and silently times no-op stubs (the Linux instrumented_benchmark does check). Silent wrong answers on AVX-512F CPUs without AVX-512BW (Knights Landing/Mill): the BW kernels called for len &gt;= 256 compile to stubs that return 0 and the counters stay unchanged. No runtime dispatch; the u8/u32 AUTO paths are scalar. API inconsistency: most kernels add into flags but pospopcnt_u16_avx512_masked_ops stores and the u8 wrappers assign, so zero the counters when mixing kernels. Timing uses CPUID/RDTSC serialization per call.

Fastest variants need AVX-512 (Cannon Lake / Skylake-X class); SSE and AVX2 fallbacks are included; experimental repo, the README points production users to libalgebra.h; small arrays (under about 512 values) can be slower than the scalar path.

## Maintenance

Abandoned since 2020-01-23 (no releases, MinGW issue #30 still open) but Apache-2.0 and small enough to vendor. The published numbers predate the 2019-12-05 bugs in benchmark.cpp; anyone re-measuring should use the instrumented_benchmark or fix calculate() and assert_truth() first.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** README speedup tables (vs auto-vectorized pospopcnt_u16_scalar_naive and vs pospopcnt_u16_scalar_naive_nosimd) contain every claimed figure, name the CPU (Core i3-8121U) and compiler (GCC 7.3.1), and the public Makefile sets -O3 -march=native; benchmark code is benchmark.cpp (checks every method against scalar_naive each iteration via assert_truth). The method is also in a peer-reviewed paper (Concurrency and Computation: Practice and Experience 33(17), 2021).
- **Verifier notes:** All claimed numbers verified on the README; tier A stands (public benchmark.cpp + Makefile flags + GCC 7.3.1 + Core i3-8121U), plus peer-reviewed CCPE 2021 paper. Shortcomings: abandoned since 2020-01-23, single Cannon Lake machine, README tables predate method renames, AVX-512-only headline. Lead: arXiv 2412.16370 follow-up (Clausecker/Lemire/Schintke) may have its own repo.
- **Fields the verifier corrected:** `workload`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-10 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/mklarqvist/positional-popcount>
  - <https://github.com/mklarqvist/positional-popcount/commits/master>
  - <https://raw.githubusercontent.com/mklarqvist/positional-popcount/HEAD/README.md>
  - <https://raw.githubusercontent.com/mklarqvist/positional-popcount/HEAD/Makefile>
  - <https://raw.githubusercontent.com/mklarqvist/positional-popcount/HEAD/pospopcnt.c>
  - <https://raw.githubusercontent.com/mklarqvist/positional-popcount/HEAD/benchmark.cpp>
  - <https://raw.githubusercontent.com/mklarqvist/positional-popcount/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/mklarqvist/positional-popcount>
  - <https://raw.githubusercontent.com/mklarqvist/positional-popcount/HEAD/README.md>
  - <https://raw.githubusercontent.com/mklarqvist/positional-popcount/HEAD/pospopcnt.h>
  - <https://raw.githubusercontent.com/mklarqvist/positional-popcount/HEAD/pospopcnt.c>
  - <https://raw.githubusercontent.com/mklarqvist/positional-popcount/HEAD/benchmark.cpp>
  - <https://raw.githubusercontent.com/mklarqvist/positional-popcount/HEAD/Makefile>
  - <https://raw.githubusercontent.com/mklarqvist/positional-popcount/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/mklarqvist/positional-popcount/HEAD/.travis.yml>
  - <https://raw.githubusercontent.com/mklarqvist/positional-popcount/HEAD/example.c>
  - <https://raw.githubusercontent.com/mklarqvist/positional-popcount/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/mklarqvist/positional-popcount/HEAD/benchmark/linux/instrumented_benchmark.cpp>
  - <https://github.com/mklarqvist/positional-popcount/commits/master/benchmark.cpp>
  - <https://github.com/mklarqvist/positional-popcount/commits/master/README.md>
  - <https://github.com/mklarqvist/positional-popcount/commit/2c941c75e7dd4aebf0b00a0eef68f537cff25c01>
  - <https://github.com/mklarqvist/positional-popcount/issues?q=is%3Aissue>
  - <https://github.com/mklarqvist/positional-popcount/issues/30>
  - <https://github.com/mklarqvist/positional-popcount/issues/25>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/mklarqvist/positional-popcount`) · [data/wave13/enrich/raw/github_com_mklarqvist_positional_popcount.json](../../../data/wave13/enrich/raw/github_com_mklarqvist_positional_popcount.json) (enrichment confidence 0.85)

</details>
