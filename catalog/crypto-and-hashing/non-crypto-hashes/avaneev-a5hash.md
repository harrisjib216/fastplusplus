# a5hash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Non-cryptographic hashes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🟢 active

> Tiny header-only C hash for hash-map keys; beats XXH64 and edges wyhash on short keys, but slow on bulk data.

| | |
|---|---|
| **Beats** | wyhash, xxHash (xxhash64) |
| **Claimed result** | SMHasher3 results summary: a5hash small-key (1-32 bytes) avg 26.91 cycles/hash vs wyhash 29.31 and XXH-64 52.60 (about 8% and 49% fewer cycles, derived from page data). On bulk data, a5hash is slower than both baselines: 2.63 bytes/cycle vs wyhash 6.98 and XXH-64 3.99 (a5hash-128 does 6.92). The author's README (first-party SMHasher3 run on Xeon E-2386G) gives 11.50 cycles/hash small-key vs XXH3-64 21.31 and rapidhash (wyhash-derived) 18.10. It also gives about 11 cycles/hash for 0-64 byte strings on Zen 5 and 15 GB/s bulk on Ryzen 9950X. |
| **Workload** | Small-key (1-32 byte, hash-table/hash-map style) hashing latency; also author's own repeated 0-64 byte hashing on Zen 5 and bulk hashing on Ryzen 9950X |
| **Metric** | latency |
| **Hardware** | Unstated in the SMHasher3 summary (raw file only converts at a nominal 3.5 GHz); author's README comparison table ran on Xeon E-2386G (Rocket Lake), AlmaLinux 9.3; author's headline numbers are from Zen 5 / Ryzen 9950X |
| **Adoption** | 51 stars |
| **Last commit** | 2025-12-19 |
| **Links** | [repository](https://github.com/avaneev/a5hash) · [benchmark](https://gitlab.com/fwojcik/smhasher3/-/blob/main/results/README.md) |

## Verdict

SMHasher3's independent results page (Frank Wojcik's suite, testing a5hash v5.21) lists a5hash at 26.91 cycles/hash averaged over 1-31 byte keys, against 29.31 for wyhash v4.2 and 52.60 for XXH-64, and at 2.63 bytes/cycle for 256 KiB bulk input, against 6.98 and 3.99. The page names no CPU or compiler and converts to GiB/s at a nominal 3.5 GHz. The author's README has a first-party SMHasher3 run on a Xeon E-2386G under AlmaLinux 9.3 (compiler unstated) showing 11.50 cycles/hash against 18.10 for rapidhash and 21.31 for XXH3-64; std::hash itself was not benchmarked.

## Use it when

- In-memory hash tables and maps keyed by short strings or small structs (about 1-32 bytes) where the cost of each hash call matters. SMHasher3 averages it at 26.91 cycles/hash over 1-31 byte keys, against 29.31 for wyhash and 52.60 for XXH64.
- Key lengths mostly between 17 and 31 bytes. That is where its SMHasher3 lead over wyhash is largest (29-30 vs 33.75 cycles); at 16 bytes and below the two are within about 2.5 cycles.
- You want a 64-bit hash that passes all 250 SMHasher3 tests at wyhash-level small-key cost. wyhash fails 15 of those tests (Permutation and SeedZeroes) and XXH64 fails 9.
- A single dependency-free header that compiles as C99 or as any C++ dialect (pre-C++11 included) and inlines into the call site.
- 32-bit embedded targets that only need a 32-bit hash: a5hash32() uses only 32x32-&gt;64 multiplies and passes all SMHasher3 tests at 25.81 cycles/hash.

## Skip it when

