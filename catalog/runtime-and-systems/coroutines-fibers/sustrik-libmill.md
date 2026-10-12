# libmill

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Coroutines and fibers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🔴 abandoned

> Go-style coroutines and channels for C; in a third-party switch shootout it beats libco and sometimes Boost.Context.

| | |
|---|---|
| **Beats** | Boost.Context (boost) and libco in the same shootout |
| **Claimed result** | benchbox switch test, 2 coroutines: LinuxMint x86_64 VM libmill 145 ms vs boost 199 ms vs libco 687 ms (derived from page data: about 1.4x vs boost, 4.7x vs libco); macOS x86_64 libmill 525 ms vs boost 728 ms (libco not run); ArchLinux i386 VM libmill 689 ms vs boost 485 ms vs libco 774 ms (slower than boost). 1000 coroutines: libmill slower than boost on LinuxMint (1014 vs 894 ms) and ArchLinux (2031 vs 1021 ms), faster on macOS (1405 vs 1949 ms); faster than libco on both Linux runs (1014 vs 2288 ms, 2031 vs 3328 ms). tbox is fastest in every row. |
| **Workload** | Same benchbox switch test: 10,000,000 switches between 2 coroutines. |
| **Metric** | throughput |
| **Hardware** | macOS x86_64, ArchLinux i386 in VirtualBox, LinuxMint x86_64 in VirtualBox; CPU model not stated |
| **Adoption** | 3.2k stars |
| **Last commit** | 2021-02-09 |
| **Links** | [repository](https://github.com/sustrik/libmill) · [benchmark](https://github.com/tboox/benchbox/wiki/switch) |

## Verdict

In tboox/benchbox's switch test (10M switches), with 2 coroutines libmill took 145 ms vs boost 199 ms and libco 687 ms on a LinuxMint x86-64 VM, and 525 vs 728 ms against boost on macOS x86-64. It lost to boost on an ArchLinux i386 VM (689 vs 485 ms) and in both 1000-coroutine Linux runs, while staying ahead of libco. Compiler, flags and CPU model are not stated.

## Use it when

- Single-threaded x86-64 C programs, such as small network daemons, written in Go-style CSP with channels and choose.
- Cases where a ping-pong between two coroutines dominates; on LinuxMint x86-64 it switched faster than boost and libco in benchbox.
- Existing libmill codebases that work and do not need threads or the libdill bundle model.

## Skip it when

- New projects: libdill supersedes it, the last commit was 2021-02-09, and issue #196 asks for deprecation in favour of libdill.
- Many concurrent coroutines: in the 1000-coroutine benchbox runs it was slower than boost on both Linux VMs (1014 vs 894 ms, 2031 vs 1021 ms), and tbox beat it in every row.
- 32-bit x86: on ArchLinux i386 it was slower than boost (689 vs 485 ms for 2 coroutines), since the assembly path is x86-64 only.
- Multithreaded schedulers: there is no thread support; parallelism is via mfork processes.
- Modern toolchains without patching: open reports include a dns.h build failure (#188), C99 'implicit declaration of asm' (#187), GCC 6.2.1 breakage (#167), an osx segfault (#189) and a tcpconnect timeout socket leak (#181).

## How it is fast

On x86-64 the switch is an inline-assembly setjmp/longjmp pair that saves callee-saved registers plus rdi/rsi, with no signal mask. The go() macro relocates the stack pointer onto a heap stack inside the caller's frame with a VLA filler, so a launch costs no trampoline call. goprepare() preallocates and caches stacks (default about 256 KiB) to keep allocation out of the hot path. Other architectures fall back to sigsetjmp/siglongjmp.

## Compared with alternatives

Rarely: prefer libdill (same author, structured cancellation, per-thread contexts), or tbox, which beat libmill in every benchbox row. libmill makes sense only when you want the literal Go API surface in single-threaded C, or are already using it.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | none; OpenSSL with --enable-ssl |
| **Minimum toolchain** | GCC or Clang with GNU C extensions (statement expressions, inline asm); autotools build |
| **Platforms** | x86-64 assembly switch; other POSIX via sigsetjmp fallback; epoll on Linux, kqueue on BSD/macOS, poll fallback; no Windows |
| **Thread safety** | Not thread-safe; one global scheduler per process (mfork for multi-process) |
| **Drop-in for the baseline** | no |

## Gotchas

- Coroutine functions must be marked 'coroutine' (noinline), and the go() argument is evaluated on the new stack, so complex expressions in go(...) run inside the coroutine.
- The x86-64 asm macros must list ymm registers as clobbered when __AVX__ is defined. Code compiled with and without AVX in one program relies on that conditional.
- Its documentation was on libmill.org, which is parked (#195); the README carries no API docs or performance numbers.
- The repo publishes no benchmarks; the only numbers come from the tbox author's benchbox wiki, run in VMs with no compiler flags or CPU model.

## Known shortcomings

- Slower than Boost on i386 and at 1000 coroutines, and tbox wins every row of the benchbox switch table. Deprecation request 196 is unanswered; open bugs 188, 187 and 181. Single-threaded only; no compiler or flags in the benchmark; abandoned.

## Caveats and trade-offs

Results against boost are mixed: win in 2-coroutine runs on LinuxMint and macOS, loss on ArchLinux i386 and at 1000 coroutines on both Linux VMs; consistently faster than libco. tbox beats it in every row. Benchmark run by the tbox author, no flags or CPU model. Repo claims no performance numbers itself. Last commit 2021-02-09.

Go-style concurrency API in C (goroutines, channels); coroutines use setjmp/longjmp style switching; superseded by libdill by the same author.

## Maintenance

Abandoned since 2021-02-09 and effectively superseded by libdill; MIT-licensed and small enough to vendor, but expect to patch build errors on current GCC/Clang.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** Third-party shootout by the competing tbox author in VMs and on macOS with no compiler, flags or CPU model; libmill itself publishes no numbers, so C.
- **Verifier notes:** LinuxMint numbers in the record are correct, but the other two platforms on the same page show mixed results against boost; claim rewritten to cover all rows. Last commit 2021-02-09 from github.com commits page.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`, `last_commit`, `maintenance_status`
- **Shortcomings recorded by:** first-party benchmark page
- **Pages the verifier opened:**
  - <https://github.com/tboox/benchbox/wiki/switch>
  - <https://github.com/sustrik/libmill>
  - <https://github.com/sustrik/libmill/commits>
- **Sources the enricher read:**
  - <https://github.com/sustrik/libmill>
  - <https://raw.githubusercontent.com/sustrik/libmill/HEAD/README.md>
  - <https://raw.githubusercontent.com/sustrik/libmill/HEAD/libmill.h>
  - <https://raw.githubusercontent.com/sustrik/libmill/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/sustrik/libmill/HEAD/Makefile.am>
  - <https://raw.githubusercontent.com/sustrik/libmill/HEAD/cr.c>
  - <https://raw.githubusercontent.com/sustrik/libmill/HEAD/stack.c>
  - <https://github.com/tboox/benchbox/wiki/switch>
  - <https://github.com/sustrik/libmill/issues>
  - <https://github.com/sustrik/libmill/issues/179>
  - <https://github.com/sustrik/libmill/issues/196>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/sustrik/libmill`) · [data/wave11/enrich/raw/github_com_sustrik_libmill.json](../../../data/wave11/enrich/raw/github_com_sustrik_libmill.json) (enrichment confidence 0.75)

</details>
