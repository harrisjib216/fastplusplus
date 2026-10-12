# pleat (Pleated Ribbon Filter, Rust)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0 (Cargo.toml and README; LICENSE plus LICENSE-APACHE present; GitHub detector reports MIT)` · 🟢 active

> Rust ribbon-filter crate: about 7.6 bits/key at 0.8% FPR, less than Bloom, with cache-local 'pleated' construction.

| | |
|---|---|
| **Beats** | Bloom filter |
| **Claimed result** | Memory: \~7.6 bits/key at 0.8% FPR, described as well under Bloom filter memory for equal accuracy (qualitative, no Bloom bits/key number given on the same page). Construction: pleated build is \~2.3x faster than the crate's own arrival-order build once the table exceeds L3 cache (26.0ns/key vs 60.4ns/key at 10M keys) -- this ratio is against the crate's own baseline construction order, not against a Bloom filter implementation. |
| **Workload** | Own Criterion benchmarks (cargo bench --bench construct/query/serde) of ribbon-filter construction throughput (pleated vs arrival-order vs 8-thread parallel) and query latency at 1M and 10M 64-bit keys; README states ribbon filters use \~7.6 bits/key at \~0.8% FPR, 'well under a Bloom filter's memory for the same accuracy'. |
| **Metric** | memory |
| **Hardware** | Intel i9-14900HX |
| **Adoption** | 1 star; crates.io pleat 0.1.0, 21 downloads |
| **Last commit** | 2026-07-12 |
| **Links** | [repository](https://github.com/integrallis/pleat) · [benchmark](https://github.com/integrallis/pleat#readme) |

## Verdict

The crate's own Criterion benchmarks on an Intel i9-14900HX (rustc version and flags not stated) measure a homogeneous w=64, R=7 filter at about 7.6 bits/key with a measured 0.783% FPR. They also show pleated construction at 26.0 ns/key vs 60.4 for the crate's own arrival-order build at 10M 64-bit keys (2.3x), and slightly slower at 1M (26.1 vs 23.8). No Bloom filter is measured in the crate. The 'less memory than Bloom' claim is analytical, and the companion preprint's C++ measurements show pleated ribbon construction still slower than single-thread blocked-Bloom insertion.

## Use it when

- Static key sets rebuilt in bulk (immutable LSM/SST files, periodic snapshots, deduplication indexes) where filter RAM or disk size matters more than build CPU.
- Filters of about 10M+ 64-bit keys, where the banding table outgrows L3 and pleating pays off: 26.0 vs 60.4 ns/key at 10M in the crate's own benchmark.
- When you want the false-positive rate tunable in 1-bit steps (R from 1 to 32), e.g. R=7 at about 7.6 bits/key and 0.8% FPR, or R=10 at about 10.9 bits/key and 0.1%, rather than fixed 8/16-bit fingerprints.
- Rust services that persist filters and want a versioned, checksummed blob whose decoder rejects corrupt or mismatched input with typed errors (fuzzed and Miri-checked in CI).
- Multi-core build machines that want a parallel build they can check: from_keys_parallel output is bit-identical to the sequential build.

## Skip it when

- The key set changes or its final size is unknown. The filter is build-once, with no insert, delete, union or counting; use a Bloom, cuckoo or quotient filter.
- Build time must match Bloom. In the companion preprint's C++ harness, pleated ribbon is still about 24 ns/key at 100M keys against 6.1-11.5 ns/key for single-thread blocked-Bloom insertion, and it takes 16 threads (11.9 ns/key) to catch up. In this crate, 8 threads give only 24.4 vs 26.0 ns/key over single-thread pleated at 10M.
- Small filters, where the banding table fits in cache. At 1M keys pleated is slower than arrival order (26.1 vs 23.8 ns/key), and from_hashable always uses the pleated path.
- Lookup latency is the bottleneck. No Bloom query comparison is measured, and each probe reads up to 2\*R u64 words (112 bytes at R=7) against one cache line for a blocked Bloom filter. The crate reports 17.4 ns scalar and 15.4 ns batched miss-dominated lookups at 10M keys (standard w=128: 24.2 ns).
- You need proven production maturity. It has 1 GitHub star, 21 crates.io downloads, 0 reverse dependencies and a single author, has had no commits since 2026-07-12, and its companion paper is an unreviewed preprint.

## How it is fast

The memory win comes from the ribbon filter itself (Dillinger and Walzer; banded GF(2) linear system solved by on-the-fly Gaussian elimination). Homogeneous w=64 ribbon costs about 1.09\*R bits/key. The companion preprint puts Bloom at about 44% over the minimum, which works out to roughly 10 bits/key at R=7 against 7.6 here. The speed contribution is 'pleating' (partition-instead-of-sort): one counting-sort pass buckets keys by start slot into 2^16-slot windows (about 768 KiB) before banding. That turns the dependent, cache-missing row-reduction chains of arrival-order banding into cache-local work, and because the banding solution is order-independent the output is bit-identical. from_keys_parallel splits the slot range across std threads and defers keys within 2^14 slots of a range boundary (plus any spills) to a sequential tail, following parallel BuRR.

## Compared with alternatives

Pick pleat over xorf (about 9 bits/key at 0.4% for BinaryFuse8) when you are in Rust and want a static filter with a tunable R and slightly less space (about 8.75 bits/key at R=8, derived from the crate's sizing formula), and your large rebuilds can use the pleated or parallel build. Choose BuRR or RocksDB Ribbon (C++) when you need sub-1% space overhead or a battle-tested production implementation, and fastbloom or Boost.Bloom when keys arrive incrementally or lookup and build speed matter more than bits/key.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | xxhash-rust 0.8 (xxh3 feature) only; requires std (not no_std). The default feature 'parallel' uses std::thread with no extra crates. |
| **Minimum toolchain** | Rust 1.87 (MSRV, built in CI), edition 2021 |
| **Platforms** | Pure Rust, any target. CI runs tests on Linux, macOS and Windows plus i686-unknown-linux-musl (32-bit). The software prefetch in contains_batch is only compiled on x86_64; other architectures run batch queries without prefetch. |
| **Thread safety** | Not documented. The source shows filters are immutable Vec-backed structs with no interior mutability, so concurrent contains() through shared references should be safe (inferred, not stated). from_keys_parallel takes an explicit thread count and uses scoped std threads. |
| **Drop-in for the baseline** | partial — it answers the same 'possibly present' question with no false negatives, but it needs the full key set up front, supports no insert or delete after the build, keys the API on u64 (or process-local Hash), and uses its own PLT1 serialization format |

## Gotchas

- The from_hashable/contains_hashable path hashes Rust Hash output with fixed-seed xxh3. The crate warns this is only reliable within the same process, target and toolchain, so do not persist such filters. For durable filters, hash a stable encoding to u64 yourself.
- The hash seed is fixed and non-cryptographic. SECURITY.md says an adversary who chooses the queried keys can inflate the false-positive rate, so keyed hashing is your job.
- Peak build memory is well above the final filter (derived from the source). A pleated w=64 build copies the whole key slice (8 B/key) and allocates about 1.09n u64 coefficient rows (about 8.7 B/key). StdRibbon allocates a u128 coefficient row plus a u32 result row per slot, re-bands every key on each seed retry (up to 64 seeds), and returns BuildError::NoSolvingSeed if none solves.
- Filter sizing is fixed by n and R at build time, and bits_per_key(n) needs you to pass n back in. An empty key set still produces a non-empty filter.

## Known shortcomings

- The Bloom comparison is memory only and qualitative; build is slower than a single-threaded Bloom build (per the paper preprint).
- No Bloom filter measured (memory win is analytical, \~7.6 vs \~10 bits/key at R=7); builds are slower than Bloom (paper \~24 vs 6.1-11.5 ns/key at 100M; the crate's 8 threads only 24.4 vs 26.0 at 10M); queries vs Bloom unmeasured (up to 112 B per probe). Build-once u64 API; fixed-seed hash lets chosen keys inflate FPR; 1 star, 21 downloads; the paper is an unreviewed preprint.

## Caveats and trade-offs

The Bloom comparison is qualitative: the README says \~7.6 bits/key at \~0.8% FPR is 'well under a Bloom filter's memory', and the companion paper (github.com/integrallis/ribbon-catches-bloom, unreviewed preprint) says 'a quarter less memory' based on theory rather than a measured Bloom filter. The ribbon filter is not faster than Bloom at construction. The paper measures pleated homogeneous ribbon at about 24 ns/key versus 6.1-11.5 ns/key for single-thread blocked-Bloom insertion at 100M keys, and it needs 16 threads to match a single Bloom thread. The only numeric head-to-head is pleated vs the crate's own arrival-order build (2.3x at 10M keys). Query speed against Bloom is not measured. The rustc version and flags are not stated (rust-version 1.87 is the MSRV). Very new project (1 star).

Immutable filter (build-once); keys must be pre-hashed to u64; this release implements homogeneous ribbon (w=64) plus a StdRibbon w=128 variant; construction still needs the full banding table in memory like other ribbon filters.

## Maintenance

A new single-author research release: repository created 2026-07-11, last main-branch commit 2026-07-12 with Dependabot PRs left open since, v0.1.0 on crates.io. It is dual MIT/Apache-2.0, tested byte-for-byte against the fastfilter_cpp reference kernel, fuzzed, Miri-checked and under a 90% coverage gate, so it is usable as a dependency or small enough (about 2.4k lines of Rust source, tests included) to vendor, but it has no track record of production use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README gives first-party measured numbers (about 7.6 bits/key; measured FPR 0.783% at r=7; construction 26.0 vs 60.4 ns/key at 10M on an i9-14900HX, benches/construct.rs). Its comparison against Bloom is only a qualitative memory statement, with no Bloom filter measured, so it is C. The companion paper repo integrallis/ribbon-catches-bloom is an unreviewed preprint in the NeurIPS template and does not change this.
- **Verifier notes:** The record is accurate. The benchmark_url anchor pointed to the construction section, which has no Bloom claim; the memory claim is in the README intro, so the URL now points to the README root. The companion paper repo may be worth tracking as a separate RocksDB-construction entry (1.78x faster Standard128 ribbon build than stock RocksDB), but that is a different baseline.
- **Fields the verifier corrected:** `benchmark_url`, `stars_or_usage`, `license`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/integrallis/pleat>
  - <https://github.com/integrallis/pleat#measured-construction-cost>
  - <https://raw.githubusercontent.com/integrallis/pleat/HEAD/Cargo.toml>
  - <https://crates.io/api/v1/crates/pleat>
  - <https://github.com/integrallis/ribbon-catches-bloom>
  - <https://raw.githubusercontent.com/integrallis/ribbon-catches-bloom/HEAD/paper/main.tex>
  - <http://export.arxiv.org/api/query?search_query=ti:%22Ribbon%20Catches%20Bloom%22&max_results=5>
- **Sources the enricher read:**
  - <https://github.com/integrallis/pleat>
  - <https://github.com/integrallis/pleat#readme>
  - <https://github.com/integrallis/pleat/blob/HEAD/Cargo.toml>
  - <https://github.com/integrallis/pleat/blob/HEAD/src/lib.rs>
  - <https://github.com/integrallis/pleat/blob/HEAD/src/filter.rs>
  - <https://github.com/integrallis/pleat/blob/HEAD/src/filter/parallel.rs>
  - <https://github.com/integrallis/pleat/blob/HEAD/src/banding.rs>
  - <https://github.com/integrallis/pleat/blob/HEAD/src/banding128.rs>
  - <https://github.com/integrallis/pleat/blob/HEAD/src/hash.rs>
  - <https://github.com/integrallis/pleat/blob/HEAD/src/format.rs>
  - <https://github.com/integrallis/pleat/blob/HEAD/PORT_NOTES.md>
  - <https://github.com/integrallis/pleat/blob/HEAD/CHANGELOG.md>
  - <https://github.com/integrallis/pleat/blob/HEAD/SECURITY.md>
  - <https://github.com/integrallis/pleat/blob/HEAD/.github/workflows/ci.yml>
  - <https://github.com/integrallis/pleat/blob/HEAD/benches/construct.rs>
  - <https://github.com/integrallis/pleat/blob/HEAD/benches/query.rs>
  - <https://github.com/integrallis/pleat/blob/HEAD/benches/results/10000000_pleated.json>
  - <https://github.com/integrallis/pleat/blob/HEAD/reproduce.sh>
  - <https://github.com/integrallis/pleat/commits>
  - <https://github.com/integrallis/pleat/issues>
  - <https://github.com/integrallis/pleat/pulls>
  - <https://crates.io/api/v1/crates/pleat>
  - <https://crates.io/api/v1/crates/pleat/reverse_dependencies>
  - <https://docs.rs/crate/pleat/latest/builds>
  - <https://raw.githubusercontent.com/integrallis/ribbon-catches-bloom/HEAD/README.md>
  - <https://raw.githubusercontent.com/integrallis/ribbon-catches-bloom/HEAD/paper/main.tex>
  - <https://hn.algolia.com/api/v1/search?query=%22Ribbon%20Catches%20Bloom%22>
  - <https://hn.algolia.com/api/v1/search?query=integrallis%20pleat>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/integrallis/pleat`) · [data/wave6/enrich/raw/github_com_integrallis_pleat.json](../../../data/wave6/enrich/raw/github_com_integrallis_pleat.json) (enrichment confidence 0.8)

</details>
