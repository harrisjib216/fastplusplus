# ChainHash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Non-cryptographic hashes](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟢 active

> Keyed 64-bit carry-less universal hash with a Lean-proved collision bound; beats XXH3-64 on long in-cache inputs.

| | |
|---|---|
| **Beats** | XXH3-64 (xxHash) |
| **Claimed result** | SMHasher3 Speed at 262,144 bytes: 28.31 B/TSC vs XXH3-64's 19.90 on Xeon 8375C (\~1.42x), and 26.26 vs 13.04 B/cycle on Apple M2 Pro (\~2.01x) (ratios derived from page data). On short 1-31-byte inputs ChainHash is much slower: 155.14 vs 29.44 cycles/hash on Xeon and 87.49 vs 25.05 on M2. |
| **Workload** | SMHasher3 Speed test, bulk hashing of 262,144-byte inputs, bytes/cycle measured on the same binaries/host for chainhash, XXH3-64, rapidhash, komihash, UMASH-64 and CLhash. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Platinum 8375C; Apple M2 Pro |
| **Compiler and flags** | Xeon: GCC 11.5, SMHasher3 CMake Release build with no global ISA flags (PCLMUL/VPCLMULQDQ/AVX-512 paths chosen at runtime), pinned to CPUs 16-23 with taskset. M2 Pro: Apple Clang 17, -O3 -march=native+crypto -std=c++11 -DNDEBUG (results/64/bench/build_m2.py). SMHasher3 --test=Speed. |
| **Adoption** | 7 stars |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/thomasahle/chainhash) · [benchmark](https://github.com/thomasahle/chainhash/blob/main/results/64/README.md) |

## Verdict

SMHasher3 --test=Speed on 262,144-byte inputs, timed in the same binaries. On a Xeon Platinum 8375C KVM guest (GCC 11.5, ChainHash on its AVX-512/VPCLMULQDQ path, XXH3-64 on SMHasher3's avx512 path, best of two passes), ChainHash ran 28.31 vs 19.90 bytes per TSC tick (\~1.42x). On an Apple M2 Pro (Apple Clang 17, -O3 -march=native+crypto, median of three gated passes) it ran 26.26 vs 13.04 bytes per calibrated cycle (\~2.0x). The author ran all of it.

## Use it when

- Hashing long in-memory buffers (roughly 1 KiB to a few hundred KiB): content fingerprints, chunk dedup and blob-keyed tables inside one process, where a random secret key is acceptable.
- You need a provable collision bound for inputs chosen without knowledge of the key, for example to resist collision flooding when hash values are never revealed.
- x86-64 with AVX-512 and VPCLMULQDQ (the Xeon 8375C figure: 28.31 vs XXH3-64's 19.90 B/TSC), or Apple M-series/AArch64 built with +crypto (26.26 vs 13.04 on M2 Pro).
- Parallel hashing of one large buffer: chainhash_partial/chainhash_join combine splits at 1 KiB multiples into the same digest as a one-shot call.

## Skip it when

- Short keys: 1-31-byte inputs cost 155 TSC ticks per hash vs 29 for XXH3-64 on the Xeon (87 vs 25 on M2), and the README says fixed costs dominate below a few hundred bytes.
- Unkeyed or public fingerprints, MACs, or any setting where an attacker sees hash values and then picks inputs: the bound is non-adaptive and the author states it is not a MAC or cryptographic digest.
- x86 without AVX-512: the author's harness measured 16.83 B/TSC on the YMM path and 16.10 on XMM vs 27.72 on ZMM, and no XXH3 comparison exists for those paths. MSVC, big-endian, non-crypto AArch64 builds and other ISAs fall back to a bit-serial carry-less multiply with no published speed.
- Out-of-cache streams: the design notes show 8 MiB inputs dropping to about 10.3 B/TSC on the Xeon, and XXH3 was not measured at that size.
- Maturity-sensitive code: the repo was created 2026-09-18, has one author and 7 stars, and has no independent benchmarks or outside review yet.

## How it is fast

Each 256-byte block is a carry-less NH: pairs of 64-bit words are XORed with key words and multiplied in GF(2^64) with PCLMUL/VPCLMULQDQ/PMULL, one multiply per 16 bytes, and reduced once per block. Block values are combined by Horner evaluation in an independent key word. Because the multiplier is constant, four interleaved blocks per 1 KiB region run as four independent lazy chains with no shuffles, reductions or spills in the loop (18 wide multiplies per KiB on AVX-512). The loop structure follows Orson Peters's PolymurHash; the binary field, comb layout and finalizer are new.

## Compared with alternatives

Over xxHash (XXH3), rapidhash or wyhash: choose it only for bulk inputs on CLMUL/PMULL hardware when you also want a provable bound, since those siblings win clearly on short keys. Over UMASH and CLHash, the other carry-less universal hashes, it is about 2.4-2.5x faster in bulk on the Xeon (28.31 vs 11.33 and 11.86 B/TSC) and 1.7-1.8x on M2, with a machine-checked bound, but UMASH is much cheaper per short key (36 vs 155 ticks).

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (libc headers; immintrin.h/cpuid.h on x86, NEON intrinsics on AArch64) |
| **Minimum toolchain** | C99 or C++11; x86 SIMD dispatch needs GCC or Clang target attributes (tested with GCC 11.5, Clang 21/22, Apple Clang 17) |
| **Platforms** | x86-64 with run-time dispatch (AVX+PCLMUL, AVX2+VPCLMULQDQ, AVX-512F+VPCLMULQDQ); little-endian AArch64 with crypto extensions enabled at compile time; portable C elsewhere, with the same digest but much slower |
| **Thread safety** | The key object can be shared read-only between threads; use one chainhash_stream per thread; backend detection is cached with relaxed atomics; the SMHasher3 thread-safety test passes |
| **Drop-in for the baseline** | partial — same role as XXH3-64 for bulk data, but it needs a 64-byte random key and a 448-byte key object instead of an optional seed, gives different digests, and is much slower on short inputs |

## Gotchas

- chainhash_key_from_seed (SplitMix64 from a 64-bit seed) exists for benchmarks, and SMHasher3 results use it. It does not supply the randomness the bound assumes: use chainhash_key_from_bytes with 64 OS-random bytes.
- Key setup runs about 48 field products through the portable bit-serial multiply, and key expansion is outside every published timing, so re-keying per message adds cost. A stream holds a 1 KiB buffer plus a pointer to the key, and the key must outlive the stream.
- The explicit backend entry points (chainhash_xmm/ymm/zmm/neon, chainhash_with_backend) are guarded only by assert(); with NDEBUG, an unsupported backend runs illegal instructions. Check chainhash_has_backend() first.
- On AArch64 without -march=armv8-a+crypto (Apple: -march=native+crypto), the header silently uses the portable path. ChainHash-128 is slower than XXH3-128 on the Xeon (14.43 vs 19.82 B/TSC).

## Known shortcomings

- Bulk-only win (28.31 vs 19.90 and 26.26 vs 13.04 GB/s against XXH3-64, \~1.4-2x); about 5x slower than XXH3 on 1-31 byte keys.
- The 1.42x Xeon result is AVX-512 against AVX-512 XXH3 in a VM; AVX2/SSE paths reach only \~16-17 bytes/TSC with no XXH3 comparison. Wins are for 256 KiB cache-resident inputs (8 MiB drops to \~10.3 bytes/TSC). Needs a 64-byte random key; the collision bound assumes inputs independent of the key (not a MAC). MSVC, ARM without crypto extensions and big-endian fall back to slow portable C. Repo is days old, single author, no outside benchmarks.

## Caveats and trade-offs

The author also wrote and ran the benchmark. Raw logs, SHA-256 provenance and the bench scripts are published, but the scripts depend on a separately configured SMHasher3 checkout and are 'archived evidence rather than a runnable distribution'. The Xeon bulk figure is the higher of two passes; M2 figures are medians of three. ChainHash is bulk-only and makes no small-key speed claim: it is \~5x (Xeon) and \~3.5x (M2) slower than XXH3 on 1-31-byte inputs. The repo was created 2026-09-18 and has no independent confirmation yet.

Bulk-only design: short inputs (1-31 bytes) are much slower than XXH3-64 (155 Xeon ticks vs 29 per hash), so it is not a drop-in for small-key hash tables. Also ships a machine-checked (Lean) collision-bound proof and a ChainHash-128 variant; ChainHash-128 loses to XXH3-128 on Xeon (14.43 vs 19.82 B/tick) but wins on M2 Pro (14.43 vs 12.53 B/cycle).

## Maintenance

Brand new: created 2026-09-18, last commit 2026-09-23, 7 stars and no issues filed. The MIT single header ships frozen test vectors, Lean proofs and a full 200/200 SMHasher3 pass, so it is easy to vendor, but it has no track record or third-party benchmark yet.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** results/64/README.md shows XXH3-64 timed in the same SMHasher3 binaries. The benchmark code is public (smhasher3/chainhash.cpp, results/64/bench/chainhash.cpp, run_speed.py, build_m2.py). CPUs are stated (Xeon Platinum 8375C, M2 Pro), as are the compilers (GCC 11.5, Apple Clang 17) and flags (M2: -O3 -march=native+crypto -DNDEBUG in build_m2.py; Xeon: SMHasher3 CMake Release, x86 paths dispatched at runtime).
- **Verifier notes:** Numbers match the page exactly, and the repo checks out: MIT, 7 stars, last commit 2026-09-23, not a fork. The added caveat on short-input slowness matters for any reader thinking of it as a general XXH3 replacement.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** Own benchmark (M2, bench/build_m2.py flags): 28.31 vs XXH3-64 19.90; 26.26 vs 13.04.
- **Pages the verifier opened:**
  - <https://github.com/thomasahle/chainhash>
  - <https://github.com/thomasahle/chainhash/blob/main/results/64/README.md>
  - <https://github.com/thomasahle/chainhash/blob/main/results/64/bench/README.md>
  - <https://github.com/thomasahle/chainhash/blob/main/results/64/bench/build_m2.py>
  - <https://github.com/thomasahle/chainhash/blob/main/results/64/bench/finish_xeon.sh>
  - <https://github.com/thomasahle/chainhash/blob/main/smhasher3/README.md>
- **Sources the enricher read:**
  - <https://github.com/thomasahle/chainhash>
  - <https://github.com/thomasahle/chainhash/blob/main/README.md>
  - <https://github.com/thomasahle/chainhash/blob/main/include/chainhash.h>
  - <https://github.com/thomasahle/chainhash/blob/main/docs/DESIGN.md>
  - <https://github.com/thomasahle/chainhash/blob/main/docs/SPEC.md>
  - <https://github.com/thomasahle/chainhash/blob/main/docs/THEOREM.md>
  - <https://github.com/thomasahle/chainhash/blob/main/Makefile>
  - <https://github.com/thomasahle/chainhash/blob/main/results/README.md>
  - <https://github.com/thomasahle/chainhash/blob/main/results/64/README.md>
  - <https://github.com/thomasahle/chainhash/blob/main/results/64/bench/README.md>
  - <https://github.com/thomasahle/chainhash/blob/main/results/64/bench/finish_xeon.sh>
  - <https://github.com/thomasahle/chainhash/blob/main/results/64/out/Xeon/environment.txt>
  - <https://github.com/thomasahle/chainhash/blob/main/results/64/out/Xeon/XXH3-64.run1.txt>
  - <https://github.com/thomasahle/chainhash/blob/main/smhasher3/README.md>
  - <https://github.com/thomasahle/chainhash/issues>
  - <https://github.com/thomasahle/chainhash/commits/main>
  - <https://hn.algolia.com/api/v1/search?query=chainhash%20ahle&tags=story>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/thomasahle/chainhash`) · [data/wave7/enrich/raw/github_com_thomasahle_chainhash.json](../../../data/wave7/enrich/raw/github_com_thomasahle_chainhash.json) (enrichment confidence 0.75)

</details>
