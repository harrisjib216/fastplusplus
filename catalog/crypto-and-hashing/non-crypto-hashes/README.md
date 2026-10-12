# Non-cryptographic hashes

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md)</sub>

**What these beat:** xxHash, wyhash, CityHash, std::hash  
**31 entries:** 6 tier A · 18 tier B · 7 tier C · 0 tier D · 31 copyable, 0 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**xxHash**](cyan4973-xxhash.md) | SIMD-vectorized non-cryptographic hash family; XXH3 beats CityHash \~2.7x on in-RAM buffer bandwidth. | **A** | C | BSD-2-Clause (library… | 🟢 active |
| 2 | [**foldhash**](orlp-foldhash.md) | Seeded folded-multiply Rust hasher for in-memory HashMaps; about 4.6x lower geometric-mean time per op than SipHash-1-3. | **A** | Rust | Zlib | 🟢 active |
| 3 | [**CLHash**](simdhash-clhash.md) | Keyed 64-bit universal string hash built on carry-less multiply; about 40% faster than CityHash64 on inputs over 64 bytes. | **A** | C | Apache-2.0 | 🟢 active |
| 4 | [**ChainHash**](thomasahle-chainhash.md) | Keyed 64-bit carry-less universal hash with a Lean-proved collision bound; beats XXH3-64 on long in-cache inputs. | **A** | C | MIT | 🟢 active |
| 5 | [**hayahash**](thevilledev-hayahash.md) | Portable scalar 64/128-bit C hash; beats XXH3-64 by about 1.35x on 1 MiB bulk in SIMD-less wasm32. | **A** | C | Unlicense | 🟢 active |
| 6 | [**haya32x64**](thevilledev-haya32x64.md) | 64-bit non-cryptographic hash built only from 32-bit operations. In pure JS it beats xxhash-wasm XXH64 on 4-8 byte keys. | **A** | C | Unlicense | 🟢 active |
| 7 | [**wyhash**](wangyi-fudan-wyhash.md) | Header-only 64-bit non-cryptographic hash + PRNG; about 9% faster bulk throughput than xxHash's XXH3. | **B** | C | Unlicense | 🟢 active |
| 8 | [**gxhash**](ogxd-gxhash.md) | AES-round Rust hash: about 1.5-2.35x XXH3's bulk throughput in SMHasher suites, but slower than XXH3 on keys under 32 bytes. | **B** | Rust | MIT | 🟢 active |
| 9 | [**FarmHash**](google-farmhash.md) | Google's CityHash successor. Its SSE4.1 32-bit hash is 3.9x City32 and \~6% faster than XXH3 on large x86-64 inputs. | **B** | C++ | MIT | 🟢 active |
| 10 | [**UMASH**](backtrace-labs-umash.md) | Keyed CLMUL-based C string hash with a proven almost-universal collision bound; 1.5-2.5x CityHash64 bulk throughput, roughly xxh3 parity. | **B** | C | MIT | 🟢 active |
| 11 | [**ChibiHash**](n-r-k-chibihash.md) | 82-line public-domain C header 64-bit hash; about 1.5x XXH64 bulk throughput and a third fewer cycles on short keys. | **B** | C | Unlicense | 🟢 active |
| 12 | [**Rain (Rainbow hash)**](dosaygo-studio-rain.md) | Small scalar multiply-rotate hash with 64/128/256-bit output; beats HighwayHash-128/256 and FarmHash-128 only on short-key latency. | **B** | C++ | Apache-2.0 | 🟢 active |
| 13 | [**MuseAir**](eternal-io-museair.md) | Portable wide-multiply Rust hash: about 1.9-2.2x XXH64 and 1.1-1.3x wyhash on bulk data; XXH3 is faster in SMHasher3. | **B** | Rust | MIT OR Apache-2.0 for the… | 🟢 active |
| 14 | [**a5hash**](avaneev-a5hash.md) | Tiny header-only C hash for hash-map keys; beats XXH64 and edges wyhash on short keys, but slow on bulk data. | **B** | C | MIT | 🟢 active |
| 15 | [**W1Hash**](peterrk-w1hash.md) | A wyhash-derived 64-bit non-cryptographic hash, tuned to spend fewer cycles on 1-16 byte keys than wyhash v4.2. | **B** | C | BSD-3-Clause | 🟢 active |
| 16 | [**SpookyHash V2 (Bob Jenkins' official repo)**](bobjen-spookyhash.md) | Bob Jenkins' own reference C++ SpookyV2, a 128-bit non-cryptographic hash about 1.2x faster than XXH64 on large buffers. | **B** | C++ | Unlicense | 🟢 active |
| 17 | [**lanehash**](ccipherx-lanehash.md) | Rust SIMD non-cryptographic 64/128-bit hash with a C99 port. First-party Zen 4 numbers show 1.5-2.2x xxh3 at 1-64 KiB, but it is slower on tiny keys. | **B** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 18 | [**NMHASH (NMHASH32X)**](gzm55-hash-garage.md) | Header-only 32-bit seeded C hash built on 16-bit SIMD multiplies; about 2x XXH64 bulk throughput with AVX2, weak SMHasher3 quality. | **B** | C | BSD-2-Clause | 🟡 stale |
| 19 | [**SeaHash**](gitlab-redox-os-org-redox-os-seahash.md) | Portable, no_std Rust 64-bit non-crypto hash; \~11x FNV-1a and \~16% over MurmurHash3 bulk, but slower than xxHash64/XXH3. | **B** | Rust | MIT | 🟡 stale |
| 20 | [**Meow hash**](cmuratori-meow-hash.md) | 128-bit AES-NI bulk hash for x86-64 file and asset hashing; about 3x XXH64's large-buffer throughput, roughly tied with XXH3. | **B** | C | Zlib | 🔴 abandoned |
| 21 | [**AquaHash**](jandrewrogers-aquahash.md) | Single-header AES-NI 128-bit hash: about 4x XXH64 bulk throughput in SMHasher3, but fails 55/250 quality tests. | **B** | C++ | Apache-2.0 | 🔴 abandoned |
| 22 | [**falkhash**](gamozolabs-falkhash.md) | One-function AES-NI 128-bit hash for x86-64; 1.4-2.5x XXH3 bulk throughput, but 3-4x slower on small keys. | **B** | C | Unlicense | 🔴 abandoned |
| 23 | [**HalftimeHash**](jbapple-halftimehash.md) | Keyed almost-universal C++ hash for long strings; \~1.3-1.4x xxh128 on 256 KiB inputs with AVX-512. | **B** | C++ | Apache-2.0 | 🔴 abandoned |
| 24 | [**pengyhash**](tinypeng-pengyhash.md) | Tiny multiply-free 64-bit ARX hash; its v0.2 beat xxHash64 bulk speed in rurban/smhasher, current v0.3 does not. | **B** | C | GPL-3.0 | 🔴 abandoned |
| 25 | [**aHash**](tkaitchuck-ahash.md) | Keyed AES-round Rust hasher for in-memory HashMaps; about 11x faster than SipHash-1-3, claims wins over xxh3/wyhash. | **C** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 26 | [**rustc-hash (FxHash)**](rust-lang-rustc-hash.md) | rustc's own tiny multiply-based hasher and FxHashMap/FxHashSet aliases. Much faster than std SipHash-1-3 on integer-heavy keys, but not DoS-resistant. | **C** | Rust | Apache-2.0 OR MIT | 🟢 active |
| 27 | [**rapidhash (Rust port)**](hoxxep-rapidhash.md) | Rust rapidhash (wyhash successor): portable 64-bit hasher, faster than XXH64/wyhash and faster than XXH3 up to about 4 KB inputs. | **C** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 28 | [**CircleHash64f**](fxamacker-circlehash.md) | Pure-Go seeded 64-bit hash from Abseil's wyhash-style design; beats seeded XXH3 5-13% at 4-128 B, 1.4-1.8x at 192-256 B. | **C** | Go | Apache-2.0 | 🟢 active |
| 29 | [**SmolRapidhash (Unity/Burst port of rapidhash)**](aras-p-unitysmolrapidhash.md) | A single-file C#/Burst port of rapidhash V3 for Unity. On large buffers it is about 1.6-2.3x faster than Unity.Collections' Burst xxHash3. | **C** | C# | MIT | 🟢 active |
| 30 | [**MuseAir (C++ port)**](twilight-dream-of-magic-museair-cpp.md) | GPL-3.0 C++20 header port of deprecated MuseAir v0.4-rc4. Ties wyhash in bulk, slower on short keys. | **C** | C++ | GPL-3.0 | 🟢 active |
| 31 | [**MetroHash**](jandrewrogers-metrohash.md) | 2015 family of machine-generated 64/128-bit non-cryptographic hashes pitched as a faster CityHash; now outpaced by XXH3 and wyhash. | **C** | C++ | Apache-2.0 | 🔴 abandoned |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
