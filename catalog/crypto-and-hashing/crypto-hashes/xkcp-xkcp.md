# KangarooTwelve (XKCP)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Cryptographic hashes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `C` · `CC0-1.0 for most files, with per-file exceptions: CRYPTOGAMS BSD-style/GPL (AVX2 and AVX-512 KeccakP-1600 asm), Apache-2.0 OR ISC OR MIT (ARMv8-A cores), and Brian Gladman's permissive license (brg_endian.h)` · 🟢 active

> Keccak team's C package; its KangarooTwelve XOF hashes long messages 5-8x faster than SHAKE128 via SIMD tree hashing.

| | |
|---|---|
| **Beats** | SHAKE128 (FIPS 202), SHA-256 and SHA-512, using the fastest implementations available to the authors, cross-checked with eBASH; 'often' OpenSSL for the traditional hashes |
| **Claimed result** | Paper Table 2 (single core, long messages, cycles/byte): KangarooTwelve runs at 0.55 on a Core i7-7800X (SkylakeX), 1.22 on a Core i5-6500 (Skylake) and 1.44 on a Core i5-4570 (Haswell). SHAKE128 runs at 4.28/5.56/7.09 (K12 \~7.8x/\~4.6x/\~4.9x faster) and SHA-256 at 6.65/6.91/9.27 (\~12x/\~5.7x/\~6.4x). Serial K12 (&lt;=8 KiB) runs at 2.35/2.89/3.68, still \~1.8-1.9x faster than SHAKE128. Ratios are derived from page data. |
| **Workload** | Single-core hashing of long messages (much larger than 8 KiB) in cycles/byte. K12 uses its 8 KiB-leaf tree mode with 4-way AVX2 or 8-way AVX-512 Keccak-p[1600,12]. The &lt;=8 KiB row is serial. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-7800X (SkylakeX, AVX-512), Core i5-6500 (Skylake), Core i5-4570 (Haswell) |
| **Adoption** | 664 stars; official Keccak-team code, basis for the SHA-3/Keccak reference and optimized implementations used across the ecosystem |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/XKCP/XKCP) · [benchmark](https://eprint.iacr.org/2016/770.pdf) |

## Verdict

In the designers' peer-reviewed paper (ACNS 2018, Table 2; compiler not stated), single-core long-message KangarooTwelve ran at 0.55/1.22/1.44 cycles/byte on a Core i7-7800X (AVX-512), i5-6500 and i5-4570 (AVX2), against 4.28/5.56/7.09 for SHAKE128 and 6.65/6.91/9.27 for SHA-256 (the fastest implementations found, often OpenSSL, cross-checked against eBASH) on CPUs without SHA-NI. Independent eBASH 2026 runs at about 16 KiB show K12 about 1.8x faster than SHAKE128 but slightly slower than SHA-NI SHA-256 (2.47 vs 2.21 cycles/byte on Tiger Lake).

## Use it when

- You want to stay in the Keccak/SHA-3 family (same permutation and cryptanalysis track record, 128-bit claim like SHAKE128) but SHAKE128 is too slow: even serially (8 KiB or less), KT128 is about 1.8x faster than SHAKE128 (paper Table 2; eBASH gives 2.77 vs 4.98 cycles/byte at 1536 B on Tiger Lake).
- Hashing large single buffers (tens of KiB and up) on x86-64 with AVX2 or AVX-512: the paper reports 1.22-1.44 cycles/byte on Skylake/Haswell and 0.55 on SkylakeX, against 4.28-7.09 for SHAKE128.
- ARMv8.4-A cores with SHA-3 instructions (Apple A14/M1): the Keccak team reports 0.75 cycles/byte for KT128, 1.7x hardware SHA-256 (a first-party figure).
- Protocols that want a standardized fast XOF with domain separation: KT128/KT256 are specified in RFC 9861.
- Projects that also need other Keccak-team constructions (SHA-3, SHAKE, cSHAKE/KMAC, TurboSHAKE, Xoodyak) from one mostly CC0 code base.

## Skip it when

- Short to medium messages on x86 CPUs with SHA-NI: in eBASH 2026 at about 16 KiB, K12 takes 2.47 cycles/byte on Tiger Lake and 2.93 on Zen 4, against 2.21/2.02 for SHA-256, so it is slower than hardware SHA-256 there.
- When FIPS 202 / FIPS 140 compliance is required: KT128 is not one of the six approved FIPS 202 instances, and its 12-round permutation has a smaller margin (the paper claims 7 of 12 rounds).
- Streaming input in small pieces: the SIMD multi-leaf path runs only when a single Update call still holds 16/32/64 KiB of full 8 KiB leaves (2/4/8-way); 4-16 KiB reads fall back to serial speed.
- When you need multi-core hashing out of the box: XKCP's K12 is single-threaded (SIMD only) and has no parallel API like BLAKE3's update_rayon.
- MSVC/Windows builds: the fast x86 assembly uses GCC syntax, so MSVC needs the \*noAsm targets, and libXKCP.dll does not link yet.

## How it is fast

It makes two changes to SHAKE128. First, the permutation is Keccak-p[1600] reduced to 12 rounds (TurboSHAKE), roughly halving the per-block cost. Second, a Sakura-coded tree mode cuts the input into 8 KiB leaves whose chaining values feed a final node, and 'kangaroo hopping' merges the first chunk into that final node so inputs of 8 KiB or less pay no tree overhead. Independent leaves go through 2-, 4- or 8-way parallel Keccak-p code (SSSE3/AVX2/AVX-512, chosen at runtime by the x86-64 target), where AVX-512 rotate and ternary-logic instructions and its 32 registers cut the instruction count further.

## Compared with alternatives

Pick K12 over BLAKE3 when you want to stay in the Keccak/SHA-3 family (RFC 9861, KT256 for 256-bit security) or target ARMv8.4-A SHA-3 hardware; pick BLAKE3 for peak speed at shorter lengths (1 KiB vs 8 KiB leaves), multithreading and a maintained Rust crate. Versus sha256-simd, ISA-L multi-buffer SHA, j-lanes and S-HASH, K12 fits when you can change the digest and hash single long messages, not many parallel SHA-256 streams.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (libXKCP via make &lt;target&gt;/libXKCP.a\|.so), or source-drop via the .pack targets / HOWTO-customize; the trimmed K12-only package lives at github.com/XKCP/K12 |
| **Dependencies** | none at runtime. Building needs GCC or clang, GNU make and xsltproc, plus initialized git submodules. |
| **Minimum toolchain** | not documented (no C standard stated). The README requires GCC or clang, GNU make and xsltproc; MSVC works only through generated .vcxproj files and noAsm targets. |
| **Platforms** | x86-64 (runtime dispatch among plain 64-bit, SSSE3, AVX2 and AVX-512); fixed targets for AVX/XOP/AVX2/AVX512, ARMv6/ARMv6M/ARMv7M/ARMv7A/ARMv8A (with an aarch64 dispatch and SHA-3-instruction cores) and AVR8; generic32/generic64 plain C elsewhere |
| **Thread safety** | Functions work on caller-owned instances (KangarooTwelve_Instance) with no internal threading or locking, so use one instance per thread. On GCC/clang, x86-64 CPU detection runs once in a constructor before main to avoid races; the XKCP_Disable\*() switches set process-wide globals. |
| **Drop-in for the baseline** | partial — KT128 output differs from SHAKE128/SHA-256, so it cannot replace them in existing formats. The same library's SimpleFIPS202/KeccakHash interfaces do produce bit-compatible SHA-3/SHAKE, but through a different API from OpenSSL's. |

## Gotchas

- Licensing is mixed: the AVX2/AVX-512 single-permutation Keccak-p assembly is CRYPTOGAMS (BSD-style or GPL), the ARMv8-A cores are Apache-2.0/ISC/MIT, and only the rest is CC0 (which gives no patent grant). Keep the LICENSE file when redistributing.
- Past memory-safety bug: CVE-2022-37454 (GHSA-6w4m-2xhg-2658, critical) was a buffer overflow in the sponge queue when a partial input reached 2^32-200 bytes or more, fixed in commit fdc6fef. Open issue #171 (Aug 2026) reports UBSan misaligned loads in the AVX2 times4 code.
- Makefile.build is XML that xsltproc expands into a makefile; there is no CMake or pkg-config support. Pick a SIMD-capable target (e.g. x86-64/libXKCP.a), because generic32/generic64 are plain C and will not reach the headline numbers.
- Headline numbers are single-core and need very long messages: parallelism starts only after the first 8 KiB, and 4-way needs 5 chunks (40 KiB) on the paper's Skylake plot. eBASH's 16 KiB 'long message' metric therefore shows K12 near its serial speed.

## Known shortcomings

- KangarooTwelve's '2x SHAKE128' holds for low-end CPUs and short messages; on modern x86 eBASH shows it slower than SHA-NI SHA-256. The fast x86 assembly comes from CRYPTOGAMS under its own license, not CC0.
- K12 evidence is the designers' 2018 paper on pre-SHA-NI CPUs with no compiler stated; eBASH 2026 at \~16 KiB has K12 slower than SHA-NI SHA-256 (2.47 vs 2.21 cycles/byte Tiger Lake, 2.93 vs 2.02 Zen 4) and \~1.8x faster than SHAKE128. SIMD path engages only when one Update call carries &gt;= 16/32/64 KiB; no multithreading API. Not FIPS-approved. Build needs xsltproc + GNU make; MSVC gets noAsm only. CVE-2022-37454 buffer overflow (fixed); open #171 UBSan misaligned loads in AVX2 times4.

## Caveats and trade-offs

The paper's authors are K12's designers, and its 2016-2018 hardware predates SHA-NI. The keccak.team page gives KT128 at 1.4 c/b with AVX2 and 0.51 c/b with AVX-512, and 0.75 c/b on Apple A14/M1 with ARMv8-A SHA-3 instructions (1.7x hardware SHA-256, 3x hardware SHA-512). That page's 'roughly twice faster than SHAKE128' applies to low-end platforms and short messages, not to the AVX2/AVX-512 figures. Independent eBASH 2026 data at \~16 KiB (too short for K12's 8 KiB-leaf parallelism to be fully used) tells a different story. On a Core i7-1165G7, K12 runs at 2.47 c/b vs SHA-256 at 2.21, so K12 is slower than SHA-NI SHA-256, though \~1.8x faster than SHAKE128 (4.49) and \~2.2x faster than SHA3-256 (5.50). On a Ryzen 7 7700 it runs at 2.93 vs SHA-256 at 2.02. No compiler or flags are stated in the paper or on the page. The fast x86 AVX2/AVX-512 cores are CRYPTOGAMS-licensed rather than CC0, and the CC0 parts carry no patent grant.

