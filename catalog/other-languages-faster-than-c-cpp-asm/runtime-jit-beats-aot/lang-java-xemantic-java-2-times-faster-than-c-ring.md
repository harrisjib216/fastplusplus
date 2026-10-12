# HotSpot Java ring-of-nodes mutation vs C at gcc -O3: xemantic/java-2-times-faster-than-c

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Java` · `GPL-3.0` · 🔴 abandoned

> HotSpot Java ring-of-nodes churn 1.49x faster than gcc -O3 C doing malloc/free per node; partly sin.

| | |
|---|---|
| **Beats** | C ring-of-nodes program (src/main/c/java_2_times_faster_than_c.c, malloc and free per node and per payload) built with gcc -O3; the README's 'Clang' row comes from build-clang.sh, which actually invokes gcc |
| **Claimed result** | Java (HotSpot) 8.569 s vs GCC C 12.800 s and 'Clang' (actually gcc) C 12.726 s (real time, one run each): about 1.49x faster than C (derived from page data). The project title claims 2x and the README dialogue says 'almost 2 times faster'; the measured ratio is about 1.5x. |
| **Workload** | Build a ring of 10,000 nodes with a pseudo-random payload of 0-49 bytes, then run 1,000,000 mutations that each delete and insert up to 200 nodes; node count and checksum are identical in every implementation. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-8550U @ 1.80GHz (4 cores, 8 threads), about 16 GB RAM (README /proc/cpuinfo dump) |
| **Compiler and flags** | C: gcc -O3 -lm (build-gcc.sh); build-clang.sh also calls gcc -O3, not clang; compiler and glibc versions not stated. Java: Gradle build with source and target level 15, run as java -cp build/classes/java/main with default JVM flags (JDK build not stated). |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | Author's hypothesis: certain algorithms gain performance just from being expressed with automatic memory management, because the C version pays a malloc and a free per node and per payload while the JVM allocates and reclaims in bulk. The README adds that better memory management in C (issue #1) can beat the Java version. |
| **Adoption** | 53 stars |
| **Last commit** | 2021-02-06 |
| **Links** | [repository](https://github.com/xemantic/java-2-times-faster-than-c) · [benchmark](https://raw.githubusercontent.com/xemantic/java-2-times-faster-than-c/HEAD/README.md) |

## Verdict

On an Intel Core i7-8550U laptop, one shell 'time' run each: Java (HotSpot of the Java 15 era, default flags) 8.569 s vs the C version built with gcc -O3 -lm 12.800 s (12.726 s for a second gcc build labelled Clang), with identical node count 13537 and checksum 470936697371, about 1.49x (derived from page data). gcc, glibc and JDK versions are not stated, and a large share of the C time is glibc's large-argument sin rather than malloc and free.

## Use it when

- Workloads that churn many small, short-lived, variable-size objects in a linked structure (caches, request pipelines) where the C alternative would call malloc and free per object: here the JVM's allocator and collector beat that pattern.
- As a counter-example to 'garbage collection always costs throughput', citing the measured 1.49x rather than the title's 2x and noting the sin share.
- As a starting harness for allocator experiments: the C file is about 100 lines, prints a checksum that every faithful port must match (node count 13537, checksum 470936697371), and is easy to rerun with a pool, an arena or another malloc.

## Skip it when

- When you control the C code: the author concedes better memory management in C can beat the Java version, and in issue #1 a one-slot node reuse cut an earlier version of the C program from 1m7s to 14s (no Java figure on that run).
- Memory-constrained or embedded targets: JVM memory use was not measured, and the README itself lists a higher memory footprint as a reason not to use Java.
- Short-lived processes where JVM start-up and JIT warm-up dominate (they are inside the 8.569 s here, but the run is long enough to hide them).
- As evidence of a pure GC win: roughly a third of the measured gap is glibc's slow large-argument sin, and the sin-free xorshift64\* variant in open PR #9 was never timed in text.
- As a current result: one run from February 2021 on unstated gcc, glibc and JDK versions; the Rust rows predate the mimalloc change in PR #10 and were not rerun.

## How it is fast

Two effects add up. Allocation: the JVM hands out memory from a heap it reserved at start-up (bump-pointer allocation, generational GC that never visits dead nodes), as issue #1 and #2 commenters note, while C pays two malloc and two free calls per node; issue #13's gprof profile puts malloc, _int_malloc, _int_free and free at about 13% of C run time and the inlined list work in main at 21.79%. Trigonometry: every node and mutation calls sin on arguments above glibc's 1.05e8 threshold, so glibc runs its slow __branred reduction (47.88% plus __sin_fma 17.32% in the same profile), while HotSpot's Intel LIBM sin intrinsic handles large arguments faster (1.26x in the repo's second benchmark).

## Compared with alternatives

The benchLANG HotSpot entry (Java 25, 2.9x over malloc/free C built with GCC 16.2.0) and LangArena Binarytrees::Obj (Java 27, 0.479 s vs 2.098 s for the best C/C++ build) show the same allocation effect with stated toolchains and no libm confound, so cite those first; use this one for its ring-mutation, variable-size-payload shape or for the documented history of how C fixes (memset, node reuse) erase the gap.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | C: libc malloc and libm. Java: none at run time; the provided build uses the Gradle 6.8 wrapper with the Kotlin JVM plugin 1.4.21 and still lists the Bintray Kotlin EAP repository (dl.bintray.com). |
| **Minimum toolchain** | JDK 15 (Gradle source and target level 15) and any C compiler with libm; the README results used gcc -O3 without -march=native. |
| **Platforms** | Measured only on x86-64 Linux (Intel Core i7-8550U, about 16 GB RAM); the sin share depends on glibc's x86-64 path and HotSpot's x86-64 sin intrinsic. |
| **Thread safety** | not applicable (single-threaded benchmark programs; the JVM adds its own JIT and GC threads) |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: the 'pseudo-random' sizes come from sin on huge arguments, so most of the C time is libm, not memory management: issue #13's gprof profile shows __branred 47.88% plus __sin_fma 17.32% against about 13% for malloc and free, and a contributor's profile in PR #7 found 59% in almost_pseudo_random (clang build). With about 1e8 sin calls and the second benchmark's per-call times (64.4 ns C, 51.2 ns Java), sin explains roughly 1.3-1.7 s of the 4.2 s gap, and outside sin Java is still about 1.9-2.3x faster (derived estimate, assumes the per-call cost carries over).
- Workload history: the January 2021 version (payloads up to 10,000 bytes; Java filled them with Arrays.fill, C with a raw byte loop that gcc did not turn into memset) showed C 1m21.495s vs Java 23.129s. After PR #7 switched C to memset, the contributor reported C about 5 s faster than Java, and commit 25d2bd8 then changed the workload (payloads up to 50 bytes, 10,000 initial nodes, 1e6 mutations of up to 200 nodes, per-byte fill loops in both); the current numbers come from that commit.
- One shell 'time' run per language on a laptop CPU without frequency locking; the 'Clang' row (12.726 s) comes from build-clang.sh, which calls gcc, and the C build has no -march=native. Java's user plus sys time (8.818 s) is still well below C's 12.8 s, so extra JVM threads do not explain the gap.
- The title says 2x and the README dialogue 'almost 2 times'; the measured ratio is 1.49x. The Go port ran different work (node count 13553, checksum 486105193130) because Go's sin returns different values.

## Known shortcomings

- First-party single run with gcc, glibc and JDK versions unstated; the 'Clang' row was built with gcc; measured ratio 1.49x although the title says 2x; the issue #13 profile puts about two thirds of C time in glibc sin and about 13% in malloc/free, so GC explains only part of the gap; the Go row ran different work (node count 13553).
- Harness flaw: sin dominates the C time. The issue #13 profile has __branred at 47.88% plus __sin_fma 17.32% with malloc and free about 13% (the PR #7 profile: 59%); by estimate sin explains about 1.3-1.7 s of the 4.2 s gap, so outside sin Java is still about 1.9-2.3x faster. History: after PR #7 (memset) made C about 5 s faster than Java, commit 25d2bd8 changed the workload, and the README numbers come from that commit; the Rust rows predate the mimalloc PR #10; the open PR #9 (sin-free xorshift64\*) was never timed in the text.

## Caveats and trade-offs

One run per implementation measured with the shell 'time' on a laptop CPU without frequency locking (no variance). gcc, glibc and JDK versions are not stated (Gradle targets Java 15), the C build has no -march=native while the JIT targets the host CPU, and the 'Clang' row was built with gcc by build-clang.sh. A large share of the C time is libm, not memory management: issue #13 (2025-06-12) profiles this C program with gprof and finds glibc's large-argument sin reduction __branred at 47.88% and __sin_fma at 17.32% of run time, against about 13% for malloc, _int_malloc, _int_free and free together; every new node and every mutation count calls sin() on arguments up to about 1e13, and the second benchmark in the repo shows HotSpot's sin faster than glibc's (Java 51.2 s vs C 64.4 s for 1e9 calls). The C version pays two malloc and two free calls per node (node and payload, including malloc(0) for empty payloads) where the JVM bump-allocates and never traces dead nodes; the author calls the title provocative, says it applies only to this algorithm, and notes that better memory management in C (issue #1, where one commenter's one-slot reuse cut a run from 1m7s to 14s, no Java figure) can beat the Java version. Contributed Rust (13.824 s, glibc sin) was slower than C; Go (14.542 s) ran different work (node count 13553, checksum 486105193130, because its sin differs); C# took 34.037 s. [retier] sin dominates the C time (issue #13 profile: __branred 47.88% plus __sin_fma 17.32%, malloc and free about 13%); by estimate sin explains about 1.3-1.7 s of the 4.2 s gap, so outside sin Java is still about 1.9-2.3x faster. After PR #7 (memset) made C about 5 s faster than Java, commit 25d2bd8 changed the workload, and the README numbers come from that commit; the Rust rows predate the mimalloc PR #10; the open PR #9 (sin-free xorshift64\*) was never timed.

JVM needs a runtime and has higher memory use (not measured in the README). The C version could be sped up with a pool or arena allocator, which the author deliberately did not add.

## Maintenance

Abandoned since February 2021 (README numbers from commit 25d2bd8 of 2021-02-04; open PR #9 with a sin-free xorshift64\* generator was never merged or timed in text), GPL-3.0 and easy to rerun, but rerun it with a sin-free generator before citing it as a garbage-collection win.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** First-party README shell 'time' output, one run each: Java 8.569 s vs gcc C 12.800 s and the 'Clang' row 12.726 s, identical node count 13537 and checksum 470936697371. The code (src/main/c/java_2_times_faster_than_c.c, Java2TimesFasterThanC.java, build-gcc.sh) and the CPU (i7-8550U) are public, but the gcc, glibc and JDK versions are unstated and the 'Clang' row is mislabelled, so it falls short of A.
- **Verifier notes:** Numbers match the README (1.49x derived from page data; title's 2x is overstated) but the evidence is first-party, single-run, with gcc, glibc and JDK versions unstated, so A drops to C. Record the shortcoming that issue #13 shows about two thirds of the C run time in glibc sin (__branred plus __sin_fma) against about 13% in malloc/free, so the memory-management explanation covers only part of the gap. The id lang:java/xemantic/java-2-times-faster-than-c#node-ring (batch 56, from w14-jitaot-shootouts) is the same benchmark and should be folded into this id as a duplicate.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
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
  - <https://raw.githubusercontent.com/xemantic/java-2-times-faster-than-c/HEAD/src/main/c/java_2_times_faster_than_c.c>
  - <https://raw.githubusercontent.com/xemantic/java-2-times-faster-than-c/HEAD/src/main/java/com/xemantic/test/howfast/Java2TimesFasterThanC.java>
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
  - <https://raw.githubusercontent.com/xemantic/java-2-times-faster-than-c/HEAD/src/main/c/java_2_times_faster_than_c.c>
  - <https://raw.githubusercontent.com/xemantic/java-2-times-faster-than-c/HEAD/src/main/java/com/xemantic/test/howfast/Java2TimesFasterThanC.java>
  - <https://raw.githubusercontent.com/xemantic/java-2-times-faster-than-c/HEAD/src/main/c/almost_pseudo_random.c>
  - <https://raw.githubusercontent.com/xemantic/java-2-times-faster-than-c/HEAD/src/main/java/com/xemantic/test/howfast/AlmostPseudoRandom.java>
  - <https://raw.githubusercontent.com/tritoke/java-2-times-faster-than-c/xorshift_rng/README.md>
  - <https://raw.githubusercontent.com/tritoke/java-2-times-faster-than-c/xorshift_rng/src/main/java/com/xemantic/test/howfast/Java2TimesFasterThanC.java>
  - <https://raw.githubusercontent.com/openjdk/jdk/master/src/hotspot/cpu/x86/stubGenerator_x86_64_sin.cpp>
  - <https://raw.githubusercontent.com/openjdk/jdk15u/master/src/hotspot/cpu/x86/macroAssembler_x86_sin.cpp>
  - <https://raw.githubusercontent.com/openjdk/jdk15u/master/src/hotspot/cpu/x86/stubGenerator_x86_64.cpp>
  - <https://raw.githubusercontent.com/openjdk/jdk15u/master/src/hotspot/cpu/x86/globals_x86.hpp>
  - <https://raw.githubusercontent.com/bminor/glibc/master/sysdeps/ieee754/dbl-64/s_sin.c>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:java/xemantic/java-2-times-faster-than-c#ring`) · [data/wave14/enrich/raw/lang_java_xemantic_java_2_times_faster_than_c_ring.json](../../../data/wave14/enrich/raw/lang_java_xemantic_java_2_times_faster_than_c_ring.json) (enrichment confidence 0.7)

</details>
