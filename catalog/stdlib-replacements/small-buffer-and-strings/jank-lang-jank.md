# jank persistent_string

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Small-buffer containers and strings](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MPL-2.0` · 🟢 active

> jank's built-in immutable string (jtl::immutable_string, backing persistent_string); claims to tie or beat std::string and folly::fbstring.

| | |
|---|---|
| **Beats** | std::string |
| **Claimed result** | Blog text, per chart: 'jank constructs small strings the fastest and ties with std::string for large strings'; 'ties with folly for copying small strings and seriously beats both when copying large strings'; 'ties with std::string for large and small string searches'; 'ties with folly for small substrings and seriously beats both when creating large substrings'. Overall it 'either ties or outperforms the fastest in every benchmark'. The page states no numeric values; results appear only as SVG bar charts. |
| **Workload** | nanobench microbenchmarks with a small ('foo') and a large (128-char) string: construction, copy-construction, find, and substr. They compare jank's persistent_string with libstdc++ std::string and folly::fbstring. The gist also has equality-comparison benchmarks, but the blog does not chart them. |
| **Metric** | latency |
| **Adoption** | 3.3k stars |
| **Last commit** | 2026-09-21 |
| **Links** | [repository](https://github.com/jank-lang/jank) · [benchmark](https://jank-lang.org/blog/2023-12-30-fast-string/) |

## Verdict

The jank blog runs nanobench microbenchmarks (construction, copy, find, substr, at 'foo'-sized and 128-char sizes) comparing jank's persistent_string against libstdc++ std::string and folly::fbstring, claiming jank ties or wins every chart (notably beating both on large-string copy and large substr). The page states no numeric axis values and no compiler, flags, or hardware; the underlying gist baseline is std::basic_string with jank's own GC allocator, not std::allocator.

## Use it when

- You're already building on jank's Clojure-on-LLVM runtime, where this is the string type used throughout the compiler and generated code.
- Workloads dominated by copying or substring-ing large (24+ byte) strings, where GC-backed sharing can avoid the copy std::string/fbstring would perform.
- Short strings (&lt;=23 bytes) where SSO avoids allocation entirely, similar in spirit to libstdc++/folly SSO.
- Read-mostly immutable string data where repeated hashing matters, since the hash is cached on first computation.
- Single-process native code already managed by a garbage collector, not code that must interoperate with plain std::string APIs.

## Skip it when

- You need a standalone C++ string library: this type only builds/links inside jank's compiler+runtime tree and depends on jank's object/oref system, jtl utilities, and Boehm GC.
- You need in-place mutation (append, resize, element write outside construction) — there is no mutator API; jank uses a separate string_builder for building strings incrementally.
- You need audited numbers: the benchmark page publishes only unlabeled SVG bar charts, no ns values, and states no compiler, flags, or CPU, so the real-world magnitude of any win is unverified (evidence tier D).
- You're sensitive to buffer lifetime: substring sharing keeps the parent large buffer alive via the GC until it's dropped or c_str() forces an owned copy, which can extend memory retention versus a copying string.
- You need a stable, versioned API: jank is alpha-stage language tooling, so this type's shape can change with the language rather than being maintained as an independent, stable library.

## How it is fast

It follows folly::fbstring's three-word (24-byte on 64-bit) layout: a tagged union of an inline small-string buffer and a {pointer,size,flags} large-string struct, discriminated by 2 bits in the last byte, giving small-string optimization for strings up to 23 bytes with zero heap allocation. Large strings are either 'owned' (allocated with GC_malloc_atomic, so the Boehm GC doesn't scan their bytes) or 'shared': copy-construction and substr() of large strings just flip a category flag and reuse the source buffer with no refcounting, relying on jank's GC to keep the memory alive, unless the substring discards more than 512 bytes relative to the source, in which case it deep-copies instead of pinning a large buffer alive. The hash is cached inside the object's otherwise-unused word, so repeated hashing (e.g., as a map key) after the first call is O(1).

## Compared with alternatives

Only pick it if you're already targeting jank itself; for a standalone C++ project, buffet or FastString (both catalogued with page-stated numeric std::string construction/append speedups) are closer to drop-in replacements, and to_static_string covers the numeric-to-string conversion niche persistent_string doesn't address.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | jank's runtime object/oref system, jtl utility library (immutable_string_view, string_builder), Boehm GC (GC_malloc_atomic/GC_free) — not usable in isolation |
| **Minimum toolchain** | C++20 (compiler+runtime/CMakeLists.txt sets cxx_std_20) |
| **Platforms** | Linux (ubuntu-24.04) and macOS (macos-26) built in CI (.github/workflows/build-compiler+runtime.yml); a separate Windows workflow file exists in the repo but its status was not checked this session |
| **Thread safety** | not documented. Copy construction and substr() mutate the \*source\* string's category flag via const_cast (to mark it large_shared) without any visible synchronization, so concurrently copying/substringing the same large string from multiple threads looks unsafe absent external locking; no thread-safety guarantee is stated in source or docs |
| **Drop-in for the baseline** | false — a GC-backed, immutable-only runtime object embedded in jank's compiler+runtime, not a header you can swap in for std::string in an arbitrary C++ project |

## Gotchas

- c_str() lazily converts a shared large string into an owned copy (allocation + memcpy) the first time it's called; data()/size() do not force this and are not guaranteed null-terminated for shared strings.
- Copy-constructing a large string mutates the source object's internal flag byte (const_cast) to mark both sides 'shared' — surprising side effect on a type documented as immutable.
- substr() cost is not uniform: small results or results within 512 bytes of the source size share the buffer (cheap), but discarding more than 512 bytes triggers a full deep copy.
- The small-string threshold is 23 bytes on a 64-bit machine (24-byte storage minus 1 flag byte); crossing it switches the code path from inline copy to GC allocation.

## Caveats and trade-offs

The page states no exact numbers (bar charts only). Compiler, flags, and CPU are not stated. libc++ is mentioned but not benchmarked. In the gist, the std::string baseline is std::basic_string&lt;char, std::char_traits&lt;char&gt;, native_allocator&lt;char&gt;&gt; (jank's GC allocator), not std::allocator. persistent_string lives inside the jank compiler, not in a standalone library. The record is kept at Tier D only because the project is notable (3.3k stars).

persistent_string is an immutable, reference-counted/shared string tied to jank's own runtime and GC model (copy-on-substring semantics, writes only in constructors); it is not a standalone drop-in std::string replacement usable outside jank's runtime without adopting that model.

## Maintenance

Actively maintained (last commit 2026-09-21), MPL-2.0, 'copyable' usability but only as part of jank's own compiler+runtime source tree — the project itself is alpha-stage language tooling, not a standalone, independently versioned string library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now D.
- **Tier reason:** The blog compares against libstdc++ std::string and folly::fbstring only in SVG bar charts. The charts have ns axes but no stated values, and the text has no numbers. Compiler, flags, and hardware are all unstated. The harness is public in a gist. The project is notable (3,333 stars), so the record is kept at D.
- **Verifier notes:** The qualitative claim is verified verbatim. The SVG files contain only axis ticks and legends, no bar value labels. Approximate values could be read from the bar geometry, but I did not use them. Metadata checks out: MPL-2.0, 3,333 stars, last commit 2026-09-21.
- **Fields the verifier corrected:** `baseline_stdlib`, `workload`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://jank-lang.org/blog/2023-12-30-fast-string/>
  - <https://jank-lang.org/img/blog/2023-12-30-fast-string/allocations.plot.svg>
  - <https://jank-lang.org/img/blog/2023-12-30-fast-string/copy.plot.svg>
  - <https://jank-lang.org/img/blog/2023-12-30-fast-string/find.plot.svg>
  - <https://jank-lang.org/img/blog/2023-12-30-fast-string/substr.plot.svg>
  - <https://gist.github.com/jeaye/306d6aefd7ed6c29fdec6eef2cafbb1f>
  - <https://github.com/jank-lang/jank>
- **Sources the enricher read:**
  - <https://github.com/jank-lang/jank>
  - <https://jank-lang.org/blog/2023-12-30-fast-string/>
  - <https://github.com/jank-lang/jank/blob/main/README.md>
  - <https://github.com/jank-lang/jank/blob/HEAD/compiler+runtime/include/cpp/jank/runtime/obj/persistent_string.hpp>
  - <https://github.com/jank-lang/jank/blob/HEAD/compiler+runtime/src/cpp/jank/runtime/obj/persistent_string.cpp>
  - <https://github.com/jank-lang/jank/blob/HEAD/compiler+runtime/include/cpp/jtl/immutable_string.hpp>
  - <https://github.com/jank-lang/jank/blob/HEAD/compiler+runtime/CMakeLists.txt>
  - <https://github.com/jank-lang/jank/blob/HEAD/.github/workflows/build-compiler+runtime.yml>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/jank-lang/jank`) · [data/wave1/enrich/raw/github_com_jank_lang_jank.json](../../../data/wave1/enrich/raw/github_com_jank_lang_jank.json) (enrichment confidence 0.35)

</details>
