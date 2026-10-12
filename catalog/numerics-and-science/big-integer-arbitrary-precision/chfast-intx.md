# intx (fixed-size 256/512-bit integers)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Header-only C++20 fixed-width uint128-uint512 integers for EVM and crypto code; no published win over GMP yet.

| | |
|---|---|
| **Beats** | GMP (low-level mpn_tdiv_qr and mpn_mul_n, called through the repo's own wrappers in test/utils/gmp.hpp) |
| **Claimed result** | None published. The benchmark harness that pits intx against GMP exists, but no result, ratio or table is committed or quoted in the README, CHANGELOG, the PRs and issues I opened (#99, #129, #147, #194, #267, #55, #291, #367) or any other page I could open. The only numbers on those pages compare intx with earlier intx (for example PR #99: 256-bit division about 40% faster, 512-bit about 10% slower, 'Time Old/New' 55146 -&gt; 33118 for uint256/uint64). |
| **Workload** | The repo's intx-bench (Google Benchmark, test/benchmarks/benchmarks.cpp) times uint256 and uint512 udivrem against gmp::udivrem (mpn_tdiv_qr) for divisors of 64, 128, 192 and 256 bits, and uint256 and uint512 multiplication against gmp::mul and gmp::mul_full (mpn_mul_n). |
| **Metric** | latency |
| **Compiler and flags** | Not stated for any GMP comparison. Build per README: cmake -DCMAKE_BUILD_TYPE=Release (CMake default for GCC/Clang Release is -O3 -DNDEBUG); intx-bench adds -falign-functions=32 on GCC/Clang (test/benchmarks/CMakeLists.txt); no -march flag there. |
| **Adoption** | 176 stars, 41 forks, 1,113 commits (github.com page, opened 2026-10-03); a required dependency of ethereum/evmone (its CMakeLists.txt calls hunter_add_package(intx) / find_package(intx)); packaged on Conan Center (README badge). |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/chfast/intx) |

## Verdict

Nothing has been measured against GMP in public: intx-bench registers uint256/uint512 udivrem against mpn_tdiv_qr and multiplication against mpn_mul_n (Google Benchmark, CMake Release, -falign-functions=32, no -march), but no results are committed or quoted. The only published numbers are intx versus earlier intx (PR #99: 256-bit division by 64- and 128-bit values up to 40% faster) and PR #367's CI medians across 13 CPU types, where intx's software reciprocal_2by1 is 2-3x slower than the x86 divq instruction on Ice Lake and Zen 5 (11.4 vs 4.0 ns; 8.9 vs 4.1 ns) but 4.7x faster on Coffee Lake (5.7 vs 26.4 ns).

## Use it when

- EVM, Solidity tooling or blockchain clients that need exact 256-bit wrapping arithmetic; evmone already depends on it.
- Hot loops over fixed 256- or 512-bit values where mpz allocation and size bookkeeping would dominate, e.g. small-operand division (256/64, 256/128) and full 256x256-&gt;512 products.
- Code that needs compile-time (constexpr/consteval) big-integer constants, including division at compile time.
- Projects that want a single header with no link dependency and can use C++20, on x86-64, arm64 or big-endian targets.

## Skip it when

- Operands that grow or vary in size (RSA, number theory, bignum factorials): there is no variable-size type, so use GMP, FLINT or Boost.Multiprecision.
- You need a measured speedup over GMP before adopting: the repo has a GMP benchmark harness but publishes no results, so the claim is unproven (tier D).
- Plain 128-bit math: a third-party harness (mikelik/int128-benchmark, 2023, GCC and Clang, 20-thread 4.6 GHz CPU) has intx::uint128 slower than unsigned __int128, absl::uint128 and even boost uint128_t for add (16.8 vs 1.74, 7.10, 13.2 ns with GCC); use the compiler builtin or _BitInt(128).
- Repeated modular multiplication with a fixed modulus (elliptic-curve fields): mulmod computes the full product and then runs Knuth division, with no Montgomery or Barrett form.
- Signed arithmetic as a type: there is no signed intN (issue #112 open); only sdivrem interprets the bits as two's complement.

## How it is fast

Everything is inline templates over a fixed word count, so there is no heap allocation, no size field and no dispatch; carries use compiler builtins (__builtin_addcll/__builtin_subcll or the x86 addcarryx/sbb intrinsics) and 64x64-&gt;128 products use unsigned __int128 or MSVC _umul128. Division follows Moller and Granlund's 'Improved division by invariant integers' (a table-seeded reciprocal_2by1/reciprocal_3by2 replaces the hardware divide), with dedicated 1-word and 2-word divisor paths and Knuth Algorithm D for longer divisors. addmod has a fast path for moduli of at least 2^192 with already-reduced operands (ported from holiman/uint256 PR #86).

## Compared with alternatives

Pick intx over ctbignum or Boost.Multiprecision's fixed cpp_int when you want a minimal, production-tested (evmone) uint256/uint512 value type with EVM helpers and byte-order I/O; pick ctbignum for fixed-modulus Montgomery arithmetic or Boost cpp_int when you need signed or checked types, since both publish measured wins over GMP and intx does not.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the library (single include/intx/intx.hpp); the tests and intx-bench pull Google Benchmark via Hunter and need GMP |
| **Minimum toolchain** | C++20 (required since 0.10.0); CMake 3.16+ if using its CMake package; MSVC x64 19.44+ / arm64 19.50+ to avoid a compiler miscompile of addc in constant evaluation (issue #369) |
| **Platforms** | any 64-bit-word target; uses __int128 where available and _umul128 on MSVC x64, with portable fallbacks; CI covers non-x86 architectures and big-endian since 0.8.0; 32-bit Windows build fixed in 0.9.1 |
| **Thread safety** | Plain value types with no mutable global state (the only global is a constexpr reciprocal lookup table), so concurrent use of distinct objects is safe; not otherwise documented. |
| **Drop-in for the baseline** | partial — replaces fixed-size uses of GMP's mpn layer (the 64-bit words are layout-compatible, as the repo's own gmp.hpp wrappers cast them to mp_limb_t), but has no mpz/mpf API, no variable sizes and no signed type |

## Gotchas

- Division by zero is undefined behavior in release builds: INTX_REQUIRE is assert() with NDEBUG unset and __builtin_unreachable() otherwise.
- from_string&lt;uint256&gt;() silently wraps some out-of-range 78-digit decimal inputs (issue #343, e.g. a value just above 2^256-1 parses as 9); the fix, PR #370, was still unmerged when checked, so validate untrusted decimal input yourself.
- from_string/to_string throw std::invalid_argument or std::out_of_range; with -fno-exceptions they print to stderr and abort(). Arithmetic operators are noexcept.
- Xcode 14.3.1 on arm64 miscompiled __builtin_subcll; intx works around it from 0.9.3 and 0.10.1 (CHANGELOG, PR #294), so older intx versions built with that Xcode can give wrong subtraction results.

## Known shortcomings

- Tier D: no published intx-vs-GMP numbers anywhere; kept because ethereum/evmone depends on it, so it is widely referenced. Last commit 2026-10-02.
- from_string&lt;uint256&gt; silently wraps some 78-digit inputs (issue #343 open, fix PR #370 unmerged); division by zero is undefined behaviour in release builds (INTX_REQUIRE becomes unreachable). mikelik/int128-benchmark has intx::uint128 slower than __int128, absl and boost for add and mul. PR #367 (merged 2026-10-01) has CI medians on 13 CPUs for reciprocal_2by1 vs x86 divq (Ice Lake 11.4 vs 4.0 ns, Zen 5 8.9 vs 4.1 ns, Coffee Lake 5.7 vs 26.4 ns), still intx vs hardware, not GMP.

## Caveats and trade-offs

Does not qualify as a speed claim yet: no published number against GMP, so tier D. The code to measure it is public (Apache-2.0, intx-bench links GMP via find_package(GMP)), so a later pass could run intx-bench and promote it. The newest PRs report only intx-vs-intx changes (PR #376: udivrem uint256 4-word divisor -4.6% with clang-23, -3.3% with GCC 16, as instruction-count reductions; PR #375: code size only); CHANGELOG mentions division up to 40% faster than earlier intx. Counter-evidence for 128-bit: in a third-party harness (https://github.com/mikelik/int128-benchmark, README, GCC run, 20-core CPU at 4600 MHz, flags and CPU model not stated) intx::uint128 is slower than boost::multiprecision::uint128_t: add 16.8 ns vs 13.2 ns, multiply 15.2 ns vs 13.1 ns; that repo has no GMP benchmark (not re-opened in this verification). docs/benchmarks.md returned 404 for the search agent.

Header-only C++20, allocation-free fixed-width types stored as arrays of uint64_t words (uint128, uint256, uint384, uint512 and any word count); no variable-size integers, so it is not a replacement for GMP mpz. Behaves like built-in unsigned types; division and modular helpers (addmod, mulmod, exp) target EVM and elliptic-curve use.

## Maintenance

Actively maintained by one maintainer (v0.15.0 released 2026-01-30; reciprocal benchmarks merged 2026-10-01), Apache-2.0, a single header that is easy to vendor, also on Conan Center.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification D, tier now D.
- **Tier reason:** benchmark_url is null and no published intx-vs-GMP number exists on the pages I opened: test/benchmarks/benchmarks.cpp registers div&lt;uint256/uint512, gmp::udivrem&gt; and binop&lt;..., gmp::mul/mul_full&gt; rows, but the README, CHANGELOG and the newest PRs (#375, #376) give no results, only intx-vs-intx deltas.
- **Verifier notes:** Kept rather than rejected as not-notable: under 1k stars, but it is the 256-bit integer library that ethereum/evmone requires, so it is widely referenced. Promotion needs someone to run intx-bench (GMP rows already exist).
- **Fields the verifier corrected:** `last_commit`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/chfast/intx/HEAD/README.md>
  - <https://raw.githubusercontent.com/chfast/intx/HEAD/test/benchmarks/benchmarks.cpp>
  - <https://raw.githubusercontent.com/chfast/intx/HEAD/test/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/chfast/intx/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/chfast/intx/HEAD/LICENSE>
  - <https://github.com/chfast/intx>
  - <https://github.com/chfast/intx/commits>
  - <https://github.com/chfast/intx/pull/375>
  - <https://github.com/chfast/intx/pull/376>
  - <https://raw.githubusercontent.com/ethereum/evmone/HEAD/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/chfast/intx/HEAD/README.md>
  - <https://raw.githubusercontent.com/chfast/intx/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/chfast/intx/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/chfast/intx/HEAD/include/intx/intx.hpp>
  - <https://raw.githubusercontent.com/chfast/intx/HEAD/test/benchmarks/benchmarks.cpp>
  - <https://raw.githubusercontent.com/chfast/intx/HEAD/test/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/chfast/intx/HEAD/test/utils/gmp.hpp>
  - <https://github.com/chfast/intx>
  - <https://github.com/chfast/intx/issues?q=is%3Aissue>
  - <https://github.com/chfast/intx/issues/343>
  - <https://github.com/chfast/intx/issues/323>
  - <https://github.com/chfast/intx/issues/304>
  - <https://github.com/chfast/intx/issues/192>
  - <https://github.com/chfast/intx/issues/369>
  - <https://github.com/chfast/intx/pull/370>
  - <https://github.com/chfast/intx/pull/367>
  - <https://github.com/boostorg/multiprecision/issues/195>
  - <https://raw.githubusercontent.com/mikelik/int128-benchmark/HEAD/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/chfast/intx`) · [data/wave8/enrich/raw/github_com_chfast_intx.json](../../../data/wave8/enrich/raw/github_com_chfast_intx.json) (enrichment confidence 0.75)

</details>
