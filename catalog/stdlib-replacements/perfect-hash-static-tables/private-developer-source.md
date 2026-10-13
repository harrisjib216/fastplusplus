# fastcpp::phf (developer source)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Perfect hashing and static tables](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Compile-time perfect hash table for fixed string-key sets (keywords, opcodes); 5.8-7x faster lookups than std::unordered_map.

| | |
|---|---|
| **Beats** | std::unordered_map |
| **Claimed result** | 6.98x on all-hit lookups (3.327ns vs 23.208ns/op), 6.70x on all-miss (3.02ns vs 20.243ns), 5.76x on mixed 1:8 (4.903ns vs 28.235ns) -- verbatim from results/fastest.json. Also beats phmap::flat_hash_map (Apache-2.0, vendored in-repo) 3.7x and frozen::unordered_map 3.5-3.7x on the same static workload, though the frozen comparison is weaker evidence (see caveats). |
| **Workload** | 200k keyword lookups against a 92-key C++20 keyword table (fastcpp::phf, a compiler-built perfect hash baked into .rodata) compared to std::unordered_map&lt;string_view,uint16_t&gt;, measured separately for all-hit, all-miss, and 1:8-mixed-hit-rate corpora. |
| **Metric** | latency |
| **Hardware** | Intel Xeon @ 2.10GHz (AVX2, SSE4.2, BMI2), 4 cores, Ubuntu 24.04 / Linux 6.18 -- a shared cloud VM; the repo's own results file warns absolute ns move between runs on this host (ratios within a run are what is claimed as stable) |
| **Compiler and flags** | gcc 13.3.0, -O2 -g -DNDEBUG -std=c++20 -march=native (CMake RelWithDebInfo, 'release' preset) |
| **Adoption** | 0 stars (private repo, not independently discoverable) |
| **Last commit** | 2026-09-04 |
| **Links** | private repository, not published yet |

## Verdict

With gcc 13.3 and libstdc++ at -O2 -march=native -std=c++20 on a shared 4-core 'Intel Xeon @ 2.10GHz' cloud VM (commit dfa74f2, minimum of 7 samples), 200k lookups against the 92 C++20 keywords took 3.3 ns vs 23.2 ns for std::unordered_map&lt;string_view,uint16_t&gt; when every lookup hit, 3.0 vs 20.2 ns when every lookup missed, and 4.9 vs 28.2 ns with 1 keyword per 8 words. These are the author's own numbers, with no outside review, and the results file warns that absolute ns drift between runs (3.42 vs 5.24 ns for the same lookup); only the ratios within a run are claimed.

## Use it when

- Keyword recognition in a lexer or parser: a closed set of short string keys (16 bytes or less by default) mapped to small integer IDs on a hot path, like the repo's 92 C++20 keywords and 48 JavaScript keywords.
- Streams where most lookups miss, like identifiers checked against keywords. The length and first-character gates reject many of them before hashing. Measured: 3.0 ns vs 20.2 ns per miss against std::unordered_map.
- Tables of opcodes, header names or enum labels that you want to cost nothing at startup, use no heap, and be checked at compile time with static_assert.
- Lexers whose source buffer has at least 16 readable bytes past every token. That allows the opt-in overread16 compare policy, which measured 3.02 ns vs 3.33 ns for the default memcmp (about 1.1x; the 1.44x figure is measured against the inline_words policy, not the default).
- You want strager's character-selection technique under a permissive licence: this is an MIT reimplementation, while strager's own repository is CC-BY-NC-ND.

## Skip it when

- Keys that are only known at run time, or that change. find_parameters can run at startup, but perfect_hash_table takes the search result as a non-type template argument, so the shipped table can only be built from compile-time keys, and it has no insert or erase.
- Large key sets. By the builder's own comment, a single-level perfect hash needs about O(n^2) slots to be found quickly. The 92-key table already takes 1024 slots (about 20 KiB), slot count is capped at 2^16, and the default budget is 1024 seeds per configuration. This is built for tens to low hundreds of keys, not thousands.
- Keys that agree at every position it can sample (s[0], s[1], s[2], s[n/2], s[n-3], s[n-2], s[n-1] and the length), such as long paths or URLs with shared prefixes and suffixes. No seed can separate them and the search fails. Non-string keys (integers) are not supported at all.
- Code you need to depend on. The repo is private, three days of commits, single-author (every commit authored by 'Claude'), not reviewed by anyone else, and its CI has never passed. The public siblings are more practical.
- If you already use a good open-addressing map, the margin is smaller. The repo measured its own SIMD Swiss table at 8.86 ns vs 3.33 ns (2.7x) on all-hit lookups, and phmap::flat_hash_map at 19.8 ns vs 5.3 ns (3.7x) on the mixed stream.

## How it is fast

