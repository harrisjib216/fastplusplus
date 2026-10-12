# Vibrato (Rust MeCab reimplementation)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Rust reimplementation of MeCab's Viterbi lattice tokenizer for Japanese; about 2x faster than MeCab on IPADIC and UniDic.

| | |
|---|---|
| **Beats** | MeCab (C++ Japanese morphological analyzer), 2020-09-14 build |
| **Claimed result** | Wiki Speed-Comparison table: Vibrato 0.5.0 ipadic 42 ms vs MeCab ipadic 87 ms (about 2.1x, derived from page data); Vibrato unidic-cwj 75 ms vs MeCab unidic-cwj 179 ms (about 2.4x, derived from page data); the Vibrato raw-connector variant takes 1364 ms (7.6x slower than MeCab) and dual-connector 170 ms (about equal). |
| **Workload** | Tokenize all 2,346 lines (158.8 characters on average) of 'I Am a Cat' (Aozora Bunko). Each tool reads the lines into memory, then times only the tokenization loop with a steady clock, single-threaded. run_all.sh runs 101 iterations, each a fresh process, and iteration 0 is a warm-up. MeCab uses mecab-ipadic 2.7.0 or unidic-cwj 3.1.1, and Vibrato uses its v0.5.0 precompiled dictionaries built from the same sources. The MeCab driver calls tagger-&gt;parse() with -Owakati, which builds a space-separated output string. The Vibrato driver calls worker.tokenize() and only counts tokens. |
| **Metric** | latency |
| **Hardware** | Intel Core i9-12900K, 64 GB DDR5, Ubuntu 22.04 |
| **Compiler and flags** | From tokenizer-speed-bench compile_all.sh (tag vibrato-0.5.0-benchmark): MeCab (taku910/mecab submodule) is built with its own ./configure, whose configure.in sets CFLAGS/CXXFLAGS to '-O3 -Wall' under GCC. The MeCab driver is built with 'g++ -std=c++11 -O3 ./main.cc -lmecab'. The Vibrato 0.5.0 crate is built with RUSTFLAGS='-C target-feature=+avx2' cargo build --release (release profile, opt-level 3). No gcc or rustc version is stated, and MeCab gets no -march, so only the Rust side is built for AVX2. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | README: reimplementation of the MeCab algorithm simplified and optimised; for dictionaries with a large connection matrix (unidic-cwj, 459 MiB) cache-efficient id mappings make it faster. |
| **Adoption** | 425 stars |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/daac-tools/vibrato) · [benchmark](https://github.com/daac-tools/vibrato/wiki/Speed-Comparison) |

## Verdict

On the authors' tokenizer-speed-bench (tag vibrato-0.5.0-benchmark), tokenizing the 2,346 lines of 'I Am a Cat' on an i9-12900K took 42 ms with Vibrato 0.5.0 vs 87 ms with MeCab 2020-09-14 on IPADIC 2.7.0, and 75 vs 179 ms on unidic-cwj 3.1.1 (about 2.1x and 2.4x, derived from page data); MeCab was built -O3 by its own configure with GCC (version not stated), Vibrato with cargo --release plus +avx2, and dictionary loading was excluded from the timing.

## Use it when

- Batch or server-side Japanese tokenization in Rust where per-sentence latency matters and the dictionary is loaded once per process.
- Large-matrix dictionaries such as unidic-cwj 3.1.1 (459 MiB matrix), where the measured gap to MeCab was largest (75 vs 179 ms on the benchmark corpus).
- IPADIC-based pipelines that can use the precompiled, id-remapped release dictionaries (42 vs 87 ms for MeCab on the same corpus).
- Projects that want to train or re-cost a MeCab-style dictionary on their own corpus without the C++ toolchain.

## Skip it when

- Short-lived processes or CLIs that tokenize a little text: the dictionary is fully deserialized into RAM, and a user reported about 14 s and about 1 GB to load UniDic cwj 2023-02 vs 28 ms for MeCab's mmap (issue #150, open; no mmap support, #148).
- Memory-constrained or embedded targets: the maintainers point such users to Vaporetto, since the full unidic-cwj 3.1.1 model is listed at 717 MB.
- When output must match MeCab byte for byte: defaults differ (spaces become tokens, unknown-word grouping is unbounded), and even with -S -M 24 the README admits tie-break corner cases.
- C or C++ codebases that would need an FFI layer; there is no C API in the repo.
- The raw-connector compact UniDic model if speed matters: it measured 1364 ms, 7.6x slower than MeCab.

## How it is fast

Same Viterbi min-cost search as MeCab, with a lexicon in a crawdad double-array trie and a lattice indexed by end position whose best predecessor is computed when each node is inserted. The main gain is cache locality of the connection-cost matrix: left/right connection ids are renumbered by occurrence frequency gathered from a training corpus (the map/reorder tool), so hot matrix cells sit together; the NLP2023 paper (C2-4, snippet only, the PDF host was unreachable) reports about 40% from this and over 2x vs MeCab. Compact models trade speed for size: raw-connector (mecab_smalldic-style) and dual-connector score splitting.

## Compared with alternatives

Pick Vibrato over Vaporetto (same organisation, 21 ms on the same corpus) when you need MeCab-dictionary lattice output with IPADIC or UniDic POS features rather than pointwise word boundaries from a KyTea-style model; jieba-rs is the analogue for Chinese, not Japanese.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | bincode 2, crawdad, csv-core, hashbrown, regex; rucrf for the default-on train feature; the caller needs zstd or ruzstd to decompress the distributed system.dic.zst |
| **Minimum toolchain** | Rust 1.88 at HEAD (rust-version in vibrato/Cargo.toml); crates.io 0.5.2 declares 1.85 |
| **Platforms** | any 32- or 64-bit Rust target (compile_error otherwise); a Wasm demo exists; no CPU feature required, though the benchmark build added +avx2 |
| **Thread safety** | not documented; the API shape is one immutable Tokenizer shared by reference and one Worker per thread, since a Worker owns the mutable lattice and sentence buffers |
| **Drop-in for the baseline** | partial — same algorithm and source dictionaries, but a Rust API, its own binary dictionary format (converted from MeCab resources), and MeCab-identical output only with ignore_space and max_grouping_len 24, minus tie-break corner cases |

## Gotchas

- The headline speed depends on remapped connection ids: the v0.5.0 release models were reordered with statistics from BCCWJ v1.1 CORE (v0.4.0 used Aozora Bunko text). A dictionary you compile yourself is slower until you run the map/reorder step from docs/map.md on representative text.
- Dictionary::read() expects decompressed bytes; the distributed models are zstd files that must be wrapped in a decoder first. The format is tied to the 'VibratoTokenizer 0.5' magic, so models from other minor versions are refused.
- read_unchecked was removed in 0.5.2, so the published benchmark harness (which calls it) does not build against current releases as written. A fix for huge allocations from an untrusted matrix.def header (#167, 2026-10-03) is on master only, not in crates.io 0.5.2.
- Harness flaws behind the numbers: the timed Vibrato loop only counts tokens while MeCab's -Owakati parse() builds an output string; only the Rust side was built with +avx2; MeCab mmaps its dictionary, so its timed loop likely absorbs page faults that Vibrato paid during the untimed load (inference); runs were not pinned to a core on the hybrid P/E-core i9-12900K. The non-compatible default mode matters little on this corpus: it has 47 ASCII spaces in 10 of 2,346 lines.

## Known shortcomings

- No g++ or rustc version; AVX2 on the Vibrato side only; MeCab formats -Owakati output while Vibrato only counts tokens (not MeCab-compatible mode, outputs not compared); MeCab mmap page faults probably inside the timed loop (harness legalforce-research/tokenizer-speed-bench, tag vibrato-0.5.0-benchmark).
- Runs were not pinned to a core on the hybrid i9-12900K; speed depends on dictionaries whose connection ids were remapped with BCCWJ CORE statistics (v0.5.0 release), so self-compiled dictionaries are slower until the map step runs. The benchmark corpus has only 47 ASCII spaces, so the non-compatible default mode barely matters. Dictionary load is untimed: issue #150 reports 14 s and about 1 GB for UniDic against MeCab's 28 ms. The benchmark calls read_unchecked, removed in 0.5.2. The paper PDF on anlp.jp is unreachable (ENOTFOUND), so its result is from a search snippet only.

## Caveats and trade-offs

First-party benchmark run by the authors' organisation (LegalForce / daac-tools): one corpus (one novel) on one machine. Compiler versions are not stated. The two sides do not do equal work. (1) MeCab's parse() with -Owakati formats an output string, while Vibrato only builds the lattice and counts tokens. (2) Vibrato runs with default settings, not the MeCab-compatible -S -M 24 options, so its tokens can differ from MeCab's (README 'MeCab-compatible options'), and outputs were not compared. (3) Only Vibrato is compiled with AVX2 (+avx2); MeCab uses generic x86-64 -O3. (4) MeCab mmaps its dictionary and 459 MiB unidic matrix, so the timed loop likely pays page faults that Vibrato, which reads the whole dictionary into memory before timing, does not. This is an inference from the harness, not a measurement. The raw-connector compact model (1364 ms) is 7.6x slower than MeCab, and the dual-connector model (170 ms) is roughly level with it. The speedup is largest with the large-matrix unidic dictionary. The numbers are for Vibrato 0.5.0 (early 2023) and have not been re-run for later releases. [retier] Runs were not pinned to a core on the hybrid i9-12900K; the headline depends on dictionaries whose connection ids were remapped with BCCWJ CORE statistics (v0.5.0), so self-compiled dictionaries are slower until the map step runs. The benchmark corpus has only 47 ASCII spaces, so the non-compatible default mode barely matters. Dictionary load is untimed (issue #150: 14 s and about 1 GB for UniDic against MeCab's 28 ms). The benchmark calls read_unchecked, removed in 0.5.2; the paper result is from a search snippet only.

Rust library, C++ needs FFI or the CLI. Uses its own compiled dictionary format (zstd compressed system.dic.zst), converted from MeCab dictionaries; MeCab-compatible output options exist.

## Maintenance

Maintained (master commits through 2026-10-03, last crates.io release 0.5.2 in March 2025, MIT OR Apache-2.0); the benchmark is first-party, dates from v0.5.0 (February 2023), and issue #96 to refresh it is still open, while its harness gives MeCab extra output formatting and a non-AVX2 build and leaves dictionary load time (Vibrato's weak spot) out of the measurement.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The wiki Speed-Comparison page (last edited 2023-03-01) has first-party times for Vibrato 0.5.0 and MeCab 2020-09-14 on an i9-12900K. The harness is public (legalforce-research/tokenizer-speed-bench, tag vibrato-0.5.0-benchmark: compile_all.sh, run_all.sh, bench/mecab-unidic-3_1_1-bench/main.cc, bench/vibrato-bench/src/main.rs) and its flags are visible, but neither the g++ nor the rustc version is stated anywhere. Under the project's precedent a missing compiler version keeps it out of A, and the authors' own run is not B, so it stays C.
- **Verifier notes:** Numbers match the wiki exactly: ipadic 42 vs 87 ms (2.07x) and unidic 75 vs 179 ms (2.39x), derived from page data. The baseline is MeCab built at -O3 by its own configure, so the C++ side is not crippled. The gain is a reimplementation with a different data layout (cache-efficient id mapping of the connection matrix) plus a lighter timed path, not a Rust codegen effect. Shortcomings to record: no compiler versions, AVX2 only on the Vibrato side, MeCab formats -Owakati output while Vibrato only counts tokens, outputs not checked equal (non-compatible default mode), and likely mmap page faults inside MeCab's timed loop (inference).
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-14 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/daac-tools/vibrato/wiki/Speed-Comparison>
  - <https://raw.githubusercontent.com/wiki/daac-tools/vibrato/Speed-Comparison.md>
  - <https://github.com/daac-tools/vibrato>
  - <https://github.com/daac-tools/vibrato/commits>
  - <https://raw.githubusercontent.com/daac-tools/vibrato/HEAD/README.md>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/vibrato-0.5.0-benchmark/README.md>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/vibrato-0.5.0-benchmark/compile_all.sh>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/vibrato-0.5.0-benchmark/run_all.sh>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/vibrato-0.5.0-benchmark/download_resources.sh>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/vibrato-0.5.0-benchmark/.gitmodules>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/vibrato-0.5.0-benchmark/bench/mecab-unidic-3_1_1-bench/main.cc>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/vibrato-0.5.0-benchmark/bench/vibrato-bench/src/main.rs>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/vibrato-0.5.0-benchmark/bench/vibrato-bench/Cargo.toml>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/vibrato-0.5.0-benchmark/stats.py>
  - <https://raw.githubusercontent.com/taku910/mecab/HEAD/mecab/configure.in>
- **Sources the enricher read:**
  - <https://github.com/daac-tools/vibrato>
  - <https://raw.githubusercontent.com/daac-tools/vibrato/HEAD/README.md>
  - <https://raw.githubusercontent.com/daac-tools/vibrato/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/daac-tools/vibrato/HEAD/vibrato/Cargo.toml>
  - <https://raw.githubusercontent.com/daac-tools/vibrato/HEAD/vibrato/src/lib.rs>
  - <https://raw.githubusercontent.com/daac-tools/vibrato/HEAD/vibrato/src/tokenizer.rs>
  - <https://raw.githubusercontent.com/daac-tools/vibrato/HEAD/vibrato/src/tokenizer/lattice.rs>
  - <https://raw.githubusercontent.com/daac-tools/vibrato/HEAD/vibrato/src/tokenizer/worker.rs>
  - <https://raw.githubusercontent.com/daac-tools/vibrato/HEAD/vibrato/src/dictionary.rs>
  - <https://raw.githubusercontent.com/daac-tools/vibrato/HEAD/vibrato/src/dictionary/connector.rs>
  - <https://raw.githubusercontent.com/daac-tools/vibrato/HEAD/vibrato/src/dictionary/connector/matrix_connector.rs>
  - <https://raw.githubusercontent.com/daac-tools/vibrato/HEAD/vibrato/src/dictionary/mapper.rs>
  - <https://raw.githubusercontent.com/daac-tools/vibrato/HEAD/vibrato/src/common.rs>
  - <https://raw.githubusercontent.com/daac-tools/vibrato/HEAD/docs/README.md>
  - <https://raw.githubusercontent.com/daac-tools/vibrato/HEAD/docs/map.md>
  - <https://raw.githubusercontent.com/daac-tools/vibrato/HEAD/docs/benchmark.md>
  - <https://raw.githubusercontent.com/daac-tools/vibrato/HEAD/map/src/main.rs>
  - <https://raw.githubusercontent.com/daac-tools/vibrato/HEAD/benchmark/src/main.rs>
  - <https://raw.githubusercontent.com/wiki/daac-tools/vibrato/Speed-Comparison.md>
  - <https://github.com/daac-tools/vibrato/commits>
  - <https://github.com/daac-tools/vibrato/releases>
  - <https://github.com/daac-tools/vibrato/releases/tag/v0.4.0>
  - <https://github.com/daac-tools/vibrato/releases/tag/v0.5.0>
  - <https://github.com/daac-tools/vibrato/issues?q=is%3Aissue>
  - <https://github.com/daac-tools/vibrato/issues/150>
  - <https://github.com/daac-tools/vibrato/issues/148>
  - <https://github.com/daac-tools/vibrato/issues/96>
  - <https://crates.io/api/v1/crates/vibrato>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/vibrato-0.5.0-benchmark/README.md>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/vibrato-0.5.0-benchmark/compile_all.sh>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/vibrato-0.5.0-benchmark/run_all.sh>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/vibrato-0.5.0-benchmark/download_resources.sh>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/vibrato-0.5.0-benchmark/stats.py>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/vibrato-0.5.0-benchmark/bench/mecab-ipadic-2_7_0-bench/main.cc>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/vibrato-0.5.0-benchmark/bench/mecab-unidic-3_1_1-bench/main.cc>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/vibrato-0.5.0-benchmark/bench/vibrato-bench/src/main.rs>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/vibrato-0.5.0-benchmark/bench/vibrato-bench/Cargo.toml>
  - <https://raw.githubusercontent.com/legalforce-research/tokenizer-speed-bench/vibrato-0.5.0-benchmark/resources/wagahaiwa_nekodearu.txt>
  - https://www.anlp.jp/proceedings/annual_meeting/2023/pdf_dir/C2-4.pdf (unreachable, ENOTFOUND; abstract via WebSearch snippet)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/daac-tools/vibrato`) · [data/wave14/enrich/raw/github_com_daac_tools_vibrato.json](../../../data/wave14/enrich/raw/github_com_daac_tools_vibrato.json) (enrichment confidence 0.8)

</details>
