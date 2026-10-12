# zpoline (x86-64 system call hook by binary rewriting)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assemblers and assembly tooling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0` · 🟡 stale

> LD_PRELOAD library that rewrites every x86-64 syscall instruction into callq \*%rax, hooking system calls in-process instead of via ptrace.

| | |
|---|---|
| **Beats** | ptrace-based system call interception (README headline); Intel Pin System Call API (reviewer Q&A in Documentation/README.md) |
| **Claimed result** | README: '100 times faster than ptrace.' (no numbers on the page). Documentation/README.md (USENIX ATC 2023 reviews Q&A, May 2023): zpoline hook overhead 41 ns (paper Table 1) against 2629 ns for the Intel Pin 3.27 System Call API (2703 ns per getpid minus 74 ns for the kernel getpid), about 64x (derived from page data); the reviewer-suggested short-jump variant gave 31 ns; the later 0xeb 0x6a 0x90 trampoline (May 2023) gave 10 ns, '4 times faster than the previous version'. Paper abstract (WebSearch snippet only, paper not opened): '28.1\~761.0 times lower overhead compared to existing mechanisms which ensure exhaustive hooking'. |
| **Workload** | Per-system-call hook overhead on Linux x86-64 with an empty hook function, measured with the getpid benchmark of Section 3.2 of the USENIX ATC 2023 paper (the benchmark program is not in the repository; apps/basic only prints syscall numbers). |
| **Metric** | latency |
| **Adoption** | 646 stars |
| **Last commit** | 2025-01-06 |
| **Links** | [repository](https://github.com/yasukata/zpoline) · [benchmark](https://raw.githubusercontent.com/yasukata/zpoline/HEAD/Documentation/README.md) |

## Verdict

The README's '100 times faster than ptrace' carries no table, and the repository has no ptrace timing; issue #10 shows the getpid loop and a PTRACE_SYSCALL tracer, but no numbers or hardware. Documentation/README.md quotes the paper's Table 1: 41 ns of hook overhead per getpid, with a hook that returns a dummy value without entering the kernel. Against that it gives a later Intel Pin 3.27 run of 2703 ns minus 74 ns of kernel time (2629 ns, about 64x, derived), plus 31 ns and 10 ns for two trampoline variants. The CPU is only 'our hardware', and all of these figures predate the December 2023 red-zone fix. The paper abstract (search snippet only, paper not reachable) claims 28.1 to 761.0 times lower overhead than exhaustive hooking mechanisms and a 5.2% Redis throughput drop.

## Use it when

- Tracing, filtering or emulating the syscalls of an unmodified, dynamically linked x86-64 Linux program where ptrace's per-syscall stops would dominate the run time (syscall-heavy servers such as the paper's simple HTTP server and Redis).
- Exhaustive in-process hooking where LD_PRELOAD wrappers are not enough because libc and other libraries issue raw syscall instructions internally.
- Prototyping user-space syscall redirection (library OS, user-space network stacks, fault injection, record and replay) on development or test machines where you control sysctl settings.
- Short-running or hot-loop workloads where hook setup happens once at start-up and the per-call cost must stay in the tens of nanoseconds.

## Skip it when

