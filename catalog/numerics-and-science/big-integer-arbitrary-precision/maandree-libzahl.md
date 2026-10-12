# libzahl

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `ISC` · 🔴 abandoned

> Small ISC-licensed C bignum library that beats GMP on cheap integer operations (assign, sign, compare, add/sub) but loses on multiply.

| | |
|---|---|
| **Beats** | GMP (also TomsFastMath and LibTomMath) |
| **Claimed result** | STATUS (1-4097 bits): zset, zswap, zbtest, zsave, zload, zneg(a,b), zabs(a,b), ztrunc(a,b,c), znot, zbits and zcmpu are 'always fastest'; zsub is 'always fastest'; zadd is 'fastest after \~90 (clang), \~260 (gcc+musl), or \~840 (gcc+glibc)'; zand and zor are fastest only after \~400 and \~1150 bits. Losses: zlsh is 'not too fast anymore'; for zrsh 'gmp is almost always faster'; zmul, zsqr and zstr are 'slowest'; for zstr_length(a,10) 'gmp is faster'. The 'zgcd 21 % of gmp' row sits in the file's '[out of date legacy area]' (152-bit operands), and the file uses 'X % of Y' in rows that still need optimising, so it most likely means libzahl is slower than GMP there. |
| **Workload** | Per-function micro-benchmarks of integer operations (set, swap, neg, abs, bit operations, comparison, add, sub, multiply, square, string conversion, gcd and more) on operands of 1 to 4097 bits, run through translation layers in bench/ for each library. |
| **Metric** | latency |
| **Hardware** | Intel Core 2 Quad Q9300 (x86-64), Linux, 50 us timer slack, benchmark process pinned to one CPU |
| **Compiler and flags** | libzahl built with gcc+glibc, gcc+musl and clang+glibc; other libraries with gcc+glibc; config.mk CFLAGS = -std=c99 -O3 -flto; no CPU extensions or assembly extensions used |
| **Adoption** | 32 stars |
| **Last commit** | 2022-07-20 |
| **Links** | [repository](https://github.com/maandree/libzahl) · [benchmark](https://github.com/maandree/libzahl/blob/master/STATUS) |

## Verdict

The repo's STATUS file ranks libzahl per function against GMP, TomsFastMath and LibTomMath on 1 to 4097-bit operands, on an Intel Core 2 Quad Q9300 under Linux with one pinned CPU, no CPU extensions, libzahl built with gcc+glibc, gcc+musl and clang+glibc and the others with gcc+glibc, -O3 (-std=c99 -O3 -flto in config.mk). It reports rankings and crossover sizes, not times: libzahl is fastest for assignment, sign, comparison, bit test, save/load and add/sub at larger sizes, and slowest for multiply, square and decimal output. GMP and compiler versions are not stated, and some wins go through the bench/ translation layer: the GMP side of zsave/zload calls mpz_out_raw/mpz_inp_raw through an fmemopen stdio stream, so those rows are not like-for-like.

## Use it when

- Programs dominated by cheap bignum bookkeeping (set, swap, negate, abs, compare, bit test, truncate, save/load) on operands up to a few thousand bits, where STATUS ranks libzahl fastest against GMP, TomsFastMath and LibTomMath.
- Addition and subtraction of operands above roughly 100-850 bits (crossover depends on compiler and libc; clang+glibc \~90 bits, gcc+glibc \~840) on x86-64.
- Single-threaded C programs that want a permissively licensed (ISC) bignum without GMP's LGPL/GPL terms and are willing to vendor a small, frozen code base.
- Code that prefers longjmp-style error handling over checking every return value, or that wants allocation caching without writing its own pool.

## Skip it when

- Anything multiplication-, squaring-, division- or exponentiation-heavy: STATUS lists zmul, zsqr and zstr as 'slowest', and the legacy table lists zmodmul, zpow, zmodpow, zptest and small-divisor division as slowest; use GMP or FLINT.
- Multi-threaded programs: the header says libzahl is not thread-safe (global temporaries, a global jmp_buf and global memory pools in zsetup.c).
- Cryptography: zahl.h says 'Do not use libzahl for cryptographic applications'; nothing is constant-time.
- C++ code bases that include zahl.h directly: open issue #4 reports it does not compile as C++ because of register and restrict.
- Long-lived maintained dependencies: the repository was archived on 2024-10-06 and open issues have no maintainer replies.

## How it is fast

Allocations are never freed while the library is set up: limb arrays are rounded up to a power of two (plus 4 'fluff' limbs) and returned to per-size pools for reuse, and internal temporaries are preallocated globals. Error checks happen only where an error can first arise (longjmp out), and -DZAHL_UNSAFE removes them. Hot paths are header inlines; small copies use a computed-jump switch over 1-20 limbs, and x86-64 add/sub and copy loops use inline assembly (adcq in groups of four limbs). Multiplication is plain recursive Karatsuba down to a single 64-bit limb with no schoolbook base case, division is bit-by-bit shift-and-subtract, and gcd is binary gcd, which is why the arithmetic-heavy rows lose.

## Compared with alternatives

Pick libzahl over Boost.Multiprecision cpp_int, mp++ or ctbignum only when you need plain C, an ISC license and no GMP dependency, and your workload is mostly assignment, comparison and add/sub at hundreds to thousands of bits; for fixed small widths in C++ cpp_int or ctbignum fit better, and for multiplication-heavy work GMP-backed mp++ or FLINT win clearly.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none (libc only; POSIX /dev/urandom and /dev/random paths for zrand, configurable via CPPFLAGS) |
| **Minimum toolchain** | C99 compiler; config.mk builds with -std=c99 -O3 -flto; GCC or Clang needed for the inline-assembly and builtin paths (-DZAHL_NO_ASM for others) |
| **Platforms** | x86-64 tested (inline assembly for add/sub/copy); other targets through portable C fallbacks with -DZAHL_NO_ASM; big-endian listed as untested in TODO |
| **Thread safety** | Not thread-safe (stated in README and zahl.h); all state is process-global. |
| **Drop-in for the baseline** | no |

## Gotchas

- Errors longjmp to the point registered by setjmp + zsetup(env); code between that point and the failing call is skipped, so resources must be cleaned up there. -DZAHL_UNSAFE turns checks off entirely and must be set both when building libzahl and before including zahl.h.
- Memory is pooled and only released by zunsetup(); peak memory stays allocated, and allocations round up to the next power of two.
- INSTALL says libzahl contains some inline assembly and asks for -DZAHL_NO_ASM on unsupported CPUs or compilers, and -DZAHL_ISA_MISSING_INDIRECT_JUMP on ISAs without computed jumps.
- znot is not GMP's NOT (GMP computes -x - 1); zstr writes decimal only, and zsets_radix/zstr_radix are TODO items.

## Known shortcomings

- Rankings only, no timing tables; no compiler or GMP version; GMP wins mul/sqr/zstr/zrsh; 'zgcd 21 % of gmp' sits in an out-of-date legacy section (likely means slower); archived 2024-10-06.
- The GMP translation layer runs zsave/zload through fmemopen stdio (mpz_out_raw), so the 'always fastest' save/load rows are not like-for-like; the library does have inline asm (record said none); zmul is plain Karatsuba down to 1 limb and division is bit-serial; global state, not thread-safe; header says not for crypto; won't compile as C++ (#4).

## Caveats and trade-offs

Mixed result, not a general win over GMP. The STATUS file's own multiply, square and string-conversion rows say 'slowest', and GMP wins on right shift. Results are published only as per-function rankings and crossover sizes, with no timing tables. Measured on a 2008 Core 2 Quad with no CPU extensions, so modern GMP assembly paths (mulx, adx, AVX) are not represented. Compiler and GMP versions are not stated, and the GMP numbers come through the repo's translation layer (bench/libgmp.h). STATUS notes that GMP does no failure checking while libzahl does, that TomsFastMath has a compile-time size limit, and that the author flags some rows (zlsb, zcmp) as suspicious. The gcd figure comes from an out-of-date legacy section. Repository archived 2024-10-06; last commit 2022-07-20. The README itself gives no numbers.

C library with long-jump error handling, allocation caching and no thread safety. Wins on cheap and small-operand operations; multiplication, squaring and many derived operations (modular multiply, pow, primality test) were still the slowest, so it does not beat GMP on arithmetic-heavy work. Plain C code, no assembly.

## Maintenance

Abandoned: archived 2024-10-06, last commit 2022-07-20, three open issues unanswered; ISC-licensed and small enough to vendor, but treat it as frozen code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** STATUS compares libzahl against GMP, TomsFastMath and LibTomMath on 1 to 4097-bit operands, and names the CPU (Intel Core 2 Quad Q9300), the compilers (gcc and clang with glibc/musl) and the flags (-O3 tested as 'Good'; config.mk CFLAGS -std=c99 -O3 -flto, which the Makefile's benchmark targets use). The benchmark code is public in bench/benchmark-func.c and bench/benchmark.c, with per-library translation layers such as bench/libgmp.h. It meets A by the rubric, but the published result is a per-function ranking with crossover sizes, not timing tables, and no compiler or GMP versions are given.
- **Verifier notes:** Metadata confirmed on the GitHub page: ISC, archived 2024-10-06, not a fork, 32 stars, last commit 2022-07-20. The record was accurate, apart from presenting the legacy 'zgcd 21 % of gmp' line without context; the catalog should present this as a narrow win on cheap operations (assignment, sign, compare, add/sub at larger sizes), not on multiply or division.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/maandree/libzahl>
  - <https://github.com/maandree/libzahl/commits>
  - <https://raw.githubusercontent.com/maandree/libzahl/HEAD/STATUS>
  - <https://raw.githubusercontent.com/maandree/libzahl/HEAD/README>
  - <https://raw.githubusercontent.com/maandree/libzahl/HEAD/config.mk>
  - <https://raw.githubusercontent.com/maandree/libzahl/HEAD/Makefile>
  - <https://raw.githubusercontent.com/maandree/libzahl/HEAD/bench/benchmark-func.c>
  - <https://raw.githubusercontent.com/maandree/libzahl/HEAD/bench/libgmp.h>
- **Sources the enricher read:**
  - <https://github.com/maandree/libzahl>
  - <https://github.com/maandree/libzahl/issues>
  - <https://github.com/maandree/libzahl/issues/2>
  - <https://github.com/maandree/libzahl/issues/4>
  - <https://github.com/maandree/libzahl/issues/5>
  - <https://raw.githubusercontent.com/maandree/libzahl/HEAD/README>
  - <https://raw.githubusercontent.com/maandree/libzahl/HEAD/STATUS>
  - <https://raw.githubusercontent.com/maandree/libzahl/HEAD/TODO>
  - <https://raw.githubusercontent.com/maandree/libzahl/HEAD/INSTALL>
  - <https://raw.githubusercontent.com/maandree/libzahl/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/maandree/libzahl/HEAD/config.mk>
  - <https://raw.githubusercontent.com/maandree/libzahl/HEAD/Makefile>
  - <https://raw.githubusercontent.com/maandree/libzahl/HEAD/zahl.h>
  - <https://raw.githubusercontent.com/maandree/libzahl/HEAD/zahl/internals.h>
  - <https://raw.githubusercontent.com/maandree/libzahl/HEAD/zahl/inlines.h>
  - <https://raw.githubusercontent.com/maandree/libzahl/HEAD/zahl/memory.h>
  - <https://raw.githubusercontent.com/maandree/libzahl/HEAD/src/internals.h>
  - <https://raw.githubusercontent.com/maandree/libzahl/HEAD/src/zmul.c>
  - <https://raw.githubusercontent.com/maandree/libzahl/HEAD/src/zsqr.c>
  - <https://raw.githubusercontent.com/maandree/libzahl/HEAD/src/zadd.c>
  - <https://raw.githubusercontent.com/maandree/libzahl/HEAD/src/allocator.c>
  - <https://raw.githubusercontent.com/maandree/libzahl/HEAD/src/zdivmod.c>
  - <https://raw.githubusercontent.com/maandree/libzahl/HEAD/src/zgcd.c>
  - <https://raw.githubusercontent.com/maandree/libzahl/HEAD/src/zsetup.c>
  - <https://raw.githubusercontent.com/maandree/libzahl/HEAD/doc/libzahls-design.tex>
  - <https://raw.githubusercontent.com/maandree/libzahl/HEAD/doc/what-is-libzahl.tex>
  - <https://raw.githubusercontent.com/maandree/libzahl/HEAD/bench/libgmp.h>
  - <https://raw.githubusercontent.com/maandree/libzahl/HEAD/bench/benchmark-func.c>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/maandree/libzahl`) · [data/wave8/enrich/raw/github_com_maandree_libzahl.json](../../../data/wave8/enrich/raw/github_com_maandree_libzahl.json) (enrichment confidence 0.8)

</details>
