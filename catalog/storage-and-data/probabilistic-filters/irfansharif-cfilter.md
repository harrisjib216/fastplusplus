# cfilter (Cuckoo Filter implementation in Go)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Go` · `MIT` · 🔴 abandoned

> Unmaintained pure-Go cuckoo filter (Fan et al. 2014) offering deletion as a Bloom-filter alternative; speed claims unmeasured, known item-loss bugs.

| | |
|---|---|
| **Beats** | Bloom filter |
| **Claimed result** | Unquantified claim: "Better Than Bloom Filters" / "achieving even higher performance than Bloom filters" |
| **Workload** | No benchmark numbers published; README and Show HN title assert general superiority over Bloom filters for approximate set-membership queries (lower space overhead, deletion support, higher performance) but provide no measured figures |
| **Metric** | other |
| **Adoption** | 751 stars; Show HN thread (item 12241332, 2016-08-07) with 181 points; listed in linvon/cuckoo-filter's README comparison of implementations and in shenwei356/awesome; go.mod dependency of finogeeks/Ligase |
| **Last commit** | 2017-07-05 |
| **Links** | [repository](https://github.com/irfansharif/cfilter) |

## Verdict

Nothing was measured. The 'higher performance than Bloom filters' line restates the Fan et al. paper, whose figures come from the authors' C++ efficient/cuckoofilter. The repo's only benchmark inserts and deletes one constant key, with no Bloom baseline, no published results and no stated hardware. The only third-party numbers for cfilter (issue #11: 100M random 16-char hex keys, Go on an unspecified Mac, no Bloom comparison) show roughly 0.5M inserts/s and 1M lookups/s, with 5,162 inserted keys missing afterwards.

## Use it when

- Reading a short, clear Go walk-through of partial-key cuckoo hashing (insert, evict, XOR alternate bucket, delete) while learning the Fan et al. design.
- Small, single-goroutine, throwaway sets of []byte keys that stay well below the 262,144-slot default capacity (the issue #13 reporter saw no losses at 200k keys but did at 300k), with Size left as a power of two, where an occasional false negative is acceptable.
- Maintaining legacy code that already imports it (pkg.go.dev lists older OWASP Amass utils, finogeeks/ligase and osamingo/shamoji), where you need to understand its failure modes before replacing it.

## Skip it when

- Anything that relies on the usual no-false-negatives property. Users reported inserted items that later cannot be found: 5,162 of 100M keys in issue #11, and lookups failing past about 300k keys in issue #13. Both issues were closed without a fix, with the note 'No longer maintaining this' (2019-11-20).
- Memory-sensitive use, which is the README's own headline claim. Each slot costs a 24-byte slice header whether it is used or not (about 7.5 MiB preallocated for the default 262k-slot filter), and each stored fingerprint is a separate heap allocation. At the default \~5e-7 FPR an optimal Bloom filter needs about 3.8 bytes per item (my arithmetic from the code and the paper's formula, not a measurement). A commenter in issue #13 estimated the footprint at 7x larger than necessary.
- High load factors. The issue #11 reporter could not get past roughly 36-50% load before Insert failed, against the \~95% the paper reports for 4-slot buckets.
- Concurrent access (no locking of any kind), persistence across restarts (the serialization request in issue #5 was closed unimplemented), or fingerprint sizes that are not a whole number of bytes.
- Any setting where you want a maintained, tagged release. The last commit was 2017-07-05, and the only tags (v0.1.0 and v0.1.1, both 2016) predate every bug fix.

## How it is fast

It uses partial-key cuckoo hashing from Fan, Andersen and Kaminsky (CoNEXT 2014). Each key stores a short fingerprint (the leading bytes of its FNV-1 64 hash) in one of two 4-slot buckets, i1 = djb2(key) mod m and i2 = (i1 XOR djb2(fingerprint)) mod m. A lookup therefore reads at most two buckets instead of k scattered Bloom bits, and a delete just clears a slot. When both buckets are full, Insert evicts random fingerprints to their alternate bucket, up to 500 times. This Go implementation gives up most of the paper's cache-locality advantage: every slot is a 24-byte []byte slice header pointing at its own heap allocation, and every Insert/Lookup/Delete allocates twice (hash.Sum plus the fingerprint slice). Nothing in the repo measures the resulting speed.

## Compared with alternatives

In practice, never for production. In Go, go-qfext (a quotient filter with measured 20-31 ns lookups against 74 ns for bits-and-blooms Bloom) or FastFilter/xorfilter (for static sets) are measured, working alternatives. efficient/cuckoofilter is the C++ reference whose paper numbers this README borrows. In 2017 the author himself pointed users to seiflotfy/cuckoofilter instead.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (Go stdlib only: hash, hash/fnv, math/rand, bytes) |
| **Minimum toolchain** | Not formally stated. There is no go.mod, and .travis.yml tested Go 1.3-1.6 plus tip in 2016-2017. Module mode resolves @latest to v0.1.1. |
| **Platforms** | any Go platform (pure Go, no unsafe or assembly) |
| **Thread safety** | Not documented, and not safe. There is no mutex, and even Lookup mutates the filter's shared hash.Hash (Reset/Write/Sum), so concurrent read-only lookups race too. Insert and swap use the global math/rand. |
| **Drop-in for the baseline** | no |

## Gotchas

- `go get github.com/irfansharif/cfilter` resolves to v0.1.1 (proxy.golang.org @latest), tagged 2016-09-11. That version still has the `i ^= hashfp(f) % cf.size` precedence bug, which panics with 'index out of range' once eviction starts (issue #8, fixed on master 2016-12-28), and a `rand.Intn(len(b)-1)` bug that never evicts the last slot (issue #10). panmari/compare_probabilistic_filters, which pins v0.1.1, commented cfilter out for exactly this panic. To get the fixes you must pin a master pseudo-version.
- Even on master, the alternate-bucket XOR trick only round-trips when Size (the bucket count) is a power of two, which the default is. With any other Size, a fingerprint that gets evicted can land in a bucket Lookup never checks, so the filter returns false negatives. The losses reported in issue #11 used Size(20,000,000) and Size(35,000,000).
- When Insert gives up after MaximumKicks, the fingerprint it is still holding is usually an earlier key's, and that key is silently dropped: Insert returns false, but Count() is not decremented and the lost key now fails Lookup. Insert also never checks for duplicates, so a key inserted twice is stored twice. Delete of a key that was never inserted can remove another key's matching fingerprint, as the README warns.
- FingerprintSize is in bytes, not bits. Its doc comment says the default is 2, but master's configure() uses 3 bytes (v0.1.1 used 2), so the effective FPR, about 2\*BucketSize/2^(8\*bytes), depends on which version you got.

## Known shortcomings

- No benchmark numbers of its own: the 'faster than Bloom' claim comes from the paper's C++ implementation (efficient/cuckoofilter, listed separately). A popular Go port (751 stars) with directional evidence only.
- Known lost items: 5,162 of 100M missing (#11) and misses past \~300k (#13), both closed unfixed; 'no longer maintaining' since 2019-11. `go get` resolves v0.1.1 (2016), which panics in the eviction loop (#8). On master the XOR alt-bucket works only for power-of-two sizes (otherwise false negatives) and a failed kick drops an old key without fixing Count. A slice per slot (24 B header plus a heap allocation per fingerprint, \~7.5 MiB preallocated) contradicts the README's space claim; not goroutine-safe; no serialization.

## Caveats and trade-offs

No numbers anywhere in the repo or the linked HN discussion; the 'faster than Bloom' claim is borrowed from the Fan et al. CoNEXT 2014 paper, whose measurements are of the authors' C++ implementation (efficient/cuckoofilter), not this Go code. The earlier claim that seiflotfy/cuckoofilter cites it could not be verified: seiflotfy's README does not mention it, and the reverse is true (cfilter borrowed seiflotfy's tests). Go, not C++.

Supports deletion (unlike a plain Bloom filter) at the cost of a small chance of deleting the wrong item on fingerprint collision

## Maintenance

Abandoned. The last commit was 2017-07-05, and on 2019-11-20 the author closed all remaining issues with 'No longer maintaining this'. It is MIT-licensed, stdlib-only and about 240 lines, so it is easy to vendor, but the false-negative bugs above (power-of-two sizing, dropped eviction victim, stale v0.1.1 tag) would need fixing first.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): reject; tier before verification D, tier now D.
- **Tier reason:** benchmark_url is null. The README only repeats the Fan et al. paper's qualitative claim ('achieving even higher performance than Bloom filters'), and the repo's only benchmark (BenchmarkInsertionAndDeletion in cfilter_test.go) has no Bloom-filter comparison and no published results. In the HN thread the author says 'i'll try putting up benchmarks as soon as i can', and none were ever posted.
- **Verifier notes:** Borderline case: under 1k stars (751), and its references are modest (a 2016 HN front page, GitHub-trending archives, a few README/list mentions, one go.mod user). It also has no measured comparison of its own, so no-baseline-comparison applies as well. The paper's evidence belongs to efficient/cuckoofilter, which is already in the catalog (data/wave6/verified.json), so rejecting loses no evidence. Metadata is correct (MIT, last commit 2017-07-05, abandoned, not a fork or archived); the orchestrator may override if it wants to spend its one Tier D slot here.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/irfansharif/cfilter>
  - <https://raw.githubusercontent.com/irfansharif/cfilter/master/README.md>
  - <https://github.com/irfansharif/cfilter/blob/master/cfilter_test.go>
  - <https://hn.algolia.com/api/v1/items/12241332>
  - <https://github.com/seiflotfy/cuckoofilter>
  - <https://github.com/linvon/cuckoo-filter>
- **Sources the enricher read:**
  - <https://github.com/irfansharif/cfilter>
  - <https://github.com/irfansharif/cfilter/blob/master/README.md>
  - <https://github.com/irfansharif/cfilter/blob/master/cfilter.go>
  - <https://github.com/irfansharif/cfilter/blob/master/bucket.go>
  - <https://github.com/irfansharif/cfilter/blob/master/fingerprint.go>
  - <https://github.com/irfansharif/cfilter/blob/master/options.go>
  - <https://github.com/irfansharif/cfilter/blob/master/doc.go>
  - <https://github.com/irfansharif/cfilter/blob/master/cfilter_test.go>
  - <https://github.com/irfansharif/cfilter/blob/master/.travis.yml>
  - <https://github.com/irfansharif/cfilter/issues?q=is%3Aissue>
  - <https://github.com/irfansharif/cfilter/issues/1>
  - <https://github.com/irfansharif/cfilter/issues/5>
  - <https://github.com/irfansharif/cfilter/issues/7>
  - <https://github.com/irfansharif/cfilter/issues/8>
  - <https://github.com/irfansharif/cfilter/issues/10>
  - <https://github.com/irfansharif/cfilter/issues/11>
  - <https://github.com/irfansharif/cfilter/issues/13>
  - <https://github.com/irfansharif/cfilter/commits/master>
  - <https://github.com/irfansharif/cfilter/commit/d07d951>
  - <https://github.com/irfansharif/cfilter/tags>
  - <https://github.com/irfansharif/cfilter/blob/v0.1.1/cfilter.go>
  - <https://github.com/irfansharif/cfilter/blob/v0.1.1/bucket.go>
  - <https://github.com/irfansharif/cfilter/blob/v0.1.1/options.go>
  - <https://proxy.golang.org/github.com/irfansharif/cfilter/@latest>
  - <https://proxy.golang.org/github.com/irfansharif/cfilter/@v/list>
  - <https://hn.algolia.com/api/v1/items/12241332>
  - <https://github.com/linvon/cuckoo-filter>
  - <https://pkg.go.dev/github.com/irfansharif/cfilter?tab=importedby>
  - <https://github.com/panmari/compare_probabilistic_filters>
  - <https://github.com/panmari/compare_probabilistic_filters/blob/master/false_positive_rate.go>
  - <https://github.com/panmari/compare_probabilistic_filters/blob/master/benchmark_test.go>
  - <https://github.com/panmari/compare_probabilistic_filters/blob/master/go.mod>
  - <https://github.com/panmari/compare_probabilistic_filters/commits/master/false_positive_rate.go>
  - <https://panmari.github.io/2020/10/09/probabilistic-filter-golang.html>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/irfansharif/cfilter`) · [data/wave6/enrich/raw/github_com_irfansharif_cfilter.json](../../../data/wave6/enrich/raw/github_com_irfansharif_cfilter.json) (enrichment confidence 0.85)

</details>
