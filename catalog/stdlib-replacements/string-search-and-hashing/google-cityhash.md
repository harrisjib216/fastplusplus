# CityHash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [String search and hashing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Non-cryptographic 64/128-bit string hash family beating Murmur2/Murmur3F, \~1.7-2.5x faster at 64 bytes.

| | |
|---|---|
| **Beats** | MurmurHash2/MurmurHash3 (Murmur2, Murmur3F, Murmur3A) — widely-used non-cryptographic hash functions used in place of std::hash |
| **Claimed result** | CityHash64 v1.0.3: 7ns for 1 byte vs Murmur2's 6ns (Murmur2 slightly faster here) but 9ns for 64 bytes vs Murmur2's 15ns and Murmur3F's 23ns (roughly 1.7x-2.5x faster at 64 bytes, derived from page data). CityHashCrc256 peaks at about 5-5.5 bytes/cycle on long strings vs the fastest Murmur variant (Murmur3F) at about 2.4 bytes/cycle (roughly 2x-2.3x faster, derived from page data). |
| **Workload** | Hashing short strings (1, 8, 64 bytes) and long strings, on a single core of a 2.67GHz Intel Xeon X5550. |
| **Metric** | throughput |
| **Hardware** | Single core, 2.67GHz Intel Xeon X5550 |
| **Adoption** | 1.2k stars; historically used in many hash-table/database implementations before Google's own successors (FarmHash, Abseil's hash) superseded it |
| **Last commit** | 2022-07-19 |
| **Links** | [repository](https://github.com/google/cityhash) · [benchmark](https://github.com/google/cityhash/blob/master/README) |

## Verdict

Google's own README (MIT, \~2011-2013 numbers) reports CityHash64 v1.0.3 vs Murmur2/Murmur3F on a single core of a 2.67GHz Xeon X5550: 9ns vs 15ns/23ns at 64 bytes (\~1.7x-2.5x faster), and CityHashCrc256 at 5-5.5 bytes/cycle vs Murmur3F's 2.4 bytes/cycle on long strings (\~2.1x-2.3x faster); compiler and flags used for these specific numbers are not stated.

## Use it when

- Fixed, fully-buffered byte strings (not streamed) used as hash-table keys, especially short strings in the 1-64 byte range
- x86-64 targets with SSE4.2 available, where CityHashCrc128/256 can use the CRC32 instruction for long-string throughput
- Codebases that want to vendor a tiny, frozen source drop (city.cc/city.h/citycrc.h) rather than add a package-manager dependency
- Need an MIT-licensed implementation with a stable, unchanging API (no upstream churn since 2013)
- Non-adversarial input, or input always hashed with a caller-supplied random seed via the \*WithSeed variants

## Skip it when

- Need to hash data arriving in chunks/streams — no incremental API exists
- Want the fastest available long-string throughput on modern hardware — newer SIMD-tuned hashes (xxh3, rapidhash, komihash) beat it and are actively maintained
- Non-x86-64 or no-SSE4.2 platform and you wanted the CRC-based variants (CityHashCrc128/256 hard-require _mm_crc32_u64)
- Untrusted/adversarial keys going into a hash table without supplying a random seed — CVE-2012-6051 hash-flooding DoS applies to unseeded CityHash
- Want a maintained project — repo is archived by Google, last real release was v1.1.1 in June 2013

## How it is fast

Short inputs (&lt;=4, &lt;=8, &lt;=16, &lt;=32, &lt;=64 bytes) each get a dedicated fast path using register-width multiply/rotate mixing tuned to that length bucket, so most hash-table-key-sized strings finish in a handful of instructions. For long strings, CityHashCrc128/256 layer that same multiply-rotate mixing on top of the hardware CRC32 instruction (_mm_crc32_u64) as a cheap mixing primitive, reaching about 5-5.5 bytes/cycle versus \~2.4 bytes/cycle for pure-software Murmur3F.

## Compared with alternatives

Pick CityHash mainly for legacy/reproducibility reasons (matching an existing on-disk hash or a 2011-era baseline); for new code, komihash, rapidhash, or t1ha in this catalog beat both CityHash and Murmur with active maintenance, and MUM/VMUM-V2 explicitly benchmarks itself against CityHash64 and wins.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (stdint.h, utility); CRC variants additionally need an SSE4.2-capable CPU and compiler support for the _mm_crc32_u64 intrinsic |
| **Minimum toolchain** | not documented precisely; header only uses uint32_t/uint64_t/std::pair, autoconf build dates to 2011-2013, no C++11-only constructs observed |
| **Platforms** | little-endian x86/x86-64 primarily (CRC variants need SSE4.2); header states big-endian support is only lightly tested |
| **Thread safety** | not documented; functions take no global state in their declarations (city.h has no mutable globals), so they are reentrant by construction, but the project makes no explicit thread-safety statement |
| **Drop-in for the baseline** | partial — explain: same free-function shape as Murmur2/Murmur3 (buffer+len in, integer out) so it's a drop-in for a hand-rolled Murmur call, but there is no std::hash specialization, so it is not a drop-in for std::hash itself |

## Gotchas

- No seed randomization by default: CityHash64/CityHash32 without a seed are vulnerable to a hash-flooding DoS (CVE-2012-6051); pass a random seed via the \*WithSeed/\*WithSeeds variants for adversarial input
- CRC-based variants (CityHashCrc128/256 in citycrc.h) require an SSE4.2 CPU and the _mm_crc32_u64 intrinsic; the autoconf build's --enable-sse4.2 flag must be set or citycrc.h isn't installed
- hash(a+b) cannot be derived from hash(a) and hash(b) for any function in this file (stated in the header) — no incremental combination of partial hashes (open issue #17)
- Big-endian support is explicitly called out in city.h as 'only lightly tested'

## Caveats and trade-offs

Repository is archived by Google and had its last real commit in 2022; the README's benchmark numbers date to roughly the CityHash v1.0.3/1.1 era (\~2011) on now-obsolete server hardware, do not state compiler flags, and are not compared against any modern hash (xxh3, rapidhash, wyhash); tier capped at C because compiler/flags are unstated for these specific numbers.

No incremental/streaming API; not SIMD/AVX-optimized the way modern hashes (xxh3, rapidhash) are; the CRC-based variants depend on the _mm_crc32_u64 intrinsic being available.

## Maintenance

Archived by Google; last commit 2022-07-19 was housekeeping, last real release was v1.1.1 in June 2013. MIT-licensed and small enough (3 source files) to vendor, but expect no further fixes — known issues such as CVE-2012-6051 and #46 (Windows byteswap.h detection) remain open.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README numbers against Murmur2/Murmur3F on a single core of a 2.67GHz Xeon X5550, with no stated compiler/flags and no benchmark harness in the repo (src/ has only city.cc, city.h, citycrc.h, city-test.cc).
- **Verifier notes:** The README matches the record verbatim: 7/6/9ns vs Murmur2 6/6/15ns and Murmur3F 14/15/23ns; CityHashCrc256 at 5-5.5 bytes/cycle vs Murmur3F at 2.4 bytes/cycle. The derived ratios (about 1.7x-2.6x at 64 bytes, 2.1x-2.3x on long strings) hold. gh api shows the repo is archived, MIT, 1231 stars, not a fork, last commit 2022-07-19, so 'abandoned' is correct.
- **Pages the verifier opened:**
  - <https://github.com/google/cityhash>
  - <https://github.com/google/cityhash/blob/master/README>
- **Sources the enricher read:**
  - <https://github.com/google/cityhash>
  - <https://github.com/google/cityhash/blob/master/README>
  - <https://github.com/google/cityhash/blob/master/src/city.h>
  - <https://github.com/google/cityhash/blob/master/NEWS>
  - <https://github.com/google/cityhash/issues>
  - <https://github.com/google/cityhash/issues/10>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/google/cityhash`) · [data/wave1/enrich/raw/github_com_google_cityhash.json](../../../data/wave1/enrich/raw/github_com_google_cityhash.json) (enrichment confidence 0.6)

</details>
