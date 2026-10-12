# Minimal perfect hash functions

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md)</sub>

**What these beat:** BBHash; CMPH; RecSplit  
**20 entries:** 14 tier A · 2 tier B · 4 tier C · 0 tier D · 20 copyable, 0 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**PTHash**](jermp-pthash.md) | Header-only C++17 minimal perfect hash library (PTHash/PHOBIC) with 3.1-4.6x faster lookups than BBHash at \~3 bits/key. | **A** | C++ | MIT | 🟢 active |
| 2 | [**PHast / PHast+ (bsuccinct-rs "ph" crate)**](beling-bsuccinct-rs.md) | Rust minimal perfect hash (PHast/PHast+) giving \~10 ns queries at under 2 bits/key; about 5x faster queries than PTHash. | **A** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 3 | [**PtrHash**](ragnargrootkoerkamp-ptrhash.md) | Rust minimal perfect hash with 8-bit pilots (PTHash descendant); queries 2.7-3.8x faster than BBHash, \~7.6x faster than CMPH CHD. | **A** | Rust | MIT | 🟢 active |
| 4 | [**LeMonHash**](bytehamster-lemonhash.md) | Learned monotone minimal perfect hash (key to sorted rank): about 3-5 bits/key and 7-19x faster queries than trie-based MMPHFs. | **A** | C++ | GPL-3.0 | 🟢 active |
| 5 | [**SicHash**](bytehamster-sichash.md) | Cuckoo-hashing-plus-retrieval (minimal) perfect hash for static key sets: about 2.1 bits/key against BBHash's 3.3-3.7, with faster queries. | **A** | C++ | GPL-3.0 | 🟢 active |
| 6 | [**SimdRecSplit / GpuRecSplit**](bytehamster-gpurecsplit.md) | SIMD, multicore and GPU construction of RecSplit minimal perfect hashes; single-threaded builds about 4x faster than BBHash at similar space. | **A** | C++ | GPL-3.0 WITH… | 🟢 active |
| 7 | [**RecSplit (Sux C++ library)**](vigna-sux.md) | Header-only RecSplit MPHF: 1.8 bits/key, smaller than CMPH's CHD and about 2x faster to build and query on 1e9 keys. | **A** | C++ | GPL-3.0-or-later WITH… | 🟡 stale |
| 8 | [**Sphinx**](sfmqrb-sphinx.md) | Dynamic succinct perfect hash index (\~4 bits/key) for log-structured KV stores; paper reports \~2x lower latency than DHT/Aleph Filter. | **A** | C++ | BSD-2-Clause | 🟡 stale |
| 9 | [**ShockHash**](bytehamster-shockhash.md) | C++ minimal perfect hash: RecSplit with cuckoo-hashing leaves, building 1.56-1.58 bits/key MPHFs 15-160x faster than RecSplit/SIMDRecSplit. | **A** | C++ | GPL-3.0 WITH… | 🟡 stale |
| 10 | [**ConsensusRecSplit**](bytehamster-consensusrecsplit.md) | Minimal perfect hash function close to the 1.443 bits/key bound; builds about 100x faster than RecSplit at lower space. | **A** | C++ | GPL-3.0 | 🟡 stale |
| 11 | [**PHOBIC-GPU**](stefanfred-phobic-gpu.md) | Vulkan GPU builder for PHOBIC minimal perfect hash functions; builds about 62x faster than 8-thread CPU PHOBIC. | **A** | C++ | GPL-3.0 | 🟡 stale |
| 12 | [**Engineering Minimal/k-Perfect Hash Functions (stefanfred…**](stefanfred-engineering-k-perfect-hashing.md) | Four minimal k-perfect hash functions; at k=10 threshold-based bumping builds 6.4x and queries 1.7x faster than cmph CHD. | **A** | C++ | GPL-3.0 | 🟡 stale |
| 13 | [**emphf**](ot-emphf.md) | Hypergraph-peeling (MWHC) minimal perfect hash builder that constructs 5-63x faster than CMPH's CHD, using \~0.5 more bits/key. | **A** | C++ | Apache-2.0 | 🔴 abandoned |
| 14 | [**LPHash**](jermp-lphash.md) | Locality-preserving MPHF for DNA k-mer sets: 0.53-0.87 bits/k-mer at k=63, versus 3.06-3.71 for BBHash and 2.04-2.76 for PTHash. | **A** | C++ | MIT | 🔴 abandoned |
| 15 | [**Sux4J (GOV / GOV3Function minimal perfect hash)**](vigna-sux4j.md) | Java GOV minimal perfect hash (F3 linear systems, \~2.2 bits/key) with C lookup; about 2x faster lookups than CMPH's CHD. | **B** | Java | LGPL-2.1-or-later OR… | 🟢 active |
| 16 | [**MorphisHash**](stefanfred-morphishash.md) | Minimal perfect hash function that removes ShockHash's redundant cycle-orientation bits: 1.501 vs 1.523 bits/key at equal build time. | **B** | C++ | GPL-3.0 | 🟡 stale |
| 17 | [**entropy-map**](cloudflare-entropy-map.md) | Cloudflare's immutable Rust map/set on a fingerprinting MPHF (2.1-2.7 bits/key); its edge over std HashMap is compactness, not lookup speed. | **C** | Rust | Apache-2.0 | 🟢 active |
| 18 | [**minperf (RecSplit implementation)**](thomasmueller-minperf.md) | Thomas Mueller's Java RecSplit minimal perfect hash: about 2 bits/key, lookups \~1.1x faster than CHD in one code comment. | **C** | Java | Apache-2.0 | 🔴 abandoned |
| 19 | [**mph (Go, Hash-Displace-Compress / CHD)**](cespare-mph.md) | Pure-Go static string-to-index table (CHD-style minimal perfect hash); author's 2021 benchmark shows 27% faster lookups than map[string]uint32. | **C** | Go | MIT | 🔴 abandoned |
| 20 | [**go-mph (Go, Hash-Displace-Compress)**](dgryski-go-mph.md) | Go hash-and-displace minimal perfect hash for fixed string sets; author reports 25-50% faster index lookups than a Go map. | **C** | Go | MIT | 🔴 abandoned |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
