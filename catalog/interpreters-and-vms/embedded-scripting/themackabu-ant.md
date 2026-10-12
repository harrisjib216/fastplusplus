# Ant (Ant Silver JavaScript engine)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🟢 active

> Small JavaScript runtime with its own engine and a MIR-based JIT; about 1.8-2.0x QuickJS on the v8-v7 suite.

| | |
|---|---|
| **Beats** | QuickJS 2026-06-04 (also Duktape 2.99.99 / 2.7.0; its own README compares cold start against Node, Bun and Deno) |
| **Claimed result** | Score on Ubuntu 2186 vs QuickJS 1217 and Duktape 489; macOS arm64 3589 vs 1761 and 905; Windows 2001 vs 1067 and 371 (about 1.8x, 2.0x and 1.9x vs QuickJS, derived from page data). README cold start: 3.9 ms vs Bun 8.8 ms, Deno 18.6 ms, Node 29.4 ms (Apple M5 Pro, hyperfine). |
| **Workload** | V8 v7 benchmark suite combined score in the ahaoboy/js-engine-benchmark daily CI; the project's own README separately times a Hono import cold start with hyperfine. |
| **Metric** | throughput |
| **Hardware** | GitHub Actions hosted runners (ubuntu-latest, macos-latest arm64, windows-latest); CPU model not stated |
| **Adoption** | 1.3k stars |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/theMackabu/ant) · [benchmark](https://github.com/ahaoboy/js-engine-benchmark) |

## Verdict

In ahaoboy/js-engine-benchmark's daily CI run of the Mozilla v8-v7 suite (10/5/2026 snapshot), ant 15.1.4977edb5.0 scored 2186 / 3589 / 2001 on ubuntu / macOS arm64 / Windows GitHub runners vs QuickJS 2026.06.04 at 1217 / 1761 / 1067 and Duktape at 489 / 905 / 371. That is about 1.8x, 2.0x and 1.9x QuickJS (derived from page data). Compiler flags for the QuickJS build are its Makefile defaults; the CPU model is not stated.

## Use it when

- CLI tools, serverless or edge handlers where startup time and binary size matter: README hyperfine run shows a Hono import cold start of 3.9 ms vs Bun 8.8 ms and Node 29.4 ms on an Apple M5 Pro
- You currently embed QuickJS or Duktape and run compute-heavy scripts (numeric loops, crypto, string and regex work) where a JIT helps: NavierStokes 8014 vs 1947 and Crypto 3696 vs 913 against QuickJS on ubuntu
- You want Node-compatible modules and npm packages without shipping V8, on Linux (glibc or static musl), macOS or Windows (MinGW), x64 or aarch64
- C hosts that can accept a multi-megabyte static library and a C23 toolchain in exchange for a faster engine than the pure interpreters

## Skip it when

- You need spec completeness: test262 pass rate is about 66% (35590 of 53578), while QuickJS covers almost all of ES2023
- Size or memory budgets fit QuickJS or Duktape: the suite's ant binary is 11.7 MB on ubuntu vs QuickJS 1 MB and Duktape 370 KB, and the Windows install totals 47.9 MB with DLLs
- Allocation- or GC-heavy workloads: QuickJS beats it on Splay (3183 vs 2483 on ubuntu, 5786 vs 2338 on macOS arm64) and on RayTrace
- You need V8, JSC or SpiderMonkey-class peak speed: issue #101 reports an N-body kernel at 551 ms in Ant vs 18 ms in Node and about 380 ms in CPython, and a Richards score of about 1862 vs Node's 57267
- You need a stable, documented embedding ABI: the C API has a 'TODO: improve naming' comment, there is no embedding guide beyond examples/embed, and the major version moves fast (README benchmark on 14.1, the suite's build on 15.1)

## How it is fast

Silver compiles source to bytecode and runs it in an interpreter. Per-function type feedback drives a method JIT built on a fork of the MIR backend: a function is compiled after 100 calls, loops tier up through on-stack replacement after about 500 back-edges (scaled by code size), and a function that bails out 5 times goes back to the interpreter. Objects use shapes with polymorphic and megamorphic inline caches, and the GC uses card tables. Release builds use Clang -O3 with LTO, checked-in LLVM PGO profiles trained on tests/bench_\* and an HTTP server workload, and mimalloc as the allocator.

## Compared with alternatives

Pick Ant over QuickJS or PrimJS when hot loops dominate and an extra 10 MB or so of binary is acceptable: the same suite shows about 1.8-2.0x QuickJS. Stay with QuickJS when you need near-complete ES conformance, a 1 MB footprint or a mature embedding API, and prefer Escargot or V8 when you need a proven engine rather than a 2026 newcomer.

## Integration

| | |
|---|---|
| **Form** | static lib (packages/libant builds libant.a and libant-lto.a) or standalone CLI binary |
| **Dependencies** | Many vendored Meson subprojects: MIR fork, mimalloc, libuv, BoringSSL, PCRE2, libffi, nghttp2, llhttp, zlib-ng, brotli, LMDB, yyjson, utf8proc, Ada, tlsuv, WAMR and others; build also needs Meson, CMake, Node.js &gt;= 22, Zig &gt;= 0.16, and a pinned Rust nightly for Temporal unless -Dtemporal=disabled |
| **Minimum toolchain** | C23 (-std=gnu23): GCC &gt;= 14 or Clang &gt;= 18; Apple Clang on macOS; MinGW-w64 GCC via MSYS2 (gnu2x) on Windows; MSVC not supported |
| **Platforms** | Linux x64 and aarch64 (glibc and static musl), macOS x64 and aarch64, Windows x64 (MinGW); a wasm32-wasip1 package carries the parser, interpreter and GC without the JIT |
| **Thread safety** | Not documented; the API is built around per-isolate state (ant_t created by ant_create), and the embed example creates one isolate per runtime |
| **Drop-in for the baseline** | no |

## Gotchas

- The suite's comparison is JIT against interpreters, with different build pipelines. Ant has no \*-build entry in js-engine-setup's info.json, so it appears to be the project's own release binary (Clang, -O3, LTO, PGO per BUILDING.md), while QuickJS is a plain upstream 'make' from ahaoboy/quickjs-build. Each engine runs once per OS with no repeats, on unnamed GitHub Actions CPUs.
- Embedders must call js_setstackbase with an address on the host stack before evaluating code, and native functions report errors by returning js_mkerr records, not ordinary Error values.
- The JIT disables itself for a function after 5 bailouts, and tier-up thresholds are fixed (100 calls; OSR after 500 or more back-edges), so short or type-unstable code runs in the interpreter.
- A libant link on macOS pulls in the Security, CoreFoundation and Hypervisor frameworks (sandbox backends), so it is not a light dependency.

## Known shortcomings

- A JIT (MIR fork) compared against interpreters on ahaoboy/js-engine-benchmark (2186/3589/2001 vs QuickJS 1217/1761/1067 and Duktape 489/905/371) with prebuilt binaries on unnamed GitHub Actions CPUs; loses RayTrace and Splay to QuickJS, the suite has 59 stars and the embedding API is unconfirmed (include/ant.h exists).
- Enricher: suite numbers re-derived to 1.8x/2.0x/1.9x over QuickJS; Ant appears to run its own release binary (Clang -O3, LTO, PGO; no build entry in info.json) against a plain upstream make of QuickJS, one run per OS, CPU unnamed; losses on Splay (2338 vs 5786 on macOS) and RayTrace, and issue #101 reports N-body at 551 ms against Node 18 ms and CPython about 380 ms. Embedding API confirmed (packages/libant, examples/embed/embed.c).

## Caveats and trade-offs

Engines are installed as prebuilt binaries through the suite owner's ahaoboy/js-engine-setup action (strip: true) and \*-build repos; compiler flags and CPU model are not stated (GitHub Actions runners), and the suite is small (59 stars), so this is third-party but short of tier A. Ant Silver has a JIT (a fork of the MIR backend) while QuickJS and Duktape are pure interpreters, so the comparison is JIT engine vs interpreters. The score is one v8-v7 aggregate (an older, partly micro-benchmark suite) and ant does not win every component: on ubuntu QuickJS beats it on RayTrace (1594 vs 1059) and Splay (3183 vs 2483). Engines are run as shells, so startup and runtime wrappers can matter. The project's own README compares only cold start and size against Node, Bun and Deno (Hono import benchmark) and does not mention QuickJS or Duktape, so the QuickJS/Duktape comparison rests only on the third-party suite. Primarily a CLI runtime; the repo has public headers (include/ant.h, isolate.h, runtime.h) that suggest an embedding API, but embedding use was not confirmed. test262 pass rate is about 66% per its README.

Own engine (Ant Silver) with a JIT built on a MIR fork, packaged as a Node-style runtime of about 9-12 MB; test262 pass rate about 66% (35590 of 53578 at revision 2026-09-13). Binary is 11.7M on Ubuntu vs QuickJS 1M.

## Maintenance

Very active (daily commits, last on 2026-10-05; 1.3k stars), MIT-licensed and usable as a CLI today, but the engine is young (about 66% of test262) and the embedding library comes with one example and no stable-ABI promise.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party suite (ahaoboy/js-engine-benchmark, v8-v7 benchmarks run by .github/workflows/update.yml on GitHub Actions) lists ant 2186/3589/2001 vs QuickJS 1217/1761/1067 vs Duktape 489/905/371 (ubuntu/macos-arm64/windows) in the 10/5/2026 snapshot. Engines come prebuilt via the ahaoboy/js-engine-setup action, no compiler flags or CPU model, so not A.
- **Verifier notes:** All quoted scores and versions (ant 15.1.4977edb5.0, QuickJS 2026.06.04, Duktape 2.99.99 / 2.7.0) match the README bench tables; 1.8x QuickJS and 4.5x Duktape on ubuntu are derived from page data. Shortcoming: JIT engine compared with interpreters, prebuilt binaries on unnamed CI hardware, ant loses RayTrace and Splay to QuickJS, embedding API unconfirmed.
- **Fields the verifier corrected:** `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ahaoboy/js-engine-benchmark>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/README.md>
  - <https://github.com/ahaoboy/js-engine-benchmark/tree/main/scripts>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/scripts/update.ts>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/scripts/build.ts>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/package.json>
  - <https://github.com/ahaoboy/js-engine-benchmark/tree/main/.github/workflows>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/.github/workflows/update.yml>
  - <https://github.com/theMackabu/ant>
  - <https://github.com/theMackabu/ant/commits>
  - <https://github.com/theMackabu/ant/tree/master/include>
  - <https://raw.githubusercontent.com/theMackabu/ant/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/theMackabu/ant>
  - <https://raw.githubusercontent.com/theMackabu/ant/HEAD/README.md>
  - <https://raw.githubusercontent.com/theMackabu/ant/HEAD/BUILDING.md>
  - <https://raw.githubusercontent.com/theMackabu/ant/HEAD/ARCHITECTURE.md>
  - <https://raw.githubusercontent.com/theMackabu/ant/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/theMackabu/ant/HEAD/include/ant.h>
  - <https://raw.githubusercontent.com/theMackabu/ant/HEAD/include/runtime.h>
  - <https://raw.githubusercontent.com/theMackabu/ant/HEAD/include/isolate.h>
  - <https://raw.githubusercontent.com/theMackabu/ant/HEAD/include/types.h>
  - <https://raw.githubusercontent.com/theMackabu/ant/HEAD/include/silver/jit.h>
  - <https://raw.githubusercontent.com/theMackabu/ant/HEAD/include/silver/feedback.h>
  - <https://raw.githubusercontent.com/theMackabu/ant/HEAD/docs/repo/runtime-invariants.md>
  - <https://raw.githubusercontent.com/theMackabu/ant/HEAD/examples/embed/embed.c>
  - <https://github.com/theMackabu/ant/tree/master/packages/libant>
  - <https://raw.githubusercontent.com/theMackabu/ant/HEAD/packages/libant/build.sh>
  - <https://raw.githubusercontent.com/theMackabu/ant/HEAD/packages/libant/example.sh>
  - <https://raw.githubusercontent.com/theMackabu/ant/HEAD/packages/libant/meson.build>
  - <https://raw.githubusercontent.com/theMackabu/ant/HEAD/packages/libant/meson_options.txt>
  - <https://github.com/theMackabu/ant/tree/master/meson/pgo>
  - <https://raw.githubusercontent.com/theMackabu/ant/HEAD/meson/pgo/build.sh>
  - <https://raw.githubusercontent.com/theMackabu/ant/HEAD/meson/pgo/flags.sh>
  - <https://github.com/theMackabu/ant/tree/master/tests>
  - <https://github.com/theMackabu/ant/issues?q=is%3Aissue>
  - <https://github.com/theMackabu/ant/issues/101>
  - <https://github.com/theMackabu/ant/commits>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/scripts/update.ts>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/.github/workflows/update.yml>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-setup/main/info.json>
  - <https://github.com/ahaoboy/quickjs-build>
  - <https://raw.githubusercontent.com/ahaoboy/quickjs-build/HEAD/build.sh>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/themackabu/ant`) · [data/wave12/enrich/raw/github_com_themackabu_ant.json](../../../data/wave12/enrich/raw/github_com_themackabu_ant.json) (enrichment confidence 0.7)

</details>
