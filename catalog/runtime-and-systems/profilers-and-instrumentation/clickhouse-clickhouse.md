# ClickHouse libunwind stack-trace cache (llvm-project fork)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Profilers and instrumentation](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0 (ClickHouse); the libunwind fork is under Apache-2.0 WITH LLVM-exception (not rechecked)` · 🟢 active

> ClickHouse's patched LLVM libunwind with a lock-free per-IP cache of decoded DWARF rules; 4.8-7.3x faster repeated stack traces.

| | |
|---|---|
| **Beats** | LLVM libunwind before the change (stack unwinder used by ClickHouse's sampling profiler) |
| **Claimed result** | Stack trace capture (45 frames, depth 64): 8594 to 1351 ns (6.36x) on x86-64, 22480 to 3093 ns (7.27x) on AArch64. Exception throw/catch at depth 16: 17418 to 3661 ns (4.76x), 41174 to 7091 ns (5.81x). 32 cache-miss call sites: 10219 to 8687 ns (1.18x), 27147 to 24630 ns (1.10x). Profiler-style signal-handler sample at depth 0: 4384 to 3103 ns (1.41x), 6900 to 3796 ns (1.82x). |
| **Workload** | benchmark_stack_trace microbenchmark: repeated stacks, exceptions, cache-missing call sites and profiler-style samples from a signal handler. |
| **Metric** | latency |
| **Hardware** | Ryzen 9 7950X3D (x86-64), Graviton4 (AArch64) |
| **Adoption** | ClickHouse 50.3k stars; used in ClickHouse's StackTrace, exceptions and query profiler |
| **Links** | [repository](https://github.com/ClickHouse/ClickHouse) · [benchmark](https://github.com/ClickHouse/ClickHouse/pull/122834) |

## Verdict

First-party before/after in ClickHouse PR #122834, using Google Benchmark (src/Common/benchmarks/stack_trace.cpp) against the previous LLVM libunwind in the same fork, on a Ryzen 9 7950X3D and a Graviton4. Repeated stacks: 8594 to 1351 ns (x86-64) and 22480 to 3093 ns (AArch64) per 45-frame capture. Throw/catch at depth 16: 4.76x and 5.81x. Cache-miss call sites: 1.18x and 1.10x. Signal-handler samples: 1.41x and 1.82x. The compiler and flags are not stated.

## Use it when

- You already build against LLVM libunwind on Linux x86-64 or AArch64 and capture stack traces on every exception or log event (repeated call stacks: 6.4-7.3x per 45-frame capture).
- Exception-heavy C++ servers where throw/catch cost is dominated by unwinding (4.8-5.8x at depth 16 in the PR's microbenchmark).
- In-process sampling profilers that unwind from a signal handler and need a lock-free, allocation-free unwinder (1.4-1.8x per sample at depth 0).
- Processes that never dlclose code, as in ClickHouse, which stubs dlopen/dlclose.

## Skip it when

- Programs that unload shared objects or JIT and free code: entries are never invalidated, so a reused address can return a stale rule. The PR says a general-purpose unwinder would need dlclose hooks.
- Mostly-unique stacks: with call sites that miss the cache the gain is only 1.10-1.18x.
- macOS, Windows, 32-bit or other architectures: the cache compiles out there (Apple is excluded on purpose because frameworks can unload).
- Toolchains on libgcc's unwinder or nongnu libunwind: it is a patch to the LLVM libunwind sources, not a drop-in library.
- Memory-tight processes: the table adds 0.72 MiB of .bss on x86-64 and 1.12 MiB on AArch64.

## How it is fast

Stock libunwind finds and interprets each frame's FDE twice per step (once for the proc info, once to compute the caller's registers). The fork stores the result in a static, direct-mapped table of 4096 slots keyed by instruction pointer (Fibonacci hashing; return addresses and plain IPs get distinct keys). Each slot is a seqlock: a lookup that races a write misses, and a racing insert is dropped. There are no locks or allocation, so it is safe in signal handlers. A hit copies only the half of the compact rule (saved registers, CFA register and offset) that the caller needs and applies it with a short applyCachedRule path. getReg also short-circuits IP and SP instead of going through the non-inlined getRegister switch.

## Compared with alternatives

Choose it over aw-backtrace when you need full DWARF unwinding (exceptions, code without frame pointers) inside LLVM libunwind rather than a separate frame-pointer backtrace library. aw-backtrace's cache-hit unwind step (about 9-10 ns) is cheaper but covers only backtraces. Unlike Tracy or Perforator, this is not a profiler; it lowers the unwind cost that such profilers and exception handling pay.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond libunwind itself (vendor libunwind/src from ClickHouse/llvm-project; DwarfRuleCache.hpp, edits to UnwindCursor.hpp, DwarfInstructions.hpp, DwarfParser.hpp, config.h) |
| **Minimum toolchain** | not documented (ClickHouse builds with recent Clang; the code uses __atomic builtins and constexpr) |
| **Platforms** | Linux x86-64 and AArch64 (ELF, dl_iterate_phdr); everywhere else the code is byte-identical to the baseline |
| **Thread safety** | Lock-free and signal-safe per the code comments: seqlock slots, racing lookups miss, racing inserts are dropped; the PR reports 8M concurrent captures in testing |
| **Drop-in for the baseline** | partial: same libunwind API and ABI, but you must vendor the patched fork and accept the no-code-unloading assumption |

## Gotchas

- Rules are cached only for FDEs in loaded modules and are never invalidated; the design depends on code never being unloaded.
- Direct-mapped with 4096 slots: a colliding insert overwrites the slot, so deep or very varied stacks thrash it. Rules that need DWARF expressions, or that save more than 12 registers (24 on AArch64), are never cached.
- In the merged code (3807b16), applyCachedRule calls registers.getRegister(rule.returnAddressRegister) without the range check, while the uncached path skips an out-of-range return-address register. A malformed CIE could therefore abort the process (_LIBUNWIND_ABORT 'unsupported x86_64 register') once the rule is cached; an AI reviewer flagged this on PR #122834. It affects only bad unwind info and does not change the measured numbers.
- On AArch64, frames with return-address signing (PAC) or MTE tagging go through the slower expandRule plus applyRule path even on a cache hit.

## Known shortcomings

- The cache is a 4096-slot direct-mapped seqlock table that is never invalidated and assumes no code unloading. The cached path (applyCachedRule, DwarfInstructions.hpp line 297) calls getRegister(returnAddressRegister) without a range check, so a malformed CIE aborts the process; the PR's AI reviewer flagged it and it is still in the merged code. The repo id is the whole ClickHouse monorepo, the code lives in the ClickHouse/llvm-project fork.

## Caveats and trade-offs

This is a before/after of the project's own change to its libunwind fork (contrib/llvm-project submodule, https://github.com/ClickHouse/llvm-project): decoded unwind rules are cached by instruction pointer in a lock-free, signal-safe table on Linux x86-64 and AArch64 only. The large wins apply only to repeated stacks; the cache-miss and profiler-sample rows show 1.1-1.8x. The benchmark code is src/Common/benchmarks/stack_trace.cpp (Google Benchmark); the PR states no compiler or flags. The PR, merged 2026-10-01, also fixes a DW_CFA_remember_state stack overflow on fibers. The baseline is the previous libunwind, not perf, gprof or Valgrind; repo_url is the host repo, since the fork itself was not opened.

Change lives in ClickHouse's vendored fork of llvm-project (contrib/llvm-project); not a standalone library.

## Maintenance

Merged 2026-10-01 into ClickHouse master (26.10) and actively maintained as part of ClickHouse. Reusable only by vendoring the Apache-2.0 WITH LLVM-exception libunwind sources from ClickHouse/llvm-project and keeping its no-unload assumption.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The PR body gives a before/after table for the ClickHouse llvm-project fork's libunwind on a Ryzen 9 7950X3D and Graviton4; the benchmark code is public (src/Common/benchmarks/stack_trace.cpp), but the compiler and flags are not stated in the PR, so the record is first-party tier C.
- **Verifier notes:** PR #122834, 'Fix a libunwind stack overflow on fibers and speed up stack traces', was merged 2026-10-01; the numbers match. Consider a name noting that the code lives in ClickHouse/llvm-project (libunwind) and is reusable only by vendoring the fork.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`, `stars_or_usage`, `license`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/ClickHouse/ClickHouse/pull/122834>
  - <https://github.com/ClickHouse/ClickHouse>
  - <https://raw.githubusercontent.com/ClickHouse/ClickHouse/HEAD/src/Common/benchmarks/stack_trace.cpp>
  - <https://raw.githubusercontent.com/ClickHouse/ClickHouse/HEAD/.gitmodules>
- **Sources the enricher read:**
  - <https://github.com/ClickHouse/ClickHouse/pull/122834>
  - <https://github.com/ClickHouse/ClickHouse/pull/122834/files>
  - <https://github.com/ClickHouse/llvm-project/pull/131>
  - <https://raw.githubusercontent.com/ClickHouse/ClickHouse/HEAD/src/Common/benchmarks/stack_trace.cpp>
  - <https://raw.githubusercontent.com/ClickHouse/ClickHouse/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/ClickHouse/llvm-project/3807b16/libunwind/src/DwarfRuleCache.hpp>
  - <https://raw.githubusercontent.com/ClickHouse/llvm-project/3807b16/libunwind/src/UnwindCursor.hpp>
  - <https://raw.githubusercontent.com/ClickHouse/llvm-project/3807b16/libunwind/src/DwarfInstructions.hpp>
  - <https://raw.githubusercontent.com/ClickHouse/llvm-project/3807b16/libunwind/src/config.h>
  - <https://raw.githubusercontent.com/ClickHouse/llvm-project/3807b16/libunwind/src/Registers.hpp>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/clickhouse/clickhouse`) · [data/wave11/enrich/raw/github_com_clickhouse_clickhouse.json](../../../data/wave11/enrich/raw/github_com_clickhouse_clickhouse.json) (enrichment confidence 0.75)

</details>
