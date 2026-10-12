# Utilities

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md)</sub>

**What these beat:** std::copy_if (and a hand-written for loop); ncurses (wide-char build); glibc memcpy / memset / memmove (system libc, called as…  
**3 entries:** 0 tier A · 0 tier B · 2 tier C · 1 tier D · 3 copyable, 0 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**FunctionalPlus (fplus::keep_if)**](dobiasd-functionalplus.md) | Header-only functional helpers (keep_if, transform, fold, compose) over STL containers; matches std::copy_if speed, does not beat it. | **C** | C++ | BSL-1.0 | 🟢 active |
| 2 | [**netbsd-curses**](sabotage-linux-netbsd-curses.md) | Portable Linux build of NetBSD's widechar curses; builds 6.6x faster and installs far smaller than ncurses, with no runtime benchmark. | **C** | C | BSD-2-Clause AND… | 🟡 stale |
| 3 | [**micron.cpp (cmemory memcpy/memset/memmove)**](rfgplk-micron-cpp.md) | Header-only inline memcpy/memset/memmove from the freestanding micron libc/STL rewrite; 1.13-1.91x fewer cycles than glibc on SPEC2017-size random copies. | **D** | C++ | BSL-1.0 | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
