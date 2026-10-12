# mr_blackwell (native Miller-Rabin GPU kernel)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `CUDA C++` · `Apache-2.0` · 🟢 active

> CUDA base-2 Miller-Rabin kernel with PTX-carry Montgomery multiplication; replaces CGBN in prime-gap and runs about 9x faster than the CPU/GMP pipeline.

| | |
|---|---|
| **Beats** | GMP (CPU Miller-Rabin probable-prime test with GMP modular exponentiation) |
| **Claimed result** | README standalone table: v2d kernel 1,805,000 PRP/sec at 683 bits labelled 132x versus 'CPU (GMP) 13,700' on a Ryzen 9 8800X3D (as named in the README), and 295,000 PRP/sec = 21x at 1240 bits; but the benchmark program computes these ratios against a hard-coded 13,700 constant rather than timing GMP. Measured end to end in the prime-gap pipeline (P=503, 13K tests): CPU gap_test_simple 28.0 s versus GPU v2 3.1 s, about 9x (derived from page data), with kernel throughput about 1,800,000 versus 13,700 PRP/sec. CGBN on Blackwell is described as 'impractical' / 'orders of magnitude slower' with no numbers. |
| **Workload** | Base-2 Miller-Rabin probable-prime tests (Montgomery CIOS modular exponentiation, 4-bit fixed window, PTX carry chains) on 65536 random 683-bit candidates, RTX 5070 GPU versus the CPU/GMP prime-gap test on a Ryzen 9 8800X3D. |
| **Metric** | throughput |
| **Hardware** | NVIDIA RTX 5070 (SM 12.0 Blackwell) versus AMD Ryzen 9 8800X3D |
| **Compiler and flags** | nvcc -O3 -arch=sm_120 (Makefile), CUDA 12.9, Linux Mint; GMP version and CPU baseline build flags not stated |
| **Adoption** | 3 stars, 1 fork, 18 commits; the README says it produced 60 prime-gap world records (as of 2026-05-05) through the sethtroisi/prime-gap pipeline |
| **Last commit** | 2026-05-05 |
| **Links** | [repository](https://github.com/pscamillo/mr_blackwell) · [benchmark](https://github.com/pscamillo/mr_blackwell) |

## Verdict

On an RTX 5070 (CUDA 12.9, nvcc -O3 -arch=sm_120) the standalone kernel tests 65,536 random odd 683-bit candidates at about 1.8 million base-2 PRP/sec (295,000 at 1240 bits). The '132x versus GMP' figure divides that by a hard-coded 13,700 PRP/sec from a single-threaded CPU run on a 'Ryzen 9 8800X3D' (as named in the README), with GMP version and flags not stated. The measured prime-gap run (P=503, 13K tests) takes 3.1 s on the GPU versus 28.0 s for CPU gap_test_simple, about 9x (derived from page data).

## Use it when

- You run sethtroisi/prime-gap's gap_test_gpu on a Blackwell GPU (sm_120), where the author reports CGBN as orders of magnitude too slow.
- Bulk base-2 PRP screening of many independent, pre-sieved odd numbers of 512-2048 bits (prime-gap and primorial searches) on a consumer NVIDIA GPU.
- The CPU PRP stage is your bottleneck: paired with the included hunt_parallel.sh, which overlaps CPU sieving with GPU testing (85 s down to 52 s per range in the script's own example).
- You want a small Apache-2.0 reference for Montgomery multiplication with PTX carry chains to adapt to another fixed-size modular-exponentiation kernel.

## Skip it when

- You need a proof of primality or a multi-base or BPSW test: only base 2 is tested and the rounds argument of test_runner_t is ignored, so base-2 strong pseudoprimes pass; confirm survivors on the CPU.
- Secret exponents or any cryptographic use: the code declares CONSTANT_TIME = false and uses exponent-indexed window tables and early exits.
- General bignum arithmetic, arbitrary bases or moduli, operands above 2048 bits, AMD/Intel GPUs or CPU-only machines.
- Pre-Blackwell NVIDIA GPUs where CGBN works: other architectures are listed as 'should work (untested)', and no comparison with CGBN on a GPU where CGBN runs normally is published.
- Multi-GPU or library embedding: test_runner_t hard-codes cudaSetDevice(0) and calls exit(1) on CUDA errors or oversized candidates.

## How it is fast

One GPU thread per candidate runs Montgomery CIOS multiplication written with inline PTX carry-chain instructions (mad.lo.cc, madc.hi, add.cc, addc), fixed-window modular exponentiation, and comparisons against 1 and n-1 done in Montgomery form to skip conversions. The limb count is a template parameter sized to the operand (22 limbs for 683 bits instead of 32, about 2x per the README). Version 2 computes R^2 mod n (by repeated doubling) and -n^-1 mod 2^32 (Newton iteration) on the device, so the host only exports limbs: per-candidate data drops from 268 to 136 bytes and the measured prime-gap run went from 92 s to 70 s.

## Compared with alternatives

Pick it over CGBN on Blackwell (sm_120) when you only need base-2 PRP tests at fixed sizes; CGBN remains the general GPU bignum library with published V100 results for add, mul and powm. For CPU-only batches, the AVX-512 truncated batch Montgomery entry (about 4-5x GMP on batched 1024-4096-bit Montgomery multiplications) is the closer alternative.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | CUDA Toolkit (README: 11.0+, 12.x recommended; tested with 12.9), GMP on the host for mpz_export and the correctness check |
| **Minimum toolchain** | nvcc from CUDA 11.0+ (README); built with nvcc -O3 -arch=sm_XXX |
| **Platforms** | NVIDIA GPUs SM 3.5+ claimed; only SM 12.0 (RTX 5070) tested; Linux (Linux Mint) tested |
| **Thread safety** | not documented; each test_runner_t owns one pinned host buffer and one device buffer and launches synchronously on device 0, so concurrent run_test calls on one runner would share those buffers |
| **Drop-in for the baseline** | partial — drop-in for CGBN's miller_rabin.h inside prime-gap only; not a replacement for GMP's mpz_probab_prime_p or for CGBN as a general GPU bignum library |

## Gotchas

- The '132x vs CPU (GMP)' and '21x' figures divide GPU throughput by a hard-coded 13,700 PRP/sec ('%.1fx vs CPU@13700' in mr_blackwell.cu); GMP is only an untimed correctness check (mpz_probab_prime_p(n, 1)), and the 13,700 comes from a single-threaded CPU run. The measured end-to-end comparison is 28.0 s versus 3.1 s, about 9x.
- The standalone benchmark kernel takes R^2 mod n and n0inv precomputed on the host, while the shipped header computes them on the GPU (its comments estimate about 8% extra kernel time), so 'make bench' does not time the shipped kernel exactly; both time the kernel only, without host-device copies.
- The code defaults to a 5-bit window (MR_WINDOW_BITS 5), while the README describes a 4-bit window and says 5 bits gave only 2.3%; the 32-entry table per thread (about 2.8 KB at 22 limbs, 5 KB at 40) lives in local memory.
- In the header LIMBS = BITS / 32, so BITS must be a multiple of 32 that covers the candidate (e.g. BITS=704 for P=503), or from_mpz_native aborts the process. The carry flag is passed between separate asm volatile statements, which relies on the compiler not inserting flag-clobbering instructions; the only correctness evidence is the GMP cross-check in 'make test'.

## Known shortcomings

- mr_blackwell.cu prints 'vs CPU' by dividing by a hard-coded 13700 and never times GMP (close to the zokio precedent, but the constant matches a CPU run from prime-gap reported in the README, so kept); measured pipeline 28.0 s vs 3.1 s (about 9x); CPU baseline gap_test_simple looks single-threaded; README names a CPU 'Ryzen 9 8800X3D' that is not a known model.
- The benchmark kernel is not the shipped kernel (the shipped header computes R^2 mod n on the GPU, the benchmark gets it from the host); only base 2 tested and the rounds argument is ignored; not constant-time (not for crypto); code uses a 5-bit window while the README describes 4-bit.

## Caveats and trade-offs

First-party README numbers. The standalone benchmark's 'vs CPU' column divides by a hard-coded 13700 (printf '%.1fx vs CPU@13700' in mr_blackwell.cu); GMP is used there only as an untimed correctness check via mpz_probab_prime_p(n, 1), so the 132x/21x ratios are not reproduced by the published harness. The 13,700 PRP/sec figure comes from sethtroisi/prime-gap's gap_test_simple, whose main loop is single-threaded at HEAD (no OpenMP), so the ratio is a GPU against what appears to be one CPU core; GMP version and CPU build flags are not stated. 'Ryzen 9 8800X3D' is the README's name for the CPU and does not match a known AMD model name, possibly a typo. The source header says 5-bit window by default while the README says 4-bit. Only Blackwell (sm_120) is tested; other architectures are listed as 'should work (untested)'. The CGBN-on-Blackwell slowness claim is the author's own observation without numbers. last_commit 2026-05-05 confirmed on the master commits page.

Specialised to Miller-Rabin / modular exponentiation of fixed-size odd moduli (template LIMBS dispatch, e.g. 22 limbs for 683 bits), not a general bigint library; NVIDIA GPUs only; drop-in replacement for the CGBN miller_rabin.h used by prime-gap.

## Maintenance

Recently active (18 commits, last 2026-05-05; 3 stars, no releases or open issues) and Apache-2.0 with a single header of about 19 KB, but tested on one RTX 5070 only and tied to prime-gap's interface.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party README tables only. The standalone benchmark (mr_blackwell.cu, 'make bench') times only the GPU kernel and prints its 'vs CPU' ratio by dividing by a hard-coded constant 13700; GMP (mpz_probab_prime_p) is called only as an untimed correctness check, so the 132x is not measured by the published harness. The only measured head-to-head is the first-party prime-gap pipeline table (28.0 s CPU vs 3.1 s GPU), without GMP version or CPU build flags.
- **Verifier notes:** Downgraded because the headline 132x is a hard-coded denominator in the benchmark program (similar in kind to the zokio precedent, though here the constant matches a separately reported CPU pipeline run); the measured pipeline comparison gives about 9x end to end. Kept at C rather than rejected; orchestrator may record this as a 'baseline not measured by harness' shortcoming.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/pscamillo/mr_blackwell/HEAD/README.md>
  - <https://github.com/pscamillo/mr_blackwell>
  - <https://github.com/pscamillo/mr_blackwell/commits/main>
  - <https://github.com/pscamillo/mr_blackwell/commits/master>
  - <https://raw.githubusercontent.com/pscamillo/mr_blackwell/HEAD/Makefile>
  - <https://raw.githubusercontent.com/pscamillo/mr_blackwell/HEAD/mr_blackwell.cu>
  - <https://raw.githubusercontent.com/pscamillo/mr_blackwell/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/sethtroisi/prime-gap/HEAD/gap_test_simple.cpp>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/pscamillo/mr_blackwell/HEAD/README.md>
  - <https://raw.githubusercontent.com/pscamillo/mr_blackwell/HEAD/Makefile>
  - <https://raw.githubusercontent.com/pscamillo/mr_blackwell/HEAD/mr_blackwell.cu>
  - <https://raw.githubusercontent.com/pscamillo/mr_blackwell/HEAD/miller_rabin_native.h>
  - <https://raw.githubusercontent.com/pscamillo/mr_blackwell/HEAD/hunt_parallel.sh>
  - <https://github.com/pscamillo/mr_blackwell>
  - <https://github.com/pscamillo/mr_blackwell/commits/main>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/pscamillo/mr_blackwell`) · [data/wave8/enrich/raw/github_com_pscamillo_mr_blackwell.json](../../../data/wave8/enrich/raw/github_com_pscamillo_mr_blackwell.json) (enrichment confidence 0.75)

</details>
