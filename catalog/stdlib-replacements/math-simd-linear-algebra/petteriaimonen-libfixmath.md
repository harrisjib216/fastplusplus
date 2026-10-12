# libfixmath

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Math, SIMD and linear algebra](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Q16.16 fixed-point math library in C for FPU-less targets; on 8-bit AVR, add/sub beat soft-float about 2x, mul/div lose.

| | |
|---|---|
| **Beats** | software single-precision float arithmetic (add, sub, mul, div) as compiled by avr-gcc for ATmega128 (avr-libc/libgcc soft-float; toolchain version unstated) |
| **Claimed result** | Average cycles from results-avr.ods (columns inferred as min/avg/max from benchmarks/interface.c print()): fix16_add 67 vs float add 135 (2.0x faster, derived from page data); fix16_sub 75 vs float sub 135 (1.8x faster, derived from page data). Not faster: fix16_mul 377 vs float mul 140 (2.7x slower, derived); fix16_div 637 vs float div 450 (1.4x slower, derived). The sheet also lists fix16_sqrt 706 and fix16_exp 3240 average cycles against float sqrtf/expf rows of 8 cycles, which are measurement artifacts and not a comparison. The README only states that the FIXMATH_FAST_SIN option 'runs at 159% the speed' of libfixmath's own accurate sine (self-comparison). |
| **Workload** | Per-call cycle counts (min/avg/max) for Q16.16 fix16_add, fix16_sub, fix16_mul and fix16_div versus the same operation on C float, over generated test cases, on a simulated 8-bit AVR ATmega128 built with -O2 -DFIXMATH_OPTIMIZE_8BIT. |
| **Metric** | latency |
| **Hardware** | Simulated ATmega128 in simulavrxx 1.0rc0 or newer (cycle counts from the simulator); no real hardware, host machine not stated. |
| **Compiler and flags** | avr-gcc -Wall -mmcu=atmega128 -std=gnu11 -O2 -DFIXMATH_OPTIMIZE_8BIT (from benchmarks/Makefile; gcc and avr-libc versions not stated). The Cortex-M3 target uses arm-none-eabi-gcc -mcpu=cortex-m3 -mthumb -O2 under QEMU, but no results file for it is committed. |
| **Adoption** | 886 stars, 191 forks |
| **Last commit** | 2026-07-13 |
| **Links** | [repository](https://github.com/PetteriAimonen/libfixmath) · [benchmark](https://raw.githubusercontent.com/PetteriAimonen/libfixmath/master/benchmarks/results-avr.ods) |

## Verdict

The only committed measurement is benchmarks/results-avr.ods (contributed in 2021): average cycles on a simulated ATmega128 (simulavr, avr-gcc -O2 -DFIXMATH_OPTIMIZE_8BIT, versions unstated) were fix16_add 67 versus 135 for soft-float add and fix16_sub 75 versus 135 (about 2x faster), but fix16_mul 377 versus 140 and fix16_div 637 versus 450 (slower). The test inputs are 50 operand pairs and 10 single operands drawn at random by generate_testcases.py (testcases.c is not committed, so the draw cannot be reproduced), overflow cases take early exits in fix16_mul, the 32 KB exp cache was left enabled on a 4 KB-SRAM part, and the float sqrtf/expf rows (8 cycles) are timing artifacts, so only the add/sub/mul/div rows are usable.

## Use it when

- 8-bit or FPU-less 32-bit microcontrollers (AVR, Cortex-M0/M0+/M3) where the hot loop is dominated by additions and subtractions of values that fit Q16.16; the project's AVR table shows fix16_add 67 versus 135 cycles for soft-float add.
- Code that must not touch floating point at all, such as Linux kernel modules (fix16 sources build under __KERNEL__ since 2022) or toolchains without soft-float support, while still needing sqrt, exp, log and trig.
- Bit-reproducible results across platforms: the core functions use integer operations only, so the same inputs and compile options give the same bits everywhere (keep the same option set on every target).
- Small firmware that can vendor a handful of MIT-licensed .c files and turn off the caches (FIXMATH_NO_CACHE) to fit in a few KB of RAM.

## Skip it when

- Any target with a hardware FPU (Cortex-M4F/M7, x86, aarch64): fpm's docs/performance.md (Google Benchmark, i7-5820K) reports its own Q16.16 type up to an order of magnitude slower than native float for most functions (faster only for add, sub and several power and trig functions) and libfixmath (built with FIXMATH_NO_CACHE) no faster than fpm except for exp.
- Multiply- or divide-heavy code on AVR: in the project's own table fix16_mul (377 cycles) is 2.7x slower and fix16_div (637 cycles) 1.4x slower than avr-gcc soft-float multiply and divide.
- Values outside about +/-32768, or computations needing more than 1/65536 resolution or float-like dynamic range (products of small numbers lose precision quickly, sin/cos error is about 2.1%).
- Multithreaded code or interrupt handlers calling fix16_exp, fix16_sin/cos or fix16_atan2 with the default caches on: the caches are unsynchronised global arrays (see gotchas).
- RAM-tight parts with default options: the exp and trig caches take 32 KB and 80 KB of static RAM unless FIXMATH_NO_CACHE is defined (an ATmega128 has 4 KB of internal SRAM).

## How it is fast

On a CPU without an FPU, every float operation is a software routine that unpacks exponent and mantissa, aligns, normalises and rounds; Q16.16 add and subtract are a single 32-bit integer add plus an optional sign-based overflow check. Multiplication has three implementations chosen at compile time: a 32x32-to-64-bit multiply (fastest on Cortex-M3 per the source comment), a 32-bit-only version, and an 8-bit version for AVR that does byte-by-byte 8x8-to-16 multiplies and skips zero bytes; division has a hardware-division path and a shift-and-subtract path. Transcendentals use Taylor series (exp), a bitwise square root, polynomial sine, and optional 4096-entry memo caches (32 KB for exp, 80 KB for trig) or a 102,688-entry sine lookup table.

## Compared with alternatives

The other catalogued math entries (SLEEF, fmath, VDT, fast_math_cpp, xsimd) speed up float or double math on CPUs that have an FPU and SIMD; pick libfixmath only when there is no FPU or floating point is off-limits (AVR, Cortex-M0, kernel code), and keep float plus one of those libraries anywhere a hardware FPU exists.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake target libfixmath, or drop the libfixmath/\*.c and .h files into the build) |
| **Dependencies** | none (stdint.h, stdbool.h, limits.h; libm only for the test programs) |
| **Minimum toolchain** | C11 per CMakeLists.txt (CMAKE_C_STANDARD 11, CMake 3.13); the code itself is C99-style; GCC-specific function attributes are applied automatically when __GNUC__ is set |
| **Platforms** | any; FIXMATH_NO_64BIT for compilers without uint64_t, FIXMATH_OPTIMIZE_8BIT for AVR-class 8-bit multipliers, FIXMATH_NO_HARD_DIVISION for cores without a divide instruction, __KERNEL__ for Linux kernel builds |
| **Thread safety** | Not documented. Pure arithmetic (add/sub/mul/div/sqrt) is reentrant; with the default caches, fix16_exp, fix16_sin (and so fix16_cos) and fix16_atan2 read and write global cache index and value arrays without synchronisation, so concurrent or interrupt-time calls can race. Define FIXMATH_NO_CACHE for threads or ISRs. |
| **Drop-in for the baseline** | partial: replacing float needs explicit conversions (fix16_from_float, fix16_to_float) and function calls in C; the C++ Fix16 class gives operators, but its default operators do raw int32 adds without overflow detection unless FIXMATH_SATURATING_ARITHMETIC is defined |

## Gotchas

- Correctness bug in the default build (found by reading libfixmath/fix16_exp.c at HEAD, unreported upstream): for a negative input fix16_exp negates inValue before storing it as the cache key, but stores it at the slot hashed from the original negative value. The hash (x ^ (x &gt;&gt; 4)) & 0xFFF is identical for x and -x exactly when x is a multiple of 0.5, so after fix16_exp(-2.0) a later fix16_exp(2.0) returns the cached exp(-2.0) = 0.135 instead of 7.389. This affects 19 inputs (0.5, 1.5, 2.0, ... 10.0; 1.0 is handled by an early return); negative inputs also never get a cache hit. FIXMATH_NO_CACHE avoids it, and fix16_exp has no unit tests (issue #43, open since 2023).
- The overflow sentinel fix16_overflow is 0x80000000, the same bit pattern as fix16_minimum, so a legitimate result of -32768.0 is indistinguishable from an overflow; fix16_sadd(0, fix16_minimum) returns fix16_maximum (issue #53, open, May 2026).
- fix16.h declares every function with __attribute__((leaf, nothrow, const)) on GCC newer than 4.6, including the cache-writing exp, sin and atan2, so the compiler may merge or move calls; the benchmark's MEASURE macro has no compiler barrier, which is how the float sqrtf and expf rows ended up at 8 cycles, and nothing guarantees the other rows' calls stayed inside the timer window.
- fix16_sqrt of a negative input returns -sqrt(-x) instead of signalling an error; FIXMATH_NO_OVERFLOW turns fix16_add/sub into plain signed int32 adds (undefined behaviour on overflow in C); the CMake test matrix passes FIXMATH_NO_HARD_DIV while the library checks FIXMATH_NO_HARD_DIVISION, so its 12 '\*div' variants do not exercise the software-division path except where FIXMATH_OPTIMIZE_8BIT forces it.

## Known shortcomings

- Tier C: only add and sub are faster (about 2x) than AVR soft float; mul is 2.7x and div 1.4x slower; the sqrtf/expf 8-cycle rows are harness artefacts (calls hoisted out of the timed region, no barriers); the ods has no headers and no avr-gcc or simulavr versions; numbers come from contributor PR #33 (2021), which also fixed fix16_div, and fix16.c was refactored in 2023; the Cortex-M0 atan2 26.3% figure is a search snippet only. MIT, active.
- Enricher: correctness bug in the default build (cache on), not reported upstream: fix16_exp stores the negated input as the cache key at the slot hashed from the original negative value, and the hash is the same for x and -x at multiples of 0.5, so after fix16_exp(-2.0), fix16_exp(2.0) returns 0.135 instead of 7.389 (19 inputs in 0.5..10.0 except 1.0 affected); fix16_exp has no unit tests (issue #43). Harness: all functions are declared const/leaf (FIXMATH_FUNC_ATTRS) and MEASURE has no compiler barrier, so calls can move outside the timer window; testcases.c is not committed (404), so the random draw is not reproducible; the 32 KB exp cache was left on for a 4 KB-SRAM ATmega128; mul has early overflow exits. Overflow sentinel equals fix16_minimum (issue #53); caches are not thread- or ISR-safe; CMake test variants define FIXMATH_NO_HARD_DIV while the library checks FIXMATH_NO_HARD_DIVISION.

## Caveats and trade-offs

Mixed result from the project's own spreadsheet: fixed point wins only add and subtract (about 2x) and loses multiply (2.7x slower) and divide (1.4x slower) to avr-libc/libgcc software float on this 8-bit target; only the add/sub rows support a 'faster' claim. The spreadsheet has no column headers (its embedded chart labels the columns only 'Sloupec C/D/E', Czech for 'Column C/D/E'); min/avg/max is inferred from benchmarks/interface.c print(), which the AVR build links. It states no avr-gcc, avr-libc or simulavr version. The timing harness has no compiler barriers: the float sqrtf and expf rows (8 cycles min/avg/max) show avr-gcc moved those libm calls out of the timed region, so no sqrt or exp comparison is valid; the add/sub/mul/div float rows (80-499 cycles) look like real soft-float calls. fix16_add/fix16_sub are timed as out-of-line calls with overflow checking (FIXMATH_NO_OVERFLOW unset); with that option they become static inline plain integer adds. The file was added by contributor maruncz in PR #33 (commit 0c88e55, merged 2021-05-03, ods metadata 2021-05-01), the same PR that fixed fix16_div failing unit tests under GCC &gt;= 9 and an overflow corner case; whether the div row was measured before or after that fix is not stated, and fix16.c changed again on 2023-08-08 (FIXMATH_NO_HARD_DIVISION refactor), so the numbers may not match current code. The Makefile also has a Cortex-M3 QEMU target, but no ARM results are committed. A Wikipedia statement that libfixmath atan2 takes 26.3% of float time on a Cortex-M0 was seen only as a WebSearch snippet (en.wikipedia.org EGRESS_BLOCKED) with no benchmark code or source in the repo; unverified. Fixed point is compared only with float, not with another fixed-point library. The README FIXMATH_FAST_SIN '159% the speed' figure is a self-comparison. README says 'Not actively maintained, pull requests welcome' although commits landed 2026-02-04 and 2026-07-13 (fix16_asin/atan2 boundary cases, fix16_to_int overflow). [retier] results-avr.ods (contributor PR #33, 2021, simulated ATmega128, no avr-gcc or simulavr versions): only add/sub about 2x faster than AVR soft float, mul 2.7x and div 1.4x slower; sqrtf/expf 8-cycle rows are artefacts (const/leaf attributes and no compiler barrier let calls leave the timed window); testcases.c not committed. Default-build bug: fix16_exp cache returns exp(-x) for x at multiples of 0.5 after exp(-x) was called (e.g. exp(2.0) = 0.135); no exp unit tests (#43). Overflow sentinel equals fix16_minimum (#53); caches not thread- or ISR-safe. fix16.c refactored 2023.

Q16.16 only (range about -32768 to 32767.99998, resolution 1/65536); optional lookup tables cost 32 KB for exp and 80 KB for trigonometry unless FIXMATH_NO_CACHE is defined; overflow checking and rounding are on by default and can be disabled by macros; sin/cos accuracy is about 2.1% (2.3% with the fast option).

## Maintenance

README says 'Not actively maintained, pull requests welcome', yet small fixes still land (2026-02-04, 2026-07-13) and CI builds 24 option variants; MIT and only a few source files, so it is easy to vendor, but build with FIXMATH_NO_CACHE given the unreported fix16_exp cache bug and the thread-unsafe caches.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** benchmarks/results-avr.ods is a bare first-party table (no headers, no toolchain or simulator versions, no commit link) whose rows match the record exactly (fix16_add 64/67/71 vs float add 93/135/183, fix16_sub 71/75/83 vs 94/135/189, fix16_mul 226/377/476 vs 81/140/148, fix16_div 132/637/1272 vs 80/450/499); compiler, flags and the simulated ATmega128 have to be inferred from benchmarks/Makefile and benchmarks/benchmark.c, avr-gcc and simulavr versions are unstated, and the harness itself mis-times two of its six float rows, so it stays C rather than A.
- **Verifier notes:** Numbers in claimed_speedup match benchmarks/results-avr.ods exactly and the derived ratios are correct; metadata (MIT, 886 stars, 191 forks, last commit 2026-07-13, not a fork, not archived) checks out. Shortcomings to record: only add/sub are faster (mul 2.7x and div 1.4x slower than soft float), sqrtf/expf rows are harness artifacts (calls hoisted out of the timed region), no toolchain versions, numbers from a 2021 contributor PR that also fixed fix16_div, Cortex-M0 atan2 26.3% figure snippet only.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-64 (wave 1); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/benchmarks/results-avr.ods>
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/README.md>
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/benchmarks/Makefile>
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/benchmarks/benchmark.c>
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/benchmarks/interface.c>
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/benchmarks/interface.h>
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/benchmarks/interface-avr.c>
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/benchmarks/generate_testcases.py>
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/libfixmath/fix16.c>
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/libfixmath/fix16.h>
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/LICENSE>
  - <https://github.com/PetteriAimonen/libfixmath>
  - <https://github.com/PetteriAimonen/libfixmath/commits/master>
  - <https://github.com/PetteriAimonen/libfixmath/commits/master/benchmarks/results-avr.ods>
  - <https://github.com/PetteriAimonen/libfixmath/commits/master/libfixmath/fix16.c>
  - <https://github.com/PetteriAimonen/libfixmath/pull/33>
- **Sources the enricher read:**
  - <https://github.com/PetteriAimonen/libfixmath>
  - <https://github.com/PetteriAimonen/libfixmath/issues>
  - <https://github.com/PetteriAimonen/libfixmath/issues?q=is%3Aissue+exp>
  - <https://github.com/PetteriAimonen/libfixmath/issues/53>
  - <https://github.com/PetteriAimonen/libfixmath/commits/master/libfixmath/fix16_exp.c>
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/README.md>
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/libfixmath/libfixmath.cmake>
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/tests/tests.cmake>
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/benchmarks/Makefile>
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/benchmarks/benchmark.c>
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/benchmarks/interface.h>
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/benchmarks/interface.c>
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/benchmarks/interface-avr.c>
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/benchmarks/generate_testcases.py>
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/benchmarks/results-avr.ods>
  - https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/benchmarks/testcases.c (404, not committed)
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/libfixmath/fix16.h>
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/libfixmath/fix16.c>
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/libfixmath/fix16_exp.c>
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/libfixmath/fix16_sqrt.c>
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/libfixmath/fix16_trig.c>
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/libfixmath/fix16_trig_sin_lut.h>
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/libfixmath/fix16.hpp>
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/libfixmath/fix16_str.c>
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/libfixmath/fixmath.h>
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/libfixmath/fract32.h>
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/libfixmath/int64.h>
  - <https://raw.githubusercontent.com/PetteriAimonen/libfixmath/HEAD/libfixmath/uint32.h>
  - <https://github.com/MikeLankamp/fpm>
  - <https://raw.githubusercontent.com/MikeLankamp/fpm/HEAD/docs/performance.md>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/petteriaimonen/libfixmath`) · [data/wave1/enrich/raw/github_com_petteriaimonen_libfixmath.json](../../../data/wave1/enrich/raw/github_com_petteriaimonen_libfixmath.json) (enrichment confidence 0.75)

</details>
