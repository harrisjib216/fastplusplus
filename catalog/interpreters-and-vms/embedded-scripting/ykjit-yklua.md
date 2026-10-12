# yklua (Yk JIT retrofitted into PUC Lua)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier A** (reproducible public benchmark) · Study only · `C (Lua interpreter) with the Rust Yk JIT` · `MIT (PUC-Rio Lua notice in src/lua.h and doc/readme.html); no repository-level LICENSE file covering the Yk additions` · 🟢 active

> PUC-Rio Lua 5.5.0 with the yk meta-tracing JIT bolted on; about 1.96x faster than stock Lua 5.5 on a 22-benchmark geomean.

| | |
|---|---|
| **Beats** | PUC-Rio Lua 5.5.0 (stock lua.org tarball, the version yklua is based on) built with -flto as an LTO baseline |
| **Claimed result** | Geometric mean execution-time ratio yklua/Lua of 0.513 (about 1.95x faster) over 22 benchmarks in the 2026-10-06 11:14 nightly run (index lists 0.504 to 0.519 for the last 10 runs). Per-benchmark mean iteration times from that run's data file (derived from page data): Mandelbrot(500) 370.2 ms vs 63.4 ms (5.84x), BigLoop 3.90x, spectralnorm 3.30x, Heightmap 3.18x, Sieve 3.01x, NBody 2.88x, fannkuchredux 2.33x, Queens 2.15x, Permute 2.08x, Bounce 1.99x, Towers 1.81x, LuLPeg 1.71x, Richards 1.59x, Json 1.52x, knucleotide 1.47x, List 1.37x, CD 1.36x, HashIds 1.35x, binarytrees 1.33x, Storage 1.23x, DeltaBlue 1.11x, Havlak 1.09x; geomean without the in-house BigLoop loop about 1.89x (derived from page data). Laurence Tratt's 2026 blog post reports 'a geometric mean speedup of a little under 2x' with about 400 lines added and under 50 changed in PUC Lua (snippet only); the Mandelbrot 3.2 s to 0.8 s figure in the original record was not found on any page opened. |
| **Workload** | ykjit/yk-benchmarks nightly ReBench suite: 14 Are-We-Fast-Yet Lua benchmarks, 4 Computer Language Benchmarks Game programs (fannkuchredux, spectralnorm, knucleotide, binarytrees), 3 real-world programs (LuLPeg, HashIds, Heightmap) and the in-house BigLoop; 5 process invocations x 10 in-process iterations each, yklua vs stock Lua 5.5.0. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 7F52 16-Core Processor (host bencher14), Debian kernel 6.12.57, recorded in the rebench results file |
| **Compiler and flags** | Baseline: Lua 5.5.0 stock Makefile (gcc -std=gnu99, -O2 in yklua's copy of the same Makefile) with MYCFLAGS=-flto; yklua: ykllvm (yk's LLVM/clang fork) via yk-config release --cflags --cppflags, -O2, -DUSE_YK -DLUA_USE_JUMPTABLE=0 (ykjit/yk-benchmarks common.sh, ykjit/yklua src/Makefile). gcc version not stated. |
| **Adoption** | 7 stars (ykjit/yklua) |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/ykjit/yklua) · [benchmark](https://raw.githubusercontent.com/ykjit/yk-benchmarks/gh-pages/index.html) |

## Verdict

yk's public ReBench harness (ykjit/yk-benchmarks) runs 22 benchmarks (14 AWFY, 4 CLBG, 3 real-world, BigLoop) for 5 invocations of 10 iterations each, on an AMD EPYC 7F52 (Debian, kernel 6.12.57). It compares yklua against stock PUC Lua 5.5.0 built with gcc -O2 -flto. I recomputed the 2026-10-06 14:23 run from its data file: a geomean time ratio of 0.511 (1.96x), with per-benchmark speedups from 1.09x (DeltaBlue) to 5.77x (Mandelbrot). The last 10 nightly runs range from 0.504 to 0.519.

## Use it when

- Loop-heavy numeric Lua on Linux x86-64, where gains are largest: Mandelbrot 5.8x, BigLoop 3.9x, spectralnorm 3.4x, Heightmap 3.1x, Sieve 3.0x and NBody 2.9x against stock Lua 5.5.0.
- You want a JIT while keeping current PUC Lua 5.5 semantics (integers, 5.4/5.5 features) rather than moving to LuaJIT's Lua 5.1 dialect.
- Research or prototyping on meta-tracing: the yk changes are a small set of USE_YK hooks in lvm.c, ldo.c, lparser.c, lfunc.c and lstate.c, so it is a readable worked example of retrofitting a JIT into a C interpreter.
- Long-running scripts where a 1.5-2x average speedup is worth carrying an experimental toolchain (Rust nightly, ykllvm).

## Skip it when

- Production or shipped embeddings. The README says experimental, yk's docs rate it pre-alpha, all.lua is 'currently failing for non-serialised compilation', and 25 issues are open, including per-file test failures since 2023 and a lua_assert failure in luac (#110).
- Any platform other than Linux on x86-64 (a yk requirement), or builds that cannot use Rust nightly and the ykllvm LLVM fork.
- Object-heavy or allocation-heavy code gains little: DeltaBlue 1.09x, Storage 1.23x, Havlak 1.24x, CD 1.35x and binarytrees 1.36x.
- Hosts that load Lua C modules or other code with dlopen at run time. yk's gotchas say it assumes no code is loaded or unloaded at run time, and code without embedded IR cannot be inlined into traces.
- When peak speed matters more than Lua 5.5 compatibility: the author's 2026 blog post says it does not reach LuaJIT's peak performance (search snippet only; tratt.net is blocked here).

## How it is fast

yk is a meta-tracing system. ykllvm embeds the interpreter's own LLVM IR (fat LTO, .llvmbc section) and stackmaps in the binary. A yk_mt_control_point call at the top of luaV_execute counts executions of per-pc YkLocations, which are placed at backward-jump and for-loop heads at parse time and at the entry of functions found to be recursive. Once a location passes YK_HOT_THRESHOLD (131 by default), yk records the interpreter's path through its own IR and compiles that trace. The interpreter is annotated so that traces specialise well: yk_promote on constants, prototype sizes and the pc, yk_idempotent on loads, and yk_unroll on helper loops. Constant-folded traces then remove dispatch, type checks and table lookups, in the same way PyPy's meta-tracing does.

## Compared with alternatives

LuaJIT Remake (Deegen) and Luau target Lua 5.1 or a 5.1-derived dialect, and Pallene compiles a typed subset. yklua is the only catalogued option that JIT-compiles unmodified Lua 5.5, so pick it when you need 5.5 semantics and can accept pre-alpha status. For production embedding, Luau's interpreter or LuaJIT are the mature choices.

## Integration

| | |
|---|---|
| **Form** | source-drop (lua executable and liblua.a built with ykllvm via yk-config) |
| **Dependencies** | yk runtime (Rust ykcapi library, Apache-2.0 or MIT), ykllvm (yk's LLVM fork, a yk submodule) and GNU make |
| **Minimum toolchain** | Rust nightly to build yk, then ykllvm clang via yk-config; Lua itself is built as gnu99 |
| **Platforms** | Linux x86-64 only (yk install docs) |
| **Thread safety** | The same as PUC Lua: one lua_State per thread. yk additionally runs trace compilation on YK_JOBS background threads (num_cpus - 1 by default). |
| **Drop-in for the baseline** | partial. The Lua 5.5.0 language and C API are unchanged, but the interpreter, and ideally the embedding host, must be compiled and linked with yk-config flags (fat LTO, all symbols exported to the dynamic table), and the full Lua test suite does not pass. |

## Gotchas

- Harness caveat on the timing: AWFY's harness.lua measures wall-clock time (os.monotonic), and yk compiles traces on up to num_cpus - 1 background threads (YK_JOBS default) on the 16-core EPYC 7F52. Stock Lua is single-threaded. CPU time is not reported, so the 1.96x is a wall-clock figure that does not charge JIT compilation. The suite also has no yklua executor with the JIT off (YK_JITC=none), so the cost of the yk instrumentation in interpreter mode is not shown.
- The two binaries are built differently. The baseline is gcc -O2 -flto with Lua's computed-goto jump-table dispatch, which lvm.c enables by default under GCC. yklua is ykllvm clang -O2 with -DLUA_USE_JUMPTABLE=0, because yk cannot trace threaded dispatch. Results are correctness-checked: harness.lua asserts each benchmark's verification result. The cbgame inputs are scaled down from the standard sizes (fannkuchredux 10, binarytrees 15), and ReBench runs with --no-denoise.
- Yk locations leak (issue #113, open since 2025-04): luaF_freeproto frees the yklocs array but never calls yk_location_drop. Programs that create functions repeatedly (load, string.dump and undump) therefore accumulate yk location state. The yklocs array is also not counted in luaF_protosize, so the GC does not account for it.
- Warm-up is cheap but steady state is not always better. In the 2026-10-06 14:23 run, no benchmark's first iteration was more than 10% slower than its steady-state mean (iterations 6-10), and most were under 5% slower (DeltaBlue is the worst case, 793 ms against 720 ms). LuLPeg got slower as it ran (787 ms in iteration 1 against 911 ms over iterations 6-10, coefficient of variation 0.18; derived from page data).

## Known shortcomings

- Upgraded C to A on the ykjit/yk-benchmarks gh-pages data (geomean time ratio 0.513, about 1.95x, over 22 benchmarks against stock Lua 5.5.0 -flto on an AMD EPYC 7F52, harness and flags public); the record's Mandelbrot 3.2 s to 0.8 s claim was not found (data shows 5.84x). Experimental, needs the yk toolchain (ykllvm versus gcc), uneven 1.09x-5.84x. No repository LICENSE file (Lua core MIT), so usability is mixed.
- Enricher: recomputed 20261006_142333.data gives geomean 0.511 (1.96x), from 1.09x DeltaBlue to 5.77x Mandelbrot, but the timing is wall clock while yk compiles on YK_JOBS (num_cpus minus 1) background threads against a single-threaded baseline with CPU time unreported; there is no JIT-off executor, the baseline is gcc computed-goto against ykllvm switch dispatch, the location leak #113 is confirmed in code (luaF_freeproto never calls yk_location_drop), LuLPeg slows over its run (787 vs 911 ms), Linux x86-64 only, and the yk docs rate it pre-alpha.

## Caveats and trade-offs

Experimental (README says so) and not drop-in: building needs the yk toolchain (Rust nightly, ykllvm, yk-config). Means include JIT warm-up iterations; gains are uneven (DeltaBlue 1.11x, Havlak 1.09x, Storage 1.23x) and the 5.84x Mandelbrot and 3.90x BigLoop results are loop-heavy microbenchmarks. Baseline and yklua are built by different compilers (gcc -O2 -flto vs ykllvm clang), and yklua disables Lua's jump-table dispatch. Results come from a rolling nightly snapshot on the gh-pages branch (force-pushed each run), so the cited data file may be replaced. Blog figures (under 2x geomean, about 400 lines added, does not reach LuaJIT's peak performance) are snippet only since tratt.net and infoq.com are blocked. No LICENSE file at the repo root: the Lua core carries PUC-Rio's MIT notice but the Yk-specific changes have no stated licence.

Needs the Yk JIT built separately (README); marked experimental; the README says the test suite is currently failing for non-serialised compilation; tracks upstream PUC Lua instead of being stuck at Lua 5.1 like LuaJIT.

## Maintenance

Very active (a run of ltratt PRs merged 2026-10-05) but experimental and pre-alpha with 7 stars. The Lua core carries PUC-Rio's MIT notice and yk is Apache-2.0 or MIT, but the yklua repo has no LICENSE file covering its own changes, so treat it as a research artefact rather than something to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C: the yk team's public benchmark harness (ykjit/yk-benchmarks rebench.conf, common.sh, suites/awfy, suites/cbgame, suites/realworld, suites/yk) runs yklua against stock PUC Lua 5.5.0, the build flags are in common.sh and yklua's src/Makefile, and each published results file records the CPU (AMD EPYC 7F52); the gh-pages summary gives a geomean time ratio of 0.513. Only the gcc version is unpinned.
- **Verifier notes:** Found the real numbers page: ykjit/yk-benchmarks publishes nightly ReBench results (geomean 0.513 time ratio, about 1.95x over 22 benchmarks) with the harness, build script and CPU all public, so this is a reproducible A-tier comparison against stock PUC Lua 5.5.0. The record's Mandelbrot 3.2 s to 0.8 s figure was not found and is replaced by per-benchmark ratios from the data file. Shortcomings: experimental, needs the yk toolchain, uneven gains (1.09x to 5.84x), different compilers for baseline and yklua, no repo licence for the Yk additions (usability mixed), 7 stars.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `license`, `usability`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ykjit/yklua/HEAD/README.md>
  - <https://raw.githubusercontent.com/ykjit/yklua/main/src/lua.h>
  - <https://raw.githubusercontent.com/ykjit/yklua/main/src/Makefile>
  - <https://raw.githubusercontent.com/ykjit/yklua/main/doc/readme.html>
  - <https://github.com/ykjit/yklua>
  - <https://github.com/ykjit/yklua/commits>
  - <https://github.com/orgs/ykjit/repositories>
  - <https://github.com/ykjit/ykbench>
  - <https://github.com/ykjit/yk-benchmarks>
  - <https://raw.githubusercontent.com/ykjit/yk-benchmarks/main/README.md>
  - <https://raw.githubusercontent.com/ykjit/yk-benchmarks/main/rebench.conf>
  - <https://raw.githubusercontent.com/ykjit/yk-benchmarks/main/common.sh>
  - <https://raw.githubusercontent.com/ykjit/yk-benchmarks/main/benchmark.sh>
  - <https://raw.githubusercontent.com/ykjit/yk-benchmarks/main/publish.sh>
  - <https://raw.githubusercontent.com/ykjit/yk-benchmarks/main/setup.sh>
  - <https://raw.githubusercontent.com/ykjit/yk-benchmarks/gh-pages/index.html>
  - <https://raw.githubusercontent.com/ykjit/yk-benchmarks/gh-pages/benchmark-data/20261006_111422.data>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ykjit/yklua/HEAD/README.md>
  - <https://raw.githubusercontent.com/ykjit/yklua/main/src/Makefile>
  - <https://raw.githubusercontent.com/ykjit/yklua/main/src/lvm.c>
  - <https://raw.githubusercontent.com/ykjit/yklua/main/src/ldo.c>
  - <https://raw.githubusercontent.com/ykjit/yklua/main/src/lparser.c>
  - <https://raw.githubusercontent.com/ykjit/yklua/main/src/lfunc.c>
  - <https://raw.githubusercontent.com/ykjit/yklua/main/src/lfunc.h>
  - <https://raw.githubusercontent.com/ykjit/yklua/main/src/lstate.c>
  - <https://raw.githubusercontent.com/ykjit/yklua/main/src/lstate.h>
  - <https://raw.githubusercontent.com/ykjit/yklua/main/src/lobject.h>
  - <https://raw.githubusercontent.com/ykjit/yklua/main/src/lundump.c>
  - <https://raw.githubusercontent.com/ykjit/yklua/main/src/lapi.c>
  - <https://raw.githubusercontent.com/ykjit/yklua/main/src/lua.c>
  - <https://raw.githubusercontent.com/ykjit/yklua/main/src/lua.h>
  - <https://raw.githubusercontent.com/ykjit/yklua/main/src/loslib.c>
  - <https://raw.githubusercontent.com/ykjit/yklua/main/LICENSE>
  - <https://github.com/ykjit/yklua>
  - <https://github.com/ykjit/yklua/tree/main/src>
  - <https://github.com/ykjit/yklua/commits/main>
  - <https://github.com/ykjit/yklua/issues>
  - <https://github.com/ykjit/yklua/issues/113>
  - <https://raw.githubusercontent.com/ykjit/yk-benchmarks/main/README.md>
  - <https://raw.githubusercontent.com/ykjit/yk-benchmarks/main/rebench.conf>
  - <https://raw.githubusercontent.com/ykjit/yk-benchmarks/main/common.sh>
  - <https://raw.githubusercontent.com/ykjit/yk-benchmarks/main/benchmark.sh>
  - <https://raw.githubusercontent.com/ykjit/yk-benchmarks/main/setup.sh>
  - <https://raw.githubusercontent.com/ykjit/yk-benchmarks/main/publish.sh>
  - <https://raw.githubusercontent.com/ykjit/yk-benchmarks/main/patches/clua_gettime>
  - <https://raw.githubusercontent.com/ykjit/yk-benchmarks/main/suites/awfy/Lua/harness.lua>
  - <https://raw.githubusercontent.com/ykjit/yk-benchmarks/gh-pages/index.html>
  - <https://raw.githubusercontent.com/ykjit/yk-benchmarks/gh-pages/benchmark-data/20261006_142333.data>
  - <https://raw.githubusercontent.com/ykjit/yk/master/README.md>
  - <https://raw.githubusercontent.com/ykjit/yk/master/COPYRIGHT>
  - <https://raw.githubusercontent.com/ykjit/yk/master/LICENSE-MIT>
  - <https://raw.githubusercontent.com/ykjit/yk/master/LICENSE-APACHE>
  - <https://github.com/ykjit/yk/tree/master/docs/src>
  - <https://raw.githubusercontent.com/ykjit/yk/master/docs/src/SUMMARY.md>
  - <https://raw.githubusercontent.com/ykjit/yk/master/docs/src/intro.md>
  - <https://raw.githubusercontent.com/ykjit/yk/master/docs/src/user/install.md>
  - <https://raw.githubusercontent.com/ykjit/yk/master/docs/src/user/interps.md>
  - <https://raw.githubusercontent.com/ykjit/yk/master/docs/src/dev/runtime_config.md>
  - <https://raw.githubusercontent.com/ykjit/yk/master/docs/src/dev/gotchas.md>
  - <https://raw.githubusercontent.com/ykjit/yk/master/docs/src/dev/build_config.md>
  - WebSearch snippet: https://tratt.net/laurie/blog/2026/retrofitting_jit_compilers_into_c_interpreters.html (page blocked; snippet only)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/ykjit/yklua`) · [data/wave12/enrich/raw/github_com_ykjit_yklua.json](../../../data/wave12/enrich/raw/github_com_ykjit_yklua.json) (enrichment confidence 0.7)

</details>
