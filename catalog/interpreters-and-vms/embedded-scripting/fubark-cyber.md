# Cyber

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig` · `MIT` · 🟡 stale

> Embeddable scripting language in Zig with a C API; its 0.3 VM beat Lua and LuaJIT's interpreter on call and fiber microbenchmarks.

| | |
|---|---|
| **Beats** | Lua (PUC-Rio), LuaJIT and QuickJS (also Janet on the fiber test) |
| **Claimed result** | Per WebSearch snippets of cyberscript.dev/performance.html (snippet only): recursive fib (VM) Cyber 19 ms, LuaJIT 21 ms, Luau 34 ms, Lua 39 ms, QuickJS 57 ms (about 2x faster than Lua, derived from page data); fib (JIT) Cyber 5 ms and LuaJIT 5 ms; fiber benchmark Cyber 2.77 +/- 0.28x faster than LuaJIT, 6.28 +/- 0.61x faster than Janet and 8.01 +/- 0.79x faster than Lua; range/iterator (VM) Luau 10 ms, LuaJIT 11 ms, Cyber 12 ms, Lua 27 ms (Cyber slower than Luau and LuaJIT there). The search record's QuickJS 78 ms range figure did not reappear in the snippets this verifier saw. |
| **Workload** | Recursive Fibonacci, range/iterator loops and a fiber (coroutine) benchmark in VM mode and JIT mode, from the project's performance page. |
| **Metric** | throughput |
| **Adoption** | 1.5k stars |
| **Last commit** | 2025-12-21 |
| **Links** | [repository](https://github.com/fubark/cyber) · [benchmark](https://cyberscript.dev/performance.html) |

## Verdict

Cyber's own performance page (seen only through search snippets) timed script bodies on a MacBook Pro M2 against Lua, LuaJIT, Luau and QuickJS (versions and build flags not seen). Cyber 0.3's VM ran recursive fib(30) in 19 ms versus LuaJIT 21 ms, Luau 34 ms, Lua 39 ms and QuickJS 57 ms, and its JIT tied LuaJIT at 5 ms. A 100,000-coroutine test was about 2.8x faster than LuaJIT and 8x faster than Lua, but a 1,000,000-element range/iterator loop trailed Luau and LuaJIT.

## Use it when

- A C or C++ host (game, tool, engine) that wants a small embedded scripting language with a plain C API and custom allocator hook, and can adopt a non-Lua language.
- Scripts that create and resume many coroutines: on the 100,000-fiber create-and-resume test the page reported Cyber about 2.8x faster than LuaJIT and 8x faster than Lua (0.3-era, snippet only).
- Call-heavy script logic: recursive fib(30) took 19 ms in Cyber's 0.3 VM versus 39 ms for Lua and 57 ms for QuickJS on an Apple M2.
- Projects that want static types and deterministic reference-counted deinitialization in a scripting language rather than a tracing GC.

## Skip it when

- You need a stable language or API: the last stable release is 0.3 (December 2023), 0.4-dev has been a pre-release since November 2024, syntax changed since 0.3 (the master libcyber example uses `a := 1`), and there are no commits since 2025-12-21.
- Array or range loops: on the page's range/iterator test Cyber (12 ms) trailed Luau (10 ms) and LuaJIT (11 ms).
- You need a production JIT: the master docs call it 'incomplete and unstable', x64 stencils were still being added in December 2025, and issue #111 (January 2026) asking whether the JIT works on ARM has no answer.
- Existing Lua code or tooling must keep working: Cyber is not Lua-compatible, so Luau, LuaJIT or a Lua-compatible VM is the natural choice.
- Programs that build cyclic object graphs: in safe mode a reference cycle is a runtime error that panics the thread at its end, not something a collector cleans up.

## How it is fast

In 0.3 values were NaN-tagged 64-bit words in a register-based bytecode VM, and memory was managed by reference counting with a cycle detector instead of a tracing GC. The JIT uses copy-and-patch: machine-code stencils are pregenerated from C with clang's musttail (so every stencil maps operands to the same registers), and a small assembler fills the holes. That lets the JIT work on arm64 too, and JIT compilation is mostly memcpy. The benchmark's fib.cy declares `n int`, so type information is available to the compiler; how much of the fib gain that explains is not documented.

## Compared with alternatives

Pick Cyber over Luau or LuaJIT only if you want its typed language, fast fibers and a C API from a Zig-built library, and can live with an unreleased, idle 0.4-dev. For proven embedding Luau or LuaJIT win, and for a statically typed embedded language with independent multi-kernel numbers, Daslang is the stronger pick.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (libcyber via `zig build lib`) plus a CLI |
| **Dependencies** | Zig toolchain to build; host side links libcyber and includes src/include/cyber.h (extern "C" guarded); malloc by default, mimalloc optional; JIT stencils are pregenerated with libLLVM; the CLI bundles tinyc for the in-progress C backend |
| **Minimum toolchain** | Zig 0.15.2 for master (docs/build.md, ReleaseSafe recommended); any C or C++ compiler for the host |
| **Platforms** | Linux x64, macOS x64 and arm64, Windows x64, WASM (web and WASI); 0.3 JIT numbers were taken on an Apple M2, and x64 JIT stencils were added in December 2025 |
| **Thread safety** | Not documented; each CLVM owns its allocator and green-thread (CLThread) handles, so treat one VM as single-threaded |
| **Drop-in for the baseline** | no |

## Gotchas

- The published numbers are for the 0.3-era engine on a MacBook Pro M2 (seen only in search snippets; cyberscript.dev is blocked here). The benchmark scripts exist only at tag 0.3, since test/bench was removed from master, and they use 0.3 syntax that master's reworked, statically typed language no longer accepts.
- Harness flaws in test/bench at 0.3: each script times itself with a different clock (Lua and Luau use os.clock(), which is CPU time; Cyber uses os.now(); JS uses Date.now() with 1 ms resolution), and startup and compilation are excluded. fib.cy declares `n int` while the Lua and JS versions are untyped.
- The range/iterator Lua and Luau scripts fill the table from index 0, so key 0 lands in the hash part, and walk it with pairs() rather than a numeric loop. Cyber and JS use plain list iteration. That handicaps the baselines, yet Cyber still trailed Luau and LuaJIT on that test.
- The Janet fiber ratio has no Janet source at tag 0.3, and the LuaJIT settings for the 'VM' rows (presumably -joff) and all runtime versions and build flags were not visible.

## Known shortcomings

- Numbers come from the 0.3-era engine via WebSearch snippets (cyberscript.dev blocked here); the benchmark code is gone from master and present only at tag 0.3 test/bench, with no Janet source file. No hardware or flags; Luau and LuaJIT beat Cyber on the range/iterator benchmark.
- Enricher: 0.3-era numbers on a MacBook Pro M2 (snippet). The 0.3 test/bench harness mixes timers (Lua and Luau os.clock CPU time, Cyber os.now, JavaScript Date.now at 1 ms), the Lua and Luau for-loop fills from index 0 and walks with pairs(), which handicaps the baselines, yet Cyber still trailed; the Janet source is missing and LuaJIT VM-mode flags unseen. master is now statically typed (the record said dynamic), the last commit is 2025-12-21 (about 9 months idle, so stale rather than active), master docs call the JIT 'incomplete and unstable', and issue #111 on the ARM JIT is unanswered.

## Caveats and trade-offs

Snippet only: cyberscript.dev is blocked here, so hardware, compiler flags and the Lua, LuaJIT, Luau, QuickJS and Janet versions were not seen. The benchmark sources the examples/README links (test/bench) were removed from master, but they exist at tag 0.3 (Dec 2023): test/bench/fib, fiber, for, heap and string with .cy, .lua, .luau and .js versions (fib also C, Go, Java and others); the 0.3 fiber directory has no Janet file, so the Janet comparison was run on code not present at that tag. The last numbered release is 0.3 (Dec 2023); master has been heavily reworked since, so the published numbers probably describe the 0.3-era VM and JIT rather than current master. First-party; the page itself says the JIT was recent and has few benchmarks. Cyber is behind LuaJIT and Luau on the range/iterator test. [retier] Numbers are 0.3-era (MacBook Pro M2, snippet only, cyberscript.dev blocked) from a harness with mixed timers and a Lua/Luau port that handicaps the baselines; the benchmark code is gone from master and present only at tag 0.3 test/bench with no Janet source. Luau and LuaJIT beat Cyber on range/iterator. master is now statically typed, last commit 2025-12-21, JIT 'incomplete and unstable' per its own docs, ARM JIT issue #111 unanswered.

Written in Zig and built with the Zig toolchain; embeddable through a C API (libcyber, see examples/libcyber in the repo), so usable from C++ via C, but the language itself is new, dynamically typed and not Lua-compatible. A stencil-based JIT was still being written in December 2025 (x64 stencils, refactored JIT backend) and the language has been reworked repeatedly, so benchmark numbers may not match current master.

## Maintenance

MIT-licensed and builds with Zig 0.15.2, but there are no commits since 2025-12-21 (over nine months idle as of 2026-10-06, so 'active' overstates it), the last stable release is 0.3 from December 2023 and the language has been redesigned since; treat it as experimental.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party numbers on cyberscript.dev/performance.html (blocked here; content seen only through WebSearch snippets) compare Cyber with Lua, LuaJIT, Luau and QuickJS. Benchmark sources exist at tag 0.3 (test/bench), but hardware, compiler flags and the versions of the other runtimes were not seen, so the record cannot reach A.
- **Verifier notes:** Fib and fiber numbers confirmed through two WebSearch snippets of the blocked performance page. Benchmark code is at https://github.com/fubark/cyber/tree/0.3/test/bench, not on master. The numbers are for the 0.3-era engine and the Janet comparison has no matching source file at that tag. Metadata (MIT, 1.5k stars, last commit 2025-12-21, active, not a fork) checked on github.com.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`, `maintenance_status`
- **Shortcomings recorded by:** current-engine measurement with stated hardware; current-engine run with one timer
- **Pages the verifier opened:**
  - <https://github.com/fubark/cyber>
  - <https://raw.githubusercontent.com/fubark/cyber/HEAD/README.md>
  - <https://github.com/fubark/cyber/commits/master>
  - <https://cyberscript.dev/performance.html>
  - <https://github.com/fubark/cyber/tree/master/examples>
  - <https://github.com/fubark/cyber/tags>
  - <https://github.com/fubark/cyber/tree/v0.3/test/bench>
  - <https://github.com/fubark/cyber/tree/0.3/test/bench>
  - <https://github.com/fubark/cyber/tree/0.3/test/bench/fib>
  - <https://github.com/fubark/cyber/tree/0.3/test/bench/fiber>
