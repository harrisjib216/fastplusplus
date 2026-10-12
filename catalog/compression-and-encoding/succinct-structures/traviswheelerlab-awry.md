# AWRY

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Succinct data structures](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust` · `BSD-3-Clause` · 🟡 stale

> Rust port of the AVX2 windowed FM-index (AvxWindowFmIndex); in the only third-party benchmark found it is slower than genedex.

| | |
|---|---|
| **Beats** | AvxWindowFmIndex (C), SeqAn3 FM-index, SDSL |
| **Claimed result** | None for AWRY. README calls it 'fastest in its class' by reference to the C library paper (doi 10.1186/s13015-021-00204-6); search snippet: C version 2-4x faster than SeqAn3 on nucleotides, 2-6x on amino acids (snippet only). |
| **Workload** | None in this repo: the README has no benchmark. The C original (AvxWindowFmIndex) paper snippet claims 2-4x faster nucleotide exact-match queries than SeqAn3. |
| **Metric** | throughput |
| **Adoption** | 5 stars on UM-Applied-Algorithms-Lab/AWRY (283 commits, 6 forks); 0 on the traviswheelerlab fork; on crates.io (awry 0.3 used by rust-fmindex-benchmark) |
| **Last commit** | 2025-01-14 |
| **Links** | [repository](https://github.com/traviswheelerlab/AWRY) |

## Verdict

AWRY publishes no benchmark of its own; its 'fastest in its class' wording borrows the C AvxWindowFmIndex paper's 2-4x (DNA) / 2-6x (protein) speedups over SeqAn3, which were not measured on this port. The only third-party numbers (RagnarGrootKoerkamp/quadrank evals/fm.csv: i7-10750H fixed at 3.0 GHz, human genome, 150 bp reads with 1% error, built from a patched AWRY) show identical match counts but AWRY 2.0x slower than genedex flat64 on 1 thread (8.56 s vs 4.18 s), 2.4x slower on 12 threads (0.97 s vs 0.41 s), with a 1.96 GB index versus 2.63 GB (flat64) / 1.68 GB (cond64) and an 872 s build versus about 109 s.

## Use it when

- You need a Rust FM-index that handles protein (amino acid) text as well as DNA, which genedex-style nucleotide indexes may not cover the same way.
- Count-heavy exact-match workloads where you can set suffix_array_compression_ratio high (README suggests 255) to shrink the index.
- Embarrassingly parallel batches of short queries on a multi-core x86-64 (AVX2) or aarch64 (Neon) machine, using parallel_count.
- Prototyping against the AvxWindowFmIndex block layout from Rust without an FFI binding to the C library.

## Skip it when

- Performance-critical read mapping: on quadrank's human-genome benchmark (i7-10750H at 3.0 GHz, 150 bp simulated reads) AWRY counted in 8.56 s on 1 thread versus 4.18 s for genedex flat64 and 0.97 s versus 0.31-0.41 s on 12 threads (about 2-3x slower, derived from page data).
- Large genomes on memory- or disk-limited machines: index build took 872 s versus about 109 s for genedex in quadrank's run, feldroop/rust-fmindex-benchmark reports 18x peak construction memory, and issue #47 reports a 32 GB RAM spike and about 40 GB of temporary files for a human genome.
- locate()-heavy work: issue #44 (Sep 2025, open, no maintainer reply) reports locate hanging in an apparent infinite loop during benchmarking, and rust-fmindex-benchmark excludes AWRY until it is fixed.
- Soft-masked references (lowercase repeats): AWRY passes ignore_softmask: true to libsufr, which turns lowercase bases into N, so queries in soft-masked regions find nothing despite the README saying the alphabet is case-insensitive.
- x86-64 CPUs without AVX2 or any other architecture: there is no scalar fallback and no runtime feature detection.

## How it is fast

The BWT is stored in 256-symbol blocks aligned to 32 bytes: each block holds per-symbol milestone counts plus 3 (nucleotide) or 5 (amino acid) bit-vectors, so an occurrence (rank) query is a few AVX2/Neon AND/ANDNOT operations to build the symbol's bit mask and a masked popcount over 4 words, i.e. one cache-line-sized block per rank. The suffix array is sampled (default ratio 8) and bit-packed, and queries are spread across threads with rayon. The C original's query batching and prefetching (4 queries at a time) are not implemented, and the k-mer lookup table it builds is not consulted when searching (see gotchas).

## Compared with alternatives

Pick genedex for Rust DNA FM-index work: it builds about 8x faster and counts about 2x faster in the same quadrank run. The catalogued C AvxWindowFmIndex (AWFM-index) is the faster original with batching and prefetching. Choose AWRY only if you need its protein alphabet support in pure Rust and can live with the open locate bug.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | rayon, anyhow, aligned, rand, serde, mem_dbg, libsufr 0.6.2 (suffix-array construction, writes to disk / \$TMPDIR) |
| **Minimum toolchain** | Rust edition 2021; no rust-version declared (code uses usize::div_ceil, stable since Rust 1.73) |
| **Platforms** | x86-64 with AVX2, aarch64 with Neon; nothing else |
| **Thread safety** | Queries take &self and the built index holds only plain Vecs; parallel_count/parallel_locate share one index across rayon threads. Construction is single-call and file-based. |
| **Drop-in for the baseline** | partial: same FM-index count/locate operations as SeqAn3/SDSL or the C AvxWindowFmIndex, but a different Rust API, a custom on-disk format, and file-only construction |

## Gotchas

- The k-mer lookup table (10-mers for DNA, 4-mers for protein in code; the README says 13 and 5) is built, populated twice during construction and saved, but KmerLookupTable::get_range_for_kmer recomputes the range by backward search instead of indexing the table, so the expected head start on every query is lost.
- Safe public functions index with get_unchecked: update_range_with_symbol is pub and SearchRange's fields are pub, so an out-of-range end_ptr (or start_ptr 0, which wraps around through start_ptr - 1) reads out of bounds. FmIndex::load trusts bwt_len and the other header values in the file, so a corrupt or crafted .awry file can do the same. AVX2 #[target_feature] functions are called without runtime detection, which is undefined behaviour (typically SIGILL) on non-AVX2 x86-64.
- An empty query panics (unwrap on chars().last()); a query containing '\$' or '#' panics in global_occurrence; any other unknown letter is silently treated as N (DNA) or X (protein) and matches those positions.
- Cargo.toml puts rustflags = ["-C", "target-cpu=native"] under [lib], where Cargo does not read it, so a normal build does not get native codegen. Without -C target-feature=+avx2 the SIMD helper functions cannot be inlined into their non-AVX2 callers.

## Caveats and trade-offs

traviswheelerlab/AWRY is a fork of UM-Applied-Algorithms-Lab/AWRY (BSD-3-Clause, last commit 2025-01-14), which is the upstream. No AWRY benchmark in either README; the 'fastest in its class' claim and the 2-4x (nucleotide) / 2-6x (amino acid) speedups over SeqAn3 belong to the C library AvxWindowFmIndex (doi 10.1186/s13015-021-00204-6, snippet only, not opened). feldroop/rust-fmindex-benchmark excluded AWRY for segmentation faults and reports 18x peak construction memory. Third-party numbers in RagnarGrootKoerkamp/quadrank evals/fm.csv (i7-10750H, simulated 150 bp reads on a human genome, built from a patched fork) show AWRY slower than the alternatives: sequential count 8.56 s on 1 thread versus genedex flat64 4.18 s (about 2.0x slower, derived from page data), and 872 s index build versus about 109 s for genedex.

Needs AVX2 or ARM Neon; supports DNA, RNA and protein; parallel_count and parallel_locate via rayon.

## Maintenance

Stale: the last upstream commit and crates.io release (0.3.1) are from 2025-01-14, with about 7.2k total downloads. Six issues are open, including the locate hang (#44), missing batching and prefetching (#45) and build-resource problems (#47), none with a maintainer reply. BSD-3-Clause, so it is legally copyable, but expect to fix it yourself; the traviswheelerlab repository is a 0-star fork.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now D.
- **Tier reason:** Neither the traviswheelerlab fork nor the UM-Applied-Algorithms-Lab upstream README has any benchmark; the only speed claim ('fastest in its class') refers to the C AvxWindowFmIndex paper, not this Rust port. The one third-party measurement found (quadrank evals/fm.csv) shows AWRY slower than genedex, so there are no numbers showing AWRY faster than a named baseline.
- **Verifier notes:** Kept at tier D per the seed-record rule; repo_url corrected to the upstream as instructed. The only measurement found shows AWRY losing to genedex, so it has no demonstrated speed win; the orchestrator may prefer to file it as a documented non-winner.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/traviswheelerlab/AWRY>
  - <https://github.com/UM-Applied-Algorithms-Lab/AWRY>
  - <https://github.com/UM-Applied-Algorithms-Lab/AWRY/commits>
  - <https://raw.githubusercontent.com/feldroop/rust-fmindex-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/feldroop/rust-fmindex-benchmark/HEAD/justfile>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/quadrank/HEAD/README.md>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/quadrank/HEAD/evals/fm.csv>
- **Sources the enricher read:**
  - <https://github.com/traviswheelerlab/AWRY>
  - <https://raw.githubusercontent.com/UM-Applied-Algorithms-Lab/AWRY/HEAD/README.md>
  - <https://raw.githubusercontent.com/UM-Applied-Algorithms-Lab/AWRY/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/UM-Applied-Algorithms-Lab/AWRY/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/UM-Applied-Algorithms-Lab/AWRY/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/UM-Applied-Algorithms-Lab/AWRY/HEAD/src/alphabet.rs>
  - <https://raw.githubusercontent.com/UM-Applied-Algorithms-Lab/AWRY/HEAD/src/bwt.rs>
  - <https://raw.githubusercontent.com/UM-Applied-Algorithms-Lab/AWRY/HEAD/src/compressed_suffix_array.rs>
  - <https://raw.githubusercontent.com/UM-Applied-Algorithms-Lab/AWRY/HEAD/src/fm_index.rs>
  - <https://raw.githubusercontent.com/UM-Applied-Algorithms-Lab/AWRY/HEAD/src/fm_index_file.rs>
  - <https://raw.githubusercontent.com/UM-Applied-Algorithms-Lab/AWRY/HEAD/src/kmer_lookup_table.rs>
  - <https://raw.githubusercontent.com/UM-Applied-Algorithms-Lab/AWRY/HEAD/src/search.rs>
  - <https://raw.githubusercontent.com/UM-Applied-Algorithms-Lab/AWRY/HEAD/src/sequence_index.rs>
  - <https://raw.githubusercontent.com/UM-Applied-Algorithms-Lab/AWRY/HEAD/src/simd_instructions.rs>
  - <https://github.com/UM-Applied-Algorithms-Lab/AWRY/issues?q=is%3Aissue>
  - <https://github.com/UM-Applied-Algorithms-Lab/AWRY/issues/44>
  - <https://github.com/UM-Applied-Algorithms-Lab/AWRY/issues/45>
  - <https://github.com/UM-Applied-Algorithms-Lab/AWRY/issues/47>
  - <https://github.com/UM-Applied-Algorithms-Lab/AWRY/commits>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/quadrank/HEAD/evals/fm.csv>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/quadrank/HEAD/README.md>
  - <https://raw.githubusercontent.com/feldroop/rust-fmindex-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/TravisWheelerLab/sufr/HEAD/README.md>
  - <https://raw.githubusercontent.com/TravisWheelerLab/sufr/HEAD/libsufr/src/util.rs>
  - <https://raw.githubusercontent.com/TravisWheelerLab/sufr/HEAD/libsufr/src/sufr_builder.rs>
  - <https://crates.io/api/v1/crates/awry>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/traviswheelerlab/awry`) · [data/wave9/enrich/raw/github_com_traviswheelerlab_awry.json](../../../data/wave9/enrich/raw/github_com_traviswheelerlab_awry.json) (enrichment confidence 0.8)

</details>
