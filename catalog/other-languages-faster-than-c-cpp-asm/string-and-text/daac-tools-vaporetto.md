# Vaporetto (Rust pointwise Japanese tokenizer)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Rust pointwise Japanese word segmenter that runs KyTea's own models about 7.6-8.7x faster than KyTea (C++).

| | |
|---|---|
| **Beats** | KyTea (C++ pointwise word segmenter, 2020-04-03 build); MeCab 2020-09-14 also timed with other models |
| **Claimed result** | README: 'Vaporetto is 8.7 times faster than KyTea.' Wiki Speed-Comparison (Vaporetto v0.4.0, mean of 100 runs, ms): KyTea 219.6 (std 2.9), Vaporetto 29.0 (0.6), Vaporetto charwise 25.3 (0.4), so 7.6x and 8.7x (derived from page data); MeCab IPAdic 102.9 and UniDic 255.1, Lindera 397.1, sudachi.rs 286.2 and rust-tinysegmenter 272.7 use other dictionaries or models. arXiv 2406.17185 abstract: 5.7 times faster than the current approach based on the same model without loss of accuracy; NLP2022 paper: 5.4x vs KyTea (both snippet only). |
| **Workload** | Tokenizing the Aozora Bunko text of 'I Am a Cat' (Soseki Natsume), elapsed time measured 100 times (mean and std reported), KyTea and Vaporetto both using the KyTea compact SVM model based on BCCWJ and UniDic; whether model loading is excluded is not stated. Measured on Vaporetto v0.4.0 (wiki last edited 2022-06-09), not the current 0.6.5. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-8086K @ 4.00GHz, 64 GiB, CentOS 7.5 |
| **Compiler and flags** | Rust 1.60.0 and GCC 11.2.0 (wiki); optimisation flags not stated for either side. The workspace Cargo.toml has no profile override (cargo release default opt-level 3); how KyTea was configured is not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Why it wins** | Not spelled out on the pages opened; the README lists the double-array Aho-Corasick paper (daachorse) among its references, which suggests the feature lookup is built on it. |
| **Adoption** | 299 stars; crates.io 331k downloads (vaporetto 0.6.5) |
| **Last commit** | 2026-07-20 |
| **Links** | [repository](https://github.com/daac-tools/vaporetto) · [benchmark](https://github.com/daac-tools/vaporetto/wiki/Speed-Comparison) |

## Verdict

The first-party wiki (Vaporetto v0.4.0, Rust 1.60.0 and GCC 11.2.0 on an Intel Core i7-8086K under CentOS 7.5) tokenized Natsume Soseki's 'I Am a Cat' 100 times with the same KyTea compact SVM model: KyTea (2020-04-03) 219.6 ms vs Vaporetto 29.0 ms (7.6x) and the charwise build 25.3 ms (8.7x), ratios derived from page data. The matching public harness (tokenizer-speed-bench) excludes model loading on both sides and times only segmentation; MeCab, Lindera, sudachi.rs and rust-tinysegmenter rows use other dictionaries or algorithms and are not like-for-like.

## Use it when

- High-throughput Japanese word segmentation (search indexing, corpus preprocessing for ML) where boundary decisions are enough and full morphological analysis is not needed
- Existing KyTea users who want the same model's segmentation faster: convert the .mod file with convert_kytea_model and keep the behaviour
- Full-text search on tantivy (vaporetto_tantivy crate) or Python pipelines (python-vaporetto)
- Browser or embedded targets: the crate builds with no_std plus alloc and has a Wasm demo
- Fixing specific mis-segmentations without retraining, by editing per-pattern boundary weights with manipulate_model

## Skip it when

- Full morphological analysis (lemmas, conjugation forms, UniDic fields): tag prediction is labelled experimental and lemma/UniDic-ID models are an open request (#148); a MeCab-style analyser such as Vibrato fits better
- Short-lived processes where startup dominates: the published timings exclude model loading, and the README says the default charwise automaton can make model loading slower
- Loading predictors from untrusted bytes: Predictor::deserialize_from_slice_unchecked is an unsafe fn that skips validation (Model::read validates)
- Pipelines that need a stable model file format: bincode is unmaintained and the maintainer has chosen postcard as its replacement (issue #153, PR #156), so serialized files may change
- Non-Japanese KyTea models on older releases: Chinese KyTea models failed to convert ('unsupported character type: 4', issue #110) until PR #111 in September 2023

## How it is fast

All character n-gram features and dictionary words go into one double-array Aho-Corasick automaton (daachorse, charwise variant by default), and each pattern's weight vector is pre-merged with the weights of its suffix patterns at model-build time, so one overlapping scan of the sentence adds one precomputed weight vector per match to the boundary-score array instead of looking up every n-gram around every boundary. Character-type features are scored from a cache (cache-type-score), and weights are 32-bit integers in fixed 8-lane arrays (fix-weight-length) so the additions vectorize without intrinsics. The gain is algorithmic restructuring of the same model, not Rust versus C++.

## Compared with alternatives

None of the listed siblings segments Japanese: the Rust regex crate and the LangArena word-count rows split on whitespace or patterns. Within the catalog, use Vibrato (also daac-tools) when you need MeCab-dictionary morphological analysis, and Vaporetto when word boundaries (optionally with tags) from a KyTea-style model are enough and speed matters most.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | bincode 2, daachorse 1, hashbrown 0.15; liblinear only with the train feature; distribution models are zstd-compressed and must be decompressed outside the API (zstd or ruzstd crate) |
| **Minimum toolchain** | Rust 1.85 for the released 0.6.5 (main branch now declares 1.88); the optional portable-simd feature needs nightly |
| **Platforms** | any target with alloc (no_std supported, Wasm demo); no architecture-specific intrinsics |
| **Thread safety** | predict takes &self plus a caller-owned &mut Sentence, so one Predictor can serve many threads with one Sentence each; Send/Sync guarantees are not documented |
| **Drop-in for the baseline** | partial — reads converted KyTea models and reproduces KyTea word segmentation, but exposes a different Rust API and CLI, and the README documents KyTea model conversion for word segmentation only |

## Gotchas

- The README's 8.7x is the charwise-automaton build (25.3 ms vs KyTea 219.6 ms), which is now the default feature; the default build at the time measured 29.0 ms (7.6x), and the authors' own papers report 5.7x (arXiv 2406.17185) and 5.4x (NLP2022), so expect roughly 5-9x depending on version and machine.
- The benchmark code exists outside the repo: legalforce-research/tokenizer-speed-bench (commits by the Vaporetto author; run_all.sh 100 iterations on wagahaiwa_nekodearu.txt with KyTea model jp-0.4.7-5). Both bench/kytea-bench/main.cc and bench/vaporetto-bench load the model before the timer, read all lines into memory first and time only segmentation, KyTea's library is built by its own configure at -O3 (bench main -O2 at the March 2022 commit 84383b2) and Vaporetto with cargo --release, so no harness flaw was found. Caveats: neither side's word count is checked against the other, and the charwise row is not in the harness at that commit (it pins Vaporetto rev a8308cd without the charwise feature). The harness plus the wiki's compiler versions and CPU could support a move from tier C to B or A.
- Sentence::update_raw returns an error for empty text, and the benchmark harness unwraps it, so strip empty lines before tokenizing.
- Weights are 32-bit integers; the README warns that hand-edited dictionary weights can overflow the boundary total.

## Known shortcomings

- Wiki numbers (KyTea 219.6 ms vs 29.0/25.3 ms, v0.4.0, 2022) with flags unstated; the win is algorithmic (same model, pattern-score arrays plus daachorse), not the language; the papers' 5.7x (arXiv) and 5.4x (NLP2022) are snippet only.
- Public harness found: legalforce-research/tokenizer-speed-bench (author's commits) loads the KyTea and Vaporetto models outside the timer, preloads lines and times segmentation only, with the KyTea library built -O3 through its own configure; no flaw found. Word counts were never cross-checked, and the charwise 8.7x row is not in the harness at matching commit 84383b2 (Vaporetto rev a8308cd, no charwise). arxiv.org and anlp.jp are DNS-blocked, so the NLP2022 and arXiv timing methods were not read.

## Caveats and trade-offs

First-party wiki table from 2022 (Vaporetto v0.4.0) with a single corpus; no benchmark script is published (evaluate/ is an accuracy tool), build flags for both sides and whether model loading is excluded are not stated; the KyTea comparison is the only like-for-like row (same model); the 8.7x headline is the charwise variant (7.6x for the default mode), and the authors' own papers report smaller gains (5.7x in arXiv 2406.17185, 5.4x in NLP2022, snippet only). The speedup comes from a restructured inference algorithm, not from Rust versus C++. [retier] Public harness: legalforce-research/tokenizer-speed-bench (author's commits) loads the KyTea and Vaporetto models outside the timer, preloads lines and times segmentation only, with the KyTea library built -O3 through its own configure. Word counts were never cross-checked, and the charwise 8.7x row is not in the harness at matching commit 84383b2 (Vaporetto rev a8308cd, no charwise).

Needs a Vaporetto model (converted from a KyTea model or trained); pointwise prediction, not full morphological analysis.

## Maintenance

Maintained at a slow pace (last commit 2026-07-20, last crate release 0.6.5 on 2025-03-17, 331k downloads with 74.6k recent, a serialization switch to postcard in progress); MIT or Apache-2.0 and copyable, with free distributed models and KyTea model conversion.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party wiki table (KyTea 219.6 ms, Vaporetto 29.0 ms, charwise 25.3 ms) with CPU and compiler versions but no optimisation flags and no benchmark script in the repo (evaluate/ measures accuracy); the arXiv 2406.17185 preprint and the NLP2022 paper are first-party and were seen only in search snippets, so C.
- **Verifier notes:** Numbers match the wiki and README; record is accurate. For wave 14 the win is algorithmic (same model, different inference method), not language-level; the authors' papers give 5.7x (arXiv) and 5.4x (NLP2022) rather than the 8.7x headline.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-83 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/daac-tools/vaporetto/wiki/Speed-Comparison>
  - <https://raw.githubusercontent.com/daac-tools/vaporetto/HEAD/README.md>
  - <https://raw.githubusercontent.com/daac-tools/vaporetto/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/daac-tools/vaporetto/HEAD/evaluate/src/main.rs>
  - <https://github.com/daac-tools/vaporetto>
  - <https://github.com/daac-tools/vaporetto/commits>
  - <https://github.com/daac-tools/vaporetto/tree/main/evaluate>
  - <https://crates.io/api/v1/crates/vaporetto>
- **Sources the enricher read:**
  - <https://github.com/daac-tools/vaporetto>
  - <https://github.com/daac-tools/vaporetto/commits/main>
  - <https://github.com/daac-tools/vaporetto/issues?q=is%3Aissue>
  - <https://github.com/daac-tools/vaporetto/issues/110>
  - <https://github.com/daac-tools/vaporetto/issues/153>
  - <https://github.com/daac-tools/vaporetto/wiki/Speed-Comparison>
  - <https://raw.githubusercontent.com/daac-tools/vaporetto/HEAD/README.md>
  - <https://raw.githubusercontent.com/daac-tools/vaporetto/HEAD/README-ja.md>
  - <https://raw.githubusercontent.com/daac-tools/vaporetto/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/daac-tools/vaporetto/HEAD/vaporetto/Cargo.toml>
  - <https://raw.githubusercontent.com/daac-tools/vaporetto/HEAD/vaporetto/README.md>
  - <https://raw.githubusercontent.com/daac-tools/vaporetto/HEAD/vaporetto/src/lib.rs>
  - <https://raw.githubusercontent.com/daac-tools/vaporetto/HEAD/vaporetto/src/predictor.rs>
  - <https://raw.githubusercontent.com/daac-tools/vaporetto/HEAD/vaporetto/src/model.rs>
  - <https://raw.githubusercontent.com/daac-tools/vaporetto/HEAD/vaporetto/src/char_scorer.rs>
  - <https://raw.githubusercontent.com/daac-tools/vaporetto/HEAD/vaporetto/src/char_scorer/boundary_scorer.rs>
  - <https://raw.githubusercontent.com/daac-tools/vaporetto/HEAD/vaporetto/src/type_scorer.rs>
  - <https://raw.githubusercontent.com/daac-tools/vaporetto/HEAD/vaporetto/src/sentence.rs>
  - <https://raw.githubusercontent.com/daac-tools/vaporetto/HEAD/predict/src/main.rs>
  - <https://raw.githubusercontent.com/daac-tools/vaporetto/v0.4.0/predict/src/main.rs>
  - <https://crates.io/api/v1/crates/vaporetto>
  - <https://github.com/legalforce-research/tokenizer-speed-bench>
  - <https://github.com/legalforce-research/tokenizer-speed-bench/commits/main>
  - <https://github.com/legalforce-research/tokenizer-speed-bench/tags>
  - <https://github.com/legalforce-research/tokenizer-speed-bench/tree/main/bench/vaporetto-bench>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/HEAD/run_all.sh>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/HEAD/compile_all.sh>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/HEAD/stats.py>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/HEAD/download_resources.sh>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/HEAD/bench/vaporetto-bench/Cargo.toml>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/HEAD/bench/vaporetto-bench/build.rs>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/HEAD/bench/vaporetto-bench/src/main.rs>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/HEAD/bench/kytea-bench/main.cc>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/84383b2/run_all.sh>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/84383b2/compile_all.sh>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/84383b2/stats.py>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/84383b2/README.md>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/84383b2/bench/vaporetto-bench/Cargo.toml>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/84383b2/bench/vaporetto-bench/src/main.rs>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/84383b2/bench/kytea-bench/main.cc>
  - <https://raw.githubusercontent.com/neubig/kytea/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/neubig/kytea/HEAD/src/lib/Makefile.am>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/daac-tools/vaporetto`) · [data/wave14/enrich/raw/github_com_daac_tools_vaporetto.json](../../../data/wave14/enrich/raw/github_com_daac_tools_vaporetto.json) (enrichment confidence 0.8)

</details>
