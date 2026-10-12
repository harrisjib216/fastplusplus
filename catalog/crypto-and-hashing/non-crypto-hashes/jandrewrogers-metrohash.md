# MetroHash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Non-cryptographic hashes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> 2015 family of machine-generated 64/128-bit non-cryptographic hashes pitched as a faster CityHash; now outpaced by XXH3 and wyhash.

| | |
|---|---|
| **Beats** | CityHash (City64/City128/City128crc) |
| **Claimed result** | Metro64 \~50% faster than City64 on bulk data, \~15% faster on small keys; Metro128 \~25% faster bulk / \~60% faster small keys vs City128; Metro128crc \~30% faster bulk / \~80% faster small keys vs City128crc |
| **Workload** | Author's own benchmarks comparing bulk-hashing and small variable-length-key throughput of Metro64/Metro128/Metro128crc against Google's CityHash equivalents. |
| **Metric** | throughput |
| **Hardware** | Haswell-class x86-64 (exact CPU model not stated, only 'Haswell test environment') |
| **Adoption** | 376 stars |
| **Last commit** | 2018-10-23 |
| **Links** | [repository](https://github.com/jandrewrogers/MetroHash) · [benchmark](http://www.jandrewrogers.com/2015/05/27/metrohash/) |

## Verdict

The author's 2015 post gives only relative figures against CityHash in an unspecified 'Haswell test environment', with no CPU model, compiler, flags or harness: Metro64 is 50% faster than City64 on bulk data and 15% on small keys, Metro128 25%/60% faster than City128, and Metro128crc 30%/80% faster than City128crc. Independent rurban SMHasher tables (262,144-byte bulk, 1-31-byte small keys; compiler not stated in what I read) show much smaller, mixed bulk gaps: metrohash64 vs City64 is -1% on a Ryzen 5 3350G, +18% on an EPYC 9554P and +2% on an i7-6820HQ, metrohash128 vs City128 is +10%/-6%/-3%, metrohash128crc_1 vs CityCrc128 ranges from -33% (Ryzen) to +41% (i7), and small keys take about 11-19% fewer cycles.

## Use it when

- You must reproduce MetroHash values that are already stored or computed elsewhere. ClickHouse vendors a copy in contrib/libmetrohash, and there are ports such as java-metrohash.
- Replacing City64/City128 in existing x86-64 C++ code. You get a small, dependency-free function (about 620-880 bytes of object code in SMHasher's size column) and roughly 11-19% fewer cycles per hash on 1-31-byte keys.
- You need a seeded 128-bit non-crypto hash with a streaming Update/Finalize API, for example hashing a file or message that arrives in chunks.
- x86-64 servers with SSE4.2 hashing large buffers to 128 bits: metrohash128crc_1 beat CityCrc128 by 35-41% in bulk throughput on SMHasher's EPYC 9554P and i7-6820HQ runs (but see the Ryzen caveat below).

## Skip it when

- New code picking a fast hash. On the same SMHasher EPYC 9554P table, xxh3 does 45,762 MiB/s against metrohash64's 18,558 (about 2.5x) and 20.6 against 29.6 cycles per small key. wyhash is also faster (24,519 MiB/s, 18.9 cycles).
- Hash tables exposed to attacker-chosen keys. There is no DoS-resistance claim, and the author states that 'resistance to cryptanalysis was not a design criterion'.
- Big-endian or strict-alignment targets, or builds run under UBSan, unless you patch it: upstream does unaligned reinterpret_cast loads and emits host-endian output.
- Portable builds that compile every source file. metrohash128crc.cpp includes &lt;nmmintrin.h&gt; and needs SSE4.2, so it fails on ARM and other non-x86 targets (open PR #19 would skip it). ARM was never a generation target.
- Workloads that need top statistical quality. SMHasher flags metrohash64 for UB, LongNeighbors and BIC (max bias 0.061, FAIL), flags metrohash128 for UB and LongNeighbors, and leaves MetroHash off its list of fastest x86-64 hashes without quality problems.

## How it is fast

The bulk loop reads 32-byte stripes into four 64-bit accumulator lanes, each running a multiply-rotate-add step (v[i] += load64 \* k_i; v[i] = rotr(v[i], 29) + v[j]) that gives the CPU instruction-level parallelism; on Hacker News, Yann Collet (Cyan4973) noted how close this structure is to xxHash64. Tails are consumed in straight-line 16/8/4/2/1-byte steps with a short rotate-multiply finalizer, which keeps small-key cost low. The constants and rotation amounts came from the author's automated generate-and-analyze search (a gradient-descent process over about 100,000 compute hours, per the blog), and the crc variants replace the multiplies in the bulk loop with SSE4.2 _mm_crc32_u64.

## Compared with alternatives

Pick MetroHash only when you need compatibility with existing MetroHash-hashed data, or want a minimal change from CityHash on x86-64. For new work, xxHash (XXH3) and wyhash are faster in the same SMHasher tables, FarmHash is CityHash's own successor, and the same author's later AquaHash (AES-intrinsic, 128-bit) supersedes it on AES-capable CPUs.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (the CRC variant needs SSE4.2 intrinsics via &lt;nmmintrin.h&gt;) |
| **Minimum toolchain** | Not documented. The code is plain C++ using &lt;stdint.h&gt;/&lt;cstring&gt;, and I saw no C++11 features. There is no build system upstream, and the CMake PRs #9, #12 and #17 were never merged. The CRC file needs -msse4.2 or an equivalent flag. |
| **Platforms** | Targets x86-64: the author says the functions are optimized for modern Intel with no attempt at portability. The non-CRC 64/128-bit code compiles anywhere but assumes little-endian and cheap unaligned loads. The CRC variant is x86-64 with SSE4.2 only. Big-endian was never tested. |
| **Thread safety** | Not documented. From the source, the static Hash() functions are stateless and therefore reentrant. MetroHash64/128 instances carry mutable state and must not be shared across threads without locking. |
| **Drop-in for the baseline** | partial: it covers the same 64-bit, 128-bit and 128-bit CRC variants as City64/City128/CityHashCrc128, but the interface differs. City64 returns a uint64 from (const char\*, size_t), while MetroHash writes bytes into a uint8_t\* output and takes a uint8_t\* input and a uint64 seed. All hash values also change, so a thin wrapper is needed and stored City hashes must be recomputed. |

## Gotchas

- The upstream read_u64/u32/u16 functions dereference reinterpret_cast pointers, which is unaligned, strict-aliasing UB and is flagged 'UB' by SMHasher. ClickHouse's vendored platform.h replaces them with memcpy plus a big-endian byteswap, and that is the copy to vendor.
- The output is a memcpy of the internal little-endian state, and testvector.h states that 'the hash assumes a little-endian architecture'. The same input therefore hashes differently on big-endian machines.
- The README says the implementations are 'fully contained by their respective headers', but they are not: you must compile metrohash64.cpp and metrohash128.cpp (and metrohash128crc.cpp for CRC). The legacy _1/_2 free functions take a 32-bit seed and produce different values from the MetroHash64/128 classes.
- After Finalize() an instance must be re-Initialize()d, or Update()/Finalize() behavior is undefined. The header also notes that the one-shot Hash() can be significantly faster than incremental use.

## Known shortcomings

- Evidence is the author's blog; unmaintained since 2018-10-23. Independent SMHasher shows only a small gap over CityHash on small and mixed inputs, and modern hashes (xxh3, wyhash, rapidhash) are faster.
- Unaligned reinterpret_cast loads (UB) and little-endian-only output (ClickHouse's vendored copy fixes both with memcpy + byteswap). XXH3 is \~2.5x faster in bulk (EPYC) and wyhash is faster too: use only for compatibility with existing MetroHash data. CRC variant is x86 SSE4.2 only; README wrongly says header-only; no build system.

## Caveats and trade-offs

The numbers are relative percentages from the author's 2015 blog post, not raw throughput, and the CPU model, compiler and flags are not stated. The independent rurban/smhasher tables show a far smaller, mixed bulk gap (derived from page data): metrohash64 vs City64 is -1% on Ryzen 3350G, +18% on EPYC 9554P and +2% on i7-6820HQ; metrohash128 vs City128 is +10%, -6% and -3%. On small keys MetroHash uses about 13-23% fewer cycles/hash. SMHasher also flags metrohash64 for UB, LongNeighbors and BIC. The author says it 'is not an active project'.

Not designed for adversarial/DoS-resistant hash-table use like SipHash; algorithmically generated rather than hand-designed; C++ classes support both incremental and one-shot hashing; re-licensed Apache-2.0 in 2018 ahead of a v2.0 that never shipped.

## Maintenance

Abandoned (last commit 2018-10-23, an Apache-2.0 relicense ahead of a v2.0 that never shipped; issues disabled; four CMake/portability PRs unmerged since 2019; the author calls it 'not an active project'), but it is small, dependency-free and Apache-2.0, so it is easy to vendor, ideally from ClickHouse's memcpy-patched copy.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The author's 2015 blog post gives only relative percentages against CityHash in a 'Haswell test environment', with no CPU model, compiler, flags or benchmark code, so the evidence is first-party without methodology: C. Independent SMHasher data does not support a stronger tier because it shows a much smaller, mixed gap.
- **Verifier notes:** The blog numbers match claimed_speedup exactly. The 2022-08-30 date was the repo's pushed_at; the actual last commit is 2018-10-23 (Apache-2.0 relicense), so status stays 'abandoned'. The license is Apache-2.0, the repo has 376 stars, and it is neither a fork nor archived.
- **Fields the verifier corrected:** `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <http://www.jandrewrogers.com/2015/05/27/metrohash/>
  - <https://github.com/jandrewrogers/MetroHash>
  - <https://raw.githubusercontent.com/jandrewrogers/MetroHash/master/README.md>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/README.md>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/metrohash64.txt>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/metrohash128.txt>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/City128.txt>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/table.html>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/epyc.html>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/i7.html>
- **Sources the enricher read:**
  - <https://github.com/jandrewrogers/MetroHash>
  - <https://raw.githubusercontent.com/jandrewrogers/MetroHash/master/README.md>
  - <https://github.com/jandrewrogers/MetroHash/blob/master/src/metrohash.h>
  - <https://github.com/jandrewrogers/MetroHash/blob/master/src/metrohash64.h>
  - <https://github.com/jandrewrogers/MetroHash/blob/master/src/metrohash64.cpp>
  - <https://github.com/jandrewrogers/MetroHash/blob/master/src/metrohash128.h>
  - <https://github.com/jandrewrogers/MetroHash/blob/master/src/metrohash128.cpp>
  - <https://github.com/jandrewrogers/MetroHash/blob/master/src/metrohash128crc.h>
  - <https://github.com/jandrewrogers/MetroHash/blob/master/src/metrohash128crc.cpp>
  - <https://github.com/jandrewrogers/MetroHash/blob/master/src/platform.h>
  - <https://github.com/jandrewrogers/MetroHash/blob/master/src/testvector.h>
  - <https://github.com/jandrewrogers/MetroHash/commits/master>
  - <https://github.com/jandrewrogers/MetroHash/pulls?q=is%3Apr>
  - <https://github.com/jandrewrogers/MetroHash/pull/19>
  - <https://github.com/jandrewrogers/MetroHash/pull/17>
  - <https://github.com/jandrewrogers/MetroHash/pull/6>
  - <http://www.jandrewrogers.com/2015/05/27/metrohash/>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/README.md>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/metrohash64.txt>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/metrohash128.txt>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/metrohash128crc_1.txt>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/epyc.html>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/i7.html>
  - <https://github.com/ClickHouse/ClickHouse/tree/master/contrib/libmetrohash>
  - <https://github.com/ClickHouse/ClickHouse/blob/master/contrib/libmetrohash/CMakeLists.txt>
  - <https://github.com/ClickHouse/ClickHouse/blob/master/contrib/libmetrohash/src/platform.h>
  - <https://github.com/jandrewrogers/AquaHash>
  - <https://hn.algolia.com/api/v1/search?query=metrohash&tags=story>
  - <https://news.ycombinator.com/item?id=9613098>
  - <https://news.ycombinator.com/item?id=10675475>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/jandrewrogers/metrohash`) · [data/wave7/enrich/raw/github_com_jandrewrogers_metrohash.json](../../../data/wave7/enrich/raw/github_com_jandrewrogers_metrohash.json) (enrichment confidence 0.8)

</details>
