# evm2 (alloy-rs)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Customizable Rust EVM from alloy-rs with a tail-call, static-table interpreter; claims up to 2x over revm, unpublished numbers.

| | |
|---|---|
| **Beats** | revm (Rust EVM interpreter) |
| **Claimed result** | README: 'up to 2x faster than revm from a tighter interpreter, static dispatch tables, and cheaper instruction plumbing'. |
| **Workload** | EVM bytecode execution; the README does not say which workloads back the 'up to 2x' claim. The public Criterion harness crates/cli/benches/evm.rs runs 21 transaction fixtures (fibonacci-calldata, factorial, counter, snailtracer, weth, hash_10k, erc20_transfer, push0_proxy, usdc_proxy, fiat_token, uniswap_v2_pair, univ2_router, seaport, airdrop, bswap64, bswap64_opt, eip4788, eip2935, burntpix, curve_stableswap, onchain_lm_v2) plus a mainnet block-range replay (blocks 25347446-25347455), and adds revm runs of the same cases when EVM2_BENCH_REVM=1 is set. |
| **Metric** | throughput |
| **Compiler and flags** | CI builds with cargo codspeed build --profile profiling (inherits release: opt-level 3, panic=abort, plus full debug info) and runs CodSpeed in simulation mode; the cargo bench profile adds lto=thin and codegen-units=1. Flags and toolchain behind the README claim are not stated. |
| **Adoption** | 72 stars (alloy-rs/evm2) |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/alloy-rs/evm2) · [benchmark](https://github.com/alloy-rs/evm2) |

## Verdict

The only claim is a first-party README line, 'up to 2x faster than revm', with no table, workloads, hardware, toolchain, backend or revm version. The repo carries a Criterion harness that runs revm 43 next to evm2 on 21 transaction fixtures and a 10-block mainnet replay when EVM2_BENCH_REVM=1 is set, but CI does not set it and no output is published.

## Use it when

- Building a custom EVM chain or L2 in Rust that needs extra opcodes, precompiles, tx types or gas rules without forking an interpreter.
- Throughput-bound single-threaded execution (simulation, replay, block building) where you can run the repo's own revm comparison (EVM2_BENCH_REVM=1 cargo bench -p evm2-cli --bench evm) on your hardware first.
- Projects already on a nightly toolchain, which unlocks the tail-call interpreter backend.
- Experiments with EVM JIT/AOT compilation via the bundled evm2-jit crate (LLVM 22, Linux or macOS).

## Skip it when

- Consensus-critical production nodes: consensus-rule fixes are still landing weekly (Oct 2026 PRs on EIP-4844 and EIP-7702 validation order, upfront gas saturation, invalid-opcode halts in issue #386).
- Code that needs a crates.io release or semver stability: the crate is version 0.1.0, not published on crates.io, and the MSRV (1.96) follows the latest stable Rust.
- Many EVM instances in parallel threads: issue #542 (open) shows a process-wide shared Arc for empty Bytecode causing atomic contention, with 30-CPU scaling of only 2.1x (BLAKE2F) to 6.5x (KECCAK256).
- Stacks built on revm types and tooling (Foundry, Reth inspectors, revm-based L2 handlers): evm2 is not API-compatible.
- Windows users of the JIT, which the LLVM backend does not support.

## How it is fast

Opcode handlers are monomorphized into a 256-entry dispatch table per EvmConfig and inspect mode at compile time, so inspector hooks and disabled opcodes cost nothing on the plain path. On nightly rustc, build.rs selects a tail-call threaded interpreter (explicit_tail_calls plus the preserve_none calling convention): each handler takes pc, stack pointer and remaining gas as arguments and jumps straight to the next handler; stable 64-bit builds get a 'packed' table loop instead. Static gas is charged in a pre-step with an unchecked pc advance, and jump-destination analysis is SIMD and lazy (PRs #498 and #492; the SIMD analysis was later ported to revm). Precompiles default to native backends (asm Keccak, libsecp256k1, GMP modexp, blst, MCL BN254, AWS-LC P256).

## Compared with alternatives

Pick evm2 over revm (catalogued) for a new Rust EVM variant where interpreter speed matters and you can validate correctness and speed yourself; stay on revm for production maturity and ecosystem compatibility. evmone (C++) is the measured leader on evm-bench and remains the choice for C/C++ hosts via EVMC; no independent run places evm2 against evmone or Guillotine.

## Integration

| | |
|---|---|
| **Form** | crate (git dependency; not on crates.io as of 2026-10-06) |
| **Dependencies** | alloy-primitives, alloy-consensus, alloy-eips and related alloy crates; default features also pull C/asm backends: libsecp256k1, GMP (gmp-mpfr-sys), blst, MCL, AWS-LC (aws-lc-rs), asm Keccak. JIT needs LLVM 22. |
| **Minimum toolchain** | Rust 1.96 (edition 2024); nightly rustc enables the tail-call backend automatically |
| **Platforms** | Any Rust target; no_std with default-features = false; tail-call backend not used on wasm or with the Cranelift codegen backend; JIT Linux and macOS only |
| **Thread safety** | Not documented; issue #542 reports cross-thread atomic contention on a shared empty-bytecode Arc when EVMs run in parallel. |
| **Drop-in for the baseline** | no |

## Gotchas

- Interpreter backend depends on the compiler: build.rs picks the tail-call backend only on nightly rustc (overridable with EVM2_DISPATCH_BACKEND), and the CI CodSpeed job builds with stable, so tracked numbers use the packed table loop. The README does not say which backend, toolchain or revm version produced 'up to 2x'.
- Harness flaw in crates/cli/benches/evm: the transaction cases are not symmetric. evm2 deep-clones its fully populated InMemoryDB in untimed setup and times transact plus commit, while revm runs on a fresh CacheDB over Arc&lt;InMemoryDB&gt;, so each first-touch account and storage slot is a cache miss plus HashMap insert inside the timed region (and tx.clone() is timed); revm does not commit. This inflates revm's time most on short transactions such as erc20_transfer.
- The 21 transaction fixtures have no cross-engine parity check: sanity_check only asserts the call returned Ok, and revm returns Ok for reverted or halted transactions. Only the 10-block mainnet replay diffs gas, success, logs and receipt roots between evm2 and revm (PR #527), and that case times evm2 through the EEST executor but revm through a separate hand-written replay loop.
- Heavy unsafe in the hot path (lifetime-erasing raw pointers in the trustme module, unchecked pc advance), which relies on bytecode padding and analysis invariants.

## Known shortcomings

- Only a headline 'up to 2x vs revm' with no table, hardware or revm version; the public revm harness (crates/cli/benches/evm.rs) runs the comparison only with EVM2_BENCH_REVM=1, which the CI CodSpeed run does not set. Off-baseline (revm); Rust EVM, not a wasm runtime.
- Enricher: in crates/cli/benches/evm the evm2 arm clones the full InMemoryDB in untimed setup and times transact plus commit while revm runs on a fresh CacheDB over Arc&lt;InMemoryDB&gt;, so first-touch account and slot misses and tx.clone() fall in revm's timed region and revm does no commit; the 21 transaction fixtures have no cross-engine parity check (sanity_check only asserts Ok, which revm returns on revert or halt); the tail-call backend is auto-selected only on nightly rustc while CI CodSpeed builds stable, and the README never says which backend produced 'up to 2x'. Version 0.1.0, not on crates.io; open issue #542 (shared empty-Bytecode Arc contention, 30-CPU scaling 2.1x-6.5x); consensus fixes still landing (PRs #537-#539, #518).

## Caveats and trade-offs

Only the headline 'up to 2x' is given; no table, workload list, hardware or revm version backs it in the README. The CI CodSpeed workflow (.github/workflows/bench.yml) does not set EVM2_BENCH_REVM, so its dashboard tracks evm2 alone, not the revm comparison; codspeed.io is also blocked from this environment. 'Up to' means best case. The comparison can be reproduced locally with EVM2_BENCH_REVM=1 cargo bench -p evm2-cli --bench evm, but no published output exists.

Rust EVM built for custom specs, opcodes and precompiles; has an interpreter with a tail-call backend (no-tco feature disables it) and a separate jit crate.

## Maintenance

Very active under alloy-rs (last commit 2026-10-05, 619 commits, 72 stars, MIT OR Apache-2.0), but pre-release (0.1.0, not on crates.io) with consensus fixes still landing; treat as experimental.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The README gives only a first-party headline 'up to 2x faster than revm' with no table, workloads, hardware or revm version. Public comparison code exists (crates/cli/benches/evm.rs runs revm side by side when EVM2_BENCH_REVM is set), but no results from it are published, so C.
- **Verifier notes:** Claim text matches the README verbatim; repo is original (not a fork), Apache-2.0 OR MIT, 72 stars, last commit 2026-10-05. Main shortcoming: unsubstantiated 'up to 2x' headline with no published numbers, though a public revm-vs-evm2 Criterion harness exists that an enricher could cite.
- **Fields the verifier corrected:** `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/alloy-rs/evm2>
  - <https://github.com/alloy-rs/evm2/commits>
  - <https://github.com/alloy-rs/evm2/tree/main/crates>
  - <https://github.com/alloy-rs/evm2/tree/main/crates/cli>
  - <https://github.com/alloy-rs/evm2/tree/main/crates/cli/benches>
  - <https://raw.githubusercontent.com/alloy-rs/evm2/HEAD/README.md>
  - <https://raw.githubusercontent.com/alloy-rs/evm2/HEAD/.github/workflows/bench.yml>
  - <https://raw.githubusercontent.com/alloy-rs/evm2/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/alloy-rs/evm2/HEAD/crates/cli/Cargo.toml>
  - <https://raw.githubusercontent.com/alloy-rs/evm2/HEAD/crates/cli/benches/evm.rs>
  - <https://raw.githubusercontent.com/alloy-rs/evm2/HEAD/crates/cli/src/evm_bench.rs>
  - <https://github.com/alloy-rs/evm2/pull/496>
- **Sources the enricher read:**
  - <https://github.com/alloy-rs/evm2>
  - <https://raw.githubusercontent.com/alloy-rs/evm2/HEAD/README.md>
  - <https://raw.githubusercontent.com/alloy-rs/evm2/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/alloy-rs/evm2/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/alloy-rs/evm2/HEAD/.github/workflows/bench.yml>
  - <https://raw.githubusercontent.com/alloy-rs/evm2/HEAD/crates/cli/Cargo.toml>
  - <https://raw.githubusercontent.com/alloy-rs/evm2/HEAD/crates/cli/benches/evm.rs>
  - <https://raw.githubusercontent.com/alloy-rs/evm2/HEAD/crates/cli/benches/evm/support.rs>
  - <https://raw.githubusercontent.com/alloy-rs/evm2/HEAD/crates/cli/benches/evm/revm.rs>
  - <https://raw.githubusercontent.com/alloy-rs/evm2/HEAD/crates/cli/benches/evm/fixture.rs>
  - <https://raw.githubusercontent.com/alloy-rs/evm2/HEAD/crates/cli/benches/evm/mainnet.rs>
  - <https://raw.githubusercontent.com/alloy-rs/evm2/HEAD/crates/cli/benches/evm/mainnet_revm.rs>
  - <https://raw.githubusercontent.com/alloy-rs/evm2/HEAD/crates/cli/benches/evm/jit.rs>
  - <https://raw.githubusercontent.com/alloy-rs/evm2/HEAD/crates/cli/src/evm_bench.rs>
  - <https://raw.githubusercontent.com/alloy-rs/evm2/HEAD/crates/cli/src/replay_bench.rs>
  - <https://raw.githubusercontent.com/alloy-rs/evm2/HEAD/crates/cli/src/lib.rs>
  - <https://raw.githubusercontent.com/alloy-rs/evm2/HEAD/crates/evm2/Cargo.toml>
  - <https://raw.githubusercontent.com/alloy-rs/evm2/HEAD/crates/evm2/build.rs>
  - <https://raw.githubusercontent.com/alloy-rs/evm2/HEAD/crates/evm2/src/lib.rs>
  - <https://raw.githubusercontent.com/alloy-rs/evm2/HEAD/crates/evm2/src/interpreter/dispatch/mod.rs>
  - <https://raw.githubusercontent.com/alloy-rs/evm2/HEAD/crates/evm2/src/interpreter/dispatch/tco.rs>
  - <https://raw.githubusercontent.com/alloy-rs/evm2/HEAD/crates/jit/README.md>
  - <https://github.com/alloy-rs/evm2/tree/main/crates/evm2/src/interpreter>
  - <https://github.com/alloy-rs/evm2/tree/main/crates/evm2/src/interpreter/dispatch>
  - <https://github.com/alloy-rs/evm2/issues?q=is%3Aissue>
  - <https://github.com/alloy-rs/evm2/issues/542>
  - <https://github.com/alloy-rs/evm2/pull/496>
  - <https://github.com/alloy-rs/evm2/pulls?q=is%3Apr+revm>
  - <https://crates.io/api/v1/crates/evm2>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/alloy-rs/evm2`) · [data/wave12/enrich/raw/github_com_alloy_rs_evm2.json](../../../data/wave12/enrich/raw/github_com_alloy_rs_evm2.json) (enrichment confidence 0.65)

</details>
