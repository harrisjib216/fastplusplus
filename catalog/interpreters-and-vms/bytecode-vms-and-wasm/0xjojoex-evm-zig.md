# evm.zig (evmz, Zig EVM execution engine)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Zig` · `MIT OR Apache-2.0` · 🟢 active

> Pre-1.0 Zig EVM with tail-call dispatch; first-party runs beat evmone baseline and revm on storage and snailtracer fixtures.

| | |
|---|---|
| **Beats** | evmone (v0.23.0, baseline and advanced interpreters) and revm (=43.0.2 raw interpreter, Interpreter::run_plain) |
| **Claimed result** | README (Apple M1 Max, ReleaseFast, 2026-08-13), evmz versus evmone-base versus revm-int: Arithmetic loop 0.104 / 0.109 / 0.501 ms, Storage SSTORE loop 0.162 / 0.854 / 0.875 ms, ERC20 transfer 3.761 / 6.247 / 6.084 ms, Snailtracer 19.965 / 59.804 / 37.990 ms. bench/README.md ratios (base/evmz and revm/evmz): SSTORE 5.27x and 5.40x, SLOAD 3.97x and 2.34x, snailtracer 3.00x and 1.90x, ERC20 transfer 1.66x and 1.62x, Arithmetic 1.05x and 4.82x. evmz is slower than evmone-base on MSTORE loop (0.125 vs 0.084 ms, 0.67x), LOG0 32-byte (0.057 vs 0.033 ms, 0.58x), LOG0 0-byte (0.69x), LOG4 0-byte (0.80x) and ten-thousand-hashes (0.86x). AMD EPYC Genoa (KVM guest pinned to one CPU) rows are near parity with evmone-base: ERC20 transfer 7.686 vs 7.447 ms (0.97x), arithmetic 0.151 vs 0.145 ms (0.96x), keccak loop 4.597 vs 4.584 ms (1.00x), snailtracer 33.347 vs 57.983 ms (1.74x), SSTORE 0.595 vs 0.838 ms (1.41x), and ahead of revm on every row (1.08x to 3.08x). |
| **Workload** | VM-core 'compare' lane over the evm-bench-style fixtures (arithmetic loop, MSTORE loop, keccak loop, ten-thousand-hashes, SLOAD and SSTORE loops, LOG0/LOG4 with 0 and 32 byte data, ERC20 mint, transfer and approval+transfer, snailtracer): deployed runtime bytecode called repeatedly through each engine's interpreter-level path with analysis prepared outside the timed window, fixed Osaka spec, median of 100-run medians, lower time is better. |
| **Metric** | throughput |
| **Hardware** | Apple M1 Max, macOS arm64 (headline snapshot, 2026-08-13); AMD EPYC Genoa, Linux x86-64, KVM guest pinned to one CPU (earlier snapshot). |
| **Compiler and flags** | Zig &gt;= 0.16.0 (bench/build.zig.zon), zig build bench-compare -Dbench-optimize=ReleaseFast -Dbench-support-min=osaka -Dbench-support-max=osaka -Dnative-keccak=xkcp -- --spec osaka --num-runs 100 --warmup-ms 100 (five repeats, median of the five per-run medians); evmz modules built with omit_frame_pointer; evmone v0.23.0 with intx 0.15.0 compiled inside the Zig build by Zig's bundled clang from a hand-listed source set with -std=c++20 -fomit-frame-pointer -fno-exceptions -fno-rtti (not evmone's own CMake Release build); revm =43.0.2 built with cargo --release, RUSTFLAGS=-C target-cpu=native -C force-frame-pointers=no, CARGO_PROFILE_RELEASE_LTO=fat, CODEGEN_UNITS=1 (Rust toolchain version not pinned for the sidecar). |
| **Adoption** | 3 stars |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/0xjojoex/evm.zig) · [benchmark](https://github.com/0xjojoex/evm.zig/blob/main/bench/README.md) |

## Verdict

Author-run VM-core benchmark (deployed runtime bytecode called repeatedly, analysis outside the timed window, fixed Osaka, median of five 100-run medians) on an Apple M1 Max with ReleaseFast and XKCP Keccak: evmz beats evmone-baseline 1.05x to 5.27x on 9 of 14 evm-bench-style fixtures (snailtracer 3.00x, ERC20 transfer 1.66x) and loses on 5, and beats revm's raw interpreter on every row; the older AMD EPYC Genoa KVM run is near parity with evmone-baseline except snailtracer 1.74x. The baselines were evmone 0.23.0-dev built by Zig's clang at -O2 and revm 41.0.0 with fat LTO, and the storage rows are skewed by differing mock hosts.

## Use it when

- A Zig codebase that needs an embeddable EVM interpreter and can track a pre-1.0 API pinned to a commit.
- Specialized or custom-fork EVMs (L2 rule changes, extra precompiles, custom opcodes) where compile-time specialization via Spec.extend beats runtime switches.
- zkVM guest work: the same stateless block validator compiles for SP1, ZisK and OpenVM with bounded pools.
- Compute-heavy contract execution (the snailtracer row: 19.97 ms vs evmone-baseline 59.80 ms on M1, 33.35 vs 57.98 ms on the AMD run), if you can re-measure on your own hardware first.

## Skip it when

- Production consensus or anything handling value: version 0.0.0, unaudited, public API changes between commits, 3 stars and no external users documented.
- C/C++ or Rust clients wanting a drop-in for evmone or revm: there is no EVMC adapter any more and only an experimental C API.
- Workloads dominated by MSTORE, LOG or many small Keccak calls: evmone-baseline is faster on the M1 MSTORE loop (0.67x), LOG0 rows (0.58x and 0.69x), LOG4 0-byte (0.80x) and ten-thousand-hashes (0.86x).
- x86-64 servers if you expect the M1 margins: the older AMD EPYC Genoa run is within about 7% of evmone-baseline on 9 of 14 rows and only clearly ahead on snailtracer (1.74x), SSTORE (1.41x) and MSTORE (1.44x).
- Teams that cannot follow Zig toolchain churn: main requires Zig 0.16.x and each release supports one Zig minor.

## How it is fast

Tail-call threaded dispatch: each opcode handler takes the instruction pointer, stack pointer and gas as register arguments, charges gas, executes and jumps to the next handler with @call(.always_tail) (src/interpreter/tail_dispatch.zig), so there is no central loop or per-op capability check. Fork rules, tracing and single-stepping are comptime choices that produce separate specialized dispatch tables, jump validity comes from a precomputed JUMPDEST bitmask, and the executor uses preallocated pooled frames, stacks and buffers. The host interface also offers fused loadStorage/storeStorage callbacks that return access warmth and value in one call, which the benchmark host implements with a single hash-map getOrPut.

## Compared with alternatives

Pick evmz over evmone or revm only when you are in Zig, want compile-time fork specialization or zkVM guest builds, and accept pre-release risk; evmone remains the mature C++ interpreter with an EVMC ABI and revm the Rust incumbent with a large user base. Guillotine's catalogued README table shows it at rough parity with evmone on ERC20 rows, so neither newcomer has a clear win over evmone beyond its own first-party runs.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none for the pure-Zig core codecs (rlp, mpt, ssz with .core = false); the EVM core pulls lazy C dependencies for crypto: libsecp256k1 v0.8.0 (default since #69), blst, mcl, and optional XKCP Keccak |
| **Minimum toolchain** | Zig 0.16.0 (minimum_zig_version in build.zig.zon); main tracks Zig 0.16.x |
| **Platforms** | native x86-64 and aarch64 (benchmarked on Linux x86-64 and macOS arm64); RV64 guest builds for SP1, ZisK, OpenVM |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw in the storage rows: the evmone runner's mock host (bench/evmone/vm_loop.cpp) stores slots in a std::map (red-black tree keyed by a 52-byte array) and every SLOAD/SSTORE goes through two EVMC callbacks (access_storage, then get_storage or set_storage), while evmz's mock host (bench/src/common.zig) uses a Zig AutoHashMap with fused loadStorage/storeStorage callbacks that do one getOrPut; revm's sidecar uses Rust's SipHash HashMap. The storage-sload-loop fixture is 1000 iterations of 8 SLOADs of slot 0, so the 3.97x SLOAD and 5.27x SSTORE wins over evmone-baseline (and part of the ERC20 margins) measure mock-host data structures and callback count as much as the interpreter, unlike the arithmetic loop where the engines are at parity (1.05x).
- The published M1 table (dated 2026-08-13, unchanged in bench/README.md since commit d8f5e95) was produced by a harness that pinned evmone at commit 786c96f1 (0.23.0-dev) and revm =41.0.0; PR #65 (2026-09-10) moved the harness to evmone v0.23.0 and revm =43.0.2 without refreshing the tables, so the baseline versions the repo now names are not the ones measured.
- Compiler asymmetry: evmone and intx are compiled inside the Zig build by Zig's bundled clang, and Zig passes -O2 (not -O3) for C/C++ sources in ReleaseFast while Zig code gets its -O3 equivalent; evmone's own CMake Release build would use CMake's -O3 default. The M1 run also gives evmz the optional XKCP Keccak while evmone uses its bundled keccak.c.
- Cross-engine correctness is not checked: each runner only requires a success status, and compare.zig never compares return data, gas used or logs between engines (EEST conformance runs in CI cover evmz's semantics separately).

## Known shortcomings

- VM-core only; the harness checks only success status with no cross-engine output or gas check; evmone-base is faster on 5 of 14 M1 rows and near parity on the older AMD KVM run; evmone was built by Zig's clang rather than its own CMake build; XKCP Keccak is used on the evmz side only; first-party, 3 stars. Not the rejected cryptuon/zig-evm.
- Enricher: the storage rows measure mock hosts, not dispatch: the evmone mock host (bench/evmone/vm_loop.cpp) uses std::map with 52-byte keys and two EVMC callbacks per SLOAD/SSTORE while the evmz host (bench/src/common.zig) uses a Zig AutoHashMap with fused loadStorage/storeStorage and one getOrPut, so SLOAD 3.97x, SSTORE 5.27x and part of the ERC20 margins come from host data structures; the arithmetic loop is at parity (1.05x). The M1 table (2026-08-13, unchanged since d8f5e95) ran evmone commit 786c96f1 (0.23.0-dev) and revm 41.0.0, and PR #65 (2026-09-10) bumped the harness to evmone v0.23.0 and revm 43.0.2 without re-measuring, so the record's baseline versions were wrong; Zig passes -O2 rather than -O3 for C/C++ under ReleaseFast, so evmone was built at -O2; the EVMC adapter was removed (#33), so it is not drop-in.

## Caveats and trade-offs

Comparison is VM-core only: interpreter execute() with analysis prepared outside the timed window, no transaction validation, journal or database, so it is not a whole-client comparison (the repo says the executor lane is deliberately later). Correctness check in all three runners is limited to a success status (evmz result status, evmone EVMC_SUCCESS in bench/evmone/vm_loop.cpp, revm InterpreterAction::Return with is_ok() in bench/revm/src/main.rs); bench/src/compare.zig only collects timings and host call counts and does not assert that return data, gas used or logs match across engines. The README headline table shows the four rows where evmz wins; the full M1 table also has rows where evmone-baseline is faster (MSTORE loop 0.67x, LOG0 0-byte 0.69x, LOG0 32-byte 0.58x, LOG4 0-byte 0.80x, ten-thousand-hashes 0.86x), and on the AMD snapshot evmz is within about 7% of evmone-base on 9 of 14 rows (ratios 0.94x to 1.07x, derived from page data) and slower on the LOG0 rows (0.73x, 0.75x). The AMD snapshot is older, run in a KVM guest pinned to one CPU, and names only the EPYC Genoa family, not a model. The M1 snapshot enables evmz's optional XKCP Keccak provider while evmone uses its bundled keccak.c, so the keccak-heavy rows partly compare hash implementations. The evmone baseline is compiled by Zig's clang from a hand-picked source list and flag set rather than evmone's CMake Release build, and revm's sidecar has no pinned Rust version. Revm is timed through its raw interpreter (Interpreter::run_plain), not a transaction path. The project is pre-release (version 0.0.0, unaudited) and contains CLAUDE.md and AGENTS.md (AI-assisted development); first-party numbers only, 3 stars. Not the cryptuon/zig-evm project, which is rejected for a hard-coded table. [retier] VM-core only, first-party, 3 stars; the harness checks only success status with no cross-engine output or gas check. Storage rows (SLOAD 3.97x, SSTORE 5.27x, part of ERC20) measure mock hosts: evmone's std::map host with two EVMC callbacks per access against evmz's fused AutoHashMap host; the arithmetic loop is at parity (1.05x) and evmone-base is faster on 5 of 14 M1 rows. Measured against evmone commit 786c96f1 (0.23.0-dev) and revm 41.0.0 (2026-08-13), with evmone built at -O2 by Zig's clang rather than its CMake build and XKCP Keccak on the evmz side only; PR #65 bumped the baselines without re-measuring. EVMC adapter removed (#33). Not the rejected cryptuon/zig-evm.

Tail-call-dispatch interpreter in Zig with fork rules, tracing and single-step selected at compile time (separate binaries), zero-alloc pooled executor, optional XKCP Keccak and native crypto libraries (blst, mcl, libsecp256k1) as lazy dependencies, zkVM guest builds (ZisK, SP1, OpenVM). The headline numbers enable the optional XKCP Keccak provider ('maximum-performance configuration'). Pre-1.0 (version 0.0.0), builds need a very recent Zig (0.16).

## Maintenance

Actively developed (last commit 2026-10-05, 174 commits, 0 issues filed) and dual MIT OR Apache-2.0, but pre-release version 0.0.0 with an unstable API, AI-assisted development (AGENTS.md, CLAUDE.md) and only first-party benchmarks whose published tables lag the current harness.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now A.
- **Tier reason:** bench/README.md publishes both snapshots against evmone v0.23.0 (baseline and advanced) and revm 43.0.2 from public harness code (bench/src/compare.zig, bench/evmone/vm_loop.cpp, bench/revm/src/main.rs, fixtures under bench/fixtures/vm-loop), with the exact command line, ReleaseFast and frame-pointer flags in bench/build.zig, Zig 0.16 toolchain (bench/build.zig.zon minimum_zig_version 0.16.0) and a named CPU (Apple M1 Max). Every number in claimed_speedup matches the page.
- **Verifier notes:** All M1 and AMD figures and ratios in the record match bench/README.md and the README Performance table; harness, flags and versions confirmed in bench/build.zig and bench/build.zig.zon (evmone v0.23.0, intx v0.15.0, revm =43.0.2). Shortcomings to record: VM-core-only scope, status-only correctness checks with no cross-engine output or gas comparison, evmone-base faster on 5 of 14 M1 rows and near parity on the older AMD run, evmone built outside its CMake build, XKCP Keccak only on the evmz side, first-party with 3 stars. Last commit 2026-10-05 (Native contract #73), MIT OR Apache-2.0, not a fork.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** output- and gas-checked comparison with evmone's own build; shared-host comparison with evmone's own -O3 build
- **Pages the verifier opened:**
  - <https://github.com/0xjojoex/evm.zig>
  - <https://github.com/0xjojoex/evm.zig/commits/main>
  - <https://github.com/0xjojoex/evm.zig/tree/main/bench>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/HEAD/README.md>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/HEAD/bench/build.zig>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/HEAD/bench/build.zig.zon>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/HEAD/bench/revm/Cargo.toml>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/HEAD/bench/revm/src/main.rs>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/HEAD/bench/evmone/vm_loop.cpp>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/HEAD/bench/src/compare.zig>
- **Sources the enricher read:**
  - <https://github.com/0xjojoex/evm.zig>
  - <https://github.com/0xjojoex/evm.zig/commits/main>
  - <https://github.com/0xjojoex/evm.zig/commits/main/bench/src/common.zig>
  - <https://github.com/0xjojoex/evm.zig/commits/main/bench/README.md>
  - <https://github.com/0xjojoex/evm.zig/issues?q=is%3Aissue>
  - <https://github.com/0xjojoex/evm.zig/pull/65>
  - <https://github.com/0xjojoex/evm.zig/pull/65/files>
  - <https://github.com/0xjojoex/evm.zig/commit/71a6a18>
  - <https://github.com/0xjojoex/evm.zig/tree/main/src>
  - <https://github.com/0xjojoex/evm.zig/tree/main/src/instruction>
  - <https://github.com/0xjojoex/evm.zig/tree/main/bench/fixtures/vm-loop>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/HEAD/README.md>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/HEAD/AGENTS.md>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/HEAD/CLAUDE.md>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/HEAD/build.zig>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/HEAD/bench/build.zig>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/HEAD/bench/build.zig.zon>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/HEAD/bench/src/compare.zig>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/HEAD/bench/src/vm_loop.zig>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/HEAD/bench/src/common.zig>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/HEAD/bench/evmone/vm_loop.cpp>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/HEAD/bench/revm/src/main.rs>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/HEAD/bench/revm/Cargo.toml>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/HEAD/bench/fixtures/vm-loop/README.md>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/HEAD/bench/fixtures/vm-loop/storage-sload-loop/init.hex>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/HEAD/bench/fixtures/vm-loop/storage-sstore-loop/init.hex>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/HEAD/bench/fixtures/vm-loop/erc20-transfer/init.hex>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/HEAD/src/instruction/storage.zig>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/HEAD/src/Host.zig>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/HEAD/src/Interpreter.zig>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/HEAD/src/interpreter/tail_dispatch.zig>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/d8f5e95/bench/README.md>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/d8f5e95/bench/revm/Cargo.toml>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/d8f5e95/bench/evmone/vm_loop.cpp>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/d8f5e95/bench/src/common.zig>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/d8f5e95/bench/build.zig.zon>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/29184a8/bench/README.md>
  - <https://raw.githubusercontent.com/0xjojoex/evm.zig/29184a8/bench/revm/Cargo.toml>
  - <https://raw.githubusercontent.com/ziglang/zig/master/src/Compilation.zig>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/0xjojoex/evm.zig`) · [data/wave12/enrich/raw/github_com_0xjojoex_evm_zig.json](../../../data/wave12/enrich/raw/github_com_0xjojoex_evm_zig.json) (enrichment confidence 0.8)

</details>
