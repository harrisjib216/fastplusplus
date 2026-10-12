# validateutf8-experiments (lookup UTF-8 validation, Keiser and Lemire)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `C++` · `no license` · 🟢 active

> Research harness for the Keiser-Lemire 'lookup' SIMD UTF-8 validator, about 4-6x faster than the best scalar validator it tests.

| | |
|---|---|
| **Beats** | scalar UTF-8 validators: shiftless DFA validators in Hoehrmann style ('dfa', 'fdfa', 'bdfa', 'dfa2-4' rows), Fuchsia's FIDL string validator ('fushia' rows, fidl_validate_string) and UTF8-CPP (utfcpp) 2.3.4 utf8::is_valid ('utf8lib' row, vendored in dependencies/utf8_v2_3_4) |
| **Claimed result** | README example, hongkong.html: lookup4 20.934 GB/s vs dfa 0.581, fushia 2.612 and utf8lib 2.570 GB/s (about 36x, 8.0x and 8.1x, derived from page data). twitter.json: lookup4 37.0 GB/s vs dfa 0.582, fushia 2.811 and utf8lib 2.577 (about 64x, 13x and 14x, derived). results/skylake.txt, hongkong.html: lookup4avx 17.081 GB/s vs dfa 0.615, fushia 1.578, utf8lib 0.512. Zwegner's AVX validator is slightly faster than lookup4 on twitter.json (41.029 vs 37.0 GB/s in the README run). |
| **Workload** | Validating examples/hongkong.html (1807 KB) and examples/twitter.json (631 KB) with SSE, AVX2 and NEON validators; GB/s, instructions per byte and branch misses reported. |
| **Metric** | throughput |
| **Hardware** | README run at about 3.5 GHz and results/skylake.txt at about 3.69 GHz (Skylake, model not stated); results/rome.txt is also checked in. CPU models are not named. |
| **Compiler and flags** | CMake Release (default build type) with -Wall -Wextra -march=native on GCC/Clang (/arch:AVX2 on MSVC); the Dockerfile (Ubuntu 20.10) installs g++, g++-9 and clang++-9, but no compiler version is tied to the published results |
| **Adoption** | 42 stars; algorithm shipped in simdutf (Node.js, Bun, WebKit per the README) |
| **Last commit** | 2026-04-21 |
| **Links** | [repository](https://github.com/lemire/validateutf8-experiments) · [benchmark](https://github.com/lemire/validateutf8-experiments) |

## Verdict

In the April 2026 README run (unnamed x86 at about 3.5 GHz, CMake Release with -march=native, compiler not stated, hot-cache best-of-N), AVX2 lookup4 validated hongkong.html (1.8 MB) at 20.9 GB/s and twitter.json (631 KB) at 37.0 GB/s. The baselines were a Hoehrmann DFA at 0.58 GB/s, Fuchsia's validator at 2.6-2.8 GB/s and UTF8-CPP 2.3.4 at 2.57 GB/s (about 8-64x), plus the best ASCII-skipping scalar variant at 5.3-6.1 GB/s (about 4-6x). The older results/skylake.txt shows 17.1 GB/s against 0.62 (DFA), 1.58 (Fuchsia) and 0.51 (UTF8-CPP).

## Use it when

- Reproducing or extending the Keiser and Lemire SPE 2021 results, or timing a new validator against lookup2/3/4, Zwegner, range and the older fastvalidate kernel on one harness with instruction and branch-miss counters.
- Choosing a SIMD UTF-8 validation design before porting it to another language or runtime (the README notes the .NET port SimdUnicode came from it).
- Studying the lookup algorithm in a small code base: src/generic/utf8_lookup4_algorithm.h is about 225 commented lines over a thin simd8 wrapper for AVX2, SSE and NEON.

## Skip it when

- Production validation: the README says 'research purposes only: not for production use' and the repo has no LICENSE file; simdutf ships the same algorithm with runtime CPU dispatch.
- You need transcoding, the error offset, or UTF-16/UTF-32 work: the kernels only answer valid or invalid.
- x86 machines without AVX2: on x86-64 the benchmark binds the haswell (AVX2) kernels unconditionally, with no runtime check, and the build uses -march=native.
- Predicting cold-data throughput: every published number is a hot-cache best-of-N run on 0.6-1.8 MB files or 16 KiB synthetic buffers; DRAM-bound throughput is not measured.

## How it is fast

The lookup algorithm classifies every byte together with the byte before it using three 16-entry pshufb/tbl table lookups: the previous byte's high nibble, its low nibble, and the current byte's high nibble. Each lookup returns an 8-bit mask of possible error classes (too short, too long, overlong 2/3/4-byte, surrogate, above U+10FFFF, two continuations), and ANDing the three masks keeps only the errors actually present. A second check uses saturating subtractions on the vectors shifted by 2 and 3 bytes to find positions that must be 3rd or 4th continuation bytes, and XORs that with the first mask. Errors are OR-accumulated with no data-dependent branches, and a 64-byte block that is all ASCII skips the checks, giving about 0.4 instructions per byte on the README's real files and about 1 on random multibyte input.

## Compared with alternatives

None of the listed simd-intrinsics siblings validate UTF-8. The catalogued simdutf, simdutf8 (Rust) and SimdUnicode (.NET) are the production forms of this algorithm, so use this repository only to benchmark or study lookup2/3/4 against Zwegner, range and the older fastvalidate ('basic') kernels on one harness.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the kernels; the benchmark fetches lemire/counters v3.2.0 via CPM and vendors UTF8-CPP 2.3.4 |
| **Minimum toolchain** | C++17, CMake 3.14+; GCC or Clang (-march=native) or MSVC (/arch:AVX2 on x64) |
| **Platforms** | x86-64 with AVX2 (SSE kernels exist in src/sse but are not timed by the driver) and ARM64 NEON; the driver stops with #error on other platforms |
| **Thread safety** | not documented; the lookup4 code read here has no mutable globals (its only static data is a const lookup table), and the checker state lives in a utf8_checker struct |
| **Drop-in for the baseline** | no |

## Gotchas

- The headline ratios depend on which baseline is picked: 36x and 64x are against the plain Hoehrmann DFA (0.58 GB/s, a serial table walk). The strongest scalar baseline in the same 2026 README run, fushia_ascii2 (Fuchsia's validator plus the authors' 16-byte ASCII skip), reached 5.33 GB/s on hongkong.html and 6.14 GB/s on twitter.json, so lookup4 leads a good scalar validator by about 3.9x and 6.0x (derived from page data). On synthetic pure ASCII in results/skylake.txt, fushia_ascii4 reached 29.4 GB/s against 58.7 for lookup4avx (2.0x).
- The utf8lib baseline (vendored UTF8-CPP 2.3.4) depends heavily on the build. On the same file with the same call it ran 22.9 instructions/byte and 0.51 GB/s in results/skylake.txt and 0.38 GB/s in the 2024 README (old Makefile, -O3 without -march=native), but 6.7 instructions/byte and 2.57 GB/s in the 2026 CMake build. fushia stayed at 6.6-6.7 instructions/byte across those runs, so the lookup-versus-utf8lib gap is 8x or 33x depending on which run is quoted, and newer UTF8-CPP releases are not measured.
- Oracle flaw in the tests: the brute-force bit-flip test in tests/unit.cpp requires lookup3 to agree exactly with fidl_validate_string. As adapted in benchmarks/fushia.h, that function range-checks 4-byte sequences with code_point &lt; 0xffff instead of &lt; 0x10000, so it accepts the overlong F0 8F BF BF (U+FFFF); a Python model of the function found this is the only invalid 4-byte sequence it accepts. The benchmark timings are unaffected because every timed input is valid, but a bit flip that produces that sequence would abort the test against a correct lookup3.
- The published tables cover AVX2 only and name no CPU: the README run (April 2026, about 3.5 GHz) gives no model, and results/skylake.txt (about 3.69 GHz) and results/rome.txt (about 3.4 GHz) are identified only by file name. The README table comes from the April 2026 CMake/counters driver, whose real-file section still prints lookup4/basic/range (lookup4avx etc. appear only in the synthetic section), so its row names are current, not stale. Zwegner's validator beat lookup4 on twitter.json in that run (41.0 vs 37.0 GB/s).

## Known shortcomings

- No CPU model and no LICENSE (reference); the utf8lib baseline is a vendored UTF8-CPP 2.3.4; a research artifact behind simdutf (already listed), kept as the lookup-algorithm evidence.
- The 36x/64x headline is against the plain Hoehrmann DFA; the best scalar validator in the same April 2026 run (fushia_ascii2) gives about 3.9x and 6.0x (derived from page data). The utf8lib baseline (UTF8-CPP 2.3.4) is build-sensitive: 22.9 instructions/byte and 0.51 GB/s in results/skylake.txt (old Makefile) vs 6.7 instructions/byte and 2.57 GB/s in the 2026 CMake build. The test oracle fidl_validate_string accepts the overlong F0 8F BF BF (code_point &lt; 0xffff check); only AVX2 is timed and no CPU model is given. The README's lookup4/basic/range rows match the current real-file driver output (April 2026 rerun), so the earlier 'stale row names' caveat was wrong. The 'basic' kernel is the fastvalidate-utf-8 algorithm, 1.35-1.9x slower than lookup4.

## Caveats and trade-offs

Tier B rests on the peer-reviewed paper cited in the README (Keiser and Lemire, Software: Practice and Experience 51(5), 2021), which could not be opened here (arxiv.org unreachable; abstract seen as a search snippet only); the repo itself names no CPU model or compiler version. The README example output uses older row names (lookup4, basic, range) than the current driver prints (lookup4avx, basicavx, rangeavx). results/rome.txt and results/skylake.txt are checked in without CPU models (about 3.4 GHz and 3.69 GHz). No LICENSE file exists in the repo (none in the sidebar), so it is reference only; the README says it is for research, not production. Zwegner's AVX validator beats lookup4 on twitter.json in the README run (41.029 vs 37.000 GB/s). The production form of this algorithm is simdutf, which is already catalogued. [retier] Tier B rests on the peer-reviewed paper cited in the README (Keiser and Lemire, Software: Practice and Experience 51(5), 2021; not opened here); the repo itself names no CPU model or compiler version, and the published tables cover AVX2 only (README run April 2026 at about 3.5 GHz; results/skylake.txt about 3.69 GHz and results/rome.txt about 3.4 GHz identified only by file name). The headline ratios depend on the baseline: 36x and 64x are against the plain Hoehrmann DFA (0.58 GB/s); the strongest scalar baseline in the same 2026 run, fushia_ascii2 (Fuchsia's validator plus a 16-byte ASCII skip), reached 5.33 GB/s on hongkong.html and 6.14 GB/s on twitter.json, so lookup4 leads a good scalar validator by about 3.9x and 6.0x (derived from page data). The utf8lib baseline (vendored UTF8-CPP 2.3.4) depends heavily on the build: 22.9 instructions/byte and 0.51 GB/s in results/skylake.txt (old Makefile) against 6.7 instructions/byte and 2.57 GB/s in the 2026 CMake build. The README's lookup4/basic/range row names match the current real-file driver output (the synthetic section prints lookup4avx etc.), so the table is current. The test oracle fidl_validate_string as adapted in benchmarks/fushia.h range-checks 4-byte sequences with code_point &lt; 0xffff, so it accepts the overlong F0 8F BF BF; timings are unaffected because every timed input is valid. Zwegner's AVX validator beat lookup4 on twitter.json (41.0 vs 37.0 GB/s). No LICENSE file in the repo (reference only); the README says research, not production. The 'basic' kernel is the fastvalidate-utf-8 algorithm, 1.35-1.9x slower than lookup4.

