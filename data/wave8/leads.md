# Wave 8 leads for a seed pass

Candidates surfaced by verifiers and enrichers, not yet in any wave's records.

- springer13/hptt (High-Performance Tensor Transposition, the library TCL depends on). (from TCL enrichment)
- TCCG / GETT (arXiv 1607.00145, Springer & Bientinesi tensor contraction code generator), cited by TCL. (from TCL enrichment)
- CoDiPack (C++ operator-overloading AD, SciComp TU Kaiserslautern), an AD peer that ad-benchmarks does not compare against. (from XAD enrichment)
- ddemidov/amgcl_benchmarks: AMGCL's benchmark code; could support a tier upgrade for AMGCL if it records compiler flags. (from AMGCL enrichment)
- HazyResearch HipKittens (AMD) and ThunderMittens (Apple Silicon), ThunderKittens siblings. (from ThunderKittens enrichment)
- NVlabs/CGBN (NVIDIA GPU bigint library; beats midint division at 2^15 bits and below). (from midint enrichment)
- coancea/midint-arithmetic (Oancea/Watt GPU multi-precision add/multiply, arXiv 2405.14642), parent of the listed division fork. (from midint enrichment)
- libxsmm/libxsmm-dnn: now holds the DL layers LIBXSMM's IPDPS 2020 paper benchmarked; may need its own entry or a duplicate decision. (from LIBXSMM enrichment)
- BesTLA (intel/neural-speed/bestla): header-only Xbyak weight-only-quantized GEMM (AVX2 to AMX) usable without Neural Speed; no numbers in README. (from Neural Speed enrichment)
- FlashAttention-4 (CuTeDSL, Hopper/Blackwell, flash-attn-4): own entry or fold into FlashAttention. (from FA3 enrichment)
- Clad (Clang-plugin source-transformation AD), likely Enzyme sibling; name only, not researched. (from Enzyme enrichment)
- prng.di.unimi.it/xoshiro256++-vect-speed.c: Vigna's public-domain 8-way vectorized xoshiro256++, the copyable original of the listed gist technique. (from xoshiro8x256pp enrichment)
- tesch1/MTGEMM-A: MIT re-implementation of the MpGEMM (ARM SME) design with public benchmark code, compiler, flags and CPU; 1.25x over Accelerate (paper design 1.09x); 0 stars. (from MpGEMM verifier)
- Indexicon (arXiv 2606.04676), spatial indexing library; not read (arXiv 429). (from geo searches)
- IATF (input-aware tuning framework for compact BLAS on ARMv8, cunyangwei.github.io/files/IATF.pdf). (from IAAT enrichment)
- hayguen/pffft_benchmarks: per-CPU results for the marton78 pffft fork itself; could back a tier change. (from pffft enrichment)
