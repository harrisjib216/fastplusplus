# Java HotSpot vs g++ -O3 virtual-call microbenchmark (gist)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Java` · `no license` · 🔴 abandoned

> 2009 gist: HotSpot Java 6 runs an alternating two-class virtual-call loop 2.3x faster than 32-bit g++ 4.0.1 -O3.

| | |
|---|---|
| **Beats** | C++ virtual dispatch compiled with g++ 4.0.1 -O3 -fomit-frame-pointer -march=pentium4 |
| **Claimed result** | C++ runs 1796.2, 1682.14, 1673.19, 1678.66, 1685.71, 1671.59, 1702.79, 1714.34, 1652.46, 1651.8 ms; Java 1.6.0_07 -server runs 967, 1036, 769, 740, 716, 718, 717, 716, 716, 717 ms; Scala 2.7.3 runs 1016, 951, 716, 717 ms. Units are not printed on the results gist but are milliseconds per the sources (C++ clock()-based CPU time, Java System.currentTimeMillis wall time). About 2.3x faster at steady state (1651.8 / 716) and 1.7x even on Java's first run (1651.8 / 967) (derived from page data). |
| **Workload** | Call a virtual perform() 400 million times through a base pointer that alternates every iteration between two derived classes (A adds 1, B adds 4). |
| **Metric** | latency |
| **Hardware** | PowerMac 2x2.8 GHz Xeon (8 cores), 4GB RAM |
| **Compiler and flags** | g++ -O3 -fomit-frame-pointer -march=pentium4 Bench.cpp (gcc version 4.0.1, Apple Inc. build 5493, Target: i686-apple-darwin9, so a 32-bit build since no -m64 is passed); javac Bench.java and java -server Bench on Java HotSpot(TM) 64-Bit Server VM (build 1.6.0_07-b06-57, mixed mode) |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | no |
| **Adoption** | 0 stars, 0 forks (gist) |
| **Last commit** | 2009-03-30 |
| **Links** | [repository](https://gist.github.com/87746) · [benchmark](https://gist.github.com/87746) |

## Verdict

On a 2x 2.8 GHz Xeon Mac (8 cores, Mac OS X 10.5), 400 million alternating virtual calls took 1651.8-1796.2 ms in C++ built by Apple g++ 4.0.1 -O3 -fomit-frame-pointer -march=pentium4 (32-bit i686) against 716-1036 ms in Java 1.6.0_07 on the 64-bit HotSpot Server VM (716-717 ms after warm-up), so about 2.3x faster at steady state and 1.7x on the first Java run (derived from page data); Scala 2.7.3 on the same JVM reached 716-717 ms.

## Use it when

- As a minimal, easy-to-read demonstration that a JIT with type profiles can beat an ahead-of-time indirect call at a hot call site that sees exactly two receiver types.
- When arguing whether to move hot polymorphic Java code to C++ through JNI: a plain C++ virtual call without devirtualization can lose to HotSpot's inlined dispatch, so a port needs templates, final classes, a type switch or PGO to pay off.
- As a starting point for a modern re-run (current GCC or Clang at -O2/-O3, with and without -fprofile-use, 64-bit target, against a current JDK) before quoting any ratio.

## Skip it when

- As evidence that Java beats current C++: the C++ side is Apple g++ 4.0.1 (2005-era compiler) building 32-bit code tuned with -march=pentium4 for a Xeon, against a 64-bit HotSpot VM, and no modern compiler, PGO or LTO build was measured.
- For megamorphic call sites (three or more receiver types), where HotSpot falls back to a vtable or itable call and the inlining advantage this loop shows does not apply.
- For short-lived processes or code that runs once: the first two Java iterations took 967 and 1036 ms (1015 and 955 ms in the gist's first revision) before settling around 716-769 ms.
- For C++ code that can already avoid the indirect call (templates or CRTP, std::variant with std::visit, final classes, or a manual type switch); those were not measured here.
- As a general language comparison: one call site, a global counter update as the only work, no memory traffic beyond that counter, and one author's single run per variant.

## How it is fast

The author gives no mechanism. The likely one is HotSpot's profile-guided bimorphic inlining: the call site's type profile records exactly two receiver classes, so C2 compiles a class check plus both inlined perform() bodies instead of a virtual call. g++ 4.0.1 has no devirtualization or profile feedback here, so each iteration is a real indirect call through the vtable, in a 32-bit i686 build that passes this on the stack. Derived from page data: about 11.6 cycles per iteration for C++ (1651.8 ms / 400M at 2.8 GHz) against about 5 cycles for Java at steady state (716 ms).

## Compared with alternatives

Prefer the LangArena and benchLANG HotSpot entries (GCC 16 and Clang 22 baselines, many C/C++ configurations) or xemantic/java-2-times-faster-than-c for current evidence; pick this gist only as the smallest isolated example of a JIT's bimorphic inlining beating an un-devirtualized C++ virtual call.

## Integration

| | |
|---|---|
| **Form** | source-drop (three short gists: C++ 87516, Java 87518, Scala 87760) |
| **Dependencies** | none (C++ &lt;ctime&gt; and &lt;iostream&gt;; Java SE 6; Scala 2.7.3 library for the Scala variant) |
| **Minimum toolchain** | as published: Apple g++ 4.0.1 (build 5493), Java 1.6.0_07, Scala 2.7.3; any C++98 compiler and JDK 6+ should build it |
| **Platforms** | measured on Mac OS X (darwin9) on 2x 2.8 GHz Xeon, 8 cores; C++ built 32-bit (i686) and Java run on the 64-bit HotSpot Server VM |
| **Thread safety** | not applicable (single-threaded microbenchmark) |
| **Drop-in for the baseline** | no |

## Gotchas

- The published C++ source does not match the posted numbers: gist 87516 went from four bench() calls (29 March) to a 10-iteration loop and then, in its latest revision, five bench() lines that the page shows without semicolons, while the results gist lists ten C++ timings in one block from its first revision. The ten numbers most likely come from one run of the 10-iteration revision, not from two runs of the five-call version as the verifier assumed; the kernel (400M-iteration loop, A/B classes, (i & 1) alternation, clock() timing) never changed.
- The Java command line was edited after the measurement: revision 5 of the results gist posted the 967/1036/769/... numbers under 'java Bench -J-Server', which passes '-J-Server' to Bench.main as an ignored program argument rather than to the VM, and a later revision only relabelled it 'java -server Bench'. The effect is cosmetic because the reported VM is the 64-bit HotSpot Server VM and the first revision's plain 'java Bench' run (1015, 955, then 716-754 ms) shows the same steady state.
- The C++ counter is a signed 'static int' that receives 1,000,000,000 per bench() call, so it overflows INT_MAX during the third call, which is undefined behaviour in C++ (Java's int wraps by definition); the printed final count is meaningless and is not a cross-language checksum, though the overflow is unlikely to have changed the timing.
- C++ is timed with clock() (process CPU time) and Java with System.currentTimeMillis() (wall time, which includes JIT compilation during the first iterations); 'PowerMac' in the hardware line is presumably an Intel Mac Pro, since the gcc target is i686-apple-darwin9, and the CPU model is not stated.

## Known shortcomings

- 2009 microbenchmark: g++ 4.0.1 targeting 32-bit pentium4 against a 64-bit JVM, no CPU model, no licence (reference).
- The published C++ source does not match the numbers: the latest gist 87516 shows five bench() calls (without semicolons) while the results list ten C++ timings, which most likely come from an earlier 10-iteration revision. The Java numbers were first posted under 'java Bench -J-Server' (the flag passed to Bench as an ignored argument) and later relabelled 'java -server Bench' (cosmetic: already a 64-bit Server VM). The C++ static int counter overflows INT_MAX in the third call (UB). The mechanism is probably bimorphic inlining (about 11.6 vs 5 cycles per iteration, derived).

## Caveats and trade-offs

From 2009 with Apple g++ 4.0.1 targeting 32-bit i686 with -march=pentium4 on a Xeon, against a 64-bit HotSpot VM, so the targets differ. No profile-guided optimization or modern speculative devirtualization for C++, which could remove the alternating indirect call; a current GCC or Clang was not measured. One call site microbenchmark (400 million alternating virtual calls incrementing a global), not a general claim. The C++ main() calls bench() 5 times, so the 10 C++ numbers come from two program runs; Java runs 10 iterations in one JVM, so later runs are fully JIT-compiled. C++ times process CPU time (clock()), Java wall time. Benchmark sources are in two other gists (87516 C++, 87518 Java); no license; CPU model not stated beyond '2.8 GHz Xeon'. Mechanism not stated by the author. Tier capped at C. [retier] From 2009 with Apple g++ 4.0.1 targeting 32-bit i686 (-march=pentium4) on a Xeon against a 64-bit HotSpot VM, so the targets differ; no PGO or modern speculative devirtualisation for C++. One call site (400 million alternating virtual calls incrementing a global), not a general claim. The published C++ source does not match the numbers: the latest revision of gist 87516 shows five bench() calls (without semicolons) while the results list ten C++ timings, which most likely come from an earlier 10-iteration revision. The Java numbers were first posted under 'java Bench -J-Server' (the flag passed to Bench as an ignored argument) and later relabelled 'java -server Bench' (cosmetic: already a 64-bit Server VM). The C++ static int counter overflows INT_MAX in the third call (UB). The mechanism is probably bimorphic inlining (about 11.6 vs 5 cycles per iteration, derived from page data).

Java needs warm-up (first runs 967 and 1036 vs 716 steady state) and a JVM; a toy loop.

## Maintenance

Abandoned since 30 March 2009, no license, reference-only; the code is trivial to re-run, and any use of the 2.3x figure should be preceded by a re-measurement with a current 64-bit GCC or Clang build (ideally with and without PGO).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Code for both sides is public (gists 87516 C++ and 87518 Java by the same author) and compiler, flags and JVM are stated, but the CPU is given only as '2x 2.8 GHz Xeon (8 cores)' with no model, and the numbers are a single individual's one-off measurement, so it falls short of A and is not independent or peer-reviewed.
- **Verifier notes:** Numbers verified on the gist; units are milliseconds per the source gists. Tier C confirmed. Shortcomings to record: 2009 toolchain (g++ 4.0.1, 32-bit pentium4 target vs 64-bit JVM), single-call-site microbenchmark, no CPU model, no license, author's one-off run; same_opt_level stays false because of the 32-bit/pentium4 target mismatch even though C++ was -O3.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-26 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://gist.github.com/87746>
  - <https://gist.github.com/hipertracker/87746>
  - <https://gist.github.com/87516>
  - <https://gist.github.com/87518>
- **Sources the enricher read:**
  - <https://gist.github.com/87746>
  - <https://gist.github.com/hipertracker/87746/revisions>
  - <https://gist.github.com/hipertracker/87516>
  - <https://gist.github.com/hipertracker/87516/revisions>
  - <https://gist.github.com/hipertracker/87518>
  - <https://gist.github.com/hipertracker/87518/revisions>
  - <https://gist.github.com/hipertracker/87760>
  - https://gist.github.com/87746/download (403 via proxy)
  - https://gist.githubusercontent.com/hipertracker/87516/raw (proxy CONNECT 403; ENOTFOUND via WebFetch)
  - WebSearch: 'hipertracker "Java & Scala vs C++ benchmark" OR "Java vs C++ benchmark" 2009 virtual perform 400000000' (no discussion or rebuttal found)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://gist.github.com/87746`) · [data/wave14/enrich/raw/gist_github_com_87746.json](../../../data/wave14/enrich/raw/gist_github_com_87746.json) (enrichment confidence 0.6)

</details>
