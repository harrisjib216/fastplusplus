# SHISHUA

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `CC0-1.0` · 🟡 stale

> Non-cryptographic SIMD PRNG for bulk byte streams; about 6.7x xoshiro256+ throughput on AVX2 Intel per first-party numbers.

| | |
|---|---|
| **Beats** | xoshiro256+ (also RomuTrio, wyrand, ChaCha8) |
| **Claimed result** | 52.93 GB/s on Intel vs xoshiro256+ 7.88 GB/s, RomuTrio 8.62 GB/s, wyrand 7.00 GB/s, ChaCha8 6.28 GB/s (xoshiro256+x8 40.18 GB/s) |
| **Workload** | Bulk 64-bit PRNG output on GCP N2 Intel instances, speed in GB/s from the repo's benchmark-perf script |
| **Metric** | throughput |
| **Hardware** | Intel Xeon (cpuinfo family 6 model 85, 2.8 GHz, GCP N2, AVX-512 capable) per test/benchmark-perf-intel |
| **Compiler and flags** | \$(CC) unstated (gcc branch in Makefile); CFLAGS -O3 -g -march=native |
| **Adoption** | 229 stars |
| **Last commit** | 2023-08-05 |
| **Links** | [repository](https://github.com/espadrine/shishua) · [benchmark](https://github.com/espadrine/shishua) |

## Verdict

The author's benchmark-perf script ran on a GCP N2 KVM guest reporting 'Intel(R) Xeon(R) CPU' family 6 model 85 at 2.8 GHz, built with -O3 -march=native and an unstated compiler. It measured SHISHUA at 0.0527 cycles/byte (52.93 GB/s) against xoshiro256+ at 7.99 GB/s in the raw file (7.88 in the README), RomuTrio 8.62, wyrand 7.00, ChaCha8 6.28 and an 8-way vectorized xoshiro256+ at 40.18 GB/s. These are first-party numbers and were not compared with std::mt19937.

## Use it when

- Filling large buffers with random bytes (Monte Carlo inputs, test data, noise, hashing salts) where GB/s matters more than per-call latency
- x86-64 hosts with AVX2, which is where the 52.93 GB/s figure was measured
- You can consume output in 128-byte blocks, or wrap it in your own buffered next() function
- You want a CC0 source-drop with no dependencies and need PractRand quality (the author reports passing 32 TiB, plus BigCrush)

## Skip it when

- Any security use: the README says not to use it for cryptography and points to ChaCha20
- Code that needs one value at a time with low latency or a std::uniform_random_bit_generator engine: you must write the buffering layer yourself
- ARM: the author's Graviton figure is 8.78 GB/s, and GCC's NEON codegen is slow enough that the header falls back to scalar unless the compiler is Clang
- You need jump-ahead, independent substreams with guarantees, or reproducible streams across versions: none of these is documented
- Projects that need a maintained dependency: last commit August 2023, and a request for a shared-library build (issue #10) is still open

## How it is fast

The state is four 256-bit vectors plus a 256-bit counter. Each 128-byte round uses only shift, 32-bit lane permute (_mm256_permutevar8x32_epi32) and 64-bit add, then XORs pairs of state parts to make the output. There is no multiplication and the dependency chain per round is short. Writing 128 bytes per iteration amortizes loop overhead, which is how it reaches roughly 0.05 cycles per byte on AVX2.

## Compared with alternatives

Pick SHISHUA over xoshiro8x256pp, Xoshiro256PlusSIMD or SIMDxorshift when you want the highest bulk throughput and better PractRand results than xoshiro256+-style generators (the author's table: xoshiro256+x8 fails at 1 KiB, SHISHUA passes 32 TiB). Pick simdpcg instead when you need a stream identical to the reference PCG32, and testingRNG's aesctr or Randen when you want an AES-based construction.

## Integration

| | |
|---|---|
| **Form** | source-drop (C header shishua.h plus per-ISA headers shishua-avx2.h / -sse2.h / -neon.h) |
| **Dependencies** | none (libc, plus &lt;immintrin.h&gt;/&lt;arm_neon.h&gt; for the SIMD paths) |
| **Minimum toolchain** | C99 compiler with AVX2 intrinsics for the fast path (the Makefile builds the AVX2 variant with -mavx2 -mtune=haswell); exact minimum not documented |
| **Platforms** | x86-64 (AVX2 fast path, SSE2/SSSE3 fallback), aarch64/ARMv7 NEON (auto-selected only with Clang), portable scalar fallback elsewhere; RISC-V vector support requested (issue #9) but not implemented |
| **Thread safety** | not documented; state is a plain struct with no globals besides a const seed table, so one prng_state per thread is the safe pattern |
| **Drop-in for the baseline** | partial: it replaces bulk xoshiro256+/wyrand output, but the API is buffer-fill (prng_gen) rather than next(), and the output stream differs from those generators |

## Gotchas

- prng_gen asserts that size % 128 == 0, and the AVX2 path stores 32-byte chunks without alignment requirements (storeu). Tail handling is a TODO in the source.
- prng_init is defined in the header as a non-static, non-inline function, so including shishua.h in more than one translation unit causes duplicate-symbol link errors. Wrap it in one .c file.
- The SIMD, scalar and NEON paths are meant to produce the same bytes (the Makefile has per-target test vectors), but endianness handling is explicit only in the scalar path. Check on big-endian targets.
- README footnote 1 says 'cycles per byte' but the table shows GB/s, and the raw Intel file has xoshiro256+ at 7.99 GB/s while the README says 7.88.

## Known shortcomings

- Compiler/version unstated (-O3 -march=native); CPU only generic 'Intel Xeon' (model 85, KVM); raw bench file says xoshiro256+ 7.99 GB/s where README says 7.88; CC0 gives no patent grant.
- Correction: AVX2 not required (SSE2, NEON with Clang, scalar fallback); AVX2 only for the 52.93 GB/s figure. prng_init is non-static non-inline in the header (two TUs break the link); buffer must be a multiple of 128 bytes; README says 'cycles per byte' but table shows GB/s.

## Caveats and trade-offs

First-party numbers; the compiler and version are unstated, and the CPU shows only as a generic 'Intel(R) Xeon(R) CPU' (family 6 model 85) under KVM. The raw test/benchmark-perf-intel file lists xoshiro256+ at 7.99 GB/s while the README table says 7.88 GB/s. CC0 means no patent grant. Compares against scalar xoshiro256+ and the author's 8-way vector variant, not std::mt19937. Uses SIMD (AVX2) paths.

Needs AVX2 (state is two 256-bit registers); ARM path is much slower (8.78 GB/s); output not reversible; non-cryptographic.

## Maintenance

Stale (last commit August 2023, 4 open issues) but CC0 and a few hundred lines of header code, so it is easy to vendor; Rust, Node.js and Python ports exist.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table backed by test/benchmark-perf-intel (lscpu shows a generic 'Intel(R) Xeon(R) CPU', family 6 model 85, KVM on GCP N2). The Makefile gives -O3 -g -march=native, but the compiler and its version are unstated (\$(CC)) and the exact CPU model name is not given, so it falls short of A.
- **Verifier notes:** README numbers match the claim (SHISHUA 52.93 GB/s, xoshiro256+x8 40.18, RomuTrio 8.62, xoshiro256+ 7.88, wyrand 7.00, ChaCha8 6.28). The raw benchmark file is dated 2021-01-01 and shows xoshiro256+ at 7.99 GB/s.
- **Fields the verifier corrected:** `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/espadrine/shishua/HEAD/README.md>
  - <https://raw.githubusercontent.com/espadrine/shishua/HEAD/test/benchmark-perf-intel>
  - <https://raw.githubusercontent.com/espadrine/shishua/HEAD/Makefile>
  - <https://github.com/espadrine/shishua/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/espadrine/shishua/HEAD/README.md>
  - <https://raw.githubusercontent.com/espadrine/shishua/HEAD/shishua.h>
  - <https://raw.githubusercontent.com/espadrine/shishua/HEAD/shishua-avx2.h>
  - <https://raw.githubusercontent.com/espadrine/shishua/HEAD/shishua-neon.h>
  - <https://raw.githubusercontent.com/espadrine/shishua/HEAD/shishua-sse2.h>
  - <https://raw.githubusercontent.com/espadrine/shishua/HEAD/prng.c>
  - <https://raw.githubusercontent.com/espadrine/shishua/HEAD/Makefile>
  - <https://raw.githubusercontent.com/espadrine/shishua/HEAD/test/benchmark-perf-intel>
  - <https://github.com/espadrine/shishua/issues>
  - <https://espadrine.github.io/blog/posts/shishua-the-fastest-prng-in-the-world.html>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/espadrine/shishua`) · [data/wave8/enrich/raw/github_com_espadrine_shishua.json](../../../data/wave8/enrich/raw/github_com_espadrine_shishua.json) (enrichment confidence 0.85)

</details>
