# revm

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `MIT` · 🟢 active

> The standard Rust EVM; about 2.8x faster than Geth's EVM on evm-bench, but slower than C++ evmone.

| | |
|---|---|
| **Beats** | go-ethereum (Geth) EVM, py-evm and ethereumjs |
| **Claimed result** | evm-bench README table, sum of five workloads: revm 84.8 ms, Geth 235 ms, pyrevm 194 ms, py-evm on PyPy 7.201 s, py-evm on CPython 19.0886 s, ethereumjs 146.3218 s; so revm is about 2.8x faster than Geth (derived from page data). evmone, the C++ EVM, is faster still at 66 ms (revm is 1.285x evmone). |
| **Workload** | evm-bench Solidity workloads: erc20 approval-transfer, mint and transfer, snailtracer and ten-thousand-hashes, summed per runner. |
| **Metric** | latency |
| **Compiler and flags** | revm runner launched with cargo run -r (release profile defaults); Geth runner launched with go run (Go 1.19 module); CPU, toolchain versions and runner versions used for the 2022-12-17 table are not stated. |
| **Adoption** | 2.2k stars; used by Reth, Foundry, Optimism and Risc0 |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/bluealloy/revm) · [benchmark](https://github.com/ziyadedher/evm-bench) |

## Verdict

Third-party evm-bench (Ziyad Edher) table dated 2022-12-17, summed over five Solidity workloads: revm 84.8 ms vs Geth 235 ms, about 2.8x faster (derived from page data); per workload from 1.8x (ERC-20 approval-transfer, 9.6 vs 17 ms) to 3.1x (ten-thousand-hashes, 4.2 vs 13.2 ms; snailtracer 53 vs 163 ms), with evmone at 66 ms. revm was built with cargo run -r and Geth with go run; CPU, compiler versions and the revm version are not stated.

## Use it when

- A Rust codebase that needs a production EVM for block building, transaction simulation, tracing, testing (Foundry-style) or zkVM guests.
- Replacing go-ethereum's EVM in a non-Go stack where 2-3x interpreter speed matters: evm-bench shows 1.8x (ERC-20 approval-transfer) up to 3.1x (ten-thousand-hashes) over Geth.
- Building an L2 or custom chain that needs handler hooks, custom precompiles or custom opcodes on a widely audited base.
- When ecosystem compatibility matters: Reth, Foundry, Optimism, Risc0 and Succinct all build on it.

## Skip it when

- Maximum single-thread interpreter speed in a C or C++ host: evmone is 1.285x faster on the same evm-bench table (66 ms vs 84.8 ms).
- Code that needs a stable API: majors arrive every month or two (42.0.0 in July 2026, 43.0.0 on 2026-08-26), and the MSRV (1.91.0) follows recent stable Rust.
- Parallel block execution out of the box: revm executes sequentially; parallel layers such as pevm build on top of it.
- Pure Go stacks, where Geth avoids an FFI boundary and its overhead.

## How it is fast

A central loop dispatches each opcode through a 256-entry function-pointer instruction table, charging static gas from a separate gas table with an unchecked subtraction before the call. Legacy bytecode is padded so the trailing byte is STOP, which lets the program counter advance without bounds checks, and the JUMPDEST bitmap is computed once per contract with SIMD scanning on x86 and aarch64 (scalar fallback). Memory is a shared buffer reused across call frames, and release builds use thin LTO and panic=abort. An optional LLVM JIT (revmc) lives in a separate repo and is not part of the measured numbers.

## Compared with alternatives

Pick revm over evmone when the host is Rust and you need the framework (handlers, inspectors, L2 variants) or Reth/Foundry compatibility; pick evmone for the fastest measured interpreter in a C/C++ host. evm2 claims up to 2x over revm and Guillotine's own table shows it matching or beating revm on some cases, but both are young, so revm stays the choice for production maturity.

## Integration

| | |
|---|---|
| **Form** | crate (crates.io revm 43.0.3, about 9.9M downloads) |
| **Dependencies** | alloy primitives and related crates; default features also pull secp256k1 (libsecp256k1), c-kzg and blst C libraries plus the tracer feature; std is a feature, so no_std works with default-features = false |
| **Minimum toolchain** | Rust 1.91.0 (rust-version of 43.0.3) |
| **Platforms** | Any Rust target; SIMD jumpdest analysis on x86/x86-64 and aarch64 with scalar fallback elsewhere |
| **Thread safety** | Not documented in the README; each Evm owns its Context and database, and the repo does not document sharing one instance across threads. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw in evm-bench: the revm runner times only Interpreter::run of the deployed contract against revm's DummyHost (a mock host with an in-memory storage map, cleared after each run), while the Geth runner times a full evm.Call against a real StateDB with snapshot and revert. Geth's rows therefore include host and state-journal costs that revm's rows skip, so the 2.8x overstates the gap for full-transaction execution by an unknown amount.
- The runner code in the repo is not the code behind the table: the table was last updated 2022-12-17, but the revm runner now pins revm-interpreter rev 3fda52e with clap 4.5.3 (a 2024 bump), Geth is pinned at v1.10.25, and no CPU or toolchain is recorded. revm has gone through dozens of major versions since.
- Open issue #3776 (June 2026): Miri found undefined behavior reachable through safe public bytecode cursor APIs in revm-interpreter 35.0.1 (Jumps::absolute_jump and relative_jump, Immediates::read_u16, read_offset_u16/i16, read_slice) when callers pass out-of-range offsets; the normal interpreter keeps the invariants, but custom instruction code calling these APIs can trigger it.
- The framework API changes between majors (Context, Handler and Inspector traits were reworked), so code written against older revm examples often does not compile on 43.x.

## Known shortcomings

- evm-bench table dated 2022-12-17 against Geth v1.10.25 with no CPU or versions; the runners are asymmetric (revm's bare Interpreter with a DummyHost against Geth's evm.Call with state), and evmone is faster in the same table. Off-baseline (Geth); Rust EVM.
- Enricher: the evm-bench revm runner times a bare Interpreter::run on a DummyHost (mock storage) while the Geth runner times a full evm.Call on a real StateDB with snapshot, so the 2.8x overstates the full-transaction gap; the runner in the repo (rev 3fda52e, clap 4.5.3) postdates the 2022-12-17 table; open miri undefined-behaviour issue #3776 in the bytecode cursor APIs; evmone is 1.285x faster in the same table.

## Caveats and trade-offs

Third-party suite (evm-bench by Ziyad Edher, GPL-3.0, 225 stars) with public code but no CPU, compiler flags or runner versions on the README. The results table was last updated 2022-12-17 (README commit 'Update benchmark times') and the repo's last commit is 2024-03-19 (dependency bumps), so the numbers are close to four years old; the Geth runner pins go-ethereum v1.10.25 and the current revm runner pins revm-interpreter at git rev 3fda52e, while the revm version behind the 2022 table is not recorded. The runners measure different scopes: the current revm runner times the bare revm Interpreter against a DummyHost, while the Geth runner times evm.Call against a state database, so host and state overhead is not equal across rows. evmone, the C++ EVM, is faster still at 66 ms (revm takes 1.285x evmone's time) and is already catalogued; this entry is the revm-versus-Geth evidence.

