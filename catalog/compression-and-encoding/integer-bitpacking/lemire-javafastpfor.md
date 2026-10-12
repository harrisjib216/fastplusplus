# JavaFastPFOR

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Integer compression and bit-packing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Java` · `Apache-2.0` · 🟢 active

> Java integer-array codecs (FastPFOR, binary packing, OptPFD, Simple9) that decode 2.7x-4x faster than VariableByte and Kamikaze PForDelta.

| | |
|---|---|
| **Beats** | VariableByte (the varint scheme included in the same library) and Kamikaze PForDelta |
| **Claimed result** | benchmarkresults_icore7_10may2013.txt, sparsity 1, decompression: IntegratedBinaryPacking+IntegratedVariableByte 1183 mis and FastPFOR+VariableByte 811 mis, versus VariableByte 299 mis and Kamikaze PForDelta 262 mis (IntegratedBinaryPacking about 4.0x over VariableByte and 4.5x over Kamikaze; FastPFOR about 2.7x over VariableByte and 3.1x over Kamikaze, derived from page data). Compression: 639 mis versus 199 (VariableByte) and 51 (Kamikaze). README says over 1.2 billion ints per second (4.5 GB/s) decode and that Kamikaze PForDelta is slower. |
| **Workload** | Compressing and decompressing sorted-gap integer arrays (benchmark run at sparsity 1, 2, ...), reporting bits per int and millions of ints per second; Java port of the FastPFor C++ library. |
| **Metric** | throughput |
| **Hardware** | Core i7 (from the result file name 'icore7', exact model not stated), 2013 |
| **Adoption** | 569 stars, 66 forks; used in LinkedIn Pinot, Apache NiFi, Terrier and ClueWeb Tools (per README); parts integrated into Parquet and inspired Lucene's PForDeltaDocIdSet |
| **Last commit** | 2026-06-24 |
| **Links** | [repository](https://github.com/lemire/JavaFastPFOR) · [benchmark](https://github.com/lemire/JavaFastPFOR/blob/master/benchmarkresults/benchmarkresults_icore7_10may2013.txt) |

## Verdict

benchmarkresults_icore7_10may2013.txt (an unspecified Core i7 with an unspecified JVM and flags, May 2013) measures synthetic clustered sorted arrays at sparsity 1, with delta coding inside the timed region. Each codec runs three times and only the third run is reported, as JIT warm-up, and every round trip is checked. Decode speeds: FastPFOR+VariableByte 811 M ints/s, IntegratedBinaryPacking 1,183 M ints/s, VariableByte 299 M ints/s, Kamikaze PForDelta 262 M ints/s. Those numbers predate the FastPFOR bug fixes of November 2013 and February 2014 and the September 2014 format change, so today's code has never been timed against them.

## Use it when

- JVM search engines, OLAP stores and inverted indexes that hold sorted docID or posting lists as int[] (the same niche as Pinot, Terrier and NiFi, which the README lists as users).
- Arrays of thousands of integers or more where most values or gaps need far fewer than 32 bits; FastPFOR copes with occasional large outliers better than plain binary packing.
- Decode-heavy workloads: in the 2013 run FastPFOR+VariableByte decoded 811 M ints/s at 2.78 bits/int versus 299 M ints/s at 8 bits/int for VariableByte.
- Sorted input where you want the fastest decode: IntegratedBinaryPacking+IntegratedVariableByte reached 1,183 M ints/s, close to the 1,468 M ints/s of a plain copy.

## Skip it when

- C or C++ code: use the C++ FastPFor library (already catalogued), which also has SIMD codecs that this port lacks.
- Short arrays (under about 1,024 integers, per the FastPFOR javadoc) or random 32-bit values; random integers do not compress.
- Older JVMs: current releases are built with maven.compiler.release 21, so they need JDK 21 or later (releases up to 0.1.12 ran on Java 7).
- Relying on the vector codecs for speed: issue #53 ('vector implementation is slower than the scalar one', Nov 2022) is still open, and the README warns that on aarch64 before JDK 24 the Vector API fallback is slower than the scalar codec.
- Long (64-bit) values: the codecs work on int[] only (issue #30 asked about long support).

## How it is fast

FastPFOR is patched frame-of-reference coding. Per 256-integer block it picks a bit width b by a cost model (getBestBFromData), bit-packs all values with b bits using unrolled 32-integer fastpack/fastunpack routines, and stores the high bits of outliers as exceptions grouped by width and bit-packed per page of 65,536 integers. Most of the decode is straight-line shift/mask code with no per-integer branches, which the JIT compiles well; the 'Integrated' codecs also fold the delta/prefix-sum into the unpack loop. An optional vector package (VectorFastPFOR, VectorBitPacker) uses the incubating Java Vector API.

## Compared with alternatives

Pick it when you are on the JVM and want pure-Java code with no JNI. Its C++ parent FastPFor and simdcomp/TurboPFor are faster but need native code, and TurboPFor's Java wrapper is GPL. Pick VTEnc or Stream VByte in C/C++ instead when you can call native code.

## Integration

| | |
|---|---|
| **Form** | Maven/Gradle jar (me.lemire.integercompression:JavaFastPFOR on Maven Central, also JitPack) |
| **Dependencies** | none at runtime (JUnit and RoaringBitmap are test-scope only); the vector package needs --add-modules jdk.incubator.vector |
| **Minimum toolchain** | JDK 21 for current releases (pom release 21; 0.3.14 tagged 2026-06-24); Java 7 for releases up to 0.1.12 |
| **Platforms** | any JVM; vector codecs want x86-64 AVX2/AVX-512 or aarch64 on JDK 24+ |
| **Thread safety** | Instances hold mutable scratch buffers (FastPFOR keeps dataTobePacked, dataPointers and a direct ByteBuffer), so the README says to use one codec per thread. |
| **Drop-in for the baseline** | partial: it uses the same IntegerCODEC interface as the library's VariableByte, so swapping codecs is a one-line change, but the formats are not interchangeable, and it is not API-compatible with Kamikaze PForDelta. |

## Gotchas

- FastPFOR, FastPFOR128 and BinaryPacking compress only the largest multiple of their block size and silently ignore the rest. Wrap them in Composition(..., new VariableByte()) or use IntCompressor, or the tail is lost.
- Plain codecs do not apply delta coding: call Delta.delta on sorted lists first, or use the Integrated\* codecs in the differential package, which need sorted input.
- Reusing one FastPFOR128 instance can give different compressed bytes for the same input (issue #59, closed with no linked fix). From reading the code: dataTobePacked is not cleared between calls, so stale exception values fill the padding bits of the last packed word. Decoding still works, but byte-for-byte golden tests and content hashing of the output can fail.
- Decoders trust their input: sizes and bit widths come from the stream without validation, so corrupt or hostile data raises ArrayIndexOutOfBounds or BufferOverflow exceptions or forces large allocations rather than returning an error. Each FastPFOR instance also allocates about 66 KB of direct (off-heap) memory.

## Known shortcomings

- May 2013 numbers predate the FastPFOR bug fixes (0.0.9 Nov 2013, 0.0.11 Feb 2014) and the 0.1.1 format change (Sep 2014); current code was never re-timed against them. Issue #59: a reused FastPFOR128 gives different compressed bytes for the same input (stale bits land in padding, decode still correct). Vector codecs are slower than scalar (issue #53 open; aarch64 needs JDK 24+). Block codecs silently drop the tail unless wrapped in Composition. Decoders do not validate input. Not thread-safe per instance. JDK 21+. CHANGELOG stale since 2016.

## Caveats and trade-offs

Result file is from 2013 on an unspecified Core i7 and JVM; no JVM flags stated. The VariableByte baseline is the library's own implementation. The repository now lives at github.com/fast-pack/JavaFastPFOR (lemire/JavaFastPFOR redirects). Current development versions require JDK 21+. This is the Java port of the already catalogued C++ FastPFor library.

JVM only; usable from C++ only by using the C++ FastPFor instead (already catalogued). Integrated (delta) codecs need sorted input. Development versions need JDK 21 or later.

## Maintenance

Actively maintained under fast-pack (Apache-2.0, releases 0.3.5 to 0.3.14 between October 2025 and June 2026), but the published benchmark is 13 years old, the CHANGELOG stops at 0.1.10 (2016), and the README's dependency snippet still shows 0.3.8.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The 2013 result file compares the codecs against Kamikaze PForDelta and VariableByte, and the benchmark code is public (me.lemire.integercompression.benchmarktools.Benchmark), but the exact CPU model and JVM/flags are not stated, so first-party C. The techniques are also peer reviewed (Lemire and Boytsov, SPE 2015), but those measurements are of the C++ code, not this Java port.
- **Verifier notes:** Numbers match the result file. Repo redirects to fast-pack/JavaFastPFOR; Apache-2.0, 569 stars, last commit 2026-06-24 confirmed. Orchestrator may want to update repo_url to the fast-pack URL; I left the id unchanged.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** first-party benchmark with round-trip check and JIT warmup
- **Pages the verifier opened:**
  - <https://github.com/lemire/JavaFastPFOR>
  - <https://github.com/fast-pack/JavaFastPFOR/commits>
  - <https://raw.githubusercontent.com/lemire/JavaFastPFOR/HEAD/benchmarkresults/benchmarkresults_icore7_10may2013.txt>
  - <https://raw.githubusercontent.com/lemire/JavaFastPFOR/HEAD/README.md>
  - <https://raw.githubusercontent.com/lemire/JavaFastPFOR/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/fast-pack/JavaFastPFOR>
  - <https://github.com/fast-pack/JavaFastPFOR/issues?q=is%3Aissue>
  - <https://github.com/fast-pack/JavaFastPFOR/issues/53>
  - <https://github.com/fast-pack/JavaFastPFOR/issues/59>
  - <https://github.com/fast-pack/JavaFastPFOR/tags>
  - <https://github.com/fast-pack/JavaFastPFOR/tree/master/src/main/java/me/lemire/integercompression>
  - <https://github.com/fast-pack/JavaFastPFOR/tree/master/src/main/java/me/lemire/integercompression/vector>
  - <https://raw.githubusercontent.com/fast-pack/JavaFastPFOR/HEAD/README.md>
  - <https://raw.githubusercontent.com/fast-pack/JavaFastPFOR/HEAD/pom.xml>
  - <https://raw.githubusercontent.com/fast-pack/JavaFastPFOR/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/fast-pack/JavaFastPFOR/HEAD/CHANGELOG>
  - <https://raw.githubusercontent.com/fast-pack/JavaFastPFOR/HEAD/benchmarkresults/benchmarkresults_icore7_10may2013.txt>
  - <https://raw.githubusercontent.com/fast-pack/JavaFastPFOR/HEAD/src/main/java/me/lemire/integercompression/benchmarktools/Benchmark.java>
  - <https://raw.githubusercontent.com/fast-pack/JavaFastPFOR/HEAD/src/main/java/me/lemire/integercompression/FastPFOR.java>
  - <https://raw.githubusercontent.com/fast-pack/JavaFastPFOR/HEAD/src/main/java/me/lemire/integercompression/FastPFOR128.java>
  - <https://raw.githubusercontent.com/fast-pack/JavaFastPFOR/HEAD/src/main/java/me/lemire/integercompression/VariableByte.java>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/lemire/javafastpfor`) · [data/wave9/enrich/raw/github_com_lemire_javafastpfor.json](../../../data/wave9/enrich/raw/github_com_lemire_javafastpfor.json) (enrichment confidence 0.75)

</details>
