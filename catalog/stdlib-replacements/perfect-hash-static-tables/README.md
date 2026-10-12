# Perfect hashing and static tables

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md)</sub>

**What these beat:** std::unordered_map; gperf; phf (rust-phf) static compile-time hash maps  
**21 entries:** 9 tier A · 0 tier B · 12 tier C · 0 tier D · 19 copyable, 2 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**frozen**](serge-sans-paille-frozen.md) | Header-only C++14 constexpr immutable set/map/unordered_map built on compile-time perfect hashing; beats std::unordered_map on fixed key sets. | **A** | C++ | Apache-2.0 | 🟢 active |
| 2 | [**hashify**](stalwartlabs-hashify.md) | Rust proc-macro that compiles fixed byte-string keyword sets into perfect-hash lookups; beats string `match` and the phf crate. | **A** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 3 | [**fph-table (Flash Perfect Hash)**](renzibei-fph-table.md) | Header-only C++17 dynamic perfect-hash map/set with unordered_map-like API: lookups 1.2-7.6x faster than std::unordered_map, inserts far slower. | **A** | C++ | Apache-2.0 | 🟢 active |
| 4 | [**static_maps**](doi-org-10-6084-m9-figshare-31416038.md) | C++23 consteval FKS perfect-hash unordered_map for compile-time keysets; 1.4-2.9x faster than std::unordered_map in three paper demos. | **A** | C++ | MIT | 🟢 active |
| 5 | [**mph (qlibs)**](qlibs-mph.md) | C++20 compile-time perfect-hash lookup built on BMI2 pext; 2.4-10x lower latency than std::unordered_map on 5-100-key string sets. | **A** | C++ | MIT | 🟡 stale |
| 6 | [**GNU gperf**](gnu-mirror-unofficial-gperf.md) | Build-time generator of perfect-hash C/C++ lookup code for fixed keyword sets; about 2-5x faster lookups than std::unordered_map in third-party tests. | **A** | C++ | GPL-3.0-or-later | ⚪ unknown |
| 7 | [**triehash**](julian-klode-triehash.md) | Order-preserving minimal perfect hash generator emitting nested C switches for fixed string sets; 1.85-5x gperf's throughput in author's benchmark. | **A** | C | MIT | 🔴 abandoned |
| 8 | [**phashtable (gsauthof)**](gsauthof-phashtable.md) | Tiny C/C++ two-level perfect hash index, built at startup, that flattens worst-case lookup latency versus std::unordered_map. | **A** | C | BSL-1.0 | 🔴 abandoned |
| 9 | [**zmph (Zig Minimal Perfect Hash Map)**](panda2code-zmph.md) | Pure-Zig minimal perfect hash map for fixed string key sets; about 1.7x faster average lookups than std.StringHashMap. | **A** | Zig | no license (study only) | 🟢 active |
| 10 | [**rust-phf (compile-time perfect hash maps)**](rust-phf-rust-phf.md) | Rust crates that bake immutable perfect-hash maps and sets into the binary at compile time, removing runtime HashMap construction. | **C** | Rust | MIT | 🟢 active |
| 11 | [**constmap**](lemire-constmap.md) | Immutable Go string-to-uint64 map built on binary fuse filters; up to 5.3x faster lookups than map[string]uint64 at 1M keys. | **C** | Go | Apache-2.0 | 🟢 active |
| 12 | [**fastconstmap**](lemire-fastconstmap.md) | Immutable string-to-uint64 map for Python, C11 core, built on binary fuse filters; beats CPython dict lookups and memory. | **C** | C | Apache-2.0 | 🟢 active |
| 13 | [**constexpr-phf (Kronuz/phf)**](kronuz-constexpr-phf.md) | Header-only C++17 constexpr minimal perfect hash for fixed integer key sets; lookups \~2.5x faster than std::unordered_map in author benchmarks. | **C** | C++ | MIT | 🟢 active |
| 14 | [**ConstexprCore/perfect_hash**](constexprcore-perfect-hash.md) | C++23 compile-time perfect-hash set/map for fixed string keys; author measures \~10x std::unordered_map throughput on a 6-key set. | **C** | C++ | MIT | 🟢 active |
| 15 | [**lute**](astral4-lute.md) | Rust no_std perfect-hash immutable Map/Set (up to 65,535 keys) with 1.9x-16.9x lower query time than phf. | **C** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 16 | [**fastcpp::phf (developer source)**](private-developer-source.md) | Compile-time perfect hash table for fixed string-key sets (keywords, opcodes); 5.8-7x faster lookups than std::unordered_map. | **C** | C++ | MIT | 🟢 active |
| 17 | [**icy**](romainaugier-icy.md) | C++23 consteval perfect-hash map/set for fixed keys; \~1.6-1.8x faster string_view hits than std::unordered_map in the author's benchmark. | **C** | C++ | BSD-3-Clause | 🟢 active |
| 18 | [**QuickPHF**](dtrifuno-quickphf.md) | Rust PTHash-based static maps/sets generated at build time; \~2x faster lookups and 10x+ faster generation than phf. | **C** | Rust | MIT OR Apache-2.0 OR Zlib | 🟡 stale |
| 19 | [**cmph / cxxmph (mph_map)**](zvelo-cmph.md) | C minimal-perfect-hash library (BDZ/CHD/BRZ) plus cxxmph::mph_map, claimed 10-50% faster than std::unordered_map on &gt;100k URLs. | **C** | C | LGPL-2.1-only OR MPL-1.1 | 🔴 abandoned |
| 20 | [**Perfect::Hash / pperf**](rurban-perfect-hash.md) | Perl generator (pperf) that emits C perfect-hash lookup tables; builds 100k-key tables in 1-2 s where gperf times out. | **C** | C | Artistic-1.0-Perl OR… | 🔴 abandoned |
| 21 | [**strager/perfect-hash-tables**](strager-perfect-hash-tables.md) | Research generator of CRC32-hashed perfect hash tables for 80 JS/TS keywords; beats gperf \~1.2-1.4x except on keyword-only input. | **C** | C++ | CC-BY-NC-ND-4.0 (study only) | 🔴 abandoned |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
