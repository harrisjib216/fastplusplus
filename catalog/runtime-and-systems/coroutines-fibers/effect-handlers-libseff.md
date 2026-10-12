# libseff

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Coroutines and fibers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MulanPSL-2.0` · 🟡 stale

> C library of shallow effect handlers on stackful coroutines; OOPSLA 2024 paper reports about 2x faster generators than Tencent libco.

| | |
|---|---|
| **Beats** | Tencent libco |
| **Claimed result** | Per search snippets of the OOPSLA 2024 paper (PDF blocked): generator benchmark libseff 0.66 us vs libco 1.33 us, about 2x faster than libco and 1.7x faster than cppcoro; libseff consistently fastest among effect-handler libraries. Snippet only. |
| **Workload** | OOPSLA 2024 evaluation of effect-handler implementations and concurrency mechanisms (context switch, skynet, http server benchmarks), including libco and cppcoro. |
| **Metric** | latency |
| **Hardware** | Intel Xeon Gold 6154, Ubuntu 20.04 (from search snippet) |
| **Compiler and flags** | clang 12.0.0 (flags not seen) |
| **Adoption** | 16 stars |
| **Last commit** | 2025-07-09 |
| **Links** | [repository](https://github.com/effect-handlers/libseff) · [benchmark](https://github.com/effect-handlers/libseff/tree/master/bench) |

## Verdict

The claim comes from the peer-reviewed OOPSLA 2024 paper, read only through search snippets: on an Intel Xeon Gold 6154 (Ubuntu 20.04, clang 12) the generator benchmark ran 0.66 us for libseff versus 1.33 us for libco, about 2x, and 1.7x faster than cppcoro. The repo's context-switch harness puts libco on a single shared stack, which adds a stack copy per switch, so the libco gap partly measures that configuration.

## Use it when

- Research or systems code in C that wants exceptions, generators and user-level threads from one effect-handler mechanism
- x86-64 Linux servers with many lightweight tasks where segmented stacks keep per-task memory small
- Comparing effect-handler runtimes: bench/ builds libseff, libco, cppcoro, libhandler, libmprompt and cpp-effects from git submodules side by side
- Generator-heavy code where the paper reports libseff ahead of libco and cppcoro (snippet: 1.7x vs cppcoro, 2x vs libco)

## Skip it when

- Anything except x86-64 Linux with clang: decls/seff_types.py accepts only x86-64, and the code relies on -fsplit-stack, the gold linker and %fs TLS offsets
- Production use that needs maintenance or a community: 16 stars, 35 commits, last commit 2025-07-09
- Hot paths that call small functions inside a coroutine under segmented stacks: the paper notes an empty call can be about 11x slower than a plain C call (hot split)
- Calling libc or other code not built with -fsplit-stack from a coroutine without the provided syscall-wrapper trampolines (MAKE_SYSCALL_WRAPPER), which switch to the system stack
- When a plain fast switch is all you need: minicoro or libaco are simpler and portable

## How it is fast

Handlers are not closures and not a stack that is walked: each coroutine records its handled-effect bitmask and seff_locate_handler finds the target by checking bits up the chain of running coroutines, then a short x86-64 assembly switch (asm/seff.S) jumps to it. Default stacks are segmented (clang -fsplit-stack, with the split-stack limit kept at %fs:0x70) and freed stacklets are kept on a linked list for reuse to soften the hot-split problem; fixed-size and virtual-memory policies are build options.

## Compared with alternatives

Pick libseff over libco, libaco or minicoro only when you want effect handlers (typed effects, handler lookup, exceptions and generators from one primitive) rather than a bare switch; for a plain fast switch libaco and minicoro are more portable and simpler, and libdill or libgo are more mature runtimes.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none at run time; build needs clang-10 (Makefile default), ld.gold and python3 to generate seff_types.h; benchmarks also need the git submodules, libc++, Boost.Context and python2.7 for cppcoro |
| **Minimum toolchain** | clang with -fsplit-stack support (Makefile pins clang-10), C gnu11; benchmark harness C++17/C++20 with libc++ |
| **Platforms** | x86-64 Linux only |
| **Thread safety** | current coroutine is __thread; coroutines can be run by the bundled multi-threaded scheduler, otherwise not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Both the top-level Makefile and bench/common.mk default to BUILD := debug (-O0); pass BUILD=release (-O3 -DNDEBUG, plus -flto=thin for benchmarks) before timing anything
- bench/context_switch_bench/libco.cpp runs both libco coroutines on one shared stack (co_alloc_sharestack(1, 128 KB)), so every alternate resume makes libco free, malloc and memcpy the used stack (save_stack_buffer in libco's co_routine.cpp); this inflates libco's switch cost relative to its private-stack mode, and it grows with the depth and padding arguments
- The README is two lines; usage has to be learned from tests/ and the paper, whose PDF was not reachable from this session
- Mulan PSL v2 license (Huawei copyright headers): OSI-approved and permissive, but less familiar to legal teams than MIT/BSD

## Known shortcomings

- Harness flaw: bench/context_switch_bench/libco.cpp puts libco on one shared stack (co_alloc_sharestack(1,128KB)), so each alternating switch does a free, malloc and memcpy of the stack (save_stack_buffer), which inflates the libco baseline. Makefiles default to BUILD=debug (-O0). x86-64 Linux with clang split-stack and gold only. Paper PDF blocked; numbers are snippet only.

## Caveats and trade-offs

Snippet only: the paper PDF (dl.acm.org, homepages.inf.ed.ac.uk, pure-oai.bham.ac.uk) is blocked here, so numbers vs libco come from search snippets; paper also notes the hot-split problem makes a call to an empty function 11x slower than a plain C call under segmented stacks. bench/ vendors libco, cppcoro, libmprompt, libhandler and cpp-effects as git submodules. Mulan PSL v2 is OSI-approved. Low star count (16). Last commit 2025-07-09, over 12 months ago.

Effect-handler API (shallow handlers) on asymmetric stackful coroutines, segmented stacks, x86-64 focus; C library with its own API, not a drop-in coroutine library.

## Maintenance

Research code, stale since 2025-07-09 with 16 stars; Mulan PSL v2 and small enough to vendor, but tied to x86-64 Linux, clang split-stack and gold.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed OOPSLA 2024 paper (Effect Handlers for C via Coroutines) evaluates libseff against libco and cppcoro; bench/context_switch_bench has libseff.cpp, libco.cpp and cppcoro.cpp, but the paper (with compiler/flags) could only be read via search snippets, so not A.
- **Verifier notes:** Downgrade of maintenance to stale (last commit 2025-07-09 vs today 2026-10). Tier B rests on the peer-reviewed paper; a retier to A is possible if the paper's methodology section (compiler, flags, CPU) becomes reachable.
- **Fields the verifier corrected:** `claimed_speedup`, `maintenance_status`, `caveats`
- **Shortcomings recorded by:** peer-reviewed paper, snippet only
- **Pages the verifier opened:**
  - <https://github.com/effect-handlers/libseff>
  - <https://github.com/effect-handlers/libseff/tree/master/bench>
  - <https://github.com/effect-handlers/libseff/tree/master/bench/context_switch_bench>
  - <https://github.com/effect-handlers/libseff/commits/master>
  - <https://github.com/effect-handlers/libseff/blob/master/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/effect-handlers/libseff>
  - <https://raw.githubusercontent.com/effect-handlers/libseff/HEAD/README.md>
  - <https://raw.githubusercontent.com/effect-handlers/libseff/HEAD/Makefile>
  - <https://github.com/effect-handlers/libseff/tree/master/src>
  - <https://raw.githubusercontent.com/effect-handlers/libseff/HEAD/src/seff.h>
  - <https://raw.githubusercontent.com/effect-handlers/libseff/HEAD/src/seff.c>
  - <https://raw.githubusercontent.com/effect-handlers/libseff/HEAD/decls/seff_types.py>
  - <https://raw.githubusercontent.com/effect-handlers/libseff/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/effect-handlers/libseff/HEAD/bench/common.mk>
  - <https://github.com/effect-handlers/libseff/tree/master/bench/context_switch_bench>
  - <https://raw.githubusercontent.com/effect-handlers/libseff/HEAD/bench/context_switch_bench/Makefile>
  - <https://raw.githubusercontent.com/effect-handlers/libseff/HEAD/bench/context_switch_bench/context_switch_common.hpp>
  - <https://raw.githubusercontent.com/effect-handlers/libseff/HEAD/bench/context_switch_bench/libseff.cpp>
  - <https://raw.githubusercontent.com/effect-handlers/libseff/HEAD/bench/context_switch_bench/libco.cpp>
  - <https://raw.githubusercontent.com/effect-handlers/libseff/HEAD/bench/context_switch_bench/cppcoro.cpp>
  - <https://raw.githubusercontent.com/Tencent/libco/HEAD/co_routine.cpp>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/effect-handlers/libseff`) · [data/wave11/enrich/raw/github_com_effect_handlers_libseff.json](../../../data/wave11/enrich/raw/github_com_effect_handlers_libseff.json) (enrichment confidence 0.55)

</details>
