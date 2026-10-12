# Janet

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🟢 active

> Embeddable Lisp-family scripting language in one C99 file; roughly CPython speed, ahead only on interpreter-bound object and float code.

| | |
|---|---|
| **Beats** | CPython |
| **Claimed result** | Mixed, not an across-the-board win. README FAQ (qualitative only): programs 'tend to be a bit faster than they would be in a language like Python', VM 'about the same speed as most interpreted languages without a JIT compiler', 'YMMV'. Independent run (MikeBeller/janet-benchmarksgame, Janet 1.14.1 vs Python 3.8, user+sys seconds): Janet faster on binarytrees 71.63 vs 110.94 s (1.55x), knucleotide 137.59 vs 164.44 s (1.20x), nbody 17.53 vs 37.77 s (2.15x); slower on fannkuch 5.04 vs 4.83 s, reverse-complement 35.78 vs 7.37 s (4.9x slower), pidigits 5.98 vs 3.92 s, regexredux 15.86 vs 13.51 s. Geometric mean over the seven: Janet about 1.12x slower than CPython (derived from page data). Lua 5.4 beat Janet on fannkuch, knucleotide, nbody and reverse-complement. |
| **Workload** | Computer Language Benchmarks Game programs, single-threaded idiomatic versions: fannkuch n=10, binarytrees depth 21, knucleotide on a 25M-line input, nbody 5,000,000 steps, reverse-complement on a 100M input, pidigits 10000 digits (Python uses built-in big ints), regexredux on a 5M input. Timed by runbench.janet as user+system CPU seconds from /usr/bin/time, one run each; only the exit code is checked, not the output. |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-7500 @ 3.40GHz, 4 cores, hyperthreading disabled |
| **Compiler and flags** | Janet 1.14.1 built with CFLAGS='-fPIC -O2 -flto' (C compiler not named); Python 3.8 from Anaconda (prebuilt binary); Lua 5.4. |
| **Adoption** | 4.4k stars; single-file amalgamation (janet.c + janet.h) for embedding in C and C++ |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/janet-lang/janet) · [benchmark](https://github.com/MikeBeller/janet-benchmarksgame/blob/master/benchmark_runs/summary.ipynb) |

## Verdict

The project publishes no numbers; its README FAQ says only 'a bit faster' than Python and 'YMMV'. The one independent run (MikeBeller/janet-benchmarksgame, 2021, Intel Core i5-7500 with hyperthreading off, single run, user+sys CPU seconds) timed Janet 1.14.1 built with -O2 -flto (C compiler unnamed) against Anaconda CPython 3.8. Janet was faster on binarytrees (1.55x), knucleotide (1.20x) and nbody (2.15x) and slower on fannkuch (1.04x), reverse-complement (4.9x), pidigits (1.53x) and regexredux (1.17x), about 1.12x slower by geometric mean (derived from page data).

## Use it when

- Embedding a scripting or configuration layer in a C or C++ application, where one MIT-licensed C99 file is easier to vendor than CPython.
- Interpreter-bound scripts that build many small trees or tuples, or do scalar float loops (binarytrees 1.55x and nbody 2.15x faster than CPython 3.8 in the only independent run).
- Text parsing that fits a PEG grammar better than a regex, using the built-in PEG engine.
- Scripts that need networking, subprocesses or OS threads from the core library without third-party packages.

## Skip it when

- As a speed upgrade over Python in general: the independent run has Janet about 1.12x slower than CPython 3.8 by geometric mean, and current CPython 3.11+ releases are faster than 3.8.
- Byte-string, regex or big-integer heavy work: it lost reverse-complement 4.9x, pidigits 1.5x and regexredux 1.2x to CPython's C-implemented builtins, and the core has no regex engine or bignum type.
- When raw interpreter speed decides: Lua 5.4 beat it on 4 of 5 shared benchmarks (about 1.43x geomean, derived from page data), and LuaJIT is far faster.
- Latency-sensitive hosts with large heaps: the stop-the-world GC has no incremental mode yet (issue #1844 is open).
- C++ hosts that rely on destructors during error propagation: Janet uses setjmp/longjmp for non-local returns.

## How it is fast

Janet compiles source to a compact register-based bytecode. On GCC and Clang the VM dispatches it with computed gotos (a switch elsewhere). Values are NaN-boxed into 8 bytes on x86-64, arm64 and riscv64, so numbers, nil and booleans need no heap allocation. The language discourages hash-table-heavy object orientation, which is the README's own explanation for any edge over Python. There is no JIT, and the GC is a simple stop-the-world collector.

## Compared with alternatives

Pick Janet over Wren or pocketpy when you want a larger standard library (PEG, event loop, networking, threads, FFI) in one embeddable C file and can accept CPython-class speed. Wren has the stronger measured lead over Lua 5.4 and Python 3.11, and pocketpy keeps Python syntax at about 1.2x CPython 3.8 on primes. Pick LuaJIT when throughput matters more than language features.

## Integration

| | |
|---|---|
| **Form** | source-drop (amalgamated janet.c + janet.h + janetconf.h); also static or shared library and standalone binary via GNU make, Meson or build_win (MSVC) |
| **Dependencies** | libm; libdl only for dynamic native modules (-DJANET_NO_DYNAMIC_MODULES removes it); optional companions spork and jpm |
| **Minimum toolchain** | C99 compiler (-std=c99); GNU make, Meson or Visual Studio build tools |
| **Platforms** | Linux, macOS, Windows, FreeBSD, NetBSD, OpenBSD, illumos, 32-bit Haiku; NaN-boxing on x86-64, arm64 and riscv64, wider 12- or 16-byte values elsewhere |
| **Thread safety** | VM state is thread-local: each OS thread runs its own VM with an isolated heap and GC, and data shared between threads is reference counted (README FAQ); a single VM must not be used from several threads |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaws in the only timing evidence (MikeBeller/janet-benchmarksgame): one run per benchmark, CPU time from /usr/bin/time, and runbench.janet checks only the exit code, never the output. The knucleotide outputs differ in format and sort order between the Janet and Python programs. The programs are also not like for like. Janet's revcomp2 caches translations of 6-byte windows. Its pidigits uses the third-party big (libbf) module with repeated-subtraction division. Its regexredux uses a hand-written regex-to-PEG converter and calls (gcsetinterval 1000000000), which effectively defers garbage collection. The Python regexredux still runs its matching through a one-worker multiprocessing Pool, despite the notebook's 'single threaded' note.
- The measured Janet was built with -O2 -flto, and the benchmark repo says LTO cuts run time by up to 30%. Janet's default Makefile build does not enable LTO; issue #1904, opened 2026-10-06, proposes making it the default. Expect stock builds to be slower than the published numbers.
- The evidence is dated: Janet 1.14.1 (2021) against today's 1.42.1 (2026-09-10) and 1.43.0-dev master, and Anaconda CPython 3.8 against current CPython. Nobody has measured the current standing.
- Non-local exits use setjmp/longjmp (README FAQ), so a Janet error unwinding through C++ frames skips destructors; catch errors at the C boundary (for example with janet_pcall) in C++ hosts.

## Known shortcomings

- Not faster overall: in the independent MikeBeller/janet-benchmarksgame run (Janet 1.14.1 vs Python 3.8, Benchmarks Game programs, i5-7500) Janet wins binarytrees 1.55x, knucleotide 1.20x and nbody 2.15x but loses fannkuch, reverse-complement (4.9x slower), pidigits and regexredux, a geomean about 1.12x slower (derived from page data). Old versions, compiler not named, one run per benchmark, output not checked, 16-star repo; the README FAQ has no numbers.
- Enricher: MikeBeller's runbench.janet checks exit code only and never output (knucleotide format and sort differ); the programs are not like for like (Janet revcomp uses a 6-byte cache, pidigits the third-party libbf 'big', regexredux a hand-written regex-to-PEG with gcsetinterval 1e9; Python regexredux runs via multiprocessing Pool(1)); Janet was built -flto, not the default (issue #1904). Geomean 1.12x slower than CPython 3.8 and Lua 5.4 is 1.43x faster (derived).

## Caveats and trade-offs

No first-party numbers: the README FAQ's 'a bit faster than Python' is hedged and qualitative, and the same FAQ says tight critical loops should be written in C or C++. The only Janet-versus-CPython timings found are a small independent repo (16 stars, last commit 2022-04-04, no license file) from 2021 on Janet 1.14.1 and Python 3.8: Janet won 3 of 7 benchmarks (pure-interpreter object and float work: binarytrees, nbody, knucleotide) and lost 4 where Python's C-implemented builtins do the work (bytes.translate, re, big ints), for a geometric mean about 1.12x slower (derived from page data). Versions are dated: CPython 3.11+ is substantially faster than 3.8 and Janet has had many releases since, so current standing is unmeasured. Single run per benchmark, no output validation.

Lisp-like language with its own syntax, a stop-the-world GC, boxed 8-byte values; threads have isolated heaps; PEG engine built in.

## Maintenance

Actively maintained (commits on 2026-10-06, release 1.42.1 on 2026-09-10) and MIT-licensed, easy to vendor as one C file; list it as an embeddable language with CPython-level speed, not as a faster replacement for CPython.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification D, tier now B.
- **Tier reason:** Upgraded from D: the original benchmark_url (README FAQ 'How fast is it?') has only a qualitative Python comparison, but an independent third-party repo (MikeBeller/janet-benchmarksgame, benchmark_runs/bench_pylua.csv, summary.ipynb, runner runbench.janet, bench_pylua.jdn) times Janet against CPython on seven Computer Language Benchmarks Game programs with CPU model (i5-7500) and Janet CFLAGS stated. Not A: the C compiler is not named and the Python baseline is an Anaconda 3.8 binary with no build details; it is a small personal repo, single run, not a well-known suite, so the orchestrator may prefer to cap it at C.
- **Verifier notes:** Metadata checked on github.com: MIT, 4.4k stars, 281 forks, not archived, last commit 2026-10-06 (active). Record's README paraphrase is accurate; I added the independent MikeBeller/janet-benchmarksgame numbers, which show Janet is not faster than CPython overall (faster on binarytrees 1.55x, knucleotide 1.20x, nbody 2.15x; slower on fannkuch, reverse-complement 4.9x, pidigits, regexredux; geomean about 1.12x slower). Shortcomings to record: claim only holds for interpreter-bound workloads, evidence dated (Janet 1.14.1, Python 3.8), compiler unnamed, single run; GitHub discussion #1239 has only anecdote ('faster than Python, but not quite as fast as PyPy').
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/janet-lang/janet>
  - <https://github.com/janet-lang/janet/commits>
  - <https://raw.githubusercontent.com/janet-lang/janet/HEAD/README.md>
  - <https://raw.githubusercontent.com/janet-lang/janet/HEAD/LICENSE>
  - <https://github.com/janet-lang/janet/discussions/1239>
  - <https://github.com/MikeBeller/janet-benchmarksgame>
  - <https://github.com/MikeBeller/janet-benchmarksgame/commits>
  - <https://raw.githubusercontent.com/MikeBeller/janet-benchmarksgame/HEAD/README.md>
  - <https://raw.githubusercontent.com/MikeBeller/janet-benchmarksgame/HEAD/benchmark_runs/bench_pylua.csv>
  - <https://raw.githubusercontent.com/MikeBeller/janet-benchmarksgame/HEAD/benchmark_runs/bench_pylua.jdn>
  - <https://raw.githubusercontent.com/MikeBeller/janet-benchmarksgame/HEAD/benchmark_runs/summary.ipynb>
  - <https://raw.githubusercontent.com/MikeBeller/janet-benchmarksgame/HEAD/runbench.janet>
  - <https://raw.githubusercontent.com/MikeBeller/janet-benchmarksgame/HEAD/pidigits/pidigits4.py>
  - <https://raw.githubusercontent.com/MikeBeller/janet-benchmarksgame/HEAD/reverse-complement/revcomp.py>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/janet-lang/janet/HEAD/README.md>
  - <https://raw.githubusercontent.com/janet-lang/janet/HEAD/src/core/vm.c>
  - <https://raw.githubusercontent.com/janet-lang/janet/HEAD/src/include/janet.h>
  - <https://raw.githubusercontent.com/janet-lang/janet/HEAD/src/conf/janetconf.h>
  - <https://raw.githubusercontent.com/janet-lang/janet/HEAD/CHANGELOG.md>
  - <https://github.com/janet-lang/janet/issues?q=is%3Aissue+performance>
  - <https://github.com/janet-lang/janet/issues/1904>
  - <https://github.com/janet-lang/janet/releases>
  - <https://raw.githubusercontent.com/MikeBeller/janet-benchmarksgame/HEAD/README.md>
  - <https://raw.githubusercontent.com/MikeBeller/janet-benchmarksgame/HEAD/runbench.janet>
  - <https://raw.githubusercontent.com/MikeBeller/janet-benchmarksgame/HEAD/benchmark_runs/bench_pylua.csv>
  - <https://raw.githubusercontent.com/MikeBeller/janet-benchmarksgame/HEAD/benchmark_runs/bench_pylua.jdn>
  - <https://raw.githubusercontent.com/MikeBeller/janet-benchmarksgame/HEAD/benchmark_runs/summary.ipynb>
  - <https://raw.githubusercontent.com/MikeBeller/janet-benchmarksgame/HEAD/knucleotide/knucleotide8.py>
  - <https://raw.githubusercontent.com/MikeBeller/janet-benchmarksgame/HEAD/knucleotide/knucleotide2.janet>
  - <https://raw.githubusercontent.com/MikeBeller/janet-benchmarksgame/HEAD/binarytrees/binarytrees2.py>
  - <https://raw.githubusercontent.com/MikeBeller/janet-benchmarksgame/HEAD/binarytrees/binarytrees1.janet>
  - <https://raw.githubusercontent.com/MikeBeller/janet-benchmarksgame/HEAD/nbody/nbody.py>
  - <https://raw.githubusercontent.com/MikeBeller/janet-benchmarksgame/HEAD/nbody/nbody2.janet>
  - <https://raw.githubusercontent.com/MikeBeller/janet-benchmarksgame/HEAD/reverse-complement/revcomp.py>
  - <https://raw.githubusercontent.com/MikeBeller/janet-benchmarksgame/HEAD/reverse-complement/revcomp2.janet>
  - <https://raw.githubusercontent.com/MikeBeller/janet-benchmarksgame/HEAD/regex-redux/regexredux1.py>
  - <https://raw.githubusercontent.com/MikeBeller/janet-benchmarksgame/HEAD/regex-redux/regexredux2.janet>
  - <https://raw.githubusercontent.com/MikeBeller/janet-benchmarksgame/HEAD/fannkuch/fannkuch.py>
  - <https://raw.githubusercontent.com/MikeBeller/janet-benchmarksgame/HEAD/fannkuch/fannkuch4-bakpakin.janet>
  - <https://raw.githubusercontent.com/MikeBeller/janet-benchmarksgame/HEAD/pidigits/pidigits4.py>
  - <https://raw.githubusercontent.com/MikeBeller/janet-benchmarksgame/HEAD/pidigits/pidigits.janet>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/janet-lang/janet`) · [data/wave12/enrich/raw/github_com_janet_lang_janet.json](../../../data/wave12/enrich/raw/github_com_janet_lang_janet.json) (enrichment confidence 0.75)

</details>
