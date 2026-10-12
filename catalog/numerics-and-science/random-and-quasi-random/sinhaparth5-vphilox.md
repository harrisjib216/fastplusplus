# vphilox

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT OR Apache-2.0` · 🟢 active

> Header-only C++20 SIMD Philox4x32-10 engine; bulk fill runs 1.3-4.6x std::mt19937 throughput, seekable and reproducible.

| | |
|---|---|
| **Beats** | std::mt19937 (also compared with xoshiro256++ and PCG64) |
| **Claimed result** | docs/benchmarks/README.md cost per byte relative to std::mt19937 (lower is faster), vphilox generate_n: Pi 5 0.75x, Sapphire Rapids 0.38x, Skylake-SP 0.22x, Cascade Lake 4v 0.24x, Cascade Lake 32v 0.33x (README: '1.3x to 4.6x the throughput of std::mt19937'). For comparison xoshiro256++ is 0.17-0.30x and PCG64 0.32-0.83x; vphilox operator() is 0.51-1.15x. |
| **Workload** | Cycles per byte of bulk random-byte generation (generate_n) and per-call operator() for a counter-based Philox4x32-10 engine with scalar/AVX2/AVX-512/NEON backends versus std::mt19937, xoshiro256++, PCG64 and unspecialised Philox on five machines. |
| **Metric** | throughput |
| **Hardware** | Raspberry Pi 5 (Cortex-A76, NEON, performance governor); Intel Xeon Platinum 8481C @ 2.70GHz (Sapphire Rapids, cloud vCPU); Intel Xeon @ 2.00GHz (Skylake-SP, GCP vCPU); Intel Xeon @ 2.80GHz Cascade Lake (family 6 model 85 stepping 7) on a 4-vCPU slice and on a whole 2-socket host. |
| **Compiler and flags** | GCC 13.3.0 (Ubuntu 24.04) for every x86 matrix run and GCC 12.2.0 (Debian 12) for the Pi 5 NEON run (docs/benchmarks/raw/machines.csv); CMake 'bench' preset = CMAKE_BUILD_TYPE=Release (CMake default -O3 -DNDEBUG for GCC), with kernel TUs adding -mavx2 or -mavx512f -mavx512dq -mavx512vl (CMakeLists.txt); runs through scripts/benchmarks/run_matrix.sh, pinned to one CPU, 9 repetitions with random interleaving and a 1% CV bar. |
| **Adoption** | 0 stars; very new |
| **Last commit** | 2026-08-31 |
| **Links** | [repository](https://github.com/sinhaparth5/vphilox) · [benchmark](https://raw.githubusercontent.com/sinhaparth5/vphilox/HEAD/docs/benchmarks/README.md) |

## Verdict

With the project's Google Benchmark harness (GCC 13.3 on x86, GCC 12.2 on the Pi, CMake Release plus per-kernel ISA flags, pinned to one CPU), bulk generate_n (AVX-512 kernel on the x86 matrix runs, NEON on the Pi) cost 0.22-0.75x the cycles per byte of libstdc++ std::mt19937 on the same machine across a Raspberry Pi 5 (NEON), Sapphire Rapids, Skylake-SP and two Cascade Lake hosts, i.e. 1.3x to 4.6x the throughput; per-value operator() ranged from 0.51x to 1.15x. All numbers are first-party, and cycles/byte is only compared within one machine.

## Use it when

- Parallel Monte Carlo or simulation where each thread or task needs its own independent stream with no locks, and results must not change with thread count.
- Jobs that checkpoint and resume, possibly on another machine or standard library, where std::mt19937's library-specific stream format is a problem.
- Filling large buffers (a few hundred values per call or more) of u32 or float on x86-64 with AVX2/AVX-512 or on aarch64 with NEON.
- Replacing std::mt19937 behind std::shuffle or &lt;random&gt; distributions when you also want O(1) skip-ahead (discard) for stream partitioning.
- Cross-checking a CPU simulation against GPU code that uses Philox (the repo documents a seeding mapping to NVIDIA cuRAND).

## Skip it when

- Raw bits per byte with no need for seeking or reproducibility: xoshiro256++ is cheaper per byte on four of the five benchmarked CPUs (vphilox wins only on Skylake-SP).
- Hot loops that draw one value at a time on ARM: per-value operator() is 0.87x the speed of std::mt19937 on a Raspberry Pi 5, and the per-value path is 1.5-2.4x slower than generate_n everywhere.
- Projects that need a released, packaged dependency: no tag yet (API may still change), no vcpkg/Conan package (open issue #65), single author, 0 stars.
- Pre-C++20 toolchains, or GPU kernels (CPU only; no CUDA/HIP backend).
- Small bulk calls: an 8-word generate_n costs 1.4-1.9x the raw kernel per byte; the overhead fades only by about 256 words.

## How it is fast

Philox blocks are independent, so the kernels run many counters in parallel in a structure-of-arrays lane layout: 8 counters per iteration under AVX2, 16 under AVX-512 (native unsigned compare and mask registers for the counter carry) and 8 under NEON as two groups of four; each 32x32-&gt;64 multiply is done with _mm\*_mul_epu32 on even and odd lanes plus a repack. The kernel is picked once at first use by CPUID/XGETBV runtime dispatch, with [[gnu::target]] attributes so one binary runs on any x86-64. generate_n writes straight into the caller's buffer and skips the 64-word refill buffer that operator() drains, which the project measures as 1.5-2.4x faster than the per-value path.

## Compared with alternatives

Pick vphilox over OpenRAND or the benchmark-rngs PhiloxSIMD prototype when you need a CPU-only Philox with runtime-dispatched AVX2/AVX-512/NEON, bit-identical output across backends and a portable checkpoint format; pick OpenRAND if you need the same generator on GPUs, and simdrng or a SIMD xoshiro when raw throughput matters more than seekability.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none at runtime; CMake configure generates vphilox/version.hpp; GoogleTest and Google Benchmark are fetched only for tests/benchmarks |
| **Minimum toolchain** | C++20; CMake 3.24+ for the build/install; CI covers GCC and Clang on Linux, Apple Clang on macOS arm64, and MSVC on Windows |
| **Platforms** | x86-64 (AVX2 or AVX-512F+DQ selected at runtime, scalar fallback), aarch64 (NEON), any other target via the scalar kernel |
| **Thread safety** | An engine object is not thread-safe; give each thread its own engine (distinct key or disjoint counter range). Kernel dispatch is resolved once in a function-local static. |
| **Drop-in for the baseline** | partial — satisfies std::uniform_random_bit_generator with 32-bit output like std::mt19937 and accepts a seed sequence, but it produces a different stream, a seed sequence fills only the 2-word key, and full speed needs the generate_n bulk API rather than operator() |

## Gotchas

- vphilox.hpp includes vphilox/version.hpp, which CMake generates from version.hpp.in, so copying include/ alone without configuring or installing will not compile.
- counter() returns where the next refill starts, not the stream position; rebuilding an engine from key() and counter() silently skips up to 64 buffered outputs. Use state()/set_state() or the serialize.hpp stream operators.
- Size thread pools by physical cores: the kernel is execution-port-bound, and two workers on hyperthread siblings each lose about a third of their throughput.
- The VPHILOX_BACKEND environment variable (scalar/avx2/avx512/neon) is read once per process at first use; next_double() consumes two 32-bit words.

## Known shortcomings

- Loses to xoshiro256++ on 4 of 5 machines (wins are vs other counter-based engines); 0 stars.
- First-party only; untagged, 0 stars, one author. xoshiro256++ is cheaper per byte on 4 of 5 CPUs; operator() on a Raspberry Pi 5 is 0.87x mt19937. Copying include/ alone does not compile because vphilox.hpp needs the CMake-generated version.hpp.

## Caveats and trade-offs

Very new (first runs 2026-08), one author, not yet tagged, 0 stars. All numbers are first-party. Cycles per byte uses RDTSC reference cycles (perf_event on the Pi) and only compares within one machine. Per-value operator() on the Pi 5 is 0.87x the speed of std::mt19937; operator() through the refill buffer is 1.5-2.4x slower than generate_n. xoshiro256++ is cheaper per byte on four of the five machines (vphilox wins only on Skylake-SP, 0.4210 vs 0.4703 cycles/byte). Four archived harness-validation runs (unpinned governor, 2-vCPU VM) are excluded from the figures by the project. SIMD backends are checked bit-for-bit against the scalar Random123 reference vectors (tests/test_reference_vectors.cpp, tests/test_kernel_parity.cpp). The accompanying paper is a preprint (TechRxiv/Zenodo), not peer-reviewed. libstdc++ inferred from GCC on Ubuntu/Debian.

Counter-based (seekable in constant time, bit-identical across machines, thread-count independent output) with C++20 header-only SIMD backends chosen at runtime; the bulk generate_n path is needed for the speed (operator() goes through a refill buffer).

## Maintenance

Actively developed (last commit 2026-08-31), MIT OR Apache-2.0 and header-only so it is easy to vendor, but untagged with a CalVer 2026.08.1 version, 0 stars and one author; the bit stream is declared frozen even though the API may change.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** docs/benchmarks/README.md gives the per-machine cost ratios against std::mt19937 produced by benchmarks/bench_engines.cpp (Google Benchmark, DoNotOptimize/ClobberMemory on the buffer). docs/benchmarks/raw/machines.csv records the compiler (GCC 13.3.0 on x86, GCC 12.2.0 on the Pi 5), the exact command and the CPU (e.g. Xeon Platinum 8481C, Cortex-A76). The bench preset is CMake Release plus per-kernel ISA flags in CMakeLists.txt.
- **Verifier notes:** All ratios in the record match the table in docs/benchmarks/README.md; README's '1.3x to 4.6x' equals 1/0.75 and 1/0.22. RNG check passed: every SIMD backend must reproduce the scalar Philox4x32-10 stream. Metadata: MIT OR Apache-2.0, 0 stars, 0 forks, 151 commits, default branch master, last commit 2026-08-31.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/sinhaparth5/vphilox/HEAD/docs/benchmarks/README.md>
  - <https://raw.githubusercontent.com/sinhaparth5/vphilox/HEAD/README.md>
  - <https://raw.githubusercontent.com/sinhaparth5/vphilox/HEAD/docs/benchmarks/raw/machines.csv>
  - <https://raw.githubusercontent.com/sinhaparth5/vphilox/HEAD/CMakePresets.json>
  - <https://raw.githubusercontent.com/sinhaparth5/vphilox/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/sinhaparth5/vphilox/HEAD/benchmarks/bench_engines.cpp>
  - <https://github.com/sinhaparth5/vphilox>
  - <https://github.com/sinhaparth5/vphilox/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/sinhaparth5/vphilox/HEAD/README.md>
  - <https://raw.githubusercontent.com/sinhaparth5/vphilox/HEAD/docs/benchmarks/README.md>
  - <https://raw.githubusercontent.com/sinhaparth5/vphilox/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/sinhaparth5/vphilox/HEAD/CMakePresets.json>
  - <https://raw.githubusercontent.com/sinhaparth5/vphilox/HEAD/include/vphilox/vphilox.hpp>
  - <https://raw.githubusercontent.com/sinhaparth5/vphilox/HEAD/include/vphilox/philox.hpp>
  - <https://raw.githubusercontent.com/sinhaparth5/vphilox/HEAD/include/vphilox/config.hpp>
  - <https://raw.githubusercontent.com/sinhaparth5/vphilox/HEAD/include/vphilox/serialize.hpp>
  - <https://raw.githubusercontent.com/sinhaparth5/vphilox/HEAD/include/vphilox/detail/dispatch.hpp>
  - <https://raw.githubusercontent.com/sinhaparth5/vphilox/HEAD/include/vphilox/detail/kernel_avx512.hpp>
  - <https://raw.githubusercontent.com/sinhaparth5/vphilox/HEAD/include/vphilox/detail/kernel_avx2.hpp>
  - <https://raw.githubusercontent.com/sinhaparth5/vphilox/HEAD/include/vphilox/detail/cpu_features.hpp>
  - <https://raw.githubusercontent.com/sinhaparth5/vphilox/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/sinhaparth5/vphilox/HEAD/VERSIONING.md>
  - <https://raw.githubusercontent.com/sinhaparth5/vphilox/HEAD/docs/benchmarks/raw/machines.csv>
  - <https://github.com/sinhaparth5/vphilox/tree/master/include/vphilox>
  - <https://github.com/sinhaparth5/vphilox/tree/master/include/vphilox/detail>
  - <https://github.com/sinhaparth5/vphilox/issues>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/sinhaparth5/vphilox`) · [data/wave8/enrich/raw/github_com_sinhaparth5_vphilox.json](../../../data/wave8/enrich/raw/github_com_sinhaparth5_vphilox.json) (enrichment confidence 0.85)

</details>
