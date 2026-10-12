# LuaBridge

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++11 Lua binding library without Boost; beat luabind on 8 of 13 rows of a 2018 shootout but trails sol2 and the raw C API.

| | |
|---|---|
| **Beats** | luabind (Boost-based Lua binding library) |
| **Claimed result** | Median cpu_time in ns from the shootout JSON (lower is better), LuaBridge vs luabind on the 13 shared rows: faster on 8, table_get 102.5 vs 224.6 (about 2.2x), table_global_string_get 112.3 vs 199.5 (1.8x), table_global_string_set 15.7 vs 110.9 (7.1x), optional_failure 22.5 vs 147.5 (6.6x), optional_half_failure 138.1 vs 353.0 (2.6x), optional_success 210.0 vs 360.6 (1.7x), return_userdata 16880.7 vs 20403.0 (1.2x), c_function 2950.6 vs 3442.4 (1.17x); slower on 5, member_function_call 21449.3 vs 15694.7, userdata_variable_access 24414.1 vs 15346.0, table_chained_get 276.2 vs 251.1, c_function_through_lua_in_c 131.1 vs 78.5 and lua_function_in_c 131.8 vs 59.3. Ratios and counts derived from page data. Among all 16 bindings LuaBridge ranks 2nd on optional_failure and 3rd on table_global_string_set, but 15th of 16 on member_function_call, 14th of 14 on lua_function_in_c, 12th of 14 on table_get and c_function_through_lua_in_c, and 9th of 10 on userdata_variable_access (derived from page data). |
| **Workload** | ThePhD/lua-bindings-shootout: Google Benchmark micro-benchmarks of binding operations (table get/set, C function calls, optional access, userdata access, member calls) across many C++ Lua binding libraries; median CPU time per operation in ns. |
| **Metric** | latency |
| **Hardware** | 8 logical CPUs at 2592 MHz per the result JSON (CPU model not named; a search snippet says Intel Core i7 2.8 GHz); run dated 2018-09-28. |
| **Compiler and flags** | Windows x64 release build of lua_bindings_shootout.exe (library_build_type release) against PUC-Rio Lua 5.3.4 with Google Benchmark; the repo's CMakeLists sets /std:c++latest for MSVC and no explicit optimization flags; LuaBridge is fetched as a shallow clone of vinniefalco/LuaBridge master with no tag (cmake/Modules/FindLuaBridgeDev.cmake, internal label 1.0.2), so the timed code is the 2018 master, not release 2.10. A WebSearch snippet says Visual Studio 2017 (snippet only). |
| **Adoption** | 1.8k stars, 360 forks; the lua-bindings-shootout harness has 14 stars |
| **Last commit** | 2025-10-13 |
| **Links** | [repository](https://github.com/vinniefalco/LuaBridge) · [benchmark](https://raw.githubusercontent.com/ThePhD/lua-bindings-shootout/HEAD/benchmark_results/lua_bindings_shootout.json) |

## Verdict

ThePhD's lua-bindings-shootout (Google Benchmark medians, Windows x64 release build with MSVC /std:c++latest, PUC Lua 5.3.4, 8 logical CPUs at 2592 MHz with no CPU model or compiler version, run 2018-09-28) timed LuaBridge master as it stood between release 2.1 and 2.1.1 against luabind: faster on 8 of 13 shared rows (table_get 102.5 vs 224.6 ns, optional_failure 22.5 vs 147.5 ns) and slower on 5 (member_function_call 21,449 vs 15,695 ns, userdata_variable_access 24,414 vs 15,346 ns). LuaBridge is slower than the plain Lua C API on every row it shares with it, and those rows measured a release whose table writes through operator[] were broken.

## Use it when

- Replacing luabind to drop Boost: in the 2018 shootout LuaBridge was faster on global and table reads (table_get 102.5 vs 224.6 ns) and optional-value checks (optional_failure 22.5 vs 147.5 ns).
- Existing codebases on the LuaBridge 2.x API that want a conservative, still-released line (2.10, October 2025) with vcpkg and Meson packaging.
- Binding a moderate C++ API (single inheritance, getters/setters, static functions, up to 8 parameters) to PUC Lua 5.1-5.4 or LuaJIT with a C++11 compiler and no build step.
- Mixed object lifetimes: values copied into Lua, raw pointers with C++ lifetime, or shared lifetime through RefCountedObjectPtr/RefCountedPtr.

## Skip it when

- Binding overhead is the bottleneck: in the same shootout LuaBridge is 15th of 16 on member_function_call (21,449 ns vs sol3 6,836 and plain C 5,469), last of 14 on lua_function_in_c (131.8 vs 32.9 ns) and 12th of 13 on multi_return_lua (8,161 vs 2,850 ns); sol2/sol3 or LuaBridge3 are faster on most rows.
- APIs that need overloaded functions or constructors, enumerated constants, multiple inheritance, more than 8 parameters, or std::shared_ptr crossing the boundary (the manual says standard smart pointers 'will not work' and lead to undefined behaviour).
- C++ calls into Lua functions that return several values: LuaRef::operator() runs pcall with one result and returns a single LuaRef.
- Multi-threaded hosts using RefCountedPtr: its counts live in one function-static std::unordered_map with no lock, shared by all lua_States.
- Hosts that cannot tolerate open crash and undefined-behaviour reports: #308 (crash passing a userdata metatable to luaL_tolstring), #289 (crash in Stack&lt;int&gt;::get), #296 (undefined-behaviour and stack-use-after-scope reports when running the tests) and #323 (clang 18/19 leak in readOnlyError) are open among 47 issues.

## How it is fast

Each bound function compiles into a fixed template thunk (Call/CallMember, built from FuncTraits and TypeList) that reads arguments with Stack&lt;T&gt;::get and pushes the result; free-function pointers ride as lightuserdata upvalues and member pointers are placement-new'd into userdata, so a call does no overload matching (overloads are unsupported) and needs no Boost. Class instances get a metatable whose __index metamethod rawgets methods, then looks up the propget table and lua_calls a getter, walking the parent chain, and Userdata::get type-checks by walking class tables in the registry. LuaRef keeps every value in the registry (luaL_ref and luaL_unref per temporary), and C++-to-Lua calls go through pcall, which is why its table-access and Lua-function-call rows are slow next to the plain C API.

## Compared with alternatives

sol2/sol3 (the shootout author's own library) is faster on most rows, and LuaBridge3, a fork of this repository, beats vanilla LuaBridge on 12 of 22 shared cases in its own chart and adds features; pick vanilla LuaBridge only to stay on the 2.x API with minimal change or when moving off luabind with the smallest header set. nanobind binds Python, not Lua, so it is not an alternative.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | Lua 5.1-5.4 or LuaJIT headers and library (include lua.hpp yourself before LuaBridge.h); nothing else |
| **Minimum toolchain** | C++11 (C++17 optional via LUABRIDGE_CXX17 for std::optional and std::string_view); CMake 3.10 only for the unit tests |
| **Platforms** | any platform with a C++11 compiler and Lua; tests cover Lua 5.1.5, 5.2.4, 5.3.6 and 5.4.4 on Linux, macOS, MinGW/MSYS2 and MSVC |
| **Thread safety** | Not documented. A lua_State is single-threaded and LuaBridge adds no locking; RefCountedPtr's global reference-count map is unsynchronized, so it is unsafe across threads even with separate states. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind the numbers: the shootout run (2018-09-28) shallow-cloned LuaBridge master between fc224ab (2018-09-16, 'Take care of LuaRef::Proxy', which removed the table proxy and shipped as release 2.1) and 74992b8 (2018-10-11, 'Restore LuaRef table proxy'). In that window operator[] returned a value copy, so t["k"] = v silently assigned to a temporary (issue #171: 'you can't actually change any table values from C++'); LuaBridge's table_set and table_chained_set rows are not unsupported but failed the harness check with 'unexpected result', and table_get, table_chained_get and the optional_\* rows timed a proxy-less read path that 2.1.1 replaced.
- The headline 7.1x win (table_global_string_set 15.7 vs 110.9 ns) compares LuaBridge's setGlobal helper, a bare push plus lua_setglobal that ties the plain C API (15.1 ns), with luabind's globals(L)["value"] = v proxy object; LuaBridge's own getGlobal path, which builds a registry-backed LuaRef, is 7x slower than its set (112.3 ns). The published JSON also does not match the committed harness: luabridge.cpp marks implicit_inheritance unsupported, yet the JSON holds a timed row (median 16,497 ns).
- Every LuaRef and table item holds registry references (a current TableItem takes two, for table and key, and releases them in its destructor), so C++-side table access in hot loops costs several registry operations; drop to Stack&lt;T&gt; or the C API there.
- Conversions report type errors through lua_error (a longjmp) unless the host calls enableExceptions or wraps calls in pcall; the manual says code must be wrapped in lua_pcall or use a throwing panic handler to be safe, and a lua_State\* parameter must come last in a bound signature or behaviour is undefined.

## Known shortcomings

- ThePhD lua-bindings-shootout (14 stars, run by the sol2 author) has no CPU model or compiler version and timed LuaBridge master unpinned; against luabind it wins 8 rows and loses 5 (the record had omitted c_function_through_lua_in_c 131.1 vs 78.5 and lua_function_in_c 131.8 vs 59.3), and it is slower than the plain Lua C API on every row. Not a duplicate of LuaBridge3 (a fork; upstream 2.x still releases, 2.10 on 2025-10-13).
- Enricher: the shootout run of 2018-09-28 timed LuaBridge master between fc224ab (proxy removed, shipped as 2.1) and 74992b8 (proxy restored 2018-10-11), a window in which t[k] = v silently did nothing (issue #171), so the table_set/table_chained_set rows failed with 'unexpected result' rather than being unsupported and the read rows timed code that 2.1.1 replaced; the headline 7.1x set row compares LuaBridge setGlobal (a bare push plus lua_setglobal, tying plain C at 15.7 vs 15.1 ns) with luabind's globals() proxy object. The result JSON does not match the committed harness (implicit_inheritance is timed but marked unsupported in code).

## Caveats and trade-offs

LuaBridge does not claim to be the fastest: its manual says it 'comes close to the highest possible performance' but 'is not quite the fastest' and that OOLua slightly outperforms it in some tests. The chosen baseline, luabind, is one of the slowest bindings in the shootout and is not a category baseline; against the real floor, the plain Lua C API, LuaBridge is slower on every shared row (c_function 2950.6 vs 2131.0 ns, table_get 102.5 vs 17.6 ns), and it is slower than sol2 and sol3 on most rows, ranking in the lower half of 16 bindings on most tests. Data is from 2018 (Lua 5.3.4, an unpinned 2018 LuaBridge master), the CPU model and compiler version are not stated, and the shootout is run by the author of sol2, a competing library. Several benchmarks have no LuaBridge row (stateful_function_object, multi_return, table_set, table_chained_set). Not a duplicate of LuaBridge3: kunitoki/LuaBridge3 is a fork of this repository, while vinniefalco/LuaBridge remains a separately maintained 2.x line (dmitry-t released 2.10 on 2025-10-13) with its own third-party evidence; LuaBridge3's own README chart shows LuaBridge3 faster than vanilla LuaBridge on 12 of 22 shared cases. [retier] ThePhD lua-bindings-shootout (14 stars, run by the sol2 author, no CPU model or compiler version, LuaBridge master unpinned). The 2018-09-28 run timed master between fc224ab (proxy removed, shipped as 2.1) and 74992b8 (proxy restored 2018-10-11), when t[k] = v silently did nothing (issue #171): the table_set and table_chained_set rows failed with 'unexpected result' rather than being unsupported, and the read rows timed code that 2.1.1 replaced. The headline 7.1x set row compares LuaBridge setGlobal (bare push plus lua_setglobal, tying plain C at 15.7 vs 15.1 ns) with luabind's globals() proxy object. Against luabind it wins 8 rows and loses 5 (including c_function_through_lua_in_c 131.1 vs 78.5 and lua_function_in_c 131.8 vs 59.3) and it is slower than the plain Lua C API on every row. The result JSON does not match the committed harness (implicit_inheritance timed but marked unsupported). Not a duplicate of LuaBridge3 (a fork); upstream 2.x still releases (2.10, 2025-10-13).

Header-only, dependency-free binding layer for Lua 5.1+ and LuaJIT. No enumerated constants, no overloaded functions or constructors, at most 8 parameters unless TypeListValues is extended, no global variables outside a named scope (manual).

## Maintenance

MIT, header-only and still released (2.10 by dmitry-t on 2025-10-13 after a 10-month gap, 47 open issues), so it is easy to vendor, but the only third-party speed evidence is a 2018 run of a short-lived master snapshot that a few weeks later needed a fix to make table writes work.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): downgrade; tier before verification B, tier now C.
- **Tier reason:** The numbers are real medians in ThePhD/lua-bindings-shootout benchmark_results/lua_bindings_shootout.json, measured by a third party, but the harness is obscure (14 stars, run by the author of the competing sol2), the CPU model and compiler version are not stated in the repo (8 logical CPUs at 2592 MHz, Windows x64 release build, 2018-09-28), and LuaBridge is pulled from an unpinned shallow clone of master (cmake/Modules/FindLuaBridgeDev.cmake), so it falls short of a well-known independent suite. The win over the chosen baseline (luabind) is mixed and the record omitted two of its losses.
- **Verifier notes:** Separate project, not a duplicate of LuaBridge3 (kunitoki/LuaBridge3 is the fork; this upstream 2.x line is still maintained, release 2.10 on 2025-10-13, and the shootout timed this repository's master, not LuaBridge3). Downgraded B to C: obscure 14-star harness from the sol2 author without CPU model or compiler version, unpinned LuaBridge revision, and a mixed 8-wins-5-losses result against luabind, a slow non-incumbent; record two omitted losses and 'slower than the plain Lua C API on every row' as shortcomings. Metadata confirmed: MIT, 1.8k stars, last commit 2025-10-13, active.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** lua-bindings-shootout (verifier downgrade B to C); enricher code and log reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ThePhD/lua-bindings-shootout/HEAD/benchmark_results/lua_bindings_shootout.json>
  - <https://raw.githubusercontent.com/ThePhD/lua-bindings-shootout/HEAD/README.md>
  - <https://raw.githubusercontent.com/ThePhD/lua-bindings-shootout/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ThePhD/lua-bindings-shootout/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/ThePhD/lua-bindings-shootout/HEAD/cmake/Modules/FindLuaBridgeDev.cmake>
  - <https://github.com/ThePhD/lua-bindings-shootout>
  - <https://github.com/vinniefalco/LuaBridge>
  - <https://github.com/vinniefalco/LuaBridge/commits/master.atom>
  - <https://raw.githubusercontent.com/vinniefalco/LuaBridge/HEAD/README.md>
  - <https://raw.githubusercontent.com/vinniefalco/LuaBridge/HEAD/CHANGES.md>
  - <https://raw.githubusercontent.com/vinniefalco/LuaBridge/HEAD/Manual.html>
- **Sources the enricher read:**
  - <https://github.com/vinniefalco/LuaBridge>
  - <https://github.com/vinniefalco/LuaBridge/commits/master>
  - <https://github.com/vinniefalco/LuaBridge/commits/master?since=2018-09-01&until=2018-10-31>
  - <https://github.com/vinniefalco/LuaBridge/tags>
  - <https://github.com/vinniefalco/LuaBridge/tags?after=2.3.1>
  - <https://github.com/vinniefalco/LuaBridge/issues>
  - <https://github.com/vinniefalco/LuaBridge/issues/171>
  - <https://raw.githubusercontent.com/vinniefalco/LuaBridge/HEAD/README.md>
  - <https://raw.githubusercontent.com/vinniefalco/LuaBridge/HEAD/CHANGES.md>
  - <https://raw.githubusercontent.com/vinniefalco/LuaBridge/HEAD/Manual.html>
  - <https://raw.githubusercontent.com/vinniefalco/LuaBridge/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/vinniefalco/LuaBridge/HEAD/Source/LuaBridge/LuaBridge.h>
  - <https://raw.githubusercontent.com/vinniefalco/LuaBridge/HEAD/Source/LuaBridge/RefCountedPtr.h>
  - <https://raw.githubusercontent.com/vinniefalco/LuaBridge/HEAD/Source/LuaBridge/detail/LuaRef.h>
  - <https://raw.githubusercontent.com/vinniefalco/LuaBridge/HEAD/Source/LuaBridge/detail/CFunctions.h>
  - <https://raw.githubusercontent.com/vinniefalco/LuaBridge/HEAD/Source/LuaBridge/detail/Userdata.h>
  - <https://raw.githubusercontent.com/vinniefalco/LuaBridge/HEAD/Source/LuaBridge/detail/Stack.h>
  - <https://raw.githubusercontent.com/vinniefalco/LuaBridge/HEAD/Source/LuaBridge/detail/Namespace.h>
  - <https://raw.githubusercontent.com/vinniefalco/LuaBridge/HEAD/Source/LuaBridge/detail/LuaHelpers.h>
  - <https://raw.githubusercontent.com/vinniefalco/LuaBridge/HEAD/Source/LuaBridge/detail/Config.h>
  - <https://raw.githubusercontent.com/vinniefalco/LuaBridge/HEAD/Source/LuaBridge/detail/FuncTraits.h>
  - <https://raw.githubusercontent.com/vinniefalco/LuaBridge/HEAD/Source/LuaBridge/detail/TypeList.h>
  - <https://raw.githubusercontent.com/vinniefalco/LuaBridge/HEAD/Source/LuaBridge/detail/ClassInfo.h>
  - <https://raw.githubusercontent.com/vinniefalco/LuaBridge/2.0/Source/LuaBridge/detail/LuaRef.h>
  - <https://raw.githubusercontent.com/vinniefalco/LuaBridge/2.1/Source/LuaBridge/detail/LuaRef.h>
  - <https://raw.githubusercontent.com/vinniefalco/LuaBridge/2.1/Source/LuaBridge/detail/LuaHelpers.h>
  - <https://raw.githubusercontent.com/vinniefalco/LuaBridge/2.1/Source/LuaBridge/detail/Security.h>
  - <https://raw.githubusercontent.com/vinniefalco/LuaBridge/2.1/Source/LuaBridge/detail/Namespace.h>
  - <https://raw.githubusercontent.com/vinniefalco/LuaBridge/2.1/Source/LuaBridge/LuaBridge.h>
  - <https://raw.githubusercontent.com/vinniefalco/LuaBridge/2.1.1/Source/LuaBridge/detail/LuaRef.h>
  - <https://raw.githubusercontent.com/vinniefalco/LuaBridge/2.2/Source/LuaBridge/detail/LuaRef.h>
  - <https://raw.githubusercontent.com/vinniefalco/LuaBridge/2.3/Source/LuaBridge/detail/LuaRef.h>
  - <https://raw.githubusercontent.com/vinniefalco/LuaBridge/2.6/Source/LuaBridge/detail/LuaRef.h>
  - <https://github.com/ThePhD/lua-bindings-shootout>
  - <https://github.com/ThePhD/lua-bindings-shootout/blob/master/cmake/Modules/FindLuaBridgeDev.cmake>
  - <https://github.com/ThePhD/lua-bindings-shootout/commits/master/source/luabridge.cpp>
  - <https://github.com/ThePhD/lua-bindings-shootout/commits/master/benchmark_results/lua_bindings_shootout.json>
  - <https://raw.githubusercontent.com/ThePhD/lua-bindings-shootout/HEAD/README.md>
  - <https://raw.githubusercontent.com/ThePhD/lua-bindings-shootout/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ThePhD/lua-bindings-shootout/HEAD/source/luabridge.cpp>
  - <https://raw.githubusercontent.com/ThePhD/lua-bindings-shootout/HEAD/source/luabind.cpp>
  - <https://raw.githubusercontent.com/ThePhD/lua-bindings-shootout/HEAD/source/plain_c.cpp>
  - <https://raw.githubusercontent.com/ThePhD/lua-bindings-shootout/HEAD/source/sol3.cpp>
  - <https://raw.githubusercontent.com/ThePhD/lua-bindings-shootout/HEAD/benchmark_results/lua_bindings_shootout.json>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/vinniefalco/luabridge`) · [data/wave12/enrich/raw/github_com_vinniefalco_luabridge.json](../../../data/wave12/enrich/raw/github_com_vinniefalco_luabridge.json) (enrichment confidence 0.7)

</details>
