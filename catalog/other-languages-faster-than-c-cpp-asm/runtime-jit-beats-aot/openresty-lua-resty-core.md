# lua-resty-core (LuaJIT FFI API for ngx_lua) vs the ngx_lua built-in Lua C API

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Lua` · `BSD-2-Clause` · 🟢 active

> LuaJIT-FFI reimplementation of ngx_lua's ngx.\* API that lets calling Lua code stay JIT-compiled; claimed faster than the Lua C API, never measured.

| | |
|---|---|
| **Beats** | the Lua C API implementation of the ngx.\* and ngx.shared.\* functions in lua-nginx-module (ngx_lua, C) |
| **Claimed result** | No numbers. README: 'its FFI implementation is both faster, safer, and more complete than the Lua C API of the ngx_lua module.' Caveat in the same README: 'You will only observe speedup when you get a good part of your user Lua code JIT compiled.' |
| **Workload** | Calls of the ngx_lua API functions from Lua code running under LuaJIT through the FFI-based reimplementation versus the C API implementation; no workload is specified. |
| **Metric** | other |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Why it wins** | README: the Lua C API 'will never be JIT compiled and the user Lua code is always interpreted (slowly)', while the FFI-based API calls can be JIT compiled by LuaJIT. |
| **Adoption** | 855 stars, 288 forks; part of the OpenResty project |
| **Last commit** | 2026-08-24 |
| **Links** | [repository](https://github.com/openresty/lua-resty-core) · [benchmark](https://github.com/openresty/lua-resty-core) |

## Verdict

Nothing was measured. The README states, with no numbers, hardware, versions or benchmark code, that the FFI implementation is 'faster, safer, and more complete' than ngx_lua's Lua C API, and warns it can be slower when code is interpreted. The only numbers found (issue #15) are a user's slowdown, about 20 ms to 250 ms latency. The claimed effect is LuaJIT trace compilation of the calling Lua code against interpreted code; the same C functions still run, so this is not JIT code beating AOT C.

## Use it when

- You run OpenResty or ngx_lua v0.10.16 or later: it is already loaded and cannot be turned off, so keep the bundled copy.
- Hot request-path Lua that calls ngx.shared.DICT get/set/incr, ngx.re.match/find/gsub, ngx.var or ngx.ctx inside loops LuaJIT can trace.
- You need APIs that exist only here: dynamic upstream balancing (ngx.balancer), certificate selection in the SSL handshake (ngx.ssl, ngx.ssl.clienthello), cross-request semaphores, non-blocking subprocesses (ngx.pipe) or error-log capture.
- You can profile with LuaJIT tools (lj-vm-states, sample-bt, lj-lua-stacks) to find code that falls back to the interpreter, as the author recommends.

## Skip it when

- Code that mostly runs in the LuaJIT interpreter (NYI-heavy, rarely hot, coroutine-heavy). The README warns of a 'performance drop in interpreted mode', and in issue #15 a user saw latency rise from about 20 ms to about 250 ms on a 15k req/s server after enabling it on OpenResty 1.7.7.2, with no improvement on 1.11.2.4.
- Outside nginx, or with PUC Lua: it works only inside ngx_http_lua_module or ngx_stream_lua_module on LuaJIT with FFI. LuaJIT 2.0 triggers an ALERT log line, and 2.1 is required in practice.
- Mixing versions: a standalone copy paired with a different ngx_lua fails at startup ('ngx_http_lua_module 0.10.32 required but got ...').
- If you need a measured speedup figure to justify a migration: none is published in the repository, its issues or the web results found.

## How it is fast

Each API is a Lua function that calls a flat C entry point exported by ngx_lua, such as ngx_http_lua_ffi_shdict_get, through ffi.cdef and ffi.C. Results come back through preallocated cdata out-parameters and a reused scratch buffer (base.get_string_buf, 4096 bytes by default), not through the Lua stack of a lua_CFunction. LuaJIT's trace compiler can compile FFI calls into the trace, so user loops that call these APIs can stay compiled; per the README, Lua C API functions are never JIT-compiled. The C work itself (shared-memory lookup, PCRE matching, hashing) is unchanged, so the gain is in call overhead and keeping the caller compiled, not faster C.

## Compared with alternatives

It is not an alternative to its siblings: on OpenResty it is the API you already use. For actual numbers on the mechanism, see the LuaJIT 2.0 FFI entry from dyu/ffi-overhead, which measured 1.78 vs 2.36 ns per plusone() call against C through the dynamic linker. pflua is the other LuaJIT-in-networking entry with a measured win over C.

## Integration

| | |
|---|---|
| **Form** | module (pure Lua, bundled with OpenResty or installed with make install LUA_LIB_DIR=...) |
| **Dependencies** | LuaJIT 2.1 (OpenResty's luajit2 fork recommended by ngx_lua), ngx_http_lua_module exactly 0.10.32 or ngx_stream_lua_module exactly 0.0.20 (base.lua check), lua-resty-lrucache; dist.ini also lists nginx &gt;= 1.29.2 |
| **Minimum toolchain** | LuaJIT 2.1 with FFI; the ngx_lua release it was cut for |
| **Platforms** | Wherever OpenResty runs with LuaJIT FFI. Linux is the main target. macOS gets separate struct-argument FFI entry points for shared dicts, and regexes compiled in the init phase are never JIT-compiled or cached there (PCRE 8.43+ MAP_JIT issue). Other platforms not documented. |
| **Thread safety** | One Lua VM per nginx worker process, single-threaded. Shared-dict operations take the zone's shared-memory lock inside the C functions. ngx.semaphore works across requests but not across worker processes (README). |
| **Drop-in for the baseline** | partial — it replaces the listed ngx.\* and ngx.shared.\* functions in place under the same names, but only those; the C API functions it replaced have since been removed from ngx_lua, so there is no longer a choice to make |

## Gotchas

- The baseline no longer exists. In current lua-nginx-module, src/ngx_http_lua_shdict.c registers Lua C API functions only for lpush, rpush, lpop, rpop, llen, flush_expired and get_keys; get, set, incr, ttl, expire, flush_all, capacity and free_space exist only as ngx_http_lua_ffi_\* exports. Likewise md5, base64 and escape_uri are FFI-only in ngx_http_lua_string.c. A head-to-head 'FFI vs C API' run therefore needs ngx_lua v0.10.15 or earlier, and lua_load_resty_core has had no effect since v0.10.16.
- Strict version lock with inconsistent docs. base.lua refuses anything but ngx_lua 0.10.32 (stream 0.0.20), while the README prerequisites say v0.10.25 / v0.0.13 and dist.ini says ngx_http_lua = 0.10.30. Always use the copy shipped with your OpenResty release, as the README's WARNING says.
- Load it only in init_by_lua\*. The author says FFI code paths 'would be very slow if being interpreted' and suggests require "jit".opt.start("minstitch=3") (trace stitching) so as much code as possible is compiled (issue #15).
- The README's 'safer' claim needs care. FFI code has its own pitfalls: commit a60ab0e (2026-06-06) fixed a NULL check in ngx.ssl get_upstream_ssl_pointer that could never fire (cdata pointers are always truthy), a crash in ngx.resp set_status when reason was nil, and errors raised as raw cdata in ngx.get_phase.

## Known shortcomings

- No numbers; the FFI path still calls ngx_http_lua_ffi_\* C functions, so the win is the LuaJIT trace compiler avoiding the Lua C API, not Lua beating C; its own README says it is slower when interpreted; arguably off-category.
- The baseline is gone: lua_load_resty_core has been a no-op since ngx_lua v0.10.16, and current ngx_lua provides shdict get/set/incr, md5, base64 and escape_uri only as ngx_http_lua_ffi_\* functions, so a head-to-head needs ngx_lua 0.10.15 or older. The only numbers found show a slowdown (issue #15: latency 20 ms to 250 ms on OpenResty 1.7.7.2). Strict version lock: base.lua requires ngx_lua exactly 0.10.32 while the README says 0.10.25 and dist.ini 0.10.30; commit a60ab0e fixed a NULL check that never fired (cdata is truthy). JIT versus interpreter, not JIT versus AOT C (off-category).

## Caveats and trade-offs

Qualitative claim only: no benchmark in the README and none found elsewhere (one web search turned up package mirrors and an api7.ai explainer without timings, snippet only). 855 stars, under the 1k notability guideline, kept for project notability (loaded by default since OpenResty 1.15.8.1). Not Lua beating C: the FFI path still calls C functions exported by lua-nginx-module (e.g. ngx_http_lua_ffi_shdict_get declared via ffi.cdef in lib/resty/core/shdict.lua); the gain is that LuaJIT traces are not aborted by Lua C API calls, so it is a JIT-versus-interpreter effect rather than JIT code beating AOT C. The README's own caveat: 'If the user Lua code is not JIT compiled, then use of this library may lead to performance drop in interpreted mode.' License text in the README is the two-clause BSD text (SPDX id inferred). No hardware, versions or flags. [retier] The baseline is gone: lua_load_resty_core has been a no-op since ngx_lua v0.10.16, and current ngx_lua exposes shdict, md5, base64 and escape_uri only as ngx_http_lua_ffi_\* functions, so a head-to-head needs ngx_lua 0.10.15 or older. The only numbers found show a slowdown (issue #15: latency 20 ms to 250 ms on OpenResty 1.7.7.2). base.lua requires ngx_lua exactly 0.10.32 while the README says 0.10.25 and dist.ini 0.10.30. JIT versus interpreter, not JIT versus AOT C (off-category).

Requires LuaJIT with FFI and a matching nginx build; replaces parts of the C API, so API coverage differs ('more complete' per README).

## Maintenance

Actively maintained by OpenResty Inc. (759 commits, version 0.1.35 bumped 2026-06-20, last commit 2026-08-24, 855 stars, BSD two-clause) and loaded in production by every OpenResty release; usable only as the copy matched to its ngx_lua release.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now D.
- **Tier reason:** README states the FFI implementation is 'both faster, safer, and more complete than the Lua C API of the ngx_lua module' with no numbers, benchmark code or links; one web search found only qualitative restatements (api7.ai learning-center article, a vendor of an OpenResty-based gateway, snippet only, no timings).
- **Verifier notes:** Tier D confirmed; metadata matches (855 stars, 288 forks, last commit 2026-08-24, BSD two-clause text in README). Kept rather than rejected per wave policy despite tier D under 1k stars. Main shortcomings: no numbers; the FFI API still calls C functions, so the win is trace-compilation of the calling Lua code, not Lua beating C; slower in interpreted mode per its own README; arguably off-category for runtime-jit-beats-aot.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-92 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/openresty/lua-resty-core>
  - <https://github.com/openresty/lua-resty-core/commits>
  - <https://raw.githubusercontent.com/openresty/lua-resty-core/HEAD/README.markdown>
  - <https://raw.githubusercontent.com/openresty/lua-resty-core/HEAD/lib/resty/core/shdict.lua>
- **Sources the enricher read:**
  - <https://github.com/openresty/lua-resty-core>
  - <https://github.com/openresty/lua-resty-core/commits/master>
  - <https://github.com/openresty/lua-resty-core/commit/a60ab0e8ef5a9810216c5b544387059ebf535c0c>
  - <https://github.com/openresty/lua-resty-core/issues?q=is%3Aissue%20slower>
  - <https://github.com/openresty/lua-resty-core/issues?q=is%3Aissue%20performance>
  - <https://github.com/openresty/lua-resty-core/issues/15>
  - <https://raw.githubusercontent.com/openresty/lua-resty-core/HEAD/README.markdown>
  - <https://raw.githubusercontent.com/openresty/lua-resty-core/HEAD/dist.ini>
  - <https://raw.githubusercontent.com/openresty/lua-resty-core/HEAD/Makefile>
  - <https://raw.githubusercontent.com/openresty/lua-resty-core/HEAD/lib/resty/core.lua>
  - <https://raw.githubusercontent.com/openresty/lua-resty-core/HEAD/lib/resty/core/base.lua>
  - <https://raw.githubusercontent.com/openresty/lua-resty-core/HEAD/lib/resty/core/shdict.lua>
  - <https://raw.githubusercontent.com/openresty/lua-resty-core/HEAD/lib/resty/core/regex.lua>
  - <https://raw.githubusercontent.com/openresty/lua-resty-core/HEAD/lib/resty/core/var.lua>
  - <https://raw.githubusercontent.com/openresty/lua-resty-core/HEAD/lib/resty/core/ctx.lua>
  - <https://raw.githubusercontent.com/openresty/lua-resty-core/HEAD/lib/resty/core/request.lua>
  - <https://raw.githubusercontent.com/openresty/lua-resty-core/HEAD/lib/resty/core/utils.lua>
  - <https://raw.githubusercontent.com/openresty/lua-nginx-module/HEAD/README.markdown>
  - <https://raw.githubusercontent.com/openresty/lua-nginx-module/HEAD/src/ngx_http_lua_shdict.c>
  - <https://raw.githubusercontent.com/openresty/lua-nginx-module/HEAD/src/ngx_http_lua_string.c>
  - https://opm.openresty.org/package/openresty/lua-resty-core/ (WebSearch snippet only)
  - https://nginx-extras.getpagespeed.com/lua/core/ (WebSearch snippet only)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/openresty/lua-resty-core`) · [data/wave14/enrich/raw/github_com_openresty_lua_resty_core.json](../../../data/wave14/enrich/raw/github_com_openresty_lua_resty_core.json) (enrichment confidence 0.6)

</details>
