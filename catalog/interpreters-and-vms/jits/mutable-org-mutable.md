# mutable (WebAssembly/V8 query compiler)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `AGPL-3.0` · 🟢 active

> Saarland research main-memory DBMS that JIT-compiles SQL to WebAssembly run by embedded V8; claims HyPer-level TPC-H speed.

| | |
|---|---|
| **Beats** | HyPer (LLVM-based query compilation) |
| **Claimed result** | EDBT 2023 abstract (quoted in the README): 'Our results show that we are able to match or even outperform state-of-the-art systems like HyPer' on TPC-H. Snippet only (paper not opened): query compilation with V8's Liftoff is up to 7.4x faster than HyPer's non-optimizing compilation (Q12), and optimizing compilation with TurboFan is up to 6x faster than HyPer's LLVM-based optimizing compilation. These are compile-latency ratios; no execution-time ratio was visible. |
| **Workload** | TPC-H queries (per the EDBT 2023 paper abstract quoted in the README): queries are JIT-compiled to WebAssembly and executed by the embedded V8 engine, which tiers unoptimized to optimized code while the query runs. |
| **Metric** | throughput |
| **Adoption** | 118 stars; academic system from Saarland University |
| **Last commit** | 2025-11-11 |
| **Links** | [repository](https://github.com/mutable-org/mutable) · [benchmark](https://bigdata.uni-saarland.de/publications/Haffner,%20Dittrich%20-%20A%20Simplified%20Architecture%20for%20Fast,%20Adaptive%20Compilation%20and%20Execution%20of%20SQL%20Queries%20@EDBT2023.pdf) |

## Verdict

The README quotes the EDBT 2023 abstract: on TPC-H the V8/Wasm design matches or outperforms HyPer. Search snippets of the paper (not opened; openproceedings.org, the Saarland PDF and arXiv 2104.15098 are blocked here) say mutable beats HyPer and DuckDB on Q1 and Q6 while HyPer is almost 2x faster on Q3, Q12 and Q14, and that compilation is much faster (TurboFan pipeline up to 36x faster than HyPer's LLVM pipeline in one snippet, up to 6x in another; Liftoff up to 7.4x faster than HyPer's non-optimising path on Q12); hardware, compiler and scale factor were not visible.

## Use it when

- Research or teaching on query compilation, join ordering (DPccp, TDMinCutAGaT, the SIGMOD 2023 HeuristicSearch enumerator) or cardinality estimation, where you want to swap one component and keep the rest.
- Studying low-latency query compilation: comparing V8 Liftoff, TurboFan and adaptive tier-up against an LLVM-based compiling engine on the same plans.
- Prototyping data-layout ideas (row, PAX, nested PAX-in-PAX) with generated access code instead of hand-written scans.
- Single-threaded analytical queries over in-memory tables on x86-64 Linux, where the supported subset (the paper evaluates TPC-H Q1, Q3, Q6, Q12 and Q14) covers your workload.

## Skip it when

- As a production database: it is a research system with no documented concurrency control, primary keys that did not reject duplicate inserts (issue #10), and an AGPL-3.0 licence.
- Workloads with DECIMAL arithmetic on the Wasm backend: conversion to DECIMAL is unimplemented at HEAD (src/backend/WasmUtil.cpp line 82), and TPC-H Q6 fails with it (issue #12, open since 2025-04-07).
- Full TPC-H or JOB coverage: only five TPC-H queries are in the benchmark suite, and users have reported crashes and schema errors running the bundled benchmarks (issues #3 and #8).
- Where build cost matters: the default build downloads and compiles a forked V8 (about an hour per the setup guide), needs depot_tools, gn and Clang 16+, and x86-64 builds hard-code -mavx2 -mbmi2.
- Workloads where HyPer's own published strength lies: per the paper (search snippet), HyPer is almost 2x faster than mutable on Q3, Q12 and Q14.

## How it is fast

The EDBT 2023 design delegates code generation to an existing engine: mutable emits Wasm (via Binaryen, optional Binaryen optimisation levels 0-2) quickly and lets V8 compile it with the Liftoff baseline compiler and tier up hot functions to TurboFan while the query runs (dynamic tiering), instead of building an LLVM pipeline as HyPer does. Table data is mapped into the Wasm linear memory with mmap rather than copied, and the DSL specialises code to the declared data layout (row, PAX) and omits three-valued-logic code for NOT NULL columns. Wasm bounds and stack checks are switched off in V8 for normal runs.

## Compared with alternatives

Pick mutable over PochiVM (copy-and-patch code generation, also evaluated on TPC-H queries) when you want a complete SQL system whose compilation tiers come from V8 rather than a code generator you embed in your own engine; pick pg_jitter, AsmJit or sljit instead if you need faster JIT inside PostgreSQL, and TPDE if you want faster LLVM IR back-end compilation.

## Integration

| | |
|---|---|
| **Form** | static lib (libmutable, shared optional) plus a shell binary |
| **Dependencies** | V8 11.1.276 from a mutable fork on gitlab.cs.uni-saarland.de (pinned commit adfc01872f43), Binaryen, Boost (system), Eigen, nlohmann_json, Replxx, Catch2, depot_tools/gn; Pipenv for the Python benchmark and test harness; Tableau Hyper API, DuckDB and PostgreSQL only for comparison runs |
| **Minimum toolchain** | C++20, Clang 16+ (doc/preliminaries.md), CMake 3.21 (CMakeLists.txt) |
| **Platforms** | x86-64 (AVX2, BMI2 and SSE4.2 forced by CMake) and arm64 (V8 target arm64, x86 flags skipped); Linux and macOS; generated code needs V8 so the Wasm backend has no Windows path documented |
| **Thread safety** | not documented; the comparison harness runs DuckDB and HyPer pinned to one core (taskset -c 2) to match mutable's single-threaded execution |
| **Drop-in for the baseline** | no |

## Gotchas

- DECIMAL is unsupported on the Wasm backend at HEAD: convert_in_place() hits M_unreachable("currently not supported") for N_Decimal (WasmUtil.cpp:82). The repo's own benchmark/tpc-h YAMLs declare l_quantity, l_extendedprice, l_discount and l_tax as DECIMAL 10 2, and issue #12 (Q6 at SF 0.01, UBSan 'execution reached an unreachable program point') shows the shipped TPC-H experiment does not run as-is. In a release build without sanitizers M_unreachable expands to __builtin_unreachable(), so this path is undefined behaviour rather than a clean error.
- CMake defaults ENABLE_SANITIZERS=ON and ENABLE_SANITY_FIELDS=ON even for Release builds; pass -DENABLE_SANITIZERS=OFF before timing anything, and define M_ENABLE_SANITY_FIELDS in client code if libmutable was built with sanity fields, or data-structure layouts mismatch.
- The paper's adaptive mode is not the default: options::wasm_adaptive is false, so V8 runs with --no-liftoff and eager TurboFan compilation unless --wasm-adaptive is passed; the bundled tpc-h YAMLs do not pass it. Generated code runs with --no-wasm-bounds-checks and --no-wasm-stack-checks unless a Chrome DevTools port is set.
- In the bundled harness mutable's time is the 'Execute machine code' line (SQL-to-Wasm and V8 compilation excluded) while HyPer's is the hyperd.log query-end 'execution-time' field; compile times are a separate experiment (compile_q1.yml). Compare like with like when reading the nightly dashboard.

## Known shortcomings

- README has no numbers; the EDBT 2023 paper is blocked from this environment (openproceedings.org, cidrdb.org, bigdata.uni-saarland.de). Search snippets show compile-time wins only (Liftoff up to 7.4x, TurboFan up to 6x faster compilation than HyPer); the execution claim is 'match or outperform'. Paper-access retier candidate (B).
- Enricher: snippets show mutable beating HyPer and DuckDB on TPC-H Q1 and Q6 while HyPer is about 2x faster on Q3, Q12 and Q14; only 5 queries covered; compile-time win quoted as 36x in one snippet and 6x in another. Correctness flaw at HEAD: the Wasm backend cannot convert to DECIMAL (src/backend/WasmUtil.cpp:82, M_unreachable 'currently not supported'); issue #12 (open since 2025-04-07, no reply) shows Q6 hitting UBSan 'execution reached an unreachable program point', and the repo's own tpc-h YAMLs use DECIMAL 10 2, so the shipped TPC-H benchmark does not run; a release build without sanitizers turns this into __builtin_unreachable undefined behaviour. ENABLE_SANITIZERS defaults ON in Release; default mode is not adaptive (wasm_adaptive=false, --no-liftoff); Wasm bounds checks off; V8 11.1.276 from a Saarland GitLab fork. Independent ADC 2023 study arXiv 2311.04692 (PostgreSQL LLVM JIT vs mutable) is a retier lead.

## Caveats and trade-offs

Snippet only: the numbers live in the EDBT 2023 paper (PDF at bigdata.uni-saarland.de and openproceedings.org/2023/conf/edbt/paper-156.pdf, plus the earlier arXiv 2104.15098 'Fast Compilation and Execution of SQL Queries with WebAssembly'), all EGRESS_BLOCKED here, so the tier is capped at C although the paper is peer reviewed (a verifier who can read it should consider B). The visible ratios are compilation-time wins; for execution the claim is 'match or even outperform', not a uniform win. Baseline HyPer is closed source, run through the proprietary Tableau Hyper API. The repo ships a continuous-benchmarking harness (benchmark/Benchmark.py with YAML experiments and connectors for PostgreSQL, DuckDB and HyPer, documented in benchmark/README.md) and a nightly dashboard at cb.mutable.uni-saarland.de (blocked here), but no result table in the repo. Research system, AGPL-3.0.

Research main-memory DBMS ('for research and fast prototyping'); AGPL-3.0 licence; relies on an embedded V8 build for code generation and execution; query compilation is one feature among many.

## Maintenance

Active (last commits 2025-11-11 adding Wasm memory64 support) research system under AGPL-3.0; issues get few maintainer replies (issue #12 open six months without one), so treat it as a reference design to study rather than a component to depend on; an independent ADC 2023 study (arXiv 2311.04692, 'An Empirical Analysis of Just-in-Time Compilation in Modern Databases') compares its Wasm JIT with PostgreSQL's LLVM JIT and could support a re-tier once readable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The repo README only quotes the EDBT 2023 abstract ('match or even outperform state-of-the-art systems like HyPer') with no numbers, and the paper itself (openproceedings.org and bigdata.uni-saarland.de copies, arXiv 2104.15098, CIDR 2023 PDF) is EGRESS_BLOCKED here and has no GitHub mirror that a search found; search snippets give compile-time ratios only. The peer-reviewed paper would justify B once someone reads it; capped at C until then.
- **Verifier notes:** Real peer-reviewed academic system with a public HyPer/DuckDB/PostgreSQL comparison harness, but no numbers reachable from this environment; candidate for the paper-access retier list (EDBT 2023 paper-156). Metadata verified: AGPL-3.0 (LICENSE and README), 118 stars, not a fork, last commit 2025-11-11 (active). The metric field says throughput while the only concrete snippet numbers are compile latency.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compared_against_cpp_std_directly`, `caveats`
- **Shortcomings recorded by:** paper access; paper or ADC 2023 study access and a DECIMAL-capable TPC-H run
- **Pages the verifier opened:**
  - <https://github.com/mutable-org/mutable>
  - <https://github.com/mutable-org/mutable/commits>
  - <https://raw.githubusercontent.com/mutable-org/mutable/HEAD/README.md>
  - <https://raw.githubusercontent.com/mutable-org/mutable/HEAD/benchmark/README.md>
  - <https://raw.githubusercontent.com/mutable-org/mutable/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/mutable-org/mutable>
  - <https://raw.githubusercontent.com/mutable-org/mutable/HEAD/README.md>
  - <https://raw.githubusercontent.com/mutable-org/mutable/HEAD/benchmark/README.md>
  - <https://raw.githubusercontent.com/mutable-org/mutable/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/mutable-org/mutable/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/mutable-org/mutable/HEAD/doc/setup.md>
  - <https://raw.githubusercontent.com/mutable-org/mutable/HEAD/doc/preliminaries.md>
  - <https://raw.githubusercontent.com/mutable-org/mutable/HEAD/benchmark/tpc-h/q1.yml>
  - <https://raw.githubusercontent.com/mutable-org/mutable/HEAD/benchmark/tpc-h/compile_q1.yml>
  - <https://raw.githubusercontent.com/mutable-org/mutable/HEAD/benchmark/database_connectors/hyper.py>
  - <https://raw.githubusercontent.com/mutable-org/mutable/HEAD/benchmark/database_connectors/hyperconf.py>
  - <https://raw.githubusercontent.com/mutable-org/mutable/HEAD/benchmark/database_connectors/mutable.py>
  - <https://raw.githubusercontent.com/mutable-org/mutable/HEAD/benchmark/database_connectors/duckdb.py>
  - <https://raw.githubusercontent.com/mutable-org/mutable/HEAD/src/backend/WasmUtil.cpp>
  - <https://raw.githubusercontent.com/mutable-org/mutable/HEAD/src/backend/V8Engine.cpp>
  - <https://raw.githubusercontent.com/mutable-org/mutable/HEAD/include/mutable/util/macro.hpp>
  - <https://raw.githubusercontent.com/mutable-org/mutable/HEAD/CMakeFiles/V8.cmake>
  - <https://github.com/mutable-org/mutable/commits>
  - <https://github.com/mutable-org/mutable/issues>
  - <https://github.com/mutable-org/mutable/issues?q=is%3Aissue+is%3Aclosed>
  - <https://github.com/mutable-org/mutable/issues/3>
  - <https://github.com/mutable-org/mutable/issues/8>
  - <https://github.com/mutable-org/mutable/issues/10>
  - <https://github.com/mutable-org/mutable/issues/12>
  - <https://github.com/mutable-org/mutable/issues/13>
  - https://openproceedings.org/2023/conf/edbt/paper-156.pdf (EGRESS_BLOCKED; WebSearch snippets used instead)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/mutable-org/mutable`) · [data/wave12/enrich/raw/github_com_mutable_org_mutable.json](../../../data/wave12/enrich/raw/github_com_mutable_org_mutable.json) (enrichment confidence 0.5)

</details>
