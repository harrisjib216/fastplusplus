# jieba-rs (Rust Chinese word segmentation)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust port of the jieba Chinese word segmenter; claimed faster than cppjieba, about 2.2x faster than nodejieba through Node bindings.

| | |
|---|---|
| **Beats** | cppjieba (C++ port of jieba Chinese word segmentation) |
| **Claimed result** | README link title only: 'Optimizing jieba-rs to be 33% faster than cppjieba' (2019-06-30 post, unreachable here; a search snippet of the later 'Making jieba-rs 2.4x faster' post says only that 'back in 2019, Paul Meng wrote a post about getting jieba-rs 33% faster than cppjieba'). The 2.4x post is jieba-rs against its own earlier version (2.85 us to 1.32 us per call on the HMM path, Apple M4 Max, criterion, one sentence; snippet only). Related binding numbers in the napi-rs/node-rs packages/jieba README (jieba-rs 0.11.0 through @node-rs/jieba against nodejieba 3.5.8, which wraps cppjieba; Apple M4 Max, Node.js v26.8.2, tinybench): Cut on the 246,568-character weicheng text 17,941,189 ns vs 39,167,640 ns average, about 2.18x (derived from page data); Cut on the 1,184-character preface 61,311 ns vs 133,632 ns, about 2.18x (derived from page data); Tag 1,184 characters 158,515 ns vs 305,060 ns and Tag 246,568 characters 42,167,642 ns vs 86,278,741 ns, about 1.9-2.05x (derived from page data). |
| **Workload** | Chinese word segmentation (cut) of text; the README does not state the corpus. |
| **Metric** | throughput |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Adoption** | 987 stars; many bindings (Node, Python, PHP, WASM, R) |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/messense/jieba-rs) · [benchmark](https://github.com/messense/jieba-rs) |

## Verdict

No reproducible jieba-rs vs cppjieba measurement exists: the 33% figure comes from a 2019 contributor blog post (blog.paulme.ng, unreachable here, known only by its title and a later snippet), and the later 'Making jieba-rs 2.4x faster' post is jieba-rs against its own earlier version (2.85 to 1.32 us per HMM cut on an Apple M4 Max, snippet only). The closest public numbers are the @node-rs/jieba README (jieba-rs 0.11.0 vs nodejieba 3.5.8 wrapping cppjieba, Apple M4 Max, Node.js v26.8.2, tinybench): Cut on the 246,568-character Weicheng text 17.9 ms vs 39.2 ms and on a 1,184-character preface 61.3 us vs 133.6 us (about 2.18x, derived from page data), Tag about 1.9-2.05x, with both bindings in non-HMM mode and binding marshalling included on both sides.

## Use it when

- Rust services or pipelines that segment large volumes of Chinese text with jieba-compatible output and dictionaries (default dictionary is jieba's; Traditional-character coverage is not documented, see issue #112).
- Search indexing (tantivy via cang-jie or tantivy-jieba) where cut_for_search or tokenize with byte offsets feeds an inverted index.
- Multi-threaded batch segmentation: one shared Jieba (cut takes &self, the crate's own bench shares a static LazyLock&lt;Jieba&gt; across rayon threads).
- Node.js, Python, PHP, WASM or R projects that want a faster drop-in for nodejieba or Python jieba through the existing bindings.
- Keyword extraction with jieba's TF-IDF or TextRank on the same segmenter (features tfidf, textrank).

## Skip it when

- You need cppjieba's exact C++ API inside a C++ codebase: jieba-rs exposes only a Rust API and an unpublished C API whose cut copies every token into a new heap string (marked FIXME), which eats into the per-call advantage.
- You need a reproducible, current speed figure against cppjieba before switching: none exists in either repository (see verified claims).
- Japanese, Korean or other languages: the classifiers treat only CJK ideographs plus ASCII alphanumerics and '+#&._%-' as segmentable text; use Vibrato or Vaporetto for Japanese.
- Binary size or startup matters: the embedded dictionary is compressed into the binary and Jieba::new decompresses and builds the trie at runtime (issue #98 asks how to reduce binary size); disable default-dict and load a dictionary yourself.
- You require output stable across versions: tokenization changed in September 2026 (RE_SKIP dot fix #157, search-mode alphanumeric blocks #161).

## How it is fast

The dictionary lives in a character-level trie whose root transitions for BMP characters are a directly indexed 65,536-entry table and whose other edges sit in one open-addressing hash table keyed by (parent node, char), each slot carrying the child id, the word id and a small Bloom-style filter of the child's first characters, so most walks cost one probe per character and non-children cost none; cppjieba's Trie.hpp instead allocates an unordered_map&lt;Rune, TrieNode\*&gt; per node. Word candidates go into a compressed-sparse-row DAG (one flat u64 edge array), log-frequencies are kept in a dense f64 array for the route DP, and per-thread scratch buffers (thread_local) are reused so a cut allocates only its output vector. Han-run splitting is a hand-written character-class scanner (the regex dependency was dropped in September 2026) and character counting uses the bytecount crate's runtime-dispatched SIMD.

## Compared with alternatives

No Chinese segmenter is catalogued yet; the nearest siblings are Vibrato (MeCab reimplementation) and Vaporetto (KyTea-style pointwise tokenizer), which target Japanese, so pick jieba-rs for Chinese text and jieba-compatible dictionaries, and those two for Japanese.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | jieba-macros, bytecount, rustc-hash; include-flate (default-dict, tfidf), ordered-float (tfidf, textrank); wasm-bindgen and serde on wasm targets |
| **Minimum toolchain** | Rust edition 2024 (Rust 1.85 or newer); no rust-version declared on crates.io |
| **Platforms** | any Rust target, including wasm (wasm-bindgen exports); no architecture-specific code in the core files read |
| **Thread safety** | cut, tag and tokenize take &self and use thread-local scratch buffers, so one Jieba can be shared across threads; add_word, load_dict and set_hmm_model need &mut self |
| **Drop-in for the baseline** | partial — same algorithm and dictionary file format as cppjieba, but a Rust API (Vec&lt;Token&gt; results); C/C++ use goes through the unpublished capi cdylib, and the Node/Python bindings replace nodejieba/jieba rather than cppjieba itself |

## Gotchas

- README example is stale: it compares jieba.cut(...) to a Vec&lt;&str&gt;, but cut now returns Vec&lt;Token&lt;'a&gt;&gt; and the crate docs map t.word first; upgrading from older versions breaks callers that expected Vec&lt;&str&gt;.
- Harness note on the only full comparison (@node-rs/jieba vs nodejieba 3.5.8): both bindings default to HMM off (node-rs cut hmm.unwrap_or(false); nodejieba lib/nodejieba.cpp useHMM = false), so the 2.18x Cut rows compare like modes on the Weicheng corpus; but nodejieba 3.5.8 is itself a node-addon-api (N-API) addon, so the README's 'N-API is faster than v8 C++ API' explanation is stale, nodejieba's binding.gyp sets no optimisation flags (node-gyp Release defaults or a downloaded prebuilt binary), and the benchmark script no longer contains the nodejieba row, so the table cannot be regenerated.
- The repository's mirror of cppjieba's load test (examples/weicheng) installs tikv-jemallocator as global allocator and cuts line by line with wall-clock Instant, while cppjieba's test/load_test.cpp uses the system allocator, CPU-time clock(), MixSegment with HMM on and now a different input (synthetic_doc.utf8); results from the two are not comparable as published.
- Very large single inputs: jieba-rs 0.7.2 aborted on a 250 MB document with a 4 GB StaticSparseDAG allocation (issue #124, fixed by capping DAG capacity in PR #126); current code also drops per-thread scratch above 4 MiB (32 MiB for DAG edges) after each call, so huge inputs re-allocate every time.

## Known shortcomings

- 33% over cppjieba appears only in a README link title to a 2019 blog post whose host is unreachable (snippet only); the @node-rs/jieba 2.2x over nodejieba (Apple M4 Max) goes through two different binding layers and its current bench script no longer runs nodejieba; the Weicheng load test pairs jemalloc against cppjieba's system allocator.
- Still no reproducible comparison with cppjieba: the 33% figure exists only in an unreachable 2019 blog (messense.me ENOTFOUND). The @node-rs/jieba vs nodejieba 3.5.8 harness runs both with HMM off (node-rs hmm.unwrap_or(false), nodejieba useHMM=false), so the Cut rows (about 2.18x) compare the same mode on Weicheng, but nodejieba 3.5.8 also uses node-addon-api (N-API), so the README's 'N-API faster than the V8 C++ API' explanation is stale; nodejieba's binding.gyp sets no -O flags and its row is gone from the bench script. The README example is stale (cut now returns Vec&lt;Token&gt;); the C API copies every token to a heap string; output changed in September 2026 (#157, #161). The speed comes from a flat open-addressing char trie against cppjieba's unordered_map-per-node Trie.

## Caveats and trade-offs

Title-only evidence for the cppjieba comparison: the 2019 blog host (blog.paulme.ng) and messense.me do not resolve from this environment, so the numbers, corpus, hardware and compiler flags are unverified, and the 2019 figure predates years of changes to both projects. The repository's examples/weicheng/src/main.rs mirrors cppjieba's load test (cut every line of the Weicheng novel 50 times with HMM) but installs tikv-jemallocator as the global allocator, while cppjieba's test/load_test.cpp uses the system allocator, clock() timing and now a different input (synthetic_doc.utf8); cppjieba's CMakeLists adds -O3 -g. The crate's own cargo bench (criterion/CodSpeed) measures jieba-rs only. The @node-rs/jieba README table (about 2.2x over nodejieba) goes through two different binding layers (N-API in Rust vs nodejieba's C++ addon), the README itself credits part of the gain to N-API being faster than the v8 C++ API, node-rs builds with lto=true and codegen-units=1 while nodejieba's build flags are not stated, and the current packages/jieba/benchmark/jieba.ts only adds the '@node-rs/jieba' row (nodejieba is no longer a dependency), so the comparison table cannot be regenerated from the repository. The 1,184 and 246,568 'words' in that table are JavaScript string lengths in characters. Kept as a lead for re-running cppjieba against current jieba-rs on the same corpus with the same allocator. [retier] The @node-rs/jieba vs nodejieba 3.5.8 harness runs both with HMM off, so the Cut rows (about 2.18x) compare the same mode, but nodejieba 3.5.8 also uses node-addon-api, so the README's 'N-API faster than the V8 C++ API' explanation is stale; nodejieba's binding.gyp sets no -O flags and its row is gone from the bench script. The speed comes from a flat open-addressing char trie against cppjieba's unordered_map-per-node Trie. Output changed in September 2026 (#157, #161); the C API copies every token to a heap string.

Default embedded dictionary is enabled by default; optional tfidf and textrank features. 'cargo bench --all-features' runs the repository's own benchmarks.

## Maintenance

Actively maintained (0.11.0 released 2026-09-16, about 4.4 million crates.io downloads, many bindings), MIT-licensed and pure Rust with no unsafe in the core files read; usable from C/C++ only via the unpublished capi crate.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The repository README names cppjieba only through link titles ('Optimizing jieba-rs to be 33% faster than cppjieba', 2019, by contributor Paul Meng); the post's host does not resolve here, so corpus, hardware and flags are unseen (snippet only). The only full table is first-party-adjacent binding numbers in the napi-rs/node-rs README whose current benchmark code no longer runs the nodejieba row, so nothing reaches A or B.
- **Verifier notes:** Real port with a long-standing, widely relayed 33%-faster-than-cppjieba claim, but the only source with the number is an unreachable 2019 contributor blog; tier C (snippet/title only). Shortcomings: no reproducible cppjieba comparison in the repo, jemalloc vs system allocator in the mirrored load test, binding-level numbers in @node-rs/jieba confounded by N-API vs nodejieba binding and no longer reproducible from its bench script. Not a language-level claim; same jieba algorithm (prefix-dict DAG plus HMM Viterbi) on both sides but harness equivalence unverified.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-37 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/messense/jieba-rs>
  - <https://github.com/messense/jieba-rs/commits>
  - <https://raw.githubusercontent.com/messense/jieba-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/messense/jieba-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/messense/jieba-rs/HEAD/jieba/Cargo.toml>
  - <https://github.com/messense/jieba-rs/tree/master/examples/weicheng>
  - <https://raw.githubusercontent.com/messense/jieba-rs/HEAD/examples/weicheng/src/main.rs>
  - <https://raw.githubusercontent.com/messense/jieba-rs/HEAD/examples/weicheng/Cargo.toml>
  - <https://raw.githubusercontent.com/yanyiwu/cppjieba/HEAD/test/load_test.cpp>
  - <https://raw.githubusercontent.com/yanyiwu/cppjieba/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/napi-rs/node-rs/HEAD/packages/jieba/README.md>
  - <https://github.com/napi-rs/node-rs/tree/main/packages/jieba>
  - <https://github.com/napi-rs/node-rs/tree/main/packages/jieba/benchmark>
  - <https://raw.githubusercontent.com/napi-rs/node-rs/HEAD/packages/jieba/benchmark/jieba.ts>
  - <https://raw.githubusercontent.com/napi-rs/node-rs/HEAD/packages/jieba/package.json>
  - <https://raw.githubusercontent.com/napi-rs/node-rs/HEAD/Cargo.toml>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/messense/jieba-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/messense/jieba-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/messense/jieba-rs/HEAD/jieba/Cargo.toml>
  - <https://raw.githubusercontent.com/messense/jieba-rs/HEAD/examples/weicheng/src/main.rs>
  - <https://raw.githubusercontent.com/messense/jieba-rs/HEAD/examples/weicheng/Cargo.toml>
  - <https://raw.githubusercontent.com/messense/jieba-rs/HEAD/jieba/src/lib.rs>
  - <https://raw.githubusercontent.com/messense/jieba-rs/HEAD/jieba/src/trie.rs>
  - <https://raw.githubusercontent.com/messense/jieba-rs/HEAD/jieba/src/sparse_dag.rs>
  - <https://raw.githubusercontent.com/messense/jieba-rs/HEAD/jieba/src/hmm.rs>
  - <https://raw.githubusercontent.com/messense/jieba-rs/HEAD/jieba/benches/jieba_benchmark.rs>
  - <https://raw.githubusercontent.com/messense/jieba-rs/HEAD/capi/Cargo.toml>
  - <https://raw.githubusercontent.com/messense/jieba-rs/HEAD/capi/src/lib.rs>
  - <https://github.com/messense/jieba-rs/tree/master/jieba/src>
  - <https://github.com/messense/jieba-rs/issues?q=is%3Aissue>
  - <https://github.com/messense/jieba-rs/issues/124>
  - <https://github.com/messense/jieba-rs/issues/157>
  - <https://github.com/messense/jieba-rs/commits/master>
  - https://messense.me/making-jieba-rs-2-4x-faster (ENOTFOUND)
  - <https://crates.io/api/v1/crates/jieba-rs>
  - <https://raw.githubusercontent.com/napi-rs/node-rs/HEAD/packages/jieba/README.md>
  - <https://raw.githubusercontent.com/napi-rs/node-rs/HEAD/packages/jieba/benchmark/jieba.ts>
  - <https://github.com/napi-rs/node-rs/tree/main/packages/jieba/src>
  - <https://raw.githubusercontent.com/napi-rs/node-rs/HEAD/packages/jieba/src/lib.rs>
  - <https://github.com/yanyiwu/nodejieba>
  - <https://github.com/yanyiwu/nodejieba/tree/master/lib>
  - <https://raw.githubusercontent.com/yanyiwu/nodejieba/HEAD/index.js>
  - <https://raw.githubusercontent.com/yanyiwu/nodejieba/HEAD/package.json>
  - <https://raw.githubusercontent.com/yanyiwu/nodejieba/HEAD/README.md>
  - <https://raw.githubusercontent.com/yanyiwu/nodejieba/HEAD/lib/nodejieba.cpp>
  - <https://raw.githubusercontent.com/yanyiwu/nodejieba/HEAD/binding.gyp>
  - <https://raw.githubusercontent.com/yanyiwu/cppjieba/HEAD/include/cppjieba/Trie.hpp>
  - <https://raw.githubusercontent.com/yanyiwu/cppjieba/HEAD/test/load_test.cpp>
  - WebSearch: "jieba-rs" cppjieba benchmark 33% faster weicheng Paul Meng (snippets: messense.me 2.4x post, npm @node-rs/jieba)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/messense/jieba-rs`) · [data/wave14/enrich/raw/github_com_messense_jieba_rs.json](../../../data/wave14/enrich/raw/github_com_messense_jieba_rs.json) (enrichment confidence 0.6)

</details>
