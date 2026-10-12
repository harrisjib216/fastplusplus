# newLISP Neo

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `GPL-3.0` · 🟢 active

> newLISP 10.7.6 rebuilt with a computed-goto bytecode VM, tail calls and a nursery GC; beats CPython 3.14 on fib(30).

| | |
|---|---|
| **Beats** | CPython 3.14.4 and CPython 3.12.3 (also original newLISP 10.7.6 tree-walker, the project it derives from) |
| **Claimed result** | fib(30): newLISP Neo 42.6 ms vs CPython 3.14.4 86.0 ms (2.02x faster), CPython 3.12.3 186.9 ms, original newLISP 592.5 ms (13.9x faster than original); 1M-iteration while loop 31.3 ms vs CPython 3.14.4 37.2 ms (1.19x faster); tail-recursive 1M loop 17.3 ms (2.15x faster than CPython 3.14.4's while loop); 100M-step self-tail-recursion runs in 1,023 ms where CPython raises RecursionError. |
| **Workload** | Recursive fib(30), a 1-million-iteration loop (while and tail-recursive forms), and deep tail-recursion tests; wall time in ms for the newLISP Neo script versus the equivalent bench.py. |
| **Metric** | latency |
| **Hardware** | 'a Windows x86_64 host' (CPU not stated) |
| **Compiler and flags** | make.bat builds makefile_mingw64_utf8: gcc -m64 -Wall -O3 -fno-strict-aliasing -DNEWLISP64 -DWINDOWS -DSUPPORT_UTF8 (Linux makefile_linuxLP64_utf8: gcc -O3 -g); the README does not say which build or GCC version produced the timings, nor how the original newLISP 10.7.6 and the two CPython builds were obtained |
| **Adoption** | 16 stars, 2 forks; 20 commits |
| **Last commit** | 2026-09-17 |
| **Links** | [repository](https://github.com/kimtg/newlisp-neo) · [benchmark](https://github.com/kimtg/newlisp-neo) |

## Verdict

One in-process timing per script on an unnamed Windows x86-64 machine (no repeats, GCC version not stated; Windows makefile is gcc -O3): fib(30) 42.6 ms vs 86.0 ms on CPython 3.14.4 (2.02x) and 592.5 ms on newLISP 10.7.6, and a 1M-iteration while loop 31.3 ms vs 37.2 ms (1.19x). The 17.3 ms tail-recursive row compares a different program with CPython's while loop, and the TCO rows have no baseline because CPython and newLISP 10.7.6 overflow.

## Use it when

- You already run newLISP scripts and their hot paths are small integer-recursive or counting-loop functions over parameters and let/local variables (fib(30) 42.6 ms vs 592.5 ms on newLISP 10.7.6).
- Deep self- or mutual tail recursion that overflows the stack on newLISP 10.7.6 (README: 100M self-tail steps in 1,023 ms, 10M mutual steps in 167 ms).
- Single-process scripting on Windows x86-64 (MinGW-w64), the only platform the numbers come from.
- Experiments or teaching on a small, readable bytecode VM bolted onto an existing Lisp interpreter.

## Skip it when

- Code that relies on newLISP's dynamic scoping: compiled functions keep parameters and let/local variables in VM stack slots, so callees, eval-string or spawn/sync that read or set those names see the global symbol instead (open issue #4: the qa-cilk spawn/sync fibo test fails).
- Programs that allocate millions of cells inside one primitive call or mutate long-lived lists heavily: by code reading the moving nursery has no write barrier and no roots for C-local pointers (see gotchas); not stress-tested by anything in the repo.
- Memory-constrained or embedded deployments: a fixed 64 MB nursery is allocated at startup, against newLISP's traditional small footprint.
- As a Python replacement: different language, and the only comparisons are fib(30) and a 1M-iteration counting loop.
- Production use generally: the VM and GC landed 2026-09-05 to 2026-09-17 from one author, 16 stars, two open issues without replies.

## How it is fast

Direct-threaded dispatch with GCC/Clang computed gotos, specialised opcodes (LOAD_LOCAL_0..3, CONST_0..2, ADD_1, SUB_1, SUB_2) and an unboxed-integer fast path for + - \* / on two longs. Parameters and let/local variables live in flat VM stack slots instead of being bound to symbols, self-recursion becomes OP_CALL_SELF without a symbol lookup or C recursion, and tail calls reuse the frame (OP_TAIL_CALL_SELF, OP_TAIL_CALL). All cells come from a 64 MB bump-pointer nursery that is copied (Cheney-style) into the old newLISP cell pool when it fills.

## Compared with alternatives

Pick it only if you already have newLISP code and want it faster; for a new embedded Lisp-like language Janet is more mature and MIT-licensed, and for Python-syntax scripting pocketpy (MIT) or CPython 3.14 itself avoid the semantic and GC risks above.

## Integration

| | |
|---|---|
| **Form** | standalone interpreter executable built with make (static C sources, bundled PCRE) |
| **Dependencies** | libm, libdl and readline on Linux (makefile_linuxLP64_utf8); ws2_32 on Windows; bundled pcre.c |
| **Minimum toolchain** | GCC or Clang (GNU C extensions: computed goto, __builtin_expect used unguarded in newlisp.h); MinGW-w64 on Windows |
| **Platforms** | Windows x86-64 (MinGW, benchmarked), Linux LP64, macOS and BSD makefiles (macOS and Linux makefiles were missing nl-vm.o until issues #1 and #2, closed 2026-09-07) |
| **Thread safety** | Single-threaded; VM stack, frame stack and nursery are process-global. newLISP concurrency is process-based (spawn/fork), and spawn inside compiled functions is broken per issue #4. |
| **Drop-in for the baseline** | false — different language from CPython; partial for newLISP 10.7.6 scripts (qa-dot passes per the README, but qa-cilk fails per issues #2 and #4) |

## Gotchas

- Dynamic-scope break (code reading of compileLambda and OP_CALL in nl-vm.c): parameters and let/local bindings are compiled to stack slots and never written to the symbol, so (define (f x) (g)) (define (g) x) makes g see the global x, and primitives the blacklist misses that evaluate their arguments lazily (spawn has flag 0 in primes.h) get eagerly evaluated arguments; issue #4 shows the qa-cilk test failing with 'ERR: value expected in function set : nil called from user function (fibo 5)'.
- GC soundness (code reading, not run): collectGen0 roots are only the symbol trees, env/result/lambda stacks and the VM stack; gcEvacuate returns at the first tenured cell without a remembered set, so a fresh nursery cell linked into a tenured list by p_push is not moved, and p_sequence builds its list in C locals while stuffInteger may trigger a collection, so (sequence 1 3000000), longer than the 2M-cell nursery, looks exposed to overwritten cells.
- Errors raised inside compiled code (for example ERR_MATH on integer division by zero) longjmp out of executeBytecode without resetting vm_sp or vm_frame_count; nothing in newlisp.c restores them.
- Recursion in a compiled body is bound to the lambda at compile time (OP_CALL_SELF), so redefining the function's symbol later does not change already-compiled recursive calls; part of why fib(30) is fast, since CPython looks up the global fib on each call.

## Known shortcomings

- bench_\*.lsp and bench.py are public with -O3 makefile flags, but no CPU or GCC version, single-run timings, and the tail-call rows have no baseline time. Derived from newLISP 10.7.6; off-baseline (CPython 3.14 only).
- Enricher (code reading): compiled lambdas keep parameters and let/local values in VM stack slots and never bind the symbols, so callees and eval-string see globals, breaking newLISP's dynamic scoping (matches open issue #4: qa-cilk fibo fails with 'value expected in function set: nil'), contradicting the '100% backward compatibility' claim; the isSpecialForm blacklist misses spawn. The moving 64 MB nursery GC has no write barrier and C locals are not roots (p_sequence builds its list in C locals), and vm_sp and frames are not reset after errors. Bench numbers are single runs on an unnamed CPU.

## Caveats and trade-offs

First-party micro-benchmarks (fib(30), a 1M-iteration counting loop, tail calls) on one unnamed Windows x86_64 machine; each script times a single run in-process (newLISP (time ...) or time-of-day, Python time.perf_counter after a small warmup), no repeats or variance. The 17.3 ms 'tail-recursive loop' row compares a different program shape against CPython's while loop, and the TCO table (100M self-tail steps in 1,023 ms, 10M mutual steps in 167 ms) has no baseline time because CPython raises RecursionError. The CPython 3.12.3 to 3.14.4 gap on fib(30) (186.9 ms vs 86.0 ms, 2.17x) is larger than usual, which suggests differently built interpreters; their provenance is not stated. All VM work landed 2026-09-05 to 2026-09-17 (earliest commit 2024-10-19 is the upstream import); constructs the bytecode VM cannot compile fall back to the original tree-walker. GPL-3.0 (documentation GFDL). Forks irr/newlisp-spark and irr/newlisp-neo-fork were not opened.

Direct-threaded bytecode VM with automatic fallback to the classic tree-walking evaluator for dynamic-binding and metaprogramming code; generational GC with a 64 MB nursery; keeps the newLISP language (Lisp-like, not Python) and its GPL-3.0 licence; README says all 396 primitives pass the qa-dot suite.

## Maintenance

Active one-author fork (VM and GC added 2026-09-05 to 2026-09-17, last commit 2026-09-17, two open issues without replies), GPL-3.0; experimental, and the dynamic-scope and GC concerns above make it unsuitable for existing newLISP code without testing.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** README tables give fib(30) and 1M-loop times against CPython 3.14.4, CPython 3.12.3 and original newLISP 10.7.6, with public benchmark code (bench_fib.lsp, bench_loop.lsp, bench_tco.lsp, bench.py) and -O3 flags in the makefiles, but the CPU (only 'a Windows x86_64 host') and GCC version are not stated, so not A; first-party, so C.
- **Verifier notes:** All README numbers match the record (fib 42.6 vs 86.0 ms = 2.02x, loop 31.3 vs 37.2 ms = 1.19x, TCO loop 17.3 ms). Benchmark sources checked: both sides print the result, so no dead-code issue; single-run timings and the unstated CPU keep it at C. Added -O3 build flags from the makefiles and the newLISP 10.7.6 derivation; 16 stars, 2 forks, 20 commits, last commit 2026-09-17, GPL-3.0 confirmed.
- **Fields the verifier corrected:** `compiler_and_flags`, `is_fork_of`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/kimtg/newlisp-neo>
  - <https://github.com/kimtg/newlisp-neo/commits>
  - <https://raw.githubusercontent.com/kimtg/newlisp-neo/HEAD/README.md>
  - <https://raw.githubusercontent.com/kimtg/newlisp-neo/HEAD/bench.py>
  - <https://raw.githubusercontent.com/kimtg/newlisp-neo/HEAD/bench_fib.lsp>
  - <https://raw.githubusercontent.com/kimtg/newlisp-neo/HEAD/bench_loop.lsp>
  - <https://raw.githubusercontent.com/kimtg/newlisp-neo/HEAD/bench_tco.lsp>
  - <https://raw.githubusercontent.com/kimtg/newlisp-neo/HEAD/makefile_mingw64_utf8>
  - <https://raw.githubusercontent.com/kimtg/newlisp-neo/HEAD/makefile_linuxLP64_utf8>
  - <https://raw.githubusercontent.com/kimtg/newlisp-neo/HEAD/make.bat>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/kimtg/newlisp-neo/HEAD/README.md>
  - <https://raw.githubusercontent.com/kimtg/newlisp-neo/HEAD/bench.py>
  - <https://raw.githubusercontent.com/kimtg/newlisp-neo/HEAD/bench_fib.lsp>
  - <https://raw.githubusercontent.com/kimtg/newlisp-neo/HEAD/bench_loop.lsp>
  - <https://raw.githubusercontent.com/kimtg/newlisp-neo/HEAD/bench_tco.lsp>
  - <https://raw.githubusercontent.com/kimtg/newlisp-neo/HEAD/makefile_linuxLP64_utf8>
  - <https://raw.githubusercontent.com/kimtg/newlisp-neo/HEAD/makefile_mingw64_utf8>
  - <https://raw.githubusercontent.com/kimtg/newlisp-neo/HEAD/make.bat>
  - <https://raw.githubusercontent.com/kimtg/newlisp-neo/HEAD/doc/ARCHITECTURE.md>
  - <https://raw.githubusercontent.com/kimtg/newlisp-neo/HEAD/doc/CHANGES.txt>
  - <https://raw.githubusercontent.com/kimtg/newlisp-neo/HEAD/nl-vm.c>
  - <https://raw.githubusercontent.com/kimtg/newlisp-neo/HEAD/nl-vm.h>
  - <https://raw.githubusercontent.com/kimtg/newlisp-neo/HEAD/newlisp.h>
  - <https://raw.githubusercontent.com/kimtg/newlisp-neo/HEAD/newlisp.c>
  - <https://raw.githubusercontent.com/kimtg/newlisp-neo/HEAD/nl-list.c>
  - <https://raw.githubusercontent.com/kimtg/newlisp-neo/HEAD/nl-liststr.c>
  - <https://raw.githubusercontent.com/kimtg/newlisp-neo/HEAD/nl-symbol.c>
  - <https://raw.githubusercontent.com/kimtg/newlisp-neo/HEAD/nl-math.c>
  - <https://raw.githubusercontent.com/kimtg/newlisp-neo/HEAD/primes.h>
  - <https://raw.githubusercontent.com/kimtg/newlisp-neo/HEAD/qa-specific-tests/qa-cilk>
  - <https://github.com/kimtg/newlisp-neo/issues?q=is%3Aissue>
  - <https://github.com/kimtg/newlisp-neo/issues/4>
  - <https://github.com/kimtg/newlisp-neo/issues/2>
  - <https://github.com/kimtg/newlisp-neo/commits>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/kimtg/newlisp-neo`) · [data/wave12/enrich/raw/github_com_kimtg_newlisp_neo.json](../../../data/wave12/enrich/raw/github_com_kimtg_newlisp_neo.json) (enrichment confidence 0.6)

</details>
