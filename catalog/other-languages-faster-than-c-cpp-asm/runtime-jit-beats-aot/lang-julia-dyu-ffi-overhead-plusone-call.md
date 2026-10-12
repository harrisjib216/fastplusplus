# Julia 0.6 ccall: dyu/ffi-overhead plusone() call loop

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Julia` · `Apache-2.0` · 🔴 abandoned

> Julia 0.6.3 ccall loop calling a trivial C function 1.3x faster than C's own PLT-routed call (2018 microbenchmark).

| | |
|---|---|
| **Beats** | C and C++ (gcc 5.4.1 -O2) calling plusone() in the shared library libnewplus.so through the dynamic linker |
| **Claimed result** | Julia 894 ms and 889 ms vs C 1182 ms and 1182 ms (C++ 1182 and 1183 ms) for 500M calls of plusone(): about 1.3x faster (derived from page data). The C and C++ rows date from the Feb 2017 run; the Julia row was added alone in May 2018 (commit c8010d5) without re-running C, so this is a cross-run comparison. |
| **Workload** | Call the C function plusone(int) in a loop 500,000,000 times (while (x &lt; count) x = plusone(x)) and report elapsed milliseconds. |
| **Metric** | latency |
| **Hardware** | Intel i7-3630QM laptop (4 cores, HT), 16 GB RAM |
| **Compiler and flags** | C and C++: gcc/g++ 5.4.1 -O2 -fPIC -Wall -Wextra (Tuprules.tup; C++ adds -std=c++14 -fno-rtti); executables linked with -O2 against newplus/libnewplus.so (plus.c built -O2 -fPIC, -shared) via rpath, so plusone is reached through the PLT. Julia 0.6.3 run as 'julia hello.jl 500000000' with default options; ccall((:plusone, "./newplus/libnewplus.so"), ...). Ubuntu 14.04 x64; 2 samples per language; timer is gettimeofday in milliseconds (C) and time() (Julia). |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | no |
| **Adoption** | 698 stars |
| **Last commit** | 2023-07-12 |
| **Links** | [repository](https://github.com/dyu/ffi-overhead) · [benchmark](https://raw.githubusercontent.com/dyu/ffi-overhead/master/README.md) |

## Verdict

On an Intel i7-3630QM laptop under Ubuntu 14.04, 500 million calls of plusone() in a gcc -O2 -fPIC shared library took 894 and 889 ms from Julia 0.6.3 (2018 run) versus 1182 and 1182 ms from C and 1182/1183 ms from C++ built with gcc/g++ 5.4.1 -O2 (2017 run), about 1.3x faster (derived from page data). The difference is PLT indirection in the C executables versus a JIT-embedded function address in Julia.

## Use it when

- As evidence that Julia's ccall into a C shared library adds essentially no overhead for scalar-argument functions, so wrapping a C library from Julia does not cost per-call time compared with C calling the same .so.
- When deciding whether a hot loop of many tiny foreign calls belongs in Julia or C: on Julia 0.6-1.10 JIT-compiled code, a constant-library ccall is a direct pointer call, cheaper than C's default lazily bound PLT call.
- As a reproducible harness (Tupfile, hello.\*, run-all.sh) to measure call-boundary cost across about 20 languages on your own machine and toolchains.

## Skip it when

- As proof that Julia beats C in general: C calling plusone directly (static link, -fno-plt, LTO, or inlining) would remove the PLT hop, and issue #15 (open since 2019-12-16) asking for exactly that non-PLT C/C++ measurement was never answered.
- On Julia 1.11 or later: current codegen no longer embeds the literal address in JIT mode; every non-vararg ccall with a constant library goes through emit_plt (a load from a per-symbol jlplt GOT slot, then an indirect call), which is structurally the same indirection as C's -fno-plt call, so the 2018 gap should not be assumed (not re-measured).
- For functions that do real work: at 500M calls the whole difference is about 0.6 ns per call, which vanishes once the callee does more than a few instructions.
- For calls that pass arrays, strings, structs or callbacks: only a single Cint argument and Int32 return were measured; marshalling costs are not covered.
- As current data: toolchains are gcc 5.4.1, Julia 0.6.3 and LuaJIT 2.0.4 on a 2012 laptop CPU, with 2 samples per language; the repo's last commit is 2023-07-12.

## How it is fast

In Julia 0.6.3's codegen (src/ccall.cpp), a ccall whose library and symbol are constants is resolved with jl_dlsym_e at JIT time and the address is embedded as a literal pointer ('just JIT the function address'), so each iteration is one call through a constant pointer into plusone. The C and C++ executables are compiled with -fPIC and linked against libnewplus.so, so every call goes to the plusone@PLT stub and then jumps through the GOT: one extra branch per iteration on a loop whose body is only 'add 1 and return'. Both sides execute the same -O2 plusone machine code; the gap (1.78 vs 2.36 ns per call) is call-linkage overhead, not better code generation (mechanism from reading Tuprules.tup and Julia's ccall.cpp; the README states none).

## Compared with alternatives

The LuaJIT 2.0 FFI row in the same table shows the identical 1.3x gap (891/905 ms) for the same reason and was measured in the same 2017 run as C, so it is the cleaner citation; pick the Julia row only when the question is specifically Julia's ccall cost. Unlike the kostya and LangArena siblings, which compare whole algorithms, this measures only call linkage.

## Integration

| | |
|---|---|
| **Form** | source-drop (benchmark scripts; hello.jl is 25 lines) |
| **Dependencies** | Julia; the repo's newplus/libnewplus.so built with tup (gcc -O2 -fPIC -shared) |
| **Minimum toolchain** | Julia 0.6.3 as measured (ccall tuple syntax still works in Julia 1.x); gcc 5.4.1 and tup 0.7.4 for the C side |
| **Platforms** | Linux x86-64 as measured (Ubuntu 14.04, i7-3630QM); hello.jl hard-codes the relative path ./newplus/libnewplus.so |
| **Thread safety** | not applicable (single-threaded loop) |
| **Drop-in for the baseline** | no |

## Gotchas

- Cross-run comparison: the C and C++ rows (1182/1182, 1182/1183 ms) are unchanged since the Feb 2017 README (commit 9f0c4d0), and the Julia row (894/889 ms) was added in May 2018 (commit c8010d5) without re-running C. The gap is still consistent with history: the 2013 run in prev.md (gcc 4.7.3, LuaJIT 2.0.2, 2 billion calls) already had LuaJIT at 3612 ms vs C 4839 ms, the same 1.34x ratio, and the 2018 Julia figure matches the 2017 LuaJIT figure (1.78 ns per call).
- The C side is handicapped by its build, not by the language: Tuprules.tup puts -fPIC in CFLAGS for the executables too and links them against the shared library via rpath with default lazy binding, so the baseline is a PLT call; the Julia side gets a JIT-resolved constant pointer (Julia 0.6.3 ccall.cpp, non-imaging branch).
- Version-specific mechanism: the literal-address path exists in Julia v0.6.3 through v1.10.0 ccall.cpp and is gone in v1.11.0 and current master, where use_jlplt defaults to 1 (src/init.c) and calls load the target from a jlplt GOT global; code compiled in imaging mode (system images) used the jlplt thunk in every version.
- Timing differs slightly: C reads gettimeofday in whole milliseconds via current_timestamp() in the library, Julia uses time() as Float64 seconds; both exclude process start-up, and Julia's JIT compilation of run() happens before the timer starts.

## Known shortcomings

- Cross-run comparison: the C row (1182) comes from a February 2017 run (9f0c4d0) and the Julia row (894/889) was added alone in May 2018 (c8010d5) with C never re-run. Otherwise public code, gcc 5.4.1 -O2 -fPIC, i7-3630QM; the gap is a linkage artifact (C calls through the PLT of a -fPIC shared object, Julia ccall uses a JIT-resolved pointer), not codegen.
- The gap is call linkage, not code quality: the C executables are built with -fPIC and call libnewplus.so through the PLT, while Julia 0.6.3's ccall embedded a JIT-resolved literal address. That literal-address path exists from v0.6.3 to v1.10.0 and is gone from v1.11.0 on (use_jlplt=1 in src/init.c routes calls through a jlplt GOT slot), so the 2018 win is version-specific; issue #15 asking for a non-PLT C baseline has been unanswered since 2019. The ratio is structurally plausible despite the cross-run (the 2013 prev.md run had LuaJIT 3612 ms vs C 4839 ms, the same 1.34x).

## Caveats and trade-offs

Cross-run comparison: the C and C++ numbers (1182/1182, 1182/1183) are from the Feb 2017 results and were never re-measured when the Julia row (894/889, Julia 0.6.3) was added in May 2018 (commit c8010d5); the LuaJIT row (891/905) that shows the same gap was measured in the 2017 run. Measures foreign-call overhead for a trivial function, not code quality: the C and C++ executables call plusone through the PLT stub of a -fPIC shared library, while Julia's ccall with a constant (symbol, library) pair calls a pointer resolved at JIT time; -fno-plt, static linking or LTO would shrink or remove the gap (verifier inference from Tupfile/Tuprules.tup and hello.jl; the README states no mechanism). Both sides run the same -O2 plusone machine code in libnewplus.so. C is compiled -O2, not -O3. Toolchains are from 2017-2018 (gcc 5.4.1, julia 0.6.3, luajit 2.0.4) and only 2 samples are shown. Most other languages in the table are slower than C (Go 37,975 ms, Node 9,163 ms, Java 4,469 ms). The only rows faster than C in the table are LuaJIT and Julia. [retier] Enricher: the gap is call linkage, not code quality; the C executables are built with -fPIC and call libnewplus.so through the PLT, while Julia 0.6.3's ccall embedded a JIT-resolved literal address. That literal-address path exists from v0.6.3 to v1.10.0 and is gone from v1.11.0 on (use_jlplt=1 in src/init.c routes calls through a jlplt GOT slot), so the 2018 win is version-specific. Issue #15 asking for a non-PLT C baseline has been unanswered since 2019. The ratio is structurally plausible despite the cross-run: the 2013 prev.md run had LuaJIT 3612 ms vs C 4839 ms, the same 1.34x.

Gain only applies to call-boundary overhead for very small functions.

## Maintenance

Abandoned benchmark repo (last commit 2023-07-12, Apache-2.0, 698 stars) whose Julia number reflects a ccall code path that Julia removed in 1.11; usable only as a harness to re-measure call overhead, not as current evidence.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now D.
- **Tier reason:** Code (hello.c, hello.cpp, hello.jl, Tuprules.tup), compiler (gcc 5.4.1 -O2 -fPIC) and CPU (i7-3630QM) are all public, which would otherwise meet A, but the Julia and C rows were measured in different runs about 15 months apart: C 1182/1182 is unchanged since the Feb 2017 README (commit 9f0c4d0) and Julia 894/889 was appended in May 2018 (commit c8010d5, '+6 lines, 0 removed') without re-running C, so under the cross-run precedent (PostgreSQL, MySQL, ODB) the comparison goes to D.
- **Verifier notes:** README numbers match, but git history shows the C row (Feb 2017) and the Julia row (May 2018, commit c8010d5) come from separate runs; downgraded C to D under the cross-run precedent (if the orchestrator accepts same-author same-laptop runs, the code/compiler/flags/CPU would meet A). Shortcomings: cross-run comparison, PLT-vs-JIT-resolved call is a linkage artifact rather than a language win, C at -O2 not -O3, 2 samples, 2018 toolchains, repo abandoned since 2023-07-12.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-57 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/README.md>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/Tupfile>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/Tuprules.tup>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/hello.c>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/hello.cpp>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/hello.jl>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/hello.lua>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/compile-all.sh>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/run-all.sh>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/prev.md>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/newplus/plus.c>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/newplus/plus.h>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/newplus/Tupfile>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/c8010d585d9b16fe49d216abf546bad4a9a4858a/README.md>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/9f0c4d0367519bfa7dcac6bf18e1958fbb0a6c3b/README.md>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/a99c92dbb9deb0d361fa2cfa581ad6152513449e/README.md>
  - <https://github.com/dyu/ffi-overhead>
  - <https://github.com/dyu/ffi-overhead/commits/master>
  - <https://github.com/dyu/ffi-overhead/commits/master/hello.jl>
  - <https://github.com/dyu/ffi-overhead/commits/master/README.md>
  - <https://github.com/dyu/ffi-overhead/commit/c8010d585d9b16fe49d216abf546bad4a9a4858a>
- **Sources the enricher read:**
  - <https://github.com/dyu/ffi-overhead>
  - <https://github.com/dyu/ffi-overhead/commits/master>
  - <https://github.com/dyu/ffi-overhead/issues?q=is%3Aissue>
  - <https://github.com/dyu/ffi-overhead/issues/13>
  - <https://github.com/dyu/ffi-overhead/issues/15>
  - <https://github.com/dyu/ffi-overhead/issues/16>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/README.md>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/Tupfile>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/Tuprules.tup>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/hello.c>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/hello.cpp>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/hello.jl>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/hello.lua>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/compile-all.sh>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/run-all.sh>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/prev.md>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/newplus/plus.c>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/newplus/plus.h>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/newplus/Tupfile>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/master/LICENSE>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/9f0c4d0367519bfa7dcac6bf18e1958fbb0a6c3b/README.md>
  - <https://raw.githubusercontent.com/dyu/ffi-overhead/c8010d585d9b16fe49d216abf546bad4a9a4858a/README.md>
  - <https://raw.githubusercontent.com/JuliaLang/julia/v0.6.3/src/ccall.cpp>
  - <https://raw.githubusercontent.com/JuliaLang/julia/v1.0.0/src/ccall.cpp>
  - <https://raw.githubusercontent.com/JuliaLang/julia/v1.6.0/src/ccall.cpp>
  - <https://raw.githubusercontent.com/JuliaLang/julia/v1.8.0/src/ccall.cpp>
  - <https://raw.githubusercontent.com/JuliaLang/julia/v1.9.0/src/ccall.cpp>
  - <https://raw.githubusercontent.com/JuliaLang/julia/v1.10.0/src/ccall.cpp>
  - <https://raw.githubusercontent.com/JuliaLang/julia/v1.11.0/src/ccall.cpp>
  - <https://raw.githubusercontent.com/JuliaLang/julia/v1.12.0/src/ccall.cpp>
  - <https://raw.githubusercontent.com/JuliaLang/julia/master/src/ccall.cpp>
  - <https://raw.githubusercontent.com/JuliaLang/julia/master/src/codegen.cpp>
  - <https://raw.githubusercontent.com/JuliaLang/julia/master/src/init.c>
  - <https://raw.githubusercontent.com/JuliaLang/julia/master/src/julia.h>
  - <https://raw.githubusercontent.com/JuliaLang/julia/master/src/aotcompile.cpp>
  - <https://raw.githubusercontent.com/JuliaLang/julia/master/src/jitlayers.cpp>
  - <https://raw.githubusercontent.com/JuliaLang/julia/master/src/gf.c>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:julia/dyu/ffi-overhead#plusone-call`) · [data/wave14/enrich/raw/lang_julia_dyu_ffi_overhead_plusone_call.json](../../../data/wave14/enrich/raw/lang_julia_dyu_ffi_overhead_plusone_call.json) (enrichment confidence 0.75)

</details>
