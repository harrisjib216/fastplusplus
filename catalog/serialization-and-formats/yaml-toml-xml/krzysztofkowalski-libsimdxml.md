# libsimdxml

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [YAML, TOML and XML](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> C++23 port of Rust simdxml: SIMD structural XML indexer with XPath 1.0, claiming 1.04-1.24x pugixml parse throughput.

| | |
|---|---|
| **Beats** | pugixml |
| **Claimed result** | Base-clock run 165913 (15.09.2026, i7-4850HQ at 2.3 GHz, no turbo): 245.7 vs 206.3 MB/s (1 MB), 261.4 vs 227.8 (5 MB) and 285.2 vs 229.2 (10 MB) against pugixml 1.16 in-situ. The README states this as 1.19x/1.15x/1.24x. In the same run libxml2 DOM reached 28.5 MB/s at 1 MB (\~8.6x, derived from page data). A later turbo-on C++-only run (24.09.2026) gives 283.0 vs 271.1 MB/s (1 MB) and 296.5 vs 278.5 (10 MB) against pugixml (\~1.04x/\~1.06x, derived from page data). Against libxml2 DOM that run gives 37.8 and 38.0 MB/s (\~7.5x/\~7.8x, derived from page data). The README notes that at 10 MB libsimdxml uses \~8% more CPU than pugixml. The README also states 1.26x/1.35x/1.47x over Rust quick-xml 0.36 at 1/5/10 MB. |
| **Workload** | Single-threaded parse of the project's own deterministic synthetic XML (16,824 elements at 1 MB, depth up to 22, attributes, entities, CDATA, comments, PIs) into libsimdxml's structural index. Measured in MB/s and peak RSS against pugixml 1.16 (in-situ DOM), libxml2 DOM, expat SAX and parsers in other languages. Speed numbers are published only for 1/5/10 MB (the 24.09 run covers only 1 and 10 MB). The 15-30 MB corpora are listed but have no published numbers. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-4850HQ (Haswell, 2013 laptop), fixed at 2.3GHz base clock with turbo off for the headline speed table (a separate reference table notes a \~3.3GHz turbo-on run, explicitly not to be mixed with the base-clock numbers) |
| **Adoption** | 0 stars; very new repo (created 2026-09-07) |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/KrzysztofKowalski/libsimdxml) · [benchmark](https://github.com/KrzysztofKowalski/libsimdxml#benchmarks) |

## Verdict

In the README's base-clock run (i7-4850HQ fixed at 2.3 GHz with turbo off, fresh process per run, median of 9), parsing into the index ran at 245.7/261.4/285.2 MB/s versus pugixml 1.16 in-situ at 206.3/227.8/229.2 MB/s, a 1.15-1.24x lead on the project's own synthetic 1/5/10 MB XML. A later turbo-on run on the same laptop narrowed this to 283.0 vs 271.1 MB/s at 1 MB and 296.5 vs 278.5 MB/s at 10 MB (\~1.04-1.06x). That run showed \~8% more CPU time than pugixml at 10 MB but 0.81-0.88x of pugixml's peak RSS. No compiler, flags or harness are published, and the libxml2 DOM figures (28.5-38 MB/s) are not a like-for-like comparison.

## Use it when

- Read-only extraction or XPath 1.0 queries over trusted, well-formed XML of about 1-10 MB. The README shows a 4-24% faster parse and 12-19% lower peak RSS than pugixml at this size.
- Markup- and attribute-dense documents with comments, CDATA and PIs. These are skipped with bitmask tricks (e.g. dash & dash&gt;&gt;1 & gt&gt;&gt;2 finds '--&gt;') rather than byte loops.
- Shipping one x86-64 binary built with GCC/Clang to mixed fleets from SSE4.2-only to AVX2 CPUs, or to AArch64 NEON, with no -mavx2 build flags.
- Repeated queries over the same large files. load_or_parse() can reuse a persisted .sxi index, and parse_for_query() indexes only the tags a query names plus their ancestors.
- C++23 codebases that want std::expected error handling and zero-copy string_view results.

## Skip it when

- Untrusted or possibly malformed input. It does not check well-formedness: mismatched close tags such as &lt;a&gt;&lt;/b&gt; are accepted, and the MismatchedCloseTag error is never raised. DOCTYPE is skipped only up to its first '&gt;', and .sxi files are documented as trusted caches only.
- Documents nested deeper than 32 levels, which get degraded parent links. Also documents that rely on DTD-defined entities: only the five predefined entities and numeric references are decoded.
- Any need to modify or write XML. Unlike pugixml, there is no mutable DOM and no serializer.
- MSVC builds. has_avx2()/has_sse42() return false under _MSC_VER, so parse falls back to the plain memchr scanner and the SIMD path that was benchmarked is never used.
- Production code that needs maturity. The repo has 0 stars, was created 2026-09-07 and is at v0.1.0. It has no tests, CI or benchmark code, and it does not include the Rust crate's XPath conformance suites.

## How it is fast

Stage 1 classifies each 64-byte chunk with PSHUFB nibble-table lookups (the simdjson technique). This yields u64 bitmasks for '&lt;', '&gt;', both quote types, '-', ']', '/', '?' and whitespace. AVX2, SSE4.2, NEON and scalar backends are all compiled in and picked at run time via [[gnu::target]]. Stage 2 is a scalar state machine that jumps between set bits with countr_zero instead of scanning bytes, and popcounts of the '&lt;'/'&gt;' masks size every output vector exactly once. The parse only records offsets. It does no per-node allocation, no entity decoding and no attribute splitting (attributes are re-scanned on demand). ensure_indices() later builds CSR child lists with an AVX2 prefix sum, plus pre/post-order numbers for O(1) ancestor checks.

## Compared with alternatives

Parshred also has runtime-dispatched SIMD and XPath 1.0, and claims a much larger lead over pugixml (1.6-3.3x on its own benchmark). RapidXml has a third-party-measured lead over libxml2. Pick libsimdxml over them only if you want its lower-memory flat index with the .sxi cache and selective query parse, or need a scalar fallback on x86 CPUs without SSE4.2 (Parshred's README requires SSE4.2).

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none |
| **Minimum toolchain** | C++23 (uses std::expected, std::format, std::jthread) and CMake 3.20+; exact compiler versions not documented |
| **Platforms** | x86-64 with runtime AVX2/SSE4.2/scalar dispatch under GCC/Clang (scalar only under MSVC); aarch64 with NEON (used when PMULL/crypto is present, scalar otherwise); other architectures use the scalar fallback |
| **Thread safety** | Not documented. ensure_indices() and build_name_index() mutate the index in place, so build them before sharing an XmlIndex across threads; CompiledXPath::eval takes a const XmlIndex&. build_indices() spawns two std::jthreads above 10K tags, and parse_parallel() spawns one per chunk. |
| **Drop-in for the baseline** | no |

## Gotchas

- Call ensure_indices() before running XPath. Without the CSR indices, each child-axis step does a linear scan over all tags, which goes quadratic on large documents. An earlier A/B in the README shows the lead over pugixml falling from 1.26-1.36x (parse only) to 1.02-1.10x once the full index is built.
- Text and attribute values come back raw. Entities are decoded only when XPath extracts text, via XmlIndex::decode_entities, which allocates a std::string. Name IDs are u16 and clamp at 65,535 distinct tag names.
- Some declared API is missing or stubbed. parse_for_xpath() and the string_view overload of load_or_parse() in simdxml.hpp have no definition, so calling them is a link error. Every batch function (eval_batch_text, count_batch, eval_batch_parallel, ...) returns an error in the shipped build because SIMDXML_HAVE_XPATH is never defined. Use parse_for_query() and the std::filesystem::path overload of load_or_parse() instead.
- load_or_parse() writes a .sxi file next to the XML as a side effect. It hashes with FNV-1a, so it cannot read .sxi files written by the Rust crate (which uses xxh3). Accessors such as tag_type()/depth() use vector::at() and throw on out-of-range indices.

## Caveats and trade-offs

The benchmark harness, runners and data generator are not in the public repo, so the numbers cannot be reproduced. No compiler name/version or flags are stated, so this is capped at C. libsimdxml is a lenient, non-validating structural indexer, and nesting deeper than 32 levels gets degraded parent links. libxml2 checks well-formedness and builds a full DOM, so the \~7.5-8.6x libxml2 ratio is not like-for-like; pugixml is the fairer comparison. The README gives the pugixml lead as 1.15-1.24x at base clock, but the later turbo-on run shows only \~4-6% wall-time lead and \~8% more CPU at 10 MB. It is a C++ port of the Rust simdxml crate. 0 stars, repo created 2026-09-07, with no third-party review.

Runtime SIMD dispatch (AVX2/SSE4.2/NEON/scalar all compiled into one binary, selected via [[gnu::target]]); structure-of-arrays index instead of per-node heap allocation; does not target HTML; excludes tinyxml2 and fast-xml-parser from its cross-language table because they error out on the benchmark's processing-instruction corpus

## Maintenance

Actively developed by one author: 18 commits from 2026-09-07 to 2026-09-23, v0.1.0, no issues, releases or tags. It is MIT-licensed, keeps the Rust original's notice, and is a small dependency-free static library you could vendor, but it ships without tests.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification C, tier now C.
- **Tier reason:** These are first-party README numbers with the CPU stated (i7-4850HQ at a fixed 2.3 GHz). No compiler or flags are stated, and the benchmark harness (tmp/benchmark/orchestrator.sh, the runners, the data generator, tools/rss_sampler.py) is not in the public repo, which has 61 files and no bench or test code. So it is not A, and with no paper or third-party suite it is C.
- **Verifier notes:** The pugixml figures match the README exactly. I downgraded because the record's 'roughly 8-10x faster than libxml2' is overstated: the page supports \~7.5-8.6x, and nothing reaches 10x. The tier stays C. I also noted that the benchmark code is absent from the repo and that the project is a port of the Rust simdxml crate.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compared_against_cpp_std_directly`, `is_fork_of`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/KrzysztofKowalski/libsimdxml#benchmarks>
  - <https://github.com/KrzysztofKowalski/libsimdxml>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/CMakeLists.txt>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/NOTICE>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/LICENSE>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/.gitignore>
  - <https://github.com/simdxml/simdxml>
- **Sources the enricher read:**
  - <https://github.com/KrzysztofKowalski/libsimdxml>
  - <https://github.com/KrzysztofKowalski/libsimdxml#benchmarks>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/CMakeLists.txt>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/NOTICE>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/.gitignore>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/simdxml.hpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/error.hpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/bloom.hpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/bloom.cpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/index/xml_index.hpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/index/xml_index.cpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/index/structural.hpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/index/structural.cpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/index/types.hpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/index/tags.cpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/index/lazy.hpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/index/lazy.cpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/simd/dispatch.hpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/simd/detail.hpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/simd/avx2.hpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/simd/sse42.hpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/simd/neon.hpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/simd/scalar.hpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/parallel/parallel.hpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/parallel/parallel.cpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/persist/persist.hpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/persist/persist.cpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/batch/batch.hpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/batch/batch.cpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/xpath/xpath.hpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/xpath/eval.hpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/xpath/eval.cpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/xpath/simd_pred.cpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/xpath/analyze.cpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/xpath/parser.cpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/xpath/eval/axis_step.cpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/xpath/eval/internal.cpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/xpath/eval/function_call.cpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/xpath/eval/binary_op.cpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/xpath/eval/filter.cpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/blob/main/simdxml/xpath/eval/path_expr.cpp>
  - <https://github.com/KrzysztofKowalski/libsimdxml/commits/main>
  - <https://github.com/KrzysztofKowalski/libsimdxml/issues>
  - <https://github.com/KrzysztofKowalski/libsimdxml/releases>
  - <https://github.com/simdxml/simdxml>
  - <https://github.com/gregghy/parshred>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/krzysztofkowalski/libsimdxml`) · [data/wave4/enrich/raw/github_com_krzysztofkowalski_libsimdxml.json](../../../data/wave4/enrich/raw/github_com_krzysztofkowalski_libsimdxml.json) (enrichment confidence 0.75)

</details>
