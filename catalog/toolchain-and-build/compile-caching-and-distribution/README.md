# Compile caching and distribution

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md)</sub>

**What these beat:** ccache, sccache, distcc  
**8 entries:** 1 tier A · 0 tier B · 7 tier C · 0 tier D · 7 copyable, 1 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**doctest**](doctest-doctest.md) | Single-header C++11 unit-testing framework whose header and asserts compile far faster than Catch2 v2's single header. | **A** | C++ | MIT | 🟢 active |
| 2 | [**distcc**](distcc-distcc.md) | Compiler front end that farms C/C++ compile jobs out to networked servers; beats a local single-machine make on big parallel builds. | **C** | C | GPL-2.0-or-later | 🟢 active |
| 3 | [**[Boost].UT (boost-ext/ut)**](boost-ext-ut.md) | Macro-free C++20 single-header/module unit-testing framework whose 2019 benchmark compiled faster than Boost.Test, GoogleTest and Catch2. | **C** | C++ | BSL-1.0 | 🟢 active |
| 4 | [**FASTBuild**](fastbuild-fastbuild.md) | Full build system combining object caching, unity builds and distributed compilation; replaces make/MSBuild, not a wrapper. | **C** | C++ | Zlib | 🟢 active |
| 5 | [**octobuild**](octobuild-octobuild.md) | Rust compiler cache for Unreal Engine that impersonates IncrediBuild's xgConsole to speed up re-compiles vs. no cache. | **C** | Rust | MIT | 🟢 active |
| 6 | [**HOMCC**](celonis-homcc.md) | Distributed C/C++ compiler wrapper replacing distcc with server-side dependency caching and compression for thin uplinks. | **C** | Python | MIT | 🟢 active |
| 7 | [**clcache**](frerich-clcache.md) | Python ccache-style object cache for MSVC cl.exe that skips recompiling unchanged translation units on repeat builds. | **C** | Python | BSD-3-Clause | 🔴 abandoned |
| 8 | [**NativeLink**](tracemachina-nativelink.md) | REAPI remote build-cache and execution server for Bazel/Buck2/CMake; beats local-only, non-distributed builds. | **C** | Rust | FSL-1.1-Apache-2.0 (study only) | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
