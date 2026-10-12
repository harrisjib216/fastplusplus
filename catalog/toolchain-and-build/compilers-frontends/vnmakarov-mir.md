# MIR / c2m (C2MIR)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Compilers and front ends](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Lightweight JIT toolkit whose C11 front-end (c2m) compiles a header-free C function \~80x faster than gcc -O2.

| | |
|---|---|
| **Beats** | GCC |
| **Claimed result** | c2m -eg compiles in 336us vs gcc -O2 in 27.1ms (\~80x) and gcc -O0 in 26.1ms (\~77x); c2m-generated code then runs at about 92% of gcc -O2 speed on the same benchmark |
| **Workload** | Compiling a single C function (Eratosthenes sieve, no #include headers) via the c2m JIT front-end vs gcc -O2/-O0, with gcc run against an in-memory filesystem to remove disk I/O |
| **Metric** | compile-time |
| **Hardware** | Intel i5-13600K, 64GB RAM, Fedora 37 |
| **Compiler and flags** | GCC 12.3.1 -O2 and -O0 (gcc run on a memory filesystem); c2m -O2 -eg (generator) and c2m -ei (interpreter) |
| **Adoption** | 2.6k stars |
| **Last commit** | 2026-06-19 |
| **Links** | [repository](https://github.com/vnmakarov/mir) · [benchmark](https://github.com/vnmakarov/mir/blob/master/README.md) |

## Verdict

On an Intel i5-13600K (Fedora 37, GCC 12.3.1), c2m -eg compiled a single header-free C function (Eratosthenes sieve) in 336us vs gcc -O2's 27.1ms (\~80x) and gcc -O0's 26.1ms (\~77x, with gcc reading source from an in-memory filesystem to remove disk I/O); the resulting c2m-generated machine code then ran at \~92% of gcc -O2 speed on that same sieve and \~91% geomean (0.96 average) across 15 small C benchmarks from the repo's own suite.

## Use it when

- Embedding a C-based JIT inside an interpreter or dynamic-language runtime (the README's own target: CRuby/MRuby-style hot-path specialization)
- Latency-sensitive compile paths where a single small function needs microsecond-scale turnaround rather than a whole translation unit
- Lazy or basic-block-level code generation (-el/-eb) to defer codegen cost until a function or block is actually executed
- Targeting x86-64, aarch64 (including Apple Silicon), ppc64le, s390x, or riscv64 on Linux/macOS and willing to vendor a small (\~55K LOC), MIT-licensed compiler
- Compiling small, self-contained C programs (no large #include trees) from the command line without installing GCC

## Skip it when

- Code needs VLAs, `_Complex`, `_Atomic`, or `_Thread_local` -- c2m's C11 subset omits them (c2mir/README.md lists them as unimplemented; issue #394 is an open request for `_Thread_local`)
- Large, multi-file, header-heavy production builds -- the quoted \~80x is a single function with no #include files on an in-memory gcc run; a real build sees a much smaller gap per the record's own tradeoffs note
- You need GDB-quality source-level debug info for compiled/JITted code -- still an open feature request (#442, opened Jul 2026)
- Untrusted or adversarial C input -- several open heap-buffer-overflow/segfault issues in the parser and preprocessor (#353, #360, #362, #364, #365, #366) mean the front-end isn't hardened
- You need generated code to match or beat gcc -O2 at runtime -- c2m -eg trades that away, running at \~91% geomean / \~92% on sieve of gcc -O2 speed

## How it is fast

c2m uses a hand-written 4-pass pipeline (PEG-based recursive-descent parser, no yacc/flex, then context checking, then MIR generation) instead of a heavyweight preprocessor/parser/optimizer stack. MIR-generator itself runs only a short, deliberately minimal optimization pipeline (SSA built via Braun's algorithm, global value numbering, copy/dead-store/dead-code elimination, and a priority-based linear-scan register allocator with aggressive coalescing) instead of GCC's full middle end, keeping per-function compile overhead in the hundreds-of-microseconds range.

## Compared with alternatives

Pick MIR/c2m over TinyCC when you need an embeddable JIT library (interpret-or-generate, lazy per-function/per-block codegen, MIR IR you can also build directly via API) rather than just a fast standalone `cc`; TinyCC's \~9x-over-gcc number is for a traditional whole-program compile-and-link and doesn't offer c2m's lazy JIT interfaces. Neither zapcc (a caching Clang wrapper for incremental full C++ builds) nor cg_clif (a Rust/Cranelift backend) is a real alternative here -- both target different languages and build workflows entirely.

## Integration

| | |
|---|---|
| **Form** | static lib + shared lib + source-drop (also builds a standalone `c2m` compiler binary) |
| **Dependencies** | none to build (self-contained, builds with system gcc/clang); programs it compiles link libc/libm at runtime |
| **Minimum toolchain** | C11/gnu11 to build MIR itself (GCC or Clang); c2m implements a C11 subset (no VLA/_Complex/_Atomic/_Thread_local) plus some GNU extensions |
| **Platforms** | x86-64, aarch64 (incl. Apple Silicon), ppc64le, s390x, riscv64 on Linux; x86-64/aarch64 macOS; Windows (MinGW/MSVC) is built by GNUmakefile though the README disclaimer only warranties the Linux/OSX/ppc64le/s390x/riscv64 CI-tested platforms |
| **Thread safety** | MIR.md: 'You can use MIR functions in different threads without any synchronization if they work with different contexts in each thread' -- sharing one MIR_context across threads is not documented as safe |
| **Drop-in for the baseline** | partial -- c2m is a working CLI C compiler with gcc-like flags (-E/-c/-S/-o), but it's a C11 subset intended for embedding a JIT, not a certified full-standard drop-in replacement for building arbitrary existing GCC-targeted projects |

## Gotchas

- No `_Thread_local`, `_Atomic`, VLA, or `_Complex` support in c2m (c2mir/README.md; issue #394 open)
- Thread safety is per-MIR_context: separate contexts per thread need no synchronization, but sharing one context across threads isn't documented as safe
- Using C as the JIT input (instead of building MIR IR directly via the API) can slow compilation up to 2x, per README
- Multiple segfault/heap-buffer-overflow issues remain open in the parser/preprocessor path (e.g. #360, #362, #364, #365, #366), so malformed C input isn't guaranteed to fail safely

## Caveats and trade-offs

Project's own README table (first-party). The headline baseline is gcc -O2 (80x); the gcc -O0 column (77x) is extra context, and for compile time -O0 is gcc's fastest setting, so the -O0 cap does not drive the tier. What keeps it at C is that the gcc compile timing is not scripted in the repo. The workload is one tiny function with no #include files, and gcc runs on a memory filesystem. That is a best case for a minimal front-end and not typical of multi-file, header-heavy C builds. On the same table, c2m-generated code runs at about 92% of gcc -O2 speed on sieve (1.74s vs 1.6s) and at 0.91 geomean over 15 c-benchmarks.

c2m targets lightweight JIT use cases: a short optimization pipeline, partial C11 + GCC-extension coverage, and no full preprocessor handling of complex real-world header trees in the quoted benchmark; general-purpose builds would see a smaller gap than the single-function test implies

## Maintenance

Actively maintained -- commits and issue activity continue through Sep 2026 (last commit 2026-06-19, new issues as recent as #475 on 2026-09-03); MIT-licensed and small (\~55K LOC per README) enough to vendor, with 'copyable' usability meaning a source/library integration rather than a packaged install.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification C, tier now C.
- **Tier reason:** README 'Current C2MIR Performance Data' table states i5-13600K, FC37, GCC 12.3.1 and shows c2m -O2 -eg compile 336us vs gcc -O2 27.1ms (80x) and gcc -O0 26.1ms (77x). The sieve source (sieve.c) and a c2m-only timing target (GNUmakefile c2mir-sieve-bench) are public, but no script times the gcc side of the compile comparison (c-benchmarks/run-benchmarks.sh times execution only), so it falls short of A. First-party numbers with partial methodology = C.
- **Verifier notes:** Numbers match the page exactly. The tier stays C, but the record's caveat wrongly said the -O0 column caps it; I rewrote that caveat. Metadata checked: MIT, 2658 stars, last commit 2026-06-19, not a fork, not archived.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/vnmakarov/mir>
  - <https://github.com/vnmakarov/mir/blob/master/README.md>
  - <https://github.com/vnmakarov/mir/tree/master>
  - <https://github.com/vnmakarov/mir/blob/master/GNUmakefile>
  - <https://github.com/vnmakarov/mir/blob/master/c-benchmarks/run-benchmarks.sh>
- **Sources the enricher read:**
  - <https://github.com/vnmakarov/mir>
  - <https://github.com/vnmakarov/mir/blob/master/README.md>
  - <https://github.com/vnmakarov/mir/tree/master>
  - <https://github.com/vnmakarov/mir/blob/master/INSTALL.md>
  - <https://github.com/vnmakarov/mir/blob/master/c2mir/README.md>
  - <https://github.com/vnmakarov/mir/blob/master/GNUmakefile>
  - <https://github.com/vnmakarov/mir/blob/master/MIR.md>
  - <https://github.com/vnmakarov/mir/issues>
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/vnmakarov/mir`) · [data/wave2/enrich/raw/github_com_vnmakarov_mir.json](../../../data/wave2/enrich/raw/github_com_vnmakarov_mir.json) (enrichment confidence 0.6)

</details>
