# Luava

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Java` · `MPL-2.0` · 🟢 active

> Pure-Java Lua 5.4 engine with a tiered Lua-to-JVM-bytecode JIT; 1.2x to 19x faster than the LuaJ 3.0.1 interpreter.

| | |
|---|---|
| **Beats** | LuaJ 3.0.1 (the widely used Java Lua implementation); PUC Lua and LuaJIT are not benchmarked |
| **Claimed result** | LuaJ time over Luava time: coroutines 234.7 ms vs 4549.9 ms (19.39x), recursive fib 243.8 ms vs 2538.6 ms (10.41x), arithmetic loop 33.7 ms vs 285.6 ms (8.47x), string concat 3.03x, table insert/scan 2.83x, hash table 2.68x, sieve 1.84x, string patterns 1.43x, closures 1.21x, OOP metatables 1.21x; all 10 tasks won. |
| **Workload** | Ten Lua tasks (arithmetic loop, recursive fib, table insert/scan, string concat, closures, coroutines, hash table, OOP metatables, string patterns, sieve), paired interleaved runs against LuaJ, order-flipped, median, warm=6, iters=10, with -Dluava.jit.sync=true. |
| **Metric** | throughput |
| **Compiler and flags** | JDK 21+ (exact JDK build not stated); harness benchmarks/harness/interleave.sh runs java -XX:+UseG1GC -Xmx1g with -Dluava.jit.sync=true, taskset-pinned to one core except the coroutine task; LuaJ 3.0.1 run through LuaJBench.java with the same flags |
| **Adoption** | 2 stars; on Maven Central |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/KienPC1234/luava) · [benchmark](https://github.com/KienPC1234/luava) |

## Verdict

With JIT tier-up made synchronous (-Dluava.jit.sync=true), JDK 21+, G1 and -Xmx1g, a paired order-flipped harness (median of best-of-10 after 6 warm-up evals) put Luava ahead of the LuaJ 3.0.1 interpreter on all 10 small Lua tasks, from 1.21x (closures, OOP metatables) to 10.41x (fib(35): 243.8 ms vs 2538.6 ms) and 19.39x (coroutines); no CPU model is given. Against C Lua the only numbers are older: the 2026-09-11 pre-JIT report shows C Lua 5.4 at 794.76 ms for fib(35) and 43.80 ms for 200k coroutine switches, so the current JIT is about 3.3x faster than C Lua on fib but about 5.4x slower on coroutines (derived from page data, different runs and builds).

## Use it when

- A JVM service or game server already embedding LuaJ whose scripts are numeric loops, recursive functions or string/table building and you can afford a host-API rewrite.
- You need Lua 5.4 semantics (integer subtype, //, bitwise operators, &lt;close&gt;) on the JVM; LuaJ only implements 5.2.
- Multi-tenant hosts running untrusted scripts that need instructionLimit or timeout plus a Java-access allowlist (note the JIT is bypassed while those guards are active).
- Coroutine-heavy scripts on the JVM: 200k yield/resume pairs took 234.7 ms against LuaJ's 4549.9 ms in the project's harness.
- Long-running processes that eval the same script repeatedly, where tier-up and C2 warm-up are amortized.

## Skip it when

- Raw Lua speed outside the JVM: use PUC Lua or LuaJIT; the project's own committed report (2026-09-11, pre-JIT build) had Luava 4x to 114x slower than C Lua 5.4, and the current JIT has no published head-to-head with C Lua or LuaJIT.
- Short-lived CLI runs or first-request-latency-sensitive paths: the README measures the first eval of a small script at about 47 ms versus 13 ms for LuaJ, unless you call JitCompiler.prewarm.
- Scripts dominated by metatable OOP, closures or string patterns: the gains there are 1.2x to 1.4x over an interpreter, and code using coroutines, debug hooks, instructionLimit or timeout never enters JIT code.
- Hosts that need native C Lua modules (.so via LUA_CPATH) or os.execute-driven tooling; both are out of scope.
- Production use that needs a stable API or track record: version 0.2.5, API may change before 1.0, 2 stars, one author, and two commits in the two days before the 0.2.5 release fixed 12 conformance gaps and six core and stdlib bugs found by differential testing against PUC Lua.

## How it is fast

The interpreter keeps numbers and booleans unboxed in three parallel stacks (long[] raw bits, byte[] type tags, LuaValue[] references). Hot protos (50 calls, or 8192 loop back-edges with on-stack replacement) that pass a static subset analysis are translated with ASM into one static JVM method per Lua function, loaded as a hidden class, with unboxed long flow, direct INVOKESTATIC self-recursion and type guards that deopt back to the interpreter at the current pc; HotSpot C2 then inlines and register-allocates that code. Coroutines run on JDK 21 virtual threads instead of LuaJ's platform threads, which accounts for the 19x coroutine result. eval caches the compiled proto tree by chunk name plus source, so a repeated eval of the same script keeps its JIT state.

## Compared with alternatives

Pick Luava when the host is a JVM and you want Lua 5.4 with sandboxing and Java interop; Apogee (Go, Lua 5.5, measured against C Lua and LuaJIT) and FakeLua (beats PUC Lua 5.4) are the choices outside the JVM, and plain LuaJIT stays faster for standalone Lua.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime (ASM 9.7 shaded into the jar as org.luava.shaded.asm) |
| **Minimum toolchain** | JDK 21+ (no --enable-preview, no JNI/FFM); Maven 3.9+ or Gradle only to build from source |
| **Platforms** | any JVM 21+ |
| **Thread safety** | A LuaState must be used from one host thread; concurrent top-level eval on one state is not supported. Separate states share no globals, but the JIT compiler (single background thread, synchronized tryCompile) and the 512-entry compiled-code LRU cache are process-wide. |
| **Drop-in for the baseline** | partial — same language role as LuaJ and mirrors java.proxy/luajava.createProxy, but the embedding API differs (LuaState instead of Globals) and the language is Lua 5.4 rather than 5.2 |

## Gotchas

- Harness asymmetry: Bench.java calls st.eval(code) on one LuaState, and LuaState caches the compiled proto tree by chunk name plus source, so timed Luava iterations skip lexing, parsing and compilation and start with already-JIT-compiled kernels; LuaJBench.java calls globals.loadfile(file) every iteration, re-reading and re-compiling the file. For these millisecond-scale tasks this is a small bias toward Luava, not a reversal, but it contradicts the 'both re-evaluate the source each iteration' reading.
- The baseline is LuaJ's interpreter: LuaJBench.java uses JsePlatform.standardGlobals() without installing LuaJ's luajc Lua-to-Java-bytecode compiler, so JIT-versus-interpreter is what was measured; weak asserts in the closures (sum &gt; 0), OOP (acc &gt; 0) and string-concat (length &gt; 100000) tasks check little.
- Running from exploded classes (IDE, mvn exec) without ASM on the classpath silently disables the JIT; since 0.2.5 a one-time stderr notice is printed. Benchmark only the packaged jar.
- The README table has no CPU model, JDK build or committed results file, and the coroutine task is run unpinned while the others are taskset-pinned to one core.

## Known shortcomings

- Baseline is the LuaJ interpreter, not PUC Lua or LuaJIT, with no CPU model or JDK build; the repo's own pre-JIT report shows 4-114x slower than C Lua and the first eval takes 47 ms against LuaJ's 13 ms. Java.
- Enricher: LuaState.eval caches the compiled proto by chunk name plus source, so timed Luava iterations skip parse and compile and start with JIT code ready while LuaJBench re-runs loadfile every iteration (a small bias, no reversal); the baseline is the LuaJ interpreter with luajc never installed and asserts are weak in the closure, OOP and concat tasks. The pre-JIT committed report gives C Lua 5.4 fib(35) at 794.76 ms and 200k coroutine switches at 43.80 ms, so the JIT is about 3.3x faster than C Lua on fib and about 5.4x slower on coroutines (derived, different runs). Fix commits of 2026-09-28/29 closed 12 conformance gaps and six core bugs.

## Caveats and trade-offs

First-party numbers with no CPU model and no committed results file for the README table; benchmarks/harness/BASELINE.txt (2026-09-14, before the JIT) had Luava behind LuaJ on 5 of 10 tasks, so the wins come from the newer tiered JIT. LuaJ interprets Lua 5.2 semantics while Luava implements 5.4, so the tasks are not exactly equivalent. Both harnesses re-evaluate the source each iteration (loadfile/eval), and every task asserts its result. Neither PUC Lua nor LuaJIT appears in the current table: the committed benchmarks/results/benchmark_report_20260911_201214.md (an early pre-JIT build) shows Luava 4x to 114x slower than C Lua 5.4. benchmarks/harness/FINDINGS.txt records C Lua 5.4.9 fib(35) at \~766 ms against a \~190 ms JIT spike on the same box, so the current JIT may beat C Lua on fib, but no head-to-head with the shipped JIT is published. Cold start is a loss: the first eval of a small script takes \~47 ms against LuaJ's 13 ms. The coroutine win (19.4x) reflects virtual threads against LuaJ's platform-thread coroutines. MPL-2.0 is file-level copyleft. Very small project (52 commits, 2 stars).

Pure-Java Lua 5.4 (register bytecode VM with a tiered JIT, sandboxing with instruction limits, Java interop). Requires JDK 21+. MPL-2.0 is file-level copyleft.

## Maintenance

Active (release 0.2.5 'Concord' on 2026-09-29, frequent commits) and MPL-2.0, so it can be embedded in proprietary JVM software while edits to Luava's own files stay open; still pre-1.0 with a single author and 2 stars.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Benchmarks table matches the record exactly (10 tasks, all won against LuaJ 3.0.1). The harness is public (benchmarks/harness/interleave.sh, Bench.java, LuaJBench.java: paired, order-flipped, taskset-pinned, java -XX:+UseG1GC -Xmx1g), but no CPU model or exact JDK version is stated and the README numbers have no committed results file, so C.
- **Verifier notes:** Numbers and metadata check out: MPL-2.0, 2 stars, 52 commits, release 0.2.5 on Maven Central, last commit 2026-09-29 on master, so active. Shortcomings: baseline is the slow LuaJ interpreter rather than PUC Lua or LuaJIT; no hardware; the repo's own committed report against C Lua (pre-JIT) shows Luava much slower; first-eval cold start loses to LuaJ.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/KienPC1234/luava/HEAD/README.md>
  - <https://github.com/KienPC1234/luava>
  - <https://github.com/KienPC1234/luava/commits>
  - <https://github.com/KienPC1234/luava/tree/master/benchmarks>
  - <https://github.com/KienPC1234/luava/tree/master/src/test/java/org/luava/benchmark>
  - <https://github.com/KienPC1234/luava/tree/master/benchmarks/results>
  - <https://github.com/KienPC1234/luava/tree/master/benchmarks/harness>
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/benchmarks/run_benchmark.sh>
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/benchmarks/results/benchmark_report_20260911_201214.md>
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/benchmarks/harness/BASELINE.txt>
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/benchmarks/harness/FINDINGS.txt>
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/benchmarks/harness/interleave.sh>
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/benchmarks/harness/Bench.java>
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/benchmarks/harness/LuaJBench.java>
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/benchmarks/lua/01_arith_loop.lua>
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/benchmarks/lua/02_fibonacci.lua>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/README.md>
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/docs/USAGE.md>
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/pom.xml>
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/benchmarks/harness/interleave.sh>
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/benchmarks/harness/Bench.java>
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/benchmarks/harness/LuaJBench.java>
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/benchmarks/harness/BASELINE.txt>
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/benchmarks/harness/FINDINGS.txt>
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/benchmarks/results/benchmark_report_20260911_201214.md>
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/benchmarks/lua/01_arith_loop.lua>
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/benchmarks/lua/02_fibonacci.lua>
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/benchmarks/lua/03_table_ops.lua>
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/benchmarks/lua/04_string_concat.lua>
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/benchmarks/lua/05_closures.lua>
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/benchmarks/lua/06_coroutines.lua>
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/benchmarks/lua/07_hash_table.lua>
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/benchmarks/lua/08_oop_metatables.lua>
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/benchmarks/lua/09_string_pattern.lua>
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/benchmarks/lua/10_sieve.lua>
  - <https://github.com/KienPC1234/luava/tree/master/src/main/java/org/luava/runtime/jit>
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/src/main/java/org/luava/runtime/jit/JitCompiler.java>
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/src/main/java/org/luava/runtime/jit/JitCodeCache.java>
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/src/main/java/org/luava/runtime/jit/JitCode.java>
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/src/main/java/org/luava/runtime/jit/JitRuntime.java>
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/src/main/java/org/luava/runtime/jit/LuaToJvmTranslator.java>
  - <https://raw.githubusercontent.com/KienPC1234/luava/master/src/main/java/org/luava/runtime/LuaState.java>
  - <https://github.com/KienPC1234/luava/issues>
  - <https://github.com/KienPC1234/luava/commits/master>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/kienpc1234/luava`) · [data/wave12/enrich/raw/github_com_kienpc1234_luava.json](../../../data/wave12/enrich/raw/github_com_kienpc1234_luava.json) (enrichment confidence 0.6)

</details>
