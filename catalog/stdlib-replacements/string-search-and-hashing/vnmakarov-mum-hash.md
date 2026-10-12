# MUM/VMUM hash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [String search and hashing](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟢 active

> Header-only C multiply-mix hash family (MUM/VMUM) rivaling xxHash3, beating CityHash and SipHash24 on most key sizes.

| | |
|---|---|
| **Beats** | xxHash3, Google CityHash (City64), Bob Jenkins SpookyHash, SipHash24, MetroHash, t1ha2 — widely-used non-cryptographic hash functions used in place of std::hash for hash-table keys |
| **Claimed result** | Geomean of relative throughput across key lengths, VMUM-V2 normalized to 1.00 (higher/lower time = slower/faster): on Apple M4, VMUM-V2 is \~1.3x faster than xxHash3 (ratio 0.79), \~2.6x faster than CityHash (0.38), and \~4.8x faster than SipHash24 (0.21); on IBM Power10 it's roughly on par with xxHash3 (0.93) and \~2.1x faster than CityHash (0.48). (derived from page data: the README's per-length tables list ratio+time for VMUM-V1/V2, MUM-V3/V4, Spooky, City, xxHash3, t1ha2, SipHash24 and Metro on AMD Ryzen 9900X, an Intel chip, IBM Power10 and Apple M4.) |
| **Workload** | Hashing 1,280M keys of lengths from 3 to 1024 bytes, plus 10,000 x 16MB bulk keys, on four different machines; each measurement repeated 3x and the minimum time kept. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9900X, Intel i5-13600K (the README prose says 'i5-1300K'), Intel Core Ultra 9 285 (table only), IBM Power10, Apple M4 10-core Mac mini |
| **Compiler and flags** | GCC 14.2.1 (AMD Ryzen 9900X and Apple M4), GCC 12.3.1 (Intel), GCC 11.5.0 (IBM Power10); -O3 for all. benchmarks/bench.sh also appends -march=native on x86_64 and -mcpu=native on ppc64, and adds -flto only for the competing hash functions (not MUM/VMUM) to allow cross-file inlining. Each test is run 3x pinned with taskset -c 0 and the minimum user time is kept. |
| **Adoption** | 165 stars |
| **Last commit** | 2026-06-02 |
| **Links** | [repository](https://github.com/vnmakarov/mum-hash) · [benchmark](https://github.com/vnmakarov/mum-hash#vmum-and-mum-benchmarking-vs-other-famous-hash-functions) |

## Verdict

Hashing 1,280M keys (3-1024 bytes) plus 10,000x16MB bulk keys, GCC -O3 (-flto added only for the competing hash functions, not MUM/VMUM), pinned single-core runs, minimum of 3 repeats kept: VMUM-V2's geomean relative throughput (1.00 baseline) is xxHash3 0.79, CityHash 0.38, SipHash24 0.21 on Apple M4 (GCC 14.2.1), and xxHash3 0.93, CityHash 0.48 on IBM Power10 (GCC 11.5.0) -- i.e. VMUM-V2 is \~1.3x faster than xxHash3 and \~2.6x faster than CityHash on M4, and roughly on par with xxHash3 on Power10.

## Use it when

- Very short keys (3-16 bytes) where MUM/VMUM's fast startup wins on every benchmarked machine (ratio \~1.00 vs xxHash3's 0.7-0.95)
- Long keys (512-1024 bytes) and 16MB bulk hashing on AVX2 (x86-64) or NEON (aarch64) hardware, where VMUM-V2 is \~1.1-1.9x faster than xxHash3
- Apple M4 / aarch64 targets specifically, where VMUM-V2 beats xxHash3 by \~1.3x geomean and CityHash/SipHash24 by 2.6x/4.8x
- Hash-table implementations that want a header-only C hash with no crypto/library dependency and are willing to hand-write the call sites
- Cases wanting the collision-attack-resistant fixed hash by default (Nov 2025 fix), with the ability to opt back into the faster pre-fix variant via VMUM_V1/MUM_V3 macros for controlled environments

## Skip it when

