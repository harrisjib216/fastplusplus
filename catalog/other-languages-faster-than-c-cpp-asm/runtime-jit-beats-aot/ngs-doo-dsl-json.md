# DSL-JSON (Java, HotSpot) vs nlohmann/json, json-c and Boost.PropertyTree in kostya/benchmarks JSON

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Java` · `BSD-3-Clause` · 🟢 active

> Java JSON databinding library with compile-time generated converters; about 2x nlohmann/json and json-c in kostya's JSON test, far behind fast C/C++ parsers.

| | |
|---|---|
| **Beats** | nlohmann/json (C++), json-c (C library called from a C++ driver) and Boost.PropertyTree (C++) as built by kostya/benchmarks; DSL-JSON does NOT beat RapidJSON (all variants incl. SAX Precise), Boost.JSON, simdjson, yyjson, yajl, gason or DAW JSON Link in the same table |
| **Claimed result** | Time in seconds (lower is better), from the kostya/benchmarks README Json table (median of runs, UPDATE: 2026-07-19): Java (DSL-JSON) 0.571; C++/clang++ (Nlohmann) 1.182; C++/g++ (Nlohmann) 1.266; C++/clang++ (json-c) 1.185; C++/g++ (json-c) 1.187; C++/clang++ (Boost.PropertyTree) 2.589; C++/g++ (Boost.PropertyTree) 2.907. That is about 2.1-2.2x faster than Nlohmann and json-c, 4.5-5.1x faster than Boost.PropertyTree (derived from page data). In the same table it is slower than C++/g++ (simdjson On-Demand) 0.060, C++/clang++ (DAW JSON Link NoCheck) 0.070, C++/clang++ (simdjson DOM) 0.103, C++/g++ (gason) 0.127, C/gcc (yyjson) 0.131, C++/g++ (RapidJSON) 0.154, C/gcc (yajl) 0.362, C++/g++ (Boost.JSON) 0.374 and C++/clang++ (RapidJSON SAX Precise) 0.500. |
| **Workload** | Parse a generated 524,288-object JSON file (generate_json.rb: x, y, z doubles plus name and opts fields, pretty-printed) and compute the mean of x, y and z; the README reports median time of the benchmark execution (data loading and code self-testing are not measured). |
| **Metric** | throughput |
| **Hardware** | Intel(R) Xeon(R) E-2324G (README Environment section; Docker on Debian forky/sid); README results marked UPDATE: 2026-07-19 |
| **Compiler and flags** | Json table rows measured 2025-08-17: C++ with gcc 14.2.0 and clang 19.1.7 (common/commands.mk flags -Wall -Wextra -pedantic -Wcast-align -O3 -march=native -flto=auto, -std=c++23; clang with -stdlib=libc++). The gcc 16.1.0 / clang 22.1.8 versions in the README environment table belong to the 2026-07-19 update, which re-measured only the Primes table. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | yes |
| **Why it wins** | From the DSL-JSON README FAQ: almost zero allocations, works on byte level, better algorithms for byte[] to type conversion, minimized unexpected branching, and compile-time databinding (generated converters) instead of reflection. |
| **Adoption** | 1.1k stars; 10 commits since 2025-10-11 |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/ngs-doo/dsl-json) · [benchmark](https://github.com/kostya/benchmarks) |

## Verdict

kostya/benchmarks' JSON test (parse a 524,288-object pretty-printed file and average x, y, z; median of runs on an Intel Xeon E-2324G, update 2026-07-19) timed DSL-JSON 2.0.2 on HotSpot with default flags (JDK 24.0.2 per the README, 26.0.1 per the current Dockerfile) at 0.571 s against nlohmann/json at 1.182 s (clang++ 22.1.8) and 1.266 s (g++ 16.1.0), json-c at 1.185-1.187 s and Boost.PropertyTree at 2.589-2.907 s, all built -O3 -march=native -flto=auto; the gain is schema binding versus DOM building, not Java codegen.

## Use it when

- Java or Kotlin services that bind known JSON shapes into POJOs and want one of the fastest JVM codecs without leaving Java (0.571 s in kostya's JSON test against 1.18-1.27 s for nlohmann/json and json-c).
- Android or Java 8 targets: v2 targets Java 8 and the README documents Android Gradle setup.
- Large arrays of small objects where only a few fields matter: unknown fields are skipped, not built, and the streaming iterateOver API reads big lists with little memory.
- Codecs that must avoid reflection at runtime, since converters are generated and discovered through META-INF/services.

## Skip it when

- You can call C or C++: simdjson On-Demand (0.060 s), DAW JSON Link (0.070-0.089 s), yyjson (0.131 s), RapidJSON (0.154 s), Boost.JSON (0.374 s) and yajl (0.362 s) all beat it on the same test, and so does jsoniter-scala on the JVM (0.147 s).
- Arbitrary or schema-less JSON: the fast path needs compile-time types; the reflection mode is described by the authors as only comparable to Jackson.
- Memory-tight processes: the JVM row used 277.81 MiB base plus 163.69 MiB peak, against 113 MiB base for the C/C++ rows; only the DOM-building C++ libraries (nlohmann +360-448 MiB, json-c +1,216 MiB) used more on top.
- You need a maintained release: the last release on Maven Central is 2.0.2 (2023-08-29); fixes since then, including a double-parsing crash and the Ryu parser, are on master only.
- Strict input validation or security-sensitive parsing without review: open issues report spec-profile misses for 2.0.2 (#300) and an XXE path in XmlConverter (#296).

## How it is fast

Generated converters read the byte[] directly with no intermediate char or String form, match property names by a hash of their bytes rather than by string comparison, skip unknown properties without materialising them, and allocate almost nothing beyond the target objects (README FAQ: almost zero allocations, byte-level work, minimised branching, compile-time databinding instead of reflection). In the benchmarked 2.0.2 release, numbers of up to 15 + precision-level characters are parsed by a hand-written digit loop with an approximate correction step, and longer ones fall back to Double.parseDouble on a new String; master (2026-10-06, unreleased) replaces this with an exact Ryu-style parser.

## Compared with alternatives

Against JSON3.jl, the other catalogued kostya JSON entry (0.700 s, 631.76 + 332.81 MiB), DSL-JSON is faster and lighter on the same test; pick it when the code base is Java or Kotlin, and pick jsoniter-scala (0.147 s, catalogued under JSON) instead for Scala, or a C++ binder such as simdjson On-Demand or DAW JSON Link when native code is an option.

## Integration

| | |
|---|---|
| **Form** | Maven jar (com.dslplatform:dsl-json) with a bundled annotation processor |
| **Dependencies** | none at runtime for the core jar (README: about 450KB); the JSON-B API is a provided dependency for JsonB support; Kotlin uses the same artifact through kapt, Scala needs dsl-json-scala |
| **Minimum toolchain** | Java 8 (v2 targets Java 8); the kostya build compiles with javac -proc:full so the processor on the classpath runs |
| **Platforms** | any JVM, Android; Kotlin via kapt; Scala via dsl-json-scala |
| **Thread safety** | README: create one DslJson and always reuse it; its serialize and deserialize methods reuse readers and writers through thread-local variables, while a JsonReader or JsonWriter you create via newReader/newWriter is a single-owner object |
| **Drop-in for the baseline** | no |

## Gotchas

- The comparison is not like-for-like: the Java test binds only coordinates[].x/y/z into generated classes and skips name, opts and info, while the nlohmann driver builds a full std::map DOM (and destroys it inside the timed call) and json-c builds a tree it never frees; RapidJSON SAX Precise (0.433-0.500 s), the closest C++ shape, is still faster than DSL-JSON's 0.571 s.
- Correction to the record's reading of DoublePrecision.LOW: in 2.0.2 it only raises the fast-path length limit to 19 characters (15 + level 4). The x and y values in the generated file are exponent-form doubles of about 21-22 characters, so they still go through Double.parseDouble on a new String, and only z (about 18-19 characters) takes the approximate path; the suite's README flags reduced-precision C/C++ variants but not this setting, and the output is printed to %g without a cross-language check.
- Released 2.0.2 throws ArrayIndexOutOfBoundsException in NumberConverter.approximateDouble on some doubles such as 2E15 or 2670986322885633.0 (issue #283); the maintainer says it works on master (2026-10-10), which has no release.
- The benchmark constructs a new DslJson with includeServiceLoader inside every timed calc call and runs a single cold parse with no JIT warm-up, contrary to the README's advice to reuse the instance; both choices count against Java, so the 2x over nlohmann is not inflated by them. Properties are matched by hash by default (hashMatch), so a colliding unknown name can land in the wrong field unless hashMatch is turned off.

## Known shortcomings

- Beats only nlohmann/json, json-c and Boost.PropertyTree in kostya/benchmarks JSON; loses to simdjson, DAW, gason, yyjson, RapidJSON, yajl and Boost.JSON; the Java side binds to a schema, skips fields and uses low-precision doubles while nlohmann builds a full DOM with its teardown timed; the Java build is plain javac -proc:full (not --release 26); JDK version unclear (README 24.0.2, Dockerfile 26.0.1); the json-c baseline is the Debian prebuilt library, not a suite -O3 build.
- Correction from the 2.0.2 source (commit d1f7a8d): DoublePrecision.LOW only raises the fast-path limit to 19 characters, so the x and y fields (about 21-22 characters, exponent form) still go through exact Double.parseDouble and only z takes the approximate path; the kostya README flags reduced-precision C++ variants but not this one, and nothing cross-checks output. Released 2.0.2 throws AIOOBE in approximateDouble on 2E15 (#283), fixed only on unreleased master; XXE report #296. RapidJSON SAX Precise (the closest C++ shape) is still faster, 0.433-0.500 s vs 0.571.
- The JSON3.jl enricher found that kostya/benchmarks' 2026-07-19 update re-measured only the Primes table and the environment table: the Json table rows kept their 2025-08-17 values (gcc 14.2.0, clang 19.1.7), so the compiler versions recorded here (gcc 16.1.0, clang 22.1.8) describe the current environment table and may not be the toolchain behind this table's rows; whether this table was re-run on 2026-07-19 was not checked.

## Caveats and trade-offs

Beats only the slow C/C++ JSON libraries; the fast ones (simdjson, DAW JSON Link, gason, yyjson, RapidJSON, yajl, Boost.JSON, RapidJSON SAX Precise) are about 1.1-9.5x faster than it in the same table (derived from page data), so this is not Java beating the C/C++ incumbent for fast JSON. Work is not identical: the Java test deserialises straight into generated Root/Coordinate classes that declare only coordinates and x, y, z (name, opts and info are skipped, not materialised) with JsonReader.DoublePrecision.LOW (reduced number-parsing accuracy), while the nlohmann test builds a full DOM (std::map objects, std::string keys and values) and calls get&lt;double&gt;. The C++ timed window also includes destruction of the nlohmann DOM when calc returns, whereas Java leaves its objects to the GC; the json-c driver never frees its tree. JIT warm-up is not separated: the self-test calls calc twice on tiny inputs, so the timed run is a single cold-ish parse (this hurts Java, not the baselines). Results are printed but not cross-checked between languages. json-c is a Debian prebuilt library. The README says implementations are written 'as the average software developer would write them'. The DSL-JSON README cites this benchmark only as 'fastest performing Java JSON library' and makes no C++ comparison; its FAQ explanation of speed is the library author's own. JDK version ambiguous (README table Java 24.0.2, Dockerfile JDK 26.0.1). [retier] The Json table was last re-run on 2025-08-17; the 2026-07-19 README update changed only the Primes table and the environment table.

Fast path needs compile-time databinding (annotation processor generates converters for @CompiledJson classes); the reflection variant is described as only comparable to Jackson. JVM warm-up and heap are part of the cost: the table shows 277.81 MiB base + 163.69 MiB peak increase for Java versus 113.33 + 447.88 MiB for g++ nlohmann and 113.21 + 123.44 MiB for g++ RapidJSON.

## Maintenance

BSD-3-Clause, 1.1k stars and 422 commits; master is active again in 2026 (Ryu number parsing, XML security fixes, skipNullValues) after almost no commits between August 2023 and June 2026, but the last published release is still 2.0.2 from 2023-08-29 with 41 open issues, so pin a version and test your number edge cases.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** kostya/benchmarks is a public third-party suite: benchmark code json/json-java/src/main/java/bench/TestJava.java vs json/test_nlohmann_json.cpp, json/test_libjson.cpp and json/test_boost_ptree.cpp, C++ flags in common/commands.mk (-O3 -march=native -flto=auto, g++ 16.1.0, clang++ 22.1.8), Java build in json/json-java/Makefile, CPU Intel Xeon E-2324G in the README Environment section. Every number in the record matches the README Json table rows (UPDATE: 2026-07-19).
- **Verifier notes:** Numbers verified row by row on the kostya/benchmarks README; tier A holds. Main shortcomings: wins only over slow DOM libraries (Nlohmann, json-c, Boost.PropertyTree), loses to every fast C/C++ parser incl. yajl; schema binding with skipped fields and low-precision doubles against a full DOM whose teardown is timed, so the gain is library design, not Java. Corrected the Java build description (json-java/Makefile uses plain javac -proc:full) and flagged the JDK version ambiguity.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-92 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/kostya/benchmarks>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/common/commands.mk>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/json/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/json/generate_json.rb>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/json/json-java/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/json/json-java/Maven.list>
  - <https://github.com/kostya/benchmarks/tree/master/json/json-java/src>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/json/json-java/src/main/java/bench/TestJava.java>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/json/test_nlohmann_json.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/json/test_libjson.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/json/test_boost_ptree.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/docker/Dockerfile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/xtime.rb>
  - <https://github.com/ngs-doo/dsl-json>
  - <https://github.com/ngs-doo/dsl-json/commits>
- **Sources the enricher read:**
  - <https://github.com/ngs-doo/dsl-json>
  - <https://github.com/ngs-doo/dsl-json/commits>
  - <https://github.com/ngs-doo/dsl-json/tags>
  - <https://github.com/ngs-doo/dsl-json/issues>
  - <https://github.com/ngs-doo/dsl-json/issues/283>
  - <https://github.com/ngs-doo/dsl-json/issues/297>
  - <https://github.com/ngs-doo/dsl-json/issues/300>
  - <https://github.com/ngs-doo/dsl-json/commits/master/library/src/main/java/com/dslplatform/json/NumberConverter.java>
  - <https://raw.githubusercontent.com/ngs-doo/dsl-json/HEAD/README.md>
  - <https://raw.githubusercontent.com/ngs-doo/dsl-json/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ngs-doo/dsl-json/HEAD/library/src/main/java/com/dslplatform/json/JsonReader.java>
  - <https://raw.githubusercontent.com/ngs-doo/dsl-json/HEAD/library/src/main/java/com/dslplatform/json/NumberConverter.java>
  - <https://raw.githubusercontent.com/ngs-doo/dsl-json/HEAD/library/src/main/java/com/dslplatform/json/RyuParser.java>
  - <https://raw.githubusercontent.com/ngs-doo/dsl-json/d1f7a8d/library/src/main/java/com/dslplatform/json/NumberConverter.java>
  - <https://raw.githubusercontent.com/ngs-doo/dsl-json/d1f7a8d/library/src/main/java/com/dslplatform/json/JsonReader.java>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/json/json-java/src/main/java/bench/TestJava.java>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/json/json-java/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/json/json-java/Maven.list>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/json/test_nlohmann_json.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/json/test_libjson.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/json/test_boost_ptree.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/json/generate_json.rb>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/json/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/common/commands.mk>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/docker/Dockerfile>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/ngs-doo/dsl-json`) · [data/wave14/enrich/raw/github_com_ngs_doo_dsl_json.json](../../../data/wave14/enrich/raw/github_com_ngs_doo_dsl_json.json) (enrichment confidence 0.58)

</details>
