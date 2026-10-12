# Yomm2

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Smart pointers and reference counting](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `BSL-1.0` · 🔴 abandoned

> Archived C++17 open multi-methods library; plain dispatch is slower than virtual calls, and its 5x virtual_ptr win is a cache-layout artifact.

| | |
|---|---|
| **Beats** | C++ virtual member function call (closed dispatch via vtable) |
| **Claimed result** | Only the virtual_ptr rows beat the baseline. In docs/benchmarks/v010500.euclid.clang.md (clang 16.0.6, release build, 100 hierarchies of 1000 objects, run 2024-04-26), arity 1 with an ordinary base: virtual function 60.1, direct virtual ptr 10.5 (ratio 0.18), indirect virtual ptr 12.2 (0.20). Arity 2 with an ordinary base: virtual function 93.2, direct virtual ptr 19.4 (0.21), indirect 20.5 (0.22). That is about 5x lower time per call (derived from page data); the page gives no time unit. With virtual inheritance, the virtual_ptr rows are about 2.1x slower than the virtual function (arity 1: direct 156.9 vs 74.3; arity 2: 231.9 vs 107.3). Every other open-method row is slower than the virtual function: ratios 1.09-1.62 with an ordinary base and 2.05-2.47 with a virtual base. The Performance section of ORIGINAL-README.md says that dispatching a method with one virtual argument takes 15-30% more time than the equivalent virtual member function, and that virtual_ptr makes dispatch 'even faster - three instructions and two memory reads'. |
| **Workload** | Google Benchmark loop picking a random hierarchy out of 100, then a random object (or two for arity 2) out of 1000 per hierarchy with randomized allocation sizes, and calling one virtual function or the equivalent open method; ordinary-inheritance and virtual-inheritance variants. |
| **Metric** | latency (average time per dispatched call, unit not stated on the page) |
| **Hardware** | host 'euclid', '16 X 3300 MHZ CPUs' (CPU model not stated; cache sizes printed with implausible units: L1 Data 32768 KiB x2, L2 524288 KiB x2, L3 4194304 KiB x8) |
| **Compiler and flags** | clang 16.0.6, build type release (CMake Release; exact flags not stated in the result file) |
| **Adoption** | 382 stars; packaged in Conan Center and vcpkg |
| **Last commit** | 2026-02-01 |
| **Links** | [repository](https://github.com/jll63/yomm2) · [benchmark](https://raw.githubusercontent.com/jll63/yomm2/HEAD/docs/benchmarks/v010500.euclid.clang.md) |

## Verdict

The author's Google Benchmark run (clang 16.0.6, release build, unnamed 16-thread 3.3 GHz host, 100 hierarchies x 1000 objects, 2024-04-26) gives, after subtracting a no-dispatch baseline, 60.1 ns per arity-1 virtual call versus 65.4-97.2 ns for reference-based open methods and 10.5-12.2 ns for virtual_ptr (arity 2: 93.2 versus 108.0-143.0 and 19.4-20.5). The virtual_ptr gap reflects that its rows never touch the randomly placed objects; with virtual inheritance all open-method rows are 2.05-2.47x slower, and the successor's own docs claim only that reference dispatch is 30-50% slower and virtual_ptr dispatch is as short as a virtual call.

## Use it when

- You need dispatch on two or more runtime types (collision handling, binary operations on a matrix hierarchy): the arity-2 open method measured 1.16-1.53x the time of a hand-written double virtual dispatch, without the Visitor boilerplate.
- You must add operations (to_json, render, serialize) to class hierarchies you cannot or do not want to modify, i.e. the Expression Problem.
- Code that can carry virtual_ptr through its call chains, so the type-hash lookup is paid once per object rather than once per call.
- An existing YOMM2 codebase that cannot move to Boost 1.90 yet and needs a BSL-1.0, header-only, C++17 dependency that keeps working.

## Skip it when

- As a speed-up over virtual member functions: dispatch through a plain reference measured 1.09-1.62x slower (ordinary base), and the \~5x faster virtual_ptr rows come from a benchmark layout effect, not cheaper dispatch.
- Hierarchies that use virtual inheritance: every open-method path, virtual_ptr included, measured 2.05-2.47x slower than the virtual function because the overrider needs a dynamic cast.
- New projects: the repository was archived on 2026-03-04 and replaced by Boost.OpenMethod (Boost 1.90), which is not source-compatible (macros, namespaces and initialize() renamed).
- Plugin-heavy programs where you cannot control when update() runs: the tables must be rebuilt after every dlopen/dlclose, and calls before update() are invalid.
- Footprint-sensitive builds: the runtime adds about 75 KB (64 KB stripped) and pulls in Boost Mp11, Preprocessor and DynamicBitset headers.

## How it is fast

Each registered class gets a method table; a call finds it through a fast perfect hash of the object's type_info pointer (one multiply, one shift, one load), then loads the method's slot and jumps, with no branches or loops (9 instructions and 7 memory reads per the author's disassembly, versus 2 and 2 for a virtual call). Multiple dispatch indexes a multi-dimensional table with per-method strides. virtual_ptr does the hash lookup once when the fat pointer is built, so a later dispatch is a slot load plus an indirect jump (3 instructions); intrusive policies store the vptr inside the object instead.

## Compared with alternatives

The siblings (woid, Delegate, stdext::inplace_function, SmallFunction) are faster std::function replacements for storing one callable; YOMM2 solves a different problem, selecting an implementation from the runtime types of one or more arguments. Pick it only when you need open or multiple dispatch over class hierarchies, and prefer its successor Boost.OpenMethod for new code.

## Integration

| | |
|---|---|
| **Form** | header-only (default); optional shared library for the runtime via -DYOMM2_SHARED=1 |
| **Dependencies** | Boost headers (Mp11, Preprocessor, DynamicBitset); Boost.Test and Google Benchmark only for tests and benchmarks; Boost unordered_flat_map optional for one benchmark policy |
| **Minimum toolchain** | C++17, CMake 3.21 for the CMake build; packaged in vcpkg and Conan Center. The benchmark program refuses to run under g++ (GCC bug 85282) and was only run with clang 16.0.6. |
| **Platforms** | Any C++17 platform with RTTI (dispatch hashes type_info pointers); not documented further |
| **Thread safety** | Not documented. Dispatch only reads global tables built by update(); update() is a global rebuild with no documented locking, so it should not run concurrently with method calls. |
| **Drop-in for the baseline** | no |

## Gotchas

- Benchmark harness flaw behind the headline: in tests/benchmarks.cpp the virtual_ptr rows copy a precomputed 16-byte fat pointer from a contiguous vector and call an empty overrider, so the object itself is never read in the timed loop; the virtual-function row must load the C++ vptr from one of 100,000 randomly drawn heap objects, so it pays the cache miss. The same table shows this: with virtual inheritance, where converting the virtual_ptr to the virtual base and casting in the overrider touch the object, virtual_ptr becomes 2.1x slower than the virtual function.
- The page's 'avg' column is Google Benchmark mean CPU time in nanoseconds (the default unit; no Unit() is set) minus a no-dispatch 'baseline' run, per dev/bmutils.py, so absolute values are net of the harness overhead (derived from harness code). The odd cache sizes ('L1 Data 32768 KiB') come from bmutils.py printing Google Benchmark's byte counts with a KiB label; the real sizes are 32 KiB L1d, 512 KiB L2 and 4 MiB L3.
- docs/articles/performance.md says object allocation sizes are randomized, but at HEAD the alloc_dist distribution in tests/benchmarks.cpp is declared and never used; objects are scattered only by allocating them round-robin across 100 randomly chosen populations.
- A call with no applicable or an ambiguous overrider goes to the error handler and then abort(); issue #36 reports that defining the same overrider twice compiles and crashes at call time (closed without a fix shown).

## Known shortcomings

- Ordinary open-method dispatch is 1.09-2.47x slower than virtual functions in the project's own benchmark; the only win (virtual_ptr 0.18-0.22x) is a layout effect (contiguous fat-pointer vector vs random heap object dereference) and virtual_ptr is 2.1x slower with virtual inheritance; no CPU model. Archived 2026-03-04, superseded by Boost.OpenMethod (Boost 1.90). No spec category fits (the baseline is a language feature); filed with the fat-pointer and delegate libraries under smart-pointers-and-refcount.
- Enricher: in tests/benchmarks.cpp the virtual_ptr rows copy prebuilt fat pointers from a contiguous vector and call empty overriders that never read the object, while the virtual-function row loads the vptr from one of 100,000 random heap objects and pays the cache miss, so the 5x win is a layout artifact (with a virtual base, where the object is touched, virtual_ptr turns 2.1x slower); avg is the Google Benchmark mean minus a no-dispatch baseline; cache sizes are byte counts printed as KiB; alloc_dist is never used; issue #36 (duplicate overrider crashes at call time). Downgraded C to D. Lead: Boost.OpenMethod docs claim no speed-up (reference dispatch 30-50% slower).

## Caveats and trade-offs

Weak evidence of 'faster'. The repo was archived on 2026-03-04 and is superseded by Boost.OpenMethod (Boost 1.90). The current README is a retirement notice saying YOMM2 'was' a library, and the original documentation now lives in ORIGINAL-README.md. The author's own text there says open methods are almost as fast as virtual functions and take 15-30% more time with plain references. The benchmark page shows ratios of 1.09-1.62 for every non-virtual_ptr row with an ordinary base (for example, arity 1: basic policy 80.4 vs virtual function 60.1), and 2.05-2.47 with a virtual base. The 0.18-0.22 ratios for virtual_ptr come from a layout effect in tests/benchmarks.cpp. The virtual_ptr rows copy a fat pointer, which already carries the vtable pointer, out of a contiguous vector (population::vptr_draw / ivptr_draw; the vectors are built during allocation, outside the timed loop). The virtual-function row dereferences a randomly chosen heap object (population::draw returns \*objects[dist(rnd)]), so cache misses on the object dominate the baseline. In real code that touches the object, the gap would shrink. With virtual inheritance, virtual_ptr dispatch is about 2.1x slower than the virtual function. The result file gives no time unit, no compiler flags and no CPU model; its cache sizes are printed with implausible units (L1 Data 32768 KiB). The benchmark source excludes g++ ('Don't benchmark g++ until this is fixed', GCC bug 85282). The 'much faster than other implementations' claim in docs/articles/performance.md has no numbers. First-party measurement, so tier C. [retier] Project's own tests/benchmarks.cpp (Google Benchmark, no CPU model): ordinary open-method dispatch is 1.09-2.47x slower than virtual functions. The only faster rows (virtual_ptr 0.18-0.22x) copy prebuilt fat pointers from a contiguous vector and call empty overriders that never read the object, while the virtual-function row loads the vptr from one of 100,000 random heap objects and pays the cache miss; with a virtual base, where the object must be touched, virtual_ptr turns 2.1x slower. avg is the Google Benchmark mean minus a no-dispatch baseline (dev/bmutils.py); the odd cache sizes are byte counts printed as KiB; alloc_dist is declared but never used. Issue #36 (duplicate overrider crashes at call time). Archived 2026-03-04, superseded by Boost.OpenMethod (Boost 1.90), whose docs claim no speed-up over virtual functions. No spec category fits; filed with the fat-pointer and delegate libraries under smart-pointers-and-refcount.

Open (non-intrusive) multi-methods for C++17 with multiple dispatch on several arguments, which virtual functions cannot do; needs class registration and a runtime update() call that builds dispatch tables (about 75K runtime). Plain-reference dispatch costs 9 instructions and 7 memory reads vs 2 and 2 for a virtual call; virtual_ptr is a fat pointer (extra pointer size) that carries the vptr. Dispatch through virtual bases needs a dynamic cast and is 2-5x slower than virtual functions.

## Maintenance

Archived on 2026-03-04 and superseded by Boost.OpenMethod in Boost 1.90; BSL-1.0 and header-only so it can still be vendored, but it will get no fixes and the virtual_ptr speed claim should not be relied on.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** The benchmark code is public (tests/benchmarks.cpp, Google Benchmark) and the result page names clang 16.0.6 with a release build. But no compiler flags are printed and no CPU model is given (only '16 X 3300 MHZ CPUs'), so it is not A. With first-party numbers only, it is C.
- **Retiered** C to D: Downgraded C to D: the only faster rows (virtual_ptr 0.18-0.22x) come from a harness in which virtual_ptr copies prebuilt fat pointers from a contiguous vector into empty overriders that never read the object while the virtual-function row dereferences random heap objects, so the win is a cache-layout artifact (AssemblyScript and Blosc precedent); ordinary dispatch is 1.09-2.47x slower than virtual functions.
- **Verifier notes:** The numbers match the page, the metadata checks out (BSL-1.0, 382 stars, last commit 2026-02-01, archived 2026-03-04, so abandoned) and the record's caveats hold up against tests/benchmarks.cpp. The only fix: the 15-30% slower statement is in ORIGINAL-README.md, not README.md. Shortcomings to record: ordinary dispatch is 1.09-2.47x slower than virtual functions; the roughly 5x virtual_ptr win is a benchmark layout effect (a contiguous fat-pointer vector vs randomly drawn heap objects); virtual_ptr is 2.1x slower with virtual inheritance; no CPU model; archived and superseded by Boost.OpenMethod (Boost 1.90, a possible lead). Category: 'polymorphic-dispatch' is not a spec category, and none fits exactly, since the baseline is a language feature rather than a std facility. The closest is wave 1 smart-pointers-and-refcount, which already holds std::function/dispatch replacements (woid, Delegate, inplace_function) and fits virtual_ptr as a fat-pointer type.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`
- **Shortcomings recorded by:** first-party benchmark (verifier, not faster); enricher harness reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/jll63/yomm2/HEAD/docs/benchmarks/v010500.euclid.clang.md>
  - <https://raw.githubusercontent.com/jll63/yomm2/HEAD/README.md>
  - <https://raw.githubusercontent.com/jll63/yomm2/HEAD/ORIGINAL-README.md>
  - <https://raw.githubusercontent.com/jll63/yomm2/HEAD/tests/benchmarks.cpp>
  - <https://raw.githubusercontent.com/jll63/yomm2/HEAD/LICENSE>
  - <https://github.com/jll63/yomm2>
  - <https://github.com/jll63/yomm2/commits>
- **Sources the enricher read:**
  - <https://github.com/jll63/yomm2>
  - <https://github.com/jll63/yomm2/issues?q=is%3Aissue>
  - <https://github.com/jll63/yomm2/issues/36>
  - <https://raw.githubusercontent.com/jll63/yomm2/HEAD/README.md>
  - <https://raw.githubusercontent.com/jll63/yomm2/HEAD/ORIGINAL-README.md>
  - <https://raw.githubusercontent.com/jll63/yomm2/HEAD/docs/benchmarks/v010500.euclid.clang.md>
  - <https://raw.githubusercontent.com/jll63/yomm2/HEAD/docs/articles/performance.md>
  - <https://raw.githubusercontent.com/jll63/yomm2/HEAD/tests/benchmarks.cpp>
  - <https://raw.githubusercontent.com/jll63/yomm2/HEAD/tests/benchmarks_parameters.hpp>
  - <https://raw.githubusercontent.com/jll63/yomm2/HEAD/dev/bm2md>
  - <https://raw.githubusercontent.com/jll63/yomm2/HEAD/dev/bmutils.py>
  - <https://raw.githubusercontent.com/jll63/yomm2/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jll63/yomm2/HEAD/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jll63/yomm2/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/jll63/yomm2/HEAD/include/yorel/yomm2/core.hpp>
  - <https://raw.githubusercontent.com/jll63/yomm2/HEAD/include/yorel/yomm2/policy.hpp>
  - <https://github.com/boostorg/openmethod>
  - <https://raw.githubusercontent.com/boostorg/openmethod/develop/doc/modules/ROOT/pages/performance.adoc>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/jll63/yomm2`) · [data/wave1/enrich/raw/github_com_jll63_yomm2.json](../../../data/wave1/enrich/raw/github_com_jll63_yomm2.json) (enrichment confidence 0.8)

</details>
