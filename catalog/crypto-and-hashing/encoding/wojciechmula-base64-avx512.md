# base64-avx512 (Muła & Lemire)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Encoding (base64, hex, CRC)](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `BSD-3-Clause` · 🔴 abandoned

> C artifact of the Muła–Lemire AVX-512 VBMI base64 codec; 10–20x faster than Chrome's table-driven codec.

| | |
|---|---|
| **Beats** | base64 (conventional/table-based scalar base64 codec, e.g. Chromium's) |
| **Claimed result** | Paper conclusion: 'our codec is 10 to 20 times faster than a highly optimized conventional codec' (Chrome). The AVX-512 codec is limited to \~40 GB/s for inputs larger than 16 kB (in L2), against Chrome's 1.5 GB/s encode and 2.6 GB/s decode. Table 3 gives real-file decode at 25-42 GB/s for AVX-512 vs 2.6 GB/s for Chrome. The 'over 150 GB/s' figure is memcpy's top speed in L1 (\~10 kB inputs), not the codec's. |
| **Workload** | Base64 encode/decode of buffers too large for L1 cache on an AVX-512 (VBMI) capable CPU |
| **Metric** | throughput |
| **Hardware** | Intel Core i3-8121U (Cannon Lake, 2018), 2.2 GHz base / 3.2 GHz max, 32 kB L1d per core (paper Table 2) |
| **Compiler and flags** | GNU GCC 9.1, -O3 -march=cannonlake |
| **Adoption** | 206 stars |
| **Last commit** | 2019-11-19 |
| **Links** | [repository](https://github.com/WojciechMula/base64-avx512) · [benchmark](https://arxiv.org/abs/1910.05109) |

## Verdict

The paper ran on an Intel i3-8121U (Cannon Lake, 3.2 GHz max) with GCC 9.1 -O3 -march=cannonlake, taking the median of 10 runs including call overhead. Encoding and decoding ran at about 40 GB/s for L2-resident inputs over 16 kB, against 1.5 GB/s (encode) and 2.6 GB/s (decode) for Chrome's table-based codec; the paper sums this up as a 10–20x gain. Real-file decode was 25–42 GB/s for in-cache images but only 9.5 GB/s, equal to memcpy, for a 34.9 MB zip. The paper's 150 GB/s figure is memcpy's L1 peak, not the codec.

## Use it when

- Bulk encode or decode of clean base64 (no line breaks, standard alphabet) on x86-64 CPUs with AVX-512 VBMI. GCC's -march lists include it for Cannon Lake, Ice Lake and AMD Zen 4.
- Buffers from a few kB up to L2 size, or large data processed in cache-sized chunks. That is where the paper measured about 40 GB/s against 1.5–2.6 GB/s for Chrome's codec.
- A fleet where you control the target CPU and can compile with a VBMI-capable -march and no dispatch layer.
- As readable reference kernels (about 50 lines each) to port into your own codec or runtime-dispatch layer.

## Skip it when

- CPUs without VBMI: this includes AVX-512 parts such as Skylake-SP, Cascade Lake and Cooper Lake (GCC's ISA lists show no AVX512VBMI; the paper wrongly names Cascade and Cooper Lake), plus pre-Zen 4 AMD and all ARM. There is no fallback or CPU detection, so the code faults with an illegal instruction.
- MIME, PEM or any line-wrapped input. The whitespace-skipping decoder has had an open 'despacing buggy' issue (#2, returns -1) since 2019.
- Decoding untrusted input: in the decoder the benchmark uses, error checking is broken (see gotchas).
- Production use that needs base64url, streaming, output-length helpers or a maintained API. simdutf and aklomp/base64 provide these.
- Data far larger than cache: on a 34.9 MB zip the paper's AVX-512 decoder ran at memcpy speed (9.5 GB/s), against 8.3 GB/s for AVX2, so the gain over AVX2 largely vanishes once memory-bound.

## How it is fast

Encoding takes three instructions per 48 input bytes. vpermb duplicates and reorders the input bytes, vpmultishiftqb moves the four 6-bit fields of each 24-bit group into separate bytes, and a second vpermb uses the 64-character alphabet held in one register as the lookup table. Decoding takes five instructions per 64 characters: vpermi2b does a 128-entry ASCII-to-6-bit lookup that flags invalid bytes with 0x80, vpternlogd ORs those flags into an error register that is checked once at the end (so the hot loop has no branch), vpmaddubsw and vpmaddwd pack the fields, and vpermb compacts the result to 48 bytes. The paper counts about 7x fewer instructions than the authors' earlier AVX2 codec for encoding and about 5x fewer for decoding.

## Compared with alternatives

Pick it only to study or vendor the paper's exact AVX-512 VBMI kernels. For production, simdutf's base64 cites this paper, runs an AVX-512 path on Ice Lake/Zen 4 behind runtime dispatch, and handles whitespace, url-safe input and strict or loose padding. aklomp/base64 offers runtime dispatch but only for AVX-512 encoding (its decoding reuses AVX2). base64simd and fastbase64 by the same authors cover AVX2-only machines.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (tails fall back to bundled Chromium/modp_b64 scalar code, BSD-licensed) |
| **Minimum toolchain** | C99 compiler with AVX-512 VBMI intrinsics. The README suggests GCC 8+ and the paper and Dockerfile used GCC 9.1. The despace variant also uses GCC builtins and BMI2 PEXT/PDEP. |
| **Platforms** | x86-64 with AVX-512 F/BW/VBMI only; the Makefile hard-codes -march=cannonlake |
| **Thread safety** | not documented; from reading the source, the codec functions touch only constant tables and caller buffers, so concurrent calls on separate buffers look safe |
| **Drop-in for the baseline** | partial — decode mirrors chromium_base64_decode (size_t return, (size_t)-1 on error), but encode returns void, the SIMD loops need extra output slack, and there is no length helper or alphabet option |

## Gotchas

- The benchmarked decode_base64_avx512vbmi__unrolled overwrites its error register on every 256-byte iteration (errorvec = _mm512_ternarylogic_epi32(t0, t1, t2, OR_ALL) with no previous errorvec). Invalid characters in any 256-byte block except the last are therefore not reported. Use decode_base64_avx512vbmi or patch it.
- From reading the source (not tested): the SIMD loop consumes every full 64-byte block and '=' decodes as invalid there, and only the sub-64-byte tail handles padding. So padded input whose length is an exact multiple of 64 appears to be rejected with -1.
- Output buffers need slack. The decoder's 64-byte loop issues full 64-byte stores while advancing only 48 bytes, so allow about 16 bytes past the decoded size; Chromium's own sizing guidance allows only len\*3/4. The encoder's tail goes through chromium_base64_encode, which writes a trailing NUL only when n % 48 != 0. The encoder returns nothing, so compute 4\*ceil(n/3) yourself.
- The paper's GB/s figures are normalized to base64 bytes, so the raw-binary rate for encoding is 3/4 of the quoted figure. The authors saw no AVX-512 downclocking on their Cannon Lake part but note that other Intel processors downclock.

## Known shortcomings

- Research code for the paper (arXiv 1910.05109), not a packaged library; needs AVX-512 VBMI (Cannon Lake i3-8121U or newer). The quoted 150 GB/s is the memcpy L1 ceiling, not the codec's speed.
- The benchmarked `__unrolled` decoder resets its error vector every 256-byte block, so invalid characters in earlier blocks go unreported; padded input whose length is a multiple of 64 has '=' flagged invalid in the SIMD loop (from source). Decoder needs \~16 bytes of output slack; encoder returns void. Cascade/Cooper Lake lack VBMI (the paper and record are wrong on this); no fallback. 25-42 GB/s real-file figures are in-cache; a 34.9 MB file runs at memcpy speed (9.5 GB/s).

## Caveats and trade-offs

Repo README has no numbers itself; the throughput/speedup figures come from the companion peer-reviewed paper (Software: Practice and Experience), not the bare repository page. Last commit is from 2019.

Requires AVX-512 VBMI (Cannon Lake/Cascade Lake+); repo is the paper's artifact, not a general-purpose runtime-dispatching library; no fallback path bundled

## Maintenance

A frozen paper artifact, abandoned since 2019-11 with one bug open since 2019. It is BSD-3-Clause and small enough to vendor; the last known-good toolchain is GCC 9.1 per its Dockerfile.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** The paper (arXiv 1910.05109, published in Software: Practice and Experience 50(2), 2020) benchmarks the AVX-512 codec against the Chrome base64 library. It states GCC 9.1 with -O3 -march=cannonlake and an Intel i3-8121U (Cannon Lake). The benchmark code is public in the linked repo: src/benchmark.c and the Makefile, which builds chromiumbase64, fastavxbase64 and the AVX-512 VBMI codecs with -O3 -march=cannonlake.
- **Verifier notes:** Everything checks out except two points. The 150 GB/s figure was attributed to the codec but is actually the memcpy peak. The hardware field lacked the CPU model, now added. License BSD-3-Clause, 206 stars and last commit 2019-11-19 (abandoned) all verified via gh.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/1910.05109>
  - <https://arxiv.org/pdf/1910.05109>
  - <https://github.com/WojciechMula/base64-avx512>
  - <https://raw.githubusercontent.com/WojciechMula/base64-avx512/master/README.md>
  - <https://raw.githubusercontent.com/WojciechMula/base64-avx512/master/Makefile>
  - <https://raw.githubusercontent.com/WojciechMula/base64-avx512/master/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/WojciechMula/base64-avx512>
  - <https://raw.githubusercontent.com/WojciechMula/base64-avx512/master/README.md>
  - <https://api.github.com/repos/WojciechMula/base64-avx512/git/trees/HEAD?recursive=1>
  - <https://raw.githubusercontent.com/WojciechMula/base64-avx512/master/Makefile>
  - <https://raw.githubusercontent.com/WojciechMula/base64-avx512/master/Dockerfile>
  - <https://raw.githubusercontent.com/WojciechMula/base64-avx512/master/include/encode_base64_avx512vbmi.h>
  - <https://raw.githubusercontent.com/WojciechMula/base64-avx512/master/include/decode_base64_avx512vbmi.h>
  - <https://raw.githubusercontent.com/WojciechMula/base64-avx512/master/include/decode_base64_avx512vbmi_despace.h>
  - <https://raw.githubusercontent.com/WojciechMula/base64-avx512/master/include/encode_base64_avx512vl.h>
  - <https://raw.githubusercontent.com/WojciechMula/base64-avx512/master/include/decode_base64_avx512vbmi__unrolled.h>
  - <https://raw.githubusercontent.com/WojciechMula/base64-avx512/master/include/chromiumbase64.h>
  - <https://raw.githubusercontent.com/WojciechMula/base64-avx512/master/src/base64/encode_base64_avx512vbmi.c>
  - <https://raw.githubusercontent.com/WojciechMula/base64-avx512/master/src/base64/encode_base64_avx512vl.c>
  - <https://raw.githubusercontent.com/WojciechMula/base64-avx512/master/src/base64/decode_base64_avx512vbmi.c>
  - <https://raw.githubusercontent.com/WojciechMula/base64-avx512/master/src/base64/decode_base64_avx512vbmi__unrolled.c>
  - <https://raw.githubusercontent.com/WojciechMula/base64-avx512/master/src/base64/decode_base64_tail_avx512vbmi.c>
  - <https://raw.githubusercontent.com/WojciechMula/base64-avx512/master/src/base64/decode_base64_avx512vbmi_despace.c>
  - <https://raw.githubusercontent.com/WojciechMula/base64-avx512/master/src/base64/chromiumbase64.c>
  - <https://raw.githubusercontent.com/WojciechMula/base64-avx512/master/src/unit.c>
  - <https://raw.githubusercontent.com/WojciechMula/base64-avx512/master/src/benchmark.c>
  - <https://raw.githubusercontent.com/WojciechMula/base64-avx512/master/scripts/setupfortesting/README.md>
  - <https://github.com/WojciechMula/base64-avx512/issues?q=is%3Aissue>
  - <https://github.com/WojciechMula/base64-avx512/issues/2>
  - <https://arxiv.org/pdf/1910.05109>
  - <https://github.com/aklomp/base64>
  - <https://github.com/simdutf/simdutf>
  - <https://gcc.gnu.org/onlinedocs/gcc/x86-Options.html>
  - <https://hn.algolia.com/api/v1/search?query=base64%20almost%20the%20speed%20of%20a%20memory%20copy&tags=story>
  - <https://news.ycombinator.com/item?id=21459839>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/wojciechmula/base64-avx512`) · [data/wave7/enrich/raw/github_com_wojciechmula_base64_avx512.json](../../../data/wave7/enrich/raw/github_com_wojciechmula_base64_avx512.json) (enrichment confidence 0.85)

</details>
