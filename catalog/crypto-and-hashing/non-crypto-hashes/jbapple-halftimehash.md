# HalftimeHash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Non-cryptographic hashes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> Keyed almost-universal C++ hash for long strings; \~1.3-1.4x xxh128 on 256 KiB inputs with AVX-512.

| | |
|---|---|
| **Beats** | xxHash (xxh128) |
| **Claimed result** | SMHasher speed test on 256KiB strings on an i7-7800X, in bytes/cycle from the paper's committed plot data (smhasher-speed.txt): HalftimeHash16 16.942 and HalftimeHash24 15.683 vs xxh128 12.162 and xxh3 12.772. That makes them about 1.39x and 1.29x faster than xxh128 (derived from page data). HalftimeHash32 (13.476) is about 1.11x faster; HalftimeHash40 (9.998) is slower than xxh128. The paper's text says the two fastest variants beat every SMHasher-suite hash on 256KiB strings. Against the AU families clhash and UMASH it claims over 50% higher throughput, exceeding 16 bytes/cycle, and typically 55% faster than clhash on strings over 1KB. On the AMD 7R32 (no AVX-512), HalftimeHash with 256-bit blocks beats clmul-based hashing by up to 2x; the 'up to 2x' figure is stated for AMD only, not for both chips. |
| **Workload** | SMHasher bulk speed test on 256KiB strings on an Intel i7-7800X (Skylake-X, AVX-512), plotted against the fastest SMHasher families (clhash, MeowHash128, xxh128, xxh3, t1ha0_aes_avx2, falkhash). Also benchmark.cpp comparisons against clhash and UMASH on 250KB strings and across input sizes, on the i7-7800X and an AMD EC2 c5a.large (7R32, no AVX-512). |
| **Metric** | throughput |
| **Hardware** | Intel i7-7800X (Skylake-X, AVX-512); AMD EC2 c5a.large (7R32, no AVX-512) |
| **Compiler and flags** | Clang++ 11.0.1 on Ubuntu 18.04 (paper). benchmark.cpp (the clhash/UMASH comparison) is built by the repo Makefile with -O3 -march=native -funroll-loops -std=c++14 -DNDEBUG. Build flags for the SMHasher run behind the xxh128 comparison (jbapple/smhasher-1, a fork of rurban/smhasher) are not stated. |
| **Adoption** | 13 stars |
| **Last commit** | 2022-05-28 |
| **Links** | [repository](https://github.com/jbapple/HalftimeHash) · [benchmark](https://github.com/jbapple/HalftimeHash/blob/main/halftime-hash.tex) |

## Verdict

In the WADS 2021 paper's SMHasher speed test on 256 KiB strings on an Intel i7-7800X (AVX-512, Clang++ 11.0.1, SMHasher build flags unstated), HalftimeHash16 reached 16.9 bytes/cycle and HalftimeHash24 15.7, against 12.2 for xxh128 and 12.8 for xxh3 (about 1.39x and 1.29x over xxh128); HalftimeHash40 was slower at 10.0. The repo's own -O3 -march=native harness shows it beating clhash and UMASH only on inputs over about 1.5 KB. On an AMD EPYC 7R32 (no AVX-512), the paper reports up to 2x over clhash and UMASH using 256-bit blocks.

## Use it when

- Hashing long buffers (roughly 1.5 KB to a few MB) where throughput matters: in the repo's i7-7800X data HalftimeHash24 runs about 54 B/ns at 128-560 KB, against about 35 B/ns for clhash and UMASH.
- When you need a keyed hash with a stated collision bound (universe collapsing before a short-input hash, one-time authentication, or DoS-resistant bucketing of large blobs) rather than an unkeyed heuristic hash.
- x86-64 builds you compile with -march=native or an explicit AVX-512/AVX2 target; use Style512 on AVX-512 and Style256 on AVX2-only chips such as AMD Zen 2.
- Targets without fast 64-bit widening multiply, since the design deliberately uses only 32x32-&gt;64-bit products.

## Skip it when

- Short keys and hash-table lookups: in the repo's size sweep HalftimeHash24 is slower than clhash and UMASH below about 1 KB (at 229 bytes, 10.9 B/ns vs 17.6 and 19.1), and every call reads from a large key array.
- arm64 builds: on main the NEON dispatch references undeclared V2Neon/V3Neon/V4Neon, so example.cpp fails to compile with Apple clang 17 (issue #1; the fix in PR #2 is still unmerged).
- Anything relying on the advanced 24-byte functions (advanced::V1&lt;3&gt; to V4&lt;3&gt;): an external audit (issue #3) shows Encode3 lacks its intended code distance, giving about 2^-32 collision probability for a specific message pair instead of about 2^-96.
- When you need streaming/incremental hashing, a portable MSVC build, or runtime CPU dispatch; none are provided.
- When you want an actively maintained dependency: no default-branch commit since 2022-05-28, and open correctness reports have no fixes merged.

## How it is fast

It builds on Nandi's Encode-Hash-Combine (EHC) and the Badger tree hash. Input blocks are expanded with a small erasure code, hashed with NH (32x32-&gt;64-bit multiplies on vector lanes), then combined by multiplying with small integer matrices implemented as shifts and adds, so extra output width costs few extra multiplications. Leaves feed a fanout-8 tree of NH nodes and a final Toeplitz NH plus tabulation step. There are no 64x64-&gt;128 or carryless multiplies, so every step maps onto SSE2/AVX2/AVX-512 _mul_epu32 (and NEON vmull_u32).

## Compared with alternatives

Pick it over UMASH or CLHash when inputs are consistently over about 1.5 KB and you can build for AVX2/AVX-512; those two are faster below about 1 KB and are better maintained. Pick xxHash (XXH3/XXH128) instead when you need a small seed, short-key speed, streaming or broad platform support, not a provable collision bound.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (umash and StronglyUniversalStringHashing submodules are only for the benchmarks) |
| **Minimum toolchain** | C++14 (Makefile uses -std=c++14); paper used Clang++ 11.0.1, repo also has GCC 10 result logs; relies on GCC/Clang vector-subscript extensions and #pragma GCC unroll |
| **Platforms** | x86-64 (SSE2, AVX2 or AVX-512 selected at compile time) plus a scalar fallback; arm64 NEON path currently fails to compile on main |
| **Thread safety** | Not documented; the functions keep no state beyond a caller-owned const key array, so concurrent calls look safe |
| **Drop-in for the baseline** | no |

## Gotchas

- You must generate and keep about 69 KiB of random key material (kEntropyBytesNeeded). The example seeds it from a default-constructed mt19937_64, which is fixed and public; use a real random source if you need the collision guarantee.
- The ISA is picked at compile time only; there is no runtime dispatch. Each Style function fixes its block width, so Style512 still works on AVX2 or SSE2 (emulated with repeated blocks) and gives the same outputs, only more slowly.
- TabulateAfter indexes table[8\*(i+1)] through a reference declared [1+width][256]. That is out-of-bounds by the C++ type rules, and UBSan flags it on a single Style64 call (issue #3), even though the tested builds compute the intended addresses.
- The paper's headline bound (more than 83 bits for HalftimeHash24) rests on a proof that issue #3 says needs repair. The public Style wrappers were separately certified at a 63-bit bound, with input-length caps of about 2.76 GB x 1/2/4/8 for Style64/128/256/512.

## Known shortcomings

- 'Up to 2x' holds on AMD only; SMHasher shows HH16/HH24 \~1.3-1.4x over xxh128 (16.94/15.68 vs 12.16 bytes/cycle) and HH40 slower; flags for the xxh128 run unstated. Main branch untouched since 2022-05-28 (a supercop branch was updated 2025-03-08). Long-input hash: needs a large random key and is not suited to short keys.
- Wins only above \~1.5 KB (clhash/UMASH are faster below \~1 KB); keyed hash needs a \~69 KiB caller-supplied key; one-shot only. arm64 build broken on main (undeclared V2Neon/V3Neon/V4Neon, #1; fix PR #2 unmerged). A Sept 2026 audit (#3) found the advanced 24-byte functions collide at \~2^-32 rather than the claimed \~2^-96 (paper proof needs repair; public Style wrappers certified at 63 bits) and an out-of-bounds index in TabulateAfter.

## Caveats and trade-offs

The xxh128 comparison comes from one SMHasher speed run on one Intel CPU, with unstated build flags; numbers exist only as plot data (smhasher-speed.txt) behind a figure. Only the two fastest variants (HalftimeHash16/24) clearly beat xxh128; HalftimeHash40 is slower. The AMD 'up to 2x' result is against clhash/UMASH, not xxHash. The default branch has not been committed to since 2022-05-28; the author's only later activity is a 2025-03-08 commit on the non-default 'supercop' branch. Few stars.

Header-only C++ almost-universal (AU) hash aimed at long-string hashing; wins shown are for 250-256KiB-class strings, not short-key hash-table lookups where xxHash/wyhash are typically used; AU construction needs larger per-instance keyed parameters than a plain xxHash seed.

## Maintenance

No commits on main since 2022-05-28; the author replied on the September 2026 audit issues but merged no fixes. It is Apache-2.0 and about 1,200 lines in one header, so vendoring is easy, but apply the NEON dispatch fix (PR #2) yourself and avoid the advanced 24-byte functions.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now B.
- **Tier reason:** The xxh128 win comes from the SMHasher speed test in a peer-reviewed paper (arXiv 2104.08865, published at WADS 2021). The paper states the compiler (Clang++ 11.0.1) and CPU (i7-7800X), but not the build flags for that SMHasher run (jbapple/smhasher-1 fork), so it falls short of A. The repo's A-grade harness (benchmark.cpp, Makefile -O3 -march=native) covers only clhash and UMASH, not xxh128.
- **Verifier notes:** This is a real, peer-reviewed (WADS 2021) long-string hash with a genuine win over xxh128. The record's claim that no numbers exist is wrong: smhasher-speed.txt holds the figure data, and I added the derived ratios. I set last_commit from the default branch as the rules require; if non-default branches count, the 2025-03-08 supercop commit would make it 'stale' instead.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `last_commit`, `maintenance_status`, `caveats`
- **Shortcomings recorded by:** HalftimeHash smhasher-speed.txt: HH16 16.94, HH24 15.68 vs xxh128 12.16 bytes/cycle.
- **Pages the verifier opened:**
  - <https://github.com/jbapple/HalftimeHash>
  - <https://raw.githubusercontent.com/jbapple/HalftimeHash/main/halftime-hash.tex>
  - <https://raw.githubusercontent.com/jbapple/HalftimeHash/main/README.md>
  - <https://raw.githubusercontent.com/jbapple/HalftimeHash/main/smhasher-speed.txt>
  - <https://raw.githubusercontent.com/jbapple/HalftimeHash/main/plot.gnu>
  - <https://raw.githubusercontent.com/jbapple/HalftimeHash/main/Makefile>
  - <https://raw.githubusercontent.com/jbapple/HalftimeHash/main/benchmark.cpp>
  - <https://raw.githubusercontent.com/jbapple/HalftimeHash/main/cloud-benchmark.sh>
  - <https://raw.githubusercontent.com/jbapple/HalftimeHash/main/.gitmodules>
  - <https://raw.githubusercontent.com/jbapple/HalftimeHash/main/halftime-hash.bib>
  - <http://export.arxiv.org/api/query?search_query=ti:HalftimeHash&max_results=5>
  - <https://arxiv.org/abs/2104.08865>
  - <https://github.com/jbapple/smhasher-1>
- **Sources the enricher read:**
  - <https://github.com/jbapple/HalftimeHash>
  - <https://github.com/jbapple/HalftimeHash/blob/main/README.md>
  - <https://github.com/jbapple/HalftimeHash/blob/main/halftime-hash.hpp>
  - <https://github.com/jbapple/HalftimeHash/blob/main/halftime-hash.h>
  - <https://github.com/jbapple/HalftimeHash/blob/main/halftime-hash.cpp>
  - <https://github.com/jbapple/HalftimeHash/blob/main/example.cpp>
  - <https://github.com/jbapple/HalftimeHash/blob/main/Makefile>
  - <https://github.com/jbapple/HalftimeHash/blob/main/smhasher-speed.txt>
  - <https://github.com/jbapple/HalftimeHash/blob/main/.gitmodules>
  - <https://github.com/jbapple/HalftimeHash/blob/main/deny-list.txt>
  - <https://github.com/jbapple/HalftimeHash/blob/main/halftime-hash.tex>
  - <https://github.com/jbapple/HalftimeHash/blob/main/plot.gnu>
  - <https://github.com/jbapple/HalftimeHash/blob/main/adu-full-001.txt>
  - <https://github.com/jbapple/HalftimeHash/issues/1>
  - <https://github.com/jbapple/HalftimeHash/issues/3>
  - <https://github.com/jbapple/HalftimeHash/pull/2>
  - <https://github.com/jbapple/HalftimeHash/commits/main>
  - <https://github.com/jbapple/HalftimeHash/branches>
  - <https://thomasahle.com/blog/adversarial-examples-for-hashes/>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/jbapple/halftimehash`) · [data/wave7/enrich/raw/github_com_jbapple_halftimehash.json](../../../data/wave7/enrich/raw/github_com_jbapple_halftimehash.json) (enrichment confidence 0.8)

</details>
