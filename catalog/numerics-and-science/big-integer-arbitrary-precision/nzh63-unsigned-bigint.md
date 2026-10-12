# Unsigned Bigint (fixed-width ADX/BMI2 big integer)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> Fixed-width unsigned big integer for MSVC x64 with MASM MULX/ADX kernels; beats Boost.Multiprecision on add/sub/mul/modexp, loses on division.

| | |
|---|---|
| **Beats** | Boost.Multiprecision (backend and version not stated) |
| **Claimed result** | README table (run time, lower is better; 500,000 ops for add/sub/mul/div, 1,000 for modexp), Unsigned Bigint vs boost: multiply 0.019142 vs 0.0335125 at 256 bits and 1.2972828 vs 5.5994093 at 4096 bits (1.75x to 4.32x across sizes, derived from page data); modular exponentiation 0.0675292 vs 0.2627964 at 256 bits and 52.701681 vs 445.34939 at 4096 bits (3.9x and 8.4x; peak 10.3x at 2048 bits, 7.361546 vs 76.14449; derived from page data); add 1.4x to 2.6x and subtract 1.5x to 3.0x faster (derived from page data). Division is slower at every size: 0.9787682 vs 0.2175322 at 256 bits (about 4.5x slower) and 11.174972 vs 10.216111 at 4096 bits. |
| **Workload** | Add, subtract, multiply, divide (500,000 operations each) and modular exponentiation (1,000 operations) on fixed 256, 512, 1024, 2048 and 4096-bit unsigned integers, run time in the README table (units not stated). |
| **Metric** | latency |
| **Hardware** | CPU model not stated; needs ADX, BMI2 and RDRAND (Intel Haswell or newer, AMD Ryzen or newer) |
| **Compiler and flags** | Visual Studio 2017 (build requirement); flags and Boost version not stated |
| **Adoption** | 2 stars, 1 fork |
| **Last commit** | 2019-06-01 |
| **Links** | [repository](https://github.com/nzh63/Unsigned-Bigint) · [benchmark](https://github.com/nzh63/Unsigned-Bigint) |

## Verdict

The README table (author's own run; CPU, Boost version and backend, compiler flags and time units not stated; no benchmark source in the repo) times 500,000 add/sub/mul/div and 1,000 modular exponentiations at 256-4096 bits against Boost. Multiply is 1.75x to 4.32x and modexp 3.9x to 10.3x less time, add 1.4x to 2.6x and subtract 1.5x to 3.0x, while division is slower at every size (derived from page data).

## Use it when

- Windows x64 projects built with Visual Studio (v141 toolset or a compatible later one) that need fixed-width 256-4096-bit unsigned arithmetic dominated by multiplication or modular exponentiation
- Non-secret modular exponentiation at 512-4096 bits, where the README table shows 6.3x to 10.3x less run time than Boost (derived from page data)
- Studying a compact MULX/ADCX/ADOX schoolbook multiply and Montgomery modexp written in MASM
- Code that already treats big integers as fixed-size values (no heap allocation per number) and can live with wraparound on overflow

## Skip it when

- Division- or remainder-heavy code: the README table shows division slower than Boost at every size, 4.0x to 5.3x at 256-1024 bits and 1.1x to 1.25x at 2048-4096 bits (derived from page data), and % uses the same algorithm
- Cryptography with secret exponents: fast_pow_mod uses a variable-time sliding window with data-dependent branches, randIntel() ignores RDRAND's failure flag, and Miller-Rabin witnesses come from std::rand()
- Linux, macOS, GCC or Clang builds, 32-bit targets, or non-x86 CPUs: the code uses MASM, __stdcall, &lt;intrin.h&gt;, the MSVC-only 1i64 literal suffix and unsigned __int8, and the assembly uses 64-bit registers
- Sizes of 128 limbs (8192 bits) or more, and is_prime_number()/multiply_mod() at 4096 bits: these route through an untested double-precision FFT multiply with an out-of-bounds write (see gotchas); the unit tests cover only unsigned_bigint&lt;8&gt;
- Anything needing signed values, arbitrary/dynamic precision, rationals or floats; use GMP, Boost.Multiprecision or mp++ instead

## How it is fast

The limb loops are hand-written MASM: addition and subtraction are 4-way unrolled ADC/SBB chains, and the schoolbook multiply-accumulate (mul_mix_add) uses BMI2 MULX with the two independent ADX carry chains (ADCX/ADOX), the same trick GMP and OpenSSL use on Broadwell and later. Multiplication only computes the low N limbs (truncated product). Modular exponentiation converts to Montgomery form and uses a sliding window (k = 1 to 6 by exponent length) over a word-by-word Montgomery reduction built on the same MULX/ADX kernel; division is HAC Algorithm 14.20 with a bit-by-bit quotient correction loop, which is why it is slower than Boost.

## Compared with alternatives

Pick it over Boost.Multiprecision's fixed cpp_int only on Windows/MSVC x64 when multiply and Montgomery modexp dominate and division is rare; ctbignum gives a portable compile-time fixed-width alternative with a peer-reviewed comparison against GMP, and mp++ or FLINT/GMP are the safer choices for general or variable-size work.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none at run time; builds need Visual Studio 2017 (v141 toolset) with MASM build customizations |
| **Minimum toolchain** | Visual Studio 2017 (MSVC v141, default C++14 mode, std::complex_literals); other compilers not supported |
| **Platforms** | Windows x64 only; CPU needs BMI2, ADX and RDRAND. The README says Haswell or newer, but Haswell lacks ADX (ADCX/ADOX arrived with Broadwell), so on Haswell the multiply kernels would fault |
| **Thread safety** | not documented; values are plain arrays, but rand() and Miller-Rabin call std::rand(), which shares global state |
| **Drop-in for the baseline** | false — own class template unsigned_bigint&lt;N&gt; with a different API from boost::multiprecision::number; only unsigned, fixed width |

## Gotchas

- mul_fft (used by operator\* whenever the type has 128 or more limbs, including the unsigned_bigint&lt;2N&gt; temporary inside multiply_mod and Miller-Rabin at 4096 bits) writes one std::complex&lt;double&gt; past its heap buffer when the limb count is a power of two (n == LEN\*8, loop touches index LEN\*8); it also uses a cyclic convolution, so an overflowing product is not reduced mod 2^(64\*N) the way mul_classic is
- is_prime_number() on an even number above 2 trips assert(mod.bit(0) == 1) in fast_pow_mod (the pre-sieve starts at 3, not 2); with NDEBUG it runs Montgomery code with an even modulus, so the answer is not reliable
- multiply_mod_Montgomery ends with if (rlt &gt; mod) instead of &gt;=, so a result can come back equal to the modulus instead of 0; fast_pow_mod with a zero exponent scans exponent.bit() down to negative indices
- Octal input accepts the digit 8, and multiplication silently wraps on overflow (truncated N-limb product)

## Known shortcomings

- No benchmark source in the repo; single commit (2019-06-01), abandoned; division slower than Boost at every size.
- Memory-safety bug (code read): mul_fft (used at 128+ limbs, also by multiply_mod/Miller-Rabin at 4096 bits) writes one complex&lt;double&gt; past its heap buffer when LEN is a power of 2; is_prime_number on even input trips an assert; modexp is variable-time and RDRAND failure is ignored; README says Haswell but ADX needs Broadwell; tests cover only unsigned_bigint&lt;8&gt;; MSVC/MASM x64 only.

## Caveats and trade-offs

First-party table without benchmark source in the repository, compiler flags, CPU model, Boost version or backend (cpp_int fixed or dynamic), or run-time units. Division loses to Boost at every size shown (4.5x slower at 256 bits). Repository has a single commit ('first commit', 2019-06-01), Visual Studio 2017 solution only with MASM assembly, so effectively Windows/MSVC-only and abandoned. Not compared against GMP.

Fixed bit width chosen at compile time (unsigned_bigint&lt;N&gt;, N limbs of 64 bits), unsigned only, Visual Studio solution build, requires ADX, BMI2 and RDRAND, README in Chinese.

## Maintenance

Abandoned: a single commit from 2019-06-01, 2 stars, no issues or releases; Apache-2.0, so copyable, but the Windows/MSVC-only build and the memory-safety bug in the large-size FFT path make it reference material rather than something to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README 性能对比 table gives first-party run times vs Boost for add/sub/mul/div/modexp at 256-4096 bits, but no benchmark source is in the repo (UnitTest/ and example/ hold only tests and a demo), and no compiler flags, CPU model, Boost version/backend or units are stated.
- **Verifier notes:** README numbers match the record; the add/subtract range in the record (1.4x-2.4x) was understated and is corrected from the table. Only one commit exists (2019-06-01), so maintenance is abandoned.
- **Fields the verifier corrected:** `claimed_speedup`, `last_commit`, `maintenance_status`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/nzh63/Unsigned-Bigint>
  - <https://github.com/nzh63/Unsigned-Bigint/commits>
  - <https://github.com/nzh63/Unsigned-Bigint/tree/master/UnitTest>
  - <https://github.com/nzh63/Unsigned-Bigint/tree/master/example>
  - <https://github.com/nzh63/Unsigned-Bigint/tree/master/bigint>
  - <https://raw.githubusercontent.com/nzh63/Unsigned-Bigint/HEAD/README.md>
  - <https://raw.githubusercontent.com/nzh63/Unsigned-Bigint/HEAD/UnitTest/unsigned_bigint_UnitTest.cpp>
  - <https://raw.githubusercontent.com/nzh63/Unsigned-Bigint/HEAD/example/example.cpp>
- **Sources the enricher read:**
  - <https://github.com/nzh63/Unsigned-Bigint>
  - <https://github.com/nzh63/Unsigned-Bigint/tree/master/bigint>
  - <https://raw.githubusercontent.com/nzh63/Unsigned-Bigint/HEAD/README.md>
  - <https://raw.githubusercontent.com/nzh63/Unsigned-Bigint/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/nzh63/Unsigned-Bigint/HEAD/UnitTest/unsigned_bigint_UnitTest.cpp>
  - <https://raw.githubusercontent.com/nzh63/Unsigned-Bigint/HEAD/example/example.cpp>
  - <https://raw.githubusercontent.com/nzh63/Unsigned-Bigint/master/bigint/unsigned_bigint.h>
  - <https://raw.githubusercontent.com/nzh63/Unsigned-Bigint/master/bigint/unsigned_bigint.hpp>
  - <https://raw.githubusercontent.com/nzh63/Unsigned-Bigint/master/bigint/unsigned_bigint_asm.hpp>
  - <https://raw.githubusercontent.com/nzh63/Unsigned-Bigint/master/bigint/unsigned_bigint_io.hpp>
  - <https://raw.githubusercontent.com/nzh63/Unsigned-Bigint/master/bigint/unsigned_bigint.asm>
  - <https://raw.githubusercontent.com/nzh63/Unsigned-Bigint/master/bigint/overload_if.hpp>
  - <https://raw.githubusercontent.com/nzh63/Unsigned-Bigint/master/bigint/bigint.vcxproj>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/nzh63/unsigned-bigint`) · [data/wave8/enrich/raw/github_com_nzh63_unsigned_bigint.json](../../../data/wave8/enrich/raw/github_com_nzh63_unsigned_bigint.json) (enrichment confidence 0.8)

</details>
