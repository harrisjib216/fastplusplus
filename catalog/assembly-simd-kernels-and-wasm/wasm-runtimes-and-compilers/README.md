# WebAssembly runtimes and compilers

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md)</sub>

**What these beat:** wasmtime, wasmer, V8, WAMR, wasm-opt  
**6 entries:** 1 tier A · 1 tier B · 3 tier C · 1 tier D · 6 copyable, 0 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**wasman**](c0mm4nd-wasman.md) | Pure-Go, dependency-free WebAssembly MVP interpreter with an optional arm64/amd64 JIT; beats wazero's interpreter 1.1-1.8x on micro-loops. | **A** | Go | MIT | 🟢 active |
| 2 | [**VectorVisor (GPU binary translator for WebAssembly)**](samginzburg-vectorvisor.md) | Binary translator that runs thousands of copies of a single-threaded Wasm program on an OpenCL GPU; per dollar it beats native x86 CPU VMs only on some compute-bound… | **B** | Rust | Apache-2.0 | 🟡 stale |
| 3 | [**DTVM (ZetaEngine lazy-JIT Wasm VM)**](dtvmstack-dtvm.md) | C++ deterministic Wasm/EVM JIT for smart contracts. Its lazy JIT reaches first invocation about 20x sooner than Wasmtime's eager compile. | **C** | C++ | Apache-2.0 | 🟢 active |
| 4 | [**Cage (wasmtime-mte, MTE-based memory safety and bounds…**](tum-dse-wasmtime-mte.md) | Research fork of Wasmtime 16 that swaps wasm64 software bounds checks for Arm MTE tag checks and adds MTE/PAC memory safety. | **C** | Rust | Apache-2.0 WITH… | 🟢 active |
| 5 | [**KinoWASM (KinoRuntime)**](a-kinoshita2026-kinowasm.md) | Embeddable C WebAssembly interpreter (tail-call threaded, register-TOS); first-party CoreMark 2.5x WAMR fast-interp, 1.2x wasm3 on Windows. | **C** | C | MIT | 🟢 active |
| 6 | [**WasmKit register-based interpreter (swiftwasm/WasmKit)**](swiftwasm-wasmkit.md) | Pure-Swift embeddable WebAssembly interpreter; register-based VM scores 7.5x its old stack interpreter on CoreMark, roughly level with wasm3. | **D** | Swift | MIT (runtime modules); the… | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
