# CRuby RTL + MJIT (vnmakarov/ruby rtl_mjit_branch)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-2-Clause OR Ruby` · 🔴 abandoned

> 2017 CRuby fork with register-based (RTL) bytecode and a method JIT that emits C and runs GCC/Clang; beats MRI 2.0 and 2.5-dev.

| | |
|---|---|
| **Beats** | Ruby MRI 2.0 (primary) and Ruby MRI 2.5-development trunk the branch is based on ('base') |
| **Claimed result** | README 'Update: 15th June, 2017' wall-time speedup over MRI 2.0, geomean of 23 microbenchmarks: mjit (GCC 6.3.1 -O2) 6.18x, mjit-cl (Clang 3.9.1 -O2) 4.02x, rtl without JIT 1.39x, base MRI 2.5-dev 1.12x; against base that is about 5.5x (mjit) and 3.6x (mjit-cl). The 'while' row (387.29x for mjit) is an empty loop whose result is unused; without it the mjit geomean is about 5.1x over MRI 2.0 and 4.5x over base, and on the ten algorithmic benchmarks (fannk through bench) mjit is about 1.93x over MRI 2.0 and 1.74x over base (all derived from page data). Optcarrot 2000 frames: 28.96 FPS MRI 2.0, 39.43 FPS base, 78.22 FPS mjit (2.7x), 90.58 FPS mjit-cl (3.13x); default 180 frames: 82.06 FPS mjit (2.83x), 85.43 FPS mjit-cl (2.94x). Optcarrot against base about 1.98x (mjit) and 2.30x (mjit-cl) at 2000 frames (derived from page data). CPU-time geomean 5.55x (mjit) and 3.67x (mjit-cl) on the microbenchmarks; optcarrot CPU-time speedup only 1.45x to 1.53x. |
| **Workload** | 23 microbenchmarks from MJIT-benchmarks (while, nest-while, ivread, aref, fib, fannk, sieve, mandelbrot, meteor, nbody, norm, trees, pent, red-black, bench, ...) plus the optcarrot NES emulator at 180 and 2000 frames; wall time, CPU time and peak memory, minimum of 3 runs. |
| **Metric** | throughput |
| **Hardware** | Intel 3.9GHz i3-7100, 32GB memory, x86-64 Fedora Core 25 |
| **Compiler and flags** | MJIT-generated C compiled with GCC 6.3.1 -O2 (mjit) or LLVM Clang 3.9.1 -O2 (mjit-cl); build flags of the MRI 2.0 and base interpreters not stated |
| **Adoption** | 206 stars |
| **Last commit** | 2017-09-29 |
| **Links** | [repository](https://github.com/vnmakarov/ruby) · [benchmark](https://github.com/vnmakarov/ruby/blob/rtl_mjit_branch/README.md) |

## Verdict

Author's README (15 June 2017, Intel i3-7100, 32 GB, Fedora 25; minimum of 3 runs via /usr/bin/time, start-up and JIT compile included): over 23 microbenchmarks MJIT with GCC 6.3.1 -O2 has a wall-time geomean of 6.18x MRI 2.0 (Clang 3.9.1 -O2: 4.02x; the 2.5-dev base 1.12x), which is about 1.93x over MRI 2.0 and 1.74x over base on the ten algorithmic programs once the loop-kernel rows are set aside (derived from page data); optcarrot at 2000 frames runs 78.22 FPS (GCC) and 90.58 FPS (Clang) versus 28.96 for MRI 2.0 and 39.43 for base. The compiler and flags used to build the interpreters themselves are not stated.

## Use it when

- Studying or copying the design of a C-compiler-backed method JIT: minimised precompiled header, priority queue of methods, parallel compile workers, deoptimisation back to the interpreter (mjit.c is about 3,100 lines).
- Research comparing register-based and stack-based bytecode in CRuby, using the branch's MJIT-benchmarks scripts (compare.rb, optcarrot-compare.rb) as a starting harness.
- Small, long-running, numeric or loop-heavy Ruby 2.5-era scripts on x86-64 Linux with GCC installed and a spare core for background compilation, where wall time matters more than CPU time or memory.

## Skip it when

- Any production or current Ruby code: the branch is a 2017 prototype on Ruby 2.5-dev, last committed 2017-09-29; use YJIT in mainline CRuby instead.
- Hosts without a C compiler at run time, with a shared or untrusted /tmp, or in sandboxes that forbid exec and dlopen.
- Memory-constrained deployments: peak memory geomean 4.15x (GCC) and 6.44x (Clang) of MRI 2.0 on the microbenchmarks, because the compiler's memory counts.
- Short scripts and code dominated by core-library C methods: each small method takes about 50-70 ms to compile, and fannk (Array#slice!/reverse/insert heavy) gets 1.1x with or without the JIT.
- CPU-time or battery-bound workloads: on optcarrot the CPU-time gain over the 2.5-dev base is only about 1.13x (derived from page data), and on red-black MJIT uses more CPU than MRI 2.0 (0.75x GCC, 0.64x Clang).

## How it is fast

RTL instructions name their operands (plus a, b, c instead of getlocal/getlocal/opt_plus/setlocal), cutting dispatch count and VM-stack traffic, with immediate-operand specialisation, combined compare-and-branch instructions and type-speculative instructions that de-speculate when a guess fails. MJIT translates a hot method's RTL into C, compiles it with gcc -O2 or clang -O2 against a precompiled, script-minimised vm.c header in background worker threads, and dlopen()s the resulting .so from /tmp; speculative code can bail out to the interpreter and be recompiled ('mutated') up to a limit (default 2).

## Compared with alternatives

Pick YJIT (ruby/ruby) for any real Ruby workload: the author's own 2023 successor branch (sir-mirjit, same repo) measured YJIT at 262.1 FPS on optcarrot against 123.1 for his newer MIRJIT, and he declared the project dormant in YJIT's favour; JRuby or TruffleRuby suit long-running servers. Pick this branch only as readable reference code for a GCC/Clang-backed method JIT on top of a register VM, the design whose JIT infrastructure fed Ruby 2.6's MJIT.

## Integration

| | |
|---|---|
| **Form** | source-drop (whole CRuby 2.5-dev fork; build the interpreter from rtl_mjit_branch) |
| **Dependencies** | gcc or clang on PATH at run time (found via execvp), pthreads, dlopen, a writable /tmp; the minimised MJIT header must be in the build dir or installed include dir |
| **Minimum toolchain** | not documented; measured with GCC 6.3.1 and Clang 3.9.1 as the JIT back end |
| **Platforms** | x86-64 Linux (Fedora 25 measured); macOS forced to Clang via a 2017 contributed patch; others not documented |
| **Thread safety** | MJIT compiles in detached worker pthreads under one engine mutex while the Ruby VM runs; open issue #10 reports a crash in a multithreaded Rails benchmark with JIT on |
| **Drop-in for the baseline** | partial — runs ordinary Ruby scripts (JIT via -j), but only Ruby 2.5-dev semantics, MJIT not passing make check, and the README limits it to small simple programs |

## Gotchas

- Harness flaws: compare.rb's 'CPU time' parses only the user field of /usr/bin/time (system time dropped); optcarrot-compare.rb runs each Ruby 2 times, not the 3 the README states, and keeps the best FPS; and on optcarrot MJIT's 2.7x-3.13x wall gain over MRI 2.0 shrinks to about 1.13x CPU time against the 2.5-dev base (derived from page data), so the wall speedup leans on compiling on a second core of the 2-core i3-7100.
- The 'while' row (387.29x, GCC) is a method running an empty counting loop 1,000,000 times, called 2,000 times, with its result discarded; since MRI 2.0 was tuned to take 20-70 s per benchmark, 387x means about 0.05-0.18 s for 2e9 iterations, so GCC -O2 removed or collapsed the loop (Clang gets 9.28x). It alone lifts the 23-benchmark geomean from about 5.1x to 6.18x.
- Security: JIT files use predictable /tmp names (/tmp/&lt;prefix&gt;p&lt;pid&gt;u&lt;id&gt;), the C file is opened with fopen("w") without O_EXCL, GCC is invoked with -I/tmp, and the compiler is looked up through PATH; a local user can plant files or symlinks. The README lists 'MJIT vulnerability' as unaddressed future work.
- Correctness: open issue #10 (Feb 2019, no maintainer reply) reports Rails Ruby Bench on the RTL branch with --jit crashing with NoMethodError "undefined method `setsockopt' for nil:NilClass" in net/http under threads; the same run without JIT works. The RTL interpreter alone is slower than its base on optcarrot (35.76 vs 39.43 FPS).

## Known shortcomings

- Interpreter builds' compiler and flags unstated (only the JIT backend GCC 6.3.1 / Clang 3.9.1 -O2 is given); 2017 prototype, abandoned. The 6.18x geomean is against Ruby 2.0 and the 387x 'while' row is an empty loop GCC removes; about 1.9x on the 10 algorithmic benchmarks and about 2x on optcarrot vs the base branch, optcarrot CPU-time gain 1.45-1.53x.
- Enricher: compare.rb's 'CPU time' parses only the user field of /usr/bin/time; optcarrot-compare.rb runs each Ruby 2 times, not 3, and keeps the best FPS; on optcarrot the 2.7x-3.13x wall gain over MRI 2.0 shrinks to about 1.13x CPU time against the 2.5-dev base (derived from page data), so the wall speedup leans on compiling on the second core of the 2-core i3-7100. The 387.29x 'while' row is an empty counting loop that GCC -O2 collapsed (Clang 9.28x); it alone lifts the 23-benchmark geomean from about 5.1x to 6.18x. Security: JIT files use predictable /tmp names opened without O_EXCL, GCC invoked with -I/tmp and looked up through PATH. Open issue #10: Rails Ruby Bench crashes with --jit under threads. The RTL interpreter alone is slower than its base on optcarrot (35.76 vs 39.43 FPS).

## Caveats and trade-offs

Numbers are from June 2017 on a prototype branch, last commit 2017-09-29; the branch is not maintained. The headline 6.18x is against Ruby 2.0, an old baseline; against the 2.5-development trunk it is about 5.5x. The 'while' microbenchmark (387x for GCC mjit) times an empty while loop inside a method whose result is discarded, which GCC -O2 can remove entirely, so that row measures dead-loop elimination and skews the geomean (about 5.1x over MRI 2.0 without it; about 1.9x on the ten algorithmic benchmarks, derived from page data). Compiler and flags of the MRI 2.0, base and rtl_mjit interpreter builds are not stated (only the JIT's C compiler: GCC 6.3.1 -O2 or Clang 3.9.1 -O2). Optcarrot is the only real-program result: 2.7x to 3.13x over MRI 2.0, about 2x over base, and CPU-time gain only 1.45x to 1.53x. Benchmark scripts are in the branch under MJIT-benchmarks (compare.rb, optcarrot-compare.rb; minimum of 3 runs timed with /usr/bin/time, start-up included). Not the same as the MJIT later shipped in Ruby 2.6 to 3.2 or today's YJIT (ruby/ruby is listed separately for YJIT); vnmakarov/mir is already catalogued and is not duplicated here. License: Ruby's dual licence (BSD-2-Clause or the Ruby terms), per COPYING. [retier] 2017 prototype branch, abandoned 2017-09-29 (successor sir-mirjit dormant since 2023). The 6.18x geomean over Ruby 2.0 (GCC MJIT, 2-core i3-7100) includes a 387x 'while' row that is an empty counting loop GCC -O2 collapsed; about 5.1x without it and about 1.9x on the 10 algorithmic benchmarks against the 2.5-dev base. optcarrot: 2.7x-3.13x wall over MRI 2.0 but about 1.13x CPU time against base (derived from page data), since compilation ran on the second core; compare.rb drops system time. Interpreter build flags unstated; predictable /tmp JIT file names; Rails Ruby Bench crashes with --jit under threads (#10).

Method JIT that generates C code and runs GCC or Clang at runtime, loading the result as a shared object from /tmp; needs a C compiler installed at run time. Compiling a small ISEQ takes about 50-70 ms. Peak memory geomean 4.15x (GCC) and 6.44x (Clang) of MRI 2.0 including the compiler. README says it is at a very early stage and only ready for a few small, simple Ruby programs (June 2017 update).

## Maintenance

rtl_mjit_branch is abandoned (last commit 2017-09-29; the repo's default branch is now the sir-mirjit successor, which the author called dormant in 2023 in favour of YJIT); dual BSD-2-Clause/Ruby licence makes the MJIT design copyable, but the code is a prototype interpreter fork, not something to deploy.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): downgrade; tier before verification A, tier now C.
- **Tier reason:** First-party README tables with public scripts (MJIT-benchmarks/compare.rb, optcarrot-compare.rb and the .rb workloads) and a named CPU (i3-7100), but only the JIT's C backend is specified (GCC 6.3.1 -O2, Clang 3.9.1 -O2); the compiler and flags used to build the MRI 2.0, base and rtl_mjit interpreter binaries themselves are never stated, so not A; no paper or independent run, so C.
- **Verifier notes:** Every number in the record matches the README; downgraded A to C because the interpreter builds' compiler and flags are unstated. Shortcomings: 2017 prototype branch (abandoned), headline geomean against Ruby 2.0 and inflated by the 387x empty 'while' loop that GCC -O2 eliminates (about 1.9x on the algorithmic benchmarks, about 2x on optcarrot vs base); optcarrot CPU-time gain is 1.45x to 1.53x, not 1.49x to 1.53x. Fork of ruby/ruby, 206 stars, last commit 2017-09-29 confirmed; distinct from the listed ruby/ruby (YJIT) entry.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** stated interpreter build flags and a CRuby 3.x comparison; CPU-time comparison against CRuby 3.x with YJIT
- **Pages the verifier opened:**
  - <https://github.com/vnmakarov/ruby/blob/rtl_mjit_branch/README.md>
  - <https://raw.githubusercontent.com/vnmakarov/ruby/rtl_mjit_branch/README.md>
  - <https://github.com/vnmakarov/ruby/tree/rtl_mjit_branch/MJIT-benchmarks>
  - <https://github.com/vnmakarov/ruby/commits/rtl_mjit_branch>
  - <https://raw.githubusercontent.com/vnmakarov/ruby/rtl_mjit_branch/MJIT-benchmarks/while.rb>
  - <https://raw.githubusercontent.com/vnmakarov/ruby/rtl_mjit_branch/MJIT-benchmarks/compare.rb>
  - <https://raw.githubusercontent.com/vnmakarov/ruby/rtl_mjit_branch/COPYING>
- **Sources the enricher read:**
  - <https://github.com/vnmakarov/ruby>
  - <https://raw.githubusercontent.com/vnmakarov/ruby/rtl_mjit_branch/README.md>
  - <https://raw.githubusercontent.com/vnmakarov/ruby/rtl_mjit_branch/MJIT-benchmarks/compare.rb>
  - <https://raw.githubusercontent.com/vnmakarov/ruby/rtl_mjit_branch/MJIT-benchmarks/optcarrot-compare.rb>
  - <https://raw.githubusercontent.com/vnmakarov/ruby/rtl_mjit_branch/MJIT-benchmarks/while.rb>
  - <https://raw.githubusercontent.com/vnmakarov/ruby/rtl_mjit_branch/MJIT-benchmarks/fannk.rb>
  - <https://raw.githubusercontent.com/vnmakarov/ruby/rtl_mjit_branch/mjit.c>
  - <https://raw.githubusercontent.com/vnmakarov/ruby/rtl_mjit_branch/mjit.h>
  - <https://raw.githubusercontent.com/vnmakarov/ruby/sir-mirjit/README.md>
  - <https://github.com/vnmakarov/ruby/commits/rtl_mjit_branch>
  - <https://github.com/vnmakarov/ruby/branches/all>
  - <https://github.com/vnmakarov/ruby/issues?q=is%3Aissue>
  - <https://github.com/vnmakarov/ruby/issues/10>
  - WebSearch snippet: Ruby 2.6 MJIT merge history (developer.squareup.com/blog/rubys-new-jit, ruby/ruby PR #1782, bugs.ruby-lang.org Feature #14235); pages not opened
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/vnmakarov/ruby`) · [data/wave12/enrich/raw/github_com_vnmakarov_ruby.json](../../../data/wave12/enrich/raw/github_com_vnmakarov_ruby.json) (enrichment confidence 0.8)

</details>
