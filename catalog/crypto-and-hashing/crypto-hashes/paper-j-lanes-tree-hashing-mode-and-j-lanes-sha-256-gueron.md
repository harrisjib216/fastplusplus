# j-lanes tree hashing mode and j-lanes SHA-256 (Gueron)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Cryptographic hashes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `any` · `no license` · 🔵 finished

> Tree-hash mode that runs one message as 4 interleaved SHA-256 lanes on AVX; 2-2.5x OpenSSL 1.0.1c, different digests.

| | |
|---|---|
| **Beats** | OpenSSL SHA-256 (v1.0.1c) |
| **Claimed result** | 4-lanes SHA-256 is 1.97-2.53x faster than OpenSSL 1.0.1c for 2KB-128KB messages (Fig. 3: 13.27 vs 6.75 c/B at 2KB; 12.78 vs 5.05 c/B at 128KB). The abstract gives \~2 to \~2.5x. Against the fastest serial implementation (the authors' own n-SMS) it is 1.5-1.97x per the abstract and 1.55-2x per Sec. 3. At 8KB it is also faster than tree-mode BLAKE and Keccak (Fig. 4). |
| **Workload** | SHA-256 hashing of single messages ranging 2KB-132KB, using a 4-lanes SIMD tree-hashing mode (j=4) on AVX, versus standard serial SHA-256 |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-3770 (3rd Gen Core, Ivy Bridge, AVX), with Hyper-Threading, Turbo Boost and Enhanced SpeedStep disabled |
| **Links** | [benchmark](https://eprint.iacr.org/2012/476.pdf) |

## Verdict

On a Core i7-3770 (Ivy Bridge; Hyper-Threading, Turbo and SpeedStep off; RDTSC, minimum of 5 runs of 100,000 iterations), AVX 4-lanes SHA-256 took 6.75 c/B at 2KB and 5.05 c/B at 128KB, against 13.27 and 12.78 c/B for OpenSSL 1.0.1c's serial SHA-256 (1.97-2.53x) and 10.45-10.09 c/B for the authors' improved n-SMS serial code (1.55-2x). No compiler or flags are given, and the outputs are j-lanes digests, not SHA-256 digests.

## Use it when

- You own both ends of the format and can define a new digest, for example signed boot or firmware images or an internal integrity manifest, and messages are at least a few KB. The paper measured 1.97x at 2KB rising to 2.53x at 128KB against OpenSSL 1.0.1c.
- One long message at a time, where multi-buffer hashing (S-HASH) has nothing to run in parallel.
- x86 cores with 128-bit or 256-bit SIMD but no SHA extensions (the paper used Ivy Bridge AVX; the 2014 follow-up also measured Haswell AVX2 with j=8).
- As a design reference when specifying a SIMD-friendly tree mode: the 2014 spec gives slicing rules, IV derivation and test vectors.

## Skip it when

- Anywhere a standard SHA-256 value is expected: TLS, HMAC interop, signature schemes, Git or any content address shared with third parties. The digest is different by construction.
- Short messages. The fixed wrap and per-lane padding cost is only amortized on longer inputs; the paper says gains are fully realized only for 'sufficiently long' messages, and Intel's similar Multi-Hash paper says benefits diminish below about 1KB.
- When you need code today. Nothing was released. The nearest shipping code, Intel ISA-L crypto's mh_sha256 (16 word-interleaved segments), pads and wraps differently, so its digests are not j-lanes digests.
- CPUs with SHA extensions. The paper predates them and never compares against them. minio/sha256-simd's README reports 1979 MB/s for SHA-extension SHA-256 on a 3.7 GHz Ryzen 7 2700X, about 1.9 c/B, well under the paper's best 4-lanes figure of 5.05 c/B. The CPUs differ, so treat that comparison as rough.
- Settings that need a standardized or formally analysed mode. Security is argued only by pointing to general tree-hashing theory, and the author's own recommended j moved from 8 (2012) to 16 (2014).

## How it is fast

Serial SHA-256 is one dependent chain of compression calls. Slicing turns one message into j independent messages, which the authors' S-HASH multi-buffer kernel runs with one slice per 32-bit lane of a 128-bit AVX register, so each SIMD Update compresses 4 blocks at once. For a 256x-byte message this costs 4x+7 Updates instead of 4x+1: one padding block per lane plus 3 serial Updates to wrap the 128 bytes of digests. The 4x bulk Updates run 4-wide. Word interleaving means plain sequential loads put each word in the right lane with no transpose. Without SIMD the mode loses: calling OpenSSL once per slice took 13.57 c/B against 12.87 c/B for plain OpenSSL at 8KB.

## Compared with alternatives

Pick j-lanes over S-HASH only when there is a single long message in flight and you control the digest format. S-HASH needs many independent messages but keeps standard SHA-256 outputs. Against minio/sha256-simd, which is shipping Go code that produces standard digests (with SHA-extension, ARM64 and AVX-512 multi-buffer paths), j-lanes is only a design option for a new format on hardware without SHA instructions.

## Integration

| | |
|---|---|
| **Form** | not applicable: a paper and specification only, with no code released |
| **Dependencies** | not documented (no code). The measured implementation was built on the authors' unreleased S-HASH AVX kernel. |
| **Minimum toolchain** | not documented: the paper gives no compiler, version or flags |
| **Platforms** | The construction is portable. Measurements are on x86-64 with AVX (Core i7-3770, Ivy Bridge), and the 2014 follow-up also used Haswell (AVX2). Scalar or per-slice serial evaluation works but is slower than plain SHA-256. |
| **Thread safety** | not documented. The paper notes the slices can also be spread across cores. |
| **Drop-in for the baseline** | no |

## Gotchas

- There are two incompatible versions. The 2012 mode uses the standard SHA-256 IV everywhere, while the 2014 spec prepends per-lane prefix blocks (lane index, j, a mode byte and 'SHA256'), which gives different IVs and different digests. Pin the spec version and j, because the digest depends on both.
- The 2014 spec text slices by 32-bit words, but its j=4 test-vector lanes are interleaved in 64-byte blocks (lane 0 is message bytes 0-63, 256-319, 512-575 and 768-831). Resolve this against the vectors before implementing.
- With j=4, a length not divisible by 256 bytes leaves at least one slice a different length and needs special last-Update handling (the paper calls the cost negligible). Very short messages give empty slices, which are hashed as the empty message. Choosing j above the SIMD width adds wrap Updates: at 8KB, 16-lanes needs 153 Updates against 135 for 4-lanes.
- The SHA-3 comparison in Fig. 4 is close. At 8KB, 4-lanes SHA-256 took 5.46 c/B against 5.74 for 4-lanes BLAKE-512 and 5.82 for plain BLAKE-512, a margin of about 5-7%.

## Known shortcomings

- New tree-hashing mode: digests differ from standard SHA-256, so it is not a drop-in replacement. Published in a weak venue (JIS 2013); measured on an i7-3770 (Ivy Bridge).
- No code, no compiler or flags. Compared against OpenSSL 1.0.1c on a 2012 CPU with no SHA-NI comparison (minio's Ryzen SHA-extension figure \~1.9 cycles/byte vs the paper's best 5.05, different CPUs). The 2012 paper and the 2014 spec (ePrint 2014/170) produce incompatible digests (per-lane IVs). Nearest shipping code, ISA-L mh_sha256, is not digest-compatible. Lead over BLAKE-512 only \~5-7%.

## Caveats and trade-offs

j-lanes SHA-256 is a different hash construction: a tree mode whose digest differs from standard SHA-256, and the paper itself says it would need distinct IVs if standardized. It is not a drop-in replacement for OpenSSL SHA-256. The 'fastest publicly available' comparator is the author's own n-SMS code. No compiler or flags are stated and no code is released. The results are from 2012 hardware against OpenSSL 1.0.1c, which predates OpenSSL's AVX2 and SHA-NI SHA-256 paths. The peer-reviewed venue is a SCIRP journal, a publisher whose review standards are widely questioned.

Requires restructuring hashing into a tree mode (message split into j independent SIMD lanes, then combined), which changes the digest unless both hasher and verifier use the same mode; needs AVX; author was an Intel researcher and later pushed related multi-buffer techniques toward OpenSSL/ISA-L.

## Maintenance

This is finished research: ePrint 2012/476, republished in Journal of Information Security 4(1):7-11 (2013, a SCIRP journal, 2 Crossref citations), plus a 2014 follow-up spec with test vectors (ePrint 2014/170, CC BY). No code or standard adoption turned up in the sources read, and the closest shipping relative, ISA-L's mh_sha256, is not digest-compatible.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The paper measures 4-lanes SHA-256 against OpenSSL 1.0.1c on an i7-3770 (Figs. 1-3: 12.78-13.27 vs 5.05-6.75 cycles/byte, 1.97-2.53x). It was peer-review published as Journal of Information Security 4(1):7-11, 2013 (DOI 10.4236/jis.2013.41002), with the same abstract numbers. There is no public code and no compiler or flags, so it is not A.
- **Verifier notes:** The claimed numbers check out against both the ePrint PDF and the JIS 2013 abstract. The main issue for enrichment is that j-lanes changes the digest, so this is a new hash mode, not a faster SHA-256. B rests on the JIS (SCIRP) publication; if the orchestrator does not count SCIRP as peer review, it drops to C.
- **Fields the verifier corrected:** `hardware`, `compared_against_cpp_std_directly`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://eprint.iacr.org/2012/476.pdf>
  - <https://doi.org/10.4236/jis.2013.41002>
  - <https://www.scirp.org/journal/paperinformation?paperid=27532>
  - <https://api.crossref.org/works/10.4236/jis.2013.41002>
- **Sources the enricher read:**
  - <https://eprint.iacr.org/2012/476.pdf>
  - <https://eprint.iacr.org/search?q=j-lanes>
  - <https://eprint.iacr.org/2014/170>
  - <https://eprint.iacr.org/2014/170.pdf>
  - <https://api.crossref.org/works/10.4236/jis.2013.41002>
  - <https://doi.org/10.4236/jis.2013.41002>
  - <https://eprint.iacr.org/2012/371.pdf>
  - https://github.com/intel/isa-l_crypto (README, include/isa-l_crypto/mh_sha256.h, mh_sha256/mh_sha256_internal.h, file tree)
  - <https://raw.githubusercontent.com/wiki/intel/isa-l_crypto/pdf/multi-hash-paper.pdf>
  - https://github.com/minio/sha256-simd (README, file tree)
  - <https://github.com/search?q=j-lanes&type=repositories>
  - <https://hn.algolia.com/api/v1/search?query=j-lanes>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `paper:j-lanes-tree-hashing-mode-and-j-lanes-sha-256-gueron`) · [data/wave7/enrich/raw/paper_j_lanes_tree_hashing_mode_and_j_lanes_sha_256_gueron.json](../../../data/wave7/enrich/raw/paper_j_lanes_tree_hashing_mode_and_j_lanes_sha_256_gueron.json) (enrichment confidence 0.8)

</details>
