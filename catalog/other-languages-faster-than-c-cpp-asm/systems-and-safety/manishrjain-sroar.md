# sroar

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Go` · `Apache-2.0` · 🔴 abandoned

> Go Roaring bitmaps stored as one byte slice, no marshalling; beats Go roaring64 v0.6.1 FastOr, not 32-bit Go roaring.

| | |
|---|---|
| **Beats** | CRoaring (C): not compared; the README compares against RoaringBitmap/roaring (Go, roaring64 v0.6.1) |
| **Claimed result** | No CRoaring comparison. Against Go roaring64 (README): 6.5x faster (-85% p50) for benchmarks over 1 ms, 15x less memory for allocations over 1 MB, 25x fewer allocations; census1881 302 ms to 2 ms (-99.29%), wikileaks-noquotes 76.5 ms to 0.9 ms (-98.83%), dimension_033 55.0 ms to 2.7 ms (-95.16%); slower on three of twelve data sets: weather_sept_85 +78.52%, uscensus2000 +42.17%, census-income_srt +279.09%. |
| **Workload** | FastOr over the Roaring real-data sets (census1881, wikileaks-noquotes, dimension_xxx, weather_sept_85 and others) with roaring64, Go benchmarks run serially. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen Threadripper 2950X 16-core |
| **Compiler and flags** | Go benchmarks: go test -bench BenchmarkRealDataFastOr --run=XXX --count=5 --benchmem; Go version unstated (go.mod says go 1.16). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | Serialized layout: the in-memory representation is the on-disk byte slice, so operations avoid allocations and marshalling (25x fewer allocations); only array and bitmap containers are implemented. |
| **Adoption** | 0 stars on this fork; dgraph-io/sroar has 277 stars and used in Dgraph |
| **Last commit** | 2022-05-27 |
| **Links** | [repository](https://github.com/dgraph-io/sroar) · [benchmark](https://github.com/manishrjain/sroar) |

## Verdict

The README's 6.5x (p50, benchmarks over 1 ms) figure compares sroar FastOr on twelve Roaring real-data sets against Go RoaringBitmap/roaring roaring64 v0.6.1 on a Threadripper 2950X with an unstated Go version; the sroar column (benchmarks/sroar.txt) was re-run on 2021-12-09 while the roaring64 column (roar64.txt) dates from a 2021-05-18 run whose harness is no longer in the repo, so it is a cross-run comparison, and no C or C++ baseline was measured.

## Use it when

- Go services that persist or ship many bitmaps (posting lists, inverted indexes) and want zero-copy load from mmap or a network buffer, as Dgraph did
- Unions over many 64-bit bitmaps where the Go roaring64 v0.6.1 FastOr allocated hundreds of MB per call (census1881 585 MB/op against 1.4 MB/op for sroar)
- Workloads where GC pressure from many small container objects matters more than raw set-operation speed
- Read-mostly bitmaps loaded with FromBuffer and queried in place

## Skip it when

- If your values fit in 32 bits: the repo's own benchmarks/roar32.txt (same FastOr real-data harness, same machine) has 32-bit Go roaring faster than sroar on 11 of 12 data sets, e.g. dimension_003 2.10 ms vs 11.66 ms and weather_sept_85_srt 0.48 ms vs 2.71 ms (derived from page data)
- Run-heavy data, since there are no run containers; even against roaring64, FastOr is 1.4x to 3.8x slower on three of twelve sets (uscensus2000, weather_sept_85, census-income_srt)
- When you need interoperability with CRoaring, Java or Go roaring files: the byte layout is sroar-specific and in host byte order
- New projects wanting maintenance: dgraph-io/sroar was archived 2024-07-18 and this fork's last commit is 2022-05-27; the weaviate/sroar fork (234 commits, go 1.21) is the live line
- When you need a C or C++ library: there is no measurement against CRoaring at all

## How it is fast

FastOr first sums per-key container cardinalities across all inputs, pre-creates every key, then lays out full 8 KiB bitmap containers before sized array containers at the tail of the buffer, so the union is written into pre-sized space with lazy cardinality and almost no allocation (9 to about 60 allocs per op, against up to 54,500 for roaring64 on census1881). Containers are array or bitmap only (no run containers), stored inline in the flat buffer; growth shifts the tail with copy (scootRight) instead of allocating new container objects.

## Compared with alternatives

Pick sroar over its Zig sibling zroar (same author, same serialized-Roaring design, measured against CRoaring 5.0.0) only when you are in Go and need the buffer-is-the-bitmap layout; for a measured win over a C baseline use zroar, and for maintained Go code use the weaviate/sroar fork.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | github.com/pkg/errors at runtime; RoaringBitmap/roaring v0.6.1 and testify only for tests and benchmarks |
| **Minimum toolchain** | Go 1.16 per go.mod; uses //go:linkname to the unexported runtime.memclrNoHeapPointers and reflect.SliceHeader casts, so newer Go releases may reject or warn |
| **Platforms** | Any Go platform in principle; buffers are reinterpreted with unsafe casts and no endian conversion, so the serialized form is only portable between hosts of the same byte order; benchmarks only on x86-64 (Threadripper 2950X) |
| **Thread safety** | not documented; no internal locking, so concurrent mutation is unsafe; FastParOr runs FastOr on bitmap groups in separate goroutines and merges the results |
| **Drop-in for the baseline** | no |

## Gotchas

- Memclr (exported, utils.go) passes len(b) of a []uint16 as the byte count to runtime.memclrNoHeapPointers, so it zeroes only the first half of the slice; internal callers appear to tolerate it (array containers are bounded by their stored cardinality and toBitmapContainer re-clears with copy from a zero slice), and I found no wrong result, but any outside caller of sroar.Memclr gets a half-cleared slice.
- FromBuffer aliases the caller's []byte (its doc says modifying the bitmap may corrupt the buffer; use FromBufferWithCopy to write), and FastOr with a single argument returns that same bitmap rather than a copy.
- Importing the package allocates a 16&lt;&lt;20-element []uint16 (32 MiB) global zero slice named empty.
- Bitmap-container Maximum() bug reported in dgraph-io/sroar PR #33 (2023-03-13) was closed unmerged when the repo was archived; the same fix was merged as weaviate/sroar#5, not here.

## Known shortcomings

- Off-baseline: no CRoaring or C++ comparison, only the Go roaring64 library, with three FastOr slowdowns. This URL is a personal fork; the canonical repository is dgraph-io/sroar (go.mod module, 277 stars, archived 2024-07-18).
- Enricher: the README's 6.5x compares sroar.txt (rerun 2021-12-09) against roar64.txt (2021-05-18), a cross-run comparison whose roaring64 harness is no longer in the repo; the repo's own roar32.txt (32-bit Go roaring, same harness) is faster than sroar on 11 of 12 datasets (dimension_003 2.10 vs 11.66 ms), so the win is only against roaring64 v0.6.1's allocation-heavy FastOr. Latent bug: exported Memclr passes len([]uint16) as a byte count and zeroes half; the README command lacks the needed -tags real; the Maximum() fix (PR #33) was never merged. A maintained fork exists at weaviate/sroar.

## Caveats and trade-offs

Recorded at D: the lead said to record only a CRoaring comparison and none exists; the numbers above are against the Go library, not a C or C++ baseline. This URL is a fork of the archived upstream dgraph-io/sroar (archived 2024-07-18, 277 stars, 47 forks, same 84 commits; the fork's last commit is 2022-05-27), and go.mod still declares module github.com/dgraph-io/sroar, so the canonical record should probably use the dgraph-io URL. Raw benchmark outputs are in benchmarks/; the README names the CPU (AMD Ryzen Threadripper 2950X 16-Core) but not the Go version. FastOr only, not And or other operations, and run containers are not implemented. The 6.5x median figure covers only benchmarks over 1 ms and hides three slowdowns (weather_sept_85 +78.52%, uscensus2000 +42.17%, census-income_srt +279.09%); memory use also rises on dimension_033, uscensus2000 and weather_sept_85. [retier] Enricher: the 6.5x pits a 2021-12-09 sroar run against a 2021-05-18 roaring64 run whose harness is gone; the repo's roar32.txt (same harness) is faster than sroar on 11 of 12 datasets; exported Memclr zeroes only half the slice; Maximum() fix PR #33 unmerged.

Only array and bitmap containers (no run containers, which Roaring has); in-memory layout equals the on-disk layout (a byte slice) so no marshal or unmarshal step; designed for Dgraph's many-bitmap workload.

## Maintenance

Abandoned: a 2022-05-27 fork of dgraph-io/sroar (archived 2024-07-18, go.mod still names github.com/dgraph-io/sroar) under Apache-2.0; the headline numbers are a cross-run comparison against roaring64 only, and the repo's own roar32.txt shows 32-bit Go roaring faster than sroar on 11 of 12 data sets, so treat the speedup as a fix for roaring64 v0.6.1's allocation-heavy FastOr rather than a general win; reproducing it on HEAD also needs -tags real (real_data_test.go carries a 'real' build tag the README command omits).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now D.
- **Tier reason:** The README benchmark (go test -bench BenchmarkRealDataFastOr, Threadripper 2950X, numbers matching the record) compares sroar only with the Go RoaringBitmap/roaring roaring64 library; neither this fork nor the dgraph-io upstream has any CRoaring or other C/C++ measurement, so there are no numbers against the wave's C/C++ baseline.
- **Verifier notes:** README numbers and metadata are accurate: Apache-2.0, 0 stars, a fork of dgraph-io/sroar, last commit 2022-05-27, and the census1881, wikileaks-noquotes and dimension_033 rows all match. Shortcoming: off-baseline. There is no C or C++ comparison, only Go roaring64, and the win comes from a serialized, allocation-free layout rather than from the language. Consider a repo_url override to https://github.com/dgraph-io/sroar (the canonical upstream, archived 2024-07-18), which is not yet in the catalog. I dropped the 'author's desktop' wording from the caveats because the README does not say that.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-113 (wave 14 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/manishrjain/sroar>
  - <https://raw.githubusercontent.com/manishrjain/sroar/HEAD/README.md>
  - <https://github.com/manishrjain/sroar/commits>
  - <https://raw.githubusercontent.com/manishrjain/sroar/HEAD/go.mod>
  - <https://github.com/dgraph-io/sroar>
- **Sources the enricher read:**
  - <https://github.com/manishrjain/sroar>
  - <https://raw.githubusercontent.com/manishrjain/sroar/HEAD/README.md>
  - <https://raw.githubusercontent.com/manishrjain/sroar/HEAD/go.mod>
  - <https://raw.githubusercontent.com/manishrjain/sroar/HEAD/real_data_test.go>
  - <https://raw.githubusercontent.com/manishrjain/sroar/HEAD/benchmark_test.go>
  - <https://raw.githubusercontent.com/manishrjain/sroar/HEAD/bitmap.go>
  - <https://raw.githubusercontent.com/manishrjain/sroar/HEAD/container.go>
  - <https://raw.githubusercontent.com/manishrjain/sroar/HEAD/utils.go>
  - <https://raw.githubusercontent.com/manishrjain/sroar/HEAD/keys.go>
  - <https://raw.githubusercontent.com/manishrjain/sroar/HEAD/setutil.go>
  - <https://github.com/manishrjain/sroar/tree/main/benchmarks>
  - <https://raw.githubusercontent.com/manishrjain/sroar/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/manishrjain/sroar/HEAD/benchmarks/sroar.txt>
  - <https://raw.githubusercontent.com/manishrjain/sroar/HEAD/benchmarks/roar32.txt>
  - <https://raw.githubusercontent.com/manishrjain/sroar/HEAD/benchmarks/roar64.txt>
  - <https://raw.githubusercontent.com/manishrjain/sroar/HEAD/benchmarks/roar64-serial.txt>
  - <https://github.com/manishrjain/sroar/commits/main/benchmarks>
  - <https://github.com/manishrjain/sroar/commit/fbc00eaa0f325e86a27e21c62f08cc13c8fda6da>
  - <https://github.com/dgraph-io/sroar/issues?q=is%3Aissue>
  - <https://github.com/dgraph-io/sroar/pulls?q=is%3Apr>
  - <https://github.com/dgraph-io/sroar/pull/33>
  - <https://github.com/weaviate/sroar>
  - <https://raw.githubusercontent.com/weaviate/sroar/HEAD/utils.go>
  - <https://raw.githubusercontent.com/weaviate/sroar/HEAD/go.mod>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/manishrjain/sroar`) · [data/wave14/enrich/raw/github_com_manishrjain_sroar.json](../../../data/wave14/enrich/raw/github_com_manishrjain_sroar.json) (enrichment confidence 0.8)

</details>