It reimplements the technique from Matthew 'strager' Glazar's talk 'Faster than Rust and C++: the PERFECT hash table' as a constexpr brute-force search for a single-level perfect hash. The search tries, cheapest first, which characters to hash (any subset of s[0], s[1], s[2], s[n/2], s[n-3], s[n-2], s[n-1] and the length), a power-of-two table size and a 32-bit seed. The resulting hash is a few byte loads packed into one 64-bit word and one multiplicative (Lehmer-style) hash, with no loop over the string; the benchmarked C++ table hashes 3 characters into 1024 slots. Length-range and first-character-range gates reject many misses before any hashing. Keys are stored inline in the slots of a .rodata array, so a hit costs one load and one std::memcmp, with no probe loop or pointer chase.

## Compared with alternatives

Pick it over strager/perfect-hash-tables when you need the same character-selection technique under MIT instead of CC-BY-NC-ND. Pick it over frozen when your keys are short strings and lookup latency is what matters, but note that the repo's 3.5x-over-frozen claim has no committed benchmark code. Otherwise the public ConstexprCore/perfect_hash and Kronuz constexpr-phf are the realistic choices, because this code cannot currently be obtained.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | None beyond the standard library. The phf code is 11 headers under include/fastcpp/{phf,hash,core}. Copy those rather than using add_subdirectory: the repo's fastcpp::fastcpp CMake target links all 10 vendored libraries (fmt, phmap, xsimd, simdjson, CRoaring, yyjson, ...) and forces C++23. |
| **Minimum toolchain** | C++20: class-type non-type template parameters, concepts, &lt;bit&gt;, std::is_constant_evaluated. The README lists gcc 13+, clang 17+ and MSVC 19.35+ (gcc 12 and clang 16 with -std=c++2b). The benchmarks used gcc 13.3 with -std=c++20. CI compiles test_phf with gcc and clang. MSVC is not in CI. |
| **Platforms** | Portable scalar lookup path, with a 64-bit multiply fallback where there is no __int128. overread16 uses SSE2 on x86 and silently falls back to inline_words on other targets. The crc32c hashers use SSE4.2, selected at run time, or ARMv8 CRC. Benchmarked only on x86-64 Linux. CI builds on Linux (gcc, clang) and macOS (clang). |
| **Thread safety** | Not documented. By construction, a table is an immutable constexpr aggregate and lookup() is const noexcept with no mutable state, so concurrent lookups are safe. |
| **Drop-in for the baseline** | partial — it replaces std::unordered_map&lt;string_view, V&gt;::find only for a key set fixed at compile time. lookup() returns V or a miss sentinel instead of an iterator, and there is no insert, erase, iteration or count. |

## Gotchas

- A miss returns a sentinel value, not an optional or an iterator: whatever miss value you pass to make_table (the keyword sets reserve 0). make_table does not check that no key maps to that same value.
- overread16 requires 16 readable bytes at the query pointer, whatever the key length. Without padding, a token near the end of a buffer or page can fault. It is opt-in for that reason.
- Slot text capacity defaults to 16 bytes and is enforced by static_assert. From reading the code, if you raise TextCapacity for longer keys, only memcmp and first_char_then_memcmp stay correct. inline_words compares only the first and last 8 bytes, so it can report a false hit on 17+ byte keys. overread16 masks just 16 lanes, so it never matches a 17+ byte key. No test covers this, because the longest test key is exactly 16 bytes.
- The compile-time search needs a raised constexpr limit on clang (the repo uses -fconstexpr-steps=100000000, 100x the default). That flag sits on the repo's internal fastcpp_flags target, not on fastcpp::fastcpp, so consumers must add it themselves. A table that builds on gcc can fail on clang. Any failure, including one caused by duplicate keys, shows up only as the static_assert 'the perfect-hash search failed; widen search_options'.

## Known shortcomings

- The repo (private:developer-source) is private, so the link returns 404 for readers and the result cannot be reproduced; the recorded run names no CPU model beyond 'Intel Xeon @ 2.10GHz'.

## Caveats and trade-offs

The repo is PRIVATE and readable only with an authenticated gh CLI, so the benchmark code is not public and the entry cannot be Tier A. List readers will get a 404 on repo_url and benchmark_url. It has 0 stars. It is a single-author project: all 13 commits are authored by 'Claude' with Claude co-author trailers, and nobody outside has reviewed it. The CPU is given only as 'Intel Xeon @ 2.10GHz' (shared cloud VM, no SKU). The results file warns that absolute ns vary between runs (3.42 vs 5.24 ns for the same lookup) and that only ratios within one run are meaningful. The std::unordered_map numbers come from commit dfa74f2 at -O2 -std=c++20. HEAD CMake now forces -O3 and C++23 for benchmarks, so a rerun at HEAD would not use the recorded flags. The frozen::unordered_map figure (3.55x in results/fastest.json, '3.5-3.7x' in the notes) cannot be reproduced. bench/bench_vs_libraries.cpp, at HEAD and at 2e21aae, benchmarks only fastcpp::phf, phmap::flat_hash_map and std::unordered_map, and mentions frozen only in comments. The repo has no gperf comparison: gperf does not appear in the README or in results/fastest.json. The PHF techniques are reimplemented from strager's talk; the README says no code was copied from strager/perfect-hash-tables (CC-BY-NC-ND).