- Security sandboxing: the hook lives in the target's address space, code mapped after start-up (JIT output, later dlopen) issues unhooked syscalls, and a syscall number outside the trampoline makes callq \*%rax jump to an arbitrary address (issue #8: 'we do not have the safeguard').
- Shared or production hosts: it needs root to set /proc/sys/vm/mmap_min_addr to 0 system-wide, which weakens NULL-dereference protection for every process, and SELinux may still block the mapping (issue #21).
- Statically linked or setuid binaries, or anything other than x86-64 Linux: it depends on LD_PRELOAD and the authors' loader for other cases is not public (issue #14); use svc-hook on ARM64.
- Programs with leaf functions that use the red zone heavily or through registers other than rsp: the red-zone workaround aborts at start-up on -0x80 to -0x79(%rsp) accesses and does not track other registers (issue #9, still open).
- Processes that run under vm.overcommit_memory=2 or an RLIMIT_AS cap, or that need very large virtual reservations: the default build reserves a 32 TiB bitmap.

## How it is fast

Before main runs, a constructor walks /proc/self/maps, disassembles every executable mapping with binutils libopcodes and overwrites each two-byte syscall (0f 05) or sysenter (0f 34) with the two-byte callq \*%rax (ff d0). Because rax holds the syscall number (0 to about 500), the call lands in a nop sled mapped at virtual address 0; the sled ends in a jump to asm_syscall_hook, which saves registers and calls the C hook. A hooked syscall therefore costs a call, a slide through the sled and a register save inside the process, instead of the two stops and context switches to a tracer that ptrace needs or the signal delivery that int3 and Syscall User Dispatch need. The sled dominates the cost: 473 nops for getpid in the paper, cut by about 127 with a short jmp planted at the unused epoll_ctl_old slot (214).

## Compared with alternatives

svc-hook is the same group's ARM64 counterpart with the same __hook_init API, so pick zpoline on x86-64 Linux and svc-hook on ARM64; the other catalogued siblings (Zydis, iced, Intel XED, bddisasm, diStorm and similar) are disassemblers or assemblers, not syscall hooks.

## Integration

| | |
|---|---|
| **Form** | shared lib (libzpoline.so via LD_PRELOAD, plus your hook shared library named in LIBZPHOOK and loaded with dlmopen) |
| **Dependencies** | binutils libopcodes (binutils-dev, GPL-3.0), libdl; glibc for dlmopen(LM_ID_NEWLM) |
| **Minimum toolchain** | gcc and make; the Makefile selects the libopcodes API by ld version (2.29+, 2.39+); builds with -O3 -Werror -Wextra; minimum versions not documented |
| **Platforms** | Linux on x86-64 only; requires vm.mmap_min_addr=0 (root) and may need SELinux disabled |
| **Thread safety** | Rewriting runs once in a constructor before main; the hook is then called on whichever thread issues the syscall, so it must be thread-safe. clone and clone3 with CLONE_VM push the return address onto the child's stack. Touching __thread variables inside the hook can recurse through a hooked sched_getaffinity and hang or crash (issue #25, open). |
| **Drop-in for the baseline** | partial — replaces ptrace only for in-process interception of dynamically linked x86-64 programs; it is not an out-of-process tracer, does not see code loaded after start-up, and needs a system-wide sysctl change |

## Gotchas

- Every published number was measured on code with a stack-corruption bug that was fixed later. callq \*%rax pushes its return address into the caller's 128-byte red zone, and the maintainer wrote in issue #9 (Sep 2023): 'we did not know about the red zone while we were writing the paper'. Commit 4c9362d (Dec 2023) added a partial workaround: sub \$0x80,%rsp in the trampoline, and every negative disp8 rsp offset in all loaded code shifted by -8. The same commit removed the 0xeb 0x6a 0x90 trampoline behind the 10 ns figure. HEAD (512 nops plus the reviewer-C short jmp) has not been re-measured.
- The red-zone workaround is heuristic (found by reading do_rewrite). It matches the printed offset against a raw byte within the next 16 bytes, so it can miss AVX-512 compressed-disp8 operands or patch a following instruction. It asserts on -0x80 to -0x79(%rsp), ignores red-zone accesses through other registers, and uses a 136-byte effective red zone that a signal frame can overwrite. Issue #9 is still open.
- Coverage depends on start-up only. A single linear-sweep disassembly runs over the executable mappings that exist before main, so JIT code and later dlopen'd libraries are not rewritten unless you hook mprotect yourself (Documentation/TIPS.md). Data embedded in .text can be mis-decoded, in which case 0f 05 bytes would be overwritten. Syscalls issued before the constructor runs are not hooked.
- Side effects hide inside assert(), and the default build is heavy. The mprotect calls, the fopen of /proc/self/maps, the hook_init call and the bitmap mmap are all written inside assert(), so a -DNDEBUG build silently drops them. The default Makefile defines SUPPLEMENTAL__REWRITTEN_ADDR_CHECK, which reserves a (1&lt;&lt;48)&gt;&gt;3 = 32 TiB MAP_NORESERVE bitmap that fails under strict overcommit or RLIMIT_AS, and it adds a bitmap lookup to every hooked call.

## Known shortcomings

- The 100x-over-ptrace headline has no numbers in the README; the Pin figure (2629 ns vs 41 ns) was measured separately from the paper run with the CPU given only as "our hardware"; the getpid benchmark and the gcc -O3 ptrace tracer live in issue #10, not the repo; needs mmap_min_addr=0 and links GPL-3.0 libopcodes; USENIX ATC 2023 paper unopened (retier candidate for B, abstract claims 28.1-761.0x lower overhead); weak category fit. Last commit 2025-01-06.
- Every published number (41 ns, 31 ns, 10 ns hook overhead; Pin 2629 ns) was measured on code with red-zone corruption: callq \*%rax clobbers the caller's red zone, and the maintainer wrote in issue #9 that they did not know about the red zone while writing the paper. Commit 4c9362d (Dec 2023) added a partial workaround and removed the 0xeb 0x6a 0x90 trampoline behind the 10 ns figure; HEAD has not been re-measured and #9 stays open. An invalid rax jumps to an arbitrary address (#8), JIT and later-dlopen code is not hooked, the default build reserves a 32 TiB MAP_NORESERVE bitmap, side effects live inside assert(), and TLS use in a hook recurses (#25).

## Caveats and trade-offs

Category fit is weak: this is syscall-interception tooling built on instruction rewriting, not an assembler or disassembler, and the baselines (ptrace, Intel Pin) are not GNU as, NASM or MASM. The 100x headline has no table, hardware, kernel version or compiler flags on the README page. The 41 ns, 2629 ns and 10 ns figures come from the repo's Documentation page and quote the paper's Table 1 (paper not opened: usenix.org is not reachable here); the CPU is only called 'our hardware'. The 64x ratio mixes the paper's zpoline run with a Pin run done later for the reviews, possibly on different days. The getpid benchmark program is not in the repository; the author posted it and a PTRACE_SYSCALL-based tracer (compiled with gcc -O3, run with 1000 iterations against 100000 for the zpoline run) in issue #10 in November 2023, and the hook returns a dummy value without entering the kernel; setup time (trampoline, rewriting, dlmopen) is excluded from the overhead. Requires /proc/sys/vm/mmap_min_addr set to 0 (trampoline at virtual address 0, which weakens NULL-dereference protection; SELinux may also need disabling). The code is Apache-2.0 but links binutils libopcodes (GPL-3.0) for disassembly. The last commit is from January 2025. [retier] Category fit is weak: syscall-interception tooling built on instruction rewriting, with ptrace and Intel Pin as baselines. The 100x headline has no table, hardware, kernel version or flags on the README; the 41 ns, 2629 ns and 10 ns figures quote the ATC 2023 paper's Table 1 (paper not opened here). Every published number was measured on code with a stack-corruption bug: callq \*%rax pushes into the caller's 128-byte red zone, and the maintainer wrote in issue #9 (Sep 2023) that they did not know about the red zone while writing the paper; commit 4c9362d (Dec 2023) added a partial workaround (sub \$0x80,%rsp) and removed the 0xeb 0x6a 0x90 trampoline behind the 10 ns figure, and HEAD has not been re-measured; #9 stays open. An invalid rax jumps to an arbitrary address (#8); JIT and later-dlopen code is not hooked (TIPS.md); the default build reserves a 32 TiB MAP_NORESERVE bitmap; side effects inside assert(); TLS use in a hook recurses (#25).

Linux on x86-64 only. Replaces the two-byte syscall/sysenter instructions in loaded code with callq \*%rax and plants a nop-sled trampoline at virtual address 0, so /proc/sys/vm/mmap_min_addr must be set to 0 (the README also reports mmap failures under SELinux). Uses the libopcodes disassembler from binutils to find the instructions. Rewritten code pages can no longer be shared between processes (glibc-2.35 has 544 syscall/sysenter instructions across 62 pages). Hook functions must avoid issuing rewritten syscalls or they loop forever. NULL-pointer writes no longer fault by default (mitigations exist).

## Maintenance

A stale research prototype from the USENIX ATC 2023 best paper: the last commit is from 2025-01-06, and the red-zone (#9) and TLS (#25) issues are still open. The Apache-2.0 code is a single roughly 550-line main.c that is easy to vendor, but it links GPL-3.0 libopcodes. Its evidence stays tier C because the numbers are first-party, the hardware is unstated, and they were measured on code that was later changed for a correctness bug.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The repo's Documentation/README.md gives first-party per-getpid hook overheads (zpoline 41 ns from paper Table 1, later 10 ns; Intel Pin 2703 ns minus 74 ns kernel time) with only 'our hardware' as the machine, and the README's 100x ptrace claim has no numbers. The getpid benchmark and a gcc -O3 ptrace tracer were posted by the author in issue #10 (Nov 2023), but no CPU model or full flags are stated, so not A; the USENIX ATC 2023 paper (peer-reviewed; abstract snippet: '28.1\~761.0 times lower overhead compared to existing mechanisms which ensure exhaustive hooking') could not be opened, so B is not reached yet.
- **Verifier notes:** Record is accurate; claimed_speedup and caveats extended with the paper-abstract snippet and the issue #10 benchmark programs (getpid loop and ptrace tracer, gcc -O3). Shortcomings to record: 100x ptrace headline unmeasured on repo pages, Pin comparison measured separately from the paper's zpoline run, CPU unstated, mmap_min_addr=0 requirement, GPL-3.0 libopcodes link dependency, weak category fit. Paper-access retier candidate to B (USENIX ATC 2023 best paper, usenix.org blocked here).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-107 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/yasukata/zpoline>
  - <https://github.com/yasukata/zpoline/commits>
  - <https://github.com/yasukata/zpoline/issues/10>
  - <https://raw.githubusercontent.com/yasukata/zpoline/HEAD/README.md>
  - <https://raw.githubusercontent.com/yasukata/zpoline/HEAD/Documentation/README.md>
  - <https://raw.githubusercontent.com/yasukata/zpoline/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/yasukata/zpoline/HEAD/README.md>
  - <https://raw.githubusercontent.com/yasukata/zpoline/HEAD/Documentation/README.md>
  - <https://raw.githubusercontent.com/yasukata/zpoline/HEAD/Documentation/TIPS.md>
  - <https://raw.githubusercontent.com/yasukata/zpoline/HEAD/main.c>
  - <https://raw.githubusercontent.com/yasukata/zpoline/HEAD/Makefile>
  - <https://raw.githubusercontent.com/yasukata/zpoline/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/yasukata/zpoline/HEAD/apps/basic/main.c>
  - <https://raw.githubusercontent.com/yasukata/zpoline/HEAD/apps/basic/Makefile>
  - <https://github.com/yasukata/zpoline/commits>
  - <https://github.com/yasukata/zpoline/commit/4c9362d>
  - <https://github.com/yasukata/zpoline/issues?q=is%3Aissue>
  - <https://github.com/yasukata/zpoline/issues/8>
  - <https://github.com/yasukata/zpoline/issues/9>
  - <https://github.com/yasukata/zpoline/issues/10>
  - <https://github.com/yasukata/zpoline/issues/14>
  - <https://github.com/yasukata/zpoline/issues/25>
  - <https://github.com/yasukata/zpoline/pull/20>
  - <https://github.com/lazypoline/lazypoline>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/yasukata/zpoline`) · [data/wave13/enrich/raw/github_com_yasukata_zpoline.json](../../../data/wave13/enrich/raw/github_com_yasukata_zpoline.json) (enrichment confidence 0.7)

</details>
