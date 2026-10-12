# revmc (revm AOT/JIT compiler)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> LLVM-based JIT/AOT compiler that turns EVM bytecode into native code for revm; beats the revm interpreter, modestly on real blocks.

| | |
|---|---|
| **Beats** | revm interpreter |
| **Claimed result** | Independent (SkelOT artifact, EuroSys 2027): replay of 10,000 Base mainnet blocks (3,520,323 transactions), exec wall time revm interpreter 534.4 s vs naive per-hash revmc AOT 459.1 s, about 1.16x (derived from page data; mode_reports[0].exec_wall_seconds in data/exec_replay_{interpreter,per_hash}_base.json); single-block smoke test 1.13x to 1.21x. First-party README chart 'REVM Compiler Improvement vs. REVM Interpreter' (Execution Time in microseconds, image only, no CPU or flags): Fibonacci 19.00x, Counter 2.77x, WETH Contract 1.85x. |
| **Workload** | Independent: SkelOT's replay harness executes 10,000 Base mainnet blocks (3.52M transactions) under the revm interpreter and under per-code-hash AOT artifacts compiled by a revmc fork, timing execution only (compilation excluded, objects cached). First-party: Criterion execution time of three contracts (Fibonacci, Counter, WETH) under the revm interpreter versus revmc-compiled code; same-named fixtures (fibonacci-calldata, counter, weth) exist in crates/revmc-cli/src/benches.rs, now run at OSAKA spec by crates/revmc-cli/benches/bench.rs. |
| **Metric** | latency |
| **Hardware** | SkelOT artifact: Intel Xeon Platinum 8275CL @ 3.00 GHz, 16 hardware threads, 30 GiB, Ubuntu 24.04.2. README chart: not stated. |
| **Compiler and flags** | SkelOT artifact: rustc 1.91 rustup channel (patch release recorded as unknown), LLVM 21.1.8 from apt.llvm.org, GNU ld, cargo build --release -p revmc-examples-runner (fork's release profile not checked). README chart: none stated; upstream revmc's release profile is opt-level 3, thin LTO, codegen-units 16, panic abort, and its bench profile inherits a debug=full profiling profile. |
| **Adoption** | 289 stars; integrated into Reth per Paradigm's announcement (search snippet only) |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/paradigmxyz/revmc) · [benchmark](https://github.com/SipengXie2024/skelot-artifact) |

## Verdict

Independently, the SkelOT EuroSys 2027 artifact replayed 10,000 Base mainnet blocks (3.52M transactions) on a Xeon Platinum 8275CL with a revmc fork (rustc 1.91 channel, LLVM 21.1.8): 534.4 s under the revm interpreter vs 459.1 s with naive per-hash AOT, about 1.16x with compilation excluded. First-party, the README bar chart (Criterion, no CPU or flags, June 2024) shows 19.00x on Fibonacci, 2.77x on Counter and 1.85x on WETH over the revm interpreter.

## Use it when

- You already run revm (a Reth-style node, indexer, simulator or replay tool) and execute the same contracts millions of times, so compile cost amortizes.
- Compute-heavy contract code (arithmetic loops, in-EVM hashing, ray tracers like snailtracer): the README chart's 19x is a Fibonacci loop.
- A known hot set of contracts (top-N by usage) that you can AOT-compile ahead of time and preload, avoiding JIT warm-up.
- Linux or macOS hosts where shipping an LLVM 22 dependency (or prebuilt AOT objects) is acceptable.
- Research on EVM compilation: the codebase is the base of at least one academic fork (SkelOT).

## Skip it when

- Storage- or I/O-bound transactions: issue #77 reports only 20-30% for a Uniswap V2 swap under AOT, and SkelOT's 10,000-block Base replay gains about 1.16x overall because most time is outside contract bytecode.
- One-shot or cold execution (RPC eth_call on arbitrary contracts, fuzzing new bytecode): LLVM compilation dwarfs execution; SkelOT's naive per-hash AOT of a Base corpus needed 27,758 s of compile time and 5.05 GB of objects for 19,130 units.
- Windows, or environments without LLVM 22; also contracts above 24 KiB, which the runtime's default jit_max_bytecode_len skips.
- Consensus-critical deployments that cannot tolerate an experimental compiler: June 2026 commits fixed stack sync for diverging builtins (#394), dynamic-gas failure order (#395) and failure-stack materialization (#392), and segfaults were reported in #61 and, for erc20_transfer in AOT mode, #79.
- If you want a faster interpreter without a native code generator: evm2 or evmone are simpler to deploy.

## How it is fast

It removes the interpreter's per-opcode dispatch loop and lets LLVM optimize whole contracts: bytecode analysis resolves dynamic jumps, drops unreachable JUMPDEST blocks, deduplicates identical blocks and runs dead store elimination on the EVM stack. Gas and stack-length checks are batched per section (base gas of a section paid once), branch-weight metadata keeps failure paths cold, gas constants are folded at compile time from the spec's GasParams, and single_error mode collapses all failure paths into one exit so LLVM can delete their materialization. Complex operations (CALL/CREATE with suspend and resume, keccak, host access) go through builtins, so host- and storage-bound code gains little.

## Compared with alternatives

Pick revmc over evm2 or Guillotine when you are committed to revm and your hot contracts are compute-bound enough to repay LLVM compilation; pick evmone or evm2 for interpreter-level gains with no LLVM dependency or warm-up. It is orthogonal to pevm (parallel block execution on revm), which attacks a different bottleneck.

## Integration

| | |
|---|---|
| **Form** | crate (git dependency; the crates.io release is 0.1.0 from 2024-06-27 and does not match main) |
| **Dependencies** | LLVM 22 via inkwell 0.9 (llvm22-1, static or dynamic linking features), revm 43.x crates, alloy-primitives, ruint, rayon, crossbeam, dashmap, libloading, tempfile; optional alloy-evm integration |
| **Minimum toolchain** | Rust 1.95 (workspace rust-version, edition 2024), LLVM 22 |
| **Platforms** | Linux and macOS; Windows unsupported. Supported CPU architectures are not documented in the README (the backend initializes only the native LLVM target). |
| **Thread safety** | Runtime JitBackend: lookups read an immutable resident map, compilation runs on a backend thread plus min(max(1, cpus/2), 4) worker threads (in-process or an out-of-process helper). EvmCompiler is used from one thread, and JIT function pointers live in the compiler's code memory, so the compiler must outlive them. |
| **Drop-in for the baseline** | partial — JitEvm wraps a revm EVM and falls back to the interpreter for uncompiled hashes, but you must compile or AOT-load code, keep compiler memory alive, export revmc-builtins for AOT, and the runtime is disabled by default (enabled: false). |

## Gotchas

- RuntimeConfig.single_error defaults to true: every failure (stack underflow, invalid jump, invalid opcode, real out-of-gas) is reported as OutOfGas, so halt reasons in traces or RPC errors differ from the interpreter's.
- Harness flaw in crates/revmc-cli/benches/bench.rs: each arm reuses one EVM and calls transact_one in a loop without finalize, so journal state accumulates across Criterion iterations (both arms equally), and sanity_check compares only is_success() between interpreter and JIT (not output, gas or state) and is skipped in CodSpeed builds.
- SkelOT's timed interpreter run diverges from its own sanity file (success_count 2,507,504 and total_gas 458,337,083,713 vs 2,511,307 and 458,309,813,705 for both modes in the sanity run); from its per_target data, family-member contracts took 141.6 s vs 93.8 s (1.51x) while the remaining 392.8 s vs 365.3 s gained only 1.075x, and of the 271 members with at least 1,000 timing samples the median ratio is 1.06x with 43% slower under naive per-hash AOT (derived from page data).
- Unsafe API surface: jit_function is unsafe, compiled code is called through raw function pointers, and AOT artifacts carry an ABI_VERSION (currently 0) that must match the runtime.

## Known shortcomings

- README chart (19x Fibonacci, 2.77x Counter, 1.85x WETH vs the revm interpreter) is a PNG with no methodology, CPU or flags and no evmone column. The independent SkelOT EuroSys 2027 artifact (SipengXie2024/skelot-artifact, Base 10k-block replay) gives interpreter 534.4 s vs revmc AOT 459.1 s, about 1.16x, measured on a modified fork with the timed arms differing in success_count and total_gas; the SkelOT paper itself is blocked (arXiv).
- Enricher: RuntimeConfig.single_error defaults to true, so every failure (stack underflow, invalid jump, invalid opcode, real out-of-gas) is reported as OutOfGas. crates/revmc-cli/benches/bench.rs reuses one EVM and calls transact_one in a loop without finalize, so journal state accumulates across iterations, and sanity_check compares only is_success(). SkelOT's timed interpreter run diverges from its own sanity file; from its per_target data, family-member contracts took 141.6 s vs 93.8 s (1.51x) while the rest gained 1.075x, and the median per-contract ratio is 1.06x with 43% slower under naive per-hash AOT (derived from page data). jit_function is unsafe, AOT artifacts carry ABI_VERSION 0; crates.io lags at 0.1.0 (2024).

## Caveats and trade-offs

On real mainnet traffic the gain is small: about 1.16x on a 10,000-block Base replay (independent SkelOT measurement, derived), in line with Paradigm's own 'O(1-10%)' remark for mainnet sync (search snippet only). The 1.85x-19x figures exist only as a README bar-chart image (asset 96adf64b-8513-469d-925d-4f8d902e4e0a, viewed) with no CPU, compiler or flags, from a June 2024 upload; the 19x Fibonacci case is a pure compute loop. The current criterion bench (crates/revmc-cli/benches/bench.rs, codspeed) commits no results, so the chart cannot be matched to a current run. SkelOT measured a modified fork (merge base 4995ac64fb4e, snapshot 9acff128, with bug fixes and a revm API migration), not a revmc release; its timed interpreter and per-hash runs report different success_count (2,507,504 vs 2,511,307) and total_gas (458,337,083,713 vs 458,309,813,705), while the README cites a separate sanity file for zero mismatches. JIT mode pays a compile cost on first execution; LLVM 22 is required, Linux/macOS only. No evmone comparison exists in the repo, chart or paper even though evmone is a listed baseline. BNB Chain blog snippet also quotes 1.85x-19x and up to 6.9x on compute-heavy workloads (snippet only).

Experimental JIT and AOT EVM-to-native compiler built on LLVM (needs LLVM 22, Linux or macOS only, Windows unsupported). AOT-compiled bytecode needs the revmc-builtins runtime exported in the final binary. Compile cost is paid up front (the bench has compile/translate and compile/jit cases).

## Maintenance

Actively maintained (last commit 2026-10-03, tracking revm 43) and dual MIT/Apache-2.0, still labelled experimental; Reth v2.4.0 ships it as opt-in experimental JIT behind --jit flags, but crates.io lags at 0.1.0 (2024), so use a git dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C: the independent SkelOT paper (EuroSys 2027; artifact SipengXie2024/skelot-artifact with harness revmc/examples/runner and scripts/run_stage_replay.sh, raw results data/exec_replay_{interpreter,per_hash}_base.json, Xeon Platinum 8275CL, rustc 1.91 channel, LLVM 21.1.8) measures naive per-hash revmc AOT against the revm interpreter on a 10,000-block Base replay. Not A because the measured code is a modified fork snapshot of revmc (merge base 4995ac64, about 1,900 added lines plus bug fixes and a revm API migration), the rustc patch level is recorded as unknown, and the fork's build profile was not checked; the README chart's 1.85x-19x figures remain first-party with no CPU or flags.
- **Verifier notes:** Chart numbers 19.00x / 2.77x / 1.85x confirmed by viewing the PNG. Tier raised C to B on the independent SkelOT EuroSys 2027 artifact, which shows only about 1.16x on a real Base replay; record that real-world gain and the fork/mismatch caveats as shortcomings. Metadata confirmed on github.com: Apache-2.0 OR MIT, 289 stars, not a fork or archived, last commit 2026-10-03.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** like-for-like replay on unmodified revmc; state-checked replay with per-contract results
- **Pages the verifier opened:**
  - <https://github.com/paradigmxyz/revmc>
  - <https://github.com/paradigmxyz/revmc/commits/main>
  - <https://raw.githubusercontent.com/paradigmxyz/revmc/HEAD/README.md>
  - <https://github.com/paradigmxyz/revmc/assets/17802178/96adf64b-8513-469d-925d-4f8d902e4e0a>
  - <https://raw.githubusercontent.com/paradigmxyz/revmc/HEAD/crates/revmc-cli/benches/bench.rs>
  - <https://raw.githubusercontent.com/paradigmxyz/revmc/HEAD/crates/revmc-cli/src/benches.rs>
  - <https://raw.githubusercontent.com/paradigmxyz/revmc/HEAD/Cargo.toml>
  - <https://github.com/SipengXie2024/skelot-artifact>
  - <https://raw.githubusercontent.com/SipengXie2024/skelot-artifact/HEAD/README.md>
  - <https://raw.githubusercontent.com/SipengXie2024/skelot-artifact/HEAD/data/exec_replay_interpreter_base.json>
  - <https://raw.githubusercontent.com/SipengXie2024/skelot-artifact/HEAD/data/exec_replay_per_hash_base.json>
- **Sources the enricher read:**
  - <https://github.com/paradigmxyz/revmc>
  - <https://github.com/paradigmxyz/revmc/tree/main/crates>
  - <https://github.com/paradigmxyz/revmc/commits/main>
  - <https://github.com/paradigmxyz/revmc/issues?q=is%3Aissue>
  - <https://github.com/paradigmxyz/revmc/issues/77>
  - <https://github.com/paradigmxyz/revmc/issues/79>
  - <https://raw.githubusercontent.com/paradigmxyz/revmc/HEAD/README.md>
  - <https://raw.githubusercontent.com/paradigmxyz/revmc/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/paradigmxyz/revmc/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/paradigmxyz/revmc/HEAD/crates/revmc/Cargo.toml>
  - <https://raw.githubusercontent.com/paradigmxyz/revmc/HEAD/crates/revmc/src/lib.rs>
  - <https://raw.githubusercontent.com/paradigmxyz/revmc/HEAD/crates/revmc-cli/benches/bench.rs>
  - <https://raw.githubusercontent.com/paradigmxyz/revmc/HEAD/crates/revmc-cli/src/benches.rs>
  - <https://raw.githubusercontent.com/paradigmxyz/revmc/HEAD/crates/revmc-cli/src/lib.rs>
  - <https://raw.githubusercontent.com/paradigmxyz/revmc/HEAD/crates/revmc-cli/src/fixture.rs>
  - <https://raw.githubusercontent.com/paradigmxyz/revmc/HEAD/crates/revmc-context/src/lib.rs>
  - <https://raw.githubusercontent.com/paradigmxyz/revmc/HEAD/crates/revmc-context/src/jit_evm.rs>
  - <https://raw.githubusercontent.com/paradigmxyz/revmc/HEAD/crates/revmc-codegen/src/lib.rs>
  - <https://raw.githubusercontent.com/paradigmxyz/revmc/HEAD/crates/revmc-codegen/README.md>
  - <https://raw.githubusercontent.com/paradigmxyz/revmc/HEAD/crates/revmc-runtime/README.md>
  - <https://raw.githubusercontent.com/paradigmxyz/revmc/HEAD/crates/revmc-runtime/Cargo.toml>
  - <https://raw.githubusercontent.com/paradigmxyz/revmc/HEAD/crates/revmc-runtime/src/lib.rs>
  - <https://raw.githubusercontent.com/paradigmxyz/revmc/HEAD/crates/revmc-runtime/src/runtime/mod.rs>
  - <https://raw.githubusercontent.com/paradigmxyz/revmc/HEAD/crates/revmc-runtime/src/runtime/config.rs>
  - <https://raw.githubusercontent.com/paradigmxyz/revmc/HEAD/crates/revmc-llvm/Cargo.toml>
  - <https://crates.io/api/v1/crates/revmc>
  - <https://raw.githubusercontent.com/SipengXie2024/skelot-artifact/HEAD/README.md>
  - <https://raw.githubusercontent.com/SipengXie2024/skelot-artifact/HEAD/data/exec_replay_interpreter_base.json>
  - <https://raw.githubusercontent.com/SipengXie2024/skelot-artifact/HEAD/data/exec_replay_per_hash_base.json>
  - <https://github.com/paradigmxyz/reth/releases>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/paradigmxyz/revmc`) · [data/wave12/enrich/raw/github_com_paradigmxyz_revmc.json](../../../data/wave12/enrich/raw/github_com_paradigmxyz_revmc.json) (enrichment confidence 0.8)

</details>
