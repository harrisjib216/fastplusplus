# BLARE (Blazingly Fast Regular Expression)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Regex engines](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `C++` · `no license` · 🟡 stale

> Research framework that decomposes regexes into reordered sub-matches via a bandit-picked plan, layered on RE2/PCRE2/Boost/ICU.

| | |
|---|---|
| **Beats** | RE2 |
| **Claimed result** | 1.6x-3.7x faster than RE2; 3.4x-7.9x faster than Boost Regex; 3.1x to over 100x faster than PCRE2 (as reported in the paper abstract) |
| **Workload** | Regex matching over 2 Microsoft-internal production workloads and 1 public workload (US-Accidents Kaggle dataset), decomposing each regex into components evaluated via a multi-armed-bandit-selected, non-left-to-right execution plan, implemented on top of RE2, PCRE2, Boost Regex, and ICU Regex |
| **Metric** | throughput |
| **Hardware** | Azure Standard_E32-16ds_v5 VM: Intel Xeon Platinum 8370C @ 2.80GHz, 16 vCPUs, 256 GB RAM, 1 TB disk; single-threaded runs (paper Sec. 5.1) |
| **Compiler and flags** | C++17 compiled with -O3 (paper Sec. 5.1); compiler named only in repo README as g++ &gt;= 8.4.0, exact version not stated. Library versions: RE2 09-20-2022, PCRE2 10.40 via JPCRE2 10.32.01 with JIT, ICU4C 72.1, Boost 1.65.1 |
| **Adoption** | 9 stars |
| **Last commit** | 2023-11-20 |
| **Links** | [repository](https://github.com/mush-zhang/Blare) · [benchmark](https://dl.acm.org/doi/10.1145/3589297) |

## Verdict

The peer-reviewed paper (Proc. ACM Manag. Data 1(2), Art. 152, SIGMOD 2023), run single-threaded on an Azure Xeon Platinum 8370C VM with C++17 code at -O3, reports BLARE 1.6x-3.7x faster than RE2 (09-2022 build), 3.4x-7.9x faster than Boost 1.65.1, and 3.1x to over 100x faster than PCRE2 10.40/JIT, across 2 Microsoft-internal production log workloads and the public US-Accidents Kaggle dataset; only the RE2/US-Accidents comparison (\~1.6x) can be independently rerun from the public repo, and the ACM DOI page returns HTTP 403 to automated fetches (paper is mirrored as BLARE.pdf in the repo).

## Use it when

- Batch, single-threaded scanning of many lines against one recurring regex (e.g. log parsing, dataset filtering) where the bandit can amortize warm-up
- You already depend on RE2, PCRE2, Boost.Regex, or ICU Regex and want extra throughput without switching engines
- Regexes with decomposable structure (alternations, literal anchors) that benefit from evaluating a cheap/selective piece first
- Reproducing or extending the SIGMOD 2023 paper's results, using original_codebase/BLARE_CODE for exact numbers
- First-match-per-line extraction workloads similar to the paper's US-Accidents / production log benchmarks

## Skip it when

- Any production dependency requiring maintenance or support: last commit 2023-11-20, 9 stars, 0 forks, no CI visible
- Anywhere licensing matters: no LICENSE file, so GitHub marks it all-rights-reserved by default
- Environments that can't add Abseil, Boost &gt;=1.65.1, ICU4C, and PCRE2/jPCRE2 as build dependencies
- Multi-threaded or latency-sensitive services: paper benchmarks are single-threaded only; thread safety is not documented
- Anything needing the exact paper numbers from current main: README states main-branch code 'may not produce results identical to that in the BLARE paper'
- Non-Linux targets: build instructions are Ubuntu/apt-based and the original experiment flags use -march=native, tying binaries to the build host's CPU

## How it is fast

The regex is split (3-way split_regex or N-way split_regex_multi) into sub-patterns, and a multi-armed-bandit policy picks which sub-pattern to evaluate first based on observed cost/selectivity, so cheap or highly discriminating fragments reject non-matching lines before the full pattern is ever run through the underlying engine. Because the same regex is reused across many lines (log/dataset scanning), the bandit amortizes its exploration cost and converges on a near-optimal evaluation order for that workload; the final per-fragment match still calls the wrapped engine (RE2/PCRE2/Boost/ICU), so BLARE is an execution-order optimizer on top of those engines, not a replacement matcher.

## Compared with alternatives

Pick BLARE over re2jit or rejit only when the goal is specifically reproducing or studying the SIGMOD 2023 decomposition/bandit technique on RE2, PCRE2, Boost, or ICU; for a production RE2 speedup, re2jit is the safer sibling (20-30% faster on capture-group workloads, no extra Abseil/Boost/ICU/PCRE2 dependency chain) since BLARE is stale and unlicensed.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Abseil, Boost (&gt;=1.65.1), RE2, PCRE2 10.40 via jPCRE2 (JIT), ICU4C 72, CMake (&gt;=3.14), git-lfs for the sample dataset |
| **Minimum toolchain** | C++17, g++ 8.4.0+, CMake 3.14+ |
| **Platforms** | Linux/Ubuntu per documented build steps; macOS/Windows not documented; original experiment binaries built with -march=native are host-CPU-specific |
| **Thread safety** | not documented — all reported benchmarks are single-threaded |
| **Drop-in for the baseline** | partial — explain: wraps RE2/PCRE2/Boost/ICU internally but exposes its own free functions (e.g. BlareRE2(lines, reg_string) -&gt; tuple) per backend rather than each engine's native API, so callers must adopt BLARE's function signatures instead of swapping a header |

## Gotchas

- Main-branch code is under active change and the README itself warns it may not reproduce the paper's numbers; use original_codebase/BLARE_CODE for that
- No LICENSE file is present (GitHub reports 'license: none'), so usage/redistribution rights are unclear by default
- The bundled US-Accidents CSV requires 'git lfs pull'; a newer Kaggle CSV format breaks the hard-coded read_traffic parser and needs manual edits
- Two of the three paper workloads (DB-X, System-Y) are Microsoft-internal logs and cannot be rerun outside Microsoft; only the 1.6x-vs-RE2 US-Accidents result is publicly reproducible

## Caveats and trade-offs

No LICENSE file (GitHub license: none), so the code is all-rights-reserved by default. Two of the three workloads (DB-X, System-Y) are Microsoft-internal production logs; only the US-Accident result (1.6x vs RE2) can be reproduced with the public original_codebase/BLARE_CODE, and the 3.7x RE2 figure comes from the proprietary DB-X workload. Numbers are single-threaded first-match-per-line extraction; exact compiler version is not stated. The ACM DL page returns HTTP 403 to fetchers, but the same paper is in the repo as BLARE.pdf. Only 9 stars and no commits since 2023-11-20.

Research prototype built as a layer on top of RE2/PCRE2/Boost/ICU rather than a standalone engine; requires linking Abseil, Boost, ICU, and PCRE2; the repo's own README warns the current main-branch code 'may not produce results identical to that in the BLARE paper' and points to a separate original_codebase/BLARE_CODE folder to reproduce the exact published numbers

## Maintenance

Stale research prototype (last commit 2023-11-20, 9 stars, no LICENSE) — useful as a reference implementation of the decompose-and-reorder technique, not something to take a runtime dependency on.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed paper (Proc. ACM Manag. Data 1(2), Art. 152, SIGMOD 2023) whose abstract states 1.6x-3.7x vs RE2, 3.4x-7.9x vs Boost, 3.1x to &gt;100x vs PCRE2. Sec. 5.1 gives CPU (Xeon Platinum 8370C) and -O3, but the compiler version is not stated and 2 of 3 workloads are Microsoft-internal, so not A.
- **Verifier notes:** Read the full paper from BLARE.pdf in the repo (ACM DOI page 403). Abstract numbers match the record exactly; the paper also reports 61.7x for ICU on US-Accident. Metadata (no license, 9 stars, last commit 2023-11-20, stale) verified.
- **Fields the verifier corrected:** `hardware`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://dl.acm.org/doi/10.1145/3589297>
  - <https://github.com/mush-zhang/Blare>
  - <https://github.com/mush-zhang/Blare/blob/main/BLARE.pdf>
  - <https://github.com/mush-zhang/Blare/tree/main/original_codebase>
- **Sources the enricher read:**
  - <https://github.com/mush-zhang/Blare>
  - <https://github.com/mush-zhang/Blare/blob/main/README.md>
  - <https://github.com/mush-zhang/Blare/blob/main/include/blare.hpp>
  - <https://github.com/mush-zhang/Blare/blob/main/include/blare_re2/blare.hpp>
  - <https://github.com/mush-zhang/Blare/blob/main/include/misc/split_regex.hpp>
  - <https://github.com/mush-zhang/Blare/blob/main/include/blare_re2/split_match_multiway.hpp>
  - <https://github.com/mush-zhang/Blare/blob/main/original_codebase/README.md>
  - <https://github.com/mush-zhang/Blare/issues>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/mush-zhang/blare`) · [data/wave3/enrich/raw/github_com_mush_zhang_blare.json](../../../data/wave3/enrich/raw/github_com_mush_zhang_blare.json) (enrichment confidence 0.6)

</details>
