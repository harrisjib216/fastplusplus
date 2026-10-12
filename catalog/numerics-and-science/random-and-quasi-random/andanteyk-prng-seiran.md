# seiran (seiran128 PRNG)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `CC0-1.0` · 🔴 abandoned

> Tiny CC0 128-bit-state LFSR PRNG in C with jump functions; author measured 3.75x reference mt19937-64.c throughput.

| | |
|---|---|
| **Beats** | Reference mt19937-64.c (Matsumoto-Nishimura C code; same algorithm as std::mt19937_64, but std::mt19937_64 itself was not timed), pcg64_xsh_rr and xoshiro256\*\* |
| **Claimed result** | README table (64-bit values/ns): seiran128 1.20 vs sfc64 1.21, xoroshiro128+ 1.13, xoshiro256\*\* 0.99, pcg64_xsh_rr 0.38, mt19937_64 0.32. README says 'About 3.7 times faster than Mersenne Twister(64-bit version)'. That is 1.20/0.32 = 3.75x, and 3.2x over pcg64_xsh_rr (both derived from page data). |
| **Workload** | 64-bit values generated per ns using the xoshiro/xoroshiro speed harness (harness.c), compared against ten other 64-bit generators. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-7700HQ @ 2.80 GHz |
| **Compiler and flags** | gcc 7.3.0 (flags not stated; xoshiro harness.c) |
| **Adoption** | 5 stars |
| **Last commit** | 2021-01-30 |
| **Links** | [repository](https://github.com/andanteyk/prng-seiran) · [benchmark](https://github.com/andanteyk/prng-seiran) |

## Verdict

The author ran Vigna's xoshiro harness.c with gcc 7.3.0 (flags not stated) on an Intel Core i7-7700HQ at 2.80 GHz: seiran128 produced 1.20 64-bit values/ns versus 0.32 for the reference mt19937-64.c (3.75x, derived from page data), 0.38 for pcg64_xsh_rr, 0.99 for xoshiro256\*\* and 1.21 for sfc64; std::mt19937_64 itself was not timed.

## Use it when

- Games and simulations that want 64-bit outputs from a 16-byte state with no 128-bit multiply or SIMD (portable to any 64-bit integer target; C# and Motoko ports exist)
- Replacing mt19937_64 in single-threaded C or C++ code where the exact Mersenne Twister sequence does not matter
- Parallel or partitioned simulations that need jump-ahead: jump64() gives 2^64 disjoint streams of 2^64 values each
- Projects that need public-domain (CC0) code to paste without attribution

## Skip it when

- Anything security-relevant: the author recovered the full state from three consecutive outputs with the Z3 solver in minutes
- When you want a generator with outside scrutiny: all PractRand, BigCrush, gjrand and hwd results are the author's, and the README says it has not been investigated by others; xoroshiro128++/xoshiro256\*\* or PCG64DXSM have far more analysis
- When raw speed is the only criterion: it ties sfc64 (1.20 vs 1.21 values/ns) in its own table, and in the same author's later .NET 8 table (Culumi README) Seiran at 97.26 ns/KiB trails Shioi (81.97) and SplitMix (91.80) and ties SFC64 (97.80); SIMD generators such as SHISHUA or 8-way xoshiro are much faster for bulk fills
- When you need a 32-bit-word variant, float/double helpers or a std::uniform_random_bit_generator class: none are provided
- Long-lived dependencies: last commit 2021-01-30 (5 commits), and CC0 gives no patent grant

## How it is fast

The state update is an xorshift/rotate linear (F2) transform in the xoroshiro style (s0 ^ rotl(s1, 29) and s0 ^ (s1 &lt;&lt; 9)), and the output scrambler is one add, one multiply by 9, one rotate and one add: rotl((s0 + s1) \* 9, 29) + s0. With 16 bytes of state, no 128-bit multiply and no table, each value costs a handful of ALU ops, against MT19937-64's 2,500-byte state (README table).

## Compared with alternatives

Against Shioi (same author, same 16-byte state) and Culumi (same author, faster but needs SSE4/PCLMUL), pick seiran when you want the plainest portable scalar code with a jump function; SFC64 has no jump function (Stream column '-' in the Culumi table), and xoroshiro128++/xoshiro256\*\* are the better-vetted alternatives at similar speed.

## Integration

| | |
|---|---|
| **Form** | source-drop (single C file) |
| **Dependencies** | none (inttypes.h only) |
| **Minimum toolchain** | C99 (static inline, loop-scoped declarations, inttypes.h); timing used gcc 7.3.0 |
| **Platforms** | any with 64-bit unsigned integers; no architecture-specific instructions |
| **Thread safety** | seiran128.c keeps one static global state, so it is not thread-safe; the README's next(uint64_t state[2]) form is reentrant with per-thread state |
| **Drop-in for the baseline** | partial — replaces mt19937_64 as a source of 64-bit values, but needs a small wrapper (result_type, min, max, operator()) to work with &lt;random&gt; distributions, and produces a different sequence |

## Gotchas

- seiran128.c has a test main() and assertion macros below the generator and exports bare next, init, jump32, jump64 and jump96 symbols; strip the test code and rename or make them static before linking into a project
- The all-zero state {0, 0} is forbidden; init() cannot produce it, but custom seeding must avoid it
- Each jump runs 128 calls of next() (polynomial jump), so it is cheap but not free, and it overwrites the global state
- The speed table's harness (Vigna's harness.c) is not in the repo and its flags are not stated; splitmix at 0.68 values/ns, slower than seiran128 there, is unusual and suggests results are harness-specific

## Known shortcomings

- Baseline is the reference mt19937-64.c, not std::mt19937_64; flags unstated (self-test vectors reproduced).
- Speed lead depends on the harness: the same author's later .NET table (Culumi README) puts Seiran at 97.26 ns/KiB, behind Shioi (81.97) and SplitMix (91.80) and level with SFC64 (97.80). seiran128.c includes a test main().

## Caveats and trade-offs

First-party measurement with compiler flags unstated. The speed edge over xoshiro256\*\* is only about 1.2x and seiran128 ties sfc64 (1.21), so the clear wins are over the reference MT19937-64 C code and PCG64 only; std::mt19937_64 was not timed. The author says that, being new, it has not been investigated by others. The PractRand 32 TB, BigCrush, gjrand and hwd results are the author's own. Not cryptographic: the author recovered the full state from 3 consecutive outputs with Z3 in a few minutes. seiran128.c uses a global static state and exports bare next()/init() symbols, so it must be wrapped before use as a library. CC0 dedication gives no patent grant. The last commit (2021) only added a C# port.

Two-word (128-bit) LFSR state with an add/rotate/multiply output scrambler, period 2^128-1, jump of 2^64; no 32-bit variant; not cryptographically secure (the author recovered state from three outputs with Z3). Portable, no 128-bit multiply. CC0 dedication, so no patent grant.

## Maintenance

Abandoned since January 2021 (the last commit only added a C# port link), but CC0 and a single 131-line C file including its self-test, so trivial to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Comparison table (author's own run with Vigna's xoshiro harness.c, gcc 7.3.0, i7-7700HQ) lists seiran128 1.20, xoshiro256\*\* 0.99, pcg64_xsh_rr 0.38 and mt19937_64 0.32 64-bit values/ns. Compiler flags are not stated and the harness is not in the repo, so this is first-party evidence short of A.
- **Verifier notes:** README numbers and repo metadata match the record (CC0, 5 stars, 1 fork, 5 commits, last commit 2021-01-30, not a fork, not archived). The Python re-implementation of next() reproduces the self-test vectors in seiran128.c for init(401). xoshiro harness.c (prng.di.unimi.it) is egress-blocked here, so its flags could not be checked. The only third-party use found is a Motoko port (research-ag/prng, 2 stars) that counts Wasm instructions and makes no MT comparison.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/andanteyk/prng-seiran>
  - <https://github.com/andanteyk/prng-seiran/commits>
  - <https://raw.githubusercontent.com/andanteyk/prng-seiran/HEAD/README.md>
  - <https://raw.githubusercontent.com/andanteyk/prng-seiran/HEAD/seiran128.c>
  - <https://github.com/research-ag/prng>
- **Sources the enricher read:**
  - <https://github.com/andanteyk/prng-seiran>
  - <https://raw.githubusercontent.com/andanteyk/prng-seiran/HEAD/README.md>
  - <https://raw.githubusercontent.com/andanteyk/prng-seiran/HEAD/README-ja.md>
  - <https://raw.githubusercontent.com/andanteyk/prng-seiran/HEAD/seiran128.c>
  - <https://raw.githubusercontent.com/andanteyk/prng-culumi/HEAD/README.md>
  - <https://github.com/Almightygir/rhet_RNG>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/andanteyk/prng-seiran`) · [data/wave8/enrich/raw/github_com_andanteyk_prng_seiran.json](../../../data/wave8/enrich/raw/github_com_andanteyk_prng_seiran.json) (enrichment confidence 0.8)

</details>
