# SFVInt

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Integer compression and bit-packing](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · ⚪ unknown

> DaMoN 2024 paper: BMI2 PEXT/PDEP LEB128 varint decoder claiming up to 2x over Folly and Protobuf; no public code.

| | |
|---|---|
| **Beats** | Facebook Folly and Google Protobuf LEB128 varint decoders |
| **Claimed result** | Abstract (search snippets only; arXiv blocked): about 500 lines of code achieve 'up to a 2x increase in decoding speed' compared with varint decoding in Facebook Folly and Google Protobuf; handles 32-bit and 64-bit unsigned integers with one C++ template using BMI2 PDEP/PEXT. |
| **Workload** | Decoding LEB128 varints using BMI2 (PDEP/PEXT), about 500 lines of code, on Intel m6i instances. |
| **Metric** | throughput |
| **Hardware** | Intel m6i instances (AWS) per snippet |
| **Adoption** | DaMoN 2024 workshop paper (ACM DOI 10.1145/3662010.3663439, arXiv 2403.06898); authors Gang Liao (University of Maryland) with Ye Liu, Yonghua Ding, Le Cai and Jianjun Chen (ByteDance) |
| **Links** | [benchmark](https://arxiv.org/abs/2403.06898) |

## Verdict

Only the abstract was seen (as search snippets): up to 2x faster LEB128 decoding than Facebook Folly and Google Protobuf varint decoders on AWS Intel m6i instances, for 32-bit and 64-bit values; one snippet cites 3.1 ms to 1.6 ms on a 'Web2' workload. Compiler, flags, library versions, datasets and per-length results were not readable here.

## Use it when

- You must keep the LEB128/protobuf varint wire format (existing files, RPC payloads, column stores) and varint decode shows up in profiles.
- Intel Haswell or later, or AMD Zen 3 or later, where PEXT/PDEP run in hardware.
- Mixed-length 64-bit varints where the scalar loop's data-dependent branches mispredict.
- You are willing to write and fuzz your own decoder from the paper's description.

## Skip it when

- AMD Zen, Zen+ and Zen 2: PDEP/PEXT are microcoded there and much slower (varint-simd's README documents this), so a BMI2 decoder can lose to the scalar loop.
- Non-x86 targets (aarch64, wasm): BMI2 does not exist; you need a separate path.
- You control the format: block formats such as Stream VByte, Masked VByte or SIMD bit-packing decode several times faster than any one-at-a-time LEB128 decoder.
- You need drop-in, tested code today: there is no public implementation to vendor.
- Untrusted input: bounds handling, overlong-encoding and malformed-input behaviour are not documented in anything readable here.

## How it is fast

Instead of the byte-at-a-time test-and-branch loop, it loads several bytes at once and uses BMI2 PEXT with a continuation-bit mask (search snippets quote masks 0x0000808080808080, 0x0080808080808080 and 0x8080808080808080 for six, seven and eight bytes) to gather the MSBs, then PEXT/PDEP to compact the 7-bit payload groups into the integer in a few instructions. The baseline it beats, folly::tryDecodeVarint, is an unrolled chain of up to ten load/test/branch steps per value.

## Compared with alternatives

Pick the technique over Stream VByte or MaskedVByte only when the LEB128 wire format is fixed; varint-simd (Rust, SSSE3/AVX2, public code and benchmarks on an i7-8850H) solves the same problem and is the safer starting point for a port to C++.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | not documented (no public code); needs BMI2 intrinsics (_pext_u64/_pdep_u64) |
| **Minimum toolchain** | not documented; C++ templates plus BMI2 intrinsics (e.g. -mbmi2) |
| **Platforms** | x86-64 with BMI2 only; fast only where PDEP/PEXT are in hardware (Intel Haswell+, AMD Zen 3+) |
| **Thread safety** | not documented (a stateless decode function would be reentrant) |
| **Drop-in for the baseline** | partial: same LEB128 format and per-value decode, but no published code or API to drop in |

## Gotchas

- No code: the 2x figure cannot be reproduced or checked; the verifier and this enricher found nothing under the first author's GitHub account (gangliao).
- A multi-byte load with a PEXT mask likely reads up to 8 bytes past the value start; the paper's padding or tail rule could not be read here, so check this before decoding at buffer ends.
- Folly's baseline already has a bounds-checked fast path only when 10+ bytes remain and reports TooManyBytes/TooFewBytes errors; a faster decoder that drops those checks is not a like-for-like comparison.

## Known shortcomings

- Tier C, paper only (arXiv 2403.06898 blocked): BMI2 varint decoding up to 2x over folly and protobuf on m6i; no code found. Candidate for a paper retier.
- No public code, licence or API; the paper body is unreadable here (arXiv blocked, paperhub mirror 403). PDEP/PEXT are microcoded on AMD Zen, Zen+ and Zen 2, so the m6i (Intel) numbers do not carry over. Likely 8-byte loads past the value start with undocumented padding. The Folly baseline (Varint.h) is an unrolled branchy loop with bounds and error checks, so it may not be like-for-like.

## Caveats and trade-offs

Snippet only: arXiv (EGRESS_BLOCKED), ACM and a review site (themoonlight.io, EGRESS_BLOCKED) could not be opened, so the numbers, hardware and methodology are unchecked; the 'Intel m6i instances' hardware in the record did not appear in any snippet I saw. No public code found: the first author's GitHub account (gangliao, 68 repos) has no repository matching varint. Folly itself has a BMI2 (PDEP) varint commit, so the baseline may already use similar tricks for encoding.

Needs BMI2 (Intel Haswell+, AMD Zen). Decodes one LEB128 varint at a time, not a SIMD batch format.

## Maintenance

Peer-reviewed workshop paper (DaMoN 2024, authors from University of Maryland and ByteDance) with no public code, licence or maintenance; treat as a reference design (usability: reference), tier C until the paper body is read.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** Peer-reviewed DaMoN 2024 paper whose abstract (seen only as consistent search snippets of arXiv 2403.06898 and the ACM page) claims up to 2x faster LEB128 decoding than Folly and Protobuf; the paper body, hardware and methodology could not be opened here, and no code was found, so it stays at C rather than B.
- **Verifier notes:** Paper and venue confirmed via search results; code not found and paper unreadable here. Candidate for a paper-access retier to B when arXiv is reachable. Left hardware uncorrected since I could not check it.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier; paper, first-party
- **Pages the verifier opened:**
  - <https://github.com/gangliao?tab=repositories&q=varint>
- **Sources the enricher read:**
  - <https://github.com/gangliao?tab=repositories&q=&type=source&sort=updated>
  - <https://raw.githubusercontent.com/as-com/varint-simd/HEAD/README.md>
  - <https://raw.githubusercontent.com/facebook/folly/main/folly/Varint.h>
  - WebSearch snippets of https://arxiv.org/abs/2403.06898, https://arxiv.org/html/2403.06898v4 and https://dl.acm.org/doi/10.1145/3662010.3663439 (pages themselves EGRESS_BLOCKED)
  - https://arxiv.org/html/2403.06898v4 (attempted, EGRESS_BLOCKED)
  - https://awesomepapers.io/systems-efficiency/papers/2403.06898 (attempted, EGRESS_BLOCKED)
  - https://paperhub.s3.amazonaws.com/2403.06898.pdf (attempted, HTTP 403)
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `paper:sfvint`) · [data/wave9/enrich/raw/paper_sfvint.json](../../../data/wave9/enrich/raw/paper_sfvint.json) (enrichment confidence 0.35)

</details>
