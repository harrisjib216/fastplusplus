# ctbignum

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Header-only constexpr C++20 fixed-width big integers and Z/qZ arithmetic; beats GMP mpn_mul at 2-4 limbs.

| | |
|---|---|
| **Beats** | GMP (mpn/mpz) |
| **Claimed result** | Table 3 (-march=native, forced inlining): 2 limbs 4 ns vs GMP mpn_mul 14 ns (3.5x); 4 limbs 18 vs 29 ns (1.6x); 8 limbs 85 vs 67 ns (GMP 1.27x faster). Table 1 (-O3 only): 2 limbs 5 vs 13 ns, 4 limbs 19 vs 30 ns, 8 limbs 125 vs 69 ns. GMP wins from 5-6 limbs up (ratios derived from page data) |
| **Workload** | Fixed-width multiplication of 2, 4 and 8 64-bit-limb integers (100-500 bit range), run time and compile time. |
| **Metric** | latency |
| **Hardware** | 2017 MacBook Pro, quad-core 2.3 GHz Intel Core i5 (Kaby Lake), 16 GB, Turbo Boost disabled |
| **Compiler and flags** | Apple LLVM 9.0.0, -O3 -march=native with forced inlining of mul (Table 3); Table 1 uses -O3 without -march=native |
| **Adoption** | 123 stars |
| **Last commit** | 2026-08-07 |
| **Links** | [repository](https://github.com/niekbouman/ctbignum) · [benchmark](https://arxiv.org/pdf/1804.07236) |

## Verdict

The 2018 arXiv paper times schoolbook multiplication against GMP mpn_mul on a 2.3 GHz Kaby Lake i5 (Turbo off) with Apple LLVM 9.0.0 -O3 -march=native and forced inlining: 4 vs 14 ns at 2 limbs (3.5x), 18 vs 29 ns at 4 limbs (1.6x), and 85 vs 67 ns at 8 limbs, where GMP wins. The public benchmark source is benchmarks/src/bench-mul.cpp.

## Use it when

- Cryptographic field/ring arithmetic on 2-4 64-bit limbs (128-256 bits), e.g. elliptic-curve or pairing fields, where the modulus is known at compile time.
- Tight inner loops of many small multiplications or Montgomery multiplications where GMP's per-call overhead dominates (paper: 4-limb Montgomery mul 39 ns vs libff assembly 66 ns, with forced inlining).
- You want big-integer constants or precomputation evaluated at compile time (constexpr, static_assert on big-integer results).
- Embedded or allocation-free code that needs fixed-size stack integers and only the C++ standard library.

## Skip it when

- Operands of about 5-6 limbs or more: GMP's mpn_mul is faster (8 limbs: 85 vs 67 ns with -march=native, 125 vs 69 ns without).
- Sizes not known at compile time or numbers that grow; there is no arbitrary-precision type (fixed vs expanding separation is an open issue).
- Side-channel-sensitive code that assumes every function is constant-time: the README says only explicitly marked functions are (add, mul and comparison are ct-verif checked).
- MSVC builds: the code relies on __uint128_t and [[gnu::always_inline]], and MSVC support is an open issue (#44).
- Large-number algorithms: multiplication is O(n^2) schoolbook only, with no Karatsuba/FFT.

## How it is fast

Because the limb count is a template parameter, the schoolbook loops (using unsigned __int128 for 64-bit limbs) have fixed trip counts that the compiler fully unrolls and, with [[gnu::always_inline]], inlines into the caller, avoiding GMP's call overhead and length dispatch. Arguments are passed by value so limbs can live in registers. Modulus-dependent constants for Barrett/Montgomery reduction and invariant division are precomputed at compile time.

## Compared with alternatives

Pick ctbignum over mp++ or FLINT when the width is fixed at compile time and small (2-4 limbs), or when you need constexpr evaluation; mp++/FLINT handle arbitrary sizes and grow dynamically. The AVX-512 batched Montgomery entry targets 1024-4096-bit operands in batches of 8, a different regime from ctbignum's 100-500-bit scalar operations.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (C++ standard library); benchmarks need GMP, NTL 10.5+, libff and Google Benchmark |
| **Minimum toolchain** | C++20 (releases up to v0.3 were C++17 on Clang 5 / Apple LLVM 9); needs GCC/Clang extensions __uint128_t and gnu::always_inline |
| **Platforms** | 64-bit targets where the compiler provides __uint128_t (GCC/Clang on x86-64, aarch64); MSVC not supported |
| **Thread safety** | Value types with no shared state; not documented explicitly |
| **Drop-in for the baseline** | partial: replaces GMP mpn/mpz only for fixed-width operands whose limb count is known at compile time; different API (big_int&lt;N&gt;, ZqElement) |

## Gotchas

- The headline wins assume forced inlining and -march=native; without -march=native the 2-limb gain shrinks (5 vs 13 ns) and GMP is 1.8x faster at 8 limbs.
- mul returns big_int&lt;M+N&gt;, so result width grows by type; use partial_mul or Montgomery/Barrett reduction to stay at a fixed width.
- Open bug #55: bit shifts larger than the limb bit width do not work.
- ZqElement's skip_reduction constructor assumes input &lt; modulus and does not check it.

## Known shortcomings

- Headline numbers need -march=native plus forced inlining; GMP is faster from \~5-6 limbs up, and up to 1.8x faster at 8 limbs without -march=native.
- GCC/Clang only (__uint128_t, gnu::always_inline; MSVC issue #44); open bug #55 (shifts wider than one limb fail); not every function constant-time; O(n^2) schoolbook multiply only.

## Caveats and trade-offs

Win is only for small fixed widths (2-4/5 limbs); GMP is faster from about 5-6 limbs and up to 1.8x faster at 8 limbs without -march=native; the headline numbers need -march=native plus forced inlining; 2018 paper on 2017 hardware; bench needs GMP, NTL, libff and Google Benchmark; not all functions are constant-time.

Fixed-width only (sizes known at compile time), C++20 header-only; wins only for small limb counts via inlining and unrolling.

## Maintenance

Small, Apache-2.0 header-only library marked 'work in progress' in its README, with commits as recent as 2026-08-07 and 12 open issues; easy to vendor, though the published benchmarks date from 2018.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** Paper Table 3 compares ctbignum against GMP mpn_mul (and NTL) with Apple LLVM 9.0.0 -O3 -march=native, forced inlining, on a stated Kaby Lake i5 2.3 GHz; the benchmark code is public at benchmarks/src/bench-mul.cpp (mul_cbn vs mul_gmp vs mul_ntl, Google Benchmark).
- **Verifier notes:** Numbers match Table 3 of the paper, but the record left out that they need -march=native plus forced inlining. I fixed the flags and noted the crossover point, where GMP becomes faster.
- **Fields the verifier corrected:** `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** paper Table 4: 4-limb Montgomery mult 39 ns vs libff hand-written asm 66 ns (forced inlining)
- **Pages the verifier opened:**
  - <https://arxiv.org/pdf/1804.07236>
  - <https://github.com/niekbouman/ctbignum>
  - <https://github.com/niekbouman/ctbignum/commits>
  - <https://raw.githubusercontent.com/niekbouman/ctbignum/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/niekbouman/ctbignum/HEAD/benchmarks/src/bench.cpp>
  - <https://raw.githubusercontent.com/niekbouman/ctbignum/HEAD/benchmarks/src/bench-mul.cpp>
- **Sources the enricher read:**
  - <https://github.com/niekbouman/ctbignum>
  - <https://raw.githubusercontent.com/niekbouman/ctbignum/HEAD/README.md>
  - <https://raw.githubusercontent.com/niekbouman/ctbignum/HEAD/doc/bigint.md>
  - <https://raw.githubusercontent.com/niekbouman/ctbignum/HEAD/doc/finitefield.md>
  - <https://raw.githubusercontent.com/niekbouman/ctbignum/HEAD/include/ctbignum/mult.hpp>
  - <https://raw.githubusercontent.com/niekbouman/ctbignum/HEAD/include/ctbignum/type_traits.hpp>
  - <https://raw.githubusercontent.com/niekbouman/ctbignum/HEAD/include/ctbignum/config.hpp>
  - <https://arxiv.org/abs/1804.07236>
  - <https://github.com/niekbouman/ctbignum/issues>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/niekbouman/ctbignum`) · [data/wave8/enrich/raw/github_com_niekbouman_ctbignum.json](../../../data/wave8/enrich/raw/github_com_niekbouman_ctbignum.json) (enrichment confidence 0.8)

</details>
