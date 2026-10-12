# JerryScript

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0` · 🟢 active

> C99 JavaScript engine for microcontrollers that trades speed for footprint; uses less memory than Duktape but runs about 2x slower.

| | |
|---|---|
| **Beats** | Duktape |
| **Claimed result** | Issue #4386 lists 'peak memory consumption' (labelled KB) of 239,664 for JerryScript ESNext vs 582,240 for Duktape and 5,523,792 for QuickJS (JerryScript about 2.4x less than Duktape, derived from page data). On speed JerryScript loses on every test: V8 TotalScore 250 vs Duktape 487 and QuickJS 1,042 (higher is better), per test vs Duktape Richards 173 vs 223, DeltaBlue 180 vs 282, Crypto 182 vs 385, RayTrace 291 vs 617, EarleyBoyer 408 vs 686, RegExp 155 vs 221, Splay 365 vs 1296, NavierStokes 398 vs 1073, so about 1.9x slower than Duktape overall (derived from page data). |
| **Workload** | V8 benchmark suite (Richards, DeltaBlue, Crypto, RayTrace, EarleyBoyer, RegExp, Splay, NavierStokes) run on JerryScript ESNext, QuickJS, Duktape and Node.js; the issue reports one peak-memory figure per engine plus per-benchmark scores. |
| **Metric** | memory |
| **Compiler and flags** | JerryScript: python tools/build.py --clean --lto=OFF --jerry-debugger=ON --jerry-cmdline=ON (issue text also lists snapshot execution, 512KB stack limit, 64MB GC mark limit). Duktape: gcc -O3 -DDUK_CMDLINE_CONSOLE_SUPPORT duktape.c duk_cmdline.c duk_console.c -lm -lc -o duk. QuickJS: qjs combined.js. Compiler versions not stated. |
| **Adoption** | 7.4k stars |
| **Last commit** | 2025-10-08 |
| **Links** | [repository](https://github.com/jerryscript-project/jerryscript) · [benchmark](https://github.com/jerryscript-project/jerryscript/issues/4386) |

## Verdict

A third-party GitHub issue (#4386, December 2020) ran the V8 benchmark suite on a debugger-enabled, malloc-backed JerryScript ESNext build, Duktape (gcc -O3), QuickJS and Node.js, and reports one 'peak memory' figure per engine (JerryScript 239,664 vs Duktape 582,240, about 2.4x less) with no hardware, compiler version or measurement method, alongside scores where JerryScript is about 1.9x slower than Duktape. Samsung's first-party SunSpider max-RSS slides (JerryScript 1.0 vs Duktape 1.5.1 on a Raspberry Pi 2) point the same way but were reachable only as search snippets.

## Use it when

- Bare-metal or RTOS microcontrollers with tens to a few hundred KB of RAM where QuickJS-class engines do not fit; the default build reserves a fixed 512 KB heap, and JERRY_GLOBAL_HEAP_SIZE shrinks it.
- Firmware that ships JavaScript precompiled: snapshot save/exec plus --js-parser=OFF removes the parser and runs byte-code straight from flash.
- Products that need a stable C embedding API with a documented port layer (time, I/O, fatal handling, context allocation) and in-tree targets such as RIOT and NuttX.
- Running several isolated scripts in one firmware image: JERRY_EXTERNAL_CONTEXT lets the port supply a separately sized context per engine instance via jerry_port_context_get.

## Skip it when

- Throughput matters: in third-party issue #4386 it scored 250 against Duktape's 487 and QuickJS's 1,042 on the V8 suite, losing all eight tests to Duktape, and in the independent ahaoboy/js-engine-benchmark CI JerryScript 3.0.0 is slower than Duktape on every test it completes.
- Workloads that allocate heavily or need more than 512 KB of heap: the stock build in ahaoboy's CI (plain tools/build.py) produced no score for EarleyBoyer, RegExp, Splay or NavierStokes; larger heaps need 32-bit compressed pointers, and the malloc-backed system allocator is documented as unsupported on 64-bit architectures.
- Running untrusted scripts or snapshots: the tracker holds dozens of open fuzzer reports from 2025-2026 without fixes, including #5302 (malformed snapshot drives a stack-buffer-overflow), #5272 (heap-overflow write during garbage collection), #5282 (heap out-of-bounds read in Array.prototype.copyWithin) and #5291 (a request for a private security contact about snapshot-loader bugs).
- Code that needs modern JavaScript: ES2025 coverage is about 70%, and error messages are compiled out by default (JERRY_ERROR_MESSAGES=0).
- You need active upstream: only two commits landed after the 3.0.0 release (2025-06-03 and 2025-10-08), with 209 open issues and 45 open pull requests.

## How it is fast

The win is footprint, not speed. A recursive-descent parser emits a compact byte-code (CBC, a CISC-like encoding with short opcodes for frequent operations) directly without building an AST, and snapshots of that byte-code can execute in place from ROM. Heap references are 16-bit compressed pointers (8-byte aligned offsets into a statically allocated heap of at most 512 KB; switching to 32-bit pointers costs about 20% more memory per the internals doc), values are tagged in their low three bits, object properties are packed two per 16-byte pair, common strings are replaced by ROM 'magic string' ids, and the VM loop is non-recursive so JS calls do not grow the C stack. Memory is reclaimed by reference counting plus a mark-and-sweep pass over a single object chain; the speed aids it does have (LCache property cache, per-object property hashmaps above 16 properties) are on by default and cost RAM.

## Compared with alternatives

Pick JerryScript over QuickJS or Duktape when RAM, not speed, is the constraint and you want precompiled snapshots in flash with a parser-free build; QuickJS is about 4x faster on the V8 suite and much more complete. Against XS (Moddable SDK) and MicroQuickJS, which also target microcontrollers, JerryScript's draws are its long-stable C port layer and Apache-2.0 licence rather than measured footprint, since no catalogued source compares them directly.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake via tools/build.py) or source-drop (amalgamated jerryscript.c, jerryscript-port.c and jerryscript-math.c from tools/amalgam.py) |
| **Dependencies** | none beyond a C library; ships its own optional libm (jerry-math) and default port implementation |
| **Minimum toolchain** | C99 compiler (GCC, Clang, MSVC, arm-none-eabi); CMake 3.10+ and Python 3 for the build scripts |
| **Platforms** | any target with a C99 compiler: ARM Thumb-2 microcontrollers (258K binary per the README), Linux, macOS, Windows; 32-bit hosts for the system-allocator mode; on 32-bit x86 the docs require -msse2 -mfpmath=sse for correct floating point |
| **Thread safety** | Not documented as thread-safe. The default build keeps all engine state in one static context (one engine per process); with JERRY_EXTERNAL_CONTEXT the port's jerry_port_context_get selects the active context, so separate threads need separate contexts. |
| **Drop-in for the baseline** | no |

## Gotchas

- The memory figure behind this entry comes from a harness that does not reflect a footprint build: issue #4386 built JerryScript with --system-allocator=ON (plain malloc instead of the compact static heap), --cpointer-32bit=ON, the debugger, line info, error messages and logging. The configuration docs say the system allocator is unsupported on 64-bit architectures, and the issue never names its architecture; in release builds jmem_compress_pointer only asserts that a 64-bit pointer offset fits in 32 bits, so on a 64-bit host the run was either unsupported or relied on malloc addresses staying in range.
- The issue's peak-memory row is not credible as labelled: Node.js and Node.js --jitless share the identical 73,873,464 'KB' (about 70 GB) and QuickJS shows 5.5 GB; no measurement method, hardware or compiler version is given, so the 2.4x-less-than-Duktape ratio is directional only.
- With the internal allocator, the heap is a fixed static array (default 512 KB) addressed by 16-bit compressed pointers; raising JERRY_GLOBAL_HEAP_SIZE above 512 forces 32-bit pointers and about 20% more memory per object, so the footprint advantage shrinks as heaps grow.
- API ownership is manual: every returned jerry_value_t must be passed to jerry_value_free, and 2.x code using jerry_release_value or jerry_get_global_object does not compile on 3.0 (the migration guide points to per-function rename notes in the API reference).

## Known shortcomings

- Memory win only, from third-party issue #4386 with no method and impossible peak-memory units (Node 73,873,464 'KB'); slower than Duktape on all 8 V8 tests (250 vs 487), and JerryScript 3.0.0 fails 4 of 8 tests in the ahaoboy CI. Samsung RSS slides seen as a snippet only.
- Enricher: issue #4386 was built with --system-allocator=ON, a mode the configuration docs call unsupported on 64-bit (the issue names no architecture), and its peak-memory row is not credible (Node 70 GB as 'KB'); the ahaoboy CI stock build (tools/build.py, fixed 512 KB heap) scores nothing on EarleyBoyer, RegExp, Splay and NavierStokes. Many open fuzzer memory-safety issues from 2025-2026 (#5302, #5272, #5282, #5291) are unanswered; only 2 commits since 3.0.0.

## Caveats and trade-offs

The only numeric comparison reachable is a third-party GitHub issue (#4386, opened 2020-12-29 by lygstate, still open with the discussion label, no replies), not project-authored. It shows JerryScript slower than Duktape on all eight V8 tests and much slower than QuickJS; the claim that holds is memory only (README: 'Heavily optimized for low memory consumption'). The peak-memory row is not credible as labelled: Node.js and Node.js Jitless share the identical 73,873,464 'KB' (about 70 GB) and QuickJS shows 5.5 GB, so the unit or method is wrong (as bytes the figures would be plausible), and no measurement method, hardware or compiler version is given. The JerryScript build used --system-allocator=ON (malloc instead of its compact heap), --cpointer-32bit=ON, --jerry-debugger=ON and --lto=OFF, so neither its memory nor its speed reflects a footprint-tuned build. Counter-evidence from the independent ahaoboy/js-engine-benchmark CI (V8 v7 suite, 10/5/2026): JerryScript 3.0.0 completes only Richards, DeltaBlue, Crypto and RayTrace (no total score) and is slower than Duktape 2.99.99 on all four on ubuntu (273/276/301/344 vs 288/315/783/584) and macos-arm64 (205/229/261/337 vs 538/632/1257/1032), and its executable is larger there (454.2K vs 370.4K on ubuntu); build configurations differ. Samsung's first-party slides (SunSpider 1.0.2 max RSS on Raspberry Pi 2, JerryScript 1.0 vs Duktape 1.5.1) report lower RSS for JerryScript, e.g. 3d-cube 35 vs 125 KB, 3d-raytrace 185 vs 339 KB, access-binary-trees 38 vs 160 KB, crypto-md5 142 vs 261 KB, but slideshare and summit.riot-os.org were blocked, so these come from a search snippet only. Last commit 2025-10-08 is one day inside the 12-month active window (the previous commit was 2025-06-03), so it turns stale on 2026-10-09. [retier] Memory win only, from third-party issue #4386 (no method; built with --system-allocator=ON, which the configuration docs call unsupported on 64-bit, architecture unstated; peak-memory units impossible, Node 73,873,464 'KB'). Slower than Duktape on all 8 V8 tests (250 vs 487); in the ahaoboy CI the stock build (tools/build.py, fixed 512 KB heap) scores nothing on EarleyBoyer, RegExp, Splay and NavierStokes, and 3.0.0 fails 4 of 8 tests. Samsung RSS slides seen as a snippet only. Open unanswered fuzzer memory-safety issues (#5302, #5272, #5282, #5291); only 2 commits since 3.0.0.

Footprint-first design: runs on devices with under 64 KB RAM and 200 KB flash, 258K binary on ARM Thumb-2, written in C99, snapshot support for precompiled bytecode. Full ECMAScript 5.1 compliance, about 70% of ECMAScript 2025 per README. The small footprint is bought with speed.

## Maintenance

Apache-2.0 and easy to vendor as amalgamated C, but development has slowed to two commits since the December 2024 3.0.0 release (last 2025-10-08, so it turns stale on 2026-10-09) while fuzzer-found memory-safety reports accumulate unanswered.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The only reachable numbers are a third-party GitHub issue (#4386) that compares JerryScript ESNext with Duktape and QuickJS on the V8 suite but states no hardware, compiler version or memory-measurement method, and its peak-memory figures are implausible as labelled; that is numbers without methodology, tier C. Samsung's first-party SunSpider RSS slides are blocked here (snippet only) and would also be C.
- **Verifier notes:** Issue #4386 numbers match the record; tier C stands (third-party, no methodology). Record as shortcomings: slower than Duktape on all eight V8 tests (250 vs 487), peak-memory figures implausible as labelled with no method, JerryScript built with system allocator and debugger, independent ahaoboy CI shows JerryScript 3.0.0 failing half the V8 suite and slower than Duktape on the rest; memory win corroborated only by Samsung's first-party slides (snippet only). Metadata confirmed: Apache-2.0, 7.4k stars, last commit 2025-10-08 (active by one day).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** third-party issue (verifier); enricher code reading
- **Pages the verifier opened:**
  - <https://github.com/jerryscript-project/jerryscript/issues/4386>
  - <https://github.com/jerryscript-project/jerryscript>
  - <https://github.com/jerryscript-project/jerryscript/commits/master.atom>
  - <https://raw.githubusercontent.com/jerryscript-project/jerryscript/HEAD/README.md>
  - <https://raw.githubusercontent.com/jerryscript-project/jerryscript/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/jerryscript-project/jerryscript>
  - <https://raw.githubusercontent.com/jerryscript-project/jerryscript/HEAD/README.md>
  - <https://raw.githubusercontent.com/jerryscript-project/jerryscript/HEAD/docs/00.GETTING-STARTED.md>
  - <https://raw.githubusercontent.com/jerryscript-project/jerryscript/HEAD/docs/01.CONFIGURATION.md>
  - <https://raw.githubusercontent.com/jerryscript-project/jerryscript/HEAD/docs/02.API-REFERENCE.md>
  - <https://raw.githubusercontent.com/jerryscript-project/jerryscript/HEAD/docs/04.INTERNALS.md>
  - <https://raw.githubusercontent.com/jerryscript-project/jerryscript/HEAD/docs/05.PORT-API.md>
  - <https://raw.githubusercontent.com/jerryscript-project/jerryscript/HEAD/docs/16.MIGRATION-GUIDE.md>
  - <https://raw.githubusercontent.com/jerryscript-project/jerryscript/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jerryscript-project/jerryscript/HEAD/jerry-core/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jerryscript-project/jerryscript/HEAD/jerry-core/config.h>
  - <https://raw.githubusercontent.com/jerryscript-project/jerryscript/HEAD/jerry-core/jmem/jmem-allocator.c>
  - <https://raw.githubusercontent.com/jerryscript-project/jerryscript/HEAD/jerry-core/jmem/jmem-heap.c>
  - <https://raw.githubusercontent.com/jerryscript-project/jerryscript/HEAD/tools/build.py>
  - <https://raw.githubusercontent.com/jerryscript-project/jerryscript/HEAD/LICENSE>
  - <https://github.com/jerryscript-project/jerryscript/issues/4386>
  - <https://github.com/jerryscript-project/jerryscript/commits/master>
  - <https://github.com/jerryscript-project/jerryscript/releases>
  - <https://github.com/jerryscript-project/jerryscript/issues?q=is%3Aissue+is%3Aopen+overflow>
  - <https://github.com/jerryscript-project/jerryscript/tree/master/tools>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/README.md>
  - <https://github.com/ahaoboy/jerryscript-build>
  - <https://raw.githubusercontent.com/ahaoboy/jerryscript-build/HEAD/.github/workflows/build.yml>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/jerryscript-project/jerryscript`) · [data/wave12/enrich/raw/github_com_jerryscript_project_jerryscript.json](../../../data/wave12/enrich/raw/github_com_jerryscript_project_jerryscript.json) (enrichment confidence 0.6)

</details>
