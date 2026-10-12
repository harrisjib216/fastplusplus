# risechain/pevm (parallel EVM on revm)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Block-STM parallel executor for whole EVM blocks on top of revm; about 2x sequential revm on mainnet blocks.

| | |
|---|---|
| **Beats** | sequential revm (pevm's own execute_revm_sequential path) |
| **Claimed result** | Benches README (Graviton3 c7g.8xlarge): mocked 1-Gigagas blocks, Uniswap Swaps 413.42 ms sequential vs 18.707 ms parallel (22.1x), ERC20 Transfers 246.43 vs 60.817 ms (4.05x), Raw Transfers 159.08 vs 56.425 ms (2.82x). Mainnet: 'We are currently \~2.02 times faster than sequential execution on average', max speed-up x4.32 (block 7279999, 4.54 vs 1.05 ms), max slow-down x0.89. Derived from page data over the 85 mainnet rows: 63 blocks more than 5% faster, 18 within 5% of 1.0, 4 slower (0.89x to 0.93x); per-block mean ratio 1.96x, geometric mean 1.78x, ratio of summed times 2.04x. Top-level README repeats 2x average and 22x on the Uniswap gigagas block for the legacy Block-STM design. |
| **Workload** | Criterion (100 samples) wall time to execute one whole Ethereum block with state preloaded in memory: 85 real mainnet blocks from Frontier to Cancun, plus three mocked 1-Gigagas blocks (raw transfers, ERC20 transfers, Uniswap swaps); sequential revm versus pevm's Block-STM style parallel executor. |
| **Metric** | throughput |
| **Hardware** | AWS c7g.8xlarge, Graviton3, 32 vCPUs @ 2.6 GHz |
| **Compiler and flags** | cargo bench --features global-alloc --bench mainnet, and JEMALLOC_SYS_WITH_MALLOC_CONF="thp:always,metadata_thp:always" cargo bench --features global-alloc --bench gigagas. Bench profile inherits the workspace release profile: codegen-units=1, lto=fat at the time the tables were written (November 2024); strip=true and panic=abort were added later (PR #443, 2024-12-16), and Cargo ignores panic for bench targets anyway. Global allocator: snmalloc on aarch64 and rpmalloc elsewhere for mainnet, jemalloc with THP for gigagas. Concurrency: min(available_parallelism, 12 on ARM / 8 on x86) for mainnet; gigagas uses available_parallelism (32 on the stated machine). rustc version not stated (no rust-toolchain file; edition 2024 at HEAD). |
| **Adoption** | 355 stars |
| **Last commit** | 2026-06-05 |
| **Links** | [repository](https://github.com/risechain/pevm) · [benchmark](https://raw.githubusercontent.com/risechain/pevm/HEAD/crates/pevm/benches/README.md) |

## Verdict

Criterion (100 samples) on an AWS c7g.8xlarge (Graviton3, 32 vCPUs), November 2024 code, rustc version not stated, release profile with fat LTO and codegen-units=1. The baseline is revm run sequentially through pevm's own execute_revm_sequential over in-memory pre-state. Results: 85 Frontier-to-Cancun mainnet blocks at 2.04x by summed time and 1.78x geometric mean (max 4.32x, min 0.89x) with up to 12 threads and snmalloc; mocked 1-Gigagas blocks with 32 threads and jemalloc THP at 2.82x (raw transfers), 4.05x (ERC20) and 22.1x (Uniswap).

## Use it when

- Syncing or building large EVM blocks (roughly 10M gas and up) on a many-core server: the 2024 tables show 1.5-3.7x on most London-to-Cancun mainnet blocks, and 22 Cancun-era rows have a geometric mean of 1.92x (derived from page data).
- App-specific chains or L2s whose blocks are dominated by transactions touching disjoint state (many independent swaps or token transfers), where the mocked 1-Gigagas blocks reach 4.05x (ERC20) to 22.1x (Uniswap) on 32 vCPUs.
- Rust node stacks already built on revm and alloy (reth-style) that can expose a Send + Sync read-only state snapshot and want results bit-identical to sequential execution.
- Research on parallel EVM scheduling: the repo calls itself a playground for Parallel EVM R&D and ships mainnet block snapshots plus mocked-block benchmarks to compare against.

## Skip it when

- Small or highly interdependent blocks: blocks under 4,000,000 gas or with fewer transactions than threads fall back to sequential revm (18 of 85 mainnet rows at 1.0x), and 4 of 85 rows are slower (0.89x to 0.93x); a block that self-destructs and redeploys a contract aborts the parallel run and starts over sequentially.
- Production consensus or block building with untrusted transactions: the README says work in progress and not production ready, issue #518 (EIP-7702 re-delegation leaves a stale code hash, so parallel diverges from sequential) is open with its fix PR #519 unmerged, and the retry path for insufficient-funds or nonce-too-high transactions is commented as able to deadlock on new or faulty blocks.
- Single-thread or per-transaction latency work: pevm still runs the stock revm interpreter for each transaction, so a faster interpreter or compiler (revmc, evmone) is the tool for that.
- If you need the state root or disk-backed state: state-root calculation (sparse trie) is still TODO, and all published numbers preload the block's pre-state into memory.
- If you need a stable published crate: crates.io has only pevm 0.1.0 from 2024-05-28, so current code has to be taken as a git dependency.

## How it is fast

Optimistic concurrency in the style of Block-STM: transactions run speculatively against a multi-version memory (a DashMap from location hash to a BTreeMap of per-transaction writes), and a collaborative scheduler hands out execution and validation tasks, re-executing transactions whose read set was invalidated. EVM-specific tweaks remove the most common false conflicts: gas payments to the block beneficiary and simple ETH transfers between already-touched accounts are recorded as lazy balance deltas and only evaluated after the block, so every transaction does not depend on the coinbase account. Smaller tricks include identifying locations by a precomputed 64-bit hash, a per-slot UnsafeCell result buffer, and freeing the multi-version memory on a background thread.

## Compared with alternatives

Pick pevm when whole-block throughput on many cores is the bottleneck and blocks have real transaction-level independence. revm (its own baseline), evmone, evm2 and Guillotine make each transaction faster on one core, and revmc compiles hot contracts, so those help even on fully serial blocks. pevm still calls revm for each transaction, so the two approaches are complementary; no combined numbers are documented. A Supra AFT 2025 paper (seen only as a search snippet) reports its conflict-specification executor up to 1.33x faster than PEVM on synthetic workloads.

## Integration

| | |
|---|---|
| **Form** | crate (git dependency; the crates.io release 0.1.0 dates from 2024-05-28) |
| **Dependencies** | revm 38, op-revm 19, alloy 2.x crates (consensus, primitives, provider, rpc-types-eth, trie, rlp), op-alloy, dashmap, hashbrown, rustc-hash, smallvec, bitflags, thiserror, serde; optional reqwest, tokio and alloy-transport (rpc-storage feature) and rpmalloc, snmalloc-rs, tikv-jemallocator (global-alloc feature; snmalloc needs cmake) |
| **Minimum toolchain** | Rust edition 2024 (rustc 1.85 or newer); no rust-version field or rust-toolchain file |
| **Platforms** | Any Rust target with std threads; numbers are from aarch64 (Graviton3). The mainnet bench caps threads at 12 on aarch64 and 8 elsewhere, and the bench README says rpmalloc can crash on Graviton. |
| **Thread safety** | Pevm::execute takes &mut self, so one block at a time per Pevm instance; each call spawns concurrency_level scoped OS threads, and each instance keeps one background thread for deferred drops. Storage must be Send + Sync. |
| **Drop-in for the baseline** | partial — it wraps revm rather than replacing it: a block-level call over its own read-only Storage trait that returns per-transaction receipts and state transitions for the caller to commit; Ethereum and RISE chain specs only (OP support was replaced by RISE in April 2026). |

## Gotchas

- The published tables come from the November 2024 code (tables last changed in commit 82fd0f1, 2024-11-05), which defined the NeedValidation bitflag as 0, so every transaction was always validated. PR #508 fixed this on 2026-05-26, and the maintainer's open issue #509 says the corrected code is slower than the buggy version, without figures. HEAD therefore probably does not reproduce the tables. That 2024 run used the risechain/revm fork at rev 7345c07, ran gigagas under SpecId::LATEST rather than the CANCUN the README states, and had panic=abort in the release profile already.
- Harness details that favour the parallel column. The sequential baseline is pevm's own execute_revm_sequential, which deep-clones each transaction's state for CacheDB::commit and frees the CacheDB inside the timed call. The parallel path hands its MvMemory and Scheduler (and in 2024 the transaction vector) to a background AsyncDropper thread, so that deallocation falls outside the timing. The gigagas blocks are independent by construction: raw and ERC20 transfers are self-transfers, and every Uniswap swap gets its own tokens, pool and router. The 'average 2.02x' is a ratio of summed times (report.py); the per-block geometric mean is 1.78x (derived from page data).
- Correctness risk, found by reading the code and not demonstrated: memory locations in the multi-version memory, read sets and write sets are identified only by an unkeyed 64-bit FxHash of (address, slot). If two storage slots read and written in one block collide, a later read silently returns the other slot's value. A contract can pick its own slot indices, so a collision found by a birthday search (about 2^32 hashes) could make parallel results diverge from sequential ones on purpose. The code's TODO considers only the performance effect of collisions.
- The gigagas bench dropped each run's Result unchecked until commit 00c6928 (2026-05-19), which added nonce: 1 and .expect(). Raw-transfer runs after the April 2026 revm bumps probably errored on the first transaction, inferred from the diff and not run. The 2024 numbers are not affected: that revm fork's TxEnv nonce was Option and None skips the check. The scheduler spin-waits with thread::yield_now, so speedup depends on the OS scheduler: the 2024-11-05 bench README reported a large slowdown on Linux 6.8 (EEVDF) before replacing that note with a warning that mixing efficiency cores costs over 25%. The benchmark machine's kernel is not stated.

## Known shortcomings

- First-party harness with sequential revm as the baseline inside pevm's own code; no rustc version; the bench tables date from November 2024 on older code (gigagas README says CANCUN while the code is now OSAKA, Graviton3 host); the 22x comes from a synthetic Uniswap block. Per-block geomean 1.78x, summed-time ratio 2.04x (derived from page data); 63/18/4 split confirmed.
- Enricher: the published tables are November 2024 code (82fd0f1) where the NeedValidation bitflag was 0 so every transaction was validated; fix PR #508 merged 2026-05-26 and maintainer issue #509 says the fixed code is slower, with no numbers, so HEAD is unlikely to reproduce the tables. Bench asymmetry: the sequential baseline deep-clones state on every transaction (commit(state.clone())) and frees its CacheDB inside the timed call while the parallel arm hands MvMemory and Scheduler drops to a background AsyncDropper thread; gigagas blocks are independent by construction (self-transfers, a separate Uniswap deployment per swap); the '2.02x average' is a summed-time ratio (report.py), geomean 1.78x. Correctness: open #518 (EIP-7702 re-delegation, parallel diverges from sequential, fix PR #519 unmerged); storage locations are keyed only by an unkeyed 64-bit FxHash, so an attacker-chosen slot collision gives silent wrong reads (code reading); vm.rs notes that the underfunded or nonce-too-high retry can deadlock on new or faulty blocks. Record corrections: the 2024 gigagas run used SpecId::LATEST, not CANCUN; the baseline revm is the risechain/revm fork at rev 7345c07.

## Caveats and trade-offs

Numbers are first-party and stale: crates/pevm/benches/README.md was last changed for results on 2024-11-05/2024-11-20 (later edit 2024-12-16 only touched profiling commands), so they reflect the November 2024 code and revm version; the gigagas section says CANCUN spec while the current gigagas.rs runs SpecId::OSAKA. No rustc version anywhere. Baseline is revm run sequentially inside pevm's own harness (pevm.execute with force_sequential, i.e. execute_revm_sequential, which wraps storage in a CacheDB, commits state.clone() per transaction and builds pevm-format state transitions), not an independent geth, evmone or reth run. Pevm::execute itself falls back to sequential for blocks under 4,000,000 gas or with fewer transactions than the concurrency level, which is why 18 mainnet rows read 1.0x. Chain state is preloaded into memory (authors argue disk-backed state would favor parallel execution, unmeasured). The 22x figure is a synthetic mocked block of independent Uniswap swaps (README says it does not represent real-world blocks). The README describes the measured design as 'Legacy'; the new architecture (inline EVM, shreds, sparse trie) is still TODO, and the repo is marked work in progress, not production ready. Parallel Go (Polygon, Sei) being slower than sequential Rust/C++ is asserted with no numbers. [retier] First-party harness on Graviton3 with the baseline being the risechain/revm fork (rev 7345c07) run sequentially inside pevm's own code; tables from November 2024 code (82fd0f1) where every transaction was validated (NeedValidation bitflag 0), fixed by PR #508 in 2026-05 with the maintainer reporting the fixed code slower and no new numbers. The sequential arm deep-clones state per transaction and frees its CacheDB inside the timed call while the parallel arm drops asynchronously. Per-block geomean 1.78x, summed-time ratio 2.04x (derived from page data); the 22x comes from a synthetic Uniswap block whose transactions are independent by construction (SpecId::LATEST). Open correctness issue #518 (EIP-7702 re-delegation divergence); unkeyed FxHash location keys; no rustc version.

Parallel executor that still delegates VM execution to revm (an inline parallel-aware EVM is only a TODO). Speedup depends on block parallelism; falls back to sequential execution when a block self-destructs then redeploys a contract, and the concurrency level is hard-coded (8 on x86, 12 on ARM) with the README noting it ideally needs auto-tuning. Needs cmake to build snmalloc. Repo warns it is a work in progress and not production ready.

## Maintenance

Active (last commit 2026-06-05) and MIT-licensed, but self-described as work in progress and not production ready. The published numbers predate the NeedValidation fix, which the maintainer says is slower, and the revm 22-to-38 bumps. An EIP-7702 divergence bug (#518) is open, and the code read here shows a 64-bit hash-collision correctness risk; treat it as a research executor to benchmark yourself, not a drop-in node component.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): downgrade; tier before verification A, tier now C.
- **Tier reason:** First-party Criterion tables in crates/pevm/benches/README.md (bench code crates/pevm/benches/mainnet.rs and gigagas.rs; CPU named as Graviton3 c7g.8xlarge), but no rustc version is stated anywhere (no rust-toolchain file) and the tables were last updated in November 2024 on older code, so the build behind the numbers cannot be pinned. Under the project's precedent a missing compiler version on first-party numbers is C, not A.
- **Verifier notes:** All quoted numbers match the benches README and the 63/18/4 split of the 85 mainnet rows checks out; the average is about 2x only as a ratio of summed times (per-block geomean 1.78x, derived). Downgraded A to C: first-party, no rustc version, tables measured on November 2024 code that has since changed (CANCUN to OSAKA spec in gigagas, profile edits). Metadata confirmed on github.com: MIT, 355 stars, not a fork or archived, last commit 2026-06-05.
- **Fields the verifier corrected:** `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** independent re-run on current code with rustc stated; re-run on post-#508 code with a symmetric sequential baseline
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/risechain/pevm/HEAD/crates/pevm/benches/README.md>
  - <https://raw.githubusercontent.com/risechain/pevm/HEAD/README.md>
  - <https://raw.githubusercontent.com/risechain/pevm/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/risechain/pevm/HEAD/crates/pevm/Cargo.toml>
  - <https://raw.githubusercontent.com/risechain/pevm/HEAD/crates/pevm/benches/mainnet.rs>
  - <https://raw.githubusercontent.com/risechain/pevm/HEAD/crates/pevm/benches/gigagas.rs>
  - <https://raw.githubusercontent.com/risechain/pevm/HEAD/crates/pevm/src/pevm.rs>
  - <https://github.com/risechain/pevm>
  - <https://github.com/risechain/pevm/commits/main>
  - <https://github.com/risechain/pevm/commits/main/crates/pevm/benches/README.md>
  - <https://github.com/risechain/pevm/pull/443/files>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/risechain/pevm/HEAD/README.md>
  - <https://raw.githubusercontent.com/risechain/pevm/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/risechain/pevm/HEAD/crates/pevm/Cargo.toml>
  - <https://raw.githubusercontent.com/risechain/pevm/HEAD/crates/pevm/benches/README.md>
  - <https://raw.githubusercontent.com/risechain/pevm/HEAD/crates/pevm/benches/mainnet.rs>
  - <https://raw.githubusercontent.com/risechain/pevm/HEAD/crates/pevm/benches/gigagas.rs>
  - <https://raw.githubusercontent.com/risechain/pevm/HEAD/crates/pevm/benches/report.py>
  - <https://raw.githubusercontent.com/risechain/pevm/HEAD/crates/pevm/src/pevm.rs>
  - <https://raw.githubusercontent.com/risechain/pevm/HEAD/crates/pevm/src/lib.rs>
  - <https://raw.githubusercontent.com/risechain/pevm/HEAD/crates/pevm/src/vm.rs>
  - <https://raw.githubusercontent.com/risechain/pevm/HEAD/crates/pevm/src/scheduler.rs>
  - <https://raw.githubusercontent.com/risechain/pevm/HEAD/crates/pevm/src/mv_memory.rs>
  - <https://raw.githubusercontent.com/risechain/pevm/HEAD/crates/pevm/src/chain.rs>
  - <https://raw.githubusercontent.com/risechain/pevm/HEAD/crates/pevm/src/chain/ethereum.rs>
  - <https://raw.githubusercontent.com/risechain/pevm/HEAD/crates/pevm/src/storage.rs>
  - <https://raw.githubusercontent.com/risechain/pevm/HEAD/crates/pevm/tests/common/mod.rs>
  - <https://raw.githubusercontent.com/risechain/pevm/HEAD/crates/pevm/tests/uniswap/mod.rs>
  - <https://raw.githubusercontent.com/risechain/pevm/HEAD/crates/pevm/tests/erc20/mod.rs>
  - <https://raw.githubusercontent.com/risechain/pevm/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/risechain/pevm/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/risechain/pevm/82fd0f1a79f16dda1f1d8a026167ec2dd56c7f2d/Cargo.toml>
  - <https://raw.githubusercontent.com/risechain/pevm/82fd0f1a79f16dda1f1d8a026167ec2dd56c7f2d/crates/pevm/benches/README.md>
  - <https://raw.githubusercontent.com/risechain/pevm/82fd0f1a79f16dda1f1d8a026167ec2dd56c7f2d/crates/pevm/benches/mainnet.rs>
  - <https://raw.githubusercontent.com/risechain/pevm/82fd0f1a79f16dda1f1d8a026167ec2dd56c7f2d/crates/pevm/benches/gigagas.rs>
  - <https://raw.githubusercontent.com/risechain/pevm/82fd0f1a79f16dda1f1d8a026167ec2dd56c7f2d/crates/pevm/src/pevm.rs>
  - <https://raw.githubusercontent.com/risechain/pevm/82fd0f1a79f16dda1f1d8a026167ec2dd56c7f2d/crates/pevm/src/vm.rs>
  - <https://raw.githubusercontent.com/risechain/pevm/82fd0f1a79f16dda1f1d8a026167ec2dd56c7f2d/crates/pevm/src/scheduler.rs>
  - <https://raw.githubusercontent.com/risechain/pevm/82fd0f1a79f16dda1f1d8a026167ec2dd56c7f2d/crates/pevm/src/lib.rs>
  - <https://raw.githubusercontent.com/risechain/pevm/82fd0f1a79f16dda1f1d8a026167ec2dd56c7f2d/crates/pevm/tests/common/runner.rs>
  - <https://raw.githubusercontent.com/risechain/pevm/164183d8406f5cf841c396873166e70bc1565a4b/crates/pevm/benches/README.md>
  - <https://raw.githubusercontent.com/risechain/pevm/164183d8406f5cf841c396873166e70bc1565a4b/crates/pevm/src/vm.rs>
  - <https://raw.githubusercontent.com/risechain/pevm/164183d8406f5cf841c396873166e70bc1565a4b/crates/pevm/src/pevm.rs>
  - <https://raw.githubusercontent.com/risechain/revm/7345c07ae7f65a976e9db4866872066aef0bdce4/crates/primitives/src/env.rs>
  - <https://github.com/risechain/pevm>
  - <https://github.com/risechain/pevm/issues?q=is%3Aissue>
  - <https://github.com/risechain/pevm/issues/518>
  - <https://github.com/risechain/pevm/issues/530>
  - <https://github.com/risechain/pevm/issues/509>
  - <https://github.com/risechain/pevm/pull/508>
  - <https://github.com/risechain/pevm/pull/519>
  - <https://github.com/risechain/pevm/pull/512>
  - <https://github.com/risechain/pevm/commits/main>
  - <https://github.com/risechain/pevm/commits/main/crates/pevm/benches/README.md>
  - <https://github.com/risechain/pevm/commits/main?after=&path=crates/pevm/benches/gigagas.rs>
  - <https://github.com/risechain/pevm/commit/00c692837ab50d25072f8c73adc9169da676156f>
  - <https://github.com/risechain/revm/commit/7345c07ae7f65a976e9db4866872066aef0bdce4>
  - <https://crates.io/api/v1/crates/pevm>
  - <https://github.com/LayerZero-Labs/fafo>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/risechain/pevm`) · [data/wave12/enrich/raw/github_com_risechain_pevm.json](../../../data/wave12/enrich/raw/github_com_risechain_pevm.json) (enrichment confidence 0.8)

</details>
