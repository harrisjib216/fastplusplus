# go-qfext (Facebook Quotient Filter for Go)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🟡 stale

> Pure-Go quotient filter that keeps full 64-bit hashes plus optional per-key integers; about 3.6x faster positive lookups than bits-and-blooms/bloom.

| | |
|---|---|
| **Beats** | Bloom filter (bits-and-blooms/bloom v3 Go implementation) |
| **Claimed result** | Lookup: unpacked quotient filter 20.43 ns/op and packed 30.95 ns/op vs bits-and-blooms/bloom v3 Bloom filter 74.47 ns/op, about 3.6x and 2.4x faster (derived from page data). The README text itself says "about 4 times faster". A native Go map lookup is shown for reference at 9.373 ns/op. |
| **Workload** | go test -bench lookup benchmark: quotient filter Contains() (unpacked and bit-packed variants) vs a popular Go Bloom filter library |
| **Metric** | latency |
| **Hardware** | Apple M1, MacBook Pro (13-inch, 2020) |
| **Compiler and flags** | Go toolchain, version not stated (go.mod declares go 1.20); `go test -run=xxx -bench=.` with default build flags |
| **Adoption** | 96 stars |
| **Last commit** | 2025-09-25 |
| **Links** | [repository](https://github.com/facebookincubator/go-qfext) · [benchmark](https://github.com/facebookincubator/go-qfext#performance---compute) |

## Verdict

The claim rests on one README go test -bench run on an Apple M1 MacBook Pro (Go version unstated, numbers from August 2021): positive Contains lookups took 20.43 ns/op unpacked and 30.95 ns/op packed, against 74.47 ns/op for bits-and-blooms/bloom v3.0.1 built with NewWithEstimates(273, 0.0001). That is about 3.6x and 2.4x faster, not the README's 'about 4 times'. The test set is 273 short strings (163 distinct), so both structures sit in L1 cache (Bloom about 0.65 KB with 14 probes, unpacked filter 4 KB), and the filter runs at a far lower false-positive rate than the Bloom filter it is compared with.

## Use it when

- Go services that check many string or byte keys against a large set built offline (the README targets 'large models that are expensive to generate') and want essentially no false positives: the error rate is only the 64-bit hash-collision rate.
- You need a small integer per key (an ID, a class, a shard number) returned by the same probe. External storage added about 5 ns in the README run (25.59 vs 20.43 ns/op).
- Sets that grow incrementally to an unknown final size. The table doubles at 65% load and rehashes losslessly because the full hash is kept, with no need to size it up front.
- Replacing a map[string]struct{} used only for membership over many long keys. Slots hold hash bits, not the key bytes, but lookups were about 2.2x slower than a Go map in the README run (20.43 vs 9.37 ns/op).
- RAM-starved, read-mostly deployments that can accept slow lookups. OpenReadOnlyFromPath opened a 2 MB filter in about 9 µs (README) and serves lookups with pread instead of loading the file.

## Skip it when

- Memory-tight approximate filtering. The remainder width is fixed at 64-q bits and load stays between 32.5% and 65%, so the README's own 1-billion-key example needs 9 GB packed (about 77 bits/key), and the unpacked form uses a full 64-bit word per slot. By the bloom package's own sizing formula, a Bloom filter needs about 19 bits/key at 1e-4 FPR and about 10 bits/key at 1%.
- You need deletion, merging or counting: the filter has no Delete, Remove or Merge API.
- Disk-backed lookups on a hot path. Disk makes one pread per slot probed, allocates a buffer per read in packed mode, panics on I/O errors, and has no mmap option (issue #7, open since 2020). No Disk lookup timings are published, and the 'packed' disk benchmark helper ignores its packed argument.
- Large DRAM-resident sets, or workloads dominated by misses, where you need evidence. The only published numbers are positive lookups over 163 distinct keys in a 4 KB table.
- Teams that need an active upstream. After the August 2021 README update the only changes are a September 2025 unsafe/ASAN cleanup and a yaml bump, three issues from 2018-2020 have no replies, and pkg.go.dev lists a single importer (an internal Tencent BlueKing package).

## How it is fast

It is a classic quotient filter. The top q bits of a 64-bit MurmurHash64A (seed 0, inlined) pick a home bucket, the remaining 64-q bits are stored as the remainder, and 3 metadata bits per slot (occupied, continuation, shifted) encode sorted runs in neighbouring slots, like linear probing. A lookup is one hash plus usually one or a few adjacent slot reads. In the benchmark's configuration (1e-4 FPR) a bits-and-blooms Bloom lookup instead runs two murmur3-128 passes and tests k=14 bit positions, each reduced modulo a non-power-of-two m. The unpacked mode keeps each slot in a whole uint64 so a slot read is plain array indexing; the packed mode bit-packs slots at 67-q bits to save memory, and it was about 50% slower in the README run.

## Compared with alternatives

The closest Go sibling is ribbonGo, a static filter at about 7.3 bits/key. Pick go-qfext instead when keys arrive incrementally, you want an integer payload per key, or you need practically zero false positives and can afford roughly 10x the bits per key (about 77 vs 7.3). For C/C++ or counting workloads, the Counting Quotient Filter (splatlab/cqf) is the more complete quotient-filter implementation.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime (the library imports only the Go standard library); go.mod also pulls aviddiviner/go-murmur, bits-and-blooms/bloom/v3 and testify for tests, and urfave/cli/v2 for the cmd tool |
| **Minimum toolchain** | Go 1.20 (go.mod; the code uses unsafe.StringData and unsafe.SliceData) |
| **Platforms** | any Go target: pure Go, no assembly or SIMD. The serialized format is little-endian, so big-endian hosts take a slower byte-swapping path, and the packed Disk reader's big-endian branch indexes raw[cnt\*8:(cnt+1)\*8] with cnt instead of i, so it looks broken. |
| **Thread safety** | Not documented. The code has no locks. Lookups on a Filter only read, so concurrent reads of a filter nobody is inserting into look safe from the code. Insert mutates slots and may replace the whole table while doubling, so writers need external synchronization. Disk reads through ReadAt on an \*os.File. |
| **Drop-in for the baseline** | partial: it fills the same role as bloom.BloomFilter (add and test byte slices or strings), but it uses New/NewWithConfig and InsertString/ContainsString instead of NewWithEstimates and AddString/TestString. It takes no FPR or size-in-bits parameters, has no Merge or deletion, and uses its own file format. |

## Gotchas

- The package name is qf, not qfext. The README snippet calling qfext.New() compiles only with the import alias that example/example.go uses.
- Filter.ReadFrom ignores the header's BitPacked flag, and HashFn is never persisted. Build the receiving Filter with the same BitPacked and HashFn as the writer. OpenReadOnlyFromPath always uses the built-in murmur hash (the code has an 'XXX: handle variable hash functions' comment), so a filter built with a custom HashFn gives wrong answers from disk without any error.
- ReadFrom reads each vector with a single io.Reader.Read call and never checks the byte count. On Unix, Go's os.File.Read returns at most 1 GiB per call (internal/poll maxRW), so loading a multi-GB filter straight from an \*os.File can be silently truncated. Use a reader that fills the whole buffer (io.ReadFull semantics), or use Disk.
- Packed vectors panic, rather than return an error, when a stored value is wider than BitsOfStoragePerEntry; unpacked vectors store it silently. Disk lookups also panic on read errors.

## Known shortcomings

- Go version unstated; the 3.6x/2.4x are derived from page data and the README's '4x' overstates them.
- Weak benchmark: 163 unique keys (the table fits in L1), positive lookups only, and the Bloom filter set to 1e-4 FPR (14 probes per lookup). Memory-heavy: stores the full 64-bit hash with non-tunable FPR, about 77 bits/key packed vs \~19 for Bloom (the README's 1B-key example needs 9 GB). No delete or merge; the disk reader does one pread per slot and panics on I/O error (no mmap, issue #7 open since 2020).
- Bugs: ReadFrom never checks read length, so filters over 1 GiB loaded from a file can silently truncate; disk mode always uses the built-in hash, so custom-hash filters answer wrongly; ReadFrom ignores the packed flag; the README example does not compile (package is named qf). Stale since 2021 apart from a 2025-09 cleanup.

## Caveats and trade-offs

Single first-party go test run on one laptop (Apple M1), with no repeated trials or variance and no Go version stated; the README numbers date from an August 2021 README update. The benchmark only does positive lookups, cycling through keys that were all inserted. The Bloom filter is built with bloom.NewWithEstimates(n, 0.0001). The baseline is one third-party Go library (bits-and-blooms/bloom v3.0.1), not a canonical C/C++ implementation. The README's own "about 4 times faster" wording overstates the measured 3.6x.

Static/quotient-hash structure; bit-packing trades speed for memory; designed for large pre-built models loaded from disk, not a general dynamic set

## Maintenance

Stale: essentially unchanged since 2021 apart from a September 2025 unsafe/ASAN cleanup and dependency bump, but it is MIT-licensed, standard-library-only and about 1,400 lines, so it is easy to vendor and patch.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now C.
- **Tier reason:** The README has first-party go test numbers from public benchmark code (qf_test.go BenchmarkBloomFilter / BenchmarkUnpackedFilterLookup / BenchmarkPackedFilterLookup, against bits-and-blooms/bloom/v3 v3.0.1) on an Apple M1. The Go toolchain version is never stated (go.mod only declares go 1.20), so methodology is partial. That matches the earlier ribbongo precedent, which was tiered C for unstated Go version.
- **Verifier notes:** The numbers match the README exactly. I downgraded A to C because the compiler (Go version) is unstated and ribbongo was tiered C on the same grounds. Metadata checks out: MIT, 96 stars, not a fork, last commit 2025-09-25, which is just over 12 months before today, so stale.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/facebookincubator/go-qfext>
  - <https://github.com/facebookincubator/go-qfext#performance---compute>
  - <https://github.com/facebookincubator/go-qfext/blob/main/qf_test.go>
  - <https://github.com/facebookincubator/go-qfext/blob/main/go.mod>
- **Sources the enricher read:**
  - <https://github.com/facebookincubator/go-qfext>
  - <https://github.com/facebookincubator/go-qfext#performance---compute>
  - <https://github.com/facebookincubator/go-qfext/blob/main/qf.go>
  - <https://github.com/facebookincubator/go-qfext/blob/main/config.go>
  - <https://github.com/facebookincubator/go-qfext/blob/main/hash.go>
  - <https://github.com/facebookincubator/go-qfext/blob/main/packed.go>
  - <https://github.com/facebookincubator/go-qfext/blob/main/unpacked.go>
  - <https://github.com/facebookincubator/go-qfext/blob/main/disk.go>
  - <https://github.com/facebookincubator/go-qfext/blob/main/serialize.go>
  - <https://github.com/facebookincubator/go-qfext/blob/main/util.go>
  - <https://github.com/facebookincubator/go-qfext/blob/main/vector.go>
  - <https://github.com/facebookincubator/go-qfext/blob/main/reader.go>
  - <https://github.com/facebookincubator/go-qfext/blob/main/qf_test.go>
  - <https://github.com/facebookincubator/go-qfext/blob/main/packed_test.go>
  - <https://github.com/facebookincubator/go-qfext/blob/main/go.mod>
  - <https://github.com/facebookincubator/go-qfext/blob/main/cmd/main.go>
  - <https://github.com/facebookincubator/go-qfext/blob/main/example/example.go>
  - <https://github.com/facebookincubator/go-qfext/commits/main>
  - <https://github.com/facebookincubator/go-qfext/issues?q=is%3Aissue>
  - <https://github.com/facebookincubator/go-qfext/issues/7>
  - <https://github.com/facebookincubator/go-qfext/issues/2>
  - <https://github.com/facebookincubator/go-qfext/issues/3>
  - <https://github.com/facebookincubator/go-qfext/issues/1>
  - <https://github.com/facebookincubator/go-qfext/pull/10>
  - <https://raw.githubusercontent.com/bits-and-blooms/bloom/v3.0.1/bloom.go>
  - <https://raw.githubusercontent.com/bits-and-blooms/bloom/v3.0.1/murmur.go>
  - <https://raw.githubusercontent.com/golang/go/master/src/internal/poll/fd_unix.go>
  - <https://pkg.go.dev/github.com/facebookincubator/go-qfext?tab=importedby>
  - <https://hn.algolia.com/api/v1/search?query=go-qfext>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/facebookincubator/go-qfext`) · [data/wave6/enrich/raw/github_com_facebookincubator_go_qfext.json](../../../data/wave6/enrich/raw/github_com_facebookincubator_go_qfext.json) (enrichment confidence 0.86)

</details>
