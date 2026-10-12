# minperf (RecSplit implementation)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Minimal perfect hash functions](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Java` · `Apache-2.0` · 🔴 abandoned

> Thomas Mueller's Java RecSplit minimal perfect hash: about 2 bits/key, lookups \~1.1x faster than CHD in one code comment.

| | |
|---|---|
| **Beats** | CHD algorithm, implementation not named in the comment. The README says performance is 'very similar' to the Sux4J CHD and GOV algorithms, so the baseline is most likely Sux4J's Java CHDMinimalPerfectHashFunction. CMPH is not mentioned anywhere. |
| **Claimed result** | Code comment in PerformanceTest.java: 'CHD: 2.25 bits/key, 182 nanoseconds/key'. The comment gives RecSplit with FastLongHash (leafSize=11, averageBucketSize=55) as '1.97 bits/key, 163 nanoseconds/key'. That is about 1.1x faster lookup than CHD at less space (derived from page data: 182/163). The same comment lists 'GOV: 2.32 bits/key, 132 nanoseconds/key', which is faster than minperf. At equal space (leafSize=12, averageBucketSize=26: 2.32 bits/key, 138 ns/key), minperf is still slightly slower than GOV. |
| **Workload** | PerformanceTest.java micro-benchmark: random long keys (default size 100,000; key count behind the commented figures not stated), RecSplit evaluation time using the test-only FastLongHash (rotate&xor). CHD/GOV figures are recorded as comments without their run setup. |
| **Metric** | latency |
| **Adoption** | 173 stars |
| **Last commit** | 2021-02-20 |
| **Links** | [repository](https://github.com/thomasmueller/minperf) · [benchmark](https://github.com/thomasmueller/minperf/blob/master/src/test/java/org/minperf/PerformanceTest.java) |

## Verdict

The only numbers are hand-written comments in PerformanceTest.java: RecSplit with the test-only rotate-and-xor FastLongHash (leafSize 11, averageBucketSize 55) reaches 1.97 bits/key and 163 ns/key, against an unnamed CHD (likely Sux4J's Java CHD, or the repo's own test CHD) at 2.25 bits/key and 182 ns/key (about 1.1x), while GOV at 132 ns/key beats both. No JVM, CPU, compiler flags or key count is recorded (the harness defaults to 100,000 random longs and 100 repeats), and there is no run setup for the baselines.

## Use it when

- Static JVM key sets from about 10^5 up to about 10^9 keys where memory per key matters more than lookup latency, e.g. mapping keys to slots in a bitmap or counter array (the use cases in recsplit.md).
- You want a pure-Java MPHF under 2 bits/key under Apache-2.0 rather than LGPL-2.1 (Sux4J's license), and you can vendor the source.
- Construction time matters on a multi-core box: buckets are built in parallel by default (parallelism = availableProcessors).
- Key sets that barely fit in heap: maxChunkSize builds one range of buckets per pass over the collection, as LargeSetTest does for 10^9 longs with 100M-key chunks.
- Long or String keys (SipHash-based LongHash/StringHash are included), or any type for which you write a seeded UniversalHash&lt;T&gt;.

## Skip it when

- Lookup throughput is the goal. The author says java.util.HashMap get() being about 8x faster than evaluate() is expected (issue #15). In the same benchmark comment, Sux4J GOV is faster at equal space (132 vs 138 ns/key at 2.32 bits/key).
- You must reject keys that are not in the set or store values: no keys or fingerprints are kept, so unknown keys return an arbitrary slot (or 0).
- The key set changes: any insert or delete means a full rebuild.
- You need a supported dependency. There are no releases or Maven Central artifact (the pom is 1.0-SNAPSHOT), the only documentation is the tests (issue #18), the README says 'work in progress', and there have been no code changes since 2019-06.
- More than about 10^9 keys, or C/C++ builds: bit offsets and results are int (a 2^31-bit description cap, about 1B keys at 2 bits/key), and the C code only evaluates functions built in Java.

## How it is fast

It implements RecSplit (Esposito, Mueller Graf, Vigna, arXiv 1910.06416): keys are hashed into buckets, and each bucket is split recursively by brute-force searching for a seed that divides it into the fanout given by precomputed split rules, down to leaves of at most leafSize keys, where a seed giving a bijection is searched. The seeds are stored Golomb-Rice coded, with per-bucket key counts and bit offsets in Elias-Fano monotone lists with select. A lookup is one universal hash, two Elias-Fano reads and a walk down the Rice-coded tree that decodes and skips sibling subtrees; it uses a cheap SplitMix-style supplemental mixer plus Lemire multiply-shift range reduction and calls the full hash only once per 2^18 seeds. Buckets are independent, so construction runs in parallel on a ForkJoinPool, and buckets over 8x the average fall back to a BDZ function (\~3.66 bits/key); the main gain over CHD is space (the README claims under 1.58 bits/key is possible) rather than lookup speed.

## Compared with alternatives

Pick minperf over Sux4J GOV only if you need a permissive-licensed (Apache-2.0 vs LGPL-2.1) pure-Java MPHF below 2 bits/key and accept unmaintained code; Sux4J is still active (pushed 2026-05) and wins on lookup time in minperf's own comment. For C++, the same algorithm is maintained in Sux's RecSplit, and PTHash or PtrHash give much faster lookups (37-45 ns/key) at about 3 bits/key.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none at runtime for the core (JDK only); the pom also declares jmh-core 1.4 at compile scope and junit 4.13.1 for tests |
| **Minimum toolchain** | Java 8 (pom source/target 1.8); C evaluator built with gcc -O3 via its Makefile |
| **Platforms** | any JVM; the C evaluator loads big-endian files written by the Java builder |
| **Thread safety** | not documented. generate() is internally parallel: each call creates a new ForkJoinPool, which is never shut down. After construction, evaluate() only does positional reads on the shared long[], so concurrent lookups look safe by inspection, but no doc or test confirms it. |
| **Drop-in for the baseline** | no |

## Gotchas

- The serialized function does not record its parameters. buildEvaluator must get the same UniversalHash, leafSize, averageBucketSize and eliasFanoMonotoneLists used for generation, and a mismatch is not detected.
- The builder accepts leafSize 1-25, but Settings only has split rules for 7-18: sizes 2-6 throw 'No split rules', and 19+ index past the rules table. Split rules are also cached only for set sizes below 10,240 (getSplit throws above that), so averageBucketSize values near or above that fail even though the builder allows up to 65,536.
- Keys must be unique. A duplicate can never be separated, so the leaf seed search loops forever instead of failing. The 163 ns/key figure uses FastLongHash, which the source says is 'not recommended to use in the real world'.
- MAVEN.md and runjmh.sh point at org.minperf.bloom.\* JMH benchmarks that are no longer in the tree. The org.minperf.hem package (a 10^12-key experiment with its own Builder and FastEvaluator, see issue #12) is a separate code path, not the RecSplitBuilder API.

## Caveats and trade-offs

The CHD/GOV figures are hand-written code comments with no JVM, CPU, key count, or harness stated. The CHD implementation is not named; the README points to Sux4J's Java CHD, not CMPH. minperf's own 163 ns/key figure uses FastLongHash, which the source calls 'not recommended to use in the real world'. The same comment shows GOV (132 ns/key) faster than minperf. The repo also has its own Java CHD reimplementation in src/test/java/org/minperf/chd/CHD.java, a possible alternative source of the CHD figure. The README calls the library 'work in progress'.

Numbers are hand-written code comments from a prior run rather than logged/automated benchmark output; no hardware, JVM version, or full dataset description is stated; the project's README says a paper was planned but the repo has been inactive since 2021 and no paper was ever added.

## Maintenance

Abandoned (the last code change was 2019-06, the last commit a 2021-02 dependabot bump, and there are no releases or Maven artifact), but it is Apache-2.0 and the core builder/evaluator is a few dozen JDK-only classes, so you can vendor it if you pin and test it yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification C, tier now C.
- **Tier reason:** The only numbers are code comments in PerformanceTest.java: first-party figures with no JVM version, CPU, or run setup. Nothing links them to a published report or paper. The RecSplit ALENEX paper times the C++ sux implementation, not minperf.
- **Verifier notes:** Downgraded because the claim is overstated. The baseline is misattributed to CMPH. The win uses a toy hash. The win covers only CHD; GOV in the same comment beats minperf. Tier stays C. baseline_in_list is left unchanged because list membership of Sux4J's CHD could not be checked. Apache-2.0, 173 stars and last commit 2021-02-20 (abandoned) verified via gh.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/thomasmueller/minperf/blob/master/src/test/java/org/minperf/PerformanceTest.java>
  - <https://github.com/thomasmueller/minperf>
  - <https://github.com/thomasmueller/minperf/blob/master/pom.xml>
  - <https://github.com/thomasmueller/minperf/blob/master/LICENSE>
  - <https://github.com/thomasmueller/minperf/blob/master/src/test/java/org/minperf/chd/CHDTest.java>
  - <https://github.com/thomasmueller/minperf/blob/master/src/test/java/org/minperf/chd/CHD.java>
  - <https://github.com/thomasmueller/minperf/blob/master/src/test/java/org/minperf/Paper.java>
  - <https://github.com/vigna/Sux4J/blob/master/src/it/unimi/dsi/sux4j/mph/CHDMinimalPerfectHashFunction.java>
  - <https://arxiv.org/pdf/1910.06416>
- **Sources the enricher read:**
  - <https://github.com/thomasmueller/minperf>
  - <https://github.com/thomasmueller/minperf/blob/master/README.md>
  - <https://github.com/thomasmueller/minperf/blob/master/src/test/java/org/minperf/PerformanceTest.java>
  - <https://github.com/thomasmueller/minperf/blob/master/pom.xml>
  - <https://github.com/thomasmueller/minperf/blob/master/MAVEN.md>
  - <https://github.com/thomasmueller/minperf/blob/master/runjmh.sh>
  - <https://github.com/thomasmueller/minperf/blob/master/src/main/java/org/minperf/RecSplitBuilder.java>
  - <https://github.com/thomasmueller/minperf/blob/master/src/main/java/org/minperf/RecSplitEvaluator.java>
  - <https://github.com/thomasmueller/minperf/blob/master/src/main/java/org/minperf/Settings.java>
  - <https://github.com/thomasmueller/minperf/blob/master/src/main/java/org/minperf/BitBuffer.java>
  - <https://github.com/thomasmueller/minperf/blob/master/src/main/java/org/minperf/universal/UniversalHash.java>
  - <https://github.com/thomasmueller/minperf/blob/master/src/main/java/org/minperf/universal/LongHash.java>
  - <https://github.com/thomasmueller/minperf/blob/master/src/main/java/org/minperf/universal/StringHash.java>
  - <https://github.com/thomasmueller/minperf/blob/master/src/main/java/org/minperf/generator/Generator.java>
  - <https://github.com/thomasmueller/minperf/blob/master/src/main/java/org/minperf/generator/ConcurrencyTool.java>
  - <https://github.com/thomasmueller/minperf/blob/master/src/main/java/org/minperf/monotoneList/MonotoneList.java>
  - <https://github.com/thomasmueller/minperf/blob/master/src/main/java/org/minperf/monotoneList/EliasFanoMonotoneList.java>
  - <https://github.com/thomasmueller/minperf/blob/master/src/main/java/org/minperf/bdz/BDZ.java>
  - <https://github.com/thomasmueller/minperf/blob/master/src/main/java/org/minperf/hash/HashPerformanceTest.java>
  - <https://github.com/thomasmueller/minperf/blob/master/src/main/java/org/minperf/hem/HemGenerator.java>
  - <https://github.com/thomasmueller/minperf/blob/master/src/main/java/org/minperf/hem/recsplit/FastEvaluator.java>
  - <https://github.com/thomasmueller/minperf/blob/master/src/main/c/rec-split.c>
  - <https://github.com/thomasmueller/minperf/blob/master/src/main/c/Makefile>
  - <https://github.com/thomasmueller/minperf/blob/master/src/test/java/org/minperf/simple/recsplit.md>
  - <https://github.com/thomasmueller/minperf/blob/master/src/test/java/org/minperf/chd/CHDTest.java>
  - <https://github.com/thomasmueller/minperf/blob/master/src/test/java/org/minperf/chd/CHD.java>
  - <https://github.com/thomasmueller/minperf/blob/master/src/test/java/org/minperf/Paper.java>
  - <https://github.com/thomasmueller/minperf/blob/master/src/test/java/org/minperf/RandomizedTest.java>
  - <https://github.com/thomasmueller/minperf/blob/master/src/test/java/org/minperf/LargeSetTest.java>
  - <https://github.com/thomasmueller/minperf/issues/12>
  - <https://github.com/thomasmueller/minperf/issues/13>
  - <https://github.com/thomasmueller/minperf/issues/15>
  - <https://github.com/thomasmueller/minperf/issues/17>
  - <https://github.com/thomasmueller/minperf/issues/18>
  - <https://github.com/thomasmueller/minperf/pulls?q=is%3Apr>
  - <https://github.com/thomasmueller/minperf/commits/master>
  - <https://github.com/vigna/Sux4J>
  - <https://github.com/vigna/sux>
  - <https://arxiv.org/abs/1910.06416>
  - <https://repo1.maven.org/maven2/thomasmueller/>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/thomasmueller/minperf`) · [data/wave1-phf/enrich/raw/github_com_thomasmueller_minperf.json](../../../data/wave1-phf/enrich/raw/github_com_thomasmueller_minperf.json) (enrichment confidence 0.7)

</details>
