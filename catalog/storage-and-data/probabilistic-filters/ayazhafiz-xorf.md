# xorf (Rust xor / binary fuse filter crate)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust static xor/binary-fuse filters: about 9 bits/key at 0.4% FPP versus about 11.5 for an optimal Bloom.

| | |
|---|---|
| **Beats** | Bloom filter |
| **Claimed result** | README (qualitative): "Xor filters are faster and smaller than Bloom and Cuckoo filters." xorf's own docs (src/bfuse8.rs) say a BinaryFuse8 filter uses about 9 bits per entry at a false-positive rate of about 2^-8 (&lt;0.4%), and a doc test asserts fewer than 9.1 bits per entry. The crate never measures a Bloom filter. The Bloom comparison exists only in the binary fuse paper (arXiv:2201.01174), measured on the authors' C++ implementation: binary fuse filters are within 13% of the storage lower bound versus 44% for Bloom filters. |
| **Workload** | Same static-set membership storage-overhead comparison as the binary fuse filter paper (xor/binary fuse vs Bloom filters) |
| **Metric** | memory |
| **Adoption** | 171 stars; crates.io `xorf` has about 6.7M total downloads (about 2.16M recent); latest crates.io version is 0.13.0 |
| **Last commit** | 2026-08-21 |
| **Links** | [repository](https://github.com/ayazhafiz/xorf) · [benchmark](https://arxiv.org/abs/2201.01174) |

## Verdict

Nothing in this crate measures a Bloom filter: its doc tests only assert BinaryFuse8 stays under 9.1 bits/key with under 0.406% false positives on 1M random u64 keys, and its Criterion benches time only xorf's own filters (the lookup bench repeats one hot key). The Bloom comparison (binary fuse within 13% of the storage lower bound vs 44% for Bloom, i.e. about 9 vs about 11.5 bits/key at 2^-8) comes from the binary fuse paper (JEA 2022), which benchmarks the authors' C++ code (GCC 10 -O3 -march=native, Intel i7-6700 Skylake), not this Rust port; the 9-bit figure carries over by construction, but speed does not.

## Use it when

- Static or rebuild-occasionally sets that are queried far more often than built, such as SST/segment filters, blocklists, dedup pre-checks and 'is this key on disk' guards, where filter RAM is what you are trying to cut.
- You already have 64-bit hashes, or can hash keys yourself, and a fixed FPP of about 0.39% (8-bit), about 0.0015% (16-bit) or effectively zero (32-bit) suits you.
- Rust services or embedded/no_std targets with an allocator. CI checks thumbv7em-none-eabi with default features off.
- Filters persisted to disk and loaded without copying: `BinaryFuse*Ref::from_dma` borrows the fingerprint bytes from an mmap'd buffer and copies only a 20-byte descriptor.
- Sets of about a million keys or more. The paper measures the 3-wise layout reaching 9 bits/key there, while below about 20k keys the xor filter can be as small or smaller.

## Skip it when

- You need inserts, deletes or counting. Every filter is rebuilt from the full key set; use a cuckoo or quotient filter instead.
- You want to tune FPP against space continuously, the way Bloom parameters allow. Only 8, 16 and 32-bit fingerprints exist, and the maintainer says in issues #61 and #69 that space per item cannot be reduced.
- Query latency on huge filters is the goal. Each lookup touches three random cache lines. A user in issue #84 measured about 280 M lookups/s at 1M keys falling to about 51 M/s at 99M keys, and in the binary fuse paper an AVX2 blocked Bloom filter queried faster than any xor-family filter.
- Building very large sets under a memory cap. From reading the code, BinaryFuse construction allocates about 13 bytes per slot plus 9 bytes per key of scratch (about 24 B/key) on top of your u64 key array, for a result of about 1.1 B/key.
- You need the smallest possible static filter. xorf has no 4-wise binary fuse (8.6 bits/key in the paper), and Ribbon filters (BuRR, RocksDB) get closer to the lower bound.

## How it is fast

Each key maps to three fingerprint slots: construction peels a random 3-uniform hypergraph so that fingerprint(key) = F[h0] ^ F[h1] ^ F[h2], and a query is one MurmurHash3 finalizer mix plus three array reads, with no SIMD. Binary fuse filters (Graf & Lemire, arXiv:2201.01174) put the three slots in adjacent power-of-two segments (a binary-partitioned fuse graph), so the array needs about 1.125n slots instead of the xor filter's 1.23n + 32. Fingerprint width alone sets the FPP (about 2^-8, 2^-16 or 2^-32) at about 9, 18 or 36 bits/key, where a Bloom filter needs about 1.44·log2(1/ε) bits/key. The code is a port of Go FastFilter/xorfilter and uses only the 3-wise variant.

## Compared with alternatives

Pick xorf when you are in Rust and want the xor_singleheader/xorfilter algorithms natively, with no_std support and zero-copy mmap loading; use those C/Go originals in their own languages. Choose BuRR or RocksDB Ribbon instead when the last few percent of space matter more than query speed (the binary fuse paper measured ribbon queries slower), and a cuckoo filter or CQF when the set must accept inserts or deletes.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | libm (via the default `binary-fuse` feature) and rand (via the default `uniform-random` feature, which needs std). Optional: serde plus serde_bytes. The published 0.13.0 also has an optional `bincode` 2.0.0-rc.3 dependency, which is flagged unmaintained (RUSTSEC-2025-0141, issue #98). Unreleased master (0.14.0) removes it and keeps `bincode` only as an alias for `serde`. |
| **Minimum toolchain** | Rust 1.85 on master (edition 2024, MSRV job in CI). The published 0.13.0 is edition 2021 and declares no rust-version, so its MSRV is not documented. |
| **Platforms** | Any Rust target with `alloc`. The code is portable and has no arch-specific intrinsics. no_std builds are CI-checked on thumbv7em-none-eabi without default features. |
| **Thread safety** | Not documented. Built filters are immutable, `contains` takes &self, and the fields are plain owned data (Descriptor plus Box&lt;[uN]&gt;), so the auto traits make them Send + Sync and safe to share read-only. |
| **Drop-in for the baseline** | partial — it replaces a Bloom filter only for static sets. You must pre-hash keys to distinct u64s (or use HashProxy), build all at once, accept a fixed FPP per fingerprint width, and handle a fallible build for BinaryFuse. There are no add, union or clear operations. |

## Gotchas

- Keys must be distinct. Debug builds check this with a BTreeSet and panic; in release, BinaryFuse drops exact duplicate hashes, but the Xor family's unbounded retry loop never terminates on duplicates (issue #25). BinaryFuse gives up after 1,000 deterministic seeds with Err("Failed to construct binary fuse filter."), and before 0.13.0 about 1 in 60k distinct key sets just past a segment-length step (n ≈ 11.5k) could never build (PR #100).
- `HashProxy` requires `From<Vec<u64>>`, which BinaryFuse types do not implement (they only have TryFrom), so the recommended filters cannot be wrapped. Issue #72 is closed, but the code still lacks the impl. Hash keys yourself or wrap Xor8 instead.
- Filter bytes are not reproducible by default. The `uniform-random` feature fills unused slots from the thread RNG (issue #77); disable default features for byte-identical output. DMA fingerprints for the 16/32-bit types are raw native-endian memory, although the descriptor is little-endian, and `from_dma` panics on misaligned buffers (it uses unsafe `from_raw_parts` after assert checks).
- The README on master says `xorf = "0.14"`, but crates.io's newest version is 0.13.0, so that line does not resolve yet. BinaryFuse index arithmetic is u32, so one filter addresses at most 2^32 slots (about 3.8B keys); this limit is not documented.

## Known shortcomings

- The paper's numbers come from the C++ reference code and never mention xorf; the crate never benchmarks a Bloom filter (its docs say \~9 bits/entry and a test asserts &lt;9.1).
- Static only, with fixed 8/16/32-bit fingerprints (#61/#69). Duplicate keys make Xor loop forever in release builds (#25) and BinaryFuse errors after 1000 seeds; boundary-size build failures fixed only in 0.13.0. HashProxy cannot wrap BinaryFuse (#72). Build scratch \~24 B/key; lookups are cache-miss bound (280 to 51 M/s from 1M to 99M keys, #84); its own lookup bench uses one hot key.
- The README says 0.14 but crates.io's latest is 0.13.0, whose optional bincode dependency is flagged unmaintained (RUSTSEC-2025-0141). Serialized bytes are native-endian and non-reproducible; unsafe from_raw_parts; u32 index caps it at \~3.8B keys.

## Caveats and trade-offs

No Bloom or cuckoo filter is benchmarked anywhere in the crate: benches/ covers only xorf's own xor, fuse and binary fuse types. The 13%/44% figures come from the binary fuse paper, measured on FastFilter/fastfilter_cpp (C++, GCC 10 -O3 -march=native, i7-6700), and that paper does not mention this Rust port. The memory advantage follows from the algorithm's array sizing, and xorf's doc test (under 9.1 bits per entry) matches the paper's 9 bits per key, so it should carry over. It is still unmeasured against Bloom for this code. Query and build speed are not established for this implementation.

no_std + alloc design; immutable static filter; binary-fuse feature pulls in a `libm` dependency

## Maintenance

Actively maintained and MIT-licensed, with about 6.7M crates.io downloads: 0.13.0 shipped on 2026-08-21 with the segment-boundary construction fix, and master already carries an unreleased 0.14.0 (edition 2024, MSRV 1.85, native bincode support removed).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** The 13%/44% storage figures are in the arXiv:2201.01174 abstract (JEA 27, 2022), but that paper measures the authors' C++ code in FastFilter/fastfilter_cpp and never mentions xorf. xorf's own evidence is first-party: its docs say BinaryFuse8 uses about 9 bits per entry at about 2^-8 FP, and a doc test asserts fewer than 9.1 bits per entry. Its benches/ time only xorf's own filters and never a Bloom filter, so the Bloom side is theoretical and the evidence is C, not B.
- **Verifier notes:** Downgraded from B to C for consistency with ribbongo (batch-25) and binfuse (batch-24): peer-reviewed numbers about another implementation do not count as this crate's evidence. Metadata is correct: MIT, 171 stars, last commit 2026-08-21, active, not a fork or archived. The crate is widely used (about 6.7M crates.io downloads).
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://export.arxiv.org/abs/2201.01174>
  - <https://arxiv.org/pdf/2201.01174>
  - <https://github.com/ayazhafiz/xorf>
  - <https://github.com/ayazhafiz/xorf/blob/master/src/lib.rs>
  - <https://github.com/ayazhafiz/xorf/blob/master/src/bfuse8.rs>
  - <https://crates.io/api/v1/crates/xorf>
- **Sources the enricher read:**
  - <https://github.com/ayazhafiz/xorf>
  - <https://github.com/ayazhafiz/xorf/blob/master/README.md>
  - <https://github.com/ayazhafiz/xorf/blob/master/Cargo.toml>
  - <https://github.com/ayazhafiz/xorf/blob/0.13.0/Cargo.toml>
  - <https://github.com/ayazhafiz/xorf/blob/master/src/lib.rs>
  - <https://github.com/ayazhafiz/xorf/blob/master/src/bfuse8.rs>
  - <https://github.com/ayazhafiz/xorf/blob/master/src/bfuse16.rs>
  - <https://github.com/ayazhafiz/xorf/blob/master/src/bfuse32.rs>
  - <https://github.com/ayazhafiz/xorf/blob/master/src/fuse8.rs>
  - <https://github.com/ayazhafiz/xorf/blob/master/src/xor8.rs>
  - <https://github.com/ayazhafiz/xorf/blob/master/src/prelude/mod.rs>
  - <https://github.com/ayazhafiz/xorf/blob/master/src/prelude/bfuse.rs>
  - <https://github.com/ayazhafiz/xorf/blob/master/src/prelude/xor.rs>
  - <https://github.com/ayazhafiz/xorf/blob/master/src/hash_proxy.rs>
  - <https://github.com/ayazhafiz/xorf/blob/master/src/murmur3.rs>
  - <https://github.com/ayazhafiz/xorf/blob/master/src/splitmix64.rs>
  - <https://github.com/ayazhafiz/xorf/blob/master/benches/bfuse8.rs>
  - <https://github.com/ayazhafiz/xorf/blob/master/tests/boundary_size_construction.rs>
  - <https://github.com/ayazhafiz/xorf/blob/master/.github/workflows/ci.yml>
  - <https://github.com/ayazhafiz/xorf/commits/master>
  - <https://github.com/ayazhafiz/xorf/compare/0.13.0...master>
  - <https://github.com/ayazhafiz/xorf/pull/100>
  - <https://github.com/ayazhafiz/xorf/issues/98>
  - <https://github.com/ayazhafiz/xorf/issues/84>
  - <https://github.com/ayazhafiz/xorf/issues/77>
  - <https://github.com/ayazhafiz/xorf/issues/72>
  - <https://github.com/ayazhafiz/xorf/issues/69>
  - <https://github.com/ayazhafiz/xorf/issues/61>
  - <https://github.com/ayazhafiz/xorf/issues/38>
  - <https://github.com/ayazhafiz/xorf/issues/25>
  - <https://github.com/ayazhafiz/xorf/issues/16>
  - <https://crates.io/api/v1/crates/xorf>
  - <https://export.arxiv.org/api/query?id_list=2201.01174>
  - <https://arxiv.org/pdf/2201.01174>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/ayazhafiz/xorf`) · [data/wave6/enrich/raw/github_com_ayazhafiz_xorf.json](../../../data/wave6/enrich/raw/github_com_ayazhafiz_xorf.json) (enrichment confidence 0.85)

</details>
