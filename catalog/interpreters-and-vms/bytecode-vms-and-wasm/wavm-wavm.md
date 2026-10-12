# WAVM

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> LLVM-based ahead-of-time WebAssembly runtime in C++; fastest total in the 2021 libsodium shootout against Wasmtime, Wasmer and V8.

| | |
|---|---|
| **Beats** | Wasmtime, Wasmer (LLVM, Cranelift, Singlepass backends) and V8 (Node.js) |
| **Claimed result** | jedisct1 libsodium shootout 2021 Q1 (macOS logs, 59 tests, compile time excluded): total time 1.43x better than wasmtime, 1.13x than node, 1.17x than wasmer-llvm, but pwhash_scrypt alone is 84% of the lead over wasmer-llvm; per-test geomeans against WAVM are wasmer-llvm 1.09x, node 1.20x, wasmtime 1.47x (derived from page data). wasmer-llvm is faster on 16 tests, node on 2, wasmtime on 1 (auth3). A 2026 rerun reportedly puts wasmer ahead (snippet only). |
| **Workload** | libsodium 1.0.18 built to WASI (clang 11.1.0, wasm-opt -O4) and run on every runtime with ./dist/wasm32-wasi.sh --bench; per-test timings across the crypto and codec test suite. |
| **Metric** | throughput |
| **Hardware** | macOS x86_64 laptop (CPU model not stated) and a Linux x86_64 machine for the LLVM-runtime comparison |
| **Compiler and flags** | All runtimes compiled from git on 2021-02-21 in release mode (Node.js from stock binaries); libsodium 1.0.18-stable built with LLVM 11.1.0 (Homebrew) via ./dist/wasm32-wasi.sh --bench, output pre-optimized with wasm-opt -O4; native and WebAssembly builds use the same default optimization flags; runtimes invoked through libsodium's test/default/wasi-test-wrapper.sh. |
| **Adoption** | 2.8k stars |
| **Last commit** | 2026-04-04 |
| **Links** | [repository](https://github.com/WAVM/WAVM) · [benchmark](https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2021-Q1/README.md) |

## Verdict

In Frank Denis's 2021-Q1 libsodium 1.0.18 WASI benchmark (LLVM 11.1.0 plus wasm-opt -O4, all runtimes built from git on 2021-02-21, unnamed Intel macOS laptop, each test timing 128 iterations inside the guest with CLOCK_MONOTONIC, compile and initialization excluded, one logged value per test), WAVM had the lowest summed time: 4.63 vs Node/V8 5.23, wasmer-llvm 5.44, wasmtime 6.65 and lucet 11.61 (native 2.04). My recount of the 59 per-test logs gives geomean time ratios to WAVM of wasmtime 1.47x, node 1.20x and wasmer-llvm 1.09x, with wasmer-llvm faster on 16 tests, node on 2 and wasmtime on 1 (auth3), so the page's 'every single test' and 'about 15% faster than wasmer' overstate a per-test margin of about 9%; the 2026 rerun (search snippet only) puts Wasmer first with WAVM close.

## Use it when

- Long-running, compute-heavy guest code (crypto, codecs, number crunching) where peak throughput on plain WebAssembly matters and LLVM compile time is amortized.
- Hosts that can precompile or cache object code (`wavm compile`, object cache) so restarts do not pay the LLVM compile again, e.g. serverless designs like FAASM that the benchmark author points to.
- C++ embedders that need many post-MVP proposals in one engine: SIMD, threads, exception handling, multi-memory, memory64 and WASI.
- 64-bit x86-64 or AArch64 hosts on Windows, macOS or Linux with 4 KB pages (all six combinations are in CI).

## Skip it when

- Startup- or latency-sensitive work and many short-lived modules: the whole module goes through LLVM O2 before the first instruction runs; the EOS VM README calls WAVM's compile times 'extremely long and unpredictable', and the benchmark numbers exclude compile time.
- Running untrusted code next to sensitive data: the README says WAVM is vulnerable to some side-channel attacks such as Spectre variant 2 and recommends OS-process isolation.
- 32-bit hosts or address-space-limited environments (ulimit -v, many instances): the runtime needs a 64-bit host and reserves 8 GB plus guard pages per 32-bit memory.
- AArch64 Linux with 64 KB kernel pages: issue #391 (2026-08, NVIDIA GH200) reports a SEGV during runtime creation, with no maintainer reply.
- Teams that need versioned releases or a deep maintainer bench: one maintainer, only nightly tags, a four-year gap from 2022-05 to 2026-04, and a hard dependency on LLVM 20+ (a patched WAVM-LLVM 21 is recommended, especially on macOS).

## How it is fast

Each module is translated to LLVM IR and run through LLVM's default O2 module pipeline for the host target machine, so code is optimized up front and tuned to the running CPU instead of being tiered up from a baseline compiler. Every 32-bit linear memory reserves 8 GB of virtual address space plus guard pages, so a 32-bit index plus 32-bit offset can never leave the reservation and bounds checks are elided; out-of-bounds accesses fault on a guard page and signal handlers turn the fault into a WebAssembly trap. The price is compile time, which can be cached (`wavm compile` precompiled objects, WAVM_OBJECT_CACHE_DIR with LMDB).

## Compared with alternatives

Pick WAVM over Wasmtime, Wasmer or WasmEdge when peak throughput on plain WebAssembly matters more than compile latency and you want an LLVM AOT engine with broad proposal support inside a C++ host; aWsm (13.4% vs WAVM's 28.1% slowdown over native in its paper) and wasm2c or w2c2 can run faster but need an offline C or LLVM compile step, and interpreters (WAMR, wasm3, Fizzy) start far faster but run code tens of times slower.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | LLVM 20+ (WAVM-LLVM 21 recommended); vendored BLAKE2, liblmdb (object cache) and libunwind |
| **Minimum toolchain** | C++17, CMake 3.16, LLVM 20; GCC or Clang on Linux, Xcode on macOS, Visual Studio 2022 on Windows |
| **Platforms** | x86-64 and AArch64 on Windows, macOS and Linux (CI-tested); 64-bit hosts only; x86 target CPU must support SSE 4.1; prebuilt macOS binaries are arm64 only |
| **Thread safety** | not documented in Runtime.h; the API separates Compartment (object ownership, garbage collection) from Context (execution state, createContext/cloneContext), and the WebAssembly threads proposal (shared memory, atomics) is supported |
| **Drop-in for the baseline** | partial — offers a WebAssembly C API binding (wavm-c.h) and a `wavm run` CLI with WASI, but its native C++ API (compartments, GC roots, contexts) is WAVM-specific and it has no Rust API like Wasmtime or Wasmer |

## Gotchas

- Each 32-bit linear memory reserves 8 GB of virtual address space plus guard bytes, so thousands of instances can exhaust address space or hit overcommit and ulimit -v limits (issue #245 asks why WebAssembly VMs take so much memory).
- Traps arrive through signal handlers on guard-page faults; wrap calls in catchRuntimeExceptions / unwindSignalsAsExceptions and check how they interact with the host's own SIGSEGV handlers.
- Runtime objects are garbage-collected per Compartment and must be held through GCPointer roots; raw pointers die at collectCompartmentGarbage, and bug #74 (open since 2018) says the GC does not scan functions on the stack.
- The benchmark totals are dominated by a few memory-hard tests: on WAVM's macOS logs pwhash_scrypt is 23.9% of the summed time and the top four tests 68%, and pwhash_scrypt alone accounts for 84% of WAVM's total-time lead over wasmer-llvm (my count from the per-test logs).

## Known shortcomings

- jedisct1 libsodium shootout, 2021 Q1, CPU model unstated: derived from the raw logs WAVM's total time is 1.43x better than wasmtime, 1.13x than node and 1.17x than wasmer-llvm, and wasmer-llvm is faster on 16 of 58 tests, so the record's 'every single test' claim was wrong and its singlepass ranking was corrected. A 2026 rerun reportedly puts wasmer ahead (snippet only).
- Enricher: recounting the 59 macOS logs, pwhash_scrypt alone is 84% of WAVM's total-time lead over wasmer-llvm and the top 4 tests are 68% of WAVM's total; per-test geomeans against WAVM are wasmer-llvm 1.09x, node 1.20x, wasmtime 1.47x, with wasmer-llvm faster on 16 tests, node on 2 and wasmtime on 1 (auth3), so '15% faster' and 'every single test' were overstated; compile time excluded. 8 GB reservation per memory, #391 SEGV on 64 KB-page aarch64, nightly-only releases, one maintainer.

## Caveats and trade-offs

Data are from February 2021 on an unnamed Intel macOS laptop plus an unnamed Linux x86_64 machine; WAVM was not run on ARM. The 'every single test' sentence is contradicted by the raw logs: wasmer-llvm beat WAVM on 16 of 58 macOS tests (mostly within 5%, auth3 at 0.46x and box2 at 0.83x of WAVM's time), so WAVM wins the totals, not every test. Reported times exclude module compilation/initialization, so WAVM's LLVM compile cost is not counted. The 2022-12 round in the same repo did not include WAVM (res/ has no wavm.csv), the repo was archived 2026-08-19, and the 2023 and 2026 posts on 00f.net are blocked here; a search snippet for the 2026 post says wasmer is the best performer with WAVM, WAMR and Wasmtime close, and that WAVM has the best optimizer (snippet only). WAVM's last commit is 2026-04-04 (a burst of fixes that day); its pace is slow.

LLVM-based compilation: the EOS VM README (github.com/AntelopeIO/eos-vm) calls WAVM compilation times 'extremely long and unpredictable'; LLVM dependency.

## Maintenance

Active again after a 2022-05 to 2026-04 gap: an LLVM 21 and C++17 overhaul plus fixes on 2026-04-02/04, nightly-only releases (VERSION 0.0.0-prerelease) and a single maintainer; BSD-3-Clause and copyable, but heavy to vendor because it needs LLVM 20+.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent shootout by the libsodium author (jedisct1/webassembly-benchmarks 2021-Q1) runs WAVM against wasmtime, wasmer (LLVM, Cranelift, Singlepass), Node.js/V8 and Lucet with public benchmark code (libsodium 1.0.18-stable dist/wasm32-wasi.sh --bench) and per-test raw logs, LLVM 11.1.0 and wasm-opt -O4 named; the CPU model is never stated ('machines with an Intel CPU', 'my laptop'), so not A.
- **Verifier notes:** Real independent evidence; ranking in the record was off (wasmtime beats wasmer-singlepass in the chart) and the 'every single test' quote is overstated per the raw logs, both corrected. Shortcomings: 2021-era data, CPU model unstated, wasmer-llvm faster on 16 of 58 tests, 2026 rerun reportedly puts wasmer ahead (snippet only).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/jedisct1/webassembly-benchmarks/blob/master/2021-Q1/README.md>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2021-Q1/README.md>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2021-Q1/macos.png>
  - <https://github.com/jedisct1/webassembly-benchmarks/tree/master/2021-Q1/output>
  - <https://github.com/jedisct1/webassembly-benchmarks/tree/master/2021-Q1/output/macos-x86_64>
  - <https://github.com/jedisct1/webassembly-benchmarks/tree/master/2021-Q1/output/macos-x86_64/wavm>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2021-Q1/output/macos-x86_64/wavm/auth.log>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2021-Q1/output/macos-x86_64/wasmtime/auth.log>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2021-Q1/output/macos-x86_64/wasmer-llvm/auth.log>
  - <https://github.com/jedisct1/webassembly-benchmarks>
  - <https://github.com/jedisct1/webassembly-benchmarks/tree/master/2022-12>
  - <https://github.com/jedisct1/webassembly-benchmarks/tree/master/2022-12/res>
  - <https://github.com/WAVM/WAVM>
  - <https://github.com/WAVM/WAVM/commits/master>
  - <https://raw.githubusercontent.com/WAVM/WAVM/HEAD/LICENSE.txt>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/WAVM/WAVM/HEAD/README.md>
  - <https://raw.githubusercontent.com/WAVM/WAVM/HEAD/Doc/Building.md>
  - <https://raw.githubusercontent.com/WAVM/WAVM/HEAD/Doc/GettingStarted.md>
  - <https://raw.githubusercontent.com/WAVM/WAVM/HEAD/Doc/CodeOrganization.md>
  - <https://raw.githubusercontent.com/WAVM/WAVM/HEAD/Doc/PortabilityMatrix.md>
  - <https://raw.githubusercontent.com/WAVM/WAVM/HEAD/VERSION>
  - <https://raw.githubusercontent.com/WAVM/WAVM/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/WAVM/WAVM/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/WAVM/WAVM/HEAD/Lib/Runtime/Memory.cpp>
  - <https://raw.githubusercontent.com/WAVM/WAVM/HEAD/Lib/LLVMJIT/LLVMCompile.cpp>
  - <https://raw.githubusercontent.com/WAVM/WAVM/HEAD/Include/WAVM/Runtime/Runtime.h>
  - <https://github.com/WAVM/WAVM/commits/master>
  - <https://github.com/WAVM/WAVM/releases>
  - <https://github.com/WAVM/WAVM/issues>
  - <https://github.com/WAVM/WAVM/issues/391>
  - <https://github.com/WAVM/WAVM/tree/master/ThirdParty>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2021-Q1/README.md>
  - <https://github.com/jedisct1/webassembly-benchmarks/tree/master/2021-Q1/output/macos-x86_64/wavm>
  - <https://raw.githubusercontent.com/jedisct1/libsodium/stable/test/default/cmptest.h>
  - <https://raw.githubusercontent.com/AntelopeIO/eos-vm/HEAD/README.md>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2021-Q1/output/macos-x86_64/wavm/pwhash_scrypt.log>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2021-Q1/output/macos-x86_64/wavm/auth3.log>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2021-Q1/output/macos-x86_64/wasmer-llvm/pwhash_scrypt.log>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2021-Q1/output/macos-x86_64/wasmer-llvm/auth3.log>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2021-Q1/output/macos-x86_64/node/pwhash_scrypt.log>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2021-Q1/output/macos-x86_64/node/auth3.log>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2021-Q1/output/macos-x86_64/wasmtime/pwhash_scrypt.log>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/master/2021-Q1/output/macos-x86_64/wasmtime/auth3.log>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/wavm/wavm`) · [data/wave12/enrich/raw/github_com_wavm_wavm.json](../../../data/wave12/enrich/raw/github_com_wavm_wavm.json) (enrichment confidence 0.75)

</details>
