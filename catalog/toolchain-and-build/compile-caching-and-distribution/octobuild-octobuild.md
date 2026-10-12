# octobuild

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Compile caching and distribution](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust compiler cache for Unreal Engine that impersonates IncrediBuild's xgConsole to speed up re-compiles vs. no cache.

| | |
|---|---|
| **Beats** | stock Unreal Build Tool / Unreal Automation Tool build without octobuild (README 'Without octobuild' column) |
| **Claimed result** | README states octobuild reduces re-compile time 'by 60-90%'. Benchmark table at 100% cache hit vs. without octobuild: Linux 3m54s to 36s (\~6.5x), Win64 8m4s to 2m15s (\~3.6x), PS4 6m12s to 2m34s (\~2.4x), PS5 5m48s to 2m11s (\~2.7x), XB1 4m40s to 1m39s (\~2.8x), XSX 4m49s to 1m40s (\~2.9x) (derived from page data). With a cold (0%) cache octobuild is equal or slower: Linux 3m53s, Win64 10m6s, PS4 7m10s, PS5 6m56s, XB1 6m10s, XSX 5m42s. |
| **Workload** | Build of an unnamed Unreal Engine 5.0.3 game project (&lt;game&gt;Editor DebugGame for Linux and Win64, &lt;game&gt; DebugGame for PS4, PS5, Xbox One and Xbox Series X), comparing no octobuild vs. octobuild with a cold (0%) and a fully warm (100%) cache. |
| **Metric** | build-time |
| **Hardware** | Linux: AMD Ryzen 7 3700X, 32GB DDR4@3200MHz, SSD. Windows/console: Intel Core i7-9700F, 32GB DDR4@2400MHz, SSD. |
| **Compiler and flags** | Win64: MSVC 2019 (stated); Linux and console toolchains not named; UE 5.0.3 DebugGame configuration via RunUAT.sh (Linux) and RunUBT.bat (Win64, consoles); compiler flags not stated |
| **Adoption** | 285 stars |
| **Last commit** | 2026-09-15 |
| **Links** | [repository](https://github.com/octobuild/octobuild) · [benchmark](https://github.com/octobuild/octobuild#benchmark) |

## Verdict

The README's first-party benchmark table (unnamed UE 5.0.3 game project, DebugGame configuration, no stated compiler flags) shows a fully warm (100%) cache beating a build without octobuild by about 2.4x-6.5x across platforms — e.g. Linux 3m54s to 36s, Win64 8m4s to 2m15s (MSVC 2019) — on an AMD Ryzen 7 3700X/32GB (Linux) or Intel Core i7-9700F/32GB (Windows/console) with SSD storage; a cold (0%) cache showed no speedup and was up to \~25% slower on Win64 (8m4s to 10m6s).

## Use it when

- Unreal Engine or UE-based game project doing iterative DebugGame rebuilds after small source edits, with a cache that can stay warm between builds
- Team already using, or willing to enable, IncrediBuild-style XGE executor integration in UBT/UAT
- Windows target with MSVC 2019/2022 (the benchmarked and best-documented path)
- Linux or macOS target where you can apply the listed UE engine patches (some already merged in UE &gt;= 5.2 / &gt;= 5.3)
- Dev or CI machines with spare local SSD space for a large (default 64GB) persistent cache

## Skip it when

- Cold-cache or from-scratch CI builds: the README's own table shows octobuild is equal to or up to \~25% slower than no octobuild at 0% cache hit rate (Win64 8m4s -&gt; 10m6s)
- You need a validated comparison against ccache, sccache, distcc, or IncrediBuild itself — none appears in the README; the only baseline is 'without octobuild'
- Non-Unreal C/C++ projects: it's UE-specific (vs/clang compiler pre/postprocessing, XGE action-graph parser), not a general-purpose compiler cache
- You can't spare disk for a multi-GB persistent cache, or your build environment is ephemeral so the cache never warms up
- You need compiler flags and an exact reproducible harness for the benchmark numbers — the README doesn't state flags and uses an unnamed game project

## How it is fast

It is a content-addressed disk cache of individual compile actions, similar in spirit to ccache/sccache, avoiding re-invocation of cl.exe/clang for translation units it has already built. The repo also ships octo_agent/octo_builder/octo_coordinator and a src/cluster module, suggesting optional distributed-build support beyond local caching, but this is undocumented in the README and not covered by the benchmark. Per the README's own numbers the entire measured speedup is cache-hit driven: at 0% cache hit rate it is roughly neutral to slower than no octobuild at all, presumably from added hashing/IPC overhead.

## Compared with alternatives

Pick octobuild specifically because the project is Unreal Engine or UE-based — its xgConsole/ib_console impersonation and MSVC/clang postprocessing are UE-specific integration points that NativeLink, FASTBuild, and HOMCC don't provide. Those siblings target generic CMake/Ninja or distcc-based C/C++ builds and would need a custom UE integration to be used at all, whereas octobuild works with UBT/UAT's existing XGE executor path out of the box.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Rust crates (bincode, crossbeam-channel, petgraph, reqwest, serde, sha2, xml-rs, figment, thiserror, uuid, etc.) plus the octobuild/daemon-rs and octobuild/ipc-rs git dependencies; winapi/winreg on Windows. Also distributed as prebuilt packages via Chocolatey, WinGet, Homebrew, and apt/deb. |
| **Minimum toolchain** | Rust stable (edition 2021 crate, CI builds against dtolnay/rust-toolchain@stable with no pinned MSRV); Windows build additionally needs Visual Studio 2019 or 2022 with the C++ desktop workload |
| **Platforms** | Win64 (MSVC 2019/2022), Linux, macOS, plus PS4/PS5/Xbox One/Xbox Series X and Android/iOS listed as supported; console/mobile targets build through UE's own toolchains |
| **Thread safety** | not documented explicitly; uses a worker pool (src/worker.rs) with concurrency capped by the OCTOBUILD_PROCESS_LIMIT setting (default: core count) |
| **Drop-in for the baseline** | partial — on Windows it plugs into UBT/UAT's existing XGE executor hook with no engine source changes; on Linux/macOS it additionally requires the UE engine patches listed in the README (some already merged into UE &gt;= 5.2 / 5.3) |

## Gotchas

- Cold cache makes the build slower than not using octobuild at all (README: Win64 8m4s without octobuild vs. 10m6s at 0% cache hit)
- Default disk cache is 64GB; tune via OCTOBUILD_CACHE_LIMIT_MB, and OCTOBUILD_CACHE_MODE can set it to read-only or fully disabled
- On Windows, long command lines can hit 'ERROR: The filename or extension is too long (os error 206)' — fix is OCTOBUILD_USE_RESPONSE_FILES=true, which is already the Windows default
- Source tree contains cluster/agent/coordinator/builder binaries implying distributed (multi-machine) build support, but this is undocumented in the README and unmeasured in the benchmark

## Caveats and trade-offs

No comparison with other caches or accelerators (ccache, sccache, distcc, IncrediBuild) appears in the README; the only baseline is a build without octobuild. The numbers are first-party, from an unnamed game project, with no published harness and no compiler flags; builds are DebugGame. On a cold cache octobuild is up to about 25% slower (Win64 10m6s vs 8m4s).

UE-specific: requires patches to Unreal Engine on Linux/macOS to enable octobuild; cache is disk-based with a configurable size limit (default 64GB); at 0% cache hit rate it adds measurable overhead over an uncached build (e.g. Win64 went from 8m4s to 10m6s cold) so benefit depends entirely on cache warmth.

## Maintenance

Actively maintained (last commit 2026-09-15, 285 stars, packaged for Chocolatey/WinGet/Homebrew/apt) and MIT-licensed, but it's a set of UE-specific CLI binaries rather than a general library, so 'copyable' means vendoring the tool, not embedding source into another project.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification C, tier now C.
- **Tier reason:** The README #benchmark table is first-party and compares 'Without octobuild' against octobuild at 0% and 100% cache. CPUs are named and MSVC 2019 is named for Win64, but flags are not stated and the game project is unnamed, so it is not reproducible. The builds are DebugGame configurations.
- **Verifier notes:** All table values match the README exactly. The record's claims that consoles use 'platform-bundled clang' and that ccache/distcc cannot support MSVC do not appear on the page, so they were removed. Metadata (MIT, 285 stars, last commit 2026-09-15) is correct.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/octobuild/octobuild#benchmark>
  - <https://github.com/octobuild/octobuild>
- **Sources the enricher read:**
  - <https://github.com/octobuild/octobuild>
  - <https://github.com/octobuild/octobuild#benchmark>
  - <https://github.com/octobuild/octobuild/blob/main/Cargo.toml>
  - <https://github.com/octobuild/octobuild/blob/main/src/lib.rs>
  - <https://github.com/octobuild/octobuild/blob/main/.github/workflows/ci.yml>
  - <https://github.com/octobuild/octobuild/issues/137>
  - <https://github.com/octobuild/octobuild/issues/134>
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/octobuild/octobuild`) · [data/wave2/enrich/raw/github_com_octobuild_octobuild.json](../../../data/wave2/enrich/raw/github_com_octobuild_octobuild.json) (enrichment confidence 0.6)

</details>
