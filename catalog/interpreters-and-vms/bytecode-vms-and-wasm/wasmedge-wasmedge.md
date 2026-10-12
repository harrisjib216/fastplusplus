# WasmEdge

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> C++ WebAssembly runtime whose LLVM AOT mode ties Wasmtime and beats V8 and wazero on libsodium; its interpreter is slow.

| | |
|---|---|
| **Beats** | Wasmtime, Wasmer (Cranelift, LLVM, Singlepass), V8 (Node.js) and wazero |
| **Claimed result** | README: 'the fastest Wasm VM' (backed by its authors' 2021 IEEE Software paper, not opened). 2022-12 libsodium suite (derived from page data, geomean of per-test time ratios over the 61 tests that also have a native result): WasmEdge 0.97x the time of Wasmtime (1.03x faster), 1.00x Wasmer Cranelift, 0.86x Node/V8 (1.17x faster), 0.31x Wasmer Singlepass, 0.21x wazero; 1.16x slower than Wasmer LLVM; 3.35x native, against 2.30x native for WAMR iwasm and 2.36x for WABT wasm2c, so WasmEdge is mid-pack, not fastest. 2026 rerun (Frank Denis, 'Performance of WebAssembly runtimes in 2026', search snippet only): WasmEdge with --run-mode=aot 1.74x native vs Wasmtime 46.0.0 2.41x and Wasmer 7.1.0 2.08x without wide arithmetic (about 1.39x faster than Wasmtime, derived from snippet numbers). |
| **Workload** | libsodium benchmark suite, 2022-12 run: 61 tests with results for every listed runtime plus native. |
| **Metric** | throughput |
| **Hardware** | AMD Zen 2 cloud instance at Scaleway, tests pinned to one core, each test run 200 times (search snippet of the blocked 00f.net 2023-01-04 post; not stated in the repo) |
| **Adoption** | 10.8k stars (CNCF sandbox project) |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/WasmEdge/WasmEdge) · [benchmark](https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/wasmedge.csv) |

## Verdict

In Frank Denis's 2022-12 libsodium WebAssembly run (jedisct1/webassembly-benchmarks CSVs; per the blocked 2023 post a Zen 2 Scaleway instance with tests pinned to one core), WasmEdge AOT took 0.97x Wasmtime's time, 1.00x Wasmer Cranelift's, 0.86x Node/V8's and 0.21x wazero's, but 1.16x Wasmer LLVM's, 1.46x WAMR AOT's and 1.42x wasm2c's (geomean over the 61 tests with a native result; I recomputed these from the CSVs), and 3.35x native; including the 8 short tests without a native result it is 1.07x slower than Wasmtime. The README's 'fastest Wasm VM' claim rests on the authors' own 2021 IEEE Software paper, which is not reachable here, and is not supported by this independent data.

## Use it when

- Long-running server or edge workloads where you can AOT-compile modules ahead of deployment and want near-Wasmtime or better throughput: 64-bit-multiply-heavy crypto (ed25519, curve25519 box/sign/scalarmult) ran in 0.55-0.60x Wasmtime's time in the 2022-12 libsodium run.
- Workloads that should beat V8/Node.js or wazero on compute: geomean 0.86x Node's time and 0.21x wazero's over 61 libsodium tests.
- When you need the WasmEdge ecosystem: LlamaEdge/WASI-NN inference plug-ins, crun and runwasi Kubernetes integration, WasmEdge socket and database extensions.
- C or C++ hosts that want a C API (including wasm.h since 0.18.0) and a CMake build, on Linux x86-64/aarch64, macOS, Windows, Android or OpenHarmony.

## Skip it when

- If you want the fastest AOT engine: in the same 2022-12 libsodium data WAMR's LLVM AOT (iwasm) and wasm2c were about 1.46x and 1.42x faster and Wasmer LLVM 1.16x faster; the 2026 rerun (search snippet only) still puts WAMR AOT at 1.57-1.59x native against WasmEdge's 1.74x.
- Interpreter-only deployments (iOS, W^X, no LLVM): the interpreter was 8.42x (M4 Max E-cores) and 9.28x (A12) the fastest of seven interpreters in the 2026-09-22 rebeckerspecialties comparison, against 1.01-1.04x for wasm3 and 1.38-1.63x for WAMR fast-interp; in the wasmi-benchmarks execute geomean it was x145.74 of the fastest on EPYC 7763 (x142.45 M4 Pro, x110.01 Xeon 8573C) against x12.40 for Wasmi v2; issue #2748 timed it at 91.5 s against 15.2 s for Wasmi and 17.7 s for WAMR on one module.
- Small-call, SHA-2/HMAC-heavy guest code: WasmEdge took 2.2-3.4x Wasmtime's time on libsodium hash, hash3, auth, auth2, auth6 and kdf in 2022-12, while winning on curve arithmetic.
- Multi-threaded hosts sharing one VM: the README says 'Currently, WasmEdge is not yet thread-safe'.
- Wasm GC guests that allocate continuously: the interpreter never collected GC structs during an instance's lifetime in the 2026-09-22 comparison (gc_trees peaked at 295 MB and still held 145 MB after the case).

