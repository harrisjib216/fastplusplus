# OpenRAND (Philox, Threefry, Squares, Tyche counter-based generators)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟡 stale

> Header-only C++17 counter-based RNGs (Philox, Threefry, Squares, Tyche) for CPU and CUDA/HIP; beats stateful cuRAND in a Brownian dynamics run and std::mt19937 on short streams.

| | |
|---|---|
| **Beats** | std::mt19937 (libstdc++) on CPU and NVIDIA cuRAND on GPU |
| **Claimed result** | Paper Fig. 4b, Brownian dynamics wall time (1M particles, 10,000 steps, Philox in every library): A100 SXM cuRAND 3.20 s vs OpenRAND 1.78 s (1.80x, derived from page data), Random123 1.81 s; Tesla V100 PCIe cuRAND 4.23 s vs OpenRAND 2.48 s (1.71x, derived from page data), Random123 2.46 s. Text: 'OpenRAND outperformed cuRAND by 1.8x, while saving \~64 MB of GPU memory per million particles, and performed on par with Random123.' CPU (Fig. 4a, log-scale chart without printed values, read by eye) against libstdc++ std::mt19937 on a Xeon Platinum 8260: all four generators are far faster for 10-100 draws per freshly constructed engine. At 10K draws, Tyche (\~1.6e4 ns) and Squares (\~1.4e4 ns) are roughly 3.5-4x faster than mt19937 (\~5.5e4 ns), while Philox (\~6.6e4 ns) is slightly slower and Threefry (\~3.3e5 ns) is about 6x slower. |
| **Workload** | CPU: Google Benchmark (benchmarks/raw_speed_cpu.cpp) constructing a fresh engine each iteration and drawing 10 to 100,000 uint32 values, against std::mt19937. GPU: 2D Brownian dynamics, 1M particles x 10,000 steps, timed with `time` on each whole executable (brownian-dynamics/runfile.sh) for cuRAND (curandStatePhilox4_32_10_t kept in global memory), Random123 Philox4x32 and OpenRAND Philox. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Platinum 8260 (CPU micro-benchmark); NVIDIA Tesla V100 PCIe and A100 SXM (Brownian dynamics benchmark). |
| **Compiler and flags** | GPU benchmark: nvcc -Xcompiler -Wall -O3 -std=c++17 -arch=sm_80 (brownian-dynamics Makefile; CUDA version not stated; the README says to change -arch for other GPUs, so the V100 build used a different arch flag). CPU micro-benchmark: compiler and flags not stated (Google Benchmark via CMake; the repo CMakeLists sets no CMAKE_BUILD_TYPE). |
| **Adoption** | 37 stars, 6 forks; SoftwareX 27 (2024) 101773 (doi 10.1016/j.softx.2024.101773) |
| **Last commit** | 2024-12-11 |
| **Links** | [repository](https://github.com/msu-sparta/OpenRAND) · [benchmark](https://github.com/msu-sparta/OpenRAND/blob/main/docs/OpenRAND.pdf) |

## Verdict

The authors' SoftwareX paper timed a 2D Brownian dynamics simulation (1M particles, 10,000 steps, Philox in every library, whole-process wall time, nvcc -O3 -std=c++17 -arch=sm_80) at 1.78 s with OpenRAND versus 3.20 s with cuRAND and 1.81 s with Random123 on an A100 SXM, and 2.48 s versus 4.23 s and 2.46 s on a Tesla V100 PCIe. Their CPU micro-benchmark on a Xeon Platinum 8260 against libstdc++ std::mt19937 (constructing a fresh engine per iteration; compiler and flags unstated) is only a log-scale chart: all four generators win on 10-100 draws, while at 10K draws only Tyche and Squares stay ahead.

## Use it when

- CUDA or HIP kernels where each thread or particle needs a few random numbers per launch and you want to stop storing curandState arrays; the paper measured 1.8x over cuRAND Philox on an A100 and 1.7x on a V100 in a RNG-bound Brownian dynamics kernel.
- Simulations that must be bitwise reproducible regardless of thread count or scheduling (seed = particle id, counter = timestep).
- CPU code that constructs many short-lived generators (10 to 1,000 draws each), where std::mt19937's seeding cost dominates.
- Code that must compile unchanged for host, CUDA and HIP from one header set with no intrinsics or platform-specific code.

## Skip it when

- Long single streams on the CPU: at 10K draws only Tyche and Squares beat std::mt19937 (roughly 3.5-4x); Philox is slightly slower and Threefry about 6x slower, and SIMD or small-state generators (xoshiro, PCG, Romu) are faster still.
- Already on Random123: the paper shows OpenRAND Philox on par with Random123 (1.78 s versus 1.81 s on A100), so the gain is API simplicity, not speed.
- More than 2^32 draws from one (seed, counter) pair: the paper states each stream has period 2^32 and the internal counter is a uint32_t.
- You need the published Squares64 output: open issue #25 reports the 64-bit Squares path differs from Widynski's paper.
- Cryptographic use: these are reduced-round statistical generators, not CSPRNGs.

## How it is fast

Counter-based generation: each output is a keyed bijection of (seed, counter) computed in registers (Philox-4x32-10 multiply/xor rounds, Threefry-2x32-20 add-rotate-xor, Widynski's Squares middle-square rounds, or the Tyche ARX mix), so construction is a few register moves instead of mt19937's 624-word seeding or a cuRAND state load/store. On the GPU the win in the paper comes from skipping curand_init and the per-thread state round trip to global memory (about 64 MB saved per million particles), not from a faster Philox; on the CPU it comes from cheap construction for short streams.

## Compared with alternatives

Pick OpenRAND for portable GPU and CPU code that wants stateless per-work-unit streams with a two-line API; vphilox and benchmark-rngs PhiloxSIMD are faster for bulk Philox output on CPUs with AVX, and the standalone Squares generator or Random123 give the same algorithms with lower-level APIs. For CPU throughput or attack resistance, Randen, Randompack or a SIMD xoshiro fit better.

## Integration

| | |
|---|---|
| **Form** | header-only (include/openrand/\*.h; CMake INTERFACE target OpenRAND::OpenRAND, FetchContent or make install) |
| **Dependencies** | none (Google Test, Google Benchmark, TestU01 and PractRand only for optional tests/benchmarks) |
| **Minimum toolchain** | C++17 (if constexpr, std::void_t); CMake 3.18 if using the CMake target; nvcc for CUDA, hipcc for HIP |
| **Platforms** | any C++17 host; NVIDIA GPUs via CUDA (__host__ __device__ through the OPENRAND_DEVICE macro) and AMD GPUs via HIP; no architecture-specific intrinsics |
| **Thread safety** | Generators are small value types with no shared or global state; the intended pattern is one generator per thread/work unit, so no synchronization is needed. Sharing one instance across threads is unsynchronized (not documented). |
| **Drop-in for the baseline** | partial: satisfies the UniformRandomBitGenerator interface (32-bit result_type) so it can replace std::mt19937 inside std:: distributions, but the constructor takes (seed, counter) and the stream model differs; against cuRAND it replaces curand_init/curand_uniform with a different API |

## Gotchas

- Philox::draw&lt;uint32_t&gt;() (used by operator() and rand&lt;float&gt;()) computes a full 4x32 Philox block and returns only one word, discarding three; use draw_int4()/draw_float4() to get all four, which is why scalar Philox loses to mt19937 on long CPU streams.
- rand&lt;float&gt;() and rand&lt;double&gt;() are documented as [0,1) but the u01 conversion (x \* 2^-32 + 2^-33 in float) rounds to exactly 1.0f for the top 128 uint32 inputs (about 1 in 33.5 million draws), and to 1.0 for the top 1,024 uint64 inputs in double (derived from the base_state.h code, not documented upstream); clamp before using the value as an index.
- range&lt;T&gt;(N) defaults to the biased multiply-shift (biased=true); pass range&lt;false&gt;(N) for unbiased Lemire rejection. randn() discards the second Box-Muller value; use randn2().
- squares.h does #define K 0xc58efd154ce32f6d at global scope, which breaks any including code that uses K as an identifier; Philox, Threefry and Squares have const members, so they are copy-constructible but not copy-assignable.

## Known shortcomings

- Gain comes from the stateless API, not the algorithm (Random123 is on par); on CPU at 10K draws only Tyche/Squares beat mt19937, while Philox and Threefry are slower.
- rand&lt;float&gt;() returns exactly 1.0f for the top 128 uint32 inputs (\~1 in 33.5M draws) against the documented [0,1); double returns 1.0 for the top 1024 uint64 inputs (derived from base_state.h u01 code, not filed upstream). Open #25: 64-bit Squares output differs from Widynski's paper. Philox draw&lt;uint32_t&gt; computes a 4x32 block and returns one word, which explains the CPU loss to mt19937. squares.h leaks #define K globally. Stream period per (seed, counter) is 2^32.

## Caveats and trade-offs

The GPU win over cuRAND comes from the counter-based API, which avoids loading and storing per-thread cuRAND state in global memory. It is not a faster algorithm: every library uses Philox, Random123 is on par, and the authors say they do not expect the margin to hold in real kernels where RNG cost is smaller. Timing is whole-process wall time (including CUDA context setup and cuRAND state initialization). The benchmark repo vendors an early copy of the library (namespace rnd) rather than the current openrand headers, and its Makefile targets sm_80 (A100); the V100 build flags are not published. CPU micro-benchmark: compiler and flags unstated, and the repo CMake sets no build type. The engine is constructed inside the timed loop, so mt19937's 624-word seeding dominates small streams (the paper says so). At 10K draws only Tyche and Squares beat mt19937; Philox and Threefry are slower. CPU values exist only as a log-scale chart. The paper is first-party.

Header-only C++17, works on CPU and GPU (CUDA) device code; counter-based design needs a (seed, counter) pair per work unit and gives reproducibility independent of thread count; the std-compatible engine interface lets it drive standard distributions.

## Maintenance

Stale since 2024-12-11 (37 stars, CMake project version 1.0, release issue #9 still open) but MIT-licensed and small (the paper counts 470 source lines of core headers at publication), so it is easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C. The paper (SoftwareX 27 (2024) 101773; preprint in the repo as docs/OpenRAND.pdf) gives Brownian-dynamics wall times against cuRAND on named GPUs (A100 SXM, Tesla V100 PCIe). The benchmark code is public in the paper's linked repo Shihab-Shahriar/brownian-dynamics (Curand.cu, Openrand.cu, r123.cu, runfile.sh), and its Makefile gives the compiler and flags (nvcc -Xcompiler -Wall -O3 -std=c++17 -arch=sm_80). That meets A for the cuRAND result; the nvcc version is not stated, the same gap the midint precedent accepted. The CPU comparison against std::mt19937 alone would only be B (chart only, compiler and flags unstated).
- **Verifier notes:** The SoftwareX page (sciencedirect), arXiv, SSRN and the project docs site are egress-blocked, but the repo carries the preprint (docs/OpenRAND.pdf); Fig. 4b values were read from the rendered PDF, matching legend order Curand/Random123/OpenRAND. Metadata: MIT, 37 stars, last commit 2024-12-11 (stale).
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/msu-sparta/OpenRAND>
  - <https://github.com/msu-sparta/OpenRAND/commits/main>
  - <https://github.com/msu-sparta/OpenRAND/tree/main/benchmarks>
  - <https://github.com/msu-sparta/OpenRAND/tree/main/examples>
  - <https://github.com/msu-sparta/OpenRAND/tree/main/docs>
  - <https://github.com/msu-sparta/OpenRAND/blob/main/docs/OpenRAND.pdf>
  - <https://raw.githubusercontent.com/msu-sparta/OpenRAND/HEAD/README.md>
  - <https://raw.githubusercontent.com/msu-sparta/OpenRAND/HEAD/docs/OpenRAND.pdf>
  - <https://raw.githubusercontent.com/msu-sparta/OpenRAND/HEAD/benchmarks/raw_speed_cpu.cpp>
  - <https://raw.githubusercontent.com/msu-sparta/OpenRAND/HEAD/benchmarks/raw_speed_cuda.cu>
  - <https://raw.githubusercontent.com/msu-sparta/OpenRAND/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/msu-sparta/OpenRAND/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/msu-sparta/OpenRAND/HEAD/LICENSE>
  - <https://github.com/Shihab-Shahriar/brownian-dynamics>
  - <https://raw.githubusercontent.com/Shihab-Shahriar/brownian-dynamics/HEAD/README.md>
  - <https://raw.githubusercontent.com/Shihab-Shahriar/brownian-dynamics/HEAD/Makefile>
  - <https://raw.githubusercontent.com/Shihab-Shahriar/brownian-dynamics/HEAD/runfile.sh>
  - <https://raw.githubusercontent.com/Shihab-Shahriar/brownian-dynamics/HEAD/Curand.cu>
  - <https://raw.githubusercontent.com/Shihab-Shahriar/brownian-dynamics/HEAD/Openrand.cu>
  - <https://raw.githubusercontent.com/Shihab-Shahriar/brownian-dynamics/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/msu-sparta/OpenRAND>
  - <https://raw.githubusercontent.com/msu-sparta/OpenRAND/HEAD/README.md>
  - <https://raw.githubusercontent.com/msu-sparta/OpenRAND/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/msu-sparta/OpenRAND/HEAD/include/openrand/base_state.h>
  - <https://raw.githubusercontent.com/msu-sparta/OpenRAND/HEAD/include/openrand/philox.h>
  - <https://raw.githubusercontent.com/msu-sparta/OpenRAND/HEAD/include/openrand/tyche.h>
  - <https://raw.githubusercontent.com/msu-sparta/OpenRAND/HEAD/include/openrand/squares.h>
  - <https://raw.githubusercontent.com/msu-sparta/OpenRAND/HEAD/include/openrand/threefry.h>
  - <https://raw.githubusercontent.com/msu-sparta/OpenRAND/HEAD/include/openrand/util.h>
  - <https://raw.githubusercontent.com/msu-sparta/OpenRAND/HEAD/benchmarks/raw_speed_cpu.cpp>
  - <https://raw.githubusercontent.com/msu-sparta/OpenRAND/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/msu-sparta/OpenRAND/HEAD/docs/OpenRAND.pdf>
  - <https://raw.githubusercontent.com/msu-sparta/OpenRAND/HEAD/tests/test_uniform.cpp>
  - <https://raw.githubusercontent.com/msu-sparta/OpenRAND/HEAD/tests/README.txt>
  - <https://raw.githubusercontent.com/msu-sparta/OpenRAND/HEAD/examples/pi_cuda.cu>
  - <https://github.com/msu-sparta/OpenRAND/issues?q=is%3Aissue>
  - <https://github.com/msu-sparta/OpenRAND/issues/25>
  - <https://github.com/msu-sparta/OpenRAND/issues/15>
  - <https://github.com/msu-sparta/OpenRAND/tree/main/examples>
  - <https://github.com/msu-sparta/OpenRAND/tree/main/tests>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/msu-sparta/openrand`) · [data/wave8/enrich/raw/github_com_msu_sparta_openrand.json](../../../data/wave8/enrich/raw/github_com_msu_sparta_openrand.json) (enrichment confidence 0.8)

</details>
