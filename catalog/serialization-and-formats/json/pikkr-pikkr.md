# pikkr

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🔴 abandoned

> Rust implementation of the Mison speculative JSON field extractor; pulls named fields 2-4x faster than serde_json in its benchmark.

| | |
|---|---|
| **Beats** | serde_json |
| **Claimed result** | 1 field (\$._id.\$oid): pikkr 954.1471 MB/s (basic parsing only) and 1424.6397 MB/s (speculative, train_num=100) vs serde_json 452.4017 MB/s (\~2.1x / \~3.1x); 16 fields: pikkr 815.7086 MB/s (basic) and 966.4520 MB/s (speculative) vs serde_json 231.7726 MB/s (\~3.5x / \~4.2x). MB/s values verbatim from benchmark README output; ratios derived from page data. |
| **Workload** | Extract 1, 2, 4, 8, and 16 named fields (via JSONPath-like queries, e.g. \$._id.\$oid) from a 1GB generated JSON file (repeated 'companies.json' startup-company dataset) using AVX2-accelerated speculative parsing, compared against serde_json and the `json` crate. |
| **Metric** | throughput |
| **Hardware** | MacBook Pro, Intel Core i7 3.3 GHz, 1 processor / 2 cores, 256 KB L2 per core, 4 MB L3, 16 GB RAM (exact CPU model not stated) |
| **Compiler and flags** | rustc 1.22.0-nightly (d93036a04 2017-09-07), cargo 0.23.0-nightly (34c0674a2 2017-09-01) per pikkr README; bench.sh builds with RUSTFLAGS="-C target-cpu=native" cargo build --release; serde_json 1.0.3, json 0.11.9, pikkr 0.16.0 (Cargo.lock) |
| **Adoption** | 641 stars |
| **Last commit** | 2017-09-21 |
| **Links** | [repository](https://github.com/pikkr/pikkr) · [benchmark](https://github.com/pikkr/rust-json-parser-benchmark) |

## Verdict

The first-party rust-json-parser-benchmark reads a \~1.09 GB file (companies.json repeated 14 times; 263,214 lines averaging 4,160 bytes) line by line and times extraction of 1-16 paths per record. At 1 field, pikkr 0.16.0 reached 954 'mb/sec' untrained and 1,425 after 100 training records, vs 452 for serde_json 1.0.3; at 16 fields it reached 816 and 966 vs 232. The build used rustc 1.22.0-nightly (2017-09-07) with -C target-cpu=native on a 2-core 3.3 GHz Intel Core i7 MacBook Pro. Inside the timed region, the serde_json target (a DeserializeSeed that skips unwanted keys with IgnoredAny) builds a serde_json::Value for each hit and re-serializes it with to_string(), while pikkr returns borrowed slices. The 'mb/sec' figure uses 1024\*1024 divisors, so it is really MiB/s.

## Use it when

- Large NDJSON or record-per-line scans (logs, event exports, analytics dumps) where you need a few fields from each record of a few KB and the records share one or a few layouts.
- Projection or filter pushdown where raw JSON text is enough and you convert only the fields you keep, e.g. comparing an ID slice or passing a sub-object through verbatim.
- Throughput-bound batch jobs on x86-64 CPUs with AVX2 where you can pin an old nightly toolchain or vendor and port the code.
- As a small, readable Rust reference for Mison's leveled colon bitmaps and pattern-learning speculation, to port or vendor into your own code.

## Skip it when

- You need validation. Invalid JSON is accepted and stray bytes can end up in values: open issue #9 shows `{"x":0,}` returning `0,`.
- You need fields inside arrays, array indexing, or wildcards. Queries support only `$.a.b` object paths, and a path through an array returns a wrong slice (open issue #72 gets `true}]`).
- Records vary in layout or queried fields are often missing. Each speculation miss falls back to basic parsing, and position statistics are learned only during the training window, so layout drift after training keeps hitting the slow path.
- You need a current toolchain. The published 0.16.0 depends on x86intrin, which uses nightly-only features. Issue #76 (2024) reports it does not build on Rust 1.80.0, and docs.rs failed to build it.
- You need typed deserialization, serialization, or a DOM: this crate does not provide them.

## How it is fast

It implements Mison (Li et al., VLDB 2017). SIMD byte compares (AVX2 through the x86intrin crate in the published crate) build bitmaps of backslashes, quotes, colons and braces. Bit tricks then turn those into a string mask and per-depth 'leveled colon bitmaps', a structural index that lets the parser hop between the colons at one nesting level and skip everything else. For the first train_num records ('basic parsing') it records which colon position each queried field sat at. After that, 'speculative parsing' checks only those positions and falls back to basic parsing on a miss. Values come back as slices, so nothing is allocated or unescaped per value.

## Compared with alternatives

For Rust, simd-json and sonic-rs are maintained and beat serde_json on full parsing, and sonic-rs builds on stable Rust with a `get` by pointer path that returns a raw LazyValue and handles array indices. Pick pikkr over them only to study or port Mison-style trained speculative skipping over many uniform records. In C++, the Mison paper entry and its structural-index successors Pison and JSONSki are the better starting points.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | fnv; x86intrin 0.4.x (always required in the published 0.16.0; optional behind the `avx-accel` feature on the unpublished git master) |
| **Minimum toolchain** | Rust nightly for crates.io 0.16.0 (README pins rustc 1.22.0-nightly 2017-09-07). Issue #76 reports it fails on 1.80.0. The unpublished master's CI targeted stable, beta and nightly in 2017 without avx-accel, but this is not verified on current rustc. |
| **Platforms** | x86-64 with AVX2 for the published 0.16.0, built with RUSTFLAGS="-C target-cpu=native". Git master adds a portable scalar SWAR emulation of the AVX2 ops when `avx-accel` is off; that path is not benchmarked. |
| **Thread safety** | Not documented. `parse` takes `&mut self`, and the parser holds a RefCell plus its learned stats, so use one instance per thread; each instance trains separately. |
| **Drop-in for the baseline** | false — a different API: path strings go in and raw byte slices come out. There are no serde traits and no typed or Value results. |

## Gotchas

- Results are raw JSON text. Strings include their quotes and escape sequences, and objects and arrays come back verbatim, so you still have to parse and unescape what you keep.
- Keys are matched as raw bytes, and queries are split on '.'. You cannot query keys that contain a dot, and an escaped key in the data will not match its unescaped query.
- One call handles exactly one JSON record, so you split the stream yourself; the benchmark splits on newlines with BufReader::lines.
- crates.io 0.16.0 (2017-09-10) is older than the master branch. The AVX2-free fallback (PR #65, 2017-09-12) was never published. Cargo metadata says MIT/Apache-2.0, while the repo LICENSE and GitHub say MIT.

## Known shortcomings

- Dormant since 2017; open issue #76 says it does not build on Rust 1.80. Issue #9 shows it accepts invalid JSON such as {"x":0,} and returns "0,". Speculative parsing only pays off on repeated same-shape records.
- First-party benchmark favours pikkr: the serde_json side builds a Value per hit and re-serializes it inside the timed region, while pikkr returns borrowed unvalidated slices. The published 0.16.0 needs nightly (x86intrin); master's portable fallback was never released or benchmarked. Querying through arrays returns wrong slices (#72); only \$.a.b object paths.

## Caveats and trade-offs

Abandoned since 2017-09-21 (no commits in \~9 years); requires nightly Rust and an AVX2 CPU, and the 2017 nightly code may not build with current rustc. First-party benchmark on a single dataset (companies.json concatenated 14x, \~1.09 GB, 263,214 records) whose uniform record structure suits pikkr's Mison-style speculative parsing; the peak numbers need training (train_num=100). The serde_json side is a hand-written DeserializeSeed query extractor that skips unneeded values with IgnoredAny, against serde_json 1.0.3 (2017); current serde_json was not tested. No exact CPU model is given.

Not a general-purpose DOM parser: implements the Mison 'speculative parsing' algorithm which only extracts a fixed, known set of field paths from records with a stable/repetitive structure, falling back to slow-path parsing when the structure varies; requires Rust nightly and an AVX2 CPU.

## Maintenance

Abandoned since 2017-09-21: the last crates.io release was 0.16.0 on 2017-09-10, docs.rs failed to build it, and it has no crates.io reverse dependencies. It is MIT-licensed and small enough to vendor, but expect to port the x86intrin AVX2 path to std::arch (issue #71 already pointed to stdsimd) before it builds on a modern toolchain.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification A, tier now C.
- **Tier reason:** The pikkr/rust-json-parser-benchmark README output (code in src/targets/{serde_json,pikkr,json}.rs, run by bench.sh with RUSTFLAGS="-C target-cpu=native" cargo build --release) shows pikkr 954.1471 / 1424.6397 MB/s vs serde_json 452.4017 MB/s for 1 field, and rustc/cargo nightly versions are in the pikkr README. The hardware is given only as 'MacBook Pro, Intel Core i7, 3.3 GHz, 2 cores' with no CPU model, so it is not A; the benchmark is first-party (same org), so C.
- **Verifier notes:** All MB/s figures match the benchmark README output and the pikkr README chart; the record's 'RUSTFLAGS default' was wrong (bench.sh sets -C target-cpu=native). Downgraded A to C only because the CPU is named as a generic 'Intel Core i7 3.3 GHz' and the benchmark is first-party; metadata (MIT, 641 stars, last commit 2017-09-21, not archived, not a fork) checks out.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/pikkr/rust-json-parser-benchmark>
  - <https://github.com/pikkr/rust-json-parser-benchmark/blob/master/bench.sh>
  - <https://github.com/pikkr/rust-json-parser-benchmark/blob/master/Cargo.toml>
  - <https://github.com/pikkr/rust-json-parser-benchmark/blob/master/Cargo.lock>
  - <https://github.com/pikkr/rust-json-parser-benchmark/blob/master/src/targets/serde_json.rs>
  - <https://github.com/pikkr/rust-json-parser-benchmark/blob/master/src/targets/pikkr.rs>
  - <https://github.com/pikkr/pikkr>
  - <https://raw.githubusercontent.com/pikkr/pikkr/master/img/benchmark.png>
- **Sources the enricher read:**
  - <https://github.com/pikkr/pikkr>
  - <https://github.com/pikkr/pikkr/blob/master/README.md>
  - <https://github.com/pikkr/pikkr/blob/master/Cargo.toml>
  - <https://github.com/pikkr/pikkr/blob/master/src/lib.rs>
  - <https://github.com/pikkr/pikkr/blob/master/src/avx.rs>
  - <https://github.com/pikkr/pikkr/blob/master/src/emulated.rs>
  - <https://github.com/pikkr/pikkr/blob/master/src/pikkr.rs>
  - <https://github.com/pikkr/pikkr/blob/master/src/error.rs>
  - <https://github.com/pikkr/pikkr/blob/master/src/index_builder.rs>
  - <https://github.com/pikkr/pikkr/blob/master/src/parser.rs>
  - <https://github.com/pikkr/pikkr/blob/master/src/query.rs>
  - <https://github.com/pikkr/pikkr/blob/master/src/utf8.rs>
  - <https://github.com/pikkr/pikkr/blob/master/src/result.rs>
  - <https://github.com/pikkr/pikkr/blob/master/tests/issues.rs>
  - <https://github.com/pikkr/pikkr/blob/master/.travis.yml>
  - <https://github.com/pikkr/pikkr/blob/master/.travis/travis.sh>
  - <https://github.com/pikkr/pikkr/commits/master>
  - <https://github.com/pikkr/pikkr/issues>
  - <https://github.com/pikkr/pikkr/issues/1>
  - <https://github.com/pikkr/pikkr/issues/5>
  - <https://github.com/pikkr/pikkr/issues/6>
  - <https://github.com/pikkr/pikkr/issues/7>
  - <https://github.com/pikkr/pikkr/issues/9>
  - <https://github.com/pikkr/pikkr/issues/14>
  - <https://github.com/pikkr/pikkr/issues/71>
  - <https://github.com/pikkr/pikkr/issues/72>
  - <https://github.com/pikkr/pikkr/issues/74>
  - <https://github.com/pikkr/pikkr/issues/75>
  - <https://github.com/pikkr/pikkr/issues/76>
  - <https://github.com/pikkr/rust-json-parser-benchmark>
  - <https://github.com/pikkr/rust-json-parser-benchmark/blob/master/bench.sh>
  - <https://github.com/pikkr/rust-json-parser-benchmark/blob/master/Cargo.toml>
  - <https://github.com/pikkr/rust-json-parser-benchmark/blob/master/src/main.rs>
  - <https://github.com/pikkr/rust-json-parser-benchmark/blob/master/src/executor.rs>
  - <https://github.com/pikkr/rust-json-parser-benchmark/blob/master/src/lib.rs>
  - <https://github.com/pikkr/rust-json-parser-benchmark/blob/master/src/targets/mod.rs>
  - <https://github.com/pikkr/rust-json-parser-benchmark/blob/master/src/targets/pikkr.rs>
  - <https://github.com/pikkr/rust-json-parser-benchmark/blob/master/src/targets/serde_json.rs>
  - <https://github.com/pikkr/rust-json-parser-benchmark/blob/master/src/targets/json.rs>
  - <https://crates.io/api/v1/crates/pikkr>
  - <https://crates.io/api/v1/crates/pikkr/reverse_dependencies>
  - <https://static.crates.io/crates/pikkr/pikkr-0.16.0.crate>
  - <https://crates.io/api/v1/crates/x86intrin>
  - <https://static.crates.io/crates/x86intrin/x86intrin-0.4.5.crate>
  - <https://docs.rs/crate/pikkr/0.16.0>
  - <https://pikkr.github.io/doc/pikkr/>
  - <https://github.com/cloudwego/sonic-rs>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/pikkr/pikkr`) · [data/wave4/enrich/raw/github_com_pikkr_pikkr.json](../../../data/wave4/enrich/raw/github_com_pikkr_pikkr.json) (enrichment confidence 0.8)

</details>
