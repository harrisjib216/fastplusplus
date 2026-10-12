# AlphaDev sort3-sort8 assembly programs (libc++ branchless sort3/4/5)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Python (RL pseudo-code) / C++ test harness with x86-64 assembly sort programs` · `Apache-2.0 (software; other materials CC-BY-4.0)` · 🔴 abandoned

> RL-discovered x86-64 cmov sorting kernels for 3-8 ints; the branchless sort3/4/5 form now sits inside libc++ std::sort.

| | |
|---|---|
| **Beats** | libc++ std::sort with its previous __sort3/__sort4/__sort5 helpers |
| **Claimed result** | LLVM commit 194d1965d2 (Differential Revision D118029) message: branchless sort3/sort4/sort5 'generated using Reinforcement Learning' achieve 'statistically significant improvement in sorting random integers on test cases from sort1 to sort262144 for uint32 and uint64'; no percentages in the commit (full overview behind a bit.ly link, not opened). Snippet only (DeepMind blog and Wikipedia summaries of the Nature paper): the libc++ changes were up to 70% faster for short sequences and about 1.7% faster for sequences over 250,000 elements, for uint32, uint64 and float on ARMv8, Intel Skylake and AMD Zen 2. |
| **Workload** | Sorting random uint32 and uint64 arrays of size 1 to 262144 in the libc++ benchmarks, on isolated Skylake, ARM and AMD machines. |
| **Metric** | throughput (time to sort) |
| **Hardware** | Intel Skylake, AMD (Zen 2 per Wikipedia snippet) and ARMv8 machines; exact CPU models not stated in the commit |
| **Adoption** | 740 stars; repository archived (read-only) by the owner on 2024-08-22; the sort3/4/5 routines were integrated into LLVM libc++ |
| **Last commit** | 2023-06-20 |
| **Links** | [repository](https://github.com/google-deepmind/alphadev) · [benchmark](https://github.com/llvm/llvm-project/commit/194d1965d2c841fa81e107d19e27fae1467e7f11) |

## Verdict

The LLVM commit 194d1965 (Marco Gelmi, 2022-04-08, review D118029) replaced libc++'s branching __sort3/__sort4/__sort5 with branchless versions for contiguous arithmetic types and reports statistically significant gains sorting random uint32 and uint64 arrays of 1 to 262,144 elements on unnamed Skylake, ARM and AMD machines, with no percentages; the 'up to 70% faster for short sequences, about 1.7% above 250,000 elements' figures come from search snippets of the Nature paper and DeepMind blog, not opened here. Third-party checks cut against the asm itself: issue #2 measured Sort3/4/5AlphaDev about 9% slower than a Clang -O3 C sorting network, and arXiv 2307.14503 (snippet only) reports a shorter and faster human-written sort3.

## Use it when

- You already build with libc++ (LLVM 15 or later) and sort contiguous arrays of int, unsigned, 64-bit integers, float or double with the default comparator: you get the branchless sort3/4/5 automatically.
- You need a reference for branchless fixed-size sorting networks of 3 to 8 signed 32-bit ints on x86-64, e.g. to compare against your own network or a compiler's cmov output.
- Research or teaching on superoptimisation and RL program search, where the exact discovered instruction sequences and their exhaustive correctness test are the point.

## Skip it when

- As a drop-in speedup: an independent cycle count in issue #2 (Clang -O3, rdcycle) found Sort3/4/5AlphaDev about 9% slower than a plain C sorting network that Clang compiled to cmov, and only 13-15% faster than a naive hand-written asm network.
- For unsigned, 64-bit or floating-point keys: the asm uses signed 32-bit compares (cmovl/cmovg on eax-class registers) and assumes int32 elements.
- With GCC, MSVC, ARM or any non-x86-64 target: the inline asm is AT&T x86-64 only and the README says only Linux with clang is supported; issue #5 reports an 'unknown register name' compile error.
- Large-array sorting: the paper-reported gain for libc++ std::sort at over 250,000 elements is about 1.7% (search snippet), and current libc++ also changed partitioning since, so the gain is not separable.
- If you want VarSort or sort6-8 in a library: none of them were upstreamed (an issue asking for VarSort5 in libc++ was closed 'not planned').

## How it is fast

The programs are branchless sorting networks: each compare-exchange is a cmp followed by paired cmovl/cmovg into fresh registers, so random input causes no branch mispredictions and the dependency chains are short. The search found small instruction savings over hand networks, notably the 'swap move' that inserts a third element into an already ordered pair with one fewer min/max; libc++ encodes this as __partially_sorted_swap next to a ternary-select __cond_swap. In std::sort these kernels only handle the 3-5 element leaves and pivot sampling, which is why the large-array gain is small.

## Compared with alternatives

No sibling in this category sorts small fixed-size arrays; the other entries (FastMemcpy, asmlib, FP-ASM, CvsAssemblyBenchmark) are memcpy, libc-replacement or numeric kernels. Pick AlphaDev only as a reference for cmov sorting networks or to cite the libc++ change; for production use, use libc++'s std::sort, or write the network in C and let Clang emit the cmovs.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the sort functions; the test needs Bazel and GoogleTest release-1.12.1; alphadev.py imports JAX/Haiku/numpy but is pseudocode |
| **Minimum toolchain** | Clang with GNU inline asm (BUILD uses -std=c++17); libc++ route: LLVM 15 or later |
| **Platforms** | x86-64 only (Linux per README); libc++ C++ version is portable |
| **Thread safety** | Pure functions on the caller's buffer; no shared state (not documented) |
| **Drop-in for the baseline** | partial — the libc++ C++ form is already inside std::sort; the asm functions are not std::sort replacements, only fixed-size int32 kernels with a different interface |

## Gotchas

- Harness flaw: the repo contains no benchmark at all. sort_functions_test.cc only checks correctness on every permutation of every '&lt;'/'=' pattern for n items, and alphadev.py stubs out the assembly simulator and measure_latency (they return {} / pass) and still has an undefined 'value' in make_target (issue #11), so none of the paper's latency figures can be reproduced from this repo.
- The VarSort programs read the element count from buffer[0] and branch on it; in VarSort3 a count of 0 or below skips the cmovge that sets r9d and stores that uninitialised register into buffer[2], and counts above 3 are treated as 3, so callers must pass 1..N.
- In libc++ the int, unsigned, long, long long, float, double and long double instantiations of std::sort with std::less are explicit externs compiled into the libc++ shared library, so on a platform with a system libc++ (macOS) the code you run depends on the OS library version, not the headers you compile against.
- The libc++ gate is is_arithmetic, not 'integral' as the commit message says, so float and double also take the branchless path (NaN keys break strict weak ordering in either path).

## Known shortcomings

- Nature paper unreachable, so the 70% and 1.7% figures are snippets only; the LLVM commit (194d1965d2) has no figures; the repo has correctness tests only, no benchmark, archived; an independent sort3 (arXiv 2307.14503, snippet) beats AlphaDev's. Paper-access retier candidate (C if the paper stays unreachable).
- Enricher: the repo has no benchmark (the test checks correctness only; alphadev.py stubs the simulator and measure_latency with an undefined value, issue #11); the independent run in issue #2 has Sort3/4/5AlphaDev about 9% slower than a Clang -O3 C sorting network (4.39 vs 4.01 cycles at N=3); VarSort3 with count &lt;= 0 stores an uninitialised r9d; the libc++ gate is is_arithmetic so floats take the path too; std::sort&lt;int,...&gt; is extern in the libc++ dylib so speed depends on the OS library version; the 70% and 1.7% figures remain snippet-only (Nature and the blogs unreachable). Retiered to D on the contrary independent number.

## Caveats and trade-offs

The commit gives no figures, and the Nature paper (the reason for tier B) could not be opened here (nature.com, ncbi PMC, ai.dmi.unibas.ch and reviews.llvm.org all unreachable); the 70% / 1.7% figures come from search snippets of DeepMind's blog and Wikipedia, and per-function latencies were not verified. The repo has no benchmark: sort_functions_test.cc only checks correctness of the inline-asm Sort3-Sort8 and VarSort3-5 programs (int32 buffers), and alphadev.py is non-runnable pseudocode. What libc++ shipped is C++ reverse-engineered from the fixed sort3/sort4/sort5 programs (commit touches libcxx/include/__algorithm/sort.h only for those); sort6-8 and the VarSort programs are not in that commit. Programs were discovered by RL, not hand-written. A later third-party paper (arXiv 2307.14503, 'Shorter and faster than Sort3AlphaDev', snippet only) reports a shorter and faster human-written sort3. Repository archived 2024-08-22.

The repo holds the RL agent pseudo-code and a test file with the discovered assembly sorts (Sort3AlphaDev to Sort8AlphaDev, VarSort3 to VarSort5); assembly execution is not included; libc++ integration is a branchless C++ translation for integral types only, fixed sizes 3 to 5.

## Maintenance

Archived read-only since 2024-08-22 with 3 commits; Apache-2.0 asm is copyable but niche (x86-64, int32, clang), and the practical value already ships in libc++ std::sort, so treat this as a reference rather than a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now D.
- **Tier reason:** Peer-reviewed Nature 2023 paper (doi 10.1038/s41586-023-06004-9, cited in the repo README) reports latency wins over the human/libc++ sort3-sort5 routines, and LLVM libc++ upstreamed the branchless sort3/4/5 after review (D118029); the paper itself was unreachable (nature.com, PMC and a university mirror all blocked), so its figures are known from search snippets only. Not A: the libc++ benchmark code (libcxx/benchmarks/algorithms.bench.cpp) is public but the commit names no compiler, flags or CPU models.
- **Retiered** B to D: Enricher (2026-10-12): the repository ships no measurement (its test checks correctness only and measure_latency is a stub) while the only independent timing, issue #2, has the AlphaDev Sort3/4/5 routines about 9% slower than a Clang -O3 C sorting network (4.39 vs 4.01 cycles at N=3); the 70% and 1.7% paper figures remain snippet-only. No supporting measurement reachable; contrary independent number.
- **Verifier notes:** Record accurate about the LLVM commit (wording, files, no percentages); kept at B on the peer-reviewed Nature paper, but the paper's numbers were seen only through snippets, so treat as a paper-access retier candidate (C if the enricher also cannot reach it). Fixed baseline_in_list to true (libc++'s own -O3-compiled __sort3/4/5 is the category's stdlib baseline). Shortcomings: no figures on benchmark_url, no benchmark harness in the repo, archived repo, an independent sort3 beats AlphaDev's.
- **Fields the verifier corrected:** `baseline_in_list`, `claimed_speedup`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-37 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/llvm/llvm-project/commit/194d1965d2c841fa81e107d19e27fae1467e7f11>
  - <https://github.com/google-deepmind/alphadev>
  - <https://github.com/google-deepmind/alphadev/commits>
  - <https://raw.githubusercontent.com/google-deepmind/alphadev/HEAD/sort_functions_test.cc>
- **Sources the enricher read:**
  - <https://github.com/google-deepmind/alphadev>
  - <https://raw.githubusercontent.com/google-deepmind/alphadev/HEAD/README.md>
  - <https://raw.githubusercontent.com/google-deepmind/alphadev/HEAD/sort_functions_test.cc>
  - <https://raw.githubusercontent.com/google-deepmind/alphadev/HEAD/alphadev.py>
  - <https://raw.githubusercontent.com/google-deepmind/alphadev/HEAD/BUILD>
  - <https://raw.githubusercontent.com/google-deepmind/alphadev/HEAD/WORKSPACE>
  - <https://github.com/google-deepmind/alphadev/issues?q=is%3Aissue>
  - <https://github.com/google-deepmind/alphadev/issues/2>
  - <https://github.com/google-deepmind/alphadev/issues/3>
  - <https://github.com/google-deepmind/alphadev/issues/4>
  - <https://github.com/google-deepmind/alphadev/issues/5>
  - <https://github.com/llvm/llvm-project/commit/194d1965d2c841fa81e107d19e27fae1467e7f11>
  - <https://github.com/llvm/llvm-project/commit/194d1965d2c841fa81e107d19e27fae1467e7f11.patch>
  - <https://raw.githubusercontent.com/llvm/llvm-project/main/libcxx/include/__algorithm/sort.h>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/google-deepmind/alphadev`) · [data/wave13/enrich/raw/github_com_google_deepmind_alphadev.json](../../../data/wave13/enrich/raw/github_com_google_deepmind_alphadev.json) (enrichment confidence 0.6)

</details>
