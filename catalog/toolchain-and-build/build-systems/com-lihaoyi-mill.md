# Mill

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Build systems](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Scala` · `MIT` · 🟢 active

> JVM build tool for Java/Scala/Kotlin; 4-44x faster clean/incremental compiles than Maven, 3.6-10.2x than Gradle.

| | |
|---|---|
| **Beats** | Apache Maven and Gradle |
| **Claimed result** | vs Maven (Netty): 4.0x sequential clean compile all, 4.9x parallel clean compile all, 7.0x clean compile single module, 30.7x incremental single module, 44.0x no-op single module. vs Gradle (Mockito): 3.7x, 3.6x, 5.2x, 5.9x, 10.2x for the same five scenarios. |
| **Workload** | Compiling Netty (\~500k LOC, 47 submodules) vs Maven, and Mockito (\~100k LOC, 22 submodules) vs Gradle: sequential/parallel clean-compile-all, single-module clean/incremental/no-op compile. |
| **Metric** | build-time |
| **Hardware** | 2021 M1 MacBook Pro, 10 CPU cores, 32GB RAM (exact M1 variant not named) |
| **Compiler and flags** | Java 17 (javac), Mill 0.12.9-native; Maven/Gradle at each project's default version; exact timed commands and flags listed on page (e.g. ./mvnw -T 10 -Pfast -Denforcer.skip=true install; ./mill -j1 __.compile) |
| **Adoption** | 2.8k stars |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/com-lihaoyi/mill) · [benchmark](https://mill-build.org/mill/comparisons/performance.html) |

## Verdict

Mill's own docs page (mill-build.org/mill/comparisons/performance.html) benchmarked Mill 0.12.9-native (Java 17) against each project's default Maven/Gradle version on a 2021 M1 MacBook Pro (10 CPU, 32GB RAM), median wall time of 3 runs after warmup. Netty (\~500k LOC, 47 modules) vs Maven: 4.0x-44.0x across sequential/parallel/single-module clean, incremental, and no-op compile. Mockito (\~100k LOC, 22 modules) vs Gradle: 3.6x-10.2x for the same five scenarios.

## Use it when

- Multi-module Java/Scala/Kotlin monorepos where edit-compile-test iteration speed matters
- CI pipelines bottlenecked by Maven/Gradle daemon startup or full-module recompilation on every run
- Teams that want built-in selective test execution, test parallelism, and Chrome-trace build profiling without extra plugins
- New JVM projects willing to adopt a non-XML/non-Groovy build DSL from the start
- Want a self-contained native (Graal) launcher with fast CLI startup and no local JDK requirement

## Skip it when

- Large existing Maven/Gradle codebase with heavy reliance on the Maven Central/Gradle Plugin Portal plugin ecosystem, which Mill's is much smaller than
- Non-JVM projects (C++/CMake/Cargo, etc.) - not applicable at all
- Windows-ARM machines: Mill has no native executable there (upstream GraalVM limitation) and falls back to the slower JVM launcher, which also needs a system JDK 17+
- Teams running very high task parallelism on newer Mill versions: an open issue (#7381, 1.2.0-RC1) reports up to \~20x slowdown and thread-pool blowup at large --jobs values
- Projects needing mature BSP/IDE tooling parity - several Metals/BSP integration bugs have been filed (mostly closed, but recent)

## How it is fast

Mill runs a persistent JVM background daemon, avoiding per-invocation JVM startup and classloading. It memoizes every build step as a fine-grained Task in a dependency graph, so unchanged tasks are skipped entirely (no-op compiles finish in \~0.1s). For Java/Scala incremental compiles it uses the Zinc incremental compiler to recompile only files whose changes affect downstream code. Unlike Maven, it works directly with classfiles on disk rather than round-tripping through .m2 jar packing/unpacking, and it parallelizes independent tasks by default.

## Compared with alternatives

No sibling overlap: ccache, Buck2, tup, and xmake all target C/C++ or polyglot native builds, not the JVM. Pick Mill specifically when the baseline pain is Maven/Gradle overhead on a Java/Scala/Kotlin project; none of the catalogued siblings apply there.

## Integration

| | |
|---|---|
| **Form** | source-drop (CLI tool + build.mill config file per project, not a library) |
| **Dependencies** | none for the default launcher (self-contained Graal native binary, downloads its own JVM for module builds); the '-jvm' launcher variant requires a system JDK 17+ |
| **Minimum toolchain** | Mill supports JVM 11+ for evaluating builds (configurable per-project via mill-jvm-version); native launcher needs no local JDK, JVM launcher needs JDK 17+ |
| **Platforms** | Native executables: Windows/Mac/Linux on Intel, Mac/Linux on ARM. Windows-ARM has no native executable and falls back to the JVM launcher. |
| **Thread safety** | not documented (CLI build tool, not a library); parallel task execution is a first-class feature but internal thread-safety guarantees for custom task code aren't specified |
| **Drop-in for the baseline** | partial - Mill provides MavenModule/other traits to ease porting, and a `mill init` scaffolder, but existing pom.xml/build.gradle files must still be manually ported to build.mill |

## Gotchas

- PowerShell 5.1 writes UTF-16LE .mill-version files that Mill can't read; PowerShell 7+ is required on Windows
- Benchmark page itself is internally inconsistent on the Mill version used: the summary text says 'Mill 1.1.0' while the detailed benchmark tables specify 'Java 17 + Mill 0.12.9-native'
- The Netty and Mockito ports used for the benchmark are not 100% complete - some subprojects, linters, and Android/Kotlin/OSGI tests were disabled to make the comparison apples-to-apples
- Open bug (#7381) shows severe negative performance scaling (thread pool grows to thousands of blocked threads) at very high --jobs counts on a 1.2.0-RC1 build; unclear if it reached a stable release

## Caveats and trade-offs

Baseline is Maven/Gradle, not one of this run's named baselines (CMake+Ninja, Make, Bazel, Cargo). These are Mill's own ad-hoc numbers (median wall time of 3 runs after warmup). The page contradicts itself on versions: a general note says Mill 1.1.0, but the in-depth sections that hold the tables say Java 17 + Mill 0.12.9-native. Maven/Gradle versions are the project defaults and are not pinned. The Mill ports of Netty and Mockito are incomplete: some subprojects and linters are disabled for the comparison.

JVM-only (Java/Scala/Kotlin), not usable for C++/CMake/Cargo projects; uses Mill's own build.mill DSL instead of pom.xml/build.gradle; smaller plugin ecosystem than Maven or Gradle.

## Maintenance

Actively maintained: latest commit is today (2026-09-24), 2.8k GitHub stars, MIT licensed. Distributed as a self-updating bootstrap script (Maven Central-hosted releases), so it's directly usable without vendoring.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification A, tier now A.
- **Tier reason:** The benchmark configs are public (example/thirdparty/netty/build.mill and example/thirdparty/mockito/build.mill), and the page lists the exact timed commands and flags, e.g. './mvnw -T 10 -Pfast -Denforcer.skip=true install' vs './mill __.compile'. It also states Java 17 + Mill 0.12.9-native and the machine (2021 M1 MacBook Pro, 10 CPU, 32GB), so the build configuration and machine are fully specified.
- **Verifier notes:** All ten speedup figures (Netty/Maven and Mockito/Gradle) match the page. The license (MIT), 2.8k stars (2,795) and last commit (2026-09-24) are confirmed.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://mill-build.org/mill/comparisons/performance.html>
  - <https://github.com/com-lihaoyi/mill>
  - <https://github.com/com-lihaoyi/mill/blob/main/example/thirdparty/netty/build.mill>
  - <https://github.com/com-lihaoyi/mill/blob/main/example/thirdparty/mockito/build.mill>
- **Sources the enricher read:**
  - <https://github.com/com-lihaoyi/mill>
  - https://raw.githubusercontent.com (README via gh api repos/com-lihaoyi/mill/readme)
  - https://mill-build.org/mill/comparisons/performance.html (fetched via gh api repos/com-lihaoyi/mill/contents/website/docs/modules/ROOT/pages/comparisons/performance.adoc)
  - <https://github.com/com-lihaoyi/mill/blob/main/example/thirdparty/netty/build.mill>
  - <https://github.com/com-lihaoyi/mill/blob/main/website/docs/modules/ROOT/pages/cli/installation-ide.adoc>
  - <https://github.com/com-lihaoyi/mill/issues/7381>
  - gh search issues --repo com-lihaoyi/mill "slow"
  - gh search issues --repo com-lihaoyi/mill "performance"
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/com-lihaoyi/mill`) · [data/wave2/enrich/raw/github_com_com_lihaoyi_mill.json](../../../data/wave2/enrich/raw/github_com_com_lihaoyi_mill.json) (enrichment confidence 0.8)

</details>
