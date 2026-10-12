# fastbloom

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Rust Bloom filter crate: classic non-blocked layout, faster lookups than other Rust Bloom crates, plus a lock-free atomic variant.

| | |
|---|---|
| **Beats** | Bloom filter |
| **Claimed result** | README headline: "2-20 times faster and magnitudes more accurate than existing Bloom filter implementations". Per-check latency charts on the page: non-member check fastbloom 1.36 ns (atomic 1.61) vs sbbf 5.16, bloomfilter 14.50, bloom 17.44, probabilistic-collections 21.29, solana-bloom 42.56 ns (\~3.8x-31x, derived from page data); member check fastbloom 7.67 ns (atomic 7.38) vs bloom 27.26, bloomfilter 29.45, probabilistic-collections 35.19, solana-bloom 121.56 ns (\~3.6x-16x, derived from page data), but sbbf is faster on member checks at 5.30 ns (fastbloom \~1.45x slower, derived from page data). |
| **Workload** | Per-lookup latency (ns) of member and non-member checks on u64 keys in a 64 KiB (2^16-byte) filter holding 45,000 items (\~8 hashes/item), measured with Criterion against other Rust Bloom filter crates (sbbf-rs-safe, bloomfilter, bloom, probabilistic-collections, solana-bloom). fastbloom uses foldhash, the others SipHash-1-3 (xxhash for sbbf). No insert benchmark is charted. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 5900X 12-Core Processor (3.70 GHz), 64-bit OS, x64 |
| **Adoption** | 360 stars |
| **Last commit** | 2026-03-01 |
| **Links** | [repository](https://github.com/tomtomwombat/fastbloom) · [benchmark](https://github.com/tomtomwombat/fastbloom#speed) |

## Verdict

The author's Criterion microbenchmark on an AMD Ryzen 9 5900X measures per-lookup latency for u64 keys in a 64 KiB filter holding 45,000 items (about 8 hashes each). Each iteration repeats the same 10 query keys, the rustc version and flags are unstated, and perf.py reads Windows-style paths, suggesting a Windows build. fastbloom (with foldhash) took 1.36 ns per non-member check vs 5.16 ns for sbbf (xxh3) and 14.5-42.6 ns for SipHash-based crates, and 7.67 ns per member check vs 5.30 ns for sbbf and 27-122 ns for the rest. Insert throughput, multi-threaded runs and out-of-cache filters were not measured.

## Use it when

- Rust services where most queries are misses, such as cache or disk-read avoidance or dedup pre-checks, since non-member checks are its strongest case (1.36 ns vs 5-43 ns for other crates on the author's benchmark).
- Filters that grow by incremental inserts at runtime and may need union or intersect, which a build-once xor or fuse filter cannot do.
- Many threads inserting and querying one filter: AtomicBloomFilter uses fetch_or on AtomicU64 words with no lock.
- Low false-positive targets per bit: the author's accuracy chart shows it tracking the classic-Bloom curve, well below the blocked sbbf and below bloom and bloomfilter at the same load.
- no_std or embedded targets with alloc: CI checks thumbv7em-none-eabi, and portable-atomic covers targets without native 64-bit atomics.

## Skip it when

- Workloads dominated by positive lookups: a member check touches k random words, and on the author's own chart the SIMD split-block sbbf is faster (5.30 ns vs 7.67 ns).
- Filters much larger than cache: non-blocked probes each risk a cache miss. The published numbers come only from a 64 KiB, cache-resident filter, and DRAM-scale behaviour is not measured.
- Static key sets built once: a xor or binary fuse filter (xorf) gives smaller filters and constant-probe lookups.
- Needs deletion or counting: not supported. A counting Bloom filter (issue #10) and xor filters (issue #7) are open requests.
- Cross-language or cross-version persisted filters: no C API, and 0.17 changed the algorithm, so serialized filters are incompatible with earlier versions.

## How it is fast

Each item is hashed once, to 64 bits. The other k-1 bit positions come from cheap double hashing (Kirsch-Mitzenmacher, 'Less hashing, same performance'): h2 = h1 \* constant, then each next index is rotl(h1, 5) + h2, instead of k separate hash calls. Indexes are mapped to the bit array with Lemire's multiply-shift fast range reduction rather than modulo. contains returns on the first unset bit, so a non-member usually costs one hash and one or two memory probes. The bit array is a plain boxed u64 slice with no SIMD and no blocking; since 0.17 the author deliberately chose a non-blocked layout, trading member-check speed for accuracy and faster non-member rejection (issue #20).

## Compared with alternatives

Pick it over xorf when you need incremental or concurrent inserts rather than a build-once static set. Pick it over the Impala-style SIMD blocked Bloom (efficient/cuckoofilter) or a cuckoo filter when you are in Rust, misses dominate and you want classic-Bloom accuracy per bit without deletes. Choose a blocked Bloom when hits dominate or the filter lives in DRAM, and a cuckoo filter when you need deletion.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | foldhash, siphasher, libm, portable-atomic (always); rand (default feature), serde and loom (optional features) |
| **Minimum toolchain** | Rust 1.70 (rust-version in Cargo.toml; CI has an MSRV job on 1.70), edition 2021 |
| **Platforms** | any Rust target, with no arch-specific or SIMD code; std and no_std+alloc, with thumbv7em-none-eabi checked in CI; tests run on ubuntu-latest |
| **Thread safety** | BloomFilter needs &mut self to insert (wrap it in RwLock to share). AtomicBloomFilter is lock-free: all methods take &self and use Relaxed atomics, so there is no ordering guarantee between one thread's insert and another's contains without external synchronization. |
| **Drop-in for the baseline** | partial — same semantics as a classic Bloom filter (no false negatives, no deletes), but it has its own builder API, and its bit layout and serde format do not interoperate with other crates or with fastbloom before 0.17 |

## Gotchas

- The default hasher is SipHash-1-3 with a random key per filter. Filters built separately cannot be unioned, intersected or compared unless both use .seed(&u128) or the same hasher, and union and intersect do not check this. Note also that the headline benchmark swapped in foldhash.
- Every probe is derived from one 64-bit hash, so a weak custom hasher (or raw values fed to insert_hash) degrades all k positions at once. The README says hashes are built from 32-bit halves, but the 0.17 code actually multiplies and rotates a single 64-bit hash.
- k comes from ln2 \* bits / items, and the minimum size is 64 bits, so tiny expected_items gives huge k (issue #17: 354 hashes for 1 item when the minimum was 512 bits; expected_items(0) meant u32::MAX hashes before the clamp to 1). In 0.15-0.16, hashes(0) panicked; 0.17 clamps it to 1.
- Recent correctness fixes, so pin to 0.17 or later: AtomicBitVec::set returned the wrong value until 0.14.1, and filters above u32::MAX bits (about 512 MiB) mapped every index into a u32 range, causing mass false positives, until 0.16 (issue #22). The src/ tree has no unsafe code.

## Known shortcomings

- The '2-20x' is overstated: on its own chart the sbbf crate's member check (5.30 ns) beats fastbloom (7.67 ns); measured gains are \~3.8-31x for non-members and \~3.6-16x for members vs the rest. Only lookups are benchmarked (no inserts), and fastbloom used foldhash while the others used SipHash.
- Flattering benchmark: the same 10 query keys repeated against a 64 KiB cache-hot filter, with foldhash vs SipHash rivals; no insert, multi-threaded or DRAM-resident numbers; rustc/flags unstated. Non-blocked design (k random probes per hit). Recent correctness fixes: FP blowup for filters &gt;512 MiB until 0.16 (#22), atomic set() fixed in 0.14.1; 0.17 serde format breaks older versions; still 0.x with frequent breaking bumps.
- Each filter gets a random SipHash key, so union/intersect require the same seed and this is not checked; the README's hash description is stale; tiny expected_items gives a huge k.

## Caveats and trade-offs

The claim is overstated: on the page's own member-check chart sbbf (5.30 ns) beats fastbloom (7.67 ns), so "2-20x faster than existing implementations" does not hold for every crate or operation. fastbloom was benchmarked with foldhash while bloom, bloomfilter and probabilistic-collections used SipHash-1-3, so part of the gap is the hasher (fastbloom's own default is SipHash-1-3). The benchmark repo has no license, no rustc version or flags are stated, the numbers exist only as labels on chart images, and it measures lookups only, with no insert throughput.

Rust-only, no C API; speed comes from deriving many index bits from a single real hash (hash composition) instead of K independent hashes. Has an AtomicBloomFilter for lock-free concurrent use.

## Maintenance

Actively maintained (0.17.0 on 2026-03-01, maintainer still replying to issues in July 2026), MIT OR Apache-2.0, a small pure-safe-Rust crate with heavy real-world use (about 23.6M crates.io downloads, a dependency of quinn-proto, turso_core and libafl), but still 0.x with breaking releases every few months.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party Criterion benchmark (tomtomwombat/bench-bloom-filters, benches/bench_bloom_filter.rs) is public and the CPU (Ryzen 9 5900X) is stated, but no rustc version or flags are given, so it falls short of A and stays C.
- **Verifier notes:** The record's claim quotes the README correctly but hides that sbbf wins member checks. The chart images do carry exact numeric labels, which are now quoted. Metadata checks out: 360 stars, last commit 2026-03-01, MIT OR Apache-2.0 per Cargo.toml and README (GitHub detects only Apache-2.0), not archived, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/tomtomwombat/fastbloom>
  - <https://github.com/tomtomwombat/fastbloom#speed>
  - <https://github.com/tomtomwombat/fastbloom/blob/main/Cargo.toml>
  - <https://github.com/tomtomwombat/bench-bloom-filters>
  - <https://github.com/tomtomwombat/bench-bloom-filters/blob/main/Cargo.toml>
  - <https://github.com/tomtomwombat/bench-bloom-filters/blob/main/benches/bench_bloom_filter.rs>
  - <https://github.com/tomtomwombat/bench-bloom-filters/blob/main/perf.py>
  - <https://github.com/user-attachments/assets/a825d2f7-4cd7-4b6b-a447-fd7f3dab356b>
  - <https://github.com/user-attachments/assets/998f9470-b91f-460c-ad2d-1f197160c210>
- **Sources the enricher read:**
  - <https://github.com/tomtomwombat/fastbloom>
  - <https://github.com/tomtomwombat/fastbloom#speed>
  - <https://github.com/tomtomwombat/fastbloom/blob/main/Cargo.toml>
  - <https://github.com/tomtomwombat/fastbloom/blob/main/.github/workflows/rust.yml>
  - <https://github.com/tomtomwombat/fastbloom/blob/main/src/lib.rs>
  - <https://github.com/tomtomwombat/fastbloom/blob/main/src/hasher.rs>
  - <https://github.com/tomtomwombat/fastbloom/blob/main/src/bit_vector.rs>
  - <https://github.com/tomtomwombat/fastbloom/blob/main/src/builder.rs>
  - <https://github.com/tomtomwombat/fastbloom/blob/main/src/math.rs>
  - <https://github.com/tomtomwombat/fastbloom/commits/main>
  - <https://github.com/tomtomwombat/fastbloom/commit/475abfd>
  - <https://github.com/tomtomwombat/fastbloom/releases>
  - <https://github.com/tomtomwombat/fastbloom/issues?q=is%3Aissue>
  - <https://github.com/tomtomwombat/fastbloom/issues/13>
  - <https://github.com/tomtomwombat/fastbloom/issues/15>
  - <https://github.com/tomtomwombat/fastbloom/issues/17>
  - <https://github.com/tomtomwombat/fastbloom/issues/20>
  - <https://github.com/tomtomwombat/fastbloom/issues/21>
  - <https://github.com/tomtomwombat/fastbloom/issues/22>
  - <https://github.com/tomtomwombat/fastbloom/issues/23>
  - <https://github.com/tomtomwombat/fastbloom/issues/28>
  - <https://github.com/tomtomwombat/fastbloom/issues/31>
  - <https://github.com/tomtomwombat/bench-bloom-filters>
  - <https://github.com/tomtomwombat/bench-bloom-filters/blob/main/Cargo.toml>
  - <https://github.com/tomtomwombat/bench-bloom-filters/blob/main/benches/bench_bloom_filter.rs>
  - <https://github.com/tomtomwombat/bench-bloom-filters/blob/main/src/container.rs>
  - <https://github.com/tomtomwombat/bench-bloom-filters/blob/main/perf.py>
  - <https://github.com/tomtomwombat/bench-bloom-filters/commits/main>
  - <https://github.com/user-attachments/assets/a825d2f7-4cd7-4b6b-a447-fd7f3dab356b>
  - <https://github.com/user-attachments/assets/998f9470-b91f-460c-ad2d-1f197160c210>
  - <https://github.com/user-attachments/assets/17ddaab7-c63f-456a-9e2e-b22c7f994386>
  - <https://crates.io/api/v1/crates/fastbloom>
  - <https://crates.io/api/v1/crates/fastbloom/reverse_dependencies>
  - <https://hn.algolia.com/api/v1/search?query=fastbloom&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/tomtomwombat/fastbloom`) · [data/wave6/enrich/raw/github_com_tomtomwombat_fastbloom.json](../../../data/wave6/enrich/raw/github_com_tomtomwombat_fastbloom.json) (enrichment confidence 0.85)

</details>
