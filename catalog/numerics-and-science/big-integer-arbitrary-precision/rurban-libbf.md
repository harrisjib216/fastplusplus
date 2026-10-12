# LibBF (Fabrice Bellard)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟡 stale

> Fabrice Bellard's tiny MIT-licensed C arbitrary-precision float library; NTT multiplication edges MPFR only at very high precision.

| | |
|---|---|
| **Beats** | GNU MPFR (mpfr_mul, via the Rust rug 1.30.0 crate: GMP 6.3 / MPFR 4.2) |
| **Claimed result** | Multiplication at 300,000-bit precision: libbf 51.2 ns/limb vs MPFR (rug) 78.9 ns/limb (about 1.5x, derived from page data), from two different harnesses. libbf is slower than MPFR everywhere else on the page: mul at 53 bits 43.4 vs 15.6, 3,000 bits 13.0 vs 9.4, 30,000 bits 43.0 vs 35.3; add, div and sqrt at every size; and exp/log/sin/cos/tan/atan/pow at 53-256 bits (for example exp at 53 bits 2985 vs 518). |
| **Workload** | Correctly rounded floating-point multiplication, addition, division and square root at 53 to 300,000 bits of precision, reported as ns per 64-bit limb. |
| **Metric** | throughput |
| **Hardware** | Apple M4, 32 GiB RAM, macOS 26.5 |
| **Compiler and flags** | libbf 2025-06-03 bftest built locally with clang -O2 ('./bftest -S -p &lt;prec&gt; &lt;op&gt; &lt;op&gt;'); the report says the C harness timed with clock_gettime(CLOCK_MONOTONIC), but the public bftest.c uses x86 rdtsc and prints cycles per limb, so the harness was modified (patch not published). MPFR side: rug 1.30.0 (gmp-mpfr-sys 1.7.1, GMP 6.3, MPFR 4.2) under rustc 1.96.1 --release in libbeef's tests/bftest.rs (BFTEST_SEED=1234, BFTEST_DURATION=200) |
| **Adoption** | 19 stars (rurban/libbf mirror). It was QuickJS's BigInt/BigFloat backend until the QuickJS 2025-04-26 release removed the bignum extensions and added a new BigInt implementation; the current QuickJS Makefile no longer builds libbf. |
| **Last commit** | 2025-08-19 |
| **Links** | [repository](https://github.com/rurban/libbf) · [benchmark](https://github.com/lifthrasiir/libbeef/blob/main/docs/benchmark-report.md) |

## Verdict

A report by the author of libbeef, a competing Rust port, put libbf 2025-06-03's own bftest (clang -O2, modified to use clock_gettime, random-length run-length operands) next to MPFR 4.2 via rug 1.30.0 in a separate Rust harness on an Apple M4; libbf's mul was faster only at 300,000 bits (51.2 vs 78.9 ns/limb, about 1.5x) and slower on every other operation and size. The comparison is cross-harness with different operand generators, so even that one win is not like-for-like.

## Use it when

- Very high precision multiplication (hundreds of thousands of bits and up) where a permissive license matters more than peak speed: the one measured win is mul at 300,000 bits, 51.2 vs 78.9 ns/limb for MPFR on an Apple M4
- Embedding arbitrary-precision floats in a small C/C++ program, interpreter or calculator without linking GMP/MPFR (LGPL): a few C files, custom allocator hook, MIT license
- Exact emulation of IEEE 754 formats with a configurable exponent width and subnormals, e.g. checking hardware or soft-float results
- Needing integers, binary floats and decimal floats from one tiny library with a single number type

## Skip it when

- Ordinary precisions (53 bits to tens of thousands of bits): MPFR is faster on mul, add, div and sqrt in the same report (mul at 53 bits 43.4 vs 15.6 ns/limb, div at 30,000 bits 370.9 vs 64.9)
- Transcendental-heavy code: exp, log, sin, cos, tan are about 2-7x slower than MPFR at 53-256 bits (exp at 53 bits 2985 vs 518 ns/limb); the README says they use an O(n^(1/2) M(n)) method and lack a rigorous rounding-error proof
- Record-size constant computation: the README says it is about 4x slower than Bellard's TachusPI on pi
- Decimal floats at high precision: base-10 arithmetic, input and output are quadratic per the README
- 32-bit targets: the README says the code is not designed to be efficient there and numbers are limited to about 10 million digits

## How it is fast

Above 100 limbs (6,400 bits) for the smaller operand, multiplication switches from schoolbook to a Number Theoretic Transform over up to five word-sized primes (50-51-bit moduli in the AVX2 build, 61-62-bit in the portable build) recombined by CRT; the AVX2 build uses an original SIMD NTT on 64-bit doubles that relies on FMA to get exact products, and the portable build uses 128-bit integers with modular reductions replaced by multiplications. Division, square root and radix conversion are built on that multiplication, giving near-linear running time for the basic operations. Below 100 limbs there is no Karatsuba or Toom stage, which is why it trails MPFR at ordinary precisions.

## Compared with alternatives

Pick libbf over MPFR-based options (FLINT, MPFR itself) only when you need an MIT-licensed, dependency-free arbitrary-precision float in a few C files; for speed at 53-256 bits, double-double/quad-double types (DoubleFloats.jl, MultiFloats.jl in Julia, TLFloat in C++) are far faster, and for huge-precision throughput FLINT (GMP-backed) is the stronger choice.

## Integration

| | |
|---|---|
| **Form** | source-drop (libbf.c, libbf.h, cutils.c, cutils.h; Makefile builds examples only) |
| **Dependencies** | none for the library (libm); bftest needs MPFR, GMP and libmpdec |
| **Minimum toolchain** | GCC or Clang with __int128 and GNU builtins/attributes on 64-bit (C99-era C); Windows via the Makefile's mingw cross-compile option; MSVC not documented |
| **Platforms** | tested on 64-bit x86 per the README; portable C elsewhere (aarch64 used in the Apple M4 benchmark); optional AVX2+FMA build (-mavx2 -mfma -mbmi2) needs Haswell or later |
| **Thread safety** | not documented; bf_context_t holds mutable pi/log2 constant caches and NTT state, so use one context per thread |
| **Drop-in for the baseline** | no |

## Gotchas

- libbf.h has no extern "C" guard; C++ code must wrap the include itself
- The AVX2 and portable builds handle different maximum sizes (8\*10^12 vs 4\*10^16 digits per the README)
- A 2024 radare2 report (issue 23317, PR 23318) flagged an unchecked size computation (na + 1) \* sizeof(limb_t) before bf_malloc in __bf_div that could overflow; the 2025-06-03 code in this mirror still lacks that check
- The README says memory allocation failures are not always reported correctly in the transcendental functions, and some unlikely overflow/underflow cases in exp and pow are not handled

## Known shortcomings

- Not faster in any like-for-like test: the only win (mul at 300k bits, 51.2 vs 78.9 ns/limb) compares libbf's C bftest with the rug Rust harness on different operands and an unstated rounding mode; public bftest.c uses x86 rdtsc, so the M4 harness was modified and the patch is unpublished; bftest's own same-operand MPFR column was not reported; slower than MPFR everywhere else; QuickJS dropped libbf in its 2025-04-26 release. Kept flagged per the keep-and-document rule.
- Possible security bug: radare2 issue 23317 / PR 23318 (2024) report an unchecked size calculation before bf_malloc in __bf_div that could overflow into an out-of-bounds write; the 2025-06-03 mirror still lacks the check (likely theoretical given BF_PREC_MAX, enricher's reading). Schoolbook multiplication only below 100 limbs; libbf.h has no extern "C" guard; README admits no rigorous rounding-error proof for transcendentals and incomplete allocation-error reporting.

## Caveats and trade-offs

The only win over MPFR is multiplication at 300,000 bits on one Apple M4, and it is not a like-for-like measurement: libbf ran in its own C bftest (operands of uniform random length in [1, 2\*prec] bits with run-length random bits, results printed per rounding mode including RNDF, where bf_mul truncates inputs to prec+2 bits; the report does not say which line it quoted) while MPFR ran via rug in libbeef's Rust harness with full-width operands. The public bftest.c already prints an MPFR column on identical operands, which the report did not quote, and it times with x86 rdtsc (cycles), so the report's C harness on Apple M4 was an unpublished modification. Measured by the author of libbeef, a competing Rust port. libbf's own README says it 'is not the fastest library' and is about 4x slower than TachusPI on pi. bellard.org/libbf was blocked, so the GitHub mirror (rurban/libbf, last commit 2025-08-19) is cited.

Small (about 90 KB compiled), no dependencies, SIMD-optimised NTT multiplication with near-linear running time, also decimal floats and IEEE semantics. Transcendental functions are much slower than MPFR (exp at 53 bits 2985 vs 518 ns/limb).

## Maintenance

Stale mirror (last commit 2025-08-19, synced to Bellard's 2025-06-03 tarball plus warning fixes and CI); QuickJS dropped libbf in 2025, but the code is MIT, small and self-contained enough to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** The libbeef report (by the author of a competing Rust port) puts libbf numbers from a locally built C bftest next to MPFR numbers from rug in a separate Rust harness, with different operand generators and unstated rounding mode. The public bftest.c (libbf 2025-06-03) times with x86 rdtsc, prints cycles per limb ('c/64bit') and has its own MPFR column on identical operands; the report says its C harness used clock_gettime on an Apple M4, so it was modified and the patch is not published, and the like-for-like MPFR column was not reported. A harness absent from public sources plus a cross-harness comparison gives C, not B.
- **Verifier notes:** The page numbers match the record, but they do not show libbf faster than MPFR in any controlled comparison: the one winning cell is cross-harness and every other operation and size is slower. A 'not-faster' rejection would be defensible; I downgraded to C instead so it can be kept with that shortcoming recorded. Metadata: MIT, last commit 2025-08-19 (stale), 19 stars; QuickJS no longer uses libbf.
- **Fields the verifier corrected:** `compiler_and_flags`, `claimed_speedup`, `is_fork_of`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/lifthrasiir/libbeef/blob/main/docs/benchmark-report.md>
  - <https://github.com/lifthrasiir/libbeef>
  - <https://raw.githubusercontent.com/lifthrasiir/libbeef/main/CLAUDE.md>
  - <https://github.com/rurban/libbf>
  - <https://github.com/rurban/libbf/commits>
  - <https://raw.githubusercontent.com/rurban/libbf/HEAD/bftest.c>
  - <https://raw.githubusercontent.com/rurban/libbf/HEAD/Makefile>
  - <https://raw.githubusercontent.com/rurban/libbf/HEAD/VERSION>
  - <https://raw.githubusercontent.com/rurban/libbf/HEAD/libbf.c>
  - <https://raw.githubusercontent.com/bellard/quickjs/master/Changelog>
  - <https://raw.githubusercontent.com/bellard/quickjs/master/Makefile>
- **Sources the enricher read:**
  - <https://github.com/rurban/libbf>
  - <https://github.com/rurban/libbf/commits>
  - <https://raw.githubusercontent.com/rurban/libbf/HEAD/readme.txt>
  - <https://raw.githubusercontent.com/rurban/libbf/HEAD/VERSION>
  - <https://raw.githubusercontent.com/rurban/libbf/HEAD/Makefile>
  - <https://raw.githubusercontent.com/rurban/libbf/HEAD/libbf.h>
  - <https://raw.githubusercontent.com/rurban/libbf/HEAD/libbf.c>
  - <https://raw.githubusercontent.com/rurban/libbf/HEAD/bftest.c>
  - <https://raw.githubusercontent.com/rurban/libbf/HEAD/cutils.h>
  - <https://raw.githubusercontent.com/lifthrasiir/libbeef/main/docs/benchmark-report.md>
  - <https://github.com/radareorg/radare2/pull/23318>
  - <https://github.com/radareorg/radare2/pull/23318/files>
  - <https://github.com/radareorg/radare2/issues/23317>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/rurban/libbf`) · [data/wave8/enrich/raw/github_com_rurban_libbf.json](../../../data/wave8/enrich/raw/github_com_rurban_libbf.json) (enrichment confidence 0.75)

</details>
