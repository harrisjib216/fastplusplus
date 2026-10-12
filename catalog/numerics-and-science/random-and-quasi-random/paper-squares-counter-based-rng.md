# Squares counter-based RNG

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C` · `no license` · ⚪ unknown

> Stateless counter-based RNG built from 4-5 rounds of middle-square squaring; author reports \~1.7x Philox4x32-10 throughput.

| | |
|---|---|
| **Beats** | Philox 4x32-10 (Random123 counter-based RNG) |
| **Claimed result** | 1e9 32-bit randoms: Philox 4x32-10 2.29 s vs squares32 1.35 s (\~1.7x, derived from page data); 64-bit squares split into two 32-bit halves 1.23 s; 53-bit float output 1.93 s |
| **Workload** | Counter-based RNG using rounds of middle-square squaring (4 rounds 32-bit, 5 rounds 64-bit) |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-9700 3.0 GHz |
| **Compiler and flags** | gcc 11.2.0 under Cygwin64; optimization flags not stated |
| **Links** | [benchmark](https://arxiv.org/abs/2004.06278) |

## Verdict

Author's own timing: generating one billion 32-bit numbers on an Intel Core i7-9700 (3.0 GHz) with gcc 11.2.0 under Cygwin64 took 2.29 s with Philox4x32-10 and 1.35 s with squares32 (\~1.7x, derived from page data); 53-bit doubles from squares64 took 1.93 s. The paper does not give the flags or the Philox source (the download page bundles Random123 1.14.0). Quality claims are 300 BigCrush runs with random keys, 300 PractRand runs to 256 GB, and 25 to 32 TB.

## Use it when

- Parallel or GPU-style Monte Carlo where each work item needs random access to element i of a stream without passing state around
- Reproducible simulations where (counter, key) fully determines the output, so you can regenerate any sample on demand
- Hot loops where Philox's per-call cost matters and you can accept 4-5 64-bit multiplies per output
- Shader or hash-like use (keyed integer hash of an index), as in ports to GLSL

## Skip it when

- Anything security-related: it is a statistical generator, not a cryptographic one
- Code that cannot take GPL code: the author's download page says the package is under the GNU GPL, so copying squares.h brings GPL terms
- When a sequential generator is enough: the catalogued sibling PCG measured 0.78 cpb in Randen's README and xoshiro-class generators are typically cheaper than any counter-based design
- Arbitrary user-chosen keys: quality depends on the key's bit pattern, so keys must come from the key utility or follow its rules
- When you need peer-reviewed evidence: the paper is a self-published arXiv preprint (v7, March 2022) and the only speed comparison is the author's own

## How it is fast

It is a counter-based version of von Neumann's middle-square method: x = ctr\*key, then each round computes x = x\*x + (y or z) and swaps the 32-bit halves with a rotate. That is one 64-bit multiply plus an add and a rotate per round, five multiplies in total for 32-bit output, against the ten rounds of 32x32-&gt;64 multiplies and key schedule in Philox4x32-10. The generator's quality depends on the key, which needs an irregular bit pattern with about half ones; the bundled key utility produces about 2 billion keys that satisfy this.

## Compared with alternatives

Pick Squares over Randen when you want a cheap stateless counter-based generator rather than a backtracking-resistant AES-based one; prefer Romu, PCG or SIMDxorshift when a single sequential stream per thread is fine, since they need no multiply-heavy rounds or key management.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (stdint.h); the key utility is a separate program |
| **Minimum toolchain** | C99 or any C++ compiler with 64-bit integer multiply; paper used gcc 11.2.0 |
| **Platforms** | any; fast when 64x64-&gt;64 multiply is cheap (x86-64, aarch64) |
| **Thread safety** | Stateless pure functions of (ctr, key), so safe to call from any number of threads |
| **Drop-in for the baseline** | partial — same counter+key model as Philox, but a different function signature (one 64-bit counter and one 64-bit key, returning one value rather than 4x32) and different output streams |

## Gotchas

- Key quality matters: the paper says keys need an irregular bit pattern with roughly equal ones and zeros; the key utility enforces distinct upper and lower digit patterns.
- The paper reports that Justin Lebar found a statistical failure in a 3-round version; do not cut rounds below 4 (32-bit) or 5 (64-bit).
- The 64-bit version costs more: 1.93 s per billion 53-bit doubles versus 1.35 s for 32-bit outputs in the paper's own timing.
- Code is distributed from a Wix site, not a public repository; the latest download is version 8 (Feb 2024), and older versions remain listed.

## Known shortcomings

- First-party, not peer-reviewed; no optimization flags; Philox implementation unnamed; code on author's site not opened, license unknown.
- Author's download page (squaresrng.wixsite.com/rand) says GNU GPL; no public repo, latest code v8 (Feb 2024); output quality depends on keys from the bundled key utility; paper notes a statistical failure in a 3-round version.

## Caveats and trade-offs

First-party, non-peer-reviewed arXiv paper; optimization flags and Philox implementation source not stated; code is distributed from the author's website (squaresrng.wixsite.com/rand), license not checked; no comparison against Threefry/mt19937 timings found

Counter-based, stateless; passes TestU01/PractRand per abstract

## Maintenance

A single-author algorithm with the latest code release (v8) in Feb 2024. It is GPL per the download page, and the core is about 10 lines you could reimplement from the paper, but reimplementing it does not remove the GPL question for derived code; usability stays reference.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification D, tier now C.
- **Tier reason:** Upgraded from D: the full paper (arXiv v7) times one billion 32-bit numbers on an Intel Core i7-9700 with gcc 11.2.0 (Cygwin64): Philox 4x32-10 2.29 s vs Squares 1.35 s. These are the author's own numbers, the paper is not peer-reviewed, and flags and the Philox implementation are unstated, so the tier is C.
- **Verifier notes:** The Philox numbers appear only in the PDF body, not on the abstract page. Code site not opened, so the license is unknown and usability stays reference; has_code may be true (software package offered) but the site is unverified.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `hardware`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** arXiv PDF: 1e9 32-bit values on i7-9700, gcc 11.2: Philox4x32-10 2.29 s vs Squares 1.35 s
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2004.06278>
  - <https://arxiv.org/pdf/2004.06278>
- **Sources the enricher read:**
  - <https://arxiv.org/abs/2004.06278>
  - <https://arxiv.org/pdf/2004.06278>
  - <https://ar5iv.labs.arxiv.org/html/2004.06278>
  - <https://squaresrng.wixsite.com/rand>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `paper:squares-counter-based-rng`) · [data/wave8/enrich/raw/paper_squares_counter_based_rng.json](../../../data/wave8/enrich/raw/paper_squares_counter_based_rng.json) (enrichment confidence 0.65)

</details>
