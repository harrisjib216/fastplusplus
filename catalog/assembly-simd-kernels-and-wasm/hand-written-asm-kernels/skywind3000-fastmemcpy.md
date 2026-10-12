# FastMemcpy

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C (header-only FastMemcpy.h using SSE2/AVX intrinsics, no assembly)` · `MIT` · 🔴 abandoned

> Header-only SSE2/AVX intrinsics memcpy from 2015 that beat the gcc 4.9 and MSVC 2012-era memcpy but not modern glibc.

| | |
|---|---|
| **Beats** | System memcpy of gcc 4.9 and MSVC 2012 |
| **Claimed result** | 32 B (16,777,216 copies, both aligned) memcpy_fast 81 ms vs memcpy 281 ms (3.5x, derived); 64 B 91 vs 364 ms (4.0x, derived); 512 B 124 vs 242 ms; 8 KiB 55 vs 70 ms; 8 MiB 287 vs 421 ms (1.5x, derived); random access 487 vs 1000 ms. Title claim: speed-up over 50% on average. At 1 MiB with both aligned memcpy_fast 181 ms is slower than memcpy 165 ms. |
| **Workload** | Total milliseconds for many copies per size from 32 B to 8 MiB across aligned/unaligned source and destination combinations, plus a random-access run. |
| **Metric** | latency |
| **Compiler and flags** | gcc 4.9: gcc -O3 -msse2 FastMemcpy.c (AVX: -O3 -mavx FastMemcpy_Avx.c); msvc 2012: cl -arch:SSE2 -O2 |
| **Adoption** | 642 stars |
| **Last commit** | 2017-12-11 |
| **Links** | [repository](https://github.com/skywind3000/FastMemcpy) · [benchmark](https://raw.githubusercontent.com/skywind3000/FastMemcpy/HEAD/README.md) |

## Verdict

The 2015 README reports gcc 4.9 (-O3 -msse2) on an unnamed x86 CPU with an unnamed C library ('msvc 2012 got a similar result'). It times total milliseconds for repeated fixed-size copies from 32 B to 8 MiB in four alignment combinations, plus 8 million random 1-2048 B copies. memcpy_fast wins 35 of 36 fixed rows (32 B 81 vs 281 ms; 8 MiB 287 vs 421 ms; it loses at 1 MiB aligned, 181 vs 165 ms) and the random test (487 vs 1000 ms). The 2017 AVX version has no published numbers, and independent runs against glibc on gcc 5.4-10.2 reverse most of these results.

## Use it when

- x86 builds tied to an old or slow C runtime (MSVC 2012-era CRT, MSVCRT.DLL under MinGW, gcc 4.9-era toolchains), the setting the README numbers come from
- Hot copies of small sizes known at compile time (up to 128/256 B) where an always-inline jump-table copy avoids a libc call; independent runs show only parity to modest gains here (issue #4, gcc 5.4: 32-64 B 42-44 vs 48-65 ms)
- Freestanding or no-libc x86 code (engines, custom runtimes) that needs an MIT, header-only memcpy built from C intrinsics without an assembler
- Multi-megabyte copies whose destination will not be read soon, where streaming stores avoid polluting the cache

## Skip it when

- Linux with a modern glibc: independent runs in issues #4 (gcc 5.4), #6 (gcc 10.2.1, Clear Linux) and #7 (gcc 9.3, Ubuntu 20.04) show glibc memcpy faster from 512 B to 8 KiB (1 KiB: 82-91 vs 41-44 ms) and on the random-size test (600 vs 531 ms, 802 vs 662 ms); a ClickHouse perf test found glibc about 0.5% better on average (issue #6)
- Copies above 2 MiB whose destination is read right afterwards: the non-temporal stores bypass the cache, and the 2 MiB threshold is hard-coded rather than taken from the CPU's cache sizes
- Non-x86 targets (ARM64 support was requested in issue #10 and never answered) or binaries that must pick SSE2 or AVX at run time
- Overlapping buffers: there is no memmove variant
- Code that needs maintenance or tests: last commit 2017-12-11, no test suite, 6 open issues and 2 unmerged PRs

## How it is fast

Sizes up to 128 bytes (256 for AVX) go through a switch jump table with one case per size, using overlapping unaligned 16/32/64-byte vector moves plus 2/4/8-byte integer moves for the tail. Larger copies store a 16-byte (or 32-byte) unaligned head, align the destination, then move 128 bytes (256 for AVX) per iteration with eight vector loads and stores and a PREFETCHNTA 256 or 512 bytes ahead. Above a hard-coded 2 MiB 'cachesize' it switches to non-temporal MOVNTDQ stores ending with SFENCE, following AMD's block-prefetch paper cited in the README.

## Compared with alternatives

Pick it over the NASM kernels in ammarfaizi2/memcpy_benchmark or abiiranathan/asmlib only if you need an MIT, header-only memcpy written in C intrinsics that builds under both MSVC and GCC without an assembler. Those siblings target large-buffer AVX/rep movsb copies or report wins against a current glibc (2.44), which FastMemcpy no longer achieves.

## Integration

| | |
|---|---|
| **Form** | header-only (one static function per translation unit) |
| **Dependencies** | none (emmintrin.h for SSE2, immintrin.h for AVX) |
| **Minimum toolchain** | C compiler with SSE2 or AVX intrinsics; README builds with gcc 4.9 (-O3 -msse2 or -O3 -mavx) and MSVC 2012 (/arch:SSE2 or /arch:AVX /O2); the bench drivers compile only on Windows or __unix |
| **Platforms** | x86 and x86-64 with SSE2 (AVX header needs AVX); no ARM, no runtime dispatch |
| **Thread safety** | Reentrant: no mutable state (the only static is the read-only 2 MiB threshold) |
| **Drop-in for the baseline** | partial — memcpy-compatible signature and return value, but it is a separately named static function; call sites must be edited or macro-redirected, and the CPU feature level is fixed at build time |

## Gotchas

- Harness flaw: FastMemcpy.c never writes its source buffers (fresh malloc for the fixed-size rows, a static 11 MiB .bss array for the random test). On Linux, reads of untouched anonymous pages map the kernel's shared zero page, so the 1-8 MiB rows and the random-access row copy from a cache-resident page rather than DRAM, which makes the source prefetching moot (inference from the code; the OS of the README run is not stated).
- Harness flaw: 71 of the 74 timings in the result block at the end of FastMemcpy.c fall within 1.6 ms of a multiple of 15.625 ms, the default Windows timeGetTime tick (the driver never calls timeBeginPeriod), so the small rows (62-125 ms) carry roughly 12-25% quantisation error. Other harness problems: the same size and buffers on every call (hot cache, perfectly predicted branches), only power-of-two sizes, and a non-noinline benchmark() that lets gcc -O3 constant-propagate size into the static memcpy_fast (issues #2 and #6).
- The README baseline costs 16.7 ns per 32-byte memcpy (281 ms for 16,777,216 copies), about 4.5-10x slower than glibc in later independent runs (29-63 ms in issues #4, #6 and #7). The 3.5-4x small-size wins therefore reflect a slow 2015 baseline (MSVC CRT, or MSVCRT.DLL through MinGW's import thunk per PR #1) rather than a technique that still wins. The gcc 7.5 run in issue #4 (fast version 3-8x slower everywhere, about 608 ns per L1-resident 4 KiB copy) looks like an unoptimised build, like issue #5 (inference; flags not stated).
- Both headers use the same include guard __FAST_MEMCPY_H__ and define the same memcpy_fast, so only one can be included per translation unit. The tiny path uses type-punned unaligned uint16/32/64 accesses, which are undefined behaviour in C (UBSan alignment reports) though fine on x86. The 129-case and 257-case always-inline jump tables cost code size.

## Known shortcomings

- No CPU model; SSE intrinsics, not assembly; not faster on modern toolchains (issue #4: gcc 7.5/glibc 2.27, 32 B 230 vs 63 ms; issue #6: gcc 10.2.1, 1024 B 85 vs 41 ms, where alexey-milovidov calls the benchmark nonsense).
- Harness flaws: FastMemcpy.c never writes its source buffers, so on Linux the 1-8 MiB and random rows read the shared zero page (cache-resident, inference); 71 of 74 in-source timings sit on the 15.6 ms Windows timeGetTime tick. The README baseline costs 16.7 ns per 32-byte copy, 4.5-10x slower than glibc in independent runs (issues #4, #6, #7), so the 3.5-4x small-size wins reflect a slow 2015 baseline; the gcc 7.5 run in issue #4 was likely an unoptimised build (inference); modern glibc is faster at 512 B-8 KiB and random sizes.

## Caveats and trade-offs

Implementation is SSE2/AVX intrinsics (85 _mm_ calls in FastMemcpy.h, 91 in FastMemcpy_Avx.h, no inline asm), so it is a memcpy-baseline entry rather than hand-written assembly. CPU model and glibc version not stated; the README results are from 2015 (gcc 4.9 / MSVC 2012); the 2017 AVX version has no published numbers. Only one README row is slower (1 MiB, both aligned: 181 vs 165 ms); the others show gains. Harness flaws (FastMemcpy.c): same src/dst and size every call (hot cache, perfectly predicted branches), millisecond gettimeofday timer, memcpy always runs first on freshly malloc'd buffers, benchmark() not marked noinline so sizes may be constant-propagated; alexey-milovidov (issue #6) called the benchmark 'nonsense' for these reasons and saw glibc slightly faster in a ClickHouse perf test. Independent runs on newer toolchains show it slower than glibc memcpy: issue #4 (gcc 7.5.0, glibc 2.27: 32 B 230 vs 63 ms, random 1953 vs 635 ms; gcc 5.4: 512 B 77 vs 56 ms) and issue #6 (gcc 10.2.1, Clear Linux: 32 B 48 vs 35 ms, 1024 B 85 vs 41 ms, random 802 vs 662 ms). Issue #5 (gcc 4.4.7, 278 vs 85 ms at 32 B) was a build-flag mistake per the reporter.

SSE2 or AVX only; jump table for small sizes, non-temporal stores and prefetch for huge sizes.

## Maintenance

Abandoned since 2017-12-11 (15 commits), MIT and header-only so trivial to vendor, but it is slower than current glibc in independent runs, and its own harness reads an uninitialised (zero-page on Linux) source and published one result set on a 15.6 ms Windows timer tick.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table (gcc 4.9, 'msvc 2012 got a similar result') from the public harness FastMemcpy.c with stated build commands (gcc -O3 -msse2), but no CPU model and no libc version, so C; all quoted numbers match the README.
- **Verifier notes:** README numbers accurate, tier C stays (no CPU model). Record the shortcoming that it is not faster on modern toolchains: independent runs in issues #4 (gcc 7.5/glibc 2.27) and #6 (gcc 10.2.1) show glibc memcpy faster at most sizes and on random access, and a ClickHouse maintainer criticised the benchmark (same-size loops, possible constant propagation, no CPU details).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-29 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/skywind3000/FastMemcpy/HEAD/README.md>
  - <https://raw.githubusercontent.com/skywind3000/FastMemcpy/HEAD/FastMemcpy.c>
  - <https://raw.githubusercontent.com/skywind3000/FastMemcpy/HEAD/FastMemcpy.h>
  - <https://raw.githubusercontent.com/skywind3000/FastMemcpy/HEAD/FastMemcpy_Avx.h>
  - <https://raw.githubusercontent.com/skywind3000/FastMemcpy/HEAD/LICENSE>
  - <https://github.com/skywind3000/FastMemcpy>
  - <https://github.com/skywind3000/FastMemcpy/commits>
  - <https://github.com/skywind3000/FastMemcpy/issues?q=is%3Aissue>
  - <https://github.com/skywind3000/FastMemcpy/issues/4>
  - <https://github.com/skywind3000/FastMemcpy/issues/5>
  - <https://github.com/skywind3000/FastMemcpy/issues/6>
- **Sources the enricher read:**
  - <https://github.com/skywind3000/FastMemcpy>
  - <https://github.com/skywind3000/FastMemcpy/commits>
  - <https://github.com/skywind3000/FastMemcpy/issues?q=is%3Aissue>
  - <https://github.com/skywind3000/FastMemcpy/issues/2>
  - <https://github.com/skywind3000/FastMemcpy/issues/4>
  - <https://github.com/skywind3000/FastMemcpy/issues/6>
  - <https://github.com/skywind3000/FastMemcpy/issues/7>
  - <https://github.com/skywind3000/FastMemcpy/pulls?q=is%3Apr>
  - <https://github.com/skywind3000/FastMemcpy/pull/1>
  - <https://github.com/skywind3000/FastMemcpy/pull/9>
  - <https://raw.githubusercontent.com/skywind3000/FastMemcpy/HEAD/README.md>
  - <https://raw.githubusercontent.com/skywind3000/FastMemcpy/HEAD/FastMemcpy.c>
  - <https://raw.githubusercontent.com/skywind3000/FastMemcpy/HEAD/FastMemcpy.h>
  - <https://raw.githubusercontent.com/skywind3000/FastMemcpy/HEAD/FastMemcpy_Avx.c>
  - <https://raw.githubusercontent.com/skywind3000/FastMemcpy/HEAD/FastMemcpy_Avx.h>
  - <https://raw.githubusercontent.com/skywind3000/FastMemcpy/HEAD/LICENSE>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/skywind3000/fastmemcpy`) · [data/wave13/enrich/raw/github_com_skywind3000_fastmemcpy.json](../../../data/wave13/enrich/raw/github_com_skywind3000_fastmemcpy.json) (enrichment confidence 0.75)

</details>
