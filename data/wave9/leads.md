# Wave 9 leads for a seed pass

Candidates surfaced by verifiers and enrichers, not yet in any wave's records.
- fast-pack/FastPFOR and simdcomp: SPE 2015 paper arXiv 1209.2137 (blocked) would raise both to B. (w9 batch 01)
- saskeli/h0_bv (C): SEA 2025 paper on drops.dagstuhl.de (blocked); retier to B when reachable. (w9 batch 04)
- williams-cs/spider (C): SEA 2024 paper LIPIcs.SEA.2024.21 on drops.dagstuhl.de (blocked); retier to B when reachable. (w9 batch 06)
- lin-toto/recoil (C): arXiv paper blocked; retier to B when reachable. SFVInt (arXiv 2403.06898, BMI2 varint, up to 2x over folly and protobuf): no code repo found. (w9 batch 10, intpack-gh-cpp2)
- dtANS (C++/CUDA, arXiv 2603.01915): repo URL unknown, arXiv blocked. (w9 entropy-gh-cpp2)
- ot/ds2i (D): SIGIR 2014 Partitioned Elias-Fano paper on groups.di.unipi.it (blocked); retier when reachable. (w9 batch 17)
- jermp/mutable_rank_select (D): arXiv 2009.12809 blocked; kurpicz/pwm (C): arXiv 1702.07578 blocked; aaronhong1024/wavelet_forest (D): arXiv 2308.07809 blocked. Retier candidates. (w9 batch 20)
- mikkohei13/faster-minuter (D): Algorithmica wt_fbb paper (Springer, blocked); retier when reachable. (w9 batch 22)
- IlyaGrebnov/libbsc (BWT; lzbench bsc 3.3.12 -m0 19.4/25.0 MB/s at 23.26%, beats xz compress): check if listed; seed candidate. AWS blog on zlib-cloudflare vs other forks (blocked, snippet). (from bzip3/cloudflare-zlib enricher)
- paddor/m77rip (credited in misa77's README): check as a sibling. Show HN item 48922838 on misa77 (blocked). (from misa77 enricher)
- paperhub.s3.amazonaws.com mirrors some arXiv PDFs and is reachable (curl); try it for blocked papers (found via FastPFor enricher). simdcomp shares the SPE paper; its own retier needs the simdcomp code tie-in checked.
- OpenZL second paper arXiv 2605.09928 'Using Graphs to Compress Smaller and Faster' (blocked, not opened). (from OpenZL enricher)
- Consistency retier at wave close: lzbench 2.4 rows (gcc 15.2.0, EPYC 9555P, Makefile -O3 -DNDEBUG, public code) were tiered A for FastLZ (batch 25) but B for Kanzi, LZAV, LZSSE, misa77, Fast LZMA2, libslz, bzip3, memlz, Snappy, Density, libbsc, libzling; pick one and write one retier file.
- Debian Code Search's Go SIMD TurboPFor port (Go 1.26 archsimd, AVX-512; claims to beat the C encode): cross-language claim for QUEUE wave 14. (from TurboPFor enricher)
- arXiv 2605.25528 'Engineering Practical Succinct Bit Vectors: A Space-Time Pareto Analysis on Apple Silicon ARM64 Cores': may list more rank/select code; blocked. (from orzo enricher)
- Apple LZMESH (OS 27 fast codec, liblzraven SPEC section 15) and libzbitmap (LZBITMAP reimplementation; lzfse issue #62): Apple-codec siblings to check. (from LZFSE/liblzraven enricher)
- pisa-engine/pisa: maintained ds2i fork (PEF plus many codecs), not catalogued; seed candidate. (from ds2i enricher)
- traviswheelerlab/avxwindowfmindex (C): AMB paper on biomedcentral/biorxiv (blocked); retier to B when reachable. (w9 batch 36)
