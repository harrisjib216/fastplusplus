# Assemblers and assembly tooling

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md)</sub>

**What these beat:** GNU as, NASM, MASM (assemble time, output quality)  
**34 entries:** 7 tier A · 4 tier B · 16 tier C · 7 tier D · 31 copyable, 3 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**Zydis**](zyantific-zydis.md) | C11 x86/x86-64 decoder, formatter and encoder with no allocation; decode+format 1.2-1.35x Capstone's throughput in disas-bench. | **A** | C | MIT | 🟢 active |
| 2 | [**iced (iced-x86)**](icedland-iced.md) | Rust x86/x64 decoder, formatter, encoder and assembler; decodes 4-7x faster than Zydis, XED and bddisasm in disas-bench. | **A** | Rust | MIT | 🟢 active |
| 3 | [**Intel XED (x86 encoder decoder)**](intelxed-xed.md) | Intel's own x86/x86-64 decoder and encoder in C; decodes faster than full-mode Zydis, roughly ties or trails Capstone once formatting is included. | **A** | C | Apache-2.0 | 🟢 active |
| 4 | [**bddisasm**](bitdefender-bddisasm.md) | Bitdefender's x86/x64 instruction decoder in C with rich operand metadata; decode+format 1.4-1.8x Capstone's throughput in disas-bench. | **A** | C | Apache-2.0 | 🟢 active |
| 5 | [**yaxpeax-x86**](iximeow-yaxpeax-x86.md) | Rust x86/x86-64 instruction decoder and formatter; in current disas-bench runs it decodes 5-9x faster than XED and Zydis. | **A** | Rust | 0BSD | 🟢 active |
| 6 | [**diStorm3**](gdabah-distorm.md) | Small table-driven x86/AMD64 decoder in C; decode+format runs 2.6-4.2x faster than Zydis, bddisasm, XED and Capstone in disas-bench. | **A** | C | BSD-3-Clause | 🔴 abandoned |
| 7 | [**udis86**](vmt-udis86.md) | Small table-driven C x86/x86-64 decoder; in decode-only mode it beat Zydis, bddisasm and XED, but it formats slowest. | **A** | C | BSD-2-Clause | 🔴 abandoned |
| 8 | [**Minotaur**](minotaur-toolkit-minotaur.md) | LLVM IR superoptimizer pass that synthesizes cheaper SIMD/scalar code; 1-7% faster than clang -O3 on GMP, libYUV, SPEC. | **B** | C++ | MIT | 🟢 active |
| 9 | [**STOKE**](stanfordpl-stoke.md) | Research stochastic superoptimizer for x86-64 that rewrites short loop-free assembly kernels to match or beat gcc -O3 and icc -O3 output. | **B** | C++ | Apache-2.0 | 🔴 abandoned |
| 10 | [**Unison**](unison-code-unison.md) | Constraint-programming register allocator and instruction scheduler for LLVM 3.8 that produces 1-10% faster or 1-4% smaller code than LLVM's heuristics. | **B** | Haskell | BSD-3-Clause | 🔴 abandoned |
| 11 | [**KeplerAs and SGEMM assembly (PPoPP 2017 artifact)**](paa-ncic-ppopp2017-artifact.md) | Kepler (sm_35) SASS assembler plus hand-scheduled SGEMM kernels that beat cuBLAS 7.0 by up to 1.15x on a Tesla K20m. | **B** | SASS assembly kernels | No repository-wide licence… | 🔴 abandoned |
| 12 | [**Keystone**](keystone-engine-keystone.md) | Embeddable multi-architecture assembler library cut down from LLVM 3.9's MC layer; claims over 10x smaller footprint than full LLVM. | **C** | C++ | GPL-2.0-only | 🟢 active |
| 13 | [**B2R2 (binary analysis framework, disassembler front-end)**](b2r2-org-b2r2.md) | Fully managed F# binary analysis framework whose x86/x86-64 front-end out-ran Capstone.NET about 4.4x in its authors' print-every-instruction harness. | **C** | F# | MIT | 🟢 active |
| 14 | [**addr2line (gimli-rs)**](gimli-rs-addr2line.md) | Rust DWARF symbolication library plus addr2line-style CLI; first-party chart shows it beating binutils, elfutils and llvm-addr2line. | **C** | Rust | Apache-2.0 OR MIT | 🟢 active |
| 15 | [**svc-hook (ARM64 system call hook by binary rewriting)**](retrage-svc-hook.md) | LD_PRELOAD library that rewrites every ARM64 svc into a branch to a trampoline, hooking system calls in-process instead of via ptrace. | **C** | C | Apache-2.0 | 🟢 active |
| 16 | [**Rasm**](edouardberge-rasm.md) | Single-file C Z80 cross-assembler (Amstrad CPC, ZX Spectrum) claiming tens of millions of instructions/s; SjasmPlus comparison unpublished. | **C** | C | MIT | 🟢 active |
| 17 | [**JWasm**](baron-von-riedesel-jwasm.md) | Portable MASM v6-compatible x86/x64 assembler in C; forum timings put it modestly ahead of ml.exe on assembly time. | **C** | C | Watcom-1.0 | 🟢 active |
| 18 | [**Asmc**](nidud-asmc.md) | Self-hosted MASM-syntax x86/x64 assembler descended from JWasm; forum timings put it about 1.5x faster than Microsoft's ML. | **C** | Assembly | GPL-2.0-or-later | 🟢 active |
| 19 | [**UASM**](terraspace-uasm.md) | Open-source MASM-syntax x86/x64 assembler descended from JWasm; forum timings put it modestly ahead of MASM, behind JWasm and AsmC. | **C** | C | Watcom-1.0 | 🟡 slow |
| 20 | [**zpoline (x86-64 system call hook by binary rewriting)**](yasukata-zpoline.md) | LD_PRELOAD library that rewrites every x86-64 syscall instruction into callq \*%rax, hooking system calls in-process instead of via ptrace. | **C** | C | Apache-2.0 | 🟡 stale |
| 21 | [**inspector-gadget**](garnts-inspector-gadget.md) | Multi-architecture ROP gadget finder in Rust; much faster than the Python tool Ropper on large binaries. | **C** | Rust | GPL-3.0 | 🟡 stale |
| 22 | [**Souper (LLVM IR superoptimizer)**](google-souper.md) | SMT-backed superoptimizer for LLVM IR that finds peephole rewrites stock LLVM misses; its published win is code size, not speed. | **C** | C++ | Apache-2.0 | 🔴 abandoned |
| 23 | [**c2goasm**](minio-c2goasm.md) | Converts clang-generated amd64 assembly into Go assembly so Go calls C SIMD kernels without cgo's per-call cost. | **C** | Go | Apache-2.0 | 🔴 abandoned |
| 24 | [**MaxAs**](nervanasystems-maxas.md) | Perl assembler for NVIDIA Maxwell SASS; its hand-scheduled SGEMM beat cuBLAS's Maxwell kernels by about 4-25%. | **C** | Perl | MIT | 🔴 abandoned |
| 25 | [**TuringAs (SASS assembler for Volta, Turing and Ampere)**](daadaada-turingas.md) | Python SASS assembler for NVIDIA SM70-SM86; its authors' hand-written Winograd kernels beat cuDNN 7.6.1 2.13-2.65x (paper only). | **C** | Python | MIT | 🔴 abandoned |
| 26 | [**K2 (smartnic/superopt, BPF superoptimizing compiler)**](smartnic-superopt.md) | K2: stochastic superoptimizer for eBPF bytecode that shrinks clang -O1/-O2/-O3 BPF output with SMT-checked equivalence. | **C** | C++ | MIT | 🔴 abandoned |
| 27 | [**z88dk (Z80 development kit: C compilers, z80asm assembler…**](z88dk-z88dk.md) | Z80/8080-family C toolchain (sccz80, zsdcc, z80asm) whose assembly C and maths libraries run 1.1-5.4x fewer cycles than stock SDCC 4.6.0. | **C** | C | Clarified Artistic License… (study only) | 🟢 active |
| 28 | [**SLOTHY**](slothy-optimizer-slothy.md) | Constraint-solver superoptimizer that reschedules, register-allocates and software-pipelines hand-written Arm and RISC-V assembly for one core. | **D** | Python | MIT | 🟢 active |
| 29 | [**Fadec**](aengelke-fadec.md) | Small freestanding C table-driven x86-32/x86-64 decoder plus x86-64 encoder; claims, unmeasured, to beat Capstone, Zydis and libopcodes. | **D** | C | BSD-3-Clause | 🟢 active |
| 30 | [**minias**](andrewchambers-minias.md) | Tiny hobby AT&T x86-64 to ELF assembler for C compiler output; README says often faster than GNU as, no numbers. | **D** | C | ISC | 🟢 active |
| 31 | [**lazypoline (hybrid SUD plus binary-rewriting syscall…**](lazypoline-lazypoline.md) | x86-64 Linux syscall interposer: traps each syscall site once via Syscall User Dispatch, then rewrites it zpoline-style; exhaustive, near-zpoline steady state. | **D** | C++ | MIT | 🟢 active |
| 32 | [**SuperCoder**](anjiang-wei-supercoder.md) | RL-fine-tuned 7B LLM that rewrites gcc-compiled x86-64 assembly, claiming 1.46x over gcc -O3 on CodeNet programs. | **D** | Python | Apache-2.0 | 🟢 active |
| 33 | [**ai-kernel-optimizer**](cleonard2341-ai-kernel-optimizer.md) | Python driver that prompts an AI for x86-64 asm and races it against GCC -O3; winning kernels unpublished. | **D** | Python | MIT (study only) | 🟢 active |
| 34 | [**aron**](not-nik-aron.md) | Incomplete Rust x86-64 Intel-syntax assembler emitting Mach-O; a startup-bound hello-world test ran 12.9x faster than macOS as. | **D** | Rust | MPL-2.0 (study only) | 🔴 abandoned |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
