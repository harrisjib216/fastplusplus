# ckmeans (Rust optimal 1-D k-means) vs Ckmeans.1d.dp C++

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `BlueOak-1.0.0` · 🟢 active

> Rust crate for optimal 1-D k-means (Wang and Song's Ckmeans); 1.6-2.1x faster than the Ckmeans.1d.dp C++ code on an M2 Pro.

| | |
|---|---|
| **Beats** | Ckmeans.1d.dp C++ implementation (kmeans_1d_dp, methods 'linear' (default) and 'loglinear'; the code behind the R package and the ckmeans-1d-dp Python package), vendored in bench_cpp |
| **Claimed result** | bench_cpp/README.md (Criterion point estimates, ms, one run of the full suite, Apple M2 Pro): Uniform(1,3) n=110,000 k=5 rust_indices 13.2 / rust_optimal 14.5 vs cpp_linear 26.0 / cpp_loglinear 25.3; k=20 49.7 / 52.7 vs 105.3 / 90.7; n=1,000,000 k=5 126.7 / 142.9 vs 254.9 / 249.8; k=20 513.5 / 556.1 vs 995.4 / 940.5; Uniform(0,1000) n=110,000 k=3 7.6 / 9.1 vs 16.5 / 16.1, k=50 114.4 / 120.0 vs 256.0 / 193.0; bimodal k=7 16.0 / 17.6 vs 31.3 / 28.7; BIC selection of k in 1..9 rust_optimal 26.7 vs 54.5 / 50.9 (n=110,000) and 263.1 vs 510.2 / 515.9 (n=1,000,000). The slowest Rust call (rust_optimal, which does the BIC step) against the faster C++ method is 1.6x to 1.9x faster in every row; rust_indices against the faster C++ method is 1.7x to 2.1x; the widest gap, fastest Rust against slowest C++, is 2.3x (Uniform(0,1000) k=30 and k=50) (all derived from page data). PR #41 (merged 2026-10-01) said 'Rust is 23 to 48 % faster than the C++ code in all cases'; that statement predates the 2026-10-02 commits that vectorised the split-point search, sped up the BIC step and replaced the table (a37c045). |
| **Workload** | Optimal 1-D k-means (dynamic programming) on seeded random inputs: Uniform(1,3) and Uniform(0,1000) at n = 110,000 and 1,000,000, k from 3 to 50, a bimodal normal input, and BIC selection of k in 1..9; Criterion point estimates, one run of the full suite. |
| **Metric** | latency |
| **Hardware** | Apple M2 Pro |
| **Compiler and flags** | Rust: rustc 1.99.0, cargo bench with the bench profile inheriting bench_cpp/Cargo.toml [profile.release] lto = true, codegen-units = 1 (opt-level 3), no -C target-cpu; split-point search dispatched at run time through fearless_simd (NEON on aarch64). C++: Apple clang 17.0.0 via the cc crate in bench_cpp/build.rs with opt_level(3) (-O3), -DNDEBUG, -std=c++11, warnings off, no LTO, no -march; the 11 Ckmeans.1d.dp sources that the ckmeans-1d-dp Python package compiles plus a C shim (cpp/shim.cpp). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Why it wins** | Source (README, 'Implementation' table): flat contiguous matrix for cache locality, stack-based divide-and-conquer column fill with a single-pass inner loop that computes the sum of squares once per candidate (the two-pointer approach computes it twice), pre-allocated stack, and a vectorised split-point search with run-time SIMD selection. |
| **Adoption** | 12 stars, 1 fork; crates.io 'ckmeans' 23,737 downloads (1,409 recent), version 2.2.0; also published to npm as @urschrei/ckmeans (WASM) |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/urschrei/ckmeans) · [benchmark](https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/bench_cpp/README.md) |

## Verdict

bench_cpp/benches/compare.rs (Criterion, seeded inputs, one full-suite run on an Apple M2 Pro) times ckmeans 2.2.0 built with rustc 1.99.0 (LTO, codegen-units 1) against the vendored Ckmeans.1d.dp 4.3.6 C++ built with Apple clang 17.0.0 -O3 -DNDEBUG. Both methods are measured: 'linear' (SMAWK, the R/Python default) and 'loglinear'. ckmeans_indices is 1.69x to 2.12x faster than the faster C++ method in every row, and ckmeans_optimal, which also does the BIC step, is 1.61x to 1.88x faster. BIC selection over k = 1..9 takes 26.7 ms against 50.9 ms at n = 110,000 (1.91x) and 263.1 ms against 510.2 ms at n = 1,000,000 (1.94x). All ratios are derived from page data.

