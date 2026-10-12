# k-mer dictionaries

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md)</sub>

**What these beat:** SSHash; Pufferfish (and dBG-FM, BLight k-mer dictionaries); Pufferfish  
**3 entries:** 1 tier A · 2 tier B · 0 tier C · 0 tier D · 3 copyable, 0 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**RSHash**](jonsmcode-rshash.md) | Static compressed k-mer dictionary that swaps SSHash's MPHF for rank/select bitvectors; 1.4x faster streaming lookups than current SSHash. | **A** | C++ | MIT | 🟢 active |
| 2 | [**SSHash**](jermp-sshash.md) | Compressed static DNA k-mer dictionary: \~5x smaller than Pufferfish, 1.6-2.4x faster streaming lookups, but slower random lookups. | **B** | C++ | MIT | 🟢 active |
| 3 | [**BLight**](malfoy-blight.md) | Minimizer-partitioned, MPHF-based exact k-mer dictionary; indexes human k=31 at 22.3 bits/k-mer versus Pufferfish's 55.6. | **B** | C++ | AGPL-3.0 | 🟡 stale |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
