# Instrew

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `LGPL-2.1-or-later` · 🟢 active

> LLVM-based user-mode dynamic binary translator for Linux (x86-64, AArch64, RISC-V64 guests); paper reports far lower overhead than QEMU and HQEMU.

| | |
|---|---|
| **Beats** | QEMU and HQEMU (LLVM-based dynamic binary translation) |
| **Claimed result** | VEE'21 paper 'Efficient LLVM-Based Dynamic Binary Translation' (snippet only, PDF blocked): on SPEC CPU2017, x86-64 guest on x86-64 host, Instrew 'achieves an emulation overhead of just 53% compared to QEMU with 648% and HQEMU with 124%'; another snippet gives mean overhead 53% (67% INT, 40% FP) for Instrew vs 124% (136% INT, 114% FP) for HQEMU and 716% (275% INT, 1541% FP) for QEMU, noting QEMU did not finish all FP benchmarks in reasonable time because of software floating point. Run time about 4.9x lower than QEMU and 1.46x lower than HQEMU (derived from snippet data, 7.48/1.53 and 2.24/1.53). The RISC-V guest figures in the search record (76% vs 202% INT, 40% vs 1267% FP) were not re-confirmed by any snippet seen here. |
| **Workload** | LLVM-based dynamic binary translator running SPEC-style integer and floating-point benchmarks for x86-64 and RISC-V64 guests on x86-64 hosts, emulation overhead relative to native. |
| **Metric** | throughput |
| **Adoption** | 292 stars |
| **Last commit** | 2026-09-10 |
| **Links** | [repository](https://github.com/aengelke/instrew) · [benchmark](https://home.cit.tum.de/~engelke/pubs/2104-vee.pdf) |

## Verdict

Only search snippets of the VEE'21 paper were seen: on SPEC CPU2017 Instrew's mean overhead over native is 53% (67% INT, 40% FP) versus HQEMU 124% and QEMU 648% (another snippet: 716%, QEMU not finishing all FP runs because of softfloat), and a second summary gives 59% vs QEMU 1044% and HQEMU 135% on x86-64; the x86-64 test machine was 2x Intel Xeon E5-2697 v3 (Haswell, 2.6 GHz) per snippet. Compiler, flags, LLVM version and whether translation time is included were not seen, and the numbers come from 2021 code.

## Use it when

- Long-running, single-threaded, compute-bound Linux programs (SPEC CPU-style kernels) where LLVM optimization time is repaid by faster translated code.
- Cross-ISA user-mode runs of RISC-V64 or AArch64 binaries on x86-64 (or x86-64 binaries on AArch64) when qemu-user is too slow, especially for floating-point-heavy code that QEMU emulates in software.
- Research or tooling that wants guest code as LLVM IR: -dumpir prints IR after lifting, calling-convention change, optimization or codegen, and -perf=2 writes JITDUMP for profiling translated code.
- Repeated runs of the same binary: -cache stores compiled objects under \~/.cache/instrew and skips lifting and codegen on a hit.

## Skip it when

- Multi-threaded guests: clone with CLONE_VM returns -EOPNOTSUPP ('multi-threading is currently not implemented', client/emulate.c; issue #9).
- Programs that install signal handlers or recover from SIGSEGV/SIGBUS: a delivered guest signal with a handler aborts the process ('guest signal handling not implemented').
- Guests that generate or modify code at run time (JITs, self-modifying code): mmap, mprotect and munmap pass straight to the host with no code-cache invalidation.
- Full-system emulation, non-Linux guests or big-endian hosts; and recent-distro binaries that use syscalls the client does not emulate (README warning; issue #18 for Ubuntu 24.04 is open).
- Short-lived processes where per-function LLVM compilation dominates; no published numbers cover startup-heavy workloads.

## How it is fast

The Rellume lifter decodes a whole guest function's control-flow graph and lifts it to one LLVM IR function, so guest registers live in SSA values across basic blocks instead of being spilled to a CPU-state struct at every block as in QEMU TCG. The server runs a short LLVM pass list (DCE, EarlyCSE, InstCombine, MemCpyOpt) and the LLVM back end at -O2 by default, and Rellume models SIMD and FP instructions so LLVM emits native host code for them. A register-based calling convention between translated functions (fastcc, on by default) and optional call/ret lifting (-callret) cut the cost of control transfers; translated objects can be cached on disk keyed by a SHA-1 of the code bytes and configuration.

## Compared with alternatives

Pick Instrew over Blink, rv8 or oxtra when you need several guest ISAs (x86-64, AArch64, RISC-V64) and peak translated-code quality from LLVM on long-running compute kernels; pick Box64 for real-world x86-64 applications on ARM64 that need threads, signals and Wine, which Instrew does not handle.

## Integration

| | |
|---|---|
| **Form** | standalone executable (meson/ninja build; server binary embeds the client) |
| **Dependencies** | LLVM 21-23 (shared or static), OpenSSL libcrypto (SHA-1 for the cache), git submodules Rellume, fadec, frvdec, farmdec; python3 at build time; clang and lld for the test suite |
| **Minimum toolchain** | C++17 and C11, meson 0.52+, LLVM 21 to 23 (the September 2026 port dropped older LLVM) |
| **Platforms** | Linux user mode only; hosts x86-64 and AArch64 (little-endian); guests x86-64, AArch64, RISC-V64 rv64imafdc |
| **Thread safety** | Guest multi-threading not implemented (clone with CLONE_VM fails); fork is supported and gets its own server connection. |
| **Drop-in for the baseline** | partial — command-line replacement for qemu-user on single-threaded Linux ELF binaries that use no signal handlers and no run-time code generation; no system mode, no plugin API comparable to QEMU TCG plugins |

## Gotchas

- README says -targetopt defaults to 3, but server/codegenerator.cc sets init(2) and documents 'default: 2'; the TargetMachine is also created with empty CPU and feature strings, so translated code targets the generic host baseline (for example plain x86-64), not -mcpu=native.
- Signal support is explicitly marked 'very simple and INCORRECT' in client/emulate.c: only SIG_DFL and SIG_IGN work, handlers abort, guest sigreturn aborts.
- No address-space isolation: guest mmap/mprotect/munmap/brk run natively ('TODO: catch dangerous maps'), so a guest can map over the client or its code cache.
- The headline overhead figures could not be tied to one configuration: search snippets give 53% vs QEMU 648% and HQEMU 124%, another 59% vs 1044% and 135% on x86-64, and one summary attributes the 53/648/124 set to a RISC-V guest on an AArch64 host; the paper PDF was blocked and the repo has no benchmark scripts.

## Known shortcomings

- The VEE'21 paper was blocked on every host tried, so the 53% overhead against QEMU's 648%/716% and HQEMU's 124% is snippet only and the RISC-V numbers were not reconfirmed; paper access (home.cit.tum.de/\~engelke/pubs/2104-vee.pdf) would likely raise it to B. Off-baseline (QEMU).
- Enricher: no guest threads (clone with CLONE_VM returns -EOPNOTSUPP), any guest signal handler aborts, no code-cache invalidation, and codegen targets a generic host CPU; the README says -targetopt defaults to 3 while the code says 2. The paper numbers are snippet only and conflict (53% vs QEMU 648% and HQEMU 124% in one, 59% vs 1044% and 135% in another; 2x Xeon E5-2697 v3).

## Caveats and trade-offs

Snippet only: the peer-reviewed VEE'21 paper (linked from the README, which also lists the VEE'20 Instrew paper and the 2021 TUM dissertation) could not be opened, so CPU, compiler, flags and whether translation time is included are unverified; a verifier with the paper may raise it to B. The headline QEMU overhead differs between snippets (648% vs 716%), and QEMU's FP figure is dominated by softfloat. The VEE'20 paper reports an average overhead of 72% vs Valgrind 367% and HQEMU LLVM-only 142% (snippet only). Numbers are from 2021 code; master was updated in September 2026 for LLVM 21-23 after a gap since June 2024. Overheads are relative to native execution (lower is better). Baseline is not one of PyPy, LuaJIT, V8, HotSpot.

Needs LLVM at run time (client/server split in the repo); guests x86-64, AArch64, RISC-V64; hosts x86-64 and AArch64 (README).

## Maintenance

Active again (LLVM 21-23 port on 2026-09-10 after no commits since 2024-06-07), single maintainer, LGPL-2.1-or-later, 4 open issues including an unhandled-syscall report and a segfault; usable as a research-grade translator, not a production qemu-user replacement.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The VEE'21 paper (peer-reviewed) and every copy tried (home.in.tum.de, home.cit.tum.de, llvm.org slides, d-nb.info thesis, conf.researchr.org) were EGRESS_BLOCKED; WebSearch snippets give the SPEC CPU2017 overheads (Instrew 53% vs QEMU 648% and HQEMU 124%) but no methodology was seen, and the repo has no benchmark scripts. C until someone reads the paper, which would likely make it B.
- **Verifier notes:** Metadata confirmed (292 stars, LGPL-2.1-or-later per README, not a fork, last commit 2026-09-10, active). Keep at C pending paper access (add to the paper-access retier list: home.cit.tum.de/\~engelke/pubs/2104-vee.pdf); headline 53% vs 648%/124% confirmed only by search snippets, the RISC-V numbers not at all.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/aengelke/instrew/HEAD/README.md>
  - <https://github.com/aengelke/instrew>
  - <https://github.com/aengelke/instrew/commits>
  - <https://github.com/aengelke?tab=repositories>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/aengelke/instrew/HEAD/README.md>
  - <https://github.com/aengelke/instrew>
  - <https://github.com/aengelke/instrew/issues?q=is%3Aissue>
  - <https://github.com/aengelke/instrew/commits/master>
  - <https://raw.githubusercontent.com/aengelke/instrew/HEAD/meson.build>
  - <https://raw.githubusercontent.com/aengelke/instrew/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/aengelke/instrew/HEAD/server/meson.build>
  - <https://raw.githubusercontent.com/aengelke/instrew/HEAD/client/meson.build>
  - <https://raw.githubusercontent.com/aengelke/instrew/HEAD/test/meson.build>
  - <https://raw.githubusercontent.com/aengelke/instrew/HEAD/server/config.cc>
  - <https://raw.githubusercontent.com/aengelke/instrew/HEAD/server/config.h>
  - <https://raw.githubusercontent.com/aengelke/instrew/HEAD/server/cache.cc>
  - <https://raw.githubusercontent.com/aengelke/instrew/HEAD/server/codegenerator.cc>
  - <https://raw.githubusercontent.com/aengelke/instrew/HEAD/server/optimizer.cc>
  - <https://raw.githubusercontent.com/aengelke/instrew/HEAD/server/rewriteserver.cc>
  - <https://raw.githubusercontent.com/aengelke/instrew/HEAD/server/callconv.cc>
  - <https://raw.githubusercontent.com/aengelke/instrew/HEAD/server/connection.cc>
  - <https://raw.githubusercontent.com/aengelke/instrew/HEAD/client/main.c>
  - <https://raw.githubusercontent.com/aengelke/instrew/HEAD/client/emulate.c>
  - <https://raw.githubusercontent.com/aengelke/instrew/HEAD/client/translator.c>
  - <https://raw.githubusercontent.com/aengelke/instrew/HEAD/client/dispatch.c>
  - <https://raw.githubusercontent.com/aengelke/instrew/HEAD/client/memory.c>
  - <https://raw.githubusercontent.com/aengelke/rellume/HEAD/README.md>
  - https://mediatum.ub.tum.de/doc/1614897/1614897.pdf (blocked, 403)
  - WebSearch: Efficient LLVM-Based Dynamic Binary Translation Instrew SPEC CPU2017 (snippets only)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/aengelke/instrew`) · [data/wave12/enrich/raw/github_com_aengelke_instrew.json](../../../data/wave12/enrich/raw/github_com_aengelke_instrew.json) (enrichment confidence 0.6)

</details>
