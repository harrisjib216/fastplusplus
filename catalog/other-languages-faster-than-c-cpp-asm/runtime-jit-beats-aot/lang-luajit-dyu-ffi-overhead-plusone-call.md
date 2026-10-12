# LuaJIT 2.0 FFI: dyu/ffi-overhead plusone() call loop

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Lua` · `Apache-2.0` · 🔴 abandoned

> LuaJIT FFI calls a shared-library C function about 1.3x faster than a dynamically linked C caller going through the PLT.

| | |
|---|---|
| **Beats** | C and C++ (gcc 5.4.1 -O2) calling plusone() in the shared library libnewplus.so through the dynamic linker |
| **Claimed result** | LuaJIT 891 ms and 905 ms vs C 1182 and 1182 ms (C++ 1182 and 1183 ms) for 500M calls of plusone() in libnewplus.so: about 1.3x faster, 1.78 vs 2.36 ns per call (derived from page data). Julia 0.6.3 ccall (894 and 889 ms) wins by the same margin. |
| **Workload** | Call the C function plusone(int) in a loop 500,000,000 times (while (x &lt; count) x = plusone(x)) and report elapsed milliseconds. |
| **Metric** | latency |
| **Hardware** | Intel i7-3630QM laptop (4 cores, HT), 16 GB RAM |
| **Compiler and flags** | C and C++: gcc/g++ 5.4.1 with -O2 -fPIC -Wall -Wextra (Tuprules.tup CFLAGS; C++ adds -std=c++14 -fno-rtti). The executables are linked at -O2 with -Lnewplus -lnewplus -Wl,-rpath,\$ORIGIN/newplus (Tupfile), so each call to plusone goes through the PLT; gcc 5.4 has no -fno-plt. libnewplus.so is built from newplus/plus.c with the same -O2 -fPIC. LuaJIT 2.0.4 runs hello.lua with default JIT settings, loads the same .so with ffi.load and calls newplus.plusone. Julia 0.6.3 uses ccall. Ubuntu 14.04; 2 samples per language (run-all.sh); timing by gettimeofday in milliseconds (newplus/plus.c current_timestamp). |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | no |
| **Adoption** | 698 stars |
| **Last commit** | 2023-07-12 |
| **Links** | [repository](https://github.com/dyu/ffi-overhead) · [benchmark](https://raw.githubusercontent.com/dyu/ffi-overhead/master/README.md) |

## Verdict

On an Intel i7-3630QM laptop with Ubuntu 14.04, 500M calls of plusone() in libnewplus.so took 891 and 905 ms from LuaJIT 2.0.4 against 1182 ms (twice) for C and 1182/1183 ms for C++ built with gcc/g++ 5.4.1 -O2 -fPIC and linked via -lnewplus, i.e. about 1.78 vs 2.36 ns per call (derived from page data); the author's earlier run in prev.md (2B calls, gcc 4.7.3, LuaJIT 2.0.2) showed the same ratio, 3612/3616 vs 4839/4822 ms. What is measured is the cost of a PLT-routed dynamic call versus a JIT-resolved direct call, not code quality.

## Use it when

- Lua scripting embedded in a C/C++ host where hot loops call many tiny C functions: compiled FFI calls cost about the same as, or less than, a dynamically linked C call (1.78 vs 2.36 ns per call on the i7-3630QM here).
- Replacing hand-written Lua C API bindings with ffi.cdef declarations; the FFI path avoids the stack-based Lua C API (the lua-resty-core sibling is the production example).
- As evidence when deciding whether PLT overhead matters for a C/C++ code base: if a 2018 JIT beats your C caller by 0.6 ns per call, static linking, a dlsym'd function pointer or -fno-plt is worth trying.

## Skip it when

- As a reason to call C from Lua instead of linking C to C: a statically linked or LTO build lets the compiler inline plusone entirely, and nobody measured that row (issue #15 asking for a direct-call C/C++ row has been open since 2019-12-16).
- Callees that do real work: the measured gap is about 0.6 ns per call and disappears against any non-trivial function body.
- C code that calls back into Lua: the LuaJIT docs call callback overhead 'absolutely detrimental' and forbid a JIT-compiled FFI call whose C callee re-enters Lua.
- Code paths LuaJIT does not compile (operations on the FFI docs' not-compiled list, or with the JIT turned off): those fall back to the interpreter, and this benchmark shows nothing about call overhead there.
- Anyone needing current numbers: the table uses LuaJIT 2.0.4, gcc 5.4.1 and Ubuntu 14.04, and issue #16 asking for a rerun is open.

## How it is fast

LuaJIT's trace compiler specializes on the identity of the C library namespace and the indexing string, so newplus.plusone becomes a constant address resolved once by dlsym; lj_emit_x86.h (emit_call_) then emits a direct rel32 call when the target is within 2 GB of the trace code, else mov rax, imm64; call rax. The C executable instead calls plusone@PLT, which jumps through the GOT on every call, and that extra indirect jump is the whole margin (the nullprogram.com write-up of this exact result, seen as a search snippet, attributes it to the PLT).

## Compared with alternatives

Against the Julia 0.6 ccall entry from the same table the margin is identical (891/905 vs 894/889 ms), so pick LuaJIT when you want a small embeddable scripting runtime inside a C/C++ host and Julia when the numeric code itself lives in Julia; lua-resty-core is the production example of the same FFI call path inside OpenResty.

## Integration

| | |
|---|---|
| **Form** | runtime: the luajit executable or the LuaJIT library embedded in a C/C++ host; the ffi module is built in |
| **Dependencies** | none beyond LuaJIT (ffi is part of LuaJIT); the benchmark itself needs tup and gcc to build libnewplus.so |
| **Minimum toolchain** | LuaJIT 2.0.4 as measured (an earlier run in prev.md used LuaJIT 2.0.2); LuaJIT 2.1 carries the same FFI |
| **Platforms** | x86-64 Linux measured; the advantage depends on ELF PLT linkage of the C baseline, other platforms not measured |
| **Thread safety** | not documented on the pages read |
| **Drop-in for the baseline** | no |

## Gotchas

- Correction to the record's caveat: in skeeto/dynamic-function-benchmark the 1.01 ns 'jit' row is machine code that benchmark.c hand-assembles into an mmap'd page (a patched call rel32), not compiler-generated C; plain C calling through a dlsym function pointer measured 1.26 ns ('ind') against 1.76 ns through the PLT (i7-6700, -O3 -fpie). So ordinary C recovers most but not all of the gap without a JIT, and a truly direct call needs static linking.
- Keep the namespace, not the function: per the LuaJIT FFI tutorial, caching local f = lib.plusone turns the call into an indirect call and 'generates bigger and slower machine code'; hello.lua uses newplus.plusone(x), which is the fast form.
- Small harness asymmetries: hello.lua makes warm-up calls (newplus.current_timestamp() and newplus.plusone(0)) before starting the clock, while hello.c starts timing cold, so its first plusone call pays lazy symbol binding inside the timed region; both sides use a millisecond gettimeofday clock and only 2 runs, and loop overhead is included in every row (issue #13).
- C++ exceptions do not cross a JIT-compiled FFI call (LuaJIT FFI semantics, 'Other missing features'), so wrapping C++ code for LuaJIT needs extern "C" shims that catch everything.

## Known shortcomings

- Win is the PLT: C calls plusone in libnewplus.so through the PLT while LuaJIT calls the dlsym address directly; skeeto/dynamic-function-benchmark shows plain C at JIT speed (1.01 vs 1.76 ns per call); C at -O2, 2018 toolchains, 2 samples.
- Correction to the record's caveat: in skeeto/dynamic-function-benchmark the 1.01 ns 'jit' row is machine code hand-assembled into an mmap'd page, not compiled C; plain C through a dlsym function pointer measured 1.26 ns and the PLT path 1.76 ns (i7-6700, -O3 -fpie). LuaJIT's lj_emit_x86.h emit_call_ issues a direct rel32 call (or mov rax; call rax) with no PLT, which is the mechanism. hello.lua makes warm-up calls before timing while hello.c starts cold with lazy binding inside the timed region, a small asymmetry on 500M calls.

## Caveats and trade-offs

Measures foreign-call overhead for a trivial function, not code quality. The C and C++ rows call through the PLT of a shared library; the LuaJIT FFI and Julia ccall paths call the resolved address directly. The independent skeeto/dynamic-function-benchmark (Unlicense; benchmark.c and Makefile with -O3 -fpie) shows plain C reaching the same direct-call speed (1.01 ns vs 1.76 ns through the PLT). The accompanying nullprogram.com article 'When FFI Function Calls Beat Native C' (2018-05-27) explains this exact ffi-overhead result by the PLT, but the blog was unreachable (search snippet only). Repo issue #15, open since 2019-12-16, asks for a direct-addressed (non-PLT) C/C++ row; it was never added. C is compiled at -O2, not -O3 (irrelevant to the call itself, since plusone sits in a separate shared object). The toolchains are from 2018 (luajit 2.0.4, julia 0.6.3, gcc 5.4.1 on Ubuntu 14.04). Only 2 samples per language are shown, timed with a millisecond gettimeofday clock. The loop is 'while (x &lt; count) x = plusone(x)'; issue #13 notes that loop overhead is part of every row. Many other languages in the table are slower than C (Go 37,975 ms, Node 9,163 ms, Java 4,469 ms). [retier] Enricher correction: in skeeto/dynamic-function-benchmark the 1.01 ns 'jit' row is machine code hand-assembled into an mmap'd page (a patched call rel32), not compiled C; plain C through a dlsym function pointer measured 1.26 ns and the PLT path 1.76 ns (i7-6700, -O3 -fpie), so ordinary C recovers most but not all of the gap without a JIT. LuaJIT's lj_emit_x86.h emit_call_ issues a direct rel32 call (or mov rax; call rax) with no PLT. hello.lua makes warm-up calls before timing while hello.c starts cold with lazy binding inside the timed region.

Gain only applies to call-boundary overhead for very small functions.

## Maintenance

Abandoned benchmark repo (last commit 2023-07-12, Apache-2.0, 698 stars) whose LuaJIT and C rows date from 2018 toolchains; LuaJIT itself remains usable, and the result is best read as a lesson about PLT overhead in dynamically linked C rather than as a reason to switch languages.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README's 500M-call table (luajit 891/905 ms, c 1182/1182, cpp 1182/1183) comes from public code (hello.c, hello.cpp, hello.lua, newplus/plus.c, Tupfile, Tuprules.tup with -O2 -fPIC), with gcc 5.4.1, luajit 2.0.4 and an i7-3630QM stated, so on paper the methodology reaches A. It is held at C because the C side is -O2 (wave 14 asks for -O3) and the win comes from call linkage, not the language: the C executable calls plusone through the PLT of libnewplus.so while LuaJIT calls the dlsym-resolved address, and an independent C benchmark (skeeto/dynamic-function-benchmark, -O3, i7-6700) shows C itself reaching direct-call speed (1.01 ns vs 1.76 ns through the PLT). This follows the sort-self precedent: A methodology, but the mechanism is not the language.
- **Verifier notes:** Confirm at C. The numbers, flags and metadata check out (Apache-2.0, 698 stars, 45 forks, last commit 2023-07-12, abandoned). Shortcomings to record: the win is the PLT trampoline of a dynamically linked C call, not language codegen, as an independent C benchmark (skeeto/dynamic-function-benchmark) shows; C at -O2 rather than -O3; issue #15 (direct-call C row) has been open since 2019; 2018 toolchains, 2 samples, millisecond timer. D is arguable under the AssemblyScript build-default precedent. It is held at C because PLT linkage is how C normally calls a shared library and the effect is real and reproduced independently.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-58 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/README.md>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/Tuprules.tup>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/Tupfile>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/hello.c>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/hello.cpp>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/hello.lua>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/run-all.sh>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/compile-all.sh>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/prev.md>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/newplus/plus.c>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/newplus/plus.h>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/newplus/Tupfile>
  - <https://github.com/dyu/ffi-overhead>
  - <https://github.com/dyu/ffi-overhead/commits/master>
  - <https://github.com/dyu/ffi-overhead/issues?q=is%3Aissue>
  - <https://github.com/dyu/ffi-overhead/issues/15>
  - <https://github.com/dyu/ffi-overhead/issues/13>
  - <https://github.com/skeeto/dynamic-function-benchmark>
  - <https://raw.githubusercontent.com/skeeto/dynamic-function-benchmark/master/Makefile>
  - <https://raw.githubusercontent.com/skeeto/dynamic-function-benchmark/master/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/README.md>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/Tuprules.tup>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/Tupfile>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/hello.c>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/hello.cpp>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/hello.lua>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/run-all.sh>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/compile-all.sh>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/prev.md>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/newplus/plus.c>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/newplus/plus.h>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/newplus/Tupfile>
  - <https://github.com/dyu/ffi-overhead>
  - <https://github.com/dyu/ffi-overhead/commits/master>
  - <https://github.com/dyu/ffi-overhead/issues?q=is%3Aissue>
  - <https://github.com/dyu/ffi-overhead/issues/13>
  - <https://github.com/dyu/ffi-overhead/issues/15>
  - <https://github.com/dyu/ffi-overhead/issues/16>
  - <https://raw.githubusercontent.com/skeeto/dynamic-function-benchmark/master/README.md>
  - <https://raw.githubusercontent.com/skeeto/dynamic-function-benchmark/master/Makefile>
  - <https://raw.githubusercontent.com/skeeto/dynamic-function-benchmark/master/benchmark.c>
  - <https://raw.githubusercontent.com/LuaJIT/LuaJIT/v2.0/src/lj_emit_x86.h>
  - <https://raw.githubusercontent.com/LuaJIT/LuaJIT/v2.1/doc/ext_ffi_semantics.html>
  - <https://raw.githubusercontent.com/LuaJIT/LuaJIT/v2.1/doc/ext_ffi_tutorial.html>
  - https://nullprogram.com/blog/2018/05/27/ (search snippet only)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:luajit/dyu/ffi-overhead#plusone-call`) · [data/wave14/enrich/raw/lang_luajit_dyu_ffi_overhead_plusone_call.json](../../../data/wave14/enrich/raw/lang_luajit_dyu_ffi_overhead_plusone_call.json) (enrichment confidence 0.5)

</details>
