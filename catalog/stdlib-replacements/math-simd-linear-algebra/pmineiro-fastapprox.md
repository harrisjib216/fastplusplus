# fastapprox

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Math, SIMD and linear algebra](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `BSD-3-Clause` · 🔴 abandoned

> Header-only C/C++ single-precision approximations of exp, log, pow, sigmoid, trig, erf, lgamma and Lambert W, with SSE2 variants; no measured speedup over libm.

| | |
|---|---|
| **Beats** | libm expf/logf/powf (single-precision libm; the repo's tests use them as the accuracy reference, libm is never timed) |
| **Claimed result** | No speed ratio against libm is stated anywhere in the repo (README is a function list plus one sentence; no results file is committed). Accuracy bounds asserted by the tests against expf/logf/powf: average relative error below 1e-4 for the 'fast' variants (fastexp, fastlog, fastpow, fastsigmoid) and below 2e-2 for the 'faster' variants (fasterexp, fasterlog, fasterpow, fastersigmoid). |
| **Workload** | Test programs (fastapprox/tests/testfastexp.c, testfastlog.c, testfastsigmoid.c, testfastpow.c, ...) assert average relative error over 100000 random inputs against expf, logf, powf, sinf, tanhf, erff and similar, and print million calls per second of the approximation only (1e8 calls on a volatile constant input 1.0f); no libm timing row exists. |
| **Metric** | throughput |
| **Adoption** | 13 stars on pmineiro/fastapprox; 222 stars on the romeric/fastapprox mirror and 57 on etheory/fastapprox; the Rust port (crate 'fastapprox' by loony-bean) has 94,746 downloads on crates.io |
| **Last commit** | 2017-03-01 |
| **Links** | [repository](https://github.com/pmineiro/fastapprox) · [benchmark](https://raw.githubusercontent.com/pmineiro/fastapprox/HEAD/fastapprox/tests/testfastexp.c) |

## Verdict

No speed comparison against libm exists: the repo's tests assert that average error on the metric above stays under 1e-4 (fast tier) and 2e-2 (faster tier) against expf, logf, powf, sigmoid built from expf, sinf and others over 100000 drand48 samples in fixed ranges, and time only the approximation on a constant input with no compiler, flags or CPU recorded. The only first-party speed statement is directional and partly negative (fasttrig.h: the full-range trig versions can be slower than libc on older machines).

## Use it when

- Machine-learning or probabilistic inner loops (logistic loss, softmax-like weights, digamma and lgamma in variational updates) that tolerate about 1e-4 relative error and keep arguments in moderate ranges.
- SSE2 batch evaluation of exp, log or sigmoid where a full vector math library is too heavy to pull in.
- Plain C codebases that want a single BSD-licensed header with no dependencies.
- Graphics, audio or game code that only needs 2-3 correct digits and can use the 'faster' tier.
- As a reference for the bit-manipulation techniques (the repo includes a Mathematica notebook explaining them).

## Skip it when

- Inputs outside the tested ranges: fastexp/fasterexp return NaN or a negative number instead of +inf for x above about 88.7, so fastsigmoid(x) returns NaN, 1.0 or a small negative number instead of nearly 0 for x below about -88.7, and fasttanh(x) returns NaN or +1 instead of -1 just below x = -44.4 (fasttanh(-45) and fasttanh(-50) give +1).
- Code that relies on libm special values: fastlog(0) is about -88.0 instead of -inf, fastlog(-1) about +177 instead of NaN, and NaN or inf inputs give finite values near 89.
- When you need a documented speedup: the repo never times libm, and the author's own fasttrig.h comment says fastsinfull, fastcosfull and fasttanfull can be slower than libc on older machines and only slightly faster on newer ones.
- Double precision, faithfully rounded results or reproducible ulp bounds: everything is float and accuracy is only checked as an average.
- AVX2, AVX-512 or NEON vectorization: only SSE2 four-wide variants exist, and the project has had no commits since 2017.

## How it is fast

It works on the IEEE-754 bit pattern instead of doing range reduction and polynomials: the 'faster' variants are Schraudolph-style tricks (exp2 builds the float bits as 2^23 \* (p + 126.94), log2 reads the raw bits as an integer and rescales), and the 'fast' variants add a small rational correction on the mantissa fraction (for example 27.728 / (4.8425 - z) in pow2). Sigmoid, pow, sinh, cosh and tanh are composed from these; sin and cos use a parabola-plus-correction approximation on [-pi, pi]; there are no branches except input clamps, so the SSE2 versions are straight-line code.

## Compared with alternatives

Pick fastapprox over SLEEF when 1e-4 average error is acceptable and you want one dependency-free header with sigmoid, lgamma, digamma, erf-inverse and Lambert W in it; pick SLEEF (1-ulp, AVX2/AVX-512/NEON, maintained) or fast_math_cpp (scalar float approximations with measured speed against glibc) when you need stated accuracy bounds or a measured speedup.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (stdint.h; emmintrin.h when __SSE2__ is defined) |
| **Minimum toolchain** | C99 or C++ (GCC or Clang vector extensions for the C SSE2 path; MSVC supported for C++ through operator overloads added in the 2017 patch) |
| **Platforms** | any for the scalar functions; x86 with SSE2 for the v4sf variants, which are compiled only when __SSE2__ is defined (MSVC does not define that macro by default, so the vector variants are absent there unless it is defined by hand) |
| **Thread safety** | reentrant pure functions (no global mutable state, only static const constants), from reading the source; not documented |
| **Drop-in for the baseline** | partial — same scalar float signatures as expf/logf/powf/sinf/tanhf under different names, but approximate (about 1e-4 or 2e-2 average error) and without libm's handling of overflow, zero, negative, NaN and infinite inputs |

## Gotchas

- Overflow bug outside the tested domain (checked this session by compiling a transcription of fastexp.h formulas with GCC -O2 on x86-64): fastexp(89) and fasterexp(89) return NaN, fastexp(90) returns -9.3e-39 and fastexp(200) returns -6.2e9 where expf returns inf, because the 2^23 \* (p + 121.27 + ...) bit pattern spills past the exponent field into the sign bit and nothing clamps the top end; vfasterexp returns -0.0 there. The composed functions inherit it: fastsigmoid(-90) and fastersigmoid(-90) return 1.0 (true value about 8e-40) and fasttanh(-45) returns +1.0 instead of -1.0. The tests never see this because they sample exp on [-5, 5], sigmoid on [-50, 50] and sinh and cosh on [-25, 25]; inputs past the 2^32 limit make the float-to-uint32 cast undefined behaviour. Clamp arguments yourself.
- The tests' accuracy metric is |est - exact| / (1e-4 + |est| + |exact|) and only its average over 100000 samples is asserted (max error is printed, not checked): it is about half the usual relative error and becomes an absolute-error test for outputs below 1e-4, so the '1e-4' figure understates the conventional relative error, especially for small sigmoid outputs.
- The timing macro in tests/testmacros.h runs the approximation 1e8 times on a volatile constant 1.0f with gettimeofday and never runs libm, so the printed million calls per second is not a comparison.
- Type punning goes through unions, which is defined in C but formally undefined in C++ (GCC, Clang and MSVC accept it); cast.h's include guard never defines __CAST_H_, which is harmless because the macro is redefined identically.

## Known shortcomings

- No speed number anywhere: the tests only check accuracy against expf (1e-4 fast, 2e-2 faster) and the timing loop times the approximation alone on a volatile 1.0f, never libm. Abandoned since 2017-03-01, a fork of etheory/fastapprox; BSD-3-Clause from COPYING. Author's blog unreachable.
- Enricher (compiled transcription of the formulas, GCC -O2): fastexp and fasterexp have no upper clamp, so fastexp(89) is NaN and fastexp(90) is -9.3e-39 (vfasterexp gives -0), which makes fastsigmoid(-90) return 1.0 and fasttanh(-45) return +1; fastlog(0) is -88 and fastlog(-1) +177. The tests sample exp only on [-5,5] and sigmoid on [-50,50] with an error metric about half the usual relative error, asserting only the average. fasttrig.h warns full-range trig can be slower than libc on older machines; SSE2 variants are missing on MSVC unless __SSE2__ is defined by hand.

## Caveats and trade-offs

The seed lead said the README and tests give speed versus libm; they do not. The README is four lines, the timing macro in tests/testmacros.h times only the approximation function on a volatile constant (1.0f, so a perfectly predictable input), and libm is never timed, so there is no speedup number to quote. The author's original blog post (machinedlearnings.com) could not be reached from this environment (host not resolvable), so any speed claim made there is unverified. Independent hints are indirect: the unrelated SIMD-math-prims README (github.com/mipac/SIMD-math-prims, a different library, CPU unstated) reports expapprox 2366.8M/s against expf 111.3M/s and logapprox 4112.9M/s against logf 115.2M/s, and a search snippet (page not openable) of a BEAST mailing-list thread says glibc exp2/log2 can beat hand-rolled approximations on modern AMD64, so speed against current glibc is hardware-dependent. The repo page shows no detected licence; the BSD-3-Clause terms come from fastapprox/COPYING and the file headers. The page marks pmineiro/fastapprox as a fork of etheory/fastapprox, which in turn is a fork of romeric/fastapprox (222 stars); the code originated in the author's Google Code project. Last commit is the 2017-03-01 merge of an MSVC and gcc narrowing patch. [retier] Enricher: fastexp and fasterexp have no upper clamp (fastexp(89) is NaN, fastexp(90) negative), so fastsigmoid(-90) returns 1.0 and fasttanh(-45) returns +1; fastlog(0) is -88 and fastlog(-1) +177; the tests cover exp only on [-5,5] and assert only an average error.

Single precision only, two accuracy tiers (fast: about 1e-4 average relative error; faster: about 2e-2). Header-only and usable from C and C++ (one big header, fastonebigheader.h) with SSE2 four-wide v4sf variants of each function. Uses union type punning on the float bit pattern. fastexp clamps its argument at -126 so underflow gives a small positive value; the ChangeLog says that guard cost 25% speed. fastlog has no guard for zero, negative, NaN or infinite input (source read). Also covers lgamma, digamma, trig, hyperbolic, erf, inverse erf and Lambert W.

## Maintenance

Abandoned since the 2017-03-01 MSVC and gcc narrowing merge (ChangeLog stops at 0.3.2), BSD-3-Clause per fastapprox/COPYING and small enough to vendor, but the unclamped exp overflow that breaks sigmoid and tanh for large negative arguments must be patched or guarded by the caller.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now D.
- **Tier reason:** fastapprox/tests/testfastexp.c and tests/testmacros.h only assert accuracy against expf (average relative error below 1e-4f for fastexp and vfastexp, below 2e-2f for fasterexp and vfasterexp over 100000 drand48 inputs) and time the approximation alone (1e8 calls on a volatile 1.0f via gettimeofday); libm is never timed and no results file or speed ratio exists in the repo, so there are no speed numbers against the baseline. A search found no reachable first-party or third-party speed figure either.
- **Verifier notes:** Record is accurate: the accuracy bounds in claimed_speedup appear in the test file, the timing macro times only the approximation on a constant input, and metadata checks out (13 stars, fork of etheory/fastapprox, no licence detected on the page but BSD-3-Clause text in fastapprox/COPYING, last commit 2017-03-01 'Etheory patch gcc narrowing fix + MSVC support', romeric/fastapprox 222 stars, Rust crate fastapprox 94,746 downloads). Shortcoming to record: no speed measurement against libm anywhere (tier D, speed versus current glibc is hardware-dependent and unmeasured), abandoned since 2017; kept as a widely ported approximation library rather than rejected.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-75 (wave 1 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/pmineiro/fastapprox/HEAD/fastapprox/tests/testfastexp.c>
  - <https://raw.githubusercontent.com/pmineiro/fastapprox/HEAD/fastapprox/tests/testmacros.h>
  - <https://raw.githubusercontent.com/pmineiro/fastapprox/HEAD/fastapprox/COPYING>
  - <https://github.com/pmineiro/fastapprox>
  - <https://github.com/pmineiro/fastapprox/commits>
  - <https://github.com/romeric/fastapprox>
  - <https://crates.io/api/v1/crates/fastapprox>
- **Sources the enricher read:**
  - <https://github.com/pmineiro/fastapprox>
  - <https://raw.githubusercontent.com/pmineiro/fastapprox/HEAD/fastapprox/ChangeLog>
  - <https://raw.githubusercontent.com/pmineiro/fastapprox/HEAD/fastapprox/src/fastexp.h>
  - <https://raw.githubusercontent.com/pmineiro/fastapprox/HEAD/fastapprox/src/fastlog.h>
  - <https://raw.githubusercontent.com/pmineiro/fastapprox/HEAD/fastapprox/src/fastpow.h>
  - <https://raw.githubusercontent.com/pmineiro/fastapprox/HEAD/fastapprox/src/fastsigmoid.h>
  - <https://raw.githubusercontent.com/pmineiro/fastapprox/HEAD/fastapprox/src/fasttrig.h>
  - <https://raw.githubusercontent.com/pmineiro/fastapprox/HEAD/fastapprox/src/sse.h>
  - <https://raw.githubusercontent.com/pmineiro/fastapprox/HEAD/fastapprox/src/cast.h>
  - <https://raw.githubusercontent.com/pmineiro/fastapprox/HEAD/fastapprox/src/fastonebigheader.h>
  - <https://raw.githubusercontent.com/pmineiro/fastapprox/HEAD/fastapprox/tests/testmacros.h>
  - <https://raw.githubusercontent.com/pmineiro/fastapprox/HEAD/fastapprox/tests/testfastexp.c>
  - <https://raw.githubusercontent.com/pmineiro/fastapprox/HEAD/fastapprox/tests/testfastlog.c>
  - <https://raw.githubusercontent.com/pmineiro/fastapprox/HEAD/fastapprox/tests/testfastsigmoid.c>
  - <https://raw.githubusercontent.com/pmineiro/fastapprox/HEAD/fastapprox/tests/testfasttrig.c>
  - <https://raw.githubusercontent.com/pmineiro/fastapprox/HEAD/fastapprox/tests/testfasthyperbolic.c>
  - <https://github.com/romeric/fastapprox/issues?q=is%3Aissue>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/pmineiro/fastapprox`) · [data/wave1/enrich/raw/github_com_pmineiro_fastapprox.json](../../../data/wave1/enrich/raw/github_com_pmineiro_fastapprox.json) (enrichment confidence 0.8)

</details>
