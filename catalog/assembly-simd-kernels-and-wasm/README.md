# Assembly, SIMD and WebAssembly

<sub>[fastpp](../../README.md) › [Catalog](../README.md)</sub>

Hand-written assembly, SIMD libraries, assemblers and WebAssembly toolchains measured against compiler output, libc routines and native builds.

**311 entries in 7 categories:** 42 tier A · 26 tier B · 189 tier C · 54 tier D

| Category | Entries | A | B | C | D | What they beat |
|---|--:|--:|--:|--:|--:|---|
| [Assemblers and assembly tooling](assemblers-and-asm-tooling/README.md) | 34 | 7 | 4 | 16 | 7 | GNU as, NASM, MASM (assemble time, output quality) |
| [Assembly-level string and memory routines](asm-level-string-and-memory/README.md) | 34 | 7 | 0 | 19 | 8 | glibc/musl string.h, std::string ops |
| [AssemblyScript and WebAssembly languages](assemblyscript-and-wasm-langs/README.md) | 48 | 1 | 2 | 33 | 12 | TypeScript/JS in V8, C++ via Emscripten |
| [Hand-written assembly kernels](hand-written-asm-kernels/README.md) | 48 | 9 | 0 | 35 | 4 | the compiler's -O3 output for the same C/C++ function; the libc/stdlib version (memcpy… |
| [SIMD intrinsics libraries](simd-intrinsics-libraries/README.md) | 67 | 11 | 7 | 41 | 8 | scalar C/C++ reference, Highway, xsimd, Eigen, std::simd |
| [WebAssembly libraries and apps](wasm-libraries-and-apps/README.md) | 74 | 6 | 12 | 42 | 14 | the same library compiled natively; the JS equivalent in-browser |
| [WebAssembly runtimes and compilers](wasm-runtimes-and-compilers/README.md) | 6 | 1 | 1 | 3 | 1 | wasmtime, wasmer, V8, WAMR, wasm-opt |

## Most-adopted tier A picks

Tier A, copyable and actively maintained, ordered by GitHub stars.

| # | Project | What it is | Category | Tier | Language | License | Status |
|--:|---|---|---|:-:|---|---|---|
| 1 | [**Dioxus (web renderer)**](wasm-libraries-and-apps/dioxuslabs-dioxus.md) | Rust UI framework whose web renderer runs a WebAssembly virtual DOM; about 1.43x faster than React 19.2 hooks in js-framework-benchmark. | [WebAssembly libraries and apps](wasm-libraries-and-apps/README.md) | **A** | Rust | Apache-2.0 OR MIT | 🟢 active |
| 2 | [**Zydis**](assemblers-and-asm-tooling/zyantific-zydis.md) | C11 x86/x86-64 decoder, formatter and encoder with no allocation; decode+format 1.2-1.35x Capstone's throughput in disas-bench. | [Assemblers and assembly tooling](assemblers-and-asm-tooling/README.md) | **A** | C | MIT | 🟢 active |
| 3 | [**zip.js (@zip.js/zip.js WebAssembly zlib codec)**](wasm-libraries-and-apps/gildas-lormeau-zip-js.md) | ZIP library whose bundled WebAssembly zlib inflates about 2x faster than pako/jszip and its own JS port. | [WebAssembly libraries and apps](wasm-libraries-and-apps/README.md) | **A** | JavaScript | BSD-3-Clause | 🟢 active |
| 4 | [**iced (iced-x86)**](assemblers-and-asm-tooling/icedland-iced.md) | Rust x86/x64 decoder, formatter, encoder and assembler; decodes 4-7x faster than Zydis, XED and bddisasm in disas-bench. | [Assemblers and assembly tooling](assemblers-and-asm-tooling/README.md) | **A** | Rust | MIT | 🟢 active |
| 5 | [**glam**](simd-intrinsics-libraries/bitshifter-glam-rs.md) | Rust f32/f64 3D game-math crate with SSE2/NEON storage; 2.5x faster Mat4 inverse than cgmath in mathbench. | [SIMD intrinsics libraries](simd-intrinsics-libraries/README.md) | **A** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 6 | [**Intel XED (x86 encoder decoder)**](assemblers-and-asm-tooling/intelxed-xed.md) | Intel's own x86/x86-64 decoder and encoder in C; decodes faster than full-mode Zydis, roughly ties or trails Capstone once formatting is included. | [Assemblers and assembly tooling](assemblers-and-asm-tooling/README.md) | **A** | C | Apache-2.0 | 🟢 active |
| 7 | [**bddisasm**](assemblers-and-asm-tooling/bitdefender-bddisasm.md) | Bitdefender's x86/x64 instruction decoder in C with rich operand metadata; decode+format 1.4-1.8x Capstone's throughput in disas-bench. | [Assemblers and assembly tooling](assemblers-and-asm-tooling/README.md) | **A** | C | Apache-2.0 | 🟢 active |
| 8 | [**Rust portable SIMD (std::simd / portable-simd)**](simd-intrinsics-libraries/rust-lang-portable-simd.md) | Rust nightly's std::simd: one portable Simd&lt;T, N&gt; type that beat scalar and autovectorized Rust loops 5-13x in a byte count. | [SIMD intrinsics libraries](simd-intrinsics-libraries/README.md) | **A** | Rust | Apache-2.0 OR MIT | 🟢 active |
| 9 | [**ultraviolet**](simd-intrinsics-libraries/termhn-ultraviolet.md) | Rust graphics/game linear algebra with SoA 'wide' f32x4/f32x8 types; about 2-5x glam's one-lane code on batched math. | [SIMD intrinsics libraries](simd-intrinsics-libraries/README.md) | **A** | Rust | MIT OR Apache-2.0 OR Zlib | 🟢 active |
| 10 | [**zeebo/blake3 (Go BLAKE3 with avo-generated AVX-512, AVX2…**](hand-written-asm-kernels/zeebo-blake3.md) | Go BLAKE3 with avo-generated AVX-512, AVX2, SSE4.1, NEON and SVE2 kernels; 6-8x its own pure-Go path on large inputs. | [Hand-written assembly kernels](hand-written-asm-kernels/README.md) | **A** | Go | MIT | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