## How it is fast

Speed comes from ahead-of-time compilation: `wasmedge compile` (formerly wasmedgec) lowers Wasm to LLVM IR, optimises it at O2 by default (O0-O3, s, z selectable) and emits a native shared library or a 'universal Wasm' file carrying the native code in a custom section, tuned for the host CPU name and features unless --generic-binary is given. 0.18.0 also inlines memory.size, table.size/get/set and the call_indirect dispatch into compiled code and maps SIMD min/max/abs to LLVM intrinsics. The interpreter is a plain switch dispatch over the loaded instruction list with an operand-stack manager (lib/executor/engine/engine.cpp), with no register-IR rewrite, which is why it trails the faster interpreters.

## Compared with alternatives

Pick WasmEdge over WAMR or wasm2c when you need its WASI-NN/LlamaEdge plug-ins, Kubernetes integrations or full Wasm 3.0 support in AOT, and can accept AOT code about 1.4x slower than WAMR AOT or wasm2c on libsodium; for interpreter-only targets pick wasm3, WAMR fast-interp or Wasmi instead, since WasmEdge's interpreter was 5-12x slower than theirs (8.42 vs 1.01-1.63 on M4 Max E-cores; x145.74 vs x12.40-17.07 on EPYC 7763 in wasmi-benchmarks).

## Integration

