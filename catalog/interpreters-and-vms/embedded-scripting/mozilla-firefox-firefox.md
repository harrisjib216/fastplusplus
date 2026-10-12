# SpiderMonkey (Mozilla)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MPL-2.0` · 🟢 active

> Mozilla's Firefox JavaScript and WebAssembly engine, embeddable through the C++ JSAPI; its JIT tiers score about 16x QuickJS on v8-v7.

| | |
|---|---|
| **Beats** | QuickJS 2026-06-04 (also Duktape 2.99.99 on Ubuntu and macOS, 2.7.0 on Windows) |
| **Claimed result** | v8-v7 Score (higher is better), ubuntu / macos-arm64 / windows: SpiderMonkey 147.0 19137 / 25455 / 19049 vs QuickJS 2026.06.04 1217 / 1761 / 1067 vs Duktape 489 / 905 / 371. About 15.7x QuickJS and 39x Duktape on ubuntu (derived from page data). Wall time for the whole suite on ubuntu: SpiderMonkey 20 s, QuickJS 37 s, Duktape 70 s. Score per MB of binary on ubuntu is lower than the small interpreters (468/M vs QuickJS 1190/M and Duktape 1352/M). |
| **Workload** | V8 v7 benchmark suite (Richards, DeltaBlue, Crypto, RayTrace, EarleyBoyer, RegExp, Splay, NavierStokes) combined score for SpiderMonkey shell 147.0 vs other engines, run by a daily GitHub Actions workflow on three operating systems. |
| **Metric** | throughput |
| **Hardware** | GitHub Actions ubuntu-latest, macos-latest (arm64) and windows-latest runners; CPU model not stated |
| **Compiler and flags** | SpiderMonkey is Mozilla's official prebuilt jsshell zip (archive.mozilla.org/pub/firefox/releases/&lt;latest development version&gt;/jsshell/), fetched by ahaoboy/spidermonkey-build download.sh, so it is Mozilla's release build; QuickJS and Duktape come from the suite owner's quickjs-build and duktape-build repos via the ahaoboy/js-engine-setup action (strip: true); compiler and flags for those builds are not stated on the benchmark page. |
| **Adoption** | 13.4k stars (mozilla-firefox/firefox); embedded via the SpiderMonkey C++ API (mozjs, spidermonkey-embedding-examples) |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/mozilla-firefox/firefox) · [benchmark](https://github.com/ahaoboy/js-engine-benchmark) |

## Verdict

ahaoboy/js-engine-benchmark runs the v8-v7 suite (8 suites, geometric-mean Score) once per engine per day on GitHub-hosted ubuntu, macos-arm64 and windows runners (CPU not stated); in the 10/5/2026 snapshot Mozilla's prebuilt jsshell 147.0 scored 19137 / 25455 / 19049 against QuickJS 2026-06-04 at 1217 / 1761 / 1067 (about 15.7x, 14.5x and 17.9x, derived from page data) and Duktape at 489 / 905 / 371. SpiderMonkey uses Mozilla's release-build flags; QuickJS and Duktape come from the suite owner's build repos with flags not stated on the page.

## Use it when

- A C++ host that runs long or compute-heavy scripts and needs JIT throughput: 19137 vs QuickJS 1217 on Ubuntu, with per-test gains of 16-22x on Richards, DeltaBlue, Crypto, RayTrace, EarleyBoyer and RegExp (Splay 6.9x, NavierStokes 11x; derived from page data).
- Products that want an engine with a long-lived API: Mozilla publishes yearly ESR branches with security backports and recommends embedders track them; Linux distributions package mozjs-140, so hosts there can skip the source build.
- Hosts on x86, x86-64, ARM, AArch64, MIPS64, LoongArch64 or RISC-V64 (the JIT is on by default for these in js/moz.configure), or on JIT-less targets such as wasm32-wasi, where the Portable Baseline Interpreter still gives IC-based speed-ups without codegen.
- Multi-threaded hosts that can give each thread its own JSContext tied to the main runtime (worker.cpp example) and share compiled scripts across threads with Stencils (stencils.cpp).
- MPL-2.0 is acceptable: SpiderMonkey sources carry per-file MPL 2.0 headers (e.g. js/src/jsapi.h), so a proprietary host can link the library while changes to SpiderMonkey's own files stay open; the repository LICENSE points to toolkit/content/license.html for bundled third-party licences.

## Skip it when

- Peak throughput: V8 scores 48107 vs 19137 on Ubuntu (about 2.5x) and wins every sub-test; JavaScriptCore scores 45928 in the same run.
- Small footprint: the Ubuntu shell is 40.8 MB vs about 1 MB for QuickJS and 370 KB for Duktape, so score per MB is 468 vs 1190 and 1352; the build drags in the Firefox tree, Rust, Python-driven configure and ICU.
- Short scripts or many cold starts: the v8-v7 harness throws away a 1 s warm-up per test, so JIT warm-up cost is not in the measured score and the 16x does not describe one-shot snippets.
- Untrusted code where JIT attack surface matters: JIT miscompilation CVEs keep landing (CVE-2026-10702, a JIT type confusion fixed in Firefox 151.0.3, per search snippets); build with --disable-jit or force the portable baseline interpreter if runtime codegen is not allowed.
- Teams that cannot absorb API churn: master breaks the embedding API often, and moving between ESRs needs the migration guide.

## How it is fast

Tiered execution: a C++ interpreter, then a baseline interpreter and baseline JIT that attach inline caches expressed in CacheIR, then the Warp optimizing tier, where WarpOracle snapshots the CacheIR stubs the baseline ICs collected and WarpBuilder turns bytecode into MIR off the main thread for the Ion backend (register allocation, native code). A generational GC with a nursery and the Irregexp regular-expression engine (js/src/irregexp) cover the allocation- and RegExp-heavy tests. The 16x gap over QuickJS and Duktape is the JIT-versus-interpreter gap; with --disable-jit or on targets without a JIT backend SpiderMonkey runs on its interpreters, optionally the Portable Baseline Interpreter, which interprets CacheIR without generating code.

## Compared with alternatives

Pick SpiderMonkey over QuickJS, Duktape or Escargot when throughput on long-running scripts matters more than a 40 MB footprint and a heavy build, and over V8 when you want ESR branches with year-long API stability under MPL-2.0; V8 is 2.5x faster here, and ChakraCore matches its score (19392 vs 19137 on Ubuntu) at about half the size but has had no tagged release since 2020.

## Integration

| | |
|---|---|
| **Form** | shared lib (libmozjs-&lt;version&gt;) or static lib built from js/src of the Firefox tree, plus the js shell; distro packages (mozjs-140) on Linux |
| **Dependencies** | Rust toolchain (1.82+ for ESR 140), GNU Make, Python (mach/configure), zlib, libffi, ICU 76.1+ (bundled copy by default); mozglue if jemalloc is left enabled |
| **Minimum toolchain** | Current main forces -std=gnu++20 and requires clang 19+ (clang-cl on Windows) or GCC 11.1+; the ESR 140 embedding guide asks for a C++17 compiler and Rust 1.82 |
| **Platforms** | JIT backends for x86, x86-64, ARM, AArch64, MIPS64, LoongArch64 and RISC-V64; interpreter-only (optionally Portable Baseline Interpreter) elsewhere, including wasm32-wasi; Mozilla ships prebuilt jsshell zips for Linux x86-64, Windows x64 and macOS |
| **Thread safety** | A JSContext is single-threaded; extra threads create their own JSContext with the main JSRuntime as parent, initialize self-hosted code and create their own global (worker.cpp). The engine uses helper threads for off-thread Warp compilation and GC. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness: v8-v7 base.js runs each of the 10 tests for a 1 s discarded warm-up plus at least 1 s timed (and at least 32 iterations), so 20 s is a floor every JIT engine hits; the record's '20 s vs QuickJS 37 s vs Duktape 70 s' wall time is not a speed ratio, and each engine runs once per day with no variance. The macOS total of 134.9 MB is a 67.5 MB exe (jsshell-mac.zip, which spidermonkey-build uses for both x86_64 and aarch64) plus another 67.5 MB counted as 'Dll size'; the cause is not documented.
- Stale binary: js-engine-setup installs the latest ahaoboy/spidermonkey-build release, but that repo's daily refresh workflow is disabled by GitHub after 60 days without repository activity, so the measured jsshell is frozen at 147.0 while Firefox main is at 159.0a1; it predates later JIT fixes such as CVE-2026-10702 (fixed in 151.0.3) and any performance work since.
- Build the library for embedding with --disable-jemalloc (or link the matching mozglue): the default browser-oriented jemalloc configuration leads to crashes when memory allocated by jemalloc is freed by the system allocator, per the embedding guide.
- Every GC thing held across calls must be rooted (JS::Rooted, or traced from your own structures as in tracing.cpp). The spidermonkey-embedding-examples default branch is still esr102; use the esr140 branch for the current ESR.

## Known shortcomings

- A JIT engine compared against interpreters on ahaoboy/js-engine-benchmark (19137 vs QuickJS 1217 and Duktape 489 on ubuntu), one run per engine, runner CPU not stated; the binary is Mozilla's official jsshell zip, not built from esr115 source as the record said, and it is a 40.8 MB binary for an embedded-scripting use.
- Enricher: v8-v7's base.js runs each of 10 tests for 1 s of discarded warm-up plus at least 1 s timed, so 20 s is a floor every JIT engine hits and the record's wall times (20 s vs QuickJS 37 s vs Duktape 70 s) are no speed ratio; the ahaoboy/spidermonkey-build daily workflow was disabled by GitHub after 60 days of inactivity, so the jsshell is frozen at 147.0 while Firefox main is 159.0a1 and predates the CVE-2026-10702 JIT fix; the macOS 134.9 MB is a 67.5 MB exe plus a 67.5 MB duplicate. V8 is 2.5x faster in the same run.

## Caveats and trade-offs

Engines are installed as prebuilt binaries through the suite owner's js-engine-setup action; the SpiderMonkey binary is Mozilla's official jsshell for the latest Firefox development release (the from-source job in ahaoboy/spidermonkey-build, whose meson.build carries the esr115 label, is disabled with if: false), so the exact revision behind 'version 147.0' was not pinned. CPU model of the GitHub Actions runners is not stated and each engine runs once per platform with no repetitions or variance, so this is short of tier A. The score is one v8-v7 aggregate (an older suite of eight benchmarks) and engines run as shells, so startup counts in the wall time. SpiderMonkey runs with its JIT while QuickJS and Duktape are interpreters, so this measures a different class of engine; binary size is 40.8 MB vs 1 MB (QuickJS) and 370 KB (Duktape) on ubuntu. The repo URL is the Firefox monorepo because SpiderMonkey source lives under js/src; embedding it is far heavier than QuickJS or Duktape. [retier] A JIT engine compared against interpreters on ahaoboy/js-engine-benchmark (19137 vs QuickJS 1217 and Duktape 489 on ubuntu), one run per engine, runner CPU not stated; the Score excludes a 1 s discarded warm-up per test and the timed phase runs at least 1 s, so total wall time (20 s vs QuickJS 37 s vs Duktape 70 s) is a harness floor, not a speed ratio. The binary is Mozilla's official jsshell zip frozen at 147.0 (the ahaoboy/spidermonkey-build workflow was disabled by GitHub after 60 days of inactivity) while Firefox main is 159.0a1, predating the CVE-2026-10702 JIT fix. 40.8 MB binary (macOS 134.9 MB is a duplicated 67.5 MB exe); V8 is 2.5x faster in the same run.

Full JIT engine: shell binary 40.8M on Ubuntu and 134.9M on macOS vs QuickJS 1M and Duktape 370K, so score per MB is far lower (468/MB vs QuickJS 1190/MB). Building SpiderMonkey standalone is heavy; the repository is the whole Firefox tree with SpiderMonkey under js/src.

## Maintenance

Actively developed in the Firefox tree (main at 159.0a1) with ESR branches for embedders; MPL-2.0 and usable as libmozjs from source or distro packages, but the measured shell is a frozen 147.0 build and the engine is heavy to build and integrate.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party shootout (ahaoboy/js-engine-benchmark, v8-v7 suite run by scripts/update.ts from .github/workflows/update.yml) puts SpiderMonkey 147.0 at Score 19137 / 25455 / 19049 (ubuntu / macos-arm64 / windows) against QuickJS 1217 / 1761 / 1067 and Duktape 489 / 905 / 371; the code is public but the runners' CPU model and the engines' compiler flags are not stated, so it falls short of A.
- **Verifier notes:** All README numbers (snapshot 10/5/2026, 4:04:34 AM) match the record; the record's 'built through spidermonkey-build/esr115' caveat was wrong: the active workflow job downloads Mozilla's official jsshell release zip. Shortcomings: JIT engine against interpreters, single run per engine on unnamed GitHub runner CPUs, 40.8 MB binary vs 1 MB QuickJS, heavy embedding cost.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/README.md>
  - <https://github.com/ahaoboy/js-engine-benchmark>
  - <https://github.com/ahaoboy/js-engine-benchmark/tree/main/.github/workflows>
  - <https://github.com/ahaoboy/js-engine-benchmark/tree/main/scripts>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/.github/workflows/update.yml>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/scripts/update.ts>
  - <https://github.com/ahaoboy/spidermonkey-build>
  - <https://github.com/ahaoboy/spidermonkey-build/tree/main/.github/workflows>
  - <https://raw.githubusercontent.com/ahaoboy/spidermonkey-build/HEAD/download.sh>
  - <https://raw.githubusercontent.com/ahaoboy/spidermonkey-build/HEAD/meson.build>
  - <https://raw.githubusercontent.com/ahaoboy/spidermonkey-build/HEAD/.github/workflows/build.yml>
  - <https://github.com/mozilla-firefox/firefox>
  - <https://github.com/mozilla-firefox/firefox/commits/main/js/src>
  - <https://raw.githubusercontent.com/mozilla-firefox/firefox/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/scripts/update.ts>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/scripts/build.ts>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/scripts/test.js>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/info.json>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/.github/workflows/update.yml>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/v8-v7/run.js>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/v8-v7/base.js>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/v8-v7/crypto.js>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/v8-v7/earley-boyer.js>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/v8-v7/splay.js>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-setup/HEAD/info.json>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-setup/HEAD/action.yml>
  - <https://raw.githubusercontent.com/ahaoboy/spidermonkey-build/HEAD/download.sh>
  - <https://raw.githubusercontent.com/ahaoboy/spidermonkey-build/HEAD/.github/workflows/build.yml>
  - <https://github.com/ahaoboy/spidermonkey-build/releases>
  - <https://github.com/ahaoboy/spidermonkey-build/releases/tag/nightly>
  - <https://github.com/ahaoboy/spidermonkey-build/actions>
  - <https://github.com/ahaoboy/spidermonkey-build/actions/workflows/build.yml>
  - <https://raw.githubusercontent.com/mozilla-firefox/firefox/HEAD/README.md>
  - <https://raw.githubusercontent.com/mozilla-firefox/firefox/HEAD/browser/config/version.txt>
  - <https://raw.githubusercontent.com/mozilla-firefox/firefox/HEAD/build/moz.configure/toolchain.configure>
  - <https://raw.githubusercontent.com/mozilla-firefox/firefox/HEAD/js/moz.configure>
  - <https://raw.githubusercontent.com/mozilla-firefox/firefox/HEAD/js/src/jit/WarpBuilder.h>
  - <https://raw.githubusercontent.com/mozilla-firefox/firefox/HEAD/js/src/jit/WarpOracle.h>
  - <https://raw.githubusercontent.com/mozilla-firefox/firefox/HEAD/js/src/jit/WarpSnapshot.h>
  - <https://raw.githubusercontent.com/mozilla-firefox/firefox/HEAD/js/src/vm/PortableBaselineInterpret.h>
  - <https://raw.githubusercontent.com/mozilla-spidermonkey/spidermonkey-embedding-examples/HEAD/README.md>
  - <https://raw.githubusercontent.com/mozilla-spidermonkey/spidermonkey-embedding-examples/esr140/README.md>
  - <https://raw.githubusercontent.com/mozilla-spidermonkey/spidermonkey-embedding-examples/next/README.md>
  - <https://raw.githubusercontent.com/mozilla-spidermonkey/spidermonkey-embedding-examples/next/docs/Building%20SpiderMonkey.md>
  - <https://raw.githubusercontent.com/mozilla-spidermonkey/spidermonkey-embedding-examples/next/docs/JSAPI%20Introduction.md>
  - <https://raw.githubusercontent.com/mozilla-spidermonkey/spidermonkey-embedding-examples/next/examples/README.md>
  - <https://raw.githubusercontent.com/mozilla-spidermonkey/spidermonkey-embedding-examples/next/examples/worker.cpp>
  - https://www.sentinelone.com/vulnerability-database/cve-2026-10702/ (WebSearch snippet only)
  - <https://raw.githubusercontent.com/mozilla-firefox/firefox/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/mozilla-firefox/firefox/HEAD/js/src/jsapi.h>
  - /home/user/fastpp/data/wave12/enrich/raw/github_com_chakra_core_chakracore.json
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/mozilla-firefox/firefox`) · [data/wave12/enrich/raw/github_com_mozilla_firefox_firefox.json](../../../data/wave12/enrich/raw/github_com_mozilla_firefox_firefox.json) (enrichment confidence 0.75)

</details>
