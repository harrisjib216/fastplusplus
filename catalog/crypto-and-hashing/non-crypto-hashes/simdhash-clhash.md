# CLHash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Non-cryptographic hashes](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `Apache-2.0` · 🟢 active

> Keyed 64-bit universal string hash built on carry-less multiply; about 40% faster than CityHash64 on inputs over 64 bytes.

| | |
|---|---|
| **Beats** | CityHash (CityHash64WithSeed, the paper's C port of v1.1.1); secondarily xxHash (xxh3) via SMHasher |
| **Claimed result** | Paper Table 5 (i7-4770): 0.16 vs 0.23 cycles/byte for CityHash on 4 kB inputs (authors: 'almost 45% faster'; about 40% faster on inputs over 64 B, similar speed at 32 B or less) and 0.45 vs 0.48 cycles/byte at 64 B. Separately, the rurban SMHasher bulk test (262144-byte keys, Ryzen 5 3350G) gives 22932.36 vs 20853.74 MiB/s for xxh3, about 10% faster (derived from page data). |
| **Workload** | Paper: hashing random inputs from 8 B to 8 kB (Table 5 reports 64 B and 4 kB), timed with rdtsc over 40 million input words per length, random-bit generation excluded. SMHasher: bulk speed test with 262144-byte keys, run with many hash functions on the same machine and build in rurban/smhasher. |
| **Metric** | throughput |
| **Hardware** | Paper: Intel i7-4770 (Haswell) at 3.4 GHz, 32 GB DDR3-1600, Turbo Boost and hyper-threading disabled. SMHasher: AMD Ryzen 5 3350G 3.6GHz (default table). |
| **Compiler and flags** | Paper: GNU GCC 4.8 with -O2 (benchmark code in lemire/StronglyUniversalStringHashing). SMHasher: CMake Release build with -march=native -std=c++11 per rurban/smhasher CMakeLists.txt; compiler version not stated. |
| **Adoption** | 302 stars; based on Lemire & Kaser, J. Cryptographic Engineering 6(3), 2016 |
| **Last commit** | 2026-05-23 |
| **Links** | [repository](https://github.com/simdhash/clhash) · [benchmark](https://arxiv.org/pdf/1503.03465) |

## Verdict

In Lemire & Kaser (J. Cryptographic Engineering 2016), built with GCC 4.8 -O2 on a 3.4 GHz i7-4770 Haswell with Turbo Boost off, the 2015 research code took 0.16 cycles/byte vs 0.23 for the authors' C port of CityHash64WithSeed 1.1.1 on 4 kB inputs, and 0.45 vs 0.48 at 64 B. SMHasher3 (hardware not stated) gives CLHash 7.36 vs CityHash-64's 4.75 bytes/cycle in bulk. rurban SMHasher (Ryzen 5 3350G, compiler not stated) gives 22932.36 vs 20853.74 MiB/s for xxh3, but 67.22 vs 29.46 cycles/hash on small keys.

## Use it when

- Bulk hashing of inputs from hundreds of bytes to many KB (documents, packets, file blocks), where cycles per byte matter more than per-call latency.
- Replacing CityHash64 on Haswell-or-newer x64 for inputs over 64 bytes (paper: about 40% faster there, parity at 32 bytes or less).
- You need a provable collision bound from a secret random key, not just a clean SMHasher run, e.g. hash tables or sketches fed by untrusted input that cannot observe hash values.
- Mixed x86-64 and AArch64 fleets that need identical hashes: the README and known-answer tests guarantee bit-for-bit equal output on both.

## Skip it when

- Short keys: rurban SMHasher measures 67.22 cycles/hash on 1-31 byte keys vs 29.46 for xxh3; issue #6 found it slower than std::hash below about 192 bytes, and lengths that are not a multiple of 8 are slower still (issue #3).
- When you need every output bit to behave randomly (e.g. using low bits directly as a table index): for short inputs the default build is linear in the input. SMHasher3 fails it on 186 of 250 tests (avalanche, BIC, Sparse, Text, Seed and more), and 23 even with CLHASH_BITMIX. rurban's BITMIX log also shows mass collisions in the Sparse, Permutation, TwoBytes and PerlinNoise keysets.
- Hardware without carry-less multiply: builds only on x86 with PCLMULQDQ+SSE4.2 or AArch64 with the PMULL crypto extension; POWER and other targets hit an #error.
- Streaming or multi-field hashing: there is no incremental API (issue #3, open since 2016), so fields must be concatenated first.
- Pure bulk speed: the xxh3 win does not replicate. SMHasher3 measures 7.36 bytes/cycle vs XXH3-64's 12.82, and on rurban's table gxhash64 (48919.73 MiB/s) and falkhash (52401.48) more than double CLHash's 22932.36.

## How it is fast

The core is CLNH: each pair of 64-bit input words is XORed with key words and multiplied with a single PCLMULQDQ (PMULL on ARM), and the 128-bit products are XOR-accumulated without any reduction, because GF(2) arithmetic has no carries. Inputs over 1 KB are cut into 1 KB blocks whose CLNH results are chained by Horner's rule in GF(2^127), using a cheap 'lazy' reduction modulo 2^128+4+2 (two shifts and XORs). A final PSHUFB-table reduction modulo x^64+x^4+x^3+x+1 produces the 64-bit output. The paper puts the Haswell bound at one CLMUL per 16 bytes (0.125 cycles/byte) and measures 0.16.

## Compared with alternatives

Pick CLHash over xxHash (XXH3), wyhash or rapidhash only when you want a proven universality bound from a random key, not for speed. XXH3 matches or beats it (rurban: CLHash about 10% faster in bulk; SMHasher3: XXH3-64 about 1.7x faster in bulk and 30.69 vs 48.19 cycles on 1-32 B keys), and gxhash or falkhash are over 2x faster in bulk.

## Integration

| | |
|---|---|
| **Form** | source-drop (one .c + one .h) or static lib (CMake, find_package(clhash)) |
| **Dependencies** | none (C standard library only) |
| **Minimum toolchain** | C99 compiler (C++11 for the clhasher wrapper; CMake 3.16 for the CMake build); GCC/Clang need -msse4.2 -mpclmul on x86 or -march=armv8-a+crypto on ARM; MSVC via the CMake Visual Studio generator |
| **Platforms** | x86-64 with PCLMULQDQ + SSE4.2 (Haswell-class or newer for full speed); AArch64 with PMULL (Apple Silicon, Graviton, modern Cortex-A); CI covers Linux x64/ARM64, macOS ARM64, Windows MSVC |
| **Thread safety** | Not documented. clhash() only reads the key and input, so one shared key appears safe for concurrent calls (inferred from source). |
| **Drop-in for the baseline** | partial — same bytes-in, 64-bit-out shape as CityHash64WithSeed, but you must build and keep a 1064-byte key via get_random_key_for_clhash() instead of passing a 64-bit seed, and hash values differ |

## Gotchas

- Key handling: get_random_key_for_clhash() expands two seeds with xorshift128+, which is not a CSPRNG, and the source says the seeds must be non-zero. clhash() uses aligned 16-byte loads on the key, so a hand-built key must be 16-byte aligned, and the alignment check is only an assert().
- The empty input hashes to 0 under every key (the known-answer vector in tests/unit.c; both the accumulator and the length term are zero).
- The C++ clhasher frees its malloc'd key in its destructor but defines no copy constructor or assignment, so any copy (including copying a container that stores it) double-frees.
- CLHASH_BITMIX (Murmur fmix64 finalizer) changes hash values and is applied only on the &lt;=1024-byte path; inputs over 1 KB skip it.

## Known shortcomings

- Peer-reviewed win is over CityHash (0.16 vs 0.23 cycles/byte, GCC 4.8, i7-4770); against xxh3 the lead is only \~10% in SMHasher and it is \~2.3x slower on small keys. Needs CLMUL (PCLMULQDQ).
- Lead over xxh3 does not hold in SMHasher3 (XXH3-64 \~1.7x faster: 12.82 vs 7.36 bytes/cycle) and small keys are 2-3x slower. Weak quality: default build fails 186/250 SMHasher3 tests (BITMIX build 23, and BITMIX only applies up to 1 KB). C++ clhasher lacks a copy constructor (double free); empty input hashes to 0 for every key; key must be 16-byte aligned (assert only); no streaming (#3). The CityHash comparison is 2015 research code; the library was revived as v1.0.0 in May 2026.

## Caveats and trade-offs

The paper-era CLHASH code (StronglyUniversalStringHashing, 2015) is not the current simdhash/clhash library, and the CityHash baseline was the authors' own C port of CityHash 1.1.1 rather than upstream C++. Against xxh3, CLHash wins only on bulk data (about 10% in SMHasher) and is about 2.3x slower on small keys (67.22 vs 29.46 cycles/hash). SMHasher flags a PerlinNoise quality issue, and the paper reports CLHASH fails the SMHasher avalanche test. It is x64 (PCLMULQDQ+SSE4.2) or ARM PMULL only. The README's own claim is '20 to 40x faster' than a naive Java-like polynomial hash, plus about 0.1 cycles/byte on Skylake. The repo was transferred from lemire/clhash (which redirects) to the simdhash org.

Requires PCLMULQDQ+SSE4.2 (x64 Haswell or newer) or ARM PMULL crypto extension; fails to build or is slow on unsupported hardware; CLHASH_BITMIX build flag needed to pass SMHasher's avalanche test.

## Maintenance

Revived in May 2026 (tagged v1.0.0) after years of near-dormancy, adding an ARM PMULL port, CMake packaging and multi-OS CI; Apache-2.0, and only two files to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded from B to A on stronger evidence. The peer-reviewed paper (Lemire & Kaser, J. Cryptographic Engineering 6(3), DOI 10.1007/s13389-015-0110-5, arXiv 1503.03465) states GCC 4.8 -O2 and an Intel i7-4770 at 3.4 GHz, and its public artifact repo (lemire/StronglyUniversalStringHashing, benchmark/benchmark.cc and benchmark/variablelengthbenchmark.cc with the include/City/City.c port) benchmarks CLHASH against CityHash64WithSeed: 0.16 vs 0.23 cycles/byte at 4 kB. The xxh3 margin in the record comes only from the rurban SMHasher table, where the row numbers match exactly (22932.36 vs 20853.74 MiB/s); that part stays B-tier, since the compiler version is not stated there.
- **Verifier notes:** SMHasher row numbers and all metadata check out (Apache-2.0, not fork/archived, 302 stars, last commit 2026-05-23). The tier was upgraded to A because the peer-reviewed paper plus its artifact repo meet every A criterion against CityHash; the xxh3 comparison is B-tier only. The orchestrator may want to present CityHash as the primary baseline.
- **Fields the verifier corrected:** `baseline`, `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Shortcomings recorded by:** Lemire & Kaser (peer-reviewed): CLHash 0.16 vs CityHash 0.23 cycles/byte on long strings (i7-4770, GCC 4.8 -O2).; SMHasher3: CLHash 7.36 vs XXH3-64 12.82 bytes/cycle bulk.
- **Pages the verifier opened:**
  - <https://github.com/rurban/smhasher/blob/master/README.md>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/README.md>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/clhash.txt>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/xxh3.txt>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/CMakeLists.txt>
  - <https://github.com/simdhash/clhash>
  - <https://github.com/lemire/clhash>
  - <https://arxiv.org/pdf/1503.03465>
  - <https://github.com/lemire/StronglyUniversalStringHashing>
  - <https://api.crossref.org/works?query.bibliographic=Faster+64-bit+universal+hashing+using+carry-less+multiplications&rows=2>
- **Sources the enricher read:**
  - <https://github.com/simdhash/clhash>
  - <https://github.com/simdhash/clhash/blob/master/README.md>
  - <https://github.com/simdhash/clhash/blob/master/include/clhash.h>
  - <https://github.com/simdhash/clhash/blob/master/src/clhash.c>
  - <https://github.com/simdhash/clhash/blob/master/CMakeLists.txt>
  - <https://github.com/simdhash/clhash/blob/master/Makefile>
  - <https://github.com/simdhash/clhash/blob/master/.github/workflows/ci.yml>
  - <https://github.com/simdhash/clhash/blob/master/benchmarks/benchmark.c>
  - <https://github.com/simdhash/clhash/blob/master/tests/unit.c>
  - <https://github.com/simdhash/clhash/commits/master>
  - <https://github.com/simdhash/clhash/issues?q=is%3Aissue>
  - <https://github.com/simdhash/clhash/pulls?q=is%3Apr>
  - <https://github.com/simdhash/clhash/issues/6>
  - <https://github.com/simdhash/clhash/issues/3>
  - <https://github.com/simdhash/clhash/issues/5>
  - <https://github.com/simdhash/clhash/tags>
  - <https://github.com/lemire/clhash>
  - <https://arxiv.org/pdf/1503.03465>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/README.md>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/clhash.txt>
  - <https://github.com/rurban/smhasher/commits/master/doc/clhash.txt>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/clhash.c>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/clhash.h>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/Hashes.h>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/Hashes.cpp>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/README.md>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/raw/CLhash.txt>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/raw/CLhash.bitmix.txt>
  - https://hn.algolia.com/api/v1/search?query=clhash&tags=(story,comment)
  - <https://hn.algolia.com/api/v1/items/29042568>
  - <https://hn.algolia.com/api/v1/items/17770155>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/simdhash/clhash`) · [data/wave7/enrich/raw/github_com_simdhash_clhash.json](../../../data/wave7/enrich/raw/github_com_simdhash_clhash.json) (enrichment confidence 0.8)

</details>
