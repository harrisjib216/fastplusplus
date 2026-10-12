# Sux4J (GOV / GOV3Function minimal perfect hash)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Minimal perfect hash functions](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Java` · `LGPL-2.1-or-later OR Apache-2.0` · 🟢 active

> Java GOV minimal perfect hash (F3 linear systems, \~2.2 bits/key) with C lookup; about 2x faster lookups than CMPH's CHD.

| | |
|---|---|
| **Beats** | CMPH (CHD algorithm) |
| **Claimed result** | PTHash paper Table 5 (mirrored in mphf_benchmark README), n=10^9 random 64-bit keys: GOV 175 ns/key lookup, 2.23 bits/key, 875 s construction vs CHD (CMPH) 419/417/416 ns/key at 2.17/2.07/2.01 bits/key (lambda=4/5/6) -&gt; GOV lookup about 2.4x faster than CHD (derived from page data: 419/175, 416/175). Same table at n=10^8: GOV 110 ns/key vs CHD 204/204/197 ns/key -&gt; about 1.8x (derived from page data). Corroborated by RecSplit paper (ALENEX 2020, arXiv 1910.06416) Table 2, 10^9 keys: GOV 210 ns/key vs CHD 447/444 ns/key (lambda=5/6), about 2.1x (derived from page data). |
| **Workload** | 1 billion random 64-bit integer keys; lookup (evaluation) time and space (bits/key) for Sux4J's GOV minimal perfect hash function compared against CMPH's CHD (λ=4,5,6), EMPHF, BBHash, RecSplit and PTHash, as reproduced in the PTHash SIGIR'21 paper's Table 5 and mirrored in the roberto-trani/mphf_benchmark README. |
| **Metric** | latency |
| **Hardware** | Intel Core i9-9900K @ 3.60GHz, 64GB DDR3 RAM @2.66GHz, Linux 5 (64-bit) |
| **Compiler and flags** | PTHash paper: gcc 9.2.1 with -O3 -march=native (mphf_benchmark CMakeLists Release also sets -O3 -march=native). Both papers state all code is C/C++ except GOV construction, which is Java-only, so GOV lookups were presumably timed with Sux4J's C lookup code (c/mph.c). The GOV lookup harness and JVM version are not stated in the PTHash paper. The RecSplit paper states gcc 8.1.1 and Java 12. |
| **Adoption** | 176 stars |
| **Last commit** | 2026-05-08 |
| **Links** | [repository](https://github.com/vigna/Sux4J) · [benchmark](https://github.com/roberto-trani/mphf_benchmark) |

## Verdict

PTHash paper Table 5 (SIGIR'21, mirrored in mphf_benchmark): 10^9 uniformly random 64-bit keys on one core of an i9-9900K (gcc 9.2.1 -O3 -march=native). GOV averaged 175 ns/key over every input key at 2.23 bits/key, vs 416-419 ns/key for CMPH's CHD (lambda=4-6, 2.01-2.17 bits/key), about 2.4x; at 10^8 keys it was 110 vs 197-204 ns/key, about 1.8x. GOV was built in Java and neither paper names its lookup harness (presumably Sux4J's C code). The RecSplit paper (i7-7770, gcc 8.1.1, Java 12, 128-bit random keys) independently measured 210 vs 444-447 ns/key at 10^9 keys.

## Use it when

- JVM services that need a static map from keys to dense IDs (0..n-1) for 10^7 to 10^9+ strings, byte arrays or longs at about 2.2 bits/key, e.g. to index a term dictionary or an ID column into flat arrays.
- Key sets larger than RAM. BucketedHashStore bucket-sorts 128-bit signatures into disk segments and needs under 0.75 bits/key of main memory while sorting. Each \~1,500-key bucket is then solved on its own.
- Building offline in Java and querying from C/C++: dump() the function, then call mph_get_uint64_t, mph_get_byte_array or mph_get_uint128_t from c/mph.c.
- Replacing CMPH's CHD when 0.06-0.22 extra bits/key is acceptable. In return you get about 2x faster lookups and 2.3-27x faster single-core construction (875 s vs 1,972-23,746 s at 10^9 keys).
- Cases that also need a membership test: signed(w) stores a w-bit signature per key, so a non-member returns -1 except with probability 2^-w.

## Skip it when

- Lookup speed is the priority in native code. In the same Table 5 (10^9 keys), PTHash answers in 37-64 ns/key and BBHash gamma=2 in 143 ns/key, vs 175 ns/key for GOV.
- Space is the priority. CHD lambda=6 (2.01 bits/key) and RecSplit l=8, b=100 (1.80 bits/key at 204 ns/key, 936 s to build) are both smaller than GOV's 2.23 bits/key.
- Pure C/C++ or Rust projects that must build the function at runtime. Construction exists only in Java, so you need a JVM plus a dump/load step.
- Dynamic sets. The structure is static, so any insert or delete means a full rebuild.
- Small, cache-resident sets. At 10^6 keys (RecSplit paper Table 1), GOV's 58 ns/key trails BBHash gamma=1 (33 ns) and RecSplit l=5, b=5 (47 ns), and its lead over CHD (91-92 ns) shrinks to about 1.6x.

## How it is fast

Each key is hashed once with SpookyHash into a 128-bit signature and assigned to a bucket of about 1,500 keys. Each bucket is a random 3-regular linear system over F3 (Genuzio-Ottaviano-Vigna, SEA 2016), with about 10% more variables than equations, solved by hypergraph peeling plus lazy Gaussian elimination. A lookup reads the bucket's offset, then three 2-bit values whose sum mod 3 picks the key's vertex, then ranks that vertex with a broadword popcount of nonzero 2-bit pairs. After the offset read, all memory access stays inside one bucket's \~1,650 cells (\~52 words), and construction scales because signatures are bucket-sorted on disk and buckets are solved in parallel.

## Compared with alternatives

Pick GOV when you are on the JVM and want a Maven-packaged MPHF that scales past RAM, with optional signatures. minperf, the other Java sibling, claims 'very similar' performance but calls itself work in progress and was last pushed in 2021. In native C/C++, Table 5 shows PTHash at 37-64 ns/key, and RecSplit (Sux) at 1.80 bits/key with similar lookup (204 ns) and build time (936 s), so GOV mainly makes sense there if Sux4J already builds your functions.

## Integration

| | |
|---|---|
| **Form** | module: Maven Central jar it.unimi.dsi:sux4j, latest release 5.4.1 (March 2023). The optional C lookup is a source-drop: c/mph.c, mph.h, spooky.c, spooky.h. |
| **Dependencies** | Java: fastutil, dsiutils, slf4j-api (logback at runtime), JSAP, commons-math3, commons-collections4, commons-lang3. C lookup: only libc/libm. |
| **Minimum toolchain** | Java 9+ (CHANGES 5.2.3; the POM targets 1.9), built with Ant + Ivy. The C lookup needs GCC/Clang extensions (__uint128_t, __builtin_popcountll, __builtin_clzll); comp.sh uses gcc -O3 -march=native. |
| **Platforms** | Any JVM. The C lookup needs a 64-bit GCC/Clang target with __uint128_t. dump() writes native byte order, so load the file on a machine with the same endianness. The optional USE_MMAP path uses Linux MAP_HUGETLB. |
| **Thread safety** | Not documented for lookups. getLong() allocates its own scratch arrays and only reads fields set at construction, and the reporter of issue #2 shares one instance across threads. Construction is internally multithreaded: min(4, cores) threads by default, overridable with the system property it.unimi.dsi.sux4j.mph.threads. |
| **Drop-in for the baseline** | no |

## Gotchas

- A key outside the build set gets an arbitrary index in [0, n), not an error, unless you build with signed(w). containsKey() always returns true.
- You cannot choose the indices. Values stored in a BucketedHashStore passed to the builder are ignored (issue #3). For key-to-value static functions use GOV3Function or GOV4Function, which are not MPHFs.
- The C lookup code does no validation. Nothing checks that the dump matches the key type or transformation strategy: the uint64_t tests expect RAW_LONG, the byte_array tests RAW_BYTE_ARRAY. Also, the c/ sources are LGPL-3.0-or-later, not the Java code's LGPL-2.1+/Apache-2.0.
- Java getLong() still allocates a long[2] and an int[3] per call; a user flagged the GC pressure in issue #2. Construction logs heavily unless you configure the SLF4J backend (issue #11). It needs a temp directory for disk segments and throws IllegalArgumentException if duplicates persist after several rebuilds.

## Caveats and trade-offs

The GOV row is not produced by the mphf_benchmark harness. Its README says GOV is excluded from the reproducible commands because GOV is Java-based. GOV construction runs in Java. GOV lookup is presumably timed via Sux4J's C lookup code, c/mph.c with c/test_mph_uint64_t.c, which the papers do not name explicitly. The measured MPHF class is GOVMinimalPerfectHashFunction. GOV3Function is a static function, not an MPHF. Java code is dual-licensed LGPL-2.1-or-later OR Apache-2.0 (GitHub reports LGPL-2.1). The c/ lookup sources carry LGPL-3.0-or-later headers. GOV uses slightly more space than CHD (2.23 vs 2.01-2.17 bits/key).

GOV uses more space than CHD (2.23 vs 2.01-2.17 bits/key) despite being \~2.4x faster to look up; GOV construction (875s for 1B keys) is much slower than BBHash (100-253s) though far faster than CHD (1972-23746s); JVM overhead vs native C/C++ libraries is not isolated in these numbers.

## Maintenance

Still receiving commits (C benchmark harnesses in May 2026), but the last Maven Central release is 5.4.1 from March 2023. The jar is the practical way in, and the C lookup files are small enough to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed PTHash paper (SIGIR'21, arXiv 2104.10402, Table 5) and its mirror in the roberto-trani/mphf_benchmark README show the GOV row (175 ns/key, 2.23 bits/key, 875 s) beating CMPH's CHD (416-419 ns/key) at n=10^9 on an i9-9900K, gcc 9.2.1 -O3 -march=native. The RecSplit ALENEX'20 paper corroborates this. Not A: the public harness does not include GOV, and neither paper names the harness or JVM used for GOV.
- **Verifier notes:** Numbers match the page exactly and belong to the GOV row. CHD in the harness is bonitao/cmph (the RecSplit paper cites sourceforge cmph), so the CMPH baseline is correct. Stars (176), last commit (2026-05-08), active status and non-fork status verified via gh. Consider renaming the entry to 'GOVMinimalPerfectHashFunction' rather than 'GOV3Function'.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `license`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/roberto-trani/mphf_benchmark>
  - <https://github.com/roberto-trani/mphf_benchmark/blob/main/CMakeLists.txt>
  - <https://arxiv.org/abs/2104.10402>
  - <https://arxiv.org/pdf/2104.10402v2>
  - <https://arxiv.org/pdf/1910.06416>
  - <https://github.com/vigna/Sux4J>
  - <https://github.com/vigna/Sux4J/tree/master/c>
  - <https://github.com/vigna/Sux4J/blob/master/c/README.md>
  - <https://github.com/vigna/Sux4J/blob/master/c/test_mph_uint64_t.c>
  - <https://github.com/vigna/Sux4J/blob/master/c/comp.sh>
  - <https://github.com/vigna/Sux4J/blob/master/c/mph.c>
  - <https://github.com/vigna/Sux4J/blob/master/src/it/unimi/dsi/sux4j/mph/GOVMinimalPerfectHashFunction.java>
- **Sources the enricher read:**
  - <https://github.com/vigna/Sux4J>
  - <https://github.com/vigna/Sux4J/blob/master/src/it/unimi/dsi/sux4j/mph/GOVMinimalPerfectHashFunction.java>
  - <https://github.com/vigna/Sux4J/blob/master/src/it/unimi/dsi/sux4j/mph/solve/Linear3SystemSolver.java>
  - <https://github.com/vigna/Sux4J/blob/master/src/it/unimi/dsi/sux4j/mph/package-info.java>
  - <https://github.com/vigna/Sux4J/blob/master/src/it/unimi/dsi/sux4j/mph/GOV3Function.java>
  - <https://github.com/vigna/Sux4J/blob/master/src/it/unimi/dsi/sux4j/mph/AbstractHashFunction.java>
  - <https://github.com/vigna/Sux4J/blob/master/src/it/unimi/dsi/sux4j/io/BucketedHashStore.java>
  - <https://github.com/vigna/Sux4J/blob/master/c/README.md>
  - <https://github.com/vigna/Sux4J/blob/master/c/comp.sh>
  - <https://github.com/vigna/Sux4J/blob/master/c/mph.h>
  - <https://github.com/vigna/Sux4J/blob/master/c/mph.c>
  - <https://github.com/vigna/Sux4J/blob/master/c/test_mph_uint64_t.c>
  - <https://github.com/vigna/Sux4J/blob/master/c/spooky.c>
  - <https://github.com/vigna/Sux4J/blob/master/ivy.xml>
  - <https://github.com/vigna/Sux4J/blob/master/build.properties>
  - <https://github.com/vigna/Sux4J/blob/master/pom-model.xml>
  - <https://github.com/vigna/Sux4J/blob/master/CHANGES>
  - <https://github.com/vigna/Sux4J/commits/master>
  - <https://github.com/vigna/Sux4J/tags>
  - <https://github.com/vigna/Sux4J/issues?q=is%3Aissue>
  - <https://github.com/vigna/Sux4J/issues/2>
  - <https://github.com/vigna/Sux4J/issues/3>
  - <https://github.com/vigna/Sux4J/issues/9>
  - <https://github.com/vigna/Sux4J/issues/11>
  - <https://github.com/roberto-trani/mphf_benchmark>
  - <https://arxiv.org/abs/1603.04330>
  - <https://arxiv.org/abs/2104.10402>
  - <https://arxiv.org/pdf/2104.10402v2>
  - <https://arxiv.org/pdf/1910.06416>
  - <https://search.maven.org/solrsearch/select?q=g:it.unimi.dsi+AND+a:sux4j>
  - <https://repo1.maven.org/maven2/it/unimi/dsi/sux4j/maven-metadata.xml>
  - <https://github.com/thomasmueller/minperf>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/vigna/sux4j`) · [data/wave1-phf/enrich/raw/github_com_vigna_sux4j.json](../../../data/wave1-phf/enrich/raw/github_com_vigna_sux4j.json) (enrichment confidence 0.8)

</details>
