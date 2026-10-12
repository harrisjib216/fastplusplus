# Marlin renderer (Java 2D)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Java` · `GPL-2.0-only WITH Classpath-exception-2.0` · 🟢 active

> Pure-Java antialiasing shape rasterizer for Java 2D that replaced Pisces and Ductus; OpenJDK's default renderer since JDK 9.

| | |
|---|---|
| **Beats** | OpenJDK 8 Pisces and Oracle JDK 8 Ductus (the Java 2D antialiasing rasterizers) |
| **Claimed result** | MapBench 0.5.6 summary (longer shared profile, 9 maps at 1, 2 and 4 threads, ratio = baseline time / Marlin time): overall score versus Ductus 228.90% and versus Pisces 223.85%; per-test ratios versus Ductus range from 99.75% to 598.66%. Summary Pct95 ms/op at 1/2/4 threads: Ductus 157.616 / 263.145 / 645.566, Pisces 345.619 / 373.08 / 477.03, Marlin 0.5.6 129.718 / 130.557 / 131.877, i.e. about 1.22x / 2.02x / 4.90x faster than Ductus and 2.66x / 2.86x / 3.62x faster than Pisces (derived from page data). Wiki Benchmarks page, Marlin 0.3 tables (same ratio direction, checked against the linked compareResults page: Pisces 173.103 ms vs Marlin 102.149 ms gives 169.46%): versus OpenJDK 8 Pisces 'score small' Tavg 163.28% (1 thread), 162.93% (2), 164.92% (4), 'score big' 327.59%, 372.77%, 391.64%; versus JDK 8 Ductus 'score small' 96.28%, 134.03%, 186.95%, 'score big' 128.67%, 164.76%, 386.80%. Wiki headline: 'Marlin 0.5.4 is 17% to 25% faster than marlin 0.3 and is as fast as Oracle ductus !' |
| **Workload** | MapBench 0.4 (Java 2D rendering of serialized GeoServer map drawings, maps/ in the mapbench repo) at 1, 2 and 4 threads: longer shared profile (one image per test, 10 s per test; 27 tests, 9 per thread count) for the 0.5.6 summary; default and shared profiles for the wiki's 0.3 and 0.5.4 comparisons. |
| **Metric** | throughput |
| **Hardware** | 0.5.6 summary: Intel i7 4800 (as written on the page; host HP ZBook 15), 4 CPUs at a fixed 2 GHz, HyperThreading and turbo boost disabled, Linux 3.13.0-47 (Ubuntu). Wiki 0.3 tables: 4 virtual CPUs on Linux 2.6.35 (Fedora 14), CPU model not stated. |
| **Compiler and flags** | 0.5.6 summary: Oracle Java SE 1.8.0_60-ea-b05 (HotSpot 25.60-b05), plus an internal OpenJDK 1.9.0 build of 2015-02-24 for the extra 'Marlin JDK9' column; JVM tuning -server -Xms2048m -Xmx2048m -XX:+UseConcMarkSweepGC; Pisces via -Xbootclasspath/a:../lib/openjdk8-pisces.jar -Dsun.java2d.renderer=sun.java2d.pisces.PiscesRenderingEngine; Marlin via -Xbootclasspath/p:../lib/marlin-0.5.6-Unsafe-sun-java2d.jar -Xbootclasspath/a:../lib/marlin-0.5.6-Unsafe.jar -Dsun.java2d.renderer.useThreadLocal=true -Dsun.java2d.renderer.useSimplifier=false -Dsun.java2d.renderer.useRef=soft -Dsun.java2d.renderer.pixelsize=2048 -Dsun.java2d.renderer.tileSize_log2=5 -Dsun.java2d.renderer=org.marlin.pisces.PiscesRenderingEngine; MapBench 0.4. Wiki 0.3 tables: custom OpenJDK8 b65 build (Pisces and Marlin), JDK8 b121 (Ductus), heap 2g, minimum 5000 ms per test. |
| **Adoption** | 197 stars; default Java 2D antialiasing renderer in OpenJDK 9+ (JEP 265) and in OpenJFX as Marlin-FX |
| **Last commit** | 2025-10-06 |
| **Links** | [repository](https://github.com/bourgesl/marlin-renderer) · [benchmark](https://bourgesl.github.io/marlin-0.5.6/longer_shared/perf_summary.htm) |

## Verdict

MapBench 0.4 (longer shared profile) on an Intel i7 4800 fixed at 2 GHz without HT or turbo, Oracle Java 8u60-ea with CMS and 2 GB heap: Marlin 0.5.6 rendered 9 serialized GeoServer maps with a mean per-test ratio of 2.29x against Oracle JDK 8 Ductus and 2.24x against OpenJDK 8 Pisces across 1, 2 and 4 threads; single-threaded the per-map geometric mean is about 1.18x over Ductus (range 1.00x to 1.42x) and 1.89x over Pisces, rising to about 3.7x over Ductus at 4 threads because Ductus does not scale (derived from page data). The summary Pct95 figures are arithmetic means over maps, so they are weighted toward the largest map (about 750 to 960 ms per op).

## Use it when

- Server-side Java 2D rendering on many threads (map servers such as GeoServer, chart or report generation): the 0.5.6 MapBench run kept per-op time flat from 1 to 4 threads while Ductus per-op time rose about 4x.
- Applications still on OpenJDK 8 or Oracle JDK 8, where the default Pisces (about 1.9x slower single-threaded in MapBench, derived from page data) or Ductus is in use.
- OpenJDK 11, 17 or 21 deployments that want rasterizer fixes newer than the Marlin copy their JDK bundled (for example JDK 17 ships Marlin 0.9.1.4; the standalone jar is 0.9.4.9 with fixes such as JDK-8341381 and JDK-8277574).
- Workloads dominated by antialiased stroked and filled vector shapes (map layers, polylines, polygons) rather than images or text.

## Skip it when

- Native C or C++ code: it only runs inside a JVM as a Java 2D RenderingEngine; use a native rasterizer instead.
- If you are on a current OpenJDK and have no rendering bug to fix: you already run Marlin, so swapping in the jar brings fixes, not the historical 1.2x to 4x gains over Pisces or Ductus.
- Text rendering, image scaling or compositing bottlenecks: Marlin only produces shape coverage masks; blending and blits stay in the JDK pipeline.
- Very large stroked curves with cusps: open bug #35 (self-intersections in large stroked curves) and #38 (cubic offset computation) are unresolved.
- Thread-heavy web servers with default ThreadLocal contexts can hold one cached context per thread; the wiki suggests useThreadLocal=false (CLQ mode) to cap memory.

## How it is fast

It is a rewrite of the Pisces scanline rasterizer that avoids garbage: each rendering thread gets a reusable RendererContext (ThreadLocal or ConcurrentLinkedQueue, held by soft/weak/hard references) with pooled array caches, and edge data lives in off-heap memory managed through Unsafe. The scanline loop advances edge crossings with fixed-point DDA, keeps crossings almost sorted between scanlines and finishes with insertion sort, merge sort or a dual-pivot quicksort depending on size, and stores coverage as RLE or raw tiles with tile flags so empty tiles are skipped. Defaults are 256 subpixels in x and 8 in y (quality profile) and 128x64 tiles where large tiles are supported. Because contexts are per thread, it scales across cores where Ductus serialised rasterization through a native singleton.

## Compared with alternatives

Pick Marlin only when your code draws through Java 2D Graphics2D on a JVM: Blend2D, AGG and Vello CPU are faster native options but need a different API and native integration, and ImageSharp.Drawing is the comparable choice on .NET. For a native C or C++ project, Blend2D is the stronger catalogued pick.

## Integration

| | |
|---|---|
| **Form** | module (jar patched into the JDK; built into OpenJDK 9+) |
| **Dependencies** | none (Maven build, no third-party runtime dependencies); uses JDK-internal Unsafe and java.desktop internals |
| **Minimum toolchain** | JDK 8 (0.9.4.7 jar via -Xbootclasspath/p), JDK 11 to 21 (0.9.4.8 jar), JDK 17 to 26 (0.9.4.9 jar, built with Java 17) |
| **Platforms** | any platform with a HotSpot-style OpenJDK and Java 2D (pure Java; JDK 8 releases also targeted Oracle JDK 8) |
| **Thread safety** | Concurrent rendering from many threads is supported: one RendererContext per thread via ThreadLocal (default) or a ConcurrentLinkedQueue pool (sun.java2d.renderer.useThreadLocal=false). |
| **Drop-in for the baseline** | partial — drop-in for Pisces or Ductus with no code changes, but enabled by JVM flags (--patch-module java.desktop=&lt;jar&gt; on JDK 11+, or -Xbootclasspath/p plus -Dsun.java2d.renderer=sun.java2d.marlin.DMarlinRenderingEngine on JDK 8), not by a library dependency |

## Gotchas

- Releases are per JDK line (JDK 8, 11+, 17+); the JDK 8 branch use_Unsafe has not been maintained since 2024-01, and the default master branch still carries an old 0.7.0.1 pom, so take sources from the jdk branch or the release jars.
- Patching java.desktop replaces JDK-internal classes (sun.java2d.marlin); a JDK update can change internals the jar relies on, so match the jar to the supported JDK range in its release notes.
- Many tuning system properties (subpixel counts, tile sizes, profile=quality|speed, pixelWidth/pixelHeight for initial array sizes) change both speed and output; the published benchmarks used non-default settings for their time (tileSize_log2=5, useRef=soft).
- Later fixes have themselves caused regressions (JDK-8341381: random lines introduced by the JDK-8297230 fix, fixed in 0.9.4.9), so test rendering output after upgrading the jar.

## Known shortcomings

- Java (language-filter mismatch). Tier A on the linked MapBench 0.5.6 summary (bourgesl/mapbench harness; Intel i7 4800 fixed at 2 GHz, JDK 1.8.0_60-ea-b05, full JVM flags): 228.90% vs Ductus and 223.85% vs Pisces, the JDK default rasterizers before JDK 9 (recognisable incumbents, not on the category list). The wiki 0.3 tables name no CPU.
- The MapBench summary Pct95 is an arithmetic mean over maps weighted toward the 750-960 ms map; per-map single-thread geomeans are 1.18x versus Ductus (1.00-1.42x) and 1.89x versus Pisces, and the 4-thread 3.7x reflects Ductus serialisation (derived from page data). Historical result: Marlin is the OpenJDK 9+ default renderer, so the jar matters only for JDK 8 or for fixes newer than the bundled copy. Open bugs #35 and #38 (stroked curve cusps and offsets); the default master branch is stale (pom 0.7.0.1) and the live code is on the jdk branch.

## Caveats and trade-offs

Java, not C++: a pure-Java Java 2D RenderingEngine plugged into the JDK through sun.java2d.renderer, derived from the OpenJDK 8 Pisces source (GPL-2.0 with Classpath exception). Pisces (OpenJDK 6-8) and Ductus (closed-source, Sun/Oracle JDK up to 8) were the default Java 2D antialiasing rasterizers before Marlin replaced them in OpenJDK 9 (JEP 265, per the README's JDK table), so they are recognisable incumbents for Java but not catalogue baselines (Skia, Cairo, Blend2D): baseline_in_list false. All numbers are first-party and from 2014-2015 builds (Marlin 0.3 to 0.5.6; current release 0.9.4.9) on early-access or internal JDK builds; since Marlin is now the JDK default, the comparison is historical and Ductus is only available as a binary in Oracle JDK 8. Summary ratios are Pct95 per-op times under concurrent threads, so the 4-thread gain over Ductus largely reflects Ductus's poor multi-thread scaling; single-thread gain over Ductus is about 1.2x (0.5.6) or none (0.3 'score small' 96.28%). The result pages live on bourgesl.github.io (blocked here; read from the bourgesl/bourgesl.github.io repository source); the wiki's newer charts (0.7.x, FOSDEM 2016) are images that were not read.

Java only; no GC pressure thanks to pooled array caches; scales near-linearly across threads where Ductus had synchronised singleton native structures; derived from OpenJDK 8 Pisces source and licensed GPLv2 with Classpath Exception.

## Maintenance

Active: release 0.9.4.9 for JDK 17 to 26 in late 2025 and 10 open issues, mostly quality enhancements; GPL-2.0 with Classpath exception, and since Marlin ships inside OpenJDK most users already have it, so the standalone jar matters mainly for JDK 8 and for newer fixes on older JDKs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C: the wiki's linked MapBench 0.5.6 summary (bourgesl.github.io/marlin-0.5.6/longer_shared/perf_summary.htm, read from the bourgesl/bourgesl.github.io repo source) compares Marlin 0.5.6 against Oracle JDK 8 Ductus and OpenJDK 8 Pisces and states the CPU (Intel i7 4800 at a fixed 2 GHz, no HT, no turbo), the JDK builds and the full JVM and renderer flags; the harness is public (github.com/bourgesl/mapbench: bin/bench_marlin.sh, bin/bench_pisces.sh, src/, maps/). The wiki's own Marlin 0.3 tables alone would be C (only '4 virtual CPUs', no CPU model).
- **Verifier notes:** Wiki numbers match the record exactly; the 0.3 detail page names no CPU model, but the linked 0.5.6 summary does (Intel i7 4800, fixed 2 GHz), so the tier rises to A. Metadata checked on github.com: GPL2 + Classpath exception, 197 stars, not a fork, last master commit 2025-10-06 (README update; release 0.9.4.9 Oct 2025), active. Language stays Java and baseline_in_list stays false.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/wiki/bourgesl/marlin-renderer/Benchmarks.md>
  - <https://raw.githubusercontent.com/bourgesl/marlin-renderer/HEAD/README.md>
  - <https://raw.githubusercontent.com/bourgesl/bourgesl.github.io/master/marlin-0.3/compare/compareResults.htm>
  - <https://raw.githubusercontent.com/bourgesl/bourgesl.github.io/master/marlin-0.5.6/longer_shared/perf_summary.htm>
  - <https://raw.githubusercontent.com/bourgesl/bourgesl.github.io/master/marlin-0.5.4/shared/compareResults_shared_ductus_marlin0.4.x.htm>
  - <https://raw.githubusercontent.com/bourgesl/mapbench/HEAD/README.md>
  - <https://github.com/bourgesl/mapbench>
  - <https://github.com/bourgesl/mapbench/tree/master/bin>
  - <https://github.com/bourgesl/marlin-renderer>
  - <https://github.com/bourgesl/marlin-renderer/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/bourgesl/marlin-renderer/HEAD/README.md>
  - <https://raw.githubusercontent.com/bourgesl/marlin-renderer/HEAD/pom.xml>
  - <https://raw.githubusercontent.com/bourgesl/marlin-renderer/jdk/pom.xml>
  - <https://raw.githubusercontent.com/bourgesl/marlin-renderer/use_Unsafe/pom.xml>
  - <https://raw.githubusercontent.com/bourgesl/marlin-renderer/jdk/src/main/java/sun/java2d/marlin/Renderer.java>
  - <https://raw.githubusercontent.com/bourgesl/marlin-renderer/jdk/src/main/java/sun/java2d/marlin/MarlinProperties.java>
  - <https://raw.githubusercontent.com/bourgesl/marlin-renderer/jdk/src/main/java/sun/java2d/marlin/OffHeapArray.java>
  - <https://raw.githubusercontent.com/bourgesl/marlin-renderer/jdk/src/main/java/sun/java2d/marlin/MarlinCache.java>
  - <https://raw.githubusercontent.com/bourgesl/marlin-renderer/jdk/src/main/java/sun/java2d/marlin/MarlinTileGenerator.java>
  - <https://raw.githubusercontent.com/bourgesl/marlin-renderer/jdk/src/main/java/sun/java2d/marlin/RendererContext.java>
  - <https://raw.githubusercontent.com/bourgesl/marlin-renderer/jdk/src/main/java/sun/java2d/marlin/DMarlinRenderingEngine.java>
  - <https://raw.githubusercontent.com/bourgesl/marlin-renderer/jdk/src/main/java/sun/java2d/marlin/MarlinConst.java>
  - <https://raw.githubusercontent.com/bourgesl/marlin-renderer/jdk/src/main/java/sun/java2d/marlin/Version.java>
  - <https://raw.githubusercontent.com/wiki/bourgesl/marlin-renderer/Benchmarks.md>
  - <https://raw.githubusercontent.com/wiki/bourgesl/marlin-renderer/Home.md>
  - <https://raw.githubusercontent.com/wiki/bourgesl/marlin-renderer/Tuning-options.md>
  - <https://raw.githubusercontent.com/wiki/bourgesl/marlin-renderer/How-to-build.md>
  - <https://raw.githubusercontent.com/wiki/bourgesl/marlin-renderer/History-and-context.md>
  - <https://raw.githubusercontent.com/wiki/bourgesl/marlin-renderer/R&D.md>
  - <https://raw.githubusercontent.com/bourgesl/bourgesl.github.io/master/marlin-0.5.6/longer_shared/perf_summary.htm>
  - <https://raw.githubusercontent.com/bourgesl/mapbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/bourgesl/mapbench/HEAD/bin/env.sh>
  - <https://raw.githubusercontent.com/bourgesl/mapbench/HEAD/bin/bench_marlin.sh>
  - <https://raw.githubusercontent.com/bourgesl/mapbench/HEAD/bin/bench_pisces.sh>
  - <https://raw.githubusercontent.com/bourgesl/mapbench/master/src/main/java/it/geosolutions/java2d/MapBench.java>
  - <https://raw.githubusercontent.com/bourgesl/mapbench/master/src/main/java/it/geosolutions/java2d/Result.java>
  - <https://github.com/bourgesl/mapbench/tree/master/src/main/java/it/geosolutions/java2d>
  - <https://github.com/bourgesl/marlin-renderer>
  - <https://github.com/bourgesl/marlin-renderer/issues>
  - <https://github.com/bourgesl/marlin-renderer/issues/35>
  - <https://github.com/bourgesl/marlin-renderer/releases>
  - <https://github.com/bourgesl/marlin-renderer/tree/jdk/src/main/java>
  - <https://github.com/bourgesl/marlin-renderer/tree/jdk/src/main/java/sun/java2d/marlin>
  - WebSearch: Azul 'Performance Rendered Visual' Marlin Ductus Java2D latency (snippet of https://www.azul.com/blog/performance-rendered-visual/ only)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/bourgesl/marlin-renderer`) · [data/wave10/enrich/raw/github_com_bourgesl_marlin_renderer.json](../../../data/wave10/enrich/raw/github_com_bourgesl_marlin_renderer.json) (enrichment confidence 0.8)

</details>
