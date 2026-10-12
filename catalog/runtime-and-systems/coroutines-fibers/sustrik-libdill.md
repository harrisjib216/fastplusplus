# libdill

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Coroutines and fibers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🔴 abandoned

> C structured-concurrency library with stackful coroutines; project numbers show roughly 20x cheaper switches than Go goroutines.

| | |
|---|---|
| **Beats** | Go goroutines (also gccgo) |
| **Claimed result** | Context switch 16 ns (master) / 13 ns (optimized) vs Go 331 ns and gccgo 825 ns on an i7 4770k; create+terminate 44 ns / 25 ns vs Go 237 ns and gccgo 3652 ns. |
| **Workload** | Coroutine context switch and coroutine create/terminate cost, libdill master and an optimized branch vs Go and gccgo. |
| **Metric** | latency |
| **Hardware** | Intel i7 4770k; also Core 2 Duo (libdill only) |
| **Adoption** | 1.9k stars |
| **Last commit** | 2022-08-10 |
| **Links** | [repository](https://github.com/sustrik/libdill) · [benchmark](https://github.com/sustrik/libdill/issues/30) |

## Verdict

Contributor raedwulf's 2016 analysis in issue #30 measured a 16 ns context switch and 44 ns create+terminate on libdill master on an i7 4770k (13 ns and 25 ns on the optimized-limit branch), against Go at 331 ns / 237 ns and gccgo at 825 ns / 3652 ns. On a Core 2 Duo libdill measured 46 / 37 ns per switch and 131 / 100 ns per create. Compiler, flags and Go version are not stated, and the comparison is against Go rather than a C/C++ coroutine library.

## Use it when

- C or C++ network servers on Linux or BSD x86-64 that want goroutine-style code with explicit cancellation and deadlines.
- Workloads with very many short-lived coroutines, where create+terminate cost (44 ns on an i7 4770k per issue #30) matters.
- Ports of Go-style designs to C where you want channels and choose() without a GC runtime.
- Programs that want TLS, WebSocket or HTTP framing built into the coroutine I/O layer rather than added separately.

## Skip it when

- ARM64, especially Apple M1: no assembly switch path, and issue #208 (segfault launching a coroutine on M1 macOS, in ___chkstk_darwin) is open and unanswered.
- Windows: not supported (issue #226). Cygwin (#201) and Android/x86 (#211) builds also fail.
- Multicore scheduling inside one scheduler: each thread has its own context, and coroutines do not migrate across threads.
- Projects that need a maintained dependency: last commit 2022-08-10, 46 open issues including build failures with gcc-13.2.0 (#229) and Fedora 31 (#206), and the libdill.org documentation site is down (#221).
- Code that needs strict ISO C: bundle_wait() is reported incompatible with -std=c99/c11/c90 (#194), and the go() macro relies on GNU statement expressions and inline asm.

## How it is fast

Context switches use inline-assembly setjmp/longjmp macros on x86-64 and i386 that save only callee-saved registers, with no signal mask and no glibc pointer mangling. Other architectures fall back to sigsetjmp(ctx, 0). The go() macro moves the stack pointer onto a heap stack inline (via alloca tricks), so launching a coroutine costs no function-pointer trampoline. Stacks (256 KiB each, plus an mprotect guard page) are cached up to 64 per thread, which keeps mprotect out of the create/terminate path. The scheduler is a run queue over an epoll/kqueue/poll pollset.

## Compared with alternatives

Pick libdill over minicoro, libaco or libco when you want a complete scheduler, structured cancellation and a coroutine-aware socket/TLS stack rather than a bare context-switch primitive. Pick it over its predecessor libmill for the bundle/handle model and per-thread support. Choose minicoro or Boost.Context if you need ARM64 or Windows.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | pthreads (unless --disable-threads); OpenSSL only with --enable-tls |
| **Minimum toolchain** | GCC or Clang with GNU C extensions; autotools build (recent gcc-13.2.0 build failure reported in #229) |
| **Platforms** | x86-64 and i386 with assembly switches; other POSIX via sigsetjmp fallback (aarch64 macOS reported segfaulting); Linux epoll, BSD/macOS kqueue, poll fallback; no Windows |
| **Thread safety** | Per-thread scheduler context (pthread TLS when DILL_THREADS); coroutines and handles are bound to the thread that created them |
| **Drop-in for the baseline** | no |

## Gotchas

- The library is built with -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0, because glibc fortification panics at the go() macro's stack-pointer manipulation. Compiling your own code with fortification can trip the same check.
- Fixed 256 KiB stacks with a guard page; stack overflow faults instead of growing, and very large coroutine counts cost real memory (the whisper benchmark in #30 ran 32k-100k coroutines without guard pages).
- Documentation lives only on libdill.org, which is down (#221); the README just points there, so the header libdill.h is the practical reference.
- The faster 13 ns / 25 ns figures come from the 'optimized-limit' inlining branch, not from master.

## Known shortcomings

- The faster 13/25 ns figures come from the optimized-limit branch, not master. Open bugs: 208 (M1 segfault), 229 (gcc 13.2.0 build failure), 194 (-std=c99 incompatibility). No Windows support; libdill.org is down (issue 221). The library is built with -D_FORTIFY_SOURCE=0 because the go() macro moves the stack pointer. No compiler or flags in the benchmark; abandoned.

## Caveats and trade-offs

Baseline is Go, not Boost.Context/Boost.Coroutine/libco; numbers are from a 2016 performance-analysis issue by contributor raedwulf (project-side, not independent); compiler, flags and Go version not stated; Haswell-era hardware; the 13 ns / 25 ns figures are from an 'optimized-limit' branch, not master. Core 2 Duo figures (46 / 37 ns switch, 131 / 100 ns create) are libdill only. README has no performance section.

C API with structured-concurrency model (bundles, deadlines); not drop-in for Boost.Context or libco; stackful coroutines with its own scheduler and I/O wrappers.

## Maintenance

Abandoned since 2022-08-10 (issue #227 asking whether it is abandoned has no answer) but MIT-licensed; usable on x86-64 Linux if you can fix the build on newer GCC yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** Issue #30 (raedwulf, 2016-10-25) lists libdill 16 / 13 ns context switch and 44 / 25 ns create+terminate vs Go 331 / 237 ns and gccgo 825 / 3652 ns on an i7 4770k; no compiler, flags or Go version stated, project-contributor numbers, so C.
- **Verifier notes:** Numbers match the issue. Last commit 2022-08-10 (over 3 years ago), so abandoned is correct; repo not archived; MIT, 1.9k stars confirmed.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** first-party issue comment
- **Pages the verifier opened:**
  - <https://github.com/sustrik/libdill/issues/30>
  - <https://github.com/sustrik/libdill>
  - <https://github.com/sustrik/libdill/commits>
- **Sources the enricher read:**
  - <https://github.com/sustrik/libdill>
  - <https://raw.githubusercontent.com/sustrik/libdill/HEAD/README.md>
  - <https://raw.githubusercontent.com/sustrik/libdill/HEAD/libdill.h>
  - <https://raw.githubusercontent.com/sustrik/libdill/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/sustrik/libdill/HEAD/Makefile.am>
  - <https://raw.githubusercontent.com/sustrik/libdill/HEAD/ctx.c>
  - <https://raw.githubusercontent.com/sustrik/libdill/HEAD/stack.c>
  - <https://github.com/sustrik/libdill/issues/30>
  - <https://github.com/sustrik/libdill/issues>
  - <https://github.com/sustrik/libdill/issues/208>
  - <https://github.com/sustrik/libdill/issues/217>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/sustrik/libdill`) · [data/wave11/enrich/raw/github_com_sustrik_libdill.json](../../../data/wave11/enrich/raw/github_com_sustrik_libdill.json) (enrichment confidence 0.75)

</details>
