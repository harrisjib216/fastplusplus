# Adaptive Learned Bloom Filter (Ada-BF)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `Python` · `no license` · 🔴 abandoned

> Research Python for learned Bloom filters that tune hashing per classifier-score band, cutting FPR versus standard and learned Bloom filters.

| | |
|---|---|
| **Beats** | Bloom filter |
| **Claimed result** | Paper: Ada-BF/disjoint Ada-BF 'reduce the FPR by over 80% and save 50% of the memory usage over existing learned Bloom filters'. On malicious URLs at a 500Kb filter size, Ada-BF cuts FPR by 81% vs LBF/sandwiched LBF (disjoint Ada-BF: 84%); at FPR \~0.35% the memory drops from over 500Kb (LBF) to 300Kb (over 40% savings). On malware MD5, 0.2% FPR needs \~300Kb for LBF vs 150Kb for Ada-BF (50%), and all learned BFs cut FPR by over 98% vs the standard Bloom filter. |
| **Workload** | False-positive rate vs. memory budget on a malicious-URL dataset (485,730 URLs, 16.47% malicious) and other real-world datasets; standard Bloom filter vs. learned Bloom filter (LBF), sandwiched LBF, Ada-BF, and disjoint Ada-BF |
| **Metric** | memory |
| **Adoption** | 17 stars |
| **Last commit** | 2022-05-24 |
| **Links** | [repository](https://github.com/DAIZHENWEI/Ada-BF) · [benchmark](https://arxiv.org/abs/1910.09131) |

## Verdict

This is a numerical FPR-versus-bitmap-size comparison, not a timing benchmark. On a 485,730-URL Kaggle set, with a random forest whose 146Kb pickle is added to the standard BF's budget, Ada-BF cut FPR by 81% versus LBF/sandwiched LBF at 500Kb (disjoint Ada-BF: 84%) and reached about 0.35% FPR in 300Kb where LBF needed over 500Kb. On VirusShare MD5 data it needed about 150Kb versus about 300Kb for LBF at 0.2% FPR, and all learned filters were over 98% below the standard BF. No hardware, compiler or runtime is reported; the only cost figure is hash operations per query in the NeurIPS version.

## Use it when

- Reproducing or teaching learned-filter results: the repo has BF, LBF, Ada-BF, disjoint Ada-BF and PLBF implementations that run on the same URL CSV.
- A static key set, such as a URL blocklist or malware-hash list, where a small classifier's score separates members (high scores) from non-members (low scores) and bits stored or sent matter more than per-query CPU. The paper reports 40-50% less memory than an LBF at the same FPR.
- Prototyping the score-banding idea before porting it to a real filter implementation; each script is 80-250 lines of plain numpy/pandas.
- Distributing a filter to many servers where update size is the constraint (the NeurIPS fake-news experiment reports half the space of an LBF at equal FPR).

## Skip it when

- Any production or library use: there is no license, no API, and no persistence, every hash is a Python-level loop over sklearn's murmurhash3_32, and each bit is stored as a 64-bit numpy int.
- Latency-sensitive lookups: every query needs a classifier inference (a 10-tree random forest in the URL experiment) plus about 2.8x the hash operations of a plain Bloom filter at 400Kb, and no timing benchmark exists.
- Adversarial or drifting query streams: the FPR depends on non-key scores following the tuning distribution, and items above the top threshold are accepted without any hash check. The paper itself names adversarial examples and drift as weaknesses of learned filters.
- Weak classifiers, or when you want the best learned filter: the later PLBF paper (arXiv 2006.03176) reports 9x lower FPR than AdaBF on URLs at 500Kb, and AdaBF needs 2.5x PLBF's space at FPR 0.001; on EMBER, where the model helps less, the gap was only 1.1x.
- Dynamic sets: there are no deletes, and thresholds and filter sizes are tuned offline over the full key set, so changing the keys means retraining or re-scoring and rebuilding.

## How it is fast

The win is FPR per bit, not speed. The learned Bloom filter (Kraska et al. 2018) uses a single score threshold; Ada-BF generalizes this to g score regions with K_j hash functions, fixing K_j - K_{j+1} = 1 and a non-key ratio m_j/m_{j+1} = c so that only (K_max, c) need tuning, with the aim of equalizing expected false positives m_j \* alpha^K_j across groups. Disjoint Ada-BF sizes each group's filter from R_j/n_j - R_1/n_1 = (j-1)log(c)/log(0.618). Queries cost more than a plain Bloom filter: the NeurIPS version reports 3.39 (BF), 6.98 (LBF), 9.40 (Ada-BF) and 12.07 (disjoint Ada-BF) hash operations per query at 400Kb, on top of one classifier inference.

## Compared with alternatives

Every sibling (Xor, BuRR, Prefix, Vacuum, Morton, and so on) is a key-agnostic filter with a fixed space overhead that needs no model; BuRR's table puts Xor/Xor+ at 14-23% over the information-theoretic minimum, versus the roughly 44% the Ada-BF paper cites for a standard Bloom filter. Pick Ada-BF only to study or prototype a learned filter when a classifier cleanly separates members from non-members and you count the model's bytes in the budget; for anything you ship over a static set, use Xor or BuRR.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | numpy, pandas, scikit-learn (murmurhash3_32), matplotlib; scipy for PLBF.py; no requirements file |
| **Minimum toolchain** | Not documented. The committed __pycache__ is CPython 3.7, and plt.style.use('seaborn-deep') needs matplotlib &lt; 3.8, which removed the seaborn-&lt;foo&gt; styles. |
| **Platforms** | any (pure Python) |
| **Thread safety** | not documented; single-threaded scripts with module-level state |
| **Drop-in for the baseline** | no |

## Gotchas

- The scripts run everything at top level (argparse, CSV load, a histogram with plt.show() that writes Score_Dist.png to the working directory), so they cannot be imported as modules, and plt.show() blocks on GUI backends.
- The README commands are partly broken. disjoint_Ada-BF.py requires --model_path, which the README omits, and it subtracts the model file size x8 from the budget while Ada-BF.py does not, so --size_of_Ada_BF means different things in the two scripts. PLBF.py reads a 'query' column that the shipped CSVs lack (open issue #1) and needs model pickles that are not in the repo.
- Datasets/Malware_data.csv has the columns label,score,md5 with labels 0/1, but every script selects label == -1 and a 'url' column, so only URL_data.csv runs as-is. Even that file has 411,184 rows (66,385 malicious), not the paper's 485,730, so reruns will not match the paper's figures exactly.
- Results are not reproducible run to run: hash seeds come from an unseeded randint and the 30% tuning sample is unseeded. The final FPR is measured on all negatives, including the tuning sample. Disjoint Ada-BF divides by only the below-threshold negatives, which overstates its printed FPR.

## Known shortcomings

- Gains are mostly over other learned Bloom filters and are in FPR/memory, not speed; abandoned since 2022-05.
- Not a library: five argparse Python scripts with no API, persistence or license; bits stored as 64-bit numpy ints; hashing in Python loops. Queries cost more (classifier inference plus 9.40/12.07 hashes vs 3.39 for a Bloom filter at 400 Kb) and there is no timing benchmark.
- README commands are partly broken (disjoint mode needs --model_path; PLBF 'query' KeyError, issue #1; model pickles absent); only the URL dataset runs (the malware CSV has the wrong label/column format) and it has 411,184 rows vs the paper's 485,730. Needs matplotlib &lt;3.8. Unseeded hashes; the final FPR includes tuning negatives and the disjoint FPR denominator is wrong. Superseded: the PLBF paper reports 9x lower FPR than Ada-BF on URLs at 500 Kb.

## Caveats and trade-offs

Reference Python research code with no LICENSE file (reference/study-only). Peer-reviewed at NeurIPS 2020 as 'Adaptive Learned Bloom Filter (Ada-BF): Efficient Utilization of the Classifier with Application to Real-Time Information Filtering on the Web'. This is a numerical FPR-vs-memory comparison, not a speed benchmark: most headline gains are vs other learned Bloom filters, and the standard BF's bit budget is credited with the classifier size (146Kb on URLs). No CPU/compiler details apply. The repo also ships a PLBF.py baseline.

Requires training/maintaining a classifier model alongside the filter; memory savings depend on how well the model's score distribution separates keys from non-keys, so gains are dataset-dependent

## Maintenance

Abandoned: the last code change was PLBF.py on 2022-05-24, the two 2021 issues were never answered, and with no LICENSE file the code is study-only (17 stars, 7 forks).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The paper (arXiv:1910.09131, later published at NeurIPS 2020 under an expanded title) compares against a standard Bloom filter, LBF and sandwiched LBF on the malicious-URL and malware datasets, and the 81%/84%, 0.35%-FPR 500Kb-to-300Kb and &gt;80% numbers all appear in it. This is a peer-reviewed FPR/memory comparison with Python code and no hardware or systems methodology, so it is B, not A.
- **Verifier notes:** Numbers are verified on the arXiv PDF. 'Save over 50% memory' is corrected to the paper's 'save 50%'. The last commit was 2022-05-24 (over 4 years ago), so the status is abandoned; there is no license (spdx null, no LICENSE file), so usability stays reference.
- **Fields the verifier corrected:** `maintenance_status`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/DAIZHENWEI/Ada-BF>
  - <https://arxiv.org/abs/1910.09131>
  - <https://arxiv.org/pdf/1910.09131>
  - <https://export.arxiv.org/api/query?id_list=1910.09131>
  - <https://proceedings.neurips.cc/paper_files/paper/2020>
- **Sources the enricher read:**
  - <https://github.com/DAIZHENWEI/Ada-BF>
  - <https://github.com/DAIZHENWEI/Ada-BF/blob/master/README.md>
  - <https://github.com/DAIZHENWEI/Ada-BF/blob/master/Ada-BF.py>
  - <https://github.com/DAIZHENWEI/Ada-BF/blob/master/Bloom_filter.py>
  - <https://github.com/DAIZHENWEI/Ada-BF/blob/master/disjoint_Ada-BF.py>
  - <https://github.com/DAIZHENWEI/Ada-BF/blob/master/learned_Bloom_filter.py>
  - <https://github.com/DAIZHENWEI/Ada-BF/blob/master/PLBF.py>
  - <https://github.com/DAIZHENWEI/Ada-BF/issues>
  - <https://github.com/DAIZHENWEI/Ada-BF/commits/master>
  - <https://raw.githubusercontent.com/DAIZHENWEI/Ada-BF/master/Datasets/URL_data.csv>
  - <https://raw.githubusercontent.com/DAIZHENWEI/Ada-BF/master/Datasets/Malware_data.csv>
  - <https://arxiv.org/pdf/1910.09131>
  - <https://export.arxiv.org/api/query?id_list=1910.09131>
  - <https://proceedings.neurips.cc/paper_files/paper/2020>
  - <https://proceedings.neurips.cc/paper_files/paper/2020/hash/86b94dae7c6517ec1ac767fd2c136580-Abstract.html>
  - <https://proceedings.neurips.cc/paper_files/paper/2020/file/86b94dae7c6517ec1ac767fd2c136580-Paper.pdf>
  - <https://export.arxiv.org/api/query?id_list=2006.03176>
  - <https://arxiv.org/pdf/2006.03176v2>
  - <https://hn.algolia.com/api/v1/search?query=%22Ada-BF%22>
  - <https://hn.algolia.com/api/v1/search?query=adaptive%20learned%20bloom%20filter>
  - <https://matplotlib.org/stable/api/prev_api_changes/api_changes_3.8.0.html>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/daizhenwei/ada-bf`) · [data/wave6/enrich/raw/github_com_daizhenwei_ada_bf.json](../../../data/wave6/enrich/raw/github_com_daizhenwei_ada_bf.json) (enrichment confidence 0.85)

</details>
