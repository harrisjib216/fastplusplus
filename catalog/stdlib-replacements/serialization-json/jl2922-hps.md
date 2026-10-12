# HPS (High Performance Serialization)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [JSON serialization](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Header-only C++11 serializer for STL/user types; faster and smaller than Boost.Serialization, no schema needed.

| | |
|---|---|
| **Beats** | Boost.Serialization |
| **Claimed result** | Up to 150% faster and up to 40% fewer bytes than Boost Serialization for several common data structures (verbatim README / arXiv abstract; 150% faster = \~2.5x, derived from page data). README serialize+parse time chart shows HPS 0.1.0 faster than Boost 1.66.0 on double array, sparse matrix and hash map; Cap'n Proto 0.6.1 is faster than HPS on sparse matrix, roughly tied on double array, and has no hash-map result (so 'beats Cap'n Proto in all cases except sparse matrix' overstates it). |
| **Workload** | Serializing common STL containers and user-defined types (including a sparse matrix), compared against Boost Serialization, Protocol Buffers, and Cap'n Proto |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E5-2620 v4 |
| **Compiler and flags** | GCC 7.2 -O3 on CentOS 7.2 (README chart subtitle); benchmark.mk uses -std=c++11 -O3 |
| **Adoption** | 93 stars |
| **Last commit** | 2022-01-17 |
| **Links** | [repository](https://github.com/jl2922/hps) · [benchmark](https://github.com/jl2922/hps) |

## Verdict

On GCC 7.2 -O3 (CentOS 7.2, Intel Xeon E5-2620 v4), HPS's own first-party benchmark (src/benchmark, run via benchmark.mk/ci.sh) times full serialize+parse round-trips against Boost 1.66.0, Protobuf 3.5.1, and Cap'n Proto 0.6.1 on a double array, sparse matrix, and string-to-double hash map; the README charts show HPS beating Boost on all three (up to \~2.5x, i.e. '150% faster', and up to 40% smaller output on several cases), while Cap'n Proto is faster than HPS specifically on the sparse-matrix case.

## Use it when

- Serializing STL containers (vector, map, unordered_map, set, deque, list, pair, unique_ptr, string, array) or composed user types within one C++ codebase/toolchain
- Want a smaller, faster wire format than Boost.Serialization without adopting an IDL or build-time codegen step (Protobuf/Cap'n Proto)
- OK vendoring a small header-only C++11 library with no runtime shared-lib dependency
- Numeric-heavy workloads (large arrays of primitives) similar to the library's own stated use case (quantum-chemistry data checkpointing)
- Internal format where both reader and writer compile from the same C++ headers, so no cross-language schema is needed

## Skip it when

- Need cross-language interop or generated bindings (Python/Java/Go) -- there is no .proto/.capnp equivalent
- Need zero-copy / read-without-parsing access into the buffer -- HPS parses into an object like Boost does; Cap'n Proto's own README-cited benchmark beats HPS specifically on the sparse-matrix case
- Need forward/backward wire compatibility as fields are added or removed -- there are no field tags, so there is no story for schema evolution (unlike Protobuf's optional fields)
- Project has been unmaintained since last commit 2022-01-17 with no recent validation against current compilers/Boost/Protobuf/Cap'n Proto versions
- Care about stream-based reads specifically: an unresolved open issue (#49) reports an abort() in StreamInputBuffer::load on a size mismatch, with no maintainer response

## How it is fast

Signed integers are zigzag-encoded and routed through a varint-style unsigned-integer serializer (confirmed in src/basic_type/int_serializer.h), the same base idea Protobuf uses. The key difference from Protobuf is that HPS emits no field numbers or wire-type tags at all -- layout comes entirely from the C++ type at compile time (per-README) -- which cuts both encoded size and per-field dispatch overhead. It also skips the reflection/schema layer and message-builder allocation model that Cap'n Proto and Boost.Serialization pay for.

## Compared with alternatives

Among the catalogued siblings, Cap'n Proto and zpp::bits are the closest (also binary serialization, not JSON-text parsers like the rest). Pick HPS over them when you're already on Boost.Serialization and want a smaller/faster same-shape replacement without adopting an IDL, schema compiler, or zero-copy buffer model -- but Cap'n Proto's own benchmark beats HPS on nested/sparse-matrix data and gives you cross-language schemas plus zero-copy reads that HPS doesn't offer.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none at runtime (STL only); googletest is a test-only submodule, not a runtime dependency |
| **Minimum toolchain** | C++11 (CI matrix tested GCC 5/6/7 and Clang 4.0/5.0 on Ubuntu Trusty via .travis.yml) |
| **Platforms** | not documented beyond Linux CI; no architecture-specific code observed in the serializers read (no SIMD/intrinsics) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial -- explain: same job (binary serialize/parse of STL + user types) as Boost.Serialization, but a different call surface (free functions hps::to_string/from_string/to_stream/from_stream vs Boost's archive objects and BOOST_SERIALIZATION_\* macros); user types need new serialize()/parse() methods rather than Boost's serialize(Archive&, unsigned version) |

## Gotchas

- Open, unresolved issue #49: a third-party project hit abort() in StreamInputBuffer::load on a read-position/file-size mismatch (oldpos 524288 vs size 589548); no fix visible in the thread
- No field numbers or wire types in the encoding -- reading with a mismatched type layout is undefined, unlike Protobuf's tag-based tolerance
- unordered_map/unordered_set serialize in iteration order, which is not guaranteed stable across runs or STL implementations
- Repo dormant since Jan 2022; last verified against 2017-era GCC 5-7 / Clang 4-5, so building with a modern compiler is unverified

## Caveats and trade-offs

First-party benchmark from the author's arXiv preprint (1811.04556, not peer reviewed), run in 2018 against Boost 1.66.0, protobuf 3.5.1 and Cap'n Proto 0.6.1, so standings versus current versions are unknown. Results are shown only as bar charts, not tables. Cap'n Proto beats HPS on sparse-matrix time.

No IDL/schema like Protobuf or Cap'n Proto (works directly on STL/user types via templates), so less cross-language tooling; unmaintained for years, may need patching to build with modern compilers

## Maintenance

Abandoned: last commit 2022-01-17 and CI last green against 2017-era GCC 5-7/Clang 4-5 on Travis; MIT-licensed, header-only, and small enough to vendor and re-verify against a current compiler yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded C-&gt;A: the README benchmark charts (src/benchmark/time.png, size.png) state 'Intel Xeon E5-2620 v4 with GCC 7.2 -O3 and CentOS 7.2', and the benchmark code is public (src/benchmark/double_array_test.cc, sparse_matrix_test.cc, map_test.cc, built via benchmark.mk with -std=c++11 -O3), directly timing Boost 1.66.0 serialization.
- **Verifier notes:** Tier upgraded because the compiler, flags and CPU are printed in the README chart images, which the search agent missed. The Cap'n Proto clause was overstated and has been corrected. Metadata checks out: MIT, 93 stars, last commit 2022-01-17, abandoned.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/jl2922/hps>
  - <https://github.com/jl2922/hps/tree/master/src/benchmark>
  - <https://github.com/jl2922/hps/blob/master/src/benchmark/double_array_test.cc>
  - <https://github.com/jl2922/hps/blob/master/benchmark.mk>
  - <https://github.com/jl2922/hps/blob/master/ci.sh>
  - <https://raw.githubusercontent.com/jl2922/hps/master/src/benchmark/time.png>
  - <https://raw.githubusercontent.com/jl2922/hps/master/src/benchmark/size.png>
  - <https://arxiv.org/abs/1811.04556>
- **Sources the enricher read:**
  - <https://github.com/jl2922/hps>
  - <https://github.com/jl2922/hps#readme>
  - <https://github.com/jl2922/hps/tree/master/src/benchmark>
  - <https://github.com/jl2922/hps/blob/master/src/hps.h>
  - <https://github.com/jl2922/hps/blob/master/benchmark.mk>
  - <https://github.com/jl2922/hps/blob/master/ci.sh>
  - <https://github.com/jl2922/hps/blob/master/LICENSE>
  - <https://github.com/jl2922/hps/blob/master/.travis.yml>
  - <https://github.com/jl2922/hps/blob/master/src/benchmark/double_array_test.cc>
  - <https://github.com/jl2922/hps/blob/master/src/basic_type/int_serializer.h>
  - <https://github.com/jl2922/hps/issues>
  - <https://github.com/jl2922/hps/issues/50>
  - <https://github.com/jl2922/hps/issues/49>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/jl2922/hps`) · [data/wave1/enrich/raw/github_com_jl2922_hps.json](../../../data/wave1/enrich/raw/github_com_jl2922_hps.json) (enrichment confidence 0.65)

</details>
