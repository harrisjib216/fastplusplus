# YJIT (CRuby)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust (JIT) inside C (CRuby)` · `BSD-2-Clause OR Ruby` · 🟢 active

> CRuby's built-in Rust JIT; about 2x the CRuby interpreter on Rails-style apps after warmup on x86-64, 1.7x on Graviton4.

| | |
|---|---|
| **Beats** | CRuby 4.1.0dev bytecode interpreter (same commit, JIT off); the report also shows CRuby 3.4.7 and YJIT 3.4.7 |
| **Claimed result** | x86_64 (Xeon Platinum 8488C): geomean of the headline benchmarks, YJIT 4.1.0dev is 99.2% faster than CRuby 4.1.0dev and 9.5% faster than YJIT 3.4.7; railsbench 120.1% faster than the interpreter. Per-benchmark interpreter/YJIT time from the x86_64 CSV (derived from page data): activerecord 2.76x, liquid-render 2.89x, railsbench 2.20x, optcarrot 3.79x, lee 1.95x, binarytrees 2.31x, nbody 2.59x, fannkuchredux 4.04x, fib 6.58x, 30k_ifelse 7.62x, 30k_methods 11.84x; 78 of 79 benchmarks faster, knucleotide 0.98x. aarch64 (Graviton4): headline geomean 1.73x, railsbench 1.87x (derived from page data). |
| **Workload** | ruby-bench (commit 17dcac94) on Ruby master 11bb12ad3c, 2026-09-20: 16 headline benchmarks (activerecord, chunky-png, erubi-rails, hexapdf, liquid-c, liquid-compile, liquid-il, liquid-render, lobsters, mail, psych-load, railsbench, rubocop, ruby-lsp, sequel, shipit) plus about 60 other and micro benchmarks; 5 warmup iterations for the interpreter and 50 for YJIT before timing. |
| **Metric** | throughput |
| **Hardware** | x86_64: Intel Xeon Platinum 8488C; aarch64: AWS Graviton4 |
| **Compiler and flags** | gcc (Ubuntu 14.3.0-12ubuntu1\~24\~ppa1) 14.3.0; Ruby configured with --disable-install-doc --disable-install-rdoc --enable-yjit --enable-zjit (default optimization flags); YJIT enabled at run time with --yjit; rustc version not stated. |
| **Adoption** | Ships in CRuby (ruby/ruby 23.8k stars); the sibling ZJIT is in the same repository |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/ruby/ruby) · [benchmark](https://speed.ruby-lang.org/benchmarks/bench-2026-09-20-010747.html) |

## Verdict

On ruby-bench (commit 17dcac94) with Ruby master 11bb12ad3c built by gcc 14.3.0 (report of 2026-09-20), YJIT 4.1.0dev ran the 16 headline apps at a geomean 1.99x the CRuby 4.1.0dev interpreter on an Intel Xeon Platinum 8488C (from 1.52x on sequel to 2.89x on liquid-render; railsbench 2.20x) and 1.095x YJIT 3.4.7; on AWS Graviton4 the geomean was 1.73x (sequel 1.25x to liquid-render 2.59x; railsbench 1.87x), ratios recomputed from the per-benchmark CSVs. Times are means of post-warmup iterations (50 warmups for YJIT, 5 for the interpreter).

## Use it when

- Long-running CRuby servers (Rails, Liquid templating, Sequel/ActiveRecord apps) where workers serve many requests: the headline app suite gains 1.5x to 2.9x on x86-64 and 1.25x to 2.6x on Graviton4.
- CPU-bound pure-Ruby code with stable types (parsers, template engines, PNG encoding, numeric loops): micro and kernel benchmarks reach 2x to 12x.
- You must stay on CRuby for C extension and gem compatibility, and only need a run-time flag plus a Rust-enabled build.
- x86-64 or arm64 on Linux, macOS or BSD with memory headroom of roughly 10-80% over the interpreter.

## Skip it when

- Short-lived processes (CLI scripts, one-shot jobs, workers killed often): compilation and warmup can cost more than they return; the published numbers come after 50 warmup iterations.
- Memory-constrained deployments: on the x86-64 headline suite YJIT 4.1.0dev used 1.00x to 1.79x the interpreter's steady-state RSS (geomean about 1.19x; psych-load 30 to 54 MiB, rubocop 1.41x, railsbench 1.32x).
- Code that runs under TracePoint, binding, or redefines basic operators (+, &lt;, ==, nil semantics): YJIT deoptimises or invalidates compiled code (coverage tools and debuggers count).
- Windows or other architectures: YJIT supports only x86-64 and arm64 on macOS, Linux and BSD.
- Workloads that spend most time in C methods or that YJIT cannot compile: knucleotide (about 25-31% of instructions in YJIT) ran 0.98x on both platforms, and 30k_variables ran 0.80x (slower than the interpreter) on Graviton4.

## How it is fast

It uses lazy basic block versioning (BBV): blocks are compiled only when first reached, and each version is specialised on the types and object shapes seen so far, which removes repeated type checks without a separate type analysis. Polymorphic sites get chained guards (up to 8 object shapes for instance-variable reads and writes, smaller limits for aref and expandarray), and about 40 core C methods (Integer ops, is_a?, truthiness and others) have hand-written inline code generators instead of a C call. Code is split into inline and outlined (cold) regions, and methods are compiled only after a call threshold (30 calls, raised to 120 once a process has 40,000 ISEQs).

## Compared with alternatives

Pick YJIT over TruffleRuby when you need stock CRuby (C extensions, same GC and tooling, quick warmup, about 1.2x memory) rather than TruffleRuby's higher peak on Are We Fast Yet; prefer it over ZJIT, which ships in the same repository, until ZJIT is declared production-ready (Ruby 4.0 NEWS says ZJIT is not yet as fast as YJIT and advises against deploying it).

## Integration

| | |
|---|---|
| **Form** | module (built into the CRuby interpreter; enabled per process) |
| **Dependencies** | rustc at Ruby build time (YJIT and ZJIT declare no required crates); nothing at run time |
| **Minimum toolchain** | rustc 1.58.0+ for YJIT alone (yjit/Cargo.toml); rustc 1.85.0+ when ZJIT is built alongside (root Cargo.toml, edition 2024); GCC or Clang for CRuby, GCC recommended for release builds |
| **Platforms** | x86-64 and arm64/aarch64 on macOS, Linux and BSD; no Windows |
| **Thread safety** | Not documented separately in doc/jit/yjit.md; YJIT is internal to the VM, so Ruby programs need no changes. |
| **Drop-in for the baseline** | partial — the same ruby binary runs unchanged code with --yjit, but Ruby must have been built with --enable-yjit (check 'ruby --yjit -v' shows +YJIT), and TracePoint/binding-heavy code loses the speedup. |

## Gotchas

- Harness asymmetry, documented in the report: YJIT runs get 50 warmup iterations and the interpreter 5, and both are timed per iteration in-process (CLOCK_MONOTONIC) after warmup, so the ratios are steady-state throughput and say nothing about first-request latency; RSS is sampled between post-warmup iterations, not as a peak.
- The Graviton4 CSV shows two regressions the x86-64 summary hides: 30k_variables 0.80x and knucleotide 0.98x; on x86-64 only knucleotide (0.98x) is slower than the interpreter.
- When the executable-memory budget (--yjit-mem-size, default 128 MiB) fills, new code stays in the interpreter unless --yjit-code-gc is on; since Ruby 4.0, ratio_in_yjit in RubyVM::YJIT.runtime_stats works only in a --enable-yjit=stats build.
- Highly polymorphic sites exceed the guard-chain limits (8 shapes for ivars) and take side exits to the interpreter; --yjit-stats lists exit reasons to find them.

## Known shortcomings

- First-party Shopify run (speed.ruby-lang.org report 2026-09-20: 99.2% faster geomean than the CRuby 4.1.0dev interpreter, railsbench 120.1%, gcc 14.3.0, Xeon Platinum 8488C and Graviton4, ruby-bench pinned at 17dcac94) read through the rubybench/yjit-reports mirror; compared against CRuby's own interpreter, not PyPy, LuaJIT or V8, with extra memory use. C, not C++.
- Enricher: headline geomeans recomputed from the CSVs (x86 1.992x matching 99.2%, Graviton4 1.731x); the record missed aarch64 30k_variables at 0.80x (slower than the interpreter) besides knucleotide at 0.98x, headline memory is 1.00-1.79x the interpreter (geomean 1.19x, psych-load worst), and YJIT gets 50 warm-up iterations against the interpreter's 5, so the numbers are steady-state only.

## Caveats and trade-offs

Run by the YJIT team at Shopify (first-party), though code, Ruby commit, build config and CPU are all published and raw per-benchmark CSVs are in rubybench/yjit-reports. Speedups are after warmup (50 YJIT warmup iterations); first-iteration and memory costs differ: YJIT uses more memory than the interpreter on most headline benchmarks (memory chart on the same report). The large micro-benchmark ratios (30k_methods 11.8x, fib 6.6x) do not carry over to applications, where the headline geomean is about 2x on x86_64 and 1.7x on Graviton4. The repository is all of CRuby, so stars and license describe CRuby; YJIT is the yjit/ directory. The VMIL 2021 and MPLR 2023 papers were not opened (dl.acm.org blocked). speed.ruby-lang.org itself was blocked here; its numbers were read from the generated HTML and CSV in rubybench/yjit-reports (branch pages). [retier] Run by the YJIT team at Shopify (first-party) with code, Ruby commit, build config and CPU published and raw CSVs in rubybench/yjit-reports; geomeans recomputed: x86_64 1.992x (99.2%), Graviton4 1.731x. Steady-state only: YJIT gets 50 warm-up iterations against the interpreter's 5. Slower than the interpreter on aarch64 30k_variables (0.80x) and level on knucleotide (0.98x). Headline memory 1.00-1.79x the interpreter (geomean 1.19x, psych-load worst). Compared against CRuby's own interpreter, not PyPy, LuaJIT or V8. C, not C++.

Uses more memory than the interpreter (executable memory plus metadata); supported on x86-64 and arm64/aarch64 macOS, Linux and BSD; requires a Rust toolchain to build; warmup needed.

## Maintenance

Actively maintained by the YJIT team at Shopify inside ruby/ruby (last commit 2026-10-06) and the recommended production JIT in Ruby 4.0, BSD-2-Clause or Ruby licence; ZJIT, its intended successor in the same repository, is not yet recommended for production.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C: the speed.ruby-lang.org report of 2026-09-20 (source and CSV in github.com/rubybench/yjit-reports, pages branch) times YJIT 4.1.0dev against the CRuby 4.1.0dev interpreter at the same commit (11bb12ad3c) using the public ruby-bench suite pinned at commit 17dcac94 (benchmarks.yml, benchmarks/\*), and states the compiler (gcc 14.3.0), configure args and CPU models (Intel Xeon Platinum 8488C, AWS Graviton4).
- **Verifier notes:** The recorded benchmark_url (Shopify/yjit-bench, now ruby/ruby-bench) only carries an explicitly outdated example table whose numbers do match the record, so claimed_speedup and benchmark_url were replaced with the current speed.ruby-lang.org report; the 99.2% geomean was re-derived from the x86_64 CSV (1.99x). Metadata: ruby/ruby 23.8k stars, last commit 2026-10-06, license Ruby or BSD-2-Clause per COPYING (recorded value fine); ruby-bench is MIT.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `workload`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Shopify/yjit-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/ruby/ruby-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/ruby/ruby/HEAD/doc/jit/yjit.md>
  - <https://raw.githubusercontent.com/Shopify/yjit-metrics/HEAD/README.md>
  - <https://raw.githubusercontent.com/Shopify/yjit-metrics/HEAD/continuous_reporting/generate_and_upload_reports.rb>
  - <https://raw.githubusercontent.com/Shopify/yjit-metrics/HEAD/lib/yjit_metrics/continuous_reporting.rb>
  - <https://github.com/rubybench/yjit-reports>
  - <https://raw.githubusercontent.com/rubybench/yjit-reports/pages/index.html>
  - <https://raw.githubusercontent.com/rubybench/yjit-reports/pages/about.html>
  - <https://raw.githubusercontent.com/rubybench/yjit-reports/pages/CNAME>
  - <https://raw.githubusercontent.com/rubybench/yjit-reports/pages/benchmarks/bench-2026-09-20-010747.html>
  - <https://raw.githubusercontent.com/rubybench/yjit-reports/pages/reports/platform_details/blog_speed_details_2026-09-20-010747.x86_64.csv>
  - <https://raw.githubusercontent.com/rubybench/yjit-reports/pages/reports/platform_details/blog_speed_details_2026-09-20-010747.aarch64.csv>
  - <https://github.com/ruby/ruby>
  - <https://github.com/ruby/ruby/commits.atom>
  - <https://raw.githubusercontent.com/ruby/ruby/HEAD/COPYING>
  - <https://raw.githubusercontent.com/ruby/ruby-bench/HEAD/LICENSE.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ruby/ruby/HEAD/doc/jit/yjit.md>
  - <https://raw.githubusercontent.com/ruby/ruby/HEAD/yjit/Cargo.toml>
  - <https://raw.githubusercontent.com/ruby/ruby/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/ruby/ruby/HEAD/yjit/src/codegen.rs>
  - <https://raw.githubusercontent.com/ruby/ruby/HEAD/NEWS.md>
  - <https://raw.githubusercontent.com/ruby/ruby/HEAD/doc/NEWS/NEWS-4.0.0.md>
  - <https://raw.githubusercontent.com/rubybench/yjit-reports/pages/benchmarks/bench-2026-09-20-010747.html>
  - <https://raw.githubusercontent.com/rubybench/yjit-reports/pages/reports/platform_details/blog_speed_details_2026-09-20-010747.x86_64.csv>
  - <https://raw.githubusercontent.com/rubybench/yjit-reports/pages/reports/platform_details/blog_speed_details_2026-09-20-010747.aarch64.csv>
  - <https://raw.githubusercontent.com/rubybench/yjit-reports/pages/reports/platform_details/blog_memory_details_2026-09-20-010747.x86_64.csv>
  - <https://raw.githubusercontent.com/rubybench/yjit-reports/pages/about.html>
  - <https://github.com/rubybench/yjit-reports/tree/pages/reports>
  - <https://raw.githubusercontent.com/ruby/ruby-bench/HEAD/harness/harness.rb>
  - <https://raw.githubusercontent.com/ruby/ruby-bench/HEAD/harness/harness-common.rb>
  - <https://raw.githubusercontent.com/ruby/ruby-bench/HEAD/README.md>
  - WebSearch: ZJIT vs YJIT Ruby 4.1 2026 performance production status (snippets only)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/ruby/ruby`) · [data/wave12/enrich/raw/github_com_ruby_ruby.json](../../../data/wave12/enrich/raw/github_com_ruby_ruby.json) (enrichment confidence 0.8)

</details>
