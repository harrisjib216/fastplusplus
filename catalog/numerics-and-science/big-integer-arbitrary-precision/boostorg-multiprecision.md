# Boost.Multiprecision (cpp_int fixed-precision)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> Header-only C++ big-number types; fixed-width cpp_int (128-bit) beats GMP's mpz on basic arithmetic by 1.5-6x.

| | |
|---|---|
| **Beats** | GMP (mpz_int via gmp_int backend) |
| **Claimed result** | 128-bit: cpp_int(fixed) beats gmp_int on operator\* (1 vs 4.80 relative time), operator+(int) (1 vs 4.98), operator+ (1 vs 5.87), operator- (1 vs 3.44), operator^ (1 vs 1.35), construct (1 vs 5.62). 256-bit: cpp_int(fixed) wins +, -, ^, construct (gmp_int 1.45, 1.25, 1.01, 1.53) but loses operator\* (1.77 vs gmp 1) and operator+(int) (1.73 vs gmp 1). |
| **Workload** | Fixed-width (128 and 256-bit) cpp_int arithmetic operators (+, -, \*, &, ^, construct) versus gmp_int, relative-time tables. |
| **Metric** | throughput |
| **Compiler and flags** | GNU C++ 10.3.0 (flags not stated) |
| **Adoption** | 263 stars; part of Boost |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/boostorg/multiprecision) · [benchmark](https://www.boost.org/doc/libs/latest/libs/multiprecision/doc/html/boost_multiprecision/perf/integer_performance.html) |

## Verdict

Boost's own docs (GCC 10.3.0, GMP 6.2.0, Boost 1.78, run 2021-09-30; CPU and flags not stated) time 500,000 ops excluding allocation/copy: fixed 128-bit cpp_int beats gmp_int on \* (4.80x), + (5.87x), / (1.70x), % (1.47x); at 256 bits it still wins + (1.45x) but loses \*, / and %, and GMP wins all 512/1024-bit multiply and modulus rows.

## Use it when

- 128-bit integer arithmetic (+, -, \*, /, %, xor) in hot loops, where the docs measure fixed cpp_int 1.5-5.9x faster than gmp_int
- 256-bit-ish workloads dominated by add/sub/construct or many temporaries (Voronoi builder test: int256_t 3.8x faster than mpz_int)
- Projects that need a permissively licensed (BSL-1.0), header-only bigint with no GMP/LGPL dependency
- Compile-time (constexpr) big-integer constants with fixed-width types
- Code that wants one generic interface and may swap to the GMP backend later

## Skip it when

- Multiplication, division or modulus at 256 bits and above: gmp_int wins (256-bit \* 1.77x, / 1.72x slower for fixed cpp_int; 512/1024-bit \* \~1.5-1.6x slower)
- Modular exponentiation / primality testing on wide types: Miller-Rabin with uint1024_t and cpp_int runs \~9-11x slower than mpz_int
- Dynamic (arbitrary-precision) cpp_int in general: it is slower than GMP at every size in the integer_performance tables
- Very large numbers (thousands of bits and up) where GMP/FLINT's subquadratic algorithms matter

## How it is fast

Fixed-width cpp_int stores its limbs inline with no heap allocation and no runtime size checks beyond the fixed limb count, so small-width operations avoid the allocation and dispatch overhead GMP's mpz layer pays per call. Expression templates (enabled by default) fuse compound expressions and cut temporaries. Fixed-precision types are also constexpr-capable, so constant arithmetic can be folded at compile time.

## Compared with alternatives

Pick it over ctbignum or mp++ when you want a mature Boost-licensed header-only type with full operator coverage, signed types and Boost.Math interop rather than maximum small-limb speed; pick FLINT or mp++ for large operands and number-theory kernels where GMP-class algorithms dominate.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | Boost.Config only in standalone mode (BOOST_MP_STANDALONE); otherwise other Boost headers; optional GMP/MPFR/MPIR/TomMath for those backends |
| **Minimum toolchain** | C++14; constexpr cpp_int arithmetic needs C++2a or GCC 6+ in C++14 mode |
| **Platforms** | any platform with a compliant C++14 compiler |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — same number&lt;&gt; interface can host gmp_int or cpp_int, so switching mpz_int to a fixed cpp_int is a typedef change, but it is not a drop-in for raw mpz_t C code |

## Gotchas

- Fixed-width types use sign-magnitude, not two's complement: int128_t has 128 magnitude bits plus a sign bit and is one machine word larger than expected
- Unchecked fixed types wrap modulo 2^MaxBits silently; checked_\* variants throw std::overflow_error instead
- Division by zero throws std::overflow_error; negative values cannot be printed in hex or octal
- Disabling expression templates can cost a lot (Miller-Rabin: cpp_int 16.2x vs 11.2x of GMP's time without/with them)

## Known shortcomings

- Docs from 2021 (GCC 10.3, GMP 6.2.0, Boost 1.78), no flags, CPU model or benchmark-code link; win limited to small fixed widths (all 128-bit ops; at 256 bits only +, -, ^, construct; GMP wins 256-bit \* 1.77x and +(int) 1.73x); on Miller-Rabin (perf/int_real_world.html) dynamic cpp_int is \~11x slower than GMP and fixed uint1024_t 9.3x slower (inputs were 128-bit).
- At 256 bits fixed cpp_int also loses / (1.72x) and % (1.29x) to GMP; GMP wins every 512- and 1024-bit \* and % row; dynamic cpp_int is slower than GMP at every size.

## Caveats and trade-offs

Docs from 2021-09-30 (GCC 10.3.0, GMP 6.2.0, Boost 1.78); CPU and flags not stated; 500,000 ops per test excluding allocation/copy. Win limited to small fixed widths: GMP wins 256-bit \* and +(int), larger sizes, and Miller-Rabin on 128-bit numbers by \~11x (mpz_int 0.00443s vs cpp_int 0.0497s on the int_real_world page).

Header-only; fixed-precision types avoid heap allocation, dynamic cpp_int loses to GMP at 512+ bits.

## Maintenance

Actively maintained Boost library (commits through Sept 2026), BSL-1.0 and header-only, so it is easy to vendor; the published performance tables are from 2021 and may not reflect current versions.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party Boost docs relative-time tables (GNU C++ 10.3.0, GMP 6.2.0, Boost 1.78, run 2021-09-30) vs gmp_int; no flags, no CPU model and no benchmark source linked from the page, so C.
- **Verifier notes:** Record overstated the 256-bit result: gmp_int wins 256-bit operator\* and operator+(int). Metadata verified (BSL-1.0, 263 stars, last commit 2026-09-24). Miller-Rabin numbers are on perf/int_real_world.html, not the benchmark_url page.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** int_real_world: Boost.Polygon Voronoi builder, int256_t 3.8x faster than mpz_int (derived from page data)
- **Pages the verifier opened:**
  - <https://www.boost.org/doc/libs/latest/libs/multiprecision/doc/html/boost_multiprecision/perf/integer_performance.html>
  - <https://www.boost.org/doc/libs/latest/libs/multiprecision/doc/html/boost_multiprecision/perf/int_real_world.html>
  - <https://github.com/boostorg/multiprecision>
  - <https://github.com/boostorg/multiprecision/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/boostorg/multiprecision/HEAD/README.md>
  - <https://www.boost.org/doc/libs/latest/libs/multiprecision/doc/html/boost_multiprecision/perf/integer_performance.html>
  - <https://www.boost.org/doc/libs/latest/libs/multiprecision/doc/html/boost_multiprecision/perf/int_real_world.html>
  - <https://www.boost.org/doc/libs/latest/libs/multiprecision/doc/html/boost_multiprecision/tut/ints/cpp_int.html>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/boostorg/multiprecision`) · [data/wave8/enrich/raw/github_com_boostorg_multiprecision.json](../../../data/wave8/enrich/raw/github_com_boostorg_multiprecision.json) (enrichment confidence 0.75)

</details>
