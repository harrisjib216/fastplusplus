# TzdLanguage NTT BigInt multiplier

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++ (CUDA)` · `MIT (stated only in the README and badge; there is no LICENSE file in the repository: raw main/LICENSE and github.com blob/main/LICENSE both 404)` · 🟢 active

> 3-prime NTT big-integer multiply (AVX2 CPU, CUDA GPU) inside a Windows hobby language; beats single-core GMP only on GPU or decimal I/O.

| | |
|---|---|
| **Beats** | GNU GMP 6.3.0 (single-core mpz_mul) |
| **Claimed result** | README/wiki, 4,741,006-digit operands on i7-4790 + P106-090: CPU AVX2 NTT convolution 54.02 ms vs single-core GMP 6.3.0 mpz_mul 111.78 ms (2.07x as stated); GPU NTT kernel 29.20 ms (3.83x as stated); 8-thread Karatsuba-wrapped GMP 84.58 ms. End-to-end decimal string in to decimal string out: CPU 175.41 ms and GPU 56.52 ms vs single-core GMP 2,549.30 ms (14.5x and 45.1x as stated). The wiki's own breakdown (parse 10.64 + ntt 54.02 + crt_carry 97.08 + format 13.67 ms) shows that the 54.02 ms leaves out CRT reconstruction and carry propagation. The complete CPU product is therefore 151.10 ms, which is 1.35x SLOWER than single-core GMP's 111.78 ms (derived from page data), even though the CPU engine uses OpenMP on all 8 threads. The complete GPU product (ntt=42.01 ms including CRT/carry/copy) is 2.66x faster than single-core GMP (derived from page data). Almost all of the end-to-end gain comes from base-10^9 storage avoiding GMP's binary/decimal conversion (686.85 ms parse + 1,750.67 ms mpz_get_str). |
| **Workload** | Multiplication of two 4,741,006-digit integers using a 3-prime NTT with Garner CRT on CPU (AVX2) and GPU (CUDA). |
| **Metric** | latency |
| **Hardware** | Intel Core i7-4790 (4C/8T, 3.60 GHz); NVIDIA P106-090 GPU (Pascal, 192 GB/s) |
| **Compiler and flags** | GMP harness: MSVC cl /O2 /openmp /EHsc /std:c++17 (test/run_bench_gmp_mt.bat), linked against vcpkg x64-windows gmp.lib (whether GMP's assembly kernels were enabled is not stated). TzdTools: MSVC (Visual Studio 2026 / v145) Release via CMakeLists.txt with /arch:AVX2 /openmp; exact optimization flags for the timed build not stated. |
| **Adoption** | 10 stars |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/tzdwindows/TzdLanguage) · [benchmark](https://github.com/tzdwindows/TzdLanguage) |

## Verdict

First-party README/wiki figures for one 4,741,006-digit multiplication on an Intel Core i7-4790 (4C/8T) and an NVIDIA P106-090: GPU NTT kernel 29.20 ms (42.01 ms with CRT, carry and copy) and CPU AVX2 NTT 54.02 ms (151.1 ms with CRT/carry) vs single-core GMP 6.3.0 mpz_mul 111.78 ms from a vcpkg MSVC build (cl /O2 /openmp), so only the GPU path beats GMP on the multiply itself (about 2.66x, derived from page data); end-to-end decimal-string-to-string times are 56.52 ms GPU and 175.41 ms CPU vs 2,549.30 ms for GMP.

## Use it when

- As reference code for a 3-prime 32-bit NTT multiplier with AVX2 Montgomery arithmetic and four-step cache blocking.
- Workloads that start and end as decimal strings of millions of digits (e.g. printing huge products), where avoiding binary/decimal conversion dominates: the wiki's end-to-end run is 175 ms CPU and 57 ms GPU vs 2,549 ms for single-core GMP at 4.74M digits.
- Windows x64 machines with an NVIDIA GPU of compute capability 6.0+ when one multiplication of roughly 1M-38M digits must finish faster than single-core GMP (GPU kernel 29.2 ms vs 111.8 ms at 4.74M digits; complete GPU product 42.0 ms).

## Skip it when

- As a faster CPU multiplier than GMP: the complete CPU product (54.02 ms NTT + 97.08 ms CRT/carry = 151.1 ms on 8 threads) is slower than single-threaded GMP mpz_mul (111.78 ms) on the same i7-4790.
- Any project that needs a library: the code is embedded in an interpreter that also pulls in ANTLR-generated sources, LLVM, LibTorch and CUDA, and the repository has no LICENSE file (MIT appears only in the README and badge).
- Linux, macOS or non-AVX2 CPUs: the CPU engine uses AVX2 intrinsics unconditionally and the MSVC _umul128 intrinsic, and the README lists Windows 10/11 x64 with Visual Studio as the platform.
- Very large operands on the CPU path: nothing checks the 2^22-element transform limit (P2 = 235\*2^22+1), so combined inputs above about 4.19M limbs (\~37.7M digits) would compute with an invalid root of unity; the GPU path throws instead.
- Anything beyond multiplication of non-negative decimal strings with a sign: no division, modular arithmetic or binary-limb interface is exposed by this engine.

## How it is fast

Numbers are stored as base-10^9 limbs, so parsing and printing decimal strings is linear chunking instead of GMP's binary/decimal radix conversion, which is where most of the 14.5x/45.1x end-to-end gains come from. The product is a cyclic convolution done as three 32-bit NTTs (primes 998244353, 985661441, 754974721 in the current source) with AVX2 Montgomery multiplication, Bailey's four-step decomposition into cache-sized row transforms with tiled transposes, OpenMP threads, and Garner CRT reconstruction. The GPU engine runs the same scheme as NVRTC-compiled Stockham kernels with shared-memory padding and a parallel carry scan.

## Compared with alternatives

Pick FLINT or mp++ for a maintained library that beats GMP on large multiplications with full arithmetic, and CGBN or the GMP-on-GPU entries for batched fixed-size GPU work; TzdLanguage is only worth opening as readable NTT/CRT example code or if your inputs and outputs are huge decimal strings on a Windows/CUDA box.

## Integration

| | |
|---|---|
| **Form** | source-drop (two files inside an interpreter; no library target) |
| **Dependencies** | CPU engine: OpenMP, AVX2, MSVC intrinsics (_umul128); GPU engine: CUDA Toolkit 12+ with NVRTC, LibTorch (used to detect CUDA), compute capability 6.0+; the full build also wants LLVM and ANTLR4 |
| **Minimum toolchain** | C++20 (CMakeLists.txt), Visual Studio 2022/2026 (MSVC v143/v145) or CMake 3.20+ |
| **Platforms** | Windows 10/11 x64 only per README; AVX2 required for the CPU engine; NVIDIA Pascal or newer for the GPU engine |
| **Thread safety** | not documented; the CPU engine's global twiddle cache checks its size outside the mutex and sets the new size before the tables are built, so concurrent multiplications of different sizes can race |
| **Drop-in for the baseline** | no |

## Gotchas

- The headline CPU '2.07x faster than GMP' times only the NTT phase; the --bigTime breakdown shows a 97.08 ms serial CRT/carry step that is excluded, and the GMP side is a complete mpz_mul.
- The wiki and the code disagree: the wiki lists primes 469762049/167772161/754974721, a Kogge-Stone carry chain and a fast_div_1e9 helper for the CPU path, while TzdExperimentalCompute.cpp uses 998244353/985661441/754974721, a sequential carry loop and plain division. The wiki's fast_div_1e9 snippet also returns a wrong quotient for some inputs above about 1.23e19 (checked by script), though the current code does not call it.
- README and wiki give two different multi-threaded GMP end-to-end figures (\~519 ms and 2,522.09 ms), and the 'multi-threaded GMP' rows are the author's own Karatsuba split over mpz_mul, not a GMP feature; all figures are single runs.
- GPU timings are taken after a warm-up multiplication at the same size with cached device buffers and twiddles (the sample output shows alloc=0.00 ms, twiddle=0.00 ms), and the kernels are NVRTC-compiled with --use_fast_math.

## Known shortcomings

- Misleading CPU ratio: the 54.02 ms 'pure' multiply excludes 97.08 ms of CRT/carry; the full 8-thread CPU multiply (151.10 ms) is slower than single-core GMP (111.78 ms) (derived from page data). Only the GPU path (42.01 ms full) and decimal-I/O end-to-end win.
- Claim not reproducible: tables contradict each other (MT GMP end-to-end \~519 vs 2,522 ms; GPU page says 'over 10x' vs 3.83x measured); single runs; GMP built with vcpkg + MSVC, asm config unknown; code lives inside a Windows-only interpreter, not a library; no LICENSE file (MIT stated in README only).
- Correctness bug: the CPU NTT path never checks the 2^22 transform limit (P2=235\*2^22+1), so inputs above \~4.19M combined limbs (\~37.7M digits) use an invalid root and give a silently wrong product (the GPU path throws); race: the global twiddle cache checks size outside the mutex and sets size before the tables are built; the wiki's primes, carry scheme and fast_div_1e9 do not match the code; LICENSE still 404.

## Caveats and trade-offs

First-party numbers from a 17-day-old language project (first commit 2026-09-13, 81 commits, 10 stars). The NTT multiply is buried in a Windows/MSVC-only interpreter (Generated/TzdExperimentalCompute.cpp uses _umul128; GPU path in TzdPyTorch.cpp) and works on decimal strings. It is not a standalone library. The CPU 2.07x 'pure multiply' ratio compares a multi-threaded NTT convolution that excludes the 97.08 ms CRT/carry step with a complete single-threaded mpz_mul; the complete CPU multiply (151.10 ms) is slower than single-core GMP. The pages contradict each other: the README and CPU wiki give multi-threaded GMP end-to-end as \~519 ms in one place and 2,522.09 ms in the table, and the GPU wiki claims 'over 10x' over GMP for the 29.20 ms kernel (3.83x). The GPU wiki links the benchmark source as a file:/// path on the author's machine. The 'multi-threaded GMP' rows are the author's own Karatsuba split over mpz_mul, not a GMP feature. GMP was a vcpkg MSVC build with unknown asm configuration. Each figure is a single run (iters=1 at 4.74M digits). No LICENSE file (MIT is declared only in the README).

The NTT multiplier lives inside a programming-language interpreter (src files TzdExperimentalCompute.cpp for the CPU engine, TzdPyTorch.cpp for the GPU engine) and surfaces through language-level operations, not as a standalone library; extracting it takes work. Single operand size tested.

## Maintenance

Very young (first commit 2026-09-13, 81 commits, 10 stars, last commit 2026-09-30) and changing daily; no LICENSE file was present on 2026-10-01 (raw LICENSE 404) despite the README's MIT claim, so copying the code carries licence risk until one is added.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party README and wiki tables only; the GMP side has public code (test/bench_gmp_mt.cpp, built by test/run_bench_gmp_mt.bat with MSVC cl /O2 /openmp against a vcpkg x64-windows gmp.lib), but the TzdLang side is timed by the interpreter's own --bigTime output on a script, the two pages disagree with each other, and the headline CPU ratio leaves out the NTT path's CRT/carry step, so it falls short of A and stays C.
- **Verifier notes:** Page numbers match the record, but the page's own phase breakdown undercuts the CPU claim: with CRT/carry included, the AVX2 NTT path takes 151.10 ms and is slower than single-core GMP. Only the GPU path and the decimal-I/O end-to-end case show real wins. Record as shortcomings: not reproducible (single run, inconsistent tables), a misleading ratio, and embedded in an interpreter rather than a library.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `license`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/tzdwindows/TzdLanguage>
  - <https://github.com/tzdwindows/TzdLanguage/commits>
  - <https://github.com/tzdwindows/TzdLanguage/blob/main/LICENSE>
  - <https://raw.githubusercontent.com/tzdwindows/TzdLanguage/HEAD/README.md>
  - <https://raw.githubusercontent.com/tzdwindows/TzdLanguage/HEAD/wiki/CPU-NTT-BigInt.md>
  - <https://raw.githubusercontent.com/tzdwindows/TzdLanguage/HEAD/wiki/GPU-NTT-BigInt.md>
  - <https://raw.githubusercontent.com/tzdwindows/TzdLanguage/HEAD/test/bench_gmp_mt.cpp>
  - <https://raw.githubusercontent.com/tzdwindows/TzdLanguage/HEAD/test/run_bench_gmp_mt.bat>
  - <https://raw.githubusercontent.com/tzdwindows/TzdLanguage/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/tzdwindows/TzdLanguage/HEAD/Generated/TzdExperimentalCompute.cpp>
- **Sources the enricher read:**
  - <https://github.com/tzdwindows/TzdLanguage>
  - <https://github.com/tzdwindows/TzdLanguage/commits>
  - <https://github.com/tzdwindows/TzdLanguage/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/tzdwindows/TzdLanguage/HEAD/README.md>
  - <https://raw.githubusercontent.com/tzdwindows/TzdLanguage/HEAD/wiki/CPU-NTT-BigInt.md>
  - <https://raw.githubusercontent.com/tzdwindows/TzdLanguage/HEAD/wiki/GPU-NTT-BigInt.md>
  - <https://raw.githubusercontent.com/tzdwindows/TzdLanguage/HEAD/test/bench_gmp_mt.cpp>
  - <https://raw.githubusercontent.com/tzdwindows/TzdLanguage/HEAD/test/run_bench_gmp_mt.bat>
  - <https://raw.githubusercontent.com/tzdwindows/TzdLanguage/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/tzdwindows/TzdLanguage/HEAD/Generated/TzdExperimentalCompute.cpp>
  - <https://raw.githubusercontent.com/tzdwindows/TzdLanguage/HEAD/Generated/TzdExperimentalCompute.h>
  - <https://raw.githubusercontent.com/tzdwindows/TzdLanguage/HEAD/Generated/TzdPyTorch.cpp>
  - <https://raw.githubusercontent.com/tzdwindows/TzdLanguage/HEAD/LICENSE>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/tzdwindows/tzdlanguage`) · [data/wave8/enrich/raw/github_com_tzdwindows_tzdlanguage.json](../../../data/wave8/enrich/raw/github_com_tzdwindows_tzdlanguage.json) (enrichment confidence 0.75)

</details>
