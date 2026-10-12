# FastNoise2

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> C++17 SIMD node-graph noise library (Perlin, Simplex, Value, Cellular) that generates arrays 4-8x faster than scalar FastNoise Lite.

| | |
|---|---|
| **Beats** | FastNoise Lite (scalar C++), FastNoise legacy, libnoise, stb_perlin |
| **Claimed result** | 3D: Value 494.49 versus 64.13 (FastNoise Lite), Perlin 261.10 versus 47.93, Simplex 268.44 versus 36.83 (OpenSimplex in FastNoise Lite), Cellular 52.43 versus 12.49 million points/s; 2D: Value 776.33 versus 114.01, Perlin 624.27 versus 92.83, Simplex 466.03 versus 71.30, Cellular 194.30 versus 39.15. Ratios of roughly 4x to 8x (derived from page data). |
| **Workload** | Million noise points generated per second, 2D and 3D Value, Perlin, Simplex and Cellular noise, FastNoise2 AVX2 build against scalar noise libraries. |
| **Metric** | throughput |
| **Hardware** | Intel 7820X @ 4.9 GHz, Windows 10 x64, AVX2 build |
| **Compiler and flags** | clang-cl 10.0.0 -m64, RelWithDebInfo (/O2 /Ob1); FastNoise2 additionally /GS- /fp:fast with its AVX2 translation unit at -mavx2 -mfma; the comparison libraries built with no extra flags (strict FP, SSE2 baseline) |
| **Adoption** | 1.4k stars |
| **Last commit** | 2026-10-10 |
| **Links** | [repository](https://github.com/Auburn/FastNoise2) · [benchmark](https://github.com/Auburn/FastNoise2) |

## Verdict

On an Intel 7820X at 4.9 GHz under Windows 10 with clang-cl 10, the author's NoiseBenchmarking harness measured a September 2020 FastNoise2 snapshot (forced to AVX2, bulk GenUniformGrid) at 262-776 million points per second for 2D and 3D Value, Perlin and Simplex and 52-194 for Cellular, about 4.2x to 7.7x the per-point scalar FastNoise Lite (derived from page data). The FastNoise2 side was built with fast-math and FMA and the scalar side without, and the numbers predate the v1.0.0 API and kernel changes.

## Use it when

- Bulk generation of noise fields: terrain heightmaps, voxel chunks (e.g. 64^3 grids), 3D density fields, procedural textures, where you fill whole arrays per call.
- Layered noise (fractal FBm, domain warp, blends of several noise types) where fusing the whole graph in SIMD avoids extra memory passes.
- x86-64 with AVX2 or AVX-512, or ARM with NEON, when a scalar library such as FastNoise Lite, libnoise or stb_perlin is a bottleneck in world or texture generation.
- Teams that want artists or designers to tune noise in a visual Node Editor and ship the encoded string, with the same tree callable from C++, C#, Rust, Java or Unreal bindings.
- Multi-threaded chunk generation: generation methods are const and documented as thread-safe on a shared node tree.

## Skip it when

- Per-point sampling scattered through game logic (one value at a time): GenSingle\* underuses SIMD lanes; FastNoise Lite's header-only scalar API is simpler there.
- You need bit-identical output across CPUs or platforms without extra work: the default build uses fast-math and FMA on some feature sets, open issue #147 asks exactly this, and a 2026-10-10 fix (#189) removed AVX2 versus SSE2 differences of up to 0.133 in 4D Simplex domain warp; build with FASTNOISE2_STRICT_FP for exact matching.
- Projects that cannot fetch dependencies at configure time or want a single header: FastNoise2 is a compiled CMake library that pulls FastSIMD through CPM, and the standalone build also builds the Node Editor by default.
- Building with plain MSVC on Windows: the README says MSVC has SIMD compiler bugs that cause incorrect generation and recommends clang-cl.
- You rely on the 2020 benchmark numbers for current code: v1.0.0 (January 2026) changed the generation API and several kernels, and no comparison table has been published for it.

## How it is fast

Each node is compiled once per SIMD feature set (scalar, SSE2, SSE4.1, AVX2, AVX-512, NEON, WASM SIMD) through the author's FastSIMD abstraction and dispatched at runtime to the best one the CPU supports. The whole node tree is evaluated per SIMD batch, so intermediate values of combined noises stay in registers instead of being written to separate arrays and recombined in scalar passes (the README's 'Why Nodes?' argument). The default build also enables fast-math (-ffast-math or /fp:fast) on the SIMD kernels unless FASTNOISE2_STRICT_FP is set.

