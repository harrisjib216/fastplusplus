# Romu (RomuTrio/RomuQuad/RomuMono)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C` · `no license` · ⚪ unknown

> Romu: tiny nonlinear multiply-rotate 64/32-bit PRNGs with zero output latency, claimed 3 cycles/value vs xoshiro256++ and PCG.

| | |
|---|---|
| **Beats** | xoshiro256++, PCG (pcg-xsh-rs) |
| **Claimed result** | Paper tables: RomuTrio/RomuQuad/RomuDuo 3 cycles, 0 output latency vs xoshiro256++ 3 cycles, 3-cycle latency and pcg-xsh-rs 9 cycles, 7 latency; RomuQuad32 and RomuTrio32 3 cycles, 0 latency vs xoshiro128\*\* 5 cycles, 5 latency; RomuMono32 4 cycles, 1 latency vs pcg-xsh-rr 4 cycles, 4 latency. The text says RomuMono32 matches pcg-xsh-rr quality with 3 arithmetic ops vs 7 |
| **Workload** | Cycle counts and output latency of 64-bit and 32-bit generator cores |
| **Metric** | latency |
| **Hardware** | Intel Xeon E5-2643 v3 (3.4-3.7 GHz) |
| **Compiler and flags** | g++ 4.8.4 -S -O3 (assembly analysis only) |
| **Links** | [benchmark](https://arxiv.org/pdf/2002.11331) |

## Verdict

The author's arXiv preprint counts cycles and output latency from g++ 4.8.4 -O3 assembly for an Intel Xeon E5-2643 v3: RomuTrio/RomuQuad/RomuDuo at 3 cycles with 0 latency vs xoshiro256++ at 3 cycles with 3 latency and 128-bit PCG at 9 cycles with 7 latency. The only wall-clock table times combinations of RomuMono32 (about 4.6 cycles/value) and no baselines, so no measured speedup over xoshiro or PCG is shown.

## Use it when

- Hot inner loops (Monte Carlo, games, procedural generation, randomized algorithms) where the PRNG call is inlined and its latency or register use shows up in the profile.
- Many independent parallel streams from random seeds: the paper estimates about 16,000 RomuTrio streams of 2^53 values each with negligible overlap risk.
- 32-bit or small cores where RomuTrio32/RomuQuad32 replace xoshiro128\*\* (3 cycles and 0 latency vs 5 and 5 by the paper's assembly analysis).
- Situations where you just need a few lines of copyable C with no dependency, provided the license question is settled for your project.

## Skip it when

- Anything security-related: the generators are invertible and the paper says they are not cryptographically secure.
- When you need jump-ahead/substreams with guaranteed non-overlap or a proven minimum period: Romu has no jump function, and periods are only probabilistic; an HN critic reported 32-bit-variant cycles shorter than the paper's bounds and disputes that the proof applies to a fixed permutation.
- Huge single jobs on the small variants: estimated capacity is 2^51 bytes for RomuDuoJr and 2^26 bytes for RomuMono32 (not for parallel streams).
- When you need a measured, reproducible speedup: the comparison to xoshiro256++/PCG is assembly-derived cycle counts, not timed against those baselines.
- Projects that need a clear license from the original source (see status note).

## How it is fast

Each step is one multiply by a constant plus one or two rotates and an add/subtract on separate state words, and the output is a state word read before the update, so output latency is 0 cycles and the multiply overlaps with the consumer's work (instruction-level parallelism). Register pressure is 4-6 registers when inlined, against 7-8 for xoshiro256++ and 10 for 128-bit PCG.

## Compared with alternatives

Pick Romu over SIMDxorshift or Squares when you want the cheapest scalar inlined 64-bit generator with low register pressure rather than a vectorized or counter-based one; pick Squares or Randen when you need counter-based reproducible substreams or backtracking resistance, and Randompack when you need distributions and a maintained library.

## Integration

| | |
|---|---|
| **Form** | source-drop (code printed in the paper; served at romu-random.org/code.c) |
| **Dependencies** | none |
| **Minimum toolchain** | any C/C++ compiler with uint64_t/uint32_t; a rotate macro that the compiler turns into one instruction (gcc and Visual Studio do, per the paper) |
| **Platforms** | any; best on CPUs with a pipelined 64-bit multiplier (paper analysis targets Intel with 3-cycle multiply latency) |
| **Thread safety** | Reference code uses global state variables, so not thread-safe as printed; give each thread its own state |
| **Drop-in for the baseline** | partial — same role as a xoshiro/PCG next() function, but you must write the seeding and any std::uniform_random_bit_generator wrapper yourself, and output sequences differ |

## Gotchas

- The state must not be all zeros; any nonzero seed works, and RomuMono32 needs its own init that maps the seed into a valid range.
- Not equidistributed and with no guaranteed minimum period; each seed lands on a cycle of unknown length.
- Only RomuTrio/RomuQuad are recommended for large or parallel jobs; RomuDuoJr trades capacity for speed.
- The reference code keeps state in globals; wrap it in a struct before using it in libraries or threads.

## Known shortcomings

- Speed figures are cycle counts read from assembly, not timings against baselines; no license or official repo; romu-random.org has an expired certificate.
- No jump-ahead; period only probabilistic; HN critic (item 22447848) reports cycles in the 32-bit variant shorter than the paper's bounds; license unconfirmed (HN says Apache-2.0, site cert expired).

## Caveats and trade-offs

Cycle and latency figures come from assembly analysis, not measured throughput against baselines; the paper's only timing table (5e9 calls, Xeon E5-2643 v3) covers just RomuMono32 combos; author-run preprint; source code is printed in the paper and served at romu-random.org/code.c (site TLS certificate expired, not opened); no license statement found; no official repo (Rust, .NET and R ports exist)

Nonlinear; short minimum cycle length guarantees weaker than xoshiro; some variants have state-dependent period

## Maintenance

Unmaintained 2020 single-author preprint (arXiv 2002.11331v1); no license appears in the paper, the official site's TLS certificate has expired so its code and license could not be read, and an HN thread says the author later moved the code to Apache 2.0 (unconfirmed); Apache-2.0 ports exist for Rust (hasenbanck/romu) and .NET (bgrainger/RomuRandom).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** arXiv preprint by the author (not peer reviewed). It compares against xoshiro and PCG mainly through cycle counts and output latency from assembly analysis (g++ 4.8.4 -S -O3). Its only wall-clock table (Xeon E5-2643 v3) times RomuMono32 combinations and no baselines.
- **Verifier notes:** The paper prints the generator code inline, so has_code was set to true. Usability stays reference because no license was found. A future search could look for an official licensed source.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** independent gist by t-mat (no CPU model): under GCC RomuDuoJr 11.40 GiB/s vs Xoroshiro128+ 8.02 GiB/s; under MSVC Wyrand (12.81) beats RomuDuoJr (11.53)
- **Pages the verifier opened:**
  - <https://arxiv.org/pdf/2002.11331>
- **Sources the enricher read:**
  - <https://arxiv.org/abs/2002.11331>
  - <https://arxiv.org/pdf/2002.11331>
  - http://www.romu-random.org/ (redirect loop to https; TLS certificate expired, not read)
  - https://www.romu-random.org/code.c (TLS certificate expired, not read)
  - <https://news.ycombinator.com/item?id=22447848>
  - <https://github.com/bgrainger/RomuRandom>
  - <https://github.com/hasenbanck/romu>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `paper:romu-romutrio-romuquad-romumono`) · [data/wave8/enrich/raw/paper_romu_romutrio_romuquad_romumono.json](../../../data/wave8/enrich/raw/paper_romu_romutrio_romuquad_romumono.json) (enrichment confidence 0.6)

</details>
