# Klein

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Math, SIMD and linear algebra](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Header-only SSE library for 3D projective geometric algebra; its llvm-mca listings show about half GLM's estimated cycles for quaternion and dual-quaternion work.

| | |
|---|---|
| **Beats** | GLM (glm::quat multiplication; glm::dualquat converted with mat3x4_cast and applied to a glm::vec4), with RTM (Realtime Math) as a second reference |
| **Claimed result** | docs/perf.md llvm-mca totals per 100 iterations: rotor composition Klein 821 cycles / 2400 instructions vs GLM 1522 cycles / 5700 instructions (1.85x fewer cycles, derived from page data) vs RTM 824 cycles / 2300 instructions (parity); block reciprocal throughput 8.0 vs GLM 14.0 vs RTM 7.0. Motor application to a point: Klein 1831 cycles / 5900 instructions vs GLM dual-quat 5435 cycles / 14100 instructions (2.97x fewer cycles, derived from page data); block reciprocal throughput 13.5 vs 38.5. docs/index.md: 'Klein's performance is fully competitive with state of the art kinematic and math libraries built with traditional vector and quaternion formulations.' |
| **Workload** | Static llvm-mca analysis (100 iterations, dispatch width 6, Skylake model) of the compiled SSE assembly for two routines marked with mc_ruler MC_MEASURE regions in perf/klein_perf.cpp, perf/glm_perf.cpp and perf/rtm_perf.cpp: rotor (quaternion) composition and motor (dual-quaternion) application to a point; no run time is measured. |
| **Metric** | other |
| **Hardware** | No run-time hardware: llvm-mca static analysis with the Intel Skylake scheduling model (SKLPort0-7 resources, dispatch width 6) for every listing. |
| **Compiler and flags** | Not stated on the page. perf/CMakeLists.txt builds the analysed regions with mc_ruler (an llvm-mca harness that needs clang; version not stated) only in a Release build; the klein target adds -msse3; glm_perf.cpp uses GLM 0.9.9.7 (fetched by tag) with no GLM_FORCE_INTRINSICS or other GLM SIMD define and no -msse flag; RTM is fetched at origin/master. |
| **Adoption** | 802 stars; repository archived on 2024-08-02 |
| **Last commit** | 2024-08-02 |
| **Links** | [repository](https://github.com/jeremyong/klein) · [benchmark](https://github.com/jeremyong/klein/blob/master/docs/perf.md) |

## Verdict

No run time was measured. docs/perf.md gives llvm-mca static estimates (Intel Skylake scheduling model, 100 iterations, dispatch width 6) for code regions marked with mc_ruler; the compiler is clang through mc_ruler, version unstated. Rotor composition: Klein 821 estimated cycles vs scalar GLM 0.9.9.7 quat\*quat at 1522 (1.85x, derived from page data) and RTM at 824 (parity). Motor-point application: Klein 1831 vs 5435 (2.97x, derived from page data), but the GLM routine normalizes, builds a 3x4 matrix and applies its transpose without translation. perf/rtm_perf.cpp has an RTM qvv point-transform routine whose result is not published.

## Use it when

- Skinning, animation or kinematic-chain code on x86 that composes many rigid transforms and applies them to points, using float32 motors (8 floats) in place of 4x4 matrices.
- Geometry code that needs points, lines and planes in one system: intersecting planes into lines, joining points into lines and planes, projecting, and measuring distances and angles without special-case formulas.
- Interpolating rigid-body motion with the motor logarithm and line exponentiation that the library provides.
- Transforming large packed arrays of points, planes or lines by one motor with the array call operator.
- Targets guaranteed to have SSE3, or SSE4.1 for the dpps path via the klein_sse42 target, where single precision is enough.

## Skip it when

- Pure quaternion composition: RTM's quat_mul is at parity in the project's own listing (824 vs 821 estimated cycles, block reciprocal throughput 7.0 vs 8.0), and RTM is maintained.
- ARM, Apple Silicon or WebAssembly: these work only through the optional SIMDe shim (KLEIN_USE_SIMDE), none of the published analysis covers them, and Emscripten issue #28 is open.
- Double precision, general-dimension algebras or a general multivector type: every type is float32 in __m128 registers, limited to the entity list in the docs.
- Projects that need a maintained dependency: the repo was archived on 2024-08-02, and issue #30 (line\*line geometric product gpLL builds a motor around the wrong axis because e23 and e12 are swapped) was filed a week earlier with a patch and never merged.
- Code that needs exactly normalized results: normalize(), invert() and point::normalize() use rcpps or rsqrtps plus one Newton step (about 22 bits per the source comments).

## How it is fast

Klein supports only one algebra in one dimension, so every product was worked out by hand. The non-zero terms of each geometric product and sandwich (conjugation) are packed into blocks of four floats, one __m128 register each, and computed with shufps, mulps and addps. A rotor uses one register and a motor uses two. Motor-point application (sw312) evaluates m p \~m directly, without building a matrix. Normalization and inversion use rcpps and rsqrtps with one Newton-Raphson step instead of division and sqrt. Array overloads such as motor::operator()(point\* in, point\* out, size_t count) reuse the motor-derived terms across a packed batch.

## Compared with alternatives

Pick Klein over xsimd when you want ready-made rotor, motor, point, line and plane operations on SSE rather than portable SIMD primitives for writing your own kernels. No other catalogued sibling covers rigid-body transforms. Pick xsimd, or a general tensor library such as Axiom, for wider-than-128-bit SIMD, ARM or double precision.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the core headers (copy public/ and include &lt;klein/klein.hpp&gt;); SIMDe only for the optional non-x86 shim |
| **Minimum toolchain** | C++11 (a C++11 fallback .inl replaces the C++17 'if constexpr' paths; the klein_sse42 target sets C++17); README tests GCC 9.2.1, Clang 9.0.1, Visual Studio 2019 and Xcode 11.3; needs -msse3, or -msse4.1 with KLEIN_SSE_4_1 |
| **Platforms** | x86/x86-64 with SSE3 (SSE4.1 optional); other architectures only through the SIMDe shim, untested in the published analysis |
| **Thread safety** | not documented; the headers read hold only __m128 value members and no shared mutable state |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw in the GLM motor row of docs/perf.md (5435 vs 1831 cycles). The routine is glm::mat3x4_cast(a) \* b with b a glm::vec4. GLM 0.9.9.7 has no mat3x4 \* vec4 operator, and GLM_EXPLICIT is empty unless GLM_FORCE_EXPLICIT_CTOR is set, so b silently converts to a vec3. Because mat3x4_cast stores the rows of [R|t] as the matrix's columns, the line computes R^T p with no translation and puts t.p in w. That is not the rigid transform Klein computes; the correct call is b \* mat3x4_cast(a). The listing confirms it: only 0, 4 and 8(%rsi) of the point are loaded. The GLM routine also normalizes the dual quaternion on every call (x.real / length2(x.real), 4 divss with 11-cycle latency), which Klein's m(p) skips because it assumes a normalized motor. So the about 3x gap compares a normalize-and-build-matrix routine that computes a different result against a direct sandwich.
- The verifier's caveat that GLM ran without its SIMD path matters less than it sounds for rotor composition. In GLM 0.9.9.7 the SIMD compute_quat_mul in detail/type_quat_simd.inl is commented out, so quat\*quat is scalar even with GLM_FORCE_INTRINSICS. The scalar listing (5700 instructions per 100 iterations) is representative of that GLM version. Five of its 57 instructions are a stack round-trip from returning a 16-byte struct in two XMM registers under the SysV ABI.
- Types are 16-byte-aligned __m128 wrappers. point::store() uses the aligned _mm_store_ps on a plain float\* while load() is unaligned. The memory layout is (w, x, y, z) with the homogeneous coordinate first, not GLM's (x, y, z, w). Containers of Klein types before C++17 need aligned allocation.
- CMake add_subdirectory always FetchContent-populates SIMDe v0.7.2 from GitHub at configure time, even with KLEIN_ENABLE_SIMDE off; copying public/ avoids this. The standalone perf build clones RTM over an SSH URL (git@github.com) at origin/master, and on non-Windows it takes any installed GLM through find_package before the pinned 0.9.9.7, so a rebuild of the analysis may use different baselines.

## Known shortcomings

- Evidence is llvm-mca static cycle estimates (Skylake model), not measured run time; the GLM baseline is scalar (0.9.9.7, no GLM_FORCE_INTRINSICS) and the GLM motor row includes a per-call mat3x4_cast; ties RTM. Archived 2024-08-02.
- Enricher: the GLM motor row (5435 vs 1831) computes glm::mat3x4_cast(a) \* b with a vec4 b that GLM 0.9.9.7 silently converts to vec3, giving R^T p with no translation (the correct call is b \* mat3x4_cast(a)), and the GLM routine normalizes on every call (4 divss) while Klein's m(p) assumes a normalized motor, so the \~3x gap compares different computations. GLM 0.9.9.7's SIMD quaternion multiply is commented out, so the scalar rotor row is representative. The RTM qvv routine in perf/rtm_perf.cpp has no published result. Open bug #30 (gpLL e23/e12 swap, patch never merged); normalize uses approximate rcp/rsqrt (about 22 bits); point layout (w,x,y,z) with aligned stores; CMake always fetches simde v0.7.2. No independent run-time benchmark exists (ga-benchmark excludes Klein).

## Caveats and trade-offs

The only numbers are first-party llvm-mca cycle estimates; docs/perf.md itself says llvm-mca 'cannot be used as a proxy for predicting performance'. No run-time measurements are published: perf/ is the mc_ruler harness that produces these llvm-mca reports, not a timing benchmark. The GLM baseline is scalar: glm_perf.cpp defines no GLM_FORCE_INTRINSICS (GLM 0.9.9.7) and gets no -msse flag, and its listings are movss-based with stack spills, so GLM's own SIMD path was not used. The GLM motor routine converts the dual quaternion with glm::mat3x4_cast on every call, which inflates its count against Klein's direct motor-point application. Against RTM, the best SIMD baseline, rotor composition is a tie (821 vs 824 cycles), and no RTM motor routine is given. Compiler version unstated (mc_ruler requires clang). The project site jeremyong.com/klein is blocked here; the docs were read from the repo's docs/ folder. Repo archived on 2024-08-02 with the README saying it was paused for lack of time. [retier] Evidence is llvm-mca static cycle estimates (Skylake model), not measured run time, from docs/perf.md. The GLM baseline is scalar (0.9.9.7, no GLM_FORCE_INTRINSICS; its SIMD quaternion multiply is commented out, so the rotor row is representative). The GLM motor row (5435 vs 1831 cycles) computes glm::mat3x4_cast(a) \* b with a vec4 b that GLM silently converts to vec3, yielding R^T p with no translation (the correct call is b \* mat3x4_cast(a)), and the GLM routine normalizes on every call while Klein's m(p) assumes a normalized motor, so the \~3x motor gap compares different computations; the listing also loads only 3 floats of the point. Ties RTM; the RTM qvv routine in perf/rtm_perf.cpp has no published result. Normalize uses approximate rcp/rsqrt (about 22 bits); open bug #30 (gpLL e23/e12 swap, patch never merged). No independent run-time benchmark (ga-benchmark excludes Klein). Archived 2024-08-02.

Specialised to 3D projective geometric algebra P(R\*_{3,0,1}) with SSE (SSE3 required, SSE4.1 optional) rather than a general vector library; SSE intrinsics only in this version (README requires an SSE3 processor). Points, lines, planes, rotors and motors share one algebra, so motors replace separate quaternion and dual-quaternion code.

## Maintenance

Archived since 2024-08-02 (the author calls it temporary) with line-product bug #30 unfixed. MIT-licensed, header-only and dependency-free, so it is small enough to vendor and patch for SSE x86 targets.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** docs/perf.md gives only first-party llvm-mca static estimates (Skylake scheduling model) for two routines against GLM and RTM; the harness (perf/\*_perf.cpp via mc_ruler) is public but compiler version and run-time measurements are absent, and the page itself says llvm-mca cannot predict performance, so C (numbers without measured methodology), not A or B.
- **Verifier notes:** Numbers match docs/perf.md exactly (rotor 821/2400 vs GLM 1522/5700 vs RTM 824/2300; motor 1831/5900 vs GLM 5435/14100; block RThroughput 8.0/14.0/7.0 and 13.5/38.5). Shortcomings to record: static llvm-mca estimates only, no measured run time; GLM baseline built without its SIMD path; GLM motor row includes a mat3x4_cast per call; ties RTM; archived.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Shortcomings recorded by:** first-party docs/perf.md (verifier); enricher code reading
- **Pages the verifier opened:**
  - <https://github.com/jeremyong/klein>
  - <https://github.com/jeremyong/klein/commits/master>
  - <https://github.com/jeremyong/klein/tree/master/perf>
  - <https://raw.githubusercontent.com/jeremyong/klein/master/docs/perf.md>
  - <https://raw.githubusercontent.com/jeremyong/klein/master/README.md>
  - <https://raw.githubusercontent.com/jeremyong/klein/master/LICENSE>
  - <https://raw.githubusercontent.com/jeremyong/klein/master/docs/index.md>
  - <https://raw.githubusercontent.com/jeremyong/klein/master/perf/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jeremyong/klein/master/perf/glm_perf.cpp>
  - <https://raw.githubusercontent.com/jeremyong/klein/master/perf/klein_perf.cpp>
  - <https://raw.githubusercontent.com/jeremyong/klein/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jeremyong/mc_ruler/master/README.md>
- **Sources the enricher read:**
  - <https://github.com/jeremyong/klein>
  - <https://github.com/jeremyong/klein/tree/master/public/klein>
  - <https://github.com/jeremyong/klein/issues?q=is%3Aissue>
  - <https://github.com/jeremyong/klein/issues/30>
  - <https://github.com/jeremyong/klein/issues/8>
  - <https://raw.githubusercontent.com/jeremyong/klein/master/README.md>
  - <https://raw.githubusercontent.com/jeremyong/klein/master/docs/perf.md>
  - <https://raw.githubusercontent.com/jeremyong/klein/master/docs/index.md>
  - <https://raw.githubusercontent.com/jeremyong/klein/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jeremyong/klein/master/LICENSE>
  - <https://raw.githubusercontent.com/jeremyong/klein/master/perf/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jeremyong/klein/master/perf/klein_perf.cpp>
  - <https://raw.githubusercontent.com/jeremyong/klein/master/perf/glm_perf.cpp>
  - <https://raw.githubusercontent.com/jeremyong/klein/master/perf/rtm_perf.cpp>
  - <https://raw.githubusercontent.com/jeremyong/klein/master/public/klein/klein.hpp>
  - <https://raw.githubusercontent.com/jeremyong/klein/master/public/klein/motor.hpp>
  - <https://raw.githubusercontent.com/jeremyong/klein/master/public/klein/rotor.hpp>
  - <https://raw.githubusercontent.com/jeremyong/klein/master/public/klein/point.hpp>
  - <https://raw.githubusercontent.com/jeremyong/klein/master/public/klein/util.hpp>
  - <https://raw.githubusercontent.com/jeremyong/klein/master/public/klein/mat3x4.hpp>
  - <https://raw.githubusercontent.com/jeremyong/klein/master/public/klein/detail/sse.hpp>
  - <https://raw.githubusercontent.com/jeremyong/klein/master/public/klein/detail/sandwich.hpp>
  - <https://raw.githubusercontent.com/jeremyong/klein/master/public/klein/detail/x86/x86_sse.hpp>
  - <https://raw.githubusercontent.com/jeremyong/klein/master/public/klein/detail/x86/x86_sandwich.hpp>
  - <https://raw.githubusercontent.com/jeremyong/klein/master/public/klein/detail/x86/x86_geometric_product.hpp>
  - <https://raw.githubusercontent.com/jeremyong/klein/master/public/klein/detail/x86/x86_matrix.hpp>
  - <https://raw.githubusercontent.com/g-truc/glm/0.9.9.7/glm/gtx/dual_quaternion.inl>
  - <https://raw.githubusercontent.com/g-truc/glm/0.9.9.7/glm/detail/type_mat3x4.hpp>
  - <https://raw.githubusercontent.com/g-truc/glm/0.9.9.7/glm/detail/type_mat3x4.inl>
  - <https://raw.githubusercontent.com/g-truc/glm/0.9.9.7/glm/detail/type_vec3.hpp>
  - <https://raw.githubusercontent.com/g-truc/glm/0.9.9.7/glm/detail/setup.hpp>
  - <https://raw.githubusercontent.com/g-truc/glm/0.9.9.7/glm/detail/type_quat.inl>
  - <https://raw.githubusercontent.com/g-truc/glm/0.9.9.7/glm/detail/type_quat_simd.inl>
  - <https://raw.githubusercontent.com/g-truc/glm/0.9.9.7/glm/gtc/type_aligned.hpp>
  - <https://github.com/ga-developers/ga-benchmark>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/jeremyong/klein`) · [data/wave1/enrich/raw/github_com_jeremyong_klein.json](../../../data/wave1/enrich/raw/github_com_jeremyong_klein.json) (enrichment confidence 0.75)

</details>
