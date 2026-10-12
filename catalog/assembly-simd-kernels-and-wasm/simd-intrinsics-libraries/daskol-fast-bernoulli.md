# fast-bernoulli (AVX Bernoulli sampler with LLVM JIT)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🔴 abandoned

> Bit-packed Bernoulli sampler (AND/NOT of random bits, AVX2, optional LLVM JIT) versus std::bernoulli_distribution over mt19937_64.

| | |
|---|---|
| **Beats** | std::bernoulli_distribution&lt;&gt; drawing from std::mt19937_64, one draw per output bit packed into bytes (TStdSampler in fast-bernoulli/cc/sampler.cc) |
| **Claimed result** | README Google Benchmark table (parameter 128, p = 0.6): BM_StdSampler 72,260,140 ns, BM_GenericSampler 104,076 ns, BM_AvxSampler 71,017 ns, BM_JitAvxSampler 55,667 ns. The raw time ratios (1017x AVX, 1298x JIT AVX) compare unequal work: BM_StdSampler allocates and fills 16 \* 128 \* 32 bytes = 524,288 bits per iteration while the other samplers produce 128 blocks of 256 bits = 32,768 bits. Per output bit: Std about 138 ns, AVX about 2.17 ns, JIT AVX about 1.70 ns, i.e. about 64x (AVX), 81x (JIT AVX) and 43x (generic, no SIMD) faster than std::bernoulli_distribution (derived from page data and sampler_bench.cc). The throughput column is bytes/s in both rows (55.4 KiB/s vs 55.0 MiB/s), computed from the same 4096 bytes per iteration, so it repeats the 16x error. |
| **Workload** | Google Benchmark BM_\*Sampler/128 at p = 0.6 (tolerance 1e-3 for the fast samplers): fast samplers fill NoSrcBlocks x 128 blocks with mt19937_64 output and combine them with and/not into 128 blocks of 256 Bernoulli bits; the Std sampler fills 16x as many bits (524,288) one std::bernoulli_distribution draw per bit. |
| **Metric** | throughput |
| **Hardware** | 4 x 3400 MHz CPUs, L1d 32K, L2 256K, L3 4096K (Google Benchmark header); model not stated |
| **Compiler and flags** | README build: CMake -DCMAKE_BUILD_TYPE=Release, C++17, library objects compiled with -mavx -mavx2, optional LLVM 8/9 JIT; compiler and version not stated |
| **Adoption** | 6 stars |
| **Last commit** | 2019-10-28 |
| **Links** | [repository](https://github.com/daskol/fast-bernoulli) · [benchmark](https://raw.githubusercontent.com/daskol/fast-bernoulli/HEAD/README.md) |

## Verdict

Google Benchmark on an unnamed 4-core 3.4 GHz x86 with the compiler and flags unrecorded, p = 0.6, tol 1e-3, 128 blocks: per output bit, std::bernoulli_distribution over mt19937_64 took about 138 ns versus 3.18 ns (generic), 2.17 ns (AVX) and 1.70 ns (JIT AVX), i.e. about 43x, 64x and 81x (derived from page data). The README's raw 1000-1300x includes 16x more work for the std baseline. The same run's mt19937_64 call costs about 9.35 ns and a std::bernoulli_distribution draw needs one, so the 138 ns baseline is about 15x its own RNG floor, which points to an unoptimised build or a slow libstdc++ generate_canonical; the fast samplers are RNG-bound (5,632 mt19937_64 calls, about 52.6 us of JIT AVX's 55.7 us). Against a baseline running near its RNG floor the per-bit gain would be nearer 5-6x (64 versus 11 random bits per output bit; derived from page data).

## Use it when

- Bulk fixed-p Bernoulli masks of thousands to millions of bits (random graph adjacency bits, dropout or erasure masks, coding-theory channel simulation) where the consumer reads packed bits.
- Throughput-bound code on x86-64 with AVX2 where about 1e-3 absolute error in p is acceptable.
- Moderate p (roughly 0.05 to 0.95), where the absolute tolerance is small relative to p.
- As a reference for the AND/NOT bit-combination trick to re-implement in your own code base (the core executor plus Quantize is under 150 lines, BSD-3-Clause).

## Skip it when

- You need the exact p or a small p: the tolerance is absolute, so p = 1e-4 at the default 1e-3 yields 2^-11 (about 4.9e-4, 4.9x too high) and p = 1e-6 yields about 488x too high (derived by porting Quantize).
- Non-x86 targets, MSVC, or CPUs with AVX but no AVX2 (Sandy and Ivy Bridge): the code includes &lt;x86intrin.h&gt;/&lt;cpuid.h&gt;, uses C++20-style designated initializers under C++17, and is built with -mavx2 throughout.
- Entropy-efficient sampling: every output bit consumes NoSrcBlocks raw bits (11 at p = 0.6) against about 0.97 bits of entropy; issue #2's reporter moved to the Fast Loaded Dice Roller for that reason.
- Small or per-call Python use: sample() builds a new sampler (and with jit=True a new LLVM JIT module) on every call, leaks its heap-allocated TRng, and expands the result to one byte per bit.
- Projects that need a maintained dependency or modern LLVM: no commits since 2019-10-28, no releases, not on PyPI, and the JIT path has an #error for LLVM other than 8 or 9.

## How it is fast

Quantize() binary-searches p into a short program of AND and NOT operations on uniform random words (ANDing two independent Bernoulli(1/2) bits halves p, NOT gives 1 - p), so each output bit costs a few raw PRNG bits and no float compare or branch; at p = 0.6 and tol 1e-3 it is 16 ops over 11 source words. The executor applies the program to whole 256-bit ymm registers (TAvxExecutor) or 64-bit words (TGeneralExecutor), in place over a buffer pre-filled with mt19937_64 output. The LLVM JIT (ORC LLJIT, LLVM 8 or 9) emits a straight-line function per plan, which removes the per-op switch but is still called once per 32-byte block through a function pointer.

## Compared with alternatives

No sibling in this category generates random variates; the closest in spirit are approximation kernels like SIMD-math-prims, which also trade exactness for SIMD throughput. Pick fast-bernoulli only for bulk packed Bernoulli bits on AVX2 x86, and treat it as an algorithm to vendor rather than a maintained library.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | none for the AOT samplers; LLVM 8 or 9 for the JIT executor; Google Benchmark, GTest and Cython only for benchmarks, tests and the Python wheel |
| **Minimum toolchain** | C++17 with GCC or Clang (designated initializers, &lt;x86intrin.h&gt;, &lt;cpuid.h&gt;), CMake 3.15 |
| **Platforms** | x86-64 only; AVX2 required in practice (library compiled with -mavx -mavx2) |
| **Thread safety** | README lists 'Thread-safe'; a sampler's plan is immutable after creation, so one sampler can be shared if each thread passes its own mt19937_64 and buffer (inferred from source, not documented further) |
| **Drop-in for the baseline** | no |

## Gotchas

- TSamplerPtr::operator() returns bool converted from EStatus, and EOk is 0, so it returns false on success; Validate() only checks 16-byte alignment while the AVX path uses aligned 32-byte loads, and the buffer must be NoSrcBlocks times the output size (11x at p = 0.6) with only its first 1/NoSrcBlocks holding samples. Use MakeBuffer() and ignore the return value's truthiness.
- Auto dispatch checks only CPUID.1:ECX.AVX (no AVX2 or OSXSAVE check) but TAvxExecutor uses AVX2 integer ops, so it can fault with SIGILL on AVX-only CPUs; on non-AVX x86 Auto selects the unimplemented SSE executor and CreateSampler returns an empty pointer, as it also does when tol is too tight for 64 ops (below about 1e-13 for non-dyadic p). Calling an empty TSamplerPtr dereferences null.
- Harness flaw behind the README table: it was produced at commit 13f57cc (2019-10-11), when TAvxExecutor applied the plan in reverse order (Ops_[NoOps_ - ip - 1]) while Quantize already reversed it; at p = 0.6 that build sampled about p = 0.40, not 0.6 (derived by porting Quantize). It was fixed in 0d005fd on 2019-10-18. The statistical test hard-codes Ise_ = General (still true at HEAD), so the AVX path was never checked for its mean. Timing is probably unaffected, since the op count is the same.
- Other defects: the JIT emits add instead of or for EOp::Or (latent, since Quantize never emits Or); the std baseline ORs bits into an uninitialised buffer; BM_JitGenericSampler runs the non-JIT sampler; HEAD guards the JIT benchmarks with a misspelled USE_JIT_EXCUTOR; and the top-level CMakeLists checks a misspelled LLVM_VERION_MAJOR.

## Known shortcomings

- BM_StdSampler does 16x the bits per iteration (sampler_bench.cc), so the raw 1000-1300x is really about 64x AVX, 81x JIT AVX and 43x generic per bit (derived); the sampler is approximate (1e-3 tolerance), the std baseline buffer is never cleared, the JitGeneric row is not JIT, the HEAD guard is misspelled USE_JIT_EXCUTOR; compiler and CPU unstated.
- Enricher: the README table was run at commit 13f57cc, when TAvxExecutor applied its plan in reverse order (fixed in 0d005fd, 2019-10-18), so the AVX row sampled about p 0.40 rather than 0.6 (derived by porting Quantize); the stat test hard-codes Ise_ = General so the AVX path is never checked; the std baseline (138 ns per draw) sits against 9.35 ns per mt19937_64 call in the same run, so the fast samplers are RNG-bound and the realistic per-bit gain is nearer 5-6x than 64-81x; absolute tolerance (p=1e-4 gives 4.9e-4), an AVX-only CPUID check before AVX2 code, operator() returns false on success. Numbers predate a correctness fix; caveats recorded in retier-03.

## Caveats and trade-offs

The benchmark gives BM_StdSampler 16x more bits per iteration than the fast samplers (size = 16 \* noblocks \* GetBufferSize()), so the README's raw \~1000x time gap is about 64x per bit (43x for the non-SIMD generic sampler, so most of the win is the algorithm's fewer RNG draws per bit, not AVX). The fast samplers are approximate: the probability is quantised to within the 1e-3 tolerance. The Std baseline ORs bits into a buffer that is never cleared (\*it |= ...), so its output is wrong after the first call (timing barely affected). BM_JitGenericSampler calls the non-JIT BM_Sampler, so that row is not JIT (its time matches the generic row). In the current tree the JIT benchmarks sit under a misspelled #ifdef USE_JIT_EXCUTOR while CMake defines USE_JIT_EXECUTOR, so HEAD cannot reproduce the JIT rows; the README table came from the October 2019 src/ layout, which had the same 16x factor. Compiler and CPU model are missing; about 138 ns per std::bernoulli_distribution draw is slow for an optimised build. [retier] Table measured before the reverse-order plan fix 0d005fd (AVX row sampled about p 0.40); AVX path never checked by the stat test; std baseline RNG-bound, realistic per-bit gain about 5-6x; absolute tolerance; AVX-only CPUID check before AVX2 code

Returns bit-packed blocks rather than bools; probability is quantised into a sequence of AND and NOT operations; uses AVX vectors and optional LLVM JIT; Python bindings.

## Maintenance

Abandoned since 2019-10-28 (47 commits, 6 stars, no releases, not on PyPI), but BSD-3-Clause and small enough to vendor the Quantize and AVX executor; the JIT needs LLVM 8 or 9, and the README's AVX timings came from a build that sampled the wrong probability (fixed 2019-10-18).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party Google Benchmark table in the README from public code (fast-bernoulli/cc/benchmark/sampler_bench.cc, src/sampler_bench.cc at the time of the run), but compiler, version and CPU model are not stated (only '4 X 3400 MHz' and cache sizes), so C. Tier unchanged; verdict is downgrade because the headline 1000x/1300x is overstated about 16x by unequal work per iteration.
- **Verifier notes:** Downgrade of the claim, not the tier: sampler_bench.cc makes the std baseline do 16x the work, so the real per-bit gain is about 64x (AVX) and 81x (JIT AVX), not 1000-1300x. Other shortcomings: approximate sampler (1e-3 tolerance), std baseline output buffer never cleared, mislabelled JitGeneric row, misspelled USE_JIT_EXCUTOR guard at HEAD, compiler and CPU model unstated, abandoned since 2019-10-28.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `workload`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-110 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/HEAD/README.md>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/master/fast-bernoulli/cc/benchmark/sampler_bench.cc>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/master/fast-bernoulli/cc/benchmark/executor_bench.cc>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/master/fast-bernoulli/cc/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/master/fast-bernoulli/cc/CMakeLists.txt>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/master/fast-bernoulli/cc/sampler.cc>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/master/fast-bernoulli/cc/sampler.h>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/2f35bf5/src/sampler_bench.cc>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/2f35bf5/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/2f35bf5/src/sampler.cc>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/2f35bf5/README.md>
  - <https://github.com/daskol/fast-bernoulli>
  - <https://github.com/daskol/fast-bernoulli/commits>
  - <https://github.com/daskol/fast-bernoulli/tree/master/fast-bernoulli>
  - <https://github.com/daskol/fast-bernoulli/tree/master/fast-bernoulli/cc>
  - <https://github.com/daskol/fast-bernoulli/tree/master/fast-bernoulli/cc/benchmark>
  - <https://github.com/daskol/fast-bernoulli/commits/master/fast-bernoulli/cc/benchmark/sampler_bench.cc>
  - <https://github.com/daskol/fast-bernoulli/commits/master/README.md>
  - <https://github.com/daskol/fast-bernoulli/tree/2f35bf5>
- **Sources the enricher read:**
  - <https://github.com/daskol/fast-bernoulli>
  - <https://github.com/daskol/fast-bernoulli/commits>
  - <https://github.com/daskol/fast-bernoulli/issues?q=is%3Aissue>
  - <https://github.com/daskol/fast-bernoulli/issues/2>
  - <https://github.com/daskol/fast-bernoulli/commit/0d005fd>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/master/README.md>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/master/LICENSE>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/master/setup.py>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/master/fast-bernoulli/CMakeLists.txt>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/master/fast-bernoulli/fast-bernoulli.h>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/master/fast-bernoulli/cc/CMakeLists.txt>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/master/fast-bernoulli/cc/common.h>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/master/fast-bernoulli/cc/config.h.in>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/master/fast-bernoulli/cc/cpuid.h>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/master/fast-bernoulli/cc/cpuid.cc>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/master/fast-bernoulli/cc/sampler.h>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/master/fast-bernoulli/cc/sampler.cc>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/master/fast-bernoulli/cc/executor.h>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/master/fast-bernoulli/cc/executor.cc>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/master/fast-bernoulli/cc/executor_jit.h>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/master/fast-bernoulli/cc/executor_jit.cc>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/master/fast-bernoulli/cc/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/master/fast-bernoulli/cc/benchmark/sampler_bench.cc>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/master/fast-bernoulli/cc/benchmark/executor_bench.cc>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/master/fast-bernoulli/cc/unittest/CMakeLists.txt>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/master/fast-bernoulli/cc/unittest/sampler_test.cc>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/master/fast-bernoulli/cc/unittest/executor_test.cc>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/master/fast-bernoulli/cc/unittest/executor_jit_test.cc>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/master/fast-bernoulli/python/CMakeLists.txt>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/master/fast-bernoulli/python/setup.py.in>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/master/fast-bernoulli/python/fast_bernoulli.pyx>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/13f57cc/README.md>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/13f57cc/src/executor.cc>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/13f57cc/src/executor_jit.cc>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/13f57cc/src/sampler_bench.cc>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/13f57cc/src/sampler_test.cc>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/13f57cc/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/13f57cc/CMakeLists.txt>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/2f35bf5/README.md>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/2f35bf5/src/executor.cc>
  - <https://raw.githubusercontent.com/daskol/fast-bernoulli/2f35bf5/src/sampler_bench.cc>
  - <https://pypi.org/pypi/fast-bernoulli/json>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/daskol/fast-bernoulli`) · [data/wave13/enrich/raw/github_com_daskol_fast_bernoulli.json](../../../data/wave13/enrich/raw/github_com_daskol_fast_bernoulli.json) (enrichment confidence 0.82)

</details>
