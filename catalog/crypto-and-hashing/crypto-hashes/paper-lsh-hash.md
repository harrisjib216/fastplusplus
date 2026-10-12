# LSH-256 / LSH-512 (Korean hash standard, TTAK.KO-12.0276)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Cryptographic hashes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `BSL-1.0 (the Crypto++ compilation is under the Boost Software License 1.0; individual files, including lsh256\*/lsh512\*.cpp, are placed in the public domain)` · 🟢 active

> Korean-standard LSH-256/LSH-512 hash; SUPERCOP's SIMD C code beats BLAKE2 and SHA-3 on long x86 messages.

| | |
|---|---|
| **Beats** | BLAKE2 (BLAKE2b vs LSH-512, BLAKE2s vs LSH-256) and SHA-3 (SHA3-512 / SHA3-256). Each eBASH row is the fastest SUPERCOP implementation of that function. For SHA-3 the winner is 'oncore64bits'; OpenSSL's SHA-3 is also measured and is 1.27-1.28x slower. |
| **Claimed result** | eBASH amd64-alder (Core i3-12100), long-message medians: LSH-512 2.14 cycles/byte vs BLAKE2b 3.36 (\~1.57x) and SHA3-512 11.25 (\~5.26x); LSH-256 3.13 vs BLAKE2s 5.24 (\~1.67x) and SHA3-256 5.96 (\~1.90x) (ratios derived from page data). Both variants also win at 576-4096 bytes but lose at 64 bytes (LSH-512 9.52, LSH-256 7.27 vs BLAKE2b 7.04, BLAKE2s 4.84 cycles/byte). BLAKE3 (1.73) and SHA-256 (2.05) are faster than both LSH variants on long messages. SUPERCOP's Crypto++-derived 'cryptopp' implementation is 2.92x slower than the best LSH-512 (11240 vs 3854 in the test-results Time column), which is \~2.2x slower than BLAKE2b's best (5142) but still \~1.56x faster than SHA3-512 (17498). For LSH-256 it is only 1.05x slower than the best (5503), still \~1.46x faster than BLAKE2s (8016) and \~1.74x faster than SHA3-256 (9597) (derived from page data). |
| **Workload** | eBASH/SUPERCOP crypto_hash timings on amd64-alder. Long-message cycles/byte is 1/16384 of the cycle-count difference between hashing 18208-byte and 1824-byte messages (per the page). Rows are medians (StQ2) of many measurements. The page also lists 8/64/576/1536/4096-byte figures. |
| **Metric** | throughput |
| **Hardware** | amd64-alder eBACS test machine: 2022 Intel Core i3-12100 (Golden Cove, model 90675-00), 4x3300MHz, supercop-20260831 |
| **Compiler and flags** | Per implementation on alder (SUPERCOP keeps the fastest compiler/flag combination; all use -fwrapv -fPIC -fPIE). LSH-512 avx2: Debian Clang 19.1.7 -march=native -O2. LSH-256 ssse3: Clang 19.1.7 -march=native -Os. BLAKE2b regs: gcc 14.2.0 -march=native -mtune=native -O. BLAKE2s avxicc: Clang 19.1.7 -march=native -O. SHA3-512 oncore64bits: gcc 14.2.0 -march=native -mtune=native -O2. SHA3-256 oncore64bits: gcc 14.2.0 -O3. Crypto++-derived LSH-512: g++ -march=native -mtune=native -O. Crypto++-derived LSH-256: clang++ -march=native -O3. |
| **Adoption** | 5,506 stars (Crypto++ library) |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://bench.cr.yp.to/supercop.html) · [benchmark](https://bench.cr.yp.to/results-hash/amd64-alder.html) |

## Verdict

eBASH on alder (Intel Core i3-12100, Golden Cove, supercop-20260831), long-message medians: LSH-512 (NSR avx2 code, Clang 19.1.7 -O2) 2.14 cycles/byte vs BLAKE2b 3.36 and SHA3-512 11.25, and LSH-256 (ssse3, Clang -Os) 3.13 vs BLAKE2s 5.24 and SHA3-256 5.96. Each row is the fastest implementation+compiler pair SUPERCOP found for that function, picked by the time to hash 1536 bytes (for example 3854 cycles for LSH-512 avx2).

## Use it when

- A Korean-standard hash (LSH, TTAK.KO-12.0276) is required and you want the fastest known code for it on x86-64.
- Long messages (576 bytes and up) on x86-64 with AVX2 that need a 512-bit digest: on alder LSH-512 runs 2.14 cycles/byte vs SHA-512 5.02 and SHA3-512 11.25.
- AMD Zen 4, where the margin is larger: LSH-512 1.72 vs BLAKE2b 3.52 cycles/byte and LSH-256 2.61 vs BLAKE2s 5.53 (hertz, Ryzen 7 7700).
- You want code that SUPERCOP lists with constant-time goals: both chosen implementations ship goal-constbranch/goal-constindex files recording a TIMECOP pass.

## Skip it when

