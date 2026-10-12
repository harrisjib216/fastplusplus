# FastDivide128 (komrad36)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Math, SIMD and linear algebra](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Unsigned 128-bit Div/Mod/DivMod for x86-64 with BMI2; author says about 2x faster than compiler-rt's __udivmodti4.

| | |
|---|---|
| **Beats** | compiler-rt __udivti3, __umodti3 and __udivmodti4 (unsigned 128-bit division as lowered by Clang) |
| **Claimed result** | README: 'about 2x faster than the compiler-rt stuff'; no timing table is given. |
| **Workload** | Unsigned 128-bit integer Div, Mod and DivMod on x86 Haswell or newer. |
| **Metric** | latency |
| **Hardware** | x86 Haswell or newer (model not stated) |
| **Compiler and flags** | README: primarily Clang (inline assembly where codegen was poor); compiles under GCC with worse code; no flags stated |
| **Adoption** | 4 stars |
| **Last commit** | 2021-02-14 |
| **Links** | [repository](https://github.com/komrad36/FastDivide128) · [benchmark](https://github.com/komrad36/FastDivide128) |

## Verdict

Nothing was measured publicly: the README states the Div, Mod and DivMod routines are 'about 2x faster than the compiler-rt stuff' (__udivti3, __umodti3, __udivmodti4) on Haswell or newer x86, with no timings, benchmark source, CPU model, compiler version or compiler-rt version. Because compiler-rt adopted the same DIVQ fast path and shift-subtract loop in July 2020, the size of any gain against a current toolchain is unknown.

## Use it when

- Runtime-variable unsigned 128-bit division or modulo in hot code (128-bit fixed point, reducing 64x64 products by a runtime modulus, big-ID hashing) built with Clang for x86-64 Haswell or newer.
- Clang targeting the MSVC ABI on Windows where unsigned __int128 division fails to link with unresolved __udivti3/__umodti3, and you would rather call a function than link compiler-rt builtins.
- Divisor mixes dominated by powers of two or 32-bit values, which take the TZCNT/BZHI and DIVL shortcuts that compiler-rt does not have.
- Code that needs quotient and remainder together: DivMod returns both from one call.

## Skip it when

- Compile-time-constant divisors or numerators: the README itself says a simpler specialised approach should be used, and compilers already strength-reduce constant division.
- Repeated division by the same 64-bit divisor: a precomputed-reciprocal library (libdivide, or the author's FastDivide) avoids DIV altogether.
- Divisors of 2^64 or more with a wide magnitude gap to the numerator: the bit-serial loop runs up to 64 iterations, the same algorithm compiler-rt uses, so expect little difference on that path.
- Non-x86 targets, MSVC proper (no __uint128_t, no GNU inline asm), CPUs without BMI1/BMI2/LZCNT (no runtime dispatch or fallback), or GCC builds (README: compiles but codegen is not as good).
- Anything that needs a tested or maintained dependency: no tests, no benchmark code, six commits on one day in February 2021.

## How it is fast

A case split runs before the general loop: D &gt; N returns 0 immediately; a power-of-two divisor is handled with TZCNT, a 128-bit shift and BZHI masks; a divisor below 2^64 uses one hardware DIVQ (or a 32-bit DIVL when the numerator's high word is zero, the divisor fits in 32 bits and the quotient fits in 32 bits), or two chained DIVQs when the quotient needs more than 64 bits. Divisors of 2^64 or more go through LZCNT-aligned restoring shift-subtract division with an inline-asm SUB/SBB/CMOVC/SBB step per quotient bit (up to 64 iterations). compiler-rt's __udivmodti4 has used the same DIVQ fast path and the same clz-aligned, branch-free shift-subtract loop since commit 68c011a (2020-07-10, D81809), seven months before this repo, so against current compiler-rt the differences are the DIVL and power-of-two shortcuts and the hand-written loop body.

## Compared with alternatives

libdivide and the author's FastDivide speed up 64-bit and 32-bit division by a reused runtime divisor, and fastmod handles 32-bit compile-time divisors; none of them divides an arbitrary 128-bit dividend by an arbitrary 128-bit divisor, which is the only case FastDivide128 covers. Pick it when both operands are unsigned __int128 and the divisor changes from call to call.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (immintrin.h intrinsics and GNU-style inline assembly) |
| **Minimum toolchain** | Clang with __uint128_t and AT&T-syntax GNU inline asm (primary target); GCC compiles with worse codegen per README and ignores the Clang-only '#pragma nounroll'; needs -mbmi -mbmi2 -mlzcnt or -march=haswell; no C++ standard stated (uses C++11 using-aliases) |
| **Platforms** | x86-64 only, Haswell or newer per README (uses LZCNT, TZCNT, BZHI, SHLX); no runtime CPU check |
| **Thread safety** | not documented; the functions are pure and keep no state, so concurrent calls are safe by inspection |
| **Drop-in for the baseline** | partial — same results as __udivti3/__umodti3/__udivmodti4 for nonzero divisors, but exposed as global Div, Mod and DivMod functions that must be called explicitly; the library does not define the compiler-rt symbols, so the / and % operators on __uint128_t are not redirected |

## Gotchas

- Division by zero does not trap: IsPow2(0, 0) returns true, so D = 0 takes the power-of-two path, sets rem = N and evaluates N &gt;&gt; 128, which is undefined behaviour in C++; compiler-rt instead reaches a hardware DIV by zero. Add your own zero check (found by reading fast-div-128.cpp; no test covers it).
- The 'about 2x faster than the compiler-rt stuff' claim has no benchmark code, numbers, CPU model, compiler version or compiler-rt version. The repo dates from 2021-02-14, after compiler-rt's July 2020 rewrite (commit 68c011a, which itself reported unsigned 128-bit small-divisor division falling from 153 ns to 27.1 ns on x86-64), so it is unknown whether the 2x was measured against the old bit-by-bit code or the current DIVQ-based code.
- Inline assembly is AT&T syntax, so builds with -masm=intel break; the names Div, Mod and DivMod live in the global namespace and may collide with other code.
- DivMod is defined out of line in fast-div-128.cpp, so each Div or Mod is a real function call unless you use LTO or move it into the header.

## Known shortcomings

- README says only "about 2x" against compiler-rt __udivti3 with no harness; 4 stars, all 6 commits on 2021-02-14; scalar, filed under math-simd-linear-algebra.
- The 'about 2x faster than compiler-rt' claim has no benchmark code; compiler-rt's __udivmodti4 gained the same divq fast path plus a clz shift-subtract loop in commit 68c011a (2020-07-10, D81809: 153 to 27.1 ns), seven months before this repo, so the baseline version is unknown and the remaining gain is only the DIVL and power-of-two shortcuts plus the asm loop. Code bug: D = 0 is counted as a power of two, so Div evaluates N &gt;&gt; 128 (undefined behaviour) with no trap and rem = N.

## Caveats and trade-offs

Prose claim only ('about 2x faster than the compiler-rt stuff'): no benchmark source, numbers, CPU model or compiler version. The baseline is compiler-rt's generic routine (which the README notes is also missing on Clang for Windows), not libgcc's __udivti3, a tuned library such as GMP, or a hand-written div-based 128/64 path. The library targets Clang with inline assembly; the README says GCC builds but with worse codegen, and x86 Haswell or newer is required. The whole history is six commits on 2021-02-14.

Written to fill the missing __udivti3 on Windows/Clang; uses inline assembly, so Clang-first and x86 Haswell+ only; one header plus fast-div-128.cpp; not for compile-time operands. Not SIMD, so a weak category fit.

## Maintenance

Abandoned since its single day of commits (2021-02-14; no issues, pull requests, tests or benchmarks), but MIT-licensed and about 100 lines, so it is easy to vendor after adding a divide-by-zero check and benchmarking it against the compiler-rt your own toolchain ships.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README says Div, Mod and DivMod for U128 on Haswell+ are 'about 2x faster than the compiler-rt stuff' (__udivti3, __umodti3, __udivmodti4); the repo has only fast-div-128.h/.cpp, README and LICENSE, with no benchmark code, numbers table, CPU model or compiler version. First-party figure without methodology: tier C (borderline D).
- **Verifier notes:** Real, MIT, 4 stars, 6 commits all on 2021-02-14, abandoned; '2x' is an unmeasured README figure, kept at C as the record had it (could be argued D). Same author and category question as FastDivide: libdivide sits in math-simd-linear-algebra.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-77 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/komrad36/FastDivide128>
  - <https://raw.githubusercontent.com/komrad36/FastDivide128/HEAD/README.md>
  - <https://raw.githubusercontent.com/komrad36/FastDivide128/HEAD/LICENSE>
  - <https://github.com/komrad36/FastDivide128/commits>
- **Sources the enricher read:**
  - <https://github.com/komrad36/FastDivide128>
  - <https://github.com/komrad36/FastDivide128/commits>
  - <https://github.com/komrad36/FastDivide128/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/komrad36/FastDivide128/HEAD/README.md>
  - <https://raw.githubusercontent.com/komrad36/FastDivide128/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/komrad36/FastDivide128/HEAD/fast-div-128.h>
  - <https://raw.githubusercontent.com/komrad36/FastDivide128/HEAD/fast-div-128.cpp>
  - <https://raw.githubusercontent.com/llvm/llvm-project/main/compiler-rt/lib/builtins/udivmodti4.c>
  - <https://github.com/llvm/llvm-project/commits/main/compiler-rt/lib/builtins/udivmodti4.c>
  - <https://github.com/llvm/llvm-project/commit/68c011aa085ab8ec198198e45c83de605a7dc31f>
  - WebSearch: clang Windows __udivti3 unresolved external symbol (results: lists.llvm.org cfe-dev 2017-November thread naming LLVM bug 25305; no source showing it fixed)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/komrad36/fastdivide128`) · [data/wave13/enrich/raw/github_com_komrad36_fastdivide128.json](../../../data/wave13/enrich/raw/github_com_komrad36_fastdivide128.json) (enrichment confidence 0.65)

</details>
