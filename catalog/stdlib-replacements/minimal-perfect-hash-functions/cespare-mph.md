# mph (Go, Hash-Displace-Compress / CHD)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Minimal perfect hash functions](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🔴 abandoned

> Pure-Go static string-to-index table (CHD-style minimal perfect hash); author's 2021 benchmark shows 27% faster lookups than map[string]uint32.

| | |
|---|---|
| **Beats** | Go native map[string]uint32 |
| **Claimed result** | 'Lookups on that dictionary take about 30ns and are 27% faster than a map[string]uint32': BenchmarkTable-12 29.99 ns/op vs BenchmarkTableMap-12 40.92 ns/op (verbatim + derived from page data: 1-29.99/40.92≈27%) |
| **Workload** | Lookups over a 102k-word dictionary using string keys; MPH Table.Lookup (CHD algorithm, Murmur3 hash) vs a Go map[string]uint32, via `go test -bench`. |
| **Metric** | latency |
| **Hardware** | Intel Core i7-8700K |
| **Compiler and flags** | go.mod declares `go 1.17`; the exact Go toolchain version/build flags used for the quoted benchmark run are not stated in the README |
| **Adoption** | 74 stars |
| **Last commit** | 2021-09-01 |
| **Links** | [repository](https://github.com/cespare/mph) · [benchmark](https://github.com/cespare/mph) |

## Verdict

The README's go test -bench run on an Intel i7-8700K (2021; Go toolchain not stated, so the old pre-Swiss-table map) looked up each word of a \~102k-entry /usr/share/dict/words in turn: Table.Lookup took 29.99 ns/op and map[string]uint32 took 40.92 ns/op, 27% less time for mph. A third-party run in issue #3 (2022, Xeon 2.80GHz, 348,454 words) measured 35.4 vs 67.8 ns/op, and nobody has published a run on Go 1.24 or later.

## Use it when

- Read-heavy Go code with a fixed set of string keys known at startup (keywords, routes, dictionary words, enum names), where lookup latency matters and rebuilds are rare.
- Short keys such as dictionary words: all published wins are on word lists (about 102k and 348k words), and the key is hashed twice per lookup.
- Lookups that include absent keys: Lookup compares against the stored key, so a non-member returns ok=false instead of a bogus index.
- When you want a zero-dependency file to vendor: 165 lines of non-test Go in two files, MIT-licensed.
- Toolchains older than Go 1.24, where the built-in map was the pre-Swiss-table design that every published mph benchmark was run against.

## Skip it when

- Keys that change at runtime. The Table is immutable, so any insert or delete means a full rebuild. The README gives 18 ms for 102k words on an i7-8700K, and the PR #4 benchstat shows 32.7 MB and 302k allocations per Build for about 348k words.
- Go 1.24 or later without re-benchmarking. Go 1.24 moved the built-in map to Swiss Tables, which the Go blog says are up to 60% faster on map microbenchmarks. The README's own margin already shrank from 'almost twice as fast' (2016) to 28% (2018) and then 27% (2021).
- Long keys. Each Lookup runs a scalar 32-bit Murmur3 over the whole key twice. Issue #3 measured that hash at 16.3 ns for 50 bytes and 202 ns for 500 bytes on a Xeon.
- Tight memory budgets or very large key sets. Seeds and slots are uncompressed uint32 arrays (roughly 5-10 bytes per key after power-of-two rounding), and the table also keeps the full keys slice. That is far above the 2-3 bits/key of compact MPHFs.
- Non-string keys, or tables you want to persist. Only string keys are supported, and with no serialization the table is rebuilt at every process start.

## How it is fast

Build hashes keys with Murmur3 (seed 0) into about n/4 buckets and sorts the buckets largest-first. For each bucket it searches for a Murmur3 seed that sends all of the bucket's keys to free slots in a power-of-two array. This is the hash-and-displace step of CHD (Belazzougui, Botelho, Dietzfelbinger, ESA 2009) without the compress step. A Lookup is two seeded Murmur3 hashes, two uint32 array reads and one string compare against the stored key, with no probing and no collision chains. The 32-bit Murmur3 is hand-written and reads 4-byte blocks directly from the string bytes via unsafe.

## Compared with alternatives

The other Go entry, dgryski/go-mph, uses one metro hash per query and depends on go-metro, and because it stores no keys an absent key returns an arbitrary index. Pick cespare/mph over it when you need built-in membership checks and zero dependencies. Pick it over C++/Rust MPHFs such as PTHash or PtrHash (2-3 bits/key, scaling to billions of keys) only in pure-Go code with modest key counts where storing the keys is acceptable.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (stdlib sort, reflect, unsafe) |
| **Minimum toolchain** | go.mod declares go 1.17; no generics are used |
| **Platforms** | any Go target in principle; all published results are amd64 (i7-8700K, Skylake laptop, Xeon); the hash does native-endian, possibly unaligned uint32 loads through unsafe |
| **Thread safety** | The Table is documented as immutable and Lookup only reads, so concurrent Lookups are safe by construction. Concurrency is not stated explicitly. |
| **Drop-in for the baseline** | partial — it replaces only a read-only map[string]uint32-style index. Values must move to a parallel slice, and there is no insert, delete, range or len. |

## Gotchas

- Duplicate keys make Build loop forever. Two identical keys collide under every seed, and the seed search has no retry limit and no error return.
- Build on an empty slice returns a Table whose Lookup panics with index out of range, because it always reads keys[n] and the slice is empty.
- The Table keeps a reference to the caller's keys slice, not a copy. Modifying that slice after Build silently breaks lookups.
- murmur.go uses the deprecated reflect.SliceHeader/StringHeader to load native-endian uint32 words. Its test vectors are the standard little-endian Murmur3 values, and the repo has no CI, so big-endian and strict-alignment targets are untested.

## Caveats and trade-offs

The README does not state the Go toolchain version or build flags for the quoted ns/op numbers. It gives only the '-12' GOMAXPROCS suffix and the i7-8700K CPU. The numbers were added to the README on 2021-09-01, so they were measured against the Go map that existed before Go 1.24, which replaced the built-in map with a Swiss-table design. The 27% gap may therefore not hold on current Go. The benchmark reads the host's /usr/share/dict/words, so the key set depends on the machine. The numbers are first-party and have not been reproduced independently.

Build/construction takes 18ms for a 102k-word dictionary and requires all keys known upfront; the table is read-only after construction; no comparison is given against other Go hash-map variants or sync.Map.

## Maintenance

Abandoned: the last commit and the only tag (v0.1.0) date from 2021-09-01, and a 2022 PR (#4) that switches to xxh3 for \~23% faster lookups is still unmerged. The code is MIT-licensed and 165 lines, so it is easy to vendor and patch.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** Benchmark code is public (mph_test.go: BenchmarkTable vs BenchmarkTableMap, a Go map[string]uint32 over the same dictionary) and the README names the CPU (i7-8700K). The Go toolchain version and build flags are not stated, so this is first-party with partial methodology: C.
- **Verifier notes:** The claim is accurate: the README shows 29.99 ns/op vs 40.92 ns/op, and the derived 27% matches. Only last_commit needed a fix: the record used the repo's pushed_at (2023-01-22), but the newest commit on the only branch (main, 14a3196) is dated 2021-09-01. It is still 'abandoned'. The README numbers and go.mod (`go 1.17`) were added in the same 2021-09-01 commits, but the README never names the toolchain, so compiler_and_flags was left as is.
- **Fields the verifier corrected:** `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/cespare/mph>
  - <https://github.com/cespare/mph/blob/main/README.md>
  - <https://github.com/cespare/mph/blob/main/mph_test.go>
  - <https://github.com/cespare/mph/blob/main/go.mod>
  - <https://github.com/cespare/mph/blob/main/LICENSE.txt>
  - <https://github.com/cespare/mph/commits/main>
  - <https://github.com/cespare/mph/commit/ed7a6385751e73b58f942091445de0831b5d5945>
  - <https://github.com/cespare/mph/commit/14a319693dfae94b633070a124c1f210b310949d>
  - <https://github.com/cespare/mph/commit/ecff71bf0208e9325253df11d1cd0e26c7a7a813>
- **Sources the enricher read:**
  - <https://github.com/cespare/mph>
  - <https://github.com/cespare/mph/blob/main/README.md>
  - <https://github.com/cespare/mph/blob/main/mph.go>
  - <https://github.com/cespare/mph/blob/main/murmur.go>
  - <https://github.com/cespare/mph/blob/main/mph_test.go>
  - <https://github.com/cespare/mph/blob/main/murmur_test.go>
  - <https://github.com/cespare/mph/blob/main/go.mod>
  - <https://github.com/cespare/mph/blob/main/LICENSE.txt>
  - <https://github.com/cespare/mph/issues?q=>
  - <https://github.com/cespare/mph/issues/1>
  - <https://github.com/cespare/mph/pull/2>
  - <https://github.com/cespare/mph/issues/3>
  - <https://github.com/cespare/mph/pull/4>
  - <https://github.com/cespare/mph/commits/main>
  - <https://github.com/cespare/mph/commit/ecff71bf0208e9325253df11d1cd0e26c7a7a813>
  - <https://github.com/cespare/mph/commit/ed7a6385751e73b58f942091445de0831b5d5945>
  - <https://github.com/cespare/mph/commit/862e796>
  - <https://github.com/cespare/mph/commit/96ffc64>
  - <https://github.com/cespare/mph/tags>
  - <https://github.com/cespare/mph/branches>
  - <https://pkg.go.dev/github.com/cespare/mph>
  - <https://pkg.go.dev/github.com/cespare/mph?tab=importedby>
  - <https://github.com/dgryski/go-mph>
  - <https://github.com/dgryski/go-mph/blob/master/mph.go>
  - <https://go.dev/doc/go1.24>
  - <https://go.dev/blog/swisstable>
  - <https://pkg.go.dev/reflect#SliceHeader>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/cespare/mph`) · [data/wave1-phf/enrich/raw/github_com_cespare_mph.json](../../../data/wave1-phf/enrich/raw/github_com_cespare_mph.json) (enrichment confidence 0.85)

</details>
