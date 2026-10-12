# sjsonnet

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Scala` · `Apache-2.0` · 🟢 active

> Databricks' Scala Jsonnet interpreter (JVM, Scala Native, GraalVM, Scala.js); about 5-9x faster than go-jsonnet on real-world configs.

| | |
|---|---|
| **Beats** | go-jsonnet and google/jsonnet (C++) v0.22.0-rc1 in jrsonnet's docs/benchmarks.adoc; sjsonnet 0.6.2 measured (current 0.7.5) |
| **Claimed result** | Independent jrsonnet docs/benchmarks.adoc (Ryzen 9 9950X3D, public nix harness, hyperfine, sjsonnet 0.6.2 Scala Native binary): real-world GraalVM CI 69.6 ms vs go-jsonnet 600.3 ms (about 8.6x) and kube-prometheus 204.6 ms vs 1068.4 ms (about 5.2x), derived from page data; google/jsonnet C++ was not timed on these ('takes longer than an hour'). The rows where sjsonnet trails go-jsonnet (Tail call, Inheritance function recursion, String strips, Big object, manifestJsonEx, manifestTomlEx, parseInt, substr) are in microseconds, about 2.4 ms vs 1.4 ms per process, so they measure startup rather than evaluation. jrsonnet (Rust) is faster on most cases. |
| **Workload** | Evaluating one large production Jsonnet config (staging/runbot-app.jsonnet in the Databricks codebase, about 6.6 MB of output). |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 9 9950X3D 16-core (jrsonnet docs/benchmarks.adoc); README 2023 numbers state no hardware |
| **Compiler and flags** | Sjsonnet 0.6.2 prebuilt release binaries (Scala Native and GraalVM native-image) wrapped with --max-stack 200000; google/jsonnet built with its own Makefile defaults and go-jsonnet with nixpkgs buildGoModule (nix/cpp-jsonnet.nix, nix/go-jsonnet.nix); compiler versions not stated |
| **Adoption** | 318 stars; used in Databricks |
| **Last commit** | 2026-09-28 |
| **Links** | [repository](https://github.com/databricks/sjsonnet) · [benchmark](https://github.com/CertainLach/jrsonnet/blob/master/docs/benchmarks.adoc) |

## Verdict

jrsonnet's docs/benchmarks.adoc (hyperfine with 4 warm-ups and at least 20 runs per command, AMD Ryzen 9 9950X3D, nix-built go-jsonnet and C++ jsonnet v0.22.0-rc1 at default flags) ran Sjsonnet 0.6.2's Scala Native and GraalVM release binaries one process per run: GraalVM CI 69.6 ms vs go-jsonnet 600.3 ms (8.6x) and kube-prometheus 204.6 ms vs 1068.4 ms (5.2x), with C++ jsonnet too slow to run on real-world inputs. On the C++ perf_tests and benchmarks, Sjsonnet native beat C++ jsonnet on every case C++ completed (for example Simple recursive call 18.0 vs 78.8 ms, Inheritance recursion 46.7 vs 1216.9 ms; ratios derived from page data).

## Use it when

- CI or build pipelines that render large Jsonnet trees (kube-prometheus, GraalVM CI style) where go-jsonnet takes 0.6-1.1 s per entry point and C++ jsonnet takes hours: Sjsonnet's native binaries ran them in 65-205 ms in jrsonnet's runs.
- JVM services that evaluate Jsonnet repeatedly: embed the Interpreter with a shared DefaultParseCache so JIT warm-up and parsing are paid once (the README's 0.10 s vs 6.5 s go-jsonnet figure is this warm-daemon mode).
- One-shot command-line use where a JVM is unwanted: use the GraalVM or Scala Native release binary (GraalVM CI 65.1 / 69.6 ms) rather than the JAR, which adds about 1 s of JVM start-up.
- Recursion- and inheritance-heavy configs: Inheritance recursion 46.7 ms vs go-jsonnet 444.7 ms and C++ 1216.9 ms, Realistic 1 12.7 ms vs go-jsonnet 3158.3 ms, and here it also beats jrsonnet (160.1 ms on Inheritance recursion).
- Browser or Node tooling that needs a Jsonnet evaluator: the Scala.js build with interpretAsync loads imports through fetch.

## Skip it when

- When the fastest available evaluator is the goal: jrsonnet (Rust) is 2.0x faster on GraalVM CI and 4.7x on kube-prometheus in its own table and faster on most micro cases; Sjsonnet's own 2026-05-13 gap report still has kube-prometheus 1.68x behind jrsonnet.
- Many tiny evaluations each in a fresh process: the Scala Native binary has a start-up floor of about 2.4 ms (go-jsonnet about 1.4 ms, jrsonnet about 0.75 ms on the same trivial inputs), and the plain JAR about 1 s.
- std.foldl-driven string concatenation in the 0.6.x releases: Foldl string concat 328.6 ms and std.foldl 80.0 ms vs jrsonnet 3.7 ms and 2.2 ms (later releases added an object-merge fast path for foldl, not measured independently).
- Windows hosts wanting a native binary (none published, open issue #391) or JVMs older than Java 17 (required since 0.7.0).
- Byte-for-byte parity with Jsonnet 0.22 std edge cases on older releases: divergences in std.reverse, splitLimit, clamp, setUnion, slice, makeArray, substr, base64 and manifestIni/manifestToml were filed in April-May 2026 and closed by June 2026, and pre-0.5.5 releases had broken assertion logic (issue #526).

## How it is fast

Parsing uses Fastparse; a single StaticOptimizer pass then resolves variables to symbol-table indices and rewrites the AST, and the optimised tree is kept in a reusable parse cache. Lazy values are memoised thunks (Lazy caches its result on first use, which the README contrasts with google/jsonnet), and the whole std library is written as Scala intrinsics instead of the Jsonnet-coded std that C++ jsonnet interprets, which is where the C++ reference loses 20-1000x on std-heavy cases. The Eval hierarchy is kept to two implementors so the JVM JIT can inline Eval.value bimorphically; the native build uses Scala Native release-full mode with full LTO, and the GraalVM binary is an ahead-of-time native image.

## Compared with alternatives

The catalogued siblings (LuaJIT, PyPy, Codon and the other interpreters) speed up general-purpose languages, and no other Jsonnet evaluator is catalogued yet, so pick Sjsonnet whenever the workload is Jsonnet and the baseline is go-jsonnet or C++ jsonnet. Prefer it over jrsonnet (a seed lead, faster on most cases) mainly when you need in-process JVM or Scala.js embedding or the inheritance-heavy patterns where Sjsonnet wins.

## Integration

| | |
|---|---|
| **Form** | Maven library (Scala 2.12/2.13/3), standalone JAR, Scala Native and GraalVM native-image CLI binaries, Scala.js CommonJS module |
| **Dependencies** | fastparse 3.1.1, ujson 4.4.3, pprint, scalatags, scala-collection-compat; the JVM CLI adds os-lib, mainargs, xz, lz4-java, snakeyaml and re2j; the Native build adds scala-native-crypto and scala-yaml |
| **Minimum toolchain** | Java 17+ to run (since 0.7.0); builds with Mill for Scala 2.12.21, 2.13.18 and 3.3.8, Scala Native 0.5.12, Scala.js 1.20.2, GraalVM CE 25 for the native image |
| **Platforms** | any JVM; native release binaries for linux-x86_64, linux-arm64 and darwin-arm64 (as named in jrsonnet's nix/sjsonnet.nix); no Windows binary; browsers and Node via Scala.js |
| **Thread safety** | An individual Interpreter is single-threaded; independent interpreters may run concurrently in one JVM after issue #1047 (shared renderer scratch buffers, the std singleton's field caches and parse-cache values were unsafe) was closed via PR #1052 in 2026; older releases should not share a parse cache across threads. |
| **Drop-in for the baseline** | partial: the CLI takes the jsonnet/go-jsonnet flags and is meant to produce the same output, but it is a separate JVM/Scala implementation with its own std, not a libjsonnet ABI replacement, and std edge cases have diverged in the past |

## Gotchas

- Unit error in the catalogued claim: in jrsonnet's docs/benchmarks.adoc the Tail call, Inheritance function recursion, String strips, Big object, std.manifestJsonEx, std.manifestTomlEx, std.parseInt and std.substr tables are in microseconds, not milliseconds (Tail call is 2.4 ms vs C++ 18.5 ms; Big object 3.8 ms vs 16.2 ms). Ratios are unaffected, but every case where Sjsonnet trails go-jsonnet (about 2.4-2.6 ms vs 1.4 ms) is one of these near-empty runs, so those losses measure process start-up rather than evaluation speed.
- The README's 65x/670x numbers compare a warm long-lived JVM daemon with cold go-jsonnet and C++ subprocesses on an internal Databricks file; the public MainBenchmark (JMH, 4 forks, 30 warm-up and 40 measured iterations) now points at test_suite/stdlib.jsonnet, so that figure cannot be reproduced from the repository.
- jrsonnet's harness (hyperfine -N -w4 -m20, all binaries wrapped with --max-stack 200000 under ulimit -s 65535) does not compare outputs between implementations; it timed Sjsonnet 0.6.2 (current release 0.7.5, whose 0.7.0 notes claim 40% faster) against go-jsonnet and C++ jsonnet v0.22.0-rc1 builds, not the 0.20.0 versions named in the record's baseline field, and skipped the Mimir case because Sjsonnet failed it ('Field does not exist', issue #829, fixed by PR #832).
- Default --max-stack is 500 frames; deeply recursive programs need -Xss (JVM) or SCALANATIVE_THREAD_STACK_SIZE plus a larger --max-stack. The repo's RegressionBenchmark only prints golden-output mismatches to stderr instead of failing.

## Known shortcomings

- Raised C to B on the independent jrsonnet docs/benchmarks.adoc (Ryzen 9 9950X3D, public nix harness): 5-9x faster than go-jsonnet on real-world configs, with google/jsonnet (C++) too slow to time there. The README's 670x is an internal file measured warm-daemon against cold-subprocess; sjsonnet is slower than go-jsonnet on 5 builtin micros and jrsonnet (Rust) is faster on most cases. Scala/JVM, not C++.
- Enricher: jrsonnet's benchmarks.adoc gives Tail call, Inheritance function recursion, String strips, Big object, manifestJsonEx, manifestTomlEx, parseInt and substr in microseconds, not milliseconds (ratios unchanged); every row where sjsonnet trails go-jsonnet is about 2.4 ms vs 1.4 ms, so those losses are process startup rather than evaluation. The baselines are go-jsonnet and C++ jsonnet v0.22.0-rc1 (not 0.20.0), the measured sjsonnet was 0.6.2 (current 0.7.5), the hyperfine harness never compares outputs, and the README's 65x/670x cannot be reproduced (MainBenchmark now points at stdlib.jsonnet).

## Caveats and trade-offs

The README's 65x/670x figures are first-party (May 2023, Sjsonnet 0.4.3) on an internal Databricks config that cannot be reproduced, and compare a warm JVM daemon with cold subprocesses for go-jsonnet and google/jsonnet, so they overstate the like-for-like gap. The independent jrsonnet runs (per-process CLI for all) give smaller margins: about 5-9x over go-jsonnet on real-world configs, and the C++ reference was too slow to time on real-world inputs. Sjsonnet is not uniformly faster than go-jsonnet: it is slower on Big object (3756.8 vs 2544.5 ms), Inheritance function recursion (2394.1 vs 1414.3 ms), std.manifestJsonEx (2443.6 vs 1426.9 ms), std.manifestTomlEx (2558.8 vs 1427.7 ms) and std.parseInt (2383.6 vs 1398.2 ms). The Rust implementation jrsonnet beats Sjsonnet on most cases (GraalVM CI 2.0x, kube-prometheus 4.7x per jrsonnet's table; Sjsonnet's own docs/perf-gap-vs-jrsonnet.md, 2026-05-13 on an Apple M3 Pro, still shows kube-prometheus 1.68x behind jrsonnet). The benchmark is run by a competitor; compiler versions for the C++/Go builds are unstated, and the mimir real-world case skipped Sjsonnet (databricks/sjsonnet issue #829). JVM startup adds about 1 s per invocation for the plain JAR (client-server mode cuts it to 0.2-0.3 s per the README). [retier] The README's 65x/670x figures are first-party (May 2023, sjsonnet 0.4.3) on an internal Databricks config that cannot be reproduced (MainBenchmark now points at stdlib.jsonnet) and compare a warm JVM daemon with cold subprocesses. The jrsonnet harness never compares outputs. Scala, run as a Scala Native binary; not C++.

JVM implementation of the Jsonnet language (Scala); best when kept as a warm long-lived process; startup cost of a cold JVM applies for one-shot use.

## Maintenance

Actively maintained by Databricks (commits to 2026-09-28, release 0.7.5 on 2026-09-23, steady perf and correctness PRs), Apache-2.0, published on Maven Central and as release binaries, so it is directly usable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C: jrsonnet's docs/benchmarks.adoc is an independent measurement (by a competing implementation's author) of Sjsonnet 0.6.2 native/GraalVM release binaries against google/jsonnet (C++) and go-jsonnet v0.22.0-rc1, with public harness code (nix/benchmarks.nix, hyperfine -N -w4 -m20, inputs from jrsonnet tests/realworld and google/jsonnet perf_tests/benchmarks) and the CPU stated (AMD Ryzen 9 9950X3D). Not A because compiler versions and flags for the C++/Go builds are not stated (nix stdenv defaults) and sjsonnet is a prebuilt binary.
- **Verifier notes:** README numbers match exactly; tier raised to B on jrsonnet's independent public-harness benchmark, which also shows jrsonnet (Rust, not in the catalog yet, a possible lead) is faster than Sjsonnet on most workloads. Category: language-interpreters fits (Jsonnet evaluator compared with other evaluators); if a data-format category is preferred, the nearest earlier-wave one is json. Metadata confirmed on github.com: Apache-2.0, 318 stars, not archived or a fork, last commit 2026-09-28.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `hardware`, `compiler_and_flags`, `caveats`, `baseline`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/databricks/sjsonnet/HEAD/readme.md>
  - <https://github.com/databricks/sjsonnet>
  - <https://github.com/databricks/sjsonnet/commits>
  - <https://github.com/databricks/sjsonnet/tree/master/bench>
  - <https://github.com/databricks/sjsonnet/tree/master/bench/resources>
  - <https://github.com/databricks/sjsonnet/tree/master/docs>
  - <https://raw.githubusercontent.com/databricks/sjsonnet/HEAD/docs/perf-gap-vs-jrsonnet.md>
  - <https://raw.githubusercontent.com/databricks/sjsonnet/HEAD/bench/resources/README.md>
  - <https://github.com/CertainLach/jrsonnet/blob/master/docs/benchmarks.adoc>
  - <https://raw.githubusercontent.com/CertainLach/jrsonnet/HEAD/docs/benchmarks.adoc>
  - <https://github.com/CertainLach/jrsonnet/tree/master/nix>
  - <https://raw.githubusercontent.com/CertainLach/jrsonnet/HEAD/nix/benchmarks.nix>
  - <https://raw.githubusercontent.com/CertainLach/jrsonnet/HEAD/nix/sjsonnet.nix>
  - <https://raw.githubusercontent.com/CertainLach/jrsonnet/HEAD/nix/cpp-jsonnet.nix>
  - <https://raw.githubusercontent.com/CertainLach/jrsonnet/HEAD/nix/go-jsonnet.nix>
- **Sources the enricher read:**
  - <https://github.com/databricks/sjsonnet>
  - <https://raw.githubusercontent.com/databricks/sjsonnet/HEAD/readme.md>
  - <https://raw.githubusercontent.com/databricks/sjsonnet/HEAD/docs/perf-gap-vs-jrsonnet.md>
  - <https://raw.githubusercontent.com/databricks/sjsonnet/HEAD/bench/resources/README.md>
  - <https://raw.githubusercontent.com/databricks/sjsonnet/HEAD/build.mill>
  - <https://raw.githubusercontent.com/databricks/sjsonnet/HEAD/bench/src/sjsonnet/bench/MainBenchmark.scala>
  - <https://raw.githubusercontent.com/databricks/sjsonnet/HEAD/bench/src/sjsonnet/bench/RegressionBenchmark.scala>
  - <https://github.com/databricks/sjsonnet/tree/master/bench/src/sjsonnet>
  - <https://github.com/databricks/sjsonnet/tree/master/bench/src/sjsonnet/bench>
  - <https://github.com/databricks/sjsonnet/releases>
  - <https://github.com/databricks/sjsonnet/commits>
  - <https://github.com/databricks/sjsonnet/issues?q=is%3Aissue+is%3Aopen>
  - <https://github.com/databricks/sjsonnet/issues?q=is%3Aissue+is%3Aclosed>
  - <https://github.com/databricks/sjsonnet/issues?q=is%3Aissue+label%3Abug>
  - <https://github.com/databricks/sjsonnet/issues/829>
  - <https://github.com/databricks/sjsonnet/issues/51>
  - <https://github.com/databricks/sjsonnet/issues/1047>
  - <https://raw.githubusercontent.com/CertainLach/jrsonnet/HEAD/docs/benchmarks.adoc>
  - <https://raw.githubusercontent.com/CertainLach/jrsonnet/HEAD/nix/benchmarks.nix>
  - <https://raw.githubusercontent.com/CertainLach/jrsonnet/HEAD/nix/sjsonnet.nix>
  - <https://raw.githubusercontent.com/CertainLach/jrsonnet/HEAD/nix/cpp-jsonnet.nix>
  - <https://raw.githubusercontent.com/CertainLach/jrsonnet/HEAD/nix/go-jsonnet.nix>
  - <https://raw.githubusercontent.com/CertainLach/jrsonnet/HEAD/README.adoc>
  - <https://github.com/eduardosm/rsjsonnet>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/databricks/sjsonnet`) · [data/wave12/enrich/raw/github_com_databricks_sjsonnet.json](../../../data/wave12/enrich/raw/github_com_databricks_sjsonnet.json) (enrichment confidence 0.8)

</details>
