# TruffleRuby

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Java/Ruby (GraalVM Truffle)` · `EPL-2.0 OR GPL-2.0-only OR LGPL-2.1-only` · 🟢 active

> Ruby 4.0 implementation on GraalVM/Truffle with a partial-evaluation JIT; peak-throughput wins over CRuby and YJIT on CPU-bound pure-Ruby code.

| | |
|---|---|
| **Beats** | CRuby 4.0.6 (MRI interpreter), also CRuby with --jit (YJIT) |
| **Claimed result** | Are We Fast Yet 2016 (runtime factor over Java 1.8.0_91): geomean 2.36 vs Node.js 2.89, faster than Node on only 6 of 14 benchmarks, the edge mostly from Node's Bounce outlier. kostya/benchmarks against CRuby 4.0.6: about 16x on bench.b, 12x on Matmul, 2x on Primes, but about 1.9x slower on Base64 and about 10x slower on Json (10.618 s vs 1.031 s); slower than LuaJIT and PyPy on 4 of 6 shared tests (derived from page data). |
| **Workload** | kostya/benchmarks: Brainfuck bench.b, matmul, primes, JSON, base64, run as the same Ruby scripts under each Ruby implementation. |
| **Metric** | throughput |
| **Hardware** | Intel(R) Xeon(R) E-2324G, Docker (Debian forky/sid) per README Environment section; base image and interpreter builds in docker/Dockerfile |
| **Compiler and flags** | TruffleRuby 34.0.1 native and JVM release tarballs vs CRuby 4.0.6 built with CC=clang ./configure --enable-yjit (docker/Dockerfile); scripts run via `truffleruby`, `ruby`, `ruby --jit`. |
| **Adoption** | 3.2k stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/oracle/truffleruby) · [benchmark](https://github.com/kostya/benchmarks) |

## Verdict

On kostya/benchmarks (2026-07-19, Intel Xeon E-2324G, Docker, same Ruby scripts, Oracle GraalVM builds of TruffleRuby 34.0.1 vs CRuby 4.0.6 built with clang and --enable-yjit) TruffleRuby was about 16x faster than CRuby on bench.b (4.645 s JVM vs 74.107 s), about 12x on Matmul (17.667 s vs 211.868 s) and about 2x on Primes (0.871 s vs 1.794 s), but about 1.9x slower on Base64 and about 10x slower on Json (derived from page data). The peer-reviewed Are We Fast Yet suite (2016 peak performance, normalised to Java 1.8.0_91) put JRuby+Truffle at a 2.36 geomean vs 45.62 for MRI, about 19x (derived from page data).

## Use it when

- Long-running, CPU-bound pure-Ruby code (interpreters, numeric loops, matrix code) where warm-up seconds do not matter: on kostya/benchmarks it ran bench.b in 4.645 s vs 74.107 s for CRuby 4.0.6 and 30.807 s for CRuby with YJIT.
- Multi-threaded Ruby that is CPU-bound, since Ruby threads run in parallel (C extensions still take a global extension lock unless marked thread-safe).
- Polyglot or JVM deployments that want to call Java, JavaScript, Python or WebAssembly from Ruby in one process (JVM Standalone).
- Servers or batch jobs with hundreds of MiB of headroom per process, where peak throughput matters more than RSS.

## Skip it when

- Short scripts, CLIs, or one-shot work that never warms up: on kostya's single-pass Json test it took 10.618 s (JVM) vs 1.031 s for CRuby, and on Base64 3.505 s (JVM) and 8.789 s (Native) vs 1.861 s for CRuby.
- Memory-constrained hosts: base RSS about 197 MiB (Native) or 355 MiB (JVM) vs 12 MiB for CRuby on bench.b, and the Json test peaked at 482.80 + 2212.51 MiB on JVM vs 122 + 212 MiB for CRuby.
- Code that needs fork, Ractor, callcc or RubyVM internals (not supported), heavy ObjectSpace, set_trace_func or exception/backtrace-heavy control flow (documented as slow), or fiber-heavy schedulers (fibers are OS threads).
- Windows or macOS on Intel: supported platforms are Linux x86-64 and Linux/macOS AArch64.
- Workloads dominated by YAML, Marshal, regex anchors or certain gems: open performance issues report Psych.load slow (#2089), Marshal.load glacial when cold (#2085), Jekyll slower than MRI after warm-up (#2363) and a primes-utils run at about 159 s vs about 43 s on Ruby 4.0 with YJIT (#4093).

## How it is fast

The interpreter is a self-specializing AST interpreter written with the Truffle framework; hot methods are compiled by the Graal compiler through partial evaluation, which inlines aggressively and removes Ruby's dynamism once the program reaches a stable state (the project's own performance guide says it also deletes unneeded computation). Threads run in parallel with no global interpreter lock. Release 40.0.0 also moved POSIX calls and C extensions onto the Java Foreign Function and Memory API (about 100 ns to about 12 ns per native call per the changelog).

## Compared with alternatives

Pick it over YJIT (CRuby) when peak throughput on long-running CPU-bound Ruby matters more than memory, warm-up and full MRI compatibility (on kostya it beat CRuby --jit on bench.b, Matmul and Primes but lost badly on Json and Base64); pick Spinel or Lightstorm only for AOT-compiled programs that fit their Ruby subsets, since TruffleRuby runs full Ruby and gems.

## Integration

| | |
|---|---|
| **Form** | language runtime (Native or JVM standalone binary tarball; Maven artifact for embedding in Java) |
| **Dependencies** | make, gcc and g++ for building C extensions; system libssl and CA certificates for the openssl extension; zlib; a UTF-8 locale |
| **Minimum toolchain** | Standalones bundle their own runtime; embedding TruffleRuby 40.0.0 needs Java 25 (GraalVM/Truffle 25.3.x) |
| **Platforms** | Linux x86-64, Linux AArch64, macOS AArch64 (tested on Oracle Linux 7-9, Ubuntu 18.04-22.04, Fedora 37-38, Debian 10-12) |
| **Thread safety** | No GIL: Ruby threads run in parallel; C extensions run under a global extension lock unless they declare themselves thread-safe or Ractor-safe (or --cexts-lock=false); ENV made thread-safe in 40.0.0 |
| **Drop-in for the baseline** | partial: runs the same Ruby source and most gems including C extensions, but about 98% ruby/spec, no fork/Ractor/callcc/RubyVM, different fiber, GC-stat and error-message behaviour |

## Gotchas

- The kostya/benchmarks Dockerfile downloads truffleruby-34.0.1-linux-amd64.tar.gz and truffleruby-jvm-34.0.1-linux-amd64.tar.gz, which the project's install guide identifies as the Oracle GraalVM builds (GraalVM Free Terms and Conditions), not the truffleruby-community-\* builds that carry the EPL-2.0/GPL-2.0/LGPL-2.1 licence; the guide says Oracle GraalVM is 'significantly faster and more memory-efficient', so the open-source build should be expected to be slower than the measured numbers.
- kostya times one run per process between two TCP notify messages, so startup is excluded but JIT warm-up is inside the timed region; this favours CRuby and YJIT on single-pass tests (Json, Base64) and is why TruffleRuby's own guide asks for benchmark-ips style warm-up before measuring.
- Performance can drop again when a program leaves the 'stable state' the JIT specialised for; the project recommends running with --engine.TraceCompilation to spot repeated deoptimisation.
- The repository has moved: github.com/oracle/truffleruby now resolves to github.com/truffleruby/truffleruby (copyright '2013-2025 Oracle; 2026 TruffleRuby contributors'), and versioning changed from GraalVM numbers (25.0.0) to Ruby-based numbers (34.0 = Ruby 3.4, 40.0 = Ruby 4.0).

## Known shortcomings

- Downgraded: the record picked the bench.b outlier; on kostya/benchmarks it is slower than LuaJIT and PyPy on 4 of 6 shared tests and in Are We Fast Yet it beats Node on only 6 of 14 benchmarks (that paper is co-authored by TruffleRuby developer Daloze). Clear wins are only over other Ruby implementations. Java, not C++.
- Enricher: the kostya Dockerfile downloads truffleruby-34.0.1-linux-amd64 and truffleruby-jvm tarballs, which are Oracle GraalVM builds under the GraalVM Free Terms and Conditions rather than the EPL/GPL/LGPL truffleruby-community builds (the install guide calls Oracle GraalVM 'significantly faster'), so the measured numbers do not represent the open-source build. Against CRuby 4.0.6 on kostya: about 16x on bench.b, 12x on Matmul, 2x on Primes, but about 1.9x slower on Base64 and about 10x slower on Json (10.618 s vs 1.031 s); the timed region includes JIT warm-up. Repo now at truffleruby/truffleruby; issue #4093 reports about 159 s vs 43 s on Ruby 4.0 YJIT.

## Caveats and trade-offs

Mixed against every listed baseline. On AWFY the geomean edge over Node.js comes mostly from Node's Bounce outlier, and Node.js has the better median. On kostya/benchmarks TruffleRuby is slower than LuaJIT and PyPy on 4 of the 6 shared tests (mandel.b, Json, Matmul, Primes), with Matmul 5.4x and Json 17x slower than PyPy. Node.js beats it on every kostya test shown. On kostya/jit-benchmarks 2023 it wins about half the time. AWFY numbers date from 2016, and the paper is co-authored by Benoit Daloze, a TruffleRuby developer, so it is peer-reviewed but not independent. JVM mode has high memory use (about 350 MB base RSS on kostya). plb2 (https://github.com/attractivechaos/plb2) lists Ruby only on the proprietary 'Graal EE 23.1.1' build. The README claim ('fastest Ruby implementation', yjit-bench) compares against other Rubies, not the listed baselines. [retier] The kostya Dockerfile downloads truffleruby-34.0.1-linux-amd64 and truffleruby-jvm tarballs, which are Oracle GraalVM builds under the GraalVM Free Terms and Conditions, not the EPL/GPL/LGPL truffleruby-community builds the install guide calls slower, so the numbers do not represent the open-source build; the timed region includes JIT warm-up. Mixed against every listed baseline; clear wins only over other Ruby implementations. The AWFY paper is co-authored by TruffleRuby developer Daloze. Repo now at truffleruby/truffleruby; issue #4093 reports about 159 s vs 43 s on Ruby 4.0 YJIT. Java, not C++.

Needs warm-up and much more memory (bench.b: 197.19 + 693.00 MiB vs 12.12 + 0.00 MiB for CRuby in the kostya tables). README offers two configurations: Native (faster startup) and JVM (better peak performance).

## Maintenance

Actively maintained (last commit 2026-09-26, 40.0.0 released with Ruby 4.0.2, 40.1.0 in development) and now community-governed under the truffleruby GitHub org; the Community Edition is open source under EPL-2.0/GPL-2.0/LGPL-2.1, while the faster Oracle GraalVM builds that independent benchmarks use are under Oracle's GraalVM Free Terms and Conditions.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): downgrade; tier before verification A, tier now B.
- **Tier reason:** The AWFY performance report (suite of the peer-reviewed DLS'16 paper) shows the record's JRuby+Truffle and Node.js values exactly, and kostya/benchmarks (Intel Xeon E-2324G, versions listed, public Docker harness) shows the bench.b numbers exactly, so the evidence stays tier B. The claim is overstated, hence downgrade: TruffleRuby beats Node.js on only 6 of 14 AWFY benchmarks, and beats LuaJIT and PyPy on only 1 of 6 shared kostya/benchmarks tests. The two kostya suites are A-level reproducible but mostly show it slower, so they cannot support an A-tier 'faster' claim.
- **Verifier notes:** All quoted numbers check out (AWFY JRuby+Truffle row; kostya bench.b rows and versions), but the record picks the one kostya test where TruffleRuby wins; recorded shortcoming should be 'mostly not faster than LuaJIT/PyPy/V8; wins are against other Ruby implementations'. Metadata checked on github.com: EPL-2.0 OR GPL-2.0-only OR LGPL-2.1-only triple licence, 3.2k stars, not archived, last commit 2026-09-26. The DLS'16 paper PDF (stefan-marr.de) is EGRESS_BLOCKED.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/smarr/are-we-fast-yet/HEAD/docs/performance.md>
  - <https://raw.githubusercontent.com/smarr/are-we-fast-yet/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/HEAD/README.md>
  - <https://github.com/oracle/truffleruby>
  - <https://github.com/oracle/truffleruby/commits/master>
- **Sources the enricher read:**
  - <https://github.com/oracle/truffleruby>
  - <https://github.com/truffleruby/truffleruby>
  - <https://github.com/oracle/truffleruby/commits/master>
  - <https://raw.githubusercontent.com/oracle/truffleruby/HEAD/README.md>
  - <https://raw.githubusercontent.com/oracle/truffleruby/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/oracle/truffleruby/HEAD/doc/user/installing-truffleruby.md>
  - <https://raw.githubusercontent.com/oracle/truffleruby/HEAD/doc/user/compatibility.md>
  - <https://raw.githubusercontent.com/oracle/truffleruby/HEAD/doc/user/reporting-performance-problems.md>
  - <https://raw.githubusercontent.com/oracle/truffleruby/HEAD/doc/user/known-cves.md>
  - <https://github.com/truffleruby/truffleruby/issues?q=is%3Aissue+is%3Aopen+label%3Aperformance>
  - <https://github.com/truffleruby/truffleruby/issues/4093>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/docker/Dockerfile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/common/commands.mk>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/json/test.rb>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/base64/test.rb>
  - <https://raw.githubusercontent.com/kostya/jit-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/smarr/are-we-fast-yet/HEAD/docs/performance.md>
  - WebSearch snippet of https://eregon.me/blog/2022/01/06/benchmarking-cruby-mjit-yjit-jruby-truffleruby.html (yjit-bench geomean vs CRuby 3.1: TruffleRuby 6.23x, YJIT 1.39x; first-party, page not opened)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/oracle/truffleruby`) · [data/wave12/enrich/raw/github_com_oracle_truffleruby.json](../../../data/wave12/enrich/raw/github_com_oracle_truffleruby.json) (enrichment confidence 0.8)

</details>
