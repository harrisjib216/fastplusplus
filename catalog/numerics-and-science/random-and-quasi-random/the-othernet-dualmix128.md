# DualMix128 (128-bit-state PRNG; superseded by LoopMix128)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟡 stale

> Tiny 128-bit-state add-rotate PRNG; author's gcc benchmark: 0.401 ns/call vs xoroshiro128++ 0.829, tied with wyrand.

| | |
|---|---|
| **Beats** | xoroshiro128++ (also wyrand, Java xoroshiro128++ and java.util.Random) |
| **Claimed result** | benchmark.out: DualMix128 0.401 ns/call versus xoroshiro128++ 0.829 ns/call (about 2.07x, derived from page data) and wyrand 0.401 ns/call (parity). README: '107% faster than C xoroshiro128++, 27% faster than Java xoroshiro128++, 8.82x Java random'. |
| **Workload** | ns per call of the generator in a 10-billion-iteration loop, built with gcc and run by benchmark.c. |
| **Metric** | latency |
| **Compiler and flags** | gcc 11.4.0 (Ubuntu 22.04): gcc -o benchmark benchmark.c -O3 -march=native |
| **Adoption** | 4 stars |
| **Last commit** | 2025-05-10 |
| **Links** | [repository](https://github.com/the-othernet/DualMix128) · [benchmark](https://raw.githubusercontent.com/the-othernet/DualMix128/HEAD/benchmark.out) |

## Verdict

benchmark.out (gcc 11.4.0 on Ubuntu 22.04, -O3 -march=native, CPU not stated) times 10^10 single-stream calls each storing to a volatile: DualMix128 0.401 ns/call, xoroshiro128++ 0.829 ns (about 2.07x, derived from page data), wyrand 0.401 ns. The xoroshiro128++ in benchmark.c is the standard algorithm, so the gap mostly reflects xoroshiro's longer dependency chain.

## Use it when

- Hot scalar loops (Monte Carlo, procedural generation, randomized testing) where a single 64-bit draw per call must be as cheap as possible and PractRand/BigCrush-level quality is enough.
- When a 16-byte, multiply-free state update is wanted, e.g. one generator embedded per object or per thread.
- As a reference for the design line that continued in LoopMix128 and biski64.

## Skip it when

- When you need a guaranteed period: injectivity is unproven (the README strikes its 'possibly injective' claim), so the period and the risk of short cycles are unknown; the author points to LoopMix128 instead.
- Parallel simulations that need non-overlapping streams: there is no jump or stream function.
- Anything security-sensitive: the README says it is for non-cryptographic use.
- When wyrand is already available: the author's own benchmark has wyrand at the same 0.401 ns/call.
- When you want a maintained, packaged library: 23 commits, 4 stars, no header or API, and the LoopMix128 link now redirects to the biski64 repository.

## How it is fast

Each step is one add (mix = s0 + s1), two rotates and two adds for the new state, and one multiply of mix by the golden-ratio constant for the output. The loop-carried dependency is only about two adds deep and the multiply sits off the critical path, while xoroshiro128++'s update chains xor, rotate, shift and xor. The state update is a nonlinear add-rotate mix with a multiplicative output scrambler, so no linear-algebra structure and no jump function.

## Compared with alternatives

Rarely: wyrand ties it in its own benchmark with 8 bytes of state and a Weyl-sequence period of 2^64, biski64 (already catalogued; the LoopMix128 link now lands there) is the author's later design with a guaranteed minimum period, and Sirius64, Romu or the xoshiro family are better analysed. Choose DualMix128 only if you specifically want its multiply-free 16-byte state update and accept an unknown period.

## Integration

| | |
|---|---|
| **Form** | source-drop (copy the function from the README or benchmark.c) |
| **Dependencies** | none |
| **Minimum toolchain** | C99 (stdint.h); the published benchmark was built with gcc 11.4.0 -O3 -march=native |
| **Platforms** | any platform with 64-bit integers (portable C, no intrinsics; the benchmark harness uses POSIX clock_gettime) |
| **Thread safety** | not documented; the reference code keeps state in global variables, so move it into a per-thread struct |
| **Drop-in for the baseline** | partial — same 128-bit state and 64-bit output as xoroshiro128++, but a different sequence and no jump()/long_jump() |

## Gotchas

- The all-zero state is a fixed point (mix = 0 keeps both words 0 and the output stays 0 forever); benchmark.c's seed function does not check for it, so seed through SplitMix64 as test_practrand.c does.
- The reference code uses global state and non-static 'inline' functions, which under C99 inline rules can fail to link at -O0; wrap it as a static inline function over a state struct.
- The timing is single-stream latency with a volatile store per call, and the CPU is not stated; DualMix128 and wyrand land on the identical 0.401 ns, which suggests a loop or store floor rather than a measured difference between them.
- The README's Java claims (27% faster than Java xoroshiro128++, 8.82x java.util.Random) have no Java code or output in the repo.

## Known shortcomings

- No CPU stated; the 0.401 ns tie with wyrand suggests a loop floor rather than generator cost; no period proof; superseded by LoopMix128.
- All-zero state is a fixed point and the seed function does not check for it. Period unproven. Speed ties wyrand (both 0.401 ns, suggesting a loop/store floor). Repo has no Java code (language corrected to C).

## Caveats and trade-offs

First-party. benchmark.c and its output give the gcc version and flags but no CPU model. The xoroshiro128++ in benchmark.c is the standard algorithm. DualMix128 and wyrand both land on exactly 0.401 ns/call with a volatile store per call, which suggests a loop or store floor, so the 2.07x over xoroshiro128++ mainly reflects xoroshiro's longer dependency chain. The update is nonlinear with no proven period; the README strikes through its 'possibly injective' claim, and the repo says it was replaced by LoopMix128 for proven injectivity and a guaranteed 2^128 period. The LoopMix128 URL (danielcota/LoopMix128) now serves the biski64 repository, and biski64 is already catalogued. DualMix128 is a different algorithm, not a copy. Statistical claims (README): PractRand from 256MB to 8TB (32TB in the feature list) with zero anomalies, and BigCrush passed. Speed ties wyrand.

Two 64-bit state words; period not guaranteed (README replaced the injectivity claim and points users to LoopMix128, which has a guaranteed 2^128 period); not cryptographic.

## Maintenance

Stale (last commit 2025-05-10) and superseded by its author, but MIT-licensed and five lines long, so copying is trivial; prefer the successor if you need a period guarantee.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** benchmark.out shows DualMix128 0.401 ns/call against a correct xoroshiro128++ (0.829 ns) and wyrand (0.401 ns), from the public benchmark.c built with gcc 11.4.0 -O3 -march=native. No CPU model is stated anywhere, so it falls short of A and stays first-party C.
- **Verifier notes:** Numbers and flags match benchmark.out and the README. last_commit 2025-05-10 ('Update README.md') confirmed, so stale is right. Kept rather than filed as a duplicate, because the algorithm differs from biski64.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/the-othernet/DualMix128/HEAD/benchmark.out>
  - <https://raw.githubusercontent.com/the-othernet/DualMix128/HEAD/benchmark.c>
  - <https://raw.githubusercontent.com/the-othernet/DualMix128/HEAD/README.md>
  - <https://raw.githubusercontent.com/the-othernet/DualMix128/HEAD/LICENSE>
  - <https://github.com/the-othernet/DualMix128>
  - <https://github.com/the-othernet/DualMix128/commits/main>
  - <https://github.com/danielcota/LoopMix128>
- **Sources the enricher read:**
  - <https://github.com/the-othernet/DualMix128>
  - <https://raw.githubusercontent.com/the-othernet/DualMix128/HEAD/README.md>
  - <https://raw.githubusercontent.com/the-othernet/DualMix128/HEAD/benchmark.c>
  - <https://raw.githubusercontent.com/the-othernet/DualMix128/HEAD/benchmark.out>
  - <https://raw.githubusercontent.com/the-othernet/DualMix128/HEAD/test_practrand.c>
  - <https://raw.githubusercontent.com/the-othernet/DualMix128/HEAD/LICENSE>
  - <https://github.com/danielcota/LoopMix128>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/the-othernet/dualmix128`) · [data/wave8/enrich/raw/github_com_the_othernet_dualmix128.json](../../../data/wave8/enrich/raw/github_com_the_othernet_dualmix128.json) (enrichment confidence 0.75)

</details>
