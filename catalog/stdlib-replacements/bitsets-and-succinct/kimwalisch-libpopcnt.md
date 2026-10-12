# libpopcnt

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Bitsets and succinct bit vectors](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-2-Clause` · 🟢 active

> Single-header C/C++ array popcount with runtime CPU dispatch (AVX512 VPOPCNTDQ, AVX2, NEON, SVE); beats a scalar POPCNT loop on mid-size and large buffers.

| | |
|---|---|
| **Beats** | scalar POPCNT loop (unrolled __builtin_popcountll, the std::popcount-style baseline) and the lookup-8 table algorithm; for the 4.2 claim, the library's own earlier scalar POPCNT or Harley-Seal paths |
| **Claimed result** | v2.3 README 'Speedup' table (Intel Xeon Platinum 8168, GCC 5.4; speedup over sse-popcount's lookup-8 table algorithm): builtin-popcnt-unrolled 4.75x at 32 B to 7.94x at 4096 B; avx2-harley-seal 1.15x at 32 B, 8.46x at 512 B, 13.66x at 4096 B; avx512-harley-seal 0.35x at 32 B, 15.12x at 1024 B, 25.60x at 4096 B. Against the scalar POPCNT baseline (builtin-popcnt-unrolled) that is about 1.7x for AVX2 and 3.2x for AVX512 at 4096 B, and slower below 256-512 B (derived from page data; libpopcnt picks the fastest algorithm per size). Current ChangeLog 4.2 (2026-07-07): 'Up to 3x faster popcount for medium arrays (96 bytes to 1 KB) using a simple AVX2 popcnt256 loop instead of scalar POPCNT or Harley-Seal' (no numbers or hardware); ChangeLog 2.2: 'Up to 6x faster on old x86 CPUs without POPCNT' (baseline not named). Current README example: 133.5 GB/s for a 16 KB array with the AVX512 algorithm on an AMD EPYC 9R14 (no baseline). |
| **Workload** | Counting 1 bits in a byte array of 96 bytes to 1 KB using a plain AVX2 popcnt256 loop instead of scalar POPCNT or Harley-Seal (libpopcnt 4.2 ChangeLog entry); the repo's benchmark program otherwise times popcnt() over fixed array sizes (23, 101, 1001, 10001, 16384 bytes in CI). |
| **Metric** | throughput |
| **Hardware** | v2.3 README table: Intel Xeon Platinum 8168. ChangeLog 4.2 claim: not stated. Current README example run: AMD EPYC 9R14 (2023), AVX512 algorithm, 16 KB array. |
| **Compiler and flags** | v2.3 README table: GCC 5.4, flags not stated. ChangeLog claims: not stated. README says build with -O3 or -O2 and no -mavx2 needed (runtime CPUID dispatch). |
| **Adoption** | 370 stars; Rust port exists as the simd-popcnt crate |
| **Last commit** | 2026-07-23 |
| **Links** | [repository](https://github.com/kimwalisch/libpopcnt) · [benchmark](https://github.com/kimwalisch/libpopcnt/blob/v2.3/README.md) |

## Verdict

All numbers are first-party. The 2019 v2.3 README table (Xeon Platinum 8168, GCC 5.4, flags and harness not named, speedups over sse-popcount's lookup-8 table) shows an unrolled builtin-popcnt loop at 4.75-8.58x, AVX2 Harley-Seal at 1.15-13.66x and the since-replaced AVX512BW Harley-Seal at 0.35-25.60x from 32 B to 4 KB; against the unrolled POPCNT loop that is about 1.7x (AVX2) and 3.2x (AVX512) at 4 KB, with AVX2 ahead only from 512 B and AVX512 from 1 KB (derived from page data). The v4.2 'up to 3x for 96 B to 1 KB' claim compares the new AVX2 popcnt256 loop with v4.1's scalar POPCNT loop (96-511 B) and Harley-Seal (512-1023 B) paths, only on CPUs without AVX512 VPOPCNTDQ, with no CPU or numbers given.

## Use it when

- You already hold a raw bit buffer (bitmap, Bloom filter, fingerprint, XORed vectors) of roughly 100 bytes or more and need its total bit count.
- Shipping one x86 binary to unknown CPUs: target-attribute kernels plus CPUID dispatch give AVX2 or AVX512 speed without compiling the whole program with -mavx2 or -mavx512.
- Large buffers on CPUs with AVX512 VPOPCNTDQ; the README reports 133.5 GB/s for a 16 KB array on an AMD EPYC 9R14 (L1-resident, no baseline given).
- C code bases: the header compiles as C, using C11 atomics or a __sync compare-and-swap for the one-time CPUID cache.
- AArch64 Linux, Android or Windows servers with SVE, where runtime SVE dispatch works with GCC 14+ or Clang 16+ and no special flags.

## Skip it when

- Single words or tiny arrays: below 40 bytes (AVX512 CPUs) or 96 bytes (AVX2 CPUs) it runs the same scalar POPCNT loop you would write yourself, plus a CPUID-cache load and size branches; std::popcount is enough.
- Hamming distance or intersection counts over two arrays: the API counts one buffer only, so you must materialize the AND or XOR first (fused operations were asked about in issue #2 and are not in the current API).
- Rank/select queries or set operations: use a succinct bit vector or bitset library instead.
- Data streamed from DRAM: the published GB/s come from re-counting one small cached array, so for large out-of-cache buffers memory bandwidth, not the kernel, likely sets the speed.
- Old toolchains: GCC below 5 gets no AVX2 path and GCC below 11 no AVX512 path, and clang-cl below 22 needs /arch flags, all without any warning.

## How it is fast

On x86 it runs CPUID once, caches the result in an atomic and picks a kernel by CPU and size: AVX512 VPOPCNTDQ from 40 bytes (4x unrolled vpopcntq into four accumulators, masked byte load for the tail); on AVX2-only CPUs, from 96 bytes, Mula's nibble-lookup popcount (vpshufb plus vpsadbw) in a plain loop below 1 KB and the Harley-Seal carry-save-adder tree over 16 vectors per iteration (Mula, Kurz and Lemire, 'Faster Population Counts Using AVX2 Instructions') from 1 KB; otherwise a scalar popcnt loop over 8-byte memcpy loads with a byte-assembled tail. ARM uses NEON vcnt with byte accumulators widened every 31 iterations, or SVE svcnt with four accumulators when HWCAP reports SVE. Building with -march=native removes the CPUID checks.

## Compared with alternatives

Pick libpopcnt when you only need the count of an existing raw buffer and want portable SIMD dispatch in one header; pick plf::bitset, BitLib or sul::dynamic_bitset when you need a bitset container with shifts and range operations, pasta::bit_vector for rank/select queries, and CRoaring for compressed sets where cardinality comes with set algebra.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (uses &lt;atomic&gt; in C++ or &lt;stdatomic.h&gt; in C11, &lt;immintrin.h&gt; on x86, &lt;arm_neon.h&gt;/&lt;arm_sve.h&gt; on ARM; &lt;sys/auxv.h&gt; or &lt;windows.h&gt; for SVE detection) |
| **Minimum toolchain** | C99 or C++11 class compiler; GCC 4.2+ or Clang 3.0+ for hardware POPCNT, GCC 5+ / Clang 3.8+ / MSVC 2017 (1910)+ for AVX2 dispatch, GCC 11+ / Clang 9+ for AVX512, GCC 14+ / Clang 16+ for runtime SVE dispatch; CMake 3.9 only for its tests and benchmark |
| **Platforms** | any; accelerated on x86/x86-64 (POPCNT, AVX2, AVX512 VPOPCNTDQ+BW), AArch64 (NEON, SVE), PPC64 (POPCNTD via builtin); portable integer fallback elsewhere (WebAssembly is in CI) |
| **Thread safety** | thread-safe per README; CPUID and SVE detection results are cached in atomics with relaxed ordering (a data race in that init code was fixed in v4.0) |
| **Drop-in for the baseline** | partial: one call replaces a loop of std::popcount or __builtin_popcountll over an array; it does not replace std::popcount on one integer or std::bitset::count |

## Gotchas

- The fastest x86 path is chosen by compiler version as much as by CPU: older GCC or clang-cl builds silently fall back to scalar POPCNT, and CPUs with AVX-512 but no VPOPCNTDQ (for example the Xeon Platinum 8168 of the old README table) now use the AVX2 path, because v3.0 replaced the AVX512BW Harley-Seal kernel that the old table measured.
- Helper functions are unprefixed (popcnt, popcnt64, popcnt64_bitwise, get_cpuid, run_cpuid, get_xcr0, CSA256, popcnt256); only macros got the LIBPOPCNT_ prefix in v3.0, so a project with its own popcnt64 or get_cpuid can hit compile-time name clashes. The x86 popcnt() is 'static' rather than 'static inline', so a translation unit that includes the header without calling it can trip -Wunused-function under -Wall -Werror.
- On Windows ARM64 with SVE dispatch enabled the header includes &lt;windows.h&gt; into every translation unit that includes it (it guards NOMINMAX but not the rest of windows.h).
- Harness flaws behind the published numbers: benchmark.cpp re-counts one array that fits in cache (16 KB by default) 10 million times, timed with std::clock, and computes a floating-point progress percentage on every iteration, so GB/s at the 23 and 101-byte CI sizes includes that overhead; its printed 'Algorithm' line is computed separately from the library's dispatch and does not show which AVX2 kernel ran; the CI job compares only against the previous release, never against a std::popcount loop. No correctness bug was found in the kernels (test1.cpp checks every suffix of a 100,000-byte random array against a bitwise reference).

## Known shortcomings

- v2.3 README Speedup table (Xeon Platinum 8168, GCC 5.4, flags and harness not named): about 1.7x AVX2 and 3.2x AVX-512 over unrolled POPCNT at 4 KB (derived), slower on small arrays; CI compares only against the previous release. Filed under stdlib-replacements/bitsets-and-succinct.
- Enricher: benchmark.cpp re-counts one cached 16 KB buffer and does a floating-point progress division every iteration (skews the 23 B and 101 B CI sizes); CI compares only against the previous release, never a std::popcount loop; the v4.2 'up to 3x' baseline is v4.1's own scalar POPCNT (96-511 B) and Harley-Seal (512-1023 B) paths and applies only on CPUs without VPOPCNTDQ; the old AVX-512 table row ran AVX512BW code removed in v3.0. Unprefixed function names; the x86 popcnt() is a non-inline static. Leads: WojciechMula/sse-popcount, positional popcount (arXiv 2412.16370).

## Caveats and trade-offs

First-party evidence only. The library's benchmark program and benchmark.yml CI compare the current code only against its own previous release (job fails if more than 2% slower). The best 'faster than' numbers are an old README table (removed by v3.0, 2024) measured on a Xeon Platinum 8168 with GCC 5.4: the algorithm names and the lookup-8 link point to Wojciech Mula's sse-popcount harness, the program and flags are not named, and the table measures the algorithms rather than necessarily libpopcnt.h itself; the AVX512 path it measured was later replaced (v3.0 swapped AVX512BW Harley-Seal for AVX512 VPOPCNTDQ). Against a plain unrolled POPCNT loop the SIMD paths win only on arrays of a few hundred bytes and up (about 1.7x AVX2 and 3.2x AVX512 at 4 KB, derived) and lose on small arrays, where the library dispatches to scalar POPCNT. The 4.2 'up to 3x' figure compares the new medium-array path with the library's own older paths, with no published numbers in the ChangeLog or the commit (923c433). The AVX2 Harley-Seal algorithm comes from the Mula, Kurz and Lemire paper 'Faster Population Counts using AVX2 Instructions' (peer-reviewed numbers for the algorithm, not for libpopcnt; arXiv blocked here).

Header-only; runtime CPUID dispatch (POPCNT, AVX2, AVX512 VPOPCNTDQ, ARM NEON, SVE, PPC64 POPCNTD, portable fallback); no special compiler flags needed; thread-safe. Only counts bits in a byte array (no bitset container).

## Maintenance

Actively maintained (v4.2 in July 2026, last commit 2026-07-23, CI on Linux, macOS, Windows, FreeBSD, ARM64 and WebAssembly, including ASan/UBSan); BSD-2-Clause single header that is easy to vendor, with a Rust port published as the simd-popcnt crate (1.0.0).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party only: the current ChangeLog's 'up to 3x' line has no hardware, compiler or baseline code, and CI compares only against the previous release; the older v2.3 README Speedup table does compare the library's AVX2/AVX512 Harley-Seal algorithms with an unrolled __builtin_popcount loop on a named CPU (Xeon Platinum 8168, GCC 5.4) but names neither the benchmark program nor the flags, so C.
- **Verifier notes:** Record accurate; added the v2.3 README Speedup table (Xeon Platinum 8168, GCC 5.4) as the clearest comparison with a scalar POPCNT baseline, with derived ratios; still first-party with flags and harness unnamed, so C. Metadata confirmed: BSD-2-Clause, 370 stars, 44 forks, last commit 2026-07-23, active.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `baseline`, `hardware`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** first-party README (verifier); enricher harness reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kimwalisch/libpopcnt/HEAD/ChangeLog>
  - <https://raw.githubusercontent.com/kimwalisch/libpopcnt/HEAD/README.md>
  - <https://raw.githubusercontent.com/kimwalisch/libpopcnt/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/kimwalisch/libpopcnt/HEAD/benchmark.cpp>
  - <https://raw.githubusercontent.com/kimwalisch/libpopcnt/HEAD/.github/workflows/benchmark.yml>
  - <https://raw.githubusercontent.com/kimwalisch/libpopcnt/v2.3/README.md>
  - <https://raw.githubusercontent.com/kimwalisch/libpopcnt/v3.0/README.md>
  - <https://raw.githubusercontent.com/transmission/libpopcnt/HEAD/README.md>
  - <https://github.com/kimwalisch/libpopcnt/blob/v2.3/README.md>
  - <https://github.com/kimwalisch/libpopcnt>
  - <https://github.com/kimwalisch/libpopcnt/commits>
  - <https://github.com/kimwalisch/libpopcnt/commit/923c43377278edc97de155ea70ac3ab20f397f3e>
- **Sources the enricher read:**
  - <https://github.com/kimwalisch/libpopcnt>
  - <https://github.com/kimwalisch/libpopcnt/commits>
  - <https://github.com/kimwalisch/libpopcnt/issues?q=is%3Aissue>
  - <https://github.com/kimwalisch/libpopcnt/issues/20>
  - <https://github.com/kimwalisch/libpopcnt/tree/master/test>
  - <https://raw.githubusercontent.com/kimwalisch/libpopcnt/HEAD/README.md>
  - <https://raw.githubusercontent.com/kimwalisch/libpopcnt/HEAD/ChangeLog>
  - <https://raw.githubusercontent.com/kimwalisch/libpopcnt/HEAD/libpopcnt.h>
  - <https://raw.githubusercontent.com/kimwalisch/libpopcnt/HEAD/benchmark.cpp>
  - <https://raw.githubusercontent.com/kimwalisch/libpopcnt/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/kimwalisch/libpopcnt/HEAD/.github/workflows/benchmark.yml>
  - <https://raw.githubusercontent.com/kimwalisch/libpopcnt/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/kimwalisch/libpopcnt/HEAD/scripts/benchmark-vs-prev-release.sh>
  - <https://raw.githubusercontent.com/kimwalisch/libpopcnt/HEAD/test/CMakeLists.txt>
  - <https://raw.githubusercontent.com/kimwalisch/libpopcnt/HEAD/test/test1.cpp>
  - <https://raw.githubusercontent.com/kimwalisch/libpopcnt/v2.3/README.md>
  - <https://raw.githubusercontent.com/kimwalisch/libpopcnt/v4.1/libpopcnt.h>
  - <https://raw.githubusercontent.com/kimwalisch/libpopcnt/v3.1/libpopcnt.h>
  - <https://crates.io/api/v1/crates/simd-popcnt>
  - <https://github.com/WojciechMula/sse-popcount>
  - WebSearch: 'Faster Population Counts Using AVX2 Instructions' (snippet: vectorized approach about twice as fast as the popcnt instruction on recent Intel processors; arXiv itself blocked here)
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/kimwalisch/libpopcnt`) · [data/wave11/enrich/raw/github_com_kimwalisch_libpopcnt.json](../../../data/wave11/enrich/raw/github_com_kimwalisch_libpopcnt.json) (enrichment confidence 0.8)

</details>