## Compared with alternatives

Pick FastNoise2 over SIMDNoise (rust-simd-noise) when you work in C++ and want a node graph with fused fractal, warp and blend operations plus AVX-512, NEON and WASM paths; pick it over writing noise kernels yourself with ISPC, EVE or the Vector Class Library when standard Perlin, Simplex, Value or Cellular noise is all you need.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | FastSIMD (downloaded by CPM at configure time, pinned to commit 16450dae); the optional Node Editor pulls further GUI dependencies |
| **Minimum toolchain** | C++17, CMake 3.10; clang-cl recommended over MSVC on Windows; GCC and Clang supported (exact minimum compiler versions not documented) |
| **Platforms** | x86 32/64-bit (scalar, SSE2, SSE4.1, AVX2, AVX-512 selected at runtime), ARM (NEON on armv7a and aarch64), WASM SIMD; Windows, Linux, macOS x86/ARM, Android, iOS, Emscripten |
| **Thread safety** | Generation methods are const and documented as fully thread-safe; one node tree can be shared across threads (Generator.h). Setting node parameters while other threads generate is not documented. |
| **Drop-in for the baseline** | partial — same noise families as FastNoise Lite, but a different interface (node objects plus bulk array generation instead of GetNoise(x, y[, z])); frequency is now expressed through step size and per-node feature size, so outputs are not identical to FastNoise Lite |

## Gotchas

- Harness flaw (asymmetric build flags): at the pinned 2020 commit e191bc2 FastNoise2's own CMake compiled its library with /GS- /fp:fast (the if(MSVC) branch also fires for clang-cl) and its AVX2 file with -mavx2 -mfma, while the FastNoise Lite, FastNoise legacy, libnoise and stb_perlin benchmark DLLs got no extra flags (strict FP, SSE2 baseline). The README's 'clang-cl 10.0.0 -m64 /O2' line does not describe this, and the harness's only release configuration in CMakeSettings.json is RelWithDebInfo (/O2 /Ob1).
- The comparison is not like-for-like in API or noise type: FastNoise2 fills a 512x512 or 64^3 float array via GenUniformGrid (frequency 0.02), while each scalar library is called once per point through GetNoise inside benchmark::DoNotOptimize (FastNoise Lite at its default frequency). The FastNoise Lite adapter has no Simplex case, so both its 2D 'Simplex' and 3D '\*OpenSimplex' numbers are OpenSimplex2 runs; against the like-for-like FastNoise legacy Simplex the 3D ratio is 6.0x (derived from page data). The author's own SIMD predecessor FastNoiseSIMD is built and run by the harness but left out of the README table.
- The README table cannot be reproduced against current code: the harness calls GenUniformGrid2D(out, int xStart, int yStart, xSize, ySize, float frequency, seed) and FastSIMD::Level_AVX2, while v1.0.0 changed GenUniformGrid to (out, float xOffset, ..., int xCount, ..., float xStepSize, ..., seed) and moved to FastSIMD FeatureSet; Google Benchmark runs once per case (Repetitions commented out) and no raw output is committed.
- Recent correctness fixes change output: #191 (2026-10-09) fixed CellularDistance Euclidean returning sqrt(F2) when both distance indices are equal and NaN at distance 0 with zero jitter; #190 applies the domain-warp seed offset once; #189 fixed 4D Simplex domain warp differing between feature sets. The default cellular configuration used in the benchmark is not affected by #191.

## Known shortcomings

- The author's NoiseBenchmarking harness pins FastNoise2 at e191bc2 (Sept 2020) and compares bulk SIMD grid generation with per-point scalar calls; the 3D Simplex column pits FN2 Simplex against FastNoise Lite OpenSimplex2 (like-for-like vs FastNoise legacy Simplex is 6.0x derived); FastNoiseSIMD is built but left out of the table; harness release config is RelWithDebInfo.
- Enricher: asymmetric build flags at the pinned 2020 commit e191bc2: FastNoise2's own CMake compiled its library with /GS- /fp:fast (the if(MSVC) branch also fires under clang-cl) and its AVX2 file with -mavx2 -mfma while the FastNoise Lite, legacy, libnoise and stb_perlin benchmark DLLs got no extra flags (strict FP, SSE2 baseline); the harness's only release configuration is RelWithDebInfo (/O2 /Ob1), one run per case with repetitions commented out and no raw output; the harness cannot build against v1.x (GenUniformGrid signature changed), so the 2020 table cannot be reproduced against current code; the FastNoise Lite adapter has no Simplex case, so its 2D and 3D Simplex rows are both OpenSimplex2. Retiered to C.

