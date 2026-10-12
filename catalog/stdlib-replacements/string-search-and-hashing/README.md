# String search and hashing

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md)</sub>

**What these beat:** std::string::find, std::hash, std::search  
**10 entries:** 5 tier A · 1 tier B · 4 tier C · 0 tier D · 10 copyable, 0 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**komihash**](avaneev-komihash.md) | Header-only, non-cryptographic 64-bit hash beating wyhash and xxHash on short keys (0-31 bytes) via full 128-bit multiply accumulation. | **A** | C | MIT | 🟢 active |
| 2 | [**MUM/VMUM hash**](vnmakarov-mum-hash.md) | Header-only C multiply-mix hash family (MUM/VMUM) rivaling xxHash3, beating CityHash and SipHash24 on most key sizes. | **A** | C | MIT | 🟢 active |
| 3 | [**HighwayHash**](google-highwayhash.md) | SIMD-based keyed hash function; \~5x faster than SipHash at 1 KiB while keeping DoS-resistant strong-hash security claims. | **A** | C++ | Apache-2.0 | 🔴 abandoned |
| 4 | [**t1ha (Fast Positive Hash)**](erthink-t1ha.md) | Portable C hash family (t1ha0/1/2) beating xxHash/Murmur on bulk throughput; modest edge on tiny keys. | **A** | C | Zlib | 🔴 abandoned |
| 5 | [**sse4-strstr (SIMD-friendly algorithms for substring…**](wojciechmula-sse4-strstr.md) | SIMD substring-search kernels (SSE2-AVX512, NEON) from a blog article; beats glibc strstr by \~1.3-1.8x on x86. | **A** | C++ | BSD-2-Clause | 🔴 abandoned |
| 6 | [**rapidhash**](nicoshev-rapidhash.md) | Header-only, wyhash-derived 64-bit hash beating xxh3 on latency and throughput on most CPUs; ties or loses on AMD Ryzen. | **B** | C | MIT | 🟢 active |
| 7 | [**StringZilla**](ashvardanian-stringzilla.md) | Header-only SIMD string kernels (search, hashing, sort, UTF-8) beating std::string::find and find_first_of. | **C** | C++ | Apache-2.0 | 🟢 active |
| 8 | [**glibc (libc string functions, qsort, regexec, strtod…**](bminor-glibc.md) | GNU C library; its CPU-dispatched string routines, malloc, qsort, regexec and strtod beat zig-bundled static musl in most micro-benchmarks. | **C** | C | LGPL-2.1-or-later | 🟢 active |
| 9 | [**Boost.Algorithm Boyer-Moore / Boyer-Moore-Horspool searchers**](boostorg-algorithm.md) | Header-only Boyer-Moore / Boyer-Moore-Horspool string searchers, \~4-5x faster than std::search on long patterns. | **C** | C++ | BSL-1.0 | 🟢 active |
| 10 | [**CityHash**](google-cityhash.md) | Non-cryptographic 64/128-bit string hash family beating Murmur2/Murmur3F, \~1.7-2.5x faster at 64 bytes. | **C** | C++ | MIT | 🔴 abandoned |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
