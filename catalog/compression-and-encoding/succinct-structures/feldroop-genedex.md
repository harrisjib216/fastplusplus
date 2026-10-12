# genedex

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Succinct data structures](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Rust FM-index for DNA-sized texts; locates short reads in hg38 about 4.4x faster than rust-bio's FM-index with a third of its memory.

| | |
|---|---|
| **Beats** | rust-bio FM-index (bio large, sampling 32); also fm-index crate and sview-fmindex |
| **Claimed result** | Locate hg38 running time: genedex flat64 1.6 s (7.2 GB index) and cond64 2.6 s (5.2 GB) versus bio large 7.0 s (19.9 GB), bio small 10.2 s (10.2 GB), fm-index multi text 87.9 s (7.3 GB), sview vec128 2.4 s (5.4 GB), sview vec32 2.3 s (6.9 GB). Derived from page data: flat64 about 4.4x faster than bio large and 1.4x faster than sview vec32. |
| **Workload** | Locate of 377 MB of 50-base Illumina read queries in an FM-index of human genome hg38 (suffix array sampling 4, lookup depth 10), best of 5 runs, plus index construction time and memory; single-threaded search loop. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Gold 6348 @ 2.60GHz, 2 sockets x 28 cores, AVX512, 1 TB RAM |
| **Compiler and flags** | rustc, version not stated (no rust-toolchain file; Cargo.toml edition 2024 implies rustc &gt;= 1.85); cargo run --release (profile.release with debug = true) with RUSTFLAGS -C target-cpu=native from .cargo/config.toml; dependency versions pinned in Cargo.lock (genedex 0.2.2, bio 3.0.0) |
| **Adoption** | 44 stars; on crates.io |
| **Last commit** | 2026-02-01 |
| **Links** | [repository](https://github.com/feldroop/genedex) · [benchmark](https://github.com/feldroop/rust-fmindex-benchmark) |

## Verdict

In the author's own rust-fmindex-benchmark (Rust, cargo --release with -C target-cpu=native, rustc version not stated, Intel Xeon Gold 6348), locating 377 MB of 50-base Illumina reads in an hg38 index (sampling 4, lookup depth 10, best of 5) took 1.6 s with flat64 (7.2 GB) and 2.6 s with cond64 (5.2 GB) versus 7.0 s for rust-bio sampling 32 (19.9 GB) and 2.3-2.4 s for sview-fmindex; genedex runs through its batched locate_many while rust-bio and fm-index run one query at a time and gain no lookup table, so part of the gap is API features rather than the rank structure.

## Use it when

- Exact-match seeding of short DNA reads (tens of bases) against a large reference such as hg38, from Rust, where many queries can be searched in batches.
- Indexing a set of texts (chromosomes, contigs) and getting hits back as (text_id, position) without manual concatenation bookkeeping.
- When rust-bio's FM-index is too large or too slow: flat64 used 7.2 GB and 1.6 s versus bio large's 19.9 GB and 7.0 s on the hg38 locate benchmark.
- Small alphabets (DNA, DNA with N, amino acids); the condensed variant keeps memory moderate as the alphabet grows.
- Fast index persistence: built-in save/load to files avoids rebuilding a multi-GB index each run.

## Skip it when

- Approximate or bidirectional search (MEMs/SMEMs, FMD-index, search schemes with errors): not implemented; listed on the roadmap only.
- Highly repetitive collections (pangenomes) where an r-index or run-length FM-index would be far smaller; not implemented.
- Maximum raw throughput on rank: the independent quadrank evaluation (i7-10750H) measured genedex flat64 at 4.18 s versus QuadFm prefetch at 1.31 s for counting simulated 150 bp reads.
- Production code that needs a stable API: the README warns the library is early-stage and the API may change.
- Loading index files from untrusted sources: the query path uses get_unchecked/unwrap_unchecked, and the safe wrappers check only the symbol and position against the stored text length, not that deserialized arrays are consistent.

## How it is fast

The occurrence table is a text-with-rank-support structure with interleaved blocks: the 'flat' variant keeps one bitvector per symbol, and the default 'condensed' variant stores each block bit-sliced into ceil(log2 sigma) bit-planes (the encoding from Gottlieb and Reinert, 'Engineering rank queries on bit vectors and strings', 2025), both with u16 block offsets and wider superblock offsets, so one LF step touches about one cache line. A precomputed lookup table skips the first d backward-search steps, and count_many/locate_many interleave batches of 64 queries on one thread so their cache misses overlap. Construction uses libsais suffix sorting parallelised with rayon.

## Compared with alternatives

Among catalogued FM-indexes, pick genedex over AWRY when you want a pure-Rust crate with multi-text support and file IO (AWRY was excluded from the author's benchmark for segmentation faults), and over AvxWindowFmIndex when you are not tied to C and x86 AVX2; pick QuadRank's QuadFm if you need the fastest counting and can use research code.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | libsais (C library via libsais-rs), rayon, num-traits, bytemuck, memchr; optional psacak (default u32-saca feature), savefile (default), mem_dbg |
| **Minimum toolchain** | Rust edition 2024 (rustc 1.85+); no rust-version field published |
| **Platforms** | any Rust target supported by libsais; no architecture-specific SIMD code found (no target_arch or intrinsics in the sources read); benchmark built with -C target-cpu=native |
| **Thread safety** | Construction is multi-threaded via rayon (thread count set through rayon's global pool). Queries take &self and the index holds plain Vecs, so concurrent reads are possible, but thread safety is not documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- Query bytes outside the alphabet panic (io_to_dense_representation calls expect); use the cursor with try_io_to_dense_representation or pre-filter reads containing unexpected characters.
- Issue #5 (overflow at condensed.rs block_offsets_sum when a superblock is all one symbol) was fixed on master with wrapping_add after the last crates.io release (0.2.2, 2025-09-25); debug builds of 0.2.2 can panic on such inputs, while release builds wrap silently, which the code comment says is harmless.
- Default config uses suffix-array sampling rate 4 and lookup-table depth 0; the benchmark speeds assume lookup depth 10 and locate_many batching, so per-query locate() calls with defaults will be slower.
- Positions are stored as the generic I (i32, u32, i64...); texts over 2^31 or 2^32 symbols need a wider type and more memory, and the u32 path relies on the psacak low-memory suffix sorter, which the roadmap calls slow.

## Known shortcomings

- Beats Rust crates only (flat64 1.6 s vs bio large 7.0 s on hg38 locate), not SDSL; author-run and disclosed. Numbers read off SVG text labels. rustc version not stated (edition 2024 implies &gt;= 1.85); harness public (src/main.rs, justfile; single-threaded, best of 5), Xeon Gold 6348, target-cpu=native. A third-party quadrank evals table shows genedex at 4.18 s vs AWRY 8.56 s on 1 thread.
- Benchmark bias: genedex runs batched locate_many with lookup depth 10 while rust-bio and fm-index run one query at a time with no lookup table (sview does use one). Issue #5 overflow (condensed.rs block_offsets_sum) fixed on master after crates.io 0.2.2, so debug builds of 0.2.2 can panic. get_unchecked/unwrap_unchecked in rank, and safe wrappers do not check that loaded savefile arrays are consistent, so untrusted index files are a risk. Out-of-alphabet query bytes panic. Early-stage API.

## Caveats and trade-offs

Benchmark author is the genedex author (bias alert stated in the benchmark README). Baselines are other Rust crates (rust-bio, fm-index, sview-fmindex); no run against SDSL (C++) or sux. rustc version not stated. Numbers come from the Locate-Hg38.svg plot; the same values are embedded as text labels in the SVG source. Index construction for genedex used 8 threads (-t 8) while the search loop is single-threaded and best of 5. AWRY was excluded from this benchmark for segmentation-fault problems. Only DNA/hg38 workload. An independent benchmark (RagnarGrootKoerkamp/quadrank evals/fm.csv, i7-10750H) uses genedex as a baseline: genedex flat64 sequential count of simulated 150 bp reads took 4.18 s on 1 thread versus AWRY 8.56 s, while QuadFm prefetch took 1.31 s, so genedex is not the fastest Rust FM-index there.

Early-stage API; sampled suffix array; flat64 trades memory (7.2 GB vs 5.2 GB for cond64) for speed; construction uses libsais and rayon (build threads only).

## Maintenance

Single-author crate, MIT OR Apache-2.0, last commit 2026-02-01 and last crates.io release 0.2.2 in September 2025; the roadmap says further work depends on user demand, so treat it as maintained but early-stage.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification A, tier now A.
- **Tier reason:** The benchmark code is public (feldroop/rust-fmindex-benchmark src/main.rs, src/common_interface.rs, justfile), the CPU is stated (Xeon Gold 6348) and the flags are stated (cargo --release, -C target-cpu=native in .cargo/config.toml), but the rustc version is not stated anywhere (no rust-toolchain file; edition 2024 only implies rustc &gt;= 1.85), so it misses A; the benchmark was run by the genedex author, so it is first-party C.
- **Retiered** C to A: Restored C to A for consistency with quadrank (same wave, same evidence shape): the harness is public (src/main.rs, justfile; single-threaded search, best of 5), the CPU (Xeon Gold 6348) and flags (target-cpu=native) are stated, and the compiler is pinned only to a minimum (edition 2024, rustc &gt;= 1.85). quadrank kept A with the same minimum-rustc gap, so the two are tiered alike; the gap is recorded in the caveats.
- **Verifier notes:** All seven Locate-Hg38 running-time and memory values in claimed_speedup match the text labels inside Locate-Hg38.svg (bio large 7.0 s/19.9 GB, bio small 10.2/10.2, fmindex multi text 87.9/7.3, cond64 2.6/5.2, flat64 1.6/7.2, sview vec128 2.4/5.4, vec32 2.3/6.9). Harness and CPU are stated but rustc version is not, per the orchestrator's A condition; note the quadrank precedent kept A with only a minimum rustc stated, so the orchestrator may choose to restore A for consistency.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** first-party benchmark with public harness and CPU
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/feldroop/rust-fmindex-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/feldroop/rust-fmindex-benchmark/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/feldroop/rust-fmindex-benchmark/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/feldroop/rust-fmindex-benchmark/HEAD/Cargo.lock>
  - <https://raw.githubusercontent.com/feldroop/rust-fmindex-benchmark/HEAD/justfile>
  - <https://raw.githubusercontent.com/feldroop/rust-fmindex-benchmark/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/feldroop/rust-fmindex-benchmark/HEAD/src/common_interface.rs>
  - <https://raw.githubusercontent.com/feldroop/rust-fmindex-benchmark/HEAD/plots/img/Locate-Hg38.svg>
  - <https://raw.githubusercontent.com/feldroop/genedex/HEAD/README.md>
  - <https://raw.githubusercontent.com/feldroop/genedex/HEAD/Cargo.toml>
  - <https://github.com/feldroop/genedex>
  - <https://github.com/feldroop/genedex/commits>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/quadrank/HEAD/README.md>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/quadrank/HEAD/evals/fm.csv>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/feldroop/genedex/HEAD/README.md>
  - <https://raw.githubusercontent.com/feldroop/genedex/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/feldroop/genedex/HEAD/ROADMAP.md>
  - <https://raw.githubusercontent.com/feldroop/genedex/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/feldroop/genedex/HEAD/src/cursor.rs>
  - <https://raw.githubusercontent.com/feldroop/genedex/HEAD/src/alphabet.rs>
  - <https://raw.githubusercontent.com/feldroop/genedex/HEAD/src/config.rs>
  - <https://raw.githubusercontent.com/feldroop/genedex/HEAD/src/batch_computed_cursors.rs>
  - <https://raw.githubusercontent.com/feldroop/genedex/HEAD/src/sampled_suffix_array.rs>
  - <https://raw.githubusercontent.com/feldroop/genedex/HEAD/src/text_with_rank_support/mod.rs>
  - <https://raw.githubusercontent.com/feldroop/genedex/HEAD/src/text_with_rank_support/condensed.rs>
  - <https://raw.githubusercontent.com/feldroop/genedex/HEAD/src/text_with_rank_support/flat.rs>
  - <https://github.com/feldroop/genedex/tree/master/src>
  - <https://github.com/feldroop/genedex/issues?q=is%3Aissue>
  - <https://github.com/feldroop/genedex/issues/2>
  - <https://github.com/feldroop/genedex/issues/5>
  - <https://github.com/RagnarGrootKoerkamp/quadrank/issues/1>
  - <https://crates.io/api/v1/crates/genedex>
  - <https://raw.githubusercontent.com/feldroop/rust-fmindex-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/feldroop/rust-fmindex-benchmark/HEAD/justfile>
  - <https://raw.githubusercontent.com/feldroop/rust-fmindex-benchmark/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/feldroop/rust-fmindex-benchmark/HEAD/src/common_interface.rs>
  - <https://raw.githubusercontent.com/feldroop/rust-fmindex-benchmark/HEAD/src/genedex_bench.rs>
  - <https://raw.githubusercontent.com/feldroop/rust-fmindex-benchmark/HEAD/src/sview_fmindex_bench.rs>
  - <https://raw.githubusercontent.com/feldroop/rust-fmindex-benchmark/HEAD/src/bio_bench.rs>
  - <https://raw.githubusercontent.com/feldroop/rust-fmindex-benchmark/HEAD/src/awry_bench.rs>
  - <https://raw.githubusercontent.com/feldroop/rust-fmindex-benchmark/HEAD/src/fmindex_bench.rs>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/feldroop/genedex`) · [data/wave9/enrich/raw/github_com_feldroop_genedex.json](../../../data/wave9/enrich/raw/github_com_feldroop_genedex.json) (enrichment confidence 0.8)

</details>
