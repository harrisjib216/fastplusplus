# komihash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [String search and hashing](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟢 active

> Header-only, non-cryptographic 64-bit hash beating wyhash and xxHash on short keys (0-31 bytes) via full 128-bit multiply accumulation.

| | |
|---|---|
| **Beats** | xxHash (XXH3_64 / XXH64) and wyhash_final4 |
| **Claimed result** | Averages over all 10 compiler/CPU combos (overhead excluded): komihash 5.34 7.2 cycles/hash (0-15b) and 8.6 (8-28b) vs wyhash_final4 13.5/18.0, XXH3_64 14.2/21.8, XXH64 10.2/15.0. That works out to \~1.9-2.1x fewer cycles than wyhash_final4, \~2.0-2.5x fewer than XXH3_64 and \~1.4-1.7x fewer than XXH64 on short keys (derived from page data). On 256,000-byte bulk hashing komihash (19.3-42.7 GB/s) is slower than XXH3_64 (28.0-68.4 GB/s) on all 10 platforms and slower than wyhash_final4 on 8 of 10 (derived from page data), so the advantage is specific to short/medium keys. |
| **Workload** | Hash short keys (0-15 bytes, 8-28 bytes) and 256,000-byte bulk buffers, averaged across 10 compiler/CPU combinations (GCC 11.5, Clang 18/19, ICC 19, clang-cl 18, Apple Clang 15) on Ryzen 3700X/9950X, Xeon E-2386G, Core i7-7700K, and Apple M1, measuring cycles/hash and GB/s. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 3700X (4.2GHz) and Ryzen 9950X (5.7GHz), Intel Xeon E-2386G (5.1GHz), Core i7-7700K (4.5GHz), Apple M1 (3.5GHz) |
| **Compiler and flags** | GCC 11.5.0 (-O3 -msse2 / -O3 -mavx2), LLVM Clang 19.1.7 (-O3 -mavx2), clang-cl 18.1.8 (/Ox -msse2 or -mavx2), ICC 19.0 (/O3 /QxSSE2), Apple Clang 15.0.0 (-O3) -- full 10-combo matrix given in the README |
| **Adoption** | 286 stars |
| **Last commit** | 2026-08-04 |
| **Links** | [repository](https://github.com/avaneev/komihash) · [benchmark](https://github.com/avaneev/komihash/blob/master/README.md) |

## Verdict

Author-run README benchmark across 10 compiler/CPU/OS combinations (GCC 11.5, Clang 18/19, ICC 19, clang-cl 18, Apple Clang 15 on Ryzen 3700X/9950X, Xeon E-2386G, Core i7-7700K, Apple M1) shows komihash 5.34 averaging 7.2 cycles/hash (0-15 bytes) and 8.6 cycles/hash (8-28 bytes) versus wyhash_final4 13.5/18.0, XXH3_64 14.2/21.8, and XXH64 10.2/15.0 — roughly 1.9-2.5x fewer cycles on short keys. On 256,000-byte bulk buffers komihash (19.3-42.7 GB/s) loses to XXH3_64 (28.0-68.4 GB/s) on all 10 platforms and to wyhash_final4 on 8 of 10.

## Use it when

- Hash table/map/Bloom-filter keying where short keys (0-31 bytes) dominate and you want lower cycles/hash than wyhash_final4 or XXH3_64 without requiring AVX2/SIMD
- Need identical hash values on both big- and little-endian platforms (e.g. hashes stored/compared across architectures)
- Hashing values whose total length isn't known upfront, or hashing many independent fixed-size fields incrementally (discrete-incremental API)
- Want a single dependency-free header (MIT) that's trivial to vendor into a C or C++ codebase
- Portable/scalar targets (no SIMD available) where a branch-light, non-vectorized hash is required

## Skip it when

- Bulk/large-buffer hashing (files, big blobs): on the README's own 256,000-byte test komihash (19.3-42.7 GB/s) loses to XXH3_64 (28.0-68.4 GB/s) on all 10 tested platforms and to wyhash_final4 on 8 of 10
- Adversarial or untrusted input where seeded collision-resistance matters: issue #23 (opened 2026-09-18, open as of this review) demonstrates a fixed 64-byte message pair that collides for \~91% of uniformly-random hidden 64-bit seeds, which weakens the README's 'seed it and hash-flooding risk is minimized' guidance
- Need a std::hash&lt;T&gt; drop-in for unordered_map/unordered_set without writing a wrapper — komihash exposes plain C functions, not a functor
- 32-bit target platforms, where the README states throughput is 'considerably lower' than 64-bit (no number given)
- Need cryptographic collision resistance — explicitly a non-cryptographic hash

## How it is fast

Unlike wyhash/CircleHash/lehmer64-style hashes, komihash keeps the full 128-bit result of each internal multiplication instead of folding it back into one 64-bit state word, so consecutive internal states stay distinguishable rather than losing entropy. It parses the input message without overlapping reads, which the author argues avoids the seed-value flaws overlap-based parsers can hit, while keeping branch count low on the 0-15/8-28 byte fast paths. It's scalar C99 (no SIMD requirement), so short-key speed comes from a tight instruction sequence rather than vector width.

## Compared with alternatives

Pick komihash over t1ha/CityHash/MUM-VMUM when you want the widest reproducible compiler/CPU benchmark matrix (10 combos) for short-key throughput and don't need SIMD. Pick rapidhash or another sibling instead if the open seed-dependent collision report (issue #23) is disqualifying for your threat model, or if bulk-buffer throughput matters more than short-key speed.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (standard C headers only: stdint.h, string.h) |
| **Minimum toolchain** | ISO C99 (C++98 supported via a stdint.h fallback path; full auto C++ compatibility, with extra branch optimizations under C++11+) |
| **Platforms** | x86, x86-64 (Intel/AMD), AArch64 (Apple Silicon); tested on Windows 10/11, AlmaLinux 9.6, macOS 26.4; scalar code, no SIMD required; 32-bit builds work but are notably slower per README |
| **Thread safety** | not documented explicitly; reading komihash.h shows the hash functions are pure/stateless with no global mutable state, so concurrent calls from independent threads with their own seed/context arguments appear safe by inspection — each thread must use its own komihash_stream_t for the streaming API |
| **Drop-in for the baseline** | partial — explain: same plain-C calling convention as xxHash/wyhash (komihash(data,len,seed) -&gt; uint64_t), not a std::hash&lt;T&gt; specialization; needs a small wrapper to use in unordered_map/unordered_set |

## Gotchas

- Open issue #23 (filed 2026-09-18, unresolved as of this review): a fixed 64-byte message pair collides under komihash for \~91% of uniformly-random hidden seeds, reproduced independently by the reporter against the released 5.34 header — a real gap in the 'seed it for collision-attack resistance' advice
- Default seed is 0 (no randomization) unless the caller passes one; self-seeding is required for any hash-flooding resistance, and per the issue above that resistance is weaker than the README implies
- No identity/passthrough hashing: README explicitly recommends using raw key values directly for fixed-size keys rather than hashing them, since komihash adds overhead a no-op wouldn't have
- Big-endian systems pay a \~20% bulk-throughput penalty from byte-swapping, which can be disabled via a macro but then breaks cross-platform hash-value portability

## Caveats and trade-offs

Never benchmarked against std::hash itself: the evidence is against best-in-class non-cryptographic hashes (xxHash, wyhash), not the std::hash baseline. The numbers are the author's own, and the benchmark exists only as an inline README snippet that relies on unpublished timer helpers (TClock/CSystem); the bulk GB/s test code is not published. On bulk throughput komihash loses to XXH3_64 on every listed platform.

Non-cryptographic hash, not adversarial-collision-resistant without seeding; header-only C (compiles as C++) but exposes plain C functions (komihash(), komirand()) rather than a std::hash&lt;T&gt; specialization, so it needs a small wrapper to drop into unordered_map/unordered_set.

## Maintenance

Actively maintained (last commit 2026-08-04, MIT-licensed, 286 stars) and trivial to vendor as one header, but an unresolved collision report (issue #23, opened 2026-09-18, six days before this review) is a live caveat for any security-relevant use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** The README 'Comparisons' section gives the compiler, flags and CPU for all 10 platforms, plus the exact measurement loop (README inline code block using komihash/wyhash/XXH3_64bits calls), comparing against xxHash and wyhash. The timer helpers (TClock/CSystem) and the bulk-test code are not published, but the cycles/hash loop can be reproduced as given.
- **Verifier notes:** Every quoted number is on the README. I tightened the ratio range (vs XXH3_64 on 8-28b it is \~2.5x) and made the bulk caveat more precise (XXH3_64 wins bulk on all 10 platforms, not just 'some'). Metadata is accurate: MIT, 286 stars, last commit 2026-08-04, not archived.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/avaneev/komihash>
  - <https://github.com/avaneev/komihash/blob/master/README.md>
- **Sources the enricher read:**
  - <https://github.com/avaneev/komihash>
  - <https://github.com/avaneev/komihash/blob/master/README.md>
  - <https://github.com/avaneev/komihash/blob/master/komihash.h>
  - <https://github.com/avaneev/komihash/issues/23>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/avaneev/komihash`) · [data/wave1/enrich/raw/github_com_avaneev_komihash.json](../../../data/wave1/enrich/raw/github_com_avaneev_komihash.json) (enrichment confidence 0.6)

</details>
