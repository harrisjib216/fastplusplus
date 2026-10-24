# Bazel

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Build systems](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Java` · `Apache-2.0` · 🟢 active

> Google's client-server build system; beats default-rules GNU Make on large null and incremental builds, loses to Ninja.

| | |
|---|---|
| **Beats** | GNU Make 4.3 with default built-in rules (also measured: Make with --no-builtin-rules --no-builtin-variables, and Ninja 1.11.1, both of which beat Bazel) |
| **Claimed result** | Bazel's own README claims only 'fast and incremental builds' (no numbers). Third-party table, x86_64, 100,000 modules: incremental build Bazel 61.911 s vs recursive Make (default rules) 692.201 s and single Make 292.019 s (about 11x and 4.7x, derived from page data); null build Bazel 20.193 s vs 688.101 s and 285.583 s (about 34x and 14x, derived from page data). At 5,000 modules: incremental 4.040 s vs 22.408 s / 24.813 s; null 1.091 s vs 22.236 s / 24.473 s. NEGATIVE results in the same table: Ninja is faster at every size (100,000 modules: incremental 10.358 s, null 7.073 s, full 407.131 s vs Bazel 61.911 s, 20.193 s, 1381.402 s), Make run with --no-builtin-rules is also faster than Bazel for incremental and null builds (9.486 s and 7.816 s recursive at 100,000 modules), and Bazel's full build is slower than every Make and Ninja variant (e.g. 82.779 s vs 28.723 s Make and 6.079 s Ninja at 5,000 modules). |
| **Workload** | Third-party overhead benchmark: N simulated modules (50 to 100,000) whose build rules only touch 0-byte files, measured as full build, incremental build (one most-imported interface file rewritten) and null build (nothing changed), parallelism 4, one run per cell. |
| **Metric** | build-time |
| **Hardware** | x86_64 run: 4 CPUs, 7G RAM, Linux 6.8.0-48-generic (Ubuntu 22.04); Arm run: aarch64 4 CPUs, 7G, Linux 6.8.0-1018-raspi (kernel name suggests a Raspberry Pi); CPU model not stated; runs dated 2025-02-10/11 |
| **Compiler and flags** | No compiler involved (rules touch 0-byte files); tools run with no arguments plus Make with --no-builtin-rules --no-builtin-variables; GNU Make 4.3, Ninja 1.11.1, Bazel 8.0.1 on the Arm runs, Bazel version recorded as 'no_version' on the x86_64 runs. |
| **Adoption** | 26.0k stars; Google's open-source build system |
| **Last commit** | 2026-10-24 |
| **Links** | [repository](https://github.com/bazelbuild/bazel) · [benchmark](https://github.com/thutt/build-tool-comparator) |

## Verdict

A third-party synthetic benchmark (thutt/build-tool-comparator: rules that only touch 0-byte files, -j4, 4-CPU x86_64 and Raspberry Pi Arm boxes, CPU model unstated, one run per cell) found Bazel about 11x faster on incremental and 34x faster on null builds than recursive GNU Make 4.3 with its default built-in rules at 100,000 modules on x86_64. The win disappears once Make's built-in rules are turned off: in every incremental and null row of the same tables, Make with -rR and Ninja 1.11.1 are 1.8x to over 100x faster than Bazel (derived from page data), and Bazel's full builds are the slowest of all tools.

## Use it when

- Large monorepos (thousands to 100,000+ targets) where developers repeat incremental and no-op builds against a warm server.
- Multi-language builds (C++, Java, Go, Android, iOS) that should share one dependency graph and one cache.
- Teams that can deploy a shared remote cache or remote execution, the speed levers the measured benchmark does not exercise.
- Projects that need sandboxed actions and cache keys stable enough to share outputs between CI and laptops.

## Skip it when

- Small and medium projects: in the third-party runs, a cold full build of 50 to 100 trivial modules took about 10 to 22 s against well under a second for Make and Ninja.
- When you only need a faster Make: the same benchmark shows Ninja, and Make with --no-builtin-rules --no-builtin-variables, beating Bazel in every row (100,000 modules on x86_64: incremental 10.4 s and 9.5 s against 61.9 s; null 7.1 s and 7.8 s against 20.2 s).
- Memory- or disk-constrained machines: measured memory ran from 242 MB to 4 GB across the x86_64 runs and \~/.cache/bazel reached 26 GB at 100,000 modules; Bazel's docs describe OutOfMemoryError on big builds and memory-saving flags that slow incremental builds (open issue #24527 reports OOM with a 9 GB heap).
- Build steps whose outputs must not be cached (network fetches, deployments) or builds made of a few long sequential steps, per Bazel's own FAQ.
- Codebases that must coexist with other build tools: every target needs a BUILD file, and outputs live under the user cache behind bazel-\* symlinks.

## How it is fast

The persistent server keeps an in-memory analysis cache (Skyframe dependency graph and loaded packages), so a repeat build skips re-reading BUILD files and re-deriving the graph. Actions are keyed by content hashes in an action cache plus a content-addressable store, which can be local or a shared remote cache, and actions can be sent to remote execution. Complete declared dependencies let it rebuild only affected targets and run independent actions in parallel.

## Compared with alternatives

Pick Bazel over Ninja, tup or xmake when you need hermetic multi-language builds with a shared remote cache or remote execution rather than low local overhead, where Ninja measured faster in every row; Buck2 is the closest peer (same BUILD-file model), and ccache is complementary rather than an alternative.

## Integration

| | |
|---|---|
| **Form** | standalone build tool (C++ client plus Java server shipped as one binary), not a library |
| **Dependencies** | none for release binaries; install docs recommend the Bazelisk launcher; rule sets for each language come as external modules |
| **Minimum toolchain** | Release binaries; maintained lines 7.7.x, 8.8.x and 9.3.x (9.3.1 latest on 2026-10-21, 10.0.0rc2 in pre-release); porting to a new Unix needs a JDK there |
| **Platforms** | Linux, macOS and Windows official; community packages for FreeBSD, Alpine, Raspberry Pi and ppc64el |
| **Thread safety** | One server per output base runs one command at a time; concurrent invocations block or fail fast (--block_for_lock) |
| **Drop-in for the baseline** | no |

## Gotchas

- The idle server stays up for 3 hours by default (--max_idle_secs) and each workspace gets its own server, so scripted builds across many directories accumulate JVMs unless shut down.
- Many command-line flag changes discard the in-memory analysis cache, and startup-option changes restart the server, turning the next build cold.
- linux-sandbox does not nest inside Docker without extra privileges; Bazel then automatically falls back to processwrapper-sandbox (or local) unless the strategy is requested by name.
- Benchmark harness caveats: one timed run per cell, the x86_64 Bazel binary reports 'no_version' (an unstamped build), its disk column excludes the install base that the Arm column includes (6 MB vs 310 MB at 50 modules), and generate.sh deletes the previous \~/.cache/bazel with a background rm -rf that overlaps the next tool's timed full build while the harness never runs bazel shutdown.

## Known shortcomings

- thutt/build-tool-comparator (5 stars, author critical of Bazel): Bazel beats Make only when Make runs with its default built-in rules, on incremental and null builds at large sizes; it loses to Ninja in every row and to Make with --no-builtin-rules, and its full build is the slowest everywhere. CPU model not stated.
- Enricher retier B to C: the only wins are over Make with default built-in rules (crippled-by-default baseline); one run per cell, unstamped x86 binary, inconsistent disk column, background cache deletion overlapping the next timed full build.

## Caveats and trade-offs

The benchmark is synthetic and measures pure build-tool overhead: no compiler runs, so it says nothing about real C or C++ compile and link wall-clock time or about remote caching and execution, which are Bazel's main speed levers. Bazel only wins against Make run with default built-in rules (the benchmark's own results show Make drops to Ninja-like times with --no-builtin-rules) and only on incremental builds from about 5,000 modules and null builds from about 1,000 modules (on Arm at 1,000 modules Make is still faster); at small sizes (50 to 100 modules) Bazel's full build is about 10 to 22 s vs 0.04 to 0.23 s for Ninja and Make, and Ninja beats Bazel in every row. The measurement is by a single maintainer repo with 5 stars (GPL-3.0 benchmark code, last commit 2025-02-28); CPU model is not stated, so it cannot be tier A. The Bazel version is not recorded on the x86_64 runs. The Bazel repo itself carries no Make or Ninja comparison; the Bazel 'fast' claim is first-party and unquantified. [retier] Enricher: one run per cell; the x86 Bazel binary is unstamped (no_version); the disk column is inconsistent (x86 excludes the install base, Arm includes it: 6M vs 310M at 50 modules, 26G vs 341M at 100k); generate.sh deletes the old \~/.cache/bazel with a background rm -rf that overlaps the next tool's timed full build; bazel shutdown is never run between tools.

JVM server process: 350 to 500 MB resident in these runs and 310 MB to 1 GB of output-base disk even for empty modules; slow cold full build; steep learning curve (BUILD/Starlark files, many options); hermetic sandboxed actions with remote cache and remote execution, whose benefits this benchmark does not exercise. Output lands in the user cache directory, not the source tree.

## Maintenance

Very actively maintained by Google (several release lines patched in October 2026, 26.0k stars) and Apache-2.0, but adopting it means rewriting the build in BUILD files and running a JVM server.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification B, tier now C.
- **Tier reason:** Independent third-party measurement (thutt/build-tool-comparator README results, harness in scripts/runner.sh and scripts/build-\*.sh, GPL-3.0) of Bazel against GNU Make 4.3 and Ninja 1.11.1 with tool versions, parallelism, RAM and kernel stated; CPU model is not stated, so not A. Every quoted figure matches the README tables.
- **Retiered** B to C: B to C: Bazel's only wins are over GNU Make 4.3 run with its default built-in rules, a baseline crippled by a build default (AssemblyScript precedent); Make with -rR and Ninja beat Bazel by 1.8x to over 100x in every incremental and null row (derived from page data). The harness also has one run per cell, an unstamped x86 Bazel binary and a background cache deletion that overlaps the next tool's timed full build.
- **Verifier notes:** All claimed figures verified in the README tables (x86_64 100,000 modules: incr 61.911 vs 692.201/292.019 s, NULL 20.193 vs 688.101/285.583 s; 5,000 modules: incr 4.040 vs 22.408/24.813 s; Ninja and no-builtin-rules Make rows also match). Weak entry: the benchmark repo has 5 stars and its author is openly Bazel-sceptical; Bazel wins only against default-rules Make on incremental/null builds at scale, loses to Ninja in every row and to Make -rR, and its full builds are slowest everywhere. Orchestrator may weigh whether default-rules Make counts as a crippled baseline; it is the out-of-the-box Make configuration and the benchmark applies out-of-the-box settings to every tool.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-09 (wave 2 book seed pass, 2026-10-24); enrichment (wave 2 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/thutt/build-tool-comparator>
  - <https://raw.githubusercontent.com/thutt/build-tool-comparator/HEAD/README.md>
  - <https://raw.githubusercontent.com/thutt/build-tool-comparator/HEAD/LICENSE>
  - <https://github.com/thutt/build-tool-comparator/commits>
  - <https://github.com/bazelbuild/bazel>
  - <https://github.com/bazelbuild/bazel/commits>
  - <https://raw.githubusercontent.com/bazelbuild/bazel/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/bazelbuild/bazel>
  - <https://raw.githubusercontent.com/bazelbuild/bazel/HEAD/README.md>
  - <https://github.com/bazelbuild/bazel/releases>
  - <https://github.com/bazelbuild/bazel/tree/master/docs>
  - <https://github.com/bazelbuild/bazel/issues?q=is%3Aissue%20state%3Aopen%20label%3Ateam-Performance>
  - <https://raw.githubusercontent.com/bazelbuild/bazel/HEAD/docs/about/faq.mdx>
  - <https://raw.githubusercontent.com/bazelbuild/bazel/HEAD/docs/install/index.mdx>
  - <https://raw.githubusercontent.com/bazelbuild/bazel/HEAD/docs/run/client-server.mdx>
  - <https://raw.githubusercontent.com/bazelbuild/bazel/HEAD/docs/advanced/performance/memory.mdx>
  - <https://raw.githubusercontent.com/bazelbuild/bazel/HEAD/docs/advanced/performance/iteration-speed.mdx>
  - <https://raw.githubusercontent.com/bazelbuild/bazel/HEAD/docs/remote/caching.mdx>
  - <https://raw.githubusercontent.com/bazelbuild/bazel/HEAD/docs/docs/sandboxing.mdx>
  - <https://raw.githubusercontent.com/thutt/build-tool-comparator/HEAD/README.md>
  - <https://raw.githubusercontent.com/thutt/build-tool-comparator/HEAD/scripts/runner.sh>
  - <https://raw.githubusercontent.com/thutt/build-tool-comparator/HEAD/scripts/run_build.py>
  - <https://raw.githubusercontent.com/thutt/build-tool-comparator/HEAD/scripts/build-bazel.sh>
  - <https://raw.githubusercontent.com/thutt/build-tool-comparator/HEAD/scripts/build-ninja.sh>
  - <https://raw.githubusercontent.com/thutt/build-tool-comparator/HEAD/scripts/generate.sh>
  - <https://raw.githubusercontent.com/thutt/build-tool-comparator/HEAD/scripts/modify-most-used-interface.sh>
  - <https://raw.githubusercontent.com/thutt/build-tool-comparator/HEAD/generator/generate.py>
  - <https://raw.githubusercontent.com/thutt/build-tool-comparator/HEAD/generator/bazel.py>
  - <https://raw.githubusercontent.com/thutt/build-tool-comparator/HEAD/generator/rmakefile.py>
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/bazelbuild/bazel`) · [data/wave2/enrich/raw/github_com_bazelbuild_bazel.json](../../../data/wave2/enrich/raw/github_com_bazelbuild_bazel.json) (enrichment confidence 0.7)

</details>
