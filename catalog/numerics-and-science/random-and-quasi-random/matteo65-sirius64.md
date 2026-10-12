# Sirius64

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `Apache-2.0` · 🟢 active

> Six-line 64-bit-state PRNG, a SplitMix64-style Weyl counter with a stronger output mix; \~1.25x faster than xoshiro256++.

| | |
|---|---|
| **Beats** | xoshiro256++, xoshiro256\*\*, PCG64 (RXS-M-XS and DXSM), xoroshiro128++, RomuTrio |
| **Claimed result** | 5.007 cycles per 64-bit value vs xoshiro256++ 6.331, xoshiro256\*\* 6.158, xoroshiro128++ 6.295, romutrio 5.842, pcg64 RXS-M-XS 6.870, pcg64 DXSM 8.623 (splitmix64 4.985); relative speed 99.6% of splitmix64 vs 78.7%/81.0%/72.6%/57.8% |
| **Workload** | 64-bit PRNG throughput relative to splitmix64 (README comparison table), also corroborated in lemire/testingRNG |
| **Metric** | throughput |
| **Hardware** | Intel Core Ultra 7 265H (16 CPUs), Ubuntu 24.04 under WSL2; independent run in lemire/testingRNG on a Xeon Gold 6548N |
| **Compiler and flags** | gcc 13.3.0 (Ubuntu 13.3.0-6ubuntu2\~24.04.1), -O3 -march=native -mtune=native (compile line in tools/benchmark.c) |
| **Adoption** | 2 stars |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/matteo65/Sirius64) · [benchmark](https://github.com/matteo65/Sirius64) |

## Verdict

With the author's benchmark.c (gcc 13.3, -O3 -march=native, 1e8 calls, best of 10) on a Core Ultra 7 265H under WSL2, Sirius64 took 5.007 cycles per 64-bit value vs xoshiro256++ 6.331, xoshiro256\*\* 6.158, RomuTrio 5.842 and PCG64 DXSM 8.623, essentially tied with SplitMix64 at 4.985. lemire/testingRNG independently measured 4.29 GB/s on a Xeon Gold 6548N with GCC 14, vs pcg64 2.53, wyrand 4.22 and splitmix64 4.35. That makes it a tie with wyrand and splitmix64, not a clear win.

## Use it when

- Scalar 64-bit random streams in simulations, games or procedural generation, where you want SplitMix64 speed but a generator that passes a 64-bit collision test
- Replacing xoshiro256++/\*\* or PCG64 in a hot loop that draws one value at a time (README: 5.0 vs 6.2-8.6 cycles per value)
- When 8 bytes of state per stream matters, e.g. one generator per object or per thread
- When you need a trivially portable generator: pure C99 with 64-bit multiply, no 128-bit arithmetic (unlike wyrand and PCG64)

## Skip it when

- Anything security-related: it is explicitly non-cryptographic
- When you need jump-ahead, provably independent parallel streams or a period above 2^64 (xoshiro256 offers 2^256 and jump functions)
- When you need a widely reviewed design: it was published in 2026, has 2 stars and a single author, and all its quality testing (PractRand to 64 TB, BigCrush x300, HWD to 15 PB) is self-reported
- When the output must be a bijection of the state: the output function is not one, so not every 64-bit value is guaranteed to appear in a period
- Bulk generation, where SIMD generators (SHISHUA, 8-way xoshiro256++) are several times faster

## How it is fast

The state update is one add of the golden-ratio constant 0x9e3779b97f4a7c15 (a Weyl sequence, as in SplitMix64). The output function is xorshift-17, a multiply, a 32-bit rotate, then a multiply of state ^ z ^ (z &gt;&gt; 17), all with the same constant. The state carries only an add dependency from call to call, and the multiplies are off that chain, so the cost is close to SplitMix64 (2.38 instructions/byte in testingRNG vs 2.75 for splitmix64).

## Compared with alternatives

Pick it over Romu/RomuTrio or xoshiro256++ when you want the smallest state and the fastest scalar draw with no 128-bit multiply. Prefer testingRNG's wyrand or lehmer64 for similar speed and a longer public track record, and SHISHUA or the 8-way xoshiro256++ gist for bulk SIMD throughput.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none |
| **Minimum toolchain** | C99 (needs uint64_t); the benchmark tool needs GCC/Clang with x86intrin.h |
| **Platforms** | any platform with 64-bit integer multiply; benchmarked only on x86-64 |
| **Thread safety** | Reentrant: all state is in the caller-supplied uint64_t. Use one state per thread. |
| **Drop-in for the baseline** | partial: one function on a uint64_t, but you must write your own wrapper to replace a C++ &lt;random&gt; engine or the xoshiro API (no jump()) |

## Gotchas

- The README's 'Collision 64: Yes' column means the generator passes a 64-bit collision test: it produces about as many repeated outputs as a random function (6.8 observed vs 6.94 expected per 16e9 values). SplitMix64 is marked 'No' because its output is a bijection and never repeats within a period. In testingRNG issue 30 a SmokeRand author points out that 64-bit bijectivity is not proven.
- Its benchmark calls each generator through a function pointer, XORs into a volatile sink and counts rdtscp TSC ticks, not core cycles. Call overhead is included, which compresses the gaps between generators, and the author says rankings changed on other machines.
- Seeds of 0 and UINT64_MAX are documented as fine; with a Weyl counter, nearby seeds give overlapping, shifted streams.
- The README's 'pgc64' labels mean PCG64.

## Known shortcomings

- 2 stars; statistical quality self-reported; timed under WSL2; only \~1.25x faster than xoshiro256++.
- 5.0 vs 6.3 cycles/value vs xoshiro256++; ties wyrand and splitmix64 in testingRNG (4.29 vs 4.22/4.35 GB/s); benchmark via function pointer counting rdtscp ticks; testingRNG issue 30: output function not proven a bijection; design weeks old.

## Caveats and trade-offs

Very new single-author design; its statistical quality (PractRand, TestU01, SmokeRand) is self-reported. Timed with rdtscp under WSL2; the author notes rankings changed on other machines. lemire/testingRNG independently lists sirius64 at 4.29 vs pcg64 2.53 and mersennetwister 1.68 (GCC 14, Xeon Gold 6548N). It is only about 1.25x faster than xoshiro256++ and ties splitmix64.

64-bit state, 64-bit output; period and jump/stream support are not those of xoshiro.

## Maintenance

Actively developed (last commit 2026-09-29) under Apache-2.0. The algorithm is six lines and easy to vendor, but the design is weeks old and has had no third-party cryptanalysis-style review.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C to A. The README Benchmark section gives cycles per 64-bit value (Sirius64 5.007 vs xoshiro256++ 6.331, xoshiro256\*\* 6.158, pcg64 DXSM 8.623, RXS-M-XS 6.870, romutrio 5.842) on an Intel Core Ultra 7 265H with gcc 13.3.0. The benchmark code tools/benchmark.c is public and states its compile line (-O3 -march=native -mtune=native). lemire/testingRNG independently corroborates the result: sirius64 at 4.29 vs pcg64 at 2.53 and mersennetwister at 1.68 on a Xeon Gold 6548N with GCC 14.
- **Verifier notes:** The tier was upgraded because the benchmark source, compiler, flags and CPU model are all public. The baselines are other PRNGs, not std::mt19937 directly. It has 2 stars and its last commit was on 2026-09-29.
- **Fields the verifier corrected:** `hardware`, `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** lemire/testingRNG independently: 4.29 vs pcg64 2.53 on Xeon Gold 6548N
- **Pages the verifier opened:**
  - <https://github.com/matteo65/Sirius64>
  - <https://raw.githubusercontent.com/matteo65/Sirius64/HEAD/README.md>
  - <https://raw.githubusercontent.com/matteo65/Sirius64/main/tools/benchmark.c>
  - <https://raw.githubusercontent.com/matteo65/Sirius64/main/LICENSE>
  - <https://github.com/matteo65/Sirius64/commits>
  - <https://raw.githubusercontent.com/lemire/testingRNG/master/README.md>
- **Sources the enricher read:**
  - <https://github.com/matteo65/Sirius64>
  - <https://raw.githubusercontent.com/matteo65/Sirius64/HEAD/README.md>
  - <https://raw.githubusercontent.com/matteo65/Sirius64/HEAD/tools/benchmark.c>
  - <https://raw.githubusercontent.com/lemire/testingRNG/master/README.md>
  - <https://github.com/lemire/testingRNG/issues/30>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/matteo65/sirius64`) · [data/wave8/enrich/raw/github_com_matteo65_sirius64.json](../../../data/wave8/enrich/raw/github_com_matteo65_sirius64.json) (enrichment confidence 0.8)

</details>
