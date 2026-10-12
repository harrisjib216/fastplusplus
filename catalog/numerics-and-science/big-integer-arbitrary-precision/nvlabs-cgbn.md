# CGBN (Cooperative Groups Big Numbers)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> NVIDIA's header-only CUDA library for fixed-size unsigned big integers; a V100 out-throughputs 20-core OpenMP GMP 4-77x on batches.

| | |
|---|---|
| **Beats** | GMP 6.1.2 (OpenMP, 20-core Xeon) |
| **Claimed result** | README speed-up table, Tesla V100 vs Xeon E5-2698v4 (GMP+OpenMP), average over 128-8192 bits: add 77.4x, sub 77.1x, mul (low) 43.5x, mont_reduce 29.3x, powm_odd 21.4x, div_qr 14.4x, sqrt 11.3x, gcd 6.9x, mod inv 4.1x; per-size extremes: 128-bit add 174.3x, 128-bit mul (low) 172.9x, 8192-bit powm_odd 16.8x, 8192-bit mod inv 4.0x |
| **Workload** | Batched fixed-size unsigned big-integer operations (add, sub, low multiply, Montgomery reduction, odd modular exponentiation, div/qr, sqrt, gcd, modular inverse) at 128 to 8192 bits, one CUDA cooperative group of 4/8/16/32 threads per number, versus GMP calls spread over 20 CPU cores with OpenMP. |
| **Metric** | throughput |
| **Hardware** | NVIDIA Tesla V100 (Volta) GPU vs Intel Xeon E5-2698v4, 20 cores at 2.2 GHz |
| **Compiler and flags** | perf_tests/Makefile: nvcc -I../include -arch=sm_70 xmp_tester.cu -lgmp (no explicit -O; CUDA 10+ required for Volta, exact version not stated); GMP side: g++ gmp_tester.cc -o gmp_tester -lgmp -fopenmp (no -O flag, so the harness loop builds at g++'s default -O0; libgmp itself is built separately with its own ./configure); compiler versions and GMP configure flags not stated |
| **Adoption** | 252 stars, 80 forks |
| **Last commit** | 2026-03-31 |
| **Links** | [repository](https://github.com/NVlabs/CGBN) · [benchmark](https://github.com/NVlabs/CGBN) |

## Verdict

NVIDIA's 2018 beta measured batch throughput on a Tesla V100 against GMP 6.1.2 running across all 20 cores of a 2.2 GHz Xeon E5-2698v4 with OpenMP, using the repo's perf_tests (nvcc -arch=sm_70; the GMP driver built with g++ -fopenmp and no -O flag): average speedups over 128-8192 bits of 77.4x (add) down to 4.1x (modular inverse). Compiler versions are not stated, and the comparison is GPU device throughput versus CPU, not a faster algorithm.

## Use it when

- Large batches (thousands or more) of independent fixed-width operations: RSA/DH-style modular exponentiation, Montgomery multiplication, primality testing or sieving, where each instance is 128-8192 bits.
- Workloads already on an NVIDIA GPU where you can write your own CUDA kernel around the arithmetic, e.g. GPU Miller-Rabin (the repo's sample 4) or prime-gap searches.
- Throughput-bound jobs where moving data to the GPU is amortized: the README's averages are 77x (add), 43.5x (low mul), 29.3x (Montgomery reduce) and 21.4x (odd powm) over 20-core OpenMP GMP on a V100.
- Building blocks for higher-level GPU multiprecision libraries (gnu-mpfr-cgbn and the steleman/nvidia-cgbn fork build on it).

## Skip it when

- Single values or small batches: it only pays off with many concurrent instances, and per-operation latency including transfer will lose to GMP on the CPU.
- Signed, variable-size or mixed-size integers, operands above 32K bits, or sizes not divisible by 32 (open issues #3 and #13); copying between environments of different sizes is described as very slow.
- Secret-key cryptography that needs constant time: CONSTANT_TIME exists as a parameter but a checked context reports cgbn_unsupported_operation when it is set, and the library cgbn_modular_power is plain binary square-and-multiply.
- Non-NVIDIA hardware, or Blackwell (sm_120) GPUs without testing: the Makefile targets stop at Ampere, and a third-party README (mr_blackwell) reports CGBN running orders of magnitude slower than expected there.
- gcd- and inverse-heavy workloads: the README says these are not optimal, and the docs call the number-theoretic functions 'a little bit slow'.

## How it is fast

Instead of one thread per bignum (which runs out of registers), each value's 32-bit limbs are distributed across TPI threads and kept in registers, and carries, comparisons and broadcasts move between the group's lanes with warp shuffles (__shfl_sync). Sizes and thread counts are template parameters, so loops over the per-thread limbs are fully unrolled, and the code picks multiply-add instruction sequences per architecture (IMAD/XMAD/WMAD paths selected by __CUDA_ARCH__). Throughput comes from running thousands of these groups concurrently on the GPU; the headline powm number uses a hand-written 5-bit fixed-window Montgomery kernel in the perf tests.

## Compared with alternatives

Pick CGBN over CPU libraries such as ctbignum, blip_mp or mp++ when you have thousands of independent fixed-width operations and an NVIDIA GPU; pick midint-arithmetic-division or TzdLanguage's NTT for a few very large operands, and gnu-mpfr-cgbn when you need MPFR-style floating point on top of CGBN.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | CUDA toolkit; GMP for the host-side mpz backend, samples and perf tests; Google Test for unit tests |
| **Minimum toolchain** | CUDA 9.0+ for Kepler/Maxwell/Pascal, CUDA 10+ for Volta and newer (README); a CUDA 12.5 build problem (issue #31) was fixed in 2025 |
| **Platforms** | NVIDIA GPUs; Makefile targets sm_35 (Kepler) through sm_80 (Ampere); no CPU fallback without GMP (cgbn_cpu.h is an #error stub) |
| **Thread safety** | Values live in each thread's registers; every thread in a TPI group must call each API together with identical uint32_t arguments or results are undefined; errors are reported through an atomicCAS on a shared cgbn_error_report_t |
| **Drop-in for the baseline** | no |

## Gotchas

- The perf-table powm_odd uses a 512-bit exponent at every modulus size and a custom fixed-window Montgomery kernel (perf_tests/xmp_test_powm.cu), not the library's cgbn_modular_power; the README itself says the sample-3 odd-modulus powm is much faster than the library API.
- Open bug #15 (2021, no reply): cgbn_mont_sqr returned (a^2 mod m) + m for a 971-bit modulus, i.e. an unreduced result; reduce or compare before trusting mont_sqr output.
- Open issue #23: cgbn_div, cgbn_div_rem and cgbn_div_rem_wide fail to compile ('incomplete type is not allowed') above 512 bits in the reporter's setup; issue #33 reported multiple-definition link errors with several .cu files, which the 2026-03-31 'Mark non-templated functions inline' commit appears to address.
- Do not #define TPI before including cgbn/cgbn.h (the docs warn it breaks compilation), and the default context constructor uses cgbn_no_checks, so errors such as division by zero are silent unless you pass a monitor and report object.

## Known shortcomings

- V100 vs 20-core Xeon measures hardware throughput, not the algorithm; the GMP harness is built without an -O flag (driver at -O0), handicapping the baseline; compiler versions unstated.
- Open bug #15: mont_sqr returns an unreduced result ((a^2 mod m)+m, 971-bit modulus, 2021, no reply); #23 div/div_rem do not compile above 512 bits; CONSTANT_TIME=true reports unsupported_operation; the README powm_odd table uses a 512-bit exponent at every size and a custom fixed-window Montgomery kernel (perf_tests/xmp_test_powm.cu), not the library's cgbn_modular_power.

## Caveats and trade-offs

Numbers are first-party, from the 2018 beta on a V100 against GMP 6.1.2 (current GMP is 6.3.x). This compares a GPU with a CPU, so it measures per-device throughput on large batches of independent operations, not a better algorithm; single-operand latency would lose to GMP. The GMP driver (perf_tests/gmp_tester.cc) is compiled with no optimisation flag, which inflates loop overhead around the cheapest calls and probably the 128-bit add/sub ratios (174x). Only libgmp's own code is optimised. Compiler versions are not stated. A third-party report (pscamillo/mr_blackwell README) says CGBN runs 'orders of magnitude slower than expected' on Blackwell (sm_120) GPUs, and the Makefile lists architectures only up to Ampere. steleman/nvidia-cgbn is a fork adding signed integers and Ada/Blackwell support (tested with CUDA 12.9/13.2); it is not reported separately. Supports fixed sizes only, up to 32K bits in multiples of 32.

Needs an NVIDIA GPU and CUDA (Kepler through Ampere targets in the Makefile). Fixed-size unsigned integers only, 32 to 32K bits in 32-bit steps, 4/8/16/32 threads per number, written inside CUDA kernels with a fixed number of bits per kernel. It pays off for large batches of independent numbers, not for one big number. No floating point, no arbitrary-size operands.

## Maintenance

MIT-licensed NVIDIA Research code (252 stars) that has stayed at its 2018 'XMP 2.0 beta' feature level, with only small maintenance commits since (latest 2026-03-31) and several open correctness and compile issues; it is vendorable and still the common base for GPU bignum work, and the steleman/nvidia-cgbn fork adds signed integers and Ada/Blackwell support.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now C.
- **Tier reason:** The README speed-up table (V100 vs a 20-core Xeon E5-2698v4 running GMP 6.1.2 with OpenMP) is first-party. The harness is public (perf_tests/xmp_tester.cu, perf_tests/gmp_tester.cc and the gmp-run targets). Neither the nvcc/CUDA nor the g++ version is stated, and the GMP harness Makefile line has no optimisation flag, so this falls short of A.
- **Verifier notes:** The README table matches the record exactly. The LICENSE file is the MIT text (Copyright 2015 NVIDIA), with 252 stars, 80 forks, last commit 2026-03-31, not archived and not a fork. The prime-gap usage is confirmed: sethtroisi/prime-gap README says gap_test_gpu is experimental and uses CGBN.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/NVlabs/CGBN>
  - <https://github.com/NVlabs/CGBN/commits/master>
  - <https://raw.githubusercontent.com/NVlabs/CGBN/HEAD/README.md>
  - <https://raw.githubusercontent.com/NVlabs/CGBN/HEAD/Makefile>
  - <https://raw.githubusercontent.com/NVlabs/CGBN/HEAD/perf_tests/Makefile>
  - <https://raw.githubusercontent.com/NVlabs/CGBN/HEAD/perf_tests/gmp_tester.cc>
  - <https://raw.githubusercontent.com/NVlabs/CGBN/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/pscamillo/mr_blackwell/HEAD/README.md>
  - <https://raw.githubusercontent.com/steleman/nvidia-cgbn/HEAD/README.md>
  - <https://raw.githubusercontent.com/sethtroisi/prime-gap/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/NVlabs/CGBN/issues?q=is%3Aissue>
  - <https://github.com/NVlabs/CGBN/issues/15>
  - <https://github.com/NVlabs/CGBN/issues/23>
  - <https://github.com/NVlabs/CGBN/issues/33>
  - <https://github.com/NVlabs/CGBN/commits/master>
  - <https://github.com/NVlabs/CGBN/tree/master/include/cgbn>
  - <https://raw.githubusercontent.com/NVlabs/CGBN/HEAD/README.md>
  - <https://raw.githubusercontent.com/NVlabs/CGBN/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/NVlabs/CGBN/HEAD/Makefile>
  - <https://raw.githubusercontent.com/NVlabs/CGBN/HEAD/docs/CGBN.md>
  - <https://raw.githubusercontent.com/NVlabs/CGBN/HEAD/include/cgbn/cgbn.h>
  - <https://raw.githubusercontent.com/NVlabs/CGBN/HEAD/include/cgbn/cgbn.cu>
  - <https://raw.githubusercontent.com/NVlabs/CGBN/HEAD/include/cgbn/cgbn_cuda.h>
  - <https://raw.githubusercontent.com/NVlabs/CGBN/HEAD/include/cgbn/impl_cuda.cu>
  - <https://raw.githubusercontent.com/NVlabs/CGBN/HEAD/include/cgbn/cgbn_mpz.h>
  - <https://raw.githubusercontent.com/NVlabs/CGBN/HEAD/include/cgbn/cgbn_cpu.h>
  - <https://raw.githubusercontent.com/NVlabs/CGBN/HEAD/perf_tests/Makefile>
  - <https://raw.githubusercontent.com/NVlabs/CGBN/HEAD/perf_tests/gmp_tester.cc>
  - <https://raw.githubusercontent.com/NVlabs/CGBN/HEAD/perf_tests/gmp_tests.cc>
  - <https://raw.githubusercontent.com/NVlabs/CGBN/HEAD/perf_tests/xmp_tester.cu>
  - <https://raw.githubusercontent.com/NVlabs/CGBN/HEAD/perf_tests/xmp_tests.cu>
  - <https://raw.githubusercontent.com/NVlabs/CGBN/HEAD/perf_tests/xmp_test_powm.cu>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/nvlabs/cgbn`) · [data/wave8/enrich/raw/github_com_nvlabs_cgbn.json](../../../data/wave8/enrich/raw/github_com_nvlabs_cgbn.json) (enrichment confidence 0.8)

</details>
