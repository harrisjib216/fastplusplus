# svc-hook (ARM64 system call hook by binary rewriting)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assemblers and assembly tooling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0` · 🟢 active

> LD_PRELOAD library that rewrites every ARM64 svc into a branch to a trampoline, hooking system calls in-process instead of via ptrace.

| | |
|---|---|
| **Beats** | ptrace-based system call interception (README headline, no numbers); ASC-Hook, another ARM64 binary-rewriting syscall hook (Documentation/README.md, with numbers) |
| **Claimed result** | README Key Features: '1,000 times faster than `ptrace`', with no ptrace timing anywhere in the repository. Documentation/README.md 'Overhead Comparision with ASC-Hook': time to hook getpid is 14 ns for svc-hook, 39 ns for ASC-Hook and 3 ns for plain LD_PRELOAD, so the trampoline overhead is 11 ns against 36 ns (about 3.3x, derived from page data); initial setup takes 25 ms against 1890 ms for ASC-Hook ('75 times faster'). The same page reports the cost of hooking against unhooked runs: SQLite per-operation time up 0.01% to 2.6%, PostgreSQL 17.6 pgbench 10790 TPS hooked against 10923 TPS unhooked (1.2% reduction), Samba 4.15 throughput down 0.9% (download, 647 to 641 MB/s) and 0.1% (upload, 858 to 857 MB/s). |
| **Workload** | System call interception on ARM64 Linux, Android, FreeBSD and NetBSD by rewriting every svc instruction in the loaded target to a b instruction that branches to a per-instruction trampoline; the README compares hook cost with ptrace. |
| **Metric** | latency |
| **Hardware** | Documentation experiments: HoneyComb LX2 board, NXP LX2160A 16-core Arm Cortex-A72 up to 2.2 GHz, 64 GB DRAM, Linux 5.10 (the ptrace claim itself states no hardware). |
| **Adoption** | 226 stars |
| **Last commit** | 2026-08-27 |
| **Links** | [repository](https://github.com/retrage/svc-hook) · [benchmark](https://raw.githubusercontent.com/retrage/svc-hook/HEAD/Documentation/README.md) |

## Verdict

The README's '1,000 times faster than ptrace' has no ptrace measurement anywhere in the repository. The only head-to-head numbers are first-party, on a HoneyComb LX2 (NXP LX2160A Cortex-A72, Linux 5.10, glibc 2.31): getpid hook cost of 14 ns for svc-hook, 39 ns for ASC-Hook and 3 ns for plain LD_PRELOAD (11 ns against 36 ns of trampoline overhead, about 3.3x, derived), and 25 ms against 1890 ms of setup. The getpid benchmark code is not in the repository, and the code measured was later changed (see gotchas).

## Use it when

- Tracing, filtering or emulating the syscalls of an unmodified, dynamically linked ARM64 Linux program where ptrace's per-syscall stops would dominate the run time (syscall-heavy servers and databases).
- Building user-space syscall redirection on ARM64 (library OS, sandbox prototypes, fault injection, record and replay) with the zpoline-style hook API.
- Syscall-intensive services that must keep near-native throughput: with a pass-through hook the authors measured 1.2% fewer pgbench TPS on PostgreSQL 17.6 and 0.1-0.9% less Samba throughput.
- Short-lived processes where hook start-up matters: 25 ms of setup against 1890 ms for ASC-Hook in the authors' run.
- ARM64 FreeBSD or NetBSD, which few in-process syscall hooks support.

## Skip it when

- Statically linked or setuid binaries: it relies on LD_PRELOAD (the authors removed -static from sqlite-bench to hook it).
- Security sandboxing: the hook lives in the target's address space, and code that is dlopen'ed, JIT-compiled or mapped after start-up issues unhooked svc instructions, because main.c scans memory only once in its constructor.
- x86-64 or 32-bit Arm targets: ARM64 only (zpoline is the same group's x86-64 counterpart).
- Hooks that call libc on Android or musl: there it loads the hook library with plain dlopen into the same namespace, and the Linux path has no re-entrancy guard (only the BSD path sets hook_active), so libc calls inside the hook appear to re-enter it (from code reading). On glibc it uses dlmopen with a private libc.
- Environments that forbid writable code: it needs mprotect on text pages, GLIBC_TUNABLES=glibc.rtld.seal=0 under glibc memory sealing, procfs on the BSDs and PaX mprotect disabled on NetBSD.

## How it is fast

Before main runs, a constructor reads /proc/self/maps, pattern-matches the svc encoding in every executable ELF section, and overwrites each svc with a direct b to a per-site gate inside the ±128 MiB branch range. The gate loads the return address and jumps to a common handler that saves registers and calls the C hook. A hooked syscall therefore costs a few branches and a register save inside the process instead of the two extra context switches to a tracer that ptrace needs per stop. Setup is fast because it only scans for one fixed instruction pattern, while ASC-Hook disassembles code to find the instructions that set x8.

## Compared with alternatives

The catalogued siblings (Zydis, iced, XED, bddisasm, diStorm and similar) are x86 disassemblers and assemblers; none intercepts system calls, so pick svc-hook only when you need in-process syscall hooking on ARM64. It is the only such tool in the category; on x86-64 use zpoline instead.

## Integration

| | |
|---|---|
| **Form** | shared lib (libsvchook.so via LD_PRELOAD, plus your hook shared library named in LIBSVCHOOK) |
| **Dependencies** | none beyond libc and libdl |
| **Minimum toolchain** | aarch64 GCC or Clang with make (Makefile builds with -O3 -fPIC -Werror; minimum versions not documented); cross-compiling via CC=aarch64-linux-gnu-gcc is supported |
| **Platforms** | ARM64 Linux, Android, FreeBSD, NetBSD |
| **Thread safety** | Rewriting runs once in a constructor before main. The hook is then called on whichever thread makes the syscall, so it must be thread-safe; clone and clone3 with CLONE_VM copy the saved register context onto the child's stack. Otherwise not documented. |
| **Drop-in for the baseline** | partial — replaces ptrace only for in-process interception of dynamically linked programs; it is not an out-of-process tracer, cannot follow static or setuid binaries, and does not see code loaded after start-up |

## Gotchas

- The published numbers come from code later fixed for a correctness bug. Documentation/README.md (Dec 2025, and the paper) predates commit c4c2e5b (2026-08-27). Before that commit, trampolines were mapped with MAP_FIXED at the first page of the reachable window, which silently replaces any mapping already there, and there was no __builtin___clear_cache before mprotect. The fixed allocator may now loop mmap/munmap page by page, and the 14 ns hook cost and 25 ms setup have not been re-measured on it.
- Register state is not fully preserved. On Linux each gate writes the svc immediate into x6, the trampoline uses x14 and x15, and asm_syscall_hook runs cmp before saving context, so those registers and the NZCV flags differ after a hooked svc, although the kernel preserves every register except x0. Inline-asm syscalls that keep live values there could break (found by reading the code; no failure has been reported).
- Side effects inside assert(): the mprotect calls, fopen of /proc/self/maps and the call to __hook_init are all written inside assert(), so a build with -DNDEBUG silently drops them. The shipped Makefile does not define NDEBUG, so build it with that Makefile.
- The memory footprint is understated. The documented 20,812 bytes assumes 28-byte per-svc gates, but the code at the linked commit f65a553 and later emits 6-instruction (24-byte) gates. The figure also leaves out the 512 KiB table of 65,536 'svc #i; ret' stubs that setup_syscall_table writes in every hooked process.

## Known shortcomings

- The "1,000 times faster than ptrace" claim has no ptrace timing anywhere in the repo; the only head-to-head is against ASC-Hook (getpid hook 14 ns vs 39 ns, setup 25 ms vs 1890 ms) with the getpid benchmark code not in the repo and no compiler flags; Middleware 2025 paper unopened (paper-access retier candidate for B); weak fit for assemblers-and-asm-tooling (syscall hook).
- All published numbers (the December 2025 documentation and the paper) were measured on code later fixed: trampolines were mapped MAP_FIXED, silently replacing existing mappings, with no __builtin___clear_cache; fixed in c4c2e5b (2026-08-27) and not re-measured. Code reading: x6, x14, x15 and NZCV change across a hooked svc; mprotect, fopen and __hook_init sit inside assert() and drop under -DNDEBUG; the 512 KiB svc stub table is missing from the documented footprint and the 28-byte gate figure is stale (the code emits 24); the 1000x ptrace claim is unmeasured.

## Caveats and trade-offs

Category fit is weak: syscall-interception tooling built on instruction rewriting, not an assembler or disassembler, and neither ptrace nor ASC-Hook is GNU as, NASM or MASM. The 1,000x ptrace figure is one README bullet with no method, hardware, kernel or command and no ptrace number exists on any repo page. The ASC-Hook numbers are first-party and say only that the setup is 'exactly same with the experiment mentioned in the section 4.1 in our paper'; the getpid microbenchmark is not in the repository and no compiler or flags are stated (hardware for the Documentation experiments: HoneyComb LX2, NXP LX2160A 16-core Cortex-A72 up to 2.2 GHz, 64 GB, Linux 5.10, glibc 2.31). Results 'reflect the implementation state at the time this document was committed' (Dec 2025); NetBSD support and trampoline-allocation changes landed in Aug 2026. The Middleware 2025 paper (Moroo, Tazaki, Yasukata, pages 195-201) was not opened (dl.acm.org blocked). Same research group as zpoline (ARM64 counterpart, separate code base, not a duplicate). Needs GLIBC_TUNABLES=glibc.rtld.seal=0 on glibc with memory sealing, procfs on FreeBSD/NetBSD and PaX mprotect disabled on NetBSD. Language inferred from main.c and the Makefile because the repo page shows no language bar.

ARM64 only (Linux, Android, FreeBSD, NetBSD). Needs no kernel support but rewrites code in memory: svc to b has a +-128 MiB branch range, so one trampoline of 28 bytes per svc instruction is instantiated (20812 bytes for 728 svc instructions in the test setup). FreeBSD and NetBSD need procfs mounted at /proc and NetBSD needs PaX mprotect restrictions disabled.

## Maintenance

Active research prototype from the Middleware 2025 paper (last commit 2026-08-27 adding NetBSD support), Apache-2.0, one roughly 1,000-line C file that is easy to vendor; its fit in assemblers-and-asm-tooling is weak, and its evidence stays tier C because it is first-party and was measured on code with the MAP_FIXED trampoline bug.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party numbers only: the README's '1,000 times faster than ptrace' has no timing at all, while Documentation/README.md gives a getpid hook-overhead comparison with ASC-Hook (14 ns against 39 ns, LD_PRELOAD 3 ns) and an initial-setup comparison (25 ms against 1890 ms) on a stated HoneyComb LX2 (NXP LX2160A Cortex-A72) running Linux 5.10, but the getpid microbenchmark code is not in the repository and no compiler or flags are given. The Middleware 2025 paper (peer-reviewed) could not be opened (dl.acm.org blocked, no mirror found), so it cannot lift the tier to B yet.
- **Verifier notes:** Record is accurate on the ptrace claim (no numbers) but missed the only head-to-head comparison in the repo: Documentation/README.md measures svc-hook against ASC-Hook (getpid hook 14 ns vs 39 ns, setup 25 ms vs 1890 ms), so baseline, benchmark_url and claimed_speedup were corrected. Shortcomings to record: ptrace 1,000x is an unmeasured README bullet; getpid benchmark code absent and compiler flags unstated; weak fit for assemblers-and-asm-tooling. Paper-access retier candidate (Middleware 2025) if dl.acm.org becomes reachable.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-107 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/retrage/svc-hook>
  - <https://github.com/retrage/svc-hook/commits>
  - <https://raw.githubusercontent.com/retrage/svc-hook/HEAD/README.md>
  - <https://raw.githubusercontent.com/retrage/svc-hook/HEAD/Documentation/README.md>
  - <https://raw.githubusercontent.com/retrage/svc-hook/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/retrage/svc-hook/issues?q=is%3Aissue>
  - <https://github.com/retrage/svc-hook/issues/18>
  - <https://github.com/retrage/svc-hook/commits>
  - <https://github.com/retrage/svc-hook/commit/c4c2e5b>
  - <https://raw.githubusercontent.com/retrage/svc-hook/HEAD/README.md>
  - <https://raw.githubusercontent.com/retrage/svc-hook/HEAD/Documentation/README.md>
  - <https://raw.githubusercontent.com/retrage/svc-hook/HEAD/Makefile>
  - <https://raw.githubusercontent.com/retrage/svc-hook/HEAD/main.c>
  - <https://raw.githubusercontent.com/retrage/svc-hook/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/retrage/svc-hook/HEAD/apps/basic/main.c>
  - <https://raw.githubusercontent.com/retrage/svc-hook/41ac430/main.c>
  - <https://raw.githubusercontent.com/retrage/svc-hook/f65a553fa95ffa130636c40022d9764394dce0e3/main.c>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/retrage/svc-hook`) · [data/wave13/enrich/raw/github_com_retrage_svc_hook.json](../../../data/wave13/enrich/raw/github_com_retrage_svc_hook.json) (enrichment confidence 0.7)

</details>
