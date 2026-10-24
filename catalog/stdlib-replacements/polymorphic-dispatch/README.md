# Polymorphic dispatch

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md)</sub>

**What these beat:** virtual member function call through a base-class pointer; dynamic_cast&lt;Derived\*&gt; on a base-class pointer (type test…; virtual function call through a base-class pointer…  
**3 entries:** 0 tier A · 0 tier B · 3 tier C · 0 tier D · 2 copyable, 1 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**Hands-On Design Patterns with C++ 2nd ed: CRTP static…**](paper-book-hands-on-design-patterns-with-cpp-second-edition-crtp-stati-140f164d.md) | Book example: CRTP base-class call versus a virtual call through a base pointer; about 5.8x per 32-call loop. | **C** | C++ | MIT | 🟡 stale |
| 2 | [**Hands-On Design Patterns with C++ 2nd ed: virtual function…**](paper-book-hands-on-design-patterns-with-cpp-second-edition-virtual-ca-6c4ff926.md) | Teaching idiom: replace a dynamic_cast type test with a virtual member call; book example code, not a library. | **C** | C++ | MIT | 🟡 stale |
| 3 | [**Static CRTP dispatch versus virtual calls (Eli Bendersky…**](paper-bendersky-cost-of-virtual-calls-vs-crtp-dispatch.md) | 2013 blog benchmark: CRTP static dispatch runs a trivial-method call loop about 6x faster than virtual calls. | **C** | C++ | no license (study only) | 🔵 finished |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
