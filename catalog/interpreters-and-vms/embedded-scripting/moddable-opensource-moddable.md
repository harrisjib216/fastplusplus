# XS JavaScript engine (Moddable SDK)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `XS engine sources (xs/sources) are LGPL-3.0-or-later and incorporate Apache-2.0 code from Kinoma/Marvell; SDK build tools GPL-3.0, examples CC-BY-4.0, some fonts OFL-1.1 (licenses/readme.md); a commercial licence is also offered` · 🟢 active

> XS, Moddable's ROM-friendly C JavaScript engine for microcontrollers; beat Duktape 2.3.0 by about 1.6x on bench-v8 in 2019, not in 2026 CI.

| | |
|---|---|
| **Beats** | Duktape 2.3.0 |
| **Claimed result** | 2019 QuickJS bench-v8 table (XS 8.8.0 vs Duktape 2.3.0, total without RegExp 738 vs 468, about 1.6x derived from page data; Duktape faster on Splay and NavierStokes; XS slower than QuickJS 1138). Current release reversed: ahaoboy/js-engine-benchmark 2026-10-05 has XS 17.9.3 xst at 266 vs Duktape 2.99.99 at 489 on ubuntu and 380 vs 905 on macOS arm64, losing every ubuntu subtest. |
| **Workload** | bench-v8 version 7 scores in Bellard's QuickJS benchmark table (RegExp disabled for XS because the engine could not run it); higher is better. |
| **Metric** | throughput |
| **Hardware** | 3.2 GHz Core i5 4570 |
| **Compiler and flags** | gcc 4.9.2 on Fedora 21; XS 8.8.0 xst x86 64-bit -O3; Duktape 2.3.0 -O2 |
| **Adoption** | 1.6k stars |
| **Last commit** | 2026-09-04 |
| **Links** | [repository](https://github.com/Moddable-OpenSource/moddable) · [benchmark](https://raw.githubusercontent.com/quickjs-zh/QuickJS/HEAD/bench.md) |

## Verdict

Bellard ran bench-v8 version 7 in 2019 (gcc 4.9.2 on Fedora 21, Core i5 4570 at 3.2 GHz, xst built at -O3, Duktape at -O2, RegExp disabled for XS). XS 8.8.0 totalled 738 without RegExp against 468 for Duktape 2.3.0 (about 1.6x, derived from page data) and won 5 of 7 tests, losing Splay and NavierStokes. The independent 2026-10-05 GitHub Actions run of the same suite reverses the ranking: Moddable's prebuilt XS 17.9.3 xst scored 266 against Duktape 2.99.99 at 489 on ubuntu, and 380 against 905 on macOS arm64.

## Use it when

- JavaScript on ESP32/ESP8266-class microcontrollers with tens of KB of RAM, where a ROM-prepared VM and precompiled bytecode matter more than raw interpreter speed.
- You need modern ECMAScript on a device: Moddable reports 98.88% of test262 language tests and 88.94% of built-ins passing on macOS (XS Conformance, revised 2026-01-31).
- You want a whole embedded JavaScript platform (build tools, drivers, graphics and UI frameworks, debugger xsbug, precompiled 'mods') rather than only an engine, with a commercial licence available if LGPL-3.0 does not fit.
- Locked-down, frozen-realm style deployments where the linker can freeze built-ins and strip eval/Function to drop the parser from the image.

## Skip it when

- Choosing an engine for interpreter throughput: in the 2026-10-05 ahaoboy/js-engine-benchmark CI run of the same bench-v8 v7 suite, XS 17.9.3 (Moddable's prebuilt xst) scored 266 on ubuntu against Duktape 2.99.99 at 489, QuickJS 2026.06.04 at 1217 and Hermes 0.12.0 at 1530. On macOS arm64 it scored 380 against Duktape 905 and QuickJS 1761.
- Replacing Duktape for speed: the 1.6x win is a 2019 result on XS 8.8.0 and the current CI shows the reverse. XS also scored below MuJS 1.3.8 there (266 vs 329 on ubuntu, 380 vs 585 on macOS arm64).
- Products that cannot meet LGPL-3.0 relinking obligations for the runtime or GPL-3.0 for the build tools, unless you buy Moddable's commercial licence.
- Code that depends on UTF-16 string semantics, Intl (ECMA-402), Annex B, multiple realms per VM or Function.prototype.toString: XS strings are UTF-8 indexed by code point unless built with mxCESU8, there is one realm per machine, and toString of functions always fails.
- Windows desktop use as a benchmarked engine: the 2026 CI produced no Windows score for xst.

## How it is fast

XS moves work off the device: the xsc compiler turns modules into bytecode on the development machine, and the XS linker builds the built-ins and preloaded modules into a prepared virtual machine stored in ROM. Bytecode and objects run in place from flash, boot is close to instant, and RAM holds only what scripts change. Objects that are modified get cloned through an alias table, and frozen objects skip it. The linker can also dead-strip unused built-ins and colour ROM properties for faster lookup. At run time it is a bytecode interpreter with GCC computed-goto dispatch (a label table in xsRun.c, used when compiled with optimisation), an integer slot type that skips floating point, in-place ROM strings (stringx), and a mark-and-sweep collector that compacts the chunk heap.

## Compared with alternatives

Pick XS over QuickJS only when the target is a microcontroller where XS's ROM-prepared VM, linker dead-stripping and the Moddable hardware SDK matter. QuickJS is about 1.5x faster in Bellard's 2019 table and about 4.6x faster in the 2026 CI (1217 vs 266 on ubuntu, derived from page data). For a desktop or server embedding, QuickJS or Hermes are the faster small engines.

## Integration

| | |
|---|---|
| **Form** | source-drop (xs/sources plus a platform layer) or the Moddable SDK toolchain (xsc, xsl, mcconfig) for devices |
| **Dependencies** | none beyond libc/libm for the engine core as built here; the xst test tool links LibYAML, fdlibm, pthread and libatomic |
| **Minimum toolchain** | C compiler; computed-goto dispatch needs GCC-compatible extensions with optimisation on, otherwise a switch is used; minimum standard not documented |
| **Platforms** | microcontrollers targeted by the Moddable SDK (ESP8266 and ESP32 named in the docs) plus macOS, Linux and Windows hosts (xst makefiles for lin, mac and win) |
| **Thread safety** | A single machine does not support multiple threads (XS in C); create one machine per thread and pass messages through the host |
| **Drop-in for the baseline** | no |

## Gotchas

- The headline claim did not hold for the current release: in the 2026-10-05 ahaoboy CI, XS 17.9.3 loses every bench-v8 sub-test to Duktape on ubuntu (for example Richards 89 vs 288, Splay 373 vs 1234). On macOS arm64 it wins only RegExp (283 vs 244). That Duktape is an unreleased 2.99.99 master built at -Os. The drop from 2019 is very large (Richards 444 on a 2013 Core i5 vs 89 on a CI runner), so the prebuilt binary's configuration may explain part of it. Moddable's release build settings for xst-lin64.zip are not documented, and the reversal was not resolved here.
- Both data points time xst, the test262 harness, not an embedder build. xs/makefiles/lin/xst.mk compiles every goal with -DmxDebug=1 and -DmxProfile=1, which add debugger and profiler checks to the interpreter's line opcodes (xsRun.c). Its default GOAL is debug (-O0 with AddressSanitizer), so a plain 'make' reproduction measures a sanitizer build. Bellard's 2019 table also built XS at -O3 against -O2 for Duktape.
- The chunk heap is compacted during garbage collection, so pointers from xsToString or xsToArrayBuffer, and host-chunk pointers, go stale after any call that can allocate, run JavaScript, coerce or throw. Refetch them after such calls, and never touch them from interrupts.
- XS in C reports errors with setjmp/longjmp, so C callbacks that hold native resources across XS macros need xsTry/xsCatch to release them.

## Known shortcomings

- On the same 2019 QuickJS bench-v8 table XS (738) is slower than QuickJS (1138) and was built -O3 against Duktape at -O2; XS 8.8.0 from 2019, RegExp not run. XS sources are LGPL-3.0-or-later including Apache-2.0 Kinoma code.
- Enricher: the claim is reversed on the current release: ahaoboy CI 2026-10-05 has XS 17.9.3 xst at 266 vs Duktape 2.99.99 at 489 on ubuntu and 380 vs 905 on macOS arm64, losing every ubuntu subtest and sitting below MuJS. xst.mk compiles every goal with -DmxDebug=1 -DmxProfile=1 (line-opcode hooks in xsRun.c) and its default GOAL is debug (-O0 plus ASan), so both data points time xst rather than an embedder build and the prebuilt xst configuration is undocumented.

## Caveats and trade-offs

Benchmark was run by the QuickJS author in 2019 on XS 8.8.0, a much older version than today's; XS lost two of seven tests (Splay, NavierStokes) to Duktape and could not run RegExp. On the same table XS is clearly slower than QuickJS (738 vs 1138 total without RegExp, derived from page data about 0.65x), and QuickJS is also a baseline of this category, so the win holds only against Duktape. XS was built at -O3 while Duktape was built at -O2. The XS engine lives under xs/ inside the Moddable SDK repository. First-party performance claims by Moddable were not found. [retier] The 2019 win was measured by the QuickJS author on XS 8.8.0 built -O3 against Duktape at -O2, RegExp not run; on the same table XS is well behind QuickJS. The independent ahaoboy CI of 2026-10-05 shows XS 17.9.3 slower than Duktape and below MuJS on every ubuntu subtest. Both data points time xst, not an embedder build: xst.mk compiles every goal with -DmxDebug=1 -DmxProfile=1 (line-opcode hooks in xsRun.c) and its default GOAL is debug (-O0 plus ASan), and the prebuilt xst configuration is undocumented. XS sources are LGPL-3.0-or-later with Apache-2.0 Kinoma code.

Targets microcontrollers (README: devices with about 45 KB free RAM); executable 1.2M vs 331K for Duktape in the table; multi-licence SDK, so check which licence applies to the XS sources you copy.

## Maintenance

Actively maintained by Moddable (SDK release 9.5.0 on 2026-09-05, commits through 2026-09-04, 1.6k stars). Usable under LGPL-3.0 or a commercial licence, but its claim to beat Duktape on speed rests on 2019 numbers that current builds do not reproduce.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now B.
- **Tier reason:** Third-party bench-v8 v7 table by the QuickJS author (Chinese mirror of bellard.org/quickjs/bench.html) has XS 8.8.0 and Duktape 2.3.0 columns with every number in the record; benchmark code is the bench-v8 suite run by the bellard/quickjs Makefile target bench-v8 (tests/bench-v8, shipped in the quickjs-extras archive), gcc 4.9.2, -O3 for XS and -O2 for Duktape, Core i5 4570 stated. Same page and tier as the already-verified QuickJS entry.
- **Retiered** A to B: A to B: the 2019 table is an independent run by the QuickJS author, but the XS build configuration behind it is undocumented (xst.mk compiles every goal with mxDebug and mxProfile hooks, default GOAL is a debug build) and the independent ahaoboy CI of 2026-10-05 reverses the claim (XS 17.9.3 at 266 vs Duktape 489 on ubuntu), so the Duktape win does not hold on current code.
- **Verifier notes:** Numbers verified exactly on the mirror page (738/468 = about 1.6x, derived from page data); original bellard.org page is EGRESS_BLOCKED here. Shortcomings to record: 2019 numbers on XS 8.8.0, slower than QuickJS on the same table, flag mismatch (-O3 vs -O2), RegExp not runnable.
- **Fields the verifier corrected:** `license`, `caveats`, `claimed_speedup`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/quickjs-zh/QuickJS/HEAD/bench.md>
  - <https://github.com/Moddable-OpenSource/moddable>
  - <https://github.com/Moddable-OpenSource/moddable/commits/public>
  - <https://raw.githubusercontent.com/Moddable-OpenSource/moddable/public/licenses/readme.md>
  - <https://raw.githubusercontent.com/Moddable-OpenSource/moddable/public/xs/sources/xsRun.c>
  - <https://raw.githubusercontent.com/bellard/quickjs/HEAD/Makefile>
- **Sources the enricher read:**
  - <https://github.com/Moddable-OpenSource/moddable>
  - <https://github.com/Moddable-OpenSource/moddable/commits/public>
  - <https://github.com/Moddable-OpenSource/moddable/releases/latest>
  - <https://github.com/Moddable-OpenSource/moddable/tree/public/.github>
  - <https://raw.githubusercontent.com/Moddable-OpenSource/moddable/public/licenses/readme.md>
  - <https://raw.githubusercontent.com/Moddable-OpenSource/moddable/public/documentation/readme.md>
  - <https://raw.githubusercontent.com/Moddable-OpenSource/moddable/public/documentation/xs/XS%20in%20C.md>
  - <https://raw.githubusercontent.com/Moddable-OpenSource/moddable/public/documentation/xs/XS%20Differences.md>
  - <https://raw.githubusercontent.com/Moddable-OpenSource/moddable/public/documentation/xs/XS%20Conformance.md>
  - <https://raw.githubusercontent.com/Moddable-OpenSource/moddable/public/xs/makefiles/lin/xst.mk>
  - <https://raw.githubusercontent.com/Moddable-OpenSource/moddable/public/xs/makefiles/mac/xst.mk>
  - <https://raw.githubusercontent.com/Moddable-OpenSource/moddable/public/xs/sources/xsCommon.h>
  - <https://raw.githubusercontent.com/Moddable-OpenSource/moddable/public/xs/sources/xsRun.c>
  - <https://raw.githubusercontent.com/quickjs-zh/QuickJS/HEAD/bench.md>
  - <https://github.com/ahaoboy/js-engine-benchmark>
  - <https://github.com/ahaoboy/js-engine-benchmark/tree/main/.github/workflows>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/.github/workflows/update.yml>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-setup/HEAD/action.yml>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-setup/HEAD/README.md>
  - <https://raw.githubusercontent.com/ahaoboy/easy-install/main/dist-manifest/xst.json>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/moddable-opensource/moddable`) · [data/wave12/enrich/raw/github_com_moddable_opensource_moddable.json](../../../data/wave12/enrich/raw/github_com_moddable_opensource_moddable.json) (enrichment confidence 0.75)

</details>
