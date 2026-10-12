# Ribbon Filter (ribbonGo)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🟢 active

> Pure-Go static Ribbon filter (Dillinger-Walzer 2021) storing 7.3-7.5 bits/key at 0.78% FPR, below textbook Bloom and Xor sizes.

| | |
|---|---|
| **Beats** | Bloom filter, xor filter |
| **Claimed result** | README: w=128 at n=1e6 stores 7.334 bits/key (4.749% over the 7-bit minimum for r=7). It compares this with Bloom's 9.6 bits/key 'at the same FPR' and claims a 23.6% space saving. The 9.6 bits/key is the analytical Bloom value at 1% FPR, not a measured Bloom run, and r=7 actually gives FPR of about 0.78%, so the FPRs are not matched. Build is 106.3 ns/key (Apple M3 Pro). Query at n=1e6 is 43.2/31.7 ns/op positive/negative (x86 Xeon Platinum). At n=1e8, w=128 reaches 7.512 bits/key (7.314% overhead). |
| **Workload** | Static approximate-membership filter over n=1e6 and n=1e8 keys, r=7 result bits, following the Dillinger & Walzer (2021) evaluation methodology |
| **Metric** | memory |
| **Hardware** | Build/Space tables on Apple M3 Pro (ARM64); Query table on an x86 Xeon Platinum host (exact CPU model not stated); absolute ns/op not comparable across the two tables |
| **Compiler and flags** | go test -bench (go.mod declares go 1.24.2); the Go toolchain version and flags actually used for the published runs are not stated |
| **Adoption** | 15 stars |
| **Last commit** | 2026-07-17 |
| **Links** | [repository](https://github.com/RibbonFilter/ribbonGo) · [benchmark](https://github.com/RibbonFilter/ribbonGo#benchmarks) |

## Verdict

Only self-measurements from the repo's go test BenchmarkPaper_\* suite with r=7 and sequential 8-byte integer keys, Go version and flags unstated. At w=128, build was 106.3 ns/key at 7.33 bits/key for n=1e6, and 384.7 ns/key at 7.51 bits/key for n=1e8, on an Apple M3 Pro. Queries at n=1e6 were 43.2/31.7 ns positive/negative, a warm-cache loop over 8192 cycled probes on an unnamed Xeon Platinum; no n=1e8 query numbers are published, and the README says only the query table was re-measured after the July 2026 storage-layout change. The Bloom (9.6 bits/key at 1%) and Xor figures are textbook constants, not benchmark runs, and FPRs are not matched: against a Bloom filter at the same 2^-7 FPR (about 10.1 bits/key by the README's 44% figure) the saving would be about 27%, not the quoted 23.6%.

## Use it when

- Go programs (no cgo) that build a filter once over a known, de-duplicated key set of about 1e6-1e8 keys and query it many times in the same process, for example per-snapshot or per-shard membership sets.
- Memory-bound cases at about 0.4-1% FPR. At w=128 the author measured 7.33 bits/key (n=1e6) and 7.51 (n=1e8). The textbook figures, from the README's own overhead percentages applied to 7 bits, are about 8.6 for Xor with 7-bit fingerprints and about 10.1 for Bloom at 2^-7. That is roughly 13-27% smaller.
- Relatively high FPR targets (r=1-8, so 50% down to 0.39%): the Ribbon paper says the design is most competitive for f &gt;= 2^-7.
- Read-heavy services where build time of about 0.1-0.4 microseconds per key is acceptable and queries of about 30-45 ns (warm cache, n=1e6) are fast enough.

## Skip it when

