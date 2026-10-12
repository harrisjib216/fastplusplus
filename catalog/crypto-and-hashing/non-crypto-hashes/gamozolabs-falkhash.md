# falkhash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Non-cryptographic hashes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `Unlicense` · 🔴 abandoned

> One-function AES-NI 128-bit hash for x86-64; 1.4-2.5x XXH3 bulk throughput, but 3-4x slower on small keys.

| | |
|---|---|
| **Beats** | xxHash (xxh3), wyhash, CityHash |
| **Claimed result** | falkhash 52401.48 MiB/s vs xxh3 20853.74 (\~2.5x), wyhash 22640.53 (\~2.3x), City128 14472.20 (\~3.6x) (derived from page data) |
| **Workload** | SMHasher bulk-hash speed test, 262144-byte keys, x64 AES-NI (AMD64-targeted design, also runs on Intel), run for many hash functions on the same machine/build in rurban/smhasher. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 5 3350G 3.6GHz (smhasher table); author's own tests used AMD Opteron 6376, Intel Xeon E5645, Core i7 970 and Core i7 4712HQ |
| **Compiler and flags** | rurban/smhasher links a prebuilt falkhash.asm object (falkhash-elf64.o / falkhash-macho64.o), so the CMake Release -march=native flags do not apply to the hash itself; the compiler version is not stated. The author's README separately reports 0.074-0.25 cycles/byte with GCC 4.9.2, clang 3.5.0, MSVC 19.00.23026 and MSVC 18.00.31101, with no baseline comparison. |
| **Adoption** | 48 stars |
| **Last commit** | 2015-11-13 |
| **Links** | [repository](https://github.com/gamozolabs/falkhash) · [benchmark](https://github.com/rurban/smhasher/blob/master/README.md) |

## Verdict

rurban SMHasher (AMD Ryzen 5 3350G, 262144-byte keys, compiler not stated, prebuilt nasm object of the v1 asm) gives falkhash 52401.48 MiB/s vs xxh3 20853.74 (\~2.5x), wyhash 22640.53 (\~2.3x) and City128 14472.20 (\~3.6x), but 122.70 vs 29.46 cycles/hash on small keys. SMHasher3 (hardware not stated) on the current v2 C code gives 18.43 bytes/cycle vs XXH3-64 12.82 (\~1.4x), wyhash 6.98 (\~2.6x) and CityHash-64 4.75 (\~3.9x).

## Use it when

- Bulk hashing of large buffers (tens of KB and up: coverage bitmaps, file chunks, snapshots) on x86-64 with AES-NI, where bytes per cycle matter more than per-call latency.
- Non-adversarial content fingerprinting that wants a native 128-bit result at bulk speed: SMHasher3 measures 18.43 bytes/cycle for v2 vs 12.82 for XXH3-64 and 12.43 for MeowHash.
- Internal tools or experiments where copying one small public-domain function is easier than adding a dependency, and portability beyond x86 does not matter.

## Skip it when

- Short keys or hash-table lookups: every input under 80 bytes is zero-padded to a full 80-byte block, giving 85.87 cycles/hash on 1-32 B keys in SMHasher3 (XXH3-64: 30.69) and 122.70 vs 29.46 for xxh3 in rurban SMHasher. Issue #2, asking about 64-bit integer keys, is unanswered.
- Anything adversarial or security-related: the README says it is not crypto and was made 'by randomly testing things until it passed all of smhasher's tests', and funny-falcon's PR #1 pointed out a route to seed-independent collisions in v1, and the suggested fix (XOR every block with the seed) went into v2.
- When you need a clean quality record: v2 fails 6 of 250 SMHasher3 tests (Sparse), and rurban rates the v1 asm POOR, with full 64-bit collisions on sparse 160-bit and 512-bit keys. MeowHash passes all 250 SMHasher3 tests at 12.43 bytes/cycle.
- Non-x86 targets or CPUs without AES-NI: there is no fallback path; it includes x86 intrinsics headers and needs -maes.
- When you need a maintained, packaged library: no commits since November 2015, no header or build target, no tests beyond a benchmark main().

## How it is fast

It consumes 80-byte chunks. Five unaligned 16-byte loads are XORed with the 128-bit seed and squeezed into one lane by a chain of AESENC rounds that uses the other four blocks as round keys, plus one more round keyed with the seed. The result is folded into the running hash with a single AESENC. Each AESENC is a full AES round (SubBytes, ShiftRows, MixColumns, key XOR) in one instruction, and per-chunk chains do not depend on the running hash, so from the source only one AESENC per 80 bytes sits on the loop-carried path. Four more seed-keyed AESENC rounds finalize, and the 0x50 chunk size was tuned for AMD family 15h, per the asm comment.

## Compared with alternatives

Among the catalogued AES-NI hashes, falkhash v2 is roughly tied with gxhash in bulk (SMHasher3 18.43 vs 19.56 bytes/cycle) but fails fewer tests (6 vs 25), and it is about 1.5x MeowHash's bulk speed. Pick it over them only for a tiny vendored C function on x86-64 with large inputs; pick MeowHash for a clean SMHasher3 record, and XXH3, wyhash or rapidhash for small keys or portability.

## Integration

| | |
|---|---|
| **Form** | source-drop (copy the falkhash() function out of falkhash.c) |
| **Dependencies** | none (C standard library plus compiler x86 intrinsics headers) |
| **Minimum toolchain** | Any C compiler with AES-NI intrinsics; the README reports GCC 4.9.2, clang 3.5.0, MSVC 18.00 and 19.00 (VS2013/VS2015); GCC/Clang need -maes |
| **Platforms** | x86 / x86-64 with AES-NI (designed for AMD64); no ARM or portable fallback |
| **Thread safety** | Not documented. falkhash() is a pure function with only stack state, so concurrent calls look safe (inferred from source). |
| **Drop-in for the baseline** | no |

## Gotchas

- Hash values changed between v1 (hand-written asm) and v2 (C intrinsics). rurban's 52401.48 MiB/s figure is for the v1 asm object; SMHasher3 benchmarks both versions (v2: 18.43 bytes/cycle; v1: 19.88).
- The result is an __m128i, not an integer: store it with _mm_storeu_si128, and take the low 64-bit lane if you need a size_t hash, as rurban's wrapper does. The buffer parameter is a non-const void\*.
- falkhash.c defines main(), so compiling the file as-is into a program or library clashes with your own main(); extract the function.
- Length is folded into the seed (high lane = seed + len + 1), which is what keeps zero-padded tails of different lengths apart. The only key is a 64-bit seed XORed into every block, so there is no DoS-resistance claim.

## Known shortcomings

- SMHasher numbers test the old v1 prebuilt assembly object, not the repo's v2 C code; rated POOR quality. Small keys \~4x slower than xxh3. Needs AES-NI. Unlicense gives no patent grant.
- SMHasher3 on the repo's current v2 C code: 18.43 vs XXH3-64 12.82 bytes/cycle (\~1.4x, not 2.5x); v2 fails 6/250 tests (Sparse). Inputs under 80 bytes are padded to 80, so small keys are 3-4x slower. Abandoned 2015; x86 AES-NI only; returns __m128i; falkhash.c contains a main(); PR #1 flagged v1 seed-independent collisions.

## Caveats and trade-offs

The SMHasher numbers are for the v1 hand-written assembly (falkhash.asm). The repo now ships the v2 C-intrinsics implementation, whose hash values differ and which the independent table does not benchmark. SMHasher now rates falkhash POOR (Sparse and LongNeighbors failures), contradicting the README's 'passes all of smhasher's tests', and the author calls it an 'Exotic Probably Shitty Hash'. The win is bulk-only: on small keys it is about 4x slower than xxh3 (122.70 vs 29.46 cycles/hash). It needs x64 AES-NI. The author's README has only raw cycles/byte and SMHasher output on decade-old CPUs, with no direct baseline numbers. It has low notability (48 stars) and has been unmaintained since 2015. Unlicense: no patent grant.

Author explicitly labels it 'Exotic Probably Shitty Hash', not intended as a rigorously designed general-purpose hash; heavily reliant on aesenc so unportable and slow without AES-NI; author states it was found by 'randomly testing things until it passed smhasher'.

## Maintenance

Abandoned since November 2015 (48 stars, one unanswered 2023 issue), but Unlicense/public domain (no patent grant) and a hash function of about 80 lines that is trivial to vendor; the last compilers the author reports are GCC 4.9.2, clang 3.5.0 and MSVC 2015.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The rurban SMHasher README table (a well-known independent suite, public code, CPU named Ryzen 5 3350G) has falkhash at 52401.48 MiB/s against xxh3 20853.74, wyhash 22640.53 and City128 14472.20, all matching the record and doc/falkhash.txt. It is not A because the table states no compiler version. The author's README has only raw cycles/byte and SMHasher output, with no baseline comparison (that alone would be C).
- **Verifier notes:** Numbers and metadata verified (Unlicense, 48 stars, last commit 2015-11-13, not fork/archived). The main issues for enrichment are that the benchmarked code is the old asm v1, not the repo's current C code, and SMHasher's POOR quality rating.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** SMHasher3 (v2 C): falkhash 18.43 vs XXH3-64 12.82 bytes/cycle bulk.
- **Pages the verifier opened:**
  - <https://github.com/rurban/smhasher/blob/master/README.md>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/README.md>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/falkhash.txt>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/xxh3.txt>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/wyhash.txt>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/City128.txt>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/CMakeLists.txt>
  - <https://github.com/rurban/smhasher>
  - <https://github.com/gamozolabs/falkhash>
- **Sources the enricher read:**
  - <https://github.com/gamozolabs/falkhash>
  - <https://github.com/gamozolabs/falkhash/blob/master/README.md>
  - <https://github.com/gamozolabs/falkhash/blob/master/falkhash.c>
  - <https://github.com/gamozolabs/falkhash/blob/master/Makefile.unix>
  - <https://github.com/gamozolabs/falkhash/blob/master/Makefile.win>
  - <https://github.com/gamozolabs/falkhash/commits/master>
  - <https://github.com/gamozolabs/falkhash/issues/2>
  - <https://github.com/gamozolabs/falkhash/pull/1>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/README.md>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/falkhash.txt>
  - <https://github.com/rurban/smhasher/commits/master/doc/falkhash.txt>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/falkhash.asm>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/Hashes.cpp>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/Hashes.h>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/README.md>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/raw/falkhash2.txt>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/raw/falkhash1.txt>
  - https://hn.algolia.com/api/v1/search?query=falkhash&tags=(story,comment)
  - <https://hn.algolia.com/api/v1/items/22538982>
  - <https://hn.algolia.com/api/v1/items/22473048>
  - <https://hn.algolia.com/api/v1/items/48222051>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/gamozolabs/falkhash`) · [data/wave7/enrich/raw/github_com_gamozolabs_falkhash.json](../../../data/wave7/enrich/raw/github_com_gamozolabs_falkhash.json) (enrichment confidence 0.8)

</details>
