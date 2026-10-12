# LuaBridge3

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> C++17 Lua binding (LuaBridge fork) with per-call overhead near sol2's; faster on Lua-to-C++ calls, slower on C++-side table access.

| | |
|---|---|
| **Beats** | Sol3 (sol2) and vanilla LuaBridge (C++ Lua binding overhead over the plain Lua C API) |
| **Claimed result** | README chart Images/benchmarks.png (ns per operation, lower is better, 34 cases): against Sol3, LuaBridge3 is faster on 20 of 30 shared cases (member function call 152.4 vs 356.9, derived method call 91.8 vs 260.5, c function 44.2 vs 116.2, static member function call 88.4 vs 212.1, shared ptr pass 61.7 vs 123.2, userdata property getter 86.4 vs 165.5, userdata variable write 79.7 vs 161.2), slower on 9 (table get 29.1 vs 17.9, table chained get 69.6 vs 28.0, table chained set 56.5 vs 26.8, table global string get 39.7 vs 11.9, table set 18.3 vs 17.2, multi return 49.7 vs 44.8, stateful function object 40.0 vs 37.4, c function through lua in c 40.4 vs 34.3, lua function in c 26.8 vs 25.7) and tied on optional failure (14.3). Against vanilla LuaBridge it is faster on 12 of 22 shared cases (table get 29.1 vs 57.1, optional success 26.8 vs 110.0, table chained get 69.6 vs 156.7) and slower on 10 (c function 44.2 vs 34.3, member function call 152.4 vs 148.7, static member function call 88.4 vs 60.9, lambda capture 45.1 vs 32.8, multi return lua 48.3 vs 33.0, return userdata 167.2 vs 142.0). The headline userdata variable access rows (70.2 vs Sol3 299.9 and vanilla 269.3) are not like-for-like: LuaBridge3's script does one read, the other two do two reads and a write. Win/loss counts derived from page data. |
| **Workload** | Per-operation binding overhead in nanoseconds across 34 cases (global and table get/set, chained table access, free, member, static and derived method calls, userdata properties, shared-pointer ownership, multi-return, lambda captures, optionals, converters), Google Benchmark, all three libraries on embedded Lua 5.4.8, each case in isolation. |
| **Metric** | latency |
| **Compiler and flags** | CMake Release build (Benchmarks/README.md), Google Benchmark v1.8.4, Lua 5.4.8 sources compiled into each executable; Sol3 built with SOL_ALL_SAFETIES_ON=1 and SOL_NO_EXCEPTIONS=1. No LTO flag is set in the CMake files despite the README's link-time-optimization wording; compiler and compiler version not stated. |
| **Adoption** | 423 stars |
| **Last commit** | 2026-09-11 |
| **Links** | [repository](https://github.com/kunitoki/LuaBridge3) · [benchmark](https://raw.githubusercontent.com/kunitoki/LuaBridge3/HEAD/README.md) |

## Verdict

First-party Google Benchmark v1.8.4 suite (Release build, Lua 5.4.8 compiled in, compiler and CPU not stated) measuring ns per binding operation: LuaBridge3 beats Sol3 on 20 of 30 shared cases, mainly Lua-to-C++ calls such as member call 152.4 vs 356.9 ns, but loses on C++-side table access (table chained get 69.6 vs 28.0 ns). It beats vanilla LuaBridge on 12 of 22 shared cases. The largest wins rest on a mismatched script and a Sol3-only per-call proxy overhead. The README itself only claims it 'competes directly with sol2'.

## Use it when

- Game or app scripting where Lua calls into C++ a lot (member, static, derived-method and shared_ptr calls): the chart puts it at 0.35x to 0.7x of Sol3's time on these script-driven cases, though part of that gap is harness overhead on the Sol3 side
- Projects that must support several Lua VMs from one binding layer: PUC Lua 5.1 to 5.5, LuaJIT 2.1, Luau and Ravi are all in CI
- Builds with -fno-exceptions or /EHsc-: the library works with and without exceptions (Noexcept test targets for every PUC Lua and LuaJIT)
- Existing vanilla LuaBridge users who want lambdas with captures, overloads, multiple inheritance, shared_ptr ownership and std containers without switching to a different binding style

## Skip it when

- C++-side table access in hot loops (LuaRef get/set, chained table access, global reads): Sol3 is 1.6x to 3.3x faster on table get, chained get/set and global string get in the project's own chart
- Deep multiple-inheritance hierarchies on hot paths: calling two base-class methods through deriveClass&lt;D, A, B&gt; cost 538.9 ns per iteration, against 91.8 ns for a method on the derived class itself
- Pure call-path latency versus vanilla LuaBridge: the old library is faster on 10 of 22 shared cases (c function 34.3 vs 44.2 ns, static member call 60.9 vs 88.4 ns, lambda capture 32.8 vs 45.1 ns, multi return lua 33.0 vs 48.3 ns)
- If you need a drop-in replacement for sol2 code: the API, ownership model and error handling differ

## How it is fast

For non-extensible classes without registered bases, __index and __newindex are C closures that carry the class's property-getter (propget), setter and method tables as upvalues (index_metamethod_simple in detail/CFunctions.h), so a property read is one raw string-keyed lua_rawget plus a getter call, with no metatable or registry walk; the propget table is checked first because it is the usual hit for instance reads. Internal tables are keyed by process-unique lightuserdata pointers via lua_rawgetp, not by string names. Classes registered with deriveClass or with __index/__newindex fallbacks use the general index_metamethod, which walks the parent list on misses.

## Compared with alternatives

Pick it over sol2 when you need one binding layer across PUC Lua, LuaJIT, Luau and Ravi, an exception-free build, or mostly Lua-to-C++ call traffic. Keep sol2 when C++ code reads and writes Lua tables in hot loops, where Sol3 is 1.6x to 3.3x faster in this same chart. nanobind is the analogous choice for Python, not Lua.

## Integration

| | |
|---|---|
| **Form** | header-only (also a single-header amalgamation in Distribution/LuaBridge; vcpkg port luabridge3) |
| **Dependencies** | none beyond the Lua headers and library of your chosen VM |
| **Minimum toolchain** | C++17 (optional headers need C++20 for std::span, coroutines and ranges, and C++23 for std::expected and flat_map/flat_set); unit tests default to C++20 with CMake 3.10+ |
| **Platforms** | any platform where the chosen Lua VM builds; CI covers Linux, macOS and Windows, plus ASAN and UBSAN builds |
| **Thread safety** | not documented; a lua_State is not thread-safe, and registerMainThread exists for Lua 5.1 thread bookkeeping |
| **Drop-in for the baseline** | no |

## Gotchas

- Benchmark harness flaw: userdata variable access, access large and access last time 'return b.var' (one read) for LuaBridge3 but 'b.var = b.var + 1.0 return b.var' (two reads and a write) for Sol3 and vanilla LuaBridge, so the biggest chart wins (70.2 vs 299.9 and 269.3 ns, 77.0 vs 285.7 ns, 73.4 vs 274.9 ns) are not like-for-like.
- Benchmark harness flaw: LuaBridge3 and vanilla script cases call lua_getglobal plus a raw lua_pcall, while every Sol3 script case goes through lua["name"]() each iteration (a proxy lookup plus a protected call under SOL_ALL_SAFETIES_ON). Sol3's own rows show about 80 ns of that overhead (c function 116.2 ns against 34.3 ns for the same C function called through a cached sol::function; derived from page data). Derived-class Sol3 cases also bind a raw C++ pointer (lua["obj"] = &ab) where LuaBridge3 uses a Lua-constructed object.
- The README says 'every library runs with its maximum safety settings enabled', but only Sol3 gets safety macros in Benchmarks/CMakeLists.txt (SOL_ALL_SAFETIES_ON=1, SOL_NO_EXCEPTIONS=1). LuaBridge3 builds with its defaults, which leave LUABRIDGE_STRICT_STACK_CONVERSIONS off (bool accepts nil, strings accept numbers). Four converter cases exist only for LuaBridge3, and the 'link-time optimization' wording has no matching flag in the CMake files.
- If Lua is compiled as C and exceptions are enabled, a C++ exception escaping a registered lua_CFunction longjmps through C++ frames unless you define LUABRIDGE_SAFE_LUA_C_EXCEPTION_HANDLING, which Config.h says costs performance; the metatable security model is bypassed if scripts get the debug library.

## Known shortcomings

- Downgraded: the headline userdata-access win is not like for like (LuaBridge3 does one read where the Sol3 and vanilla cases do read, write and read: 70.2 vs 299.9 ns), and every Sol3 script case pays an extra lua['name']() proxy call per iteration that the LuaBridge3 harness skips by calling lua_pcall directly. Vanilla LuaBridge is faster on 10 of 22 shared cases and Sol3 on most C++-side table operations; no compiler or CPU stated, and the sol2 version is ambiguous (CMakeLists pins v3.3.0, Benchmarks/README.md says v3.5.0).
- Enricher: the README's 'max safety for all' is false (only Sol3 gets SOL_ALL_SAFETIES_ON while LuaBridge3 runs defaults with LUABRIDGE_STRICT_STACK_CONVERSIONS=0); the Sol3 derived cases bind a raw pointer against a Lua-owned LuaBridge3 object, 4 converter cases are LuaBridge3-only, deriveClass and index-fallback classes lose the upvalue fast path (derived base 538.9 ns vs 91.8 ns derived method), and Sol3 is 1.6-3.3x faster on C++-side table access.

## Caveats and trade-offs

First-party chart only, embedded as an image (Images/benchmarks.png); no hardware, compiler or compiler version stated. Harness is not like-for-like: (1) userdata variable access, access large and access last run 'return b.var' for LuaBridge3 but 'b.var = b.var + 1.0 return b.var' (two reads plus a write) for Sol3 and vanilla LuaBridge, so the largest claimed wins (70.2 vs 299.9 ns) compare one operation against three; (2) LuaBridge3 and vanilla cases invoke the Lua script with raw lua_getglobal + lua_pcall while every Sol3 script case goes through sol's lua["name"]() proxy lookup and call each iteration, adding C++-side overhead only to Sol3 (Sol3 c function 116.2 vs c function through lua in c 34.3, a gap of about 82 ns that LuaBridge3 does not show, 44.2 vs 40.4; rough inference derived from page data). On cases that use each library's own C++ API on both sides (table get/set, chained, global get, multi return, stateful function object), Sol3 is mostly faster. Vanilla LuaBridge beats LuaBridge3 on 10 of 22 shared cases, mostly call paths. Sol2 version is ambiguous: Benchmarks/CMakeLists.txt pins v3.3.0 while Benchmarks/README.md says v3.5.0, and vanilla LuaBridge is fetched from master. README says it 'competes directly with sol2', not that it beats it. Baseline (other binding libraries) is not in the category list (Lua, Duktape, QuickJS). Derived from vinniefalco/LuaBridge per README.

Dependency-free binding that works with PUC Lua, LuaJIT, Luau and Ravi; supports many C++17/20/23 std types, lambdas and multiple inheritance; works with or without exceptions.

## Maintenance

Active (1,038 commits, last commit 2026-09-11 per the verified record, 4 open issues including a callWithHandler message bug, #263), MIT-licensed, header-only with a single-header amalgamation and a vcpkg port, so easy to vendor; v3 broke API compatibility with vanilla LuaBridge, and an open issue (#273) reports LuaResult changing twice within v3.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party Google Benchmark code is public (Benchmarks/benchmark_luabridge3.cpp, benchmark_sol3.cpp, benchmark_luabridge.cpp; Release build, embedded Lua 5.4.8), but no compiler, flags beyond the CMake build type, or CPU model are stated, so not A; the numbers exist only in the README chart image Images/benchmarks.png.
- **Verifier notes:** Numbers in the record match the chart, but the claim is overstated: the biggest wins (userdata variable access 70.2 vs 299.9/269.3 ns) time one property read for LuaBridge3 against a read-modify-write-read for Sol3 and vanilla, and every Sol3 script case pays an extra lua["name"]() proxy call that the LuaBridge3 harness avoids with raw lua_pcall. Keep at C with harness flaws documented; it is slower than vanilla LuaBridge on 10 of 22 shared cases and slower than Sol3 on most C++-side table cases.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `is_fork_of`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kunitoki/LuaBridge3/HEAD/README.md>
  - <https://raw.githubusercontent.com/kunitoki/LuaBridge3/HEAD/Images/benchmarks.png>
  - <https://github.com/kunitoki/LuaBridge3>
  - <https://github.com/kunitoki/LuaBridge3/commits>
  - <https://github.com/kunitoki/LuaBridge3/tree/master/Benchmarks>
  - <https://raw.githubusercontent.com/kunitoki/LuaBridge3/HEAD/Benchmarks/README.md>
  - <https://raw.githubusercontent.com/kunitoki/LuaBridge3/HEAD/Benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/kunitoki/LuaBridge3/HEAD/Benchmarks/benchmark_common.hpp>
  - <https://raw.githubusercontent.com/kunitoki/LuaBridge3/HEAD/Benchmarks/benchmark_luabridge3.cpp>
  - <https://raw.githubusercontent.com/kunitoki/LuaBridge3/HEAD/Benchmarks/benchmark_sol3.cpp>
  - <https://raw.githubusercontent.com/kunitoki/LuaBridge3/HEAD/Benchmarks/benchmark_luabridge.cpp>
  - <https://raw.githubusercontent.com/kunitoki/LuaBridge3/HEAD/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/kunitoki/LuaBridge3>
  - <https://raw.githubusercontent.com/kunitoki/LuaBridge3/HEAD/README.md>
  - <https://raw.githubusercontent.com/kunitoki/LuaBridge3/HEAD/Images/benchmarks.png>
  - <https://raw.githubusercontent.com/kunitoki/LuaBridge3/HEAD/Benchmarks/README.md>
  - <https://raw.githubusercontent.com/kunitoki/LuaBridge3/HEAD/Benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/kunitoki/LuaBridge3/HEAD/Benchmarks/benchmark_common.hpp>
  - <https://raw.githubusercontent.com/kunitoki/LuaBridge3/HEAD/Benchmarks/benchmark_luabridge3.cpp>
  - <https://raw.githubusercontent.com/kunitoki/LuaBridge3/HEAD/Benchmarks/benchmark_sol3.cpp>
  - <https://raw.githubusercontent.com/kunitoki/LuaBridge3/HEAD/Benchmarks/benchmark_luabridge.cpp>
  - <https://raw.githubusercontent.com/kunitoki/LuaBridge3/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/kunitoki/LuaBridge3/HEAD/CHANGES.md>
  - <https://raw.githubusercontent.com/kunitoki/LuaBridge3/HEAD/Source/LuaBridge/detail/CFunctions.h>
  - <https://raw.githubusercontent.com/kunitoki/LuaBridge3/HEAD/Source/LuaBridge/detail/Namespace.h>
  - <https://raw.githubusercontent.com/kunitoki/LuaBridge3/HEAD/Source/LuaBridge/detail/Config.h>
  - <https://raw.githubusercontent.com/kunitoki/LuaBridge3/HEAD/Source/LuaBridge/detail/Userdata.h>
  - <https://raw.githubusercontent.com/kunitoki/LuaBridge3/HEAD/Source/LuaBridge/detail/ClassInfo.h>
  - <https://raw.githubusercontent.com/kunitoki/LuaBridge3/HEAD/Documentation/security/index.md>
  - <https://github.com/kunitoki/LuaBridge3/tree/master/Source/LuaBridge/detail>
  - <https://github.com/kunitoki/LuaBridge3/tree/master/Documentation>
  - <https://github.com/kunitoki/LuaBridge3/tree/master/Documentation/security>
  - <https://github.com/kunitoki/LuaBridge3/issues?q=is%3Aissue+is%3Aopen>
  - <https://github.com/kunitoki/LuaBridge3/issues?q=is%3Aissue+crash+OR+performance+OR+slow>
  - <https://github.com/kunitoki/LuaBridge3/issues/194>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/kunitoki/luabridge3`) · [data/wave12/enrich/raw/github_com_kunitoki_luabridge3.json](../../../data/wave12/enrich/raw/github_com_kunitoki_luabridge3.json) (enrichment confidence 0.8)

</details>
