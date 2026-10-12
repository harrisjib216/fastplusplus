# pengyhash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Non-cryptographic hashes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `GPL-3.0` · 🔴 abandoned

> Tiny multiply-free 64-bit ARX hash; its v0.2 beat xxHash64 bulk speed in rurban/smhasher, current v0.3 does not.

| | |
|---|---|
| **Beats** | xxHash64 |
| **Claimed result** | rurban/smhasher: 13347.17 MiB/s vs 11176.72 MiB/s for xxHash64 in the 262144-byte bulk test, \~19% faster (derived from page data). This is not reproduced by SMHasher3, where pengyhash v0.3 runs 12.47 GiB/s vs 13.02 GiB/s for XXH-64 (3.80 vs 3.99 bytes/cycle in the summary table), \~4-5% slower (derived from page data). |
| **Workload** | SMHasher bulk speed test: 262144-byte keys, averaged over byte alignments 0-7 |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 5 3350G 3.6GHz (rurban/smhasher default reference machine, per README) |
| **Adoption** | 12 stars (tinypeng/pengyhash); packaged as a reference hash in rurban/smhasher (2.2k stars) |
| **Last commit** | 2022-11-30 |
| **Links** | [repository](https://github.com/tinypeng/pengyhash) · [benchmark](https://github.com/rurban/smhasher/blob/master/README.md) |

## Verdict

rurban/smhasher's 262,144-byte bulk test on its reference Ryzen 5 3350G (logs normalized to 3 GHz; compiler and flags unstated) measured pengyhash v0.2 at 13,347 MiB/s against 11,177 MiB/s for xxHash64. That is \~19%, or \~9% against xxHash64's best alignment (12,263 MiB/s), since xxHash64 drops to 10,125 MiB/s at alignments 4-7. SMHasher3 on a Ryzen 9 3950X pinned at 3.5 GHz measured the current v0.3 at 12.47 GiB/s vs 13.02 GiB/s for XXH64, about 4% slower.

## Use it when

- You want a very small, portable 64-bit hash with no multiplies, for example on cores where 64x64 multiplication is slow. The whole algorithm is about 25 lines of add, rotate and xor.
- Hashing medium-to-large buffers (KBs and up) where scalar XXH64-class throughput is enough: about 3.8 bytes/cycle for v0.3 in SMHasher3, about 4.7 for v0.2 in rurban/smhasher.
- You need the same output on little- and big-endian hosts. v0.3 assembles words byte by byte in little-endian order, and SMHasher3 registers it as endian-independent with identical LE/BE verification values.
- You must match hash values already produced by rurban/smhasher or the Fortran stdlib pengy_hash; that requires the v0.2 code (BSD-2-Clause), not the current repo.

## Skip it when

- Short keys such as hash-table strings or integers: SMHasher3 averages 89.81 cycles/hash on 1-31-byte keys (about 116 at 8-16 bytes), against 52.60 for XXH64 and 29.31 for wyhash. rurban/smhasher shows 74.79 vs 49.67 for xxHash64.
- Expecting to beat XXH64 with the code you download today: the current v0.3 runs about 4% slower than XXH64 in SMHasher3 (12.47 vs 13.02 GiB/s). xxh3 and wyhash are about 1.6-1.7x faster in bulk in the rurban table.
- Proprietary or permissively licensed products: v0.3 is GPLv3, unlike most peer non-crypto hashes. Only the older v0.2 is BSD-2-Clause.
- Seeded use that relies on the seed to separate hash families. The seed is mixed in only during finalization, and SMHasher3's SeedBlockLen test finds full 64-bit collisions on 16-31-byte keys (126 found where 0 are expected) when seed and key blocks vary together.
- Code that must be well-defined C: v0.3 has an unsequenced read and write of the same state word, reported in 2023 (issue #2) and unanswered, in a repo abandoned since November 2022.

## How it is fast

It uses no multiplications. The state is four 64-bit words updated with add-rotate-xor (ARX) steps, 32 input bytes per iteration, in two cross-coupled chains (s0/s1 and s2/s3), with every input word added twice per block. The last 0-31 bytes are packed into four words and mixed by six fixed finalization rounds, the only place the seed enters. There is no SIMD; speed comes from cheap scalar ALU ops and instruction-level parallelism.

## Compared with alternatives

Rarely. SpookyHash (SpookyV2_64) matches its rurban bulk speed (13,401 vs 13,347 MiB/s), and xxHash (XXH3) and wyhash are about 1.6-1.7x faster in bulk and much faster on short keys, so pengyhash only wins if a tiny multiply-free ARX hash with endian-independent output (v0.3) is itself the requirement.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (stdint.h, stddef.h) |
| **Minimum toolchain** | C99 (stdint.h); no compiler versions documented |
| **Platforms** | any (portable scalar C, no intrinsics); v0.3 output is endian-independent, v0.2 (memcpy loads) is not |
| **Thread safety** | Not documented. The function is pure (no globals or static state), so concurrent calls are safe by construction. |
| **Drop-in for the baseline** | partial — it is a one-shot (buffer, length, 64-bit seed) -&gt; uint64_t call like one-shot XXH64, but produces different values and has no streaming API |

## Gotchas

- Undefined behavior in v0.3. Statements such as s[1] = (s[0] += (s[1] += V64(p+8)) + V64(p)) ^ rotl(s[1],14) read and modify s[1] without a sequence point (GCC -Wsequence-point), so the hash can change with the compiler's evaluation order. SMHasher3 ships a rewrite with explicit sequencing whose verification value (0x861A1254) matches the repo's own v0.3 log. Use that form.
- v0.2 and v0.3 give different hashes, and the published \~19% win over xxHash64 was measured on v0.2 (rurban/smhasher bundles v0.2, verification 0x1FC2217B; v0.3 is 0x861A1254). v0.2 also reads input with native-endian memcpy, so its values differ on big-endian machines, which the Fortran stdlib documents for its port.
- The license changed from BSD-2-Clause (v0.2) to GPLv3 (v0.3) in the same commit that changed the algorithm, so older attributions citing BSD for pengyhash.c at master (rurban issue #210, Fortran stdlib docs) now point at GPLv3 code.
- Every call runs six full finalization rounds regardless of length, so there is a fixed \~68-116-cycle cost per hash even for 1-byte keys (SMHasher3: 67.63 cycles at 1 byte).

## Known shortcomings

- Wins on rurban/smhasher only (13,347 vs 11,177 MiB/s); SMHasher3 has it \~4% slower than XXH64 (12.47 vs 13.02 GiB/s). GPL-3.0.
- The \~19% win over XXH64 is for v0.2; current v0.3 is \~4% slower than XXH64 in SMHasher3, and small keys are slow (89.81 vs 52.60 cycles). v0.3 has unsequenced-modification UB (s[1]/s[3], issue #2 open since 2023); license changed to GPL-3.0 in v0.3 (v0.2 was BSD-2). Seed applied only at finalization, giving 64-bit SeedBlockLen collisions on 16-31 byte keys. Abandoned since 2022-11.

## Caveats and trade-offs

The speed win over xxHash64 is not robust. It shows in rurban/smhasher (\~19%), where xxHash64's average is dragged down by slow unaligned runs (10125 MiB/s at alignments 4-7 vs \~12200 MiB/s at 0-3). In the independent SMHasher3 suite, pengyhash is \~4% slower than XXH-64. SMHasher3 also marks pengyhash FAIL (234/250 tests passed). The repo has no benchmark section, but it ships first-party SMHasher output (SMhasher_results.txt: 14673.04 MiB/s @ 3 GHz, with no xxHash64 row). Compiler and flags for both shootouts are unstated, which caps the tier at B. The GPL-3.0 license limits embedding.

64-bit output only, no seeding beyond a 32-bit seed, GPLv3 license (copyleft, unlike most peer non-crypto hashes which are permissive)

## Maintenance

Abandoned: the last commit (v0.3 and the GPLv3 relicense) was November 2022, and a 2023 undefined-behavior report is unanswered. The two small files are trivial to vendor, but pick v0.2 (BSD-2-Clause) or SMHasher3's sequenced v0.3 rewrite deliberately, based on your license and output-compatibility needs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now B.
- **Tier reason:** The rurban/smhasher README table (well-known independent suite, 2177 stars) lists pengyhash at 13347.17 MiB/s and xxHash64 at 11176.72 MiB/s, and doc/pengyhash.txt confirms the 13347.17 average. The suite code and CPU (Ryzen 5 3350G) are public, but the compiler and flags are not stated, so it is B.
- **Verifier notes:** The numbers match exactly, and the rurban README table (now benchmark_url) holds both rows. The per-hash .txt page alone has no xxHash64 figure. I downgraded because the claim is contradicted by SMHasher3 (pengyhash is \~4% slower than XXH-64 there), so 'faster than xxHash64' holds on one suite only. The tier stays B.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** SMHasher3: pengyhash 12.47 vs XXH-64 13.02 GiB/s.
- **Pages the verifier opened:**
  - <https://github.com/rurban/smhasher/blob/master/doc/pengyhash.txt>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/pengyhash.txt>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/xxHash64.txt>
  - <https://github.com/rurban/smhasher/blob/master/README.md>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/README.md>
  - <https://github.com/rurban/smhasher>
  - <https://raw.githubusercontent.com/fwojcik/smhasher3/main/results/raw/pengyhash.txt>
  - <https://raw.githubusercontent.com/fwojcik/smhasher3/main/results/raw/XXH-64.txt>
  - <https://raw.githubusercontent.com/fwojcik/smhasher3/main/results/README.md>
  - <https://github.com/tinypeng/pengyhash>
- **Sources the enricher read:**
  - <https://github.com/tinypeng/pengyhash>
  - <https://github.com/tinypeng/pengyhash/blob/master/README.md>
  - <https://github.com/tinypeng/pengyhash/blob/master/pengyhash.c>
  - <https://github.com/tinypeng/pengyhash/blob/master/pengyhash.h>
  - <https://github.com/tinypeng/pengyhash/blob/70a23e4/pengyhash.c>
  - <https://github.com/tinypeng/pengyhash/blob/70a23e4/LICENSE>
  - <https://github.com/tinypeng/pengyhash/commits/master>
  - <https://github.com/tinypeng/pengyhash/blob/master/SMhasher_results.txt>
  - <https://github.com/tinypeng/pengyhash/blob/master/SMhasher_demerphq_results.txt>
  - <https://github.com/tinypeng/pengyhash/issues/1>
  - <https://github.com/tinypeng/pengyhash/issues/2>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/README.md>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/pengyhash.txt>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/xxHash64.txt>
  - <https://github.com/rurban/smhasher/blob/master/pengyhash.c>
  - <https://github.com/rurban/smhasher/blob/master/main.cpp>
  - <https://github.com/rurban/smhasher/issues/210>
  - <https://github.com/rurban/smhasher/issues/298>
  - <https://raw.githubusercontent.com/fwojcik/smhasher3/main/results/README.md>
  - <https://raw.githubusercontent.com/fwojcik/smhasher3/main/results/raw/pengyhash.txt>
  - <https://raw.githubusercontent.com/fwojcik/smhasher3/main/results/raw/XXH-64.txt>
  - <https://raw.githubusercontent.com/fwojcik/smhasher3/main/results/raw/wyhash.txt>
  - <https://raw.githubusercontent.com/fwojcik/smhasher3/main/README.md>
  - <https://github.com/fwojcik/smhasher3/blob/main/hashes/pengyhash.cpp>
  - <https://github.com/fortran-lang/stdlib/blob/master/doc/specs/stdlib_hash_procedures.md>
  - <https://github.com/fortran-lang/stdlib/blob/master/test/hash_functions/pengyhash.c>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/tinypeng/pengyhash`) · [data/wave7/enrich/raw/github_com_tinypeng_pengyhash.json](../../../data/wave7/enrich/raw/github_com_tinypeng_pengyhash.json) (enrichment confidence 0.82)

</details>
