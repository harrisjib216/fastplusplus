# liblzraven

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `0BSD` · 🟢 active

> Clean-room C11 codec for Apple's LZRAVEN format (LZMA-class model, adaptive rANS); decodes about 1.7-2x faster than xz -6.

| | |
|---|---|
| **Beats** | xz |
| **Claimed result** | x86-64 (Ryzen 9 7950X, AVX2 path): decoder 1.96x xz -6 throughput per the README (SPEC.md section 12.4: 2182 versus 1096 MiB/s size-weighted, 1.99x; dense subset 1071 versus 642 MiB/s, 1.67x) on 89.7 MiB of real OS 27 OTA payloads, at ratio on par with xz -6 (10 wins, 9 losses, 1 tie; Apple's encoder produced the streams); decoder memory 35,336 bytes versus 8.06 MiB for liblzma at -6. Apple M4 Pro NEON path: 954 MiB/s versus xz -6 at 328 MiB/s (2.91x) on a substitute corpus. |
| **Workload** | Decoding 89.7 MiB of OS 27 over-the-air payloads, measured with tools/benchmark.py; also a synthetic corpus on Apple M4 Pro. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 7950X (Zen 4), Linux 6.12, single pinned core for the x86 tables; Apple M4 Pro (10P + 4E), macOS 27.0 for the NEON table |
| **Compiler and flags** | GCC 14.2 at -O2 with run-time SIMD dispatch (avx2 selected) on x86-64; Apple clang 21 at -O2 on the M4 Pro; liblzma 5.8.1 and zlib 1.3.1 (x86) and liblzma 5.8.3 (M4 Pro) as baselines, their build flags not stated |
| **Adoption** | 7 stars |
| **Last commit** | 2026-07-30 |
| **Links** | [repository](https://github.com/anat0m1a/liblzraven) · [benchmark](https://raw.githubusercontent.com/anat0m1a/liblzraven/HEAD/SPEC.md) |

## Verdict

On 20 real iOS 27 OTA streams (89.7 MiB of output, best of 9, one pinned core of a Ryzen 9 7950X, GCC 14.2 -O2, AVX2 path), the decoder ran at 2182 MiB/s versus liblzma 5.8.1 xz -6 at 1096 MiB/s (1.99x) and 1071 versus 642 MiB/s (1.67x) on the 39 MiB dense subset, where zlib 1.3.1 -6 was faster still (1282 MiB/s) at a much worse ratio; the ratio column (a tie with xz -6) uses Apple's encoder output. On an M4 Pro with a substitute corpus the NEON path ran 954 versus 328 MiB/s for xz -6 (2.91x), below Apple's own decoder at 1333 MiB/s.

## Use it when

- Unpacking Apple OS 27 (and later) OTA payloads (pbzm/LZRAVEN) on Linux, Windows or other non-Apple hosts, where there is no other open decoder.
- Decoding LZRAVEN in memory-constrained or allocation-free contexts: fixed 35 KB of automatic storage versus about 8 MiB for liblzma at xz -6.
- Multi-threaded batch decoding of many independent chunks: the decoder is a pure, reentrant function of its arguments.
- Producing LZRAVEN streams that Apple's libcompression will accept, where encode speed is not critical.

## Skip it when

- As a general replacement for xz/LZMA in your own formats: the evidence is one niche corpus (Apple OTA chunks, 29.9x compressible), the format has no published spec beyond this repo's reverse-engineered one, no checksum and no streaming, and it is tied to one Apple build (iOS 27.0 beta 4 dylib).
- When encode speed matters: the encoder runs about 70 MB/s on highly redundant OTA plaintext and 4-20 MB/s on Mach-O or text, and its output is about 4% larger than Apple's encoder (greedy plus one-step lazy parse, no optimal parse).
- On Apple platforms: Apple's own decoder is faster on dense coded content (1333 versus 954 MiB/s on M4 Pro, ours at 72%), so call libcompression there.
- When you need a maintained dependency: one commit, 7 stars, AI-authored, and the owner states he does not intend to maintain it.
- When the output must be trustworthy without a container: in the SPEC's own bit-flip test, 49 of 300 single-bit flips decoded to different data without error.

## How it is fast

The format pairs an LZMA-style grammar (state machine, four repeat distances, matched literals) with 8-way interleaved adaptive rANS over AV1/Daala-style 16-symbol CDFs instead of LZMA's serial binary range coder, so consecutive symbols are independent enough for instruction-level parallelism. The library hand-vectorises the 16-lane CDF search and update (SSE2/AVX2 compare + movemask + popcnt, NEON cmhi/uzp1/saddlv) with run-time dispatch, plus a vectorised overlapping match copy; SPEC.md section 12.4 credits these kernels with 2.75-2.96x over its own portable C path, which alone is slower than xz (0.67x). Matches address the output buffer directly, so the decoder needs only a fixed 35,336-byte working set and never allocates.

## Compared with alternatives

Pick it only when the data is or must be LZRAVEN; for general archives that beat xz, Fast LZMA2 keeps the xz/LZMA2 format and LZHAM, libbsc or bzip3 have broader, independent benchmarks. Against LZFSE (Apple's older fast codec) it aims at the xz ratio band rather than the zlib band.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none (a shared object via `make shared`; optional stdlib-only Python ctypes binding) |
| **Minimum toolchain** | C11 (Makefile uses -std=c11 -O2); measured with GCC 14.2 and Apple clang 21 |
| **Platforms** | x86-64 (scalar, SSE2, AVX2 paths with run-time dispatch), arm64 (NEON), portable C elsewhere |
| **Thread safety** | Decoder and encoder are thread-safe on distinct buffers and scratch; lzraven_simd_set, which pins the SIMD path, is not thread-safe and must be called before decoding starts. |
| **Drop-in for the baseline** | no |

## Gotchas

- lzraven_decode_buffer returns 0 both for failure and for a valid empty stream; use lzraven_decode_buffer_ex to tell them apart.
- The decoder is deliberately stricter than Apple's (it rejects blocks whose rANS states did not drain, and matches that overrun the coded region), so a few streams Apple accepts are rejected here.
- Encoder scratch is large (a few thousand times the decoder's 35 KB; Apple's own is about 10.9 MB) and grows 4 bytes per window position; windows above 8 MiB emit distance classes Apple's encoder never produces.
- Streams are limited to 8192 blocks of 512 KiB, so at most 4 GiB of output per stream; the Makefile does not define NDEBUG, so asserts stay live (SPEC says at no measurable cost).

## Known shortcomings

- Upgraded C to A: SPEC.md section 12 names tools/benchmark.py, GCC 14.2 -O2 on a Ryzen 9 7950X, plus tools/bench_apple.py with Apple clang 21 -O2 on an M4 Pro; the x86 corpus is not redistributable and zlib -6 decodes faster on the dense subset. Last commit 2026-07-30.
- The scalar path is 0.67x xz, so the speedup comes from the SIMD kernels; Apple's decoder is faster (1333 vs 954 MiB/s on an M4 Pro); the encoder runs 4-20 MB/s on non-redundant data and output is about 4% bigger than Apple's; 49 of 300 bit flips decode silently (no checksum); asserts are live (no NDEBUG); 4 GiB maximum per stream. README and SPEC section 12.4 disagree on the dense-subset xz figure (652 vs 642 MiB/s).

## Caveats and trade-offs

Measured on a niche corpus of OS payloads that compress 29.9x; the ratio parity with xz -6 is for streams written by Apple's encoder, while this library's own encoder is about 4% larger than Apple's. On the dense subset zlib -6 decodes faster (1282 MiB/s) than liblzraven (1071 MiB/s), though at much lower ratio (8.85x versus 13.77x). The x86 corpus is carved from Apple OTA payloads and is not redistributable, so only the M4 Pro table (built with tools/make_corpus.py, which needs Apple's native encoder) can be reproduced from public data. The README admits Apple's own decoder is faster (1333 versus 954 MiB/s). The repo is entirely AI-authored and the owner says he does not intend to maintain it; one commit (2026-07-30). Compared against xz and zlib only, not zstd. The format has no integrity checks. TurboBench lists it as an Apple lzraven reimplementation.

Clean-room C11 decoder and encoder of Apple's LZRAVEN codec (LZ + rANS) for OTA payloads; buffer-only, no streaming, no allocation in the decoder. Encoder is slow (about 70 MB/s on redundant data, 4-20 MB/s otherwise).

## Maintenance

Single AI-authored commit (2026-07-30) that the owner says he will not maintain, but it is 0BSD, dependency-free C11, heavily fuzzed (377 million AFL++ decoder executions, ASan/UBSan clean) and differentially tested against Apple's decoder, so it is reasonable to vendor for OTA tooling.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C: SPEC.md section 12 gives the full method for the README's numbers: public harness tools/benchmark.py, decoder built with GCC 14.2 at -O2 (AVX2 selected at run time), AMD Ryzen 9 7950X, Linux 6.12, against liblzma 5.8.1 and zlib 1.3.1 on the same machine, best of 9 pinned to one core; the M4 Pro table uses tools/bench_apple.py, Apple clang 21 at -O2, against liblzma 5.8.3 on a corpus built by tools/make_corpus.py. Code, compiler, flags and CPU model are all stated, so A, with the caveat that the x86 corpus (Apple OTA payloads) is not redistributable.
- **Verifier notes:** All README figures appear as stated; SPEC.md section 12 supplies the methodology the record lacked, hence the upgrade to A. Repo: 0BSD, 7 stars, 1 fork, a single commit dated 2026-07-30; tools/ holds benchmark.py, bench_apple.py and make_corpus.py.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `last_commit`, `maintenance_status`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/anat0m1a/liblzraven/HEAD/README.md>
  - <https://raw.githubusercontent.com/anat0m1a/liblzraven/HEAD/SPEC.md>
  - <https://github.com/anat0m1a/liblzraven>
  - <https://github.com/anat0m1a/liblzraven/commits>
  - <https://github.com/anat0m1a/liblzraven/tree/main/tools>
  - <https://raw.githubusercontent.com/powturbo/TurboBench/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/anat0m1a/liblzraven>
  - <https://raw.githubusercontent.com/anat0m1a/liblzraven/HEAD/README.md>
  - <https://raw.githubusercontent.com/anat0m1a/liblzraven/HEAD/SPEC.md>
  - <https://raw.githubusercontent.com/anat0m1a/liblzraven/HEAD/include/lzraven.h>
  - <https://raw.githubusercontent.com/anat0m1a/liblzraven/HEAD/Makefile>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/anat0m1a/liblzraven`) · [data/wave9/enrich/raw/github_com_anat0m1a_liblzraven.json](../../../data/wave9/enrich/raw/github_com_anat0m1a_liblzraven.json) (enrichment confidence 0.7)

</details>
