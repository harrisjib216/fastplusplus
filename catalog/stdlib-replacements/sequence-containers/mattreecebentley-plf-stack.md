# plf::stack

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sequence containers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Zlib` · 🟢 active

> Header-only LIFO container on chained, never-relocated memory blocks; author reports it beats std::stack over std::deque.

| | |
|---|---|
| **Beats** | std::stack (default std::deque backing container) |
| **Claimed result** | 82% faster for 1-byte types, 83% for 4-byte, 80% for 8-byte, 82% for 40-byte and 724% faster for 490-byte types than std::stack over std::deque, averaged over 10 to 1,000,000 stored elements (README wording). |
| **Workload** | Total time to construct, push all elements, read and pop all elements, then destruct, averaged across stored element counts from 10 to 1,000,000, for 1-, 4-, 8-, 40- and 490-byte element types. |
| **Metric** | throughput |
| **Adoption** | 79 stars |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/mattreecebentley/plf_stack) · [benchmark](https://github.com/mattreecebentley/plf_stack) |

## Verdict

The README (first party) reports plf::stack 82%, 83%, 80%, 82% and 724% faster than std::stack over std::deque for 1-, 4-, 8-, 40- and 490-byte elements, averaged over 10 to 1,000,000 elements for construct, push, read-and-pop, destruct, against libstdc++; compiler, flags and CPU are not in the repo, and per search snippets the plflib.org benchmark pages (blocked here) used a Core2 E8500 with GCC 5.1 -O2 -march=native and a Xeon E3-1241 with mingw GCC 9.2, so it is not known which run produced the README averages.

## Use it when

- LIFO workloads (DFS, undo stacks, parsers, work lists) whose size swings widely, where std::stack's default std::deque spends time in allocation and block-map management.
- Large or non-trivially-movable element types: the README's biggest gain (724% for 490-byte elements under libstdc++) comes where std::deque degenerates to one element per block and std::vector would have to relocate on growth.
- Code that keeps pointers or references into the stack (inter-linked data) and needs them to stay valid while more elements are pushed.
- Projects stuck on old compilers: the header still supports C++98/03 and adds move, emplace and allocator_traits support when the compiler has them.

## Skip it when

- Small trivially copyable elements (char, int) where a std::vector-backed stack with reserve() is competitive: per a search snippet of the author's own Haswell GCC 9.2 page, std::vector beat plf::stack for char, which contradicts the README's 'faster than all std:: containers' line (snippet only; page blocked here).
- When you need the evidence reproduced: the README gives only averages and the benchmark code is not in any of the author's GitHub repositories; per search snippets the plflib pages used a Core2 E8500 with GCC 5.1 (-O2 -march=native) and a Xeon E3-1241 with mingw GCC 9.2, so the numbers say nothing about libc++ or MSVC STL deques.
- Memory-sensitive code after a burst: popped-empty blocks stay allocated until you call trim(), shrink_to_fit() or clear().
- Code using stateful allocators: get_allocator() returns a default-constructed allocator_type() instead of the stored one.
- Generic code that relies on std::stack's adaptor surface (Container template parameter, the protected c member, construction from a container, operators &lt;, &lt;=, &gt;, &gt;=): only == and != are provided.

## How it is fast

Elements live in a doubly linked chain of memory blocks; when the top block fills, a new block sized to the current element count is allocated (so capacity roughly doubles) and nothing already stored is moved or copied, unlike a std::vector reallocation. pop() destroys the element (skipped for trivially destructible types), steps a cached top pointer back and keeps emptied blocks for reuse, so push/pop cycles across a block boundary do not hit the allocator; trim() releases them later. Compared with libstdc++'s std::deque, blocks are not capped at 512 bytes, which is why large element types (the README's 490-byte case) gain the most.

## Compared with alternatives

Pick it over veque, fast_vector or eastl::vector when the workload is strictly LIFO, elements are large or must not move, or references into the container must survive growth; those siblings are contiguous vectors that suit small trivially copyable types and need a contiguous buffer. Use plf::list or plf::colony instead when you need erase from the middle or iteration-heavy unordered storage; plf::stack only adds and removes at the top.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none outside the standard library; needs three files from the repo in one directory: plf_stack.h, plf_tools.h and plf_tools_undef.h (included at the end of plf_stack.h) |
| **Minimum toolchain** | C++98/03 (features such as move, emplace and allocator_traits switch on by compiler version, e.g. MSVC 2010+ for move semantics); C++20 adds a std::reverse_iterator overload |
| **Platforms** | any (portable C++, no intrinsics on the stack path) |
| **Thread safety** | not documented; no internal synchronisation, so treat it like a standard container (concurrent reads only). |
| **Drop-in for the baseline** | partial — push/emplace/pop/top/empty/size/swap match std::stack&lt;T&gt;, but the second template parameter is an allocator rather than an underlying container, there is no protected c member or container-taking constructor, only == and != comparisons exist, and emplace() returns void where C++17 std::stack::emplace returns a reference. |

## Gotchas

- Self copy-assignment (s = s, or a = \*p with p == &a) asserts in debug builds; in release builds operator=(const stack&) calls destroy_all_data() before copying from the now-empty source, so the stack silently ends up empty.
- get_allocator() returns allocator_type() rather than the allocator the stack holds, which is wrong for stateful allocators such as std::pmr::polymorphic_allocator and does not compile for allocators without a default constructor.
- top() is declared const but returns a mutable reference, and top()/pop() on an empty stack are only checked by assert (undefined behaviour in release, as with std::stack).
- The README's 'X% faster' figures are averages over 10 to 1,000,000 elements of construct, push all, read and pop all, destruct; the README does not say whether 82% means 1.82x throughput or 82% less time, and the 724% row reflects libstdc++'s 512-byte deque block limit rather than a general result.

## Known shortcomings

- README percentages only (plflib.org blocked, no benchmark code on GitHub); the 724% row reflects libstdc++ deque's 512-byte block limit.
- Enricher: self copy-assignment empties the stack in release builds and get_allocator() returns allocator_type() rather than the stored allocator; a snippet of the author's Haswell page shows std::vector beating plf::stack for char, contradicting the README's 'faster than all std:: containers'; setups per snippets are Core2 E8500 GCC 5.1 -O2 -march=native and Xeon E3-1241 mingw GCC 9.2; the harness is still not public (plflib.org blocked).

## Caveats and trade-offs

First-party numbers taken from the README only. The full benchmark page (plflib.org/stack.htm#benchmarks) is blocked by this environment's egress policy, so compiler, flags, CPU, OS and the per-size graphs could not be checked, and the README gives only averages. The repo holds plf_stack.h, plf_tools.h and plf_stack_test_suite.cpp (functional tests with no timing code); none of the author's GitHub repositories carries the benchmark harness, so the numbers cannot be reproduced from GitHub. Baseline is std::deque-backed std::stack only; the README's 'faster than all std:: containers in a stack context' for vector and list comes with no numbers on the page I could open. The 724% figure is for 490-byte elements, where the README itself says libstdc++'s deque degenerates into a linked list because of its 512-byte block limit, so that row reflects a libstdc++ weakness rather than a general result. Libc++ and MSVC STL results are not given in the README (a search snippet says the site also links MSVC graphs; not verified).

Header-only (plf_stack.h plus plf_tools.h), C++98/03/11/14 compatible, drop-in style replacement for std::stack. Elements live in chained memory groups (design described on plflib.org and in search-result text; that page was blocked), so there is no contiguous buffer to hand to C APIs, unlike a std::vector-backed stack.

## Maintenance

Actively maintained (v2.0.37, 103 commits, last commit 2026-10-03, three issues all closed) under the Zlib licence; copyable as three headers, but the benchmark harness lives only on plflib.org, so the speed claim stays first-party.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README (the benchmark_url) states first-party averaged results versus std::stack over std::deque (82%, 83%, 80%, 82% and 724% faster for 1-, 4-, 8-, 40- and 490-byte types) with no compiler, flags, CPU or benchmark code; the full benchmark page plflib.org/stack.htm returned EGRESS_BLOCKED and no mattreecebentley GitHub repository carries the benchmark harness, so the result cannot be checked beyond first-party numbers.
- **Verifier notes:** README numbers match the record exactly; metadata confirmed on github.com (79 stars, 7 forks, Zlib, not a fork, last commit 2026-10-03 'Add files via upload', so active). Tier stays C until someone with access to plflib.org/stack.htm checks compiler, flags, CPU and whether the benchmark code is downloadable there (the sibling plf_list and plf_bitsets entries reached A from plflib.org pages).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** first-party README (verifier); enricher code reading
- **Pages the verifier opened:**
  - <https://github.com/mattreecebentley/plf_stack>
  - <https://github.com/mattreecebentley/plf_stack/commits>
  - <https://raw.githubusercontent.com/mattreecebentley/plf_stack/HEAD/README.md>
  - <https://raw.githubusercontent.com/mattreecebentley/plf_stack/HEAD/plf_stack_test_suite.cpp>
  - <https://raw.githubusercontent.com/mattreecebentley/plf_stack/HEAD/LICENSE.md>
  - <https://github.com/mattreecebentley?tab=repositories>
- **Sources the enricher read:**
  - <https://github.com/mattreecebentley/plf_stack>
  - <https://github.com/mattreecebentley/plf_stack/commits>
  - <https://github.com/mattreecebentley/plf_stack/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/mattreecebentley/plf_stack/HEAD/README.md>
  - <https://raw.githubusercontent.com/mattreecebentley/plf_stack/HEAD/plf_stack.h>
  - <https://raw.githubusercontent.com/mattreecebentley/plf_stack/HEAD/plf_tools.h>
  - <https://raw.githubusercontent.com/mattreecebentley/plf_stack/HEAD/plf_tools_undef.h>
  - <https://raw.githubusercontent.com/mattreecebentley/plf_stack/HEAD/plf_stack_test_suite.cpp>
  - <https://raw.githubusercontent.com/mattreecebentley/plf_stack/HEAD/LICENSE.md>
  - https://plflib.org/stack.htm (EGRESS_BLOCKED; content known only from WebSearch snippets)
  - WebSearch snippets: https://plflib.org/stack_benchmarks_core2_gcc.htm and https://plflib.org/stack_benchmarks_haswell_gcc.htm
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/mattreecebentley/plf_stack`) · [data/wave1/enrich/raw/github_com_mattreecebentley_plf_stack.json](../../../data/wave1/enrich/raw/github_com_mattreecebentley_plf_stack.json) (enrichment confidence 0.65)

</details>
