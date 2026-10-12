# Compilers and front ends

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md)</sub>

**What these beat:** GCC, Clang, MSVC, rustc  
**7 entries:** 1 tier A · 1 tier B · 4 tier C · 1 tier D · 4 copyable, 3 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**TinyCC (tcc)**](tinycc-tinycc.md) | Tiny self-hosting C compiler/JIT that compiles about 9x faster than gcc -O0, trading away optimization. | **A** | C | LGPL-2.1 | 🟢 active |
| 2 | [**zapcc**](yrnkrn-zapcc.md) | zapcc: a Clang fork with a persistent caching server that rebuilds template-heavy C++ 1.2-3.3x faster than GCC/Clang. | **B** | C++ | NCSA | 🔴 abandoned |
| 3 | [**MIR / c2m (C2MIR)**](vnmakarov-mir.md) | Lightweight JIT toolkit whose C11 front-end (c2m) compiles a header-free C function \~80x faster than gcc -O2. | **C** | C | MIT | 🟢 active |
| 4 | [**rustc_codegen_cranelift (cg_clif)**](rust-lang-rustc-codegen-cranelift.md) | Drop-in Cranelift codegen backend for rustc that replaces LLVM to cut debug-build compile times. | **C** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 5 | [**Intel oneAPI DPC++/C++ Compiler (icpx)**](intel-llvm.md) | Intel's LLVM-based C++ compiler (icpx); under relaxed FP it ran a math-heavy pipeline 1.5-1.8x faster than GCC/Clang. | **C** | C++ | Apache-2.0 WITH… (study only) | 🟢 active |
| 6 | [**AMD C++ Compiler (AOCC)**](amd-com-en-developer-aocc-html.md) | AMD's closed-source LLVM/Clang-based C/C++/Fortran compiler for Zen whose binaries ran about 8% faster than GCC 11.2's. | **C** | C++ | Proprietary AMD EULA… (study only) | 🟢 active |
| 7 | [**Microsoft Visual C++ (MSVC cl.exe)**](learn-microsoft-com-en-us-cpp-build-reference-compiler-options.md) | Microsoft's closed C++ compiler; one Node.js report had it compiling \~2.5x faster than clang-cl, but only versus no-PCH clang-cl. | **D** | C++ | proprietary (closed-source… (study only) | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
