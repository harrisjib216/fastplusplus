# FastDivide (komrad36)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Math, SIMD and linear algebra](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Branch-free 64-bit unsigned divide and modulo via a Newton-Raphson reciprocal; claims about 30% faster than hardware div on Intel.

| | |
|---|---|
| **Beats** | hardware 64-bit unsigned div instruction (what a runtime a / b and a % b compile to on x86-64) |
| **Claimed result** | README: 'About 30% faster' than the hardware div instruction, 'at least on Intel, where div is crazy slow'; no timing table is given. |
| **Workload** | 64-bit unsigned integer division and modulo of arbitrary runtime operands, plus an optional precomputed-divisor class for repeated division by the same divisor. |
| **Metric** | latency |
| **Hardware** | Intel x86-64 (model not stated) |
| **Compiler and flags** | README: supports Clang, GCC and MSVC; no flags stated |
| **Adoption** | 32 stars |
| **Last commit** | 2021-09-30 |
| **Links** | [repository](https://github.com/komrad36/FastDivide) · [benchmark](https://github.com/komrad36/FastDivide) |

## Verdict

The README asserts 'About 30% faster' than the hardware 64-bit div 'at least on Intel' with no benchmark code, CPU model, compiler version, operand distribution or latency-versus-throughput distinction; the only timings the author posted (issue #1: C path 0.310 vs inline-asm path 0.283, units and CPU unstated) compare the library with itself. Correctness, not speed, was checked here with a Python model of the GCC/Clang asm path: exact quotients and remainders for 660,231 (N, D) pairs over 191,217 divisors, including every divisor within 300 of a power of two, with the class's reciprocal equal to floor(2^64/D) (saturated at 2^64-1 for D = 1) in every case.

## Use it when

- Latency-bound 64-bit unsigned division by divisors that change from call to call, on Intel cores of the Haswell-to-Skylake-derivative generation where DIV r64 is slow (the README hedges: 'at least on Intel').
- Code that needs data-independent timing for 64-bit division (the README's crypto use case), built with GCC or Clang so the branch-free inline-asm path is used.
- A divisor reused a handful of times, where FastDivider's setup (one Newton sequence, no branching on divisor class) is cheaper than heavier precomputation schemes.
- Hot loops with spare registers: the asm pins N to rcx, D to rdx and the result to rax and needs two more scratch registers.

## Skip it when

- Recent CPUs with fast dividers: search snippets give DIV r64 latency of about 14-18 cycles on Rocket Lake and Alder Lake-P (uops.info) and 9-17 cycles on Zen 3, well under this routine's chain of about a dozen serial multiplies, so it is probably slower there; benchmark before adopting.
- Divisors known at compile time (the README itself says the compiler's multiply-shift codegen is better) or a divisor reused millions of times (libdivide or fastmod).
- Register-starved inner loops: the README warns that spills caused by the extra registers can erase the gain.
- Signed or 32-bit division, non-x86-64 targets, or x86 CPUs without LZCNT and BMI2 (pre-Haswell Intel, pre-Excavator AMD); no runtime CPU check exists.
- Code that relies on a divide-by-zero trap: the result is simply undefined.

## How it is fast

It replaces the microcoded DIV with multiplies: lzcnt plus two BMI2 shifts (shlx/shrx) give a 2-bit-accurate first guess of floor(2^64/D) from a first-order expansion around the normalized divisor, five Newton-Raphson steps (M += umulh(M, -M\*D)) double the correct bits up to 64, and a multiply-high by N gives a quotient at most 2 below the true one, corrected with add/cmov/adc instead of branches. There are no table lookups or branches, so the cost does not depend on the operands; FastDivider hoists the Newton steps out of the loop, so each later divide is one mul, one imul and a carry fix-up. The standalone path is a serial chain of about a dozen 64-bit multiplies, so it can only win where DIV r64 is slow (42-95 cycles latency on Skylake per Agner Fog's tables, as quoted in a search snippet).

## Compared with alternatives

Pick it over libdivide or fastmod when the divisor changes on nearly every call and you want a branch-free, constant-time 64-bit divide on an older Intel core; when one divisor is reused many times, libdivide (precomputed magic numbers, up to 10x claimed for 64-bit, SIMD variants) or fastmod (32-bit operands) fit better, and for 128-bit operands use the same author's FastDivide128.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (&lt;cstdint&gt;, &lt;immintrin.h&gt;, &lt;intrin.h&gt; on MSVC) |
| **Minimum toolchain** | C++11 (&lt;cstdint&gt;); GCC or Clang with LZCNT enabled for the _lzcnt_u64 intrinsic in FastDivider (e.g. -mlzcnt or -march=haswell or later; the author's own test in issue #1 used -march=skylake); MSVC x64 for the C fallback. No build files, tests or benchmark in the repo. |
| **Platforms** | x86-64 only; CPU must support LZCNT and BMI2 (Intel Haswell or later, AMD Excavator/Zen or later); any x86-64 OS with GCC, Clang or MSVC |
| **Thread safety** | Not documented; the functions are pure and FastDivider is immutable after construction, so concurrent const use is safe by construction. |
| **Drop-in for the baseline** | partial: FastDivide/FastModulo/FastDivMod calls replace N / D and N % D for uint64_t only; no operator overloads, no signed or 32-bit versions, and division by zero is undefined instead of trapping |

## Gotchas

- FastDivider::GetDivisor() returns the stored member m_D, which the constructor sets to (uint64_t)-(int64_t)divisor, so FastDivider(7).GetDivisor() returns 2^64 - 7, not 7 (API bug in the current header; Divide/Modulo/DivMod are unaffected).
- No CPU feature check: on CPUs without LZCNT the lzcnt encoding executes as bsr and silently yields a different count, after which the GCC/Clang asm path faults on shlx (no BMI2) and the MSVC path, which uses ordinary shifts unless built for AVX2, would return untrustworthy quotients instead of crashing.
- The MSVC fallback computes E &gt;&gt;= C with C = 2^64 - lzcnt(D), a shift count of 64 or more that is undefined behavior in C++ and only works because x86 masks shift counts; the author's own comments call its codegen 'super dumb' (branches), so neither the speed nor the constant-time claim is assured on MSVC.
- FastDivider::Modulo returned wrong results until the 2021-02-17 fix (cmovc %[D] changed to cmovc %[N]); the standalone functions were unaffected. Issue #1's wrong results came from the reporter's own C refactor (1 &lt;&lt; t instead of 1ULL &lt;&lt; t), not the library.

## Known shortcomings

- README says only "about 30% faster" than hardware division on Intel, with no bench code, CPU or compiler; scalar, filed under math-simd-linear-algebra with libdivide and fastmod. Abandoned since 2021-09-30.
- A Python model of the asm path passed 660,231 quotient/remainder checks with 0 errors, so the algorithm is correct. Bugs: FastDivider::GetDivisor() returns the stored negated divisor (2^64 - 7 for 7); no LZCNT/BMI2 feature check; the MSVC path shifts by 2^64 - lzcnt (undefined behaviour). The 30% claim has no harness; DIV r64 costs about 14-18 cycles on Rocket Lake and Alder Lake and 9-17 on Zen 3 (search snippets) against about 12 serial multiplies here, so it is likely slower on those cores.

## Caveats and trade-offs

Only a prose claim ('About 30% faster', 'At least on Intel, where div is crazy slow'); the repo has no benchmark source, numbers, CPU model or compiler version, so results on cores with a faster 64-bit divider (newer Intel and AMD) may differ. The README itself warns that the routine uses more registers than a single div and that spilling can erase the gain, and that compile-time-constant divisors should be left to the compiler. Division or modulo by 0 is undefined (no trap). The only timing the author posted (issue #1) compares the library's C and inline-asm versions (0.310 vs 0.283, units and CPU unstated), not the hardware div. A divider-class bug was fixed on 2021-02-17 (commit 'fix issue in divider class (standalone funcs unaffected)'); the last commit is a README edit on 2021-09-30.

Scalar branchless algorithm (leading-zero count, shifts and five Newton-Raphson iterations, then a multiply-high), not SIMD, so it is a weak fit for this category; uses more registers than a single div, so spills can erase the win; undefined for division by zero; no side-channel leakage via branches or memory. For divisors known at compile time the compiler is better. Single header fast-divide.h.

## Maintenance

Abandoned since a 2021-09-30 README edit (last code change 2021-02-17); MIT-licensed, a single 13 KB header that is easy to vendor, but benchmark it on your own CPU first, since the 30% claim predates the fast 64-bit dividers in Ice Lake-era Intel and Zen 3 and may well be reversed there.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README states 'About 30% faster' than the hardware div instruction 'At least on Intel', but the repo holds only LICENSE, README.md and fast-divide.h: no benchmark code, no timing table, no CPU model and no compiler version. A first-party percentage without methodology is tier C (borderline D).
- **Verifier notes:** Real, MIT, 32 stars, 24 commits, abandoned since 2021-09-30; claim is a single unmeasured percentage with no harness, so it stays at C (could be argued D). Scalar integer division, not SIMD: libdivide and fastmod are filed under math-simd-linear-algebra, so the orchestrator may want a category override to sit next to them; no independent benchmark of this repo was found by search.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-77 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/komrad36/FastDivide>
  - <https://raw.githubusercontent.com/komrad36/FastDivide/HEAD/README.md>
  - <https://raw.githubusercontent.com/komrad36/FastDivide/HEAD/LICENSE>
  - <https://github.com/komrad36/FastDivide/commits>
  - <https://github.com/komrad36/FastDivide/issues?q=is%3Aissue>
  - <https://github.com/komrad36/FastDivide/issues/1>
- **Sources the enricher read:**
  - <https://github.com/komrad36/FastDivide>
  - <https://github.com/komrad36/FastDivide/commits>
  - <https://github.com/komrad36/FastDivide/commit/18fa261>
  - <https://github.com/komrad36/FastDivide/issues?q=is%3Aissue>
  - <https://github.com/komrad36/FastDivide/issues/1>
  - <https://raw.githubusercontent.com/komrad36/FastDivide/HEAD/README.md>
  - <https://raw.githubusercontent.com/komrad36/FastDivide/HEAD/fast-divide.h>
  - <https://raw.githubusercontent.com/komrad36/FastDivide/HEAD/LICENSE>
  - WebSearch snippets: https://www.postgresql.org/message-id/CAFBsxsHgygbSn0fc%3DLQgsQyjaR%3DEkGFJMJ4-sR-Styjgjbc3RA%40mail.gmail.com (Agner Fog Skylake 64-bit div 42-95 cycles), https://uops.info/html-instr/DIV_R64.html (snippet only; page blocked here), https://lists.puremagic.com/pipermail/digitalmars-d/2021-May/316025.html
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/komrad36/fastdivide`) · [data/wave13/enrich/raw/github_com_komrad36_fastdivide.json](../../../data/wave13/enrich/raw/github_com_komrad36_fastdivide.json) (enrichment confidence 0.8)

</details>
