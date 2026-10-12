# DTVM (ZetaEngine lazy-JIT Wasm VM)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly runtimes and compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> C++ deterministic Wasm/EVM JIT for smart contracts. Its lazy JIT reaches first invocation about 20x sooner than Wasmtime's eager compile.

| | |
|---|---|
| **Beats** | Wasmtime (Cranelift); also Wasmer Singlepass, Cranelift and LLVM |
| **Claimed result** | Paper (arXiv 2504.16552 preprint, April 2025 copy at resources/DTVM_paper.pdf). Time to first invocation with lazy JIT on: DTVM 0.95-0.96 ms vs Wasmtime (Cranelift) 20.5-20.6 ms on PolyBench. Table 9 averages: 22.21x over Wasmtime (Cranelift), 4.05x over Wasmer Singlepass, 68.01x over Wasmer Cranelift and 234.13x over Wasmer LLVM on 30 PolyBench cases; on WAPM, 18.87x over Wasmtime, 4.35x over Wasmer Singlepass (one case at 0.49x), 18.66x over Wasmer Cranelift and 197.99x over Wasmer LLVM. Figure 9 shows 21.35x and 21.54x (deriche, doitgen) and 24.51x and 23.36x (echo, pi), so 21.54x is the larger of two displayed PolyBench cases, not a per-case maximum. From the appendix tables (derived from page data): per-case Wasmtime ratios run 19.2-26.0x on PolyBench and 3.2-24.2x on the 20 WAPM packages, and the Wasmer Cranelift PolyBench average is about 22.2x rather than Table 9's 68.01x. Processing time (load + compile + execute; section 5.2.2 says lazy compilation was off): DTVM beats Wasmtime (Cranelift) in 20 of 30 PolyBench cases (1.20x average there, best 1.63x on deriche) and loses the other 10 (0.76x average, worst about 0.57x on trisolv, derived from page data); it averages 11.03-12.14x over the three Wasmer backends. Fibonacci(30): 11.73 ms, which is 11.8% less than Wasmtime (Cranelift) and 25.6%, 29.6% and 40.5% less than Wasmer Cranelift, Singlepass and LLVM. Integer Overflow: 5.5 ms, about 20.6% less than Wasmtime (Cranelift) and up to 64.6% less than the Wasmer variants. The abstract also claims up to 2x over evmone on ERC20/721/1155; that was not checked here. |
| **Workload** | PolyBench/C 4.2.1 (30 kernels, int data, DUMP_ARRAYS; the package build notes say SMALL_DATASET) run as archived prebuilt wasm, 20 WAPM packages (time to first invocation only), a recursive Fibonacci(30) and an Integer Overflow (Uniswap-like swap) contract with host APIs mocked in memory. DTVM multipass and lazy JIT are compared against Wasmtime (Cranelift) and Wasmer Singlepass, Cranelift and LLVM. |
| **Metric** | startup (time to first invocation) and latency (processing time = load+compile+execute) |
| **Hardware** | Cloud VM, 8 vCPU, 16 GiB, Intel Xeon Platinum 8369B @ 2.70GHz, CentOS 7.9, Linux 3.10.0 (paper section 5). benchmarks/paper/ENVIRONMENT.md records Turbo Boost off only for the contract microbenchmark machine and says the other baselines may have run on a different machine. |
| **Compiler and flags** | PolyBench wasm: archived prebuilt binaries whose toolchain was inferred from binary traces (WASI clang 11.0.0 for 27 cases, 14.0.3 for 3). benchmarks/paper/benchmarks/polybenchc/build.sh reconstructs them with wasi-sdk clang -O3 -DSMALL_DATASET -DDATA_TYPE_IS_INT -DPOLYBENCH_DUMP_ARRAYS -D_WASI_EMULATED_PROCESS_CLOCKS. Paper-era DTVM: commit 882c83155 with LLVM 15. The package's Release build line (-DZEN_ENABLE_SINGLEPASS_JIT=ON -DZEN_ENABLE_MULTIPASS_JIT=ON -DZEN_ENABLE_CHECKED_ARITHMETIC=ON) and run flags (-m multipass [--enable-multipass-lazy] --disable-multipass-greedyra --disable-multipass-multithread) are reconstructions marked 'inferred from xlsx', and the paper does not record its build type. Baselines in the paper text: Wasmtime 31.0.0 (Cranelift) and Wasmer 5.0.5. The package records Wasmer 5.0.4 with Singlepass from v5.0.5-rc1, and its current pins are Wasmtime 45.0.0, Wasmer 7.1.0 (LLVM 21) and DTVM c3c3fd856. |
| **Adoption** | 157 stars |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/DTVMStack/DTVM) · [benchmark](https://media.githubusercontent.com/media/DTVMStack/DTVM/main/resources/DTVM_paper.pdf) |

## Verdict

The project's own non-peer-reviewed preprint (Xeon Platinum 8369B cloud VM, CentOS 7.9, paper-era DTVM 882c83155 with LLVM 15, Wasmtime 31.0.0, Wasmer 5.0.x) reports about 22x faster time-to-first-invocation than Wasmtime (Cranelift) on 30 PolyBench modules. That compares a lazy compile of the first function against Wasmtime's eager whole-module compile. Whole-run processing time is mixed (20 of 30 PolyBench wins, 1.20x average there), and the fib and integer-overflow microbenchmarks are startup-dominated or compare different wasm programs.

## Use it when

- Smart-contract or plugin hosts that load a module and call one or two exports, where time to first call matters more than peak throughput (the paper's TTFI case: about 0.95 ms vs about 20.5 ms for Wasmtime on PolyBench modules).
- Systems that need deterministic execution, gas metering and checked integer arithmetic built into the JIT (ZEN_ENABLE_CHECKED_ARITHMETIC lowers imported checked_i64_\* calls into inline checked operations).
- Embedding a Wasm or EVM JIT from C or C++ with a small trusted computing base, including Intel SGX enclaves (ZEN_ENABLE_SGX).
- Linux x86-64 deployments that can link LLVM 15 for the multipass/lazy JIT, or ARM64 hosts that can live with the singlepass JIT or interpreter.

## Skip it when

- Long-running compute: on PolyBench processing time it beats Wasmtime (Cranelift) in only 20 of 30 kernels (1.20x average where it wins, as slow as about 0.57x on trisolv), so steady-state code quality is roughly at par.
- General-purpose WASI applications: the project is built for contracts. Builtin WASI and libc are partial ('builtin libc (partial)'), and support for proposals such as SIMD and threads is not documented in the README.
- Non-x86-64 targets that need the optimising JIT: 'Lazy JIT currently only supports the x86-64 target'.
- Multi-threaded embedding without your own locking: module and host-module APIs in zetaengine-c.h are marked '\warning not thread-safe'.
- Teams wanting releases or semver: the GitHub Releases section is empty, and recent commit activity is almost all EVM-side work.

## How it is fast

Wasm and EVM are lowered to a deterministic middle IR (dMIR) and then to x86-64 code through an LLVM-derived backend. Lazy mode (FLAT, 'Function Level fAst Transpile') does only load, precompile, instantiation and the first called function's JIT before running. A background tier (FLAS, 'Function Level Adaptive hot-Switching') recompiles hot functions at higher optimisation levels and swaps them in through trampolines. Wasm traps and bounds checks use CPU exceptions (ZEN_ENABLE_CPU_EXCEPTION, on by default) instead of explicit checks. The startup win comes from deferring compilation, not from a faster compiler: the package's own docs put DTVM's eager multipass compile at about 90 ms on the current build, against about 20 ms for Wasmtime's whole-module compile.

## Compared with alternatives

Pick DTVM over wasman (Go interpreter), WasmKit (Swift interpreter) or KinoWASM (interpreter) when you need an optimising x86-64 JIT with gas metering and determinism embedded from C/C++. Pick it over Cage when you want fast cold invocation rather than MTE memory safety. VectorVisor solves a different problem: batch GPU throughput.

## Integration

| | |
|---|---|
| **Form** | static lib (libzetaengine.a) plus dtvm CLI; Rust crate in rust_crate/ |
| **Dependencies** | LLVM 15 (multipass/lazy JIT only); asmjit, CLI11 and spdlog fetched via CMake FetchContent; evmc submodule for EVM builds |
| **Minimum toolchain** | C++17, CMake 3.16+ |
| **Platforms** | Linux x86-64 for multipass/lazy JIT; singlepass JIT on x86-64 and ARM64; interpreter portable; optional Intel SGX |
| **Thread safety** | C API module load/delete and host-module functions are documented as not thread-safe; multipass JIT uses up to 8 compile threads by default and background JIT threads in lazy and profile-guided modes |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw in the paper's Integer Overflow benchmark (5.5 ms, 20.6% less than Wasmtime): the runtimes run different programs. The DTVM wasm (-DENABLE_DTVM_TEST) imports env.checked_i64_add/sub/mul, which DTVM's module loader resolves and its bytecode visitor turns into inline checked arithmetic. The Wasmtime and Wasmer wasm uses __builtin_\*_overflow, compiled to portable wasm, plus explicit divide-by-zero and INT64_MIN/-1 checks that the DTVM variant drops (it uses plain '/'). Wasmer also gets a third build with a main() entry. The gap therefore measures a DTVM-only intrinsic and less source-level work, not JIT quality, and the DTVM module cannot run on the other VMs. REPRODUCE_fib_overflow_5way.md calls this 'a real architectural advantage, not a testing artifact'.
- The fib(30) figure (11.73 ms) is the shell `time` wall clock of one process running a recursive fib(30), so CLI startup and compilation dominate it. The package's current fib benchmark is a different workload (500,000,000 iterations of an 8x-unrolled iterative fib(30)), and its run_wasmtime45.sh omits the '-C cache=n' that the reproduction guide lists.
- TTFI cannot be reproduced from public sources. The current paper pin c3c3fd856 (2026-05-29, '30% fib speedup') returns 404 on github.com. Main's src/utils/statistics.cpp, the file the package names, prints no 'Total compilation time' line, and the change note docs/changes/2026-05-28-wapm-ttfi-compile-time-report is absent. The Wasmtime 45 and Wasmer 7.1 timing patches are not shipped; only a Wasmtime 31 patch is. scripts/README.md calls the paper's DTVM formula 'inferred': load + precompile + instantiation + fg_jit/fg_count, an average per-function JIT time, measured against Wasmtime's whole compile_module().
- The README build lines use CMAKE_BUILD_TYPE=Debug, and the default CMake options leave the multipass JIT OFF. Benchmarking that build gives numbers far below the paper's Release build.

## Known shortcomings

- Evidence is the repo's own April 2025 preprint (resources/DTVM_paper.pdf) with paper-era flags "inferred from xlsx" and the build type unrecorded; the 22x time-to-first-invocation is lazy against eager compilation (the FAQ gives DTVM eager compile about 90 ms vs Wasmtime about 20 ms), processing time beats Wasmtime in only 20 of 30 PolyBench cases (1.20x average), the 11-12x over Wasmer is suspect (all three Wasmer backends about 10x slower than Wasmtime there), the paper tables disagree (WAPM 30 vs 20 cases, Wasmer Cranelift 68.01x vs about 22.2x) and the reproduction package swaps out zuk; paper used Wasmtime 31.0.0 and Wasmer 5.0.5.
- Enricher: the 'Integer Overflow' claim (20.6% less than Wasmtime) times different wasm programs (the DTVM build imports env.checked_i64_\* which bytecode_visitor.h inlines under ZEN_ENABLE_CHECKED_ARITHMETIC, the baseline build uses __builtin_\*_overflow plus extra div-by-zero/INT64_MIN checks, and Wasmer gets a third main() build); the fib(30) 11.73 ms is a whole-process time of one recursive call, mostly startup and compile; the current pin c3c3fd856 gives 404, main's statistics.cpp has no 'Total compilation time' line, the docs/changes 2026-05-28 note is absent, the Wasmtime 45 and Wasmer 7.1 TTFI patches are unshipped and scripts/README calls the DTVM TTFI formula 'inferred'.

## Caveats and trade-offs

The paper is a first-party arXiv preprint (arXiv 2504.16552; a v2 exists but arxiv.org is blocked here) by Ant Digital Technologies authors and is not peer reviewed. The reproduction package (benchmarks/paper, added 2026-09) ships cases, version pins and reconstructed scripts but no result data, no per-runtime logs and not the paper's 'Average time' timing script; the contract microbenchmark runner is not included. Its runtimes/dtvm/BUILD.md marks the paper-era DTVM run flags as 'inferred from xlsx'. Its docs/XLSX_FORMAT.md is an issue log: the archived table's cell semantics (compile vs total, ms vs s) are unconfirmed, and the paper's DTVM PolyBench values (2mm 3283.6 ms) match the archived 'dtvm multipass + lazy' total cell (3283.55), although section 5.2.2 says lazy compilation was disabled for that comparison (the eager 'dtvm multipass' cell is 3314.16). The time-to-first-invocation (TTFI) metric is asymmetric. DTVM lazy counts load, lazy precompile, instantiation and the first function's JIT; Wasmtime counts an eager whole-module compile_module(); Wasmer counts Module::new. The package FAQ says DTVM's own eager multipass compile reads about 90 ms on the current build, so the 22x comes from lazy vs eager compilation, not from a faster compiler. Wasmer's three backends post nearly identical processing times about 10x Wasmtime's on compute-heavy kernels (2mm: Cranelift 43.5 s, LLVM 43.9 s, Singlepass 53.0 s vs Wasmtime 3.8 s). LLVM no faster than Cranelift points to a harness or configuration effect in the Wasmer runs, so the 11-12x averages over Wasmer are unexplained. The paper's tables disagree internally. Table 9 lists 30 WAPM cases where appendix Table 12 has 20. Table 9's 68.01x Wasmer Cranelift TTFI average does not match the appendix (about 22.2x, derived from page data). Table 8's Wasmer backend labels are permuted relative to the appendix columns. The build notes say SMALL_DATASET, but the multi-second processing times (2mm 3.3 s) are far above what SMALL_DATASET kernels need, so the dataset size of the archived wasm is unclear. The package's WAPM set replaces the paper's zuk with fortune. zuk was DTVM's worst case: 0.49x vs Wasmer Singlepass and only 3.2x vs Wasmtime. Versions: the paper used Wasmtime 31.0.0 and Wasmer 5.0.x with DTVM 882c83155. The package now pins Wasmtime 45.0.0, Wasmer 7.1.0 and DTVM c3c3fd856 (2026-05-29) for a revised experiment set whose numbers are not in the repo. The package says it is not recorded whether the paper's wall-clock runs cleared the Wasmtime and Wasmer module caches; TTFI runs need WASMTIME_CACHE=0. The README build examples use CMAKE_BUILD_TYPE=Debug, which the package warns is far slower than the paper's Release build. Lazy JIT is x86-64 only. The LICENSE is Apache-2.0, with LLVM-derived portions under Apache-2.0 and BSD-3-Clause.

Built for blockchain smart contracts (deterministic execution, gas metering, EVM ABI compatibility, TEE portability), not a general-purpose WASI runtime. Lazy JIT with LLVM 15 requires x86-64; the singlepass JIT and interpreter modes are the portable ones. Small codebase (69.5 KLoC vs 143.6 KLoC for Wasmtime per the paper).

## Maintenance

Actively developed (last commit 2026-10-08, 157 stars, no tagged releases), now mostly on the EVM JIT. Apache-2.0 with LLVM-derived code, usable as a C/C++ library. Its performance evidence stays first-party, and the current reproduction pin, c3c3fd856, is not public.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** The numbers come from the project's own arXiv preprint (Ant Digital Technologies authors, not peer reviewed; resources/DTVM_paper.pdf, April 2025), which states the CPU (Xeon Platinum 8369B) but not the DTVM build type or run flags. The reproduction package benchmarks/paper ships cases and reconstructed scripts but no result data or the paper's timing script; its runtimes/dtvm/BUILD.md says the paper-era run CLI was 'inferred from xlsx', and docs/XLSX_FORMAT.md says the archived table's semantics (compile vs total, ms vs s) are unconfirmed. Flags absent from public sources and first-party authorship cap this at C.
- **Verifier notes:** This is a real Wasm VM, and the numbers quoted do appear in the repo's paper PDF. The TTFI headline is lazy-vs-eager compilation (DTVM's eager compile is slower than Wasmtime's per the package FAQ), and processing time beats Wasmtime in only 20 of 30 PolyBench cases at a 1.20x average. Wasmer results look anomalous (all three backends about 10x slower than Wasmtime with LLVM = Cranelift), and the paper's tables have internal inconsistencies (WAPM case count, 68.01x average, lazy-vs-eager column). The repo's own reproduction notes say paper-era flags were inferred, so the tier drops from A to C. Metadata checked: Apache-2.0, 157 stars, last commit 2026-10-08, not a fork. No earlier wave lists DTVM.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-114 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://media.githubusercontent.com/media/DTVMStack/DTVM/main/resources/DTVM_paper.pdf>
  - <https://github.com/DTVMStack/DTVM>
  - <https://github.com/DTVMStack/DTVM/commits/main>
  - <https://github.com/DTVMStack/DTVM/commit/882c83155>
  - <https://github.com/DTVMStack/DTVM/tree/main/benchmarks/paper>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/README.md>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/main/LICENSE>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/main/benchmarks/paper/README.md>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/main/benchmarks/paper/VERSIONS.md>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/main/benchmarks/paper/ENVIRONMENT.md>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/main/benchmarks/paper/SOURCES.md>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/main/benchmarks/paper/docs/POLYBENCH_REPRODUCE.md>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/main/benchmarks/paper/docs/POLYBENCH_TTFI_REPRODUCE.md>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/main/benchmarks/paper/docs/WAPM_TTFI_REPRODUCTION.md>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/main/benchmarks/paper/docs/XLSX_FORMAT.md>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/main/benchmarks/paper/benchmarks/polybenchc/build.sh>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/main/benchmarks/paper/benchmarks/polybenchc/BUILD.md>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/main/benchmarks/paper/benchmarks/fib/README.md>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/main/benchmarks/paper/runtimes/dtvm/BUILD.md>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/main/benchmarks/paper/runtimes/dtvm_main/version.txt>
- **Sources the enricher read:**
  - <https://github.com/DTVMStack/DTVM>
  - <https://github.com/DTVMStack/DTVM/commits/main>
  - <https://github.com/DTVMStack/DTVM/issues>
  - <https://github.com/DTVMStack/DTVM/commit/882c83155>
  - <https://github.com/DTVMStack/DTVM/commit/c3c3fd856>
  - <https://github.com/DTVMStack/DTVM/commit/c3c3fd856d693d33be05ba25c5e6969a58be7e1f>
  - <https://github.com/DTVMStack/DTVM/tree/main/src>
  - <https://github.com/DTVMStack/DTVM/tree/main/src/host>
  - <https://github.com/DTVMStack/DTVM/tree/main/src/host/env>
  - <https://github.com/DTVMStack/DTVM/tree/main/src/compiler>
  - <https://github.com/DTVMStack/DTVM/tree/main/src/compiler/wasm_frontend>
  - <https://github.com/DTVMStack/DTVM/tree/main/docs/changes>
  - <https://github.com/DTVMStack/DTVM/tree/main/tests/wast>
  - <https://github.com/DTVMStack/DTVM/tree/main/benchmarks/paper/scripts>
  - <https://github.com/DTVMStack/DTVM/tree/main/benchmarks/paper/docs>
  - <https://github.com/DTVMStack/DTVM/tree/main/benchmarks/paper/benchmarks/overflow>
  - <https://github.com/DTVMStack/DTVM/tree/main/benchmarks/paper/runtimes/wasmtime-45.0.0>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/README.md>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/docs/user-guide.md>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/src/zetaengine.h>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/src/zetaengine-c.h>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/src/runtime/config.h>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/src/utils/statistics.cpp>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/src/utils/statistics.h>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/src/cli/dtvm.cpp>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/src/action/bytecode_visitor.h>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/src/action/module_loader.cpp>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/src/host/env/env.cpp>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/src/compiler/README.md>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/src/compiler/wasm_frontend/wasm_mir_compiler.cpp>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/src/common/defines.h>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/src/runtime/module.cpp>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/docs/changes/2026-05-28-wapm-ttfi-compile-time-report/README.md>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/c3c3fd856/src/utils/statistics.cpp>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/README.md>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/REPRODUCE.md>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/VERSIONS.md>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/ENVIRONMENT.md>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/SOURCES.md>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/docs/POLYBENCH_TTFI_REPRODUCE.md>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/docs/POLYBENCH_REPRODUCE.md>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/docs/WAPM_TTFI_REPRODUCTION.md>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/docs/XLSX_FORMAT.md>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/scripts/README.md>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/scripts/common.sh>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/scripts/avg_compile_time.py>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/scripts/infer_lazy_timing.py>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/scripts/bench_polybench_timing.sh>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/scripts/run_polybench_ttfi_round.sh>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/scripts/run_polybench_ttfi_compare.sh>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/scripts/run_lazy_ttfi_est.sh>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/scripts/run_wasmtime_ttfi_compare.sh>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/scripts/run_wasmer_ttfi_compare.sh>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/scripts/run_polybench.sh>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/benchmarks/overflow/README.md>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/benchmarks/overflow/REPRODUCE_fib_overflow_5way.md>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/benchmarks/overflow/build.sh>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/benchmarks/overflow/perf_test_swap_pool.cpp>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/benchmarks/overflow/fib_recursive.cpp>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/benchmarks/overflow/perf_test_fib.cpp>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/benchmarks/overflow/run_dtvm.sh>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/benchmarks/overflow/run_wasmtime45.sh>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/runtimes/dtvm/BUILD.md>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/runtimes/dtvm_main/README.md>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/runtimes/dtvm_main/version.txt>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/runtimes/wasmtime-31.0.0/patches/ttfi-report.patch>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/runtimes/wasmtime-45.0.0/README.md>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/runtimes/wasmer-7.1.0/README.md>
  - <https://raw.githubusercontent.com/DTVMStack/DTVM/HEAD/benchmarks/paper/runtimes/wasmer-5.0.4/README.md>
  - WebSearch: DTVM ZetaEngine wasm benchmark evmone Wasmtime (snippets of arxiv.org/abs/2504.16552)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/dtvmstack/dtvm`) · [data/wave13/enrich/raw/github_com_dtvmstack_dtvm.json](../../../data/wave13/enrich/raw/github_com_dtvmstack_dtvm.json) (enrichment confidence 0.8)

</details>
