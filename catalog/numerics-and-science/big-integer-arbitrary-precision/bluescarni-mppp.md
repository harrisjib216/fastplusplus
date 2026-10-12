# mp++

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MPL-2.0` · 🟡 stale

> C++ multiprecision integer/rational/float types over GMP with inline small-value storage; 4-8x faster than raw GMP on 1-limb operands.

| | |
|---|---|
| **Beats** | GMP (mpz_t) |
| **Claimed result** | dot product: almost 4 times faster than GMP; multiply-add: more than 7 times faster; division: about 8 times faster (mp++ and FLINT) |
| **Workload** | 1-limb unsigned integer dot product, vector multiply-add and vector division over small operands (also compared with Boost.Multiprecision cpp_int/gmp_int and FLINT fmpzxx). |
| **Metric** | throughput |
| **Adoption** | 321 stars |
| **Last commit** | 2024-12-10 |
| **Links** | [repository](https://github.com/bluescarni/mppp) · [benchmark](https://bluescarni.github.io/mppp/integer_benchmarks.html) |

## Verdict

First-party mp++ 2.0.0 benchmark page compares integer&lt;1&gt;/&lt;2&gt; to GMP (via Boost gmp_int), Boost cpp_int, FLINT fmpzxx and native ints on 3e7-element vectors: on 1-limb unsigned values mp++ is \~4x faster than GMP for dot product, &gt;7x for multiply-add and \~8x for division (FLINT similar on division). Compiler, flags and CPU are not stated.

## Use it when

- Computer algebra / polynomial coefficient arithmetic where most integers fit in 64 or 128 bits but must not overflow.
- Large vectors of mostly-small arbitrary-precision integers (dot products, multiply-add, division, sort) where GMP's per-object heap allocation dominates.
- You want a modern C++ wrapper over GMP/MPFR/MPC with one consistent API, including arbitrary-precision special functions via FLINT/Arb.
- Code that must interoperate with existing mpz_t-based libraries without copying.

## Skip it when

- Large operands (many limbs): arithmetic defers to GMP, so expect no speedup and a small wrapper cost.
- You need fixed-width wide integers (uint256/uint512): explicitly a non-goal; use Boost.Multiprecision fixed cpp_int.
- Dependency-free or header-only builds: GMP is mandatory and the library is built with CMake.
- Projects needing an actively maintained dependency: last commit 2024-12-10 (2.0.0).

## How it is fast

Small-buffer (small-value) optimisation: values up to SSize 64-bit limbs live inline in the object with no heap allocation, and only spill to a GMP mpz_t when they grow past SSize. Hand-written primitives for SSize 1 and 2 (add, mul, addmul, div, shift, gcd) avoid GMP's general-purpose call and allocation overhead on tiny operands.

## Compared with alternatives

no siblings catalogued yet

## Integration

| | |
|---|---|
| **Form** | shared lib (static via MPPP_BUILD_STATIC_LIBRARY) |
| **Dependencies** | GMP 5+ (required); optional MPFR 3+, GNU MPC, FLINT 3+, libquadmath, Boost (serialization/benchmarks), fmt 6.2+ |
| **Minimum toolchain** | C++11 (uses C++14/17/20 features when available), CMake 3.12; tested on GCC, Clang, MSVC |
| **Platforms** | Linux, Windows, macOS, FreeBSD; x86 and ARM |
| **Thread safety** | not documented (docs only note thread_local performance issues on MinGW and older Xcode) |
| **Drop-in for the baseline** | partial — value type with mpz_t interop (get_mpz_t, mpz_view, mpz_t constructors), but code using raw mpz_\* calls must be rewritten to use the class API to benefit |

## Gotchas

- Choice of SSize is a compile-time tradeoff: larger SSize bloats every object; optimised fast paths exist only for SSize 1 and 2.
- Promotion to dynamic storage is automatic but demotion back to static storage requires an explicit demote() call.
- mpz_view references internal data and is invalidated by modifying the integer; assigning from an aliasing mpz_t is not allowed.
- Binary serialization format is platform-specific, not for long-term storage.

## Known shortcomings

- No compiler, flags or CPU stated on the benchmark page; the 4-8x gains over GMP apply only to 1-limb operands.
- Fast paths only for 1- and 2-limb values, larger operands fall through to GMP; requires GMP and CMake build (not header-only).

## Caveats and trade-offs

Docs state no compiler, flags or CPU. Advantage is limited to 1-limb values; large operands defer to GMP.

C++ wrapper built on GMP/MPFR/MPC; small-value optimisation (inline limbs) beats GMP only for small operands.

## Maintenance

Stale since mp++ 2.0.0 (2024-12-10) with 9 open issues, but MPL-2.0, on conda-forge and mature enough to use as a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party benchmark page compares mp++ against GMP (via Boost.Multiprecision gmp_int) and states the \~4x/7x/8x figures verbatim, but gives no compiler, flags or CPU model and links no benchmark code (repo has a benchmark/ folder), so C.
- **Verifier notes:** Claims match the page exactly. Last commit 2024-12-10 (mp++ 2.0.0) is about 21 months before today, so maintenance_status corrected from active to stale. MPL-2.0, 321 stars, not archived or a fork.
- **Fields the verifier corrected:** `maintenance_status`
- **Shortcomings recorded by:** first-party benchmark page
- **Pages the verifier opened:**
  - <https://bluescarni.github.io/mppp/integer_benchmarks.html>
  - <https://github.com/bluescarni/mppp>
  - <https://github.com/bluescarni/mppp/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/bluescarni/mppp/HEAD/README.md>
  - <https://bluescarni.github.io/mppp/integer_benchmarks.html>
  - <https://bluescarni.github.io/mppp/installation.html>
  - <https://bluescarni.github.io/mppp/integer.html>
  - <https://bluescarni.github.io/mppp/changelog.html>
  - <https://github.com/bluescarni/mppp/issues>
  - <https://github.com/bluescarni/mppp/issues/324>
  - <https://github.com/bluescarni/mppp/commits>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/bluescarni/mppp`) · [data/wave8/enrich/raw/github_com_bluescarni_mppp.json](../../../data/wave8/enrich/raw/github_com_bluescarni_mppp.json) (enrichment confidence 0.82)

</details>