- Bulk data such as files, large buffers or checksums. In SMHasher3, plain a5hash() does 2.63 bytes/cycle, against 6.98 for wyhash, 3.99 for XXH64 and 12.82 for XXH3-64. Use a5hash128() or XXH3 instead.
- Hashes that are stored, sent between machines or compared across builds. Output differs between big- and little-endian hosts by design, outputs have changed between releases (the 5.15 and 5.16 commits both say "changed output"), and there is no streaming API. The README itself recommends komihash when you need portable hashes.
- Services exposed to hash flooding that rely on a secret seed. A third-party report filed 2026-09-18 (komihash issue #24, no reply when read) gives fixed 17- and 25-byte pairs on which a5hash128 collides for every seed. For 64-bit a5hash it gives weak-seed classes in which one specific pair collides with probability of at least about 2^-38. That is far above the 2^-59 to 2^-62 blinding-multiplication odds the README estimates.
- When you need a clear, reproducible small-key win. Independent numbers are thin: SMHasher3's margin over wyhash is about 8%, and rurban/smhasher (which tested the older v5.13) puts a5hash at 28.84 cycles/hash, level with wyhash (28.91) and behind rapidhash (22.04).
- Teams that want an upstream bug tracker and a review trail. The repo has issues and discussions disabled. The author has also said that a5hash's mathematical structure is of lower quality than komihash's, and that he rates komihash higher overall.

## How it is fast

Like wyhash, it is built on 64x64-&gt;128-bit multiplication. Unlike wyhash's multiply-and-fold (mum), it never XORs the product halves together during hashing: both halves become the next two state words, and adding the constants 0x5555... and 0xAAAA... after each 16-byte block lets the state recover if a product comes out zero. A key of 4-16 bytes is read as overlapping 32-bit loads from both ends, so a short key costs a couple of multiplies and no loop. The function is force-inlined and small (about 270-330 bytes of machine code per the README), so a seed of 0 or a compile-time-constant length folds away. The 64-bit bulk loop is one serial multiply chain at 16 bytes per step, which explains its low bulk speed; a5hash128 runs four independent multiply lanes over 64-byte blocks and reaches about 2.6x the bulk throughput.

## Compared with alternatives

Pick it over wyhash or xxHash (XXH64) only when almost every key is under about 32 bytes and you want a hash that passes all of SMHasher3. Once bulk throughput matters, wyhash, XXH3, AquaHash or Meow hash win clearly (6.98-15.84 vs 2.63 bytes/cycle). The original MuseAir's BFast variant (SMHasher3 row MuseAir.bfast: 26.28 cycles, 8.64 bytes/cycle) matches it on short keys and wins bulk, so a5hash's remaining edge over MuseAir is mostly smaller code and C99 portability.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (string.h/stdint.h, plus intrin.h/immintrin.h under MSVC) |
| **Minimum toolchain** | ISO C99, or any C++ (C++11 and later use noexcept/nullptr; older dialects use throw()). The README reports testing with GCC, Clang, MSVC and Intel C++. It uses __uint128_t, _umul128, _mulx_u64 or __umulh when available and falls back to portable 32-bit code. |
| **Platforms** | any. Tested on x86, x86-64 and AArch64 (Apple Silicon) under Windows 11, AlmaLinux 9.3 and macOS 15.3.2. The 64-bit variants are slow on 32-bit CPUs (use a5hash32 there), and big-endian hosts produce different hash values. |
| **Thread safety** | Not documented. By reading the source, all functions are pure static inline code with no global state, so they are reentrant; a5rand() keeps its state in variables the caller owns. |
| **Drop-in for the baseline** | partial — it has the same (ptr, len, seed) -&gt; uint64 shape as XXH64 and wyhash, but it produces different values, takes no secret array (unlike wyhash), has no streaming state API (unlike XXH64), and its results depend on endianness. |

## Gotchas

- In SMHasher3, a5hash128() with rh=NULL (the a5hash-128.64 row) beats plain a5hash() on both short keys (24.64 vs 26.91 cycles, and a flat 22 cycles for 20-31 bytes) and bulk data (6.92 vs 2.63 bytes/cycle). The author's case for a5hash() rests on forced inlining and small code size inside real hash maps, which a benchmark that calls through function pointers does not reward, so benchmark both in your own table. Remember that a5hash128 is the variant with the seed-independent 17-32 byte collision report.
- Flooding resistance depends on how you seed it. The README requires a uniformly random 64-bit seed and hash outputs that are never exposed, and says a5hash32 (32-bit seed) should not be used in open systems.
- Gains at the hash-map level are small. The README's own table (Xeon E-2386G) shows 11.50 vs 18.10-21.31 cycles/hash on small keys, but std::unordered_map run cost is only 404 vs 428-430 cycles/op against XXH3-64 and rapidhash (about 6%). Its parallel-hashmap init (294) is slower than komihash (285), rust-ahash-fb (286) and XXH3-64 (292).
- The 64-bit variants are much slower on 32-bit CPUs, where the 64x64-&gt;128 multiply falls back to a multi-step routine built from 32-bit multiplies (adapted from Hacker's Delight). The README recommends a5hash32() on those targets.

## Known shortcomings

- Small-key speed only: on bulk data a5hash is slower than both baselines (SMHasher3 2.63 bytes/cycle vs wyhash 6.98 and XXH-64 3.99); use a5hash-128 (6.92) or another hash for long inputs.
- Third-party report (komihash#24, 2026-09-18, unanswered): a5hash128 17/25-byte input pairs collide for every seed, and a5hash64 weak-seed pair classes reach \~2^-38 versus the README's 2^-59 estimate. The author rates komihash as higher quality. Repo issues are disabled. Endian-dependent output, no streaming API. In rurban/smhasher (v5.13) it only ties wyhash (28.84 vs 28.91 cycles) and trails rapidhash (22.04).

## Caveats and trade-offs

Same author as komihash (already catalogued); the win is small-key only: bulk throughput on the SMHasher3 page (2.63 B/cycle) is below wyhash (6.98) and XXH-64 (3.99), and the author says bulk is 'intentionally moderately fast'; the SMHasher3 page gives no compiler or CPU; SMHasher3 tested a5hash v5.21 while the repo is now at v5.25; the README's own comparison table (Xeon E-2386G, SMHasher3 commit 7be7e9e) gives no compiler or flags

plain a5hash() bulk throughput (2.63 bytes/cycle in SMHasher3) is lower than wyhash's (6.98) - it is optimized specifically for small-key latency, not bulk; a5hash128 variant trades some small-key speed for much higher bulk throughput (6.92 bytes/cycle); non-portable hash values across endianness by design

## Maintenance

Active single-author project: 36 releases between March and December 2025, last commit 2025-12-19, and releases 5.22-5.25 changed only macros and comments, so the v5.21 that SMHasher3 tested has the same hash output as today's header. It is one MIT header and trivial to vendor, but issues are disabled on the repo, so bug reports end up elsewhere (for example in the komihash tracker).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** SMHasher3 is a well-known independent suite. Its results summary lists a5hash at 26.91 avg cycles (1-32 byte keys) against wyhash 29.31 and XXH-64 52.60. The summary and the raw a5hash.txt give no CPU model or compiler (only a nominal '@ 3.5 ghz' conversion), so it cannot be A.
- **Verifier notes:** The numbers on the SMHasher3 page match the record exactly, and a5hash passes 250/250 tests while wyhash fails 15 and XXH-64 fails 9. The README has a first-party table against XXH3-64 and rapidhash that the record said was missing, so it was added. Metadata is confirmed: MIT, 51 stars, last commit 2025-12-19, active.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`
- **Shortcomings recorded by:** SMHasher3 summary: small keys (1-32 B) 26.91 cycles/hash vs wyhash 29.31, XXH-64 52.60; bulk 2.63 B/cycle vs wyhash 6.98, XXH-64 3.99.; rurban/smhasher (a5hash v5.13): 28.84 cycles/hash vs wyhash 28.91, rapidhash 22.04. SMHasher3: a5hash128 (rh=NULL) 24.64 cycles, 6.92 B/cycle.
- **Pages the verifier opened:**
  - <https://gitlab.com/fwojcik/smhasher3/-/blob/main/results/README.md>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/README.md>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/raw/a5hash.txt>
  - <https://github.com/avaneev/a5hash>
  - <https://raw.githubusercontent.com/avaneev/a5hash/main/a5hash.h>
- **Sources the enricher read:**
  - <https://github.com/avaneev/a5hash>
  - <https://github.com/avaneev/a5hash/blob/main/README.md>
  - <https://github.com/avaneev/a5hash/blob/main/a5hash.h>
  - <https://github.com/avaneev/a5hash/commits/main>
  - <https://gitlab.com/fwojcik/smhasher3/-/blob/main/results/README.md>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/README.md>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/raw/a5hash.txt>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/raw/a5hash-128.64.txt>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/raw/wyhash.txt>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/raw/XXH-64.txt>
  - <https://github.com/avaneev/komihash/issues/24>
  - <https://github.com/avaneev/komihash/issues/19>
  - <https://github.com/fwojcik/smhasher3/issues/6>
  - <https://github.com/rurban/smhasher/issues/314>
  - <https://github.com/rurban/smhasher/issues/316>
  - <https://github.com/rurban/smhasher/issues/328>
  - <https://github.com/rurban/smhasher/blob/master/README.md>
  - <https://github.com/rurban/smhasher/blob/master/doc/a5hash.txt>
  - <https://hn.algolia.com/api/v1/search?query=a5hash>
  - <https://news.ycombinator.com/item?id=43513580>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/avaneev/a5hash`) · [data/wave7/enrich/raw/github_com_avaneev_a5hash.json](../../../data/wave7/enrich/raw/github_com_avaneev_a5hash.json) (enrichment confidence 0.8)

</details>