KangarooTwelve (12-round Keccak-p variant) is an XOF, not a drop-in SHA-3/SHAKE replacement -- smaller security margin (12 vs 24 rounds) in exchange for speed; needs the XKCP AVX2/AVX-512 target build to hit the stated numbers.

## Maintenance

Actively maintained by the Keccak team (commits through 2026-09-25, including recent alignment and aliasing fixes; 664 stars) and mostly CC0, but the fast x86 cores carry CRYPTOGAMS terms, so vendor it through the .pack targets or the trimmed XKCP/K12 repo and keep the LICENSE file.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded C-&gt;B. The peer-reviewed KangarooTwelve paper (IACR ePrint 2016/770; ACNS 2018, LNCS, DOI 10.1007/978-3-319-93387-0_21) has a Table 2 comparing K12 with SHAKE128 and SHA-256 on three named Intel CPUs. For traditional hashes it uses the fastest implementations, 'often' OpenSSL's, cross-checked with eBASH. It states no compiler or flags, so it is not A. The keccak.team page alone is first-party with no methodology (C).
- **Verifier notes:** The keccak.team numbers are present, but the record attached the '\~2x SHAKE128' claim to the wrong context. I switched benchmark_url to the peer-reviewed paper, which gives the tier B evidence. eBASH's per-implementation page could support an A-grade comparison of k12 against OpenSSL shake128/sha3256 at 1536 bytes, but it does not label the message length, so I did not claim A. Metadata checks out: 664 stars, last commit 2026-09-25, not archived.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `baseline`, `workload`, `hardware`, `license`, `caveats`
- **Shortcomings recorded by:** ePrint 2016/770 (ACNS 2018) Table 2: K12 0.55/1.22/1.44 vs SHAKE128 4.28/5.56/7.09 cycles/byte.; eBASH \~16 KiB: K12 2.47 vs SHA-256 (SHA-NI) 2.21 cycles/byte (Tiger Lake); 2.93 vs 2.02 (Zen 4).
- **Pages the verifier opened:**
  - <https://keccak.team/kangarootwelve.html>
  - <https://eprint.iacr.org/2016/770.pdf>
  - <https://api.crossref.org/works?query.bibliographic=KangarooTwelve+fast+hashing+based+on+Keccak-p&rows=2>
  - <https://github.com/XKCP/XKCP>
  - <https://github.com/XKCP/XKCP/blob/master/LICENSE>
  - <https://bench.cr.yp.to/results-hash/amd64-panther.html>
  - <https://bench.cr.yp.to/results-hash/amd64-hertz.html>
  - <https://bench.cr.yp.to/web-impl/amd64-panther-crypto_hash.html>
