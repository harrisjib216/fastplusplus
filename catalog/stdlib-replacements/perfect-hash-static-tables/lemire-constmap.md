# constmap

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Perfect hashing and static tables](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `Apache-2.0` · 🟢 active

> Immutable Go string-to-uint64 map built on binary fuse filters; up to 5.3x faster lookups than map[string]uint64 at 1M keys.

| | |
|---|---|
| **Beats** | Go builtin map[string]uint64 |
| **Claimed result** | README 'Performance gains' table (Apple M4 Max, 1,000,000 keys, every key queried once in random order): ConstMap 8.7 ns/op vs Go map[string]uint64 46 ns/op. The README states this as 5.3x over the whole key set, and 1.2x over only 256 queries. VerifiedConstMap, the variant that detects missing keys like a Go map does, takes 15 ns/op, about 3.1x (derived from page data). Memory is 9.0 bytes/key for ConstMap and 18 for VerifiedConstMap vs 48 for the Go map, about 5.3x and 2.7x less (derived from page data). The README 'Scaling' table (TestLookupAndMemoryTable, one pass, M4 Max) reports ConstMap / VerifiedConstMap / Go map at 10K keys as 9.4 / 10.4 / 14.8 ns (about 1.6x / 1.4x), at 1M keys as 12.5 / 18.6 / 51.1 ns (about 4.1x / 2.7x), and at 10M keys as 34.8 / 41.3 / 70.1 ns (about 2.0x / 1.7x). All of these ratios are derived from page data. |
| **Workload** | Every key of a 1,000,000-key string-to-uint64 dataset (keys 'key-%d') is looked up exactly once in random order, from a query buffer allocated in query order (makeQueryOrder in constmap_test.go). The Scaling table runs one pass at 10K, 100K, 1M and 10M keys. The README's batched MapMany numbers compare only against a loop over ConstMap.Map, not against Go's map. |
| **Metric** | latency |
| **Hardware** | Apple M4 Max for every Go-map comparison. The Intel Xeon Gold 6548N appears only in the MapMany-vs-loop batching, paired-vs-split layout and serialization numbers, none of which include Go's map. |
| **Compiler and flags** | Go gc toolchain via go test. The Go version is not stated: go.mod declares only a go 1.22 minimum, and CI uses 'stable'. The README gives `go test -bench=. -benchmem` and recommends `-count=5 -benchtime=3s`, but does not say which flags produced the headline table. The batch table uses medians of `-benchtime 3s -count 3`. The Go-map benchmark code is constmap_test.go (BenchmarkConstMap, BenchmarkVerifiedConstMap, BenchmarkGoMap, TestLookupAndMemoryTable with RUN_HEAVY_MEMORY_TESTS=1). batch_bench_test.go, hashbatch_bench_test.go and paired_test.go hold the batching and paired-layout benchmarks, which have no Go-map baseline. |
| **Adoption** | 238 stars |
| **Last commit** | 2026-09-17 |
| **Links** | [repository](https://github.com/lemire/constmap) · [benchmark](https://github.com/lemire/constmap/blob/main/README.md) |

## Verdict

The author's go test benchmark on an Apple M4 Max (Go version not stated) looked up each of 1,000,000 'key-%d' strings once in random order: ConstMap 8.7 ns vs 46 ns for a presized Go map[string]uint64 (5.3x), and VerifiedConstMap 15 ns (about 3.1x), at 9/18 vs 48 bytes/key. A separate scaling test times one run of 1,000,000 lookups per size (so repeated passes below 1M keys and a partial pass at 10M), and there the gap is about 1.6x at 10K keys, 4.1x at 1M and 2.0x at 10M.

## Use it when

- Read-only string-to-ID or string-to-offset tables in Go (dictionaries, token or symbol IDs, feature-name indexes) built at startup or offline, where every queried key is known to be in the set.
- Key sets from about 100K to 10M, where Go's map spills out of cache: the README reports 8.7 vs 46 ns at 1M keys (random order) and 4.1x in its scaling test, at 9.0 vs about 48 bytes/key.
- Memory-constrained services: about 9 bytes/key without keys stored, or 18 bytes/key when you need missing-key detection, against 27-48 bytes/key measured for the Go map.
- Bulk lookups of keys shorter than 32 bytes: MapMany/MapManyInto run 34-47% faster than a loop over Map on an Apple M4 Max and 0-32% faster on a Xeon Gold 6548N (README batch table), and MapManyInto does not allocate.
- Values wider than 64 bits: store an index into a side array; the author's blog measured 11 ns vs 21 ns for map[string][]float32 at 100K keys.

## Skip it when

- The key set changes at runtime: there is no insert or delete, every change means a full rebuild, and construction is slower than filling a Go map (the README says so but gives no figure).
- Callers may pass keys that were never inserted and you use plain ConstMap: it silently returns a wrong value. Use VerifiedConstMap (15 ns, 18 bytes/key at 1M keys) or accept the risk.
- Small or cache-hot working sets: the README measures only 1.2x over 256 repeated queries and about 1.6x at 10K keys, which may not justify a non-standard API.
- Maps far larger than the last-level cache: the margin falls to about 2.0x at 10M keys in the README, and a blog reader measured near-parity at 25M keys on an M3 Max (45.70 vs 47.21 ns) under the older sequential benchmark.
- You need iteration, key recovery, len, or values other than uint64, or mostly-absent lookups with PairedVerifiedConstMap, which the README says is slower than VerifiedConstMap on misses.

## How it is fast

It is a retrieval structure (static function), not a hash table. The binary fuse filter construction (Graf and Lemire, ACM JEA 2022) gives each key three positions in overlapping segments of a uint64 array about 1.125n long, peels the resulting 3-hypergraph to find an order, and fills cells so the XOR of a key's three cells equals its value. A lookup is one XXH64 hash plus a murmur finalizer, three array loads and two XORs, with no key comparison and no probing, and the array is about 9 bytes/key against about 48 for Go's map, so much more of it stays in cache. MapMany hashes blocks of eight keys first, using an amd64/arm64 assembly XXH64 that keeps the primes in registers, so the loads of all eight keys are in flight at once.

## Compared with alternatives

Pick it for Go: it is the only Go entry in this category, and fastconstmap is the same binary-fuse design for CPython/C and reads the same files, so you can build in one language and load in the other. The C++ siblings (frozen, qlibs mph, ConstexprCore/perfect_hash) generate tables at compile time for small keyword sets, while constmap builds at runtime and scales to millions of keys at about 9 bytes/key.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | github.com/cespare/xxhash/v2 v2.3.0 |
| **Minimum toolchain** | Go 1.22 (go.mod); CI tests on current stable Go |
| **Platforms** | any Go target via pure-Go code; amd64 and arm64 get assembly for batched hashing and the paired gather (SSE2/NEON, no CPU feature gate); -tags purego disables it; CI covers linux x64, linux arm64 and macOS |
| **Thread safety** | not documented; from the source, Map and MapMany only read slices that are never modified after construction, so concurrent lookups appear safe |
| **Drop-in for the baseline** | no |

## Gotchas

- ConstMap.Map on a map built from zero keys indexes an empty slice and panics (from the source); VerifiedConstMap and PairedVerifiedConstMap return NotFound instead.
- VerifiedConstMap cannot tell a stored value of 0xFFFFFFFFFFFFFFFF from a missing key, and its false-positive rate is about 2^-64 per the doc comment.
- The seed is mixed in after an unseeded XXH64, so two distinct keys with the same XXH64 make New fail with 'duplicate key hash detected' on every retry; duplicate keys also return an error rather than keeping the last value. This matters for adversarial key sets.
- Construction allocates a temporary map[uint64]uint64 over all keys plus several per-slot scratch arrays, so peak build memory is several times the final \~9 bytes/key.

## Caveats and trade-offs

First-party benchmark by the library author (Daniel Lemire). The code and CPU model are public, but the Go version is not stated. Baseline is Go's built-in map[string]uint64, not C++ std::unordered_map, so this is evidence for the binary-fuse-filter static-map technique, not a direct C++ stdlib win. ConstMap stores no keys and returns an undefined value for absent keys. VerifiedConstMap (15 ns vs 46 ns, about 3.1x) is the semantically comparable variant. The margin depends on cache residency: 1.2x over 256 queries vs 5.3x over the full 1M key set, and about 1.6x at 10K and 2.0x at 10M keys in the Scaling table. Construction is slower than building a Go map, which the README states but does not quantify. The headline table (8.7 vs 46 ns) and the Scaling table (12.5 vs 51.1 ns) differ at the same 1M size. The 2026-03-29 launch blog post reported 7.4 vs 20 ns (about 2.7x) under an earlier methodology; the README switched to random-order lookups on 2026-08-27 (commit d2e538f5).

Immutable: keys must be known at construction time (build-then-query), so it targets static/compile-time-known key sets like std::unordered_map replacements built from a fixed keyword set, not general dynamic maps. Uses a binary-fuse-filter-style construction (\~9 bytes/key) rather than a hash table with separate chaining/open addressing.

## Maintenance

Actively developed (v1.2.0 on 2026-09-17, four tagged releases since March 2026) and Apache-2.0 on GitHub, though pkg.go.dev lists the license as UNKNOWN and hides the API docs; it is a small pure-Go package with one dependency and easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification A, tier now C.
- **Tier reason:** The README's 'Performance gains' and 'Scaling' tables compare ConstMap against Go's map[string]uint64 on a stated Apple M4 Max, and the code is public in constmap_test.go (BenchmarkConstMap, BenchmarkVerifiedConstMap, BenchmarkGoMap, makeQueryOrder, TestLookupAndMemoryTable). Neither the README nor either of Lemire's blog posts states the Go toolchain version, and the README does not say which go test flags produced the headline table. That leaves first-party numbers with partial methodology, which is tier C. The missing Go version matters here because Go 1.24 replaced the built-in map with a Swiss-table design.
- **Verifier notes:** Numbers verified on the README: 8.7/15/46 ns, 9.0/18/48 bytes/key, and 5.3x appear verbatim. The \~3.1x Verified ratio was derived, not stated, and is now marked so. Downgraded A to C because the Go toolchain version is not stated anywhere, including both lemire.me posts, and the record's benchmark-file list omitted constmap_test.go, where the Go-map benchmarks live. Metadata checked via gh: Apache-2.0, 238 stars, last commit 2026-09-17, not archived, not a fork, active.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/lemire/constmap>
  - <https://github.com/lemire/constmap/blob/main/README.md>
  - <https://github.com/lemire/constmap/blob/main/constmap_test.go>
  - <https://github.com/lemire/constmap/blob/main/batch_bench_test.go>
  - <https://github.com/lemire/constmap/blob/main/hashbatch_bench_test.go>
  - <https://github.com/lemire/constmap/blob/main/paired_test.go>
  - <https://github.com/lemire/constmap/blob/main/go.mod>
  - <https://github.com/lemire/constmap/blob/main/.github/workflows/test.yml>
  - <https://github.com/lemire/constmap/commits/main/README.md>
  - <https://lemire.me/blog/2026/03/29/a-fast-immutable-map-in-go/>
  - <https://lemire.me/blog/2026/05/05/mapping-strings-to-float-arrays-in-go-how-fast-can-we-go/>
- **Sources the enricher read:**
  - <https://github.com/lemire/constmap>
  - <https://github.com/lemire/constmap/blob/main/README.md>
  - <https://github.com/lemire/constmap/blob/main/constmap.go>
  - <https://github.com/lemire/constmap/blob/main/mapmany.go>
  - <https://github.com/lemire/constmap/blob/main/paired.go>
  - <https://github.com/lemire/constmap/blob/main/paired_asm.go>
  - <https://github.com/lemire/constmap/blob/main/paired_other.go>
  - <https://github.com/lemire/constmap/blob/main/hashbatch_asm.go>
  - <https://github.com/lemire/constmap/blob/main/hashbatch_other.go>
  - <https://github.com/lemire/constmap/blob/main/constmap_test.go>
  - <https://github.com/lemire/constmap/blob/main/go.mod>
  - <https://github.com/lemire/constmap/blob/main/go.sum>
  - <https://github.com/lemire/constmap/blob/main/LICENSE>
  - <https://github.com/lemire/constmap/blob/main/.github/workflows/test.yml>
  - <https://github.com/lemire/constmap/commits/main>
  - <https://github.com/lemire/constmap/releases>
  - <https://github.com/lemire/constmap/issues/1>
  - <https://github.com/lemire/constmap/issues/3>
  - <https://github.com/lemire/constmap/pull/2>
  - <https://lemire.me/blog/2026/03/29/a-fast-immutable-map-in-go/>
  - <https://lemire.me/blog/2026/05/05/mapping-strings-to-float-arrays-in-go-how-fast-can-we-go/>
  - <https://pkg.go.dev/github.com/lemire/constmap>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/lemire/constmap`) · [data/wave1-phf/enrich/raw/github_com_lemire_constmap.json](../../../data/wave1-phf/enrich/raw/github_com_lemire_constmap.json) (enrichment confidence 0.8)

</details>
