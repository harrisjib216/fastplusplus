# libaco

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Coroutines and fibers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0` · 🔴 abandoned

> Small C asymmetric-coroutine library for x86/x86-64 whose hand-written switch routine runs about 1.7x faster than Tencent libco's coctx_swap.

| | |
|---|---|
| **Beats** | Tencent libco (coctx_swap) |
| **Claimed result** | acosw 1.72x faster than Tencent libco's coctx_swap (author's claim): coctx_swap measured at 17.64 ns/op per switch in the benchmark branch (test_libco_benchmark) versus acosw 10.29 ns/op in the main README benchmark (standalone stack, shared FPU/MXCSR); 17.64/10.29 = 1.71x (derived from page data). |
| **Workload** | Pure context switch cost, acosw versus libco's coctx_swap, 20 million resume calls (40 million switches) on x86_64. |
| **Metric** | latency |
| **Hardware** | AWS c5d.large virtual machine, RHEL-7.5, 2018-06-30 (exact CPU model not stated) |
| **Compiler and flags** | -DACO_CONFIG_SHARE_FPU_MXCSR_ENV, tcmalloc_minimal; README example builds with gcc -g -O2 |
| **Adoption** | 3.7k stars |
| **Last commit** | 2022-05-21 |
| **Links** | [repository](https://github.com/hnes/libaco) · [benchmark](https://github.com/hnes/libaco/tree/tencent_libco_bug_report_and_coctx_swap_benchmark) |

## Verdict

On one AWS c5d.large VM (RHEL 7.5, June 2018, CPU model not stated, gcc -g -O2 per make.sh, tcmalloc preloaded, shared FPU/MXCSR), acosw measured 10.29 ns per switch (20.59 ns per resume round trip, 40M switches), against 17.64 ns for libco's coctx_swap swapped into the same harness in the benchmark branch; that is 1.72x per the author (1.71x derived from page data). First-party, and only the switch routine was compared.

## Use it when

- Single-threaded event loops or generators in C on Linux x86-64 or i386, where you write your own scheduler and want switch cost around 10 ns.
- Millions of mostly idle coroutines with small stacks at yield points: the README runs 10,000,000 cos with a 120 B copy-stack in 2.8 GB under tcmalloc.
- Replacing libco's coctx_swap in an existing design, where its ABI violation (stack pointer addressing heap memory, unsafe under signals) is a concern.
- Code that needs a small, readable implementation (about 700 LOC) that is easy to vendor and audit.

## Skip it when

- ARM, aarch64, Windows/MSVC or any non-Sys-V target: only i386 and x86-64 Sys V are supported (issues #20, #57 and #6 are open).
- Shared-stack cos that yield with deep stacks: resume cost grows with copied bytes (33 ns at 8 B, 211 ns at 1000 B, 1090 ns at 7992 B in the README table).
- Needing symmetric transfer, return values from yield, a scheduler, I/O integration or per-co TLS: none are provided (issues #47, #22 and #46 open).
- Long-lived projects that need upstream fixes: the last release is v1.2.4 (July 2018), there are 27 open issues and the last commit was 2022.

## How it is fast

acosw.S is a minimal assembly switch that saves and restores only the Sys V ABI callee-saved registers, the stack pointer and the return address, plus, unless ACO_CONFIG_SHARE_FPU_MXCSR_ENV is defined, the x87 control word and MXCSR (fnstcw/stmxcsr). It jumps to the saved return address instead of using push/ret tricks, and unlike libco's coctx_swap it never points the stack pointer at heap memory. For shared-stack cos, aco.c copies only the live stack bytes with an inline aligned short-copy path on amd64 and falls back to memcpy for larger frames (copy-stack design).

## Compared with alternatives

Pick libaco over libco or libcopp when you want only a correct, minimal x86 switch plus copy-stacks in plain C; pick minicoro for a single-header library that also runs on ARM, Windows and WebAssembly, and libgo or libfiber when you need a scheduler with hooked I/O.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (optional valgrind headers for ACO_USE_VALGRIND; tcmalloc used only in benchmarks) |
| **Minimum toolchain** | GCC or Clang with GNU assembler (Intel syntax .S); builds with -std=c99; make.sh uses gcc -g -O2 -Wall -Werror |
| **Platforms** | Linux x86-64 and i386 (Sys V ABI) only |
| **Thread safety** | One libaco instance per thread via __thread globals (aco_thread_init per thread); no data shared across threads, and cos must not migrate between threads |
| **Drop-in for the baseline** | no |

## Gotchas

- Pointers to locals on a shared stack are invalid from another co sharing that stack; the README says to heap-allocate anything passed between cos.
- Defining ACO_CONFIG_SHARE_FPU_MXCSR_ENV (the 10.29 ns configuration) is only correct if no code changes the FPU or MXCSR control words; without it every co keeps its own copy (10.38 ns).
- A co that returns from its function instead of calling aco_exit triggers the protector, which aborts the process; errors call abort() rather than returning codes (issue #41).
- Valgrind memcheck reports false positives with shared stacks; build with ACO_USE_VALGRIND or ACO_USE_ASAN when debugging, and not in release builds. The README warns to build from releases, not master.

## Known shortcomings

- The 1.72x figure compares only the switch routine. x86 and i386 System V only (ARM issues 20 and 57 are open). Shared-stack resume cost grows with the copied bytes: 33 ns at 8 B, 1090 ns at 7992 B. Last release v1.2.4, July 2018.

## Caveats and trade-offs

The 17.64 ns/op figure is libco's coctx_swap, not acosw; acosw is 10.29 ns/op. Numbers from 2018 on an AWS c5d.large VM with no CPU model; build flags for the benchmark binaries not fully stated (README shows gcc -g -O2 builds; -DACO_CONFIG_SHARE_FPU_MXCSR_ENV and tcmalloc_minimal via LD_PRELOAD). Compares only the switch routine against libco, not Boost.Context. Last commit 2022-05-21 (merge of PR #54). First-party.

Asymmetric coroutines only, x86_64 and i386 Sys V ABI plus limited others; C API; no scheduler; shared-stack mode copies stack contents, which slows switches as copied size grows.

## Maintenance

Abandoned: v1.2.4 dates from July 2018 and the last commit is a 2022 merge, but it is Apache-2.0, about 700 LOC and easy to vendor for x86 Linux.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** Benchmark branch README states acosw is 1.72x faster than libco's coctx_swap and shows the run with coctx_swap substituted (17.64 ns/op per switch); main README shows acosw at 10.29 ns/op, same AWS c5d.large / RHEL-7.5 setup. Benchmark code public but CPU model and exact flags of the benchmark build not stated; first-party, so C.
- **Verifier notes:** Record mislabelled 17.64 ns as acosw's time; corrected. License Apache-2.0 confirmed from LICENSE; 3.7k stars.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/hnes/libaco/tree/tencent_libco_bug_report_and_coctx_swap_benchmark>
  - <https://raw.githubusercontent.com/hnes/libaco/tencent_libco_bug_report_and_coctx_swap_benchmark/README.md>
  - <https://raw.githubusercontent.com/hnes/libaco/HEAD/README.md>
  - <https://raw.githubusercontent.com/hnes/libaco/HEAD/LICENSE>
  - <https://github.com/hnes/libaco/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/hnes/libaco/HEAD/README.md>
  - <https://raw.githubusercontent.com/hnes/libaco/HEAD/aco.h>
  - <https://raw.githubusercontent.com/hnes/libaco/HEAD/aco.c>
  - <https://raw.githubusercontent.com/hnes/libaco/HEAD/acosw.S>
  - <https://raw.githubusercontent.com/hnes/libaco/HEAD/make.sh>
  - <https://raw.githubusercontent.com/hnes/libaco/tencent_libco_bug_report_and_coctx_swap_benchmark/README.md>
  - <https://github.com/hnes/libaco/issues>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/hnes/libaco`) · [data/wave11/enrich/raw/github_com_hnes_libaco.json](../../../data/wave11/enrich/raw/github_com_hnes_libaco.json) (enrichment confidence 0.8)

</details>
