# Ranges and views

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md)</sub>

**What these beat:** the issue's 'handrolled' implementation, marked '# base' in…; std::ranges / std::views (libstdc++ 13): filter, chunk…  
**2 entries:** 0 tier A · 0 tier B · 2 tier C · 0 tier D · 2 copyable, 0 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**range-v3**](ericniebler-range-v3.md) | Header-only C++14/17/20 ranges library (basis of std::ranges); one bug-report benchmark beat an unshown hand-rolled loop by 3-13%. | **C** | C++ | BSL-1.0 | 🟢 active |
| 2 | [**cpp-lazy**](kaaserne-cpp-lazy.md) | Header-only C++11 lazy-iterator library; first-party 32-element benchmarks show filter 3.6x and chunks 2.6x faster than std::views. | **C** | C++ | MIT | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
