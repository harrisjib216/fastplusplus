# MicroQuickJS (MQuickJS)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `MIT` · 🟢 active

> Bellard's ES5-subset JavaScript engine for microcontrollers: runs scripts in about 10 kB RAM and 100 kB ROM; speed only 'comparable' to QuickJS.

| | |
|---|---|
| **Beats** | QuickJS (Bellard); the README is the only comparison and gives no QuickJS numbers |
| **Claimed result** | No speed-up claimed: 'The speed is comparable to QuickJS.' Memory claim without a QuickJS figure: programs run in as little as 10 kB of RAM, whole engine about 100 kB ROM. |
| **Workload** | Not measured against QuickJS in the README; the README describes running JavaScript in as little as 10 kB of RAM with about 100 kB of ROM (ARM Thumb-2 code including the C library) and references 'make microbench' and an Octane run. |
| **Metric** | memory |
| **Adoption** | 6.2k stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/bellard/mquickjs) · [benchmark](https://github.com/bellard/mquickjs) |

## Verdict

No measurement backs a comparison: the README states that scripts run in as little as 10 kB of RAM and that the engine needs about 100 kB of ARM Thumb-2 ROM including the C library, and that speed is 'comparable to QuickJS', with no QuickJS figures, compiler flags or hardware. The in-repo microbench target cannot print a QuickJS reference column, and one web search found no independent MQuickJS-versus-QuickJS numbers.

## Use it when

- Microcontrollers with tens of kB of RAM and about 100 kB of flash where QuickJS's roughly 1 MB binary and malloc-based reference-counted heap do not fit (README: mandelbrot.js runs with --memory-limit 10k).
- Firmware that must not depend on libc malloc or on a growing heap: all engine memory lives in one fixed buffer you size up front, and out-of-memory becomes a JS exception.
- Scripts precompiled on the host (mqjs -o, with -m32 for 32-bit targets) and executed from ROM, so the device ships no parser input and instantiation is nearly free.
- Targets without an FPU: the engine carries its own small libm and an optional soft-float emulator (CONFIG_SOFTFLOAT).

## Skip it when

- Running existing ES2015+ code: the parser handles only var and function declarations (no let, const, arrow functions or classes), the mqjs stdlib has no Map, Set, Promise, Symbol, Proxy or BigInt, and there are no modules, custom iterators or array holes; use QuickJS or XS instead.
- Throughput-bound scripting on a PC or Linux-class device: the only speed statement is 'comparable to QuickJS' with no numbers, and QuickJS itself is 15-40x slower than JIT engines on the V8 suite.
- Loading untrusted bytecode: the README says bytecode is not verified and must come from trusted sources.
- Hostile or fuzzer-grade input without patching: closed issues #32-#56 (Dec 2025 to Jan 2026) report heap-buffer overflows in JS_Call, get_u16 and get_u32, SEGVs in gc_mark_all, JS_GetPropertyInternal and lre_exec, and memory corruption in string_buffer_concat_str, all within the first month of the public release.
- Deep C-to-JS re-entry: JS_MAX_CALL_RECURSE is 8, so more than eight nested JS_Call levels from C callbacks throw 'C stack overflow'.

## How it is fast

The win is footprint, not throughput. A tracing, compacting garbage collector replaces QuickJS's reference counting, so objects are smaller (3 CPU words minimum) and the heap never fragments; JSValue is one machine word (31-bit ints, single code points and, on 64-bit hosts, short floats are immediate), strings are WTF-8, property keys are plain JSValues, and most built-in functions are single immediate values stored in ROM so context creation allocates almost nothing. The parser is non-recursive and the VM keeps its stack inside the same buffer, so C stack use is bounded; bytecode is generated in one pass (QuickJS runs several optimisation passes) and line/column tables are exponential-Golomb coded.

## Compared with alternatives

Pick MQuickJS over QuickJS or the XS engine (Moddable SDK) only when RAM is measured in tens of kB and an ES5 subset is acceptable; QuickJS gives near-complete ES2025 and 2.3x Duktape throughput on Linux-class hardware, and XS gives modern ECMAScript on microcontrollers with a larger footprint.

## Integration

| | |
|---|---|
| **Form** | source-drop (mquickjs.c, dtoa.c, libm.c, cutils.c plus a stdlib header generated at build time by a host-compiled tool) |
| **Dependencies** | none at run time beyond a few libc string/math symbols (no malloc, free or printf); building needs a host C compiler to run the stdlib generator |
| **Minimum toolchain** | GCC (Makefile uses gcc, GNU extensions such as __attribute__ and ##__VA_ARGS__); minimum version and C standard not documented |
| **Platforms** | 32-bit and 64-bit CPUs (ARM Thumb-2 cross build via CONFIG_ARM32, x86-32, Win32/Win64 via MinGW); bytecode depends on endianness and word size |
| **Thread safety** | not documented; all engine state lives in the caller's buffer and the source has no mutable globals outside debug builds, so one context per thread looks possible, but a context must not be shared |
| **Drop-in for the baseline** | partial: the C API resembles QuickJS's but differs (no JS_FreeValue, moving GC with JSGCRef handles, ROM stdlib tables), and only a strict ES5-like JavaScript subset runs |

## Gotchas

- Harness flaw behind the speed claim: 'make microbench' runs QuickJS's tests/microbench.js, but its reference comparison reads microbench.txt through the QuickJS-only std.open; mqjs defines no std object, so load_result returns null and the target prints absolute ns per test with no QuickJS column (BigInt tests and several others are also dropped). Nothing in the repository produces a QuickJS comparison, and the patched Octane lives in a bellard.org tarball that was not reachable.
- The default build is size-optimised (CONFIG_SMALL=y gives -Os) while QuickJS builds at -O2; any speed comparison should set CONFIG_SMALL off or say which build was timed.
- Objects move on every allocation: a JSValue held in a C local across any API call that allocates is a dangling value unless it sits in a JSGCRef; build with DEBUG_GC on a PC to force moves and catch this.
- GC runs only when the heap meets the VM stack inside the buffer (the source TODO lists 'launch gc at regular intervals'), so pause length scales with the buffer size; on 32-bit targets every non-integer double is a heap-allocated box, so float-heavy code churns the heap there.

## Known shortcomings

- Directional only: the README says speed is 'comparable' to QuickJS with no numbers and no QuickJS memory figures; ES5 subset. Kept for notability (6.2k stars).
- Enricher: 'make microbench' cannot make a QuickJS comparison (its reference column needs std.open, which mqjs lacks, so load_result returns null and only absolute nanoseconds print; BigInt tests dropped), the Octane harness lives only in the blocked bellard.org tarball, and the default build is -Os (CONFIG_SMALL=y) against QuickJS's -O2, so 'comparable speed' has nothing behind it. The parser handles only var and function (no let, const, arrows or classes), no Map, Set, Promise or BigInt; closed issues #32-#56 were fuzzer heap overflows and SEGVs in the first month; JS_MAX_CALL_RECURSE is 8; GC runs only when the heap meets the stack; floats are boxed on 32-bit.

## Caveats and trade-offs

No numbers for QuickJS are given, so the memory advantage is not quantified, and speed is stated to be merely comparable (not faster). MQuickJS supports only a subset of JavaScript close to ES5 (stricter mode), so it is not a drop-in QuickJS replacement. Kept as a notable tier D entry for the memory-footprint claim; the benchmark inputs (QuickJS microbench via 'make microbench', patched Octane) come from a separate tarball on bellard.org that is blocked here and was not opened.

Supports only a stricter ES5-like subset of JavaScript; tracing compacting GC, no dependency on malloc, UTF-8 strings, standard library lives in ROM so instantiation is nearly free. C API similar to QuickJS but not compatible.

## Maintenance

Active (first public version 2025-12-22, 54 commits, latest 2026-09-26 fixing user finalizers and exception propagation in JS_CFUNC_f_f), MIT-licensed and small enough to vendor, but young: no version numbers or release tags yet (open issues #18 and #69) and a burst of fuzzer-found memory-safety bugs in its first month.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification D, tier now D.
- **Tier reason:** The README compares with QuickJS only qualitatively ('The speed is comparable to QuickJS') and gives absolute footprint figures (10 kB RAM, about 100 kB ARM Thumb-2 ROM) with no QuickJS figure, so there is no measured advantage over the baseline.
- **Verifier notes:** README text matches the record exactly; MIT, 6.2k stars, last commit 2026-09-26, not a fork. Not rejected: notable (6.2k stars) and the claim is footprint rather than speed. Shortcomings: no QuickJS numbers for memory, speed only 'comparable', ES5 subset. One WebSearch found no independent MQuickJS-vs-QuickJS numbers (only a Zig port's self-comparison).
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/bellard/mquickjs>
  - <https://github.com/bellard/mquickjs/commits>
  - <https://raw.githubusercontent.com/bellard/mquickjs/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/bellard/mquickjs>
  - <https://github.com/bellard/mquickjs/commits>
  - <https://github.com/bellard/mquickjs/issues>
  - <https://github.com/bellard/mquickjs/issues?q=is%3Aissue+is%3Aclosed>
  - <https://github.com/bellard/mquickjs/issues/37>
  - <https://github.com/bellard/mquickjs/tree/main/tests>
  - <https://raw.githubusercontent.com/bellard/mquickjs/HEAD/README.md>
  - <https://raw.githubusercontent.com/bellard/mquickjs/HEAD/Makefile>
  - <https://raw.githubusercontent.com/bellard/mquickjs/HEAD/Changelog>
  - <https://raw.githubusercontent.com/bellard/mquickjs/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/bellard/mquickjs/HEAD/mquickjs.h>
  - <https://raw.githubusercontent.com/bellard/mquickjs/HEAD/mquickjs.c>
  - <https://raw.githubusercontent.com/bellard/mquickjs/HEAD/mqjs.c>
  - <https://raw.githubusercontent.com/bellard/mquickjs/HEAD/mqjs_stdlib.c>
  - <https://raw.githubusercontent.com/bellard/mquickjs/HEAD/example.c>
  - <https://raw.githubusercontent.com/bellard/mquickjs/HEAD/tests/microbench.js>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/README.md>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/bellard/mquickjs`) · [data/wave12/enrich/raw/github_com_bellard_mquickjs.json](../../../data/wave12/enrich/raw/github_com_bellard_mquickjs.json) (enrichment confidence 0.75)

</details>
