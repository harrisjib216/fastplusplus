# Toolchain and build

<sub>[fastpp](../../README.md) › [Catalog](../README.md)</sub>

Compilers, linkers, build systems and compile caches that turn source into binaries faster than GCC, Clang, GNU ld, Make or ccache.

**33 entries in 6 categories:** 8 tier A · 4 tier B · 20 tier C · 1 tier D

| Category | Entries | A | B | C | D | What they beat |
|---|--:|--:|--:|--:|--:|---|
| [Build systems](build-systems/README.md) | 6 | 1 | 1 | 4 | 0 | CMake+Ninja, Make, Bazel, Cargo |
| [Compile caching and distribution](compile-caching-and-distribution/README.md) | 5 | 1 | 0 | 4 | 0 | ccache, sccache, distcc |
| [Compilers and front ends](compilers-frontends/README.md) | 7 | 1 | 1 | 4 | 1 | GCC, Clang, MSVC, rustc |
| [Formatters, linters and language servers](formatters-linters-lsps/README.md) | 6 | 3 | 0 | 3 | 0 | clang-format, clang-tidy, clangd, rust-analyzer |
| [Linkers](linkers/README.md) | 4 | 2 | 1 | 1 | 0 | GNU ld, gold, lld, MSVC link.exe |
| [Preprocessors and code generators](preprocessors-and-codegen/README.md) | 5 | 0 | 1 | 4 | 0 | cpp, protoc, m4 |

## Most-adopted tier A picks

Tier A, copyable and actively maintained, ordered by GitHub stars.

| # | Project | What it is | Category | Tier | Language | License | Status |
|--:|---|---|---|:-:|---|---|---|
| 1 | [**Oxlint (oxc-project/oxc)**](formatters-linters-lsps/oxc-project-oxc.md) | Rust-based JavaScript/TypeScript linter and toolchain that replaces ESLint with 50-100x faster linting. | [Formatters, linters and language servers](formatters-linters-lsps/README.md) | **A** | Rust | MIT | 🟢 active |
| 2 | [**ty**](formatters-linters-lsps/astral-sh-ty.md) | Rust-based Python type checker and language server from Astral; 10-100x faster cold checks than mypy and Pyright. | [Formatters, linters and language servers](formatters-linters-lsps/README.md) | **A** | Rust | MIT | 🟢 active |
| 3 | [**mold**](linkers/rui314-mold.md) | Drop-in ELF linker beating LLVM lld and GNU ld via pervasive data-parallelism across the whole link pipeline. | [Linkers](linkers/README.md) | **A** | Rust | MIT | 🟢 active |
| 4 | [**Pyrefly**](formatters-linters-lsps/facebook-pyrefly.md) | Rust type checker and LSP for Python; faster than mypy and Pyright on cold, whole-project checks. | [Formatters, linters and language servers](formatters-linters-lsps/README.md) | **A** | Rust | MIT | 🟢 active |
| 5 | [**doctest**](compile-caching-and-distribution/doctest-doctest.md) | Single-header C++11 unit-testing framework whose header and asserts compile far faster than Catch2 v2's single header. | [Compile caching and distribution](compile-caching-and-distribution/README.md) | **A** | C++ | MIT | 🟢 active |
| 6 | [**Wild (wild-linker)**](linkers/wild-linker-wild.md) | Rust linker for Linux that beats LLVM lld on debug-build link time via mmap'd input and rayon-parallelized phases. | [Linkers](linkers/README.md) | **A** | Rust | Apache-2.0 OR MIT | 🟢 active |
| 7 | [**TinyCC (tcc)**](compilers-frontends/tinycc-tinycc.md) | Tiny self-hosting C compiler/JIT that compiles about 9x faster than gcc -O0, trading away optimization. | [Compilers and front ends](compilers-frontends/README.md) | **A** | C | LGPL-2.1 | 🟢 active |
| 8 | [**Mill**](build-systems/com-lihaoyi-mill.md) | JVM build tool for Java/Scala/Kotlin; 4-44x faster clean/incremental compiles than Maven, 3.6-10.2x than Gradle. | [Build systems](build-systems/README.md) | **A** | Scala | MIT | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
