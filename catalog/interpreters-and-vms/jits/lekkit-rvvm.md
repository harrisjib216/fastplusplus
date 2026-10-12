# RVVM

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `MPL-2.0 (librvvm); GPL-3.0 (rvvm and rvvm-user binaries)` · 🟢 active

> Embeddable RISC-V full-system and userland emulator with a tracing JIT; claims, without numbers, to outrun QEMU TCG.

| | |
|---|---|
| **Beats** | QEMU TCG |
| **Claimed result** | README bullet: 'Tracing JIT with x86_64, ARM64, RISC-V backends - Faster than QEMU TCG'. No numbers given. |
| **Workload** | RISC-V guest emulation with a tracing JIT (RVJIT) with x86_64, ARM64 and RISC-V host backends; no workload named. |
| **Metric** | throughput |
| **Adoption** | 1.3k stars |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/LekKit/RVVM) · [benchmark](https://github.com/LekKit/RVVM) |

## Verdict

No measurement exists: the README and wiki only assert 'Faster than QEMU TCG', crediting the tracing RVJIT IR, less splitting of guest instructions and use of the host FPU. The one figure is the author's informal 'about 10x with some synthetic FPU benchmarks' (search snippet only), with no hardware, compiler or QEMU version.

## Use it when

- Running or embedding a full RV64 Linux/BSD/Haiku guest on an x86-64, ARM64 or RISC-V64 host, where RVJIT is enabled by default
- Products that need a RISC-V VM as a library: librvvm is MPL-2.0 and supports static linking into non-GPL code, with JNI bindings
- FP-heavy guest code where a hardware-FPU interpreter path beats soft-float emulation (the author's only figure is about 10x on synthetic FPU benchmarks, search snippet only)
- Sandboxed emulation on Linux or OpenBSD hosts: seccomp or pledge isolation plus a privilege drop to nobody

## Skip it when

- If you need measured evidence: no RVVM-vs-QEMU benchmark, workload, hardware or QEMU version is published anywhere the verifier or this pass could reach
- Guests that need the Vector extension (RVV) or RVA23-class profiles: USE_RVV defaults to 0 and vectors are a TODO
- Code that depends on bit-exact IEEE behaviour of fused multiply-add under directed rounding: issues #306 to #310 (opened 2026-09-06, still open) report wrong results and flags in the software FMA fallback used on x86-64 hosts without the builtin FMA path
- Hosts without a JIT backend (WASM, DOS, i386 or arm32 for 64-bit guests) fall back to the interpreter, which the wiki calls slower
- Production setups that need QEMU's breadth: virtio devices are on the TODO list, KVM is work in progress, and userland emulation is marked WIP

## How it is fast

RVJIT is a trace-based dynamic binary translator. The interpreter runs guest code and, when it misses in a per-hart JIT TLB, records the instructions it executes (interpret-trace-compile) into a block keyed by physical PC, unrolling through JAL up to a size cap and turning AUIPC+JALR pairs with known targets into direct exits. Guest registers are mapped to host registers with an LRU allocator. Exits to blocks in the same 4 KiB page are patched into direct jumps (block chaining), while cross-page exits do an inline lookup so self-modifying-code invalidation stays per page (dirty-page bitmaps). Floating point is not JIT-compiled; the interpreter runs it on the host FPU, switching host rounding modes, instead of QEMU-style soft-float emulation.

## Compared with alternatives

Pick RVVM over rv32emu or rv8 when you need a full-system RV64 machine (NVMe, PCIe, networking, GUI) that boots stock Linux/BSD images and can be embedded as an MPL-2.0 library. rv32emu has an actual benchmark against QEMU v9.0.0 but targets RV32. For a sandboxed RISC-V scripting engine inside an app, libriscv is the closer fit.

## Integration

| | |
|---|---|
| **Form** | shared lib or static lib (librvvm) plus the rvvm and rvvm-user executables; GNU Make (recommended) or CMake build |
| **Dependencies** | none required (libm for the FPU); optional X11, Wayland or SDL for the GUI and a sound backend; libraries can be probed at runtime |
| **Minimum toolchain** | C compiler; the wiki lists GCC, Clang, cosmocc and TCC as compiler brands; LTO on by default; exact minimum C standard not documented |
| **Platforms** | Hosts: Linux, \*BSD, macOS, Windows, Haiku, also WASM and DOS (no JIT). JIT backends: x86_64, ARM64, RISC-V64 (default), with a LoongArch64 header in src/rvjit and legacy i386, arm32 and riscv32 backends that can only accelerate riscv32 guests |
| **Thread safety** | Multiple machines per process are supported. Each hart owns its own JIT cache, and dirty-memory marking is atomic across harts; other API thread-safety rules are not documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- The 'faster than QEMU TCG' claim has no numbers, workloads, hardware or QEMU version anywhere in the README or wiki; the only figure (about 10x on synthetic FPU benchmarks) is the author's HN comment, seen as a search snippet only.
- The hardware-FPU path, which the wiki credits for the speed, still has open correctness bugs. The software FMA fallback (src/util/fpu_lib.h, used on x86-64 hosts without the optimal builtin FMA) gives wrong results under directed rounding (#309 reports 173 differences in 4,000 directed-mode cases for fmadd.s) and corrupts inf/NaN inputs (#306). RMM rounding is mapped to host round-to-nearest-even with a separate fix-up step.
- When the JIT code cache fills, the whole per-hart cache and its links are flushed (no partial eviction). Caches are not shared between harts ('shared caches' is a TODO), so memory grows with -smp.
- The default branch is 'staging', and the README asks bug reporters to check staging; the last tagged version shown is 0.7-git.

## Known shortcomings

- Directional only: a bare 'faster than QEMU TCG' in the README and wiki with no numbers; the author's 'like 10x' on synthetic FPU benchmarks is a snippet-only quote. Off-baseline (QEMU, not a wasm runtime). MPL-2.0 library, GPL-3.0 binaries.
- Enricher: no benchmark anywhere beyond the author's '\~10x synthetic FPU' snippet; the host-FPU path credited for the speed has open conformance bugs #306-#310 (software FMA fallback on x86-64 gives wrong directed-rounding results, 173 of 4000 diffs in #309, inf/NaN corruption), floating point is not JIT-compiled (TODO 'FPU JIT'), no RVV (USE_RVV=0), and the JIT flushes its whole cache when full.

## Caveats and trade-offs

Tier D: bare claim in README and wiki ('Faster than QEMU TCG'; wiki credits the tracing RVJIT IR, less guest instruction splitting and use of the host hardware FPU), with no benchmark, hardware or QEMU version. A search snippet (snippet only, HN/LinuxLinks) quotes the author saying the hardware FPU path is 'like 10x faster with some synthetic FPU benchmarks', with no methodology. QEMU is not one of the listed incumbents. Licence split: librvvm MPL-2.0, rvvm and rvvm-user binaries GPL-3.0.

Library under MPL-2.0 and binaries under GPL-3.0; JNI bindings are MPL-2.0. Runs Linux, Haiku, FreeBSD and OpenBSD guests; also userland emulation.

## Maintenance

Very active (2,926 commits on the staging branch, last commit 2026-10-05 per the verified record, 45 open issues, many of them recent FPU-conformance reports with fix PRs pending). librvvm is MPL-2.0, so it is usable as a vendored library; the rvvm and rvvm-user binaries are GPL-3.0.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification D, tier now D.
- **Tier reason:** The README only says 'Tracing JIT with x86_64, ARM64, RISC-V backends - Faster than QEMU TCG' and the wiki Home page says emulation performance is higher than QEMU TCG thanks to the tracing RVJIT and the hardware FPU; neither gives numbers, workloads, hardware or a QEMU version, and two web searches found no published RVVM-vs-QEMU benchmark.
- **Verifier notes:** Real, notable project (1.3k stars, active, last commit 2026-10-05), so it stays at tier D on the bare claim. Shortcoming to record: no numbers anywhere for the 'faster than QEMU TCG' claim; only a vague author quote of about 10x on synthetic FPU benchmarks (search snippet only). Licence (MPL-2.0 library, GPL-3.0 binaries) and copyable usability confirmed.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/LekKit/RVVM>
  - <https://raw.githubusercontent.com/LekKit/RVVM/HEAD/README.md>
  - <https://github.com/LekKit/RVVM/commits>
  - <https://github.com/LekKit/RVVM/wiki>
- **Sources the enricher read:**
  - <https://github.com/LekKit/RVVM>
  - <https://raw.githubusercontent.com/LekKit/RVVM/HEAD/README.md>
  - <https://raw.githubusercontent.com/LekKit/RVVM/HEAD/Makefile>
  - <https://raw.githubusercontent.com/LekKit/RVVM/HEAD/CMakeLists.txt>
  - <https://github.com/LekKit/RVVM/wiki>
  - <https://raw.githubusercontent.com/wiki/LekKit/RVVM/Home.md>
  - <https://raw.githubusercontent.com/wiki/LekKit/RVVM/Building-&-Installing.md>
  - <https://raw.githubusercontent.com/wiki/LekKit/RVVM/Running.md>
  - <https://github.com/LekKit/RVVM/tree/staging/src/rvjit>
  - <https://raw.githubusercontent.com/LekKit/RVVM/staging/src/rvjit/rvjit.h>
  - <https://raw.githubusercontent.com/LekKit/RVVM/staging/src/rvjit/rvjit.c>
  - <https://raw.githubusercontent.com/LekKit/RVVM/staging/src/rvjit/rvjit_emit.c>
  - <https://raw.githubusercontent.com/LekKit/RVVM/staging/src/rvjit/rvjit_emit.h>
  - <https://raw.githubusercontent.com/LekKit/RVVM/staging/src/rvjit/rvjit_la64.h>
  - <https://github.com/LekKit/RVVM/tree/staging/src/cpu>
  - <https://raw.githubusercontent.com/LekKit/RVVM/staging/src/cpu/riscv_cpu.c>
  - <https://raw.githubusercontent.com/LekKit/RVVM/staging/src/cpu/riscv_jit.h>
  - <https://raw.githubusercontent.com/LekKit/RVVM/staging/src/cpu/riscv_interpreter.h>
  - <https://raw.githubusercontent.com/LekKit/RVVM/staging/src/cpu/riscv_fpu.h>
  - <https://github.com/LekKit/RVVM/issues?q=qemu+OR+benchmark+OR+performance+OR+slow>
  - <https://github.com/LekKit/RVVM/issues/306>
  - <https://github.com/LekKit/RVVM/issues/309>
  - WebSearch: RVVM RISC-V emulator benchmark vs QEMU TCG coremark dhrystone (snippets only)
  - WebSearch (news.ycombinator.com): "RVVM" RISC-V virtual machine faster than QEMU numbers (snippets of https://news.ycombinator.com/item?id=35009765, thread itself blocked)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/lekkit/rvvm`) · [data/wave12/enrich/raw/github_com_lekkit_rvvm.json](../../../data/wave12/enrich/raw/github_com_lekkit_rvvm.json) (enrichment confidence 0.7)

</details>
