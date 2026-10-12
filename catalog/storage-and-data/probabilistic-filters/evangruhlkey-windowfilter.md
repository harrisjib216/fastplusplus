# Windowed Cuckoo Filter (WindowFilter, implements 'Smaller and More Flexible Cuckoo Filters')

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Safe-Rust (2,2) windowed cuckoo filter: 12.8 bits/key at 2^-10 FPR, 12% under Bloom, 7-25% under cuckoo; slower inserts.

| | |
|---|---|
| **Beats** | cuckoo filter, Bloom filter |
| **Claimed result** | Windowed cuckoo (2,2): 1.5958 bytes/item vs Bloom's 1.8034 (README: about 12% less memory) and Cuckoo(2,4)'s 2.1299 (about 25% less) at similar FPR (2^-10 target); lookup 60.28 ns vs Bloom's 81.59 ns and Cuckoo's 61.19 ns (essentially tied with cuckoo). Inserts are slower: 162.97 ns vs 58.74 ns for Cuckoo(2,4) and 93.61 ns for Bloom, and max load is 0.9575 vs 0.9780 for Cuckoo |
| **Workload** | Bit-packed Bloom filter, standard Cuckoo(2,4) filter, and overlapping-window Cuckoo(2,2) filter compared on bytes/item, false-positive rate, lookup/insert latency, and max load factor |
| **Metric** | memory |
| **Compiler and flags** | Rust stable toolchain (version not pinned, rust-toolchain.toml), edition 2024, release profile lto=thin, codegen-units=1 |
| **Adoption** | 0 stars |
| **Last commit** | 2026-09-03 |
| **Links** | [repository](https://github.com/EvanGruhlkey/WindowFilter) · [benchmark](https://github.com/EvanGruhlkey/WindowFilter#benchmark) |

## Verdict

In one run of the author's benchmark binary (100k string keys, 200k queries half present, target rate 2^-10, release build with thin LTO on unpinned stable Rust, CPU not stated), the windowed (2,2) filter used 1.596 bytes/key vs 1.803 for the author's own classic Bloom and 2.130 for the author's own (2,4) cuckoo; lookups tied with cuckoo (60.3 vs 61.2 ns) and beat Bloom (81.6 ns), while inserts were 2.8x slower than cuckoo (163 vs 59 ns). Most of the 25% memory gap to cuckoo is power-of-two rounding at n=100k, which leaves the cuckoo table at 76% load: against a well-sized cuckoo the code's parameters give about 7% (12/0.94 vs 13/0.95 bits per key), matching the paper's overhead factors of 1.272 vs 1.365.

## Use it when

- A Rust service needs a deletable 'definitely absent' pre-check in front of a disk, database or network lookup, the maximum key count is known, and bytes per key matter more than insert speed: about 12.8 bits/key at a 2^-10 rate vs 14.4 for a classic Bloom filter.
- Key counts that fall just above a power-of-two boundary, where a standard XOR-addressed cuckoo filter must round its bucket count up and can waste up to about 2x (the author's own cuckoo sits at 76% load for 100k keys).
- Read-mostly workloads: fill once or slowly, then query often. The author's run measured lookups on par with (2,4) cuckoo and faster than an unblocked Bloom filter, on a cache-resident 100k-key filter.
- Keys are already strings, or converting them to &str is cheap.
- You want a short, readable reference for the windowed layout (about 740 lines of library code including tests, #![forbid(unsafe_code)], no dependencies) that you can vendor and adapt.

## Skip it when

- Insert-heavy or streaming fills. Inserts were 2.8x slower than the author's (2,4) cuckoo (163 vs 59 ns) and 1.7x slower than Bloom. The paper's own implementation also shows windowed (2,2) inserting about 2x slower than bucketed (2,4), and about 10x slower than the Prefix filter (3.1 vs 33 M keys/s at 2^-8).
- Untrusted keys. The hash is FNV-1a plus a splitmix finalizer with fixed seeds, and the relocation RNG is a fixed-seed xorshift, so crafted keys can collide and force failed inserts; the README says it is for experiments and trusted input only.
- Unknown or growing key counts. There is no resizing: the table is sized for 94% load at the declared capacity, and the author's max-load run failed at 95.75%, which leaves only about 2% headroom before insert returns false.
- Static key sets known up front. At a 2^-10 rate, Xor filters (1.23x overhead, per the paper) and BuRR are smaller than this filter's \~1.28x and need no relocation.
- Production dependencies that need persistence, integer or byte keys, batch or SIMD lookups, concurrent inserts, or a maintained crate. None of these are provided; the crate is not on crates.io, has 0 stars, and all 18 commits landed within one day. Performance on DRAM-sized filters was never measured (the benchmark stops at 100k keys, about 160 KB).

## How it is fast

The gain is in memory, not speed. It implements (2,2) windowed cuckoo hashing from Schmitz, Zentgraf and Rahmann (arXiv:2505.05847): each key has two candidate windows of two adjacent slots, neighbouring windows overlap by one slot, and the theoretical load threshold is 0.965 with only four candidate slots (vs 0.980 with eight slots for (2,4) buckets), so a 2^-k rate needs k+2 bits per slot instead of k+3 and the table is sized for 94% load. The second window is the first plus a fingerprint-derived offset modulo the window count (a signed offset instead of the classic XOR), so the table size need not be a power of two; each slot also stores a choice bit and a window-offset bit, which let an evicted fingerprint find its other window and count as extra match bits. Slots are bit-packed into a Vec&lt;u64&gt;, and lookups check the four slots one at a time: no SIMD, no bit-parallel matching, no prefetching.

## Compared with alternatives

Pick it only when you need a deletable filter in dependency-free safe Rust and can live with slow inserts; Vacuum Filter (a similar \~25%-smaller-than-cuckoo claim) and Morton Filter (1.3-2.5x faster lookups) are more heavily engineered C++, and Prefix Filter inserts about 10x faster but needs AVX-512. For key sets known up front, Xor Filter or BuRR is smaller.

## Integration

| | |
|---|---|
| **Form** | crate (git dependency only; not published on crates.io) |
| **Dependencies** | none (std only; Cargo.lock lists no external packages) |
| **Minimum toolchain** | Rust 1.85+, implied by edition 2024. No rust-version field; rust-toolchain.toml pins only the floating 'stable' channel. |
| **Platforms** | any Rust std target: pure safe Rust (#![forbid(unsafe_code)]) with no SIMD or architecture-specific code; CI runs only on ubuntu-latest, and the benchmark hardware is not documented |
| **Thread safety** | Not documented. The filters are plain structs backed by Vec&lt;u64&gt; with no interior mutability, so Rust's auto traits make them Send + Sync: contains takes &self and can be shared across threads for reads, while insert and delete take &mut self and need external locking. The paper's lock-free parallel subfilters are not implemented. |
| **Drop-in for the baseline** | partial — it has the usual cuckoo-filter insert/contains/delete semantics, but its API mirrors no existing crate, takes only &str keys, has a fixed capacity and no serialization, so call sites and any persistence code must be rewritten |

## Gotchas

- Any insert whose four candidate slots are all full allocates a rollback log with Vec::with_capacity(max_kicks) before the first kick: 16-byte entries x 10,000 is about 160 KB per such insert at the default setting.
- Inserts are not deduplicated. Repeated inserts of one key each take a slot, and once the key's four candidate slots (three when its two windows are adjacent) all hold its copies, the next insert runs all 10,000 kicks and fails.
- delete on a key that was never inserted can remove another key's matching entry and create false negatives. The README warns about this, as with cuckoo filters in general.
- Bad parameters panic instead of returning errors: new asserts capacity &gt; 0 and fpr_bits in 1..=30 (1..=29 for CuckooFilter). A fingerprint of 0 is remapped to 1 so that 0 can mean an empty slot, which slightly raises the false-positive rate (the paper makes the same trade).

## Known shortcomings

- Baselines are the author's own Bloom/cuckoo implementations; no CPU model; inserts 2.8x slower than cuckoo (162.97 vs 58.74 ns); 0 stars.
- The '25% smaller than cuckoo' is mostly an artifact: its own cuckoo baseline rounds to a power of two (76% load at n=100k); against a well-sized cuckoo filter the gain is about 7% (matching the paper's 1.272 vs 1.365). Baselines are self-made (unblocked Bloom), cache-resident 100k keys, one run, no CPU stated; FNV string hashing dominates lookup time.
- Inserts are 2.8x slower than cuckoo; no resize (\~2% headroom); no dedup (a fifth copy fails after 10k kicks); a 160 KB rollback Vec per kicking insert. &str keys only, fixed hash seeds (unsafe for adversarial keys), no serialization. A one-day repo (18 commits on 2026-09-03), not on crates.io, 0 stars; the paper authors' own implementation is gitlab rahmannlab/cuckoo-filters (Python/numba).

## Caveats and trade-offs

Third-party Rust reimplementation of arXiv:2505.05847 (Smaller and More Flexible Cuckoo Filters), not the paper authors' code. The baselines are the author's own Bloom and Cuckoo(2,4) implementations, not established libraries. The README table is one run (defaults: 100k items, 200k queries, k=10), with no CPU model and no pinned toolchain version. Inserts are about 2.8x slower than the conventional cuckoo filter. It uses a non-cryptographic hash that is not safe against adversarial input. 0 stars; created and pushed around 2026-09-03.

Insert is slower than both Bloom and plain Cuckoo (162.97 ns vs 93.61 / 58.74 ns) because of the overlapping-window relocation logic

## Maintenance

Listed as active, but it is a one-day project (18 commits on 2026-09-03, CI green, no issues, releases or crates.io publication) that is MIT-licensed, dependency-free and small enough to vendor, so treat it as a readable reference rather than a maintained library; for the full design (bit-parallel probes, prefetching, parallel subfilters), see the paper authors' MIT-licensed Python/numba code at gitlab.com/rahmannlab/cuckoo-filters.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** These are first-party numbers from a single run in the README. The benchmark code is public (src/bin/benchmark.rs) and the release profile is in Cargo.toml, but no CPU model is given and the Rust toolchain version is not pinned ('stable'). The Bloom and Cuckoo(2,4) baselines are the author's own from-scratch implementations, not incumbent libraries.
- **Verifier notes:** The README numbers match the record exactly, and the 12%/25% memory figures are stated on the page. Metadata checks out: MIT license, not a fork, 0 stars, last commit 2026-09-03, active. The claim now includes the insert-speed regression the record left out.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/EvanGruhlkey/WindowFilter>
  - <https://github.com/EvanGruhlkey/WindowFilter#benchmark>
  - <https://github.com/EvanGruhlkey/WindowFilter/blob/main/Cargo.toml>
  - <https://github.com/EvanGruhlkey/WindowFilter/blob/main/rust-toolchain.toml>
  - <https://github.com/EvanGruhlkey/WindowFilter/blob/main/src/bin/benchmark.rs>
  - <https://github.com/EvanGruhlkey/WindowFilter/blob/main/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/EvanGruhlkey/WindowFilter>
  - <https://github.com/EvanGruhlkey/WindowFilter#benchmark>
  - <https://github.com/EvanGruhlkey/WindowFilter/blob/main/README.md>
  - <https://github.com/EvanGruhlkey/WindowFilter/blob/main/Cargo.toml>
  - <https://github.com/EvanGruhlkey/WindowFilter/blob/main/Cargo.lock>
  - <https://github.com/EvanGruhlkey/WindowFilter/blob/main/rust-toolchain.toml>
  - <https://github.com/EvanGruhlkey/WindowFilter/blob/main/.github/workflows/ci.yml>
  - <https://github.com/EvanGruhlkey/WindowFilter/blob/main/src/lib.rs>
  - <https://github.com/EvanGruhlkey/WindowFilter/blob/main/src/hash.rs>
  - <https://github.com/EvanGruhlkey/WindowFilter/blob/main/src/packed.rs>
  - <https://github.com/EvanGruhlkey/WindowFilter/blob/main/src/windowed.rs>
  - <https://github.com/EvanGruhlkey/WindowFilter/blob/main/src/cuckoo.rs>
  - <https://github.com/EvanGruhlkey/WindowFilter/blob/main/src/bloom.rs>
  - <https://github.com/EvanGruhlkey/WindowFilter/blob/main/src/bin/benchmark.rs>
  - <https://github.com/EvanGruhlkey/WindowFilter/blob/main/docs/windowfilter-flow.mmd>
  - <https://github.com/EvanGruhlkey/WindowFilter/commits/main>
  - <https://github.com/EvanGruhlkey/WindowFilter/issues?q=is%3Aissue>
  - <https://github.com/EvanGruhlkey/WindowFilter/actions>
  - <https://crates.io/api/v1/crates/windowfilter>
  - <https://arxiv.org/abs/2505.05847>
  - <https://arxiv.org/pdf/2505.05847v4>
  - <https://gitlab.com/rahmannlab/cuckoo-filters>
  - <https://gitlab.com/rahmannlab/cuckoo-filters/-/raw/main/README.md>
  - <https://gitlab.com/rahmannlab/cuckoo-filters/-/raw/main/LICENSE>
  - <https://hn.algolia.com/api/v1/search?query=EvanGruhlkey%20WindowFilter>
  - <https://hn.algolia.com/api/v1/search?query=%22Smaller%20and%20More%20Flexible%20Cuckoo%20Filters%22>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/evangruhlkey/windowfilter`) · [data/wave6/enrich/raw/github_com_evangruhlkey_windowfilter.json](../../../data/wave6/enrich/raw/github_com_evangruhlkey_windowfilter.json) (enrichment confidence 0.82)

</details>
