# turbovec (Rust TurboQuant vector index with Python bindings)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust (Python bindings)` · `MIT` · 🟢 active

> In-process Rust/Python vector index on 2-4 bit TurboQuant codes; searches 2-5x faster than FAISS IndexPQFastScan at equal bits.

| | |
|---|---|
| **Beats** | FAISS IndexPQFastScan (C++) at a matched bit rate (m = d sub-quantizers, 4-bit codes in the published 4-bit script); FAISS IndexPQ (LUT256, nbits=8) for the recall comparison |
| **Claimed result** | README: 'searches them 4.4x faster than FAISS, at matching recall'; '4.4x FAISS FastScan at 4-bit and 2.2x at 2-bit, on ARM and x86'. README table: search 4-bit '3.8-5.1x faster across the eight cells (ARM 4.0x, x86 4.9x)', search 2-bit '1.8-2.5x faster (ARM 2.05x, x86 2.35x)'. Spot check: benchmarks/results/speed_d1536_4bit_x86_mt.json gives 0.127 vs 0.588 ms/query, 4.6x (derived from page data). Project-recorded losses: whole-file save 1.0-1.4x slower and load to first search 1.0-1.5x slower than FAISS. |
| **Workload** | Search speed: nearest-neighbour search over 100K normalised OpenAI text-embedding-3 vectors (d=1536 and d=3072), k=64, 1K-query batch, median of 5 runs, 2-bit and 4-bit, single- and multi-threaded, on one ARM and one x86 cloud VM (8 cells per bit width). GloVe d=200 appears only in the recall tables, not in the speed runs. |
| **Metric** | throughput |
| **Hardware** | GCP c4a-standard-8 (Google Axion, ARM, 8 vCPUs) and GCP c3-standard-8 (Intel Xeon Platinum 8481C, Sapphire Rapids, 8 vCPUs), from docs/benchmarks.md. |
| **Compiler and flags** | Rust release build. x86_64 builds target x86-64-v2 via .cargo/config.toml, with #[target_feature]-gated AVX-512 and AVX2 kernels chosen at runtime (README). The FAISS version, build (pip wheel variant) and flags are not stated; the benchmarks/suite scripts import the Python faiss module and use the default OpenMP threads, or faiss.omp_set_num_threads(1) in the st scripts. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | Staged bit-plane search: a sign plane is scanned with a nibble-LUT table kernel adapted from FAISS FastScan, a shortlist is ranked on the lower planes, then rescored exactly; AVX-512/AVX2/NEON kernels are selected at runtime. |
| **Adoption** | 17.4k stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/RyanCodrai/turbovec) · [benchmark](https://raw.githubusercontent.com/RyanCodrai/turbovec/HEAD/README.md) |

## Verdict

First-party runs on GCP c4a-standard-8 (Google Axion ARM) and c3-standard-8 (Xeon Platinum 8481C) over 100K normalised OpenAI text-embedding-3 vectors (d=1536 and 3072), k=64, 1,000-query batches, median of 5, both libraries timed through Python. turbovec 1.1.0 was compared with the Python faiss IndexPQFastScan at the same bits per dimension, FAISS version unstated: 3.8-5.1x faster at 4-bit (for example x86, 8 threads, d=1536: 0.127 vs 0.588 ms/query) and 1.8-2.5x at 2-bit. Recall was compared against a different FAISS index (IndexPQ, nbits=8).

## Use it when

- Embedded RAG or semantic search over about 10^4 to a few 10^6 OpenAI-class embeddings (d=768 to 3072) where RAM matters: 75 MB vs 586 MB float32 for 100K x 1536 at 4-bit.
- Indexes that change constantly: single add 7.9-21.7 us and remove 1.4-5.8 us, against 0.19-1.03 s per remove_ids on a FAISS IndexIDMap over IndexPQFastScan, which repacks all codes on each call.
- Streaming data where a PQ codebook would need training and periodic retraining; TurboQuant's codebook comes from the maths, not the data.
- Filtered queries (ACLs, time windows, a SQL or BM25 candidate set) via allowlists or slot masks.
- Servers with AVX-512 VBMI and VNNI (Sapphire Rapids class) or ARM Neoverse (Google Axion), where the staged search runs and the published numbers were measured.

## Skip it when

- Hundreds of millions of vectors or strict tail latency: every query scans the whole index, so cost grows linearly; use HNSW or IVF.
- Sparse, bimodal, one-hot-like or low-dimensional data: open issues #309 (recall drops of up to 65 points on sparse data) and #310 (loses to the FAISS PQ baseline); on GloVe d=200 at 2-bit the uncalibrated index scores R@1 0.550 against FAISS IndexPQ's 0.565.
- x86 hosts without AVX-512 VBMI and VNNI (AVX2-only CPUs): the staged search is off and the whole-index scan runs; no FAISS comparison has been published for such hardware.
- High-concurrency single-query serving with concurrent writers: issue #336 measured reads dropping 40-50% with one writer and almost no gain from Python-level threads (one shared rayon pool).
- You need exact float results, an L2 metric, a network server or replication.

## How it is fast

Data-oblivious quantization: one shared random rotation makes every coordinate follow a known Beta distribution, so the Lloyd-Max scalar codebook is computed analytically, with no training and no rebuilds. Codes are scored with SIMD lookup tables; the x86 kernel adapts FAISS FastScan's pack layout, nibble-LUT scoring and u16 accumulators, and AVX-512, AVX2 or NEON kernels are picked at run time. Since 1.1.0, indexes of 32,768 vectors or more keep bit planes and search in stages: the sign plane (a quarter of the bytes at 4-bit) gives a shortlist, the lower planes rank it, and the best max(64, 1.5k) are rescored exactly. Even before staging, the 1.0.0 whole-index scan was 3.5x FastScan at 4-bit; staging raised that to 4.4x.

## Compared with alternatives

No vector-search siblings are catalogued in numerics-and-arrays; the nearest entries (Gaius.jl, hpla-rs, TriangularSolve.jl) are dense or sparse linear-algebra kernels. Compared with the FAISS incumbent, pick turbovec for a small-footprint, training-free, frequently mutated in-process index; stay on FAISS for IVF or HNSW at large scale, GPUs or L2 metrics.

## Integration

| | |
|---|---|
| **Form** | crate (turbovec) plus a Python extension wheel built with maturin (pip install turbovec) |
| **Dependencies** | Rust: rayon, ordered-float, rand, rand_chacha =0.3.1 and statrs =0.17.1 (exact pins because they shape encoded bytes); Python: numpy&gt;=1.20. FAISS is not needed. |
| **Minimum toolchain** | Rust 1.89 (stabilised AVX-512 intrinsics); Python 3.9+ |
| **Platforms** | x86-64 (x86-64-v2 baseline; AVX2 and AVX-512 kernels dispatched at run time; the staged search needs AVX-512 VBMI and VNNI), aarch64 NEON; wheel classifiers list Linux, macOS and Windows |
| **Thread safety** | Search releases the GIL and runs on one process-wide rayon pool. A fair RwLock means each write blocks the readers behind it (issue #336). sync() supports one writer per file path. |
| **Drop-in for the baseline** | no |

## Gotchas

- The headline speed figures predate a recall fix. The speed JSONs were last regenerated 2026-10-04 (#552, release 1.1.0). Release 1.1.2 (2026-10-06, #562) fixed the 1.1.0 staged search losing recall on corpora whose vectors share a strong common direction (MedCPT k=10 recall 0.931 vs the full scan's 0.944, with the true nearest neighbour sometimes missing). The wider stages cost up to 3% at 4-bit and 7-12% at 2-bit (k=10), or 2-5% from k=32, and the CHANGELOG says the README figures will be refreshed later.
- Harness: at 4-bit the FAISS comparator is IndexPQFastScan(d, m=d, 4), i.e. one-dimensional sub-quantizers. It runs with the default L2 metric and no refine, its version is unpinned (no benchmarks/requirements.txt), and its recall is never measured: the recall tables use IndexPQ(m=d/2, nbits=8). Most of the 4-bit gap predates staging; on x86 at one thread, 1,000-query batches and k=64, the whole-index scan takes 0.701 ms per query against FAISS's 2.518 ms, about 3.6x (derived from page data).
- The staged search returns exact scores but an approximate id set. On structureless random vectors it misses most of the exact top-k. Set TURBOVEC_4BIT_PLANES=0 or TURBOVEC_2BIT_PLANES=0 before the first search to force the whole-index scan. Staging only applies to indexes of 32,768 vectors or more, with dims a multiple of 32.
- Masks name slots, so any mutation, swap_remove included, silently invalidates a mask; use IdMapIndex allowlists instead. bit_width=3 is stored in 4-bit fields (issue #561), and the AVX-512 kernels are not run in CI (issue #282).

## Known shortcomings

- FAISS version and build unstated; a staged bit-plane scan is compared with the full IndexPQFastScan without refine; 'matching recall' was measured against a different index (IndexPQ nbits=8), never against the timed FastScan; GloVe is absent from the speed runs.
- The headline 4.4x/2.2x speed JSONs were last regenerated 2026-10-04 (1.1.0, #552), before the 1.1.2 recall fix (#562, 2026-10-06: the staged search lost recall on bunched corpora); the fix costs up to 3% at 4-bit and 7-12% at 2-bit, and the CHANGELOG admits the README figures predate it. The FAISS comparator is IndexPQFastScan(d, m=d, 4) with 1-D sub-quantizers, recall never measured and version unpinned; most of the gap predates staging (whole-index scan already 3.5x in 1.0.0; x86 1 thread k=64 0.701 vs 2.518 ms). The staged path needs AVX-512 VBMI plus VNNI on x86 (AVX2 hosts unbenchmarked). Open issues #309/#310 (recall losses on sparse or bimodal data), #336 (writer contention), #282 (AVX-512 kernels not run in CI).

## Caveats and trade-offs

Not the same algorithm. turbovec runs a staged search: one bit plane scanned with a table kernel, a shortlist ranked on the lower planes, the best rescored exactly, so the first stage reads about a quarter of the 4-bit code bytes. The speed comparator, faiss.IndexPQFastScan(d, m=d, 4) with the default L2 metric and no refinement, scans every code. 'At matching recall' is not supported for the speed comparator. FastScan's recall is never measured, the recall tables compare against a different index (IndexPQ m=d/2, nbits=8), the speed runs use an uncalibrated index, and the README recall row reports the calibrated TQ+. Per docs/benchmarks.md, the calibrated index trails FAISS by 0.7 points at R@1 for d=1536 4-bit, and GloVe d=200 is the harder regime. The author ran it on cloud VMs; the FAISS version and build are not stated; timings include Python call overhead on both sides. The x86 kernel adapts FAISS FastScan's pack layout, nibble-LUT scoring and u16 accumulators. Vector search sits at the edge of the numerics-and-arrays category; the orchestrator may re-file it. [retier] The headline speed JSONs were last regenerated 2026-10-04 (1.1.0), before the 1.1.2 recall fix (#562: the staged search lost recall on bunched corpora), which costs up to 3% at 4-bit and 7-12% at 2-bit; the CHANGELOG admits the README figures predate it. The FAISS comparator is IndexPQFastScan(d, m=d, 4) with 1-D sub-quantizers, recall never measured and version unpinned. The staged path needs AVX-512 VBMI plus VNNI on x86 (AVX2 hosts unbenchmarked). Open issues #309/#310 (recall losses), #336 (writer contention), #282 (AVX-512 kernels not run in CI).

Brute-force scan of every vector with no graph index, so query cost grows linearly with corpus size (README advises another index for hundreds of millions of vectors); lossy 2- and 4-bit quantization; Python-facing API; atomic save and load are slower than FAISS write_index/read_index.

## Maintenance

Very active (1.1.2 on 2026-10-06, 376 commits, 22 open issues, 17.4k stars), but the PyPI classifier still says 'Development Status :: 3 - Alpha' and the file format has moved to v8 (1.0.0 cannot read v8 files); MIT and copyable. Treat the 4.4x/2.2x figures as first-party numbers measured before the 1.1.2 recall fix, against an unpinned FAISS comparator whose recall was never checked.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** The README and docs/benchmarks.md carry the claimed numbers, and the benchmark code is public (benchmarks/suite/speed_\*.py, with results JSON in benchmarks/results/), with the CPUs named. It falls short of A: the FAISS side is the Python faiss module, and its version, build and flags are stated nowhere (no requirements pin). The numbers are first-party, so the tier is C.
- **Verifier notes:** Downgrade A to C. Shortcomings: the FAISS version and build are unstated; the win is algorithmic (a staged bit-plane scan against a full FastScan scan with no refine); 'matching recall' is measured against a different FAISS index (IndexPQ nbits=8) and never against the timed FastScan; GloVe is not in the speed runs. Metadata checked: MIT, 17.4k stars, last commit 2026-10-06, not a fork; not a wrapper of FAISS, so not a duplicate.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-79 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/RyanCodrai/turbovec/HEAD/README.md>
  - <https://raw.githubusercontent.com/RyanCodrai/turbovec/HEAD/docs/benchmarks.md>
  - <https://raw.githubusercontent.com/RyanCodrai/turbovec/HEAD/benchmarks/suite/speed_d1536_4bit_x86_mt.py>
  - <https://raw.githubusercontent.com/RyanCodrai/turbovec/HEAD/benchmarks/suite/speed_d1536_4bit_x86_st.py>
  - <https://raw.githubusercontent.com/RyanCodrai/turbovec/HEAD/benchmarks/results/speed_d1536_4bit_x86_mt.json>
  - <https://raw.githubusercontent.com/RyanCodrai/turbovec/HEAD/benchmarks/suite/recall_d1536_4bit.py>
  - <https://raw.githubusercontent.com/RyanCodrai/turbovec/HEAD/benchmarks/results/recall_d1536_4bit.json>
  - <https://raw.githubusercontent.com/RyanCodrai/turbovec/HEAD/benchmarks/results/recall_glove_4bit.json>
  - <https://raw.githubusercontent.com/RyanCodrai/turbovec/HEAD/benchmarks/results/recall_glove_2bit.json>
  - <https://github.com/RyanCodrai/turbovec>
  - <https://github.com/RyanCodrai/turbovec/commits/main>
  - <https://github.com/RyanCodrai/turbovec/tree/main/benchmarks/suite>
  - <https://github.com/RyanCodrai/turbovec/tree/main/benchmarks>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/RyanCodrai/turbovec/HEAD/README.md>
  - <https://raw.githubusercontent.com/RyanCodrai/turbovec/HEAD/docs/benchmarks.md>
  - <https://raw.githubusercontent.com/RyanCodrai/turbovec/HEAD/docs/api.md>
  - <https://raw.githubusercontent.com/RyanCodrai/turbovec/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/RyanCodrai/turbovec/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/RyanCodrai/turbovec/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/RyanCodrai/turbovec/HEAD/turbovec/Cargo.toml>
  - <https://raw.githubusercontent.com/RyanCodrai/turbovec/HEAD/turbovec-python/pyproject.toml>
  - <https://raw.githubusercontent.com/RyanCodrai/turbovec/HEAD/benchmarks/suite/speed_d1536_4bit_x86_mt.py>
  - <https://raw.githubusercontent.com/RyanCodrai/turbovec/HEAD/benchmarks/suite/speed_d1536_2bit_arm_st.py>
  - <https://raw.githubusercontent.com/RyanCodrai/turbovec/HEAD/benchmarks/suite/recall_d1536_4bit.py>
  - <https://raw.githubusercontent.com/RyanCodrai/turbovec/HEAD/benchmarks/results/speed_d1536_4bit_x86_mt.json>
  - <https://raw.githubusercontent.com/RyanCodrai/turbovec/HEAD/benchmarks/results/speed_d1536_4bit_x86_st.json>
  - <https://raw.githubusercontent.com/RyanCodrai/turbovec/HEAD/benchmarks/results/speed_d1536_2bit_arm_st.json>
  - <https://raw.githubusercontent.com/RyanCodrai/turbovec/HEAD/benchmarks/results/recall_d1536_4bit.json>
  - <https://raw.githubusercontent.com/RyanCodrai/turbovec/HEAD/benchmarks/results/recall_d1536_2bit.json>
  - <https://raw.githubusercontent.com/RyanCodrai/turbovec/HEAD/benchmarks/results/recall_glove_2bit.json>
  - <https://raw.githubusercontent.com/RyanCodrai/turbovec/HEAD/benchmarks/requirements.txt>
  - <https://github.com/RyanCodrai/turbovec>
  - <https://github.com/RyanCodrai/turbovec/commits/main/benchmarks/results/speed_d1536_4bit_x86_mt.json>
  - <https://github.com/RyanCodrai/turbovec/issues>
  - <https://github.com/RyanCodrai/turbovec/issues/336>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/ryancodrai/turbovec`) · [data/wave14/enrich/raw/github_com_ryancodrai_turbovec.json](../../../data/wave14/enrich/raw/github_com_ryancodrai_turbovec.json) (enrichment confidence 0.75)

</details>
