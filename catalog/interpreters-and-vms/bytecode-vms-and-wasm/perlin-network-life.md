# Life (perlin-network)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🔴 abandoned

> Pure-Go WebAssembly MVP interpreter with gas metering; 2018 runs beat the then-current wasmi and wagon by about 2x.

| | |
|---|---|
| **Beats** | wasmi (paritytech/wasmi, 2018 version) and wagon (go-interpreter/wagon) |
| **Claimed result** | Raw results gist, real time: Pollard rho Life JIT 1.672 s, interpreter 2.178 s, wagon 4.349 s, wasmi 4.852 s; Snappy compress Life JIT 1.072 s, interpreter 2.977 s, wagon 5.443 s, wasmi 7.017 s; recursive Fibonacci Life JIT 3.898 s, interpreter 3.071 s, wagon 6.204 s, wasmi 5.811 s. So roughly 1.5x to 6.5x faster than wasmi with the JIT/AOT engine and 1.9x to 2.4x with the plain interpreter, and 1.6x to 5.1x faster than wagon with the JIT (derived from page data). |
| **Workload** | Three Rust programs in bench/cases compiled to wasm32-unknown-unknown with cargo build --release: 128-bit Pollard rho factoring, Snappy compression and recursive Fibonacci, timed end to end with the shell `time` command (bench/cases/run_item.sh), so real time includes process startup and module compilation. |
| **Metric** | throughput |
| **Adoption** | 1.7k stars |
| **Last commit** | 2019-12-03 |
| **Links** | [repository](https://github.com/perlin-network/life) · [benchmark](https://gist.github.com/losfair/5605f61602537916f342c3e4ace1cc9b) |

## Verdict

In August 2018, the author's gist timed three Rust programs compiled to wasm32-unknown-unknown (128-bit Pollard rho, one Snappy compression of 8 MiB of zeros, fib(35)) with shell 'time'. Life's interpreter took 2.18/2.98/3.07 s against 4.85/7.02/5.81 s for the 2018 wasmi and 4.35/5.44/6.20 s for wagon, about 1.9-2.4x faster than wasmi (derived from page data). The timings state no CPU, Go version or engine versions, and the 'JIT' column comes from an engine that has since been removed.

## Use it when

- A Go program that must run untrusted Wasm MVP modules with per-instruction gas accounting and hard memory/call-depth caps, without cgo (interpreter-only mode).
- Studying or forking a small, readable register-IR Wasm interpreter written in Go (SSA translation plus a switch loop).
- Legacy deployments already pinned to Life whose modules are plain integer-heavy MVP code (no SIMD, threads, bulk memory or reference types).

## Skip it when

- Any new project. The repo has had no commit since 2019-12-03, 29 issues are open, and modern Go runtimes (wazero, or the catalogued Go sibling wazy) and modern interpreters (wasm3, Wasmi) are maintained and much faster.
- Raw speed. wasm3's docs/Interpreter.md (independent, 4 GHz Core i7 iMac) times Life at 547 s on Mandelbrot vs wasm3 17.9 s, and 153 s on CRC32 vs 5.1 s, roughly 30x slower.
- WASI programs, or modules built by current toolchains that emit post-MVP features: neither is supported (issue #96 asks for WASI; issue #112 asks about Go-built Wasm).
- Floating-point-heavy code: open issue #98 reports wrong pow() results (pow(3.0, 0.3) gives 1.1293 instead of 1.3904).
- Using Polymerase in production: it needs cgo, clang on the host at run time and dlopen of a temp file. The AOTService only invokes functions with 0, 1 or 2 parameters, and open bug #90 reports fib returning 0 with Polymerase enabled.

## How it is fast

Before execution, each function is translated from the Wasm stack bytecode into an SSA-style register IR (compiler/ssa.go). Registers are then assigned per stack slot. The FIXME in liveness.go says there is no real liveness-based allocation yet. The interpreter runs this register code in one big switch loop over 5-byte instruction headers (uint32 target register plus opcode), which avoids the push/pop traffic of a stack interpreter. The optional Polymerase engine translates the whole module to C, compiles it with clang -O2 -fPIC -shared at run time and dlopens the result through cgo. The 'JIT' timed in the 2018 gist was an earlier engine: it generated C per function, compiled it with cc -O1 and dlopened it, and it has since been removed.

## Compared with alternatives

Pick Life only when you are maintaining an existing Life integration that depends on its gas-metering API. For new Go embeddings, use wazy (the catalogued wazero fork) or wasm2go, and for a fast interpreter use wasm3 or Wasmi: all are maintained and beat Life's interpreter by large margins.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | github.com/go-interpreter/wagon v0.6.0 (parser, disassembler, validation), github.com/vmihailenco/msgpack; Polymerase also needs cgo, libdl and a clang binary on PATH at run time |
| **Minimum toolchain** | go.mod says go 1.13 (Go modules required; README uses GO111MODULE=on) |
| **Platforms** | Interpreter: any Go target (pure Go). Polymerase: aot_unix.go includes runtime_linux_x86_64.h, and there are separate aot_windows.go and aot_android_arm.go files plus a js/wasm placeholder; other platforms print 'not yet supported'. |
| **Thread safety** | not documented; a VirtualMachine holds mutable run state (frames, Delegate, InsideExecute, Exited), so use one VM per goroutine |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: the committed bench/cases/run_item.sh runs '../../life -jit', but current main.go defines no -jit flag (only -entry, -polymerase and -no-fp), and exec/vm.go prints 'Warning: JIT support is removed.'. The script fails at HEAD, and the gist's 'Life (JIT enabled)' columns (1.672 s, 1.072 s, 3.898 s) came from a removed per-function C codegen engine (cc -O1 plus dlopen) that you cannot use today.
- Harness flaw: the README chart (media/bench.png, updated 2018-12-17) shows near-zero 'Life (Polymerase)' bars, but no raw numbers or method exist for them, while its interp/wagon/wasmi bars are the August 2018 gist values. The next day (b783dc5, 2018-12-18) snappy_compress was changed to loop 1000 times. The gist's return value 393476 is one compression of 8 MiB of zeros, so the committed workload no longer matches any published number.
- Methodology: all numbers are whole-process 'time' real values, so Life's figures include Go startup, validation and SSA compilation, and wasmi's include its own load. The commands used to run wagon and wasmi are not in the repo or the gist. The snappy case compresses an all-zero buffer, a degenerate input dominated by the match-extension loop.
- Errors inside the VM are Go panics recovered in Execute and stored in vm.ExitError; open issues #99, #100 and #104 report panic handling, unreachable detection and 'inconsistent stack pattern' failures.

## Known shortcomings

- Gist numbers date from 2018-08-01 (not 2019) with no hardware; the fibonacci JIT is slower than Life's own interpreter; bench/cases code is public. Go wasm VM; abandoned.
- Harness flaw: bench/cases/run_item.sh calls life -jit, but HEAD main.go has no -jit flag and exec/vm.go prints 'JIT support is removed.', so the gist 'JIT' columns came from since-removed per-function C codegen (cc -O1 plus dlopen). The README chart (2018-12-17) adds near-zero 'Life (Polymerase)' bars with no raw numbers. Commit b783dc5 (2018-12-18) made the snappy_compress loop run 1000x, so the committed workload matches no published number (gist value 393476 is one compression of 8 MiB zeros). Independent wasm3 docs/Interpreter.md has Life about 30x slower than wasm3 (Mandelbrot 547 s vs 17.9 s, CRC32 153 s vs 5.1 s). Open bugs #90 (Polymerase returns 0) and #98 (pow wrong).

## Caveats and trade-offs

Numbers date from August 2018 (gist created 2018-08-01) against the then-current wasmi (a much slower pre-register-machine design) and wagon, so they do not carry to wasmi 0.30+/1.x, wasm3 or Wasmtime. No hardware, Go version or engine versions are stated; the README only shows a chart image and links the gist. On recursive Fibonacci the Life JIT/AOT (3.898 s) is slower than Life's own interpreter (3.071 s). The repo was last committed in December 2019 and is unmaintained (not archived).

Pure-Go interpreter (no cgo) plus an experimental AOT/JIT engine that needs native code generation; implements WebAssembly MVP only (66 of 72 spec tests passed at the time) and has no WASI or modern proposals.

## Maintenance

Abandoned since December 2019 (not archived) and MIT-licensed. The pure-Go interpreter still builds as a module, but the benchmark script no longer runs against current main.go and the published speedups describe 2018 competitors, so treat it as a historical reference rather than a current fast choice.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The gist holds first-party raw `time` output for Life JIT, Life interpreter, wagon and wasmi on three programs, with matching return values; the workload code is public (bench/cases: Rust programs built with cargo build --release for wasm32, run via run_item.sh), but no CPU, Go version or engine versions are stated, so C.
- **Verifier notes:** Gist numbers match the record exactly and the derived ratios hold (JIT 1.5x to 6.5x vs wasmi, interpreter 1.9x to 2.4x, JIT 1.6x to 5.1x vs wagon). Only fix: the measurements are from 2018, not 2019. Repo MIT, 1.7k stars, last commit 2019-12-03, abandoned.
- **Fields the verifier corrected:** `baseline`, `workload`, `caveats`
- **Shortcomings recorded by:** independent measurement against current wasmi, wasm3 and Wasmtime
- **Pages the verifier opened:**
  - <https://github.com/perlin-network/life>
  - <https://github.com/perlin-network/life/commits/master>
  - <https://github.com/perlin-network/life/tree/master/bench>
  - <https://github.com/perlin-network/life/tree/master/bench/cases>
  - <https://raw.githubusercontent.com/perlin-network/life/HEAD/README.md>
  - <https://raw.githubusercontent.com/perlin-network/life/master/bench/cases/build_all.sh>
  - <https://raw.githubusercontent.com/perlin-network/life/master/bench/cases/build_item.sh>
  - <https://raw.githubusercontent.com/perlin-network/life/master/bench/cases/run_builds.sh>
  - <https://raw.githubusercontent.com/perlin-network/life/master/bench/cases/run_item.sh>
  - <https://raw.githubusercontent.com/perlin-network/life/master/bench/cases/.cargo/config>
  - <https://gist.github.com/losfair/5605f61602537916f342c3e4ace1cc9b>
- **Sources the enricher read:**
  - <https://github.com/perlin-network/life>
  - <https://github.com/perlin-network/life/commits/master>
  - <https://github.com/perlin-network/life/tree/master/bench/cases>
  - <https://github.com/perlin-network/life/tree/master/platform>
  - <https://github.com/perlin-network/life/tree/master/compiler>
  - <https://github.com/perlin-network/life/tree/955d4ba/exec>
  - <https://github.com/perlin-network/life/commits/master/bench/cases/snappy_compress/src/lib.rs>
  - <https://github.com/perlin-network/life/commits/master/media/bench.png>
  - <https://github.com/perlin-network/life/issues>
  - <https://github.com/perlin-network/life/issues/98>
  - <https://github.com/perlin-network/life/issues/90>
  - <https://raw.githubusercontent.com/perlin-network/life/HEAD/README.md>
  - <https://raw.githubusercontent.com/perlin-network/life/HEAD/main.go>
  - <https://raw.githubusercontent.com/perlin-network/life/HEAD/go.mod>
  - <https://raw.githubusercontent.com/perlin-network/life/HEAD/media/bench.png>
  - <https://raw.githubusercontent.com/perlin-network/life/HEAD/bench/cases/run_item.sh>
  - <https://raw.githubusercontent.com/perlin-network/life/HEAD/bench/cases/build_item.sh>
  - <https://raw.githubusercontent.com/perlin-network/life/HEAD/bench/cases/build_all.sh>
  - <https://raw.githubusercontent.com/perlin-network/life/HEAD/bench/cases/run_builds.sh>
  - <https://raw.githubusercontent.com/perlin-network/life/HEAD/bench/cases/.cargo/config>
  - <https://raw.githubusercontent.com/perlin-network/life/HEAD/bench/cases/fib_recursive/src/lib.rs>
  - <https://raw.githubusercontent.com/perlin-network/life/HEAD/bench/cases/pollard_rho_128/src/lib.rs>
  - <https://raw.githubusercontent.com/perlin-network/life/HEAD/bench/cases/snappy_compress/src/lib.rs>
  - <https://raw.githubusercontent.com/perlin-network/life/955d4ba/bench/cases/snappy_compress/src/lib.rs>
  - <https://raw.githubusercontent.com/perlin-network/life/955d4ba/main.go>
  - <https://raw.githubusercontent.com/perlin-network/life/955d4ba/exec/vm.go>
  - <https://raw.githubusercontent.com/perlin-network/life/955d4ba/exec/vm_codegen.go>
  - <https://raw.githubusercontent.com/perlin-network/life/955d4ba/exec/code_loader_unix.go>
  - <https://raw.githubusercontent.com/perlin-network/life/HEAD/platform/aot_unix.go>
  - <https://raw.githubusercontent.com/perlin-network/life/HEAD/compiler/ssa.go>
  - <https://raw.githubusercontent.com/perlin-network/life/HEAD/compiler/liveness.go>
  - <https://raw.githubusercontent.com/perlin-network/life/HEAD/compiler/gas_policy.go>
  - <https://raw.githubusercontent.com/perlin-network/life/HEAD/exec/vm.go>
  - <https://gist.github.com/losfair/5605f61602537916f342c3e4ace1cc9b>
  - <https://raw.githubusercontent.com/wasm3/wasm3/main/docs/Performance.md>
  - <https://raw.githubusercontent.com/wasm3/wasm3/main/docs/Interpreter.md>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/perlin-network/life`) · [data/wave12/enrich/raw/github_com_perlin_network_life.json](../../../data/wave12/enrich/raw/github_com_perlin_network_life.json) (enrichment confidence 0.8)

</details>
