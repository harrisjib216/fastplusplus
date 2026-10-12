# SmallFunction (LoopPerfect/smallfunction)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Smart pointers and reference counting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Header-only, fixed-capacity alternative to std::function that placement-news the callable into an inline stack buffer instead of the heap.

| | |
|---|---|
| **Beats** | std::function |
| **Claimed result** | README claims SmallFun is '3-5x faster than std::function' in some benchmarks. Table (ns, lower is better): std::function 1141 ns (g++6) / 1511 ns (clang++6 & libc++) vs sf32 312/300, sf64 369/310, sf128 346/333, sf256 376/320, sf512 503/450, sf1024 569/512, sf2048 870/709. That is about 3.0-3.7x (g++6) and 4.5-5.0x (clang) for 32-256-byte buffers, falling to 1.3x (g++6) / 2.1x (clang) at sf2048 (derived from page data) |
| **Workload** | Google Benchmark: assign 100 identical small lambdas (capture int i, unsigned N) into a vector of std::function or SmallFun&lt;..., B&gt; (B = 32-2048 byte buffer), then invoke all via std::transform, per iteration |
| **Metric** | throughput |
| **Compiler and flags** | g++6 and clang++6/libc++; repo .buckconfig sets cxxflags = -O3 -Os -Ofast |
| **Adoption** | 54 stars |
| **Last commit** | 2018-01-04 |
| **Links** | [repository](https://github.com/LoopPerfect/smallfunction) · [benchmark](https://github.com/LoopPerfect/smallfunction#benchmarks) |

## Verdict

First-party Google Benchmark (100 identical lambdas capturing int i and unsigned N, assigned into a vector and invoked via std::transform per iteration) on g++6 and clang++6/libc++, no CPU stated: std::function averaged 1141 ns (g++6) / 1511 ns (clang++6+libc++) versus SmallFun buffers from 312 ns (32-byte) up to 870 ns (2048-byte) on g++6 — about 3.0-3.7x faster at 32-256-byte buffers, narrowing to 1.3x at 2048 bytes (up to \~5.0x on clang at the smallest buffer).

## Use it when

- Hot loops that repeatedly construct/reassign many short-lived small-capture callables (the upstream benchmark: 100 lambdas capturing one int and one unsigned, assigned and invoked per iteration).
- Capture size is small and known ahead of time — the largest wins (3-5x) are at 32-256 byte buffers.
- A single call site can commit to one fixed buffer size and doesn't need to store arbitrarily-sized callables behind one type.
- You're willing to vendor a \~100-line single header (MIT) and patch it yourself rather than rely on upstream maintenance.
- Target has relaxed alignment handling for unaligned/misaligned loads (see gotchas) or you've verified/fixed the alignment issue yourself.

## Skip it when

- You need to store callables of unpredictable or varying size behind one type — oversized captures are a hard compile error here, not a transparent heap fallback like std::function.
- Captures include pointers or other over-aligned members on strict-alignment platforms (e.g. ARM) — issue #1 shows UBSan-confirmed misaligned member-access crashes because storage is a plain char[N] with no alignas.
- Code paths may call a default-constructed or moved-from SmallFun — invoking an empty one is undefined behavior; std::function would throw std::bad_function_call instead.
- You require move semantics for move-only state — SmallFun only defines copy construction/assignment.
- You need an actively maintained dependency — last commit 2018-01-04, the alignment bug is still open, and the only fix (PR #3, alignof(std::max_align_t)) was never merged.

## How it is fast

Classic type erasure (SFConcept/SFModel, i.e. a hand-rolled PImpl) combined with small-buffer optimization: the Model is placement-new'd directly into a char[N] member on the stack, removing the heap allocation and one pointer indirection that std::function pays on every assignment. The repo's own Google Benchmark constructs and invokes 100 small lambdas per iteration; because the gain is almost entirely 'no malloc', it is largest for small buffers and shrinks as N grows and the inline copy itself gets more expensive to construct/copy.

## Compared with alternatives

Pick SmallFun over woid, Delegate, or sy_callback.hpp when you want the smallest possible (\~100-line) header-only SBO implementation to vendor and are willing to patch the known alignment bug yourself; stdext::inplace_function (WG21-SG14) implements the same idea with an actively-referenced SG14 design and no open alignment defect, and is the safer default when that matters more than minimalism.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (only &lt;type_traits&gt;) |
| **Minimum toolchain** | C++14 (uses std::enable_if_t); upstream benchmarked with g++6 and clang++6/libc++ |
| **Platforms** | any standard C++ target in principle; not safe on strict-alignment platforms without patching the buffer's alignment (see gotchas) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — explain: same construct/assign/call syntax as std::function, but requires choosing a compile-time buffer size, rejects (does not heap-fallback) oversized callables at compile time, has no operator bool/empty check, and lacks move semantics |

## Gotchas

- Storage is a raw char[size] member with no alignas; open issue #1 documents a UBSan-caught case (pointer capture placed after a bool member) producing 'member call on misaligned address ... requires 8 byte alignment' crashes. An unmerged PR (#3) fixes this via alignof(std::max_align_t), but master still ships without it.
- operator() has no allocated-flag check, so calling a default-constructed or emptied SmallFun is undefined behavior rather than throwing.
- No move constructor or move-assignment operator is defined — only copy, which round-trips through the stored callable's own copy constructor.
- Exceeding the fixed buffer size for a given signature is a compile-time SFINAE failure, so bumping a lambda's capture set can break the build until you also raise the template's size parameter.

## Caveats and trade-offs

First-party benchmark; flags come from .buckconfig (-O3 -Os -Ofast) but no CPU model is stated, so tier is capped at C. The speedup shrinks with larger buffers (1.3x g++6 at sf2048). SmallFun rejects at compile time (enable_if) any callable larger than its fixed buffer; there is no heap fallback. No commits since January 2018.

Stack capacity is a fixed compile-time template parameter (e.g. SmallFun&lt;Sig,64&gt;); no heap fallback for oversized captures, so it is not template-compatible drop-in replacement for arbitrary-size std::function usages.

## Maintenance

Abandoned: no commits since 2018-01-04, the same day an alignment bug (issue #1) was reported and an unrelated operator= bug (issue #2) was fixed; MIT-licensed and small enough to vendor and patch, but the alignment issue is unresolved on master and its only proposed fix (PR #3) was never merged.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party Google Benchmark code is public (smallfun/apps/main.cpp) and .buckconfig sets cxxflags '-O3 -Os -Ofast', compilers named (g++6, clang++6/libc++), but no CPU model is stated, so it cannot be A; being first-party, it is C.
- **Verifier notes:** Numbers match the README table. The record's '3.1-4.9x depending on buffer size/compiler' range covers only sf64 and overstates the low end (real range 1.3-5.0x across buffers), so claimed_speedup is corrected; tier stays C. Metadata verified: MIT, 54 stars, last commit 2018-01-04, not archived or a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/LoopPerfect/smallfunction>
  - <https://github.com/LoopPerfect/smallfunction#benchmarks>
  - <https://github.com/LoopPerfect/smallfunction/blob/master/smallfun/apps/main.cpp>
  - <https://github.com/LoopPerfect/smallfunction/blob/master/.buckconfig>
  - <https://github.com/LoopPerfect/smallfunction/blob/master/BUCK>
  - <https://github.com/LoopPerfect/smallfunction/blob/master/LICENSE>
  - <https://github.com/LoopPerfect/smallfunction/blob/master/smallfun/include/smallfun.hpp>
- **Sources the enricher read:**
  - <https://github.com/LoopPerfect/smallfunction>
  - <https://github.com/LoopPerfect/smallfunction/blob/master/smallfun/include/smallfun.hpp>
  - <https://github.com/LoopPerfect/smallfunction/issues>
  - <https://github.com/LoopPerfect/smallfunction/issues/1>
  - <https://github.com/LoopPerfect/smallfunction/issues/2>
  - <https://github.com/LoopPerfect/smallfunction/pull/3>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/loopperfect/smallfunction`) · [data/wave1/enrich/raw/github_com_loopperfect_smallfunction.json](../../../data/wave1/enrich/raw/github_com_loopperfect_smallfunction.json) (enrichment confidence 0.55)

</details>
