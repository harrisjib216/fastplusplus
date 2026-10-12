# libdivide

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Math, SIMD and linear algebra](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Zlib OR BSL-1.0` · 🟢 active

> Header-only C/C++ library replacing division by a runtime-invariant integer with multiply-shift sequences; about 6.7x over hardware DIV.

| | |
|---|---|
| **Beats** | hardware integer division (compiler-emitted DIV/IDIV with a runtime divisor) |
| **Claimed result** | README: 'a speedup of up to 10x for 64-bit integer division and a speedup of up to 5x for 32-bit integer division', more with SSE2/AVX2/AVX512/NEON/SVE vectors. README sample output (integer type, CPU and compiler not stated; the benchmark's default type is u64): for divisor 1 (algo 0, no magic number) hardware divide 9.684 ns versus libdivide scalar 0.792 ns (12.2x, derived from page data) and vector 0.426 ns (22.7x, derived from page data); powers of two 2 and 4 (also algo 0) give 11.5 to 11.6x scalar and 21.3x vector (derived from page data); for divisors 3, 5 and 6 (algo 1, multiply-by-magic-number path) libdivide scalar 1.349 to 1.355 ns versus 9.074 to 9.078 ns (6.7x, derived from page data), vector 1.334 ns (6.8x, derived from page data) and branchfree 1.609 ns (5.6x, derived from page data). Author's 2021 blog (snippet only): Intel Xeon 8275CL, divisor 7, u64 hardware 6.998 ns versus libdivide scalar 0.891 ns (7.9x, derived) and AVX512 0.492 ns; u32 hardware 2.298 ns versus scalar 0.872 ns (2.6x, derived). |
| **Workload** | Sum of quotients of an array of random numerators divided by one runtime divisor (benchmark default type u64; u16/s16/u32/s32/s64 selectable), timed for hardware division and for libdivide scalar, branchfree, vector and vector-branchfree dividers plus divider generation; minimum of 30 runs per divisor, with every libdivide result checked against the hardware quotient sum. |
| **Metric** | throughput |
| **Compiler and flags** | CMake Release build by default (CMake's -O3 -DNDEBUG on GCC/Clang) with -march=native when supported, -fno-lax-vector-conversions, and compiler auto-vectorization disabled for the benchmark target (-fno-tree-vectorize on GCC, -fno-vectorize on Clang, chosen by the C compiler's ID); compiler not stated for the README sample. |
| **Adoption** | 1.4k stars |
| **Last commit** | 2026-10-04 |
| **Links** | [repository](https://github.com/ridiculousfish/libdivide) · [benchmark](https://raw.githubusercontent.com/ridiculousfish/libdivide/HEAD/README.md) |

## Verdict

In the README sample from test/benchmark (integer type, CPU and compiler not stated; the default type is u64; each run sums quotients of about 524k uniformly random full-width numerators, and the best of 30 runs is kept and checked against the hardware result), hardware division took 9.07-9.68 ns per divide. libdivide scalar took 0.78-0.79 ns for divisor 1 and powers of two (11.5-12.2x, shift only) and 1.35 ns for divisors 3, 5 and 6 (6.7x); vector took 0.426 and 1.334 ns. The author's 2021 blog (snippet only) measured d = 7 on a Xeon 8275CL: u64 hardware 6.998 ns against scalar 0.891 ns (7.9x) and AVX512 0.492 ns, and 2.6x for u32.

## Use it when

- Hot loops that divide many integers by the same divisor known only at run time (table sizes, strides, user-configured periods, bucketing).
- 64-bit unsigned division on x86 cores with slow 64-bit dividers: the README sample shows 9.07 ns for hardware versus 1.35 ns for ordinary divisors (6.7x) and the author's Xeon 8275CL run (snippet only) 7.9x for d = 7.
- SIMD code that must divide packed 16- or 32-bit lanes (SSE2, AVX2, AVX512, NEON, SVE), since there is no hardware vector integer divide.
- Microcontrollers without a hardware divider, such as AVR (the CI builds an ATmega2560 target).
- Iterating over an array of different divisors: precompute branchfree_divider objects so the division has no data-dependent branches.

## Skip it when

- The divisor is a compile-time constant: compilers already emit the multiply-shift sequence.
- The divisor changes nearly every time: building a divider cost 1.3 ns for shift divisors and 29 ns for u64 multiply-path divisors in the README sample, about three hardware divides.
- CPUs with fast dividers (Apple M1, recent Intel and AMD) and 32-bit types, where the margin is small: the author's 2021 Xeon run gives 2.6x for u32 (snippet only), and the README's 90-cycle latency premise is dated.
- You need remainders (there is no operator% or modulo API), or 64-bit vector division on x86, which the README says is much slower than 32-bit because x86 lacks a 64x64-to-128-bit vector multiply.

## How it is fast

It applies division by invariant integers using multiplication (the Granlund-Montgomery / Hacker's Delight 'magic number' method): the quotient is the high half of n times a precomputed magic number, optionally with an add-and-shift fix-up step, and powers of two (and 1) reduce to a shift. The default 'branchfull' divider picks one of three paths (algo 0 shift, 1 multiply, 2 multiply plus add marker) with a branch the compiler can hoist out of a loop, while the branchfree divider uses a single straight-line sequence for arrays of different divisors. Vector versions use SIMD high-multiplies, which hardware lacks an integer-divide counterpart for.

## Compared with alternatives

Pick libdivide over fastmod when you need 64-bit or signed division, SIMD vector division, a C API or AVR support; fastmod targets 32-bit x % d and x / d and gives you the remainder, which libdivide does not provide. The other catalogued siblings (xsimd, SLEEF, fmath) are floating-point or general SIMD libraries and do not replace integer division.

## Integration

| | |
|---|---|
| **Form** | header-only (libdivide.h; optional constant_fast_div.h and constant_fast_div.hpp) |
| **Dependencies** | none (stdint.h, plus stdio.h/stdlib.h on hosted targets and the intrinsic headers of the enabled vector ISA) |
| **Minimum toolchain** | C99 for the C API (the CI builds a test_c99 program); C++11 for the C++ divider classes and the branchfree_divider alias; constexpr null-construction needs C++14 constexpr or C++20 on MSVC; GCC, Clang and MSVC are tested in CI |
| **Platforms** | any, with a portable scalar path down to 8-bit AVR; vector paths for x86 SSE2/AVX2/AVX512 and Arm NEON/SVE/SVE2; uses __int128 or MSVC __umulh intrinsics where available |
| **Thread safety** | Not documented; a divider is a small struct that is not modified after construction and divide() is const, so a shared const divider can be read concurrently (inference from the API). |
| **Drop-in for the baseline** | partial: n / d becomes n / fast_d after constructing libdivide::divider&lt;T&gt; fast_d(d), with quotients checked against hardware division, but there is no modulo, a zero divisor aborts at construction on hosted builds, and an unsigned branchfree divider cannot be 1 |

## Gotchas

- Benchmark timer bug (harness flaw): test/timer.hpp, added in June 2021 by PR #73, converts gettimeofday's tv_usec with '\* MICROS_PER_SEC' (1,000,000) instead of 1,000, so on Linux and macOS the benchmark prints per-divide times about 1000x too large. Ratios between columns are unaffected because every column shares the error, and runs that cross a second boundary underflow to huge values that the min-of-30 discards. The README's sub-10 ns sample therefore came from Windows (QueryPerformanceCounter path) or from the pre-2021 harness, whose nanoseconds() helper was correct.
- The benchmark's auto-vectorization guard only matches compiler IDs 'Clang' and 'GNU' (and the C++ benchmark target takes the C compiler's flag, test_c99 the C++ one), so AppleClang and MSVC builds get no -fno-vectorize and their 'scalar' columns may be compiler-vectorized; this could overstate scalar speedups on macOS, but it was not measured here.
- Error handling is abort(): a zero divisor, or 1 for an unsigned branchfree divider, prints a message and aborts on hosted builds. On AVR and freestanding builds LIBDIVIDE_ERROR is empty, so the bad divider goes through silently (issue #112 reported division by 0 hanging non-AVR microcontrollers).
- Speedups depend heavily on the divisor and the CPU: the README's 12.2x and 22.7x headline ratios are for divisor 1, where libdivide is just a shift. Issue #68 (i7-4770HQ, macOS) reported hardware 3.241 ns against libdivide scalar 14.439 ns and was closed with no visible explanation. Issue #125 (Arrow Lake, clang 19) timed hardware divq at 1.91 against 5.74 for libdivide's portable 128/64 routine used when generating u64 dividers.

## Known shortcomings

- README sample has no CPU, compiler or integer type; the 12.2x and 22.7x rows are divisor-1 shift cases and multiply-path divisors reach 6.7x (the 'generic algorithm' label is wrong); divider generation costs about 3 hardware divides and the 90-cycle premise is dated; auto-vectorization was disabled. The author's blog (libdivide.com, blocked) reports Xeon 8275CL u64 7.9x as a snippet only.
- Enricher: test/timer.hpp (PR #73, June 2021) multiplies tv_usec by 1,000,000 instead of 1,000, so the POSIX benchmark prints times about 1000x too large (ratios intact; the README sample came from Windows or pre-2021 code); the no-vectorize guard matches only Clang/GNU compiler ids, so AppleClang/MSVC scalar columns may auto-vectorize; no modulo operation; issue #68 (hardware 3.241 vs scalar 14.439 ns) closed without explanation.

## Caveats and trade-offs

First-party claim. The benchmark program is public, but the README's sample output names no CPU, compiler or integer width, so it is tier C. The largest ratios in the sample (12.2x scalar, 22.7x vector) are for divisor 1 and powers of two, where libdivide reduces to a shift; ordinary divisors on the multiply path give about 6.7x scalar in the same sample, and the README sample omits algo 2 divisors (those needing the add step, such as 7), which the author's 2021 blog (snippet only, Xeon 8275CL) measured at 7.9x for u64 and 2.6x for u32. Generating a divider costs 29 ns for multiply-path divisors in the sample, about three hardware divides, so the divisor must be reused. The README's 90-cycle 64-bit divide latency describes older x86 parts; recent Intel and AMD cores and Apple M1 have much faster dividers (the author's own M1 benchmark post and a 2021 D-forum thread, snippet only, discuss this), so the 10x figure is likely smaller on current hardware (not measured here). The baseline is the compiler-emitted hardware divide for the built-in '/' operator with a runtime divisor, not a C++ library facility. An independent user report on an AMD Zen+ CPU (D forum, snippet only, unverified) gave u32 1.156 ns hardware versus 0.399 ns libdivide.

Only pays off when the divisor is a runtime value reused many times (a hot loop); compilers already turn compile-time constant divisors into multiply and shift. Building a divider costs a few to a few tens of nanoseconds (the 'gener' column, 1.3 to 29 ns in the sample). Branchfree divider cannot take unsigned divisor 1 and uses more instructions; signed types are slower than unsigned; x86 64-bit vector division is much slower than 32-bit for lack of a vector multiply.

## Maintenance

Active (v5.4.0 tagged 2026-09-06, last commit 2026-10-04, 1.4k stars, 1 open issue), dual-licensed Zlib or BSL-1.0, header-only and easy to vendor; it appears in search results as a Fedora/EPEL package and a Fuchsia third_party mirror. Its own benchmark has a POSIX timer bug since 2021 that scales absolute times by 1000x (ratios intact), and an auto-vectorization guard that misses AppleClang and MSVC.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README compares libdivide against hardware division with sample output from the public benchmark program (test/benchmark.cpp and test/benchmark.h), but the sample names no CPU, compiler or integer width, so it is first-party with partial methodology. The author's 2021 blog post 'Benchmarking division and libdivide on Apple M1 and Intel AVX512' (blocked here, snippet only) names an Intel Xeon 8275CL at 3.0 GHz; if that post also states compiler and flags it could support A on a later paper-access retier.
- **Verifier notes:** Numbers are on the README and the harness is sound (checked results, minimum of 30 runs, scalar auto-vectorization disabled), so confirm at C; I corrected claimed_speedup because the 12.2x and 22.7x headline figures come from divisor 1 (and the 'generic algorithm' label was wrong: algo 1 is the multiply-by-magic path). Shortcomings to record: README sample has no CPU, compiler or integer type; headline ratios from trivial divisors; divider generation cost about three divides; the 90-cycle premise is dated on current CPUs. libdivide.com, ridiculousfish.com, forum.dlang.org and lists.puremagic.com were EGRESS_BLOCKED; blog figures are from search snippets only.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `compared_against_cpp_std_directly`, `workload`, `caveats`
- **Shortcomings recorded by:** first-party README (verifier); enricher code reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ridiculousfish/libdivide/HEAD/README.md>
  - <https://github.com/ridiculousfish/libdivide>
  - <https://github.com/ridiculousfish/libdivide/commits>
  - <https://raw.githubusercontent.com/ridiculousfish/libdivide/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/ridiculousfish/libdivide/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ridiculousfish/libdivide/HEAD/test/benchmark.cpp>
  - <https://raw.githubusercontent.com/ridiculousfish/libdivide/HEAD/test/benchmark.h>
- **Sources the enricher read:**
  - <https://github.com/ridiculousfish/libdivide>
  - <https://github.com/ridiculousfish/libdivide/commits>
  - <https://github.com/ridiculousfish/libdivide/commits/master/README.md>
  - <https://github.com/ridiculousfish/libdivide/commits/master/test/timer.hpp>
  - <https://github.com/ridiculousfish/libdivide/commit/6b6089d07074fb7289afc812cb4e3be495af6611>
  - <https://github.com/ridiculousfish/libdivide/issues?q=is%3Aissue>
  - <https://github.com/ridiculousfish/libdivide/issues?q=benchmark>
  - <https://github.com/ridiculousfish/libdivide/issues/68>
  - <https://github.com/ridiculousfish/libdivide/issues/125>
  - <https://github.com/ridiculousfish/libdivide/pull/174>
  - <https://github.com/ridiculousfish/libdivide/pull/176>
  - <https://raw.githubusercontent.com/ridiculousfish/libdivide/HEAD/README.md>
  - <https://raw.githubusercontent.com/ridiculousfish/libdivide/HEAD/libdivide.h>
  - <https://raw.githubusercontent.com/ridiculousfish/libdivide/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ridiculousfish/libdivide/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/ridiculousfish/libdivide/HEAD/doc/CPP-API.md>
  - <https://raw.githubusercontent.com/ridiculousfish/libdivide/HEAD/test/benchmark.cpp>
  - <https://raw.githubusercontent.com/ridiculousfish/libdivide/HEAD/test/benchmark.h>
  - <https://raw.githubusercontent.com/ridiculousfish/libdivide/HEAD/test/random_numerators.hpp>
  - <https://raw.githubusercontent.com/ridiculousfish/libdivide/HEAD/test/timer.hpp>
  - <https://raw.githubusercontent.com/ridiculousfish/libdivide/badc03f/test/benchmark.cpp>
  - WebSearch: libdivide benchmark modern CPU hardware division Ice Lake Zen 4 speedup u64 (snippets: ridiculousfish.com blog, lists.puremagic.com D forum, src.fedoraproject.org, fuchsia.googlesource.com)
  - WebSearch: Benchmarking division and libdivide on Apple M1 (snippets only; ridiculousfish.com blocked)
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/ridiculousfish/libdivide`) · [data/wave1/enrich/raw/github_com_ridiculousfish_libdivide.json](../../../data/wave1/enrich/raw/github_com_ridiculousfish_libdivide.json) (enrichment confidence 0.7)

</details>
