# Build systems

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md)</sub>

**What these beat:** CMake+Ninja, Make, Bazel, Cargo  
**7 entries:** 1 tier A · 1 tier B · 5 tier C · 0 tier D · 7 copyable, 0 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**Mill**](com-lihaoyi-mill.md) | JVM build tool for Java/Scala/Kotlin; 4-44x faster clean/incremental compiles than Maven, 3.6-10.2x than Gradle. | **A** | Scala | MIT | 🟢 active |
| 2 | [**Ninja**](ninja-build-ninja.md) | Minimal C++ build executor fed by generated build.ninja files; much faster no-op and incremental builds than CMake-generated Makefiles. | **B** | C++ | Apache-2.0 | 🟢 active |
| 3 | [**Bazel**](bazelbuild-bazel.md) | Google's client-server build system; beats default-rules GNU Make on large null and incremental builds, loses to Ninja. | **C** | Java | Apache-2.0 | 🟢 active |
| 4 | [**xmake**](xmake-io-xmake.md) | Lua-scripted cross-platform build tool with built-in package manager; beats CMake+Make, roughly matches plain Ninja. | **C** | C | Apache-2.0 | 🟢 active |
| 5 | [**Buck2**](facebook-buck2.md) | Meta's Rust rewrite of the Buck build system; up to 2x faster than Buck1 in Meta's internal monorepo usage. | **C** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 6 | [**ccache**](ccache-ccache.md) | Compiler cache that skips re-running GCC/Clang/MSVC on unchanged source, reusing prior object output. | **C** | C++ | GPL-3.0-or-later | 🟢 active |
| 7 | [**tup**](gittup-tup.md) | File-based build tool that beats Make's incremental-rebuild scanning via a persistent Linux-only file monitor and per-command sandboxing. | **C** | C | GPL-2.0 | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