## Use it when

- Exact 1-D clustering or class breaks (choropleth bins, histogram binning, natural-breaks style classing) on f64 data from about 10^4 to 10^6 values with k up to a few dozen
- Choosing the number of groups automatically: ckmeans_optimal's BIC picks the same k as the R package (Rust reports the negated BIC values)
- Rust, C (FFI) or browser/Node (WASM) projects that want Ckmeans.1d.dp results without linking LGPL C++ or embedding R or Python
- Replacing heuristic Jenks or iterative k-means in 1-D when you need a guaranteed optimum at comparable or lower cost

## Skip it when

- Large n times k: both DP matrices are dense k x n (an f64 and a usize per cell, 16 bytes), so 1,000,000 values at k = 50 need about 800 MB plus a sorted copy (derived from FlatMatrix::new)
- When you need per-value labels in input order, weights, the L1 criterion or k above 255 (k is a u8): use Ckmeans.1d.dp, which offers weighted, L1 and L2Y variants
- Multi-dimensional data: this is univariate only
- If you are staying in R or Python: calling Ckmeans.1d.dp with method 'loglinear' instead of the default 'linear' (SMAWK) was up to 1.33x faster in this same table (Uniform(0,1000), k = 50), with no language switch
- Projects that need upstream contributions accepted: issue #48 (2026-10-04) says the repo no longer accepts pull requests, and the Cargo badge says passively-maintained

## How it is fast

It fills the k x n dynamic-programming matrices with the divide-and-conquer optimisation, the same bounds as the C++ 'loglinear' fill: the optimal split is monotone in i and in k, so each cell searches only between neighbouring split points. Each cell's search is a single pass that computes the segment cost once per candidate, where the C++ two-pointer loop evaluates two candidates per step. Long ranges (16 or more candidates) keep four independent running minima so the loop vectorises, and the column loop is compiled per SIMD level and picked at run time with fearless_simd (AVX2 or SSE2 on x86-64, NEON on aarch64). The matrices are flat contiguous arrays, the divide-and-conquer stack is preallocated and reused, and the input is scaled by a power of two and shifted by its median before the f64 prefix sums are built.

## Compared with alternatives

No catalogued sibling does 1-D clustering; the systems-and-safety siblings (sorts, file tools, compilers) solve other problems, so the choice is only between this crate and the Ckmeans.1d.dp baseline itself.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | fearless_simd 1.0, num-traits, libc, wasm-bindgen and js-sys (the last two are unconditional dependencies, and the wasm module is compiled on native targets as well); optional cbindgen for the C header |
| **Minimum toolchain** | Rust 1.89 (edition 2024), from crate 2.2.0 |
| **Platforms** | any Rust target; run-time AVX2/SSE2 selection on x86-64, NEON on aarch64, scalar elsewhere; wasm32 through wasm-bindgen; C FFI cdylib on non-wasm targets |
| **Thread safety** | Not documented. The functions take a slice and allocate their own matrices with no global state (from the source), so concurrent calls are independent. The FFI entry point wraps the call in catch_unwind and reports errors through a CkmeansStatus out-parameter. |
| **Drop-in for the baseline** | partial — same objective, same clusters and same BIC-selected k as kmeans_1d_dp() for unweighted L2 input, but a different API: no input-order labels, BIC sign reversed, k limited to u8, and no weighted or L1 modes |

## Gotchas

