# C3 (related_post_gen suite)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C3` · `MIT` · 🟢 active

> C3 entry of the related_post_gen benchmark: same top-5 related-posts algorithm as the C++ entry, about 1.23x faster single-core.

| | |
|---|---|
| **Beats** | C++ solution of the same suite (clang++ -O3 -std=c++20, nlohmann/json for JSON) |
| **Claimed result** | Single-core total: c3 1.28 s vs C++ 1.57 s (about 1.23x faster, derived from page data); 60k posts 1.13 s vs 1.39 s; 5k posts 10.50 ms vs 12.20 ms. |
| **Workload** | Given posts with tags, compute the top 5 related posts per post by shared tag count (read JSON, tag index, count, sort, write JSON); 5k, 20k and 60k posts; single core; no FFI, unsafe, or single-thread SIMD allowed. |
| **Metric** | latency |
| **Hardware** | AWS c7a.xlarge (4 vCPU, 8 GB RAM), Ubuntu 24.04; CPU model not stated |
| **Compiler and flags** | c3c compile related.c3 json.c3 -O3 (run.sh run_c3; c3c v0.7.9 per dockerfiles/c3.Dockerfile). In c3c v0.7.9 (src/build/builder.c) -O3 means LLVM O2 pipeline, safety checks OFF (no runtime bounds checks), single module, loop/SLP vectorisation on. C++: clang++ -O3 -std=c++20 -I./include main.cpp (run.sh run_cpp), clang from the unpinned Arch Linux base image (dockerfiles/base.Dockerfile), no -march or LTO. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Adoption** | 500 stars (suite repo) |
| **Last commit** | 2026-02-24 |
| **Links** | [repository](https://github.com/jinyus/related_post_gen) · [benchmark](https://raw.githubusercontent.com/jinyus/related_post_gen/main/readme.md) |

## Verdict

The suite README's single-core table, from an AWS c7a.xlarge (4 vCPU, 8 GB, Ubuntu 24.04; CPU model not stated), gives C3 (c3c 0.7.9 -O3) mean processing times of 10.50 ms, 141.00 ms and 1.13 s for 5k, 20k and 60k posts against C++ (clang++ -O3 -std=c++20 from an unpinned Arch Linux image, nlohmann/json) at 12.20 ms, 164.33 ms and 1.39 s, totals 1.28 s and 1.57 s (about 1.23x). JSON is excluded from both timings; 10 runs at 5k and 3 runs each at 20k and 60k, and the C3 raw results (committed 2026-02-11) and C++ raw results come from separate runs.

## Use it when

- As evidence that C3 compiled through LLVM reaches C++-class speed on a scalar, cache-resident counting loop, when you read it together with the safety-off caveat.
- As a compact reference for porting the suite's tag-index, uint8 counter and blocked top-5 technique to C3 or C: under 250 lines, MIT-licensed.
- When comparing C3 against other systems languages in the same suite and harness, single-threaded and with JSON excluded from the timed region.

## Skip it when

- As proof that C3 beats C++ at equal safety: the C3 binary runs with runtime checks off, which the suite's own rules forbid, while the C++ baseline keeps them; no number exists for a rule-compliant C3 build (c3c -O1 keeps safety checks at the same LLVM optimisation level).
- As a JSON writer for real data: titles, tags and ids are written without escaping, so any quote, backslash or control character produces invalid JSON.
- Multi-core work: there is no concurrent C3 entry; the suite's multicore table is led by D and C++ concurrent versions.
- As a margin at 5k posts: both programs report integer milliseconds, so 10.50 ms versus 12.20 ms is close to the timer's resolution.

## How it is fast

The algorithm is the same as the C++ entry: a tag-to-post-index map, a uint8 shared-tag counter per post that is zeroed and refilled for every post, a 64-byte-block 'any count above the current minimum' pre-check, and insertion into a fixed top-5 array. The difference is the build: c3c -O3 sets SAFETY_OFF in c3c 0.7.9's builder.c, so the counting and top-5 loops run without bounds checks, while the C++ entry indexes with std::vector::at() in the same loops. With 4-5 of 28 tags per post, the 60k run does about 2.6 billion counter increments (derived from gen_fake_posts.py parameters), so a compare-and-branch per increment is a plausible source of most of the gap; the C3 side actually does more hashing (has_key/set/get_ref while indexing and a map get per tag per post), which is negligible at this scale.

## Compared with alternatives

In the same suite table the Rust entry (1.23 s total) and D (v2) (1.10 s) are faster than C3 (1.28 s) against the same C++ baseline; whether those builds keep runtime checks was not checked here, so treat all three as same-harness language rows and cite C3 only for C3-specific questions. The C3 compiler compile-throughput sibling is a different claim (build speed, not program speed).

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | C3 standard library only (std::collections HashMap and List, std::encoding::json, std::io, std::time::clock) |
| **Minimum toolchain** | c3c 0.7.x (code updated for 0.7.1 in May 2025; the suite's Dockerfile pins c3c 0.7.9) |
| **Platforms** | Linux x86-64 as benchmarked (c3-linux release tarball on an Arch Linux image); other platforms not documented for this program |
| **Thread safety** | Single-threaded program; not applicable |
| **Drop-in for the baseline** | no |

## Gotchas

- Build flags break the suite's rules: run.sh compiles with `c3c compile related.c3 json.c3 -O3`, and in c3c 0.7.9 every level from -O2 up sets safety_level = SAFETY_OFF (no bounds or other runtime checks), while the rules list 'No: Disabling runtime checks (bounds etc)' and the C++ baseline keeps .at() checks in its hot loops. The 1.23x gap is therefore C3-without-checks against C++-with-checks, not a like-for-like language comparison.
- The hand-written JSON output in json.c3 appends raw strings between quotes with no escaping; the suite's Faker-generated titles happen to contain no quotes or backslashes, so verify.py passes, but the 'Be production ready' rule is not met. Output writing is outside the timed region, so this does not change the reported numbers.
- Timed region: both programs start the clock after JSON parsing and stop it before writing, so the README numbers exclude JSON entirely. Whole-process wall time in the raw files tells a different story at 60k posts: C3 1.76-1.79 s and 291 MB peak versus C++ 3.35-3.40 s and 460 MB, mostly nlohmann/json against a hand-rolled writer.
- Both versions fill missing top-5 slots with post index 0 at score 0, so a post with fewer than five tag-sharing posts would list post 0, possibly itself; the generated data (4-5 of 28 tags per post) never triggers it.

## Known shortcomings

- c3c 0.7.9 -O3 turns safety checks off while the C++ side keeps std::vector::at() bounds checks (same_opt_level false); the timed region excludes JSON on both sides; no mechanism given by the source.
- Confirmed from c3c v0.7.9 builder.c: -O2 and up set SAFETY_OFF (runtime checks disabled) while -O1 keeps checks at the same LLVM level, which breaks the suite's rule against disabling runtime checks while the C++ baseline keeps .at() checks; derived from gen_fake_posts.py's parameters, about 2.6e9 counter increments at 60k posts, so a bounds check per increment plausibly explains most of the 1.23x gap. Second flaw: the hand-written JSON writer in json.c3 never escapes strings, failing the 'production ready' rule (outside the timed region, so the numbers are unchanged).

## Caveats and trade-offs

The README table reports each program's own 'Processing time (w/o IO)' (extract_results.dart pTimeRegex), and both cpp/main.cpp and c3/related.c3 start the clock after the JSON is parsed and stop it before the JSON is written, so JSON parsing (nlohmann/json vs the hand-written json.c3) is NOT in the measured numbers; it only shows in the wall-clock 'total' lines of the raw files (60k posts: C++ about 3.35 s, c3 about 1.76 s). The algorithm is the same on both sides (tag-to-post-index map, uint8 shared-tag counters, 64-byte chunk filter, insertion top-5), and C3 even does extra hashing (has_key/set/get_ref per tag when building the index and a map get per tag per post), while C++ resolves each tag's vector once. The main asymmetry is runtime checks: the C++ solution indexes with std::vector::at() in the counting and top-5 loops (bounds checks kept, as the suite's 'no disabling runtime checks' rule requires), while c3c -O3 turns safety checks off entirely, so the C3 build does not keep the bounds checks the rules ask for. C++ and c3 rows come from separate runs (results committed 2026-02-24 and 2026-02-11) on the same VM type; CPU model (c7a.xlarge) and clang version are not stated. Timers have 1 ms resolution on both sides, so the 5k-post margin (10.50 vs 12.20 ms) is near the timer granularity. Community-written implementations; no plain C solution. [retier] c3c v0.7.9 builder.c sets SAFETY_OFF at -O2 and up (runtime checks disabled) while -O1 keeps checks at the same LLVM level, breaking the suite's rule against disabling runtime checks while the C++ baseline keeps .at() checks; at about 2.6e9 counter increments for 60k posts, a bounds check per increment plausibly explains most of the 1.23x gap. The hand-written JSON writer in json.c3 never escapes strings (outside the timed region).

Community-submitted implementations in a prescribed task; each language uses its own JSON library, so results mix language, library and algorithm-variant effects.

## Maintenance

The suite is active (MIT, 500 stars, results refreshed February 2026), but the C3 solution is a one-off contributor submission last changed in May 2025 and built with safety checks off; it is copyable as example code, not a maintained library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** The suite README single-core table has the c3 row (10.50 ms, 141.00 ms, 1.13 s, total 1.28 s) next to the C++ row (12.20 ms, 164.33 ms, 1.39 s, total 1.57 s), and raw_results_c3.md / raw_results_cpp.md back them; code and flags are public, but the CPU model and the clang version are not stated and the suite gives no mechanism, so the wave-14 no-mechanism cap keeps it at C.
- **Retiered** C to D: Enricher: c3c -O2 and up disable runtime checks (SAFETY_OFF) against the suite's rule while the C++ baseline keeps its .at() checks, and a bounds check per increment plausibly accounts for most of the 1.23x; asymmetric checks with no like-for-like measurement: C to D.
- **Verifier notes:** Numbers match the README row and the raw results. Correct the JSON caveat: the timed region excludes JSON on both sides, so the gap is not JSON-library cost. Shortcoming: the C3 build runs with safety checks off (c3c -O3) against a bounds-checked C++ (.at()) baseline, which breaks the suite's own no-disabling-runtime-checks rule and makes same_opt_level false; separate runs, CPU model and clang version unstated, no mechanism from the source.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
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
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/c3/related.c3>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/c3/json.c3>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/dockerfiles/c3.Dockerfile>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/results/raw_results_c3.md>
  - <https://github.com/jinyus/related_post_gen/commits/main/results/raw_results_c3.md>
  - <https://raw.githubusercontent.com/c3lang/c3c/v0.7.9/src/build/build_options.c>
  - <https://raw.githubusercontent.com/c3lang/c3c/v0.7.9/src/build/builder.c>
  - <https://raw.githubusercontent.com/c3lang/c3c/v0.7.9/src/compiler/llvm_codegen.c>
- **Sources the enricher read:**
  - <https://github.com/jinyus/related_post_gen>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/readme.md>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/setup.md>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/run.sh>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/extract_results.dart>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/verify.py>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/gen_fake_posts.py>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/c3/related.c3>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/c3/json.c3>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/cpp/main.cpp>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/dockerfiles/c3.Dockerfile>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/dockerfiles/base.Dockerfile>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/results/raw_results_c3.md>
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/results/raw_results_cpp.md>
  - <https://github.com/jinyus/related_post_gen/commits/main/c3>
  - <https://github.com/jinyus/related_post_gen/commits/main/results/raw_results_c3.md>
  - <https://github.com/jinyus/related_post_gen/issues?q=c3>
  - <https://github.com/jinyus/related_post_gen/pulls?q=is%3Apr+c3>
  - <https://github.com/jinyus/related_post_gen/pull/531>
  - <https://raw.githubusercontent.com/c3lang/c3c/v0.7.9/src/build/builder.c>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:c3/jinyus/related_post_gen#related-posts`) · [data/wave14/enrich/raw/lang_c3_jinyus_related_post_gen_related_posts.json](../../../data/wave14/enrich/raw/lang_c3_jinyus_related_post_gen_related_posts.json) (enrichment confidence 0.75)

</details>
