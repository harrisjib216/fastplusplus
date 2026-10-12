# optimization-detective (SWAR memcasecmp, common suffix and whitespace patches for Abseil)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Three patch-sized rewrites of Abseil string helpers (SWAR memcasecmp, word-at-a-time common suffix, clean-input fast path), 1.3-6.9x over Abseil's byte loops.

| | |
|---|---|
| **Beats** | Abseil absl::strings_internal::memcasecmp, FindLongestCommonSuffix and RemoveExtraAsciiWhitespace (verbatim upstream code from abseil-cpp@7e706921, byte-at-a-time loops) |
| **Claimed result** | FindLongestCommonSuffix 6.87x headline (the half_match/256 row of results/absl_lcp_lcs_bench.txt: 55.84 to 8.13 ns); FINDINGS.md table: full match 4096 B 1524 to 233 ns (6.5x), 256 B 100 to 15 ns (6.9x), half match 4096 B 754 to 121 ns (6.2x); regresses to about 0.5x (0.55 to about 1.05 ns) when the last bytes differ. memcasecmp 5.98x headline (FINDINGS.md: eq_case 256 B 229 to 38 ns; 4096 B eq_exact 1227 to 246 ns 4.99x, eq_case 3557 to 612 ns 5.82x; the checked-in results file is a slightly different run: eq_case/256 6.29x, eq_case/4096 5.97x, eq_exact/4096 4.96x); 4.1-4.3x at 16 B; mismatch at byte 0 is 0.47x (0.90 to 1.91 ns). RemoveExtraAsciiWhitespace 1.40x on already-clean 4096 B input (2460 to 1758 ns; results file 1.38x), 1.27-1.46x on clean input across sizes, but 0.78-0.84x on input with one internal double space (64-4096 B). |
| **Workload** | Standalone microbenchmarks (median of 25 reps, autotuned iteration count) of each function on 256 B to 4096 B strings: full match, half match, byte-identical and case-flipped equality. |
| **Metric** | throughput |
| **Hardware** | Apple M2, macOS 24.5 |
| **Compiler and flags** | Apple clang 14, -std=c++17 -O3 |
| **Adoption** | 0 stars; new repo created 2026-08-16 |
| **Last commit** | 2026-08-17 |
| **Links** | [repository](https://github.com/marufzaber/optimization-detective) · [benchmark](https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/FINDINGS.md) |

## Verdict

On one Apple M2 with Apple clang 14 -std=c++17 -O3, the repo's own harness (median of 25 reps, autotuned inner loop) times each patch against the Abseil original compiled in the same file: memcasecmp 4.96x on equal 4096 B strings and 5.97-6.29x on case-flipped 256-4096 B strings, FindLongestCommonSuffix 6.4-6.9x on 256-4096 B shared tails, RemoveExtraAsciiWhitespace 1.27-1.46x on already-clean input; all three regress (about 0.45-0.84x) on early-mismatch or needs-rewrite inputs. The baseline is Abseil's scalar code, not libc strncasecmp or memcmp.

## Use it when

- You maintain an Abseil fork or vendored copy and profiles show absl::EqualsIgnoreCase / StartsWithIgnoreCase / EndsWithIgnoreCase on strings of 8 bytes or more (header names, config keys): 3.75-4.9x at 8-32 B and 4.9-6.3x at 256-4096 B in the author's runs.
- Inputs where case-insensitive matches are the common outcome (equal or case-only-different strings), since that is where the SWAR loop replaces a byte loop for the whole length.
- Code that calls FindLongestCommonSuffix on strings that share long tails (path or log-line dedup): 2.8-6.9x on full matches of 8 B or more (2.2x when only 4 of 8 tail bytes match).
- RemoveExtraAsciiWhitespace on inputs that are usually already canonical: 1.27-1.46x by skipping the write-back.
- As a template for small, testable string-primitive patches: each pair comes with a differential fuzz test against the original code.

## Skip it when

- Inputs that usually differ in the first or last byte: memcasecmp is 0.44-0.47x at every size from 8 B up when byte 0 differs (0.90 to 1.91-2.04 ns), and FindLongestCommonSuffix is about 0.5x on random strings and on last-byte mismatches (0.55 to 1.03-1.10 ns). The suffix function's no_match rows, the likely case for unrelated strings, all regress.
- RemoveExtraAsciiWhitespace inputs that do need rewriting: one internal double space costs 0.78-0.84x from 64 B up, because the pre-scan runs and the original rewrite then runs anyway.
- Big-endian targets: the patches use raw memcpy loads with clz/ctz byte indexing, whereas upstream FindLongestCommonPrefix uses absl::little_endian::Load64, so the code as written returns wrong answers on big-endian machines.
- When you want a maintained library: this is a two-day, 0-star showcase repo (12 commits, 2026-08-16/17) and none of the patches is in Abseil (upstream master still has the byte loops on 2026-10-12).
- Non-ASCII case folding: like the original it only folds A-Z.

## How it is fast

memcasecmp loads 8 bytes per side, skips equal words outright, and otherwise lower-cases both words with a SWAR range test (mask to 7 bits, add 0x3F and 0x25, keep the bytes in 'A'..'Z', OR in 0x20) before locating the first differing byte with ctz on the XOR. FindLongestCommonSuffix mirrors Abseil's own FindLongestCommonPrefix: XOR of two 8-byte windows walked backward from the end, with clz/8 giving the number of matching tail bytes. RemoveExtraAsciiWhitespace adds a read-only scan that returns early when the string has no leading, trailing or adjacent whitespace, skipping the byte-by-byte rewrite; the scan itself is still a scalar table-lookup loop.

## Compared with alternatives

None of the catalogued siblings offers a case-insensitive compare or a common-suffix routine; pick this when the bottleneck is Abseil's EqualsIgnoreCase family or FindLongestCommonSuffix in code already on Abseil, whereas memx-cdy or Arm Optimized Routines cover plain memcmp/memchr and simstr replaces the whole std::string idiom set.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (C++17 standard library only; benchmarks use the repo's bench/bench.h) |
| **Minimum toolchain** | C++17; GCC or Clang (uses __builtin_clzll, __builtin_ctzll, __builtin_expect) |
| **Platforms** | little-endian 64-bit targets only; measured on Apple M2 (arm64) only |
| **Thread safety** | pure functions on caller-owned buffers (RemoveExtraAsciiWhitespace mutates its std::string argument), same as the Abseil originals |
| **Drop-in for the baseline** | partial — same signatures and verified-identical results for the Abseil internals, but you must patch them into your Abseil copy (absl::string_view, little_endian loads, ABSL_ macros) yourself; no upstream release ships them |