- **Sources the enricher read:**
  - <https://github.com/XKCP/XKCP>
  - <https://github.com/XKCP/XKCP/blob/master/README.md>
  - <https://github.com/XKCP/XKCP/blob/master/LICENSE>
  - <https://github.com/XKCP/XKCP/blob/master/lib/high/KangarooTwelve/KangarooTwelve.h>
  - <https://github.com/XKCP/XKCP/blob/master/lib/high/KangarooTwelve/KangarooTwelve.c>
  - <https://github.com/XKCP/XKCP/blob/master/lib/low/x86-64-dispatch/x86-64-dispatch.c>
  - <https://github.com/XKCP/XKCP/blob/master/lib/low/x86-64-dispatch/x86-64-dispatch.h>
  - <https://github.com/XKCP/XKCP/blob/master/Makefile.build>
  - <https://github.com/XKCP/XKCP/blob/master/Makefile.ci>
  - <https://github.com/XKCP/XKCP/blob/master/.github/workflows/ci.yml>
  - <https://github.com/XKCP/XKCP/blob/master/usage-example.md>
  - <https://github.com/XKCP/XKCP/commits/master>
  - <https://github.com/XKCP/XKCP/issues>
  - <https://github.com/XKCP/XKCP/issues/171>
  - <https://github.com/XKCP/XKCP/issues/170>
  - <https://github.com/XKCP/XKCP/issues/105>
  - <https://github.com/advisories/GHSA-6w4m-2xhg-2658>
  - <https://github.com/XKCP/K12>
  - <https://eprint.iacr.org/2016/770.pdf>
  - <https://keccak.team/kangarootwelve.html>
  - <https://keccak.team/sw_performance.html>
  - <https://bench.cr.yp.to/results-hash/amd64-panther.html>
  - <https://bench.cr.yp.to/results-hash/amd64-hertz.html>
  - <https://bench.cr.yp.to/web-impl/amd64-panther-crypto_hash.html>
  - <https://raw.githubusercontent.com/BLAKE3-team/BLAKE3-specs/master/blake3.pdf>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/xkcp/xkcp`) · [data/wave7/enrich/raw/github_com_xkcp_xkcp.json](../../../data/wave7/enrich/raw/github_com_xkcp_xkcp.json) (enrichment confidence 0.8)

</details>
