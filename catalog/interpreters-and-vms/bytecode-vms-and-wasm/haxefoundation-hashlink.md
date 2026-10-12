# HashLink (Haxe virtual machine, Neko successor)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Haxe's typed-bytecode VM with an x86-64 JIT and a C backend (HL/C); several times faster than the older NekoVM target.

| | |
|---|---|
| **Beats** | NekoVM (Haxe code compiled to the Neko target; also Haxe's Lua and Python targets, not stock Lua or CPython) |
| **Claimed result** | Third-party gist run of that suite (created 2018-06-28, Intel Core i5-6600, Arch Linux, kernel 4.17.2): total hl 5.68 s versus neko 27.16 s, 4.8x faster (derived from page data); per test Fib 0.08 vs 0.42 s, NBodies 0.13 vs 5.91 s, Anonymous 0.29 vs 4.57 s, Mandelbrot 4.28 vs 9.65 s. Same table: Haxe Lua target 60.55 s, Python target 48.73 s, PHP 12.59 s (hl about 10.7x, 8.6x and 2.2x faster, derived). Gist author's 2025-09-20 rerun on AMD Ryzen 7 7700: Fib hl 0.04 vs neko 0.58 s, Mandelbrot 1.32 vs 8.83 s (hlc column errored on every test). Slower than the other targets in the 2018 table: C++ 0.72 s, Java 0.81 s, JavaScript 0.96 s total. |
| **Workload** | The repo's other/benchs suite (Haxe programs Anonymous, BinaryTrees, Fib, FloatArray, IntArray, Mandelbrot, NBodies) compiled to each Haxe target and run as a process, startup time subtracted, in a third-party run. |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-6600 @ 3.9 GHz, 15959 MB, Arch Linux, kernel 4.17.2 (2018 run); AMD Ryzen 7 7700, 32 GB, Arch Linux kernel 6.16.8 (2025 rerun) |
| **Compiler and flags** | Per other/benchs/Benchs.hx: haxe with -dce full for every target; hlc built with gcc -O3 -std=c11; hxcpp with -D HXCPP_GC_GENERATIONAL; Haxe, HashLink and Neko versions not visible on the page |
| **Adoption** | 905 stars, 202 forks |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/HaxeFoundation/hashlink) · [benchmark](https://gist.github.com/tong/84992efadb204c2140e24dbdbeeee06c) |

## Verdict

A third-party gist ran the repo's other/benchs suite (7 Haxe programs, each run as a process for at least 1 s, startup subtracted) on an Intel Core i5-6600 under Arch Linux in 2018: HashLink JIT took 5.65 s in total vs NekoVM 27.12 s (about 4.8x), and the author's 2025 rerun on a Ryzen 7 7700 gives 2.00 s vs 21.62 s (about 10.8x); versions are not stated and HashLink loses to the hxcpp, JVM and Node targets in both runs (ratios derived from page data).

## Use it when

- Haxe projects still on the Neko target (tools, servers, scripts): in a third-party run HL JIT finished the repo's 7-program suite in 5.65 s vs Neko 27.12 s (about 4.8x, 12.8x without Mandelbrot), and 2.00 s vs 21.62 s (about 10.8x) in the 2025 rerun (derived from page data)
- Games and desktop apps built with Heaps on x86-64 Windows, Linux or macOS, where the JIT gives fast edit-run cycles and HL/C gives a native release build
- When you want hot reload, the HashLink CPU profiler or the VS Code debugger during development, then ship HL/C
- Consoles and ARM targets via HL/C, since the generated C only needs libhl and a C11 compiler

## Skip it when

- Raw throughput on allocation-heavy code: in the same 2018 table HL took 4.28 s on Mandelbrot (allocates a Complex object per iteration) vs 0.13 s for hxcpp and 0.10 s for Node, and 1.32 s vs 0.07 s (Node and JVM) in 2025; hxcpp, JVM and JS targets are faster across the suite
- ARM64 with the JIT: the 1.16 JIT errors out on ARM ('only x86 and x86-64 are supported, please use HashLink/C') and the Makefile skips building the hl VM on arm64; only HL/C works there
- Non-Haxe languages: the bytecode is produced only by the Haxe compiler, so this is not a general embeddable VM like the catalogued Wasm runtimes
- Tracking master in production: master is HL_VERSION 2.0 with a restructured JIT (jit_emit.c, jit_regs.c, jit_x86_64.c) and an open regression (#988, 'JIT ERROR get_tmp_args:294 (Too many arguments)', not seen on the 1.16 tag); use the 1.16 release
- Latency-sensitive apps with large heaps: the GC is non-generational stop-the-world marking (threads are paused via gc_stop_world), so pause time grows with live heap size

## How it is fast

Haxe's static types are kept in a strictly typed, register-based bytecode, so the JIT (one 4,771-line jit.c in 1.16) can emit x86/x86-64 machine code with integer registers and SSE scalar float instructions (ADDSD, MULSD) from each function's typed opcodes. HL/C goes further by handing the same typed code to an optimizing C compiler (gcc -O3 in the repo's bench script). Memory is managed by a non-moving, mostly precise mark collector over 64 KB pages, with parallel mark threads (up to 16 on master; 'multiple mark threads' since 1.14).

## Compared with alternatives

No catalogued sibling runs Haxe: pick HashLink when your code is Haxe and you are moving off Neko, or want JIT development plus an HL/C release build; for a general-purpose embeddable bytecode VM for other languages, pick a Wasm runtime such as WAMR or wasm3 instead.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | core libhl: libc, libm, pthread, bundled PCRE2; optional .hdll libraries: libpng, libturbojpeg, libvorbis (fmt), OpenAL, SDL3 plus GLU (sdl), mbedTLS (ssl), libuv, SQLite, MySQL; the Haxe compiler to produce .hl or HL/C output |
| **Minimum toolchain** | C11 compiler (Makefile uses -std=c11 -O3); Visual Studio solution hl.sln on Windows; SDL3 must be built from source on current Ubuntu per the README |
| **Platforms** | JIT (hl): x86 and x86-64 on Windows, Linux, macOS; HL/C: any platform with a C11 compiler, including arm64 (the Makefile builds only libhl and .hdll files on arm64) |
| **Thread safety** | Multithreaded builds (HL_THREADS) are supported; the GC pauses registered threads for marking (gc_stop_world), so native threads that touch HL values must be registered (hl_register_thread); thread safety of Haxe-level data structures is not documented |
| **Drop-in for the baseline** | partial — same Haxe source recompiled with -hl instead of -neko, but Neko-specific packages and .ndll native extensions do not carry over |

## Gotchas

- Harness resolution: the bench script subtracts a startup estimate (the _Startup.hx run) and truncates each time to 10 ms (Std.int(et\*100)/100), and five of seven HL cells are 0.03-0.13 s, so per-test ratios such as FloatArray 48x are resolution-limited; Mandelbrot alone is 76% of HL's 2018 total. When a single benchmark is selected, _Startup is skipped and the reported time is not startup-corrected.
- No usable HL/C numbers in the 2025 rerun: every hlc cell is 'hlc result 0 but expected N', and 0 is the _Startup program's expected result, so each benchmark ran a stale _Startup hlc binary (or stale generated C) rather than failing; the hl JIT column is unaffected.
- Evidence is a personal gist with a modified script (it adds cs, java, lua, php and python targets that Benchs.hx does not have) and no Haxe, HashLink or Neko versions; the 'lua' and 'python' columns are Haxe compiled to those targets, not stock Lua or CPython, and Neko is HashLink's own predecessor, a weak baseline.
- HL JIT is much slower than HL/C or native C on numeric code: haddock7/hashlink_benchmark (OpenSimplex noise, HashLink 1.11.0, i7-7500U) has HL VM 16.76 s, HL/C 5.91 s, native C 3.88 s (HL VM 4.32x slower than native).

## Known shortcomings

- Evidence is a personal gist created 2018-06-28 (not 2016) by tong with versions unstated and the modified script unpublished; the 2025 re-run by the gist author had every hlc cell error out. Slower than hxcpp, the JVM and Node; NekoVM is not on the category baseline list.
- Enricher: in the 2025 gist rerun every hlc cell printed 0, which is _Startup's expected result, so a stale _Startup hlc binary or stale generated C ran each time and there are no HL/C numbers. Benchs.hx truncates times to 10 ms after subtracting startup, so tiny cells (FloatArray 48x) are noise; Mandelbrot is 76% of HL's 2018 total. hl vs neko: 4.8x total in 2018, 10.8x in 2025 (derived from page data). The JIT is x86/x86-64 only (1.16 jit.c errors on ARM, Makefile skips hl on arm64); master is HL_VERSION 2.0 with a split JIT and open regression #988. Non-generational GC; loses to hxcpp, the JVM and Node.

## Caveats and trade-offs

The README has no numbers. The in-repo benchmark suite (other/benchs/Benchs.hx: hl, hlc, js, neko, cpp and swf/AIR targets) has no committed results; the figures come from a personal gist by a Haxe community member (created 2018-06-28, not 2016) whose table also has cs, java, lua, php and python targets that the in-repo script does not build, so the exact script is not published and tool versions are not stated; tier stays C. The 'Lua' and 'Python' columns are Haxe compiled to those targets, not hand-written Lua 5.x or CPython. HashLink loses to hxcpp, JVM and Node in the same table (Mandelbrot 4.28 s vs 0.10 s for JavaScript); in the 2025 rerun every hlc (HashLink/C) cell is an error ('hlc result 0 but expected'). A second repository (haddock7/hashlink_benchmark, i7-7500U, HashLink 1.11.0, OpenSimplex noise) has HashLink VM 16.76 s, HashLink/C 5.91 s, native C 3.88 s, i.e. HL VM 4.32x slower than native C. Haxe's 'HashLink InDepth' blog (haxe.org, blocked here) reportedly says HL/JIT beats Adobe AIR and Node/V8 in many cases (search snippet only), which the gist's numbers do not support for Node. NekoVM is not one of the category's listed baselines (wasmtime, wasmer, WAMR, V8).

Strictly typed register bytecode with a JIT (hl) or a C backend (HL/C); needs libhl plus optional SDL, OpenAL, SQLite and other native libraries; Haxe-only; debugging through a VS Code extension.

## Maintenance

Actively maintained by the Haxe Foundation (commits to 2026-10-06, release 1.16 plus nightlies; master is 2.0 development with a reworked JIT), MIT-licensed and copyable, but only useful to Haxe code and its JIT is x86/x86-64 only.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** Third-party gist (tong, created 2018-06-28) states the CPU and OS but no Haxe, HashLink or Neko versions, and its targets (cs, java, lua, php, python) are not in the in-repo other/benchs/Benchs.hx, so the script that produced it is not public; a personal gist is not a well-known suite, so C.
- **Verifier notes:** Gist numbers match the record; the gist was created 2018-06-28 (revisions page), not 2016, and the 2025 rerun is the gist author's own comment. Licence MIT, 905 stars, last commit 2026-10-06 verified. Shortcomings: only a personal gist with unstated versions and an unpublished modified script, baseline NekoVM is off the category list, HashLink is slower than hxcpp/JVM/Node, hlc errored in the 2025 rerun.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `baseline_in_list`, `caveats`
- **Shortcomings recorded by:** published script with versions; benchs.haxe.org suite results with versions
- **Pages the verifier opened:**
  - <https://gist.github.com/tong/84992efadb204c2140e24dbdbeeee06c>
  - <https://gist.github.com/tong/84992efadb204c2140e24dbdbeeee06c/revisions>
  - <https://github.com/HaxeFoundation/hashlink>
  - <https://github.com/HaxeFoundation/hashlink/commits>
  - <https://raw.githubusercontent.com/HaxeFoundation/hashlink/HEAD/other/benchs/Benchs.hx>
  - <https://github.com/haddock7/hashlink_benchmark>
- **Sources the enricher read:**
  - <https://github.com/HaxeFoundation/hashlink>
  - <https://raw.githubusercontent.com/HaxeFoundation/hashlink/HEAD/README.md>
  - <https://raw.githubusercontent.com/HaxeFoundation/hashlink/HEAD/Makefile>
  - <https://raw.githubusercontent.com/HaxeFoundation/hashlink/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/HaxeFoundation/hashlink/HEAD/src/jit.c>
  - <https://raw.githubusercontent.com/HaxeFoundation/hashlink/HEAD/src/jit_x86_64.c>
  - <https://raw.githubusercontent.com/HaxeFoundation/hashlink/HEAD/src/hl.h>
  - <https://raw.githubusercontent.com/HaxeFoundation/hashlink/HEAD/src/gc.c>
  - <https://raw.githubusercontent.com/HaxeFoundation/hashlink/HEAD/src/main.c>
  - <https://raw.githubusercontent.com/HaxeFoundation/hashlink/1.16/src/jit.c>
  - <https://raw.githubusercontent.com/HaxeFoundation/hashlink/1.16/src/hl.h>
  - <https://github.com/HaxeFoundation/hashlink/tree/master/other/benchs>
  - <https://raw.githubusercontent.com/HaxeFoundation/hashlink/HEAD/other/benchs/Benchs.hx>
  - <https://raw.githubusercontent.com/HaxeFoundation/hashlink/HEAD/other/benchs/_Startup.hx>
  - <https://raw.githubusercontent.com/HaxeFoundation/hashlink/HEAD/other/benchs/Mandelbrot.hx>
  - <https://raw.githubusercontent.com/HaxeFoundation/hashlink/HEAD/other/benchs/Anonymous.hx>
  - <https://raw.githubusercontent.com/HaxeFoundation/hashlink/HEAD/other/benchs/NBodies.hx>
  - <https://raw.githubusercontent.com/HaxeFoundation/hashlink/HEAD/other/benchs/benchs.hxml>
  - <https://github.com/HaxeFoundation/hashlink/releases>
  - <https://github.com/HaxeFoundation/hashlink/commits>
  - <https://github.com/HaxeFoundation/hashlink/issues?q=is%3Aissue+jit+crash>
  - <https://github.com/HaxeFoundation/hashlink/issues/988>
  - <https://github.com/HaxeFoundation/hashlink/wiki>
  - <https://github.com/HaxeFoundation/hashlink/wiki/Notes-on-Garbage-Collector>
  - <https://gist.github.com/tong/84992efadb204c2140e24dbdbeeee06c>
  - <https://github.com/haddock7/hashlink_benchmark>
  - <https://github.com/HaxeBenchmarks/benchmark-runner>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/haxefoundation/hashlink`) · [data/wave12/enrich/raw/github_com_haxefoundation_hashlink.json](../../../data/wave12/enrich/raw/github_com_haxefoundation_hashlink.json) (enrichment confidence 0.7)

</details>
