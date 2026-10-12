# Apogee (Lua 5.5 VM in pure Go with amd64/arm64 JIT)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Go` · `MIT` · 🟢 active

> Pure-Go Lua 5.5 VM with an amd64/arm64 method JIT; 0.57x C Lua 5.5's time on 17 standard benchmarks, about 3x behind LuaJIT.

| | |
|---|---|
| **Beats** | C Lua 5.5 (PUC-Rio; Lua 5.4.9 on the Apple M1 run) and Shopify/go-lua |
| **Claimed result** | With the JIT, 0.57x of C Lua 5.5's time (about 1.75x faster, derived from page data) on a Ryzen 9 9900X3D, faster than C Lua on all 17 standard benchmarks (Mandelbrot 0.20x, spectral-norm 0.33x, NBody 0.39x; least on DeltaBlue 0.90x, Json 0.88x, Richards 0.85x); 0.75x of C Lua 5.4 on an Apple M1 Pro; interpreter-only build is 1.8x slower than C Lua 5.5; about 10x faster than go-lua (5.9x C Lua's time); LuaJIT is still 0.18x of C Lua 5.5 (about 3x faster than Apogee's JIT, derived). Embedding suite vs native Go: 5.6x (JIT) vs 7.8x (C Lua 5.5) vs 2.3x (LuaJIT). |
| **Workload** | 17 standard benchmarks (14 Are We Fast Yet ports plus binary-trees, fannkuch-redux and spectral-norm from the Benchmarks Game) and an 11-workload embedding suite; geometric mean of per-benchmark time divided by C Lua's time. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 9900X3D, Linux, pinned to the six cores of one CCD (taskset -c 0-5); also Apple M1 Pro, macOS |
| **Compiler and flags** | Go 1.27.1, go test -bench -count 6 -ldflags=-funcalign=64 (CGO_ENABLED=0 for the Go interpreters), medians, taskset -c 0-5 (six cores of one CCD); C Lua 5.5.1 and LuaJIT 2.1.1788460057 from Arch Linux packages linked through cgo with build tags clua55 and luajit |
| **Adoption** | 0 stars |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/matjam/apogee) · [benchmark](https://raw.githubusercontent.com/matjam/apogee/HEAD/bench/README.md) |

## Verdict

On an AMD Ryzen 9 9900X3D (linux, Go 1.27.1, -ldflags=-funcalign=64, medians of 6 go test -bench runs), Apogee with its JIT took 0.57x the time of Arch Linux's C Lua 5.5.1 on the geometric mean of 14 Are We Fast Yet plus 3 Benchmarks Game programs (faster on all 17; 1.8x without the JIT; LuaJIT 2.1 0.18x), figures I recomputed exactly from the checked-in raw output; results are cross-checked by agreement tests, but the C rows are from an earlier, unpinned run.

## Use it when

- Go programs that embed Lua and want it faster than C Lua on compute without cgo, e.g. per-frame game or visualiser scripts (Mandelbrot 0.20x, spectral-norm 0.33x, NBody 0.39x C Lua 5.5's time)
- Numeric per-pixel or per-sample loops over Go-owned data: PushBuffer lets compiled kernels read and write a Go []float64/[]float32/[]int32/[]uint8 inline (plasma frame 0.25 ms vs 0.30 ms native Go in the bench notes)
- Replacing Shopify/go-lua: about 6x less time on the standard benchmarks (geomean 5.9x C Lua's time for go-lua vs 0.57x) and no allocation per number or call
- Hosts that need Lua 5.5 semantics (integer subtype, bitwise ops, &lt;close&gt;, global, utf8, string.pack) rather than LuaJIT's 5.1 dialect
- linux or darwin on amd64 or arm64, where the JIT is enabled

## Skip it when

- Peak Lua speed with cgo allowed: LuaJIT 2.1 is about 3x faster on the same table (0.18x vs 0.57x C Lua's time), 5-15x on numeric loops such as Permute and spectral-norm, and has FFI
- C or C++ hosts: it is a Go library; embed C Lua 5.5 or LuaJIT directly
- Windows or other platforms: no JIT there, and the interpreter alone takes 1.8x C Lua 5.5's time
- Scripts dominated by calls into Go, Go-called short Lua callbacks or table construction: on the embedding suite the JIT is slower than C Lua 5.5 on array fill and sum (1.00 vs 0.58 ms), sort with a comparator (3.84 vs 3.26 ms) and calls into Go (1.37 vs 1.07 ms)
- Projects that need C modules, standard luac bytecode, an incremental Lua GC or a mature, widely used runtime: C modules cannot load, binary chunks are apogee's own format, and the project is weeks old (v1.0.0 on 2026-09-26) with 0 stars

## How it is fast

A function-at-a-time JIT with hand-written amd64 and arm64 encoders (no cgo, no LLVM) compiles functions whose pc-0 or loop-head counters pass 1000, running on the interpreter's own 16-byte stack slots with inline caches for fields, native Lua-to-Lua calls and tail calls, and exits to a Go driver for Go calls, NEWTABLE, CLOSURE and generic table access. Innermost numeric loops (and, since v1.1.2, while loops, loop nests and whole small functions) become 'kernels': typed per pc, lowered through a small IR with a linear register allocator so integers and floats live in machine registers, with constant division by Hacker's Delight magic numbers, inline sqrt/sin/cos/floor/min/max bit-exact with Go, and inlining of tiny numeric Lua functions. Separately, the redesigned value, table and call representation means numbers, booleans and calls allocate nothing.

## Compared with alternatives

Pick it over FakeLua (C++ Lua JIT) when the host is Go and cgo is unwanted, over Luava when you are not on the JVM, and over goja-perf or quickjs-jit when you want Lua rather than JavaScript scripting in Go with numeric code in machine registers; choose LuaJIT instead whenever cgo and Lua 5.1 are acceptable.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none for the library (pure Go, CGO_ENABLED=0); the bench module uses Shopify/go-lua and, with build tags, C Lua or LuaJIT via cgo |
| **Minimum toolchain** | Go 1.27.1 (go.mod) |
| **Platforms** | JIT: linux and darwin on amd64 and arm64 (inline floor/ceil need SSE4.1 on amd64; inline sin/cos only below GOAMD64=v3); interpreter everywhere else Go runs, Windows included |
| **Thread safety** | One goroutine per State; only State.Interrupt is documented as safe to call from any goroutine. Generated code cannot be preempted by Go: it spends a 65536-step budget, then returns to Go and calls runtime.Gosched so the GC can stop the world |
| **Drop-in for the baseline** | partial: runs Lua 5.5 scripts (official 5.5 test suite passes except calls.lua's binary-chunk header check), but the host API is Go mirroring the C API, C modules cannot load, binary chunks differ, only the C locale exists and collectgarbage('count') reports Go's heap |

## Gotchas

- Benchmark provenance is mislabelled: bench/README.md says the amd64 Apogee rows are from 2026-09-27 at commit 45b42e8, but PR #168 (2026-09-28) re-ran them after the five kernel-IR phases (#159-#167) and moved the geomean from 0.69x to 0.57x without changing that header; at 45b42e8 the same README showed 0.69x. Reproduce at v1.1.2 or later, not 45b42e8.
- The C Lua 5.5 and LuaJIT baselines were not run under the stated 'taskset -c 0-5' pinning: the raw suite-results-amd64.txt shows every lua55 and luajit row at GOMAXPROCS 24 (no affinity mask) against 6 for every Go row, and they were measured two days earlier; on this dual-CCD 9900X3D the C rows could land on either CCD. Times are wall-clock, so Apogee's allocation-heavy rows (binary-trees, Havlak, CD) also get Go's concurrent collector on the other pinned cores while C Lua collects on the benchmark thread.
- Kernels need type-stable numeric loops: math.min(x, 1) returns an integer and can knock a float loop out of its kernel (write 1.0); a kernel whose entry check keeps failing slows the ordinary loop, and while Go's write barrier is on, compiled code exits for pointer stores, native calls and kernels.
- The M1 Pro table predates the Lua 5.5 port (compares with C Lua 5.4 at d5dba73) and was run on a busy machine; its Homebrew LuaJIT is anomalously slower than C Lua 5.4 on CD (329 vs 57.6 ms) and Json (19.3 vs 7.26 ms), which the project notes but does not explain.

## Known shortcomings

- LuaJIT is about 3x faster; the C Lua rows come from an older commit with up to 10% drift between days; the project is one week old, AI-written, 0 stars. Go, not C++; the record's 'first commits 2026-09-26' was the first release date.
- Enricher: bench/README names commit 45b42e8 (2026-09-27) for the amd64 rows but PR #168 re-ran them on 2026-09-28 after IR phases #159-#167 (geomean 0.69x to 0.57x of C Lua time) without updating the header; the raw suite-results-amd64.txt has all lua55 and luajit rows at GOMAXPROCS 24 and all Go rows at 6, and the C baselines were not under the stated taskset -c 0-5 pinning on the dual-CCD 9900X3D. Recomputed geomeans 0.57/1.80/0.18 match; the M1 Homebrew LuaJIT row is anomalous (CD 329 ms vs Lua 5.4 57.6 ms).

## Caveats and trade-offs

Not faster than LuaJIT: the same table puts LuaJIT at 0.18x C Lua 5.5 against Apogee's 0.57x, so LuaJIT is about 3x faster (derived from page data); the win is over PUC C Lua only. The C Lua 5.5 and LuaJIT rows were measured on 2026-09-25 at commit 3d3b49e and carried over, while the Apogee rows are from 2026-09-27 at commit 45b42e8, and the README says rows move by up to 10% between days. C Lua and LuaJIT come from Arch Linux packages linked through cgo, so their build flags are the distribution's, not stated in the README. Benchmark sizes are small (most Are We Fast Yet programs run one inner iteration; several rows take under 1 ms per op) and Go's benchmark loop amortizes JIT compilation, so the figures are steady-state. The M1 Pro table predates the Lua 5.5 port, compares against C Lua 5.4 and was run on a machine that was not idle (Apogee is 1.2x slower on binary-trees there). Very young: first release v1.0.0 on 2026-09-26 (bench runs from 2026-09-25); 540 commits including the inherited Shopify/go-lua history; most recent commits are co-authored by Claude and the README says generative AI did the engineering; 0 stars. Go, not C++. Found under its earlier repository name matjam/luart (renamed September 2026). [retier] bench/README names commit 45b42e8 (2026-09-27) for the amd64 rows, but PR #168 re-ran them on 2026-09-28 after IR phases #159-#167 (geomean 0.69x to 0.57x of C Lua 5.5 time) without updating the header; reproduce at v1.1.2. In suite-results-amd64.txt the lua55 and luajit rows ran at GOMAXPROCS 24 and the Go rows at 6, and the C baselines were not under the stated taskset -c 0-5 pinning (dual-CCD Ryzen 9 9900X3D). Recomputed geomeans 0.57 (vs Lua 5.5), 1.80 (vs LuaJIT, about 3x slower) and 0.18 (vs gopher-lua). The M1 Homebrew LuaJIT row is anomalous (CD 329 ms vs Lua 5.4 57.6 ms). One week old, AI-written, 0 stars; Go.

Pure Go with no cgo, so it is not directly usable from C++. Needs Go 1.27.1 or later. The JIT runs only on linux and darwin for arm64 and amd64; elsewhere (Windows included) it interprets at 1.8x C Lua's time. Lua 5.5 semantics but its own binary chunk format; C modules cannot load; C locale only; the collector is Go's with a Lua mark pass for weak tables and finalizers, not incremental.

## Maintenance

Active (v1.1.2 released 2026-10-05, about 540 commits including go-lua history, recent ones co-authored by Claude) and MIT-licensed pure Go that installs with go get, but a few weeks old with 0 stars, so treat it as experimental.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now A.
- **Tier reason:** bench/README.md carries every quoted number (standard-benchmark geomean 0.57x C Lua 5.5 with the JIT, 1.8x without, LuaJIT 0.18x; Mandelbrot 0.20x, spectral-norm 0.33x, fannkuch-redux 0.49x, DeltaBlue 0.90x; M1 Pro 0.75x against Lua 5.4). The benchmark code is public (bench/standard_test.go, bench/suite_test.go, bench/standard/ with the Are We Fast Yet Lua port, agreement tests) with raw output bench/suite-results-amd64.txt checked in, and Go 1.27.1, -count 6, -ldflags=-funcalign=64, taskset -c 0-5 and the AMD Ryzen 9 9900X3D are stated, so A holds.
- **Verifier notes:** All quoted numbers, MIT licence (Shopify 2014 plus Nathan Ollerenshaw 2026), 0 stars, fork of Shopify/go-lua and last commit 2026-10-05 verified on GitHub. Shortcomings to record: LuaJIT is about 3x faster than Apogee's JIT; baseline rows measured two days earlier at another commit with up to 10% day-to-day drift; distro-built C Lua and LuaJIT; small steady-state benchmarks; AI-written, one-week-old project with 0 stars; Go not C++. The record's 'first commits 2026-09-26' was really the first release date and is corrected in caveats.
- **Fields the verifier corrected:** `caveats`, `compiler_and_flags`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/matjam/apogee/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/matjam/apogee/HEAD/README.md>
  - <https://raw.githubusercontent.com/matjam/apogee/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/matjam/apogee/HEAD/bench/standard_test.go>
  - <https://raw.githubusercontent.com/matjam/apogee/HEAD/bench/suite-results-amd64.txt>
  - <https://github.com/matjam/apogee>
  - <https://github.com/matjam/apogee/commits>
  - <https://github.com/matjam/apogee/releases>
- **Sources the enricher read:**
  - <https://github.com/matjam/apogee>
  - <https://raw.githubusercontent.com/matjam/apogee/HEAD/README.md>
  - <https://raw.githubusercontent.com/matjam/apogee/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/matjam/apogee/edfd3f2/bench/README.md>
  - <https://raw.githubusercontent.com/matjam/apogee/HEAD/bench/standard_test.go>
  - <https://raw.githubusercontent.com/matjam/apogee/HEAD/bench/suite_test.go>
  - <https://raw.githubusercontent.com/matjam/apogee/HEAD/bench/suite-results-amd64.txt>
  - <https://raw.githubusercontent.com/matjam/apogee/HEAD/go.mod>
  - <https://raw.githubusercontent.com/matjam/apogee/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/matjam/apogee/HEAD/AGENTS.md>
  - <https://raw.githubusercontent.com/matjam/apogee/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/matjam/apogee/HEAD/lua/jit.go>
  - <https://raw.githubusercontent.com/matjam/apogee/HEAD/lua/jit_kernel.go>
  - <https://raw.githubusercontent.com/matjam/apogee/HEAD/lua/vm_jit.go>
  - <https://raw.githubusercontent.com/matjam/apogee/HEAD/lua/jit_none.go>
  - <https://github.com/matjam/apogee/tree/main/lua>
  - <https://github.com/matjam/apogee/tree/main/internal/jit>
  - <https://github.com/matjam/apogee/issues?q=is%3Aissue>
  - <https://github.com/matjam/apogee/commits/main>
  - <https://github.com/matjam/apogee/pull/168>
  - <https://github.com/matjam/apogee/pull/168/files>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/matjam/apogee`) · [data/wave12/enrich/raw/github_com_matjam_apogee.json](../../../data/wave12/enrich/raw/github_com_matjam_apogee.json) (enrichment confidence 0.75)

</details>
