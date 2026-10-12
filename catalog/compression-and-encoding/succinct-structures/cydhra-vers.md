# vers (vers-vecs)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Succinct data structures](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Pure-Rust succinct structures (rank/select bit vector, Elias-Fano, RMQ, wavelet matrix, BP tree) benchmarked against other Rust crates only.

| | |
|---|---|
| **Beats** | Rust crates succinct (rank9), rsdict, bio, fid, indexed_bitvec, sucds (rank9, darray); range_minimum_query and librualg for RMQ; bitm and qwt mentioned but not plotted as winners |
| **Claimed result** | Qualitative: 'among the fastest publicly available bit vector implementations for rank and select'; 'substantially lower memory overhead than alternatives'; 'outperforms both [RMQ crates] by a significant margin'; BMI2/popcnt intrinsics speed rank and select by 2 to 3x. The succinct crate is faster on rank. Results are SVG plots, no numeric table on the page. |
| **Workload** | Bit-vector rank and select, Elias-Fano access and predecessor, and range-minimum queries versus other Rust crates, plus heap overhead of the bit vector. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 7950X, 32 GB RAM |
| **Compiler and flags** | target-cpu=native, simd feature enabled (requires AVX-512), rsdict simd feature on nightly Rust |
| **Adoption** | 134 stars |
| **Last commit** | 2026-08-10 |
| **Links** | [repository](https://github.com/Cydhra/vers) · [benchmark](https://github.com/Cydhra/vers/blob/HEAD/readme.md) |

## Verdict

First-party criterion plots (no numeric table) on a Ryzen 9 7950X with target-cpu=native and Vers' simd feature compare rank/select, heap overhead, Elias-Fano access/predecessor and RMQ only against other Rust crates (succinct rank9, rsdict, bio, fid, indexed_bitvec, sucds, bitm; range_minimum_query, librualg); the claim is qualitative ('among the fastest'), succinct's rank9 wins on rank, and the 2-3x figure is Vers with versus without BMI2/popcnt. The benchmark Cargo.toml has rsdict's simd feature commented out although the README says it was enabled, lists sux 0.14 as a dependency although no sux results appear in the README plots, and does not state the rustc version.

## Use it when

- Rust project on x86-64 with BMI2 and popcnt (build with -C target-cpu=native or +bmi2,+popcnt) that needs both rank and select on a static bit vector with about 5.5 percent overhead (doc comment: 28 bits per 512 bits).
- Static monotone integer sequences in Rust where Elias-Fano predecessor/successor queries must have a logarithmic worst case (README notes sucds degrades to linear on adversarial input).
- Range-minimum queries over large u64 arrays in Rust where FastRmq's lower memory than a sparse table matters (BinaryRmq exceeded 32 GB in the author's largest runs).
- You want one dependency-free crate (std only by default) covering bit vector, Elias-Fano, RMQ, wavelet matrix and BP tree with serde support behind a feature.

## Skip it when

- C++ code bases: there are no C or C++ bindings; SDSL, sux (C++) or the C++ siblings below are the native options.
- Rank-heavy workloads: the README itself says the succinct crate's rank9 substantially outperforms Vers on rank, and the catalogued sux-rs entry measured sux Rank9 rank1 2.8-3.8x faster than vers-vecs RsVec (ARM64).
- Non-x86 targets such as aarch64: PDEP/TZCNT fall back to portable code the README calls significantly slower; the catalogued sucds entry measured vers-vecs select1 1.3x to 7.8x slower than sucds Rank9Sel on ARM64.
- Wavelet-tree style queries at scale: the README says qwt is substantially faster because of fewer cache misses, and no wavelet-matrix benchmarks are published.
- Mutable bit vectors with rank/select: RsVec is immutable; changes require into_bit_vec and a full rebuild.

## How it is fast

RsVec uses a two-level rank directory: 512-bit blocks with a 16-bit zero count relative to 8192-bit super-blocks that hold an absolute count, so rank is two table loads plus popcount over at most 7 words. Select samples every 8192th 0-bit and 1-bit to pick a super-block range, binary-searches super-blocks, then does a manually unrolled binary search over the 16 block counts (or, with the simd feature and AVX-512BW/VL, one 256-bit unsigned compare plus mask popcount), and finishes inside a 64-bit word with the PDEP + TZCNT select trick (pdep code copied from the MIT bitintr crate). FastRmq is a block-decomposed linear-space RMQ design that uses small per-block bit vectors with rank/select instead of logarithmic-size tables.

