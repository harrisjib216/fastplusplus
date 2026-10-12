# Random123

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Random numbers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-3-Clause` · 🔴 abandoned

> Header-only counter-based CPU/GPU RNG family (Philox, Threefry, ARS); only AES-NI variants clearly beat std::mt19937_64.

| | |
|---|---|
| **Beats** | std::mt19937_64 |
| **Claimed result** | ARS-7 (AES-NI hardware-accelerated): 11.1 GB/s vs std::mt19937_64: 6.1 GB/s (\~1.8x, derived from page data) on the Intel CPU tested; Threefry-4x64-20 (no special hardware needed): 6.4 GB/s vs 6.1 GB/s (\~1.05x, derived from page data, i.e. only marginally faster without AES-NI) |
| **Workload** | Single-chip raw random byte-stream generation throughput (GB/s) and cycles-per-byte, counter-based generators (Philox, Threefry, ARS) vs conventional PRNGs including the C++0x std::mt19937_64. |
| **Metric** | throughput |
| **Hardware** | 3.07GHz quad-core Intel Xeon X5667 (Westmere) |
| **Compiler and flags** | gcc 4.5.3 (Intel CPU build); optimization flags not stated in the paper |
| **Adoption** | 127 stars |
| **Last commit** | 2022-01-17 |
| **Links** | [repository](https://github.com/DEShawResearch/random123) · [benchmark](https://www.thesalmons.org/john/random123/papers/random123sc11.pdf) |

## Verdict

In the peer-reviewed SC11 paper's Table 2 (confirmed directly from the PDF), on a 3.07GHz quad-core Xeon X5667 (Westmere) with gcc 4.5.3 and no stated optimization flags, std::mt19937_64 (the C++0x/libstdc++ engine) ran at 6.1 GB/s; the AES-NI-accelerated ARS-7 reached 11.1 GB/s (\~1.8x) and ARS-5 reached 17.8 GB/s (\~2.9x), while the portable, no-special-hardware Threefry-4x64-20 reached 6.4 GB/s, only a marginal \~1.05x.

## Use it when

- Monte Carlo / stochastic simulation workloads needing millions of independent, reproducible streams addressed by (counter,key) instead of stored per-thread generator state
- CUDA/OpenCL/Metal GPU kernels or heavily multithreaded CPU code, where per-thread state size and synchronization matter more than single-core throughput
- x86 CPUs with AES-NI, where ARS-7/ARS-5 give a real \~1.8x-2.9x throughput win over std::mt19937_64 (11.1-17.8 GB/s vs 6.1 GB/s)
- Checkpoint/restart or exact cross-run/cross-platform reproducibility, since output depends only on (counter,key), not call history

## Skip it when

- CPU-only code without AES-NI and no tolerance for a marginal win: the portable Threefry-4x64-20 is only about 1.05x std::mt19937_64 (6.4 vs 6.1 GB/s), and several Philox variants are slower than mt19937_64 on CPU
- Code needing a true drop-in std::mt19937/std::mt19937_64 replacement without writing adapter code; the native call shape rng(counter,key) differs from a stateful engine's operator()
- Cryptography or security-sensitive randomness: the README explicitly states these CBRNGs, despite being built from cipher-like primitives, are not suitable for crypto
- Projects wanting active upstream support: last commit on main was 2022-01-17, and open issues (NVCC optimization flags, RISC-V/LoongArch/HIP ports) have sat unanswered since 2022-2023

## How it is fast

Because each call is a pure function of (counter, key) with no state to read-modify-write, the generators vectorize and parallelize trivially and avoid the roughly 2.5KB of per-thread state std::mt19937 needs. ARS and AESNI reuse the hardware AES-NI round function directly, so on supporting CPUs ARS-7 needs only about 1.1 cycles/byte (ARS-5 about 0.7). Threefry (ARX rounds derived from the Skein/Threefish hash) and Philox (Feistel network plus one wide integer multiply per round) get most of their speed from a handful of cheap integer ops per output word rather than a large state-shuffle step.

## Compared with alternatives

Pick Random123 (ARS-7) over PCG/xoshiro/biski64/AESRand when the workload specifically needs stateless, independently-addressable (counter,key) streams for parallel/GPU Monte Carlo or exact reproducibility across runs; for plain single-threaded CPU throughput with a conventional stateful RNG API, PCG-cpp, wjakob/pcg32, xoshiro_cpp, or biski64 all show larger and more portable speedups over std::mt19937(_64) without requiring AES-NI hardware.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the core library; GNU Scientific Library only if using the optional gsl_cbrng/gsl_microrng adapters or the ut_gsl test |
| **Minimum toolchain** | a reasonable C99 (C API) or C++98 compiler per tests/README; C++11 needed for the SeedSeq-based seed() overloads in r123::Engine; AES-NI-capable CPU plus compiler intrinsics needed for the ARS/AESNI speedups |
| **Platforms** | x86 (AES-NI required for ARS/AESNI's advantage; a 64-bit-producing-128-bit multiply is needed for the Nx64 Philox variants); also ships CUDA, OpenCL, and Metal kernel code; ARM/RISC-V/LoongArch/HIP support is requested in open issues but not confirmed working |
| **Thread safety** | not documented as an explicit guarantee; the core CBRNG functors are stateless pure functions of (counter,key), so concurrent calls with distinct counters are safe by construction, but the stateful r123::Engine&lt;&gt; wrapper's thread safety is not documented |
| **Drop-in for the baseline** | partial — explain: the native CBRNG call rng(counter,key) is not drop-in for std::mt19937_64; the bundled r123::Engine&lt;CBRNG&gt; template wraps any generator to satisfy the C++11 UniformRandomNumberEngine interface so it can back &lt;random&gt; distributions, but the application must still pick and construct the generator explicitly. |

## Gotchas

- Engine&lt;CBRNG&gt;'s copy constructor calls fix_invariant() to recompute a cached output block when a sentinel (v.back()!=0) is set — an internal correctness detail worth knowing before subclassing or serializing it
- AESNI/ARS key_type is opaque and must be built from a separate ukey_type via key construction, unlike Threefry/Philox keys which can be used directly
- Philox's Nx64 forms only compile/run on hardware and compilers that support 64-bit multiplication producing a 128-bit result; Nx32 forms are the portable fallback
- README notes Random123 has been reported to use 16 bytes of static memory per CUDA thread, unintentionally, with no workaround given

## Caveats and trade-offs

Peer-reviewed paper (Salmon, Moraes, Dror & Shaw, 'Parallel Random Numbers: As Easy as 1,2,3', SC11) with a benchmark table (Table 2) that states CPU model and compiler but not flags. The hardware dates from 2011 (Westmere Xeon X5667). On the CPU, only the AES-NI generators (ARS-5 17.8 GB/s, ARS-7 11.1 GB/s) and Threefry-4x64-12 (11.2 GB/s) clearly beat std::mt19937_64 (6.1 GB/s). The recommended portable Threefry-4x64-20 is roughly a tie (6.4 GB/s), and the Philox variants are slower on the CPU (for example Philox4x32-10 at 3.4 GB/s and Philox4x64-10 at 3.9 GB/s). The large wins in the paper are on GPUs, where there is no C++ std baseline. GitHub's license detector reports NOASSERTION, but the LICENSE file is standard BSD-3-Clause text.

Counter-based API (application manages key + counter explicitly) is a different programming model than a stateful std::mt19937 engine, so it is not a drop-in engine substitute without an adapter; the standout CPU speedup (ARS-7) needs AES-NI hardware support -- without it, gains over std::mt19937_64 on CPU are small; largest wins shown in the paper are on GPU, not directly relevant to a CPU std::mt19937 comparison.

## Maintenance

Abandoned: the last commit on main was 2022-01-17 (the repo's 2024-02-15 pushed_at is only a push/metadata timestamp, not a new commit) and several issues opened in 2022-2023 (NVCC optimization flags, new-architecture ports) remain unaddressed; still BSD-3-Clause licensed and header-only, so it is trivial to vendor and freeze regardless of upstream activity.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now B.
- **Tier reason:** In the peer-reviewed SC11 paper, Table 2 lists ARS-7(hw) at 11.1 GB/s, Threefry-4x64-20 at 6.4 GB/s and std::mt19937_64 at 6.1 GB/s. The footnote states a Xeon X5667 and gcc 4.5.3. It is not A: the paper states no optimization flags, and the repo's timing code (tests/time_serial.c, tests/timers.cpp) does not include the std::mt19937_64 measurement.
- **Verifier notes:** The numbers are accurate, but the evidence is not reproducible to tier A: the flags are missing and the MT timing harness is not public. The last commit on main is 2022-01-17; the record's 2024-02-15 is only the repo's pushed_at timestamp, so the status is abandoned. The paper does not name the standard library, although gcc 4.5.3 implies libstdc++, so I left baseline_stdlib empty.
- **Fields the verifier corrected:** `last_commit`, `maintenance_status`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://www.thesalmons.org/john/random123/papers/random123sc11.pdf>
  - <https://github.com/DEShawResearch/random123>
  - <https://github.com/DEShawResearch/random123/blob/main/LICENSE>
  - <https://github.com/DEShawResearch/random123/blob/main/tests/GNUmakefile>
  - <https://github.com/DEShawResearch/random123/blob/main/tests/time_serial.c>
  - <https://github.com/DEShawResearch/random123/blob/main/tests/timers.cpp>
- **Sources the enricher read:**
  - <https://github.com/DEShawResearch/random123>
  - <https://github.com/DEShawResearch/random123/blob/main/README.md>
  - <https://github.com/DEShawResearch/random123/blob/main/include/Random123/conventional/Engine.hpp>
  - <https://github.com/DEShawResearch/random123/blob/main/tests/README>
  - <https://github.com/DEShawResearch/random123/blob/main/LICENSE>
  - <https://github.com/DEShawResearch/random123/issues>
  - <https://www.thesalmons.org/john/random123/papers/random123sc11.pdf>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/deshawresearch/random123`) · [data/wave1/enrich/raw/github_com_deshawresearch_random123.json](../../../data/wave1/enrich/raw/github_com_deshawresearch_random123.json) (enrichment confidence 0.62)

</details>
