# libpostal

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Text search and indexing](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🟢 active

> C library that parses and normalizes street addresses worldwide with a CRF; about 10-65x faster per address than Deepparse's neural parser.

| | |
|---|---|
| **Beats** | Deepparse (GRAAL-Research neural address parser; fastText, fastText-light, BPEmb and attention variants, GPU and CPU) |
| **Claimed result** | libpostal about 0.00004 s per address vs Deepparse fastText about 0.0004 s (GPU, batch of more than 1; about 10x, derived from page data) and about 0.0026 s (CPU, batch of more than 1; about 65x, derived from page data); Deepparse batch-of-1 figures are 0.0023 s (GPU) and 0.0128 s (CPU), and its slowest variant, BPEmbAttention on CPU, 0.0286 s at batch 1. libpostal's own README separately says it processes 10-30k addresses per second per thread. |
| **Workload** | Parse about 183,000 multinational street addresses and report mean time per address (total time / 183,000); Deepparse run with batch sizes 1 to 512 on a GPU and on a CPU, libpostal run without batching. |
| **Metric** | latency |
| **Hardware** | Linux, Python 3.11, Torch 2.0, CUDA 11.7 (run 2023-03-21); the paper snippet names an RTX 2080 GPU; the CPU model is not given on the docs page |
| **Adoption** | 4.9k stars; widely bound from Python, Go, Ruby, Node and others (pypostal etc.) |
| **Last commit** | 2025-12-06 |
| **Links** | [repository](https://github.com/openvenues/libpostal) · [benchmark](https://raw.githubusercontent.com/GRAAL-Research/deepparse/main/docs/source/parser.rst) |

## Verdict

Deepparse's authors (a competing project) timed about 183,000 multinational addresses on Linux with Python 3.11, Torch 2.0 and CUDA 11.7 on 2023-03-21 (an RTX 2080 GPU per their paper's search snippets; CPU model, libpostal version and build flags not stated): libpostal via pypostal took about 0.00004 s per address, against Deepparse fastText at about 0.0004 s on GPU and 0.0026 s on CPU when batched (about 10x and 65x, derived from page data) and 0.0023 s and 0.0128 s at batch size 1. The libpostal row is a single unbatched number reused in both tables, so the comparison mixes a CRF in a Python loop with neural models at varying batch sizes.

## Use it when

- Batch normalization, deduplication or geocoder preprocessing of millions of addresses on CPUs, where a CPU-only throughput of thousands to tens of thousands of addresses per second per process is enough and no GPU is available.
- Multilingual, multinational address data (trained on over 1 billion OSM and OpenAddresses records covering every inhabited country) where per-country rule sets are not maintainable.
- Building fuzzy address matching on top of a normal search engine or hash table: expand once at index time and once at query time.
- Calling from Python, Go, Ruby or Node in-process through an existing binding, instead of standing up a separate model server.
- US, UK and Singapore-heavy data, where the optional Senzing model (MODEL=senzing) reports 4.3 percent better parses on Senzing's own test set.

## Skip it when

- Memory- or disk-constrained deployments: the default model is about 1.8 GB (2.2 GB for Senzing) and a parser process sits near 1.9 GB RSS (issue #676 pmap figures); serverless hosts such as AWS Lambda are an open question (issue #538).
- Multithreaded in-process parsing: the library keeps one global parser with a single shared context and CRF scratch buffers, 'Make libpostal thread safe' (#34) has been open since 2016 and #102 reports SIGSEGV with 8 threads; scale with processes, which multiplies the memory cost.
- Untrusted input without a timeout: a single invalid UTF-8 byte 0xC6 makes parse_address spin at 100 percent CPU in scan_token (#460, open), and invalid characters can drive tokenize_add_tokens into an endless loop and OOM (#548, open).
- Windows-first or Apple Silicon builds: Windows needs MSYS2 and MinGW with several open build issues, and ARM builds disable SSE2, which the README says gives poorer performance.
- When you need to retrain or fine-tune on your own address style cheaply: Deepparse is built for that, while libpostal's training pipeline works on a 100 GB-plus corpus.

## How it is fast

Parsing is a linear-chain Conditional Random Field decoded with Viterbi over sparse, hand-engineered features (normalized word, dictionary phrase membership, postal-code and admin context), so each address costs a few sparse dot products per token instead of the embedding lookups and recurrent network passes of a neural tagger; an older greedy averaged-perceptron model format is still loadable. Dictionaries live in double-array tries, weights in compressed sparse matrices and most other data in contiguous arrays, all loaded once at setup. On x86 the build enables SSE2 math routines by default. The README itself says the design optimizes memory first and speed last.

## Compared with alternatives

None of the catalogued siblings parse addresses: use libpostal to parse and expand addresses before indexing them in Tantivy, Manticore or PISA, and pick it over RapidFuzz when matching must understand address abbreviations, transliteration and component structure rather than raw string similarity.

## Integration

| | |
|---|---|
| **Form** | shared lib (autotools build of libpostal.so / .a) plus separately downloaded model data |
| **Dependencies** | autoconf, automake, libtool, pkg-config and curl to build; about 1.8 GB of model data fetched at install (or --disable-data-download); optional CBLAS if cblas.h is found; packages exist in Homebrew and MacPorts |
| **Minimum toolchain** | C99 (AC_PROG_CC_C99); library built at -O2, tools at -O3, scanner always at -O0 |
| **Platforms** | Linux and macOS supported; Windows only via MSYS2/MinGW ('not a priority'); x86 gets -msse2 -DUSE_SSE by default, arm64/aarch64 builds skip SSE2 automatically or need --disable-sse2 on M1 |
| **Thread safety** | Not thread-safe: libpostal_parse_address reuses one global address_parser_context and the CRF's single context and Viterbi buffer on every call; serialize calls with a mutex or use one process per core (issues #34, #102). |
| **Drop-in for the baseline** | no |

## Gotchas

- The README's '10-30k addresses / second in a single thread' points to src/bench.c, which times libpostal_expand_address (normalization, not the parser) on one command-line string repeated 100,000 times with clock(); it is not a parse_address throughput figure on varied input. The Deepparse run's 0.00004 s per parse (about 25,000 per second, derived from page data) is the only independent parser number.
- Harness flaws in the cited Deepparse comparison: libpostal was timed through pypostal in a Python loop inside memory_profiler's @profile, whose line tracing takes a memory sample on each executed line, so the libpostal figure is pessimistic; Deepparse's committed speed_test_evaluation.py calls process_fn() without its required batch_size argument (a TypeError as written) and reopens its result file in 'w' mode on every batch size; the 'batch of more than 1' column is a mean over batch sizes 2-512, and the GPU fastText-light row shows that mean (0.0037 s) slower than batch 1 (0.0028 s).
- Before 1.1.4 (fix of 2025-10-18, #676) context-&gt;separators was never cleared between parses, so RSS grew about 20-30 MB per 500,000 parses; the array is not read by the parser's feature function in the current source, so parse results were not affected, but long-running services on older builds (including whatever version the 2023 benchmark used) leak.
- Issue #597 reported out-of-bounds writes in the SSE path (remez9_0_log2_sse assumes buffers are multiples of 4 doubles and realloc ignores alignment); it is closed (2024) but the issue page does not show the fix, so test SSE builds under a sanitizer if you vendor an older release.

## Known shortcomings

- Tier B on the Deepparse docs (parser.rst: libpostal about 0.00004 s per address vs fastText 0.0004 s GPU batched and 0.0026 s CPU batched; code public in models_evaluation/speed_test_evaluation_libpostal.py), but Deepparse is an off-baseline neural competitor (353 stars), libpostal was timed through pypostal under memory_profiler, CPU model and build unstated, the committed Deepparse script is broken (process_fn() missing an argument), the docs cite no paper for the timing, and the text-search-and-indexing category is loose. NLP-OSS 2023 paper (RTX 2080) seen only in snippets.
- Enricher: the README's '10-30k addresses/s' comes from src/bench.c, which times expand_address on one repeated string, not the parser; in the Deepparse harness libpostal ran under memory_profiler's @profile (pessimistic), speed_test_evaluation.py calls process_fn() without batch_size (TypeError), and GPU fastText-light at batch&gt;1 (0.0037 s mean) was slower than batch 1 (0.0028 s). Not thread-safe (one global parser context, #34 open since 2016, #102 SIGSEGV); 0xC6 single byte infinite loop (#460 open) and endless loop with OOM (#548 open); about 1.9 GB RSS per process; pre-1.1.4 separators leak (#676); SSE out-of-bounds writes reported (#597, closed 2024, fix not shown).

## Caveats and trade-offs

Independent measurement by the Deepparse authors (competitors, not the libpostal team). The numbers are in Deepparse's docs (docs/source/parser.rst); that page does not cite a paper for the timing tables (its arXiv link, 2006.16152, is the 2020 accuracy paper). Search snippets (snippet only; arXiv and ACL Anthology blocked) say the NLP-OSS 2023 paper 'Deepparse: An Extendable, and Fine-Tunable State-Of-The-Art Library for Parsing Multinational Street Addresses' (arXiv 2311.11846, ACL Anthology 2023.nlposs-1.3) reports the same experiment in Tables 1-2 on an RTX 2080 GPU and states that libpostal had the better inference time. The benchmark code is public in GRAAL-Research/deepparse models_evaluation/: libpostal was timed through the pypostal Python binding (postal.parser.parse_address in a Python loop over \~183,000 addresses, wall-clock time.time()), not from C, and both runs are wrapped in memory_profiler's @profile, whose line tracing adds overhead to the libpostal loop, so the libpostal figure is if anything pessimistic. The committed speed_test_evaluation.py calls process_fn() without its batch_size argument and reopens its result file inside the batch loop, so it cannot have produced the Deepparse rows as written; its 'batch of more than 1' column is the mean over batch sizes 2 to 512, not the best batch. The CPU model, libpostal version, data model and build flags are not stated (run 2023-03-21: Linux, Python 3.11, Torch 2.0, CUDA 11.7). The libpostal row has a single number (repeated in the GPU and CPU tables; RAM and batch-1 cells are N/A), so ratios against Deepparse's batch-of-1 column are not like for like. Off-baseline: Deepparse (353 stars, LGPL-3.0) is a neural parser aimed at accuracy on noisy multinational addresses, not an incumbent; libpostal is itself the incumbent for address parsing, and its own README claims 10-30k addresses per second per thread with a simple benchmark program but publishes no comparison. 0.00004 s per address equals 25,000 addresses per second (derived from page data), consistent with that README claim. Category fit is loose: address parsing and normalization filed under text-search-and-indexing.

Needs about 1.8 GB of downloaded model data (2.2 GB for the Senzing model); no batching API; trades memory and data size for speed. README reports 99.45 percent full-parse accuracy on held-out OSM data; the README says it optimizes memory first and performance last.

## Maintenance

Maintained at a slow cadence by the original author (releases 1.1.0 to 1.1.4 in September-October 2025, Senzing data v1.2.0 merged 2025-12-06, many 2019-2023 bug reports still open); MIT-licensed code, copyable, but it needs the separately downloaded \~1.8 GB model, is not thread-safe, and the cited speed comparison comes from a competitor's harness with the flaws listed under gotchas (pessimistic for libpostal, broken script for Deepparse).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent measurement by the Deepparse authors: the docs table (libpostal \~0.00004 s/address vs fastText \~0.0004 s GPU and \~0.0026 s CPU) is backed by public code (models_evaluation/speed_test_evaluation_libpostal.py and speed_test_evaluation.py) and, per search snippets, by Tables 1-2 of their peer-reviewed NLP-OSS 2023 paper (RTX 2080 GPU); not A because the CPU model and libpostal build are unstated and the committed Deepparse timing script does not run as written.
- **Verifier notes:** Numbers verified on parser.rst (libpostal \~0.00004 s; fastText GPU 0.0023/0.0004, CPU 0.0128/0.0026; BPEmbAttention CPU batch-1 0.0286). Shortcomings: off-baseline (Deepparse is a niche neural competitor, not an incumbent), libpostal timed via pypostal Python binding under memory_profiler, CPU model and libpostal build unstated, committed Deepparse speed script broken (process_fn() missing argument), paper only via search snippets, loose category. Metadata checked: MIT, 4.9k stars, not fork or archived, last commit 2025-12-06, active.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-19 (wave 3); enricher (wave 3)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/GRAAL-Research/deepparse/main/docs/source/parser.rst>
  - <https://github.com/openvenues/libpostal>
  - <https://github.com/openvenues/libpostal/commits>
  - <https://raw.githubusercontent.com/openvenues/libpostal/HEAD/README.md>
  - <https://github.com/GRAAL-Research/deepparse>
  - <https://github.com/GRAAL-Research/deepparse/tree/main/models_evaluation>
  - <https://raw.githubusercontent.com/GRAAL-Research/deepparse/main/models_evaluation/speed_test_evaluation_libpostal.py>
  - <https://raw.githubusercontent.com/GRAAL-Research/deepparse/main/models_evaluation/speed_test_evaluation.py>
  - <https://raw.githubusercontent.com/GRAAL-Research/deepparse/main/models_evaluation/evaluation_requirements.txt>
  - <https://raw.githubusercontent.com/GRAAL-Research/deepparse/main/models_evaluation/timer/timer.py>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/openvenues/libpostal/HEAD/README.md>
  - <https://raw.githubusercontent.com/openvenues/libpostal/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/openvenues/libpostal/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/openvenues/libpostal/HEAD/src/Makefile.am>
  - <https://raw.githubusercontent.com/openvenues/libpostal/HEAD/src/libpostal.h>
  - <https://raw.githubusercontent.com/openvenues/libpostal/HEAD/src/libpostal.c>
  - <https://raw.githubusercontent.com/openvenues/libpostal/HEAD/src/address_parser.c>
  - <https://raw.githubusercontent.com/openvenues/libpostal/HEAD/src/address_parser.h>
  - <https://raw.githubusercontent.com/openvenues/libpostal/HEAD/src/crf.c>
  - <https://raw.githubusercontent.com/openvenues/libpostal/HEAD/src/averaged_perceptron.c>
  - <https://raw.githubusercontent.com/openvenues/libpostal/HEAD/src/address_parser_test.c>
  - <https://raw.githubusercontent.com/openvenues/libpostal/HEAD/src/bench.c>
  - <https://raw.githubusercontent.com/openvenues/pypostal/master/postal/pyparser.c>
  - <https://github.com/openvenues/libpostal/commits>
  - <https://github.com/openvenues/libpostal/issues?q=is%3Aissue+thread+safe>
  - <https://github.com/openvenues/libpostal/issues?q=is%3Aissue+is%3Aopen+segfault+OR+crash+OR+overflow+OR+slow+OR+memory>
  - <https://github.com/openvenues/libpostal/issues/34>
  - <https://github.com/openvenues/libpostal/issues/102>
  - <https://github.com/openvenues/libpostal/issues/460>
  - <https://github.com/openvenues/libpostal/issues/597>
  - <https://github.com/openvenues/libpostal/issues/676>
  - <https://raw.githubusercontent.com/GRAAL-Research/deepparse/main/docs/source/parser.rst>
  - <https://raw.githubusercontent.com/GRAAL-Research/deepparse/main/models_evaluation/speed_test_evaluation_libpostal.py>
  - <https://raw.githubusercontent.com/GRAAL-Research/deepparse/main/models_evaluation/speed_test_evaluation.py>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/openvenues/libpostal`) · [data/wave3/enrich/raw/github_com_openvenues_libpostal.json](../../../data/wave3/enrich/raw/github_com_openvenues_libpostal.json) (enrichment confidence 0.75)

</details>