- Short messages: at 64 bytes on alder LSH-512 (9.52) and LSH-256 (7.27 cycles/byte) lose to BLAKE2s (4.84), SHA-256 (4.69) and BLAKE3 (3.12). At 8 bytes they cost 60-77 cycles/byte.
- When BLAKE3 or SHA-NI SHA-256 is acceptable: both beat LSH on long messages (alder BLAKE3 1.73, SHA-256 2.05; Zen 4 BLAKE3 0.60 cycles/byte).
- ARM: on a Raspberry Pi 5 (Cortex-A76, supercop-20251222) LSH-512 only ties BLAKE2b (3.76 cycles/byte), LSH-256 is slower than BLAKE2s (6.88 vs 6.22), and SHA-256 with the ARMv8 crypto extensions (2.03) beats both.
- You need broad interoperability or a long cryptanalysis record: LSH has few implementations and little outside analysis. A withdrawn 2015 ePrint (2015/494) showed free-start collisions on full LSH because it has no feed-forward, though this is not a practical collision on the standard hash.
- You want a packaged, maintained library: the only one found is Crypto++, and SUPERCOP measures its LSH-512 at 2.92x slower than the NSR AVX2 code (11240 vs 3854 cycles for 1536 bytes).

## How it is fast

LSH is an ARX design (add, rotate, xor) with a 16-word chaining value split into left/right halves and a wide-pipe Merkle-Damgard mode. The AVX2 LSH-512 code keeps the whole chaining value in four 256-bit registers and runs 28 steps using vector adds, shift-or rotations, byte-granular rotations via _mm256_shuffle_epi8 and word permutations via _mm256_permute4x64_epi64. Message expansion is vectorized the same way. The SSSE3 LSH-256 code does the same with 128-bit registers and pshufb over 26 steps, and on this CPU it edges out the AVX2 LSH-256 code (5231 vs 5401 cycles for 1536 bytes).

## Compared with alternatives

Pick LSH over BLAKE3, blake2_simd, KangarooTwelve (XKCP) or SHA-NI SHA-256 only when LSH itself is mandated, or when you need a 512-bit digest on AVX2 x86 and cannot use BLAKE3. On alder BLAKE3 (1.73) and SHA-256 (2.05) are faster, while LSH-512 (2.14) beats BLAKE2b (3.36) and K12 (2.67).

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (compiler intrinsics headers only) |
| **Minimum toolchain** | C99 compiler with SSSE3/AVX2 intrinsics (ifdefs also cover MSVC); SUPERCOP's fastest builds used Debian Clang 19.1.7 with -march=native |
| **Platforms** | x86/amd64 per the architectures file; lsh512/avx2 needs AVX2, lsh256/ssse3 needs SSSE3; separate ref, sse2, xop and neon directories exist |
| **Thread safety** | No mutable globals in the source (tables are static const); all state lives in a caller-owned context, so use one context per thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Lengths are in bits: lsh512_update/lsh512_digest take databitlen (SUPERCOP's wrapper passes 8\*inlen), so one call covers at most 512 MiB when size_t is 32 bits, and any update after a non-multiple-of-8 bit length returns LSH_ERR_INVALID_DATABITLEN.
- Each SUPERCOP directory is a single ISA variant chosen at compile time (LSH_USE_AVX2); there is no CPUID dispatch, and lsh.h declares lsh_init_simd()/lsh_get_simd_type(), which the per-variant lsh-impl.c does not define. Call the lsh512_\*/lsh256_\* functions from lsh-impl.h and add your own dispatch.
- The fastest variant differs by width and CPU. On alder, LSH-256's winner is ssse3, not avx2, and LSH-512's ssse3 code (5206 cycles) is no faster than ref (5203), so benchmark on your target instead of assuming AVX2 is best.
- The comments are in Korean. The header says the output buffer must be aligned, but the code uses unaligned stores plus memcpy. lsh512_final wipes the context with a plain memset, which the compiler may remove.

## Known shortcomings

- The wins come from SUPERCOP's AVX2/SSSE3 LSH implementations, not Crypto++: SUPERCOP's 'cryptopp' LSH-512 is 2.92x slower and falls behind BLAKE2b. LSH loses at 64-byte messages, and BLAKE3 and SHA-NI SHA-256 are faster. Korean national standard with little use outside Korea.
- The fast code is NSR's 2016 C99 implementation under an MIT-style license (not Crypto++'s BSL-1.0 code). KS X 3262 designation not verified; KISA lists TTAK.KO-12.0276. Loses on short inputs and on Raspberry Pi 5 (ARM); each SUPERCOP folder builds for one CPU feature set with no runtime detection. Wide-pipe Merkle-Damgard; LSH-512 block is 256 bytes.

## Caveats and trade-offs

