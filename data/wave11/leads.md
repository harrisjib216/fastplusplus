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
- oneTBB second claim (ParallelReductionsBenchmark: libstdc++ std::reduce par on oneTBB vs spawn-per-call std::thread, 1.7x Graviton4, 3.3x Zen4): folded into the wave 1 oneTBB entry; retier lead if a direct TBB-vs-thread-pool benchmark appears. junction (preshing.com, arXiv 1601.04017) blocked.
- HPX: arXiv 2606.11937 Cholesky-Bench snippet (HPX 15-30% faster than OpenMP) unreachable; issue 3137 shows OpenMP faster. Paper-access retry.
- Enricher w11 pair-018: the reckless doc/performance.md spdlog adapter passes true as truncate (spdlog 1.3.1 basic_logger_mt), not force-flush as the page claims; spdlog and reckless entries citing that page should carry the same caveat (retier lead).
- Enricher w11 pair-020 leads (uncatalogued): andreasbuhr/cppcoro (tzcnt suite mean 3.67x, beats HPX, concurrencpp and libcoro), jbaldwin/libcoro, STEllAR-GROUP/hpx.
- Seed pass w11-seed-b (2026-10-13): paper-access retiers for OpenCilk (PPoPP 2023, abstract snippet only: geomean 4-26% at 1 core, 10-120% at 48 cores) and Lace (Euro-Par 2014 and the 2020 Twente thesis, parity with Wool, beats Cilk Plus, TBB and OpenMP without figures); Nowa (Schmaus, IPDPS 2021) may compare Lace.
