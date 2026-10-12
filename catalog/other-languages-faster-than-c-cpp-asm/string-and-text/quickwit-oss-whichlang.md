# Whichlang (Rust language detection)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `MIT` · 🟢 active

> Dependency-free Rust language detector for 16 languages; about 5x faster than Google's CLD2 (C++) per sentence in Lingua's benchmark.

| | |
|---|---|
| **Beats** | CLD2 (Google Compact Language Detector 2, C++), called through the deprecated cld2 1.0.2 crate (emk/rust-cld2), whose cld2-sys build.rs compiles the bundled CLD2 sources plus a thin C++ wrapper with the gcc crate and -std=c++03; the Rust side calls CLD2_ExtDetectLanguageSummary4 over FFI. Whatlang (Rust) and Lingua (Rust) are also compared. |
| **Claimed result** | Lingua README 'How fast is it?': Whichlang 4.47 ms vs CLD 2 23.92 ms single thread (about 5.4x, derived from page data) and 651.89 us vs 4.81 ms multi thread (about 7.4x, derived from page data); accuracy-reporter run time Whichlang 0.28 s vs CLD 2 1.70 s (about 6.1x, derived from page data; this row includes harness overhead, see caveats). Whichlang's own README compares only with Whatlang (about 10x faster; 0.26 us vs 16.62 us short text, 5.21 us vs 62.00 us long text) and claims above 100 MB/s (105.69 and 112.31 MiB/s). |
| **Workload** | Lingua benches/benchmark.rs (Criterion): 16 sentences, one per language in the common 16-language set, repeated 125 times, giving 2,000 detections per iteration, single thread and rayon multi-thread. Second table: the accuracy_reports binary classifying 3,000 texts (1,000 single words, 1,000 word pairs, 1,000 sentences) for each of Lingua's 75 languages, timed together with statistics collection and report-file writing. |
| **Metric** | throughput |
| **Hardware** | iMac 3.6 GHz 8-core Intel Core i9 with 40 GB RAM (stated for the Lingua README table) |
| **Compiler and flags** | Not stated on the page. 'cargo bench --features benchmark' implies the bench profile (rustc opt-level 3); the gcc crate used by cld2-sys passes cargo's OPT_LEVEL to the C++ compiler, so CLD2 was presumably built at -O3 with -std=c++03 (inferred from cld2-sys/build.rs, not stated). rustc and C++ compiler versions are not given. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | Whichlang README: a small multiclass logistic regression over hashed 2-4-gram letter and codepoint features projected into a 4,096-dimension space (the hashing trick), with no dependencies. Whatlang's comparison table lists CLD2 as quadgram based; the link between model size and speed is this agent's inference. |
| **Adoption** | 461 stars; about 469,000 crates.io downloads (latest 0.1.1, 2025-01-21); used by Quickwit |
| **Last commit** | 2026-03-30 |
| **Links** | [repository](https://github.com/quickwit-oss/whichlang) · [benchmark](https://github.com/pemistahl/lingua-rs) |

## Verdict

In Lingua's Criterion benchmark (2,000 detections of 16 one-per-language sentences, iMac 3.6 GHz 8-core Core i9, compiler versions not stated), whichlang 0.1.1 took 4.47 ms vs 23.92 ms for CLD2 called through the cld2 1.0.2 crate's FFI (about 5.4x) on one thread and 651.89 us vs 4.81 ms with rayon (about 7.4x). This is a smaller 16-language model beating a larger 80-plus-language C++ detector, not like-for-like work, and the numbers were measured by Lingua's author, independent of both projects.

## Use it when

- Routing or tagging high volumes of text known to be in one of the 16 supported languages, for example choosing a tokenizer or stemmer per document in a search indexer (it was written for Quickwit).
- Short and medium strings where throughput matters: its own Criterion benchmark reports 0.26 us for a 29-byte English sentence and 5.21 us for a long paragraph (about 106 to 112 MiB/s), and Lingua's benchmark puts it at about 2.2 us per sentence vs about 12 us for CLD2 (derived from page data).
- Builds that cannot take a C++ toolchain or FFI: pure safe Rust with no runtime dependencies, so it compiles for any Rust target, including WebAssembly (inferred from the code; no target list is published).
- Multi-threaded batch jobs: the function is stateless, and Lingua's rayon run scaled to 651.89 us for 2,000 sentences on 8 cores vs 4.81 ms for CLD2.

## Skip it when

- Text that may be in any language outside the 16: there is no 'unknown' outcome, so Polish, Ukrainian or Indonesian input is silently labelled as the nearest supported language (issues #12 'support all whatlang languages' and #16 'return Option&lt;Lang&gt;' are open).
- When you need a confidence score or reliability flag to reject low-quality guesses: none exists (issue #24, open since 2025-08-26); CLD2 and Whatlang both return one.
- Very short inputs and closely related languages: on the whatlang-accuracy-benchmark it averages 92.10% for texts of 20 characters or fewer (Spanish 76.36%, German 80.00%, Portuguese 83.87%), against 99.39% above 100 characters; the 99.5% README figure is on the author's unpublished validation set (issue #8 asks for the data).
- HTML or mixed-markup input, language hints (TLD, Content-Language) or per-span language percentages: CLD2 has these and Whichlang does not.
- Workloads that need retraining or new languages without Python: weights.rs is generated by the train.ipynb notebook from a dataset that is not published.

## How it is fast

Detection is one pass of a hashed linear model: each ASCII character emits lowercased 2-, 3- and 4-gram features packed into a u32, each non-ASCII character emits a codepoint/128 feature and a script-class feature, each feature is hashed with MurmurHash2 into one of 4,096 buckets (the hashing trick), and the bucket's 16 f32 weights (one 64-byte row) are added to a 16-entry score array. A 1/sqrt(n) scale, per-language intercepts and an argmax finish the multiclass logistic regression. The model is a 65,536-float (256 KiB) constant table compiled into the binary, so there is no allocation, no model loading and no per-language table walk; CLD2 scores far more languages with larger n-gram tables (the link between model size and speed is inference).

## Compared with alternatives

No other language-identification library is catalogued in string-and-text; the nearest siblings (Vaporetto, Vibrato, jieba-rs) segment text in a known language, so Whichlang is the step before them when a pipeline must first decide which tokenizer to run.

## Integration

| | |
|---|---|
| **Form** | crate (whichlang 0.1.1 on crates.io) |
| **Dependencies** | none (criterion only as a dev-dependency) |
| **Minimum toolchain** | Rust edition 2021 (rustc 1.56+); no rust-version declared |
| **Platforms** | any Rust target; pure safe Rust with no SIMD intrinsics, unsafe blocks or platform code |
| **Thread safety** | detect_language is a pure function over constant tables and can be called from any number of threads concurrently. |
| **Drop-in for the baseline** | partial — replaces CLD2's top-language call only for the 16 shared languages; no reliability flag, percentages, hints, HTML mode or unknown-language result |

## Gotchas

- Input that yields no features (an empty string) returns Lang::Eng rather than an error; version 0.1.0 panicked on an empty string (fixed in 0.1.1, October 2024), so pin 0.1.1.
- Only ASCII letters are lowercased and turned into n-grams; accented Latin letters contribute only their codepoint/128 bucket and a class from a fixed list of about 40 codepoints, so languages that differ mainly in accented letters lean on that coarse signal, and the default fallback language is English.
- Benchmark caveats behind the CLD2 numbers: the Criterion input is 16 distinct sentences repeated 125 times (cache-resident), CLD2 scores all of its languages while Whichlang knows 16, and the 0.28 s vs 1.70 s accuracy-reporter row also times report writing and a CLD2 adapter that converts every result by iterating up to 75 Lingua languages and allocating an ISO-code String per candidate.
- The baseline binding is weak in its own right: the cld2 1.0.2 crate is marked deprecated, compiles the bundled CLD2 sources with -std=c++03 through the old gcc 0.3 build crate, and its to_c_str_or_null() returns the pointer of a CString that is dropped inside the map closure, a dangling pointer whenever a TLD or Content-Language hint is passed (not exercised by the benchmark, which uses default hints).

## Known shortcomings

- Library win, not a language win: Lingua author's Criterion benchmark (benches/benchmark.rs) pits Whichlang's 16-language model against CLD2 scoring all its languages through the deprecated cld2 1.0.2 FFI crate (its -O3 build inferred from source); input is 16 sentences repeated 125 times, and the 0.28 s vs 1.70 s row includes report writing plus a String allocation in Lingua's CLD2 adapter.
- No harness bug in the Lingua Criterion bench; caveats confirmed (16 repeated sentences; the CLD2 adapter allocates per candidate in the accuracy reporter). The baseline cld2 1.0.2 crate's to_c_str_or_null returns a dangling CString pointer when hints are passed (the benchmark uses default hints, so the numbers are unaffected). The current Quickwit Cargo.lock no longer lists whichlang, so 'used by Quickwit' is historical. No unknown-language result and no confidence score (issues #16, #24 open); 92.10% accuracy at 20 characters or fewer.

## Caveats and trade-offs

The CLD2 comparison is in a competitor's README (Lingua), not in Whichlang's own. The Criterion input is only 16 distinct sentences repeated 125 times (tiny, cache-resident working set). CLD2 considers all of its languages while Whichlang knows only 16, so the two do different amounts of work; the single-thread table is a Whichlang-versus-CLD2 library result, not a Rust-versus-C++ one (Whatlang, also Rust, is slower than CLD2 single-threaded at 36.24 ms). The 0.28 s vs 1.70 s accuracy-reporter row times statistics collection and report writing too, and Lingua's CLD2 adapter maps each result by iterating all Lingua languages and allocating an ISO-code String per candidate, which penalises the CLD2 row. CLD2 build flags (-O3) are inferred from the gcc crate, not stated; the cld2 binding crate is deprecated and bundles CLD2 sources from about 2015. Whichlang supports only 16 languages; Lingua reports it is less accurate than Lingua on that common set. [retier] The cld2 1.0.2 crate's to_c_str_or_null returns a dangling CString pointer when hints are passed (the benchmark uses default hints, so the numbers are unaffected). The current Quickwit Cargo.lock no longer lists whichlang. No unknown-language result and no confidence score (issues #16, #24 open); 92.10% accuracy at 20 characters or fewer.

Supports only 16 languages (CLD2 supports about 83 per the Whatlang README table); the author reports 99.5% accuracy on a private validation set, and accuracy is lower for short inputs. No HTML handling.

## Maintenance

MIT-licensed and small, but the model has not changed since the October 2024 empty-string fix (2026 commits are CI and dependency bumps); 461 stars, about 470,000 crates.io downloads (157,751 recent) and 11 reverse dependencies including lingua as an optional benchmark dependency, while the current Quickwit Cargo.lock no longer lists it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now B.
- **Tier reason:** Independent third-party measurement: the Lingua README 'How fast is it?' table (Whichlang 4.47 ms vs CLD 2 23.92 ms single thread, 651.89 us vs 4.81 ms multi thread) was produced by the Lingua author, not the Whichlang or CLD2 authors, with a public Criterion harness (benches/benchmark.rs) on a stated iMac 3.6 GHz 8-core Core i9. Not A because neither the rustc version nor the C++ compiler used for CLD2 is stated and the CPU is described rather than named; upgraded from C on the independence of the measurement.
- **Verifier notes:** Numbers match the Lingua README exactly; the C++ baseline really is CLD2 compiled from source through the cld2 crate's FFI wrapper, presumably at -O3. Record as a Whichlang library win over CLD2 (different model, fewer languages), not a language-level win; harness shortcomings: 16 repeated sentences, CLD2 scores all its languages, and the accuracy-reporter timing includes report writing and an allocation-heavy CLD2 language mapping. Tier raised from C to B because the measurement is independent of both projects.
- **Fields the verifier corrected:** `baseline`, `workload`, `compiler_and_flags`, `claimed_speedup`, `caveats`, `stars_or_usage`
- **Shortcomings recorded by:** verifier batch-38 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/pemistahl/lingua-rs>
  - <https://raw.githubusercontent.com/pemistahl/lingua-rs/HEAD/README.md>
  - <https://github.com/pemistahl/lingua-rs/tree/main/benches>
  - <https://raw.githubusercontent.com/pemistahl/lingua-rs/HEAD/benches/benchmark.rs>
  - <https://raw.githubusercontent.com/pemistahl/lingua-rs/HEAD/Cargo.toml>
  - <https://github.com/pemistahl/lingua-rs/tree/main/src/bin>
  - <https://github.com/pemistahl/lingua-rs/tree/main/src/bin/accuracy_reports>
  - <https://raw.githubusercontent.com/pemistahl/lingua-rs/HEAD/src/bin/accuracy_reports/main.rs>
  - <https://raw.githubusercontent.com/pemistahl/lingua-rs/HEAD/src/bin/accuracy_reports/cld2.rs>
  - <https://raw.githubusercontent.com/pemistahl/lingua-rs/HEAD/src/bin/accuracy_reports/whichlang.rs>
  - <https://raw.githubusercontent.com/pemistahl/lingua-rs/HEAD/src/bin/accuracy_reports/language_detection.rs>
  - <https://github.com/emk/rust-cld2>
  - <https://raw.githubusercontent.com/emk/rust-cld2/HEAD/cld2-sys/build.rs>
  - <https://raw.githubusercontent.com/emk/rust-cld2/HEAD/cld2-sys/Cargo.toml>
  - <https://raw.githubusercontent.com/emk/rust-cld2/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/emk/rust-cld2/HEAD/src/detection.rs>
  - <https://raw.githubusercontent.com/emk/rust-cld2/HEAD/cld2-sys/src/wrapper.cpp>
  - <https://github.com/quickwit-oss/whichlang>
  - <https://github.com/quickwit-oss/whichlang/commits>
  - <https://raw.githubusercontent.com/quickwit-oss/whichlang/HEAD/README.md>
  - <https://crates.io/api/v1/crates/whichlang>
- **Sources the enricher read:**
  - <https://github.com/quickwit-oss/whichlang>
  - <https://github.com/quickwit-oss/whichlang/commits/main>
  - <https://github.com/quickwit-oss/whichlang/issues?q=is%3Aissue>
  - <https://github.com/quickwit-oss/whichlang/issues/24>
  - <https://raw.githubusercontent.com/quickwit-oss/whichlang/HEAD/README.md>
  - <https://raw.githubusercontent.com/quickwit-oss/whichlang/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/quickwit-oss/whichlang/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/quickwit-oss/whichlang/HEAD/src/weights.rs>
  - <https://raw.githubusercontent.com/quickwit-oss/whichlang/HEAD/benches/bench.rs>
  - <https://crates.io/api/v1/crates/whichlang>
  - <https://crates.io/api/v1/crates/whichlang/reverse_dependencies?per_page=50>
  - <https://raw.githubusercontent.com/pemistahl/lingua-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/pemistahl/lingua-rs/HEAD/benches/benchmark.rs>
  - <https://raw.githubusercontent.com/pemistahl/lingua-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/pemistahl/lingua-rs/HEAD/src/bin/accuracy_reports/cld2.rs>
  - <https://raw.githubusercontent.com/pemistahl/lingua-rs/HEAD/src/bin/accuracy_reports/whichlang.rs>
  - <https://raw.githubusercontent.com/pemistahl/lingua-rs/HEAD/src/bin/accuracy_reports/main.rs>
  - <https://raw.githubusercontent.com/emk/rust-cld2/HEAD/README.md>
  - <https://raw.githubusercontent.com/emk/rust-cld2/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/emk/rust-cld2/HEAD/src/detection.rs>
  - <https://raw.githubusercontent.com/emk/rust-cld2/HEAD/cld2-sys/build.rs>
  - <https://raw.githubusercontent.com/emk/rust-cld2/HEAD/cld2-sys/Cargo.toml>
  - <https://raw.githubusercontent.com/emk/rust-cld2/HEAD/cld2-sys/src/wrapper.cpp>
  - <https://github.com/emk/rust-cld2/tree/master/cld2-sys/cld2/internal>
  - <https://raw.githubusercontent.com/quickwit-oss/quickwit/HEAD/quickwit/Cargo.toml>
  - <https://raw.githubusercontent.com/quickwit-oss/quickwit/HEAD/quickwit/quickwit-query/Cargo.toml>
  - <https://raw.githubusercontent.com/quickwit-oss/quickwit/HEAD/quickwit/Cargo.lock>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/quickwit-oss/whichlang`) · [data/wave14/enrich/raw/github_com_quickwit_oss_whichlang.json](../../../data/wave14/enrich/raw/github_com_quickwit_oss_whichlang.json) (enrichment confidence 0.75)

</details>
