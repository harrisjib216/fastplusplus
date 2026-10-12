# Parabix (bitstream UTF-16 validation kernel)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Unicode and UTF-8](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `OSL-3.0` · 🔴 abandoned

> Bitstream-parallel text-processing framework whose LLVM-JIT'd SIMD kernel beat a simdutf CLI wrapper on UTF-16 validation.

| | |
|---|---|
| **Beats** | simdutf |
| **Claimed result** | Apple M1, single thread, valid input, whole-process wall clock (median of 7). Raw: Parabix 2900-3760 MiB/s vs simdutf 1824-2532 MiB/s, about 1.18x-2.0x (the page's 'Speedup vs simd_t1' column shows simdutf at 0.50x-0.85x). Overhead-adjusted: Parabix 5075-5205 MiB/s vs simdutf 1883-2600 MiB/s, about 2.0x-2.7x (derived from page data). The student project's README headline is '\~2.3-2.5x adjusted' (Apple 2.33x/2.34x, CSIL QEMU x86-64 2.42x/2.52x on the default dataset). |
| **Workload** | UTF-16LE validation of 128/256 MiB generated corpora (cjk, default, emoji_heavy, english_ascii_heavy, european_accented, mixed_multilingual, south_asian), valid input, single thread, median of 7 runs after 2 warmups. Timed as whole-process wall clock (includes process startup, file reading and, for Parabix, pipeline load), with an 'adjusted' column that subtracts a fixed per-process overhead measured on a tiny input. |
| **Metric** | throughput |
| **Hardware** | Apple M1, 8 GiB RAM (primary, native); a CSIL x86-64 host run inside a QEMU guest (secondary, explicitly flagged by the benchmark authors as 'not Ice Lake') |
| **Compiler and flags** | Apple clang 21.0.0 (clang-2100.1.1.101) with Homebrew LLVM 16.0.6 as the Parabix JIT backend. Parabix is built as CMake Release by scripts/setup_parabix.sh. The simdutf v9.0.0 wrapper is built with `c++ -O3 -std=c++17` by scripts/setup_clausecker_lemire.sh. The x86-64 leg used GCC 13.3.0 inside a QEMU guest (simdutf SSE4.2 'westmere' path). |
| **Adoption** | 17 stars (GitHub mirror) |
| **Last commit** | 2021-08-10 |
| **Links** | [repository](https://github.com/parabix/parabix-devel-mirror) · [benchmark](https://github.com/dakshkashyap/cmpt479-project-group8/blob/main/results/utf16_benchmark_apple_arm64_summary.md) |

## Verdict

On valid UTF-16LE corpora (128/256 MiB, single thread, Apple M1, median of 7 runs), a third-party benchmark measured Parabix's SIMD kernel at 2900-3760 MiB/s raw (5075-5205 MiB/s overhead-adjusted) against a simdutf v9.0.0 CLI wrapper (clang -O3 -std=c++17) at 1824-2532 MiB/s raw (1883-2600 MiB/s adjusted) -- about 1.18-2.0x raw and 2.0-2.7x adjusted -- but the simdutf wrapper reads the whole file into memory before validating while Parabix streams it, so part of the gap reflects I/O handling rather than the validation kernels.

## Use it when

- Building a new streaming text pipeline (regex search, XML parsing, transcoding) where adopting the whole Parabix framework is acceptable, not just linking a validator
- Multi-stage text transforms where replacing many per-character branches with bitwise ops across a full register/vector width is the goal (icgrep-style regex matching)
- Research or teaching on bit-parallel SIMD algorithms and LLVM JIT code generation
- Environments that can carry an LLVM 5+/Boost 1.61+/Z3/CMake toolchain at both build and run time
- Workloads that also want multicore pipeline parallelism (thread-num &gt; 1) inside the same kernel model

## Skip it when

- You need a small, embeddable UTF-8/UTF-16 validator with a stable C/C++ API — no such component exists in this mirror; use simdutf directly
- Startup latency matters: Parabix's LLVM JIT pipeline load adds \~0.019s fixed overhead per process vs \~0.002s for simdutf, dominating small-input timings
- You need permissive licensing — Parabix/icgrep is OSL-3.0 (strong copyleft), unlike simdutf's permissive license
- You need an actively maintained project — no commits on this mirror since 2021-08-10
- You need UTF-8 rather than UTF-16 — this benchmark and the validator it measures are UTF-16LE only

## How it is fast

Core technique is Cameron et al.'s parallel bit-stream method: input is transposed (s2p) into 8/16 bitstreams, each holding one bit-position across the whole buffer, turning per-character branching into bitwise AND/OR/shift ops across a full register width, plus optional multicore pipeline parallelism (--thread-num). On this specific benchmark part of the apparent win is a process/I-O gap rather than kernel speed: Parabix streams the file through ReadSourceKernel while the simdutf wrapper CLI reads the whole file into a std::vector via ifstream before validating; the benchmark authors' own methodology doc says I/O is not equalized between the two.

## Compared with alternatives

None of the catalogued UTF-8 siblings (ada-url/idna, simdutf8, xutf, SimdUnicode, utf8_range) target UTF-16, so there's no direct sibling for this workload; pick Parabix over building your own UTF-16 path only if you're already adopting its whole bit-parallel framework for other text processing, not for a standalone validator.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | LLVM 5+ (JIT backend), Boost 1.61+, Z3 theorem prover, CMake 2.8+ |
| **Minimum toolchain** | C++14; benchmark used Homebrew LLVM 16.0.6 as the JIT backend under Apple clang 21 |
| **Platforms** | x86-64 and aarch64 exercised by the benchmark (Apple M1 native; x86-64 via QEMU); source tree also has NVPTX/CUDA kernel code (editd GPU kernel, NVPTXDriver.h) that this benchmark does not exercise |
| **Thread safety** | not documented in README; kernels expose a --thread-num pipeline-parallelism option, but no stated guarantee about concurrent use of a single pipeline instance |
| **Drop-in for the baseline** | partial — explain: not an API-level drop-in for simdutf; it is a separate framework/CLI (and the specific validator tool isn't even present in this GitHub mirror), requiring an LLVM JIT toolchain rather than linking a small library |

## Gotchas

- The benchmarked tools/utf16validate isn't in this GitHub mirror; it's added by a third-party patch to Parabix commit f0369dd pulled from the SFU GitLab, and that commit postdates this mirror's last sync (2021-08-10)
- Fixed per-process overhead (\~0.019s, mostly LLVM JIT pipeline load) is roughly 9x simdutf's (\~0.002s) — raw wall-clock throughput on small inputs is dominated by this, use the benchmark's overhead-adjusted numbers instead
- GitHub reports this repo's license as NOASSERTION even though the README and OSL3.0.txt/LLVM-LICENSE.txt in the tree declare OSL-3.0 for Parabix code and the LLVM Release License for vendored LLVM files
- This is a read-only mirror: it does not accept GitHub pull requests; patches go to an SFU GitLab research repo instead

## Known shortcomings

- The benchmarked UTF-16 validator is not in this mirror: it is a patch in an unlicensed 0-star student repo (dakshkashyap/cmpt479-project-group8), and its timings are whole-process runs dominated by file I/O rather than validation.

## Caveats and trade-offs

The benchmarked UTF-16 validator is not in this repo. It is tools/utf16validate, added by patches/utf16-simd-milestone.patch in the unlicensed, 0-star student repo dakshkashyap/cmpt479-project-group8. That patch is applied to Parabix commit f0369dd from the SFU GitLab (cs-git-research.cs.sfu.ca/cameron/parabix-devel), and that commit is absent from this GitHub mirror (last commit 2021-08-10). I/O is not equalized between the tools (the authors' docs/benchmark_methodology.md §6 says so). The simdutf wrapper reads the whole file into a zero-filled std::vector via ifstream before validating, and runs are timed whole-process. The measured simdutf throughput therefore reflects the wrapper's I/O path more than simdutf's kernel. The headline 2.3-2.5x is overhead-adjusted; the raw gap is 1.18x-2.0x. The x86-64 leg ran in a QEMU guest ('not a physical Ice Lake CPU'). Parabix itself is OSL-3.0 (copyleft; LLVM files under the LLVM Release License). Category: UTF-16, not UTF-8.

Parabix requires an LLVM JIT toolchain at build/run time (heavier dependency, \~0.019s fixed per-process overhead vs simdutf's \~0.002s); this benchmark validates UTF-16, not UTF-8; it is a research/academic codebase without a stable packaged API.

## Maintenance

Abandoned on this mirror since 2021-08-10 (no evidence in this session of active development elsewhere) and usability is mixed: it's a research framework with no stable API, requiring a full LLVM/Boost/Z3 build toolchain rather than a library you can drop in.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification A, tier now C.
- **Tier reason:** The code (benchmarks/run_utf16_benchmark.py, patches/utf16-simd-milestone.patch, external/baselines/clausecker_lemire/utf16validate_cl.cpp), compiler, flags and CPU (Apple M1) are all public. But the harness does not isolate the baseline. Timing is whole-process via Python subprocess. The simdutf wrapper reads the whole file with std::ifstream into a zero-filled vector before validating, while Parabix streams through ReadSourceKernel. The authors' own docs/benchmark_methodology.md §6 says I/O is not equalized. The numbers come from the authors of the measured kernel and do not cleanly measure simdutf's validator, so the tier is C, not A.
- **Verifier notes:** The adjusted numbers are on the page, but the comparison pits a streaming Parabix CLI against a simdutf CLI wrapper that reads the whole file first, so it likely measures I/O, not simdutf's validation kernel. The orchestrator may want to drop this record or re-point it at the student repo. The license is not missing: the mirror README declares OSL-3.0 and ships OSL3.0.txt (GitHub reports NOASSERTION).
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `license`, `usability`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/parabix/parabix-devel-mirror>
  - <https://github.com/parabix/parabix-devel-mirror/blob/master/README.md>
  - <https://github.com/parabix/parabix-devel-mirror/blob/master/OSL3.0.txt>
  - <https://github.com/parabix/parabix-devel-mirror/blob/master/README-icgrep.md>
  - <https://github.com/dakshkashyap/cmpt479-project-group8>
  - <https://github.com/dakshkashyap/cmpt479-project-group8/blob/main/results/utf16_benchmark_apple_arm64_summary.md>
  - <https://github.com/dakshkashyap/cmpt479-project-group8/blob/main/results/apple_arm64_toolchain.md>
  - <https://github.com/dakshkashyap/cmpt479-project-group8/blob/main/results/csil_x86_64_toolchain.md>
  - <https://github.com/dakshkashyap/cmpt479-project-group8/blob/main/README.md>
  - <https://github.com/dakshkashyap/cmpt479-project-group8/blob/main/docs/cross_arch_evaluation.md>
  - <https://github.com/dakshkashyap/cmpt479-project-group8/blob/main/docs/benchmark_methodology.md>
  - <https://github.com/dakshkashyap/cmpt479-project-group8/blob/main/external/baselines/clausecker_lemire/README.md>
  - <https://github.com/dakshkashyap/cmpt479-project-group8/blob/main/external/baselines/clausecker_lemire/utf16validate_cl.cpp>
  - <https://github.com/dakshkashyap/cmpt479-project-group8/blob/main/scripts/setup_parabix.sh>
  - <https://github.com/dakshkashyap/cmpt479-project-group8/blob/main/scripts/setup_clausecker_lemire.sh>
  - <https://github.com/dakshkashyap/cmpt479-project-group8/blob/main/patches/utf16-simd-milestone.patch>
  - <https://github.com/dakshkashyap/cmpt479-project-group8/blob/main/benchmarks/run_utf16_benchmark.py>
  - <https://cs-git-research.cs.sfu.ca/cameron/parabix-devel>
- **Sources the enricher read:**
  - <https://github.com/parabix/parabix-devel-mirror>
  - <https://github.com/parabix/parabix-devel-mirror/blob/master/README.md>
  - <https://github.com/parabix/parabix-devel-mirror/blob/master/README-icgrep.md>
  - <https://github.com/dakshkashyap/cmpt479-project-group8/blob/main/results/utf16_benchmark_apple_arm64_summary.md>
  - <https://github.com/dakshkashyap/cmpt479-project-group8/blob/main/docs/benchmark_methodology.md>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/parabix/parabix-devel-mirror`) · [data/wave3/enrich/raw/github_com_parabix_parabix_devel_mirror.json](../../../data/wave3/enrich/raw/github_com_parabix_parabix_devel_mirror.json) (enrichment confidence 0.4)

</details>
