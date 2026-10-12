# simdrng

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Study only · `C++` · `BSD-3-Clause-Attribution` · 🟢 active

> C++20 xoshiro256++, ChaCha and Philox engines with xsimd SIMD bulk fill; beats std::mt19937_64 per call and in bulk.

| | |
|---|---|
| **Beats** | std::mt19937_64 and std::uniform_real_distribution; also scalar xoshiro256++ |
| **Claimed result** | gcc-15 benchmark JSON (2026-07-22): XoshiroSIMD fill_u64 1645 ns per 4096 values (2.49e9 values/s) vs scalar Xoshiro fill_u64 3835 ns (1.07e9 values/s), about 2.3x (derived from page data); SIMD Philox4x32 fill 7970 vs scalar 27502 ns (about 3.5x) and ChaCha20 21555 vs 61019 ns (about 2.8x) (derived from page data). Scalar Xoshiro uniform() 1.32 ns vs the same engine through std::uniform_real_distribution 4.65 ns (about 3.5x) and vs std::mt19937_64 + std::uniform_real_distribution 8.01 ns (about 6x) (derived from page data); std::mt19937_64 single u64 call 1.60 ns vs scalar Xoshiro 0.94 ns. docs/benchmarks.rst: Xoshiro bulk 'reaches \~2.3x its scalar loop'; uniform() \~1.6 ns vs \~5.2 ns, 'roughly 3x' (a different run). |
| **Workload** | Google Benchmark runs (CI, GitHub-hosted runner) of per-call u64, per-call double and buffer fill for Xoshiro256++, ChaCha and Philox, scalar versus xsimd-dispatched SIMD, against std::mt19937_64. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 7763 (GitHub-hosted runner, 4 vCPUs, 2.445 GHz; cpu_model.txt in results) |
| **Compiler and flags** | GCC 15, CMake Release, CMAKE_CXX_FLAGS=-march=x86-64-v3 (bench preset in CMakePresets.json); also clang-19/20 and gcc-14 result sets on the same branch |
| **Adoption** | 3 stars |
| **Last commit** | 2026-07-22 |
| **Links** | [repository](https://github.com/DiamonDinoia/simdrng) · [benchmark](https://raw.githubusercontent.com/DiamonDinoia/simdrng/benchmark-results/results/gcc-15/20260722T164804Z.json) |

## Verdict

The project's CI Google Benchmark run (gcc-15, Release, -march=x86-64-v3, AMD EPYC 7763 GitHub runner, libstdc++) measured XoshiroSIMD bulk fill at 1645 ns per 4096 u64 vs 3835 ns for the scalar loop (about 2.3x), Philox4x32 3.5x and ChaCha20 2.8x SIMD over scalar fills. Against the standard library it measured per-call times only: std::mt19937_64 1.60 ns vs XoshiroScalar 0.94 ns, and std::mt19937_64 + std::uniform_real_distribution 8.01 ns vs XoshiroScalar::uniform() 1.32 ns; std::mt19937_64 was never timed in bulk.

## Use it when

- Filling large u64 buffers (Monte Carlo batches, tensors, NumPy arrays): XoshiroSIMD generate() measured 0.40 ns/value vs 0.94 ns for the scalar loop on an AVX2 EPYC 7763
- Replacing std::mt19937_64 + std::uniform_real_distribution in a per-call loop: XoshiroScalar::uniform() was 1.32 ns vs 8.01 ns
- Counter-based reproducible streams across threads or MPI ranks: Philox4x32 SIMD bulk fill was about 3.5x its scalar version, and Philox derives sub-streams from (seed, counter) without coordination
- One binary shipped to mixed x86 fleets, built with SIMDRNG_DISPATCH=ON so the AVX-512/AVX2/SSE2 tier is picked at runtime (NEON and RVV128 on other ISAs)
- Python code that wants a drop-in numpy.random.Generator backed by a GIL-released C++ bulk fill

## Skip it when

- Cheap engines consumed one value at a time: XoshiroSIMD/XoshiroNative cost 2.81-2.82 ns per call vs 0.94 ns for XoshiroScalar because of the buffered read, so stay scalar there
- Results that must be bit-identical across machines: the SIMD stream interleaves SIMD_WIDTH lanes, so the same seed gives different sequences on SSE2 (2 lanes), AVX2 (4) and AVX-512 (8); use XoshiroScalar or Philox/ChaCha with fixed counters
- Double-precision bulk fill expecting the u64 speedup: fill_uniform went through a 256-value temporary and measured 4219 ns vs 5116 ns scalar per 4096 doubles (about 1.2x, derived from page data)
- Projects that need a stable API or a permissive OSI license: pre-1.0 with no tagged release, and the BSD-3-Clause-Attribution license adds an acknowledgement clause for every redistribution
- Security uses, unless you vet it yourself: the ChaCha guide calls ChaCha12/20 'the cryptographic choices', but there is no claim of constant-time code, key handling or reseeding, so treat it as a statistical generator

## How it is fast

The SIMD engines keep SIMD_WIDTH independent xoshiro256++ states in the lanes of four xsimd registers, lane i being the scalar generator after i jump() calls (2^128 steps), so one vector step yields 2/4/8 outputs on SSE2/AVX2/AVX-512. generate() writes whole 256-value blocks straight to the caller's buffer with unrolled unaligned vector stores; single-value calls drain a 256-entry cache refilled by the same code. The scalar uniform() uses the (x &gt;&gt; 11) \* 2^-53 conversion from Vigna's notes instead of std::uniform_real_distribution, and the scalar engine is a constexpr inlined port of the reference xoshiro256plusplus.c. ChaCha and Philox gain more from SIMD because their per-value compute is heavier.

## Compared with alternatives

Pick simdrng over Xoshiro256PlusSIMD or the xoshiro8x256pp gist when you want a maintained, tested package with runtime ISA dispatch, std-compatible engines, xoshiro256++ (not 256+) and Philox/ChaCha in one place. Pick VMT19937 instead if you must keep Mersenne Twister output, and SHISHUA or the AES-based testingRNG generators if raw byte throughput matters more than a standard algorithm.

## Integration

| | |
|---|---|
| **Form** | header-only for scalar and \*Native types; static/shared lib (small dispatch TUs) for the runtime-dispatched \*SIMD types; single-header amalgamation on the single-header branch (Native types only) |
| **Dependencies** | none for the scalar path; xsimd 14.3.0 and DiamonDinoia/poet (pinned SHA) for SIMD types, fetched via CPM; Google Benchmark/Catch2 for tests; nanobind for Python |
| **Minimum toolchain** | C++20 (INTERFACE cxx_std_20), CMake 3.29; CI covers GCC 13/14, Clang 18/20, Apple Clang (macos-14) and MSVC (windows-2022) |
| **Platforms** | x86-64 (SSE2/AVX2/AVX-512BW tiers), aarch64 (NEON dispatch tier; an SVE instantiation is declared when xsimd has SVE enabled), riscv64 (RVV, VLEN 128); scalar path anywhere |
| **Thread safety** | Instances hold no shared or global state and are heap-free (docs/benchmarks.rst), so one generator per thread is safe; a single instance is not synchronized |
| **Drop-in for the baseline** | partial: satisfies UniformRandomBitGenerator and works with std distributions, but it is a different generator from std::mt19937_64 (different sequence), and the speedup on doubles needs uniform()/fill_uniform rather than std::uniform_real_distribution |

## Gotchas

- simdrng::Xoshiro is not the scalar engine: xoshiro.hpp aliases it to XoshiroSIMD with SIMDRNG_DISPATCH=ON and to XoshiroNative (non-portable, build-host -march) by default, while docs/guides/xoshiro.rst says it falls back to XoshiroScalar. Name XoshiroScalar explicitly for per-call use.
- Stream overlap when mixing types: XoshiroScalar(seed, t) jumps t times by 2^128, which is exactly lane t of XoshiroSIMD(seed); SIMD thread_id uses mid_jump (2^160) instead. Do not mix scalar thread streams and SIMD engines on the same seed.
- On SIMD types jump(n) advances every lane by n (so n x SIMD_WIDTH outputs of the interleaved stream) and does not flush values already in the 256-entry cache (from xoshiro_simd.hpp).
- Each SIMD instance carries a 2 KiB output cache plus up to 256 bytes of 64-byte-aligned state, and the runtime-dispatch types need the compiled library; they are not available from the single header.

## Known shortcomings

- Single-value SIMD calls are 3x slower than scalar (wins need bulk generation); BSD-3-Clause-Attribution is not OSI-approved, so reference.
- The simdrng::Xoshiro alias is the buffered XoshiroNative/XoshiroSIMD (2.8 ns per call), not the scalar engine, contrary to the docs guide. XoshiroScalar(seed,t) produces the same stream as lane t of XoshiroSIMD(seed), so mixing them overlaps streams. SIMD output depends on ISA width. fill_double gains only \~1.2x; std::mt19937_64 was timed per call only.

## Caveats and trade-offs

The gain is for bulk fills only: single-value SIMD calls cost 2.82 ns vs 0.94 ns for scalar Xoshiro (buffered read overhead, per the docs), so one-at-a-time use should stay scalar. The SIMD stream interleaves SIMD_WIDTH xoshiro256++ lanes, lane i being the scalar generator after i jump() calls (tests/test_xoshiro_simd.cpp checks each lane against the scalar engine, which tests/test_xoshiro.cpp checks against Vigna's xoshiro256plusplus.c), so it is the same generator but a different output order than one scalar stream for the same seed. The std::mt19937_64 figure is a per-call time, not a bulk fill. Shared GitHub-hosted runner; cpu_model.txt is rewritten on each publish run. libstdc++ inferred from gcc-15 on ubuntu-24.04. License is BSD-3-Clause with an added acknowledgement clause (SPDX BSD-3-Clause-Attribution, not OSI-approved), so marked reference although permissive. Pre-1.0, no tagged release, 3 stars.

Header-only C++20 with xsimd runtime dispatch and numpy.random.Generator-compatible Python bindings (nanobind); the SIMD engines are faster only in bulk fills (single-call SIMD xoshiro is 2.81 ns vs 0.94 ns scalar) and produce lane-interleaved streams.

## Maintenance

Active (last commit 2026-07-22, 151 commits, CI on Linux/macOS/Windows with sanitizers and static analysis) but pre-1.0, single author, 3 stars, and under a BSD-3-Clause-Attribution license that requires an acknowledgement, so listed as reference rather than copyable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** Benchmark code is public (tests/benchmarks.cpp, Google Benchmark with DoNotOptimize/ClobberMemory on the filled buffer), the CI workflow (.github/workflows/benchmarks.yml) builds with the 'bench' preset (Release, -march=x86-64-v3) for gcc-14/15 and clang-19/20 and records the CPU (cpu_model.txt: AMD EPYC 7763). The gcc-15 JSON contains every number in the record.
- **Verifier notes:** Numbers match the gcc-15 JSON exactly. RNG check passed: the SIMD path is per-lane xoshiro256++ verified against the scalar reference, not a different generator. Last commit 2026-07-22 on main (151 commits, 3 stars, 1 fork); LICENSE text confirmed as BSD-3-Clause plus attribution clause 4.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/DiamonDinoia/simdrng/benchmark-results/results/gcc-15/20260722T164804Z.json>
  - <https://raw.githubusercontent.com/DiamonDinoia/simdrng/benchmark-results/results/gcc-15/cpu_model.txt>
  - <https://github.com/DiamonDinoia/simdrng>
  - <https://github.com/DiamonDinoia/simdrng/commits/main>
  - <https://github.com/DiamonDinoia/simdrng/tree/main/tests>
  - <https://github.com/DiamonDinoia/simdrng/tree/main/.github/workflows>
  - <https://raw.githubusercontent.com/DiamonDinoia/simdrng/main/readme.md>
  - <https://raw.githubusercontent.com/DiamonDinoia/simdrng/main/docs/benchmarks.rst>
  - <https://raw.githubusercontent.com/DiamonDinoia/simdrng/main/LICENSE>
  - <https://raw.githubusercontent.com/DiamonDinoia/simdrng/main/CMakePresets.json>
  - <https://raw.githubusercontent.com/DiamonDinoia/simdrng/main/.github/workflows/benchmarks.yml>
  - <https://raw.githubusercontent.com/DiamonDinoia/simdrng/main/tests/benchmarks.cpp>
  - <https://raw.githubusercontent.com/DiamonDinoia/simdrng/main/tests/test_xoshiro_simd.cpp>
  - <https://raw.githubusercontent.com/DiamonDinoia/simdrng/main/tests/test_xoshiro.cpp>
- **Sources the enricher read:**
  - <https://github.com/DiamonDinoia/simdrng>
  - <https://github.com/DiamonDinoia/simdrng/issues>
  - <https://github.com/DiamonDinoia/simdrng/tree/main/include/simdrng>
  - <https://github.com/DiamonDinoia/simdrng/tree/main/docs>
  - <https://github.com/DiamonDinoia/simdrng/tree/main/docs/guides>
  - <https://raw.githubusercontent.com/DiamonDinoia/simdrng/main/readme.md>
  - <https://raw.githubusercontent.com/DiamonDinoia/simdrng/main/docs/benchmarks.rst>
  - <https://raw.githubusercontent.com/DiamonDinoia/simdrng/main/docs/guides/xoshiro.rst>
  - <https://raw.githubusercontent.com/DiamonDinoia/simdrng/main/docs/guides/chacha.rst>
  - <https://raw.githubusercontent.com/DiamonDinoia/simdrng/main/LICENSE>
  - <https://raw.githubusercontent.com/DiamonDinoia/simdrng/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/DiamonDinoia/simdrng/main/CMakePresets.json>
  - <https://raw.githubusercontent.com/DiamonDinoia/simdrng/main/include/simdrng/xoshiro.hpp>
  - <https://raw.githubusercontent.com/DiamonDinoia/simdrng/main/include/simdrng/xoshiro_scalar.hpp>
  - <https://raw.githubusercontent.com/DiamonDinoia/simdrng/main/include/simdrng/xoshiro_simd.hpp>
  - <https://raw.githubusercontent.com/DiamonDinoia/simdrng/main/include/simdrng/dispatch_arch.hpp>
  - <https://raw.githubusercontent.com/DiamonDinoia/simdrng/main/include/simdrng/macros.hpp>
  - <https://raw.githubusercontent.com/DiamonDinoia/simdrng/main/include/simdrng/philox_simd.hpp>
  - <https://raw.githubusercontent.com/DiamonDinoia/simdrng/main/include/simdrng/chacha.hpp>
  - <https://raw.githubusercontent.com/DiamonDinoia/simdrng/main/tests/benchmarks.cpp>
  - <https://raw.githubusercontent.com/DiamonDinoia/simdrng/main/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/DiamonDinoia/simdrng/main/.github/workflows/benchmarks.yml>
  - <https://raw.githubusercontent.com/DiamonDinoia/simdrng/benchmark-results/results/gcc-15/20260722T164804Z.json>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/diamondinoia/simdrng`) · [data/wave8/enrich/raw/github_com_diamondinoia_simdrng.json](../../../data/wave8/enrich/raw/github_com_diamondinoia_simdrng.json) (enrichment confidence 0.85)

</details>
