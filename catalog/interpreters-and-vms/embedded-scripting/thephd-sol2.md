# sol2

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Header-only C++17 Lua binding whose wrapper overhead sits closest to the raw Lua C API among 15 binding libraries.

| | |
|---|---|
| **Beats** | Other C++ Lua binding libraries (LuaBridge, OOLua, Kaguya, luwra, Selene, SWIG, tolua++ and others); floor is the plain Lua C API |
| **Claimed result** | README: 'Fastest in the land (see: sol2 bar in graph)'; benchmarks page: sol 'seems to take the cake in most categories for speed'. The page has graphs only, no numeric table. |
| **Workload** | Per-operation overhead of binding layers over the Lua C API (member function call, userdata variable access, table get/set, multi-return and others) measured with nonius in the lua-bindings-shootout repo. |
| **Metric** | latency |
| **Compiler and flags** | All libraries compiled against a DLL build of Lua 5.3.3, no link-time optimization (per page); compiler and flags otherwise not stated |
| **Adoption** | 5.2k stars |
| **Last commit** | 2025-03-07 |
| **Links** | [repository](https://github.com/ThePhD/sol2) · [benchmark](https://raw.githubusercontent.com/ThePhD/sol2/develop/documentation/source/benchmarks.rst) |

## Verdict

The author's lua-bindings-shootout (raw Google Benchmark JSON dated 2018-09-28, Windows x64, 8 logical CPUs at 2592 MHz, Lua 5.3.x as a DLL, sol2 v2.20.0 and sol3 of that date with safeties off, compiler not stated) puts sol2 or sol3 first among bindings in about 10 of 22 tests and within a few percent of the leader in most others (derived from page data); sol1 (old_sol), luwra, lua-api-pp, OOLua, kaguya or LuaBridge win the rest, and hand-written C API code beats sol in every test except table chained get (plus a tie on global get). The third-party satoren suite (sol2 v2.5.1, 2016) and LuaBridge3's 2026 safety-on chart give mixed or opposite results, so 'fastest in the land' holds only for unchecked builds on 2018-era versions.

## Use it when

- Embedding Lua or LuaJIT in a C++17 application (games, tools, plugin hosts) where calls cross the C++/Lua boundary often and binding overhead shows up in profiles.
- C++-side table get/set and calling Lua functions from C++: in the 2018 shootout sol2 was within about 0 to 25% of hand-written C API code (table chained get 42.9 vs 43.2 ns, Lua function call 34.5 vs 32.6 ns).
- Binding member functions with c_call: sol3 was the fastest binding on member function calls (6.9 us per 51 set+get iterations vs 5.5 us plain C, 7.5 us OOLua, 21.3 us vanilla LuaBridge).
- You need broad features in one header: overloads, multiple inheritance base/derived casts, std::optional/variant, containers, coroutines.
- Code that must target both PUC Lua and LuaJIT from one binding layer.

## Skip it when

- You ship with full argument and userdata type checking: sol's speed numbers come from its default unchecked mode, and LuaBridge3's 2026 chart, run with every library at maximum safety, has Sol3 slower on most script-invoked cases (member function call 356.9 vs 152.4 ns).
- Compile time or binary size matter: heavy template metaprogramming makes translation units that include sol slow to build.
- You need Luau or Ravi support: LuaBridge3 claims those, sol2 documents Lua 5.1+ and LuaJIT only.
- Toolchains newer than its last release: GCC 15 and Clang 19 hit 'no member named construct' errors in sol::optional&lt;T&&gt; (issues #1617, #1692, #1695); the fix sits on the v3.5.0 tag but users report it is not in a packaged release.
- Returning C++ objects by value to Lua is your hot path: in the 2018 shootout sol2 (14.3 us) was about 1.7x slower than luwra (8.5 us) and lua-api-pp (8.6 us) on return userdata.

## How it is fast

Bound functions can be transported as compile-time template arguments (sol::c_call&lt;decltype(&f), &f&gt;), which yields a plain lua_CFunction with no upvalue or std::function indirection. By default it reads values with the unchecked lua_to\* functions rather than lua_check\*, and argument and userdata checks are only compiled in debug builds or with SOL_ALL_SAFETIES_ON. Table access goes through lazy proxy objects so chained lookups like lua["a"]["b"]["c"] do not materialize intermediate references, and usertype method lookup avoids per-call string handling.

## Compared with alternatives

Pick sol2 over LuaBridge3 when you run unchecked release builds, do much C++-side table access, or need sol's wider feature set (overloads, multiple inheritance, containers); pick LuaBridge3 when you ship with full safety checks, want faster compiles, or target Luau/Ravi. Engines like Luau, LuaJIT Remake or Daslang speed up the script itself, which sol2 does not; it only trims the C++/Lua boundary cost.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | Lua 5.1-5.4 or LuaJIT 2.x headers and library (the user supplies them) |
| **Minimum toolchain** | C++17; GCC 7+, Clang 3.9+, Visual Studio 2017+ per README (newest GCC 15 / Clang 19 need the v3.5.0 tag or develop) |
| **Platforms** | any with a C++17 compiler; README lists Windows, Linux, macOS, Android and iOS builds |
| **Thread safety** | None beyond Lua's own: docs say Lua has no thread safety and recommend one sol::state per thread with serialized transfer between states. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw in the lua-bindings-shootout baseline: plain_c_member_function_call stores a basic\* in an 8-byte userdata, but basic_get_wrap/basic_set_wrap cast lua_touserdata(L, 1) straight to basic\* instead of dereferencing basic\*\*, so the 'plain C' floor reads and writes the pointer slot as the double var and never touches the C++ object. The check script still passes (set then get the same 8 bytes), it is undefined behavior, and it skips one indirection, so the floor is slightly flattered; binding rankings are unaffected.
- sol2 and sol3 table_chained_get benchmarks never validate their accumulated result (no lbs::expect), unlike plain_c, LuaBridge and OOLua; sol2's 42.9 ns there edges plain C's 43.2 ns, which is within noise.
- Default build does no argument or userdata type checking in release: passing the wrong userdata or nil to a bound member function can crash; define SOL_ALL_SAFETIES_ON to get checked behaviour, at a runtime cost the published benchmarks do not show.
- Docs page says results were taken with nonius against a Lua 5.3.3 DLL; the shootout repo's only raw data (benchmark_results/lua_bindings_shootout.json, 2018-09-28) is Google Benchmark output from a Windows x64 build on an 8-logical-CPU 2592 MHz machine, with compiler and flags not recorded.

## Known shortcomings

- First-party 2018 graphs with no numbers in the text; the third-party satoren suite (i5-4460, GCC 5.3.1, sol2 v2.5.1, 2016) has sol2 winning 2 of 6 categories and mid-pack on member calls. Binding library, not an interpreter; last commit 2025-03-07 (stale).
- Enricher: raw lua-bindings-shootout data (benchmark_results/lua_bindings_shootout.json, Google Benchmark, 2018-09-28, Windows x64, 8 CPUs at 2592 MHz, compiler unstated) has sol the best binding in 10 of 22 tests (member call per 51 set+get loops: sol3 6895 ns vs plain C 5503, OOLua 7456, LuaBridge 21286); the plain-C member_function_call floor casts lua_touserdata straight to basic\* (undefined behaviour, rankings unchanged) and the sol table_chained_get cases never validate their result. The 'fastest' ranking rests on sol's default no-safety-checks mode and reverses under LuaBridge3's all-safety chart; GCC 15 and Clang 19 compile errors (#1695) are fixed only on the v3.5.0 tag, not in a packaged release.

## Caveats and trade-offs

Evidence is first-party graphs from 2018 (page dated May 17th, 2018) from the author's own lua-bindings-shootout (nonius, Lua 5.3.3 DLL per the docs page; shootout README lists plain C on Lua 5.3.4, sol2 v2.20.0 and sol3 'latest'); no numbers in text and no hardware, compiler or flags stated. Approximate values read off benchmark_results/member function call.png: plain_c about 115 ns, sol3 about 135, oolua about 145, sol2 about 150, luwra about 205, luabridge about 420, old sol about 425, toluapp about 590 (read from the image, not text). Third-party counter-evidence: satoren/lua_binding_benchmark result/result.csv (Intel Core i5-4460, GCC 5.3.1, CMake Release, units not stated, lower is better) puts sol2 v2.5.1 fastest among bindings on global table (338.4) and table chain (561.0, below plain API 596.5), but behind kaguya (1006.9), luacppinterface (1002.0) and the plain API (1086.6) on C++ object member call (sol2 1342.9), behind luwra on C function call (234.7 vs 254.8) and returning a class object (1253.3 vs 1314.4), and behind sol v1 on Lua function call (293.4 vs 330.0). A 2026 first-party chart in the LuaBridge3 README shows Sol3 slower than LuaBridge3 on most script-invoked cases (member function call 356.9 vs 152.4 ns) but faster on C++-side table get/set; that harness is biased against Sol3 (extra lua["name"]() call per iteration, unequal userdata access scripts). Binding-layer overhead, not script execution speed; every binding is slower than the plain Lua C API. Baseline (other binding libraries) is not in the category list (Lua, Duktape, QuickJS). Last commit 2025-03-07, so stale.

Header-only C++17 binding for Lua, LuaJIT and others; heavy template use means long compile times; its fast paths (c_call and disabled type checks) trade safety for speed.

## Maintenance

Stale: last commit 2025-03-07 (v3.5.0 tag 2025-02-25), 292 open issues, newest-compiler fixes not in a packaged release; MIT-licensed, header-only and widely used (5.2k stars), so vendoring a pinned commit is easy.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The benchmarks page is first-party (2018) with graphs only and no numbers in text; the lua-bindings-shootout code is public but states no compiler, flags or CPU, so C. A third-party suite (satoren/lua_binding_benchmark: i5-4460, GCC 5.3.1, CMake Release, code public) exists but tests sol2 v2.5.1 from 2016 and shows mixed results, so it does not support an upgrade.
- **Verifier notes:** Record is accurate: README says 'Fastest in the land' and the docs page says sol 'seems to take the cake in most categories', with graphs only. Keep at C; add that the only independent suite found (satoren, i5-4460, GCC 5.3.1, sol2 v2.5.1, 2016) shows sol2 winning 2 of 6 categories and mid-pack on member calls, and that all evidence predates current sol3 releases.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ThePhD/sol2/develop/documentation/source/benchmarks.rst>
  - <https://github.com/ThePhD/sol2>
  - <https://github.com/ThePhD/sol2/commits/develop>
  - <https://raw.githubusercontent.com/ThePhD/lua-bindings-shootout/master/README.md>
  - <https://raw.githubusercontent.com/ThePhD/lua-bindings-shootout/master/benchmark_results/member%20function%20call.png>
  - <https://github.com/satoren/lua_binding_benchmark>
  - <https://github.com/satoren/lua_binding_benchmark/tree/master/result>
  - <https://raw.githubusercontent.com/satoren/lua_binding_benchmark/HEAD/result/result.csv>
  - <https://raw.githubusercontent.com/satoren/lua_binding_benchmark/HEAD/result/system_info.txt>
  - <https://raw.githubusercontent.com/satoren/lua_binding_benchmark/HEAD/result/library_info.csv>
  - <https://raw.githubusercontent.com/satoren/lua_binding_benchmark/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/satoren/lua_binding_benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/satoren/lua_binding_benchmark/HEAD/multiple_lua_version_benchmark.sh>
  - <https://raw.githubusercontent.com/kunitoki/LuaBridge3/HEAD/README.md>
  - <https://raw.githubusercontent.com/kunitoki/LuaBridge3/HEAD/Images/benchmarks.png>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ThePhD/sol2/develop/README.md>
  - <https://raw.githubusercontent.com/ThePhD/sol2/develop/documentation/source/benchmarks.rst>
  - <https://raw.githubusercontent.com/ThePhD/sol2/develop/documentation/source/safety.rst>
  - <https://raw.githubusercontent.com/ThePhD/sol2/develop/documentation/source/threading.rst>
  - <https://raw.githubusercontent.com/ThePhD/sol2/develop/documentation/source/api/c_call.rst>
  - <https://github.com/ThePhD/sol2>
  - <https://github.com/ThePhD/sol2/commits/develop>
  - <https://github.com/ThePhD/sol2/issues?q=is%3Aissue+is%3Aopen+compile+error+gcc+OR+clang>
  - <https://github.com/ThePhD/sol2/issues/1695>
  - <https://github.com/ThePhD/lua-bindings-shootout>
  - <https://github.com/ThePhD/lua-bindings-shootout/tree/master/source>
  - <https://github.com/ThePhD/lua-bindings-shootout/tree/master/benchmark_results>
  - <https://raw.githubusercontent.com/ThePhD/lua-bindings-shootout/master/README.md>
  - <https://raw.githubusercontent.com/ThePhD/lua-bindings-shootout/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ThePhD/lua-bindings-shootout/master/source/benchmark.hpp>
  - <https://raw.githubusercontent.com/ThePhD/lua-bindings-shootout/master/source/lbs_lib.hpp>
  - <https://raw.githubusercontent.com/ThePhD/lua-bindings-shootout/master/source/lbs_lua.hpp>
  - <https://raw.githubusercontent.com/ThePhD/lua-bindings-shootout/master/source/lua_bindings_shootout.cpp>
  - <https://raw.githubusercontent.com/ThePhD/lua-bindings-shootout/master/source/plain_c.cpp>
  - <https://raw.githubusercontent.com/ThePhD/lua-bindings-shootout/master/source/sol2.cpp>
  - <https://raw.githubusercontent.com/ThePhD/lua-bindings-shootout/master/source/sol3.cpp>
  - <https://raw.githubusercontent.com/ThePhD/lua-bindings-shootout/master/source/luabridge.cpp>
  - <https://raw.githubusercontent.com/ThePhD/lua-bindings-shootout/master/source/oolua.cpp>
  - <https://raw.githubusercontent.com/ThePhD/lua-bindings-shootout/master/benchmark_results/lua_bindings_shootout.json>
  - <https://raw.githubusercontent.com/kunitoki/LuaBridge3/HEAD/README.md>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/thephd/sol2`) · [data/wave12/enrich/raw/github_com_thephd_sol2.json](../../../data/wave12/enrich/raw/github_com_thephd_sol2.json) (enrichment confidence 0.75)

</details>
