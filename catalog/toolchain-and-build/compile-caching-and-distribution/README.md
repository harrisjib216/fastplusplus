# Compile caching and distribution

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md)</sub>

**What these beat:** ccache, sccache, distcc  
**4 entries:** 0 tier A · 0 tier B · 4 tier C · 0 tier D · 3 copyable, 1 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**FASTBuild**](fastbuild-fastbuild.md) | Full build system combining object caching, unity builds and distributed compilation; replaces make/MSBuild, not a wrapper. | **C** | C++ | Zlib | 🟢 active |
| 2 | [**octobuild**](octobuild-octobuild.md) | Rust compiler cache for Unreal Engine that impersonates IncrediBuild's xgConsole to speed up re-compiles vs. no cache. | **C** | Rust | MIT | 🟢 active |
| 3 | [**HOMCC**](celonis-homcc.md) | Distributed C/C++ compiler wrapper replacing distcc with server-side dependency caching and compression for thin uplinks. | **C** | Python | MIT | 🟢 active |
| 4 | [**NativeLink**](tracemachina-nativelink.md) | REAPI remote build-cache and execution server for Bazel/Buck2/CMake; beats local-only, non-distributed builds. | **C** | Rust | FSL-1.1-Apache-2.0 (study only) | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
