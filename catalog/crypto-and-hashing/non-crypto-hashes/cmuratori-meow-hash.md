# Meow hash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Non-cryptographic hashes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `Zlib` · 🔴 abandoned

> 128-bit AES-NI bulk hash for x86-64 file and asset hashing; about 3x XXH64's large-buffer throughput, roughly tied with XXH3.

| | |
|---|---|
| **Beats** | XXH64 (legacy xxHash), CityHash64, wyhash |
| **Claimed result** | SMHasher3 results table: MeowHash 12.43 bytes/cycle average bulk, against XXH-64 3.99, CityHash-64 4.75 and wyhash 6.98. That is about 3.1x, 2.6x and 1.8x (derived from page data). The same table puts XXH3-64 (current xxHash) at 12.82 bytes/cycle, slightly ahead of Meow in bulk, so the win is over legacy XXH64, not XXH3. |
| **Workload** | SMHasher3 bulk speed test (262144-byte and 262017-262144-byte keys, 'Alignment rnd' average), AES-NI path, single thread |
| **Metric** | throughput |
| **Hardware** | Unspecified x86-64 CPU with AES-NI. SMHasher3 gives GiB/s assuming 3.5 GHz and names no CPU model. |
| **Adoption** | 1.8k stars |
| **Last commit** | 2021-07-02 |
| **Links** | [repository](https://github.com/cmuratori/meow_hash) · [benchmark](https://gitlab.com/fwojcik/smhasher3/-/blob/main/results/README.md) |

## Verdict

SMHasher3 measured the bulk speed of its lightly modified MeowHash copy single-threaded on 262,017-262,144-byte keys at random alignment: 12.43 bytes/cycle (40.5 GiB/s at a nominal 3.5 GHz), against XXH-64 3.99, CityHash-64 4.75, wyhash 6.98 and XXH3-64 12.82. The copy is identical to upstream at seed 0 and adds a 64-bit seed in the nonce slot; CPU model and compiler are not named. Separately, xxHash's wiki (i7-9700K, clang 10, -O3 -mavx2) has Meow at 58.2 GB/s, about 3x XXH64's 19.4 GB/s and level with XXH3-AVX2's 59.4 GB/s.

## Use it when

- Change detection, deduplication and cache keys for large files or assets (tens of KB to GB) on x86-64 CPUs with AES-NI. SMHasher3 measures about 12.4 bytes/cycle at 256 KB, against 4.0 for XXH64 and 7.0 for wyhash.
- Cases that need a full 128-bit hash of data you control, where accidental collisions must be negligible. Meow passes all 250 SMHasher3 tests at 32, 64 and 128 bits, while XXH3-128 fails 36 and AquaHash fails 55 in the same summary.
- Replacing SHA-1 or MD5 used purely as a content fingerprint in a trusted build or asset pipeline, where there is no adversary.
- Codebases that can vendor one zlib-licensed header and already compile with -maes -mssse3 (or MSVC on x64).

## Skip it when

- Hash-table keys or anything under about 64 bytes. SMHasher3 puts Meow at about 61.5 cycles/hash for 1-32 byte keys, against 29.3 for wyhash and 30.7 for XXH3-64.
- Any adversarial setting: MACs, hash-flooding-resistant tables, or content addressing an attacker can influence. Peter Schmidt-Nielsen's 2021 cryptanalysis found a key-independent differential with probability about 2^-45, key recovery in about 2^49 queries, and SAT-built full 128-bit collisions for a known key (issue #80). The README downgraded v0.5 to 'level 1' and points to SipHash.
- Non-x86 targets, CPUs without AES-NI, or code that needs runtime dispatch. v0.5 ships only the x64 AES-NI header, with no ARM, C or runtime-detection path (issue #86 is still open).
- Projects that want a maintained dependency with a stable spec. v0.5 is still labelled a 'proposal' and never reached v1.0. The last code change was in 2021, and the NoHatCoder 0.6 candidates (#82) were never merged.
- Plain bulk speed on modern x86 where XXH3 is an option. xxHash's own benchmark (i7-9700K, clang 10, -O3 -mavx2) has XXH3-AVX2 at 59.4 GB/s against Meow at 58.2 GB/s, and SMHasher3 has XXH3-64 at 12.82 against Meow's 12.43 bytes/cycle, with XXH3 about 2x faster on small inputs.

## How it is fast

There are eight 128-bit accumulator lanes. Each 32-byte chunk drives two AES decryption rounds (aesdec) on two lanes, plus 64-bit adds and XORs into others of the same data reloaded at 1-byte offsets. The main loop consumes 256 bytes per iteration, which the authors describe as 16 AES rounds per 256 bytes, with a design target of 16 bytes/cycle. Above about 256 KB (0x3ff blocks) the loop switches to a variant with explicit prefetcht0 4 KB ahead. Tail bytes are fetched with one unaligned 16-byte load plus a pshufb/pand mask, which may read past the end of the buffer but never crosses a page. Finalisation is a fixed 12-step AES/add/xor shuffle that folds eight lanes into one, so every input under 32 bytes costs about the same (about 61 cycles).

## Compared with alternatives

Choose Meow over xxHash (XXH3/XXH128) or AquaHash when you hash large trusted buffers on x86-64 with AES-NI and want a 128-bit result that passes every SMHasher3 test; XXH3 matches its bulk speed but fails 27-36 SMHasher3 tests, and AquaHash is faster in bulk (15.84 bytes/cycle) but fails 55. Choose wyhash, rapidhash or a5hash for short keys and hash tables, and xxHash when you need portability, an integer seed or an actively maintained library.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (compiler intrinsics headers &lt;x86intrin.h&gt; / &lt;intrin.h&gt; only) |
| **Minimum toolchain** | C or C++ compiler with AES-NI and SSSE3/SSE4.1 intrinsics; build scripts use clang++ -O3 -maes -mavx (or -msse4) and MSVC cl -O2. GCC needs -maes -mssse3 at minimum or it fails with 'inlining failed ... target specific option mismatch' (#70). No minimum version is documented. |
| **Platforms** | x86-64 with AES-NI (32-bit x86 compiles but is untested, and MeowU64From is broken there, #74); Windows/MSVC, Windows/clang, Linux/clang per README; no ARM or portable fallback in v0.5 |
| **Thread safety** | Not documented. MeowHash is a pure function of its arguments with no global mutable state (unless MEOW_DUMP is defined); the streaming meow_state is per-caller. |
| **Drop-in for the baseline** | partial — it can replace XXH64/CityHash64 as a content fingerprint if you store MeowU64From(hash, 0) or the full 128 bits, but the API (128-byte seed, __m128i result) and the hash values differ, and it is not a suitable std::hash / hash-table replacement. |

## Gotchas

- Reads up to 15 bytes past the end of the input (without crossing a 4 KB page) and masks them off. ASan reports this as global-buffer-overflow (#79, closed as 'not a buffer overflow'); the PR to add an ASan guard (#83) is unmerged, so exclude the function from ASan yourself.
- The input and seed parameters are non-const void\* (a const PR was merged and then reverted, #71/#72; #78 is open), so C++ callers must cast away const.
- Hash values changed between v0.2, v0.3, v0.4 and v0.5, and the archived mollyrocket.com/meowhash docs describe the older API (meow_intrinsics.h, MeowHash_Accelerated, an ARM and C version) that is not in the v0.5 header. The live site is gone (#87), and the .travis.yml still references the removed headers.
- MeowU64From/MeowU32From require a compile-time-constant lane index (_mm_extract_epi64); on 32-bit builds the macro ignores the index and always returns the low 64 bits (#74, open).

## Known shortcomings

- Beats only legacy XXH64/CityHash64/wyhash in bulk: in the same SMHasher3 table XXH3-64 is about as fast (12.82 vs 12.43 bytes/cycle), and short keys are \~2x slower. Security notice downgraded to level 1: do not use as a MAC. Needs AES-NI; last commit 2021-07-02.
- Cryptanalysed in 2021 (Schmidt-Nielsen): key-free differentials at 2^-45, key recovery at 2^49 and full 128-bit collisions (#80); treat as non-cryptographic only. Bulk-only speed: \~61.5 cycles on short keys vs \~30 for wyhash/XXH3, and XXH3 ties in bulk (xxHash wiki 59.4 vs 58.2 GB/s). v0.5 is x64 AES-NI only with no ARM/C fallback or runtime check (#86); reads past the buffer end (ASan, #79 wontfix). Stuck at the v0.5 'proposal' since 2021.

## Caveats and trade-offs

Meow is built for large-buffer hashing. On short keys it is about 2x slower: 61.51 average cycles per hash for 1-32 bytes, against 29.31 for wyhash and 30.69 for XXH3-64. XXH3-64 (12.82 bytes/cycle) edges it out in bulk, and gxhash, falkhash and t1ha0.aesB are faster still but fail some SMHasher3 quality tests. Meow passes all 250 tests. The README security notice reclassifies v0.5 from level 3 to level 1 after Peter Schmidt-Nielsen's cryptanalysis, so it should not be used for MACs or DoS-resistant hash tables. v0.5 is still labelled a 'proposal' and never reached v1.0. mollyrocket.com/meowhash redirects to a Computer, Enhance! stub page with no benchmark data.

much worse small-key latency (61.5 cycles/hash vs wyhash's 29.3); after a published cryptanalysis break the maintainer downgraded it from security level 3 to level 1 and now recommends against using it for hash tables where hash-flooding/DoS is a concern; requires AES-NI hardware; project stalled at v0.5 'proposal' status, never reached v1.0

## Maintenance

Abandoned: the last commit (2021-07-02) only added the security notice, and v0.5 never left 'proposal' status. It is zlib-licensed, a single 744-line header that is easy to vendor, has 1.8k stars and 22 open issues, and is not archived.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The SMHasher3 results summary is a well-known independent third-party suite. It lists MeowHash at 12.43 bytes/cycle bulk against XXH-64 at 3.99, CityHash-64 at 4.75 and wyhash at 6.98, and the benchmark code is public. It is not A because neither the summary nor the raw MeowHash result names the CPU model, compiler or flags; they only give GiB/s '@ 3.5 ghz' with ncpu=1.
- **Verifier notes:** All four numbers match the SMHasher3 summary rows exactly (MeowHash 12.43, XXH-64 3.99, CityHash-64 4.75, wyhash 6.98). The record's last_commit of 2022-07-31 was the repo's pushed_at date; the newest commit on any branch is 2021-07-02 (master). It is still abandoned, not archived, Zlib licensed, with 1,831 stars.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `workload`, `hardware`, `last_commit`, `caveats`
- **Shortcomings recorded by:** SMHasher3 summary: bulk 12.43 B/cycle vs XXH3-64 12.82, wyhash 6.98, CityHash-64 4.75, XXH-64 3.99.; xxHash wiki: XXH3 59.4 vs Meow 58.2 GB/s bulk.
- **Pages the verifier opened:**
  - <https://gitlab.com/fwojcik/smhasher3/-/blob/main/results/README.md>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/README.md>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/raw/MeowHash.txt>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/raw/XXH3-64.txt>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/README.md>
  - <https://github.com/cmuratori/meow_hash>
  - <https://mollyrocket.com/meowhash>
  - <https://www.computerenhance.com/p/meowhash>
- **Sources the enricher read:**
  - <https://github.com/cmuratori/meow_hash>
  - <https://github.com/cmuratori/meow_hash/blob/master/README.md>
  - <https://github.com/cmuratori/meow_hash/blob/master/meow_hash_x64_aesni.h>
  - <https://github.com/cmuratori/meow_hash/blob/master/meow_example.cpp>
  - <https://github.com/cmuratori/meow_hash/blob/master/build.sh>
  - <https://github.com/cmuratori/meow_hash/blob/master/build.bat>
  - <https://github.com/cmuratori/meow_hash/blob/master/.travis.yml>
  - <https://github.com/cmuratori/meow_hash/blob/master/LICENSE>
  - <https://github.com/cmuratori/meow_hash/blob/master/util/meow_bench.cpp>
  - <https://github.com/cmuratori/meow_hash/blob/master/util/meow_test.cpp>
  - <https://github.com/cmuratori/meow_hash/blob/master/util/meow_test.h>
  - <https://github.com/cmuratori/meow_hash/issues>
  - <https://github.com/cmuratori/meow_hash/issues/47>
  - <https://github.com/cmuratori/meow_hash/issues/59>
  - <https://github.com/cmuratori/meow_hash/issues/70>
  - <https://github.com/cmuratori/meow_hash/issues/74>
  - <https://github.com/cmuratori/meow_hash/issues/76>
  - <https://github.com/cmuratori/meow_hash/issues/79>
  - <https://github.com/cmuratori/meow_hash/issues/80>
  - <https://github.com/cmuratori/meow_hash/issues/82>
  - <https://github.com/cmuratori/meow_hash/issues/83>
  - <https://github.com/cmuratori/meow_hash/issues/84>
  - <https://github.com/cmuratori/meow_hash/issues/86>
  - <https://github.com/cmuratori/meow_hash/issues/87>
  - <https://github.com/cmuratori/meow_hash/commits/master>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/README.md>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/raw/MeowHash.txt>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/hashes/meowhash.cpp>
  - <https://peter.website/meow-hash-cryptanalysis>
  - <https://web.archive.org/web/20230228011534/https://mollyrocket.com/meowhash>
  - <https://github.com/Cyan4973/xxHash/wiki/Performance-comparison>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/cmuratori/meow_hash`) · [data/wave7/enrich/raw/github_com_cmuratori_meow_hash.json](../../../data/wave7/enrich/raw/github_com_cmuratori_meow_hash.json) (enrichment confidence 0.8)

</details>
