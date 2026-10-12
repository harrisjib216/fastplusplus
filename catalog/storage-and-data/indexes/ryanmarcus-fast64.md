# fast64 (FAST: Fast Architecture Sensitive Tree, 64-bit)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Indexes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `GPL-3.0` · 🔴 abandoned

> Rust/C AVX-512 static search tree for sorted u32/u64 keys; about 10% faster lookups than STX B-Tree in SOSD.

| | |
|---|---|
| **Beats** | B-tree (STX B-Tree) |
| **Claimed result** | Table 2 (32-bit amzn, fastest variant of each structure): FAST 435.33 ns/lookup (102.0 MB) vs BTree 482.11 ns/lookup (166.0 MB), about 1.1x lower latency (derived from page data). IBTree is 446.55 ns and plain binary search 741.69 ns. Separately, FAST had the highest relative multithreaded speedup of any structure tested: 32x throughput at 40 threads against its own single-thread run. |
| **Workload** | Point lookups (10M random lookup keys) on the SOSD amzn dataset (200M keys), comparing FAST against a tuned STX B-Tree. The Table 2 numbers are for a 32-bit version of amzn, which SOSD runs through this crate's create_fast32 path. The 64-bit results (Fig. 7 Pareto, Fig. 10, Fig. 16 multithreading) appear only as plots. |
| **Metric** | latency |
| **Hardware** | Intel Xeon Gold 6230 CPU @ 2.10GHz, 256GB RAM (20 physical / 40 logical cores for the multithreading experiment) |
| **Compiler and flags** | Not stated in the paper. From the code: SOSD's CMakeLists.txt adds -ffast-math -Wall -march=native (plus -fopenmp), and fast64's c/Makefile builds the AVX-512 lookup with gcc -O3 -march=native. The compiler used for the paper runs is unstated. |
| **Adoption** | 8 stars |
| **Last commit** | 2020-04-23 |
| **Links** | [repository](https://github.com/RyanMarcus/fast64) · [benchmark](http://www.vldb.org/pvldb/vol14/p1-marcus.pdf) |

## Verdict

On an Intel Xeon Gold 6230, the SOSD paper (Marcus et al., PVLDB 14(1)) ran 10M random lookups on a 32-bit version of the 200M-key amzn dataset: the fastest FAST variant took 435.33 ns per lookup at 102 MB, including last-mile binary search (its size matches a tree sampling every 16th key), against 482.11 ns at 166 MB for the fastest STX B-Tree variant, about 1.1x faster. No compiler or version is stated (SOSD's CMake uses -march=native -ffast-math, and build.rs compiles the C kernel with -march=native), and the 32x figure compares FAST at 40 threads with FAST at one thread, not with B-Tree.

## Use it when

- Read-only, build-once lower-bound lookups over sorted, unique u64 or u32 integer keys where the value is an array position, for example a sparse index over a large sorted array followed by a last-mile binary search.
- x86-64 servers with AVX-512F, like the paper's Xeon Gold 6230, where you build and run on the same CPU model.
- Throughput-bound lookups across many threads. SOSD measured the highest relative scaling of any structure: 32x its single-thread throughput at 40 threads. Its latency barely changed with a memory fence between lookups.
- 32-bit keys. Each 512-bit compare covers 16 keys, and SOSD notes that tree structures gain from 32-bit keys while learned indexes do not.
- As a reproducible SIMD-tree baseline in index research, since it is the exact code behind SOSD's FAST numbers (SOSD pins its final commit, b3d15a9).

## Skip it when

- Any workload with updates. There is no insert or delete, so every change means a full rebuild, and SOSD found FAST's build among the slowest of the non-learned structures it tested.
- When a learned index or hash table fits. In the same SOSD table, RMI (180.90 ns, 48 MB), RadixSpline (266.58 ns, 4 MB) and PGM (326.48 ns, 14 MB) are all faster and smaller than FAST (435.33 ns, 102 MB). If order does not matter, the hash tables took 94-115 ns.
- CPUs without AVX-512F, non-x86 targets, or binaries that must be portable. Without AVX-512F you get an unbenchmarked scalar C fallback (a linear scan with early exit), and build.rs ties the binary to the build machine's CPU.
- When you need exact-match or membership answers, duplicate keys, arbitrary payload types, range iteration, or more than about 2.1 billion u64 keys (see gotchas).
- Proprietary or closed-source distribution (GPL-3.0), or when you need a maintained dependency: it has no README, no docs, no releases and no activity since April 2020.

## How it is fast

Named after Kim et al.'s FAST (Fast Architecture Sensitive Tree, SIGMOD 2010), the code builds a pointer-free B+-tree bottom-up in which every node is a 128-byte-aligned page: one 64-byte cache line of keys (8 u64 or 16 u32), then one line of child offsets, or of values at the leaves. Each level does a branch-free node search in C (one AVX-512 broadcast, one unsigned compare-to-mask and one popcount), and the count indexes straight into the offset line, so a lookup reads one page per level with fanout 8 for u64 keys or 16 for u32. The SOSD authors credit its multithreaded scaling to few cache misses and to AVX-512 overlapping compute with memory reads.

## Compared with alternatives

RMI, RadixSpline and PGM-index all beat it on both latency and size in the same SOSD table, and ALEX, LIPP and HOT also accept inserts, so pick FAST only if you want a model-free comparison tree on AVX-512 hardware (nothing to tune except the sampling rate, and depth depends on key count, not key distribution). Its SOSD strengths are highly concurrent or fence-separated lookups: it scaled 32x at 40 threads and barely moved with fences that slowed RMI and RS by about 50%, though the learned indexes still had the better size/latency trade-off.

## Integration

| | |
|---|---|
| **Form** | crate (Cargo lib + staticlib with a C-ABI header fast64.h; git-only, not published on crates.io) |
| **Dependencies** | num 0.2 (Rust); cc build-dependency plus a C compiler for c/lookup.c; criterion and rand for dev only. SOSD builds it with `cargo build --release` and links target/release/libfast64.a. |
| **Minimum toolchain** | Rust 2018 edition with a C compiler that accepts -march=native (GCC or Clang). MSRV not documented, and Cargo.lock is gitignored, so dependency versions float. SOSD's README targets Ubuntu 20.04 with clang and rustup stable. |
| **Platforms** | x86-64. The AVX-512F SIMD path is chosen when build.rs detects avx512f on the build host (CPUID). Other x86-64 CPUs get a scalar C fallback. Non-x86 is not documented: build.rs uses an x86-only feature check. Windows/MSVC is not documented. |
| **Thread safety** | Not documented. Lookups only read (&self, no interior mutability), and SOSD ran 40 concurrent threads through the C API. But the Rust FAST&lt;T&gt; struct holds raw pointers (Vec&lt;\*const T&gt;), so it is neither Send nor Sync, and sharing it across Rust threads needs an unsafe wrapper. |
| **Drop-in for the baseline** | no |

## Gotchas

- The SIMD path is picked at build time. build.rs checks avx512f on the machine running cargo and compiles lookup.c with -march=native. A binary built on an AVX-512 host can fault on a CPU without it, and cross-compiling picks the host's path, not the target's.
- It returns bounds, not matches. A query below the minimum key returns (0, min_val); a query at or above the maximum returns (max_val, T::MAX). Keys must already be sorted ascending (min and max are taken from the first and last element, and order is never checked). Duplicate-key behavior is not documented, and SOSD only runs the 64-bit wrapper on unique-key datasets.
- Unsafe memory handling. copy_to_aligned passes a 128-byte-aligned allocation to Vec, which frees it with T's smaller alignment; the source comment admits this, and it breaks Rust's allocator contract. Empty input or unequal key/value lengths panic (unwrap/assert_eq), and the C API has no error return. The build copies the input three times and allocates a small Vec per page, which helps explain the slow build.
- Child offsets are stored through `index as u32`, so a u64 tree whose leaf layer exceeds 2^32 slots (about 2^31 keys) silently truncates offsets. The bundled Criterion bench imports a nonexistent `fast64::Fast64` type and does not compile as shipped. fast64.h uses a bare extern "C" block and includes no &lt;stdint.h&gt;, so it only works from C++.

## Known shortcomings

- The listed numbers are for 32-bit keys (SOSD's create_fast32), not 64-bit; compiler unstated.
- A static read-only tree over sorted u32/u64 keys; lookup returns a bracketing pair (a search bound, not a map), with no inserts or found flag. About 1.1x vs the STX B-tree on 32-bit keys only; RMI, RadixSpline and PGM are faster and smaller in the same SOSD table.
- The AVX-512 path is chosen on the build host (-march=native), so binaries are not portable; the non-AVX-512 path is an unbenchmarked scalar C fallback. Bugs: aligned allocations freed with the wrong alignment (UB, admitted in a comment); offsets cast to u32 silently truncate beyond \~2^31 keys; the shipped bench references a nonexistent Fast64 type and does not compile; the Rust struct is not Send/Sync. No README, not on crates.io, GPL-3.0.

## Caveats and trade-offs

The single-thread margin over STX B-Tree in Table 2 is small (about 10%), and that table uses 32-bit keys, not 64-bit. The 32x claim is a self-relative multithreading speedup, not a multithreaded FAST-vs-BTree comparison, so do not read it as a 32x win over BTree. The fast lookup path is AVX-512 C code (build.rs checks for avx512f); machines without it get a slower safe Rust path. In the same paper FAST is slower than the learned indexes (RMI 180.90 ns, RS 266.58 ns, PGM 326.48 ns) and the hash tables, and it has one of the longest build times.

Read-only, static tree built once; relies heavily on AVX-512 for its throughput and multithreaded scaling advantage, so results are CPU-generation dependent; build times are among the slowest of the structures SOSD tested.

## Maintenance

Abandoned after 12 commits over 10 days (last 2020-04-23), with no README, releases or crates.io package and two outside Oct 2025 PRs (a C++23/Highway port and CI) closed unmerged; at about 500 lines of Rust and 150 of C it is easy to vendor, but GPL-3.0 copyleft applies and you would maintain it yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The peer-reviewed PVLDB 14(1) SOSD paper (Marcus et al.) benchmarks FAST against the STX B-Tree. Table 2 gives FAST 435.33 ns / 102.0 MB against BTree 482.11 ns / 166.0 MB, and Sec. 4.5 states the 32x at 40 threads. It is not A: the benchmark code is public (learnedsystems/SOSD, benchmarks/benchmark_fast64.cc plus competitors/fast64_search.h, which wraps this repo as a submodule) and the CPU is named (Xeon Gold 6230), but neither the paper nor the SOSD README states a compiler or version.
- **Verifier notes:** Metadata checked and correct: GPL-3.0, 8 stars, last commit 2020-04-23, not a fork, not archived, so abandoned. SOSD pulls this repo in as the fast64 git submodule and uses it for both the FAST32 and FAST64 competitors, so the Table 2 FAST row does belong to this project. SOSD's older SSE competitors/fast.h is a separate class.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <http://www.vldb.org/pvldb/vol14/p1-marcus.pdf>
  - <https://github.com/RyanMarcus/fast64>
  - <https://github.com/RyanMarcus/fast64/blob/master/c/Makefile>
  - <https://github.com/RyanMarcus/fast64/blob/master/c/lookup.c>
  - <https://github.com/RyanMarcus/fast64/blob/master/build.rs>
  - <https://github.com/RyanMarcus/fast64/blob/master/benches/main_bench.rs>
  - <https://github.com/learnedsystems/SOSD>
  - <https://github.com/learnedsystems/SOSD/blob/master/CMakeLists.txt>
  - <https://github.com/learnedsystems/SOSD/blob/master/competitors/fast64_search.h>
  - <https://github.com/learnedsystems/SOSD/blob/master/competitors/fast.h>
  - <https://github.com/learnedsystems/SOSD/blob/master/benchmarks/benchmark_fast64.cc>
  - <https://github.com/learnedsystems/SOSD/blob/master/.gitmodules>
- **Sources the enricher read:**
  - <https://github.com/RyanMarcus/fast64>
  - <https://github.com/RyanMarcus/fast64/blob/master/Cargo.toml>
  - <https://github.com/RyanMarcus/fast64/blob/master/build.rs>
  - <https://github.com/RyanMarcus/fast64/blob/master/src/lib.rs>
  - <https://github.com/RyanMarcus/fast64/blob/master/c/lookup.c>
  - <https://github.com/RyanMarcus/fast64/blob/master/c/lookup.h>
  - <https://github.com/RyanMarcus/fast64/blob/master/c/Makefile>
  - <https://github.com/RyanMarcus/fast64/blob/master/fast64.h>
  - <https://github.com/RyanMarcus/fast64/blob/master/benches/main_bench.rs>
  - <https://github.com/RyanMarcus/fast64/blob/master/.gitignore>
  - <https://github.com/RyanMarcus/fast64/commits/master>
  - <https://github.com/RyanMarcus/fast64/pull/1>
  - <https://github.com/RyanMarcus/fast64/pull/2>
  - <https://github.com/mattyv/fast64>
  - <http://www.vldb.org/pvldb/vol14/p1-marcus.pdf>
  - <https://github.com/learnedsystems/SOSD>
  - <https://github.com/learnedsystems/SOSD/blob/master/CMakeLists.txt>
  - <https://github.com/learnedsystems/SOSD/blob/master/.gitmodules>
  - <https://github.com/learnedsystems/SOSD/tree/master/fast64>
  - <https://github.com/learnedsystems/SOSD/blob/master/competitors/fast64_search.h>
  - <https://github.com/learnedsystems/SOSD/blob/master/benchmarks/benchmark_fast64.cc>
  - <https://crates.io/api/v1/crates/fast64>
  - <https://doc.rust-lang.org/std/macro.is_x86_feature_detected.html>
  - <https://dl.acm.org/doi/10.1145/1807167.1807206>
  - <https://api.crossref.org/works/10.1145/1807167.1807206>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/ryanmarcus/fast64`) · [data/wave6/enrich/raw/github_com_ryanmarcus_fast64.json](../../../data/wave6/enrich/raw/github_com_ryanmarcus_fast64.json) (enrichment confidence 0.8)

</details>