Rust EVM built as a customizable execution framework (hooks, custom specs), not only an interpreter; it is slower than evmone and the benchmark does not cover its experimental revmc JIT.

## Maintenance

Very active (last commit 2026-10-01, 43.0.3 released 2026-09-24, 2.2k stars, 2,535 commits), MIT-licensed and the de facto Rust EVM; production-ready, but expect breaking changes each major.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party suite (ziyadedher/evm-bench, public benchmark and runner code) whose README table shows revm 84.8 ms vs Geth 235 ms summed over five Solidity workloads; no CPU, toolchain versions or flags are stated, so not A.
- **Verifier notes:** Numbers match the evm-bench README exactly (revm 84.8 ms, Geth 235 ms, about 2.8x derived). Shortcomings: table dated 2022-12-17 with old Geth v1.10.25, no hardware or versions, asymmetric runners (revm bare interpreter with DummyHost vs Geth evm.Call with state), evmone faster; baseline Geth is not one of the category's listed baselines.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/README.md>
  - <https://github.com/ziyadedher/evm-bench>
  - <https://github.com/ziyadedher/evm-bench/commits/main>
  - <https://github.com/ziyadedher/evm-bench/commits/main/README.md>
  - <https://github.com/ziyadedher/evm-bench/commits/main/runners/revm>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/runners/revm/Cargo.toml>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/runners/revm/entry.sh>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/runners/revm/src/main.rs>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/runners/geth/go.mod>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/runners/geth/entry.sh>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/runners/geth/runner.go>
  - <https://github.com/bluealloy/revm>
  - <https://github.com/bluealloy/revm/commits/main>
- **Sources the enricher read:**
  - <https://github.com/bluealloy/revm>
  - <https://raw.githubusercontent.com/bluealloy/revm/HEAD/README.md>
  - <https://raw.githubusercontent.com/bluealloy/revm/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/bluealloy/revm/HEAD/crates/revm/Cargo.toml>
  - <https://raw.githubusercontent.com/bluealloy/revm/HEAD/crates/interpreter/Cargo.toml>
  - <https://raw.githubusercontent.com/bluealloy/revm/HEAD/crates/interpreter/src/interpreter.rs>
  - <https://raw.githubusercontent.com/bluealloy/revm/HEAD/crates/interpreter/src/instructions.rs>
  - <https://raw.githubusercontent.com/bluealloy/revm/HEAD/crates/bytecode/src/legacy/analysis.rs>
  - <https://github.com/bluealloy/revm/tree/main/crates/bytecode/src>
  - <https://github.com/bluealloy/revm/security/advisories>
  - <https://github.com/bluealloy/revm/issues?q=is%3Aissue+performance>
  - <https://github.com/bluealloy/revm/issues/3776>
  - <https://github.com/bluealloy/revm/issues/2363>
  - <https://crates.io/api/v1/crates/revm>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/runners/revm/src/main.rs>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/runners/revm/Cargo.toml>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/runners/geth/runner.go>
  - <https://github.com/risechain/pevm>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/bluealloy/revm`) · [data/wave12/enrich/raw/github_com_bluealloy_revm.json](../../../data/wave12/enrich/raw/github_com_bluealloy_revm.json) (enrichment confidence 0.75)

</details>
