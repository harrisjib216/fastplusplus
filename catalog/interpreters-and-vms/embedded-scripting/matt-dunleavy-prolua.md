# Prolua

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig` · `MIT` · 🟢 active

> Lua 5.4 reimplemented in Zig: roughly at parity with PUC Lua 5.4.8, faster on sort and numeric loops, slower on strings.

| | |
|---|---|
| **Beats** | Lua 5.4.8 (reference C interpreter) |
| **Claimed result** | Between 0.60x and 1.19x of the C interpreter's time: faster on sort (0.250 s vs 0.418 s, 0.60x), loops (0.375 s vs 0.521 s, 0.72x), coroutines (0.158 s vs 0.192 s, 0.82x) and nbody (0.612 s vs 0.686 s, 0.89x); parity (1.00-1.03x) on binarytrees, closures, fannkuch, fib, tables; slower on json (1.15x), spectralnorm (1.19x) and strings (1.19x). |
| **Workload** | Twelve scripts in test/bench (binarytrees, closures, coroutines, fannkuch, fib, json, loops, nbody, sort, spectralnorm, strings, tables), each timed as a whole process by src/cli/bench.zig (wall clock, best of three runs, child stdout discarded, non-zero exit fails the run), prolua run vs the reference lua found on PATH, measured 2026-09-12 on Linux. |
| **Metric** | throughput |
| **Compiler and flags** | Zig 0.16.0, zig build bench -Doptimize=ReleaseFast (runs prolua bench --dir test/bench); the measured 'installed' Lua 5.4.8 build is not described in the Performance section. CI (.github/workflows/ci.yml) builds the reference from the lua.org 5.4.8 tarball with 'make linux' (upstream Makefile defaults), and the README notes Ubuntu ships only 5.4.6, so a tarball build is likely but not stated for the benchmark run. |
| **Adoption** | 3 stars |
| **Last commit** | 2026-09-16 |
| **Links** | [repository](https://github.com/matt-dunleavy/prolua) · [benchmark](https://github.com/matt-dunleavy/prolua) |

## Verdict

The README's 2026-09-12 table, produced by the repo's own `prolua bench` harness (whole process, best of 3 wall-clock runs, Zig 0.16.0 ReleaseFast for the host CPU, Linux, CPU model not stated), times the twelve test/bench scripts against an installed Lua 5.4.8 whose build flags are not stated. Prolua takes 0.60-0.89x of the C interpreter's time on sort, loops, coroutines and nbody, 1.00-1.03x on five more and 1.15-1.19x on json, spectralnorm and strings (geometric mean about 0.95x, derived from page data).

## Use it when

- You are writing a Zig application and want a full Lua 5.4 in pure Zig (only libc linked) with the reference's exact semantics, error messages and both collector modes.
- Scripts dominated by table.sort on plain arrays (0.250 s vs 0.418 s), integer/float loops (0.375 s vs 0.521 s), coroutine round trips (0.158 s vs 0.192 s) or n-body-style float maths (0.612 s vs 0.686 s), where the README table shows 1.1-1.7x gains (derived from page data).
- You want Lua plus a built-in project and dependency tool (init, add, vendor, module.sum content hashes) in one binary.
- As a single-binary Lua 5.4 drop-in for running existing scripts where speed at parity with PUC Lua is enough (geometric mean 0.95x of the C interpreter's time over the twelve scripts, derived from page data).

## Skip it when

- C or C++ hosts that link liblua: there is no C ABI (embedding.md: C code needs a Zig shim) and no custom lua_Alloc hook.
- String-heavy or JSON-style workloads: strings (0.247 s vs 0.208 s), json (0.521 s vs 0.455 s) and spectralnorm (0.517 s vs 0.435 s) run 1.15-1.19x slower than PUC Lua.
- Code doing 64-bit integer arithmetic (hashes, bit manipulation, PRNGs, large counters): integers outside the 48-bit inline range are heap-allocated BoxedInt objects owned by the collector (vm.zig intResult), a cost no bench script exercises.
- Any production use: the README calls it a very early release that may break without notice; the repo has three commits (all 2026-09-16), 3 stars and no issue history.
- When you need more speed than PUC Lua rather than parity: in the catalogue's sibling entries Luau (about 1.5x PUC Lua 5.5.1), yklua (about 1.95x PUC Lua 5.5.0) and LuaJIT Remake (185% faster than PUC Lua 5.1) are well ahead of both.

## How it is fast

Values are one-word (8-byte) NaN boxes, which value.zig notes diverges from the official tagged representation; hash nodes stay 24 bytes like Lua's Node. The interpreter mirrors lvm.c, and every opcode arm ends with Zig's labeled-switch `continue :vm`, which gives the same per-arm indirect-jump threading that PUC Lua gets from computed gotos (ljumptab.h). The biggest win, sort (1.67x), comes from the library: table.sort keeps Lua's quicksort but, for a plain table whose elements are all in the array part, reads and swaps array slots directly instead of going through lua_geti/lua_seti on the stack, and compares two integers inline when there is no comparator. table.concat has a similar direct array-part path.

## Compared with alternatives

Pick Prolua over PUC Lua or Luau when you want exact Lua 5.4 semantics inside a Zig program with no C toolchain; for raw speed Luau (about 1.5x PUC Lua on dasProfile) and yklua (about 1.95x PUC Lua 5.5 geomean) are much faster, and Lua-CSharp or sol2/LuaBridge3 are the picks for .NET or C++ hosts.

## Integration

| | |
|---|---|
| **Form** | Zig package (zig fetch --save; b.dependency("prolua")) plus a standalone CLI binary |
| **Dependencies** | libc only |
| **Minimum toolchain** | Zig 0.16.0 (minimum_zig_version in build.zig.zon); Debug builds cannot compile its tail calls, so measure or ship ReleaseFast/ReleaseSafe |
| **Platforms** | Linux (all suites in CI), macOS (unit, differential and CLI suites), Windows (build, unit tests, smoke run; Ctrl-C and io.popen untested); cross-compiles to x86_64-windows-gnu, aarch64-macos, x86_64-linux-musl and aarch64-linux-gnu |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — the Lua 5.4 language and standard library are matched byte for byte against 5.4.8, so scripts run unchanged; the embedding API is Zig-only, not the C API/ABI |

## Gotchas

- Build asymmetry in the benchmark: build.zig calls b.standardTargetOptions(.{}) with no default, so `zig build bench -Doptimize=ReleaseFast` compiles Prolua for the native host CPU with all its extensions, while the reference lua (installed build, flags unstated; CI builds it with upstream `make linux`) is a generic x86-64 build. The CPU model is not given either.
- Harness: src/cli/bench.zig times whole processes (best of 3, start-up included; fib totals only about 0.055 s), discards stdout and checks only the exit status, so the bench outputs are never compared. Correctness rests on the separate differential and official suites instead. sort.lua is seeded (math.randomseed(42)) and mathlib.zig implements the same xoshiro256\*\* generator as 5.4, so both interpreters sort the same input if the generator matches.
- Integers that do not fit 48 bits are boxed on the heap (ValueType.boxint), unlike PUC Lua's unboxed 64-bit integers, so integer-heavy code can allocate per arithmetic result.
- Licence metadata conflicts: LICENSE, the README and the source headers say MIT, but NOTICE says 'Licensed under the Apache License 2.0'. The README also links docs/architecture.md, which is not in the repo (only docs/embedding.md is).

## Known shortcomings

- Mixed result: faster on 4 of 12 scripts, 1.15-1.19x slower on 3 and tied on 5; no CPU model, the reference Lua build flags are unstated for the measured run, startup is included, 3-star repo from 2026-09-16. Zig.
- Enricher: Prolua is built for the native CPU (standardTargetOptions) against a generic reference lua, bench output is discarded with only the exit status checked, integers over 48 bits are heap-boxed (no bench exercises that), and the sort win (0.60x) comes from a table.sort fast path touching the array part directly rather than from the VM. Licence conflict (LICENSE, README and headers MIT, NOTICE Apache-2.0); docs/architecture.md is a 404; no C ABI.

## Caveats and trade-offs

Mixed result, not a uniform speed-up: faster on 4 of 12 scripts (sort 0.60x, loops 0.72x, coroutines 0.82x, nbody 0.89x), within 3% on 5, slower on 3 (json 1.15x, spectralnorm 1.19x, strings 1.19x). Whole-process times include interpreter start-up (fib runs only about 0.055 s). CPU model not given (only 'Linux'); the benchmarked reference Lua's build flags are not stated (CI builds it from the tarball with upstream defaults). The bench harness discards output and does not compare it, although the separate differential suite (55 scripts) and the official Lua 5.4.8 suite check semantics byte for byte. README calls it 'a very early release' not for production; repository created 2026-09-16 with three commits, 3 stars.

Lua 5.4 reimplementation in Zig with 8-byte NaN-boxed values and 24-byte table nodes; passes the official Lua 5.4.8 suite (30 of 30 runnable files) and byte-for-byte differential tests. Zig package API mirrors the C API shape but is not the C ABI, so existing C hosts cannot link it as liblua.

## Maintenance

Brand new (three commits on 2026-09-16, 3 stars, no issues, README calls it a very early release) but MIT-licensed per LICENSE, pure Zig with only libc, and heavily tested against the reference, so worth trying for Zig hosts and not for C/C++ hosts or production.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table (Performance section) times the twelve test/bench scripts under prolua and the installed Lua 5.4.8 with the public harness src/cli/bench.zig (whole process, best of 3, stdout ignored) and states Zig 0.16.0 ReleaseFast, but gives no CPU model and no build flags for the reference lua, so not A; no independent or peer-reviewed measurement, so not B.
- **Verifier notes:** README Performance table matches the record's numbers exactly; bench harness src/cli/bench.zig is a straightforward best-of-3 wall-clock runner against lua on PATH. Shortcomings to record: mixed result (wins 4 of 12, loses 3), no CPU model, reference Lua build flags unstated for the measured run, start-up included, very new 3-star repo.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/matt-dunleavy/prolua>
  - <https://github.com/matt-dunleavy/prolua/commits/main>
  - <https://github.com/matt-dunleavy/prolua/tree/main/test/bench>
  - <https://github.com/matt-dunleavy/prolua/tree/main/src/cli>
  - <https://raw.githubusercontent.com/matt-dunleavy/prolua/HEAD/README.md>
  - <https://raw.githubusercontent.com/matt-dunleavy/prolua/HEAD/build.zig>
  - <https://raw.githubusercontent.com/matt-dunleavy/prolua/HEAD/src/cli/bench.zig>
  - <https://raw.githubusercontent.com/matt-dunleavy/prolua/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/matt-dunleavy/prolua/HEAD/test/bench/sort.lua>
  - <https://raw.githubusercontent.com/matt-dunleavy/prolua/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/matt-dunleavy/prolua>
  - <https://raw.githubusercontent.com/matt-dunleavy/prolua/HEAD/README.md>
  - <https://raw.githubusercontent.com/matt-dunleavy/prolua/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/matt-dunleavy/prolua/HEAD/NOTICE>
  - <https://raw.githubusercontent.com/matt-dunleavy/prolua/HEAD/build.zig>
  - <https://raw.githubusercontent.com/matt-dunleavy/prolua/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/matt-dunleavy/prolua/HEAD/src/cli/bench.zig>
  - <https://raw.githubusercontent.com/matt-dunleavy/prolua/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/matt-dunleavy/prolua/HEAD/test/bench/sort.lua>
  - <https://raw.githubusercontent.com/matt-dunleavy/prolua/HEAD/test/bench/loops.lua>
  - <https://raw.githubusercontent.com/matt-dunleavy/prolua/HEAD/test/bench/coroutines.lua>
  - <https://raw.githubusercontent.com/matt-dunleavy/prolua/HEAD/test/bench/nbody.lua>
  - <https://raw.githubusercontent.com/matt-dunleavy/prolua/HEAD/test/bench/fib.lua>
  - <https://raw.githubusercontent.com/matt-dunleavy/prolua/HEAD/test/bench/strings.lua>
  - <https://raw.githubusercontent.com/matt-dunleavy/prolua/HEAD/src/vm.zig>
  - <https://raw.githubusercontent.com/matt-dunleavy/prolua/HEAD/src/value.zig>
  - <https://raw.githubusercontent.com/matt-dunleavy/prolua/HEAD/src/table.zig>
  - <https://raw.githubusercontent.com/matt-dunleavy/prolua/HEAD/src/lib/tablelib.zig>
  - <https://raw.githubusercontent.com/matt-dunleavy/prolua/HEAD/src/lib/mathlib.zig>
  - <https://raw.githubusercontent.com/matt-dunleavy/prolua/HEAD/docs/embedding.md>
  - <https://raw.githubusercontent.com/matt-dunleavy/prolua/HEAD/docs/architecture.md>
  - <https://github.com/matt-dunleavy/prolua/tree/main/src>
  - <https://github.com/matt-dunleavy/prolua/tree/main/src/lib>
  - <https://github.com/matt-dunleavy/prolua/tree/main/docs>
  - <https://github.com/matt-dunleavy/prolua/commits/main>
  - <https://github.com/matt-dunleavy/prolua/issues?q=is%3Aissue>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/matt-dunleavy/prolua`) · [data/wave12/enrich/raw/github_com_matt_dunleavy_prolua.json](../../../data/wave12/enrich/raw/github_com_matt_dunleavy_prolua.json) (enrichment confidence 0.75)

</details>
