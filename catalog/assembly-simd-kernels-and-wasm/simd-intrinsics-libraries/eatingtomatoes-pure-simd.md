# Pure SIMD (pure_simd)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSD-3-Clause` · 🔴 abandoned

> Header-only C++17 vector template that unrolls element-wise operators at compile time for compiler auto-vectorization; beat a scalar shader loop 9.4x.

| | |
|---|---|
| **Beats** | scalar_shader, the same per-pixel shader written as a plain scalar C++ loop in the repo's benchmark directory |
| **Claimed result** | Scalar 103 ms vs pure_simd width 64 10.9 ms (about 9.4x, derived from page data); width 32 12.5 ms, width 16 16.2 ms, width 8 28.0 ms; width 128 regresses to 158 ms (slower than scalar). |
| **Workload** | Per-pixel integer shader over a 512x512 int screen buffer (99 iterations of multiply and modulo-by-constant integer arithmetic per pixel), pure_simd_shader instantiated with vector sizes 1 to 128, against the same loop written in plain scalar C++. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-9750H, Ubuntu 18.04 |
| **Compiler and flags** | clang++ 9.0 -O3 -march=native |
| **Adoption** | 233 stars |
| **Last commit** | 2021-10-04 |
| **Links** | [repository](https://github.com/eatingtomatoes/pure_simd) · [benchmark](https://github.com/eatingtomatoes/pure_simd) |

## Verdict

On an Intel Core i7-9750H under Ubuntu 18.04 with clang++ 9.0 -O3 -march=native (Google Benchmark 1.5.0, mean of 10 repetitions via scripts/benchmark.sh), a 512x512 integer shader with a 99-step serial chain per pixel took 103 ms as the author's plain scalar loop and 10.9 ms with pure_simd width 64 (about 9.4x, derived from page data); width 8 took 28.0 ms and width 128 regressed to 158 ms. The baseline is the author's own latency-bound scalar loop that the compiler did not vectorize, not a standard-library routine or another SIMD library, and the test checks every width's output against it.

## Use it when

- Loops whose iterations are independent but whose body is a long serial dependency chain (per-pixel shaders, per-element iterative integer or float math), where the compiler will not vectorize the outer loop by itself.
- Element-wise transforms over int, float or double arrays built with clang or gcc at -O3 -march=native, when you want portable source with no intrinsics and are willing to read the generated assembly.
- Small projects that can vendor one 643-line BSD-3-Clause header and need nothing beyond C++17.
- Tuning vector width as an unroll knob: widths 8 to 64 helped in the README shader (28.0 ms down to 10.9 ms) while 128 hurt.

## Skip it when

- Reductions and horizontal tests (sum, all-ones or all-zeros checks): in issue #9 gcc 10 did not vectorize them and clang's output loaded data with scalar 4-byte moves; the maintainer recommended intrinsics for that pattern.
- Small element types such as uint8 byte streams: the maintainer reported only slight gains over 128-bit intrinsics on an ASCII validation test (issue #6).
- When you need predictable codegen or rich SIMD features (masks, shuffles, gathers, vector math functions): results depend on the compiler and the chosen width (the maintainer found clang 9 sensitive to vector size and gcc 7.5 not), so an intrinsics-backed library is safer.
- MSVC or any compiler without strong SLP vectorization; the README lists 'C++17 & SLP vectorization' as the requirement and names only gcc and clang.
- Production code that needs a stable API: the README calls the library experimental with drastically changing interfaces, and there have been no commits since 2021-10-04.

## How it is fast

There are no intrinsics: each operator expands into N independent scalar operations through index_sequence pack expansion, and the compiler's SLP (superword-level parallelism) vectorizer is expected to fuse them into SIMD instructions. Even without fusion, the expansion interleaves N independent dependency chains, which is effectively manual outer-loop vectorization of the pixel loop; clang does not do this for the plain scalar loop, whose 99-step serial chain per pixel leaves it latency-bound. The maintainer later wrote in issue #6 (2020-05-23) that clang's IR for the new shader example was not vectorized at all and that he 'didn't expect simple code expansion to make such a big difference', so part or all of the gain may be instruction-level parallelism rather than SIMD.

## Compared with alternatives

Pick it over EVE or the Vector Class Library only when you want a tiny intrinsic-free header that coaxes gcc or clang into vectorizing or interleaving an existing scalar loop and you will inspect the assembly; for guaranteed SIMD codegen, reductions, byte-level work or vector math functions EVE and VCL are safer, and ISPC is the mature tool for the same one-lane-per-pixel shader pattern.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for include/pure_simd.hpp; Conan with Google Benchmark 1.5.0 and GoogleTest 1.10.0 for the tests and benchmarks |
| **Minimum toolchain** | C++17 with an SLP-vectorizing compiler (gcc or clang); published numbers used clang++ 9.0 with -O3 -march=native |
| **Platforms** | any target in principle (standard C++, no intrinsics; native_vectorsize reads __AVX512\*__/__AVX__ to guess register width), but example/shader.cpp, and so the benchmark and test binaries, includes &lt;x86intrin.h&gt; and builds only on x86 |
| **Thread safety** | not documented; vectors are plain value types and the header has no global state |
| **Drop-in for the baseline** | no |

## Gotchas

- The README attributes the shader speedup to SIMD, but after the 2020-05-17 rewrite that produced the README table the maintainer reported (issue #6, 2020-05-23) that clang did not vectorize the new shader example at all. The README's width-64 time is about 0.42 ns per pixel-iteration against 3.97 ns scalar (derived from page data: 512 x 512 x 99 iterations), and no IR or assembly is published, so it is unclear which build the table came from; check your own compiler's output before relying on it.
- Harness defect in the second example: example/sum.hpp pure_simd_add_bits uses VECTOR_SIZE 16, but scatter_bits of one uint8_t fills only lanes 0-7 while the loop advances one source byte per 16 targets, so it reads half the bit stream, never updates lanes 8-15 and computes a different result from scalar_add_bits; its unit test (n = 8) loads and stores 16 ints from an 8-int array, an out-of-bounds access that passes by accident. For int targets the sum benchmark's factors (1/100, 1/10000, 1/1000000) also cast to 0. The sum benchmark has no published numbers, so the catalogued shader claim is unaffected.
- The shader workload relies on signed 32-bit overflow (px\*py terms exceed INT_MAX), which is undefined behaviour in both the scalar and the vector version; the repo's equality test passing shows only that the author's build happened to agree. The example also indexes rows by SCRHEIGHT instead of SCRWIDTH, harmless only because the buffer is square.
- The header includes only &lt;climits&gt;, &lt;functional&gt; and &lt;cmath&gt; yet uses std::max on an initializer list, std::clamp, std::transform, std::array, std::index_sequence and std::reverse_iterator, so it depends on transitive includes; include &lt;algorithm&gt;, &lt;array&gt;, &lt;utility&gt; and &lt;iterator&gt; first. accumulate and inner_product return a per-lane vector, not a scalar (reduce with sum), and gather_bits was broken on clang until the final commit (issue #9, fixed 2021-10-04).

## Known shortcomings

- One toy shader against the author's own scalar loop, with signed-int overflow UB in both versions (outputs match in the repo test); size 128 is slower (158 ms); not compared with any other SIMD library; abandoned since 2021-10-04.
- Enricher: the README credits SIMD for the shader 9.4x, but the maintainer wrote in issue #6 (2020-05-23, after the 2020-05-17 rewrite that produced the table) that clang 'did not vectorize the new shader example at all' and credited 'simple code expansion'; no IR or assembly published; example/sum.hpp pure_simd_add_bits uses VECTOR_SIZE 16 while scatter_bits fills 8 lanes (half the bit stream read, result differs from scalar) and its unit test loads and stores 16 ints out of bounds on an 8-int array (sum benchmark unpublished); gcc 10 does not vectorise the reductions (issue #9).

## Caveats and trade-offs

A single toy workload (one shader adapted from the 'Practical SIMD Programming' tutorial) on one laptop CPU; the scalar baseline is the author's own loop with the same flags. Its inner loop is a serial 99-step dependency chain per pixel, so the gain comes from the compiler SLP-vectorizing the unrolled independent pixels, while the scalar loop as written evidently was not vectorized (it ties vector size 1 at 103 ms) and size 128 is 1.5x slower (158 ms). The shader relies on signed 32-bit overflow (px\*py terms exceed INT_MAX), which is undefined behaviour in both versions; outputs match in the repo's test. The second benchmark (benchmark/sum.cpp) has no published results. Numbers are aggregate means of 10 repetitions. No comparison with Highway, xsimd, Eigen or std::simd; the README calls the library experimental with unstable interfaces.

No intrinsics: variadic-template unrolled vector types that rely on the compiler's SLP vectorizer (gcc or clang needed). Vector width must be tuned (too wide hurts the instruction cache). Header-only C++17; Conan is needed to build the tests and benchmarks.

## Maintenance

Abandoned since 2021-10-04 (41 commits, all three issues closed, README says experimental), but BSD-3-Clause and a single 643-line header, so it is easy to vendor as a pattern; its benefit depends on the compiler, so verify codegen on yours.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** README benchmark output matches every claimed time (scalar 103 ms; sizes 8/16/32/64 at 28.0/16.2/12.5/10.9 ms; 128 at 158 ms) and states clang++ 9.0, -O3 -march=native, Core i7-9750H; the benchmark code is public (benchmark/shader.cpp with example/shader.cpp, CMakeLists.txt sets -O3 -march=native) and test/shader.cpp checks every vector size against the scalar output.
- **Verifier notes:** Numbers verified; tier A holds on public benchmark code, compiler, flags and CPU, and the test confirms equal outputs. Shortcomings: one toy shader, author-written scalar baseline, signed-overflow UB in the workload, no comparison against other SIMD libraries, abandoned since 2021-10-04.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-10 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/eatingtomatoes/pure_simd>
  - <https://github.com/eatingtomatoes/pure_simd/commits/master>
  - <https://raw.githubusercontent.com/eatingtomatoes/pure_simd/HEAD/README.md>
  - <https://raw.githubusercontent.com/eatingtomatoes/pure_simd/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/eatingtomatoes/pure_simd/HEAD/benchmark/shader.cpp>
  - <https://raw.githubusercontent.com/eatingtomatoes/pure_simd/HEAD/benchmark/sum.cpp>
  - <https://raw.githubusercontent.com/eatingtomatoes/pure_simd/HEAD/example/shader.cpp>
  - <https://raw.githubusercontent.com/eatingtomatoes/pure_simd/HEAD/example/shader.hpp>
  - <https://raw.githubusercontent.com/eatingtomatoes/pure_simd/HEAD/test/shader.cpp>
- **Sources the enricher read:**
  - <https://github.com/eatingtomatoes/pure_simd>
  - <https://github.com/eatingtomatoes/pure_simd/commits/master>
  - <https://github.com/eatingtomatoes/pure_simd/commits/master/README.md>
  - <https://github.com/eatingtomatoes/pure_simd/commits/master/example/shader.cpp>
  - <https://github.com/eatingtomatoes/pure_simd/issues?q=is%3Aissue>
  - <https://github.com/eatingtomatoes/pure_simd/issues/4>
  - <https://github.com/eatingtomatoes/pure_simd/issues/6>
  - <https://github.com/eatingtomatoes/pure_simd/issues/9>
  - <https://github.com/eatingtomatoes/pure_simd/tree/master/scripts>
  - <https://raw.githubusercontent.com/eatingtomatoes/pure_simd/HEAD/README.md>
  - <https://raw.githubusercontent.com/eatingtomatoes/pure_simd/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/eatingtomatoes/pure_simd/HEAD/conanfile.txt>
  - <https://raw.githubusercontent.com/eatingtomatoes/pure_simd/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/eatingtomatoes/pure_simd/HEAD/include/pure_simd.hpp>
  - <https://raw.githubusercontent.com/eatingtomatoes/pure_simd/HEAD/example/shader.cpp>
  - <https://raw.githubusercontent.com/eatingtomatoes/pure_simd/HEAD/example/shader.hpp>
  - <https://raw.githubusercontent.com/eatingtomatoes/pure_simd/HEAD/example/sum.hpp>
  - <https://raw.githubusercontent.com/eatingtomatoes/pure_simd/HEAD/benchmark/main.cpp>
  - <https://raw.githubusercontent.com/eatingtomatoes/pure_simd/HEAD/benchmark/shader.cpp>
  - <https://raw.githubusercontent.com/eatingtomatoes/pure_simd/HEAD/benchmark/sum.cpp>
  - <https://raw.githubusercontent.com/eatingtomatoes/pure_simd/HEAD/test/shader.cpp>
  - <https://raw.githubusercontent.com/eatingtomatoes/pure_simd/HEAD/test/sum.cpp>
  - <https://raw.githubusercontent.com/eatingtomatoes/pure_simd/HEAD/test/vector.cpp>
  - <https://raw.githubusercontent.com/eatingtomatoes/pure_simd/HEAD/scripts/benchmark.sh>
  - <https://raw.githubusercontent.com/eatingtomatoes/pure_simd/HEAD/scripts/benchmark_shader.sh>
  - <https://raw.githubusercontent.com/eatingtomatoes/pure_simd/HEAD/scripts/config.sh>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/eatingtomatoes/pure_simd`) · [data/wave13/enrich/raw/github_com_eatingtomatoes_pure_simd.json](../../../data/wave13/enrich/raw/github_com_eatingtomatoes_pure_simd.json) (enrichment confidence 0.75)

</details>
