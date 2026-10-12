# PolkaVM

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Sandboxed RISC-V (RV32EM/RV64EM) VM with a single-pass x86-64 recompiler: compiles 170-470x faster than Wasmtime Cranelift, executes near Wasmtime speed.

| | |
|---|---|
| **Beats** | Wasmtime (cranelift); the same table also lists Wasmtime winch, Wasmer singlepass, Wasm3, Wasmi, wazero, CKB VM and Solana RBPF |
| **Claimed result** | One-shot (compile + init + run) on pinky: PolkaVM 64-bit recompiler 55.408 ms vs Wasmtime (cranelift) 116.002 ms and Wasmer (singlepass) 137.832 ms (about 2.1x and 2.5x, derived from page data). prime-sieve: 14.390 ms vs Wasmtime cranelift 125.107 ms, Wasmtime winch 54.295 ms, Wasmer singlepass 57.379 ms (about 8.7x, 3.8x, 4.0x, derived from page data). minimal: 113.743 us vs Wasmtime cranelift 935.241 us (about 8.2x) but only 1.13x ahead of Wasmer singlepass 128.467 us (derived from page data). Compile time on pinky: 167.553 us vs Wasmtime cranelift 62.212 ms (about 370x); prime-sieve 442.354 us vs 76.662 ms (about 173x) (derived from page data). Steady-state execution is not faster: pinky 6.422 ms vs Wasmtime cranelift 5.776 ms; prime-sieve 2.104 ms vs 2.161 ms (parity); minimal 4.852 us vs 0.252 us per call (PolkaVM about 19x slower, derived from page data). |
| **Workload** | Three guest programs (pinky, a cycle-accurate NES emulator running a homebrew game; prime-sieve; minimal) built for PolkaVM's RISC-V RV32EM ISA and for WebAssembly for the other VMs; one-shot time including compilation and initialization, steady-state execution time, and compile time. |
| **Metric** | startup |
| **Hardware** | AMD Ryzen Threadripper 3970X 32-Core, x86_64 Linux; results from commit 190ea5ac, timestamp 2024-11-24 |
| **Compiler and flags** | At the benchmarked commit 190ea5ac: benchtool built with Rust 1.82.0 (tools/benchtool/rust-toolchain.toml; the workspace root pinned 1.75.0, and the 1.86.0 in the record is today's HEAD), cargo --release with lto = true, codegen-units = 1, debug = true; guest programs built with nightly-2024-11-01 (guest-programs/rust-toolchain.toml) by guest-programs/build-benchmarks.sh, Wasm guests with RUSTFLAGS '-C target-cpu=mvp -C target-feature=-sign-ext'; benchtool pins wasmtime 26.0.1 (default features off: cranelift, winch, runtime, so no parallel compilation and no cache), wasmer 5.0.0 (singlepass), wasmi 0.39.1, and a Go shim on wazero v1.8.1; 02-run-benchmarks.rb disables turbo boost, sets the performance governor and pins the run to CPUs 1-2 with a cgroup; criterion sample_size 10, mean estimate reported. |
| **Adoption** | 434 stars; crates.io polkavm about 9.75M downloads |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/paritytech/polkavm) · [benchmark](https://github.com/paritytech/polkavm/blob/master/BENCHMARKS.md) |

## Verdict

The author's benchtool (criterion, sample size 10, Threadripper 3970X, turbo off, pinned to two cores, commit 190ea5ac, 2024-11-24) shows PolkaVM's 64-bit recompiler finishing compile+instantiate+run in 55.4 ms on the pinky NES emulator vs 116.0 ms for Wasmtime 26 Cranelift and 137.8 ms for Wasmer 5 singlepass, and 14.4 ms vs 125.1 ms on prime-sieve; the win comes from compile time (0.168 ms vs 62.2 ms on pinky), while steady-state execution is at parity or slower.

## Use it when

- Hosts that load many different untrusted programs and run each briefly, where compile latency dominates: blockchain smart contracts (Polkadot SDK's pallet-revive and sc-executor-polkavm depend on it) or plugin systems.
- x86-64 Linux deployments that need deterministic execution plus built-in gas metering; async gas costs about 14% on pinky execution vs 44% for Wasmtime fuel metering (derived from page data).
- Workloads of a few hundred milliseconds of guest execution or less: on pinky the 62 ms Cranelift compile only pays for itself after about 96 emulated frames (about 0.6 s of execution, derived from page data).
- When you control the guest toolchain (Rust, or C via the guest header in capi/) and can target its RISC-V ISA instead of Wasm.

## Skip it when

- Existing WebAssembly modules or a Wasm toolchain you cannot change: there is no Wasm front end (issue #37 is still research).
- Long-running or call-heavy guests: steady-state execution is equal to or slower than Wasmtime Cranelift (pinky 6.422 ms vs 5.776 ms) and the recompiler's per-call cost is 4.852 us vs 0.252 us for Wasmtime on the minimal program (about 19x).
- Tiny programs: PolkaVM's own interpreter does the minimal one-shot in 2.533 us vs 113.743 us for its recompiler, and Wasmi in about 26 us.
- Non-x86-64 or non-Linux hosts: the recompiler is compiled only for x86-64 Linux (macOS/FreeBSD x86-64 behind the experimental generic-sandbox feature); aarch64 and everything else fall back to the interpreter, which is about 30x slower on pinky.
- Floating-point or SIMD guest code, a C host API (issue #132 open), or production stability: the README says unfinished, heavy work in progress, do not use in production.

## How it is fast

The recompiler translates RISC-V instructions to x86-64 in a single O(n) pass with its own assembler, which is why compile time is in microseconds where Cranelift's optimising pipeline takes tens of milliseconds. Despite the single pass, its output is only about 11% slower than Cranelift's on pinky and about equal on prime-sieve. Compiler scratch buffers are reused across compilations, and the Engine keeps a pool of pre-spawned sandbox worker processes (default 2) so instantiation does not fork a process.

## Compared with alternatives

Pick PolkaVM over Wasmi, wasm3 or DLR-FT's interpreter when guests do real work: on pinky its recompiler executes about 17x faster than Wasmi (6.4 ms vs 112 ms) while compiling in 0.17 ms; pick it over wisp, zwasm or Wasmtime Winch when you can leave Wasm and want both microsecond compile and near-Cranelift execution, and stay with Wasmi or PolkaVM's interpreter for tiny, call-once programs.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | log, picosimd, polkavm-assembler, polkavm-common (all in-repo except log and picosimd); polkavm-linux-raw on x86-64 Linux; optional schnellru for module-cache; guests need polkatool and a nightly Rust for -Z build-std |
| **Minimum toolchain** | Rust 1.86.0 (crate 0.37.0); benchmarked commit used Rust 1.82.0 for the host and nightly-2024-11-01 for guests |
| **Platforms** | Recompiler: x86-64 Linux (x86-64 macOS/FreeBSD only with the experimental generic-sandbox feature); interpreter everywhere, including no_std |
| **Thread safety** | not documented in the files read |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness note (no bug found behind the numbers): 'one-shot' starts the timer after Engine creation, and PolkaVM's Engine::new pre-spawns two Linux sandbox worker processes that are reused between instantiations, so cold process start is excluded (Wasmtime's Engine creation is excluded too). Even so, on the minimal program about 107 us of PolkaVM's 113.7 us one-shot is instantiation beyond compile and run (derived from page data).
- Harness note: Wasm guests were built with -C target-cpu=mvp -C target-feature=-sign-ext, i.e. without bulk-memory or sign-extension ops, while the headline PolkaVM row is the 64-bit RV64EMAC build; benchtool at HEAD still pins Wasmtime 26.0.1 and Wasmer 5.0.0 and BENCHMARKS.md has not been regenerated since 2024-11-24 (crate now 0.37.0). Only prime-sieve validates its output (asserts in initialize); pinky's timed path has no output check.
- Open correctness issue #413 (2026-08-15): interpreter and recompiler disagree on memset operand width (interpreter truncates dst and count to 32 bits) in the Latest32/Latest64 instruction sets, so crosscheck runs can diverge; #402 (Linux sandbox rewrite, correctness and performance, P-high) is pending.
- Gas metering variants are not free: sync gas adds about 24% to pinky execution and 81% to prime-sieve one-shot on the 64-bit recompiler (derived from page data).

## Known shortcomings

- First-party BENCHMARKS.md snapshot from 2024 (benchtool Rust 1.82.0, guests nightly-2024-11-01 at 190ea5ac): wins only one-shot and compile time, steady-state at or below Wasmtime Cranelift, the minimal per-call benchmark 19x slower (4.852 us vs 0.252 us), and the README says it is not for production. Rust RISC-V VM, not a wasm runtime in C++.
- Enricher: the one-shot timer starts after Engine::new, which pre-spawns 2 sandbox worker processes, so cold process start is excluded; Wasm guests were built MVP without sign-ext; benchtool HEAD still pins Wasmtime 26.0.1 and Wasmer 5.0.0 with results not refreshed since 2024-11-24. The pinky win is compile time only (Wasmtime breaks even after about 96 frames, about 0.6 s, derived); the recompiler is x86-64 Linux only with aarch64 falling back to the interpreter; open #413 (interpreter/recompiler memset width mismatch); capi/ is a guest-only header, so still no C host API (#132).

## Caveats and trade-offs

Numbers date from November 2024 (commit 190ea5ac; Wasmtime 26, Wasmer 5), long before current Wasmtime releases. This is a first-party suite: the PolkaVM author chose the workloads. The VMs execute different binaries (RISC-V for PolkaVM, Wasm for the rest), and the Wasm guests were built for the MVP target with sign-ext disabled. The win is in one-shot and compile time. Wasmtime cranelift is faster or equal in steady-state execution on pinky and prime-sieve, and about 19x faster per call on the minimal program, because PolkaVM's recompiler has a high fixed per-call cost from running in a separate sandbox process. Part of the compile-time gap is that Wasmtime cranelift optimizes while PolkaVM's recompiler is single-pass (README: guaranteed single-pass O(n) compilation). Wasmtime was built without parallel compilation. The README says the project is unfinished and should not be used in production.

Guests must be compiled for PolkaVM's own RV32EM RISC-V ISA, not WebAssembly; no floating point or SIMD by design; Rust host API (no C API seen in the workspace); sandboxing and gas metering are built in; the interpreter fallback is far slower (pinky 1.689 s one-shot vs 55.408 ms recompiler); README says the project is unfinished and a heavy work in progress.

## Maintenance

Very active (crate 0.37.0 released 2026-09-28, about 9.75M crates.io downloads, last commit 2026-10-06) and MIT OR Apache-2.0, used by Polkadot SDK crates despite the README's not-for-production warning; the benchmark is first-party and two years old, and the enricher found no correctness bug behind the measured numbers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now A.
- **Tier reason:** BENCHMARKS.md gives per-VM tables against Wasmtime (cranelift, winch) and Wasmer singlepass with the CPU model (Threadripper 3970X), the exact commit 190ea5ac and replication steps; the harness is public (tools/benchtool: src/main.rs, src/backend/backend_\*.rs, 01-build-benchmarks.sh, 02-run-benchmarks.rb, 03-analyze-benchmarks.rb), with toolchains pinned by rust-toolchain.toml files and flags in Cargo.toml and guest-programs/build-benchmarks.sh at that commit. I checked that PolkaVM's compile rows are not cache hits: the module-cache feature is off by default and benchtool does not enable it.
- **Verifier notes:** The numbers match BENCHMARKS.md exactly. The record's toolchain was HEAD's (1.86.0), not the benchmarked commit's (benchtool 1.82.0, guests nightly-2024-11-01); I fixed it and added the minimal-program rows, where PolkaVM's per-call execution is about 19x slower than Wasmtime. The metadata checks out: 434 stars, MIT OR Apache-2.0, last commit 2026-10-06, crates.io 9,754,111 downloads. Shortcomings to record: a first-party suite, a 2024 snapshot, the win is one-shot and compile time only, steady-state execution is equal to or slower than Wasmtime cranelift, and the README says not for production.
- **Fields the verifier corrected:** `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/paritytech/polkavm/blob/master/BENCHMARKS.md>
  - <https://github.com/paritytech/polkavm>
  - <https://github.com/paritytech/polkavm/commits>
  - <https://raw.githubusercontent.com/paritytech/polkavm/HEAD/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/paritytech/polkavm/HEAD/README.md>
  - <https://raw.githubusercontent.com/paritytech/polkavm/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/paritytech/polkavm/HEAD/tools/benchtool/Cargo.toml>
  - <https://raw.githubusercontent.com/paritytech/polkavm/190ea5ac10344714b914230974bb9cb12bef56d6/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/paritytech/polkavm/190ea5ac10344714b914230974bb9cb12bef56d6/tools/benchtool/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/paritytech/polkavm/190ea5ac10344714b914230974bb9cb12bef56d6/tools/benchtool/Cargo.toml>
  - <https://raw.githubusercontent.com/paritytech/polkavm/190ea5ac10344714b914230974bb9cb12bef56d6/tools/benchtool/src/main.rs>
  - <https://raw.githubusercontent.com/paritytech/polkavm/190ea5ac10344714b914230974bb9cb12bef56d6/tools/benchtool/src/backend/backend_polkavm.rs>
  - <https://raw.githubusercontent.com/paritytech/polkavm/190ea5ac10344714b914230974bb9cb12bef56d6/tools/benchtool/src/backend/backend_wasmtime.rs>
  - <https://raw.githubusercontent.com/paritytech/polkavm/190ea5ac10344714b914230974bb9cb12bef56d6/tools/benchtool/02-run-benchmarks.rb>
  - <https://raw.githubusercontent.com/paritytech/polkavm/190ea5ac10344714b914230974bb9cb12bef56d6/tools/benchtool/03-analyze-benchmarks.rb>
  - <https://raw.githubusercontent.com/paritytech/polkavm/190ea5ac10344714b914230974bb9cb12bef56d6/guest-programs/build-benchmarks.sh>
  - <https://raw.githubusercontent.com/paritytech/polkavm/190ea5ac10344714b914230974bb9cb12bef56d6/guest-programs/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/paritytech/polkavm/190ea5ac10344714b914230974bb9cb12bef56d6/crates/polkavm/Cargo.toml>
  - <https://raw.githubusercontent.com/paritytech/polkavm/190ea5ac10344714b914230974bb9cb12bef56d6/crates/polkavm/src/module_cache.rs>
  - <https://crates.io/api/v1/crates/polkavm>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/paritytech/polkavm/HEAD/README.md>
  - <https://raw.githubusercontent.com/paritytech/polkavm/HEAD/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/paritytech/polkavm/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/paritytech/polkavm/HEAD/crates/polkavm/Cargo.toml>
  - <https://raw.githubusercontent.com/paritytech/polkavm/HEAD/crates/polkavm/src/lib.rs>
  - <https://raw.githubusercontent.com/paritytech/polkavm/HEAD/benches/run.sh>
  - <https://raw.githubusercontent.com/paritytech/polkavm/HEAD/benches/Cargo.toml>
  - <https://raw.githubusercontent.com/paritytech/polkavm/HEAD/tools/benchtool/Cargo.toml>
  - <https://raw.githubusercontent.com/paritytech/polkavm/190ea5ac10344714b914230974bb9cb12bef56d6/tools/benchtool/src/main.rs>
  - <https://raw.githubusercontent.com/paritytech/polkavm/190ea5ac10344714b914230974bb9cb12bef56d6/tools/benchtool/src/backend.rs>
  - <https://raw.githubusercontent.com/paritytech/polkavm/190ea5ac10344714b914230974bb9cb12bef56d6/tools/benchtool/src/backend/backend_polkavm.rs>
  - <https://raw.githubusercontent.com/paritytech/polkavm/190ea5ac10344714b914230974bb9cb12bef56d6/tools/benchtool/src/backend/backend_wasmtime.rs>
  - <https://raw.githubusercontent.com/paritytech/polkavm/190ea5ac10344714b914230974bb9cb12bef56d6/tools/benchtool/02-run-benchmarks.rb>
  - <https://raw.githubusercontent.com/paritytech/polkavm/190ea5ac10344714b914230974bb9cb12bef56d6/tools/benchtool/Cargo.toml>
  - <https://raw.githubusercontent.com/paritytech/polkavm/190ea5ac10344714b914230974bb9cb12bef56d6/tools/benchtool/01-build-benchmarks.sh>
  - <https://raw.githubusercontent.com/paritytech/polkavm/190ea5ac10344714b914230974bb9cb12bef56d6/guest-programs/build-benchmarks.sh>
  - <https://raw.githubusercontent.com/paritytech/polkavm/190ea5ac10344714b914230974bb9cb12bef56d6/guest-programs/bench-pinky/src/main.rs>
  - <https://raw.githubusercontent.com/paritytech/polkavm/190ea5ac10344714b914230974bb9cb12bef56d6/guest-programs/bench-minimal/src/main.rs>
  - <https://raw.githubusercontent.com/paritytech/polkavm/190ea5ac10344714b914230974bb9cb12bef56d6/guest-programs/bench-prime-sieve/src/main.rs>
  - <https://raw.githubusercontent.com/paritytech/polkavm/190ea5ac10344714b914230974bb9cb12bef56d6/crates/polkavm/src/config.rs>
  - <https://raw.githubusercontent.com/paritytech/polkavm/190ea5ac10344714b914230974bb9cb12bef56d6/crates/polkavm/src/api.rs>
  - <https://raw.githubusercontent.com/paritytech/polkavm/190ea5ac10344714b914230974bb9cb12bef56d6/crates/polkavm/src/compiler.rs>
  - <https://github.com/paritytech/polkavm>
  - <https://github.com/paritytech/polkavm/issues>
  - <https://github.com/paritytech/polkavm/issues/413>
  - <https://github.com/paritytech/polkavm/issues/402>
  - <https://github.com/paritytech/polkavm/tree/master/capi>
  - <https://github.com/paritytech/polkavm/tree/master/benches>
  - <https://crates.io/api/v1/crates/polkavm>
  - <https://crates.io/api/v1/crates/polkavm/reverse_dependencies?per_page=20>
  - <https://crates.io/api/v1/crates/polkavm-ffi>
  - <https://crates.io/api/v1/crates/pallet-revive>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/paritytech/polkavm`) · [data/wave12/enrich/raw/github_com_paritytech_polkavm.json](../../../data/wave12/enrich/raw/github_com_paritytech_polkavm.json) (enrichment confidence 0.8)

</details>
