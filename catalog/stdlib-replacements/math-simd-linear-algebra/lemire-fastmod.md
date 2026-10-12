# fastmod

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Math, SIMD and linear algebra](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Header-only C/C++ 32-bit remainder, division and divisibility by a reused divisor (LKK direct remainder); about 3x faster than hardware div.

| | |
|---|---|
| **Beats** | Clang-generated code for 32-bit x % d and x / d with a compile-time-known divisor, and the hardware 32-bit division instruction |
| **Claimed result** | README text: 'In hashing benchmarks on Intel Skylake with Clang, this library outperforms compiler optimizations' and 'Faster than compiler-optimized divisions for known divisors'. Plot values read off the image (approximate, not printed as text): division instruction about 0.86 s at every divisor; compiler about 0.26-0.44 s; fastmod ('our approach (LKK)') about 0.25-0.30 s for most divisors. That is about 2.9-3.4x faster than the division instruction and up to about 1.7x faster than the compiler at the compiler's worst divisors (derived from plot reading). At the power-of-two divisors 4, 8, 16, 32 and 64 both the compiler and LKK lines drop to about 0.02 s (no win there), and at divisors 5 and 6 the compiler line is slightly below LKK (about 0.27-0.28 s vs 0.30 s). Paper abstract (search snippet only): C implementations beat optimized code from state-of-the-art C compilers on Intel Skylake and AMD Ryzen, 'sometimes by more than 25%'. |
| **Workload** | Latency-bound linear congruential generator ('hash benchmark'): seed = (seed\*31 + 27961) % D repeated 100,000,000 times with D a compile-time constant from 2 to 64; whole-process time via bash 'time' for lkk (fastmod's LKK remainder), system (the compiler's x % D) and slow (x % d through a volatile divisor, i.e. the hardware division instruction). Harness: lemire/constantdivisionbenchmarks hashbenches (time_hash_benches_clang.sh); the script checks that all variants return the same exit code. The fastmod README shows the resulting plot for Clang on Skylake. |
| **Metric** | throughput |
| **Hardware** | Intel Skylake (README; the harness script's host case is named 'skylake'); exact CPU model not stated on any page reachable here |
| **Compiler and flags** | clang -O3 (hashbenches/time_hash_benches_clang.sh in lemire/constantdivisionbenchmarks); Clang version not stated. fastmod's own Makefile builds its tests at -O3 but its 64-bit benchmarks (tests/modnbenchmark.cpp, tests/moddivnbenchmark.cpp) have no published results. |
| **Adoption** | 352 stars |
| **Last commit** | 2026-04-11 |
| **Links** | [repository](https://github.com/lemire/fastmod) · [benchmark](https://github.com/lemire/fastmod) |

## Verdict

The README plot (Intel Skylake, clang -O3, Clang version and exact CPU not stated) times 10^8 dependent iterations of seed = (seed\*31 + 27961) % D for divisors 2-64: the divide instruction through a volatile divisor takes about 0.86 s at every divisor, Clang's constant-divisor code about 0.26-0.44 s, and the LKK remainder about 0.25-0.30 s (read off the image), so roughly 3x over div and up to about 1.7x over Clang at its worst divisors, with no gain at powers of two and Clang slightly ahead at 5 and 6. The Software: Practice and Experience 2019 paper reports gains over compiler code of sometimes more than 25% on Skylake and Ryzen, and about 15% over libdivide for reused runtime divisors (abstract via search snippets only).

## Use it when

- Hash tables, sharding or hash/LCG steps where the modulus is chosen at run time (prime bucket counts, configurable shard counts) and reused many times: it replaces a 32-bit div (README plot: about 0.86 s vs 0.25-0.30 s for 10^8 dependent remainders, roughly 3x).
- Constant non-power-of-two 32-bit divisors on x64 where the compiler's quotient-then-subtract code is on the critical path: the plot shows LKK at or below Clang for most divisors from 2 to 64, up to about 1.7x at Clang's worst divisors.
- Divisibility tests (n % d == 0) in hot loops: one multiply and one compare.
- C or C++ on 64-bit targets (GCC/Clang with __uint128_t, MSVC x64 or ARM64) that wants a single dependency-free header.

## Skip it when

- Power-of-two divisors: use a mask; the plot shows both compiler and LKK collapse to about 0.02 s at 4, 8, 16, 32 and 64, so there is nothing to gain.
- Compile-time constant divisors where a few cycles do not matter: Clang's own code is slightly faster at divisors 5 and 6 in the plot and within a few percent at several others.
- 64-bit operands: the u64 functions are experimental, signed 64-bit functions do not exist (issue #14), and on MSVC ARM64 computeM_u64 runs a 64-step bit-by-bit division.
- 32-bit targets: the 32-bit path itself needs __uint128_t (GCC/Clang) or __umulh (MSVC x64/ARM64), so x86-32 and ARM32 builds are not supported.
- SIMD lanes or 16-bit types: libdivide (not catalogued here) covers vector and 16-bit division.

## How it is fast

It implements the Lemire-Kaser-Kurz (LKK) direct remainder: with M = ceil(2^64/d), the low 64 bits of M\*a hold the fractional part of a/d, and the high 64 bits of that fraction times d are a % d. A remainder therefore costs two multiplications (one of them a 64x64 high product) instead of a divide instruction, and skips the quotient-multiply-subtract sequence compilers emit for constant divisors. Division is the high half of M\*a, and divisibility is one multiply and compare (a\*M &lt;= M-1). The 64-bit variants need 128-bit M and products, and the header itself warns they may not beat compiler code.

## Compared with alternatives

None of the category's siblings (xsimd, SLEEF, VDT, fmath and other SIMD or elementary-function libraries) do integer division, so fastmod is the pick for scalar 32-bit modulo, division or divisibility by a reused divisor. For SIMD lanes, 16-bit or signed 64-bit types, libdivide (not catalogued) is the usual alternative; the LKK paper's abstract reports beating libdivide by about 15% for most reused non-constant divisors (search snippet only).

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (stdint.h/stdbool.h in C, &lt;cstdint&gt; in C++, &lt;intrin.h&gt; on MSVC) |
| **Minimum toolchain** | C99 or C++11 (constexpr functions with C++14 relaxed constexpr, disabled on MSVC); a 64-bit compiler with __uint128_t, or MSVC x64/ARM64 (64-bit functions need _MSC_VER &gt;= 1923); CMake 3.16 for the optional package config |
| **Platforms** | 64-bit only: x86-64 and AArch64 with GCC or Clang, MSVC x64 and ARM64 |
| **Thread safety** | stateless pure functions; M is a plain integer that can be shared read-only across threads |
| **Drop-in for the baseline** | partial: results match % and / on 32-bit operands for supported divisors, but you call functions with a precomputed M instead of using the operators |

## Gotchas

- C++ template bug (found by reading include/fastmod.h at HEAD; not reported upstream): fastmod::fastmod&lt;int32_t d&gt;(x) passes the template divisor straight to fastmod_s32 as positive_d, which must be |d|. For a negative d the uint32_t conversion gives garbage: emulating the header's arithmetic, fastmod&lt;-5&gt;(7) returns 1717986916 instead of 2, and 24 of 30 sampled negative-divisor cases are wrong. No test (tests/unit.c, cppincludetest1/2.cpp) exercises the fastmod&lt;d&gt;/fastdiv&lt;d&gt; templates; the documented fastmod_s32(a, M, |d|) form is correct.
- Unchecked preconditions: fastdiv_u32 with d = 1 returns 0 (issue #9; documented as requiring d &gt; 1), signed fastdiv must avoid d in {-1, 1, INT32_MIN}, computeM_s32 cannot take INT32_MIN, and fastmod_s32 with d = -1 and a = INT32_MIN is undefined. Nothing asserts these at run time.
- The README API list shows uint64_t/int64_t dividends, but the header takes uint32_t/int32_t, so a 64-bit argument is silently truncated to 32 bits; use the experimental fastmod_u64 for 64-bit values.
- Evidence harness: the README plot comes from lemire/constantdivisionbenchmarks/hashbenches, which inlines its own copy of the LKK remainder with the divisor as a compile-time macro (not fastmod.h with a runtime divisor), times one process per variant and divisor with bash time (a single run, no repetitions), and checks only that the exit codes, the low 8 bits of the final seed, agree. The 64-bit benchmarks in tests/ (modnbenchmark, moddivnbenchmark) have no published results.

## Known shortcomings

- Plot-only evidence (SPE 2019 paper abstract seen as a snippet; public harness lemire/constantdivisionbenchmarks hashbenches, clang -O3) with Clang version and CPU model unstated; no win at power-of-two divisors and the compiler is slightly faster at divisors 5 and 6. Moved from big-integer-arbitrary-precision to math-simd-linear-algebra (constant integer division).
- Enricher: the C++ template fastmod::fastmod&lt;int32_t d&gt; passes d rather than |d| to fastmod_s32 (emulated fastmod&lt;-5&gt;(7) gives 1717986916, not 2; 24 of 30 sampled cases wrong), untested and unreported upstream; the documented C API is fine and the hashbenches harness inlines its own LKK copy with a macro divisor (one run, exit-code check covers only the low 8 bits). Leads: libdivide, lemire/fast_division.

## Caveats and trade-offs

The only quantitative evidence in the README is a plot image (values read by eye). The plot's harness is most likely lemire/constantdivisionbenchmarks/hashbenches (11 stars, research-only, not linked from the fastmod README): it times whole processes with bash 'time' on a single dependent LCG chain, so it measures latency of one remainder per iteration, not throughput. Clang version and exact CPU model are not stated on reachable pages. At power-of-two divisors the compiler is as fast as LKK, and at divisors 5 and 6 the compiler is slightly faster. The peer-reviewed paper (Lemire, Kaser, Kurz, Software: Practice and Experience 49(6), 2019, arXiv 1902.01961) could not be opened (arxiv.org, lemire.me, r-libre.teluq.ca blocked); its abstract via search snippets says the C code beats state-of-the-art compilers on Skylake and Ryzen 'sometimes by more than 25%', and the record's earlier snippet mentions 18 vs 72 cycles (unverified). Category is a weak fit: fastmod is 32-bit (and experimental 64-bit) integer remainder and division by a runtime-invariant divisor, not big-integer arithmetic. The 64-bit functions need __uint128_t and are not supported on Visual Studio.

Header-only (include/fastmod.h), C and C++. 32-bit operands on 64-bit hardware (64-bit variants are marked experimental). The multiplier M must be precomputed once per divisor (computeM_u32), so the win needs a divisor reused across many operations. fastdiv requires d &gt; 1; signed fastdiv must avoid d in {-1, 1, INT32_MIN}.

## Maintenance

Active: CI and quick-test commits on 2026-03-31 and 2026-04-11, release 0.1.0 in July 2024, MSVC 64-bit support merged in November 2024, no open issues; an Apache-2.0 single header that is trivial to vendor, but avoid the C++ fastmod&lt;d&gt; template with negative divisors until it passes |d|.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Raised C to B: the README's plot (docs/hashbenches-skylake-clang.png) is backed by the peer-reviewed Software: Practice and Experience 2019 paper the README links, whose abstract (search snippets only; arXiv, lemire.me and r-libre blocked) reports beating optimized compiler code on Skylake and Ryzen, sometimes by more than 25%. The public harness lemire/constantdivisionbenchmarks hashbenches/time_hash_benches_clang.sh (clang -O3; lkk vs system vs slow) matches the plot, but the Clang version and exact CPU model are not on any page reachable here, so not A.
- **Verifier notes:** Tier raised C to B on the peer-reviewed SPE 2019 paper (abstract via search snippets only) plus a public research harness (lemire/constantdivisionbenchmarks hashbenches, clang -O3) that matches the README plot; A would need the paper's Clang version and CPU model. Shortcomings: plot-only evidence read by eye; no win at power-of-two divisors and slightly slower than compiler code at divisors 5 and 6; category big-integer-arbitrary-precision is a poor fit. License Apache-2.0, 352 stars, not a fork, not archived confirmed on github.com; last commit 2026-04-11 confirmed (commits atom feed), so active.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** constantdivisionbenchmarks (verifier C to B); enricher code reading
- **Pages the verifier opened:**
  - <https://github.com/lemire/fastmod>
  - <https://raw.githubusercontent.com/lemire/fastmod/HEAD/README.md>
  - <https://raw.githubusercontent.com/lemire/fastmod/HEAD/docs/hashbenches-skylake-clang.png>
  - <https://raw.githubusercontent.com/lemire/fastmod/HEAD/tests/modnbenchmark.cpp>
  - <https://raw.githubusercontent.com/lemire/fastmod/HEAD/Makefile>
  - <https://raw.githubusercontent.com/lemire/fastmod/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/lemire/fastmod/HEAD/LICENSE>
  - <https://github.com/lemire/constantdivisionbenchmarks>
  - <https://github.com/lemire/constantdivisionbenchmarks/tree/master/hashbenches>
  - <https://raw.githubusercontent.com/lemire/constantdivisionbenchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/lemire/constantdivisionbenchmarks/HEAD/hashbenches/README.md>
  - <https://raw.githubusercontent.com/lemire/constantdivisionbenchmarks/HEAD/hashbenches/time_hash_benches_clang.sh>
  - <https://raw.githubusercontent.com/lemire/constantdivisionbenchmarks/HEAD/hashbenches/hash_benchmark_lkk.c>
  - <https://raw.githubusercontent.com/lemire/constantdivisionbenchmarks/HEAD/hashbenches/hash_benchmark_system.c>
  - <https://raw.githubusercontent.com/lemire/constantdivisionbenchmarks/HEAD/hashbenches/hash_benchmark_slow.c>
  - <https://github.com/lemire/fastmod/commits/master.atom>
- **Sources the enricher read:**
  - <https://github.com/lemire/fastmod>
  - <https://raw.githubusercontent.com/lemire/fastmod/HEAD/README.md>
  - <https://raw.githubusercontent.com/lemire/fastmod/HEAD/include/fastmod.h>
  - <https://raw.githubusercontent.com/lemire/fastmod/HEAD/docs/hashbenches-skylake-clang.png>
  - <https://raw.githubusercontent.com/lemire/fastmod/HEAD/Makefile>
  - <https://raw.githubusercontent.com/lemire/fastmod/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/lemire/fastmod/HEAD/tests/CMakeLists.txt>
  - <https://raw.githubusercontent.com/lemire/fastmod/HEAD/tests/unit.c>
  - <https://raw.githubusercontent.com/lemire/fastmod/HEAD/tests/cppincludetest1.cpp>
  - <https://raw.githubusercontent.com/lemire/fastmod/HEAD/tests/cppincludetest2.cpp>
  - <https://raw.githubusercontent.com/lemire/fastmod/HEAD/tests/modnbenchmark.cpp>
  - <https://raw.githubusercontent.com/lemire/fastmod/HEAD/tests/moddivnbenchmark.cpp>
  - <https://github.com/lemire/fastmod/commits/master>
  - <https://github.com/lemire/fastmod/issues?q=is%3Aissue>
  - <https://github.com/lemire/fastmod/issues/12>
  - <https://github.com/lemire/fastmod/issues/17>
  - <https://raw.githubusercontent.com/lemire/constantdivisionbenchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/lemire/constantdivisionbenchmarks/HEAD/hashbenches/README.md>
  - <https://raw.githubusercontent.com/lemire/constantdivisionbenchmarks/HEAD/hashbenches/common.h>
  - <https://raw.githubusercontent.com/lemire/constantdivisionbenchmarks/HEAD/hashbenches/time_hash_benches_clang.sh>
  - <https://raw.githubusercontent.com/lemire/constantdivisionbenchmarks/HEAD/hashbenches/hash_benchmark_lkk.c>
  - <https://raw.githubusercontent.com/lemire/constantdivisionbenchmarks/HEAD/hashbenches/hash_benchmark_system.c>
  - <https://raw.githubusercontent.com/lemire/constantdivisionbenchmarks/HEAD/hashbenches/hash_benchmark_slow.c>
  - <https://github.com/lemire/fast_division>
  - <https://github.com/ridiculousfish/libdivide>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/lemire/fastmod`) · [data/wave8/enrich/raw/github_com_lemire_fastmod.json](../../../data/wave8/enrich/raw/github_com_lemire_fastmod.json) (enrichment confidence 0.85)

</details>
