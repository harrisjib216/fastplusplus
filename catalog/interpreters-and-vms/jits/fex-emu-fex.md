# FEX (x86/x86-64 emulator for ARM64 with JIT)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Usermode x86 and x86-64 Linux emulator for ARM64 hosts with an IR-based JIT; about 1.6-2.4x QEMU user-mode in a 2022 test.

| | |
|---|---|
| **Beats** | QEMU user-mode (qemu-x86_64 and qemu-i386); Box64 is faster than FEX in the same tables |
| **Claimed result** | x86_64 guest, FEX against QEMU: 7z 1486 vs 931 (1.6x, derived from page data); dav1d 1 thread 27.28 vs 11.24 (2.4x, derived from page data). x86 guest: 7z 1197 vs 691 (1.7x, derived from page data); dav1d 1 thread 21.75 vs 10.57 (2.1x, derived from page data). Box64 in the same table: 7z 3084, dav1d 1 thread 49.72 (Box86: 3117 and 49.94). The article's summary puts FEX at 13-26% of native speed on 7-Zip and dav1d, against QEMU at 5-16% and Box64 at 27-53%. The record's other x86_64 figures (dav1d 4 threads 52.67 vs 15.65, glmark2 164 vs 4, OpenArena 1.8 vs 0.083) could not be confirmed here. |
| **Workload** | 7-Zip benchmark (MIPS), dav1d (1 and 4 threads), glmark2 and OpenArena run as x86 and x86_64 binaries under QEMU user-mode, FEX and Box64 on an ARM Linux machine, by the Box86/Box64 author in March 2022. |
| **Metric** | throughput |
| **Adoption** | 8.2k stars, 380 forks. In discussion #4113 the maintainer said in October 2024 that FEX does not support Android, and a July 2026 comment says the Chinese Android app Game Fusion uses FEX. An HN snippet says Valve funds Igalia work on FEX for its Snapdragon-based Steam Frame headset (snippet only). |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/FEX-Emu/FEX) · [benchmark](https://box86.org/2022/03/box86-box64-vs-qemu-vs-fex-vs-rosetta2/) |

## Verdict

In a March 2022 Box86/Box64-author test on an unnamed ARM Linux machine (CPU, flags and versions not visible; snippet only), FEX ran an x86-64 guest at 1486 7-Zip MIPS vs 931 for QEMU user-mode (about 1.6x) and dav1d single-threaded at 27.28 vs 11.24 fps (about 2.4x); on an x86 guest 1197 vs 691 and 21.75 vs 10.57 (about 1.7x and 2.1x), while Box64/Box86 were roughly twice as fast as FEX on the same rows.

## Use it when

- Running closed-source x86 or x86-64 Linux binaries (games via Steam/Proton, drivers, tools) on ARM64 Linux, where QEMU user-mode is too slow.
- Mixed 32-bit and 64-bit x86 guests on one ARM64 host with one emulator, with multithreaded guests that need x86 memory-ordering semantics preserved by default.
- GPU-heavy workloads where forwarding OpenGL/Vulkan to host drivers matters more than the CPU JIT (the 2022 glmark2/OpenArena gap against QEMU came mostly from this).
- Hardware with good x86-emulation support: ARMv8.3+ cores with LRCPC, Apple Silicon with its TSO bit, Snapdragon X2 Elite/Oryon-3, or Valve's Steam Frame with its unaligned-atomic kernel patch.

## Skip it when

