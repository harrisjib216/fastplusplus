# Cascaded Learned Bloom Filter (CLBF)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Learned Bloom filter: pruned boosted-tree cascade plus Bloom filters; less memory than Bloom/PLBF, faster rejects than PLBF.

| | |
|---|---|
| **Beats** | Bloom filter |
| **Claimed result** | At the same FPR, CLBF uses up to 17% less memory than the best PLBF configuration, for example on Ember at F=0.005. It cuts reject time by up to 14.6x vs PLBF under the default XGBoost setting, and by up to 65x across the appendix model variants. Construction takes 1.003x-1.23x longer than existing LBFs. A classical Bloom filter (fastfilter_cpp) is plotted as a baseline in Fig. 5, but no CLBF-vs-Bloom ratio is quoted. PLBF is described as the most memory-efficient LBF under a fixed model; G-PLBF matches CLBF on memory vs FPR. |
| **Workload** | Memory-vs-FPR (target F from 0.1 to 0.001) and memory-vs-reject-time trade-offs on the URL, Ember and Higgs datasets (14 datasets in the appendix), using XGBoost models and 10,000 held-out test non-keys. Baselines are all in C++: classical Bloom filter (fastfilter_cpp), PLBF (via Fast PLBF), Sandwiched LBF, G-PLBF, Ensemble LBF, PHBF and HABF. |
| **Metric** | memory |
| **Hardware** | Linux, Intel Core i9-11900H @ 2.50 GHz, 64 GB RAM |
| **Compiler and flags** | GCC 11.4.0 with -O3, single-threaded (paper Section 6); repo builds with CMake Release inside an Ubuntu 22.04 Docker image |
| **Adoption** | 0 stars |
| **Last commit** | 2026-08-24 |
| **Links** | [repository](https://github.com/atsukisato/CascadedLBF) · [benchmark](https://arxiv.org/abs/2502.03696) |

## Verdict

arXiv 2502.03696 v2 setup: Intel i9-11900H, GCC 11.4.0 -O3, single-threaded; 100-round depth-4 XGBoost; 10,000 held-out non-keys. At the same FPR, CLBF used up to 17% less total memory (model plus filters) than the best PLBF configuration (Ember, F=0.005). Its mean reject time was up to 14.6x lower than PLBF's at about 9,250 kB on Higgs, and 65x in an appendix shallow-NN variant. Against the classical fastfilter_cpp Bloom filter it is mostly just plotted; the one quoted number is Kitsune [SSDP] at F=0.01, 3.3 kB vs 1,684 kB, an easy dataset. Reject time includes inference but is measured in a batch over pre-extracted feature vectors, so feature extraction is not counted.

## Use it when

- Static blocklist-style sets whose members are predictable from features: malicious URLs or files, intrusion-traffic signatures (the paper's URL, Ember and Kitsune data). Memory must be scarce and rebuilds rare.
- You would otherwise use a PLBF or Sandwiched LBF with boosted trees and don't want to hand-tune the tree count. CLBF prunes a 100-tree XGBoost model to the depth D that minimizes total memory.
- The filter is a pre-filter in front of an expensive exact lookup and non-key reject latency matters. Lower lambda below 1 to trade memory for faster rejects (lambda=0 falls back to a plain Bloom filter).
- Reproducing or benchmarking learned Bloom filters: Docker scripts rebuild CLBF and C++ baselines (Bloom, PLBF, Sandwiched LBF, G-PLBF, ELBF, PHBF, HABF) on 14 datasets.

## Skip it when

- Keys carry no predictive features (random IDs, hashes). No classifier can separate them, and the optimizer's best case is a plain Bloom filter; use a xor, ribbon or blocked Bloom filter instead.
- The key set changes often. Single-key add() and contains() throw 'Not implemented', and the paper says updates shift the distribution and need a rebuild. Construction includes model training and calibration: even Sandwiched LBF builds 180x-1,100,000x slower than a Bloom filter, and CLBF is 1.003x-1.23x on top of that.
- The query distribution can drift from the calibration non-keys, or is adversarial. The FPR target is met only in expectation on calibration data.
- You need a production library. It is research code with 6 commits and 0 stars, no tests or CI of its own, filter memory that is never freed, hard-coded /tmp scratch files, and headers that link from only one translation unit.
- You need the smallest possible filters: every internal filter is a classical Bloom filter (about 1.44x the information-theoretic bound). The paper says any AMQ could be used, but the code hard-wires Bloom.

## How it is fast

The query runs through a cascade of up to D boosted weak learners. Before each tree, a 'trunk' Bloom filter rejects non-keys without running inference. After each tree, a query whose running score exceeds a threshold exits early to a 'branch' Bloom filter. Queries that survive reach a PLBF-style final stage with K=8 score-partitioned Bloom filters. A dynamic program over discretized FPRs (powers of 0.5, 20 levels) chooses how many trees to keep, which prunes an over-sized ensemble, and sets each filter's FPR. It minimizes lambda\*memory/M_BF + (1-lambda)\*reject_time/R_BF at target FPR F. Thresholds come from quantile candidates, with optional Optuna refinement. The memory saving comes from right-sizing model versus filters; the reject-time saving comes from early rejection, whereas PLBF runs the whole ensemble on every query.

## Compared with alternatives

Over PLBF (kapilvaidya24/PLBF), pick CLBF when your model is a boosted ensemble: at matched memory it rejects up to 14.6x faster and needs up to 17% less memory, with no hand-picked tree count. The paper skipped Ada-BF because PLBF dominates it. Pick non-learned siblings (Xor/xor_singleheader, BuRR, Prefix Filter, ChainedFilter) when keys lack predictive features, the set changes, or you need a maintained library.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | XGBoost C API (libxgboost, dmlc/xgboost git submodule), nlohmann/json, and the vendored fastfilter_cpp Bloom filter (modified for runtime bits-per-key). The experiments additionally need Eigen3 (PHBF baseline) and Python (preprocessing, Optuna variant). |
| **Minimum toolchain** | C++17, CMake 3.12+ for the example; paper and Docker image use GCC 11.4.0 on Ubuntu 22.04; fast range reduction uses __uint128_t (GCC/Clang), with a modulo fallback otherwise |
| **Platforms** | Tested on Linux x86-64 (Docker Ubuntu 22.04; experiments build with -march=native). The example CMake also links libxgboost.dylib on macOS. Hard-coded /tmp paths assume POSIX. |
| **Thread safety** | Not documented. contains_all only reads state. Model load, pruning and configuration write and delete fixed files (/tmp/xgboost_model.bin, /tmp/xgboost_model.json, /tmp/xgboost.json, /tmp/reduced_xgboost.json), so concurrent builds on one host can clobber each other. |
| **Drop-in for the baseline** | no |

## Gotchas

- Every query must pass the exact feature vector used when the key was inserted. The path through the cascade depends on the running score, so changed features can produce a false negative. Keys are uint64; the experiments hash strings with djb2 first.
- The vendored BloomFilter holds a raw new[] array and its destructor is commented out. Filters are never freed, and copying a CLBF (the example does clbf = calibration_manager.configure_lbf_assembly(...)) gives shallow copies that share bit arrays.
- Headers define non-inline functions and a global variable (warn_too_many_false_positives). Include them from exactly one .cpp file, or linking fails with duplicate symbols.
- The custom tree evaluator ignores XGBoost's default_left, so NaN features always go right and scores can differ from XGBoost's own output. Configuration also times a plain Bloom filter (n keys, 1M queries) at build time, so with lambda &lt; 1 the chosen layout depends on the machine.

## Known shortcomings

- Code (Apache-2.0, C++) was found by the verifier at github.com/atsukisato/CascadedLBF; the paper reports GCC 11.4 -O3 on an i9-11900H.
- Research code, not a library: 6 commits, 0 stars, no CI/tests; single add()/contains() throw 'Not implemented' (batch only, static set). The BloomFilter destructor is commented out (never freed; copies share bit arrays); non-inline headers; fixed /tmp scratch files clobber concurrent builds. Needs a trained XGBoost model and per-query feature vectors; changed features cause false negatives.
- The only quoted Bloom comparison is an appendix result on an easy dataset (Kitsune SSDP 3.3 kB vs 1,684 kB); the 17%/14.6x/65x figures are all vs PLBF, and reject time excludes feature extraction.

## Caveats and trade-offs

The record said there was no code, but that was wrong. The official implementation is https://github.com/atsukisato/CascadedLBF (Apache-2.0, C++, Docker-based reproduction scripts for CLBF and all baselines, 0 stars, created 2026-01). The repo_url should be set to it, but that field cannot be corrected here. The paper itself does not link the repo. The headline memory figure is against PLBF, not a classical Bloom filter. Reject time includes ML inference, so a plain Bloom filter may still reject faster. The source is arXiv v2 (2026-08-24), and no peer-review venue was confirmed.

Adds a DP-based size/threshold optimizer at construction time (paper reports this is 0.3-24% of total build time); like other learned filters, needs a trained scoring model and benefits are dataset/model dependent

## Maintenance

Active research code: 6 commits from January to August 2026, 0 stars, no issues, Apache-2.0. You can copy src/ plus the vendored Bloom header and link libxgboost, but it is not a packaged library. The arXiv v2 abstract links this repo.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C. The official code exists at github.com/atsukisato/CascadedLBF (first author's account; the README names the paper). It includes the classical Bloom filter baseline benchmark (experiment/bloom/construct_bloom.cpp, test_bloom.cpp, scripts/bloom/), and docker_run_all.sh reproduces all of the paper's results. Paper Section 6 states GCC 11.4.0, -O3, single-threaded, on an Intel Core i9-11900H @ 2.50 GHz. The quoted 17% figure is against PLBF; the classical Bloom filter appears only as a plotted Fig. 5 baseline.
- **Verifier notes:** The key finding is that code exists: set repo_url to https://github.com/atsukisato/CascadedLBF (owner matches first author Atsuki Sato, who also owns FastPLBF) and rekey the id if the pipeline allows. The quoted 17% is confirmed verbatim (abstract, Section 6, Fig. 5 caption: Ember F=0.005). The record's 'strongest prior baseline' wording is softened because G-PLBF is comparable.
- **Fields the verifier corrected:** `license`, `usability`, `last_commit`, `maintenance_status`, `stars_or_usage`, `compiler_and_flags`, `hardware`, `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2502.03696>
  - <https://arxiv.org/pdf/2502.03696>
  - <https://github.com/atsukisato/CascadedLBF>
  - <https://github.com/atsukisato/CascadedLBF/blob/main/Dockerfile>
  - <https://github.com/atsukisato/CascadedLBF/tree/main/experiment/bloom>
- **Sources the enricher read:**
  - <https://github.com/atsukisato/CascadedLBF>
  - <https://github.com/atsukisato/CascadedLBF/blob/main/README.md>
  - <https://github.com/atsukisato/CascadedLBF/blob/main/.gitmodules>
  - <https://github.com/atsukisato/CascadedLBF/blob/main/src/clbf/clbf.h>
  - <https://github.com/atsukisato/CascadedLBF/blob/main/src/clbf/calibration_manager.h>
  - <https://github.com/atsukisato/CascadedLBF/blob/main/src/clbf/find_optimal_parameters.h>
  - <https://github.com/atsukisato/CascadedLBF/blob/main/src/clbf/lbf_config.h>
  - <https://github.com/atsukisato/CascadedLBF/blob/main/src/bloom/bloom.h>
  - <https://github.com/atsukisato/CascadedLBF/blob/main/src/utils/tree.h>
  - <https://github.com/atsukisato/CascadedLBF/blob/main/src/utils/bloom_io.h>
  - <https://github.com/atsukisato/CascadedLBF/blob/main/src/utils/reduce_xgboost_model.h>
  - <https://github.com/atsukisato/CascadedLBF/blob/main/thirdparty/fastfilter_cpp/src/bloom/bloom.h>
  - <https://github.com/atsukisato/CascadedLBF/blob/main/thirdparty/fastfilter_cpp/src/hashutil.h>
  - <https://github.com/atsukisato/CascadedLBF/blob/main/examples/simple.cpp>
  - <https://github.com/atsukisato/CascadedLBF/blob/main/examples/CMakeLists.txt>
  - <https://github.com/atsukisato/CascadedLBF/blob/main/experiment/CMakeLists.txt>
  - <https://github.com/atsukisato/CascadedLBF/blob/main/experiment/clbf/test_clbf.cpp>
  - <https://github.com/atsukisato/CascadedLBF/blob/main/experiment/utils/str2uint64_hash.h>
  - <https://github.com/atsukisato/CascadedLBF/blob/main/scripts/clbf/construct_clbf.sh>
  - <https://github.com/atsukisato/CascadedLBF/blob/main/scripts/setup.sh>
  - <https://github.com/atsukisato/CascadedLBF/blob/main/Dockerfile>
  - <https://github.com/atsukisato/CascadedLBF/commits/main>
  - <https://github.com/atsukisato/CascadedLBF/issues>
  - <https://arxiv.org/abs/2502.03696>
  - <https://arxiv.org/pdf/2502.03696>
  - <http://export.arxiv.org/api/query?id_list=2502.03696>
  - <https://hn.algolia.com/api/v1/search?query=Cascaded%20Learned%20Bloom%20Filter>
  - <https://api.crossref.org/works?query.bibliographic=Cascaded+Learned+Bloom+Filter+Model-Filter+Size+Balance+Fast+Rejection>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `paper:cascaded-learned-bloom-filter-clbf`) · [data/wave6/enrich/raw/paper_cascaded_learned_bloom_filter_clbf.json](../../../data/wave6/enrich/raw/paper_cascaded_learned_bloom_filter_clbf.json) (enrichment confidence 0.8)

</details>
