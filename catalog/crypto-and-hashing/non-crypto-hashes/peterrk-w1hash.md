# W1Hash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Non-cryptographic hashes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C, Go` · `BSD-3-Clause` · 🟢 active

> A wyhash-derived 64-bit non-cryptographic hash, tuned to spend fewer cycles on 1-16 byte keys than wyhash v4.2.

| | |
|---|---|
| **Beats** | wyhash |
| **Claimed result** | Independent rurban/smhasher: small-key average 26.85 vs 28.91 cycles/hash for wyhash v4.2 (about 7% fewer cycles, derived from page data). Per key size, 23.5-25.8 vs 27-28 cycles/hash for 1-16 byte keys (about 8-15% fewer, derived from page data). Author's README chart (Core Ultra 7 155H, clang): about 12 vs 17 units for 1-7 byte keys and 12 vs 14 for 8-16 byte keys against a single combined wyhash/rapidhash line (about 1.42x and 1.17x, derived from the chart), with a slight edge at 17-32 bytes, where XXH3 (xxh3low) is fastest. W1Hash is not faster than rapidhash v3 in SMHasher (about 20 cycles/hash at 1-16 bytes). It is also about 37% slower than wyhash in bulk throughput: 14208 vs 22640 MiB/s (derived from page data). |
| **Workload** | Small-key hashing speed (1-32 byte keys, cycles/hash) and bulk throughput (262144-byte keys, MiB/s) in rurban/smhasher, alongside wyhash v4.2, rapidhash v3 and xxh3. Also the author's README chart for 1-32 byte keys against wyhash/rapidhash (one combined line), xxh3low, t1ha2_atonce and komihash. |
| **Metric** | throughput |
| **Hardware** | SMHasher main table: AMD Ryzen 5 3350G, as labeled in its README. Author's chart: Intel Core Ultra 7 155H. |
| **Compiler and flags** | SMHasher: compiler and flags not stated (built with the repo's CMake setup). Author's chart: clang on Ubuntu, flags not stated. |
| **Adoption** | 4 stars |
| **Last commit** | 2026-07-25 |
| **Links** | [repository](https://github.com/PeterRK/w1hash) · [benchmark](https://github.com/rurban/smhasher/blob/master/README.md) |

## Verdict

In rurban/smhasher (table labeled AMD Ryzen 5 3350G, compiler and flags not stated), w1hash averaged 26.85 cycles/hash on 1-32 byte keys against wyhash v4.2's 28.91 (23.5-25.8 vs 27-28 at 1-16 bytes), but rapidhash v3 averaged 22.04, and w1hash's bulk throughput at 256 KB was 14,208 vs 22,640 MiB/s for wyhash. SMHasher3 found no average small-key win (29.34 vs 29.31 cycles) but better bulk (8.15 vs 6.98 bytes/cycle). The author's own chart (Core Ultra 7 155H, clang) shows about 12 vs 14-17 units at 1-16 bytes against a combined wyhash/rapidhash line, with XXH3 fastest above 16 bytes.

## Use it when

- Hash-table keys of 1-16 bytes (short strings, small IDs, packed structs) on x86-64 or AArch64, where rurban/smhasher measured 23.5-25.8 cycles/hash against wyhash v4.2's 27-28
- Hashing 64-bit integer keys with the dedicated w1hash64() (two multiplies)
- In-memory tables where the hash is never persisted, so the fact that its output differs from wyhash does not matter
- Mixed C and Go code that needs the same hash value on both sides: the Go port is tested bit-for-bit against the C header through cgo

## Skip it when

- Bulk hashing (KB and up) as measured in rurban/smhasher: about 14.2 GB/s against wyhash's 22.6 GB/s, roughly 37% slower. SMHasher3 measured the opposite (8.15 vs 6.98 bytes/cycle), so check on your own hardware.
- When rapidhash v3 or a5hash is an option: rapidhash v3 is faster at every 1-16 byte size in rurban/smhasher (about 20 vs 23.5-25.8 cycles/hash), and both pass all 250 SMHasher3 tests. w1hash does not.
- When hash quality matters on sparse inputs: SMHasher3 fails w1hash on the TwoBytes keyset at 48-byte keys (6 full 64-bit collisions against 0 expected). Its small-key average there is 29.34 cycles, the same as wyhash's 29.31, so the short-key edge does not appear in that harness.
- Any code running under AddressSanitizer or Valgrind, or any strictly portable C, because of the deliberate past-the-end reads (see gotchas)
- Hash-flooding (HashDoS) resistance or anything cryptographic: it is a plain seeded non-cryptographic hash, and no security analysis is documented

## How it is fast

Keys of 0-16 bytes go through a per-length switch that loads the key in at most two reads, then run a single 64x64-&gt;128 multiply-and-fold (MUM) finalization. On x86-64 and AArch64, 3, 5, 6 and 7-byte tails use one wider load that may run past the end of the key, masked down, whenever that load stays inside the same 4 KB page. Longer inputs are consumed 16 bytes per MUM, with a 4-lane 64-byte loop above 64 bytes (wyhash v4.2 uses 3 lanes of 48 bytes). The seed and length are pre-mixed with one extra multiply at entry.

## Compared with alternatives

Pick it over wyhash only for very short keys where you control persistence: it fails 1 SMHasher3 test against wyhash v4.2's 15, and rurban/smhasher shows 7-15% fewer cycles at 1-16 bytes. rapidhash (faster at small keys in rurban/smhasher and passes all SMHasher3 tests) and a5hash (26.91 cycles small-key average in SMHasher3, passes all tests) are generally the better choice, and w1hash's main remaining draws are its 1-4 byte speed in SMHasher3 and its matching Go port.

## Integration

| | |
|---|---|
| **Form** | header-only (C, w1hash.h); Go module (github.com/peterrk/w1hash) |
| **Dependencies** | none |
| **Minimum toolchain** | C: C99-level compiler (stdint.h, static inline), using __uint128_t, MSVC x64 _umul128, or a portable 32-bit multiply fallback. Go: 1.25 (go.mod declares go 1.25.0). |
| **Platforms** | any. Fast unaligned-read paths are enabled on x86-64 and AArch64 (or with -DW1_LITTLE_ENDIAN_UNALIGNED_READ); other targets use byte-assembled little-endian reads. Go has hand-translated amd64 assembly and a pure-Go fallback on every other GOARCH. |
| **Thread safety** | Stateless pure functions with no globals, so concurrent use is safe. Not stated in the docs; follows from the code. |
| **Drop-in for the baseline** | partial: the call shape matches wyhash (key, len, seed -&gt; uint64), but outputs differ from wyhash and there is no secret-array parameter, so it only replaces wyhash where hashes are never stored or compared across versions |

## Gotchas

- Past-the-end reads: on x86-64/AArch64 the C header, and the Go amd64 assembly, read up to 3 bytes beyond the key for 3/5/6/7-byte tails when the read stays within a 4 KB page. They also use unaligned type-punned loads (\*(uint64_t\*)p). SMHasher3 tags the implementation 'ub_reads' and FLAG_IMPL_READ_PAST_EOB. Expect ASan/UBSan/Valgrind reports.
- Until 2026-07-25 (commit 68a6bf2, issue #1, still open) the portable multiply fallback declared a variable twice and did not compile on targets that have neither __int128 nor MSVC x64, such as 32-bit builds. Use a revision at or after that fix.
- The MSVC x64 branch calls _umul128 without including &lt;intrin.h&gt;. MSVC users may need to include it before w1hash.h; the repo has no MSVC CI.
- In Go, the tests and BenchmarkHash build only with cgo (they compare against the C header), the old purego build tag was removed in March 2026 so amd64 always uses assembly, and the benchmark times only w1hash itself (Go vs C), not any competitor.

## Known shortcomings

- Small-key win over wyhash only (rurban smhasher 1-16 B: 23.5-25.8 vs 27-28 cycles); rapidhash v3 is faster (\~20 cycles) despite the author's chart, and bulk is \~37% slower than wyhash (14,208 vs 22,640 MiB/s). 4 stars.
- SMHasher3 marks it FAIL (TwoBytes 48 B: six 64-bit collisions; 249/250) and shows no small-key win there (29.34 vs wyhash 29.31 cycles), while bulk is better (8.15 vs 6.98 bytes/cycle), the opposite of rurban's result. rapidhash v3 and a5hash beat it and pass all tests. Reads past the end of the buffer with type-punned loads (ASan noise); non-int128 builds were broken until 2026-07-25; MSVC build lacks &lt;intrin.h&gt;.

## Caveats and trade-offs

The author's benchmark is only a PNG chart with an unlabeled y-axis (probably cycles or ns per hash, lower is better). There is no comparison benchmark script in the repo; the Go BenchmarkHash benchmarks only w1hash itself. The chart puts wyhash and rapidhash on one line and does not say which rapidhash version. Independent SMHasher confirms the small-key win over wyhash v4.2, but shows rapidhash v3 faster at every small key size and w1hash about 37% slower than wyhash in bulk throughput. SMHasher tested the November 2024 C version; the C header has changed since only by a one-line cleanup. Output differs from wyhash. Very low visibility (4 stars).

A wyhash variant tuned for short inputs; does not produce the same digests as wyhash, so it is not a drop-in replacement. Go port ships hand-written amd64 assembly plus a generic fallback; also embedded as a reference hash inside rurban/smhasher and fwojcik/smhasher3.

## Maintenance

The C algorithm dates from November 2024, a Go port was added in March 2026, and the last commit (a compile fix) landed on 2026-07-25. It is BSD-3-Clause, a single \~5 KB header that is trivial to vendor, and has very low adoption (4 stars) beyond its inclusion in rurban/smhasher and SMHasher3.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C to B. rurban/smhasher is a well-known independent suite (about 2.2k stars). Its README table and per-hash reports (doc/w1hash.txt, doc/wyhash.txt) show w1hash using fewer small-key cycles/hash than wyhash v4.2. SMHasher does not state its compiler or flags, so this is not A. The author's own README evidence is only a PNG chart with no benchmark script, which on its own would be C.
- **Verifier notes:** The metadata checked out: BSD-3-Clause, not a fork, not archived, 4 stars, last commit 2026-07-25, so active. The wyhash small-key claim is independently supported by SMHasher, but the rapidhash part holds only in the author's own chart and is contradicted by SMHasher's rapidhash v3 numbers. The catalog should frame this as a short-key-only win over wyhash.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `hardware`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** rurban/smhasher: W1Hash avg small-key 26.85 vs wyhash v4.2 28.91 cycles/hash; bulk 14,208 vs 22,640 MiB/s.; SMHasher3: W1Hash FAIL (249/250); small keys 29.34 vs wyhash 29.31 cycles; bulk 8.15 vs 6.98 bytes/cycle.
- **Pages the verifier opened:**
  - <https://github.com/PeterRK/w1hash>
  - <https://github.com/PeterRK/w1hash/blob/main/README.md>
  - <https://raw.githubusercontent.com/PeterRK/w1hash/main/README.md>
  - <https://raw.githubusercontent.com/PeterRK/w1hash/main/benchmark.png>
  - <https://raw.githubusercontent.com/PeterRK/w1hash/main/w1hash_test.go>
  - <https://github.com/rurban/smhasher>
  - <https://github.com/rurban/smhasher/blob/master/README.md>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/README.md>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/w1hash.txt>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/wyhash.txt>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/rapidhash.txt>
- **Sources the enricher read:**
  - <https://github.com/PeterRK/w1hash>
  - <https://github.com/PeterRK/w1hash/blob/main/README.md>
  - <https://github.com/PeterRK/w1hash/blob/main/benchmark.png>
  - <https://github.com/PeterRK/w1hash/blob/main/w1hash.h>
  - <https://github.com/PeterRK/w1hash/blob/main/w1hash_amd64.go>
  - <https://github.com/PeterRK/w1hash/blob/main/w1hash_amd64.s>
  - <https://github.com/PeterRK/w1hash/blob/main/w1hash_generic.go>
  - <https://github.com/PeterRK/w1hash/blob/main/w1hash_test.go>
  - <https://github.com/PeterRK/w1hash/blob/main/go.mod>
  - <https://github.com/PeterRK/w1hash/blob/main/internal/cgotest/cgo.go>
  - <https://github.com/PeterRK/w1hash/commits/main>
  - <https://github.com/PeterRK/w1hash/commit/3bc9da17>
  - <https://github.com/PeterRK/w1hash/commit/68a6bf2c>
  - <https://github.com/PeterRK/w1hash/issues/1>
  - <https://github.com/rurban/smhasher/blob/master/README.md>
  - <https://github.com/rurban/smhasher/blob/master/doc/w1hash.txt>
  - <https://github.com/rurban/smhasher/blob/master/doc/wyhash.txt>
  - <https://github.com/rurban/smhasher/blob/master/doc/rapidhash.txt>
  - <https://github.com/fwojcik/smhasher3>
  - <https://github.com/fwojcik/smhasher3/blob/main/hashes/w1hash.cpp>
  - <https://github.com/fwojcik/smhasher3/blob/main/results/README.md>
  - <https://github.com/fwojcik/smhasher3/blob/main/results/raw/w1hash.txt>
  - <https://github.com/fwojcik/smhasher3/blob/main/results/raw/wyhash.txt>
  - <https://github.com/fwojcik/smhasher3/blob/main/results/raw/rapidhash.txt>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/peterrk/w1hash`) · [data/wave7/enrich/raw/github_com_peterrk_w1hash.json](../../../data/wave7/enrich/raw/github_com_peterrk_w1hash.json) (enrichment confidence 0.8)

</details>
