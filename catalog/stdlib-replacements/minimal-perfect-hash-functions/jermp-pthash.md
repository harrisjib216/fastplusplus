# PTHash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Minimal perfect hash functions](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++17 minimal perfect hash library (PTHash/PHOBIC) with 3.1-4.6x faster lookups than BBHash at \~3 bits/key.

| | |
|---|---|
| **Beats** | BBHash |
| **Claimed result** | At similar space (\~3 bits/key) on 1 billion random 64-bit keys, single core, PTHash lookups take 37 ns/key (C-C, alpha=0.99, c=7, 3.23 bits/key) and 55 ns/key (D-D, alpha=0.94, c=7, 2.99 bits/key), vs 170 ns/key for BBHash gamma=1 (3.06 bits/key). That is about 3.1-4.6x faster lookups (derived from page data); the paper text says 3-4.5x vs BBHash gamma=1,2. BBHash builds faster at that setting (253 s vs 689-1042 s for these PTHash variants). |
| **Workload** | Construction and lookup of MPHFs over 1 billion uniformly random 64-bit integer keys, single core (construction and lookup single-threaded; BBHash also run with one thread), reproducing Table 5 of the PTHash SIGIR'21 paper. |
| **Metric** | latency |
| **Hardware** | Intel i9-9900K @3.60GHz, 64GB DDR3 RAM @2.66GHz, Linux 5 (64-bit) |
| **Compiler and flags** | gcc 9.2.1, -O3 -march=native (PTHash SIGIR'21 paper Sec. 5; mphf_benchmark CMakeLists.txt sets -O3 -march=native) |
| **Adoption** | 267 stars |
| **Last commit** | 2026-07-27 |
| **Links** | [repository](https://github.com/jermp/pthash) · [benchmark](https://github.com/roberto-trani/mphf_benchmark/blob/main/README.md) |

## Verdict

On the authors' mphf_benchmark harness (1 billion uniformly random 64-bit keys, single core, gcc 9.2.1 -O3 -march=native, Intel i9-9900K with 64 GB DDR3), PTHash looked up keys in 37 ns/key (C-C, 3.23 bits/key) and 55 ns/key (D-D, 2.99 bits/key), versus 170 ns/key for single-threaded BBHash gamma=1 (3.06 bits/key), about 3.1-4.6x faster. BBHash built the set faster (253 s versus 689-1042 s), and these numbers come from a 2022 PTHash commit, not the current lambda-based code.

## Use it when

- Static sets of millions to billions of keys (64-bit integers, strings, URLs, n-grams) where lookup latency matters most. On 1B random 64-bit keys, a single core looks up in 37-55 ns/key at 3.0-3.2 bits/key.
- Build-once/query-many deployments. You build offline, serialize with essentials::save, and load or mmap the function at query time.
- Long variable-length keys. PTHash hashes each key only once per lookup; the paper reports only a 6-26 ns/key increase for q-grams and URLs relative to 64-bit keys.
- Key sets larger than RAM. single_phf and partitioned_phf have external-memory builders capped by config.ram, and construction can be multi-threaded with config.num_threads.
- Space/speed tuning. The author's current recommended default is PHOBIC (dense partitioned, C-int encoder, opt bucketer, lambda=7). On 100M keys with 8 threads on a Xeon W-2245, it gave 2.51 bits/key and 33.5 ns/key lookup in an 8.3 s build (author's own benchmark, with no BBHash comparison).

## Skip it when

- Dynamic key sets. The function is static by design, so any insert or delete means a full rebuild.
- When single-threaded build time matters more than lookup speed. At similar space on 1B keys, BBHash gamma=1 built in 253 s versus 689-1042 s for the fast-lookup PTHash configurations.
- Tiny key sets (tens to thousands of keys). Fixed metadata dominates: 469 bits/key for 6 keys was reported in issue #88. Several pathological small inputs made the pilot search hang (#14, #67, #87; the maintainer reports these as fixed). The author says MPHFs are meant for at least hundreds of thousands of keys.
- When you need order preservation or membership tests. Output slots come in arbitrary order, and a key outside the build set still returns a valid-looking slot in [0, n), so you must store and compare keys yourself.
- 32-bit, embedded or MSVC/Windows targets. The author says it is meant for 64-bit architectures, and the code relies on __uint128_t and POSIX sysconf. Also, PHOBIC's dense_partitioned_phf cannot yet be built in external memory (open issue #90).

## How it is fast

It revisits the FCH (Fox-Chen-Heath) scheme: keys are hashed once into buckets (skewed so 60% of keys land in 30% of buckets, or with PHOBIC's 'optimal' bucket function), and the builder processes buckets largest-first, searching for a small integer 'pilot' per bucket that sends all its keys to free slots via a multiply-high reduction of mix(h(x) XOR mix(pilot)). A lookup is therefore one key hash, one random access into a compressed pilot array and a multiply, whereas BBHash can hash the key several times per lookup (once per level). The pilots compress well because small ones are tried first; encodings include compact, dictionary, Elias-Fano, Rice, front/back 'dual' and PHOBIC's interleaved codes. Building with a load factor alpha &lt; 1 makes the pilot search much faster, and minimality is restored by an Elias-Fano 'free slots' array consulted only for keys that land at a position &gt;= n.

## Compared with alternatives

Pick PTHash when lookup latency dominates. In the same 1B-key table it answers in 37-101 ns/key, versus 199 ns for emphf and 197-220 ns for RecSplit, at a cost of roughly 0.4-1.4 bits/key more than RecSplit's 1.80. Prefer RecSplit, ShockHash or ConsensusRecSplit when you need to get down near 1.5-1.8 bits/key, and LPHash for k-mer sets (the PTHash author himself points k-mer users there).

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | Header-only git submodules: jermp/bits (which pulls in jermp/essentials), jermp/mm_file and xxHash (included inline via xxh3.h). Also pthreads via CMake Threads::Threads. cmd_line_parser is used only by the bundled build/example tools. |
| **Minimum toolchain** | C++17 (C++14 is explicitly unsupported, per issue #8) and CMake &gt;= 3.5. CI builds with GCC 11-14 and Clang 16-18 on Ubuntu 24.04; the paper used GCC 9.2.1. |
| **Platforms** | 64-bit only. Tested on Linux/GCC and macOS/Clang, on both x86-64 and Apple ARM (the author reports faster queries on M1 than on the x86 box). On x86-64 Unix, the CMake target adds -march=native -mbmi2 -msse4.2. Windows/MSVC support is not documented. |
| **Thread safety** | Not documented. Lookup (operator()) is a const method that mutates no state, so concurrent lookups on a built function appear safe. Construction is parallel internally via config.num_threads, and search throws if that exceeds std::thread::hardware_concurrency(). |
| **Drop-in for the baseline** | partial — it fills the same role as BBHash (a static MPHF mapping keys to [0, n)), but the API is different: template-configured types, iterator plus build_configuration construction, and its own serialization. Call sites and saved files must be rewritten. |

## Gotchas

- build_configuration defaults to verbose=true, and seed-retry messages go to std::cout regardless, so set config.verbose=false in library code. The default seed is random (up to 10 retries), so builds are not reproducible unless you set config.seed. With a fixed seed, a failed search throws seed_runtime_error instead of retrying.
- Duplicate keys, or colliding 64-bit hashes, make construction throw 'seed did not work'. The xxhash_64 hasher throws outright above 2^30 keys; use xxhash_128 for large sets.
- The exported PTHASH CMake target injects -march=native into every consumer target on x86-64 Unix. Binaries built this way may not run on older CPUs; override the flags if you ship binaries.
- The API and parameters changed after the benchmarked version. mphf_benchmark pins a Dec-2022 commit (b9a0c37) that uses the old 'c' parameter and MurmurHash2, while current master uses 'lambda', xxHash and a Bucketer template argument. Use release v2.0.0 to get 'c' semantics, and re-tune rather than copying the paper's configurations.

## Caveats and trade-offs

The benchmark is by the PTHash authors, and the README table reproduces their own SIGIR'21 Table 5. That table includes GOV, which is Java-only and cannot be run by the harness. The README lists D-D alpha=0.88 with c=7, but the paper and code use c=11. BBHash was run single-threaded even though it supports multi-threaded construction, and PTHash builds slower than BBHash at similar space. CMPH's CHD was benchmarked directly via libcmph; only CMPH's FCH was replaced by the authors' own FCH reimplementation, because CMPH's FCH was 'orders of magnitude slower'.

Offline/batch construction only (not incremental); needs a 64-bit-bucket-id compile flag beyond 2^32 buckets; several encoder/bucketer configs (lambda, alpha, dense vs partitioned) must be tuned for the desired space/time trade-off.

## Maintenance

Actively maintained: the last commit on 2026-07-27 added string_view keys and key mappers, and only one issue is open. It is MIT-licensed and header-only, and adding it as a git submodule is the documented integration path.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** roberto-trani/mphf_benchmark (src/mphf_benchmark.cpp, include/pthash_wrapper.hpp, include/bbhash_wrapper.hpp with the rizkg/BBHash submodule) runs PTHash against BBHash. The README states the i9-9900K CPU, CMakeLists.txt sets -O3 -march=native, and the PTHash SIGIR'21 paper (Sec. 5) states gcc 9.2.1 and single-core runs.
- **Verifier notes:** Numbers match the PTHash and BBHash rows of the mphf_benchmark README; the ratio is now marked as derived. The '8-thread construction' in the workload came from the PTHash repo's own benchmarks README (Xeon W-2245, gcc 10.3.0), not from this table, which was run on a single core. The old caveat wrongly said CMPH was not benchmarked directly. The metadata (MIT, 267 stars, last commit 2026-07-27, active) checks out.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/roberto-trani/mphf_benchmark/blob/main/README.md>
  - <https://github.com/roberto-trani/mphf_benchmark>
  - <https://github.com/roberto-trani/mphf_benchmark/blob/main/CMakeLists.txt>
  - <https://github.com/roberto-trani/mphf_benchmark/blob/main/src/mphf_benchmark.cpp>
  - <https://github.com/roberto-trani/mphf_benchmark/blob/main/include/pthash_wrapper.hpp>
  - <https://github.com/roberto-trani/mphf_benchmark/blob/main/include/bbhash_wrapper.hpp>
  - <https://arxiv.org/pdf/2104.10402>
  - <https://github.com/jermp/pthash>
  - <https://github.com/jermp/pthash/blob/master/README.md>
  - <https://github.com/jermp/pthash/blob/master/benchmarks/README.md>
- **Sources the enricher read:**
  - <https://github.com/jermp/pthash>
  - <https://github.com/jermp/pthash/blob/master/README.md>
  - <https://github.com/jermp/pthash/blob/master/CMakeLists.txt>
  - <https://github.com/jermp/pthash/blob/master/.gitmodules>
  - <https://github.com/jermp/pthash/blob/master/include/pthash.hpp>
  - <https://github.com/jermp/pthash/blob/master/include/single_phf.hpp>
  - <https://github.com/jermp/pthash/blob/master/include/partitioned_phf.hpp>
  - <https://github.com/jermp/pthash/blob/master/include/dense_partitioned_phf.hpp>
  - <https://github.com/jermp/pthash/blob/master/include/utils/hasher.hpp>
  - <https://github.com/jermp/pthash/blob/master/include/utils/util.hpp>
  - <https://github.com/jermp/pthash/blob/master/include/utils/bucketers.hpp>
  - <https://github.com/jermp/pthash/blob/master/include/utils/encoders.hpp>
  - <https://github.com/jermp/pthash/blob/master/include/utils/dense_encoders.hpp>
  - <https://github.com/jermp/pthash/blob/master/include/builders/util.hpp>
  - <https://github.com/jermp/pthash/blob/master/include/builders/search.hpp>
  - <https://github.com/jermp/pthash/blob/master/include/builders/internal_memory_builder_single_phf.hpp>
  - <https://github.com/jermp/pthash/blob/master/src/example.cpp>
  - <https://github.com/jermp/pthash/blob/master/src/build.cpp>
  - <https://github.com/jermp/pthash/blob/master/benchmarks/README.md>
  - <https://github.com/jermp/pthash/blob/master/.github/workflows/build.yml>
  - <https://github.com/jermp/pthash/releases>
  - <https://github.com/jermp/pthash/commits/master>
  - <https://github.com/jermp/pthash/commit/b9a0c372cd4c12219f9508f2edac24347aaaca98>
  - <https://github.com/jermp/pthash/issues>
  - <https://github.com/jermp/pthash/issues/4>
  - <https://github.com/jermp/pthash/issues/8>
  - <https://github.com/jermp/pthash/issues/9>
  - <https://github.com/jermp/pthash/issues/13>
  - <https://github.com/jermp/pthash/issues/14>
  - <https://github.com/jermp/pthash/issues/16>
  - <https://github.com/jermp/pthash/issues/42>
  - <https://github.com/jermp/pthash/issues/62>
  - <https://github.com/jermp/pthash/issues/63>
  - <https://github.com/jermp/pthash/issues/66>
  - <https://github.com/jermp/pthash/issues/67>
  - <https://github.com/jermp/pthash/issues/80>
  - <https://github.com/jermp/pthash/issues/84>
  - <https://github.com/jermp/pthash/issues/87>
  - <https://github.com/jermp/pthash/issues/88>
  - <https://github.com/jermp/bits/blob/HEAD/CMakeLists.txt>
  - <https://github.com/Cyan4973/xxHash/blob/HEAD/xxh3.h>
  - <https://github.com/roberto-trani/mphf_benchmark>
  - <https://github.com/roberto-trani/mphf_benchmark/blob/main/README.md>
  - <https://github.com/roberto-trani/mphf_benchmark/tree/main/external>
  - <https://github.com/roberto-trani/mphf_benchmark/blob/main/include/pthash_wrapper.hpp>
  - <https://github.com/roberto-trani/mphf_benchmark/blob/main/include/bbhash_wrapper.hpp>
  - <https://arxiv.org/abs/2104.10402>
  - <https://arxiv.org/pdf/2104.10402>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/jermp/pthash`) · [data/wave1-phf/enrich/raw/github_com_jermp_pthash.json](../../../data/wave1-phf/enrich/raw/github_com_jermp_pthash.json) (enrichment confidence 0.88)

</details>
