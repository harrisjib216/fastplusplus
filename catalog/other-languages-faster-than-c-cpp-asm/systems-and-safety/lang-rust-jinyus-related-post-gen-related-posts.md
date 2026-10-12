# Rust (related_post_gen suite)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust` · `MIT` · 🟢 active

> Community Rust solution to the related-posts benchmark, about 1.28x faster than the suite's C++ solution on one core.

| | |
|---|---|
| **Beats** | C++ solution of the same suite (clang++ -O3 -std=c++20, nlohmann/json for JSON) |
| **Claimed result** | Single-core table on AWS c7a.xlarge, measuring processing time without JSON I/O: Rust 9.84 ms, 124.59 ms and 1.10 s (5k/20k/60k posts, total 1.23 s) versus C++ 12.20 ms, 164.33 ms and 1.39 s (total 1.57 s). That is about 1.28x on the total and 1.26x at 60k posts (derived from page data). D (v2) is fastest at 1.10 s total and C3 takes 1.28 s. In the multicore table C++ Concurrent (402.33 ms total) beats Rust Concurrent (489.91 ms), so the Rust lead holds only on a single core. The raw files results/raw_results_rust.md and raw_results_cpp.md match the table. At 60k posts their whole-process wall times, including JSON I/O, are 1.27-1.32 s for Rust and 3.35-3.40 s for C++. |
| **Workload** | Given posts with tags, compute the top 5 related posts per post by shared tag count (read JSON, tag index, count, sort, write JSON); 5k, 20k and 60k posts; single core; no FFI, unsafe, or single-thread SIMD allowed. |
| **Metric** | latency |
| **Hardware** | AWS c7a.xlarge (4 vCPU, 8 GB RAM) with an Ubuntu 24.04 host, per the README. The solutions run in an archlinux:base Docker image. The page does not state the CPU model. |
| **Compiler and flags** | C++: clang++ -O3 -std=c++20 -I./include main.cpp (run.sh run_cpp). It is a single translation unit with header-only nlohmann/json, so the missing -flto changes little. Neither side uses -march; the suite rules forbid hardware targeting. Rust: cargo build --release with the rust/Cargo.toml release profile lto = "fat", codegen-units = 1, panic = "abort" (default opt-level 3), plus hashbrown 0.14.3, aligned-vec 0.5 and serde_json. Compiler versions are not stated: the Docker image is archlinux:base with an unpinned pacman clang and rustup stable (dockerfiles/base.Dockerfile, dockerfiles/rust.Dockerfile). |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | no |
| **Adoption** | 500 stars (suite repo) |
| **Last commit** | 2026-02-24 |
| **Links** | [repository](https://github.com/zupat/related_post_gen) · [benchmark](https://raw.githubusercontent.com/zupat/related_post_gen/main/readme.md) |

## Verdict

On an AWS c7a.xlarge (CPU model not stated), mean processing time without JSON I/O was 9.84 / 124.59 / 1,100 ms for 5k / 20k / 60k posts (10, 3 and 3 runs) for Rust built by cargo --release with fat LTO, codegen-units 1 and panic=abort (stable toolchain, version unstated), versus 12.20 / 164.33 / 1,393 ms for the C++ entry built with Arch Linux clang++ -O3 -std=c++20 (no LTO, no -march, clang version unstated): about 1.28x on the totals (derived from page data). Whole-process times including JSON are 1.27-1.32 s versus 3.35-3.40 s at 60k posts.

## Use it when

- As a reference pattern for sparse co-occurrence top-k (posts by tags, items by features) where one row of u8 counters fits in L1/L2: the measured sizes are 5k to 60k items
- Single-core batch jobs with 4-5 tags per item from a small vocabulary (the generator draws from 28 tags), the measured shape
- When end-to-end memory and JSON time matter too: the raw results show 29 MB peak RSS and 1.27-1.32 s whole-process at 60k posts versus 460 MB and 3.35-3.40 s for the C++ entry (nlohmann/json DOM)
- Small inputs: at 5k posts it has the suite's best single-core time (9.84 ms versus D v2 12.06 ms and C++ 12.20 ms)

## Skip it when

- As evidence that Rust beats C++: the C++ entry is a port of this algorithm held to .at() everywhere and a separate memset, and nothing in the Rust code (u8 counters, chunk scan, fused zeroing) is beyond standard C++
- Multicore runs: C++ Concurrent (402.33 ms total) beats Rust Concurrent (489.91 ms), and the separate Rust HO entry (51.55 ms) uses specialised data structures
- Items that can share more than 255 tags: counters are u8 and would wrap (the suite caps tags at 100 per post)
- Library integration: hard-coded ../posts.json and ../related_posts_rust.json paths, unwrap() on parse errors, and no API
- Large vocabularies with long tag lists per item, where the per-post counter scan (O(n) per post, O(n^2) total) dominates; that shape was not measured

## How it is fast

Same algorithm as cpp/main.cpp, which was ported from the Rust code in Sept 2024 ('copy rust algorithm, process every cacheline'): per-tag Vec&lt;u32&gt; of post indices, a u8 shared-tag counter per post, a scan in 64-byte chunks that skips a chunk unless some count exceeds the running 5th-best, and insert-and-bubble top-5. The counter buffer is a 64-byte-aligned AVec padded to a multiple of 64, the chunk scan uses slice iterators (no per-element bounds checks), and since Feb 2026 each chunk is zeroed right after it is scanned instead of a whole-array fill. The C++ entry runs the same steps with std::vector::at() on every counter access, a full memset per post and std::unordered_map; the suite publishes no profile, so which difference carries the gap is not documented.

## Compared with alternatives

Among the same-suite siblings, pick it for the smallest inputs (fastest at 5k posts, 9.84 ms) or a Rust codebase; D (v2) is faster at 60k posts (961.08 ms versus 1.10 s) and on the total (1.10 s versus 1.23 s), and C3 trails at 1.28 s. Treat all three as implementation comparisons, not language results.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | hashbrown 0.14.3 (ahash 0.8.7 default hasher), aligned-vec 0.5.0; serde 1 and serde_json 1.0.111 for JSON I/O only |
| **Minimum toolchain** | Rust 2021 edition; usize::next_multiple_of needs Rust 1.73+ (inferred from the API used). The suite builds with rustup stable, version unstated |
| **Platforms** | any Rust target; measured on x86-64 (AWS c7a.xlarge) with no target-cpu flag |
| **Thread safety** | single-threaded program; a separate rust_con (Rayon) variant exists for the multicore table |
| **Drop-in for the baseline** | no |

## Gotchas

- The Rust and C++ rows come from separate container runs (Rust raw results committed 2026-02-11, C++ refreshed 2026-02-24), and docker_start.sh regenerates the 20k and 60k posts.json with gen_fake_posts.py, which calls random.sample without a seed, so the two rows were timed on different random datasets of the same distribution; verify.py checks output only on the 5k round (fixed posts.json).
- The lead predates the fused chunk-zeroing commit (a9d2d27, Feb 2026): in the May 2025 run (Ubuntu 22.04 host), when Rust still zeroed the whole array after each scan like C++'s memset, Rust was 1.30 s versus C++ 1.72 s at 60k posts (about 1.32x, derived from page data). So the gap does not come from that trick, and the suite has not isolated what does (candidates are .at() in the C++ scan and insert loops, unordered_map, and the C++ build without LTO).
- The C++ timer truncates to whole milliseconds (duration_cast&lt;milliseconds&gt;; raw values are 12 or 13 ms at 5k posts), which biases the C++ 5k figure low by up to 1 ms, so if anything Rust's 5k lead is understated. The Rust hot increment still uses bounds-checked indexing, as the suite's no-unchecked rule requires.
- If fewer than 5 other posts share a tag, the unfilled top-5 slots stay (0, 0) and point at post 0, which can be the post itself; the C++ entry behaves the same and the suite's data never triggers it.

## Known shortcomings

- The real gap is a separate memset pass and .at() bounds checks on the C++ side against Rust's fused chunk zeroing on an aligned buffer (JSON I/O sits outside the timed region); C++ Concurrent beats Rust Concurrent (402 vs 490 ms); compiler versions and CPU model unstated. Repo moved to zupat/related_post_gen.
- Cross-run comparison: the Rust and C++ rows come from separate container runs (Rust raw results committed 2026-02-11, C++ refreshed 2026-02-24), and docker_start.sh regenerates the 20k and 60k posts.json with an unseeded gen_fake_posts.py, so the two rows were timed on different random datasets; verify.py checks output only on the 5k round. The lead predates the fused chunk-zeroing commit a9d2d27 (the May 2025 run already had Rust 1.30 s vs C++ 1.72 s at 60k), the C++ timer truncates to whole milliseconds, which biases the 5k figure toward C++, and the suite never isolated the mechanism. Retiered to D like the suite's C3 and D rows.

## Caveats and trade-offs

The suite gives no mechanism. The timed region ('Processing time (w/o IO)') excludes JSON parsing and writing on both sides, so nlohmann/json versus serde_json does not affect the table. It does dominate whole-process time: C++ 3.35 s versus Rust 1.27 s at 60k posts, with 460 MB versus 29 MB RSS. Inside the timed region both programs run the same algorithm: per-tag lists of post indices, uint8 shared-tag counters, a scan in 64-entry chunks with a running minimum, and 5-slot top-k insertion. The tuning differs. Rust zeroes each 64-byte chunk right after scanning it, on a 64-byte-aligned counter buffer padded to a multiple of 64. C++ memsets the whole counter array before each post and uses bounds-checked std::vector::at() for every counter access in the hot loops. The tag index is hashbrown in Rust and std::unordered_map&lt;std::string, unique_ptr&lt;vector&lt;int&gt;&gt;&gt; in C++; Rust re-hashes each tag string per post, while C++ caches per-post pointers. The suite has no C solution. The solutions are community-written and were run on a cloud VM (10 runs at 5k posts, 3 at 20k and 60k) with compiler versions and CPU model unstated. Zig (1.93 s) and Odin (2.00 s) are slower than C++. The Rust HO row (51.55 ms) uses specialised data structures and is excluded. The repository now lives at zupat/related_post_gen, and the jinyus URL redirects there. [retier] Enricher: the Rust and C++ rows come from separate container runs (Rust raw results committed 2026-02-11, C++ refreshed 2026-02-24), and docker_start.sh regenerates the 20k and 60k posts.json with an unseeded gen_fake_posts.py, so the rows were timed on different random datasets; verify.py checks output only on the 5k round. The lead predates the fused chunk-zeroing commit a9d2d27 (the May 2025 run already had Rust 1.30 s vs C++ 1.72 s at 60k), the C++ timer truncates to whole milliseconds, and the suite never isolated the mechanism.

Community-submitted implementations in a prescribed task; each language uses its own JSON library, so results mix language, library and algorithm-variant effects.

## Maintenance

The suite (served as zupat/related_post_gen after a transfer from jinyus, 500 stars, MIT) is maintained, with Rust results from 2026-02-11 after a Feb 2026 code change; it is a copyable reference pattern, not a maintained library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** The benchmark code (cpp/main.cpp, rust/src/main.rs, run.sh) and flags are public, but compiler versions (unpinned Arch clang, rustup stable) and the CPU model (only the c7a.xlarge instance type) are not stated, so it is not A. The two community programs differ in tuning details and the suite states no mechanism, so it stays at C as recorded.
- **Retiered** C to D: Downgraded from C to D: cross-run comparison. The Rust and C++ rows come from separate container runs (2026-02-11 and 2026-02-24) on different unseeded random datasets for the 20k and 60k rounds, and the C++ timer truncates to whole milliseconds; same ruling as the suite's C3 and D rows.
- **Verifier notes:** The numbers match the readme table and the raw result files. Metadata checks out: MIT, 500 stars, last commit 2026-02-24, active. The repository was transferred to zupat/related_post_gen, so the orchestrator may want a repo_url override. The record's caveat blamed the gap on nlohmann/json versus serde_json, but JSON I/O sits outside the timed region; the real differences are C++ memset-then-scan with .at() bounds checks against Rust's fused chunk zeroing on an aligned buffer. same_opt_level is corrected to true because the C++ side is one TU at -O3, so Rust's fat LTO adds little. C++ wins the multicore table.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-29 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/jinyus/related_post_gen/main/readme.md>
  - <https://github.com/jinyus/related_post_gen>
  - <https://github.com/jinyus/related_post_gen/commits/main>
  - <https://github.com/zupat/related_post_gen/tree/main/dockerfiles>
  - <https://github.com/zupat/related_post_gen/tree/main/results>
  - <https://raw.githubusercontent.com/zupat/related_post_gen/main/run.sh>
  - <https://raw.githubusercontent.com/zupat/related_post_gen/main/cpp/main.cpp>
  - <https://raw.githubusercontent.com/zupat/related_post_gen/main/rust/src/main.rs>
  - <https://raw.githubusercontent.com/zupat/related_post_gen/main/rust/Cargo.toml>
  - <https://raw.githubusercontent.com/zupat/related_post_gen/main/dockerfiles/base.Dockerfile>
  - <https://raw.githubusercontent.com/zupat/related_post_gen/main/dockerfiles/rust.Dockerfile>
  - <https://raw.githubusercontent.com/zupat/related_post_gen/main/results/raw_results_cpp.md>
  - <https://raw.githubusercontent.com/zupat/related_post_gen/main/results/raw_results_rust.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/zupat/related_post_gen/main/readme.md>
  - <https://raw.githubusercontent.com/zupat/related_post_gen/main/run.sh>
  - <https://raw.githubusercontent.com/zupat/related_post_gen/main/docker_start.sh>
  - <https://raw.githubusercontent.com/zupat/related_post_gen/main/cpp/main.cpp>
  - <https://raw.githubusercontent.com/zupat/related_post_gen/main/rust/src/main.rs>
  - <https://raw.githubusercontent.com/zupat/related_post_gen/main/rust/Cargo.toml>
  - <https://raw.githubusercontent.com/zupat/related_post_gen/main/rust/Cargo.lock>
  - <https://raw.githubusercontent.com/zupat/related_post_gen/main/dockerfiles/rust.Dockerfile>
  - <https://raw.githubusercontent.com/zupat/related_post_gen/main/dockerfiles/base.Dockerfile>
  - <https://raw.githubusercontent.com/zupat/related_post_gen/main/results/raw_results_rust.md>
  - <https://raw.githubusercontent.com/zupat/related_post_gen/main/results/raw_results_cpp.md>
  - <https://raw.githubusercontent.com/zupat/related_post_gen/main/verify.py>
  - <https://raw.githubusercontent.com/zupat/related_post_gen/main/gen_fake_posts.py>
  - <https://raw.githubusercontent.com/zupat/related_post_gen/6c556df/results/raw_results_rust.md>
  - <https://raw.githubusercontent.com/zupat/related_post_gen/6c556df/results/raw_results_cpp.md>
  - <https://raw.githubusercontent.com/zupat/related_post_gen/6c556df/readme.md>
  - <https://github.com/zupat/related_post_gen/commits/main/rust>
  - <https://github.com/zupat/related_post_gen/commits/main/cpp/main.cpp>
  - <https://github.com/zupat/related_post_gen/commits/main/results/raw_results_rust.md>
  - <https://github.com/zupat/related_post_gen/commits/main/results/raw_results_cpp.md>
  - <https://github.com/zupat/related_post_gen/commit/a9d2d27>
  - <https://github.com/zupat/related_post_gen/commit/a3a1cf17b1c64ccf7782ffd66dd59f1c41d1b86a>
  - <https://github.com/zupat/related_post_gen/commit/7cbabaf4010d5dcb2ed727d6f4d7d09013590999>
  - <https://github.com/jinyus/related_post_gen/commit/610496503a80ffc7c069a2569a68cbd4c6acd0ec>
  - <https://github.com/zupat/related_post_gen/issues?q=is%3Aissue+cpp>
  - <https://github.com/zupat/related_post_gen/issues/360>
  - <https://github.com/zupat/related_post_gen/issues/203>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:rust/jinyus/related_post_gen#related-posts`) · [data/wave14/enrich/raw/lang_rust_jinyus_related_post_gen_related_posts.json](../../../data/wave14/enrich/raw/lang_rust_jinyus_related_post_gen_related_posts.json) (enrichment confidence 0.7)

</details>
