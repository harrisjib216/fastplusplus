# stochastic-generation (Owen-scrambled Sobol', Halton, Faure and pmj02 sample sequences)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MIT` · 🟢 active

> Reference code for EGSR 2021 stochastic generation: Owen-scrambled Sobol', Halton, Faure and pmj02(bn) sequences at O(1) per coordinate.

| | |
|---|---|
| **Beats** | other published generators of Owen-scrambled Sobol', Halton, Faure and pmj02(bn) sequences (not named in the README) |
| **Claimed result** | README: 'I don't think there are any faster or simpler open-source implementations out there' and 'the code in this library is faster than any other published method'; no timings and no named baseline. It also says the minimal 2D Sobol' code of Listing 2 in the paper would be about 3x faster than this general-purpose code. Paper abstract (WebSearch snippet only, not read): an Owen-scrambled Sobol' (0,2)-sequence implementation in fewer than 30 lines of C++ generates 200 million samples per second on a single CPU thread; the snippet gives no baseline figure. |
| **Workload** | Generating low-discrepancy sample sequences (stochastic Sobol' up to 64 dimensions, Halton up to 10 dimensions, Faure, pmj02 and pmj02bn) with the method of 'Stochastic Generation of (t,s) Sample Sequences' (Helmer, Christensen, Kensler, 2021). |
| **Metric** | throughput |
| **Adoption** | 55 stars, 2 forks, 18 commits; reference implementation by the first author of the EGSR 2021 paper (DOI 10.2312/sr.20211287) |
| **Last commit** | 2026-07-10 |
| **Links** | [repository](https://github.com/Andrew-Helmer/stochastic-generation) · [benchmark](https://github.com/Andrew-Helmer/stochastic-generation) |

## Verdict

There are no measurements to verify. The README claims the code is 'faster than any other published method' for these sequences, names no competitor, and says the paper's 2D-only Listing 2 is about 3x faster. The paper abstract (WebSearch snippet only; the paper itself is egress-blocked) puts Listing 2 at 200 million samples/s on one CPU thread, which would imply roughly 65 million 2D samples/s for this library (derived, unmeasured, hardware unknown). For context, the author's earlier pmj-cpp documents pmj02 at about 1.65 million samples/s on a 2017 MacBook Pro, but that is different code and hardware.

## Use it when

- Monte Carlo or quasi-Monte Carlo integration (rendering, option pricing, uncertainty propagation) where you want Owen-scrambled Sobol', Faure or Halton points with fresh randomization per run.
- Precomputing sample tables (pmj02, pmj02bn, ssobol) in a renderer or tool, where the whole array is generated at once.
- Low-dimensional integrands of 3, 5, 7 or 11 dimensions at power-of-base sample counts: the sfaure (0,s)-sequences stratify on all elementary intervals.
- Learning or reimplementing the paper: the code favours readability, and the README says a specialised 2D version (paper Listing 2) is about 3x faster.

## Skip it when

- You need plain uniform random numbers: this produces stratified point sets, not a PRNG stream; use a PRNG (std::mt19937 replacement) instead.
- You need reproducible output: the array generators take no seed and seed PCG32 from std::random_device on each call; only the stateless Sobol' function takes a seed.
- Per-sample on-the-fly generation inside a renderer: the main generators need the whole n x nd array resident because each point reads an earlier one, so streaming needs the slower stateless path.
- More than 64 Sobol' or 10 Halton dimensions, or more than about 2^31 coordinates: dimensions are capped by compile-time tables, and indices and n\*nd products are plain int.
- Production use that needs error handling: bad arguments call std::terminate via an ASSERT macro, and there are no tests, releases or packaging.

## How it is fast

Stochastic generation (Helmer, Christensen, Kensler, EGSR 2021) builds the scrambled sequence directly instead of generating Sobol' points and then Owen-scrambling them digit by digit. For each new index prev_len+i, each dimension looks up an earlier sample at i XOR a precomputed per-dimension 'xor-value', takes that sample's stratum, flips its last digit (stratum ^ 1, or a base-b digit add for Faure and Halton), and draws one uniform offset inside the flipped stratum. So each coordinate costs one table lookup, one array read and one PCG32 draw, and the output is distributed as an Owen-scrambled sequence. The stateless variant recurses over the index bits instead, at O(log n) per coordinate.

## Compared with alternatives

No quasi-random siblings are catalogued yet; every listed sibling (Randompack, OpenRAND, EigenRand, the xoshiro and PCG variants) is a pseudo-random generator for independent uniforms. Pick this when you need stratified, Owen-scrambled point sets for integration, and a sibling PRNG when you need a random stream.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (C++ standard library only); xor_values.py (Python) is needed only to regenerate xor-value tables |
| **Minimum toolchain** | C++14 (makefile: g++ -std=c++14 -O2, 'make release' adds -O3) |
| **Platforms** | any; portable scalar C++ with no SIMD or intrinsics; 32-bit builds fixed by PR #1 (merged 2023-12-14) |
| **Thread safety** | Not documented; each call builds its own RNG, and the seeding helper in rng.h uses thread_local engines, so concurrent calls on separate output arrays look independent (inferred from the source). |
| **Drop-in for the baseline** | no |

## Gotchas

- Best-candidate mode (--bn2d, candidates &gt; 1) evaluates kBestCandidateSamples = 100 candidates per point, with a grid nearest-neighbour query each, so pmj02bn-style output costs far more than plain pmj02 or ssobol.
- The stateless Sobol' functions were broken until the 2022-09-01 commit 'Fix bugs with the stateless Sobol' implementation'; use current HEAD.
- Progressive shuffling ASSERTs that the sample count is a constant multiple of a power of the base (otherwise std::terminate) and copies the full array. Halton cannot be shuffled, and passing owen=true to ssobol or pmj02 only prints a warning and is ignored.
- Strata of earlier points are recovered by multiplying stored doubles by the stratum count, so outputs must stay as double; do not narrow the buffer to float.

## Known shortcomings

- 'Faster than any published method' has no numbers or baseline in the repo; the EGSR paper (blocked here) gives \~200M samples/s per thread without a named baseline.
- No measurements anywhere reachable; the paper is still blocked. Array generators take no seed (std::random_device), so output is not reproducible; the stateless Sobol' generator was broken until the 2022-09-01 fix; errors call std::terminate. Rough context only: the author's pmj-cpp documents pmj02 at about 1.65M samples/s on a 2017 MacBook Pro while the paper snippet gives 200M samples/s for Listing 2, on different code and hardware.

## Caveats and trade-offs

Claim has no comparative numbers and no named baseline. The paper (diglib.eg.org) and the co-author's abstract page (seanet.com) are egress-blocked here, so whether the paper times other Owen-scrambling or pmj02 generators is unknown; a paper-access retier could lift it to B. generate_samples.cpp times its own run (std::chrono) but nothing is published. Quasi-random generators have no mt19937/PCG/xoshiro equivalent, so baseline_in_list is false. The 2026 commits only edit the README; the last code change is the 2023-12-14 merge of a 32-bit PR.

Written for readability and generality, not peak speed. Command-line generate_samples and shuffle_indices tools plus a Python xor-value generator. Sobol' xor-values rely on pbrt-v3 generator matrices. Also supports progressive shuffling and best-candidate (blue-noise) sampling.

## Maintenance

Code has been stable since the 2023-12-14 32-bit fix (the 2026 commits only touch the README); MIT-licensed, about 1,700 lines of plain C++14 across sampling/, easy to vendor, with 55 stars and no open issues.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification D, tier now D.
- **Tier reason:** The README's Performance section claims the code is 'faster than any other published method' and that the paper's Listing 2 would be about 3x faster, but it names no baseline and gives no timings; generate_samples.cpp prints its own wall time but no results are published, so D.
- **Verifier notes:** Tier D with 55 stars would allow a strict not-notable reject, but it is the reference code of a peer-reviewed EGSR 2021 paper by well-known rendering authors, so confirm and keep with the shortcoming. Add it to leads.md for a paper-access retier (EGSR 2021 'Stochastic Generation of (t,s) Sample Sequences'). Tried seanet.com abstract page and pbr-book.org Further Reading: both EGRESS_BLOCKED.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Andrew-Helmer/stochastic-generation/HEAD/README.md>
  - <https://raw.githubusercontent.com/Andrew-Helmer/stochastic-generation/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Andrew-Helmer/stochastic-generation/HEAD/generate_samples.cpp>
  - <https://github.com/Andrew-Helmer/stochastic-generation>
  - <https://github.com/Andrew-Helmer/stochastic-generation/commits>
- **Sources the enricher read:**
  - <https://github.com/Andrew-Helmer/stochastic-generation>
  - <https://github.com/Andrew-Helmer/stochastic-generation/tree/main/sampling>
  - <https://github.com/Andrew-Helmer/stochastic-generation/commits/main>
  - <https://github.com/Andrew-Helmer/stochastic-generation/pulls?q=is%3Apr>
  - <https://raw.githubusercontent.com/Andrew-Helmer/stochastic-generation/HEAD/README.md>
  - <https://raw.githubusercontent.com/Andrew-Helmer/stochastic-generation/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Andrew-Helmer/stochastic-generation/HEAD/makefile>
  - <https://raw.githubusercontent.com/Andrew-Helmer/stochastic-generation/HEAD/generate_samples.cpp>
  - <https://raw.githubusercontent.com/Andrew-Helmer/stochastic-generation/HEAD/shuffle_indices.cpp>
  - <https://raw.githubusercontent.com/Andrew-Helmer/stochastic-generation/HEAD/xor_values.py>
  - <https://raw.githubusercontent.com/Andrew-Helmer/stochastic-generation/HEAD/sampling/rng.h>
  - <https://raw.githubusercontent.com/Andrew-Helmer/stochastic-generation/HEAD/sampling/ssobol.h>
  - <https://raw.githubusercontent.com/Andrew-Helmer/stochastic-generation/HEAD/sampling/ssobol.cpp>
  - <https://raw.githubusercontent.com/Andrew-Helmer/stochastic-generation/HEAD/sampling/sfaure.h>
  - <https://raw.githubusercontent.com/Andrew-Helmer/stochastic-generation/HEAD/sampling/sfaure.cpp>
  - <https://raw.githubusercontent.com/Andrew-Helmer/stochastic-generation/HEAD/sampling/shalton.h>
  - <https://raw.githubusercontent.com/Andrew-Helmer/stochastic-generation/HEAD/sampling/shalton.cpp>
  - <https://raw.githubusercontent.com/Andrew-Helmer/stochastic-generation/HEAD/sampling/shuffling.h>
  - <https://raw.githubusercontent.com/Andrew-Helmer/stochastic-generation/HEAD/sampling/shuffling.cpp>
  - <https://raw.githubusercontent.com/Andrew-Helmer/stochastic-generation/HEAD/sampling/bn_utils.h>
  - <https://raw.githubusercontent.com/Andrew-Helmer/stochastic-generation/HEAD/sampling/bn_utils.cpp>
  - <https://raw.githubusercontent.com/Andrew-Helmer/stochastic-generation/HEAD/sampling/utils.h>
  - <https://raw.githubusercontent.com/Andrew-Helmer/stochastic-generation/HEAD/sampling/xor_values.h>
  - <https://github.com/Andrew-Helmer?tab=repositories>
  - <https://raw.githubusercontent.com/Andrew-Helmer/pmj-cpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/Andrew-Helmer/pmj-cpp/HEAD/docs/code_usage.md>
  - <https://github.com/Andrew-Helmer/Andrew-Helmer.github.io>
  - <https://github.com/Andrew-Helmer/Andrew-Helmer.github.io/tree/master/_posts>
  - <https://raw.githubusercontent.com/Andrew-Helmer/Andrew-Helmer.github.io/master/_posts/2021-08-09-tree-shuffling.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/andrew-helmer/stochastic-generation`) · [data/wave8/enrich/raw/github_com_andrew_helmer_stochastic_generation.json](../../../data/wave8/enrich/raw/github_com_andrew_helmer_stochastic_generation.json) (enrichment confidence 0.5)

</details>
