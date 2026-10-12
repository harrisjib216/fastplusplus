# ChakraCore

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🟢 active

> Microsoft's former Edge JavaScript engine with a flat C API; a JIT engine about 16-26x QuickJS on Octane v8-v7.

| | |
|---|---|
| **Beats** | QuickJS (and Duktape in the same table) |
| **Claimed result** | Suite score: ChakraCore 19392 vs QuickJS 1217 on ubuntu, 27267 vs 1067 on windows (derived from page data: about 16x and 26x). |
| **Workload** | Octane/v8-v7 subset run by CI with a standalone ChakraCore build (ubuntu and windows only; macOS arm64 not supported). |
| **Metric** | throughput |
| **Hardware** | CI runners (ubuntu, macos-arm64, windows sections of the README, results dated 10/5/2026); CPU model not stated |
| **Compiler and flags** | Not stated on the page. The ubuntu binary comes from ahaoboy/ChakraCore-build build.sh, which clones ChakraCore at HEAD (depth 1), runs ChakraCore's default ./build.sh and copies out/Release/ch (Release build; compiler and flags not stated). The windows column is version 1.11.24.0, provenance not checked. |
| **Adoption** | 9.3k stars |
| **Last commit** | 2026-02-19 |
| **Links** | [repository](https://github.com/chakra-core/ChakraCore) · [benchmark](https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/README.md) |

## Verdict

In ahaoboy/js-engine-benchmark (Octane v8-v7 subset forked from Mozilla's arewefastyet, run 10/5/2026 on GitHub-hosted ubuntu-latest and windows-latest runners, CPU not stated, one run per engine), ChakraCore scored 19392 vs QuickJS 2026-06-04 1217 on Ubuntu (master 1.13.0.0-beta, clang Release build) and 27267 vs 1067 on Windows (Microsoft's NuGet 1.11.24 binary). Duktape scored 489 and 371 in the same runs.

## Use it when

- A C or C++ host on x64 Linux or Windows that needs JIT-level JavaScript throughput (about 16x QuickJS on Ubuntu, 26x on Windows in this shootout) behind a stable flat C API rather than V8's C++ API.
- Compute-heavy scripts (Crypto, NavierStokes, Richards in the suite run at 23-36k points versus 0.9-1.9k for QuickJS) where a 19 MB engine footprint is acceptable.
- Windows hosts that want a prebuilt, MIT-licensed engine: Microsoft's NuGet package (Microsoft.ChakraCore.vc140 1.11.24) is what produced the 27267 Windows score.
- Hosts that need control over threading: JIT and GC can run on background threads or be forced onto the host thread (JsRuntimeAttributeDisableBackgroundWork), and hosts can supply their own thread service.

## Skip it when

- Peak throughput matters most: V8 scores 48107 vs 19392 on Ubuntu (about 2.5x) and 46932 vs 27267 on Windows in the same run.
- macOS on Apple Silicon: the build fails to detect the target processor (issue #6860, open since 2022-11-09) and the shootout has no macOS arm64 build; README lists x86 and ARM only for Windows.
- Security-sensitive embedding of untrusted code: Microsoft's security updates for 1.11 ended 2021-03-09, there has been no tagged release since v1.11.24, and master is a community 1.13.0.0-beta; JIT engines carry a larger attack surface (a --no-jit build option exists).
- Small footprint or new language features: the Ubuntu build totals about 19.3 MB versus about 1 MB for QuickJS, and no community release documents ES2020+ feature support.
- GC- and allocation-heavy scripts on the Linux master build: EarleyBoyer scored 7048 on Ubuntu versus 39201 for the Windows 1.11.24 build (V8 is flat across the two OSes), so expect uneven results on Linux.

## How it is fast

Multi-tier execution: deferred parsing, a bytecode interpreter that records type and call-count profiles, then a background JIT thread that promotes hot functions and loop bodies first to SimpleJit and then to FullJit optimized code, with bailout to the interpreter on mis-speculation. Memory is managed by the Recycler, a generational mark-and-sweep collector with concurrent and partial collections on a background thread. The gap over QuickJS and Duktape in the shootout is the JIT-versus-interpreter gap.

## Compared with alternatives

Pick ChakraCore over QuickJS when you need JIT throughput on x64 (16-26x here) and can afford about 19 MB, and over V8 or SpiderMonkey when a flat, stable C API and a smaller binary (19.3 MB vs 66 MB for V8 and 40.8 MB for SpiderMonkey on Ubuntu) matter more than V8's 2.5x higher score. Prefer V8 for peak speed and ongoing security support, and QuickJS or Escargot for small footprint, ARM and macOS.

## Integration

| | |
|---|---|
| **Form** | shared lib (default libChakraCore.so/.dylib/.dll) or static lib (build.sh --static) |
| **Dependencies** | ICU for Unicode and Intl (system ICU by default, --embed-icu to download and link it statically, or --no-icu to drop Intl); build needs clang, CMake 3.10+, and ninja or make on Linux/macOS; Visual Studio on Windows; also on vcpkg (chakracore) |
| **Minimum toolchain** | C++17 (CMake sets CMAKE_CXX_STANDARD 17 after the Dec 2025 refactor #7038); clang on Linux/macOS (build.sh requires clang++); the README's Visual Studio 2015/2017 note predates the C++17 move |
| **Platforms** | x64 Linux, macOS and Windows; x86 and ARM on Windows; Linux ARM64 build fixes landed Jan 2026 but support is not documented in the README; macOS arm64 not supported (issue #6860) |
| **Thread safety** | Rental threading: a runtime is single-threaded and can be active on only one thread at a time, but an idle runtime can move to another thread; each runtime starts background JIT and GC threads unless JsRuntimeAttributeDisableBackgroundWork is set. |
| **Drop-in for the baseline** | no |

## Gotchas

- The two shootout columns are different code: Ubuntu runs a stripped master build (1.13.0.0-beta, ahaoboy/ChakraCore-build: depth-1 clone, default ./build.sh Release with clang, -msse4.2, shared library, JIT on), while Windows runs Microsoft's official NuGet Microsoft.ChakraCore.vc140 1.11.24 binary (Dec 2020 release).
- Harness: scripts/update.ts runs each engine once, in sequence, on one GitHub-hosted runner and records that single v8-v7 score; there are no repetitions or variance figures, so small gaps (ChakraCore 19392 vs SpiderMonkey 19137 on Ubuntu) are within noise.
- Linux anomaly: the Ubuntu master build scores 7048 on EarleyBoyer and 18100 on Splay versus 39201 and 27259 for the Windows build, while other engines are flat across OSes; the cause is not documented, but it accounts for much of the lower Ubuntu total.
- JSRT error model: after a script throws, the runtime is in an exception state and every API call fails with JsErrorInExceptionState until the host calls JsGetAndClearException; values kept outside the GC heap must be pinned with JsAddRef/JsRelease.

## Known shortcomings

- A JIT compared against an interpreter (19392 vs QuickJS 1217 on ubuntu, 27267 vs 1067 on windows) on CI runners with no CPU model or flags; V8 is about 2.5x faster, the binary is 19.3 MB, and the benchmark suite has 59 stars.
- Enricher: the two ahaoboy columns run different code (ubuntu: master 1.13.0.0-beta clang Release build; windows: the Microsoft NuGet Microsoft.ChakraCore.vc140 1.11.24 binary from December 2020); scripts/update.ts runs each engine once with no repeats or variance, and the EarleyBoyer anomaly (7048 ubuntu vs 39201 windows while V8 is flat) is undocumented. No release since v1.11.24, macOS arm64 still open (#6860).

## Caveats and trade-offs

Third-party shootout run by CI on GitHub-hosted runners (results dated 10/5/2026); CPU model, compiler and flags are not stated and engine binaries come from per-engine build repos (ahaoboy/ChakraCore-build, 0 stars), so this is tier B rather than A. The suite is a small independent project (59 stars). It compares a JIT engine against interpreters: ChakraCore's win over QuickJS (19392 vs 1217 ubuntu, 27267 vs 1067 windows) and Duktape (19392 vs 489 ubuntu) is the JIT-vs-interpreter gap, and it costs size (19.3M total vs 1M for QuickJS on ubuntu). Among embeddable JIT engines it is not the fastest: V8 scores 48107 on ubuntu (about 2.5x ChakraCore, derived from page data), and ChakraCore is not built for macOS arm64 in this suite. Community-maintained since Microsoft ended support of 1.11 on 2021-03-09; commits are sparse (latest 2026-02-19). Different versions per OS (1.13.0.0.beta on ubuntu, 1.11.24.0 on windows).

README describes it as a JavaScript engine with a C API for adding JavaScript to C-compatible projects; JIT engine with a larger footprint than QuickJS (ubuntu listing about 19.3M total); macOS arm64 build is marked unsupported in the shootout.

## Maintenance

Community-maintained with a handful of commits per quarter (latest 2026-02-19: CI, clang and Linux ARM64 build fixes) but no tagged release since v1.11.24 (Dec 2020) and no Microsoft security support since 2021-03-09; MIT-licensed and buildable from source or via vcpkg, so copyable for x64 hosts that accept the security posture.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party shootout (ahaoboy/js-engine-benchmark) with public harness code (v8-v7/, forked from mozilla arewefastyet) runs ChakraCore, QuickJS and Duktape on GitHub-hosted CI runners; CPU model, compiler and flags are not stated, so it falls short of A. The suite is small (59 stars), but it is independent of ChakraCore, which keeps it at B under the independent-measurement rule.
- **Verifier notes:** Numbers are in ChakraCore's own column of the shared table on all three listed rows (ubuntu Score 19392, windows Score 27267; QuickJS 1217 and 1067). Metadata checked on github.com: MIT, 9.3k stars, last commit 2026-02-19, not archived. Shortcoming to record: JIT-vs-interpreter comparison, slower than V8 by about 2.5x, large binary, unstated CPU and flags.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/README.md>
  - <https://github.com/ahaoboy/js-engine-benchmark>
  - <https://github.com/ahaoboy/ChakraCore-build>
  - <https://raw.githubusercontent.com/ahaoboy/ChakraCore-build/HEAD/build.sh>
  - <https://github.com/chakra-core/ChakraCore>
  - <https://github.com/chakra-core/ChakraCore/commits/master>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/chakra-core/ChakraCore/HEAD/README.md>
  - <https://raw.githubusercontent.com/chakra-core/ChakraCore/HEAD/build.sh>
  - <https://raw.githubusercontent.com/chakra-core/ChakraCore/HEAD/CMakeLists.txt>
  - <https://github.com/chakra-core/ChakraCore/wiki/Architecture-Overview>
  - https://github.com/chakra-core/ChakraCore/wiki/JavaScript-Runtime-(JSRT)-Overview
  - <https://github.com/chakra-core/ChakraCore/commits/master>
  - <https://github.com/chakra-core/ChakraCore/releases>
  - <https://github.com/chakra-core/ChakraCore/issues/6860>
  - <https://github.com/chakra-core/ChakraCore/issues?q=is%3Aissue+performance+linux>
  - <https://github.com/chakra-core/ChakraCore/issues/2299>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/README.md>
  - <https://github.com/ahaoboy/js-engine-benchmark>
  - <https://github.com/ahaoboy/js-engine-benchmark/tree/main/scripts>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/scripts/update.ts>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/scripts/build.ts>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/scripts/test.js>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/info.json>
  - <https://github.com/ahaoboy/js-engine-benchmark/tree/main/.github/workflows>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/.github/workflows/update.yml>
  - <https://github.com/ahaoboy/js-engine-setup>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-setup/HEAD/action.yml>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-setup/HEAD/info.json>
  - <https://github.com/ahaoboy/ChakraCore-build>
  - <https://raw.githubusercontent.com/ahaoboy/ChakraCore-build/HEAD/readme.md>
  - <https://raw.githubusercontent.com/ahaoboy/ChakraCore-build/HEAD/build.sh>
  - <https://raw.githubusercontent.com/ahaoboy/ChakraCore-build/HEAD/.github/workflows/build.yml>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/chakra-core/chakracore`) · [data/wave12/enrich/raw/github_com_chakra_core_chakracore.json](../../../data/wave12/enrich/raw/github_com_chakra_core_chakracore.json) (enrichment confidence 0.75)

</details>
