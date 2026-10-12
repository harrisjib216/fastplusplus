# go-mph (Go, Hash-Displace-Compress)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Minimal perfect hash functions](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🔴 abandoned

> Go hash-and-displace minimal perfect hash for fixed string sets; author reports 25-50% faster index lookups than a Go map.

| | |
|---|---|
| **Beats** | Go native map[K]V |
| **Claimed result** | 'My implementation is about 25% faster than using a regular Go map for 16 keys and 50% faster when testing with the 235,000 entries in /usr/dict/words.' (verbatim from blog post; no raw ns/op table is given for this specific comparison — a separate ns/op table earlier on the same page, 20.4 vs 172 ns/op, benchmarks an unrelated toy multiplicative hash function, not go-mph, and must not be conflated with it) |
| **Workload** | 16-key toy protocol-command lookup table, and the 235,000-word /usr/dict/words dictionary; go-mph (hash/displace MPHF) lookups vs Go's built-in map, as described in the author's Gopher Academy Advent 2017 blog post. |
| **Metric** | latency |
| **Adoption** | 65 stars |
| **Last commit** | 2021-12-17 |
| **Links** | [repository](https://github.com/dgryski/go-mph) · [benchmark](https://blog.gopheracademy.com/advent-2017/mphf/) |

## Verdict

The only go-mph-versus-map evidence is prose in the author's December 2017 Gopher Academy post: about 25% faster than a Go map for 16 keys and 50% faster for the \~235k entries of /usr/dict/words, with no ns/op, Go version, CPU or flags given, against the pre-Swiss-table map that Go 1.24 replaced. The repo's BenchmarkMPH/BenchmarkMap pair compares an unverified index lookup with a map[string]int32 lookup that does compare keys, and the post's 20.4 vs 172 ns/op table measures a toy multiplier hash, not go-mph.

## Use it when

- Static string sets fixed at build time or startup (protocol commands, keywords, dictionary words, ID or enum tables) where you need a key-to-dense-index mapping and keep payloads in a parallel slice.
- Hot read paths where every queried key is guaranteed to be in the set. Skipping the key comparison is safe there, and it is part of where the speed comes from.
- Sets from a few keys up to a few million held in RAM. Construction is linear, and the author reports 100-125 ms for about 235k words.
- Tables you want to precompute and ship. The exported Values/Seeds slices can be serialized, mmapped (the author's suggestion) or generated as Go source, and go-metro reads input little-endian, so hashes match across architectures.
- When you want about 140 lines of MIT-licensed code you can read in full and vendor, rather than a larger MPHF library.

## Skip it when

- Queries that may include unknown keys. Query returns an arbitrary in-range index for them, so you have to keep the keys and compare, which gives back part of the speedup. cespare/mph does that check inside Lookup.
- Key sets that change at runtime. There is no insert or delete, so any change means a full rebuild that needs every key up front.
- Tight memory budgets or very large sets. Values and Seeds together take 8 bytes per power-of-two slot, which is 8-16 bytes per key (about 2 MB for 235k words). PTHash, PtrHash and RecSplit need roughly 2-3 bits per key, and the author's own go-boomphf needs 3.7 bits per key.
- Non-string keys. New accepts only []string, so integer or struct keys must be encoded to strings first.
- Anything that needs a maintained dependency. The repo has no go.mod, no tags, 3 known importers on pkg.go.dev, and a 2025 bug-fix PR that nobody has reviewed.

## How it is fast

It is a simplified, uncompressed form of hash-and-displace from Belazzougui, Botelho and Dietzfelbinger's 'Hash, Displace, and Compress' (CHD), with one bucket per slot chosen by the low bits of a 64-bit MetroHash. For each multi-key bucket, largest first, New brute-forces a seed so that xorshift-multiply(hash+seed) sends every key in the bucket to a free slot, while single-key buckets skip the search and store their slot directly as a negative seed. A Query is one MetroHash of the key (avo-generated assembly on amd64 via go-metro, pure Go elsewhere), a bitmask into Seeds, an optional xorshift-multiply, and a load from Values: two array reads, no probing and no key comparison. The arrays are padded to a power of two so the slot comes from a mask instead of a modulo.

## Compared with alternatives

Pick go-mph over cespare/mph, the other Go CHD-style entry, when you need to serialize or code-generate the table (cespare's fields are private) or every key is known to be present, since go-mph then does one full-key hash and no string compare per query where cespare does two Murmur3 hashes and a compare. Pick cespare/mph when absent keys are possible, and PTHash, PtrHash or RecSplit (about 2-3 bits/key) when memory or scale matters more than staying in pure Go.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | github.com/dgryski/go-metro (MetroHash64, MIT) |
| **Minimum toolchain** | Not documented. There is no go.mod, so it resolves to pseudo-version v0.0.0-20211217222804-81a8625fb7ed. The code uses sort.Slice (Go 1.8+). go-metro's amd64 stub file carries only a //go:build constraint, so Go 1.17+ is the safe floor. |
| **Platforms** | Any Go target. MetroHash runs as avo-generated assembly on amd64 with the gc compiler (unless the purego or noasm tag is set) and as pure Go elsewhere. No results are published for any platform. |
| **Thread safety** | Not documented. New builds a fresh Table and Query only reads the Seeds and Values slices, so concurrent Queries on a finished Table look safe from the source. |
| **Drop-in for the baseline** | partial — it replaces only a read-only map[string]int-style index in which every queried key is known to be present. Query returns an index rather than a value, has no ok result, and the table cannot be modified. |

## Gotchas

- Duplicate keys make New hang. Two identical keys always hash to the same slot, so the seed search for their bucket can never succeed, and it has no iteration cap or error return. Deduplicate first; the open PR #7 adds a duplicate check.
- Query derives its mask from len(Values), so a hand-built or deserialized Table needs equal-length, power-of-two Values and Seeds. A zero-value Table panics with index out of range.
- Open PR #7 (Aug 2025, unmerged, no reproducer) reports occasional out-of-bounds panics in Query's negative-seed (singleton) branch. The root cause is not documented.
- A persisted table only works with the same hash: go-metro's MetroHash64 with seed 0. Swapping the hash, as PR #7 does with xxhash, invalidates saved tables.

## Caveats and trade-offs

The 25%/50% figures are prose claims in a 2017 blog post, with no raw numbers, CPU model, or Go version for this comparison. The benchmark code exists in mph_test.go (BenchmarkMPH vs BenchmarkMap; -keys flag loads a word file), but the repo publishes no results. The benchmark does not compare equal work. Table.Query returns an index for any input and does not verify key membership, while a map lookup does compare the key. The baseline was Go's 2017 map, and Go 1.24 replaced it with a Swiss-table map, so the margin may differ today. The 20.4 vs 172 ns/op table on the same page benchmarks the toy hash2 multiplier function, not go-mph.

Construction for the 235k-word set takes 100-125ms and needs all keys upfront; uses 8 bytes/entry (index + seed), far more than the same author's companion project go-boomphf (\~3.7 bits/entry), which trades speed (only 'a tiny bit faster than a regular Go map') for much lower memory use.

## Maintenance

Abandoned: the last commit (2021-12-17) was a test-name tweak, the author's own 2018 serialization and space-optimization issues are still open, and an Aug 2025 fix PR is unreviewed, but it is a single 140-line MIT file (plus the MIT go-metro) that is easy to vendor and patch.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The author's own blog post states the result in prose: 25% faster than a Go map for 16 keys and 50% faster for 235,000 /usr/dict/words entries. The post gives no raw numbers, Go version, or CPU. The repo has BenchmarkMPH and BenchmarkMap in mph_test.go, but no results are published, so the evidence is first-party with partial methodology.
- **Verifier notes:** The verbatim quote and the attribution of the ns/op table in the record are both correct. The ns/op table measures hash2 with a brute-forced multiplier, not go-mph. MIT license, 65 stars, last commit 2021-12-17 (abandoned) and non-fork status verified via gh.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://blog.gopheracademy.com/advent-2017/mphf/>
  - <https://github.com/dgryski/go-mph>
  - <https://github.com/dgryski/go-mph/blob/master/mph_test.go>
  - <https://github.com/dgryski/go-mph/blob/master/mph.go>
  - <https://github.com/dgryski/go-mph/blob/master/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/dgryski/go-mph>
  - <https://github.com/dgryski/go-mph/blob/master/README>
  - <https://github.com/dgryski/go-mph/blob/master/mph.go>
  - <https://github.com/dgryski/go-mph/blob/master/mph_test.go>
  - <https://github.com/dgryski/go-mph/blob/master/LICENSE>
  - <https://github.com/dgryski/go-mph/commits/master>
  - <https://github.com/dgryski/go-mph/issues?q=>
  - <https://github.com/dgryski/go-mph/issues/1>
  - <https://github.com/dgryski/go-mph/issues/2>
  - <https://github.com/dgryski/go-mph/issues/4>
  - <https://github.com/dgryski/go-mph/pull/7>
  - <https://blog.gopheracademy.com/advent-2017/mphf/>
  - <https://github.com/dgryski/go-metro>
  - <https://github.com/dgryski/go-metro/blob/master/README>
  - <https://github.com/dgryski/go-metro/blob/master/LICENSE>
  - <https://github.com/dgryski/go-metro/blob/master/metro64.go>
  - <https://github.com/dgryski/go-metro/blob/master/metro_stub.go>
  - <https://github.com/dgryski/go-metro/blob/master/asm.go>
  - <https://github.com/cespare/mph>
  - <https://github.com/cespare/mph/blob/main/README.md>
  - <https://github.com/cespare/mph/blob/main/mph.go>
  - <https://github.com/cespare/mph/blob/main/go.mod>
  - <https://pkg.go.dev/github.com/dgryski/go-mph?tab=importedby>
  - <https://go.dev/doc/go1.24>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/dgryski/go-mph`) · [data/wave1-phf/enrich/raw/github_com_dgryski_go_mph.json](../../../data/wave1-phf/enrich/raw/github_com_dgryski_go_mph.json) (enrichment confidence 0.8)

</details>
