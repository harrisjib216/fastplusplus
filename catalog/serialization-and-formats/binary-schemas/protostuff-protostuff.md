# protostuff

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Java` · `Apache-2.0` · 🟡 stale

> Java serializer using a protobuf-style tagged binary format; serializes about 1.4x faster than protobuf-java but deserializes slower.

| | |
|---|---|
| **Beats** | Protobuf |
| **Claimed result** | Main jvm-serializers results (wiki Home, edited 2023-10-08, JVM 11.0.19): protostuff total (ser+deser) 1,261 ns vs protobuf 1,402 ns (\~1.11x); ser 608 vs 875 ns (\~1.44x); deser 653 vs 527 ns (protobuf \~1.24x faster); size 242 vs 242 bytes. Older Staging-Results page (last edited 2017-07-22): total 1,173 vs 1,950 ns (\~1.66x), ser 444 vs 1,193 ns (\~2.7x), deser 689 vs 689 ns (tie), size 239 vs 239 bytes (derived from page data) |
| **Workload** | Serialize plus full deserialize of the 'media content' object tree (cycle-free, schema known in advance) in the eishay/jvm-serializers suite; times in ns per op; 'total' = ser + deser. |
| **Metric** | latency |
| **Hardware** | 2.6 GHz 6-Core Intel Core i7 (exact model not stated), Mac OS X / Darwin Kernel 21.6.0, 12 logical cores (wiki Home) |
| **Compiler and flags** | JVM: Oracle Corporation 11.0.19 (wiki Home test platform); JVM flags not stated |
| **Adoption** | 2.1k stars |
| **Last commit** | 2025-04-02 |
| **Links** | [repository](https://github.com/protostuff/protostuff) · [benchmark](https://github.com/eishay/jvm-serializers/wiki) |

## Verdict

On the eishay/jvm-serializers wiki (Home, edited 2023-10-08; Oracle JDK 11.0.19; 2.6 GHz 6-core Intel Core i7 on macOS/Darwin 21.6.0; JVM flags not stated), the media-content round trip with protostuff-generated code took 1,261 ns (ser 608 + deser 653) vs 1,402 ns for protobuf-java (875 + 527), about 1.11x overall. Serialization is \~1.44x faster and deserialization \~1.24x slower; both outputs are 242 bytes. The suite ships protobuf-java 3.6.1 and protostuff 1.5.9 jars, so newer protobuf-java releases are not measured.

## Use it when

- JVM-to-JVM RPC or cache/datastore values where the hot path is serialization: 608 vs 875 ns to serialize the \~242-byte jvm-serializers media object, compared with protobuf-java.
- You have existing Java POJOs and want protobuf-style tagged binary with schema evolution without writing .proto files or generating builder classes (protostuff-runtime; 1,389 ns total vs protobuf-java's 1,402 in the same run).
- You must emit protobuf wire bytes from plain Java objects with simple proto2-style shapes (scalars, strings, nested and repeated messages): ProtobufIOUtil measured 1,248 ns total vs 1,402 ns for protobuf-java.
- Object graphs with shared or cyclic references, which protobuf cannot encode: GraphIOUtil (protostuff-graph, 1,686 ns total in the same run).
- One schema needs several formats (binary for services, JSON/YAML for debugging) through the pluggable format modules.

## Skip it when

- Deserialization-heavy workloads: in the same run protobuf-java deserialized faster (527 vs 653 ns).
- Cross-language protobuf interop or strict proto3 compatibility: open issues report that map fields written by ProtobufIOUtil do not parse correctly in protobuf-java (#357, #362) and that proto3 backward compatibility is broken (#286). The default protostuff format uses groups for nested messages, so ordinary protobuf parsers cannot read it.
- You want the fastest JVM binary serializer: in the same jvm-serializers table, fury (442-508 ns total) and colfer (633 ns) beat protostuff's 1,261 ns.
- Modern JDKs and records: on JDK 17+ the runtime needs --add-opens for some JDK collection types (#360); JDK 8 and JDK 21 produce different String schemas, which breaks deserializing across JDKs (#371); Java records are unsupported (#313); and there has been no release since 1.8.0 (2022).
- Untrusted input with polymorphic fields: the default runtime writes class names and auto-loads them on read (auto_load_polymorphic_classes=true).

## How it is fast

The native protostuff format marks each nested message with START_GROUP/END_GROUP tags instead of a length prefix. That lets the encoder stream a whole object tree in one pass, with no size-computation pass first (protobuf-java computes and memoizes every message's size before writing). Its protobuf-format writer (ProtobufOutput) is also single-pass: it reserves one byte for the nested length and back-patches it when the message is under 128 bytes; otherwise it splices a new segment holding the length varint into the LinkedBuffer chain. Output goes into reusable chained byte-array segments (LinkedBuffer). UTF-8 strings are sized and written in one step, using a worst-case size bound. Runtime schemas are cached per class and, on HotSpot, read and write fields through sun.misc.Unsafe offsets instead of reflection.

## Compared with alternatives

Pick it over Simple Binary Encoding or Apache Thrift when you want to serialize an existing Java object model, cycles included, without a separate IDL or flyweight codec; thrift-compact was also slower in the same table (1,483 vs 1,261 ns). If raw JVM speed matters more than protobuf-style evolution or wire compatibility, Fury/Apache Fory (442-508 ns) and colfer (633 ns) were over 2x faster in the same table.

## Integration

| | |
|---|---|
| **Form** | module (Maven jars: io.protostuff:protostuff-core plus protostuff-runtime; latest on Maven Central is 1.8.0) |
| **Dependencies** | protostuff-api and protostuff-core; the runtime adds protostuff-collectionschema. The JSON/YAML modules need Jackson; codegen needs protostuff-compiler or the Maven plugin. |
| **Minimum toolchain** | Java 6 (the pom compiles with javac target 1.6; README says Java 1.6+); building needs Maven 3.2.3+. JDK 9+ support was added in 1.8.0; JDK 17+ may need --add-opens. |
| **Platforms** | Any JVM. The runtime uses sun.misc.Unsafe when a Sun/HotSpot ReflectionFactory is present and otherwise falls back to plain reflection. |
| **Thread safety** | RuntimeSchema.getSchema is thread-safe and caches the schema (README). A LinkedBuffer is per-call state: reuse one per thread and clear() it after every write. |
| **Drop-in for the baseline** | partial: ProtobufIOUtil writes and reads protobuf wire format from protostuff schemas, but there is no protobuf-java Message/Builder API. Map fields and proto3 compatibility have open bugs, and the default protostuff format is not protobuf-readable. |

## Gotchas

- toByteArray throws 'Buffer previously used and had not been reset' unless you call LinkedBuffer.clear() after each use; a buffer is not safe to share across threads.
- Runtime-schema field numbers come from declaration order (parent class first) unless you use @Tag. Inserting or reordering fields, or changing a base class, silently breaks old data. Without @Tag the limit is 126 fields, and tag 127 is reserved.
- Defaults chosen for protobuf compatibility lose information: null elements in collections are dropped, empty collections come back as null, and non-final POJO subclasses are not preserved. Enable preserve_null_elements / collection_schema_on_repeated_fields / morph_\* (system properties or IdStrategy flags) to keep them; these change the wire output.
- Polymorphic fields serialize the fully qualified class name, and auto_load_polymorphic_classes defaults to true, so input can make the runtime load classes by name. For untrusted data, pre-register your schemas and set it to false. No advisories are listed in the GitHub Advisory Database for protostuff-core or protostuff-runtime.

## Known shortcomings

- Small margin on the suite's current results (jvm-serializers wiki, 2023, JVM 11.0.19): about 1.11x total and 1.44x serialize over protobuf, and protobuf is faster at deserialize. The larger claim came from a 2017 staging page with no JVM or CPU stated.
- Protobuf compatibility is partial: map fields written with ProtobufIOUtil fail to parse in protobuf-java (#357, #362), proto3 backward compatibility is broken (#286), and the default format encodes nested messages as groups. JDK 17+ needs --add-opens, JDK 8 vs 21 String schemas differ (#371), no records support; last release 1.8.0 (2022-03). auto_load_polymorphic_classes is on by default. fury and colfer are more than 2x faster in the same suite.

## Caveats and trade-offs

Times are in nanoseconds, not microseconds (wiki Home: 'Ser Time+Deser Time (ns)'). 'total' is ser + deser and does not include create. The record's staging numbers come from a page last edited 2017-07-22 that states no JVM, flags, or CPU. The current main results (2023-10-08, JVM 11.0.19, generic Core i7, no JVM flags) show a much smaller total win (\~1.11x), and there protobuf is faster at deserialization. The suite repo's last commit was 2023-10-07.

JVM-only; protostuff can emit protobuf-wire-compatible output while using a faster runtime encoder, but requires protostuff's own runtime schema/codegen machinery.

## Maintenance

Stale: last commit 2025-04-02 (a null-check fix) and last Maven Central release 1.8.0 in March 2022, with open unanswered requests for a new release and JDK 21 support. It is Apache-2.0 and still a straightforward Maven dependency for Java 8/11 codebases.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification B, tier now B.
- **Tier reason:** Well-known independent suite (eishay/jvm-serializers, about 3.3k stars) with public code, comparing protostuff with protobuf in the same run. The main wiki results give JVM 11.0.19 and only a generic '2.6 GHz 6-Core Intel Core i7' (no exact model, no JVM flags). The cited Staging-Results page gives no JVM or CPU at all, so it cannot be A.
- **Verifier notes:** Downgraded for an overstated/misstated claim, not for tier (stays B). The staging numbers are real but wrongly labelled µs, with 'total' wrongly described as including create, and they are superseded by the suite's current main results, which show \~1.11x total and \~1.44x serialize. benchmark_url repointed to the main wiki results. Metadata (Apache-2.0, 2,098 stars, last commit 2025-04-02, stale) all verified.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/eishay/jvm-serializers/wiki/Staging-Results>
  - <https://raw.githubusercontent.com/wiki/eishay/jvm-serializers/Staging-Results.md>
  - <https://github.com/eishay/jvm-serializers/wiki/Staging-Results/_history>
  - <https://github.com/eishay/jvm-serializers/wiki>
  - <https://github.com/eishay/jvm-serializers/wiki/Home/_history>
  - <https://github.com/eishay/jvm-serializers>
  - <https://github.com/protostuff/protostuff>
- **Sources the enricher read:**
  - <https://github.com/protostuff/protostuff>
  - <https://github.com/protostuff/protostuff/blob/master/README.md>
  - <https://github.com/protostuff/protostuff/blob/master/CHANGELOG.md>
  - <https://github.com/protostuff/protostuff/blob/master/pom.xml>
  - <https://github.com/protostuff/protostuff/blob/master/protostuff-runtime/pom.xml>
  - <https://github.com/protostuff/protostuff/blob/master/protostuff-core/pom.xml>
  - <https://github.com/protostuff/protostuff/blob/master/protostuff-core/src/main/java/io/protostuff/ProtostuffOutput.java>
  - <https://github.com/protostuff/protostuff/blob/master/protostuff-core/src/main/java/io/protostuff/ProtobufOutput.java>
  - <https://github.com/protostuff/protostuff/blob/master/protostuff-core/src/main/java/io/protostuff/ProtobufIOUtil.java>
  - <https://github.com/protostuff/protostuff/blob/master/protostuff-core/src/main/java/io/protostuff/ProtostuffIOUtil.java>
  - <https://github.com/protostuff/protostuff/blob/master/protostuff-api/src/main/java/io/protostuff/LinkedBuffer.java>
  - <https://github.com/protostuff/protostuff/blob/master/protostuff-api/src/main/java/io/protostuff/StringSerializer.java>
  - <https://github.com/protostuff/protostuff/blob/master/protostuff-runtime/src/main/java/io/protostuff/runtime/RuntimeEnv.java>
  - <https://github.com/protostuff/protostuff/blob/master/protostuff-runtime/src/main/java/io/protostuff/runtime/RuntimeSchema.java>
  - <https://github.com/protostuff/protostuff/blob/master/protostuff-runtime/src/main/java/io/protostuff/runtime/UnsafeAccessor.java>
  - <https://github.com/protostuff/protostuff/blob/master/protostuff-runtime/src/main/java/io/protostuff/runtime/RuntimeUnsafeFieldFactory.java>
  - <https://github.com/protostuff/protostuff/blob/master/protostuff-runtime/src/main/java/io/protostuff/runtime/RuntimeFieldFactory.java>
  - <https://github.com/protostuff/protostuff/commits/master>
  - <https://github.com/protostuff/protostuff/tags>
  - <https://github.com/protostuff/protostuff/issues>
  - <https://github.com/protostuff/protostuff/issues/374>
  - <https://github.com/protostuff/protostuff/issues/319>
  - <https://github.com/protostuff/protostuff/issues/331>
  - <https://github.com/protostuff/protostuff/issues/371>
  - <https://github.com/protostuff/protostuff/issues/376>
  - <https://github.com/protostuff/protostuff/issues/360>
  - <https://github.com/protostuff/protostuff/issues/357>
  - <https://github.com/protostuff/protostuff/issues/362>
  - <https://github.com/protostuff/protostuff/issues/313>
  - <https://github.com/protostuff/protostuff/issues/286>
  - <https://github.com/protostuff/protostuff/issues/254>
  - <https://github.com/protostuff/protostuff.github.io/blob/master/documentation/tmp/ProtostuffSerialization.md>
  - <https://github.com/protostuff/protostuff.github.io/blob/master/documentation/tmp/ThingsYouNeedToKnow.md>
  - <https://github.com/eishay/jvm-serializers/wiki>
  - <https://github.com/eishay/jvm-serializers>
  - <https://github.com/eishay/jvm-serializers/blob/master/tpc/src/serializers/protostuff/Protostuff.java>
  - <https://github.com/eishay/jvm-serializers/blob/master/tpc/src/serializers/protobuf/Protobuf.java>
  - <https://repo1.maven.org/maven2/io/protostuff/protostuff-runtime/maven-metadata.xml>
  - https://api.github.com/graphql (GitHub Advisory Database query: io.protostuff:protostuff-core, io.protostuff:protostuff-runtime)
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/protostuff/protostuff`) · [data/wave4/enrich/raw/github_com_protostuff_protostuff.json](../../../data/wave4/enrich/raw/github_com_protostuff_protostuff.json) (enrichment confidence 0.8)

</details>
