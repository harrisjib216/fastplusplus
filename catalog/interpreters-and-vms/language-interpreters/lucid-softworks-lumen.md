# lumen (Rust JavaScript engine with ARM64 template JIT)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `MIT` · 🟢 active

> Std-only Rust JavaScript engine with an ARM64 template JIT; about 2.2x QuickJS on V8-v7 on Apple Silicon, slower on x86-64.

| | |
|---|---|
| **Beats** | QuickJS (bellard, version 2026.06.04 in the CI table); V8 and JavaScriptCore are NOT beaten |
| **Claimed result** | ahaoboy/js-engine-benchmark macos-arm64 table (run dated 10/5/2026): lumen Score 3953 vs QuickJS 1761, quickjs-ng 1660, hermes 1233, i.e. 2.24x QuickJS (derived from page data). The composite win comes from three numeric subtests: Richards 11374 vs 1246, Crypto 10633 vs 1170, NavierStokes 21200 vs 2349 (about 9x each, derived from page data); lumen is slower than QuickJS on RayTrace (1925 vs 2408), EarleyBoyer (1808 vs 3217) and Splay (5444 vs 5786). Same table: JavaScriptCore 67664, v8 64220, bun 46772, node 37405, so lumen is about 16x below V8 (derived from page data). Ubuntu table: lumen 444 vs QuickJS 1217 (0.36x, slower on all eight subtests), v8 48107. No Windows result for lumen. |
| **Workload** | Classic V8 v7 benchmark suite composite score (Richards, DeltaBlue, Crypto, RayTrace, EarleyBoyer, RegExp, Splay, NavierStokes), higher is better, run nightly in GitHub Actions across engines. |
| **Metric** | throughput |
| **Hardware** | GitHub Actions runners macos-latest (arm64) and ubuntu-latest, scheduled daily; CPU model not stated |
| **Compiler and flags** | Not stated; the workflow installs engines through the ahaoboy/js-engine-setup action and runs the v8-v7 suite (fork of mozilla/arewefastyet benchmarks/v8-v7); lumen build flags not stated |
| **Adoption** | 271 stars; used as the JS backend of lucid-softworks/browser |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/lucid-softworks/lumen) · [benchmark](https://github.com/ahaoboy/js-engine-benchmark) |

## Verdict

In ahaoboy/js-engine-benchmark's daily GitHub Actions run of the classic V8-v7 suite (snapshot 2026-10-05), the lumen nightly 0.1.3 (f6c9860, rustc stable, opt-level 3, fat LTO, codegen-units 1, panic=abort per lumen's Cargo.toml and nightly.yml) scored 3953 against QuickJS 2026.06.04's 1761 on the macos-latest arm64 runner, but 444 against 1217 on the ubuntu-latest x86-64 runner; runner CPU models are not recorded and each engine runs once.

## Use it when

- Embedding a full-spec JS engine in a Rust program with zero third-party dependencies, running on Apple Silicon or Linux arm64.
- Numeric-loop-heavy scripts on ARM64, where the JIT wins big: Richards, Crypto and NavierStokes score about 9x QuickJS on the macOS arm64 runner.
- You need spec completeness (Intl, Temporal, Proxy, modules, full RegExp) that small embeddable engines lack, and can trade binary size for it.
- Experimenting with a hackable, safe-Rust engine whose three tiers are cross-checked by a differential fuzzer.

## Skip it when

