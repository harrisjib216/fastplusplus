# Bitsets and succinct bit vectors

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md)</sub>

**What these beat:** std::bitset, std::vector&lt;bool&gt;  
**7 entries:** 3 tier A · 0 tier B · 4 tier C · 0 tier D · 5 copyable, 2 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**CRoaring (Roaring Bitmaps)**](roaringbitmap-croaring.md) | Compressed bitmap for sparse 32/64-bit integer sets; set-algebra ops beat std::unordered_set/vector by 3x-800x, loses on dense data. | **A** | C | Apache-2.0 OR MIT | 🟢 active |
| 2 | [**pasta::bit_vector**](pasta-toolbox-bit-vector.md) | Header-only C++20 rank/select bit vector: 8% faster rank, 16.5% faster select than cs-poppy. | **A** | C++ | GPL-3.0 | 🟡 stale |
| 3 | [**plf::bitset (plf_bitsets)**](mattreecebentley-plf-bitsets.md) | Header-only bitset beating std::bitset at ranged set/reset, shifts, and bit search, minus from-string constructors. | **A** | C++ | Computing For Good License… (study only) | 🟢 active |
| 4 | [**libpopcnt**](kimwalisch-libpopcnt.md) | Single-header C/C++ array popcount with runtime CPU dispatch (AVX512 VPOPCNTDQ, AVX2, NEON, SVE); beats a scalar POPCNT loop on mid-size and large buffers. | **C** | C | BSD-2-Clause | 🟢 active |
| 5 | [**sul::dynamic_bitset**](pinam45-dynamic-bitset.md) | Header-only C++17/20 dynamic bitset beating std::vector&lt;bool&gt; on word-level shift/count operations in third-party benchmarks. | **C** | C++ | MIT | 🟢 active |
| 6 | [**BitLib**](bkille-bitlib.md) | Header-only bit_vector and STL-style bit algorithms that beat std::vector&lt;bool&gt; by operating word-at-a-time instead of bit-at-a-time. | **C** | C++ | BSD-3-Clause | 🟡 stale |
| 7 | [**better_bitset**](mrelectrify-better-bitset.md) | Header-only C++20 bitset adding fast first_one/first_zero bit-scan that std::bitset lacks above 64 bits. | **C** | C++ | no license (study only) | 🔴 abandoned |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
