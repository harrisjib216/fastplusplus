# QuadRank / BiRank

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Succinct data structures](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust rank structures for bit vectors and 2-bit DNA, one cache miss per query; about 2x sux-rs Rank9 throughput with prefetching.

| | |
|---|---|
| **Beats** | sux-rs Rank9 and RankSmall (Rust implementation of sux), qwt RSNarrow/RSWide/RSQVector, bitm RankSelect101111 and genedex rank structures; for the FM-index: genedex and AWRY |
| **Claimed result** | README: BiRank and QuadRank 'up to 2x faster than other methods in high-throughput settings'; QuadFm 'up to 4x faster than genedex'. From evals/rank-laptop.csv at n=2^35 bits, 12 threads, prefetched stream mode: BiRank (BinaryBlock16, 3.3% overhead) 2.63 ns/query vs sux Rank9 4.92 ns and RankSmall&lt;1,11&gt; 5.71 ns, i.e. 1.9x and 2.2x (derived from page data); single-thread latency is not better (94.66 vs 89.42 ns for Rank9). QuadRank 2.6-2.7 ns vs qwt RSQVector256 5.68-6.79 ns in the same mode (derived from page data). evals/fm.csv: best QuadFm 0.156 s vs best genedex 0.312 s at 12 threads (2.0x) and 0.988 vs 2.463 s at 1 thread (2.5x); up to 5.3x vs the slowest genedex configuration (derived from page data). Paper snippet: about 1.5x and 2x faster than similar-overhead methods without interleaving, plus about 2x more from prefetching. |
| **Workload** | Rank over bit vectors and 2-bit DNA text under batched and prefetched queries (1, 6 and 12 threads); FM-index count-only mapping of simulated 150bp reads (1% error) against a 3.1 Gbp human genome with 12 threads. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-10750H (6 cores, hyper-threading), fixed at 3.0 GHz; 1, 6 and 12 threads (README; paper snippet says all experiments ran on this CPU). evals/rank-server.csv is from an unnamed 48/96-thread server. |
| **Compiler and flags** | rustc (rust-version 1.93, edition 2024) via cargo run -r; -C target-cpu=native from .cargo/config.toml; AVX2 only |
| **Adoption** | 18 stars; crates.io quadrank |
| **Last commit** | 2026-04-01 |
| **Links** | [repository](https://github.com/RagnarGrootKoerkamp/quadrank) · [benchmark](https://github.com/RagnarGrootKoerkamp/quadrank/tree/master/evals) |

## Verdict

The repo's committed bench (examples/bench.rs, cargo run -r with -C target-cpu=native, rustc &gt;= 1.93) on an Intel i7-10750H fixed at 3.0 GHz measured BiRank at about 1.9x the throughput of sux-rs Rank9 and 2.2x RankSmall&lt;1,11&gt; for prefetched streams at 12 threads on a 2^35-bit vector, with no gain in single-query latency; QuadFm counts 150bp reads against a 3.1 Gbp genome 2.0x (12 threads) to 2.5x (1 thread) faster than the best genedex configuration. Against genedex's FlatText rank (2.67x space) QuadRank's lead narrows to about 1.2x (3.28 vs 2.68 ns, derived from page data).

## Use it when

- High-throughput rank over very large bit vectors (GBs, far beyond L3) where queries are independent and can be prefetched in batches or streams.
- FM-index / BWT backward search over DNA (2-bit alphabet) where you need rank for all 4 symbols at the same position; QuadFm counts reads against a human genome 2.0-2.5x faster than the best genedex configuration in the repo's fm.csv.
- Space-constrained binary rank: BiRank16 has 3.3% overhead yet streamed 2.63 ns/query at 12 threads on n=2^35 bits vs 4.92 ns for sux-rs Rank9 (25% overhead).
- Rust projects on x86-64 with AVX2 that already pack data into u64 words.

## Skip it when

- Single dependent queries (pointer-chasing, latency-bound): at n=2^35, 1 thread, latency mode BiRank16 took 94.66 ns vs Rank9 89.42 ns, so no gain.
- You need select, dynamic updates, or a general alphabet: only rank over sigma 2 and 4 is provided.
- Non-x86 targets: the quad module imports std::arch::x86_64 unconditionally and NEON support is an open issue (#2); only AVX2 is supported.
- C++ codebases that want a header: this is a Rust crate; from C++ you would need an FFI layer, or reimplement the cache-line layout yourself.
- Small bit vectors that fit in cache: the prefetching advantage shrinks (the CSV shows qwt RSNarrow at 0.72 ns stream/12 threads for n=8192).

## How it is fast

Each 512-bit cache line holds both the data bits and an inline rank counter (BinaryBlock16 stores 496 bits plus a 16-bit count to the middle of the line), so a query touches one cache line plus a small superblock array that usually stays in cache. The in-block count masks and popcounts at most 256 bits forward or backward from the stored midpoint, and QuadRank interleaves the transposed 2-bit data with per-symbol counters and uses SIMD (wide u32x4, SSSE3 _mm_sign_epi32) to compute all four counts at once. Most of the gain comes from software prefetching and batching independent queries, which turns memory latency into memory-bandwidth-bound throughput.

## Compared with alternatives

Pick it over SPIDER when you are in Rust and want the same \~3.3% overhead with a single cache-line access and prefetch hooks (the repo's own Spider-style block streamed 2.81 vs 2.63 ns at 12 threads and 17.82 vs 10.12 ns at 1 thread); pick it over QWT (Rust) for 4-symbol DNA rank, where QuadRank16 streamed 2.68 ns vs 5.68 ns for qwt RSQVector256 at similar overhead. Stay with QWT or the C++ quad-wavelet-tree for larger alphabets, select or access queries.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | mem_dbg, packed-seq, prefetch-index, rayon, dyn_size_of, wide, perfcnt (benchmark baselines behind the optional ext feature) |
| **Minimum toolchain** | Rust 1.93 (edition 2024); stable since v0.2.0 |
| **Platforms** | x86-64 with AVX2 (build with -C target-cpu=native); no aarch64/NEON yet |
| **Thread safety** | Structures are Send + Sync and immutable after construction, so concurrent queries are safe; construction itself is parallelized with rayon. |
| **Drop-in for the baseline** | partial — same rank semantics as sux-rs Rank9 (count of ones before pos) but a different trait, unsafe unchecked calls only, and no select |

## Gotchas

- Only unsafe rank_unchecked APIs exist; pos must be in 0..=n, and the BinaryBlock16 query deliberately reads past the data bytes into the counter field as padding.
- The README's API listing is stale relative to v0.2.0 (RankerT was renamed to BiRanker/QuadRanker, and constructors are new_packed/new_ascii_dna); follow lib.rs docs and docs.rs.
- Benchmark baselines (sux-rs, qwt, genedex, bitm, AWRY) are pulled from the author's own patched forks via [patch.crates-io], so measured competitors are not exactly the upstream releases.
- Speed depends on the caller prefetching ahead; a plain loop without prefetching gave 4.96 ns vs 2.63 ns with streaming prefetch for BiRank16 at 12 threads.

## Known shortcomings

- Upgraded B to A: bench.rs, raw CSVs, target-cpu=native and an i7-10750H are all in the repo; vs sux-rs Rank9/RankSmall at 2^35 bits with 12 threads and prefetch 2.63 vs 4.92 ns (1.9x derived from page data), but single-thread latency is not better. The exact rustc version is unstated (minimum 1.93). Rust.
- Baselines (sux-rs, qwt, genedex, bitm, AWRY) come from the author's patched forks via [patch.crates-io]; the quad module imports std::arch::x86_64 unconditionally, so x86-only (NEON issue #2 open); the README API is stale vs v0.2.0. The lead over genedex FlatText rank is only about 1.2x (3.28 vs 2.68 ns, derived from page data) and there is no latency gain (94.66 vs 89.42 ns for Rank9).

## Caveats and trade-offs

Rust crate (callable from C++ only via FFI). Peer-reviewed at SEA 2026 (LIPIcs), but the paper, blog and Dagstuhl pages are blocked here; claims checked against the repo's committed CSVs. The speedup is for batched/prefetched high-throughput queries; single-query latency is on par with or slightly worse than sux Rank9. The sux baseline is sux-rs (Rust), not the C++ sux, and SDSL is not compared. The paper says SPIDER is about as fast; the repo includes its own BinaryBlock16Spider variant. No LICENSE file; MIT comes from Cargo.toml. AVX2 only. Exact rustc version not stated (rust-version 1.93 is the minimum).

Needs AVX2; gains come from batching and prefetching, so single dependent queries gain less. Rust API with packed u64 input, unsafe unchecked ranks. Not directly usable from C++.

## Maintenance

Active (last commit 2026-04-01, v0.2.0 on crates.io since 2026-02-04, 155 downloads), MIT per Cargo.toml with no LICENSE file; young, single-author research code backing a SEA 2026 paper.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded: the repo carries the benchmark code (examples/bench.rs, which runs sux-rs Rank9/RankSmall, qwt, bitm and genedex structures), raw result CSVs (evals/rank-laptop.csv, evals/fm.csv), release build with -C target-cpu=native (.cargo/config.toml), rustc via cargo (rust-version 1.93), and the CPU (Intel Core i7-10750H, README and SEA 2026 paper snippet). Exact rustc version is only lower-bounded by rust-version; the paper itself is peer-reviewed at SEA 2026 (LIPIcs).
- **Verifier notes:** Strong evidence: raw CSVs plus bench code against sux-rs Rank9/RankSmall, qwt and genedex. Upgraded B to A; if the orchestrator requires an exact compiler version for A, B (SEA 2026 peer review) is the fallback.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `baseline_in_list`, `compiler_and_flags`, `hardware`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/RagnarGrootKoerkamp/quadrank>
  - <https://github.com/RagnarGrootKoerkamp/quadrank/commits/master>
  - <https://github.com/RagnarGrootKoerkamp/quadrank/tree/master/evals>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/quadrank/HEAD/README.md>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/quadrank/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/quadrank/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/quadrank/HEAD/examples/bench.rs>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/quadrank/HEAD/evals/rank-laptop.csv>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/quadrank/HEAD/evals/rank-server.csv>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/quadrank/HEAD/evals/fm.csv>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/quadrank/HEAD/README.md>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/quadrank/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/quadrank/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/quadrank/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/quadrank/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/quadrank/HEAD/src/binary.rs>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/quadrank/HEAD/src/binary/ranker.rs>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/quadrank/HEAD/src/binary/blocks.rs>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/quadrank/HEAD/src/quad.rs>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/quadrank/HEAD/src/quad/blocks.rs>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/quadrank/HEAD/evals/rank-laptop.csv>
  - <https://github.com/RagnarGrootKoerkamp/quadrank/issues?q=is%3Aissue>
  - <https://github.com/RagnarGrootKoerkamp/quadrank/commits/master>
  - <https://crates.io/api/v1/crates/quadrank>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/ragnargrootkoerkamp/quadrank`) · [data/wave9/enrich/raw/github_com_ragnargrootkoerkamp_quadrank.json](../../../data/wave9/enrich/raw/github_com_ragnargrootkoerkamp_quadrank.json) (enrichment confidence 0.8)

</details>
