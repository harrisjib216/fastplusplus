# Wangshu (望舒)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Go` · `Apache-2.0` · 🟢 active

> Pure-Go embeddable Lua 5.1 VM with NaN-boxing, a Wasm tier and a native method JIT; 2-18x faster than gopher-lua on numeric scripts.

| | |
|---|---|
| **Beats** | gopher-lua (Go implementation of Lua 5.1); no direct PUC Lua or LuaJIT column in the README table |
| **Claimed result** | Linux/amd64 ratios over gopher-lua v1.1.2 (gopher time / Wangshu time): P4 method JIT in production 'auto' mode 18.0x HeavyArith, 17.7x HeavyFloatloop, 15.0x spectral-norm, 14.5x n-body, 9.35x fib, 7.51x fannkuch, 4.80x HeavyRecursion, 1.89x binary-trees; the non-production 'force' mode reaches 18.5x, 18.0x, 15.4x, 14.7x, 9.10x, 7.87x, 4.93x and 1.78x. The P1 interpreter is 1.27-5.54x faster on the micro, heavy and most small-program rows but slower on fib (0.87x) and fannkuch (0.77x). On the Go-to-Lua embedding rows Wangshu is slower than gopher-lua with the allocating Call API (CallOnly 0.41-0.47x, Boundary 0.56-0.64x, Predicate/Transform x1000 0.86-1.03x) and up to 1.52x faster only with the zero-alloc CallInto API. arm64 Cobalt 100 P4 peaks are 13.7x (HeavyArith) and 14.1x (HeavyFloatloop); macOS arm64 11.3x. |
| **Workload** | Pure-VM micro benchmarks, three heavy numeric kernels, five Benchmarks Game scripts (fib, binary-trees, spectral-norm, fannkuch, n-body) and Go-to-Lua boundary call and batch-transform workloads, on GitHub Actions runners. |
| **Metric** | throughput |
| **Hardware** | GitHub Actions hosted runners: Intel Xeon Platinum 8573C (linux/amd64), Azure Cobalt 100 Neoverse-N2 (linux/arm64), Apple M-series (macos-latest) |
| **Compiler and flags** | Go 1.27.0 (go.mod go directive, installed by actions/setup-go go-version-file); go test -run='^\$' -bench=&lt;tier pattern&gt; -benchtime=2s -count=3 -cpu=1, median of 3; tiers selected by build tags (P1 default, P3/P4 tagged); script scripts/bench-readme-table.sh, workflow bench-readme-table (run 29098511106, 2026-07-10). |
| **Adoption** | 8 stars; the README says it runs in production at the author's employer |
| **Last commit** | 2026-10-04 |
| **Links** | [repository](https://github.com/Liam0205/wangshu) · [benchmark](https://github.com/Liam0205/wangshu) |

## Verdict

In one GitHub Actions round (2026-07-10, Go 1.27.0, go test -benchtime=2s -count=3 -cpu=1, median), on an Intel Xeon Platinum 8573C runner the P4 method JIT in production auto mode was 18.0x faster than gopher-lua v1.1.2 on HeavyArith, 17.7x on HeavyFloatloop, 14.5-15.0x on n-body and spectral-norm, 9.35x on fib(24) and 1.89x on binary-trees, with smaller peaks on Azure Cobalt 100 (up to 14.2x) and macOS arm64 (up to 11.3x). gopher-lua is the only timing baseline; PUC Lua 5.1.5 is used only as the correctness oracle.

## Use it when

- Go services embedding Lua whose scripts are numeric loops or recursive kernels (rule engines, feature transforms, simulations) and that can enable the P4 build tags on linux or darwin amd64/arm64.
- Batch processing where the host can pass whole columns through the arena and keep the loop inside Lua (one Program.Call per batch) rather than calling Lua per item.
- Pure-Go, cgo-free builds that need cross-compilation and must not link C Lua or LuaJIT.
- When byte-for-byte Lua 5.1.5 output parity matters: the project gates CI on differential tests against the official 5.1.5 binary and runs nightly differential fuzzing.

## Skip it when

- Per-item Go-to-Lua calls with the allocating Call API: CallOnly runs at 0.41-0.47x of gopher-lua's speed on amd64 and the batch Predicate/Transform rows are 0.86-1.03x; only the zero-alloc CallInto path wins (up to 1.52x).
- Call-heavy or table-shuffling scripts on the default P1 build: fib is 0.87x and fannkuch 0.77x of gopher-lua without the JIT tier.
- Hosts that need Lua 5.2+ features, io.open/popen, require/module/package, string.dump, getfenv/setfenv or most of the debug library; all are listed exemptions.
- Locked-down deployments (strict seccomp, SELinux deny_execmem, PaX MPROTECT) or platforms other than linux/darwin amd64/arm64: P4 cannot map executable pages and silently stays on the interpreter.
- When you need LuaJIT-class speed: no Wangshu-versus-LuaJIT or PUC Lua timings are published, although a comparison harness exists (scripts/bench-vs-luajit.sh).

## How it is fast

Values are NaN-boxed 64-bit words in a self-managed arena instead of gopher-lua's interface-boxed values with switch dispatch, which gives the P1 interpreter its 1.3-5.5x. With the wangshu_p4 and wangshu_profile tags, protos that cross a heat threshold (200 entries, plus back-edge sampling) and pass shape checks are compiled to machine code in W^X mmap pages, with byte-level templates for FORLOOP, inline-cached table access (ArrayHit/NodeHit), direct segment-to-segment calls for self-recursion, self-tail-call loops and inline SQRTSD/FSQRT-style math intrinsics; generated code runs on its own spill stack with preemption checks at back edges to coexist with the Go runtime.

## Compared with alternatives

Pick Wangshu over LuaJIT when the host is Go and cgo is ruled out; when cgo is acceptable, LuaJIT (and LuaAOT for ahead-of-time Lua 5.4) remain the speed references, since Wangshu publishes no numbers against either. Among pure-Go options, Apogee (catalogued under JITs, a Lua 5.5 VM measured against C Lua and LuaJIT) is the alternative if you need 5.x semantics beyond 5.1.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none for the default P1 build (pure Go, no cgo); P3 uses github.com/tetratelabs/wazero v1.12.0; golang.org/x/sys v0.44.0 is listed as indirect |
| **Minimum toolchain** | Go 1.27.0 (go.mod go directive; older toolchains refuse to build) |
| **Platforms** | linux/amd64, linux/arm64, darwin/arm64 tested; P4 JIT only on linux/darwin amd64 and arm64 with executable mmap allowed; other GOOS/GOARCH compile via pure-Go stubs but are not exercised |
| **Thread safety** | Program is immutable and shareable across States; each goroutine needs its own State (States are not shared across goroutines, so the tier on/off switch is per State). |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness note: the P4 cells in the pure-VM micro rows (Simple, Arith, Loop) are not JIT code; scripts/bench-readme-table.sh runs the plain _Wangshu benchmark under the P4 build because a vararg top-level chunk never promotes, so those cells are the interpreter with profiling hooks. The gopher-lua denominator is also measured only in the earlier P1 go test pass, not interleaved with the P3/P4 passes on the same shared runner.
- The timed benchmark loops check only for errors, not results; correctness of the benchmarked scripts relies on separate oracle tests (TestRealWorld_OracleParity skips when lua5.1 is not installed) and the CI differential and fuzz jobs.
- Promotion needs both build tags (wangshu_p4 wangshu_profile); without wangshu_profile, heat sampling is compiled out and a 'P4' build runs the interpreter. Check TierStatsSnapshot().Promoted &gt; 0 and alert on StuckCompileFailed.
- Open bugs as of 2026-10-04: a script that allocates only through host functions never triggers GC (#297), and arena capacity only grows under large-block churn (#296); each promoted proto also costs a 64 KiB spill stack plus code pages.

## Known shortcomings

- GitHub-runner CI tables against gopher-lua v1.1.2 only (no PUC Lua or LuaJIT timing): the headline peaks come from the non-production force mode (auto mode 17.7-18.0x), the Go-to-Lua call-boundary rows are slower than gopher-lua (0.41-0.64x), 8 stars. Go, not C++; off-baseline.
- Enricher: the P4 cells in the micro rows (Simple, Arith, Loop) are the interpreter, not the JIT (bench-readme-table.sh runs _Wangshu under the P4 build); gopher-lua is timed only in the P1 go test pass, not interleaved with the P3 and P4 passes; the timed loops check errors rather than results; scripts/bench-vs-luajit.sh and benchmarks/vsluajit/bench.lua exist but no LuaJIT numbers are published. Open bugs #297 (GC never triggers on host-only allocations) and #296 (arena grow-only).

## Caveats and trade-offs

Baseline is gopher-lua (itself roughly 3x slower than C Lua per its own wiki), so the ratios say little about PUC Lua 5.x or LuaJIT; there is no PUC Lua timing in the table (Lua 5.1.5 is only the correctness oracle). Numbers come from shared GitHub-hosted runners; the README says wall times drift 10-20% between rounds, and the workflow header itself says hosted-runner numbers should not be pasted into the README, yet the README tables are those numbers. The headline peaks (18.5x etc.) are from the non-production 'force' mode; 'auto' is a little lower. P1 loses to gopher-lua on fib and fannkuch, and the embedding-boundary rows (the main use of an embeddable VM) are slower than gopher-lua with the Call API. P3 baseline columns run a different workload shape (kernel x50). macOS runner CPU named only as Apple M-series. New project with 8 stars.

Pure Go, no cgo, so not directly usable from C++. Implements Lua 5.1 (no string.dump compatibility, VARARG never compiled by the JIT tiers, limited io). JIT tiers need explicit build tags, and the P5 trace JIT is not implemented. Differential fuzzing against the official Lua 5.1.5 is part of CI.

## Maintenance

Very active (1,244 commits, last commit 2026-10-04, nightly differential fuzzing) and Apache-2.0, but young (8 stars, 1 fork); the README says it runs in production at the author's company, while the P3 and P4 tiers are still release-candidate quality and the trace JIT (P5) is not implemented.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now A.
- **Tier reason:** README (and README.en.md) tables compare every Wangshu tier with gopher-lua v1.1.2 run on the same runner in the same round; benchmark code is public (benchmarks/baseline, benchmarks/heavy, benchmarks/realworld, benchmarks/embedded, scripts/bench-readme-table.sh, .github/workflows/bench-readme-table.yml), the Go toolchain comes from go.mod (go 1.27.0 via setup-go go-version-file), go test flags are given, and CPUs are named for the Linux rows (Intel Xeon Platinum 8573C, Azure Cobalt 100).
- **Verifier notes:** All quoted ratios appear on the page; record cherry-picked force-mode peaks and omitted that the Go-to-Lua Call boundary rows are slower than gopher-lua, corrected above. Metadata checked on github.com: Apache-2.0 (LICENSE file), 8 stars, 1 fork, not a fork or archived, last commit 2026-10-04 (active). Category language-interpreters fits; embedded-scripting (same wave) would also fit since it is an embeddable Lua 5.1 VM for Go.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Liam0205/wangshu/HEAD/README.md>
  - <https://raw.githubusercontent.com/Liam0205/wangshu/HEAD/README.en.md>
  - <https://raw.githubusercontent.com/Liam0205/wangshu/HEAD/.github/workflows/bench-readme-table.yml>
  - <https://raw.githubusercontent.com/Liam0205/wangshu/HEAD/scripts/bench-readme-table.sh>
  - <https://raw.githubusercontent.com/Liam0205/wangshu/HEAD/go.mod>
  - <https://raw.githubusercontent.com/Liam0205/wangshu/HEAD/LICENSE>
  - <https://github.com/Liam0205/wangshu>
  - <https://github.com/Liam0205/wangshu/commits>
- **Sources the enricher read:**
  - <https://github.com/Liam0205/wangshu>
  - <https://raw.githubusercontent.com/Liam0205/wangshu/HEAD/README.en.md>
  - <https://raw.githubusercontent.com/Liam0205/wangshu/HEAD/README.md>
  - <https://raw.githubusercontent.com/Liam0205/wangshu/HEAD/go.mod>
  - <https://raw.githubusercontent.com/Liam0205/wangshu/HEAD/scripts/bench-readme-table.sh>
  - <https://raw.githubusercontent.com/Liam0205/wangshu/HEAD/.github/workflows/bench-readme-table.yml>
  - <https://github.com/Liam0205/wangshu/tree/master/benchmarks>
  - <https://github.com/Liam0205/wangshu/tree/master/benchmarks/heavy>
  - <https://github.com/Liam0205/wangshu/tree/master/benchmarks/realworld>
  - <https://github.com/Liam0205/wangshu/tree/master/benchmarks/vsluajit>
  - <https://raw.githubusercontent.com/Liam0205/wangshu/master/benchmarks/go.mod>
  - <https://raw.githubusercontent.com/Liam0205/wangshu/master/benchmarks/realworld/realworld_bench_test.go>
  - <https://raw.githubusercontent.com/Liam0205/wangshu/master/benchmarks/realworld/realworld_gibbous_jit_test.go>
  - <https://raw.githubusercontent.com/Liam0205/wangshu/master/benchmarks/realworld/realworld_test.go>
  - <https://raw.githubusercontent.com/Liam0205/wangshu/master/benchmarks/heavy/heavy_bench_test.go>
  - <https://raw.githubusercontent.com/Liam0205/wangshu/master/benchmarks/heavy/heavy_gibbous_jit_test.go>
  - <https://raw.githubusercontent.com/Liam0205/wangshu/master/benchmarks/realworld/testdata/fib.lua>
  - <https://raw.githubusercontent.com/Liam0205/wangshu/master/benchmarks/realworld/testdata/fannkuch.lua>
  - <https://raw.githubusercontent.com/Liam0205/wangshu/master/benchmarks/realworld/testdata/nbody.lua>
  - <https://raw.githubusercontent.com/Liam0205/wangshu/master/benchmarks/realworld/testdata/spectralnorm.lua>
  - <https://raw.githubusercontent.com/Liam0205/wangshu/master/benchmarks/realworld/testdata/binarytrees.lua>
  - <https://raw.githubusercontent.com/Liam0205/wangshu/master/benchmarks/heavy/testdata/heavy_arith.lua>
  - <https://raw.githubusercontent.com/Liam0205/wangshu/master/benchmarks/heavy/testdata/heavy_recursion.lua>
  - <https://raw.githubusercontent.com/Liam0205/wangshu/master/benchmarks/heavy/testdata/heavy_floatloop.lua>
  - <https://raw.githubusercontent.com/Liam0205/wangshu/master/benchmarks/vsluajit/bench.lua>
  - <https://github.com/Liam0205/wangshu/tree/master/scripts>
  - <https://raw.githubusercontent.com/Liam0205/wangshu/master/scripts/bench-vs-luajit.sh>
  - <https://github.com/Liam0205/wangshu/tree/master/docs>
  - <https://raw.githubusercontent.com/Liam0205/wangshu/master/docs/embedding-tiers.md>
  - <https://raw.githubusercontent.com/Liam0205/wangshu/master/docs/design/roadmap.md>
  - <https://raw.githubusercontent.com/Liam0205/wangshu/master/docs/design/p4-method-jit/implementation-progress.md>
  - <https://github.com/Liam0205/wangshu/issues?q=is%3Aissue+luajit>
  - <https://github.com/Liam0205/wangshu/issues/112>
  - <https://github.com/Liam0205/wangshu/issues>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/liam0205/wangshu`) · [data/wave12/enrich/raw/github_com_liam0205_wangshu.json](../../../data/wave12/enrich/raw/github_com_liam0205_wangshu.json) (enrichment confidence 0.7)

</details>
