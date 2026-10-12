# cslarsen/mersenne-twister

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🔴 abandoned

> Loop-unrolled, batch-tempered MT19937 in one C++ file; same output as reference mt19937ar.c, 1.1-1.6x faster on Intel.

| | |
|---|---|
| **Beats** | reference mt19937ar.c (Mersenne Twister) |
| **Claimed result** | 1.58707 times faster than reference (351.4-354.5 M numbers/s vs 221.6-223.4 M/s) on Xeon with gcc 6.3; 1.12485x on an older Core i7 with clang |
| **Workload** | Generating 32-bit MT19937 numbers, best of 20 passes, vs reference mt19937ar.c |
| **Metric** | throughput |
| **Hardware** | Intel Xeon (model unstated); older Intel Core i7 |
| **Compiler and flags** | gcc 6.3 (Xeon run) / clang 4 'I think' (Core i7 run); Makefile CXXFLAGS include -O2 plus warnings |
| **Adoption** | 86 stars |
| **Last commit** | 2017-12-06 |
| **Links** | [repository](https://github.com/cslarsen/mersenne-twister) · [benchmark](https://github.com/cslarsen/mersenne-twister) |

## Verdict

Author's own test-mt run (best of 20 passes, both implementations built with the repo Makefile's -O2 -march=native flags) gave 351-355 M numbers/s vs 222-223 M/s for the reference mt19937ar code (1.59x) on an unnamed Intel Xeon with gcc 6.3, and only 1.12x on an older Core i7 with clang 4; no comparison with std::mt19937.

## Use it when

- Legacy code that must keep the exact MT19937 sequence (reproducible simulations, saved seeds) but wants a faster scalar implementation than mt19937ar.c
- C or C++ projects on x86 that want a tiny vendorable MT19937 with no dependencies
- Single-threaded Monte Carlo code drawing many 32-bit values in a tight loop

## Skip it when

- Multithreaded code: state is one static global struct with no locking; you must edit the source to make it per-instance
- When you are free to change generator: modern generators (lehmer64, wyrand, splitmix64, pcg64) are faster and MT19937 fails PractRand binary-rank tests
- Non-Intel CPUs: the author says he only tested Intel and doubts the speedup holds elsewhere; the extra unrolling (MT_UNROLL_MORE) is slower on newer Xeons
- Code already using std::mt19937: no comparison against libstdc++/libc++ is published, and those implementations may already be competitive
- Need for 64-bit outputs, jump-ahead, or cryptographic unpredictability (624 outputs reveal the state, per the README)

## How it is fast

The state-update loop is split into two index ranges (0..226 and 227..622) so the wrap-around modulus disappears, the odd/even matrix select uses a branchless sign-extension trick ((int32_t(y) &lt;&lt; 31) &gt;&gt; 31) & MAGIC instead of a table lookup, and tempering is done for all 624 words in one batch into a second array so rand_u32() is just an array read. The Makefile adds -O2 -march=native -funroll-loops -ftree-vectorize so the batch loops can vectorize.

## Compared with alternatives

Pick this only when you must keep the MT19937 sequence; if the generator can change, testingRNG's lehmer64 or wyrand headers are about 2x faster than MT19937 in that repo's table, and SHISHUA or xoshiro8x256pp are far faster for bulk fills.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none |
| **Minimum toolchain** | C++11 (Makefile uses --std=gnu++11; source uses default member initializers) |
| **Platforms** | any in principle; only tested on Intel x86-64 |
| **Thread safety** | Not thread-safe: single static MTState shared by all callers |
| **Drop-in for the baseline** | partial — same output sequence as mt19937ar.c's init_genrand/genrand_int32, but different function names (seed/rand_u32) and no init_by_array or real-valued outputs |

## Gotchas

- Exports unprefixed C symbols named seed and rand_u32, which can collide with other code; the README's namespace wrapper does not change the extern "C" linkage names
- Earlier unrolled versions produced wrong numbers and had an out-of-bounds read (both fixed per README); the srand/rand drop-ins were removed because the author believed they had errors
- State is \~5 KB (624 raw + 624 tempered words), double the reference's footprint
- No LICENSE file in the repo; the BSD license is stated only in the README and source headers

## Known shortcomings

- Baseline is mt19937ar.c, not the std library; CPU models unstated; clang version hedged ('I think'); no LICENSE file, modified BSD only per README.
- Not thread-safe (one static global state); exports unprefixed C symbols seed and rand_u32; never compared with std::mt19937; \~5 KB state, double the reference; older unrolled versions gave wrong output and had an out-of-bounds read (fixed).

## Caveats and trade-offs

Baseline is the reference C implementation (mt19937ar.c), not std::mt19937 (libstdc++). Numbers are from 2017 on the author's machines, CPU models unstated. There is no LICENSE file in the repo (404); the README says 'Distributed under the modified BSD license.'

Same MT19937 algorithm and output (verified against reference); 32-bit only; author doubts speed holds on non-Intel CPUs.

## Maintenance

Abandoned since December 2017, but it is two small BSD-licensed files (license stated in README only) that are easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README numbers against the reference mt19937ar.c; the Makefile with -O2 is public, but the CPU models are unstated ('Intel Xeon', 'older Intel Core i7') and the clang version is hedged ('clang 4 (I think)'), so this falls short of A.
- **Verifier notes:** Numbers match the README (1.58707x, 351.4-354.5M/s vs 221.6-223.4M/s on Xeon/gcc 6.3; 1.12485x on Core i7/clang). The commits page shows the last commit as Dec 7, 2017 (the record says 2017-12-06, likely a timezone difference; left unchanged). The license comes only from the README statement.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** reference/mt19937ar.cpp built with same flags: 1.59x like-for-like
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/cslarsen/mersenne-twister/HEAD/README.md>
  - <https://raw.githubusercontent.com/cslarsen/mersenne-twister/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/cslarsen/mersenne-twister/HEAD/Makefile>
  - <https://github.com/cslarsen/mersenne-twister/commits>
- **Sources the enricher read:**
  - <https://github.com/cslarsen/mersenne-twister>
  - <https://raw.githubusercontent.com/cslarsen/mersenne-twister/HEAD/README.md>
  - <https://raw.githubusercontent.com/cslarsen/mersenne-twister/HEAD/Makefile>
  - <https://raw.githubusercontent.com/cslarsen/mersenne-twister/HEAD/mersenne-twister.h>
  - <https://raw.githubusercontent.com/cslarsen/mersenne-twister/HEAD/mersenne-twister.cpp>
  - <https://raw.githubusercontent.com/cslarsen/mersenne-twister/HEAD/test-mt.cpp>
  - <https://raw.githubusercontent.com/cslarsen/mersenne-twister/HEAD/reference/mt19937ar.cpp>
  - <https://raw.githubusercontent.com/lemire/testingRNG/HEAD/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/cslarsen/mersenne-twister`) · [data/wave8/enrich/raw/github_com_cslarsen_mersenne_twister.json](../../../data/wave8/enrich/raw/github_com_cslarsen_mersenne_twister.json) (enrichment confidence 0.85)

</details>