Research code for validation only (no transcoding); x64 SSE/AVX2 and ARM64 NEON paths; README says not for production use.

## Maintenance

Refreshed in April 2026 (CMake, CI, new README run) but explicitly research-only and without a LICENSE file, so reference-only; production users should take simdutf, which carries this algorithm.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** This repo is the artifact of a peer-reviewed paper (Keiser and Lemire, Software: Practice and Experience 51(5), 2021; abstract per search snippet: lookup beats UTF-8 validators used in many libraries and languages by more than 10x), with public benchmark code (benchmarks/benchmark.cpp) and checked-in results; the repo names no CPU model or compiler version for its runs, and the paper could not be opened (arxiv.org unreachable), so it stays at B rather than A.
- **Verifier notes:** README and results/skylake.txt numbers match the record exactly (hongkong.html lookup4 20.934 vs dfa 0.581, fushia 2.612, utf8lib 2.570 GB/s; skylake lookup4avx 17.081 vs dfa 0.615, fushia 1.578, utf8lib 0.512). The 'utf8lib' baseline is the vendored UTF8-CPP 2.3.4, a recognizable incumbent. This is the research artifact behind simdutf's validator (already listed); the orchestrator may prefer to fold it into simdutf as a duplicate.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-76 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/lemire/validateutf8-experiments>
  - <https://github.com/lemire/validateutf8-experiments/commits>
  - <https://raw.githubusercontent.com/lemire/validateutf8-experiments/HEAD/README.md>
  - <https://raw.githubusercontent.com/lemire/validateutf8-experiments/HEAD/results/skylake.txt>
  - <https://raw.githubusercontent.com/lemire/validateutf8-experiments/HEAD/results/rome.txt>
  - <https://raw.githubusercontent.com/lemire/validateutf8-experiments/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/lemire/validateutf8-experiments/HEAD/Dockerfile>
  - <https://raw.githubusercontent.com/lemire/validateutf8-experiments/HEAD/benchmarks/benchmark.cpp>
