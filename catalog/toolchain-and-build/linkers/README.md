# Linkers

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md)</sub>

**What these beat:** GNU ld, gold, lld, MSVC link.exe  
**4 entries:** 2 tier A · 1 tier B · 1 tier C · 0 tier D · 4 copyable, 0 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**mold**](rui314-mold.md) | Drop-in ELF linker beating LLVM lld and GNU ld via pervasive data-parallelism across the whole link pipeline. | **A** | Rust | MIT | 🟢 active |
| 2 | [**Wild (wild-linker)**](wild-linker-wild.md) | Rust linker for Linux that beats LLVM lld on debug-build link time via mmap'd input and rayon-parallelized phases. | **A** | Rust | Apache-2.0 OR MIT | 🟢 active |
| 3 | [**LLVM lld (LLVM linker)**](paper-llvm-lld-linker.md) | LLVM's drop-in linker (ELF, COFF, Mach-O, Wasm): roughly 2x to 12x faster than GNU ld and gold, though mold and wild now beat it. | **B** | C++ | Apache-2.0 WITH… | 🟢 active |
| 4 | [**zld**](michaeleisel-zld.md) | Drop-in fork of Apple's ld64 that speeds up incremental Xcode debug linking; archived, maintainer now recommends lld instead. | **C** | C++ | MIT | 🔴 abandoned |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
