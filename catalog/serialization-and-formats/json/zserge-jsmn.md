# jsmn

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🔴 abandoned

> C89 zero-allocation JSON tokenizer; beat nlohmann/json on 8 of 14 benchmark files but trails RapidJSON.

| | |
|---|---|
| **Beats** | nlohmann/json |
| **Claimed result** | The project claim "world fastest JSON parser/tokenizer" is not supported. Paper Table 10 (Skylake i7-6700, GCC 9.1, GB/s): jsmn beats JSON for Modern C++ (nlohmann/json) on 8 of 14 files, e.g. numbers 0.65 vs 0.06, github_events 0.52 vs 0.09, twitter 0.27 vs 0.10, instruments 0.24 vs 0.10. It is slower on the other 6: canada 0.01 vs 0.05, random 0.03 vs 0.07, apache_builds 0.07 vs 0.10, mesh 0.05 vs 0.06, mesh.pretty 0.09 vs 0.11, update-center 0.06 vs 0.07. Derived from page data: geomean \~1.5x faster than nlohmann/json. Against RapidJSON (default 0.38-0.86, insitu 0.41-1.0 GB/s), jsmn is slower on 12 of 14 files. It is faster only on numbers (0.65 vs 0.45) and on github_events against the default mode (0.52 vs 0.46). |
| **Workload** | Tokenizing 14 in-memory JSON files (twitter, canada, citm_catalog, github_events, gsoc-2018, numbers, etc.), single-threaded, best time. jsmn_parse writes into a token array sized to the input, in the default build without JSMN_PARENT_LINKS. RapidJSON and nlohmann/json do full DOM parses. |
| **Metric** | throughput |
| **Hardware** | Intel i7-6700 Skylake, 3.4 GHz, hyper-threading disabled (simdjson VLDB paper) |
| **Compiler and flags** | GCC 9.1, -O3 -march=native, Linux (simdjson VLDB paper; simdjson v0.2.1 Makefile) |
| **Adoption** | 4,194 stars |
| **Last commit** | 2021-10-14 |
| **Links** | [repository](https://github.com/zserge/jsmn) · [benchmark](https://arxiv.org/abs/1902.08318) |

## Verdict

The simdjson paper (Langdale and Lemire, VLDB Journal 2019, Table 10) ran jsmn from a 2018 commit (18e9fe4, default build without parent links, token array sized to the input) against nlohmann/json's full DOM parse on 14 files, single-threaded on an Intel i7-6700 (Skylake) with GCC 9.1 -O3 -march=native. jsmn was faster on 8 files (e.g. numbers 0.65 vs 0.06 GB/s, twitter 0.27 vs 0.10) and slower on 6 (e.g. canada 0.01 vs 0.05), about 1.5x by geomean, while RapidJSON insitu beat it on 13 of 14; a tokenizer against a DOM parser is not like-for-like.

## Use it when

- Microcontrollers (the README says it is tested on AVR and ARM) or builds with no heap and no libc, where one C89 header and a fixed stack array of 16-byte tokens (20 bytes with parent links) is all you can afford.
- Small, known-schema messages such as config files or API responses where you extract a few fields and convert only those. The author's page reports good results on objects of about 4 KB.
- Input that arrives in chunks over UART or a socket: call jsmn_parse again as bytes arrive until it stops returning JSMN_ERROR_PART, without building a tree.
- A C or C++ hot path where nlohmann/json is the bottleneck, the documents are flat or shallow, and most values need no conversion. In the paper jsmn ran numbers.json at 0.65 vs 0.06 GB/s and github_events at 0.52 vs 0.09 GB/s.

## Skip it when

- Untrusted input that must be validated. Even with JSMN_STRICT it accepts missing commas (#217) and stray leading or trailing ':' or ',' (#247). The paper reports that it accepts [0e+]. It does not reject raw control characters in strings or check UTF-8.
- Large nested documents in the default build. canada.json (GeoJSON coordinate arrays) tokenized at 0.01 GB/s, and issue #36 reports a 9 MB nested file taking about 6 s until JSMN_PARENT_LINKS was defined.
- Server or desktop throughput. In the same table RapidJSON insitu, which builds a full DOM, is faster on 13 of 14 files (about 5x geomean). cJSON is faster on 11 of 14, and gason and sajson are faster on all 14.
- Anything that needs lookup by key, DOM mutation, serialization, or decoded numbers and strings. You have to write that layer yourself.
- Documents over 2 GB, because offsets are int and issue #44 shows negative end offsets on overflow. Also projects that need a maintainer: the last commit was 2021-10-14, with 100 open issues and 42 open PRs.

## How it is fast

It does much less work than a DOM parser: one byte-at-a-time pass through a switch-based state machine that records offsets only, with no heap allocation, copying, number or escape decoding, UTF-8 validation or SIMD. A `toksuper` index tracks the enclosing container. In the default build a closing bracket finds its parent by scanning the token array backwards, which is quadratic on containers with many container children. -DJSMN_PARENT_LINKS stores a parent index in each token (4 more bytes), so that walk is bounded by nesting depth.

## Compared with alternatives

Pick jsmn over gason, sajson or yyjson only when you need C89, no heap, no libc and a tiny footprint on a microcontroller: in the paper's Table 10, gason (0.71-1.1 GB/s) and sajson beat jsmn (0.01-0.65 GB/s) on every file, and yyjson is also ANSI C but validates to RFC 8259 and builds a full DOM with a custom allocator. If you want a real DOM without malloc, parsed into a buffer you supply, qajson4c is the closer fit.

## Integration

| | |
|---|---|
| **Form** | header-only: a single jsmn.h. Define JSMN_HEADER in every .c file but one, or JSMN_STATIC to make the symbols static. |
| **Dependencies** | none. It includes only &lt;stddef.h&gt; and calls no libc functions. |
| **Minimum toolchain** | Any C89 (ANSI C) compiler. It is usable from C++ through its extern "C" guard. |
| **Platforms** | Any. It is plain portable C with no SIMD. The README says it is tested on x86/amd64, ARM and AVR, and library.json declares platforms "\*" (PlatformIO). |
| **Thread safety** | Not documented. In the source there is no global or static mutable state: all state lives in the caller's jsmn_parser and token array. Separate parser and token pairs can run concurrently, but one parser must not be shared between threads. |
| **Drop-in for the baseline** | no |

## Gotchas

- JSMN_PARENT_LINKS changes the jsmntok_t layout. Every translation unit must be built with the same setting or you get memory corruption (#70). Without it, large nested inputs are quadratic.
- Non-strict mode is the default. It accepts unquoted primitives, primitives as keys, and even arrays or objects as keys. That input can give a key a child count that breaks key/value pairing (#193), and the bundled jsondump example reads out of bounds on such trees (#125, #249). Bounds-check any token walk.
- `size` counts direct children only (keys, for objects), and there is no next-sibling link, so skipping a nested value means walking its whole subtree. String tokens exclude the quotes but keep escapes raw. Primitives are untyped: you tell them apart by their first byte.
- Parsing stops at the first NUL byte even if len is larger. On JSMN_ERROR_NOMEM, grow the token array while keeping its contents and call jsmn_parse again with the same parser. The simdjson benchmark avoided this by allocating one 16-byte token per input byte.

## Known shortcomings

- Mixed win only: in the simdjson VLDB paper it beats nlohmann/json on 8 of 14 files and loses to RapidJSON on 12 of 14. It is a tokenizer, not a full parser (no number or string decoding).
- The default build is quadratic: without -DJSMN_PARENT_LINKS each closing bracket scans back for its parent (canada.json runs at 0.01 GB/s; a 9 MB file took about 6 s in issue #36). Strict mode still accepts missing commas (#217) and stray ':' or ',' (#247). int offsets overflow above 2 GB. The benchmarked build is a 2018 commit; last release v1.1.0 (2019).

## Caveats and trade-offs

jsmn is only a tokenizer. It does not convert numbers, unescape strings, validate UTF-8 or build a queryable DOM, so a comparison with DOM parsers is not like-for-like. The paper says jsmn accepts invalid JSON such as [0e+]. The paper ran the default build without JSMN_PARENT_LINKS; the author's page says that build is 'terribly slow' on large objects (canada 0.01 GB/s). In the paper jsmn is slower than RapidJSON, sajson, gason and cJSON on most files. A 2012 third-party benchmark by Lev Walkin (lionet.livejournal.com/118853.html, code vlm/vlm-json-test) reports jsmn at 16 MB/s by default and 482 MB/s with the parent-links hack, vs yajl 249 MB/s, json-c 38 MB/s and Jansson 25 MB/s; it states no hardware or compiler. The README itself has no numbers. Last commit 2021-10-14.

Tokenizer only (no value conversion), zero dynamic allocation, tokens are boundary pointers into the source buffer rather than a DOM; C89, no libc dependency, designed for embedded/AVR/ARM targets

## Maintenance

Abandoned: the last commit was 2021-10-14 and the last release v1.1.0 (June 2019), with 100 open issues and 42 open PRs, but it is an MIT-licensed single header with no dependencies that is easy to vendor and patch.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification D, tier now A.
- **Tier reason:** Tier raised from D to A on methodology. The independent, peer-reviewed simdjson paper (VLDB Journal 2019, arXiv 1902.08318) benchmarks jsmn against RapidJSON 1.1.0 and nlohmann/json ('JSON for Modern C++') on 14 files in its Table 10. It states the CPU (Intel i7-6700), compiler (GCC 9.1) and flags (-O3 -march=native). The code is public: simdjson benchmark/parsingcompetition.cpp built as allparsingcompetition with -DALLPARSER (tag v0.2.1), plus the artifact repo simdjson/simdjson_experiments_vldb2019. The win is only against nlohmann/json and only on 8 of 14 files.
- **Verifier notes:** Kept because it is notable (4,194 stars). The tier rises to A because the methodology is complete, but the 'world fastest' claim is refuted and RapidJSON is not beaten. The only in-list baseline that loses is nlohmann/json, on 8 of 14 files. The orchestrator may want to flag this entry as a weak or mixed win. Metadata checks OK: MIT, not archived, not a fork, last commit 2021-10-14, abandoned.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `workload`, `hardware`, `compiler_and_flags`, `compared_against_cpp_std_directly`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/zserge/jsmn>
  - <https://zserge.com/jsmn/>
  - <http://lionet.livejournal.com/118853.html>
  - <https://arxiv.org/abs/1902.08318>
  - <https://arxiv.org/pdf/1902.08318>
  - <https://github.com/simdjson/simdjson/blob/v0.2.1/benchmark/parsingcompetition.cpp>
  - <https://github.com/simdjson/simdjson/blob/v0.2.1/Makefile>
  - <https://github.com/simdjson/simdjson_experiments_vldb2019>
  - <https://github.com/simdjson/simdjson_experiments_vldb2019/blob/master/experiments/comparison/Dockerfile>
  - <https://github.com/simdjson/simdjson_experiments_vldb2019/blob/master/results/skylake/comparison/alltwitter.table>
- **Sources the enricher read:**
  - <https://github.com/zserge/jsmn>
  - <https://github.com/zserge/jsmn/blob/master/jsmn.h>
  - <https://github.com/zserge/jsmn/blob/master/Makefile>
  - <https://github.com/zserge/jsmn/blob/master/library.json>
  - <https://github.com/zserge/jsmn/blob/master/example/simple.c>
  - <https://github.com/zserge/jsmn/commits/master>
  - <https://github.com/zserge/jsmn/releases/tag/v1.1.0>
  - <https://github.com/zserge/jsmn/compare/v1.1.0...master>
  - <https://github.com/zserge/jsmn/commit/18e9fe42cbfe21d65076f5c77ae2be379ad1270f>
  - <https://github.com/zserge/jsmn/issues/36>
  - <https://github.com/zserge/jsmn/issues/44>
  - <https://github.com/zserge/jsmn/issues/70>
  - <https://github.com/zserge/jsmn/issues/110>
  - <https://github.com/zserge/jsmn/issues/111>
  - <https://github.com/zserge/jsmn/issues/125>
  - <https://github.com/zserge/jsmn/issues/138>
  - <https://github.com/zserge/jsmn/issues/154>
  - <https://github.com/zserge/jsmn/issues/167>
  - <https://github.com/zserge/jsmn/issues/193>
  - <https://github.com/zserge/jsmn/issues/217>
  - <https://github.com/zserge/jsmn/issues/239>
  - <https://github.com/zserge/jsmn/issues/247>
  - <https://github.com/zserge/jsmn/issues/249>
  - <https://zserge.com/jsmn/>
  - <https://arxiv.org/pdf/1902.08318>
  - <http://lionet.livejournal.com/118853.html>
  - <https://github.com/simdjson/simdjson/blob/v0.2.1/benchmark/parsingcompetition.cpp>
  - <https://github.com/simdjson/simdjson/blob/v0.2.1/Makefile>
  - <https://github.com/simdjson/simdjson/tree/v0.2.1/dependencies>
  - <https://github.com/ibireme/yyjson>
  - <https://github.com/DeHecht/qajson4c>
  - <https://github.com/vivkin/gason>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/zserge/jsmn`) · [data/wave4/enrich/raw/github_com_zserge_jsmn.json](../../../data/wave4/enrich/raw/github_com_zserge_jsmn.json) (enrichment confidence 0.85)

</details>