## Gotchas

- FINDINGS.md says the little-endian assumption is safe because FindLongestCommonPrefix 'already assumes it', but upstream prefix code loads through absl::little_endian::Load64/Load16 and is endian-neutral; the patches' plain memcpy + clz/ctz byte indexing is not. Swap in absl::little_endian::Load64 before upstreaming.
- optimized.h for RemoveExtraAsciiWhitespace claims clang emits NEON that scans 16 bytes per iteration, but the loop has an early exit and a table lookup, and the measured clean/4096 rate (about 1825 ns including the 4 KiB buffer copy, roughly 0.4 ns per byte) fits a scalar loop (derived from page data). A SWAR or vector pre-scan would likely gain more.
- Benchmarks re-run one fixed input pair in a hot loop with an asm memory clobber, so ns/op is cache-resident throughput with perfectly predicted branches; the 0.55 ns early-exit rows are overlapped iterations, not single-call latency. The remove_ws timings include a buf.assign(tpl) copy on both sides, which slightly understates its ratio.
- The headline 6.87x (FindLongestCommonSuffix) and 5.98x (memcasecmp) are each the best row of their table; FINDINGS.md tables and the checked-in results/\*.txt are slightly different runs (for example eq_case/256 5.98x vs 6.29x, clean/4096 1.40x vs 1.38x).

## Known shortcomings

- Baseline is Abseil's scalar loop copied verbatim (abseil-cpp@7e706921) and compiled in the same file as the patch, not glibc strncasecmp or memcmp, so the ratios say nothing about libc; one machine (Apple M2) and one compiler (Apple clang 14); each benchmark re-runs one fixed cache-resident input pair in a hot loop.
- Patch code is correct and the harness is sound (cache-hot fixed inputs). Documentation flaws: FINDINGS.md claims the upstream prefix code 'already assumes' little-endian, but Abseil uses absl::little_endian::Load64, so the patches break on big-endian; optimized.h claims a NEON pre-scan for RemoveExtraAsciiWhitespace, contradicted by its own clean/4096 numbers (a scalar rate). Regressions of 0.44-0.84x on mismatching inputs. Abseil master still had the byte loops on 2026-10-12. Showcase repo, 2 days old, 0 stars.

## Caveats and trade-offs

