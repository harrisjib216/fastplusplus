# CBQN (BQN array language) - CRLF-to-LF conversion versus plain C

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `BQN (implementation in C, SIMD kernels generated with Singeli)` · `LGPL-3.0-only OR GPL-3.0-only OR MPL-2.0` · 🟢 active

> C interpreter for the BQN array language whose SIMD primitives beat a plain C loop 5-11x on CRLF-to-LF filtering.

| | |
|---|---|
| **Beats** | Plain scalar C loop for the same line-ending conversion (crlf_to_lf), compiled with clang 15.0.7 -O3 -march=native |
| **Claimed result** | Page text: BQN breaks even with C at a little under 200 bytes and hits 5x C's speed on inputs of a few thousand bytes or more with AVX-512 disabled, over 10x with AVX-512 until cache becomes a bottleneck. Page timings on a Tiger Lake i5-1135G7 (a CRLF every \~100 bytes): C (clang 15.0.7 -O3 -march=native) 0.555 ns/elt from 10k to 1M bytes (0.613 at 100 bytes); CBQN avx2/bmi2/pclmul build 0.893 (100 bytes, slower than C), 0.127 (3k), 0.106 (10k), 0.094 (30k), 0.107 (1M) ns/elt, about 4.4x at 3k and 5.2-5.9x from 10k up (derived from page data); CBQN native build (AVX-512) 0.0526 (10k), 0.0506 (30k), 0.0537 (100k), 0.0787 (1M) ns/elt, about 10.3-11.0x from 10k to 300k and 7.1x at 1M (derived from page data). The page's selection figures (0.04 ns per selection from a table of 32 or fewer 1-byte values via shuffles versus 0.2 ns via gather) are two CBQN code paths, not a C measurement. The compiler benchmark (implementation/bootbench.md) is a separate claim: boot3.bqn in CBQN compiles boot2.bqn in 270.6 us versus 415.5 us for dzaima's comp.c built with clang 15.0 (system values and error handling removed), average of 10,000 runs on a Skylake i5-6200U, i.e. 35% less time (about 1.54x, derived from page data); the two compilers use different algorithms and the C build flags are not stated. |
| **Workload** | Replace every CRLF with LF in a byte buffer of 100 to 1,000,000 bytes with a CRLF about every 100 characters; BQN one-liner (cr!=) with (0 shifted lf!=) filtered by Replicate versus a scalar C loop; the page also reports selection and compiler benchmarks. |
| **Metric** | throughput |
| **Hardware** | Intel Tiger Lake Core i5-1135G7 |
| **Compiler and flags** | C baseline: clang 15.0.7, 'clang -O3 -march=native lineending.c' (gcc 12.2.1 also discussed: branching code, slightly faster at low density, much slower at high). CBQN built at commit 0d2631a2 with FFI, singeli x86-64 avx2 bmi2 pclmul (and a native build) |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | yes |
| **Why it wins** | Array primitives are implemented with hand-written SIMD, lookup tables and blocked multi-pass techniques (Replicate compresses with AVX2/AVX-512 mask operations, adapts to sparse inputs), which compilers do not generate from a scalar branching loop (no SIMD scan, movmask or compress idioms from portable C). The page itself says this is a best case: 'Your BQN programs are unlikely to outperform equivalent C programs' and specialized C is always faster. |
| **Adoption** | 409 stars |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/dzaima/CBQN) · [benchmark](https://raw.githubusercontent.com/mlochbaum/BQN/master/docs/implementation/versusc.html) |

## Verdict

Marshall Lochbaum's versusc page measured CRLF-to-LF conversion with about one CRLF per 100 bytes on a Tiger Lake i5-1135G7. A scalar C loop (clang 15.0.7 -O3 -march=native, branchless, unrolled 4x) ran at 0.555 ns/byte. CBQN at commit 0d2631a ran at 0.094-0.107 ns/byte from 10 KB up with an AVX2/BMI2/PCLMUL build (5.2-5.9x) and 0.051-0.054 ns/byte with a native AVX-512 build (about 10-11x up to 300 KB, 7.1x at 1 MB). BQN was slower at 100 bytes.

## Use it when

- Data-parallel filtering, selection, grouping, sorting and searching over long homogeneous arrays (hundreds to millions of elements), especially 1- or 2-byte elements such as text bytes
- Text and byte-stream transforms that fit compress or mask patterns (strip characters, split, tokenise) where the C alternative is a scalar loop the compiler cannot vectorise
- Prototyping a SIMD strategy before hand-writing it in C: the author uses BQN this way, and the primitive kernels in src/singeli show how each primitive is vectorised
- x86-64 machines where you can build natively (make o3n) to get AVX2, BMI2 and, on AVX-512 VBMI2 CPUs, the compress-instruction paths

## Skip it when

- Small inputs: on the page BQN is slower than C below about 200 bytes (100 bytes: 0.893 vs 0.613 ns/elt) because each primitive call has overhead
- Sequential, data-dependent loops, object-heavy code, wrapping fixed-width integer arithmetic (cryptography) or decimal rounding; the page names all of these as poor fits
- Competing against hand-written SIMD C: the C baseline here is a portable scalar loop, and the page says specialised C is always faster
- Hot paths that must exchange data with C/C++ often: bqn_make\*Vec copies its input, and the page calls FFI not the fastest interface
- Arrays over 2^31 elements or deeply nested data: the README warns some builtins error or give wrong results above 2^31, recursive freeing can overflow the stack (issue #129 open), and caught errors leak memory permanently

## How it is fast

Each primitive dispatches at run time on element type (packed 1-bit booleans, 1- and 2-byte chars and ints), length and data statistics into hand-written kernels. Most of these are generated as C intrinsics from the Singeli SIMD DSL. Boolean Replicate (/), the kernel behind this result, adapts its method to the mask: a sparse method when few bits are set, grouped memcpy when the mask switches rarely, otherwise a dense SIMD compress (table lookup plus shuffle on AVX2, the AVX-512 VBMI2 compress instruction on native builds). The comparisons that build the mask produce bit-packed output via SIMD compare and movemask, which clang does not generate from the scalar C loop.

## Compared with alternatives

Halide and Futhark compile ahead of time: Halide schedules stencil and image pipelines, and Futhark targets GPUs. Pick CBQN for interactive, irregular data-movement work on CPU (filtering, grouping, selection on byte-sized data) where no compile or scheduling step is wanted. Pick Halide or Futhark for dense numeric pipelines and GPU kernels.

## Integration

| | |
|---|---|
| **Form** | interpreter executable, or shared/static library (libcbqn) with a C API in include/bqnffi.h |
| **Dependencies** | C compiler; libffi &gt;= 3.3 for •FFI (FFI=0 drops it); C++11 compiler for the optional replxx REPL; Singeli and precompiled bytecode come as git submodules |
| **Minimum toolchain** | gcc &gt;= 9 or clang &gt;= 10 (clang preferred and default); bootstraps a build-time CBQN to run build.bqn and Singeli |
| **Platforms** | x86-64 (SSE baseline by default; AVX2, BMI2 and PCLMUL via has= or native builds; AVX-512 paths only in native builds), aarch64 (NEON), generic C fallback, 32-bit x86 with SSE2, Emscripten and WASI; Linux, BSD and macOS, Windows by cross-compilation |
| **Thread safety** | not documented; the embedding API has one global bqn_init() and no thread-related functions |
| **Drop-in for the baseline** | no |

## Gotchas

- The README says CBQN 'does not utilize AVX-512', yet src/singeli/src/slash.singeli has AVX-512 VBMI2 and AVX-512F compress paths for Replicate. build.bqn passes no arch restriction to Singeli for native builds, so these paths are enabled there, and the page's &gt;10x row depends on them. The has= option accepts only up to avx2 and bmi2, and a plain 'make' (o3) targets baseline x86-64, so distro packages or default builds are likely below the measured 5x AVX2 figure (not measured).
- Benchmark harness checked: same LCG data, the same number of elements per timing (5e8), and C writes into a preallocated buffer while BQN allocates a fresh result each call (this favours C). At 1 CRLF per 100 bytes the mask switches more than once per 128 bytes, so CBQN takes its branchless dense SIMD compress (slash.c dispatch), not a branchy path the repeated input could train. The BQN one-liner drops a lone CR at the very end of a buffer (« shifts in 0), while the C loop keeps it. Simulating the generator shows no tested prefix ends in CR, so the outputs match.
- The 35% compiler-benchmark claim (bootbench.md) is a different measurement on a Skylake i5-6200U. comp.c was built into CBQN commit 92763fa via f='-DNATIVE_COMPILER' (so probably the same native -O3 build, inferred). The two compilers use different designs, and C is faster on sources under 1 KB, where both take about 50 us.
- Error throwing uses longjmp, so the GC can only run fully between REPL lines. Long-running embedded use with frequent caught errors leaks memory (README Limitations).

## Known shortcomings

- First-party 2023 run (versusc.md, clang 15.0.7 -O3 -march=native, i5-1135G7); the win comes from CBQN's SIMD Replicate primitive against a portable scalar C loop, a best case by the author's own account (native-build ratio 7.1-11.0x); the 0.04 vs 0.2 ns selection row compares two CBQN code paths; the 35% compiler-benchmark claim ran on an i5-6200U with different algorithms and no C flags.
- Harness sound (same data, same element counts, branchless dense compress path; the BQN one-liner drops a trailing lone CR but no tested prefix ends in CR). The README says CBQN does not use AVX-512, yet slash.singeli has AVX-512 VBMI2 compress paths enabled only in native builds (make o3n); the &gt;10x row needs them, and default or has= builds are likely below 5x (not measured).

## Caveats and trade-offs

First-party measurement by the BQN author on one machine; both programs, the C compile line and the CBQN commit and build options are on the page, so it is reproducible (CBQN builds at -O3 with the system cc by default; the compiler used for CBQN is not named). The C baseline is the plain portable scalar loop the author took from his 2017 Dyalog talk; clang 15 makes it branchless and unrolls it 4x, so it is not crippled, but no SIMD-intrinsic or memchr/memcpy-chunk C version was tested and the page says specialized C is always faster. The win is CBQN's hand-written Singeli SIMD Replicate primitive (an adaptive sparse/dense compress) against compiler output for a scalar loop: a best case for BQN primitives, as the page itself says ('combinations of primitives never do so well'); density 1/100 is described as not particularly favourable. Not the same algorithm in the strict sense (data-parallel mask plus Replicate versus a sequential scan), but output is identical. The selection figures (0.04 versus 0.2 ns) compare two CBQN paths, not C. The compiler benchmark side claim (35% faster) ran on different hardware (i5-6200U), compares different compiler designs and states no C flags. The page dates from 2023 (clang 15.0.7, gcc 12.2.1; 'the C compilers of today (2023)') and CBQN has changed since. Licence: most files LGPL-3.0-only OR GPL-3.0-only OR MPL-2.0 at the user's choice; timsort files MIT and Ryu Apache-2.0 or BSL-1.0. [retier] The README says CBQN does not use AVX-512, yet slash.singeli has AVX-512 VBMI2 compress paths enabled only in native builds (make o3n); the &gt;10x row depends on them, and default or has= builds (which accept only up to avx2) are likely below 5x (not measured). The BQN one-liner drops a trailing lone CR, but no tested prefix ends in CR, so outputs match.

Whole-array style only: per-primitive call overhead, benefits grow with array length (hundreds to thousands of elements) and small element types; poor for sequential, data-dependent loops, cryptography with wrapping integer ops, and C++-style object dispatch. Interpreter, so C interop is through an FFI with copying. Licensing is a per-file mix with timsort (MIT) and Ryu (Apache-2.0/Boost) exceptions.

## Maintenance

Actively developed (last commit 2026-10-05, 4,105 commits, 409 stars, mostly by dzaima) with no GitHub releases, so you build from the develop branch with submodules. The licence is a choice of LGPLv3, GPLv3 or MPL-2.0 (timsort MIT, Ryu Apache-2.0/BSL-1.0). The 2023 benchmark has not been re-run on current CBQN or newer compilers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** The page (implementation/versusc.md, rendered as docs/implementation/versusc.html) prints both benchmark programs (lineending.bqn and lineending.c), the exact C build line 'clang -O3 -march=native lineending.c' with clang 15.0.7, the CBQN commit 0d2631a2 with its Singeli build options, and the CPU (Tiger Lake i5-1135G7); every quoted ns/elt figure matches. CBQN's makefile at that commit builds with -O3 by default; only the C compiler used to build CBQN itself is unstated, which is how other interpreter entries held at A were treated.
- **Verifier notes:** All numbers match the page; native-build ratio corrected to 7.1-11.0x and the selection figure reclassified as CBQN-internal (both paths are CBQN). Shortcomings to record: first-party single-machine 2023 run; C side is portable scalar code at -O3 -march=native (no intrinsics or memchr-based version), so the win is CBQN's SIMD Replicate primitive and a best case by the author's own account; compiler-benchmark side claim on other hardware with different algorithms and unstated C flags. CBQN is not listed in any earlier wave.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-02 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/mlochbaum/BQN/master/docs/implementation/versusc.html>
  - <https://raw.githubusercontent.com/mlochbaum/BQN/master/implementation/versusc.md>
  - <https://raw.githubusercontent.com/mlochbaum/BQN/master/implementation/bootbench.md>
  - <https://raw.githubusercontent.com/dzaima/CBQN/0d2631a2278fab44164f4619a1a8c295fe674fa0/makefile>
  - <https://github.com/dzaima/CBQN>
  - <https://github.com/dzaima/CBQN/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/mlochbaum/BQN/master/implementation/versusc.md>
  - <https://raw.githubusercontent.com/mlochbaum/BQN/master/implementation/bootbench.md>
  - <https://raw.githubusercontent.com/dzaima/CBQN/HEAD/README.md>
  - <https://raw.githubusercontent.com/dzaima/CBQN/HEAD/docs/README.md>
  - <https://raw.githubusercontent.com/dzaima/CBQN/HEAD/docs/system.md>
  - <https://raw.githubusercontent.com/dzaima/CBQN/HEAD/include/bqnffi.h>
  - <https://raw.githubusercontent.com/dzaima/CBQN/HEAD/build/src/build.bqn>
  - <https://raw.githubusercontent.com/dzaima/CBQN/HEAD/src/singeli/src/slash.singeli>
  - <https://raw.githubusercontent.com/dzaima/CBQN/HEAD/src/builtins/slash.c>
  - <https://raw.githubusercontent.com/dzaima/CBQN/0d2631a2278fab44164f4619a1a8c295fe674fa0/src/singeli/src/slash.singeli>
  - <https://raw.githubusercontent.com/dzaima/CBQN/0d2631a2278fab44164f4619a1a8c295fe674fa0/src/builtins/slash.c>
  - <https://github.com/dzaima/CBQN>
  - <https://github.com/dzaima/CBQN/commits>
  - <https://github.com/dzaima/CBQN/issues?q=is%3Aissue>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/dzaima/cbqn`) · [data/wave14/enrich/raw/github_com_dzaima_cbqn.json](../../../data/wave14/enrich/raw/github_com_dzaima_cbqn.json) (enrichment confidence 0.8)

</details>
