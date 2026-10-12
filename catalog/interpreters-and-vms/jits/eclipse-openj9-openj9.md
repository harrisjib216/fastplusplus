# Eclipse OpenJ9

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `EPL-2.0 OR Apache-2.0 OR GPL-2.0-only WITH Classpath-exception-2.0 OR GPL-2.0-only WITH OpenJDK-assembly-exception-1.0` · 🟢 active

> Alternative Java VM (ex-IBM J9) whose shared class cache plus dynamic AOT starts Java servers faster, with less RAM, than HotSpot.

| | |
|---|---|
| **Beats** | HotSpot (AdoptOpenJDK 11.0.7) |
| **Claimed result** | DayTrader 3 on OpenJDK 9: with AOT enabled (shared class cache populated by an earlier cold run) OpenJ9 startup is almost 40% lower than HotSpot, with AOT plus -Xquickstart almost 50% lower (page headline '2x faster startup'); with no options OpenJ9 starts slightly slower than HotSpot. Footprint about 60% less right after startup; during ramp-up HotSpot used about 80% more RSS (headline '40% less footprint'). Similar peak throughput, reached about 7 minutes sooner by OpenJ9. Single-core cloud test (AOT plus -Xtune:virtualized): headline '4x faster ramp up', HotSpot needs about 30 minutes to peak vs 7.5 minutes for default OpenJ9. Newer pages in the same repo: OpenJDK 11 DayTrader7 51-55% faster startup and 45-57% smaller startup footprint with SCC/AOT (benchmark/openjdk11-daytrader7.md); Quarkus REST+CRUD 64-66% faster startup, 18-37% smaller startup footprint (benchmark/quarkus.md). |
| **Workload** | DayTrader7 on WebSphere Liberty with DB2 on a second machine: startup time to 'ready to run a smarter planet', RSS footprint after startup and during load, ramp-up and peak throughput. |
| **Metric** | startup |
| **Hardware** | Intel Core i7-3770K @ 3.50GHz, 16GB RAM, HyperThreading (8 hardware threads), CentOS 7.3; JVM pinned to 4 hardware threads; Db2 and JMeter on separate machines over 10Gb Ethernet (benchmark page). The OpenJDK 11 and Quarkus pages use the same i7-3770K. |
| **Compiler and flags** | AdoptOpenJDK OpenJDK9-OPENJ9 build 20170925 (OpenJ9 VM 2.9, based on jdk-9+181) vs AdoptOpenJDK OpenJDK9 HotSpot build of the same date; OpenJ9 options -Xshareclasses -Xscmx60M -Xscmaxaot8M (AOT), plus -Xquickstart, and -Xscmx150M -Xscmaxaot120m -Xtune:virtualized (cloud tuning); -Xmx1g; long --add-modules/--add-exports list for both JVMs. Native build compiler not applicable. |
| **Adoption** | 3.5k stars |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/eclipse-openj9/openj9) · [benchmark](https://raw.githubusercontent.com/eclipse-openj9/openj9-website/master/benchmark/openjdk11-daytrader7.md) |

## Verdict

IBM/Eclipse engineers ran DayTrader 3 on a private OpenLiberty build (OpenJDK 9, 2017), DayTrader7 on Liberty 20.0.0.5 (OpenJDK 11) and a Quarkus REST+CRUD app in a 1-CPU, 256 MB Docker container, on an Intel Core i7-3770K with Db2/PostgreSQL and JMeter on other machines; with a pre-populated SCC/AOT cache OpenJ9 started 40-50% faster (JDK 9), 51-55% faster (JDK 11 DayTrader7) and 64-66% faster (Quarkus) than AdoptOpenJDK HotSpot, with 45-60% smaller RSS after startup and similar peak throughput. Without the cache OpenJ9 startup was similar to or slightly slower than HotSpot; a newer DayTrader8/Java 17 page on eclipse.dev (blocked, search snippet only) reports smaller gains of 10-30% startup and 31-38% footprint.

## Use it when

- Server or microservice JVMs (Liberty, Quarkus, similar frameworks) that restart often, where startup time and resident memory per instance cost more than the last few percent of peak throughput.
- Dense container or cloud deployments with small memory limits: the project's pages report 18-37% (Quarkus, 256 MB container) to 45-57% (DayTrader7) smaller RSS right after startup and 19-33% smaller RSS under load versus HotSpot 11.
- CPU-constrained instances (one core or fractional vCPU) where JIT compilation competes with application threads: with SCC/AOT and -Xtune:virtualized OpenJ9 reached useful throughput much earlier than HotSpot on a single pinned core.
- Fleets that can keep a populated SCC between runs (persistent cache directory or Docker volume) or use JITServer to offload compilation from many small JVMs on Linux x86-64, AArch64, ppc64le or s390x.

## Skip it when

- Long-running batch or compute-bound services judged on peak throughput: the project's own pages claim only 'comparable' peak throughput, and -Xtune:virtualized costs about 10% of peak in the OpenJDK 11 and Quarkus runs.
- Cold starts with no populated cache (ephemeral containers that do not persist the SCC): without SCC/AOT the pages report startup similar to HotSpot, and OpenJDK 9 OpenJ9 started slightly slower than HotSpot with no options.
- Code shapes with known JIT gaps: open issues report Spring Boot plus Apache Camel EndpointRouteBuilder (a class with 344 interfaces) starting in 4.2-6.2 s versus 2.95 s on HotSpot (#14764), a fuzzer-mutated MergeSort 3-4x slower than HotSpot and GraalVM on JDK 21 (#21947), Nashorn up to 29x slower (#5371) and nested-loop and Record.equals gaps (#15544, #12359).
- Teams relying on HotSpot-specific -XX tuning flags, GC choices or tooling: OpenJ9 has its own option set, GC policies and dump formats, so runbooks need translation.
- If you need a Java SE TCK-certified binary from the Eclipse project itself: Eclipse does not distribute JDK binaries; you depend on a vendor build or your own.

## How it is fast

Class data sharing stores parsed (ROM) classes in a persistent, memory-mapped shared classes cache (SCC) that later JVMs map instead of re-loading and verifying classes, which cuts both startup time and per-process footprint. With the SCC enabled, the JIT also emits relocatable dynamic AOT code into the cache during an application's startup phase; the next run loads those method bodies (the project says about 100x faster than JIT-compiling them) and the JIT later recompiles the hot ones at higher levels. The Testarossa JIT (shared with Eclipse OMR) tiers methods through cold, warm, hot, very-hot-with-profiling and scorching, driven by invocation counts and a sampling thread; -Xquickstart and -Xtune:virtualized lower optimisation effort to save CPU in small containers, and JITServer can move compilation into a separate remote process.

## Compared with alternatives

OpenJ9 is the only Java VM among the catalogued jits; pick it over the incumbent HotSpot when an existing Java service is limited by startup time or per-instance memory, whereas siblings such as the .NET RyuJIT runtime, Graal.js or the Dart VM only matter if you are choosing a language, and none of them runs Java bytecode.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | OpenJDK class libraries from the ibmruntimes openj9-openjdk-jdkNN mirror (HotSpot removed, openj9 branch patches), Eclipse OMR (fetched by get_source.sh), a boot JDK of the same level, optional OpenSSL 3.x; built with the OpenJDK make/configure system |
| **Minimum toolchain** | Project build machines use gcc 14.2 on Linux (the Docker recipe uses gcc-11/g++-11), Visual Studio 2022 plus LLVM/Clang and NASM 2.15.05+ on Windows, Xcode 15.2 / clang 15 on macOS, XL C/C++ 16.1 or Open XL 17.1.3 on AIX; Linux binaries need glibc 2.17+ |
| **Platforms** | Linux x86-64, AArch64, ppc64le and s390x; Windows x64 (x86-32 for JDK 8); macOS x64 and Apple silicon (JDK 11+); AIX ppc64; JITServer and CRIU support are Linux-only |
| **Thread safety** | Full multithreaded JVM; JIT and AOT compilation run on background compilation threads, and one SCC can be shared by concurrent JVM processes from the same Java installation |
| **Drop-in for the baseline** | partial — runs the same Java bytecode on the same OpenJDK class libraries and java launcher, but HotSpot -XX tuning flags, GC names and diagnostic outputs differ, and the startup/footprint gains need -Xshareclasses (or a framework such as Liberty that enables it) plus a warm cache |

## Gotchas

- Harness asymmetry: all four openj9-website pages measure OpenJ9 with an SCC and AOT code populated by an uncounted previous cold run, but list no CDS or AppCDS options for HotSpot (AppCDS has been in OpenJDK since JDK 10), so the 40-66% startup gains compare a warm-cache OpenJ9 against HotSpot without its own class-data archive. A competing vendor's 2022 comparison (BellSoft, snippet only, site blocked) reports AppCDS alone cutting HotSpot footprint by about 30%.
- The OpenJDK 11 DayTrader7 and Quarkus pages compare a nightly OpenJ9 build (11.0.8+3, master-78f76052e, 2020-05-20) against GA HotSpot 11.0.7+10, so the class library levels differ; results are charts only, with no run counts or variance.
- Footprint gaps partly reflect GC defaults, not the JIT: the OpenJDK 8 page itself attributes much of its 63% ramp-up footprint gap to HotSpot's default ParallelGC; heap was capped at -Xmx256m/-Xmx1G/-Xmx128m depending on the test.
- Default class sharing covers bootstrap classes only (-Xshareclasses:bootClassesOnly,nonFatal,silent) and is off in containers, so the advertised gains need -Xshareclasses (or Liberty's scripts) and a persistent cache location; a cache baked into a container image started slower than a Docker volume in the Quarkus tests.

## Known shortcomings

- Vendor charts only (IBM/Eclipse, private OpenLiberty build); the startup and footprint wins need a shared class cache filled by an earlier cold run, and a default OpenJ9 start is slightly slower than HotSpot. Startup and memory numbers, not throughput; Java/C++ runtime whose baseline HotSpot it does not beat on peak performance.
- Enricher: all four openj9-website pages (daytrader3, daytrader7, openjdk11-daytrader7, quarkus) compare OpenJ9 with a shared class cache and AOT code from an uncounted prior run against HotSpot with no CDS or AppCDS options, so warm OpenJ9 versus cold HotSpot; the JDK 11 pages pit nightly OpenJ9 11.0.8 against GA HotSpot 11.0.7, the JDK 8 page blames HotSpot's ParallelGC default for much of the footprint gap, charts only with no run counts. Newer DayTrader8/Java 17 page shows 10-30% startup and 31-38% footprint (snippet only); issues #14764 (Spring Boot plus Camel 4.2-6.2 s vs 2.95 s on HotSpot) and #21947 (mutated MergeSort 3-4x slower) contradict it on some code.

## Caveats and trade-offs

First-party IBM/Eclipse benchmark on a 2012-era desktop CPU against OpenJDK 9 HotSpot (2017); results are shown only as charts and percentages. The startup and footprint wins depend on a shared class cache and AOT code populated by a previous cold run that is not counted; with no options OpenJ9 started slightly slower than HotSpot (OpenJDK 11 pages: similar without SCC). The run used a private OpenLiberty build with a beta ASM V6 library, so it cannot be reproduced exactly. Peak throughput is described as comparable, not faster. The repository README has no numbers. Newer eclipse.dev daytrader8 pages were not opened (blocked); figures for them are snippet only.

The win is startup time and memory footprint, not peak throughput. Needs a shared class cache populated by a prior cold run for the startup gain; the AOT code is slightly larger than JIT code. Builds are AdoptOpenJDK-style OpenJDK binaries with the OpenJ9 VM and JIT in place of HotSpot.

## Maintenance

Very active (3.5k stars, about 26.8k commits, last commit 2026-10-05, quarterly releases tracking every OpenJDK LTS plus feature releases); EPL-2.0 or Apache-2.0 with GPLv2-compatible secondary licences, usable today through vendor JDK builds such as IBM Semeru or by building it yourself, although nobody would vendor its source into a C++ project.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party IBM/Eclipse write-up (openj9-website benchmark/daytrader3.md) against OpenJDK 9 HotSpot with CPU model, JDK builds and JVM options stated, but results are charts only, the run used a private OpenLiberty build with a beta ASM V6, and the JMeter/Db2 harness is not published, so it is not reproducible; vendor evidence stays C.
- **Verifier notes:** All numbers in claimed_speedup appear on daytrader3.md; the record was accurate apart from the licence (four-way SPDX expression in LICENSE) and the missing caveat that default OpenJ9 starts slightly slower than HotSpot and the wins need a pre-populated shared class cache. Metadata checked: 3.5k stars, not archived, last commit 2026-10-05.
- **Fields the verifier corrected:** `license`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/eclipse-openj9/openj9-website/master/benchmark/daytrader3.md>
  - <https://raw.githubusercontent.com/eclipse-openj9/openj9-website/master/benchmark/daytrader7.md>
  - <https://raw.githubusercontent.com/eclipse-openj9/openj9-website/master/benchmark/openjdk11-daytrader7.md>
  - <https://raw.githubusercontent.com/eclipse-openj9/openj9-website/master/benchmark/quarkus.md>
  - <https://github.com/eclipse-openj9/openj9-website/tree/master/benchmark>
  - <https://github.com/eclipse-openj9/openj9>
  - <https://github.com/eclipse-openj9/openj9/commits>
  - <https://raw.githubusercontent.com/eclipse-openj9/openj9/HEAD/README.md>
  - <https://raw.githubusercontent.com/eclipse-openj9/openj9/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/eclipse-openj9/openj9>
  - <https://raw.githubusercontent.com/eclipse-openj9/openj9/HEAD/README.md>
  - <https://raw.githubusercontent.com/eclipse-openj9/openj9/HEAD/doc/build-instructions/Build_Instructions_V21.md>
  - <https://raw.githubusercontent.com/eclipse-openj9/openj9/HEAD/doc/build-instructions/Build_Instructions_V17.md>
  - <https://github.com/eclipse-openj9/openj9/tree/master/runtime/compiler>
  - <https://github.com/eclipse-openj9/openj9/issues?q=is%3Aissue%20slower%20than%20hotspot>
  - <https://github.com/eclipse-openj9/openj9/issues/14764>
  - <https://github.com/eclipse-openj9/openj9/issues/21947>
  - <https://github.com/eclipse-openj9/openj9-website/tree/master/benchmark>
  - <https://raw.githubusercontent.com/eclipse-openj9/openj9-website/master/benchmark/daytrader3.md>
  - <https://raw.githubusercontent.com/eclipse-openj9/openj9-website/master/benchmark/daytrader7.md>
  - <https://raw.githubusercontent.com/eclipse-openj9/openj9-website/master/benchmark/openjdk11-daytrader7.md>
  - <https://raw.githubusercontent.com/eclipse-openj9/openj9-website/master/benchmark/quarkus.md>
  - <https://raw.githubusercontent.com/eclipse-openj9/openj9-docs/master/docs/jit.md>
  - <https://raw.githubusercontent.com/eclipse-openj9/openj9-docs/master/docs/aot.md>
  - <https://raw.githubusercontent.com/eclipse-openj9/openj9-docs/master/docs/shrc.md>
  - <https://raw.githubusercontent.com/eclipse-openj9/openj9-docs/master/docs/jitserver.md>
  - <https://raw.githubusercontent.com/eclipse-openj9/openj9-docs/master/docs/criusupport.md>
  - <https://raw.githubusercontent.com/eclipse-openj9/openj9-docs/master/docs/openj9_support.md>
  - https://bell-sw.com/announcements/2022/06/28/hotspot-vs-openj9-performance-comparison/ (EGRESS_BLOCKED; WebSearch snippet only)
  - https://eclipse.dev/openj9/performance/benchmark17/daytrader8_java17.html (not opened; WebSearch snippet only)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/eclipse-openj9/openj9`) · [data/wave12/enrich/raw/github_com_eclipse_openj9_openj9.json](../../../data/wave12/enrich/raw/github_com_eclipse_openj9_openj9.json) (enrichment confidence 0.75)

</details>
