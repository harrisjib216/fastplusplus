# hypersonic-rANS

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Entropy coders](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-2-Clause` · 🟡 stale

> Research C++ rANS codecs with AVX2/AVX-512 decoders reaching about 3 GiB/s, about 3.1x FSE and 1.27x htscodecs.

| | |
|---|---|
| **Beats** | FSE (Finite State Entropy, tANS), FSE Huff0 (Huffman), htscodecs rANS (scalar/SSE/AVX2/AVX-512); also TurboANX (closed source) |
| **Claimed result** | enwik8 decode: rANS32x64 16w 11 (raw) 3,018.02 MiB/s vs FSE 966.58 MiB/s (about 3.1x, derived from page data), FSE Huff0 2,515.23 MiB/s (about 1.2x, derived), htscodecs rans32avx2 order-0 2,374.04 MiB/s (about 1.27x, derived). Ratio 64.48 % vs FSE 63.2 % and Huff0 63.4 % (slightly worse ratio). README: 'Fastest decoders can reach a throughput of up to 3.3 GB/s'. |
| **Workload** | Single-threaded decode of enwik8 (100,000,000 bytes) and Silesia x-ray, order-0 static, blocks as in the repo benchmark harness. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 7950X, 32 GB DDR5-6000 CL30, Windows 11 via WSL2 |
| **Compiler and flags** | clang++ (version not stated); project.lua sets -O3, -mxsave and LinkTimeOptimization for the Linux ReleaseClang config (premake5 gmake2, config=releaseclang_x64) |
| **Adoption** | 21 stars |
| **Last commit** | 2024-09-03 |
| **Links** | [repository](https://github.com/rainerzufalldererste/hypersonic-rANS) · [benchmark](https://github.com/rainerzufalldererste/hypersonic-rANS) |

## Verdict

The author's single-threaded runs on an AMD Ryzen 9 7950X under WSL2, built with clang++ at -O3 with LTO (version not stated), decoded enwik8 at 3,018.02 MiB/s with rANS32x64 16w 11 (raw), against 966.58 MiB/s for FSE, 2,515.23 MiB/s for Huff0 and 2,374.04 MiB/s for htscodecs rans32avx2 order-0 (about 3.1x, 1.2x and 1.27x, derived from page data). On x-ray, 3,079.98 MiB/s beat htscodecs AVX2 at 2,244.87 MiB/s.

## Use it when

- Decode-dominated, single-thread order-0 entropy decoding of large byte buffers (MB scale such as enwik8 or Silesia files) on x86-64 with AVX2, where you can vendor and adapt code yourself.
- As a reference design for building your own SIMD rANS decoder: it lays out many decoder variants (gather vs shuffle vs permute, 32 vs 64 states, 10-15 bit precision) with per-variant numbers.
- Block-parallel decompression: the multithreaded block variants reported 7.0-18.0 GiB/s decode on x-ray (Ryzen 9 7950X), at a small ratio cost.
- When a slight ratio loss (enwik8 64.48% vs FSE 63.2% and Huff0 63.4%) is acceptable in exchange for decode speed.

## Skip it when

- Encode-heavy workloads: all encoders are scalar and run at about 190-350 MiB/s, versus FSE 736 MiB/s and Huff0 1,581 MiB/s on the same enwik8 table.
- Non-x86 or pre-AVX2 targets: every top decoder needs AVX2; there are no NEON or portable SIMD paths.
- Untrusted input: from reading the raw scalar decoder, it checks header lengths but not each 16-bit renormalisation read, and computes the loop bound as expectedOutputLength - 64 + 1 in size_t, which underflows for outputs shorter than 63 bytes (code reading only, not run); no fuzzing is documented.
- When you need a maintained library: functional code last changed July 2023 (later commits are CI and dependabot updates), there are no releases, and there is no stable on-disk format or API.
- Adaptive or context-modelled (order-1+) coding: only static order-0 histograms are implemented.

## How it is fast

Wide interleaving (32 or 64 independent rANS states) keeps 8-lane AVX2 or 16-lane AVX-512 registers busy. Decode uses a cumulative-inverse slot-to-symbol table plus a packed (freq, cumul) table, looked up with hardware gathers (_mm256_i32gather_epi32), and renormalisation is done by compacting the lanes that need a 16-bit word with shuffle/permute lookup tables (variants 'xmm shfl', 'xmm shfl2', 'ymm perm'). The encoder writes the interleaved streams in a permuted order (idx2idx) so the decoder's pack/unpack needs no extra shuffles, and lower probability precision (10-12 bits) keeps the tables in L1, which is why the 11-bit variants are the fastest.

## Compared with alternatives

Pick hypersonic-rANS over htscodecs or FiniteStateEntropy only when x86 AVX2 decode throughput is the single goal and you will own the code; use htscodecs for a maintained, fuzzed library with fast SIMD encoders and NEON, and FSE/Huff0 when encode speed or portability matters. Compared with rans-tricks and ryg_rans, it is the more aggressively vectorised successor design.

## Integration

| | |
|---|---|
| **Form** | source-drop (repo builds only a benchmark executable via premake5; no library target) |
| **Dependencies** | none beyond the C++ standard library and pthreads (Linux); premake5 to generate build files |
| **Minimum toolchain** | C++17 (Windows clang configuration) / C++20 (Linux and MSVC configurations); clang++, GCC or MSVC 2022 per the README build steps |
| **Platforms** | x86-64 only; AVX2 for the fast decoders, optional AVX-512 (F/BW) variants; Windows and Linux |
| **Thread safety** | Codec functions use only caller buffers and stack state, so separate calls look independent (from source reading); not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Function names encode precision and lane count; the encoder and decoder precision (10-15) and variant family must match, and the stream carries no format tag that would catch a mismatch.
- Headline 'raw' rows are hidden by default in the benchmark tool (--include-raw), and the default variants are block-based; the non-raw rows encode slower (about 225-240 MiB/s on enwik8).
- The decoders rely on hardware AVX2 gathers; the htscodecs README notes that Intel's GDS/Downfall microcode slows such gathers 2-3x, and the published numbers are from an AMD Ryzen 9 7950X only.
- Comparisons mix environments: TurboANX numbers came from a separate 2023 native-Windows TurboBench run, and the htscodecs rows predate htscodecs 1.6.0's switch to simulated gathers. GCC CI jobs were removed in July 2023 because they hung.

## Known shortcomings

- Tier C: enwik8 numbers reproduce but project.lua's -O3/LTO build names no clang version and the baselines are not run by the repo harness; the win is decode only (encode 336.81 vs FSE 736.10 MiB/s).
- Source reading (not run): the raw decoders compute the loop bound expectedOutputLength - 64 + 1 in size_t, so outputs under 63 bytes underflow and write out of bounds; no per-read bounds check on renormalisation, so unsafe on untrusted input; no fuzzing. Benchmark-only build with no library, API or releases; functional code last changed Jul 2023 and the GCC CI was dropped because it hung; AVX2 hardware gathers only (Downfall exposure); numbers from a Ryzen 7950X only and the htscodecs baseline rows predate its 1.6.0 simulated gathers.

## Caveats and trade-offs

Ratio and speed trade-offs are per variant; the headline 'raw' row has slightly worse ratio (64.48 % versus FSE 63.2 % and Huff0 63.4 %). Win is decode only: the top row encodes at 336.81 MiB/s versus FSE 736.10 and Huff0 1,581.32 MiB/s; README says all encoders are scalar and not particularly optimized, and the best decoders require AVX2. TurboANX (closed source) is within about 2% (2,964.02 versus 3,018.02 MiB/s) and comes from a June 2023 TurboBench run on a native Windows build, so mixed environment. Compiler version not stated. First-party benchmark. The author calls it an R&D repo not yet finalized for integration. README also lists multithreaded variants up to 18,035.77 MiB/s decode. Last commit is a dependabot actions bump (2024-09-03).

Decode-optimised; every best decoder variant needs AVX2 (some AVX-512 variants), x86-64 only. Encoders are scalar and unoptimised (about 230-350 MiB/s). Needs many interleaved streams (32 or 64 lanes), so small inputs and multi-symbol-per-state formats differ from FSE. Author calls it R&D, not finalised, not integration-friendly yet.

## Maintenance

Stale research code (last functional change July 2023, last commit a 2024-09-03 CI bump; 2 open issues, no releases), BSD-2-Clause, so copyable for vendoring, but needs hardening before production use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README tables give first-party decode throughput on a named CPU (Ryzen 9 7950X) against FSE, FSE Huff0 and htscodecs; build files (project.lua: -O3, LTO for Linux ReleaseClang) are public, but the clang version is not stated and the README does not show that the baselines ran through the repo's own harness (TurboANX came from a separate TurboBench run), so not A.
- **Verifier notes:** enwik8 rows (3,018.02 / 966.58 / 2,515.23 / 2,374.04 MiB/s), hardware and 'up to 3.3 GB/s' all confirmed on the README; BSD-2-Clause and 21 stars confirmed. github.io graph page not opened (blocked host).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/rainerzufalldererste/hypersonic-rANS>
  - <https://github.com/rainerzufalldererste/hypersonic-rANS/commits>
  - <https://raw.githubusercontent.com/rainerzufalldererste/hypersonic-rANS/HEAD/README.md>
  - <https://raw.githubusercontent.com/rainerzufalldererste/hypersonic-rANS/HEAD/premake5.lua>
  - <https://raw.githubusercontent.com/rainerzufalldererste/hypersonic-rANS/master/project.lua>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/rainerzufalldererste/hypersonic-rANS/master/README.md>
  - <https://raw.githubusercontent.com/rainerzufalldererste/hypersonic-rANS/master/LICENSE>
  - <https://raw.githubusercontent.com/rainerzufalldererste/hypersonic-rANS/master/project.lua>
  - <https://raw.githubusercontent.com/rainerzufalldererste/hypersonic-rANS/master/premake5.lua>
  - <https://github.com/rainerzufalldererste/hypersonic-rANS/tree/master/src>
  - <https://raw.githubusercontent.com/rainerzufalldererste/hypersonic-rANS/master/src/rANS32x64_16w.h>
  - <https://raw.githubusercontent.com/rainerzufalldererste/hypersonic-rANS/master/src/rANS32x64_16w.cpp>
  - <https://raw.githubusercontent.com/rainerzufalldererste/hypersonic-rANS/master/src/hist.h>
  - <https://raw.githubusercontent.com/rainerzufalldererste/hypersonic-rANS/master/src/rans.h>
  - <https://raw.githubusercontent.com/rainerzufalldererste/hypersonic-rANS/master/src/simd_platform.h>
  - <https://raw.githubusercontent.com/rainerzufalldererste/hypersonic-rANS/master/src/main.cpp>
  - <https://github.com/rainerzufalldererste/hypersonic-rANS/issues?q=is%3Aissue>
  - <https://github.com/rainerzufalldererste/hypersonic-rANS/commits>
  - <https://raw.githubusercontent.com/samtools/htscodecs/master/README.md>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/rainerzufalldererste/hypersonic-rans`) · [data/wave9/enrich/raw/github_com_rainerzufalldererste_hypersonic_rans.json](../../../data/wave9/enrich/raw/github_com_rainerzufalldererste_hypersonic_rans.json) (enrichment confidence 0.8)

</details>
