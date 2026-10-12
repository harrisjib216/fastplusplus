# FAFO (parallel EVM transaction scheduler on revm)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟡 stale

> Pre-block transaction scheduler on revm and QMDB claiming 1.1M Merkleized ETH transfers/s on 96 cores; no sequential baseline.

| | |
|---|---|
| **Beats** | state-of-the-art sharded execution (paper's cost baseline); no sequential revm or pevm comparison found |
| **Claimed result** | README: 'Over 1 million Merkleized EVM-Compatible transactions per second while maintaining state verifiability'; 'Near-linear throughput scaling up to 96 cores and beyond on a single machine'; '91% cheaper than sharded execution'. Search-result text of the paper (arXiv 2507.10757): over 1.1 million native ETH transfers per second and over half a million ERC-20 transfers per second on a single node. No timing of sequential revm or pevm on the same workload is given in the repo. |
| **Workload** | bench-sendeth: replay of native ETH and ERC-20 transfer workloads (zero contention 'none', hot-account 'hotn', and replayed real-trace generators) over a 2^30-account QMDB database with Merkleization every block, using revm for execution on one many-core node; the README claims throughput scaling and a cost comparison. |
| **Metric** | throughput |
| **Hardware** | Repo states none. Third-party article snippet (OAK Research, not opened): one AWS server with 96 vCPUs, 786 GiB DRAM and six NVMe SSDs in RAID0 (22.5 TB). |
| **Compiler and flags** | Rust 1.85.0 (rust-toolchain.toml); benchmark run with cargo run --release through bench-sendeth/run.sh (which exports RUSTFLAGS=-Awarnings); release profile opt-level 3, thin LTO, codegen-units 16, panic=abort; revm 20.0.0 and alloy 0.11.1 per workspace Cargo.toml. Paper reproduction commands: run.sh --size full with --generator none, hotn (--contention-degree 0.1 --skew 100) or replay. |
| **Adoption** | 65 stars |
| **Last commit** | 2025-06-26 |
| **Links** | [repository](https://github.com/LayerZero-Labs/fafo) · [benchmark](https://github.com/LayerZero-Labs/fafo/blob/main/README.md) |

## Verdict

The README and LayerZero Labs' own preprint (arXiv 2507.10757, 'Under submission', read only as search-result text) claim over 1.1 million native ETH transfers and over 0.5 million ERC-20 transfers per second on a 96-core server while Merkleizing every block, plus 91% lower cost than unnamed 'state-of-the-art sharded execution'; the repo has the bench-sendeth harness but no result files, no hardware, and no sequential revm, pevm or Block-STM run. Reading the harness shows those runs use million-transaction blocks, oracle write sets for 99% of ERC-20 transactions and no nonce or signature checks, so the figures are an upper bound for transfer-only traffic, not a like-for-like speedup over revm.

## Use it when

- Prototyping or researching a high-throughput EVM-compatible sequencer or rollup node where you control the whole execution stack and can run a many-core server with large NVMe storage.
- Workloads dominated by native ETH and ERC-20 transfers spread over many accounts with low contention, which is the only shape the repo benchmarks.
- When a state commitment per block is required at high throughput (light clients, stateless or ZK validation) and you are willing to adopt QMDB as the state store.
- As a reference implementation of Bloom-filter conflict framing to compare against Block-STM style executors (pevm) on your own traces.

## Skip it when

- You want a faster executor inside an existing client: there is no reth/geth integration, no crates.io release (exepipe is publish = false), and the code is a single 'Initial commit' marked ongoing research.
- You need exact Ethereum semantics: both run_tx and run_tx_with_disable_nonce_check pass disable_nonce_check = true, MpexHandler skips the beneficiary reward, and any EVM error other than an access-set violation hits handle_tx_execute_mpex_err, which is panic!("not implemented").
- Contract-heavy or hot-contract traffic: nothing beyond plain transfers is benchmarked, and the README itself says gains are bounded by contention (hotn generator).
- Small machines: the paper-size run initialises 2^30 accounts, the README asks for at least 256 GB of Docker virtual disk and 32 GB of memory, and thread pools are compile-time constants (12 warm-up, 64 execution, 16 simulation threads).
- You need a maintained dependency: no commits since 2025-06-26, issues are restricted to collaborators, and the only pull request is an open typo fix.

## How it is fast

ParaLyze pre-executes a transaction on revm against current state to predict its read and write sets as 80-bit short hashes of accounts and storage slots. ParaFramer packs 4-transaction tasks into up to 64 frames (Framer&lt;u64&gt;) using ParaBloom, a per-frame Bloom-filter bitmap, so tasks inside a frame never conflict; the dispatcher runs frames on a 64-thread rayon pool with 12 warm-up (prefetch) threads, i.e. deterministic scheduling from predicted access sets instead of optimistic execute-and-validate as in Block-STM. Any transaction that touches state outside its predicted set is dropped by the access check, and QMDB's append-only Merkle storage keeps per-block root computation cheap on NVMe.

## Compared with alternatives

risechain/pevm is the closer sibling: Block-STM style optimistic parallel execution on revm with published sequential-revm baselines (22.1x on Uniswap swaps on Graviton3); pick FAFO only if you want deterministic pre-block framing plus per-block Merkleization on a large node and can live with research code. For single-thread EVM speed, revm, evmone or revmc are the relevant entries.

## Integration

| | |
|---|---|
| **Form** | source-drop (Cargo workspace: exepipe, exepipe-common, codedb, hpfile, bench-sendeth, with QMDB vendored in-tree; not published to crates.io) |
| **Dependencies** | revm 20.0.0, alloy 0.11.1, rayon, crossbeam, threadpool, parking_lot, dashmap (workspace pins); QMDB in-tree; tikv-jemallocator on Linux for the benchmark binary |
| **Minimum toolchain** | Rust 1.85.0 pinned in rust-toolchain.toml, edition 2021; .cargo/config.toml adds --cfg const_slice_from_raw_parts_mut |
| **Platforms** | Linux recommended (README steers users to a VS Code Dev Container; jemalloc is Linux-gated); other platforms not documented |
| **Thread safety** | Internally multi-threaded; ExePipe::run_block_with_sim takes &mut self and processes one block at a time, with hard-coded pool sizes |
| **Drop-in for the baseline** | false: a whole-block pipeline over its own QMDB state store, not a replacement for revm's executor or Database trait, and not comparable to sequential revm without porting state |

## Gotchas

- Harness flaw (bench-sendeth/src/common/parallel_transfer.rs): ERC-20 runs attach precomputed write sets (the sender and receiver balance slots) to 99 of every 100 transactions (no_rwsets_pct = 1), so the revm pre-execution ParaLyze needs in production runs for only 1% of the measured ERC-20 transactions; native ETH runs skip it entirely because SimulatorShard gives every empty-calldata transaction an empty CrwSets (commented 'TODO: need review'), which is correct for EOA-to-EOA transfers but would mis-schedule a value transfer into a contract whose receive() or fallback writes storage.
- Throughput is transfer_txn_count divided by replay wall time: it counts transactions handed to the framer (the only assertion is framer.txns_processed == transfer_txn_count), never checks execution results, and every transaction carries nonce 0, gas price 0, a default hash and no signature, so signature recovery, nonce checks and fee accounting are absent from the measured path.
- Paper-size runs use huge blocks: the full ETH preset (30 bits) replays 32 blocks of 2^20 = 1,048,576 transfers (2^25 in total) and the ERC-20 preset 256 blocks of 131,072, so 'Merkleizing every block' amortises one state root over about a million transfers; init-db and the database copy are excluded from the timed region.
- Thread counts are fixed in source (Dispatcher::new(12, 64), ThreadPool::new(16), 4 simulator shards) with no CLI flag, so reproducing the 'near-linear scaling to 96 cores' curve needs code edits; the workspace Cargo.toml declares license MIT while the README and LICENSE files say MIT OR Apache-2.0.

## Known shortcomings

- README makes only first-party TPS and '91% cheaper than sharded' claims with no sequential revm or pevm baseline; the vendor preprint is unreachable here; transfer-only workloads; single commit 2025-06-26, stale; weak category fit (a transaction scheduler, not a VM).
- Enricher (bench-sendeth/src/common/parallel_transfer.rs): the ERC-20 runs hand 99 of every 100 transactions precomputed write sets (no_rwsets_pct = 1), so the revm pre-execution runs for only 1% of them, and the ETH runs skip it entirely (empty calldata gets an empty CrwSets, marked 'TODO: need review'); run_tx always sets disable_nonce_check = true; every transaction has nonce 0, gas price 0 and no signature; the beneficiary reward is skipped; non-access-set EVM errors hit panic!('not implemented'); TPS is submitted transactions over wall time with results never checked; the full ETH preset is 32 blocks of 1,048,576 transactions, so one Merkle root per million transfers; thread pools are hard-coded (12/64/16), so the 96-core scaling claim needs source edits. Workspace Cargo.toml says MIT only. The TPS figures are an upper bound, not a like-for-like comparison with revm.

## Caveats and trade-offs

Not a faster-than-baseline claim in the sense of the listed baselines: neither the README nor bench-sendeth compares against sequential revm or pevm on a common workload (the only comparison in the README is '91% cheaper than sharded execution', a cost figure against an unnamed baseline, with the methodology in LayerZero Labs' own paper, which is blocked here: layerzero.network, arxiv.org and emergentmind.com returned EGRESS_BLOCKED, so the paper's numbers come from search-result text only). The workloads are plain ETH and ERC-20 transfers, which is far easier to parallelise than general contract code; the paper is 'Under submission' (not peer reviewed) and is written by the vendor. The repo holds a single 'Initial commit' dated 2025-06-26, so there is no development history to check, and the 96-vCPU machine is only known from a third-party article snippet. bench-sendeth writes a metrics JSON per run but no published result file is in the repo. FAFO is a transaction scheduler and parallel execution pipeline on revm plus QMDB, not a bytecode VM, so the bytecode-vms-and-wasm filing is a loose fit. pevm and revm are catalogued separately, and Block-STM style comparison, if any, is in the unopened paper. [retier] First-party TPS and '91% cheaper than sharded' claims only, no sequential revm or pevm baseline, vendor preprint unreachable here. The bench harness hands precomputed write sets to 99% of ERC-20 transactions and all ETH transfers, runs with nonce checks disabled, nonce 0, gas price 0 and no signatures, skips the beneficiary reward, never checks results, and hard-codes thread pools, so the numbers are an upper bound. Transfer-only workloads; single commit 2025-06-26, stale; a transaction scheduler rather than a VM (loose category fit); Cargo.toml says MIT only.

A transaction scheduler and pipeline (ParaLyze address estimation, ParaFramer with ParaBloom Bloom filters to group non-conflicting transactions into frames, ParaScheduler precedence graphs) rather than a new EVM interpreter: it runs revm and QMDB underneath, so gains come from parallel scheduling of independent transfers and are bounded by contention. Needs a very large machine (the benchmark initialises a database with billions of accounts, and the README's Docker setup asks for at least 256 GB of virtual disk and 32 GB of memory). Synthetic transfer workloads; the repo is described as ongoing research.

## Maintenance

Stale research drop (one 'Initial commit' on 2025-06-26, 65 stars, issues closed to the public) under MIT OR Apache-2.0; useful as a reference design, not as a production executor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The README carries only first-party throughput and cost claims (over 1 million Merkleized TPS, near-linear scaling to 96 cores, 91% cheaper than unnamed sharded execution) from LayerZero Labs' own preprint; bench-sendeth code is public but no hardware, no baseline run (sequential revm, pevm or Block-STM) and no result table are in the repo, and the paper was unreachable.
- **Verifier notes:** README claims match the record; repo is one 'Initial commit' (2025-06-26), 65 stars, 13 forks, MIT and Apache-2.0, not a fork; stale is correct (15 months). Shortcomings to record: no baseline timing in repo (only a cost ratio vs unnamed sharded execution), vendor preprint not peer reviewed and unreachable, transfer-only workloads, no hardware in repo, weak category fit (scheduler, not VM).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** comparison against sequential revm and pevm; like-for-like replay against sequential revm with signatures and nonce checks
- **Pages the verifier opened:**
  - <https://github.com/LayerZero-Labs/fafo>
  - <https://github.com/LayerZero-Labs/fafo/commits/main>
  - <https://raw.githubusercontent.com/LayerZero-Labs/fafo/HEAD/README.md>
  - <https://raw.githubusercontent.com/LayerZero-Labs/fafo/HEAD/bench-sendeth/readme.md>
  - <https://raw.githubusercontent.com/LayerZero-Labs/fafo/HEAD/bench-sendeth/run.sh>
  - <https://raw.githubusercontent.com/LayerZero-Labs/fafo/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/LayerZero-Labs/fafo/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/LayerZero-Labs/fafo/HEAD/.cargo/config.toml>
- **Sources the enricher read:**
  - <https://github.com/LayerZero-Labs/fafo>
  - <https://github.com/LayerZero-Labs/fafo/pulls?q=is%3Apr>
  - <https://github.com/LayerZero-Labs/fafo/tree/main/bench-sendeth/src>
  - <https://github.com/LayerZero-Labs/fafo/tree/main/bench-sendeth/src/common>
  - <https://github.com/LayerZero-Labs/fafo/tree/main/exepipe/src>
  - <https://github.com/LayerZero-Labs/fafo/tree/main/exepipe/src/simulator>
  - <https://github.com/LayerZero-Labs/fafo/tree/main/exepipe/src/dispatcher>
  - <https://github.com/LayerZero-Labs/fafo/tree/main/exepipe/src/context>
  - <https://github.com/LayerZero-Labs/fafo/tree/main/exepipe-common/src>
  - <https://raw.githubusercontent.com/LayerZero-Labs/fafo/HEAD/README.md>
  - <https://raw.githubusercontent.com/LayerZero-Labs/fafo/HEAD/bench-sendeth/readme.md>
  - <https://raw.githubusercontent.com/LayerZero-Labs/fafo/HEAD/bench-sendeth/run.sh>
  - <https://raw.githubusercontent.com/LayerZero-Labs/fafo/HEAD/bench-sendeth/Cargo.toml>
  - <https://raw.githubusercontent.com/LayerZero-Labs/fafo/HEAD/bench-sendeth/src/bin/bench-sendeth.rs>
  - <https://raw.githubusercontent.com/LayerZero-Labs/fafo/HEAD/bench-sendeth/src/common/parallel_transfer.rs>
  - <https://raw.githubusercontent.com/LayerZero-Labs/fafo/HEAD/bench-sendeth/src/common/def.rs>
  - <https://raw.githubusercontent.com/LayerZero-Labs/fafo/HEAD/bench-sendeth/src/common/cli.rs>
  - <https://raw.githubusercontent.com/LayerZero-Labs/fafo/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/LayerZero-Labs/fafo/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/LayerZero-Labs/fafo/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/LayerZero-Labs/fafo/HEAD/workloads/get_workloads.sh>
  - <https://raw.githubusercontent.com/LayerZero-Labs/fafo/HEAD/exepipe/Cargo.toml>
  - <https://raw.githubusercontent.com/LayerZero-Labs/fafo/HEAD/exepipe/src/lib.rs>
  - <https://raw.githubusercontent.com/LayerZero-Labs/fafo/HEAD/exepipe/src/framer.rs>
  - <https://raw.githubusercontent.com/LayerZero-Labs/fafo/HEAD/exepipe/src/exetask.rs>
  - <https://raw.githubusercontent.com/LayerZero-Labs/fafo/HEAD/exepipe/src/simulator/simulator.rs>
  - <https://raw.githubusercontent.com/LayerZero-Labs/fafo/HEAD/exepipe/src/simulator/simulator_shard.rs>
  - <https://raw.githubusercontent.com/LayerZero-Labs/fafo/HEAD/exepipe/src/simulator/crw_sets.rs>
  - <https://raw.githubusercontent.com/LayerZero-Labs/fafo/HEAD/exepipe/src/dispatcher/dispatcher.rs>
  - <https://raw.githubusercontent.com/LayerZero-Labs/fafo/HEAD/exepipe/src/dispatcher/def.rs>
  - <https://raw.githubusercontent.com/LayerZero-Labs/fafo/HEAD/exepipe/src/context/block_context.rs>
  - <https://raw.githubusercontent.com/LayerZero-Labs/fafo/HEAD/exepipe-common/src/revm.rs>
  - <https://raw.githubusercontent.com/LayerZero-Labs/fafo/HEAD/exepipe-common/src/access_set.rs>
  - <https://raw.githubusercontent.com/LayerZero-Labs/fafo/HEAD/exepipe-common/src/executor/mod.rs>
  - <https://raw.githubusercontent.com/LayerZero-Labs/fafo/HEAD/exepipe-common/src/executor/execute_tx.rs>
  - <https://raw.githubusercontent.com/LayerZero-Labs/qmdb/HEAD/README.md>
  - WebSearch: FAFO 1 million TPS EVM Merkleizing paper (result text for arXiv 2507.10757 and layerzero.network/research/fafo; pages not opened)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/layerzero-labs/fafo`) · [data/wave12/enrich/raw/github_com_layerzero_labs_fafo.json](../../../data/wave12/enrich/raw/github_com_layerzero_labs_fafo.json) (enrichment confidence 0.65)

</details>
