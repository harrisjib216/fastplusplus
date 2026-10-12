# shioi128 (Shioi PRNG)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `CC0-1.0` · 🔴 abandoned

> Public-domain 16-byte-state 64-bit PRNG with O(1) 2^64 jump; about 3x reference mt19937-64, parity with xoshiro256\*\*.

| | |
|---|---|
| **Beats** | Reference mt19937-64.c (Matsumoto-Nishimura C code; same algorithm as std::mt19937_64, but std::mt19937_64 itself was not timed), pcg64_xsh_rr and xoshiro256\*\* |
| **Claimed result** | shioi128 1.00 64-bit/ns vs xoshiro256\*\* 0.99, pcg64_xsh_rr 0.38, mt19937_64 0.32 (about parity with xoshiro256\*\*, 2.6x PCG64, derived from page data). README: 'About 3.1 times faster than Mersenne Twister (64 bit version)'. |
| **Workload** | Speed of 64-bit outputs per nanosecond measured with the xoshiro/xoroshiro harness.c, same ten-generator table as seiran. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-7700HQ @ 2.80GHz |
| **Compiler and flags** | gcc 7.3.0; flags not stated. |
| **Adoption** | 4 stars |
| **Last commit** | 2019-08-18 |
| **Links** | [repository](https://github.com/andanteyk/prng-shioi) · [benchmark](https://github.com/andanteyk/prng-shioi) |

## Verdict

Author-run xoshiro harness.c on an i7-7700HQ with gcc 7.3.0 (flags not stated): shioi128 1.00 64-bit outputs/ns vs the reference mt19937-64.c at 0.32 (3.1x), pcg64_xsh_rr 0.38 and xoshiro256\*\* 0.99; std::mt19937_64 itself was not timed. An independent casual C++ benchmark (t-mat gist, last updated 2022-11-24, -std=c++20 -O3, CPU not stated) measured Shioi128 at 10.15 GiB/s with GCC 11.2 vs xoroshiro128+ 8.02 and wyrand 8.85, and 10.86 GiB/s with MSVC 19.32 vs xoroshiro128+ 6.75 and wyrand 12.81.

## Use it when

- Games, simulations and Monte Carlo code on 64-bit CPUs that need a small non-cryptographic 64-bit generator faster than std::mt19937_64 and can vendor \~20 lines of CC0 code.
- Parallel or per-task streams: jump64() costs about one next() and splits the period into 2^64 non-overlapping subsequences of length 2^64.
- Many independent generator instances (per particle, per entity), where 16 bytes of state beats mt19937_64's \~2.5 KB.
- When you want a fast 128-bit-state generator that, per the author, passes PractRand to 32 TB, BigCrush (normal and bit-reversed), the Hamming-weight-dependency test to 1.5 PB and gjrand. In the same table xoroshiro128+ fails BRank and hwd.

## Skip it when

- Anything security-relevant (tokens, keys, adversarial inputs). It is not a CSPRNG, and the only attack the author reports is one day of Z3 that did not recover the state.
- When raw speed is the goal: in the author's own C table it is behind sfc64 (1.21), seiran128 (1.20) and xoroshiro128+ (1.13) and only ties xoshiro256\*\* (1.00 vs 0.99 outputs/ns).
- 32-bit targets or cores without a fast 64x64-bit multiply: the README warns that speed may drop there, and the 32-bit-word variants are unfinished.
- When you need a widely analysed or standardized generator: the author says it 'has not been investigated by others', and no paper or third-party statistical analysis is linked.
- When you need a maintained, packaged library: there are four commits (the last on 2019-08-18) and no tests beyond the self-test main() in the source file.

## How it is fast

Each step is one 64-bit constant multiply (by 0xD2B74407B1CE6E93), a rotate-left by 29 and an add for the output, plus a shift/xor update of the state (s1' = (s0 &lt;&lt; 2) ^ (s0 &gt;&gt; 19, arithmetic) ^ s1). That is a two-word linear recurrence over GF(2) (the README calls it LFSR-based) with a multiply-rotate-add output scrambler, so everything stays in two registers. mt19937-64 instead keeps about 2.5 KB of state that it regenerates in blocks. Because the recurrence is linear, a 2^64-step jump reduces to a closed-form two-word update costing about one next().

## Compared with alternatives

Over seiran128 (same author, 1.20 vs 1.00 outputs/ns in the shared C table), pick shioi128 for the O(1) jump64. In the author's later Culumi table, Seiran's state is rated 'easy(Z3)' to predict and Shioi's 'unknown', and Shioi was faster there (81.97 vs 97.26 ns/KiB under .NET 8). Over xoshiro256\*\*, it gives half the state and a constant-time 2^64 jump at equal measured speed; pick Culumi (needs SSE4/PCLMUL) or a SIMD generator such as simdrng or SHISHUA when bulk fill throughput matters more.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (&lt;inttypes.h&gt;; &lt;stdio.h&gt; only for the bundled self-test main) |
| **Minimum toolchain** | C99 (for-loop declarations, &lt;inttypes.h&gt;); needs a compiler whose &gt;&gt; on a negative int64_t is an arithmetic shift, which is guaranteed only from C23 / C++20 and implementation-defined before that |
| **Platforms** | any target with 64-bit integers; benchmarked only on x86-64 (i7-7700HQ); slower where 64-bit multiply is slow |
| **Thread safety** | Not thread-safe as shipped: next()/init()/jump\*() share one file-static state[2]. Give each thread its own state (the README's minimal version takes state[2] as a parameter). |
| **Drop-in for the baseline** | partial — not a std::UniformRandomBitGenerator; needs a small wrapper class to replace std::mt19937_64 under std:: distributions, and the output sequence differs from MT |

## Gotchas

- shioi128.c defines bare global symbols next(), init(), jump32/64/96() and a main() self-test in the same file. Strip main and rename or namespace the functions before linking into a real program.
- The update must use an arithmetic (sign-extending) right shift of (int64_t)s0 (the source says 'MUST use arithmetic right shift'). A port that uses a logical shift, such as Java's &gt;&gt;&gt; or an unsigned &gt;&gt; in Rust or C#, silently produces a different, untested generator.
- State {0,0} is a fixed point. The shipped init() seeds both words through a 64-bit LCG, which never yields {0,0}, but custom seeding must avoid two zero words.
- Only jump64() is O(1). jump32() and jump96() run the generic polynomial jump, which is 128 next() calls plus XORs.

## Known shortcomings

- About parity with xoshiro256\*\* (1.00 vs 0.99), not a clear win; needs arithmetic right shift of negative int64_t (implementation-defined before C23/C++20).
- shioi128.c has file-static state, bare next()/init() and a main() self-test in the same file. Only jump64 is O(1); jump32/jump96 cost 128 next() calls. Independent t-mat gist (GCC 11.2 / MSVC 19.32, -O3, CPU not stated): Shioi128 10.15 GiB/s vs xoroshiro128+ 8.02 and wyrand 8.85.

## Caveats and trade-offs

Roughly equal to xoshiro256\*\* in speed (1.00 vs 0.99) and slower than seiran128, xoroshiro128+ and sfc64 in the same table, so it only beats PCG64 and the Mersenne Twisters. First-party numbers, flags unstated, one laptop CPU; std::mt19937_64 was not timed. The author says it needs a fast 64-bit multiply and that it has not been investigated by others. It relies on arithmetic right shift of a negative int64_t (the README says 'MUST use arithmetic right shift'), which is implementation-defined in C before C23 and in C++ before C++20. It uses a global static state with bare next()/init() symbols. CC0 dedication gives no patent grant. Four commits, the last on 2019-08-18. It is a sibling of seiran128 (same author, same table).

16 bytes of state, period 2^128-1; needs a 64-bit constant multiply (slow on some targets); constant-time jump of 2^64 steps costs about one next(); 32-bit variants incomplete; not cryptographic (Z3 attack failed in a day per README).

## Maintenance

Abandoned since 2019-08-18 (four commits, no issues), but CC0 and about 20 lines of logic, so vendoring and maintaining a wrapper yourself is trivial.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Comparison table (the same author-run xoshiro harness.c table as seiran, gcc 7.3.0, i7-7700HQ) gives shioi128 1.00 vs xoshiro256\*\* 0.99, pcg64_xsh_rr 0.38 and mt19937_64 0.32 64-bit values/ns. Flags are not stated and no benchmark code is in the repo, so this is first-party evidence short of A.
- **Verifier notes:** README numbers and metadata match the record (CC0, 4 stars, 0 forks, 4 commits, last commit 2019-08-18). 'About 3.1 times faster than Mersenne Twister' matches 1.00/0.32. The Python re-implementation of next() reproduces the self-test vectors in shioi128.c. The xoshiro harness.c host is egress-blocked here.
- **Fields the verifier corrected:** `baseline`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/andanteyk/prng-shioi>
  - <https://github.com/andanteyk/prng-shioi/commits>
  - <https://raw.githubusercontent.com/andanteyk/prng-shioi/HEAD/README.md>
  - <https://raw.githubusercontent.com/andanteyk/prng-shioi/HEAD/shioi128.c>
- **Sources the enricher read:**
  - <https://github.com/andanteyk/prng-shioi>
  - <https://github.com/andanteyk/prng-shioi/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/andanteyk/prng-shioi/HEAD/README.md>
  - <https://raw.githubusercontent.com/andanteyk/prng-shioi/HEAD/README-ja.md>
  - <https://raw.githubusercontent.com/andanteyk/prng-shioi/HEAD/shioi128.c>
  - <https://raw.githubusercontent.com/andanteyk/prng-culumi/HEAD/README.md>
  - <https://gist.github.com/t-mat/ff347c3ea6b94f3c60150631edeb07d3>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/andanteyk/prng-shioi`) · [data/wave8/enrich/raw/github_com_andanteyk_prng_shioi.json](../../../data/wave8/enrich/raw/github_com_andanteyk_prng_shioi.json) (enrichment confidence 0.75)

</details>
