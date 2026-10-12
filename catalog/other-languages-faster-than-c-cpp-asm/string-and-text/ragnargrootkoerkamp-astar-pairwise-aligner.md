# A\*PA2 (astar-pairwise-aligner)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MPL-2.0` · 🟢 active

> Rust exact global DNA aligner using A\*-guided band doubling over SIMD bit-parallel blocks; beats Edlib and BiWFA on long, similar sequences.

| | |
|---|---|
| **Beats** | Edlib (C++) and BiWFA / WFA2-lib (C) exact global aligners |
| **Claimed result** | Repo README: 'It achieves up to 20x speedup over other exact aligners and is competitive with approximate aligners' (the WABI paper title says 'up to 19x faster'). pa-bench evals/astarpa2/evals.ipynb saved output: mean speedup of A\*PA2-simple over Edlib 7.48 on the scaling-n synthetic set and 8.26 on the scaling-e set (notebook output). Its runtime table, with a 'best A\*PA2 vs best of Edlib/BiWFA' speedup row, has no saved output. Paper abstract, seen only in a search snippet (WABI 2024, LIPIcs 312; paper page blocked): 19x faster than BiWFA and Edlib on &gt;500 kbp ONT reads with 6% divergence; 5.6x on 11 kbp reads with 11% divergence; 0.81x (slower) on 800 bp reads with 11% divergence. |
| **Workload** | Exact global pairwise alignment (edit distance) of long DNA sequences, e.g. ONT reads of a human genome with 6% to 11% divergence, plus synthetic sequences. |
| **Metric** | latency |
| **Hardware** | CPU model not stated in pa-bench; evals/astarpa2/justfile pins the CPU at 3.6 GHz with cpupower (performance governor), and pa-bench pins each job to one core. |
| **Compiler and flags** | pa-bench release profile: lto = true, codegen-units = 1 (pa-bench Cargo.toml); A\*PA2 is pulled in as a git dependency, and its repo pins a nightly toolchain (rust-toolchain.toml). The aligner repo's .cargo/config.toml sets -C target-cpu=native, but pa-bench does not state which RUSTFLAGS the paper runs used. Edlib is built by edlib-rs through the cmake crate; its build.rs passes '-D CMAKE_BUILD_TYPE=Release' as a C flag, so the build type comes from the cmake crate's profile mapping (derived). The rust-wfa2 build for BiWFA was not checked. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | Per the paper snippet: like Edlib it uses Ukkonen band doubling with Myers bit-packing, adding large blocks, SIMD, a new profile and the A\* heuristics from A\*PA (a different algorithm, not a language effect). |
| **Adoption** | 152 stars |
| **Last commit** | 2026-05-22 |
| **Links** | [repository](https://github.com/RagnarGrootKoerkamp/astar-pairwise-aligner) · [benchmark](https://github.com/pairwise-alignment/pa-bench/tree/main/evals/astarpa2) |

## Verdict

Opened first-party evidence: the pa-bench evals notebook reports A\*PA2-simple averaging 7.48x (scaling-n) and 8.26x (scaling-e) faster than Edlib (C++, through edlib-rs) on synthetic pairs. scaling-n runs 3 kbp to 10 Mbp at 5% and 15% uniform error with traceback, a 3 h and 32 GiB limit, one pinned core at a fixed 3.6 GHz, and no CPU model given. The WABI 2024 paper reports 19x on &gt;500 kbp ONT reads at 6% divergence, 5.6x at 11 kbp and 11%, and 0.81x at 800 bp and 11% against the best of Edlib and BiWFA (C), but these were seen only in search snippets.

## Use it when

- Exact (optimal) global edit-distance alignment of long DNA pairs, from tens of kbp to Mbp, at low to moderate divergence: for example ONT or PacBio reads, or assembled sequences that should be similar end to end.
- When you need a guaranteed-optimal cost and CIGAR, not the heuristic answer of a banded or X-drop aligner, and Edlib or BiWFA are too slow at your lengths.
- Rust pipelines that can take a git dependency on a nightly toolchain, or C/C++ code that can link the astarpa-c shared library.
- Throughput-bound batches of long pairs on one core per pair; pa-bench measures it single-threaded and pinned to a core, so parallelise across pairs.

## Skip it when

- Short, highly divergent reads: the WABI 2024 abstract (search snippet only) reports 0.81x, i.e. slower than the best of Edlib and BiWFA, on 800 bp ONT reads at 11% divergence.
- Any input that is not upper-case A, C, G or T. The profile uses rust-bio's RankTransform over b"ACGT", which panics with 'Unexpected character.' on N, IUPAC codes or lower case: issue #31 ('N characters are not currently supported with A\*'), and issue #33 (lower-case bases) is still open. Protein is not supported. Edlib takes arbitrary byte alphabets.
- Affine gaps, local or semi-global alignment, or pattern search: it computes global unit-cost edit distance only. Use Sassy or Edlib's infix mode for search.
- Builds that must use stable Rust: it needs nightly (rust-toolchain.toml pins nightly-2026-05-21) for portable_simd and the incomplete generic_const_exprs feature, and new nightlies have repeatedly broken the build (issues #28, #32, #36, #41).
- Projects that need a versioned package: there is no crates.io release (the README says to add it as a git dependency), and the code is research code with open cleanup issues (#22-#27).

## How it is fast

Like Edlib, it uses Ukkonen band doubling over Myers' bit-parallel DP, with several changes. It computes 256-column blocks of 64-bit words with std::simd (4 x u64 lanes, two vectors in flight for instruction-level parallelism) and uses a bit-sliced profile that matches a character in two XOR/AND operations. Doubling starts at the heuristic value h(0,0) rather than 0, and each block's row range is narrowed with an admissible A\* heuristic: the gap-cost heuristic in -simple, and in -full the gap-chaining seed heuristic (k=12) with match pruning and incremental doubling. Traceback runs diagonal transition over the stored block fronts. On low-divergence pairs the heuristic skips most of the band, so the gain grows with length and shrinks as divergence rises. This is an algorithmic advantage, not a language one.

## Compared with alternatives

Pick A\*PA2 for exact end-to-end alignment of long, similar DNA sequences. Pick Sassy (same author) to find short patterns with errors inside long texts, and bitdp for batched throughput on many short (150 bp to 1 kbp) pairs, where bitdp beats Edlib and A\*PA2's long-read advantage does not apply.

## Integration

| | |
|---|---|
| **Form** | crate (git dependency) plus a C API (astarpa-c shared library) and the pa-bin CLI |
| **Dependencies** | workspace crates pa-types, pa-heuristic, pa-bitpacking, pa-affine-types and pa-vis, plus rust-bio 1.3.0, itertools, clap and serde; SDL2 only for the optional visualizer |
| **Minimum toolchain** | Rust nightly (pinned nightly-2026-05-21, edition 2024; std::simd portable_simd, generic_const_exprs) |
| **Platforms** | any target std::simd supports; tuned for 256-bit vectors (4 x u64 lanes); the repo's .cargo/config.toml builds with -C target-cpu=native |
| **Thread safety** | not documented; each alignment runs single-threaded in its own aligner instance |
| **Drop-in for the baseline** | partial — same task as Edlib's global (NW) mode with a cost and CIGAR, but a different API, DNA (ACGT) only, and no semi-global or infix modes |

## Gotchas

- Input validation is a panic: any byte outside A, C, G and T aborts the alignment with 'Unexpected character.' from rust-bio (issue #31, a pa-bin run on a FASTA file containing N). Sanitise or split on N before calling, and never pass lower-case sequence (issue #33 is open).
- Evidence caveats: the numbers that could be opened are the pa-bench notebook means of 7.48x and 8.26x over Edlib. These are arithmetic means of per-(length, error-rate) runtime ratios on uniform-random synthetic pairs, so they are weighted toward the largest-n cells. They use capped runtimes: a timeout counts as the time limit, any other failure as 1.1x the limit, and a failure skips all larger jobs. The 19x, 5.6x and 0.81x paper figures were seen only in search snippets, since dagstuhl and bioRxiv are blocked here, and no CPU model is stated anywhere.
- Build flags of the published runs are undocumented: pa-bench has no .cargo/config.toml and its justfile sets no RUSTFLAGS, so the aligner repo's target-cpu=native does not apply when pa-bench builds A\*PA2 as a git dependency. Edlib is built through edlib-rs and the cmake crate, whose '-D CMAKE_BUILD_TYPE=Release' is passed as a C flag, not a CMake option. pa-bench does cross-check costs between exact aligners and validates every CIGAR, so no correctness flaw was found behind the numbers.
- The -full variant builds a k-mer seed heuristic (k=12, pruning) before aligning. Issues #29 and #30 were block-indexing and traceback panics, both closed in September 2024, so pin a known-good commit (pa-bench's Cargo.lock uses f83c131).

## Known shortcomings

- The WABI 19x/5.6x/0.81x figures are a snippet only (dagstuhl blocked); opened sources give README "up to 20x" and the pa-bench notebook's 7.48x/8.26x over Edlib on synthetic data; no CPU; an algorithm win, not the language; slower on 800 bp reads.
- Panics with 'Unexpected character.' on any non-ACGT byte (N, lowercase; issues #31, #33 open); nightly-only with repeated build breaks. The notebook's 7.48x/8.26x are arithmetic means of capped-runtime ratios on synthetic data; pa-bench ignores the repo's target-cpu=native, so the run build flags are undocumented. Costs are cross-validated (no correctness flaw). The paper's 19x/5.6x/0.81x remain snippet only (drops.dagstuhl.de ENOTFOUND).

## Caveats and trade-offs

The paper's 19x, 5.6x and 0.81x figures are snippet only, because the LIPIcs and bioRxiv pages are blocked here. What could be opened is the author's own README claim and the pa-bench notebook. The full results live in a release results.zip that was not opened. No CPU model is stated in the repos. The speedup comes from a different algorithm: band doubling with Myers bit-packing plus blocks, SIMD, a new profile and the A\* heuristics. It is not a Rust-vs-C++ language effect, and A\*PA2 is slower than Edlib and BiWFA on short (800 bp) high-divergence reads. Pairwise alignment is on the edge of the string-and-text category. [retier] Panics with 'Unexpected character.' on any non-ACGT byte (issues #31, #33 open); nightly-only with repeated build breaks. The notebook's 7.48x/8.26x are arithmetic means of capped-runtime ratios on synthetic data; pa-bench ignores the repo's target-cpu=native, so the run build flags are undocumented. Costs are cross-validated.

Gains only on long, low-divergence inputs; slower than Edlib on short, highly divergent reads. Latest commit message mentions 'latest nightly', so a nightly Rust toolchain may be needed (not confirmed). MPL-2.0 is file-level copyleft. Evaluation harness lives in a separate pa-bench repo.

## Maintenance

Active research code (last commit 2026-05-22, nightly-toolchain fixes) under MPL-2.0, a file-level copyleft that permits linking. It is usable as a git dependency or C shared library, but only for upper-case ACGT input and only with a nightly toolchain.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now C.
- **Tier reason:** A WABI 2024 paper exists, but its headline numbers (19x, 5.6x, 0.81x) were seen only in a search snippet: drops.dagstuhl.de, bioRxiv and doi.org are blocked here. Under the wave-14 rule, snippet-only paper numbers stay at tier C. What could be opened is first-party: the README's 'up to 20x' sentence, and the pa-bench evals notebook (evals/astarpa2/evals.ipynb), whose saved output gives mean A\*PA2-simple speedups over Edlib of 7.48 and 8.26 on synthetic data. Neither states a CPU model or compiler version.
- **Verifier notes:** Downgraded from B to C: the peer-reviewed numbers could not be opened, and the reachable evidence (README, pa-bench notebook with 7.48x and 8.26x mean A\*PA2-simple vs Edlib on synthetic data) is first-party with no CPU or compiler version. Shortcomings: algorithmic rather than language win; slower on short reads (0.81x, snippet); hardware unstated. Metadata confirmed: MPL-2.0, 152 stars, last commit 2026-05-22 (active).
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-11 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/RagnarGrootKoerkamp/astar-pairwise-aligner>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/astar-pairwise-aligner/HEAD/README.org>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/astar-pairwise-aligner/HEAD/.cargo/config.toml>
  - <https://github.com/RagnarGrootKoerkamp/astar-pairwise-aligner/commits>
  - <https://raw.githubusercontent.com/pairwise-alignment/pa-bench/HEAD/README.md>
  - <https://github.com/pairwise-alignment/pa-bench/tree/main/evals/astarpa2>
  - <https://raw.githubusercontent.com/pairwise-alignment/pa-bench/HEAD/evals/astarpa2/justfile>
  - <https://raw.githubusercontent.com/pairwise-alignment/pa-bench/HEAD/evals/astarpa2/evals.ipynb>
  - <https://raw.githubusercontent.com/pairwise-alignment/pa-bench/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/pairwise-alignment/pa-bench/HEAD/pa-wrapper/Cargo.toml>
  - <https://raw.githubusercontent.com/pairwise-alignment/edlib-rs/HEAD/build.rs>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/astar-pairwise-aligner/HEAD/README.org>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/astar-pairwise-aligner/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/astar-pairwise-aligner/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/astar-pairwise-aligner/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/astar-pairwise-aligner/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/astar-pairwise-aligner/HEAD/astarpa2/Cargo.toml>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/astar-pairwise-aligner/HEAD/astarpa2/src/lib.rs>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/astar-pairwise-aligner/HEAD/astarpa2/src/params.rs>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/astar-pairwise-aligner/HEAD/astarpa2/src/blocks.rs>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/astar-pairwise-aligner/HEAD/pa-bitpacking/Cargo.toml>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/astar-pairwise-aligner/HEAD/pa-bitpacking/src/lib.rs>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/astar-pairwise-aligner/HEAD/pa-bitpacking/src/simd.rs>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/astar-pairwise-aligner/HEAD/pa-bitpacking/src/profile.rs>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/astar-pairwise-aligner/HEAD/astarpa-c/astarpa.h>
  - <https://github.com/RagnarGrootKoerkamp/astar-pairwise-aligner/issues?q=is%3Aissue>
  - <https://github.com/RagnarGrootKoerkamp/astar-pairwise-aligner/issues/31>
  - <https://github.com/RagnarGrootKoerkamp/astar-pairwise-aligner/issues/37>
  - <https://github.com/RagnarGrootKoerkamp/astar-pairwise-aligner/commits>
  - <https://github.com/RagnarGrootKoerkamp?tab=repositories&q=paper&type=&language=&sort=>
  - <https://github.com/RagnarGrootKoerkamp?tab=repositories&q=thesis&type=&language=&sort=>
  - <https://raw.githubusercontent.com/rust-bio/rust-bio/v1.3.0/src/alphabets/mod.rs>
  - <https://raw.githubusercontent.com/pairwise-alignment/pa-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/pairwise-alignment/pa-bench/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/pairwise-alignment/pa-bench/HEAD/Cargo.lock>
  - <https://raw.githubusercontent.com/pairwise-alignment/pa-bench/HEAD/pa-wrapper/Cargo.toml>
  - <https://raw.githubusercontent.com/pairwise-alignment/pa-bench/HEAD/evals/astarpa2/justfile>
  - <https://raw.githubusercontent.com/pairwise-alignment/pa-bench/HEAD/evals/astarpa2/evals.ipynb>
  - <https://raw.githubusercontent.com/pairwise-alignment/pa-bench/HEAD/evals/astarpa2/experiments/scaling-n.yaml>
  - <https://raw.githubusercontent.com/pairwise-alignment/edlib-rs/HEAD/build.rs>
  - https://drops.dagstuhl.de/storage/00lipics/lipics-vol312-wabi2024/LIPIcs.WABI.2024.17/LIPIcs.WABI.2024.17.pdf (blocked: ENOTFOUND)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/ragnargrootkoerkamp/astar-pairwise-aligner`) · [data/wave14/enrich/raw/github_com_ragnargrootkoerkamp_astar_pairwise_aligner.json](../../../data/wave14/enrich/raw/github_com_ragnargrootkoerkamp_astar_pairwise_aligner.json) (enrichment confidence 0.55)

</details>