| | |
|---|---|
| **Form** | shared lib (libwasmedge) or static lib, CMake build; prebuilt CLI and libraries via installer |
| **Dependencies** | LLVM and LLD for AOT/JIT (WASMEDGE_USE_LLVM, on by default; off gives an interpreter-only build); spdlog, fmt, simdjson and blake3 (system copies or pinned FetchContent copies); Threads; std::filesystem; zstd/zlib when linking LLVM statically; plug-ins pull their own (OpenSSL, llama.cpp, OpenCV, ...) |
| **Minimum toolchain** | C++17 compiler, CMake 3.18; LLVM version handling covers roughly LLVM 13 through 23 in the build scripts (exact minimum not documented) |
| **Platforms** | Linux x86-64 and aarch64, macOS x86-64 and Apple silicon, Windows 10, Android, seL4, OpenWrt, OpenHarmony, Raspberry Pi, s390x; RISC-V marked work in progress |
| **Thread safety** | README: 'Currently, WasmEdge is not yet thread-safe'; 0.18.0 removed getter locks from the hot path and fixed data races in store teardown, but no thread-safety guarantee is documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness trap: since 0.17.0 the default run mode is the interpreter and an AOT-compiled universal Wasm file runs interpreted (its native section ignored) unless --run-mode=aot is passed; since 0.18.0 (PR #5292) a native .so input is rejected outright without it. A script in the style of libsodium's wasi-test-wrapper.sh (`wasmedgec x.wasm x.so && wasmedge x.so`) therefore measures the interpreter on 0.17.x and fails on 0.18.0; the 2026 rerun had to force --run-mode=aot.
- The 2022-12 numbers come from libsodium's own harness: the wrapper runs `wasm-opt -O4` on every module, AOT-compiles with wasmedgec and runs the .so, and cmptest.h times ITERATIONS calls of the test body inside the guest with clock_gettime and printf compiled out. Startup and AOT compile time are therefore excluded, so WasmEdge's 2-3x losses on the short tests are not process startup as the verifier assumed; the cause is unidentified. A candidate: WasmEdge AOT indirect calls were about 10x slower than WAMR's (issue #2444: 1M function-pointer calls 26.8 ms vs 2.77 ms; closed by PR #5088, and 0.18.0 inlined call_indirect dispatch in #4613), and libsodium routes poly1305 and randombytes through function-pointer tables. The WasmEdge version, compiler and flags of the 2022-12 run are not recorded.
- AOT artifacts are host-specific native code loaded with dlopen: they target the build machine's CPU features unless --generic-binary is used, the AOT binary format was bumped to version 3 in 0.18.0 (older artifacts must be recompiled), and before PR #5292 a .so's initialisers ran at load time even in interpreter mode, so only load AOT files you built yourself.
- Security: CVE-2025-69261 (GHSA-89fm-8mr7-gg4m, integer wrap in MemoryInstance::getSpan's size check) was fixed in 0.15.1, and 0.18.0 lists many hardening fixes (WASI symlink escape outside the preopen, OOB write via stale try_table handlers, memory64 bounds checks in AOT); only 0.17.1 and 0.16.4 are listed as supported in SECURITY.md.

## Known shortcomings

- Derived from the jedisct1 2022-12 CSVs, WasmEdge only ties the Cranelift runtimes (1.07x slower than Wasmtime once the 8 short non-native tests are counted), beats V8 by 1.17x, and loses to Wasmer LLVM (1.16x), WAMR iwasm (1.46x) and wasm2c (1.42x), so the README's 'fastest' claim is unsupported; its interpreter mode is the slowest of 7 (8.42x). The 2026 rerun (AOT 1.74x native vs Wasmtime 2.41x) is snippet only.
- Enricher: since 0.17.0 the default run mode is the interpreter and AOT universal-wasm files run interpreted without --run-mode=aot, and since 0.18.0 (PR #5292) .so input without that flag is rejected, so a libsodium-style 'wasmedgec x.wasm x.so && wasmedge x.so' measures the interpreter on 0.17.x and fails on 0.18.0. The libsodium cmptest.h times the loop inside the guest with printf compiled out, so the 2-3x losses on short tests are not per-run overhead (slow AOT indirect calls, issue #2444, are a candidate cause, since fixed); the 2022-12 WasmEdge version is unrecorded, the README says not yet thread-safe, the interpreter never frees GC structs, CVE-2025-69261 fixed in 0.15.1.

## Caveats and trade-offs

Parity with Wasmtime and Wasmer Cranelift only: the 3% edge over Wasmtime on the 61 native-comparable tests reverses to WasmEdge 1.07x slower than Wasmtime (and 1.05x slower than Wasmer Cranelift) when the 8 short tests without a native result are included (hash3, onetimeauth, secretbox, secretbox2, shorthash, siphashx24, stream3, stream4, where WasmEdge takes 2-3x longer, likely fixed per-run overhead). Slower than Wasmer LLVM (1.16x), WAMR iwasm (1.46x) and wasm2c (1.42x) in the same 2022-12 data, contradicting the README's 'fastest' claim; the README claim rests on a 2021 IEEE Software paper by WasmEdge's own authors that I could not open (IEEE blocked). The CSVs do not say WasmEdge ran AOT (implied by 3.35x native; the 2026 post had to force --run-mode=aot). The 2026 numbers are snippet only (00f.net blocked) and no 2026 results repo exists (jedisct1/webassembly-benchmarks holds only 2021-Q1 and 2022-12 and is archived). In interpreter mode WasmEdge is the slowest of seven interpreters, 8.42x the fastest geomean on M4 Max E-cores (rebeckerspecialties/wasm-benchmark docs/runtime-comparison-2026-09-22.md). Compiler and flags unknown.

Speed needs the LLVM-based AOT compiler step; the interpreter mode is among the slowest: geomean 8.42x the fastest on the M4 Max E-cores (REB doc) and 145.74x vs 1.15x for Wasmtime Cranelift on EPYC 7763 in the wasmi-benchmarks execute plot. Large dependency footprint.

## Maintenance

Very active CNCF sandbox project (0.18.0 released 2026-10-05, Apache-2.0, 10.8k stars) usable as a library today, but it is a large LLVM-dependent C++ code base and its benchmark speed depends on using AOT mode explicitly.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent, well-known third-party suite (Frank Denis's libsodium WebAssembly benchmark, jedisct1/webassembly-benchmarks 2022-12/res/\*.csv, with the wasm binaries in 2022-12/wasm) puts WasmEdge beside Wasmtime, Wasmer, V8/Node, wazero, WAMR and native; I re-derived the record's ratios exactly from the CSVs. Not A: the repo states no compiler, flags or CPU model (the blocked 2023-01-04 blog post says only a Scaleway Zen 2 instance, snippet only).
- **Verifier notes:** Derived ratios in the record reproduce exactly (0.968/1.002/0.856/0.313/0.214/1.157/3.347 over 61 tests); kept at B on the independent suite, but WasmEdge only ties Wasmtime/Wasmer Cranelift, beats V8, wazero, Singlepass and Bun, and loses to Wasmer LLVM, WAMR and wasm2c in 2022-12, so 'fastest Wasm VM' is not supported by the cited data; a 2026 rerun (snippet only) shows WasmEdge AOT 1.74x native vs Wasmtime 2.41x. Metadata (Apache-2.0, 10.8k stars, last commit 2026-10-06, not archived) confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/wasmedge.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/wasmtime.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/wasmer-cranelift.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/wasmer-llvm.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/wasmer-singlepass.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/node.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/wazero.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/native.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/iwasm.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/wasm2c.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/wasm3.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/bun.csv>
  - <https://github.com/jedisct1/webassembly-benchmarks>
  - <https://github.com/jedisct1/webassembly-benchmarks/tree/master/2022-12>
  - <https://github.com/jedisct1/webassembly-benchmarks/tree/master/2022-12/res>
  - <https://github.com/jedisct1?tab=repositories&q=wasm&type=&language=&sort=>
  - <https://github.com/WasmEdge/WasmEdge>
  - <https://github.com/WasmEdge/WasmEdge/commits>
  - <https://github.com/rebeckerspecialties/wasm-benchmark/blob/main/docs/runtime-comparison-2026-09-22.md>
- **Sources the enricher read:**
  - <https://github.com/WasmEdge/WasmEdge>
  - <https://raw.githubusercontent.com/WasmEdge/WasmEdge/HEAD/README.md>
  - <https://raw.githubusercontent.com/WasmEdge/WasmEdge/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/WasmEdge/WasmEdge/HEAD/cmake/Helper.cmake>
  - <https://raw.githubusercontent.com/WasmEdge/WasmEdge/HEAD/lib/llvm/CMakeLists.txt>
  - <https://raw.githubusercontent.com/WasmEdge/WasmEdge/HEAD/lib/llvm/compiler.cpp>
  - <https://raw.githubusercontent.com/WasmEdge/WasmEdge/HEAD/lib/executor/engine/engine.cpp>
  - <https://raw.githubusercontent.com/WasmEdge/WasmEdge/HEAD/lib/driver/runtimeTool.cpp>
  - <https://raw.githubusercontent.com/WasmEdge/WasmEdge/HEAD/include/common/configure.h>
  - <https://raw.githubusercontent.com/WasmEdge/WasmEdge/HEAD/Changelog.md>
  - <https://raw.githubusercontent.com/WasmEdge/WasmEdge/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/WasmEdge/WasmEdge/HEAD/docs/ROADMAP.md>
  - <https://raw.githubusercontent.com/WasmEdge/docs/main/docs/start/build-and-run/aot.md>
  - <https://raw.githubusercontent.com/WasmEdge/docs/main/docs/start/wasmedge/features.md>
  - <https://raw.githubusercontent.com/WasmEdge/docs/main/docs/embed/c/intro.md>
  - <https://raw.githubusercontent.com/WasmEdge/docs/main/docs/start/build-and-run/cli.md>
  - <https://github.com/WasmEdge/WasmEdge/security/advisories>
  - <https://github.com/WasmEdge/WasmEdge/pull/5292>
  - <https://github.com/WasmEdge/WasmEdge/issues?q=is%3Aissue+performance+slow>
  - <https://github.com/WasmEdge/WasmEdge/issues/2963>
  - <https://github.com/WasmEdge/WasmEdge/issues/2748>
  - <https://github.com/WasmEdge/WasmEdge/issues/2444>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/wasmedge.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/wasmtime.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/wasmer-cranelift.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/wasmer-llvm.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/wasmer-singlepass.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/node.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/wazero.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/native.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/iwasm.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/wasm2c.csv>
  - <https://raw.githubusercontent.com/jedisct1/libsodium/stable/test/default/wasi-test-wrapper.sh>
  - <https://raw.githubusercontent.com/jedisct1/libsodium/stable/test/default/cmptest.h>
  - <https://raw.githubusercontent.com/jedisct1/libsodium/stable/test/default/hash3.c>
  - <https://raw.githubusercontent.com/jedisct1/libsodium/stable/src/libsodium/crypto_onetimeauth/poly1305/onetimeauth_poly1305.c>
  - <https://raw.githubusercontent.com/jedisct1/libsodium/stable/src/libsodium/randombytes/randombytes.c>
  - <https://github.com/jedisct1/libsodium/tree/master/test/default>
  - <https://github.com/jedisct1/libsodium/commits/master/test/default/wasi-test-wrapper.sh>
  - <https://raw.githubusercontent.com/rebeckerspecialties/wasm-benchmark/HEAD/docs/runtime-comparison-2026-09-22.md>
  - WebSearch: "Performance of WebAssembly runtimes in 2026" WasmEdge run-mode aot (00f.net post itself EGRESS_BLOCKED; snippet only)
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-execute.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/apple-m4-pro/lin-scale/geomean-execute.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/intel-xeon-platinum-8573c/lin-scale/geomean-execute.svg>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/wasmedge/wasmedge`) · [data/wave12/enrich/raw/github_com_wasmedge_wasmedge.json](../../../data/wave12/enrich/raw/github_com_wasmedge_wasmedge.json) (enrichment confidence 0.75)

</details>
