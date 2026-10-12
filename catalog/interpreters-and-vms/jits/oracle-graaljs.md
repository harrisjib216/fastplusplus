# Graal.js (GraalJS)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Java` · `UPL-1.0` · 🟢 active

> Oracle's JavaScript and Node.js engine in Java on Truffle/Graal; beat Node.js 6 on 2016 peak benchmarks, loses to current V8.

| | |
|---|---|
| **Beats** | Node.js (V8) |
| **Claimed result** | Are We Fast Yet performance report (https://github.com/smarr/are-we-fast-yet/blob/master/docs/performance.md, generated 2016-06-20, peak performance after warmup, runtime factor over Java 1.8.0_91, lower is better), geomean: Graal.js 2.23 (median 2.13, sd 2.82, max 12.22) vs Node.js 2.89 (median 2.54, sd 3.33, max 12.25), about 1.3x lower geomean runtime (derived from page data). Per benchmark Graal.js is faster on 8 of 14 (Bounce 1.26 vs 12.25, CD, DeltaBlue, List, NBody, Richards, Storage, Towers), slower on 5 (Havlak 12.22 vs 10.24, Json 1.60 vs 1.14, Mandelbrot, Permute 3.06 vs 2.13, Queens) and tied on Sieve (3.61). Excluding the Bounce outlier the geomeans are 2.33 vs 2.58, about 1.11x (derived from page data). Counter-evidence: kostya/jit-benchmarks round 1 (2023-02-28, AMD Ryzen 7 3800X, https://github.com/kostya/jit-benchmarks) has Graal.js 22.3.1 (graalnode, node 16.18.1), native and JVM modes, slower than Node.js 19.7.0 on all 13 benchmarks (e.g. brainfuck 76.16 s native / 52.08 s JVM vs 5.88 s, nbody 4.82 / 5.59 vs 0.82, regexdna 10.0 / 6.68 vs 1.06, matmul 0.51 / 0.30 vs 0.26). |
| **Workload** | Are We Fast Yet suite (CD, DeltaBlue, Havlak, Json, Richards, Bounce, List, Mandelbrot, NBody, Permute, Queens, Sieve, Storage, Towers) after warmup, peak performance, runtime normalised to Java 1.8.0_91. |
| **Metric** | throughput |
| **Compiler and flags** | AWFY report: Java 1.8.0_91 baseline; Graal.js and Node.js versions and flags not stated on the page (the DLS'16 paper used Node.js 6.2, per a search snippet). kostya/jit-benchmarks: graalnode 22.3.1 (node 16.18.1) vs nodejs 19.7.0, run commands in tools/languages.rb, Docker images in docker/. |
| **Adoption** | about 2.0k stars |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/oracle/graaljs) · [benchmark](https://github.com/smarr/are-we-fast-yet/blob/master/docs/performance.md) |

## Verdict

The only measured win is the Are We Fast Yet report of 2016-06-20: peak performance after warmup, runtime normalised to Java 1.8.0_91, Graal.js geomean 2.23 vs Node.js 2.89 (Node.js 6.2 per the DLS'16 paper snippet; CPU and flags not stated), faster on 8 of 14 benchmarks. The independent, reproducible kostya/jit-benchmarks round 1 (AMD Ryzen 7 3800X, Docker on Ubuntu 22.10, GraalVM CE 22.3.1 graalnode vs Node.js 19.7.0) has GraalJS slower on all 13 programs in both native and JVM modes.

## Use it when

- A Java application that must embed modern JavaScript (ECMAScript 2026) with direct Java interop, for example replacing Nashorn or Rhino.
- Long-running, warmed-up, object-oriented JavaScript where the 2016 Are We Fast Yet peak numbers put Graal.js ahead of Node.js 6.2 (DeltaBlue 2.10 vs 3.93, Richards 2.91 vs 4.12, Storage 0.98 vs 2.03 runtime factor over Java).
- Polyglot processes that mix JavaScript with other Truffle languages (Python, Ruby, WebAssembly) and want one compiler and shared tooling (--cpusampler, --memtracer).
- Numeric kernels where the 2023 kostya run shows it close to Node.js 19.7.0 in JVM mode: mandelbrot 0.48 vs 0.46 s, matmul 0.30 vs 0.26 s, spectralnorm 0.13 vs 0.11 s.

## Skip it when

- As a faster replacement for current V8/Node.js: in kostya/jit-benchmarks round 1 (2023) GraalJS 22.3.1 lost all 13 benchmarks to Node.js 19.7.0, e.g. brainfuck 52.08 s (JVM) and 76.16 s (native) vs 5.88 s, nbody 5.59/4.82 vs 0.82 s.
- Short-lived scripts and CLIs: in the kostya run the time before the first benchmark line ('Compile T') was 1.99-4.8 s in JVM mode and 0.47-3.27 s native vs 0.17-0.64 s for Node.js, and the FAQ warns the first iterations are slower than on other engines.
- Memory-constrained deployments: max RSS in the same suite was 0.73-2.3 GB (JVM) and 0.33-1.2 GB (native) vs 45-625 MB for Node.js.
- Regex- and string-heavy work: regexdna 6.68-10.0 s vs 1.06 s, revcomp 7.28-8.31 vs 3.15 s, knucleotide 9.7-13.67 vs 5.21 s; issue #290 reports simple character-set regexes slower than Node 20.1.
- C++ hosts that want a V8-style embedding API, or code from untrusted sources (SECURITY.md: execution of untrusted or adversarial code is not supported).

## How it is fast

JavaScript is executed by a self-specializing AST interpreter built with Truffle; hot functions are compiled to machine code by the Graal compiler through partial evaluation of the specialized interpreter, with deoptimization back to the interpreter when speculation fails. Peak speed therefore depends on having the Graal JIT available (GraalVM JDK, Oracle JDK or OpenJDK with Graal via JVMCI) and on giving it enough warmup; on a stock JVM without Graal it runs interpreter-only.

## Compared with alternatives

Pick GraalJS only when the code must stay JavaScript inside a JVM process with Java interop; the catalogued JIT siblings that beat Node.js on kostya/benchmarks (Chez Scheme, Julia, .NET RyuJIT, Dart VM) require switching languages, while GraalJS keeps JavaScript but runs slower than Node.js/V8 in current measurements.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | GraalVM polyglot SDK and Truffle runtime (Maven org.graalvm.polyglot:polyglot plus js or js-community); the Graal JIT compiler (GraalVM JDK, or Oracle JDK/OpenJDK with Graal on the module path) for compiled performance; standalone builds bundle everything |
| **Minimum toolchain** | JDK 21 or later (per the FAQ); GraalVM JDK recommended |
| **Platforms** | Binaries for Linux x64 and AArch64, macOS AArch64, Windows x64 (macOS x86-64 builds removed in 25.1.3); the Java engine runs on any compatible JVM, interpreter-only without Graal |
| **Thread safety** | Share-nothing: a JavaScript Context and its objects may be used by only one thread at a time (synchronised hand-off allowed); Java objects can be shared across threads; Node.js Worker threads supported |
| **Drop-in for the baseline** | partial — the node standalone runs unmodified Node.js applications and most npm packages, but binary addons built for V8 may need recompiling, and Java embedders use the polyglot Context API rather than any V8 API |

## Gotchas

- Benchmark artefacts on both sides of the evidence: the 2016 AWFY geomean edge rests mostly on Bounce (Node.js 12.25 vs Graal.js 1.26), whose June 2016 JavaScript hot loop was balls.forEach(closure) mutating a captured counter (rewritten to for-of in 2022), an engine-version-specific weakness of Node.js 6 rather than a general Graal.js advantage; without Bounce the geomean gap is 2.33 vs 2.58.
- kostya/jit-benchmarks reports the best of up to 5 in-process iterations timed in-language after a 'started' marker, so JVM startup is excluded (shown as 'Compile T'), but GraalJS completed only 2 (native) and 3 (JVM) brainfuck iterations before the 190 s timeout, knucleotide/regexdna/revcomp run a single iteration (warmup included), it used GraalVM CE 22.3.1 rather than Oracle GraalVM, and the JS mandelbrot program is marked expected_check_failed for node, graalnode and graalnode_jvm.
- The default standalone is a Native Image build, which the FAQ says may have lower peak throughput than the -jvm build; on a stock JDK without the Graal compiler it silently drops to interpreter-only mode (with a WarnInterpreterOnly warning) and is far slower.
- Creating a new Context per request is slow unless one Engine is shared and Source objects cached; and Oracle's default artifacts (Maven js, standalones without -community) are under the GraalVM Free Terms and Conditions, only the -community builds and source are UPL-1.0.

## Known shortcomings

- Downgraded: the 2016 Are We Fast Yet geomean win over Node comes mostly from the Bounce outlier (1.11x without it), and kostya/jit-benchmarks 2023 shows Graal.js 22.3.1 slower than Node 19.7.0 on 13 of 13 programs, so it is not faster now. Java, not C++.
- Enricher: the 2016 AWFY Bounce outlier (Node.js 12.25 vs 1.26) came from a June 2016 bounce.js hot loop using balls.forEach with a closure mutating a captured counter (rewritten to for-of in 2022), a Node.js 6 weakness rather than a Graal.js advantage. In kostya 2023 GraalJS 22.3.1 (GraalVM CE) loses 13 of 13 to Node.js 19.7.0, its brainfuck finished only 2 of 3 of 5 iterations before the 190 s timeout, and JS mandelbrot is marked expected_check_failed for node and graalnode.

## Caveats and trade-offs

The only measured win is from June 2016 (early Graal.js vs Node.js 6.2), and its geomean edge is driven by Bounce, where Node.js was 12.25x Java; without Bounce the gap is about 1.11x. Node.js is still faster on 5 of 14 AWFY benchmarks (Graal.js has the better median, 2.13 vs 2.54). The independent, reproducible kostya/jit-benchmarks round 1 (2023) shows Graal.js 22.3.1 slower than Node.js 19.7.0 on all 13 benchmarks, often by 2x to 13x, so current Graal.js should not be presented as faster than V8. Peak performance only; startup and warmup, where Graal.js is known to be weak, are excluded. The AWFY report states no CPU. The community distribution is UPL-1.0 but Oracle's non-community builds are under the GraalVM Free Terms and Conditions.

Runs on the JVM (Java and Truffle/Graal compiler); long warmup and high memory; native-image distribution exists; Java interoperability; JavaScript only, no V8 embedding API from C++.

## Maintenance

Actively developed by Oracle (last commit 2026-10-05, Node.js base 24.18.1 in 25.3.4, UPL-1.0 for community builds) and usable today as a Java-embedded JavaScript engine, but the speed claim against V8 is a 2016 peak-performance result driven by one Node.js 6 outlier, and the 2023 independent run shows it 1.1x to 13x slower than Node.js.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): downgrade; tier before verification B, tier now B.
- **Tier reason:** The Are We Fast Yet performance report (suite of the peer-reviewed DLS'16 paper by Marr, Daloze and Mössenböck) shows the record's Graal.js and Node.js geomean, median, sd and max values exactly, so the measured win stays tier B; the report states neither CPU nor flags. The claim is overstated, hence downgrade: the geomean edge comes mostly from one Node.js outlier (Bounce), and the newer, fully reproducible kostya/jit-benchmarks round 1 (2023) has Graal.js slower than Node.js on all 13 benchmarks.
- **Verifier notes:** All AWFY numbers in the record are on the page and belong to the Graal.js row; hardware is unstated on the page and the paper (stefan-marr.de) is EGRESS_BLOCKED, versions taken from a WebSearch snippet only. Main shortcoming to record: not faster than V8 in current measurements (kostya/jit-benchmarks 2023: slower on 13 of 13), and the 2016 geomean win rests mostly on one outlier. Metadata checked on github.com: UPL-1.0, 2.0k stars, not archived, last commit 2026-10-05.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/smarr/are-we-fast-yet/HEAD/docs/performance.md>
  - <https://raw.githubusercontent.com/smarr/are-we-fast-yet/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/README.md>
  - <https://github.com/oracle/graaljs>
  - <https://github.com/oracle/graaljs/commits/master>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/oracle/graaljs/HEAD/README.md>
  - <https://raw.githubusercontent.com/oracle/graaljs/HEAD/docs/user/FAQ.md>
  - <https://raw.githubusercontent.com/oracle/graaljs/HEAD/docs/user/Multithreading.md>
  - <https://raw.githubusercontent.com/oracle/graaljs/HEAD/docs/user/RunOnJDK.md>
  - <https://raw.githubusercontent.com/oracle/graaljs/HEAD/docs/user/JavaScriptCompatibility.md>
  - <https://raw.githubusercontent.com/oracle/graaljs/HEAD/docs/user/Options.md>
  - <https://raw.githubusercontent.com/oracle/graaljs/HEAD/docs/user/README.md>
  - <https://raw.githubusercontent.com/oracle/graaljs/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/oracle/graaljs/HEAD/SECURITY.md>
  - <https://github.com/oracle/graaljs/issues?q=is%3Aissue+performance+slower+than+node>
  - <https://github.com/oracle/graaljs/issues/74>
  - <https://github.com/oracle/graaljs/issues/360>
  - <https://github.com/oracle/graaljs/tree/master/graal-nodejs/deps/v8/src>
  - <https://raw.githubusercontent.com/smarr/are-we-fast-yet/HEAD/docs/performance.md>
  - <https://raw.githubusercontent.com/smarr/are-we-fast-yet/HEAD/README.md>
  - <https://raw.githubusercontent.com/smarr/are-we-fast-yet/HEAD/benchmarks/JavaScript/bounce.js>
  - <https://raw.githubusercontent.com/smarr/are-we-fast-yet/HEAD/benchmarks/JavaScript/som.js>
  - <https://github.com/smarr/are-we-fast-yet/commits/master/benchmarks/JavaScript/bounce.js>
  - <https://raw.githubusercontent.com/smarr/are-we-fast-yet/9e533ca/benchmarks/JavaScript/bounce.js>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/languages.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/cli.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/runner.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/benchmarks.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/dc>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/graalvm>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/graalnode>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/nodejs>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/nbody/test.js>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/brainfuck/test.js>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/oracle/graaljs`) · [data/wave12/enrich/raw/github_com_oracle_graaljs.json](../../../data/wave12/enrich/raw/github_com_oracle_graaljs.json) (enrichment confidence 0.75)

</details>
