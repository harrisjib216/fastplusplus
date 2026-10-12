# evmone

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> C++20 Ethereum Virtual Machine interpreter behind the EVMC API; about 3.5x faster than go-ethereum's EVM in evm-bench.

| | |
|---|---|
| **Beats** | go-ethereum (geth) built-in EVM interpreter |
| **Claimed result** | evm-bench README table: sum of benchmark times evmone 66ms vs geth 235ms (README prints geth as 3.561x relative to evmone 1.000x); snailtracer 43ms vs 163ms; erc20.transfer 8.6ms vs 24.6ms; ten-thousand-hashes 2.4ms vs 13.2ms. |
| **Workload** | Execution of five EVM contract benchmarks (erc20.approval-transfer, erc20.mint, erc20.transfer, snailtracer, ten-thousand-hashes) through the evm-bench runners. |
| **Metric** | throughput |
| **Compiler and flags** | evm-bench evmone runner: CMake -DCMAKE_BUILD_TYPE=Release (compiler not named), evmone 0.9.1 pulled via CPM; geth runner: `go run`, Go 1.19 module, go-ethereum v1.10.25 |
| **Adoption** | 979 stars; EVMC module usable as a geth plugin |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/ipsilon/evmone) · [benchmark](https://github.com/ziyadedher/evm-bench) |

## Verdict

The third-party evm-bench README times only the contract call (deployment excluded), averaging 5 runs (1 for snailtracer) each rounded to a whole millisecond: evmone 0.9.1 (CMake Release, compiler unnamed, on evmc::MockedHost) sums 66 ms versus 235 ms for go-ethereum v1.10.25's interpreter (go run, in-memory StateDB), with snailtracer 43 ms vs 163 ms; hardware is not stated.

## Use it when

- Building an Ethereum client, simulator, test harness or fuzzer in C/C++ that needs a fast, spec-tracking EVM behind a stable C ABI (EVMC).
- Compute-heavy contract execution: in evm-bench evmone was the fastest of seven EVMs, 3.8x faster than geth on snailtracer and 1.3x faster than revm on the summed suite.
- Running Ethereum execution-spec state or blockchain test fixtures quickly (the `evmone test` command recognises both formats).
- Embedding EVM execution in non-Go stacks where linking geth is not an option (any language with a C FFI can load the EVMC module).

## Skip it when

- As a drop-in speedup for stock go-ethereum: upstream geth does not load EVMC modules, and in a real node the state database and host calls, which the benchmark mocked away on the evmone side, take a large share of block-processing time.
- Consensus-critical deployments without your own differential testing: open issues include EIP-7702 consensus bugs (#1447, #1448, #1449, #1728) and a state-root divergence versus geth/revm (#1727, RIPEMD160 empty-account touch).
- Precompile-heavy workloads with a default build: the README says ecrecover is implemented directly 'with degraded performance' (a libsecp256k1 option exists since 0.19.0) and expmod uses stubs unless EVMONE_PRECOMPILES_GMP=1 is set.
- MSVC builds where interpreter speed matters: computed goto is not supported there, so the Baseline falls back to switch dispatch.
- Old toolchains: C++20 and CMake 3.25 or newer are required.

## How it is fast

The default Baseline interpreter does only a minimal JUMPDEST analysis and dispatches with computed goto (switch dispatch on MSVC or with cgoto=no); it reuses per-call-depth execution states and does 256-bit arithmetic with the intx library and Keccak with ethash. The optional Advanced interpreter uses indirect call threading over a pre-analysed instruction table and charges gas and stack checks once per basic block, but its analysis is expensive; since 0.9.0 the Baseline is 18% faster than Advanced on the project's own suite. Linux and Windows x86-64 builds default to -march=x86-64-v2.

## Compared with alternatives

No EVM interpreter is catalogued yet; the siblings (Fizzy, wasm3, Wasmi, WAMR and others) execute WebAssembly, not EVM bytecode, so pick evmone whenever the input is EVM bytecode and one of those when it is Wasm. Outside the catalogue, revm (Rust) is the nearest alternative and was 1.3x slower than evmone in the same evm-bench table.

## Integration

| | |
|---|---|
| **Form** | shared lib (EVMC module, BUILD_SHARED_LIBS defaults ON) \| static lib |
| **Dependencies** | EVMC, intx, ethash (Keccak); optional GMP for full expmod, optional libsecp256k1 for ecrecover, blst for BLS precompiles; google/benchmark and googletest only for tests |
| **Minimum toolchain** | C++20, CMake 3.25; changelog lists GCC 11, Clang 13, Visual Studio 2022 as minimum tested compilers and Xcode 16.2 for macOS |
| **Platforms** | x86-64 Linux/Windows (x86-64-v2 by default, configurable via EVMONE_X86_64_ARCH_LEVEL), macOS, aarch64 Linux |
| **Thread safety** | Not documented; lib/evmone/vm.hpp shows each VM instance reuses a per-call-depth ExecutionState vector and tracer chain without locking, so use one VM instance per thread. |
| **Drop-in for the baseline** | partial: geth can use it only through an EVMC-enabled geth build (--vm.evm=./libevmone.so); otherwise it is a library with a different (EVMC) interface |

## Gotchas

- Harness flaw: evm-bench rounds every run to a whole millisecond before averaging (src/run.rs parses each runner line and stores Duration::from_millis(value.round())), so rows of a few milliseconds are coarse: ten-thousand-hashes at 2.4 ms and erc20.mint at 5 ms carry up to 0.5 ms quantisation per run, about 20% of the evmone figure, which makes their 5.5x and 3.4x ratios rough.
- snailtracer, the row the record treats as the fair compute-bound comparison, runs only once per runner (num-runs 1, no warm-up) and is not pure compute: traceray copies every sphere (11 storage slots) and triangle (19 slots) from storage into memory for each ray and rand() writes the seed to storage, so its 3.8x also reflects geth's StateDB storage path versus evmc::MockedHost's unordered_map.
- Host asymmetry: the evmone runner builds a fresh evmc::MockedHost per run, while geth runs through its full StateDB with access-list preparation and snapshot/revert; both runners use London rules (EVMC 10.0.0's EVMC_LATEST_STABLE_REVISION is EVMC_LONDON), so the fork rules match. Outputs are not cross-checked beyond a success status.
- The table is from 2022 releases (evmone 0.9.1, go-ethereum v1.10.25) with no CPU or compiler stated; evmone has since released up to 0.24.0 (2026-09-23) and geth has had its own interpreter optimisations, so the current ratio is unmeasured here.

## Known shortcomings

- evm-bench numbers (66 ms vs geth 235 ms) name no CPU or compiler and use 2022 versions (evmone 0.9.1, geth 1.10.25); evmone runs on the evmc MockedHost while geth runs on a full StateDB, so the erc20 ratios are inflated (the fairest row, snailtracer, is about 3.8x). Off-baseline: an EVM, not a wasm runtime.
- Enricher: evm-bench's src/run.rs rounds each run to whole milliseconds before averaging, so the 2.4 ms and 5 ms rows carry about 20% quantisation and snailtracer runs once (num-runs 1); snailtracer is not compute-bound either, since each ray copies 11-slot spheres and 19-slot triangles from storage, so its 3.8x also measures StateDB against MockedHost. Revisions match (EVMC 10.0.0 London, same as geth). Open EIP-7702 consensus bugs (#1447-#1449, #1728) and a state-root divergence (#1727).

## Caveats and trade-offs

Evidence is the independent third-party evm-bench suite (ziyadedher/evm-bench, GPL-3.0, 225 stars, last commit 2024-03-19, renovate dependency bumps only). Its README states no hardware or compiler; the runners pin evmone 0.9.1 (Baseline interpreter, the default) and go-ethereum v1.10.25, both 2022 releases, so the table is several versions old. Each runner times only the contract call (deployment excluded), 5 runs per benchmark. The evmone runner executes against evmc::MockedHost (in-memory hash-map storage, fresh per run), while the geth runner goes through geth's full StateDB with access-list preparation and snapshot/revert on an in-memory database, so the storage-heavy erc20 rows charge geth for a state layer the evmone side mocks away; the compute-bound snailtracer row (43ms vs 163ms, about 3.8x derived from page data) is the fairest interpreter-to-interpreter comparison. Results are not cross-checked between runners beyond a success status. evmone's own geth-vs-evmone HackMD report (notes.ethereum.org, blocked here) was seen only as a search snippet: geomean evmone/Baseline 784M gas/s vs Geth 161M gas/s. The repo CHANGELOG has only self-comparisons (v0.9.0: Baseline 26% faster than 0.8.0 and 18% faster than Advanced on a 4.0 GHz Intel Haswell with Clang 15). The ipsilon/evmone repo was formerly ethereum/evmone. [retier] Independent evm-bench (ziyadedher/evm-bench, 2022 versions evmone 0.9.1 Baseline interpreter and go-ethereum v1.10.25, EVMC 10.0.0 London) with no CPU or compiler named; evmone runs on the evmc MockedHost while geth runs on a full StateDB, so the erc20 ratios are inflated and even snailtracer (3.8x) copies 11-slot spheres and 19-slot triangles from storage per ray. src/run.rs rounds each run to whole milliseconds before averaging (about 20% quantisation on the 2.4 ms and 5 ms rows) and snailtracer runs once. Open EIP-7702 consensus bugs (#1447-#1449, #1728) and state-root divergence (#1727). An EVM, not a wasm runtime.

C++20 required. Exposes the EVMC API, uses intx for 256-bit arithmetic and ethash for Keccak. Two interpreters: Baseline (default, minimal JUMPDEST analysis) and Advanced (indirect call threading, expensive upfront bytecode analysis). Using it inside geth needs a geth build with EVMC support. ecrecover is implemented directly by evmone with degraded performance (README).

## Maintenance

Actively maintained by Pawel Bylica (Ipsilon), with releases tracking every Ethereum fork up to Amsterdam (0.24.0 on 2026-09-23) and commits on 2026-10-06; Apache-2.0 and copyable as a library, but consensus-critical users should watch the open EIP-7702 issues.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party suite ziyadedher/evm-bench (README table; runner code public in runners/evmone/runner.cpp and runners/geth/runner.go) shows evmone 66ms vs geth 235ms summed over five contracts; build type (CMake Release) and pinned versions are in the repo, but no compiler name and no CPU model are stated, so not A.
- **Verifier notes:** Numbers match the evm-bench README exactly (sums 66ms vs 235ms, relative 3.561x; per-row values correct). Shortcomings: no CPU or compiler stated, 2022 versions (evmone 0.9.1, geth 1.10.25), and an asymmetric host (evmone on evmc MockedHost vs geth on its full StateDB) that inflates the storage-heavy erc20 ratios; snailtracer gives about 3.8x. Metadata verified: Apache-2.0, 979 stars, 340 forks, not a fork, last commit 2026-10-06.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/README.md>
  - <https://github.com/ziyadedher/evm-bench>
  - <https://github.com/ziyadedher/evm-bench/tree/main/runners>
  - <https://github.com/ziyadedher/evm-bench/tree/main/runners/evmone>
  - <https://github.com/ziyadedher/evm-bench/tree/main/runners/geth>
  - <https://github.com/ziyadedher/evm-bench/commits/main>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/runners/evmone/runner.cpp>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/runners/evmone/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/runners/evmone/entry.sh>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/runners/geth/runner.go>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/runners/geth/entry.sh>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/runners/geth/go.mod>
  - <https://github.com/ziyadedher/evm-bench/tree/main/benchmarks>
  - <https://github.com/ziyadedher/evm-bench/tree/main/benchmarks/erc20>
  - <https://github.com/ziyadedher/evm-bench/tree/main/benchmarks/erc20/transfer>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/benchmarks/erc20/transfer/ERC20Transfer.sol>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/benchmarks/erc20/transfer/benchmark.evm-bench.json>
  - <https://raw.githubusercontent.com/ipsilon/evmone/HEAD/README.md>
  - <https://github.com/ipsilon/evmone>
  - <https://github.com/ipsilon/evmone/commits/master>
- **Sources the enricher read:**
  - <https://github.com/ipsilon/evmone>
  - <https://raw.githubusercontent.com/ipsilon/evmone/HEAD/README.md>
  - <https://raw.githubusercontent.com/ipsilon/evmone/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/ipsilon/evmone/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ipsilon/evmone/HEAD/lib/evmone/vm.hpp>
  - <https://github.com/ipsilon/evmone/issues?q=is%3Aissue+is%3Aopen>
  - <https://github.com/ipsilon/evmone/issues/71>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/src/run.rs>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/src/results.rs>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/runners/evmone/runner.cpp>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/runners/evmone/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/runners/evmone/entry.sh>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/runners/geth/runner.go>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/runners/geth/entry.sh>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/benchmarks/erc20/transfer/ERC20Transfer.sol>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/benchmarks/erc20/transfer/benchmark.evm-bench.json>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/benchmarks/erc20/mint/ERC20Mint.sol>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/benchmarks/erc20/mint/benchmark.evm-bench.json>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/benchmarks/erc20/approval-transfer/ERC20ApprovalTransfer.sol>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/benchmarks/erc20/approval-transfer/benchmark.evm-bench.json>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/benchmarks/ten-thousand-hashes/TenThousandHashes.sol>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/benchmarks/ten-thousand-hashes/benchmark.evm-bench.json>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/benchmarks/snailtracer/SnailTracer.sol>
  - <https://raw.githubusercontent.com/ziyadedher/evm-bench/HEAD/benchmarks/snailtracer/benchmark.evm-bench.json>
  - <https://raw.githubusercontent.com/ethereum/evmc/v10.0.0/include/evmc/evmc.h>
  - <https://raw.githubusercontent.com/ethereum/evmc/v10.0.0/include/evmc/mocked_host.hpp>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/ipsilon/evmone`) · [data/wave12/enrich/raw/github_com_ipsilon_evmone.json](../../../data/wave12/enrich/raw/github_com_ipsilon_evmone.json) (enrichment confidence 0.8)

</details>