## Caveats and trade-offs

Benchmark harness is the author's own Auburn/NoiseBenchmarking repo (6 stars, 14 commits, last commit 2020-09-15; no results file checked in) and pins the FastNoise2 submodule at commit e191bc2 from September 2020, so the README table describes a six-year-old version of the library, not current master (which keeps receiving correctness fixes, e.g. CellularDistance double sqrt fixed 2026-10-09). The comparison is FastNoise2's bulk GenUniformGrid2D/3D into an array (AVX2 level forced) against per-point GetNoise calls wrapped in benchmark::DoNotOptimize for FastNoise Lite and the other scalar libraries, so the gain mixes SIMD and API-shape effects. The 3D 'Simplex' column compares FastNoise2's Simplex node with FastNoise Lite's OpenSimplex2 (marked with an asterisk); against the like-for-like FastNoise legacy Simplex (44.74) the 3D ratio is 6.0x (derived from page data). The author's earlier SIMD library FastNoiseSIMD is built by the harness but omitted from the README table, so no SIMD competitor is shown. Frequencies differ (0.02 for FastNoise2, FastNoise Lite default for the others). Old compiler (clang-cl 10) on Windows, single machine. The continuous-benchmark page on auburn.github.io was not reachable here. [retier] Asymmetric flags (/fp:fast and AVX2+FMA only on the FastNoise2 side); single run per case; harness pinned to the 2020 API and not buildable against v1.x; FastNoise Lite adapter has no Simplex case so both its Simplex rows are OpenSimplex2; not like-for-like in API or noise type

Node-graph API aimed at generating arrays of noise with fused SIMD pipelines (the README argues scalar combination of separately generated arrays defeats SIMD); several SIMD feature sets are supported; a 2026-10-10 commit fixed 4D Simplex domain-warp output differing between SIMD feature sets, so outputs can vary slightly across instruction sets; not the same noise function as FastNoise Lite in every column (Simplex versus OpenSimplex).

## Maintenance

Actively maintained (v1.1.1 in February 2026, correctness fixes through 2026-10-10), MIT-licensed, with C#, Rust, Java and Unreal bindings; the published library comparison has not been rerun since 2020.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now C.
- **Tier reason:** README 'Library Comparisons' tables match every claimed number (FastNoise Lite, FastNoise legacy, libnoise, stb perlin rows) and state CPU (Intel 7820X @ 4.9 GHz), compiler (clang-cl 10.0.0) and flags (-m64 /O2); the harness is public in Auburn/NoiseBenchmarking (main.cpp, FastNoise2/Benchmark_FastNoise2.cpp, FastNoiseLite/Benchmark_FastNoiseLite.cpp, Google Benchmark submodule).
- **Retiered** A to C: Enricher (2026-10-12): asymmetric build flags behind the published table. At the pinned 2020 commit e191bc2 FastNoise2 was compiled with /fp:fast (and its AVX2 file with -mavx2 -mfma) while the FastNoise Lite, FastNoise legacy, libnoise and stb_perlin benchmark DLLs received no extra flags (strict FP, SSE2 baseline); the README's 'clang-cl 10.0.0 -m64 /O2' line does not describe this, the only release configuration is RelWithDebInfo, one run per case, and the harness cannot build against current FastNoise2 v1.x. Crippled-baseline precedent, numbers kept.
- **Verifier notes:** Numbers and ratios (about 4.2x to 7.7x) verified on the README; tier A holds because the harness code, compiler, flags and CPU are all public, but the table is from a 2020 FastNoise2 snapshot and the Simplex column is not like-for-like against FastNoise Lite. Record shortcomings: stale 2020 numbers, bulk SIMD API vs per-point scalar API, OpenSimplex2 vs Simplex mismatch, first-party harness.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-10 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/Auburn/FastNoise2>
  - <https://github.com/Auburn/FastNoise2/commits>
  - <https://raw.githubusercontent.com/Auburn/FastNoise2/HEAD/README.md>
  - <https://github.com/Auburn/NoiseBenchmarking>
  - <https://github.com/Auburn/NoiseBenchmarking/commits/master>
  - <https://github.com/Auburn/NoiseBenchmarking/tree/master/FastNoise2>
  - <https://raw.githubusercontent.com/Auburn/NoiseBenchmarking/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Auburn/NoiseBenchmarking/HEAD/CMakeSettings.json>
  - <https://raw.githubusercontent.com/Auburn/NoiseBenchmarking/HEAD/main.cpp>
  - <https://raw.githubusercontent.com/Auburn/NoiseBenchmarking/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/Auburn/NoiseBenchmarking/HEAD/FastNoise2/Benchmark_FastNoise2.cpp>
  - <https://raw.githubusercontent.com/Auburn/NoiseBenchmarking/HEAD/FastNoise2/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Auburn/NoiseBenchmarking/HEAD/FastNoiseLite/Benchmark_FastNoiseLite.cpp>
