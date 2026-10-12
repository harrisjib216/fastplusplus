# rans-tricks

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Entropy coders](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Public domain (dedication in README: 'All of this is public domain, do whatever you want with it'; no LICENSE file)` · 🔴 abandoned

> Branchless 16-bit-renormalizing variant of ryg's rans_byte.h; README reports about 1.5-1.7x over standard 4-way interleaved rANS.

| | |
|---|---|
| **Beats** | standard 4-way interleaved rANS (rans_byte style); FSE |
| **Claimed result** | 4-way interleaved rans trick 415 MB/s encode, 460 MB/s decode vs 4-way interleaved standard rans 250 / 300 MB/s (about 1.66x / 1.53x, derived) and FSE 325 / 440 MB/s (about 1.28x / 1.05x, derived). |
| **Workload** | enwik8 encode and decode with adaptive-probability branchless rANS variants (4-way interleaved and implicit). |
| **Metric** | throughput |
| **Hardware** | Ryzen 1700 @ 3.7 GHz |
| **Adoption** | 27 stars |
| **Last commit** | 2018-04-27 |
| **Links** | [repository](https://github.com/loxxous/rans-tricks) · [benchmark](https://github.com/loxxous/rans-tricks) |

## Verdict

The README reports, for enwik8 on a Ryzen 1700 at 3.7 GHz with no compiler or flags stated, 415 MB/s encode and 460 MB/s decode for the 4-way interleaved trick versus 250/300 MB/s for 4-way interleaved standard rANS; only the trick variants exist in main.cpp (the standard-rANS rows came from code not in the current main.cpp), the harness reports MiB/s, and the FSE row (325/440 MB/s) equals the Proba80 row in the FiniteStateEntropy README rather than an enwik8 run.

## Use it when

- You already use ryg_rans rans_byte.h and want a small, branch-free renormalization patch to copy into your own rANS loop.
- Order-0 or model-driven byte coding where symbol frequencies may change per symbol (rANS with arbitrary start/freq per call), and you want speed near static FSE without SIMD.
- Portable scalar code is required: the coder header uses no intrinsics or assembly (only the test harness uses __rdtsc).
- Teaching or prototyping: the whole technique fits in about 20 changed lines and is public domain.

## Skip it when

- You need a finished codec with headers, table serialization and bounds checking; this is a header plus a demo, last touched 2018-04-27.
- Peak throughput on modern x86 or ARM: SIMD rANS (rans_static r32x16b_avx2, hypersonic-rANS, htscodecs 32-way) or Huffman decoders reach several times the 460 MB/s reported here.
- Untrusted or truncated input: the decoder unconditionally reads 2 bytes at the stream pointer and there are no bounds checks.
- Big-endian targets or cross-platform bitstreams: 16-bit words are stored and loaded natively through uint16_t\* casts, while the flush writes bytes little-endian.

## How it is fast

The normalization lower bound is raised to L = 2^16 and the coder emits and consumes 16 bits at a time, so each symbol needs at most one renormalization step; that step is then made branchless: the encoder always stores the low 16 bits at ptr-2 and advances the pointer by (x &gt;= x_max) &lt;&lt; 1, and the decoder always loads a 16-bit word and selects the new state with a mask (x = (-s & (tx - x)) + x). Removing the data-dependent renorm branch avoids mispredictions, and 4-way interleaving (four explicit states, or an 'implicit' rotating array of four states) supplies instruction-level parallelism. The encoder keeps ryg's reciprocal-multiply division (Alverson) for static symbols.

## Compared with alternatives

Pick it over ryg_rans when you want ryg's scalar API with a branchless 16-bit renorm and are willing to fix the unaligned casts yourself; pick rans_static, hypersonic-rANS or htscodecs instead when SIMD is available and raw throughput matters, and FiniteStateEntropy when static tables are fine and you want a maintained codec.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for rans_byte.h (stdint.h); the demo main.cpp needs platform.h, which uses x86intrin/intrin.h and supports only Windows and Linux |
| **Minimum toolchain** | not documented; plain C-compatible header (C99 or any C++ compiler), demo built with MSVC or GCC per platform.h |
| **Platforms** | header: any little-endian target tolerating unaligned 16-bit access; demo: x86 only (__rdtsc), Windows or Linux |
| **Thread safety** | not documented; all state is caller-owned (RansState and the output pointer), so separate coders on separate threads share nothing |
| **Drop-in for the baseline** | partial — same function names and call pattern as ryg_rans rans_byte.h, but the bitstream is not compatible (16-bit renorm, L = 2^16 instead of byte renorm with L = 2^23), so it replaces rans_byte only when both ends switch |

## Gotchas

- The encoder writes 2 bytes at ptr-2 on every symbol even when it does not advance, and the decoder reads 2 bytes past the current position on every symbol; reserve slack before the start of the output buffer and after the end of the input stream.
- The 16-bit loads and stores go through uint16_t\* casts of uint8_t pointers (unaligned, strict-aliasing UB in C/C++); replace them with memcpy before vendoring.
- The demo's 4-way decoder tail (input length not a multiple of 4) writes dec_bytes[in_size+k], past the end of the output buffer, and pops the tail states in the same order they were pushed; enwik8 (100,000,000 bytes) is a multiple of 4, so the benchmark never exercises this path.
- Despite the README's 'supporting adaptive probabilities', main.cpp uses one static order-0 table (counted once, normalized to 2^15); adaptivity is only a property of rANS that the code permits, not something that was measured.

## Known shortcomings

- Tier C: README numbers reproduce, but the FSE row (325/440) is copied from the FSE README's Proba80 row and main.cpp has no FSE code, so the FSE comparison is doubtful. Public-domain dedication in the README with no LICENSE file or patent grant.
- main.cpp uses one static order-0 table, so the README's 'adaptive probabilities' was never measured and the FSE comparison is static vs static; the standard-rANS rows (250/300) are not in the current main.cpp. The 4-way decode tail writes dec_bytes[in_size+k] out of bounds and pops tail states in the wrong order (never hit on enwik8, whose size is a multiple of 4); unaligned uint16_t\* type punning (undefined behaviour) and an unconditional 2-byte overread/overwrite; the harness reports MiB/s.

## Caveats and trade-offs

No LICENSE file (repo holds only README.md, main.cpp, platform.h, rans_byte.h); the README dedicates the code to the public domain, which this catalog treats as copyable; no patent grant. main.cpp (a ryg_rans-style harness timing rANS variants with __rdtsc) contains no FSE code, and the FSE row (325 MB/s encode, 440 MB/s decode) is identical to the Proba80 FSE row in the FiniteStateEntropy README, so it was probably copied rather than measured on the Ryzen 1700 with enwik8; the FSE comparison is doubtful and the standard-rANS comparison is the credible one. No compiler or flags stated; single file, single machine; last commit 2018-04-27.

Branchless adaptive rANS with no intrinsics or assembly (portable C++); only a small header (rans_byte.h), main.cpp and platform.h. Adaptive probabilities, so FSE (static tables) is not a like-for-like workload.

## Maintenance

Abandoned: 18 commits, all on 2018-04-27, no issues or PRs; public-domain dedication in the README (no LICENSE file), and the core change is small enough to re-implement from reading it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README table (enwik8, Ryzen 1700 @ 3.7 GHz) shows 4-way interleaved rans trick 415/460 MB/s vs 4-way interleaved standard rans 250/300 MB/s and FSE 325/440 MB/s; main.cpp holds the rANS harness but no compiler or flags are stated and FSE is not in the harness, so first-party C.
- **Verifier notes:** Numbers match README exactly; derived ratios fine. Confirmed FSE row equals FSE README Proba80 row (Cyan4973/FiniteStateEntropy dev README line 33). Usability changed to copyable per public-domain dedication rule.
- **Fields the verifier corrected:** `license`, `usability`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/loxxous/rans-tricks>
  - <https://github.com/loxxous/rans-tricks/commits>
  - <https://raw.githubusercontent.com/loxxous/rans-tricks/HEAD/README.md>
  - <https://raw.githubusercontent.com/loxxous/rans-tricks/HEAD/main.cpp>
  - <https://raw.githubusercontent.com/Cyan4973/FiniteStateEntropy/dev/README.md>
- **Sources the enricher read:**
  - <https://github.com/loxxous/rans-tricks>
  - <https://github.com/loxxous/rans-tricks/commits>
  - <https://github.com/loxxous/rans-tricks/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/loxxous/rans-tricks/HEAD/README.md>
  - <https://raw.githubusercontent.com/loxxous/rans-tricks/HEAD/rans_byte.h>
  - <https://raw.githubusercontent.com/loxxous/rans-tricks/HEAD/main.cpp>
  - <https://raw.githubusercontent.com/loxxous/rans-tricks/HEAD/platform.h>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/loxxous/rans-tricks`) · [data/wave9/enrich/raw/github_com_loxxous_rans_tricks.json](../../../data/wave9/enrich/raw/github_com_loxxous_rans_tricks.json) (enrichment confidence 0.6)

</details>
