# Wave 11 leads for a seed pass

Candidates surfaced by verifiers and enrichers, not yet in any wave's records.
- tidwall/bluebox (Neco Redis clone): README memtier numbers on a Ryzen 9 5950X, 493,346 ops/s against redis-server 207,735 (about 2.4x, derived from page data); app-level, first-party. Surfaced by the Neco enricher.
- dsx-ai-factory/model-streamer: the Run:ai Model Streamer repo moved here; check whether the old id should fold into it.
- google/nsync (the Apache-2.0 mutex library behind Cosmopolitan's pthread_mutex_t fast path): not catalogued (wave 11 batch 51 verifier, 2026-10-07); seed candidate.
- Kokkos (wave 11, kokkos/kokkos): arXiv 2411.05009 PIC paper, C to B once the PDF is reachable.
- whippet (wingo/whippet): embeddable GC in C (MIT) with a bdw backend and mt-gcbench derived from GCBench; README has no numbers (enricher lead, 2026-10-07).
- sse-popcount (WojciechMula/sse-popcount): BSD-2-Clause, 357 stars, results/ directory with per-CPU popcount numbers; positional popcount (Clausecker/Lemire, arXiv 2412.16370). Leads from the libpopcnt enrichment (2026-10-07).
- tbox retier lead (https://github.com/tboox/tbox, coroutines-fibers): benchbox wiki channel page gives buffered channel 293 ms vs Go 782 ms vs libmill 1135 ms (first-party, tier C either way); fold into the existing tbox record's claim when next retiering (w1-mine-ae backfill, 2026-10-07).

## Backfill round 2, 2026-10-11 (seeds w11-mine-e to o)
- RaftLib: PMAM 2015 / IJHPCA 2016 paper (vs GNU Parallel+grep, Spark) likely tier B; ccrc.wustl.edu, arxiv, raftlib.io, aminer all blocked. Paper-access retry.
- HiGHS-style uncatalogued leads from wave 8 verifiers apply here too: none for wave 11 this round.
- VexCL: arXiv 1601.03144 and 1212.6326 blocked; snippet says VexCL is the best OpenCL scan under about 2M elements and below 20% of CUB at large sizes. Paper-access retier lead, domain numerics-and-science.
