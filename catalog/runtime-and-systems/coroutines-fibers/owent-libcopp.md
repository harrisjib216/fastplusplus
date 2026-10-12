# libcopp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Coroutines and fibers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT and BSL-1.0` · 🟢 active

> Cross-platform stackful coroutine library (with C++20 coroutine helpers) that switches up to about 1.65x faster than Tencent libco at 30,000 coroutines.

| | |
|---|---|
| **Beats** | Tencent libco |
| **Claimed result** | Switch overhead: libcopp 77 / 105 / 273 ns versus libco static stack pool 84 / 168 / 450 ns (1 / 1,000 / 30,000 coroutines); versus libco 4K shared stack 83 / 529 / 1,073 ns. Gap is about 1.1x at 1 coroutine and about 1.65x at 30,000 (ratios derived from page data). |
| **Workload** | Coroutine switch overhead in ns with 1, 1,000 and 30,000 live coroutines (64 KB stacks for the high-count tests). |
| **Metric** | latency |
| **Adoption** | 866 stars |
| **Last commit** | 2026-09-15 |
| **Links** | [repository](https://github.com/owent/libcopp) · [benchmark](https://gist.github.com/owent/1842b56ac1edd5a7db54590d41af1c44) |

## Verdict

A 2019-09-29 gist by the libcopp maintainer reports average switch costs of 77 / 105 / 273 ns for libcopp at 1 / 1,000 / 30,000 coroutines versus 84 / 168 / 450 ns for libco with a static stack pool and 83 / 529 / 1,073 ns for libco with a 4K shared stack; the libcopp rows used 2 MB stacks while libco used 64 KB, and the libcopp-with-dynamic-stack-pool row at 64 KB (74 / 110 / 270 ns) shows the win holds at equal stack size. No CPU, compiler or flags are given, and the numbers predate the current v2 code.

## Use it when

- Game or RPC servers with thousands to tens of thousands of live stackful coroutines where switch cost at scale matters (273 ns vs libco's 450 ns at 30,000 in the maintainer's gist).
- High churn of short-lived coroutines, if you enable the stack pool: create cost drops to 101-222 ns against about 4 us for libco and plain libcopp.
- Cross-platform code that must run on Linux, Windows (MSVC, MinGW), macOS and non-x86 targets (arm64, RISC-V, PowerPC, MIPS, s390x, LoongArch assembly provided).
- Codebases migrating from stackful to C++20 coroutines that want one library covering both, with C++20 promises awaiting cotask::task.

## Skip it when

- You can use C++20 stackless coroutines directly: the same gist measures them at 5-9 ns per switch (Clang), an order of magnitude below libcopp.
- Single-pair ping-pong switching latency is the only metric: the gap to libco is 77 vs 84 ns, and libgo measured 30 ns in the same table; minicoro and libaco report lower raw switch costs in their own benchmarks.
- You want libco-style transparent hooking of blocking syscalls (read, connect, sleep) so existing synchronous code becomes asynchronous; libcopp has no hooks or built-in scheduler/event loop.
- Memory-tight deployments using the defaults: plain libcopp rows used 2 MB stacks, so 30,000 coroutines reserve tens of GB of address space unless you configure smaller stacks or the pool.
- You need a header-only drop-in: it is a compiled CMake library (copp and cotask) with assembly sources.

## How it is fast

Context switches use hand-written jump_fcontext/make_fcontext/ontop_fcontext assembly copied from Boost.Context (Oliver Kowalke, BSL-1.0), which saves only callee-saved registers plus the FP control words instead of the full signal-mask save that ucontext does. Each coroutine keeps its own stack, so switching never copies stack memory, unlike libco's shared-stack mode whose cost grows with stack contents (529 ns at 1,000 coroutines for a 4K shared stack). A stack pool allocator amortizes the mmap cost of creation (101 ns vs 4.1 us per create at 1,000 coroutines).

## Compared with alternatives

Pick libcopp over libco or libaco when you want per-coroutine stacks with a pool, a task layer and C++20 interop on many platforms including Windows; pick libaco or minicoro for the smallest raw switch in a tiny C library, libgo if you want a full scheduler with syscall hooks, and Boost.Cobalt or plain C++20 coroutines when stackless is acceptable.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none (gtest or Boost.Test optional for tests); masm needed on Windows |
| **Minimum toolchain** | C++11, CMake 3.16+; C++20 coroutine features need GCC 10+, Clang 14+ (13 with -fcoroutines-ts), MSVC 1932+ |
| **Platforms** | Linux, Windows (MSVC, MinGW), macOS; x86, x86-64, arm, arm64, RISC-V64, MIPS, PowerPC, s390x, LoongArch64, SPARC64 fcontext assembly |
| **Thread safety** | Built multi-thread aware by default (LIBCOPP_ENABLE_MULTI_THREAD=YES); a thread-unsafe build is offered and tested in CI. A coroutine should not be resumed concurrently from two threads (not documented in detail). |
| **Drop-in for the baseline** | no |

## Gotchas

- Builds with -fstack-protector need LIBCOPP_MACRO_TLS_STACK_PROTECTOR=ON because, per the README, it changes the default context-switching logic.
- Intel TSX use in fcontext (LIBCOPP_FCONTEXT_USE_TSX) defaults to ON; TSX is disabled by microcode on many recent Intel CPUs, so expect no benefit there.
- Unhandled exceptions inside a coroutine are caught and rethrown when the coroutine is resumed back to the caller; SetUnhandledExceptionFilter only works with the Windows fiber context.
- Major-version upgrades renamed types (stack_allocator_t to stack_allocator_type, coroutine_t to coroutine_type, libcopp::util to copp::util) and require value_type in task macros, so 1.x code does not compile unchanged.

## Known shortcomings

- The gist rows use 2 MB stacks against libco's 64 KB, but the dynamic-stack-pool row at 64 KB (74/110/270 ns) still beats libco (84/168/450 ns). The gist is from 2019, before the v2 code, with no CPU, compiler or flags; the C++20 stackless path (5-9 ns) is far faster. The fcontext asm is copied from Boost.Context (BSL-1.0).

## Caveats and trade-offs

Numbers are from a 2019 gist by the maintainer; hardware, compiler version and flags not stated on the gist (the -O2 in the original record could not be confirmed). Create cost is not a win: libcopp 4.1 us / 3.8 us vs libco 3.9 us / 4.2 us at 1K / 30K (only the dynamic-stack-pool variant, 101 ns / 222 ns, beats libco on create). libgo is faster at 1 coroutine (30 ns) and 30K (150 ns) switch, and C++20 stackless coroutines are far faster (5-9 ns). No Boost.Context or Boost.Coroutine rows. The README says current benchmarks run in GitHub Actions CI, which was not opened.

Stackful and C++20 stackless modes, stack pools, optional Intel TSX; uses Boost.Context-style assembly switching on supported platforms. Heavier API than a bare switch library.

## Maintenance

Actively maintained (last commit 2026-09-15, 866 stars, CI on Linux, Windows, MinGW and macOS, packaged in vcpkg); MIT for libcopp code and BSL-1.0 for the vendored Boost.Context assembly, so it is copyable with attribution.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** Maintainer's 2019-09-29 gist has a table with libcopp 77 / 105 / 273 ns switch vs libco static stack pool 84 / 168 / 450 ns and libco 4K shared stack 83 / 529 / 1073 ns; first-party, no CPU model, compiler version or flags stated, so C.
- **Verifier notes:** Gist numbers match the record exactly; repo metadata (866 stars, MIT and BSL-1.0, last commit 2026-09-15) confirmed via github.com pages since gh api is blocked here.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** first-party gist
- **Pages the verifier opened:**
  - <https://gist.github.com/owent/1842b56ac1edd5a7db54590d41af1c44>
  - <https://github.com/owent/libcopp>
  - <https://github.com/owent/libcopp/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/owent/libcopp/HEAD/README.md>
  - <https://gist.github.com/owent/1842b56ac1edd5a7db54590d41af1c44>
  - <https://github.com/owent/libcopp/tree/v2>
  - <https://github.com/owent/libcopp/tree/v2/src/libcopp>
  - <https://github.com/owent/libcopp/tree/v2/include/libcopp>
  - <https://github.com/owent/libcopp/tree/v2/src/libcopp/fcontext/asm>
  - <https://github.com/owent/libcopp/tree/v2/include/libcopp/stack/allocator>
  - <https://raw.githubusercontent.com/owent/libcopp/v2/src/libcopp/fcontext/asm/jump_x86_64_sysv_elf_gas.S>
  - <https://raw.githubusercontent.com/owent/libcopp/v2/LICENSE>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/owent/libcopp`) · [data/wave11/enrich/raw/github_com_owent_libcopp.json](../../../data/wave11/enrich/raw/github_com_owent_libcopp.json) (enrichment confidence 0.75)

</details>
