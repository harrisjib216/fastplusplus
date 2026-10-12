# nanobind

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> C++17/CPython binding library from pybind11's author; 2.3-3.1x faster builds, 3-10x lower call overhead than pybind11.

| | |
|---|---|
| **Beats** | pybind11 (also Boost.Python, Cython, cppyy) |
| **Claimed result** | Per-bar labels in the page's SVG plots (ratios relative to nanobind). Compile time: vs pybind11 2.3-3.1x (2.7x func, 3.1x class in -Os builds), vs pybind11+smart_holder 2.3-4.0x, vs Boost.Python 1.4-3.4x, vs Cython 1.6-4.4x except func [debug] where Cython compiles faster (x0.8). The page prose says '\~2.7-4.4x vs pybind11', but the 4.4x label belongs to Cython's class [opt] column; the pybind11 maximum is 3.1x (4.0x with smart_holder). Binary size in -Os builds: vs pybind11 3.3-3.7x (smart_holder 3.7-4.9x), vs Boost.Python 9.4-10.9x, vs Cython 3.3-12.5x (in the func debug build Cython is smaller, x0.4). Runtime for a bound call loop in -Os builds: vs pybind11 3.0x (func: 1.80 s vs 0.61 s for 10M calls) and 10.1x (class: 3.06 s vs 0.30 s for 2.5M construct+sum), 13.7x and 22.5x in debug builds; vs Boost.Python 2.2x/4.4x; vs cppyy 1.6x/2.1x; Cython 1.1x slower on func but about 1.4x faster on class (0.21 s vs 0.30 s, derived from page data). |
| **Workload** | Generated binding microbenchmark: function-heavy module of 720 trivial functions (all permutations of six integer/float argument types) and class-heavy module of 252 small structs with constructor and sum() (the generator stops after i &gt; 250, so not 720); compile time and stripped binary size of each module, and runtime of calling test_0000 10M times and constructing Struct0 + sum() 2.5M times, each in debug (-O0 -g3) and size-optimised (-Os -g0) builds, median of 5 runs. |
| **Metric** | compile-time; binary size (memory); call latency (runtime overhead) |
| **Hardware** | AMD Ryzen 9 7950X workstation, Ubuntu 22.04.2 LTS, CPU boost disabled and clocks pinned, median of five runs |
| **Compiler and flags** | clang++ 15.0.7 -march=native -shared -std=c++17 -fPIC -fno-stack-protector -Wno-deprecated-declarations -DPYBIND11_USE_SMART_HOLDER_AS_DEFAULT, plus -O0 -g3 (debug) or -Os -g0 (opt, then stripped); same command for every library (docs/microbenchmark.ipynb). Python 3.10.6, cppyy 1.12.13, Cython 0.29.28, nanobind 1.2.0; pybind11 and Boost.Python versions not stated (pybind11 built from a local git checkout). |
| **Adoption** | 3.7k stars; adopted by JAX, XLA/MLIR, IREE, Apple MLX and FEniCS per the README testimonials |
| **Last commit** | 2026-09-28 |
| **Links** | [repository](https://github.com/wjakob/nanobind) · [benchmark](https://raw.githubusercontent.com/wjakob/nanobind/master/docs/benchmark.rst) |

## Verdict

The author's notebook compiled 720 trivial functions and 252 small classes with clang++ 15.0.7 (-std=c++17 -march=native, -O0 -g3 or -Os then stripped) on an AMD Ryzen 9 7950X with boost off and clocks pinned (median of 5): in -Os builds nanobind 1.2.0 compiled 2.7x (func) and 3.1x (class) faster than pybind11, produced 3.7x and 3.3x smaller modules (excluding libnanobind), and ran 10M calls in 0.61 s vs 1.80 s and 2.5M construct+sum in 0.30 s vs 3.06 s under Python 3.10.6. Cython won the class runtime test (0.21 s).

## Use it when

- Exposing a large C++17 library to CPython where build time and wheel size matter: the author's 720-function and 252-class modules compiled 2.3-3.1x faster than pybind11 and were 3.3-3.7x smaller in -Os builds (see the libnanobind caveat under gotchas).
- Chatty Python-to-C++ boundaries with small arguments: about 3x lower overhead than pybind11 for plain function calls and about 10x for constructing a bound object and calling a method, in -Os builds.
- Shipping one wheel per platform across Python versions via the stable ABI (Python 3.12+), as JAX does for its CUDA plugins.
- Zero-copy tensor exchange between C++ and NumPy/PyTorch/JAX/TensorFlow through nb::ndarray, or free-threaded CPython 3.13+ extensions (FREE_THREADED flag, supported since 2.2.0).

## Skip it when

- You need to embed Python inside a C++ executable or run several interpreters in one process: the porting guide lists embedding and multi-interpreter support as removed by design (pybind11's embed API remains the option).
- Existing pybind11 code that relies on binding multiple C++ base classes, custom holder types, classes with overloaded or deleted operator new/delete, custom metaclasses, module-local bindings, py::array or .def_buffer(): these are removed, and custom type casters must be rewritten (from_python/from_cpp, noexcept).
- Per-call work dominates: the benchmark functions only add six numbers, so the call-overhead gains vanish when each call does real work.
- Cython is competitive at run time: in the author's class benchmark Cython was about 1.4x faster than nanobind (0.21 s vs 0.30 s in -Os builds) and Cython compiled the function-heavy debug module faster (x0.8).
- Python older than 3.10: nanobind 3.x requires 3.10 or newer.

## How it is fast

C++ instance data, function records and type records are co-located with the corresponding Python objects (24 bytes per-instance overhead vs 56 in pybind11, no holder indirection), calls in both directions use PEP 590 vectorcall with a dispatch loop that does no heap allocation, and internal maps use tsl::robin_map instead of std::unordered_map. Compile time and binary size drop because the dispatch loop and runtime live in a separately compiled support library (libnanobind) instead of being re-instantiated in every binding file, headers avoid most of the STL (STL casters are opt-in includes), and features such as overload complexity, C++ multiple inheritance and holder types were simplified or removed.

## Compared with alternatives

The siblings in this category (sol2, LuaBridge3) bind C++ to an embedded Lua state; pick nanobind when the target is CPython extension modules, and pick sol2 or LuaBridge3 when you are embedding a scripting runtime in your C++ program, which nanobind explicitly does not support. The category placement is questionable: nanobind belongs with FFI/binding generators rather than embedded scripting engines.

## Integration

| | |
|---|---|
| **Form** | headers plus a small support library (libnanobind) compiled from source by nanobind_add_module; static by default, NB_SHARED or a split-mode nanobind-backend wheel optional |
| **Dependencies** | CPython (or PyPy, with documented limitations) headers; tsl::robin_map bundled as a submodule; CMake 3.15+ or scikit-build-core 0.10+ (Bazel documented) |
| **Minimum toolchain** | C++17, CMake 3.15, Python 3.10+ (nanobind 3.x); stable ABI needs Python 3.12+ |
| **Platforms** | Linux, macOS and Windows (MSVC; clang-cl tested in CI since 3.0.1); the prebuilt backend wheels cover x86-64, aarch64 and riscv64 |
| **Thread safety** | GIL-protected by default; with FREE_THREADED on Python 3.13+ nanobind's internals use localized locks, but the bound C++ code must protect its own state (ft_mutex/ft_lock_guard provided), and loading any extension without free-threading support re-enables the GIL globally |
| **Drop-in for the baseline** | partial — near-identical syntax to pybind11, but removed features (multiple C++ inheritance, holders, embedding, py::array, module-local bindings) and a changed type-caster API require code changes |

## Gotchas

- Harness flaw in the size and compile-time comparison: docs/microbenchmark.ipynb links every nanobind module against a prebuilt shared library (-L.. -lnanobind, -rpath ..), so libnanobind's own compile time and size are left out of the nanobind bars, while pybind11 compiles its whole runtime into each module. nanobind_add_module's default is a static libnanobind linked into each extension. The compiled core in today's nanobind-backend 1.0.0 wheel (cp312, x86-64) is 230,640 bytes; adding about 0.22 MiB to nanobind's 0.38 and 0.26 MiB -Os module sizes would shrink the lead over pybind11 (1.41 and 0.85 MiB) from 3.7x/3.3x to roughly 2.3x/1.8x (my estimate from a newer version, not measured by the author). The lead remains, but the '\~5x smaller' headline is not what a default single-module build gets.
- The [debug] runtime ratios (13.7x and 22.5x vs pybind11) compare pybind11's dispatch code compiled at -O0 inside the module with nanobind's dispatch code in the separately built libnanobind, whose build flags the notebook does not record; quote the -Os ratios (3.0x function, 10.1x class) instead. The README and docs headlines ('\~4x' compile time, '\~5x' size, '\~10x' runtime) match only the pybind11+smart_holder or class-only columns; plain pybind11 maxima are 3.1x, 3.7x and 10.1x.
- Numbers date from nanobind 1.2.0, Python 3.10.6 and clang 15 (2023) and were not re-run for 2.x/3.x. Minor harness quirks that do not touch the pybind11 comparison: the Boost.Python class bindings declare the fifth argument type twice in py::init, and the pure-Python reference Struct0.sum omits field d.
- Type bindings are shared across extensions only when they use the same nanobind ABI version, compiler family, C++ library, debug/release mode and stable/unstable ABI; otherwise they are isolated, and two packages binding the same type can trigger 'type was already registered' warnings (FAQ). STL type casters need explicit includes such as nanobind/stl/string.h.

## Known shortcomings

- Binding generator rather than a scripting engine, and off-baseline (pybind11, not Lua, Duktape or QuickJS); the prose '2.7-4.4x vs pybind11' compile claim is contradicted by the plot labels (pybind11 max 3.1x, the 4.4x is Cython's column), the 10x runtime win is the class test only (about 3x for plain calls) and Cython is about 1.4x faster on class runtime; -Os builds, the class module has 252 structs rather than 720, pybind11 and Boost versions unpinned (docs/microbenchmark.ipynb, clang++ 15.0.7, Ryzen 9 7950X).
- Enricher: the notebook links a prebuilt shared -lnanobind, so libnanobind's size and compile time are left out of the nanobind bars (the default nanobind_add_module links it statically; the current core .so is 230,640 B, which cuts the size lead over pybind11 from about 3.7x/3.3x to about 2.3x/1.8x); the debug runtime ratios (13.7x/22.5x) pit -O0 pybind11 against a separately built libnanobind with unrecorded flags, so the -Os 3.0x/10.1x figures are the fair ones. Python embedding is unsupported by design.

## Caveats and trade-offs

Numbers come from nanobind 1.2.0, Python 3.10 and one workstation, measured by the author; they measure binding overhead on trivial functions, not application speed. The 'opt' builds use -Os, not -O2/-O3, and -march=native. The page's prose '2.7-4.4x vs pybind11' compile-time range is slightly overstated versus its own plot labels (pybind11 max 3.1x, smart_holder 4.0x). The '\~10x lower runtime overhead' holds for the class benchmark only (about 3x for plain function calls), and Cython is about 1.4x faster than nanobind in the class runtime test. pybind11 and Boost versions are unpinned. Harness quirks that do not affect the pybind11 comparison: the Boost.Python class bindings declare init with the fifth argument type twice, and the pure-Python reference Struct0.sum omits field d. The baseline is not one of the category's listed incumbents (Lua, Duktape, QuickJS), and nanobind extends CPython from C++ rather than embedding a script engine, so a category move (FFI/bindings) is plausible.

Simplified feature set compared with pybind11 (overload resolution, C++ multiple inheritance and holder types were simplified or removed). Requires C++17 and a recent CPython; bindings are generated at compile time and ship as ordinary wheels.

## Maintenance

Actively maintained (3.1.0 released Sep 2026, last commit 2026-09-28), BSD-3-Clause, about 3.7k stars and used by JAX, XLA/MLIR, IREE, Apple MLX and FEniCS; safe to adopt for new CPython bindings, with porting effort for pybind11 code that uses removed features.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now A.
- **Tier reason:** docs/benchmark.rst compares nanobind against pybind11, pybind11+smart_holder, Boost.Python, Cython and cppyy; the generating and timing code is public in docs/microbenchmark.ipynb, which gives the full clang++ 15.0.7 command line (-march=native -std=c++17 -fPIC -fno-stack-protector; -O0 -g3 debug, -Os -g0 opt), and the page names the CPU (AMD Ryzen 9 7950X, boost off, clocks pinned, median of 5).
- **Verifier notes:** Tier A holds: public notebook with exact compiler command and named CPU. Correct the compile-time range to the plot labels (2.3-3.1x vs pybind11 overall, 2.7-3.1x in -Os builds) and record that the 10x runtime figure is class-only and that Cython wins the class runtime test; metadata (BSD-3-Clause, 3.7k stars, last commit 2026-09-28, not a fork) confirmed. Consider moving it out of embedded-scripting into an FFI/bindings category.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/wjakob/nanobind/master/docs/benchmark.rst>
  - <https://raw.githubusercontent.com/wjakob/nanobind/master/docs/microbenchmark.ipynb>
  - <https://raw.githubusercontent.com/wjakob/nanobind/master/docs/images/times.svg>
  - <https://raw.githubusercontent.com/wjakob/nanobind/master/docs/images/sizes.svg>
  - <https://raw.githubusercontent.com/wjakob/nanobind/master/docs/images/perf.svg>
  - <https://github.com/wjakob/nanobind>
  - <https://github.com/wjakob/nanobind/commits>
- **Sources the enricher read:**
  - <https://github.com/wjakob/nanobind>
  - <https://raw.githubusercontent.com/wjakob/nanobind/master/README.md>
  - <https://raw.githubusercontent.com/wjakob/nanobind/master/docs/benchmark.rst>
  - <https://raw.githubusercontent.com/wjakob/nanobind/master/docs/microbenchmark.ipynb>
  - <https://raw.githubusercontent.com/wjakob/nanobind/master/docs/images/times.svg>
  - <https://raw.githubusercontent.com/wjakob/nanobind/master/docs/images/sizes.svg>
  - <https://raw.githubusercontent.com/wjakob/nanobind/master/docs/images/perf.svg>
  - <https://raw.githubusercontent.com/wjakob/nanobind/master/docs/why.rst>
  - <https://raw.githubusercontent.com/wjakob/nanobind/master/docs/porting.rst>
  - <https://raw.githubusercontent.com/wjakob/nanobind/master/docs/changelog.rst>
  - <https://raw.githubusercontent.com/wjakob/nanobind/master/docs/faq.rst>
  - <https://raw.githubusercontent.com/wjakob/nanobind/master/docs/free_threaded.rst>
  - <https://raw.githubusercontent.com/wjakob/nanobind/master/docs/building.rst>
  - <https://raw.githubusercontent.com/wjakob/nanobind/master/docs/api_cmake.rst>
  - <https://raw.githubusercontent.com/wjakob/nanobind/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/wjakob/nanobind/master/pyproject.toml>
  - <https://raw.githubusercontent.com/wjakob/nanobind/master/cmake/nanobind-config.cmake>
  - <https://pypi.org/pypi/nanobind/json>
  - <https://pypi.org/pypi/nanobind-backend/json>
  - <https://files.pythonhosted.org/packages/b9/2c/7fb13ecb1e8c0c268e26c6bc44be4a7f51996b2a3c006749ce6fc4fd7da2/nanobind_backend-1.0.0-cp312-cp312-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl>
  - <https://github.com/wjakob/nanobind/issues?q=is%3Aissue+performance+slower+pybind11>
  - <https://github.com/wjakob/nanobind/issues/918>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/wjakob/nanobind`) · [data/wave12/enrich/raw/github_com_wjakob_nanobind.json](../../../data/wave12/enrich/raw/github_com_wjakob_nanobind.json) (enrichment confidence 0.85)

</details>
