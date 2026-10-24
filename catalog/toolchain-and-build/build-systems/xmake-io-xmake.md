# xmake

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Build systems](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0` · 🟢 active

> Lua-scripted cross-platform build tool with built-in package manager; beats CMake+Make, roughly matches plain Ninja.

| | |
|---|---|
| **Beats** | Make (via CMake-generated Makefiles) |
| **Claimed result** | Parallel (-j12): Termux 24.890s (xmake) vs 33.889s total (cmake gen+make) = \~1.36x; macOS 12.264s vs 15.233s total = \~1.24x (derived from page data). Single-task (-j1): Termux 117.707s vs 135.955s total = \~1.15x; macOS 39.937s vs 42.940s total = \~1.08x (derived from page data). xmake is roughly on par with, and sometimes slightly slower than, plain ninja/cmake+ninja in the same table. |
| **Workload** | Building xmake's own xmake-core C project on Termux (8-core, -j12) and macOS (8-core, -j12), plus single-threaded (-j1) builds; xmake vs ninja vs cmake(gen+make) vs cmake(gen+ninja). |
| **Metric** | build-time |
| **Hardware** | Termux 8-core (-j12); macOS 8-core (-j12); exact CPU model not stated |
| **Adoption** | 12.2k stars |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/xmake-io/xmake) · [benchmark](https://github.com/xmake-io/xmake/blob/master/README.md) |

## Verdict

First-party README benchmark building xmake's own in-repo xmake-core (C) target: on Termux (8-core, -j12) xmake finished in 24.890s vs cmake(gen+make)'s 5.416s+28.473s=33.889s total (\~1.36x), but plain ninja ran in 25.682s, barely behind xmake; on macOS (8-core, -j12) xmake was 12.264s vs cmake(gen+make)'s 1.203s+14.030s=15.233s total (\~1.24x), while plain ninja was faster than xmake at 11.327s. Single-threaded (-j1) gaps vs cmake+make were smaller (\~1.08-1.15x). Exact CPU model and compiler/flags are not stated.

## Use it when

- Migrating off raw CMake+Make (not CMake+Ninja) where a single tool that configures and builds without a separate generate step is the goal
- Want a built-in cross-platform package manager instead of wiring vcpkg/conan into CMake by hand
- Targeting niche platforms/toolchains in one config file (WDK drivers, CUDA, Zig, Rust, embedded compilers like Keil/IAR/TI, arbitrary cross toolchains) that CMake supports poorly
- New small-to-medium C/C++ project where xmake.lua's terser syntax is a feature rather than a migration cost
- Want distributed/remote build or a build cache without separately standing up distcc/ccache/sccache

## Skip it when

- Project already builds via CMake+Ninja or Meson: per this same README, xmake is on par with or slightly slower than plain Ninja, so there is no measured win there
- Team depends on CMake's mature IDE/CI/third-party tooling ecosystem; xmake's own IDE plugins (VSCode/Sublime/IDEA/Zed) are official but far smaller in adoption
- Large existing CMake codebase: there is no automatic CMakeLists.txt -&gt; xmake.lua converter in this repo, so migration means hand-porting build logic
- Treating the claimed multiplier as portable: this is a first-party, tier-C benchmark with no CPU model, OS version, or compiler/flags disclosed
- Need airtight incremental-build correctness across all language backends: open issues report gaps for at least one backend (see gotchas)

## How it is fast

xmake's core engine (xmake-core, written in C, bundled with a modified Lua/tbox runtime) parses xmake.lua and runs the resulting dependency DAG directly in one process and one invocation, the same way Ninja does, instead of the two-stage 'generate Makefiles, then run recursive make' path CMake+Make requires. The measured speedup is specifically against that generate+make baseline (\~1.24-1.36x at -j12, \~1.08-1.15x at -j1); xmake does not claim to beat Ninja's own scheduler and is measurably not doing so here. It also ships an optional content-based local/remote build cache (not exercised in this particular benchmark).

## Compared with alternatives

None of the catalogued siblings are direct substitutes: ccache caches compiler invocations and composes with any build system including xmake; Mill/Buck2 target JVM/Meta monorepo ecosystems, not general C/C++; tup targets the specific pathology of huge (100k-file) trees with slow no-op/rebuild checks under Make. Pick xmake over CMake+Make when you also want a bundled package manager and one-file multi-language config, but pick tup instead if your real bottleneck is Make's no-op/rebuild-check cost at large scale, since xmake's own numbers show it merely tying Ninja rather than tup's claimed order-of-magnitude jump.

## Integration

| | |
|---|---|
| **Form** | CLI binary (not a library) — precompiled install via curl/wget/PowerShell script or OS package managers |
| **Dependencies** | none to install (self-contained binary); requires whatever C/C++/other-language toolchain the project itself needs (GCC/Clang/MSVC/etc.), which xmake detects rather than provides |
| **Minimum toolchain** | not documented as a minimum — no dependencies outside the standard library per README; current release v3.1.1 (2026-08-27); source-build requirements (compiler for xmake-core, Lua) not stated in README |
| **Platforms** | Windows, macOS, Linux, FreeBSD/NetBSD/OpenBSD/DragonflyBSD, Solaris, Android, iOS, watchOS, tvOS, visionOS, MSYS/MinGW/Cygwin, Wasm, Haiku, HarmonyOS, and arbitrary cross-toolchains, each with multiple listed architectures |
| **Thread safety** | not documented — it is a build orchestrator, not a library; parallel job scheduling (-j) is internal to the tool |
| **Drop-in for the baseline** | false — projects are described in the xmake.lua DSL, not consumed directly from an existing CMakeLists.txt/Makefile; xmake can generate CMake/Ninja/VS project files as output but there is no documented importer for existing CMake projects |

## Gotchas

- The repo's default branch is 'dev', not 'master'; benchmark_url points at master but the same numbers appear on dev's README
- README's headline claim is 'on par with Ninja' — in this exact benchmark table xmake (12.264s parallel / 39.937s single, macOS) is slower than plain ninja (11.327s / 38.995s), so 'faster' here means faster than CMake+Make, not faster than Ninja
- Benchmark hardware is described only as '8core' with no CPU model, OS version, or compiler/flags disclosed
- Open issues report incremental-build gaps for at least one language backend ('rust project not being rebuilt when modified', #4790) and occasional flaky build failures fixed only by restarting (#4796); verify incremental correctness for your specific toolchain before relying on it

## Caveats and trade-offs

First-party README benchmark; CPU model, OS version, and underlying C compiler/flags are unstated, so capped at tier C. On macOS, xmake (12.264s) is slightly slower than plain ninja (11.327s), so the 'faster' claim only clearly holds against the Make backend, not Ninja.

Uses its own xmake.lua DSL rather than CMakeLists.txt; smaller ecosystem/IDE integration than CMake; the table's real win is vs cmake+make, not vs Ninja itself, which it roughly matches or trails.

## Maintenance

Actively maintained: last commit 2026-09-22, latest release v3.1.1 (2026-08-27), 259 open issues, 12.2k stars, no open security advisories found; Apache-2.0 licensed and distributed as a self-contained precompiled binary, so it's cheap to adopt or vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification C, tier now C.
- **Tier reason:** The README's Benchmark section gives first-party timings for building the in-repo xmake-core (core/) with xmake, ninja, cmake+make and cmake+ninja. It gives only '8core' for hardware, with no CPU model, compiler or flags, and no benchmark script. That is tier C.
- **Verifier notes:** Every raw time matches the README, and the derived ratios check out (1.36x, 1.24x, 1.155x, 1.075x). The cmake+make totals include the generate step; make alone vs xmake is about 1.14x on both -j12 runs (derived from page data). License (Apache-2.0), 12,231 stars and last commit 2026-09-22 on the default branch 'dev' are confirmed.
- **Pages the verifier opened:**
  - <https://github.com/xmake-io/xmake/blob/master/README.md>
  - <https://github.com/xmake-io/xmake>
  - <https://github.com/xmake-io/xmake/blob/dev/README.md>
- **Sources the enricher read:**
  - <https://github.com/xmake-io/xmake>
  - <https://github.com/xmake-io/xmake/blob/dev/README.md>
  - <https://github.com/xmake-io/xmake/tree/master/core>
  - <https://github.com/xmake-io/xmake/releases/latest>
  - <https://github.com/xmake-io/xmake/blob/dev/LICENSE.md>
  - <https://github.com/xmake-io/xmake/issues>
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/xmake-io/xmake`) · [data/wave2/enrich/raw/github_com_xmake_io_xmake.json](../../../data/wave2/enrich/raw/github_com_xmake_io_xmake.json) (enrichment confidence 0.75)

</details>
