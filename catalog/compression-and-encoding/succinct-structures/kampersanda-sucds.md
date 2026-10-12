# sucds

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Succinct data structures](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Safe pure-Rust succinct structures (Rank9Sel, DArray, Elias-Fano, wavelet matrix); select1 1.3-7.8x faster than vers-vecs on ARM64.

| | |
|---|---|
| **Beats** | vers-vecs RsVec and succinctly BitVec (Rust crates), not SDSL |
| **Claimed result** | select1 (10,000 random queries, ARM64): sucds Rank9Sel 70.8-139.7 us vs vers-vecs RsVec 174.4-575.6 us, i.e. 1.3x (10M/10%) to 7.8x (1M/90%) faster (derived from page data), and vs succinctly BitVec 181.0-279.8 us, 1.6-3.4x faster (page states 1.6-3.4x). rank1: sucds 16.0-17.9 us, about level with succinctly (14.2-17.9 us; sucds slightly slower at 1M) and 1.8-2.1x faster than vers-vecs 30.0-34.0 us (derived from page data). sux-rs beats sucds on both rank1 and select1 in the same tables. |
| **Workload** | select1 over 10,000 random positions on identical seeded random bit vectors of 1M and 10M bits at 10/50/90% density, Rank9Sel with intrinsics |
| **Metric** | throughput |
| **Hardware** | Apple M5 Max (ARM64, 18 cores, 128 GB), macOS 26.5.2 |
| **Compiler and flags** | rustc 1.97.0, cargo bench with criterion 0.5; sucds 0.8.3 with `intrinsics` feature (pinned in bench-compare/Cargo.toml); no [profile.bench] override, RUSTFLAGS or target-cpu stated, so default bench profile |
| **Adoption** | 108 stars |
| **Last commit** | 2026-08-31 |
| **Links** | [repository](https://github.com/kampersanda/sucds) · [benchmark](https://github.com/maxi-tools/succinctly/blob/main/docs/benchmarks/rust-succinct-libs.md) |

## Verdict

succinctly's own cross-crate benchmark (rustc 1.97.0, criterion, default bench profile, Apple M5 Max ARM64) timed 10,000 random select1 queries on identical seeded 1M- and 10M-bit vectors: sucds 0.8.3 Rank9Sel with `intrinsics` took 70.8-139.7 us against 174.4-575.6 us for vers-vecs RsVec (scalar select on ARM64) and 181.0-279.8 us for succinctly BitVec, while rank1 was level with succinctly and about 2x faster than vers-vecs; sux-rs beat it on both.

## Use it when

- Static bit vectors of millions of bits where you need rank1 and select1 from one structure and want a code base with no unsafe memory tricks.
- select-heavy workloads on ARM64: in the succinctly comparison sucds' select1 beat vers-vecs and succinctly at every size and density tested (1M and 10M bits, 10-90% density).
- Projects that need several succinct families (Elias-Fano, DACs, wavelet matrix) behind one consistent trait API and a built-in serialization format.
- no_std targets with alloc (supported since 0.9.0), and portable builds where the serialized format must not depend on pointer width.

## Skip it when

- Peak rank/select speed: sux-rs was faster on both rank1 (about 1.5-1.85x) and select1 in the same tables.
- Memory-tight bit vectors: rank9 alone costs 25% over the raw bits by design; vers-vecs measured 5-6.5% total overhead against sucds' 36% at 1M bits.
- When you already hold the data as Vec&lt;u64&gt; and build often: there is no constructor that adopts a word vector, so you copy it in (word-at-a-time push_bits works; bit-at-a-time from_bits is far slower).
- Loading untrusted serialized files: deserialize_from does not check that the stored length matches the word count or that the index belongs to the vector, and Vec deserialization reserves the stored length up front, so a crafted file can trigger a huge allocation or later index panics.
- If you need RRR, balanced parentheses or an FM-index: these are open feature requests (#13, #17, #27), not implemented.

## How it is fast

Rank9Sel is Vigna's rank9: per 512-bit block one 64-bit absolute rank plus seven 9-bit sub-block ranks packed into one word, so rank1 is two loads and a popcount. select1 uses optional hints (one per 1024 ones) to narrow a binary search over block ranks, then a broadword parallel compare over the packed 9-bit counts picks the word, and an in-word select finishes with broadword byte sums plus a 2 KB select-in-byte lookup table (no PDEP). The `intrinsics` feature swaps the broadword popcount and bit scans for count_ones/trailing_zeros, which compile to hardware instructions (the docs recommend -C target-cpu=native with it).

## Compared with alternatives

Pick sucds over sux-rs when you want a small, dependency-free, no_std-capable crate with a broad family of structures and no unsafe internals, and can accept slower rank1/select1; pick vers-vecs when space (5-6.5% overhead) or fast construction from Vec&lt;u64&gt; matters more than select speed; QWT (Rust) is the better choice for wavelet trees over larger alphabets.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none (only alloc/std); optional features `std` (default) and `intrinsics` |
| **Minimum toolchain** | Rust 1.62 (rust-version in Cargo.toml for 0.9.x; 1.61 for 0.8.x), edition 2018 |
| **Platforms** | any; tuned for 64-bit, 32-bit support (broadword emulation, under 2^32 bits) merged on 2026-08-31 after the 0.9.1 release |
| **Thread safety** | not documented; query methods take &self on plain Vec-backed structs, so immutable sharing across threads follows normal Rust Send/Sync rules |
| **Drop-in for the baseline** | partial: shares the conceptual rank/select API of other Rust crates but uses its own Rank/Select traits returning Option&lt;usize&gt;; not a drop-in for vers-vecs, sux or SDSL |

## Gotchas

- Rank9Sel::from_bits does not build select hints; call .select1_hints() (and .select0_hints()) or select falls back to a full binary search over all blocks.
- BitVector::from_bits pushes bit by bit into a growing Vec and never calls shrink_to_fit, so resident memory can be up to about 2x the bits: this matches the benchmark's 99% overhead at 10M bits (156,250 words rounded up to a 262,144-word capacity plus the 25% rank directory), against 36% at 1M bits. Build with BitVector::with_capacity and push_bits(word, 64), or shrink before indexing.
- Rank9SelIndex::rank1/select1 are `unsafe fn` only as an API contract (you must pass the same BitVector used at construction); the crate itself uses bounds-checked safe Rust, and a mismatched vector gives wrong answers or a panic rather than memory corruption.
- Even with `intrinsics`, in-word select does not use BMI2 PDEP/TZCNT on x86-64, so select1 leaves some x86 speed on the table compared with PDEP-based implementations.

## Known shortcomings

- Rust, not C++. Baselines are the Rust crates vers-vecs and succinctly, not SDSL. The independent page benchmarked 0.8.3 (current 0.9.1) on an Apple M5 Max only; optimisation flags unstated. Slow construction and 99% space overhead at 10M bits.
- The benchmark's 99% overhead at 10M bits is a harness artifact: BitVector::from_bits never calls shrink_to_fit, so Vec capacity is 262,144 vs 156,250 words, plus rank9's 25%; the harness comment 'per-bit only path' is wrong since push_bits(word,64) exists. deserialize_from does no validation (a stored length can force a huge allocation; length vs words unchecked), so bad files panic. No PDEP path. Benchmarked 0.8.3; 0.9.0 is breaking; 32-bit support unreleased.

## Caveats and trade-offs

Measured by the rival succinctly project (independent of sucds) on ARM64 only; x86_64 run outstanding. vers-vecs' SIMD select is AVX-512-only, so it ran scalar on ARM64 and its select could improve substantially on x86_64. sux-rs is faster than sucds in the same tables. select1 cells varied up to about 40% run to run; the page says read ordering, not ratios. Optimisation flags not stated. Baseline is other Rust crates, not SDSL or a C++ incumbent; vers-vecs is not a widely used incumbent. sucds construction is about 30-37x slower than vers-vecs because it has no bulk-word constructor (bit-at-a-time fill), and its resident overhead is 36% at 1M and 99% at 10M bits vs 5-7% for vers-vecs. Page benchmarked sucds 0.8.3; current release is 0.9.1. README has no performance numbers.

Rank9Sel space overhead 36% at 1M and 99% at 10M bits vs vers-vecs 5-6.5%; construction one bit at a time, 30-120x slower than vers-vecs.

## Maintenance

Actively maintained by Shunsuke Kanda (0.9.1 on 2026-08-29, breaking 0.9.0 API changes on 2026-08-28, 32-bit support merged 2026-08-31, about 950k crates.io downloads), dual MIT/Apache-2.0 safe pure Rust, so it is easy to depend on or vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent measurement: the page is succinctly's own comparison (author John Ky, rust-works/succinctly; maxi-tools/succinctly is a fork carrying a byte-identical copy), unrelated to the sucds author, and succinctly loses to sucds on select1, so there is no bias toward sucds. Harness is public (bench-compare/benches/succinct_libs.rs, features pinned in bench-compare/Cargo.toml, answers cross-checked by verify_agreement) and rustc 1.97.0 plus Apple M5 Max are stated, but optimisation flags are not stated (no [profile.bench] override or .cargo/config in the repo, so cargo bench defaults, no target-cpu), which keeps it short of A.
- **Verifier notes:** All numbers match the page; the record's '6.6x at 1M/90%' was understated (page data gives 554.1/70.8 = 7.8x) and the succinctly select1 range starts at 181.0 not 195.9; corrected. Metadata checked: 108 stars, Apache-2.0 OR MIT, not archived or a fork, last commit 2026-08-31.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** independent rust-works/succinctly rank/select benchmark (public harness bench-compare/benches/succinct_libs.rs, rustc 1.97.0, Apple M5 Max); independent rust-works/succinctly benchmark
- **Pages the verifier opened:**
  - <https://github.com/maxi-tools/succinctly/blob/main/docs/benchmarks/rust-succinct-libs.md>
  - <https://raw.githubusercontent.com/maxi-tools/succinctly/HEAD/docs/benchmarks/rust-succinct-libs.md>
  - <https://raw.githubusercontent.com/rust-works/succinctly/HEAD/docs/benchmarks/rust-succinct-libs.md>
  - <https://raw.githubusercontent.com/maxi-tools/succinctly/HEAD/bench-compare/Cargo.toml>
  - <https://raw.githubusercontent.com/maxi-tools/succinctly/HEAD/bench-compare/benches/succinct_libs.rs>
  - <https://raw.githubusercontent.com/maxi-tools/succinctly/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/maxi-tools/succinctly/HEAD/README.md>
  - <https://github.com/kampersanda/sucds>
  - <https://github.com/kampersanda/sucds/commits>
- **Sources the enricher read:**
  - <https://github.com/kampersanda/sucds>
  - <https://github.com/kampersanda/sucds/issues?q=is%3Aissue>
  - <https://github.com/kampersanda/sucds/commits/main>
  - <https://raw.githubusercontent.com/kampersanda/sucds/HEAD/README.md>
  - <https://raw.githubusercontent.com/kampersanda/sucds/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/kampersanda/sucds/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/kampersanda/sucds/HEAD/src/intrinsics.rs>
  - <https://raw.githubusercontent.com/kampersanda/sucds/HEAD/src/bit_vectors.rs>
  - <https://raw.githubusercontent.com/kampersanda/sucds/HEAD/src/bit_vectors/bit_vector.rs>
  - <https://raw.githubusercontent.com/kampersanda/sucds/HEAD/src/bit_vectors/rank9sel.rs>
  - <https://raw.githubusercontent.com/kampersanda/sucds/HEAD/src/bit_vectors/rank9sel/inner.rs>
  - <https://raw.githubusercontent.com/kampersanda/sucds/HEAD/src/bit_vectors/darray.rs>
  - <https://raw.githubusercontent.com/kampersanda/sucds/HEAD/src/broadword.rs>
  - <https://raw.githubusercontent.com/kampersanda/sucds/HEAD/src/serial.rs>
  - <https://crates.io/api/v1/crates/sucds>
  - <https://raw.githubusercontent.com/maxi-tools/succinctly/HEAD/docs/benchmarks/rust-succinct-libs.md>
  - <https://raw.githubusercontent.com/maxi-tools/succinctly/HEAD/bench-compare/benches/succinct_libs.rs>
  - <https://raw.githubusercontent.com/maxi-tools/succinctly/HEAD/bench-compare/Cargo.toml>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/kampersanda/sucds`) · [data/wave9/enrich/raw/github_com_kampersanda_sucds.json](../../../data/wave9/enrich/raw/github_com_kampersanda_sucds.json) (enrichment confidence 0.75)

</details>
