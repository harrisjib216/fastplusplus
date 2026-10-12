# Escargot

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `LGPL-2.1` · 🟢 active

> Samsung's embeddable no-JIT JavaScript interpreter (ES2026, Intl, Temporal); about 1.2-1.3x QuickJS speed on ARM64 suites, with lower RSS on large workloads.

| | |
|---|---|
| **Beats** | QuickJS (Bellard release 2026-06-04); the same dashboard also runs V8 d8 and V8 --jitless |
| **Claimed result** | Samsung CI dashboard latest.json (2026-06-04) vs QuickJS: Octane 1.19x (single run), SunSpider 1.30x, Web Tooling 1.20x; the Web Tooling gain rests on the coffeescript subtest alone (QuickJS 0.05 vs Escargot 0.86 runs/s), without which it is about 1.02x with Escargot losing 7 of 18 tests (derived from page data). Loses Splay (1147 vs 2353) and SplayLatency (1872 vs 5405); V8 --jitless is faster on all three suites. |
| **Workload** | SunSpider (26 scripts), Octane (18 benchmark functions) and Web Tooling Benchmark (18 functions) run in each engine's shell on one pinned CPU core of an ARM64 host; execution scores and fixed-work memory (RSS from smaps_rollup, median of 3 fresh processes) measured separately |
| **Metric** | throughput |
| **Hardware** | aarch64 Linux 6.8.0-1063-aws, 16 cores, Arm CPU implementer 0x41 part 0xd0c (Neoverse N1 class, an AWS Graviton2-type host, inferred from the CPU part id and kernel), engine pinned to one core with taskset and the memory monitor on another |
| **Compiler and flags** | Escargot built by tools/monthly-engine-benchmark.py with CMake -DCMAKE_BUILD_TYPE=Release -DESCARGOT_DEPLOY=ON -DESCARGOT_THREADING=ON -DESCARGOT_TCO=ON -DESCARGOT_ENABLE_SHELL=ON (Ninja) into out/monthly-engine-release-arm64; QuickJS 2026-06-04 built from the official tarball with its own Makefile ('make qjs', upstream default -O2) and run as 'qjs --std --stack-size 8388608'; compiler and version not recorded; glibc 2.39 runtime for all engines. |
| **Adoption** | 364 stars; 'used in shipping products' (Samsung, per README) |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/Samsung/escargot) · [benchmark](https://raw.githubusercontent.com/Samsung/escargot/gh-pages/performance/monthly/latest.json) |

## Verdict

Escargot's own monthly CI dashboard (2026-10-04, commit fc608b59b, CMake Release -O2 with TCO on) against QuickJS 2026-06-04 built with its Makefile, on one pinned core of an AWS Neoverse-N1 (Arm part 0xd0c) aarch64 host with a shared glibc 2.39 runtime: SunSpider 823.2 vs 981.6 ms (wins 21 of 26 tests), Octane 2198 vs 1689 (wins 15 of 17 sub-scores, loses Splay and SplayLatency), Web Tooling 1.07 vs 0.89 runs/s (about 1.02x without the coffeescript outlier). Fixed-work memory (median of 3 processes) favours Escargot on Octane and Web Tooling and QuickJS on SunSpider.

## Use it when

- You need modern JavaScript (ES2026 with Intl and Temporal) on a device or store where JIT is not allowed or not affordable: iOS apps, Tizen and Android products, embedded Linux, FreeRTOS or NuttX on Cortex-M.
- Large or long-running scripts (bundled apps, parsers, compilers) where QuickJS's RSS grows: on the fixed-work ARM64 runs Escargot averaged 85.7 MiB vs 161.4 MiB on Octane and 171.6 MiB vs 375.9 MiB on Web Tooling.
- CPU-bound interpreter work where a 1.2-1.3x gain over QuickJS on ARM64 matters and a C++ embedding API (or Node-API addon compatibility) is wanted.
- You want lower memory than V8 --jitless: Escargot used less RSS than d8 --jitless on all three suites (SunSpider 14.2 vs 40.7 MiB, Octane 85.7 vs 152.8, Web Tooling 171.6 vs 265.8).

## Skip it when

- Small scripts and tiny footprints: on SunSpider QuickJS averaged 5.3 MiB RSS vs Escargot's 14.2 MiB, and QuickJS has no ICU dependency.
- GC-latency-sensitive workloads: Escargot scored less than half of QuickJS on Octane Splay (1147 vs 2353) and SplayLatency (1872 vs 5405); its collector is a conservative, non-moving bdwgc.
- Untrusted or hostile scripts: the README says the project assumes valid JavaScript only, and 2026 reports include a type confusion in InterpreterSlowPath::initializeClassOperation, heap-buffer-overflows and an ArrayBuffer.prototype.transfer TOCTOU null dereference.
- Peak speed: V8 d8 --jitless (also no JIT) beat it on all three suites (SunSpider 694.6 vs 823.2 ms, Octane 2300 vs 2198, Web Tooling 2.02 vs 1.07 runs/s), and full V8 is about 11x on Octane.
- Proprietary products that cannot meet LGPL-2.1 obligations: the default artefact is a static library, so static linking requires providing relinkable objects.

## How it is fast

Source is compiled to a register-based bytecode run by a computed-goto (threaded) dispatch loop, with inline caches for property gets and instanceof and shared object-structure transitions (hidden-class style). Memory is managed by a vendored Boehm-Demers-Weiser conservative collector (third_party/GCutil, thread-isolated heaps), with optional 32-bit-in-64-bit pointer compression and code and string compression aimed at keeping RSS low (the project's Software: Practice and Experience 2023 paper covers dynamic code compression). The v5.0.3 release notes list cutting temporary allocations, streaming UTF-8 sources through bounded parser windows and specialising TypedArray indexed access.

## Compared with alternatives

Pick Escargot over QuickJS when you need Intl/Temporal and run large scripts where its lower RSS on Octane and Web Tooling matters, and over Hermes when you must run plain JavaScript source rather than precompiled bytecode; pick QuickJS (or MicroQuickJS) for the smallest footprint, MIT licensing and short scripts, and Ant or PrimJS if raw interpreter speed over QuickJS matters more than ICU-backed standards coverage.

## Integration

| | |
|---|---|
| **Form** | static lib (libescargot.a by default; shared library with ESCARGOT_BUILD_SHARED_LIBS=ON), built with CMake |
| **Dependencies** | vendored bdwgc (third_party/GCutil submodule); ICU for Intl/Temporal (system ICU via dlopen on Linux, vendored ICU on macOS/iOS, vcpkg or Windows ICU on Windows, or disabled); optional vendored WABT for WebAssembly; Python 3 at build time |
| **Minimum toolchain** | CMake 2.8.12+; GCC or Clang compiling with -std=c++11 on Linux (C++17 on macOS and MSVC); Visual Studio 2022 (MSVC v143) in the Windows example; exact minimum compiler versions not documented |
| **Platforms** | Linux x86/x64/arm/aarch64/riscv64, Android, Tizen, macOS x64/arm64, iOS arm64 (simulator run in CI, device build-only), Windows x86/x64/arm64 (no WebAssembly on arm64), FreeRTOS/NuttX on Cortex-M |
| **Thread safety** | Globals::initialize once per process, then Globals::initializeThread/finalizeThread on each thread that uses the engine; bdwgc is built with GC_THREAD_ISOLATE so each thread has its own heap; sharing one VM instance across threads is not documented beyond the cross-thread job hooks |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness finding: the Web Tooling headline (1.07 vs 0.89 runs/s geomean, about 1.20x) rests on one subtest, coffeescript, where QuickJS ran at 0.05 runs/s against Escargot's 0.86 and V8 --jitless's 2.77 (confirmed in the run's raw quickjs-web_tooling.log). Without it the geomean ratio is about 1.02x (1.083 vs 1.059, derived from page data), and Escargot loses 7 of 18 Web Tooling subtests (babel, babel-minify, buble, chai, jshint, postcss, prepack).
- Measurement depth is thin outside SunSpider: Octane is one scored run, and Web Tooling's minSamples was patched from 20 to 3 by the harness; no variance is reported for either. SunSpider is the mean of 5 fresh processes (Escargot 809-830 ms, QuickJS 979-986 ms).
- The dashboard binary is built with -DESCARGOT_TCO=ON, which is off by default, and the Release flags are -O2 -fno-stack-protector -fno-omit-frame-pointer; the compiler version is not recorded. ESCARGOT_SMALL_CONFIG's -Os has a known memory conflict with newer GCC (issue #1480), so it is only applied for GCC 9 and older.
- Conservative GC: host objects that hold JS values must be allocated with Memory::gcMalloc (or registered), stack scanning can retain dead objects, and the README asks for vulnerability reports through public issues (issue #1662 asks how to report privately).

## Known shortcomings

- First-party CI dashboard (latest.json, 1.19x/1.30x/1.20x over QuickJS, 2026-06-04) with the compiler not recorded; V8 --jitless is faster on all 3 suites and Escargot uses more memory than QuickJS on SunSpider.
- Enricher: the Web Tooling 1.20x gain rests on one subtest (coffeescript: QuickJS 0.05 vs Escargot 0.86 runs/s, confirmed in the raw quickjs-web_tooling.log); without it the gain is about 1.02x and Escargot loses 7 of 18 WTB tests. Octane is a single run, WTB minSamples was patched from 20 to 3, the build uses non-default TCO=ON, and Escargot loses Splay and SplayLatency (1147 vs 2353, 1872 vs 5405). README says valid JavaScript only; 2026 fuzzing found memory-safety bugs.

## Caveats and trade-offs

First-party dashboard published by the Escargot project from its own CI runner; the harness and raw JSON are public but the compiler is not recorded, so capped at tier C. QuickJS uses less memory than Escargot on SunSpider (5.3 vs 14.2 MiB average RSS), so the memory advantage only holds on the larger Octane and Web Tooling workloads. The score gains over QuickJS are 20-30%, not an order of magnitude. On the same dashboard V8 d8 --jitless (also no JIT) is faster than Escargot on all three suites (SunSpider 694.6 ms, Octane 2300, Web Tooling 2.02 runs/s), though it uses more memory (Octane 152.8 MiB, Web Tooling 265.8 MiB average RSS); full d8 with JIT is roughly 11x Escargot on Octane. A prebuilt ARM32 dashboard exists too but was not opened. The pretty dashboard on samsung.github.io was not reachable; numbers were read from the gh-pages branch file latest.json.

Bytecode interpreter with no JIT and no executable memory needed; targets ECMAScript 2026 with ICU-backed Intl and Temporal (ICU dependency or bundle adds size); C++ embedding API plus optional Node-API layer; LGPL-2.1 licence.

## Maintenance

Very active (commits through 2026-10-06, release tag v5.0.3, shipped in Samsung Tizen products) and copyable under LGPL-2.1, but treat it as a trusted-code engine: fuzzing reports of memory-safety bugs were still arriving in mid-2026.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party dashboard from the Escargot project's own self-hosted ARM64 runner; the harness (tools/monthly-engine-benchmark.py via .github/workflows/monthly-engine-benchmark.yml) and raw JSON are public and the CPU is identifiable from cpu_info (Arm part 0xd0c), but the compiler and version are not recorded, so it is not A, and first-party numbers with partial methodology stay at C.
- **Verifier notes:** All speed and fixed-work memory numbers in the record match latest.json (measured 2026-10-04, Escargot fc608b59b); harness and build options are public in tools/monthly-engine-benchmark.py. Shortcomings: first-party CI dashboard, compiler not recorded, only 1.2-1.3x over QuickJS, loses to V8 --jitless on speed, uses more memory than QuickJS on SunSpider.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `caveats`, `claimed_speedup`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Samsung/escargot/gh-pages/performance/monthly/latest.json>
  - <https://github.com/Samsung/escargot>
  - <https://github.com/Samsung/escargot/commits/master>
  - <https://github.com/Samsung/escargot/tree/master/.github/workflows>
  - <https://raw.githubusercontent.com/Samsung/escargot/HEAD/README.md>
  - <https://raw.githubusercontent.com/Samsung/escargot/HEAD/.github/workflows/monthly-engine-benchmark.yml>
  - <https://raw.githubusercontent.com/Samsung/escargot/HEAD/tools/monthly-engine-benchmark.py>
  - <https://raw.githubusercontent.com/bellard/quickjs/HEAD/Makefile>
- **Sources the enricher read:**
  - <https://github.com/Samsung/escargot>
  - <https://github.com/Samsung/escargot/issues>
  - <https://github.com/Samsung/escargot/issues?q=is%3Aissue%20state%3Aclosed%20crash>
  - <https://github.com/Samsung/escargot/releases>
  - <https://raw.githubusercontent.com/Samsung/escargot/HEAD/README.md>
  - <https://raw.githubusercontent.com/Samsung/escargot/gh-pages/performance/monthly/latest.json>
  - <https://raw.githubusercontent.com/Samsung/escargot/gh-pages/performance/monthly/raw/2026-10-04-fc608b59b.zip>
  - <https://raw.githubusercontent.com/Samsung/escargot/HEAD/tools/monthly-engine-benchmark.py>
  - <https://raw.githubusercontent.com/Samsung/escargot/HEAD/.github/workflows/monthly-engine-benchmark.yml>
  - <https://raw.githubusercontent.com/Samsung/escargot/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Samsung/escargot/HEAD/build/target.cmake>
  - <https://raw.githubusercontent.com/Samsung/escargot/HEAD/build/config.cmake>
  - <https://raw.githubusercontent.com/Samsung/escargot/HEAD/build/escargot.cmake>
  - <https://raw.githubusercontent.com/Samsung/escargot/HEAD/src/api/EscargotPublic.h>
  - <https://raw.githubusercontent.com/Samsung/escargot/HEAD/src/interpreter/ByteCodeInterpreter.cpp>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/samsung/escargot`) · [data/wave12/enrich/raw/github_com_samsung_escargot.json](../../../data/wave12/enrich/raw/github_com_samsung_escargot.json) (enrichment confidence 0.8)

</details>
