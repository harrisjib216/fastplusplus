# pg_jitter

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C and C++` · `Apache-2.0` · 🟡 stale

> PostgreSQL JIT provider with sljit, AsmJit and MIR backends; compiles typical queries in 0.05-1 ms where llvmjit takes 20-60 ms.

| | |
|---|---|
| **Beats** | PostgreSQL LLVM JIT (llvmjit); also PostgreSQL's expression interpreter |
| **Claimed result** | Benchmark page (https://github.com/vladich/pg_jitter/blob/master/bench/ARM64/0.3.0/BENCHMARKS_v18.md): query time with JIT forced on, SUM_int no JIT 44.859 ms, llvmjit 68.090 ms, sljit 42.401 ms, asmjit 42.201 ms, mir 45.620 ms; GroupBy_5agg no JIT 117.367 ms, llvmjit 149.033 ms, sljit 99.530 ms, asmjit 98.079 ms, mir 125.102 ms. JIT compilation overhead (EXPLAIN JSON): SUM_int llvmjit 22.263 ms vs sljit 0.052 ms, asmjit 0.109 ms, mir 0.345 ms; GroupBy_5agg llvmjit 45.5 ms vs sljit 0.069 ms, asmjit 0.245 ms, mir 1.087 ms. README (https://github.com/vladich/pg_jitter): compile time 'tens to low hundreds of microseconds' (sljit) and 'hundreds of microseconds' (AsmJit) vs LLVM 'tens to hundreds of milliseconds'; sljit '5-25% faster than the interpreter'; average speedup over the interpreter TPC-C 8%, TPC-H 6%, ecommerce 14%, OLAP 42%, CRM \~400%. |
| **Workload** | PostgreSQL 18.1 queries on 1M-row tables (aggregation, joins, wide rows, text, numeric, jsonb), JIT thresholds set to 0, median of 3 timed runs after 2 warmups, parallel workers off. |
| **Metric** | compile-time and query throughput |
| **Hardware** | Apple M1 Pro, 32 GB RAM, Darwin 25.2.0 arm64 |
| **Compiler and flags** | PostgreSQL 18.1; pg_jitter CMakeLists.txt defaults CMAKE_BUILD_TYPE to Release; compiler, compiler version and PostgreSQL build flags not stated. |
| **Adoption** | 210 stars |
| **Last commit** | 2026-05-03 |
| **Links** | [repository](https://github.com/vladich/pg_jitter) · [benchmark](https://github.com/vladich/pg_jitter/blob/master/bench/ARM64/0.3.0/BENCHMARKS_v18.md) |

## Verdict

First-party run of pg_jitter 0.3.0 (dated 2026-03-24, two days before the v0.3.0 tag) against PostgreSQL 18.1's interpreter and llvmjit on an Apple M1 Pro (macOS, compiler and flags not stated), median of 3 EXPLAIN ANALYZE execution times per query: compile time mostly 0.04-0.12 ms for sljit (max 0.46 ms), 0.1-0.3 ms for AsmJit (max 2.8 ms) and 0.3-1.3 ms for MIR (16.9 ms on CASE_ts_range_30) vs 17-114 ms (mostly 20-60 ms) for llvmjit forced to full optimization and inlining, and 0.09-2.04 s on the 100-1000-column tables. Against the interpreter, most of the 108 queries land between 0.9x and 1.3x (LIKE_3wild as low as 0.77-0.81x), with 2-7x only on ILIKE/regex, CASE/IN rewrites, LIKE suffix and Interval_arith.

## Use it when

- Analytical or reporting queries in the 10 ms to seconds range where llvmjit's 20-60 ms compile cost (seconds on 100-1000-column tables) wipes out its gain, and you want JIT on with jit_above_cost around 200-2000.
- Queries dominated by ILIKE, regex, long CASE ladders or large integer IN lists: the PG18 page shows 2.5-4.9x over the interpreter on ILIKE/regex and 2-7x on CASE_eq/CASE_lt_50-100 because these are algorithmic rewrites, not just compiled code.
- Expression-heavy scans and joins on integer columns over wide-ish rows (10-300 columns), where the page shows roughly 1.1-1.3x over the interpreter.
- Teams that cannot or do not want to ship an LLVM build with PostgreSQL; the backends are small C/C++ libraries, and the sljit backend also builds and passes regression tests on Linux ppc64le and s390x.

## Skip it when

- OLTP point lookups and sub-5 ms queries: the README itself warns of up to about 1 ms of extra execution after JIT, and the PG18 page shows a fixed cost of about 2-2.4 ms even when nothing was compiled (COUNT_star 39.4 vs 37.0 ms, UNION_ALL_agg 97.5 vs 95.5 ms with no compile time recorded; derived from page data, probably per-connection provider loading).
- Workloads dominated by numeric, jsonb, array or plain text equality: the backends still call PostgreSQL's C functions and measured 0.90-1.03x of the interpreter there.
- Production systems that cannot tolerate wrong results: open issue #84 (2026-08-17, no reply) reports `SELECT (SELECT 0) > 0.1` returning true under pg_jitter_sljit on PG 17.9 while llvmjit is correct, and the README calls the code beta quality.
- When you want vendor support or a fast bug turnaround: one maintainer, no commits since 2026-05-03, and issues #82-#84 (ARM Linux build failure, MIR crash on Chinese text, the wrong-result bug) are unanswered.
- Platforms beyond the tested ones if you need AsmJit (arm64 and x86_64 only); x86_64 benchmark results are still marked TBD.

## How it is fast

Compile time: it generates machine code directly through lightweight code generators (sljit, AsmJit, MIR) instead of building LLVM IR, inlining PostgreSQL bitcode and running LLVM's optimizer, which is where llvmjit's tens of milliseconds go. Execution: hot functions are emitted inline (Tier 0) or called directly without fmgr/FunctionCallInfo (Tier 1), tuple deforming is specialised per TupleDesc with an L1I-size-derived switch from unrolled to loop form, and several rewrites change the algorithm rather than the code: monotonic CASE chains and integer IN lists become precompiled binary searches (CRC32C hash probing above 4096 elements), and LIKE/ILIKE/regex go to PCRE2 JIT and StringZilla SIMD search.

## Compared with alternatives

The sljit and AsmJit entries cite this same benchmark but are code-generator libraries you would have to build a lowering for; pick pg_jitter when the goal is simply faster JIT inside PostgreSQL (sljit backend for lowest compile time, AsmJit for deform-heavy rows), and look at TPDE or PochiVM-style copy-and-patch only if you are building your own query compiler.

## Integration

| | |
|---|---|
| **Form** | shared lib (PostgreSQL extension loaded through jit_provider; one .so/.dylib per backend plus a meta-provider) |
| **Dependencies** | PostgreSQL 14-18 server headers; sljit (author's patched fork vladich/sljit) and/or AsmJit and/or MIR (patched fork vladich/mir-patched) as sibling source directories; StringZilla headers (required); PCRE2 and yyjson (optional, on by default) |
| **Minimum toolchain** | CMake 3.16, C11 and C++17 compilers (C++20 under MSVC); Release build type by default |
| **Platforms** | Built and regression-tested on Linux and macOS arm64 (all backends), Linux, FreeBSD and Windows x86_64 (all backends), Linux ppc64le and s390x (sljit only); benchmarks published for Apple M1 Pro only |
| **Thread safety** | Not applicable in the usual sense: PostgreSQL backends are single-threaded processes; compiled code is per backend and freed with the query's ResourceOwner, and an experimental 'shared' parallel mode passes code to workers through DSM. |
| **Drop-in for the baseline** | partial — it is a drop-in jit_provider replacement for llvmjit with no SQL changes, but it only pays off with jit_above_cost lowered to about 200-2000, the README recommends keeping jit_inline_above_cost and jit_optimize_above_cost at 500000 (the bench script says lowering them adds about 30 ms), and it is beta quality |

## Gotchas

- The published PG18 page was produced by tests/bench_comprehensive.sh (its markdown template matches), not tests/bench_all_backends.sh, which has no llvmjit column. That script runs llvmjit with jit_inline_above_cost and jit_optimize_above_cost at 0 but gives the pg_jitter backends 500000 (comment: they add about 30 ms otherwise), so LLVM is forced into full inlining and -O3 on 20-150 ms queries that default settings would never JIT; most of the llvmjit gap is that compile time (SUM_int execution without it about 45.8 ms vs 42.4 ms sljit, derived from page data).
- Each warmup and timed run is a separate `psql -c` call, so every run starts a new backend process: the deform cache (pg_jitter.deform_cache, per-process) cannot carry compiled code between runs, which removes the cache-favouritism worry, but every run also pays per-connection provider loading, which shows up as the 2-2.4 ms penalty on queries where pg_jitter compiled nothing.
- Numbers were taken 2026-03-24, before the v0.3.0 tag (2026-03-26); v0.3.1 (2026-03-28) fixed a sparse deform dispatch bug around the same time a sljit segfault was reported (issue #59), and the source now says the 0.3.0-era cap 'incorrectly disabled profitable 1000-column sparse deform', so the Wide1K rows (0.94-0.99x vs interpreter) measured no deform JIT at all.
- Several big wins are algorithm swaps inside the JIT (binary-search CASE, PCRE2/StringZilla LIKE and regex) that a different interpreter build could also adopt; upper()/lower() fast paths are disabled in source because collation detection treated en_US.UTF-8 as C and mishandled multibyte text.

## Known shortcomings

- First-party, ARM64 only, compiler and flags unstated; the harness sets jit_inline_above_cost and jit_optimize_above_cost to 0 so LLVM pays full optimization on every query, and the win is mostly compile time, with execution gains over the interpreter small (COUNT_star 0.94x). Off-baseline (PostgreSQL llvmjit, not PyPy, LuaJIT, V8 or HotSpot).
- Enricher: the PostgreSQL 18 page comes from tests/bench_comprehensive.sh, which sets llvmjit's jit_inline_above_cost and jit_optimize_above_cost to 0 but pg_jitter's to 500000, so most of the llvmjit gap is forced compile time; each run is a fresh psql -c backend, so the deform cache cannot favour pg_jitter, and the about 2-2.4 ms per-connection cost shows where nothing compiled (COUNT_star, UNION_ALL_agg). Open wrong-result issue #84 (sljit backend evaluates '(SELECT 0) &gt; 0.1' incorrectly), unanswered; the run (2026-03-24) predates the v0.3.0 tag and v0.3.1's deform-dispatch fix; no commits since 2026-05-03.

## Caveats and trade-offs

First-party benchmarks, one machine, ARM64 only (x86_64 results marked TBD), dated 2026-03-24 for release 0.3.0. The harness (tests/bench_all_backends.sh) sets jit_above_cost, jit_inline_above_cost and jit_optimize_above_cost to 0, so LLVM runs full optimization and inlining on every query and that compile time is inside the EXPLAIN ANALYZE execution time; most of the win over llvmjit is compile time (execution-only SUM_int about 45.8 ms llvmjit vs 42.3 ms sljit, derived from page data). Default thresholds would keep LLVM off these queries entirely. Per-query gains over the interpreter are small and some queries are slower (COUNT_star 0.94x for all three backends); pg_jitter.deform_cache (on by default) can reuse compiled deform code across the warmup and timed runs in one connection while LLVM recompiles, which may favour pg_jitter (not checked). The CRM benchmark is synthetic and built to show the strongest cases. Requires the author's patched forks of sljit and MIR. README calls the code beta quality. Baseline is PostgreSQL's LLVM JIT, not one of the category baselines. [retier] First-party, ARM64 only (single M1 Pro), compiler and flags unstated. The PostgreSQL 18 page comes from tests/bench_comprehensive.sh, which sets llvmjit's jit_inline_above_cost and jit_optimize_above_cost to 0 but pg_jitter's to 500000, so most of the llvmjit gap is forced LLVM compile time; execution gains over the interpreter are small (COUNT_star 0.94x). Each run is a fresh psql -c backend (about 2-2.4 ms per-connection cost where nothing compiles). Open wrong-result issue #84: the sljit backend evaluates '(SELECT 0) &gt; 0.1' incorrectly, unanswered. The run (2026-03-24) predates the v0.3.0 tag and v0.3.1's deform-dispatch fix; no commits since 2026-05-03. Off-baseline (PostgreSQL llvmjit).

PostgreSQL extension only; beta quality by its own README; jit_above_cost must be lowered from 100000 to about 200-2000; avoid for point lookups; AsmJit backend only on arm64 and x86_64; adds embedded JIT libraries (sljit, AsmJit, MIR) in place of LLVM.

## Maintenance

Apache-2.0 and buildable from source for PG 14-18, but beta quality by its own README, maintained by one author with no commits since 2026-05-03 and an unanswered wrong-result bug (#84), so treat it as an experiment to validate against your own query suite rather than an 'active' production component.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party benchmark with public harness (tests/bench_all_backends.sh) and stated CPU (Apple M1 Pro, Darwin 25.2.0, PostgreSQL 18.1), but compiler and build flags for pg_jitter and PostgreSQL are not stated (CMakeLists only defaults to a Release build type), so not A; no independent measurement, so C.
- **Verifier notes:** Record numbers match the PG18 page exactly; added the page's compile-time table and corrected compiler_and_flags. Metadata checked: Apache-2.0, 210 stars, 2 forks, 398 commits, not a fork, last commit 2026-05-03 (active). Shortcomings: first-party ARM64-only numbers, LLVM forced to full optimization on every query, small execution gains over the interpreter, flags and compiler unstated.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`, `maintenance_status`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/bench/ARM64/0.3.0/BENCHMARKS_v18.md>
  - <https://github.com/vladich/pg_jitter>
  - <https://github.com/vladich/pg_jitter/commits/master>
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/README.md>
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/tests/bench_all_backends.sh>
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/vladich/pg_jitter>
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/README.md>
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/bench/ARM64/0.3.0/BENCHMARKS_v18.md>
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/tests/bench_all_backends.sh>
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/tests/bench_comprehensive.sh>
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/tests/parse_explain_json.py>
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/src/pg_jitter_sljit.c>
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/src/pg_jitter_meta.c>
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/src/pg_jitter_common.c>
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/src/pg_jitter_deform_jit.c>
  - <https://raw.githubusercontent.com/vladich/pg_jitter/HEAD/src/pg_jit_funcs.c>
  - <https://github.com/vladich/pg_jitter/tree/master/src>
  - <https://github.com/vladich/pg_jitter/issues?q=is%3Aissue>
  - <https://github.com/vladich/pg_jitter/issues/84>
  - <https://github.com/vladich/pg_jitter/issues/70>
  - <https://github.com/vladich/pg_jitter/issues/59>
  - <https://github.com/vladich/pg_jitter/commits/master>
  - <https://github.com/vladich/pg_jitter/tags>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/vladich/pg_jitter`) · [data/wave12/enrich/raw/github_com_vladich_pg_jitter.json](../../../data/wave12/enrich/raw/github_com_vladich_pg_jitter.json) (enrichment confidence 0.75)

</details>