## Compared with alternatives

Among Rust siblings, pick sux-rs for the fastest rank and sucds for select on ARM; pick Vers when you want one dependency-free crate covering bit vector, Elias-Fano with logarithmic worst-case predecessor, RMQ, wavelet matrix and BP tree on x86-64 with BMI2. Pick QWT (Rust) for wavelet-tree workloads, and the C++ entries (succinct-bitvec-cpp, 3star-rankselect, SPIDER) when you are in C++.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none by default; optional serde (derive) and mem_dbg 0.4.3 features |
| **Minimum toolchain** | Rust edition 2021; no rust-version field in Cargo.toml, and the code calls usize::is_multiple_of, so in practice Rust 1.87 or newer |
| **Platforms** | any Rust target; fast path needs x86-64 BMI1/BMI2 and popcnt; simd feature needs AVX, AVX2, AVX-512F/BW/VL (cfg-gated at compile time, no runtime dispatch) |
| **Thread safety** | not documented; structures are immutable after construction and hold only Vecs, so they are Send and Sync by Rust auto traits |
| **Drop-in for the baseline** | no |

## Gotchas

- simd feature: the AVX-512 BitSetIter (bit_set_iter0/bit_set_iter1) mishandles the final 16-bit chunk. Reading bitset.rs at HEAD (v1.10.2), it loads the last chunk with SIMD, then when no further chunk exists re-scans bit by bit from that same chunk base, so matching bits in the last chunk are returned twice; bit_set_iter0 also returns padding positions &gt;= len() when len is not a multiple of 16. A Python transcription of the logic gives 48 items for a 32-bit all-ones vector instead of 32. The crate's tests only use vectors whose last chunk has no matching bits, so they pass. Found by reading source, not by running the crate; the default (non-simd) iter0/iter1 are not affected.
- Recent correctness history: closed bugs #6 and #8 (iter1 errors, including length &gt; 8192), #29 (from_bit_vec panic after append_bits(u64::MAX, 1)), and on 2026-08-09 fixes for successor0 rank adjustment, the select-block upper-bound sentinel, and garbage bits when appending zeros. Use 1.10.2 or later.
- Performance bug fixed 2026-08-09: the select1 super-block binary search undershot its upper bound and fell back to linear search in all cases; the published select plots were made earlier (benchmark repo last commit 2026-06-09, vers submodule pinned at 4c495ae), so they reflect the pre-fix code.
- Naming and docs: get_unchecked is a safe function that may panic or return garbage, not an unsafe unchecked access; the README calls the BP lookup feature u16_lookup while Cargo.toml names it bp_u16_lookup; issue #19 showed the documented select1(rank1(pos)) == pos only holds when pos is a 1-bit.

## Known shortcomings

- Tier C: Rust crates only, plots only, no rustc version.
- Correctness bug with the simd feature (read from source, not run): BitSetIter (bit_set_iter0/bit_set_iter1, src/bit_vec/fast_rs_vec/bitset.rs at v1.10.2) re-scans the last 16-bit chunk after loading it, so its matches come out twice, and iter0 also returns padding positions &gt;= len; crate tests miss it. Default iter0/iter1 are fine. Published select plots predate the 2026-08-09 fix in which select1's superblock binary search fell back to linear search (measured code was slower, not faster); same-day successor0 and select-sentinel fixes and a 2026-08-07 zero-append garbage fix. Baselines are Rust crates only (no SDSL or sux C++); the bench Cargo.toml has rsdict simd commented out although the README says enabled; sux 0.14 is a dependency yet absent from plots; rustc version unstated. Rust &gt;= 1.87 in practice with no rust-version field. No C++ bindings.

## Caveats and trade-offs

Compares only against other Rust crates, not SDSL or sux, so it does not beat the named baselines of this category. README states the succinct crate's rank9 substantially outperforms Vers on rank, and qwt is substantially faster for wavelet-matrix style queries. Benchmark repo (Cydhra/vers_benchmarks, 2 stars) has no README and its results are plots, so no numbers were verified; rustc version not stated. The 2 to 3x figure is BMI2/popcnt intrinsics versus Vers without them, not versus a competitor. The simd feature needs AVX-512. Included as shootout context for Rust succinct libraries.

