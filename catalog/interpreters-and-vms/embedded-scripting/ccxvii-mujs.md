# MuJS

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `ISC` · 🟢 active

> Small ISC-licensed ES5 bytecode interpreter in C for embedding; outscores goja, Boa and Jint on V8 v7, trails Duktape and QuickJS.

| | |
|---|---|
| **Beats** | goja (Go JavaScript interpreter); also Boa (Rust) and Jint (.NET) JavaScript interpreters in the same table |
| **Claimed result** | V8 v7 overall Score, README snapshot 10/11/2026 (higher is better; MuJS reported as version 1.3.8): ubuntu MuJS 435 vs goja 365, Boa 279, Jint 246 (1.19x, 1.56x, 1.77x, derived from page data); macos-arm64 MuJS 522 vs goja 358, Boa 302, Jint 239 (1.46x, 1.73x, 2.18x, derived from page data); windows MuJS 339 vs goja 229, Jint 159 (1.48x, 2.13x, derived from page data; Boa has no score there). The same tables put MuJS below the category incumbents Duktape (682 / 842 / 371) and QuickJS (1522 / 1672 / 1105). |
| **Workload** | V8 v7 benchmark suite (Richards, DeltaBlue, Crypto, RayTrace, EarleyBoyer, RegExp, Splay, NavierStokes) run once per engine per daily GitHub Actions job through each engine's CLI; base.js times every benchmark in-process (one warm-up Measure, then at least 1 s and 32 runs), and Score is the geometric mean of the per-benchmark scores, higher is better. |
| **Metric** | throughput |
| **Hardware** | GitHub Actions hosted runners (ubuntu-latest, macos-latest arm64, windows-latest); CPU model not stated. |
| **Compiler and flags** | MuJS: ahaoboy/mujs-build .github/workflows/build.yml clones the Codeberg HEAD daily and runs 'make release HAVE_READLINE=no'; the Makefile (checked at GitHub mirror commit 05cd646; the Codeberg HEAD copy could not be opened) compiles the one.c amalgamation with '-std=c99 -pedantic -Wall -Wextra -Wno-unused-parameter -O3' using the runner's default cc (gcc on ubuntu-latest, Apple clang on macos-latest, MinGW-w64 gcc under MSYS2 on windows-latest; versions not stated). goja: ahaoboy/goja-build runs 'go build ./goja/main.go' on dop251/goja HEAD with default Go toolchain settings. |
| **Adoption** | 858 stars and 103 forks on the GitHub mirror (canonical repo moved to Codeberg); packaged by Debian, Ubuntu and openSUSE (search snippets). |
| **Last commit** | 2025-08-13 |
| **Links** | [repository](https://codeberg.org/ccxvii/mujs) · [benchmark](https://github.com/ahaoboy/js-engine-benchmark) |

## Verdict

On ahaoboy/js-engine-benchmark, a daily third-party GitHub Actions run of the V8 v7 suite (8 benchmarks, in-process timing after a warm-up, geometric-mean Score), MuJS 1.3.8 built with the stock Makefile (-O3, runner default cc) scored 435 / 522 / 339 on ubuntu / macos-arm64 / windows against goja 365 / 358 / 229, Boa 279 / 302 and Jint 246 / 239 / 159 (about 1.2-1.5x goja, derived from page data). The runners' CPU models and compiler versions are not stated, each engine runs once per day, and the same table puts Duktape (682 / 842 / 371) and QuickJS (1522 / 1672 / 1105) ahead of MuJS on every platform.

## Use it when

- You need ES5 scripting inside a C or C++ application and binary size matters: the ubuntu CLI binary is 378.8 KB (about 180-260 KB for the library per the project docs), against 2.2 MB for QuickJS.
- You want a permissive ISC licence, no build system (compile one.c with any C99 compiler) and no C++ runtime dependency.
- Your scripts are glue that calls into C for heavy work; the docs describe a very fast C call-out path and recommend doing the heavy lifting in C.
- You are replacing a Go, Rust or .NET JavaScript interpreter (goja, Boa, Jint) with a native one and only need ES5: MuJS scored 1.19x-1.48x goja and 1.56x-1.77x Boa on the V8 v7 suite.
- You want the engine already shipped by mpv, MuPDF and the Debian/Ubuntu/openSUSE packages.

## Skip it when

- Raw script throughput matters: Duktape scores 1.09x-1.61x and QuickJS 3.2x-3.5x higher on the same suite and runners, and any JIT engine is one to two orders of magnitude faster.
- Your code uses ES2015 or later (let/const, classes, arrow functions, modules, Promises, BigInt): MuJS implements ES5 only.
- GC- or allocation-heavy workloads: on ubuntu goja beats it on Splay (1074 vs 818), EarleyBoyer (666 vs 534) and RegExp (271 vs 251), and on macOS goja still wins Splay.
- You run hostile scripts and need a hardened engine: the GitHub tracker lists heap-use-after-free (#209, GC during an Array.prototype.sort comparator), heap-buffer-overflows in jsarray.c (#207, #208) and Ap_sort_cmp (#193, #211), all on 1.3.x; earlier CVEs include CVE-2021-45005 (nested try/finally heap overflow in 1.1.3) and an O_getOwnPropertyDescriptor memory-corruption bug fixed in 1.3.2.
- Deep recursion or large regex backtracking: the value stack is fixed at 4096 slots and the environment stack at 1024, and the backtracking regex matcher gives up past 1024 recursion levels.

## How it is fast

Its lead over the Go, Rust and .NET interpreters comes from being a plain compiled-C switch-dispatched stack bytecode VM: 16-bit instructions, a tagged-union js_Value on a fixed 4096-slot value stack, interned strings, a dense 'flat' array part for simple arrays, and a stop-the-world mark-and-sweep collector that runs when allocations reach 5x the live set (JS_GCFACTOR 5.0). It does no JIT and has no hidden classes or inline caches: every property access is a strcmp walk of a per-object AA-tree (jsproperty.c), each opcode carries a line-number word, and the loop checks the GC counter on every instruction. That is why Duktape and QuickJS, also C interpreters, beat it.

## Compared with alternatives

Pick MuJS over Duktape when you want the smallest, simplest ES5 C engine with an ISC licence and a Lua-like stack API, and you can live with roughly 1.1-1.6x lower V8 v7 scores (Duktape won even when built -Os). Pick QuickJS instead when you need modern JavaScript or about 3x more interpreter throughput and can afford a 2 MB binary; pick MuJS over goja only when the host is C or C++ rather than Go.

## Integration

| | |
|---|---|
| **Form** | source-drop (single one.c amalgamation) or static/shared lib via make release |
| **Dependencies** | none beyond libc and libm (readline optional for the shell; regenerating utfdata.h needs python3 and the Unicode data files) |
| **Minimum toolchain** | C99 compiler (Makefile uses -std=c99 -pedantic -O3); gcc, clang and MinGW-w64 all build it in the benchmark's CI |
| **Platforms** | any: Linux, macOS (arm64 tested), Windows via MinGW, Android/iOS and small boards per the docs |
| **Thread safety** | not documented; all mutable state lives in js_State (the static sentinels in jsproperty.c and jsintern.c are read-only), so one state per thread with no sharing is the safe pattern |
| **Drop-in for the baseline** | no |

## Gotchas

- Errors use setjmp/longjmp (js_try, js_pcall); a JavaScript exception or error unwinds straight through C++ frames without running destructors, and an error outside any protected call runs the panic handler and then abort() unless the panic function longjmps out.
- A regex whose backtracking exceeds REG_MAXREC (1024) does not match slowly; js_regexec returns -1 and the script gets a thrown Error 'regexec failed'.
- The GitHub repository is a stub since 2025-08-13 ('Migrate to Codeberg'); the 1.3.8 code measured here lives on codeberg.org/ccxvii/mujs, and many GitHub memory-safety issues (#206-#211) were closed as completed on 2026-03-31 with no linked commit, so check the Codeberg history for the fixes before pinning a version.
- Allocation sizes are int (js_Alloc takes int size); arrays are capped at 64M entries (JS_ARRAYLIMIT) and strings at 256 MB (JS_STRLIMIT).

## Known shortcomings

- ahaoboy/js-engine-benchmark scores match (ubuntu 435 vs goja 365, macos-arm64 522 vs 358, windows 339 vs 229) but MuJS beats only the Go, Rust and .NET interpreters (goja, Boa, Jint) and is slower than the incumbents Duktape and QuickJS on every platform; one CI run per day, runner CPU unstated, and the c2rust translation mujs-one scores 505 vs 435 on ubuntu so noise is near the 1.19x margin. Canonical repo is https://codeberg.org/ccxvii/mujs (blocked here); the GitHub mirror is a stub.
- Enricher: ES5 only; slower than Duktape (1.09-1.61x) and QuickJS (3.2-3.5x) everywhere, and goja wins Splay, EarleyBoyer and RegExp on ubuntu; plain switch VM with AA-tree strcmp property lookup, a line word per opcode and a GC check every instruction; fuzzer memory-safety bugs #193, #207-#211 closed 2026-03-31 with no linked commit; regex past 1024 recursion levels throws 'regexec failed'; longjmp error model.

## Caveats and trade-offs

Nobody at the MuJS project claims this win; it is read off an automated third-party leaderboard (ahaoboy/js-engine-benchmark, 59 stars, regenerated daily, one run per engine per day on shared GitHub Actions runners whose CPU model is not stated). The only engines MuJS beats are interpreters written in other languages (goja in Go, Boa in Rust, Jint in .NET, plus es5, quickjs-oxide, xst and ringo); the category incumbents Duktape (about 1.57x, 1.61x and 1.09x faster on ubuntu, macos-arm64 and windows, derived from page data) and QuickJS (about 3.2-3.5x faster) beat it on every platform, so MuJS is not faster than the usual C embeddable JavaScript engines. Noise check: mujs-one, a c2rust translation of MuJS of unstated revision, scores 505 vs MuJS 435 on ubuntu, a gap close to the 1.19x ubuntu margin over goja; the macOS and Windows margins (1.46x, 1.48x) are larger and consistent. Score excludes process startup and CLI-wrapper overhead (base.js times in-process after a warm-up); only the Time(s) row includes it. The README rows align with the engine columns (MuJS's eight per-test values 310, 397, 241, 620, 534, 251, 818, 640 give the 435 Score as a geometric mean, derived from page data). The GitHub repo is a stub (README: 'This repository has migrated to https://codeberg.org/ccxvii/mujs'; last mirror commit 2385035 'Migrate to Codeberg.' on 2025-08-13, last mirror tag 1.3.7 on 2025-06-23); the Codeberg repo could not be opened here, but the benchmark's daily Codeberg build reports version 1.3.8 and Debian/Ubuntu ship a 1.3.8 tarball dated December 2025 (search snippet), so development continues there. ISC licence verified from COPYING at mirror commit 05cd646 (copyright Artifex Software).

Interpreter only, built for embedding. Very small: total size 378.8K on the ubuntu run, giving the benchmark's Score/MB of 1175. It is not the fastest embeddable engine: in the same table QuickJS scores 1522 and Duktape 682 on ubuntu, and Duktape 842 vs MuJS 522 on macos-arm64.

## Maintenance

Actively maintained by Artifex on Codeberg (1.3.8 is the version built in the benchmark's daily job; the GitHub mirror stopped at 2025-08-13), ISC-licensed and small enough to vendor as one C file, but treat it as unsafe for untrusted scripts given its steady stream of fuzzer-found memory-safety bugs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now B.
- **Tier reason:** Independent third-party CI shootout (ahaoboy/js-engine-benchmark: V8 v7 suite code in v8-v7/ forked from mozilla/arewefastyet, driver scripts/update.ts, MuJS built by ahaoboy/mujs-build build.yml with the public Makefile's -O3) shows MuJS Score 435/522/339 vs goja 365/358/229 on ubuntu/macos-arm64/windows; not A because the runners' CPU models and compiler versions are not stated. Upgraded from C to B for consistency with the other entries tiered from this suite (ChakraCore, V8, njs, quanta, ant, lo, bare, ladybird, lumen, SpiderMonkey).
- **Verifier notes:** Numbers match the README snapshot exactly on all three platforms, and goja is a verified wave-12 entry, so the comparison stands; tier raised C to B to match every other entry tiered from this suite. Main shortcoming: MuJS only beats Go/Rust/.NET interpreters and is slower than Duktape and QuickJS on every platform. Consider a repo_url override to https://codeberg.org/ccxvii/mujs (GitHub is a migration stub; codeberg.org did not resolve from this container), and last_commit stays the mirror's 2025-08-13 because the Codeberg history could not be read.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `maintenance_status`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-98 (wave 12); enricher w12 pair-006
- **Pages the verifier opened:**
  - <https://github.com/ahaoboy/js-engine-benchmark>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/package.json>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/info.json>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/scripts/update.ts>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/v8-v7/run.js>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/v8-v7/base.js>
  - <https://github.com/ahaoboy/mujs-build>
  - <https://github.com/ahaoboy/mujs-build/tree/main/.github/workflows>
  - <https://raw.githubusercontent.com/ahaoboy/mujs-build/HEAD/.github/workflows/build.yml>
  - <https://raw.githubusercontent.com/ahaoboy/goja-build/HEAD/.github/workflows/build.yml>
  - <https://github.com/ccxvii/mujs>
  - <https://github.com/ccxvii/mujs/commits>
  - <https://github.com/ccxvii/mujs/tags>
  - <https://raw.githubusercontent.com/ccxvii/mujs/05cd646/COPYING>
  - <https://raw.githubusercontent.com/ccxvii/mujs/05cd646/Makefile>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ccxvii/mujs/05cd646/README>
  - <https://raw.githubusercontent.com/ccxvii/mujs/05cd646/Makefile>
  - <https://raw.githubusercontent.com/ccxvii/mujs/05cd646/mujs.h>
  - <https://raw.githubusercontent.com/ccxvii/mujs/05cd646/COPYING>
  - <https://raw.githubusercontent.com/ccxvii/mujs/05cd646/jsi.h>
  - <https://raw.githubusercontent.com/ccxvii/mujs/05cd646/jsrun.c>
  - <https://raw.githubusercontent.com/ccxvii/mujs/05cd646/jscompile.c>
  - <https://raw.githubusercontent.com/ccxvii/mujs/05cd646/jsproperty.c>
  - <https://raw.githubusercontent.com/ccxvii/mujs/05cd646/jsgc.c>
  - <https://raw.githubusercontent.com/ccxvii/mujs/05cd646/jsintern.c>
  - <https://raw.githubusercontent.com/ccxvii/mujs/05cd646/jsstate.c>
  - <https://raw.githubusercontent.com/ccxvii/mujs/05cd646/jsvalue.c>
  - <https://raw.githubusercontent.com/ccxvii/mujs/05cd646/regexp.c>
  - <https://raw.githubusercontent.com/ccxvii/mujs/05cd646/jsregexp.c>
  - <https://raw.githubusercontent.com/ccxvii/mujs/05cd646/main.c>
  - <https://raw.githubusercontent.com/ccxvii/mujs/05cd646/docs/introduction.html>
  - <https://raw.githubusercontent.com/ccxvii/mujs/05cd646/docs/reference.html>
  - <https://github.com/ccxvii/mujs/commits>
  - <https://github.com/ccxvii/mujs/issues?q=is%3Aissue>
  - <https://github.com/ccxvii/mujs/issues/209>
  - https://codeberg.org/ccxvii/mujs (blocked: proxy CONNECT 403)
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/scripts/update.ts>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/v8-v7/run.js>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/v8-v7/base.js>
  - <https://raw.githubusercontent.com/ahaoboy/mujs-build/HEAD/.github/workflows/build.yml>
  - <https://raw.githubusercontent.com/mpv-player/mpv/master/meson.build>
  - <https://raw.githubusercontent.com/ArtifexSoftware/mupdf/master/Makethird>
  - WebSearch: mujs CVE 2025 OR 2026 heap overflow Artifex mujs 1.3.8 (snippets from rapid7.com CVE-2021-45005, cvefeed.io CVE-2016-10133, db.gcve.eu CVE-2016-7564)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/ccxvii/mujs`) · [data/wave12/enrich/raw/github_com_ccxvii_mujs.json](../../../data/wave12/enrich/raw/github_com_ccxvii_mujs.json) (enrichment confidence 0.75)

</details>
