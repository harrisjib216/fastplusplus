# libMetalFloat64 (philipturner/metal-float64; emulated FP64 on Apple GPUs)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier D** (directional, no numbers) · Study only · `Metal Shading Language (Swift package)` · `MIT` · 🔴 abandoned

> Archived plan for emulated FP64 on Apple GPUs in Metal; no arithmetic is implemented, only theoretical peaks versus CPU FP64.

| | |
|---|---|
| **Beats** | Native hardware FP64 on the Apple Silicon CPU (NEON) in the README table, and OpenCL FP64 in the precision table; the listed baselines GMP and MPFR are not compared |
| **Claimed result** | README 'Performance' table of maximum theoretical scalar Gops (not measured), CPU FP64 vs GPU FP32x2 (double-single, 1+47-bit mantissa): FFMA 392 vs 590, FADD 196 vs 482, FMUL 196 vs 758, FCMPSEL 196 vs 2123, FCMP 196 vs 1769, FRECIP 49 vs 196, FDIV 49 vs 183, FRSQRT 49 vs 171, FSQRT 49 vs 189 (ratios 1.5x to 10.8x, derived from page data). The 'GPU eFP64' column (float64_t with edge-case checking disabled) is empty. Text: 'Based on theoretical estimates, additions and multiplications will have 1/32-1/64 the throughput of their 32-bit counterparts.' |
| **Workload** | Theoretical maximum scalar giga-operations per second per operation (FFMA, FADD, FMUL, FCMPSEL, FCMP, FRECIP, FDIV, FRSQRT, FSQRT) for a reference system with an 8-core 3.064 GHz ARM CPU (four 128-bit vector ALUs per core) and a 32-core 1.296 GHz Apple GPU, computed from instruction counts and not measured. |
| **Metric** | throughput |
| **Hardware** | README reference system: 8-core 3.064 GHz ARM CPU and 32-core 1.296 GHz Apple GPU; the chip is not named. |
| **Adoption** | 65 stars, 3 forks; archived (read-only) on 2024-08-11 |
| **Last commit** | 2023-05-17 |
| **Links** | [repository](https://github.com/philipturner/metal-float64) · [benchmark](https://github.com/philipturner/metal-float64) |

## Verdict

Nothing was measured: the README table gives theoretical scalar Gops for an unnamed reference system (8-core 3.064 GHz ARM CPU and 32-core 1.296 GHz Apple GPU), derived from instruction counts, comparing CPU hardware FP64 with GPU double-single FP32x2 (e.g. FMUL 196 vs 758, FADD 196 vs 482). The IEEE eFP64 column is empty, most of the precision table is '???', and the code that would produce those numbers does not exist in the repository.

## Use it when

- As a design reference when planning your own FP64 or double-single emulation in Metal: the README lists per-operation instruction counts and the dylib-versus-inline split.
- As a starting point for lock-buffer 64-bit atomics on Apple GPUs (MetalAtomic64 hashes addresses into a lock buffer, borrowing the idea from Kokkos desul's Lock_Array), after finishing and testing it yourself.
- Not for production numerics in any form: there is no working FP64 add, multiply or FMA to call.

## Skip it when

- Any real workload: the README opens with 'Still in the planning stage - this is not a finished library!' and the sources confirm it.
- Arbitrary-precision or big-integer work: it is fixed 64-bit floating point, not a GMP or MPFR alternative, so it is in the wrong category for that comparison.
- Code that needs correct 64-bit atomics: __metal_atomic64_fetch_add_explicit ignores its type argument and always does integer addition (so f64 adds would be wrong), and the device-memory store has its lock acquire and release left as comments.
- Pre-Metal 3 hardware: it needs function pointers and Metal dynamic libraries, so Apple6-family GPUs (A13 and later) or macOS 13 Ventura on Intel Macs.
- Fast-math builds of double-single code: the author notes in openmm/openmm#3889 that the Metal compiler optimizes away double-single FP64 emulation.

## How it is fast

The intended speed comes from emulating FP64 with FP32 and 32-bit integer ALU instructions on the GPU's wide FP32 units: an IEEE path modeled on Berkeley SoftFloat and LLVM compiler-rt fp_lib.h, and a faster double-single (float-float, e8m48) path with flushed denormals. The README's speedups over the CPU's NEON FP64 are instruction-count estimates (for example 11 FP32/integer instructions per double-single add, 7 per multiply), multiplied by the GPU's ALU count and clock; none of that arithmetic is in the repository.

## Compared with alternatives

Do not pick it for computation: sibling entries such as MultiFloats.hpp, DoubleFloats.jl or libQD3 ship working double-double arithmetic with measurements, while this repository has none. It is only worth reading if you target Metal, which none of the siblings do, and plan to write the emulation yourself.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | Xcode Metal toolchain (xcrun metal), Swift 5.7 (SwiftPM) for build.swift and the MetalAtomic64 product |
| **Minimum toolchain** | Swift tools 5.7; macOS 13, iOS 16 or tvOS 16 (Package.swift); Metal 3 feature set |
| **Platforms** | Apple GPUs of the Apple6 family or newer (A13 Bionic and later, Apple silicon Macs); Intel Macs on macOS Ventura |
| **Thread safety** | not documented; the 64-bit atomics are the only concurrency code and are incomplete |
| **Drop-in for the baseline** | no |

## Gotchas

- The README warns that forgetting useResource(_:usage:) on the atomics lock buffer can freeze half of the GPU until a restart, or silently draw half its maximum TDP in the background.
- The library header copies parts of Apple's Metal Standard Library and says Apple owns the copyright of that code, so the MIT license does not cover all of it.
- README and code disagree: the README documents float64_t and float32x2_t, while the headers define float64_t, float59_t and float43_t, and the atomics enum adds f32x2 and f32.
- Clients must ship libMetalFloat64.metallib in the same directory as their own library, because it is linked with @loader_path.

## Known shortcomings

- Tier D: the README Performance table is theoretical peak derived from instruction counts, not a measurement, and the baseline is the CPU's hardware FP64 peak rather than GMP or MPFR. It is FP64 emulation on Apple GPUs, so it sits oddly in the arbitrary-precision category. Archived 2024-08-11, last commit 2023-05-17.
- HEAD has no FP64 arithmetic: float64_t/float59_t/float43_t are empty ulong wrappers with no operators, the only MetalFloat64 source is a placeholder increment(uint) marked 'TODO: Remove this entire file', and the README's float32x2_t does not exist. MetalAtomic64 fetch_add ignores the type id (an f64 add would be an integer add) and the device store has no lock. The header copies Apple Metal stdlib code under Apple copyright, so MIT does not cover all of it. openmm/openmm#3889: the Metal compiler optimizes away double-single emulation. Usability corrected to reference (retier-09).

## Caveats and trade-offs

The README says 'Still in the planning stage - this is not a finished library!'. The only numbers are theoretical peaks from instruction counts (the README's own 'maximum theoretical performance'); no workload was timed anywhere I could open, the eFP64 column (float64_t with edge-case checks disabled) is blank and the precision table is mostly '???'. The comparison is not like-for-like: the CPU column is full IEEE FP64, while the filled GPU column is FP32x2 double-single with an 8-bit exponent and 1+47-bit mantissa that flushes denormals and gives undefined results for INF/NAN. The comparison is against the CPU's hardware double, not the category baselines GMP or MPFR (software arbitrary precision), so the entry does not fit big-integer-arbitrary-precision; it would sit better with floating-point emulation or GPU numerics. The README credits GPT-4 for much of the work. Archived (read-only) on 2024-08-11; last commit 2023-05-17. [retier] HEAD contains no FP64 arithmetic: float64_t/float59_t/float43_t are empty ulong wrappers with no operators; the only MetalFloat64 source is a placeholder increment(uint) marked 'TODO: Remove this entire file'; the README's float32x2_t does not exist in the code. MetalAtomic64 fetch_add ignores the type id (an f64 add would be an integer add) and the device store has no lock. The header copies Apple Metal stdlib code under Apple copyright, so MIT does not cover all of it. The README Performance table is theoretical peak from instruction counts, not a measurement; archived 2024-08-11.

Swift package that builds a Metal dynamic library and headers; needs an Apple6-family or newer GPU (A13 and later, Metal 3) and macOS Ventura on Intel Macs. Two precisions: float64_t is IEEE-compliant but the README gives no throughput for it, while float32x2_t has 1+47 mantissa bits, flushes denormals and has undefined INF/NaN results. Larger functions are called through the dynamic library, so inlining is partial. The planned 64-bit atomics use a lock buffer and the README warns that a missing useResource call can freeze half the GPU. Matrix types, division, square root and transcendentals were still planned; the README states the library is 'not a finished library'.

## Maintenance

Archived and read-only since 2024-08-11 with the last commit on 2023-05-17; MIT-licensed but unusable as shipped, since it contains only type scaffolding, a placeholder function and partial 64-bit atomics.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification D, tier now D.
- **Tier reason:** The README's Performance table is explicitly 'maximum theoretical performance' computed from instruction counts for an unnamed reference system, not a measurement; the IEEE-path eFP64 column is empty and nothing in the repo or the linked openmm-benchmarks/FP64Emulation folder (Trial1.swift, Trial2.swift, Trial3.cl, bing-conversation.md) times a real workload. The 'baseline' is the CPU's hardware FP64 peak, not GMP or MPFR.
- **Verifier notes:** README numbers match the record exactly; they are theoretical, so D stands. Wrong category (FP64 emulation on Apple GPUs vs CPU FP64, not arbitrary precision vs GMP/MPFR); 65 stars and tier D would allow a not-notable-tier-d reject, but I confirmed it so the keep-and-document rule applies. Metadata verified: MIT, 65 stars, 3 forks, not a fork, archived 2024-08-11, last commit 2023-05-17 ('Correct for rounding error'), abandoned.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`, `usability`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/philipturner/metal-float64>
  - <https://github.com/philipturner/metal-float64/commits>
  - <https://raw.githubusercontent.com/philipturner/metal-float64/HEAD/README.md>
  - <https://github.com/philipturner/openmm-benchmarks/tree/main/FP64Emulation>
- **Sources the enricher read:**
  - <https://github.com/philipturner/metal-float64>
  - <https://github.com/philipturner/metal-float64/commits/main>
  - <https://raw.githubusercontent.com/philipturner/metal-float64/HEAD/README.md>
  - <https://raw.githubusercontent.com/philipturner/metal-float64/HEAD/Package.swift>
  - <https://raw.githubusercontent.com/philipturner/metal-float64/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/philipturner/metal-float64/HEAD/build.sh>
  - <https://raw.githubusercontent.com/philipturner/metal-float64/HEAD/build.swift>
  - <https://github.com/philipturner/metal-float64/tree/main/Sources>
  - <https://github.com/philipturner/metal-float64/tree/main/Sources/MetalFloat64>
  - <https://github.com/philipturner/metal-float64/tree/main/Sources/MetalFloat64/src>
  - <https://github.com/philipturner/metal-float64/tree/main/Sources/MetalFloat64/include/MetalFloat64>
  - <https://github.com/philipturner/metal-float64/tree/main/Sources/MetalAtomic64/src>
  - <https://github.com/philipturner/metal-float64/tree/main/Tests/MetalFloat64Tests>
  - <https://raw.githubusercontent.com/philipturner/metal-float64/HEAD/Sources/MetalFloat64/include/MetalFloat64/MetalFloat64.h>
  - <https://raw.githubusercontent.com/philipturner/metal-float64/HEAD/Sources/MetalFloat64/include/MetalFloat64/Double.h>
  - <https://raw.githubusercontent.com/philipturner/metal-float64/HEAD/Sources/MetalFloat64/include/MetalFloat64/Defines.h>
  - <https://raw.githubusercontent.com/philipturner/metal-float64/HEAD/Sources/MetalFloat64/include/MetalFloat64/Vector.h>
  - <https://raw.githubusercontent.com/philipturner/metal-float64/HEAD/Sources/MetalFloat64/include/MetalFloat64/Atomic.h>
  - <https://raw.githubusercontent.com/philipturner/metal-float64/HEAD/Sources/MetalFloat64/src/Atomic.metal>
  - <https://raw.githubusercontent.com/philipturner/metal-float64/HEAD/Sources/MetalAtomic64/src/Atomic.metal>
  - <https://raw.githubusercontent.com/philipturner/metal-float64/HEAD/Tests/MetalFloat64Tests/MetalFloat64Tests.swift>
  - <https://raw.githubusercontent.com/philipturner/metal-float64/HEAD/Tests/MetalFloat64Tests/AtomicTests.swift>
  - <https://github.com/philipturner/openmm-benchmarks/tree/main/FP64Emulation>
  - <https://github.com/openmm/openmm/issues/3889>
  - <https://github.com/philipturner/amx-benchmarks>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/philipturner/metal-float64`) · [data/wave8/enrich/raw/github_com_philipturner_metal_float64.json](../../../data/wave8/enrich/raw/github_com_philipturner_metal_float64.json) (enrichment confidence 0.85)

</details>
