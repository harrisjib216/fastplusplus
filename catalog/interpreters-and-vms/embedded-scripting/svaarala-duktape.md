# Duktape

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🟢 active

> Compact, portable embeddable ES5.1 JavaScript interpreter in C; about 1.6x MuJS on Linux/macOS, about half QuickJS's speed.

| | |
|---|---|
| **Beats** | MuJS 1.3.8 (embeddable JavaScript interpreter); QuickJS 2026.06.04 is faster than Duktape in the same table |
| **Claimed result** | ahaoboy js-engine-benchmark geometric-mean score vs MuJS 1.3.8: ubuntu 682 vs 435 (1.57x), macOS arm64 842 vs 522 (1.61x), windows 371 vs 339 (1.09x, within noise; MuJS ahead 1.13x without Crypto and NavierStokes); slower than QuickJS and quickjs-ng everywhere. |
| **Workload** | Octane/v8-v7 subset (Richards, DeltaBlue, Crypto, RayTrace, EarleyBoyer, RegExp, Splay, NavierStokes) run by the repo's CI (commits by 'update-by-ci') with the duk binary; the score is a sum over sub-benchmarks, higher is better. |
| **Metric** | throughput |
| **Hardware** | CI runners for the ubuntu, macos-arm64 and windows sections (runner type and CPU model not stated). README result timestamp 10/11/2026. |
| **Compiler and flags** | Ubuntu and macOS: ahaoboy/duktape-build build.sh clones svaarala/duktape master and runs make, whose duk target builds with -Os -fomit-frame-pointer -fno-stack-protector -g -ggdb and configure options from util/makeduk_base.yaml (DUK_USE_FASTINT, but also DUK_USE_INTERRUPT_COUNTER, DUK_USE_DEBUGGER_SUPPORT and DUK_USE_SELF_TESTS enabled); windows: release 2.7.0 built with make -f Makefile.cmdline. MuJS is built by ahaoboy/mujs-build .github/workflows/build.yml with 'make release HAVE_READLINE=no' from codeberg.org/ccxvii/mujs (MuJS Makefile flags not read). Compiler versions not stated. |
| **Adoption** | 6.2k stars |
| **Last commit** | 2026-09-04 |
| **Links** | [repository](https://github.com/svaarala/duktape) · [benchmark](https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/README.md) |

## Verdict

In ahaoboy/js-engine-benchmark (V8 v7 suite from arewefastyet, one run per engine on GitHub-hosted runners with unstated CPUs, README snapshot 10/11/2026), the Duktape command-line binary scores 682 vs MuJS 435 on ubuntu, 842 vs 522 on macOS arm64 (both Duktape master built with gcc/clang -Os and fastint) and 371 vs 339 on windows (release 2.7.0, MinGW gcc -Os, no fastint), while QuickJS scores 1522/1672/1105; the binaries are stripped by the harness and compiler versions are not stated.

## Use it when

- Embedding a scripting layer in a C/C++ application or firmware where binary size and portability matter more than speed: the stripped duk command-line binary is 370.4K on ubuntu, versus 2.2M for QuickJS, and Duktape has the best Score/MB of every engine in the ubuntu table (1885).
- Targets that only have a C89 compiler (plus snprintf/vsnprintf), exotic CPUs or 32-bit pointers, where its packed 8-byte value representation (DUK_USE_PACKED_TVAL) keeps memory use low.
- When you need ES5.1 compliance plus a remote debugger protocol and bytecode caching, and you control the scripts that run.
- As a faster alternative to MuJS for numeric or object-heavy scripts on Linux or macOS (Crypto, Splay, NavierStokes rows), provided you build with fastint.

## Skip it when

- Throughput-sensitive scripting: QuickJS scores about 2.2x higher on ubuntu (1522 vs 682), 2.0x on macOS arm64 (1672 vs 842) and 3.0x on windows (1105 vs 371), and quickjs-ng is also ahead; Duktape has no JIT.
- Modern JavaScript: the README promises ES5.1 with only partial ES2015/ES2016 support, so ES2017+ features such as async/await need transpiling first.
- Regex-heavy workloads: Duktape's RegExp row is its weakest and MuJS beats it on all three platforms (ubuntu 184 vs 251, macOS 224 vs 282, windows 104 vs 192); open issue #334 notes slow case-insensitive Unicode regexps.
- Random access into long non-ASCII strings: character-offset lookups scan the UTF-8/WTF-8 bytes behind a small string cache (open issue #335 proposes an index).
- Running untrusted bytecode, or depending on the 3.x master branch for production: master is undergoing incompatible changes and the 2.x line (v2-maintenance) has had no commit since 2022-07-24.

## How it is fast

It is footprint-first rather than speed-first: a register-based bytecode interpreter (doc/execution.rst) with no JIT, reference counting plus mark-and-sweep for tight memory, and configure.py options that trade size for speed. The relevant speed option is DUK_USE_FASTINT (48-bit integer fast path, off by default, on in the benchmarked Linux/macOS build), which explains most of its lead over MuJS on the integer-heavy Crypto test (1022 vs 241 on ubuntu); the guide also recommends PGO (about 20% for GCC -O2).

## Compared with alternatives

Pick Duktape over QuickJS when binary size and C89-level portability matter more than about 2x throughput and ES2020+ features, and over MuJS when your scripts are numeric or object-heavy rather than regex-heavy; for microcontroller-class memory budgets also compare JerryScript (lower peak memory in its issue #4386 table) and XS (Moddable).

## Integration

| | |
|---|---|
| **Form** | source-drop (amalgamated duktape.c + duktape.h + duk_config.h from the release tarball); custom configurations are generated with tools/configure.py |
| **Dependencies** | none at run time beyond libc and libm (the Date built-in may need a platform provider); configure.py needs Python with PyYAML |
| **Minimum toolchain** | C89 compiler with snprintf()/vsnprintf() (guide, Portability); also compiles as C++; the repo Makefile builds with -std=c99 |
| **Platforms** | any platform with such a compiler: Linux, macOS (including arm64 in CI), Windows (MinGW and MSVC), embedded and 32-bit targets; LoongArch support added on master in 2024 |
| **Thread safety** | One native thread at a time per Duktape heap (application must lock, or use duk_suspend/duk_resume to hand over); separate heaps are fully isolated and can run concurrently. |
| **Drop-in for the baseline** | no |

## Gotchas

- Benchmark harness: the ahaoboy CI installs Duktape from ahaoboy/duktape-build's only release (v0.1.0, built 2025-06-19 from master, which had no commits between 2024-01-29 and 2026-09-04), so the binary is unchanged between daily runs; its ubuntu score still moved from 489 (10/5/2026 snapshot) to 682 (10/11/2026), about 39%, and QuickJS moved from 1217 to 1522 in the same window, so single runs on shared GitHub runners carry noise larger than the 1.09x windows margin over MuJS.
- The three platforms run different Duktape builds: ubuntu and macOS use master (2.99.99) built with util/makeduk_base.yaml (DUK_USE_FASTINT on, plus interrupt counter, debugger support and self tests), while windows uses release 2.7.0 built with Makefile.cmdline and the default config, where DUK_USE_FASTINT defaults to false; that is why windows Crypto is 309 against 1022 on ubuntu and why the windows lead over MuJS nearly disappears.
- Score is the geometric mean of the eight per-test scores (recomputed: 681.5 and 435.4 from the ubuntu rows), not a sum. Leaving out Crypto and NavierStokes, Duktape over MuJS drops to about 1.29x on ubuntu and 1.27x on macOS, and MuJS leads about 1.13x on windows (derived from page data).
- Duktape does not validate loaded bytecode; its guide warns that crafted bytecode can lead to exploitable memory-unsafe behavior. A WebSearch snippet of NVD's CVE-2026-12216 (count_instr in the bytecode loader, up to 2.99.99) says Debian lists 2.7.0-2 as unfixed. Master also carried a heap-buffer-overflow in the backwards WTF-8 string-cache scanner until PR #2587 (merged 2026-09-04), so the benchmarked master build predates that fix.

## Known shortcomings

- ahaoboy js-engine-benchmark: Duktape beats only MuJS and weaker engines (ubuntu 682 vs 435) and is slower than QuickJS and quickjs-ng; the Windows margin is thin (MuJS wins 5 of 8 sub-tests there), daily scores drift (489 to 682 on ubuntu), and the build is -Os with debugger hooks.
- Enricher: the benchmark binary (ahaoboy/duktape-build v0.1.0, built 2025-06-19) is unchanged across runs yet the ubuntu score moved from 489 to 682 (39%), so runner noise exceeds the 1.09x windows margin over MuJS; the Windows build is 2.7.0 default config with FASTINT off (Crypto 309 vs 1022 on ubuntu); the score is a geometric mean, not a sum; without Crypto and NavierStokes the lead is 1.29x on ubuntu and 1.27x on macOS and MuJS is ahead 1.13x on windows. Maintenance: last release 2.7.0 (2022), v2-maintenance idle since 2022-07-24, one merged fix on master since 2024-01-29 (PR #2587 WTF-8 heap overflow, 2026-09-04); CVE-2026-12216 (bytecode loader, snippet only).

## Caveats and trade-offs

The project itself does not claim to be faster than any named engine: its README stresses portability and compact footprint, and QuickJS is clearly faster in the same table (ubuntu 1522 versus 682; quickjs-ng 800). The wins recorded here are only over MuJS and weaker engines (xst, goja, Boa, Jint) in a third-party CI shootout: one run per engine, no variance, runner CPU not stated, ubuntu and macOS build master (2.99.99) while windows runs release 2.7.0, and the scores drift between daily runs (other wave 12 verifiers read Duktape at 489/905/371 in the 10/5/2026 snapshot versus 682/842/371 on 10/11/2026), which is large next to the margins. The lead over MuJS comes mostly from Crypto and NavierStokes: MuJS wins RegExp on all three platforms (ubuntu 251 versus 184) and on windows also wins Richards, DeltaBlue, RayTrace and EarleyBoyer, so the windows total (371 versus 339) is thin. The Duktape build handicaps speed (-Os, interrupt counter and debugger support compiled in). Binary size: Duktape 370.4K versus MuJS 378.8K on ubuntu, but 431.4K versus 395.5K on macOS, so the size edge is not consistent. A 2015 Scriptorium run (r-lyeh-archived/scriptorium, AMD A10 3.8 GHz, Windows 7, VS2015 RC or VS2013, recursive fib) has Duktape at 9.544 s versus v7 at 51.940 s (about 5.4x, derived from page data) and Jim Tcl at 12.280 s, but far behind PUC Lua at 1.341 s and most other embeddable languages (rank 32 of 50). A JerryScript issue (#4386) peak-memory row (Duktape 582,240 KB versus QuickJS 5,523,792 KB) looks like an aggregate and was not used. [retier] Daily score drift up to 39% on an unchanged binary; Windows build 2.7.0 default config, FASTINT off; -Os build with debugger hooks; stale (last release 2.7.0, 2022).

Footprint-first design (README: portability and compact footprint); ECMAScript 5.1 with selected later features, no JIT. Master is undergoing incompatible changes for Duktape 3.x and 2.x users are pointed to the v2-maintenance branch.

## Maintenance

MIT-licensed and easy to vendor, but maintenance is thin: the last release is 2.7.0 (February 2022), v2-maintenance has been idle since 2022-07-24, and master (unreleased 3.x, incompatible changes in progress) received only one merged fix between January 2024 and September 2026, so the record's 'active' status overstates it; vendor 2.7.0 and apply security fixes yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party CI shootout (ahaoboy/js-engine-benchmark, V8 v7 suite forked from mozilla arewefastyet, README snapshot 10/11/2026) shows Duktape Score 682/842/371 vs MuJS 435/522/339 on ubuntu/macos-arm64/windows; build recipe public (ahaoboy/duktape-build build.sh runs make on svaarala/duktape master, Makefile CCOPTS_NONDEBUG -Os). Not A: GitHub runner CPU model and compiler versions are not stated; B matches the wave 12 precedent for this suite (ChakraCore, njs, MuJS).
- **Verifier notes:** Scores, versions and sizes match the 10/11/2026 README snapshot; MuJS is already verified in wave 12 (batch-98), so baseline_in_list is true. Shortcomings to record: not faster than QuickJS or quickjs-ng, thin windows margin with MuJS winning 5 of 8 sub-tests there, daily-run score drift, -Os build with debugger hooks, runner CPU unstated; the Scriptorium figures were confirmed on its README.
- **Fields the verifier corrected:** `baseline_in_list`, `compiler_and_flags`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-99 (wave 12); enricher w12 pair-008
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/README.md>
  - <https://github.com/ahaoboy/js-engine-benchmark>
  - <https://github.com/ahaoboy/duktape-build>
  - <https://raw.githubusercontent.com/ahaoboy/duktape-build/main/build.sh>
  - <https://raw.githubusercontent.com/svaarala/duktape/master/Makefile>
  - <https://raw.githubusercontent.com/svaarala/duktape/master/util/makeduk_base.yaml>
  - <https://github.com/ahaoboy/mujs-build>
  - <https://github.com/ahaoboy/mujs-build/tree/main/.github/workflows>
  - <https://raw.githubusercontent.com/ahaoboy/mujs-build/main/.github/workflows/build.yml>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/README.md>
  - <https://github.com/svaarala/duktape>
  - <https://github.com/svaarala/duktape/commits/master>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/README.md>
  - <https://github.com/ahaoboy/js-engine-benchmark>
  - <https://github.com/ahaoboy/js-engine-benchmark/tree/main/scripts>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/main/scripts/update.ts>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/main/scripts/build.ts>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/main/scripts/test.js>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/main/package.json>
  - <https://github.com/ahaoboy/js-engine-benchmark/tree/main/.github/workflows>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/main/.github/workflows/update.yml>
  - <https://github.com/ahaoboy/js-engine-setup>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-setup/HEAD/info.json>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-setup/HEAD/action.yml>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-setup/HEAD/strip.sh>
  - <https://github.com/ahaoboy/duktape-build>
  - <https://github.com/ahaoboy/duktape-build/releases>
  - <https://github.com/ahaoboy/duktape-build/commits/main>
  - <https://github.com/ahaoboy/duktape-build/tree/main/.github/workflows>
  - <https://raw.githubusercontent.com/ahaoboy/duktape-build/main/build.sh>
  - <https://raw.githubusercontent.com/ahaoboy/duktape-build/main/.github/workflows/build.yml>
  - <https://github.com/svaarala/duktape>
  - <https://github.com/svaarala/duktape/commits/master>
  - <https://github.com/svaarala/duktape/commits/v2-maintenance>
  - <https://github.com/svaarala/duktape/pull/2587>
  - <https://github.com/svaarala/duktape/issues?q=is%3Aissue+is%3Aopen+label%3Aperformance>
  - <https://raw.githubusercontent.com/svaarala/duktape/master/README.md>
  - <https://raw.githubusercontent.com/svaarala/duktape/master/Makefile>
  - <https://raw.githubusercontent.com/svaarala/duktape/master/util/makeduk_base.yaml>
  - <https://raw.githubusercontent.com/svaarala/duktape/v2.7.0/dist-files/Makefile.cmdline>
  - <https://raw.githubusercontent.com/svaarala/duktape/v2.7.0/config/config-options/DUK_USE_FASTINT.yaml>
  - <https://raw.githubusercontent.com/svaarala/duktape/master/config/config-options/DUK_USE_PACKED_TVAL.yaml>
  - <https://raw.githubusercontent.com/svaarala/duktape/master/doc/execution.rst>
  - <https://raw.githubusercontent.com/svaarala/duktape/master/website/guide/threading.html>
  - <https://raw.githubusercontent.com/svaarala/duktape/master/website/guide/portability.html>
  - <https://raw.githubusercontent.com/svaarala/duktape/master/website/guide/bytecodedumpload.html>
  - <https://raw.githubusercontent.com/svaarala/duktape/master/website/guide/performance.html>
  - WebSearch snippets for CVE-2026-12216 and CVE-2021-46322 (nvd.nist.gov, security-tracker.debian.org, ubuntu.com; pages not opened)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/svaarala/duktape`) · [data/wave12/enrich/raw/github_com_svaarala_duktape.json](../../../data/wave12/enrich/raw/github_com_svaarala_duktape.json) (enrichment confidence 0.65)

</details>
