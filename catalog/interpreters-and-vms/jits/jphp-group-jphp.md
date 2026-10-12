# JPHP

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Java` · `Apache-2.0` · 🔴 abandoned

> PHP 7.1+ compiled to JVM bytecode; claims 2.5x over PHP 5.6 and 1.1x over 7.0, but is 13% slower than 7.4.

| | |
|---|---|
| **Beats** | PHP 5.6, PHP 7.0 and PHP 7.4 (Zend engine) |
| **Claimed result** | README feature line: JIT (\~2.5x faster PHP 5.6, \~1.1x faster PHP 7.0, \~13% slower than PHP 7.4). |
| **Workload** | Benchmark scripts run through './gradlew bench' on JPHP and 'php -f bench/src/bench.php' on PHP; the README states only the summary ratios. |
| **Metric** | throughput |
| **Adoption** | 1.7k stars |
| **Last commit** | 2020-07-07 |
| **Links** | [repository](https://github.com/jphp-group/jphp) · [benchmark](https://github.com/jphp-group/jphp) |

## Verdict

The only published result is a first-party README line: about 2.5x faster than PHP 5.6, about 1.1x faster than PHP 7.0 and about 13% slower than PHP 7.4 on the repo's own suite of 21 synthetic micro-benchmarks (bench/src). No JVM version, PHP build or opcache setting, hardware, or per-benchmark numbers are given.

## Use it when

- Embedding PHP-syntax scripting in a Java/JVM application that needs to call Java classes directly.
- Desktop or GUI tools written in PHP on JavaFX/SWT, which is what the DevelNext IDE was built on.
- Legacy PHP 5.6-era CPU-bound scripts where a JVM deployment is acceptable and the claimed \~2.5x over PHP 5.6 matters.
- Long-running JVM processes, such as its own HTTP server or multithreaded workers, where JIT warm-up is amortised.

## Skip it when

- Any deployment that can run PHP 7.4 or 8.x: by its own README JPHP is about 13% slower than PHP 7.4, and it was never compared with PHP 8's opcache JIT.
- Code that depends on Zend extensions (curl, PCRE-specific runtime, mbstring and the like): the project says it does not plan to implement Zend's runtime libraries.
- PHP 8 syntax or semantics: support stops at PHP 7.4 features, and some of those are partial (typed properties without references).
- Production use needing fixes: no commits since 2020-07-07 and 40 open issues, including crashes (#414 ClassCastException, #403 and #396 parse crashes) and wrong arithmetic (#422 intdiv, #419 negative power).
- Short CLI scripts, where JVM startup and warm-up outweigh any steady-state gain.

## How it is fast

jphp-core walks the PHP AST and emits JVM bytecode with ASM 7.3. Values are boxed Memory objects (LongMemory, DoubleMemory, StringMemory, ReferenceMemory), but the compiler tracks INT, DOUBLE and constant stack items so arithmetic on known types skips boxing. Calls to built-ins marked immutable are constant-folded at compile time, and native functions are bound by direct INVOKESTATIC calls. The 'JIT' in the README is HotSpot's JIT working on that bytecode; JPHP has no JIT of its own.

## Compared with alternatives

Pick JPHP over PHP JIT (php-src opcache JIT) or HHVM only when you need PHP syntax inside a JVM with direct Java interop. For raw speed, PHP 8 with the opcache JIT is maintained and faster than the PHP 7.4 that JPHP already trails.

## Integration

| | |
|---|---|
| **Form** | module (Java jars org.develnext.jphp:jphp-\* via Maven/Gradle, or jppm packages) |
| **Dependencies** | JVM; jphp-runtime, jphp-core (ASM 7.3.1); optional extensions (jphp-zend-ext for Zend-style functions, JSON, HTTP server, SQL, GUI) |
| **Minimum toolchain** | Java 8 (sourceCompatibility 1.8); the build uses an old Gradle with `compile` configurations and Shadow plugin 4.0.3 |
| **Platforms** | Any JVM platform (Linux, Windows, macOS); Android through the separate jphp-android project |
| **Thread safety** | Ships php\lang\Thread and isolated Environment objects for multithreading; per-object thread-safety rules are not documented in what was read |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness asymmetry: StringBenchmark runs a different code path per engine, php\lib\Str methods on JPHP and strlen/strpos/strtoupper/str_replace on Zend, so the string part of the ratio does not compare like with like.
- Harness design: 21 tiny micro-benchmarks (for example fib(1..5) per call, 8^4 empty loops) are each timed with microtime() around a single call, 10,000 times. Results are never used, so HotSpot is free to drop dead work. JVM warm-up is included. No per-benchmark times, JVM version, PHP build or opcache setting, or hardware are published.
- UndefinedBenchmark reads an undefined constant, property and array key 8 times per run. On Zend PHP 7.2-7.4 the constant read raises E_WARNING, so with default CLI display settings Zend's time includes printing warnings; on PHP 8 it is a fatal Error. The error settings used are not documented.
- The README's `./gradlew bench` command has no matching task in the root build.gradle, jppm.gradle, ext-template.gradle or the sandbox, packager and runtime build files; bench/ is a jppm package that settings.gradle does not include. Strings are UTF-16 Java strings, so byte-oriented string code can behave differently from Zend.

## Known shortcomings

- Only ratios in the README, about 13% slower than PHP 7.4 and predating the PHP 8 JIT; abandoned (last commit 2020-07-07). Off-baseline (PHP); Java.
- Enricher: StringBenchmark runs different code per engine (php\lib\Str against strlen and strpos), the microbenchmarks are tiny with results discarded and no per-benchmark data, UndefinedBenchmark triggers E_WARNING on Zend 7.2+ (fatal on PHP 8), and the README's './gradlew bench' task does not exist in the build files.

## Caveats and trade-offs

Ratios only, no hardware or workload detail, and the README itself says it is slower than PHP 7.4 (the numbers predate PHP 8 and its JIT). Last commit 2020-07-07. Listed for completeness as a PHP-on-JVM claim, not as a win over PyPy, LuaJIT, V8 or HotSpot.

PHP 7.1+ language implementation on the JVM (PHP compiled to JVM bytecode and then JIT-compiled by the JVM), with Java interop, UTF-16 strings, threads and JavaFX/SWT GUI extensions. Not drop-in for PHP extensions.

## Maintenance

Abandoned: last commit 2020-07-07, and a 2024 issue asking why it stalled has no maintainer reply. It is Apache-2.0 and usable for JVM-embedded PHP 7-style scripting, but it is only faster than obsolete Zend versions, and its benchmark has an asymmetric string test.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The README feature line gives only first-party summary ratios against Zend PHP (\~2.5x faster than PHP 5.6, \~1.1x faster than PHP 7.0, \~13% slower than PHP 7.4). Benchmark scripts are public (bench/src/bench.php with \~22 micro-benchmarks, run via ./gradlew bench), but no per-benchmark numbers, JVM or PHP build details, or hardware are given, so C.
- **Verifier notes:** Numbers and metadata check out (Apache-2.0, 1.7k stars, last commit 2020-07-07 on master, not archived, so abandoned). Shortcoming: slower than PHP 7.4 by its own README and predates PHP 8 and its JIT, so it beats only obsolete Zend versions; ratios only, no per-benchmark data, hardware or flags.
- **Pages the verifier opened:**
  - <https://github.com/jphp-group/jphp>
  - <https://github.com/jphp-group/jphp/commits>
  - <https://raw.githubusercontent.com/jphp-group/jphp/HEAD/README.md>
  - <https://raw.githubusercontent.com/jphp-group/jphp/HEAD/bench/src/bench.php>
- **Sources the enricher read:**
  - <https://github.com/jphp-group/jphp>
  - <https://raw.githubusercontent.com/jphp-group/jphp/HEAD/README.md>
  - <https://raw.githubusercontent.com/jphp-group/jphp/HEAD/build.gradle>
  - <https://raw.githubusercontent.com/jphp-group/jphp/HEAD/settings.gradle>
  - <https://raw.githubusercontent.com/jphp-group/jphp/HEAD/jppm.gradle>
  - <https://raw.githubusercontent.com/jphp-group/jphp/HEAD/exts/ext-template.gradle>
  - <https://raw.githubusercontent.com/jphp-group/jphp/HEAD/sandbox/build.gradle>
  - <https://raw.githubusercontent.com/jphp-group/jphp/HEAD/packager/build.gradle>
  - <https://raw.githubusercontent.com/jphp-group/jphp/HEAD/jphp-runtime/build.gradle>
  - <https://raw.githubusercontent.com/jphp-group/jphp/HEAD/jphp-core/build.gradle>
  - <https://raw.githubusercontent.com/jphp-group/jphp/HEAD/bench/package.php.yml>
  - <https://raw.githubusercontent.com/jphp-group/jphp/HEAD/bench/src/bench.php>
  - <https://github.com/jphp-group/jphp/tree/master/bench/src/benchmarks>
  - <https://raw.githubusercontent.com/jphp-group/jphp/HEAD/bench/src/benchmarks/Benchmark.php>
  - <https://raw.githubusercontent.com/jphp-group/jphp/HEAD/bench/src/benchmarks/FibonacciBenchmark.php>
  - <https://raw.githubusercontent.com/jphp-group/jphp/HEAD/bench/src/benchmarks/LoopBenchmark.php>
  - <https://raw.githubusercontent.com/jphp-group/jphp/HEAD/bench/src/benchmarks/MathBenchmark.php>
  - <https://raw.githubusercontent.com/jphp-group/jphp/HEAD/bench/src/benchmarks/ArrayBenchmark.php>
  - <https://raw.githubusercontent.com/jphp-group/jphp/HEAD/bench/src/benchmarks/StringBenchmark.php>
  - <https://raw.githubusercontent.com/jphp-group/jphp/HEAD/bench/src/benchmarks/UndefinedBenchmark.php>
  - <https://github.com/jphp-group/jphp/tree/master/jphp-core/src/org/develnext/jphp/core/compiler/jvm/statement>
  - <https://raw.githubusercontent.com/jphp-group/jphp/HEAD/jphp-core/src/org/develnext/jphp/core/compiler/jvm/statement/ExpressionStmtCompiler.java>
  - <https://github.com/jphp-group/jphp/commits/master>
  - <https://github.com/jphp-group/jphp/issues>
  - <https://github.com/jphp-group/jphp/issues?q=is%3Aissue+performance>
  - <https://github.com/jphp-group/jphp/issues/430>
  - <https://github.com/jphp-group/jphp/issues/379>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/jphp-group/jphp`) · [data/wave12/enrich/raw/github_com_jphp_group_jphp.json](../../../data/wave12/enrich/raw/github_com_jphp_group_jphp.json) (enrichment confidence 0.65)

</details>
