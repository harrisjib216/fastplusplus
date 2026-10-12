# Vector Class Library (VCL) version 2

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Agner Fog's header-only C++17 SIMD vector classes for x86, with inline vector math meant to replace scalar libm loops.

| | |
|---|---|
| **Beats** | standard scalar math function libraries (libm) and scalar code that the compiler fails to auto-vectorize |
| **Claimed result** | No numbers. Manual: 'Both versions are many times faster than standard (scalar) math function libraries' (inline and external SVML-based vector math versions). |
| **Workload** | No benchmark workload is published. The manual states qualitatively that vector math functions (log, exp, pow, trig, hyperbolic) process whole SIMD vectors and so beat scalar math libraries, and that VCL gives the same optimization level as hand-written intrinsics. |
| **Metric** | throughput |
| **Adoption** | 1.5k stars; used as a dependency by other libraries (for example andyD123/DR3 vendors a VCL2 copy) |
| **Last commit** | 2026-09-09 |
| **Links** | [repository](https://github.com/vectorclass/version2) · [benchmark](https://raw.githubusercontent.com/vectorclass/manual/master/vcl_manual.pdf) |

## Verdict

No measurement exists: the 2026-09-09 manual (section 8.3) only asserts that the inline and SVML-based vector math versions are 'many times faster than standard (scalar) math function libraries' and that VCL matches the optimization level of hand-written intrinsics, with no baseline library version, compiler, flags or CPU. A WebSearch this session also found no independent VCL-versus-libm, SLEEF or SVML timing.

## Use it when

- x86-64 hot loops where GCC/Clang auto-vectorization fails or is fragile: branchy per-element logic, data that must be rearranged, table lookups or calls to math functions inside the loop.
- Batch evaluation of exp/log/pow/sin/cos on float or double arrays where about 2 ULP accuracy, INF/NaN error signalling and flushed subnormals are acceptable.
- Code that must ship SSE2, AVX2 and AVX-512 builds from one source, with runtime dispatch by compiling the same file several times (dispatch_example1.cpp, dispatch_example2.cpp).
- Integer kernels dividing many lanes by the same divisor, or needing saturating, permute and lookup operations that are awkward to write with raw intrinsics.
- Projects on C++17 that want a mature, single-maintainer, Apache-2.0 wrapper rather than a C++20 multi-architecture library.

## Skip it when

- Anything that must also run on ARM, POWER or RISC-V: the README and manual say there are no plans for non-x86 support and point to Google Highway instead.
- Simple array loops the compiler already vectorizes; the manual itself recommends auto-vectorization when it works.
- Code that needs IEEE-exact behaviour: subnormal inputs, errno, floating-point traps, pow(NaN,0) = 1, or bit-identical results across instruction sets (signed zero and out-of-range indexes differ by instruction set).
- Builds that cannot take a proprietary binary: the vectormath_lib.h variant needs libsvml.a/libirc.a (Linux) or svml_dispmt.lib/libircmt.lib (Windows) copied from an Intel compiler installation; only the inline math headers are pure Apache-2.0.
- Teams that need a published performance baseline: neither the README nor the 2026-09-09 manual gives any timing, hardware or compiler for the 'many times faster than scalar libraries' claim.

## How it is fast

Every operator is a static inline wrapper over one or a few intrinsics, and C++17 template metaprogramming picks the cheapest instruction sequence for a given permute/blend index pattern and instruction set at compile time. Integer division by a vector-invariant or compile-time-constant divisor is replaced by multiply-and-shift (Divisor_i / const_int classes). The inline math functions use Cephes/VDT-derived polynomial approximations (Taylor polynomial for exp, Pade alternatives) with exponent-bit tricks for 2^n, and test all lanes with horizontal_and so the special-case (overflow, NaN, underflow) select path is skipped when every lane is in range; they also drop subnormal support and errno for speed.

## Compared with alternatives

Pick VCL over EVE when you are x86-only, stuck on C++17 rather than C++20, and want explicit fixed-width classes plus Agner Fog's documented per-function ULP bounds; pick EVE or Highway for ARM. Over math_intrinsics or SIMD-math-prims, VCL gives a full vector type system and roughly 2 ULP math instead of looser approximations, but those siblings at least publish timings against libm while VCL publishes none.

## Integration

| | |
|---|---|
| **Form** | header-only (plus optional instrset_detect.cpp source file for runtime CPU detection) |
| **Dependencies** | none for the core and inline math; optional Intel SVML (libsvml.a and libirc.a, or svml_dispmt.lib, libircmt.lib and the repo's svmlpatch.lib on 64-bit Windows) for vectormath_lib.h; optional add-on repo (containers, random, complex, quaternion, vector3d, decimal) |
| **Minimum toolchain** | C++17 (instrset.h #errors otherwise); GCC, Clang, MSVC (VS 2019 / _MSC_VER 1920+ recommended for AVX-512; MSVC cannot target AVX512F without AVX512DQ), Intel compiler 2021+; GCC 9 and older lack some zero-extend intrinsics and are worked around |
| **Platforms** | x86 and x86-64 only (Windows, Linux, macOS); SSE2 minimum, up to AVX2, FMA3, AVX512F/VL/BW/DQ/VBMI/VBMI2 and AVX512-FP16, selected at compile time by -m flags or INSTRSET |
| **Thread safety** | Vector objects are plain values with no shared state; the manual says containers are not safe for concurrent access and the MXCSR control word set by no_subnormals() is per thread, so each thread must set it |
| **Drop-in for the baseline** | partial: vector math overloads are named like libm (exp, log, sin, pow) but take vectors, so loops must be restructured into vector loads, operations and stores |

## Gotchas

- Inline log, exp, pow and root functions treat subnormal inputs as zero (log_special_cases for Vec8d under AVX512DQ maps a subnormal input to -INF, as for zero), never set errno or raise exceptions, and rely on INF/NaN propagation; -ffast-math, -ffinite-math-only or /fp:fast can disable that detection, and a NaN compared into a boolean vector silently becomes false.
- Out-of-range element indexes, shift counts and boolean vectors holding values other than 0/-1 give instruction-set-dependent results with no error (select works bit-by-bit before SSE4.1 and on the sign bit or high byte bit from SSE4.1), so an SSE2 build and an AVX2 build of the same code can disagree.
- When dispatching, vector objects must not cross between translation units compiled for different instruction sets (their representation differs); pass arrays instead. The manual's GCC flags for AVX/AVX2 include -fabi-version=0, alignment faults are possible before AVX when vectors sit in under-aligned containers, and instrset.h #undefs min/max and defines NOMINMAX on MSVC.
- Open issue #91 (2026-09-28), confirmed in instrset_detect.cpp: the AVX-512 OS-support test reads CPUID leaf 0xD (what the CPU can enable, masked with 0x60) instead of XGETBV XCR0 bits 5-7, so on an OS or VM that has not enabled ZMM state the optional dispatcher can report level 9+ and the AVX-512 path faults; the leaf-7 test also uses the signed shift 1 &lt;&lt; 31.

## Known shortcomings

- Manual says "many times faster" than scalar libm with no numbers (tier D); the SVML variant needs Intel's proprietary library; x86 only.
- No timing anywhere, and a WebSearch found no independent VCL vs libm/SLEEF/SVML timing. Bug confirmed in source: instrset_detect.cpp checks AVX-512 OS support with CPUID leaf 0xD masked with 0x60 instead of XGETBV XCR0 bits 5-7 (open issue #91, 2026-09-28), plus a signed 1 &lt;&lt; 31; the inline log/exp/pow flush subnormals (AVX512DQ log returns -INF); the SVML variant needs proprietary Intel libraries.

## Caveats and trade-offs

Tier D: the speed claims have no benchmark, hardware, compiler or flags. Included under the notable-D allowance (1.5k stars, 156 forks, very widely referenced, named repeatedly in HN threads about SIMD wrappers). The manual itself recommends compiler auto-vectorization where it works and positions VCL as the alternative when it fails. The external math-library variant (vectormath_lib.h) needs Intel's proprietary SVML from an Intel compiler installation; only the inline vectormath_\*.h functions are fully Apache-2.0. Inline math functions trade subnormal support for speed (per the author's forum remarks, snippet only). x86/x86-64 only; the README says there are no plans to support ARM. Manual date 2026-09-09 matches the latest commit.

x86 and x86-64 only (SSE2 up to AVX-512 and AVX512-FP16 types); the README says there are no plans for ARM or other instruction sets. Header-only, C++17 or later. The external vector math library variant needs Intel's SVML (Intel compiler); the inline variant is portable across GCC, Clang and MSVC. Manual rates exp-type math functions as 'poor' efficiency relative to simple operations, though still faster than scalar alternatives.

## Maintenance

Actively maintained by Agner Fog (version 2.02.04, 2026-09-09; 1.5k stars, 156 forks) and Apache-2.0 header-only, so easy to vendor, but the speed claim is tier D with no benchmark, and the optional runtime dispatcher has an open AVX-512 OS-state detection bug (#91).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now D.
- **Tier reason:** The manual (dated 2026-09-09) only says the inline and SVML-based vector math versions are 'many times faster than standard (scalar) math function libraries' (section 8.3); it has no benchmark, numbers, hardware or flags, and a WebSearch found no independent VCL-vs-libm/SLEEF timing, so D.
- **Verifier notes:** Record accurate: no numbers anywhere in the manual or README; Apache-2.0, 1.5k stars, last commit 2026-09-09 (version 2.02.04) confirmed. Shortcomings: no benchmark at all (tier D), SVML variant depends on proprietary Intel library, x86-only.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-96 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/vectorclass/manual/master/vcl_manual.pdf>
  - <https://raw.githubusercontent.com/vectorclass/version2/HEAD/README.md>
  - <https://raw.githubusercontent.com/vectorclass/version2/HEAD/LICENSE>
  - <https://github.com/vectorclass/version2>
  - <https://github.com/vectorclass/version2/commits>
- **Sources the enricher read:**
  - <https://github.com/vectorclass/version2>
  - <https://raw.githubusercontent.com/vectorclass/version2/HEAD/README.md>
  - <https://raw.githubusercontent.com/vectorclass/manual/master/vcl_manual.pdf>
  - <https://raw.githubusercontent.com/vectorclass/version2/HEAD/instrset_detect.cpp>
  - <https://raw.githubusercontent.com/vectorclass/version2/HEAD/instrset.h>
  - <https://raw.githubusercontent.com/vectorclass/version2/HEAD/vectormath_exp.h>
  - <https://raw.githubusercontent.com/vectorclass/version2/HEAD/changelog.txt>
  - <https://github.com/vectorclass/version2/issues?q=is%3Aissue>
  - <https://github.com/vectorclass/version2/issues/91>
  - <https://github.com/vectorclass/version2/issues/67>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/vectorclass/version2`) · [data/wave13/enrich/raw/github_com_vectorclass_version2.json](../../../data/wave13/enrich/raw/github_com_vectorclass_version2.json) (enrichment confidence 0.8)

</details>
