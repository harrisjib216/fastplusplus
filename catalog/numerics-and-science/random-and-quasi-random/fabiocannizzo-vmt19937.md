# VMT19937 (V-family and X-family vectorized Mersenne Twister)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only SIMD Mersenne Twister (MT19937, MT19937-64, SFMT); bulk fills 3.7-4.9x std::mt19937_64 on AVX2/AVX-512, X-family bit-identical.

| | |
|---|---|
| **Beats** | std::mt19937 and std::mt19937_64 (STL-MT19937 / STL-MT19937-64 rows); also the original reference MT19937 / MT19937-64 / SFMT19937 and Intel MKL MT/SFMT |
| **Claimed result** | README table, M samples/s, vectorial mode: V-MT19937-64 2865 (AVX-512) / 1161 (AVX2) vs STL-MT19937-64 590 / 317 (about 4.9x and 3.7x, derived from page data); V-MT19937 2392 (AVX2) vs ORIG-MT19937 259 (about 9.2x, derived from page data); V-SFMT19937 10943 (AVX-512) vs ORIG-SFMT19937 4445 (about 2.5x, derived from page data). Scalar mode: X-MT19937-64 1095 (AVX-512) vs STL 590 (about 1.9x, derived from page data). doc/main.tex also has a 32-bit std::mt19937 row: V-MT19937 vectorial 2391.8 (AVX2) / 5841.4 (AVX-512) vs STL-MT19937 305.7 / 598.6 (about 7.8x and 9.8x, derived from page data). |
| **Workload** | Throughput in million samples/s of 32-bit (MT19937, SFMT19937) and 64-bit (MT19937-64) random numbers, about 1.6e10 numbers per CPU (30 runs of 8.19e6 samples), in scalar (one value per call) and vectorial (block of 10,240) query modes, on five CPU targets (SSE4.2, AVX2, AVX-512, NEON, SVE256). |
| **Metric** | throughput |
| **Hardware** | Intel Celeron J4125 2.0 GHz (SSE4.2), Intel Xeon E5-2686 v4 2.3 GHz (AVX2), Intel Xeon Platinum 8375C 2.9 GHz (AVX-512), Neoverse-N1 2.5 GHz (NEON), Neoverse-V1 2.6 GHz (SVE256) (from doc/main.tex). |
| **Compiler and flags** | GCC 16 per doc/main.tex; Makefile default (NBITS=native) is -O3 -std=c++20 -march=native (plus -msve-vector-bits=256 on SVE); explicit NBITS builds use -msse4.2/-mavx2/-mavx512f -mavx512vl -mavx512bw -mavx512dq with -mpclmul, or -march=armv8-a+simd / -march=armv8-a+sve -msve-vector-bits=256. Which variant produced the tables is not stated. Harness: perf.exe from src/perf.cpp. |
| **Adoption** | 3 stars |
| **Last commit** | 2026-05-29 |
| **Links** | [repository](https://github.com/fabiocannizzo/VMT19937) · [benchmark](https://github.com/fabiocannizzo/VMT19937) |

## Verdict

The author's perf.cpp harness (GCC 16; -O3 -std=c++20 with -march=native or explicit ISA flags; volatile traps against dead-code elimination) measured millions of samples per second on five CPUs: Celeron J4125 (SSE4.2), Xeon E5-2686 v4 (AVX2), Xeon Platinum 8375C (AVX-512), Neoverse-N1 (NEON) and Neoverse-V1 (SVE256). In block mode (10,240 values per call) V-MT19937-64 reached 1161 and 2865 M/s against 317 and 590 for libstdc++ std::mt19937_64 on the AVX2 and AVX-512 Xeons. The STL 'vectorial' figures are copied from its per-call loop, since std::mt19937 has no block API (doc/main.tex footnote).

## Use it when

- You must keep Mersenne Twister output: XMT19937_64 matches std::mt19937_64 for the same seed and ran 1095 vs 590 M/s per call (AVX-512) and 2525 vs 590 M/s in bulk (about 4.3x, derived from page data)
- Bulk generation on x86 with AVX2 or AVX-512 where a different MT-quality stream is acceptable: V-MT19937-64 reached 1161 (AVX2) and 2865 (AVX-512) M/s vs 317 and 590 for std::mt19937_64
- Many independent MT streams for Monte Carlo (finance is the author's target), using the shipped jump-polynomial files or the jump_generator tool to space instances
- 32-bit output on AVX2: V-MT19937 vectorial 2392 M/s vs 305.7 for std::mt19937 (about 7.8x, derived from doc/main.tex)
- Faster SFMT: V-SFMT19937 10943 M/s vs 4445 for the reference SFMT at AVX-512

## Skip it when

- ARM NEON or SVE for 64-bit output: std::mt19937_64 matched or beat it (NEON vectorial STL 285 vs X 255 and V 290 M/s; SVE256 scalar STL 573 vs V 513)
- AVX-512 bulk 32-bit MT where MKL is available: MKL-MT was faster than V-MT19937 (6479 vs 5742 M/s README, 6578.9 vs 5841.4 in doc/main.tex), and X-MT19937 also beat V-MT19937 there because the 16-state V-MT19937 needs about 40 KB of state and overflows L1
- Portable binaries for baseline x86-64: the ISA is fixed at compile time (no runtime dispatch), and simd_config.h stops with '#error SSE4.2 is needed' for SSE2-only flags or 'AVX2 is needed' for AVX-only flags
- Code that wants a drop-in engine for &lt;random&gt; distributions: there is no operator()/result_type/min/max, so you need a small adapter
- Teams that want an established dependency: single author, 3 stars, no tagged releases, and one open issue (MKL comparison request)

## How it is fast

The V-family is inter-state vectorization: SIMD lane i holds its own MT19937 state jumped ahead by roughly P/N steps (x^J mod the characteristic polynomial, Haramoto et al.'s polynomial jump), so the twist and tempering run at full register width with no remainder iterations or misaligned word groups. The X-family vectorizes the single-state recurrence with shifts and blends, which caps its gain. Both families regenerate and temper the whole state in bulk and serve values from a cache-aligned buffer, which is why even one-value-per-call use beats the reference code by 1.5-3.5x (doc/main.tex).

## Compared with alternatives

Pick VMT19937 over pXart, SFMT or cslarsen/mersenne-twister when you need Mersenne Twister specifically and want AVX-512, NEON and SVE paths, a bit-identical X-family, plus jump-ahead tooling for parallel streams. If you are free to change algorithm, simdrng (xoshiro256++/Philox) or SHISHUA give more throughput per core with far smaller state.

## Integration

| | |
|---|---|
| **Form** | header-only (include/ directory; RandGen.h plus polynomial_jump.h); V-family also needs the \~4 KB dat/poly/\*.bits jump files at runtime |
| **Dependencies** | none for the library; Intel MKL and TestU01 optional for the benchmark and test executables |
| **Minimum toolchain** | C++20; README lists GCC 13+, Clang 16+ or MSVC 2022 (/std:c++20); bundled executables need GNU make |
| **Platforms** | x86-64 with SSE4.2, AVX2 or AVX-512 (F/VL/BW/DQ plus PCLMUL in the Makefile), aarch64 NEON and SVE (256-bit vector length); chosen at compile time via SIMD_N_BITS/SIMD_ISA or compiler flags |
| **Thread safety** | not documented; generator state lives in the object and the shared statics are const tables, so one instance per thread is the natural pattern |
| **Drop-in for the baseline** | partial: the X-family reproduces std::mt19937/std::mt19937_64 output (test.cpp checks XMT19937_64 against std::mt19937_64 and the 32-bit reference against std::mt19937), but the API is genrand_uint32/genrand_uint64 rather than operator(), and the V-family produces a different sequence |

## Gotchas

- The README's 'Multiple Independent Generators' example builds 10 generators with the same seed and the same 2^100 commonJump, so all ten emit identical streams; the code comment admits you would need commonJump^i. Pre-compute distinct jumps per instance.
- V-family output depends on VRegBitLen, not the ISA: fix the template width (e.g. VMT19937&lt;512&gt;) to get the same stream on AVX2 and AVX-512 hosts, and load the jump file that matches it (J19934 for 256-bit MT32, etc.). Polynomial::fromBinFile does not check the generator type (loadWithCheck does).
- Constructing a V-family generator without a sequential jump throws std::logic_error ('Having multiple states and no sequential jump provided does not make sense'); missing files also fail through MYASSERT exceptions, so plan for exceptions at init.
- QryBlk16 switches the API at compile time: with it, genrand_uint32() fails a static_assert and you must use genrand_uint32_blk16(dst) (dst ideally 64-byte aligned); without it, only per-value and anySize calls exist.

## Known shortcomings

- README leaves out the std::mt19937 32-bit row present in doc/main.tex (V-MT 7.8-9.8x faster, derived); README and tex AVX-512 numbers differ; MKL beats V-MT on AVX-512.
- README parallel-streams example yields 10 identical generators (same seed, same jump). On NEON/SVE 64-bit, std::mt19937_64 ties or wins. The STL 'vectorial' figures are copied from its scalar loop. ISA is compile-time only (#error on SSE2-only builds). No URBG interface.

## Caveats and trade-offs

Big speedups are in vectorial (block fill of 10,240) mode; scalar single-value V-MT19937 is about 1.7-2.1x the original reference. Intel MKL-MT beats V-MT19937 at AVX-512 vectorial (6479 vs 5742 M/s README; 6578.9 vs 5841.4 in main.tex). The README omits the 32-bit STL-MT19937 row that doc/main.tex and perf.cpp include; std::mt19937 beats the original reference from AVX2 up. On SVE256 STL-MT19937-64 (573) beats V-MT19937-64 scalar (513). README and main.tex disagree on the AVX-512 MT19937 scalar figures (README X 1341 / V 729; main.tex X 929.5 / V 1354.0) and slightly on other AVX-512 MT19937 cells, so they come from different runs. V-family output interleaves jump-separated MT states (src/test.cpp checks each against the reference at the jumped index), so it is a different sequence from one MT19937 for the same seed; the X-family is bit-identical to the reference. libstdc++ inferred from GCC 16 (main.tex credits GCC auto-vectorization of the STL MT). Single author, first-party; arXiv 2309.16682 could not be opened (egress blocked).

The V-family changes the output sequence: it interleaves several MT19937 states de-phased by polynomial jump-ahead, and the sequence depends on the chosen register width (VRegBitLen). The X-family is bit-identical to the original MT19937/MT19937-64/SFMT sequences. Needs jump-polynomial data files (dat/poly) for the V-family, C++20, and SSE4.2/AVX2/AVX-512 or NEON/SVE hardware for the large gains. Large block-fill API (block of 16 or state-size blocks) is where the speedup is.

## Maintenance

Active (393 commits, last commit 2026-05-29) and MIT-licensed, so easy to vendor, but single-author with 3 stars and no releases; the paper source is in doc/main.tex.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** Benchmark harness src/perf.cpp (std::mt19937 and std::mt19937_64 rows, volatile traps against dead-code elimination) is public, the Makefile gives -O3 -std=c++20 plus -march=native (default NBITS=native) or explicit ISA flags, and doc/main.tex names GCC 16 and all five CPU models; every number in the record is on the README and in doc/main.tex.
- **Verifier notes:** README and doc/main.tex numbers checked; derived ratios correct. RNG check passed: X-family matches the original MT output and V-family lanes match the reference at jumped offsets in src/test.cpp. Metadata: MIT, 3 stars, 0 forks, 393 commits, default branch master, last commit 2026-05-29.
- **Fields the verifier corrected:** `baseline`, `baseline_stdlib`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/fabiocannizzo/VMT19937/HEAD/README.md>
  - <https://raw.githubusercontent.com/fabiocannizzo/VMT19937/master/Makefile>
  - <https://raw.githubusercontent.com/fabiocannizzo/VMT19937/master/doc/main.tex>
  - <https://raw.githubusercontent.com/fabiocannizzo/VMT19937/master/src/test.cpp>
  - <https://raw.githubusercontent.com/fabiocannizzo/VMT19937/master/src/perf.cpp>
  - <https://github.com/fabiocannizzo/VMT19937>
  - <https://github.com/fabiocannizzo/VMT19937/commits>
- **Sources the enricher read:**
  - <https://github.com/fabiocannizzo/VMT19937>
  - <https://github.com/fabiocannizzo/VMT19937/issues>
  - <https://github.com/fabiocannizzo/VMT19937/tree/master/src>
  - <https://github.com/fabiocannizzo/VMT19937/tree/master/include>
  - <https://raw.githubusercontent.com/fabiocannizzo/VMT19937/master/README.md>
  - <https://raw.githubusercontent.com/fabiocannizzo/VMT19937/master/BUILD.txt>
  - <https://raw.githubusercontent.com/fabiocannizzo/VMT19937/master/LICENSE>
  - <https://raw.githubusercontent.com/fabiocannizzo/VMT19937/master/Makefile>
  - <https://raw.githubusercontent.com/fabiocannizzo/VMT19937/master/doc/main.tex>
  - <https://raw.githubusercontent.com/fabiocannizzo/VMT19937/master/src/perf.cpp>
  - <https://raw.githubusercontent.com/fabiocannizzo/VMT19937/master/src/test.cpp>
  - <https://raw.githubusercontent.com/fabiocannizzo/VMT19937/master/include/RandGen.h>
  - <https://raw.githubusercontent.com/fabiocannizzo/VMT19937/master/include/MT19937.h>
  - <https://raw.githubusercontent.com/fabiocannizzo/VMT19937/master/include/SIMD.h>
  - <https://raw.githubusercontent.com/fabiocannizzo/VMT19937/master/include/simd_config.h>
  - <https://raw.githubusercontent.com/fabiocannizzo/VMT19937/master/include/polynomial_jump.h>
  - <https://raw.githubusercontent.com/fabiocannizzo/VMT19937/master/include/macros.h>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/fabiocannizzo/vmt19937`) · [data/wave8/enrich/raw/github_com_fabiocannizzo_vmt19937.json](../../../data/wave8/enrich/raw/github_com_fabiocannizzo_vmt19937.json) (enrichment confidence 0.85)

</details>
