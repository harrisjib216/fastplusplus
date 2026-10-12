# SIMD Everywhere

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Math, SIMD and linear algebra](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Header-only C99 library implementing x86 (MMX to AVX2, parts of AVX-512), Neon and WASM SIMD intrinsics on any target, beating scalar ports.

| | |
|---|---|
| **Beats** | unvectorized (scalar) implementation of the same program (VVenC/VVdeC ported from x86 SSE/AVX to Arm) |
| **Claimed result** | More than 200% performance gain over unvectorized code on Arm (search-result text of the Arm Community blog post 'Part 1: Porting to Arm Intrinsics with SIMDe'; snippet only). A separate arXiv paper (2309.16509, 'SIMD Everywhere Optimization from ARM NEON to RISC-V Vector Extensions', snippet only) reports 1.51x to 5.13x over the original SIMDe on XNNPACK for an RVV-enhanced SIMDe, which is a different baseline. |
| **Workload** | Fraunhofer HHI VVenC encoder and VVdeC decoder (H.266/VVC) whose x86 SSE/AVX intrinsics were translated to Arm Neon automatically through SIMDe, compared with the unvectorized build. |
| **Metric** | throughput |
| **Adoption** | 3.1k stars; used by Bowtie 2, MMseqs2, OBS Studio, wabt, vvenc/vvdec, vectorscan, Firefox (WASM SIMD128 builds), plink2 and over 30 other projects listed on its wiki |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/simd-everywhere/simde) · [benchmark](https://developer.arm.com/community/arm-community-blogs/b/tools-software-ides-blog/posts/porting-to-arm-intrinsics-with-simde) |

## Verdict

No reproducible benchmark exists: SIMDe's repo, README and wiki carry no numbers, and the only figures are search snippets of a blocked Arm Community blog (VVenC/VVdeC ported from SSE/AVX to Neon with SIMDe, 'over 200% performance gains', baseline apparently the unvectorized build, no hardware or compiler given) and of a blocked arXiv paper (2309.16509, an RVV-enhanced SIMDe 1.51x to 5.13x faster than the original SIMDe on XNNPACK, a different baseline).

## Use it when

- Porting an existing code base written with SSE/AVX intrinsics to Arm (Graviton, Apple silicon, Android) or WebAssembly, where the alternative is the scalar fallback build.
- Getting a vectorized port running first and profiling it, then rewriting only the hottest kernels in native Neon, as the AWS Graviton guide and Fraunhofer's VVdeC work did.
- Keeping one intrinsics source tree across x86, Arm, POWER, s390x, LoongArch, RISC-V and emscripten in CI, or developing Neon code on an x86 machine without an emulator.
- C or C++ projects that need a dependency-free header drop-in; it is packaged by Debian and other distributions.

## Skip it when

- Writing new portable SIMD code from scratch: a portable abstraction (xsimd, Highway) or native intrinsics per target avoid emulating one ISA's semantics on another.
- Kernels that dominate run time on the non-native target: translated code cannot fuse operations the way a hand port can, and some fallbacks (exact NaN handling for min/max, round-to-even on ARMv7, current-rounding-mode conversions) are slow; nothing warns when a call falls back to a scalar loop (issue #310, open since 2020).
- Targets or ISA subsets without native mappings, where the fallback depends on the auto-vectorizer: performance then hinges on -O3 plus -fopenmp-simd -DSIMDE_ENABLE_OPENMP and varies by target, so each port needs its own benchmarks.
- Code that relies on x86 side effects SIMDe cannot reproduce portably: _mm256_test\* flags, _mm256_zeroupper/zeroall, and MXCSR bits other than the rounding mode.
- Anyone needing a recent stable release: the last stable tag is v0.8.2 (2024-04-30) and v0.8.4 has been at release candidate since 2025 (rc3 2026-02-22).

## How it is fast

Each intrinsic is a compile-time cascade: the native instruction if available, else an equivalent from the target's own ISA (Neon, WASM SIMD128, AltiVec/z vector, LoongArch LSX, partial RVV), else GCC/Clang vector extensions and __builtin_shufflevector/__builtin_convertvector, else a plain loop annotated with OpenMP 4 SIMD or loop pragmas for the auto-vectorizer. After inlining, a translated intrinsic often becomes one or a few target instructions, so the gain reported for VVenC/VVdeC on Arm is the gain of keeping the SIMD code paths instead of compiling the scalar fallback. Optional SIMDE_FAST_\* macros drop exact NaN, rounding-mode and conversion-range emulation for speed.

## Compared with alternatives

Pick SIMDe over xsimd when the code already exists as x86 or Neon intrinsics and must run elsewhere unchanged; xsimd (or Highway) is the better base for new code because it exposes a portable vector type instead of one vendor's instruction set. SLEEF and NumKong are complementary: they supply vectorized math functions and similarity kernels, not a translation layer.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none at run time; &lt;math.h&gt;/&lt;fenv.h&gt; needed for some functions to be defined; OpenMP SIMD flags optional; meson &gt;= 0.64 only for the test suite |
| **Minimum toolchain** | C99 (the MSVC subset works); usable from C++; CI-tested back to GCC 4.8, Clang 3.8 and MSVC 2013, plus ICC and IBM XL |
| **Platforms** | any C99 target; CI covers x86, x86-64, AArch64, ARMv8, ARMv7, ARMv5, PPC64, s390x, MIPS Loongson, RISC-V 64, LoongArch64 and emscripten; acceleration depends on the target's SIMD extension |
| **Thread safety** | not documented; intrinsics are stateless value functions, but SIMDE_MM_SET_ROUNDING_MODE and simde_mm_setcsr emulate MXCSR through fesetround(), changing the floating-point environment |
| **Drop-in for the baseline** | partial: replaces the native intrinsic headers rather than a scalar library; with SIMDE_ENABLE_NATIVE_ALIASES the original names work (the README calls this error-prone and recommends it only for testing), and char-based Intel signatures become int8_t |

## Gotchas

- Compiling with -ffast-math or -ffinite-math-only silently defines SIMDE_FAST_MATH or SIMDE_FAST_NANS (simde-common.h), switching emulated intrinsics to the target's own NaN, rounding and conversion-range behaviour: _mm_min_ps then maps straight to vminq_f32, which returns NaN where SSE returns the non-NaN operand. Define SIMDE_NO_FAST_\* to keep exact x86 results.
- Including the native header after a SIMDe header with native aliases enabled causes compile errors; on 32-bit Windows x86 some MMX and __m64-using SSE/SSE2 functions may return wrong results with native aliases.
- The catalogue's speedup is not measured against SIMDe alternatives: the 'over 200%' VVenC/VVdeC figure (Arm Community blog, 2024-06-26, retelling Bross et al., 'Open and optimized VVC Implementations on ARM Architectures', MHV '23, ACM, per the VVdeC wiki) is SIMDe-translated SIMD versus the scalar build, known here only from search snippets, with no hardware, compiler or flags.
- Search snippets of Fraunhofer's FOSDEM 2024 talk 'VVdeC&lt;&gt;Arm' (slides EGRESS_BLOCKED) say hand-written arm_neon.h kernels ranged from about 0.5x to 3.0x of their SIMDe versions and gained 0-10% on average for the whole decoder over 11 JVET sequences, with the authors concluding SIMDe 'does a decent job'; VVdeC v2.1 (2023-11-08) shipped that 'initial native ARM SIMD implementation'.

## Known shortcomings

- Evidence is a snippet of a 2023 Fraunhofer HHI study on the Arm developer blog (blocked): the 'over 200%' is SIMD over the scalar fallback, not over another SIMD route, and SIMDe carries overhead against hand-written NEON; no page could be opened (strict null-page reading would make it D). Filed under stdlib-replacements/math-simd-linear-algebra.
- Enricher: FOSDEM 2024 snippets put hand-written NEON kernels at about 0.5x-3.0x of their SIMDe versions while the whole VVdeC decoder gained only 0-10% over SIMDe across 11 JVET sequences (the Arm paper is MHV '23, DOI 10.1145/3588444.3591001); -ffast-math silently turns on SIMDE_FAST_NANS and changes min/max NaN results; last stable release v0.8.2 (2024-04-30). Weak lead: DLTcollab/sse2neon.

## Caveats and trade-offs

Numbers are snippet only: the Arm Community blog post 'Porting to Arm Intrinsics with SIMDe Part 1' (developer.arm.com, published 2024-06-26 per search snippet; EGRESS_BLOCKED here), its source study 'Open and optimized VVC Implementations on ARM Architectures' (Bross, Lehmann, Hege, Wieckowski, Fraunhofer HHI, 2023; abstract in CEUR-WS Vol-3562 SEViC23-abstract5, EGRESS_BLOCKED), the FOSDEM 2024 VVdeC-on-Arm slides (EGRESS_BLOCKED) and arXiv 2309.16509 (EGRESS_BLOCKED) could not be opened, so hardware, compiler flags, per-workload breakdown and the exact baseline are unverified; my snippets say 'over 200% performance gains' without naming the baseline, the earlier search agent's snippet said over unvectorized code. The baseline is the program's own scalar fallback, not one of the category baselines (std::valarray, std::transform, std::reduce, &lt;cmath&gt;), and the gain is that of SIMD vectorization rather than of SIMDe over another SIMD route; SIMDe's translation has overhead versus hand-written Neon (the AWS Graviton SIMD guide advises rewriting hot paths in native Neon after a SIMDe port, and Fraunhofer later hand-optimized VVdeC with arm_neon.h). The arXiv paper's baseline is SIMDe itself (RVV-enhanced vs original SIMDe on XNNPACK). On x86 with native intrinsics SIMDe should simply match them. The SIMDe README, wiki and repo have no benchmark numbers or benchmark directory. Needs a second pass from a thread that can open developer.arm.com, ceur-ws.org and arxiv.org.

Header-only portable implementations of x86 (MMX to AVX-512), NEON, WASM SIMD128 and other intrinsic sets; use the native instruction when available, otherwise a fallback that depends on compiler auto-vectorization (README strongly recommends -O3 and OpenMP SIMD pragmas via -fopenmp-simd or SIMDE_ENABLE_OPENMP). Some fallbacks are slow on a given target and which of two code paths is faster varies by target (wiki FAQ), so porting needs per-target benchmarking. Intel's char-based signatures become int8_t, which can need minor source changes.

## Maintenance

Actively maintained (3.1k stars, 323 forks, 129 open issues, last commit 2026-09-30) and MIT-licensed, but releases lag: v0.8.2 (2024-04-30) is the latest stable tag and v0.8.4 is at rc3; evidence stays tier C on snippets only, and a thread that can open developer.arm.com, archive.fosdem.org or the MHV '23 paper (DOI 10.1145/3588444.3591001) could add hardware and per-kernel numbers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The only numbers are search snippets of a blocked Arm Community blog post (June 2024, retelling a 2023 Fraunhofer HHI study, 'over 200% performance gains' for VVenC/VVdeC ported to Neon with SIMDe) and of arXiv 2309.16509 (1.51x to 5.13x over original SIMDe); no hardware, compiler, flags or harness could be read, and the SIMDe repo and wiki carry no benchmark, so C (snippet only) at best.
- **Verifier notes:** Tier C kept on snippet-only evidence (Arm blog URL found via search and set as benchmark_url, but EGRESS_BLOCKED, as were the CEUR-WS abstract, FOSDEM slides and ar5iv/arXiv); if the orchestrator wants the strict null-page rule, it is D. Shortcomings: snippet-only numbers, baseline is scalar fallback code outside the category list, the speedup is SIMD over scalar rather than SIMDe over an alternative, and SIMDe has overhead versus hand-written Neon. Metadata checked: MIT (COPYING is the MIT text), 3.1k stars, 323 forks, last commit 2026-09-30, not archived, not a fork.
- **Fields the verifier corrected:** `benchmark_url`, `baseline_in_list`, `caveats`
- **Shortcomings recorded by:** Arm blog snippet (verifier); enricher snippet reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/simd-everywhere/simde/HEAD/README.md>
  - <https://raw.githubusercontent.com/simd-everywhere/simde/HEAD/COPYING>
  - <https://github.com/simd-everywhere/simde>
  - <https://github.com/simd-everywhere/simde/commits>
  - <https://raw.githubusercontent.com/fraunhoferhhi/vvdec/HEAD/README.md>
  - <https://raw.githubusercontent.com/fraunhoferhhi/vvenc/HEAD/README.md>
  - <https://raw.githubusercontent.com/aws/aws-graviton-getting-started/main/SIMD_and_vectorization.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/simd-everywhere/simde/HEAD/README.md>
  - <https://raw.githubusercontent.com/simd-everywhere/simde/HEAD/COPYING>
  - <https://raw.githubusercontent.com/simd-everywhere/simde/HEAD/simde/simde-common.h>
  - <https://raw.githubusercontent.com/simd-everywhere/simde/HEAD/simde/simde-arch.h>
  - <https://raw.githubusercontent.com/simd-everywhere/simde/HEAD/simde/x86/sse.h>
  - <https://raw.githubusercontent.com/simd-everywhere/simde/HEAD/meson.build>
  - <https://github.com/simd-everywhere/simde>
  - <https://github.com/simd-everywhere/simde/wiki/FAQ>
  - <https://github.com/simd-everywhere/simde/releases>
  - <https://github.com/simd-everywhere/simde/tags>
  - <https://github.com/simd-everywhere/simde/issues?q=is%3Aissue+label%3Aperformance>
  - <https://github.com/simd-everywhere/simde/issues?q=is%3Aissue+slow>
  - <https://github.com/simd-everywhere/simde/issues/291>
  - <https://github.com/simd-everywhere/simde/issues/310>
  - <https://raw.githubusercontent.com/aws/aws-graviton-getting-started/main/SIMD_and_vectorization.md>
  - <https://raw.githubusercontent.com/fraunhoferhhi/vvenc/HEAD/README.md>
  - <https://raw.githubusercontent.com/fraunhoferhhi/vvdec/HEAD/README.md>
  - <https://github.com/fraunhoferhhi/vvdec/wiki/Changelog>
  - <https://github.com/fraunhoferhhi/vvdec/wiki/Publications>
  - <https://github.com/Sahamec/VVdeC2_ARM_Neon>
  - https://developer.arm.com/community/arm-community-blogs/b/tools-software-ides-blog/posts/porting-to-arm-intrinsics-with-simde (EGRESS_BLOCKED; search snippet only)
  - https://archive.fosdem.org/2024/schedule/event/fosdem-2024-2400-vvdec-arm-optimizing-an-open-source-vvc-decoder-for-arm-architectures (EGRESS_BLOCKED; search snippet only)
  - https://publica.fraunhofer.de/entities/publication/51a5dcb1-c96e-4d73-88b0-1e5c335fd32f (EGRESS_BLOCKED)
  - https://gitlab.citsem.upm.es/victor.arandal/vvenc-simde-neon (EGRESS_BLOCKED)
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/simd-everywhere/simde`) · [data/wave1/enrich/raw/github_com_simd_everywhere_simde.json](../../../data/wave1/enrich/raw/github_com_simd_everywhere_simde.json) (enrichment confidence 0.65)

</details>
