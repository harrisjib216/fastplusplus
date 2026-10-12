# fast-crc32 (corsix) — novel CRC32/CRC32C SIMD kernels

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Encoding (base64, hex, CRC)](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT OR Zlib` · 🟢 active

> Code generator emitting tuned CRC32/CRC32C C kernels (PCLMUL/VPCLMULQDQ/PMULL plus crc32 instruction) that beat Chromium zlib's SIMD CRC32.

| | |
|---|---|
| **Beats** | CRC32 |
| **Claimed result** | README headline vs previous state of the art: Apple M1 9.6% faster (77.55-&gt;85.05 GB/s; baseline dougallj Faster CRC32); Cascade Lake 25% (25.32-&gt;31.55 GB/s; baseline corsix crc32_4k_fusion); Ice Lake 56% (41.00-&gt;63.98 GB/s; baseline Chromium zlib vector AVX512 CRC32); Sapphire Rapids 19% (81.68-&gt;97.30 GB/s; baseline Chromium zlib vector AVX512, aligned inputs). Against Chromium zlib's NEON vector CRC32 on M1: 26.57-&gt;85.05 GB/s (\~3.2x, derived from page data) |
| **Workload** | Single-core CRC32/CRC32C throughput on large buffers across x86_64 (SSE, AVX-512, AVX-512+VPCLMULQDQ) and aarch64 (NEON, NEON+EOR3). Compared against Chromium zlib's crc32.c/crc32_simd.c, dougallj's Faster CRC32 (M1, Ampere Altra) and the author's earlier crc32_4k_\* implementations |
| **Metric** | throughput |
| **Hardware** | Apple M1; GCP Tau T2A (Ampere Altra); Intel Xeon Silver 4214 @2.2GHz (Cascade Lake), Intel Xeon @2.6GHz (Ice Lake), Intel Xeon Platinum 8481C @2.7GHz (Sapphire Rapids); AMD EPYC 7B12 (Rome/Zen2), EPYC 7B13 (Milan/Zen3), EPYC 9B14 (Genoa/Zen4) (/proc/cpuinfo excerpts in README) |
| **Compiler and flags** | gcc (version not stated) -O3 -march=native for the generated kernels (Makefile) and the Chromium/dougallj baselines (third_party/Makefile); per-ISA gcc-equivalent flags documented, e.g. -msse4.2 -mpclmul, -mavx512f -mavx512vl -mvpclmulqdq, -march=armv8-a+crypto+crc |
| **Adoption** | 141 stars |
| **Last commit** | 2025-11-27 |
| **Links** | [repository](https://github.com/corsix/fast-crc32) · [benchmark](https://github.com/corsix/fast-crc32#readme) |

## Verdict

Single-core throughput on a 512 KiB buffer (the bench.c default; start offsets vary by up to 63 bytes unless --aligned; best of 40 rounds), everything built with gcc -O3 -march=native with no compiler version given. Each new kernel is compared with the fastest prior code on that CPU: dougallj's NEON CRC32 on M1 (77.55 to 85.05 GB/s, same zlib polynomial), the author's crc32_4k_fusion on a Xeon Silver 4214 Cascade Lake (25.32 to 31.55 GB/s CRC-32C), and Chromium zlib's AVX-512 CRC32 on Ice Lake (41.00 to 63.98 GB/s, cross-polynomial) and Sapphire Rapids (81.68 GB/s aligned or 65.20 unaligned, to 97.30 GB/s). An independent Tiger Lake benchmark (clang 23) confirms the win only from about 64 KiB up.

## Use it when

- Checksumming large buffers (tens of KiB to MiB: storage blocks, WAL/log segments, network payloads, file integrity) where CRC throughput per core is the bottleneck.
- CRC-32C (iSCSI/ext4/Btrfs polynomial) on x86-64 with VPCLMULQDQ (Ice Lake, Sapphire Rapids, Zen 4): about 64-97 GB/s single core in the README.
- zlib/gzip/PNG CRC-32 on aarch64 (Apple M1, Ampere Altra), where both scalar crc32 and PMULL paths exist: 85 GB/s on M1, 35.9 GB/s on Altra.
- You want to vendor one dependency-free C file into a C/C++ codebase and already have (or can add) CPUID/HWCAP dispatch, as PostgreSQL and zlib-ng did.
- CRCs with non-standard 32-bit polynomials (crc32k, crc32q or any hex polynomial) that still need PCLMUL-class speed.

## Skip it when

- Small inputs (under about 1-8 KiB). Most fusion kernels only enter the SIMD loop above a few hundred bytes (384 B for v4s5x3) and fall back to a byte/8-byte crc32 loop below that. A third-party Tiger Lake benchmark has MariaDB's AVX-512 CRC32C ahead of every corsix variant from 256 B to 8 KiB.
- You need a ready-made library with runtime CPU detection, a build system, packaging or an API beyond one function; none is provided.
- x86 zlib-polynomial CRC-32 where you expected the headline numbers: x86 has no scalar crc32 instruction for that polynomial, so the fusion kernels (all CRC-32C on x86) do not apply and only vector-only variants remain (e.g. 47.3 GB/s on Ice Lake).
- Portability beyond x86-64/aarch64 little-endian with GCC/Clang: the generated NEON code uses GNU inline asm (MSVC ARM64 cannot compile it), and big-endian or 32-bit targets are not documented.
- CRC-16/CRC-64 or reflected/non-reflected variants other than the bit-reflected 32-bit form; only 32-bit CRCs are generated.

## How it is fast

It folds 16- or 64-byte vector accumulators with carry-less multiplication (PCLMULQDQ/VPCLMULQDQ on x86, PMULL on aarch64), as in Intel's CRC folding whitepaper. It uses three-way XOR (VPTERNLOGQ or EOR3) so each fold step needs fewer uops. The key idea is 'fusion' (from the author's crc32_4k_fusion post): while the vector folds process one part of the buffer, several independent scalar crc32 instruction streams process other parts on a different execution port, and the partial CRCs are merged with x^n mod P shift constants. Accumulator counts and load unrolling are tuned per microarchitecture so that enough streams are in flight to hide the latencies of the pmull+eor chain (6-7 cycles on M1 per the README) and of crc32 (3 cycles on Intel).

## Compared with alternatives

Pick it over crc-fast or crc32fast when you are in C/C++, want the highest large-buffer CRC-32C/CRC-32 throughput on a known CPU, and are happy to vendor one generated file and write your own dispatch. crc-fast gives packaged runtime dispatch and CRC-16/64 variants, and crc32fast is the idiomatic Rust choice. Pick it over htot/crc32c on any post-2017 CPU: its kernels are the successors to the Intel crc32+pclmul 3-way approach that htot ports, and they add VPCLMULQDQ/AVX-512 and aarch64.

## Integration

| | |
|---|---|
| **Form** | source-drop (one generated .c file per ISA/polynomial/algorithm) |
| **Dependencies** | none (compiler intrinsics headers only; the `-i none` target emits lookup tables instead) |
| **Minimum toolchain** | Not documented. Built and benchmarked with gcc -O3 -march=native (version not stated). Needs GCC/Clang-style intrinsics and GNU inline asm for NEON. AVX-512 output uses _mm512_zextsi128_si512, which older compilers may lack. |
| **Platforms** | x86-64 (SSE4.2+PCLMULQDQ minimum; AVX-512F/VL; AVX-512+VPCLMULQDQ on Ice Lake+/Zen 4), aarch64 (crypto+crc; EOR3 variants need armv8.2-a+sha3), and a portable table-driven `-i none` fallback |
| **Thread safety** | Not documented. Generated functions are pure (inputs plus const tables, no mutable globals), so concurrent calls are safe by construction. |
| **Drop-in for the baseline** | partial — same (crc, buf, len) signature and pre/post inversion as zlib crc32(), but the function is named crc32_impl, one file covers only one polynomial and ISA, and there is no runtime CPU dispatch, so you must rename it and add feature checks. |

## Gotchas

- The checked-in AVX-512 VPCLMULQDQ sample files (v4s5x3, v3s1_s3), which are the headline Ice Lake and Sapphire Rapids kernels, still use _mm512_castsi128_si512. PR #1 (from PostgreSQL developers) fixed only generate.c: the undefined upper bits gave wrong CRCs with clang 18/19 at -O0. Regenerate rather than copying the samples.
- The best algorithm string differs per microarchitecture (v9s3x4e Cascade Lake, v4s5x3 Ice Lake, v3s1_s3 Sapphire Rapids, v1s3x3 Rome, v1s4x2 Milan, v3s2x4 Genoa). A kernel tuned for one CPU can be well off the pace on another, so run `make sweep`/autobench on your target.
- The Ice Lake '56% faster' headline compares a CRC-32C kernel against Chromium's zlib-polynomial CRC-32. The same-polynomial generated equivalent is 47.31 GB/s against Chromium's 41.00.
- Sapphire Rapids pays about 20% for unaligned 64-byte loads. The generated code aligns the pointer to 64 bytes with scalar crc32 steps first, but hand-edited copies must keep that prologue.

## Known shortcomings

- Speedups are per-CPU against different baselines (Apple M1 vs dougallj's kernel; Ice Lake/Sapphire Rapids vs Chromium zlib CRC32), so no single headline ratio applies.
- A code generator plus sample kernels, not a library: one `crc32_impl` per build, no runtime CPU dispatch, and the best algorithm string differs per microarchitecture. The checked-in AVX-512 VPCLMULQDQ samples (the headline Ice Lake/SPR kernels) still use `_mm512_castsi128_si512`, giving wrong CRCs on clang 18/19 at -O0 (PR #1 fixed generate.c only; regenerate them). Loses on small buffers: a third-party Tiger Lake run has MariaDB's AVX-512 code ahead from 256 B to 8 KiB; wins only from \~64 KiB. The Ice Lake 56% compares CRC32C against zlib-polynomial CRC32 (same polynomial: 47.31 vs 41.00). Adopted by PostgreSQL and zlib-ng.

## Caveats and trade-offs

Baselines are prior state-of-the-art SIMD code (Chromium zlib vectorized CRC32, dougallj, the author's crc32_4k), not naive table-driven CRC32. On Ice Lake and Sapphire Rapids the headline pits Chromium's CRC32 (zlib polynomial) against the new CRC32C kernel. The Sapphire Rapids baseline uses Chromium with aligned inputs; unaligned it is 65.20 GB/s. The repo is a code generator plus sample outputs, not a packaged library.

Code-generator based (terse syntax -&gt; generate.c produces per-architecture C); some variants need very recent CPU extensions (VPCLMULQDQ, SHA3/EOR3)

## Maintenance

Small and low-churn: 6 commits, the last on 2025-11-27 adding the zlib license. Still counted as active, and adopted downstream by PostgreSQL (AVX-512 CRC32C path) and zlib-ng (ARMv8 PMULL+EOR3 CRC32, merged Dec 2025). MIT-or-zlib licensed; the generated output is trivial to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** The README benchmarks the new kernels head to head against Chromium's zlib crc32.c and crc32_simd.c, which are vendored in third_party/, plus dougallj's and corsix's earlier crc32c_4k code. It gives exact reproduce commands for bench.c and autobench.c, the Makefile and third_party/Makefile build everything with gcc -O3 -march=native, and each CPU is identified by a /proc/cpuinfo dump. The only gap is that the compiler version is not stated.
- **Verifier notes:** Tier A is confirmed. The last commit (2025-11-27) is within 12 months, so it counts as active, not stale. GitHub reports the license as NOASSERTION, but LICENSE.md offers a choice of MIT or zlib, so 'MIT OR Zlib' is correct.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `maintenance_status`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/corsix/fast-crc32#readme>
  - <https://github.com/corsix/fast-crc32>
  - <https://github.com/corsix/fast-crc32/blob/main/Makefile>
  - <https://github.com/corsix/fast-crc32/blob/main/third_party/Makefile>
  - <https://github.com/corsix/fast-crc32/blob/main/LICENSE.md>
- **Sources the enricher read:**
  - <https://github.com/corsix/fast-crc32>
  - <https://github.com/corsix/fast-crc32#readme>
  - <https://github.com/corsix/fast-crc32/blob/main/Makefile>
  - <https://github.com/corsix/fast-crc32/blob/main/third_party/Makefile>
  - <https://github.com/corsix/fast-crc32/blob/main/LICENSE.md>
  - <https://github.com/corsix/fast-crc32/blob/main/generate.c>
  - <https://github.com/corsix/fast-crc32/blob/main/bench.c>
  - <https://github.com/corsix/fast-crc32/blob/main/autobench.c>
  - <https://github.com/corsix/fast-crc32/blob/main/sample_avx512_vpclmulqdq_crc32c_v4s5x3.c>
  - <https://github.com/corsix/fast-crc32/blob/main/sample_avx512_vpclmulqdq_crc32c_v3s1_s3.c>
  - <https://github.com/corsix/fast-crc32/blob/main/sample_avx512_crc32c_v9s3x4e.c>
  - <https://github.com/corsix/fast-crc32/blob/main/sample_neon_crc32_v3s4x2e_v2.c>
  - <https://github.com/corsix/fast-crc32/blob/main/sample_neon_eor3_crc32_v9s3x2e_s3.c>
  - <https://github.com/corsix/fast-crc32/commits/main>
  - <https://github.com/corsix/fast-crc32/pull/1>
  - <https://github.com/corsix/fast-crc32/issues/2>
  - <https://github.com/corsix/fast-crc32/issues/3>
  - <https://github.com/zlib-ng/zlib-ng/pull/2023>
  - <https://raw.githubusercontent.com/postgres/postgres/master/src/port/pg_crc32c_sse42.c>
  - <https://www.corsix.org/content/fast-crc32c-4k>
  - <https://github.com/chirizxc/crc32c-benchmark>
  - <https://hn.algolia.com/api/v1/search?query=corsix%20crc32&tags=story>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/corsix/fast-crc32`) · [data/wave7/enrich/raw/github_com_corsix_fast_crc32.json](../../../data/wave7/enrich/raw/github_com_corsix_fast_crc32.json) (enrichment confidence 0.85)

</details>