Pure Rust crate; not usable from C++ without bindings. SIMD feature needs AVX-512 and unsafe code. Wavelet matrix, Elias-Fano, BP tree included.

## Maintenance

Actively maintained (v1.10.2 on crates.io 2026-08-10, about 174k downloads, 3 open issues, 2.0 breaking-change wishlist open); MIT OR Apache-2.0, std-only by default and easy to depend on from Rust, but not usable from C++ without writing an FFI layer.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README benchmarks with public code (Cydhra/vers_benchmarks), CPU (Ryzen 9 7950X) and flag (target-cpu=native) stated, but no rustc version and results only as SVG plots without numeric values; comparisons are only against other Rust crates (succinct rank9, rsdict, sucds, bio, fid, indexed_bitvec; RMQ crates), not the C++ SDSL/sux incumbents.
- **Verifier notes:** README and repo page match the record (Apache-2.0 OR MIT, 134 stars, last commit 2026-08-10). Tier C stands; claim is qualitative and not against C++ incumbents.
- **Fields the verifier corrected:** `baseline`, `caveats`
- **Shortcomings recorded by:** verifier; first-party benchmark (public bench repo pinned at vers 4c495ae)
- **Pages the verifier opened:**
  - <https://github.com/Cydhra/vers>
  - <https://github.com/Cydhra/vers/commits>
  - <https://raw.githubusercontent.com/Cydhra/vers/HEAD/readme.md>
  - <https://raw.githubusercontent.com/Cydhra/vers/HEAD/images/rank_comparison.svg>
  - <https://github.com/Cydhra/vers_benchmarks>
- **Sources the enricher read:**
  - <https://github.com/Cydhra/vers>
  - <https://raw.githubusercontent.com/Cydhra/vers/HEAD/readme.md>
  - <https://raw.githubusercontent.com/Cydhra/vers/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Cydhra/vers/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/Cydhra/vers/HEAD/src/bit_vec/fast_rs_vec/mod.rs>
  - <https://raw.githubusercontent.com/Cydhra/vers/HEAD/src/bit_vec/fast_rs_vec/select.rs>
  - <https://raw.githubusercontent.com/Cydhra/vers/HEAD/src/bit_vec/fast_rs_vec/bitset.rs>
  - <https://raw.githubusercontent.com/Cydhra/vers/HEAD/src/bit_vec/fast_rs_vec/tests.rs>
  - <https://raw.githubusercontent.com/Cydhra/vers/HEAD/src/bit_vec/fast_rs_vec/iter.rs>
  - <https://raw.githubusercontent.com/Cydhra/vers/HEAD/src/bit_vec/mod.rs>
  - <https://raw.githubusercontent.com/Cydhra/vers/HEAD/src/bit_vec/sparse.rs>
  - <https://raw.githubusercontent.com/Cydhra/vers/HEAD/src/util/mod.rs>
  - <https://raw.githubusercontent.com/Cydhra/vers/HEAD/src/util/pdep.rs>
  - <https://raw.githubusercontent.com/Cydhra/vers/HEAD/src/elias_fano/mod.rs>
  - <https://raw.githubusercontent.com/Cydhra/vers/HEAD/src/rmq/fast_rmq/mod.rs>
  - <https://raw.githubusercontent.com/Cydhra/vers/HEAD/src/rmq/binary_rmq/mod.rs>
  - <https://raw.githubusercontent.com/Cydhra/vers/HEAD/.github/workflows/rust.yml>
  - <https://github.com/Cydhra/vers/issues?q=is%3Aissue>
  - <https://github.com/Cydhra/vers/issues/19>
  - <https://github.com/Cydhra/vers/issues/29>
  - <https://github.com/Cydhra/vers/commits/master>
  - <https://crates.io/api/v1/crates/vers-vecs>
  - <https://github.com/Cydhra/vers_benchmarks>
  - <https://github.com/Cydhra/vers_benchmarks/commits/master>
  - <https://raw.githubusercontent.com/Cydhra/vers_benchmarks/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Cydhra/vers_benchmarks/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/Cydhra/vers_benchmarks/HEAD/.gitmodules>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/cydhra/vers`) · [data/wave9/enrich/raw/github_com_cydhra_vers.json](../../../data/wave9/enrich/raw/github_com_cydhra_vers.json) (enrichment confidence 0.75)

</details>