- **Sources the enricher read:**
  - <https://github.com/Auburn/FastNoise2>
  - <https://raw.githubusercontent.com/Auburn/FastNoise2/HEAD/README.md>
  - <https://raw.githubusercontent.com/Auburn/FastNoise2/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Auburn/FastNoise2/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Auburn/FastNoise2/HEAD/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Auburn/FastNoise2/HEAD/include/FastNoise/FastNoise.h>
  - <https://raw.githubusercontent.com/Auburn/FastNoise2/HEAD/include/FastNoise/Generators/Generator.h>
  - <https://raw.githubusercontent.com/Auburn/FastNoise2/HEAD/cmake/CPM.cmake>
  - <https://raw.githubusercontent.com/Auburn/FastNoise2/e191bc2c7c93bd6bd5c0db5b0c30d241172fbbb6/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Auburn/FastNoise2/e191bc2c7c93bd6bd5c0db5b0c30d241172fbbb6/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Auburn/FastNoise2/e191bc2c7c93bd6bd5c0db5b0c30d241172fbbb6/README.md>
  - <https://raw.githubusercontent.com/Auburn/FastNoise2/e191bc2c7c93bd6bd5c0db5b0c30d241172fbbb6/include/FastNoise/Generators/Generator.h>
  - <https://raw.githubusercontent.com/Auburn/FastNoise2/e191bc2c7c93bd6bd5c0db5b0c30d241172fbbb6/include/FastSIMD/FastSIMD.h>
  - <https://github.com/Auburn/FastNoise2/commits>
  - <https://github.com/Auburn/FastNoise2/releases>
  - <https://github.com/Auburn/FastNoise2/issues?q=is%3Aissue+is%3Aopen>
  - <https://github.com/Auburn/FastNoise2/pull/191>
  - <https://github.com/Auburn/FastNoise2/pull/189>
  - <https://github.com/Auburn/FastNoise2/wiki>
  - <https://github.com/Auburn/FastNoise2/wiki/Including-the-library-in-your-project>
  - <https://raw.githubusercontent.com/Auburn/FastSIMD/16450dae9528727e500e7254f635a671f9c7ee2d/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Auburn/FastSIMD/16450dae9528727e500e7254f635a671f9c7ee2d/README.md>
  - <https://github.com/Auburn/NoiseBenchmarking>
  - <https://github.com/Auburn/NoiseBenchmarking/tree/master/FastNoise2>
  - <https://raw.githubusercontent.com/Auburn/NoiseBenchmarking/HEAD/README.md>
  - <https://raw.githubusercontent.com/Auburn/NoiseBenchmarking/HEAD/main.cpp>
  - <https://raw.githubusercontent.com/Auburn/NoiseBenchmarking/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Auburn/NoiseBenchmarking/HEAD/CMakeSettings.json>
  - <https://raw.githubusercontent.com/Auburn/NoiseBenchmarking/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/Auburn/NoiseBenchmarking/HEAD/FastNoise2/Benchmark_FastNoise2.cpp>
  - <https://raw.githubusercontent.com/Auburn/NoiseBenchmarking/HEAD/FastNoise2/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Auburn/NoiseBenchmarking/HEAD/FastNoiseLite/Benchmark_FastNoiseLite.cpp>
  - <https://raw.githubusercontent.com/Auburn/NoiseBenchmarking/HEAD/FastNoiseLite/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Auburn/NoiseBenchmarking/HEAD/FastNoise/Benchmark_FastNoise.cpp>
  - <https://raw.githubusercontent.com/Auburn/NoiseBenchmarking/HEAD/FastNoiseSIMD/Benchmark_FastNoiseSIMD.cpp>
  - <https://raw.githubusercontent.com/Auburn/NoiseBenchmarking/HEAD/FastNoiseSIMD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Auburn/NoiseBenchmarking/HEAD/NoiseBenchmarkInterface/NoiseBenchmarkInterface.h>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/auburn/fastnoise2`) · [data/wave13/enrich/raw/github_com_auburn_fastnoise2.json](../../../data/wave13/enrich/raw/github_com_auburn_fastnoise2.json) (enrichment confidence 0.8)

</details>
