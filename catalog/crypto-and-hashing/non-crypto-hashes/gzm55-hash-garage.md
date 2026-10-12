# NMHASH (NMHASH32X)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Non-cryptographic hashes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `BSD-2-Clause` · 🟡 stale

> Header-only 32-bit seeded C hash built on 16-bit SIMD multiplies; about 2x XXH64 bulk throughput with AVX2, weak SMHasher3 quality.

| | |
|---|---|
| **Beats** | xxHash64 |
| **Claimed result** | SMHasher3 (AVX2 build of NMHASH): 25.44 GiB/s vs 13.02 GiB/s for XXH-64 and 15.52 GiB/s for CityHash-64 in the 262144-byte bulk test (raw/NMHASH.txt, raw/XXH-64.txt, raw/CityHash-64.txt). The summary table gives 7.71 vs 3.99 bytes/cycle. That is \~95% faster than xxHash64 and \~64% faster than CityHash64. rurban/smhasher shows a much smaller gap: nmhash32 at 12676.08 MiB/s and nmhash32x at 13072.64 MiB/s vs 11176.72 MiB/s for xxHash64, \~13-17% (derived from page data). |
| **Workload** | SMHasher3 bulk speed test: 262144-byte keys, averaged over byte alignments 0-7, AVX2 build |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 3950X, boost disabled, pinned to 3500 MHz (SMHasher3 README Performance section). Raw result files report speeds '@ 3.5 ghz'. |
| **Compiler and flags** | Not stated for the published results, which were generated with SMHasher3 20251015/20251112/20260827 releases. The README's 'gcc 9.3' refers only to its older runtime-comparison section (SMHasher3 beta1). |
| **Adoption** | 7 stars (gzm55/hash-garage collection); NMHASH itself is also bundled directly inside rurban/smhasher and fwojcik/smhasher3 |
| **Last commit** | 2024-12-15 |
| **Links** | [repository](https://github.com/gzm55/hash-garage) · [benchmark](https://github.com/fwojcik/smhasher3/blob/main/results/README.md) |

## Verdict

SMHasher3's 262,144-byte bulk test on a Ryzen 9 3950X pinned at 3.5 GHz measured the AVX2 build of NMHASH32 v2 at 25.44 GiB/s (7.81 bytes/cycle; NMHASH32X 25.50 GiB/s) against 13.02 GiB/s for XXH64, about 1.95x; the compiler and flags are not stated. rurban/smhasher's older v1 run shows only 12,676 vs 11,177 MiB/s, about 13%.

## Use it when

- You need a seeded 32-bit hash over large buffers (256 B and up) on x86-64 and can build with -mavx2 or AVX-512BW. SMHasher3 measures about 7.8 bytes/cycle: roughly 2x XXH64 (3.99) and 3.9x XXH32 (2.00), the same-width baseline.
- Short keys where 32 bits of output is enough: NMHASH32X averages 39.77 cycles/hash on 1-31-byte keys in SMHasher3, against 52.60 for XXH64 and 44.38 for XXH32. NMHASH32 is slower here, at 52.79.
- Targets where 16-bit lane multiplies are cheap but wide multiplies are not. Apart from NMHASH32X's short-key paths, the core uses only 16x16-&gt;16 multiplies plus 32-bit add, xor and shift.
- You want the same hash value on little- and big-endian machines. All loads go through NMH_readLE32/NMH_readLE16 byte-order normalization, and the Fortran stdlib port documents identical results on all architectures.

## Skip it when

- Quality-sensitive uses such as hash tables fed structured keys, sketches or dedup. SMHasher3 marks NMHASH FAIL with 78 of 250 tests failed and NMHASHX with 100 (Sparse, Permutation, TwoBytes, PerlinNoise, SeedBlockOffset and others), against 9 for XXH64. rurban's own nmhash32 log shows a 181x collision excess on PerlinNoise even though its table row lists no problems.
- Anything that needs more than 32 bits, such as fingerprints, content addressing or very large tables. The author confirmed in issue #2 that both output and seed are fixed at 32 bits.
- Non-x86 targets, especially Apple Silicon. There is no NEON path, and the scalar code produced wrong verification values for both variants on macos-14-arm64 in rurban/smhasher CI (issue #294).
- Maximum throughput or small-key latency. In the same SMHasher3 run, XXH3-64 reaches 12.82 bytes/cycle (42.21 GiB/s), MeowHash.32 12.44 and AquaHash 15.84. On 1-31-byte keys wyhash (29.31 cycles) and a5hash (26.91) are much faster, and both fail fewer tests.
- Portable x86 binaries: the SIMD level is fixed at compile time with no runtime CPU dispatch. An -mavx2 build will not run on pre-AVX2 CPUs, and a baseline build gets only 128-bit SSE2 lanes.

## How it is fast

The bulk path keeps 64 lanes of 32-bit accumulators (two 128-byte arrays) and consumes 256 bytes per round. Each round uses only invertible xor/add, xorshift and 16x16-&gt;16 lane multiplies (_mm_mullo_epi16 / _mm256_ / _mm512_ variants), so one AVX2 instruction multiplies 16 lanes; the published speedup pits this vectorized build against a scalar XXH64. SSE2, AVX2 or AVX-512BW code is picked at compile time from predefined macros. The scalar fallback is written breadth-first so GCC can auto-vectorize it (the author puts this at about 80% of the hand-vectorized speed), and short keys take length-bucketed paths (0-4, 5-8, 9-32 and 33-255 bytes) with hash-prospector-style mixers.

## Compared with alternatives

Only when a seeded 32-bit hash built from 16-bit multiplies is a hard requirement on x86 and bulk speed matters more than SMHasher3 quality. Otherwise XXH3 (xxHash) is faster in the same run, wyhash and a5hash are faster on short keys, and SpookyHash (SpookyHash2-32) or MeowHash.32 give 32-bit output while passing every SMHasher3 test.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (stdint.h and string.h, plus x86 intrinsic headers when SSE2/AVX2 is enabled) |
| **Minimum toolchain** | C99, or C++ (pre-C++11 handled via __STDC_CONSTANT_MACROS). Has code paths for GCC, Clang, MSVC, ICC and SDCC; no minimum compiler versions are documented. |
| **Platforms** | Any target via the scalar path (little- or big-endian). Hand-written SIMD exists only for x86/x86-64 (SSE2, AVX2 or AVX-512BW, chosen at compile time); there is no NEON path. |
| **Thread safety** | Not documented. The functions are stateless and read only static const tables, so concurrent calls are safe by construction. |
| **Drop-in for the baseline** | no |

## Gotchas

- Outputs changed between NMH_VERSION 1 and 2 (the NMHASH32 verification value for rurban/smhasher went from 0x0DC5C2DC to 0x12A30553). rurban's published nmhash32 log and the Fortran stdlib port (pinned to commit a8913138) are both v1, so their numbers and hash values do not match the current header. Pin the version if you persist hashes.
- The scalar path type-puns uint32_t accumulators through uint16_t pointers, and SMHasher3 tags the implementation FLAG_IMPL_TYPE_PUNNING. Its uint16_t\*uint16_t compound multiplies promote to signed int and can overflow. PR #3 (Dec 2024) fixed that only in the avalanche function; the scalar 0-8, 9-255 and long-round paths still have it. rurban/smhasher now runs a nmhash32_broken() probe at startup because some compilers (macOS arm64) produce different results.
- For inputs of 256 bytes or more, NMHASH32 and NMHASH32X run the same NMHASH32_long loop and differ only in the final avalanche, so choosing X only speeds up shorter keys. The last round rehashes the final 256 bytes and overlaps the previous block.
- The SIMD path is selected from __AVX512BW__, __AVX2__ or __SSE2__, or from NMH_VECTOR set on the command line. For AVX2 builds the header comment recommends GCC's -mno-avx256-split-unaligned-load/-store flags.

## Known shortcomings

- The 25.44 GiB/s figure is nmhash32, not NMHASH32X, and there is no NMHASH64. SMHasher3 marks both as FAIL (nmhash32 172/250, nmhash32x 150/250 tests passed). rurban margin over xxHash64 is only \~13-17%.
- 32-bit output and 32-bit seed only (by design, issue #2). Scalar path type-puns and has uint16 x uint16 signed-overflow UB; wrong values on macOS arm64 (rurban #294); no NEON; SIMD level fixed at compile time. The rurban table (and the Fortran stdlib port) use v1, not current v2, so the \~13% rurban margin is stale; XXH3 is faster in the same run.

## Caveats and trade-offs

The 25.44 GiB/s figure is NMHASH32 ('nmhash32 v2' [avx2]); NMHASH32X ('nmhash32x v2') measured 25.50 GiB/s. Both are 32-bit-output hashes (there is no NMHASH64), so the xxHash64 comparison crosses output widths. The \~95% margin is an AVX2-vectorized NMHASH against scalar XXH-64. In rurban/smhasher the win shrinks to \~13-17%, and in the same SMHasher3 run NMHASH trails XXH3-64 (42.21 GiB/s) and roughly ties wyhash (23.17 GiB/s). SMHasher3 marks NMHASH as FAIL (172/250 tests passed) and NMHASHX as FAIL (150/250), against XXH-64 at 241/250. The hash-garage README claims both pass rurban/smhasher and demerphq/smhasher. Compile flags are unstated, which caps the tier at B.

32-bit output hash (NMHASH32/NMHASH32X), AVX2 build used for the fastest numbers reported here; scalar path is slower; small/obscure repo with little independent adoption outside the smhasher test suites.

## Maintenance

Stale: the algorithm froze at v2 in June 2021, and the only later commit is a December 2024 UB fix from rurban. The code is BSD-2-Clause, a single 832-line header and easy to vendor, but it is used mainly by hash test suites and by a Fortran stdlib port of v1.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** SMHasher3 is an independent third-party hash suite; its results/README.md table lists NMHASH (7.71 bytes/cycle bulk) next to XXH-64 (3.99), and the raw per-hash files give 25.44 GiB/s (NMHASH.txt) vs 13.02 GiB/s (XXH-64.txt) and 15.52 GiB/s (CityHash-64.txt) at 3.5 GHz. Suite code and CPU are public, but the compile flags (and the compiler used for the current results) are not stated, so it is B, not A.
- **Verifier notes:** The numbers are exact. The original benchmark_url, NMHASH.txt, holds only NMHASH's own numbers, so I repointed it to the SMHasher3 summary table that lists both rows. I also fixed the caveats (NMHASH64 does not exist, NMHASH32 vs 32X numbers) and the misattributed gcc 9.3. Important: SMHasher3 flags heavy quality failures (78 failed tests for NMHASH, 100 for NMHASHX).
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** SMHasher3: nmhash32 25.44 vs XXH-64 13.02 GiB/s bulk.
- **Pages the verifier opened:**
  - <https://github.com/fwojcik/smhasher3/blob/main/results/raw/NMHASH.txt>
  - <https://raw.githubusercontent.com/fwojcik/smhasher3/main/results/raw/NMHASH.txt>
  - <https://raw.githubusercontent.com/fwojcik/smhasher3/main/results/raw/NMHASHX.txt>
  - <https://raw.githubusercontent.com/fwojcik/smhasher3/main/results/raw/XXH-64.txt>
  - <https://raw.githubusercontent.com/fwojcik/smhasher3/main/results/raw/XXH-32.txt>
  - <https://raw.githubusercontent.com/fwojcik/smhasher3/main/results/raw/CityHash-64.txt>
  - <https://raw.githubusercontent.com/fwojcik/smhasher3/main/results/raw/wyhash.txt>
  - <https://raw.githubusercontent.com/fwojcik/smhasher3/main/results/raw/XXH3-64.txt>
  - <https://github.com/fwojcik/smhasher3/blob/main/results/README.md>
  - <https://raw.githubusercontent.com/fwojcik/smhasher3/main/results/README.md>
  - <https://raw.githubusercontent.com/fwojcik/smhasher3/main/README.md>
  - <https://github.com/fwojcik/smhasher3>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/README.md>
  - <https://github.com/gzm55/hash-garage>
- **Sources the enricher read:**
  - <https://github.com/gzm55/hash-garage>
  - <https://github.com/gzm55/hash-garage/blob/master/README.md>
  - <https://github.com/gzm55/hash-garage/blob/master/nmhash.h>
  - <https://github.com/gzm55/hash-garage/commits/master>
  - <https://github.com/gzm55/hash-garage/pull/3>
  - <https://github.com/gzm55/hash-garage/issues/2>
  - <https://github.com/gzm55/hash-garage/blob/a8913138bdb3b7539c202edee30a7f0794bbd835/nmhash.h>
  - <https://raw.githubusercontent.com/fwojcik/smhasher3/main/results/README.md>
  - <https://raw.githubusercontent.com/fwojcik/smhasher3/main/results/raw/NMHASH.txt>
  - <https://raw.githubusercontent.com/fwojcik/smhasher3/main/results/raw/NMHASHX.txt>
  - <https://raw.githubusercontent.com/fwojcik/smhasher3/main/results/raw/XXH-64.txt>
  - <https://raw.githubusercontent.com/fwojcik/smhasher3/main/results/raw/XXH3-64.txt>
  - <https://raw.githubusercontent.com/fwojcik/smhasher3/main/results/raw/wyhash.txt>
  - <https://raw.githubusercontent.com/fwojcik/smhasher3/main/README.md>
  - <https://github.com/fwojcik/smhasher3/blob/main/hashes/nmhash.cpp>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/README.md>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/nmhash32.txt>
  - <https://github.com/rurban/smhasher/blob/master/main.cpp>
  - <https://github.com/rurban/smhasher/blob/master/Hashes.h>
  - <https://github.com/rurban/smhasher/blob/master/Hashes.cpp>
  - <https://github.com/rurban/smhasher/commits/master/Hashes.cpp>
  - <https://github.com/rurban/smhasher/issues/190>
  - <https://github.com/rurban/smhasher/issues/194>
  - <https://github.com/rurban/smhasher/issues/294>
  - <https://github.com/fortran-lang/stdlib/blob/master/doc/specs/stdlib_hash_procedures.md>
  - <https://hn.algolia.com/api/v1/search?query=nmhash>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/gzm55/hash-garage`) · [data/wave7/enrich/raw/github_com_gzm55_hash_garage.json](../../../data/wave7/enrich/raw/github_com_gzm55_hash_garage.json) (enrichment confidence 0.8)

</details>
