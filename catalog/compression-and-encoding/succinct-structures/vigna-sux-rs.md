# sux-rs

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Succinct data structures](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Vigna's Rust succinct-structures crate; Rank9 plus SelectAdapt was fastest of four Rust crates on rank1 and select1.

| | |
|---|---|
| **Beats** | sucds Rank9Sel and vers-vecs RsVec (Rust crates; also succinctly BitVec), not SDSL directly |
| **Claimed result** | rank1 (10,000 random queries, ARM64): sux SelectAdapt&lt;Rank9&lt;AddNumBits&lt;BitVec&gt;&gt;&gt; 9.0-10.8 us vs sucds 16.0-17.9 us (1.5-1.85x), vers-vecs 30.0-34.0 us (2.8-3.8x) and succinctly 14.2-17.9 us (page states 1.5-1.7x) (ratios derived from page data unless stated). select1: sux 55.8-78.7 us vs sucds 70.8-139.7 us (1.0-2.2x; near parity at 1M/90%: 69.3 vs 70.8 us), vers-vecs 174.4-575.6 us (2.6-9.1x) and succinctly 181.0-279.8 us (page states roughly 3-4x) (derived from page data). Fastest of the four crates on both queries in every cell. |
| **Workload** | rank1 and select1 over 10,000 random positions on identical seeded random bit vectors of 1M and 10M bits at 10/50/90% density, SelectAdapt&lt;Rank9&lt;AddNumBits&lt;BitVec&gt;&gt;&gt; |
| **Metric** | throughput |
| **Hardware** | Apple M5 Max (ARM64, 18 cores, 128 GB), macOS 26.5.2 |
| **Compiler and flags** | rustc 1.97.0, cargo bench with criterion 0.5; sux 0.14.0 (no relevant features), sucds 0.8.3 `intrinsics`, vers-vecs 1.10.1 `simd`, succinctly 0.7.0 `simd` (pinned in bench-compare/Cargo.toml); no [profile.bench] override, RUSTFLAGS or target-cpu stated, so default bench profile |
| **Adoption** | 80 stars |
| **Last commit** | 2026-09-11 |
| **Links** | [repository](https://github.com/vigna/sux-rs) · [benchmark](https://github.com/maxi-tools/succinctly/blob/main/docs/benchmarks/rust-succinct-libs.md) |

## Verdict

succinctly's cross-crate benchmark (rustc 1.97.0, criterion, default bench profile with no target-cpu, Apple M5 Max ARM64) timed 10,000 random queries on identical seeded 1M- and 10M-bit vectors: sux 0.14.0 SelectAdapt&lt;Rank9&lt;AddNumBits&lt;BitVec&gt;&gt;&gt; took 9.0-10.8 us for rank1 against 16.0-17.9 us for sucds, 14.2-17.9 us for succinctly and 30.0-34.0 us for vers-vecs, and 55.8-78.7 us for select1 against 70.8-139.7 us for sucds (near parity at 1M/90%) and 174.4-575.6 us for vers-vecs, whose AVX-512 select did not run on ARM64.

## Use it when

- Static bit vectors where both rank1 and select1 latency matter: in the succinctly benchmark (ARM64, 1M and 10M bits, 10-90% density) it was fastest of four Rust crates on both in every cell.
- Pipelines that need rank/select together with Elias-Fano, static functions, MMPHFs or compressed string lists from one coherent, actively developed library.
- Large read-only indexes you want to build once and memory-map (ε-serde zero-copy loading).
- x86-64 builds where you can enable BMI2 (target-cpu=native): in-word select switches to PDEP.

## Skip it when

- Memory-tight bit vectors: the benchmarked Rank9 plus SelectAdapt costs 32-39% over the raw bits (Rank9 alone is 25% by design), against 5-6.5% for vers-vecs; consider RankSmall or vers-vecs instead.
- Small dependency budgets: the crate pulls in anyhow, rayon (default), zstd and flate2 (default), rand, rdst, epserde-related and other crates, and needs Rust 1.85 (edition 2024 on main).
- When API stability matters: 0.14.0 (2026-04-11) was a full rewrite incompatible with 0.13, and the unreleased main changes field names and serialized formats again.
- Loading untrusted serde data: Rank9's safe rank() checks only the position against the bit length, then reads the counter array with get_unchecked, and serde deserialization does not check that the counters match the bits; a crafted file could cause an out-of-bounds read (inferred from reading the source, not tested).
- Bit vectors with mixed very dense and very sparse halves: the SelectAdapt docs warn its select speed then depends on which bit you ask for and suggest Select9.

## How it is fast

Rank9 (Vigna, WEA 2008) interleaves a 64-bit absolute count per 512-bit block with seven 9-bit relative counts in Gog and Petri's reversed order, so rank is at most two cache misses with no loops or branches, and it exposes prefetch hooks. SelectAdapt extends Vigna's 'simple' select with an adaptive two-level inventory: an indexed one every L ones, plus M (default 8, one cache line) words of 16-bit offsets interleaved with it, falling back to 32- or 64-bit spill entries for very sparse stretches, then a short broadword scan. In-word select uses BMI2 PDEP when the build enables bmi2 and a broadword routine otherwise; unchecked accessors skip bounds checks on the hot path.

## Compared with alternatives

Pick sux-rs over sucds when query speed matters most (1.5-1.85x faster rank1 and faster select1 in the same tables) and you can accept heavier dependencies and API churn; pick vers-vecs when space or fast construction matters more; QuadRank/BiRank reports beating sux-rs Rank9 on high-throughput rank, so prefer it for batched rank-only workloads.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | anyhow, mem_dbg, ambassador, impl-tools, lender, num-primitive, atomic-primitive, rand, rdst, value-traits, zerocopy, xxhash-rust, thiserror, crossbeam-channel, dsi-progress-logger, tempfile and others; optional rayon, zstd, flate2 (default on), epserde, serde, mmap |
| **Minimum toolchain** | Rust 1.85 (rust-version); main uses edition 2024; aarch64_prefetch and iter_advance_by features need nightly |
| **Platforms** | 64-bit and 32-bit targets (Rank9 requires 64-bit words, enforced at compile time); x86-64 PDEP path needs bmi2 enabled at build time; wasm32-wasip1 configured in .cargo/config.toml |
| **Thread safety** | not documented for the rank/select structures; they are immutable after construction and queried through &self; AtomicBitVec provides concurrent bit updates (orderings fixed on main) |
| **Drop-in for the baseline** | partial: implements its own Rank/Select traits; rank(pos) returns usize and saturates to num_ones() for pos &gt;= len, while sucds and succinctly return Option; not a drop-in for SDSL or other Rust crates |

## Gotchas

- The repo's .cargo/config.toml sets -C target-cpu=native, so its own benchmarks use native code, but that setting does not apply when sux is a dependency: the succinctly benchmark ran it without target-cpu, and you must set RUSTFLAGS yourself to get PDEP on x86-64.
- The 30-120x slower construction in the benchmark is a harness artifact: it filled BitVec::new(len) with per-bit set(), while sux has unsafe BitVec::from_raw_parts(words, len) to adopt an already-packed Vec&lt;usize&gt; without copying.
- 0.14.0 is still affected by issues fixed only on unreleased main: EliasFano::pred with a value above the upper bound caused undefined behavior (issue #108), Select9 was wrong on very sparse vectors, unsound reference-based From conversions between BitVec and AtomicBitVec were removed, and structures built from deserialized input with dirty padding bits could return spurious rank/select answers. The benchmarked Rank9 plus SelectAdapt answers were cross-checked against the other crates.
- Licence differs by version: published crates up to 0.14.0 are Apache-2.0 OR LGPL-2.1-or-later; main is Apache-2.0 OR MIT. Both allow Apache-2.0 use.

## Known shortcomings

- Rust, not C++. Baselines are the Rust crates sucds and vers-vecs, not SDSL. Independent numbers are ARM64 only (Apple M5 Max) with optimisation flags unstated. Construction is slow.
- Licence caveat: published crates up to 0.14.0 are Apache-2.0 OR LGPL-2.1-or-later; MIT only on unreleased main. Benchmarked 0.14.0 still has bugs fixed only on main: EliasFano::pred UB (#108), a Select9 sparse bug, unsound BitVec/AtomicBitVec From impls, dirty-padding spurious rank/select (the benchmarked Rank9+SelectAdapt answers were cross-checked). Safe Rank9::rank uses get_unchecked on counters with no serde length check, so untrusted serde input is a possible out-of-bounds read (inferred, not tested). The construction gap is a harness artifact (unsafe BitVec::from_raw_parts adopts packed words). The repo's .cargo/config target-cpu=native does not apply as a dependency, so the bench ran without PDEP/BMI2. Heavy dependencies; needs Rust 1.85.

## Caveats and trade-offs

Measured by the rival succinctly project (independent of the sux authors) on ARM64 only; x86_64 run outstanding. vers-vecs' SIMD select is AVX-512-only, so it ran scalar here. select1 cells varied up to about 40% run to run; the page says read ordering, not ratios. Optimisation flags not stated. Baseline is other Rust crates, not SDSL or a C++ incumbent. sux construction is the slowest of the four (1.66-29.81 ms vs vers-vecs 19.7-215.3 us) because it was filled bit at a time with no bulk-word constructor; resident overhead 32-39% vs 5-7% for vers-vecs. The sux-rs README itself only says 'almost always as fast or faster than the ones in other libraries' with no numbers, and points to external vers_benchmarks/cseq_benchmark. Same author family as the catalogued C++ sux (https://github.com/vigna/sux).

Space overhead about 32-39% for the rank+select structure benchmarked (vers-vecs is 5-6.5%, far smaller); construction from bits one at a time is 30-120x slower than vers-vecs because there is no bulk-word constructor in the benchmarked version.

## Maintenance

Very active (about 3,600 commits, last commit 2026-09-11, 0.15.0 in preparation with many soundness and robustness fixes), maintained by Sebastiano Vigna and Tommaso Fontana; copyable under Apache-2.0, though the large dependency tree makes vendoring single structures harder than with the C++ sux.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent measurement by the rival succinctly project (author John Ky, unrelated to Vigna), whose page concludes its own BitVec loses to sux; public harness bench-compare/benches/succinct_libs.rs with versions/features pinned in bench-compare/Cargo.toml and cross-library answer agreement checked, rustc 1.97.0 and Apple M5 Max stated. Optimisation flags are not stated (cargo bench defaults, no target-cpu), so not A.
- **Verifier notes:** Numbers match the page; rank1 ratio vs sucds is 1.5-1.85x rather than 1.6-1.8x and vs vers-vecs 2.8-3.8x rather than 'about 3x'; corrected and added the succinctly comparison. Metadata checked: 80 stars, Apache-2.0 OR MIT, not archived or a fork, last commit 2026-09-11. A Rust project with no C++ baseline; consider whether the C++ sux entry should be the primary listing.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** independent rust-works/succinctly rank/select benchmark (public harness, rustc 1.97.0, Apple M5 Max); independent rust-works/succinctly benchmark
- **Pages the verifier opened:**
  - <https://github.com/maxi-tools/succinctly/blob/main/docs/benchmarks/rust-succinct-libs.md>
  - <https://raw.githubusercontent.com/maxi-tools/succinctly/HEAD/docs/benchmarks/rust-succinct-libs.md>
  - <https://raw.githubusercontent.com/rust-works/succinctly/HEAD/docs/benchmarks/rust-succinct-libs.md>
  - <https://raw.githubusercontent.com/maxi-tools/succinctly/HEAD/bench-compare/Cargo.toml>
  - <https://raw.githubusercontent.com/maxi-tools/succinctly/HEAD/bench-compare/benches/succinct_libs.rs>
  - <https://raw.githubusercontent.com/maxi-tools/succinctly/HEAD/Cargo.toml>
  - <https://github.com/vigna/sux-rs>
  - <https://github.com/vigna/sux-rs/commits>
- **Sources the enricher read:**
  - <https://github.com/vigna/sux-rs>
  - <https://github.com/vigna/sux-rs/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/vigna/sux-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/vigna/sux-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/vigna/sux-rs/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/vigna/sux-rs/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/vigna/sux-rs/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/vigna/sux-rs/HEAD/src/rank_sel/mod.rs>
  - <https://raw.githubusercontent.com/vigna/sux-rs/HEAD/src/rank_sel/rank9.rs>
  - <https://raw.githubusercontent.com/vigna/sux-rs/HEAD/src/rank_sel/select_adapt.rs>
  - <https://raw.githubusercontent.com/vigna/sux-rs/HEAD/src/traits/rank_sel.rs>
  - <https://raw.githubusercontent.com/vigna/sux-rs/HEAD/src/bits/bit_vec.rs>
  - <https://raw.githubusercontent.com/vigna/sux-rs/HEAD/src/utils/select_in_word.rs>
  - <https://raw.githubusercontent.com/vigna/sux-rs/HEAD/src/utils/mod.rs>
  - <https://crates.io/api/v1/crates/sux>
  - <https://raw.githubusercontent.com/maxi-tools/succinctly/HEAD/docs/benchmarks/rust-succinct-libs.md>
  - <https://raw.githubusercontent.com/maxi-tools/succinctly/HEAD/bench-compare/benches/succinct_libs.rs>
  - <https://raw.githubusercontent.com/maxi-tools/succinctly/HEAD/bench-compare/Cargo.toml>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/vigna/sux-rs`) · [data/wave9/enrich/raw/github_com_vigna_sux_rs.json](../../../data/wave9/enrich/raw/github_com_vigna_sux_rs.json) (enrichment confidence 0.75)

</details>
