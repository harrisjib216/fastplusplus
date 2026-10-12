# HotSpot Java Math.sin/% loop vs C libm sin/fmod at gcc -O3: xemantic/java-2-times-faster-than-c

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Java` · `GPL-3.0` · 🔴 abandoned

> Java Math.sin loop 1.26x faster than gcc -O3 C with glibc sin, on huge arguments only.

| | |
|---|---|
| **Beats** | C loop calling libm sin() and fmod() (src/main/c/almost_pseudo_random.c) built with gcc -O3 -lm; the README's 'Clang' row again comes from a gcc build |
| **Claimed result** | Java 51.235 s vs GCC C 1 m 4.433 s and 'Clang' C 1 m 4.878 s (real time, one run each): about 1.26x faster than gcc C (derived from page data). Contributed Go finished in 28.191 s (faster than both), Rust in 1 m 7.944 s. |
| **Workload** | Sum fmod(sin(i \* 100000.0) + 1.0, 1.0) for 1,000,000,000 iterations (a trigonometry-based pseudo-random function from The Book of Shaders). |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-8550U @ 1.80GHz (4 cores, 8 threads), about 16 GB RAM (README /proc/cpuinfo dump) |
| **Compiler and flags** | C: gcc -O3 -lm with no -ffast-math (build-gcc.sh); compiler and glibc versions not stated. Java: Gradle build with source level 15, default JVM flags. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | Author cannot fully explain it and lists hypotheses: HotSpot inlines aggressively after profiling, C math functions come from a library and cannot be inlined, and Java's % operator on doubles may map to better machine code. |
| **Adoption** | 53 stars |
| **Last commit** | 2021-02-06 |
| **Links** | [repository](https://github.com/xemantic/java-2-times-faster-than-c) · [benchmark](https://raw.githubusercontent.com/xemantic/java-2-times-faster-than-c/HEAD/README.md) |

## Verdict

On an Intel Core i7-8550U laptop, one shell 'time' run each: the Java loop (HotSpot of the Java 15 era, default flags) took 51.235 s and the same loop in C built with gcc -O3 -lm took 1m4.433s (1m4.878s for a second gcc build labelled Clang), about 1.26x (derived from page data); Rust on glibc took 1m7.944s and Go with its own sin 28.191 s. gcc, glibc and JDK versions are not stated, and the time is almost all large-argument sin.

## Use it when

- JVM code whose hot loops call Math.sin or Math.cos on very large arguments (above about 1e8 radians), such as GLSL-style fract(sin(x \* k)) noise ported from shaders: HotSpot's x86-64 intrinsic beat glibc by about 1.26x there.
- As a two-file test to rerun on your own JDK and glibc before trusting either for trig-heavy code; both versions print the same checksum to the printed digits (4.9999999712235045E8 vs 499999997.122350).
- As a teaching example that the math library, not the language or the JIT, decides trig-bound microbenchmarks (Rust on glibc 67.9 s matches C; Go's own sin 28.2 s beats both).

## Skip it when

- As evidence that HotSpot generates faster code than gcc: the timed work is almost entirely inside sin, so code generation barely enters.
- For ordinary angles: below about 1.05e8 glibc uses its cheaper reduce_sincos path and HotSpot stays on its main path below 90112, so the measured ratio does not carry over (not measured in the repo).
- As a pseudo-random generator: fract(sin(x)) costs about 64 ns per call in C here and differs across libraries (Go's checksum is 4.999999924931206e+08); open PR #9 proposes xorshift64\*, which its author reports is about 35x faster and identical across languages.
- When C code can switch implementation: Go's own sin finished in 28.2 s on the same machine, faster than both Java and glibc, so the gap is a library choice rather than a language property.
- On non-x86-64 platforms: only HotSpot's x86-64 Intel LIBM stub and glibc's x86-64 ifunc variant (__sin_fma) were involved.

## How it is fast

The loop is one libm call per iteration, so the result compares two sin implementations. Every argument with i &gt;= 1055 is at least 1.054e8, past glibc's 0x419921FB threshold in s_sin.c, so glibc sends nearly all 1e9 calls to its slow large-argument reduction __branred (the issue #13 gprof profile of the repo's other C program puts __branred at 47.88% of run time and __sin_fma at 17.32%). HotSpot replaces Math.sin with a hand-written x86-64 stub derived from Intel LIBM (generate_libmSin, on by default via UseLibmIntrinsic in JDK 15); its main path covers only |x| &lt; 90112, and larger arguments go through an inline Payne-Hanek-style reduction against a 2/pi bit table (PI_INV_TABLE), which was faster here. The author's hypotheses about inlining and Java's double % are not needed to explain the gap.

## Compared with alternatives

Use this only as evidence about sin on huge arguments (HotSpot's Intel LIBM stub against glibc's __branred). For claims about JIT code generation, the LangArena and benchLANG HotSpot entries state their toolchains and measure more than one library call; the sibling ring entry from the same repo is about allocation but inherits this sin cost.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | C: libm only. Java: none at run time; the provided build uses the Gradle 6.8 wrapper with the Kotlin JVM plugin 1.4.21 and still lists the Bintray Kotlin EAP repository (dl.bintray.com). |
| **Minimum toolchain** | JDK 15 (Gradle source and target level 15) and any C compiler with libm; the README results used gcc -O3. |
| **Platforms** | Measured only on x86-64 Linux (Intel Core i7-8550U); the Java advantage depends on HotSpot's x86-64 sin intrinsic and on the glibc version, both platform-specific. |
| **Thread safety** | not applicable (single-threaded benchmark programs) |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw in what is measured: i \* 100000.0 puts all but about 1,054 of the 1e9 arguments above glibc's 1.05e8 threshold, so the benchmark measures only large-argument range reduction (glibc __branred against HotSpot's PI_INV_TABLE path), a regime real code rarely hits.
- The result depends on the glibc and JDK builds, and neither version is stated (Gradle targets Java 15; the README mentions 'the newest JVM of Java 15'); glibc picks __sin_fma at run time on FMA-capable CPUs such as the i7-8550U.
- One shell 'time' run per language on a laptop CPU without frequency locking; the 'Clang' row (1m4.878s) comes from build-clang.sh, which calls gcc, so there is no clang measurement.
- Java's 51.235 s includes JVM start-up and JIT warm-up, which count against Java; user time (51.193 s) is close to real time, so extra JVM threads do not explain the gap.

## Known shortcomings

- First-party single run; gcc, glibc and JDK versions unstated; compares glibc sin with HotSpot's Intel LIBM sin intrinsic rather than language codegen (issue #13 gprof: __branred 47.88%, __sin_fma 17.32%).
- Harness flaw: the benchmark times sin on huge arguments, not JIT code generation. i\*1e5 exceeds glibc's 0x419921FB threshold (about 1.05e8) for every i &gt;= 1055, so nearly all 1e9 calls go to glibc's __branred slow reduction, and they are also past the 90112 main-path limit of HotSpot's Intel LIBM sin stub (generate_libmSin, UseLibmIntrinsic on by default in JDK 15), which uses its own PI_INV_TABLE reduction. Go's own sin ran in 28.2 s and beat both. The result does not carry over to ordinary angles.

## Caveats and trade-offs

One run per implementation (shell 'time') on a laptop CPU without frequency locking; gcc, glibc and JDK versions not stated (Gradle targets Java 15, and the README mentions 'the newest JVM of Java 15'). The 'Clang' row was built by build-clang.sh, which calls gcc. The loop spends nearly all its time in sin(): arguments reach 1e14, far outside the fast range of both libraries, so the gap measures two sin implementations rather than language code generation. Issue #13 (2025-06-12) profiles the repo's C ring program with gprof and finds glibc's large-argument reduction __branred at 47.88% and __sin_fma at 17.32% of run time. Java's Math.sin is a HotSpot intrinsic generated from Intel LIBM assembly (current openjdk master stubGenerator_x86_64_sin.cpp, main path only for |x| &lt; 90112); the 2021 JDK build was not checked. Rust, which also calls glibc sin, took 1m7.944s (about C's time), and Go, with its own sin and slightly different results (checksum 4.999999924931206e+08), took 28.191 s. The Java checksum prints as 4.9999999712235045E8 against 499999997.122350 for C (same value to the printed digits). gcc ran without -ffast-math or -fno-math-errno, so sin and fmod stay library calls, which matches Java's strict semantics. [retier] The benchmark times sin on huge arguments: i\*1e5 exceeds glibc's 0x419921FB threshold (about 1.05e8) for every i &gt;= 1055, so nearly all 1e9 calls go to glibc's __branred slow reduction, and they are past the 90112 main-path limit of HotSpot's Intel LIBM sin stub (UseLibmIntrinsic on by default in JDK 15), which uses its own PI_INV_TABLE reduction. Go's own sin ran in 28.2 s and beat both. The result does not carry over to ordinary angles.

Measures the speed of the runtime's sin and floating-point remainder implementation against glibc's, not general code generation; JVM start-up and memory not compared.

## Maintenance

Abandoned since February 2021 (last commit 2021-02-06; open PR #9, which replaces the sin-based generator with xorshift64\*, was never merged), GPL-3.0 and trivial to rerun, but the result reflects glibc's large-argument sin against HotSpot's intrinsic, not JIT code generation.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now D.
- **Tier reason:** First-party README shell 'time' output, one run each: Java 51.235 s vs gcc C 1m4.433s and the 'Clang' row 1m4.878s. The code (src/main/c/almost_pseudo_random.c, AlmostPseudoRandom.java, build-gcc.sh) and the CPU (i7-8550U) are public, but the gcc, glibc and JDK versions are not stated, and for a benchmark that times only the math library the glibc and JDK versions decide the result, so it falls short of A.
- **Retiered** C to D: Enricher: nearly every one of the 1e9 sin calls takes glibc's __branred huge-argument reduction while HotSpot's LIBM stub uses its own table, so the single-run 1.26x measures libm argument reduction on degenerate inputs rather than JIT codegen, and Go's sin beats both; degenerate-workload precedent: C to D.
- **Verifier notes:** Numbers match the README (1.26x derived from page data) but the evidence is first-party, single-run, with gcc, glibc and JDK versions unstated, so A drops to C. Keep with the shortcoming that the timed work is a library sin() comparison (glibc vs HotSpot's Intel LIBM intrinsic), so it is not a language-level or JIT code-generation win; record corrections to why_faster and the language_level_claim stays false.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-53 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/xemantic/java-2-times-faster-than-c/HEAD/README.md>
  - <https://github.com/xemantic/java-2-times-faster-than-c>
  - <https://github.com/xemantic/java-2-times-faster-than-c/commits>
  - <https://github.com/xemantic/java-2-times-faster-than-c/issues>
  - <https://github.com/xemantic/java-2-times-faster-than-c/issues/1>
  - <https://github.com/xemantic/java-2-times-faster-than-c/issues/13>
  - <https://raw.githubusercontent.com/xemantic/java-2-times-faster-than-c/HEAD/build-gcc.sh>
  - <https://raw.githubusercontent.com/xemantic/java-2-times-faster-than-c/HEAD/build-clang.sh>
  - <https://raw.githubusercontent.com/xemantic/java-2-times-faster-than-c/HEAD/build.gradle.kts>
  - <https://raw.githubusercontent.com/xemantic/java-2-times-faster-than-c/HEAD/src/main/c/almost_pseudo_random.c>
  - <https://raw.githubusercontent.com/xemantic/java-2-times-faster-than-c/HEAD/src/main/java/com/xemantic/test/howfast/AlmostPseudoRandom.java>
  - <https://raw.githubusercontent.com/xemantic/java-2-times-faster-than-c/HEAD/src/main/c/java_2_times_faster_than_c.c>
  - <https://raw.githubusercontent.com/openjdk/jdk/master/src/hotspot/cpu/x86/stubGenerator_x86_64_sin.cpp>
- **Sources the enricher read:**
  - <https://github.com/xemantic/java-2-times-faster-than-c>
  - <https://github.com/xemantic/java-2-times-faster-than-c/commits>
  - <https://github.com/xemantic/java-2-times-faster-than-c/commits/main>
  - <https://github.com/xemantic/java-2-times-faster-than-c/commit/25d2bd81fe60a9ef8bc9ef962d50333e217a8f2d>
  - <https://github.com/xemantic/java-2-times-faster-than-c/issues?q=is%3Aissue>
  - <https://github.com/xemantic/java-2-times-faster-than-c/issues/1>
  - <https://github.com/xemantic/java-2-times-faster-than-c/issues/2>
  - <https://github.com/xemantic/java-2-times-faster-than-c/issues/13>
  - <https://github.com/xemantic/java-2-times-faster-than-c/pulls?q=is%3Apr>
  - <https://github.com/xemantic/java-2-times-faster-than-c/pull/7>
  - <https://github.com/xemantic/java-2-times-faster-than-c/pull/9>
  - <https://github.com/xemantic/java-2-times-faster-than-c/pull/9/files>
  - <https://github.com/xemantic/java-2-times-faster-than-c/pull/10>
  - <https://raw.githubusercontent.com/xemantic/java-2-times-faster-than-c/HEAD/README.md>
  - <https://raw.githubusercontent.com/xemantic/java-2-times-faster-than-c/HEAD/build-gcc.sh>
  - <https://raw.githubusercontent.com/xemantic/java-2-times-faster-than-c/HEAD/build-clang.sh>
  - <https://raw.githubusercontent.com/xemantic/java-2-times-faster-than-c/HEAD/build-rs.sh>
  - <https://raw.githubusercontent.com/xemantic/java-2-times-faster-than-c/HEAD/build.gradle.kts>
  - <https://raw.githubusercontent.com/xemantic/java-2-times-faster-than-c/HEAD/gradle/wrapper/gradle-wrapper.properties>
  - <https://raw.githubusercontent.com/xemantic/java-2-times-faster-than-c/HEAD/src/main/c/almost_pseudo_random.c>
  - <https://raw.githubusercontent.com/xemantic/java-2-times-faster-than-c/HEAD/src/main/java/com/xemantic/test/howfast/AlmostPseudoRandom.java>
  - <https://raw.githubusercontent.com/xemantic/java-2-times-faster-than-c/HEAD/src/main/c/java_2_times_faster_than_c.c>
  - <https://raw.githubusercontent.com/xemantic/java-2-times-faster-than-c/HEAD/src/main/java/com/xemantic/test/howfast/Java2TimesFasterThanC.java>
  - <https://raw.githubusercontent.com/tritoke/java-2-times-faster-than-c/xorshift_rng/README.md>
  - <https://raw.githubusercontent.com/tritoke/java-2-times-faster-than-c/xorshift_rng/src/main/java/com/xemantic/test/howfast/Java2TimesFasterThanC.java>
  - <https://raw.githubusercontent.com/openjdk/jdk/master/src/hotspot/cpu/x86/stubGenerator_x86_64_sin.cpp>
  - <https://raw.githubusercontent.com/openjdk/jdk15u/master/src/hotspot/cpu/x86/macroAssembler_x86_sin.cpp>
  - <https://raw.githubusercontent.com/openjdk/jdk15u/master/src/hotspot/cpu/x86/stubGenerator_x86_64.cpp>
  - <https://raw.githubusercontent.com/openjdk/jdk15u/master/src/hotspot/cpu/x86/globals_x86.hpp>
  - <https://raw.githubusercontent.com/bminor/glibc/master/sysdeps/ieee754/dbl-64/s_sin.c>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:java/xemantic/java-2-times-faster-than-c#almost-pseudo-random`) · [data/wave14/enrich/raw/lang_java_xemantic_java_2_times_faster_than_c_almost_pseudo_random.json](../../../data/wave14/enrich/raw/lang_java_xemantic_java_2_times_faster_than_c_almost_pseudo_random.json) (enrichment confidence 0.75)

</details>
