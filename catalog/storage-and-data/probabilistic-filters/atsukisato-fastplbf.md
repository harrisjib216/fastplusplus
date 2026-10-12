# FastPLBF (fast PLBF / fast PLBF++)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Python` · `MIT` · 🟡 stale

> Python reference code for fast PLBF and PLBF++, which cut partitioned learned Bloom filter construction time 34x-761x versus PLBF.

| | |
|---|---|
| **Beats** | PLBF (Partitioned Learned Bloom Filter) |
| **Claimed result** | The maximum speedups come from the k ablation at k=50. There, fast PLBF constructs the same data structure as PLBF 233x faster (URLs) and 199x faster (EMBER), and fast PLBF++ is 761x faster (URLs) and 500x faster (EMBER). At the paper's default setting (N=1000, k=5, including model training), fast PLBF is 50.8x/34.3x faster and fast PLBF++ is 63.1x/39.3x faster than PLBF (URLs/EMBER). Fast PLBF has memory efficiency identical to PLBF. Fast PLBF++ has up to 1.0019x (URLs) and 1.000083x (EMBER) higher false positive rate than PLBF. |
| **Workload** | Constructing a partitioned learned-Bloom-filter data structure from real-world datasets (Malicious URLs dataset, EMBER malware dataset), varying segment count N and region count k, measuring wall-clock construction time versus resulting memory usage / false positive rate |
| **Metric** | build-time |
| **Adoption** | 13 stars |
| **Last commit** | 2025-06-24 |
| **Links** | [repository](https://github.com/atsukisato/FastPLBF) · [benchmark](https://arxiv.org/abs/2306.02846) |

## Verdict

The NeurIPS 2023 paper times Python construction (including LightGBM training and key insertion) of fast PLBF and fast PLBF++ against the authors' own reimplementation of PLBF, on the Malicious URLs and EMBER datasets, in the memory-budget framework. At N=1000, k=5, fast PLBF is 50.8x (URLs) and 34.3x (EMBER) faster and fast PLBF++ is 63.1x and 39.3x faster; at N=1000, k=50 with a 500 Kb backup-filter budget the figures are 233x/199x and 761x/500x. Fast PLBF gives identical FPR and fast PLBF++ is at most 1.0019x (URLs) and 1.000083x (EMBER) worse; no CPU, Python version or hardware is stated.

## Use it when

- You use or plan to use a PLBF, and the parameter search dominates build time at N around 1000. The paper reports PLBF spending over 3 minutes finding t and f, while fast PLBF and fast PLBF++ finish the whole build in under 2 seconds.
- The filter is rebuilt often (model retraining, changing key sets), so construction latency matters more than query speed.
- You want to raise N and k to lower FPR without cubic build cost. The authors suggest N \~1000 and k \~100, with builds of a few tens of seconds.
- Pick fast PLBF when you need exactly PLBF's thresholds and FPRs. Pick fast PLBF++ when classifier scores are close to monotone and an FPR penalty of about 0.2% (URLs) is acceptable.
- You want a compact reference for porting the DP into your own C++ or Rust learned filter. The core is about 100 lines across calc_DPKL.py, fast_calc_DPKL.py and matrix_problem_on_monotone_matrix.py.

## Skip it when

- On a production query path. Backup filters use the pure-Python bloom-filter 1.3.3 package, contains() does a Python bisect plus Python hashing, and the paper reports no query-throughput numbers. The speedup is build-time only.
- When you have no classifier that produces [0,1] scores at query time. Every lookup needs s(x), so model inference cost and model size (312 Kb and 1.19 Mb LightGBM models in the paper) add to each query and to total memory.
- When scores are weakly correlated with membership, use fast PLBF++ with care. It is not guaranteed optimal, and on synthetic data with almost no monotonicity (10^8 swaps) its FPR reached 1.85x PLBF's (paper Appendix G). Use fast PLBF there.
- When the baseline you actually run is the original public PLBF code (kapilvaidya24/plbf). That code appears to run one DP over at most 100 quantile chunks, which is the 'relaxed' method. Appendix F shows the relaxed method builds about as fast as fast PLBF, although its FPR is up to 1.48x worse on EMBER. The 34x-761x figures are against the O(N^3 k) complete method.
- When you need dynamic inserts or deletes. Keys go in once at construction, into fixed-size backup Bloom filters, and there is no update or serialization API.

## How it is fast

PLBF solves a separate O(j^2 k) DP for each j = k..N, which is O(N^3 k) in total. Fast PLBF observes that every one of those subproblems is a prefix of the single j = N table, so it builds that table once and traces back each j in O(k). That gives O(N^2 k) with an identical result. Fast PLBF++ also treats each DP layer as a row-maxima 'matrix problem' on a monotone matrix (Aggarwal et al. 1987) and solves it by divide-and-conquer: exhaustively search the middle row, then recurse on the narrowed ranges (matrix_problem_on_monotone_matrix.py). That gives O(Nk log N + Nk^2). Monotonicity is proven only for an 'ideal' score distribution where g_i/h_i is non-decreasing; otherwise the result can be suboptimal.

## Compared with alternatives

No siblings catalogued yet. Compared with the baseline PLBF code, pick this when you need the complete, fi &lt;= 1-constrained optimum at large N or k in seconds. If you want a pip-installable wrapper with scikit-learn-style classifiers, learnedbf vendors this code.

## Integration

| | |
|---|---|
| **Form** | source-drop. There is no setup.py or pyproject and it is not on PyPI; the scripts prepend the parent directory to sys.path. The MIT code is also vendored in the pip package learnedbf (SLIMlaboratory, Apache-2.0). |
| **Dependencies** | bloom-filter==1.3.3 (pure Python), pandas==2.3.0, scikit-learn==1.6.1. PLBF.py imports pandas and scikit-learn at module top level even though only the CLI uses them. |
| **Minimum toolchain** | Python 3.9+ (inferred: signatures use list[float] annotations, and the pinned pandas 2.3.0 and scikit-learn 1.6.1 require &gt;=3.9); not otherwise documented |
| **Platforms** | any (pure Python) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — FastPLBF and FastPLBFpp subclass the repo's own PLBF class, keep the same constructor and contains(key, score), and override only find_best_t_and_f. They are not API-compatible with the original kapilvaidya24/plbf functions (get_thresholds, get_optimal_fpr). |

## Gotchas

- Inputs are validated with assert statements, one per score. Running under python -O strips them, and when they are active they add an O(n) Python loop to construction.
- A June 2025 commit ('fix counting method') switched to add-one smoothing: segment and region counts now start at 1 and totals include the pseudo-counts. The current code is therefore not identical to the code behind the 2023 paper numbers.
- In PLBF_M and FastPLBF_M, memory_usage_of_backup_bf is computed from the last loop iteration's t and f, not from t_best and f_best, so the reported figure may not match the configuration chosen. The filters themselves are built with the best values.
- Segments are equal-width score intervals (i/N), not quantiles as in the original plbf code, so heavily skewed score distributions leave many segments nearly empty.

## Known shortcomings

- The 233x/761x construction speedups are the k=50 ablation; at the default N=1000, k=5 it is 34-63x faster than PLBF; no hardware stated.
- The speedup is build time only, in a pure-Python reference with pure-Python Bloom backups (source drop, no package; the caller must pass a model score per query). The baseline is the authors' own O(N^3 k) complete PLBF; the original PLBF code appears to run a relaxed single DP about as fast as fast PLBF (App. F). fast PLBF++ is not guaranteed optimal (FPR up to 1.85x PLBF on synthetic non-monotone data). A 2025-06 counting fix means the code differs from the paper-era code; \*_M report the last loop's memory, not the best; asserts used for validation; stale, no releases (also vendored in the learnedbf PyPI package).

## Caveats and trade-offs

Peer-reviewed (NeurIPS 2023), but the paper gives no CPU or hardware details for the construction-time numbers, so it falls short of tier A despite public code and real datasets. The comparison is against the authors' own PLBF implementation (src/PLBFs/PLBF.py) in a slightly modified framework: minimize FPR under a memory budget instead of PLBF's original objective. It is not an independent PLBF benchmark. The 233x/761x headline comes from the k=50 ablation. At the default N=1000, k=5, the gains are 34x-63x. The implementation is pure Python (a reference implementation, not a production library).

Reference Python implementation only, no production/C++ port; the speedup is an algorithmic construction-time complexity reduction (O(N^2 k) or O(Nk log N + Nk^2) vs PLBF's O(N^3 k)), most pronounced at large N; fast PLBF++ trades a small amount of memory efficiency for its larger speedup.

## Maintenance

Stale research code: 13 stars, no releases or tags, and only four small commits since 2023 (June 2025: import fix, counting fix, eval scripts, dependency bump). It is MIT-licensed and small enough to vendor or port, and it is already vendored in the learnedbf PyPI package.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** This is a peer-reviewed NeurIPS 2023 paper (arXiv 2306.02846) that measures construction time of fast PLBF / fast PLBF++ against PLBF on the Malicious URLs and EMBER datasets. Public Python code exists (src/PLBFs/), but no CPU or hardware is stated, so it is not tier A. The &gt;50x gains are not implausible because they follow from the complexity reduction from O(N^3 k) to O(N^2 k) or O(Nk log N + Nk^2), so no cap to C applies.
- **Verifier notes:** The abstract and Section 5.3 of the arXiv paper both contain the 233x/761x figures, and Section 5.1 gives the smaller default-setting speedups, which I added for context. Metadata checks out: MIT license, 13 stars, last commit 2025-06-24 (stale), not a fork. The original PLBF repo (kapilvaidya24/plbf) is in known_list.txt.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2306.02846>
  - <https://arxiv.org/pdf/2306.02846>
  - <https://github.com/atsukisato/FastPLBF>
- **Sources the enricher read:**
  - <https://github.com/atsukisato/FastPLBF>
  - <https://github.com/atsukisato/FastPLBF/blob/main/src/PLBFs/PLBF.py>
  - <https://github.com/atsukisato/FastPLBF/blob/main/src/PLBFs/FastPLBF.py>
  - <https://github.com/atsukisato/FastPLBF/blob/main/src/PLBFs/FastPLBFpp.py>
  - <https://github.com/atsukisato/FastPLBF/blob/main/src/PLBFs/PLBF_M.py>
  - <https://github.com/atsukisato/FastPLBF/blob/main/src/PLBFs/FastPLBF_M.py>
  - <https://github.com/atsukisato/FastPLBF/tree/main/src/PLBFs/utils>
  - <https://github.com/atsukisato/FastPLBF/blob/main/src/test.py>
  - <https://github.com/atsukisato/FastPLBF/blob/main/requirements.txt>
  - <https://github.com/atsukisato/FastPLBF/commits/main>
  - <https://github.com/atsukisato/FastPLBF/commit/11d1fba>
  - <https://github.com/atsukisato/FastPLBF/issues?q=is%3Aissue>
  - <https://arxiv.org/abs/2306.02846>
  - <https://arxiv.org/pdf/2306.02846>
  - <https://export.arxiv.org/api/query?id_list=2306.02846>
  - <https://github.com/kapilvaidya24/plbf>
  - <https://github.com/kapilvaidya24/plbf/blob/master/plbf_algo.py>
  - <https://github.com/SLIMlaboratory/learnedbf>
  - <https://github.com/atsukisato/CascadedLBF>
  - <https://pypi.org/pypi/bloom-filter/json>
  - <https://pypi.org/pypi/pandas/2.3.0/json>
  - <https://pypi.org/pypi/scikit-learn/1.6.1/json>
  - <https://pypi.org/pypi/learnedbf/json>
  - <https://hn.algolia.com/api/v1/search?query=%22partitioned%20learned%20bloom%22&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/atsukisato/fastplbf`) · [data/wave6/enrich/raw/github_com_atsukisato_fastplbf.json](../../../data/wave6/enrich/raw/github_com_atsukisato_fastplbf.json) (enrichment confidence 0.85)

</details>