- Sets that grow or change: there is no Add or Delete. Every change is a full rebuild costing 57-385 ns/key in the author's M3 Pro runs, with per-key cost rising at larger n.
- Filters that must be persisted or shipped, such as LSM table blocks or on-disk indexes. No serialization API exists (issue #23 is open). The hash is final XXH3, which the code notes is not byte-compatible with RocksDB's on-disk Ribbon blocks.
- FPR below about 0.39%: ResultBits is capped at 8. The Config comment lists r=10, but validateConfig panics above 8.
- Memory-tight build hosts. Construction holds 8 B/key of stored hashes plus 17 B/slot of banding arrays at w=128 (9 B/slot at w&lt;=64), on top of the caller's key slice. The benchmark file warns of about 8 GB peak at n=1e8, including the test keys.
- Narrow widths at large n. w=32 at n=1e8 used 10.17 bits/key (45% slot overhead, from extrapolated non-RocksDB sizing constants), no better than a textbook Bloom at the same FPR. w=64 at n=1e8 (8.23 bits/key) is only about 4% under textbook Xor.

## How it is fast

Each key is hashed once with XXH3 to 64 bits. That hash is cheaply remixed per seed into a start slot, a w-bit coefficient row and an r-bit fingerprint. The rows form a banded linear system over GF(2), solved by on-the-fly Gaussian elimination (the paper's 'Rapid Incremental Boolean Banding ON the fly') plus back-substitution, retrying with a new seed if banding hits a linear dependence. At w=128, RocksDB's empirical slot tables put the slot count only about 5-7% above n, so storage stays near the r-bits/key minimum. The README puts Bloom at about 44% overhead. The solution is stored in RocksDB's Interleaved Column-Major Layout. A query is one hash plus up to r shift/AND/POPCNT parity checks over two adjacent w-bit words, and it exits on the first mismatched column, so negatives are cheaper than positives.

## Compared with alternatives

Pick it when you need the smallest static filter at about 0.4-1% FPR in pure Go without cgo. If C/C++ is acceptable, BuRR (bumped Ribbon; the Ribbon paper reports load-balanced Ribbon below 1% overhead, against 4.7-7.3% here) or xor_singleheader (simpler, with published head-to-head benchmarks) are stronger picks. The cuckoo-family siblings (Vacuum, Windowed cuckoo) fit better if you need inserts after build.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | github.com/zeebo/xxh3 v1.1.0 (indirect: klauspost/cpuid/v2, golang.org/x/sys) |
| **Minimum toolchain** | Go 1.24.2 per go.mod; CI runs tests on Go 1.25 |
| **Platforms** | Any Go target: the library is pure Go, and the xxh3 dependency ships amd64 SSE2/AVX2/AVX-512 and arm64 NEON assembly with a generic fallback. Published numbers cover arm64 (Apple M3 Pro) and x86-64 (Xeon Platinum); CI runs on ubuntu-latest. |
| **Thread safety** | Documented: Contains is safe for concurrent use once Build has returned. Build swaps the internal filter pointer without synchronization, so rebuilding while other goroutines call Contains is a data race. |
| **Drop-in for the baseline** | false: build-once API over []string with no incremental Add, no delete and no serialization, so it cannot replace a Bloom filter that is filled incrementally or persisted. It fits only where the Bloom/Xor filter was already built from a complete key set in memory. |

## Gotchas

- Keys must be unique, and uniqueness really applies to the 64-bit XXH3 hash. Every seed retry remixes only the stored hash, and the bander rejects even consistent redundant equations. So a duplicate key, or two distinct keys whose 64-bit hashes collide (birthday odds of about n^2/2^65: about 3e-4 at 1e8 keys, about 3% at 1e9), fails every seed. Build then runs all MaxSeeds (default 256) banding attempts before returning ErrConstructionFailed.
- The Config doc comments quote the paper's asymptotic overheads (w=32 about 7.2%, w=64 about 3.6%, w=128 about 1.8%). Measured slot overhead is much higher: 31.8/12.0/4.7% at n=1e6 and 45.3/17.6/7.3% at n=1e8. That is because slot counts follow RocksDB's tables for a 5% per-seed failure rate and grow with log n.
- NewWithConfig and NewFromKeysWithConfig panic, rather than return an error, on an invalid CoeffBits or ResultBits. Keys are []string only; the pre-hashed build path (buildFromHashes) is unexported.
- The README's benchmark commands (-bench='BenchmarkRibbon...') match no benchmark function; the real ones are BenchmarkPaper_Build/Query_Positive/Query_Negative/Space, and -short skips n=1e8. The w&lt;=64 build loop also lacks the prefetch load that the README credits with a 20-36% gain at scale (open issue #42); only the w=128 path has it.

## Known shortcomings

- The Bloom 9.6 bits/key comparison is a textbook constant, not a benchmark; FPRs are not matched (r=7 is about 0.78%).
- Static only: no add/delete and no serialization (issue #23), so it cannot be persisted. At matched 2^-7 FPR a Bloom filter needs \~10.1 bits/key, so the saving is \~27%; the Bloom baseline is never benchmarked (#26). Duplicate keys or a 64-bit XXH3 collision (\~3% at 1e9 keys) make all 256 seeds fail.
- Real slot overhead is 4.7-45% (doc comments say 1.8-7.2%); w=32 at 1e8 keys is no better than Bloom; r&lt;=8 gives an FPR floor of 0.39%; build needs \~25 B/key. The README benchmark command runs no benchmark; query numbers are warm-cache at n=1e6 only; the w&lt;=64 build lacks prefetch (#42).

## Caveats and trade-offs

This is a third-party Go reimplementation of the standard Ribbon filter (Dillinger & Walzer 2021, arXiv:2103.02515; it mirrors RocksDB ribbon_impl.h). It is distinct from BuRR (lorenzhs/BuRR, bumped ribbon retrieval), which is already catalogued, so it is not a duplicate. It is not a fork, and the repo was created 2026-03. The Bloom/Xor comparison is analytical only (a table of textbook bits/key constants); no baseline filter is benchmarked. Build and query figures come from two different hosts. The README's claim of 'at the same FPR' is loose because r=7 gives about 0.78% FPR, while 9.6 bits/key is Bloom's figure at 1%.

Static/immutable once built (no incremental insert), no deletion support, construction cost is higher than Bloom's simple incremental build

## Maintenance

Active but young: created March 2026, v1.0.10 released 2026-07-18 after the ICML storage rewrite, 15 stars, 10 open issues including serialization (#23) and Bloom/Cuckoo/Xor benchmarks (#26). It is MIT-licensed, seven source files and one dependency, so easy to vendor, but not production-proven.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** These are first-party README numbers from the project's own go test benches (ribbon_bench_test.go BenchmarkPaper_\*). The Bloom and Xor figures are textbook constants in a comparison table; no Bloom or Xor filter is benchmarked anywhere in the repo. Methodology is partial: Go version and flags are unpinned, and hardware is given only as 'Apple M3 Pro' and 'x86 Xeon Platinum' with no model. This is not peer-reviewed and not a third-party suite, so C rather than B.
- **Verifier notes:** It is a distinct implementation, not BuRR, and has its own measured numbers for itself only; the baseline side is theoretical. The default branch main was last committed 2026-07-17 (release v1.0.10 on 2026-07-18). The record's 2026-08-01 date comes from the non-default branch DhruvilK7-patch-1, so the repo is still active. MIT license and 15 stars confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `last_commit`, `hardware`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/RibbonFilter/ribbonGo>
  - <https://github.com/RibbonFilter/ribbonGo#benchmarks>
  - <https://raw.githubusercontent.com/RibbonFilter/ribbonGo/main/ribbon_bench_test.go>
  - <https://raw.githubusercontent.com/RibbonFilter/ribbonGo/main/filter_bench_test.go>
  - <https://github.com/RibbonFilter/ribbonGo/blob/main/go.mod>
- **Sources the enricher read:**
  - <https://github.com/RibbonFilter/ribbonGo>
  - <https://github.com/RibbonFilter/ribbonGo#benchmarks>
  - <https://github.com/RibbonFilter/ribbonGo/blob/main/ribbon.go>
  - <https://github.com/RibbonFilter/ribbonGo/blob/main/filter.go>
  - <https://github.com/RibbonFilter/ribbonGo/blob/main/builder.go>
  - <https://github.com/RibbonFilter/ribbonGo/blob/main/hash.go>
  - <https://github.com/RibbonFilter/ribbonGo/blob/main/bander.go>
  - <https://github.com/RibbonFilter/ribbonGo/blob/main/solver.go>
  - <https://github.com/RibbonFilter/ribbonGo/blob/main/uint128.go>
  - <https://github.com/RibbonFilter/ribbonGo/blob/main/go.mod>
  - <https://github.com/RibbonFilter/ribbonGo/blob/main/.github/workflows/ci.yml>
  - <https://github.com/RibbonFilter/ribbonGo/blob/main/ribbon_bench_test.go>
  - <https://github.com/RibbonFilter/ribbonGo/blob/main/filter_bench_test.go>
  - <https://github.com/RibbonFilter/ribbonGo/blob/main/bander_bench_test.go>
  - <https://github.com/RibbonFilter/ribbonGo/blob/main/hash_bench_test.go>
  - <https://github.com/RibbonFilter/ribbonGo/blob/main/solver_bench_test.go>
  - <https://github.com/RibbonFilter/ribbonGo/blob/main/ribbon_test.go>
  - <https://github.com/RibbonFilter/ribbonGo/blob/main/filter_test.go>
  - <https://github.com/RibbonFilter/ribbonGo/issues?q=is%3Aissue>
  - <https://github.com/RibbonFilter/ribbonGo/issues/41>
  - <https://github.com/RibbonFilter/ribbonGo/issues/38>
  - <https://github.com/RibbonFilter/ribbonGo/issues/42>
  - <https://github.com/RibbonFilter/ribbonGo/issues/23>
  - <https://github.com/RibbonFilter/ribbonGo/issues/26>
  - <https://github.com/RibbonFilter/ribbonGo/issues/27>
  - <https://github.com/RibbonFilter/ribbonGo/issues/29>
  - <https://github.com/RibbonFilter/ribbonGo/pulls?q=is%3Apr>
  - <https://github.com/RibbonFilter/ribbonGo/releases>
  - <https://arxiv.org/abs/2103.02515>
  - <https://github.com/zeebo/xxh3>
  - <https://github.com/zeebo/xxh3/tree/v1.1.0>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/ribbonfilter/ribbongo`) · [data/wave6/enrich/raw/github_com_ribbonfilter_ribbongo.json](../../../data/wave6/enrich/raw/github_com_ribbonfilter_ribbongo.json) (enrichment confidence 0.72)

</details>