Baseline is Abseil's scalar loop copied verbatim into original.h (abseil-cpp@7e706921) and compiled in the same file as the patch, not glibc strncasecmp or memcmp, so the ratios say nothing about libc; one machine (Apple M2) and one compiler (Apple clang 14; 'macOS 24.5' is probably the Darwin version, i.e. macOS 15.5). Each benchmark re-runs one fixed input pair in a hot loop (cache-resident, perfectly predicted), and the eq_case workload flips every letter, the worst case for the original's per-byte branch. Raw outputs in results/ (absl_lcp_lcs_bench.txt, absl_memcasecmp_bench.txt, absl_remove_ws_bench.txt) come from a slightly different run than the FINDINGS.md tables (within a few percent). The patches regress on early mismatches (about 2x slower at 1-2 ns absolute) and RemoveExtraAsciiWhitespace is 16-28% slower when a rewrite is needed. The patches are not upstreamed to Abseil (no PR linked); the author notes FindLongestCommonSuffix has no call sites in the codebases checked. The repo's dollar and CO2 fleet estimates are heuristics, not evidence. Two more patches in the repo (nlohmann/json dump_escaped 4.62x, cpp-httplib header hash 1.44x) belong to JSON and HTTP categories and are not recorded here. Optimized code lives alongside verbatim Apache-2.0 Abseil source (original.h); the author's additions are MIT.

Header-only drop-in replacements (original.h, optimized.h, test.cc, bench.cc per function, no build system); the SWAR 8-byte loads assume little-endian and ASCII-only case folding; the suffix and case-compare versions pay about 0.5-1 ns extra when the mismatch is in the first or last byte.

## Maintenance

A 0-star showcase repo written over 2026-08-16/17 (commit history includes LinkedIn post drafts and an 'llm' topic) and not touched since; the author's code is MIT and small enough to paste into an Abseil copy, but nothing has been upstreamed and the code is unmaintained.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Public standalone benchmark code (src/absl_lcp_lcs/bench.cc, src/absl_memcasecmp/bench.cc, src/absl_remove_ws/bench.cc on the bench/bench.h harness, driven by run_all.sh) times verbatim Abseil code (original.h) against the patch; compiler (Apple clang 14), flags (-std=c++17 -O3) and CPU (Apple M2) are stated, and raw outputs are checked in under results/.
- **Verifier notes:** Numbers check out against FINDINGS.md and the checked-in results files; code is correct on inspection (SWAR tolower masks to 7 bits, clz/ctz guarded against zero). Shortcomings to record: Abseil scalar loops as baseline (not libc), single Apple M2 machine, fixed hot-cache inputs, regressions on early-mismatch and needs-rewrite inputs, patches not upstreamed, 0-star repo from 2026-08.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-61 (wave 13), file only (agent killed by the spend limit before reporting); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/marufzaber/optimization-detective>
  - <https://github.com/marufzaber/optimization-detective/commits>
  - <https://github.com/marufzaber/optimization-detective/tree/main/results>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/FINDINGS.md>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/README.md>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/bench/bench.h>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/run_all.sh>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/src/absl_lcp_lcs/bench.cc>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/src/absl_lcp_lcs/optimized.h>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/src/absl_lcp_lcs/original.h>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/src/absl_memcasecmp/bench.cc>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/src/absl_memcasecmp/optimized.h>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/src/absl_memcasecmp/original.h>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/src/absl_remove_ws/bench.cc>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/results/absl_lcp_lcs_bench.txt>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/results/absl_memcasecmp_bench.txt>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/results/absl_remove_ws_bench.txt>
- **Sources the enricher read:**
  - <https://github.com/marufzaber/optimization-detective>
  - <https://github.com/marufzaber/optimization-detective/commits>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/README.md>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/FINDINGS.md>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/bench/bench.h>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/run_all.sh>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/src/absl_lcp_lcs/bench.cc>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/src/absl_lcp_lcs/optimized.h>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/src/absl_lcp_lcs/original.h>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/src/absl_lcp_lcs/test.cc>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/src/absl_memcasecmp/bench.cc>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/src/absl_memcasecmp/optimized.h>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/src/absl_memcasecmp/original.h>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/src/absl_memcasecmp/test.cc>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/src/absl_remove_ws/bench.cc>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/src/absl_remove_ws/optimized.h>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/src/absl_remove_ws/original.h>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/src/absl_remove_ws/test.cc>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/results/absl_lcp_lcs_bench.txt>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/results/absl_memcasecmp_bench.txt>
  - <https://raw.githubusercontent.com/marufzaber/optimization-detective/HEAD/results/absl_remove_ws_bench.txt>
  - <https://raw.githubusercontent.com/abseil/abseil-cpp/master/absl/strings/internal/memutil.cc>
  - <https://raw.githubusercontent.com/abseil/abseil-cpp/master/absl/strings/match.cc>
  - <https://raw.githubusercontent.com/abseil/abseil-cpp/master/absl/strings/ascii.cc>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/marufzaber/optimization-detective`) · [data/wave13/enrich/raw/github_com_marufzaber_optimization_detective.json](../../../data/wave13/enrich/raw/github_com_marufzaber_optimization_detective.json) (enrichment confidence 0.75)

</details>