- Raw CPU speed is the only criterion: in the only head-to-head with numbers, Box64 beat FEX on every row (7z 3084 vs 1486, dav1d 49.72 vs 27.28 fps on an x86-64 guest, March 2022), and a January 2026 user report (#5221, Cortex-A53, multithreaded SpliX printer filter) measured FEX at 2.260 s against box64 0.908 s and native 0.381 s.
- Hosts other than 64-bit ARM Linux or Windows/Wine arm64ec: no RISC-V, LoongArch, 32-bit ARM, macOS or supported Android build (the maintainer said in October 2024 that FEX does not support Android); x86-64 hosts are CI-only.
- Exact x86 atomicity: split-lock (cacheline-crossing) atomics are emulated on a best-effort basis that can tear data, and each one costs an alignment fault plus a kernel and userspace signal round trip unless the kernel carries Valve's patch.
- Systems with a dedicated PCIe GPU: storing to write-combine (uncached) memory under TSO emulation hits a cliff (the project reports up to 816x worse store bandwidth and games below 1 FPS) unless TSO emulation is disabled for that app.
- Full-system or kernel emulation: FEX is userspace-only by design (no CPL0-2, real or protected mode, IRQs).

## How it is fast

A dynamic binary translator: an x86 frontend decodes blocks (with multiblock fragments), lowers them to an SSA IR loosely modelled on arm64, runs IR passes such as redundant flag-calculation elimination and register allocation, and emits arm64 code through a 'splatter' backend; translated blocks are looked up in a block cache, and an optional on-disk code cache (FEX_DISKCACHE=1, FOZ database) cuts JIT stutter. API forwarding (thunking) skips emulating whole graphics and system libraries. It maps x86-TSO onto ARM using LRCPC/LRCPC2/LRCPC3 loads, Apple's hardware TSO bit on Asahi, and per-app options to skip memory-model emulation where an app tolerates it.

## Compared with alternatives

Pick FEX over Box64 when you want one emulator for 32-bit and 64-bit x86 guests with x86 memory-ordering emulated by default, Valve-backed Steam/Proton integration and per-app tuning on ARM64; pick Box64 for higher measured CPU throughput or for RISC-V and LoongArch hosts, and Blink when the host is not ARM64.

## Integration

| | |
|---|---|
| **Form** | application (FEX loader and FEXInterpreter via binfmt_misc, FEXConfig GUI, PPA and distro packages) built on the FEXCore library; Wine arm64ec/WoW64 module on Windows targets |
| **Dependencies** | x86-64 RootFS (downloadable with FEXRootFSFetcher); build needs CMake 3.14+ and Clang 13+ (GCC and MSVC are rejected); vendored forks of vixl, jemalloc, robin-map and xxHash; thunk libraries are optional (BUILD_THUNKS off by default in a source build) |
| **Minimum toolchain** | C++20, Clang 13+ (MinGW Clang for Windows targets), CMake 3.14 |
| **Platforms** | ARM64 Linux, ARMv8.0-a or newer with FEAT_FP and FEAT_CRC32 (FEXCore targets ARMv8.1+); tested on Arch, Fedora, openSUSE and Ubuntu 22.04-25.04; a Fedora wiki snippet (page blocked) says only 4K page-size kernels are supported; Windows arm64ec via MinGW |
| **Thread safety** | Runs multithreaded guests and emulates the x86-TSO memory model by default; the JIT compiles from several threads at once, with lock contention reduced in FEX-2609. Per-app options that skip memory-model emulation trade correctness for speed. |
| **Drop-in for the baseline** | partial: replaces qemu-x86_64/qemu-i386 user mode through binfmt_misc on ARM64 Linux, but only on ARM64 hosts and it needs its own RootFS setup |

## Gotchas

- The QEMU comparison is a March 2022 blog by the Box86/Box64 author, read here only from search snippets (box86.org blocked): CPU, compiler flags and the QEMU and FEX versions are not visible, the glmark2 and OpenArena rows measure FEX's GL forwarding against QEMU's software rendering rather than the JIT, and FEX has changed monthly since (now FEX-2609).
- FEX itself publishes no numbers against QEMU or Box64; the maintainer said in October 2024 he had never compared FEX with Box (discussion #4113), and #4626 (June 2025, 'How is the performance compared to Box64?') got no answer with numbers.
- Speed depends heavily on the host CPU's memory-ordering features. On ARMv8.0 every x86 load becomes load-acquire and every store becomes store-release, which the project calls 'exceedingly costly'; LRCPC extensions or Apple's TSO bit recover most of that cost.
- The FEX-2609 disk cache is experimental: it can grow without bound for guests that JIT their own code, has no eviction, and may not be invalidated when files change; delete \$HOME/.cache/fex-emu/ to reclaim space.

## Known shortcomings

- Only evidence is the Box64 author's March 2022 blog (competitor-run, read as snippets since box86.org is blocked): 7z 1486 vs QEMU 931 and dav1d 1-thread 27.28 vs 11.24 (x86-64), 1197 vs 691 and 21.75 vs 10.57 (x86); dav1d 4-thread, glmark2 and OpenArena figures unconfirmed, and the GL rows measure QEMU software rendering rather than the JIT. Slower than Box64 on every row. No CPU, flags or versions.
- Enricher: independent data point issue #5221 (January 2026, Cortex-A53, SpliX filter): FEX 2.260 s vs box64 0.908 s vs native 0.381 s. FEX's own 2026-09-17 TSO article: on ARMv8.0 every load and store becomes acquire/release ('exceedingly costly'), split-lock emulation is best effort and can tear data, store bandwidth on PCIe GPU write-combine memory is up to 816x worse, and the FEX-2609 disk cache has no eviction. The 4K-page-only claim is from a Fedora wiki snippet; issue #4626 asking for a Box64 comparison got no numbers.

## Caveats and trade-offs

Snippet only: box86.org is blocked here, so the numbers were read from search-result text. Search snippets confirm the 7z and dav1d 1-thread rows for both guests; the dav1d 4-thread, glmark2 and OpenArena x86_64 figures could not be checked. The CPU model, compiler flags and the QEMU and FEX versions are not visible. The measurement is from March 2022 and was made by the Box86/Box64 author, a competing project; FEX has changed a lot since, and its maintainer said in October 2024 (discussion #4113) that he has never compared FEX with Box and that its CPU emulation performance has improved over the years. The glmark2 and OpenArena gaps mostly measure GL forwarding, not the JIT: the article says QEMU has no GL pass-through by default and renders in software. An HN snippet says FEX was slower than QEMU on some workloads and had glitches (snippet only, no numbers). FEX publishes no numbers of its own against QEMU in its README. In these tables FEX is slower than Box64 on every row.

ARM64 Linux host only; x86 and x86-64 guests via a binary recompiler with a custom IR; forwards API calls to host libraries (thunking); per-app configuration and an experimental code cache; GUI configuration tool. Not supported on Android.

## Maintenance

Very active and MIT-licensed, with monthly releases (latest FEX-2609, September 2026), backing from Valve since its start and a Valve kernel patch for it on the Steam Frame; mature enough for gaming on ARM64 Linux, though its speed edge over QEMU rests on old, competitor-run numbers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The only numbers against QEMU are a March 2022 blog post by the Box86/Box64 author (a competing project), read here from search snippets because box86.org is blocked; the CPU model, compiler flags and emulator versions are not visible, and it is not a well-known independent suite, so it falls short of A and B. FEX itself publishes no numbers against QEMU.
- **Verifier notes:** Kept at C: real comparison against QEMU user-mode, but from a competitor's 2022 blog with unknown hardware and versions; box86.org (benchmark_url) and brianlovin.com (HN mirror) were EGRESS_BLOCKED, so only snippets were seen. Shortcomings to record: competitor-run and 4 years old, methodology unknown, slower than Box64 on every row, GL rows measure GL forwarding against QEMU's software rendering, dav1d 4-thread/glmark2/OpenArena figures unconfirmed. Metadata confirmed: MIT, 8.2k stars, last commit 2026-10-05, active.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** first-party or independent measurement with hardware stated; first-party numbers vs QEMU and Box64 with hardware stated
- **Pages the verifier opened:**
  - <https://github.com/FEX-Emu/FEX>
  - <https://github.com/FEX-Emu/FEX/commits>
  - <https://github.com/FEX-Emu/FEX/discussions/4113>
  - <https://raw.githubusercontent.com/FEX-Emu/FEX/HEAD/Readme.md>
  - <https://github.com/ptitSeb/box64/issues/107>
- **Sources the enricher read:**
  - <https://github.com/FEX-Emu/FEX>
  - <https://raw.githubusercontent.com/FEX-Emu/FEX/HEAD/Readme.md>
  - <https://raw.githubusercontent.com/FEX-Emu/FEX/HEAD/docs/SourceOutline.md>
  - <https://raw.githubusercontent.com/FEX-Emu/FEX/HEAD/FEXCore/Readme.md>
  - <https://raw.githubusercontent.com/FEX-Emu/FEX/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/FEX-Emu/FEX/HEAD/LICENSE>
  - <https://github.com/FEX-Emu/FEX/discussions/4113>
  - <https://github.com/FEX-Emu/FEX/issues?q=is%3Aissue+is%3Aopen+slow+OR+performance>
  - <https://github.com/FEX-Emu/FEX/issues/4626>
  - <https://github.com/FEX-Emu/FEX/issues/5221>
  - <https://github.com/orgs/FEX-Emu/repositories>
  - <https://github.com/FEX-Emu/fex-emu.com/tree/main/_posts>
  - <https://raw.githubusercontent.com/FEX-Emu/fex-emu.com/HEAD/_posts/2026-09-17-Scourge-of-emulation.md>
  - <https://raw.githubusercontent.com/FEX-Emu/fex-emu.com/HEAD/_posts/2026-09-07-FEX-2609.md>
  - <https://raw.githubusercontent.com/FEX-Emu/fex-emu.com/HEAD/_posts/2025-11-28-FEXiversary.md>
  - https://box86.org/2022/03/box86-box64-vs-qemu-vs-fex-vs-rosetta2/ (EGRESS_BLOCKED; search snippets only)
  - https://fedoraproject.org/wiki/Changes/FEX (EGRESS_BLOCKED; search snippet only)
  - https://printserver.ink/blog/box64-vs-fex/ (EGRESS_BLOCKED; search snippet only, no numbers)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/fex-emu/fex`) · [data/wave12/enrich/raw/github_com_fex_emu_fex.json](../../../data/wave12/enrich/raw/github_com_fex_emu_fex.json) (enrichment confidence 0.7)

</details>
