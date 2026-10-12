# Partitioned Learned Bloom Filter (PLBF)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `Python` · `no license` · 🔴 abandoned

> Python solver for Partitioned Learned Bloom Filter parameters; the resulting design uses less space than Bloom, sandwiched LBF, Ada-BF.

| | |
|---|---|
| **Beats** | Bloom filter |
| **Claimed result** | at matched space (400Kb/500Kb/3000Kb for synthetic/URLs/EMBER), PLBF achieves 22x, 26x, and 3x smaller false-positive rates than the sandwiching approach, and 8.5x, 9x, 1.9x smaller than Ada-BF; to hit FPR=0.001, sandwiching needs 8.8x/3.3x/1.2x the space of PLBF and Ada-BF needs 6x/2.5x/1.1x the space |
| **Workload** | False-positive rate vs. space tradeoff on a synthetic dataset, a URL dataset, and the EMBER malware dataset, comparing PLBF against a theoretically-optimal Bloom filter, sandwiched learned Bloom filter, and Ada-BF |
| **Metric** | memory |
| **Adoption** | 7 stars |
| **Last commit** | 2022-06-29 |
| **Links** | [repository](https://github.com/kapilvaidya24/PLBF) · [benchmark](https://arxiv.org/abs/2006.03176) |

## Verdict

ICLR 2021 paper (arXiv 2006.03176v2, Section 4.1), Python simulations with an sklearn random-forest model counted at its pickle size, k=5, N=1000, and an idealized 'optimal' backup filter (standard Bloom size / log2 e) for every learned variant. At 400/500/3000 Kb on synthetic/URLs/EMBER, PLBF had 22x/26x/3x lower FPR than sandwiched LBF and 8.5x/9x/1.9x lower than Ada-BF; to reach FPR 0.001, sandwiched LBF needed 8.8x/3.3x/1.2x and Ada-BF 6x/2.5x/1.1x PLBF's space. There are no compiler, hardware or query-latency numbers, and the comparison against a standard Bloom filter appears only as a plot (Appendix E.1, Fig. 4).

## Use it when

- Static key sets that come with predictive features and a classifier that separates keys from non-keys well, such as malicious-URL or malware blocklists. The large paper wins (3.3x-8.8x less space than sandwiched LBF at FPR 0.001) came from models with F1 of 0.97-0.99.
- You have a representative sample of non-key queries (for example, historical query logs). The solver estimates the non-key score distribution from it, and the target FPR holds only in expectation over that distribution.
- Filter size is the binding constraint (for example, a blocklist shipped to clients or edge nodes) and each query can afford a model inference.
- You already run a sandwiched or Ada-BF-style learned filter and want principled thresholds and per-region FPRs instead of heuristics. The solver is about 200 lines of plain Python and easy to port.
- Studying the algorithm: this is the authors' own reference code for Algorithm 1 and the KL-divergence DP.

## Skip it when

- Keys with no learnable signal (random IDs, bare hashes). The model adds bytes without adding divergence. Even EMBER, with a model at F1 0.85, needed only 1.1x-1.2x less space than the learned baselines at FPR 0.001.
- Latency-sensitive query paths. Every query pays for model inference (a random forest in the paper) plus a filter probe, and the paper reports no query-time numbers. The CLBF paper (arXiv 2502.03696v2) measures PLBF reject time at about 14.6x slower on average, and up to 65x slower, than its cascaded design.
- Dynamic sets or query distributions that drift. Any change means retraining the model and re-solving, there is no insert or delete path, and queries aimed at high-score regions can push the FPR above target.
- Production use of this repo as-is. It has no license and no filter implementation, and it crashes (ValueError: math domain error) when any score chunk contains no keys, which happens with exactly the well-separated models PLBF is meant for. For runnable code, use atsukisato/FastPLBF (MIT).
- Workloads that want a plain, fast, model-free AMQ in C/C++. Xor filters sit only 14-23% above the space lower bound (figures from the catalog's BuRR entry), and ribbon filters sit lower still, all without a model.

## How it is fast

The gain is in space, not speed. With boundaries fixed, the KKT conditions give each region's optimal FPR as f_i = F \* g_i / h_i (the region's share of keys divided by its share of non-key queries), and the space saved against a plain Bloom filter works out to c \* |S| \* KL(g||h) minus the model size. So the thresholds come from a dynamic program over a discretized score axis that maximizes the KL divergence between region-level key and non-key distributions (O(N^2 k)). Algorithm 1 then caps any f_i &gt;= 1 at 1 (no filter in that region) and re-solves the rest; the paper finds that 4-6 regions are enough.

## Compared with alternatives

Over Ada-BF: same learned-filter setup, but PLBF picks thresholds and FPRs by optimization and needed 1.1x-6x less space at FPR 0.001 in the paper. Over CLBF: only when you want the simpler PLBF formulation and query latency does not matter, since CLBF reports up to 17% less memory and much faster rejects than PLBF. For key sets with no learnable signal, Xor Filter or BuRR is the better pick, and for working PLBF code start from FastPLBF rather than this solver.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | numpy (imported at the top of plbf_algo.py but used only by the built-in demo). You must supply your own classifier and backup Bloom filter implementation. |
| **Minimum toolchain** | not documented; plain Python 3 (ran under CPython 3.9.6 in this session) |
| **Platforms** | any (pure Python) |
| **Thread safety** | not documented. The functions are stateless and run offline at build time; threshold_params is sorted in place. |
| **Drop-in for the baseline** | no |

## Gotchas

- Importing plbf_algo runs the module-level demo: it generates about 200k normal samples, solves for K=5 at FPR 0.1 and prints the result. Strip the bottom block before importing it as a library.
- Crashes on well-separated scores: the DP calls math.log(delta_G/delta_H), so a score chunk with zero keys raises ValueError and a chunk with zero non-keys divides by zero. Reproduced here with keys in [0.8,1] and non-keys in [0,0.3], and again with Gaussians at 0.9/0.1 and 0.1/0.1. FastPLBF's DP guards both cases.
- Not the benchmarked algorithm. The repo runs Algorithm 2 (relaxed-DP thresholds, then the Algorithm 1 fix-up) over at most 100 quantile chunks. Paper Section 4.1 used Algorithm 3 (search over the last region's boundary, O(N^3 k)) with N=1000, which the Fast PLBF paper says takes over 3 minutes at k=5. Expect results somewhat off the paper's curves.
- Inputs must be Python lists of scores in [0,1]; with numpy arrays, key_scores+non_key_scores would add elementwise instead of concatenating. Several regions can come back with FPR 1 (the demo returns [..., 1, 1]); those regions accept everything and should be merged. The README's 'ICLR 2020' is wrong: the paper appeared at ICLR 2021.

## Known shortcomings

- The repo is only the algorithm file with no license (all rights reserved); abandoned since 2022-06. Venue is ICLR 2021.
- The repo is only a parameter solver (thresholds and per-region FPR) with no filter or query code; importing it runs a demo. Well-separated scores (the strong-model case PLBF targets) crash with a math domain error (log 0). It implements Algorithm 2 with &lt;=100 chunks while the paper benchmarked Algorithm 3 with N=1000. Gains are space vs learned variants, no latency numbers; CLBF reports PLBF reject is 14.6x on average (up to 65x) slower. atsukisato/FastPLBF (MIT) is a runnable alternative.

## Caveats and trade-offs

Peer-reviewed at ICLR 2021. The repo README says 'ICLR 2020', which is wrong; the CLBF paper cites it as ICLR 2021. The repo has only plbf_algo.py (threshold/FPR optimizer) and a README. It has no LICENSE file (reference/study only) and no experiment or benchmark code. The headline multipliers are against learned variants (sandwiched LBF, Ada-BF), not a raw Bloom filter. The 'optimal Bloom filter' curve is analytical (standard Bloom filter space / log2 e), and the standard-Bloom-filter comparison (Appendix E.1, Fig. 4) is shown only as a plot. The model is an sklearn random forest, sized by its pickle file. Last commit was in 2022-06, more than 3 years ago.

Needs a trained scoring model plus a dynamic-program solve for optimal partition thresholds; benefit shrinks when the model is weak (EMBER dataset shows only a slight improvement)

## Maintenance

Abandoned: six commits, all on 2022-06-29, 7 stars, zero issues, no license, and the experiment code was never released. Treat it as an algorithm reference and use the MIT-licensed atsukisato/FastPLBF (NeurIPS 2023; its PLBF class builds real backup Bloom filters) as the runnable base.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed paper (ICLR 2021, per the CLBF paper's reference [38]; arXiv 2006.03176v2). Section 4.1 plots PLBF against a theoretically optimal Bloom filter (standard Bloom filter space divided by log2 e) and Appendix E.1 (Fig. 4) against standard Bloom filters. All the quoted multipliers vs sandwiched LBF and AdaBF appear verbatim in Section 4.1. The repo has only the parameter-optimization algorithm, not the experiment code, so this cannot be A.
- **Verifier notes:** Numbers check out exactly against arXiv Section 4.1. The only fixes are the venue year (ICLR 2021, not 2020) and maintenance status: the last commit on 2022-06-29 is more than 3 years before 2026-09-26, so the repo is abandoned, not stale. Metadata confirmed via gh: no license, 7 stars, not a fork, not archived.
- **Fields the verifier corrected:** `maintenance_status`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2006.03176>
  - <https://arxiv.org/pdf/2006.03176>
  - <https://github.com/kapilvaidya24/PLBF>
  - <https://arxiv.org/pdf/2502.03696>
- **Sources the enricher read:**
  - <https://github.com/kapilvaidya24/PLBF>
  - <https://github.com/kapilvaidya24/PLBF/blob/main/README.md>
  - <https://github.com/kapilvaidya24/PLBF/blob/main/plbf_algo.py>
  - <https://github.com/kapilvaidya24/PLBF/commits/main>
  - <https://github.com/kapilvaidya24/PLBF/issues>
  - <https://arxiv.org/abs/2006.03176>
  - <https://arxiv.org/pdf/2006.03176>
  - <https://api.openreview.net/notes/search?term=Partitioned%20Learned%20Bloom%20Filters>
  - <https://api2.openreview.net/notes/search?term=Partitioned%20Learned%20Bloom%20Filter&limit=5>
  - <https://arxiv.org/pdf/2306.02846>
  - <https://github.com/atsukisato/FastPLBF>
  - <https://github.com/atsukisato/FastPLBF/blob/main/src/PLBFs/PLBF.py>
  - <https://github.com/atsukisato/FastPLBF/blob/main/src/PLBFs/utils/calc_DPKL.py>
  - <https://github.com/atsukisato/FastPLBF/blob/main/src/PLBFs/utils/const.py>
  - <https://github.com/atsukisato/FastPLBF/blob/main/requirements.txt>
  - <https://arxiv.org/pdf/2502.03696>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/kapilvaidya24/plbf`) · [data/wave6/enrich/raw/github_com_kapilvaidya24_plbf.json](../../../data/wave6/enrich/raw/github_com_kapilvaidya24_plbf.json) (enrichment confidence 0.85)

</details>
