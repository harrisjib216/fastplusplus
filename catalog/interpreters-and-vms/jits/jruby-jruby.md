# JRuby

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Java` · `EPL-2.0 OR GPL-2.0-only OR LGPL-2.1-only` · 🟢 active

> Ruby on the JVM; with invokedynamic it beat CRuby 2.7.7 on 9 of 13 single-threaded shootout programs once warm.

| | |
|---|---|
| **Beats** | CRuby (MRI) 2.7.7p221 |
| **Claimed result** | Mixed result. JRuby with invokedynamic is faster than CRuby 2.7.7 on 9 of 13 programs (derived from page data): binarytrees 1.24 s vs 6.75 s, fannkuchredux 1.19 s vs 4.34 s, nbody 14.85 s vs 43.56 s, spectralnorm 4.09 s vs 17.18 s, mandelbrot 7.12 s vs 16.74 s; slower on fasta (26.86 s vs 18.19 s), regexdna (9.49 s vs 6.25 s), revcomp (8.78 s vs 4.2 s) and about equal on matmul (18.9 s vs 18.39 s). Default JRuby (no invokedynamic) is faster on 8 of 13 and slower on matmul, nbody, fasta, regexdna, revcomp. |
| **Workload** | Same 13 single-threaded Benchmarks-Game-style programs as the Topaz entry (JRuby 9.4.1.0 on OpenJDK 19.0.1, default flags and `-Xcompile.invokedynamic=true`), best of up to 5 runs, time measured inside the language by the shootout harness. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3800X, 80 GB DDR4-3200, Docker on Ubuntu 22.10 |
| **Compiler and flags** | jruby-dist 9.4.1.0 binary tarball from Maven Central on OpenJDK 19 (openjdk-19-jre-headless from apt; README lists openjdk 19.0.1), run as `jruby <file>` (JRuby row) and `jruby -Xcompile.invokedynamic=true -S <file>` (JRuby_InDy row) per tools/languages.rb; CRuby 2.7.7 built from source with gcc 12.2.0 (ubuntu:22.10 build-essential) using `./configure --prefix=/opt/ruby --disable-install-doc --disable-install-rdoc --disable-install-capi --with-openssl-dir=/opt/openssl1.1.1q` and `make -j4` (default CRuby optimization flags), per docker/ruby2. |
| **Adoption** | 3.9k stars |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/jruby/jruby) · [benchmark](https://github.com/kostya/jit-benchmarks) |

## Verdict

In kostya/jit-benchmarks round 1 (2023-02-28; AMD Ryzen 7 3800X, Docker on Ubuntu 22.10), JRuby 9.4.1.0 on OpenJDK 19.0.1 with -Xcompile.invokedynamic=true beat CRuby 2.7.7p221 (built from source with gcc 12.2.0, default flags) on 9 of 13 single-threaded programs, for example binarytrees 1.24 vs 6.75 s and spectralnorm 4.09 vs 17.18 s, using best in-process iteration times that exclude 1.5-2.2 s of JVM startup; it lost on fasta, regexdna and revcomp and roughly tied on matmul.

## Use it when

- Long-running, CPU-bound Ruby processes (servers, workers, batch jobs) where 1.5-2.2 s of JVM startup and JIT warm-up are amortised; object allocation and numeric loops gained most (binarytrees 5.4x, spectralnorm 4.2x, nbody 2.9x over CRuby 2.7.7, derived from page data)
- Multi-threaded Ruby that needs real parallelism on many cores (no GIL)
- Ruby code that must call Java libraries or run embedded inside a Java application
- Teams already running JVM infrastructure (monitoring, GC tuning, deployment) who want to host Ruby on it

## Skip it when

- Short scripts and CLI tools: the shootout's 'Compile T,s' column shows 1.5-2.2 s before the program starts, against 0.2-0.4 s for CRuby
- Memory-constrained hosts: JRuby rows peaked at 0.36-2.1 GB (MaxMem) versus 21-169 MB for CRuby 2.7.7 in the same runs
- Apps that depend on gems with MRI C extensions, which JRuby does not support
- String, IO and regex-heavy work: slower than CRuby 2.7.7 on fasta (26.86 vs 18.19 s), regexdna (9.49 vs 6.25 s) and revcomp (8.78 vs 4.2 s)
- If your comparison point is modern CRuby with YJIT: the cited shootout has no YJIT row and uses CRuby 2.7.7 as the baseline

## How it is fast

Ruby source is compiled to JRuby's own IR and interpreted; methods that pass a call-count threshold (jit.threshold) are compiled in a background thread to JVM bytecode (ASM), which HotSpot then optimises and inlines like Java. With compile.invokedynamic, call sites, constants and yields are bound through invokedynamic and method handles (invokebinder) with polymorphic inline caches (invokedynamic.maxpoly 6), so HotSpot can inline through Ruby's dynamic dispatch. Regexps use Joni, a Java port of Oniguruma.

## Compared with alternatives

Topaz beat CRuby 2.7.7 on 12 of 13 programs in the same run and was faster than JRuby on most of them, and TruffleRuby's GraalVM rows in that table were faster still (binarytrees 0.69 s vs 1.24 s, mandelbrot 1.34 s vs 7.12 s); pick JRuby when you need an actively maintained Ruby implementation with mature Java interop and real threads rather than the top single-threaded number.

## Integration

| | |
|---|---|
| **Form** | JVM runtime (jruby-dist tarball, jruby-complete jar or Maven artifacts for embedding) |
| **Dependencies** | a JVM (JRE 21+ for current master and 10.x); bundles ASM, Joni, jcodings, invokebinder and jnr-ffi/jffi (core/pom.rb) |
| **Minimum toolchain** | JRE 21 or newer to run current releases; JDK 21+ and Maven wrapper to build (BUILDING.md); the 9.4 line measured here ran on OpenJDK 19 |
| **Platforms** | any OS/CPU with a supported JVM; FFI uses jffi's bundled native stubs |
| **Thread safety** | Ruby threads run in parallel on JVM threads with no global interpreter lock (README); thread-safety guarantees of core collections are not documented in the files read |
| **Drop-in for the baseline** | partial: runs the same Ruby source (9.4 targets Ruby 3.1.7, master targets Ruby 4.0.0 per default.build.properties) but no MRI C extensions, and startup/memory behaviour differ sharply |

## Gotchas

- The invokedynamic default depends on the release: on the 9.4 branch calculateInvokedynamicDefault() returns false, while 10.0 and master set compile.invokedynamic to true; the shootout's JRuby_InDy row is therefore the one that approximates current defaults, and the plain 'JRuby' row (9.4 default, indy off) also loses on matmul (27.1 vs 18.39 s) and nbody (51.32 vs 43.56 s)
- Harness asymmetry in kostya/jit-benchmarks: times come from Time.now inside the script, after a 'started' marker, as the best of up to 5 in-process iterations, so JVM boot and most JIT warm-up are excluded; but the stdin-fed programs (knucleotide, regexdna, revcomp) are run with args [1], one cold iteration per process, so two of JRuby's three losses are measured without warm-up, and some rows (CRuby and default JRuby on nbody and brainfuck) completed only 1 iteration inside the timeout
- No -Xmx or other JVM heap flags were passed (tools/languages.rb), so the 0.36-2.1 GB MaxMem figures reflect default JVM heap sizing on an 80 GB host; footprint under a capped heap was not measured
- The wiki's --dev startup flag turns off the JIT (compile.mode=OFF) and invokedynamic, and the wiki notes the JIT can slow very short runs; benchmark with the same flags you deploy with

## Known shortcomings

- kostya/jit-benchmarks round 1 numbers: mixed result, slower than CRuby on fasta, regexdna and revcomp; the baseline is CRuby 2.7.7 with no YJIT row; in-process timing leaves out JVM startup; JRuby uses 0.8-2.1 GB RAM on these programs.
- Enricher: invokedynamic is off by default in 9.4 (calculateInvokedynamicDefault returns false) and on in 10.0 and master, so the JRuby_InDy row is closest to the current default. kostya/jit-benchmarks asymmetry: stdin programs (knucleotide, regexdna, revcomp) run one cold iteration while the others report the best of up to 5 warm in-process iterations with Time.now inside the script and JVM startup (1.5-2.2 s) excluded, so 2 of the 3 InDy losses were timed cold. No -Xmx set on the 80 GB host, so the 0.36-2.1 GB MaxMem figures are default heap sizing.

## Caveats and trade-offs

Mixed evidence: JRuby loses to CRuby on several programs (fasta, regexdna, revcomp with invokedynamic; also matmul and nbody without it), so this is not a uniform speedup. Baseline is CRuby 2.7.7; against the same run's Ruby 3.2.1 interpreter row JRuby_InDy is faster on 10 of 13 and still slower on fasta, regexdna and revcomp (derived from page data). The shootout has no YJIT row: its base image installs no Rust toolchain, which Ruby 3.2's YJIT needs at build time. Times are measured inside the program after a 'started' marker and the table reports the best of up to 5 iterations, so JVM startup (shown in the separate 'Compile T,s' column, 1.6-2.2 s) and part of the warm-up are excluded, which favours JRuby; several CRuby baseline rows (brainfuck, knucleotide, nbody, regexdna, revcomp) completed only 1 iteration inside the time limit. JRuby uses 0.8-2.1 GB of RAM on these programs versus tens of MB for CRuby. The shootout states its programs are chosen to be simplest, single-thread and without low-level hacks; one machine, one round, single benchmark author. Found by harvesting rows from a shootout; JRuby's own README only says it can be used 'as a faster version of Ruby' and gives no numbers. Java project, not C++.

Runs on the JVM (repo page: current branches need JRE 21 or newer), so JVM startup and memory apply: in the same shootout JRuby used about 1.2-2.1 GB on binarytrees versus 44.6 MB for CRuby. Repo page lists no global interpreter lock and tight Java integration.

## Maintenance

Actively maintained (last commit 2026-10-03, master is 10.1.3.0-SNAPSHOT) under EPL-2.0/GPL-2.0/LGPL-2.1; usable as a production Ruby runtime, but the cited numbers are for the older 9.4.1.0 release against an end-of-life CRuby 2.7.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now A.
- **Tier reason:** Every JRuby, JRuby_InDy and Ruby2 (CRuby 2.7.7p221) time in the record matches the round-1 (2023-02-28) tables of the kostya/jit-benchmarks README. The setup is fully public: &lt;bench&gt;/test.rb sources shared by both runtimes, run commands in tools/languages.rb (`jruby <file>` and `jruby -Xcompile.invokedynamic=true -S <file>`), runtime builds in docker/jruby, docker/java and docker/ruby2 (gcc 12.2.0 on ubuntu:22.10), and the CPU (AMD Ryzen 7 3800X), consistent with the A tiers given to php-src, cython, codon and graalpython on the same suite.
- **Verifier notes:** All claimed numbers and the 9-of-13 (InDy) and 8-of-13 (default) counts check out against the README tables; outputs are validated by the suite's check step (tools/cli.rb check_exact) and JRuby is not on any expected_check_failed list. Metadata verified: EPL-2.0 OR GPL-2.0 OR LGPL-2.1 per COPYING, 3.9k stars, not a fork, last commit 2026-10-03 on master. Shortcomings to record: mixed wins, old CRuby baseline, startup excluded by in-process timing, high memory.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** comparison against CRuby 3.x with YJIT including startup; uniform warm or cold timing across programs
- **Pages the verifier opened:**
  - <https://github.com/jruby/jruby>
  - <https://github.com/jruby/jruby/commits>
  - <https://raw.githubusercontent.com/jruby/jruby/HEAD/COPYING>
  - <https://raw.githubusercontent.com/jruby/jruby/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/languages.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/cli.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/benchmarks.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker-compose.yml>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/base>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/ruby2>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/ruby3>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/java>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/jruby>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/topaz>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/dc>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/binarytrees/test.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/revcomp/test.rb>
- **Sources the enricher read:**
  - <https://github.com/jruby/jruby>
  - <https://raw.githubusercontent.com/jruby/jruby/HEAD/README.md>
  - <https://raw.githubusercontent.com/jruby/jruby/HEAD/COPYING>
  - <https://raw.githubusercontent.com/jruby/jruby/HEAD/BUILDING.md>
  - <https://raw.githubusercontent.com/jruby/jruby/HEAD/VERSION>
  - <https://raw.githubusercontent.com/jruby/jruby/HEAD/default.build.properties>
  - <https://raw.githubusercontent.com/jruby/jruby/jruby-9.4/default.build.properties>
  - <https://raw.githubusercontent.com/jruby/jruby/HEAD/core/pom.rb>
  - <https://raw.githubusercontent.com/jruby/jruby/HEAD/core/src/main/java/org/jruby/util/cli/Options.java>
  - <https://raw.githubusercontent.com/jruby/jruby/jruby-9.4/core/src/main/java/org/jruby/util/cli/Options.java>
  - <https://raw.githubusercontent.com/jruby/jruby/jruby-10.0/core/src/main/java/org/jruby/util/cli/Options.java>
  - <https://github.com/jruby/jruby/wiki/PerformanceTuning>
  - <https://github.com/jruby/jruby/wiki/Improving-startup-time>
  - <https://github.com/jruby/jruby/wiki/C-Extension-Alternatives>
  - <https://github.com/jruby/jruby/issues?q=is%3Aissue+is%3Aopen+label%3Aperformance>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/languages.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/cli.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/runner.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/tools/benchmarks.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/jruby>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/java>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/ruby2>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/ruby3>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/docker/base>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/binarytrees/test.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/fasta/test.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/revcomp/test.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/regexdna/test.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/matmul/test.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/nbody/test.rb>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/jruby/jruby`) · [data/wave12/enrich/raw/github_com_jruby_jruby.json](../../../data/wave12/enrich/raw/github_com_jruby_jruby.json) (enrichment confidence 0.8)

</details>
