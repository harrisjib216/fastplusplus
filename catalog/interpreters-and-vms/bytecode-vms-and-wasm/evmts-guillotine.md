# Guillotine (evmts)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig` · `MIT` · 🟡 stale

> Early-alpha Zig EVM interpreter with tail-call threaded dispatch; first-party runs show it 1.05-1.48x faster than REVM, about level with evmone.

| | |
|---|---|
| **Beats** | REVM (Rust EVM interpreter) and Geth EVM |
| **Claimed result** | README table, ms per run, Guillotine vs REVM vs Geth vs evmone: erc20-approval-transfer 1.59/1.67/3.65/1.56; erc20-mint 4.28/5.76/12.84/4.26; erc20-transfer 6.65/8.30/17.50/6.01; ten-thousand-hashes 2.46/3.31/9.36/2.90; snailtracer 26.41/39.01/86.02/27.15. So about 1.05x to 1.48x faster than REVM and 2.3x to 3.8x faster than Geth (derived from page data); on par with evmone (slower on 3 of 5 rows). |
| **Workload** | evm-bench test cases (erc20-approval-transfer, erc20-mint, erc20-transfer, ten-thousand-hashes, snailtracer) timed with hyperfine per run. |
| **Metric** | latency |
| **Adoption** | 170 stars |
| **Last commit** | 2026-01-04 |
| **Links** | [repository](https://github.com/evmts/guillotine) · [benchmark](https://github.com/evmts/guillotine) |

## Verdict

First-party README table: evm-bench workloads timed with hyperfine, ms per run, on unstated hardware and flags, showing Guillotine 1.05-1.48x faster than REVM, 2.3-3.8x faster than Geth and within about 10% of evmone (slower on 3 of 5 rows). The successor evm-benchmarks results.md (1 run per process, startup not subtracted, no result check) shows native Guillotine 1.03-1.8x faster than REVM on 33 rows that are mostly 1-2 ms.

## Use it when

- Research or experiments on EVM interpreter design in Zig, especially dispatch, opcode fusion and comptime-configured EVM variants.
- Embedding an EVM in a Zig program where a C-ABI or Wasm build with a small footprint matters (README: 119 KB core EVM at ReleaseSmall without precompiles).
- Compute-bound, single-call contract execution on mainnet rules (snailtracer-style loops, hashing) where the first-party numbers show about 1.3-1.5x over REVM, if you can verify the results yourself.
- Building custom EVM variants (added or overridden opcodes and precompiles) without Rust generics and feature flags.

## Skip it when

- Anything that must be consensus-correct: the README says DO NOT USE IN PRODUCTION and reports 1165 of 2251 Ethereum spec tests passing (about 52%, most failures in ecmul/BN254).
- Production pipelines that need a maintained, audited engine: no commits since 2026-01-04, the repo says it is in flux, and the team now describes evmts/guillotine-mini as its spec-compliant core engine.
- Linux or Windows builds without extra work: building is documented for macOS only and pins Zig 0.15.1 exactly plus a Rust toolchain for the crypto dependencies.
- Browser or Wasm use expecting native speed: the dispatch code turns off forced tail calls on wasm32/wasm64, and the Bun SDK rows in results.md are 15-20 ms against 1-2 ms native.
- OP Stack or Arbitrum chains: only Ethereum mainnet is supported.

## How it is fast

Before running a frame it preprocesses the bytecode into a dispatch schedule of handler pointers with inline metadata, folding common sequences into synthetic fused opcodes (PUSH_ADD_INLINE and similar) and batching static gas and stack-height checks per basic block, then executes it with indirect threading through Zig's always_tail calls so each handler jumps straight to the next. It adds a hand-tuned stack, comptime removal of unused features, and assembly Keccak (keccak-asm).

## Compared with alternatives

evmone (C++) matches or beats it on 3 of 5 README rows and is spec-compliant, and revm is the maintained Rust standard used across the ecosystem, so pick either for real work; pick Guillotine only for a Zig-native, comptime-configurable EVM experiment. evm2 (alloy-rs) is the sibling to watch if you need more than REVM speed in Rust.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | arkworks (Rust, elliptic curves), c-kzg-4844, keccak-asm, Zig std crypto; build-time zBench and zig-clap; FFI SDKs for Go, Rust, Bun, C, TypeScript |
| **Minimum toolchain** | Zig 0.15.1 exactly, Rust 1.75+ |
| **Platforms** | macOS documented; Linux planned; wasm32 build without forced tail calls |
| **Thread safety** | not documented; each Evm instance holds a mutable journal, call arena and database pointer, so use one instance per thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw (evmts/evm-benchmarks, where the README says the benchmarks moved): src/guillotine_runner.zig calls evm.simulate and discards the result, never checking success, gas used or output, and main.zig only parses hyperfine means, so nothing confirms Guillotine and REVM did the same work; with about 48% of spec tests failing, a run that halts early would still be timed as fast. results.md itself admits the FFI runners fail on several rows (shown as 0.00 ms).
- Harness flaw: the evm-benchmarks README says startup overhead is measured and subtracted, but runBenchmarkWithResult ignores the overhead argument and internal_runs is hard-coded to 1, so the 1-2 ms rows in results.md are whole-process times (process start, hex-decoding the bytecode from argv, database setup) comparing a Zig binary with a Rust clap binary; the same README's example output has REVM 1.44x faster than Guillotine on factorial.
- Build asymmetry: REVM is built with plain cargo --release and default features, without its optional asm-keccak feature, while Guillotine uses assembly Keccak, which favours Guillotine on hash-heavy rows such as ten-thousand-hashes.
- The README table (with evmone and Geth) comes from an evm-bench harness that now lives only in old commits, with no CPU, flags or versions; evm.zig rebuilds the dispatch schedule for every frame with no caching, so call-heavy workloads pay preprocessing on each CALL.

## Known shortcomings

- README numbers have no CPU or flags; alpha with 1086 of 2251 spec tests failing; the evm-benchmarks results.md shows 1.03x-1.8x over REVM but most rows are about 1-2 ms (startup-dominated) and do not match the README. Off-baseline (REVM); Zig EVM.
- Enricher: in evmts/evm-benchmarks guillotine_runner.zig calls simulate and discards the result (no success, gas or output check, with a 52% spec pass rate), the README says startup is subtracted but runBenchmarkWithResult ignores the overhead with internal_runs hard-coded to 1 (so the 1-2 ms rows are whole-process times), REVM is built without asm-keccak while Guillotine uses keccak-asm, and the Wasm build drops forced tail calls. The repo has been idle since 2026-01-04 (the team now builds evmts/guillotine-mini).

## Caveats and trade-offs

First-party table with no CPU, compiler flags or versions; the harness was moved to the first-party evmts/evm-benchmarks repo. That repo's README example output shows REVM fastest on factorial (Guillotine 1.44x slower), while its generated results.md (1 internal run per benchmark, no hardware stated) shows native Guillotine faster than REVM on all 33 rows by 1.03x to 1.8x (derived from page data); most rows there are about 1-2 ms, so process startup likely dominates, and its ten-thousand-hashes time (7.46 ms) does not match the README table (2.46 ms). The README says it is on par with evmone, not faster (slower on 3 of 5 rows). Early alpha marked DO NOT USE IN PRODUCTION: 1165 of 2251 Ethereum spec tests pass (about 52%, most failures in ecmul/BN254), and the repo is 'in flux' being refactored, so the speed may omit work a conforming EVM must do. Build documented for macOS only. [retier] README numbers have no CPU or flags; alpha with 1086 of 2251 spec tests failing (52% pass). In evmts/evm-benchmarks, guillotine_runner.zig calls simulate and discards the result (no success, gas or output check), runBenchmarkWithResult ignores the startup overhead the README says is subtracted with internal_runs hard-coded to 1, so the 1-2 ms rows (1.03x-1.8x over REVM in results.md, not matching the README) are whole-process times; REVM is built without asm-keccak while Guillotine uses keccak-asm; the Wasm build drops forced tail calls. Idle since 2026-01-04, development moved to evmts/guillotine-mini. Off-baseline (REVM); Zig EVM.

Early-alpha Zig EVM with comptime-configurable features; the repo page reports about 48% of its own tests failing (mostly elliptic-curve precompiles) and says it is being refactored.

## Maintenance

MIT and 170 stars, but early alpha (about 52% spec-test pass rate), idle since 2026-01-04 while the team builds a full client on evmts/guillotine-mini, macOS-only build, so treat it as a reference design rather than a library to depend on.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The README table (evm-bench cases timed with hyperfine) lists Guillotine, REVM, Geth and evmone with exactly the numbers in the record, but gives no CPU, compiler flags or versions, and the harness lives only in old commits and the separate first-party evmts/evm-benchmarks repo. First-party with partial methodology, so C.
- **Verifier notes:** Numbers and derived ratios check out (1.05x to 1.48x vs REVM, 2.3x to 3.8x vs Geth). Repo MIT, 170 stars, not a fork, last commit 2026-01-04 (active). Main shortcomings: alpha with \~48% of spec tests failing, no hardware or flags, inconsistent numbers between README and the evm-benchmarks results.md.
- **Fields the verifier corrected:** `caveats`, `maintenance_status`
- **Pages the verifier opened:**
  - <https://github.com/evmts/guillotine>
  - <https://github.com/evmts/guillotine/commits>
  - <https://raw.githubusercontent.com/evmts/guillotine/HEAD/README.md>
  - <https://github.com/evmts/evm-benchmarks>
  - <https://raw.githubusercontent.com/evmts/evm-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/evmts/evm-benchmarks/HEAD/results.md>
- **Sources the enricher read:**
  - <https://github.com/evmts/guillotine>
  - <https://github.com/evmts/guillotine/commits>
  - <https://github.com/evmts/guillotine/tree/main/bench>
  - <https://github.com/evmts/guillotine/issues?q=is%3Aissue+benchmark>
  - <https://raw.githubusercontent.com/evmts/guillotine/HEAD/README.md>
  - <https://raw.githubusercontent.com/evmts/guillotine/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/evmts/guillotine/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/evmts/guillotine/HEAD/src/evm.zig>
  - <https://raw.githubusercontent.com/evmts/guillotine/HEAD/src/root.zig>
  - <https://raw.githubusercontent.com/evmts/guillotine/HEAD/src/preprocessor/dispatch.zig>
  - <https://raw.githubusercontent.com/evmts/guillotine/HEAD/bench/evm_fixture_benchmarks.zig>
  - <https://raw.githubusercontent.com/evmts/guillotine/HEAD/bench/evm_benchmarks.zig>
  - <https://raw.githubusercontent.com/evmts/guillotine/HEAD/bench/evm_benchmarks_simple.zig>
  - <https://raw.githubusercontent.com/evmts/guillotine/HEAD/bench/build.zig>
  - <https://raw.githubusercontent.com/evmts/evm-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/evmts/evm-benchmarks/HEAD/results.md>
  - <https://raw.githubusercontent.com/evmts/evm-benchmarks/HEAD/src/main.zig>
  - <https://raw.githubusercontent.com/evmts/evm-benchmarks/HEAD/src/guillotine_runner.zig>
  - <https://raw.githubusercontent.com/evmts/evm-benchmarks/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/evmts/evm-benchmarks/HEAD/src/revm_executor.rs>
  - <https://raw.githubusercontent.com/evmts/evm-benchmarks/HEAD/src/evm.rs>
  - <https://raw.githubusercontent.com/evmts/evm-benchmarks/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/evmts/evm-benchmarks/HEAD/build.zig>
  - <https://raw.githubusercontent.com/evmts/evm-benchmarks/HEAD/run.sh>
  - <https://raw.githubusercontent.com/evmts/evm-benchmarks/HEAD/fixtures/factorial.json>
  - <https://raw.githubusercontent.com/evmts/evm-benchmarks/HEAD/fixtures/snailtracer.json>
  - <https://raw.githubusercontent.com/evmts/evm-benchmarks/HEAD/fixtures/ten-thousand-hashes.json>
  - <https://raw.githubusercontent.com/evmts/evm-benchmarks/HEAD/fixtures/erc20transfer.json>
  - <https://raw.githubusercontent.com/bluealloy/revm/HEAD/crates/revm/Cargo.toml>
  - <https://github.com/evmts/guillotine-mini>
  - <https://raw.githubusercontent.com/evmts/guillotine-mini/HEAD/README.md>
  - <https://gist.github.com/roninjin10/5dd988c2a95f01ef8c885a809f9f2396>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/evmts/guillotine`) · [data/wave12/enrich/raw/github_com_evmts_guillotine.json](../../../data/wave12/enrich/raw/github_com_evmts_guillotine.json) (enrichment confidence 0.6)

</details>
