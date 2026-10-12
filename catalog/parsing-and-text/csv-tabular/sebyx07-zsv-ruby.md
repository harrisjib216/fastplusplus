# zsv-ruby

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [CSV and tabular data](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Ruby` · `MIT` · 🟢 active

> Ruby native-extension binding to the zsv C library; drop-in CSV stdlib replacement, 5-6x faster.

| | |
|---|---|
| **Beats** | CSV (Ruby standard library CSV parser) |
| **Claimed result** | 6.20x faster (1K rows), 5.27x faster (10K rows), 5.00x faster (100K rows), 4.33x faster (10K rows with headers); also \~82.6% less memory and \~57% fewer string allocations |
| **Workload** | Parsing CSV files of 1K, 10K and 100K rows (5-10 cols) via Ruby native-extension bindings to the zsv C library, measured in iterations/second, vs Ruby's stdlib CSV class |
| **Metric** | throughput |
| **Adoption** | 17 stars |
| **Last commit** | 2026-07-30 |
| **Links** | [repository](https://github.com/sebyx07/zsv-ruby) · [benchmark](https://github.com/sebyx07/zsv-ruby#-performance) |

## Verdict

README benchmark-ips results (Ruby 3.4.7, no CPU/compiler stated) show ZSV beating stdlib CSV by 6.20x at 1K rows (1,013.7 vs 163.4 i/s), 5.27x at 10K rows, 5.00x at 100K rows, and 4.33x at 10K rows with headers enabled, plus 82.6% less memory and 56.9% fewer string allocations at 10K-100K rows.

## Use it when

- Ruby app already reading large CSVs with stdlib CSV and CPU time in parsing is a bottleneck
- Batch/ETL jobs on 10K-100K+ row files where throughput matters more than ecosystem maturity
- Simple, mostly-unquoted or lightly-quoted tabular data (the benchmarks use synthetic value_i_j fields, no heavy quoting)
- Linux or macOS (ARM or x86) environments where a C toolchain is available at gem-install time
- Willing to accept a single-author, low-adoption (17-star) dependency in exchange for the speedup

## Skip it when

- Need CSV stdlib's type/header converters (:numeric, :date, :date_time) or unconverted_fields -- explicitly marked 'not yet implemented' (Phase 2 roadmap item)
- Need CVS generation/writing -- only reading/parsing is implemented
- Windows without a working C build environment, since the gem compiles zsv from source at install time (no confirmed precompiled binary gems)
- Risk-averse production use: single maintainer, first release Dec 2025, only 17 stars, no independent (non-author) verification of the benchmark numbers
- Heavily-quoted or malformed/adversarial CSV, since only synthetic unquoted data was benchmarked and liberal_parsing edge cases aren't documented in depth

## How it is fast

The speed comes entirely from zsv's SIMD-accelerated scanning (SSE2/AVX2, per its build output) for delimiter/quote detection, plus a streaming pull-based parser that avoids buffering whole files. The Ruby layer adds a row builder (row.c) that converts parsed fields straight into Ruby arrays/hashes with frozen strings, cutting string allocations (\~57% fewer per the README) versus stdlib CSV's line-by-line Ruby-level splitting.

## Compared with alternatives

Pick this specifically when you're on Ruby and want zsv's speed without writing your own FFI bindings; for any other language, use liquidaty/zsv directly (same underlying engine, more mature, more battle-tested) or a language-native SIMD parser like simd-csv (Rust) or go-simdcsv (Go).

## Integration

| | |
|---|---|
| **Form** | module (native C extension gem) |
| **Dependencies** | none at runtime beyond a C toolchain; extconf.rb downloads and compiles liquidaty/zsv 1.4.3 source from GitHub during gem install |
| **Minimum toolchain** | Ruby &gt;= 3.3 (gemspec); README states tested on 3.3, 3.4, 4.0; C99 compiler (extconf uses -std=c99) |
| **Platforms** | Linux and macOS (ARM and x86) per README; extconf.rb has Darwin/Linux-specific link flags (-framework Foundation vs -lpthread -lm) and no Windows branch |
| **Thread safety** | Project's own docs/VERIFICATION.md claims 'Thread-safe (no global state)', but this is a self-generated report, not independently audited; no GVL-release calls (e.g. rb_thread_call_without_gvl) found in parser.c, so a parse call does not appear to release the GVL for concurrent Ruby threads |
| **Drop-in for the baseline** | partial -- matches CSV's read-path method names/options/exception classes, but has no writer and is missing CSV's converter/header-converter features |

## Gotchas

- Native extension: gem install compiles C code and fetches zsv 1.4.3 source over the network at install time, which can fail or be slow in sandboxed/offline CI
- No CSV writing support -- read-only replacement
- Type/header converters from stdlib CSV are unimplemented (explicit roadmap gap)
- Returned strings are frozen for efficiency, which can break code that mutates row values in place

## Known shortcomings

- A Ruby binding around zsv (github.com/liquidaty/zsv, also listed); its speed is zsv's, so prefer zsv directly outside Ruby.

## Caveats and trade-offs

No CPU model or compiler flags stated for the benchmark (only Ruby 3.4.7), so it cannot exceed Tier C, although the benchmark script is public (benchmark/parse_bench.rb, benchmark-ips; memory in benchmark/memory_bench.rb). Synthetic data only (value_i_j fields, no quoting). Extremely small/new project (17 stars, single author, README says it was built with Claude Code), so treat numbers as unverified by outside parties; the underlying speedup is really zsv's (liquidaty/zsv 1.4.3), wrapped for Ruby.

Thin Ruby wrapper around the C zsv library (see liquidaty/zsv entry in this same batch); inherits zsv's SIMD-dependent performance characteristics; very new and low-adoption gem, README states it was built with Claude Code

## Maintenance

Actively maintained (last commit 2026-07-30) and MIT-licensed, but very new (first release Dec 2025) and low-adoption (17 stars, single author); README discloses it was built with Claude Code, so treat it as an early-stage convenience wrapper around the more established liquidaty/zsv C library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** README Performance section shows benchmark-ips results vs Ruby stdlib CSV (163.4 vs 1,013.7 i/s = 6.20x; 5.27x; 5.00x; 4.33x) and the script is public (benchmark/parse_bench.rb), but only the Ruby version (3.4.7) is stated -- no CPU model, compiler or flags, so first-party Tier C.
- **Verifier notes:** All numbers match the README verbatim (string allocations are 56.9% fewer). Metadata checked: MIT, not a fork, 17 stars, last commit 2026-07-30. It is a Ruby binding of liquidaty/zsv (also a wave-3 known-list entry); the orchestrator may prefer to fold it under zsv rather than list it separately.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/sebyx07/zsv-ruby>
  - <https://github.com/sebyx07/zsv-ruby#-performance>
  - <https://github.com/sebyx07/zsv-ruby/blob/main/benchmark/parse_bench.rb>
- **Sources the enricher read:**
  - <https://github.com/sebyx07/zsv-ruby>
  - <https://github.com/sebyx07/zsv-ruby#-performance>
  - <https://github.com/sebyx07/zsv-ruby/blob/main/benchmark/parse_bench.rb>
  - <https://github.com/sebyx07/zsv-ruby/blob/main/README.md>
  - <https://github.com/sebyx07/zsv-ruby/blob/main/ext/zsv/extconf.rb>
  - <https://github.com/sebyx07/zsv-ruby/blob/main/zsv.gemspec>
  - <https://github.com/sebyx07/zsv-ruby/blob/main/CHANGELOG.md>
  - <https://github.com/sebyx07/zsv-ruby/blob/main/docs/VERIFICATION.md>
  - <https://github.com/sebyx07/zsv-ruby/blob/main/ext/zsv/parser.c>
  - <https://github.com/sebyx07/zsv-ruby/blob/main/lib/zsv/version.rb>
  - <https://github.com/sebyx07/zsv-ruby/issues>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/sebyx07/zsv-ruby`) · [data/wave3/enrich/raw/github_com_sebyx07_zsv_ruby.json](../../../data/wave3/enrich/raw/github_com_sebyx07_zsv_ruby.json) (enrichment confidence 0.5)

</details>