- Rust does more dynamic-programming work than the C++ in the measured calls, and it still wins. The C++ fills only the final cell of the last column (EWL2_dynamic_prog.cpp sets imin = N-1 for q = K-1), while ckmeans' fill_matrices computes the whole last column although backtrack reads only its last entry. At k = 3 that is two full columns against one plus a cell. Two other C++ costs are implementation choices, not language effects: it sorts an index vector through a static-pointer comparator and then gathers, where Rust calls sort_unstable_by on the values, and it scatters per-value labels back to input order. Neither was timed separately.
- The C++ baseline's ldouble is typedef'd to double in the vendored precision.h (Ckmeans.1d.dp 4.3.6, commit c960a53), and both sides shift by the median, so precision is matched. The only comparison table is one Criterion run on an Apple M2 Pro (NEON); the x86 AVX2 path was measured only against the crate's own 2.1.0 (CHANGELOG: 22 to 32 percent faster on an AMD EPYC), not against the C++.
- Version history matters: before 2.1.0 (2026-10-01), ckmeans_optimal selected k_max for most inputs, and the selected k and BIC values changed in 2.1.0. Versions 2.0.0, 2.1.0 and 2.2.0 shipped on three consecutive days (2026-09-30 to 2026-10-02). The licence moved from MIT OR Apache-2.0 (up to 1.0.6) to BlueOak-1.0.0 (from 1.2.0).
- Input edge cases: NaN returns NanError. Infinite values give a partition with no optimality guarantee and NaN BIC. A k above the number of distinct values is silently reduced. Integers above 2^53 lose precision in the cost computation. Very wide ranges can be sub-optimal by less than f64 resolution (README 'Numerical Limits').

## Known shortcomings

