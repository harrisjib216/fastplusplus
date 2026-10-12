# Simultaneous hashing of multiple messages / S-HASH (Gueron & Krasnov)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Cryptographic hashes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `any` · `no license` · 🔵 finished

> Multi-buffer SHA-256 that hashes 4 independent messages per AVX register with standard digests; 3.42x OpenSSL 1.0.1 on 4KB messages.

| | |
|---|---|
| **Beats** | OpenSSL SHA-256 (v1.0.1) |
| **Claimed result** | From L1/L2/LLC/memory (4KB messages): 5.18-5.21 c/B vs OpenSSL 1.0.1 at 17.72-17.80 c/B, 3.42x, and 2.25x vs the authors' own n-SMS serial code. From disk at the native 3.3GHz: 2.26x (UNIFORM directory, 8.65 vs 19.55 c/B) and 1.73x (DIVERSE directory). The abstract's '\~6.73 c/B, almost 3x' figure is with the CPU down-clocked to 1.6GHz (UNIFORM: 6.73 vs 19.26 c/B, 2.86x). |
| **Workload** | 4-buffer parallel (multi-buffer) SHA-256 hashing of multiple independent messages, measured from CPU cache/memory and from disk |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-2500 (Sandy Bridge, 3.3GHz; some disk runs down-clocked to 2.6/1.7/1.6GHz), Turbo Boost, Hyper-Threading and SpeedStep disabled, 8GB DDR3-1600, RAID0 of two Intel SSD 320, Fedora 16 |
| **Links** | [benchmark](https://eprint.iacr.org/2012/371.pdf) |

## Verdict

On a Core i5-2500 (Sandy Bridge, 3.3GHz; Turbo, HT and SpeedStep off; Fedora 16), 4-buffer AVX SHA-256 hashed 4KB chunks at 5.18-5.21 c/B from L1 through main memory. Serial OpenSSL 1.0.1 took 17.72-17.80 c/B (3.42x) and the authors' n-SMS took 11.68-11.81 c/B (2.25x). Hashing files from a two-SSD RAID0 at native clock gave 8.65 vs 19.55 c/B (2.26x) for eight equal 17.76MB files and 17.53 vs 30.32 c/B (1.73x) for 350 mixed-size files. No compiler or flags are stated.

## Use it when

- Many independent messages are ready at once and each needs a standard SHA-256 digest: boot-time integrity checks of OS components, dedup chunk fingerprints, file-tree manifests, or TLS/HMAC servers that batch work across connections (the paper's own scenarios).
- Messages of similar length. Eight equal 17.76MB files reached 2.26x over OpenSSL from disk at native clock, against 1.73x for 350 mixed Windows driver files, because equal lanes finish together.
- Data already in cache or RAM. On 4KB chunks, speed was flat at 5.18-5.21 c/B whether the data sat in L1, L2, LLC or main memory.
- Wide-SIMD x86 without SHA extensions. AVX2 doubles the lane count to 8 and AVX-512 to 16. minio's README reports 3498 MB/s per core with 16-lane AVX-512 on a Xeon Platinum 8124M, 7.8x its AVX2 path.

## Skip it when

- One message at a time, or latency-bound single-stream hashing. Only one lane does useful work. For that, use a fast serial or SHA-extension SHA-256, or a tree mode such as j-lanes if you control the format.
- Very uneven message sizes. Lanes stall until they are refilled and stragglers finish serially, which is why the mixed-size directory got only 1.73x.
- Pipelines limited by I/O. At 3.3GHz, the 400MB/s SSD RAID0 equals about 7.15 c/B, so S-HASH reached 8.65 c/B from disk rather than 5.2. The abstract's '\~6.73 c/B, almost 3x' needed the CPU down-clocked to 1.6GHz.
- Small messages or thin batches. OpenSSL's multi-buffer notes say real-world gains on 2KB fragments are 75-130% on Haswell, against a 170% asymptotic figure. minio's README advises plain SHA-256 below about 1MB for its channel-scheduled server.
- Code you would have to maintain yourself. Linux added AVX2 multibuffer SHA-256/512 in 4.8 (2016), then removed it in August 2018 because it was broken, too complex to maintain, and its 'performance benefits for real-world use cases are debatable'.

## How it is fast

This is SIMD across messages ('multi-buffer', first tried by Aciicmez in 2004 on Pentium 4 SSE2 for a 1.71x gain). Each lane holds one message's state, so one S-UPDATE compresses four 64-byte blocks from four messages with the same instruction stream. The scheduler runs min(remaining length)/64 blocks at a time, then finalizes or refills the lanes that ran out, and finishes any leftover buffers serially. The paper gives two reasons it falls short of 4x on Sandy Bridge: the scalar ALU path is faster than the SIMD unit, and each SHA-256 rotate costs two SIMD shifts plus an xor instead of one ROR.

## Compared with alternatives

Choose S-HASH (in practice ISA-L's sha256_mb) over j-lanes when you have many independent messages and need interoperable standard SHA-256 digests. j-lanes speeds up a single message but changes the digest. In Go, minio/sha256-simd already ships the same multi-buffer idea as its AVX-512 server alongside a drop-in crypto/sha256 replacement, so use it rather than porting the paper.

## Integration

| | |
|---|---|
| **Form** | not applicable: a paper only, with no S-HASH code released. The shipping equivalent is Intel ISA-L crypto sha256_mb, a C and assembly static or shared library. |
| **Dependencies** | not documented for the paper. ISA-L crypto needs nasm 2.14.01 or later on x86-64 per its README. |
| **Minimum toolchain** | not documented: the paper gives no compiler or flags. ISA-L crypto builds with gcc, clang, icc or MSVC 2019+, and on aarch64 with gas 2.34+ and gcc 8+. |
| **Platforms** | The paper measured x86-64 with AVX (Core i5-2500, Sandy Bridge, Fedora 16). ISA-L crypto's sha256_mb has SSE, AVX, AVX2 and AVX-512 (4, 8 and 16 lanes) plus SHA-NI variants, and aarch64 code, with runtime dispatch. |
| **Thread safety** | not documented in the paper. In ISA-L the context manager is a mutable scheduler object, and its header does not state a threading contract. |
| **Drop-in for the baseline** | partial: the digests are byte-identical to SHA256(), but the caller must batch many messages through a submit/flush (or array) interface instead of the per-message init/update/final or one-shot API. |

## Gotchas

- Completion is decoupled from submission. ISA-L processes jobs out of order and returns a context only when its lane finishes, so callers must keep submitting or call flush to drain. The paper itself says the software needs restructuring to benefit.
- The 2.25x figure is against the authors' own n-SMS serial code, which is also their OpenSSL RT #2784 patch, not against a third-party implementation. The 3.42x figure is against stock OpenSSL 1.0.1.
- The disk results are in cycles/byte, so down-clocking flatters them. At 1.6GHz, S-HASH on the UNIFORM files is 6.73 c/B but only 226.73 MB/s, against 363.83 MB/s at 3.3GHz.
- OpenSSL's sha256_multi_block is internal. It is used only by the AES-CBC-HMAC-SHA256 multi-block TLS cipher code and cannot be reached as a general multi-message digest API.

## Known shortcomings

- 3.42x holds for cached data only; the '\~3x from disk' figure was measured with the CPU at 1.6 GHz (native 2.26x / 1.73x). OpenSSL later shipped its own multi-buffer SHA-256 (sha256-mb), so the baseline is superseded. JIS 2012.
- Paper has no code; shipping forms are ISA-L sha256_mb (submit/flush API), OpenSSL's internal sha256_multi_block (used only by TLS AES-CBC-HMAC multi-block) and minio's AVX-512 server. Needs a batch of independent messages: single-stream gains nothing and uneven sizes cut the gain to 1.73x. Linux dropped its AVX2 multibuffer SHA in 2018 (broken, real-world gains debated).

## Caveats and trade-offs

Applies only when many independent messages are available: each message still gets a standard SHA-256 digest, but a single message is not sped up (see j-lanes for that). OpenSSL RT ticket 2784 is the authors' n-SMS patch (the faster serial comparator), not S-HASH itself. No S-HASH code is released and no compiler or flags are stated. The disk results are bound by the SSDs, and the \~3x disk figure needs a down-clocked CPU. OpenSSL later shipped its own multi-buffer SHA-256 (crypto/sha/asm/sha256-mb-x86_64.pl, Polyakov, (c) 2013, used for multi-block AES-CBC-HMAC), so the incumbent absorbed the technique for that use. The results are from 2012 hardware against OpenSSL 1.0.1. The peer-reviewed venue is a SCIRP journal.

Only pays off when multiple independent messages/buffers can be hashed concurrently (e.g. boot-time integrity checks, multi-stream server workloads); unlike j-lanes (2012/476), gives no benefit for a single serial message.

## Maintenance

This is finished 2012 research (ePrint 2012/371, republished in Journal of Information Security 3(4):319-325, a SCIRP journal, 9 Crossref citations) with no code of its own. The technique is maintained in Intel ISA-L crypto (last push 2026-07) and survives inside OpenSSL's TLS multi-block path, while Linux dropped its copy in 2018.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The paper benchmarks 4-buffer S-HASH SHA-256 against serial OpenSSL 1.0.1 on a Core i5-2500 (Fig. 2: 17.72-17.80 vs 5.18-5.21 c/B, i.e. 3.42x; Figs. 3-4 for disk). It was peer-review published as Journal of Information Security 3(4):319-325, 2012 (DOI 10.4236/jis.2012.34039). There is no code and no compiler or flags, so it is not A.
- **Verifier notes:** The record's '\~3x from disk at 6.73 c/B' omitted that this is at a 1.6GHz down-clock; at native frequency it is 2.26x. I rewrote the claim with the full numbers, and the tier stands. The RT 2784 caveat was misattributed and is fixed. B rests on the JIS (SCIRP) publication, and without it this would be C.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `compared_against_cpp_std_directly`, `caveats`
- **Pages the verifier opened:**
  - <https://eprint.iacr.org/2012/371.pdf>
  - <https://doi.org/10.4236/jis.2012.34039>
  - <https://www.scirp.org/journal/paperinformation?paperid=23995>
  - <https://api.crossref.org/works/10.4236/jis.2012.34039>
  - <https://raw.githubusercontent.com/openssl/openssl/master/crypto/sha/asm/sha256-mb-x86_64.pl>
- **Sources the enricher read:**
  - <https://eprint.iacr.org/2012/371.pdf>
  - <https://api.crossref.org/works/10.4236/jis.2012.34039>
  - <https://doi.org/10.4236/jis.2012.34039>
  - <https://eprint.iacr.org/2012/476.pdf>
  - <https://raw.githubusercontent.com/openssl/openssl/master/crypto/sha/asm/sha256-mb-x86_64.pl>
  - <https://github.com/search?q=repo%3Aopenssl%2Fopenssl+sha256_multi_block&type=code>
  - https://github.com/intel/isa-l_crypto (README, include/isa-l_crypto/sha256_mb.h, file tree, repo metadata)
  - https://github.com/minio/sha256-simd (README, file tree, repo metadata)
  - <https://github.com/torvalds/linux/commit/ab8085c130edd65be0d95cc95c28b51c4c6faf9d>
  - <https://api.github.com/search/commits?q=repo:torvalds/linux+multibuffer+sha256+remove>
  - <https://hn.algolia.com/api/v1/search?query=simultaneous%20hashing%20multiple%20messages>
  - <https://hn.algolia.com/api/v1/search?query=multi-buffer%20sha256>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `paper:simultaneous-hashing-of-multiple-messages-s-hash-gueron-krasnov`) · [data/wave7/enrich/raw/paper_simultaneous_hashing_of_multiple_messages_s_hash_gueron_krasnov.json](../../../data/wave7/enrich/raw/paper_simultaneous_hashing_of_multiple_messages_s_hash_gueron_krasnov.json) (enrichment confidence 0.8)

</details>
