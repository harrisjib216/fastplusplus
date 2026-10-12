# jsoniter-scala

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Scala` · `MIT` · 🟢 active

> Scala macro-generated JSON codecs; decoding straight into case classes edged out RapidJSON's DOM (0.147 vs 0.154 s) in kostya/benchmarks.

| | |
|---|---|
| **Beats** | RapidJSON |
| **Claimed result** | 0.147s (Scala/jsoniter-scala) vs RapidJSON 0.154s (g++) and 0.194s (clang++) (\~1.05x-1.32x faster, derived from page data) |
| **Workload** | Parse /tmp/1.json and average the x/y/z coordinates. json/generate_json.rb generates the file as a pretty-printed object: 'coordinates' holds 524,288 records, each with x/y/z doubles, a 'name' string and a nested 'opts' object. The timed window, bracketed by notify start/stop, excludes process/JVM startup, file loading and a two-tiny-document self-test. It runs on the same machine and Docker image as the C++ entries. |
| **Metric** | throughput |
| **Hardware** | Intel(R) Xeon(R) E-2324G, Debian GNU/Linux (Docker image) |
| **Compiler and flags** | Scala 3.8.4: plain `scalac` (no extra options) compiles json/json-scala/src/main/scala/JsonTest.scala against jsoniter-scala-macros_3 2.39.1 (json/json-scala/Maven.list, fetched with coursier). The classes go into a fat jar built by common/jvm/combinejars.sh (not sbt-assembly), which runs as `scala application.jar` under xtime.rb. RapidJSON (a clone of miloyip/rapidjson) builds with g++ 16.1.0 as `g++ $(COMMON_FLAGS) -std=c++23` and with clang++ 22.1.8 as `clang++ $(COMMON_FLAGS) -std=c++23 -stdlib=libc++`. COMMON_FLAGS = -Wall -Wextra -pedantic -Wcast-align -O3 -march=native -flto=auto -Wa,-mbranches-within-32B-boundaries (common/commands.mk). README results are dated UPDATE: 2026-07-19. |
| **Adoption** | 819 stars |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/plokhotnyuk/jsoniter-scala) · [benchmark](https://github.com/kostya/benchmarks#json) |

## Verdict

In kostya/benchmarks' Json test (README update 2026-07-19, Xeon E-2324G, Debian Docker image), jsoniter-scala 2.39.1 was compiled with plain scalac 3.8.4 and run via the `scala` launcher (the README lists Java 24.0.2). It parsed the 524,288-record file and averaged x/y/z in 0.147 s. RapidJSON's DOM took 0.154 s with g++ 16.1.0 and 0.194 s with clang++ 22.1.8/libc++, both built with -O3 -march=native -flto: about 1.05x and 1.32x. The comparison is not like-for-like. jsoniter-scala decodes only x/y/z into case classes and skips the rest, while RapidJSON builds a full DOM with its default, less precise number parsing (RapidJSON Precise took 0.212/0.262 s). The JVM was warmed only by two tiny self-test documents.

## Use it when

- Scala services on the JVM that decode and encode known schemas (case classes, sealed-trait ADTs, Option, collections) from byte arrays or streams, for example HTTP bodies via its tapir, sttp, http4s, pekko-http or zio-http integrations.
- Large documents where you only need some fields. Unmapped fields are skipped without being materialized: in the benchmark the RSS increase was 25.62 MiB vs RapidJSON DOM's 123.44 MiB for 524,288 records.
- Multi-GB top-level JSON arrays or NDJSON-like value streams, processed one element at a time with scanJsonArrayFromStream or scanJsonValuesFromStream without holding the whole input in memory.
- Untrusted input where you want safe defaults: fail-fast validation, stack-less exceptions, BigDecimal/BigInt capped at 308 digits, map/set insert caps, recursive types disabled, and only a fixed set of classes instantiated.
- Number-heavy payloads that need correctly rounded double parsing and shortest round-trip double output, or as a faster parse/serialize backend for existing circe or play-json code through the booster modules.

## Skip it when

- C or C++ code, which is where RapidJSON lives. On the same benchmark page, simdjson On-Demand (0.060 s), gason (0.127 s), yyjson (0.131 s) and Mir asdf (0.133 s) all beat it, and it uses more memory and energy than RapidJSON g++.
- Schema-less or dynamic JSON that you need to query as a tree. The library has no AST of its own, so you need circe, dijon or play-json on top.
- Short-lived CLI or cold-start serverless processes. Base RSS was 283.94 MiB vs 113.21 MiB for RapidJSON, energy was 7.89 J vs 6.61 J, and neither JVM startup nor full JIT warm-up is part of the measured result.
- Payloads dominated by long ASCII strings, or where most of the input is skipped. The author reports that simdjson-java (JDK Vector API) beats it on long strings and on skipping (issue #650). It uses SWAR, not explicit SIMD.
- Recursive or cyclic object graphs (only acyclic graphs; recursive types need an opt-in flag), and Scala 3 union types or complex opaque types, which need hand-written custom codecs.

## How it is fast

Black-box macros emit a specialized parser per type that reads UTF-8 bytes straight into constructor arguments, with no reflection, intermediate AST or hash maps. Keys go into a reused char buffer and are matched by sequential compares (up to 8 fields and 64 name chars) or by a @switch on a precomputed hash, and unknown fields are skipped by bracket/quote counting. Hot paths use SWAR word tricks through VarHandle byte-array views: 4-byte string scanning from borer, and 8-byte digit, java.time and UUID parsing from FastDoubleParser and simdjson ideas. Doubles take an exact pow10 fast path, then rust-lexical's 'moderate path' (multiplyHigh by precomputed power-of-10 mantissas), with Double.parseDouble only for near-halfway cases; output uses Schubfach/XJB shortest-double and James Anhalt integer printing, with parsers and writers pooled per thread in a ThreadLocal.

## Compared with alternatives

It is the only JVM/Scala entry in this category, so choose it whenever the code is Scala: nothing else here runs there. In C/C++, glaze is the closest analogue (compile-time typed struct mapping), and simdjson, yyjson or gason are faster than jsoniter-scala on the same kostya page.

## Integration

| | |
|---|---|
| **Form** | module (Maven Central jars: jsoniter-scala-core at runtime; jsoniter-scala-macros as a compile-internal/provided dependency) |
| **Dependencies** | Runtime: scala-library only on the JVM, plus scala-java-time on Scala.js and Scala Native. Macros are compile-time only. Optional: jsoniter-scala-circe (needs circe-core). |
| **Minimum toolchain** | Scala 2.12, 2.13 or 3.3 LTS+; JDK 11+ (v2.13.5.2 was the last release for JDK 8); Scala.js 1.0+; Scala Native 0.5+ |
| **Platforms** | Any JVM on JDK 11+ (architecture-independent bytecode), GraalVM native-image, Scala.js (browsers/Node; WASM builds are benchmarked), Scala Native 0.5+ |
| **Thread safety** | The top-level read\*/write\* functions draw a JsonReader/JsonWriter from a per-thread ThreadLocal pool, so calls from different threads do not share parser state. They are non-reentrant within one thread, so nested calls must use the \*Reentrant variants. Thread safety of the codec objects themselves is not documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- Nesting read/write calls on the same thread corrupts state because of the pooled reader/writer. For example, calling readFromString inside a scanJsonValuesFromStream callback breaks (README known issue 5, #923). Use the \*Reentrant functions for all but the innermost call.
- Unknown fields are skipped leniently by default. skip() only balances brackets and quotes and scans number-ish characters, so malformed JSON inside ignored fields can be accepted. Set skipUnexpectedFields=false to reject unknown fields instead of skipping them.
- The safe defaults reject some valid data. A Map or Set with more than 1024 entries fails with 'too many map inserts'/'too many set inserts', and BigDecimal/BigInt values with 308+ digits fail, until you raise them via CodecMakerConfig. Duplicate keys throw, serializing null throws NPE, and total input length is not limited, so check it yourself (known issue 1).
- The make() config is evaluated at compile time. It cannot depend on code in the same compilation module, and having two jsoniter-scala versions on the classpath gives 'Cannot evaluate a parameter of the make macro' errors. ADTs nested inside classes or functions can crash the compiler (#551), and escaped characters are not accepted inside numeric or java.time string values.

## Known shortcomings

- Skipped fields are not validated (skip() only balances brackets and quotes), so the kostya comparison against RapidJSON's full validated DOM is not like-for-like. Default limits reject maps/sets over 1024 entries and 308+ digit BigDecimal/BigInt (configurable); no input-length limit. Nested read/write on one thread needs the \*Reentrant functions. SWAR, not SIMD; simdjson-java beats it on long ASCII strings and skipping.

## Caveats and trade-offs

The win over RapidJSON(g++) is small: 0.147 vs 0.154 s, \~1.05x. The comparison is not like-for-like in two ways. jsoniter-scala uses a compile-time typed case-class codec that decodes only x/y/z and skips name/opts, while RapidJSON builds a full DOM. The RapidJSON rows also use its default, less precise number parsing. Against RapidJSON Precise (0.212 s g++, 0.262 s clang++), jsoniter-scala leads by \~1.44x/1.78x (derived from page data). The Scala row uses more energy than g++ RapidJSON (7.89 J vs 6.61 J) and more memory (283.94+25.62 MiB vs 113.21+123.44 MiB). JIT warm-up is only the two tiny self-test calls, so this is a single-shot run, not steady-state throughput. Several C/C++ parsers are faster on the same page: simdjson On-Demand at 0.060 s, DAW JSON Link, gason and yyjson. The suite pins jsoniter-scala 2.39.1, while the current release is v2.41.1 (2026-09-25). The workload is a single synthetic one.

JVM-only, needs code-generated codecs per-type at compile time (macro-based), not a drop-in DOM parser like RapidJSON; JVM warmup/startup cost not captured by this steady-state benchmark.

## Maintenance

Actively maintained: v2.41.1 was released 2026-09-25, while the benchmark pinned 2.39.1. It is MIT-licensed, depended on by tapir, sttp, caliban and smithy4s, and patch versions are binary-compatible both ways (minor versions backward only, checked with MiMa).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** kostya/benchmarks is an independent third-party suite (2.9k stars). Its Json table has Scala (jsoniter-scala) at 0.147±0.001 s, C++/g++ (RapidJSON) at 0.154±0.001 s and C++/clang++ (RapidJSON) at 0.194±0.001 s. The code is public (json/json-scala/src/main/scala/JsonTest.scala, json/test_rapid.cpp, json/Makefile), the flags are in common/commands.mk, and the README's Environment section gives the compiler versions (Scala 3.8.4, gcc 16.1.0, clang 22.1.8) and the CPU (Xeon E-2324G). Everything tier A needs is present.
- **Verifier notes:** The three times match the page exactly and the derived \~1.05x-1.32x is correct. Metadata is correct: MIT, 819 stars, not a fork or archived, last commit 2026-09-25, active. I corrected the build description, because the suite uses scalac, coursier and combinejars.sh, not sbt-assembly, and gave the full COMMON_FLAGS. I set compared_against_cpp_std_directly to false, because RapidJSON is a third-party C++ library and not a C++ standard library.
- **Fields the verifier corrected:** `compiler_and_flags`, `compared_against_cpp_std_directly`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/kostya/benchmarks#json>
  - <https://github.com/kostya/benchmarks/blob/master/common/commands.mk>
  - <https://github.com/kostya/benchmarks/blob/master/json/Makefile>
  - <https://github.com/kostya/benchmarks/blob/master/json/json-scala/Makefile>
  - <https://github.com/kostya/benchmarks/blob/master/json/json-scala/Maven.list>
  - <https://github.com/kostya/benchmarks/blob/master/json/json-scala/src/main/scala/JsonTest.scala>
  - <https://github.com/kostya/benchmarks/blob/master/json/test_rapid.cpp>
  - <https://github.com/kostya/benchmarks/blob/master/json/generate_json.rb>
  - <https://github.com/plokhotnyuk/jsoniter-scala>
- **Sources the enricher read:**
  - <https://github.com/plokhotnyuk/jsoniter-scala>
  - <https://github.com/plokhotnyuk/jsoniter-scala/blob/master/README.md>
  - <https://github.com/plokhotnyuk/jsoniter-scala/blob/master/build.sbt>
  - <https://github.com/plokhotnyuk/jsoniter-scala/blob/master/jsoniter-scala-core/jvm-native/src/main/scala/com/github/plokhotnyuk/jsoniter_scala/core/JsonReader.scala>
  - <https://github.com/plokhotnyuk/jsoniter-scala/blob/master/jsoniter-scala-core/jvm-native/src/main/scala/com/github/plokhotnyuk/jsoniter_scala/core/package.scala>
  - <https://github.com/plokhotnyuk/jsoniter-scala/blob/master/jsoniter-scala-core/jvm/src/main/java/com/github/plokhotnyuk/jsoniter_scala/core/ByteArrayAccess.java>
  - <https://github.com/plokhotnyuk/jsoniter-scala/blob/master/jsoniter-scala-core/shared/src/main/scala/com/github/plokhotnyuk/jsoniter_scala/core/ReaderConfig.scala>
  - <https://github.com/plokhotnyuk/jsoniter-scala/blob/master/jsoniter-scala-core/shared/src/main/scala/com/github/plokhotnyuk/jsoniter_scala/core/JsonCodec.scala>
  - <https://github.com/plokhotnyuk/jsoniter-scala/blob/master/jsoniter-scala-macros/shared/src/main/scala-3/com/github/plokhotnyuk/jsoniter_scala/macros/JsonCodecMaker.scala>
  - <https://github.com/plokhotnyuk/jsoniter-scala/releases>
  - <https://github.com/plokhotnyuk/jsoniter-scala/issues?q=label%3Abug>
  - <https://github.com/plokhotnyuk/jsoniter-scala/issues?q=label%3Aperformance+is%3Aopen>
  - <https://github.com/plokhotnyuk/jsoniter-scala/issues/650>
  - <https://github.com/plokhotnyuk/jsoniter-scala/security/advisories>
  - <https://github.com/advisories?query=ecosystem%3Amaven+jsoniter-scala>
  - <https://github.com/kostya/benchmarks#json>
  - <https://github.com/kostya/benchmarks/blob/master/json/json-scala/src/main/scala/JsonTest.scala>
  - <https://github.com/kostya/benchmarks/blob/master/json/json-scala/Maven.list>
  - <https://github.com/kostya/benchmarks/blob/master/json/json-scala/Makefile>
  - <https://github.com/kostya/benchmarks/blob/master/json/test_rapid.cpp>
  - <https://github.com/kostya/benchmarks/blob/master/json/Makefile>
  - <https://github.com/kostya/benchmarks/blob/master/common/commands.mk>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/plokhotnyuk/jsoniter-scala`) · [data/wave4/enrich/raw/github_com_plokhotnyuk_jsoniter_scala.json](../../../data/wave4/enrich/raw/github_com_plokhotnyuk_jsoniter_scala.json) (enrichment confidence 0.8)

</details>
