# JSONSki

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🟡 stale

> Streaming JSONPath engine that skips irrelevant JSON with bit-parallel fast-forwarding; \~4.8x faster than simdjson parse+query (ASPLOS'22).

| | |
|---|---|
| **Beats** | RapidJSON, simdjson |
| **Claimed result** | README (single large record): "JSONSki runs over 12x faster over ... JPStream ... JSONSki is about 3x faster than Pison, and more than 4x faster than simdjson". ASPLOS'22 paper section 5.2: 12.3x over JPStream, 4.8x over simdjson, 3.1x over Pison on average (single large record, all single-threaded). README Fig.1 mean times: RapidJSON 5.07s, JPStream 4.90s, simdjson 1.92s, Pison 1.24s, JSONSki 0.40s, about 12.7x vs RapidJSON (derived from page data). README Fig.2 small records mean: RapidJSON 4.19s, simdjson 1.70s, JSONSki 0.41s. |
| **Workload** | JSONPath query evaluation over \~1GB single-record and small-record JSON datasets (Twitter, BestBuy, Google Maps Directions, UK NSPL, Walmart, Wikipedia) across 12 distinct JSONPath queries, measuring end-to-end execution time including any preprocessing/parsing |
| **Metric** | latency |
| **Hardware** | Two Intel Xeon E5-2620 v4 @2.1GHz (16 cores), 128GB RAM, CentOS 7 (paper); requires 64-bit ALU, 256-bit SIMD (AVX2) and pclmulqdq |
| **Compiler and flags** | G++ 7.4.0 with -O3 on CentOS 7 (ASPLOS'22 paper section 5.1); repo makefile builds with g++ -O3 -std=c++11 -mavx -mavx2 -msse -msse2 -msse4 -msse4.2 -mpclmul; README lists g++ 7.4.0 or higher as prerequisite |
| **Adoption** | 33 stars; ASPLOS 2022 Best Paper Award winner |
| **Last commit** | 2024-10-10 |
| **Links** | [repository](https://github.com/AutomataLab/JSONSki) · [benchmark](https://github.com/AutomataLab/JSONSki#performance-results) |

## Verdict

In the ASPLOS'22 paper, measured on 2x Xeon E5-2620 v4 with G++ 7.4.0 -O3 on CentOS 7, single-threaded JSONSki averaged 0.40 s over 12 JSONPath queries on six \~1 GB single-record datasets. The baselines, timed end to end including parse or index build, were simdjson at 1.92 s (4.8x), Pison at 1.24 s (3.1x) and RapidJSON at 5.07 s (\~12.7x, derived); JPStream was 12.3x slower. On small-record inputs JSONSki averaged 0.41 s, against 1.70 s for simdjson and 4.19 s for RapidJSON. Baseline versions are unstated (2020-era), the simdjson run used its parse-tree path, and the repo has no baseline harness, so the numbers cannot be reproduced from source.

## Use it when

- Pulling a few fields with a simple path (such as \$[\*].entities.urls[\*].url) out of very large single JSON documents, 100 MB to tens of GB, where most of the bytes are irrelevant to the query
- Memory-bound jobs: the paper measured about 1 GB total for a 1 GB input, against 2-3 GB for simdjson, RapidJSON and Pison. It scaled to a 72 GB single record, where RapidJSON and Pison ran out of memory and simdjson hit its 4 GB document limit
- Newline-delimited JSON with records under about 1 MB each, one query per record, parallelized by giving each thread its own QueryProcessor (the paper's 16-thread small-record run scaled 10.3x)
- Trusted, machine-generated, compact JSON (your own logs or data-lake dumps) on x86-64 Linux servers with AVX2
- A research or prototype base when you want the fast-forward primitives (goOverObj, goToAryEnd, etc.) for custom one-pass analytics and are willing to edit the source

## Skip it when

- Untrusted or possibly malformed input. Nothing is validated, and several fixed-size buffers are filled with unchecked memcpy: 10,000 bytes per output match (mText) and 1,000 bytes per key (mKey). A large matched value or a long key corrupts the heap or object memory
- You need more than the supported JSONPath subset. Recursive descent '..', filters, unions, negative indices and quoted/bracketed keys are unsupported, and there is one path per QueryProcessor. The parser gives no error for unsupported syntax and just builds a different automaton. The code also has no special case for an object-member '.\*' wildcard (keys are memcmp'd literally), even though the README lists '\*'
- You need typed values, a DOM, mutation or serialization. The output is raw JSON text joined with ';', so values that contain ';' are ambiguous and every value still needs a real parser
- ARM, Apple Silicon, or x86 without AVX2 and PCLMULQDQ. The code calls _mm256 and _mm_clmulepi64 intrinsics unconditionally and has no scalar fallback
- Many-core processing of one huge record. JSONSki runs a single record on one thread, and the paper reports 16-thread speculative Pison was 48% faster on single large records

## How it is fast

The query becomes a small automaton that drives recursive-descent streaming. When the automaton is in an unmatched state, or the value's type cannot match, the engine jumps over whole objects, arrays or primitives without tokenizing them. The jumps use 'structural intervals': AVX2 compares build 64-bit bitmaps of one metacharacter per 64-byte word, a PCLMULQDQ prefix-XOR masks out bytes inside strings (the simdjson/Mison quote-and-escape technique), and interval bitmaps between successive '{' or '[' are counted with popcnt/lzcnt/ctz to find where the matching '}' or ']' falls. The paper reports that more than 95% of input bytes were fast-forwarded on all 12 queries. Bitmaps are built lazily per word, so no global index is kept.

## Compared with alternatives

Over simdjson: pick JSONSki only for simple-path extraction from GB-scale trusted documents where memory or the 4 GB document limit matters. The paper's 4.8x was measured against simdjson building a parse tree, and current simdjson On-Demand has at_path() and for_each_at_path_with_wildcard(), plus validation, typed values, ARM support and active maintenance, so try it first. Over Pison (same lab): JSONSki is 3.1x faster single-threaded and needs no index memory, but Pison's speculative multi-threading wins on one huge record when you have 16 cores. Mison is paper-only.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (C++ standard library plus x86 intrinsics headers; -lpthread is linked but no threads are used) |
| **Minimum toolchain** | C++11. The README requires g++ 7.4.0+, and the makefile compiles with -O3 -std=c++11 -mavx -mavx2 -msse4.2 -mpclmul. CircleCI builds with gcc 10. No CMake, library target or install rule: the makefile only builds the four examples, so you add the three src/\*.cpp files to your own build |
| **Platforms** | x86-64 only (AVX2 and PCLMULQDQ required). The README says Linux. The badge says linux-macos and a 2022 PR added macOS include guards, but the CI job named 'build-for-macos' actually runs in a Linux gcc10 Docker image |
| **Thread safety** | Not documented. QueryProcessor keeps per-run mutable state (bitmaps, automaton stack, output buffer), so use one instance per thread. Records loaded by loadRecords share one read-only text buffer |
| **Drop-in for the baseline** | no |

## Gotchas

- Truncated or unbalanced JSON can hang. goOverObj, goOverAry, goToObjEnd and goToAryEnd wrap their word loop in while(true), so once word_id reaches the end of the input without finding the closing bracket they spin forever. Errors go to stdout ('pop out exception', 'additional [') and are not returned, and RecordSet::operator[] calls exit(0) on an out-of-range index
- The loaders have memory bugs. loadSingleRecord writes its NUL one byte past the allocation when the file size is a multiple of 64. loadRecords allocates str.size() bytes and then strcpy's the terminator (one byte over), uses a 1 MB stack line buffer, silently splits lines longer than about 1 MB, and can overflow that buffer while padding lines near 1 MB. The QueryProcessor destructor free()s a buffer allocated with new[]
- The text scanning is fragile. getElementType and getAttributeType skip only spaces, and tabs are never skipped anywhere, so a tab or newline after ':' can make an object be read as a primitive; feed minified JSON. Keys are compared as raw bytes, with no \uXXXX decoding and no escaped-quote handling in the key scanner
- The headers are unhygienic. They use 'using namespace std' at global scope and unprefixed macros (OBJECT, ARRAY, KEY, NONE, SUCCESS, INVALID, and MAX_KEY_LENGTH defined twice, as 100 and 1000). The fast-forward functions the README documents are private members of QueryProcessor. getOutputMatchesNum() accumulates across runQuery calls because init() never resets mNumMatches

## Known shortcomings

- Unsafe on untrusted input: no validation, values and keys are copied into fixed 10,000- and 1,000-byte buffers without length checks, loaders write one byte past their allocations, and truncated or unbalanced JSON can loop forever. Object-member '.\*' wildcards are not implemented despite the README; x86-64 AVX2+PCLMULQDQ only. The 4.8x over simdjson is against simdjson's DOM path, not its On-Demand at_path API. Source unchanged since 2023-09.

## Caveats and trade-offs

Baselines include parse/index time and use 2020-era simdjson/RapidJSON with versions unstated; no baseline harness is published in the repo, so the comparison is not reproducible from source. Paper notes single-threaded JSONSki is 48% slower than 16-thread speculative Pison on single large records. Only a JSONPath subset is supported (no '..', no filters); x86 AVX2+pclmul, Linux only; repo stale since 2024-10-10.

Supports only a subset of JSONPath (no filter expressions, recursive descent '..', or multi-index arrays); requires Linux plus specific SIMD/pclmulqdq CPU support; streaming API is lower-level than a DOM library

## Maintenance

Stale: the source was last changed 2023-09-20 and later commits touch only README and LICENSE; there are no releases, no tests beyond running example1 in CI, and 3 closed PRs with no open issues. It is MIT-licensed and only 8 source files, so vendoring is easy, but plan to fix the buffer and termination bugs yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed ASPLOS'22 paper (read in full; section 5) shows JSONSki beating simdjson (4.8x) and RapidJSON on end-to-end JSONPath time, and states G++ 7.4.0, -O3, 2x Xeon E5-2620 v4. It stays B, not A, because the repo holds only src/ and example/ with no baseline (RapidJSON/simdjson/Pison) harness, there is no artifact appendix, and baseline versions are unstated.
- **Verifier notes:** README numbers match the paper's text (12.3x/4.8x/3.1x) and the README figure's mean bars. The dl.acm.org PDF returned 403 to curl and WebFetch, so the paper was read from the Wayback Machine copy of the same gold-OA ACM PDF. The Best Paper claim comes from the README and the author's page; the ASPLOS site was not checked.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/AutomataLab/JSONSki>
  - <https://github.com/AutomataLab/JSONSki#performance-results>
  - <https://github.com/AutomataLab/JSONSki/blob/master/doc/compare_seq_large.png>
  - <https://github.com/AutomataLab/JSONSki/blob/master/doc/compare_seq_small.png>
  - <https://github.com/AutomataLab/JSONSki/blob/master/makefile>
  - <https://github.com/AutomataLab/JSONSki/blob/master/LICENSE>
  - <https://dl.acm.org/doi/pdf/10.1145/3503222.3507719>
  - <https://web.archive.org/web/20240414071233id_/https://dl.acm.org/doi/pdf/10.1145/3503222.3507719>
  - <https://api.semanticscholar.org/graph/v1/paper/DOI:10.1145/3503222.3507719?fields=title,openAccessPdf,externalIds,url>
  - <https://www.cs.ucr.edu/~zhijia/>
  - <https://www.cs.ucr.edu/~zhijia/html/publications.html>
  - <http://www.cs.ucr.edu/~ljian006/>
- **Sources the enricher read:**
  - <https://github.com/AutomataLab/JSONSki>
  - <https://github.com/AutomataLab/JSONSki#performance-results>
  - <https://github.com/AutomataLab/JSONSki/blob/master/makefile>
  - <https://github.com/AutomataLab/JSONSki/blob/master/.circleci/config.yml>
  - <https://github.com/AutomataLab/JSONSki/blob/master/src/lib/QueryProcessor.h>
  - <https://github.com/AutomataLab/JSONSki/blob/master/src/lib/QueryAutomaton.h>
  - <https://github.com/AutomataLab/JSONSki/blob/master/src/lib/RecordLoader.h>
  - <https://github.com/AutomataLab/JSONSki/blob/master/src/lib/Records.h>
  - <https://github.com/AutomataLab/JSONSki/blob/master/src/lib/JSONPathParser.h>
  - <https://github.com/AutomataLab/JSONSki/blob/master/src/QueryProcessor.cpp>
  - <https://github.com/AutomataLab/JSONSki/blob/master/src/RecordLoader.cpp>
  - <https://github.com/AutomataLab/JSONSki/blob/master/src/JSONPathParser.cpp>
  - <https://github.com/AutomataLab/JSONSki/blob/master/example/example1.cpp>
  - <https://github.com/AutomataLab/JSONSki/blob/master/example/example4.cpp>
  - <https://github.com/AutomataLab/JSONSki/issues?q=is%3Aissue%20OR%20is%3Apr>
  - <https://github.com/AutomataLab/JSONSki/commits/master>
  - <https://github.com/AutomataLab/JSONSki/commits/master/src>
  - <https://github.com/AutomataLab/JSONSki_nodejs>
  - <https://web.archive.org/web/20240414071233id_/https://dl.acm.org/doi/pdf/10.1145/3503222.3507719>
  - <https://github.com/simdjson/simdjson/blob/master/doc/basics.md>
  - <https://github.com/AutomataLab/Pison>
  - <https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=JSONSki>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/automatalab/jsonski`) · [data/wave4/enrich/raw/github_com_automatalab_jsonski.json](../../../data/wave4/enrich/raw/github_com_automatalab_jsonski.json) (enrichment confidence 0.8)

</details>
