# xorfilter (Go binary fuse / xor filter reference implementation)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Go` · `Apache-2.0` · 🟢 active

> Pure-Go binary fuse and xor filters: static membership filters at \~9 bits/key (0.39% FPR) vs \~11.5 for Bloom.

| | |
|---|---|
| **Beats** | Bloom filter |
| **Claimed result** | Per the binary fuse filter paper (arXiv:2201.01174) abstract: storage within 13% of the information-theoretic lower bound for binary fuse filters vs 23% for xor filters and 44% for Bloom filters; construction "more than twice as fast" as xor filters (derived from paper abstract, not this repo's own README numbers) |
| **Workload** | Static-set membership filter storage-overhead comparison (binary fuse vs xor vs Bloom filters), evaluated in the companion Journal of Experimental Algorithmics papers |
| **Metric** | memory |
| **Adoption** | 764 stars; used in CockroachDB Pebble, Oracle Coherence Go client, MatrixOne |
| **Last commit** | 2026-01-26 |
| **Links** | [repository](https://github.com/FastFilter/xorfilter) · [benchmark](https://arxiv.org/abs/2201.01174) |

## Verdict

The storage overheads over the information-theoretic minimum (13% binary fuse, 23% xor, 44% Bloom) and the 'more than twice as fast' build vs xor filters come from the authors' C++ fastfilter_cpp runs in JEA 2022 (GCC 10 -O3 -march=native, single-threaded, Intel i7-6700 Skylake, 100M random 64-bit keys), not from this Go code; the paper only says the Go port was checked qualitatively. The Go repo itself has only a README bits-per-key chart and construction benchmarks in PR threads (about 36 M keys/s at 1M keys on an Apple M1), with no head-to-head against a Go Bloom filter.

## Use it when

- Static key sets, or sets rebuilt per batch, in Go: per-SSTable filters in an LSM store (Pebble uses it for sstable table filters), per-segment or per-partition indexes, shipped allow/deny lists.
- Memory-bound deployments of roughly 100k+ keys, where the README's \~9 bits/key (8-bit) and \~18 bits/key (16-bit) figures hold and \~20% less space than a Bloom filter at the same FPR matters.
- Read-heavy concurrent lookups: the built filter is immutable, so many goroutines can call Contains without locks.
- Filters stored on disk or sent over the network: Save/LoadBinaryFuse use a portable little-endian format, and the README says the fingerprint arrays compress with gzip or zstd.
- Services that build many filters: BinaryFuseBuilder reuses scratch slices to cut GC churn. Single-threaded build speed is roughly 28-57 M keys/s depending on CPU and set size (PR #54 benchmarks on M1, AMD Turin, Intel Emerald Rapids and Axion).

## Skip it when

- Sets that grow incrementally or need deletes: there is no Add or Remove, so any change means a full rebuild. A Bloom, cuckoo or quotient filter fits better.
- Paths sensitive to build time or build memory. Building 1M keys allocated about 25 MB for a \~1.1 MB result (PR #48), and Pebble's wrapper budgets \~24 bytes per hash. On the same M1, a cache-line-blocked Bloom built at \~130 M keys/s vs \~36 M keys/s here (PR #48 note).
- Small sets (a few thousand keys or fewer). The code's size factor rises to 1.25n at 10k keys and 1.375n at 1k keys, plus segment rounding, so most of the space edge over Bloom disappears. The paper notes xor filters can be smaller below \~20k keys.
- FP rates other than 2^-8, 2^-16 or 2^-32: the width is fixed by the fingerprint type, and issue #19 (tunable rate) has been open since 2020. Ribbon filters are configurable.
- Lowest possible query latency: in the paper's C++ runs, an AVX2 blocked Bloom filter queried faster than 3-wise binary fuse (one cache line vs three scattered loads).

## How it is fast

Each key maps to three slots in three consecutive segments of a fingerprint array of about 1.125n entries (the binary fuse layout the paper builds from Dietzfelbinger and Walzer's work). Construction 'peels' the resulting 3-hypergraph by repeatedly removing slots that hold a single key, then assigns fingerprints in reverse order so that fp(x) = H[h0] xor H[h1] xor H[h2]. A query is one murmur-style mix, three loads and two xors, with no loop over k hash functions as in a Bloom filter. The Go build buckets keys by segment for cache locality, derives peeling indexes with branchless bit tricks and can reuse scratch buffers (Jan 2026 releases); only the 3-wise variant is implemented (arity is hard-coded to 3), not the paper's denser 4-wise variant (\~8.6 bits/key).

## Compared with alternatives

In Go, pick this for a static key set when you want the production-tested option (Pebble, Oracle Coherence Go client, MatrixOne) at fixed 8- or 16-bit FP rates. Pick go-qfext if you need inserts after the build, ribbonGo if you need arbitrary FP rates or lower space overhead (its README claims \~4.7% over the minimum at r=7, vs \~12.5% here), and xorf or xor_singleheader for the same algorithm in Rust or C.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime (stdlib only; cespare/xxhash and testify are test-only) |
| **Minimum toolchain** | Go 1.22 (go.mod); CI runs Go 1.22.x, plus 1.24.x for the big-endian job |
| **Platforms** | any Go target. CI covers linux, macOS and windows (amd64), linux/386, and ppc64 big-endian under QEMU; Drone builds arm and arm64. The package imports unsafe on every target. |
| **Thread safety** | Built filters are immutable; the README says they are safe for concurrent queries. BinaryFuseBuilder is not documented as goroutine-safe, and filters built through it alias its buffers. |
| **Drop-in for the baseline** | partial — the query semantics match a Bloom filter (no false negatives, Contains(uint64)), but the filter is built once from the full []uint64 of hashes, has no Add or Remove, and its FP rate is fixed at 2^-8, 2^-16 or 2^-32 |

## Gotchas

- NewBinaryFuse, PopulateBinaryFuse8 and Populate may sort and deduplicate your keys slice in place. Pass a copy if you need the original.
- With BuildBinaryFuse, the returned filter's Fingerprints slice belongs to the builder and is overwritten by the next build. Copy it, or use one builder per live filter; Pebble guards its builders with sync.Pool and a mutex.
- LoadBinaryFuse has no integrity check (per the README) and trusts the stored length and segment fields. Corrupted or untrusted input can trigger a huge allocation or an index-out-of-range panic in Contains, so add your own checksum.
- Construction is randomized and returns 'too many iterations' after MaxIterations (1024, a mutable package-level var). Before the Jan 2026 fix (PR #50), some sizes near segment-length boundaries averaged \~110 retries; a 2023 false-negative bug on duplicate-heavy input (issue #35) is fixed. Use v0.5.1 or later. Xor8 has no Save/Load.

## Known shortcomings

- The 13/23/44% space overheads are from the paper; the JEA 2022 paper says the Go port was checked but reports no Go timings.
- No Go-vs-Bloom benchmark in the repo; Go numbers exist only in PRs (\~36M keys/s build on M1), where a blocked Bloom filter builds \~130M keys/s (\~3.6x faster). Build needs \~24 B/key scratch. Static only (no add/delete); FPR fixed at 2^-8/16/32 (tunable-rate issue #19 open since 2020); 3-wise only.
- Gotchas: the keys slice is sorted/deduplicated in place; a builder-built filter aliases builder memory; Load does no validation (can panic or over-allocate); construction can fail with 'too many iterations' (boundary-size retries fixed 2026-01). Below \~10k keys the space advantage over Bloom mostly disappears.

## Caveats and trade-offs

The 13%/23%/44% abstract figures and the Fig. 5 memory results were measured on the authors' C++ code (FastFilter/fastfilter_cpp; GCC 10 -O3 -march=native; Intel i7-6700). The paper says binary fuse filters were ported to Go and verified qualitatively, but it gives no Go numbers. This repo's README states about 9 bits/key (8-bit, 0.39% FP) and about 18 bits/key (16-bit), next to a theoretical bits-per-entry chart (Bloom 1.44 log2(1/eps)). It has no benchmark against a Bloom filter. Blocked Bloom filters still build faster (paper Fig. 4).

Immutable/static filter, must rebuild to add keys; construction needs substantially more temporary memory than the final filter size; no deletion support

## Maintenance

Actively maintained: v0.5.1 was tagged 2026-01-26 after a Dec 2025-Jan 2026 run of build-speed and buffer-reuse PRs, one issue is open, and it is Apache-2.0 with under 1,000 lines of stdlib-only Go, easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The abstract of arXiv:2201.01174 (Journal of Experimental Algorithmics 27, 2022; peer-reviewed; same authors) states the 13%/23%/44% storage figures and the 'more than twice as fast' xor construction. Its Section 4 says the filters were ported to Go and that 'our good results are not specific to our C++ implementations'. The measured numbers come from the C++ fastfilter_cpp code (GCC 10 -O3 -march=native, i7-6700), not from this Go code, so the evidence is B, not A.
- **Verifier notes:** Abstract numbers match exactly. The README confirms the Pebble, Oracle coherence-go-client and MatrixOne usage. Metadata is correct: Apache-2.0, 764 stars, last commit 2026-01-26 (committer date), active, not a fork or archived.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://export.arxiv.org/abs/2201.01174>
  - <https://arxiv.org/pdf/2201.01174>
  - <https://github.com/FastFilter/xorfilter>
  - <https://raw.githubusercontent.com/FastFilter/xorfilter/master/figures/comparison.png>
- **Sources the enricher read:**
  - <https://github.com/FastFilter/xorfilter>
  - <https://github.com/FastFilter/xorfilter/blob/master/README.md>
  - <https://github.com/FastFilter/xorfilter/blob/master/binaryfusefilter.go>
  - <https://github.com/FastFilter/xorfilter/blob/master/binaryfusefilter8.go>
  - <https://github.com/FastFilter/xorfilter/blob/master/xorfilter.go>
  - <https://github.com/FastFilter/xorfilter/blob/master/xorfilter_definitions.go>
  - <https://github.com/FastFilter/xorfilter/blob/master/serialization.go>
  - <https://github.com/FastFilter/xorfilter/blob/master/serialization_le.go>
  - <https://github.com/FastFilter/xorfilter/blob/master/binaryfusefilter_test.go>
  - <https://github.com/FastFilter/xorfilter/blob/master/go.mod>
  - <https://github.com/FastFilter/xorfilter/blob/master/.github/workflows/test.yml>
  - <https://github.com/FastFilter/xorfilter/blob/master/.github/workflows/bigendian.yml>
  - <https://github.com/FastFilter/xorfilter/blob/master/.drone.yml>
  - <https://github.com/FastFilter/xorfilter/issues?q=is%3Aissue>
  - <https://github.com/FastFilter/xorfilter/issues/57>
  - <https://github.com/FastFilter/xorfilter/issues/47>
  - <https://github.com/FastFilter/xorfilter/issues/35>
  - <https://github.com/FastFilter/xorfilter/issues/30>
  - <https://github.com/FastFilter/xorfilter/issues/19>
  - <https://github.com/FastFilter/xorfilter/pull/54>
  - <https://github.com/FastFilter/xorfilter/pull/53>
  - <https://github.com/FastFilter/xorfilter/pull/52>
  - <https://github.com/FastFilter/xorfilter/pull/50>
  - <https://github.com/FastFilter/xorfilter/pull/48>
  - <https://github.com/FastFilter/xorfilter/pull/46>
  - <https://github.com/FastFilter/xorfilter/commits/master>
  - <https://github.com/FastFilter/xorfilter/releases>
  - <https://github.com/cockroachdb/pebble/blob/master/go.mod>
  - <https://github.com/cockroachdb/pebble/blob/master/sstable/tablefilters/binaryfuse/filter.go>
  - <https://export.arxiv.org/api/query?id_list=2201.01174>
  - <https://arxiv.org/pdf/2201.01174>
  - <https://hn.algolia.com/api/v1/search?query=binary%20fuse%20filters&tags=story>
  - <https://news.ycombinator.com/item?id=46658128>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/fastfilter/xorfilter`) · [data/wave6/enrich/raw/github_com_fastfilter_xorfilter.json](../../../data/wave6/enrich/raw/github_com_fastfilter_xorfilter.json) (enrichment confidence 0.8)

</details>
