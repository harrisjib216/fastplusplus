# lazypoline (hybrid SUD plus binary-rewriting syscall interposer)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assemblers and assembly tooling](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MIT` · 🟢 active

> x86-64 Linux syscall interposer: traps each syscall site once via Syscall User Dispatch, then rewrites it zpoline-style; exhaustive, near-zpoline steady state.

| | |
|---|---|
| **Beats** | zpoline (binary rewriting) and pure Syscall User Dispatch (SUD) interposition; the paper also discusses ptrace and seccomp-based interposition but the artifact scripts opened here only run baseline, zpoline, lazypoline and SUD variants |
| **Claimed result** | No numbers on any opened page. README and artifact give no results; they are in Table II and Figures 4 and 5 of the DSN 2024 paper 'System Call Interposition Without Compromise' (egress-blocked). Qualitative claim in README: 'fast, exhaustive, and expressive'; paper abstract (search snippet) claims the efficiency of pure rewriting for syscall-intensive workloads. |
| **Workload** | DSN 2024 artifact (github.com/lazypoline/benchmarks): bench/bench_micro.sh runs a syscall microbenchmark pinned to one core, 10 repetitions, for plain syscall baseline, zpoline, lazypoline with SUD interposition, SUD enabled without interposition, lazypoline after rewriting, SUD disabled and with extended-state (vector) preservation; bench_nginx.sh and bench_lighttpd.sh drive nginx and lighttpd with 12 workers and wrk. |
| **Metric** | latency |
| **Hardware** | 48-core Intel Xeon Gold 5318S at 2.10 GHz, 1.0 TiB RAM, hyperthreading disabled, Ubuntu 22.04.3 LTS, Linux 5.15.0-83 (benchmarks README) |
| **Adoption** | 32 stars, 6 forks; peer-reviewed at IEEE/IFIP DSN 2024 (pp. 183-194); superseded by the same group's Secpoline (USENIX Security 2026), which the README links |
| **Last commit** | 2026-06-15 |
| **Links** | [repository](https://github.com/lazypoline/lazypoline) · [benchmark](https://github.com/lazypoline/benchmarks) |

## Verdict

No numbers could be read: Table II and Figures 4-5 of the DSN 2024 paper are egress-blocked here (repository.tudelft.nl failed DNS, adriaanjacobs.github.io blocked), and neither repository prints results. The artifact's microbenchmark times 1e8 invocations of invalid syscall 500 with rdtsc on one pinned core, subtracts an empty-loop noise run, and reports the geometric mean of 10 runs as a ratio to a plain syscall loop for zpoline (with its rewritten-address check disabled by zpoline.patch), lazypoline, lazypoline with xstate preservation, SUD enabled without interposition, and pure SUD interposition. Everything is built with clang -O3 -flto -march=native (Ubuntu 22.04 apt clang) and run on a 48-core Xeon Gold 5318S, Linux 5.15.0-83, with hyperthreading off.

## Use it when

- Tracing, sandboxing or emulating every syscall of an unmodified x86-64 Linux binary where ptrace or pure-SUD cost (one SIGSYS per call) is too high, e.g. syscall-heavy servers such as nginx or lighttpd, which the DSN 2024 artifact benchmarks
- Programs that generate or load code at run time (JITs, tcc, dlopen'd plugins) where zpoline's load-time scan would miss sites; the artifact's exhaustiveness test shows zpoline missing getpid from tcc-generated code
- Research or prototyping of syscall-level tools where you can edit and rebuild one C++ dispatch function
- Kernels 5.11 or newer on hosts where you are allowed to set vm.mmap_min_addr=0

## Skip it when

- Security monitoring against a hostile application: the interposer shares the address space and its selector byte and is not isolated; the authors' Secpoline (github.com/lazypoline/secpoline, USENIX Security 2026) adds isolation and says it supersedes lazypoline
- Non-x86-64 targets (the call \*%rax trampoline is x86-specific; see svc-hook for ARM64) or kernels older than 5.11
- Hosts where mapping page 0 is forbidden (vm.mmap_min_addr must be 0, a hardening regression), or apps that use the %gs base themselves
- Applications that call unshare, use clone with CLONE_VM but without CLONE_THREAD or CLONE_VFORK, or need clone3: unshare and unsupported clone flags hit asserts, and clone3 is answered with -ENOSYS so glibc falls back to clone
- Short-lived processes with many distinct syscall sites: each site pays one SIGSYS trap plus two mprotect calls before it is rewritten, and syscalls made before or during loading of the preload library are missed

## How it is fast

Hybrid interposition: SUD (prctl PR_SET_SYSCALL_USER_DISPATCH, Linux 5.11+) delivers SIGSYS the first time a syscall site runs, and the handler overwrites that 2-byte `syscall` (0f 05) with `callq *%rax` (ff d0). Later executions jump into a nop sled mapped at virtual address 0 (the zpoline trampoline) and on to an assembly hook, with no signal and no kernel round trip for the redirect. A per-thread selector byte at %gs:0 is flipped to ALLOW while the interposer runs and back to BLOCK on return. xsave/xrstor of vector state (SAVE_VECTOR_REGS) is a compile-time option.

## Compared with alternatives

Pick lazypoline over zpoline when the target generates or loads code after startup and you need every syscall caught; zpoline rewrites everything at load time, has a hook-library API and no first-hit trap, so prefer it for static binaries. svc-hook is the ARM64 counterpart of zpoline, and the disassembler and assembler siblings solve unrelated problems.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | CMake 3.16+, clang/clang++ (hard-coded in CMakeLists.txt), libpthread, libdl; glibc-specific sysdeps/ headers and SIGSETSIZE in util.h must match the running glibc |
| **Minimum toolchain** | C++20 with clang (CMakeLists sets clang explicitly); built with -O3 -flto -march=native |
| **Platforms** | x86-64 Linux 5.11+ only; tested on Ubuntu 20.04 and 22.04 (glibc 2.35); -march=native output is not portable to other CPUs |
| **Thread safety** | Multi-threaded and multi-process programs are supported (per-thread state at %gs, rewrites under a spinlock, test cases in main.cpp cover threads, fork and signal delivery), but there is no formal statement |
| **Drop-in for the baseline** | partial: launched the same way as zpoline (LD_PRELOAD plus mmap_min_addr=0), but zpoline loads a separate hook library (LIBZPHOOK, __hook_init) while lazypoline is customised by editing syscall_emulate and rebuilding |

## Gotchas

- Harness flaw in the DSN artifact (github.com/lazypoline/benchmarks, bench/bench_micro.sh): the xstate-preserving 'lazypoline\*' run comes straight after the 'SUD disable' step and never switches the microbenchmark back from mb_config_sud_disable.h, so the app turns SUD off before timing. That row therefore leaves out the kernel's SUD slow-path cost, and plot_micro.py also subtracts the SUD\* overhead from the xstate segment, so the Figure 4 bar for the full configuration (SUD on, vector state saved) is understated by roughly the SUD\* overhead.
- The headline 'lazypoline' microbenchmark row uses config_rw_zpoline.h with SAVE_VECTOR_REGS 0, so the interposer does not preserve vector registers. The repository default is SAVE_VECTOR_REGS 1, the slower 'lazypoline\*' row. The loop calls invalid syscall 500 (-ENOSYS) via a pre-written `callq *%rax`, so it measures steady-state hook cost on a near-empty kernel body, not the first-hit SIGSYS-and-rewrite path.
- The default config.h has PRINT_SYSCALLS 1 (commit 'print syscalls by default', 2024-03-27), so an out-of-the-box build fprintf's every syscall to stderr; set it to 0 before measuring anything. asserts stay on in the -O3 build because NDEBUG is not defined.
- rewrite_syscall_inst mprotects only the page holding the first byte of the 2-byte syscall (an instruction straddling a page boundary is not handled), makes the page write+exec without read while it patches, and then sets it to read+exec whatever it was before (JIT pages that need RWX need COMPAT_NONDEP_APP). The vDSO is assumed to be one page ('check whether your vdso is larger than a page'). Bugs fixed after the paper: red-zone clobbering on the signal-return trampoline (2025-04-21) and xsave across setup_new_thread (2025-01-12); the artifact pins src at aed8164, which predates both.

## Known shortcomings

- No reachable numbers: the DSN 2024 paper is blocked (the author's github.io source repo returns 404) and the artifact repo has no results, compiler or flags; peer reviewed, 32 stars; paper-access retier candidate.
- Enricher: in lazypoline/benchmarks bench_micro.sh the xstate run never resets the microbench from mb_config_sud_disable.h, so the app disables SUD before timing, and plot_micro.py subtracts the SUD overhead from the xstate segment, so Figure 4's full-configuration bar is understated by about that overhead; the headline row uses SAVE_VECTOR_REGS 0 (non-default); the microbench is invalid syscall 500 through a pre-rewritten call, steady state only. Default config.h has PRINT_SYSCALLS 1; the artifact pins src aed8164, before the 2025 redzone and xsave fixes. Successor: lazypoline/secpoline (USENIX Security 2026, no README numbers).

## Caveats and trade-offs

No usable numbers: the DSN paper (adriaanjacobs.github.io, repository.tudelft.nl, zenodo) is egress-blocked and neither README nor the artifact repo prints results, so the tier is D although the work is peer reviewed and the benchmark scripts are public (compiler and flags not described; the artifact repo has no licence file and 0 stars). A third-party table seen only as a search snippet (SysComb, arXiv 2608.26871, getpid x 1e6 on Linux 6.8: native about 166 ns, ptrace 11,931 ns, SUD 2,658 ns, zpoline 198 ns) does not include lazypoline. By design lazypoline is not expected to beat zpoline on raw latency; its claim is near-zpoline cost with exhaustiveness, and a large gain over SUD-only and ptrace. The latest commit (2026-06-15) is a README edit; last code change 2025-04-21 ('redzone fix'). A verifier with paper access should read Table II and could raise this to B or A. [retier] Enricher: bench_micro.sh's xstate run leaves SUD disabled and plot_micro.py subtracts the SUD overhead, so the full-configuration bar is understated; the headline row uses non-default SAVE_VECTOR_REGS 0; the artifact pins a commit before the 2025 redzone and xsave fixes.

Needs Linux 5.11+ (SUD) and permission to mmap the zero page (vm.mmap_min_addr=0) like zpoline; exhaustive interposition of dynamically generated code that zpoline misses (the artifact's exhaustiveness test shows zpoline missing getpid from tcc-generated code); not isolated from a malicious application (that is what Secpoline adds); tested on Ubuntu 20.04 and 22.04 glibc 2.35; per the paper abstract (search snippet) each syscall site is first caught through the slow kernel SUD path and only then rewritten, so first executions cost more than later ones.

## Maintenance

Research artifact with occasional maintenance (last code change 'redzone fix' 2025-04-21, README edit 2026-06-15, one closed build issue); MIT-licensed and small enough to vendor, but the authors point new users to Secpoline, which says it supersedes lazypoline. The published artifact's xstate microbenchmark row runs with SUD disabled, so its full-configuration overhead is understated.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now D.
- **Tier reason:** Neither the lazypoline README nor the artifact repo github.com/lazypoline/benchmarks prints any result; the README there gives only the hardware (48-core Intel Xeon Gold 5318S at 2.10 GHz, 1.0 TiB RAM), suite runtimes and the scripts (bench/bench_micro.sh, bench_nginx.sh, bench_lighttpd.sh), with no compiler or flags. The DSN 2024 paper holding the numbers is unreachable (adriaanjacobs.github.io blocked, no public adriaanjacobs.github.io source repo, raw.githubusercontent.com copy 404), and two searches found no lazypoline figures in snippets.
- **Verifier notes:** Real, peer-reviewed project (MIT, last commit 2026-06-15 README edit, last code change 2025-04-21 'redzone fix'), but no numbers are reachable, so tier D; record shortcoming 'no reachable numbers; paper Table II and Figures 4-5 unread; artifact repo has 0 stars and no visible licence file; compiler and flags unstated'. A later paper-access retier could raise it to B (DSN paper) or A if the paper states compiler and flags. Low star count but peer reviewed, so keep rather than reject.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-122 (wave 13 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/lazypoline/lazypoline>
  - <https://github.com/lazypoline/lazypoline/commits>
  - <https://github.com/lazypoline/benchmarks>
  - <https://raw.githubusercontent.com/adriaanjacobs/adriaanjacobs.github.io/HEAD/files/dsn24lazypoline.pdf>
  - <https://github.com/adriaanjacobs/adriaanjacobs.github.io>
- **Sources the enricher read:**
  - <https://github.com/lazypoline/lazypoline>
  - <https://raw.githubusercontent.com/lazypoline/lazypoline/HEAD/README.md>
  - <https://raw.githubusercontent.com/lazypoline/lazypoline/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/lazypoline/lazypoline/HEAD/config.h>
  - <https://raw.githubusercontent.com/lazypoline/lazypoline/HEAD/lazypoline.cpp>
  - <https://raw.githubusercontent.com/lazypoline/lazypoline/HEAD/zpoline.cpp>
  - <https://raw.githubusercontent.com/lazypoline/lazypoline/HEAD/sud.cpp>
  - <https://raw.githubusercontent.com/lazypoline/lazypoline/HEAD/asm_syscall_hook.asm>
  - <https://raw.githubusercontent.com/lazypoline/lazypoline/aed816456e9466e299f1771b4e94065cb7a293f0/config.h>
  - <https://github.com/lazypoline/lazypoline/issues?q=is%3Aissue>
  - <https://github.com/lazypoline/lazypoline/commits>
  - <https://github.com/lazypoline/lazypoline/commits/main>
  - <https://github.com/lazypoline/lazypoline/commit/41b88bd16e390bce388695230383ed887927182f>
  - <https://github.com/lazypoline/benchmarks>
  - <https://github.com/lazypoline/benchmarks/tree/main/bench>
  - <https://github.com/lazypoline/benchmarks/tree/main/bench/microbench>
  - <https://raw.githubusercontent.com/lazypoline/benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/lazypoline/benchmarks/HEAD/install.sh>
  - <https://raw.githubusercontent.com/lazypoline/benchmarks/HEAD/bench/bench_micro.sh>
  - <https://raw.githubusercontent.com/lazypoline/benchmarks/HEAD/bench/zpoline.patch>
  - <https://raw.githubusercontent.com/lazypoline/benchmarks/HEAD/bench/plot_micro.py>
  - <https://raw.githubusercontent.com/lazypoline/benchmarks/HEAD/bench/microbench/bench.cpp>
  - <https://raw.githubusercontent.com/lazypoline/benchmarks/HEAD/bench/microbench/bench_config.h>
  - <https://raw.githubusercontent.com/lazypoline/benchmarks/HEAD/bench/microbench/bench_syscall.asm>
  - <https://raw.githubusercontent.com/lazypoline/benchmarks/HEAD/bench/microbench/CMakeLists.txt>
  - <https://raw.githubusercontent.com/lazypoline/benchmarks/HEAD/bench/microbench/mb_config_syscall.h>
  - <https://raw.githubusercontent.com/lazypoline/benchmarks/HEAD/bench/microbench/mb_config_sud_enable.h>
  - <https://raw.githubusercontent.com/lazypoline/benchmarks/HEAD/bench/microbench/mb_config_rax.h>
  - <https://raw.githubusercontent.com/lazypoline/benchmarks/HEAD/bench/microbench/mb_config_sud_disable.h>
  - <https://raw.githubusercontent.com/lazypoline/benchmarks/HEAD/bench/conf/config_sud.h>
  - <https://raw.githubusercontent.com/lazypoline/benchmarks/HEAD/bench/conf/config_rw_zpoline.h>
  - <https://raw.githubusercontent.com/lazypoline/benchmarks/HEAD/bench/conf/config_preserving_xstate.h>
  - <https://raw.githubusercontent.com/lazypoline/secpoline/HEAD/README.md>
  - <https://repository.tudelft.nl/file/File_499bdf55-5322-4e4a-b266-913e73d29d3a>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/lazypoline/lazypoline`) · [data/wave13/enrich/raw/github_com_lazypoline_lazypoline.json](../../../data/wave13/enrich/raw/github_com_lazypoline_lazypoline.json) (enrichment confidence 0.6)

</details>