- x86-64 hosts: on the Ubuntu runner lumen scores 444 against QuickJS 1217 and loses all eight V8-v7 subtests, because the x86-64 JIT backend is 'correctness-first' with checked per-op helpers.
- Object-, GC- or string-heavy code: even on arm64 it loses RayTrace, EarleyBoyer and Splay to QuickJS; the maintainers' own docs put a Djot parser at about 15.5x Node's time, and issue #12 timed a yt-dlp ejs script at 55.80 minutes against QuickJS's 8.20 seconds (July 2026).
- You need JIT-class speed: the authors' Apple M4 runs give a V8-v7 composite of about 8,560, about 9.7x below Node 24 and 11x below Bun.
- Size-constrained targets: the release binary is about 8 to 11 MB (about 3 MB of CLDR data unless built with --no-default-features), versus about 1 MB for QuickJS.
- Windows or https: no nightly Windows build (issue #22 open), and fetch rejects https URLs.

## How it is fast

Bytecode functions get per-site inline caches backed by object shapes (hidden classes) and dense-array fast paths; on ARM64 the template JIT bakes those cache reads into the machine code, fuses compare-and-branch, and keeps runs of arithmetic in floating-point registers ('numeric register chains'). A separate numeric-loop backend finds closed numeric loops in the control-flow graph, gives up to eight locals fixed FP register homes, and writes state back at guarded exits. A liveness pass moves values at their last use instead of cloning them, which matters because values are reference-counted with a cycle collector.

## Compared with alternatives

Pick lumen over Porffor when you need a full-spec engine that runs arbitrary JS (test262-complete, modules, Intl) rather than an AOT compiler, and over lo or LLRT when you want a pure-Rust, dependency-free engine rather than a V8- or QuickJS-based runtime; for speed on x86-64 none of these beats plain QuickJS by lumen's route.

## Integration

| | |
|---|---|
| **Form** | Rust workspace used as a git dependency (not published to crates.io; the crates.io name 'lumen' is an unrelated tool) or prebuilt CLI binaries |
| **Dependencies** | none (std only) |
| **Minimum toolchain** | Rust 1.82 (workspace rust-version), edition 2021 |
| **Platforms** | ARM64 JIT on macOS, Linux and Windows; correctness-first x86-64 JIT on macOS, Linux and Windows; other architectures fall back to the bytecode VM; nightly binaries for macOS arm64/x86_64 and Linux x86_64/arm64 only |
| **Thread safety** | Engine is !Send; the runtime gives one loop thread ownership of the engine and runs blocking work on a std thread pool |
| **Drop-in for the baseline** | no |

## Gotchas

- The speedup over QuickJS is architecture-dependent: on the same 2026-10-05 shootout lumen is 2.24x QuickJS on macos-arm64 but 0.36x on ubuntu x86-64, so benchmark on your own target.
- The composite is a geometric mean, and the arm64 win comes from three numeric subtests at about 9x; the suite's Richards fixture is part of lumen's own JIT CI, so the engine is tuned on this benchmark.
- The shootout runs each engine once per platform per day on shared GitHub runners; the macOS runner score (3953) is less than half of the authors' Apple M4 score (about 8,560), so absolute numbers move with runner hardware.
- Memory is reference counting plus cycle collection, and the JIT maps executable memory through raw mmap/mprotect or VirtualAlloc declarations; unsafe code is concentrated in the JIT templates and the N-API loader.

## Known shortcomings

- Win only on macOS arm64 in ahaoboy's js-engine-benchmark (3953 vs QuickJS 1761) and only from Richards, Crypto and NavierStokes; loses RayTrace, EarleyBoyer and Splay to QuickJS; on Ubuntu 444 vs 1217, slower on all 8 subtests; no Windows run; about 16x below V8.
- Enricher: the arm64 win comes from three numeric subtests at about 9x and the suite's Richards fixture is part of lumen's own JIT CI, so the engine is tuned on this benchmark; the shootout runs each engine once per platform per day on shared GitHub runners (the macOS runner score 3953 is under half the authors' Apple M4 score of about 8,560). Real applications still run 15x or more slower than Node; fast JIT paths are ARM64-only; not published as a library crate.

## Caveats and trade-offs

The README makes no speed claim; the claim here comes only from a third-party engine shootout. The advantage over QuickJS appears on the macOS arm64 runner only, and only in the composite: lumen wins Richards, Crypto, NavierStokes, DeltaBlue and RegExp but loses RayTrace, EarleyBoyer and Splay to QuickJS there. On the Ubuntu x86-64 runner lumen scores 444 against QuickJS 1217 and is slower on every subtest; the README says the full set of inline JIT fast paths lives only in the ARM64 backend, while the x86-64 backend is correctness-first with checked per-op helpers. Lumen is not run on Windows in the shootout. It is far behind JIT engines (V8, JavaScriptCore, Node, Bun) on both platforms. Lumen's own docs/closure-numeric-regions.md says Djot takes about 15.5x Node's time and 23.9x Bun's, and docs/closure-call-cache.md says the 'within-2x Node/Bun objective remains unmet'. The shootout's lumen version column reads 0.1.3.f6c9860 and the GitHub Actions CPU model is not recorded.

std-only, zero third-party dependencies, three execution tiers (tree-walker, bytecode VM, template JIT; jit is default). Full inline fast paths exist only in the ARM64 JIT backend; the x86-64 backend is 'correctness-first' with native control flow and checked helpers. Other architectures degrade to the bytecode VM. Passes 100% of test262 (53,400/53,400, README). Release binary is about 8 to 11 MB (about 3 MB of it Intl/CLDR data); no https in fetch.

## Maintenance

Very active (last commit 2026-09-24, 0.1.x, MIT) and copyable, but young: real applications still run 15x or more slower than Node, the fast JIT paths are ARM64-only, and it is not published as a library crate.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party CI shootout (ahaoboy/js-engine-benchmark, v8-v7 suite forked from mozilla/arewefastyet, run daily by .github/workflows/update.yml on macos-latest, ubuntu-latest and windows-latest) lists lumen 0.1.3.f6c9860 at Score 3953 vs QuickJS 2026.06.04 at 1761 on macos-arm64 in the 10/5/2026 snapshot; code is public but the runners' CPU models and the engines' compiler flags are not stated, so not A (same B precedent as ChakraCore, ant, njs, quanta in this wave).
- **Verifier notes:** Every number in the record matches the ahaoboy README tables (10/5/2026 snapshot); metadata checked (MIT, 271 stars, 8 forks, not a fork, last commit 2026-09-24, JS backend of lucid-softworks/browser). Shortcomings to record: win over QuickJS is arm64-only and driven by three numeric subtests (loses RayTrace, EarleyBoyer, Splay), slower than QuickJS on x86-64 Ubuntu on all subtests, no Windows run, far below V8/JSC/Node/Bun, own docs say about 15.5x Node's time on Djot.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** x86-64 comparison; x86-64 comparison and application-level workloads
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/.github/workflows/update.yml>
  - <https://github.com/lucid-softworks/lumen>
  - <https://github.com/lucid-softworks/lumen/commits>
  - <https://raw.githubusercontent.com/lucid-softworks/lumen/HEAD/README.md>
  - <https://raw.githubusercontent.com/lucid-softworks/lumen/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/lucid-softworks/lumen/HEAD/docs/closure-numeric-regions.md>
  - <https://raw.githubusercontent.com/lucid-softworks/lumen/HEAD/docs/closure-call-cache.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/lucid-softworks/lumen/HEAD/README.md>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/README.md>
  - <https://github.com/ahaoboy/js-engine-benchmark>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/info.json>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/macos-amd64.json>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/macos-arm64.json>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/ubuntu.json>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/.github/workflows/update.yml>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/package.json>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/scripts/update.ts>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/scripts/build.ts>
  - <https://github.com/ahaoboy/js-engine-setup>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-setup/main/info.json>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-setup/main/README.md>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-setup/main/action.yml>
  - <https://github.com/lucid-softworks/lumen/tree/main/.github/workflows>
  - <https://raw.githubusercontent.com/lucid-softworks/lumen/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/lucid-softworks/lumen/HEAD/crates/lumen/Cargo.toml>
  - <https://raw.githubusercontent.com/lucid-softworks/lumen/HEAD/.github/workflows/nightly.yml>
  - <https://raw.githubusercontent.com/lucid-softworks/lumen/HEAD/.github/workflows/jit.yml>
  - <https://raw.githubusercontent.com/lucid-softworks/lumen/HEAD/.github/workflows/release-plz.yml>
  - <https://raw.githubusercontent.com/lucid-softworks/lumen/HEAD/release-plz.toml>
  - <https://github.com/lucid-softworks/lumen/tree/main/docs>
  - <https://github.com/lucid-softworks/lumen/tree/main/docs/benchmarks>
  - <https://raw.githubusercontent.com/lucid-softworks/lumen/HEAD/docs/closure-numeric-regions.md>
  - <https://raw.githubusercontent.com/lucid-softworks/lumen/HEAD/docs/closure-call-cache.md>
  - <https://raw.githubusercontent.com/lucid-softworks/lumen/HEAD/docs/optimizer.md>
  - <https://github.com/lucid-softworks/lumen/issues?q=is%3Aissue>
  - <https://github.com/lucid-softworks/lumen/issues/8>
  - <https://github.com/lucid-softworks/lumen/issues/12>
  - <https://crates.io/api/v1/crates/lumen>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/lucid-softworks/lumen`) · [data/wave12/enrich/raw/github_com_lucid_softworks_lumen.json](../../../data/wave12/enrich/raw/github_com_lucid_softworks_lumen.json) (enrichment confidence 0.7)

</details>
