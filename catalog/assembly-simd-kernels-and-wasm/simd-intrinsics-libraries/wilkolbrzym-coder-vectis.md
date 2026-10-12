# Vectis

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> New header-only C++20 vec&lt;T,N&gt; SIMD engine (scalar, AVX2, AVX-512) whose AVX2 dot kernels beat a naive scalar loop 13.9x.

| | |
|---|---|
| **Beats** | scalar C++ loop (and the same loop with four independent accumulators, and the same loop built with -ffast-math), as the reference for an AVX2 intrinsics/assembly dot-product kernel |
| **Claimed result** | README 'The assembly verdict' table, dot_f32 at n = 1024 floats, L1-resident, min of 21 runs: scalar 1491 ns (4.92 cycles/element, 1.00x), scalar-4acc 679 ns (1.73 cycles/element, 2.05x), intrinsics 107 ns (0.338 cycles/element, 13.93x), asm 107 ns (0.333 cycles/element, 13.93x); against the four-accumulator scalar loop the vector kernels are about 6.3x faster (derived from page data). The README also states that the naive loop compiled with -ffast-math reaches 6.9x, but no benchmark in the repo measures that row (README text only). saxpy at n = 1024: asm 100 ns versus intrinsics 132 ns (1.28x), a small-n effect that disappears at DRAM sizes where asm sometimes loses (0.92x). SoA table (bench_soa.cpp): SoA vectorised 1.61x (n=8) and 1.37x (n=16) over AoS scalar at 28 KiB, 1.41x/1.28x at 448 KiB, 0.95x-0.96x at 7 MiB, 0.95x/0.87x at 112 MiB. |
| **Workload** | dot_f32 over n = 1024 floats, L1-resident, min of 21 runs, comparing scalar, scalar-4acc, intrinsics and hand-written GAS assembly twins with the same shape. |
| **Metric** | latency |
| **Hardware** | Intel i5-6500T (Skylake, AVX2, FMA, no AVX-512), 32 KiB L1d, powersave governor |
| **Compiler and flags** | Compiler and version for the README benchmark numbers are not stated (README names GCC 15 and GCC 16 only for the test suites and reflection; CI builds with g++-13 to g++-16 and clang++-18/19). Build per README: CMake Release (CMake default -O3 -DNDEBUG; the bench_simd.cpp comment says -O2) with -DVECTIS_ISA_TIER=avx2, i.e. -march=x86-64-v3 -mno-avx512f -mno-avx512bw -mno-avx512dq -mno-avx512vl. bench_asm times each single call with std::chrono::steady_clock, reports the min of 21 runs after 3 warmups, and derives cycles/element from rdtsc averaged over the whole 21-run batch. |
| **Adoption** | 0 stars, 0 forks, 7 commits, all on 2026-09-20 and 2026-09-21 |
| **Last commit** | 2026-09-21 |
| **Links** | [repository](https://github.com/wilkolbrzym-coder/Vectis) · [benchmark](https://github.com/wilkolbrzym-coder/Vectis) |

## Verdict

On the author's Intel i5-6500T (Skylake, powersave governor), a hand-written AVX2 dot_f32 over 1024 L1-resident floats takes 107 ns (min of 21) in both intrinsics and GAS assembly versus 1491 ns for a one-accumulator scalar loop (13.93x) and 679 ns for a four-accumulator scalar loop (about 6.3x, derived from page data), built with CMake Release at -march=x86-64-v3 with AVX-512 disabled and an unstated GCC version. No AVX-512 number exists, and the README attributes most of the gain to summation order rather than width.

## Use it when

- Learning or prototyping explicit SIMD on x86-64 with AVX2: the code base is small, heavily commented, and its scalar backend is a bit-exact oracle you can test against.
- Float reductions (dot products, sums) over L1/L2-resident arrays where an explicit multi-accumulator order is acceptable and -ffast-math is not.
- Particle-style kernels over a handful of float fields that stay in SoA form across several passes and fit in L1/L2 (README: SoA 1.3-1.6x over AoS scalar there).
- GCC 16 users who want AoS-to-SoA conversion generated from the struct by reflection without a field list.

## Skip it when

- Production code: the repository is a few weeks old (7 commits on 2026-09-20/21, 0 stars, version 0.1.1), and commit 76b4ecc, made the same day as the first code commit, fixed AVX2 mask factories that were wrong for 254 of 256 bit patterns plus a per-lane constructor over-read.
- ARM or other non-x86 targets: there is no NEON or SVE backend, so the whole library runs its scalar path there.
- Transcendental math (exp, log, sin, cos), int8/int16 lanes, gather/scatter or compress/expand: all absent.
- Bandwidth-bound data (L3 or DRAM-sized arrays): SoA ties or loses to AoS (0.87-0.96x) and the vector kernels converge on memory bandwidth; AoS-to-SoA conversion costs 2-4x a kernel pass at large sizes.
- MSVC builds (the CMake script rejects non-GCC/Clang compilers) or builds that pass no -march, which silently get the scalar backend.

## How it is fast

Explicit 256-bit (AVX2) or 512-bit (AVX-512) lanes with FMA, and above all the freedom to choose the floating-point reduction order: the benchmarked dot kernels keep four independent 8-lane accumulators, breaking the serial dependency chain that an IEEE-strict compiler cannot reassociate without -ffast-math. The README's own breakdown attributes most of the 13.9x to that reassociation (four scalar accumulators alone give 2.05x) and under 2.3x to width and FMA. Capability concepts remove operations a backend lacks (for example 64-bit multiply on AVX2) at compile time instead of emulating them.

## Compared with alternatives

EVE covers far more ISAs (including NEON and SVE) and operations, and the Vector Class Library has years of use plus SVML-style math functions, so either is the default choice; pick Vectis only if you want a small AVX2/AVX-512 engine you can read end to end, with compile-time capability concepts and reflection-generated SoA. Against marcelcases/simd it is a library rather than a set of example kernels.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (optional GAS assembly object for the asm kernels; CMake 3.24+ for the package) |
| **Minimum toolchain** | C++20, GCC or Clang (CI: g++-13 to g++-16, clang++-18 to 20); reflection path needs GCC 16 with -freflection |
| **Platforms** | x86-64 for vector code (AVX2 via -march=x86-64-v3, AVX-512 via x86-64-v4); scalar backend on aarch64 and macOS; asm layer Linux/ELF x86-64 only |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: bench_asm times each 100-1500 ns call individually with steady_clock, and the timed lambda dispatches by strcmp on the row name first (one strcmp for scalar, three for intrinsics and asm), so timer and dispatch overhead sit inside every row. At n = 1024 the 4-accumulator FMA kernel's floor is about 128 core cycles (about 41 ns at 3.1 GHz; estimate from 2 loads per cycle and 8 floats per load), so roughly half of the 107 ns is fixed cost. That makes 'asm ties intrinsics exactly' weak evidence and compresses the speedups at L1 sizes.
- The cycles/element column is rdtsc ticks over the whole 21-run batch, timer calls included, divided by runs x elements; it is a batch average in TSC ticks (not core cycles on a powersave-governed CPU) and does not correspond to the min-of-21 ns column it sits beside.
- The 13.93x headline measures the intrinsics/asm twins in kernels/asm_kernels.hpp against a single-accumulator loop, not the vec&lt;T,N&gt; engine; bench_simd.cpp measures the engine against an auto-vectorised scalar loop, but no numbers from it are published. The -ffast-math 6.9x row has no benchmark code.
- The asm layer is enabled by default on any x86 host but uses ELF directives (.type @function, .note.GNU-stack) and the System V calling convention, and CI's macos-13 x86 job passes -DVECTIS_ENABLE_ASM=OFF; expect assembler or ABI failures on macOS x86-64 or MinGW unless you turn it off (inference from the source).

## Known shortcomings

- No compiler or version named for the bench numbers; the -ffast-math 6.9x row is README text with no harness; the 13.93x is hand-written intrinsics/assembly twins against a single-accumulator scalar loop, not the vec&lt;T,N&gt; engine; 0 stars, created 2026-09-20.
- Harness flaw: bench_asm times each 100-1500 ns call with steady_clock and a strcmp row dispatch (1-3 calls) sits inside the timed region; the estimated floor at n = 1024 is about 41 ns against 107 ns measured, so 'asm ties intrinsics' is weak evidence, and the cycles/element column is a TSC batch average not tied to the min. The asm layer is ELF/System V only but on by default for any x86 host. Commit 76b4ecc fixed AVX2 masks that were wrong for the 254 and 256 patterns.

## Caveats and trade-offs

Brand-new single-author repository (first commit 2026-09-20, 0 stars). The 13.93x figure is for hand-written intrinsics and GAS assembly twins in include/vectis/kernels/asm_kernels.hpp and src/asm/avx2_kernels.S, not for the library's vec&lt;T,N&gt; engine (bench_simd.cpp measures that, but the README publishes no numbers from it). The baseline is a deliberately serial single-accumulator loop that GCC may not reassociate without -ffast-math; the README itself says most of the gain is summation order (scalar-4acc already 2.05x, -ffast-math 6.9x, leaving under 2.3x for width and FMA). The benchmark compiler is not stated; the -ffast-math row has no benchmark code. Each 100-1500 ns call is timed individually with steady_clock, so timer overhead is part of every row; cycles/element is a batch average over all 21 runs, not the min. Measured on a powersave-governed i5-6500T; the author calls the timings noisy. Only AVX2 is measured; AVX-512 is compiled but never benchmarked, and the latest commit fixed false AVX-512 claims. SoA layouts lose to AoS at L3 and DRAM sizes, and AoS-to-SoA conversion costs 2-4x a kernel pass at large sizes.

Header-only C++20/23 vec&lt;T,N&gt; over scalar, AVX2 and AVX-512 backends; no SSE4 tier, no NEON; consumer must pass -march (otherwise the scalar backend is selected). Optional GAS assembly layer (dot, saxpy, sum) that the README itself recommends not adding by default. AoS to SoA with C++26 reflection needs GCC 16 -freflection.

## Maintenance

Single-author Apache-2.0 repository created 2026-09-20 with 7 commits, 0 stars and no release, last touched 2026-09-21; its CI and sanitizer setup is unusually thorough for its age, but it should be treated as an experiment until it shows sustained maintenance.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** First-party README table produced by public code (bench/bench_asm.cpp with bench/bench_harness.hpp, kernels in include/vectis/kernels/asm_kernels.hpp) on a named CPU (Intel i5-6500T) and the avx2 tier flags, but neither the README nor the repo names the compiler or version used for the benchmark numbers (GCC 15/16 appear only for tests and reflection; CI covers g++-13..16 and clang++-18/19), so it falls short of A; the -ffast-math 6.9x row has no benchmark code at all.
- **Verifier notes:** Numbers on the README match the record; downgrade A to C because the benchmark compiler/version is never stated (only inferred from the test matrix) and the -ffast-math 6.9x row is README text with no harness. The headline speedup is for hand-written intrinsics/asm kernels against a single-accumulator scalar loop, and the README itself attributes most of it to reassociation, not the Vectis vector engine.
- **Fields the verifier corrected:** `compiler_and_flags`, `claimed_speedup`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-76 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/wilkolbrzym-coder/Vectis>
  - <https://github.com/wilkolbrzym-coder/Vectis/commits>
  - <https://raw.githubusercontent.com/wilkolbrzym-coder/Vectis/HEAD/README.md>
  - <https://raw.githubusercontent.com/wilkolbrzym-coder/Vectis/HEAD/bench/bench_asm.cpp>
  - <https://raw.githubusercontent.com/wilkolbrzym-coder/Vectis/HEAD/bench/bench_harness.hpp>
  - <https://raw.githubusercontent.com/wilkolbrzym-coder/Vectis/HEAD/bench/bench_simd.cpp>
  - <https://raw.githubusercontent.com/wilkolbrzym-coder/Vectis/HEAD/bench/CMakeLists.txt>
  - <https://raw.githubusercontent.com/wilkolbrzym-coder/Vectis/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/wilkolbrzym-coder/Vectis/HEAD/include/vectis/kernels/asm_kernels.hpp>
  - <https://raw.githubusercontent.com/wilkolbrzym-coder/Vectis/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/wilkolbrzym-coder/Vectis/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/wilkolbrzym-coder/Vectis>
  - <https://github.com/wilkolbrzym-coder/Vectis/commits>
  - <https://github.com/wilkolbrzym-coder/Vectis/commit/76b4ecc>
  - <https://raw.githubusercontent.com/wilkolbrzym-coder/Vectis/HEAD/README.md>
  - <https://raw.githubusercontent.com/wilkolbrzym-coder/Vectis/HEAD/bench/bench_asm.cpp>
  - <https://raw.githubusercontent.com/wilkolbrzym-coder/Vectis/HEAD/bench/bench_harness.hpp>
  - <https://raw.githubusercontent.com/wilkolbrzym-coder/Vectis/HEAD/bench/bench_simd.cpp>
  - <https://raw.githubusercontent.com/wilkolbrzym-coder/Vectis/HEAD/bench/bench_soa.cpp>
  - <https://raw.githubusercontent.com/wilkolbrzym-coder/Vectis/HEAD/bench/CMakeLists.txt>
  - <https://raw.githubusercontent.com/wilkolbrzym-coder/Vectis/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/wilkolbrzym-coder/Vectis/HEAD/include/vectis/kernels/asm_kernels.hpp>
  - <https://raw.githubusercontent.com/wilkolbrzym-coder/Vectis/HEAD/src/asm/avx2_kernels.S>
  - <https://raw.githubusercontent.com/wilkolbrzym-coder/Vectis/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/wilkolbrzym-coder/Vectis/HEAD/LICENSE>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/wilkolbrzym-coder/vectis`) · [data/wave13/enrich/raw/github_com_wilkolbrzym_coder_vectis.json](../../../data/wave13/enrich/raw/github_com_wilkolbrzym_coder_vectis.json) (enrichment confidence 0.7)

</details>