The eBASH headline numbers come from SUPERCOP's own avx2 (LSH-512) and ssse3 (LSH-256) implementations, not from Crypto++. SUPERCOP also benchmarks a 'cryptopp' LSH implementation: on alder it is 2.92x slower than the best for LSH-512, which puts it behind BLAKE2b, and 1.05x slower for LSH-256. It is not known whether that build uses Crypto++'s lsh512_avx.cpp path. Crypto++'s LSH code (lsh256/lsh512 .cpp plus _sse/_avx) was written by Jeffrey Walton from KISA's specification and reference code. LSH loses to BLAKE2 on short (64-byte and 8-byte) messages, and BLAKE3 and SHA-NI SHA-256 beat it on long messages on this CPU. IACR eprint 2015/494 (withdrawn) described free-start collision and pseudo-preimage attacks on full-round LSH, possible because LSH has no feed-forward, plus 14-round boomerang attacks; none is a practical collision on the standard hash. The ISO/IEC 10118-3 inclusion claim was not verified. The Crypto++ compilation is BSL-1.0 and the individual files are public domain.

LSH uses a wider 128-byte block and a generalized-Feistel structure unrelated to Merkle-Damgard SHA-2 or sponge-based SHA-3/BLAKE2; far fewer independent implementations, audits, and years of cryptanalysis than SHA-2/SHA-3/BLAKE2. Only actively-maintained C/C++ library implementation found is Crypto++ (SSE2/AVX2 code, header cites Korea Internet & Security Agency spec).

## Maintenance

The NSR code (2016, MIT-style permissive license, about 20-25 KB of C per variant) was added in supercop-20240625 and has not changed in the jedisct1 mirror since; it is small enough to vendor, and SUPERCOP itself is actively released (20260831).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now B.
- **Tier reason:** eBACS/eBASH is a well-known independent suite. SUPERCOP is public, and the alder test-results page gives the compiler and flags for every implementation, so the method would reach A for the algorithm. The headline LSH numbers come from SUPERCOP's own avx2 (LSH-512) and ssse3 (LSH-256) implementations, not from the cataloged Crypto++ code, so the tier stays at B.
- **Verifier notes:** The numbers for both variants match the alder results page exactly. The compiler and flags per implementation are on https://bench.cr.yp.to/web-impl/amd64-alder-crypto_hash.html. repo_url (Crypto++) is not the code that produced the headline numbers. Consider pointing the entry at SUPERCOP's avx2/ssse3 LSH implementations; if the entry is kept as algorithm-level, A-level methodology exists. GitHub reports license NOASSERTION; License.txt says Boost 1.0 for the compilation. last_commit 2026-09-23 and active status confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `workload`, `compiler_and_flags`, `license`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** eBASH (alder): LSH-512 2.14 vs BLAKE2b 3.36, SHA3-512 11.25 cycles/byte; LSH-256 3.13 vs BLAKE2s 5.24, SHA3-256 5.96.
- **Pages the verifier opened:**
  - <https://bench.cr.yp.to/results-hash/amd64-alder.html>
  - <https://bench.cr.yp.to/web-impl/amd64-alder-crypto_hash.html>
  - <https://bench.cr.yp.to/impl-hash/lsh512.html>
  - <https://bench.cr.yp.to/impl-hash/lsh256.html>
  - <https://bench.cr.yp.to/primitives-hash.html>
  - <https://github.com/weidai11/cryptopp>
  - <https://github.com/weidai11/cryptopp/blob/master/License.txt>
  - <https://github.com/weidai11/cryptopp/blob/master/lsh512.cpp>
  - <https://eprint.iacr.org/2015/494>
- **Sources the enricher read:**
  - <https://bench.cr.yp.to/supercop.html>
  - <https://bench.cr.yp.to/results-hash/amd64-alder.html>
  - <https://bench.cr.yp.to/web-impl/amd64-alder-crypto_hash.html>
  - <https://bench.cr.yp.to/impl-hash/lsh512.html>
  - <https://bench.cr.yp.to/impl-hash/lsh256.html>
  - <https://bench.cr.yp.to/primitives-hash.html>
  - <https://bench.cr.yp.to/results-hash/amd64-hertz.html>
  - <https://bench.cr.yp.to/results-hash/aarch64-pi5.html>
  - <https://github.com/jedisct1/supercop/tree/master/crypto_hash/lsh512/avx2>
  - <https://github.com/jedisct1/supercop/tree/master/crypto_hash/lsh256/ssse3>
  - <https://github.com/jedisct1/supercop/blob/master/crypto_hash/lsh512/cryptopp/hash.cpp>
  - <https://github.com/jedisct1/supercop/commits/master/crypto_hash/lsh512/avx2>
  - <https://github.com/weidai11/cryptopp/blob/master/lsh512.cpp>
  - <https://github.com/weidai11/cryptopp/blob/master/lsh.h>
  - <https://eprint.iacr.org/2015/494>
  - <https://seed.kisa.or.kr/kisa/algorithm/EgovLSHInfo.do>
  - <https://api.crossref.org/works?query.bibliographic=LSH+A+New+Fast+Secure+Hash+Function+Family>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `paper:lsh-hash`) · [data/wave7/enrich/raw/paper_lsh_hash.json](../../../data/wave7/enrich/raw/paper_lsh_hash.json) (enrichment confidence 0.65)

</details>
