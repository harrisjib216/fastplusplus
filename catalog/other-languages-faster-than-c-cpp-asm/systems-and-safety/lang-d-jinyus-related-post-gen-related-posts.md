# D v2 (related_post_gen suite)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `D` · `MIT` · 🟢 active

> Community D (ldc2) solution to the related-posts benchmark, about 1.43x faster than the suite's C++ solution single-core.

| | |
|---|---|
| **Beats** | C++ solution of the same suite (clang++ -O3 -std=c++20, nlohmann/json for JSON) |
| **Claimed result** | Single-core total (processing time without I/O): D (v2) 1.10 s vs C++ 1.57 s (about 1.43x, derived from page data); 60k posts 961.08 ms vs 1.39 s (about 1.45x); 20k posts 122.21 ms vs 164.33 ms (about 1.34x); 5k posts 12.06 ms vs 12.20 ms (parity). The first D entry (2.88 s total) is slower than C++. Multicore table: D Concurrent (v2) 326.26 ms vs C++ Concurrent 402.33 ms. |
| **Workload** | Given posts with tags, compute the top 5 related posts per post by shared tag count (read JSON, tag index, count, sort, write JSON); 5k, 20k and 60k posts; single core; no FFI, unsafe, or single-thread SIMD allowed. |
| **Metric** | latency |
| **Hardware** | AWS c7a.xlarge (4 vCPU, 8 GB RAM), Ubuntu 24.04; CPU model not stated |
| **Compiler and flags** | D v2: dub build --build=release (run.sh run_d_v2) with a custom release buildType of buildOptions optimize and inline only; the D image (dockerfiles/d.Dockerfile) installs only ldc2 1.41.0, and dub maps these to ldc2 -O3 -enable-inlining (dub source/dub/compilers/ldc.d); no -release and no -boundscheck=off, so bounds checks and asserts stay on. JSON via asdf 0.7.17 (dub.selections.json), outside the timed region. C++: clang++ -O3 -std=c++20 -I./include main.cpp (run.sh run_cpp), clang from the unpinned Arch Linux base image, no -march or LTO. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Adoption** | 500 stars (suite repo) |
| **Last commit** | 2026-02-24 |
| **Links** | [repository](https://github.com/jinyus/related_post_gen) · [benchmark](https://raw.githubusercontent.com/jinyus/related_post_gen/main/readme.md) |

## Verdict

On an AWS c7a.xlarge (CPU model not stated), mean processing time without JSON I/O was 12.06 / 122.21 / 961.08 ms for 5k / 20k / 60k posts (10, 3 and 3 runs) for D v2 built with ldc2 1.41.0 at -O3 with bounds checks on, versus 12.2 / 164.33 / 1393 ms for the C++ entry built with Arch Linux clang++ -O3 -std=c++20 (no -march, clang version unstated), about 1.43x on the totals (derived from page data). End to end including asdf versus nlohmann/json, the raw results show about 1.60 s versus 3.35-3.40 s and 118 MB versus 460 MB at 60k posts.

## Use it when

- As a reference pattern for sparse co-occurrence counting (posts by tags, items by features) where one post's counters fit in L1/L2 (tens of thousands of entries)
- When a D codebase needs bounds-checked (@safe, no -release) code that still avoids per-element checks in a hot scatter loop: hoist the check into pointer creation
- Single-core batch jobs of 5k to 60k items with 4-5 tags each from a 28-tag vocabulary, the measured shape
- When end-to-end memory matters: the raw results show about 118 MB peak RSS at 60k posts versus about 460 MB for the C++ entry

## Skip it when

- As evidence that D beats C++: the same pointer, unroll and fused-reset tricks are expressible in standard C++; the C++ entry simply does not use them
- Small inputs: at 5k posts it is at parity with C++ (12.06 vs 12.20 ms, C++ timer has 1 ms resolution) and slower than Rust (9.84 ms)
- Workloads with more than 255 shared tags per pair: counters are ubyte and would wrap (the suite caps tags at 100 per post)
- Concurrent or highly optimised settings: the suite's separate tables (D Concurrent v2, D HO) apply, and D HO at 163.89 ms is about 3x slower than Rust HO at 51.55 ms
- Library integration: it is a benchmark program with hard-coded ../posts.json paths and a GC-allocated result array

## How it is fast

Same algorithm as cpp/main.cpp (tag index, uint8 shared-tag counters, 64-byte chunk filter, insertion top-5). The tag index stores pointers to the counter bytes (SharedCount\*), taken once with a bounds-checked &counts[i], so the hot increment loop is ptr[0]++ with no per-increment bounds check, while the C++ entry increments through std::vector::at(). The increment loop is unrolled 11 wide, the 64-byte chunk filter is a plain foreach over a static array that the compiler can auto-vectorize, and counter reset is fused into the top-5 scan (chunk[] = 0 while the line is in cache) instead of a separate memset per post.

## Compared with alternatives

Among the same-suite siblings it has the best single-core total (1.10 s versus Rust 1.23 s and C3 1.28 s), mainly from the 60k round; pick the Rust entry instead for the smallest inputs (9.84 ms at 5k) or if you want the faster Rust HO variant, and treat all three as implementation comparisons rather than language results.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | D runtime and GC (Phobos); asdf 0.7.17 with mir-algorithm 3.21.0 and mir-core 1.6.0 for JSON I/O only |
| **Minimum toolchain** | ldc2 1.41.0 via dub (as measured, -O3 inlining, no -release); other D compilers not tested by the suite |
| **Platforms** | any ldc2 target; measured on x86-64 (AWS c7a.xlarge) without -march |
| **Thread safety** | single-threaded; a separate d_con_v2 variant exists for the multicore table |
| **Drop-in for the baseline** | no |

## Gotchas

- Rule asymmetry behind the speedup: the C++ hot increment was switched from raw pointer arithmetic to taggedPostCount.at() in commit 6104965 ('[cpp] use at', Oct 2023), and issue #350 rejected D's .ptr indexing for the same loop (Oct 2023), yet D v2 (Nov 2023) gets unchecked increments by storing GC-held element pointers in @safe code. It is within the suite's letter, but a C++ entry storing uint8_t\* would remove the same checks.
- C++ and D (v2) rows come from separate container runs (C++ 2026-02-24, D 2026-02-11), and the 20k and 60k posts.json files are regenerated by gen_fake_posts.py with an unseeded random generator for every run, so the two rows were timed on different random datasets of the same distribution; verify.py checks output only on the 5k round.
- Despite the 'SWAR optimization' description in dub.json there is no SWAR; and D still does one associative-array lookup per tag per post in the timed loop, which C++ avoids by pre-resolving tag vectors.
- When fewer than 5 posts share a tag, D leaves the remaining related slots as empty default Posts while C++ fills them with post 0; never triggered by the suite's data but the outputs differ in that edge case.

## Known shortcomings

- The win comes from implementation tricks (counter pointers dodging .at() checks, an 11-wide unroll, reset fused into the scan) rather than D; rows from separate runs with the CPU model and clang version unstated (ldc2 1.41.0 -O3, bounds checks on).
- Harness flaw: the rules treated C++ and D differently. The C++ hot increment moved from a raw pointer to .at() in commit 6104965 (October 2023) and issue #350 rejected D .ptr indexing in the same loop, yet D v2 skips the per-increment bounds check anyway by storing GC-held SharedCount\* pointers in @safe code; C++ could do the same, so the win is implementation, not language. The 20k and 60k posts.json are regenerated each run with unseeded random, so the C++ and D rows were timed on different datasets in separate runs; verify.py checks the 5k round only. The repo is now served as zupat/related_post_gen.

## Caveats and trade-offs

Timed region on both sides is 'Processing time (w/o IO)': the clock starts after JSON parsing and stops before JSON output, so asdf vs nlohmann/json does not enter the table numbers. Despite the 'SWAR optimization' label in dub.json, d_v2/source/app.d runs the same algorithm as cpp/main.cpp (tag index, uint8 shared-tag counters, 64-byte chunk filter, insertion top-5); the differences are implementation tricks: the tag index stores pointers to the counters so the hot increment loop has no index bounds check (C++ uses std::vector::at() there), increments are unrolled 11 wide, and counter reset is fused into the top-5 scan instead of a separate memset; D still does an associative-array lookup per tag per post, which C++ avoids. Both sides keep bounds checks elsewhere (suite rule). C++ and D (v2) rows come from separate runs (results committed 2026-02-24 and 2026-02-11) on the same VM type; CPU model (c7a.xlarge) and clang version not stated; the C++ timer has 1 ms resolution. Community-written implementations; the plain D entry (2.88 s) is slower than C++. [retier] The rules treated C++ and D differently: the C++ hot increment moved from a raw pointer to .at() in commit 6104965 and issue #350 rejected D .ptr indexing in the same loop, yet D v2 skips the per-increment bounds check by storing GC-held SharedCount\* pointers in @safe code (C++ could do the same). The 20k and 60k posts.json are regenerated each run with unseeded random, so the C++ and D rows were timed on different datasets in separate runs; verify.py checks the 5k round only. The repo is now served as zupat/related_post_gen.

Community-submitted implementations in a prescribed task; each language uses its own JSON library, so results mix language, library and algorithm-variant effects.

## Maintenance

The suite (now served as zupat/related_post_gen, 500 stars, MIT) is maintained, with C++ results refreshed 2026-02-24, but the d_v2 directory has had no commits since Feb 2024; it is a copyable reference pattern, not a maintained library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** The README single-core table has the D (v2) row (12.06 ms, 122.21 ms, 961.08 ms, total 1.10 s) against C++ (12.20 ms, 164.33 ms, 1.39 s, total 1.57 s), backed by raw_results_d2.md and raw_results_cpp.md; code and flags are public, but the CPU model and clang version are not stated and the suite gives no mechanism, so the wave-14 cap keeps it at C.
- **Retiered** C to D: Enricher: the suite forced C++ onto checked .at() indexing and rejected D's .ptr indexing, yet D v2 skips the per-increment bounds check through GC-held pointers in @safe code, and the C++ and D rows were timed on different unseeded datasets in separate runs; asymmetric rules on a cross-run table: C to D.
- **Verifier notes:** Numbers match the README and raw results. Corrections: same_algorithm is true (the 'SWAR' label covers no algorithm change), the D compiler is ldc2 1.41.0 with -O3 and bounds checks on, so same_opt_level is true; JSON is outside the timed region. Shortcoming: the win is implementation-level (pointer-based counter updates that dodge the bounds checks the C++ .at() code pays, fused reset), not a language mechanism stated by the source; separate runs, CPU model and clang version unstated.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-28 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/readme.md>
  - <https://github.com/jinyus/related_post_gen>
  - <https://github.com/jinyus/related_post_gen/commits/main>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/run.sh>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/extract_results.dart>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/cpp/main.cpp>
  - <https://github.com/jinyus/related_post_gen/commits/main/cpp/main.cpp>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/dockerfiles/base.Dockerfile>
  - <https://github.com/jinyus/related_post_gen/tree/main/dockerfiles>
  - <https://github.com/jinyus/related_post_gen/tree/main/results>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/results/raw_results_cpp.md>
  - <https://github.com/jinyus/related_post_gen/commits/main/results/raw_results_cpp.md>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/setup.md>
  - <https://github.com/jinyus/related_post_gen/tree/main/d_v2>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/d_v2/dub.json>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/d_v2/dub.selections.json>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/d_v2/source/app.d>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/dockerfiles/d.Dockerfile>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/results/raw_results_d2.md>
  - <https://github.com/jinyus/related_post_gen/commits/main/results/raw_results_d2.md>
  - <https://raw.githubusercontent.com/dlang/dub/master/source/dub/compilers/ldc.d>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/readme.md>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/run.sh>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/d_v2/source/app.d>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/d_v2/dub.json>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/d_v2/dub.selections.json>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/cpp/main.cpp>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/cpp/main_con.cpp>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/d_con_v2/source/app.d>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/d/source/app.d>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/d/dub.json>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/dockerfiles/d.Dockerfile>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/dockerfiles/base.Dockerfile>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/results/raw_results_d2.md>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/results/raw_results_cpp.md>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/setup.md>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/verify.py>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/gen_fake_posts.py>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/docker_start.sh>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/extract_results.dart>
  - <https://github.com/jinyus/related_post_gen>
  - <https://github.com/jinyus/related_post_gen/commits/main/d_v2>
  - <https://github.com/jinyus/related_post_gen/commits/main/cpp/main.cpp>
  - <https://github.com/jinyus/related_post_gen/commit/a3a1cf17b1c64ccf7782ffd66dd59f1c41d1b86a>
  - <https://github.com/jinyus/related_post_gen/commit/7cbabaf4010d5dcb2ed727d6f4d7d09013590999>
  - <https://github.com/jinyus/related_post_gen/commit/610496503a80ffc7c069a2569a68cbd4c6acd0ec>
  - <https://github.com/jinyus/related_post_gen/issues?q=is%3Aissue+bounds>
  - <https://github.com/jinyus/related_post_gen/issues/350>
  - <https://github.com/jinyus/related_post_gen/issues/159>
  - <https://github.com/zupat/related_post_gen/commits/main>
  - <https://github.com/zupat/related_post_gen/pulls>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:d/jinyus/related_post_gen#related-posts`) · [data/wave14/enrich/raw/lang_d_jinyus_related_post_gen_related_posts.json](../../../data/wave14/enrich/raw/lang_d_jinyus_related_post_gen_related_posts.json) (enrichment confidence 0.75)

</details>