- Mid-size keys, roughly 32-128 bytes (16 bytes on Power10): xxHash3 is faster there, e.g. 128 bytes is 1.98x faster on AMD, 1.81x on M4, 2.03x on Power10
- Targets without AVX2/NEON/Altivec and without a compiler 128-bit-integer extension: VMUM drops to scalar emulation and MUM needs GCC/Clang-style __int128 to hit its documented numbers
- Projects that require a real drop-in for std::hash/xxHash's call signature without touching call sites -- MUM/VMUM's API shape is different
- Teams uncomfortable with no LICENSE file at repo root (MIT is only asserted in per-file header comments; GitHub's own license detector shows none)
- Cross-platform byte-identical hashes across BE/LE or 32/64-bit targets, unless [V]MUM_TARGET_INDEPENDENT_HASH is explicitly defined (with a performance cost on BE/no-int128 targets)

## How it is fast

MUM (Multiply and Mix) randomizes each 64-bit chunk with a 64x64-&gt;128-bit multiply, mixes the high/low halves with addition, and XORs into a running state, using a table of pre-generated random factors; the main loop is written to be unrolled by the compiler for out-of-order scheduling, with no per-byte branching. VMUM extends this with target vector instructions (AVX2 32x32-&gt;64 multiplies on x86-64, NEON on aarch64, Altivec on ppc64) processing multiple lanes per step, and runs two unrolled loops in parallel to keep OOO execution units busy; targets without vector support fall back to scalar emulation.

## Compared with alternatives

Pick VMUM over rapidhash, t1ha, or CityHash when hashing very short keys (&lt;=16 bytes) or long/bulk keys on AVX2 or NEON hardware, where it edges out xxHash3 and clearly beats CityHash/SipHash24/t1ha2. Prefer xxHash3, rapidhash, or komihash instead for the common 32-128 byte range, where VMUM-V2 loses to xxHash3 by up to \~2x.

## Integration

| | |
|---|---|
| **Form** | header-only (single file: mum.h or vmum.h) |
| **Dependencies** | none beyond the C standard library (stddef.h, stdlib.h, string.h, limits.h, stdint.h) |
| **Minimum toolchain** | C99; GCC or Clang recommended to get the 128-bit-integer multiply path (checked via __GNUC__); MSVC compiles via typedef shims but takes the non-__int128 fallback path |
| **Platforms** | x86-64 (AVX2 needed for VMUM's full speed, e.g. -mavx2), aarch64 (NEON), ppc64 (Altivec); scalar emulation on any other target |
| **Thread safety** | mum_hash_init/step/finish/hash/hash64 only read pre-generated, read-only factor tables and are reentrant. mum_hash_randomize()/vmum_hash_randomize() mutate shared module-level globals and are not documented as thread-safe -- call once at startup before spawning threads. |
| **Drop-in for the baseline** | partial -- same hash-table-key role as xxHash3/CityHash/SipHash24 but a different call signature (mum_hash(key,len,seed), not a pluggable std::hash specialization), so call sites need to be rewritten |

## Gotchas

- The pre-Nov-2025 VMUM/MUM-V3 variants have a collision-attack weakness (issue #18: an adversary can zero one operand of _vmum to force identical hashes); the fix is now default and costs \~10% throughput, old fast variants are opt-in via VMUM_V1/MUM_V3 macros
- No LICENSE file at repo root; MIT terms live only in the header comment of each source file (mum.h, vmum.h, mum512.h, mum-prng.h)
- Hash values are not target-independent by default (differ across BE/LE and 32/64-bit, and with/without int128 support) unless [V]MUM_TARGET_INDEPENDENT_HASH is defined
- VMUM needs an explicit compile flag (e.g. -mavx2 on x86-64, -mcpu=native/NEON on aarch64) to use its vector code path; without it, it silently falls back to slower scalar emulation

## Caveats and trade-offs

There is no LICENSE file and GitHub reports no SPDX license, but every source header (mum.h, vmum.h, mum512.h, mum-prng.h) carries the MIT permission notice. The benchmark is first-party (author's repo) but fully disclosed. xxHash3 is not beaten everywhere: it is faster than VMUM-V2 on mid-size keys (about 32/64-128 bytes, and 16 bytes on Power10; e.g. 128 bytes: 1.98x on AMD, 1.81x on M4, 2.03x on Power10) and on bulk on AMD/M4. VMUM-V1 is itself \~1.1x faster than VMUM-V2 on geomean. Timings are whole-program user time, including key generation.

VMUM needs target SIMD (AVX2 on x86-64, NEON on aarch64, Altivec on ppc64) to get its full speed advantage on mid/long keys, falling back to scalar emulation elsewhere; an earlier VMUM/MUM-V3 had a collision-attack weakness (fixed Nov 2025 at \~10% extra cost, now default); requires compiler support for 128-bit integer extensions.

## Maintenance

Actively maintained (last commit 2026-06-02, with a collision-attack fix shipped Nov 2025); MIT-licensed via per-file source headers (no repo-root LICENSE file) and small enough as single headers to vendor directly.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** The benchmark code is public (benchmarks/bench.sh + benchmarks/bench.c, with competitor sources vendored). The README states the GCC versions per machine, -O3 (+ -flto for the competitors), and the CPU models. The per-machine tables list geomeans matching the claim (M4: xxHash3 0.79, City 0.38, SipHash24 0.21; Power10: xxHash3 0.93, City 0.48).
- **Verifier notes:** The claimed ratios match the M4 and Power10 geomean rows. The license is MIT via per-file headers, not unlicensed, so usability changes from reference to copyable. The tables cover 5 machines, including an Intel Ultra 9 285 not mentioned in the prose. Metadata verified: 165 stars, last commit 2026-06-02, not a fork or archived.
- **Fields the verifier corrected:** `license`, `usability`, `hardware`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/vnmakarov/mum-hash>
  - <https://github.com/vnmakarov/mum-hash#vmum-and-mum-benchmarking-vs-other-famous-hash-functions>
  - <https://github.com/vnmakarov/mum-hash/tree/master/benchmarks>
  - <https://github.com/vnmakarov/mum-hash/blob/master/benchmarks/bench.sh>
  - <https://github.com/vnmakarov/mum-hash/blob/master/mum.h>
  - <https://github.com/vnmakarov/mum-hash/blob/master/vmum.h>
  - <https://github.com/vnmakarov/mum-hash/blob/master/mum512.h>
  - <https://github.com/vnmakarov/mum-hash/blob/master/mum-prng.h>
- **Sources the enricher read:**
  - <https://github.com/vnmakarov/mum-hash>
  - <https://github.com/vnmakarov/mum-hash#vmum-and-mum-benchmarking-vs-other-famous-hash-functions>
  - <https://github.com/vnmakarov/mum-hash/blob/master/mum.h>
  - <https://github.com/vnmakarov/mum-hash/blob/master/vmum.h>
  - <https://github.com/vnmakarov/mum-hash/issues>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/vnmakarov/mum-hash`) · [data/wave1/enrich/raw/github_com_vnmakarov_mum_hash.json](../../../data/wave1/enrich/raw/github_com_vnmakarov_mum_hash.json) (enrichment confidence 0.75)

</details>
