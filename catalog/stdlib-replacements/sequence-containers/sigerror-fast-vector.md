# fast_vector (sigerror/fast-vector)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sequence containers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Header-only C++17 vector without zero-init, exceptions, or a real allocator; beats std::vector on trivial-type push_back workloads.

| | |
|---|---|
| **Beats** | std::vector |
| **Claimed result** | Trivial types: push_back 20,126ns (std::vector) vs 9,392ns (fast_vector) \~2.1x; reserve+push_back 12,991ns vs 6,416ns \~2.0x; push_back+pop_back 12,704ns vs 9,253ns \~1.4x (all derived from page data). Non-trivial types: push_back 137,225ns vs 121,523ns \~1.1x; emplace_back 87,804ns vs 65,897ns \~1.3x (derived from page data) |
| **Workload** | Google Benchmark of push_back, reserve+push_back, push_back+pop_back and emplace_back over 10,000 elements, for both trivial and non-trivial element types |
| **Metric** | latency |
| **Hardware** | Intel Core i7-4720HQ, 8GB DDR3 |
| **Compiler and flags** | Visual Studio 2017 (exact optimization flags/build configuration not stated) |
| **Adoption** | 21 stars |
| **Last commit** | 2019-04-20 |
| **Links** | [repository](https://github.com/sigerror/fast-vector) · [benchmark](https://github.com/sigerror/fast-vector) |

## Verdict

On an Intel i7-4720HQ (Visual Studio 2017, MSVC STL, Windows 10), Google Benchmark over 10,000 elements showed fast_vector roughly 1.4-2.1x faster than std::vector for trivial-type push_back, reserve+push_back, and push_back+pop_back, but only about 1.0-1.3x for non-trivial types, with non-trivial reserve+push_back essentially a wash (88,303ns vs 88,671ns).

## Use it when

- Hot loops doing push_back/emplace_back on many trivial (POD) elements where leaving memory uninitialized (instead of value-initialized) is acceptable
- Codebases already built assertions-first/exceptions-off (e.g. game or low-latency style code) that want realloc-based growth instead of malloc+copy+free
- Header-only vendoring into a C++17 project where pulling in a full container library is undesirable
- Non-trivial types specifically via emplace_back (\~1.3x measured) rather than push_back+pop_back or reserve+push_back, which show little to no win for non-trivial T

## Skip it when

- Any code that copies or copy-assigns a fast_vector&lt;T&gt; where sizeof(T) &gt; 1: the copy ctor/operator= call memcpy(dst, src, other.m_size) using element count instead of byte count, under-copying data (open issue #2, unresolved since 2019)
- operator=(const fast_vector&) never frees the destination's existing allocation before overwriting the pointer, leaking the old buffer on reassignment
- Anything needing insert()/erase() at arbitrary positions, at(), swap(), comparison operators, or initializer-list construction — none exist (open issue #1)
- Release builds where out-of-bounds safety matters: assert() is a no-op under NDEBUG, so operator[]/front/back/pop_back have zero bounds checking in release
- Non-trivial-type reserve+push_back workloads specifically: the README's own numbers show std::vector 88,303ns vs fast_vector 88,671ns, i.e. no measured win

## How it is fast

For trivial T, reserve/resize skip the construct/destruct loops std::vector runs and grow via realloc() in place instead of malloc+copy+free; push_back writes trivial elements by assignment rather than placement-new. Bounds and precondition checks are assert()-based, so unlike std::vector's exception-safety machinery they cost nothing under NDEBUG. There is no SIMD, custom allocator, or branchless logic involved — the win is purely from removing zero-initialization and object-lifetime bookkeeping that trivial types don't need.

## Compared with alternatives

Pick it over plf::colony/plf::list/veque/EASTL only when you want a minimal, header-only, std::vector-shaped container purely for trivial-type push_back-heavy code and can tolerate its two open correctness bugs; veque and plf::colony/plf::list report larger, more thoroughly benchmarked wins for their respective access patterns, and EASTL is a more mature, allocator-aware drop-in that fast_vector doesn't match.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (only &lt;cassert&gt;, &lt;cstdlib&gt;, &lt;cstring&gt;, &lt;new&gt;, &lt;type_traits&gt; from the standard library) |
| **Minimum toolchain** | C++17 (stated in README); benchmarked with Visual Studio 2017, no other compiler/version documented |
| **Platforms** | any — portable C++17, no platform-specific intrinsics or code observed in fast_vector.h |
| **Thread safety** | not documented; no internal synchronization in the header, same external-locking burden as std::vector |
| **Drop-in for the baseline** | partial — explain: same core method names (push_back/emplace_back/pop_back/resize/reserve/iterators) as std::vector, but missing insert/erase/at/swap/allocator support, no value-initialization, and two unresolved correctness bugs (wrong memcpy size, leak in copy-assignment) make it unsafe as a literal find-and-replace for std::vector |

## Gotchas

- Copy constructor and copy-assignment memcpy the wrong byte count (other.m_size instead of other.m_size \* sizeof(T)) for trivial T larger than 1 byte — filed as issue #2, still open at last commit
- Copy-assignment operator leaks the destination's prior allocation: it never calls std::free on the old m_data before reassigning the pointer
- grow_factor is advertised as 'modifiable' but is a static constexpr size_type = 2 baked into the header, not a template or runtime parameter — changing it means editing the source
- reserve()/resize() assert preconditions (new_cap &gt; capacity; count != size) that are silently skipped in release builds rather than raising an error

## Caveats and trade-offs

Only tested against MSVC STL on one Windows machine; no libstdc++ or libc++ numbers. Build configuration and flags are not stated, and the benchmark source is not in the repo. For non-trivial types, reserve+push_back is a wash (std 88,303ns vs fast_vector 88,671ns) and push_back+pop_back is only \~1.06x (101,814 vs 96,396ns). No commits since 2019.

Drops zero-initialization and exception handling (uses assertions instead) and exposes a configurable growth factor; part of the speedup comes from these relaxed semantics, so it is not a strict drop-in replacement for code relying on value-initialization or exceptions

## Maintenance

Abandoned since its last commit on 2019-04-20, with two unresolved open issues (a copy-constructor memcpy bug and a missing insert/erase request); MIT-licensed, 21 stars, and small enough — one header — to vendor and patch yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README shows first-party Google Benchmark output against std::vector on an i7-4720HQ with VS2017. The repo contains no benchmark code (only fast_vector.h, README.md and LICENSE) and states no optimization flags, so it is not A.
- **Verifier notes:** All claimed timings match the README exactly, and the derived ratios are correct. last_commit corrected to the default-branch commit date (the 2019-06-21 date was pushed_at). MIT, 21 stars, not archived.
- **Fields the verifier corrected:** `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/sigerror/fast-vector>
- **Sources the enricher read:**
  - <https://github.com/sigerror/fast-vector>
  - <https://github.com/sigerror/fast-vector/blob/master/README.md>
  - <https://github.com/sigerror/fast-vector/blob/master/fast_vector.h>
  - <https://github.com/sigerror/fast-vector/issues/1>
  - <https://github.com/sigerror/fast-vector/issues/2>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/sigerror/fast-vector`) · [data/wave1/enrich/raw/github_com_sigerror_fast_vector.json](../../../data/wave1/enrich/raw/github_com_sigerror_fast_vector.json) (enrichment confidence 0.6)

</details>