- **Sources the enricher read:**
  - <https://github.com/lemire/validateutf8-experiments>
  - <https://github.com/lemire/validateutf8-experiments/commits>
  - <https://github.com/lemire/validateutf8-experiments/issues?q=is%3Aissue>
  - <https://github.com/lemire/validateutf8-experiments/issues/1>
  - <https://raw.githubusercontent.com/lemire/validateutf8-experiments/HEAD/README.md>
  - <https://raw.githubusercontent.com/lemire/validateutf8-experiments/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/lemire/validateutf8-experiments/HEAD/Dockerfile>
  - <https://raw.githubusercontent.com/lemire/validateutf8-experiments/HEAD/benchmarks/benchmark.cpp>
  - <https://raw.githubusercontent.com/lemire/validateutf8-experiments/HEAD/benchmarks/benchstream.cpp>
  - <https://raw.githubusercontent.com/lemire/validateutf8-experiments/HEAD/benchmarks/fushia.h>
  - <https://raw.githubusercontent.com/lemire/validateutf8-experiments/HEAD/benchmarks/hoehrmann.h>
  - <https://raw.githubusercontent.com/lemire/validateutf8-experiments/HEAD/benchmarks/random_utf8.cpp>
  - <https://raw.githubusercontent.com/lemire/validateutf8-experiments/HEAD/benchmarks/random_utf8.h>
  - <https://raw.githubusercontent.com/lemire/validateutf8-experiments/HEAD/src/generic/utf8_lookup4_algorithm.h>
  - <https://raw.githubusercontent.com/lemire/validateutf8-experiments/HEAD/src/generic/utf8_fastvalidate_algorithm.h>
  - <https://raw.githubusercontent.com/lemire/validateutf8-experiments/HEAD/src/avx2/implementations.h>
  - <https://raw.githubusercontent.com/lemire/validateutf8-experiments/HEAD/tests/unit.cpp>
  - <https://raw.githubusercontent.com/lemire/validateutf8-experiments/HEAD/dependencies/utf8_v2_3_4/source/utf8/core.h>
  - <https://raw.githubusercontent.com/lemire/validateutf8-experiments/HEAD/results/skylake.txt>
  - <https://raw.githubusercontent.com/lemire/validateutf8-experiments/HEAD/results/rome.txt>
  - <https://raw.githubusercontent.com/lemire/validateutf8-experiments/87f94e8/README.md>
  - <https://raw.githubusercontent.com/lemire/validateutf8-experiments/87f94e8/Makefile>
  - <https://raw.githubusercontent.com/lemire/validateutf8-experiments/87f94e8/benchmarks/benchmark.cpp>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/lemire/validateutf8-experiments`) · [data/wave13/enrich/raw/github_com_lemire_validateutf8_experiments.json](../../../data/wave13/enrich/raw/github_com_lemire_validateutf8_experiments.json) (enrichment confidence 0.8)

</details>
