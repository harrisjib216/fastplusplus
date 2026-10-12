# libco (higan-emu)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C (hand-assembled machine-code context switch per CPU)` · `ISC` · 🟡 stale

> C89 stackful coroutine library whose hand-assembled per-CPU switch costs a few function calls, against hundreds for POSIX ucontext.

| | |
|---|---|
| **Beats** | POSIX ucontext context switch (libco's own ucontext.c backend), plus its setjmp/longjmp and Windows-fiber backends, each expressed as a multiple of an ordinary C function call; the README also contrasts kernel-scheduled preemptive threads |
| **Claimed result** | doc/targets.md switch overhead versus an ordinary C function call: libco.amd64 \~6x (\~10x on Windows), libco.x86 \~5x, libco.ppc \~20x, versus libco.fiber (Windows fibers) \~15x, libco.sjlj (setjmp/longjmp) \~30x and libco.ucontext (POSIX ucontext) \~300x; about 50x lower switch overhead for the hand-assembled amd64 backend than the ucontext backend (derived from page data). README: 'libco can easily scale to 10,000,000 or more context switches per second' while applications needing '100,000 or more context switches per second' hit kernel overhead with preemptive threads (assertion, no measurement). |
| **Workload** | Cost of one co_switch between cooperative threads relative to an ordinary C function call, per backend (doc/targets.md); README asserts 10,000,000+ user-space switches per second versus kernel thread switching becoming the bottleneck above 100,000 per second. |
| **Metric** | throughput |
| **Adoption** | 183 stars; README names servers and emulators as ideal use cases |
| **Last commit** | 2024-09-10 |
| **Links** | [repository](https://github.com/higan-emu/libco) · [benchmark](https://github.com/higan-emu/libco/blob/master/doc/targets.md) |

## Verdict

doc/targets.md gives switch overhead as a multiple of an ordinary C function call: amd64 \~6x (\~10x on Windows), x86 \~5x, PowerPC \~20x, Windows fibers \~15x, setjmp/longjmp \~30x and POSIX ucontext \~300x. No hardware, compiler or date is given; the multiples presumably come from the repo's test_timing.cpp, whose call baseline is likely inlined at -O3. The README's 10,000,000+ switches per second is an assertion, and no independent measurement was found.

## Use it when

- Emulators and simulators that interleave several components (CPU cores, video, audio) in one OS thread and switch between them millions of times per second.
- Single-threaded servers or event loops in C or C++ that want stackful coroutines through a tiny, permissively licensed C89 API instead of ucontext.
- Snapshot and restore of coroutine state, for example emulator save states: co_serializable() returns 1 on the hand-assembled backends read here (amd64, arm, aarch64), so copying the co_derive() buffer captures the cothread.
- Portable code that must cover x86, amd64, ARM, AArch64 and PowerPC with one API, falling back to setjmp/longjmp on other POSIX targets or Windows fibers.

## Skip it when

- C++ code that throws exceptions inside cothreads on Windows with the amd64.c or x86.c backend. Issue #45 (open since 2024-08-31) reports terminate() or invalid memory reads; exceptions work on Linux and with fiber.c.
- 32-bit ARM hard-float code that keeps floating-point values live across co_switch: arm.c saves only r4-r11, sp and lr, not the AAPCS callee-saved VFP registers d8-d15 (found by reading the code; no issue filed).
- When you need guard pages, growable stacks, overflow detection, entry-function arguments (closure support was closed as wontfix, issue #16) or moving cothreads between OS threads.
- Multithreaded programs that do not define LIBCO_MP: without it thread_local expands to nothing and the active-cothread state is a plain process global.
- RISC-V and other CPUs without a backend (they fall back to sjlj, issue #44 open). Also avoid it in hardened builds: the machine-code arrays have no ENDBR64 and no shadow-stack handling, an inference that matters if CET/IBT is enforced.

## How it is fast

Each CPU backend is a few dozen bytes of hand-assembled machine code stored as a const array (co_swap_function) in the text section, or made executable with mprotect/VirtualProtect. It saves only callee-saved state and jumps to the target: rsp, rbp, rbx and r12-r15 on SysV amd64 (plus xmm6-15 on Win64); x19-x30, sp and d8-d15 on AArch64. The swap is entered through an ordinary call and leaves with 'pop rax; jmp rax', so a switch costs about as much as a call plus a handful of loads and stores. Compared with glibc swapcontext, it skips the signal-mask system call. It also does not save the MXCSR/x87 control words or switch any OS thread-block fields, which is part of why it is cheap.

## Compared with alternatives

Against the Boost.Context sibling (fcontext 9 ns / 19 cycles vs 547 ns for ucontext on its own published harness), pick libco when you want a four-call C89 API, an ISC licence, a small vendorable source set (libco.c, settings.h, one backend file and the bundled valgrind.h) and serializable cothread state. Pick Boost.Context when you need measured numbers, C++ exceptions inside coroutines on Windows, or 32-bit ARM hard-float code.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (C library malloc/free/assert, overridable through LIBCO_MALLOC, LIBCO_FREE and LIBCO_ASSERT; bundled valgrind.h header) |
| **Minimum toolchain** | C89; CI builds with GCC -std=c89 on Linux, -m32 for x86, qemu for armv7/aarch64/ppc64le/ppc, and MSVC (cl /Zc:__STDC__) for Windows amd64/x86 |
| **Platforms** | x86 and amd64 (Windows, macOS, Linux, BSD), 32-bit ARM, AArch64, 32/64-bit PowerPC ELFv1 and ppc64le ELFv2; other POSIX targets via sjlj.c, Windows via fiber.c; ucontext.c is never picked by libco.c and must be compiled directly |
| **Thread safety** | Not thread-safe by default; define LIBCO_MP to make the active-cothread state thread_local. usage.md warns not to switch a non-cothread context across CPU cores. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind the overhead multiples: doc/examples/test_timing.cpp, the only timing code in the repo, prints a 'co_switch skew' ratio. Its 'subroutine call' baseline is a one-line function in the same file built at -O3 (build.sh, CI), so GCC and Clang will normally inline it (not built here to confirm). The denominator is then a loop of volatile increments, not a call. Each co_switch iteration performs two switches (there and back). The printed labels say '50 million' and '100 million' calls while Iterations is 500,000,000. No output is recorded, and the workflow page shows 0 runs today.
- ABI state not saved: ARM32 skips VFP d8-d15, and SysV amd64 skips the callee-saved MXCSR and x87 control-word bits, so a rounding-mode change in one cothread leaks into others. On Win64, LIBCO_NO_SSE clobbers xmm6-15 against the ABI (issue #43). Windows amd64/x86 backends break C++ exception handling (issue #45).
- The register save area sits at the bottom of the same malloc'd block that the stack grows down into. With no guard page, an overflow silently corrupts the saved context; issue #13's Windows crash in fflush was a too-small stack.
- Backend quirks: sjlj.c needs -D_FORTIFY_SOURCE=0 (CI sets it; glibc's checked longjmp rejects cross-stack jumps), swaps the process-wide SIGUSR1 handler while creating a cothread, and fails valgrind with an unexplained invalid write. Under LIBCO_MPROTECT, which Clang builds force on, the mprotect/VirtualProtect return value is ignored.

## Known shortcomings

- Numbers are rough multiples in doc/targets.md (amd64 about 6x a C call vs ucontext about 300x, about 50x derived) with no code or methodology; machine-code bytes are placed in the text section.
- Harness flaw: doc/examples/test_timing.cpp, the only timing code in the repo, uses a same-file one-line 'subroutine call' baseline built at -O3 that compilers normally inline, so the denominator behind the '\~6x' multiples is likely a loop of volatile increments, not a call; each co_switch iteration is two switches; labels say 50M/100M calls while Iterations is 500,000,000; no output is recorded. ABI bugs: arm.c skips VFP d8-d15 (AAPCS callee-saved, armhf corruption), SysV amd64 skips MXCSR and x87 control word, Windows asm backends break C++ exceptions (issue #45), sjlj needs -D_FORTIFY_SOURCE=0.

## Caveats and trade-offs

The overhead figures are rough first-party multiples ('\~6x', '\~300x') with no benchmark code, methodology, compiler, hardware or date in the repo; the 10,000,000 switches per second README figure is an assertion. The ucontext backend's cost is dominated by the signal-mask system call glibc swapcontext makes, so the gap mostly reflects avoiding that call. Not compared against Boost.Context fcontext, minicoro or other user-space switchers. The amd64/x86 backends store the switch routine as hand-assembled machine-code bytes in a const array placed in the text section (or made executable with mprotect/VirtualProtect under LIBCO_MPROTECT), which hardened toolchains or W^X policies may object to. valgrind.h is under a BSD-style license; the rest is ISC. Last commit 2024-09-10. [retier] The overhead figures are rough first-party multiples ('\~6x', '\~300x') with no methodology, compiler, hardware or date in the repo; the 10,000,000 switches per second README figure is an assertion. The only timing code, doc/examples/test_timing.cpp, prints a 'co_switch skew' ratio whose 'subroutine call' baseline is a one-line function in the same file built at -O3, which GCC and Clang normally inline, so the denominator is probably a loop of volatile increments rather than a call; each iteration performs two switches; the printed labels say 50 and 100 million calls while Iterations is 500,000,000; no output is recorded. The ucontext backend's cost is dominated by the signal-mask system call glibc swapcontext makes. Not compared against Boost.Context fcontext, minicoro or other user-space switchers. ABI state not saved: ARM32 skips VFP d8-d15 (AAPCS callee-saved, armhf corruption), SysV amd64 skips the callee-saved MXCSR and x87 control-word bits, Win64 LIBCO_NO_SSE clobbers xmm6-15 (issue #43), and the Windows amd64/x86 backends break C++ exception handling (issue #45). The register save area sits at the bottom of the same malloc'd block the stack grows into, with no guard page. sjlj.c needs -D_FORTIFY_SOURCE=0 and swaps the process-wide SIGUSR1 handler during creation. The amd64/x86 backends store the switch routine as machine-code bytes in a const array (mprotect/VirtualProtect under LIBCO_MPROTECT, return value ignored), which W^X policies may object to. valgrind.h is BSD-style; the rest is ISC. Last commit 2024-09-10.

Four-function C89 API (co_active, co_create, co_delete, co_switch); backends for x86, amd64, PowerPC, PowerPC64 ELFv1/ELFv2, ARM, AArch64, plus setjmp, ucontext and Windows fiber fallbacks. No safety checks by design. Single-core cooperative scheduling only. The amd64 backend writes the switch routine as a byte array of machine code (co_swap_function) made executable at runtime.

## Maintenance

Stale since 2024-09-10 (CI and C89 fixes), with 6 open issues including Windows exceptions and RISC-V. It is ISC-licensed and small enough to vendor (libco.c plus one backend file), but treat the ARM32 VFP and Windows exception gaps as blockers for those targets.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** doc/targets.md gives first-party switch-overhead multiples relative to a plain C function call (amd64 \~6x, x86 \~5x, ucontext \~300x, sjlj \~30x, Windows fibers \~15x) with no benchmark code, compiler, flags or hardware; the README's 10,000,000 switches per second is an assertion. Numbers without methodology are C.
- **Verifier notes:** Found real (if rough) numbers in doc/targets.md that the search record missed; benchmark_url and claimed_speedup corrected, tier stays C. Main shortcomings: no benchmark code or methodology, multiples only, baseline cost dominated by swapcontext's system call. Not already listed (wave 11 has minicoro and libcopp, not libco; Tencent/libco is a different project of the same name).
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `workload`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-106 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/higan-emu/libco>
  - <https://github.com/higan-emu/libco/commits/master>
  - <https://github.com/higan-emu/libco/blob/master/doc/targets.md>
  - <https://raw.githubusercontent.com/higan-emu/libco/HEAD/README.md>
  - <https://raw.githubusercontent.com/higan-emu/libco/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/higan-emu/libco/HEAD/doc/targets.md>
  - <https://raw.githubusercontent.com/higan-emu/libco/HEAD/doc/usage.md>
  - <https://raw.githubusercontent.com/higan-emu/libco/HEAD/amd64.c>
  - <https://raw.githubusercontent.com/higan-emu/libco/HEAD/settings.h>
- **Sources the enricher read:**
  - <https://github.com/higan-emu/libco>
  - <https://github.com/higan-emu/libco/commits/master>
  - <https://github.com/higan-emu/libco/issues?q=is%3Aissue>
  - <https://github.com/higan-emu/libco/issues/13>
  - <https://github.com/higan-emu/libco/issues/32>
  - <https://github.com/higan-emu/libco/issues/43>
  - <https://github.com/higan-emu/libco/issues/45>
  - <https://github.com/higan-emu/libco/issues/51>
  - <https://github.com/higan-emu/libco/pulls?q=is%3Apr>
  - <https://github.com/higan-emu/libco/tree/master/doc>
  - <https://github.com/higan-emu/libco/tree/master/doc/examples>
  - <https://github.com/higan-emu/libco/tree/master/.github/workflows>
  - <https://github.com/higan-emu/libco/actions/workflows/ci.yml>
  - <https://raw.githubusercontent.com/higan-emu/libco/HEAD/README.md>
  - <https://raw.githubusercontent.com/higan-emu/libco/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/higan-emu/libco/HEAD/doc/targets.md>
  - <https://raw.githubusercontent.com/higan-emu/libco/HEAD/doc/usage.md>
  - <https://raw.githubusercontent.com/higan-emu/libco/HEAD/libco.h>
  - <https://raw.githubusercontent.com/higan-emu/libco/HEAD/libco.c>
  - <https://raw.githubusercontent.com/higan-emu/libco/HEAD/settings.h>
  - <https://raw.githubusercontent.com/higan-emu/libco/HEAD/amd64.c>
  - <https://raw.githubusercontent.com/higan-emu/libco/HEAD/x86.c>
  - <https://raw.githubusercontent.com/higan-emu/libco/HEAD/arm.c>
  - <https://raw.githubusercontent.com/higan-emu/libco/HEAD/aarch64.c>
  - <https://raw.githubusercontent.com/higan-emu/libco/HEAD/ppc.c>
  - <https://raw.githubusercontent.com/higan-emu/libco/HEAD/ppc64v2.c>
  - <https://raw.githubusercontent.com/higan-emu/libco/HEAD/sjlj.c>
  - <https://raw.githubusercontent.com/higan-emu/libco/HEAD/ucontext.c>
  - <https://raw.githubusercontent.com/higan-emu/libco/HEAD/fiber.c>
  - <https://raw.githubusercontent.com/higan-emu/libco/HEAD/doc/examples/test_timing.cpp>
  - <https://raw.githubusercontent.com/higan-emu/libco/HEAD/doc/examples/test.h>
  - <https://raw.githubusercontent.com/higan-emu/libco/HEAD/doc/examples/build.sh>
  - <https://raw.githubusercontent.com/higan-emu/libco/HEAD/doc/examples/build.bat>
  - <https://raw.githubusercontent.com/higan-emu/libco/HEAD/.github/workflows/ci.yml>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/higan-emu/libco`) · [data/wave13/enrich/raw/github_com_higan_emu_libco.json](../../../data/wave13/enrich/raw/github_com_higan_emu_libco.json) (enrichment confidence 0.65)

</details>