- **Sources the enricher read:**
  - <https://github.com/fubark/cyber>
  - <https://github.com/fubark/cyber/commits/master>
  - <https://github.com/fubark/cyber/issues>
  - <https://github.com/fubark/cyber/issues/111>
  - <https://github.com/fubark/cyber/releases>
  - <https://github.com/fubark/cyber/tree/master/examples>
  - <https://github.com/fubark/cyber/tree/master/examples/libcyber>
  - <https://github.com/fubark/cyber/blob/master/docs/build.md>
  - <https://raw.githubusercontent.com/fubark/cyber/HEAD/README.md>
  - <https://raw.githubusercontent.com/fubark/cyber/0.3/README.md>
  - <https://raw.githubusercontent.com/fubark/cyber/HEAD/docs/docs.md>
  - <https://raw.githubusercontent.com/fubark/cyber/HEAD/src/include/cyber.h>
  - <https://raw.githubusercontent.com/fubark/cyber/HEAD/examples/libcyber/main.c>
  - <https://raw.githubusercontent.com/fubark/cyber/0.3/src/value.zig>
  - <https://raw.githubusercontent.com/fubark/cyber/0.3/src/vm.zig>
  - <https://raw.githubusercontent.com/fubark/cyber/0.3/test/bench/fib/fib.cy>
  - <https://raw.githubusercontent.com/fubark/cyber/0.3/test/bench/fib/fib.lua>
  - <https://raw.githubusercontent.com/fubark/cyber/0.3/test/bench/fib/fib.luau>
  - <https://raw.githubusercontent.com/fubark/cyber/0.3/test/bench/fib/fib.js>
  - <https://raw.githubusercontent.com/fubark/cyber/0.3/test/bench/fiber/fiber.cy>
  - <https://raw.githubusercontent.com/fubark/cyber/0.3/test/bench/fiber/fiber.lua>
  - <https://raw.githubusercontent.com/fubark/cyber/0.3/test/bench/for/for.cy>
  - <https://raw.githubusercontent.com/fubark/cyber/0.3/test/bench/for/for.lua>
  - <https://raw.githubusercontent.com/fubark/cyber/0.3/test/bench/for/for.luau>
  - <https://raw.githubusercontent.com/fubark/cyber/0.3/test/bench/for/for.js>
  - https://cyberscript.dev/performance.html (EGRESS_BLOCKED; content from WebSearch snippets)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/fubark/cyber`) · [data/wave12/enrich/raw/github_com_fubark_cyber.json](../../../data/wave12/enrich/raw/github_com_fubark_cyber.json) (enrichment confidence 0.55)

</details>
