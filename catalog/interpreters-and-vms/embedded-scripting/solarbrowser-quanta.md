# Quanta

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MPL-2.0` · 🟢 active

> Young C++20 JavaScript interpreter from the Solar browser project; 1.2-2.5x Duktape on v8-v7, but slower than QuickJS everywhere.

| | |
|---|---|
| **Beats** | Duktape 2.99.99 (unreleased master, built by ahaoboy/duktape-build with Duktape's development Makefile, which uses -Os -fomit-frame-pointer -g) on ubuntu/macos-arm64, Duktape 2.7.0 release (Makefile.cmdline) on windows; QuickJS 2026.06.04 is faster than Quanta in this suite |
| **Claimed result** | Score on Ubuntu 1068 vs Duktape 489; macOS arm64 1118 vs 905; Windows 941 vs 371 (about 2.2x, 1.2x and 2.5x, derived from page data). Versus QuickJS it is slower: 1068 vs 1217, 1118 vs 1761, 941 vs 1067. Results dated 2026-10-05. |
| **Workload** | V8 v7 benchmark suite combined score in the ahaoboy/js-engine-benchmark daily CI, which the Quanta README links as its performance evidence. |
| **Metric** | throughput |
| **Hardware** | GitHub Actions ubuntu-latest, macos-latest (arm64), windows-latest runners; CPU model not stated |
| **Adoption** | 26 stars, 3 forks; v1.0.0 release (dated September 28 on the releases page) |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/solarbrowser/quanta) · [benchmark](https://github.com/ahaoboy/js-engine-benchmark) |

## Verdict

In ahaoboy/js-engine-benchmark's daily GitHub Actions run (results dated 2026-10-05; CPU models not stated), the Quanta 1.0.0 release binary scored 1068 vs 489 for an -Os Duktape 2.99.99 on Ubuntu, 1118 vs 905 on macOS arm64 and 941 vs 371 against Duktape 2.7.0 on Windows (about 2.2x, 1.2x and 2.5x, derived from page data). QuickJS 2026.06.04 beat Quanta on every platform (1217, 1761, 1067).

## Use it when

- You are replacing Duktape in a desktop host on x86-64 Linux or Windows and want about 2.2-2.5x its v8-v7 score with modern syntax, and can accept a 5-8 MB binary.
- You are building a browser-like host that needs multiple realms per isolate, WindowProxy-style exotic objects, structured clone and host-driven module loading and timers, all of which Embed.h now exposes.
- Compute-style scripts close to QuickJS speed: on Ubuntu it edges QuickJS on DeltaBlue, Crypto, RayTrace and NavierStokes.
- MPL-2.0 (file-level copyleft) suits you better than LGPL, and you are comfortable tracking a fast-moving C++20 codebase.

## Skip it when

- When QuickJS is an option: QuickJS 2026.06.04 scored higher on every platform in the same suite (1217 vs 1068 Ubuntu, 1761 vs 1118 macOS arm64, 1067 vs 941 Windows) with a binary about one fifth the size.
- Allocation-heavy or long-lived-structure workloads: Quanta scores about half of QuickJS on Splay (1655 vs 3183 on Ubuntu) and well below on EarleyBoyer, and its own docs/internals/gc.md says a splay tree's garbage gets no help from minor collections.
- macOS arm64: only about 1.2x Duktape by score, losing Crypto, RegExp and Splay to Duktape, with the same 46 s wall time.
- Small or constrained devices and footprint-sensitive embedding: 5.3-8 MB executables against Duktape's 330-430 KB; Linux, macOS and Windows are the only documented platforms, and there is no Intl or Temporal yet (ICU4X and Temporal are on the roadmap).
- Production or untrusted code: v1.0.0 shipped on 2026-09-28, 26 stars, a single main author with AI-assisted commits, the embedding API was still gaining core features on 2026-10-04/05, and no fuzzing or security policy is documented.

## How it is fast

A register-based bytecode VM with hybrid switch/tail-call dispatch (since 0.9.2; the tree-walking interpreter was removed), NaN-boxed 8-byte values, shared immortal Shapes for objects, butterfly-style property storage, string slices as views and lazy function-body parsing. Memory comes from a non-moving, size-class-segregated cell heap (16 KB blocks in 1 MB chunks) with a sticky-mark-bit generational collector, a write-barrier remembered set and time-sliced majors, plus conservative stack scanning; non-GC memory goes through mimalloc and RegExp through PCRE2 with its JIT enabled. Default builds are clang -O3 -march=native with ThinLTO.

## Compared with alternatives

Pick Quanta over Duktape, njs or LibJS when you want a modern, faster-than-Duktape C++20 engine with a browser-oriented multi-realm embedding API; QuickJS is faster and smaller in the same suite, and Ant (about 1.8-2x QuickJS in the same suite) or Escargot (Intl/Temporal, wide platform support) are better picks when speed or maturity matter.

## Integration

| | |
|---|---|
| **Form** | static lib (build/lib/libquanta.a via ./build.sh lib or make lib, bundling PCRE2, utf8proc and mimalloc) plus a console executable; CMake build also available |
| **Dependencies** | vendored submodules: PCRE2 (BSD-3-Clause with exception, JIT on), utf8proc (MIT), mimalloc (MIT); no ICU |
| **Minimum toolchain** | C++20; clang and clang++ (CMake defaults to clang because its clang-only vectorisation flags break the C libraries under GCC; ThinLTO needs lld), CMake 3.15+ if using CMake; MSVC path in CMakeLists uses /std:c++20 |
| **Platforms** | Linux, macOS and Windows; release binaries for linux-x64, macos-arm64 and windows-x64. Default builds use -march=native; the Linux CI build uses -march=x86-64 -msse4.2 -mavx -mavx2 -mtune=haswell and the MSVC CMake path /arch:AVX2, so the CI and MSVC binaries require AVX2 (compiler and flags of the release assets are not documented) |
| **Thread safety** | One Isolate per thread, any number of Realms in it; everything allocated in an Isolate belongs to its creating thread and may not move to another; a second Isolate cannot be created while one is live on the same thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Benchmark asymmetry: the Duktape baseline is ahaoboy/duktape-build's -Os build of unreleased master 2.99.99 (2.7.0 on Windows), while Quanta's own builds use -O3, ThinLTO and -march=native or AVX2 flags; the release binary that was measured has no documented compiler or flags, and each engine ran the v8-v7 suite once per day on unspecified GitHub runner CPUs.
- The MSVC branch of CMakeLists.txt compiles with /fp:fast, although the clang branch deliberately excludes -ffast-math because it breaks IEEE 754 behaviour that JavaScript numbers require; prefer the clang build (build.sh or build-windows.bat) on Windows.
- C++ members of a native object do not keep JS cells alive; only its Visit() does, and roots are found by a conservative scan of the real stack, so ASan's use-after-return mode must stay off (the Makefile notes it caused live objects to be swept). The interpreter and runtime are compiled with -fno-stack-protector on purpose; only the lexer and parser keep -fstack-protector-strong.
- Values are NaN-boxed with pointers in the low 48 bits, and the RegExp engine is PCRE2 with JIT, so JavaScript RegExp execution does need executable memory even though the VM itself has no JIT.

## Known shortcomings

- Beats only the -Os Duktape baseline and is slower than QuickJS on ahaoboy/js-engine-benchmark; release-binary flags unknown, 26 stars (v1.0.0 released and measured, not pre-1.0 as the record said).
- Enricher: flag asymmetry (Duktape baseline -Os while Quanta builds -O3 with ThinLTO and -march=native/AVX2; release-binary flags undocumented), Splay about half of QuickJS (its own gc.md admits), the MSVC CMake path uses /fp:fast, PCRE2 JIT needs executable memory, the embedding API is still changing after 1.0, and Test262 is about 80% (snippet only).

## Caveats and trade-offs

Engines are prebuilt through the suite owner's \*-build repos or taken as release binaries (Quanta has no build repo in the suite's info.json, so its release binary's compiler and flags are unknown); CPU models are not stated (GitHub Actions runners) and each engine runs once per day with no variance reported. The v8-v7 suite is old and partly micro-benchmark. The Duktape baseline is an -Os build (unreleased master 2.99.99 on ubuntu/macOS). On macos-arm64 the margin is about 1.2x by score and Quanta loses 3 of 8 sub-benchmarks (Crypto 912 vs 1257, RegExp 215 vs 244, Splay 2074 vs 2594) with equal wall time (46 s each); on ubuntu and windows it wins all eight. Quanta trails QuickJS on every platform and is much larger (5.6 MB executable vs Duktape 370 KB and QuickJS 1 MB on ubuntu). Very young project (26 stars); v1.0.0 was released shortly before this snapshot; the README links the same third-party daily benchmark and lists no numbers of its own. MPL-2.0 is file-level copyleft; bundled PCRE2 (BSD-3-Clause with exception, used for RegExp), mimalloc (MIT) and utf8proc (MIT plus the Unicode data licence) as submodules.

Experimental ECMAScript engine with an embedding API (recent commits add host-hook module loading and DefineGlobalFunction). Binary 5.6M on Ubuntu vs Duktape 370K and QuickJS 1M.

## Maintenance

Very active (dozens of commits on 2026-10-04/05, v1.0.0 tagged 2026-09-28) and copyable under MPL-2.0 with permissive bundled dependencies, but experimental: a web snippet from the Solar browser site (snippet only, page blocked) says it passes about 80% of test262, and the embedding API is still changing.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party CI shootout (ahaoboy/js-engine-benchmark; v8-v7 suite code in v8-v7/, driver scripts/update.ts, results 10/5/2026) shows quanta Score 1068/1118/941 vs Duktape 489/905/371 on ubuntu/macos-arm64/windows; not A because the runners' CPU models are not stated and Quanta is taken as a prebuilt release binary whose compiler and flags are not given. B matches the ChakraCore and v8 verdicts on the same suite.
- **Verifier notes:** Numbers match the README tables exactly (quanta 1068/1118/941, duktape 489/905/371, quickjs 1217/1761/1067). Record said 'still pre-1.0'; corrected: v1.0.0 is released and is the version measured. Main shortcomings: -Os Duktape baseline, mixed macOS sub-results, slower than QuickJS, unknown release-binary flags.
- **Fields the verifier corrected:** `baseline`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ahaoboy/js-engine-benchmark>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/scripts/update.ts>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/info.json>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/.github/workflows/update.yml>
  - <https://raw.githubusercontent.com/ahaoboy/duktape-build/HEAD/build.sh>
  - <https://raw.githubusercontent.com/svaarala/duktape/HEAD/Makefile>
  - <https://github.com/solarbrowser/quanta>
  - <https://github.com/solarbrowser/quanta/commits/main>
  - <https://github.com/solarbrowser/quanta/releases>
  - <https://raw.githubusercontent.com/solarbrowser/quanta/HEAD/README.md>
  - <https://raw.githubusercontent.com/solarbrowser/quanta/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/solarbrowser/quanta/HEAD/NOTICE.md>
  - <https://raw.githubusercontent.com/solarbrowser/quanta/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/solarbrowser/quanta>
  - <https://github.com/solarbrowser/quanta/commits/main>
  - <https://github.com/solarbrowser/quanta/releases>
  - <https://github.com/solarbrowser/quanta/releases/expanded_assets/v1.0.0>
  - <https://github.com/solarbrowser/quanta/issues?q=is%3Aissue>
  - <https://github.com/solarbrowser/quanta/issues/2>
  - <https://github.com/solarbrowser/quanta/tree/main/docs>
  - <https://github.com/solarbrowser/quanta/tree/main/.github/workflows>
  - <https://raw.githubusercontent.com/solarbrowser/quanta/HEAD/README.md>
  - <https://raw.githubusercontent.com/solarbrowser/quanta/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/solarbrowser/quanta/HEAD/NOTICE.md>
  - <https://raw.githubusercontent.com/solarbrowser/quanta/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/solarbrowser/quanta/HEAD/Makefile>
  - <https://raw.githubusercontent.com/solarbrowser/quanta/HEAD/build.sh>
  - <https://raw.githubusercontent.com/solarbrowser/quanta/HEAD/.github/workflows/build-linux.yml>
  - <https://raw.githubusercontent.com/solarbrowser/quanta/HEAD/.github/workflows/build-macos.yml>
  - <https://raw.githubusercontent.com/solarbrowser/quanta/HEAD/.github/workflows/build-windows.yml>
  - <https://raw.githubusercontent.com/solarbrowser/quanta/HEAD/docs/README.md>
  - <https://raw.githubusercontent.com/solarbrowser/quanta/HEAD/docs/embedding/README.md>
  - <https://raw.githubusercontent.com/solarbrowser/quanta/HEAD/docs/contributing/building.md>
  - <https://raw.githubusercontent.com/solarbrowser/quanta/HEAD/docs/internals/memory.md>
  - <https://raw.githubusercontent.com/solarbrowser/quanta/HEAD/docs/internals/representation.md>
  - <https://raw.githubusercontent.com/solarbrowser/quanta/HEAD/docs/internals/gc.md>
  - <https://github.com/ahaoboy/js-engine-benchmark/issues/45>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/info.json>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/scripts/update.ts>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/.github/workflows/update.yml>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/solarbrowser/quanta`) · [data/wave12/enrich/raw/github_com_solarbrowser_quanta.json](../../../data/wave12/enrich/raw/github_com_solarbrowser_quanta.json) (enrichment confidence 0.7)

</details>
