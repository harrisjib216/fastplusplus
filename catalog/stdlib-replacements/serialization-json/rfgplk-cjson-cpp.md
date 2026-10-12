# cjson.cpp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [JSON serialization](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only SIMD index/tape JSON parser for C++26 on the micron runtime, \~9-31x faster than nlohmann::json.

| | |
|---|---|
| **Beats** | nlohmann::json |
| **Claimed result** | vs simdjson-dom(warm) parse/index (as printed on page, best variant cjson-reuse): 1.18x on 64KB (2.69 vs 2.29 GB/s), 1.11x on 1MB (2.52 vs 2.27 GB/s), 0.99x on twitter.json and 5MB. cjson-reuse is behind simdjson-dom on 12 of 18 corpus documents, e.g. canada 0.55 vs 0.73, numbers 0.61 vs 0.82 GB/s. vs nlohmann::json 3.12.0: \~31x on 1MB parse (cjson-reuse 2.52 vs nlohmann tree 0.08 GB/s) and \~25x on twitter extract-dom (2.02 vs 0.08 GB/s) (both derived from page data). Plain non-reuse cjson on 1MB is 0.74 GB/s, \~9x nlohmann (derived from page data). vs yyjson serialize (as printed, cjson-reuse): 2.13x twitter (2.33 vs 1.09 GB/s), 3.16x 1MB (2.21 vs 0.70), 3.12x 5MB (2.11 vs 0.68). |
| **Workload** | Parse/extract/serialize over an 18-document JSON corpus (57KB-26MB: synthetic 64kb/1MB/5MB/large-file, twitter, github_events, citm_catalog, canada, numbers, mesh, gsoc-2018, semanticscholar, etc.). The benchmark is benches/corpus_vs.cpp. It compares cjson's index/tape parser against nlohmann::json 3.12.0, RapidJSON 1.1.0, Boost.JSON 1.90.0, glaze 8.0.0, simdjson and yyjson. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3700U, kernel 7.1.7-200.fc44.x86_64, taskset -c 0, medians of 7 runs |
| **Compiler and flags** | GCC 16.1.1 20260515; every contender built -O3 -march=native -flto -ffat-lto-objects, bench TU adds -Ofast -std=c++26 |
| **Adoption** | 2 stars |
| **Last commit** | 2026-08-14 |
| **Links** | [repository](https://github.com/rfgplk/cjson.cpp) · [benchmark](https://github.com/rfgplk/cjson.cpp/blob/master/benches/results/corpus_vs.txt) |

## Verdict

On the author's own benches/corpus_vs.cpp (GCC 16.1.1, -O3 -march=native -flto -ffat-lto-objects, AMD Ryzen 7 3700U, taskset -c 0, medians of 7 runs), cjson-reuse parses 1MB JSON at 2.52 GB/s vs nlohmann::json 3.12.0's 0.08-0.09 GB/s on comparable documents (twitter.json parse/tree: 0.08 GB/s) and extracts fields from twitter.json (cjson-dom) at 2.02 GB/s vs nlohmann's 0.08 GB/s; against simdjson-dom(warm) cjson-reuse is close (1.18x on 64KB, 0.99x on twitter/5MB) and behind on 12 of 18 corpus documents.

## Use it when

- Hot-path parse/extract of JSON from 64KB to tens of MB where an index/tape handle (not an owning, freely-mutable tree) is acceptable
- Already targeting C++26 on GCC and willing to build against the micron core library instead of STL/libc
- Need SIMD parsing on amd64 (SSSE3/AVX2+PCLMUL), aarch64/armv7 NEON, or a portable SWAR fallback, and can fix the build to one target ISA
- Want compile-time (consteval) JSON parsing/validation baked into a binary, e.g. static config literals
- Serialize-heavy workloads where cjson-reuse is claimed 2-3x over yyjson on twitter/1MB/5MB documents

## Skip it when

- Need a drop-in nlohmann::json replacement with a fully owning, freely-mutable std::string/vector/map tree
- Cannot take on a second core library (micron) or cannot leave the C++ STL/libc; README states no traditional STL support
- Need a single binary that runs across AVX2 and non-AVX2 hosts -- no runtime CPU dispatch is provided
- Need proven maturity: repo is about 7 weeks old, 2 stars, 1 open issue, single author, no third-party reproduction of the benchmark numbers
- Object-heavy or numeric corpora where cjson-reuse still trails simdjson-dom(warm), e.g. canada.json 0.55 vs 0.73 GB/s and numbers.json 0.61 vs 0.82 GB/s -- pick simdjson there instead

## How it is fast

Two-stage SIMD engine: stage 1 scans 64-byte blocks to build structural indexes, quote/escape masks, and validate UTF-8 in one sweep (SSSE3/AVX2+PCLMUL on amd64, NEON on aarch64/armv7, a SWAR fallback elsewhere); stage 2 is a scalar FSM building a contiguous 16-byte value arena, i.e. a flat tape rather than a DOM tree. Strings stay as {offset,length} spans with lazy unescape and linear-scan object lookup, avoiding per-node allocation entirely; the 'cjson-reuse' variant additionally amortizes allocation by reusing a warm scratch buffer across calls. This is the same index/tape design used by simdjson-dom and yyjson (which is why cjson tracks those two closely), and it is what produces the large margin over owning-tree parsers like nlohmann, RapidJSON, Boost.JSON and glz::generic.

## Compared with alternatives

Pick cjson over json.cpp, DAW JSON Link, or Tachyon.JSON when you want simdjson-class index/tape throughput (it tracks simdjson-dom within about 1x on several sizes) plus a native consteval parse mode and a lazy functional pipeline; those siblings stay on an STL-based, nlohmann-like data model, while cjson requires leaving the STL for micron.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | micron core library (github.com/rfgplk/micron.cpp) only; no STL, no libc |
| **Minimum toolchain** | C++26; README states 'GCC 16+', INSTALL states 'g++ &gt;= 14 (cjson uses -std=c++26 and `if consteval`)' -- the two documents disagree on the minimum GCC version |
| **Platforms** | x86-64 (SSSE3, AVX2+PCLMUL), aarch64 (NEON), armv7 (NEON), portable SWAR fallback; no runtime CPU dispatch, so a binary built with AVX2 requires AVX2 at runtime |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial -- explain: conceptually similar one-shot/DOM surface (parse/get/iterate) but different types and ownership model (index/tape doc vs nlohmann's owning tree) plus a mandatory micron dependency; not a header-swap replacement |

## Gotchas

- Adopting cjson means leaving the C++ STL/libc for the micron core library -- a whole-program dependency change, not just adding a header
- No runtime CPU dispatch: a binary built for AVX2 will not run correctly on non-AVX2 hardware
- Erasing an object member does not reclaim its pool bytes, and a warm scratch buffer holds memory proportional to the largest document it has seen until release()
- Glaze's own author opened issue #2 arguing the DOM benchmark rows compare cjson against glz::generic (Glaze's schema-less owning-tree fallback), not Glaze's reflection-based fast path; this dispute is about the Glaze rows specifically, not the nlohmann numbers

## Caveats and trade-offs

The cjson-vs-nlohmann numbers cross parser categories: cjson's index/tape parse vs nlohmann's full owning-tree parse. The file prints them in separate index and tree bands, so the \~25-31x figures divide across bands. Headline wins use the 'cjson-reuse' buffer-reuse variant. Plain cjson parse is much slower, e.g. 0.74 GB/s on 1MB, tied with yyjson. cjson-reuse trails simdjson-dom(warm) on 12 of 18 documents, and cjson-ondemand trails simdjson-ondemand on every document. For serialize, the GB/s ratios disagree with the cyc/op ratios (1MB: 3.16x GB/s but 0.94x cyc/op), so treat the serialize GB/s wins with caution. The repo is \~7 weeks old, has 2 stars and one author, and no third party has reproduced it.

Depends on a custom 'micron' core library instead of the traditional C++ STL/glibc (README states 'no support for the traditional C++ Standard Library'); requires C++26; cjson is an index/tape parser (strings not materialized, lazy unescape) so its output shape differs from nlohmann's fully-materialized owning tree.

## Maintenance

Active (created 2026-08-08, last commit 2026-08-14) but very new: about 7 weeks old, 2 stars, 1 open issue, single author, MIT-licensed and header-only so it is cheap to vendor even if development stalls.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** corpus_vs.txt states the Ryzen 7 3700U CPU, GCC 16.1.1 and full flags (-O3 -march=native -flto -ffat-lto-objects; bench TU -Ofast -std=c++26). The benchmark code is public in benches/corpus_vs.cpp and scripts/vsbuild. It includes nlohmann 3.12.0 rows. First-party, but it meets the A criteria.
- **Verifier notes:** All cited figures appear in corpus_vs.txt. The claim was cherry-picked vs simdjson, so I expanded claimed_speedup and caveats. The nlohmann baseline claim holds on every document. Metadata matches gh: MIT, 2 stars, last commit 2026-08-14.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/rfgplk/cjson.cpp>
  - <https://github.com/rfgplk/cjson.cpp/blob/master/benches/results/corpus_vs.txt>
  - <https://github.com/rfgplk/cjson.cpp/blob/master/scripts/vsbuild>
  - <https://github.com/rfgplk/cjson.cpp/blob/master/scripts/license_swap.py>
- **Sources the enricher read:**
  - <https://github.com/rfgplk/cjson.cpp>
  - <https://github.com/rfgplk/cjson.cpp/blob/master/README.md>
  - <https://github.com/rfgplk/cjson.cpp/blob/master/INSTALL>
  - <https://github.com/rfgplk/cjson.cpp/blob/master/scripts/license_swap.py>
  - <https://github.com/rfgplk/cjson.cpp/blob/master/include/fetch_micron.sh>
  - <https://github.com/rfgplk/cjson.cpp/blob/master/benches/results/corpus_vs.txt>
  - <https://github.com/rfgplk/cjson.cpp/issues/2>
  - https://github.com/rfgplk/cjson.cpp (repo metadata: stars, forks, open issues, license, timestamps)
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/rfgplk/cjson.cpp`) · [data/wave1/enrich/raw/github_com_rfgplk_cjson_cpp.json](../../../data/wave1/enrich/raw/github_com_rfgplk_cjson_cpp.json) (enrichment confidence 0.68)

</details>
