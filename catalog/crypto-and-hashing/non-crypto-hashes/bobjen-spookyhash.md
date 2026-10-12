# SpookyHash V2 (Bob Jenkins' official repo)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Non-cryptographic hashes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Unlicense` · 🟢 active

> Bob Jenkins' own reference C++ SpookyV2, a 128-bit non-cryptographic hash about 1.2x faster than XXH64 on large buffers.

| | |
|---|---|
| **Beats** | xxHash64 (XXH64) |
| **Claimed result** | SpookyV2_64 13401 MiB/s bulk vs xxHash64 11177 MiB/s bulk (\~1.2x faster bulk throughput, derived from page data); but xxHash64 is faster per small-key call (49.67 cycles/hash, 230.24 cycles/map) than SpookyV2_64 (56.18 cycles/hash, 246.33 cycles/map), so SpookyV2 loses on small keys (derived from page data); xxh3 (20854 MiB/s) and City64 (14390 MiB/s) both beat SpookyV2_64 on every column (derived from page data). The bobjen/spookyhash README's own table (C++ vs its new Rust port, DoTimingSmall, no baseline hash) shows C++ reaching 19.54 GB/s at 16KB keys and 18.68 GB/s at 8KB, g++ -O3, one machine. |
| **Workload** | rurban/smhasher main table on an AMD Ryzen 5 3350G. MiB/sec is the average bulk speed over alignments 0-7 with 262144-byte keys. cycl./hash is the average of the small-key speed test over 1-31 byte keys. cycl./map is a C++ hashmap get test over /usr/dict/words. Rows compared: SpookyV2_32/64/128 vs xxHash64, xxh3 and City64 on the same machine. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 5 3350G 3.6GHz (rurban/smhasher's default results machine) |
| **Adoption** | 3 stars, 1 fork (repo created Mar 2026) |
| **Last commit** | 2026-03-29 |
| **Links** | [repository](https://github.com/bobjen/spookyhash) · [benchmark](https://github.com/rurban/smhasher) |

## Verdict

rurban/smhasher on its reference AMD Ryzen 5 3350G, with no compiler or flags stated, measured bulk speed on 256 KiB keys averaged over alignments 0-7, with MiB/s converted from bytes/cycle at a nominal 3 GHz. SpookyV2_64 ran at 13,401 MiB/s (4.68 B/cycle) against 11,177 MiB/s (3.91 B/cycle) for XXH64, about 1.2x, while XXH64 won the 1-31 byte small-key average (49.7 vs 56.2 cycles/hash) and XXH3 and City64 beat it on every column. The SpookyV2 code rurban built matches this repo's C++ (CRLF endings aside), and the README's own 19.5 GB/s at 16 KB (g++ -O3, unnamed machine) compares C++ only with the repo's Rust port.

## Use it when

- Checksumming or fingerprinting large, cache-resident buffers (roughly 1 KB and up) on 64-bit little-endian CPUs. SpookyV2_64 averaged 13,401 MiB/s against 11,177 for XXH64 on 256 KiB keys in rurban/smhasher, and SMHasher3 shows 4.40 against 3.99 bytes/cycle.
- You need a 128-bit result from plain, portable 64-bit integer code with no SIMD, AES or wide-multiply dependency, for example dedup keys or content IDs where 64-bit collision odds are too high.
- You must reproduce existing SpookyV2 values, such as stored keys, Bloom filters or on-disk indexes. This repo is the author's reference: rurban/smhasher's SpookyV2 rows build byte-identical copies of cplus/SpookyV2.cpp/.h, and TestSpookyV2.cpp holds 512 expected Hash32 values.
- Input arrives in fragments and you want the streaming result to match the one-shot hash. TestPieces checks every two-piece split of inputs up to 1 KB.
- You want a seeded 32-bit hash that passes both suites: rurban lists no quality problems for SpookyV2_32, and SMHasher3 passes SpookyHash2-32 on all 250 tests.

## Skip it when

- Hash-table keys of 16-32 bytes. When the 16-byte branch into ShortMix kicks in, it jumps from about 41-46 to 66-71 cycles/hash, against 43-68 for XXH64. Overall it averages 56.2 against 49.7 cycles/hash over 1-31 byte keys, and 246 against 230 cycles/map (rurban).
- New code that doesn't need SpookyV2-compatible values. XXH3 (20,854 MiB/s, 29.5 cycles/hash), wyhash (22,641) and rapidhash (21,514, 22.0 cycles/hash) beat it on both bulk and small keys in the same rurban table.
- Anything adversarial, such as hash-flooding-exposed tables or integrity against an attacker. Jenkins' page says 'When NOT to use it: if you have an opponent', and warns that a resourceful opponent can build same-hash messages.
- Portable persisted hashes across endianness, or strict-alignment CPUs. The page says big-endian machines are unsupported (they produce different values), and unaligned reads are enabled by default via a hard-coded #define in the .cpp.
- Memory-bound streaming from RAM. Jenkins notes that uncached reads cap it below about 2 bytes/cycle on his machines, and the README's 16-way parallel run fell to 6.5 GB/s per process (105 GB/s total) against 19.5 GB/s single-process at 16 KB.

## How it is fast

Inputs of 192 bytes or more go through Mix(), which runs 96-byte blocks over 12 independent 64-bit state words. Each 8-byte input word gets an add, two xors, a rotate and an add. With 12 lanes the CPU has a lot of instruction-level parallelism, using only add/xor/rotate: no SIMD and no multiplies. Jenkins says SSE2 and 64-bit-multiply versions were slower, and that about 12 variables was the sweet spot. Shorter inputs use a 4-word ShortMix/ShortEnd path that has a lower startup cost, and long inputs finish with three EndPartial rounds.

## Compared with alternatives

Pick it over xxHash (XXH3), wyhash or rapidhash only when you need SpookyV2-compatible values or a 128-bit result from multiply-free, SIMD-free code under a public-domain dedication, because those siblings are faster on both bulk and small keys. Against CityHash (City64 is faster in every rurban column but flagged 'Sparse, TwoBytes') or pengyhash (same 13.3-13.4 GB/s bulk but 74.8 against 56.2 cycles/hash on small keys), SpookyV2 has a clean rurban quality record and faster small keys than pengyhash.

## Integration

| | |
|---|---|
| **Form** | source-drop (cplus/SpookyV2.h + SpookyV2.cpp; no build system in the repo, and an open PR #1 proposes CMake) |
| **Dependencies** | none (stddef.h, stdint.h, memory.h). The Rust translation in rust/ is a standalone Cargo package with no dependencies and is not published on crates.io. |
| **Minimum toolchain** | Not stated. The library files use only pre-C++11 constructs plus &lt;stdint.h&gt; and an MSVC typedef branch. The test harness needs C++11 (&lt;chrono&gt;), and the README's timings used g++ -O3. The Rust port is edition 2021. |
| **Platforms** | Designed for and tested on 64-bit little-endian x86. Big-endian runs but gives different values. Strict-alignment CPUs need ALLOW_UNALIGNED_READS edited to 0 in SpookyV2.cpp. |
| **Thread safety** | The static Hash128/64/32 functions keep no global state and are reentrant. A SpookyHash streaming object is plain mutable state and needs one instance per thread (not documented beyond the code). |
| **Drop-in for the baseline** | partial — Hash64(msg, len, seed) has the same shape as XXH64(input, len, seed), but the values differ, the streaming API (Init/Update/Final on a class) differs from XXH64_state_t, and it is C++-only with no C linkage |

## Gotchas

- Hash128's hash1/hash2 are in-out: they carry the seed in and the hash out. Reusing the same variables across calls silently chains seeds, which is exactly what TestSpookyV2's DoTimingSmall does, so the README's GB/s table measures dependent back-to-back calls.
- SpookyV2.h has no include guard or #pragma once, and it puts global typedefs uint64/uint32/uint16/uint8 and an INLINE macro into every includer. That can clash with other code's typedefs, and a double include redefines the class.
- Reads go through uint64\*/uint32\* casts on unaligned pointers via a union. That is undefined behaviour under strict C++ and UBSan (rurban lists 'Spooky' among misaligned-read hashes) and faults on strict-alignment hardware unless you flip the macro.
- Don't use the two 64-bit halves of the 128-bit result as independent hashes for short keys. SMHasher3 fails SpookyHash2-128 on BIC for 3-28-byte keys (235/250 passed), while SpookyHash2-64 fails only SeedBIC/SeedBitflip on 3-11-byte keys (244/250).

## Known shortcomings

- Small keys are slower than xxHash64 (56 vs 50 cycles in rurban/smhasher), and XXH3, wyhash and CityHash are faster in bulk. SMHasher3: the 128-bit output fails BIC on 3-28 byte keys and the 64-bit output fails 6 seed tests. Not seed-independent-collision resistant (non-cryptographic). Replaces the archived g1mv/spookyhash C port.
- Only \~1.2x over XXH64 in bulk; loses on 16-31 byte keys (66-71 vs 43-68 cycles). The Rust port is 2-29% slower than the C++. Unaligned reads (UB); header lacks an include guard and defines global typedefs; big-endian machines give different values. Last commit 2026-03-29.

## Caveats and trade-offs

rurban/smhasher states the CPU (AMD Ryzen 5 3350G) for its main table but not the compiler or flags, so this is capped at tier B. SpookyV2 beats xxHash64 only on large-buffer bulk throughput. On small keys (cycles/hash, averaged over 1-31 byte keys) and in the hashmap test (cycles/map) it is slower than xxHash64, and xxh3 and City64 beat it in every column. The GitHub repo was created on 2026-03-28, but its history starts on 2025-12-23. It is Bob Jenkins' own repo: burtleburtle.net/bob/hash/spooky.html links to it and the commits are by Robert J Jenkins Jr. Its cplus/SpookyV2.cpp and cplus/SpookyV2.h are identical, apart from CRLF line endings, to the SpookyV2.cpp/.h that rurban/smhasher builds for its SpookyV2_32/64/128 rows, so those rows measure exactly this repo's C++ code. SpookyHash V1 (the 'UB' Spooky32/64/128 rows) was removed from this repo in Feb 2026. The repo also has a new Rust port, which Claude generated according to the README. The README's own throughput table (DoTimingSmall, g++ -O3, one unnamed machine) compares only C++ with Rust and includes no baseline hash. The Unlicense is a public-domain dedication with no patent grant.

No SIMD, plain 64-bit arithmetic with xor/barrel-shift for high ILP; 128-bit output (32/64-bit truncations available) vs xxHash64's 64-bit; repo adds a Rust port (Claude-generated) that reproduces identical hashes but runs \~7-13% slower than the C++ reference in the repo's own DoTimingSmall table.

## Maintenance

The algorithm has been frozen since 2012. Its author curated the repo in commits from Dec 2025 to 29 Mar 2026 (V1 removed Feb 2026, Rust port added Mar 2026), and nothing has been committed since; PR #1 (CMake) has been unanswered since April. The two C++ files are Unlicense (public domain, no patent grant) and trivial to vendor. The Rust port was written by Claude, reproduces the C++ hashes, and runs about 2-6% slower from 256 B up and 10-29% slower below that in the README table.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** rurban/smhasher is a well-known independent suite. Its main table on the stated CPU (AMD Ryzen 5 3350G 3.6GHz) lists SpookyV2_64 at 13401.13 MiB/s, 56.18 cycles/hash and 246.33 cycles/map, against xxHash64 at 11176.72 MiB/s, 49.67 cycles/hash and 230.24 cycles/map. The code is public, but neither the README nor doc/SpookyV2_64.txt names the compiler or flags, so this is B, not A.
- **Verifier notes:** bobjen/spookyhash contains the reference SpookyV2 code that the rurban/smhasher SpookyV2 rows measure. cplus/SpookyV2.cpp and .h diff clean against rurban's copies once CRLF endings are ignored, and burtleburtle.net links to this repo as the official source. That makes it a sound replacement for the archived g1mv/spookyhash C port. All numbers match rurban's README. They come from rurban/smhasher, not SMHasher3, which I did not check.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Shortcomings recorded by:** rurban/smhasher: SpookyV2 13,401 vs xxHash64 11,177 MiB/s bulk.
- **Pages the verifier opened:**
  - <https://github.com/bobjen/spookyhash>
  - <https://github.com/bobjen/spookyhash/blob/main/README.md>
  - <https://github.com/bobjen/spookyhash/blob/main/cplus/SpookyV2.cpp>
  - <https://github.com/bobjen/spookyhash/blob/main/cplus/SpookyV2.h>
  - <https://github.com/bobjen/spookyhash/commits/main>
  - <https://github.com/rurban/smhasher>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/SpookyV2.cpp>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/SpookyV2.h>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/SpookyTestV2.cpp>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/SpookyV2_64.txt>
  - <https://burtleburtle.net/bob/hash/spooky.html>
- **Sources the enricher read:**
  - <https://github.com/bobjen/spookyhash>
  - <https://github.com/bobjen/spookyhash/blob/main/README.md>
  - <https://github.com/bobjen/spookyhash/blob/main/LICENSE>
  - <https://github.com/bobjen/spookyhash/blob/main/cplus/SpookyV2.h>
  - <https://github.com/bobjen/spookyhash/blob/main/cplus/SpookyV2.cpp>
  - <https://github.com/bobjen/spookyhash/blob/main/cplus/TestSpookyV2.cpp>
  - <https://github.com/bobjen/spookyhash/blob/main/rust/Cargo.toml>
  - <https://github.com/bobjen/spookyhash/blob/main/rust/src/lib.rs>
  - <https://github.com/bobjen/spookyhash/blob/main/rust/src/main.rs>
  - <https://github.com/bobjen/spookyhash/commits/main>
  - <https://github.com/bobjen/spookyhash/commit/57ca2624>
  - <https://github.com/bobjen/spookyhash/pull/1>
  - <https://burtleburtle.net/bob/hash/spooky.html>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/README.md>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/SpookyV2_64.txt>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/xxHash64.txt>
  - <https://raw.githubusercontent.com/fwojcik/smhasher3/main/results/README.md>
  - <https://raw.githubusercontent.com/fwojcik/smhasher3/main/results/raw/SpookyHash2-64.txt>
  - <https://raw.githubusercontent.com/fwojcik/smhasher3/main/results/raw/SpookyHash2-128.txt>
  - <https://crates.io/api/v1/crates/spookyhash>
  - <https://hn.algolia.com/api/v1/search?query=bobjen%20spookyhash>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/bobjen/spookyhash`) · [data/wave7/enrich/raw/github_com_bobjen_spookyhash.json](../../../data/wave7/enrich/raw/github_com_bobjen_spookyhash.json) (enrichment confidence 0.8)

</details>
