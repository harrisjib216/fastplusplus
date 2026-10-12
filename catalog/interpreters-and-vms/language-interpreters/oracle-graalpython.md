# GraalPy

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Java/Python (GraalVM Truffle)` · `UPL-1.0` · 🟢 active

> Python 3.13 runtime on GraalVM Truffle; JIT-compiled pure Python runs many times faster than CPython, but mostly behind PyPy.

| | |
|---|---|
| **Beats** | CPython (first-party: CPython 3.12.8; independent suite: CPython 3.10.7); PyPy3 7.3.11 also in the independent suite, where GraalPy mostly loses |
| **Claimed result** | Independent kostya/jit-benchmarks round 1 (GraalPy 22.3.1 '--jvm' vs CPython 3.10.7, best time in s): binarytrees 2.02 vs 73.15, fannkuchredux 0.36 vs 4.04, fasta 3.53 vs 8.65, knucleotide 5.04 vs 8.41, mandelbrot 0.84 vs 37.52, matmul 1.4 vs 22.73, nbody 3.19 vs 53.72, spectralnorm 0.62 vs 20.69, brainfuck2 11.44 vs 142.26, brainfuck 14.22 vs &gt;190 (CPython timed out); slower than CPython on pidigits 9.78 vs 6.17, regexdna 9.04 vs 5.2, revcomp 4.36 vs 2.45. Against PyPy3 7.3.11 GraalPy wins only 4 of 13 (binarytrees 2.02 vs 3.84, fannkuchredux 0.36 vs 0.71, nbody 3.19 vs 4.44, spectralnorm 0.62 vs 0.71) and loses 9 (e.g. brainfuck 14.22 vs 8.77, matmul 1.4 vs 0.36, mandelbrot 0.84 vs 0.54, regexdna 9.04 vs 2.38). First-party: GraalPy 25.1.3 geomean 4.30x faster than CPython 3.12.8 on pyperformance when JIT compiled (README '\~4x', docs/user/assets/performance.svg); without the Graal JIT about 4x slower than CPython (docs/user/Performance.md). |
| **Workload** | Benchmarks Game style single-threaded programs (binarytrees, brainfuck, fannkuchredux, fasta, knucleotide, mandelbrot, matmul, nbody, pidigits, regexdna, revcomp, spectralnorm) run as whole processes in kostya/jit-benchmarks; first-party: pyperformance geomean over the pair-wise intersection of working benchmarks. |
| **Metric** | throughput |
| **Hardware** | Independent suite: AMD Ryzen 7 3800X, 80GB DDR4-3200, Docker on Ubuntu 22.10. First-party page states no hardware. |
| **Compiler and flags** | Independent suite: GraalVM image with 'gu install python', run as 'graalpython --jvm &lt;file&gt;' (GraalPy 22.3.1, Python 3.8.5); CPython 3.10.7 from Ubuntu 22.10 apt; PyPy3 7.3.11 official linux64 tarball; Docker on Ubuntu 22.10. First-party: each interpreter installed via pyenv, 'pyperformance run', flags and JDK not stated. |
| **Adoption** | 1.7k stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/oracle/graalpython) · [benchmark](https://github.com/kostya/jit-benchmarks) |

## Verdict

Independent kostya/jit-benchmarks round 1 (2023-02-28, AMD Ryzen 7 3800X, Docker on Ubuntu 22.10): GraalPy 22.3.1 in JVM mode beat CPython 3.10.7 on 10 of 13 single-threaded programs by about 1.7x (knucleotide) to 45x (mandelbrot) (derived from page data, best of up to 5 in-process iterations, startup excluded), lost on pidigits, regexdna and revcomp, and lost 9 of 13 to PyPy3 7.3.11. The project's own chart reports GraalPy 25.1.3 at a 4.30x pyperformance geomean over CPython 3.12.8 with no hardware stated.

## Use it when

- Long-running, CPU-bound pure-Python loops where warmup is amortised: in kostya/jit-benchmarks GraalPy 22.3.1 (JVM mode) ran mandelbrot in 0.84 s vs 37.52 s, nbody 3.19 vs 53.72 s and binarytrees 2.02 vs 73.15 s on CPython 3.10.7.
- Embedding Python inside a Java application (Maven/Gradle artifacts, polyglot Context API, Java interop, file-system and OS access mediated by Java), including migrating Jython code with --python.EmulateJython.
- Shipping a Python application as a single standalone binary through GraalVM Native Image.
- Polyglot services that already run on GraalVM and want Python next to Java, JavaScript or Ruby with one compiler and shared tooling.

## Skip it when

- When PyPy is an option for standalone pure-Python speed: in the same independent run PyPy3 7.3.11 beat GraalPy on 9 of 13 programs (e.g. matmul 0.36 vs 1.4 s, regexdna 2.38 vs 9.04 s) at about 60-270 MB max RSS on most programs vs 1.1-3.3 GB for GraalPy in JVM mode.
- Short scripts, CLIs and serverless cold starts: time before the first benchmark line was 2.79-6.55 s in JVM mode (0.27-4.27 s native) vs 0.19-1.07 s for CPython, and without the JIT GraalPy is about 4x slower than CPython; a user measured the 24.1.2 standalone about 5x slower than CPython on a pyperformance fork (issue #480).
- C-extension-heavy code (NumPy, pandas, ML stacks): extensions are API- but not ABI-compatible, CPython wheels from PyPI cannot be used, packages must be built with GraalPy's patched pip, and the docs say such code benefits little from the JIT (issue #334 reported pandas performance as terrible).
- Regex, bignum and bulk string or I/O work: regexdna 9.04 vs 5.2 s, pidigits 9.78 vs 6.17 s and revcomp 4.36 vs 2.45 s against CPython 3.10.7; issue #445 (open) reports the re module about 4x slower than CPython 3.12.6.
- Memory-limited hosts, Windows or macOS (documented as less tested, Windows with more limitations), or untrusted code (SECURITY.md: execution of untrusted or adversarial code is not supported).

## How it is fast

Python is executed by a Truffle interpreter whose hot code is compiled by the Graal JIT through partial evaluation of the interpreter with type speculation and deoptimization, so tight loops, object allocation and float arithmetic compile to machine code instead of being dispatched opcode by opcode as in CPython. The speedup needs the Graal compiler and warmup: without JIT compilation the project says GraalPy runs pure Python about 4x slower than CPython. C extensions run through an emulation of CPython internals and gain little.

## Compared with alternatives

Pick GraalPy over PyPy when Python has to run inside a JVM application with Java interop or be packaged as a Native Image binary; for standalone pure-Python throughput PyPy won 9 of 13 kostya benchmarks with a fraction of the memory, and Cython or Codon beat both on hot loops if you can compile the code.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | GraalVM polyglot SDK and Truffle runtime (Maven org.graalvm.polyglot:polyglot plus python); the Graal JIT compiler (GraalVM JDK or a Graal-enabled JDK) for compiled speed; a C toolchain to build native extension packages; the standalone launcher bundles the runtime |
| **Minimum toolchain** | Python 3.13 language level (25.3.x, stdlib 3.13.14); minimum JDK for embedding not stated in the pages read |
| **Platforms** | Linux amd64 and aarch64 (recommended; Oracle Linux is the primary test platform), macOS aarch64, Windows amd64 (more limitations) |
| **Thread safety** | Has a global interpreter lock like CPython; the GIL is released by default during interop with other languages (polyglot.gil_locked_during_interop keeps it held) |
| **Drop-in for the baseline** | partial — runs pure Python 3.13 code with pip and venv (the CPython test suite passes about 85%), but C extensions must be rebuilt from source with GraalPy's pip, CPython binary wheels do not work, and replacing pip or using uv is discouraged |

## Gotchas

- Harness detail behind the A-tier numbers: kostya/jit-benchmarks times each iteration inside the process after a 'started' marker and reports the best of up to 5 in-process iterations, so JVM startup is excluded (reported separately as 'Compile T', 2.79-6.55 s for GraalPy JVM) and later iterations are warmed; the record's 'whole-process times, startup included' description is wrong, and only knucleotide, regexdna and revcomp (one iteration each) include warmup.
- Harness asymmetry against PyPy: PyPy's fannkuchredux (0.71 s) and nbody (4.44 s) rows show Runs 1 although five iterations fit well inside the 60 s and 80 s timeouts, and the runner records at most one time(...) match per 1024-byte stderr read, so 2 of GraalPy's 4 wins over PyPy compare a single recorded PyPy iteration with GraalPy's best of 5.
- The independent numbers are JVM mode ('graalpython --jvm', GraalVM CE 22.3.1, Python 3.8.5), but standalone JVM distributions stopped in 25.1; the native launcher was slower in the same run (binarytrees 3.41 vs 2.02 s, matmul 2.26 vs 1.4 s, revcomp 10.98 vs 4.36 s), now defaults to -X jit=1 (one compiler thread, higher thresholds) and on Linux to a lower-footprint GC that the docs say can slow some workloads; use -X jit=2 for throughput.
- The first-party 4.30x pyperformance geomean (GraalPy 25.1.3 vs CPython 3.12.8) covers only the pair-wise intersection of benchmarks that run on both and states no hardware, JDK, JIT preset or flags.

## Known shortcomings

- Java, not C++. Independent kostya/jit-benchmarks numbers (GraalPy 22.3.1, Ryzen 7 3800X, vs CPython 3.10.7) show it losing 9 of 13 programs to PyPy with 1.1-3.3 GB RSS; the first-party 4.30x geomean over CPython 3.12.8 is vendor-measured.
- Enricher: kostya times in-process after a 'started' marker (best of up to 5 iterations, JVM startup excluded), so the record's 'whole-process times' caveat was wrong; the runner keeps at most one time(...) per 1024-byte stderr read, and the PyPy fannkuchredux and nbody rows show that 2 of GraalPy's 4 wins over PyPy are a single PyPy iteration against GraalPy's best of 5. The A-tier numbers are --jvm mode, but JVM standalones were discontinued in 25.1; the native launcher was slower in the same run and now defaults to -X jit=1. Issue #445: re about 4x slower than CPython; issue #480: a user saw the 24.1.2 standalone about 5x slower.

## Caveats and trade-offs

Java implementation (runs on the JVM or as a GraalVM native image), not a C++ library; listed because the claim is against Python implementations and its JIT is the Graal compiler. Independent numbers are for GraalPy 22.3.1 (Feb 2023), not the current release; whole-process times, so JVM startup and JIT warm-up are included. Against PyPy, the jits-category incumbent, GraalPy loses 9 of 13 benchmarks. Memory is far higher: 1.1-3.3 GB max RSS for GraalPy JVM vs 8-951 MB for CPython in the suite (binarytrees 3265 MB vs 98.5 MB). Without JIT compilation GraalPy is about 4x slower than CPython, so short scripts are slower; C-extension-heavy code benefits little. First-party 4x geomean has no hardware and only covers benchmarks that run on both. [retier] Java implementation (JVM or GraalVM native image), not a C++ library; listed because the claim is against Python implementations. Independent numbers are GraalPy 22.3.1 --jvm (February 2023): kostya times in-process after a 'started' marker, best of up to 5 iterations with JVM startup excluded, keeping at most one time(...) per 1024-byte stderr read; the PyPy fannkuchredux and nbody rows show 2 of GraalPy's 4 wins over PyPy are a single PyPy iteration against GraalPy's best of 5. Loses 9 of 13 to PyPy, uses 1.1-3.3 GB RSS. JVM standalones were discontinued in 25.1; the native launcher was slower in the same run and now defaults to -X jit=1. Issue #445: re about 4x slower than CPython; issue #480: 24.1.2 standalone about 5x slower for one user. First-party 4.30x geomean over CPython 3.12.8 is vendor-measured.

Runs on the JVM and needs JIT warm-up; README describes native extension module support as experimental.

## Maintenance

Actively developed by Oracle (last commit 2026-10-06, release 25.3.4.1 with the 3.13.14 standard library, UPL-1.0) and usable as a CPython replacement for pure-Python code or as Java-embedded Python, but the independent evidence is a 2023 JVM-mode run of 22.3.1 (JVM standalones discontinued in 25.1) whose harness gives PyPy only one recorded iteration on two of GraalPy's four wins over it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded C to A on the independent kostya/jit-benchmarks round 1 (2023-02-28): public benchmark code (BENCH/test.py per benchmark, docker/graalpython, docker/python3, docker/pypy3, run command 'graalpython --jvm' in tools/languages.rb), runtime versions (GraalPy 22.3.1, CPython 3.10.7, PyPy3 7.3.11) and CPU (AMD Ryzen 7 3800X) all stated, and it runs against CPython. The first-party docs/user/Performance.md 4x claim alone would be C (no hardware).
- **Verifier notes:** Upgraded C to A on kostya/jit-benchmarks (independent, reproducible, against CPython); the record's own caveat listed only 3 of GraalPy's 9 losses to PyPy, corrected. Shortcomings: slower than PyPy on most benchmarks, multi-GB memory, startup-dominated short runs slower than CPython, old version in the independent run, Java not C++. Metadata checked: UPL-1.0, 1.7k stars, last commit 2026-10-06.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `baseline`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/oracle/graalpython/HEAD/docs/user/Performance.md>
  - <https://raw.githubusercontent.com/oracle/graalpython/HEAD/README.md>
  - <https://raw.githubusercontent.com/oracle/graalpython/HEAD/docs/user/assets/performance.svg>
  - <https://github.com/oracle/graalpython>
  - <https://github.com/oracle/graalpython/commits>
  - <https://github.com/kostya/jit-benchmarks>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/languages.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/graalpython>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/python3>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/pypy3>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/oracle/graalpython/HEAD/README.md>
  - <https://raw.githubusercontent.com/oracle/graalpython/HEAD/docs/user/Performance.md>
  - <https://raw.githubusercontent.com/oracle/graalpython/HEAD/docs/user/assets/performance.svg>
  - <https://raw.githubusercontent.com/oracle/graalpython/HEAD/docs/user/README.md>
  - <https://raw.githubusercontent.com/oracle/graalpython/HEAD/docs/user/Native-Extensions.md>
  - <https://raw.githubusercontent.com/oracle/graalpython/HEAD/docs/user/Python-Runtime.md>
  - <https://raw.githubusercontent.com/oracle/graalpython/HEAD/docs/user/Standalone-Getting-Started.md>
  - <https://raw.githubusercontent.com/oracle/graalpython/HEAD/docs/user/Embedding-Getting-Started.md>
  - <https://raw.githubusercontent.com/oracle/graalpython/HEAD/docs/user/Python-on-JVM.md>
  - <https://raw.githubusercontent.com/oracle/graalpython/HEAD/docs/user/Tooling.md>
  - <https://raw.githubusercontent.com/oracle/graalpython/HEAD/docs/user/Troubleshooting.md>
  - <https://raw.githubusercontent.com/oracle/graalpython/HEAD/docs/user/Test-Tiers.md>
  - <https://raw.githubusercontent.com/oracle/graalpython/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/oracle/graalpython/HEAD/SECURITY.md>
  - <https://github.com/oracle/graalpython/issues?q=is%3Aissue+slower+than+cpython>
  - <https://github.com/oracle/graalpython/issues/480>
  - <https://github.com/oracle/graalpython/issues/445>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/languages.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/cli.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/runner.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/benchmarks.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/graalvm>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/nbody/test.py>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/brainfuck/test.py>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/oracle/graalpython`) · [data/wave12/enrich/raw/github_com_oracle_graalpython.json](../../../data/wave12/enrich/raw/github_com_oracle_graalpython.json) (enrichment confidence 0.75)

</details>