Only usable when the key set is closed at compile time (keywords, opcodes, enum labels) -- no runtime insert/delete. The shipped default comparison policy (std::memcmp) is not the fastest one measured: compare_policy::overread16 is 1.44x faster still but requires 16 readable bytes at the query pointer, so it is opt-in rather than default. Table size scales with key count and is baked into .rodata, growing binary size. Requires a C++20-capable compiler (gcc 13+/clang 17+/MSVC 19.35+) for the constexpr search; clang needs a much larger constexpr-step budget than gcc for the same search.

## Maintenance

The repo is currently private, so the public gets a 404, and it has 0 stars, no releases and 13 commits over 2026-09-02 to 2026-09-04. The phf part is MIT and small enough to vendor if you have access, but all 21 CI runs have failed: at HEAD the failures are in unrelated targets (the xsimd matmul benchmark build and a UBSan error in string/parse.hpp), and test_phf passes where it runs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification A, tier now C.
- **Tier reason:** Not Tier A, because the repo is PRIVATE (gh api reports visibility 'private'), so the benchmark code is not public. The search agent's claim that bench/bench_phf.cpp 'is public' is wrong. results/fastest.json (run 2026-09-02-core, commit dfa74f2) states the numbers, gcc 13.3.0, the flags and the CPU. bench/bench_phf.cpp does benchmark std::unordered_map&lt;string_view,uint16_t&gt;. The numbers are first-party and not peer-reviewed, so the tier is C.
- **Verifier notes:** All three std::unordered_map numbers match results/fastest.json exactly. bench/bench_phf.cpp at commit dfa74f2 is identical to HEAD. The phmap 3.7x figure is 19.787/5.322 ns (3.72x). The orchestrator should decide whether a private repo can go in COPYABLE at all. It has an MIT license, but the public cannot get the code.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - private:developer-source
  - private:developer-source/blob/main/results/fastest.json
  - private:developer-source/blob/main/bench/bench_phf.cpp
  - private:developer-source/blob/dfa74f2328b4dc52c99cc64352d20f063818e3d2/bench/bench_phf.cpp
  - private:developer-source/blob/main/bench/bench_vs_libraries.cpp
  - private:developer-source/blob/2e21aae/bench/bench_vs_libraries.cpp
  - private:developer-source/blob/main/bench/CMakeLists.txt
  - private:developer-source/blob/main/CMakeLists.txt
  - private:developer-source/blob/main/CMakePresets.json
  - private:developer-source/blob/main/include/fastcpp/phf/keyword_sets.hpp
  - private:developer-source/blob/main/README.md
  - private:developer-source/blob/main/LICENSE
  - private:developer-source/commit/dfa74f2328b4dc52c99cc64352d20f063818e3d2
- **Sources the enricher read:**
  - private:developer-source
  - private:developer-source/blob/main/README.md
  - private:developer-source/blob/main/include/fastcpp/phf/perfect_hash_table.hpp
  - private:developer-source/blob/main/include/fastcpp/phf/builder.hpp
  - private:developer-source/blob/main/include/fastcpp/phf/character_selection.hpp
  - private:developer-source/blob/main/include/fastcpp/phf/keyword_sets.hpp
  - private:developer-source/blob/main/include/fastcpp/hash/hashers.hpp
  - private:developer-source/blob/main/include/fastcpp/hash/crc32c.hpp
  - private:developer-source/blob/main/include/fastcpp/hash/lehmer.hpp
  - private:developer-source/blob/main/include/fastcpp/hash/mix.hpp
  - private:developer-source/blob/main/include/fastcpp/core/bits.hpp
  - private:developer-source/blob/main/include/fastcpp/core/cpu.hpp
  - private:developer-source/blob/main/include/fastcpp/core/macros.hpp
  - private:developer-source/blob/main/bench/bench_phf.cpp
  - private:developer-source/blob/main/bench/bench_vs_libraries.cpp
  - private:developer-source/blob/2e21aae/bench/bench_vs_libraries.cpp
  - private:developer-source/commit/2e21aae
  - private:developer-source/blob/main/bench/CMakeLists.txt
  - private:developer-source/blob/main/results/fastest.json
  - private:developer-source/blob/main/CMakeLists.txt
  - private:developer-source/blob/dfa74f2328b4dc52c99cc64352d20f063818e3d2/CMakeLists.txt
  - private:developer-source/commit/dfa74f2328b4dc52c99cc64352d20f063818e3d2
  - private:developer-source/blob/main/CMakePresets.json
  - private:developer-source/blob/main/.github/workflows/ci.yml
  - private:developer-source/blob/main/tests/test_phf.cpp
  - private:developer-source/blob/main/support/corpus.hpp
  - private:developer-source/blob/main/third_party/parallel-hashmap/VENDORING.md
  - private:developer-source/issues/1
  - private:developer-source/actions
  - private:developer-source/actions/runs/33828450197
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `private:developer-source`) · [data/wave1-phf/enrich/raw/private_developer_source.json](../../../data/wave1-phf/enrich/raw/private_developer_source.json) (enrichment confidence 0.85)

</details>
