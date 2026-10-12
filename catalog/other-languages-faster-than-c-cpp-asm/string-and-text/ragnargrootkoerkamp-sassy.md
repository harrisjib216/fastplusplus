# Sassy (SIMD approximate string matching)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust SIMD library and CLI that finds all k-edit occurrences of short DNA/ASCII patterns in long texts, 4-15x faster than Edlib.

| | |
|---|---|
| **Beats** | Edlib (C++ Myers bit-vector aligner); parasail (C) and SWOffinder also compared in the paper |
| **Claimed result** | Paper abstract (Bioinformatics, May 2026; repo copy in doc/abstract.md): Sassy1 is 4-15x faster than Edlib for patterns up to 1000 bp and reaches a text throughput up to 2 Gbp/s; for CRISPR off-target detection of 61 guides in a human genome it is 100x faster than SWOffinder and only slightly slower than the index-based CHOPOFF. 'Over 100x faster than parasail' appears in the published abstract only as quoted by a WebSearch snippet (snippet only; not in the repo copy). Sassy2 (bioRxiv, March 2026) is an additional 10-50x faster than Sassy1 for short (&lt;200 bp) texts and 2.5-4.5x for long (&gt;8 kbp) texts; README: Sassy2 2x faster with AVX-512 and pre-encoded patterns 10-20x faster for short texts (internal comparisons). |
| **Workload** | Searching short DNA/ASCII patterns (up to about 1000 characters) in long texts allowing k edit errors, synthetic data and a human genome search. |
| **Metric** | throughput |
| **Compiler and flags** | Sassy: Rust &gt;= 1.91, release profile opt-level 3 (debug info on; dist profile adds LTO and one codegen unit) with .cargo/config.toml target-cpu=native; the Edlib eval is built with 'cargo build --release -p evals'. Edlib (C++) is called through edlib-rs, whose build.rs uses the cmake crate; the cmake crate derives CMAKE_BUILD_TYPE from the Cargo profile, and with sassy's release profile (debug = true) that is RelWithDebInfo (CMake default -O2 -g), with no -march=native; edlib-rs's .cflag("-D CMAKE_BUILD_TYPE=Release") only adds a C preprocessor define and Edlib's CMakeLists sets no build type. Parasail built from its CMake (flags unstated, striped SSE4.1/AVX2 kernels tried); Ish built with ISH_SIMD_TARGET=sse. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | Bit-packing with SIMD (AVX2/NEON) where the bit-vectors run along the text direction ('tiling in the text direction'), with the text split into 4 parts searched in parallel; complexity O(k ceil(n/W)) with W=256. |
| **Adoption** | 169 stars, 18 forks; crates.io 6101 downloads (2287 recent, v0.2.6); also on bioconda and PyPI (sassy-rs); third-party DuckDB/R bindings (ducksassy) |
| **Last commit** | 2026-09-27 |
| **Links** | [repository](https://github.com/RagnarGrootKoerkamp/sassy) · [benchmark](https://github.com/RagnarGrootKoerkamp/sassy/blob/master/doc/abstract.md) |

## Verdict

Committed eval output evals/src/sassy1/output/search_throughput_pat_len.csv (single thread, 100 random patterns x 10 random 100 kbp texts, IUPAC mode) gives Sassy1 0.32-1.87 GB/s against Edlib (C++, via edlib-rs, built RelWithDebInfo) 0.077-0.128 GB/s, i.e. 4.1x (m=1000, k=50) to 14.7x (m=20-50, k=1) (derived from page data), matching the Bioinformatics abstract's 4-15x and 'up to 2 Gbp/s'; the text-length sweep (m=100) gives 4.4-9.3x, lowest for 100-250 bp texts. CPU model is not stated anywhere in the repo; the paper (Bioinformatics, May 2026) was not reachable.

## Use it when

- Finding every approximate occurrence (k edits) of 20-1000 bp primers, barcodes, adapters or guides in reads or a genome, where Edlib's HW mode would only report the optimal-cost end positions.
- Single-pattern scans over long texts on x86-64 with AVX2/AVX-512 or on ARM with NEON, built with target-cpu=native or x86-64-v3; the committed evals show 0.3-1.9 GB/s per core on 100 kbp texts.
- Many equal-length patterns of at most 64 bp against short reads (demultiplexing, barcode lookup): the Sassy2 encoded-pattern path is documented as 10-20x faster than per-pattern search for texts up to 200 bp.
- CRISPR off-target search over a whole genome without building an index (sassy crispr, exact PAM by default).
- Fuzzy grep over plain ASCII files from the command line (sassy agrep, sassy grep with coloured alignments).

## Skip it when

- Global (end-to-end) or long-read alignment of two long sequences: it is tuned for patterns up to about 1000 and long-query handling is still an open issue (#18); use Edlib NW mode or A\*PA2 instead.
- Affine-gap or substitution-matrix scoring: it is unit-cost edit distance only, and its greedy traceback (matches, then substitutions, then deletions, then insertions) does not guarantee the fewest substitutions.
- Targets without AVX2 or NEON or portable binaries built for baseline x86-64: the crate refuses to build without the SIMD target features unless the slower scalar feature is enabled, so a default cargo build of a dependent crate can fail or be slow.
- Searching many patterns against an indexed reference repeatedly: index-based tools (CHOPOFF in the project's own CRISPR test) are slightly faster once the index exists.
- IUPAC mode on N-rich data without a cap: every pattern matches NNN...N and a traceback runs from each position in N stretches unless max_n_frac or without_trace is set.

## How it is fast

Myers-style bit-parallel edit-distance DP with the bit-vectors laid along the text rather than the pattern: each u64 lane holds the horizontal deltas of 64 text columns and the kernel walks the pattern rows, so the work per row is a few SIMD bit operations for 64 text characters. Sassy1 splits one text into 4 overlapping chunks (overlap = ceil((m+k)/64) blocks) and runs one chunk per lane of a 256-bit AVX2 or NEON vector (u64x8 when the target has AVX-512), with an early-termination check once every row exceeds k. Sassy2 instead packs the deltas in the pattern direction, one short pattern per lane, after a suffix filter, which is why it wins on many short patterns over short texts. Edlib, the baseline, runs scalar 64-bit Myers/Hyyro blocks along the pattern with Ukkonen banding, so the gain is algorithmic layout plus SIMD width, not a Rust-versus-C++ effect.

## Compared with alternatives

Pick Sassy over A\*PA2 (same author) when you search a short pattern inside a long text with up to k edits rather than aligning two whole sequences end to end; pick it over the regex crate, grep clones or needletail when you need edit-distance (fuzzy) matches rather than exact or regex matches.

## Integration

| | |
|---|---|
| **Form** | crate (rlib and cdylib); also CLI binary, PyPI wheel sassy-rs, bioconda package, C header via the c feature |
| **Dependencies** | wide (author's git fork), ensure_simd, rayon, itertools, memchr, arrayvec, pa-types, prefetch-index, log, either, derivative; optional clap, needletail, colored, env_logger, num_cpus (cli), rand (diagnostics), pyo3 (python) |
| **Minimum toolchain** | Rust 1.91 (edition 2024) |
| **Platforms** | x86-64 with AVX2 required at compile time (AVX-512 used when the target enables it), aarch64 with NEON; other targets only with the slower scalar feature |
| **Thread safety** | Searcher keeps per-search scratch buffers and its methods take &mut self, so use one Searcher per thread; search_many parallelises over pattern/text pairs with rayon (num_threads 0 reuses the global pool). |
| **Drop-in for the baseline** | partial: it covers the Edlib HW (infix) use case with a different API and different output semantics (all rightmost local minima with cost &lt;= k, not only optimal-cost ends); there is no NW/SHW global mode and no Edlib-compatible C API. |

## Gotchas

- Harness detail behind the 4-15x: evals/src/benchsuite/bench.rs times single-threaded median runs (min 0.1 s, no warmup) on random ACGT data in IUPAC mode for both tools. The committed CSVs report 0 matches in 48 of 49 rows, so the headline measures pure scanning; traceback cost is benchmarked separately (trace.rs). Edlib runs HW mode with EDLIB_TASK_PATH, which returns only the end positions of optimal cost plus one path, while Sassy must report every rightmost local minimum with cost &lt;= k and a CIGAR, so the requested output does not favour Sassy.
- Optimisation levels are not matched: Edlib is built through edlib-rs's build.rs by the cmake crate, which maps sassy's release profile (opt-level 3, debug = true) to CMAKE_BUILD_TYPE=RelWithDebInfo (-O2 -g) with generic x86-64 flags; the '-D CMAKE_BUILD_TYPE=Release' in edlib-rs is passed as a C compiler flag only, so it never reaches the C++ Edlib build. Sassy gets opt-level 3 plus target-cpu=native. Edlib is scalar 64-bit code, so this probably costs it far less than the 4-15x gap.
- The '100x faster than SWOffinder' CRISPR figure is against a Java tool (javac-built, run with java) and CHOPOFF is Julia, so neither is a C/C++ baseline; the fork's committed summary.txt contains no Sassy rows (it still lists the CRISPRitz and cas-offinder runs the README says were removed), and the Snakefile builds Sassy from unpinned git HEAD.
- Before 0.1.10 (2025-12-10) the sassy grep CLI skipped a record after every 1 MB of input, searching only every other record of a human genome; the library calls behind the Edlib evals were not affected. The current code also auto-selects 8-lane AVX-512 for Sassy1 when target-cpu=native finds avx512f (changelog #68, while Cargo.toml still says the avx512 feature is 'not faster'), so re-runs on AVX-512 machines measure a different kernel than the paper's W=256.

## Known shortcomings

- The win comes from the algorithm, not the language; in the evals harness Edlib is probably built -O2 -g without native tuning (edlib-rs via the cmake crate, RelWithDebInfo) while Sassy gets target-cpu=native; the &gt;100x over Parasail is a snippet only; paper hardware unseen.
- The committed eval CSVs give Sassy1 0.32-1.87 GB/s against Edlib 0.077-0.128 GB/s (4.1-14.7x, derived), so the abstract claim holds, but 48 of 49 rows had 0 matches, so the runs measure scanning only, not traceback. Edlib was built RelWithDebInfo (-O2 -g, generic x86-64) because edlib-rs passes its -D CMAKE_BUILD_TYPE=Release as a C flag that never reaches the C++ build, while Sassy is opt-level 3 plus target-cpu=native (Edlib is scalar, so the mismatch is probably small). The 100x claim is against SWOffinder, which is Java; the fork's summary.txt has no Sassy rows; hardware is not stated anywhere in the repo.

## Caveats and trade-offs

Edlib numbers come from the peer-reviewed paper's abstract (repo copy doc/abstract.md); the full paper, its hardware and the eval CSVs were not opened (bioRxiv, doi.org and the KIT library PDF host were unreachable). The win is algorithmic, not a language effect: Sassy tiles bit-vectors along the text with 256-bit AVX2 lanes over 4 text chunks, while Edlib runs scalar 64-bit Myers/Hyyro bit-vectors. In the public evals harness Edlib is probably compiled at RelWithDebInfo (-O2 -g, generic x86-64) while Sassy gets opt-level 3 plus target-cpu=native, so optimisation levels are not matched (not a crippled -O0 build). The parasail &gt;100x figure is snippet only. Requires AVX2 or NEON at compile time (scalar feature is slower). [retier] The committed eval CSVs give Sassy1 0.32-1.87 GB/s against Edlib 0.077-0.128 GB/s (4.1-14.7x), but 48 of 49 rows had 0 matches, so the runs measure scanning only. Edlib was built RelWithDebInfo (-O2 -g, generic x86-64; edlib-rs passes CMAKE_BUILD_TYPE=Release as a C flag that never reaches the C++ build) while Sassy is opt-level 3 plus target-cpu=native (Edlib is scalar, so the mismatch is probably small). The 100x is against SWOffinder (Java); hardware is not stated anywhere in the repo.

Needs AVX2 or NEON; supports ASCII, DNA and IUPAC alphabets; best for patterns up to about 1000; C bindings, Python bindings and a CLI exist.

## Maintenance

Actively maintained (825 commits, last commit 2026-09-27, crate 0.2.6 from July 2026, 6106 crates.io downloads), MIT-licensed, published in Bioinformatics and packaged on crates.io, PyPI and bioconda, so it is production-usable for x86-64 AVX2/AVX-512 and NEON targets.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed Bioinformatics article (May 2026, doi 10.1093/bioinformatics/btag244) whose abstract, checked into the repo as doc/abstract.md, reports Sassy1 4-15x faster than Edlib for patterns up to 1000 bp; the harness (evals/, run_tool_bench.py, edlib-rs and parasail-rs dependencies) is public, but no CPU model or Edlib build flags are stated in the repo and the paper itself was unreachable, so not A.
- **Verifier notes:** Abstract in repo confirms the 4-15x vs Edlib and 100x vs SWOffinder claims; parasail &gt;100x is snippet only. Shortcomings to record: algorithmic win (text-direction SIMD tiling vs scalar Myers), Edlib likely built -O2 -g without native tuning in the evals harness via edlib-rs/cmake crate while Sassy uses target-cpu=native, hardware unstated in repo.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-12 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/README.md>
  - <https://github.com/RagnarGrootKoerkamp/sassy>
  - <https://github.com/RagnarGrootKoerkamp/sassy/tree/master/evals>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/evals/README.md>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/evals/Cargo.toml>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/.cargo/config.toml>
  - <https://github.com/RagnarGrootKoerkamp/sassy/tree/master/doc>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/doc/abstract.md>
  - <https://github.com/RagnarGrootKoerkamp/sassy/commits/master>
  - <https://raw.githubusercontent.com/pairwise-alignment/edlib-rs/HEAD/build.rs>
  - <https://raw.githubusercontent.com/pairwise-alignment/edlib-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Martinsos/edlib/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/rust-lang/cmake-rs/HEAD/src/lib.rs>
  - <https://crates.io/api/v1/crates/sassy>
- **Sources the enricher read:**
  - <https://github.com/RagnarGrootKoerkamp/sassy>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/README.md>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/doc/abstract.md>
  - <https://github.com/RagnarGrootKoerkamp/sassy/tree/master/doc>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/src/search.rs>
  - <https://github.com/RagnarGrootKoerkamp/sassy/tree/master/src>
  - <https://github.com/RagnarGrootKoerkamp/sassy/tree/master/bin>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/c/README.md>
  - <https://github.com/RagnarGrootKoerkamp/sassy/tree/master/evals>
  - <https://github.com/RagnarGrootKoerkamp/sassy/tree/master/evals/src>
  - <https://github.com/RagnarGrootKoerkamp/sassy/tree/master/evals/src/sassy1>
  - <https://github.com/RagnarGrootKoerkamp/sassy/tree/master/evals/src/benchsuite>
  - <https://github.com/RagnarGrootKoerkamp/sassy/tree/master/evals/src/sassy1/configs>
  - <https://github.com/RagnarGrootKoerkamp/sassy/tree/master/evals/src/sassy1/output>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/evals/README.md>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/evals/Cargo.toml>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/evals/src/main.rs>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/evals/src/benchsuite/bench.rs>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/evals/src/benchsuite/edlib.rs>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/evals/src/benchsuite/mod.rs>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/evals/src/benchsuite/sim_data.rs>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/evals/src/sassy1/mod.rs>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/evals/src/sassy1/throughput_m.rs>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/evals/src/sassy1/throughput_n.rs>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/evals/src/sassy1/trace.rs>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/evals/src/sassy1/configs/throughput_m.toml>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/evals/src/sassy1/configs/throughput_n.toml>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/evals/src/sassy1/configs/trace.toml>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/evals/src/sassy1/output/search_throughput_pat_len.csv>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/sassy/HEAD/evals/src/sassy1/output/search_throughput_text_len.csv>
  - <https://github.com/RagnarGrootKoerkamp/sassy/issues?q=is%3Aissue>
  - <https://github.com/RagnarGrootKoerkamp/sassy/issues?q=is%3Aissue&page=2>
  - <https://github.com/RagnarGrootKoerkamp/sassy/issues/80>
  - <https://github.com/RagnarGrootKoerkamp/sassy/issues/21>
  - <https://github.com/RagnarGrootKoerkamp/sassy/issues/18>
  - <https://crates.io/api/v1/crates/sassy>
  - <https://raw.githubusercontent.com/pairwise-alignment/edlib-rs/HEAD/build.rs>
  - <https://raw.githubusercontent.com/pairwise-alignment/edlib-rs/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/Martinsos/edlib/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Martinsos/edlib/HEAD/edlib/src/edlib.cpp>
  - <https://raw.githubusercontent.com/rust-lang/cmake-rs/HEAD/src/lib.rs>
  - <https://github.com/rickbeeloo/sassy-crispr-bench>
  - <https://raw.githubusercontent.com/rickbeeloo/sassy-crispr-bench/HEAD/Snakefile>
  - <https://raw.githubusercontent.com/rickbeeloo/sassy-crispr-bench/HEAD/summary.txt>
  - <https://raw.githubusercontent.com/rickbeeloo/sassy-crispr-bench/HEAD/config.yaml>
  - <https://raw.githubusercontent.com/rickbeeloo/sassy-crispr-bench/HEAD/environment.yml>
  - https://curiouscoding.nl/posts/sassy/ (DNS failure, not read)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/ragnargrootkoerkamp/sassy`) · [data/wave14/enrich/raw/github_com_ragnargrootkoerkamp_sassy.json](../../../data/wave14/enrich/raw/github_com_ragnargrootkoerkamp_sassy.json) (enrichment confidence 0.72)

</details>
