# PrimJS

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C/C++` · `Apache-2.0` · 🟢 active

> ByteDance's QuickJS fork for Lynx with an arm64 template interpreter and tracing GC; claims 1.29x QuickJS on Octane.

| | |
|---|---|
| **Beats** | QuickJS (commit 6e2e68) |
| **Claimed result** | Octane (version 9) overall score 3735 vs 2904 for QuickJS 6e2e68 (about 1.29x, derived from page data; the README rounds it to about 28%). Per test: RayTrace 2751 vs 1273, EarleyBoyer 4270 vs 2284, NavierStokes 4166 vs 2640, PdfJS 6642 vs 4236, Crypto 1844 vs 1349, Richards 1247 vs 1163, Mandreel 1372 vs 1350; CodeLoad (16992 vs 18137) and MandreelLatency (9587 vs 9680) are lower. |
| **Workload** | Octane benchmark suite (15 sub-benchmarks, Octane score version 9) run on both engines. |
| **Metric** | throughput |
| **Hardware** | Apple M1 Max, 64GB RAM, macOS Sonoma 14.0 |
| **Compiler and flags** | gn build with enable_quickjs_debugger=false target_cpu=arm64 target_os=mac is_debug=false enable_optimize_with_O2=true; snapshot, compatible_mm and tracing GC at defaults; compiler name not stated (gn default toolchain). |
| **Adoption** | 1.1k stars; engine of the Lynx cross-platform framework |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/lynx-family/primjs) · [benchmark](https://github.com/lynx-family/primjs/blob/develop/docs/benchmark.md) |

## Verdict

The project's own table (Apple M1 Max, macOS Sonoma 14.0, gn release build with O2, target_cpu arm64, snapshot, compatible memory management and tracing GC on; compiler not named) gives an Octane v9 score of 3735 for PrimJS vs 2904 for QuickJS commit 6e2e68 (about 1.29x, derived from page data), winning 13 of 15 sub-tests. Independent GitHub Actions runs of the V8 v7 suite (ahaoboy/js-engine-benchmark, PrimJS built by ahaoboy/primjs-build with the same feature flags on arm64) do not reproduce a lead over current QuickJS 2026.06.04: 1694 vs 1761 on macOS arm64 and 737 vs 1217 on ubuntu x86-64, where the PrimJS features are compiled out.

## Use it when

- You are building on Lynx, where PrimJS is the engine and its object-model integration and DevTools support come with it.
- Mobile arm64 apps (Android, iOS) that need an interpreter-only engine (no JIT allowed) and run code like the Octane RayTrace, EarleyBoyer, NavierStokes or PdfJS kernels, where PrimJS posted 1.6-2.2x a 2024 QuickJS build on an Apple M1 Max.
- Hosts that want a tracing GC instead of QuickJS reference counting, for example to avoid leaks from reference cycles or to get heap snapshots and memory analysis.
- Projects that need Chrome DevTools Protocol debugging of an embedded QuickJS-class engine without writing their own debugger.

## Skip it when

- Linux, Windows or any x86-64 target: config.gni forces snapshot, compatible memory management and tracing GC off unless target_cpu is arm64 on Android, iOS or macOS, and the independent ahaoboy/js-engine-benchmark CI scored PrimJS 737 vs 1217 for QuickJS 2026.06.04 on ubuntu, with no Windows build.
- When current upstream QuickJS is an option: on macOS arm64, with the template interpreter and tracing GC enabled by the same gn args as the project's benchmark, the same CI scored PrimJS 1694 vs QuickJS 2026.06.04 1761 on the V8 v7 suite (PrimJS ahead on Crypto, DeltaBlue and NavierStokes, behind on RayTrace, EarleyBoyer, RegExp, Splay and Richards).
- Code that needs ES2020+ language features: the engine targets ES2019, and open issue #44 reports that `null ?? 3` returns null.
- Drop-in replacement of an existing QuickJS embedding: every API symbol is renamed (JS_\* to LEPUS_\*), the tracing GC requires HandleScope registration of temporaries in native code, and the build needs gn, ninja and the Lynx 'hab sync' dependency tooling.
- Startup-sensitive or parse-heavy workloads: PrimJS scored below QuickJS on Octane CodeLoad (16992 vs 18137) and MandreelLatency (9587 vs 9680) in its own table.

## How it is fast

On arm64 Android, iOS and macOS it replaces QuickJS's C interpreter loop with a template interpreter: per-bytecode handlers are generated ahead of time (by an LLVM-based generator in src/interpreter/primjs/codegen) into embedded.S, run on the native stack, keep JSContext, bytecode pointer, constant pool and variable buffers pinned in callee-saved registers x19-x28, and cache the top two stack slots in x0/x1 (top-of-stack caching) with table dispatch at the end of each handler. Memory management switches from reference counting to a parallel mark-sweep tracing GC (dlmalloc-style per-thread free lists, multi-threaded mark and sweep with task stealing), which the design doc expects to be 10-20% faster than reference counting by removing increments and decrements.

## Compared with alternatives

Pick PrimJS over QuickJS only inside Lynx or when you specifically need its tracing GC, CDP debugger or Node-API layer on arm64 mobile; for raw interpreter throughput the current QuickJS release scored higher in the independent CI on both ubuntu and macOS arm64. Hermes (AOT bytecode for React Native) and Escargot are the other mobile-oriented choices in this category.

## Integration

| | |
|---|---|
| **Form** | static lib or source set built with gn and ninja (qjs_exe target for the shell); CMakeLists.txt files also exist for parts of the tree |
| **Dependencies** | Lynx build tooling (tools/envsetup.sh, hab sync) for third-party sources; LLVM-based generator only needed to regenerate embedded.S |
| **Minimum toolchain** | not documented; C++ built with Clang-style warning flags through the gn toolchain |
| **Platforms** | Template interpreter, snapshot and tracing GC: arm64 Android, iOS and macOS only. Elsewhere (Linux, x86-64) it builds the QuickJS-derived C interpreter with reference counting. Windows not documented (no Windows build in the ahaoboy CI). |
| **Thread safety** | not documented for the embedding API; gc.md says allocation has no lock contention because JavaScript is single-threaded, while marking and sweeping run on multiple GC worker threads |
| **Drop-in for the baseline** | partial: same engine lineage and API shape as QuickJS, but all symbols are renamed to LEPUS_\*, it implements ES2019 while current QuickJS has added many later features (Iterator helpers, set methods, Float16Array, RegExp v flag per its Changelog), and the speed features exist only on arm64 Android, iOS and macOS targets |

## Gotchas

- Stale baseline: docs/benchmark.md compares against QuickJS commit 6e2e68fd (authored 2024-07-27), before the QuickJS 2025-04-26, 2025-09-13 and 2026-06-04 releases; the 2026-06-04 Changelog lists 'micro optimizations (30% faster on bench-v8)' and a small-block allocator '(11% faster on bench-v8)', and the independent 2026 CI shows current QuickJS ahead of PrimJS overall even on macOS arm64 (1761 vs 1694).
- docs/template_interpreter.md describes QuickJS as a switch-based interpreter, but upstream quickjs.c sets DIRECT_DISPATCH 1 (computed-goto dispatch table) on every target except Emscripten, so the documented dispatch advantage over the baseline is overstated; the gain comes mostly from register pinning, stack caching and the GC.
- The benchmark document gives build args only for PrimJS; how the QuickJS baseline was built (flags, allocator, compiler) is not stated, the compiler is not named, and no Octane runner is checked in.
- Open correctness issues when read: #44 (`null ?? 3` returns null), #118 and #56 (stack underflow on real-world bundles), #406 (WeakMap entries kept alive); #413 (Android arm64 handlers generated for virtual-sp while ENABLE_VIRTUAL_STACK was off) was closed on 2026-09-22.

## Known shortcomings

- Downgraded A to C: first-party Octane table only, compiler not named, QuickJS build not described, no runner script; the template interpreter and tracing GC are on by default only for arm64 Android, iOS and macOS and off on Linux and x86-64. An independent ahaoboy CI shootout shows it slightly slower than QuickJS. QuickJS fork, filed under embedded-scripting where QuickJS is the baseline.
- Enricher: the baseline is a stale QuickJS commit 6e2e68 (2024-07-27); the independent ahaoboy CI, built with the same gn feature flags, has PrimJS at 1694 vs QuickJS 2026.06.04 at 1761 on macOS arm64 and 737 vs 1217 on ubuntu (config.gni compiles the template interpreter and tracing GC out off arm64 Android, iOS and macOS). template_interpreter.md calls QuickJS switch-based, but upstream quickjs.c uses DIRECT_DISPATCH 1 (computed goto). Open bug #44: 'null ?? 3' returns null; API renamed to LEPUS_\*.

## Caveats and trade-offs

First-party benchmark on one machine (Apple M1 Max, macOS) and one deprecated suite (Octane); compiler not named, QuickJS baseline build flags not given, no runner script in the repository. The speedups come from the template interpreter (embedded.S), snapshot, compatible memory management and tracing GC, which the README says are enabled by default only on arm64 targets with pre-generated embedded.S (Android, iOS, macOS) and stay disabled on Linux and non-arm64 targets, so the gain is not shown for x86-64 or Linux. Baseline is QuickJS, not V8 (the language-interpreters JS baseline); no memory or startup comparison. Built on QuickJS (MIT); the repository also carries MIT and BSD-3-Clause third-party code alongside Apache-2.0. [retier] First-party Octane 9 table (3735 vs 2904) against a stale QuickJS commit 6e2e68 from 2024-07-27, compiler unnamed, no runner script. Independent ahaoboy/js-engine-benchmark CI built with the same gn feature flags: PrimJS 1694 vs QuickJS 2026.06.04 1761 on macOS arm64 and 737 vs 1217 on ubuntu, so PrimJS is not faster than current QuickJS-NG; config.gni compiles the template interpreter and tracing GC out off arm64 Android, iOS and macOS. template_interpreter.md calls QuickJS switch-based, but upstream quickjs.c uses DIRECT_DISPATCH 1 (computed goto). Open bug #44 ('null ?? 3' returns null); API renamed to LEPUS_\*. QuickJS fork.

Built for Lynx: ES2019 only; replaces QuickJS reference counting with a tracing garbage collector; adds a template interpreter with stack caching and register optimizations plus snapshot support; Chrome DevTools Protocol integration. Not a standalone drop-in CLI.

## Maintenance

Actively developed by the Lynx team (commits through 2026-09-29), Apache-2.0 with QuickJS MIT code inside; usable mainly within Lynx-style arm64 mobile builds, and its headline gain rests on a 2024 QuickJS baseline that current QuickJS has overtaken.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): downgrade; tier before verification A, tier now C.
- **Tier reason:** First-party table in docs/benchmark.md: Octane scores for PrimJS vs QuickJS 6e2e68 on an Apple M1 Max with the PrimJS gn build args; the compiler is not named, the QuickJS build is not described and the repository has no Octane runner script, so it falls short of A and is first-party, hence C.
- **Verifier notes:** Numbers match docs/benchmark.md exactly; downgraded A to C because it is first-party with no compiler, no baseline build description and no runner script. Metadata checked: Apache-2.0, 1.1k stars, not a GitHub fork but built on QuickJS, last commit 2026-09-29 on develop. QuickJS is a listed baseline of the embedded-scripting category, which may be a better home for this entry.
- **Fields the verifier corrected:** `claimed_speedup`, `is_fork_of`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/lynx-family/primjs/HEAD/docs/benchmark.md>
  - <https://raw.githubusercontent.com/lynx-family/primjs/HEAD/README.md>
  - <https://raw.githubusercontent.com/lynx-family/primjs/HEAD/docs/template_interpreter.md>
  - <https://github.com/lynx-family/primjs>
  - <https://github.com/lynx-family/primjs/commits/develop>
  - <https://github.com/lynx-family/primjs/tree/develop/testing>
  - <https://github.com/lynx-family/primjs/tree/develop/docs>
- **Sources the enricher read:**
  - <https://github.com/lynx-family/primjs/commits/develop>
  - <https://github.com/lynx-family/primjs/issues?q=is%3Aissue>
  - <https://github.com/lynx-family/primjs/issues/28>
  - <https://github.com/lynx-family/primjs/issues/44>
  - <https://github.com/lynx-family/primjs/tree/develop/src/interpreter/primjs>
  - <https://github.com/lynx-family/primjs/tree/develop/src/interpreter/primjs/codegen>
  - <https://raw.githubusercontent.com/lynx-family/primjs/HEAD/README.md>
  - <https://raw.githubusercontent.com/lynx-family/primjs/HEAD/docs/benchmark.md>
  - <https://raw.githubusercontent.com/lynx-family/primjs/HEAD/docs/template_interpreter.md>
  - <https://raw.githubusercontent.com/lynx-family/primjs/HEAD/docs/gc.md>
  - <https://raw.githubusercontent.com/lynx-family/primjs/HEAD/BUILD.gn>
  - <https://raw.githubusercontent.com/lynx-family/primjs/HEAD/Primjs.gni>
  - <https://raw.githubusercontent.com/lynx-family/primjs/HEAD/config.gni>
  - <https://raw.githubusercontent.com/lynx-family/primjs/HEAD/.gn>
  - <https://raw.githubusercontent.com/lynx-family/primjs/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/lynx-family/primjs/HEAD/NOTICE>
  - <https://raw.githubusercontent.com/lynx-family/primjs/HEAD/src/interpreter/quickjs/include/quickjs.h>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/README.md>
  - <https://github.com/ahaoboy/primjs-build>
  - <https://raw.githubusercontent.com/ahaoboy/primjs-build/HEAD/build.sh>
  - <https://raw.githubusercontent.com/ahaoboy/primjs-build/HEAD/readme.md>
  - <https://github.com/bellard/quickjs/commit/6e2e68>
  - <https://github.com/bellard/quickjs/commit/6e2e68fd0896957f92eb6c242a2e048c1ef3cae0.patch>
  - <https://raw.githubusercontent.com/bellard/quickjs/HEAD/quickjs.c>
  - <https://raw.githubusercontent.com/bellard/quickjs/HEAD/Changelog>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/lynx-family/primjs`) · [data/wave12/enrich/raw/github_com_lynx_family_primjs.json](../../../data/wave12/enrich/raw/github_com_lynx_family_primjs.json) (enrichment confidence 0.8)

</details>
