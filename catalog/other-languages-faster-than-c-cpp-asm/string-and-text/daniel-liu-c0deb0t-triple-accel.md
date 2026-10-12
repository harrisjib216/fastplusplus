# triple_accel

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust` · `MIT` · 🔴 abandoned

> Rust crate of AVX2/SSE4.1 banded Hamming, Levenshtein and restricted Damerau-Levenshtein routines; no measured win over Edlib or any C/C++ library.

| | |
|---|---|
| **Beats** | none measured: the README and benches compare only against the crate's own scalar fallback; no edlib (C++) or parasail (C) comparison found |
| **Claimed result** | No measured claim. README motivation: 'Although vectorized SIMD code allows for up to 20-30x speedups over their scalar counterparts, the difficulty of handling platform-dependent SIMD code makes SIMD routines less attractive' (a general statement about SIMD, not a figure measured for this crate and not against a C/C++ baseline). No numeric comparison against Edlib or parasail in the repo. |
| **Workload** | Hamming and Levenshtein distance and search on random strings (criterion benches), SIMD routines against the crate's own naive scalar versions. |
| **Metric** | throughput |
| **Compiler and flags** | README recommends RUSTFLAGS='-C target-cpu=native'; Cargo release profile opt-level=3, codegen-units=1, panic='abort'; benches use criterion 0.3. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Why it wins** | SIMD vectorisation (AVX2 or SSE4.1) of Hamming and Levenshtein routines with the vector width chosen from the string lengths; the README ties the 20-30x figure only to the scalar fallback. |
| **Adoption** | 109 stars, 15 forks; crates.io 0.4.0, about 2.04M downloads (about 232k recent) |
| **Last commit** | 2022-12-05 |
| **Links** | [repository](https://github.com/Daniel-Liu-c0deb0t/triple_accel) · [benchmark](https://github.com/Daniel-Liu-c0deb0t/triple_accel) |

## Verdict

Nothing against a C or C++ baseline was measured: the README's 20-30x line is a general remark about SIMD versus scalar code, and the crate's criterion benches compare only its own SIMD and scalar routines without published numbers. The only cross-library timing found is block-aligner's rand_scan bench (Rust, rust-bio's wrapper around triple_accel), which does different work (exact bounded Levenshtein against block-aligner's adaptive-band NW1 scoring with affine gaps), so it is not a like-for-like comparison.

## Use it when

- Rust code on x86-64 that needs exact Levenshtein or Hamming distance between byte strings of tens to a few thousand bytes where the expected distance is small relative to length (the banded, exponential-search path is what pays off).
- Fuzzy matching or deduplication over ASCII keys (BK-trees, spell lookups); bk-tree and editdistancek on crates.io already depend on it.
- Short-read or barcode matching with unit or simple affine-ish costs where a k-bounded answer (None above k) is useful and no traceback precision with gap-open costs is needed.
- Builds where a zero-dependency crate with automatic scalar fallback is preferred over FFI to Edlib or parasail.

## Skip it when

- rdamerau or any RDAMERAU_COSTS call on the SIMD path: issue #17 (open) reports rdamerau('AL NASSER','HALA NASSER') returns 3 with SIMD and 2 with default-features = false, and levenshtein_simd_k_with_opts('warsa','was',3,RDAMERAU_COSTS) returns 3 instead of 2; the proposed fix (PR #19) is unmerged.
- Tracebacks with non-zero gap-open costs: issue #9 (open since May 2022) reports inaccurate traceback.
- Long sequences with high divergence: with a large bound the band covers most of the matrix and the 16-bit or 32-bit paths are used; block-aligner's own bench (via rust-bio's bounded_levenshtein wrapper) times it at about 7.8 ms for a 10 kbp pair at K=1000.
- aarch64 / Apple Silicon or WASM: SIMD paths are x86-only; elsewhere every call runs the scalar fallback (maintainer in issue #11: no NEON support).
- Unicode text: u8 only; levenshtein_simd_k_str maps non-ASCII chars to bytes and returns None for more than 256 distinct characters, which is indistinguishable from 'distance above k' (PR #21 open).

## How it is fast

Levenshtein runs as a Ukkonen-style banded DP (band set by the bound k, which levenshtein_exp finds by exponential search starting at k=30 and doubling) whose anti-diagonals are held in SIMD registers ('Jewel' vectors: 1, 2, 4 or 8 AVX2 registers of 8-bit cells, or wider 16-bit and 32-bit cells), updated with alignr/permute shifts, cmpeq and unsigned min. The cell width and register count are chosen at runtime from k and the string lengths, and AVX2 or SSE4.1 is picked by is_x86_feature_detected. Hamming uses a 32-byte cmpeq per step (hamming_simd_parallel), with SWAR u64/u128 variants for aligned buffers.

## Compared with alternatives

Pick it over block-aligner (same author, affine-gap adaptive banding, NEON and WASM support) only when you need exact unit-cost Levenshtein or Hamming distance in a tiny dependency-free crate on x86; for pattern search against Edlib-class speed Sassy is the measured choice, and for exact global alignment of long divergent sequences A\*PA2 or bitdp have published C/C++ comparisons.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none at runtime (criterion 0.3 and rand 0.7.3 are dev-dependencies for benches) |
| **Minimum toolchain** | Rust 2018 edition on stable; no rust-version (MSRV) declared in Cargo.toml |
| **Platforms** | any for scalar paths; SIMD only on x86 and x86-64 (AVX2 or SSE4.1, detected at runtime) |
| **Thread safety** | not documented; the API is free functions over borrowed slices with no global mutable state in the files read |
| **Drop-in for the baseline** | no |

## Gotchas

- hamming_words_64 and hamming_words_128 are safe pub fns that cast &[u8] to u64/u128 pointers and read a whole word for the tail: issue #20 (open, Miri reproductions) shows out-of-bounds reads and misaligned loads on ordinary slices. They are only safe on buffers from alloc_str; the default hamming() uses hamming_simd_parallel with unaligned loads and is not affected.
- alloc_str builds a Vec&lt;u8&gt; from a Vec&lt;u128&gt; allocation, so it frees with a different alignment than it allocated (issue #6, open; the maintainer agreed and proposed removing it) and can overflow its capacity calculation (issue #16).
- hamming_search and hamming_search_simd_with_opts panic if the haystack contains a zero byte; the &str and byte APIs give no error type, only Option.
- The crate's benches (benches/rand_benchmarks.rs) check each SIMD result against the naive routine before timing, but compare only against its own scalar code on random printable-ASCII strings with 5-10% edits, and levenshtein_naive is the full O(nm) DP, so that group mixes the banding gain with the SIMD gain; no results are saved in the repo (issue #8 asks for them).

## Known shortcomings

- No C or C++ baseline and no numbers; the '20-30x' is README motivation, not a measurement. About 2.04M crates.io downloads; abandoned since 2022-12-05.
- Enricher: wrong results with the SIMD path on (issue #17, open: rdamerau('AL NASSER','HALA NASSER') returns 3, should be 2; fix PR #19 unmerged); traceback wrong with gap-open costs (#9); soundness issues #4, #6, #16, #20 (alloc_str frees with the wrong alignment; hamming_words_64/128 are safe public functions that read out of bounds and misaligned under Miri); no NEON path. Its own bench compares SIMD only to its own scalar code, whose levenshtein_naive is full O(nm) DP, so banding gains mix into the SIMD gain; block-aligner's 34x row calls it through rust-bio with different scoring and work.

## Caveats and trade-offs

No C/C++ comparison in the repo (benches/rand_benchmarks.rs compares only hamming_naive, levenshtein_naive and the crate's SIMD routines, with no saved results). The only cross-implementation timing found is inside block-aligner's own notebook (Rust against Rust): triple_accel 7,809,720 ns for the 1000/10000 nucleotide case against 226,318 ns for block-aligner (about 34x slower, derived from page data) and 23,337 ns against 23,150 ns for the 100/1000 case. A web search found no third-party Edlib or parasail benchmark; the pa-bench harness (pairwise-alignment/pa-bench) wraps triple_accel next to Edlib and parasail but its published result files were not reachable. Notable by usage (about 2.04M crates.io downloads, mostly as a dependency) rather than stars; recorded at D per the seed-record instruction. Last commit 2022-12-05, last release 0.4.0 in June 2021. [retier] Enricher: SIMD path returns wrong results (issue #17, fix PR #19 unmerged); traceback wrong with gap-open costs (#9); soundness issues #4, #6, #16, #20 (misaligned free, out-of-bounds reads in safe public functions under Miri).

u8 byte strings only (no Unicode); x86 and x86-64 only for the SIMD paths (AVX2 and SSE4.1, runtime-detected), other CPUs fall back to scalar; the SIMD element width and vector type are selected at runtime from the input lengths.

## Maintenance

Abandoned: last commit 2022-12-05, last release 0.4.0 on 2021-06-18, with open soundness (issues #4, #6, #16, #20) and wrong-result (#9, #17) reports and five unmerged PRs; MIT-licensed and still widely pulled in (about 2.04M crates.io downloads, mostly via bk-tree and editdistancek), so pin it and avoid rdamerau and the words_\* Hamming helpers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now D.
- **Tier reason:** The README and benches/rand_benchmarks.rs compare only against the crate's own naive scalar routines and publish no numbers; the '20-30x' sentence is a general motivating remark about SIMD code, not a measurement, and no C or C++ (Edlib, parasail) comparison exists in the repo.
- **Verifier notes:** Keep at D: no C/C++ baseline and no published numbers; the 20-30x line is motivation, not a measurement. Widely depended on (about 2.04M crates.io downloads), so notable despite 109 stars; abandoned (last commit 2022-12-05).
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-112 (wave 14 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/Daniel-Liu-c0deb0t/triple_accel>
  - <https://github.com/Daniel-Liu-c0deb0t/triple_accel/commits>
  - <https://raw.githubusercontent.com/Daniel-Liu-c0deb0t/triple_accel/HEAD/README.md>
  - <https://raw.githubusercontent.com/Daniel-Liu-c0deb0t/triple_accel/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Daniel-Liu-c0deb0t/triple_accel/HEAD/benches/rand_benchmarks.rs>
  - <https://crates.io/api/v1/crates/triple_accel>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Daniel-Liu-c0deb0t/triple_accel/HEAD/README.md>
  - <https://raw.githubusercontent.com/Daniel-Liu-c0deb0t/triple_accel/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Daniel-Liu-c0deb0t/triple_accel/HEAD/benches/rand_benchmarks.rs>
  - <https://raw.githubusercontent.com/Daniel-Liu-c0deb0t/triple_accel/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/Daniel-Liu-c0deb0t/triple_accel/HEAD/src/hamming.rs>
  - <https://raw.githubusercontent.com/Daniel-Liu-c0deb0t/triple_accel/HEAD/src/levenshtein.rs>
  - <https://raw.githubusercontent.com/Daniel-Liu-c0deb0t/triple_accel/HEAD/src/jewel.rs>
  - <https://github.com/Daniel-Liu-c0deb0t/triple_accel/issues?q=is%3Aissue>
  - <https://github.com/Daniel-Liu-c0deb0t/triple_accel/issues/17>
  - <https://github.com/Daniel-Liu-c0deb0t/triple_accel/issues/20>
  - <https://github.com/Daniel-Liu-c0deb0t/triple_accel/issues/6>
  - <https://github.com/Daniel-Liu-c0deb0t/triple_accel/issues/11>
  - <https://github.com/Daniel-Liu-c0deb0t/triple_accel/commits>
  - <https://github.com/Daniel-Liu-c0deb0t/triple_accel/pulls>
  - <https://crates.io/api/v1/crates/triple_accel>
  - <https://crates.io/api/v1/crates/triple_accel/reverse_dependencies?per_page=10>
  - <https://pypi.org/pypi/lev-rs/json>
  - <https://raw.githubusercontent.com/KarelZe/lev/HEAD/Cargo.toml>
  - <https://github.com/Daniel-Liu-c0deb0t/block-aligner>
  - <https://github.com/Daniel-Liu-c0deb0t/block-aligner/tree/main/examples>
  - <https://github.com/Daniel-Liu-c0deb0t/block-aligner/tree/main/benches>
  - <https://raw.githubusercontent.com/Daniel-Liu-c0deb0t/block-aligner/main/benches/rand_scan.rs>
  - <https://raw.githubusercontent.com/Daniel-Liu-c0deb0t/block-aligner/main/examples/nanopore_bench.rs>
  - <https://raw.githubusercontent.com/Daniel-Liu-c0deb0t/block-aligner/main/examples/nanopore_bench_global.rs>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/daniel-liu-c0deb0t/triple_accel`) · [data/wave14/enrich/raw/github_com_daniel_liu_c0deb0t_triple_accel.json](../../../data/wave14/enrich/raw/github_com_daniel_liu_c0deb0t_triple_accel.json) (enrichment confidence 0.85)

</details>
