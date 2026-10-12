# GBF-NEON (Galois Bipartite Filter, Ribbon-filter variant)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Static uint64 filter using per-block GF(2) solves and NEON parity; \~2x faster negative queries than author's blocked Bloom.

| | |
|---|---|
| **Beats** | Bloom filter |
| **Claimed result** | 8.4 ns query latency (GBF) vs 16.4 ns (Blocked Bloom, 8.26 bits/key) and 17.6 ns (naive Bloom, k=6) — roughly 2x faster query latency at near-equal memory (8.52 vs 8.26 bits/key), with false positive rate 0.78% vs 2.90%/1.69% (README table, 'Head-to-head vs competent Blocked Bloom'). |
| **Workload** | 1M random uint64 keys, queried with 1M positives and 1M negatives on one Apple M2 (src/bench_vs.cpp). GBF is compared with the project's own 64-byte cache-line Blocked Bloom (8 bits set per block) at 8.26 and 12 bits/key, and with a naive Bloom (k=6). |
| **Metric** | latency |
| **Hardware** | Apple M2 (Apple Silicon, NEON) |
| **Compiler and flags** | -O3 -march=native (CMakeLists.txt GBF_BASE_FLAGS), CMAKE_BUILD_TYPE=Release; compiler/version not stated |
| **Adoption** | 0 stars |
| **Last commit** | 2026-05-28 |
| **Links** | [repository](https://github.com/ElVec1o/GBF-NEON) · [benchmark](https://github.com/ElVec1o/GBF-NEON#head-to-head-vs-competent-blocked-bloom-buildbench_vs) |

## Verdict

Only the author's src/bench_vs.cpp, run once on one Apple M2 (-O3 -march=native, compiler unstated) with 1M random uint64 keys, backs the claim. The timed loop covers only the 1M non-member queries, so '8.4 ns vs 16.4 ns' is amortized per-query time on an all-miss stream, not isolated latency or a mixed workload. The baseline is the author's scalar blocked Bloom (512-bit blocks, 8 double-hashed bits, 64-bit modulo, early-exit loop), not a library implementation. My re-simulation of its hashing reproduces the published 2.90% and 1.97% FPRs, while the same layout with independent bit positions gives about 2.5% and 0.40%. So GBF's FPR edge holds at about 8.3 bits/key, but the 12-bits/key Bloom row is about 5x worse than it should be. GBF's 30 ms build uses one thread per partition, against 4-7 ms of single-threaded Bloom inserts.

## Use it when

- A read-only set of 64-bit keys (or keys you pre-hash to 64 bits) that is built once and queried many times on Apple Silicon or other aarch64 with NEON, where most lookups miss. The 8.4 ns figure comes from an all-negative query stream.
- Around 1M-key sets where about 0.8% FPR at about 8.5 bits/key suits you and you can size N just below a power-of-two boundary. Bits/key is lowest just under 62 x 2^k keys, for example 1,015,808 or 2,031,616.
- Filters built offline and shipped as files to same-architecture readers: save() plus load_mmap() maps the payload without copying.
- Studying or prototyping cache-line-local GF(2) filters. The core is a readable 649-line header with a libFuzzer harness and a 'what failed' design log (ARTICLE.md).

## Skip it when

- Sets that change, or targets other than about 0.78% FPR. There is no insert or erase, and the 8-bit fingerprint and 2-way probe are hard-coded, so lower FPR cannot be bought with more memory.
- Arbitrary or growing N when memory matters. The block count rounds up to a power of two, so bits/key follows a sawtooth between about 8.4 and 16.8. By the sizing code, 1,000,000 keys cost 8.52 bits/key but 1,015,809 keys cost 16.77 at the same about 0.78% FPR. The README's 'up to \~30%' over-allocation understates this.
- Small and mid-size sets built with the default thread count. There is no resize-and-retry: the constructor throws std::runtime_error and the C API returns false. In my re-simulation of the partitioning at worst-case sizes with 16 partitions (machines with 9-16 hardware threads), some partition exceeds its capacity, which guarantees failure, in essentially 100% of trials up to N=7,936. The rate is 96% at 15,872, 75% at 31,744 and 20% at 63,488, and 83% at N=992 with 4 partitions. The tests build small sets only with threads=1, and the fuzz harness de-duplicates keys and treats build exceptions as acceptable.
- Mixed hit/miss or positive-heavy lookups without your own benchmark. The author's own article measured 20.2 ns for a 50/50 mix (versus 6.5 ns all-positive), which it attributes to branch mispredicts. The Bloom baseline was never timed on positives or mixes.
- x86, Windows, or anything that needs a track record. x86 falls back to a scalar parity loop with no AVX2/AVX-512 path and has never been performance-measured (the CI logs have since expired). The code needs POSIX open/mmap and GCC/Clang builtins, so there is no MSVC. It is a 3-commit, 0-star weekend project.

## How it is fast

Memory is split into 64-byte blocks, each holding eight 64-bit columns. Each key is placed by 2-choice cuckoo hashing into one of two blocks inside a hash-selected partition (64 keys per block at most, about 62 targeted). Gaussian elimination over GF(2) then solves each block so that the parity of (key hash vector AND column j) reproduces the key's 8-bit fingerprint, retrying up to 256 per-block seeds. The author calls it a Ribbon-filter variant, but it is block-local dense elimination with cuckoo placement, not Ribbon's banded matrix. A query hashes to two block indices using bit masks (power-of-two sizing removes the modulo), prefetches both cache lines, and checks 8 AND-popcount parities per block. On aarch64 those parities are explicit NEON vcnt/vpaddl lanes, which the author measured at 1.5-3 ns faster than the scalar __builtin_parityll loop. GBF touches two cache lines per query versus the blocked Bloom's one. The Bloom baseline uses a 64-bit modulo and a branchy 8-probe loop, so part of the gap likely comes from that baseline's implementation rather than the structure.

## Compared with alternatives

Rarely. At its best-case N, GBF's 8.52 bits/key for 0.78% FPR is about 22% above the 7-bit minimum, roughly the Xor filter's 23% overhead cited in the BuRR entry, and it probes two cache lines instead of three with a parallel build. But xor_singleheader is mature, portable and has no size cliff, BuRR is far closer to the space minimum, and the Impala-derived SIMD blocked Bloom in efficient/cuckoofilter supports inserts with one cache line per query. Pick GBF only for a read-only uint64 set on aarch64 whose size you control, or as a small header to experiment with.

## Integration

| | |
|---|---|
| **Form** | header-only (src/gbf.hpp + src/hash.hpp); optional static lib gbf_c for the C API |
| **Dependencies** | none beyond the C++ standard library, pthreads (std::thread; CMake links Threads::Threads) and POSIX file/mmap calls |
| **Minimum toolchain** | C++17 and CMake 3.16+. Needs GCC or Clang (__builtin_parityll, __builtin_prefetch). Compiler versions are not documented: CI built with ubuntu-latest gcc and clang, and the logs have expired. |
| **Platforms** | aarch64 with NEON, measured only on an Apple M2. x86-64 Linux compiles and passes tests in CI using scalar parity, with no performance numbers. POSIX only; no Windows. |
| **Thread safety** | Not documented. From the code, contains() and contains_batch() are const and touch no mutable state, so concurrent reads after construction look safe. Construction spawns one std::thread per partition (the next power of two at or above hardware_concurrency unless you pass threads). |
| **Drop-in for the baseline** | false: it is a build-once constructor over a uint64_t range with no insert, so it cannot replace an incrementally filled Bloom filter. The bundled adapter targets the xor8_\* API, not a Bloom API. |

## Gotchas

- The xor8 adapter maps xor8_serialize/xor8_deserialize to gbf_filter_save/gbf_filter_load. In xor_singleheader those functions take a memory buffer (char\*), but here they take a file path, so ported code compiles and silently treats the buffer as a filename. xor8_allocate's size argument is ignored, and populate copies the keys and builds with all hardware threads.
- The file format stores a magic number plus block and partition counts, but not WAYS and not the payload length. load_mmap() never checks the file size, so a truncated or untrusted file can be read out of bounds, and a GBF&lt;3&gt; file opened as GBF&lt;2&gt; silently gives false negatives. After load, key_count() and bits_per_key() return 0.
- The layout (partition count) depends on the build machine's hardware_concurrency unless you pass threads explicitly. The CMake gbf_headers INTERFACE target also pushes -O3 -march=native onto every target that links it, which yields non-portable binaries.
- The README's batch example does not compile, because std::vector&lt;bool&gt; has no data(); contains_batch needs a real bool array (bench.cpp casts a char buffer). fast_hash (a splitmix64-style mixer) is declared in the global namespace. The version labels disagree: v0.3 in bench_vs.cpp, v0.4 in gbf.hpp, v0.8 in comments, v1.0 in the README.

## Known shortcomings

- A hobby project (0 stars) whose baseline is its own blocked Bloom filter; -O3 -march=native with the compiler unstated. The author reports 7 of 8 tried ideas failed.
- The 8.4 ns lookup is an all-miss stream; the author's own 50/50 mix is 20.2 ns, and the Bloom baseline is never timed on hits. The baseline is the author's branchy scalar Bloom with 64-bit modulo; with proper hashing the same layout gets 2.5%/0.40% FPR instead of 2.90%/1.97%, so the 12 bits/key comparison is \~5x too pessimistic.
- Memory sawtooth from power-of-two block rounding (1M keys 8.52 bits/key, 1,015,809 keys 16.77); build throws with no retry and in simulation almost always fails for N&lt;=8k with 16 partitions (75% at 32k). Fixed 0.78% FPR, static only, x86 performance never measured, POSIX only. The xor8 adapter maps buffer serialization to a file-path save (silent misuse) and load_mmap skips the size check. Three commits in two days, AI-built.

## Caveats and trade-offs

First-party, self-run benchmark (src/bench_vs.cpp) on an Apple M2. Flags are -O3 -march=native from CMakeLists.txt; the compiler and version are not stated. The Blocked Bloom baseline is the author's own implementation, not an established library. At 1M keys (\~1 MB) the filter is cache-resident, and build is \~6x slower than Blocked Bloom (30 vs 5 ms). The README's design-journey note says 8 ideas were tried, 7 failed and 1 shipped. The bench_vs.cpp header still says 'GBF v0.3'. The headline numbers are Apple-M2-only; x86 results exist only in CI artifacts. This is a Ribbon-filter variant, not a novel algorithm, from a brand-new (0-star) single-author project and not independently reproduced.

Static only, no insert/erase after build; build time \~6x slower than Bloom (30ms vs \~4-7ms for 1M keys); no AVX-512 path shipped (x86 falls back to scalar, and author states x86 perf is unverified beyond CI correctness); power-of-2 partition sizing can over-allocate space up to \~30% at adversarial N.

## Maintenance

Effectively a one-weekend drop: three commits on 2026-05-27/28 and nothing since, 0 stars, forks or issues, and the author says it was built in 24 hours and heavily AI-assisted. It is MIT-licensed and small enough to read and vendor, but not production-proven.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** These are first-party README numbers from the project's own src/bench_vs.cpp, run against the author's own Blocked Bloom and naive Bloom on an Apple M2. The flags (-O3 -march=native) are in CMakeLists.txt, but the compiler and version are not stated, so the evidence falls short of A. It is not peer-reviewed or third-party.
- **Verifier notes:** README numbers match exactly: 8.4 ns vs 16.4/14.8/17.6 ns, and FPR 0.78% vs 2.90%/1.97%/1.69%. Metadata verified: MIT, created 2026-05-27, last commit 2026-05-28 (active), 0 stars, not a fork or archived.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ElVec1o/GBF-NEON>
  - <https://github.com/ElVec1o/GBF-NEON#head-to-head-vs-competent-blocked-bloom-buildbench_vs>
  - <https://github.com/ElVec1o/GBF-NEON/blob/main/CMakeLists.txt>
  - <https://github.com/ElVec1o/GBF-NEON/blob/main/src/bench_vs.cpp>
- **Sources the enricher read:**
  - <https://github.com/ElVec1o/GBF-NEON>
  - <https://github.com/ElVec1o/GBF-NEON#head-to-head-vs-competent-blocked-bloom-buildbench_vs>
  - <https://github.com/ElVec1o/GBF-NEON/blob/main/src/gbf.hpp>
  - <https://github.com/ElVec1o/GBF-NEON/blob/main/src/hash.hpp>
  - <https://github.com/ElVec1o/GBF-NEON/blob/main/src/bench_vs.cpp>
  - <https://github.com/ElVec1o/GBF-NEON/blob/main/src/bench.cpp>
  - <https://github.com/ElVec1o/GBF-NEON/blob/main/src/gbf_c.h>
  - <https://github.com/ElVec1o/GBF-NEON/blob/main/src/gbf_c.cpp>
  - <https://github.com/ElVec1o/GBF-NEON/blob/main/src/gbf_xor8_adapter.h>
  - <https://github.com/ElVec1o/GBF-NEON/blob/main/CMakeLists.txt>
  - <https://github.com/ElVec1o/GBF-NEON/blob/main/docs/X86_STATUS.md>
  - <https://github.com/ElVec1o/GBF-NEON/blob/main/ARTICLE.md>
  - <https://github.com/ElVec1o/GBF-NEON/blob/main/tests/test_correctness.cpp>
  - <https://github.com/ElVec1o/GBF-NEON/blob/main/fuzz/README.md>
  - <https://github.com/ElVec1o/GBF-NEON/blob/main/fuzz/fuzz_gbf.cpp>
  - <https://github.com/ElVec1o/GBF-NEON/blob/main/.github/workflows/ci.yml>
  - <https://github.com/ElVec1o/GBF-NEON/commits/main>
  - <https://github.com/ElVec1o/GBF-NEON/actions/runs/26591212481>
  - <https://github.com/FastFilter/xor_singleheader/blob/master/include/xorfilter.h>
  - <https://hn.algolia.com/api/v1/search?query=%22Galois%20Bipartite%20Filter%22>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/elvec1o/gbf-neon`) · [data/wave6/enrich/raw/github_com_elvec1o_gbf_neon.json](../../../data/wave6/enrich/raw/github_com_elvec1o_gbf_neon.json) (enrichment confidence 0.4)

</details>
