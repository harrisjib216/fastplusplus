# Objeck

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Objeck: object-oriented language with a C++ VM and AMD64/ARM64 method JIT; beats CPython and Ruby, LuaJIT only on binarytrees.

| | |
|---|---|
| **Beats** | LuaJIT 2.1 (tracing JIT); the same table also lists Java 21 (OpenJDK 21.0.12 HotSpot, tiered JIT), CPython 3.12.3 and Ruby 3.2.3 |
| **Claimed result** | docs/performance.md (2026-09-12 Docker run, median of 3): binarytrees 17 Objeck 2.14 s vs LuaJIT 3.57 s (1.7x faster, the one like-for-like win) and Java 21 0.26 s; nbody 50M Objeck 8.14 s vs LuaJIT 4.37 s and Java 2.35 s (slower); spectralnorm 5500 Objeck 2.72 s vs LuaJIT 1.12 s and Java 1.18 s (slower); fannkuchredux 12 Objeck 32.76 s vs LuaJIT 117.99 s (page says 3.6x faster) and Java 20.70 s, but that row is not like-for-like because Objeck runs the optimized CLBG algorithm and LuaJIT a naive port that allocates a table per permutation. Objeck beats CPython 3.12 and Ruby 3.2 on all four rows (for example nbody 16.6x and 27.0x). |
| **Workload** | Computer Language Benchmarks Game programs (nbody 50M, binarytrees 17, spectralnorm 5500, fannkuchredux 12) in one Docker run, median of 3 runs; Objeck programs compiled with -opt s3 and JIT-compiled at runtime. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 7950X3D (16C/32T), 128 GB RAM (62 GB visible in Docker), Docker on a Windows 11 host |
| **Compiler and flags** | Objeck v2026.9.1 (f6b3b09046), VM (obr) and compiler (obc) built from source in Ubuntu 24.04 with g++ from build-essential using core/vm/make/Makefile.amd64 (-O3 -flto=auto -mavx2 -std=c++20); programs compiled with -opt s3; LuaJIT, Python 3.12.3, Ruby 3.2.3 and OpenJDK 21.0.12 from Ubuntu apt packages (perf-results/docker/Dockerfile); Objeck timed with /usr/bin/time %e, the other languages with date +%s%N around each process |
| **Adoption** | 165 stars |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/objeck/objeck-lang) · [benchmark](https://github.com/objeck/objeck-lang/blob/HEAD/docs/performance.md) |

## Verdict

In one Docker run (Ubuntu 24.04 on a Windows 11 host, Ryzen 9 7950X3D, median of 3), Objeck v2026.9.1 built with g++ -O3 -flto -mavx2 and programs compiled at -opt s3 ran binarytrees 17 in 2.14 s against LuaJIT 2.1's 3.57 s (1.7x, comparable single-threaded programs) but lost to LuaJIT on nbody (8.14 s vs 4.37 s) and spectralnorm (2.72 s vs 1.12 s); its fannkuchredux win (32.76 s vs 117.99 s) uses a weaker Lua program, and OpenJDK 21 beat Objeck on nbody, binarytrees and fannkuchredux.

## Use it when

- You want a small batteries-included OO scripting language that runs integer and call-heavy code 13-47x faster than CPython 3.12 and Ruby 3.2 (nbody, spectralnorm, fannkuchredux rows of the Docker run).
- Allocation-heavy tree code where it measured 2.14 s against LuaJIT 2.1's 3.57 s and CPython's 3.48 s on binarytrees depth 17, if 209 MB peak RSS is acceptable.
- Projects that would otherwise glue a scripting language to HTTP/3, ONNX or OpenCV libraries and value having those in the standard library on Linux, macOS and Windows, x64 and ARM64.

## Skip it when

- Float-heavy loops: nbody is 1.9x slower than LuaJIT and 3.5x slower than OpenJDK 21, spectralnorm about 2.4x slower than both.
- When Java, .NET or Julia is an option: HotSpot won 3 of the 4 cross-language rows (binarytrees 8.2x faster than Objeck), even running the naive fannkuchredux port.
- Code that relies on Try() for error recovery in hot paths: methods holding a Try region never JIT, and issue #925 (errors raised inside JIT-compiled code cannot be caught by Try()) is still open.
- Production systems that need a long-stable compiler: the September-October 2026 releases fixed several silent miscompiles at the default -opt s3 level (#1037 infinite loop from inlined helpers, #988 Bool[] call results), NaN comparisons that were all true on Windows (#1000) and GC/thread crashes (#874, #877, #913).

## How it is fast

A single-pass method JIT translates each method's bytecode with an accumulator model, keeps locals in native stack slots with a register cache, folds constants and strength-reduces division, and emits inline nil, bounds and divide-by-zero checks. Methods marked native are always compiled and other methods auto-JIT after 10 calls; since v2026.9.1 compiled callers enter compiled callees directly through a native calling convention with inline caches at virtual and function-reference sites. A young-generation bump allocator with parallel marking is what took binarytrees from 8.53 s to 2.14 s.

## Compared with alternatives

Pick Objeck over WrenJIT or stryke when you want a full general-purpose language with a mature standard library rather than a single fast embeddable VM; for raw throughput against LuaJIT the .NET runtime, Julia, Dart or Chez Scheme entries beat it on independent shootouts, and Objeck's own table shows HotSpot ahead on 3 of 4 rows.

## Integration

| | |
|---|---|
| **Form** | language toolchain (obc compiler and obr VM binaries; release archives for Windows, Linux and macOS) |
| **Dependencies** | Linux release needs system mbedTLS, readline, SDL2/GL, OpenCV, unixODBC and LAME (install_deps.sh); a source-built obr links mbedTLS and zlib plus static nghttp2, ngtcp2, nghttp3 and AWS-LC built by tools/deps/build_quic_deps.sh |
| **Minimum toolchain** | C++20 compiler (Makefile.amd64 uses g++ -std=c++20 -O3 -flto=auto -mavx2) |
| **Platforms** | Linux, macOS, Windows on x86-64 and ARM64 (JIT on both); the stock amd64 source build uses -mavx2 so needs an AVX2 CPU |
| **Thread safety** | Language-level threads with a parallel-marking GC; several thread/GC races were fixed in September 2026 (#874, #877, #913); embedding thread rules not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: every benchmark's output goes to /dev/null unchecked and the cross-language runner discards stderr (eval "\$cmd" &gt; /dev/null 2&gt;&1), so a crashed or miscompiled run would still be timed; the page itself says this hid a fasta compile failure and a Console-&gt;WriteBuffer double-encoding bug for months, and v2026.10.0 later fixed an -opt s3 miscompile (#1037) in the same optimizer level the benchmarks used.
- The 3.6x fannkuchredux win over LuaJIT compares Objeck's optimized CLBG algorithm (native-annotated, reversal of the inner span only) with a naive Lua port that allocates and fills a fresh table per permutation; it measures the Lua program, not LuaJIT.
- The JIT does no inlining (ProcessInlineMethod is never called, yet every compiled frame reserves inline stack space), methods with frame-dependent traps (serialization, time, file-time calls) stay interpreted, and on ARM64 an expression with more than twelve live temporaries falls back to the interpreter whole.
- Timings come from Docker on a Windows 11 host, where the page says interpreter-bound rows run 30-50% slower than native, and LuaJIT, Python, Ruby and Java are Ubuntu 24.04 apt packages with unrecorded builds.

## Known shortcomings

- Downgraded A to C: the 3.6x fannkuchredux win over LuaJIT is not like for like (fannkuchredux.lua allocates a fresh table per permutation with naive full reversal while Objeck runs the optimized CLBG algorithm in a native-annotated function); the only fair win over LuaJIT is binarytrees at 1.7x, it loses nbody 1.9x and spectralnorm 2.4x, and Java wins 3 of 4.
- Enricher: all outputs go to /dev/null unchecked and the cross-language runner drops stderr (the page admits this hid a fasta failure), and v2026.10.0 later fixed an -opt s3 miscompile (#1037) at the optimizer level the benchmarks used; fannkuchredux compares the optimized algorithm with a naive Lua port while binarytrees (1.7x over LuaJIT) runs comparable programs. Open #925: Try() cannot catch errors raised in JIT code; the JIT does no inlining.

## Caveats and trade-offs

The Lua source behind the 117.99 s LuaJIT fannkuchredux time (perf-results/cross-lang/benchmarks/fannkuchredux.lua) creates a new table with 'local perm = {}' and copies 12 elements into it for every permutation (hundreds of millions of table allocations and resizes for n=12) and reverses from index 0, whereas the Java port reuses one preallocated array and Objeck's programs/tests/clbg/fannkuchredux.obs is the optimized CLBG algorithm (first-element swap trick, reversal of the inner span only) inside a native-annotated function; the Python and Ruby ports are the same naive algorithm. The 3.6x fannkuchredux win over LuaJIT therefore measures a weaker Lua program, not LuaJIT, and Java, running the naive algorithm, still beats Objeck on it. The Java and Python ports also compute the checksum sign from the checksum's parity rather than the permutation index, and every program's output goes to /dev/null unchecked. Like-for-like rows: Objeck beats LuaJIT only on binarytrees (1.7x) and loses on nbody (1.9x) and spectralnorm (2.4x); Java wins 3 of 4 rows. Only four benchmarks are in the cross-language table, all in Docker on a Windows 11 host; LuaJIT is the distro package with the exact build not recorded. Objeck is a language VM with a JIT, not a drop-in library. The most recent commit seen was a bot download-stats snapshot (2026-10-05); the last code commits are 2026-10-03 and release notes for v2026.10.0 were added on 2026-10-02, while the repo page shows v2026.9.7 as the latest release. [retier] The 3.6x fannkuchredux win over LuaJIT is not like for like (the Lua port allocates a fresh table per permutation with naive full reversal while Objeck runs the optimized CLBG algorithm in a native-annotated function); the only fair win over LuaJIT is binarytrees at 1.7x, it loses nbody 1.9x and spectralnorm 2.4x, and Java wins 3 of 4. All benchmark outputs go to /dev/null unchecked and the cross-language runner drops stderr (the page admits this hid a fasta failure); v2026.10.0 later fixed an -opt s3 miscompile (#1037) at the optimizer level used. Open #925: Try() cannot catch errors raised in JIT code; the JIT does no inlining.

A separate language (Objeck), not a drop-in for Lua or Java code. Method JIT applies to methods annotated native and to auto-JIT for methods containing MTHD_CALL. binarytrees peaks at 209 MB RSS against single-digit MB for the others. Interpreter-bound rows run 30-50% slower in Docker than natively, per the page.

## Maintenance

Very active (releases every few weeks, v2026.9.7 current with v2026.10.0 notes landed, last commit 2026-10-05) and BSD-3-Clause, but recent releases still fix silent miscompiles and GC races, so pin a release and run your own output checks.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): downgrade; tier before verification A, tier now C.
- **Tier reason:** The cross-language table in docs/performance.md is reproducible on paper (perf-results/docker/Dockerfile, perf-results/docker/run_all_benchmarks.sh, perf-results/cross-lang/benchmarks/\*, obr built with -O3 -flto=auto -mavx2 per core/vm/make/Makefile.amd64, Ryzen 9 7950X3D), but the headline win over LuaJIT compares different algorithms: Objeck runs programs/tests/clbg/fannkuchredux.obs, the optimized CLBG algorithm in a native-annotated (always JIT-compiled) function, while LuaJIT runs perf-results/cross-lang/benchmarks/fannkuchredux.lua, a naive full-reversal port that allocates a fresh table for every permutation. A baseline column that ran a weaker program caps the evidence at C (v8malloc precedent).
- **Verifier notes:** Inspected the Lua source as asked: fannkuchredux.lua allocates a fresh table per permutation and uses a naive algorithm, while Objeck runs the optimized CLBG program, so the 3.6x 'beats LuaJIT' headline is not like-for-like; downgraded A to C rather than rejected because the remaining rows are genuine and Objeck's binarytrees win (1.7x) uses comparable programs. Record shortcomings: not faster than LuaJIT on like-for-like float rows, not faster than Java on 3 of 4, unequal baseline port on the headline row. BSD-3-Clause confirmed from LICENSE (bundled OpenSSL, SDL2, zlib and Eigen notices), 165 stars, last commit 2026-10-05.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/objeck/objeck-lang/HEAD/docs/performance.md>
  - <https://raw.githubusercontent.com/objeck/objeck-lang/HEAD/perf-results/docker/Dockerfile>
  - <https://raw.githubusercontent.com/objeck/objeck-lang/HEAD/perf-results/docker/run_all_benchmarks.sh>
  - <https://github.com/objeck/objeck-lang/tree/master/perf-results/cross-lang/benchmarks>
  - <https://raw.githubusercontent.com/objeck/objeck-lang/HEAD/perf-results/cross-lang/benchmarks/fannkuchredux.lua>
  - <https://raw.githubusercontent.com/objeck/objeck-lang/HEAD/perf-results/cross-lang/benchmarks/fannkuchredux.java>
  - <https://raw.githubusercontent.com/objeck/objeck-lang/HEAD/perf-results/cross-lang/benchmarks/fannkuchredux.py>
  - <https://raw.githubusercontent.com/objeck/objeck-lang/HEAD/perf-results/cross-lang/benchmarks/binarytrees.lua>
  - <https://raw.githubusercontent.com/objeck/objeck-lang/HEAD/perf-results/cross-lang/benchmarks/spectralnorm.lua>
  - <https://raw.githubusercontent.com/objeck/objeck-lang/HEAD/perf-results/cross-lang/benchmarks/nbody.lua>
  - <https://raw.githubusercontent.com/objeck/objeck-lang/HEAD/perf-results/cross-lang/benchmarks/run_cross_lang.sh>
  - <https://raw.githubusercontent.com/objeck/objeck-lang/HEAD/programs/tests/clbg/fannkuchredux.obs>
  - <https://raw.githubusercontent.com/objeck/objeck-lang/HEAD/programs/tests/clbg/binarytrees.obs>
  - <https://raw.githubusercontent.com/objeck/objeck-lang/HEAD/core/vm/make/Makefile.amd64>
  - <https://raw.githubusercontent.com/objeck/objeck-lang/HEAD/LICENSE>
  - <https://github.com/objeck/objeck-lang>
  - <https://github.com/objeck/objeck-lang/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/objeck/objeck-lang/HEAD/README.md>
  - <https://raw.githubusercontent.com/objeck/objeck-lang/HEAD/docs/performance.md>
  - <https://raw.githubusercontent.com/objeck/objeck-lang/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/objeck/objeck-lang/HEAD/perf-results/docker/Dockerfile>
  - <https://raw.githubusercontent.com/objeck/objeck-lang/HEAD/perf-results/docker/run_all_benchmarks.sh>
  - <https://raw.githubusercontent.com/objeck/objeck-lang/HEAD/perf-results/cross-lang/benchmarks/run_cross_lang.sh>
  - <https://raw.githubusercontent.com/objeck/objeck-lang/HEAD/perf-results/cross-lang/benchmarks/binarytrees.lua>
  - <https://raw.githubusercontent.com/objeck/objeck-lang/HEAD/perf-results/cross-lang/benchmarks/binarytrees.java>
  - <https://raw.githubusercontent.com/objeck/objeck-lang/HEAD/perf-results/cross-lang/benchmarks/nbody.lua>
  - <https://raw.githubusercontent.com/objeck/objeck-lang/HEAD/perf-results/cross-lang/benchmarks/spectralnorm.lua>
  - <https://raw.githubusercontent.com/objeck/objeck-lang/HEAD/perf-results/cross-lang/benchmarks/fannkuchredux.lua>
  - <https://raw.githubusercontent.com/objeck/objeck-lang/HEAD/programs/tests/clbg/binarytrees.obs>
  - <https://raw.githubusercontent.com/objeck/objeck-lang/HEAD/programs/tests/clbg/nbody.obs>
  - <https://raw.githubusercontent.com/objeck/objeck-lang/HEAD/programs/tests/clbg/spectralnorm.obs>
  - <https://raw.githubusercontent.com/objeck/objeck-lang/HEAD/programs/tests/clbg/fannkuchredux.obs>
  - <https://raw.githubusercontent.com/objeck/objeck-lang/HEAD/core/vm/make/Makefile.amd64>
  - <https://raw.githubusercontent.com/objeck/objeck-lang/HEAD/core/vm/arch/jit/README.md>
  - <https://github.com/objeck/objeck-lang/tree/master/core/vm/arch/jit>
  - <https://github.com/objeck/objeck-lang/issues?q=is%3Aissue+JIT>
  - <https://github.com/objeck/objeck-lang>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/objeck/objeck-lang`) · [data/wave12/enrich/raw/github_com_objeck_objeck_lang.json](../../../data/wave12/enrich/raw/github_com_objeck_objeck_lang.json) (enrichment confidence 0.8)

</details>
