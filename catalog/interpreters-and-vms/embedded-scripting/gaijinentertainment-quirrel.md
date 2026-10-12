# Quirrel (Gaijin Entertainment Squirrel fork)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Gaijin's stricter Squirrel fork: about 1.28x faster than Squirrel 3.2 on the same scripts, still slower than Lua 5.5.

| | |
|---|---|
| **Beats** | Squirrel 3.2 (original); also measured against Lua 5.5.1, LuaJIT 2.1 with -joff, Luau 0.735, QuickJS-ng 0.16.2 |
| **Claimed result** | doc/content/_bench.json (Quirrel-4.38.0 vs Squirrel-3.2, seconds): particles-kinematics 0.211 vs 0.36; primes-loop 0.099 vs 0.173; spectral-norm 0.475 vs 0.657; fibonacci-recursive 0.097 vs 0.133; fibonacci-loop 0.035 vs 0.048; n-bodies 0.867 vs 1.075; darg-ui-benchmark 0.351 vs 0.468; sort 0.085 vs 0.11; faster in 12 of 13 workloads (float2string 0.044 vs 0.0409999 is the exception), geomean about 1.28x over Squirrel 3.2 (derived from page data). Against Lua-5.5.1 Quirrel is slower: geomean about 0.87x, faster in only 3 of 13 (particles-kinematics 0.211 vs 0.381, fibonacci-loop 0.035 vs 0.037, float2string 0.044 vs 0.458); against LuaJIT -joff about 0.51x; against QuickJS-ng about 1.56x faster (derived from page data). README text: 'equal performance to Lua'. |
| **Workload** | Thirteen interpreter workloads (n-bodies, particles-kinematics, exp-loop, dictionary, darg-ui-benchmark, fibonacci recursive and loop, primes-loop, float2string, queen, sort, spectral-norm, string2float), best time per cell over 3 processes pinned to one core, seconds, lower is better. |
| **Metric** | throughput |
| **Hardware** | Windows 11 x64, Intel64 Family 6 Model 183 Stepping 1 (GenuineIntel; marketing name not stated), pinned to one P-core, run dated 2026-09-03 |
| **Compiler and flags** | Quirrel: release build of the Dagor tree interpreter, clang with mimalloc (jam -sConfig=rel); third-party interpreters built with clang-cl (LLVM 21.1.8) /O2 /MT, Lua with -DLUA_USE_JUMPTABLE=1; LuaJIT with cl via msvcbuild.bat static and run with -joff |
| **Adoption** | 223 stars; README says used in dozens of games and apps with hundreds of millions of installations (first-party statement) |
| **Last commit** | 2026-09-16 |
| **Links** | [repository](https://github.com/GaijinEntertainment/quirrel) · [benchmark](https://github.com/GaijinEntertainment/quirrel/blob/master/doc/content/_bench.json) |

## Verdict

The project's benchmarks.py runs the same .nut workloads on Quirrel 4.38.0 (Dagor release build, clang plus mimalloc, flags not published) and Squirrel 3.2 (clang-cl LLVM 21.1.8 /O2 /MT, CRT heap), with Lua 5.5.1, Luau 0.735, LuaJIT -joff and QuickJS-ng 0.16.2 on their own ports. It ran on Windows 11 with an Intel Family 6 Model 183 CPU (Raptor Lake generation) pinned to one P-core, taking the best of 3 processes, each reporting the best of 10-20 in-process reps. Quirrel is faster than Squirrel in 12 of 13 rows (geomean about 1.28x) and about 1.56x faster than QuickJS-ng, but slower than Lua (0.87x), Luau (0.54x) and LuaJIT -joff (0.51x), all derived from page data.

## Use it when

- You already embed Squirrel 3.x in a C++ engine and are willing to port scripts for about 1.28x geomean speed (faster in 12 of 13 of the project's workloads) plus compile-time error checking.
- Game UI and gameplay scripting on platforms that forbid runtime code generation (consoles, iOS), where an interpreter is required and the scripts are dominated by class-field access, which the inline caches speed up.
- Hosts that want deterministic reference-counted freeing, with the cycle collector run only when the host calls sq_collectgarbage, so there are no GC pauses the host did not ask for.
- Teams that want C/Java-like syntax with a built-in static analyzer (`sq -sa`, about a hundred checks) rather than Lua syntax.

## Skip it when

- If raw interpreter speed is the goal: the project's own tables have Quirrel at about 0.87x of Lua 5.5.1, 0.54x of Luau 0.735 and 0.51x of LuaJIT -joff (all derived from page data). Its paired VM acceptance harness has it slower than Lua 5.5 in 7 of 10 workloads (geomean about 0.75x) and slower than Luau in all 10 (about 0.46x).
- Running existing Squirrel scripts unchanged: `extends`, `#` comments, `delete`, `switch` (off by default), implicit `this` calls and several builtins are rejected or renamed.
- A standalone cmake build without a custom allocator: the default sqmem.cpp calls malloc, and the project's bench README says a CRT-heap build is up to 2x slower on table sweeps than the shipped mimalloc build.
- Code generators that emit large functions or deep expressions: the limits are 255 stack slots per function, a 500-unit parser depth budget ('AST too big', about 33 levels of parentheses) and 32768 static memos per function.
- Projects that need a JIT, a large third-party ecosystem, or an upstream other than one game studio's engine tree.

## How it is fast

The gain over Squirrel 3.2 comes from a reworked bytecode and compiler. There are fused compare-and-jump opcodes with integer, float or literal immediates (_OP_JCMPI/_OP_JCMPF/_OP_JCMPK), _OP_ADDI and combined load-move opcodes, plus per-instruction inline caches for class member get and set (_OP_GET_LITERAL/_OP_SET_LITERAL keep a 64-bit hint word holding a locked class's type id and the member index). It also has _OP_FASTCALL, which calls leaf native functions without frame setup, and _OP_LOAD_STATIC_MEMO for `static` expressions that are computed once. Dispatch is still a plain switch in sqvm.cpp, with no JIT and no computed goto. The benchmarked binary also swaps malloc for mimalloc through the SQ_EXCLUDE_DEFAULT_MEMFUNCTIONS hooks.

## Compared with alternatives

Pick it over Squirrel when you can port scripts and want the same embedding model about 1.28x faster with compile-time checks. Pick Luau (about 1.8x faster than Quirrel in Quirrel's own table) or Daslang (which Quirrel's performance page itself recommends when you need the fastest interpreter) when speed matters more than C-like syntax or an existing Squirrel/Sqrat codebase.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none for the core (sqstdlib, sqmodules and the Sqrat binding headers ship in the repo); mimalloc is optional, plugged in through SQ_EXCLUDE_DEFAULT_MEMFUNCTIONS |
| **Minimum toolchain** | C++17 (CMake 3.5+; GCC and Clang builds use -fno-rtti -fno-exceptions); the benchmarked binary is a Dagor jam build with clang |
| **Platforms** | Windows, macOS, Linux, Android, iOS and consoles per README; 64-bit SQInteger (_SQ64) by default |
| **Thread safety** | One VM per thread. Separate VMs from sq_open share nothing and can run on different threads; sq_newthread creates friend VMs that share the parent's globals. sqasync::post_from_any_thread is mutex-protected, and post_on_vm_thread is a data race if called off the VM's thread. |
| **Drop-in for the baseline** | partial: the Squirrel-lineage C API and Sqrat bindings carry over, but Squirrel scripts rarely compile unchanged, and some code compiles but behaves differently (filter callback argument order, file-scope functions and consts are now local) |

## Gotchas

- Harness flaw in the published table: the float2string and string2float rows run opposite operations across languages. Quirrel's and Squirrel's f2s.nut parses strings (num.tofloat()) and f2i.nut formats floats (tostring().len()), while the Lua, Luau, LuaJIT and QuickJS f2s files format floats and their f2i files parse strings. The 10.4x 'win' over Lua on float2string is parsing against formatting. Matched by operation, Quirrel beats Lua 3.4x on formatting (0.136 vs 0.458 s) and 2.4x on parsing (0.044 vs 0.105 s), and loses to Luau 0.31x on formatting. The geomean is unchanged and Quirrel vs Squirrel is unaffected (same file).
- The cross-language ports are not like-for-like either. particles.nut uses one flat table per particle {x,y,z,vx,vy,vz}, while the Lua, Luau and JS ports use nested pos/vel tables (about three times as many table lookups per update) and the Lua loop runs 101 sweeps instead of 100. Quirrel's lead on particles (0.211 vs Lua 0.381 s) and its near-tie with LuaJIT -joff rest on that layout; without that row, the geomean vs Lua falls from 0.87x to 0.82x (derived). The Lua sort row also times a pairs()-based table copy that Quirrel replaces with a native clone. The JS f2s/f2i files time one iteration with Date.now() instead of best-of-20.
- The shipped speed depends on the allocator. sqmem.cpp defaults to malloc and free, and the Squirrel 3.2 baseline ran on the CRT heap, so part of the 1.28x margin may be mimalloc rather than the VM. Define SQ_EXCLUDE_DEFAULT_MEMFUNCTIONS and supply sq_vm_malloc/realloc/free to match the benchmarked build.
- Silent semantic changes when porting from Squirrel: filter passes (value, index) instead of (index, value), and file-scope functions, classes, const and enum are local to the module rather than root-table slots. Open issue #107 ('Quirrel is slower than Lua in almost all cases', Dec 2025) had no maintainer reply when read.

## Known shortcomings

- Own _bench.json: geomean 1.28x over Squirrel 3.2 only; slower than Lua 5.5.1 (0.87x), LuaJIT -joff (0.51x) and Luau 0.735 (0.54x, omitted from the record). Allocator differs: Quirrel on mimalloc, Squirrel on the CRT heap. CPU given only as Family 6 Model 183 (Raptor Lake, no SKU); Quirrel build flags unstated. Bench code at DagorEngine .../quirrel/bench/benchmarks.py.
- Enricher: in the published table the float2string and string2float rows run opposite operations across languages (Quirrel's and Squirrel's f2s.nut parses while the Lua, Luau, LuaJIT and QuickJS f2s files format), so the 10.4x 'win' over Lua on float2string is parsing against formatting; matched by operation Quirrel beats Lua 3.4x on formatting and 2.4x on parsing and loses to Luau 0.31x. particles.nut uses one flat table per particle while the Lua, Luau and JS ports use nested pos/vel tables and the Lua loop runs 101 sweeps; without that row the geomean vs Lua falls from 0.87x to 0.82x (derived from page data). sqmem.cpp defaults to malloc while the benchmarked build used mimalloc. Silent semantic changes from Squirrel: filter passes (value, index), file-scope functions and classes are module-local.

## Caveats and trade-offs

First-party benchmark. The Quirrel binary is the shipped configuration with mimalloc, while the repo bench README says a CRT-heap build is up to 2x slower on table-sweep workloads (50k-table particles sweep 0.20s vs 0.11s), so part of the margin over the Squirrel 3.2 baseline (sq3-64.exe, upstream sources built with clang-cl /O2 /MT on the CRT heap) may be allocator rather than VM. Quirrel's own build is only described as 'jam -sConfig=rel' in prog/tools/sq (clang, mimalloc), with no compiler version or flags on the page. Quirrel loses to Lua 5.5.1 overall in its own table (geomean about 0.87x, faster in 3 of 13), to LuaJIT -joff (about 0.51x) and to Luau 0.735 (about 0.54x, faster only on particles-kinematics); against QuickJS-ng it wins about 1.56x over the 11 workloads QuickJS has rows for (queen and sort have none) but loses on 4 of them (all derived from page data). The daslang dasProfile README (borisbat/dasProfile, Quirrel 4.29.1 vs Lua 5.5.1, 16 interpreted tests) gives geomean 0.89x on Apple M1 Max and 0.94x on Ryzen 7 PRO 8700GE (derived from page data); that suite has no Squirrel column and comes from a Gaijin-affiliated project. The README claim 'equal performance to Lua' is therefore roughly true and the only clear win is over Squirrel 3.2 (about 1.28x geomean, faster in 12 of 13). CPU identified only as Intel Family 6 Model 183 Stepping 1 (Raptor Lake generation, SKU and clock not stated). Each cell is the fastest of 3 whole processes, each process reporting the best of 10-20 in-process iterations; the standalone repo is a batched mirror of the DagorEngine tree (latest batch v4.41.0 on 2026-09-16, the table labels Quirrel 4.38.0). [retier] Own _bench.json (Raptor Lake, no SKU, flags unstated): geomean 1.28x over Squirrel 3.2 only, with Quirrel on mimalloc and Squirrel on the CRT heap. Slower than Lua 5.5.1 (0.87x; 0.82x without the particles row whose Lua port uses nested tables and 101 sweeps), LuaJIT -joff (0.51x) and Luau (0.54x). The float2string and string2float rows run opposite operations across languages (Quirrel's f2s parses while the Lua, Luau and QuickJS f2s format), so the 10.4x float2string 'win' over Lua is parsing against formatting.

Stricter and safer than Squirrel by design (README), so not guaranteed to be a drop-in replacement for Squirrel scripts; C/Java-like syntax with Lua-like dynamism; no JIT by design (targets consoles and phones). Standalone repo is synced in batches from the Dagor engine tree.

## Maintenance

Actively maintained in the DagorEngine tree and mirrored in batches (last batch 2026-09-16, v4.41.0), MIT-licensed and copyable, but the speed claim holds only against Squirrel 3.2. The published cross-language table has a swapped float2string/string2float pair and an asymmetric particles port.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party _bench.json from public harness code (DagorEngine prog/1stPartyLibs/quirrel/quirrel/bench/benchmarks.py plus the .nut workloads) with Squirrel 3.2 in every row; baselines' compiler and flags are stated (clang-cl LLVM 21.1.8 /O2 /MT) but the CPU is given only as CPUID 'Intel64 Family 6 Model 183 Stepping 1' (Raptor Lake generation, no SKU or clock) and Quirrel's own build is described only as 'jam -sConfig=rel' (clang, mimalloc) with no compiler version or flags, so it stops one step short of A.
- **Verifier notes:** All Squirrel 3.2, Lua 5.5.1, LuaJIT, QuickJS-ng numbers and the derived geomeans (1.283x vs Squirrel, 0.867x vs Lua, 0.513x vs LuaJIT -joff, 1.56x vs QuickJS-ng) check out against _bench.json; the record also omits Luau 0.735, which beats Quirrel at about 0.54x. Shortcoming: wins only against its own ancestor Squirrel 3.2 (about 1.28x geomean), slower than Lua 5.5.1, Luau and LuaJIT -joff, and the margin over Squirrel mixes in mimalloc vs the CRT heap. License MIT, 223 stars, last commit 2026-09-16 confirmed; dasProfile geomeans 0.892x/0.943x recomputed and match.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** same-allocator comparison with stated flags; like-for-like ports with the same allocator
- **Pages the verifier opened:**
  - <https://github.com/GaijinEntertainment/quirrel/blob/master/doc/content/_bench.json>
  - <https://raw.githubusercontent.com/GaijinEntertainment/quirrel/HEAD/doc/content/_bench.json>
  - <https://raw.githubusercontent.com/GaijinEntertainment/quirrel/HEAD/README.md>
  - <https://github.com/GaijinEntertainment/quirrel>
  - <https://github.com/GaijinEntertainment/quirrel/commits/master>
  - <https://github.com/GaijinEntertainment/DagorEngine/tree/main/prog/1stPartyLibs/quirrel/quirrel/bench>
  - <https://raw.githubusercontent.com/GaijinEntertainment/DagorEngine/main/prog/1stPartyLibs/quirrel/quirrel/bench/README.md>
  - <https://raw.githubusercontent.com/borisbat/dasProfile/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/GaijinEntertainment/quirrel>
  - <https://raw.githubusercontent.com/GaijinEntertainment/quirrel/HEAD/README.md>
  - <https://raw.githubusercontent.com/GaijinEntertainment/quirrel/HEAD/doc/content/_bench.json>
  - <https://raw.githubusercontent.com/GaijinEntertainment/quirrel/HEAD/doc/content/_vm_bench.json>
  - <https://github.com/GaijinEntertainment/quirrel/tree/master/doc/content>
  - <https://github.com/GaijinEntertainment/quirrel/tree/master/doc/content/pages>
  - <https://raw.githubusercontent.com/GaijinEntertainment/quirrel/HEAD/doc/content/pages/performance.md>
  - <https://raw.githubusercontent.com/GaijinEntertainment/quirrel/HEAD/doc/content/pages/limits.md>
  - <https://github.com/GaijinEntertainment/quirrel/tree/master/doc/content/pages/coming-from>
  - <https://raw.githubusercontent.com/GaijinEntertainment/quirrel/HEAD/doc/content/pages/coming-from/squirrel.md>
  - <https://github.com/GaijinEntertainment/quirrel/tree/master/doc/content/pages/embedding>
  - <https://raw.githubusercontent.com/GaijinEntertainment/quirrel/HEAD/doc/content/pages/embedding/index.md>
  - <https://raw.githubusercontent.com/GaijinEntertainment/quirrel/HEAD/doc/content/pages/embedding/async.md>
  - <https://raw.githubusercontent.com/GaijinEntertainment/quirrel/HEAD/doc/content/pages/embedding/running.md>
  - <https://github.com/GaijinEntertainment/quirrel/tree/master/squirrel>
  - <https://raw.githubusercontent.com/GaijinEntertainment/quirrel/HEAD/squirrel/opcodes.h>
  - <https://raw.githubusercontent.com/GaijinEntertainment/quirrel/HEAD/squirrel/sqvm.cpp>
  - <https://raw.githubusercontent.com/GaijinEntertainment/quirrel/HEAD/squirrel/sqmem.cpp>
  - <https://raw.githubusercontent.com/GaijinEntertainment/quirrel/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/GaijinEntertainment/quirrel/HEAD/squirrel/CMakeLists.txt>
  - <https://github.com/GaijinEntertainment/quirrel/issues?q=is%3Aissue>
  - <https://github.com/GaijinEntertainment/quirrel/issues/107>
  - <https://raw.githubusercontent.com/GaijinEntertainment/DagorEngine/main/prog/1stPartyLibs/quirrel/quirrel/bench/README.md>
  - <https://raw.githubusercontent.com/GaijinEntertainment/DagorEngine/main/prog/1stPartyLibs/quirrel/quirrel/bench/benchmarks.py>
  - <https://raw.githubusercontent.com/GaijinEntertainment/DagorEngine/main/prog/1stPartyLibs/quirrel/quirrel/bench/quirrel/f2s.nut>
  - <https://raw.githubusercontent.com/GaijinEntertainment/DagorEngine/main/prog/1stPartyLibs/quirrel/quirrel/bench/quirrel/f2i.nut>
  - <https://raw.githubusercontent.com/GaijinEntertainment/DagorEngine/main/prog/1stPartyLibs/quirrel/quirrel/bench/lua/f2s.lua>
  - <https://raw.githubusercontent.com/GaijinEntertainment/DagorEngine/main/prog/1stPartyLibs/quirrel/quirrel/bench/lua/f2i.lua>
  - <https://raw.githubusercontent.com/GaijinEntertainment/DagorEngine/main/prog/1stPartyLibs/quirrel/quirrel/bench/luau/f2s.luau>
  - <https://raw.githubusercontent.com/GaijinEntertainment/DagorEngine/main/prog/1stPartyLibs/quirrel/quirrel/bench/luau/f2i.luau>
  - <https://raw.githubusercontent.com/GaijinEntertainment/DagorEngine/main/prog/1stPartyLibs/quirrel/quirrel/bench/js/f2s.js>
  - <https://raw.githubusercontent.com/GaijinEntertainment/DagorEngine/main/prog/1stPartyLibs/quirrel/quirrel/bench/js/f2i.js>
  - <https://raw.githubusercontent.com/GaijinEntertainment/DagorEngine/main/prog/1stPartyLibs/quirrel/quirrel/bench/quirrel/particles.nut>
  - <https://raw.githubusercontent.com/GaijinEntertainment/DagorEngine/main/prog/1stPartyLibs/quirrel/quirrel/bench/lua/particles.lua>
  - <https://raw.githubusercontent.com/GaijinEntertainment/DagorEngine/main/prog/1stPartyLibs/quirrel/quirrel/bench/luau/particles.luau>
  - <https://raw.githubusercontent.com/GaijinEntertainment/DagorEngine/main/prog/1stPartyLibs/quirrel/quirrel/bench/js/particles.js>
  - <https://raw.githubusercontent.com/GaijinEntertainment/DagorEngine/main/prog/1stPartyLibs/quirrel/quirrel/bench/quirrel/primes.nut>
  - <https://raw.githubusercontent.com/GaijinEntertainment/DagorEngine/main/prog/1stPartyLibs/quirrel/quirrel/bench/lua/primes.lua>
  - <https://raw.githubusercontent.com/GaijinEntertainment/DagorEngine/main/prog/1stPartyLibs/quirrel/quirrel/bench/quirrel/queen.nut>
  - <https://raw.githubusercontent.com/GaijinEntertainment/DagorEngine/main/prog/1stPartyLibs/quirrel/quirrel/bench/lua/queen.lua>
  - <https://raw.githubusercontent.com/GaijinEntertainment/DagorEngine/main/prog/1stPartyLibs/quirrel/quirrel/bench/quirrel/profile.nut>
  - <https://raw.githubusercontent.com/GaijinEntertainment/DagorEngine/main/prog/1stPartyLibs/quirrel/quirrel/bench/lua/profile.lua>
  - <https://raw.githubusercontent.com/GaijinEntertainment/DagorEngine/main/prog/1stPartyLibs/quirrel/quirrel/bench/quirrel/fib_loop.nut>
  - <https://raw.githubusercontent.com/GaijinEntertainment/DagorEngine/main/prog/1stPartyLibs/quirrel/quirrel/bench/lua/fib_loop.lua>
  - <https://raw.githubusercontent.com/GaijinEntertainment/DagorEngine/main/prog/1stPartyLibs/quirrel/quirrel/bench/quirrel/fib_recursive.nut>
  - <https://raw.githubusercontent.com/GaijinEntertainment/DagorEngine/main/prog/1stPartyLibs/quirrel/quirrel/bench/lua/fib_recursive.lua>
  - <https://raw.githubusercontent.com/GaijinEntertainment/DagorEngine/main/prog/1stPartyLibs/quirrel/quirrel/bench/quirrel/dict.nut>
  - <https://raw.githubusercontent.com/GaijinEntertainment/DagorEngine/main/prog/1stPartyLibs/quirrel/quirrel/bench/lua/dict.lua>
  - <https://raw.githubusercontent.com/GaijinEntertainment/DagorEngine/main/prog/1stPartyLibs/quirrel/quirrel/bench/quirrel/exp.nut>
  - <https://raw.githubusercontent.com/GaijinEntertainment/DagorEngine/main/prog/1stPartyLibs/quirrel/quirrel/bench/lua/exp.lua>
  - <https://raw.githubusercontent.com/GaijinEntertainment/DagorEngine/main/prog/1stPartyLibs/quirrel/quirrel/bench/quirrel/table-sort.nut>
  - <https://raw.githubusercontent.com/GaijinEntertainment/DagorEngine/main/prog/1stPartyLibs/quirrel/quirrel/bench/lua/table-sort.lua>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/gaijinentertainment/quirrel`) · [data/wave12/enrich/raw/github_com_gaijinentertainment_quirrel.json](../../../data/wave12/enrich/raw/github_com_gaijinentertainment_quirrel.json) (enrichment confidence 0.75)

</details>
