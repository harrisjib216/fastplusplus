# wisp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Compact Rust Wasm runtime whose single-pass AArch64 compiler compiles faster than wasmtime Winch and wasmer Singlepass.

| | |
|---|---|
| **Beats** | wasmtime Winch (baseline compiler); wasmer Singlepass; wasmtime Cranelift on fib |
| **Claimed result** | Compile-only (wall clock, median): regex.wasm (1.36 MB) wisp 16.3 ms vs wasmtime Winch 24.2 ms, wasmer Singlepass 31.5 ms, wasmtime Cranelift 71.6 ms, wasmer Cranelift 82.0 ms; json.wasm (0.19 MB) wisp 4.5 ms vs Winch 8.3, Singlepass 14.2, wasmtime Cranelift 16.0, wasmer Cranelift 28.8. End to end (whole process, seconds): fib 34 wisp 0.022 vs wasmtime Cranelift 0.024, Winch 0.031, wasmer Singlepass 0.028; raytrace 0.054 vs Winch 0.066; json 0.263 vs Winch 0.325; regex 0.308 vs Winch 0.341. Slower than Winch on primes (0.120 vs 0.070), matmul (0.056 vs 0.049) and compress (0.713 vs 0.517), and 1.5-2.5x slower than wasmtime Cranelift on six of seven programs. |
| **Workload** | Whole-process wall time (including startup and compilation) of seven programs (primes, fib, matmul, raytrace, compress, json, regex) compiled to wasm32-wasip1, plus compile-only time for a 1.36 MB regex.wasm; median of 5 runs. |
| **Metric** | compile-time |
| **Hardware** | Apple M5, 10 cores, Darwin 27.0.0 (macOS 27); machine shared with other work while measuring |
| **Compiler and flags** | wisp: cargo build --release (Cargo.toml release profile with debug = 1; rustc version not recorded for the run, README says developed on 1.98). Guest programs: cargo build --release --target wasm32-wasip1. Baselines: wasmtime 49.0.1 and wasmer 7.5.0 release binaries run with -C cache=n / --disable-cache, Winch via -C compiler=winch (bench/run.py). |
| **Adoption** | 0 stars |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/useless-husband/wisp) · [benchmark](https://github.com/useless-husband/wisp/blob/HEAD/docs/benchmarks.md) |

## Verdict

First-party bench/run.py on an Apple M5 (10 cores, macOS 27, shared with other work) compares wisp 0.1.0 with wasmtime 49.0.1 and wasmer 7.5.0 release binaries with caches off, taking the median of 5 whole-process wall-clock runs and checking each run's output against native. Compile-only for regex.wasm takes 16.3 ms for wisp against 24.2 ms (Winch), 31.5 ms (Singlepass), 71.6 ms (wasmtime Cranelift) and 82.0 ms (wasmer Cranelift). End to end, wisp beats Winch on 4 of 7 programs but trails Cranelift by 1.5-2.5x on 6 of 7. The rustc version of the measured build is not recorded.

## Use it when

- Short-lived, compile-dominated Wasm runs on Apple Silicon macOS, where compile latency matters more than peak throughput (regex.wasm compile-only 16.3 ms against 24.2 ms for Winch and 31.5 ms for Singlepass).
- Mid-sized programs where a baseline compiler is enough: whole-process time beats wasmtime Winch on fib, raytrace, json and regex.
- Studying or teaching how a complete Wasm engine is built: about 12,600 lines with a design document, its own spec runner and a wasm-smith differential fuzzer.
- A dependency-light Rust embedding (libc is the only runtime dependency) that needs a cap-std-style WASI path sandbox.

## Skip it when

- Throughput-bound work: end to end it is 1.5-2.5x slower than wasmtime Cranelift on six of seven programs, and slower than Winch on primes (0.120 s vs 0.070 s), matmul and compress.
- Linux, x86-64 or Windows hosts: the compiler runs only on AArch64 macOS (Linux AArch64 paths exist but are disabled), and the interpreter used elsewhere is 3-8x slower than the compiler.
- Modules that need SIMD (v128 is rejected), threads, or any Wasm 3.0 feature (GC, exceptions, tail calls, memory64, multi-memory).
- C or C++ hosts: there is no C API header yet.
- Production use: 15 commits made on 2026-10-01 and 2026-10-02, version 0.1.0 unreleased, 0 stars, one author, no outside users or issues.

## How it is fast

Compile speed comes from a Liftoff-style single-pass compiler with no IR: an abstract operand stack whose entries sit in a register, a spill slot, the condition flags (so i32.lt_s; br_if becomes cmp; b.lt) or a pending constant, emitted straight through its own AArch64 encoder into MAP_JIT memory. Everything is spilled at block boundaries, so merges need no reconciliation; that keeps compilation cheap (the README demo compiles 1.36 MB regex.wasm in 8.3 ms in-process) but costs run-time speed. The interpreter uses slot-addressed three-address bytecode (the operand at depth d lives in slot nlocals+d), fused compare-and-branch and callee frames laid over the caller's argument slots.

## Compared with alternatives

Pick wisp over zwasm or cataggar/wamr only when you want a small, readable Rust engine with a baseline compiler on Apple Silicon and value compile latency; for a portable Rust embedding with fast startup pick Wasmi, and for throughput stay on wasmtime Cranelift.

## Integration

| | |
|---|---|
| **Form** | crate (use a git dependency; the crates.io name 'wisp' belongs to an unrelated tmux tool) plus a CLI binary |
| **Dependencies** | libc only; wast and wat are dev-dependencies for the spec runner; the spec suite is downloaded with curl on first test run |
| **Minimum toolchain** | Rust 1.88 (edition 2024); developed on 1.98 |
| **Platforms** | compiler: AArch64 macOS only; interpreter: any host Rust targets (CI runs macOS arm64 and Linux x86-64) |
| **Thread safety** | a Store is single-threaded; handles (Func, Memory and so on) are plain indices not checked against the Store they came from |
| **Drop-in for the baseline** | partial — API resembles wasmtime's but types and crate differ; no SIMD, threads or Wasm 3.0, and the compiler only on macOS AArch64 |

## Gotchas

- Compile-time comparison is not like for like: every figure is whole-process wall clock including start-up, wisp compile keeps the code in memory and compiles on one thread, while wasmtime compile and wasmer compile run in parallel and also serialize and write an artefact to disk. The README demo shows 8.3 ms of actual compile inside wisp's 13.7 ms in-process total for regex.wasm.
- The end-to-end rows under about 0.06 s (fib, matmul, raytrace) are dominated by process start-up and compilation, so wins over Winch there partly reflect wisp's faster compile rather than better generated code; the fib win over Cranelift (0.022 s vs 0.024 s) is within the noise of 5 runs on a machine shared with other work.
- Linear-memory accesses carry an explicit add; cmp; b.hi bounds check (no guard pages); the design notes blame it for the 2.5x gap to wasmtime on the memory-bound sieve.
- Functions too large for the 1 MiB reach of AArch64 conditional branches are silently left to the interpreter (a performance cliff on very large functions), and fuel traps may fire up to one block early.

## Known shortcomings

- Wins only on compile time and against Winch on 4 of 7 programs; 1.5-2.5x slower than Cranelift at run time, the compile comparison is not like for like, 5 runs on a shared machine with the rustc version unrecorded. Compiler is AArch64 macOS only, no C API, 0 stars.
- Enricher: docs/benchmarks.md uses whole-process wall clock, wasmtime and wasmer compile in parallel and write an artefact to disk, rows under 0.06 s are startup-dominated and the fib win is within noise; the compiler runs on macOS AArch64 only and the crates.io name 'wisp' belongs to an unrelated tmux tool.

## Caveats and trade-offs

The README says plainly that wisp is 1.5-2.5x slower than wasmtime Cranelift end to end on six of seven programs (only fib is faster, 0.022 vs 0.024 s, within noise). It also loses to Winch on primes, compress and matmul. The compile-time comparison is not like for like: wasmtime and wasmer compile functions in parallel and write the artefact to disk, while wisp compiles single-threaded in one process. All timings are whole-process wall clock (start-up included), median of only 5 runs, on a machine shared with other work. Own benchmarks only, 0 stars, 15 commits made 2026-10-01 to 2026-10-02, very new. The compiler runs only on AArch64 macOS (Linux/AArch64 paths are untested and disabled; other hosts use the interpreter, which is 3-8x slower than the compiler). No SIMD, threads or Wasm 3.0 proposals. A Rust library with no C API header yet, so not callable from C++ without bindings.

Compact (about 12,600 lines of Rust) runtime with validator, register-style interpreter and a single-pass AArch64 baseline compiler (macOS AArch64 only, Linux paths untested); passes 27,416 spec assertions on both engines; explicit bounds checks and no cross-block register allocation.

## Maintenance

Brand-new single-author project (15 commits over two days in October 2026, 0.1.0 unreleased) that is MIT-licensed and small enough to read or vendor, but it is a study piece, not yet a production runtime.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The README and docs/benchmarks.md (generated 2026-10-02 by the public bench/run.py) show all claimed numbers against wasmtime 49.0.1 Cranelift and Winch and wasmer 7.5.0 Cranelift and Singlepass on an Apple M5, with each run's output checked against native. It falls short of A because the rustc version used for the measured build is not recorded: there is no rust-toolchain file, and the README says only 'developed on 1.98'. The numbers are first-party, from 5 runs on a machine 'shared with other work while measuring', so tier C.
- **Verifier notes:** Numbers match the README and docs/benchmarks.md; added the json.wasm compile-only rows and the losing rows to claimed_speedup. Metadata checked on github.com: MIT (LICENSE and Cargo.toml), 0 stars, 0 forks, not a fork, last commit 2026-10-02 (active). Benchmarks were rerun on the final code ('bench: rerun on the final code'); only an interpreter NaN-rounding fix came after. Shortcomings to record: wins only on compile time and against Winch on 4 of 7 programs; compile comparison not like for like; first-party, 5 runs on a shared machine, rustc version unrecorded; compiler limited to AArch64 macOS; no C API.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/useless-husband/wisp/HEAD/README.md>
  - <https://github.com/useless-husband/wisp>
  - <https://github.com/useless-husband/wisp/commits>
  - <https://raw.githubusercontent.com/useless-husband/wisp/HEAD/docs/benchmarks.md>
  - <https://raw.githubusercontent.com/useless-husband/wisp/HEAD/bench/run.py>
  - <https://raw.githubusercontent.com/useless-husband/wisp/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/useless-husband/wisp/HEAD/Makefile>
  - <https://raw.githubusercontent.com/useless-husband/wisp/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/useless-husband/wisp>
  - <https://github.com/useless-husband/wisp/commits>
  - <https://github.com/useless-husband/wisp/tree/main/src>
  - <https://github.com/useless-husband/wisp/tree/main/src/jit>
  - <https://raw.githubusercontent.com/useless-husband/wisp/HEAD/README.md>
  - <https://raw.githubusercontent.com/useless-husband/wisp/HEAD/docs/benchmarks.md>
  - <https://raw.githubusercontent.com/useless-husband/wisp/HEAD/docs/DESIGN.md>
  - <https://raw.githubusercontent.com/useless-husband/wisp/HEAD/bench/run.py>
  - <https://raw.githubusercontent.com/useless-husband/wisp/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/useless-husband/wisp/HEAD/Makefile>
  - <https://raw.githubusercontent.com/useless-husband/wisp/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/useless-husband/wisp/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/useless-husband/wisp/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/useless-husband/wisp/HEAD/src/config.rs>
  - <https://raw.githubusercontent.com/useless-husband/wisp/HEAD/src/jit/compile.rs>
  - <https://raw.githubusercontent.com/useless-husband/wisp/HEAD/src/jit/mod.rs>
  - <https://raw.githubusercontent.com/useless-husband/wisp/HEAD/src/jit/codemem.rs>
  - <https://raw.githubusercontent.com/useless-husband/wisp/HEAD/src/wasi/sandbox.rs>
  - <https://crates.io/api/v1/crates/wisp>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/useless-husband/wisp`) · [data/wave12/enrich/raw/github_com_useless_husband_wisp.json](../../../data/wave12/enrich/raw/github_com_useless_husband_wisp.json) (enrichment confidence 0.7)

</details>