- Library win (flat matrix, four independent minima, fearless_simd) against scalar SMAWK/divide-and-conquer C++, so not the same algorithm; LTO on the Rust side only; first-party single M2 Pro run; the derived range is 1.6-1.9x (slowest Rust vs fastest C++), not 2.3x; PR #41's '23 to 48%' predates the 2026-10-02 SIMD/BIC commits. BlueOak-1.0.0 is OSI-approved per SPDX 3.29.0.
- No harness flaw found: C++ ldouble equals double, so precision is matched; Rust fills the whole last DP column where C++ fills one cell, so Rust does more work and still wins. The C++ indirect index sort and label scatter are library choices, not language, and are not timed separately. SMAWK 'linear' (the R and Python default) is slower than 'loglinear' in every row, up to 1.33x. Before 2.1.0 ckmeans_optimal picked k_max for most inputs. The licence moved from MIT/Apache to BlueOak; the repo takes no PRs (issue #48); matrices use 16 bytes per value per cluster; no x86 comparison against C++.

## Caveats and trade-offs

Library win, not a language-level claim: the Rust crate and the C++ code solve the same objective and the agreement tests check identical clusters, but the implementations differ (Rust: flat matrix, stack-based divide-and-conquer column fill computing SSQ once per candidate, split-point search with four independent minima vectorised through fearless_simd; C++: SMAWK for 'linear' and scalar divide-and-conquer for 'loglinear'), so the speedup mixes algorithm constant factors, accumulator structure and explicit SIMD. The C++ call does a BIC step with Kmin = Kmax = k (6 to 10 percent of its time) that rust_indices and rust_clusters skip, writes a per-value label array in input order, and is wrapped in a Rust mutex plus an O(n) finiteness check; rust_optimal does the same BIC step and is still 1.6x to 1.9x faster. LTO and codegen-units = 1 apply to the Rust side only (C++ built as a static library without LTO); neither side sets a target CPU. Single run of the suite on one Apple M2 Pro, benchmark written by the crate author; the bench_cpp crate (2026-10-01, 5456a98) and its results were added in October 2026 commits, and PR #41 links a claude.ai/code session. The vendored C++ in bench_cpp/vendor is LGPL-3.0-or-later (benchmark only); the crate itself is BlueOak-1.0.0, which is OSI-approved per the SPDX license list 3.29.0 and includes a patent licence. The repository's Cargo badge says 'passively-maintained'. [retier] C++ ldouble equals double, so precision is matched; Rust fills the whole last DP column where C++ fills one cell. The C++ indirect index sort and label scatter are library choices, not timed separately. SMAWK 'linear' (the R and Python default) is slower than 'loglinear' in every row, up to 1.33x. Licence moved to BlueOak; the repo takes no PRs (issue #48); no x86 comparison against C++.

The vendored C++ code is LGPL-3.0-or-later and the Rust crate is BlueOak-1.0.0. Rust ckmeans_indices returns sorted data plus index ranges rather than per-value labels; the C++ call also returns labels, centres and sizes, and the Rust wrapper needs a mutex because kmeans_1d_dp() sorts through a static pointer. Results are identical to the scalar search (README).

## Maintenance

Single maintainer with a 'passively-maintained' badge and no outside PRs accepted (issue #48), yet active in October 2026 (2.2.0 on 2026-10-02, last commit 2026-10-12). BlueOak-1.0.0 (OSI-approved, permissive) and small enough to vendor; 12 stars, 23,737 crates.io downloads, no crates.io reverse dependencies.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Public benchmark code against the named C++ baseline (bench_cpp/benches/compare.rs, Criterion, seeded inputs; C++ compiled by bench_cpp/build.rs with cc opt_level(3), -DNDEBUG, -std=c++11; Rust bench profile inherits bench_cpp/Cargo.toml [profile.release] lto = true, codegen-units = 1), compilers named (rustc 1.99.0, Apple clang 17.0.0) and CPU named (Apple M2 Pro), so it meets A. First-party run, which the A rubric allows.
- **Verifier notes:** All table numbers match bench_cpp/README.md exactly; the record's derived range was wrong at the top (slowest Rust against the faster C++ method is 1.6x to 1.9x, not up to 2.3x) and the PR #41 '23 to 48 %' quote is stale, both corrected. BlueOak-1.0.0 is OSI-approved (SPDX license-list-data 3.29.0, isOsiApproved true), so usability moves from reference to copyable. Shortcomings to record: library-vs-library win with different accumulator structure and explicit SIMD (same_algorithm false), first-party single run on one laptop, LTO on the Rust side only, benchmark added in October 2026.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `usability`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-86 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/bench_cpp/README.md>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/README.md>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/bench_cpp/build.rs>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/bench_cpp/Cargo.toml>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/bench_cpp/benches/compare.rs>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/bench_cpp/cpp/shim.cpp>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/bench_cpp/src/lib.rs>
  - <https://github.com/urschrei/ckmeans>
  - <https://github.com/urschrei/ckmeans/commits>
  - <https://github.com/urschrei/ckmeans/pull/41>
  - <https://crates.io/api/v1/crates/ckmeans>
  - <https://raw.githubusercontent.com/spdx/license-list-data/main/json/details/BlueOak-1.0.0.json>
  - <https://raw.githubusercontent.com/spdx/license-list-data/main/json/licenses.json>
- **Sources the enricher read:**
  - <https://github.com/urschrei/ckmeans>
  - <https://github.com/urschrei/ckmeans/tree/main/src>
  - <https://github.com/urschrei/ckmeans/commits/main>
  - <https://github.com/urschrei/ckmeans/issues>
  - <https://github.com/urschrei/ckmeans/issues/26>
  - <https://github.com/urschrei/ckmeans/issues/48>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/README.md>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/src/algo.rs>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/src/ffi.rs>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/src/wasm.rs>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/src/errors.rs>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/bench_cpp/README.md>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/bench_cpp/Cargo.toml>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/bench_cpp/build.rs>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/bench_cpp/benches/compare.rs>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/bench_cpp/cpp/shim.cpp>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/bench_cpp/src/lib.rs>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/bench_cpp/vendor/Ckmeans.1d.dp/README.md>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/bench_cpp/vendor/Ckmeans.1d.dp/Ckmeans.1d.dp.cpp>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/bench_cpp/vendor/Ckmeans.1d.dp/Ckmeans.1d.dp.h>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/bench_cpp/vendor/Ckmeans.1d.dp/precision.h>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/bench_cpp/vendor/Ckmeans.1d.dp/EWL2.h>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/bench_cpp/vendor/Ckmeans.1d.dp/EWL2_dynamic_prog.cpp>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/bench_cpp/vendor/Ckmeans.1d.dp/EWL2_fill_log_linear.cpp>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/bench_cpp/vendor/Ckmeans.1d.dp/EWL2_fill_SMAWK.cpp>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/bench_cpp/vendor/Ckmeans.1d.dp/dynamic_prog.cpp>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/bench_cpp/vendor/Ckmeans.1d.dp/fill_log_linear.cpp>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/bench_cpp/vendor/Ckmeans.1d.dp/fill_SMAWK.cpp>
  - <https://raw.githubusercontent.com/urschrei/ckmeans/HEAD/bench_cpp/vendor/Ckmeans.1d.dp/select_levels.cpp>
  - <https://crates.io/api/v1/crates/ckmeans>
  - <https://crates.io/api/v1/crates/ckmeans/reverse_dependencies>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/urschrei/ckmeans`) · [data/wave14/enrich/raw/github_com_urschrei_ckmeans.json](../../../data/wave14/enrich/raw/github_com_urschrei_ckmeans.json) (enrichment confidence 0.8)

</details>
