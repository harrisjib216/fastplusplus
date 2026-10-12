# Box64 DynaRec

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> User-mode x86-64 Linux emulator for Arm64, RISC-V and LoongArch hosts whose dynamic recompiler beats its own interpreter 5-10x.

| | |
|---|---|
| **Beats** | Box64 interpreter mode (no DynaRec) |
| **Claimed result** | README: 'With DynaRec for Arm, RISC-V and LoongArch platforms, Box64 achieves a speed boost 5-10x faster than the interpreter alone.' EuroSys 2026 paper 'Practical and Efficient x86-64 Emulation on RISC-V' (Tan, Liu, Chevalier, Chen, Liu, Fu; https://doi.org/10.1145/3767295.3803574), abstract (snippet only): average performance penalty of less than 40% versus native execution and outperforms QEMU-TCG by 3.3x on RISC-V. |
| **Workload** | x86-64 Linux programs run on Arm, RISC-V and LoongArch hosts, dynamic recompiler (DynaRec) versus the project's own interpreter. |
| **Metric** | throughput |
| **Adoption** | 5.7k stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/ptitSeb/box64) · [benchmark](https://github.com/ptitSeb/box64) |

## Verdict

The only number in the repository is the README's first-party '5-10x faster than the interpreter alone' for DynaRec builds versus Box64's own interpreter, with no workload, CPU, compiler or flags stated. The README-cited EuroSys 2026 paper (co-authored by the Box64 author) reports, per its abstract seen only in search snippets, under 40% average slowdown versus native and 3.3x over QEMU-TCG on RISC-V; its setup and benchmarks were not read.

## Use it when

- Running closed-source x86-64 Linux binaries or games on an Arm64 board, Snapdragon/Apple-Silicon Linux laptop, Ampere server, RISC-V or LoongArch machine where no native build exists.
- Running Windows games on Arm64 Linux via Wine64/Proton (with Box86 or Wine WOW64 for 32-bit parts), where native GL/Vulkan drivers are reached through wrappers.
- Workloads that spend much of their time in wrapped system libraries (libc, libm, SDL, GL), where Box64's wrapping skips emulation entirely.
- Repeated launches of the same binaries, where DynaCache removes recompilation cost on the second run.

## Skip it when

- On an x86-64 host, or for 32-bit x86 programs without Box86/Box32; the DynaRec exists only for Arm64, RISC-V, LoongArch and a work-in-progress PPC64LE backend, other hosts fall back to the interpreter.
- Multithreaded programs that depend on x86 total store order: BOX64_DYNAREC_STRONGMEM defaults to 0 (no barriers), so lock-free guest code can misbehave unless you raise it, which costs speed.
- Code that needs bit-exact x86 floating point or exceptions: FASTNAN=1 and FASTROUND=1 are defaults, division-by-zero exceptions are off (DIV0=0) and x87 80-bit math is done in float/double.
- As an embeddable JIT or library: it is a standalone executable with no API, so it is not a component you can link into your own interpreter.
- Production servers that must not crash: open issues include DynaRec-only failures (Valheim server #4065, Dead Space 2 #4119, Java ZGC/G1 crashes #4023, OpenJDK 25 JIT SIGSEGV #3864) and an unsynchronised memExist() lookup reported as thread-unsafe (#3617).

## How it is fast

The DynaRec is a block-based dynamic binary translator: FillBlock64 in src/dynarec/dynarec_native.c runs four passes per block (pass0 finds addresses, jumps and block size; pass1 does float and flag-liveness optimisation; pass2 sizes native instructions; pass3 emits), with per-host backends in src/dynarec/{arm64,rv64,la64,ppc64le}. Speed comes from deferred and native-flag x86 EFLAGS emulation (only computing flags that are read), big blocks that run past overlaps, CALL/RET optimisation that bypasses the jump table (BOX64_DYNAREC_CALLRET=2 default), and fast-but-inexact defaults for NaN, rounding and memory ordering. Wrapping native libraries means library-heavy code (libc string routines, GL drivers) never gets emulated at all, and DynaCache (default on since v0.4.4) stores translated code under \~/.cache/box64 so second launches skip translation.

## Compared with alternatives

Pick Box64 over Blink when you need to run large dynamically linked x86-64 programs or games on Arm64, RISC-V or LoongArch with native GPU drivers, since Blink is a small portable emulator measured on SSE math and short-lived processes against qemu-x86_64; pick it over research translators such as oxtra or Instrew when you need a maintained tool with Wine/Proton support rather than a paper prototype.

## Integration

| | |
|---|---|
| **Form** | standalone executable built with CMake (registered via binfmt_misc); not a library |
| **Dependencies** | Python 3.7+ at build time (wrapper generation), CMake 3.19+; libz.so loaded at run time via dlopen for DynaCache compression (optional); Zydis only for trace builds; host 64-bit libraries for any wrapped library |
| **Minimum toolchain** | C (-std=gnu11), GCC or Clang; GCC 11+ for Jetson Orin and GCC 15.2+ for the NVIDIA GB10 preset per docs/COMPILE.md |
| **Platforms** | Linux on 64-bit little-endian hosts: AArch64, RISC-V 64, LoongArch64 with DynaRec; PPC64LE DynaRec still WIP; x86-64 build is interpreter only (for testing); Android/Termux experimental |
| **Thread safety** | Emulates multithreaded guests, but x86 memory ordering is only approximated unless BOX64_DYNAREC_STRONGMEM is raised; issue #3617 reports an unlocked memory-map lookup. |
| **Drop-in for the baseline** | partial: the baseline is the same binary with BOX64_DYNAREC=0, so switching is one environment variable; against QEMU user mode it is a drop-in for x86-64 Linux programs only |

## Gotchas

- Default DynaRec settings trade accuracy for speed (STRONGMEM=0, FASTNAN=1, FASTROUND=1, DIV0=0, x87 in float/double where possible); per-program rcfile profiles in /etc/box64.box64rc override these for known-bad titles, so measured speed depends on which profile applied.
- DynaCache is on by default and may use up to 2 GB in \~/.cache/box64; set BOX64_DYNACACHE=2 (read-only) or 0 to disable, and remember it when timing first versus second launches.
- No benchmark harness, workload list, CPU or flags are published in the repository; the '5-10x faster than the interpreter' figure is an unqualified README claim, and the linked box86.org game-performance analysis and the EuroSys 2026 paper could not be opened here (box86.org and dl.acm.org EGRESS_BLOCKED, no PDF copy on GitHub found by two searches).
- Comparisons against QEMU-TCG mix two effects: JIT quality and native-library wrapping (QEMU emulates guest libc and drivers, Box64 calls host builds), and QEMU enforces x86 ordering on weak-memory hosts while Box64 does not by default; BOX64_DYNAREC_STRONGMEM=4 exists to 'mimic x86 TSO similarly to QEMU's approach, for evaluation purposes'.

## Known shortcomings

- README 5-10x is against Box64's own interpreter with no numbers' provenance; the EuroSys 2026 paper abstract (3.3x over QEMU TCG on RISC-V) is snippet only (ACM blocked), so a rebaseline to QEMU and tier B needs the PDF. Off-baseline x86-64 emulator.
- Enricher: no benchmark harness in the repo and the '5-10x vs own interpreter' has no workload, CPU or flags; defaults favour speed over accuracy (STRONGMEM=0 so no x86 TSO, FASTNAN=1, FASTROUND=1, DIV0=0), and the 3.3x QEMU-TCG claim mixes JIT speed with native-library wrapping and QEMU's TSO barriers. Open DynaRec crash issues #4065, #4119, #4023 and thread-unsafe memExist #3617.

## Caveats and trade-offs

README baseline is the project's own interpreter, not an independent incumbent; no workload, CPU or flags named. The stronger comparison (3.3x over QEMU-TCG, RISC-V only) is in the peer-reviewed EuroSys 2026 paper co-authored by the Box64 author, seen only as an abstract snippet because dl.acm.org is blocked and no PDF copy was found on GitHub; that paper could support tier B against QEMU once read. The linked box86.org game-performance analysis (2021) was not opened. Baseline is not one of PyPy, LuaJIT, V8, HotSpot.

User-mode x86-64 Linux emulator that wraps native system libraries; Wine/Proton support; JIT only on the three listed host architectures.

## Maintenance

Very active (last commit 2026-10-06, about 8,960 commits, 5.7k stars, release v0.4.4 adds DynaCache and LoongArch/RISC-V work), MIT-licensed and usable as a packaged tool via Pi-Apps-Coders debs, but the performance claim stays first-party (tier C) until the EuroSys paper's numbers are read.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The README's '5-10x faster than the interpreter alone' is a first-party claim against the project's own interpreter with no workload, CPU or flags. The peer-reviewed EuroSys 2026 paper reports 3.3x over QEMU-TCG on RISC-V, but only its abstract was seen (search snippet; dl.acm.org EGRESS_BLOCKED, no PDF found on GitHub), so it does not lift the tier yet.
- **Verifier notes:** README claim confirmed verbatim; README also cites a EuroSys 2026 paper whose abstract (snippet only) claims 3.3x over QEMU-TCG on RISC-V. If the orchestrator reaches the paper PDF, consider re-baselining to QEMU-TCG and retiering to B. Metadata checked on github.com: MIT, 5.7k stars, last commit 2026-10-06 (active).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ptitSeb/box64>
  - <https://github.com/ptitSeb/box64/commits>
  - <https://raw.githubusercontent.com/ptitSeb/box64/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ptitSeb/box64/HEAD/README.md>
  - <https://raw.githubusercontent.com/ptitSeb/box64/HEAD/docs/COMPILE.md>
  - <https://raw.githubusercontent.com/ptitSeb/box64/HEAD/docs/USAGE.md>
  - <https://raw.githubusercontent.com/ptitSeb/box64/HEAD/docs/CHANGELOG.md>
  - <https://raw.githubusercontent.com/ptitSeb/box64/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ptitSeb/box64/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ptitSeb/box64/HEAD/src/dynarec/dynarec_native.c>
  - <https://raw.githubusercontent.com/ptitSeb/box64/HEAD/src/dynarec/dynacache_compress.c>
  - <https://github.com/ptitSeb/box64>
  - <https://github.com/ptitSeb/box64/tree/main/src/dynarec>
  - <https://github.com/ptitSeb/box64/tree/main/docs>
  - <https://github.com/ptitSeb/box64/issues?q=is%3Aissue+slow+OR+performance+OR+regression>
  - <https://github.com/ptitSeb/box64/issues/3730>
  - <https://github.com/ptitSeb/box64/issues/3617>
  - https://box86.org/index.php/2021/06/game-performances/ (EGRESS_BLOCKED)
  - WebSearch snippets for the EuroSys 2026 paper abstract (https://dl.acm.org/doi/10.1145/3767295.3803574, not opened)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/ptitseb/box64`) · [data/wave12/enrich/raw/github_com_ptitseb_box64.json](../../../data/wave12/enrich/raw/github_com_ptitseb_box64.json) (enrichment confidence 0.6)

</details>
